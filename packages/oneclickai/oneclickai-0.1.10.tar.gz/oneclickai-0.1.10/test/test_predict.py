from oneclickai.YOLO import load_model, predict, draw_result
import os 
import cv2
import numpy as np

data_path = 'C:/Users/osy04/Desktop/wok_me/project/yolo/images/train2017/'
file_img = os.listdir(data_path)

# Load the model
model = load_model("YOLO_coco")

# Single image prediction
for i in range(5):
    image = cv2.imread(data_path + file_img[i])/255.0
    result_annotation = predict(model, image)
    result_image = draw_result(np.array(image), result_annotation)
    cv2.imshow('image', result_image)
    cv2.waitKey(0)