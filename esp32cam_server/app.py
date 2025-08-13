from flask import Flask, request, send_file, render_template_string
import os

app = Flask(__name__)
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# 保存每个摄像头的最新图片路径
latest_files = {}

HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8" />
    <title>ESP32-CAM 多摄像头实时图片</title>
    <style>
        body {
            text-align: center;           /* 整体居中 */
            font-family: Arial, sans-serif;
        }
        .cam-container {
            display: inline-block;        /* 让每台摄像头单独容器 */
            margin: 20px;
            border: 3px solid #333;      /* 边框 */
            padding: 10px;                /* 内边距，让图片不贴边 */
            box-shadow: 2px 2px 8px rgba(0,0,0,0.3); /* 阴影，可选 */
        }
        img {
            max-width: 100%;              /* 自适应容器宽度 */
            height: auto;
            display: block;
            margin: 0 auto;               /* 图片水平居中 */
        }
        h2 {
            margin: 10px 0;
        }
    </style>
</head>
<body>
    <h1>ESP32-CAM 多摄像头实时图片</h1>

    {% for cam_id in cam_ids %}
    <div class="cam-container">
        <h2>摄像头 {{ cam_id }}</h2>
        <img id="img_{{ cam_id }}" src="/latest/{{ cam_id }}" />
    </div>
    {% endfor %}

    <script>
        const camIds = {{ cam_ids|tojson }};
        setInterval(() => {
            camIds.forEach(cam_id => {
                const img = document.getElementById("img_" + cam_id);
                if (img) {
                    img.src = "/latest/" + cam_id + "?ts=" + Date.now();
                }
            });
        }, 500);
    </script>
</body>
</html>

"""

@app.route("/")
def index():
    cam_ids = list(latest_files.keys())
    return render_template_string(HTML_PAGE, cam_ids=cam_ids)

@app.route("/upload/<cam_id>", methods=["POST"])
def upload(cam_id):
    global latest_files
    if request.data:
        cam_folder = os.path.join(UPLOAD_FOLDER, cam_id)
        os.makedirs(cam_folder, exist_ok=True)
        tmp_path = os.path.join(cam_folder, "temp.jpg")
        final_path = os.path.join(cam_folder, "latest.jpg")
        with open(tmp_path, "wb") as f:
            f.write(request.data)
        os.replace(tmp_path, final_path)
        latest_files[cam_id] = final_path
        print(f"摄像头 {cam_id} 图片保存成功: {final_path}, 大小: {os.path.getsize(final_path)} bytes")
        return "OK", 200
    else:
        return "No image uploaded", 400

@app.route("/latest/<cam_id>")
def latest(cam_id):
    global latest_files
    path = latest_files.get(cam_id)
    if path and os.path.exists(path):
        return send_file(path, mimetype="image/jpeg")
    else:
        return "No image", 404

if __name__ == "__main__":
    print("Flask服务器启动，监听0.0.0.0:5000")
    app.run(host="0.0.0.0", port=5000)
