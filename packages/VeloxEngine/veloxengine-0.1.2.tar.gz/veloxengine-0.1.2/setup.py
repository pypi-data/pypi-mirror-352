from setuptools import setup, find_packages

setup(
    name="VeloxEngine",
    version="0.1.2",
    author="AynuDaDev",
    description="A minimal SDL2-based game engine in Python for building 2D games quickly.",
    long_description="""
VeloxEngine is a lightweight Python game engine built on SDL2, designed to help you create
2D games with ease and speed.

Pixnox Studio's : https://github.com/Pixnox-Studio

Docs:
https://pixnox-studio.github.io/Velox-Web/
""",
    long_description_content_type="text/markdown",
    url="https://pixnox-studio.github.io/Velox-Web/",
    packages=find_packages(),
    install_requires=[
        "PySDL2",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",

    ],
    python_requires=">=3.7",
)
