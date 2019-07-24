# hupu
一个基于Scrapy的虎扑爬虫

### 概览  
基于 Scrapy 框架，并通过 scrapy-redis 组件，使爬虫可以分布式扩展。
数据来源是虎扑安卓客户端，爬取目标是虎扑的全量用户，所以并没有对回帖等内容过多解析。

### 使用  
> pip install -r requirements.txt
> python run.py
