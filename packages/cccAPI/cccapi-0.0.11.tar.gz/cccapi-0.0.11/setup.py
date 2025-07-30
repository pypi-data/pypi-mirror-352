from setuptools import setup, find_packages

setup(
    name="cccAPI",
    version="0.0.11",
    description="A Python client for interacting with the CCC API",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Aalap Tripathy",
    author_email="atripathy.bulk@gmail.com",
    url="https://github.com/atripathy86/cccAPI",
    license="MIT",
    packages=find_packages(where=".") + ["cccAPI.definitions"],  # Explicitly add cccAPI.definitions
    include_package_data=True,  # Include non-Python files specified in MANIFEST.in
    install_requires=[
        "requests>=2.25.1",
        "jsonschema>=4.23.0",
    ],
    python_requires=">=3.6",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)