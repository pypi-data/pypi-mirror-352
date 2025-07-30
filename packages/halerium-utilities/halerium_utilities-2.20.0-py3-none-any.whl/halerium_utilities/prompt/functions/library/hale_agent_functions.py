from halerium_utilities.hal_es import HalE, get_workspace_hales
from halerium_utilities.collab import CollabBoard
from pathlib import Path

def find_hales_with_agent():
    data = get_workspace_hales()
    matching_hales = [
        hale.name for hale in data
        if 'agent' in hale.name.lower()
    ]
    return matching_hales

def _simplify_note(note):
        return {
            "title": getattr(note.type_specific, "title", ""),
            "message": getattr(note.type_specific, "message", "")
        }

def get_agent_specification(agent_name):
    new_hale = HalE.from_name(agent_name)
    board_path = new_hale.template_board
    full_session_path = Path.home() / board_path.lstrip("/")
    board = CollabBoard(path=full_session_path)
    path_elements = board.path_elements

    action_index = next(
        (i for i, e in enumerate(path_elements) if e.type == 'action-chain'),
        None
    )
    if action_index is None:
        raise ValueError("No action-chain element found in the path.")

    action_element = path_elements[action_index]
    action_title = getattr(action_element.type_specific, "title", "")

    notes_before = [
        _simplify_note(e) for i, e in enumerate(path_elements)
        if e.type == 'note' and i < action_index
    ]
    notes_after = [
        _simplify_note(e) for i, e in enumerate(path_elements)
        if e.type == 'note' and i > action_index
    ]

    return {
        "agent_name": agent_name,
        "action": action_title,
        "input": notes_before,
        "output": notes_after
    }

def execute_agent(agent_name, input_elements):
    new_hale = HalE.from_name(agent_name)
    hale_instance = new_hale.get_instance()
    path_elements = hale_instance.get_elements()

    for input_note in input_elements:
        if isinstance(input_note, dict):
            title = input_note.get("title", "")
            message = input_note.get("message", "")
        elif hasattr(input_note, "type") and input_note.type == 'note':
            title = getattr(input_note.type_specific, "title", "")
            message = getattr(input_note.type_specific, "message", "")
        else:
            continue

        matching_note = next(
            (e for e in path_elements if e.type == 'note' and hasattr(e.type_specific, 'title') and e.type_specific.title == title),
            None
        )
        if not matching_note:
            raise ValueError(f"No note element found with title '{title}'.")
        
        hale_instance.insert_text(element_id=matching_note.id, text=message, field="message")

    action_chain_element = next((e for e in path_elements if e.type == 'action-chain'), None)
    if not action_chain_element:
        raise ValueError("No action-chain element found.")
    
    action_index = path_elements.index(action_chain_element)
    hale_instance.execute_actions(element_id=action_chain_element.id)
    updated_elements = hale_instance.get_elements()

    notes_after_action = [
        simplified for i, e in enumerate(updated_elements)
        if i > action_index and (simplified := _simplify_note(e)) is not None
    ]

    return {
        "output": notes_after_action
    }
