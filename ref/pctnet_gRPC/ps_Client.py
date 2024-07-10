import grpc
import cv2
import numpy as np
import portrait_stylization_pb2
import portrait_stylization_pb2_grpc

# Load and encode an image to bytes
img = cv2.imread('../input.jpg')
_, img_encoded = cv2.imencode('.jpg', img)
image_data = img_encoded.tobytes()

# Set up a connection to the server.
channel = grpc.insecure_channel('localhost:50053')
stub = portrait_stylization_pb2_grpc.PortraitStylizationStub(channel)

# Create a request with the encoded image as bytes
request = portrait_stylization_pb2.ImageRequest(image_data=image_data)

# Get the response
response = stub.StylizeImage(request)

# Decode the response
nparr = np.frombuffer(response.image_data, dtype=np.uint8)
img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
cv2.imwrite('stylized_image.jpg', img)
