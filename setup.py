from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="easy-s3-multipart",
    version="0.1.0",
    author="Arpit",
    author_email="arpit.thukral@gmail.com",
    description="Production-ready S3 multipart upload handler for FastAPI",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/arpit0515/easy-s3-multipart",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Framework :: FastAPI",
    ],
    python_requires=">=3.8",
    install_requires=[
        "boto3>=1.26.0",
        "pydantic>=2.0.0",
        "fastapi>=0.100.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "black>=23.0.0",
            "isort>=5.12.0",
            "mypy>=1.0.0",
            "moto>=4.0.0",  # For mocking AWS services
        ],
    },
)
