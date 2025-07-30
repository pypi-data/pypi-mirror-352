"""## Package Documentation
This package provides utility functions for reading from and writing to pandas DataFrames. It includes support for handling Excel files, Parquet files, and CSV files. The functions are designed to integrate with a metadata-driven workflow, allowing for flexible input and output configurations.

### Functions

#### `read_csv(data: dict[str, Any]) -> dict[str, Any]`
Reads a CSV file into a pandas DataFrame.

- `input_path`: Directory path for the input file. If it is a directory and `file_name` is not specified, the output will be `None`. Defaults to the value identified by the label `constants.DEFAULT_IO_DATA_LABEL` (if it is a string).
- `relative_path`: Boolean indicating if `input_path` is relative. Defaults to `False`.
- `csv_file_extension_only`: If `True`, the function will only read files with a `.csv` extension, returning `None` otherwise.
- `file_name`: Name of the CSV file to append to `input_path`.
- `separator`: Field delimiter for the CSV file. Defaults to `,`.
- `skip_rows`: Number of rows to skip at the top of the CSV file or a list of zero-based row indexes to skip.
- `engine`: Engine to use for reading the CSV file. Defaults to `c`.

- Updates `data` with the content of the CSV file as a pandas DataFrame, identified by the label `output`. Defaults to `constants.DEFAULT_IO_DATA_LABEL`.

---

#### `read_excel_worksheets(data: dict[str, Any]) -> dict[str, Any]`
Reads worksheets from an Excel file into a dictionary of pandas DataFrames.

**Yaml Arguments:**
- `input_path`: Directory path for the input file (default: `constants.DEFAULT_IO_DATA_LABEL` if it is a string).
- `relative_path`: Boolean indicating if `input_path` is relative (default: `False`).
- `file_name`: Name of the Excel file.
- `skip_rows`: Number of top rows or list of zero-based row indexes to skip in each worksheet.
- `skip_worksheets`: List of zero-based worksheet indices or names to skip.
- `engine`: Engine to use for reading the Excel file (default: `openpyxl`).

**Returns:**
- Updates `data` with a dictionary of DataFrames, keyed by worksheet names.

---

#### `write_parquet(data: dict[str, Any]) -> dict[str, Any]`
Writes a pandas DataFrame to a Parquet file.

**Yaml Arguments:**
- `input`: Label in `data` identifying the input DataFrame (default: `constants.DEFAULT_IO_DATA_LABEL`).
- `output_path`: Directory path for the output file.
- `relative_path`: Boolean indicating if `output_path` is relative (default: `False`).
- `file_name`: Name of the output Parquet file (default: `constants.DEFAULT_OUTPUT_FILE`).
- `preserve_index`: Whether to preserve the DataFrame index in the Parquet file.

**Returns:**
- Updates `data` with the input DataFrame under the specified output label.

---

#### `write_csv(data: dict[str, Any]) -> dict[str, Any]`
Writes a pandas DataFrame to a CSV file.

**Yaml Arguments:**
- `input`: Label in `data` identifying the input DataFrame (default: `constants.DEFAULT_IO_DATA_LABEL`).
- `output_path`: Directory path for the output file.
- `relative_path`: Boolean indicating if `output_path` is relative (default: `False`).
- `file_name`: Name of the output CSV file (default: `constants.DEFAULT_OUTPUT_FILE`).
- `separator`: Field delimiter for the CSV file (default: `,`).

**Returns:**
- Updates `data` with the input DataFrame under the specified output label.

---

### Dependencies
- `pandas`: For DataFrame manipulation and file I/O.
- `pyarrow`: For handling Parquet files.
- `mcpf_core`: For metadata and routine utilities.

### Usage
Import the package and call the desired function with the appropriate arguments. Ensure that the `data` dictionary contains the necessary metadata and input/output labels.
"""

import os
from typing import Any

import mcpf_core.core.routines as routines
import mcpf_core.func.constants as constants
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq


