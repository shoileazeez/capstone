import os
import zipfile

def zip_project(folder_path, zip_name):
    # Create a zip file
    with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for foldername, subfolders, filenames in os.walk(folder_path):
            for filename in filenames:
                file_path = os.path.join(foldername, filename)
                
                # Exclude specific files and folders
                if (
                    ".git" in file_path or
                    ".vscode" in file_path or
                    "myworld" in file_path or
                    "create_zip.py" == filename  # Exclude the script itself
                ):
                    continue

                print(f'Adding: {file_path}')  # Debug output to see what is being added
                # Add file to the zip file
                zip_file.write(file_path, os.path.relpath(file_path, folder_path))

# Usage
folder_to_zip = '.'  # Specify the root folder you want to zip (current directory)
zip_filename = 'capstone_project.zip'  # Specify the zip file name
zip_project(folder_to_zip, zip_filename)

print(f'Created {zip_filename} successfully.')
