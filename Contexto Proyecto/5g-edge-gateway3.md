Academic Editor: Christos J. Bouras
Received: 22 June 2025
Revised: 4 August 2025
Accepted: 6 August 2025
Published: 8 August 2025
**Citation:** Gkagkas, G.; Karamerou, V.;
Michalas, A.; Dossis, M.; Vergados, D.J.
The Behavior of an IoT Sensor
Monitoring System Using a 5G
Network and Its Challenges in 6G
Networking.Electronics **2025** , 14 , 3167.
https://doi.org/10.3390/
electronics
**Copyright:** © 2025 by the authors.
Licensee MDPI, Basel, Switzerland.
This article is an open access article
distributed under the terms and
conditions of the Creative Commons
Attribution (CC BY) license
(https://creativecommons.org/
licenses/by/4.0/).

Article

# The Behavior of an IoT Sensor Monitoring System Using a 5G

# Network and Its Challenges in 6G Networking

```
Georgios Gkagkas1,*, Vasiliki Karamerou^2 , Angelos Michalas^3 , Michael Dossis^1
and Dimitrios J. Vergados^1
```
(^1) Department of Informatics, University of Western Macedonia, 52100 Kastoria, Greece;
mdossis@uowm.gr (M.D.); dvergados@uowm.gr (D.J.V.)
(^2) Department of Computer Science and Biomedical Informatics, University of Thessaly, 35100 Lamia, Greece;
vkaramerou@uth.gr
(^3) Department of Electrical and Computer Engineering, University of Western Macedonia, 50100 Kozani, Greece;
amichalas@uowm.gr
***** Correspondence: g.gkagkas@uowm.gr
**Abstract**
The recent advances in 5G and beyond wireless networking have enabled the possibility
of using the cellular network as the infrastructure for wireless sensor networks, due to
the high bandwidth availability and the reduced cost per data unit. In this paper, we
perform an evaluation of the 5G infrastructure for sensor networks in order to quantify the
performance in terms of energy efficiency and bandwidth within a testing environment. We
used an ESP32 sensor with BLE-connected sensing devices for environmental conditions,
and a Raspberry Pi with the Waveshare SIM8200EA-M2 5G module for cellular connectivity.
We measured the power usage of each component of the system, in real conditions, as well
as the power consumption for different bandwidth usage scenarios, and the end-to-end
delay of the system. The results showed that the system is capable of achieving the required
delay and bandwidth; however, the energy efficiency of the specific setup leaves room
for improvement.
**Keywords:** Internet of Things (IoT); 5G networks; Bluetooth Low Energy (BLE); sensor
monitoring; ESP32; Raspberry Pi; real-time data processing; data visualization

## 1. Introduction

```
Internet of Things (IoT) networks have been transforming the cyber-physical landscape
during the past few years as they enable the interconnection of physical devices, such as
sensors, machines, appliances, vehicles, etc., to the internet, allowing these objects to
collect, exchange, and act on data [ 1 ]. The key features of IoT networks is that they
allow a multitude of new features on physical devices, including (a) automation and
intelligent decision making [ 2 ], (b) real-time monitoring and control [ 3 ], (c) efficiency and
cost reduction [ 2 ], (d) smart cities and infrastructure [ 4 ], (e) healthcare transformation [ 5 ],
(f) industrial IoT [ 5 ], (g) environmental monitoring and sustainability [ 4 ], and (h) security
and safety enhancements [5–7]
The traditional architecture for interconnecting IoT systems usually utilizes the existing
network infrastructure (e.g., Wi-Fi or Ethernet), or alternatively relies on a dedicated
wireless network [ 8 ], such as ZigBee [ 9 ], Bluetooth Low Energy (BLE) [ 10 ], z-Wave [ 11 ],
LoRaWAN [ 12 , 13 ], and many others. These technologies have the advantage of relying on
unlicensed radio frequencies, and therefore can be used without a subscription for each
```
Electronics **2025** , 14 , 3167 https://doi.org/10.3390/electronics


device. Additionally, the dedicated wireless networks have been designed specifically for
IoT applications, and have benefits in terms of energy efficiency compared with Wi-Fi. On
the other hand, they require a gateway to facilitate the communication between the wireless
network and the rest of the infrastructure, thus having increased installation complexity
compared with Wi-Fi devices.
At the same time, as the cost of cellular networks keeps decreasing, and the band-
width keeps increasing, the 5G and beyond network seems an increasingly attractive
alternative [ 14 – 16 ]. The advantages of the 5G network include (a) high data rates and
bandwidth [ 17 ], which may be orders of magnitudes larger than some other technologies,
(b) ultra-low latency [ 18 ], which can be as low as 1 ms, (c) massive scalability [ 17 ], allowing
for the system to increase the number of sensors without costly infrastructure updates,
(d) mobility support [ 19 ], since the networks are inherently mobile, (e) network slicing and
QoS [ 20 ], allowing for multiple operators and/or applications to share the same infrastruc-
ture, (f) Integrated Edge Computing [ 21 , 22 ], allowing for computation very near to the
source of the data streams, and g) enhanced security and reliability [23].
This paper focuses on exploring the suitability of the 5G network for an environmental
monitoring system, using off-the-shelf equipment and technologies. The implementation
and deployment consists of an IoT sensor monitoring system that includes hardware parts
such as ESP32 [ 24 ] and Raspberry Pi [ 25 ] using Bluetooth Low Energy (BLE) [ 26 ] and
wireless networks for real-time transformation of real-time data. All of the above is imple-
mented by optimizing data processing at the edge, ensuring reliable cloud connectivity for
scalability and efficiency, and reducing any network congestion.
The motivation for this research stems from the need to leverage 5G networking
technology to enhance IoT sensor monitoring systems; thus, the implementation of a system
that utilizes 5G to achieve real-time data collection and monitoring, overcoming limitations
of traditional sensor network deployments, is investigated. By focusing on optimizing
data processing at the edge, ensuring reliable cloud connectivity, and reducing network
congestion, this research aims to provide a valuable contribution to the development of
next-generation IoT-based wireless communication systems [27,28].
The research problem is the following: what is the energy efficiency and latency of
an IoT system that relies on 5G networking instead of traditional architectures? In order
to answer this question, we have designed and implemented a sensing architecture that
consists of an ESP32 microcontroller, with a sensor, a Raspberry Pi, and a 5G module. This
sensing node is connected to the ThingSpeak cloud platform in order to visualize the data
in real time.
The results show that the power consumption of the ESP32 monitoring system and
the sensors is very satisfactory; however, the introduction of the Raspberry Pi and the
associated 5G module drastically increases the power consumption of the setup. Therefore,
dedicated ESP32 5G modules are necessary to limit power consumption to a value that
would allow practical autonomous operation.
The contributions of this paper are the following:

- It leverages 5G technology to improve real-time data collection and in parallel moni-
    toring within the IoT sensor systems.
- It addresses the limitations of traditional sensor networking like bandwidth, latency,
    and networking congestion.
