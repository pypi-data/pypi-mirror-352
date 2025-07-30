import inspect

from nonebot.adapters import Event, MessageTemplate
from nonebot.rule import to_me
from nonebot_plugin_alconna import (Alconna, AlconnaMatch, AlconnaQuery, Args,
                                    Arparma, At, Match, MultiVar, Option,
                                    Query, Subcommand, on_alconna, store_true)
from nonebot_plugin_uninfo import Uninfo
from nonebot_plugin_waiter import waiter

from nonebot import logger
from zhenxun_utils.message import MessageUtils

from .config import g_bSignStatus
from .dbService import g_pDBService
from .farm.farm import g_pFarmManager
from .farm.shop import g_pShopManager
from .json import g_pJsonManager
from .tool import g_pToolManager


async def isRegisteredByUid(uid: str) -> bool:
    result = await g_pDBService.user.isUserExist(uid)

    if not result:
        await MessageUtils.build_message("尚未开通农场，快at我发送 开通农场 开通吧").send()
        return False

    return True


diuse_register = on_alconna(
    Alconna("开通农场"),
    priority=5,
    rule=to_me(),
    block=True,
)

@diuse_register.handle()
async def handle_register(session: Uninfo):
    uid = str(session.user.id)
    user = await g_pDBService.user.getUserInfoByUid(uid)

    if user:
        await MessageUtils.build_message("🎉 您已经开通农场啦~").send(reply_to=True)
        return

    try:
        raw_name = str(session.user.name)
        safe_name = sanitize_username(raw_name)

        # 初始化用户信息
        success = await g_pDBService.user.initUserInfoByUid(
            uid=uid,
            name=safe_name,
            exp=0,
            point=500
        )

        msg = (
            "✅ 农场开通成功！\n💼 初始资金：500农场币"
            if success
            else "⚠️ 开通失败，请稍后再试"
        )
        logger.info(f"用户注册 {'成功' if success else '失败'}：{uid}")

    except Exception as e:
        msg = "⚠️ 系统繁忙，请稍后再试"
        logger.error(f"注册异常 | UID:{uid} | 错误：{str(e)}")

    await MessageUtils.build_message(msg).send(reply_to=True)

def sanitize_username(username: str, max_length: int = 15) -> str:
    """
    安全处理用户名
    功能：
    1. 移除首尾空白
    2. 过滤危险字符
    3. 转义单引号
    4. 处理空值
    5. 限制长度
    """
    # 处理空值
    if not username:
        return "神秘农夫"

    # 基础清洗
    cleaned = username.strip()

    # 允许的字符白名单（可自定义扩展）
    safe_chars = {
        '_', '-', '!', '@', '#', '$', '%', '^', '&', '*', '(', ')',
        '+', '=', '.', ',', '~', '·', ' ',
        'a','b','c','d','e','f','g','h','i','j','k','l','m',
        'n','o','p','q','r','s','t','u','v','w','x','y','z',
        'A','B','C','D','E','F','G','H','I','J','K','L','M',
        'N','O','P','Q','R','S','T','U','V','W','X','Y','Z',
        '0','1','2','3','4','5','6','7','8','9',
    }
    # 添加常用中文字符（Unicode范围）
    safe_chars.update(chr(c) for c in range(0x4E00, 0x9FFF+1))

    # 过滤危险字符
    filtered = [
        c if c in safe_chars or 0x4E00 <= ord(c) <= 0x9FFF
        else ''
        for c in cleaned
    ]

    # 合并处理结果
    safe_str = ''.join(filtered)

    # 转义单引号（双重保障）
    escaped = safe_str.replace("'", "''")

    # 处理空结果
    if not escaped:
        return "神秘农夫"

    # 长度限制
    return escaped[:max_length]

