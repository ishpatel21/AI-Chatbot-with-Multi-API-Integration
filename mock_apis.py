from fastapi import FastAPI
from fastapi.responses import JSONResponse

mock_app = FastAPI()

@mock_app.get("/order")
async def get_order(patientId: str):
    return {"orderId": "12345", "date": "2025-09-10", "items": ["X-ray Scan"]}

@mock_app.get("/payment")
async def get_payment(patientId: str):
    return {"amount": "199.99", "status": "Paid"}

@mock_app.get("/patient")
async def get_patient(patientId: str):
    return {"patientId": patientId, "name": "John Doe", "insurance": "BlueCross"}

@mock_app.get("/lab")
async def get_lab(patientId: str):
    return {"labTest": "Blood Test", "result": "Normal"}
