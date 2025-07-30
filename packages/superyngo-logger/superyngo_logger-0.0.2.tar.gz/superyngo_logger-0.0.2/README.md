# Superyngo Logger

[![PyPI version](https://badge.fury.io/py/superyngo-logger.svg)](https://badge.fury.io/py/superyngo-logger)
[![Python Support](https://img.shields.io/pypi/pyversions/superyngo-logger.svg)](https://pypi.org/project/superyngo-logger/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

A simple and efficient logging utility for Python applications. My Logger provides an easy-to-use logging solution with file rotation, custom formatting, and log cleanup capabilities.

## ✨ Features

- **簡單初始化**: 一行代碼即可設置完整的日誌系統
- **文件輪轉**: 自動管理日誌文件大小和數量
- **日誌清理**: 自動清理舊的日誌文件
- **彩色輸出**: 控制台輸出支援彩色日誌
- **靈活配置**: 支援自定義日誌格式和輸出路徑
- **Multiton 模式**: 相同路徑的 logger 實例復用

## 🚀 Installation

```bash
pip install superyngo-logger
```

## 📖 Quick Start

### Basic Usage

```python
from superyngo_logger import init_logger
from pathlib import Path

# 初始化 logger（使用預設設置）
logger = init_logger()

# 開始記錄日誌
logger.info("這是一條資訊日誌")
logger.warning("這是一條警告日誌")
logger.error("這是一條錯誤日誌")
```

### Advanced Usage

```python
from superyngo_logger import init_logger, clean_logs
from pathlib import Path

# 自定義日誌目錄和應用名稱
log_dir = Path("./logs")
logger = init_logger(
    log_dir=log_dir,
    app_name="my_app"
)

# 記錄不同級別的日誌
logger.debug("調試資訊")
logger.info("程式正常運行")
logger.warning("注意：某些條件可能需要關注")
logger.error("發生錯誤")
logger.critical("嚴重錯誤！")

# 清理10天前的舊日誌文件
clean_logs(log_dir, days_count=10)
```

### Custom Configuration

```python
from superyngo_logger import init_logger
from pathlib import Path

# 使用自定義配置文件
config_path = Path("./my_logging.conf")
logger = init_logger(
    log_dir=Path("./custom_logs"),
    config_path=config_path,
    app_name="custom_app"
)
```

## 📝 API Reference

### `init_logger(log_dir=None, config_path=None, app_name="myapp")`

初始化並返回一個 logger 實例。

**參數:**

- `log_dir` (Path, optional): 日誌文件目錄。預設為執行檔案目錄下的 "Logs" 資料夾
- `config_path` (Path, optional): 自定義配置文件路徑。如果不存在則使用預設配置
- `app_name` (str): 應用程式名稱，用於日誌文件命名。預設為 "myapp"

**返回:**

- `Logger`: 配置好的 logger 實例

### `clean_logs(log_dir, days_count=10)`

清理指定目錄中的舊日誌文件。

**參數:**

- `log_dir` (Path): 包含日誌文件的目錄路徑
- `days_count` (int): 保留日誌文件的天數。預設為 10 天

## 🔧 Configuration

Logger 支援兩種配置方式：

### 1. 預設配置（字典格式）

程式內建的預設配置包含：

- 控制台處理器：彩色輸出，DEBUG 級別
- 文件處理器：純文字輸出，INFO 級別
- 自動日誌輪轉和時間戳

### 2. 配置文件格式

您可以提供一個 `.conf` 格式的配置文件來自定義日誌行為：

```ini
[loggers]
keys=root

[handlers]
keys=consoleHandler,fileHandler

[formatters]
keys=formatter

[logger_root]
level=DEBUG
handlers=consoleHandler,fileHandler

[handler_consoleHandler]
class=StreamHandler
level=DEBUG
formatter=formatter
args=(sys.stdout,)

[handler_fileHandler]
class=FileHandler
level=INFO
formatter=formatter
args=('app.log', 'a')

[formatter_formatter]
format=%(asctime)s - %(levelname)s - %(message)s
```

## 📁 Project Structure

```
superyngo-logger/
├── src/
│   └── superyngo_logger/
│       ├── __init__.py          # 套件入口
│       ├── logger_module.py     # 主要功能模組
│       └── config.py           # 配置和格式化
├── tests/                      # 測試文件
├── docs/                       # 文檔
├── README.md
├── LICENSE
├── CHANGELOG.md
└── pyproject.toml
```

## 🧪 Development

### 安裝開發依賴

```bash
pip install -e ".[dev]"
```

### 運行測試

```bash
pytest
```

### 代碼格式化

```bash
black src tests
isort src tests
```

### 類型檢查

```bash
mypy src
```

## 📄 License

本專案使用 MIT 授權條款 - 詳見 [LICENSE](LICENSE) 文件。

## 🤝 Contributing

歡迎貢獻！請先閱讀我們的貢獻指南。

1. Fork 這個專案
2. 創建您的功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交您的更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 開啟一個 Pull Request

## 📮 Support

如果您有任何問題或建議，請通過以下方式聯繫：

- 📧 Email: superyngo@gmail.com
- 🐛 Issues: [GitHub Issues](https://github.com/superyngo/my_logger/issues)

## 📝 Changelog

查看 [CHANGELOG.md](CHANGELOG.md) 以了解每個版本的更改內容。

---

**Made with ❤️ by Wenyang**
