
# -*- coding: utf-8 -*-
import cv2
import numpy as np
import time
import grpc
import base64
import portrait_stylization_pb2
import portrait_stylization_pb2_grpc

# Set up a connection to the gRPC server.
channel = grpc.insecure_channel('localhost:50053')
stub = portrait_stylization_pb2_grpc.PortraitStylizationStub(channel)

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

if not cap.isOpened():
    print("Failed to open camera")
    exit()

try:
    while True:
        start_time = time.time()
        
        ret, frame = cap.read()
        print(frame.shape)
        read_time = time.time()
        
        if not ret:
            print("Failed to receive frames")
            break

        # Encode the frame to send to gRPC service
        # _, buffer = cv2.imencode('.jpg', frame)
        # encoded_string = base64.b64encode(buffer).decode('utf-8')
        request = portrait_stylization_pb2.ImageRequest(image_data=frame.tobytes(), height=frame.shape[0], width=frame.shape[1], channel=frame.shape[2])
        
        # Send the frame to the gRPC server and get the stylized image
        response = stub.StylizeImage(request)
        inference_time = time.time()

        # Decode the received image
        # response_data = base64.b64decode(response.image_data)
        # image_array = np.frombuffer(response_data, dtype=np.uint8)
        image_array = np.frombuffer(response.image_data, dtype=np.uint8)
        cartoon_img = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
        process_time = time.time()
        cv2.imshow('Cartoon Camera', cartoon_img)

        # response_image = np.frombuffer(response.image_data, dtype=np.uint8)
        # response_image = response_image.reshape(frame.shape)  # Reshape based on original frame shape
        
        # process_time = time.time()
        # cv2.imshow('Cartoon Camera', response_image)

        display_time = time.time()

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        

        print(f"Read Time: {read_time - start_time:.3f} sec")
        print(f"Inference Time: {inference_time - read_time:.3f} sec")
        print(f"Processing Time: {process_time - inference_time:.3f} sec")
        print(f"Display Time: {display_time - process_time:.3f} sec")
        print(f"Total Loop Time: {display_time - start_time:.3f} sec\n")

finally:
    cap.release()
    cv2.destroyAllWindows()
