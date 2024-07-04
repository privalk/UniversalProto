import requests
import cv2
import io
from threading import Thread

class FaceDetectManager:
    def __init__(self, base_url, api_key, test_image_path):
        self.base_url = base_url
        self.api_key = api_key
        self.test_image_path = test_image_path
        # 使用提供的测试图像进行API可达性测试
        self.is_api_reachable = False
        # self.test_api()

    def send_recognition_request(self, frame, options=None):
        # 组装完整的API URL，根据options参数
        if options:
            options_query = ",".join(options)
            api_url = f"{self.base_url}?face_plugins={options_query}"
        else:
            api_url = self.base_url
        
        # 将图像编码为JPEG格式
        success, buffer = cv2.imencode('.jpg', frame)
        if not success:
            raise Exception("Failed to encode frame to JPEG format.")
        
        files = {'file': ('current_frame.jpg', io.BytesIO(buffer), 'image/jpeg')}
        headers = {'x-api-key': self.api_key}
        response = requests.post(api_url, files=files, headers=headers)
        return response

    def test_api(self):
        # 读取测试图像
        test_image = cv2.imread(self.test_image_path)
        if test_image is None:
            raise ValueError("Test image could not be loaded.")
        
        # 发送测试请求
        response = self.send_recognition_request(test_image, ['landmarks', 'gender', 'age', 'pose'])
        if response.status_code != 200:
            raise Exception(f"API is not reachable, returned status code {response.status_code}")
        print("人脸识别模块加载成功，CompreFace API可达。")
        self.is_api_reachable = True

    def queryFace(self, image, in_needed):
        """获取形如[{'subject': '级别_姓名_昵称', 'similarity': 0.9988, 'box': {...}}]的识别结果列表"""
        plugins = [option for option in in_needed if option not in ['subject', 'similarity']]
        response = self.send_recognition_request(image, plugins)

        if response.status_code != 200:
            if response.status_code == 400 and response.json().get('code') == 28:
                # print(f"No Face is Found in Image.")
                return []
            else:
                raise Exception(f"Face recognition failed with status code {response.status_code}, response = \n{response}")
        
        data = response.json()
        results = []
        for item in data.get('result', []):
            face_data = {field: item.get(field, item.get('subjects', [{}])[0].get(field))
                            for field in in_needed}
            if 'gender' in in_needed:
                face_data = self.extractSimpleValue(face_data, 'gender', 'value')
            if 'age' in in_needed:
                face_data = self.extractSimpleValue(face_data, 'age', 'high')
            results.append(face_data)
        return results            

    def queryFaceAsync(self, image, in_needed, callback):
        Thread(target=lambda: callback(self.queryFace(image, in_needed))).start()

    @staticmethod
    def extractSimpleValue(data, keyName, valueName):
        # Check if the key exists, is a dictionary, and contains the desired value key
        if (keyName in data) and (isinstance(data[keyName], dict)) and (valueName in data[keyName]):
            data[keyName] = data[keyName][valueName]
        else: 
            data[keyName] = None
        return data

if __name__ == '__main__':
    test_image_path = "test_image.jpg"
    test_image_path = "./test_family.png"
    needed_info = ['box', 'gender', 'age']
    # needed_info = ['subject', 'similarity', 'box']
    # 最多支持如下参数
    # needed_info = ['subject', 'similarity', 'box', 'gender', 'age', 'landmarks', 'pose']
    # base_url = "http://139.224.44.136:8123/api/v1/recognition/recognize"
    # api_key = "d594011e-48ae-4bac-a7bc-d18f4039771b"
    # manager = FaceDetectManager(base_url, api_key, test_image_path)
    COMPRE_API_URL = "http://localhost:8000/api/v1/detection/detect"
    COMPRE_API_KEY = "8b646ae9-7aa9-4df5-9119-b52981464cf8"
    manager = FaceDetectManager(COMPRE_API_URL, COMPRE_API_KEY, test_image_path)
    test_image = cv2.imread(test_image_path)
    
    # 异步调用示例
    def callback(results):
        print("异步调用结果:", results)
    manager.queryFaceAsync(test_image, needed_info, callback)

    # 同步调用示例
    results = manager.queryFace(test_image, needed_info)
    print("同步调用结果:", results)
    