diuse_farm = on_alconna(
    Alconna(
        "我的农场",
        Option("--all", action=store_true),
        Subcommand("detail", help_text="农场详述"),
        Subcommand("my-point", help_text="我的农场币"),
        Subcommand("seed-shop", Args["res?", MultiVar(str)], help_text="种子商店"),
        Subcommand("buy-seed", Args["name?", str]["num?", int], help_text="购买种子"),
        Subcommand("my-seed", help_text="我的种子"),
        Subcommand("sowing", Args["name?", str]["num?", int], help_text="播种"),
        Subcommand("harvest", help_text="收获"),
        Subcommand("eradicate", help_text="铲除"),
        Subcommand("my-plant", help_text="我的作物"),
        Subcommand("sell-plant", Args["name?", str]["num?", int], help_text="出售作物"),
        Subcommand("stealing", Args["target?", At], help_text="偷菜"),
        Subcommand("change-name", Args["name?", str], help_text="更改农场名"),
        Subcommand("sign-in", help_text="农场签到"),
        Subcommand("admin-up", Args["num?", int], help_text="农场下阶段"),
    ),
    priority=5,
    block=True,
)

@diuse_farm.assign("$main")
async def _(session: Uninfo):
    uid = str(session.user.id)

    if not await isRegisteredByUid(uid):
        return

    image = await g_pFarmManager.drawFarmByUid(uid)
    await MessageUtils.build_message(image).send(reply_to=True)

diuse_farm.shortcut(
    "农场详述",
    command="我的农场",
    arguments=["detail"],
    prefix=True,
)

@diuse_farm.assign("detail")
async def _(session: Uninfo):
    uid = str(session.user.id)

    if not await isRegisteredByUid(uid):
        return

    info = await g_pFarmManager.drawDetailFarmByUid(uid)

    await MessageUtils.alc_forward_msg([info], session.self_id, session.user.name).send()

diuse_farm.shortcut(
    "我的农场币",
    command="我的农场",
    arguments=["my-point"],
    prefix=True,
)

@diuse_farm.assign("my-point")
async def _(session: Uninfo):
    uid = str(session.user.id)
    point = await g_pDBService.user.getUserPointByUid(uid)

    if point < 0:
        await MessageUtils.build_message("尚未开通农场，快at我发送 开通农场 开通吧").send()
        return False

    await MessageUtils.build_message(f"你的当前农场币为: {point}").send(reply_to=True)

diuse_farm.shortcut(
    "种子商店(.*?)",
    command="我的农场",
    arguments=["seed-shop"],
    prefix=True,
)

@diuse_farm.assign("seed-shop")
async def _(session: Uninfo, res: Match[tuple[str, ...]]):
    uid = str(session.user.id)

    if not await isRegisteredByUid(uid):
        return

    if res.result is inspect._empty:
        raw = []
    else:
        raw = res.result

    filterKey: str | int | None = None
    page: int = 1

    if len(raw) >= 1 and raw[0] is not None:
        first = raw[0]
        if isinstance(first, str) and first.isdigit():
            page = int(first)
        else:
            filterKey = first

    if len(raw) >= 2 and raw[1] is not None and isinstance(raw[1], str) and raw[1].isdigit():
        page = int(raw[1])

    if filterKey is None:
        image = await g_pShopManager.getSeedShopImage(page)
    else:
        image = await g_pShopManager.getSeedShopImage(filterKey, page)

    await MessageUtils.build_message(image).send()

diuse_farm.shortcut(
    "购买种子(?P<name>.*?)",
    command="我的农场",
    arguments=["buy-seed", "{name}"],
    prefix=True,
)

@diuse_farm.assign("buy-seed")
async def _(session: Uninfo, name: Match[str], num: Query[int] = AlconnaQuery("num", 1)):
    if not name.available:
        await MessageUtils.build_message(
            "请在指令后跟需要购买的种子名称"
        ).finish(reply_to=True)

    uid = str(session.user.id)

    if not await isRegisteredByUid(uid):
        return

    result = await g_pShopManager.buySeed(uid, name.result, num.result)
    await MessageUtils.build_message(result).send(reply_to=True)

