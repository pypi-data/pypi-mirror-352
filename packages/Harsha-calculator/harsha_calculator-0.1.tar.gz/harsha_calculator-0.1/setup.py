from setuptools import setup, find_packages

setup(
    name="Harsha_calculator",
    version="0.1",
    packages=find_packages(),
    description="A simple calculator package",
    author="Your Name",
    author_email="you@example.com",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License"
    ],
    python_requires='>=3.6',
)
