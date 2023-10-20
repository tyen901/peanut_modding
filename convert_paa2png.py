import os
import subprocess
import shutil
from conversion_utils import convert_paa_to_png

if __name__ == "__main__":
    # Get path to this file
    this_file = os.path.realpath(__file__)

    # Get a path relative to this file
    INPUT_DIR = os.path.join(os.path.dirname(this_file), "source")
    OUTPUT_DIR = os.path.join(os.path.dirname(this_file), "extracted")
    convert_paa_to_png(INPUT_DIR, OUTPUT_DIR)
