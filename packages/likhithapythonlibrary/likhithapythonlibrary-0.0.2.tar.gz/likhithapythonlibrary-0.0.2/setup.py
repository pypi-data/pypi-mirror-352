from setuptools import setup, find_packages

with open('README.md', 'r') as f:
    long_description = f.read()

setup(
    name='likhithapythonlibrary',
    version='0.0.2',
    description='A simple calculator library',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Likhitha Jayavarapu',
    author_email='likhithaswapna703@gmail.com',
    url='https://github.com/jayavarapulikhitha/pyliblikhitha',
    license='MIT',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Education',
        'Operating System :: Microsoft :: Windows :: Windows 10',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3'
    ],
    keywords='calculator, arithmetic, math',
    packages=find_packages(),
    install_requires=[],
)
