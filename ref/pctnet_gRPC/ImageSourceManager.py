import cv2
import time

class ImageSourceManager:
    def __init__(self, source="Camera", cameraNum=0, resolution=(1920, 1080), videoPath=None, startTime=0):
        """初始化图像源管理器，设置为从摄像头或视频文件读取。"""
        self.source = source
        self.capture = None
        
        if source == "Camera":
            self.capture = cv2.VideoCapture(cameraNum)
            self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, resolution[0])
            self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, resolution[1])
        elif source == "Video":
            if videoPath is None:
                raise ValueError("A video path must be provided for video source.")
            self.capture = cv2.VideoCapture(videoPath)
            # 跳转到视频的指定开始时间
            if startTime > 0:
                self.fps = self.capture.get(cv2.CAP_PROP_FPS) if self.capture.isOpened() else 30
                self.capture.set(cv2.CAP_PROP_POS_FRAMES, int(self.fps * startTime)) 
        
        # 捕获一帧以检查
        frame = self.getCurrentFrame()
        if frame is not None:
            print(f"输入图像格式为 {frame.shape}.")
        print(" == 等待1秒用于预热摄像头 == ")
        time.sleep(1)

    def getCurrentFrame(self):
        """从图像源获取当前帧。"""
        if self.capture is not None and self.capture.isOpened():
            ret, frame = self.capture.read()
            if ret:
                return frame
            print("\n ==================================\n")
            print(" Failed to grab frame from camera.")
            print("\n ==================================\n")
            print(" Launch FAILED. Please RESTART the code ")
            print("\n ==================================\n")
        return None

    def release(self):
        """释放资源，关闭视频文件或摄像头。"""
        if self.capture is not None:
            self.capture.release()

# 使用示例
if __name__ == "__main__":
    # # 使用摄像头
    # camera_manager = ImageSourceManager(source="Camera", cameraNum=0, resolution=(1920, 1080))
    # while camera_manager.capture.isOpened():
    #     frame = camera_manager.getCurrentFrame()
    #     if frame is not None:
    #         print(frame.shape)
    #         cv2.imshow("Camera Frame", frame)
    #         # 按'q'退出
    #         if cv2.waitKey(1) & 0xFF == ord('q'):
    #             break

    # 使用视频文件
    video_manager = ImageSourceManager(source="Video", videoPath=r"D:\MediaPipe\poseDetection\soloDance.mp4", startTime=10)
    frame_delay = int(1000 / video_manager.fps)  # Calculate frame delay in milliseconds
    while video_manager.capture.isOpened():
        frame = video_manager.getCurrentFrame()
        if frame is not None:
            cv2.imshow("Video Frame", frame)
            if cv2.waitKey(frame_delay) & 0xFF == ord('q'):  # Wait for frame delay and check for 'q' to quit
                break

    cv2.destroyAllWindows()
