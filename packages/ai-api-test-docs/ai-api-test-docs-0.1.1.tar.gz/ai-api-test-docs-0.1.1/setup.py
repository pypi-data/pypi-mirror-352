from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="ai-api-test-docs",
    version="0.1.1",
    description="AI-powered API test and documentation generator using Gemini",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Ezeana Micheal",
    packages=find_packages(),
    install_requires=[
        "google-generativeai>=0.6.9",
        "python-dotenv>=1.0.0"
    ],
    entry_points={
        "console_scripts": [
            "ai-api-test-docs=ai_api_docs.cli:main"
        ]
    },
    python_requires=">=3.9",
    license="MIT",
)