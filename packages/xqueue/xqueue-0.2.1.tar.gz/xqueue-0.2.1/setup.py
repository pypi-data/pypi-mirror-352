# Always prefer setuptools over distutils
from setuptools import setup, find_packages
import pathlib

here = pathlib.Path(__file__).parent.resolve()

# Get the long description from the README file
long_description = (here / "README.md").read_text(encoding="utf-8")

setup(
    name="xqueue",
    version="0.2.1",
    description="A distributed task queue with cron scheduling built on top of Redis",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/chishui/xq",
    author="chishui",
    author_email="chishui2@gmail.com",
    packages=find_packages(
        include=[
        "xq",
        "server"
        ]),  # Include server package for web UI
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Distributed Computing",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3 :: Only",
    ],
    keywords="queue,redis,messaging,cron,scheduler,task,distributed",
    python_requires=">=3.8, <4",
    install_requires=[
        "redis>=5.0.0",
        "croniter>=6.0.0",
    ],
    extras_require={
        "server": [
            "fastapi>=0.100.0",
            "uvicorn>=0.27.0",
            "jinja2>=3.1.0",
        ],
    },
    package_data={
        "server": ["templates/*.html", "static/*"],
    },
    entry_points={
        "console_scripts": [
            "xq-server=server.api:main",
        ],
    },
    project_urls={
        "Bug Reports": "https://github.com/chishui/xq/issues",
        "Source": "https://github.com/chishui/xq",
    },
)
