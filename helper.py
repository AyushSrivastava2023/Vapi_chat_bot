import requests
import json
import logging

# Setup logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

RECOMMENDATION_API_URL = "http://44.213.132.172:8000/api/v1/recommend"
VTEX_BASE_URL = "https://app.io.vtex.com/cashmerehlc.cashmere-core-services/v0/cashmerehlc/cashdevps/_v/store/product-details"
IOT_API_URL = "https://dev.showcase-cashmere.store/api/iot/glowProduct"


def call_recommendation_api(payload):
    response = requests.post(RECOMMENDATION_API_URL, json=payload)
    if response.status_code != 200:
        raise Exception(f"Recommendation API failed: {response.status_code}")
    return response.json()

# def fetch_product_details_from_vtex(product_ids):
#     logger.info("Fetching product details from VTEX for product IDs: %s", product_ids)
#     product_data = []
#     for pid in product_ids:
#         response = requests.post(VTEX_API_URL, json={"id": pid})
#         if response.status_code == 200:
#             logger.info("VTEX response success for product ID: %s", pid)
#             product_data.append(response.json())
#         else:
#             logger.error("VTEX API failed for ID %s with status %s", pid, response.status_code)
#     return product_data

def fetch_product_details_from_vtex(product_ids, fields="basic, price"):
    VTEX_BASE_URL = "https://app.io.vtex.com/cashmerehlc.cashmere-core-services/v0/cashmerehlc/cashdevps/_v/store/product-details"
    
    headers = {
         "VtexIdclientAutCookie": "eyJhbGciOiJFUzI1NiIsImtpZCI6IjhCRkM1QjAxODUyNUE3OTk1RjAxNDExNTZBNDNCNTcwOTc4NDkxMUQiLCJ0eXAiOiJqd3QifQ.eyJzdWIiOiJ2dGV4YXBwa2V5LWNhc2htZXJlaGxjLUlZWldOUyIsImFjY291bnQiOiJjYXNobWVyZWhsYyIsImF1ZGllbmNlIjoiYWRtaW4iLCJleHAiOjE3NTI3NjQwOTksInR5cGUiOiJhcHBrZXkiLCJ1c2VySWQiOiJjOTQ1ZjA0Yy0yMjk3LTQ5NTktYWVjOS03MjQxNWJkNmM5OTYiLCJpYXQiOjE3NTI3NDI0OTksImlzUmVwcmVzZW50YXRpdmUiOmZhbHNlLCJpc3MiOiJ0b2tlbi1lbWl0dGVyIiwianRpIjoiZTIzNjI2ODEtYjdhNS00NDM5LWEwYmEtZGZhYzA4NDNkZWQzIn0.-4-Ft4jAQNKKTEb_Qm0IDcJUHiDe8y_kjJMnlxd2QkGFP9o3ahFf-kfKwUYhWeJdvAVFzrus_h_gDY2GM2w6dA",  
         "VtexIdclientAutCookie_cashmerehlc": "eyJhbGciOiJFUzI1NiIsImtpZCI6IjQ4RUM2MUNFODdDMTc0MTEwOTM5NzIwQ0M5NUI4NTRBMTEzOTQ3MDciLCJ0eXAiOiJqd3QifQ.eyJzdWIiOiJwcml5YW5zaHUuc2F4ZW5hQG5hZ2Fycm8uY29tIiwiYWNjb3VudCI6ImNhc2htZXJlaGxjIiwiYXVkaWVuY2UiOiJ3ZWJzdG9yZSIsInNlc3MiOiI1OGQwMGM2NC0yMWMwLTRjODktYmQ0MC00OTcxYzNkMDJlYmMiLCJleHAiOjE3NTI4Mjg5MDksInR5cGUiOiJ1c2VyIiwidXNlcklkIjoiZDM2MDIyYzYtNWE4YS00ZDM5LWI0ZDAtOWZjMmFhZTIyNWE3IiwiaWF0IjoxNzUyNzQyNTA5LCJpc1JlcHJlc2VudGF0aXZlIjpmYWxzZSwiaXNzIjoidG9rZW4tZW1pdHRlciIsImp0aSI6ImRkMjEwNTgxLWRmZjItNGMwZC1hNDQ3LWRkYmE3OGVmNTNkYiJ9.Jwo_Kqs8FYj9Q2WVntc0AgJnuCRe12MWC7s20eX5aZtspYawYkhH2zrLusrMB6jM-Lzrex6VOTG8vj9oflQFlg"  
    }

    product_data = []

    for pid in product_ids:
        params = {
            "fields": fields,
            "productId": pid
        }

        response = requests.get(VTEX_BASE_URL, headers=headers, params=params)

        if response.status_code == 200:
            try:
                product_json = response.json()

                # Clean image fields
                product = product_json.get("data", {}).get("product", {})
                default = product.get("basic", {}).get("default", {})
                default.pop("images", None)
                default.pop("allImages", None)

                product_data.append(product_json)
               

            except json.JSONDecodeError:
                logger.warning("Invalid JSON for product ID %s", pid)
        else:
            logger.error("VTEX API failed for ID %s with status code %s", pid, response.status_code)
    
    return product_data

def call_iot_api(ids):
    payload = {
        "product_codes": ids,
    }
    params = {
        "status": "on"
    }
    logger.info("Calling IoT API with payload: %s", payload)
    response = requests.post(IOT_API_URL, params=params,json=payload)

    if response.status_code != 200:
        logger.error("IoT API failed with status code: %s", response.status_code)
        raise Exception(f"IoT API failed: {response.status_code}")
    logger.info("IoT API call successful")
    return response.json()

def handle_request_for_vapi(skin_type: str, concerns: list,recommendation_type: str):
    try:
       
        recommendation_payload = {
            "recommendation_type": recommendation_type,
            "skin_type": skin_type,
            "concerns": concerns,
            "exclusions": ["hair products"],
            "base_product": "cleanser",
            "price": 0,
            "count": 2
        }

        recommendation_response = call_recommendation_api(recommendation_payload)
        product_ids = recommendation_response.get("product_codes", [])

        full_product_data = fetch_product_details_from_vtex(product_ids)
        iot_response = call_iot_api(product_ids)

        return {
            "data": full_product_data,
            "iot_status": "IoT call successful",
            "iot_response": iot_response
        }

    except Exception as e:
        logger.exception("Error occurred while handling VAPI request")
        return {
            "error": str(e),
            "iot_status": "IoT call skipped"
        }
