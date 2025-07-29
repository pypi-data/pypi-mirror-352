from setuptools import setup, find_packages

setup(
    name="png2gobytes",
    version="0.1.0",
    description="Convert PNG files to Go byte slices for systray icons",
    author="Your Name",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "png2gobytes=png2gobytes.__main__:main"
        ]
    },
    python_requires=">=3.6",
)
