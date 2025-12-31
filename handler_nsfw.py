import runpod
from runpod.serverless.utils import rp_upload
import os
import websocket
import base64
import json
import uuid
import logging
import urllib.request
import urllib.parse
import binascii
import time

# 日志配置
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

server_address = os.getenv('SERVER_ADDRESS', '127.0.0.1')
client_id = str(uuid.uuid4())

def save_data_if_base64(data_input, temp_dir, output_filename):
    """
    处理Base64编码或URL/路径输入
    """
    if not isinstance(data_input, str):
        return data_input

    try:
        decoded_data = base64.b64decode(data_input)
        os.makedirs(temp_dir, exist_ok=True)
        file_path = os.path.abspath(os.path.join(temp_dir, output_filename))
        with open(file_path, 'wb') as f:
            f.write(decoded_data)
        logger.info(f"✅ Base64 input saved to '{file_path}'")
        return file_path
    except (binascii.Error, ValueError):
        logger.info(f"➡️ Using '{data_input}' as file path")
        return data_input

def queue_prompt(prompt):
    url = f"http://{server_address}:8188/prompt"
    logger.info(f"Queueing prompt to: {url}")
    p = {"prompt": prompt, "client_id": client_id}
    data = json.dumps(p).encode('utf-8')
    req = urllib.request.Request(url, data=data)
    return json.loads(urllib.request.urlopen(req).read())

def get_history(prompt_id):
    url = f"http://{server_address}:8188/history/{prompt_id}"
    with urllib.request.urlopen(url) as response:
        return json.loads(response.read())

def get_videos(ws, prompt):
    prompt_id = queue_prompt(prompt)['prompt_id']
    output_videos = {}

    while True:
        out = ws.recv()
        if isinstance(out, str):
            message = json.loads(out)
            if message['type'] == 'executing':
                data = message['data']
                if data['node'] is None and data['prompt_id'] == prompt_id:
                    break
        else:
            continue

    history = get_history(prompt_id)[prompt_id]
    for node_id in history['outputs']:
        node_output = history['outputs'][node_id]
        videos_output = []
        if 'gifs' in node_output:
            for video in node_output['gifs']:
                with open(video['fullpath'], 'rb') as f:
                    video_data = base64.b64encode(f.read()).decode('utf-8')
                videos_output.append(video_data)
        output_videos[node_id] = videos_output

    return output_videos

def load_workflow(workflow_path):
    with open(workflow_path, 'r') as file:
        return json.load(file)

def handler(job):
    job_input = job.get("input", {})
    logger.info(f"Received job input: {job_input}")

    task_id = f"task_{uuid.uuid4()}"

    # 处理输入图像
    image_input = job_input.get("image_path", "/example_image.png")
    if image_input == "/example_image.png":
        image_path = "/example_image.png"
    else:
        image_path = save_data_if_base64(image_input, task_id, "input_image.jpg")

    # 加载NSFW工作流
    workflow_file = "/workflow_nsfw.json"
    prompt = load_workflow(workflow_file)

    # 从输入获取参数
    positive_prompt = job_input.get("prompt", "A person walking naturally")
    negative_prompt = job_input.get("negative_prompt",
        "色调艳丽，过曝，静态，细节模糊不清，字幕，风格，作品，画作，画面，静止，整体发灰，最差质量，低质量")
    seed = job_input.get("seed", 12345)
    width = job_input.get("width", 480)
    height = job_input.get("height", 640)
    length = job_input.get("length", 81)
    fps = job_input.get("fps", 16)
    steps = job_input.get("steps", 4)
    cfg = job_input.get("cfg", 1.0)

    # LoRA配置（可选）
    lora_high = job_input.get("lora_high", "DR34ML4Y_I2V_14B_HIGH.safetensors")
    lora_low = job_input.get("lora_low", "DR34ML4Y_I2V_14B_LOW.safetensors")
    lora_high_strength = job_input.get("lora_high_strength", 1.0)
    lora_low_strength = job_input.get("lora_low_strength", 1.0)

    # 设置工作流参数
    # 节点97: 加载图像
    prompt["97"]["inputs"]["image"] = image_path

    # 节点93: 正向提示词
    prompt["93"]["inputs"]["text"] = positive_prompt

    # 节点89: 负向提示词
    prompt["89"]["inputs"]["text"] = negative_prompt

    # 节点98: WanImageToVideo 主要参数
    prompt["98"]["inputs"]["width"] = width
    prompt["98"]["inputs"]["height"] = height
    prompt["98"]["inputs"]["length"] = length

    # 节点86: 第一个采样器的随机种子
    prompt["86"]["inputs"]["noise_seed"] = seed
    prompt["86"]["inputs"]["steps"] = steps
    prompt["86"]["inputs"]["cfg"] = cfg

    # 节点85: 第二个采样器
    prompt["85"]["inputs"]["steps"] = steps
    prompt["85"]["inputs"]["cfg"] = cfg

    # 节点94: 视频FPS
    prompt["94"]["inputs"]["fps"] = fps

    # 节点101, 102: LoRA配置
    prompt["101"]["inputs"]["lora_name"] = lora_high
    prompt["101"]["inputs"]["strength_model"] = lora_high_strength

    prompt["102"]["inputs"]["lora_name"] = lora_low
    prompt["102"]["inputs"]["strength_model"] = lora_low_strength

    logger.info(f"Using NSFW workflow with params: width={width}, height={height}, length={length}, seed={seed}")

    # 连接WebSocket
    ws_url = f"ws://{server_address}:8188/ws?clientId={client_id}"
    logger.info(f"Connecting to WebSocket: {ws_url}")

    # HTTP连接检查
    http_url = f"http://{server_address}:8188/"
    max_http_attempts = 180
    for http_attempt in range(max_http_attempts):
        try:
            response = urllib.request.urlopen(http_url, timeout=5)
            logger.info(f"HTTP connected (attempt {http_attempt+1})")
            break
        except Exception as e:
            logger.warning(f"HTTP connection failed (attempt {http_attempt+1}/{max_http_attempts}): {e}")
            if http_attempt == max_http_attempts - 1:
                raise Exception("Cannot connect to ComfyUI server")
            time.sleep(1)

    # WebSocket连接
    ws = websocket.WebSocket()
    max_attempts = int(180/5)
    for attempt in range(max_attempts):
        try:
            ws.connect(ws_url)
            logger.info(f"WebSocket connected (attempt {attempt+1})")
            break
        except Exception as e:
            logger.warning(f"WebSocket connection failed (attempt {attempt+1}/{max_attempts}): {e}")
            if attempt == max_attempts - 1:
                raise Exception("WebSocket connection timeout (3 minutes)")
            time.sleep(5)

    # 执行工作流
    videos = get_videos(ws, prompt)
    ws.close()

    # 返回视频
    for node_id in videos:
        if videos[node_id]:
            return {"video": videos[node_id][0]}

    return {"error": "Video not found"}

runpod.serverless.start({"handler": handler})
