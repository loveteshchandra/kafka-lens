#!/usr/bin/env python3
"""Setup script for Kafka Lens."""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="kafka-lens",
    version="1.0.0",
    author="Kafka Lens",
    description="A CLI tool for Kafka cluster management and monitoring",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.7",
    install_requires=[
        "PyYAML>=6.0.1",
        "boto3>=1.34.0",
        "kafka-python>=2.0.2",
        "click>=8.1.7",
        "colorama>=0.4.6",
    ],
    entry_points={
        "console_scripts": [
            "kafka-lens=kafka_lens:cli",
            "kl=kafka_lens:cli",
        ],
    },
)
