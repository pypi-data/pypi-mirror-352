from setuptools import setup, find_packages

setup(
    name="VeloxEngine",
    version="0.1.0",
    description="Lightweight SDL2 wrapper for 2D games",
    author="Pixnox Studio's",
    packages=find_packages(),
    include_package_data=True,
    install_requires=["PySDL2"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
