import queue
import grpc
from concurrent import futures
import numpy as np
import cv2
import base64
import face_recognition_pb2
import face_recognition_pb2_grpc
from FaceDetectManager import FaceDetectManager
from dotenv import load_dotenv
import os

# 加载环境变量
load_dotenv()

class FaceDetectService(face_recognition_pb2_grpc.FaceDetectServiceServicer):
    def __init__(self):
        self.face_detect_manager = FaceDetectManager(
            base_url=os.getenv("COMPRE_API_URL", "http://localhost:8123/api/v1/recognition/recognize"),
            api_key=os.getenv("COMPRE_API_KEY", "d594011e-48ae-4bac-a7bc-d18f4039771b"),
            test_image_path=os.getenv("TEST_IMAGE_PATH", "test_image.jpg")
        )
        self.result_queue = queue.Queue()
        self.empty_launch = int(os.getenv("EMPTY_LAUNCH", 3))
        # 预先填充队列
        face = face_recognition_pb2.Face(gender=face_recognition_pb2.Face.MALE, age=0, box=[66,66,88,88])
        for _ in range(self.empty_launch):
            self.result_queue.put([face])  # 空结果

        print("FaceDetectManager initialized with:", self.face_detect_manager.base_url,
              self.face_detect_manager.api_key, self.face_detect_manager.test_image_path)

    def async_callback(self, results):
        faces = []
        for result in results:
            gender_enum = face_recognition_pb2.Face.FEMALE if result['gender'] == 'female' else face_recognition_pb2.Face.MALE
            box = [result['box']['x_min'], result['box']['y_min'], result['box']['x_max'], result['box']['y_max']]
            face = face_recognition_pb2.Face(gender=gender_enum, age=result['age'], box=box)
            faces.append(face)
        self.result_queue.put(faces)

    def DetectFaces(self, request, context):
        print("Received image for processing.")
        image_data = base64.b64decode(request.image_base64)
        image_np = np.frombuffer(image_data, dtype=np.uint8)
        frame = cv2.imdecode(image_np, cv2.IMREAD_COLOR)

        if frame is None:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details('Error decoding image data.')
            return face_recognition_pb2.FaceDetectResponse()
        
        # 打印图片尺寸
        if frame is not None:
            print("Decoded image size: Height = {}, Width = {}, Channels = {}".format(frame.shape[0], frame.shape[1], frame.shape[2]))

        # 异步调用处理图像
        needed_info = ['gender', 'age', 'box']
        self.face_detect_manager.queryFaceAsync(frame, needed_info, self.async_callback)

        # 等待结果
        result_faces = self.result_queue.get()  # 阻塞直到有结果
        return face_recognition_pb2.FaceDetectResponse(subjects=result_faces)

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    service = FaceDetectService()
    face_recognition_pb2_grpc.add_FaceDetectServiceServicer_to_server(service, server)
    server_host = os.getenv("SERVER_HOST", "localhost")
    server_port = os.getenv("SERVER_PORT", "50051")
    server.add_insecure_port(f'{server_host}:{server_port}')
    print(f"Starting server on {server_host}:{server_port}")
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    serve()
