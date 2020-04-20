from setuptools import setup, find_packages


with open("README.md", "r") as f:
    long_description = f.read()

setup(
    name="JuBox",
    version="0.1",
    author="Mikael Koli",
    author_email="koli.mikael@op.fi",
    packages=find_packages(),
    description="Object oriented interface to Jupyter Notebook",
    long_description=long_description,
    long_description_content_type="text/markdown",
     classifiers=[
         "Programming Language :: Python :: 3",
     ],
     include_package_data=True # for MANIFEST.in
)
