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

def fetch_product_details_from_vtex(product_ids, fields="basic"):
    VTEX_BASE_URL = "https://dev.showcase-cashmere.store/api/ccs/product-details"

    logger.info("Fetching product details from VTEX for product IDs: %s", product_ids)
    def try_fetch(pid):
        params = {
            "fields": fields,
            "productId": pid
        }

        try:
            response = requests.get(VTEX_BASE_URL, params=params)

            if response.status_code == 200:
                product_json = response.json()
                basic = product_json.get("data", {}).get("product", {}).get("basic", {})

                default = basic.get("default", {})
                default.pop("images", None)
                default.pop("allImages", None)
                default.pop("sellerId", None)
                default.pop("listPrice", None)
                
                productinfo = product_json.get("data", {}).get("product", {}).get("basic", {})
                productinfo.pop("productReference", None)
                productinfo.pop("brandId", None)
                productinfo.pop("titleTag", None)
                productinfo.pop("metaTagDescription", None)
                productinfo.pop("benefits", None) 
                productinfo.pop("releaseDate", None)
                productinfo.pop("productClusters", None)
                productinfo.pop("link", None)
                productinfo.pop("linkText", None)


                return productinfo
            else:
                logger.warning("VTEX API failed for ID %s with status %s", pid, response.status_code)
        except Exception as e:
            logger.warning("Exception while fetching VTEX product ID %s: %s", pid, str(e))

        return None

    product_data = []
    for pid in product_ids:
        result = try_fetch(pid)
        if result is None:
            logger.info("Retrying VTEX API for product ID %s", pid)
            result = try_fetch(pid)

        if result:
            product_data.append(result)
        else:
            logger.error("Final failure fetching VTEX product ID %s", pid)

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

def handle_request_for_vapi(
    skin_type: str = "dry",
    concerns: list = None,
    recommendation_type: str = "skincare"
):
    try:
        if concerns is None:
            concerns = []
 
        recommendation_payload = {
            "recommendation_type": recommendation_type,
            "skin_type": skin_type,
            "concerns": concerns,
            "count": 4
        }
 
        recommendation_response = call_recommendation_api(recommendation_payload)
        product_ids = recommendation_response.get("product_codes", [])
 
        logger.info("Received product IDs from recommendation API: %s", product_ids)
        logger.info("Recommendation payload: %s", recommendation_payload)
 
        full_product_data = fetch_product_details_from_vtex(product_ids)
 
        # 🧠 IoT API call handled safely
        iot_status = "IoT call successful"
        iot_response = None
        try:
            iot_response = call_iot_api(product_ids)
        except Exception as iot_error:
            logger.error("IoT API call failed: %s", str(iot_error))
            iot_status = "IoT call failed"
 
        return {
            "data": full_product_data,
            "iot_status": iot_status,
            "iot_response": iot_response
        }
 
    except Exception as e:
        logger.exception("Error occurred while handling VAPI request")
        return {
            "error": str(e),
            "iot_status": "IoT call skipped"
        }
