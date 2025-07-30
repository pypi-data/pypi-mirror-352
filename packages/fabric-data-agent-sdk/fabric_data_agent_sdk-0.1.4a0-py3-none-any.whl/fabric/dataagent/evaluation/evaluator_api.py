from datetime import datetime
from deltalake.writer import write_deltalake
from IPython.display import display, HTML
from tqdm import tqdm
from types import SimpleNamespace

from fabric.dataagent.client import FabricDataAgentManagement
from fabric.dataagent.client import FabricOpenAI
from synapse.ml.internal_utils.session_utils import get_fabric_context

import json
import logging
import numpy as np
import pandas as pd
import re
import time
import uuid

OPEN_AI_MODEL = "gpt-4o"
USER_ROLE = "user"
DATA_AGENT_STAGE = "production"
SPARK_HOST = "spark.trident.pbiHost"


def evaluate_data_agent(
    df: pd.DataFrame,
    data_agent_name: str,
    workspace_name: str = None,
    table_name: str = 'evaluation_output',
    critic_prompt: str = None,
    data_agent_stage: str = DATA_AGENT_STAGE,
):
    """
    API to evaluate the Data Agent. Returns the unique id for the evaluation run.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame with question and expected_answer list.
    data_agent_name : str
        Name of the Data Agent.
    workspace_name : str, optional
        Workspace Name if Data Agent is in different workspace. Default to None.
    table_name : str, optional
        Table name to store the evaluation result. Default to 'evaluation_output'.
    critic_prompt : str, optional
        Prompt to evaluate the actual answer from Data Agent. Default to None.
    data_agent_stage : str, optional
        Data Agent stage ie., sandbox or production. Default to production.

    Returns
    -------
    str
        Unique id for the evaluation run.
    """

    output_rows = []
    output_steps = []
    run_timestamp = datetime.now()
    # Unique id for each evaluation
    eval_id = str(uuid.uuid4())

    # Create fabric client
    fabric_client = FabricOpenAI(
        artifact_name=data_agent_name,
        workspace_name=workspace_name,
        ai_skill_stage=data_agent_stage,
    )
    # Create Data Agent management
    data_agent = FabricDataAgentManagement(data_agent_name, workspace_name)

    # Loops through the input file
    for index, row in tqdm(
        df.iterrows(), desc="Processing Rows", unit="step", total=len(df), leave=True
    ):
        query = row['question']
        expected_answer = row['expected_answer']
        start_time = time.time()

        # Generate the response for the query
        response = generate_answer(query, fabric_client, data_agent)

        end_time = time.time()

        actual_answer = response.message

        # Generate the prompt for evaluating the actual answer
        prompt = generate_prompt(query, expected_answer, actual_answer, critic_prompt)

        eval_response = generate_answer(prompt, fabric_client, data_agent)

        message = eval_response.message.lower()

        score = False if "no" in message else True if "yes" in message else np.nan

        output_rows.append(
            {
                'id': response.id,
                'evaluation_id': eval_id,
                'thread_id': response.thread_id,
                'run_timestamp': run_timestamp,
                'question': query,
                'expected_answer': expected_answer,
                'actual_answer': actual_answer,
                'execution_time_sec': round(end_time - start_time, 2),
                'status': response.status,
                'thread_url': response.thread_url,
                'evaluation_judgement': score,
                'evaluation_message': eval_response.message,
                'evaluation_status': eval_response.status,
                'evaluation_thread_url': eval_response.thread_url,
            }
        )
        output_steps.append(response.run_steps)

    df = pd.DataFrame(output_rows)

    # Add configuration and data sources to the DataFrame
    df_data_agent = add_data_agent_details(df, data_agent)

    # Saving the evaluation output to a file
    save_output(df_data_agent, table_name)
    # Saving the evaluation output steps to a file
    save_output(pd.DataFrame(output_steps), f"{table_name}_steps")

    return eval_id


def generate_answer(
    query: str, fabric_client: FabricOpenAI, data_agent: FabricDataAgentManagement
):
    """
    Generates the response for input query.

    Parameters
    ----------
    query : str
        Question from the input DataFrame.
    fabric_client: FabricOpenAI
        An instance of the fabric client to interact with Data Agent.
    data_agent: FabricDataAgentManagement
        An instance of FabricDataAgentManagement to get the details of the Data Agent.

    Returns
    -------
    types.SimpleNamespace
        Formatted response of the Data Agent.
    """

    # Unique id for each row in input dataset
    unique_id = str(uuid.uuid4())
    # Create thread with custom tag (uuid)
    thread = fabric_client.get_or_create_thread(unique_id)
    thread_id = thread.id

    # Generate answer for the input query
    message, run = get_message(fabric_client, thread_id, query)

    # Construct the thread URL
    thread_url = get_thread_url(thread_id, data_agent)

    run_steps = get_steps(fabric_client, thread_id, run.id, unique_id)

    answer_details = {
        'id': unique_id,
        'thread_id': thread_id,
        'status': run.status,
        'message': message,
        'thread_url': thread_url,
        'run_steps': run_steps,
    }

    return SimpleNamespace(**answer_details)


