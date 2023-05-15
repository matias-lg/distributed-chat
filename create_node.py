#!/usr/bin/env python3
import os
import subprocess
import sys
from random import randint

node_name = sys.argv[1]
known_ip = sys.argv[2] if len(sys.argv) > 2 else "IGNORE"
known_port = sys.argv[3] if len(sys.argv) > 3 else "IGNORE"

# Generate a random IP and port for the new node
rand_ip = f"172.18.{randint(0, 254)}.{randint(0, 254)}"
rand_port = randint(0, 1000)

print(f"Creando nodo con IP: {rand_ip} y puerto: {rand_port}")

# Create the .env file with temporary environment variables
env_content = f"""\
NODE_NAME={node_name}
NODE_PORT={rand_port}
NODE_IP={rand_ip}
KNOWN_NODE_IP={known_ip}
KNOWN_NODE_PORT={known_port}
NODE_ADDR={rand_ip}:{rand_port}
"""
with open(".env", "w") as env_file:
    env_file.write(env_content)

# Check if docker compose is installed
compose_command = "docker-compose"
try:
    subprocess.run(["docker", "compose"], capture_output=True, check=True)
except subprocess.CalledProcessError:
    compose_command = "docker compose"

# Run docker-compose to create the new node
subprocess.run([compose_command, "--project-name", node_name, "up", "app"], check=True)

if subprocess.CompletedProcess.returncode == 0:
    print("Se creó el nuevo nodo")
else:
    print("Error al ejecutar el nuevo nodo")
