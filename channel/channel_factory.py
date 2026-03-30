"""
channel factory
"""
from common import const
from .channel import Channel
from .utils import parse_channel_name


def create_channel(channel_name) -> Channel:
    """
    create a channel instance
    :param channel_name: channel name (e.g., "weixin" or "weixin:instance1")
    :return: channel instance
    """
    from common.log import logger
    channel_type, instance_name = parse_channel_name(channel_name)
    logger.info(f"[ChannelFactory] Creating channel: name={channel_name}, type={channel_type}, instance={instance_name}")

    ch = Channel()
    kwargs = {'_instance_name': instance_name} if instance_name else {}

    if channel_type == "terminal":
        from channel.terminal.terminal_channel import TerminalChannel
        ch = TerminalChannel(**kwargs)
    elif channel_type == 'web':
        from channel.web.web_channel import WebChannel
        ch = WebChannel(**kwargs)
    elif channel_type == "wechatmp":
        from channel.wechatmp.wechatmp_channel import WechatMPChannel
        ch = WechatMPChannel(passive_reply=True, **kwargs)
    elif channel_type == "wechatmp_service":
        from channel.wechatmp.wechatmp_channel import WechatMPChannel
        ch = WechatMPChannel(passive_reply=False, **kwargs)
    elif channel_type == "wechatcom_app":
        from channel.wechatcom.wechatcomapp_channel import WechatComAppChannel
        ch = WechatComAppChannel(**kwargs)
    elif channel_type == const.FEISHU:
        from channel.feishu.feishu_channel import FeiShuChanel
        ch = FeiShuChanel(**kwargs)
    elif channel_type == const.DINGTALK:
        from channel.dingtalk.dingtalk_channel import DingTalkChanel
        ch = DingTalkChanel(**kwargs)
    elif channel_type == const.WECOM_BOT:
        from channel.wecom_bot.wecom_bot_channel import WecomBotChannel
        ch = WecomBotChannel(**kwargs)
    elif channel_type == const.QQ:
        from channel.qq.qq_channel import QQChannel
        ch = QQChannel(**kwargs)
    elif channel_type in (const.WEIXIN, "wx"):
        from channel.weixin.weixin_channel import WeixinChannel
        ch = WeixinChannel(**kwargs)
        logger.info(f"[ChannelFactory] WeixinChannel instance: id={id(ch)}, _instance_name={getattr(ch, '_instance_name', 'N/A')}, instances in singleton: {list(WeixinChannel._instances.keys()) if hasattr(WeixinChannel, '_instances') else 'N/A'}")
        channel_type = const.WEIXIN
    else:
        raise RuntimeError(f"Unknown channel type: {channel_type}")
    ch.channel_type = channel_name  # Keep full name (e.g., "weixin:instance1")
    return ch