- It emphasizes edge computing in order to optimize local data processing be-
    fore transmission.
- It ensures the reliability of cloud connectivity for scalable and efficient systemperformance.
- It aims to advance the next-generation of IoT systems, contributing to the evolution of
    wireless communication technologies.


Some related papers have been identified from the literature. Specifically, [ 29 ] in-
vestigates energy savings in hydraulic press systems, reducing electrical consumption by
replacing traditional Direct-On-Line (DOL) starters with VSD-controlled motors. This is an
IIoT system allowing efficient remote data collection and analysis and in parallel reducing
audit time and cost. In addition, [ 30 ] explores parallel deep reinforcement learning (DRL)
methodology for 5G network resource allocation in order to achieve spectrum efficiency
and latency. With the use of multiple DRL agents, there is an improvement in convergence
speed and scalability. Paper [ 31 ] proposes an enhancement of IoT devices security by prior-
itizing 18 critical security features, ending up with a security priorities list that helps the
researchers to focus on the most impactful features for securing an IoT system. Finally, [ 32 ]
focuses on an Over-the-Air Computation with multiple shared wireless channels of an
industrial environment. There are a large number of sensors continuously sending data-
related information in order to monitor, power control, and detect any faults, leading to the
improvement of data aggregation in industrial Internet of Things (IIoT) environments.
The paper is organized as follows: Section 2 presents the system architecture that was
experimentally studied in this paper, Section 3 presents the methodology and results of
each of the experiments carried out for this study, Section 4 discusses the findings and
suggests future work, and finally Section 5 contains some concluding remarks.

## 2. System Architecture

The system under consideration is a system designed to automatically collect, transfer,
and visualize data over a 5G network. The purpose of the measurements is to monitor the
atmospheric conditions of a secluded area. It is implemented in the following layers: the
measurement layer, the data collection layer, and the data storage and visualization layer
(Figure 1).
The solution for implementing our experiment was guided by three factors: cost
efficiency, development flexibility, and modularity. ESP32 is a very powerful microcon-
troller with native BLE support and ultra-low power consumption, making it ideal for our
experiment. On the other hand, Raspberry Pi is a Linux environment ideal for easy code
development, debugging, integration, and updates with cloud services. All the above are
factors that provide easy system maintenance and scalability, although these components
are not ideal for power-critical environments, which is the novelty of our experiment.

**Figure 1.** The system architecture block diagram.

The measurement and data collection layers are deployed to a remote location. This
part of the whole system consists of two primary components: an ESP32 microcontroller
with a connected sensor, and a Raspberry Pi acting as a Bluetooth Low Energy (BLE) server.
These components communicate using Bluetooth Low Energy (BLE), which is a power-
efficient wireless communication protocol widely used for IoT (Internet ofThings) devices.


The measurement layer is the device acting on the field to conduct the measurements,
organize the measured values, and transmit them. The main device of this layer is an ESP
connected with the needed sensors (Figure 2). It is a versatile microcontroller with built-in
BLE capabilities, making it ideal for use in IoT applications where low-power wireless
communication is essential. In the system, the ESP32 is connected to a sensor that gathers
data (for example, temperature, humidity, or motion) (Figure 3). The ESP32 is configured
to act as a BLE client, which means that it initiates communication with the BLE server
(Raspberry Pi) to send the sensor data.

**Figure 2.** ESP32 development board.

**Figure 3.** DHT11 temperature and humidity sensor.

Data collected from sensors during a specified interval are structured into a single
string for transmission to the next processing layer. Each sensor reading is prefixed with a
distinctive letter or phrase to indicate the type of measurement. For instance, if the system
captures temperature and humidity values, the resulting string could be organized as
T34H46, where T represents temperature and H represents humidity, followed by their
respective values. The data collection layer is subsequently responsible for decoding this
string format, ensuring accurate interpretation of the sensor readings.
The Raspberry Pi (Figure 4) serves as a server in the data collection layer, decoding the
data string after receiving it from the ESP32. As a BLE server, the Raspberry Pi broadcasts
its location and awaits connections from BLE clients, like the ESP32. In this configuration,
the ESP32 communicates with one or more Generic Attribute Profile (GATT) [ 33 ] services
hosted by the Raspberry Pi. The structure of the data being transferred is specified by
these GATT services. After waiting for the ESP32 to establish a connection, the Raspberry
Pi takes in incoming data. After connecting, the ESP32 can transmit sensor data as BLE
characteristics, which can then be processed further for real-time applications, such as data
storage, or stored locally on the Raspberry Pi.


**Figure 4.** Raspberry Pi 4.

Communication between the measurement layer and the data collection layer is
facilitated via the BLE protocol. The BLE protocol used for communication is specifically
designed for low-power, short-range applications. It is ideal for devices like the ESP32 that
are often battery-powered and need to transmit small amounts of data intermittently. The
BLE connection is initiated by the ESP32 (the client), which scans for the Raspberry Pi’s BLE
advertisement (the server). Once connected, the ESP32 reads or writes BLE characteristics
as defined by the GATT services on the Raspberry Pi.
BLE’s advantage is its energy efficiency. Devices remain in low-power modes most of
the time and only wake up to transmit small bursts of data, such as sensor readings. This is
crucial for IoT systems, where power consumption needs to be minimized.
The ThingSpeak platform, which provides cloud-based management of real-time
sensor data sent from the Raspberry Pi over a 5G network, acts as the system’s data storage
and visualization layer. The platform enables the system to safely store environmental data,
including temperature and humidity, and display them in real time through dashboards that
can be customized. ThingSpeak allows users to track trends and patterns over time by time-
stamped each incoming sensor reading. This is particularly helpful for monitoring isolated
or remote locations. By facilitating sophisticated data analysis and predictive modeling,
its integration with MATLAB (https://www.mathworks.com/products/thingspeak.html
(accessed on 5 August 2025)) improves the platform even more and provides insights
beyond simple monitoring. However, ThingSpeak does come with limitations, particularly
in terms of data transfer and processing capabilities. The free version of ThingSpeak
restricts the rate of data updates, with only one data point allowed every 15 s, and limits
the total number of data points that can be stored. This could pose a challenge for systems
that require high-frequency data transmission or real-time responsiveness in fast-changing
environments. Additionally, the platform’s free tier limits the amount of data that can be
processed simultaneously, which may require the use of paid subscriptions for larger-scale
applications or more frequent data transfers. Due to these limitations, ThingSpeak is not
ideal for immediate-response requirements or high-volume data collection, but it is still an
excellent solution for low-to-moderate data throughput in a variety of IoT projects.
There are limitations on the data packet size that ThingSpeak can send to its cloud
platform. Each packet constitutes an API call and can send up to eight fields of data with
a maximum size of 255 bytes for each field. It comprises the data recorded by the sensor
and its accompanying metadata or timestamps. This packet size is usually enough for
small-scale IoT tasks that only manage small sensor readings such as temperature, humidity,
or motion, but can get limiting when it comes to more complex or high-resolution data.
A 5G cellular network is utilized in this system to facilitate rapid and reliable trans-
mission of sensor data from peripheral locations into the cloud. To achieve the above,
a Waveshare SIM8200EA-M2 5G module is integrated on the Raspberry Pi to give it the
capability to connect to the internet through the high-speed 5G cellular network. The


