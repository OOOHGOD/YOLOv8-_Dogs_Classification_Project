"""将数据集从PASCAL VOC XML格式转换为YOLO格式（调试版）"""

import xml.etree.ElementTree as ET
from pathlib import Path

def convert_bbox_to_yolo(
    size: tuple[int, int], box: tuple[float, float, float, float]
) -> tuple[float, float, float, float]:
    """（函数内容保持不变）"""
    # ... 原有代码不变 ...

def xml_to_txt(input_file: Path, output_txt: Path, classes: list[str]) -> int:
    """返回成功转换的对象数量"""
    try:
        tree = ET.parse(input_file)
        root = tree.getroot()
    except ET.ParseError as e:
        print(f"❌ 解析失败 {input_file}: {str(e)}")
        return 0
    except FileNotFoundError:
        print(f"❌ 文件不存在 {input_file}")
        return 0

    # 尺寸校验（添加详细错误信息）
    size_element = root.find("size")
    if not size_element:
        print(f"⚠️  {input_file.name} 缺少 <size> 节点")
        return 0

    try:
        image_width = int(size_element.findtext("width", "0"))
        image_height = int(size_element.findtext("height", "0"))
        if image_width <= 0 or image_height <= 0:
            print(f"⚠️  {input_file.name} 无效尺寸: {image_width}x{image_height}")
            return 0
    except ValueError:
        print(f"⚠️  {input_file.name} 尺寸包含非数字内容")
        return 0

    valid_objects = 0
    with output_txt.open("w") as file:
        for obj_idx, obj in enumerate(root.iter("object"), 1):
            # 类名检查（显示具体错误）
            class_name = obj.findtext("name", "").strip()
            if not class_name:
                print(f"⚠️  {input_file.name} 第{obj_idx}个对象缺少类名")
                continue

            if class_name not in classes:
                print(f"🚫  {input_file.name} 第{obj_idx}个对象类名 '{class_name}' 不在classes列表")
                continue

            # 困难样本过滤
            is_difficult = int(obj.findtext("difficult", "0"))
            if is_difficult:
                print(f"⏭️  {input_file.name} 第{obj_idx}个对象标记为困难样本，已跳过")
                continue

            # 边界框解析（添加异常处理）
            try:
                xml_box = obj.find("bndbox")
                bbox = (
                    float(xml_box.findtext("xmin", "0")),
                    float(xml_box.findtext("ymin", "0")),
                    float(xml_box.findtext("xmax", "0")),
                    float(xml_box.findtext("ymax", "0")),
                )
                # 坐标校验
                if not (0 <= bbox[0] <= bbox[2] <= image_width):
                    raise ValueError(f"x坐标越界: {bbox}")
                if not (0 <= bbox[1] <= bbox[3] <= image_height):
                    raise ValueError(f"y坐标越界: {bbox}")
            except Exception as e:
                print(f"⚠️  {input_file.name} 第{obj_idx}个对象边框错误: {str(e)}")
                continue

            yolo_bbox = convert_bbox_to_yolo((image_width, image_height), bbox)
            file.write(f"{classes.index(class_name)} {' '.join(f'{x:.6f}' for x in yolo_bbox)}\n")
            valid_objects += 1

    return valid_objects

def main(input_dir: Path, output_dir: Path, classes_file: Path) -> None:
    """添加详细的运行日志"""
    print("🔍 启动转换器".center(50, "="))
    print(f"📁 输入目录: {input_dir.resolve()}")
    print(f"📂 输出目录: {output_dir.resolve()}")
    print(f"🏷️  类别文件: {classes_file.resolve()}")

    # 类别文件校验
    try:
        classes = classes_file.read_text(encoding="utf-8").splitlines()
        classes = [c.strip() for c in classes if c.strip()]
        print(f"✅ 加载 {len(classes)} 个类别: {', '.join(classes)}")
    except FileNotFoundError:
        print(f"❌ 错误: 类别文件 {classes_file} 不存在")
        return
    except Exception as e:
        print(f"❌ 读取类别文件失败: {str(e)}")
        return

    # 输入目录校验
    xml_files = list(input_dir.glob("*.xml"))
    if not xml_files:
        print(f"❌ 错误: 输入目录中没有找到XML文件")
        return
    print(f"📄 发现 {len(xml_files)} 个XML文件")

    # 准备输出目录
    try:
        output_dir.mkdir(parents=True, exist_ok=True)
        print(f"📂 已创建输出目录")
    except PermissionError:
        print(f"❌ 错误: 无权限创建输出目录 {output_dir}")
        return

    # 处理文件
    total_objects = 0
    for xml_file in xml_files:
        print(f"\n🔧 正在处理 {xml_file.name}".ljust(50, "-"))
        txt_file = output_dir / f"{xml_file.stem}.txt"

        count = xml_to_txt(xml_file, txt_file, classes)
        if count > 0:
            print(f"✅ 转换成功，写入 {count} 个对象到 {txt_file.name}")
            total_objects += count
        else:
            print(f"⚠️  未找到有效对象，创建空文件")
            txt_file.touch()

    # 最终报告
    print("\n" + "转换完成".center(50, "="))
    print(f"• 处理文件: {len(xml_files)} 个")
    print(f"• 有效对象: {total_objects} 个")
    print(f"• 输出目录: {output_dir.resolve()}")

if __name__ == "__main__":
    # 配置路径（请在此处确认实际路径）
    input_dir = Path("./VOC_Dataset")
    output_dir = Path("./YOLO_Dataset")
    classes_file = Path("./classes.txt")

    # 添加路径预检查
    print("[路径预检查]".center(50, "-"))
    print(f"输入目录存在: {input_dir.exists()}",
          f"（内容示例: {list(input_dir.glob('*'))[:3]}...）" if input_dir.exists() else "")
    print(f"类别文件存在: {classes_file.exists()}")

    main(input_dir, output_dir, classes_file)