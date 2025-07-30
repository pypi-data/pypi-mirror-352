import os.path

from halerium_utilities.collab import CollabBoard
from halerium_utilities.hal_es.hal_e_session import HalESession


class BoardPathSession(HalESession):

    def __init__(self, board_path: str):

        self.board = CollabBoard(board_path)
        workspace_path = os.path.relpath(
            os.path.abspath(board_path), "/home/jovyan"
        )
        workspace_path = (workspace_path
                          if workspace_path.startswith("/")
                          else "/" + workspace_path)

        self.session_info = {"sessionContent": {"path": workspace_path}}

    def __repr__(self):

        return f"BoardPathSession(board_path='{self.board.file_path}')"
