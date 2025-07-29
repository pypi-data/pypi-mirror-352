from setuptools import setup, find_packages

setup(
    name="yose",
    version="0.1.3",
    description="",
    author="Koutarou Mori",
    author_email="m.koutarou2004@example.com",
    url="https://github.com/m-dev672/yose",
    packages=find_packages(),
    python_requires='>=3.8',
    install_requires=[
        "numpy==1.26.4",
        "scikit-learn==1.6.1",
        "POT==0.9.5",
        "jax==0.5.2",
        "ott-jax==0.5.0",
    ],
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Text Processing :: Linguistic",
    ],
    include_package_data=True,
)