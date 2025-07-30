from setuptools import setup, find_packages

setup(
    name="upload-to-gcs",
    version="1.0.0",
    author="Andrii Omelianovych",
    description="Program to upload large files to GCP",
    packages=find_packages(),
    install_requires=['google.cloud'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
    python_requires='>=3.12',
)
