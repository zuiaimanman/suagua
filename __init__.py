import os
import random

import requests
from nonebot import on_command
from nonebot.params import CommandArg
from nonebot.plugin import PluginMetadata
from nonebot.adapters.onebot.v11 import Bot, Event, Message, MessageSegment

from zhenxun.services.log import logger
from zhenxun.configs.utils import PluginExtraData

# from zhenxun.configs.path_config import IMAGE_PATH

__plugin_meta__ = PluginMetadata(
    name="算卦",
    description="算卦不算命，求己胜求人",
    usage="""
    指令：
        算卦  起卦
    """.strip(),
    extra=PluginExtraData(
        author="蔡徐坤",
        version="0.1",
        menu_type="群内小游戏",
    ).dict(),
)
# yong字典来存储每个用户的卦象图片编号
user_gua_numbers = {}
# liao链接
url = "https://gitee.com/shiranranran/suagua/raw/master/suagua/images/{rand}.jpg"
url_2 = "https://github.com/zuiaimanman/suagua/raw/main/suagua/images/{rand}.jpg"

suangua = on_command("算卦", aliases={"起卦", "推算"}, priority=5, block=True)


@suangua.handle()
async def handle_suangua(bot: Bot, event: Event, arg: Message = CommandArg()):
    user_id = event.get_user_id()
    rand = user_gua_numbers.get(user_id, random.randint(0, 64))
    user_gua_numbers[user_id] = rand

    image_url = url.format(rand=rand)
    logger.info(f"算卦：第{rand}卦，图片链接：{image_url}")

    response = requests.get(image_url)
    if response.status_code == 200:
        msg_image = MessageSegment.image(response.content)
        await suangua.finish(msg_image, at_sender=True)
    else:
        logger.warning(f"第一个链接下载图片s失败，状态码：{response.status_code}")
        image_url_2 = url_2.format(rand=rand)
        logger.info(f"尝试第二个链接：{image_url_2}")
        response_2 = requests.get(image_url_2)
        if response_2.status_code == 200:
            msg_image = MessageSegment.image(response_2.content)
            await suangua.finish(msg_image, at_sender=True)
        else:
            await suangua.finish(
                f"哦豁，两个链接都无法下载图片，状态码：{response_2.status_code}",
                at_sender=True,
            )


# 每天凌晨清空字典以重置所有用户的卦象图片编号
def reset_gua_numbers():
    global user_gua_numbers
    user_gua_numbers = {}
