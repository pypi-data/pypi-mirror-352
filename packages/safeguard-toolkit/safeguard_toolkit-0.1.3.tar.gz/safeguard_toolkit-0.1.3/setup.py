from setuptools import setup, find_packages

setup(
    name="safeguard-toolkit",
    version="0.1.2",
    description="A project for scanning secrets, configs, dependencies, and permissions",
    author="Purvi Verma",
    packages=find_packages(),  
    install_requires=[
        "pyyaml==6.0.2",
        "requests==2.32.3",
        "packaging==25.0",
        "toml==0.10.2",
        "packaging==25.0"
    ],
    python_requires=">=3.12",
)
