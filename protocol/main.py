import os
import random
import ntplib
from fastapi import FastAPI, Request, BackgroundTasks
from fastapi_utils.tasks import repeat_every
from .local_set import LocalSet
from .utils import print_receive_message, inform_node, propagate_message
from .classes import NodeInfo, SetMessage, ApiSimpleMessage, ApiSetMessage


# set que contiene las direcciones de los nodos conocidos
local_nodes = LocalSet[str]()
# set que contiene los mensajes del chat
local_messages = LocalSet[SetMessage]()

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
def get_nodes():
    return {"nodes": local_nodes.get_all_elements()}


@app.post("/nodes")
def add_node(node_msg: NodeInfo, background_tasks: BackgroundTasks):
    new_address = node_msg.new_node_address
    sender = node_msg.sender
    if local_nodes.contains(new_address):
        return {"message": "El nodo ya es conocido"}
    if new_address == THIS_NODE_ADDR:
        return {"message": "No me envíes a mi mismo"}

    print_receive_message(sender, new_address)
    local_nodes.add(new_address)
    # Avisarle a nuestros conocidos de la existencia del nuevo nodo
    for node in local_nodes.get_all_elements():
        if node not in [sender, new_address]:
            background_tasks.add_task(inform_node, node, new_address, THIS_NODE_ADDR)
    # Avisarle de mi existencia al nuevo nodo, si es que él no se envió a si mismo
    # (eso significa que ya me conoce)
    if sender != new_address:
        inform_node(new_address, THIS_NODE_ADDR, THIS_NODE_ADDR)
    return {"message": "Nodo agregado exitosamente"}


@app.on_event("startup")
def initial_setup():
    # El primer nodo se inicia sin nodos conocidos
    if KNOWN_NODE_IP != "IGNORE" and KNOWN_NODE_PORT != "IGNORE":
        # Se agrega a los nodos conocidos y le avisamos de nuestra existencia
        known_address: str = f"{KNOWN_NODE_IP}:{KNOWN_NODE_PORT}"
        local_nodes.add(known_address)
        inform_node(known_address, THIS_NODE_ADDR, THIS_NODE_ADDR)
    print(f"{THIS_NODE_NAME} iniciado con dirección {THIS_NODE_ADDR}")


@app.on_event("startup")
@repeat_every(seconds=5)
# Cada 30 segundos informaremos a un nodo aleatorio de la existencia de otro nodo aleatorio, para evitar que por un error en la red un nodo quede aislado
def randomnly_inform():
    all_nodes = local_nodes.get_all_elements()
    print(f"Nodos conocidos: {all_nodes}")
    random_dest_node = random.choice(all_nodes)
    random_new_node = random.choice(all_nodes + [THIS_NODE_ADDR])
    while random_new_node == random_dest_node:
        random_new_node = random.choice(all_nodes + [THIS_NODE_ADDR])
    inform_node(random_dest_node, random_new_node, THIS_NODE_ADDR)
# END Descubrimiento de nodos


# BEGIN Chat
@app.get("/messages")
def get_messages(last: int  = 0):
    last = int(max(0, last))
    all_messages = local_messages.get_all_elements()
    # ordenar por timestamp
    all_messages.sort(key=lambda x: x.timestamp)
    all_messages = [ msg.content for msg in all_messages]  
    if last == 0:
        return {"messages": all_messages}

    last = min(last, len(all_messages))
    return {"messages": all_messages[:last]} 

@app.post("/messages")
def add_message(apiMessage: ApiSimpleMessage, request: Request, background_tasks: BackgroundTasks):
    if request.client is None:
        return {"error": "No se pudo obtener la dirección del cliente"}
    msg = apiMessage.message
    client_addr = request.client.host
    #El timestamp se obtiene del servidor NTP
    c = ntplib.NTPClient()
    ntp_response = c.request(NTP_SERVER)
    msg_timestamp = ntp_response.tx_time
    new_message = SetMessage(content=msg, sender=client_addr, timestamp=msg_timestamp)
    local_messages.add(new_message)
    # avisar a los nodos conocidos del nuevo mensaje
    background_tasks.add_task(propagate_messages, new_message)
    return {"success": "Mensaje publicado exitosamente"}

@app.post("/sync_messages")
def sync_messages(message: ApiSetMessage):
    new_set_message = SetMessage(content=message.content, sender=message.sender, timestamp=message.timestamp)
    if message in local_messages.get_all_elements():
        return {"success": "El mensaje ya existe"}
    else:
        local_messages.add(new_set_message)
        return {"success": "Mensaje sincronizado exitosamente"}

def propagate_messages(new_message: SetMessage):
    for node in local_nodes.get_all_elements():
        just_ip = node.split(":")[0]
        if just_ip not in [THIS_NODE_ADDR, new_message.sender]:
            propagate_message(node, new_message)
# END Chat