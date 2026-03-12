"""Common utility functions for FalconPy scripts."""

from typing import Dict, Any, List
import json


def check_response(response: Dict[str, Any], operation_name: str = "API call") -> bool:
    """
    Check if an API response was successful and print errors if not.

    Args:
        response: The response dictionary from a FalconPy API call
        operation_name: Name of the operation for error messages

    Returns:
        True if successful, False otherwise
    """
    status_code = response.get('status_code')

    if status_code in [200, 201, 202, 204]:
        return True

    print(f"❌ {operation_name} failed with status code: {status_code}")

    if 'body' in response and 'errors' in response['body']:
        errors = response['body']['errors']
        for error in errors:
            print(f"   Error: {error.get('message', 'Unknown error')}")

    return False


def extract_resources(response: Dict[str, Any]) -> List[Any]:
    """
    Extract resources from an API response.

    Args:
        response: The response dictionary from a FalconPy API call

    Returns:
        List of resources, or empty list if not found
    """
    if 'body' in response and 'resources' in response['body']:
        return response['body']['resources']
    return []


def print_json(data: Any, indent: int = 2) -> None:
    """
    Pretty-print JSON data.

    Args:
        data: Data to print (dict, list, etc.)
        indent: Indentation level for JSON formatting
    """
    print(json.dumps(data, indent=indent, default=str))


def paginate_results(api_method, **kwargs) -> List[Any]:
    """
    Paginate through all results from an API method that supports pagination.

    Args:
        api_method: The FalconPy API method to call
        **kwargs: Additional arguments to pass to the API method

    Returns:
        List of all resources across all pages
    """
    all_resources = []
    offset = None

    while True:
        if offset:
            kwargs['offset'] = offset

        response = api_method(**kwargs)

        if not check_response(response, "Pagination request"):
            break

        resources = extract_resources(response)
        all_resources.extend(resources)

        # Check if there are more pages
        if 'body' in response and 'meta' in response['body']:
            pagination = response['body']['meta'].get('pagination', {})
            offset = pagination.get('offset')

            if not offset:
                break
        else:
            break

    return all_resources


def format_timestamp(timestamp: str) -> str:
    """
    Format a Falcon API timestamp for display.

    Args:
        timestamp: ISO format timestamp string

    Returns:
        Formatted timestamp string
    """
    from datetime import datetime

    try:
        dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        return dt.strftime('%Y-%m-%d %H:%M:%S UTC')
    except:
        return timestamp


def chunk_list(items: List[Any], chunk_size: int) -> List[List[Any]]:
    """
    Split a list into chunks of specified size.

    Args:
        items: List to split
        chunk_size: Size of each chunk

    Returns:
        List of chunks
    """
    return [items[i:i + chunk_size] for i in range(0, len(items), chunk_size)]
