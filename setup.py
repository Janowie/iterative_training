import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="iterative-training-pkg-janowie",
    version="0.0.5",
    author="Krcmar Jan",
    author_email="krcmar.jan@gmail.com",
    description="Package providing utilities for experiments on iterative training.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Janowie/iterative_training",
    project_urls={
        "Bug Tracker": "https://github.com/Janowie/iterative_training/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.6",
)
