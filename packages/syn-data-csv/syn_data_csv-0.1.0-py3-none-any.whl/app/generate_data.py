import pandas as pd
import csv

from generate_text_prompt import generate_prompt
from ai_accelerators import generate_text_from_llm
from constants import MAX_DEFAULT_ROWS, MAX_BATCH_SIZE

def _extract_total_rows_columns(config, ref_data):
    
    if config and "row_count" in config:
        try:
            return int((config.get("row_count", MAX_DEFAULT_ROWS))[0])
        except ValueError:
            print("⚠️  Invalid row_count in config. Using default.")
    
    # Fallback if no config or invalid value
    return MAX_DEFAULT_ROWS

def _get_columns(config, ref_data):

    if config and "columns" in config:
        column_names = [col["name"] for col in config["columns"]]
        expected_columns = len(column_names)

    elif not ref_data.empty:
        column_names = ref_data.columns.tolist()
        expected_columns = len(column_names)

    return column_names, expected_columns

    
def generate_synthetic_data(config, ref_data, api_key, model):
    """Generate synthetic data in batches while ensuring valid CSV format."""

    total_rows = _extract_total_rows_columns(config, ref_data)
    column_names, expected_columns = _get_columns(config, ref_data)
    
    max_rows_per_batch = MAX_BATCH_SIZE  # Limit per batch
    total_generated_rows = 0
    generated_set = set()
    all_data = []

    while total_generated_rows < total_rows:  
        remaining_rows = total_rows - total_generated_rows
        batch_size = min(max_rows_per_batch, remaining_rows)

        # Adjust prompt dynamically for each batch
        prompt = generate_prompt(config, ref_data, column_names, expected_columns)

        response = generate_text_from_llm(prompt, api_key, model)
        # print(f"Batch Response ({total_generated_rows + 1}-{total_generated_rows + batch_size}):", response)

        rows = response.strip().split("\n")

        for row in rows:
            row_values = next(csv.reader([row], quotechar='"'))  # Proper CSV parsing

            if len(row_values) != expected_columns:
                continue  # Skip invalid rows

            row_tuple = tuple(row_values)
            if row_tuple not in generated_set:
                generated_set.add(row_tuple)
                all_data.append(dict(zip(column_names, row_values)))
                total_generated_rows += 1

            if total_generated_rows >= total_rows:  # Stop when we reach required total rows
                break

    print("Total Generated Rows:", total_generated_rows)
    return pd.DataFrame(all_data)