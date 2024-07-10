
# -*- coding: utf-8 -*-
import cv2
import numpy as np
import time
import grpc
import portrait_stylization_pb2
import portrait_stylization_pb2_grpc

from ImageSourceManager import ImageSourceManager

# Set up a connection to the gRPC server.
channel = grpc.insecure_channel('192.168.5.205:50053')
stub = portrait_stylization_pb2_grpc.PortraitStylizationStub(channel)

video_manager = ImageSourceManager(source="Video", videoPath=r"D:\MediaPipe\poseDetection\soloDance720.mp4", startTime=10)
# camera_manager = ImageSourceManager(source="Camera", cameraNum=0, resolution=(1920, 1080))
frame_delay = int(1000 / video_manager.fps)  # Calculate frame delay in milliseconds

if not video_manager.capture.isOpened():
    print("Failed to open camera")
    exit()

frame = video_manager.getCurrentFrame()
height=frame.shape[0]
width=frame.shape[1]
channel=frame.shape[2]

while video_manager.capture.isOpened():
    frame = video_manager.getCurrentFrame()
    if frame is not None:
        start_time = time.time()
        # encoded_string = base64.b64encode(buffer).decode('utf-8')
        request = portrait_stylization_pb2.ImageRequest(image_data=frame.tobytes(), height=height, width=width, channel=channel)
        
        # Send the frame to the gRPC server and get the stylized image
        response = stub.StylizeImage(request)

        image_array = np.frombuffer(response.image_data, dtype=np.uint8)
        cartoon_img = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
        # process_time = time.time()
        cv2.imshow('Cartoon Camera', cartoon_img)
        display_time = time.time()

        # cv2.imshow("Video Frame", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):  # Wait for frame delay and check for 'q' to quit
        # if  0xFF == ord('q'):  # Wait for frame delay and check for 'q' to quit
            break

        # print(f"Read Time: {read_time - start_time:.3f} sec")
        # print(f"Inference Time: {inference_time - read_time:.3f} sec")
        # print(f"Processing Time: {process_time - inference_time:.3f} sec")
        # print(f"Display Time: {display_time - process_time:.3f} sec")
        print(f"Total Loop Time: {display_time - start_time:.3f} sec\n")

cv2.destroyAllWindows()
