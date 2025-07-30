from setuptools import setup, find_packages, Extension
from Cython.Build import cythonize
import numpy
import os
import sys

# Define the extension modules paths
ext_modules = []
source_files = []

# Base paths for Cython and C++ files
src_dir = "src/indicators/viphl/dto"
modules = [
    "settings",
    "bypoint",
    "recovery_window",
    "hl",
    "viphl",
]

# Check if we're building from source distribution or from development
# Development: .pyx files exist
# Source distribution: .cpp files exist but .pyx files don't
has_pyx = False
has_cpp = False

# Check for existence of source files
for module in modules:
    pyx_file = f"{src_dir}/{module}.pyx"
    cpp_file = f"{src_dir}/{module}.cpp"
    
    if os.path.exists(pyx_file):
        has_pyx = True
        source_files.append((module, pyx_file, "c++"))
    elif os.path.exists(cpp_file):
        has_cpp = True
        source_files.append((module, cpp_file, "c++"))
    else:
        print(f"Warning: Neither {pyx_file} nor {cpp_file} exists")

if not source_files:
    print("Error: No source files found for extension modules")
    sys.exit(1)

# Create extension modules based on available files
for module, source_file, language in source_files:
    ext_modules.append(
        Extension(
            f"indicators.viphl.dto.{module}",
            [source_file],
            include_dirs=[numpy.get_include()],
            language=language,
        )
    )

# Use cythonize if we have .pyx files, otherwise use extensions directly
if has_pyx:
    print("Using Cython to build extensions from .pyx files")
    ext_modules = cythonize(
        ext_modules,
        compiler_directives={
            'language_level': 3,
            'embedsignature': True,
        },
    )
else:
    print("Building extensions from pre-compiled .cpp files")

setup(
    name="viphl",
    version="0.1.5",
    author="Your Name",
    author_email="your.email@example.com",
    description="A library for trend analysis and indicators",
    long_description=open("README.md").read() if os.path.exists("README.md") else "",
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/pivot-trend-python",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    ext_modules=ext_modules,
    python_requires=">=3.7",
    install_requires=["numpy>=1.19.0"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
) 