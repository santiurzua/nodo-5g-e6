# Hito 1: Propuesta Conceptual

## Bloques funcionales del sistema

Se definen los siguientes bloques y sus funciones:

- **Adquisición:** captura de variables ambientales (temperatura y humedad) y
    conversión análoga-digital para su lectura.
- **Procesamiento y Transmisión Local:** gestión de las mediciones y envío
    mediante protocolo inalámbrico de corto alcance (BLE) hacia el nodo central.
- **Procesamiento Global:** recepción, decodificación y coordinación de
    variables ambientales para su integración con puerta de enlace 5G.
- **Transmisión Global:** encapsulamiento y transporte de datos hacia la
    plataforma de almacenamiento de datos en la nube, a través de una red
    celular 5G.
- **Almacenamiento y Visualización:** almacenamiento de datos en la nube y
    despliegue de interfaz gráfica de usuario para monitoreo remoto.
- **Alimentación:** suministro y gestión energética para garantizar continuidad
    operacional y autonomía del nodo.

## Requerimientos del sistema

### Sensores

Se selecciona el sensor SHT31 para el nodo 5G debido a su compatibilidad y
eficiencia.
El SHT31 utiliza comunicación digital I2C, lo que permite una conexión directa tanto
con la ESP32 como con la Raspberry Pi 4, lo que reduce la complejidad del diseño,
el ruido en las mediciones y el consumo energético del sistema.
Este sensor específicamente presenta un consumo muy bajo, especialmente en modo
de reposo, lo cual es fundamental considerando que el nodo opera con energía


limitada proveniente de un sistema solar con batería. Esta característica permite
maximizar la autonomía del nodo y asegurar operación continua incluso en
condiciones de baja radiación solar.
Sin embargo, la razón más fuerte por la que se escoge este sensor es porque en el
contexto del crecimiento del oídio de la vid, es necesario tener un seguimiento preciso
de la humedad y temperatura, y este sensor ofrece muy buena precisión y estabilidad,
ya que tiene una exactitud de ±2% en humedad relativa y ±0.3 °C en temperatura.

### Comunicación

Uno de los objetivos del proyecto es implementar un sistema de comunicación
inalámbrica 5G. Para esto es necesario un módulo que sea capaz de conectarse a
antenas 5G NR (New Radio), que es el estándar global de quinta generación.

El sistema debe cumplir con los siguientes requerimientos técnicos de comunicación
del módulo:

- Debe soportar la banda de frecuencia n78 (3.5 GHz) para transmisiones de
    alta velocidad y baja latencia, y la banda n28 (700 MHz) para asegurar
    cobertura en interiores y zonas suburbanas.
- Debe ser compatible con el modo NSA (Non-Standalone), para asegurar una
    amplia cobertura y conectividad con la infraestructura actual de las antenas
    desplegadas en Chile, que aún depende del núcleo 4G. Debe ser compatible
    con el modo SA (Standalone) como proyección a futuro, debido a que la
    instalación de antenas que soportan SA está creciendo, lo que servirá para
    ventajas nativas del 5G y para el uso de tecnologías como 5G RedCap.
- El hardware debe contar con capacidad de _fallback_ automático hacia redes
    4G LTE y 3G, para garantizar la continuidad de la transmisión de datos en
    caso de pérdida de señal 5G debido a la geografía o movilidad del nodo.

### Cómputo

[agregaría cómputo para los sensores, lo que debe tener el microcontrolador]

Para el funcionamiento del sistema de comunicación 5G es necesario que el
procesamiento sea realizado por un dispositivo que tenga los controladores
necesarios para comunicarse con el módulo 5G de manera eficiente.

La unidad de procesamiento debe cumplir con lo siguiente:

- Sistema operativo basado en Linux. Permite la gestión sencilla de
    dispositivos de red y asegura disponibilidad de controladores nativos para
    protocolos industriales de comunicación como QMI o MBIM.
- Interfaz física USB 3.0 o superior. Permite que el flujo de datos desde los
    sensores y hacia la nube aproveche el potencial de ancho de banda del
    estándar 5G.


- Debe ser capaz de realizar el pre-procesamiento, encriptación (SSL/TLS) y
    empaquetamiento de datos (JSON/MQTT) localmente antes de la
    transmisión.

### Energía

Debido a que la energía solar no está disponible las 24 horas del día, es necesario
utilizar una batería que permita mantener la autonomía del nodo durante un mayor
período de tiempo. En este caso, se decidió dimensionar el sistema para mantener
una autonomía de dos días en caso de lluvias o días nublados. Si bien durante el
invierno los días lluviosos o nublados son más prolongados, según el académico
Vitiscience, no es necesario el monitoreo de condiciones durante este periodo
debido a la ausencia de plantaciones.

_Consumo estimado_

```
Tabla 1. Consumo nodo medición
Corriente Idle ESP32 15 uA [1]
Corriente BLE activo ESP32 80 mA [1]
Corriente Idle sensor 2 uA [2]
Corriente medición sensor 0.8 mA [2]
```
```
Tabla 2. Consumo Gateway o nodo central
Potencia Idle raspberryPi 4 (𝑃𝑖𝑑𝑙𝑒𝑅𝑃) 3.2W^ [^1 ]^
Potencia máxima raspberryPi 4 (𝑃𝑇𝑥𝑅𝑃) 7.8W^ [^1 ]^
Potencia Idle módulo 5G (𝑃𝑖𝑑𝑙𝑒^5 𝐺) 1.5*^
Potencia transmisión módulo 5G (𝑃𝑇𝑥^5 𝐺) 5*^
```
```
Tabla 3. Tiempos de transmisión
Tiempo de transmisión BLE (𝑡𝑇𝑥−𝐵𝐿𝐸) 0.1s [1]^
Intervalo de transmisión BLE (𝑡𝑖𝑛𝑡−𝐵𝐿𝐸) 2 s^
Tiempo de transmisión 5G (𝑡𝑇𝑥) 10 s^
Intervalo de transmisión (𝑡𝑖𝑛𝑡) 30 s^
```
*El datasheet del módulo 5G Teltonika no especifica el consumo de potencia del mismo, por lo que
para los cálculos y dimensionamiento preliminar del sistema de alimentación se utilizaron los valores
detallados para un gateway 5G de la misma empresa [4]. Al momento de montar el prototipo se
realizarán mediciones empíricas de consumo de potencia antes de gestionar las compras para el
sistema final del prototipo.

