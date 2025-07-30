import httpx
import os

from typing import Dict, List, Optional

from .schemas import CapabilityGroupModel, FunctionModel, UpdateCapabilityGroupModel


class CapabilityGroupException(Exception):
    pass


TIMEOUT = 20


def _get_base_endpoint_url() -> str:
    """
    Constructs the base endpoint URL using environment variables.

    Returns
    -------
    str
        The base endpoint URL.
    """
    base_url = os.environ['HALERIUM_BASE_URL']
    tenant = os.environ['HALERIUM_TENANT_KEY']
    workspace = os.environ['HALERIUM_PROJECT_ID']
    return f"{base_url}/api/tenants/{tenant}/projects/{workspace}/runners/{os.environ['HALERIUM_ID']}/token-access"


def _get_headers() -> dict:
    """
    Constructs the headers for HTTP requests.

    Returns
    -------
    dict
        The headers for HTTP requests.
    """
    return {"Content-Type": "application/json",
            "halerium-runner-token": os.environ["HALERIUM_TOKEN"]}


# Sync Methods
def _get_capability_groups() -> List[Dict]:
    endpoint = _get_base_endpoint_url() + "/manifests"
    response = httpx.get(endpoint, headers=_get_headers())
    response.raise_for_status()

    return response.json().get("data", [])


async def _get_capability_groups_async() -> List[Dict]:
    """
    Asynchronously retrieves a list of capability groups.

    Returns
    -------
    List[Dict]
        A list of capability groups.
    """
    endpoint = _get_base_endpoint_url() + "/manifests"
    async with httpx.AsyncClient() as client:
        response = await client.get(endpoint, headers=_get_headers())
        response.raise_for_status()
        return response.json().get("data", [])


def get_capability_groups() -> List[Dict]:
    """
    Retrieves the list of capability groups.

    Returns
    -------
    List[Dict]
        List of capability groups.
    """

    raw_data = _get_capability_groups()

    relevant_data = []
    for capa_group in raw_data:
        relevant_data.append({
            "name": capa_group["name"],
            "editable": not capa_group["global"],
            "functions": [
                {"name": f["function"]["name"],
                 "description": f["function"]["description"]}
                for f in capa_group["runnerFunctions"]
            ]
        })

    return relevant_data


async def get_capability_groups_async() -> List[Dict]:
    """
    Asynchronously retrieves the list of capability groups.

    Returns
    -------
    List[Dict]
        List of capability groups.
    """

    raw_data = await _get_capability_groups_async()

    relevant_data = []
    for capa_group in raw_data:
        relevant_data.append({
            "name": capa_group["name"],
            "editable": not capa_group["global"],
            "functions": [
                {"name": f["function"]["name"],
                 "description": f["function"]["description"]}
                for f in capa_group["runnerFunctions"]
            ]
        })

    return relevant_data


def get_capability_group(name: str) -> Dict:
    """
    Retrieves details of a specific capability group by name.

    Parameters
    ----------
    name : str
        The name of the capability group.

    Returns
    -------
    Dict
        The details of the capability group.
    """
    capability_group_id = _get_capability_id_by_name(name)
    endpoint = _get_base_endpoint_url() + f"/manifests/{capability_group_id}"

    response = httpx.get(endpoint, headers=_get_headers())
    response.raise_for_status()
    capability_group_data = response.json().get("data", {})

    source_path = os.path.join("/home/jovyan", ".functions", capability_group_data.get("name", ""), "source.py")
    if os.path.exists(source_path):
        with open(source_path, "r") as f:
            source_code = f.read()
    else:
        source_code = None

    capability_group_data["sourceCode"] = source_code
    # Validate the capability group against the CapabilityGroupModel
    capability_group = CapabilityGroupModel.validate(capability_group_data)
    return capability_group.dict()


