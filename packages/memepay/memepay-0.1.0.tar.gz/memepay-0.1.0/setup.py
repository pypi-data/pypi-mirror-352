import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="memepay",
    version="0.1.0",
    author="MemePay",
    author_email="support@memepay.lol",
    description="MemePay Python SDK",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://memepay.lol",
    project_urls={
        "Documentation": "https://memepay.lol/docs",
    },
    packages=["memepay"],
    package_dir={"memepay": "."},
    install_requires=[
        "requests",
        "pydantic"
    ],
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
