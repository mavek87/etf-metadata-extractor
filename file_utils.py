import os

def create_output_folder(base_path, folder_name):
    output_path = os.path.join(base_path, folder_name)
    os.makedirs(output_path, exist_ok=True)
    print(f"Folder '{output_path}' created successfully (or already exists)!")
    return output_path

def find_csv_files(folder: str):
    return [f for f in os.listdir(folder) if f.lower().endswith(".csv")]