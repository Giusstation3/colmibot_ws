import os
from glob import glob
from setuptools import find_packages, setup

package_name = 'joystick_teleop'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob('launch/*.launch.py')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Pablo Cano',
    maintainer_email='juanpa2_canorub@outlook.com',
    description='Teleoperacion de turtlesim con joystick DualSense',
    license='Apache-2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'joy_turtle_teleop = joystick_teleop.joy_turtle_teleop:main',
        ],
    },
)
