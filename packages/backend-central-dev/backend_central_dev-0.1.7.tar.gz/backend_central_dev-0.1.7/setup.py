from setuptools import setup, find_packages

with open('../requirements.txt') as f:
    required = f.read().splitlines()

setup(
    name='backend_central_dev',
    version='0.1.7',
    packages=find_packages(),
    install_requires=required,
)
