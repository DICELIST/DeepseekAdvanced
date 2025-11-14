### 站外链接OlivOS论坛
-  点击跳转到[OlivOS论坛-深度求索进阶版-DeepseekAdvanced](https://forum.olivos.run/d/873-deepseekadvanced)

**使用前必须配置：请使用解压软件解压插件压缩包，找到 `DeepseekAdvanced/main.py` 文件，用文本编辑器打开，搜索 `MASTER_USERS` 配置项（约在第50行），将 `['2139497594']` 中的QQ号替换为你自己的QQ号，保存文件后重启OlivOS，确保你拥有管理员权限。**

具体步骤：
1. **解压文件**：使用WinRAR、7-Zip等解压软件解压插件压缩包
2. **找到文件**：进入解压后的 `DeepseekAdvanced` 文件夹，找到 `main.py` 文件
3. **编辑配置**：用记事本、VS Code等文本编辑器打开 `main.py` 文件
4. **搜索定位**：按Ctrl+F搜索 `MASTER_USERS` 关键字（约在第50行）
5. **修改QQ号**：将 `['2139497594']` 中的数字替换为你的QQ号，例如 `['123456789']`
6. **保存重启**：保存文件后重启OlivOS服务
7. **验证权限**：使用 `.deepseek help` 命令验证是否拥有管理员权限

## 🎯 功能特性

### 核心功能
- **智能对话**：基于 Deepseek AI 的自然语言对话
- **前缀触发**：使用 `#chat` 前缀触发 AI 对话
- **频率限制**：可配置的冷却时间，防止滥用
- **会话隔离**：基于 QQ 号的独立会话管理
- **上下文记忆**：可配置的对话历史记忆（默认5段）
- **个人预设**：支持用户自定义预设提示词
- **权限管理**：完善的用户权限控制系统

### 数据管理
- **会话清理**：用户可自主清空会话记录
- **自动维护**：自动清理30天未使用的会话
- **数据统计**：详细的使用统计和用户管理

## 🚀 快速开始

### 环境要求
- OlivOS 框架
- Python 3.7+
- 网络连接（用于调用 Deepseek API）
- Deepseek API Key

### 安装步骤
1. 将插件文件夹放置于 `plugin/app/` 目录下
2. 重启 OlivOS 服务
3. 获取 Deepseek API Key
4. 使用 Master 账号配置 API Key

## 📖 使用指南

### 普通用户命令

#### 基础对话
`#chat [你的问题或对话内容]`

**示例**：
`#chat 你好，请介绍一下你自己`
`#chat 什么是人工智能？`

#### 帮助信息
`.chat help`
查看可用命令和系统状态信息。

#### 会话管理
`.chat clear`
清空自己的会话记录，重新开始对话。

### Master 管理命令

> **注意**：以下命令仅限 Master 用户使用

#### 系统状态管理
- `.deepseek status` - 查看系统状态
- `.deepseek config` - 查看详细配置
- `.deepseek help` - 查看管理帮助

#### 用户管理
- `.deepseek users` - 查看用户列表
- `.deepseek user <用户ID>` - 查看用户详情
- `.deepseek user lock <用户ID>` - 锁定用户
- `.deepseek user unlock <用户ID>` - 解锁用户
- `.deepseek user clear <用户ID>` - 清空用户记录

#### 系统配置
- `.deepseek set cooldown <秒数>` - 设置冷却时间
- `.deepseek set context <段数>` - 设置上下文限制
- `.deepseek set prefix <前缀>` - 设置触发前缀
- `.deepseek set tokens <数量>` - 设置最大token数
- `.deepseek set temperature <数值>` - 设置温度参数
- `.deepseek set model <模型名>` - 设置AI模型
- `.deepseek set apikey <key>` - 设置API Key
- `.deepseek set endpoint <url>` - 设置API端点

#### 功能开关
- `.deepseek toggle group` - 切换群聊功能
- `.deepseek toggle private` - 切换私聊功能
- `.deepseek toggle debug` - 切换Debug模式

#### 系统维护
- `.deepseek reset` - 重置系统配置
- `.deepseek cleanup` - 清理过期数据

## ⚙️ 配置说明

### 首次配置
1. 获取 Deepseek API Key
2. 使用 Master 账号执行：
`.deepseek set apikey your_api_key_here`

### 默认配置参数
- **冷却时间**：10秒 - 两次对话间的最小间隔
- **上下文限制**：5段 - 记忆的对话轮数
- **触发前缀**：`#chat` - 触发AI对话的前缀
- **最大Token**：1000 - 单次回复的最大长度
- **温度参数**：0.7 - AI回复的创造性（0-1）
- **AI模型**：`deepseek-chat` - 使用的AI模型
- **API端点**：`https://api.deepseek.com/v1/chat/completions` - API服务地址
- **群聊功能**：开启 - 是否在群聊中启用
- **私聊功能**：开启 - 是否在私聊中启用
- **Debug模式**：关闭 - 是否显示详细错误信息

## 🛠️ 故障排除

### 常见错误及解决方法

#### ❌ "API Key未配置，请联系管理员"
**原因**：未设置有效的 Deepseek API Key
**解决方法**：
1. 获取 Deepseek API Key
2. 使用 Master 账号执行：
`.deepseek set apikey your_actual_api_key`

#### ❌ "系统冷却中，请等待 X 秒后重试"
**原因**：触发频率限制
**解决方法**：
- 等待指定时间后重试
- 或联系管理员调整冷却时间：
`.deepseek set cooldown 20` （设置为20秒）

#### ❌ "AI功能对你禁用，请联系管理员"
**原因**：用户被锁定
**解决方法**：
- 联系管理员解锁：
`.deepseek user unlock 你的QQ号`

#### ❌ "AI服务暂时不可用，请稍后再试"
**原因**：API 服务异常
**解决方法**：
1. 检查网络连接
2. 确认 API Key 有效且未过期
3. 检查 Deepseek 服务状态
4. 开启 Debug 模式查看详细错误：
`.deepseek toggle debug`

#### ❌ "权限不足，无法执行此操作"
**原因**：非 Master 用户尝试使用管理命令
**解决方法**：
- 联系管理员添加 Master 权限
- 或在代码中配置 Master 用户列表

#### ❌ "内容不能为空"
**原因**：消息内容为空
**解决方法**：
- 在 `#chat` 后输入有效内容

#### ❌ "清空会话记录失败"
**原因**：文件操作异常
**解决方法**：
- 检查插件文件权限
- 重启 OlivOS 服务

### Debug 模式
启用 Debug 模式可获取详细错误信息：
`.deepseek toggle debug`
启用后，API 错误将显示状态码和错误详情。

## 💾 数据管理

### 文件结构
```
DeepseekAdvanced/
├── data/
│   ├── config.json          # 系统配置文件
│   ├── users/
│   │   └── user_QQ号.json   # 用户配置文件
│   └── sessions/
│       └── session_QQ号.json # 会话记录文件
```

### 数据说明
- **用户配置**：包含自定义提示词、锁定状态、使用次数、最后使用时间
- **会话记录**：保存对话历史，遵循配置的上下文限制
- **自动清理**：30天未使用的会话会自动清理

### 数据安全
- 所有数据本地存储
- 会话记录定期自动清理
- 支持手动清理特定用户数据

## 🔧 高级配置

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

## 📊 系统状态说明

使用 `.deepseek status` 查看的系统状态包含：
- **用户总数**：已记录的用户数量
- **群聊功能**：是否在群聊中启用
- **私聊功能**：是否在私聊中启用  
- **冷却时间**：当前设置的冷却时间
- **上下文限制**：对话历史记忆段数
- **Debug模式**：是否开启详细错误显示

## 🚀 未来更新方向

### 功能增强
- [ ] **多模型支持**：集成 GPT、Claude 等更多 AI 模型
- [ ] **预设模板**：提供多种角色预设模板
- [ ] **对话导出**：支持导出对话记录
- [ ] **批量操作**：用户批量管理功能
- [ ] **使用统计**：详细的使用数据统计分析
- [ ] **插件市场**：在线获取插件和预设

### 用户体验
- [ ] **图形化界面**：Web 管理界面
- [ ] **移动端支持**：手机端管理功能
- [ ] **多语言支持**：国际化语言包
- [ ] **主题系统**：可切换的界面主题
- [ ] **快捷命令**：自定义快捷指令

### 技术优化
- [ ] **性能优化**：对话缓存和性能提升
- [ ] **容错机制**：更好的错误处理和重试
- [ ] **安全增强**：API Key 加密存储
- [ ] **数据库支持**：可选数据库后端
- [ ] **插件热重载**：无需重启更新配置
- [ ] **API 代理**：支持代理服务器配置

### 集成扩展
- [ ] **Webhook 支持**：外部系统集成
- [ ] **API 接口**：提供 RESTful API
- [ ] **消息推送**：重要事件通知
- [ ] **第三方集成**：与其他系统对接

## 🆘 技术支持

### 问题反馈
如遇问题，请提供以下信息：
1. **错误日志截图**
2. **操作步骤描述**
3. **系统环境信息**
4. **插件版本号**

### 常见问题
**Q：如何确认插件已正确加载？**
A：在聊天窗口发送 `.chat help`，如果收到回复说明插件正常运行。

**Q：如何查看详细的错误信息？**
A：使用 `.deepseek toggle debug` 开启 Debug 模式。

**Q：如何重置所有配置？**
A：使用 `.deepseek reset` 重置为默认配置。

**Q：用户被误锁定了怎么办？**
A：使用 `.deepseek user unlock <用户ID>` 解锁用户。

## 📄 许可证

MIT License

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request 来改进本项目：
1. Fork 本项目
2. 创建功能分支
3. 提交更改
4. 推送到分支
5. 创建 Pull Request

## ⚠️ 免责声明

本插件仅供学习和交流使用，请遵守：
- 相关法律法规
- 平台使用规定  
- AI 服务商的使用条款
- 尊重他人隐私和权益

