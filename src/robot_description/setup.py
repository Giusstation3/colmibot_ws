from setuptools import find_packages, setup

package_name = 'robot_description'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/launch', ['launch/display.launch.py']),
        ('share/' + package_name + '/urdf', ['urdf/colmibot.urdf']),
        ('share/' + package_name + '/rviz', ['rviz/display.rviz']),
        ('share/' + package_name + '/meshes', [
            'meshes/chasis.stl',
            'meshes/rueda_izquierda.stl',
            'meshes/rueda_derecha.stl',
            'meshes/rueda_loca.stl',
            'meshes/camara.stl',
            'meshes/imu.stl',
            'meshes/tof.stl',
        ]),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='parallels',
    maintainer_email='giuseppevalencia28@gmail.com',
    description='TODO: Package description',
    license='TODO: License declaration',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
        ],
    },
)
