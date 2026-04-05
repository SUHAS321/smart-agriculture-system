import network
import time
from machine import Pin, ADC
import dht
import ujson
from umqtt.simple import MQTTClient

# ---------------- WIFI ----------------
ssid = "Wokwi-GUEST"
password = ""

wifi = network.WLAN(network.STA_IF)
wifi.active(True)
wifi.connect(ssid, password)

print("Connecting to WiFi...")
while not wifi.isconnected():
    time.sleep(1)

print("✅ WiFi Connected")

# ---------------- MQTT ----------------
MQTT_BROKER = "broker.hivemq.com"
CLIENT_ID = "esp32-smartfarm"
TOPIC = "smartfarm/data"

client = MQTTClient(CLIENT_ID, MQTT_BROKER)

try:
    client.connect()
    print("✅ MQTT Connected")
except Exception as e:
    print("❌ MQTT Connection Failed:", e)

# ---------------- SENSORS ----------------
dht_sensor = dht.DHT22(Pin(4))

soil = ADC(Pin(34))
soil.atten(ADC.ATTN_11DB)

led = Pin(2, Pin.OUT)

# ---------------- LOOP ----------------
while True:
    try:
        # Read sensors
        dht_sensor.measure()
        temp = dht_sensor.temperature()
        hum = dht_sensor.humidity()

        soil_raw = soil.read()
        soil_percent = int((soil_raw / 4095) * 100)

        # Create JSON
        data = {
            "temperature": temp,
            "humidity": hum,
            "soil_moisture": soil_percent
        }

        # Publish MQTT
        client.publish(TOPIC, ujson.dumps(data))

        # Print output
        print("\n📡 Data Sent to MQTT")
        print("Temperature:", temp, "°C")
        print("Humidity:", hum, "%")
        print("Soil Moisture:", soil_percent, "%")

        # LED Logic (Pump Simulation)
        if soil_percent < 30:
            led.value(1)
            print("⚠️ Pump ON (Soil Dry)")
        else:
            led.value(0)
            print("✅ Pump OFF (Soil OK)")

    except Exception as e:
        print("Error:", e)

    time.sleep(5)
