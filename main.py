# main.py

from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
from helper import handle_request_for_vapi
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

class VapiRequest(BaseModel):
    skin_care: str
    concern: List[str]

@app.post("/api/v1/process-request", tags=["VAPI"])
def process_vapi_input(request: VapiRequest):
    logger.info("Vapi endpoint called")
    response = handle_request_for_vapi(request.skin_care, request.concern)
    logger.info(f"Vapi endpoint response: {response}")
    return response
