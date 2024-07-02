import grpc
import UnityGeneral_pb2
import UnityGeneral_pb2_grpc
from PIL import Image

def run():
    # 创建与服务器的连接
    channel = grpc.insecure_channel('localhost:50051')
    stub = UnityGeneral_pb2_grpc.UnityGrpcServiceStub(channel)


    #############################################################
    # 处理图像反色
    with open('input.jpg', 'rb') as f:
        img_data = f.read()
    
    request = UnityGeneral_pb2.Request(func='ImgTest', info='')
    request.data.bytes_data = img_data
    response = stub.RemoteCall(request)
    print("\nImage Test Response:")
    print("Success:", response.success)
    print("Info:", response.info)

    # 保存反色处理后的图像
    if response.success:
        with open('output.jpg', 'wb') as f:
            f.write(response.data.bytes_data)


    #############################################################
    # 测试字符串列表生成
    request = UnityGeneral_pb2.Request(func='StrTest', info=r'num=5|num2=100')
    request.data.var_single.float_value = 3.14        
    response = stub.RemoteCall(request)
    print("\nString Test Response:")
    print("Success:", response.success)
    print("Info:", response.info)
    print("Data:", response.data)

if __name__ == '__main__':
    run()
