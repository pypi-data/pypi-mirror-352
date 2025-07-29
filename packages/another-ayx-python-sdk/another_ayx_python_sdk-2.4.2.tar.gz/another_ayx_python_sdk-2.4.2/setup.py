from setuptools import setup, find_packages
import os

# Read version from version.py
with open(os.path.join("another_ayx_python_sdk", "version.py"), "r") as f:
    exec(f.read())

setup(
    name="another-ayx-python-sdk",
    version="2.4.2",  # This will be read from version.py
    description="Python SDK for Alteryx Plugin Development and Testing",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Jupiter Bakakeu",
    author_email="jupiter.bakakeu@gmail.com",
    maintainer="Jupiter Bakakeu",
    maintainer_email="jupiter.bakakeu@gmail.com",
    license="MIT",
    license_files=["LICENSE"],
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Software Development :: Build Tools",
        "Topic :: Software Development :: Testing",
        "Environment :: Console",
    ],
    packages=find_packages(
        exclude=["tests*", "docs*", "__pycache__", "**/__pycache__", "**/*.pyc", "**/__pycache__/"]
    ),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        "pydantic",
        "packaging",
        "setuptools>=65.5.0",
        "pyarrow",
        "xmltodict",
        "pyyaml",
        "requests",
        "another-ayx-plugin-cli==1.2.3",
        "typing-extensions",
        "pypac",
        "pandas",
        "numpy",
        "deprecation",
        "grpcio",
        "grpcio-tools",   
        "protobuf",
        "psutil", 
        "Click",
        "python-dateutil",
        "pytz",
        "six",
        "typer",
        "wincertstore"
    ],
    extras_require={
        "dev": [
            "pytest",
            "pytest-cov",
            "black",
            "isort",
            "flake8",
            "mypy",
        ]
    },
    entry_points={
        "console_scripts": [
            "another-ayx-python-sdk=another_ayx_python_sdk.__main__:main",
        ],
    },
    package_data={
        "another_ayx_python_sdk": [
            "assets/*",
            "cli/*",
            "core/**/*",
            "docs/**/*",
            "examples/**/*",
            "providers/**/*",
            "test_harness/**/*",
            "providers/amp_provider/resources/generated/*",
        ],
    },
    project_urls={
        "Homepage": "https://github.com/jupiterbak/another-ayx-python-sdk",
        "Repository": "https://github.com/jupiterbak/another-ayx-python-sdk.git",
    },
) 