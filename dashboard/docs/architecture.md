# Arquitectura: Capa de almacenamiento y visualización VitiScience

## Donde se ubica dentro del nodo completo

```
[SHT31]--I2C--[ESP32]--BLE-->[Raspberry Pi 4 gateway]--5G-->(internet)
                                        |
                                        |  (app gateway de Juan Ignacio:
                                        |   mesh_receiver / mqtt_connector)
                                        v
                        +-------------------------------------------------+
                        |  ESTE ENTREGABLE: dashboard/ (stack Docker)     |
                        |  corre SOBRE la Raspberry Pi (es el servidor)   |
                        +-------------------------------------------------+
```

La RPi es a la vez el gateway de terreno **y** el servidor: todo el stack de
almacenamiento + visualizacion corre ahi en Docker. Sin VM en la nube, sin servicio
de pago. Se accede desde un telefono o PC a traves de la red.

## El stack (un solo Docker Compose)

```
  Publicador (simulador hoy / gateway real manana)
        |  MQTT publish  vitiscience/nodes/<id>/telemetry  (JSON)
        v
  +----------+      suscripcion       +----------+        +----------+
  | Mosquitto| ─────────────────────► | Telegraf | ──────► | InfluxDB |
  |  broker  |                        | mqtt_    | escribe | bucket   |
  |   :1883  |                        | consumer |         |'telemetry'
  +----------+                        +----------+         | 3d reten.|
                                                           +-----+----+
                                                                 | consulta Flux
                                                                 v
                        +--------------------------------------------+
                        | Grafana  :3000                             |
                        | dashboard "VitiScience Overview"           |
                        | Datasource InfluxDB - ultimos ~3 dias      |
                        | auto-refresh cada 5 s                      |
                        +--------------------------------------------+
        ^ navegador: telefono / PC (LAN o Tailscale)
```

### Camino de lectura

| Camino    | Fuente                   | Que sirve                                       |
|-----------|--------------------------|-------------------------------------------------|
| Historico | InfluxDB (bucket 3 dias) | Tendencias y graficos de los ultimos 2-3 dias. Auto-refresh 5 s. |

## Desacoplamiento: por que el dashboard nunca depende del simulador

Lo único compartido entre *quien produce los datos* y *quien los muestra* es el
**contrato de datos** (`docs/data-contract.md` + `docs/telemetry.schema.json`):

- mismo topic MQTT: `vitiscience/nodes/<node_id>/telemetry`
- mismo payload JSON

Reemplazar `simulator/` por el `mqtt_connector` del gateway real no cambia nada
dentro de `dashboard/`. El contrato se aplica desde ambos lados mediante tests
(`simulator/tests/test_payload_contract.py`, `dashboard/tests/test_data_contract.py`).

## Despliegue y acceso remoto

### Desarrollo local (Windows/Linux/macOS)
Docker Desktop corre el mismo `docker-compose.yml`. Todo está en `localhost`.
Ver el README para los pasos de arranque y demo.

### En la Raspberry Pi
- Usar Raspberry Pi OS **64-bit** (todas las imágenes son multi-arch / arm64).
- `docker compose up -d` (identico al desarrollo).
- Apuntar el publicador del gateway real al broker de la Pi (`<ip-pi>:1883`,
  mismo topic/payload).

### Acceso desde teléfono / PC
- **Misma Wi-Fi/LAN:** abrir `http://<ip-pi>:3000`.
- **Remoto sobre internet / 5G:** la Pi generalmente no tiene IP pública en redes
  celulares (NAT de operador). Usar un **tunel gratuito y sin configuracion:
  Tailscale** (recomendado): instalar en la Pi y en el telefono/PC, luego navegar
  a la IP tailnet de la Pi en el puerto 3000. Sin port-forwarding, sin servicio de
  pago. (Cloudflare Tunnel es una alternativa gratuita equivalente.)

## Nota de seguridad (prototipo vs. terreno)

El broker del prototipo es **anónimo** y Grafana usa la contraseña de administrador
del `.env`. Antes de cualquier despliegue real en terreno: habilitar autenticación
MQTT (usuario/contraseña o TLS) en `config/mosquitto/mosquitto.conf`, dividir el
token de InfluxDB en solo-escritura (Telegraf) y solo-lectura (Grafana), y cambiar
todas las contraseñas por defecto. Nada de esto modifica el contrato de datos.
