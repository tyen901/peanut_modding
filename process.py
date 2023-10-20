import os
import shutil
from conversion_utils import convert_psd_to_png, convert_png_to_paa

MAKE_PBO_PATH = "C:\\Program Files (x86)\\Mikero\\DePboTools\\bin\\MakePbo.exe"

def sync_folders(source_dir, patched_dir):
    # Ensure the patched directory exists
    if not os.path.exists(patched_dir):
        os.makedirs(patched_dir)
    
    # Walk through source directory
    for root, dirs, files in os.walk(source_dir):
        for file in files:
            source_file = os.path.join(root, file)
            rel_path = os.path.relpath(root, source_dir)
            patched_subdir = os.path.join(patched_dir, rel_path)
            
            # Ensure the corresponding directory exists in patched
            if not os.path.exists(patched_subdir):
                os.makedirs(patched_subdir)
            
            patched_file = os.path.join(patched_subdir, file)

            # Check if file sizes are different or file doesn't exist in patched
            if not os.path.exists(patched_file) or os.path.getsize(source_file) != os.path.getsize(patched_file):
                shutil.copy2(source_file, patched_file)

    # Delete files/folders in patched not present in source
    for root, dirs, files in os.walk(patched_dir):
        for file in files:
            patched_file = os.path.join(root, file)
            rel_path = os.path.relpath(root, patched_dir)
            source_subdir = os.path.join(source_dir, rel_path)
            source_file = os.path.join(source_subdir, file)
            
            if not os.path.exists(source_file):
                os.remove(patched_file)
                
        for dir in dirs:
            patched_subdir = os.path.join(root, dir)
            rel_path = os.path.relpath(patched_subdir, patched_dir)
            source_subdir = os.path.join(source_dir, rel_path)
            
            if not os.path.exists(source_subdir):
                shutil.rmtree(patched_subdir)

def copy_to_patched(temp_converted_dir, patched_dir):
    # Copy contents of temp/converted to patched
    for root, dirs, files in os.walk(temp_converted_dir):
        for file in files:
            temp_file = os.path.join(root, file)
            rel_path = os.path.relpath(root, temp_converted_dir)
            patched_subdir = os.path.join(patched_dir, rel_path)
            
            # Ensure the corresponding directory exists in patched
            if not os.path.exists(patched_subdir):
                os.makedirs(patched_subdir)
            
            patched_file = os.path.join(patched_subdir, file)
            shutil.copy2(temp_file, patched_file)

if __name__ == "__main__":

    this_file = os.path.realpath(__file__)
    base_dir = os.path.dirname(this_file)
    
    # Define directories
    SOURCE_DIR = os.path.join(base_dir, "raw")
    PATCHED_DIR = os.path.join(base_dir, "patched")
    EDITED_DIR = os.path.join(base_dir, "edits")
    
    TEMP_DIR = os.path.join(base_dir, "temp")
    TEMP_PNG_DIR = os.path.join(TEMP_DIR, "png")
    TEMP_PAA_DIR = os.path.join(TEMP_DIR, "paa")

    if os.path.exists(TEMP_DIR):
        shutil.rmtree(TEMP_DIR)

    if os.path.exists(PATCHED_DIR):
        shutil.rmtree(PATCHED_DIR)

    # # Convert files
    convert_psd_to_png(EDITED_DIR, TEMP_PNG_DIR)
    convert_png_to_paa(TEMP_PNG_DIR, TEMP_PAA_DIR)
    
    # Sync folders
    sync_folders(SOURCE_DIR, PATCHED_DIR)

    # Patch with converted files
    copy_to_patched(TEMP_PAA_DIR, PATCHED_DIR)

    # copy all .p3d files from edited folder to patched
    for root, dirs, files in os.walk(EDITED_DIR):
        for file in files:
            if file.endswith(".p3d"):
                edited_file = os.path.join(root, file)
                rel_path = os.path.relpath(root, EDITED_DIR)
                patched_subdir = os.path.join(PATCHED_DIR, rel_path)
                
                # Ensure the corresponding directory exists in patched
                if not os.path.exists(patched_subdir):
                    os.makedirs(patched_subdir)
                
                patched_file = os.path.join(patched_subdir, file)
                shutil.copy2(edited_file, patched_file)
