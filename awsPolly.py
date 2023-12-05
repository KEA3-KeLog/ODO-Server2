import boto3

# AWS 자격 증명 설정 (AWS CLI를 사용하면 설정할 필요가 없습니다.)
aws_access_key_id = 'AKIAUOFWKKMBKKU3ARMF'
aws_secret_access_key = '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'
region_name = 'ap-northeast-2'

# Polly 클라이언트 생성
polly_client = boto3.client('polly', aws_access_key_id=aws_access_key_id,
                            aws_secret_access_key=aws_secret_access_key,
                            region_name=region_name)

# 변환할 텍스트
input_text = "안녕하세요 아이유에용 kea 켈로그 많이 사랑해주시고요 오지구요"

# Polly에 음성 변환 요청0ㅔ0
response = polly_client.synthesize_speech(
    Text=input_text,
    OutputFormat='mp3',
    VoiceId='Seoyeon'  # 원하는 음성 유형 및 성별 선택
)

# MP3 파일로 저장
with open("output.mp3", 'wb') as file:
    file.write(response['AudioStream'].read())