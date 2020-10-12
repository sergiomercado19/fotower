import json
import boto3
import logging
from botocore.exceptions import ClientError


# Set up our logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

# Connect to DynamoDB
dynamodb = boto3.resource('dynamodb')
pictures_table = dynamodb.Table('fg-pictures-table')

def lambda_handler(event, context):
    # Request parsing
    payload = json.loads(event['body'])

    # Request processing
    picId = event['pathParameters']['id']
    description = payload['description']
    location = payload['location']

    # Response formatting
    status_code = 200
    body = {}

    # Update db item
    try:
        logger.info('Updating picture ({})'.format(picId))
        response = pictures_table.update_item(
            Key={
                'picId': picId
            },
            UpdateExpression="set description=:d, location=:l",
            ExpressionAttributeValues={
                ':d': description,
                ':l': location
            },
            ReturnValues="UPDATED_NEW"
        )

        if response['ResponseMetadata']['HTTPStatusCode'] != 200:
            logger.warn(response['Error']['Message'])
            status_code = response['ResponseMetadata']['HTTPStatusCode']
            body['errors'] = [ response['Error']['Message'] ]
        else:
            logger.info('Updated picture ({})'.format(picId))

    except ClientError as e:
        logger.warn(e.response['Error']['Message'])
        status_code = e.response['ResponseMetadata']['HTTPStatusCode']
        body['errors'] = [ e.response['Error']['Message'] ]

    return {
        'statusCode': status_code,
        'body': json.dumps(body)
    }