Raspberry Pi interacts with the modem through a USB interface. This 5G module acts as a
modem connecting the Raspberry Pi to the cellular network, giving the device constant
wireless real-time data transfer ability.The 5G network’s low latency and high bandwidth
make it ideal for all the needed IoT data transmission, in our case for constant remote
monitoring of environmental conditions.
The 5G SIM8200EA-M2 module easily interfaces with the Raspberry Pi for seamless
integration, and uploads sensor data from the ThingSpeak cloud via USB 3.0. It offers
both 5G NSA (non-standalone) and SA (stand-alone) architecture support, allowing it to
function over a wide range of network coverage. If a 5G network is unavailable, the module
will switch to LTE or 3G, which maintains a constant connection. This feature is important
for IoT systems that deploy remote environments with unpredictable network coverage
issues (Figure 5).

**Figure 5.** The 5G module used in the experiments.

As network coverage, 5G technology is ideal for IoT applications that need reliable
and high-speed internet access connectivity in order to send sensor information from hard-
to-reach areas. The substantial bandwidth provided by the 5G network ensures that the 5G
link will not be the bottleneck for the transmission of our system’s data. Specifically, in our
system we transmit up to 255 bytes per packet, with each packet transmitted every 15 s.
This makes the 5G-enabled Raspberry Pi configuration a versatile and dependable option
for IoT applications that need sustained data transfer in remote locations.

2.1. Equipment Used and Specifications

The methodology behind designing the experiment is based on the following prin-
ciples for the selection of the sensors: they should be low-cost, low-power, and widely
supported sensors. The selection of the communication protocol is based on energy ef-
ficiency, and therefore BLE was selected and not ZigBee, which is best used on mesh
networking rather than point-to-point communications. More specifically, the sensors were
chosen for their simplicity, low power usage, and sufficient accuracy for basic environmen-
tal monitoring. The chosen communication protocol (BLE) was selected for its short-range
and energy-efficient communication between the ESP32 and Raspberry Pi. The Raspberry
Pi supports reliable cloud connectivity with the support of BLE and the 5G network, which
offers high bandwidth with low latency, ideal for IoT systems. The data transmission of a
10 s timeframe using an encoded string of T34H46 (temperature and humidity) ensured
real-time updates based on ThingSpeak limitations and in parallel we minimized the energy
use. Power consumption was measured using a USB power meter and iperf3 based on


realistic load scenarios with solar panel testing for feasibility for sustainability. The MQTT
protocol was chosen as a future upgrade for better scalability and network flexibility.
Tables 1 and 2 demonstrate the essential hardware chosen for the gateway and sensing
stack. For each item, they summarize key specifications, such as the processor type and
speed, memory, I/O ports, wireless and wired connectivity, power requirements, and,
where applicable, peak data-rate figures.

**Table 1.** Raspberry Pi system specifications.

```
Feature Specification
Processor Broadcom BCM2711, Quad-Core Cortex-A72 (ARM v8) @ 1.5 GHz
RAM 4 GB LPDDR4-3200 SDRAM
Storage MicroSD card slot (supports high-speed SD cards)
USB Ports 2 ×USB 3.0, 2×USB 2.
Video Output 2 ×Micro HDMI (supports 4K resolution)
Networking Gigabit Ethernet (1 Gbps), Wi-Fi 5 (802.11ac), Bluetooth 5.
GPIO 40-pin header for hardware interfacing
Power Supply USB-C, Power consumption: 2.8–7.6 W
Operating System Raspberry Pi OS, Ubuntu, Debian, other ARM-based OS
```
**Table 2.** 5G module specifications.

```
Feature Specification
Supported Networks 5G (sub-6 GHz), 4G LTE, 3G HSPA+
Maximum Speeds 5G: 2.5 Gbps DL, 900 Mbps UL4G LTE: 1 Gbps DL
Interfaces USB 3.1, PCIe (some models), UART, GPIO
SIM Card Slot Nano SIM (eSIM support on some models)
Antenna External 4× 5G antennas required
```
2.2. Communication Protocols

Protocols such as ZigBee and Bluetooth Low Energy (BLE) are used in IoT applications,
with all of them serving as wireless communication protocols with specific differences
in data bandwidth, power consumption, and accuracy [ 34 ]. In terms of power saving,
BLE is an improved optimized protocol for low-power consumption, making it ideal
for devices that operate with batteries and need to send small numbers of data such as
sensor readings. ZigBee, which is another energy-efficient protocol functioning as a mesh
networking protocol, allowing multiple devices to be connected over long distances with
moderate pacing but consumes more power over large periods of time compared with BLE.
Regarding data transmission rates, BLE performs communication rates of up to 1 Mbps,
ideal for most of IoT applications, and ZigBee has lower rates of up to 150 kbps but with
excellent range and network scalability. In terms of fidelity, BLE is the one that provides
value in short-range communications with low error rates especially in point-to-point
communications, like ESP32 and Raspberry Pi.
Bluetooth Low Energy (BLE) is currently the best protocol for simple low-power point-
to-point communications, like ESP32 and a Raspberry Pi, although it has limited scalability.
ZigBee and Thread are both used for large-scale IoT security advanced-complex mesh
connections. Wi-Fi Direct is a protocol that offers high data throughput like media sharing,
making it a not-ideal protocol for us to use due to its power consumption requirements
and less attractive for sensor-based IoT systems communications.
Comparing the most popular communication protocols that are used in IoT applica-
tions, we can say the following:


- LoRaWAN is the most energy efficient for long-range protocol, low-frequency com-
    munication, ideal for remote environmental monitoring, and has a long battery life.
- BLE is ideal for short-range communications with high-frequency, and has ultra-low
    power consumption requirements.
- ZigBee provides a good balance between range and power, but with higher en-
    ergy costs.
    Table 3 summarizes the key differences between these protocols.

**Table 3.** Comparison of communication protocols.

```
Feature BLE (BluetoothLow Energy) ZigBee LoRaWAN
```
```
Power
Consumption
```
```
Very low, used on
ultra-low-power
applications.
```
```
Low, but higher
than BLE.
```
```
Extremely low
consumption.
```
```
Sleep Mode
Efficiency
```
```
Excellent, devices
can sleep for long
periods.
```
```
Good, it supports
sleep modes.
```
```
Outstanding,
devices can stay
asleep most of the
time.
```
```
Battery Life
```
```
1+ year (coin-cell
battery, depending
on use).
```
```
Up to 2 years in
low-traffic
applications.
```
```
5–10 years on a
single AA battery.
```
```
Optimal Use Case Short-range (e.g.,wearables).
```
```
Medium-range
networks (e.g.,
home automation).
```
```
Long-range, (e.g.,
remote sensors).
```
The power source of the ESP32 in IoT is batteries. This greatly benefits from BLE’s
low-energy power consumption, which enables longer operational periods without the
frequent need for recharge. In addition to this, the 1 Mbps data rate for BLE is more than
enough for compact data strings from the sensors (e.g., temperature, humidity readings),
while the point-to-point architecture allows communication with the Raspberry Pi and
ESP32 without the overhead from a ZigBee mesh network; a reason that makes it ideal for
remote monitoring systems that require low power communication.

