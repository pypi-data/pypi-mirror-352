
from .core import Pool, Kanban
from .utils import sync_obsidian_github,controlKanban
from grapherz.canvas.core import Canvas,Color



def give_a_task_time(task:str)->str:
    from llmada import GoogleAdapter
    from promptlibz import Templates,TemplateType
    llm = GoogleAdapter()
    template = Templates(TemplateType.ESTIMATE_DURATION)
    prompt = template.format(task=task)

    completion = llm.product(prompt)
    if completion and len(completion)<5:
        return completion + " "+ task
    else:
        return "2P" + " "+ task


class KanBanManager():
    def __init__(self,kanban_path,pathlib):
        self.pathlib = pathlib
        self.kanban = Kanban(kanban_path)
        self.main_path = "/Users/zhaoxuefeng/GitHub/obsidian/工作"


    def get_info_from_pathlib(self):
        pass
        

    def sync_ready(self):
        def encode(i,project_name):
            return project_name+'-'+i
        
        def save_in_pauses(i,pauses):
            for pause in pauses:
                if i.get('text') in pause:
                    return True
            return False

        for path in self.pathlib:
            canvas_path=self.main_path+path
            try:
                canvas = Canvas(file_path=canvas_path)
            except FileNotFoundError as e:
                print(e)
                continue
            with controlKanban(self.kanban) as kb:
                project_name = canvas_path.rsplit('/',2)[-2] 
                pauses = kb.get_tasks_in(pool=Pool.阻塞池)
                readys = kb.get_tasks_in(pool=Pool.预备池)

                nodes = [i.get('text') or '' for i in canvas.select_by_color(Color.yellow,type='node') if not save_in_pauses(i,pauses=pauses)]
                for i in nodes:
                    if i not in readys:
                        kb.insert(text=encode(i,project_name),pool=Pool.预备池)
        return 'success'

    def sync_order(self):
        with sync_obsidian_github("调整优先级"):
            with controlKanban(self.kanban) as kb:
                tasks = kb.get_tasks_in(Pool.预备池)
                order_tasks = kb.get_tasks_in(Pool.就绪池)
                orders = ' '.join(order_tasks)
                for task in tasks:
                    kb.pop(text = task,pool = Pool.预备池)
                    if task not in orders:
                        task_ = give_a_task_time(task)
                        kb.insert(text=task_,pool=Pool.就绪池)
        return 'success'

    def sync_run(self)->str:
        with sync_obsidian_github("同步到执行池"):
            with controlKanban(self.kanban) as kb:
                tasks = kb.get_tasks_in(Pool.就绪池)
                all_task_time = 0
                for task in tasks:
                    if task.split(' ')[0][-1].lower() != 'p':
                        continue
                    task_time = int(task.split(' ')[0][:-1])

                    if all_task_time + task_time <=14:
                        all_task_time += task_time
                        kb.pop(text=task,pool=Pool.就绪池)
                        kb.insert(text=task,pool=Pool.执行池)

                    elif all_task_time < 8:
                        pass
        return 'success'

    def sync_run2order(self):
        with controlKanban(self.kanban) as kb:
            tasks = kb.get_tasks_in(Pool.执行池)
            if tasks:
                for task in tasks:
                    kb.pop(text=task,pool=Pool.执行池)
                    kb.insert(text=task,pool=Pool.就绪池)
            
        return 'success'

    def sync_run2over(self,task:str,
                      canvas_path:str):

        """从执行池添加到完成池
        # multi_line_input = "备案-新域名做域名备案$/工程系统级设计/项目级别/数字人生/模拟资质认证/模拟资质认证.canvas\n"

        1 将task从执行池添加到完成池
        2 将canvas 中的颜色变绿
        Args:
            kanban_path (str): 看板路径

        Returns:
            None: None
        """
        
        canvas_path = canvas_path.replace('\n','')
        canvas_path =self.main_path+canvas_path


        with controlKanban(self.kanban) as kb:
            task = task.split('-',1)[-1]
            if len(kb.get_task_by_word(task,pool=Pool.执行池)) == 0:
                kb.insert(text=task,pool=Pool.完成池)
                kb.push()
                return 'failed'

            task_ = kb.get_task_by_word(task,pool=Pool.执行池)[0]
            kb.pop(text=task_,pool=Pool.执行池)
            kb.insert(text=task_,pool=Pool.完成池)

            # and
            canvas = Canvas(file_path=canvas_path)
            tasks = canvas.select_nodes_by_text(task)
            try:
                tasks[0].color = Color.green.value
            except IndexError as e:
                return f'error: {e}'
            canvas.to_file(canvas_path)

        return 'success'

    def add_tips(self,task:str):
        """从执行池添加到完成池
        1 将task从执行池添加到完成池
        2 将canvas 中的颜色变绿
        Args:
            kanban_path (str): 看板路径

        Returns:
            None: None
        """
        with controlKanban(self.kanban) as kb:
            kb.insert(text=task,pool=Pool.预备池)
        return 'success'
