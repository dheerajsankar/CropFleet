from setuptools import find_packages, setup

package_name = 'swarming'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='dheeraj',
    maintainer_email='dheerajsankar2@gmail.com',
    description='TODO: Package description',
    license='TODO: License declaration',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'drone_node = swarming.drone_node:main',
            'mission_manager = swarming.mission_manager:main',
            'visualization = swarming.visualization:main'

        ],
    },
)