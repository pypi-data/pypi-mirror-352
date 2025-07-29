from setuptools import setup, find_packages
import os

# Read the contents of your README file
this_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='likhithapythonlibrary',
    version='0.0.3',
    author='Likhitha Jayavarapu',
    author_email='likhithaswapna703@gmail.com',
    description='Short description of your package',
    long_description=long_description,             # This line is important
    long_description_content_type='text/markdown', # or 'text/x-rst' for reStructuredText
    packages=find_packages(),
    # other args...
)
