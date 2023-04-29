from fastapi import FastAPI

app = FastAPI()

local_nodes = set()

@app.get("/")
def root():
    return {"message": "Tarea 1 de sistemas distribuidos"}

@app.get("/nodes")
def read_root():
    return {"nodes": [node for node in local_nodes]}

@app.post("/nodes")
def add_node(node: str):
    local_nodes.add(node)
    return {"node": node}
