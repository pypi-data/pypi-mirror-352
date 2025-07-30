#!/usr/bin/env python
import setuptools

if __name__ == "__main__":
    setuptools.setup(
        name="pysurveytools",
        version="0.1.0",
        author="Stefan Printz",
        author_email="stefan.printz@hs-bochum.de",
        description="Geodetic classes for managing and calculating (Angle, Coordinate, Measurement, …)",
        long_description=open("README.md", encoding="utf-8").read(),
        long_description_content_type="text/markdown",
        url="https://gitlab-ce.hs-bochum.de/fachbereich-geodaesie/pypi/pysurveytools",
        packages=setuptools.find_packages(where="src"),
        package_dir={"": "src"},
        install_requires=[
            "numpy>=1.20",
        ],
        extras_require={
            "test": ["pytest>=7.0"],
        },
        classifiers=[
            "Programming Language :: Python :: 3",
            "License :: OSI Approved :: MIT License",
            "Operating System :: OS Independent",
        ],
        entry_points={
            "console_scripts": [
                "surveytools-cli=surveytools.surveytools:main",
            ],
        },
    )
