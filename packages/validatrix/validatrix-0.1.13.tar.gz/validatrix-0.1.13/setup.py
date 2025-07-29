from setuptools import setup, find_packages

setup(
    name="validatrix",
    version="0.1.13",
    packages=find_packages(),
    install_requires=[
        "python-can>=4.0.0",
        "cantools>=36.0.0",
        "adafruit-circuitpython-mcp4725>=1.4.6",
        "adafruit-blinka>=8.0.0",
        "pymodbus==3.1.3",
        "pyserial>=3.5",
        "asyncio>=3.4.3",
    ],
    author="Prateek Pawar",
    author_email="prateekspawar@gmail.com",
    description="A Python library for using validatrix emulation hardware",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/prateekspawar/validatrix_python",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
