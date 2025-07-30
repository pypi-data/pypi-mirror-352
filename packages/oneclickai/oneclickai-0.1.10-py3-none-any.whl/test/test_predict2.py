#%%
from oneclickai.YOLO import stream, load_model

# example usage
model = load_model("./20250604_1135/yolo_model_best.h5")

# coco dataset cls names
coco_cls_names = ['handcream']

stream(model, conf=0.4, class_names=coco_cls_names, video_source=0)