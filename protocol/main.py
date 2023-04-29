import os
import requests
from fastapi import FastAPI
from pydantic import BaseModel
from contextlib import asynccontextmanager


class Node(BaseModel):
    ip: str = ""
    port: str = ""


local_nodes: set[str] = set()
# Leer las variables de entorno que contienen al nodo conocido
known_node_ip = os.environ.get("KNOWN_NODE_IP")
known_node_port = os.environ.get("KNOWN_NODE_PORT")


@asynccontextmanager
async def lifespan(app: FastAPI):
    if known_node_ip and known_node_port:
        # Se agrega a los nodos conocidos y le avisamos de nuestra existencia
        local_nodes.add(f"{known_node_ip}:{known_node_port}")
        requests.post(f"http://{known_node_ip}:{known_node_port}/nodes", json={"ip": known_node_ip, "port": known_node_port}
                      )
    else:
        print("ERROR al leer las variables de entorno")
    yield

app = FastAPI(lifespan=lifespan)


@app.get("/")
def root():
    return {"message": "Tarea 1 de sistemas distribuidos"}


@app.get("/nodes")
def get_nodes():
    return {"nodes": [node for node in local_nodes]}


@app.post("/nodes")
def add_node(new_node: Node):
    new_node_route = f"{new_node.ip}:{new_node.port}"
    if new_node_route not in local_nodes:
        local_nodes.add(new_node_route)
        # Si el nodo que recibo no está en el set es uno nuevo, avisarle a los conocidos
        for node in local_nodes:
            if node != new_node_route:
                requests.post(f"http://{node}/nodes", json={"ip": new_node.ip, "port": new_node.port})
        return {"node": new_node_route}
    else:
        return {"message": "El nodo ya es conocido"}
