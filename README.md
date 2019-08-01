# hupu
一个基于Scrapy框架的虎扑爬虫

### 概览  
基于 Scrapy 框架，并通过分布式扩展，使爬虫可以在多台机器上部署。  
数据来源是虎扑安卓客户端，爬取目标是虎扑的全量用户，所以并没有对回帖等内容过多解析。

### 更新日志  
- 2019.07.25：将 `scrapy-redis` 的去重组件更换为布隆过滤器。    
- 2019.07.26：在生成请求指纹过程中，可在设置中指定删除url参数或formdata参数。  

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
| bbs\_fans\_url        | 粉丝数url            |
| bbs\_job              | 论坛职位              |
| reputation            | 声望                |
| update_time           | 数据更新时间          |
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
| update_time   | 数据更新时间    |



### 使用  
```
pip install -r requirements.txt  
python run.py
```

### 某些细节  
#### 关注列表和粉丝列表  
虎扑的服务器最近可能有些问题，很多页面都是 `正在进行数据维护，部分内容暂时无法浏览`。   
所以可能会出现数据不准确的情况，以粉丝数为例，`fans_count` 所显示的关注数与实际得到的关注列表 `bbs_fans`数据可能不同（我的`fans_count`是3，然而`bbs_fans`关注列表只有两个人），当然另一方面原因是生产环境下的关注数或粉丝数的动态变化。  
基于以上情况，对于用户关注列表和粉丝列表的获取，没有使用异步请求。原因在于无法通过`fans_count`和`bbs_fans`的数量对比来确定保存用户数据的时机。  
在同步获取列表时，每次请求只能返回20个粉丝，一些优质账号的粉丝数可能多达十几万，这就成为了十分耗时的一个步骤，所以此处的请求去重尤为关键，针对 `puid`的去重在两处实现：  

- 下载中间件  
	截取请求中的 `puid`，并与数据库数据对比，判断是否需要继续发送请求。此处去重是为了避免redis持久化出问题。
	
- 请求指纹去重  
	每次请求的 `ssid` 和 `clientId` 等参数都是随机生成的，所以针对同一`puid`的请求，其他参数是不同的，这样指纹去重就没有意义了，因此通过在设置中添加过滤参数，在生成请求指纹前删除指定的几个参数。指纹去重首先速度比直接去数据库检索对比要快，其次避免了在分布式情况下，多台机器跑同一个`puid`的情况。
