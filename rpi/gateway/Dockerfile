# Gateway BLE -> MQTT de VitiScience.
#
# bleak habla con el BlueZ del host por D-Bus, por lo que el contenedor debe
# correr con network_mode: host y montar /var/run/dbus (ver docker-compose.yml,
# servicio "gateway"). bleak trae su propia capa D-Bus en Python, asi que no se
# necesitan paquetes de sistema adicionales.
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY config.py ble_mqtt_gateway.py ble_client.py ./

# Salida de logs sin buffer para que docker logs muestre todo en vivo.
ENV PYTHONUNBUFFERED=1

CMD ["python", "ble_mqtt_gateway.py"]
