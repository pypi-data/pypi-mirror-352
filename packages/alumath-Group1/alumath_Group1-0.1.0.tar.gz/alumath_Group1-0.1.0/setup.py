# setup.py
from setuptools import setup, find_packages

# Read the README file for the long description
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='alumath_Group1',
    version='0.1.0',
    author='Peer_Group1',
    author_email='d.ganza@alustudent.com',
    description='A Python library for advanced matrix operations, including multiplication.',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/Flo-renc/ML_peer_group_1_F-A.git',
    packages=find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Topic :: Scientific/Engineering :: Mathematics',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    python_requires='>=3.6',
    # No external dependencies needed for basic matrix multiplication
    # install_requires=[
    #     'numpy', # Uncomment if you decide to use numpy internally
    # ],
)