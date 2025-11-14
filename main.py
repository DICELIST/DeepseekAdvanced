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
    "debug_mode": False
}

dictStrCustom = {
    'strCooldown': '系统冷却中，请等待 {tContent} 秒后重试',
    'strUserLocked': 'AI功能对你禁用，请联系管理员',
    'strNoContent': '内容不能为空',
    'strHelpCommon': '''【DeepSeek AI 聊天助手】
使用 #chat [内容] 与AI对话
.chat help - 查看帮助信息
.chat clear - 清空自己的会话记录
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

🔧 功能开关:
.deepseek toggle group - 切换群聊功能
.deepseek toggle private - 切换私聊功能
.deepseek toggle debug - 切换Debug模式

🛠️ 系统维护:
.deepseek reset - 重置系统配置
.deepseek cleanup - 清理过期数据
.deepseek status - 查看系统状态
.deepseek config - 查看详细配置''',
    'strNoPermission': '权限不足，无法执行此操作',
    'strConfigUpdated': '配置已更新: {tContent}',
    'strUserNotFound': '用户不存在',
    'strUserLockedSuccess': '用户 {tTargetName} 已锁定',
    'strUserUnlockedSuccess': '用户 {tTargetName} 已解锁',
    'strUserClearedSuccess': '用户 {tTargetName} 记录已清空',
    'strUserDetail': '用户 {tTargetName} 详情:\n使用次数: {tUseCount}\n状态: {tStatus}\n最后使用: {tLastUsed}',
    'strSystemStatus': '''系统状态:
用户总数: {tUserCount}
群聊功能: {tGroupStatus}
私聊功能: {tPrivateStatus}
冷却时间: {tCooldown}秒
上下文限制: {tContext}段
Debug模式: {tDebugStatus}''',
    'strAPICallFailed': 'AI服务暂时不可用，请稍后再试',
    'strDebugInfo': 'Debug信息: {tContent}',
    'strClearSuccess': '已清空你的会话记录',
    'strClearFailed': '清空会话记录失败'
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
    'tDebugStatus': '关闭'
}

# 在这里定义Master用户ID列表
MASTER_USERS = ['2139497594']  # 将你的QQ号添加到Master列表

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

def get_user_file(user_id):
    return os.path.join(data_dir, 'users', f'user_{user_id}.json')

def get_session_file(user_id):
    return os.path.join(data_dir, 'sessions', f'session_{user_id}.json')

def load_user_data(user_id):
    user_file = get_user_file(user_id)
    default_user = {
        "user_id": user_id,
        "custom_prompt": "",
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
    """清空用户会话记录"""
    try:
        session_file = get_session_file(user_id)
        if os.path.exists(session_file):
            os.remove(session_file)
        return True
    except:
        return False

def unity_reply(plugin_event):
    config = load_config()
    
    if plugin_event.plugin_info['func_type'] == 'group_message' and not config["enable_group"]:
        return
    if plugin_event.plugin_info['func_type'] == 'private_message' and not config["enable_private"]:
        return
    
    tmp_reast_str = plugin_event.data.message
    tmp_userID = plugin_event.data.user_id
    
    dictTValue_local = dictTValue.copy()
    dictTValue_local['tUserName'] = plugin_event.data.sender.get('name', '用户')
    
    def call_deepseek_api(prompt, user_id):
        try:
            user_data = load_user_data(user_id)
            session_data = load_session_data(user_id)
            
            system_prompt = user_data.get("custom_prompt", "")
            if not system_prompt:
                system_prompt = "你是一个有用的助手"
            
            messages = [{"role": "system", "content": system_prompt}]
            messages.extend(list(session_data["history"]))
            messages.append({"role": "user", "content": prompt})
            
            response = requests.post(
                config["api_endpoint"],
                headers={"Authorization": f"Bearer {config['api_key']}"},
                json={
                    "model": config["default_model"],
                    "messages": messages,
                    "temperature": config["temperature"],
                    "max_tokens": config["max_tokens"],
                    "stream": False
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                assistant_reply = result['choices'][0]['message']['content']
                
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
    
    def check_cooldown(user_id):
        user_data = load_user_data(user_id)
        if user_data["last_used"]:
            current_time = time.time()
            cooldown_end = user_data["last_used"] + config["cooldown_time"]
            if current_time < cooldown_end:
                return int(cooldown_end - current_time)
        return 0
    
    if tmp_reast_str.startswith('#chat'):
        if not config["api_key"]:
            plugin_event.reply("API Key未配置，请联系管理员")
            return
        
        user_data = load_user_data(tmp_userID)
        if user_data["is_locked"]:
            plugin_event.reply(dictStrCustom['strUserLocked'])
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
        
        response = call_deepseek_api(prompt, tmp_userID)
        if response:
            plugin_event.reply(response)
        else:
            plugin_event.reply(dictStrCustom['strAPICallFailed'])
        return
    
    elif tmp_reast_str == '.chat help':
        dictTValue_local['tCooldown'] = str(config["cooldown_time"])
        dictTValue_local['tContext'] = str(config["max_context"])
        tmp_reply_str = format_reply_str(dictStrCustom['strHelpCommon'], dictTValue_local)
        plugin_event.reply(tmp_reply_str)
        return
    
    elif tmp_reast_str == '.chat clear':
        # 清空自己的会话记录
        if clear_user_session(tmp_userID):
            plugin_event.reply(dictStrCustom['strClearSuccess'])
        else:
            plugin_event.reply(dictStrCustom['strClearFailed'])
        return
    
    elif tmp_reast_str.startswith('.deepseek'):
        if not is_master_user(tmp_userID):
            plugin_event.reply(dictStrCustom['strNoPermission'])
            return
        
        parts = tmp_reast_str.split()
        if len(parts) < 2:
            plugin_event.reply("使用 .deepseek help 查看帮助")
            return
        
        command = parts[1]
        
        if command == 'help':
            plugin_event.reply(dictStrCustom['strHelpMaster'])
            return
        
        elif command == 'status':
            user_ids = get_all_users()
            dictTValue_local['tUserCount'] = str(len(user_ids))
            dictTValue_local['tGroupStatus'] = '开启' if config["enable_group"] else '关闭'
            dictTValue_local['tPrivateStatus'] = '开启' if config["enable_private"] else '关闭'
            dictTValue_local['tCooldown'] = str(config["cooldown_time"])
            dictTValue_local['tContext'] = str(config["max_context"])
            dictTValue_local['tDebugStatus'] = '开启' if config["debug_mode"] else '关闭'
            tmp_reply_str = format_reply_str(dictStrCustom['strSystemStatus'], dictTValue_local)
            plugin_event.reply(tmp_reply_str)
            return
        
        elif command == 'config':
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
Debug模式: {'开启' if config["debug_mode"] else '关闭'}'''
            plugin_event.reply(config_info)
            return
        
        elif command == 'users':
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
            if len(parts) < 3:
                plugin_event.reply("请指定用户ID，例如: .deepseek user 123456")
                return
            
            # 处理子命令或直接用户ID
            if len(parts) >= 4:
                # 有子命令的情况: .deepseek user lock 123456
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
                # 直接用户ID的情况: .deepseek user 123456
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
            set_type = parts[2]
            set_value = parts[3]
            
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
        
        elif command == 'toggle' and len(parts) >= 3:
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
        
        elif command == 'reset':
            save_config(default_config)
            plugin_event.reply("系统配置已重置为默认值")
            return
        
        elif command == 'cleanup':
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