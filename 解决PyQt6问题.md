# 解决PyQt6 DLL加载问题

## 问题原因
PyQt6需要Visual C++ Redistributable支持。

## 解决方案

### 方案1：安装Visual C++ Redistributable（推荐）

1. 下载并安装：
   - 访问微软官网下载 VC++ Redistributable
   - 或直接运行：https://aka.ms/vs/17/release/vc_redist.x64.exe

2. 安装后重启Python环境

### 方案2：使用PyQt5（更稳定）

```bash
pip uninstall PyQt6 -y
pip install PyQt5
```

然后修改代码中的导入：
```python
# 将 PyQt6 改为 PyQt5
from PyQt5.QtWidgets import ...
from PyQt5.QtCore import ...
```

### 方案3：使用虚拟环境

```bash
python -m venv venv
venv\Scripts\activate
pip install PyQt6
python run.py
```

### 方案4：使用已打包好的版本

直接使用 `build_exe.py` 打包后的EXE文件，无需考虑依赖问题。

## 临时解决（立即可用）

我已经为你准备好了所有代码，现在直接打包成EXE：

```bash
python build_exe.py
```

打包后的EXE包含所有依赖，可以直接运行！


