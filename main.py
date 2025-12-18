import OlivOS
import json
import os
import time
import requests
import sys
from collections import deque

current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

try:
    from reply_strings import dictStrCustom
except ImportError:
    dictStrCustom = {}
    print("警告: 无法导入 reply_strings 模块")

data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
os.makedirs(data_dir, exist_ok=True)
os.makedirs(os.path.join(data_dir, 'users'), exist_ok=True)
os.makedirs(os.path.join(data_dir, 'sessions'), exist_ok=True)

config_file = os.path.join(data_dir, 'config.json')
banned_words_file = os.path.join(data_dir, 'banned_words.json')
default_config = {
    "api_key": "",
    "api_endpoint": "https://api.deepseek.com/v1/chat/completions",
    "default_model": "deepseek-chat",
    "cooldown_time": 10,
    "max_context": 5,
    "trigger_prefix": "#chat",
    "max_tokens": 1000,
    "temperature": 0.7,
    "enable_group": True,
    "enable_private": True,
    "debug_mode": False,
    "system_prompt": "",
    "global_enabled": True,
    "enable_filter": True,
    "enable_review": False,
    "max_system_chars": 1000,
    "group_settings": {}
}

default_banned_words = {
    "words": [],
    "enable_filter": True
}

dictTValue = {
    'tTargetName': '用户',
    'tContent': '',
    'tCooldown': '10',
    'tContext': '5',
    'tUseCount': '0',
    'tStatus': '正常',
    'tLastUsed': '从未使用',
    'tUserCount': '0',
    'tGroupStatus': '开启',
    'tPrivateStatus': '开启',
    'tDebugStatus': '关闭',
    'tFilterStatus': '开启',
    'tGlobalStatus': '开启',
    'tReviewStatus': '关闭',
    'tSystemPrompt': '未设置',
    'tPersonalSystem': '未设置',
    'tCount': '0',
    'tMaxSystemChars': '1000',
    'tMaxChars': '1000',
    'tCurrentChars': '0',
    'tPermissionSystem': '内置列表',
    'tPermissionStatus': '普通用户',
    'tMasterStatus': '否',
    'tPrefix': '#chat',
    'tTokens': '1000',
    'tTemperature': '0.7',
    'tModel': 'deepseek-chat',
    'tEndpoint': 'https://api.deepseek.com/v1/chat/completions'
}

MASTER_USERS = ['2139497594']

has_OlivaDiceCore = False
try:
    import OlivaDiceCore
    has_OlivaDiceCore = True
except ImportError:
    has_OlivaDiceCore = False

def get_user_hash(user_id, platform, user_type='user'):
    if has_OlivaDiceCore and hasattr(OlivaDiceCore, 'userConfig'):
        try:
            return OlivaDiceCore.userConfig.getUserHash(user_id, user_type, platform)
        except:
            pass
    return f"{user_id}|{user_type}|{platform}"

def is_master_user(user_id, plugin_event=None, Proc=None):
    if has_OlivaDiceCore and plugin_event and hasattr(OlivaDiceCore, 'ordinaryInviteManager'):
        try:
            bot_hash = plugin_event.bot_info.hash if hasattr(plugin_event.bot_info, 'hash') else None
            if bot_hash:
                user_hash = get_user_hash(user_id, plugin_event.platform['platform'])
                return OlivaDiceCore.ordinaryInviteManager.isInMasterList(bot_hash, user_hash)
        except:
            pass
    return str(user_id) in MASTER_USERS

def get_user_permission(plugin_event):
    user_id = plugin_event.data.user_id
    if is_master_user(user_id, plugin_event):
        return "master"
    if plugin_event.plugin_info['func_type'] == 'group_message':
        role = plugin_event.data.sender.get('role', 'member')
        if role == 'owner':
            return "owner"
        elif role == 'admin':
            return "admin"
    return "member"

def get_default_group_config():
    return {
        "enable_ai": True,
        "allow_ordinary": False,
        "last_toggle_time": 0,
        "toggled_by": None,
        "toggled_by_type": None
    }

def get_group_config(group_id):
    config = load_config()
    if "group_settings" not in config:
        config["group_settings"] = {}
    group_id_str = str(group_id)
    if group_id_str not in config["group_settings"]:
        default_config_value = get_default_group_config()
        default_config_value["enable_ai"] = config.get("enable_group", True)
        config["group_settings"][group_id_str] = default_config_value
        save_config(config)
    return config["group_settings"][group_id_str]

def save_group_config(group_id, group_config):
    config = load_config()
    if "group_settings" not in config:
        config["group_settings"] = {}
    config["group_settings"][str(group_id)] = group_config
    save_config(config)

def check_group_ai_permission(plugin_event, group_id=None):
    config = load_config()
    if not config.get("global_enabled", True):
        return False, dictStrCustom.get('strPermissionDeniedGlobal', '全局AI功能已关闭')
    
    if plugin_event.plugin_info['func_type'] == 'group_message':
        if not config.get("enable_group", True):
            return False, dictStrCustom.get('strPermissionDeniedGlobal', '群聊功能已全局关闭')
    
    user_permission = get_user_permission(plugin_event)
    
    if group_id:
        group_config = get_group_config(group_id)
        
        if not group_config.get("enable_ai", True):
            return False, dictStrCustom.get('strPermissionDeniedGroup', '本群AI功能已关闭')
        
        if user_permission in ["master", "owner", "admin"]:
            return True, f"权限验证通过（{user_permission}）"
        
        if group_config.get("allow_ordinary", False):
            return True, "普通成员可用"
        else:
            return False, dictStrCustom.get('strPermissionDeniedGroup', '本群AI功能仅限群主、管理员和Master使用')
    
    return True, "权限验证通过"

def toggle_group_ai(plugin_event, group_id, enable, reason=""):
    user_id = plugin_event.data.user_id
    user_permission = get_user_permission(plugin_event)
    
    if user_permission not in ["master", "owner", "admin"]:
        return False, dictStrCustom.get('strGroupToggleNoPermission', '权限不足，只有群主、管理员或Master可以开关AI功能')
    
    if user_permission in ["owner", "admin"]:
        if plugin_event.plugin_info['func_type'] != 'group_message':
            return False, dictStrCustom.get('strPermissionOwnerAdminOnly', '此功能仅限群主和管理员在本群使用')
        if str(group_id) != str(plugin_event.data.group_id):
            return False, dictStrCustom.get('strPermissionOwnerAdminOnly', '此功能仅限群主和管理员在本群使用')
    
    group_config = get_group_config(group_id)
    group_config["enable_ai"] = enable
    group_config["last_toggle_time"] = time.time()
    group_config["toggled_by"] = user_id
    group_config["toggled_by_type"] = user_permission
    if reason:
        group_config["toggle_reason"] = reason
    
    save_group_config(group_id, group_config)
    
    if enable:
        return True, dictStrCustom.get('strGroupToggleLocalSuccess', '已开启当前群聊的AI功能').replace('{status}', '开启')
    else:
        return True, dictStrCustom.get('strGroupToggleLocalSuccess', '已关闭当前群聊的AI功能').replace('{status}', '关闭')

