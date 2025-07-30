"""
Setup script for python_midjourney package
"""

from setuptools import find_packages, setup

# Read README.md file
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="python_midjourney",
    version="1.0.0",
    author="ooeunoo",
    author_email="seongeun.cho.dev@gmail.com",
    description="Midjourney automation system using Discord user tokens",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ooeunoo/python_midjourney",
    packages=find_packages(),
    license="MIT",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers", 
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Communications :: Chat",
        "Topic :: Multimedia :: Graphics",
    ],
    python_requires=">=3.7",
    install_requires=[
        "requests>=2.25.0",
        "Pillow>=8.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "black>=21.0",
            "flake8>=3.8",
        ],
    },
    keywords="midjourney discord automation image generation ai art",
    project_urls={
        "Bug Reports": "https://github.com/ooeunoo/python_midjourney/issues",
        "Source": "https://github.com/ooeunoo/python_midjourney",
        "Documentation": "https://github.com/ooeunoo/python_midjourney#readme",
    },
) 