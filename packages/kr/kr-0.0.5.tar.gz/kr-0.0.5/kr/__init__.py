"""Utils to work with json"""


import json
import traceback

__author__ = 'tcw'


def get_dict_of_error_object(error_object, with_traceback=True):

    msg_dict = {'error': str(error_object.__class__), 'message': error_object.args[0]}
    if with_traceback:
        msg_dict['traceback'] = traceback.format_exc()


def get_json_of_error_object(error_object):
    return json.dumps(get_dict_of_error_object(error_object))



def update_error_object_with_additional_info(error_object, additional_info, with_traceback=True):
    """
    Enhances the error dictionary with additional information provided by the user.

    Parameters:
        error_object (Exception): The exception object to serialize.
        additional_info (dict): A dictionary containing additional information to be added to the error object.
        with_traceback (bool, optional): Boolean flag to determine if traceback information should be included. Defaults to True.

    Returns:
        dict: A dictionary containing the error type, message, additional information, and optionally the traceback.

    Example:
        try:
            1 / 0
        except Exception as e:
            error_info = update_error_object_with_additional_info(e, {'function': 'division', 'input': 'zero'})
            print(error_info)
    """
    error_dict = get_dict_of_error_object(error_object, with_traceback=with_traceback)
    error_dict.update(additional_info)
    return error_dict

def log_error_to_file(error_object, file_path, with_traceback=True):
    """
    Logs the error object into a file in JSON format.

    Parameters:
        error_object (Exception): The exception object to serialize and log.
        file_path (str): The path to the file where the error log should be written.
        with_traceback (bool, optional): Boolean flag to determine if traceback information should be included. Defaults to True.

    Example:
        try:
            1 / 0
        except Exception as e:
            log_error_to_file(e, 'error_log.txt')
    """
    import os

    error_json = get_json_of_error_object(error_object)
    with open(file_path, 'a') as file:
        file.write(error_json + os.linesep)



def serialize_error_to_dict(error_object, include_traceback=False):
    """
    Serializes an error object to a dictionary with options to include detailed traceback information.

    Parameters:
        error_object (Exception): The exception object to serialize.
        include_traceback (bool, optional): Flag to include traceback information in the output. Defaults to False.

    Returns:
        dict: A dictionary containing the error type, message, and optionally the traceback.

    Example:
        try:
            result = 10 / 0
        except Exception as e:
            error_dict = serialize_error_to_dict(e, include_traceback=True)
            print(error_dict)
    """
    error_info = {
        'error_type': str(error_object.__class__.__name__),
        'message': str(error_object)
    }
    if include_traceback:
        import traceback
        error_info['traceback'] = traceback.format_exc()
    return error_info

def print_error_details(error_object, include_traceback=False):
    """
    Prints the details of an error object to the console, optionally including traceback information.

    Parameters:
        error_object (Exception): The exception object whose details are to be printed.
        include_traceback (bool, optional): Flag to include traceback information in the output. Defaults to False.

    Example:
        try:
            result = 10 / 0
        except Exception as e:
            print_error_details(e, include_traceback=True)
    """
    error_details = serialize_error_to_dict(error_object, include_traceback=include_traceback)
    for key, value in error_details.items():
        print(f"{key}: {value}")
