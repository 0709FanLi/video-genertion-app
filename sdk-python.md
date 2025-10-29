Python
SDK地址：https://github.com/volcengine/volc-sdk-python同步接口(直接返回结果) Action=CVProcess
调用示例
示例在SDK中的路径：https://github.com/volcengine/volc-sdk-python/blob/main/volcengine/example/visual/cv_process.py# coding:utf-8
from __future__ import print_function

from volcengine.visual.VisualService import VisualService

if __name__ == '__main__':
    visual_service = VisualService()

    # call below method if you don't set ak and sk in $HOME/.volc/config
    visual_service.set_ak('your ak')
    visual_service.set_sk('your sk')
    
    # 请求Body(查看接口文档请求参数-请求示例，将请求参数内容复制到此)
    form = {
        "req_key": "xxx",
        # ...
    }

    resp = visual_service.cv_process(form)
    print(resp)

异步提交任务(返回taskId) Action=CVSubmitTask
调用示例
示例在SDK中的路径：https://github.com/volcengine/volc-sdk-python/blob/main/volcengine/example/visual/cv_submit_task.py# coding:utf-8
from __future__ import print_function

from volcengine import visual
from volcengine.visual.VisualService import VisualService

if __name__ == '__main__':
    visual_service = VisualService()

    # call below method if you don't set ak and sk in $HOME/.volc/config
    visual_service.set_ak('your ak')
    visual_service.set_sk('your sk')
    
    # 请求Body(查看接口文档请求参数-请求示例，将请求参数内容复制到此)
    form = {
        "req_key": "xxx",
        # ...
    }
    resp = visual_service.cv_submit_task( form)
    print(resp)

异步查询任务(返回结果) Action=CVGetResult
调用示例
示例在SDK中的路径：https://github.com/volcengine/volc-sdk-python/blob/main/volcengine/example/visual/cv_get_result.py# coding:utf-8
from __future__ import print_function

from volcengine import visual
from volcengine.visual.VisualService import VisualService

if __name__ == '__main__':
    visual_service = VisualService()

    # call below method if you don't set ak and sk in $HOME/.volc/config
    visual_service.set_ak('your ak')
    visual_service.set_sk('your sk')
    
    # 请求Body(查看接口文档请求参数-请求示例，将请求参数内容复制到此)
    form = {
        "req_key": "xxx",
        "task_id": "xxx"
    }
    resp = visual_service.cv_get_result(form)
    print(resp)

同步转异步提交任务(返回taskId)Action=CVSync2AsyncSubmitTask
调用示例
示例在SDK中的路径：https://github.com/volcengine/volc-sdk-python/blob/main/volcengine/example/visual/cv_sync2async_submit_task.py# coding:utf-8
from __future__ import print_function

from volcengine import visual
from volcengine.visual.VisualService import VisualService

if __name__ == '__main__':
    visual_service = VisualService()

    # call below method if you don't set ak and sk in $HOME/.volc/config
    visual_service.set_ak('your ak')
    visual_service.set_sk('your ak')
    
    # 请求Body(查看接口文档请求参数-请求示例，将请求参数内容复制到此)
    form = {
        "req_key": "xxx",
        # ...

    }
    resp = visual_service.cv_sync2async_submit_task(form)
    print(resp)

同步转异步查询任务(返回结果)Action=CVSync2AsyncGetResult
调用示例
示例在SDK中的路径：https://github.com/volcengine/volc-sdk-python/blob/main/volcengine/example/visual/cv_sync2async_get_result.py# coding:utf-8
from __future__ import print_function

from volcengine import visual
from volcengine.visual.VisualService import VisualService

if __name__ == '__main__':
    visual_service = VisualService()

    # call below method if you don't set ak and sk in $HOME/.volc/config
    visual_service.set_ak('your ak')
    visual_service.set_sk('your ak')
    
    # 请求Body(查看接口文档请求参数-请求示例，将请求参数内容复制到此)
    form = {
        "req_key": "xxx",
        "task_id": "xxx",
        "req_json": "{\"logo_info\":{\"add_logo\":true，\"position\":1, \"language\":1,\"opacity\"：0.5}}"
    }
    resp = visual_service.cv_sync2async_get_result(form)
    print(resp)

