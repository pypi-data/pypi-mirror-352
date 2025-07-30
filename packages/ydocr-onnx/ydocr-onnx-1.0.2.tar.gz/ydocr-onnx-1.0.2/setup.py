from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="ydocr-onnx",
    version="1.0.2",
    author="jiaer",
    author_email="jia.er@winrobot360.com",
    license='Apache 2.0',
    description="基于 PaddleOCR 的离线 OCR 识别工具，使用 ONNX 模型进行推理",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/ydocr-onnx",
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
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Scientific/Engineering :: Image Recognition',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
    ]
)