async def get_capability_group_async(name: str) -> Dict:
    """
    Asynchronously retrieves details of a specific capability group by name.

    Parameters
    ----------
    name : str
        The name of the capability group.

    Returns
    -------
    Dict
        The details of the capability group.
    """
    capability_group_id = await _get_capability_id_by_name_async(name)
    endpoint = _get_base_endpoint_url() + f"/manifests/{capability_group_id}"

    async with httpx.AsyncClient() as client:
        response = await client.get(endpoint, headers=_get_headers())
        response.raise_for_status()
        capability_group_data = response.json().get("data", {})

    source_path = os.path.join("/home/jovyan", ".functions", capability_group_data.get("name", ""), "source.py")
    if os.path.exists(source_path):
        with open(source_path, "r") as f:
            source_code = f.read()
    else:
        source_code = None

    capability_group_data["sourceCode"] = source_code
    # Validate the capability group against the CapabilityGroupModel
    capability_group = CapabilityGroupModel.validate(capability_group_data)
    return capability_group.dict()


def _get_capability_id_by_name(name: str) -> Dict:
    """
    Retrieves the ID of a capability group by name.

    Parameters
    ----------
    name : str
        The name of the capability group.

    Returns
    -------
    Dict
        The ID of the capability group.
    """
    capability_groups = _get_capability_groups()

    for capability_group in capability_groups:
        if capability_group.get("name") == name:
            return capability_group.get("id")
    raise CapabilityGroupException(f"Capability group {name} not found.")


async def _get_capability_id_by_name_async(name: str) -> Dict:
    """
    Asynchronously retrieves the ID of a capability group by name.

    Parameters
    ----------
    name : str
        The name of the capability group.

    Returns
    -------
    Dict
        The ID of the capability group.
    """
    capability_groups = await _get_capability_groups_async()

    for capability_group in capability_groups:
        if capability_group.get("name") == name:
            return capability_group.get("id")
    raise CapabilityGroupException(f"Capability group {name} not found.")


def delete_capability_group(name: str) -> Dict:
    """
    Deletes a capability group by name.

    Parameters
    ----------
    name : str
        The name of the capability group.

    Returns
    -------
    Dict
        The result of the deletion operation.
    """
    capability_group_id = _get_capability_id_by_name(name)

    endpoint = _get_base_endpoint_url() + f"/manifests/{capability_group_id}"

    response = httpx.delete(endpoint, headers=_get_headers())
    response.raise_for_status()
    return response.json().get("data", {})


async def delete_capability_group_async(name: str) -> Dict:
    """
    Asynchronously deletes a capability group by name.

    Parameters
    ----------
    name : str
        The name of the capability group.

    Returns
    -------
    Dict
        The result of the deletion operation.
    """
    capability_group_id = await _get_capability_id_by_name_async(name)

    endpoint = _get_base_endpoint_url() + f"/manifests/{capability_group_id}"

    async with httpx.AsyncClient() as client:
        response = await client.delete(endpoint, headers=_get_headers())
        response.raise_for_status()
        return response.json().get("data", {})


def create_capability_group(name: str,
                            runner_type: str = None,
                            shared_runner: bool = None,
                            setup_commands: List[str] = None,
                            source_code: str = None,
                            functions: Optional[List[Dict]] = None) -> Dict:
    """
    Creates a new capability group.

    Parameters
    ----------
    name : str
        The name of the capability group.
    runner_type : Optional[str], optional
        The type of runner, by default None.
    shared_runner : Optional[bool], optional
        Whether the runner is shared, by default None.
    setup_commands : Optional[List[str]], optional
        The setup commands, by default None.
    source_code : Optional[str], optional
        The source code, by default None.
    functions : Optional[List[Dict]], optional
        The functions, by default None.

    Returns
    -------
    Dict
        The result of the creation operation.
    """
    if not setup_commands:
        setup_commands = []

    # Validate the name
    if not name:
        raise ValueError("Name is required.")
    if "\n" in name:
        raise ValueError("Name cannot contain line breaks.")

    runner_type = runner_type if runner_type else "nano"
    shared_runner = bool(shared_runner)
    setup_commands = [str(c) for c in setup_commands] if setup_commands else []
    source_code = str(source_code) if source_code else ""
    functions = [FunctionModel.validate({**func, "group": name}).dict() for func in functions] if functions else []

    payload = {
        "name": name,
        "displayName": name,
        "runnerType": runner_type,
        "sharedRunner": shared_runner,
        'setupCommand': {'setupCommands': setup_commands},
        "sourceCode": source_code,
        "functions": functions
    }

    # Validate payload
    payload = CapabilityGroupModel.validate(payload).dict()

    endpoint = _get_base_endpoint_url() + "/manifests"

    # Make the POST request
    response = httpx.post(
        endpoint,
        json=payload,
        headers=_get_headers()
    )
    try:
        response.raise_for_status()
        return response.json().get("data", {})
    except httpx.HTTPStatusError:
        return response.json()


