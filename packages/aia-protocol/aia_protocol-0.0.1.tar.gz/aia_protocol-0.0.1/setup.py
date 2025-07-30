from setuptools import setup, find_packages

setup(
    name="aia-protocol",
    version="0.0.1",
    packages=find_packages(include=["aia_protocol", "aia_protocol.*"]),
    install_requires=["cryptography>=44.0.3"],
    python_requires=">=3.9",
)
