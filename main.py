import OlivOS
import json
import os
import time
import requests
from collections import deque

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
    "default_prompt": "你是一个有用的助手",
    "system_prompt": "",
    "global_enabled": True,
    "enable_filter": True,
    "enable_review": False
}

default_banned_words = {
    "words": [],
    "enable_filter": True
}

dictStrCustom = {
    'strCooldown': '系统冷却中，请等待 {tContent} 秒后重试',
    'strUserLocked': 'AI功能对你禁用，请联系管理员',
    'strNoContent': '内容不能为空',
    'strHelpCommon': '''【DeepSeek AI 聊天助手】
使用 #chat [内容] 与AI对话
.chat help - 查看帮助信息
.chat clear - 清空自己的会话记录
.chat config - 查看个人设置
.chat show prompt - 查看个人预设提示词
.chat show system - 查看个人系统提示词
.chat set prompt <内容> - 设置个人预设提示词
.chat set system <内容> - 设置个人系统提示词
.chat clear prompt - 清空个人预设提示词
.chat clear system - 清空个人系统提示词
系统冷却时间: {tCooldown}秒
上下文记忆: {tContext}段''',
    'strHelpMaster': '''【DeepSeek AI 管理指令】
👥 用户管理:
.deepseek users - 查看用户列表
.deepseek user <用户ID> - 查看用户详情
.deepseek user lock <用户ID> - 锁定用户
.deepseek user unlock <用户ID> - 解锁用户
.deepseek user clear <用户ID> - 清空用户记录

⚙️ 系统配置:
.deepseek set cooldown <秒数> - 设置冷却时间
.deepseek set context <段数> - 设置上下文限制
.deepseek set prefix <前缀> - 设置触发前缀
.deepseek set tokens <数量> - 设置最大token数
.deepseek set temperature <数值> - 设置温度参数
.deepseek set model <模型名> - 设置AI模型
.deepseek set apikey <key> - 设置API Key
.deepseek set endpoint <url> - 设置API端点
.deepseek set prompt <预设内容> - 设置公共预设提示词
.deepseek set system <内容> - 设置公共系统提示词

🔧 功能开关:
.deepseek toggle group - 切换群聊功能
.deepseek toggle private - 切换私聊功能
.deepseek toggle debug - 切换Debug模式
.deepseek toggle filter - 切换违禁词过滤
.deepseek toggle global - 切换全局AI功能
.deepseek toggle review - 切换二次内容审核

🛠️ 违禁词管理:
.deepseek ban add <词语> - 添加违禁词
.deepseek ban remove <词语> - 移除违禁词
.deepseek ban list - 查看违禁词列表
.deepseek ban clear - 清空违禁词库
.deepseek ban toggle - 开关违禁词过滤

🗑️ 数据清理:
.deepseek clean all - 清理所有用户会话记录
.deepseek clean before <天数> - 清理指定天数前的记录
.deepseek clean users <数量> - 清理最早N个用户记录

🛠️ 系统维护:
.deepseek reset - 重置系统配置
.deepseek cleanup - 清理过期数据
.deepseek status - 查看系统状态
.deepseek config - 查看详细配置
.deepseek prompt - 查看当前公共预设
.deepseek system - 查看当前公共系统提示词''',
    'strNoPermission': '权限不足，无法执行此操作',
    'strConfigUpdated': '配置已更新: {tContent}',
    'strUserNotFound': '用户不存在',
    'strUserLockedSuccess': '用户 {tTargetName} 已锁定',
    'strUserUnlockedSuccess': '用户 {tTargetName} 已解锁',
    'strUserClearedSuccess': '用户 {tTargetName} 记录已清空',
    'strUserDetail': '''用户详情:
用户ID: {tTargetName}
使用次数: {tUseCount}
最后使用: {tLastUsed}
状态: {tStatus}''',
    'strSystemStatus': '''系统状态:
用户总数: {tUserCount}
群聊功能: {tGroupStatus}
私聊功能: {tPrivateStatus}
冷却时间: {tCooldown}秒
上下文限制: {tContext}段
Debug模式: {tDebugStatus}
违禁词过滤: {tFilterStatus}
全局AI功能: {tGlobalStatus}
二次审核: {tReviewStatus}
公共预设: {tDefaultPrompt}
公共系统提示词: {tSystemPrompt}''',
    'strAPICallFailed': 'AI服务暂时不可用，请稍后再试',
    'strDebugInfo': 'Debug信息: {tContent}',
    'strClearSuccess': '已清空你的会话记录',
    'strClearFailed': '清空会话记录失败',
    'strBannedWordFound': '内容包含违禁词汇，请修改后重新发送',
    'strBanAddSuccess': '已添加违禁词: {tContent}',
    'strBanAddFailed': '添加违禁词失败',
    'strBanRemoveSuccess': '已移除违禁词: {tContent}',
    'strBanRemoveFailed': '移除违禁词失败，该词语不存在',
    'strBanListEmpty': '违禁词库为空',
    'strBanClearSuccess': '已清空违禁词库',
    'strBanToggleSuccess': '违禁词过滤已{tContent}',
    'strPromptUpdated': '公共预设已更新',
    'strSystemPromptUpdated': '公共系统提示词已更新',
    'strSystemPromptCleared': '公共系统提示词已清空',
    'strCurrentPrompt': '当前公共预设: {tContent}',
    'strCurrentSystem': '当前公共系统提示词: {tContent}',
    'strPersonalConfig': '''你的个人设置:
预设提示词: {tPersonalPrompt}
系统提示词: {tPersonalSystem}
使用次数: {tUseCount}
最后使用: {tLastUsed}''',
    'strPersonalPrompt': '个人预设提示词: {tContent}',
    'strPersonalSystem': '个人系统提示词: {tContent}',
    'strPersonalPromptSet': '个人预设提示词已设置',
    'strPersonalSystemSet': '个人系统提示词已设置',
    'strPersonalPromptCleared': '个人预设提示词已清空',
    'strPersonalSystemCleared': '个人系统提示词已清空',
    'strGlobalDisabled': 'AI功能暂时关闭，请联系管理员',
    'strGlobalEnabled': 'AI功能已{tContent}',
    'strReviewEnabled': '二次审核功能已{tContent}',
    'strReviewConfirm': '开启后会增加tokens消耗量，是否确认开启？请再次输入 .deepseek toggle review 确认',
    'strReviewProcessing': '已开启二次审核，生成时间可能略长，请耐心等待',
    'strReviewBlocked': '⚠️ 内容包含违规信息，用户已被锁定',
    'strReviewFailed': '⚠️ 内容审核失败，请稍后重试',
    'strCleanAllSuccess': '已清理所有用户会话记录，共 {tContent} 个',
    'strCleanBeforeSuccess': '已清理 {tContent} 天前的会话记录，共 {tCount} 个',
    'strCleanUsersSuccess': '已清理最早 {tContent} 个用户的会话记录'
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
    'tDefaultPrompt': '你是一个有用的助手',
    'tSystemPrompt': '未设置',
    'tPersonalPrompt': '未设置',
    'tPersonalSystem': '未设置',
    'tCount': '0'
}

