from moviepy.editor import *
import urllib.request
import os

print("🎵 유튜브 대박 예감! [감동 사연 배경음악]을 다운로드합니다...")
bgm_url = "https://incompetech.com/music/royalty-free/mp3-royaltyfree/Heartbreaking.mp3"
bgm_path = "heartbreaking_bgm.mp3"

if not os.path.exists(bgm_path):
    urllib.request.urlretrieve(bgm_url, bgm_path)
    print("✅ 성공적으로 감동 배경음악을 불러왔습니다!")

print("🎬 이미지와 음악을 합쳐서 [유튜브용 사연 영상]을 알아서 만들고 있습니다... (약 1~2분 소요)")
try:
    # 릴리의 배경 이미지 로드 (없으면 youngja.png 사용)
    img_path = "lily_bg.png"
    if not os.path.exists(img_path):
        img_path = "youngja.png"
        
    # 오디오 로드 및 길이 자르기 (유튜브에 올리기 좋게 앞 1분만)
    audio = AudioFileClip(bgm_path).subclip(0, 60)
    
    # 이미지를 오디오 길이에 맞춤
    video = ImageClip(img_path).set_duration(audio.duration)
    video = video.set_audio(audio)
    
    # 최종 영상 출력 (초당 24프레임)
    final_output = "Final_Story_Video.mp4"
    video.write_videofile(final_output, fps=24, codec="libx264", audio_codec="aac")
    
    print("\n🎉 모든 작업이 끝났습니다!")
    print(f"👉 방금 만들어진 영상 경로: {os.path.abspath(final_output)}")
    print("터미널에서 youtube_manager.py를 켜고 위 경로를 붙여넣어 바로 업로드하세요!")
    
except Exception as e:
    print(f"❌ 오류 발생: {e}")
