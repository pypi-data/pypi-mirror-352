from oneclickai.YOLO import fit_yolo_model

# training data path
train_data_path = './yolo_dataset'
train_label_path = './yolo_dataset'

# validation data path
val_data_path = './yolo_dataset'
val_label_path = './yolo_dataset'

# fit model
fit_yolo_model(train_data_path, train_label_path, val_data_path, val_label_path, epochs=20)