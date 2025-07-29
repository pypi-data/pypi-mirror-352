from setuptools import setup, find_packages

setup(
    name="impkinpy",
    __version__="1.0.0",
    author="Vitek",
    author_email="cheeseqwertycheese@gmail.com",
    description="Library for mechanics and astronomy",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/Viktor640266/impkinpy",
    packages=find_packages(),
        install_requires=[
        "numpy",
        "scipy",
        "matplotlib"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
)