from setuptools import setup, find_packages

setup(
    name="teon",
    version="0.6.0",
    author="Mihailo D (YT: @NotMihax)",
    author_email="mickeyyess2@gmail.com",
    description="A simple, beginner-friendly 2D game engine using Pygame and ModernGL",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "pygame",
        "Pillow",
        "moderngl",
        "numpy"
    ],
    keywords="game engine pygame moderngl 2d simple",
)