2.3. Cloud Platform

On the data storage and visualization layer, the ThingSpeak platform is used. ThingS-
peak is an open-source IoT platform designed to allow users to collect in real time, analyze,
store, and visualize data from different devices, sensors, or applications. This platform
is popular among developers as it allows monitoring and controlling remote IoT devices.
Based on specific data conditions, users can set triggers in order to send notifications. The
platform is quite popular due to its flexibility, ease of use, support of a wide range of
communication protocols, such as HTTP and MQTT, and more, making it a good choice for
smart devices, environmental monitoring, and home automation projects.
A user may connect to ThingSpeak using a Mathworks account (Figure 6), which can
be created on the website. After signing in, the user needs to create a channel, which is a
fundamental unit that allows storage and management of data from various IoT devices.
Each channel can store up to eight data fields for information readings (e.g., temperature,
humidity, etc.) and can be public or private. The novelty of the ThingSpeak platform is that,
apart from real-time visualization with graphs, data processing using MATLAB (R2014b
and above) is also possible on the cloud.


**Figure 6.** Mathworks sign-in page.

First, the user should provide a name for the new channel and then create the nec-
essary data fields according to the application needs. Each data field must be given an
individual/unique name. After that, the user saves the created channel. The user can
click on the channel name to go to the channel management view. An API key for this
channel can be created there. This API key is then used to send data to the channel using a
different device. The Write API Key in ThingSpeak is a unique key assigned to each of the
channels that allows the user to send or update data to a specific channel. It functions as an
authentication token, making sure that only authorized users or devices can upload data to
that specific channel. The key is essential in preventing unauthorized access and ensuring
the protection of the data that are being sent (Figure 7).

**Figure 7.** Write API key for the channel.

Figures 8 and 9 depict some sample graphs from the platform. Specifically, we see
how the temperature and humidity readings from the sensor are depicted over time.


**Figure 8.** Temperature visualization over half an hour.

**Figure 9.** Humidity data visualization over half hour.

Although ThingSpeak is suitable for the experiments in this paper, in general it
has some limitations regarding data throughput and scalability issues that make it un-
suitable for large-scale systems that need multiple connections with high data rates.
More specifically:

- There is a limitation of one data point every 15 s, which limits the monitoring above
    that data frame and could also lead to data loss.
- In terms of big data storage, ThingSpeak is not ideal, so users will need to export any
    important data frequently and store them in an external file server in order not to lose
    any critical data.
- There could be data gaps during connection loss.
- There is limitation of 255 bytes per data packet.


As part of future work on this issue, there are alternatives that could be used such as
Google Cloud IoT, which supports large data streams, and Azure IoT Hub, which supports
MQTT for large streams.

## 3. Experiments

All of the system’s components were tested in a number of scenarios through a series
of experiments. To determine the baseline demand of the sensing layer, we begin with
an ESP32 duty-cycle test that separates the active-transmit and deep-sleep currents of the
microcontroller. The heavier gateway, a Raspberry Pi 4 with a 5G modem, is covered in
Section 3.3. The test measures both peak and steady-state requirements by profiling their
joint draw during boot, idle, and full-throughput uplink. Lastly, end-to-end round-trip
times are recorded by the 5G delay experiment.
With the focus on our IoT system’s power consumption, there was a series of opera-
tional tests designed and performed in order to evaluate the energy requirements of ESP
node, the Raspberry Pi, and the 5G cellular module. The main goal is to identify the energy
usage of different scenarios and data transmission rates and determine if the needed power
requirements could be fulfilled with sustainable power sources such as solar panels in order
to be able to provide the needed functional power to the system for long-term deployment
in remote environments. Finally, the methodology, setup, and results are analyzed.

3.1. ESP32 Power Consumption

In this subsection, we focus on measuring how much energy the ESP32 microcontroller
consumes in a typical operation including active and idle (sleep) states. Our goal is to
estimate the daily energy consumption (24 h cycle) and how long the system can operate
autonomously while connected to a standard power bank, which is a critical measurement
for sustainable IoT deployment.

Methodology and Results

The oscilloscope measures from each phase are presented in Table 4. Based on these
measurements, we can calculate the energy consumption of the ESP32 [35] over a day.

**Table 4.** ESP32 current consumption.

```
Feature Value
Active BLE current 80 mA
Idle/sleep current 15 μA
Idle with DHT11 sensor current 250 μA
Transmission time 0.1 s per transmission
Transmission interval Every 10 s
```
Firstly, we have to determine the active time per day. The ESP32 is active for 0.1 s
every 10 s, leading to 8640 active transmissions per day (since there are 86,400 s in a day).
Now, calculating the energy use for a day.

- Active energy for BLE:

```
Ea=80 mA×
```
### 0.

### 3600

```
h× 8640 =19.2 mAh/d (1)
```
- Idle/sleep energy:

```
Ei=0.01 mA×
```
### 86391.

```
3600 h=0.24 mAh/d (2)
```

- DHT11 sensor energy:

```
Es=0.25 mA× 0.
3600
h× 8640 =0.06 mAh/d (3)
```
```
So finally, the total energy use over a day is:
```
E=Ea+Ei+Es=19.2 mAh/d+0.24 mAh/d+0.06 mAh/d (4)
E=19.5 mAh/d (5)
In order to get a feeling of the viability of the ESP32 remote node, used as an IoT
device, we can construct a hypothesis. For example, we have a 10,000 mAh power bank
available to be used as a power supply for the ESP32 with the sensor. This type of power
supply is pretty common, cheap, and easy to use. Knowing that the ESP32 with the sensors
can operate with a consumption of 19.5 mAh per day, we can estimate how long the setup
will last by dividing the capacity of the power bank by the daily consumption.

```
10000 mAh
19.5 mAh/d
=512.82 d (6)
```
3.2. Photovoltaic Power Measurements

The goal of this experiment was to verify that a miniature photovoltaic (PV) panel can
replenish the energy the sensing node consumes each day. The procedure followed four
analytical steps drawn directly from the design notes in the document:

1. Translate the daily current budget into energy.
    The battery must recover the 30 mAh that the node is expected to draw every 24 h.
    Converting to watt-hours:

```
Energy(Wh) =Capacity(Ah)×Voltage(V) (7)
30 mAh=0.030 Ah (8)
0.030 Ah×5 V=0.15 Wh (9)
```
2. Convert the energy target into a required panel power rating.
    Assuming an average of 4 h of effective sunshine per day (Athens climate), the mean
    electrical power that must reach the battery is

