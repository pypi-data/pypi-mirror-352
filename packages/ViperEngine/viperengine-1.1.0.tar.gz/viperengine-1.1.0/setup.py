from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="ViperEngine",
    version="1.1.0",
    description="Minimal pygame-like 2D game framework using SDL2 and ctypes",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Aynu",
    packages=find_packages(),
    python_requires='>=3.6',
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Games/Entertainment",
        "Intended Audience :: Developers",
        "Development Status :: 3 - Alpha",
    ],
    install_requires=[],
    entry_points={
        'console_scripts': [
            'velox-sdl2=velox_sdl2.__main__:main',
        ],
    },
)
