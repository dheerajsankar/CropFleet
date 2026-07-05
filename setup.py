from setuptools import setup,find_packages

setup(
    name="coverage-planner",
    version="0.1.0",
    description="Multi-drone agricultural coverage planning library",
    author="Dheeraj Sankar",
    author_email="dheerajsankar2@gmail.com",
    license="MIT",
    packages=find_packages(include=["coverage_planner", "coverage_planner.*"]),
    install_requires=[
        "numpy",
        "shapely",
        "opencv-python",
        "matplotlib",
        "pyproj"

    ]
)