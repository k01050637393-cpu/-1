import os
import random
import datetime
import urllib.request
from moviepy.editor import AudioFileClip, ImageClip
import youtube_manager

print("🤖 [레오 에이전트: 새벽 3시 일일 오토봇 가동]")

# 1. 고품질 감동/치유 BGM 데이터베이스 (저작권 무료)
MUSIC_SOURCE_LIST = [
    "https://incompetech.com/music/royalty-free/mp3-royaltyfree/Heartbreaking.mp3",
    "https://incompetech.com/music/royalty-free/mp3-royaltyfree/Despair%20and%20Triumph.mp3",
    "https://incompetech.com/music/royalty-free/mp3-royaltyfree/Agnus%20Dei%20X.mp3",
    "https://incompetech.com/music/royalty-free/mp3-royaltyfree/Prelude%20and%20Action.mp3",
    "https://incompetech.com/music/royalty-free/mp3-royaltyfree/Windswept.mp3"
]

# 제목 생성 (미국 유튜브 100 대장 분석: [목적성 괄호] + [파이프 |] + [따옴표 강조])
TITLE_TEMPLATES = [
    "[눈물 주의] 10년을 기다린 끝에 찾아온 기적 | 의사가 내민 \"한 장의 편지\"",
    "[감동 실화] 시한부 판정 후 남겨진 남편 | 딸아이가 매일 밤 읽은 \"그 일기장\"",
    "(반전 사연) 쓰레기통에서 발견한 낡은 반지 | 잃어버린 어머니의 \"마지막 편지\"",
    "[100% 실화] 휠체어를 탄 신부의 입장 | 하객들을 오열하게 만든 \"한 마디\"",
    "[위로가 필요할 때] 지친 하루 끝에 만난 뜻밖의 위로 | 혼자가 아니라는 \"따뜻한 증거\""
]

TAGS_LIST = ["감동", "눈물", "사연", "기적", "휴식", "위로", "가족", "실화"]

# 오늘 3시라서, 오늘 오후 시간대 3곳 설정 (한국시간 오후 6시, 7시, 8시는 퇴근 후 가장 시청률이 높은 골든타임)
# 유튜브 API는 UTC 기준 시간을 요구하므로 KST(UTC+9)에서 9시간을 빼줍니다.
now = datetime.datetime.now()
schedule_hours_kst = [18, 19, 20] # 오후 6시, 7시, 8시 예약

# 배경 이미지
img_path = "lily_bg.png" if os.path.exists("lily_bg.png") else "youngja.png"

try:
    youtube = youtube_manager.get_authenticated_service()

    for i in range(3):
        print(f"\n▶️ [작업 {i+1}/3] {schedule_hours_kst[i]}시 예약 영상 제작 시작")
        
        # 1. 무작위 음악 선택 및 다운로드
        music_url = random.choice(MUSIC_SOURCE_LIST)
        bgm_path = f"temp_music_{i}.mp3"
        urllib.request.urlretrieve(music_url, bgm_path)
        
        # 2. 30초 길이의 영상 자동 생성 (무작위 구간 자르기)
        audio = AudioFileClip(bgm_path)
        # 음악의 중간 어디쯤에서 30초 추출 (단, 음악의 총 길이를 초과하지 않도록)
        max_start = max(0, int(audio.duration) - 30)
        start_time = random.randint(0, max_start)
        audio_clip = audio.subclip(start_time, start_time + 30)
        
        video = ImageClip(img_path).set_duration(30)
        video = video.set_audio(audio_clip)
        
        output_file = f"Auto_Upload_{i}.mp4"
        video.write_videofile(output_file, fps=10, codec="libx264", audio_codec="aac", logger=None)
        audio.close()
        video.close()
        os.remove(bgm_path) # 사용한 mp3 치우기
        
        # 3. 예약 시간 산출 (UTC 변환: 오후 x시 - 9시간 = UTC)
        # 반드시 'isoformat' 규격 끝에 Z(UTC)를 붙여야 함 (예: 2026-03-19T09:00:00.0Z)
        target_time_utc = now.replace(hour=schedule_hours_kst[i]-9, minute=0, second=0, microsecond=0)
        publish_at_str = target_time_utc.strftime("%Y-%m-%dT%H:%M:%S.0Z")
        
        title = random.choice(TITLE_TEMPLATES)
        description = f"현대인의 지친 마음을 달래주는 감동 스토리와 음악입니다.\n(BGM 제공: Incompetech - Kevin MacLeod 힐링 음악)\n#감동 #사연 #위로 #휴식"
        selected_tags = random.sample(TAGS_LIST, 5)

        print(f"   => 제목 세팅: {title}")
        print(f"   => 예약(예약 게시) 시간: {target_time_utc} UTC (한국 오후 {schedule_hours_kst[i]}시)")
        
        # 4. 예약 업로드 기능 구현 (유튜브 API)
        body = {
            'snippet': {
                'title': title,
                'description': description,
                'tags': selected_tags,
                'categoryId': "22"
            },
            'status': {
                'privacyStatus': 'private', # 반드시 private로 등록된 후 예약 시간이 되면 public으로 자동 전환
                'publishAt': publish_at_str
            }
        }

        from googleapiclient.http import MediaFileUpload
        insert_request = youtube.videos().insert(
            part=",".join(body.keys()),
            body=body,
            media_body=MediaFileUpload(output_file, chunksize=-1, resumable=True)
        )
        
        response = insert_request.execute()
        print(f"✅ {i+1}번째 영상 업로드 & 예약 대성공! (영상 ID: {response['id']})")
        
    print("\n🎉 모든 자동화 작업이 끝났습니다! 에이전트는 다시 잠에 듭니다...")

except Exception as e:
    print(f"❌ 작업 중 오류 발생: {e}")
