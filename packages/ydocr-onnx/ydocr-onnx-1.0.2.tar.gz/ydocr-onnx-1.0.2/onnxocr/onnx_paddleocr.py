import time
import os
import requests
from pathlib import Path

from .predict_system import TextSystem
from .utils import infer_args as init_args
from .utils import str2bool, draw_ocr
import argparse
import sys

def download_model(url, save_path):
    """下载模型文件"""
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    if not os.path.exists(save_path):
        print(f"Downloading {url} to {save_path}")
        response = requests.get(url, stream=True)
        response.raise_for_status()
        with open(save_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        print(f"Downloaded {save_path}")
    else:
        print(f"Model already exists at {save_path}, skipping download.")

class ONNXPaddleOcr(TextSystem):
    def __init__(self, **kwargs):
        # 默认参数
        parser = init_args()
        inference_args_dict = {}
        for action in parser._actions:
            inference_args_dict[action.dest] = action.default
        params = argparse.Namespace(**inference_args_dict)

        # params.rec_image_shape = "3, 32, 320"
        params.rec_image_shape = "3, 48, 320"

        # 根据传入的参数覆盖更新默认参数
        params.__dict__.update(**kwargs)

        # 如果指定使用server模式，下载模型
        if kwargs.get('mode') == 'server':
            # 使用用户主目录下的路径存储模型
            user_home = os.path.expanduser('~')
            base_path = Path(user_home) / ".onnxocr/models/server"
            
            # 下载检测模型
            det_url = "https://winrobot-pub-a.oss-cn-hangzhou.aliyuncs.com/client/utility/ai_model/ocr/model/det.onnx"
            det_path = base_path / "det" / "det.onnx"
            download_model(det_url, str(det_path))
            params.det_model_dir = str(det_path)
            
            # 下载识别模型
            rec_url = "https://winrobot-pub-a.oss-cn-hangzhou.aliyuncs.com/client/utility/ai_model/ocr/model/rec.onnx"
            rec_path = base_path / "rec" / "rec.onnx"
            download_model(rec_url, str(rec_path))
            params.rec_model_dir = str(rec_path)

        # 初始化模型
        super().__init__(params)

    def ocr(self, img, det=True, rec=True, cls=True):
        if cls == True and self.use_angle_cls == False:
            print(
                "Since the angle classifier is not initialized, the angle classifier will not be uesd during the forward process"
            )

        if det and rec:
            ocr_res = []
            dt_boxes, rec_res = self.__call__(img, cls)
            tmp_res = [[box.tolist(), res] for box, res in zip(dt_boxes, rec_res)]
            ocr_res.append(tmp_res)
            return ocr_res
        elif det and not rec:
            ocr_res = []
            dt_boxes = self.text_detector(img)
            tmp_res = [box.tolist() for box in dt_boxes]
            ocr_res.append(tmp_res)
            return ocr_res
        else:
            ocr_res = []
            cls_res = []

            if not isinstance(img, list):
                img = [img]
            if self.use_angle_cls and cls:
                img, cls_res_tmp = self.text_classifier(img)
                if not rec:
                    cls_res.append(cls_res_tmp)
            rec_res = self.text_recognizer(img)
            ocr_res.append(rec_res)

            if not rec:
                return cls_res
            return ocr_res


def sav2Img(org_img, result, name="draw_ocr.jpg"):
    # 显示结果
    from PIL import Image

    result = result[0]
    # image = Image.open(img_path).convert('RGB')
    # 图像转BGR2RGB
    image = org_img[:, :, ::-1]
    boxes = [line[0] for line in result]
    txts = [line[1][0] for line in result]
    scores = [line[1][1] for line in result]
    im_show = draw_ocr(image, boxes, txts, scores)
    im_show = Image.fromarray(im_show)
    im_show.save(name)


if __name__ == "__main__":
    import cv2

    model = ONNXPaddleOcr(use_angle_cls=True, use_gpu=False)

    img = cv2.imread(
        "/data2/liujingsong3/fiber_box/test/img/20230531230052008263304.jpg"
    )
    s = time.time()
    result = model.ocr(img)
    e = time.time()
    print("total time: {:.3f}".format(e - s))
    print("result:", result)
    for box in result[0]:
        print(box)

    sav2Img(img, result)
