from yt_dlp import YoutubeDL
import sys

def download_video(url, quality="best"):
    options = {
        'outtmpl': '%(title)s.%(ext)s',      # ফাইলের নাম
        'format': quality,                   # best, 720p, 1080p ইত্যাদি
        'noplaylist': True,                  # প্লেলিস্ট না নামানোর জন্য
        'quiet': False,
    }
    
    try:
        with YoutubeDL(options) as ydl:
            print("✅ ডাউনলোড শুরু হচ্ছে...")
            ydl.download([url])
            print("🎉 ডাউনলোড সম্পন্ন!")
    except Exception as e:
        print(f"❌ এরর হয়েছে: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        url = input("ভিডিওর লিংক দাও: ")
    else:
        url = sys.argv[1]
    
    print("কোন কোয়ালিটি চাও?")
    print("1. সেরা কোয়ালিটি (best)")
    print("2. 1080p")
    print("3. 720p")
    print("4. শুধু অডিও")
    
    choice = input("নম্বর লিখো (1-4): ").strip()
    
    quality_map = {
        "1": "best",
        "2": "bestvideo[height<=1080]+bestaudio",
        "3": "bestvideo[height<=720]+bestaudio",
        "4": "bestaudio"
    }
    
    selected = quality_map.get(choice, "best")
    download_video(url, selected)