async def create_capability_group_async(name: str,
                                        runner_type: str = None,
                                        shared_runner: bool = None,
                                        setup_commands: List[str] = None,
                                        source_code: str = None,
                                        functions: Optional[List[Dict]] = None) -> Dict:
    """
    Asynchronously creates a new capability group.

    Parameters
    ----------
    name : str
        The name of the capability group.
    runner_type : Optional[str], optional
        The type of runner, by default None.
    shared_runner : Optional[bool], optional
        Whether the runner is shared, by default None.
    setup_commands : Optional[List[str]], optional
        The setup commands, by default None.
    source_code : Optional[str], optional
        The source code, by default None.
    functions : Optional[List[Dict]], optional
        The functions, by default None.

    Returns
    -------
    Dict
        The result of the creation operation.
    """
    if not setup_commands:
        setup_commands = []

    # Validate the name
    if not name:
        raise ValueError("Name is required.")
    if "\n" in name:
        raise ValueError("Name cannot contain line breaks.")

    runner_type = runner_type if runner_type else "nano"
    shared_runner = bool(shared_runner)
    setup_commands = [str(c) for c in setup_commands] if setup_commands else []
    source_code = str(source_code) if source_code else ""
    functions = [FunctionModel.validate({**func, "group": name}).dict() for func in functions] if functions else []

    payload = {
        "name": name,
        "displayName": name,
        "runnerType": runner_type,
        "sharedRunner": shared_runner,
        'setupCommand': {'setupCommands': setup_commands},
        "sourceCode": source_code,
        "functions": functions
    }

    # Validate payload
    payload = CapabilityGroupModel.validate(payload).dict()

    endpoint = _get_base_endpoint_url() + "/manifests"

    async with httpx.AsyncClient() as client:
        response = await client.post(
            endpoint,
            json=payload,
            headers=_get_headers()
        )
        try:
            response.raise_for_status()
            return response.json().get("data", {})
        except httpx.HTTPStatusError:
            return response.json()


def update_capability_group(name: str,
                            new_name: Optional[str] = None,
                            runner_type: Optional[str] = None,
                            shared_runner: Optional[bool] = None,
                            setup_commands: Optional[List[str]] = None,
                            source_code: Optional[str] = None,
                            functions: Optional[List[Dict]] = None) -> Dict:
    """
    Updates an existing capability group.

    Parameters
    ----------
    name : str
        The current name of the capability group.
    new_name : Optional[str], optional
        The new name of capability group to update to, by default None.
    runner_type : Optional[str], optional
        The type of runner, by default None.
    shared_runner : Optional[bool], optional
        Whether the runner is shared, by default None.
    setup_commands : Optional[List[str]], optional
        The setup commands, by default None.
    source_code : Optional[str], optional
        The source code, by default None.
    functions : Optional[List[Dict]], optional
        The functions, by default None.

    Returns
    -------
    Dict
        The result of the update operation.
    """
    capability_id = _get_capability_id_by_name(name)

    endpoint = _get_base_endpoint_url() + f"/manifests/{capability_id}"

    if functions is not None:
        functions = [FunctionModel.validate({**func, "group": name}).dict() for func in functions]

    # Validate payload and exclude None values
    capability_group = UpdateCapabilityGroupModel(
        name=new_name, displayName=new_name,
        runnerType=runner_type, sharedRunner=shared_runner,
        setupCommands=setup_commands,
        sourceCode=source_code, functions=functions
    )
    payload_dict = capability_group.dict(exclude_none=True)

    # Update capability group
    response = httpx.put(endpoint, json=payload_dict,
                         headers=_get_headers())
    try:
        response.raise_for_status()
        return response.json().get("data", {})
    except httpx.HTTPStatusError:
        return response.json()


