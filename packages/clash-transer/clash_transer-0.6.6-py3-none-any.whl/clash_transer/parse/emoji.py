import unicodedata


def is_emoji(char):
    if not char:
        return False
    try:
        name = unicodedata.name(char)
        return "EMOJI" in name or any(
            [
                "\U0001f600" <= char <= "\U0001f64f",  # 表情符号
                "\U0001f300" <= char <= "\U0001f5ff",  # 符号和图标
                "\U0001f680" <= char <= "\U0001f6ff",  # 运输与地图
                "\U0001f700" <= char <= "\U0001f77f",  # 占星符号
                "\U0001f780" <= char <= "\U0001f7ff",  # 几何符号扩展
                "\U0001f800" <= char <= "\U0001f8ff",  # 补充箭头
                "\U0001f900" <= char <= "\U0001f9ff",  # 表情扩展
                "\U0001fa00" <= char <= "\U0001fa6f",  # 补充符号和象形文字
                "\U0001fa70" <= char <= "\U0001faff",  # 表情补充
                "\U00002700" <= char <= "\U000027bf",  # 杂项符号
                "\U00002600" <= char <= "\U000026ff",  # 杂项符号
                "\U00002b00" <= char <= "\U00002bff",  # 箭头
                "\U0001f1e6" <= char <= "\U0001f1ff",  # 区域标志符号（国旗）
            ]
        )
    except ValueError:
        return False
