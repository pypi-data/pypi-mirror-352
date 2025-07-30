import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="calculator_kelseye",
    description="a simple caluculator MCP",
    long_description_content_type="text/markdown",
    version="1.0.2",
    author="kelseye",
    author_email="",
    url="",
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.6",
)