#!/bin/sh
node_name=$1
known_ip=$2
known_port=$3

# Se genera una IP y puerto aleatorio para el nuevo nodo
rand_ip=$(awk 'BEGIN{srand(); printf "172.18.%d.%d\n", int(254*rand()), int(254*rand())}')
rand_port=$(awk 'BEGIN{srand(); printf "%d\n", int(1000*rand())}')

echo "Creando nodo con IP: $rand_ip y puerto: $rand_port"
docker run --ip $rand_ip -p $rand_port:80 --net tarea1net -e KNOWN_NODE_IP=$known_ip -e KNOWN_NODE_PORT=$known_port --name $node_name distnode:latest

if [ $? -eq 0 ]; then
  echo "Se creó el nuevo nodo"
else
  echo "Error al ejecutar el nuevo nodo"
fi
