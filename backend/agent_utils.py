from dotenv import load_dotenv
load_dotenv()

import re
import os
import io
import sys
import json
import pandas as pd
import numpy as np
from openai import OpenAI
import traceback
from glob import glob
from datetime import datetime, timedelta
import pytz
import textwrap
from logging_config import setup_logger
from utils import is_query_valid

logger = setup_logger(__name__)

DATA_DIR = "./data/"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if OPENAI_API_KEY:
    logger.info("OPENAI_API_KEY loaded successfully")
else:
    logger.error("OPENAI_API_KEY not found")

client = OpenAI(api_key=OPENAI_API_KEY)

def format_display_name(name):
    """Convert underscore names to readable format"""
    # Handle special cases and common patterns
    name = str(name)
    
    # Replace underscores with spaces
    formatted = name.replace('_', ' ')
    
    # Title case each word
    formatted = formatted.title()
    
    # Handle special cases for better readability
    replacements = {
        'Co2': 'CO2',
        'Avg': 'Average',
        'Min': 'Minimum',
        'Max': 'Maximum',
        'Temp': 'Temperature',
        'Rh': 'Humidity'
    }
    
    for old, new in replacements.items():
        formatted = formatted.replace(old, new)
    
    return formatted

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
            logger.error(f"Error loading {file_path}: {e}")

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

    if 'timestamp' in df.columns:
        df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')

    logger.info("Column normalization completed")
    return df

def create_prompt(datasets, user_query):
    """Create a comprehensive prompt for the LLM"""
    
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
5. **CRITICAL**: When comparing timestamps, ensure timezone consistency:
   - Use pd.Timestamp with timezone: pd.Timestamp('2025-07-19', tz='UTC')
   - Or make timestamps timezone-naive: df['timestamp'].dt.tz_localize(None)
   - Or use datetime with timezone: datetime(2025, 7, 19, tzinfo=pytz.UTC)
6. For time-based analysis, use pandas datetime operations
7. Your final output should be either:
   - A pandas DataFrame (assign to variable 'result')
   - A descriptive string (assign to variable 'result')
8. Round numeric values to 2 decimal places for readability
9. Handle missing or unavailable data gracefully, do not retun null.
10. Use .loc[] for setting values to avoid pandas warnings
11. **FORMATTING**: Use clean, readable column names without underscores. Use spaces and proper capitalization.
    - Good: 'Room Name', 'Average Temperature', 'Morning Average'
    - Bad: 'room_name', 'avg_temp', 'morning_avg'

EXAMPLES:

Example 1 - Last week analysis (timezone-aware):
```python
# Get current time in UTC
now = pd.Timestamp.now(tz='UTC')
one_week_ago = now - pd.Timedelta(days=7)

# Combine all room data
all_rooms = []
room_names = [name for name in locals().keys() if 'Room' in name]

for room_name in room_names:
    if room_name in locals():
        df = locals()[room_name].copy()
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        # Ensure timezone consistency
        if df['timestamp'].dt.tz is None:
            df['timestamp'] = df['timestamp'].dt.tz_localize('UTC')
        
        # Filter for last week
        last_week_data = df[df['timestamp'] >= one_week_ago]
        if not last_week_data.empty:
            last_week_data.loc[:, 'Room Name'] = room_name.replace('_', ' ')
            all_rooms.append(last_week_data)

if all_rooms:
    combined = pd.concat(all_rooms, ignore_index=True)
    # Your analysis here
    result = combined
else:
    result = "No data available for the last week"
```

Example 2 - Room comparison with clean formatting:
```python
room_stats = []
room_names = [name for name in locals().keys() if 'Room' in name]

for room_name in room_names:
    if room_name in locals():
        df = locals()[room_name].copy()
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        # Handle timezone
        if df['timestamp'].dt.tz is None:
            df['timestamp'] = df['timestamp'].dt.tz_localize('UTC')
        
        avg_temp = df['temperature'].mean()
        if not pd.isna(avg_temp):
            room_stats.append({{'Room Name': room_name.replace('_', ' '), 'Average Temperature': round(avg_temp, 2)}})

if room_stats:
    result = pd.DataFrame(room_stats)
else:
    result = "No room data available"
```

