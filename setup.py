import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    # name='Velasco\' Python Structures',
    name='vel_data_structures',
    version='3.8.0',
    author='Alfredo Velasco',
    author_email='alfredo0234@gmail.com',
    description='Installation of Package',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/VelascoAMath/vel_data_structures/',
    project_urls = {
        "Bug Tracker": "https://github.com/VelascoAMath/vel_data_structures/issues"
    },
    license='MIT',
    packages=['vel_data_structures'],
    install_requires=['requests'],
)
