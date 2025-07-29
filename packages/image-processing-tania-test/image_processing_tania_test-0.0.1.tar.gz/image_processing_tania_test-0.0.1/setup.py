from setuptools import setup, find_packages

with open("README.md", "r") as f:
    page_description = f.read()

with open("requirements.txt") as f:
    requirements = f.read().splitlines()

setup(
    name="image-processing-tania-test",
    version="0.0.1",
    author="Tania Cremonini",
    author_email="taninha_cremonini@hotmail.com",
    description="Image Processing Package using Skimag",
    long_description=page_description,
    long_description_content_type="text/markdown",
    url="https://github.com/taniacremonini/image-processing-package.git",
    packages=find_packages(),
    install_requires=requirements,
    python_requires='>=3.5',
)

 
