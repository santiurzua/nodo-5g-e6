# VitiScience — Nodo autónomo de monitoreo de microclima en viñedos

**IEE3112 — Proyecto Final de Ingeniería Eléctrica, PUC.**

Diseño y prototipado de un nodo autónomo (TRL4) de monitoreo de microclima para
viñedos, orientado a detectar las condiciones que favorecen el **oídio de la vid**
(*Erysiphe necator*), enfermedad impulsada por la temperatura y la humedad relativa.

- **Host / cliente:** Centro de investigación VitiScience + CPS-RTC.
- **Contraparte técnica:** Juan Ignacio Lorca (CPS-RTC).
- **Sitio de terreno objetivo:** Viña Santa Emiliana.

> Los briefs del proyecto (propuesta, Hito 1, presupuesto, paper de referencia)
> están en [`Contexto Proyecto/`](Contexto%20Proyecto/).

---

## Cadena de hardware

```
[Sensor SHT31]
    │  I2C
[Microcontrolador ESP32]
    │  BLE  ← enlace confirmado (NO LoRa)
[Raspberry Pi 4 — 4 GB RAM]  ← gateway + servidor
    │  Teltonika Calyx 5G HAT (módulo EBD050000000)
    │  5G → Entel n78/n28 NSA+SA, fallback LTE/3G
[Dashboard]  ← corre sobre la propia RPi (ver despliegue)
```

**Energía:** panel solar 100 W → MPPT Victron BlueSolar 75/15 → batería LiFePO4
12V 30Ah → conversor reductor XH-M400 → RPi + módulo 5G. Dimensionado para 48 h de
autonomía sin sol. **Caja:** IP65 plástica 200×120×75 mm.

---

## Estructura del repositorio

```
.
├── README.md                   ← este archivo
│
├── Contexto Proyecto/          ← briefs del proyecto (referencia)
│   ├── Proyecto_Vitiscience.md
│   ├── E6_Hito1.md             ← entregable Hito 1 (completo)
│   ├── E6_presupuestos.md      ← tabla de presupuesto / BOM
│   └── 5g-edge-gateway3.md     ← paper de referencia (IoT+5G, misma arquitectura)
│
├── dashboard/                  ← almacenamiento + visualización
│   ├── docker-compose.yml      ← Mosquitto + Telegraf + InfluxDB + Grafana
│   ├── .env.example            ← copiar a .env antes del primer arranque
│   ├── run.ps1                 ← wrapper de conveniencia (Windows PowerShell)
│   ├── config/                 ← config de Mosquitto, Telegraf y Grafana
│   ├── docs/                   ← contrato de datos, esquema JSON, arquitectura
│   └── tests/                  ← tests unitarios + integración
│
└── simulator/                  ← publicador MQTT sin hardware (para desarrollo)
    ├── sensor_simulator.py     ← punto de entrada
    ├── models.py               ← modelo diurno temp/HR (Python puro, testeable)
    ├── config.py               ← configuración por variables de entorno
    └── tests/
```

---

## Subsistema de dashboard (almacenamiento + visualización)

La capa de **almacenamiento + visualización** está implementada y validada. Corre
con un solo comando `docker compose up`.

| Servicio  | Imagen                       | Rol                                                          |
|-----------|------------------------------|-------------------------------------------------------------|
| Mosquitto | `eclipse-mosquitto:2`        | Broker MQTT. Publicadores en :1883. WebSocket en :9001.     |
| Telegraf  | `telegraf:1.32`              | Suscribe al wildcard MQTT → escribe en InfluxDB.            |
| InfluxDB  | `influxdb:2.7`               | Base de datos de series de tiempo. Retención 3 días.        |
| Grafana   | `grafana/grafana-oss:11.3.0` | UI del dashboard. Datasources + dashboard auto-provisionados. |

Todas las imágenes son multi-arquitectura (amd64 + arm64): el mismo stack corre en
Windows/macOS/Linux (desarrollo) y en la RPi (despliegue).

