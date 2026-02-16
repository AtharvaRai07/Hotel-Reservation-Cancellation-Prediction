from setuptools import setup, find_packages

HYPEN_E_DOT = "-e ."

with open("requirements.txt") as f:
    requirements = f.read().splitlines()
    if HYPEN_E_DOT in requirements:
        requirements.remove(HYPEN_E_DOT)

setup(
    name="hotel_reservation_prediction",
    version="0.1.0",
    author="Atharva Rai",
    packages=find_packages(),
    install_requires=requirements
)
