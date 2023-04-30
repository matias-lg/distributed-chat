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
INFO:     Uvicorn running on http://0.0.0.0:825 (Press CTRL+C to quit)
```
bastará con acceder desde el navegador a `0.0.0.0:825` para ver información acerca del nodo. O bien,
ejecutar `curl 0.0.0.0:825`. La respuesta es `{"message":"Tarea 1 de sistemas distribuidos","node_name":"first","node_addr":"172.18.209.249:825"}`.
También podemos ver los nodos que este conoce mediante un GET a `0.0.0.0:825/nodes` desde el host. Desde el shell de otro nodo se debe usar su dirección dentro de la subnet, `172.18.209.249:825/nodes`. 

### Crear otro nodo que conozca al primero
Basta con ejecutar `create_node.sh` pasando la IP y puerto del primer nodo, que se muestra en consola o haciendo una petición como se explicó
anteriormente.

```
./create_node.sh anothernode 172.18.209.249 825
```
Al ejecutar el script de esta manera, se creará un segundo nodo que agregará a su lista de conocidos
la IP y puerto entregado. Este nuevo nodo le informará de su existencia al primer nodo. Por lo tanto,
si ahora revisamos la ruta `/nodes` en el primer nodo, debería aparecer el segundo:
desde el host: `curl 0.0.0.0:825/nodes` o desde el shell de uno de los nodos, `curl 172.18.209.249:825`
responde:
```
{"nodes":["172.18.73.78:289"]}
```
la IP del segundo en nuestra subnet aparece dentro de sus IPs conocidas. Si hacemos lo mismo para el segundo nodo se verá la IP y puerto del primero.

De esta misma forma se pueden crear cuantos nodos se quiera. Si se entregan IPs y puertos conocidos
se observará que los nodos de la red se empezarán a informar de la existencia de todos los que vayamos agregando.
