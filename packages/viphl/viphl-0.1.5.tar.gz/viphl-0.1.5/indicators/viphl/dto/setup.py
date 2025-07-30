from setuptools import setup, Extension
from Cython.Build import cythonize
import numpy

# Define the extensions
extensions = [
    Extension(
        "settings",
        ["settings.pyx"],
        include_dirs=[numpy.get_include()],
        language="c++",
    ),
    Extension(
        "bypoint",
        ["bypoint.pyx"],
        include_dirs=[numpy.get_include()],
        language="c++",
    ),
    Extension(
        "recovery_window",
        ["recovery_window.pyx"],
        include_dirs=[numpy.get_include()],
        language="c++",
    ),
    Extension(
        "hl",
        ["hl.pyx"],
        include_dirs=[numpy.get_include()],
        language="c++",
    ),
    Extension(
        "viphl",
        ["viphl.pyx"],
        include_dirs=[numpy.get_include()],
        language="c++",
    ),
]

setup(
    name="viphl_cython",
    ext_modules=cythonize(extensions, compiler_directives={'language_level': 3}),
    zip_safe=False,
) 