diuse_farm.shortcut(
    "我的种子",
    command="我的农场",
    arguments=["my-seed"],
    prefix=True,
)

@diuse_farm.assign("my-seed")
async def _(session: Uninfo):
    uid = str(session.user.id)

    if not await isRegisteredByUid(uid):
        return

    result = await g_pFarmManager.getUserSeedByUid(uid)
    await MessageUtils.build_message(result).send(reply_to=True)

diuse_farm.shortcut(
    "播种(?P<name>.*?)",
    command="我的农场",
    arguments=["sowing", "{name}"],
    prefix=True,
)

@diuse_farm.assign("sowing")
async def _(session: Uninfo, name: Match[str], num: Query[int] = AlconnaQuery("num", -1)):
    if not name.available:
        await MessageUtils.build_message(
            "请在指令后跟需要播种的种子名称"
        ).finish(reply_to=True)

    uid = str(session.user.id)

    if not await isRegisteredByUid(uid):
        return

    result = await g_pFarmManager.sowing(uid, name.result, num.result)
    await MessageUtils.build_message(result).send(reply_to=True)


diuse_farm.shortcut(
    "收获",
    command="我的农场",
    arguments=["harvest"],
    prefix=True,
)

@diuse_farm.assign("harvest")
async def _(session: Uninfo):
    uid = str(session.user.id)

    if not await isRegisteredByUid(uid):
        return

    result = await g_pFarmManager.harvest(uid)
    await MessageUtils.build_message(result).send(reply_to=True)

diuse_farm.shortcut(
    "铲除",
    command="我的农场",
    arguments=["eradicate"],
    prefix=True,
)

@diuse_farm.assign("eradicate")
async def _(session: Uninfo):
    uid = str(session.user.id)

    if not await isRegisteredByUid(uid):
        return

    result = await g_pFarmManager.eradicate(uid)
    await MessageUtils.build_message(result).send(reply_to=True)


diuse_farm.shortcut(
    "我的作物",
    command="我的农场",
    arguments=["my-plant"],
    prefix=True,
)

@diuse_farm.assign("my-plant")
async def _(session: Uninfo):
    uid = str(session.user.id)

    if not await isRegisteredByUid(uid):
        return

    result = await g_pFarmManager.getUserPlantByUid(uid)
    await MessageUtils.build_message(result).send(reply_to=True)


reclamation = on_alconna(
    Alconna("开垦"),
    priority=5,
    block=True,
)

@reclamation.handle()
async def _(session: Uninfo):
    uid = str(session.user.id)

    if not await isRegisteredByUid(uid):
        return

    condition = await g_pFarmManager.reclamationCondition(uid)
    condition += "\n 回复是将执行开垦"
    await MessageUtils.build_message(condition).send(reply_to=True)

    @waiter(waits=["message"], keep_session=True)
    async def check(event: Event):
        return event.get_plaintext()

    resp = await check.wait(timeout=60)
    if resp is None:
        await MessageUtils.build_message("等待超时").send(reply_to=True)
        return
    if not resp == "是":
        return

    res = await g_pFarmManager.reclamation(uid)
    await MessageUtils.build_message(res).send(reply_to=True)

diuse_farm.shortcut(
    "出售作物(?P<name>.*?)",
    command="我的农场",
    arguments=["sell-plant", "{name}"],
    prefix=True,
)

@diuse_farm.assign("sell-plant")
async def _(session: Uninfo, name: Match[str], num: Query[int] = AlconnaQuery("num", -1)):
    uid = str(session.user.id)

    if not await isRegisteredByUid(uid):
        return

    result = await g_pShopManager.sellPlantByUid(uid, name.result, num.result)
    await MessageUtils.build_message(result).send(reply_to=True)

diuse_farm.shortcut(
    "偷菜",
    command="我的农场",
    arguments=["stealing"],
    prefix=True,
)

