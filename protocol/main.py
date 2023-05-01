import os
import random
from fastapi import FastAPI
from fastapi_utils.tasks import repeat_every
from pydantic import BaseModel
from .local_node import LocalNode
from .utils import print_receive_message, inform_node


class NodeMsg(BaseModel):
    sender: str = ""
    new_node_address: str = ""


# set que contiene las direcciones de los nodos conocidos
local_nodes = LocalNode()

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
async def get_nodes():
    return {"nodes": await local_nodes.get_all_nodes()}


@app.post("/nodes")
async def add_node(node_msg: NodeMsg):
    new_address = node_msg.new_node_address
    sender = node_msg.sender
    if await local_nodes.contains(new_address):
        return {"message": "El nodo ya es conocido"}
    if new_address == this_node_addr:
        return {"message": "No me envíes a mi mismo"}

    print_receive_message(sender, new_address)
    await local_nodes.add(new_address)
    # Avisarle a nuestros conocidos de la existencia del nuevo nodo
    for node in await local_nodes.get_all_nodes():
        if node not in [sender, new_address]:
            inform_node(node, new_address, this_node_addr)
    # Avisarle de mi existencia al nuevo nodo, si es que él no se envió a si mismo
    # (eso significa que ya me conoce)
    if sender != new_address:
        inform_node(new_address, this_node_addr, this_node_addr)
    return {"message": "Nodo agregado exitosamente"}


@app.on_event("startup")
async def initial_setup():
    # El primer nodo se inicia sin nodos conocidos
    if known_node_ip != "IGNORE" and known_node_port != "IGNORE":
        # Se agrega a los nodos conocidos y le avisamos de nuestra existencia
        known_address: str = f"{known_node_ip}:{known_node_port}"
        await local_nodes.add(known_address)
        inform_node(known_address, this_node_addr, this_node_addr)
    print(f"{this_node_name} iniciado con dirección {this_node_addr}")


@app.on_event("startup")
@repeat_every(seconds=30)
# Cada 30 segundos informaremos a un nodo aleatorio de la existencia de otro nodo aleatorio, para evitar que por un error en la red un nodo quede aislado
async def randomnly_inform():
    all_nodes = await local_nodes.get_all_nodes()
    if len(all_nodes) < 2:
        return
    random_dest_node = random.choice(all_nodes)
    random_new_node = random.choice(all_nodes + [this_node_addr])
    while random_new_node == random_dest_node:
        random_new_node = random.choice(all_nodes + [this_node_addr])
    inform_node(random_dest_node, random_new_node, this_node_addr)
