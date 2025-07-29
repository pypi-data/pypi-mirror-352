import yaml
import pandas as pd


def load_yaml(file_path):
    """Load YAML configuration file."""
    with open(file_path, 'r') as file:
        return yaml.safe_load(file)


def validate_yaml(config):
    """Validate the structure of the YAML configuration file."""
    required_keys = {"columns", "prompt"}
    
    if not isinstance(config, dict):
        raise ValueError("YAML configuration should be a dictionary.")

    print("✅ YAML configuration format is valid.")

def validate_csv(file_path):
    """Validate the CSV reference file format without enforcing column order."""
    try:
        df = pd.read_csv(file_path, nrows=5)  # Read only the first few rows
    except Exception as e:
        raise ValueError(f"Error reading CSV file: {e}")
    
    print("✅ CSV reference file format is valid.")
    return df


def process_and_validate_files(args):

    yaml_file = None
    config = None
    reference_file = None

    if len(args) >= 2 and not args[-2].endswith(('.yaml', '.yml', '.csv')):
        api_key = args[-2]
        model = args[-1]
        file_args = args[:-2]
    elif len(args) >= 1 and not args[-1].endswith(('.yaml', '.yml', '.csv')):
        api_key = args[-1]
        file_args = args[:-1]
    else:
        file_args = args

    # Identify YAML and CSV files
    for arg in file_args:
        if arg.endswith(('.yaml', '.yml')):
            yaml_file = arg
        elif arg.endswith('.csv'):
            reference_file = arg

    if not yaml_file and not reference_file:
        print("❌ No valid .yaml or .csv files provided.")
        print("✅ Usage: python test1.py <file.yaml> <file.csv> [api_key] [model]")
        sys.exit(1)

    # Validate YAML format
    if yaml_file:
        config = load_yaml(yaml_file)
        try:
            validate_yaml(config)
        except ValueError as e:
            print(f"❌ YAML validation error: {e}")
            sys.exit(1)

    # Validate CSV format
    if reference_file:
        try:
            reference_file = validate_csv(reference_file)
        except ValueError as e:
            print(f"❌ CSV validation error: {e}")
            sys.exit(1)

    return config, reference_file