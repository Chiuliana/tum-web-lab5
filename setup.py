from setuptools import setup

setup(
    name="go2web",
    version="1.0.0",
    description="A simple command-line tool to search the web using DuckDuckGo",
    py_modules=["main"],
    install_requires=[
        "beautifulsoup4",
    ],
    entry_points={
        'console_scripts': [
            'go2web=main:main',
        ],
    },
)