MASTER_USERS = ['2139497594']

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
        "custom_prompt": "",
        "system_prompt": "",
        "is_locked": False,
        "use_count": 0,
        "last_used": None
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
        "history": deque(maxlen=config["max_context"]),
        "last_active": None
    }
    if not os.path.exists(session_file):
        save_session_data(user_id, default_session)
        return default_session
    try:
        with open(session_file, 'r', encoding='utf-8') as f:
            session_data = json.load(f)
            session_data["history"] = deque(session_data.get("history", []), maxlen=config["max_context"])
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

def format_reply_str(reply_str, dictTValue):
    for key in dictTValue:
        reply_str = reply_str.replace('{' + key + '}', str(dictTValue[key]))
    return reply_str

def is_master_user(user_id):
    return str(user_id) in MASTER_USERS

def clear_user_session(user_id):
    try:
        session_file = get_session_file(user_id)
        if os.path.exists(session_file):
            os.remove(session_file)
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

def build_messages(user_input, user_id):
    config = load_config()
    user_data = load_user_data(user_id)
    
    messages = []
    
    system_content = user_data.get("system_prompt", "")
    if not system_content:
        system_content = config.get("system_prompt", "")
    
    if system_content:
        messages.append({"role": "system", "content": system_content})
    
    session_data = load_session_data(user_id)
    messages.extend(list(session_data["history"]))
    
    preset_content = user_data.get("custom_prompt", "")
    if not preset_content:
        preset_content = config.get("default_prompt", "")
    
    if preset_content:
        messages.append({"role": "user", "content": preset_content})
    
    messages.append({"role": "user", "content": user_input})
    
    return messages

