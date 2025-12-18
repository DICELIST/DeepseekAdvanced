### 站外链接OlivOS论坛
-  点击跳转到[OlivOS论坛-深度求索进阶版-DeepseekAdvanced](https://forum.olivos.run/d/873-deepseekadvanced)

**重要配置说明：使用前必须配置：请使用解压软件解压插件压缩包，找到 `DeepseekAdvanced/main.py` 文件，用文本编辑器打开，搜索 `MASTER_USERS` 配置项（约在第70行），将 `['2139497594']` 中的QQ号替换为你自己的QQ号，保存文件后重启OlivOS，确保你拥有管理员权限。**

**重要更新：本插件现在支持双权限系统。如果您的框架已安装 OlivaDiceCore 模块，插件会自动优先使用其权限系统，此时可以不需要修改 `MASTER_USERS` 配置。不过如果担心安全问题，建议把默认的ID改成不可能是个人ID的数值，例如 `['0']`。**

基于 Deepseek AI 的智能聊天插件，支持前缀触发、频率限制、个人系统提示词管理和上下文管理。

## 更新日志

### 版本 1.6.0 (最新更新)

#### 新增功能：群聊权限控制
1.  **群聊AI功能分级控制**
    *   新增群聊AI功能开关：群主/管理员可在本群控制AI功能启用状态
    *   普通成员权限管理：可设置是否允许普通成员使用AI功能
    *   Master用户远程管理：可通过群聊ID远程控制任意群聊的AI功能

2.  **群聊管理命令**
    *   **群内管理（群主/管理员/Master）**：
        - `.chat toggle [on/off]` - 开关本群AI功能
        - `.chat status` - 查看本群AI状态
        - `.chat allow` - 允许普通成员使用
        - `.chat deny` - 禁止普通成员使用
    *   **Master远程管理**：
        - `.deepseek group list` - 查看所有群聊配置
        - `.deepseek group <群聊ID> status` - 查看指定群聊状态
        - `.deepseek group <群聊ID> toggle [on/off]` - 开关指定群聊AI功能
        - `.deepseek group <群聊ID> allow/deny` - 允许/禁止普通成员使用
        - `.deepseek group <群聊ID> reset` - 重置群聊配置

3.  **权限层级系统**
    *   **Master权限**：最高权限，可管理所有群聊和用户
    *   **群主权限**：可管理本群AI功能设置
    *   **管理员权限**：可管理本群AI功能设置
    *   **普通成员权限**：根据群聊设置决定是否可用

4.  **兼容性改进**
    *   完全兼容原有配置结构
    *   新增群聊配置自动继承全局设置
    *   旧群聊默认使用原有全局开关设置

### 版本 1.5.0

#### 新增功能：双权限系统支持
1.  **OlivaDiceCore 权限系统兼容**
    *   自动检测并优先使用 OlivaDiceCore 的权限系统
    *   完美兼容原有骰主权限管理
    *   自动回退到内置权限系统

2.  **权限系统检测命令**
    *   `.deepseek checkperm` - 查看当前用户的权限状态和使用的权限系统
    *   显示权限系统类型、用户状态和Master列表信息

3.  **权限系统信息整合**
    *   在系统状态和配置查看中显示当前使用的权限系统
    *   管理帮助中新增权限说明部分

### 版本 1.4.0

#### 重要修复与优化
1.  **修复消息拼接错误**
    *   修复了系统提示词拼接的问题
    *   重新设计了消息构建逻辑，现在消息结构符合预期

2.  **删除预设提示词功能**
    *   移除了所有预设提示词（prompt）相关功能
    *   简化了用户设置，专注于系统提示词管理
    *   删除了相关配置项和命令

3.  **字符串全面分离**
    *   将所有用户可见的字符串分离到 `reply_strings.py` 文件
    *   提高了代码可维护性和多语言支持能力
    *   简化了 `main.py` 文件结构

### 版本 1.3.0

#### 功能新增与优化
1.  **个人与系统提示词管理**
    *   **个人系统提示词**：用户可设置个人专属的系统行为指令
    *   **公共系统提示词**：管理员可为所有用户设置默认的系统行为指令
    *   **查看个人配置**：用户可通过命令查看自己的所有个人设置

2.  **个人设置管理命令 (用户)**
    *   `.chat set system <内容>` - 设置个人系统提示词
    *   `.chat clear system` - 清空个人系统提示词
    *   `.chat config` 或 `.chat myconfig` - 查看个人所有设置
    *   `.chat show system` - 查看个人系统提示词

3.  **增强管理命令 (管理员)**
    *   `.deepseek set system <内容>` - 设置公共系统提示词
    *   `.deepseek clear system` - 清空公共系统提示词
    *   `.deepseek toggle global` - 全局开关AI功能
    *   `.deepseek clean all` - 清理所有用户的会话记录
    *   `.deepseek clean before <天数>` - 清理指定天数前的会话记录
    *   `.deepseek clean users <数量>` - 清理最早N个用户的会话记录
    *   `.deepseek toggle review` - 开关AI回复内容的二次审核功能

4.  **二次内容审核机制**
    *   新增安全层，在AI回复发出前，可启用二次审核流程
    *   将回复内容发送给Deepseek API进行合规性判断
    *   若审核不通过，将警告用户内容违规并自动锁定该用户

5.  **批量清理与全局控制**
    *   管理员可灵活按时间或用户数量批量清理会话记录
    *   新增全局开关，便于进行维护或临时禁用普通用户功能

#### 提示词优先级说明
*   **系统提示词 (system_prompt)**：
    1.  个人系统提示词（若设置）
    2.  公共系统提示词（若设置）
    3.  不使用系统提示词

## 功能特性

### 核心功能
-   **智能对话**：基于 Deepseek AI 的自然语言对话
-   **前缀触发**：使用 `#chat` 前缀触发 AI 对话
-   **频率限制**：可配置的冷却时间，防止滥用
-   **会话隔离**：基于 QQ 号的独立会话管理
-   **上下文记忆**：可配置的对话历史记忆（默认5段）
-   **提示词系统**：支持公共/个人层级的系统提示词
-   **权限管理**：支持OlivaDiceCore权限系统和内置Master列表系统
-   **群聊控制**：群主/管理员可控制本群AI功能，Master可远程管理
-   **内容安全**：违禁词过滤与可选的AI二次内容审核

### 数据管理
-   **会话清理**：用户可自主清空会话记录；管理员支持批量清理
-   **自动维护**：自动清理30天未使用的会话
-   **数据统计**：详细的使用统计和用户管理

## 使用指南

### 普通用户命令

#### 基础对话
`#chat [你的问题或对话内容]`

示例：
`#chat 你好，请介绍一下你自己`
`#chat 什么是人工智能？`

#### 帮助与配置
-   `.chat help` - 查看可用命令和系统状态信息
-   `.chat config` / `.chat myconfig` - 查看个人所有设置

#### 个人设置管理
-   `.chat set system <内容>` - 设置个人系统提示词
-   `.chat clear system` - 清空个人系统提示词
-   `.chat show system` - 查看个人系统提示词

#### 会话管理
-   `.chat clear` - 清空自己的会话记录，重新开始对话

### Master 管理命令

**注意：以下命令仅限 Master 用户使用**

#### 系统状态与配置查看
-   `.deepseek help` - 查看管理帮助（包含权限系统说明）
-   `.deepseek status` - 查看系统状态（包含权限系统信息）
-   `.deepseek config` - 查看详细配置（包含权限系统信息）
-   `.deepseek system` - 查看当前公共系统提示词
-   `.deepseek checkperm` - 检查当前用户的权限状态

#### 用户管理
-   `.deepseek users` - 查看用户列表
-   `.deepseek user <用户ID>` - 查看用户详情
-   `.deepseek user lock <用户ID>` - 锁定用户
-   `.deepseek user unlock <用户ID>` - 解锁用户
-   `.deepseek user clear <用户ID>` - 清空用户记录

#### 群聊管理（Master专属）
-   `.deepseek group list` - 查看所有群聊配置
-   `.deepseek group <群聊ID> status` - 查看指定群聊状态
-   `.deepseek group <群聊ID> toggle [on/off]` - 开关指定群聊AI功能
-   `.deepseek group <群聊ID> allow/deny` - 允许/禁止普通成员使用
-   `.deepseek group <群聊ID> reset` - 重置群聊配置

#### 系统配置
-   `.deepseek set cooldown <秒数>` - 设置冷却时间
-   `.deepseek set context <段数>` - 设置上下文限制
-   `.deepseek set prefix <前缀>` - 设置触发前缀
-   `.deepseek set tokens <数量>` - 设置最大token数
-   `.deepseek set temperature <数值>` - 设置温度参数
-   `.deepseek set model <模型名>` - 设置AI模型
-   `.deepseek set apikey <key>` - 设置API Key
-   `.deepseek set endpoint <url>` - 设置API端点
-   `.deepseek set system <内容>` - 设置公共系统提示词
-   `.deepseek set maxsystemchars <字符数>` - 设置系统提示词最大字符数

#### 功能开关
-   `.deepseek toggle group` - 切换群聊功能
-   `.deepseek toggle private` - 切换私聊功能
-   `.deepseek toggle debug` - 切换Debug模式
-   `.deepseek toggle filter` - 切换违禁词过滤
-   `.deepseek toggle global` - 全局开关AI功能
-   `.deepseek toggle review` - 开关AI回复二次审核

#### 批量清理
-   `.deepseek clean all` - 清理所有用户会话记录
-   `.deepseek clean before <天数>` - 清理指定天数前的记录
-   `.deepseek clean users <数量>` - 清理最早N个用户记录

#### 违禁词管理
-   `.deepseek ban add <词语>` - 添加违禁词
-   `.deepseek ban remove <词语>` - 移除违禁词
-   `.deepseek ban list` - 查看违禁词列表
-   `.deepseek ban clear` - 清空违禁词库
-   `.deepseek ban toggle` - 开关违禁词过滤

#### 系统维护
-   `.deepseek reset` - 重置系统配置
-   `.deepseek cleanup` - 清理过期数据

### 群聊管理员命令（群主/管理员）

**注意：以下命令仅限群主、管理员和Master在本群使用**

#### 本群AI功能管理
-   `.chat toggle [on/off]` - 开关本群AI功能
-   `.chat status` - 查看本群AI状态
-   `.chat allow` - 允许普通成员使用本群AI
-   `.chat deny` - 禁止普通成员使用本群AI

#### 权限说明
-   **群主**：可管理本群AI功能
-   **管理员**：可管理本群AI功能
-   **Master**：可管理所有群聊的AI功能
-   **普通成员**：根据群聊设置决定是否可用

## 权限系统说明

### 双权限系统工作机制
本插件支持两种权限系统，优先级如下：

1.  **OlivaDiceCore 权限系统（优先）**
    -   如果检测到 OlivaDiceCore 模块已安装
    -   使用 `OlivaDiceCore.ordinaryInviteManager.isInMasterList()` 进行权限判定
    -   完美兼容原有的骰主权限管理

2.  **内置 Master 列表系统（回退）**
    -   如果未检测到 OlivaDiceCore 模块
    -   使用 `main.py` 中的 `MASTER_USERS` 列表进行权限判定
    -   需要手动配置Master用户QQ号

### 群聊权限层级
1.  **Master权限**：最高权限，可管理所有群聊和用户
2.  **群主权限**：可管理本群AI功能设置
3.  **管理员权限**：可管理本群AI功能设置
4.  **普通成员权限**：根据群聊设置决定是否可用

### 如何确认当前使用的权限系统
使用命令：`.deepseek checkperm`

### 权限系统配置建议
-   **已安装 OlivaDiceCore**：无需额外配置，自动使用骰主权限系统
-   **未安装 OlivaDiceCore**：在 `main.py` 中配置 `MASTER_USERS` 列表
-   **安全建议**：即使使用OlivaDiceCore权限系统，也建议将 `MASTER_USERS` 中的默认ID改成不可能是个人ID的数值，例如 `['0']`

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
-   **群聊设置**：
    -   新群聊默认AI功能：开启（继承全局设置）
    -   新群聊普通成员权限：禁止
-   **提示词**：
    -   公共系统提示词：未设置
    -   系统提示词最大字符数：1000

### 群聊配置继承规则
-   新加入的群聊自动继承全局 `enable_group` 设置
-   群主/管理员可独立控制本群AI功能状态
-   Master用户可远程管理任意群聊设置

## 故障排除

### 常见错误及解决方法

-   **"API Key未配置，请联系管理员"**
    *   **原因**：未设置有效的 Deepseek API Key
    *   **解决**：使用 Master 账号执行 `.deepseek set apikey your_actual_api_key`

-   **"系统冷却中，请等待 X 秒后重试"**
    *   **原因**：触发频率限制
    *   **解决**：等待指定时间后重试，或联系管理员调整冷却时间

-   **"AI功能对你禁用，请联系管理员"**
    *   **原因**：用户被锁定或全局功能关闭
    *   **解决**：联系管理员检查全局开关或解锁用户

-   **"本群AI功能已关闭"**
    *   **原因**：当前群聊的AI功能已被群主/管理员/Master关闭
    *   **解决**：联系群主/管理员开启本群AI功能，或等待Master远程开启

-   **"本群AI功能仅限群主、管理员和Master使用"**
    *   **原因**：当前群聊禁止普通成员使用AI功能
    *   **解决**：联系群主/管理员允许普通成员使用，或等待Master远程设置

-   **"AI服务暂时不可用，请稍后再试"**
    *   **原因**：API 服务异常、网络问题或全局功能关闭
    *   **解决**：检查网络，确认 API Key 有效，或联系管理员

-   **"内容包含违禁词汇，请修改后重新发送"**
    *   **原因**：消息内容命中违禁词库
    *   **解决**：修改消息内容，或联系管理员调整违禁词设置

-   **"警告：生成内容涉嫌违规，你已被锁定"**
    *   **原因**：启用了二次审核且AI回复被判定为违规内容
    *   **解决**：联系管理员解锁并检查问题

### 权限相关问题

-   **"权限不足，无法执行此操作"**
    *   **原因**：用户不是Master，无法执行管理命令
    *   **解决**：确认权限系统配置，使用 `.deepseek checkperm` 检查权限状态

-   **"此功能仅限群主和管理员在本群使用"**
    *   **原因**：用户尝试跨群操作或非群聊环境使用群管理命令
    *   **解决**：群主/管理员只能在本群使用群管理命令

-   **权限系统检测失败**
    *   **原因**：OlivaDiceCore模块存在但接口调用失败
    *   **解决**：插件会自动回退到内置权限系统，检查 `MASTER_USERS` 配置

### Debug 模式
启用 Debug 模式可获取详细错误信息：
`.deepseek toggle debug`
启用后，API 错误将显示状态码和错误详情

## 数据管理

### 文件结构
```
DeepseekAdvanced/
├── data/
│   ├── config.json          # 系统配置文件（包含群聊设置）
│   ├── banned_words.json    # 违禁词库文件
│   ├── users/
│   │   └── user_QQ号.json   # 用户配置文件
│   └── sessions/
│       └── session_QQ号.json # 会话记录文件
├── reply_strings.py         # 所有回复字符串定义
└── main.py                  # 主程序文件
```

### 数据安全
-   所有数据本地存储
-   会话记录支持用户自主清理和管理员批量清理
-   提供违禁词过滤与可选的AI二次内容审核机制
-   群聊配置独立存储，互不干扰

## 技术支持

### 问题反馈
如遇问题，请提供：
1.  错误日志截图
2.  操作步骤描述
3.  系统环境信息（是否安装OlivaDiceCore）
4.  插件版本号

### 常见问题
**Q：如何确认插件已正确加载？**
A：在聊天窗口发送 `.chat help`，如果收到回复说明插件正常运行

**Q：个人提示词和系统提示词有什么区别？**
A：系统提示词是影响AI核心行为的底层指令，可以控制AI的角色、行为规范和回复格式

**Q：如何开启内容二次审核？**
A：管理员使用 `.deepseek toggle review` 命令开启。开启后，所有AI回复都会经过一次额外的合规性审核

**Q：如何确认当前使用的权限系统？**
A：使用 `.deepseek checkperm` 命令查看权限状态和权限系统类型

**Q：OlivaDiceCore和内置权限系统哪个优先级更高？**
A：OlivaDiceCore优先级更高。如果检测到OlivaDiceCore模块，会自动使用其权限系统；否则回退到内置权限系统

**Q：群主/管理员如何开关本群AI功能？**
A：在本群使用 `.chat toggle on` 开启或 `.chat toggle off` 关闭

**Q：Master如何远程管理其他群聊的AI功能？**
A：使用 `.deepseek group <群聊ID> toggle on/off` 远程开关指定群聊的AI功能

**Q：新群聊的AI功能默认是开启还是关闭？**
A：新群聊默认继承全局 `enable_group` 设置，如果全局群聊功能开启，则新群聊AI功能也默认开启

## 许可证
MIT License

## 免责声明
本插件仅供学习和交流使用，请遵守：
-   相关法律法规
-   平台使用规定
-   AI 服务商的使用条款
-   尊重他人隐私和权益

如有问题，请查阅本文档或联系开发者获取支持。
