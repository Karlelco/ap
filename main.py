from fastapi import FastAPI, HTTPException, Header, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import requests
import base64
from typing import Optional
import os


port = int(os.environ.get("PORT", 10000))

app = FastAPI(title="M-Pesa Gateway API", description="Simplified M-Pesa Integration for Websites", version="1.0.0")

BASE_URL = "https://sandbox.safaricom.co.ke"  # Change to production for live

# Mount static directory for CSS
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/generate-token", summary="Generate M-Pesa Access Token")
def generate_token(consumer_key: str, consumer_secret: str):
    """
    Generate an M-Pesa access token using a consumer key and secret.
    """
    credentials = f"{consumer_key}:{consumer_secret}"
    encoded_credentials = base64.b64encode(credentials.encode()).decode()

    headers = {
        "Authorization": f"Basic {encoded_credentials}"
    }

    url = f"{BASE_URL}/oauth/v1/generate?grant_type=client_credentials"
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        raise HTTPException(status_code=500, detail=response.text)

@app.post("/stk-push", summary="Initiate STK Push")
def stk_push(
    access_token: str = Header(...),
    BusinessShortCode: str = "174379",
    Password: str = "",
    Timestamp: str = "",
    TransactionType: str = "CustomerPayBillOnline",
    Amount: int = 1,
    PartyA: str = "",
    PartyB: str = "174379",
    PhoneNumber: str = "",
    CallBackURL: str = "https://yourdomain.com/callback",
    AccountReference: str = "Test123",
    TransactionDesc: str = "Test Payment"
):
    """
    Initiates an STK Push request to the M-Pesa API.
    """
    url = f"{BASE_URL}/mpesa/stkpush/v1/processrequest"

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    payload = {
        "BusinessShortCode": BusinessShortCode,
        "Password": Password,
        "Timestamp": Timestamp,
        "TransactionType": TransactionType,
        "Amount": Amount,
        "PartyA": PartyA,
        "PartyB": PartyB,
        "PhoneNumber": PhoneNumber,
        "CallBackURL": CallBackURL,
        "AccountReference": AccountReference,
        "TransactionDesc": TransactionDesc
    }

    response = requests.post(url, headers=headers, json=payload)

    if response.status_code == 200:
        return response.json()
    else:
        raise HTTPException(status_code=response.status_code, detail=response.text)

@app.get("/health", summary="API Health Check")
def health_check():
    return {"status": "M-Pesa Gateway API is running."}

@app.get("/", response_class=HTMLResponse, summary="HTML Guide")
def docs_guide():
    try:
        with open("templates/index.html", "r") as file:
            html_content = file.read()
        return HTMLResponse(content=html_content, status_code=200)
    except FileNotFoundError:
        return HTMLResponse(content="<h1>Guide Not Found</h1>", status_code=404)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)