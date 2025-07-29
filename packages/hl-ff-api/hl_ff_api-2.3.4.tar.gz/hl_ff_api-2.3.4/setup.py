from setuptools import setup, find_packages

setup(
    name="hl_ff_api",
    version="2.3.4",
    author="Haroon Brokha",
    author_email="developers@hlgamingofficial.com",
    description="Python client library for HL Gaming Official Free Fire API",
    long_description="Python client to easily access HL Gaming Official's Free Fire API data.",
    long_description_content_type="text/markdown",
    packages=find_packages(),
    install_requires=[
        "requests",
    ],
    python_requires=">=3.6",
    url="https://www.hlgamingofficial.com/p/api.html",
    project_urls={
        "Documentation": "https://www.hlgamingofficial.com/p/free-fire-api-data-documentation.html",
        "Homepage": "https://www.hlgamingofficial.com",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: MIT License",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)
