import json 
import os
import boto3
import logging

from decimal import Decimal

logger = logging.getLogger()
logger.setLevel(logging.INFO)

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(os.environ["DYNAMODB_TABLE_NAME"])

def decimal_to_native(obj):
    """Convert DynamoDB Decimal types to native Python types"""

    if isinstance(obj, Decimal):
        return int(obj) if obj % 1 == 0 else float(obj)
    elif isinstance(obj, dict):
        return {k: decimal_to_native(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [decimal_to_native(i) for i in obj]
    return obj

def lambda_handler(event, context):
    """handle get requests retrieves key generation result from DynamoDB"""

    path_params = event.get("pathParameters", {})
    request_id = path_params.get("id")

    if not request_id:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "Missing request ID in path parameters"}),
            "headers": {"Content-Type": "application/json"},
        }
    
    logger.info(f"Fetching key generation result for request ID: {request_id}")

    try:
        response = table.get_item(key = {"request_id":request_id})
    except Exception as e:
        logger.error(f"Error fetching item from DynamoDB: {e}")
        return {
            "statusCode": 500,
            "body": json.dumps({"error": "Internal server error"}),
            "headers": {"Content-Type": "application/json"},
        }
    item = response.get("Item")

    if item:
        logger.info(f"Successfully retrieved item for request ID: {request_id}")
        return {
            "statusCode": 200,
            "body": json.dumps(decimal_to_native(item)),
            "headers": {"Content-Type": "application/json"},
        }
    logger.info(f"Result not yet available for {request_id}")

    return {
        "statusCode": 202,
        "body": json.dumps({"request_id": request_id, "status": "Result not yet available"}),
        "headers": {"Content-Type": "application/json"},
    }