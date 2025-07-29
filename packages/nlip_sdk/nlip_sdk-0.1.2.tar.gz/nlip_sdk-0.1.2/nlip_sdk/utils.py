"""
 *******************************************************************************
 * 
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 *******************************************************************************/
"""
# Documentation Assisted by WCA@IBM
# Latest GenAI contribution: ibm/granite-8b-code-instruct

"""
This file contains a variety of convenience routines. 
These routines are used to simplify file path management, 
reading file contents, and other functions that are used commonly 
across many other modules and solutions using NLIP. 

"""

import os
from pathlib import Path
from base64 import b64encode



def get_resolved_path(file_path: str) -> str:
    """
    Returns the absolute path of the given file path after resolving any symbolic links.

    Args:
        file_path (str): The path of the file to resolve.

    Returns:
        str: The absolute path of the resolved file.
    """
    return str(Path(file_path).resolve().absolute())

def get_parent_location(file_path: str) -> str:
    """
    Returns the absolute path of the parent directory of the given file path after resolving

    Args:
        file_path (str): The path of the file to resolve.

    Returns:
        str: The absolute path of the parent directory of the resolved file.
    """
    parent = Path(file_path).parent
    return str(parent.resolve().absolute())

def get_joined_path(file_path_1: str, file_path_2: str) -> str:
    """
    Returns the absolute path by concataning the two provided file_path arguments 
    The second file_path can be relative to the first file_path, e.g. using .. or . 
    Any of the two arguments can contain relative path names. 

    Args:
        file_path_1 (str): The first part of the file_path 
        file_path_2 (str): The second part of the file_path 

    Returns:
        str: The absolute path of the parent directory of the resolved file.
    """
    base_path = Path(file_path_1)
    this_path = base_path.joinpath(file_path_2)
    return str(this_path.resolve().absolute())



def make_destination_path(this_path: str) -> None:
    """
    Creates a directory leading to specified path if it does not already exist.
    This convenience routine ensures that a new file is being created in a directory
    that exists and will not fail because the directory is not present. 

    Args:
        this_path (str): The path to create the directory at.

    Returns:
        None
    """
    path = Path(this_path).resolve().absolute()
    path.parent.mkdir(parents=True, exist_ok=True)


def check_file_exists(filename) -> bool:
    """
    A quick check to see if a file exists. 

    Parameters:

        filename (str): The path to the file to check.
    Returns:

        bool: True if the file exists, False otherwise.

    """
    path = Path(filename).resolve().absolute()
    return os.path.exists(path)


def get_file_extension(filename: str) -> str | None:
    """
    Returns the extension of a file  

    Parameters:

        filename (str): The path to the file to get the extension
    Returns:

        str: The part of file name after the . sign. Returns None if no extension is found

    """
    if "." in filename:
        return "." + filename.rsplit(".", 1)[-1]
    return None

def read_binary_file(filename) -> str:
    """
    Reads a binary file and returns its base64 encoded content as a string.

    Args:
        filename (str): The path of the binary file to be read.

    Returns:
        str: The base64 encoded content of the file as a string.
    """
    with open(filename, "rb") as file:
        file_content = file.read()
        return b64encode(file_content).decode("utf-8")

def read_text_file(filename):
    """
    Reads the contents of a text file and returns it as a string.

    Args:
        filename (str): The path to the text file.

    Returns:
        str: The contents of the text file.
    """
    with open(filename, "rb") as file:
        return file.read()


def get_class_name(this_object: object) -> str:
    """
    get the class name of an object   

    Parameters:

        this_object (object): The object whose class is to be determined
    Returns:

        str: The name of the class of the object 

    """
    return this_object.__class__.__name__

