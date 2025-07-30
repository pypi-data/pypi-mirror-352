from setuptools import setup, find_packages

setup(
    name='trainflow',
    version='0.1.0',
    description='A modular batch training interface with metric control.',
    author='ResearchLab',
    packages=find_packages(),
    install_requires=[
        'torch',
        'numpy',
        'tqdm',
        'scikit-learn'
    ],
    python_requires='>=3.6',
)

