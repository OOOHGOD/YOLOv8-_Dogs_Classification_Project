import sys
import pymysql
import shutil
import os
import uuid
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QLabel, QPushButton, QVBoxLayout, QHBoxLayout,
    QWidget, QFileDialog, QMessageBox, QTableWidget, QTableWidgetItem, QDialog, QSlider
)
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
from ultralytics import YOLO

try:
    from dogs_windows import HistoryWindow
except ImportError:
    print("未能导入 HistoryWindow，请检查 dogs_windows 模块是否存在。")

model = YOLO('./trained_models/dog_classification_yolov8n-200epoch/weights/best.pt')


# MySQL 数据库连接
def get_db_connection():
    try:
        return pymysql.connect(
            host='localhost',
            user='root',
            password='123456',
            database='dog_db',
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
    except pymysql.Error as e:
        print(f"数据库连接失败: {e}")
        return None


# 查询历史记录
def get_history_records():
    conn = get_db_connection()
    if conn is None:
        return []
    cursor = conn.cursor()
    try:
        cursor.execute('SELECT id, image_path, breed, confidence FROM dog_recognition ORDER BY id DESC')
        records = cursor.fetchall()
        return records
    except pymysql.Error as e:
        print(f"查询历史记录错误：{e}")
        return []
    finally:
        cursor.close()
        conn.close()


# 预测函数
def predict_dog_breed(image_path, threshold=0.5):
    try:
        results = model(image_path)
        names = model.names
        boxes = results[0].boxes
        if len(boxes) == 0 or boxes.conf.max().item() < threshold:
            return "未知", 0.0, "", ""
        max_conf_idx = boxes.conf.argmax()
        class_id = boxes.cls[max_conf_idx].item()
        confidence = boxes.conf[max_conf_idx].item()
        breed = names[class_id]
        description = dog_info.get(breed, {}).get("description", "暂无描述")
        care = dog_info.get(breed, {}).get("care", "暂无建议")
        return breed, confidence, description, care
    except Exception as e:
        print(f"预测狗品种时出错: {e}")
        return "未知", 0.0, "", ""


# 数据库存储
def save_to_database(image_path, breed, confidence):
    conn = get_db_connection()
    if conn is None:
        return
    cursor = conn.cursor()
    try:
        cursor.execute('INSERT INTO dog_recognition (image_path, breed, confidence) VALUES (%s, %s, %s)',
                       (image_path, breed, confidence))
        conn.commit()
    except pymysql.Error as e:
        print(f"保存到数据库时出错：{e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()


dog_info = {
    "husky": {"description": "哈士奇是一种非常聪明、活泼、忠诚的狗，适合喜欢户外活动的家庭。",
              "care": "需要定期梳理毛发，保持清洁；需要大量的运动和社交活动；饮食要均衡，避免肥胖。"},
    "beagle": {"description": "比格犬友好、好奇、善于交际，适合家庭养。",
               "care": "需要定期梳理毛发，保持清洁；需要适量的运动；饮食要均衡，避免肥胖。"},
    "chihuahua": {"description": "吉娃娃体型小、活泼、忠诚，适合喜欢小动物的家庭。",
                  "care": "需要定期梳理毛发，保持清洁；需要适量的运动；饮食要均衡，避免肥胖。"},
    "japanese_spaniel": {"description": "日本柴犬是一种聪明、活泼、忠诚的狗，适合家庭养。",
                         "care": "需要定期梳理毛发，保持清洁；需要适量的运动；饮食要均衡，避免肥胖。"},
    "pekinese": {"description": "北京犬是一种友好、活泼、忠诚的狗，适合家庭养。",
                 "care": "需要定期梳理毛发，保持清洁；需要适量的运动；饮食要均衡，避免肥胖。"},
    "shih_tzu": {"description": "西高地白梗是一种友好、活泼、忠诚的狗，适合家庭养。",
                 "care": "需要定期梳理毛发，保持清洁；需要适量的运动；饮食要均衡，避免肥胖。"},
    "afghan_hound": {"description": "阿富汗猎犬是一种聪明、活泼、忠诚的狗，适合喜欢户外活动的家庭。",
                     "care": "需要定期梳理毛发，保持清洁；需要大量的运动和社交活动；饮食要均衡，避免肥胖。"},
    "airedale": {"description": "边境牧羊犬是一种聪明、活泼、忠诚的狗，适合喜欢户外活动的家庭。",
                 "care": "需要定期梳理毛发，保持清洁；需要大量的运动和社交活动；饮食要均衡，避免肥胖。"},
    "basset": {"description": "巴塞特猎犬是一种友好、好奇、善于交际的狗，适合家庭养。",
               "care": "需要定期梳理毛发，保持清洁；需要适量的运动；饮食要均衡，避免肥胖。"},
    "blenheim_spaniel": {"description": "布林杰猎犬是一种聪明、活泼、忠诚的狗，适合喜欢户外活动的家庭。",
                         "care": "需要定期梳理毛发，保持清洁；需要大量的运动和社交活动；饮食要均衡，避免肥胖。"},
    "bloodhound": {"description": "寻血猎犬是一种聪明、活泼、忠诚的狗，适合喜欢户外活动的家庭。",
                   "care": "需要定期梳理毛发，保持清洁；需要大量的运动和社交活动；饮食要均衡，避免肥胖。"},
    "corgi": {"description": "威尔士柯基犬是一种聪明、活泼、忠诚的狗，适合家庭养。",
              "care": "需要定期梳理毛发，保持清洁；需要适量的运动；饮食要均衡，避免肥胖。"},
    "dandie_dinmont": {"description": "丹迪 Dinmont 牧羊犬是一种聪明、活泼、忠诚的狗，适合喜欢户外活动的家庭。",
                       "care": "需要定期梳理毛发，保持清洁；需要大量的运动和社交活动；饮食要均衡，避免肥胖。"},
    "irish_wolfhound": {"description": "爱尔兰猎狼犬是一种聪明、活泼、忠诚的狗，适合喜欢户外活动的家庭。",
                        "care": "需要定期梳理毛发，保持清洁；需要大量的运动和社交活动；饮食要均衡，避免肥胖。"},
    "maltese_dog": {"description": "马尔泰斯犬是一种友好、活泼、忠诚的狗，适合家庭养。",
                    "care": "需要定期梳理毛发，保持清洁；需要适量的运动；饮食要均衡，避免肥胖。"},
    "papillon": {"description": "蝴蝶犬是一种聪明、活泼、忠诚的狗，适合家庭养。",
                 "care": "需要定期梳理毛发，保持清洁；需要适量的运动；饮食要均衡，避免肥胖。"},
    "retriever": {"description": "拉布拉多寻回犬是一种聪明、活泼、忠诚的狗，适合喜欢户外活动的家庭。",
                  "care": "需要定期梳理毛发，保持清洁；需要大量的运动和社交活动；饮食要均衡，避免肥胖。"},
    "rhodesian_ridgeback": {"description": "罗德西亚背脊犬是一种聪明、活泼、忠诚的狗，适合喜欢户外活动的家庭。",
                            "care": "需要定期梳理毛发，保持清洁；需要大量的运动和社交活动；饮食要均衡，避免肥胖。"},
    "saluki": {"description": "萨卢基是一种聪明、活泼、忠诚的狗，适合喜欢户外活动的家庭。",
               "care": "需要定期梳理毛发，保持清洁；需要大量的运动和社交活动；饮食要均衡，避免肥胖。"},
    "staffordshire_bullterrier": {"description": "斯塔福德郡斗牛梗是一种聪明、活泼、忠诚的狗，适合喜欢户外活动的家庭。",
                                  "care": "需要定期梳理毛发，保持清洁；需要大量的运动和社交活动；饮食要均衡，避免肥胖。"},
    "standard_schnauzer": {"description": "标准 Schnauzer 是一种聪明、活泼、忠诚的狗，适合喜欢户外活动的家庭。",
                           "care": "需要定期梳理毛发，保持清洁；需要大量的运动和社交活动；饮食要均衡，避免肥胖。"},
    "toy_terrier": {"description": "玩具梗是一种聪明、活泼、忠诚的狗，适合家庭养。",
                    "care": "需要定期梳理毛发，保持清洁；需要适量的运动；饮食要均衡，避免肥胖。"},
    "vizsla": {"description": "维兹拉是一种聪明、活泼、忠诚的狗，适合喜欢户外活动的家庭。",
               "care": "需要定期梳理毛发，保持清洁；需要大量的运动和社交活动；饮食要均衡，避免肥胖。"},
}


# 主窗口
class DogBreedDetectorApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("狗品种识别系统")
        self.setFixedSize(800, 600)  # 调整窗口大小以适应新控件

        main_layout = QVBoxLayout()
        content_layout = QHBoxLayout()

        self.image_label = QLabel("请上传图片")
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setStyleSheet("border: 2px dashed #aaa; background-color: #333; color: white;")
        self.image_label.setFixedSize(500, 400)
        content_layout.addWidget(self.image_label)

        result_panel_layout = QVBoxLayout()

        self.upload_btn = QPushButton("图片上传")
        self.upload_btn.clicked.connect(self.upload_image)
        result_panel_layout.addWidget(self.upload_btn)

        self.detect_btn = QPushButton("开始检测")
        self.detect_btn.clicked.connect(self.detect_breed)
        self.detect_btn.setEnabled(False)
        result_panel_layout.addWidget(self.detect_btn)

        self.show_result_btn = QPushButton("最近一次检测")
        self.show_result_btn.clicked.connect(self.show_last_result)
        self.show_result_btn.setEnabled(True)
        result_panel_layout.addWidget(self.show_result_btn)

        self.history_btn = QPushButton("查看历史记录")
        self.history_btn.clicked.connect(self.show_history)
        self.history_btn.setEnabled(True)
        result_panel_layout.addWidget(self.history_btn)

        self.clear_btn = QPushButton("清除图片")
        self.clear_btn.clicked.connect(self.clear_image)
        self.clear_btn.setEnabled(False)
        result_panel_layout.addWidget(self.clear_btn)

        # 置信度阈值滑块
        self.threshold_label = QLabel("置信度阈值：0.50")
        self.threshold_label.setAlignment(Qt.AlignCenter)
        result_panel_layout.addWidget(self.threshold_label)

        self.threshold_slider = QSlider(Qt.Horizontal)
        self.threshold_slider.setMinimum(0)
        self.threshold_slider.setMaximum(100)
        self.threshold_slider.setValue(50)
        self.threshold_slider.setTickPosition(QSlider.TicksBelow)
        self.threshold_slider.setTickInterval(10)
        self.threshold_slider.valueChanged.connect(self.update_threshold_label)
        result_panel_layout.addWidget(self.threshold_slider)

        self.result_label = QLabel("识别结果：未检测")
        self.result_label.setAlignment(Qt.AlignCenter)
        result_panel_layout.addWidget(self.result_label)

        self.confidence_label = QLabel("置信度：0.25")
        self.confidence_label.setAlignment(Qt.AlignCenter)
        result_panel_layout.addWidget(self.confidence_label)

        self.iou_label = QLabel("IOU：0.40")
        self.iou_label.setAlignment(Qt.AlignCenter)
        result_panel_layout.addWidget(self.iou_label)

        # 新增品种描述和饲养建议标签
        self.description_label = QLabel("品种描述：")
        self.description_label.setAlignment(Qt.AlignLeft)
        result_panel_layout.addWidget(self.description_label)

        self.care_label = QLabel("饲养建议：")
        self.care_label.setAlignment(Qt.AlignLeft)
        result_panel_layout.addWidget(self.care_label)

        content_layout.addLayout(result_panel_layout)
        main_layout.addLayout(content_layout)

        self.bottom_btn = QPushButton("历史检测清理重置")
        self.bottom_btn.clicked.connect(self.clear_history)
        self.bottom_btn.setEnabled(True)
        main_layout.addWidget(self.bottom_btn)

        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        self.current_image_path = None

    def upload_image(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择图片", "", "图片文件 (*.jpg *.jpeg *.png)"
        )
        if file_path:
            self.current_image_path = file_path
            pixmap = QPixmap(file_path)
            self.image_label.setPixmap(
                pixmap.scaled(500, 400, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            )
            self.detect_btn.setEnabled(True)
            self.clear_btn.setEnabled(True)
            self.result_label.setText("识别结果：等待检测")
            self.confidence_label.setText("置信度：0.25")
            self.iou_label.setText("IOU：0.40")
            self.description_label.setText("品种描述：")
            self.care_label.setText("饲养建议：")

    def detect_breed(self):
        if self.current_image_path:
            threshold = self.threshold_slider.value() / 100
            breed, confidence, description, care = predict_dog_breed(self.current_image_path, threshold)
            self.result_label.setText(f"识别结果：{breed}")
            self.confidence_label.setText(f"置信度：{confidence:.2%}")
            self.iou_label.setText(f"IOU：{confidence:.2f}")
            if breed != "未知":
                save_to_database(self.current_image_path, breed, confidence)
                QMessageBox.information(
                    self, "识别完成",
                    f"已识别为：{breed}\n置信度：{confidence:.2%}\n数据已存储到数据库！\n\n"
                    f"品种描述：{description}\n饲养建议：{care}"
                )
                self.description_label.setText(f"品种描述：{description}")
                self.care_label.setText(f"饲养建议：{care}")
            else:
                QMessageBox.warning(
                    self, "识别失败",
                    f"置信度低于阈值 {threshold:.2f}，无法识别品种！"
                )
                self.description_label.setText("品种描述：暂无描述")
                self.care_label.setText("饲养建议：暂无建议")

    def clear_image(self):
        self.image_label.setPixmap(QPixmap())
        self.image_label.setText("请上传图片")
        self.current_image_path = None
        self.detect_btn.setEnabled(False)
        self.clear_btn.setEnabled(False)
        self.result_label.setText("识别结果：未检测")
        self.confidence_label.setText("置信度：0.25")
        self.iou_label.setText("IOU：0.40")
        self.description_label.setText("品种描述：")
        self.care_label.setText("饲养建议：")

    def show_last_result(self):
        records = get_history_records()
        if records:
            record = records[0]
            image_path = record['image_path']
            if os.path.exists(image_path):
                self.current_image_path = image_path
                pixmap = QPixmap(image_path)
                self.image_label.setPixmap(
                    pixmap.scaled(500, 400, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                )
                self.result_label.setText(f"识别结果：{record['breed']}")
                self.confidence_label.setText(f"置信度：{record['confidence']:.2%}")
                self.iou_label.setText("IOU：未提供")
                self.detect_btn.setEnabled(True)
                self.clear_btn.setEnabled(True)
                breed = record['breed']
                description = dog_info.get(breed, {}).get("description", "暂无描述")
                care = dog_info.get(breed, {}).get("care", "暂无建议")
                self.description_label.setText(f"品种描述：{description}")
                self.care_label.setText(f"饲养建议：{care}")
            else:
                QMessageBox.warning(self, "错误", "最近一次检测的图片不存在！")
        else:
            QMessageBox.information(self, "提示", "暂无历史检测记录！")

    def show_history(self):
        try:
            history_window = HistoryWindow(self)
            history_window.exec_()
        except NameError:
            QMessageBox.warning(self, "错误", "未能找到 HistoryWindow，请检查 dogs_windows 模块。")

    def clear_history(self):
        reply = QMessageBox.question(
            self, "确认", "确定要删除所有历史检测记录和图片吗？",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            conn = get_db_connection()
            if conn is None:
                return
            cursor = conn.cursor()
            try:
                cursor.execute('DELETE FROM dog_recognition')
                conn.commit()
                target_dir = 'detected_dogs'
                if os.path.exists(target_dir):
                    shutil.rmtree(target_dir)
                os.makedirs(target_dir, exist_ok=True)
                QMessageBox.information(self, "成功", "历史记录已清空！")
            except pymysql.Error as e:
                conn.rollback()
                QMessageBox.critical(self, "错误", f"清空历史记录失败：{e}")
            finally:
                cursor.close()
                conn.close()

    def update_threshold_label(self):
        threshold = self.threshold_slider.value() / 100
        self.threshold_label.setText(f"置信度阈值：{threshold:.2f}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DogBreedDetectorApp()
    window.show()
    sys.exit(app.exec_())
