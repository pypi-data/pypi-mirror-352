from setuptools import setup, find_packages, Command
import os
import sys
import shutil
import glob
from setuptools.command.install import install
from distutils.sysconfig import get_python_lib

# Custom install command to copy files to site-packages
class CustomInstall(install):
    def run(self):
        # Run the standard install first
        install.run(self)
        
        # Get the site-packages directory
        site_packages = get_python_lib()
        
        # Create the madlabjs directory in site-packages
        target_dir = os.path.join(site_packages, 'madlabjs')
        if not os.path.exists(target_dir):
            os.makedirs(target_dir)
            
        # Copy package.json to madlabjs directory
        if os.path.exists('package.json'):
            shutil.copy('package.json', target_dir)
            
        # Copy all directories to madlabjs directory
        directories = [d for d in os.listdir('.') if os.path.isdir(d) and 
                      not d.startswith('.') and 
                      d not in ['__pycache__', 'dist', 'build', 'test_env', 'madlabjs.egg-info']]
        
        for directory in directories:
            src_dir = os.path.join(os.getcwd(), directory)
            dst_dir = os.path.join(target_dir, directory)
            if os.path.exists(dst_dir):
                shutil.rmtree(dst_dir)
            shutil.copytree(src_dir, dst_dir)
            print(f'Copied {directory} to {dst_dir}')

setup(
    name="madlabjs",
    version="2.0.0",
    description="Android project files package with preserved folder structure",
    author="Your Name",
    author_email="your.email@example.com",
    packages=['madlabjs'],  # Create an empty madlabjs package
    package_dir={'madlabjs': 'madlabjs'},
    package_data={'madlabjs': ['*']},
    include_package_data=True,
    cmdclass={
        'install': CustomInstall,
    },
    zip_safe=False,
)
