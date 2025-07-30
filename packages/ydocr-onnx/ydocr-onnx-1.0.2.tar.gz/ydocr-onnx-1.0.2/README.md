# YDOCR-ONNX

基于 PaddleOCR 的离线 OCR 识别工具，使用 ONNX 模型进行推理。

## 特点

- 完全离线运行，无需联网
- 基于 PaddleOCR 的 PP-OCRv5 模型
- 使用 ONNX 进行模型推理，性能优异
- 支持文本检测、文本识别和方向分类
- 支持中英文识别
- 支持自定义模型路径

## 安装

```bash
pip install ydocr-onnx
```

## 使用方法

### 基本使用

```python
from onnxocr.onnx_paddleocr import ONNXPaddleOcr
import cv2

# 初始化 OCR 引擎
ocr = ONNXPaddleOcr()

# 读取图片
img = cv2.imread('test.jpg')

# 执行 OCR 识别
result = ocr.ocr(img)

# 打印识别结果
print(result)
```

### 使用自定义模型

```python
from onnxocr.onnx_paddleocr import ONNXPaddleOcr

# 指定模型路径
ocr = ONNXPaddleOcr(
    det_model_path='path/to/det.onnx',
    rec_model_path='path/to/rec.onnx',
    cls_model_path='path/to/cls.onnx'
)
```

## 参数说明

- `det_model_path`: 检测模型路径
- `rec_model_path`: 识别模型路径
- `cls_model_path`: 方向分类模型路径
- `use_gpu`: 是否使用 GPU 推理
- `use_angle_cls`: 是否使用方向分类
- `lang`: 识别语言，支持 'ch' 和 'en'

## 依赖要求

- Python >= 3.7
- opencv-python-headless >= 4.7
- onnxruntime >= 1.14
- numpy
- requests
- shapely
- pyclipper
- scikit-image

## 许可证

Apache License 2.0

## 贡献

欢迎提交 Issue 和 Pull Request！

## 致谢

本项目基于 [PaddleOCR](https://github.com/PaddlePaddle/PaddleOCR) 开发。

## 🛠️ 环境安装  
```bash  
python>=3.6  

pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt  
```  

**注意**：  
- 默认使用 PP-OCRv5_mobile-ONNX 模型。
- 由于PyPI上传限制（100MB），模型文件会在首次使用时自动下载到用户主目录下的 `.onnxocr/models` 目录。
- 您也可以手动下载模型：

```bash
# 下载server模型（更准确但更大）
python download_models.py --mode server

# 下载mobile模型（更快但精度略低）
python download_models.py --mode mobile
```

模型下载地址：
- Server模型：
  - det: https://winrobot-pub-a.oss-cn-hangzhou.aliyuncs.com/client/utility/ai_model/ocr/model/det.onnx
  - rec: https://winrobot-pub-a.oss-cn-hangzhou.aliyuncs.com/client/utility/ai_model/ocr/model/rec.onnx

## 🚀 一键运行  
```bash  
python test_ocr.py  
```  


## 📡 API 服务（CPU 示例）  
### 启动服务  
```bash  
python app-service.py  
```  

### 测试示例  
#### 请求  
```bash  
curl -X POST http://localhost:5005/ocr \  
-H "Content-Type: application/json" \  
-d '{"image": "base64_encoded_image_data"}'  
```  

#### 响应  
```json  
{  
  "processing_time": 0.456,  
  "results": [  
    {  
      "text": "名称",  
      "confidence": 0.9999361634254456,  
      "bounding_box": [[4.0, 8.0], [31.0, 8.0], [31.0, 24.0], [4.0, 24.0]]  
    },  
    {  
      "text": "标头",  
      "confidence": 0.9998759031295776,  
      "bounding_box": [[233.0, 7.0], [258.0, 7.0], [258.0, 23.0], [233.0, 23.0]]  
    }  
  ]  
}  
```  

### POST 请求  
```  
url: ip:5006/ocr  
```  

### 返回值示例  
```json  
{  
  "processing_time": 0.456,  
  "results": [  
    {  
      "text": "名称",  
      "confidence": 0.9999361634254456,  
      "bounding_box": [[4.0, 8.0], [31.0, 8.0], [31.0, 24.0], [4.0, 24.0]]  
    },  
    {  
      "text": "标头",  
      "confidence": 0.9998759031295776,  
      "bounding_box": [[233.0, 7.0], [258.0, 7.0], [258.0, 23.0], [233.0, 23.0]]  
    }  
  ]  
}  
```  


## 🌟 效果展示  
| 示例 1 | 示例 2 |  
|--------|--------|  
| ![](result_img/r1.png) | ![](result_img/r2.png) |  

| 示例 3 | 示例 4 |  
|--------|--------|  
| ![](result_img/r3.png) | ![](result_img/draw_ocr4.jpg) |  

| 示例 5 | 示例 6 |  
|--------|--------|  
| ![](result_img/draw_ocr5.jpg) | ![](result_img/555.png) |
