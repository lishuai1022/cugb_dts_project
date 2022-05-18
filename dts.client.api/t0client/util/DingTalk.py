
'''
钉钉发送消息的异步类
'''
from ..config.config import *
import json
from tornado.httpclient import AsyncHTTPClient

class DingTalk(object):
    def res_callback(self,response):
        pass
        # print(response.body.decode())

    def send(self, token, text):
        try:
            url = 'https://oapi.dingtalk.com/robot/send?access_token=' + token
            values = {
                "msgtype": "text",
                "text": {
                    "content": '【' + MODE + '】' + text
                },
                "at": {
                    "isAtAll": True
                }
            }
            headers = {
                'User-Agent': 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)',
                'Content-type': 'application/json'
            }
            AsyncHTTPClient().fetch(
                url,
                method='POST',
                headers=headers,
                body=json.dumps(values, sort_keys=True).encode('utf-8'),
                callback=self.res_callback
            )
        except:
            print('发送钉钉失败')

if __name__ == '__main__':
    pass
