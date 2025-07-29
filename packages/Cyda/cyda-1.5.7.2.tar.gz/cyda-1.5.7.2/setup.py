from setuptools import setup, find_packages

with open("README.md", "r") as f:
    description = f.read()

setup(
    name = "Cyda",
    version = "1.5.7.2",
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'cyda = Cyda.main:main',
        ],
    },
    long_description=description,
    long_description_content_type="text/markdown",
)
