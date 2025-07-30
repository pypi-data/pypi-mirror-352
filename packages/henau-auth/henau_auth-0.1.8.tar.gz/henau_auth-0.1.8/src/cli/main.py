import os
from pathlib import Path
import typer


def create_file_tree(directory_structure, root_path="."):
    """
    根据多维字典创建文件树

    参数:
        directory_structure: 多维字典，键是文件/文件夹名，字符串值作为文件内容
        root_path: 文件树的根目录路径，默认为当前目录
    """
    root_path = Path(root_path)

    for name, content in directory_structure.items():
        current_path = root_path / name

        if isinstance(content, dict):
            # 如果是字典，创建文件夹并递归处理
            os.makedirs(current_path, exist_ok=True)
            create_file_tree(content, current_path)
        elif isinstance(content, str):
            # 如果是字符串，创建文件并写入内容
            with open(current_path, "w", encoding="utf-8") as f:
                f.write(content)
        else:
            # 其他类型，转换为字符串写入
            with open(current_path, "w", encoding="utf-8") as f:
                f.write(str(content))


app = typer.Typer()


@app.command()
def fastapi():
    """
    生成 FastAPI 项目文件
    """
    from .template.fastapi import fastapi_template

    create_file_tree(fastapi_template, root_path=".")


@app.command()
def list():
    """
    列出所有命令
    """
    print("fastapi: 生成 FastAPI 项目文件")


def main(*args, **kwargs):
    app(*args, **kwargs)
