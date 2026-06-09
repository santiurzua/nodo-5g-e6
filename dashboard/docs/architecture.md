# Arquitectura — Capa de almacenamiento y visualización VitiScience

## Dónde se ubica dentro del nodo completo

```
[SHT31]──I2C──[ESP32]──BLE──►[Raspberry Pi 4 gateway]──5G──►(internet)
                                        │
                                        │  (app gateway de Juan Ignacio:
                                        │   mesh_receiver / mqtt_connector)
                                        ▼
                        ┌──────────────────────────────────────────────────┐
                        │  ESTE ENTREGABLE — dashboard/ (stack Docker)     │
                        │  corre SOBRE la Raspberry Pi (es el servidor)    │
                        └──────────────────────────────────────────────────┘
```

La RPi es a la vez el gateway de terreno **y** el servidor: todo el stack de
almacenamiento + visualización corre ahí en Docker. Sin VM en la nube, sin servicio
de pago. Se accede desde un teléfono o PC a través de la red.

## El stack (un solo Docker Compose)

```
  Publicador (simulador hoy / gateway real mañana)
        │  MQTT publish  vitiscience/nodes/<id>/telemetry  (JSON)
        ▼
  ┌──────────┐      suscripción       ┌──────────┐        ┌──────────┐
  │ Mosquitto│ ────────────────────►  │ Telegraf │ ──────► │ InfluxDB │
  │  broker  │                        │ mqtt_    │ escribe │ bucket   │
  │ 1883/9001│                        │ consumer │         │'telemetry'
  └────┬─────┘                        └──────────┘         │ 3d reten.│
       │ suscripción (Grafana Live)                        └────┬─────┘
       │                                                         │ consulta Flux
       ▼                                                         ▼
  ┌─────────────────────────────────────────────────────────────────────┐
  │ Grafana  :3000   ── dashboard "VitiScience — Overview"               │
  │   • Datasource InfluxDB  → paneles históricos (últimos ~3 días)      │
  │   • Datasource MQTT      → panel de stream en vivo (tiempo real)     │
  └─────────────────────────────────────────────────────────────────────┘
        ▲ navegador: teléfono / PC (LAN o Tailscale)
```

### Dos caminos de lectura (por diseño, según Juan Ignacio)

| Camino      | Fuente                               | Qué sirve                                                           |
|-------------|--------------------------------------|---------------------------------------------------------------------|
| Histórico   | InfluxDB (bucket 3 días)             | Tendencias y gráficos de los últimos 2–3 días (el buffer).         |
| Tiempo real | Suscripción MQTT directa (Grafana Live) | Valores en vivo enviados al llegars — el "cable del broker a tu pantalla". |

Los paneles históricos también se refrescan cada 5 s, por lo que sirven como
fallback garantizado cuasi en tiempo real si el plugin experimental de datasource
MQTT no carga.

## Desacoplamiento — por qué el dashboard nunca depende del simulador

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
- `docker compose up -d` — idéntico al desarrollo.
- Apuntar el publicador del gateway real al broker de la Pi (`<ip-pi>:1883`,
  mismo topic/payload).

### Acceso desde teléfono / PC
- **Misma Wi-Fi/LAN:** abrir `http://<ip-pi>:3000`.
- **Remoto sobre internet / 5G:** la Pi generalmente no tiene IP pública en redes
  celulares (NAT de operador). Usar un **túnel gratuito y sin configuración —
  Tailscale** (recomendado): instalar en la Pi y en el teléfono/PC, luego navegar
  a la IP tailnet de la Pi en el puerto 3000. Sin port-forwarding, sin servicio de
  pago. (Cloudflare Tunnel es una alternativa gratuita equivalente.)

## Nota de seguridad (prototipo vs. terreno)

El broker del prototipo es **anónimo** y Grafana usa la contraseña de administrador
del `.env`. Antes de cualquier despliegue real en terreno: habilitar autenticación
MQTT (usuario/contraseña o TLS) en `config/mosquitto/mosquitto.conf`, dividir el
token de InfluxDB en solo-escritura (Telegraf) y solo-lectura (Grafana), y cambiar
todas las contraseñas por defecto. Nada de esto modifica el contrato de datos.
