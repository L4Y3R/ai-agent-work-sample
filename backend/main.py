from dotenv import load_dotenv
load_dotenv()

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from agent_utils import load_data_files, run_openai_code_agent, execute_user_code
from logging_config import setup_logger

logger = setup_logger(__name__)
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Query(BaseModel):
    query: str

@app.on_event("startup")
def load_data():
    global datasets
    datasets = load_data_files()
    logger.info("Datasets loaded on startup")

@app.post("/query")
def process_query(request: Query) -> dict:
    try:
        logger.info(f"Received query: {request.query}")
        code = run_openai_code_agent(datasets, request.query)
        if isinstance(code, dict) and not code.get("success"):
            return {"output": code}
            
        output = execute_user_code(code, datasets)
        logger.info(f"Returned output: {output}")
        return {"output": output}
    except Exception as e:
        logger.error(f"Unexpected error processing query: {str(e)}\n{traceback.format_exc()}")
        return {
            "output": {
                "success": False,
                "type": "text",
                "data": "An unexpected error occurred. Our team has been notified."
            }
        }