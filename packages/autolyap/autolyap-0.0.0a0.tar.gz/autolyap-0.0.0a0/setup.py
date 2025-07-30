from pathlib import Path
from setuptools import setup, find_packages

this_dir = Path(__file__).parent

setup(
    name="autolyap",
    version="0.0.0a0",                    # use an alpha tag while reserving
    author="Manu Upadhyaya",
    author_email="manu.upadhyaya.42@gmail.com",
    description="Automatic Lyapunov analysis.",
    long_description=(this_dir / "README.md").read_text(encoding="utf-8"),
    long_description_content_type="text/markdown",
    license="MIT",
    python_requires=">=3.9",

    packages=find_packages(),

    install_requires=[
        "numpy>=1.24",
        "matplotlib>=3.7",
        "mosek",
    ],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Topic :: Scientific/Engineering :: Mathematics",
    ],
    project_urls={
        "Source": "https://github.com/AutoLyap/AutoLyap",
    },
)
