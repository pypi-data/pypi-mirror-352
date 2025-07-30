from setuptools import setup, find_packages

setup(
    name="ai-api-test-docs",
    version="0.1.0",
    description="AI-powered API test and documentation generator using Gemini",
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