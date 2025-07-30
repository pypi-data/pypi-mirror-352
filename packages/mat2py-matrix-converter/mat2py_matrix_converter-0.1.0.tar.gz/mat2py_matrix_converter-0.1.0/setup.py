from setuptools import setup, find_packages

setup(
    name='mat2py_matrix_converter',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[],
    author='Angelos Guan',
    description='A small utility to convert MATLAB-style matrix strings to Python/torch syntax',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/AngelosGuan/mat2py_matrix_converter.git',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
    ],
    python_requires='>=3.6',
)
