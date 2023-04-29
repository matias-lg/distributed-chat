import os
import requests
from fastapi import FastAPI
from pydantic import BaseModel
from contextlib import asynccontextmanager


class NodeMsg(BaseModel):
    sender: str = ""
    ip: str = ""
    port: str = ""


local_nodes: set[str] = set()
# Leer las variables de entorno que contienen al nodo conocido
known_node_ip = os.environ.get("KNOWN_NODE_IP")
known_node_port = os.environ.get("KNOWN_NODE_PORT")
this_node_name = os.environ.get("NODE_NAME")
this_node_ip = os.environ.get("NODE_IP")
this_node_port = os.environ.get("NODE_PORT")
this_node_addr = os.environ.get("NODE_ADDR")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # El primer nodo se inicia sin nodos conocidos
    if known_node_ip != "IGNORE" and known_node_port != "IGNORE":
        # Se agrega a los nodos conocidos y le avisamos de nuestra existencia
        local_nodes.add(f"{known_node_ip}:{known_node_port}")
        requests.post(f"http://{known_node_ip}:{known_node_port}/nodes",
                      json={"ip": this_node_ip, "port": this_node_port,
                            "sender": this_node_addr}
                      )
    print(f"{this_node_name} iniciado con dirección {this_node_addr}")
    yield

app = FastAPI(lifespan=lifespan)


@app.get("/")
def root():
    return {"message": f"Tarea 1 de sistemas distribuidos",
            "node_name": this_node_name,
            "node_addr": this_node_addr
            }


@app.get("/nodes")
def get_nodes():
    return {"nodes": [node for node in local_nodes]}


@app.post("/nodes")
def add_node(node_msg: NodeMsg):
    new_node_route = f"{node_msg.ip}:{node_msg.port}"
    sender = node_msg.sender
    print(f"Recibido nuevo nodo: {new_node_route} desde {sender}")
    if new_node_route not in local_nodes and new_node_route != this_node_addr:
        local_nodes.add(new_node_route)
        # Si el nodo que recibo no está en el set es uno nuevo, avisarle a los conocidos
        # de este nuevo nodo
        for node in local_nodes:
            if node not in [sender, new_node_route]:
                requests.post(f"http://{node}/nodes", json={"ip": node_msg.ip,
                                                            "port": node_msg.port,
                                                            "sender": this_node_addr
                                                            })
        # Igualmente avisarle de mi existencia al nuevo nodo
        requests.post(f"http://{new_node_route}/nodes", json={"ip": this_node_ip,
                                                              "port": this_node_port,
                                                              "sender": this_node_addr
                                                              })
        return {"node": new_node_route}
    else:
        return {"message": "El nodo ya es conocido"}
