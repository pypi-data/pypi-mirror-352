from setuptools import setup, find_packages

setup(
    name="guardrails_sdk",
    version="0.1.0",
    author="Viswateja Rayapaneni",
    author_email="viswatejaster@gmail.com",
    description="A Python SDK for interacting with the Guardrails API.",
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    url="https://github.com/tejadata/guardrails",
    packages=find_packages(),
    install_requires=[
        "pydantic==2.9.2"
        "presidio_analyzer==2.2.358"
        "presidio_anonymizer==2.2.358"
        "torch==2.5.1"
        "transformers==4.47.1"
        "sentence-transformers==3.3.1"

    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8',
)
