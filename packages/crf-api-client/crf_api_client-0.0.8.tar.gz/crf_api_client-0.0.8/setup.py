from setuptools import setup, find_packages

setup(
    name="crf-api-client",
    version="0.0.8",
    packages=find_packages(),
    install_requires=[
        "requests==2.32.3",
        "datamodel-code-generator==0.30.1",
        "tqdm==4.67.1",
    ],
    author="CRF",
    description="A client for the CRF API",
    python_requires=">=3.11",
)