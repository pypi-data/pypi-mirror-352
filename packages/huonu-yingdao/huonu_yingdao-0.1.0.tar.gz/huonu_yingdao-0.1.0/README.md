# My Package

这是一个示例 Python 包。

## 安装

```bash
pip install huonu_yingdao
```

## 使用方法

```python
from my_package import example

# 使用示例
result = example.some_function()
```

## 开发

1. 克隆仓库
2. 安装开发依赖：
   ```bash
   pip install -r requirements.txt
   pip install -e .
   ```
3. 运行测试：
   ```bash
   pytest
   ```

## 构建和发布

1. 安装构建工具：
   ```bash
   pip install build twine
   ```

2. 构建分发包：
   ```bash
   python -m build
   ```

3. 发布到 PyPI：
   ```bash
   # 测试发布到 TestPyPI
   python -m twine upload --repository testpypi dist/*
   
   # 正式发布到 PyPI
   python -m twine upload dist/*
   ```

## 许可证

MIT License 