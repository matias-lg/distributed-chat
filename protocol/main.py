import os
import random
from fastapi import FastAPI
from fastapi_utils.tasks import repeat_every
from pydantic import BaseModel
from .utils import print_receive_message, inform_node

class NodeMsg(BaseModel):
    sender: str = ""
    new_node_address: str = ""


local_nodes: set[str] = set()
# Leer las variables de entorno que contienen al nodo conocido
known_node_ip = os.environ.get("KNOWN_NODE_IP")
known_node_port = os.environ.get("KNOWN_NODE_PORT")
this_node_name = os.environ.get("NODE_NAME")
this_node_ip = os.environ.get("NODE_IP")
this_node_port = os.environ.get("NODE_PORT")
this_node_addr = os.environ.get("NODE_ADDR") or "IGNORE"

app = FastAPI()
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
    new_address = node_msg.new_node_address
    sender = node_msg.sender
    if new_address in local_nodes:
        return {"message": "El nodo ya es conocido"}
    if new_address == this_node_addr:
        return {"message": "No me envíes a mi mismo"}

    print_receive_message(sender, new_address)
    local_nodes.add(new_address)
    # Avisarle a nuestros conocidos de la existencia del nuevo nodo
    for node in local_nodes:
        if node not in [sender, new_address]:
            inform_node(node, new_address, this_node_addr)
    # Avisarle de mi existencia al nuevo nodo, si es que él no se envió a si mismo
    # (eso significa que ya me conoce)
    if sender != new_address:
        inform_node(new_address, this_node_addr, this_node_addr)
    return {"message": "Nodo agregado exitosamente"}

@app.on_event("startup")
def initial_setup():
    # El primer nodo se inicia sin nodos conocidos
    if known_node_ip != "IGNORE" and known_node_port != "IGNORE":
        # Se agrega a los nodos conocidos y le avisamos de nuestra existencia
        known_address: str = f"{known_node_ip}:{known_node_port}"
        local_nodes.add(known_address)
        inform_node(known_address, this_node_addr, this_node_addr)
    print(f"{this_node_name} iniciado con dirección {this_node_addr}")

# Cada 30 segundos informaremos a un nodo aleatorio de la existencia de otro nodo aleatorio, para evitar
# que por un error en la red un nodo quede aislado
@app.on_event("startup")
@repeat_every(seconds=30)
def randomnly_inform():
    if len(local_nodes) > 0:
        random_dest_node = random.choice(tuple(local_nodes))
        inform_node(random_dest_node, this_node_addr, this_node_addr)
