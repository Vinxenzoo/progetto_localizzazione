from setuptools import find_packages, setup

package_name = 'progetto_localizzazione'

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
    maintainer='Vincenzo',
    maintainer_email='tuamail@todo.todo',
    description='Sistema di localizzazione probabilistica (Particle Filter)',
    license='Apache-2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'particle_filter = progetto_localizzazione.particle_filter_node:main'
        ],
    },
)