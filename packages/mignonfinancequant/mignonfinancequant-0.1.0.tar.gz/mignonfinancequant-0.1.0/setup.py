from setuptools import setup, find_packages

setup(
    name="mignonfinancequant",
    version="0.1.0",
    author="Evilafo",
    author_email="evil2846@gmail.com",
    description="Une bibliothèque Python pour les calculs de finance quantitative",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/Evilafo/mignonfinancequant", 
    packages=find_packages(),
    install_requires=[
        "numpy",
        "scipy",
        "matplotlib",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)