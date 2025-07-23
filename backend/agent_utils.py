from dotenv import load_dotenv
load_dotenv()

import os
import io
import sys
import json
import pandas as pd
from openai import OpenAI
import traceback
from glob import glob
from datetime import datetime, timedelta
import pytz
import textwrap

DATA_DIR = "./data/"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
print("OPENAI_API_KEY =", OPENAI_API_KEY)


client = OpenAI(api_key=OPENAI_API_KEY)

def load_data_files():
    all_files = glob(os.path.join(DATA_DIR, "*.ndjson"))
    datasets = {}

    for file_path in all_files:
        room_name = os.path.basename(file_path).split('.')[0]
        rows = []
        with open(file_path, 'r') as f:
            for line in f:
                rows.append(json.loads(line.strip()))
        df = pd.DataFrame(rows)
        df = normalize_columns(df)
        datasets[room_name] = df

    return datasets

def normalize_columns(df):
    mapping = {
        'co2': ['co2', 'CO2', 'CO2 (ppm)'],
        'humidity': ['rh', 'RH', 'Relative Humidity (%)'],
        'temperature': ['temp', 'Temp', 'Temperature (°C)', 'Temperature (\u00b0C)'],
        'timestamp': ['timestamp']
    }

    col_map = {}
    for standard_name, variants in mapping.items():
        for variant in variants:
            for col in df.columns:
                if variant.lower() == col.lower():
                    col_map[col] = standard_name
                    break
            if standard_name in col_map.values():
                break

    df = df.rename(columns=col_map)

    # Convert timestamp column to datetime dtype if it exists
    if 'timestamp' in df.columns:
        df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')

    return df


def create_prompt(datasets, user_query):
    # Build a description of available data
    data_description = "You have air quality data from these rooms:\n"
    for room, df in datasets.items():
        data_description += f"- {room} with columns: {', '.join(df.columns)}\n"
    data_description += "\n"
    
    prompt = (
        f"{data_description}"
        "Write Python code that uses pandas DataFrames named as the room names (e.g. Room_1) to answer this question:\n"
        f"\"\"\"\n{user_query}\n\"\"\"\n"
        "When filtering by dates, use timezone-aware datetime objects as follows:\n"
        "from datetime import datetime, timedelta\n"
        "import pytz\n"
        "utc = pytz.UTC\n"
        "end_date = (datetime.now() - timedelta(days=datetime.now().weekday() + 1)).replace(tzinfo=pytz.utc)\n"
        "start_date = end_date - timedelta(days=7)\n"
        "Your code should print the answer or a pandas DataFrame as the final result.\n"
        "Do not import libraries or redefine the DataFrames. Only write the code to analyze.\n"
        "If you can't answer, print 'Cannot answer this query.'"
    )
    return prompt

def run_openai_code_agent(datasets, user_query):
    prompt = create_prompt(datasets, user_query)
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful assistant who writes python code to analyze air quality data."},
                {"role": "user", "content": prompt}
            ],
            temperature=0
        )
        code = response.choices[0].message.content

        # Extract the code block if returned as markdown
        if "```" in code:
            code = code.split("```")[1]
            if code.startswith("python"):
                code = code[len("python"):].strip()
            code = code.strip()

        # Prepend safe boilerplate imports
        safe_boilerplate = """
from datetime import datetime, timedelta
import pytz
import pandas as pd
"""
        final_code = safe_boilerplate + "\n\n" + code

        # Dedent to remove leading spaces from all lines
        final_code = textwrap.dedent(final_code)

        return final_code

    except Exception as e:
        return f"Error calling OpenAI API: {str(e)}"

    
def execute_user_code(code: str, datasets: dict):
    from datetime import datetime, timedelta
    import pytz

    # Prepare the local environment with datasets as variables
    local_env = {}
    for room, df in datasets.items():
        var_name = room.replace(" ", "_").replace(".", "_")
        if var_name.startswith("sensor_data_"):
            var_name = var_name[len("sensor_data_"):]
        local_env[var_name] = df.copy()

    # Add timezone-aware start_date and end_date to local_env
    utc = pytz.UTC
    end_date = (datetime.now() - timedelta(days=datetime.now().weekday() + 1)).replace(tzinfo=utc)
    start_date = end_date - timedelta(days=7)

    local_env['start_date'] = start_date
    local_env['end_date'] = end_date

    # Redirect stdout to capture prints
    stdout = io.StringIO()
    sys_stdout = sys.stdout
    sys.stdout = stdout

    result = None
    error = None

    try:
        exec(code, {}, local_env)
        if 'result' in local_env:
            result = local_env['result']
        else:
            result = stdout.getvalue()
    except Exception as e:
        error = str(e) + "\n" + traceback.format_exc()
    finally:
        sys.stdout = sys_stdout

    if error:
        return {"error": error}
    if isinstance(result, pd.DataFrame):
        return {"dataframe": result.to_dict(orient="records")}
    if isinstance(result, str):
        return {"text": result}
    return {"text": str(result)}
