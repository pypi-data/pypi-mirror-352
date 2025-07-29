from setuptools import setup, find_packages
import os

# Read the contents of README.md file
with open(os.path.join(os.path.dirname(__file__), 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name="getllm",
    version= "0.1.71",
    description="Python LLM operations service for the DevLama ecosystem",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Tom Sapletta",
    author_email="info@softreck.dev",
    license="Apache-2.0",
    packages=find_packages(),
    install_requires=[
        "requests>=2.31.0,<3.0.0",
        "bs4>=0.0.1,<0.0.2",
        "beautifulsoup4>=4.12.2,<5.0.0",
        "python-dotenv>=1.0.0,<2.0.0",
        "questionary>=2.0.1,<3.0.0",
        "appdirs>=1.4.4,<2.0.0"
    ],
    entry_points={
        'console_scripts': [
            'getllm=getllm.cli:main',
        ],
    },
    extras_require={
        'dev': [
            'pytest>=7.4.0',
            'pytest-cov',
            'tox',
            'flake8',
            'black',
            'twine',
            'build',
            'wheel'
        ],
    },
    python_requires='>=3.8,<4.0',
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    url="https://github.com/py-lama/devlama",
    project_urls={
        "Bug Tracker": "https://github.com/py-lama/devlama/issues",
    },
)
