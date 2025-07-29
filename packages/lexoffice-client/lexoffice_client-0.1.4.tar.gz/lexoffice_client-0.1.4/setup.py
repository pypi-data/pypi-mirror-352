from setuptools import setup, find_packages

setup(
    name="lexoffice-client",
    version="0.1.4",
    author="James Maguire",
    author_email="jvm986@gmail.com",
    description="A Python client for the Lexoffice API",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/jvm986/lexoffice-client",
    packages=find_packages(),
    include_package_data=True,
    package_data={
        "lexoffice_client": ["py.typed", "**/*.pyi"],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=["email_validator", "httpx", "pydantic"],
)
