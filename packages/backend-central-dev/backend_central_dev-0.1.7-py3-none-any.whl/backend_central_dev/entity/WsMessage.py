from dataclasses import asdict, dataclass
from enum import Enum, unique
import json

import websockets


@unique
class WsMessageType(str, Enum):
    TASK_STATUS_UPDATE: str = 'TASK_STATUS_UPDATE'
    TASK_EXE_RESULT_UPDATE: str = 'TASK_EXE_RESULT_UPDATE'
    PIPELINE_EXE_RESULT_UPDATE: str = 'PIPELINE_EXE_RESULT_UPDATE'


@dataclass(kw_only=True)
class WsMessage():

    message_type: WsMessageType
    payload: dict

    def __str__(self):
        return json.dumps(asdict(self))


async def send_and_remove_closed(
        ws_map: dict[websockets.asyncio.server.ServerConnection],
        message: WsMessage):
    removed_keys = []
    for key, ws in ws_map.items():
        try:
            await ws.send(str(message))
        except websockets.ConnectionClosedOK as e:
            print(f"Connection {key} ConnectionClosedOK.")
            removed_keys.append(key)
        except websockets.ConnectionClosedError as e:
            print(f"Connection {key} ConnectionClosedError.")
            removed_keys.append(key)

    for k in removed_keys:
        ws_map.pop(k)
