from setuptools import setup, find_packages

setup(
    name='qmt-data',
    version='0.1.0',
    description='QMT – Airflow DAG Generator CLI',
    author='Твоє Імʼя',
    author_email='email@example.com',
    packages=find_packages(),
    install_requires=[
        # залежності, наприклад:
        # 'requests', 'pyyaml'
    ],
    entry_points={
        'console_scripts': [
            'qmt-data = main.main:main',
        ],
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.7',
)
