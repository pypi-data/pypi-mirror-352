import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="flotech",
    version="0.2.1",
    author="Nashat Jumaah Omar",
    author_email="nashattt90@gmail.com",
    description="Multiphase flow package [This is a Test Release]",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Nashat90/flotech",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)