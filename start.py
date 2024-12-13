import subprocess
import yaml
import os
import shutil
import sys

# Function to create/update YAML file with specified content
def create_yaml_file(file_path, content):
    with open(file_path, 'w') as file:
        yaml.dump(content, file)

# Define the content for settings.yaml
settings_content = {
    'title': '<TITLE>',
    'port': '<PORT>',
    'interface': None,
    'tabs': {
        'config': False,
        'main': False,
        'notebook': False
    },
    'timer': {
        'client': 1000,
        'group': [],
        'retention': 86400000,
        'server': 60000,
        'invalid': 10000
    },
    'redis': {
        'host': "127.0.0.1",
        'port': 6379
    },
    'notebook': {
        'host': None,
        'port': None
    }
}

# Create or update settings.yaml with the specified content
create_yaml_file('settings.yaml', settings_content)

# Load current settings from settings.yaml
with open('settings.yaml', 'r') as file:
    current_settings = yaml.safe_load(file)

# Ask user for new title and port
new_title = input("Enter the new title: ")
new_port = input("Enter the new port: ")

# Update settings
current_settings['title'] = new_title
current_settings['port'] = new_port

# Write back to settings.yaml
with open('settings.yaml', 'w') as file:
    yaml.dump(current_settings, file)

print("Settings updated successfully!")

# Create or update style.yaml and varname.yaml with curly brackets
create_yaml_file('style.yaml', {})
create_yaml_file('varname.yaml', {})

try:
    # Clone the latest version of Bora repository
    bora_repo_url = "https://github.com/kit-ipe/bora.git"
    bora_clone_path = "bora"  # This assumes 'bora' is the desired destination folder

    # Check if the 'bora' directory already exists
    if not os.path.exists(bora_clone_path):
        subprocess.run(['git', 'clone', bora_repo_url, bora_clone_path])
        print("Bora repository cloned !!!")

        # Install requirements after cloning
        bora_requirements_path = os.path.join(bora_clone_path, 'requirements.txt')
        subprocess.run(['pip', 'install', '-r', bora_requirements_path])
        print("Bora requirements installed !!!")
    else:
        print("Bora repository already cloned.")
except Exception as e:
    print(f"An error occurred in cloning the Bora repository: {e}")
    sys.exit()

# Copy background.png from bora directory to current working directory
bora_background_path = os.path.join(bora_clone_path, 'misc', 'bora_v1', 'background.png')
current_directory = os.getcwd()
default_user_background_path = os.path.join(current_directory, 'background.png')

shutil.copy(bora_background_path, default_user_background_path)

os.chdir(bora_clone_path)
os.chdir("..")

# Define default background image path
default_background_image_path = default_user_background_path

# Ask user whether to use the default background image or their own image
while True:
    user_choice = input("Do you want to use the default background image provided? (Enter 'yes' for default, or enter 'no' to provide your own image path): ").strip()
    if user_choice == "yes":
        print("Using default background image.")
        break
    elif user_choice.lower() == "no":
        user_background_image_path = input("Enter the path to your background image: ").strip()
        if os.path.isfile(user_background_image_path):
            shutil.copy(user_background_image_path, default_user_background_path)
            print("Using a custom background image.")
            break
        else:
            print("Invalid image path. Please provide a valid path.")
    else:
        print("Invalid choice. Please enter 'yes or 'no' only.")
