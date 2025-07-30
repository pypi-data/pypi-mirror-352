from setuptools import setup, find_packages

setup(
    name="format_tree",
    version="0.1.0",
    description="A utility to plot decision trees with formatted node information.",
    author="kk715",
    author_email="your.email@example.com",
    packages=find_packages(),
    install_requires=[
        "numpy",
        "matplotlib",
        "scikit-learn"
    ],
    python_requires=">=3.6",
    url="https://pypi.org/project/format_tree/",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
