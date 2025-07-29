"""Setup configuration for TFQ0tool package."""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="tfq0tool",            
    version="2.1.5",            
    author="Talal",
    description="A powerful text extraction utility for multiple file formats, including PDFs, Word documents, spreadsheets, and code files.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/tfq0/tfq0tool",
    packages=find_packages(),
    install_requires=[
        "PyPDF2>=3.0.0",
        "python-docx>=0.8.11",
        "openpyxl>=3.1.0",
        "pdfminer.six>=20221105",
        "pytesseract>=0.3.10",
        "Pillow>=9.5.0",
        "tqdm>=4.65.0",
        "chardet>=5.1.0",
    ],
    entry_points={
        "console_scripts": [
            "tfq0tool=tfq0tool.tfq0tool:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Text Processing :: General",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Environment :: Console",
    ],
    python_requires='>=3.8',
    keywords='text extraction pdf docx xlsx ocr',
    project_urls={
        'Bug Reports': 'https://github.com/tfq0/TFQ0tool/issues',
        'Source': 'https://github.com/tfq0/TFQ0tool',
    },
)
