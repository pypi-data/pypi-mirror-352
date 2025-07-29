from setuptools import find_packages, setup

setup(
    name="crf_api_client",  # Package name
    version="0.0.6",  # Package version
    packages=find_packages(),  # Automatically finds `mypackage`
    install_requires=[
        "requests>=2.32.3",
        "datamodel-code-generator>=0.30.1",
        "tqdm>=4.67.1",
    ],  # List dependencies if any
    author="CRF",
    description="A client for the CRF API",
    python_requires=">=3.11",  # Minimum Python version
)
