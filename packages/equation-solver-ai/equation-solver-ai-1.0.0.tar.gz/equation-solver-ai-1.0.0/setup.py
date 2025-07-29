from setuptools import setup, find_packages

setup(
    name="equation-solver-ai",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "sympy",
        "requests",
        "matplotlib",
        "pillow",
        "psutil"
    ],
    author="John_MC_Python",
    author_email="b297209694@example.com",
    description="A solver for univariate polynomial equations (degree 1-4) with AI support",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/John-is-playing/equation-solver",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.10',
    include_package_data=True,
)