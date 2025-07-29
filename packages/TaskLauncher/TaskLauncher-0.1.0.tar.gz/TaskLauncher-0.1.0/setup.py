from setuptools import setup, find_packages

setup(
    name="TaskLauncher",
    version="0.1.0",
    description="A cross-platform command and python script task launcher with process management.",
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    author="Zeturn",
    author_email="hollowdata@outlook.com",
    packages=find_packages(),

    install_requires=[
        "psutil"
    ],
    python_requires='>=3.7',
    include_package_data=True,
    url="https://github.com/zeturns/TaskLauncher",
    entry_points={},
)
