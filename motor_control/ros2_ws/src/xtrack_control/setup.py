from setuptools import find_packages, setup

package_name = 'xtrack_control'

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
    maintainer='thyaen',
    maintainer_email='Thomasda.nguyen@outlook.de',
    description='Motor Control for the XTrack vehicle',
    license='TODO: License declaration',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            "motor_control_node = xtrack_control.motor_control_node:main"
        ],
    },
)
