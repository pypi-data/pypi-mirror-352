from setuptools import setup, find_packages

setup(
    name="yubin_mcp",
    version="0.0.1",
    packages=find_packages(),
    install_requires=[
        "posuto",
        "geopy",
        "mcp[cli]"
    ],
    entry_points={
        "console_scripts": [
            "yubin-mcp=yubin_mcp.server:main"
        ]
    },
    author="Masashi Morita",
    author_email="masashi.morita.mm@gmail.com",
    description="MCP server that retrieves addresses and map links from Japanese postal codes and latitude/longitude coordinates",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/masashimorita/yubin-mcp.git",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
)
