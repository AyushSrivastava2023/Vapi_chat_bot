import requests
import json
import logging

# Setup logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

RECOMMENDATION_API_URL = "http://44.213.132.172:8000/api/v1/recommend"
VTEX_API_URL = "https://webhook.site/f1ad94eb-92d3-45e1-82b5-226fd68cdde4"
IOT_API_URL = "https://webhook.site/ce0c97ac-e18e-45f6-bc39-9d1ac7282663"

def call_recommendation_api(payload):
    logger.info("Calling Recommendation API with payload: %s", payload)
    response = requests.post(RECOMMENDATION_API_URL, json=payload)
    if response.status_code != 200:
        logger.error("Recommendation API failed with status code: %s", response.status_code)
        raise Exception(f"Recommendation API failed: {response.status_code}")
    logger.info("Received response from Recommendation API")
    return response.json()

def fetch_product_details_from_vtex(product_ids):
    logger.info("Fetching product details from VTEX for product IDs: %s", product_ids)
    product_data = []
    for pid in product_ids:
        response = requests.post(VTEX_API_URL, json={"id": pid})
        if response.status_code == 200:
            logger.info("VTEX response success for product ID: %s", pid)
            product_data.append(response.json())
        else:
            logger.error("VTEX API failed for ID %s with status %s", pid, response.status_code)
    return product_data

def call_iot_api(ids):
    payload = {
        "iot_tracking_ids": ids,
        "event": "recommendation_sent"
    }
    logger.info("Calling IoT API with payload: %s", payload)
    response = requests.post(IOT_API_URL, json=payload)
    if response.status_code != 200:
        logger.error("IoT API failed with status code: %s", response.status_code)
        raise Exception(f"IoT API failed: {response.status_code}")
    logger.info("IoT API call successful")
    return response.json()

def handle_request_for_vapi(skin_type: str, concerns: list):
    try:
        logger.info("Handling VAPI request with skin_type: %s and concerns: %s", skin_type, concerns)

        recommendation_payload = {
            "recommendation_type": "skincare",
            "skin_type": skin_type,
            "concerns": concerns,
            "exclusions": ["hair products"],
            "base_product": "cleanser",
            "price": 0,
            "count": 2
        }

        recommendation_response = call_recommendation_api(recommendation_payload)
        product_ids = recommendation_response.get("product_codes", [])

        logger.info("Product IDs received: %s", product_ids)

        full_product_data = fetch_product_details_from_vtex(product_ids)
        iot_response = call_iot_api(product_ids)

        logger.info("Request handling complete")

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
