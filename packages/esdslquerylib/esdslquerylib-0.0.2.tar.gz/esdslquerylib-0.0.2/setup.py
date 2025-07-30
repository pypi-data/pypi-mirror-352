from setuptools import setup, find_packages

setup(
    name="esdslquerylib",
    version="0.0.2",
    author="Jun Ke",
    author_email="kejun91@gmail.com",
    description="Elasticsearch query lib",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/kejun91/esdslquerylib",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[],
    python_requires='>=3.9',
)