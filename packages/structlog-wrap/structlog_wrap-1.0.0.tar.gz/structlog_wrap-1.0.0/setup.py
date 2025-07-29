"""
structlog_wrap 包的安装配置
"""
from setuptools import setup, find_packages

# 读取 README 文件作为长描述
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# 读取 requirements.txt 文件
with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="structlog-wrap",
    version="1.0.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="基于structlog的函数日志装饰器，自动打印函数调用日志",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/structlog-wrap",
    py_modules=["structlog_wrap"],  # 单个模块文件
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Logging",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov",
            "black",
            "flake8",
        ],
    },
    keywords="structlog logging decorator function calls",
    project_urls={
        "Bug Reports": "https://github.com/yourusername/structlog-wrap/issues",
        "Source": "https://github.com/yourusername/structlog-wrap",
    },
)
