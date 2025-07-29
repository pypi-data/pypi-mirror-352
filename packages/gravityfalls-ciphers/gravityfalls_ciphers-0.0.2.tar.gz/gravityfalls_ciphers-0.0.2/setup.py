from setuptools import setup, find_packages
with open("README.md", "r") as f:
    description = f.read()
setup(
    name="gravityfalls_ciphers",
    version='0.0.2',
    packages=find_packages(),
    long_description = description,
    long_description_content_type="text/markdown"
)