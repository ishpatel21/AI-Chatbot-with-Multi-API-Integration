# AI Chatbot with Multi-API Integration
This project demonstrates a chatbot that fetches data from multiple APIs (Order, Payment, Patient, Lab, etc.) and returns a friendly, natural language response using OpenAI GPT models.
It dynamically decides which APIs to call based on the user query and aggregates results in a structured format before generating a user-friendly reply.

## Features:
Handles dynamic user queries
Detects which APIs are required per request
Fetches data from multiple APIs in parallel
Aggregates responses into structured JSON
Uses OpenAI GPT models to generate natural, friendly responses
Easy to extend by adding new APIs to the registry

## Setup
1. Clone the repository
- git clone https://github.com/yourusername/multi-api-chatbot.git
- cd multi-api-chatbot
2. Create a virtual environment
- python3 -m venv venv
- source venv/bin/activate     # Mac/Linux
- venv\Scripts\activate        # Windows
3. Install dependencies
- pip install -r requirements.txt
4. Set your OpenAI API key
- export OPENAI_API_KEY="sk-xxxxxx"   # Mac/Linux
- setx OPENAI_API_KEY "sk-xxxxxx"     # Windows PowerShell

## Running the App:
1. Start the mock APIs (for testing without real services)
- uvicorn mock_apis:mock_app --host 0.0.0.0 --port 8001 --reload
2. Start the chatbot server
- uvicorn app:app --host 0.0.0.0 --port 8000 --reload
3. Access API docs
- Open your browser: http://localhost:8000/docs

## cURL Request:
% curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"question": "Can I get my order receipt?", "patientId": "123"}'

cURL Response:
{"answer":"Sure! Your order #12345 was placed on September 10, 2025, for an X-ray Scan. The total amount of $199.99 has been paid successfully. If you need any more information or assistance, feel free to ask!","data":{"OrderAPI":{"orderId":"12345","date":"2025-09-10","items":["X-ray Scan"]},"PaymentAPI":{"amount":"199.99","status":"Paid"}}}%                            

## requirements.txt:
- fastapi
- uvicorn
- aiohttp
- openai>=1.0.0

## Future Improvements:
- Integrate vector search for FAQ or knowledge base queries
- Cache frequent API responses for speed
- Add authentication for sensitive APIs
- Extend AI logic for multi-turn conversations

Built with ❤️ as a demo project for multi-API chatbot integration with OpenAI GPT models.
