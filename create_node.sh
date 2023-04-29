#!/bin/sh
node_name=$1
known_ip=${2:-IGNORE}
known_port=${3:-IGNORE}

# Se genera una IP y puerto aleatorio para el nuevo nodo
rand_ip=$(awk 'BEGIN{srand(); printf "172.18.%d.%d\n", int(254*rand()), int(254*rand())}')
rand_port=$(awk 'BEGIN{srand(); printf "%d\n", int(1000*rand())}')

echo "Creando nodo con IP: $rand_ip y puerto: $rand_port"

# variables de entorno temporales para crear el nuevo nodo
tmpenv="NODE_NAME=$node_name
NODE_PORT=$rand_port
NODE_IP=$rand_ip
KNOWN_NODE_IP=$known_ip
KNOWN_NODE_PORT=$known_port
NODE_ADDR=$rand_ip:$rand_port"

echo "$tmpenv" > .env

docker compose --project-name $node_name up app

if [ $? -eq 0 ]; then
  echo "Se creó el nuevo nodo"
else
  echo "Error al ejecutar el nuevo nodo"
fi
