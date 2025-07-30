from setuptools import setup, find_packages

setup(
    name="ydocr-onnx",
    version="1.0.1",
    author="jiaer",
    author_email="jia.er@winrobot360.com",
    license='Apache 2.0',
    description="影刀离线OCR，paddlev5",
    packages=find_packages(),
    install_requires=[
        'opencv-python-headless>=4.7',
        'onnxruntime>=1.14',
        'numpy',
        'requests',
        'shapely',
        'pyclipper',
        'scikit-image'
    ],
    include_package_data=True,
    package_data={
        'onnxocr': [
            'fonts/*.ttf',
            'models/ppocrv5/*.onnx',
            'models/ppocrv5/*.txt',
            'models/ppocrv5/det/*.onnx',
            'models/ppocrv5/rec/*.onnx',
            'models/ppocrv5/cls/*.onnx'
        ]
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ]
)