from setuptools import setup

setup(
    name="structtkinter",
    version="0.1.1",
    py_modules=["structtkinter"],
    install_requires=[],
    author="Gustavo de Melo Timbó",
    author_email="gustavo.wbu@gmail.com",
    description="A CSS-like, HTML-inspired UI framework built on top of Tkinter.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/gustavowbu/structtkinter",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)
