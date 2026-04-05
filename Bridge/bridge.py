import paho.mqtt.client as mqtt
import paho.mqtt.enums as mqtt_enums
import ssl, os, time, uuid

FOLDER    = r"C:\Users\suhas\Downloads\king"
CERT_PATH = os.path.join(FOLDER, "SmartFarmESP32.cert.pem.crt")
KEY_PATH  = os.path.join(FOLDER, "SmartFarmESP32.private.key")
CA_PATH   = os.path.join(FOLDER, "AmazonRootCA1.pem")

AWS_ENDPOINT = "a11v8398qcsecp-ats.iot.eu-north-1.amazonaws.com"
AWS_PORT     = 8883
AWS_TOPIC    = "smartfarm/data"
WOKWI_BROKER = "broker.hivemq.com"
WOKWI_PORT   = 1883
WOKWI_TOPIC  = "smartfarm/data"

CLIENT_ID = f"SmartFarmBridge-{uuid.uuid4().hex[:8]}"
print(f"Client ID: {CLIENT_ID}")

ssl_ctx = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
ssl_ctx.load_verify_locations(cafile=CA_PATH)
ssl_ctx.load_cert_chain(certfile=CERT_PATH, keyfile=KEY_PATH)
ssl_ctx.check_hostname = False

def on_aws_connect(client, userdata, flags, reason_code, properties):
    if reason_code == 0:
        print("[AWS]  Connected to IoT Core!")
    else:
        print(f"[AWS]  Failed: {reason_code}")

def on_aws_disconnect(client, userdata, flags, reason_code, properties):
    print(f"[AWS]  Disconnected: {reason_code}")

def on_wokwi_connect(client, userdata, flags, reason_code, properties):
    if reason_code == 0:
        print("[Wokwi] Connected to HiveMQ!")
        client.subscribe(WOKWI_TOPIC)
        print(f"[Wokwi] Subscribed to: {WOKWI_TOPIC}")
    else:
        print(f"[Wokwi] Failed: {reason_code}")

def on_wokwi_message(client, userdata, msg):
    payload = msg.payload.decode()
    print(f"[Wokwi] Received: {payload}")
    aws.publish(AWS_TOPIC, payload, qos=1)
    print(f"[AWS]   Forwarded to: {AWS_TOPIC}")

aws = mqtt.Client(
    callback_api_version=mqtt_enums.CallbackAPIVersion.VERSION2,
    client_id=CLIENT_ID,
    protocol=mqtt.MQTTv311
)
aws.on_connect    = on_aws_connect
aws.on_disconnect = on_aws_disconnect
aws.tls_set_context(ssl_ctx)
aws.connect(AWS_ENDPOINT, AWS_PORT, keepalive=60)
aws.loop_start()
time.sleep(3)

wokwi = mqtt.Client(
    callback_api_version=mqtt_enums.CallbackAPIVersion.VERSION2,
    client_id=f"WokwiListener-{uuid.uuid4().hex[:8]}"
)
wokwi.on_connect = on_wokwi_connect
wokwi.on_message = on_wokwi_message
wokwi.connect(WOKWI_BROKER, WOKWI_PORT, keepalive=60)

print("\nBridge running... (Ctrl+C to stop)\n")
wokwi.loop_forever()
