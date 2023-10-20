import os
import subprocess
import shutil
from wand.image import Image
from concurrent.futures import ThreadPoolExecutor

def _convert_single_file_paa_to_png(full_path, output_file):
    """Convert a single .paa file to .png."""
    cmd = ["Pal2PacE.exe", full_path, output_file]
    subprocess.run(cmd)

def convert_paa_to_png(input_dir, output_dir, max_threads=10):
    """Batch convert .paa files to .png using multiple threads."""
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    tasks = []

    for root, dirs, files in os.walk(input_dir):
        for file in files:
            if file.endswith('.paa'):
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(root, input_dir)
                output_subdir = os.path.join(output_dir, rel_path)
                
                if not os.path.exists(output_subdir):
                    os.makedirs(output_subdir)
                
                output_file = os.path.join(output_subdir, file.replace('.paa', '.png'))
                if os.path.exists(output_file):
                    continue
                
                tasks.append((full_path, output_file))

    with ThreadPoolExecutor(max_threads) as executor:
        for task in tasks:
            executor.submit(_convert_single_file_paa_to_png, task[0], task[1])

def _convert_single_file_psd_to_png(full_path, output_file):
    """Convert a single .psd file to .png."""

    # make sure path exists
    if not os.path.exists(os.path.dirname(output_file)):
        os.makedirs(os.path.dirname(output_file))

    # Convert a large PSD to small PNG thumbnail
    myImage = Image(filename=full_path + "[0]")
    myImage.format = "png"
    myImage.save(filename=output_file)

def convert_psd_to_png(input_dir, output_dir, max_threads=10):
    """Batch convert .png files to .paa using multiple threads."""
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    tasks = []

    for root, dirs, files in os.walk(input_dir):
        for file in files:
            if file.endswith('.psd'):
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(root, input_dir)
                output_subdir = os.path.join(output_dir, rel_path)
                
                output_file_path = os.path.join(output_subdir, file.replace('.psd', '.png'))

                if os.path.exists(output_file_path):
                    os.remove(output_file_path)

                # Add task to convert the temp png to paa
                tasks.append((full_path, output_file_path))

    with ThreadPoolExecutor(max_threads) as executor:
        for task in tasks:
            executor.submit(_convert_single_file_psd_to_png, task[0], task[1])

def _convert_single_file_png_to_paa(full_path, output_file):
    """Convert a single .png file to .paa."""

    # make sure path exists
    if not os.path.exists(os.path.dirname(output_file)):
        os.makedirs(os.path.dirname(output_file))

    cmd = ["Pal2PacE.exe", full_path, output_file]
    subprocess.run(cmd)

def convert_png_to_paa(input_dir, output_dir, max_threads=10):
    """Batch convert .png files to .paa using multiple threads."""
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    tasks = []

    for root, dirs, files in os.walk(input_dir):
        for file in files:
            if file.endswith('.png'):
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(root, input_dir)
                output_subdir = os.path.join(output_dir, rel_path)
                output_file_path = os.path.join(output_subdir, file.replace('.png', '.paa'))

                if os.path.exists(output_file_path):
                    os.remove(output_file_path)

                if not os.path.exists(output_subdir):
                    os.makedirs(output_subdir)
                
                # Add task to convert the temp png to paa
                tasks.append((full_path, output_file_path))

    with ThreadPoolExecutor(max_threads) as executor:
        for task in tasks:
            executor.submit(_convert_single_file_png_to_paa, task[0], task[1])

def create_temp_converted_folder(base_dir):
    """Create the temp/converted directory."""
    temp_converted_dir = os.path.join(base_dir, "temp", "converted")
    if not os.path.exists(temp_converted_dir):
        os.makedirs(temp_converted_dir)
    return temp_converted_dir

def delete_temp_converted_folder(base_dir):
    """Delete the temp/converted directory."""
    temp_converted_dir = os.path.join(base_dir, "temp", "converted")
    if os.path.exists(temp_converted_dir):
        shutil.rmtree(temp_converted_dir)
