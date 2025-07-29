from .desktop import (
    open_file,
    cmd,
    run_program,
    kill_process,
    fullscreen,
    switch_to_next_window,
    switch_to_last_window,
    reload_window,
)
from .keyboard import (
    click,
    move,
    drag,
    press,
    hold,
    write,
    get_position,
)
from .web import (
    open_url,
    download,
)
from .pocketbase import (
    get_execution,
    update_execution,
    get_offline_computer,
    get_computer,
    update_computer,
)
from .json_storage import JSONFile

__all__ = [
    "open_file",
    "cmd",
    "run_program",
    "kill_process",
    "fullscreen",
    "switch_to_next_window",
    "switch_to_last_window",
    "reload_window",
    "click",
    "move",
    "drag",
    "press",
    "hold",
    "write",
    "get_position",
    "open_url",
    "download",
    "get_execution",
    "update_execution",
    "get_offline_computer",
    "get_computer",
    "update_computer",
    "JSONFile",
]
