import requests
import time

def print_inform_message(dest_addr: str, new_addr: str, this_node_addr: str):
    if new_addr == this_node_addr:
        print(f"Se informó a {dest_addr} de mi existencia")
    else:
        print(f"Se informó a {dest_addr} de la existencia de {new_addr}")

def print_receive_message(sender: str, new_addr: str):
    if sender == new_addr:
        print(f"{sender} me informó de su existencia")
    else:
        print(f"{sender} me informó de la existencia de {new_addr}")

# Los nodos se comunican a través de un POST a /nodes
def inform_node(dest_addr: str, new_addr: str, this_node_addr: str):
    sleep_time = 5
    ntries = 3
    for _ in range(ntries):
        try:
            requests.post(f"http://{dest_addr}/nodes",
                          json={"new_node_address": new_addr,
                                "sender": this_node_addr}
                          )
            print_inform_message(dest_addr, new_addr, this_node_addr)
            return
        except requests.exceptions.ConnectionError:
            time.sleep(sleep_time)
    print(f"No se pudo conectar con {dest_addr} luego de {ntries} intentos")