def read_csv(data: dict[str, Any]) -> dict[str, Any]:
    """
    It reads the given input csv file.
    Yaml args:
        'input_path':       a string containing a directory path; if it is
                            a directory, and `file_name` is not specified,
                            the output will be None.
                            by default it is the value identified with the label
                            constants.DEFAULT_IO_DATA_LABEL (if it is a string)
        'relative_path':    a bool value, if it is 'True' the given 'input_path' is a relative path
                            by default it is 'False'
        'csv_file_extension_only': If 'True', the function will only read files with a `csv` extension,
                            returning None otherwise.
        'file_name':        file name to append to `input_path`
        'separator':        a string, the field delimiter for the csv file, by default `,`.
        'skip_rows':        count of rows to skip at the top of the csv file or list
                            of zero-based row indexes to skip
        'engine':           engine to use for reading the csv file, by default it is 'c'

    Returns in data:
        'output':   it is a label in 'data' which identifies the output
                    (the content of the csv file in pandas dataframe),
                    by default it is constants.DEFAULT_IO_DATA_LABEL
    """
    # general code part 2/1
    iterator = routines.pop_loop_iterator()
    meta = routines.get_meta_data(data)

    # default_arguments_values
    default_input_path = "."
    if constants.DEFAULT_IO_DATA_LABEL in data and isinstance(data[constants.DEFAULT_IO_DATA_LABEL], str):
        default_input_path = data[constants.DEFAULT_IO_DATA_LABEL]
    arg = {
        "output": constants.DEFAULT_IO_DATA_LABEL,
        "input_path": default_input_path,
        "file_name": "",
        "relative_path": False,
        "csv_file_extension_only": False,
        "separator": ",",
        "skip_rows": 0,
        "engine": "c",
    }
    # merging default values with current argument values
    if meta[constants.ARGUMENTS]:
        arg = arg | meta[constants.ARGUMENTS]
    # if the function part of a loop
    if iterator:
        arg["input_path"] = iterator

    # specific code part
    if arg["file_name"]:
        arg["input_path"] = os.path.join(arg["input_path"], arg["file_name"])

    if arg["relative_path"]:
        arg["input_path"] = os.path.join(routines.get_current_input_dir(meta), arg["input_path"])
    if not os.path.isdir(arg["input_path"]) and (
        not arg["csv_file_extension_only"] or arg["input_path"][-3:].lower() == "csv"
    ):
        data[arg["output"]] = pd.read_csv(
            arg["input_path"], sep=arg["separator"], skiprows=arg["skip_rows"], engine=arg["engine"]
        )
    else:
        data[arg["output"]] = None

    # general code part 2/2
    routines.set_meta_in_data(data, meta)
    return data


def read_excel_worksheets(data: dict[str, Any]) -> dict[str, Any]:
    """
    It reads the worksheets from the given input excel file.
    Yaml args:
        'input_path':       a string containing a directory path,
                            by default it is the value identified with the label
                            constants.DEFAULT_IO_DATA_LABEL (if it is a string)
        'relative_path':    a bool value, if it is 'True' the given 'input_path' is a relative path
                            by default it is 'False'
        'file_name':        relative path and file name to be appended to `input_path`
        'skip_rows':        count of rows to skip at the top of each worksheet or list
                            of zero-based row indexes to skip in each worksheet
        'skip_worksheets':  list of zero-based worksheet indices or names to skip
        'engine':           engine to use for reading the excel file, by default it is 'openpyxl'

    Returns in data:
        'output':   it is a label in 'data' which identifies the output
                    (the content of the excel file in pandas dataframe),
                    by default it is constants.DEFAULT_IO_DATA_LABEL

                    In the case if the output consists of more excel worksheets, then the function returns
                    with a dictionary, where:
                        - the keys are the name of the worksheets
                        - the values are pandas dataframe
    """
    # general code part 2/1
    iterator = routines.pop_loop_iterator()
    meta = routines.get_meta_data(data)

    # default_arguments_values
    default_input_path = "."
    if constants.DEFAULT_IO_DATA_LABEL in data and isinstance(data[constants.DEFAULT_IO_DATA_LABEL], str):
        default_input_path = data[constants.DEFAULT_IO_DATA_LABEL]
    arg = {
        "output": constants.DEFAULT_IO_DATA_LABEL,
        "input_path": default_input_path,
        "file_name": "",
        "relative_path": False,
        "skip_rows": 0,
        "skip_worksheets": [],
        "engine": "openpyxl",
    }
    # merging default values with current argument values
    if meta[constants.ARGUMENTS]:
        arg = arg | meta[constants.ARGUMENTS]
    # if the function part of a loop
    if iterator:
        arg["input_path"] = iterator

    # specific code part
    if arg["file_name"]:
        arg["input_path"] = os.path.join(arg["input_path"], arg["file_name"])

    if arg["relative_path"]:
        arg["input_path"] = os.path.join(routines.get_current_input_dir(meta), arg["input_path"])
    xls = pd.ExcelFile(arg["input_path"], engine=arg["engine"])
    data[arg["output"]] = {}
    for nr, sheet_name in enumerate(xls.sheet_names):
        if nr in arg["skip_worksheets"] or sheet_name in arg["skip_worksheets"]:
            continue
        data[arg["output"]][sheet_name] = xls.parse(sheet_name, skiprows=arg["skip_rows"])

    if len(data[arg["output"]]) == 1:
        data[arg["output"]] = next(iter(data[arg["output"]].values()))

    # general code part 2/2
    routines.set_meta_in_data(data, meta)
    return data


