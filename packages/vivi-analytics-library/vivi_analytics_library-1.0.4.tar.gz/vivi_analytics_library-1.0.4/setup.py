from setuptools import find_packages, setup

setup(
    name="vivi_analytics_library",
    version="1.0.4",
    author="Developer",
    description="A library with methods used in data pipelines for analytics and reports.",
    packages=find_packages(),
    install_requires=[
        "aiohttp",
        "pydantic",
    ],
    python_requires=">=3.10",
)
