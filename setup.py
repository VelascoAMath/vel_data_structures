import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name='PythonDataStructures',
    version='0.0.1',
    author='Alfredo Velasco',
    author_email='avelasco@princeton.edu',
    description='Testing installation of Package',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/VelascoAMath/PythonDataStructures/',
    project_urls = {
        "Bug Tracker": "https://github.com/VelascoAMath/PythonDataStructures/issues"
    },
    license='MIT',
    packages=['PythonDataStructures'],
    install_requires=['requests'],
)