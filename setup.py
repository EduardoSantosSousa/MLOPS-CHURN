from setuptools import setup, find_packages

with open("requirements.txt") as f:
    requirements = f.read().splitlines()

setup(
    name="MLOPS-PROJECT-TELCO-CUSTUMER-CHURCH",
    version="0.1",
    author="Eduardo dos Santos Sousa",
    packages=find_packages(),
    install_requires=requirements,
)