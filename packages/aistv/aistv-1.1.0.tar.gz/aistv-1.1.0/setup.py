from setuptools import setup, find_packages

setup(
    name="aistv",                    # tên package
    version="1.1.0",                 # phiên bản
    description="STV AI Chatbot Library for Python",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Trọng Phúc",
    author_email="phuctrongytb16@gmail.com",
    url="https://github.com/phuctrong1tuv",  # link repo (nếu có)
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        "requests"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)