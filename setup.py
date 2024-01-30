from setuptools import setup, find_packages


setup(
    name="categorical_cluster",
    version="0.3",
    packages=find_packages(),
    description="A package for clustering categorical data",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Maciej Bajor",
    author_email="maciekbajor@gmail.com",
    url="https://github.com/bajor/categorical-cluster",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
    ],
)