async def update_capability_group_async(name: str,
                                        new_name: Optional[str] = None,
                                        runner_type: Optional[str] = None,
                                        shared_runner: Optional[bool] = None,
                                        setup_commands: Optional[List[str]] = None,
                                        source_code: Optional[str] = None,
                                        functions: Optional[List[Dict]] = None) -> Dict:
    """
    Asynchronously updates an existing capability group.

    Parameters
    ----------
    name : str
        The current name of the capability group.
    new_name : Optional[str], optional
        The new name of capability group to update to, by default None.
    runner_type : Optional[str], optional
        The type of runner, by default None.
    shared_runner : Optional[bool], optional
        Whether the runner is shared, by default None.
    setup_commands : Optional[List[str]], optional
        The setup commands, by default None.
    source_code : Optional[str], optional
        The source code, by default None.
    functions : Optional[List[Dict]], optional
        The functions, by default None.

    Returns
    -------
    Dict
        The result of the update operation.
    """
    capability_id = await _get_capability_id_by_name_async(name)

    endpoint = _get_base_endpoint_url() + f"/manifests/{capability_id}"

    if functions is not None:
        functions = [FunctionModel.validate({**func, "group": name}).dict() for func in functions]

    # Validate payload and exclude None values
    capability_group = UpdateCapabilityGroupModel(
        name=new_name, displayName=new_name,
        runnerType=runner_type, sharedRunner=shared_runner,
        setupCommands=setup_commands,
        sourceCode=source_code, functions=functions
    )
    payload_dict = capability_group.dict(exclude_none=True)

    async with httpx.AsyncClient() as client:
        response = await client.put(endpoint, json=payload_dict,
                                    headers=_get_headers())
        try:
            response.raise_for_status()
            return response.json().get("data", {})
        except httpx.HTTPStatusError:
            return response.json()


# TODO: revisit on how this should be done
# def add_function_to_capability_group(name: str, function: str,
#                                      source_file: Union[str, Path],
#                                      config_parameters: Dict[str, str] = None,
#                                      pretty_name: str = None,
#                                      function_schema: Optional[dict] = None) -> Dict:
#     """
#     Adds a function to an existing capability group.
#
#     Parameters
#     ----------
#     name (str): the name of the capability group.
#     function (str): the object name of the function.
#     source_file (str or Path): the path of the source .py file in which the function is located.
#     function_schema (Optional[dict]): the schema of the function. If not provided, it will be generated automatically.
#     config_parameters (dict): possible fixed parameters to the function on each call. Must be JSON serializable.
#     pretty_name (str): display name for the function. Will be used as a display name in the bot setup card and within the function call.
#
#     Returns
#     -------
#     dict: the result (status, error, ...) of the update attempt.
#     """
#
#     # Get the source code of the new function
#     if not os.path.exists(source_file):
#         return {"error": f"File path {source_file} does not exist."}
#     with open(source_file, "r") as f:
#         source_code = f.read()
#
#     # Prepare the function registration details
#     function_details = prepare_register(
#         file_path=source_file,
#         function=function,
#         function_schema=function_schema,
#         config_parameters=config_parameters,
#         group=name,
#         pretty_name=pretty_name,
#     )
#
#     # Get the existing capability group details
#     capability_group = get_capability_group(name)
#
#     # get existing source code
#     existing_source_path = os.path.join("/home/jovyan", ".functions",
#                                         capability_group.get("name", ""), "source.py")
#     if os.path.exists(existing_source_path):
#         with open(existing_source_path, "r") as f:
#             existing_source_code = f.read()
#     updated_source = existing_source_code + "\n" + source_code
#
#     # get existing functions
#     existing_functions = capability_group["functions"]
#
#     new_function = FunctionModel(
#         function=function,
#         pretty_name=pretty_name,
#         group=name,
#         description=function_details["function_spec"]["description"],
#         config_parameters=config_parameters,
#         parameters=ParametersModel(
#             properties=function_details["function_spec"]["parameters"]["properties"],
#             required=function_details["function_spec"]["parameters"]["required"]
#         )
#     )
#     # Append the new function to the list
#     functions = existing_functions + [new_function.dict()]
#
#     # Update the capability group with the new function
#     update_result = update_capability_group(
#         name=name,
#         source_code=updated_source,
#         functions=functions
#     )
#
#     return update_result


