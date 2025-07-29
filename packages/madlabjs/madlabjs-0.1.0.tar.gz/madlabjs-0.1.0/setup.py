from setuptools import setup, find_packages
import os
from setuptools.command.install import install
import shutil
import glob

# Get all directories at the top level
directories = [d for d in os.listdir('.') if os.path.isdir(d) and not d.startswith('.') and d != '__pycache__']

# Get all files at the top level
files = [f for f in os.listdir('.') if os.path.isfile(f) and not f.startswith('.') 
         and f not in ['setup.py', 'MANIFEST.in', 'README.md', '.gitignore']]

# Create package_data dictionary
package_data = {
    '': files,  # Include top-level files
}

# Add all files in each directory
for directory in directories:
    package_data[directory] = ['*', '*/*', '*/*/*', '*/*/*/*']  # Include all nested files

setup(
    name="madlabjs",
    version="0.1.0",
    description="Android project files package with preserved folder structure",
    author="Your Name",
    author_email="your.email@example.com",
    packages=[''] + directories,  # Include the root package and all directories as packages
    package_dir={'': '.'},  # The root package is in the current directory
    package_data=package_data,
    include_package_data=True,
    zip_safe=False,
)
