import json

from constants import MAX_BATCH_SIZE

def generate_prompt(config, ref_data, column_names, expected_columns):

    """Construct the LLM prompt dynamically."""
    num_rows = MAX_BATCH_SIZE

    if config: 
        user_prompt = config.get("prompt", [""])[0]  # Extract user-given text
        column_definitions = "\n".join(
            [f"- {col['name']} ({col['type']})" for col in config.get('columns', [])]
        )
    
    elif not ref_data.empty:
        user_prompt = """Generate a csv file"""
        column_definitions = column_names


    prompt = f"""
    Generate {num_rows} unique rows of synthetic data in CSV format with these columns:
    {column_definitions}

    **Rules:**

    - Data format: CSV only.
    - Rows must be unique; columns need not be unique.
    - Include at least one primary key.
    - Ensure the data follows a realistic pattern.
    - Strings shouldn't be in quotes. Ex: ('""user101"" -->incorrect, user101  --> correct)
    - **Replicate the pattern in reference data**
    - Take count of rows form the user instruction.
    - **Each row must contain exactly {expected_columns} values. No missing or extra fields.**
    - **Output format: Only comma-separated values (NO HEADER, NO EXTRA TEXT).**'
    - **Ensure CSV output has NO extra text, NO headers, NO extra spacing, and is STRICTLY comma-separated.**
    - **No excessive quotation marks unless necessary for escaping commas in text fields.**



    ----
    - User instruction: {user_prompt}
    """
    return prompt.strip()
