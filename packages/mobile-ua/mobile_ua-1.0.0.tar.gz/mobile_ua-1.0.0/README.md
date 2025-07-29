*** 1.0.4 版本新增功能** *

版本新增配置任务队列优先级,以用来支持有优先级的消息队列

```
#在settings.py 新增系列配置即可
'QUEUE_X_MAX_PRIORITY': 10
```

## Scrapy分布式RabbitMQ调度器

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

