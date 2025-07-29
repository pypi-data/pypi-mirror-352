from setuptools import setup, find_packages, Extension
from Cython.Build import cythonize
import numpy

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

setup(
    name="viphl",
    version="0.1.0",
    description="VipHL Trading Indicator Library",
    author="",
    author_email="",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "numpy",
        "pandas",
    ],
    ext_modules=cythonize(
        extensions,
        compiler_directives={
            'language_level': 3,
            'embedsignature': True,
        },
    ),
    python_requires=">=3.7",
    zip_safe=False,
) 