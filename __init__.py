import os
import random

import requests
from nonebot import on_command
from nonebot.params import CommandArg
from nonebot.plugin import PluginMetadata
from nonebot.adapters.onebot.v11 import Bot, Event, Message, MessageSegment

from zhenxun.services.log import logger
from zhenxun.configs.utils import PluginExtraData
from zhenxun.configs.path_config import IMAGE_PATH

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


dir_path = IMAGE_PATH / "suagua"
gua_path = dir_path / "images"

# 创建一个字典来存储每个用户的卦象图片编号
user_gua_numbers = {}

# GitHub 图片链接模板
image_url_template = "https://github.com/your_repo/suagua/images/{rand}.jpg"

suangua = on_command("算卦", aliases={"起卦", "推算"}, priority=5, block=True)


@suangua.handle()
async def handle_suangua(bot: Bot, event: Event, arg: Message = CommandArg()):
    user_id = event.get_user_id()
    rand = user_gua_numbers.get(user_id, random.randint(0, 64))
    user_gua_numbers[user_id] = rand

    image_file = (gua_path / f"{rand}.jpg").resolve()
    logger.info(f"算卦：第{rand}卦，图片路径：{image_file}")

    if not image_file.exists():
        logger.info(f"图片文件不存在：{image_file}，尝试从链接下载")
        try:
            response = requests.get(image_url_template.format(rand=rand))
            if response.status_code == 200:
                with open(image_file, "wb") as f:
                    f.write(response.content)
                logger.info(f"成功下载图片：{image_file}")
            else:
                await suangua.finish(
                    f"无法下载图片，状态码：{response.status_code}", at_sender=True
                )
                return
        except Exception as e:
            logger.error(f"下载图片时发生错误：{e}")
            await suangua.finish(f"下载图片时发生错误：{e}", at_sender=True)
            return

    msg_image = MessageSegment.image(str(image_file))
    await suangua.finish(msg_image, at_sender=True)


# 每天凌晨清空字典以重置所有用户的卦象图片编号
def reset_gua_numbers():
    global user_gua_numbers
    user_gua_numbers = {}
# 在适当的地方调用 reset_gua_numbers 函数，例如在插件加载时设置一个定时任务
