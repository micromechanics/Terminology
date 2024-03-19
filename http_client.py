""" Http client for communicating with servers """
#  PASTA-ELN and all its sub-parts are covered by the MIT license.
#
#  Copyright (c) 2023
#
#  Author: Jithu Murugan
#  Filename: webclient.py
#
#  You should have received a copy of the license with this file. Please refer the license file for more information.
import logging
from asyncio import CancelledError, IncompleteReadError, InvalidStateError, LimitOverrunError, \
  TimeoutError as AsyncTimeoutError
from functools import wraps
from json import JSONDecodeError
from typing import Any, Callable
from typing import Union

from aiohttp import BasicAuth, ClientResponse, ClientSession
from aiohttp import ClientConnectorError, InvalidURL


def handle_http_client_exception(wrapped: Callable[..., Any]) -> Callable[..., Any]:
  """
  Handle exceptions from http client methods.
  Args:
    wrapped (Callable): The wrapped function where the exceptions can be raised.

  Returns:
    The wrapper function which handles the exceptions.
  """

  @wraps(wrapped)
  async def wrapper(self: Any, *args: object, **kwargs: object) -> Any:
    try:
      return await wrapped(self, *args, **kwargs)
    except AsyncTimeoutError as e:
      url = kwargs["base_url"] if 'base_url' in kwargs else args[0]
      error = f"Client session request timeout for url ({url}) with error: {e}"
      self.logger.error(error)
      self.session_request_errors.append(error)
      return {}
    except CancelledError as e:
      url = kwargs["base_url"] if 'base_url' in kwargs else args[0]
      error = f"Client session request cancelled for url ({url}) with error: {e}"
      self.logger.error(error)
      self.session_request_errors.append(error)
      return {}
    except InvalidStateError as e:
      url = kwargs["base_url"] if 'base_url' in kwargs else args[0]
      error = f"Client session request in invalid state for url ({url}) with error: {e}"
      self.logger.error(error)
      self.session_request_errors.append(error)
      return {}
    except IncompleteReadError as e:
      url = kwargs["base_url"] if 'base_url' in kwargs else args[0]
      error = f"Client session request incomplete read for url ({url}) with error: {e}"
      self.logger.error(error)
      self.session_request_errors.append(error)
      return {}
    except LimitOverrunError as e:
      url = kwargs["base_url"] if 'base_url' in kwargs else args[0]
      error = f"Client session request limit overrun for url ({url}) with error: {e}"
      self.logger.error(error)
      self.session_request_errors.append(error)
      return {}
    except TypeError as e:
      url = kwargs["base_url"] if 'base_url' in kwargs else args[0]
      error = f"Client session type error for url ({url}) with error: {e}"
      self.logger.error(error)
      self.session_request_errors.append(error)
      return {}
    except ClientConnectorError as e:
      url = kwargs["base_url"] if 'base_url' in kwargs else args[0]
      error = f"ClientConnectorError for url ({url}) with error: {e}"
      self.logger.error(error)
      self.session_request_errors.append(error)
      return {}
    except InvalidURL as e:
      url = kwargs["base_url"] if 'base_url' in kwargs else args[0]
      error = f"Client session InvalidURL for url ({url}) with error: {e}"
      self.logger.error(error)
      self.session_request_errors.append(error)
      return {}
    except JSONDecodeError as e:
      url = kwargs["base_url"] if 'base_url' in kwargs else args[0]
      error = f"Client session JSONDecodeError for url ({url}) with error: {e}"
      self.logger.error(error)
      self.session_request_errors.append(error)
      return {}
    except AssertionError as e:
      url = kwargs["base_url"] if 'base_url' in kwargs else args[0]
      error = f"Client session AssertionError for url ({url}) with error: {e}"
      self.logger.error(error)
      self.session_request_errors.append(error)
      return {}
    except ValueError as e:
      url = kwargs["base_url"] if 'base_url' in kwargs else args[0]
      error = f"Client session ValueError for url ({url}) with error: {e}"
      self.logger.error(error)
      self.session_request_errors.append(error)
      return {}

  return wrapper


async def prepare_result(response: ClientResponse) -> dict[str, Any]:
  """
  Prepare the result from the http response
  Args:
    response (ClientResponse): The response object returned after GET/POST/DELETE/PUT Commands

  Returns:
    dict[str, Any]: The result is returned as a dictionary
      {
        "status": response.status,
        "headers": response.headers,
        "reason": response.reason,
        "result": response.result
      }

  """
  result = {
    "status": response.status,
    "headers": response.headers,
    "reason": response.reason
  }
  match response.headers.get('Content-Type'):
    case x if "json" in x:  # type: ignore[operator]
      result["result"] = await response.json()
    case _:
      result["result"] = await response.text()
  return result