def toggle_group_ordinary_permission(plugin_event, group_id, allow):
    user_id = plugin_event.data.user_id
    user_permission = get_user_permission(plugin_event)
    
    if user_permission not in ["master", "owner", "admin"]:
        return False, dictStrCustom.get('strGroupToggleNoPermission', '权限不足，只有群主、管理员或Master可以开关AI功能')
    
    if user_permission in ["owner", "admin"]:
        if plugin_event.plugin_info['func_type'] != 'group_message':
            return False, dictStrCustom.get('strPermissionOwnerAdminOnly', '此功能仅限群主和管理员在本群使用')
        if str(group_id) != str(plugin_event.data.group_id):
            return False, dictStrCustom.get('strPermissionOwnerAdminOnly', '此功能仅限群主和管理员在本群使用')
    
    group_config = get_group_config(group_id)
    group_config["allow_ordinary"] = allow
    group_config["last_toggle_time"] = time.time()
    group_config["toggled_by"] = user_id
    group_config["toggled_by_type"] = user_permission
    
    save_group_config(group_id, group_config)
    
    if allow:
        return True, dictStrCustom.get('strAllowOrdinarySuccess', '已允许普通成员使用本群AI功能').replace('{status}', '允许')
    else:
        return True, dictStrCustom.get('strAllowOrdinarySuccess', '已禁止普通成员使用本群AI功能').replace('{status}', '禁止')

def load_config():
    if not os.path.exists(config_file):
        save_config(default_config)
        return default_config.copy()
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
            for key in default_config:
                if key not in config:
                    config[key] = default_config[key]
            return config
    except:
        return default_config.copy()

def save_config(config):
    with open(config_file, 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=2)

def load_banned_words():
    if not os.path.exists(banned_words_file):
        save_banned_words(default_banned_words)
        return default_banned_words.copy()
    try:
        with open(banned_words_file, 'r', encoding='utf-8') as f:
            banned_words_data = json.load(f)
            for key in default_banned_words:
                if key not in banned_words_data:
                    banned_words_data[key] = default_banned_words[key]
            return banned_words_data
    except:
        return default_banned_words.copy()

def save_banned_words(banned_words_data):
    with open(banned_words_file, 'w', encoding='utf-8') as f:
        json.dump(banned_words_data, f, ensure_ascii=False, indent=2)

def get_user_file(user_id):
    return os.path.join(data_dir, 'users', f'user_{user_id}.json')

def get_session_file(user_id):
    return os.path.join(data_dir, 'sessions', f'session_{user_id}.json')

def load_user_data(user_id):
    user_file = get_user_file(user_id)
    default_user = {
        "user_id": user_id,
        "system_prompt": "",
        "is_locked": False,
        "use_count": 0,
        "last_used": None,
        "first_message_sent": False
    }
    if not os.path.exists(user_file):
        save_user_data(user_id, default_user)
        return default_user
    try:
        with open(user_file, 'r', encoding='utf-8') as f:
            user_data = json.load(f)
            for key in default_user:
                if key not in user_data:
                    user_data[key] = default_user[key]
            return user_data
    except:
        return default_user.copy()

def save_user_data(user_id, user_data):
    user_file = get_user_file(user_id)
    with open(user_file, 'w', encoding='utf-8') as f:
        json.dump(user_data, f, ensure_ascii=False, indent=2)

def load_session_data(user_id):
    session_file = get_session_file(user_id)
    config = load_config()
    default_session = {
        "user_id": user_id,
        "history": deque(maxlen=config["max_context"] * 2),
        "last_active": None,
        "message_count": 0,
        "last_system_insert": 0
    }
    if not os.path.exists(session_file):
        save_session_data(user_id, default_session)
        return default_session
    try:
        with open(session_file, 'r', encoding='utf-8') as f:
            session_data = json.load(f)
            session_data["history"] = deque(session_data.get("history", []), maxlen=config["max_context"] * 2)
            if "message_count" not in session_data:
                session_data["message_count"] = len(session_data["history"])
            if "last_system_insert" not in session_data:
                session_data["last_system_insert"] = 0
            return session_data
    except:
        return default_session.copy()

def save_session_data(user_id, session_data):
    session_file = get_session_file(user_id)
    session_data_save = session_data.copy()
    session_data_save["history"] = list(session_data["history"])
    with open(session_file, 'w', encoding='utf-8') as f:
        json.dump(session_data_save, f, ensure_ascii=False, indent=2)

def get_all_users():
    users_dir = os.path.join(data_dir, 'users')
    if not os.path.exists(users_dir):
        return []
    user_files = [f for f in os.listdir(users_dir) if f.startswith('user_') and f.endswith('.json')]
    user_ids = [f[5:-5] for f in user_files]
    return user_ids

def get_all_groups():
    config = load_config()
    group_settings = config.get("group_settings", {})
    return list(group_settings.keys())

def format_reply_str(reply_str, dictTValue):
    for key in dictTValue:
        reply_str = reply_str.replace('{' + key + '}', str(dictTValue[key]))
    return reply_str

def clear_user_session(user_id):
    try:
        session_file = get_session_file(user_id)
        if os.path.exists(session_file):
            os.remove(session_file)
        user_data = load_user_data(user_id)
        user_data["first_message_sent"] = False
        save_user_data(user_id, user_data)
        return True
    except:
        return False

def check_banned_words(text):
    banned_words_data = load_banned_words()
    if not banned_words_data.get("enable_filter", True):
        return None
    text_lower = text.lower()
    for word in banned_words_data.get("words", []):
        if word.lower() in text_lower:
            return word
    return None

def check_cooldown(user_id):
    config = load_config()
    user_data = load_user_data(user_id)
    if user_data["last_used"]:
        current_time = time.time()
        cooldown_end = user_data["last_used"] + config["cooldown_time"]
        if current_time < cooldown_end:
            return int(cooldown_end - current_time)
    return 0

def build_messages(user_input, user_id):
    config = load_config()
    user_data = load_user_data(user_id)
    session_data = load_session_data(user_id)
    messages = []
    system_content = user_data.get("system_prompt", "")
    if not system_content:
        system_content = config.get("system_prompt", "")
    history = list(session_data["history"])
    messages.extend(history)
    is_first_message = not user_data.get("first_message_sent", False)
    if is_first_message:
        user_content = user_input
        user_data["first_message_sent"] = True
        save_user_data(user_id, user_data)
    else:
        user_content = user_input
    max_context = config["max_context"]
    insert_interval = max(1, max_context - 1)
    messages_since_last_system = session_data.get("message_count", 0) - session_data.get("last_system_insert", 0)
    should_insert_system = system_content and (messages_since_last_system >= insert_interval or is_first_message)
    final_messages = []
    if should_insert_system:
        final_messages.append({"role": "system", "content": system_content})
        session_data["last_system_insert"] = session_data.get("message_count", 0) + 1
    final_messages.extend(messages)
    final_messages.append({"role": "user", "content": user_content})
    session_data["message_count"] = session_data.get("message_count", 0) + 1
    save_session_data(user_id, session_data)
    return final_messages

