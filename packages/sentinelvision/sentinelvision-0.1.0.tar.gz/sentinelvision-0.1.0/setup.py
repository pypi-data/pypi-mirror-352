from setuptools import setup, find_packages
import os
setup(
    name='sentinelvision',
    version='0.1.0',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'ultralytics==8.0.172',
        'mediapipe',
        'opencv-python',
        'numpy',
        'torch',
        'torchvision',
        'scipy',
        'matplotlib',
        'onnxruntime',
        'pyyaml'
    ],
    entry_points={
        'console_scripts': [
            'sentinelvision=sentinelvision.run:main'
        ],
    },
    author='Your Name',
    description='Real-time autonomous visual tracking and reasoning system',
    long_description=open('README.md').read() if os.path.exists('README.md') else '',
    long_description_content_type='text/markdown',
    license='MIT',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
    ],
)
