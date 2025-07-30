from setuptools import setup, find_packages

setup(
    name="pymakcu",
    version="0.1.0",
    packages=find_packages(),
    description="For makcu project",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Igor Kuznetsov",
    author_email="admin@neuralaim.ru",
    url="https://github.com/neuralaim/pymakcu",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
    python_requires=">=3.6",
    install_requires=[],
)