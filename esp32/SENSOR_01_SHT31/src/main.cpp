#include <Arduino.h>      
#include <Wire.h>         
#include <SPI.h>          
#include "Adafruit_SHT31.h" 
#include <BLEDevice.h>    
#include <BLEServer.h>    
#include <BLE2902.h>      

// CONFIGURACIÓN DE TIEMPOS 

#define TIME_TO_SLEEP        60          // Tiempo en Deep Sleep (1 minuto)
#define TIME_AWAKE_MS        10000       // Ventana activa transmitiendo (10 segundos)
#define TIMEOUT_CONEXION_MS  15000       // Tiempo límite de espera si la Raspi no está (15 segundos)
#define US_TO_S_FACTOR       1000000ULL  // Factor de conversión para microsegundos

#define I2C_SDA 33
#define I2C_SCL 32

Adafruit_SHT31 sht31 = Adafruit_SHT31();
BLECharacteristic *pCharacteristic;
BLEServer *pServer;

bool deviceConnected = false;

#define SERVICE_UUID           "fc3816f9-e1c0-4530-b80e-086f8d8f5491"
#define CHARACTERISTIC_UUID    "5bd26117-cecc-41b2-96b6-1ceefeb4526c"

class MyServerCallbacks: public BLEServerCallbacks {
    void onConnect(BLEServer* pServer) override { deviceConnected = true; }
    void onDisconnect(BLEServer* pServer) override { deviceConnected = false; }
};

void irADormir() {
  Serial.printf("[POWER] Entrando en Deep Sleep por %d segundos...\n", TIME_TO_SLEEP);
  delay(100);
  esp_sleep_enable_timer_wakeup(TIME_TO_SLEEP * US_TO_S_FACTOR);
  esp_deep_sleep_start();
}

void setup() {
  Serial.begin(115200);
  delay(200); // Pausa mínima inicial
  Serial.println("\n--- NODO DESPIERTO ---");

  // 1. Inicializar Hardware
  Wire.begin(I2C_SDA, I2C_SCL);
  if (!sht31.begin(0x44)) {
    Serial.println("[-] Sensor no detectado. Forzando sleep.");
    irADormir();
  }

  // 2. Inicializar BLE
  BLEDevice::init("ESP32_SHT31_Sensor_01"); 
  pServer = BLEDevice::createServer();
  pServer->setCallbacks(new MyServerCallbacks());

  BLEService *pService = pServer->createService(SERVICE_UUID);
  pCharacteristic = pService->createCharacteristic(
                      CHARACTERISTIC_UUID,
                      BLECharacteristic::PROPERTY_READ | BLECharacteristic::PROPERTY_NOTIFY
                    );
  pCharacteristic->addDescriptor(new BLE2902()); 
  pService->start();
  
  BLEDevice::getAdvertising()->addServiceUUID(SERVICE_UUID);
  BLEDevice::startAdvertising();
  Serial.println("[BLE] Anunciando en el aire...");

  // 3. Control de Ventana Activa y Protección contra desconexiones
  unsigned long tiempoInicioDespierto = millis();
  unsigned long tiempoInicioTransmision = 0;
  unsigned long ultimoMuestreo = 0;
  bool transmitiendo = false;

  while (true) {
    unsigned long tiempoActual = millis();

    if (deviceConnected) {
      // Si se acaba de conectar la Raspberry Pi, marcamos el inicio de los 10 segundos
      if (!transmitiendo) {
        transmitiendo = true;
        tiempoInicioTransmision = tiempoActual;
        Serial.println("[BLE] ¡Raspberry Pi vinculada! Iniciando ráfaga de 10 segundos...");
      }

      // Control de envío cada 2 segundos dentro de la ventana de 10 segundos
      if (tiempoActual - tiempoInicioTransmision < TIME_AWAKE_MS) {
        if (tiempoActual - ultimoMuestreo >= 2000) { 
          ultimoMuestreo = tiempoActual;
          
          float t = sht31.readTemperature();
          float h = sht31.readHumidity();
          
          if (!isnan(t) && !isnan(h)) {
            String dataStr = String(t, 1) + "," + String(h, 1);
            pCharacteristic->setValue(dataStr.c_str());
            pCharacteristic->notify(); 
            Serial.printf("[TX] T: %.1f | H: %.1f\n", t, h);
          }
        }
      } else {
        // Ya se cumplieron los 10 segundos de transmisión exitosa
        Serial.println("[POWER] Ráfaga de 10 segundos completada con éxito.");
        break;
      }
    } else {
      // Si la Raspi se desconectó a mitad de la transmisión o nunca se conectó...
      if (transmitiendo) {
        Serial.println("!!!! Conexión interrumpida durante la transmisión. Abortando.");
        break; 
      }

      // PROTECCIÓN DE TIMEOUT: Si pasan 15 segundos y la Raspi nunca apareció
      if (tiempoActual - tiempoInicioDespierto > TIMEOUT_CONEXION_MS) {
        Serial.println("[-] Timeout: La Raspberry Pi no respondió en 15s. Durmiendo.");
        break;
      }

      // Mantener los anuncios activos mientras espera
      BLEDevice::startAdvertising();
      delay(200); 
    }
    
    yield(); 
  }

  // 4. Fin del ciclo -> Dormir de inmediato
  irADormir();
}

void loop() {
  // Vacío. Todo ocurre en el setup controlado.
}