def unity_reply(plugin_event):
    config = load_config()
    banned_words_data = load_banned_words()
    
    tmp_reast_str = plugin_event.data.message
    tmp_userID = plugin_event.data.user_id
    
    dictTValue_local = dictTValue.copy()
    dictTValue_local['tUserName'] = plugin_event.data.sender.get('name', '用户')
    
    def call_deepseek_api(prompt, user_id):
        try:
            user_data = load_user_data(user_id)
            
            messages = build_messages(prompt, user_id)
            
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
                        return dictStrCustom['strReviewBlocked']
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
                        return dictStrCustom['strReviewFailed']
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

    def check_cooldown(user_id):
        user_data = load_user_data(user_id)
        if user_data["last_used"]:
            current_time = time.time()
            cooldown_end = user_data["last_used"] + config["cooldown_time"]
            if current_time < cooldown_end:
                return int(cooldown_end - current_time)
        return 0
    
    # 先处理管理员指令
    if tmp_reast_str.startswith('.deepseek'):
        is_master = is_master_user(tmp_userID)
        
        parts = tmp_reast_str.split()
        if len(parts) < 2:
            plugin_event.reply("使用 .deepseek help 查看帮助")
            return
        
        command = parts[1]
        
        if command == 'help':
            if not is_master:
                plugin_event.reply(dictStrCustom['strNoPermission'])
                return
            plugin_event.reply(dictStrCustom['strHelpMaster'])
            return
        
        elif command == 'status':
            if not is_master:
                plugin_event.reply(dictStrCustom['strNoPermission'])
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
            dictTValue_local['tDefaultPrompt'] = config.get("default_prompt", "你是一个有用的助手")[:50] + ("..." if len(config.get("default_prompt", "")) > 50 else "")
            dictTValue_local['tSystemPrompt'] = config.get("system_prompt", "未设置")[:50] + ("..." if len(config.get("system_prompt", "")) > 50 else "")
            tmp_reply_str = format_reply_str(dictStrCustom['strSystemStatus'], dictTValue_local)
            plugin_event.reply(tmp_reply_str)
            return
        
        elif command == 'config':
            if not is_master:
                plugin_event.reply(dictStrCustom['strNoPermission'])
                return
            config_info = f'''当前配置:
冷却时间: {config["cooldown_time"]}秒
上下文限制: {config["max_context"]}段
触发前缀: {config["trigger_prefix"]}
最大Token: {config["max_tokens"]}
温度参数: {config["temperature"]}
AI模型: {config["default_model"]}
API端点: {config["api_endpoint"]}
群聊功能: {'开启' if config["enable_group"] else '关闭'}
私聊功能: {'开启' if config["enable_private"] else '关闭'}
Debug模式: {'开启' if config["debug_mode"] else '关闭'}
违禁词过滤: {'开启' if banned_words_data.get("enable_filter", True) else '关闭'}
全局AI功能: {'开启' if config.get("global_enabled", True) else '关闭'}
公共预设: {config.get("default_prompt", "你是一个有用的助手")[:100]}{'...' if len(config.get("default_prompt", "")) > 100 else ''}
公共系统提示词: {config.get("system_prompt", "未设置")[:100]}{'...' if len(config.get("system_prompt", "")) > 100 else ''}'''
            plugin_event.reply(config_info)
            return
        
        elif command == 'prompt':
            if not is_master:
                plugin_event.reply(dictStrCustom['strNoPermission'])
                return
            current_prompt = config.get("default_prompt", "你是一个有用的助手")
            dictTValue_local['tContent'] = current_prompt
            tmp_reply_str = format_reply_str(dictStrCustom['strCurrentPrompt'], dictTValue_local)
            plugin_event.reply(tmp_reply_str)
            return
        
        elif command == 'system':
            if not is_master:
                plugin_event.reply(dictStrCustom['strNoPermission'])
                return
            current_system = config.get("system_prompt", "未设置")
            dictTValue_local['tContent'] = current_system
            tmp_reply_str = format_reply_str(dictStrCustom['strCurrentSystem'], dictTValue_local)
            plugin_event.reply(tmp_reply_str)
            return
        
        elif command == 'users':
            if not is_master:
                plugin_event.reply(dictStrCustom['strNoPermission'])
                return
            user_ids = get_all_users()
            if user_ids:
                user_list = "用户列表:\n" + "\n".join([f"- {uid}" for uid in user_ids[:20]])
                if len(user_ids) > 20:
                    user_list += f"\n... 还有 {len(user_ids) - 20} 个用户"
                plugin_event.reply(user_list)
            else:
                plugin_event.reply("暂无用户数据")
            return
        
        elif command == 'user':
            if not is_master:
                plugin_event.reply(dictStrCustom['strNoPermission'])
                return
            
            if len(parts) < 3:
                plugin_event.reply("请指定用户ID，例如: .deepseek user 123456")
                return
            
            if len(parts) >= 4:
                sub_command = parts[2]
                target_user_id = parts[3]
                
                if sub_command == 'lock':
                    user_data = load_user_data(target_user_id)
                    user_data["is_locked"] = True
                    save_user_data(target_user_id, user_data)
                    dictTValue_local['tTargetName'] = target_user_id
                    tmp_reply_str = format_reply_str(dictStrCustom['strUserLockedSuccess'], dictTValue_local)
                    plugin_event.reply(tmp_reply_str)
                    return
                
                elif sub_command == 'unlock':
                    user_data = load_user_data(target_user_id)
                    user_data["is_locked"] = False
                    save_user_data(target_user_id, user_data)
                    dictTValue_local['tTargetName'] = target_user_id
                    tmp_reply_str = format_reply_str(dictStrCustom['strUserUnlockedSuccess'], dictTValue_local)
                    plugin_event.reply(tmp_reply_str)
                    return
                
                elif sub_command == 'clear':
                    if clear_user_session(target_user_id):
                        dictTValue_local['tTargetName'] = target_user_id
                        tmp_reply_str = format_reply_str(dictStrCustom['strUserClearedSuccess'], dictTValue_local)
                        plugin_event.reply(tmp_reply_str)
                    else:
                        plugin_event.reply("清空用户记录失败")
                    return
                else:
                    plugin_event.reply("未知子命令，可用: lock, unlock, clear")
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
                tmp_reply_str = format_reply_str(dictStrCustom['strUserDetail'], dictTValue_local)
                plugin_event.reply(tmp_reply_str)
                return
        
        elif command == 'set' and len(parts) >= 4:
            if not is_master:
                plugin_event.reply(dictStrCustom['strNoPermission'])
                return
            
            set_type = parts[2]
            set_value = ' '.join(parts[3:])
            
            if set_type == 'cooldown':
                try:
                    value = int(set_value)
                    config["cooldown_time"] = value
                    save_config(config)
                    dictTValue_local['tContent'] = f"冷却时间设置为 {value} 秒"
                    tmp_reply_str = format_reply_str(dictStrCustom['strConfigUpdated'], dictTValue_local)
                    plugin_event.reply(tmp_reply_str)
                except:
                    plugin_event.reply("参数错误，请输入数字")
                return
            
            elif set_type == 'context':
                try:
                    value = int(set_value)
                    config["max_context"] = value
                    save_config(config)
                    dictTValue_local['tContent'] = f"上下文限制设置为 {value} 段"
                    tmp_reply_str = format_reply_str(dictStrCustom['strConfigUpdated'], dictTValue_local)
                    plugin_event.reply(tmp_reply_str)
                except:
                    plugin_event.reply("参数错误，请输入数字")
                return
            
            elif set_type == 'prefix':
                config["trigger_prefix"] = set_value
                save_config(config)
                dictTValue_local['tContent'] = f"触发前缀设置为 {set_value}"
                tmp_reply_str = format_reply_str(dictStrCustom['strConfigUpdated'], dictTValue_local)
                plugin_event.reply(tmp_reply_str)
                return
            
            elif set_type == 'tokens':
                try:
                    value = int(set_value)
                    config["max_tokens"] = value
                    save_config(config)
                    dictTValue_local['tContent'] = f"最大Token数设置为 {value}"
                    tmp_reply_str = format_reply_str(dictStrCustom['strConfigUpdated'], dictTValue_local)
                    plugin_event.reply(tmp_reply_str)
                except:
                    plugin_event.reply("参数错误，请输入数字")
                return
            
            elif set_type == 'temperature':
                try:
                    value = float(set_value)
                    config["temperature"] = value
                    save_config(config)
                    dictTValue_local['tContent'] = f"温度参数设置为 {value}"
                    tmp_reply_str = format_reply_str(dictStrCustom['strConfigUpdated'], dictTValue_local)
                    plugin_event.reply(tmp_reply_str)
                except:
                    plugin_event.reply("参数错误，请输入数字")
                return
            
            elif set_type == 'model':
                config["default_model"] = set_value
                save_config(config)
                dictTValue_local['tContent'] = f"AI模型设置为 {set_value}"
                tmp_reply_str = format_reply_str(dictStrCustom['strConfigUpdated'], dictTValue_local)
                plugin_event.reply(tmp_reply_str)
                return
            
            elif set_type == 'apikey':
                config["api_key"] = set_value
                save_config(config)
                plugin_event.reply("API Key已更新")
                return
            
            elif set_type == 'endpoint':
                config["api_endpoint"] = set_value
                save_config(config)
                dictTValue_local['tContent'] = f"API端点设置为 {set_value}"
                tmp_reply_str = format_reply_str(dictStrCustom['strConfigUpdated'], dictTValue_local)
                plugin_event.reply(tmp_reply_str)
                return
            
            elif set_type == 'prompt':
                config["default_prompt"] = set_value
                save_config(config)
                plugin_event.reply(dictStrCustom['strPromptUpdated'])
                return
            
            elif set_type == 'system':
                config["system_prompt"] = set_value
                save_config(config)
                plugin_event.reply(dictStrCustom['strSystemPromptUpdated'])
                return
        
        elif command == 'toggle' and len(parts) >= 3:
            if not is_master:
                plugin_event.reply(dictStrCustom['strNoPermission'])
                return
            
            toggle_type = parts[2]
            
            if toggle_type == 'group':
                config["enable_group"] = not config["enable_group"]
                save_config(config)
                status = "开启" if config["enable_group"] else "关闭"
                dictTValue_local['tContent'] = f"群聊功能已{status}"
                tmp_reply_str = format_reply_str(dictStrCustom['strConfigUpdated'], dictTValue_local)
                plugin_event.reply(tmp_reply_str)
                return
            
            elif toggle_type == 'private':
                config["enable_private"] = not config["enable_private"]
                save_config(config)
                status = "开启" if config["enable_private"] else "关闭"
                dictTValue_local['tContent'] = f"私聊功能已{status}"
                tmp_reply_str = format_reply_str(dictStrCustom['strConfigUpdated'], dictTValue_local)
                plugin_event.reply(tmp_reply_str)
                return
            
            elif toggle_type == 'debug':
                config["debug_mode"] = not config["debug_mode"]
                save_config(config)
                status = "开启" if config["debug_mode"] else "关闭"
                dictTValue_local['tContent'] = f"Debug模式已{status}"
                tmp_reply_str = format_reply_str(dictStrCustom['strConfigUpdated'], dictTValue_local)
                plugin_event.reply(tmp_reply_str)
                return
            
            elif toggle_type == 'filter':
                banned_words_data["enable_filter"] = not banned_words_data.get("enable_filter", True)
                save_banned_words(banned_words_data)
                status = "开启" if banned_words_data["enable_filter"] else "关闭"
                dictTValue_local['tContent'] = status
                tmp_reply_str = format_reply_str(dictStrCustom['strBanToggleSuccess'], dictTValue_local)
                plugin_event.reply(tmp_reply_str)
                return
            
            elif toggle_type == 'global':
                config["global_enabled"] = not config.get("global_enabled", True)
                save_config(config)
                status = "开启" if config["global_enabled"] else "关闭"
                dictTValue_local['tContent'] = status
                tmp_reply_str = format_reply_str(dictStrCustom['strGlobalEnabled'], dictTValue_local)
                plugin_event.reply(tmp_reply_str)
                return
            
            elif toggle_type == 'review':
                config["enable_review"] = not config.get("enable_review", False)
                save_config(config)
                status = "开启" if config["enable_review"] else "关闭"
                dictTValue_local['tContent'] = f"二次审核已{status}"
                tmp_reply_str = format_reply_str(dictStrCustom['strConfigUpdated'], dictTValue_local)
                plugin_event.reply(tmp_reply_str)
                return
        
        elif command == 'ban':
            if not is_master:
                plugin_event.reply(dictStrCustom['strNoPermission'])
                return
            
            if len(parts) < 3:
                plugin_event.reply("使用: .deepseek ban [add|remove|list|clear|toggle]")
                return
            
            sub_command = parts[2]
            
            if sub_command == 'add' and len(parts) >= 4:
                word_to_add = ' '.join(parts[3:])
                banned_words_data = load_banned_words()
                if word_to_add not in banned_words_data.get("words", []):
                    banned_words_data["words"].append(word_to_add)
                    save_banned_words(banned_words_data)
                    dictTValue_local['tContent'] = word_to_add
                    tmp_reply_str = format_reply_str(dictStrCustom['strBanAddSuccess'], dictTValue_local)
                    plugin_event.reply(tmp_reply_str)
                else:
                    plugin_event.reply("该违禁词已存在")
                return
            
            elif sub_command == 'remove' and len(parts) >= 4:
                word_to_remove = ' '.join(parts[3:])
                banned_words_data = load_banned_words()
                if word_to_remove in banned_words_data.get("words", []):
                    banned_words_data["words"].remove(word_to_remove)
                    save_banned_words(banned_words_data)
                    dictTValue_local['tContent'] = word_to_remove
                    tmp_reply_str = format_reply_str(dictStrCustom['strBanRemoveSuccess'], dictTValue_local)
                    plugin_event.reply(tmp_reply_str)
                else:
                    plugin_event.reply(dictStrCustom['strBanRemoveFailed'])
                return
            
            elif sub_command == 'list':
                banned_words_data = load_banned_words()
                words = banned_words_data.get("words", [])
                if words:
                    word_list = "违禁词列表:\n" + "\n".join([f"{i+1}. {word}" for i, word in enumerate(words)])
                    plugin_event.reply(word_list)
                else:
                    plugin_event.reply(dictStrCustom['strBanListEmpty'])
                return
            
            elif sub_command == 'clear':
                banned_words_data = load_banned_words()
                banned_words_data["words"] = []
                save_banned_words(banned_words_data)
                plugin_event.reply(dictStrCustom['strBanClearSuccess'])
                return
            
            elif sub_command == 'toggle':
                banned_words_data = load_banned_words()
                banned_words_data["enable_filter"] = not banned_words_data.get("enable_filter", True)
                save_banned_words(banned_words_data)
                status = "开启" if banned_words_data["enable_filter"] else "关闭"
                dictTValue_local['tContent'] = status
                tmp_reply_str = format_reply_str(dictStrCustom['strBanToggleSuccess'], dictTValue_local)
                plugin_event.reply(tmp_reply_str)
                return
            
            else:
                plugin_event.reply("未知子命令，可用: add, remove, list, clear, toggle")
                return
        
        elif command == 'clean':
            if not is_master:
                plugin_event.reply(dictStrCustom['strNoPermission'])
                return
            
            if len(parts) < 3:
                plugin_event.reply("使用: .deepseek clean [all|before|users]")
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
                tmp_reply_str = format_reply_str(dictStrCustom['strCleanAllSuccess'], dictTValue_local)
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
                    tmp_reply_str = format_reply_str(dictStrCustom['strCleanBeforeSuccess'], dictTValue_local)
                    plugin_event.reply(tmp_reply_str)
                except:
                    plugin_event.reply("参数错误，请输入天数数字")
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
                    tmp_reply_str = format_reply_str(dictStrCustom['strCleanUsersSuccess'], dictTValue_local)
                    plugin_event.reply(tmp_reply_str)
                except:
                    plugin_event.reply("参数错误，请输入用户数量数字")
                return
            
            else:
                plugin_event.reply("未知子命令，可用: all, before, users")
                return
        
        elif command == 'reset':
            if not is_master:
                plugin_event.reply(dictStrCustom['strNoPermission'])
                return
            save_config(default_config)
            save_banned_words(default_banned_words)
            plugin_event.reply("系统配置已重置为默认值")
            return
        
        elif command == 'cleanup':
            if not is_master:
                plugin_event.reply(dictStrCustom['strNoPermission'])
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
            plugin_event.reply(f"已清理 {cleaned_count} 个过期会话")
            return
        
        else:
            plugin_event.reply("未知命令，使用 .deepseek help 查看帮助")
            return
    
    # 处理用户 .chat 指令 - 重新设计解析逻辑
    elif tmp_reast_str.startswith('.chat'):
        parts = tmp_reast_str.split()
        
        if len(parts) < 2:
            plugin_event.reply("格式错误，使用 .chat help 查看帮助")
            return
        
        sub_command = parts[1]
        
        if sub_command == 'help':
            dictTValue_local['tCooldown'] = str(config["cooldown_time"])
            dictTValue_local['tContext'] = str(config["max_context"])
            tmp_reply_str = format_reply_str(dictStrCustom['strHelpCommon'], dictTValue_local)
            plugin_event.reply(tmp_reply_str)
            return
        
        elif sub_command == 'clear':
            if len(parts) == 2:  # .chat clear（清除会话）
                if clear_user_session(tmp_userID):
                    plugin_event.reply(dictStrCustom['strClearSuccess'])
                else:
                    plugin_event.reply(dictStrCustom['strClearFailed'])
                return
            elif len(parts) >= 3:  # .chat clear prompt/system
                clear_type = parts[2]
                user_data = load_user_data(tmp_userID)
                
                if clear_type == 'prompt':
                    user_data["custom_prompt"] = ""
                    save_user_data(tmp_userID, user_data)
                    plugin_event.reply(dictStrCustom['strPersonalPromptCleared'])
                    return
                elif clear_type == 'system':
                    user_data["system_prompt"] = ""
                    save_user_data(tmp_userID, user_data)
                    plugin_event.reply(dictStrCustom['strPersonalSystemCleared'])
                    return
                else:
                    plugin_event.reply("未知清除类型，可用: prompt, system")
                    return
            else:
                plugin_event.reply("格式错误，正确格式: .chat clear 或 .chat clear prompt/system")
                return
        
        elif sub_command == 'config' or sub_command == 'myconfig':
            user_data = load_user_data(tmp_userID)
            dictTValue_local['tPersonalPrompt'] = user_data.get("custom_prompt", "未设置")
            dictTValue_local['tPersonalSystem'] = user_data.get("system_prompt", "未设置")
            dictTValue_local['tUseCount'] = str(user_data["use_count"])
            if user_data["last_used"]:
                dictTValue_local['tLastUsed'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(user_data["last_used"]))
            else:
                dictTValue_local['tLastUsed'] = '从未使用'
            tmp_reply_str = format_reply_str(dictStrCustom['strPersonalConfig'], dictTValue_local)
            plugin_event.reply(tmp_reply_str)
            return
        
        elif sub_command == 'show':
            if len(parts) >= 3:
                show_type = parts[2]
                user_data = load_user_data(tmp_userID)
                
                if show_type == 'prompt':
                    content = user_data.get("custom_prompt", "未设置")
                    dictTValue_local['tContent'] = content
                    tmp_reply_str = format_reply_str(dictStrCustom['strPersonalPrompt'], dictTValue_local)
                    plugin_event.reply(tmp_reply_str)
                    return
                elif show_type == 'system':
                    content = user_data.get("system_prompt", "未设置")
                    dictTValue_local['tContent'] = content
                    tmp_reply_str = format_reply_str(dictStrCustom['strPersonalSystem'], dictTValue_local)
                    plugin_event.reply(tmp_reply_str)
                    return
                else:
                    plugin_event.reply("未知显示类型，可用: prompt, system")
                    return
            else:
                plugin_event.reply("格式错误，正确格式: .chat show prompt 或 .chat show system")
                return
        
        elif sub_command == 'set':
            if len(parts) >= 4:
                set_type = parts[2]
                set_value = ' '.join(parts[3:])
                
                if not set_value:
                    plugin_event.reply("设置内容不能为空")
                    return
                
                user_data = load_user_data(tmp_userID)
                
                if set_type == 'prompt':
                    user_data["custom_prompt"] = set_value
                    save_user_data(tmp_userID, user_data)
                    plugin_event.reply(dictStrCustom['strPersonalPromptSet'])
                    return
                elif set_type == 'system':
                    user_data["system_prompt"] = set_value
                    save_user_data(tmp_userID, user_data)
                    plugin_event.reply(dictStrCustom['strPersonalSystemSet'])
                    return
                else:
                    plugin_event.reply("未知设置类型，可用: prompt, system")
                    return
            else:
                plugin_event.reply("格式错误，正确格式: .chat set prompt <内容> 或 .chat set system <内容>")
                return
        
        else:
            plugin_event.reply("未知指令，使用 .chat help 查看帮助")
            return
    
    # 最后处理 AI 对话 #chat
    elif tmp_reast_str.startswith('#chat'):
        if not config["api_key"]:
            plugin_event.reply("API Key未配置，请联系管理员")
            return
        
        if not config.get("global_enabled", True):
            plugin_event.reply(dictStrCustom['strGlobalDisabled'])
            return
        
        if config.get("enable_review", False):
            plugin_event.reply(dictStrCustom['strReviewProcessing'])
        
        if plugin_event.plugin_info['func_type'] == 'group_message' and not config["enable_group"]:
            return
        if plugin_event.plugin_info['func_type'] == 'private_message' and not config["enable_private"]:
            return
        
        user_data = load_user_data(tmp_userID)
        if user_data["is_locked"]:
            plugin_event.reply(dictStrCustom['strUserLocked'])
            return
        
        banned_word = check_banned_words(tmp_reast_str)
        if banned_word:
            plugin_event.reply(dictStrCustom['strBannedWordFound'])
            return
        
        cooldown_remaining = check_cooldown(tmp_userID)
        if cooldown_remaining > 0:
            dictTValue_local['tContent'] = str(cooldown_remaining)
            tmp_reply_str = format_reply_str(dictStrCustom['strCooldown'], dictTValue_local)
            plugin_event.reply(tmp_reply_str)
            return
        
        prompt = tmp_reast_str[5:].strip()
        if not prompt:
            plugin_event.reply(dictStrCustom['strNoContent'])
            return
        
        banned_word = check_banned_words(prompt)
        if banned_word:
            plugin_event.reply(dictStrCustom['strBannedWordFound'])
            return
        
        response = call_deepseek_api(prompt, tmp_userID)
        if response:
            plugin_event.reply(response)
        else:
            plugin_event.reply(dictStrCustom['strAPICallFailed'])
        return

class Event(object):
    def init(plugin_event, Proc):
        pass

    def init_after(plugin_event, Proc):
        pass

    def private_message(plugin_event, Proc):
        unity_reply(plugin_event)

    def group_message(plugin_event, Proc):
        unity_reply(plugin_event)

    def poke(plugin_event, Proc):
        pass
    
    def menu(plugin_event, Proc):
        pass
