from setuptools import setup, find_packages

with open('README.md', 'r') as f:
    description = f.read()
    
setup(
    name='refinitiv-data-loader',
    version='0.0.3',
    author='Jonathan Willert',
    packages=find_packages(),
    install_requires=[
        'pandas',
        'polars',
        'requests',
    ],
    entry_points={
        'console_scripts': [
            'load=data_loader:main',
        ],
    },
    long_description=description,
    long_description_content_type='text/markdown',
)