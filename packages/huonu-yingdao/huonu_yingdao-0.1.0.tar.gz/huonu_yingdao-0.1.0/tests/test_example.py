"""
示例测试模块
"""
from huonu_yingdao import example

def test_some_function():
    """测试 some_function 函数"""
    result = example.some_function()
    assert isinstance(result, str)
    assert "Hello" in result 