# hupu
一个基于Scrapy框架的虎扑爬虫

### 概览  
基于 Scrapy 框架，并通过 scrapy-redis 组件，使爬虫可以分布式扩展。  
数据来源是虎扑安卓客户端，爬取目标是虎扑的全量用户，所以并没有对回帖等内容过多解析。

### 数据库字段说明  
#### users   
| 字段名                   | 说明                |
|-----------------------|-------------------|
| puid                  | 用户id              |
| nickname              | 昵称                |
| header\_url           | 头像url             |
| level                 | 等级                |
| register\_days        | 注册日期              |
| gender                | 性别（0：未设置，1：男，2：女） |
| location              | 地点                |
| follow\_count         | 关注人数              |
| fans\_count           | 粉丝人数              |
| be\_light\_count      | 被点亮数              |
| be\_recommend\_count  | 被推荐数              |
| bbs\_msg\_count       | 发帖数               |
| bbs\_post\_count      | 回帖数               |
| bbs\_recommend\_count | 推荐数               |
| news\_comment\_count  | 新闻评论数             |
| bbs\_msg\_url         | 发帖url             |
| bbs\_post\_url        | 评论url             |
| bbs\_recommend\_url   | 推荐url             |
| news\_comment\_url    | 新闻评论url           |
| bbs\_follow\_url      | 关注列表url           |
| bbs\_followers        | 关注列表              |
| bbs\_fans\_url        | 粉丝数url            |
| bbs\_fans             | 粉丝列表              |
| bbs\_job              | 论坛职位              |
| reputation            | 声望                |
---

#### topics  
| 字段名           | 说明    |
|---------------|-------|
| light\_replys | 高亮回复数 |
| recommends    | 被推荐数  |
| replys        | 回复数   |
| tid           | 话题id  |
| launch\_time  | 发布时间  |
| title         | 帖子标题  |
| user\_name    | 发帖人   |


### 使用  
```
pip install -r requirements.txt  
python run.py
```

