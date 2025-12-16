### 站外链接OlivOS论坛
-  点击跳转到[OlivOS论坛-深度求索进阶版-DeepseekAdvanced](https://forum.olivos.run/d/873-deepseekadvanced)


**重要配置说明：使用前必须配置：请使用解压软件解压插件压缩包，找到 `DeepseekAdvanced/main.py` 文件，用文本编辑器打开，搜索 `MASTER_USERS` 配置项（约在第50行），将 `['2139497594']` 中的QQ号替换为你自己的QQ号，保存文件后重启OlivOS，确保你拥有管理员权限。**

基于 Deepseek AI 的智能聊天插件，支持前缀触发、频率限制、个人/系统提示词管理和上下文管理。

## 更新日志

### 版本 1.3.0 (最新更新)

#### 功能新增与优化
1.  **个人与系统提示词管理**
    *   **个人预设提示词**：用户可设置个人专属的对话预设（如角色扮演、专业方向）。
    *   **个人系统提示词**：新增更底层的AI行为控制系统指令，优先级高于公共系统提示词。
    *   **公共系统提示词**：管理员可为所有用户设置默认的系统行为指令。
    *   **查看个人配置**：用户可通过命令查看自己的所有个人设置。

2.  **个人设置管理命令 (用户)**
    *   `.chat set prompt <内容>` - 设置个人预设提示词
    *   `.chat clear prompt` - 清空个人预设提示词
    *   `.chat set system <内容>` - 设置个人系统提示词
    *   `.chat clear system` - 清空个人系统提示词
    *   `.chat config` 或 `.chat myconfig` - 查看个人所有设置（预设、系统提示词、使用统计等）
    *   `.chat show prompt` - 查看个人预设提示词
    *   `.chat show system` - 查看个人系统提示词

3.  **增强管理命令 (管理员)**
    *   `.deepseek set system <内容>` - 设置公共系统提示词
    *   `.deepseek clear system` - 清空公共系统提示词
    *   `.deepseek toggle global` - 全局开关AI功能（仅影响普通用户，管理员命令不受限）
    *   `.deepseek clean all` - 清理所有用户的会话记录
    *   `.deepseek clean before <天数>` - 清理指定天数前的会话记录
    *   `.deepseek clean users <数量>` - 清理最早N个用户的会话记录
    *   `.deepseek toggle review` - 开关AI回复内容的二次审核功能

4.  **二次内容审核机制**
    *   新增安全层，在AI回复发出前，可启用二次审核流程。
    *   将回复内容发送给Deepseek API进行合规性判断。
    *   若审核不通过，将警告用户内容违规并自动锁定该用户。
    *   通过 `.deepseek toggle review` 控制此功能的开关。

5.  **批量清理与全局控制**
    *   管理员可灵活按时间或用户数量批量清理会话记录，优化数据管理。
    *   新增全局开关，便于进行维护或临时禁用普通用户功能。

#### 提示词优先级说明
*   **预设提示词 (custom_prompt)**：
    1.  个人预设提示词（若设置）
    2.  公共预设提示词（若设置）
    3.  系统默认（"你是一个有用的助手"）
*   **系统提示词 (system_prompt)**：
    1.  个人系统提示词（若设置）
    2.  公共系统提示词（若设置）
    3.  不使用系统提示词

#### 消息构建顺序
```
[系统提示词]（可选的 system 消息）
[历史对话]（0-5条历史记录）
[预设提示词]（可选的 user 消息，作为第一条）
[当前用户消息]（user 消息）
```

### 版本 1.2.0

#### 功能新增
1.  **默认预设提示词管理**
    *   新增命令：`.deepseek set prompt <预设内容>` - 设置系统默认预设提示词
    *   新增命令：`.deepseek prompt` - 查看当前默认预设提示词
    *   预设优先级：用户个人预设 > 系统默认预设 > 硬编码默认预设

2.  **违禁词库系统**
    *   新增命令：`.deepseek ban add <词语>` - 添加违禁词
    *   新增命令：`.deepseek ban remove <词语>` - 移除违禁词
    *   新增命令：`.deepseek ban list` - 查看违禁词列表
    *   新增命令：`.deepseek ban clear` - 清空违禁词库
    *   新增命令：`.deepseek ban toggle` - 开关违禁词过滤
    *   新增命令：`.deepseek toggle filter` - 开关违禁词过滤（快捷方式）
    *   支持模糊匹配检测，命中违禁词时提示“内容包含违禁词汇，请修改后重新发送”

#### 问题修复
1.  **修复私聊开关Bug**
    *   修复了关闭私聊模式后无法使用 `.deepseek toggle private` 重新打开的问题
    *   现在管理命令可以绕过功能开关限制，确保系统可维护性
2.  **优化流式传输**
    *   启用流式API响应，避免长文本生成时的超时问题
    *   增加超时时间至60秒，提高稳定性

## 功能特性

### 核心功能
-   **智能对话**：基于 Deepseek AI 的自然语言对话
-   **前缀触发**：使用 `#chat` 前缀触发 AI 对话
-   **频率限制**：可配置的冷却时间，防止滥用
-   **会话隔离**：基于 QQ 号的独立会话管理
-   **上下文记忆**：可配置的对话历史记忆（默认5段）
-   **提示词系统**：支持公共/个人层级的预设提示词和系统提示词
-   **权限管理**：完善的用户权限控制系统
-   **内容安全**：违禁词过滤与可选的AI二次内容审核

### 数据管理
-   **会话清理**：用户可自主清空会话记录；管理员支持批量清理
-   **自动维护**：自动清理30天未使用的会话
-   **数据统计**：详细的使用统计和用户管理

## 快速开始

### 环境要求
-   OlivOS 框架
-   Python 3.7+
-   网络连接（用于调用 Deepseek API）
-   Deepseek API Key

### 安装步骤
1.  将插件文件夹放置于 `plugin/tmp/DeepseekAdvanced/` 目录下
2.  重启 OlivOS 服务
3.  获取 Deepseek API Key
4.  使用 Master 账号配置 API Key

## 使用指南

### 普通用户命令

#### 基础对话
`#chat [你的问题或对话内容]`

示例：
`#chat 你好，请介绍一下你自己`
`#chat 什么是人工智能？`

#### 帮助与配置
-   `.chat help` - 查看可用命令和系统状态信息。
-   `.chat config` / `.chat myconfig` - 查看个人所有设置（预设、系统提示词、使用次数等）
-   `.chat show prompt` - 查看个人预设提示词
-   `.chat show system` - 查看个人系统提示词

#### 个人设置管理
-   `.chat set prompt <内容>` - 设置个人预设提示词
-   `.chat clear prompt` - 清空个人预设提示词
-   `.chat set system <内容>` - 设置个人系统提示词
-   `.chat clear system` - 清空个人系统提示词

#### 会话管理
-   `.chat clear` - 清空自己的会话记录，重新开始对话。

### Master 管理命令

**注意：以下命令仅限 Master 用户使用**

#### 系统状态与配置查看
-   `.deepseek status` - 查看系统状态
-   `.deepseek config` - 查看详细配置
-   `.deepseek help` - 查看管理帮助
-   `.deepseek prompt` - 查看当前公共预设提示词

#### 用户管理
-   `.deepseek users` - 查看用户列表
-   `.deepseek user <用户ID>` - 查看用户详情
-   `.deepseek user lock <用户ID>` - 锁定用户
-   `.deepseek user unlock <用户ID>` - 解锁用户
-   `.deepseek user clear <用户ID>` - 清空用户记录

#### 系统配置
-   `.deepseek set cooldown <秒数>` - 设置冷却时间
-   `.deepseek set context <段数>` - 设置上下文限制
-   `.deepseek set prefix <前缀>` - 设置触发前缀
-   `.deepseek set tokens <数量>` - 设置最大token数
-   `.deepseek set temperature <数值>` - 设置温度参数
-   `.deepseek set model <模型名>` - 设置AI模型
-   `.deepseek set apikey <key>` - 设置API Key
-   `.deepseek set endpoint <url>` - 设置API端点
-   `.deepseek set prompt <预设内容>` - 设置公共预设提示词
-   `.deepseek set system <内容>` - **（新增）** 设置公共系统提示词
-   `.deepseek clear system` - **（新增）** 清空公共系统提示词

#### 功能开关
-   `.deepseek toggle group` - 切换群聊功能
-   `.deepseek toggle private` - 切换私聊功能
-   `.deepseek toggle debug` - 切换Debug模式
-   `.deepseek toggle filter` - 切换违禁词过滤
-   `.deepseek toggle global` - **（新增）** 全局开关AI功能（普通用户）
-   `.deepseek toggle review` - **（新增）** 开关AI回复二次审核

#### 批量清理
-   `.deepseek clean all` - **（新增）** 清理所有用户会话记录
-   `.deepseek clean before <天数>` - **（新增）** 清理指定天数前的记录
-   `.deepseek clean users <数量>` - **（新增）** 清理最早N个用户记录

#### 违禁词管理
-   `.deepseek ban add <词语>` - 添加违禁词
-   `.deepseek ban remove <词语>` - 移除违禁词
-   `.deepseek ban list` - 查看违禁词列表
-   `.deepseek ban clear` - 清空违禁词库
-   `.deepseek ban toggle` - 开关违禁词过滤

#### 系统维护
-   `.deepseek reset` - 重置系统配置
-   `.deepseek cleanup` - 清理过期数据

## 配置说明

### 首次配置
1.  获取 Deepseek API Key
2.  使用 Master 账号执行：
    `.deepseek set apikey your_api_key_here`

### 默认配置参数
-   **对话参数**：
    -   冷却时间：10秒
    -   上下文限制：5段
    -   触发前缀：`#chat`
    -   最大Token：1000
    -   温度参数：0.7
    -   AI模型：`deepseek-chat`
-   **API设置**：
    -   API端点：`https://api.deepseek.com/v1/chat/completions`
-   **功能开关**：
    -   群聊功能：开启
    -   私聊功能：开启
    -   Debug模式：关闭
    -   全局开关：开启
    -   违禁词过滤：开启
    -   二次审核：关闭
-   **提示词**：
    -   公共预设提示词：`你是一个有用的助手`
    -   公共系统提示词：未设置

## 故障排除

### 常见错误及解决方法

-   **“API Key未配置，请联系管理员”**
    *   **原因**：未设置有效的 Deepseek API Key。
    *   **解决**：使用 Master 账号执行 `.deepseek set apikey your_actual_api_key`。

-   **“系统冷却中，请等待 X 秒后重试”**
    *   **原因**：触发频率限制。
    *   **解决**：等待指定时间后重试，或联系管理员调整冷却时间。

-   **“AI功能对你禁用，请联系管理员”**
    *   **原因**：用户被锁定或全局功能关闭。
    *   **解决**：联系管理员检查全局开关或解锁用户。

-   **“AI服务暂时不可用，请稍后再试”**
    *   **原因**：API 服务异常、网络问题或全局功能关闭。
    *   **解决**：检查网络，确认 API Key 有效，或联系管理员。

-   **“内容包含违禁词汇，请修改后重新发送”**
    *   **原因**：消息内容命中违禁词库。
    *   **解决**：修改消息内容，或联系管理员调整违禁词设置。

-   **“警告：生成内容涉嫌违规，你已被锁定”**
    *   **原因**：启用了二次审核且AI回复被判定为违规内容。
    *   **解决**：联系管理员解锁并检查问题。

### Debug 模式
启用 Debug 模式可获取详细错误信息：
`.deepseek toggle debug`
启用后，API 错误将显示状态码和错误详情。

## 数据管理

### 文件结构
```
DeepseekAdvanced/
├── data/
│   ├── config.json          # 系统配置文件
│   ├── banned_words.json    # 违禁词库文件
│   ├── users/
│   │   └── user_QQ号.json   # 用户配置文件（含个人提示词）
│   └── sessions/
│       └── session_QQ号.json # 会话记录文件
```

### 数据安全
-   所有数据本地存储。
-   会话记录支持用户自主清理和管理员批量清理。
-   提供违禁词过滤与可选的AI二次内容审核机制。

## 高级配置

### Master 用户配置
在 `main.py` 中修改 `MASTER_USERS` 列表：
```python
MASTER_USERS = ['123456789', '987654321']  # 添加 Master 用户的 QQ 号
```

### 自定义回复消息
修改 `dictStrCustom` 字典来自定义系统回复：
```python
dictStrCustom = {
    'strCooldown': '系统冷却中，请等待 {tContent} 秒后重试',
    'strUserLocked': 'AI功能对你禁用，请联系管理员',
    # ... 其他消息
}
```

## 未来更新方向

### 功能增强
-   多模型支持：集成 GPT、Claude 等更多 AI 模型
-   预设模板：提供多种角色预设模板
-   对话导出：支持导出对话记录
-   使用统计：详细的使用数据统计分析

### 技术优化
-   性能优化：对话缓存和性能提升
-   容错机制：更好的错误处理和重试
-   安全增强：API Key 加密存储
-   数据库支持：可选数据库后端

## 技术支持

### 问题反馈
如遇问题，请提供：
1.  错误日志截图
2.  操作步骤描述
3.  系统环境信息
4.  插件版本号

### 常见问题
**Q：如何确认插件已正确加载？**
A：在聊天窗口发送 `.chat help`，如果收到回复说明插件正常运行。

**Q：个人提示词和系统提示词有什么区别？**
A：个人提示词是用户自定义的对话风格或角色；系统提示词是更底层、影响AI核心行为的指令。系统提示词优先级更高。

**Q：如何开启内容二次审核？**
A：管理员使用 `.deepseek toggle review` 命令开启。开启后，所有AI回复都会经过一次额外的合规性审核。

## 许可证
MIT License

## 免责声明
本插件仅供学习和交流使用，请遵守：
-   相关法律法规
-   平台使用规定
-   AI 服务商的使用条款
-   尊重他人隐私和权益


如有问题，请查阅本文档或联系开发者获取支持。
