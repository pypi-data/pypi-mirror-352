import httpx
import os
import shutil

from copy import deepcopy
from pathlib import Path
from urllib.parse import urljoin

from halerium_utilities.board import BoardNavigator
from halerium_utilities.collab import CollabBoard
from halerium_utilities.hal_es.hal_e import HalE
from halerium_utilities.logging.exceptions import PathLinkError, ElementTypeError
from halerium_utilities.prompt import apply_board_action
from halerium_utilities.stores.api import get_file_as_text


class HalESession:
    """
    Class for Hal-E Sessions.
    """
    def __init__(self, hale: HalE):
        """
        Initializes a new HalESession instance.

        This constructor creates a session for a specific HalE board and initializes
        a CollabBoard instance representing the board.

        Parameters
        ----------
        hale : HalE
            The HalE instance that this session represents
        """
        self.hale = hale

        tenant = os.getenv("HALERIUM_TENANT_KEY", "")
        workspace = os.getenv("HALERIUM_PROJECT_ID", "")
        runner_id = os.getenv("HALERIUM_ID", "")
        base_url = os.getenv("HALERIUM_BASE_URL", "")
        url = urljoin(
            base_url,
            "/api"
            f"/tenants/{tenant}"
            f"/projects/{workspace}"
            f"/runners/{runner_id}"
            f"/token-access/hal-es/session/{self.hale.name}",
        )

        with httpx.Client() as client:
            response = client.post(
                url,
                json={},
                headers={"Content-Type": "application/json",
                         "halerium-runner-token": os.environ["HALERIUM_TOKEN"]}
            )
            response.raise_for_status()
            self.session_info = response.json()["data"]

        session_path = self.session_info["sessionContent"]["path"]
        full_session_path = Path.home() / session_path.lstrip("/")
        self.board = CollabBoard(path=full_session_path)

        self.session_url = urljoin(
            self.hale.init_url, self.session_info['halESessionId'])

    def _resolve_element(self, element):
        if not hasattr(element.type_specific, "linkedNodeId"):
            return element  # immediate return for unlinkable elements

        resolved_element = deepcopy(element)
        if card_id := resolved_element.type_specific.linkedNodeId:
            new_type_specific = self.board.get_card_by_id(card_id).type_specific.dict()
            new_type_specific.update({"linkedNodeId": card_id})
            resolved_element.type_specific = type(resolved_element.type_specific).validate(
                new_type_specific)
        return resolved_element

    def get_elements(self, resolve=True):
        """
        Fetch the Hal-E path (elements)

        Parameters
        ----------
        resolve: bool, optional
            Whether to resolve the element wrt a linked card.
            The default is True.
        
        Returns
        -------
        list
            A list of Hal-E path elements
        """
        self.board.pull()
        if resolve:
            path_elements = [
                self._resolve_element(element) for element in self.board.path_elements]
        else:
            path_elements = self.board.path_elements
        
        return path_elements

    def get_element_by_id(self, element_id: str, resolve=True):
        """
        Fetch a specified Hal-E path element by id

        Parameters
        ----------
        element_id : str
            The ID of the path element to retrieve.
        resolve: bool, optional
            Whether to resolve the element wrt a linked card.
            The default is True.

        Returns
        -------
        PathElement
            A specific Hal-E path element
        """
        self.board.pull()
        path_element = self.board.get_path_element_by_id(element_id)

        if resolve:
            return self._resolve_element(path_element)
        else:
            return path_element

    def insert_text(self, element_id: str, text: str, field: str):
        """
        Inserts text into any path element.

        Parameters
        ----------
        element_id : str
            The ID of the path element to update.
        text : str
            The text to insert into the path element.
        field : str
            Specifies the field within the path element where the value should be inserted. Must be one of: 'title', 'message', 'prompt_input', or 'prompt_output'.
        Returns
        -------
        Dict
            The updated path element.
        """
        path_element = self.get_element_by_id(element_id, resolve=False)
        element_type = path_element.type

        if element_type not in {"note", "bot"}:
            raise ElementTypeError(f"Cannot insert text into a '{path_element.type}' element. Must be 'note' or 'bot'.")

        if element_type == "note" and field not in {"title", "message"}:
            raise ElementTypeError(f"Field in a 'note' element must be of type 'title' or 'message'.")

        if element_type == "bot" and field not in {"prompt_input", "prompt_output"}:
            raise ElementTypeError(f"Field in a 'bot' element must be of type 'prompt_input' or 'prompt_output'.")

        card_id = path_element.type_specific.linkedNodeId
        if card_id:
            card_update = {
                "id": card_id,
                "type_specific": {field: text}
            }
            self.board.update_card(card_update)
        else:
            element_update = {
                "id": path_element.id,
                "type_specific": {field: text}
            }
            self.board.update_path_element(element_update)

        self.board.push()

    def send_prompt_with_input(self, element_id: str, prompt_input: str):
        """
        Sends user input and triggers the prompt on a 'bot' path element.

        Parameters
        ----------
        element_id : str
            The ID of the bot path element.
        prompt_input : str
            The user's input.

        Returns
        -------
        str
            The bot's answer.
        """
        self.insert_text(element_id=element_id, text=prompt_input, field="prompt_input")
        return self.send_prompt(element_id)

    def send_prompt(self, element_id):
        """
        Triggers the prompt on a 'bot' path element.

        Parameters
        ----------
        element_id : str
            The ID of the bot path element.

        Returns
        -------
        str
            The bot's answer.
        """
        path_element = self.get_element_by_id(element_id, resolve=False)

        if path_element.type != "bot":
            raise ElementTypeError(f"Cannot send prompt to '{path_element.type}' element. Must be 'bot'.")

        card_id = path_element.type_specific.linkedNodeId
        if not card_id:
            raise PathLinkError("Bot element must be linked to a card to be evaluated.")

        self._execute_action(card_id)
        self.board.push()
        return self.board.get_card_by_id(card_id).type_specific.prompt_output

    def append_bot_element(self, element_id):
        """
        Appends a bot element to an existing bot element to continue a chat.

        Parameters
        ----------
        element_id : str
            The element_id of the bot element to append to.

        Returns
        -------
        new_element_id : str
            The id of the newly created bot element.
        """
        path_element = self.board.get_path_element_by_id(element_id)
        if path_element.type != "bot":
            raise ElementTypeError(f"Bot element can only be appended to element of type 'bot'. "
                                   f"Got element of type '{path_element.type}' instead.")
        card_id = path_element.type_specific.linkedNodeId
        if not card_id:
            raise PathLinkError("Bot element must be linked to a card to append to it.")

        path_element_index = self.board.path_elements.index(path_element)

        card = self.board.get_card_by_id(card_id)

        new_position = card.position.dict()
        new_position["x"] += card.size.width + 80

        new_card = self.board.create_card(
            type="bot",
            position=new_position
        )
        self.board.add_card(new_card)

        new_connection = self.board.create_connection(
            type="prompt_line",
            connections={
                "source": {
                    "connector": "prompt-output",
                    "id": card_id
                },
                "target": {
                    "connector": "prompt-input",
                    "id": new_card.id
                }
            }
        )
        self.board.add_connection(new_connection)

        new_element = self.board.create_path_element(
            type="bot",
            type_specific={
                "linkedNodeId": new_card.id
            }
        )
        self.board.add_path_element(new_element, index=path_element_index+1)
        self.board.push()
        return new_element.id

    def _execute_action(self, card_id: str):
        """
        Executes a single action on a given card.

        Parameters
        ----------
        card_id : str
            The ID of the card to apply the action to.
        """
        self.board = apply_board_action(
            board=self.board,
            card_id=card_id,
            action="run",
            board_path="/"+self.board.file_path.resolve().relative_to("/home/jovyan").as_posix()
        )

    def execute_actions(self, element_id: str):
        """
        Executes the action button specified by the element_id

        Parameters
        ----------
        element_id : str
            The ID of the action button element.
        """
        self.board.pull()
        navigator = BoardNavigator(board=self.board)
        bot_card_ids = navigator.get_action_element_executions(id=element_id)

        for card_id in bot_card_ids:
            self._execute_action(card_id)

        self.board.push()

    def _get_unique_filename(self, directory, filename):
        base, ext = os.path.splitext(filename)
        counter = 1
        new_filename = filename
        while os.path.exists(os.path.join(directory, new_filename)):
            new_filename = f"{base}-{counter}{ext}"
            counter += 1
        return new_filename

    def upload_file(self, element_id: str, file_path: str):
        """
        Utilizes an upload button.
        The upload is emulated by copying the specified file to the target
        location of the upload button.

        Parameters
        ----------
        element_id : str
            The ID of the upload element.
        file_path : str
            The path of the file that is to be uploaded.
        """
        path_element = self.get_element_by_id(element_id, resolve=False)

        if path_element.type != "upload":
            raise ElementTypeError(f"Cannot upload a file to '{path_element.type}' element. Must be 'upload'.")

        board_path = self.session_info["sessionContent"]["path"]
        folder_name = Path(board_path).parent.name
        
        target_folder = os.path.dirname(board_path)
        target_folder_with_home = Path.home() / target_folder.lstrip('/')

        filename = os.path.basename(file_path)
        unique_filename = self._get_unique_filename(target_folder_with_home, filename)

        relative_path = f"../{folder_name}/{unique_filename}"

        target_path = os.path.join(target_folder_with_home, unique_filename)
        target_path_without_home = os.path.join(target_folder, unique_filename)

        shutil.copy(file_path, target_path)

        if path_element.type_specific.filePathTargets:
            for target in path_element.type_specific.filePathTargets:
                card_update = {
                    "id": target.targetId,
                    "type_specific": {"message": relative_path}
                }

                existing_message = self.board.get_card_by_id(target.targetId).type_specific.message
                updated_message = existing_message + "\n" + relative_path if existing_message else relative_path
                card_update["type_specific"]["message"] = updated_message

                self.board.update_card(card_update)

        if path_element.type_specific.fileContentTargets:
            for target in path_element.type_specific.fileContentTargets:
                chunker_args = path_element.type_specific.chunkingArguments
                file_content = get_file_as_text(target_path_without_home, chunker_args)
                card_update = {
                    "id": target.targetId,
                    "type_specific": {"message": file_content['item']}
                }

                existing_message = self.board.get_card_by_id(target.targetId).type_specific.message
                updated_message = (existing_message + "\n" + file_content['item']
                                   if existing_message else file_content['item'])
                card_update["type_specific"]["message"] = updated_message

                self.board.update_card(card_update)

        self.board.push()

    def __repr__(self):
        hale_name = self.hale.name
        session_path = self.session_info["sessionContent"]["path"]
        created_at = self.session_info["sessionContent"].get("created_at")

        return (f"HalESession(hale=HalE(name='{hale_name}'), session_url={self.session_url}, "
                f"session_path={session_path}, created_at='{created_at}')")
