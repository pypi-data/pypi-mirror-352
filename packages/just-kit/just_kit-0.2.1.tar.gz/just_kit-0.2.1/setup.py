from setuptools import setup, find_packages

setup(
    name="just_kit",
    version="0.2.1",
    packages=find_packages(),
    install_requires=[
        'requests',  # 用于发送HTTP请求
        'beautifulsoup4',  # 用于解析HTML
        'dotenv',
        'pycryptodome'
    ],
    package_data={
        'just_kit': ['js/*'],
    },
    author="Harmog",
    author_email="harmog@foxmail.com",
    description="江苏科技大学信息门户工具包",
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    url="https://github.com/heerheer/just-kit",
    # classifiers=[
    #     "Programming Language :: Python :: 3",
    #     "License :: OSI Approved :: MIT License",
    #     "Operating System :: OS Independent",
    # ],
    # python_requires='>=3.11',
)