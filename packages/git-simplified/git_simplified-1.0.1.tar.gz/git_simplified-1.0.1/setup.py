from setuptools import setup, find_packages

setup(
    name="git-simplified",  # Or whatever unique name you've chosen
    version="1.0.1",
    packages=find_packages(),  # This should find 'easygit' and all subpackages
    install_requires=[
        "colorama",  # Add any other dependencies your project needs
    ],
    entry_points={
        "console_scripts": [
            "easygit=easygit.__main__:main",
        ],
    },
    author="QinCai-rui",
    author_email="your.email@example.com",
    description="A beginner-friendly Git CLI with colorful output",
    long_description=open("README.md").read() if open("README.md") else "A beginner-friendly Git CLI",
    long_description_content_type="text/markdown",
    url="https://github.com/QinCai-rui/easygit",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
