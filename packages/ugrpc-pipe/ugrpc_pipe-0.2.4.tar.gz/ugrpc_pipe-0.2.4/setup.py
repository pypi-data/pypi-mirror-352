from setuptools import setup, find_packages

setup(
    name='ugrpc_pipe',
    version='0.2.4',
    license='MIT',
    description='protobuf for grpc Pipe',
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author='esun',
    author_email='esun@voteb.com',
    url='https://github.com/ImagineersHub/unity-grpc-build-proto-pipe',
    keywords=['python', 'grpc'],
    packages=find_packages(),
    install_requires=[
        'grpcio==1.50.0',
        'grpcio-tools==1.50.0',
        'protobuf>=4.25.2,<5.0dev',
        'betterproto[compiler]==2.0.0b5'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Programming Language :: Python :: 3.10'
    ]
)
