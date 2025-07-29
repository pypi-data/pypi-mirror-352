from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="ceco",
    version="1.0.10",
    author="muhammad hanif ramadhani",
    author_email="mhaniframadhani985@gmail.com",
    url="https://github.com/haniframadhani/cecopy",
    packages=find_packages(exclude=['test*', 'docs*']),
    extras_require={
        "dev": ["pytest>=7.0", "twine>=4.0.2"],
    },
    python_requires=">=3.6",
    install_requires=['numpy>=1.19.0'],
    long_description=long_description,
    long_description_content_type="text/markdown",
)
