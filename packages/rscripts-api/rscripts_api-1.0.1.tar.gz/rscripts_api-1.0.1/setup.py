with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()


from setuptools import setup, find_packages

setup(
    name="rscripts_api",
    version="1.0.1",
    description="A Python wrapper for the Rscripts.net API",
    author="Flames aka Aura",
    packages=find_packages(),
    install_requires=["requests"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    long_description=long_description,
    long_description_content_type="text/markdown",
)
