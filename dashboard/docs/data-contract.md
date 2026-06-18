# Contrato de datos: Telemetria VitiScience

Este documento es la **fuente de verdad única** que desacopla al *publicador* (el simulador
hoy, el gateway real de la Raspberry Pi mañana) del *dashboard* (almacenamiento + visualización).

Mientras un publicador respete este contrato, el dashboard funciona **sin ningún cambio de código**.
Nada dentro de `dashboard/` sabe ni le importa quién produjo los datos.

---

## 1. Transporte: MQTT

| Propiedad           | Valor                                                         |
|---------------------|--------------------------------------------------------------|
| Broker              | Mosquitto                                                     |
| Host (desarrollo)   | `localhost`                                                   |
| Host (desplegado)   | la Raspberry Pi corriendo el stack `dashboard/`              |
| Puerto (TCP)        | `1883`                                                        |
| Autenticacion       | anonima para el prototipo (ver seccion 5 para endurecimiento)|
| QoS                 | `1` recomendado (al menos una vez); `0` aceptable            |
| Retain              | `false`                                                      |

### Topic

```
vitiscience/nodes/<node_id>/telemetry
```

- `<node_id>` es el identificador único del nodo sensor (ej. `node-01`).
- Un nodo publica en exactamente un topic.
- El dashboard se suscribe con el wildcard `vitiscience/nodes/+/telemetry`.

Ejemplo: `vitiscience/nodes/node-01/telemetry`

---

## 2. Payload: JSON

Un objeto JSON UTF-8 por mensaje. Ejemplo:

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

### Campos

| Campo            | Tipo    | Unidad | Requerido | Notas                                                                 |
|------------------|---------|--------|-----------|-----------------------------------------------------------------------|
| `node_id`        | string  | -      | **si**    | Debe coincidir con `<node_id>` en el topic.                          |
| `temperature_c`  | number  | C      | **si**    | Temperatura del aire. Rango plausible -40 a 85 (rango del SHT31).   |
| `humidity_pct`   | number  | %HR    | **si**    | Humedad relativa. Rango 0 a 100.                                     |
| `timestamp`      | string  | -      | no        | UTC ISO-8601 (RFC3339), ej. `2026-06-07T12:00:00Z`. Si se omite, Telegraf registra la hora de llegada. |
| `battery_v`      | number  | V      | no        | Voltaje de la bateria del nodo (LiFePO4 aprox. 12 V nominal).       |
| `rssi_dbm`       | number  | dBm    | no        | Intensidad de senal del enlace (ej. BLE/5G), tipicamente negativo.   |

La versión legible por máquina de estas reglas está en
[`telemetry.schema.json`](./telemetry.schema.json) (JSON Schema, draft 2020-12) y es
validada por tests en **ambos** lados: simulador y dashboard.

---

## 3. Mapeo de almacenamiento (InfluxDB)

El input `mqtt_consumer` de Telegraf decodifica el payload y lo escribe en InfluxDB:

| Concepto InfluxDB | Valor                                                       |
|-------------------|-------------------------------------------------------------|
| Measurement       | `telemetry`                                                 |
| Tag               | `node_id`                                                   |
| Fields            | `temperature_c`, `humidity_pct`, `battery_v`, `rssi_dbm`   |
| Time              | desde `timestamp`, si no la hora de llegada del mensaje    |
| Bucket            | `telemetry` (retencion 3 dias - el buffer historico)        |

---

## 4. Camino de lectura (lado dashboard)

**Historico**: Grafana consulta InfluxDB (bucket `telemetry`, ultimos ~3 dias) con Flux.
Los paneles se refrescan cada 5 s.

El contrato definido arriba es la unica interfaz entre el publicador y Grafana.

---

## 5. Notas para el gateway real / endurecimiento en producción

- El `mqtt_connector` del gateway debe publicar en el **topic exacto** y con el payload
  definido aquí.
- Para el prototipo el broker es anónimo. Antes del despliegue en terreno, habilitar
  usuario/contraseña (o certificados TLS de cliente) en `mosquitto.conf` y actualizar
  las credenciales del publicador y de Telegraf. Esto **no** modifica el topic ni el
  payload del contrato.
- Mantener los payloads bien por debajo de los límites de MQTT/Telegraf; un mensaje de
  telemetría ocupa < 256 bytes, acorde al presupuesto de paquetes pequeños discutido en
  la literatura del proyecto.