```
Power(W) =
Energy Wh
Sunlight hours(h)
```
### (10)

### =

```
0.15 Wh
4 h
```
### =0.0375 W (11)

3. Derate for charging and weather losses.
    To cover charger inefficiency, temperature effects, and cloudy days, we apply a 0.
    system-efficiency factor, giving a name-plate power

```
Require Power=
```
### 0.0375 W

### 0.

### =0.05 W (12)

4. Translate the power rating into physical size.


```
With peak irradianceG=1000 W/m^2 and 18% efficient monocrystalline cell, the
active area required is
```
```
Area(m^2 ) =
Power(W)
Efficiency×Solar Irradiance(W/m^2 )
```
### (13)

### = 0.05 W

```
0.18×1000 W/m^2
```
### =0.

### 180

```
m^2 =0.000278 m^2 (14)
```
```
So a solar panel of 30 cm^2 will be enough to sustain the system’s needs [36].
```
3.3. Raspberry Pi and 5G Module Power Consumption
Even though the ESP32 microcontroller has low power consumption characteristics,
making it ideal for battery-powered devices, the gateway, which is a Raspberry Pi 4, and
the 5G cellular module have different power profiles. Within this subsection we explore
the gateway’s needed energy demands under different operating conditions, such as with
“active”, “idle”, and “full-load” scenarios. By taking real-time power consumption mea-
surements under different bandwidth consumption levels, we aim to highlight the power
costs for remote or off-grid deployments where energy consumption is a critical factor.

```
3.3.1. Methodology
Power draw was measured with an inline USB-C power meter placed between the
5 V/3 A supply and the Raspberry Pi 4 B. This meter logs real-time voltage and current,
making it suitable for the watt-level loads of the gateway, where a milliohm shunt plus
oscilloscope would have been cumbersome. Two test suites were run:
```
1. Standalone Pi—the board was allowed to reach a steady idle desktop and then stressed
    with stress-ng on all four cores for 60 s to capture “Load” watts.
2. Pi + Waveshare SIM8200EA-M2 5G modem—three operating points were profiled:
    - Idle (modem attached but no traffic);
    - Active use (two CPU cores stressed while downloading a 1 GB file over 5G);
    - Load (three CPU cores stressed while simultaneously downloading and upload-
       ing the file).
A second pass repeated the Active-use and Load scenarios while throttling iperf3 [ 37 ]
traffic to 100 Mbps, 500 Mbps, and 1 Gbps, revealing how modem demand scales
with throughput.

```
3.3.2. Results
The 5G module measurements observed are outlined in Table 5.
```
```
Table 5. 5G module measurements.
```
```
Model Idle Power (W) Load Power (W)
Raspberry Pi 4B (4 GB) 2.8–3.4 W 5.6–7.8 W
```
```
The idle power consumption represents the state in which the raspberry is just up and
running. To measure the power consumption under heavy work load, we run a CPU stress
test. To simulate the full CPU usage, we used the stress-ng tool. The test we run uses all
4 CPU cores and performs matrix multiplication for 60 s (Tables 6 and 7).
```

**Table 6.** Raspberry pi with Waveshare SIM8200EA-M2 5G module power consumption.

```
Setup Idle Power (W) Active Use Power (W) Load Power (W)
Raspberry Pi +
5G Module 4.3–6.4 W 9.5–14.6 W 14–19 W
```
**Table 7.** Raspberry pi with Waveshare SIM8200EA-M2 5G module power consumption.

```
Bandwidth Active Use Power (W) Load Power (W)
100 Mbps 9.5 14.
500 Mbps 12.0 16.
1 Gbps 14.6 19.
```
3.4. 5G Delay Experiments

Apart from the energy optimization, latency is another crucial factor for IoT systems
within real-time monitoring scenarios. This subsection analyses the end-to-end commu-
nication delays within the 5G network under different data sizes and link conditions. All
the tests were performed using different payloads and bandwidth constraints, which can
impact transmission latency. This is critical information for determining the responsiveness
and reliability of a 5G-based IoT system.

3.4.1. Methodology

To understand how the 5G back-haul affects end-to-end responsiveness, we placed
the Raspberry Pi 4 B + SIM8200EA-M2 gateway on a public 5G network and used iperf
to upload payloads of increasing size (1 KB→100 MB) to a cloud server. Three link-rates
were imposed to emulate typical field conditions (Figure 10):

- 100 Mbs—fringe or throttled coverage.
- 500 Mbs—average urban cell.
- 1 Gbs—near-peak sub-6 GHz performance.

Figure 10 illustrates two usage scenarios, where the x-axis (logarithmic scale) repre-
sents the bandwidth in Mbps and the y-axis shows power consumption in Watts. The active
usage related to power consumption and bandwidth is represented by the yellow line, and
the channel load related to power consumption and bandwidth is represented by the red
line. The power consumption increases with the bandwidth in both scenarios. These two
scenarios are quite critical when we are dealing with energy-battery consumption. When
dealing with low data rates, the system can be power balanced, while high rates require
higher power supply capacity.

3.4.2. Results

The measurements confirm the qualitative finding recorded in the design notes: “Data
size increased. Total delay followed a nonlinear trend, particularly at lower network speeds
where the transmission time became dominant factor”.
In practical terms:

- Small telemetry packets (<10 kB) incur only the 35–40 ms network round trip and can
    be pushed at the full ThingSpeak rate limit without perceptible lag.
- Moderate uploads (1–10 MB) remain sub-second on links >500 Mbps but stretch into
    the 1–10 s range if the cell throttles to 100 Mbps.
- Bulk transfers (100 MB) are viable only when the link holds at several hundred Mbps;
    otherwise the gateway is occupied for many seconds and the modem climbs into its
    14–19 W power envelope (see Section 3.3).


## 102 103

```
Bandwidth (Mbps)
```
## 10

## 12

## 14

## 16

## 18

```
Power Consumption (W)
```
```
Power Consumption vs. Bandwidth
```
```
Usage Scenario
Active Use
Load
```
**Figure 10.** Throughput mattered: at 100 Mbps the gateway held to9.5 W (Active)/14 W (Load); ̃
raising the link to 500 Mbps pushed those figures to 12 W/16.2 W; and saturating a near-gigabit
channel drove consumption to 14.6 W/19.1 W. In other words, every 400 Mbps increment costs
roughly 2–2.5 W of extra power.

Accordingly, the deployment plan schedules high-volume firmware or data dumps
during strong signal periods and leaves the regular sensor feed well below 1 MB per
transaction, ensuring end-to-end delays of <50 ms under normal conditions while keeping
energy consumption in check (Figure 11).

### 10 −3 10 −2 10 −1 100 101 102

```
Data Size (MB)
```
### 100

### 101

### 102

### 103

### 104

