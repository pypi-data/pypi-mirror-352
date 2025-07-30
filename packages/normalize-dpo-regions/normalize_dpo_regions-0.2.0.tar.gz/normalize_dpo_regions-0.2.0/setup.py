from setuptools import setup, find_packages

setup(
    name="normalize_dpo_regions",           # имя для PyPI и pip
    version="0.2.0",             # версия
    author="Mikhail Demkov",
    author_email="mkdemkov@gmail.com",
    description="Normalize Russian regions using generative models",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    packages=find_packages(),    # автоматически найдёт my_library
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)