import setuptools

setuptools.setup(
    name="illuin_inject",
    version="DEV",
    url="https://gitlab.illuin.tech/bot-factory/illuin-inject/",

    author="Illuin Technology",
    author_email="contact@illuin.tech",

    description="Dependency injection library",

    zip_safe=False,
    platforms="any",

    install_requires=[
        "attrs>=19.1.0,<20.0.0"
    ],
    python_requires=">=3.6,<4.0",
    packages=setuptools.find_packages(include=["illuin_inject", "illuin_inject.*"]),

    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
    ],
)
