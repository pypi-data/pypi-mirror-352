import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="AiSummary",
    version="1.0.0",
    author="Mohammad Taha Gorji",
    author_email="MohammadTahaGorjiProfile@gmail.com",
    description="Text summarization with Ai (without using API)",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=[
    "torch>=1.10.0",
    "transformers>=4.0.0",
    "langdetect>=1.0.9",
    "googletrans>=4.0.0-rc1",
    "spacy>=3.0.0",
    "hazm>=0.7.0",
    "sentencepiece>=0.1.95"
],

)
