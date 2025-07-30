from setuptools import setup, find_packages, Extension
from Cython.Build import cythonize
import numpy
import os

# Define the extensions
extensions = [
    Extension(
        "indicators.viphl.dto.settings",
        ["src/indicators/viphl/dto/settings.pyx"],
        include_dirs=[numpy.get_include()],
        language="c++",
    ),
    Extension(
        "indicators.viphl.dto.bypoint",
        ["src/indicators/viphl/dto/bypoint.pyx"],
        include_dirs=[numpy.get_include()],
        language="c++",
    ),
    Extension(
        "indicators.viphl.dto.recovery_window",
        ["src/indicators/viphl/dto/recovery_window.pyx"],
        include_dirs=[numpy.get_include()],
        language="c++",
    ),
    Extension(
        "indicators.viphl.dto.hl",
        ["src/indicators/viphl/dto/hl.pyx"],
        include_dirs=[numpy.get_include()],
        language="c++",
    ),
    Extension(
        "indicators.viphl.dto.viphl",
        ["src/indicators/viphl/dto/viphl.pyx"],
        include_dirs=[numpy.get_include()],
        language="c++",
    ),
]

setup(
    name="viphl",
    version="0.1.4",
    author="Your Name",
    author_email="your.email@example.com",
    description="A library for trend analysis and indicators",
    long_description=open("README.md").read() if os.path.exists("README.md") else "",
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/pivot-trend-python",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    ext_modules=cythonize(
        extensions,
        compiler_directives={
            'language_level': 3,
            'embedsignature': True,
        },
    ),
    python_requires=">=3.7",
    install_requires=["numpy>=1.19.0"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
) 