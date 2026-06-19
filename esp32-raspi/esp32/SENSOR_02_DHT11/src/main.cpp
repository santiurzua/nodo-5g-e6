#include <Arduino.h>      // Cabecera core obligatoria para usar tipos de datos Arduino en PlatformIO
#include <DHT.h>          // Librería oficial de Adafruit para sensores de la familia DHT
#include <BLEDevice.h>    // Componentes base del stack Bluetooth Low Energy
#include <BLEServer.h>    // Controladores para comportarse como Servidor GATT
#include <BLE2902.h>      // Descriptor necesario para habilitar las Notificaciones asíncronas

// Configuración del pin físico digital para el DHT11
#define DHTPIN 32         // Conecta el pin 'S' del módulo a este GPIO
#define DHTTYPE DHT11     // Definimos explícitamente el modelo de transductor

// Instanciación del objeto del sensor DHT
DHT dht(DHTPIN, DHTTYPE);

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
      Serial.println("¡Central (Raspberry Pi) conectada al Sensor 2!");
    };
    
    void onDisconnect(BLEServer* pServer) { 
      deviceConnected = false;
      Serial.println("Central desconectada del Sensor 2.");
    }
};

void setup() {
  // Inicialización del puerto serie para telemetría local
  Serial.begin(115200);
  delay(3000); // Pausa de cortesía para estabilizar voltajes
  while (!Serial) delay(10); 
  
  Serial.println("--- INICIANDO SENSOR 2: MONITOREO BLE + DHT11 ---");

  // 1. INICIALIZACIÓN DEL SENSOR DHT11
  dht.begin();
  Serial.println("[+] Sensor DHT11 inicializado.");

  // 2. CONFIGURACIÓN DEL ENTORNO INALÁMBRICO BLE
  // CORRECCIÓN: Nombre sincronizado exactamente con la clave de tu script en la Raspberry Pi
  BLEDevice::init("ESP32_DHT11_Sensor_02");
  
  // Creamos el Servidor GATT
  pServer = BLEDevice::createServer();
  pServer->setCallbacks(new MyServerCallbacks());

  // Creamos la "Carpeta" (Servicio)
  BLEService *pService = pServer->createService(SERVICE_UUID);

  // Creamos el "Archivo" (Característica)
  pCharacteristic = pService->createCharacteristic(
                      CHARACTERISTIC_UUID,
                      BLECharacteristic::PROPERTY_READ |
                      BLECharacteristic::PROPERTY_NOTIFY
                    );

  // Inyectamos el Descriptor CCCD (0x2902) obligatorio para Linux
  pCharacteristic->addDescriptor(new BLE2902()); 
  
  // Levantamos el servicio en memoria
  pService->start();
  
  // 3. CONFIGURACIÓN DE LOS PAQUETES DE ANUNCIO (ADVERTISING)
  BLEAdvertising *pAdvertising = BLEDevice::getAdvertising();
  pAdvertising->addServiceUUID(SERVICE_UUID);
  pAdvertising->setScanResponse(true);       
  pAdvertising->setMinPreferred(0x06);        
  pAdvertising->setMinPreferred(0x12);
  
  // Encendemos la antena de radiofrecuencia
  BLEDevice::startAdvertising();
  Serial.println("[+] Servidor BLE del Sensor 2 activo. Esperando Raspberry Pi...");
}

void loop() {
  static int ciclosEspera = 0;

  // GESTIÓN INDUSTRIAL DE ANUNCIOS: Reinicio asíncrono y seguro fuera del callback
  if (!deviceConnected && oldDeviceConnected) {
      delay(500); // Pausa táctica para que el stack limpie buffers de radio
      pServer->getAdvertising()->start(); 
      Serial.println("[BLE SENSOR 2] Anuncios reiniciados con éxito en el aire.");
      oldDeviceConnected = deviceConnected;
  }
  
  if (deviceConnected && !oldDeviceConnected) {
      oldDeviceConnected = deviceConnected;
  }

  // ESCENARIO 1: La Raspberry Pi está activamente conectada
  if (deviceConnected) {
    ciclosEspera = 0; 
    
    // Captura de variables del DHT11
    float h = dht.readHumidity();
    float t = dht.readTemperature();

    // Filtro de seguridad anti-NaN
    if (!isnan(t) && !isnan(h)) {
      // Formateamos los datos a CSV string: "25.4,60.1"
      String dataStr = String(t, 1) + "," + String(h, 1);
      
      // Cargamos el buffer y disparamos la notificación push
      pCharacteristic->setValue(dataStr.c_str());
      pCharacteristic->notify(); 
      
      Serial.printf("[TX SENSOR 2] Enviando -> Temp: %.1f °C | Hum: %.1f %%\n", t, h);
    } else {
      Serial.println("[-] Error de lectura: Falla en la adquisición del DHT11. Revisa pin 32.");
    }
    
    delay(2000); // Muestreo nominal cada 2 segundos
  } 
  // ESCENARIO 2: Modo Standby (Esperando conexión)
  else {
    if (ciclosEspera % 10 == 0) {
      Serial.println("[STANDBY SENSOR 2] Esperando enlace con la Raspberry Pi...");
    }
    ciclosEspera++;
    delay(500); 
  }
}