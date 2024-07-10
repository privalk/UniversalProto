import grpc
import cv2
import numpy as np
import time
from concurrent import futures
import portrait_stylization_pb2
import portrait_stylization_pb2_grpc

class PortraitStylizationServicer(portrait_stylization_pb2_grpc.PortraitStylizationServicer):
    def __init__(self):
        # self.img_cartoon = pipeline(Tasks.image_portrait_stylization, model='damo/cv_unet_person-image-cartoon-3d_compound-models')
        # self.img_cartoon = pipeline(Tasks.image_portrait_stylization, model='../cv_unet_person-image-cartoon_compound-models', model_revision='v1.0.5')
        print("fake run")

    def StylizeImage(self, request, context):
        start_time = time.time()
        strTime = time.strftime("%Y-%m-%d %H:%M:%S")

        expected_size = request.width * request.height * request.channel
        received_size = len(request.image_data)
        
        print(f"{strTime} - 接收到的数据长度：{received_size}")
        print(f"{strTime} - 预期的数据长度：{expected_size}")

        # 解码图像
        nparr = np.frombuffer(request.image_data, dtype=np.uint8)
        
        # 判断接收到的数据是否符合预期大小
        if received_size == expected_size:
            print(f"{strTime} - 使用预设形状解码")
            nparr = nparr.reshape((request.height, request.width, request.channel))
        else:
            print(f"{strTime} - 使用JPEG解码")
            nparr = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        # # 解码图像        
        # nparr = np.frombuffer(request.image_data, dtype=np.uint8)
        # print(f"{strTime} - 解码后的二进制数据形状：", nparr.shape)
        # nparr = nparr.reshape((request.height, request.width, request.channel))

        # img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        # 处理图像
        # result = self.img_cartoon(nparr)
        result = nparr[...,::-1]

        # 将处理后的图像编码为JPEG格式
        _, img_encoded = cv2.imencode('.jpg', result)
        
        finish_time = time.time()
        print(f"Total Time: {finish_time - start_time:.3f} sec\n")

        return portrait_stylization_pb2.ImageReply(image_data=img_encoded.tobytes())

# Create a gRPC server
server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
portrait_stylization_pb2_grpc.add_PortraitStylizationServicer_to_server(
    PortraitStylizationServicer(), server)

print('Starting server. Listening on port 50053.')
server.add_insecure_port('[::]:50053')
server.start()
server.wait_for_termination()


# docker run --runtime=nvidia -it --rm -v "${PWD}:/DCT-Net" -w /DCT-Net -p 50053:50053 modelscope-dct-net-base-rebuild bash
