# main.py

from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
from helper import handle_request_for_vapi
import logging
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, Query
from typing import List, Literal

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 🔓 Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # 🔓 Allows all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],  # 🔓 Allows all headers
)
class VapiRequest(BaseModel):
    skin_care: str
    concern: List[str]
    recommendation_type: str

@app.post("/api/v1/process-request", tags=["VAPI"])
def process_vapi_input(request: VapiRequest):
    response = handle_request_for_vapi(request.skin_care, request.concern,request.recommendation_type)
    logger.info(f"Vapi endpoint response: {response}")
    return response


# Data
concerns = sorted(set([
    "Dryness", "Dullness", "Dehydration", "Sensitivity", "Redness", "Excess Oil"
]))
 
skin_types = [
    "All Skin Types", "Combination", "Oily", "Normal", "Dry Skin", "Sensitive Skin"
]
 
@app.get("/options", response_model=List[str])
async def get_options(
    type: Literal["concern", "skintype"] = Query(..., description="Specify 'concern' or 'skintype'")
):
    """
    Returns a list of skincare concerns or skin types based on the query param.
    Example: /options?type=concern or /options?type=skintype
    """
    logger.info(f"Request received for type: {type}")
 
    if type == "concern":
        logger.info("Returning concerns list.")
        return concerns
    else:
        logger.info("Returning skin types list.")
        return skin_types