```
Total Delay (ms)
```
```
5G Waveshare Transmission Delay vs Data Size
Network Speed
100 Mbps
500 Mbps
1000 Mbps
```
**Figure 11.** 5G transmission delay vs. data size.


3.5. Use Cases

Based on the above experiments and the results obtained, we can consider several use
cases where the system can be applied:

- Smart agriculture, where we could add soil moisture sensors using LoRaWAN for
    longer range instead of BLE.
- Industrial automation, where we could replace the BLE communication protocol with
    MODBUS/MQTT in order to provide multinode communications.
- Disaster monitoring, where we could add CO 2 sensors using ZigBee in case of multiple
    nodes used within a single mesh.

3.6. Enhancing Scientific Rigor

While this study focuses on the practical implementation and evaluation of a 5G-
enabled IoT sensor monitoring system, we point out that the scientific level could be further
strengthened by incorporating formal mathematical, statistical, and algorithmic analysis.
In later versions of this study, we will attempt to add analytical delay models such as
round-trip time (RTT) with data-size-to-bandwidth ratios that can be used in order to
predict transmission latency systematically. Including multiple test iterations will give
us the possibility for robust statistical interpretations of the experimental results. From
algorithmic perspectives, we would like to apply heuristic or machine learning techniques
to create a power-aware transmission scheduling mechanism in order to optimize the
energy usage during data uploads. Machine learning approaches will optimally reorder
the time of data uploads for reducing the energy expenditures. With this approach, we aim
not only to analyse the empirical data but also to support our findings with a theoretical
framework for scalable and sustainable IoT deployments on 5G and 6G networks.

## 4. Future Work and Discussion

It looks like a 5G connection could be the best choice to send data to a cloud device.
In future development, changing from BLE (Bluetooth Low Energy) to MQTT (Message
Queuing Telemetry Transport) [ 38 ] could greatly improve the system’s scalability, efficiency,
and communication range. We believe that MQTT is better than BLE because it is a
messaging protocol that works very well for IoT environments where devices are trying to
communicate over long distances or through the internet. Unlike BLE, which is short-range
and for point-to-point communication, MQTT enables real-time data transmission from
multiple devices over a broad network. Finally, there is a need to optimize the exchange of
information in an efficient manner with reduced power consumption and better support
for future scalability, which makes the publish-subscribe model of MQTT the most optimal.
It could be tested if there are possibilities of integrating more edge devices or if the current
consumption is lower with the MQTT protocol.

4.1. Research Challenges and Future Directions for 6G IoT

In the 6G IoT network, energy consumption of IoT devices is a major issue. All IoT
devices connected to the network require significant resources in order to have all data
received and transmitted to the registered base stations. Therefore, the 6G IoT network
will require thousands of base stations in order to provide the necessary coverage, with
each base station consuming about 2.5 up to 4 kW of energy [ 39 ]. Using protocols and
resources that are energy efficient (such as solar power, thermal power, wind power, or
even vibration power) will profit QoS in terms of energy consumption [ 40 ]. On the other
hand, the lack of standards hinders the deployment of the 6G network as a technology
in order to meet the stringent requirements 6G brings. The integration of the MODBUS


protocol [ 41 ] for 6G IoT communication will provide enhanced connectivity and speed,
supporting the needed data rate and latency to IoT systems.
The MODBUS protocol is a protocol originally developed in 1979 by Modicon for
device communication based on master–slave architecture, where the master initiates
and controls the communication and the slave responds back to the master’s requests.
MODBUS remains one of the fundamental protocols for 6G IoT communication and can be
integrated with other modern IoT protocols due to its reliability, high-speed, high-capacity
and robustness characteristics. We could consider for instance a smart building scenario
where sensors and controllers use the MODBUS protocol using the 6G network. Real-time
monitoring, connection security, and edge analysis will be the characteristic the MODBUS
protocol can offer. Real-time monitoring will be able to send real-time data for the status of
the equipment used, authentication and encryption will ensure reliability and security on
the transmitted data, and edge analysis will detect any anomalies, triggering immediate
corrections without any latency.
From the hardware point of view, sensors, memory and network servers are used to
support powerful and smart IoT and nano IoT devices and embedded wearables need to
be redesigned in order to be energy efficient. From the privacy and security points of view,
the growth of IoT device communication based on the 6G network brings new security and
privacy challenges concerning risks to thread attacks. Key security aspects that need to be
taken into consideration are end-to-end encryption, AI thread detection algorithms, and
blockchain technology.
AI integration, in combination with MODBUS and MQTT-SN, is going to be key task
for future work. MODBUS is a protocol with low overheads and compatibility with edge
devices, and AI with Raspberry Pi filtering will lead to lower power consumption and
bandwidth reduction. MODBUS could offer faster and more structured communication,
leading to lower energy consumption, and AI will perform data transmission optimiza-
tion, sending data only when they are needed or during low-traffic periods. MQTT-SN
could be used in combination with MODBUS on the edge layer, improving scalability and
low-latency requirements.

4.2. Discussion

In our experiments, the 5G connection proved reliable when sending data to the cloud
device. For future development, adopting MQTT (Message Queuing Telemetry Transport)
instead of BLE (Bluetooth Low Energy) could be investigated. MQTT is lightweight and
is designed for high-latency, low-bandwidth networks. These characteristics make it
ideal for IoT environments, where devices must communicate over long distances. In
contrast to BLE’s short range and point-to-point connections, MQTT allows multiple
devices to communicate over a broader network. Finally, MQTT’s publish-subscribe model
would simplify the data exchange procedure, enabling effective data handling and lower
power consumption.
Regarding the results of our experiments, it can be concluded that the power char-
acteristics of the presented architecture would be significantly improved if the use of the
Raspberry Pi could be avoided, since it is the dominant factor in the power consumption of
the system. In order to reach this goal, the system would need to be updated at the very
least in the following two ways:

1. To use an integrated 5G module directly on the ESP32 for long-range communication.
    These modules are starting to become available and we plan on procuring one for
    future research.


2. To implement the needed application-layer protocols on the ESP32 software. This is
    challenging, because, unlike the Raspberry Pi that runs Linux, the ESP32 needs to be
    programmed in C/C++ directly, without the ability to use most of the Linux libraries.
The current 5G IoT sensor monitoring system could face several limitations.For instance:
- Physical risks: outdoor devices could be exposed to weather conditions such as
    extreme heat or cold conditions, as well as theft risks.
- Power constraints: the reliance on batteries or solar panels is challenging.
- Environmental interference: the BLE protocol is sensitive to electromagnetic interfer-
    ence, which may affect the reliability, especially in industrial environments.
- Sensor vulnerability: sensor accuracy could vary based on extreme weather conditions
- Network instability: this could lead to high energy consumption.

## 5. Conclusions

