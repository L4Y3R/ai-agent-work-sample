from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from agent_utils import load_data_files, run_openai_code_agent, execute_user_code
import os
from dotenv import load_dotenv

load_dotenv()


app = FastAPI()

@app.get("/")
def root():
    return {"message": "Backend running!"}

class Query(BaseModel):
    query: str

@app.post("/query")
def process_query(request: Query):
    datasets = load_data_files()
    user_query = request.query

    # Get code from LLM
    code = run_openai_code_agent(datasets, user_query)
    
    # Execute code
    output = execute_user_code(code, datasets)
    
    return {"code": code, "output": output}


# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
