from setuptools import setup, find_packages, Extension
import numpy
import os
import sys

# Check if we're building from source or from a source distribution
# If building from source, Cython will be required
if os.path.exists('indicators/viphl/dto/settings.pyx'):
    try:
        from Cython.Build import cythonize
        USE_CYTHON = True
    except ImportError:
        print("Cython not found, falling back to pre-built C/C++ files")
        USE_CYTHON = False
else:
    # Not building from source, assume C/C++ files already exist
    USE_CYTHON = False

# Define the extensions for modules
ext_modules = []
if USE_CYTHON:
    # Define the extensions for Cython modules
    extensions = [
        Extension(
            "indicators.viphl.dto.settings",
            ["indicators/viphl/dto/settings.pyx"],
            include_dirs=[numpy.get_include()],
            language="c++",
        ),
        Extension(
            "indicators.viphl.dto.bypoint",
            ["indicators/viphl/dto/bypoint.pyx"],
            include_dirs=[numpy.get_include()],
            language="c++",
        ),
        Extension(
            "indicators.viphl.dto.recovery_window",
            ["indicators/viphl/dto/recovery_window.pyx"],
            include_dirs=[numpy.get_include()],
            language="c++",
        ),
        Extension(
            "indicators.viphl.dto.hl",
            ["indicators/viphl/dto/hl.pyx"],
            include_dirs=[numpy.get_include()],
            language="c++",
        ),
    ]
    
    # If you have a viphl.pyx file, add it here too
    try:
        with open("indicators/viphl/viphl.pyx", "r") as f:
            extensions.append(
                Extension(
                    "indicators.viphl.viphl",
                    ["indicators/viphl/viphl.pyx"],
                    include_dirs=[numpy.get_include()],
                    language="c++",
                )
            )
    except FileNotFoundError:
        pass
        
    ext_modules = cythonize(
        extensions,
        compiler_directives={
            'language_level': 3,
            'embedsignature': True,
        },
    )
else:
    # If not using Cython, use the pre-built C/C++ files
    extensions = [
        Extension(
            "indicators.viphl.dto.settings",
            ["indicators/viphl/dto/settings.c"],
            include_dirs=[numpy.get_include()],
        ),
        Extension(
            "indicators.viphl.dto.bypoint",
            ["indicators/viphl/dto/bypoint.c"],
            include_dirs=[numpy.get_include()],
        ),
        Extension(
            "indicators.viphl.dto.recovery_window",
            ["indicators/viphl/dto/recovery_window.c"],
            include_dirs=[numpy.get_include()],
        ),
        Extension(
            "indicators.viphl.dto.hl",
            ["indicators/viphl/dto/hl.c"],
            include_dirs=[numpy.get_include()],
        ),
    ]
    
    # If you have a viphl.c file, add it here too
    if os.path.exists("indicators/viphl/viphl.c"):
        extensions.append(
            Extension(
                "indicators.viphl.viphl",
                ["indicators/viphl/viphl.c"],
                include_dirs=[numpy.get_include()],
            )
        )
    
    ext_modules = extensions

setup(
    name="viphl",
    version="0.1.1",
    description="VipHL Trading Indicator Library",
    author="",
    author_email="",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "numpy",
        "pandas",
    ],
    ext_modules=ext_modules,
    python_requires=">=3.7",
    zip_safe=False,
) 