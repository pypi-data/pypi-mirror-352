
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
