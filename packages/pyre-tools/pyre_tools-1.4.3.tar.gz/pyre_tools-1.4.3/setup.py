from setuptools import setup, find_packages

setup(
    name='pyre_tools',  
    version='1.4.3',
    description='从源文件中提取Python项目依赖项的CLI工具。',
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    author='dawalishi122',
    author_email='1710802268@qq.com',
    url='https://github.com/dawalishi122/pypre_tools',  
    license='MIT',
    packages=find_packages(),
    python_requires='>=3.6',
    entry_points={
        'console_scripts': [
            'pyre = pyre.__main__:main'
        ],
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
    ],
    include_package_data=True,
)
