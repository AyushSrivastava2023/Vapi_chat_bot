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

# # Data
concerns = sorted(set([
    "Dryness", "Dullness", "Dehydration", "Sensitivity", "Redness", "Excess Oil","Congestion","Pollution","fatigue"
]))
 
skin_types = [
    "All Skin Types", "Combination", "Oily", "Normal", "Dry Skin", "Sensitive Skin","Dull","Depleted","Mature"
]
 
from pydantic import BaseModel

class OptionsRequest(BaseModel):
    type: Literal["concern", "skintype"]

@app.post("/options",)
async def get_options(request: OptionsRequest):
    """
    Returns a list of skincare concerns or skin types based on the body param.
    Example body:
    {
      "type": "concern"
    }
    """
    logger.info(f"Request received for type: {request.type}")
 
    if request.type == "concern":
        logger.info("Returning concerns list.")
        return {"options": concerns}
    else:
        logger.info("Returning skin types list.")
        return {"options": skin_types}
