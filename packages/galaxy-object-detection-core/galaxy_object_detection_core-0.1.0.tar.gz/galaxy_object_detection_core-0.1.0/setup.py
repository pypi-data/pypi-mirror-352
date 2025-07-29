from setuptools import setup, find_packages

setup(
    name='galaxy-object-detection-core',
    version='0.1.0',
    author='muhammadhaerul.25',
    description='YOLO-based object detection system for various industries',
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type='text/markdown',
    url='https://github.com/muhammadhaerul/Galaxy-Object-Detection-Core',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'ultralytics==8.3.146',
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.10',
)
