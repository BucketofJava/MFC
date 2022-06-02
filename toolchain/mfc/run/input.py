
import os
import json
import dataclasses

import rich

import common

#import run.case_dicts as case_dicts
import case

@dataclasses.dataclass
class MFCInputFile:
    filename:     str
    case_dirpath: str
    case_dict:    dict

    # Generate .inp and case.fpp input files.
    def dump(self,  target_name: str) -> None:
        # === case.fpp ===
        filepath = f"{os.getcwd()}/src/common/case.fpp"
        content  = f"""\
! This file was generated by MFC to
! describe the case one wishes to run.

#:set CASE={self.case_dict}

"""

        # Check if this case already has a case.fpp file.
        # If so, we don't need to generate a new one, which
        # would cause a partial and unnecessary rebuild.
        if os.path.exists(filepath):
            with open(filepath, "r") as f:
                if f.read() == content:
                    return

        common.file_write(filepath, content)


# Load from Python input file
def load(filename: str) -> MFCInputFile:
    dirpath:    str  = os.path.abspath(os.path.dirname(filename))
    dictionary: dict = {}

    rich.print(f"> > Fetching case dictionary from {filename}...")

    if not os.path.exists(filename):
        raise common.MFCException(f"Input file '{filename}' does not exist. Please check the path is valid.")

    if filename.endswith(".py"):
        (json_str, err) = common.get_py_program_output(filename)

        if err != 0:
            raise common.MFCException(f"Input file {filename} terminated with a non-zero exit code. Please make sure running the file doesn't produce any errors.")
    elif filename.endswith(".json"):
        json_str = common.file_read(filename)
    else:
        raise common.MFCException("Unrecognized input file format. Only .py and .json files are supported. Please check the README and sample cases in the samples directory.")
    
    try:
        dictionary = json.loads(json_str)
    except Exception as exc:
        raise common.MFCException(f"Input file {filename} did not produce valid JSON. It should only print the case dictionary.\n\n{exc}\n")

    return MFCInputFile(filename, dirpath, dictionary)
