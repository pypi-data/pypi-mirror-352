from setuptools import setup, find_packages

setup(
    name="imagery24",
    version="0.7.2",
    packages=find_packages(),
    description="A short description of your package",
    long_description_content_type="text/markdown",
    author_email="your.email@example.com",
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=[
        "rasterio==1.4.3",
        "pillow==11.1.0",
        "imagecodecs==2024.12.30",
        "geopandas==1.0.1",
        "matplotlib==3.10.0",
        "pykml==0.2.0",
    ],
    zip_safe=True,
)
