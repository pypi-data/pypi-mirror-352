import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name='iron_toolbox',
    packages=['iron_toolbox'],
    version='1.1.24',
    license='MIT',
    description='Functions to be used by Iron Data Analytics Team',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author='Luciano Siqueira',
    author_email='lucianosiqueira@iron.fit',
    url='https://github.com/IronTrainers/iron_data_toolbox',
    project_urls={"Bug Tracker": "https://github.com/IronTrainers/iron_data_toolbox/issues"},
    install_requires=['DateTime==5.1',
                      'duckdb==0.7.1',
                      'fsspec==2022.7.1',
                      'paramiko',
                      'pydomo==0.3.0.9',
                      'pymongo==4.6.3',
                      's3fs==2022.7.1',
                      'tqdm==4.65.0',
                      'Unidecode==1.3.6',
                      'pysftp==0.2.9'],
    keywords=['python',
              'mongodb',
              'aws',
              'domo',
              'iron_toolbox'],
    download_url="https://github.com/IronTrainers/iron_data_toolbox/archive/refs/tags/iron_data_toolboox.tar.gz",)