User Question: "{user_query}"

Write Python code to answer this question. Remember to:
- Handle timezone-aware timestamps properly
- Use clean, readable column names with spaces instead of underscores
- Format room names nicely (e.g., "Room 1" instead of "Room_1")
"""
    return prompt_template

def run_openai_code_agent(datasets, user_query):
    """Generate Python code using OpenAI to answer the user query"""

    if not is_query_valid(user_query):
        return {
            "success": False,
            "type": "text",
            "data": "Sorry, I couldn't understand your question. Please try rephrasing it."
        }

    prompt = create_prompt(datasets, user_query)
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful assistant who writes Python code to analyze air quality data. Always ensure your code handles timezone-aware timestamps properly and avoids pandas warnings by using .copy() and .loc[] appropriately. Use clean, readable column names without underscores."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.4
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

        # Add necessary imports with timezone utilities
        safe_boilerplate = """
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import pytz
import warnings
warnings.filterwarnings('ignore', category=pd.errors.SettingWithCopyWarning)

# Timezone utilities
utc = pytz.UTC
"""

        final_code = safe_boilerplate + "\n\n" + code
        final_code = textwrap.dedent(final_code)

        return final_code

    except Exception as e:
        return f"Error calling OpenAI API: {str(e)}"

def format_dataframe_for_display(df):
    """Format DataFrame columns and content for display"""
    if not isinstance(df, pd.DataFrame):
        return df
    
    display_df = df.copy()
    
    # Format column names
    new_columns = {}
    for col in display_df.columns:
        new_columns[col] = format_display_name(col)
    
    display_df = display_df.rename(columns=new_columns)
    
    # Format room names in data if there's a room-related column
    for col in display_df.columns:
        if 'room' in col.lower():
            display_df[col] = display_df[col].apply(lambda x: format_display_name(x) if pd.notna(x) else x)
    
    return display_df

def clean_variable_name(name: str) -> str:
    """Sanitize dataset variable names for code execution"""
    var_name = name.replace(" ", "_").replace(".", "_").replace("-", "_")
    if var_name.startswith("sensor_data_"):
        var_name = var_name[len("sensor_data_"):]
    return var_name

def execute_user_code(code: str, datasets: dict):
    """Execute the generated code safely with the datasets"""

    # Prepare the local environment with datasets as variables
    local_env = {}
    for room, df in datasets.items():
        var_name = clean_variable_name(room)
        local_env[var_name] = df.copy()

    # Add timezone and pandas/numpy utilities
    local_env['utc'] = pytz.UTC
    local_env['pd'] = pd
    local_env['np'] = np
    local_env['datetime'] = datetime
    local_env['timedelta'] = timedelta
    local_env['pytz'] = pytz

    stdout = io.StringIO()
    sys_stdout = sys.stdout
    sys.stdout = stdout

    result = None
    error = None

    try:
        # Check if code is actually an error response from run_openai_code_agent
        if isinstance(code, dict):
            if code.get("success") == False:
                return code  # Return the error dict as-is
            else:
                return {"success": False, "data": "Invalid code format received"}
        
        if not isinstance(code, str):
            return {"success": False, "data": f"Generated code is not a string, got {type(code)}"}

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
        return {"success": False, "data": error}
    
    if isinstance(result, pd.DataFrame):
        formatted_df = format_dataframe_for_display(result)
        return {
            "success": True,
            "type": "dataframe",
            "data": formatted_df.to_dict(orient="records"),
            "columns": list(formatted_df.columns)
        }

    elif isinstance(result, (str, int, float)):
        formatted_result = str(result)
        formatted_result = re.sub(
            r'\b(\w+)_(\w+)\b',
            lambda m: format_display_name(f"{m.group(1)}_{m.group(2)}"),
            formatted_result
        )
        return {
            "success": True,
            "type": "text",
            "data": formatted_result
        }

    else:
        return {
            "success": True,
            "type": "text",
            "data": str(result)
        }