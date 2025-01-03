from setuptools import setup, find_packages

setup(
    name="cyberhack",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "pygame>=2.5.2",
        "python-dotenv>=1.0.0",
        "pillow>=10.0.0",
    ],
    entry_points={
        "console_scripts": [
            "cyberhack=src.main:main",
        ],
    },
    author="Votre Nom",
    description="Un jeu de hacking cyberpunk",
    python_requires=">=3.8",
) 