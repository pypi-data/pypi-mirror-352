from setuptools import setup, find_packages

setup(
    name="flowscale",
    version="1.1.0b1",
    packages=find_packages(),
    install_requires=[
        "requests>=2.25.0",
        "urllib3>=1.25.0",
    ],
    extras_require={
        "websocket": ["websocket-client>=1.0.0"],
    },
    author="flowscale",
    author_email="rupayan@example.com",
    description="A Python library for communicating with the Flowscale APIs",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/flowscale/flowscale-python",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.10",
)