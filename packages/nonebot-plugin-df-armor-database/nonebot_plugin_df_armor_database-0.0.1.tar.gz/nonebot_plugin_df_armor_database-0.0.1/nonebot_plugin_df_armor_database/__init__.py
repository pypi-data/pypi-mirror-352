import json
from pathlib import Path
from nonebot import on_command, require
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent, Message
from nonebot.matcher import Matcher
from nonebot.params import EventMessage

require("nonebot_plugin_waiter")
from nonebot_plugin_waiter import waiter

ARMOR_DB_PATH = Path("data/armor_database/armors.json")
HELMET_DB_PATH = Path("data/armor_database/helmets.json")
ARMOR_DB_PATH.parent.mkdir(parents=True, exist_ok=True)

# 初始化简介数据库

def init_armor_db():
    if not ARMOR_DB_PATH.exists():
        data = {
            "3": {
                "1": {
                    "name": "制式防弹背心",
                    "desc": "标准防弹背心，适合一般作战环境。"
                }
            },
            "4": {},
            "5": {},
            "6": {}
        }
        with open(ARMOR_DB_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

def init_helmet_db():
    if not HELMET_DB_PATH.exists():
        data = {
            "3": {
                "1": {
                    "name": "制式防弹头盔",
                    "desc": "标准防弹头盔，提供基础头部防护。"
                }
            },
            "4": {},
            "5": {},
            "6": {}
        }
        with open(HELMET_DB_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

def load_armor_db():
    with open(ARMOR_DB_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def load_helmet_db():
    with open(HELMET_DB_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

init_armor_db()
init_helmet_db()

# 状态缓存
desc_state = {}

armor_desc_cmd = on_command("防具简介", priority=10, block=True)

@armor_desc_cmd.handle()
async def _(bot: Bot, event: GroupMessageEvent, matcher: Matcher, msg: Message = EventMessage()):
    text = str(msg).strip()
    uid = event.user_id
    gid = event.group_id
    key = f"{gid}_{uid}"

    if text == "防具简介":
        # 使用 waiter 只等待当前用户的后续输入
        await matcher.send("你要查询护甲还是头盔？（请输入‘护甲’或‘头盔’，输入‘退出’可结束）")
        @waiter(waits=["message"], keep_session=True)
        async def wait_type(event: GroupMessageEvent):
            return event.get_plaintext().strip()
        reply = await wait_type.wait(timeout=60)
        if reply is None or reply == "退出":
            await matcher.send("已退出防具简介查询。")
            return
        if reply not in ("护甲", "头盔"):
            await matcher.send("请输入‘护甲’或‘头盔’。"); return
        # 进入等级选择
        await matcher.send(f"请输入要查询的{reply}等级（3, 4, 5或6）")
        @waiter(waits=["message"], keep_session=True)
        async def wait_level(event: GroupMessageEvent):
            return event.get_plaintext().strip()
        level = await wait_level.wait(timeout=60)
        if level is None or level == "退出":
            await matcher.send("已退出防具简介查询。")
            return
        if level not in ("3", "4", "5", "6"):
            await matcher.send("请输入3、4、5或6作为等级。")
            return
        # 展示装备列表
        state = {"type": reply, "level": level, "page": 1}
        await send_desc_item_list(matcher, state)
        # 进入装备选择
        while True:
            @waiter(waits=["message"], keep_session=True)
            async def wait_item(event: GroupMessageEvent):
                return event.get_plaintext().strip()
            item_text = await wait_item.wait(timeout=60)
            if item_text is None or item_text == "退出":
                await matcher.send("已退出防具简介查询。")
                return
            if item_text.startswith("第") and item_text.endswith("页"):
                try:
                    page = int(item_text[1:-1])
                    state["page"] = page
                    await send_desc_item_list(matcher, state)
                except Exception:
                    await matcher.send("页码格式错误，请输入如‘第2页’。"); continue
                continue
            try:
                idx = int(item_text)
            except Exception:
                await matcher.send("请输入装备名称前的序号选择，或输入‘第x页’翻页。")
                continue
            items = get_desc_item_list(state["type"], state["level"])
            page = state.get("page", 1)
            start = (page-1)*10
            if not (1 <= idx <= min(10, len(items)-start)):
                await matcher.send("序号超出范围，请重新输入。")
                continue
            item_idx = str(start + idx)
            item = items[item_idx]
            await matcher.send(f"{item['name']}简介：\n{item['desc']}")
            break
        return

def get_desc_item_list(item_type: str, level: str):
    if item_type == "护甲":
        data = load_armor_db()
    else:
        data = load_helmet_db()
    items = []
    for idx, (k, v) in enumerate(sorted(data.get(level, {}).items(), key=lambda x: int(x[0])), 1):
        items.append((str(idx), v))
    return dict(items)

async def send_desc_item_list(matcher: Matcher, state: dict):
    item_type = state["type"]
    level = state["level"]
    items = get_desc_item_list(item_type, level)
    page = state.get("page", 1)
    per_page = 10
    total = len(items)
    pages = (total+per_page-1)//per_page
    start = (page-1)*per_page
    end = start+per_page
    items_on_page = list(items.items())[start:end]
    if not items_on_page:
        await matcher.send(f"该等级暂无{item_type}简介。")
        return
    msg = f"【{level}级{item_type}简介列表 第{page}/{pages}页】\n"
    for idx, item in items_on_page:
        msg += f"{int(idx)-start}. {item['name']}\n"
    if pages > 1:
        msg += "输入“第x页”翻页。\n"
    msg += "请输入装备名称前的序号选择。"
    await matcher.send(msg)
