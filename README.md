# Sistemas Distribuidos: Tarea 1

Esta tarea consiste de un sistema distribuido donde los nodos que ejecutan el protocolo
mantienen en memoria la lista de los demás nodos. Se pueden crear nodos de dos formas:
La primera crea un nodo que inmediatamente se conecta con otro conocido, a través del comando:
```
./create_node.sh <nombre_nodo> <ip_nodo_conocido> <puerto_nodo_conocido>
```

O bien, crear un nodo que no conozca a ningún otro:
```
./create_node.sh <nombre_nodo>
```

## Configuración del entorno
Para poder ejecutar el proyecto, es necesario tener docker y docker compose.

En primer lugar, se debe buildear la imagen base que usan los nodos:
`docker build -t distnode .`

### Crear subnet
Todos los nodos se comunican dentro de una subnet de Docker, para poder levantar los nodos con sus
propias IP es necesario crear esta subnet:
``docker network create --subnet=172.18.0.0/16 tarea1net``

### Crear el primer nodo
Como es el primer nodo, no tendrá nodos conocidos:
```
./create_node.sh firstnode
```

El script `create_node.sh` genera una IP aleatoria dentro del rango posible de la subnet,
cuando el nodo recién creado ejecute el protocolo, mostrará en la consola su IP y puerto, este
puerto se mapeará al mismo puerto en el host. Luego si aparece
```
INFO:     Uvicorn running on http://0.0.0.0:254 (Press CTRL+C to quit)
```
bastará con acceder desde el navegador a `0.0.0.0:254` para ver información acerca del nodo.
Podemos ver los nodos que este conoce mediante un GET a `0.0.0.0:254/nodes`


### Crear otro nodo que conozca al primero
Basta con ejecutar `create_node.sh` pasando la IP y puerto del primer nodo (nuevamente, esto lo podemos
obtener con un GET a 0.0.0.0/254 en nuestro ejemplo) 
```
./create_node.sh anothernode 172.18.64.150 254
```
Al ejecutar el script de esta manera, se creará un segundo nodo que agregará a su lista de conocidos
la IP y puerto entregado. Inmediatamente le informará de su existencia al primer nodo. Por lo tanto,
si ahora revisamos la ruta `/nodes` en el primer nodo, debería aparecer el segundo!

De esta misma forma se pueden crear cuantos nodos se quiera. Si se entregan IPs y puertos conocidos
se observará que los nodos de la red se empezarán a informar de la existencia de todos los que vayamos agregando.