def get_message(fabric_client: FabricOpenAI, thread_id: str, query: str):
    """
    Get message for the input query and thread.

    Parameters
    ----------
    fabric_client: FabricOpenAI
        An instance of the fabric client created to interact with Data Agent.
    thread_id: str
        An unique identifier of the thread.
    query : str
        Question from the input DataFrame.

    Returns
    -------
    tuple[str, object]
        Tuple with actual answer and run instance.

    Raises
    -------
        RuntimeError: If fabric client is None.
    """

    # Raise RuntimeError if fabric client is None
    if fabric_client is None:
        logging.debug("Fabric client is None")
        raise RuntimeError("Fabric client is None")

    # Create assistant
    assistant = fabric_client.beta.assistants.create(model=OPEN_AI_MODEL)

    # Add message to the thread
    fabric_client.beta.threads.messages.create(
        thread_id=thread_id, role=USER_ROLE, content=query
    )

    # Start the run
    run = fabric_client.beta.threads.runs.create_and_poll(
        thread_id=thread_id, assistant_id=assistant.id
    )

    status = run.status
    # Log error message if status is failed
    if status == "failed" and run.last_error:
        generated_answer = f"Error ({run.last_error.code}): {run.last_error.message}"
        logging.debug(generated_answer)
    else:
        # Get the messages from response
        messages = fabric_client.beta.threads.messages.list(
            thread_id=thread_id, order="desc"
        )

        if messages:
            generated_answer = list(messages)[0].content[0].text.value
        else:
            generated_answer = "No answer returned from Data Agent"

    return generated_answer, run


def get_steps(
    fabric_client: FabricOpenAI, thread_id: str, run_id: str, unique_id: str = None
):
    """
    Get steps for the run.

    Parameters
    ----------
    fabric_client : FabricOpenAI
        An instance of the fabric client created to interact with Data Agent.
    thread_id : str
        An unique identifier of the thread.
    run_id : str
        An unique identifier of the run.
    unique_id : str
        An unique identifier for the input processing row.

    Returns
    -------
    dict
        Dictionary of run steps in the Data Agent response.

    Raises
    -------
        RuntimeError: If fabric client is None.
    """

    # Raise RuntimeError if fabric client is None
    if fabric_client is None:
        logging.debug("Fabric client is None")
        raise RuntimeError("Fabric client is None")

    function_names = []
    function_queries = []
    function_outputs = []
    sql_commands = []
    dax_commands = []
    kql_commands = []

    # Get run steps for a thread
    run_steps = fabric_client.beta.threads.runs.steps.list(
        thread_id=thread_id, run_id=run_id
    )

    # Extract list of run steps
    for run_step in run_steps:
        if run_step.step_details.type == "tool_calls":
            for tool_call in run_step.step_details.tool_calls:
                if tool_call.type == "function":
                    function_names.append(str(tool_call.function.name))
                    arguments = json.loads(tool_call.function.arguments)
                    # Convert to json dict if arguments is not dict
                    if not isinstance(arguments, dict):
                        arguments = json.loads(arguments)
                    # Check if arguments is dict to get the params or save arguments as function query
                    if isinstance(arguments, dict):
                        query = arguments.get("query") or arguments.get("natural_language_query")
                    else:
                        query = arguments
                    function_queries.append(str(query))
                    function_output = tool_call.function.output
                    function_outputs.append(str(function_output))
                    commands = get_commands(function_output)
                    sql_commands.append(str(commands.get("sql")))
                    dax_commands.append(str(commands.get("dax")))
                    kql_commands.append(str(commands.get("kql")))

    return {
        'id': unique_id,
        'thread_id': thread_id,
        'run_id': run_id,
        'function_names': str(function_names),
        'function_queries': str(function_queries),
        'function_outputs': str(function_outputs),
        # TODO: Make seperate tables for the commands.
        'sql_steps': str(sql_commands),
        'dax_steps': str(dax_commands),
        'kql_steps': str(kql_commands),
    }


