from ultralytics import YOLO

# 加载预训练模型（从本地加载）
model = YOLO('./pre_trained_model/yolov8n.pt')  # 本地路径

# 开始训练
results = model.train(
    data='G:/Couresware/DeepLearning_project/YOLOv8 _Dogs_Classification_Project/YOLOv8 _Dogs_classification/YOLO_Dataset/data.yaml',
    # 确保数据集配置文件正确
    epochs=200,  # 增加训练轮数以更好地学习复杂分类任务
    batch=16,
    imgsz=640,
    device='cpu',  # 使用cpu
    optimizer='Adam',
    lr0=0.001,
    augment=True,  # 启用数据增强
    pretrained=True,
    classes=23,  # 设置类别数为23
    workers=4  # 增加数据加载器工作线程
)

# 验证模型
metrics = model.val()

# 测试集评估
metrics_test = model.val(split='test')

# 预测示例
results = model.predict('test.jpg', save=True, conf=0.5)

# 将训练好的模型保存到本地
model.export(format='onnx', file='./trained_modles/trained_model.onnx')
model.export(format='pt', file='./trained_modles/trained_model.pt')
