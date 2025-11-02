from setuptools import setup, find_packages

setup(
    name="appian-analyzer",
    version="1.0.0",
    description="Professional Appian Application Analyzer for Amazon Q Integration",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.7",
    install_requires=[
        "lxml>=4.6.0",
    ],
    entry_points={
        "console_scripts": [
            "appian-analyze=appian_analyzer.cli:main",
        ],
    },
)
