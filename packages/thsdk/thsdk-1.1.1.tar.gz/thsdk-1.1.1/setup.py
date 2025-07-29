import codecs
import os
from setuptools import setup

# these things are needed for the README.md show on pypi
here = os.path.abspath(os.path.dirname(__file__))

with codecs.open(os.path.join(here, "README.md"), encoding="utf-8") as fh:
    long_description = "\n" + fh.read()

about = {}
with codecs.open(os.path.join(here, "thsdk", "__version__.py"), "r", "utf-8") as f:
    exec(f.read(), about)

setup(
    name=about["__title__"],
    version=about["__version__"],
    author=about["__author__"],
    author_email=about["__author_email__"],
    description=about["__description__"],
    long_description_content_type="text/markdown",
    long_description=long_description,
    packages=["thsdk"],
    include_package_data=True,
    python_requires=">=3.9",
    install_requires=[],
    keywords=['python', 'thsdk'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Programming Language :: Python :: 3 :: Only",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ],
    package_data={
        'thsdk': ['*', 'example/*'],
    },
)
