from setuptools import setup, find_packages

setup(
    name="dfp-protocol",
    version="0.1.0",
    author="Tarun N",
    description="Data Flag Protocol (DFP): A lightweight client-server TCP protocol",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    entry_points={
        'console_scripts': [
            'dfp-server=examples.run_server:main',
            'dfp-client=examples.run_client:main',
        ],
    },
)
