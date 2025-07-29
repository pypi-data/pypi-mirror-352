from setuptools import setup, find_packages

setup(
    name="chunk_retriever_client",
    version="0.2.0",
    description="Asynchronous client for Chunk Retriever microservice.",
    author="Your Name",
    author_email="your@email.com",
    packages=find_packages(),
    install_requires=[
        "aiohttp>=3.8.0",
    ],
    python_requires=">=3.8",
    include_package_data=True,
    url="",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
) 