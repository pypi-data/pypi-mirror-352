from setuptools import setup, find_packages

setup(
    name="cloud_auto_deployor",
    version="1.0.6",
    author="Raja P",
    author_email="your_email@example.com",
    description="A Python CLI library for automated cloud deployment to Azure (ACI + ACR)",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/Raja900-del/cloud_auto_deployor",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "azure-cli",
        "docker",
        "pyyaml"
    ],
    entry_points={
        "console_scripts": [
            "cloud-auto-deploy = cloud_auto_deployor.main:main"
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.9',
)
