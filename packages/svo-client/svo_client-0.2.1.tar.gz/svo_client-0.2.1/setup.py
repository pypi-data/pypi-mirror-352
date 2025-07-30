from setuptools import setup, find_packages

setup(
    name="svo-client",
    version="0.2.1",
    description="Async client for SVO semantic chunker microservice.",
    author="Your Name",
    author_email="your@email.com",
    packages=find_packages(),
    install_requires=[
        "aiohttp>=3.8.0",
        "pydantic>=2.0.0",
        "chunk_metadata_adapter"
    ],
    python_requires=">=3.8",
    url="https://github.com/your_org/svo_client",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    include_package_data=True,
) 