def write_parquet(data: dict[str, Any]) -> dict[str, Any]:
    """
    It writes its pandas dataframe input to a parquet file.
    Yaml args:
        'input':            it is a label in "data", which identifies the input data
                            (given in terms of pandas dataframe),
                            by default it is the value identified with the label
                            constants.DEFAULT_IO_DATA_LABEL (if it is a string)
        'output_path':      Directory path for the output file, if not specified,
                            it defaults to the value of `constants.DEFAULT_IO_DATA_LABEL`
                            in the `data` dictionary.
        'relative_path':    a bool value, if it is 'True' the given 'output_path' is a relative path
                            by default it is 'False'
        'file_name':        relative path and file name to be appended to `output_path`,
                            by default it is constants.DEFAULT_OUTPUT_FILE
        'preserve_index':   None (default) means the index is preserved in the output
                            file, `false` means the index omitted from the output file

    Returns in data:
        'output':   it is a label in 'data' which identifies the output
                    (the content of the input in pandas dataframe),
                    by default it is constants.DEFAULT_IO_DATA_LABEL
    """
    # general code part 2/1
    iterator = routines.pop_loop_iterator()
    meta = routines.get_meta_data(data)

    # default_arguments_values
    default_output_path = "."
    arg = {
        "input": constants.DEFAULT_IO_DATA_LABEL,
        "output": constants.DEFAULT_IO_DATA_LABEL,
        "output_path": default_output_path,
        "file_name": data[constants.DEFAULT_OUTPUT_FILE] if constants.DEFAULT_OUTPUT_FILE in data else "",
        "relative_path": False,
        "preserve_index": None,
    }
    # merging default values with current argument values
    if meta[constants.ARGUMENTS]:
        arg = arg | meta[constants.ARGUMENTS]
    # if the function part of a loop
    # if iterator:
    #    arg['output_path'] = iterator

    # specific code part
    if arg["file_name"]:
        arg["output_path"] = os.path.join(arg["output_path"], arg["file_name"])

    if arg["relative_path"]:
        arg["output_path"] = os.path.join(routines.get_current_tmp_dir(meta), arg["output_path"])

    if not os.path.exists(os.path.dirname(arg["output_path"])):
        os.makedirs(os.path.dirname(arg["output_path"]))

    pq.write_table(pa.Table.from_pandas(data[arg["input"]], preserve_index=arg["preserve_index"]), arg["output_path"])
    if arg["input"] != arg["output"]:
        data[arg["output"]] = data[arg["input"]]
    # general code part 2/2
    routines.set_meta_in_data(data, meta)
    return data


def write_csv(data: dict[str, Any]) -> dict[str, Any]:
    """
        It writes its pandas dataframe input to a csv file.
    Yaml args:
        'input':            it is a label in "data", which identifies the input data
                            (given in terms of pandas dataframe),
                            by default it is the value identified with the label
                            constants.DEFAULT_IO_DATA_LABEL (if it is a string)
        'output_path':      Directory path for the output file, if not specified,
                            it defaults to the value of `constants.DEFAULT_IO_DATA_LABEL`
                            in the `data` dictionary.
        'relative_path':    a bool value, if it is 'True' the given 'output_path' is a relative path
                            by default it is 'False'
        'file_name':        relative path and file name to be appended to `output_path`,
                            by default it is constants.DEFAULT_OUTPUT_FILE
        'separator':        a string, the field delimiter for the csv file, by default it is ','

    Returns in data:
        'output':   it is a label in 'data' which identifies the output
                    (the content of the input in pandas dataframe),
                    by default it is constants.DEFAULT_IO_DATA_LABEL
    """
    # general code part 2/1
    iterator = routines.pop_loop_iterator()
    meta = routines.get_meta_data(data)

    # default_arguments_values
    default_output_path = "."
    arg = {
        "input": constants.DEFAULT_IO_DATA_LABEL,
        "output": constants.DEFAULT_IO_DATA_LABEL,
        "output_path": default_output_path,
        "file_name": data[constants.DEFAULT_OUTPUT_FILE] if constants.DEFAULT_OUTPUT_FILE in data else "",
        "relative_path": False,
        "separator": ",",
    }
    # merging default values with current argument values
    if meta[constants.ARGUMENTS]:
        arg = arg | meta[constants.ARGUMENTS]
    # if the function part of a loop
    # if the function part of a loop
    # if iterator:
    #    arg['output_path'] = iterator

    # specific code part
    if arg["file_name"]:
        arg["output_path"] = os.path.join(arg["output_path"], arg["file_name"])

    if arg["relative_path"]:
        arg["output_path"] = os.path.join(routines.get_current_tmp_dir(meta), arg["output_path"])

    if not os.path.exists(os.path.dirname(arg["output_path"])):
        os.makedirs(os.path.dirname(arg["output_path"]))

    data[arg["input"]].to_csv(arg["output_path"], sep=arg["separator"], index=False)
    if arg["input"] != arg["output"]:
        data[arg["output"]] = data[arg["input"]]
    # general code part 2/2
    routines.set_meta_in_data(data, meta)
    return data
