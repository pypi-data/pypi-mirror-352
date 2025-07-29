from setuptools import setup, find_packages

setup(
    name="zeuslab",
    version="1.1.0",
    description="ZeusLab core package — building blocks for agentic AI and intelligent systems.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Zeus Lab",
    author_email="gokulskrishnan74@gmail.com",
    url="https://github.com/zeuslabs-aizeuslab",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    install_requires=[
        "autogen",
        "requests"
    ],
    python_requires='>=3.7',
)
