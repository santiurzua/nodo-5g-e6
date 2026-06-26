# Raspberry Pi: stack completo (almacenamiento + visualizacion + gateway)

Todo lo que corre en la Raspberry Pi de VitiScience, en un solo `docker compose`:

- **Almacenamiento + visualizacion** (siempre activo): ingesta de telemetria desde
  MQTT, ~3 dias de historial en InfluxDB y visualizacion en Grafana con auto-refresh
  cada 5 s.
- **Gateway BLE -> MQTT** (solo en la Pi, perfil `gateway`): lee los ESP32 por
  Bluetooth y publica al broker con el contrato de datos.

Ver [`docs/architecture.md`](docs/architecture.md) para el diagrama completo y
[`docs/data-contract.md`](docs/data-contract.md) para el contrato MQTT/JSON que
mantiene esta capa independiente del productor de datos.

```
ESP32 (BLE) --> gateway --> Mosquitto (MQTT) --> Telegraf --> InfluxDB (buffer 3 dias) --> Grafana
```

## Servicios

| Servicio  | URL / puerto          | Funcion                                            | Perfil   |
|-----------|-----------------------|----------------------------------------------------|----------|
| Grafana   | http://localhost:3000 | Dashboards (abrir "VitiScience Overview")          | siempre  |
| InfluxDB  | http://localhost:8086 | Base de datos de series de tiempo / UI admin       | siempre  |
| Mosquitto | localhost:1883 (TCP)  | Broker MQTT: publicadores y Telegraf conectan aqui | siempre  |
| Telegraf  | (interno)             | Escritor MQTT a InfluxDB                           | siempre  |
| gateway   | (host network)        | Lee los ESP32 por BLE y publica a Mosquitto        | `gateway`|

El servicio `gateway` esta detras del perfil `gateway` de compose, de modo que el
`docker compose up` por defecto NO lo levanta. En el PC de desarrollo (Windows, sin
BlueZ) se usa el simulador en su lugar; en la Raspberry Pi se agrega con
`--profile gateway`. Ver [`gateway/README.md`](gateway/README.md).

## Requisitos

- Docker Desktop (Windows/macOS) o Docker Engine + plugin compose (Raspberry Pi, SO 64-bit).

## Inicio rapido (desarrollo Windows, sin hardware)

```powershell
cd rpi
Copy-Item .env.example .env      # revisar y ajustar passwords/token
docker compose up -d             # solo los 4 servicios del dashboard
# o usar el helper:  ./run.ps1 up
```

Abrir Grafana en http://localhost:3000 (usuario/contrasena del `.env`). El dashboard
**VitiScience Overview** se provisiona automaticamente.

Para ver datos fluyendo sin hardware, iniciar el simulador en otra terminal:

```powershell
cd ../simulator
pip install -r requirements.txt
python sensor_simulator.py
```

### Con hardware real (Raspberry Pi)

```bash
cd rpi
cp .env.example .env             # editar passwords/token
docker compose --profile gateway up -d --build
docker logs -f vitiscience-gateway   # ver el enlace BLE y las publicaciones
```

Con ambos ESP32 encendidos, `node-01` y `node-02` aparecen en Grafana en pocos segundos.

### Script de conveniencia

```powershell
./run.ps1 up      # crear .env si falta + iniciar
./run.ps1 logs    # seguir logs
./run.ps1 ps      # estado
./run.ps1 down    # detener (mantiene datos)
./run.ps1 reset   # detener + borrar volumenes de datos
./run.ps1 urls    # imprimir URLs
```

## El dashboard

`VitiScience Overview` tiene:
1. **Temperatura actual**: ultima temperatura por nodo (stat).
2. **Humedad relativa actual**: ultima HR por nodo (gauge).
3. **Riesgo de oidio (simplificado)**: indicador de riesgo provisional: "Favorable"
   cuando temp entre 15-30 C y HR mayor o igual a 70% en la ultima hora. Ajustar esta regla con
   los criterios agronomicos de VitiScience (umbrales en las constantes del dashboard
   `temp_min` / `temp_max` / `rh_min`).
4. **Temperatura / Humedad por nodo**: serie de tiempo de 3 dias desde InfluxDB (auto-refresh 5 s).

## Despliegue en la Raspberry Pi

Ver la guia completa paso a paso en [`docs/deployment-guide.md`](docs/deployment-guide.md).
Cubre: instalacion del OS 64-bit, Docker, configuracion del HAT Teltonika Calyx 5G (APN Entel),
Tailscale para acceso remoto sobre NAT de operador, endurecimiento de seguridad y mantenimiento.

## Tests

```bash
cd rpi
pip install -r tests/requirements-test.txt
pytest tests/test_data_contract.py -v          # no requiere el stack
docker compose up -d
pytest tests/test_pipeline_integration.py -v   # verificacion completa MQTT -> InfluxDB -> Grafana
```

El test de integracion publica una lectura conocida y verifica que llega a InfluxDB y
que Grafana esta sano con sus datasources provisionados. Si el stack no esta corriendo,
ese test se omite (los tests de contrato siguen ejecutandose).

## Configuracion

Todos los parametros viven en `.env` (copiado desde `.env.example`): organizacion/bucket/
retencion/token de InfluxDB, credenciales de Grafana, puertos MQTT y los parametros del
gateway BLE. Si se cambia `INFLUXDB_BUCKET` tambien hay que actualizar la constante
`bucket` en el JSON del dashboard (o via las variables del dashboard en Grafana).

## Estructura

```
rpi/
  docker-compose.yml          # los 4 servicios del dashboard + gateway (perfil)
  .env.example                # copiar a .env
  run.ps1                     # wrapper de conveniencia
  config/
    mosquitto/mosquitto.conf
    telegraf/telegraf.conf
    grafana/provisioning/...  # datasources + proveedor de dashboards
    grafana/dashboards/vitiscience-overview.json
  gateway/                    # pasarela BLE -> MQTT (ver gateway/README.md)
    ble_mqtt_gateway.py
    ble_client.py             # diagnostico: guarda CSV por sensor
    config.py                 # configuracion compartida
    Dockerfile  requirements.txt
  docs/
    data-contract.md          # topic MQTT + payload JSON (fuente de verdad)
    telemetry.schema.json     # contrato legible por maquina
    architecture.md  deployment-guide.md
  tests/                      # contrato (sin stack) + integracion (con stack)
```
