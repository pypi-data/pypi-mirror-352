from setuptools import setup, find_packages

setup(
    name='teon',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[
        'numpy',
        'pygame',
        'moderngl',
        'Pillow'
    ],
)
