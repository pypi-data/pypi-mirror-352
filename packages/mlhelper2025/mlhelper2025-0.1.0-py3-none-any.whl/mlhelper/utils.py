import os

def print_code(lab_number):
    filename = f"lab{lab_number}.py"
    package_dir = os.path.dirname(__file__)
    file_path = os.path.join(package_dir, filename)
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            print(f.read())
    else:
        print(f"File {filename} not found.")
