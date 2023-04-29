# Sistemas Distribuidos: Tarea 1

## Buildear Dockerfile base para nodos
`docker build -t distnode .`

## Crear subnet
Para correr la tarea, es necesario crear una subnet de Docker para que los nodos puedan
tener sus propias IPs.
``docker network create --subnet=172.18.0.0/16 tarea1net``


## Crear el primer nodo
Como es el primer nodo, no tendrá nodos conocidos.
`docker run --ip 172.18.3.1 -p 80:80 --net tarea1net --name firstnode distnode:latest`

## Ejecutar script con pasando IP y Puerto de un nodo
`./create_node <IP> <PORT>`
Por ejemplo:
`./create_node 192.168.21.1 80`
o bien, ejecutar el comando manualmente para crear un nodo:
```bash
docker run --ip 172.18.0.23 -p 172:80 --net tarea1net \
-e KNOWN_NODE_IP='mila'\
-e KNOWN_NODE_PORT='the_westie'\
distnode:latest
```
