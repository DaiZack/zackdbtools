import setuptools

with open("README.md", "r") as fh:

    long_description = fh.read()

setuptools.setup(

    name="zackdbtools", # Replace with your username

    version="0.1.12",

    author="Zack Dai",

    author_email="zack.dai@delta4digital.com",

    description="a python package to connect db and data sources like google sheets",

    long_description=long_description,

    long_description_content_type="text/markdown",

    url="https://github.com/DaiZack/zackdbtools",

    packages=setuptools.find_packages(),
    include_package_data=True,
    install_requires=[
        'pandas~=1.4.2',
        'sqlalchemy~=1.4.37',
        'google-api-core~=2.8.1',
        'google-api-python-client~=2.50.0',
        'google-auth~=2.7.0',
        'google-auth-httplib2~=0.1.0',
        'google-auth-oauthlib~=0.5.1',
        'PyMySQL~=1.0.2',
        'psycopg2-binary~=2.9.3',
        'openpyxl~=3.0.10'
      ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ]

)