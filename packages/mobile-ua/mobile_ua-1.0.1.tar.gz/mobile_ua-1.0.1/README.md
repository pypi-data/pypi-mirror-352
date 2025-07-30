

# 安装mobile_ua请求头

## 安装

使用pip安装

```
pip install mobile_ua
```

或者克隆这个项目并且执行setup.py安装

```
python setup.py install
```

## 使用

```python
"""
@Time    : 2025/6/2 13:51
@Author  : white.tie
@File    : test.py
@Desc    :
"""
from mobile_ua import useragent
# 获取随机Ua
print(useragent.random_ua())
# 获取指定UA
print(useragent.get_ua(2))
```

