from setuptools import setup, find_packages

setup(
    name="lzutils",
    version="1.3",
    description="Simple CLI utility lz",
    author="YourName",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "lz=lzutils.cli:main",
        ],
    },
    python_requires=">=3.6",
)
