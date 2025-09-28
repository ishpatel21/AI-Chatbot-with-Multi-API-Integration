from fastapi import FastAPI, Request
from dotenv import load_dotenv
from openai import OpenAI, OpenAIError
import asyncio
import aiohttp
import json
import os

load_dotenv()

app = FastAPI()

# 🔹 API Registry
API_REGISTRY = [
    {"name": "OrderAPI", "url": "http://localhost:8001/order", "description": "Fetch order details"},
    {"name": "PaymentAPI", "url": "http://localhost:8001/payment", "description": "Fetch payment info"},
    {"name": "PatientAPI", "url": "http://localhost:8001/patient", "description": "Fetch patient details"},
    {"name": "LabAPI", "url": "http://localhost:8001/lab", "description": "Fetch lab test results"}
]

# 🔹 Initialize OpenAI client (reads API key from env: OPENAI_API_KEY)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# 🔹 Async API Caller with error handling
async def call_api(session, api, patient_id):
    try:
        async with session.get(f"{api['url']}?patientId={patient_id}") as response:
            if response.status == 200:
                return {api["name"]: await response.json()}
            else:
                return {api["name"]: {"error": f"API returned status {response.status}"}}
    except Exception as e:
        return {api["name"]: {"error": str(e)}}

# 🔹 LLM decides which APIs to call
def choose_apis_with_llm(user_question: str):
    registry_text = "\n".join([f"{a['name']}: {a['description']}" for a in API_REGISTRY])
    prompt = f"""
    You are an API orchestrator.
    User asked: "{user_question}"

    Available APIs:
    {registry_text}

    Which APIs are required? 
    Return ONLY a JSON array of API names, like: ["OrderAPI", "PaymentAPI"]
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )
        content = response.choices[0].message.content.strip()

        # Safe JSON parsing
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            # fallback: try to extract JSON-like substring
            start = content.find("[")
            end = content.rfind("]") + 1
            if start != -1 and end != -1:
                try:
                    return json.loads(content[start:end])
                except Exception:
                    return []
            return []
    except OpenAIError as e:
        print("OpenAI error:", e)
        return []

# 🔹 LLM rephrases the final response
def rephrase_with_llm(user_question: str, data: dict):
    prompt = f"""
    The user asked: "{user_question}"
    
    Here is the raw API data:
    {json.dumps(data, indent=2)}

    👉 Your job:
    - Summarize this data into a clear, conversational answer.
    - DO NOT include raw JSON in your response.
    - Speak like a helpful assistant explaining results to a human.
    - If there are multiple APIs, combine the info naturally in one answer.
    - Example: Instead of showing raw JSON, say something like:
      "The order #12345 was placed on Sept 10 for an X-ray Scan. Payment of $199.99 has already been received."
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.5
    )

    return response.choices[0].message.content.strip()
    
# 🔹 Main Chat Endpoint
@app.post("/chat")
async def chat(req: Request):
    try:
        body = await req.json()
    except Exception:
        return {"error": "Invalid or missing JSON body"}

    user_question = body.get("question")
    patient_id = body.get("patientId", "123")

    if not user_question:
        return {"error": "Missing 'question' in request body"}

    # Step 1: Determine APIs
    apis_to_call = choose_apis_with_llm(user_question)

    # Step 2: Fetch APIs in parallel
    async with aiohttp.ClientSession() as session:
        tasks = [call_api(session, api, patient_id) for api in API_REGISTRY if api["name"] in apis_to_call]
        results = await asyncio.gather(*tasks)

    # Step 3: Aggregate
    combined = {}
    for result in results:
        combined.update(result)

    # Step 4: Rephrase
    reply = rephrase_with_llm(user_question, combined)
    return {"answer": reply, "data": combined}