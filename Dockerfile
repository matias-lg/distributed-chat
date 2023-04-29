FROM python:3.9
WORKDIR /code
COPY ./requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt
COPY ./protocol /code/protocol
# Asignaremos la ip y puerto conocidos por el nodo como una variable de entorno
# la pasaremos al invocar el script para crear un nodo
CMD ["uvicorn", "protocol.main:app", "--host", "0.0.0.0", "--port", "80"]