The specific study focuses into the design, implementation, and evaluation of an IoT
sensor monitoring system. This is achieved with the integration of an ESP32 microcontroller,
the use of BLE communication protocol, the Raspberry Pi 4 as a getaway, and a 5G module
for cellular connectivity.
Our experiment has proven great benefits in terms of real time data transmission,
energy utilization, and scalability. With the use of a ESP32 microcontroller and Raspberry
Pi with BLE for data transmission, the system performs with high efficiency and reliability
at the communication level. In terms of cloud-based data storage and visualization, the
ThingSpeak platform enhances to the maximum the accessibility and usability. In parallel,
we proved that its data rate limitations and storage constrain reveal scalability challenges.
Experimental results provided key performance metrics, especially in terms of power
consumption and data transmission efficiency. In terms of energy consumption, the analysis
performed has shown that the system could be improved with the adoption of solar cells
for further enhancement, being able to operate with minimal energy, supporting long-term
deployment with photovoltaic sources.
With the integrated 5G module, high-speed data transmission with low latency is
enabled, making it ideal for smart real-time environmental monitoring solutions. Future
optimization could be performed with the use of the MQTT protocol for performance
improvement, scalability, and efficiency, as well as MODBUS protocols for enhancement of
communication efficiency using 6G bandwidth and meeting energy efficiency challenges
through novel sources of power. This work contributes to the field for understanding any
practical limitations of a 5G IoT system deployment, offering a benchmark and emphasizing
any trade-offs between data rates, energy consumption issues, and latency.
Looking into the future, the transition to the 6G network will bring new challenges
and opportunities, especially in terms of IoT devices power consumption interoperability
and security. We can expect emerging technologies, including AI-powered threat detection,
blockchain-based security, and real-time edge processing that will ensure reliable and
secure IoT deployments. Future work on optimization of energy efficiency and resilience
will be essential for making IoT-based sensor systems more sustainable.

**Author Contributions:** Conceptualization, G.G. and D.J.V.; methodology, G.G. and D.J.V.; software,
G.G.; validation, G.G., A.M., M.D. and D.J.V.; formal analysis, G.G.; investigation, G.G.; resources,
G.G. and D.J.V.; data curation, G.G., V.K.; writing—original draft preparation, G.G. and V.K.; writing—
review and editing, V.K. and D.J.V.; visualization, G.G.; supervision, A.M., M.D., and D.J.V.; project
administration, D.J.V. All authors have read and agreed to the published version of the manuscript.

**Funding:** This research received no external funding.


```
Data Availability Statement: Data is available by request to the corresponding author.
Conflicts of Interest: The authors declare no conflict of interest.
```
## References

1. Munirathinam, S. Chapter Six—Industry 4.0: Industrial Internet of Things (IIOT).Adv. Comput. **2020** , 117 , 129–164. [CrossRef]
2. Witczak, D.; Szymoniak, S. Review of Monitoring and Control Systems Based on Internet of Things.Appl. Sci. **2024** , 14 , 8943.
    [CrossRef]
3. Duguma, A.L.; Bai, X. How the internet of things technology improves agricultural efficiency.Artif. Intell. Rev. **2024** , 58 , 63.
    [CrossRef]
4. Hajjaji, Y.; Boulila, W.; Farah, I.R.; Romdhani, I.; Hussain, A. Big data and IoT-based applications in smart environments:
    A systematic review.Comput. Sci. Rev. **2021** , 39 , 100318. [CrossRef]
5. Chataut, R.; Phoummalayvane, A.; Akl, R. Unleashing the Power of IoT: A Comprehensive Review of IoT Applications and
    Future Prospects in Healthcare, Agriculture, Smart Homes, Smart Cities, and Industry 4.0.Sensors **2023** , 23 , 7194. [CrossRef]
6. Khan, W.; Usama, M.; Khan, M.S.; Saidani, O.; Al Hamadi, H.; Alnazzawi, N.; Alshehri, M.S.; Ahmad, J. Enhancing security in
    6G-enabled wireless sensor networks for smart cities: A multi-deep learning intrusion detection approach.Front. Sustain. Cities
    **2025** , 7 , 1580006. [CrossRef]
7. Ferrag, M.A.; Friha, O.; Kantarci, B.; Tihanyi, N.; Cordeiro, L.; Debbah, M.; Hamouda, D.; Al-Hawawreh, M.; Choo, K.K.R. Edge
    Learning for 6G-Enabled Internet of Things: A Comprehensive Survey of Vulnerabilities, Datasets, and Defenses.IEEE Commun.
    Surv. Tutor. **2023** , 25 , 2654–2713. [CrossRef]
8. Triantafyllou, A.; Sarigiannidis, P.; Lagkas, T.D. Network Protocols, Schemes, and Mechanisms for Internet of Things (IoT):
    Features, Open Challenges, and Trends.Wirel. Commun. Mob. Comput. **2018** , 2018 , 5349894. [CrossRef]
9. Rajendhar, P.; Kumar, P.P.; Venkatesh, R. Zigbee based wireless system for remote supervision and control of a substation. In
    Proceedings of the 2017 International Conference on Innovative Research In Electrical Sciences (IICIRES), Nagapattinam, India,
    16–17 June 2017; pp. 1–4. [CrossRef]
10. Raza, S.; Misra, P.; He, Z.; Voigt, T. Building the Internet of Things with bluetooth smart.Ad Hoc Netw. **2017** , 57 , 19–31. [CrossRef]
11. Barker, P.; Hammoudeh, M. A Survey on Low Power Network Protocols for the Internet of Things and Wireless Sensor Networks.
    In Proceedings of the Proceedings of the International Conference on Future Networks and Distributed Systems, New York, NY,
    USA, 19–20 July 2017; [CrossRef]
12. Raza, U.; Kulkarni, P.; Sooriyabandara, M. Low Power Wide Area Networks: An Overview.IEEE Commun. Surv. Tutor. **2017** ,
    19 , 855–873. [CrossRef]
13. Adelantado, F.; Vilajosana, X.; Tuset-Peiro, P.; Martinez, B.; Melia-Segui, J.; Watteyne, T. Understanding the Limits of LoRaWAN.
    IEEE Commun. Mag. **2017** , 55 , 34–40. [CrossRef]
14. Ichimescu, A.; Popescu, N.; Popovici, E.C.; Toma, A. Energy efficiency for 5G and beyond 5G: Potential, limitations, and future
    directions.Sensors **2024** , 24 , 7402. [CrossRef]
15. Bhide, P.; Shetty, D.; Mikkili, S. Review on 6G communication and its architecture, technologies included, challenges, security
    challenges and requirements, applications, with respect to AI domain.IET Quantum Commun. **2025** , 6 , e12114. [CrossRef]
16. Akbar, M.S.; Hussain, Z.; Ikram, M.; Sheng, Q.Z.; Mukhopadhyay, S.C. On challenges of sixth-generation (6G) wireless networks:
    A comprehensive survey of requirements, applications, and security issues.J. Netw. Comput. Appl. **2025** , 233 , 104040. [CrossRef]
17. Lien, S.Y.; Hung, S.C.; Deng, D.J.; Wang, Y.J. Optimum Ultra-Reliable and Low Latency Communications in 5G New Radio.Mob.
    Netw. Appl. **2018** , 23 , 1020–1027. [CrossRef]
