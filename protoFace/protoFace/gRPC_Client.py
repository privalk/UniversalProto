import grpc
import base64
import time
import face_recognition_pb2
import face_recognition_pb2_grpc
from dotenv import load_dotenv
import os

# 加载环境变量
load_dotenv()
test_image_path=os.getenv("TEST_IMAGE_PATH", "test_image.jpg")

def run():
    with grpc.insecure_channel('localhost:50051') as channel:
        stub = face_recognition_pb2_grpc.FaceDetectServiceStub(channel)
        
        # 读取图片文件，并进行base64编码
        with open(test_image_path, 'rb') as image_file:
            image_data = image_file.read()
        image_base64 = base64.b64encode(image_data).decode('utf-8')

        # 发送请求
        response = stub.DetectFaces(face_recognition_pb2.FaceDetectRequest(image_base64=image_base64))
        
        # 打印响应结果
        for face in response.subjects:
            gender = "Male" if face.gender == face_recognition_pb2.Face.MALE else "Female"
            print(f"Gender: {gender}, Age: {face.age},Box: {face.box}")
        print()

if __name__ == '__main__':


    start_time = time.time()  # 开始时间
    iterations = 10  # 运行次数
    for _ in range(iterations):
        run()
    end_time = time.time()  # 结束时间
    total_time = end_time - start_time  # 总时间
    runs_per_second = iterations / total_time  # 每秒运行次数
    print(f"Total time for {iterations} iterations: {total_time:.2f} seconds.")
    print(f"Runs per second: {runs_per_second:.2f}")