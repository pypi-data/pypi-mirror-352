from setuptools import setup, find_packages

setup(
    name='WebEasyML',
    version='0.1.0',
    description='wzai ; A simple ML web server,from wenzhou S&T High school',
    author='linmy',
    packages=find_packages(),
    install_requires=[
        'flask',
        'werkzeug',
        # 其他依赖
    ],
    include_package_data=True,
)