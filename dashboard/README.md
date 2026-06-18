# Dashboard (almacenamiento + visualizacion)

Capa de almacenamiento y visualizacion para el nodo de microclima VitiScience. Ingesta
telemetria (temperatura y humedad relativa) desde el broker MQTT, guarda ~3 dias de
historial en InfluxDB y lo muestra en Grafana con auto-refresh cada 5 s.

Todo corre en **un solo stack Docker Compose** identico en Windows (desarrollo) y en la
Raspberry Pi (servidor). Ver [`docs/architecture.md`](docs/architecture.md) para el
diagrama completo y [`docs/data-contract.md`](docs/data-contract.md) para el contrato
MQTT/JSON que mantiene esta capa independiente del productor de datos.

```
Mosquitto (MQTT) --> Telegraf --> InfluxDB (buffer 3 dias) --> Grafana
```

## Servicios

| Servicio  | URL / puerto          | Funcion                                        |
|-----------|-----------------------|------------------------------------------------|
| Grafana   | http://localhost:3000 | Dashboards (abrir "VitiScience Overview")      |
| InfluxDB  | http://localhost:8086 | Base de datos de series de tiempo / UI admin   |
| Mosquitto | localhost:1883 (TCP)  | Broker MQTT: publicadores y Telegraf conectan aqui |
| Telegraf  | (interno)             | Escritor MQTT a InfluxDB                       |

## Requisitos

- Docker Desktop (Windows/macOS) o Docker Engine + plugin compose (Raspberry Pi, SO 64-bit).

## Inicio rápido (desarrollo Windows)

```powershell
cd dashboard
Copy-Item .env.example .env      # revisar y ajustar passwords/token
docker compose up -d
# o usar el helper:  ./run.ps1 up
```

Abrir Grafana en http://localhost:3000 (usuario/contrasena del `.env`, por defecto
`admin` y la contrasena que hayas configurado). El dashboard **VitiScience Overview**
se provisiona automaticamente.

Para ver datos fluyendo, iniciar el simulador en otra terminal:

```powershell
cd ../simulator
pip install -r requirements.txt
python sensor_simulator.py
```

En pocos segundos los paneles historicos se llenan con datos.

### Script de conveniencia

```powershell
./run.ps1 up      # crear .env si falta + iniciar
./run.ps1 logs    # seguir logs
./run.ps1 ps      # estado
./run.ps1 down    # detener (mantiene datos)
./run.ps1 reset   # detener + borrar volúmenes de datos
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

Mismos comandos; usar Raspberry Pi OS 64-bit. Luego apuntar el publicador del gateway
real al broker de la Pi (`<ip-pi>:1883`) con el mismo topic/payload. Para acceso remoto
sobre 5G, instalar **Tailscale** en la Pi y en el teléfono/PC y navegar a la IP tailnet
de la Pi en el puerto 3000. Ver [`docs/architecture.md`](docs/architecture.md).

## Tests

```bash
cd dashboard
pip install -r tests/requirements-test.txt
pytest tests/test_data_contract.py -v          # no requiere el stack
docker compose up -d
pytest tests/test_pipeline_integration.py -v   # verificación completa MQTT→InfluxDB→Grafana
```

El test de integración publica una lectura conocida y verifica que llega a InfluxDB y
que Grafana está sano con sus datasources provisionados. Si el stack no está corriendo,
ese test se omite (los tests de contrato siguen ejecutándose).

## Configuración

Todos los parámetros viven en `.env` (copiado desde `.env.example`): organización/bucket/
retención/token de InfluxDB, credenciales de Grafana, puertos MQTT. Si se cambia
`INFLUXDB_BUCKET` también hay que actualizar la constante `bucket` en el JSON del dashboard
(o via las variables del dashboard en Grafana).

## Estructura

```
dashboard/
  docker-compose.yml          # el stack de 4 servicios
  .env.example                # copiar a .env
  run.ps1                     # wrapper de conveniencia
  config/
    mosquitto/mosquitto.conf
    telegraf/telegraf.conf
    grafana/provisioning/...  # datasources + proveedor de dashboards
    grafana/dashboards/vitiscience-overview.json
  docs/
    data-contract.md          # topic MQTT + payload JSON (fuente de verdad)
    telemetry.schema.json     # contrato legible por máquina
    architecture.md
  tests/                      # contrato (sin stack) + integración (con stack)
```
