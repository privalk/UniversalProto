import grpc
import cv2
import numpy as np
import time
from concurrent import futures
import portrait_stylization_pb2
import portrait_stylization_pb2_grpc
from modelscope.outputs import OutputKeys
from modelscope.pipelines import pipeline
from modelscope.utils.constant import Tasks

class PortraitStylizationServicer(portrait_stylization_pb2_grpc.PortraitStylizationServicer):
    def __init__(self):
        # self.img_cartoon = pipeline(Tasks.image_portrait_stylization, model='damo/cv_unet_person-image-cartoon-3d_compound-models')
        self.img_cartoon = pipeline(Tasks.image_portrait_stylization, model='../cv_unet_person-image-cartoon_compound-models', model_revision='v1.0.5')

    def StylizeImage(self, request, context):
        start_time = time.time()
        strTime = time.strftime("%Y-%m-%d %H:%M:%S")

        # 解码图像        
        nparr = np.frombuffer(request.image_data, dtype=np.uint8)
        print(f"{strTime} - 解码后的二进制数据形状：", nparr.shape)
        nparr = nparr.reshape((request.height, request.width, request.channel))

        # img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        # 处理图像
        result = self.img_cartoon(nparr)

        # 将处理后的图像编码为JPEG格式
        _, img_encoded = cv2.imencode('.jpg', result[OutputKeys.OUTPUT_IMG])
        
        finish_time = time.time()
        print(f"Total Time: {finish_time - start_time:.3f} sec\n")


        # StartTime = time.time()
        # # 图像本地路径
        # img_path = 'testLocal.jpg'
        # # 图像url链接
        # # img_path = '/test/images/image_cartoon.png'
        # result = self.img_cartoon(img_path)
        # cv2.imwrite('result01.jpg', result[OutputKeys.OUTPUT_IMG])

        # EndTime = time.time()
        # CostTime=EndTime-StartTime
        # print(f'代码运行时间：{CostTime:.3f}')



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
