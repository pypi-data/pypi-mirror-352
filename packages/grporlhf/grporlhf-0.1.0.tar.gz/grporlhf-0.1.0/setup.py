from setuptools import setup, find_packages

setup(
    name="grporlhf",
    version="0.1.0",
    packages=find_packages(include=["grporlhf*"]),
    install_requires=[
        "torch>=2.2,<2.4",
        "transformers>=4.41.2,<4.43",
        "peft>=0.11.0",
        "datasets>=2.20.0",
        "pyyaml",
        "tqdm",
    ],
    entry_points={
        'console_scripts': [
            'grporlhf = grporlhf.cli:main',
        ],
    },
    author="Kaushik D. (Not associated with DeepSeek -- Demo Implementation)",
    author_email="dwivedi.kaushik24@gmail.com",
    description="Reference implementation of Group Relative Policy Optimization (GRPO) by DeepSeek",
    license="Apache-2.0",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.9',
    url="https://github.com/kaushikd24/GRPO-Package",
    long_description_content_type='text/markdown',
) 