@diuse_farm.assign("stealing")
async def _(session: Uninfo, target: Match[At]):
    uid = str(session.user.id)

    if not await isRegisteredByUid(uid):
        return

    if not target.available:
        await MessageUtils.build_message("请在指令后跟需要at的人").finish(reply_to=True)

    tar = target.result
    result = await g_pDBService.user.isUserExist(tar.target)

    if not result:
        await MessageUtils.build_message("目标尚未开通农场，快邀请ta开通吧").send()
        return None

    result = await g_pFarmManager.stealing(uid, tar.target)
    await MessageUtils.build_message(result).send(reply_to=True)

diuse_farm.shortcut(
    "更改农场名(?P<name>)",
    command="我的农场",
    arguments=["change-name", "{name}"],
    prefix=True,
)

@diuse_farm.assign("change-name")
async def _(session: Uninfo, name: Match[str]):
    if not name.available:
        await MessageUtils.build_message(
            "请在指令后跟需要更改的农场名"
        ).finish(reply_to=True)

    uid = str(session.user.id)

    if not await isRegisteredByUid(uid):
        return

    safeName = sanitize_username(name.result)

    if safeName == "神秘农夫":
        await MessageUtils.build_message("农场名不支持特殊符号！").send(reply_to=True)
        return

    result = await g_pDBService.user.updateUserNameByUid(uid, safeName)

    if result == True:
        await MessageUtils.build_message("更新农场名成功！").send(reply_to=True)
    else:
        await MessageUtils.build_message("更新农场名失败！").send(reply_to=True)

diuse_farm.shortcut(
    "农场签到",
    command="我的农场",
    arguments=["sign-in"],
    prefix=True,
)

@diuse_farm.assign("sign-in")
async def _(session: Uninfo):
    uid = str(session.user.id)

    if not await isRegisteredByUid(uid):
        return

    #判断签到是否正常加载
    if not g_bSignStatus:
        await MessageUtils.build_message("签到功能异常！").send()

        return

    toDay = g_pToolManager.dateTime().date().today()
    message = ""
    status = await g_pDBService.userSign.sign(uid, toDay.strftime("%Y-%m-%d"))

    #如果完成签到
    if status == 1 or status == 2:
        #获取签到总天数
        signDay = await g_pDBService.userSign.getUserSignCountByDate(uid, toDay.strftime("%Y-%m"))
        exp, point = await g_pDBService.userSign.getUserSignRewardByDate(uid, toDay.strftime("%Y-%m-%d"))

        message += f"签到成功！累计签到天数：{signDay}\n获得经验{exp}，获得金币{point}"

        reward = g_pJsonManager.m_pSign['continuou'].get(f"{signDay}", None)

        if reward:
            extraPoint = reward.get('point', 0)
            extraExp = reward.get('exp', 0)

            plant = reward.get('plant', {})

            message += f"\n\n成功领取累计签到奖励：\n额外获得经验{extraExp}，额外获得金币{extraPoint}"

            vipPoint = reward.get('vipPoint', 0)

            if vipPoint > 0:
                message += f"，额外获得点券{vipPoint}"

            if plant:
                for key, value in plant.items():
                    message += f"\n获得{key}种子 * {value}"
    else:
        message = "签到失败！未知错误"

    await MessageUtils.build_message(message).send()

    # await MessageUtils.alc_forward_msg([info], session.self_id, BotConfig.self_nickname).send(reply_to=True)

diuse_farm.shortcut(
    "农场下阶段(.*?)",
    command="我的农场",
    arguments=["admin-up"],
    prefix=True,
)

@diuse_farm.assign("admin-up")
async def _(session: Uninfo, num: Query[int] = AlconnaQuery("num", 0)):
    uid = str(session.user.id)

    if not await isRegisteredByUid(uid):
        return

    await g_pDBService.userSoil.nextPhase(uid, num.result)
