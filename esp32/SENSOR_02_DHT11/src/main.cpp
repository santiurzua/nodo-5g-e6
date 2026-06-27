#include <Arduino.h>      // Cabecera core obligatoria para usar tipos de datos Arduino en PlatformIO
#include <DHT.h>          // Librería oficial de Adafruit para sensores de la familia DHT
#include <BLEDevice.h>    // Componentes base del stack Bluetooth Low Energy
#include <BLEServer.h>    // Controladores para comportarse como Servidor GATT
#include <BLE2902.h>      // Descriptor necesario para habilitar las Notificaciones asíncronas

// CONFIGURACIÓN DE TIEMPOS (Sincronizados con el Nodo 1)

#define TIME_TO_SLEEP        900          // Tiempo en Deep Sleep (15 minutos)
#define TIME_AWAKE_MS        5000         // Ventana activa transmitiendo (5 segundos)
#define TIMEOUT_CONEXION_MS  15000        // Tiempo límite de espera si la Raspi no está (15 segundos)
#define US_TO_S_FACTOR       1000000ULL  // Factor de conversión para microsegundos

// Configuración del pines para el DHT11
#define DHTPIN 32         // Conecta el pin 'S' del módulo a este GPIO
#define DHTTYPE DHT11     // Definimos explícitamente el modelo de transductor

// Instanciación del objeto del sensor DHT
DHT dht(DHTPIN, DHTTYPE);

// Punteros globales
BLECharacteristic *pCharacteristic;
BLEServer *pServer;

// VARIABLES GLOBALES PARA TELEMETRÍA DE TIEMPO
unsigned long tiempoInicioAnuncios = 0; // Guarda cuándo se activa el Bluetooth
unsigned long tiempoConexion = 0;       // Guarda el momento exacto del enlace

bool deviceConnected = false;

// UUIDs únicos sincronizados con el script de Python de la Raspberry Pi
#define SERVICE_UUID           "fc3816f9-e1c0-4530-b80e-086f8d8f5491"
#define CHARACTERISTIC_UUID    "5bd26117-cecc-41b2-96b6-1ceefeb4526c"

// Clase Callback adaptada con cronómetro de conexión BLE para el Sensor 2
class MyServerCallbacks: public BLEServerCallbacks {
    void onConnect(BLEServer* pServer) override { 
      deviceConnected = true; 
      tiempoConexion = millis(); // Captura instantánea del tiempo de enlace
      
      unsigned long tiempoTranscurrido = tiempoConexion - tiempoInicioAnuncios;
      Serial.println("\n==================================================");
      Serial.println("[BLE] ¡Central (Raspberry Pi) conectada al Sensor 2!");
      Serial.printf("[CRONÓMETRO] Tiempo total de conexión BLE: %lu ms\n", tiempoTranscurrido);
      Serial.println("==================================================\n");
    }
    void onDisconnect(BLEServer* pServer) override { 
      deviceConnected = false; 
      Serial.println("[BLE] Central desconectada del Sensor 2.");
    }
};

// Función para mandar el módulo a dormir de forma limpia
void irADormir() {
  Serial.printf("[POWER] Sensor 2 entrando en Deep Sleep por %d segundos...\n", TIME_TO_SLEEP);
  delay(100);
  esp_sleep_enable_timer_wakeup(TIME_TO_SLEEP * US_TO_S_FACTOR);
  esp_deep_sleep_start();
}

void setup() {
  // Inicialización del puerto serie para telemetría local
  Serial.begin(115200);
  delay(500); // Pausa de cortesía para la radio y el puerto serie
  Serial.println("\n--- ESP32 SENSOR 2 DESPIERTA DE DEEP SLEEP ---");

  // 1. INICIALIZACIÓN DEL SENSOR DHT11
  dht.begin();
  Serial.println("[+] Sensor DHT11 inicializado.");

  // 2. CONFIGURACIÓN DEL ENTORNO INALÁMBRICO BLE
  // Identificador unificado para el script de la Raspberry Pi
  BLEDevice::init("ESP32_DHT11_Sensor_02"); 
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
  
  // Guardamos el momento justo antes de encender la radio para telemetría
  tiempoInicioAnuncios = millis();
  BLEDevice::startAdvertising();
  Serial.println("[BLE] Sensor 2 anunciando en el aire. Esperando Raspberry Pi...");

  // 3. Control de Ventana Activa y Protección contra desconexiones
  unsigned long tiempoInicioDespierto = millis();
  unsigned long tiempoInicioTransmision = 0;
  unsigned long ultimoMuestreo = 0;
  bool transmitiendo = false;

  while (true) {
    unsigned long tiempoActual = millis();

    if (deviceConnected) {
      // Si se acaba de conectar la Raspberry Pi, marcamos el inicio de los 5 segundos de ráfaga
      if (!transmitiendo) {
        transmitiendo = true;
        tiempoInicioTransmision = tiempoActual;
        Serial.println("[BLE SENSOR 2] ¡Raspberry Pi vinculada! Iniciando ráfaga de 5 segundos...");
      }

      // Control de envío cada 1 segundo dentro de la ventana de 5 segundos
      if (tiempoActual - tiempoInicioTransmision <= TIME_AWAKE_MS) {
        if (tiempoActual - ultimoMuestreo >= 1000) { 
          ultimoMuestreo = tiempoActual;
          
          float h = dht.readHumidity();
          float t = dht.readTemperature();
          
          if (!isnan(t) && !isnan(h)) {
            String dataStr = String(t, 1) + "," + String(h, 1);
            
            // CRONOMETRAR EL PROCESO DE ENVÍO EN MICROSEGUNDOS
            unsigned long t_envio_inicio = micros();
            
            pCharacteristic->setValue(dataStr.c_str());
            pCharacteristic->notify(); 
            
            unsigned long t_envio_fin = micros();
            unsigned long duracion_envio = t_envio_fin - t_envio_inicio;
            
            Serial.printf("[TX SENSOR 2] Temp: %.1f °C | Hum: %.1f %% | [Procesado/Envío: %lu µs]\n", 
                          t, h, duracion_envio);
          } else {
            Serial.println("[-] Error de lectura: Falla en la adquisición del DHT11.");
          }
        }
      } else {
        // Ya se cumplieron los 5 segundos de transmisión exitosa
        Serial.println("[POWER] Ráfaga de 5 segundos del Sensor 2 completada.");
        break;
      }
    } else {
      // Si la Raspi se desconectó a mitad de la transmisión activa...
      if (transmitiendo) {
        Serial.println("!!!! Conexión interrumpida en Sensor 2. Abortando.");
        break; 
      }

      // PROTECCIÓN DE TIMEOUT: Si pasan 15 segundos y la Raspi nunca apareció
      if (tiempoActual - tiempoInicioDespierto > TIMEOUT_CONEXION_MS) {
        Serial.println("[-] Timeout: La Raspberry Pi no respondió al Sensor 2 en 15s. Durmiendo.");
        break;
      }

      // Mantener los anuncios activos mientras espera
      BLEDevice::startAdvertising();
      delay(200); 
    }
    
    yield(); // Evita que se dispare el hardware Watchdog de la ESP32
  }

  // 4. Fin del ciclo -> Dormir de inmediato
  irADormir();
}

void loop() {
  // Vacío. Toda la lógica corre controlada en el setup().
}
