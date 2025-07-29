import os
from setuptools import find_packages
from setuptools import setup
import pathlib

#####################################################
# Create and distribute Python pkg
#
# To create instalation wheel run cmd command "python -m build"
# from directory the setup.py is located.
#
# To install the resulting wheel localy, run
# "python -m pip install ./dist/rfem-...-py3-none-any.whl".
#####################################################

here = pathlib.Path(__file__).parent
readme = (here/"README.md").read_text(encoding="utf-8")
# version = os.environ.get('PACKAGE_VERSION')
setup(
    name='dlubal.api',
    # version=version,
    version="2.10.9",
    python_requires=">=3.10",
    description='Python Client Library for Dlubal Software APIs powered by gRPC',
    long_description=readme,
    long_description_content_type = "text/markdown",
    # url="https://github.com/Dlubal-Software/RFEM_Python_Client",
    author="Dlubal Software",
    author_email="api@dlubal.com",
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12"
    ],
    package_dir={"": "."},
    packages=find_packages(exclude=["rstab", "rsection", "examples", "__pycache__"]),
    include_package_data=True,
    install_requires=["grpcio==1.68.0", "grpcio-tools==1.68.0", "pandas==2.2.3"], # setuptools
    zip_safe = False
)
