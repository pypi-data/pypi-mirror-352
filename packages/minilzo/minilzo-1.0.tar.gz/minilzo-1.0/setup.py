from setuptools import setup, Extension

include_dirs = []
define_macros = []
library_dirs = []
libraries = []
runtime_library_dirs = []
extra_objects = []
extra_compile_args = []
extra_link_args = []

ext = Extension(
    name="_minilzo",
    sources=["lzomodule.c", "minilzo.c"],
    include_dirs=include_dirs,
    define_macros=define_macros,
    library_dirs=library_dirs,
    libraries=libraries,
    runtime_library_dirs=runtime_library_dirs,
    extra_objects=extra_objects,
    extra_compile_args=extra_compile_args,
    extra_link_args=extra_link_args,
)

setup(
    name='minilzo',
    version='1.0',
    description='This is a python library deals with lzo files compressed with lzop.',
    long_description=open('README', 'r').read(),
    long_description_content_type='text/markdown',
    license=open('COPYING', 'r').read(),
    author="ir193",
    author_email="iridiummx@gmail.com",
    maintainer="Myldero",
    url='https://github.com/Myldero/python-minilzo',
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: C",
    ],
    python_requires=">=3",
    py_modules=['minilzo'],
    ext_modules=[ext])

