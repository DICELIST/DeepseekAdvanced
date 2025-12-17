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
.deepseek set maxsystemchars <字符数> - 设置系统提示词最大字符数

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
公共系统提示词: {tSystemPrompt}
系统提示词最大字符: {tMaxSystemChars}''',
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
    'strSystemTooLong': '系统提示词过长，最大允许 {tMaxChars} 字符，当前 {tCurrentChars} 字符',
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
