from concurrent import futures
import grpc
import UnityGeneral_pb2
import UnityGeneral_pb2_grpc

from PIL import Image, ImageOps
import io

class UnityGrpcService(UnityGeneral_pb2_grpc.UnityGrpcServiceServicer):    
    #############################################################
    ####    初始化、函数注册
    #############################################################
    def __init__(self):
        # 初始化路由字典
        self.routes = {}
        self.add_func_route("ImgTest", self.handle_image_test, "bytes|none", "bytes|none")
        self.add_func_route("StrTest", self.handle_string_test, "var|float", "list|string")
        # self.add_func_route("PortraitStylization",self.hanlde_PortraitStylization,"bytes","bytes")
        # self.add_func_route("FaceRecognition",self.hanlde_FaceRecognition,"bytes","bytes")
    

    def add_func_route(self, func_name: str, endpoint, request_type: str, response_type: str):
        self.routes[func_name] = {
            "endpoint": endpoint,
            "request_type": request_type,
            "response_type": response_type
        }

       
    #############################################################
    ####    入口函数、辅助解析函数
    #############################################################

    def RemoteCall(self, request, context):
        func = request.func
        route_info = self.routes.get(func)
        if not route_info:
            response = self.encode_response(False, f"Function '{func}' not supported")
            return response
        
        try:
            # 解析info字符串为字典
            reqs = self.parse_info(request.info)
            # 解码UData
            data = self.decode_udata(request.data, route_info["request_type"])
            # 调用相应的处理函数
            success, info, result = route_info["endpoint"](reqs, data)
            # 编码UData
            response = self.encode_response(success, info, result, route_info["response_type"])
        except Exception as e:
            response = self.encode_response(False, str(e))
            return response
        
        return response
    
    @staticmethod
    def parse_info(info_str: str) -> dict:
        """解析形如 'var1=xxx|var2=yyy|...' 的字符串为字典."""
        info_dict = {}
        pairs = info_str.split('|')
        for pair in pairs:
            if '=' in pair:
                key, value = pair.split('=', 1)
                info_dict[key.strip()] = value.strip()
        return info_dict

    @staticmethod
    def decode_udata(data: UnityGeneral_pb2.UData, type: str):
        """根据提供的类型描述从 UData 解包数据。"""
        category, subtype = type.split('|')

        if category == 'none' and subtype == 'none':
            return None        
        
        if category == 'bytes' and subtype == 'none' and data.HasField('bytes_data'):
            return data.bytes_data        
        
        expected_field = subtype + '_value'

        if category == 'var' and data.HasField('var_single'):
            return getattr(data.var_single, expected_field)     
                   
        elif category == 'list' and data.var_list:
            return [getattr(item, expected_field) for item in data.var_list]
                           
        else:
            raise ValueError(f"Unsupported TYPE specification : {type}")

    @staticmethod
    def encode_response(success: bool, info: str, data:any = None, type:str = "none|none") -> UnityGeneral_pb2.Response:
        """根据提供的类型描述将数据打包到 Response。"""
        category, subtype = type.split('|')
        expected_field = subtype + '_value'
        response = UnityGeneral_pb2.Response(success=success, info=info)

        if not data:
            pass

        elif category == 'none' and subtype == 'none':
            pass             

        elif category == 'bytes' and subtype == 'none':
            response.data.bytes_data = data

        elif category == 'var':
            setattr(response.data.var_single, expected_field, data)

        elif category == 'list':
            for item in data:
                new_var = response.data.var_list.add()
                setattr(new_var, expected_field, item)
        else:
            raise ValueError(f"Unsupported TYPE specification : {type}")
        
        return response


    #############################################################
    ####    具体的路由函数
    #############################################################

    
    def handle_image_test(self, reqs: dict, data: bytes):
        # 示例逻辑：从bytes数据读取图像，进行反色处理，再保存为bytes
        img = Image.open(io.BytesIO(data))
        inverted_image = ImageOps.invert(img)
        byte_arr = io.BytesIO()
        inverted_image.save(byte_arr, format='JPEG')
        return True, "Inverted image processed", byte_arr.getvalue()

    def handle_string_test(self, reqs: dict, data: float):
        # 示例逻辑：从reqs中获取num，并基于float数据构造字符串列表响应
        num = int(reqs.get('num', -1))  # Default to -1 if num is not provided
        info = f"Get num from reqs as {num}."
        str_list = [str(data) for _ in range(3)]  # 示例: 根据float生成3个相同的字符串
        return True, info, str_list
    
    # def hanlde_PortraitStylization(self, reqs: dict, data: bytes):
    #     # 风格化服务


    #     return True, "PortraitStylization", rdata
    
    # def hanlde_FaceRecognition(self, reqs: dict, data: bytes):
    #     # 人脸识别服务
        
        
    #     return True, "FaceRecognition", rdata

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    UnityGeneral_pb2_grpc.add_UnityGrpcServiceServicer_to_server(UnityGrpcService(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    print('Starting server. Listening on port 50051.')
    server.wait_for_termination()

if __name__ == '__main__':
    serve()
