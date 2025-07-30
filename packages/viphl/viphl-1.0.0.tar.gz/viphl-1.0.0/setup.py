from setuptools import setup, find_packages, Extension
from Cython.Build import cythonize
import numpy
import os
import sys

# Define the extension modules paths
ext_modules = []
source_files = []

# Base paths for Cython and C++ files
src_dir = "src/viphl/dto"
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

# Create __init__.py files if they don't exist
def ensure_init_files():
    dirs = ["src/viphl", "src/viphl/dto"]
    for d in dirs:
        os.makedirs(d, exist_ok=True)
        init_file = os.path.join(d, "__init__.py")
        if not os.path.exists(init_file):
            with open(init_file, "w") as f:
                f.write("# Package namespace\n")
            print(f"Created {init_file}")

ensure_init_files()

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
            f"viphl.dto.{module}",
            [source_file],
            include_dirs=[numpy.get_include(), "src"],  # Include src for relative imports
            language=language,
            define_macros=[("NPY_NO_DEPRECATED_API", "NPY_1_7_API_VERSION")],
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
            'c_string_type': 'str',
            'c_string_encoding': 'utf8',
        },
        include_path=["src"],  # This helps with relative imports
    )
else:
    print("Building extensions from pre-compiled .cpp files")

setup(
    name="viphl",
    version="1.0.0",
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