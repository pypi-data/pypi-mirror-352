# ==================================================================================
# L2CS: Based on https://github.com/Ahmednull/L2CS-Net/blob/main/l2cs/vis.py
# ==================================================================================
import cv2
import numpy as np

from face_analysis.gazes.results import GazeResultContainer

def draw_gaze(a,b,c,d,image_in, pitchyaw, thickness=2, color=(255, 255, 0),sclae=2.0):
    """Draw gaze angle on given image with a given eye positions."""
    image_out = image_in
    (h, w) = image_in.shape[:2]
    length = c
    pos = (int(a+c / 2.0), int(b+d / 2.0))
    if len(image_out.shape) == 2 or image_out.shape[2] == 1:
        image_out = cv2.cvtColor(image_out, cv2.COLOR_GRAY2BGR)
    dx = -length * np.sin(pitchyaw[0]) * np.cos(pitchyaw[1])
    dy = -length * np.sin(pitchyaw[1])
    cv2.arrowedLine(image_out, tuple(np.round(pos).astype(np.int32)),
                   tuple(np.round([pos[0] + dx, pos[1] + dy]).astype(int)), color,
                   thickness, cv2.LINE_AA, tipLength=0.18)
    return image_out

def draw_bbox(frame: np.ndarray, bbox: np.ndarray, color=(0, 255, 0), thickness=1):
    
    x_min = int(bbox[0])
    if x_min < 0:
        x_min = 0
    y_min = int(bbox[1])
    if y_min < 0:
        y_min = 0
    x_max = int(bbox[2])
    y_max = int(bbox[3])

    cv2.rectangle(frame, (x_min, y_min), (x_max, y_max), color, thickness)
    return frame

def render(frame: np.ndarray, results: GazeResultContainer):

    image_out = frame.copy()

    # if there are bboxes to render
    if results.bboxes.shape[0] != 0:

        # Draw bounding boxes
        for bbox in results.bboxes:
            image_out = draw_bbox(image_out, bbox)

    # Draw Gaze
    for i in range(results.pitch.shape[0]):

        pitch = results.pitch[i]
        yaw = results.yaw[i]

        if results.bboxes.shape[0] != 0:
            bbox = results.bboxes[i]
            # Extract safe min and max of x,y
            x_min=int(bbox[0])
            if x_min < 0:
                x_min = 0
            y_min=int(bbox[1])
            if y_min < 0:
                y_min = 0
            x_max=int(bbox[2])
            y_max=int(bbox[3])
        else:
            x_min=0
            y_min=0
            y_max=image_out.shape[0]
            x_max=image_out.shape[1]

        # Compute sizes
        bbox_width = x_max - x_min
        bbox_height = y_max - y_min

        draw_gaze(x_min,y_min,bbox_width, bbox_height,image_out,(pitch,yaw),color=(0,0,255))

    return image_out
