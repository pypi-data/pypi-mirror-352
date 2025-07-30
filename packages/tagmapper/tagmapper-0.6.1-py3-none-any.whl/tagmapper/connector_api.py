import json
import logging
from types import SimpleNamespace
from typing import Dict, List, Literal, Optional, Union
from azure.identity import DefaultAzureCredential
import requests
from msal_bearer import BearerAuth, get_user_name
from io import BytesIO
import os


logger = logging.getLogger(__name__)

_token = ""
_user_name = ""


def set_token(token: str) -> None:
    """Setter for global property token.

    Args:
        token (str): Token to set.
    """
    global _token
    _token = token


def get_token() -> str:
    """Getter for token. Will first see if a global token has been set, then try to get a token using app registration, then last try to get via azure authentication.

    Returns:
        str: Authentication token
    """
    if _token:

        return _token

    token = get_app_token()

    if token:
        return token

    return get_az_token()


def get_az_token() -> str:
    """Getter for token uzing azure authentication.

    Returns:
        str: Token from azure authentication
    """
    credential = DefaultAzureCredential()
    databaseToken = credential.get_token("582e9f1c-1814-449b-ae6c-0cdc5fecdba2")
    return databaseToken[0]


def get_app_bearer(username: str = "") -> str:
    global _user_name

    if not username:
        if not _user_name:
            _user_name = get_user_name()
        username = _user_name  # type: ignore
    else:
        _user_name = username

    # SHORTNAME@equinor.com -- short name shall be capitalized
    username = username.upper()  # Also capitalize equinor.com
    if not username.endswith("@EQUINOR.COM"):
        username = username + "@EQUINOR.COM"

    tenantID = "3aa4a235-b6e2-48d5-9195-7fcf05b459b0"
    clientID = "5850cfaf-0427-4e96-9813-a7874c8324ae"

    scope = ["582e9f1c-1814-449b-ae6c-0cdc5fecdba2/user_impersonation"]

    auth = BearerAuth.get_auth(
        tenantID=tenantID,
        clientID=clientID,
        scopes=scope,
        username=username,
        token_location="api_token_cache.bin",
    )
    return auth.token  # type: ignore


def get_app_token(username: str = "") -> str:
    """Getter for token using app registration authentication.

    Args:
        username (str, optional): User name (email address) of user to get token for.

    Returns:
        str: Token from app registration
    """
    return get_app_bearer(username=username)


def get_object_from_json(text: str):
    if isinstance(text, list):
        obj = [json.loads(x, object_hook=lambda d: SimpleNamespace(**d)) for x in text]
    else:
        obj = json.loads(text, object_hook=lambda d: SimpleNamespace(**d))
    return obj


def get_api_url(use_dev: bool = False) -> str:
    """Getter for API URL. Will return the dev URL if use_dev is True, otherwise will return the production URL.
    Args:
        use_dev (bool, optional): If True, will return the dev URL. Defaults to False.
    Returns:
        str: API URL
    """
    if use_dev:
        return "https://spdapi-dev.radix.equinor.com"
    else:
        return "https://spdapi.radix.equinor.com"


def get_json(url: str, params: Optional[dict] = None, raise_for_status=False):
    token = get_token()
    header = {"Authorization": f"Bearer {token}"}
    response = requests.get(url, headers=header, params=params)
    if raise_for_status:
        response.raise_for_status()

    if response.status_code == 200:
        try:
            return response.json()
        except json.JSONDecodeError:
            logger.warning(
                f"Warning: {str(url)} returned successfully, but not with a valid json response"
            )
    else:
        logger.warning(
            f"Warning: {str(url)} returned status code {response.status_code}"
        )

    return response


def get_file(url: str, file_name: str, raise_for_status=False, stream=True) -> str:
    token = get_token()
    header = {"Authorization": f"Bearer {token}"}
    response = requests.get(url, headers=header, stream=stream)
    # try:
    if raise_for_status:
        response.raise_for_status()

    if file_name is not None and len(file_name) > 0:
        save_path = os.path.join(os.getcwd(), file_name)
        with open(save_path, "wb") as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)
        print(f"File downloaded successfully and saved to {save_path}")
        return save_path
    else:
        return response.text
    # except requests.exceptions.RequestException as e:
    #     print(f"Error downloading schema: {e}")
    # except PermissionError as e:
    #     print(f"Permission error: {e}")
    # except Exception as e:
    #     print(f"An unexpected error occurred: {e}")


def post_json(
    url: str, upload: Dict[str, List[Dict[str, str]]], raise_for_status=False
):
    header = {"Authorization": f"Bearer {get_token()}"}
    json_file = BytesIO(json.dumps(upload).encode("utf-8"))
    response = requests.post(
        url, headers=header, files={"file": ("upload_data.json", json_file)}
    )

    if raise_for_status:
        response.raise_for_status()

    if not (response.status_code == 200):
        logger.warning(
            f"Warning: {str(url)} returned status code {response.status_code}"
        )

    return response


