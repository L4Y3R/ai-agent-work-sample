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

# Don't print the API key for security
if OPENAI_API_KEY:
    print("OPENAI_API_KEY loaded successfully")
else:
    print("WARNING: OPENAI_API_KEY not found")

client = OpenAI(api_key=OPENAI_API_KEY)

def load_data_files():
    """Load all .ndjson files from the data directory"""
    all_files = glob(os.path.join(DATA_DIR, "*.ndjson"))
    datasets = {}

    for file_path in all_files:
        room_name = os.path.basename(file_path).split('.')[0]
        rows = []
        try:
            with open(file_path, 'r') as f:
                for line in f:
                    try:
                        rows.append(json.loads(line.strip()))
                    except json.JSONDecodeError:
                        continue
            if rows:
                df = pd.DataFrame(rows)
                df = normalize_columns(df)
                datasets[room_name] = df
        except Exception as e:
            print(f"Error loading {file_path}: {e}")

    return datasets

def normalize_columns(df):
    """Normalize column names to standard format"""
    mapping = {
        'co2': ['co2', 'CO2', 'CO2 (ppm)', 'CO2 (PPM)', 'co2_ppm', 'carbon_dioxide'],
        'humidity': ['rh', 'RH', 'Relative Humidity (%)', 'humidity', 'Humidity', 'relative_humidity'],
        'temperature': ['temp', 'Temp', 'Temperature (°C)', 'Temperature (\u00b0C)', 'temperature', 'Temperature'],
        'timestamp': ['timestamp', 'time', 'datetime', 'date_time']
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
    """Create a comprehensive prompt for the LLM"""
    # Build a description of available data
    data_description = "You have air quality data from these rooms:\n"
    for room, df in datasets.items():
        sample_data = df.head(2).to_string(index=False) if not df.empty else "No data"
        data_description += f"- {room}: {len(df)} records, columns: {', '.join(df.columns)}\n"
        data_description += f"  Sample data:\n{sample_data}\n\n"

    prompt_template = f"""
{data_description}

You are an AI assistant that analyzes air quality data. Write Python code to answer the user's question.

IMPORTANT GUIDELINES:
1. The DataFrames are available as variables named exactly like the room names (e.g., 'Room_1', 'Room_2', etc.)
2. All DataFrames have standardized columns: 'timestamp', 'co2', 'temperature', 'humidity'
3. Always work with copies of DataFrames to avoid pandas warnings: df = df.copy()
4. Always convert timestamps properly: df['timestamp'] = pd.to_datetime(df['timestamp'])
5. For time-based analysis, use pandas datetime operations
6. Your final output should be either:
   - A pandas DataFrame (assign to variable 'result')
   - A descriptive string (assign to variable 'result')
7. Round numeric values to 2 decimal places for readability
8. Handle missing data gracefully
9. Use .loc[] for setting values to avoid pandas warnings

EXAMPLES:

Example 1 - Hourly temperature analysis:
```python
# Combine all room data
all_rooms = []
room_names = [name for name in locals().keys() if 'Room' in name]

for room_name in room_names:
    if room_name in locals():
        df = locals()[room_name].copy()
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df.loc[:, 'room'] = room_name
        all_rooms.append(df)

if all_rooms:
    combined = pd.concat(all_rooms, ignore_index=True)
    combined.loc[:, 'hour'] = combined['timestamp'].dt.hour
    hourly_temp = combined.groupby('hour')['temperature'].mean().reset_index()
    hourly_temp.loc[:, 'temperature'] = hourly_temp['temperature'].round(2)
    result = hourly_temp
else:
    result = "No data available"
```

Example 2 - Room comparison:
```python
room_stats = []
room_names = [name for name in locals().keys() if 'Room' in name]

for room_name in room_names:
    if room_name in locals():
        df = locals()[room_name].copy()
        avg_temp = df['temperature'].mean()
        if not pd.isna(avg_temp):
            room_stats.append({{'Room': room_name, 'Average_Temperature': round(avg_temp, 2)}})

if room_stats:
    result = pd.DataFrame(room_stats)
else:
    result = "No room data available"
```

User Question: "{user_query}"

Write Python code to answer this question. Remember to use .copy() and .loc[] to avoid pandas warnings:
"""
    return prompt_template

def run_openai_code_agent(datasets, user_query):
    """Generate Python code using OpenAI to answer the user query"""
    prompt = create_prompt(datasets, user_query)
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful assistant who writes Python code to analyze air quality data. Always ensure your code is complete, handles edge cases, and avoids pandas warnings by using .copy() and .loc[] appropriately."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1
        )
        code = response.choices[0].message.content

        # Extract the code block if returned as markdown
        if "```python" in code:
            code = code.split("```python")[1].split("```")[0].strip()
        elif "```" in code:
            code = code.split("```")[1]
            if code.startswith("python"):
                code = code[len("python"):].strip()
            code = code.strip()

        # Add necessary imports
        safe_boilerplate = """
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import pytz
import warnings
warnings.filterwarnings('ignore', category=pd.errors.SettingWithCopyWarning)
"""

        final_code = safe_boilerplate + "\n\n" + code
        final_code = textwrap.dedent(final_code)

        return final_code

    except Exception as e:
        return f"Error calling OpenAI API: {str(e)}"

def execute_user_code(code: str, datasets: dict):
    """Execute the generated code safely with the datasets"""
    # Prepare the local environment with datasets as variables
    local_env = {}
    for room, df in datasets.items():
        var_name = room.replace(" ", "_").replace(".", "_").replace("-", "_")
        if var_name.startswith("sensor_data_"):
            var_name = var_name[len("sensor_data_"):]
        # Make a copy to avoid pandas warnings
        local_env[var_name] = df.copy()

    # Add timezone utilities
    utc = pytz.UTC
    local_env['utc'] = utc

    # Redirect stdout to capture prints
    stdout = io.StringIO()
    sys_stdout = sys.stdout
    sys.stdout = stdout

    result = None
    error = None

    try:
        exec(code, {"__builtins__": __builtins__}, local_env)
        if 'result' in local_env:
            result = local_env['result']
        else:
            printed_output = stdout.getvalue().strip()
            result = printed_output if printed_output else "Code executed successfully but no result was returned."
    except Exception as e:
        error = str(e) + "\n" + traceback.format_exc()
    finally:
        sys.stdout = sys_stdout

    if error:
        return {"success": False, "error": error}
    
    if isinstance(result, pd.DataFrame):
        return {
            "success": True,
            "type": "dataframe",
            "data": result.to_dict(orient="records"),
            "columns": list(result.columns)
        }
    elif isinstance(result, (str, int, float)):
        return {
            "success": True,
            "type": "text",
            "data": str(result)
        }
    else:
        return {
            "success": True,
            "type": "text",
            "data": str(result)
        }