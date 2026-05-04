# WeChatSender MVVM 版本

## 运行

```bash
python main.py
```

## 打包

```bash
python -m PyInstaller -F --noconsole --name AutoWeChatSender --paths . main.py
```

## 测试
```bash
python -m unittest discover -s tests -v
```

## 目录说明

```text
models/         数据模型
services/        业务服务：微信、配置、日志、定时器
viewmodels/     ViewModel，连接界面和业务服务
views/          tkinter 界面和托盘
data/           外部可修改配置文件
log/            日志文件
main.py         程序入口
tests/          测试文件
```

## 配置文件

打包后配置文件位于：

```text
exe所在目录/data/config.json
```

程序第一次运行时会自动创建。
