from setuptools import setup, find_packages

setup(
    name='mkxcli',
    version='0.4',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'make = mkxcli.make:main',
            'encode = mkxcli.encode:main',
            'decode = mkxcli.decode:main',
        ],
    },
    install_requires=[],
    author='Martin V.',
    description='Simple CLI tools for make, encode, decode',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    python_requires='>=3.6',
)
