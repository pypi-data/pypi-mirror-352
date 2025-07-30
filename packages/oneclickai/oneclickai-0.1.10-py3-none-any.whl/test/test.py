from oneclickai.YOLO import fit_yolo_model

# 학습용 데이터 위치, 이미지 데이터(.png, .jpg, .jpeg), 라벨 데이터(.txt)
train_data_path = './yolo_dataset'
train_label_path = './yolo_dataset'

# 검증용 데이터 위치, 이미지 데이터(.png, .jpg, .jpeg), 라벨 데이터(.txt)
val_data_path = './yolo_dataset'
val_label_path = './yolo_dataset'

# 모델 학습 (데이터 위치, epochs)
fit_yolo_model(train_data_path, train_label_path, val_data_path, val_label_path, epochs=30)