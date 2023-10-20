import os
import subprocess
import shutil
from concurrent.futures import ThreadPoolExecutor, as_completed

def extract_and_move(pbo_path, extractor_path, dest_dir, src_dir):
    # Extract the PBO
    path_without_pbo = pbo_path[:-4]  # Remove the .pbo extension
    # If the extracted folder already exists, delete it
    if os.path.exists(path_without_pbo):
        shutil.rmtree(path_without_pbo)

    # Run the ExtractPbo.exe
    args = [extractor_path, "-P", pbo_path]

    try:
        subprocess.run(args, check=True)
        move_folder(path_without_pbo, dest_dir, src_dir)
        if os.path.exists(path_without_pbo):
            shutil.rmtree(path_without_pbo)
    except subprocess.CalledProcessError:
        # Just return if the PBO is corrupted
        return

def move_folder(src_path, dest_dir, src_dir):

    # Iterate through the first level of folders in the src_path
    for dir in os.listdir(src_path):
        full_dir_path = os.path.join(src_path, dir)

        if os.path.isdir(full_dir_path):
            dest_path = os.path.join(dest_dir, dir)
            shutil.copytree(full_dir_path, dest_path, dirs_exist_ok=True)
            shutil.rmtree(full_dir_path)

def extract_and_move_pbo_files(src_dir, dest_dir, max_threads=30):
    # Path to the ExtractPbo.exe
    extractor_path = r"C:\Program Files (x86)\Mikero\DePboTools\bin\ExtractPbo.exe"

    # First, gather all the pbo files
    pbo_files = []
    for root, dirs, files in os.walk(src_dir):
        for file in files:
            if file.endswith(".pbo"):
                pbo_files.append(os.path.join(root, file))

    with ThreadPoolExecutor(max_workers=max_threads) as executor:
        # Submit tasks to extract and move
        futures = [executor.submit(extract_and_move, pbo_path, extractor_path, dest_dir, src_dir) for pbo_path in pbo_files]

        # Ensure all tasks are completed
        for future in as_completed(futures):
            future.result()

if __name__ == "__main__":
    source_directory = "D:\\modding"
    destination_directory = "P:\\"
    extract_and_move_pbo_files(source_directory, destination_directory)
