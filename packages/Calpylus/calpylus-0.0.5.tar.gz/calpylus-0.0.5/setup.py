from setuptools import setup, find_packages
import os
NAME = "Calpylus"
VERSION = "0.0.5"
AUTHOR = "Mohammad Mahfuz Rahman"
AUTHOR_EMAIL = "mahfuzrahman0712@gmail.com"
DESCRIPTION = "Calpylus is a strong python library for calculus"
GIT_REPO_URL = "https://github.com/mahfuz0712/Calpylus.git"


with open(os.path.join(os.path.dirname(__file__), "README.md"), encoding="utf-8") as readme_file:
    LONG_DESCRIPTION = readme_file.read()
setup(
    name=NAME,
    version=VERSION,
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    url=GIT_REPO_URL,
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent"
    ],
    python_requires='>=3.9',
    install_requires=[
        
    ],
    include_package_data=True,
)