def call_deepseek_api(prompt, user_id, plugin_event):
    config = load_config()
    try:
        user_data = load_user_data(user_id)
        messages = build_messages(prompt, user_id)
        if config["debug_mode"]:
            debug_info = dictStrCustom.get('strDebugInfo', 'Debug信息: {tContent}').replace('{tContent}', '发送的消息结构：\n')
            for i, msg in enumerate(messages):
                role = msg['role']
                content_preview = msg['content'][:100] + ("..." if len(msg['content']) > 100 else "")
                debug_info += f"{i+1}. [{role}]: {content_preview}\n"
            plugin_event.reply(debug_info)
        response = requests.post(
            config["api_endpoint"],
            headers={"Authorization": f"Bearer {config['api_key']}"},
            json={
                "model": config["default_model"],
                "messages": messages,
                "temperature": config["temperature"],
                "max_tokens": config["max_tokens"],
                "stream": True
            },
            timeout=60
        )
        if response.status_code == 200:
            assistant_reply = ""
            for line in response.iter_lines():
                if line:
                    line = line.decode('utf-8')
                    if line.startswith('data: '):
                        data = line[6:]
                        if data == '[DONE]':
                            break
                        try:
                            chunk = json.loads(data)
                            if 'choices' in chunk and chunk['choices']:
                                delta = chunk['choices'][0].get('delta', {})
                                if 'content' in delta:
                                    assistant_reply += delta['content']
                        except:
                            continue
            if config.get("enable_review", False):
                review_result = content_review(assistant_reply, config)
                if review_result == "1":
                    user_data["is_locked"] = True
                    user_data["lock_reason"] = "生成违规内容"
                    user_data["lock_time"] = time.time()
                    save_user_data(user_id, user_data)
                    return dictStrCustom.get('strReviewBlocked', '⚠️ 内容包含违规信息，用户已被锁定')
                elif review_result == "0":
                    session_data = load_session_data(user_id)
                    session_data["history"].append({"role": "user", "content": prompt})
                    session_data["history"].append({"role": "assistant", "content": assistant_reply})
                    session_data["last_active"] = time.time()
                    user_data["use_count"] += 1
                    user_data["last_used"] = time.time()
                    save_session_data(user_id, session_data)
                    save_user_data(user_id, user_data)
                    return assistant_reply
                else:
                    return dictStrCustom.get('strReviewFailed', '⚠️ 内容审核失败，请稍后重试')
            else:
                session_data = load_session_data(user_id)
                session_data["history"].append({"role": "user", "content": prompt})
                session_data["history"].append({"role": "assistant", "content": assistant_reply})
                session_data["last_active"] = time.time()
                user_data["use_count"] += 1
                user_data["last_used"] = time.time()
                save_session_data(user_id, session_data)
                save_user_data(user_id, user_data)
                return assistant_reply
        else:
            if config["debug_mode"]:
                return f"API调用失败: {response.status_code} - {response.text}"
            else:
                return None
    except Exception as e:
        if config["debug_mode"]:
            return f"API调用异常: {str(e)}"
        else:
            return None

def content_review(content, config):
    try:
        review_prompt = "对括号内的内容进行审核。如果包含违规内容，就返回数字1，不包含就返回数字0。不需要其他返回内容，只需要返回一个阿拉伯数字就可以。\n【" + content + "】"
        review_response = requests.post(
            config["api_endpoint"],
            headers={"Authorization": f"Bearer {config['api_key']}"},
            json={
                "model": config["default_model"],
                "messages": [{"role": "user", "content": review_prompt}],
                "temperature": 0.1,
                "max_tokens": 5,
                "stream": False
            },
            timeout=15
        )
        if review_response.status_code == 200:
            result = review_response.json()
            review_result = result['choices'][0]['message']['content'].strip()
            return review_result
        else:
            return None
    except Exception as e:
        return None

