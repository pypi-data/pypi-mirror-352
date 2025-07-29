from setuptools import setup, find_packages

with open("requirements.txt") as f:
    install_requires = f.read().splitlines()

print("Install requires:", install_requires)

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
    install_requires=install_requires,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8',
)