def get_generic_model_mappings(data: dict) -> List[dict[str, str]]:
    """Get generic model mappings from the API. Function is typically called from the Model class functions get_mappings().

    Args:
        data (dict): The data to send in the request. A dictionary with keys like "Model_Owner", "Attribute_Type", "Model_Name", and "unique_object_identifier".

    Raises:
        ValueError: If the response is not valid JSON object

    Returns:
        list: A list of generic model mappings
    """
    url = get_api_url() + "/get-model"
    response = get_json(url, params=data)

    if isinstance(response, dict):
        if "data" in response.keys():
            if isinstance(response["data"], list):
                return response["data"]
            else:
                return [response["data"]]
        raise ValueError("Response is not a valid JSON object")
    else:
        print(f"{response}")
        return []


def post_generic_model_mapping(data: Union[dict[str, str], List[dict[str, str]]]):
    """
    Post generic model mapping to the API
    """

    if isinstance(data, dict):
        data = [data]

    for d in data:
        d["AttributeName"] = d["AttributeName"].lower().replace(" ", "_")

    upload = {"data": data}

    url = get_api_url() + "/upload-model"
    response = post_json(url, upload)
    return response


def post_timeseries_mapping(
    object_name: str,
    model_owner: str,
    model_name: str,
    attribute_name: str,
    time_series_tag_no: str,
    timeseries_source: str,
    mode: Optional[str] = "",
    unit_of_measure: Optional[str] = "",
    comment: Optional[str] = "",
):
    """
    Post a timeseries mapping to the API
    """
    timeseries_dict = make_timeseries_mapping_dict(
        object_name,
        model_owner,
        model_name,
        attribute_name,
        time_series_tag_no,
        timeseries_source,
        mode,
        unit_of_measure,
        comment,
    )

    return post_generic_model_mapping(timeseries_dict)


def make_timeseries_mapping_dict(
    object_name: str,
    model_owner: str,
    model_name: str,
    attribute_name: str,
    time_series_tag_no: str,
    timeseries_source: str,
    mode: Optional[str] = "",
    unit_of_measure: Optional[str] = "",
    comment: Optional[str] = "",
):
    timeseries_dict = {
        "unique_object_identifier": object_name,
        "model_owner": model_owner,
        "model_name": model_name,
        "mode": mode,
        "UnitOfMeasure": unit_of_measure,
        "TimeseriesSource": timeseries_source,
        "comment": comment,
        "AttributeName": attribute_name,
        "TimeSeriesTagNo": time_series_tag_no,
    }

    return timeseries_dict


def post_constant_mapping(
    object_name: str,
    model_owner: str,
    model_name: str,
    attribute_name: str,
    value: str,
    mode: Optional[str] = "",
    unit_of_measure: Optional[str] = "",
    comment: Optional[str] = "",
):
    """
    Post a constant mapping to the API
    """

    return post_generic_model_mapping(
        make_constant_mapping_dict(
            object_name,
            model_owner,
            model_name,
            attribute_name,
            value,
            mode,
            unit_of_measure,
            comment,
        )
    )


def make_constant_mapping_dict(
    object_name: str,
    model_owner: str,
    model_name: str,
    attribute_name: str,
    value: str,
    mode: Optional[str] = "",
    unit_of_measure: Optional[str] = "",
    comment: Optional[str] = "",
):
    constant_dict = {
        "unique_object_identifier": object_name,
        "model_owner": model_owner,
        "model_name": model_name,
        "mode": mode,
        "UnitOfMeasure": unit_of_measure,
        "comment": comment,
        "AttributeName": attribute_name,
        "ConstantValue": value,
    }

    return constant_dict


def get_mappings(
    model_owner: str = "",
    model_name: str = "",
    object_name: str = "",
    attribute_type: Optional[Literal["constant", "timeseries"]] = None,
) -> List[dict[str, str]]:
    """
    Get generic model mappings from the API as List of dicts
    """

    if attribute_type is None:
        const = get_mappings(
            model_owner=model_owner,
            model_name=model_name,
            object_name=object_name,
            attribute_type="constant",
        )

        ts = get_mappings(
            model_owner=model_owner,
            model_name=model_name,
            object_name=object_name,
            attribute_type="timeseries",
        )
        const.extend(ts)
        return const

    model_dict = {
        "Model_Owner": model_owner,
        "Attribute_Type": str(attribute_type),
        "Model_Name": model_name,
        "unique_object_identifier": object_name,
    }

    return get_generic_model_mappings(data=model_dict)
