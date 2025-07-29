from setuptools import setup, find_packages

setup(
    name='LILEITEST1',              # 包名
    version='1.1.0',                # 版本号
    author='LILEI',
    author_email='114976@email.com',
    description='A simple example package2',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/yourusername/my_package',  # 可选
    packages=find_packages(),       # 自动查找子模块
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)