### Flujo de datos (dos caminos de lectura)

```
Publicador ──MQTT──► Mosquitto ──► Telegraf ──► InfluxDB ──► Grafana (histórico)
                         │
                         └─────────────────────────────────► Grafana (stream en vivo)
```

- **Camino histórico:** Telegraf escribe cada mensaje en InfluxDB (retención 3 días).
  Grafana consulta con Flux y refresca cada 5 s.
- **Camino en tiempo real:** Grafana se suscribe directo al broker vía el plugin
  `grafana-mqtt-datasource`; los datos llegan al navegador apenas se publican,
  independiente de la base de datos.

---

## Cómo correr el dashboard localmente

### Requisitos
- Python 3.10+ (con pip)
- Docker Desktop (Windows/macOS) o Docker Engine (Linux), con Docker Compose.

### Primera vez

**Windows (PowerShell):**
```powershell
cd dashboard
Copy-Item .env.example .env        # luego edita .env y cambia passwords/token
docker compose up -d               # o:  ./run.ps1 up
Start-Process http://localhost:3000
```

**macOS / Linux (bash):**
```bash
cd dashboard
cp .env.example .env               # luego edita .env y cambia passwords/token
docker compose up -d
xdg-open http://localhost:3000     # macOS: open http://localhost:3000
```

Login de Grafana: `GRAFANA_USER` / `GRAFANA_PASSWORD` desde `.env`
(por defecto `admin` / `changeme-grafana-pass`). Abre el dashboard
**"VitiScience — Overview"**.

> ⚠️ **Nunca subas tu archivo `.env`** — contiene credenciales y está ignorado por
> git. Solo se versiona `.env.example`.

### Uso diario

**Windows:**
```powershell
cd dashboard
./run.ps1 up       # iniciar
./run.ps1 logs     # ver logs
./run.ps1 ps       # estado
./run.ps1 down     # detener (mantiene datos)
./run.ps1 reset    # detener + borrar datos
./run.ps1 urls     # imprimir URLs de los servicios
```

**macOS / Linux:**
```bash
cd dashboard
docker compose up -d            # iniciar
docker compose logs -f          # ver logs
docker compose ps               # estado
docker compose down             # detener (mantiene datos)
docker compose down -v          # detener + borrar datos
```

---

## Cómo correr el simulador

Publica telemetría sintética al broker para ver el flujo de datos sin hardware.

```bash
cd simulator
pip install -r requirements.txt
python sensor_simulator.py
```

Configuración por variables de entorno (valores por defecto entre corchetes):

| Variable          | Default     | Descripción                              |
|-------------------|-------------|------------------------------------------|
| `MQTT_HOST`       | `localhost` | Host del broker                          |
| `MQTT_PORT`       | `1883`      | Puerto TCP del broker                    |
| `SIM_NODE_COUNT`  | `3`         | Número de nodos simulados                |
| `SIM_NODE_IDS`    | (no fijado) | IDs explícitos, ej. `node-01,node-02`    |
| `SIM_INTERVAL_S`  | `5`         | Segundos entre rondas de publicación     |
| `SIM_SEED`        | (no fijado) | Fija el RNG para ruido reproducible      |

Ejemplo (bash):
```bash
SIM_NODE_COUNT=5 SIM_INTERVAL_S=2 python sensor_simulator.py
```

Ejemplo (PowerShell):
```powershell
$env:SIM_NODE_COUNT = "5"; $env:SIM_INTERVAL_S = "2"
python sensor_simulator.py
```

---

## Contrato de datos (decoupling)

El dashboard y el publicador (simulador hoy, gateway real mañana) están
**totalmente desacoplados**. Comparten solo el contrato de datos:

- **Topic:** `vitiscience/nodes/<node_id>/telemetry`
- **Payload** (JSON, UTF-8):
  ```json
  {
    "node_id": "node-01",
    "timestamp": "2026-06-07T12:00:00Z",
    "temperature_c": 23.45,
    "humidity_pct": 56.12,
    "battery_v": 12.7,
    "rssi_dbm": -78
  }
  ```
  Requeridos: `node_id`, `temperature_c`, `humidity_pct`.
  Opcionales: `timestamp` (ISO-8601 UTC), `battery_v`, `rssi_dbm`.

