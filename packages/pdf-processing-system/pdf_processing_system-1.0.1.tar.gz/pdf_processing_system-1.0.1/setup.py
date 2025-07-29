from setuptools import setup, find_packages

# Read the README file
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Read requirements
# Note: Installation may show dependency conflicts with packages like Streamlit
# that require older versions of Pillow (<11) and packaging (<24).
# These conflicts are harmless and do not affect functionality.
with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="pdf-processing-system",
    version="1.0.1",
    author="goliathuy",
    author_email="aug1381-goliathuy@yahoo.com",
    description="Comprehensive PDF content extraction and intelligent splitting system",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/goliathuy/pdf-extractor",
    packages=find_packages(),
    py_modules=["extract_pdf_content", "pdf_cli"],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Office/Business :: Office Suites",
        "Topic :: Text Processing :: Filters",
        "Topic :: Multimedia :: Graphics :: Graphics Conversion",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "pdf-cli=pdf_cli:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["config.json", "samples/*.pdf"],
    },
    keywords="pdf extraction text images splitting cli processing",    project_urls={
        "Bug Reports": "https://github.com/goliathuy/pdf-extractor/issues",
        "Source": "https://github.com/goliathuy/pdf-extractor",
        "Documentation": "https://github.com/goliathuy/pdf-extractor#readme",
    },
)
