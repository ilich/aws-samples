from typing import Dict, Any
import json


def error(message: str) -> Dict[str, Any]:
    body = json.dumps({"error": message})
    return {"statusCode": 400, "body": body}


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    req = event.get("queryStringParameters", None)
    if req is None:
        return {"statusCode": 400, "body": error("Bad Request")}

    name = req.get("name", "").strip()
    if name == "":
        return {"statusCode": 400, "body": error("Name is required")}

    res = {"message": f"Hello, {name}!"}
    return {"statusCode": 200, "body": json.dumps(res)}
