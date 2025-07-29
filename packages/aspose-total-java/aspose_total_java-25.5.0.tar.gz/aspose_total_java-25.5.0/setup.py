from setuptools import setup

NAME = "aspose-total-java"
VERSION = "25.5.0"

# Common dependencies without JPype1 conflicts
COMMON_REQUIRES = [
    "aspose-cells==25.5.0",
    "aspose-diagram==25.5.0",
    "aspose-ocr-python-java==25.2.0",
    "aspose-pdf-for-python-via-java==24.9",
]

# Dependencies that have JPype1 conflicts
EXTRAS_REQUIRE = {
    # Requires JPype1==1.4.1
    "barcode": ["aspose-barcode-for-python-via-java==25.5.0", "JPype1==1.4.1"],
    
    # Requires JPype1>=1.5.0
    "slides": ["aspose-slides-java==24.6.0", "JPype1>=1.5.0"],
    
    # Full install (Choose latest JPype1)
    "full": ["aspose-barcode-for-python-via-java==25.5.0",
             "aspose-slides-java==24.6.0",
             "JPype1>=1.5.0"],
}

setup(
    name=NAME,
    version=VERSION,
    description="Aspose.Total for Python via Java is a file format processing library...",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="Aspose",
    author_email="total@aspose.com",
    url="https://products.aspose.com/total/python-java",
    packages=["aspose-total-java"],
    include_package_data=True,
    install_requires=COMMON_REQUIRES,
    extras_require=EXTRAS_REQUIRE,  # Allows optional installations
    classifiers=[
        "Programming Language :: Python :: 3.5",
        "License :: Other/Proprietary License",
    ],
    python_requires=">=3.5",
)
