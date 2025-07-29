import pip

pip.main(["install", "rich"])

from setuptools import setup, find_packages
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeRemainingColumn

# 初始化彩色进度条组件,固定为0
progress = Progress(
    SpinnerColumn(),
    TextColumn("[progress.description]{task.description}"),
    BarColumn(),
    TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
    TimeRemainingColumn(),
    transient=True  # 设置为临时显示
)

# 创建任务
task = progress.add_task("[cyan]Installing...", total=100)

# 启动进度条
with progress:
    setup(
        name='randtools-test',
        version='0.9.15',
        packages=find_packages(),
        url='',
        license='BSD 3-Clause License',
        author='Creative Star Studio',
        author_email='qu20121118@yeah.net',
        description='A Python module for generating random data with various features including random integers, letters, ASCII characters, bytes, floats, booleans, and URLs',
        install_requires=[
            'ping3',
        ],
    )
    # 设置进度为100%
    progress.update(task, completed=100)
