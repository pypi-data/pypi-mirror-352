from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="paper-solver",
    version="0.1.0",
    author="QC Lab",
    author_email="baijifei0411@163.com",
    description="一个专门面向造纸行业的高性能约束优化求解器",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/baijifei/paper-solver",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Scientific/Engineering :: Mathematics",
        "Topic :: Scientific/Engineering :: Optimization",
    ],
    python_requires=">=3.7",
    install_requires=[
        "numpy>=1.17.0",
        "scipy>=1.5.0",
        "autograd>=1.3",
    ],
    extras_require={
        "sparse": ["scikit-sparse>=0.4.5"],
    }
)