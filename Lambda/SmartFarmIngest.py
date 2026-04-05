import json
import boto3
import datetime

dynamodb = boto3.resource('dynamodb')
table    = dynamodb.Table('SmartFarmData')

def lambda_handler(event, context):
    print("Received event:", json.dumps(event))

    # Validate humidity
    humidity = event.get('humidity')
    if humidity is None or float(humidity) > 100 or float(humidity) < 0:
        print("Invalid humidity:", humidity)
        return {'statusCode': 400, 'body': 'Invalid humidity'}

    # Validate temperature
    temperature = event.get('temperature')
    if temperature is None:
        print("Missing temperature")
        return {'statusCode': 400, 'body': 'Missing temperature'}

    item = {
        'FarmID':        event.get('farm_id', 'FARM_001'),
        'Timestamp':     datetime.datetime.utcnow().isoformat(),
        'temperature':   str(temperature),
        'humidity':      str(humidity),
        'soil_moisture': str(event.get('soil_moisture', 0))
    }

    table.put_item(Item=item)
    print("Saved to DynamoDB:", item)

    return {'statusCode': 200, 'body': 'OK'}
