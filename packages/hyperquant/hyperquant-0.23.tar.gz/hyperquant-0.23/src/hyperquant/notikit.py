"""
通知类的功能简单封装，非必要别修改 :)
只要知道怎么使用以下函数：
- send_wecom_msg
- send_wecom_img

Binance期现套利 | 邢不行 | 2024分享会
author: 邢不行
微信: xbx6660
"""
import base64
import hashlib
import os.path
import requests
import json
import traceback
from datetime import datetime

from hyperquant.logkit import get_logger
logger = get_logger('notikit', './data/logs/notikit.log', show_time=True)



proxy = {}


def handle_exception(e: Exception, msg: str = '') -> None:
    logger.error(f"{msg}:{e}")
    logger.error(e)
    logger.error(traceback.format_exc())


# 企业微信通知
def send_wecom_msg(content, webhook_url):
    if not webhook_url:
        logger.warning('未配置wecom_webhook_url，不发送信息')
        return
    if not content:
        logger.warning('未配置content，不发送信息')
        return
    try:
        data = {
            "msgtype": "text",
            "text": {
                "content": content + '\n' + datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        }
        r = requests.post(webhook_url, data=json.dumps(data), timeout=10, proxies=proxy)
        logger.info(f'调用企业微信接口返回： {r.text}')
        logger.ok('成功发送企业微信')
    except Exception as e:
        handle_exception(e, '发送企业微信失败')


# 上传图片，解析bytes
class MyEncoder(json.JSONEncoder):
    def default(self, obj):
        """
        只要检查到了是bytes类型的数据就把它转为str类型
        :param obj:
        :return:
        """
        if isinstance(obj, bytes):
            return str(obj, encoding='utf-8')
        return json.JSONEncoder.default(self, obj)


# 企业微信发送图片
def send_wecom_img(file_path, webhook_url):
    """
    企业微信发送图片
    :param file_path: 图片地址
    :param webhook_url: 企业微信webhook网址
    :return:
    """
    if not os.path.exists(file_path):
        logger.warning('找不到图片')
        return
    if not webhook_url:
        logger.warning('未配置wecom_webhook_url，不发送信息')
        return
    try:
        with open(file_path, 'rb') as f:
            image_content = f.read()
        image_base64 = base64.b64encode(image_content).decode('utf-8')
        md5 = hashlib.md5()
        md5.update(image_content)
        image_md5 = md5.hexdigest()
        data = {
            'msgtype': 'image',
            'image': {
                'base64': image_base64,
                'md5': image_md5
            }
        }
        # 服务器上传bytes图片的时候，json.dumps解析会出错，需要自己手动去转一下
        r = requests.post(webhook_url, data=json.dumps(data, cls=MyEncoder, indent=4), timeout=10, proxies=proxy)
        logger.info(f'调用企业微信接口返回： {r.text}')
        logger.ok('成功发送企业微信图片')
    except Exception as e:
        handle_exception(e, '发送企业微信图片失败')
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)
