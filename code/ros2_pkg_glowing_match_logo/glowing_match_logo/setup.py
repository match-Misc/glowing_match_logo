from setuptools import find_packages, setup

package_name = 'glowing_match_logo'

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
    maintainer='pmlab',
    maintainer_email='pmlab',
    description='TODO: Package description',
    license='Apache-2.0',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'gml_node_serial = glowing_match_logo.gml_node_serial:main',
            'gml_node_ble = glowing_match_logo.gml_node_ble:main',
        ],
    },
)
