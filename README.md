# 计算机网络实验六 - 简易即时通信工具

一个基于UDP/TCP协议的局域网即时通信工具，支持自动发现、一对一消息、广播消息和文件传输功能。

## 小组成员（第九组）

| 学号 | 姓名 | 负责模块 |
|------|------|----------|
| 202300800609 | 李牧熹 | 成员一：消息分发器 + 网络发现 |
| 202300800626 | 马驰原 | 成员二：界面整合与设计 |
| 202300800677 | 孟俊宇 | 成员三：广播消息 |
| 202300800585 | 何准 | 成员四：文件传输（TCP协议） |
| 202300800662 | 刘泽楷 | 成员五：组员管理 |
| 202300800596 | 石明琦 | 成员六：手动刷新组员列表 |
| 202300800607 | 孙聿轩 | 成员七：一对一消息传输 |

> **架构优化说明**：引入了MessageDispatcher（消息分发器）统一管理UDP通信，各模块职责更加清晰。详见 `docs/架构优化说明.md`

## github 仓库
- [项目仓库](https://github.com/MuxiZhaoyang/computer_network_experiment)

## 技术栈

- **编程语言**：Python 3.8+
- **GUI框架**：PyQt6
- **网络协议**：UDP（发现、消息）、TCP（文件传输）
- **序列化**：JSON
- **多线程**：threading
- **架构模式**：消息分发器模式（MessageDispatcher）

## 项目结构

```
computer_network_experiment/
├── src/                      # 源代码目录
│   ├── common/              # 公共模块
│   │   ├── __init__.py
│   │   ├── config.py       # 配置文件
│   │   ├── message_types.py # 消息类型定义
│   │   └── utils.py        # 工具函数
│   ├── core/               # 核心功能模块
│   │   ├── __init__.py
│   │   ├── message_dispatcher.py  # 消息分发器（成员一+七）⭐新增
│   │   ├── network_discovery.py   # 网络发现（成员一）
│   │   ├── message_p2p.py         # 一对一消息（成员二）
│   │   ├── message_broadcast.py   # 广播消息（成员三）
│   │   ├── file_transfer.py       # 文件传输（成员四）
│   │   ├── member_manager.py      # 组员管理（成员五）
│   │   └── member_refresh.py      # 手动刷新（成员六）
│   ├── ui/                 # 用户界面
│   │   ├── __init__.py
│   │   ├── main_window.py  # 主窗口（成员七）
│   │   └── components/     # UI组件
│   ├── __init__.py
│   └── main.py            # 程序入口
├── tests/                  # 测试目录
├── docs/                   # 文档目录
│   ├── 开发指南.md
│   ├── API文档.md
│   ├── 快速开始.md
│   ├── 成员任务分配.md
│   ├── 架构优化说明.md         # ⭐重要
│   ├── 架构优化后的成员任务.md  # ⭐必读
│   └── 接口对接检查清单.md     # ⭐必读
├── downloads/              # 文件下载目录（自动创建）
├── requirements.txt        # 依赖包列表
├── run.py                 # 启动脚本
├── .gitignore
└── README.md

```

## 功能特性

### ✅ 1. 自动发现聊天组（UDP广播）
- 客户端启动时自动发送UDP广播
- 使用特定关键字识别组内成员
- 自动更新在线成员列表

### ✅ 2. 一对一消息传输
- 点对点UDP消息发送
- 选择目标成员进行私聊
- 实时消息显示

### ✅ 3. 广播消息
- 向所有在线成员广播消息
- 所有成员实时接收广播内容

### ✅ 4. 文件传输
- 基于TCP协议的可靠文件传输
- 支持大文件传输
- 实时显示传输进度
- 文件传输确认机制

### ✅ 5. 组员管理
- 动态维护成员列表
- 成员加入/离开通知
- 实时更新在线状态

### ✅ 6. 手动刷新组员列表
- 手动触发成员发现
- 及时更新最新成员信息

### ✅ 7. 友好的用户界面
- 现代化GUI设计
- 清晰的功能布局
- 实时消息显示
- 文件传输进度条

## 安装与运行

### 1. 环境要求

- Python 3.8 或更高版本
- Windows/Linux/macOS

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 运行程序

```bash
python run.py
```

或者：

```bash
python -m src.main
```

### 4. 使用说明

1. **启动程序**：运行后输入用户名
2. **自动发现**：程序自动发现局域网内的其他用户
3. **发送消息**：
   - 选择成员，输入消息，点击"发送"进行一对一聊天
   - 点击"广播"向所有成员发送消息
4. **发送文件**：选择成员，点击"发送文件"，选择文件
5. **刷新列表**：点击"刷新成员列表"更新在线成员

## 开发指南

### 模块开发流程

1. **克隆项目**
   ```bash
   git clone <repository_url>
   cd computer_network_experiment
   ```

2. **创建开发分支**
   ```bash
   git checkout -b feature/your-module-name
   ```

3. **实现功能**
   - 找到你负责的模块文件（如 `src/core/network_discovery.py`）
   - 实现标注了 `TODO: 成员X实现` 的部分
   - 参考模块内的注释和文档字符串

4. **测试功能**
   - 运行程序测试你的模块
   - 确保不影响其他模块

5. **提交代码**
   ```bash
   git add .
   git commit -m "实现XXX功能"
   git push origin feature/your-module-name
   ```

### 模块间协作

- **共享UDP Socket**：`network_discovery`、`message_p2p`、`message_broadcast` 共享同一个UDP socket
- **信号槽机制**：各模块通过PyQt6信号与主窗口通信
- **成员列表同步**：通过 `member_manager` 统一管理成员列表

### 代码规范

- 遵循PEP 8代码风格
- 函数和类添加文档字符串
- 使用类型注解提高代码可读性
- 异常处理要完善

## 技术要点

### 网络协议

- **UDP广播地址**：255.255.255.255
- **默认UDP端口**：8888
- **默认TCP端口**：8889
- **消息格式**：JSON序列化

### 消息类型

```python
MessageType.DISCOVERY           # 发现请求
MessageType.DISCOVERY_RESPONSE  # 发现响应
MessageType.JOIN                # 加入通知
MessageType.LEAVE               # 离开通知
MessageType.REFRESH             # 刷新请求
MessageType.P2P_MESSAGE         # 一对一消息
MessageType.BROADCAST_MESSAGE   # 广播消息
MessageType.FILE_REQUEST        # 文件传输请求
```

### 数据结构

- **Member**：成员信息（用户名、IP、端口）
- **ChatMessage**：聊天消息（类型、发送者、内容）
- **FileTransferInfo**：文件传输信息（文件名、大小、发送者）

## 常见问题

### Q: 无法发现其他成员？
A: 检查防火墙设置，确保UDP 8888端口未被阻止

### Q: 文件传输失败？
A: 检查TCP 8889端口是否被占用，确保网络连接正常

### Q: 消息发送失败？
A: 确认目标成员在线，检查网络连接

## ⚠️ 重要更新：架构优化

### 必读文档（按顺序）
1. **`docs/项目开发总览.md`** - 📚 开始从这里！完整的开发指南
2. **`docs/架构优化后的成员任务.md`** - 查看你的具体任务和示例代码
3. **`docs/接口对接检查清单.md`** - 确认接口定义和对接关系
4. **`docs/详细测试方法指南.md`** - 学习如何测试你的模块
5. **`docs/理想实现结果清单.md`** - 对照此清单自查完成度

### 关键变化
- ✅ 新增 `MessageDispatcher` 统一管理UDP通信
- ✅ 各模块不再自己管理socket
- ✅ 消息通过信号分发到各模块
- ✅ 接口更加清晰，对接风险大大降低

### 开发流程
1. 阅读架构优化文档
2. 找到你的模块文件
3. 实现TODO标记的函数
4. 参考文档中的示例代码
5. 本地测试后提交

## 许可证

本项目仅用于教学实验目的。

## 联系方式

如有问题，请联系小组成员或提交Issue。