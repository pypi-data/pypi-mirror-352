"""
kanban manager
"""
from enum import Enum
from .utils import read,write

class Pool(Enum):
    """
    预备池,就绪池,阻塞池,执行池,完成池,酱油池
    """
    预备池 ='预备池'
    就绪池 ='就绪池'
    阻塞池 ='阻塞池'
    执行池 ='执行池'
    完成池 ='完成池'
    酱油池 ='酱油池'


class Kanban():
    """
    看板管理工具
    """
    def __init__(self,kanban_path:str):
        """
        kanban_path 路径
        """
        self.kanban_path = kanban_path
        self.kanban_dict = {}

    def pull(self) -> None:
        """
        从文档拉取信息到 kanban_dict 属性。

        该方法打开指定的看板路径文件，读取其内容，并使用 _read 方法解析文本，
        将解析后的数据存储到 kanban_dict 属性中。
        """
        with open(self.kanban_path, 'r', encoding="utf-8") as f:
            text = f.read()
        self.kanban_dict = read(text)

    def push(self) -> None:
        """
        将 kanban_dict 属性中的信息写入到文档。

        该方法使用 _write 方法将 kanban_dict 属性中的数据转换为文本格式，
        然后将该文本写入到指定的看板路径文件中。
        """
        text = write(self.kanban_dict)
        with open(self.kanban_path, 'w', encoding="utf-8") as f:
            f.write(text)

    

    def insert(self, text: str, pool: Pool) -> None:
        """
        在指定的池中插入一条新的任务信息。

        Args:
            text (str): 任务的描述信息。
            pool (Pool): 要插入任务的池。

        Returns:
            None
        """
        self.kanban_dict[pool.value].append({'status': ' ',
                                             'description': text, 
                                             'id': 12, 'level': 2})

    def pop(self, text: str, pool: Pool) -> list["task"]:
        """
        从指定的池中删除一条任务信息。

        Args:
            text (str): 用于匹配的任务信息，可以是描述或ID。
            pool (Pool): 要从中删除任务的池。

        Returns:
            None
        """
        def delete_by_description(data: list, description: str) -> list:
            for i, item in enumerate(data):
                if item.get('description') == description:
                    del data[i]
                    return data
            print(f"未找到描述为 '{description}' 的数据列")
            return data

        data = self.kanban_dict[pool.value]
        return delete_by_description(data, text)

    def get_tasks_in(self, pool:Pool)->list[str]:
        """获取事件池中的任务

        Args:
            pool (Pool): 枚举的池类型

        Returns:
            list[str]: 返回对应的事件名称列表
        """

        pools = self.kanban_dict.get(pool.value)
        return [des.get("description") for des in pools]

    def get_task_by_word(self,word:str, pool:Pool = None)->list[str]:
        """查询任务通过关键字

        Args:
            word (str): 关键字
            pool (Pool, optional): 任务池,枚举类型. Defaults to None.

        Returns:
            list[str]: 返回查询到的任务列表
        """
        output = []
        if pool is None:
            for _ , content in self.kanban_dict.items():
                for core in content:
                    if word in core.get('description'):
                        output.append(core.get("description"))
        else:
            content = self.kanban_dict.get(pool.value)
            for core in content:
                if word in core.get('description'):
                    output.append(core.get("description"))

        return output
