import os
import json

# Configuration
LOCK_FILE = ".bootstrap_complete"
ADMIN_DIR = "admin"
VARS_FILENAME = "repo_vars.json"
VARS_PATH = os.path.join(ADMIN_DIR, VARS_FILENAME)
TARGET_EXTENSION = ".md"

def load_variables():
    """Reads JSON and handles the specific project naming logic."""
    if not os.path.exists(VARS_PATH):
        print(f"Check: {VARS_PATH} not found.")
        return None
    
    try:
        with open(VARS_PATH, 'r', encoding='utf-8') as f:
            replacements = json.load(f)
        
        # Override <PROJECT_TITLE> with the actual root folder name
        root_folder_name = os.path.basename(os.getcwd())
        replacements["<PROJECT_TITLE>"] = root_folder_name

        print(f"Project Title detected as: {root_folder_name}")
        return replacements
    except (json.JSONDecodeError, OSError) as e:
        print(f"Error reading JSON: {e}")
        return None

def bootstrap_repo():
    """Main logic to walk the directory and replace tags in Markdown files."""
    if os.path.exists(LOCK_FILE):
        print("Setup already complete. Skipping replacement logic.")
        return

    replacements = load_variables()
    if not replacements:
        return

    print("Initializing repository structure and updating documentation...")

    # Recursive Walk through the repo
    for root, dirs, files in os.walk('.'):
        # Skip hidden directories (like .git or .vscode)
        dirs[:] = [d for d in dirs if not d.startswith('.')]

        for file in files:
            if file.endswith(TARGET_EXTENSION):
                file_path = os.path.join(root, file)
                process_file(file_path, replacements)

    # 1. Create the lock file
    try:
        with open(LOCK_FILE, 'w', encoding = "utf-8") as f:
            f.write("Bootstrap successful.")
        print(f"Created lock file: {LOCK_FILE}")
    except OSError as e:
        print(f"Failed to create lock file: {e}")

    # 2. Cleanup: Remove ONLY the JSON file
    # try:
    #     if os.path.exists(VARS_PATH):
    #         os.remove(VARS_PATH)
    #         print(f"Cleaned up {VARS_PATH}. The '{ADMIN_DIR}' folder remains.")
    # except Exception as e:
    #     print(f"Cleanup of JSON failed: {e}")

    print("\nProject successfully initialized with provided metadata.")

def process_file(file_path, replacements):
    """Reads, replaces, and writes back the content of a file."""
    try:
        # Set <FOLDER> based on the folder containing the file being processed.
        dirpath = os.path.dirname(file_path) or '.'
        folder_basename = os.path.basename(os.path.abspath(dirpath))
        folder_name = folder_basename.capitalize()
        # If the folder name is Gis, change it to GIS
        if folder_name.lower() == "gis":
            folder_name = "GIS"
        replacements["<FOLDER>"] = folder_name

        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        original_content = content
        
        # Explicitly replacing the four required variables
        # Using a loop to handle the dictionary keys provided in load_variables
        for placeholder, value in replacements.items():
            content = content.replace(str(placeholder), str(value))
        
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"Updated: {file_path}")
            
    except (OSError, UnicodeDecodeError) as e:
        print(f"Could not process {file_path}: {e}")

if __name__ == "__main__":
    bootstrap_repo()