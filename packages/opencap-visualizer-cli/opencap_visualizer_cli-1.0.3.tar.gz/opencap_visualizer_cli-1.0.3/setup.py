from setuptools import setup, find_packages
import os

# Read the contents of README file
this_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_directory, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="opencap-visualizer-cli",
    version="1.0.3",
    author="OpenCap Team",
    author_email="your-email@example.com",
    description="Command-line tool for generating videos from OpenCap biomechanics JSON files",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/your-username/opencap-visualizer",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering",
        "Topic :: Multimedia :: Video",
    ],
    python_requires=">=3.8",
    install_requires=[
        "playwright>=1.40.0",
        "pathlib",
        "aiohttp>=3.8.0",
    ],
    extras_require={
        "dev": [
            "pytest",
            "black",
            "flake8",
        ],
    },
    entry_points={
        "console_scripts": [
            "opencap-visualizer=visualizer_cli:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["dist/**/*", "public/**/*"],
    },
    zip_safe=False,
    project_urls={
        "Bug Reports": "https://github.com/your-username/opencap-visualizer/issues",
        "Source": "https://github.com/your-username/opencap-visualizer",
    },
) 