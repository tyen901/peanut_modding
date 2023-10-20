import json
import os
import shutil

def copy_tagged_images(tags_file, src_dir, dest_dir, tag='copy'):
    """
    Copy all files with the specified tag from source directory to destination directory, 
    while preserving the relative directory structure.

    :param tags_file: path to the tags.json file
    :param src_dir: source directory
    :param dest_dir: destination directory
    :param tag: tag to filter images
    """
    
    # Load tags from the tags.json file
    with open(tags_file, 'r') as f:
        tags = json.load(f)

    # Filter images with the specified tag and copy them
    for image, image_tags in tags.items():
        if tag in image_tags:
            # Determine the source and destination paths
            src_path = os.path.join(src_dir, image)
            dest_path = os.path.join(dest_dir, image)
            
            # Ensure the destination directory exists
            os.makedirs(os.path.dirname(dest_path), exist_ok=True)
            
            if os.path.exists(src_path) == False:
                continue
            
            # Copy the file
            shutil.copy2(src_path, dest_path)

if __name__ == "__main__":
    TAGS_FILE = 'tags.json'
    SRC_DIR = "extracted"
    DEST_DIR = "selected"
    SRC_DIR = os.path.join(os.getcwd(), SRC_DIR)
    DEST_DIR = os.path.join(os.getcwd(), DEST_DIR)
    
    copy_tagged_images(TAGS_FILE, SRC_DIR, DEST_DIR, tag='copy')
    print(f"Files tagged with 'copy' have been copied from {SRC_DIR} to {DEST_DIR}.")