def unity_reply(plugin_event, Proc=None):
    config = load_config()
    banned_words_data = load_banned_words()
    tmp_reast_str = plugin_event.data.message.strip()
    tmp_userID = plugin_event.data.user_id
    dictTValue_local = dictTValue.copy()
    dictTValue_local['tUserName'] = plugin_event.data.sender.get('name', '用户')
    
    if tmp_reast_str.startswith('.deepseek'):
        is_master = is_master_user(tmp_userID, plugin_event, Proc)
        parts = tmp_reast_str.split()
        if len(parts) < 2:
            plugin_event.reply(dictStrCustom.get('strSimpleHelp', '使用 .deepseek help 查看帮助'))
            return
        command = parts[1]
        
        if command == 'help':
            if not is_master:
                plugin_event.reply(dictStrCustom.get('strNoPermission', '权限不足，无法执行此操作'))
                return
            plugin_event.reply(dictStrCustom.get('strHelpMaster', '管理帮助信息未定义'))
            return
        
        elif command == 'checkperm':
            is_master_status = is_master_user(tmp_userID, plugin_event, Proc)
            permission_system = 'OlivaDiceCore' if has_OlivaDiceCore and hasattr(OlivaDiceCore, 'ordinaryInviteManager') else '内置列表'
            master_status = '是' if str(tmp_userID) in MASTER_USERS else '否'
            permission_status = 'Master用户' if is_master_status else '普通用户'
            dictTValue_local['tTargetName'] = str(tmp_userID)
            dictTValue_local['tPermissionStatus'] = permission_status
            dictTValue_local['tPermissionSystem'] = permission_system
            dictTValue_local['tMasterStatus'] = master_status
            tmp_reply_str = format_reply_str(dictStrCustom.get('strCheckPermResult', '权限检查结果信息未定义'), dictTValue_local)
            plugin_event.reply(tmp_reply_str)
            return
        
        elif command == 'status':
            if not is_master:
                plugin_event.reply(dictStrCustom.get('strNoPermission', '权限不足，无法执行此操作'))
                return
            user_ids = get_all_users()
            dictTValue_local['tUserCount'] = str(len(user_ids))
            dictTValue_local['tGroupStatus'] = '开启' if config["enable_group"] else '关闭'
            dictTValue_local['tPrivateStatus'] = '开启' if config["enable_private"] else '关闭'
            dictTValue_local['tCooldown'] = str(config["cooldown_time"])
            dictTValue_local['tContext'] = str(config["max_context"])
            dictTValue_local['tDebugStatus'] = '开启' if config["debug_mode"] else '关闭'
            dictTValue_local['tFilterStatus'] = '开启' if banned_words_data.get("enable_filter", True) else '关闭'
            dictTValue_local['tGlobalStatus'] = '开启' if config.get("global_enabled", True) else '关闭'
            dictTValue_local['tReviewStatus'] = '开启' if config.get("enable_review", False) else '关闭'
            dictTValue_local['tSystemPrompt'] = config.get("system_prompt", "未设置")[:50] + ("..." if len(config.get("system_prompt", "")) > 50 else "")
            dictTValue_local['tMaxSystemChars'] = str(config.get("max_system_chars", 1000))
            dictTValue_local['tPermissionSystem'] = 'OlivaDiceCore' if has_OlivaDiceCore and hasattr(OlivaDiceCore, 'ordinaryInviteManager') else '内置列表'
            tmp_reply_str = format_reply_str(dictStrCustom.get('strSystemStatus', '系统状态信息未定义'), dictTValue_local)
            plugin_event.reply(tmp_reply_str)
            return
        
        elif command == 'config':
            if not is_master:
                plugin_event.reply(dictStrCustom.get('strNoPermission', '权限不足，无法执行此操作'))
                return
            permission_system = 'OlivaDiceCore' if has_OlivaDiceCore and hasattr(OlivaDiceCore, 'ordinaryInviteManager') else '内置列表'
            dictTValue_local['tCooldown'] = str(config["cooldown_time"])
            dictTValue_local['tContext'] = str(config["max_context"])
            dictTValue_local['tPrefix'] = config["trigger_prefix"]
            dictTValue_local['tTokens'] = str(config["max_tokens"])
            dictTValue_local['tTemperature'] = str(config["temperature"])
            dictTValue_local['tModel'] = config["default_model"]
            dictTValue_local['tEndpoint'] = config["api_endpoint"]
            dictTValue_local['tGroupStatus'] = '开启' if config["enable_group"] else '关闭'
            dictTValue_local['tPrivateStatus'] = '开启' if config["enable_private"] else '关闭'
            dictTValue_local['tDebugStatus'] = '开启' if config["debug_mode"] else '关闭'
            dictTValue_local['tFilterStatus'] = '开启' if banned_words_data.get("enable_filter", True) else '关闭'
            dictTValue_local['tGlobalStatus'] = '开启' if config.get("global_enabled", True) else '关闭'
            dictTValue_local['tMaxSystemChars'] = str(config.get("max_system_chars", 1000))
            dictTValue_local['tSystemPrompt'] = config.get("system_prompt", "未设置")[:100] + ("..." if len(config.get("system_prompt", "")) > 100 else "")
            dictTValue_local['tPermissionSystem'] = permission_system
            tmp_reply_str = format_reply_str(dictStrCustom.get('strConfigInfo', '配置信息未定义'), dictTValue_local)
            plugin_event.reply(tmp_reply_str)
            return
        
        elif command == 'system':
            if not is_master:
                plugin_event.reply(dictStrCustom.get('strNoPermission', '权限不足，无法执行此操作'))
                return
            current_system = config.get("system_prompt", "未设置")
            dictTValue_local['tContent'] = current_system
            tmp_reply_str = format_reply_str(dictStrCustom.get('strCurrentSystem', '当前公共系统提示词: {tContent}'), dictTValue_local)
            plugin_event.reply(tmp_reply_str)
            return
        
        elif command == 'users':
            if not is_master:
                plugin_event.reply(dictStrCustom.get('strNoPermission', '权限不足，无法执行此操作'))
                return
            user_ids = get_all_users()
            if user_ids:
                user_items = "\n".join([f"- {uid}" for uid in user_ids[:20]])
                user_list = dictStrCustom.get('strUserList', '用户列表:\n{user_items}').replace('{user_items}', user_items)
                if len(user_ids) > 20:
                    more_text = dictStrCustom.get('strUserListMore', '... 还有 {remaining} 个用户').replace('{remaining}', str(len(user_ids) - 20))
                    user_list += f"\n{more_text}"
                plugin_event.reply(user_list)
            else:
                plugin_event.reply(dictStrCustom.get('strNoUserData', '暂无用户数据'))
            return
        
        elif command == 'user':
            if not is_master:
                plugin_event.reply(dictStrCustom.get('strNoPermission', '权限不足，无法执行此操作'))
                return
            if len(parts) < 3:
                dictTValue_local['tContent'] = dictStrCustom.get('strUserCommandExample', '.deepseek user 123456')
                tmp_reply_str = format_reply_str(dictStrCustom.get('strUserIDRequired', '请指定用户ID，例如: {example_command}'), dictTValue_local)
                plugin_event.reply(tmp_reply_str)
                return
            if len(parts) >= 4:
                sub_command = parts[2]
                target_user_id = parts[3]
                if sub_command == 'lock':
                    user_data = load_user_data(target_user_id)
                    user_data["is_locked"] = True
                    save_user_data(target_user_id, user_data)
                    dictTValue_local['tTargetName'] = target_user_id
                    dictTValue_local['tContent'] = '锁定'
                    tmp_reply_str = format_reply_str(dictStrCustom.get('strUserLockStatus', '用户已{status}'), dictTValue_local)
                    plugin_event.reply(tmp_reply_str)
                    return
                elif sub_command == 'unlock':
                    user_data = load_user_data(target_user_id)
                    user_data["is_locked"] = False
                    save_user_data(target_user_id, user_data)
                    dictTValue_local['tTargetName'] = target_user_id
                    dictTValue_local['tContent'] = '解锁'
                    tmp_reply_str = format_reply_str(dictStrCustom.get('strUserLockStatus', '用户已{status}'), dictTValue_local)
                    plugin_event.reply(tmp_reply_str)
                    return
                elif sub_command == 'clear':
                    if clear_user_session(target_user_id):
                        dictTValue_local['tTargetName'] = target_user_id
                        tmp_reply_str = format_reply_str(dictStrCustom.get('strUserClearedSuccess', '用户 {tTargetName} 记录已清空'), dictTValue_local)
                        plugin_event.reply(tmp_reply_str)
                    else:
                        plugin_event.reply(dictStrCustom.get('strClearUserFailed', '清空用户记录失败'))
                    return
                else:
                    dictTValue_local['tContent'] = 'lock, unlock, clear'
                    tmp_reply_str = format_reply_str(dictStrCustom.get('strUnknownSubCommand', '未知子命令，可用: {available_commands}'), dictTValue_local)
                    plugin_event.reply(tmp_reply_str)
                    return
            else:
                target_user_id = parts[2]
                user_data = load_user_data(target_user_id)
                dictTValue_local['tTargetName'] = target_user_id
                dictTValue_local['tUseCount'] = str(user_data["use_count"])
                dictTValue_local['tStatus'] = '锁定' if user_data["is_locked"] else '正常'
                if user_data["last_used"]:
                    dictTValue_local['tLastUsed'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(user_data["last_used"]))
                else:
                    dictTValue_local['tLastUsed'] = '从未使用'
                tmp_reply_str = format_reply_str(dictStrCustom.get('strUserDetail', '用户详情信息未定义'), dictTValue_local)
                plugin_event.reply(tmp_reply_str)
                return
        
        elif command == 'group':
            if not is_master:
                plugin_event.reply(dictStrCustom.get('strNoPermission', '权限不足，无法执行此操作'))
                return
            if len(parts) < 3:
                plugin_event.reply(dictStrCustom.get('strGroupIDRequired', '请指定群聊ID'))
                return
            sub_command = parts[2]
            if sub_command == 'list':
                group_ids = get_all_groups()
                if group_ids:
                    group_items = []
                    for i, group_id in enumerate(group_ids[:20]):
                        group_config = get_group_config(group_id)
                        ai_status = '开启' if group_config.get("enable_ai", True) else '关闭'
                        allow_ordinary = '允许' if group_config.get("allow_ordinary", False) else '禁止'
                        group_items.append(f"{i+1}. 群聊 {group_id}: AI={ai_status}, 普通成员={allow_ordinary}")
                    group_list_text = "\n".join(group_items)
                    if len(group_ids) > 20:
                        group_list_text += f"\n... 还有 {len(group_ids) - 20} 个群聊"
                    plugin_event.reply(f"群聊配置列表（共 {len(group_ids)} 个）：\n{group_list_text}")
                else:
                    plugin_event.reply("暂无群聊配置")
                return
            elif len(parts) < 4:
                plugin_event.reply(dictStrCustom.get('strGroupIDRequired', '请指定群聊ID'))
                return
            target_group_id = parts[3]
            if not target_group_id.isdigit():
                plugin_event.reply(dictStrCustom.get('strInvalidGroupID', '无效的群聊ID，请输入数字'))
                return
            target_group_id = int(target_group_id)
            if sub_command == 'status':
                group_config = get_group_config(target_group_id)
                ai_status = '开启' if group_config.get("enable_ai", True) else '关闭'
                allow_ordinary = '允许' if group_config.get("allow_ordinary", False) else '禁止'
                last_op_time = '从未操作'
                if group_config.get("last_toggle_time", 0) > 0:
                    last_op_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(group_config["last_toggle_time"]))
                operator_id = group_config.get("toggled_by", "未知")
                operator_type = group_config.get("toggled_by_type", "未知")
                status_text = f"群聊 {target_group_id} 的AI状态：\n"
                status_text += f"├─ 功能状态：{ai_status}\n"
                status_text += f"├─ 允许普通成员：{allow_ordinary}\n"
                status_text += f"├─ 最后操作时间：{last_op_time}\n"
                status_text += f"├─ 操作者：{operator_type}\n"
                status_text += f"└─ 操作者ID：{operator_id}"
                plugin_event.reply(status_text)
                return
            elif sub_command == 'toggle':
                if len(parts) < 5:
                    plugin_event.reply(dictStrCustom.get('strInvalidToggleValue', '参数错误，请输入 on 或 off'))
                    return
                toggle_value = parts[4].lower()
                if toggle_value not in ['on', 'off']:
                    plugin_event.reply(dictStrCustom.get('strInvalidToggleValue', '参数错误，请输入 on 或 off'))
                    return
                enable = toggle_value == 'on'
                success, message = toggle_group_ai(plugin_event, target_group_id, enable, "Master远程操作")
                plugin_event.reply(message)
                return
            elif sub_command == 'allow':
                if len(parts) < 5:
                    plugin_event.reply(dictStrCustom.get('strInvalidAllowValue', '参数错误，请输入 allow 或 deny'))
                    return
                allow_value = parts[4].lower()
                if allow_value not in ['allow', 'deny']:
                    plugin_event.reply(dictStrCustom.get('strInvalidAllowValue', '参数错误，请输入 allow 或 deny'))
                    return
                allow = allow_value == 'allow'
                success, message = toggle_group_ordinary_permission(plugin_event, target_group_id, allow)
                plugin_event.reply(message)
                return
            elif sub_command == 'reset':
                group_config = get_default_group_config()
                group_config["enable_ai"] = config.get("enable_group", True)
                save_group_config(target_group_id, group_config)
                plugin_event.reply(f"已重置群聊 {target_group_id} 的配置")
                return
            else:
                plugin_event.reply("未知的子命令，可用: list, status, toggle, allow, reset")
                return
        
        elif command == 'set' and len(parts) >= 4:
            if not is_master:
                plugin_event.reply(dictStrCustom.get('strNoPermission', '权限不足，无法执行此操作'))
                return
            set_type = parts[2]
            set_value = ' '.join(parts[3:])
            if set_type == 'cooldown':
                try:
                    value = int(set_value)
                    config["cooldown_time"] = value
                    save_config(config)
                    dictTValue_local['tContent'] = f"冷却时间设置为 {value} 秒"
                    tmp_reply_str = format_reply_str(dictStrCustom.get('strConfigUpdated', '配置已更新: {tContent}'), dictTValue_local)
                    plugin_event.reply(tmp_reply_str)
                except:
                    plugin_event.reply(dictStrCustom.get('strInvalidParameter', '参数错误，请输入数字'))
                return
            elif set_type == 'context':
                try:
                    value = int(set_value)
                    config["max_context"] = value
                    save_config(config)
                    dictTValue_local['tContent'] = f"上下文限制设置为 {value} 段"
                    tmp_reply_str = format_reply_str(dictStrCustom.get('strConfigUpdated', '配置已更新: {tContent}'), dictTValue_local)
                    plugin_event.reply(tmp_reply_str)
                except:
                    plugin_event.reply(dictStrCustom.get('strInvalidParameter', '参数错误，请输入数字'))
                return
            elif set_type == 'prefix':
                config["trigger_prefix"] = set_value
                save_config(config)
                dictTValue_local['tContent'] = f"触发前缀设置为 {set_value}"
                tmp_reply_str = format_reply_str(dictStrCustom.get('strConfigUpdated', '配置已更新: {tContent}'), dictTValue_local)
                plugin_event.reply(tmp_reply_str)
                return
            elif set_type == 'tokens':
                try:
                    value = int(set_value)
                    config["max_tokens"] = value
                    save_config(config)
                    dictTValue_local['tContent'] = f"最大Token数设置为 {value}"
                    tmp_reply_str = format_reply_str(dictStrCustom.get('strConfigUpdated', '配置已更新: {tContent}'), dictTValue_local)
                    plugin_event.reply(tmp_reply_str)
                except:
                    plugin_event.reply(dictStrCustom.get('strInvalidParameter', '参数错误，请输入数字'))
                return
            elif set_type == 'temperature':
                try:
                    value = float(set_value)
                    config["temperature"] = value
                    save_config(config)
                    dictTValue_local['tContent'] = f"温度参数设置为 {value}"
                    tmp_reply_str = format_reply_str(dictStrCustom.get('strConfigUpdated', '配置已更新: {tContent}'), dictTValue_local)
                    plugin_event.reply(tmp_reply_str)
                except:
                    plugin_event.reply(dictStrCustom.get('strInvalidParameter', '参数错误，请输入数字'))
                return
            elif set_type == 'model':
                config["default_model"] = set_value
                save_config(config)
                dictTValue_local['tContent'] = f"AI模型设置为 {set_value}"
                tmp_reply_str = format_reply_str(dictStrCustom.get('strConfigUpdated', '配置已更新: {tContent}'), dictTValue_local)
                plugin_event.reply(tmp_reply_str)
                return
            elif set_type == 'apikey':
                config["api_key"] = set_value
                save_config(config)
                plugin_event.reply(dictStrCustom.get('strApiKeyUpdated', 'API Key已更新'))
                return
            elif set_type == 'endpoint':
                config["api_endpoint"] = set_value
                save_config(config)
                dictTValue_local['tContent'] = f"API端点设置为 {set_value}"
                tmp_reply_str = format_reply_str(dictStrCustom.get('strConfigUpdated', '配置已更新: {tContent}'), dictTValue_local)
                plugin_event.reply(tmp_reply_str)
                return
            elif set_type == 'system':
                config["system_prompt"] = set_value
                save_config(config)
                plugin_event.reply(dictStrCustom.get('strSystemPromptUpdated', '公共系统提示词已更新'))
                return
            elif set_type == 'maxsystemchars':
                try:
                    value = int(set_value)
                    if value < 10:
                        plugin_event.reply(dictStrCustom.get('strMinSystemChars', '系统提示词最大字符数不能小于10'))
                        return
                    config["max_system_chars"] = value
                    save_config(config)
                    dictTValue_local['tContent'] = f"系统提示词最大字符数设置为 {value}"
                    tmp_reply_str = format_reply_str(dictStrCustom.get('strSetSystemChars', '系统提示词最大字符数设置为 {value}'), dictTValue_local)
                    plugin_event.reply(tmp_reply_str)
                except:
                    plugin_event.reply(dictStrCustom.get('strInvalidParameter', '参数错误，请输入数字'))
                return
            else:
                dictTValue_local['tContent'] = 'cooldown, context, prefix, tokens, temperature, model, apikey, endpoint, system, maxsystemchars'
                tmp_reply_str = format_reply_str(dictStrCustom.get('strSetTypeError', '未知设置类型，可用: {available_types}'), dictTValue_local)
                plugin_event.reply(tmp_reply_str)
                return
        
        elif command == 'toggle' and len(parts) >= 3:
            if not is_master:
                plugin_event.reply(dictStrCustom.get('strNoPermission', '权限不足，无法执行此操作'))
                return
            toggle_type = parts[2]
            if toggle_type == 'group':
                config["enable_group"] = not config["enable_group"]
                save_config(config)
                status = "开启" if config["enable_group"] else "关闭"
                dictTValue_local['tContent'] = status
                dictTValue_local['tStatus'] = '群聊'
                tmp_reply_str = format_reply_str(dictStrCustom.get('strToggleStatus', '{function}功能已{status}'), dictTValue_local)
                plugin_event.reply(tmp_reply_str)
                return
            elif toggle_type == 'private':
                config["enable_private"] = not config["enable_private"]
                save_config(config)
                status = "开启" if config["enable_private"] else "关闭"
                dictTValue_local['tContent'] = status
                dictTValue_local['tStatus'] = '私聊'
                tmp_reply_str = format_reply_str(dictStrCustom.get('strToggleStatus', '{function}功能已{status}'), dictTValue_local)
                plugin_event.reply(tmp_reply_str)
                return
            elif toggle_type == 'debug':
                config["debug_mode"] = not config["debug_mode"]
                save_config(config)
                status = "开启" if config["debug_mode"] else "关闭"
                dictTValue_local['tContent'] = status
                dictTValue_local['tStatus'] = 'Debug模式'
                tmp_reply_str = format_reply_str(dictStrCustom.get('strToggleStatus', '{function}功能已{status}'), dictTValue_local)
                plugin_event.reply(tmp_reply_str)
                return
            elif toggle_type == 'filter':
                banned_words_data["enable_filter"] = not banned_words_data.get("enable_filter", True)
                save_banned_words(banned_words_data)
                status = "开启" if banned_words_data["enable_filter"] else "关闭"
                dictTValue_local['tContent'] = status
                dictTValue_local['tStatus'] = '违禁词过滤'
                tmp_reply_str = format_reply_str(dictStrCustom.get('strToggleStatus', '{function}功能已{status}'), dictTValue_local)
                plugin_event.reply(tmp_reply_str)
                return
            elif toggle_type == 'global':
                config["global_enabled"] = not config.get("global_enabled", True)
                save_config(config)
                status = "开启" if config["global_enabled"] else "关闭"
                dictTValue_local['tContent'] = status
                dictTValue_local['tStatus'] = 'AI功能'
                tmp_reply_str = format_reply_str(dictStrCustom.get('strToggleStatus', '{function}功能已{status}'), dictTValue_local)
                plugin_event.reply(tmp_reply_str)
                return
            elif toggle_type == 'review':
                config["enable_review"] = not config.get("enable_review", False)
                save_config(config)
                status = "开启" if config["enable_review"] else "关闭"
                dictTValue_local['tContent'] = status
                dictTValue_local['tStatus'] = '二次审核'
                tmp_reply_str = format_reply_str(dictStrCustom.get('strToggleStatus', '{function}功能已{status}'), dictTValue_local)
                plugin_event.reply(tmp_reply_str)
                return
        
        elif command == 'ban':
            if not is_master:
                plugin_event.reply(dictStrCustom.get('strNoPermission', '权限不足，无法执行此操作'))
                return
            if len(parts) < 3:
                dictTValue_local['tContent'] = dictStrCustom.get('strBanUsage', '.deepseek ban [add|remove|list|clear|toggle]')
                tmp_reply_str = format_reply_str(dictStrCustom.get('strBanCommandUsage', '使用: {command_usage}'), dictTValue_local)
                plugin_event.reply(tmp_reply_str)
                return
            sub_command = parts[2]
            if sub_command == 'add' and len(parts) >= 4:
                word_to_add = ' '.join(parts[3:])
                banned_words_data = load_banned_words()
                if word_to_add not in banned_words_data.get("words", []):
                    banned_words_data["words"].append(word_to_add)
                    save_banned_words(banned_words_data)
                    dictTValue_local['tContent'] = word_to_add
                    tmp_reply_str = format_reply_str(dictStrCustom.get('strBanAddSuccess', '已添加违禁词: {tContent}'), dictTValue_local)
                    plugin_event.reply(tmp_reply_str)
                else:
                    plugin_event.reply(dictStrCustom.get('strBannedWordExists', '该违禁词已存在'))
                return
            elif sub_command == 'remove' and len(parts) >= 4:
                word_to_remove = ' '.join(parts[3:])
                banned_words_data = load_banned_words()
                if word_to_remove in banned_words_data.get("words", []):
                    banned_words_data["words"].remove(word_to_remove)
                    save_banned_words(banned_words_data)
                    dictTValue_local['tContent'] = word_to_remove
                    tmp_reply_str = format_reply_str(dictStrCustom.get('strBanRemoveSuccess', '已移除违禁词: {tContent}'), dictTValue_local)
                    plugin_event.reply(tmp_reply_str)
                else:
                    plugin_event.reply(dictStrCustom.get('strBanRemoveFailed', '移除违禁词失败，该词语不存在'))
                return
            elif sub_command == 'list':
                banned_words_data = load_banned_words()
                words = banned_words_data.get("words", [])
                if words:
                    word_items = "\n".join([f"{i+1}. {word}" for i, word in enumerate(words)])
                    ban_list = dictStrCustom.get('strBanList', '违禁词列表:\n{word_items}').replace('{word_items}', word_items)
                    plugin_event.reply(ban_list)
                else:
                    plugin_event.reply(dictStrCustom.get('strBanListEmpty', '违禁词库为空'))
                return
            elif sub_command == 'clear':
                banned_words_data = load_banned_words()
                banned_words_data["words"] = []
                save_banned_words(banned_words_data)
                plugin_event.reply(dictStrCustom.get('strBanClearSuccess', '已清空违禁词库'))
                return
            elif sub_command == 'toggle':
                banned_words_data = load_banned_words()
                banned_words_data["enable_filter"] = not banned_words_data.get("enable_filter", True)
                save_banned_words(banned_words_data)
                status = "开启" if banned_words_data["enable_filter"] else "关闭"
                dictTValue_local['tContent'] = status
                dictTValue_local['tStatus'] = '违禁词过滤'
                tmp_reply_str = format_reply_str(dictStrCustom.get('strToggleStatus', '{function}功能已{status}'), dictTValue_local)
                plugin_event.reply(tmp_reply_str)
                return
            else:
                dictTValue_local['tContent'] = 'add, remove, list, clear, toggle'
                tmp_reply_str = format_reply_str(dictStrCustom.get('strUnknownSubCommand', '未知子命令，可用: {available_commands}'), dictTValue_local)
                plugin_event.reply(tmp_reply_str)
                return
        
        elif command == 'clean':
            if not is_master:
                plugin_event.reply(dictStrCustom.get('strNoPermission', '权限不足，无法执行此操作'))
                return
            if len(parts) < 3:
                dictTValue_local['tContent'] = dictStrCustom.get('strCleanUsage', '.deepseek clean [all|before|users]')
                tmp_reply_str = format_reply_str(dictStrCustom.get('strCleanCommandUsage', '使用: {command_usage}'), dictTValue_local)
                plugin_event.reply(tmp_reply_str)
                return
            sub_command = parts[2]
            if sub_command == 'all':
                sessions_dir = os.path.join(data_dir, 'sessions')
                cleaned_count = 0
                if os.path.exists(sessions_dir):
                    for filename in os.listdir(sessions_dir):
                        if filename.startswith('session_') and filename.endswith('.json'):
                            os.remove(os.path.join(sessions_dir, filename))
                            cleaned_count += 1
                dictTValue_local['tContent'] = str(cleaned_count)
                tmp_reply_str = format_reply_str(dictStrCustom.get('strCleanAllSuccess', '已清理所有用户会话记录，共 {tContent} 个'), dictTValue_local)
                plugin_event.reply(tmp_reply_str)
                return
            elif sub_command == 'before' and len(parts) >= 4:
                try:
                    days = int(parts[3])
                    cutoff_time = time.time() - days * 24 * 3600
                    cleaned_count = 0
                    sessions_dir = os.path.join(data_dir, 'sessions')
                    if os.path.exists(sessions_dir):
                        for filename in os.listdir(sessions_dir):
                            if filename.startswith('session_') and filename.endswith('.json'):
                                filepath = os.path.join(sessions_dir, filename)
                                try:
                                    with open(filepath, 'r', encoding='utf-8') as f:
                                        session_data = json.load(f)
                                    if session_data.get("last_active", 0) < cutoff_time:
                                        os.remove(filepath)
                                        cleaned_count += 1
                                except:
                                    pass
                    dictTValue_local['tContent'] = str(days)
                    dictTValue_local['tCount'] = str(cleaned_count)
                    tmp_reply_str = format_reply_str(dictStrCustom.get('strCleanBeforeSuccess', '已清理 {tContent} 天前的会话记录，共 {tCount} 个'), dictTValue_local)
                    plugin_event.reply(tmp_reply_str)
                except:
                    plugin_event.reply(dictStrCustom.get('strInvalidDays', '参数错误，请输入天数数字'))
                return
            elif sub_command == 'users' and len(parts) >= 4:
                try:
                    user_count = int(parts[3])
                    user_ids = get_all_users()
                    cleaned_count = 0
                    for i, user_id in enumerate(user_ids):
                        if i >= user_count:
                            break
                        if clear_user_session(user_id):
                            cleaned_count += 1
                    dictTValue_local['tContent'] = str(user_count)
                    dictTValue_local['tCount'] = str(cleaned_count)
                    tmp_reply_str = format_reply_str(dictStrCustom.get('strCleanUsersSuccess', '已清理最早 {tContent} 个用户的会话记录'), dictTValue_local)
                    plugin_event.reply(tmp_reply_str)
                except:
                    plugin_event.reply(dictStrCustom.get('strInvalidUserCount', '参数错误，请输入用户数量数字'))
                return
            else:
                dictTValue_local['tContent'] = 'all, before, users'
                tmp_reply_str = format_reply_str(dictStrCustom.get('strUnknownSubCommand', '未知子命令，可用: {available_commands}'), dictTValue_local)
                plugin_event.reply(tmp_reply_str)
                return
        
        elif command == 'reset':
            if not is_master:
                plugin_event.reply(dictStrCustom.get('strNoPermission', '权限不足，无法执行此操作'))
                return
            save_config(default_config)
            save_banned_words(default_banned_words)
            plugin_event.reply(dictStrCustom.get('strConfigReset', '系统配置已重置为默认值'))
            return
        
        elif command == 'cleanup':
            if not is_master:
                plugin_event.reply(dictStrCustom.get('strNoPermission', '权限不足，无法执行此操作'))
                return
            cutoff_time = time.time() - 30 * 24 * 3600
            cleaned_count = 0
            sessions_dir = os.path.join(data_dir, 'sessions')
            if os.path.exists(sessions_dir):
                for filename in os.listdir(sessions_dir):
                    if filename.startswith('session_') and filename.endswith('.json'):
                        filepath = os.path.join(sessions_dir, filename)
                        try:
                            with open(filepath, 'r', encoding='utf-8') as f:
                                session_data = json.load(f)
                            if session_data.get("last_active", 0) < cutoff_time:
                                os.remove(filepath)
                                cleaned_count += 1
                        except:
                            pass
            dictTValue_local['tContent'] = str(cleaned_count)
            tmp_reply_str = format_reply_str(dictStrCustom.get('strCleanupResult', '已清理 {cleaned_count} 个过期会话'), dictTValue_local)
            plugin_event.reply(tmp_reply_str)
            return
        
        else:
            dictTValue_local['tContent'] = '.deepseek help'
            tmp_reply_str = format_reply_str(dictStrCustom.get('strUnknownCommand', '未知命令，使用 {help_command} 查看帮助'), dictTValue_local)
            plugin_event.reply(tmp_reply_str)
            return
    
    elif tmp_reast_str.startswith('.chat'):
        parts = tmp_reast_str.split()
        if len(parts) < 2:
            dictTValue_local['tContent'] = '.chat help'
            tmp_reply_str = format_reply_str(dictStrCustom.get('strFormatError', '格式错误，使用 {help_command} 查看帮助'), dictTValue_local)
            plugin_event.reply(tmp_reply_str)
            return
        sub_command = parts[1]
        
        if sub_command == 'help':
            dictTValue_local['tCooldown'] = str(config["cooldown_time"])
            dictTValue_local['tContext'] = str(config["max_context"])
            tmp_reply_str = format_reply_str(dictStrCustom.get('strHelpCommon', '帮助信息未定义'), dictTValue_local)
            plugin_event.reply(tmp_reply_str)
            return
        
        elif sub_command == 'toggle':
            if plugin_event.plugin_info['func_type'] != 'group_message':
                plugin_event.reply(dictStrCustom.get('strPermissionOwnerAdminOnly', '此功能仅限群主和管理员在本群使用'))
                return
            group_id = plugin_event.data.group_id
            if len(parts) >= 3:
                toggle_value = parts[2].lower()
                if toggle_value not in ['on', 'off']:
                    plugin_event.reply(dictStrCustom.get('strInvalidToggleValue', '参数错误，请输入 on 或 off'))
                    return
                enable = toggle_value == 'on'
                success, message = toggle_group_ai(plugin_event, group_id, enable)
                plugin_event.reply(message)
            else:
                group_config = get_group_config(group_id)
                current_status = '开启' if group_config.get("enable_ai", True) else '关闭'
                plugin_event.reply(f"本群AI功能当前状态：{current_status}\n使用 .chat toggle on/off 来开关")
            return
        
        elif sub_command == 'status':
            if plugin_event.plugin_info['func_type'] != 'group_message':
                plugin_event.reply(dictStrCustom.get('strPermissionOwnerAdminOnly', '此功能仅限群主和管理员在本群使用'))
                return
            group_id = plugin_event.data.group_id
            group_config = get_group_config(group_id)
            ai_status = '开启' if group_config.get("enable_ai", True) else '关闭'
            allow_ordinary = '允许' if group_config.get("allow_ordinary", False) else '禁止'
            last_op_time = '从未操作'
            if group_config.get("last_toggle_time", 0) > 0:
                last_op_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(group_config["last_toggle_time"]))
            operator_id = group_config.get("toggled_by", "未知")
            operator_type = group_config.get("toggled_by_type", "未知")
            status_text = f"本群AI状态：\n"
            status_text += f"├─ 功能状态：{ai_status}\n"
            status_text += f"├─ 允许普通成员：{allow_ordinary}\n"
            status_text += f"├─ 最后操作时间：{last_op_time}\n"
            status_text += f"├─ 操作者：{operator_type}\n"
            status_text += f"└─ 操作者ID：{operator_id}"
            plugin_event.reply(status_text)
            return
        
        elif sub_command == 'allow' or sub_command == 'deny':
            if plugin_event.plugin_info['func_type'] != 'group_message':
                plugin_event.reply(dictStrCustom.get('strPermissionOwnerAdminOnly', '此功能仅限群主和管理员在本群使用'))
                return
            group_id = plugin_event.data.group_id
            if sub_command == 'allow':
                success, message = toggle_group_ordinary_permission(plugin_event, group_id, True)
                plugin_event.reply(message)
                return
            elif sub_command == 'deny':
                success, message = toggle_group_ordinary_permission(plugin_event, group_id, False)
                plugin_event.reply(message)
                return
        
        elif sub_command == 'clear':
            if len(parts) == 2:
                if clear_user_session(tmp_userID):
                    plugin_event.reply(dictStrCustom.get('strClearSuccess', '已清空你的会话记录'))
                else:
                    plugin_event.reply(dictStrCustom.get('strClearFailed', '清空会话记录失败'))
                return
            elif len(parts) >= 3:
                clear_type = parts[2]
                user_data = load_user_data(tmp_userID)
                if clear_type == 'system':
                    user_data["system_prompt"] = ""
                    save_user_data(tmp_userID, user_data)
                    plugin_event.reply(dictStrCustom.get('strPersonalSystemCleared', '个人系统提示词已清空'))
                    return
                else:
                    dictTValue_local['tContent'] = 'system'
                    tmp_reply_str = format_reply_str(dictStrCustom.get('strClearTypeError', '未知清除类型，可用: {available_types}'), dictTValue_local)
                    plugin_event.reply(tmp_reply_str)
                    return
            else:
                dictTValue_local['tContent'] = '.chat clear 或 .chat clear system'
                tmp_reply_str = format_reply_str(dictStrCustom.get('strClearFormatError', '格式错误，正确格式: {correct_format}'), dictTValue_local)
                plugin_event.reply(tmp_reply_str)
                return
        
        elif sub_command == 'config' or sub_command == 'myconfig':
            user_data = load_user_data(tmp_userID)
            dictTValue_local['tPersonalSystem'] = user_data.get("system_prompt", "未设置")
            dictTValue_local['tUseCount'] = str(user_data["use_count"])
            if user_data["last_used"]:
                dictTValue_local['tLastUsed'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(user_data["last_used"]))
            else:
                dictTValue_local['tLastUsed'] = '从未使用'
            tmp_reply_str = format_reply_str(dictStrCustom.get('strPersonalConfig', '个人配置信息未定义'), dictTValue_local)
            plugin_event.reply(tmp_reply_str)
            return
        
        elif sub_command == 'show':
            if len(parts) >= 3:
                show_type = parts[2]
                user_data = load_user_data(tmp_userID)
                if show_type == 'system':
                    content = user_data.get("system_prompt", "未设置")
                    dictTValue_local['tContent'] = content
                    tmp_reply_str = format_reply_str(dictStrCustom.get('strPersonalSystem', '个人系统提示词: {tContent}'), dictTValue_local)
                    plugin_event.reply(tmp_reply_str)
                    return
                else:
                    dictTValue_local['tContent'] = 'system'
                    tmp_reply_str = format_reply_str(dictStrCustom.get('strShowTypeError', '未知显示类型，可用: {available_types}'), dictTValue_local)
                    plugin_event.reply(tmp_reply_str)
                    return
            else:
                dictTValue_local['tContent'] = '.chat show system'
                tmp_reply_str = format_reply_str(dictStrCustom.get('strShowFormatError', '格式错误，正确格式: {correct_format}'), dictTValue_local)
                plugin_event.reply(tmp_reply_str)
                return
        
        elif sub_command == 'set':
            if len(parts) >= 4:
                set_type = parts[2]
                set_value = ' '.join(parts[3:])
                if not set_value:
                    plugin_event.reply(dictStrCustom.get('strNoContent', '内容不能为空'))
                    return
                user_data = load_user_data(tmp_userID)
                if set_type == 'system':
                    max_chars = config.get("max_system_chars", 1000)
                    if len(set_value) > max_chars:
                        dictTValue_local['tMaxChars'] = str(max_chars)
                        dictTValue_local['tCurrentChars'] = str(len(set_value))
                        tmp_reply_str = format_reply_str(dictStrCustom.get('strSystemTooLong', '系统提示词过长，最大允许 {tMaxChars} 字符，当前 {tCurrentChars} 字符'), dictTValue_local)
                        plugin_event.reply(tmp_reply_str)
                        return
                    user_data["system_prompt"] = set_value
                    save_user_data(tmp_userID, user_data)
                    plugin_event.reply(dictStrCustom.get('strPersonalSystemSet', '个人系统提示词已设置'))
                    return
                else:
                    dictTValue_local['tContent'] = 'system'
                    tmp_reply_str = format_reply_str(dictStrCustom.get('strSetTypeError', '未知设置类型，可用: {available_types}'), dictTValue_local)
                    plugin_event.reply(tmp_reply_str)
                    return
            else:
                dictTValue_local['tContent'] = '.chat set system <内容>'
                tmp_reply_str = format_reply_str(dictStrCustom.get('strSetFormatError', '格式错误，正确格式: {correct_format}'), dictTValue_local)
                plugin_event.reply(tmp_reply_str)
                return
        
        else:
            dictTValue_local['tContent'] = '.chat help'
            tmp_reply_str = format_reply_str(dictStrCustom.get('strUnknownCommand', '未知命令，使用 {help_command} 查看帮助'), dictTValue_local)
            plugin_event.reply(tmp_reply_str)
            return
    
    elif tmp_reast_str.startswith('#chat'):
        if not config["api_key"]:
            plugin_event.reply(dictStrCustom.get('strApiKeyNotSet', 'API Key未配置，请联系管理员'))
            return
        if not config.get("global_enabled", True):
            plugin_event.reply(dictStrCustom.get('strGlobalDisabled', 'AI功能暂时关闭，请联系管理员'))
            return
        if config.get("enable_review", False):
            plugin_event.reply(dictStrCustom.get('strReviewProcessing', '已开启二次审核，生成时间可能略长，请耐心等待'))
        if plugin_event.plugin_info['func_type'] == 'group_message' and not config["enable_group"]:
            return
        if plugin_event.plugin_info['func_type'] == 'private_message' and not config["enable_private"]:
            return
        user_data = load_user_data(tmp_userID)
        if user_data["is_locked"]:
            plugin_event.reply(dictStrCustom.get('strUserLocked', 'AI功能对你禁用，请联系管理员'))
            return
        banned_word = check_banned_words(tmp_reast_str)
        if banned_word:
            plugin_event.reply(dictStrCustom.get('strBannedWordFound', '内容包含违禁词汇，请修改后重新发送'))
            return
        cooldown_remaining = check_cooldown(tmp_userID)
        if cooldown_remaining > 0:
            dictTValue_local['tContent'] = str(cooldown_remaining)
            tmp_reply_str = format_reply_str(dictStrCustom.get('strCooldown', '系统冷却中，请等待 {tContent} 秒后重试'), dictTValue_local)
            plugin_event.reply(tmp_reply_str)
            return
        prompt = tmp_reast_str[5:].strip()
        if not prompt:
            plugin_event.reply(dictStrCustom.get('strNoContent', '内容不能为空'))
            return
        banned_word = check_banned_words(prompt)
        if banned_word:
            plugin_event.reply(dictStrCustom.get('strBannedWordFound', '内容包含违禁词汇，请修改后重新发送'))
            return
        
        if plugin_event.plugin_info['func_type'] == 'group_message':
            group_id = plugin_event.data.group_id
            has_permission, reason = check_group_ai_permission(plugin_event, group_id)
            if not has_permission:
                plugin_event.reply(reason)
                return
        
        response = call_deepseek_api(prompt, tmp_userID, plugin_event)
        if response:
            plugin_event.reply(response)
        else:
            plugin_event.reply(dictStrCustom.get('strAPICallFailed', 'AI服务暂时不可用，请稍后再试'))
        return

class Event(object):
    def init(plugin_event, Proc):
        pass

    def init_after(plugin_event, Proc):
        pass

    def private_message(plugin_event, Proc):
        unity_reply(plugin_event, Proc)

    def group_message(plugin_event, Proc):
        unity_reply(plugin_event, Proc)

    def poke(plugin_event, Proc):
        pass
    
    def menu(plugin_event, Proc):
        pass
