import sys,os
from setuptools import setup, find_packages
import subprocess
from os.path import join as pjoin, dirname, exists
from glob import glob
from painfacelib.config import INFO as info

def install_conda_packages():
    '''
    We are using the conda flag -c to specify the channel so please add the channel
    and package_name as a string seperated by a space. Please pass -y at the end
    '''
    conda_packages = [
    ]
    try:
        print("Checking for Conda dependencies...")
        for packages in conda_packages:
            subprocess.run(["conda", "install", "-c"] + packages, check=True)
    except subprocess.CalledProcessError:
        print("Error installing Conda packages. Please install them manually.")

def is_conda_env():
    return "CONDA_PREFIX" in os.environ

if is_conda_env():
    install_conda_packages()
else:
    print("Warning: You are not in a Conda environment. Some dependencies may fail to install.")

using_setuptools = 'setuptools' in sys.modules
extra_setuptools_args = {}

if using_setuptools:
    # Set setuptools extra arguments
    extra_setuptools_args = dict(
        tests_require=[],
        zip_safe=False,
        python_requires=">= 3.8",
        )

    
setup(
    name='painface-lc',
    version=info['painface']['version'],
    python_requires=">=3.8",
    license='MIT',
    author="SK Park, Zylka Lab, University of North Carolina @ Chapel Hill",
    author_email='scalphunter@gmail.com',
    packages=find_packages('.'),
    package_dir={'':'.'},
    package_data = {
    '': ['*.yml','*.yaml','*.json','*.xml','*.cnf','*.md','*.zip']
    },
    scripts=glob(pjoin('bin', '*')),
    url='https://github.com/Zylka-Lab/PainfaceLC',
    keywords=['mouse grimace','grimace','painface'],
    install_requires=[
        'wheel',
        'pyyaml',
        'torch',
        'torchvision',
        'numpy',
        'opencv-python',
        'bson',
        'pillow'
       ],

 )
