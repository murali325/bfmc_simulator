import os
from glob import glob
from setuptools import setup

package_name = 'simulator_py'

setup(
    name=package_name,
    version='1.0.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob('launch/*.launch.py')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='simulator',
    maintainer_email='simulator@todo.todo',
    description='BFMC Simulator ROS 2 Python Node and Launch Files',
    license='Bosch ECC',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'simulator_node = simulator_py.simulator_node:main',
        ],
    },
)
