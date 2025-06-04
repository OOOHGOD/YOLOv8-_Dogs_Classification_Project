import os
import requests

# 目标目录
target_dir = './pre_trained_model'

# 创建目标目录（如果不存在）
os.makedirs(target_dir, exist_ok=True)

# 模型URL和文件名
models = {
    'yolov8n': 'https://github.com/ultralytics/assets/releases/download/v0.0.0/yolov8n.pt',
    'yolov7-tiny': 'https://github.com/WongKinYiu/yolov7/releases/download/v0.1/yolov7-tiny.pt',
    'yolov5s': 'https://github.com/ultralytics/yolov5/releases/download/v6.2/yolov5s.pt'
}

# 下载模型
for model_name, url in models.items():
    file_path = os.path.join(target_dir, f'{model_name}.pt')
    print(f'Downloading {model_name} to {file_path}...')
    
    try:
        response = requests.get(url, stream=True)
        if response.status_code == 200:
            with open(file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            print(f'Successfully downloaded {model_name}')
        else:
            print(f'Failed to download {model_name}')
    except Exception as e:
        print(f'Error downloading {model_name}: {str(e)}')

print('All models downloaded successfully.')