from setuptools import setup, find_packages

setup(
    name='pyfilterlab',
    version='0.1.0',
    description='Digital filter design and visualization toolkit',
    author='Shinjan Saha',
    author_email='shinjansaha02@gmail.com',
    packages=find_packages(),
    install_requires=[
        'numpy',
        'scipy',
        'matplotlib'
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'Topic :: Scientific/Engineering',
    ],
    python_requires='>=3.7',
)
