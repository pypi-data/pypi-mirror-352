import pandas as pd

def load_data(path: str, file_type: str):
    try:
        if file_type == 'csv':
            return pd.read_csv(path)
        elif file_type == 'excel':
            return pd.read_excel(path)
        elif file_type == 'json':
            return pd.read_json(path)
        else:
            print(f"Unsupported file type: {file_type}")
            return None
    except Exception as e:
        print(f"Error loading {file_type} file: {e}")
        return None

def save_data(df, file_type: str, path: str):
    try:
        if file_type == 'csv':
            df.to_csv(path, index=False)
        elif file_type == 'excel':
            df.to_excel(path, index=False)
        elif file_type == 'json':
            df.to_json(path, orient='records', indent=4)
        else:
            print(f"Unsupported file type: {file_type}")
            return
        print(f"✅ Data saved successfully to {path}")
    except Exception as e:
        print(f"Error saving data: {e}")
