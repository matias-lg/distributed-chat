# Sistemas Distribuidos: Tarea 3

Esta tarea consiste de un sistema distribuido donde los nodos que ejecutan el protocolo
se informan de la existencia de otros nodos a través de una API REST por medio de HTTP.

Para agregar nodos a la red, se proveen scripts en bash y python que son equivalentes: `create_node.sh` y `create_node.py`, la forma
de ejecutarse se explica más adelante.

## Configuración del entorno
Para poder ejecutar el proyecto, es necesario tener docker y docker compose. También es necesario darle permisos de ejecución al script
para crear nodos: `chmod +x ./create_node.sh`

### Build Dockerfile
En primer lugar, se debe buildear la imagen base que usan los nodos:
```bash
docker build -t distnode .
```

### Crear subnet
Todos los nodos se comunican dentro de una network de Docker, para poder levantar los nodos con sus
propias IP es necesario crear la network "tarea2net" con la subnet `172.18.0.0/16`:

```bash
docker network create --subnet=172.18.0.0/16 tarea2net
```


## Ejecutar el protocolo
Para crear nodos existen dos formas:
`./create_node.sh <nombre_nodo>` y `./create_node.sh <nombre_nodo> <ip_conocida> <puerto_conocido>`
La primera forma creará un nodo que no conocerá a ningún otro. La segunda forma crea un nodo que conocerá al nodo
con dirección `$<ip_conocida>:$<puerto_conocido>` dentro de la red tarea2net.

### Crear el primer nodo
Como es el primer nodo, no tendrá nodos conocidos:
```bash
./create_node.sh primernodo
```

El script `create_node.sh` genera una IP aleatoria dentro del rango posible de la red tarea2net,
cuando el nodo recién creado ejecute el protocolo, mostrará en la consola su IP y puerto, este
puerto se mapeará al mismo puerto en el host. Luego si aparece

```
Creando nodo con IP: 172.18.106.56 y puerto: 840
```

Desde el host se podrá acceder a este nodo a través de la dirección `0.0.0.0:840`, para acceder al nodo desde otros nodos,
se deberá hacer desde la dirección `172.18.106.56:840`.

Podemos verificar que esté funcionando desde el host:
```
curl 0.0.0.0:840
```

responde:
```json
{"message":"Tarea 1 de sistemas distribuidos","node_name":"firstnode","node_addr":"172.18.106.56:840"}
```
y,
```
curl 0.0.0.0:840/nodes
```

entrega (aun no hay ningún otro nodo conocido):
```json
{"nodes":[]}
```

### Crear otro nodo que conozca al primero
Basta con ejecutar `create_node.sh` pasando la IP y puerto del primer nodo (que se muestra en consola al crearlo, o haciendo un GET a su ruta `/`):
```
./create_node.sh secondnode 172.18.106.56 840
```
creará un segundo nodo:
```
Creando nodo con IP: 172.18.137.191 y puerto: 556
```

y observamos que en la consola del primer nodo se muestra:
```
firstnode | 172.18.137.191:556 me informó de su existencia
firstnode | INFO: 172.18.137.191:57118 - "POST /nodes HTTP/1.1" 200 OK
```
El segundo nodo recién creado le informa al primero de su existencia a través de un POST request a la ruta `/nodes` del primero.
De esta forma, si ahora hacemos un GET a `\nodes` del primer nodo. (desde el host a 0.0.0.0:840/nodes, desde el terminal del container del segundo nodo a 172.18.106.56:840/nodes),
el primer nodo responde:
```json
{"nodes":["172.18.137.191:556"]}
```
¡Tiene en memoria la dirección del segundo nodo! Si hacemos lo mismo para el segundo nodo se debería mostrar la dirección del primero. De esta forma se pueden ir agregando más
nodos, los que se irán informando sobre la existencia de los demás. Por ejemplo, si creamos un tercer nodo que conozca la IP del segundo, el tercero le informará al segundo de su existencia,
más adelante el segundo nodo le informará al primero la existencia del tercero.
NOTA: Cada 5 segundos, cada nodo le informa de la existencia de un nodo aleatorio en su lista de conocidos a otro (también elegido al azar dentro de sus conocidos).

## Chat global de mensajes
Se pueden enviar mensajes entre los nodos, estos mensajes se mantienen en un chat global el cual cada nodo mantiene una copia. Para mantener el orden de los mensajes, cada
nodo se sincroniza con un servidor NTP para obtener un timestamp de los mensajes. De esta forma, todos los nodos guardan los mensajes en el mismo orden.

### Publicar un mensaje en el chat global
Para publicar un mensaje en el chat global, se debe hacer un POST request a la ruta `/messages` de algún nodo.
Por ejemplo, desde el host:
```bash
curl -X POST -H "Content-type: application/json" -d '{"message":"Hola a todos, este es el primer mensaje"}' 0.0.0.0:840/messages
```
Después de un tiempo, el mensaje aparecerá en la lista de mensajes de todos los nodos, se puede verificar haciendo un GET a la ruta `/messages` de cada nodo.