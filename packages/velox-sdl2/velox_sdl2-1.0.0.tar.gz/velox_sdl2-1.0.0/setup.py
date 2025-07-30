from setuptools import setup, find_packages

setup(
    name="velox_sdl2",
    version="1.0.0",
    description="Minimal pygame-like 2D game framework using SDL2 and ctypes",
    author="Aynu",
    packages=find_packages(),
    python_requires='>=3.6',
    classifiers=[
    ],
    install_requires=[],
    entry_points={
        'console_scripts': [
            'velox-sdl2=velox_sdl2.__main__:main',
        ],
    },
)
