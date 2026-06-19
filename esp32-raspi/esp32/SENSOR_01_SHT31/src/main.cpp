#include <Arduino.h>      // Cabecera core obligatoria para usar tipos de datos Arduino en PlatformIO
#include <Wire.h>         // Librería para manejar la comunicación I2C física
#include <SPI.h>          // Requerida explícitamente por las dependencias internas de Adafruit
#include "Adafruit_SHT31.h" // Librería de abstracción para el sensor SHT31
#include <BLEDevice.h>    // Componentes base del stack Bluetooth Low Energy
#include <BLEServer.h>    // Controladores para comportarse como Servidor GATT
#include <BLE2902.h>      // Descriptor necesario para habilitar las Notificaciones asíncronas

// Configuración de los pines físicos I2C en la placa ESP32
#define I2C_SDA 33
#define I2C_SCL 32

// Instanciación del objeto del sensor SHT31
Adafruit_SHT31 sht31 = Adafruit_SHT31();

// Punteros globales para control desde el loop()
BLECharacteristic *pCharacteristic;
BLEServer *pServer;

// Variables de estado para la máquina de reconexión segura
bool deviceConnected = false;
bool oldDeviceConnected = false;

// UUIDs únicos sincronizados con el script de Python de la Raspberry Pi
#define SERVICE_UUID           "fc3816f9-e1c0-4530-b80e-086f8d8f5491"
#define CHARACTERISTIC_UUID    "5bd26117-cecc-41b2-96b6-1ceefeb4526c"

// Clase Callback: Monitorea el estado de la conexión en tiempo real
class MyServerCallbacks: public BLEServerCallbacks {
    void onConnect(BLEServer* pServer) { 
      deviceConnected = true; 
      Serial.println("¡Central (Raspberry Pi) conectada!");
    };
    
    void onDisconnect(BLEServer* pServer) { 
      deviceConnected = false;
      Serial.println("Central desconectada.");
    }
};

void setup() {
  // Inicialización del puerto serie para telemetría local
  Serial.begin(115200);
  delay(3000); // Pausa de cortesía para estabilizar voltajes
  while (!Serial) delay(10); 
  
  Serial.println("--- INICIANDO SISTEMA DE MONITOREO BLE + I2C ---");

  // 1. INICIALIZACIÓN DEL BUS I2C
  bool status = Wire.begin(I2C_SDA, I2C_SCL);
  if (!status) {
    Serial.println("[-] Error crítico: Fallo en hardware al iniciar el bus I2C");
  } else {
    Serial.println("[+] Bus I2C inicializado con éxito.");
  }

  // 2. INICIALIZACIÓN DEL SENSOR SHT31
  if (!sht31.begin(0x44)) {   
    while (1) {
      Serial.println("[-] Error: Sensor SHT31 no detectado. Verifica cables SDA/SCL.");
      delay(1000); 
    }
  }
  Serial.println("[+] Sensor SHT31 detectado y respondiendo.");

  // 3. CONFIGURACIÓN DEL ENTORNO INALÁMBRICO BLE
  // RECUERDA: Cambiar a "ESP32_SHT31_Sensor_01" cuando flashees el otro módulo.
  BLEDevice::init("ESP32_SHT31_Sensor_02"); 
  
  // Creamos el Servidor GATT
  pServer = BLEDevice::createServer();
  pServer->setCallbacks(new MyServerCallbacks());

  // Creamos el Servicio bajo el UUID unificado
  BLEService *pService = pServer->createService(SERVICE_UUID);

  // Creamos la Característica
  pCharacteristic = pService->createCharacteristic(
                      CHARACTERISTIC_UUID,
                      BLECharacteristic::PROPERTY_READ |
                      BLECharacteristic::PROPERTY_NOTIFY
                    );

  // Descriptor CCCD (0x2902) obligatorio para permitir notificaciones en Linux
  pCharacteristic->addDescriptor(new BLE2902()); 
  
  // Levantamos el servicio en memoria
  pService->start();
  
  // 4. CONFIGURACIÓN DE LOS PAQUETES DE ANUNCIO (ADVERTISING)
  BLEAdvertising *pAdvertising = BLEDevice::getAdvertising();
  pAdvertising->addServiceUUID(SERVICE_UUID); 
  pAdvertising->setScanResponse(true);       
  pAdvertising->setMinPreferred(0x06);        
  pAdvertising->setMinPreferred(0x12);
  
  // Encendemos la antena de radiofrecuencia
  BLEDevice::startAdvertising();
  Serial.println("[+] Servidor BLE activo. Esperando el enlace de la Raspberry Pi...");
}

void loop() {
  static int ciclosEspera = 0;

  // GESTIÓN INDUSTRIAL DE ANUNCIOS: Evita el congelamiento de la antena del ESP32
  if (!deviceConnected && oldDeviceConnected) {
      // Ocurrió una desconexión: esperamos a que el stack limpie el canal y reiniciamos anuncios
      delay(500); 
      pServer->getAdvertising()->start(); 
      Serial.println("[BLE] Anuncios reiniciados de forma segura en el aire.");
      oldDeviceConnected = deviceConnected;
  }
  
  if (deviceConnected && !oldDeviceConnected) {
      // Conexión exitosa detectada
      oldDeviceConnected = deviceConnected;
  }

  // ESCENARIO 1: La Raspberry Pi está activamente conectada
  if (deviceConnected) {
    ciclosEspera = 0; 
    
    // Captura de datos
    float t = sht31.readTemperature();
    float h = sht31.readHumidity();

    if (!isnan(t) && !isnan(h)) {
      // Vectorizamos a formato CSV string: "25.4,60.1"
      String dataStr = String(t, 1) + "," + String(h, 1);
      
      // Cargamos el buffer y disparamos la notificación push
      pCharacteristic->setValue(dataStr.c_str());
      pCharacteristic->notify(); 
      
      Serial.printf("[TX] Enviando a Raspi -> Temp: %.1f °C | Hum: %.1f %%\n", t, h);
    } else {
      Serial.println("[-] Advertencia: Error al leer datos del SHT31.");
    }
    
    delay(2000); // Muestreo nominal cada 2 segundos
  } 
  
  // ESCENARIO 2: Modo Standby (Esperando conexión)
  else {
    if (ciclosEspera % 10 == 0) {
      Serial.println("[STANDBY] Esperando que la Raspberry Pi inicie el script...");
    }
    ciclosEspera++;
    
    delay(500); // Bucle rápido de media velocidad para mantener reactividad
  }
}