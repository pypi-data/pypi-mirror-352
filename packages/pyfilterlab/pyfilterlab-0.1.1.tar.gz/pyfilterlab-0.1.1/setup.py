from setuptools import setup, find_packages

setup(
    name='pyfilterlab',
    version='0.1.1',
    description='Digital filter design and visualization toolkit',
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
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
