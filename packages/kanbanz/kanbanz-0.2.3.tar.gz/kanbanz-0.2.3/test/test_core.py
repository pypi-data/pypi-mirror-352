
import pytest

from kanbanz import Kanban,Pool

@pytest.fixture
def kanban_create():
    kanban_path = "/Users/zhaoxuefeng/GitHub/obsidian/实验室/ceshi.md"
    cm = Kanban(kanban_path)
    cm.pull()

    yield cm
    cm.push()


def test_insert(kanban_create):
    print(kanban_create.insert('知识',Pool.预备池))


def test_pop(kanban_create):
    print(kanban_create.pop('等待反馈',Pool.预备池))


def test_get_tasks_in(kanban_create):
    print(kanban_create.get_tasks_in(Pool.预备池))


def test_get_task_by_word(kanban_create):
    print(kanban_create.get_task_by_word('知识',Pool.预备池))

