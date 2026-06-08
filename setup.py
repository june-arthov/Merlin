from setuptools import setup, find_packages

setup(
    name="merlin-cli",
    version="3.0.0",
    packages=find_packages(),
    install_requires=[
        "openai>=1.0.0",
        "rich",
        "playwright",
        "chromadb",
    ],
    entry_points={
        "console_scripts": [
            "merlin=merlin.main_launcher:main",
        ],
    },
    author="june-arthov",
    description="Sovereign Tier-3 Auto-Coding Agent",
    license="Apache 2.0",
)
