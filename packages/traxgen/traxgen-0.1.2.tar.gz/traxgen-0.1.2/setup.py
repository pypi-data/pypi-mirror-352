from setuptools import setup, find_packages

setup(
    name="traxgen",  
    version="0.1.2",
    author="anonymous",  
    author_email="",
    description="Trajectory ground truth generator for agentic frameworks",
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    packages=find_packages(include=["traxgen", "traxgen.*"]),
    install_requires=[
        "networkx>=2.8",
        "matplotlib>=3.5",
        "seaborn>=0.11",
        "pydantic>=1.10",
    ],
    python_requires=">=3.8",
)
