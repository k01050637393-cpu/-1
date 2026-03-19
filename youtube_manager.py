
import os
import pickle
import google.auth
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# 전용 마스터 키(기기 인증용) 파일 이름
CLIENT_SECRETS_FILE = "client_secrets.json"
SCOPES = ['https://www.googleapis.com/auth/youtube.force-ssl']
API_SERVICE_NAME = "youtube"
API_VERSION = "v3"

def get_authenticated_service():
    """유튜브 API 인증 및 서비스 객체 반환"""
    credentials = None
    # 이전에 저장된 토큰이 있는지 확인
    if os.path.exists("token.pickle"):
        with open("token.pickle", "rb") as token:
            credentials = pickle.load(token)
            
    # 유효한 인증 정보가 없으면 새로 로그인
    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
        else:
            if not os.path.exists(CLIENT_SECRETS_FILE):
                raise FileNotFoundError(f"'{CLIENT_SECRETS_FILE}' 파일이 없습니다. GCP에서 발급받아 현재 폴더에 넣어주세요!")
            
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS_FILE, SCOPES)
            credentials = flow.run_local_server(port=0)
            
        # 인증 정보 저장
        with open("token.pickle", "wb") as token:
            pickle.dump(credentials, token)
            
    return build(API_SERVICE_NAME, API_VERSION, credentials=credentials)

def upload_video(youtube, file_path, title, description, category="22", tags=None):
    """영상 자동 업로드 기능"""
    body = {
        'snippet': {
            'title': title,
            'description': description,
            'tags': tags,
            'categoryId': category
        },
        'status': {
            'privacyStatus': 'public' # 또는 'unlisted', 'private'
        }
    }

    insert_request = youtube.videos().insert(
        part=",".join(body.keys()),
        body=body,
        media_body=MediaFileUpload(file_path, chunksize=-1, resumable=True)
    )

    print(f"🚀 '{title}' 업로드를 시작합니다...")
    response = insert_request.execute()
    print(f"✅ 업로드 완료! 영상 ID: {response['id']}")
    return response

def manage_comments(youtube, video_id):
    """최신 댓글 확인 및 AI 스타일 자동 답장 (예시)"""
    results = youtube.commentThreads().list(
        part="snippet",
        videoId=video_id,
        textFormat="plainText"
    ).execute()

    for item in results.get("items", []):
        comment = item["snippet"]["topLevelComment"]["snippet"]["textDisplay"]
        user = item["snippet"]["topLevelComment"]["snippet"]["authorDisplayName"]
        print(f"💬 [{user}]: {comment}")
        # 여기에 에이전트(레오/영자)의 로직을 연결하여 답장을 생성할 수 있습니다.

if __name__ == "__main__":
    print("--- Connect AI LAB 유튜브 관리 엔진 작동 ---")
    try:
        youtube = get_authenticated_service()
        print("✅ 루나 에이전트가 유튜브 시스템에 성공적으로 접속했습니다!")
        
        # 내 채널 정보 가져오기
        request = youtube.channels().list(
            part="snippet,statistics",
            mine=True
        )
        response = request.execute()
        
        if response['items']:
            channel_title = response['items'][0]['snippet']['title']
            print(f"📺 연결된 채널: {channel_title}")
            print(f"📈 총 구독자 수: {response['items'][0]['statistics']['subscriberCount']}명")
        
        print("\n--- 🎬 영상 업로드 테스트 모드 ---")
        print("업로드할 영상 파일의 전체 경로를 입력해주세요.")
        print("(예: C:\\Users\\PC\\Downloads\\test.mp4)")
        
        file_path = input("👉 파일 경로: ").strip().replace('"', '')
        
        if os.path.exists(file_path):
            title = "루나 에이전트 첫 업로드 테스트! 🚀"
            description = "AI 에이전트 루나가 자동으로 업로드한 영상입니다.\n#AI #유튜브자동화 #루나에이전트"
            tags = ["AI", "유튜브자동화", "루나"]
            
            # 실제 업로드 실행
            upload_video(youtube, file_path, title, description, tags=tags)
        else:
            if file_path:
                print(f"❌ '{file_path}' 파일을 찾을 수 없습니다. 경로를 다시 확인해주세요!")
            else:
                print("💡 테스트를 종료합니다. 준비가 되면 파일 경로를 알려주세요!")
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