Especificación completa en [`dashboard/docs/data-contract.md`](dashboard/docs/data-contract.md).
Esquema JSON legible por máquina en
[`dashboard/docs/telemetry.schema.json`](dashboard/docs/telemetry.schema.json).

---

## Tests

```bash
# Tests unitarios / de contrato (no requieren el stack levantado)
cd simulator
pip install -r requirements-dev.txt
pytest tests -v

cd ../dashboard
pip install -r tests/requirements-test.txt
pytest tests/test_data_contract.py -v

# Test de integración (el stack debe estar corriendo)
pytest tests/test_pipeline_integration.py -v
```

El test de integración publica un payload conocido → verifica que llega a InfluxDB
→ verifica que Grafana está sano y ambos datasources provisionados.

---

## Despliegue en la Raspberry Pi

1. **SO:** Raspberry Pi OS 64-bit (requerido para imágenes Docker arm64).
2. **Instalar Docker:**
   ```bash
   curl -fsSL https://get.docker.com | sh && sudo usermod -aG docker $USER
   ```
3. **Copiar la carpeta `dashboard/`** a la Pi (git clone, SCP, USB, etc.).
4. En la Pi:
   ```bash
   cd dashboard
   cp .env.example .env   # editar passwords/token
   docker compose up -d
   ```
5. **Acceso desde la misma LAN:** `http://<ip-de-la-pi>:3000`
6. **Acceso remoto sobre 5G** (NAT de operador = sin IP pública): instalar
   [Tailscale](https://tailscale.com/download) en la Pi y en el teléfono/PC, luego
   navegar a `http://<tailscale-ip-de-la-pi>:3000`. Gratis, sin port forwarding.
7. **Apuntar el gateway real** al broker: debe publicar en
   `vitiscience/nodes/<id>/telemetry` con el payload del contrato de datos. Único
   cambio: host del broker de `localhost` → IP de la Pi. **Cero cambios en el dashboard.**

---

## Cómo colaborar

1. **Clonar** el repositorio:
   ```bash
   git clone <url-del-repo>
   cd "IEE3112 - Proyecto de Título"
   ```
   > 💡 Recomendado: clonar en una ruta **fuera de OneDrive/Drive sincronizado**.
   > Que la nube sincronice la carpeta `.git/` puede corromper el repositorio.

2. **Crear una rama** para tu trabajo (no trabajar directo sobre `main`):
   ```bash
   git checkout -b feature/mi-cambio
   ```

3. **Confirmar y subir** tus cambios:
   ```bash
   git add -A
   git commit -m "Descripción breve del cambio"
   git push -u origin feature/mi-cambio
   ```

4. **Abrir un Pull Request** en GitHub hacia `main` para revisión del grupo.

5. Antes de correr el dashboard, recuerda copiar `dashboard/.env.example` →
   `dashboard/.env` (nunca subas tu `.env`).

---

## Hitos

| Hito | Estado | Resumen |
|------|--------|---------|
| **Hito 1 — Propuesta Conceptual** | ✅ Completo | Bloques funcionales, requisitos de sensor/comunicaciones/cómputo/energía, selección de componentes, presupuesto estimado (~$722k CLP). Ver `Contexto Proyecto/E6_Hito1.md`. |
| **Hito 2 — Ingeniería Básica** | 🔲 Pendiente | Diagramas de bajo nivel (electrónica, firmware, software), diagramas de secuencia de comunicación, specs de hardware/firmware, análisis de proveedores, presupuesto final. |
| **Hito 3 — Prototipado y Validación** | 🔲 Pendiente | Prototipo físico, BoM, esquemáticos PCB, firmware, pruebas de desempeño + resultados, propuesta de mejoras, costo final. |
