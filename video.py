video_path = "D:/直播素材/videos/lv.mp4"
# video_path = "D:/直播素材/videos/v.mov"
import cv2
import numpy as np

def resize_and_pad(frame, target_width, aspect_ratio):
    """根据目标宽度和长宽比调整图像大小，并在周围填充绿色"""
    original_height, original_width = frame.shape[:2]
    
    # 计算目标高度以匹配给定的宽高比
    target_height = int(target_width / aspect_ratio)
    
    # 计算缩放比例
    scale_ratio = target_width / original_width
    
    new_height = int(original_height * scale_ratio)
    
    # 调整大小
    resized_frame = cv2.resize(frame, (target_width, new_height), interpolation=cv2.INTER_LANCZOS4)
    
    # 创建一个绿色背景的画布
    canvas = np.zeros((target_height, target_width, 3), dtype=np.uint8)
    canvas[:] = (0, 255, 0)  # 绿色填充
    
    # 如果新高度小于目标高度，则垂直居中；否则水平居中
    if new_height < target_height:
        y_offset = (target_height - new_height) // 2
        x_offset = 0
    else:
        y_offset = 0
        x_offset = (target_width - resized_frame.shape[1]) // 2
    
    # 将调整后的帧放到绿色背景上
    canvas[y_offset:y_offset + new_height, x_offset:x_offset + resized_frame.shape[1]] = resized_frame[:, :target_width]
    
    return canvas


cap = cv2.VideoCapture(video_path)

# 设置目标宽度和长宽比
target_width = 300
aspect_ratio = 9 / 16

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break
    
    # 调整帧大小并添加绿色填充以符合目标尺寸
    processed_frame = resize_and_pad(frame, target_width, aspect_ratio)
    
    # 显示处理后的帧
    cv2.imshow('Resized and Padded Video Playback', processed_frame)
    
    key = cv2.waitKey(25) & 0xFF
    if key == ord('q'):  # 按 'q' 键退出
        break

cap.release()
cv2.destroyAllWindows()