class AsyncHttpClient:
  """
  Asynchronous http client for communicating with REST based servers.
  """

  def __init__(self, session_timeout: int = 5) -> None:
    self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    self.session_timeout = session_timeout  # Timeout in seconds for the requests send to the lookup services
    self.session_request_errors: list[str] = []  # List of request errors

  @handle_http_client_exception
  async def get(self,
                base_url: str,
                request_params: Union[dict[str, Any], None] = None,
                request_headers: Union[dict[str, Any], None] = None,
                auth: Union[BasicAuth, None] = None,
                timeout: Union[int, None] = None) -> dict[str, Any]:
    """
    Send get request to the given url and parameters
    Args:
      base_url (str): Base url
      request_params (dict[str, Any]): Request parameters for the get request
      request_headers (dict[str, Any]): Request headers for the get request
      auth (BasicAuth): Basic authentication
      timeout (int): Timeout in seconds

    Returns (dict[str, Any]):
      The result is returned as a dictionary
      {
        "status": response.status,
        "headers": response.headers,
        "reason": response.reason,
        "result": response.result
      }
    """
    self.logger.info("Get url: %s", base_url)
    self.session_request_errors.clear()
    async with ClientSession() as session:
      async with session.get(base_url,
                             params=request_params,
                             headers=request_headers,
                             timeout=timeout if timeout is not None else self.session_timeout,
                             auth=auth) as response:
        result = await prepare_result(response)
    return result

  @handle_http_client_exception
  async def post(self,
                 base_url: str,
                 request_params: Union[dict[str, Any], None] = None,
                 request_headers: Union[dict[str, Any], None] = None,
                 json: Union[dict[str, Any], None] = None,
                 data: Union[Any, None] = None,
                 auth: Union[BasicAuth, None] = None,
                 timeout: Union[int, None] = None) -> dict[str, Any]:
    """
    Send post request to the given url and parameters
    Args:
      base_url (str): Base url
      request_params (dict[str, Any]): Request parameters for the post request
      request_headers (dict[str, Any]): Request headers for the post request
      json (dict[str, Any]): Json data for the post request
      data (Any): Data for the post request
      auth (BasicAuth): Basic authentication
      timeout (int): Timeout in seconds

    Returns:
      The result is returned as a dictionary
      {
        "status": response.status,
        "headers": response.headers,
        "reason": response.reason,
        "result": response.result
      }
    """
    self.logger.info("Post url: %s", base_url)
    self.session_request_errors.clear()
    async with ClientSession() as session:
      async with session.post(base_url,
                              headers=request_headers,
                              params=request_params,
                              timeout=timeout if timeout is not None else self.session_timeout,
                              json=json,
                              data=data,
                              auth=auth) as response:
        result = await prepare_result(response)
    return result

  @handle_http_client_exception
  async def delete(self,
                   base_url: str,
                   request_params: Union[dict[str, Any], None] = None,
                   request_headers: Union[dict[str, Any], None] = None,
                   json: Union[dict[str, Any], None] = None,
                   data: Union[Any, None] = None,
                   auth: Union[BasicAuth, None] = None,
                   timeout: Union[int, None] = None) -> dict[str, Any]:
    """
    Send delete request to the given url and parameters.
    Args:
      base_url (str): Base url
      request_params (dict[str, Any]): Request parameters for the delete request
      request_headers (dict[str, Any]): Request headers for the delete request
      json (dict[str, Any]): Json data for the delete request
      data (Any): Data for the delete request
      auth (BasicAuth): Basic authentication
      timeout (int): Timeout in seconds

    Returns:
      The result is returned as a dictionary
      {
        "status": response.status,
        "headers": response.headers,
        "reason": response.reason,
        "result": response.result
      }
    """
    self.logger.info("Delete url: %s", base_url)
    self.session_request_errors.clear()
    async with ClientSession() as session:
      async with session.delete(base_url,
                                headers=request_headers,
                                params=request_params,
                                timeout=timeout if timeout is not None else self.session_timeout,
                                json=json,
                                data=data,
                                auth=auth) as response:
        result = await prepare_result(response)
    return result
