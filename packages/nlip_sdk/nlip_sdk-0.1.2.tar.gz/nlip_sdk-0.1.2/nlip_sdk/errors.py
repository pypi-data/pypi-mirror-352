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
This file defines some common types of exceptions in the code. 
They are defined as children of PrivateException class so that 
all children of PrivateException can be caught and handled. 

"""


class PrivateException(Exception):
    """
    The Exception that provides the root for all exceptions in this package

    Constructor Arguments:
        message (str): The diagnostic message to be passed to exception super-class
    """
    def __init__(self, message: str):
        super().__init__(message)


class UnitializedConfigurationError(PrivateException):
    """
    This Exception is raised when a configuration parameter is not defined.

    Constructor Arguments:
        parameter (str): The name of the parameter that is not initialized
    """
    def __init__(self, parameter:str):
        super().__init__(f"Configuration parameter {parameter} needs to be defined")


class RethrownException(PrivateException):
    """
    Sometimes it is convenient to rethrow an exception as a child of PrivateException
    This allows catching the other exception which may not be a child of PrivateException.
    

    Constructor Arguments:
        message (str): The additional message to be added to the original exception
        e (Exception): The original exception that is being rethrown
    """
    def __init__(self, message: str, e: Exception = None):
        if e is None:
            super().__init__(message)
        else:
            super().__init__(f"{message} generated exception {e}")


class UnImplementedError(PrivateException):
    """
    When placeholder functions are provided, with the expectation that they will be 
    implemented either in a subclass, or in another module, a class may forget to 
    define a required function. The UnimplementedError exception is raised in the 
    default implementation of the function -- which allows one to identify such 
    unimplemented functions during implementationa nd development. 
    

    Constructor Arguments:
        function_name (str): The name of the function that is not implemented 
        class_name (str): The name of the class which should have implemented the function.
                          If the function was not defined within a class, this argument can be None.
    """
    def __init__(
        self,
        function_name: str,
        class_name: str = None,
    ):
        if class_name is None:
            message = f"function {function_name} is not implemented"
        else:
            message = (
                f"function {function_name} in class {class_name} is not implemented"
            )
        super().__init__(message)
