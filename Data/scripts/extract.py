from pathlib import Path
import zipfile

def extract_archives_in_directory(target_dir, extract_to):
    dir_path = Path(target_dir)
    
    if not dir_path.exists():
        print(f"Directory {target_dir} does not exist.")
        return

    for file_path in dir_path.iterdir():
        if not file_path.is_file():
            continue

        try:
            # Handle .zip files
            if file_path.suffix.lower() == '.zip':
                with zipfile.ZipFile(file_path, 'r') as zip_ref:
                    zip_ref.extractall(extract_to)

        except Exception as e:
            print(f"❌ Failed to extract {file_path.name}: {e}")
            
if __name__ == "__main__":
    extract_archives_in_directory("./Data/zipped", "./Data/raw")