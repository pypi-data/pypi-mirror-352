from setuptools import setup, find_packages

setup(
    name="ytc",
    version="2.7.4",
    author="GoldenX",
    author_email="",
    description="fetch youtube cookies from remote api to use with yt_dlp.",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://t.me/goldenxpris",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=[],
    include_package_data=True,
    zip_safe=False,
)