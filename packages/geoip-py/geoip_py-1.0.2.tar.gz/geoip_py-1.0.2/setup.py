from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="geoip-py",
    version="1.0.2",
    author="Malith Rukshan",
    author_email="hello@malith.dev",
    description="Self-hosted IP geolocation library and API with currency support that works completely offline!",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Malith-Rukshan/geoip-api",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.9",
    install_requires=[
        "geoip2==5.1.0",
        "requests>=2.32.3",
        "pycountry>=24.6.1",
    ],
    extras_require={
        "dev": ["pytest>=6.0", "black", "isort", "mypy", "flake8"],
    },
)
