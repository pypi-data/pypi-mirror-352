from setuptools import setup, find_packages

setup(
    name="audit-trail-lib",
    version="0.1.0",
    author="Your Name",
    description="Audit trail library with JSON persistence",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    # package_dir={"": "src"},
    packages=find_packages(where="src"),
    install_requires=[
        "pydantic>=1.10.0"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
    python_requires=">=3.7",
)
