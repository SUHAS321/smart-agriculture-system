import json
import boto3

sns = boto3.client('sns')

TOPIC_ARN = "arn:aws:sns:eu-north-1:420653164002:smartfarm"

def lambda_handler(event, context):
    print("Received event:", event)

    # Extract values safely
    soil = float(event.get("soil_moisture", 0))
    temp = float(event.get("temperature", 0))
    hum  = float(event.get("humidity", 0))

    # Condition: LOW SOIL
    if soil < 30:
        message = f"""
🚨 SMART FARM ALERT 🚨

Soil Moisture: {soil}%
Temperature: {temp}°C
Humidity: {hum}%

⚠ Soil is DRY → Turn ON water pump immediately!
"""

        response = sns.publish(
            TopicArn=TOPIC_ARN,
            Subject="🚨 Smart Farm Alert",
            Message=message
        )

        print("Alert sent:", response)
        return {"status": "ALERT SENT"}

    return {"status": "NORMAL"}
