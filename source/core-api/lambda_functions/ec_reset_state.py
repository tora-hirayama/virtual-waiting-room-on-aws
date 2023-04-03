import requests
import os
import json
import urllib3
import hashlib
import datetime
from aws_requests_auth.aws_auth import AWSRequestsAuth
from vwr.common.sanitize import deep_clean

http = urllib3.PoolManager()

# アクセスキー
access_key = os.environ["ACCESS_KEY"]
# シークレットキー
secret_key = os.environ["SECRET_KEY"]
# リージョン
region = 'ap-northeast-1'
# プライベートAPIのホスト名
private_api_hostname = os.environ["PRIVATE_API_HOSTNAME"]
# eventID
event_id = os.environ["EVENT_ID"]

def lambda_handler(event, context):
    
    # レスポンス作成
    response = {}
    headers = {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*'
    }
    
    # 現在日付を取得
    now = datetime.datetime.now()
    
    # 日付を文字列に変換
    date_string = now.strftime("%Y-%m-%d")
    
    # ハッシュを生成する文字列
    message = date_string + '濃いめ'
    
    # sha512ハッシュオブジェクトを作成
    hash_object = hashlib.sha512()
    
    # ハッシュオブジェクトに文字列を追加
    hash_object.update(message.encode())
    
    # ハッシュ値を16進数で取得
    hash_value = hash_object.hexdigest()
    
    # 結果を出力
    print("sha512ハッシュ値:", hash_value)
    
    body = json.loads(event['body'])
    code = deep_clean(body['code'])
    if(code is not None):

        # 認証コード確認
        if(hash_value == code):
            # リセットURL
            reset_url = "https://" + private_api_hostname + "/api/reset_initial_state"
            
            reset_data = {'event_id': event_id}
            
            reset_auth = AWSRequestsAuth(aws_access_key=access_key,
                        aws_secret_access_key=secret_key,
                        aws_host=private_api_hostname,
                        aws_region=region,
                        aws_service='execute-api')
                        
            reset_r = requests.post(reset_url, auth=reset_auth, data=json.dumps(reset_data))
            
            print(reset_r)
            
            response = {
                "statusCode": 200,
                "headers": headers,
                "body": json.dumps({})
            }
            
        else:
            response = {
                "statusCode": 403,
                "headers": headers,
                "body": json.dumps({ "message": "Authentication failured" })
            }
    else:
        response = {
            "statusCode": 400,
            "headers": headers,
            "body": json.dumps({"error": "Invalid code"}),
        }
        
    print(response)
    return response