from pydantic import BaseModel

class NodeInfo(BaseModel):
    sender: str = ""
    new_node_address: str = ""

class chatMessage:
    def __init__(self, content: str, sender: str, timestamp: float):
        self.content = content
        self.sender = sender
        self.timestamp = timestamp

class ApiMessage(BaseModel):
    message: str