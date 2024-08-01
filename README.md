# 裁判文书质量评估平台

### 环境设置

语言环境：python 3.6

框架：flask

异步任务调度：celery 3.1.25 + 本地redis（python中redis包要求2.*，不然会有奇怪的错误item错误）

接口文件自动生成：flasgger

模块划分：blueprint

数据库：SQLAlchemy +本地mySQL

其他依赖包：requirements.txt

### 简介

评估平台后端，为民事一审裁判文书提供客观质量度量和主观质量度量服务，接口文件说明在api_description中。

### 运行

0. 修改配置文件

   修改`config/global_vars.py`中的数据库配置和redis配置等

1. 安装依赖包

   ```shell
   pip install -r requirements.txt
   ```

2. 运行Python

   ```shell
   python run.py
   ```

3. 启动Redis

4. 启动MySQL

5. 运行Celery

   ```shell
   celery -A my_celery_server.tasks worker -l info
   ```

### 访问API Docs

后端运行后点击[http://localhost:5000/apidocs/](http://localhost:5000/apidocs/)查看API文档
