from setuptools import setup, find_packages

setup(
    name='etf-strategy',  # 包名，不能和已有PyPI包重名
    version='0.1.5',
    description='ETF策略工具包',
    author='Jack',
    packages=find_packages(),
    install_requires=[
        'pandas',
        'numpy',
        # 其他依赖
    ],
    python_requires='>=3.7',
)