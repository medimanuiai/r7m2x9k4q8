from setuptools import setup, find_namespace_packages

setup(
    name="jyothishyam",
    version="0.1.0",
    description="Jyothishyam local editable install for development",
    packages=find_namespace_packages(include=["systems*"]),
    include_package_data=True,
)
