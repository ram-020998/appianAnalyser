from setuptools import setup, find_packages

setup(
    name="appian-analyzer",
    version="2.0.0",
    description="Professional Appian Application Analyzer",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.7",
    entry_points={
        "console_scripts": [
            "appian-analyzer=appian_analyzer.analyzer:main",
        ],
    },
)
