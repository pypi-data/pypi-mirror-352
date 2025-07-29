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
        "fastapi",
        "httpx",
        "pydantic",
        "torch",
        "transformers",
        "presidio-analyzer",
        "presidio-anonymizer",
        "llm-guard"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8',
)
