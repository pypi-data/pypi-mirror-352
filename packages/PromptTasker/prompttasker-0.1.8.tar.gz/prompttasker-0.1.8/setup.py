from setuptools import setup, find_packages

with open("README.md", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="PromptTasker",
    version="0.1.8",
    packages=find_packages(),
    install_requires=[
        "requests",
        "numpy",
        "pandas",
        "pillow",
        "duckdb",
        "mdformat"
    ],
    entry_points={
        'console_scripts': [
            'PromptTasker=PromptTasker.cli:main',  
        ],
    },
    author="Suneha Datta",
    description="A prompt-powered multi-task CLI utility",
    long_description=long_description,
    long_description_content_type="text/markdown",
    python_requires='>=3.7',
)

