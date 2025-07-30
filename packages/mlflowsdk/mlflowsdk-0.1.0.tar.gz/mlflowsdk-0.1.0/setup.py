from setuptools import setup, find_packages
from pathlib import Path

# read the requirements
requirements_path = Path("requirements.txt")
# extract all the requirements to install
if requirements_path.exists():
    requirements = requirements_path.read_text().splitlines()
else:
    requirements = []

setup(
    name='mlflowsdk',
    packages=find_packages(),
    version='0.1.0',
    description='cybage mlflow sdk',
    author='AI Cloud Data Team - [Viraj]',
    install_requires=requirements,  # <- This installs dependencies from requirements.txt
    license='MIT'
)
