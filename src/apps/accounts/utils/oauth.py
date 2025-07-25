import requests
from django.conf import settings


class KakaoOAuth:
    @staticmethod
    def get_user_info(auth_code):
        """카카오 OAuth로 사용자 정보 가져오기 (이메일 권한 없음 대응)"""
        # 1. 액세스 토큰 받기
        token_url = "https://kauth.kakao.com/oauth/token"
        token_data = {
            'grant_type': 'authorization_code',
            'client_id': settings.KAKAO_CLIENT_ID,
            'code': auth_code,
            'redirect_uri': 'http://localhost:8000/api/auth/kakao/callback',
        }

        # Client Secret이 있으면 추가
        if settings.KAKAO_CLIENT_SECRET:
            token_data['client_secret'] = settings.KAKAO_CLIENT_SECRET

        token_response = requests.post(token_url, data=token_data)
        token_json = token_response.json()

        if 'access_token' not in token_json:
            raise Exception(f"카카오 액세스 토큰 요청 실패: {token_json}")

        # 2. 사용자 정보 받기
        user_url = "https://kapi.kakao.com/v2/user/me"
        headers = {'Authorization': f"Bearer {token_json['access_token']}"}

        user_response = requests.get(user_url, headers=headers)
        user_json = user_response.json()

        # 3. 이메일 처리 (권한 없으면 임시 이메일 생성)
        try:
            # 이메일 권한이 있으면 실제 이메일 사용
            email = user_json['kakao_account']['email']
        except KeyError:
            # 이메일 권한이 없으면 임시 이메일 생성
            email = f"kakao_{user_json['id']}@temp.com"

        return {
            'social_id': str(user_json['id']),
            'email': email,  # 실제 이메일 또는 임시 이메일
            'name': user_json['kakao_account']['profile']['nickname'],
            'provider': 'kakao'
        }


class GoogleOAuth:
    @staticmethod
    def get_user_info(auth_code):
        """구글 OAuth로 사용자 정보 가져오기 (이메일 권한 있음)"""
        # 1. 액세스 토큰 받기
        token_url = "https://oauth2.googleapis.com/token"
        token_data = {
            'grant_type': 'authorization_code',
            'client_id': settings.GOOGLE_CLIENT_ID,
            'client_secret': settings.GOOGLE_CLIENT_SECRET,
            'code': auth_code,
            'redirect_uri': 'http://localhost:8000/api/auth/google/callback',
        }

        token_response = requests.post(token_url, data=token_data)
        token_json = token_response.json()

        if 'access_token' not in token_json:
            raise Exception(f"구글 액세스 토큰 요청 실패: {token_json}")

        # 2. 사용자 정보 받기
        user_url = "https://www.googleapis.com/oauth2/v2/userinfo"
        headers = {'Authorization': f"Bearer {token_json['access_token']}"}

        user_response = requests.get(user_url, headers=headers)
        user_json = user_response.json()

        return {
            'social_id': user_json['id'],
            'email': user_json['email'],  # 구글은 항상 실제 이메일
            'name': user_json['name'],
            'provider': 'google'
        }