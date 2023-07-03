from pydantic import BaseModel

class NodeInfo(BaseModel):
    sender: str = ""
    new_node_address: str = ""

class SetMessage:
    def __init__(self, content: str, sender: str, timestamp: float):
        self.content = content
        self.sender = sender
        self.timestamp = timestamp

class ApiSetMessage(BaseModel):
    content: str
    sender: str
    timestamp: float

class ApiSimpleMessage(BaseModel):
    message: str