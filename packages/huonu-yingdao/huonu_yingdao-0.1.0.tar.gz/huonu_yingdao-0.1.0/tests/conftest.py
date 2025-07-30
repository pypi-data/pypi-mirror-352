"""
pytest 配置文件
"""
import pytest

def pytest_configure(config):
    """配置 pytest"""
    config.addinivalue_line(
        "markers", "slow: 标记耗时较长的测试"
    ) 