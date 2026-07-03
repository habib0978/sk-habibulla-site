from flask import Flask, request, jsonify, send_file
import yt_dlp
import os
import threading
import time

app = Flask(__name__)

# ডাউনলোড ফোল্ডার
DOWNLOAD_FOLDER = 'downloads'
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

def download_video_task(url, quality, task_id):
    try:
        quality_map = {
            'best': 'best',
            '1080': 'bestvideo[height<=1080]+bestaudio/best',
            '720': 'bestvideo[height<=720]+bestaudio/best',
            'audio': 'bestaudio/best'
        }
        
        ydl_opts = {
            'outtmpl': f'{DOWNLOAD_FOLDER}/{task_id}_%(title)s.%(ext)s',
            'format': quality_map.get(quality, 'best'),
            'noplaylist': True,
            'quiet': True,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            final_path = filename
        
        # ফাইলের নাম সেভ করে রাখি
        with open(f'{DOWNLOAD_FOLDER}/{task_id}_info.txt', 'w', encoding='utf-8') as f:
            f.write(final_path)
            
    except Exception as e:
        with open(f'{DOWNLOAD_FOLDER}/{task_id}_error.txt', 'w', encoding='utf-8') as f:
            f.write(str(e))

@app.route('/')
def home():
    return '''
<!DOCTYPE html>
<html lang="bn">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Social Video Downloader</title>
  <style>
    body {
      font-family: 'Segoe UI', sans-serif;
      background: linear-gradient(135deg, #667eea, #764ba2);
      margin: 0;
      padding: 20px;
      color: white;
      min-height: 100vh;
    }
    .container {
      max-width: 600px;
      margin: 40px auto;
      background: rgba(255,255,255,0.15);
      padding: 30px;
      border-radius: 15px;
      text-align: center;
      backdrop-filter: blur(10px);
    }
    h1 { margin: 0 0 10px 0; }
    input, select, button {
      width: 100%;
      padding: 15px;
      margin: 12px 0;
      border: none;
      border-radius: 8px;
      font-size: 16px;
    }
    input, select { background: white; color: black; }
    button {
      background: #ff0066;
      color: white;
      font-weight: bold;
      cursor: pointer;
    }
    button:hover { background: #cc0052; }
    #status { margin-top: 20px; min-height: 30px; font-weight: bold; }
  </style>
</head>
<body>
  <div class="container">
    <h1>📥 Social Media Video Downloader</h1>
    <p>যেকোনো লিংক থেকে ভিডিও ডাউনলোড করুন</p>
    
    <input type="text" id="url" placeholder="ভিডিওর লিংক পেস্ট করুন..." required>
    
    <select id="quality">
      <option value="best">সেরা কোয়ালিটি (Best)</option>
      <option value="1080">1080p</option>
      <option value="720">720p</option>
      <option value="audio">শুধু অডিও (MP3)</option>
    </select>
    
    <button onclick="startDownload()">ডাউনলোড শুরু করুন</button>
    
    <div id="status"></div>
  </div>

  <script>
    async function startDownload() {
      const url = document.getElementById('url').value.trim();
      const quality = document.getElementById('quality').value;
      const status = document.getElementById('status');

      if (!url) {
        status.innerHTML = '<span style="color:red">লিংক দিন!</span>';
        return;
      }

      status.innerHTML = '⏳ ভিডিও প্রসেসিং হচ্ছে... দয়া করে অপেক্ষা করুন';

      try {
        const res = await fetch('/download', {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify({url, quality})
        });
        
        const data = await res.json();
        
        if (data.success) {
          status.innerHTML = `✅ <a href="${data.download_url}" style="color:white" download>📥 ডাউনলোড শুরু হয়েছে! ক্লিক করুন</a>`;
        } else {
          status.innerHTML = `❌ ${data.error}`;
        }
      } catch (e) {
        status.innerHTML = '❌ সার্ভারে সমস্যা হয়েছে। আবার চেষ্টা করুন।';
      }
    }
  </script>
</body>
</html>
    '''

@app.route('/download', methods=['POST'])
def download():
    data = request.get_json()
    url = data.get('url')
    quality = data.get('quality', 'best')
    
    if not url:
        return jsonify({'success': False, 'error': 'URL দরকার'})
    
    task_id = str(int(time.time()))
    
    # ব্যাকগ্রাউন্ডে ডাউনলোড শুরু
    thread = threading.Thread(target=download_video_task, args=(url, quality, task_id))
    thread.daemon = True
    thread.start()
    
    # কিছুক্ষণ পর ফাইল চেক করার জন্য
    time.sleep(3)
    
    try:
        # ফাইল খুঁজে বের করা
        for file in os.listdir(DOWNLOAD_FOLDER):
            if file.startswith(task_id) and not file.endswith(('.txt')):
                return jsonify({
                    'success': True,
                    'download_url': f'/download_file/{file}'
                })
    except:
        pass
    
    return jsonify({
        'success': True,
        'download_url': f'/check_status/{task_id}'
    })

@app.route('/download_file/<filename>')
def download_file(filename):
    try:
        return send_file(os.path.join(DOWNLOAD_FOLDER, filename), as_attachment=True)
    except:
        return "File not found", 404

@app.route('/check_status/<task_id>')
def check_status(task_id):
    try:
        for file in os.listdir(DOWNLOAD_FOLDER):
            if file.startswith(task_id) and not file.endswith(('.txt')):
                return jsonify({'success': True, 'download_url': f'/download_file/{file}'})
    except:
        pass
    return jsonify({'success': False, 'error': 'এখনো প্রসেসিং চলছে... রিফ্রেশ করুন'})

if __name__ == '__main__':
    print("🌐 সার্ভার চালু হচ্ছে... ব্রাউজারে খুলুন: http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=False)
