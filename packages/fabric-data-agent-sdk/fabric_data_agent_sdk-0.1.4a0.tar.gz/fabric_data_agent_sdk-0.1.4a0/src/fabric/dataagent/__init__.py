_warning_printed = False

if not _warning_printed:
    _warning_printed = True
    try:
        import os

        if os.environ.get("MSNOTEBOOKUTILS_RUNTIME_TYPE", "").lower() != "jupyter":
            print("Warning: This package is only supported in Fabric Python notebook.")
    except:  # noqa: E722
        pass
