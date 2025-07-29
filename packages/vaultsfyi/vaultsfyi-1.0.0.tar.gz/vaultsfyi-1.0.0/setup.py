from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="vaultsfyi",
    version="1.0.0",
    author="Kaimi Seeker",
    author_email="kaimi@wallfacer.io",
    description="A Python SDK for interacting with the Vaults.fyi API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/kaimiseeker/vaults-fyi-python",
    packages=find_packages(),
    include_package_data=True,
    package_data={
        'vaultsfyi': ['py.typed'],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    keywords="defi, vaults, yield, ethereum, web3, crypto",
    project_urls={
        "Bug Reports": "https://github.com/kaimiseeker/vaults-fyi-python/issues",
        "Source": "https://github.com/kaimiseeker/vaults-fyi-python",
        "Documentation": "https://github.com/kaimiseeker/vaults-fyi-python#readme",
    },
)