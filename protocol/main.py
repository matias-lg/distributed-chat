import os
import random
import ntplib
from fastapi import FastAPI, Request
from fastapi_utils.tasks import repeat_every
from .local_set import LocalSet
from .utils import print_receive_message, inform_node, propagate_message
from .classes import NodeInfo, chatMessage, ApiMessage


# set que contiene las direcciones de los nodos conocidos
local_nodes = LocalSet[str]()
# set que contiene los mensajes del chat
local_messages = LocalSet[chatMessage]()

# Leer las variables de entorno que contienen al nodo conocido
KNOWN_NODE_IP = os.environ.get("KNOWN_NODE_IP")
KNOWN_NODE_PORT = os.environ.get("KNOWN_NODE_PORT")
THIS_NODE_NAME = os.environ.get("NODE_NAME")
THIS_NODE_IP = os.environ.get("NODE_IP")
THIS_NODE_PORT = os.environ.get("NODE_PORT")
THIS_NODE_ADDR = os.environ.get("NODE_ADDR") or "IGNORE"

# Servidor HTTP
app = FastAPI()

# Instanciar la conexión al servidor NTP
NTP_SERVER = "time.google.com"

@app.get("/")
def root():
    return {"message": f"Tarea 1 de sistemas distribuidos",
            "node_name": THIS_NODE_NAME,
            "node_addr": THIS_NODE_ADDR
            }


# BEGIN Descubrimiento de nodos
@app.get("/nodes")
async def get_nodes():
    return {"nodes": await local_nodes.get_all_elements()}


@app.post("/nodes")
async def add_node(node_msg: NodeInfo):
    new_address = node_msg.new_node_address
    sender = node_msg.sender
    if await local_nodes.contains(new_address):
        return {"message": "El nodo ya es conocido"}
    if new_address == THIS_NODE_ADDR:
        return {"message": "No me envíes a mi mismo"}

    print_receive_message(sender, new_address)
    await local_nodes.add(new_address)
    # Avisarle a nuestros conocidos de la existencia del nuevo nodo
    for node in await local_nodes.get_all_elements():
        if node not in [sender, new_address]:
            inform_node(node, new_address, THIS_NODE_ADDR)
    # Avisarle de mi existencia al nuevo nodo, si es que él no se envió a si mismo
    # (eso significa que ya me conoce)
    if sender != new_address:
        inform_node(new_address, THIS_NODE_ADDR, THIS_NODE_ADDR)
    return {"message": "Nodo agregado exitosamente"}


@app.on_event("startup")
async def initial_setup():
    # El primer nodo se inicia sin nodos conocidos
    if KNOWN_NODE_IP != "IGNORE" and KNOWN_NODE_PORT != "IGNORE":
        # Se agrega a los nodos conocidos y le avisamos de nuestra existencia
        known_address: str = f"{KNOWN_NODE_IP}:{KNOWN_NODE_PORT}"
        await local_nodes.add(known_address)
        inform_node(known_address, THIS_NODE_ADDR, THIS_NODE_ADDR)
    print(f"{THIS_NODE_NAME} iniciado con dirección {THIS_NODE_ADDR}")


@app.on_event("startup")
@repeat_every(seconds=30)
# Cada 30 segundos informaremos a un nodo aleatorio de la existencia de otro nodo aleatorio, para evitar que por un error en la red un nodo quede aislado
async def randomnly_inform():
    all_nodes = await local_nodes.get_all_elements()
    if len(all_nodes) < 2:
        return
    random_dest_node = random.choice(all_nodes)
    random_new_node = random.choice(all_nodes + [THIS_NODE_ADDR])
    while random_new_node == random_dest_node:
        random_new_node = random.choice(all_nodes + [THIS_NODE_ADDR])
    inform_node(random_dest_node, random_new_node, THIS_NODE_ADDR)
# END Descubrimiento de nodos


# BEGIN Chat
@app.get("/messages")
async def get_messages(last: int  = 0):
    print("Aqui tienes tu mensaje")
    last = int(max(0, last))
    all_messages = await local_messages.get_all_elements()
    # ordenar por timestamp
    all_messages.sort(key=lambda x: x.timestamp, reverse=True)
    all_messages = [ msg.content for msg in all_messages]  
    if last == 0:
        return {"messages": all_messages}

    last = min(last, len(all_messages))
    return {"messages": all_messages[:last]} 

@app.post("/messages")
async def add_message(apiMessage: ApiMessage, request: Request):
    if request.client is None:
        return {"error": "No se pudo obtener la dirección del cliente"}
    msg = apiMessage.message
    client_addr = request.client.host
    print(f"Recibido mensaje de {client_addr}")
    # El timestamp se obtiene del servidor NTP
    # c = ntplib.NTPClient()
    # ntp_response = c.request(NTP_SERVER)
    # msg_timestamp = ntp_response.tx_time
    msg_timestamp = 123
    new_message = chatMessage(content=msg, sender=client_addr, timestamp=msg_timestamp)
    await local_messages.add(new_message)

    # avisar a los nodos conocidos del nuevo mensaje
    for node in await local_nodes.get_all_elements():
        just_ip = node.split(":")[0]
        if just_ip not in [THIS_NODE_ADDR]:
            propagate_message(node, ApiMessage(message=msg))

    return {"success": "Mensaje publicado exitosamente"}
# END Chat