"""
setup for btpytools
"""

import os
from setuptools import setup, find_packages

# Read in the README file as a variable so we can later add it to the description

THIS_DIRECTORY = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(THIS_DIRECTORY, "README.md"), encoding="utf-8") as f:
    LONG_DESCRIPTION = f.read()


# Blank setup.py which pip seems to need in order to be happy with setup.cfg
setup(
    name="btpytools",
    version="0.1.18",
    packages=find_packages(),
    description="Helper functions for BakingTray and StitchIt",
    license_files="LICENSE",
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    install_requires=["pyyaml"],
    extras_require={"dev": ["black", "pytest"]},
    python_requires=">=3.6",
    url="https://github.com/SainsburyWellcomeCentre/btpytools",
    project_urls={
        "Source Code": "https://github.com/SainsburyWellcomeCentre/btpytools"
    },
    author="Rob Campbell",
    author_email="rob.campbell@ucl.ac.uk",
    classifiers=[
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
    ],
    zip_safe=True,
    include_package_data=True,
    entry_points={
        "console_scripts": [
            "summariseAcqs=btpytools.summariseAcquisitions:main",
            "compressRawData=btpytools.compressRawData:main",
            "transferToServer=btpytools.transferToServer:main",
        ]
    },
)
