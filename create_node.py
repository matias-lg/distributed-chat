import sys
# Crear una imagen de docker que ejecute el servidor web de main


def create_dockerfile(ip, port):
    dockerfile = '''
    FROM python:3.8-slim-buster
    '''




if __name__ == "__main__":
    # ip and port of the known node must be passed as arguments
    if len(sys.argv) != 3:
        print("Usage: python3 create_node.py <ip> <port>")
        sys.exit(1)

    ip = sys.argv[1]
    port = sys.argv[2]
    new_node_dockerfile = create_dockerfile(ip, port)
    # Build and run the docker image


