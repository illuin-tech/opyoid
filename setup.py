import os

import setuptools

with open(os.path.join(os.path.dirname(__file__), "README.md")) as readme:
    long_description = readme.read()

setuptools.setup(
    name="opyoid",
    version="DEV",
    url="https://github.com/illuin-tech/opyoid/",

    author="Illuin Technology",
    author_email="contact@illuin.tech",

    description="Dependency injection library",
    long_description=long_description,
    long_description_content_type="text/markdown",

    zip_safe=False,
    platforms="any",

    install_requires=[
        "attrs>=19.1.0,<23.0.0"
    ],
    python_requires=">=3.6,<4.0",
    packages=setuptools.find_packages(include=["opyoid", "opyoid.*"]),

    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Software Development :: Libraries",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)
