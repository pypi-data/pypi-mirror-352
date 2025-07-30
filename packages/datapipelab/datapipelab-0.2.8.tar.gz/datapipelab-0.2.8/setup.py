from setuptools import setup, find_packages

setup(
    name='datapipelab',
    version='0.2.8',
    description='A data pipeline library with connectors, sources, processors, and sinks.',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'json5',
        'loguru',
        # 'azure-storage-blob',
        # 'google-cloud-storage',
        # 'pandas'
    ],
)