def get_commands(output: str):
    """
    Get commands from run steps.

    Parameters
    ----------
    output : str
        Output string from a Data Agent response.

    Returns
    -------
    dict
        Dictionary of command type and command value returned in run steps.
    """
    commands = {}
    # Regular expression pattern to extract content inside triple backticks
    pattern = r"```(sql|dax|kql)\s(.*?)```"

    if output:
        # Extract matches
        matches = re.findall(pattern, output, re.DOTALL)
        # Store extracted commands in a dictionary
        commands = {match[0]: match[1] for match in matches}

    return commands


def generate_prompt(
    query: str, expected_answer: str, actual_answer: str, critic_prompt: str = None
):
    """
    Generate the prompt for the evaluation.

    Parameters
    ----------
    query : str
        Question from an input DataFrame.
    expected_answer : str
        Expected answer from an input DataFrame.
    actual_answer : str
        Actual answer string from a Data Agent response.
    critic_prompt : str, optional
        Prompt to evaluate the actual answer from Data Agent. Default to None.

    Returns
    -------
    str
        String prompt for the evaluation.
    """

    import textwrap

    if critic_prompt:
        prompt = critic_prompt.format(
            query=query, expected_answer=expected_answer, actual_answer=actual_answer
        )
    else:
        prompt = f"""
        Given the following query, ground truth, and generated response, please determine if the response is equivalent to ground truth. If they are equivalent, respond with 'yes'.

        Query: {query}

        Ground Truth:
        {expected_answer}

        Generated Response:
        {actual_answer}

        Is the generated response equivalent to the ground truth?
        """

    return textwrap.dedent(prompt)


def add_data_agent_details(df: pd.DataFrame, data_agent: FabricDataAgentManagement):
    """
    Add Data Agent details to the DataFrame.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame with processed output rows.
    data_agent: FabricDataAgentManagement
        An instance of FabricDataAgentManagement to get the details of the Data Agent.

    Returns
    -------
    pd.DataFrame
        Updated dataframe with Data Agent details.
    """

    # Return unmodified DataFrame if data agent is None
    if data_agent is None:
        return df

    # Add the Data Agent details to DataFrame
    df['data_agent_configuration'] = str(data_agent.get_configuration())
    publishing_info = data_agent._client.get_publishing_info()
    df['data_agent_version'] = publishing_info.value['currentVersion']
    df['data_agent_etag'] = publishing_info.etag
    df['data_agent_last_updated'] = publishing_info.value['lastUpdated']
    data_sources = str(data_agent.get_datasources())
    df['data_sources'] = [data_sources] * len(df)

    return df


def get_fabric_host():
    """
    Get Fabric host address.

    Returns
    -------
    str
        Fabric host address.

    Raises
    -------
        RuntimeError: If host address is None.
    """
    host = get_fabric_context().get(SPARK_HOST)
    if host is None:
        logging.debug(f"Fabric Host address is empty")
        raise RuntimeError("Fabric Host address is empty")

    return host.replace('api', "", 1)


def get_thread_url(thread_id: str, data_agent: FabricDataAgentManagement):
    """
    Get thread URL for the thread.

    Parameters
    ----------
    thread_id : str
        An unique identifier of the thread.
    data_agent : FabricDataAgentManagement
        An instance of FabricDataAgentManagement to get the details of the Data Agent.

    Returns
    -------
    str
        Thread URL for the input thread id.
    """

    data_agent_id = data_agent._client.data_agent_id
    host = get_fabric_host()

    thread_url = f"https://{host}/workloads/de-ds/dataagents/{data_agent_id}/externalThread?debug.aiSkillThreadIdOverride={thread_id}&debug.aiSkillViewPublishedOverride=0"

    return thread_url


def save_output(df: pd.DataFrame, table_name: str):
    """
    Saves the Dataframe to the Delta table.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame with processed output rows.
    table_name : str
        Table name to store the evaluation result
    """

    lakehouse_path = _default_lakehouse_path()
    # Write to a Delta Lake table
    write_deltalake(f"{lakehouse_path}/Tables/{table_name}", df, mode="append")


