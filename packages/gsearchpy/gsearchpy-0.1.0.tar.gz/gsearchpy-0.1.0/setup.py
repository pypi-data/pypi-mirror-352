from setuptools import setup, find_packages

setup(
    name="gsearchpy",
    version="0.1.0",
    description="A simple Python package for performing Google searches",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Aman Gupta",
    author_email="itsamangupta365@gmail.com",
    url="https://github.com/itsguptaaman/gsearchpy",
    packages=find_packages(),
    install_requires=[
        "seleniumbase",
        "user_agent",
        "curl_cffi",
        "bs4",
        "lxml",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    entry_points={
        'console_scripts': [
            'gsearchpy = gsearchpy.cli:main',
        ],
    },
)
