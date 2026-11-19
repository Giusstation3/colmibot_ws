from setuptools import find_packages, setup

package_name = 'colmibot_datos'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/datos', ['datos/maquinas.csv']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='pablo-cano',
    maintainer_email='juanpa2_canorub@outlook.com',
    description='TODO: Package description',
    license='Apache-2.0',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'ejemplo_registro = colmibot_datos.registro:ejemplo',
            'mantenimiento = colmibot_datos.mantenimiento:main',
            'generar_codigos = colmibot_datos.generador:main',
            'grabar_linea_base = colmibot_datos.sonido:main',
            'detector_sonido = colmibot_datos.detector_sonido:main',
        ],
    },
)
