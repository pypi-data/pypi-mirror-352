import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="AiSummary",
    version="1.0.1",
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
    "torch",
    "transformers",
    "langdetect",
    "googletrans",
    "spacy",
    "hazm",
    "sentencepiece"
],

)