A partir de la información resumida en las tablas se tiene que el consumo promedio
del gateway es

```
𝑃𝑚𝑒𝑎𝑛 = (𝑃𝑖𝑑𝑙𝑒𝑅𝑃 + 𝑃𝑖𝑑𝑙𝑒^5 𝐺)⋅
```
#### 𝑡𝑖𝑛𝑡−𝑡𝑇𝑥

#### 𝑡𝑖𝑛𝑡

#### +(𝑃𝑇𝑥𝑅𝑃 + 𝑃𝑇𝑥^5 𝐺)⋅

#### 𝑡𝑇𝑥

#### 𝑡𝑖𝑛𝑡


#### 𝑃𝑚𝑒𝑎𝑛 = 6 𝑊

Para mantener el funcionamiento durante las 48 horas planteadas, la energía total
generada debe ser

```
𝐸𝑡𝑜𝑡𝑎𝑙 = 𝑃𝑚𝑒𝑎𝑛⋅ 48 𝐻𝑟𝑠 = 288 𝑊𝐻𝑟𝑎
```
Considerando que la luz solar efectiva en un día dura en promedio 5 horas [5], la
potencia del panel necesaria para generar la energía total requerida es de

```
𝑃𝑝𝑎𝑛𝑒𝑙 =
```
#### 𝐸𝑡𝑜𝑡𝑎𝑙

#### 5 𝐻𝑟𝑠

#### = 60 𝑊

Se decide utilizar el tipo de batería LiFePo4 debido a su mayor estabilidad de
voltaje, mayores ciclos de carga, mejor resistencia a altas temperaturas y mayor
profundidad de descarga. Este último parámetro es del 80% para el tipo de batería
seleccionado, por lo que esta debe ser capaz de almacenar 1. 25 ⋅𝐸𝑡𝑜𝑡𝑎𝑙.

Considerando una batería estándar de 12V, esta debe tener una capacidad de

```
𝐶 =
```
#### 1. 25 ⋅𝐸𝑡𝑜𝑡𝑎𝑙

#### 𝑉𝑜𝑙𝑡𝑎𝑗𝑒

#### = 30 𝐴𝑚𝑝⋅𝐻𝑟𝑎

Por otro lado, el consumo del sistema de adquisición de datos, considerando una
alimentación de 3.3V es de 0.15W (se utilizan la misma ecuación que para 𝑃𝑚𝑒𝑎𝑛 del
gateway).

- Si este sistema es conectado al mismo sistema de alimentación solar para
    fines de prototipado, no induce cambios significativos en los requerimientos
    del mismo.
- Para implementación práctica, sería necesaria una batería propia, sin
    embargo, se utilizaría protocolo LoRa y chips Nordic para minimizar el
    consumo y utilizar una única batería por añosl, en lugar de incorporar más
    sistemas solares a la red.

_Requerimientos de corriente mínima_

Según [6], un módem 5G puede consumir hasta 0.3A durante la transmisión de
datos, por lo que tanto el regulador de carga, la batería y el conversor buck deben
ser capaces de suministrar al menos 0.5A (con margen de seguridad).

## Propuesta de componentes y presupuesto

El siguiente enlace dirige al presupuesto y menciona los componentes que
utilizaremos: E6_presupuestos.xlsx

## Bibliografía


[1] Gkagkas, G., Karamerou, V., Michalas, A., Dossis, M., & Vergados, D. J. (2025).

```
The Behavior of an IoT Sensor Monitoring System Using a 5G Network and
```
```
Its Challenges in 6G Networking. Electronics, 14(16), 3167.
```
```
https://doi.org/10.3390/electronics
```
[2] Sensirion. (2026). Datasheet SHT3x-DIS: Humidity and Temperature Sensor

```
[Ficha técnica]. link
```
[3] Sergio. (2020, 27 abril). Mi análisis de la Raspberry Pi 4 » Raspberry para

```
novatos. Raspberry para novatos.
```
```
https://raspberryparanovatos.com/articulos/mi-analisis-de-la-raspberry-pi-
```
```
4/#consume_mas_energia
```
[4] Teltonika Networks. (s.f.). _TRB501 Industrial 5G Gateway_. https://www.teltonika-

```
networks.com/es/products/gateways/trb
```
[5] Enerlife. (s.f.). _¿Cuántas horas de sol necesita un panel solar para ser eficiente?_.

```
https://enerlife.cl/cuantas-horas-de-sol-necesita-un-panel-solar-para-ser-
```
```
eficiente/
```
[6] Samsung Electronics. (2019). _4G-5G Interworking: Key Technologies for Smooth_

```
5G Evolution [White paper].
```
```
https://images.samsung.com/is/content/samsung/p5/global/business/networks
```
```
/insights/white-paper/4g-5g-interworking/global-networks-insight-4g-5g-
```
```
interworking-0.pdf
```

