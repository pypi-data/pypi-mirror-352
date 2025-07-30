import inspect

import requests


def get(url, headers=None, params=None, timeout=10):
    """
    Make a GET request.

    Parameters
    ----------
    url : str
        The URL to request.
    headers : dict, optional
        Additional headers to include in the request.
    params : dict, optional
        URL parameters to pass with the request.
    timeout : int, optional
        Request timeout in seconds.

    Returns
    -------
    dict or list
        Parsed JSON response.

    Raises
    ------
    ConnectionError
        For network issues.
    RuntimeError
        For unexpected HTTP responses or JSON decode errors.
    ValueError
        If the resource is not found (404).

    """
    context = inspect.stack()[1].function

    try:
        response = requests.get(url, headers=headers, params=params, timeout=timeout)
    except requests.exceptions.Timeout:
        raise ConnectionError(f"Request timed out in {context}().")
    except requests.exceptions.ConnectionError:
        raise ConnectionError(f"Network connection error in {context}().")
    except requests.RequestException as e:
        raise RuntimeError(f"Error in {context}(): {e}")

    if response.status_code == 204:
        return {"status_code": 204}
    elif response.status_code == 200:
        try:
            return response.json()
        except ValueError:
            raise RuntimeError(f"Failed to parse JSON in {context}().")
    elif response.status_code == 404:
        raise ValueError(f"Resource not found in {context}().")
    elif (
        response.status_code == 403
        and response.headers.get("X-RateLimit-Remaining") == "0"
    ):
        raise RuntimeError("GitHub API rate limit exceeded.")
    else:
        raise RuntimeError(
            f"Unexpected response ({response.status_code}) in {context}(): "
            f"{response.text}"
        )


def post(url, headers=None, data=None, json=None, timeout=10):
    """
    Make a POST request.

    Parameters
    ----------
    url : str
        The URL to request.
    headers : dict, optional
        Additional headers to include in the request.
    data : dict or str, optional
        Data to send in the body of the request.
    json : dict, optional
        JSON data to send in the body of the request.
    timeout : int, optional
        Request timeout in seconds.

    Returns
    -------
    dict or list
        Parsed JSON response.

    Raises
    ------
    ConnectionError
        For network issues.
    RuntimeError
        For unexpected HTTP responses or JSON decode errors.
    ValueError
        If the resource is not found (404).

    """
    context = inspect.stack()[1].function

    try:
        response = requests.post(
            url, headers=headers, data=data, json=json, timeout=timeout
        )
    except requests.exceptions.Timeout:
        raise ConnectionError(f"Request timed out in {context}().")
    except requests.exceptions.ConnectionError:
        raise ConnectionError(f"Network connection error in {context}().")
    except requests.RequestException as e:
        raise RuntimeError(f"Error in {context}(): {e}")

    if response.status_code in (200, 201):
        try:
            return response.json()
        except ValueError:
            raise RuntimeError(f"Failed to parse JSON in {context}().")
    elif response.status_code == 204:
        return {"status_code": 204}
    elif response.status_code == 404:
        raise ValueError(f"Resource not found in {context}().")
    elif (
        response.status_code == 403
        and response.headers.get("X-RateLimit-Remaining") == "0"
    ):
        raise RuntimeError("GitHub API rate limit exceeded.")
    else:
        raise RuntimeError(
            f"Unexpected response ({response.status_code}) in {context}(): "
            f"{response.text}"
        )


def put(url, headers=None, data=None, json=None, timeout=10):
    """
    Make a PUT request.

    Parameters
    ----------
    url : str
        The URL to request.
    headers : dict, optional
        Additional headers to include in the request.
    data : dict or str, optional
        Data to send in the body of the request.
    json : dict, optional
        JSON data to send in the body of the request.
    timeout : int, optional
        Request timeout in seconds.

    Returns
    -------
    dict or list
        Parsed JSON response.

    Raises
    ------
    ConnectionError
        For network issues.
    RuntimeError
        For unexpected HTTP responses or JSON decode errors.
    ValueError
        If the resource is not found (404).

    """
    context = inspect.stack()[1].function

    try:
        response = requests.put(
            url, headers=headers, data=data, json=json, timeout=timeout
        )
    except requests.exceptions.Timeout:
        raise ConnectionError(f"Request timed out in {context}().")
    except requests.exceptions.ConnectionError:
        raise ConnectionError(f"Network connection error in {context}().")
    except requests.RequestException as e:
        raise RuntimeError(f"Error in {context}(): {e}")

    if response.status_code in (200, 201):
        try:
            return response.json()
        except ValueError:
            raise RuntimeError(f"Failed to parse JSON in {context}().")
    elif response.status_code == 204:
        return {"status_code": 204}
    elif response.status_code == 404:
        raise ValueError(f"Resource not found in {context}().")
    elif (
        response.status_code == 403
        and response.headers.get("X-RateLimit-Remaining") == "0"
    ):
        raise RuntimeError("GitHub API rate limit exceeded.")
    else:
        raise RuntimeError(
            f"Unexpected response ({response.status_code}) in {context}(): "
            f"{response.text}"
        )
