from rest_framework.response import Response
from rest_framework import status

def success_response(message, data=None, count=None, status_code=status.HTTP_200_OK):
    """
    Generate a standardized success response with optional count.

    Args:
    - message (str): The success message.
    - data (list): Optional data to include in the response (should default to an empty list).
    - count (int): Optional count of items.
    - status_code (int): The HTTP status code for the response.

    Returns:
    - Response: A DRF Response object with the standardized format.
    """
    response_data = {
        "status": status_code,
        "message": message
    }
    if count is not None:
        response_data['count'] = count
    response_data['data'] = data if data is not None else []  # Default to empty list

    return Response(response_data, status=status_code)


def error_response(message, validation_errors=None, status_code=status.HTTP_400_BAD_REQUEST):
    """
    Generate a standardized error response with optional validation errors.

    Args:
    - message (str): The error message.
    - validation_errors (dict or str): Optional dictionary of validation errors or a string.
    - status_code (int): The HTTP status code for the response.

    Returns:
    - Response: A DRF Response object with the standardized format.
    """
    response_data = {
        "status": status_code,
        "message": message,
    }
    
    if validation_errors is not None:
        if isinstance(validation_errors, dict):
            # If validation_errors is a dictionary, add it directly
            response_data['errors'] = validation_errors
        elif isinstance(validation_errors, str):
            # If it's a string, wrap it in a dictionary with a generic key
            response_data['errors'] = {'error': validation_errors}
        else:
            # Handle unexpected types
            response_data['errors'] = {'error': 'An unknown error occurred.'}

    return Response(response_data, status=status_code)