# TODO: revisit how this should be done
# async def add_function_to_capability_group_async(name: str, function: str, config_parameters: dict, pretty_name: str,
#                                                  description: str, file_path: Optional[Union[str, Path]] = None,
#                                                  file_source: Optional[str] = None, function_name: Optional[str] = None,
#                                                  function_schema: Optional[dict] = None) -> Dict:
#     """
#     Adds a function to an existing capability group.
#
#     Parameters
#     ----------
#     name (str): the name of the capability group.
#     function (str): the object name of the function.
#     file_path (Optional[str or Path]): the path of the source .py file in which the function is located.
#     file_source (Optional[str]): the source code of the function.
#     function_name (Optional[str]): the name under which to register the function. If not set it will be set to the object name `function`.
#     function_schema (Optional[dict]): the schema of the function. If not provided, it will be generated automatically.
#     config_parameters (dict): possible fixed parameters to the function on each call. Must be JSON serializable.
#     pretty_name (str): display name for the function. Will be used as a display name in the bot setup card and within the function call.
#     description (str): description for the function.
#
#     Returns
#     -------
#     dict: the result (status, error, ...) of the update attempt.
#     """
#     if not file_path and not file_source:
#         return {"error": "Either file_path or file_source must be provided."}
#
#     # Prepare the function registration details
#     function_details = prepare_register(
#         file_path=file_path,
#         file_source=file_source,
#         function=function,
#         function_name=function_name,
#         function_schema=function_schema,
#         config_parameters=config_parameters,
#         group=name,
#         pretty_name=pretty_name,
#     )
#
#     # Get the existing capability group details
#     capability_group = await get_capability_group_async(name)
#     if "error" in capability_group:
#         return capability_group
#
#     # Get the source code of the new function
#     if not file_source:
#         if not os.path.exists(file_path):
#             return {"error": f"File path {file_path} does not exist."}
#         with open(file_path, 'r') as file:
#             file_source = file.read()
#
#     # Get the source code of the existing capability group
#     capability_id_response = await _get_capability_id_by_name_async(name)
#     if "error" in capability_id_response:
#         return capability_id_response
#
#     capabilityGroupId = capability_id_response.get("capabilityGroupId")
#     endpoint = _get_base_endpoint_url() + f"/manifests/{capabilityGroupId}"
#
#     try:
#         async with httpx.AsyncClient() as client:
#             response = await client.get(endpoint, headers={"Content-Type": "application/json",
#                                                            "halerium-runner-token": os.environ["HALERIUM_TOKEN"]})
#             response.raise_for_status()
#             capability_group_data = response.json().get("data", {})
#
#             source_path = os.path.join("/home/jovyan", ".functions", capability_group_data.get("name", ""), "source.py")
#             if os.path.exists(source_path):
#                 with open(source_path, "r") as f:
#                     source_code = f.read()
#
#             # source code of the existing capability group
#             capability_group_data["sourceCode"] = source_code
#
#     except httpx.RequestError as e:
#         return {"error": str(e)}
#
#     # Append the new function's source code and declaration to the capability group
#     capability_group_data["sourceCode"] += file_source
#
#     new_function = FunctionModel(
#         function=function,
#         pretty_name=pretty_name,
#         group=name,
#         description=description,
#         config_parameters=config_parameters,
#         parameters=ParametersModel(
#             properties=function_details["function_spec"]["parameters"]["properties"],
#             required=function_details["function_spec"]["parameters"]["required"]
#         )
#     )
#
#     # Retrieve the current list of functions
#     current_functions = capability_group['functions']
#
#     # Append the new function to the list
#     current_functions.append("\n" + new_function)
#
#     # Update the capability group with the new function
#     update_result = await update_capability_group_async(
#         name=name,
#         source_code=capability_group_data["sourceCode"],
#         functions=current_functions
#     )
#
#     return update_result
