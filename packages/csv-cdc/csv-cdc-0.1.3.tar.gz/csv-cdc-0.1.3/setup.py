from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="csv-cdc",
    version="1.0.1",
    author="Mauro Bartolomeu dos Reis",
    author_email="maurohktga@gmail.com",
    description="A high-performance CSV Change Data Capture tool",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/maurohkcba/csv-cdc",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Utilities",
        "Topic :: Text Processing",
    ],
    python_requires=">=3.7",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "csvcdc=csvcdc:main",
            "csv-cdc=csvcdc:main"
        ],
    },
    keywords="csv, diff, cdc, change-data-capture, data-comparison, file-comparison",
    project_urls={
        "Bug Reports": "https://github.com/maurohkcba/csv-cdc/issues",
        "Source": "https://github.com/maurohkcba/csv-cdc/",
        "Documentation": "https://github.com/maurohkcba/csv-cdc/wiki",
    },
    use_scm_version={
    "local_scheme": "no-local-version",
    },
    setup_requires=["setuptools_scm"],
)