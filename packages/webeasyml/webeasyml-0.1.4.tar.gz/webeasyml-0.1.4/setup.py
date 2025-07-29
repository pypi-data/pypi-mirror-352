from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='webeasyml',
    version='0.1.4',
    description='wzai ; A simple ML web server,from wenzhou S&T High school',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author='linmy',
    packages=find_packages(),
    package_data={
        'webeasyml': [
            '*.py', '*.md', '*.txt', '*.js', '*.css', '*.html'
        ],
    },
    install_requires=[
        'flask',
        'werkzeug',
        # 其他依赖
    ],
    include_package_data=True,
)