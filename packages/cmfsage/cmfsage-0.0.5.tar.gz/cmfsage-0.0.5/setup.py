from setuptools import setup

setup(
    name='cmfsage',
    version='0.0.5',
    description='This project is to enable common metadata framework logging for waggle sensor plugins: https://github.com/waggle-sensor.',
    author='han.liu@hpe.com',
    py_modules=["cmfsage"],
    package_dir={"": "src"},
    install_requires=[
        "cmflib",
        "pywaggle"
    ],
    python_requires='>=3.9',
)
