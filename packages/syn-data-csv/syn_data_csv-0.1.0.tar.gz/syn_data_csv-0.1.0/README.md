# Synthetic Data Generation PoC

## Overview
This project generates synthetic data using an AI model based on a given YAML configuration file and a reference CSV file. The generated data follows the provided column structure and user-defined constraints.

## Features
- Reads column definitions and user instructions from a YAML configuration file.
- Validates the structure of the YAML file.
- Validates the format of the reference CSV file.
- Generates synthetic data using Groq's Mixtral model.
- Ensures the output is in CSV format without headers or extra text.
- Enforces unique rows with consistent column counts.

## Prerequisites
- Python 3.8+
- Required Python packages:
  - `yaml`
  - `pandas`
  - `json`
  - `csv`
  - `groq`

<!-- ## Installation
1. Clone the repository or copy the script to your local environment.
2. Install dependencies using pip:
   ```sh
   pip install pandas pyyaml groq
   ```
3. Obtain a Groq API key and replace `api_key` in the script with your key. -->

## Usage
Run the script with the required YAML configuration file and reference CSV file:
```sh
python test1.py config.yaml test_data.csv [optional_api_key]
```

## Arguments

config.yaml - YAML file specifying column definitions and generation rules.
test_data.csv - Reference CSV file to guide synthetic data generation.
[optional_api_key] - (Optional) Your own Groq API key. If not provided, a default API key will be used.



### YAML Configuration Structure
The YAML file should define columns and the prompt:
```yaml
columns:
  - name: "id"
    type: "integer"
  - name: "name"
    type: "string"
  - name: "email"
    type: "string"
  - name: "age"
    type: "integer"
  - name: "city"
    type: "string"
  - name: "signup_date"
    type: "datetime"
    
num_rows: 100
prompt: "Generate a dataset for user profiles."
```


## Reference CSV File (`test_data.csv`)
This file provides sample data for reference.

### Example `test_data.csv`:
```csv
id,name,age,email,city,signup_date
101,John Doe,28,john.doe@example.com,New York,2023-05-14
102,Jane Smith,34,jane.smith@example.com,Los Angeles,2022-11-21
...
```

## Expected Output
- The generated dataset will be stored in `synthetic_data.csv`.
- The output will contain only comma-separated values without extra text or headers.
- The generated rows will be unique and follow the reference data pattern.

## Error Handling
- If the YAML configuration is invalid, the script will display an error message and exit.
- If the reference CSV file has missing columns, the script will halt with an error.
- If no valid data is generated, an appropriate message will be displayed.

## License
This project is for demonstration purposes only. Usage is subject to Groq API policies.

