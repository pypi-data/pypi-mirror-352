import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# 从 __init__.py 读取版本号
def get_version():
    with open("bit_login/__init__.py", "r", encoding="utf-8") as f:
        for line in f:
            if line.startswith("__version__"):
                return line.split("=")[1].strip().strip('"').strip("'")

setuptools.setup(
    name="bit_login", 
    version=get_version(),
    author="teclab",   
    author_email="admin@teclab.org.cn",
    description="北京理工大学统一身份验证登录模块",
    keywords="BIT, BITCAS, BITLogin, BITWebVPN, BITSSO, BITSSOLogin, BITSSOClient",
    long_description=long_description,   
    long_description_content_type="text/markdown",
    url="https://github.com/yht0511/bit-login",
    packages=setuptools.find_packages(),
    install_requires=[
        "requests>=2.25.0",
        "beautifulsoup4>=4.9.0", 
        "pycryptodome>=3.15.0",
    ],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9", 
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8',
    project_urls={
        "Bug Reports": "https://github.com/yht0511/bit-login/issues",
        "Source": "https://github.com/yht0511/bit-login",
    },
)