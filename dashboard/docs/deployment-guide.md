# Guia de despliegue: Raspberry Pi + 5G + Tailscale

Guia completa para desplegar el stack VitiScience desde cero en una Raspberry Pi 4,
configurar la conectividad 5G con el HAT Teltonika Calyx y habilitar acceso remoto con
Tailscale. Sigue las secciones en orden la primera vez.

Para el contexto del sistema completo, ver [`architecture.md`](architecture.md).
Para el contrato MQTT/JSON, ver [`data-contract.md`](data-contract.md).

---

## 1. Prerequisitos de hardware

| Componente | Especificacion |
|------------|---------------|
| Compute | Raspberry Pi 4 - 4 GB RAM |
| HAT 5G | Teltonika Calyx (EBD050000000) |
| SIM | Entel 5G prepago (NSA+SA, bandas n78/n28) |
| Almacenamiento | microSD 32 GB clase 10 (minimo) o SSD USB |
| Alimentacion | LiFePO4 12V 30Ah + Victron BlueSolar MPPT 75/15 + step-down XH-M400 |
| Red local | Cable Ethernet para la primera configuracion |

---

## 2. Preparar la microSD (OS 64-bit)

El SO debe ser **64-bit** porque las imagenes Docker para ARM64 lo requieren.

1. Descargar [Raspberry Pi Imager](https://www.raspberrypi.com/software/) e instalarlo en el PC.
2. Insertar la microSD en el PC.
3. En Raspberry Pi Imager:
   - **Dispositivo**: Raspberry Pi 4
   - **SO**: Raspberry Pi OS (64-bit)
   - **Almacenamiento**: la microSD
4. Antes de escribir, hacer clic en **Editar configuracion** (icono de engranaje):
   - Establecer nombre de host, por ejemplo `vitiscience-gw`
   - Habilitar SSH (usar autenticacion por contrasena la primera vez)
   - Crear usuario y contrasena
   - Si hay WiFi disponible para el primer arranque, configurarlo aqui
5. Escribir la imagen. Esto tarda varios minutos.
6. Insertar la microSD en la RPi y encenderla.

---

## 3. Primera conexion por SSH

```bash
# Desde Windows PowerShell o cmd:
ssh pi@vitiscience-gw.local
# Si el hostname no resuelve, usar la IP directa (verla en el router o con un scanner de red)
ssh pi@192.168.X.X
```

Una vez dentro:

```bash
sudo raspi-config
```

En `raspi-config`:
- **6 Advanced Options > A1 Expand Filesystem**: asegura usar toda la microSD.
- **5 Localisation Options**: ajustar timezone a America/Santiago y locale.
- Salir y reiniciar cuando pida.

Actualizar el sistema:

```bash
sudo apt update && sudo apt full-upgrade -y
sudo reboot
```

---

## 4. Instalar Docker en la Raspberry Pi

```bash
# Script oficial de Docker (valido en Raspberry Pi OS / Debian)
curl -fsSL https://get.docker.com | sh

# Agregar el usuario actual al grupo docker para no necesitar sudo
sudo usermod -aG docker $USER

# Cerrar la sesion SSH y volver a conectarse para que el grupo tome efecto
exit
```

Reconectar y verificar:

```bash
docker run --rm hello-world
docker compose version
```

Ambos deben ejecutarse sin errores. Si `docker compose` falla, instalar el plugin:

```bash
sudo apt install docker-compose-plugin -y
```

---

## 5. Copiar el dashboard a la Raspberry Pi

Elegir uno de estos metodos:

### Opcion A: SCP desde Windows

```powershell
# Desde PowerShell en el PC, dentro de la carpeta del proyecto:
scp -r "dashboard/" pi@vitiscience-gw.local:/home/pi/vitiscience/dashboard
```

### Opcion B: Git clone (si el repo es accesible)

```bash
# En la RPi:
sudo apt install git -y
git clone <url-del-repo> /home/pi/vitiscience
```

### Opcion C: USB

Copiar la carpeta `dashboard/` a un pendrive FAT32. En la RPi:

```bash
sudo mount /dev/sda1 /mnt
cp -r /mnt/dashboard /home/pi/vitiscience/
sudo umount /mnt
```

---

## 6. Configurar y arrancar el stack

```bash
cd /home/pi/vitiscience/dashboard

# Crear el .env a partir del ejemplo
cp .env.example .env
nano .env   # editar passwords y token con valores seguros
```

Variables criticas en `.env`:

```
INFLUXDB_ADMIN_USER=admin
INFLUXDB_ADMIN_PASSWORD=<contrasena-segura>
INFLUXDB_TOKEN=<token-largo-aleatorio>
GRAFANA_USER=admin
GRAFANA_PASSWORD=<contrasena-segura>
```

Para generar un token seguro:
```bash
openssl rand -hex 32
```

Iniciar el stack:

```bash
docker compose up -d
```

Verificar que los cuatro servicios esten sanos:

```bash
docker compose ps
# Todos deben mostrar "Up" o "healthy"
```

Ver logs en tiempo real:

```bash
docker compose logs -f
# Ctrl+C para salir
```

Abrir Grafana desde el mismo LAN:
```
http://vitiscience-gw.local:3000
```
Usuario y contrasena: los del `.env`. El dashboard **VitiScience Overview** se carga automaticamente.

---

## 7. Configurar el HAT Teltonika Calyx 5G

### 7.1 Instalacion fisica

1. Apagar la RPi (`sudo shutdown -h now`).
2. Montar el HAT Calyx sobre los GPIO de la RPi. El HAT se apoya en los 40 pines y ademas
   usa un cable USB interno (de los puertos USB de la RPi al conector del modem).
3. Insertar la SIM Entel en la ranura del HAT.
4. Volver a encender.

### 7.2 Instalar ModemManager y NetworkManager

```bash
sudo apt install modemmanager network-manager -y
sudo systemctl enable ModemManager NetworkManager
sudo systemctl start ModemManager NetworkManager
```

Verificar que el modem sea detectado (puede tardar 15-30 s despues del arranque):

```bash
mmcli -L
```

Salida esperada similar a:
```
/org/freedesktop/ModemManager1/Modem/0 [Teltonika] Calyx
```

Obtener info del modem (sustituir `0` por el indice correcto):

```bash
mmcli -m 0
```

### 7.3 Crear la conexion Entel

```bash
sudo nmcli connection add \
  type gsm \
  con-name "Entel-5G" \
  ifname "*" \
  apn "bam.entelpcs.cl"
```

Activar la conexion:

```bash
sudo nmcli connection up "Entel-5G"
```

Verificar la conexion:

```bash
nmcli connection show "Entel-5G"
ip route   # debe aparecer una ruta via la interfaz del modem (wwan0 o similar)
ping -c 4 8.8.8.8
```

Ver la calidad de senal y tecnologia de acceso (5G/LTE):

```bash
mmcli -m 0 --signal-get
mmcli -m 0 | grep "access tech"
```

### 7.4 Hacer la conexion persistente al arranque

NetworkManager la activa automaticamente si `autoconnect` esta en yes (es el default). Verificar:

```bash
nmcli connection show "Entel-5G" | grep autoconnect
```

Si dice `no`:

```bash
sudo nmcli connection modify "Entel-5G" connection.autoconnect yes
```

### 7.5 Diagnostico 5G

| Sintoma | Comando de diagnostico |
|---------|----------------------|
| Modem no aparece en `mmcli -L` | `lsusb`, `dmesg | tail -30` |
| Sin IP en la interfaz | `ip addr show wwan0` |
| Ping falla pero IP existe | `cat /etc/resolv.conf`, revisar APN |
| Senal baja | Reubicar la antena, revisar `mmcli -m 0 --signal-get` |

---

## 8. Instalar y configurar Tailscale

Tailscale crea una VPN de malla (mesh) privada. Permite acceder a la RPi desde
cualquier red aunque este detras de NAT de operador (lo que ocurre con 5G).

### 8.1 Instalar en la Raspberry Pi

```bash
curl -fsSL https://tailscale.com/install.sh | sh
```

Habilitar e iniciar:

```bash
sudo systemctl enable tailscaled
sudo tailscale up
```

La terminal muestra una URL para autenticar:
```
To authenticate, visit:
  https://login.tailscale.com/a/XXXXXXXX
```

Abrir esa URL en cualquier navegador, iniciar sesion (o crear cuenta gratis) y autorizar el dispositivo.

### 8.2 Verificar la IP Tailscale

```bash
sudo tailscale status
# Ejemplo:
# 100.64.1.10   vitiscience-gw        pi@            linux   -
```

La IP `100.x.x.x` es la IP permanente de la RPi dentro de la red Tailscale.

### 8.3 Instalar Tailscale en el PC / telefono

- Windows/macOS/Linux: [tailscale.com/download](https://tailscale.com/download)
- Android/iOS: buscar "Tailscale" en la tienda de aplicaciones
- Iniciar sesion con la misma cuenta que se uso en el paso 8.1

### 8.4 Acceder al dashboard de forma remota

Con el PC o telefono en cualquier red (datos moviles, WiFi de casa, etc.):

```
http://100.x.x.x:3000
```

Usando el hostname:

```
http://vitiscience-gw:3000
```

Tambien funciona para SSH:

```bash
ssh pi@vitiscience-gw
```

---

## 9. Verificar acceso remoto completo

Esta secuencia confirma que todo el pipeline funciona desde fuera de la LAN:

```bash
# 1. En la RPi: asegurarse de que el stack este corriendo
docker compose ps

# 2. En el PC: desconectarse del mismo WiFi que la RPi (o usar datos moviles)
# 3. Abrir  http://vitiscience-gw:3000  en el navegador -> debe cargar Grafana

# 4. En el PC o en la RPi: publicar un mensaje MQTT de prueba
#    (requiere mqtt-cli o mosquitto-clients instalado en algun lado)
mosquitto_pub -h vitiscience-gw -p 1883 \
  -t "vitiscience/nodes/node-test/telemetry" \
  -m '{"node_id":"node-test","temperature_c":22.5,"humidity_pct":60.0}'

# 5. En Grafana: abrir "VitiScience Overview", verificar que "node-test" aparece
#    en los paneles de temperatura y humedad actuales
```

Si el paso 4 da "connection refused", verificar que el puerto 1883 no este bloqueado por
el firewall de la RPi (`sudo ufw status`). Si UFW esta activo:

```bash
sudo ufw allow 1883/tcp comment "MQTT broker"
sudo ufw allow 3000/tcp comment "Grafana"
```

---

## 10. Conectar el gateway real (cuando el firmware ESP32 este listo)

El gateway (codigo de Juan Ignacio, `mqtt_connector`) debe publicar al broker con estos
parametros exactos (no requiere ningun cambio en el dashboard):

| Parametro | Valor |
|-----------|-------|
| Host del broker | `localhost` (si corre en la misma RPi) o IP/hostname de la RPi |
| Puerto | `1883` |
| Topic | `vitiscience/nodes/<node_id>/telemetry` |
| Payload | JSON con campos obligatorios `node_id`, `temperature_c`, `humidity_pct` |
| Auth | Ninguna (prototipo anonimo) |

Ver el contrato completo en [`data-contract.md`](data-contract.md).

Para probar desde la RPi antes de tener el firmware:

```bash
# Instalar cliente MQTT
sudo apt install mosquitto-clients -y

# Publicar una lectura de prueba
mosquitto_pub -h localhost -p 1883 \
  -t "vitiscience/nodes/node-01/telemetry" \
  -m '{"node_id":"node-01","timestamp":"2026-06-18T12:00:00Z","temperature_c":23.4,"humidity_pct":58.0,"battery_v":12.7,"rssi_dbm":-72}'
```

---

## 11. Endurecimiento de seguridad (antes del despliegue de campo)

El prototipo usa configuracion anonima para simplificar el desarrollo. Antes de
instalarlo en el viñedo, aplicar estos cambios:

### 11.1 Cambiar todos los passwords del .env

Asegurarse de que `.env` no tiene los valores por defecto:
- `INFLUXDB_ADMIN_PASSWORD`: minimo 16 caracteres
- `INFLUXDB_TOKEN`: `openssl rand -hex 32`
- `GRAFANA_PASSWORD`: minimo 12 caracteres

### 11.2 Agregar autenticacion MQTT

Crear el archivo de contraseñas:

```bash
# En la RPi, dentro de config/mosquitto/:
docker compose exec mosquitto mosquitto_passwd -c /mosquitto/config/passwd gateway
# pedira una contrasena para el usuario "gateway"
```

Editar `config/mosquitto/mosquitto.conf` para requerir autenticacion:

```
# Cambiar esta linea:
allow_anonymous true
# por:
allow_anonymous false
password_file /mosquitto/config/passwd
```

Actualizar `config/telegraf/telegraf.conf` con las credenciales:

```toml
[[inputs.mqtt_consumer]]
  username = "gateway"
  password = "<la-misma-contrasena>"
```

Reiniciar el stack:

```bash
docker compose restart mosquitto telegraf
```

### 11.3 Limitar acceso a puertos

Si solo el gateway necesita conectarse al broker:

```bash
sudo ufw deny 1883/tcp     # cerrar acceso publico
sudo ufw allow from <ip-del-gateway> to any port 1883
```

Grafana puede quedar accesible via Tailscale sin abrir puertos al publico.

---

## 12. Mantenimiento del stack

### Ver logs de un servicio especifico

```bash
docker compose logs -f grafana
docker compose logs -f influxdb
docker compose logs -f telegraf
docker compose logs -f mosquitto
```

### Reiniciar un servicio sin detener los demas

```bash
docker compose restart telegraf
```

### Detener el stack (los datos en InfluxDB se conservan)

```bash
docker compose down
```

### Detener y borrar todos los datos (inicio limpio)

```bash
docker compose down -v
```

### Actualizar las imagenes Docker

```bash
docker compose pull
docker compose up -d
```

### Ver espacio en disco

```bash
# Espacio total de Docker (imagenes + volumenes + contenedores)
docker system df

# Solo el volumen de InfluxDB
docker volume inspect dashboard_influxdb-data
df -h /var/lib/docker/volumes/
```

Si el disco esta casi lleno, reducir la retencion en `.env`:
```
INFLUXDB_RETENTION=1d   # en vez de 3d
```
Luego `docker compose up -d` para aplicar el cambio.

### Hacer backup de los datos de InfluxDB

```bash
# Dentro del contenedor InfluxDB:
docker compose exec influxdb influx backup /tmp/backup --token $DOCKER_INFLUXDB_INIT_ADMIN_TOKEN
# Copiar el backup fuera del contenedor:
docker compose cp influxdb:/tmp/backup ./influxdb-backup-$(date +%F)
```

---

## 13. Solucion de problemas

### El stack no arranca

```bash
docker compose logs        # ver mensajes de error de todos los servicios
docker compose ps          # identificar cual servicio falla
```

Causas comunes:
- `.env` no existe o tiene variables mal escritas -> revisar nombres contra `.env.example`
- Puerto 3000 o 1883 ocupado por otro proceso -> `sudo lsof -i :3000`
- Sin espacio en disco -> `df -h`

### Grafana no muestra datos

1. Verificar que Telegraf esta recibiendo mensajes: `docker compose logs telegraf | grep "metric"`
2. Verificar que InfluxDB tiene datos:
   ```bash
   docker compose exec influxdb influx query \
     --org vitiscience \
     --token $DOCKER_INFLUXDB_INIT_ADMIN_TOKEN \
     'from(bucket:"vitiscience-data") |> range(start:-1h) |> limit(n:5)'
   ```
3. En Grafana: verificar que el rango de tiempo del dashboard incluye los ultimos datos.
4. Datasource mal configurado: en Grafana ir a Connections > Data sources > InfluxDB > Test.

### No llegan datos al broker

```bash
# Suscribirse al topic wildcard para ver todo lo que llega:
mosquitto_sub -h localhost -p 1883 -t "vitiscience/#" -v
```

Si el publicador conecta pero no se ven mensajes, verificar el topic exacto contra el
contrato en `data-contract.md`.

### El modem 5G no conecta

```bash
mmcli -L                    # listar modems detectados
mmcli -m 0                  # estado del modem 0
nmcli connection show       # listar conexiones
journalctl -u ModemManager -n 50  # logs de ModemManager
```

Pasos de diagnostico:
1. `lsusb` - verificar que el modem aparece como dispositivo USB
2. `dmesg | grep -i usb` - errores de reconocimiento del hardware
3. Si la SIM no es detectada, extraerla y reinsertarla con la RPi apagada

### Tailscale no alcanza la RPi

```bash
# En la RPi:
sudo tailscale status       # debe mostrar "connected"
sudo tailscale ping <ip-del-pc>  # prueba de conectividad punto a punto

# Si aparece "offline":
sudo systemctl restart tailscaled
sudo tailscale up
```

Si la RPi esta detras de un firewall corporativo que bloquea los puertos de Tailscale,
activar el modo relay: `sudo tailscale up --netfilter-mode=off` (ultimo recurso).

### Grafana muestra "No data source found"

El datasource se provisiona automaticamente desde `config/grafana/provisioning/`.
Si no aparece, verificar que el volumen esta montado:

```bash
docker compose exec grafana ls /etc/grafana/provisioning/datasources/
```

Si el archivo no esta ahi, revisar el `docker-compose.yml` y que la carpeta
`config/grafana/` esta en la misma ubicacion que `docker-compose.yml`.