def get_evaluation_summary(
    table_name: str = 'evaluation_output', verbose: bool = False
):
    """
    Overall summary of an evaluation stored in the delta table.

    Parameters
    ----------
    table_name : str, optional
        Table name to store the evaluation result. Default to 'evaluation_output'.
    verbose : bool, optional
        Flag to print the evaluation summary. Default to False.

    Returns
    -------
    pd.DataFrame
        DataFrame with summary details.
    """

    # Get the delta table
    delta_table = _get_delta_table(table_name)

    # Return if table is not found
    if delta_table is None:
        return None

    # Convert to pandas DataFrame
    df = delta_table.to_pandas()

    # Calculate the percentage of True values in the DataFrame
    eval_percentage = (df['evaluation_judgement'].mean()) * 100

    # Group by timestamp and count the occurrences of True, False, and None in the 'evaluation_judgement' column
    grouped_df = (
        df.groupby('evaluation_id')['evaluation_judgement']
        .value_counts(dropna=False)
        .unstack(fill_value=0)
    )

    # Reindex to ensure True, False, None columns are included even if their count is zero
    grouped_df = grouped_df.reindex(columns=[True, False, np.nan], fill_value=0)

    # Calculate the percentage of True values per evaluation
    grouped_df['true_percentage'] = (grouped_df[True] / grouped_df.sum(axis=1)) * 100

    # Reset index and rename the columns in the DataFrame
    grouped_df = grouped_df.reset_index().rename(
        columns={True: "true_count", False: "false_count", np.nan: "unclear_count"}
    )

    if verbose:
        eval_string = f"<h5>Evaluation judgement in percentage: {int(eval_percentage) if eval_percentage.is_integer() else round(eval_percentage, 2)}%</h5>"
        display(HTML(eval_string))
        _display_styled_html(grouped_df)

    grouped_df.columns.name = 'index'
    return grouped_df


def get_evaluation_details(
    evaluation_id: str,
    table_name: str = 'evaluation_output',
    get_all_rows: bool = False,
    verbose: bool = False,
):
    """
    Get evaluation details of a single run.

    Parameters
    ----------
    evaluation_id : str
        Unique id for the evaluation run.
    table_name : str, optional
        Table name to store the evaluation result. Default to 'evaluation_output'.
    get_all_rows : bool, optional
        Flag to get all the rows for an evaluation. Default to False, which returns only failed evaluation rows.
    verbose : bool, optional
        Flag to print the evaluation summary. Default to False.

    Returns
    -------
    pd.DataFrame
        DataFrame with single evaluation details.
    """

    # Get the delta table
    delta_table = _get_delta_table(table_name)

    # Return if table is not found
    if delta_table is None:
        return None

    filters = [("evaluation_id", "=", evaluation_id)]
    # Filter for only failed rows if get_all_rows is False
    if not get_all_rows:
        filters.append(("evaluation_judgement", "=", False))

    # Convert to pandas DataFrame
    df = delta_table.to_pandas(filters=filters)

    if verbose:
        if df.empty:
            display(HTML('<b>There are no failed evaluation rows.</b> Use <i>get_all_rows</i> parameter as <i>True</i> to display all the evaluation rows.'))
            return df
        
        selected_cols_df = df[
            [
                "question",
                "expected_answer",
                "evaluation_judgement",
            ]
        ]

        actual_answers = []
        thread_urls = []
        for index, row in df.iterrows():
            actual_answers.append(f'<pre>{row["actual_answer"]}</pre>')
            thread_urls.append(
                f'<a href="{row["thread_url"]}" target="_blank">{row["thread_id"]}</a>'
            )

        selected_cols_df = selected_cols_df.assign(
            actual_answer=actual_answers, thread_url=thread_urls
        )

        selected_cols_df['actual_answer'] = selected_cols_df[
            'actual_answer'
        ].str.replace('\n', '<br>')

        _display_styled_html(selected_cols_df)

    return df


def _default_lakehouse_path():
    """
    Get default lakehouse path.

    Returns
    -------
    str
        Default lakehouse path.
    """
    defaultFs = get_fabric_context().get('fs.defaultFS')
    lakehouse_id = get_fabric_context().get('trident.lakehouse.id')
    return f"{defaultFs}{lakehouse_id}"


def _get_delta_table(table_name: str):
    """
    Get delta table.

    Parameters
    ----------
    table_name : str
        Table name which contains the evaluation result.

    Returns
    -------
    DeltaTable
        Delta table instance for provided table name.
    """

    from deltalake import DeltaTable

    lakehouse_path = _default_lakehouse_path()
    try:
        # Load the Delta Lake table
        delta_table = DeltaTable(f"{lakehouse_path}/Tables/{table_name}")
    except Exception:
        message = f"<h4>File does not exist. Please provide the folder path with 'evaluation_output.xlsx' file.</h4>"
        display(HTML(message))
        return None

    return delta_table


def _display_styled_html(df: pd.DataFrame):
    """
    Display styled html of a Dataframe.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame with processed output rows.
    """

    # Convert DataFrame to HTML and add inline CSS to enforce left alignment
    html_table = df.to_html(escape=False, index=False)

    # Modify the HTML output to enforce left alignment
    styled_html = html_table.replace(
        '<th>', '<th><div style="text-align: center !important;">'
    ).replace('</th>', '</div></th>')
    styled_html = styled_html.replace(
        '<td>', '<td><div style="text-align: left !important;">'
    ).replace('</td>', '</div></td>')

    display(HTML(styled_html))
