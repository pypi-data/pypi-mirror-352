from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="meritum",
    version="0.3.0",
    author="Mauricio Bedoya",
    author_email=None,
    description="A tool for tracking student progress using Gantt charts and task management",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/maurobedoya/meritum",
    packages=["meritum"],
    package_data={
        "meritum": ["assets/*.png"],
    },
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Education",
        "Topic :: Office/Business :: Scheduling",
    ],
    python_requires=">=3.7",
    install_requires=[
        "customtkinter>=5.2.2",
    ],
    entry_points={
        "console_scripts": [
            "meritum=meritum.meritum:main",
        ],
    },
    include_package_data=True,
)