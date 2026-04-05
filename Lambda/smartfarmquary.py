import json
import boto3
from boto3.dynamodb.conditions import Key

dynamodb = boto3.resource('dynamodb')
table    = dynamodb.Table('SmartFarmData')

def lambda_handler(event, context):
    params  = event.get('queryStringParameters') or {}
    farm_id = params.get('farm_id', 'FARM_001')
    limit   = int(params.get('limit', 20))

    response = table.query(
        KeyConditionExpression=Key('FarmID').eq(farm_id),
        ScanIndexForward=False,
        Limit=limit
    )

    return {
        'statusCode': 200,
        'headers': {
            'Access-Control-Allow-Origin': '*',
            'Content-Type': 'application/json'
        },
        'body': json.dumps(response['Items'])
    }