18. Heletei, V. Latency and reliability in URLLC for advanced wireless networks. In Proceedings of the 7th ISPC «Scientific
    Community: Interdisciplinary Research», Hamburg, Germany, 6–8 February 2024; pp. 350–352.
19. Yan, J.; Härri, J. On the feasibility of URLLC for 5G-NR V2X sidelink communication at 5.9 GHz. In Proceedings of the
    GLOBECOM 2022, IEEE Global Communications Conference, Rio de Janeiro, Brazil, 4–8 December 2022.
20. Siddiqi, M.A.; Yu, H.; Joung, J. 5G Ultra-Reliable Low-Latency Communication Implementation Challenges and Operational
    Issues with IoT Devices.Electronics **2019** , 8 , 981. [CrossRef]
21. Liang, B.; Gregory, M.A.; Li, S. Latency Analysis for Mobile Cellular Network uRLLC Services.J. Telecommun. Digit. Econ. **2022** ,
    10 , 39–57. [CrossRef]
22. Kaushik, A.; Singh, R.; Li, M.; Luo, H.; Dayarathna, S.; Senanayake, R.; An, X.; Stirling-Gallacher, R.A.; Shin, W.; Di Renzo, M.
    Integrated Sensing and Communications for IoT: Synergies with Key 6G Technology Enablers.IEEE Internet Things Mag. **2024** ,
    7 , 136–143. [CrossRef]
23. Pradhan, A.; Das, S.; Piran, M.J.; Han, Z. A Survey on Security of Ultra/Hyper Reliable Low Latency Communication: Recent
    Advancements, Challenges, and Future Directions.IEEE Access **2024** , 12 , 112320–112353. [CrossRef]


24. Espressif Systems. ESP32 Overview | Espressif Systems. 2019. Available online: https://www.espressif.com/en/products/
    hardware/esp32/overview (accessed on 20 June 2025).
25. Lewis, A.; Campbell, M.; Stavroulakis, P. Performance evaluation of a cheap, open source, digital environmental monitor based
    on the Raspberry Pi.Measurement **2016** , 87 , 228–235. [CrossRef]
26. Kim, J.; Han, K. Backoff scheme for crowded Bluetooth low energy networks.IET Commun. **2017** , 11 , 548–557. [CrossRef]
27. Kanwal, T.; Rehman, S.U.; Imran, A.; Mahmoud, H.A. Energy-Efficient Internet of Things-Based Wireless Sensor Network for
    Autonomous Data Validation for Environmental Monitoring.Comput. Syst. Sci. Eng. **2025** , 49 , 185–212.
28. Zreikat, A.I.; AlArnaout, Z.; Abadleh, A.; Elbasi, E.; Mostafa, N. The Integration of the Internet of Things (IoT) Applications into
    5G Networks: A Review and Analysis.Computers **2025** , 14 , 250. [CrossRef]
29. Sumit; Gupta, D.; Juneja, S.; Nauman, A.; Hamid, Y.; Ullah, I.; Kim, T.; Tag eldin, E.M.; Ghamry, N.A. Energy Saving
    Implementation in Hydraulic Press Using Industrial Internet of Things (IIoT).Electronics **2022** , 11 , 4061. [CrossRef]
30. Waleed, S.; Ullah, I.; Khan, W.U.; Rehman, A.U.; Rahman, T.; Li, S. Resource allocation of 5G network by exploiting particle
    swarm optimization.Iran J. Comput. Sci. **2021** , 4 , 211–219. [CrossRef]
31. Ullah, I.; Noor, A.; Nazir, S.; Ali, F.; Ghadi, Y.Y.; Aslam, N. Protecting IoT devices from security attacks using effective
    decision-making strategy of appropriate features.J. Supercomput. **2024** , 80 , 5870–5899. [CrossRef]
32. Tang, M.; Cai, S.; Lau, V.K.N. Over-the-Air Aggregation with Multiple Shared Channels and Graph-Based State Estimation for
    Industrial IoT Systems.IEEE Internet Things J. **2021** , 8 , 14638–14657. [CrossRef]
33. Bluetooth SIG. Bluetooth GATT Specifications. 2020. Available online: https://www.bluetooth.com/specifications/gatt/
    (accessed on 20 June 2025).
34. Godara, B.; Nikita, K.S. Wireless mobile communication and healthcare. In Proceedings of the 7th International Conference,
    MobiHealth 2017, Vienna, Austria, 14–15 November 2017; Proceedings; Springer: Cham, Switzerland, 2012; pp. 21–23.
35. Zafar, S.; Miraj, G.; Baloch, R.; Murtaza, D.; Arshad, K. An IoT based real-time environmental monitoring system using Arduino
    and cloud service.Eng. Technol. Appl. Sci. Res. **2018** , 8 , 3238–3242. [CrossRef]
36. Nadeem, B.; Jamil, F.; Hussain, A.; Nadeem, H.; Khiadani, M.; Ali, H.M. Comparative experimental analysis of monocrystalline
    and polycrystalline photovoltaic panel through hybrid phase change material.J. Energy Storage **2024** , 100 , 113357. [CrossRef]
37. ESnet. iperf3: A TCP, UDP, and SCTP Network Bandwidth Measurement Tool. Available online: https://github.com/esnet/iperf
    (accessed on 20 June 2025).
38. Luzuriaga, J.E.; Cano, J.C.; Calafate, C.; Manzoni, P.; Perez, M.; Boronat, P. Handling mobility in IoT applications using the
    MQTT protocol. In Proceedings of the 2015 Internet Technologies and Applications (ITA), Wrexham, UK, 8–11 September 2015;
    pp. 245–250. [CrossRef]
39. Sodhro, A.H.; Pirbhulal, S.; Luo, Z.; Muhammad, K.; Zahid, N.Z. Toward 6G Architecture for Energy-Efficient Communication in
    IoT-Enabled Smart Automation Systems.IEEE Internet Things J. **2021** , 8 , 5141–5148. [CrossRef]
40. Wu, T.; Redouté, J.M.; Yuce, M.R. A Wireless Implantable Sensor Design with Subcutaneous Energy Harvesting for Long-Term
    IoT Healthcare Applications.IEEE Access **2018** , 6 , 35801–35808. [CrossRef]
41. Yuanyuan, Y.; Meng, C. An Improved Algorithm for Adaptive Communication Frame Length Based on Modbus Protocol.
    In Proceedings of the 2020 IEEE 6th International Conference on Computer and Communications (ICCC), Chengdu, China,
    11–14 December 2020; pp. 132–135. [CrossRef]

**Disclaimer/Publisher’s Note:** The statements, opinions and data contained in all publications are solely those of the individual
author(s) and contributor(s) and not of MDPI and/or the editor(s). MDPI and/or the editor(s) disclaim responsibility for any injury to
people or property resulting from any ideas, methods, instructions or products referred to in the content.


