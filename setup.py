import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

dependencies = ['numpy',
                'scipy',
                'pandas',
                'Shapely',
                'ply']

setuptools.setup(
    name="pysamos",
    version="0.1.0",
    author="Mark Olenik",
    author_email="mark.olenik@gmail.com",
    description="A wrapper around the active matter simulator SAMoS",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitlab.com/mark_olenik/PySAMoS",
    packages=setuptools.find_packages(),
    install_requires=dependencies,
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GPL License",
        "Operating System :: OS Independent",
    ),
)
