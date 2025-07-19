

# YOLOv8犬类分类项目指南
#喜欢的话请点个小小的start谢谢😘💕
基于 YOLOv8 的犬类品种检测项目，使用哈佛大学狗狗数据集完成训练与验证。

## 环境准备

在运行程序前，请确保以下环境正确配置：

- **操作系统**：Windows、Linux 或 macOS（推荐 Windows，含 PyQt5 GUI 界面）
- **Python 版本**：Python 3.8+
- **依赖库**：安装所需的 Python 第三方库
- **数据库**：MySQL 数据库服务已安装并运行
- **GPU 支持（可选）**：如需加速训练或推理，建议安装 CUDA 和 cuDNN，并确保 GPU 驱动正常

## 安装依赖库

在终端或命令行中运行以下命令安装依赖：

```bash
# 基础环境
pip install ultralytics pymysql PyQt5 requests torch torchvision

# GPU 环境（可选）
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124
```

## 下载预训练模型

运行以下脚本下载预训练模型文件：

```bash
python download_models.py
```

该脚本会将模型文件下载到 `./pre_trained_model` 目录中。

## 准备数据集

### 标注文件转换

将 PASCAL VOC 格式的 XML 文件转换为 YOLO 格式。运行 `voc_to_yolo.py` 脚本完成转换：

```bash
python voc_to_yolo.py
```

确保输入目录 (`./VOC_Dataset`) 包含 XML 文件，输出目录 (`./YOLO_Dataset`) 将生成对应的 YOLO 格式标签文件。

### 数据集配置

编辑 `data.yaml` 文件，确保路径指向正确的训练集、验证集和测试集目录。例如：

```yaml
train: ./YOLO_Dataset/Train_YOLO/images
val: ./YOLO_Dataset/Validation_YOLO/images
test: ./YOLO_Dataset/Test_YOLO/images

nc: 23  # 类别数量
names: ['husky', 'beagle', 'chihuahua', ...]  # 类别名称
```

## 训练模型

运行 `training_model.py` 脚本以训练模型：

```bash
python training_model.py
```

如果使用 GPU，请将 `device='cpu'` 修改为 `device='cuda'`。训练完成后，模型权重将保存到 `./trained_models` 目录中。

## 配置 MySQL 数据库

### 创建数据库

使用 MySQL 客户端工具（如 Navicat 或 MySQL Workbench），执行 `dog_db.sql` 文件以创建数据库和表：

```sql
SOURCE G:/Couresware/DeepLearning_project/YOLOv8 _Dogs_Classification_Project/YOLOv8 _Dogs_classification/dog_db.sql;
```

### 修改数据库连接信息

打开 `dogs_windows.py` 文件，检查 `get_db_connection` 函数中的数据库连接参数，确保与本地 MySQL 配置一致：

```python
pymysql.connect(
    host='localhost',
    user='root',
    password='123456',
    database='dog_db',
    charset='utf8mb4',
    cursorclass=pymysql.cursors.DictCursor
)
```

## 启动 GUI 应用程序

运行 `dogs_windows.py` 脚本以启动狗品种识别系统的图形界面：

```bash
python dogs_windows.py
```

程序启动后，您可以上传图片进行检测，查看识别结果、历史记录等。

## 测试和验证

### 测试模型

在训练完成后，使用 `model.val()` 和 `model.predict()` 方法对模型进行验证和测试。示例代码已在 `training_model.py` 中提供。

### 导出模型

如果需要将模型部署到其他平台，可以导出为 ONNX 或 PyTorch 格式：

```python
model.export(format='onnx', file='./exported_models/dog_classifier.onnx')
model.export(format='pt', file='./exported_models/dog_classifier.pt')
```
