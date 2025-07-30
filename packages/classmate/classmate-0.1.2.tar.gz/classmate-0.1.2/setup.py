from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="classmate",
    version="0.1.2",
    author="linmy",
    author_email="wzlinmiaoyan@163.com",
    description="一个基于 Python 的助学web系统",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    include_package_data=True,
    package_data={
        "classmate": [
            "static/css/*",
            "static/js/*",
            "templates/*",
        ],
    },

    python_requires=">=3.8",
    install_requires=[
        
        "flask>=2.0.0",
        "opencv-python>=4.1.2.30",
        "numpy>=1.24.4",
        "pillow>=8.0.0",
        "werkzeug>=2.0.0",
    ],
    
) 