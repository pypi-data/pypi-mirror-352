The Fabric Data Agent SDK supports programmatic access for [Fabric Data Agent](https://learn.microsoft.com/en-us/fabric/data-science/concept-ai-skill) artifacts.

This package is released as a preview and has been tested with Microsoft Fabric Python notebooks.

# Getting started

## Prerequisites

* A [Microsoft Fabric subscription](https://learn.microsoft.com/en-us/fabric/enterprise/licenses). Or sign up for a free [Microsoft Fabric (Preview) trial](https://learn.microsoft.com/en-us/fabric/get-started/fabric-trial).
* Sign in to [Microsoft Fabric](https://fabric.microsoft.com/).
* Create [a new notebook](https://learn.microsoft.com/en-us/fabric/data-engineering/how-to-use-notebook#create-notebooks) or a new [spark job](https://learn.microsoft.com/en-us/fabric/data-engineering/create-spark-job-definition) to use this package. **Note that semantic link is supported only within Microsoft Fabric.**

## Install the `fabric-data-agent-sdk` package

To install the most recent version `fabric-data-agent-sdk` in your Fabric Python notebook kernel by executing this code in a notebook cell:

  ```python
  %pip install -U fabric-data-agent-sdk
  ```

# Key concepts

Fabric Data Agent SDK has two main entry points:

* Data plane using OpenAI SDK for conversational interaction with an existing Data Agent artifact.
* Management plane to create, update and delete Data Agent artifacts.

# Change logs

## 0.1.4a0

* switch to public apis for artifact management.

## 0.1.3a0

* add column/table descriptions for sql data sources.
* allow selection of multiple columns at once in the datasource.
* bug fix to address the run_steps response structure change.

## 0.1.2a0

* bugfix for *fabric_openai* artifact type - should support "DataAgent".
* bugfix for data source type ("datawarehouse" should be "warehouse").

## 0.1.1a0

* bugfix for *create_data_agent* where type should support "DataAgent".

## 0.1.0a0

* add upload_fewshots for adding multiple fewshots to DataSource.

## 0.0.4a0

* add evaluation APIs to the SDK

## 0.0.3a1

* return fewshot id from add_fewshots
* fix the aiskill stage parameter
* return datasource display name in pretty_print
* return thread object for get_or_create_thread API.

## 0.0.2a0

* rename module
* support Fabric get_or_create_thread to decouple from UX thread

## 0.0.1a0

Initial alpha release of the package.

* add: data plane client
* add: management plane client
