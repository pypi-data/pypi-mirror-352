from setuptools import setup

installation_requirements = [
    "openai-agents==0.0.16",
    "openai==1.84.0",
    "loguru==0.7.3",
    "neo4j==5.28.1",
    "google-genai==1.12.1"
]

setup(
    version="0.16",
    name="freeflock-contraptions",
    description="A collection of contraptions",
    author="(~)",
    url="https://github.com/freeflock/contraptions",
    package_dir={"": "packages"},
    packages=["freeflock_contraptions"],
    install_requires=installation_requirements,
)
