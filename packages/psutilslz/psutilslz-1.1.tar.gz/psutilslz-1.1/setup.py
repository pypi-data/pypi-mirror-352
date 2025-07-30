from setuptools import setup, find_packages

setup(
    name="psutilslz",
    version="1.1",
    description="CLI utility to SSH file content and run v.py",
    author="ubuntu",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "lz=utilslz.cli:main",
        ],
    },
    python_requires=">=3.6",
)
