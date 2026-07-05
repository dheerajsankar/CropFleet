from setuptools import find_packages, setup

package_name = 'planner'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/planner/launch',
        ['launch/swarm_launch.xml']),
        ('share/planner/rviz',
        ['rviz/swarm.rviz'])
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Dheeraj Sankar',
    maintainer_email='dheerajsankar2@gmail.com',
    description='ROS2 planner nodes for multi-drone agricultural coverage missions',
    license='MIT',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'drone_node = planner.drone_node:main',
            'mission_manager = planner.mission_manager:main',
            'visualization = planner.visualization:main',
            'fleet_gui = planner.fleet_gui:main'

        ],
    },
)
