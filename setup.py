from setuptools import setup
from setuptools import find_packages

with open('requirements.txt', encoding='utf-8') as f:
    content = f.readlines()
requirements = [x.strip() for x in content]

setup(
    name='backend',
    description="Backend of the ForestVision web app",
    packages=find_packages(),
    install_requires=requirements)
