import json

from typing import Dict, List, Union, Optional
from traceback import format_exception_only


from halerium_utilities.prompt.capabilities import (
    get_capability_groups_async,
    get_capability_group_async,
    delete_capability_group_async,
    create_capability_group_async,
    update_capability_group_async
)


# Async wrapper functions

# TODO: create docstrings and pydantic.v1 based descriptions of the arguments
async def get_all_capability_groups() -> List[Dict]:
    try:
        return await get_capability_groups_async()
    except Exception as exc:
        return "".join(format_exception_only(exc))


async def get_capability_group(name: str) -> Dict:
    try:
        return await get_capability_group_async(name)
    except Exception as exc:
        return "".join(format_exception_only(exc))


async def delete_capability_group(name: str) -> Dict:
    try:
        return await delete_capability_group_async(name)
    except Exception as exc:
        return "".join(format_exception_only(exc))


async def create_capability_group(name: str,
                                  runner_type: Optional[str] = None,
                                  shared_runner: Optional[bool] = None,
                                  setup_commands: Optional[str] = None,
                                  source_code: Optional[str] = None,
                                  functions: Optional[str] = None) -> Dict:
    if setup_commands is not None:
        setup_commands = json.loads(setup_commands)
    if functions is not None:
        functions = json.loads(functions)

    try:
        return await create_capability_group_async(
            name=name,
            runner_type=runner_type,
            shared_runner=shared_runner,
            setup_commands=setup_commands,
            source_code=source_code,
            functions=functions)
    except Exception as exc:
        return "".join(format_exception_only(exc))


async def update_capability_group(name: str,
                                  new_name: Optional[str] = None,
                                  runner_type: Optional[str] = None,
                                  shared_runner: Optional[bool] = None,
                                  setup_commands: Optional[str] = None,
                                  source_code: Optional[str] = None,
                                  functions: Optional[str] = None) -> Dict:
    if setup_commands is not None:
        setup_commands = json.loads(setup_commands)
    if functions is not None:
        functions = json.loads(functions)

    try:
        return await update_capability_group_async(
            name=name, new_name=new_name,
            runner_type=runner_type,
            shared_runner=shared_runner,
            setup_commands=setup_commands,
            source_code=source_code,
            functions=functions)
    except Exception as exc:
        return "".join(format_exception_only(exc))
