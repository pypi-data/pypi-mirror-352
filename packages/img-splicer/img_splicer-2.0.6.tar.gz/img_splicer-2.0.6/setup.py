from setuptools import setup, find_packages

long_description = """
This Python package provides a lightweight interface for parsing, constructing, 
and modifying PNG image files using only built-in libraries. It allows users to 
inspect and manipulate PNG file structure at the chunk level, enabling custom 
edits to metadata, color profiles, and raw image data. The library is designed 
for developers who need fine-grained control over PNG internals without 
relying on external imaging dependencies. Ideal for educational purposes, 
format exploration, or crafting minimal image-processing tools, it offers 
a clean and extensible foundation for working directly with the PNG specification.
"""

setup(
    name='img-splicer',
    version='2.0.6',
    packages=find_packages(),
    description='img-splicer',
    long_description_content_type='text/plain',
    long_description=long_description,
    url='https://github.com/Hedroed/png-parser',
    download_url='https://github.com/Hedroed/png-parser',
    project_urls={
        'Documentation': 'https://github.com/Hedroed/png-parser'},
    author='Nathan Rydin',
    author_email='nrydin@alvinnet.com',
    include_package_data=True,
)
