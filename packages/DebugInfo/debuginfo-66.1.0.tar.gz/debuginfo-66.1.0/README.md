# 调试模块

## 介绍

一个用于消息整理和打印输出的模块，主要功能包括 文本对齐，表格对齐，文本修饰，生成分隔线，文本颜色修饰等，另外，还提供了一个秒表装饰器 和一个语义日期模板。

## 文档架构

调试模块.py # 主功能代码

## 依赖说明
本程序依赖以下库:
- colorama
- wcwidth
- pyperclip
- argparse
- 其它标准库


## 安装教程
```bash
pip install DebugInfo
```

## 使用说明

### 文本上色
```python
# -*- coding:UTF-8 -*-

# region 引入必要依赖
from DebugInfo.DebugInfo import *

# endregion

# 将要打印的文本做为 函数 红字 的入参
print(红字('这是串红色的文字'))
```
以上代码，将要打印的文本通过方法 红字 修饰后做为 print 的参数，则可以打印出红色的字体，如下：  
![输入图片说明](demo%20%E7%BA%A2%E5%AD%97.jpg)

**DebugInfo**模型还提供了以下的颜色修饰支持，以下代码分别进行的方法名和效果的打印展示：
```python
# -*- coding:UTF-8 -*-

# region 引入必要依赖
from DebugInfo.DebugInfo import *

# endregion

画板 = 打印模板()

画板.添加一行('红字', 红字('红字'))
画板.添加一行('红底', 红底('红底'))

画板.添加一行('红底白字', 红底白字('红底白字'))
画板.添加一行('红底黑字', 红底黑字('红底黑字'))
画板.添加一行('红底黄字', 红底黄字('红底黄字'))
画板.添加一行('绿字', 绿字('绿字'))
画板.添加一行('绿底', 绿底('绿底'))
画板.添加一行('黄字', 黄字('黄字'))

画板.添加一行('黄底', 黄底('黄底'))
画板.添加一行('蓝字', 蓝字('蓝字'))
画板.添加一行('蓝底', 蓝底('蓝底'))

画板.添加一行('洋红字', 洋红字('洋红字'))
画板.添加一行('洋红底', 洋红底('洋红底'))
画板.添加一行('青字', 青字('青字'))
画板.添加一行('青底', 青底('青底'))
画板.添加一行('白字', 白字('白字'))
画板.添加一行('白底黑字', 白底黑字('白底黑字'))

画板.添加一行('黑字', 黑字('黑字'))
画板.添加一行('黑底', 黑底('黑底'))
画板.添加一行('绿底白字', 绿底白字('绿底白字'))

画板.展示表格()
```
代码运行如下：  
![输入图片说明](demo%20%E6%96%87%E5%AD%97%E4%B8%8A%E8%89%B2%E6%89%93%E5%8D%B0%E6%95%88%E6%9E%9C.jpg)

事实上，不同的颜色修饰是可以嵌套的，例如下面的代码将红字进行三重修饰。
```python
# -*- coding:UTF-8 -*-

# region 引入必要依赖
from DebugInfo.DebugInfo import *

# endregion

文本 = 红字('红字')
文本 = 黄字(f'黄字{文本}')
文本 = 蓝字(f'蓝字{文本}')

print(文本)
```

上面的代码运行效果如下，最内层是红字，中间是黄字，外层是蓝字：  
![输入图片说明](demo%20%E6%96%87%E5%AD%97%E9%A2%9C%E8%89%B2%E7%9A%84%E5%B5%8C%E5%A5%97%E4%BF%AE%E9%A5%B0.jpg)

***
### 分隔线
**DebugInfo**模块提供了一个**分隔线模板**类，可以方便的生成分隔线。分隔线模板支持：
- 指定符号
- 指定提示内容
-- 指定对齐方式
- 修饰颜色
- 指定长度
-- 提示内容不影响分隔线长度,除非提示内容长于指定的总长度

🎯 以下代码中,使用分隔线模板生成了4条分隔线实例,使用 print 函数进行打印
```python
# -*- coding:UTF-8 -*-

# region 引入必要依赖
from DebugInfo.DebugInfo import *

# endregion

print(分隔线模板(), ': 这是默认的分隔线, 符号是 -, 长度是 50, 默认文本颜色')
print()
print(分隔线模板().符号('~ '), ': 这是一个定制的分隔线, 符号是 ~')
print()
print(分隔线模板().符号('-').提示内容('我是分隔线'), ': 这是一个定制的分隔线, 符号是 -, 有提示内容, 但提示内容不影响分隔线的长度')
print()
print(分隔线模板().符号('-').提示内容('我是分隔线').修饰(红字), ': 这是一个定制的分隔线, 符号是 -, 有提示内容, 文本颜色被修饰为红色了')
```
![输入图片说明](demo%20%E5%88%86%E9%9A%94%E7%BA%BF%E7%94%9F%E6%88%90.jpg)

🎯 下面的代码展示了分隔提示文本的对齐操作,和使用效果; 代码生成并打印了三条分隔线,其提示文本分别使用了不同的对齐方式
```python
# -*- coding:UTF-8 -*-

# region 引入必要依赖
from DebugInfo.DebugInfo import *

# endregion

print(分隔线模板().提示内容('提示内容在这里').文本对齐('l'), f": 分隔线提示文本是 {黄字('左对齐')} 的")
print()
print(分隔线模板().提示内容('提示内容在这里').文本对齐('c'), f": 分隔线提示文本是 {黄字('居中对齐')} 的")
print()
print(分隔线模板().提示内容('提示内容在这里').文本对齐('r'), f": 分隔线提示文本是 {黄字('右对齐')} 的")
```
![输入图片说明](demo%20%E5%88%86%E9%9A%94%E7%BA%BF%20%E6%8F%90%E7%A4%BA%E6%96%87%E6%9C%AC%E5%AF%B9%E9%BD%90.jpg)

🎯 下面的代码展示了如何控制分隔线的长度; 代码中分别生成了三条分隔线,使用了不同的长度(**等效英文空格宽度的数量**)
```python
# -*- coding:UTF-8 -*-

# region 引入必要依赖
from DebugInfo.DebugInfo import *

# endregion

print()
print(分隔线模板().提示内容('提示内容在这里'), '这是默认的长度, 50 英文空格宽度')
print()
print(分隔线模板().提示内容('提示内容在这里').总长度(60), '指定分隔线长度为 60 英文空格宽度')
print()
print(分隔线模板().提示内容('提示内容在这里').总长度(80), '指定分隔线长度为 80 英文空格宽度')
```
![输入图片说明](demo%20%E5%88%86%E9%9A%94%E7%BA%BF%20%E4%B8%8D%E5%90%8C%E9%95%BF%E5%BA%A6%E7%9A%84%E5%88%86%E9%9A%94%E7%BA%BF.jpg)

***
### 文本对齐，表格对齐
**DebugInfo**模块提供了文本对齐功能, 基础思想是通过英文空格来进行间隙填充,以使文本内容达到对齐的效果,这可以理解为一个表格。表格提供以下功能：
- 添加单行
-- 支持修饰
-- 支持字符串内换行符的换行对齐
- 添加多行
- 支持分隔行
- 修饰指定的列
- 控制对齐的列间距
- 控制对齐表列宽度
- 支持左右颠倒表格
- 支持上下颠倒表格

🎯 下面的代码演示了文本对齐的效果,支持中文,英文,数字,符号等各种混合字符串的对齐打印; 代码中构造了一个示例数据,数据是个二维list对象,第一列的同容中包含了**中文,英文,日文,数字**等内容,成分比较复杂.
```python
# -*- coding:UTF-8 -*-

# region 引入必要依赖
from DebugInfo.DebugInfo import *

# endregion

示例数据 = [['小张', '18745986526'],
            ['刘Sire', '技术宅,大牛'],
            ['中村 くみ子', '一个来自日本的同学, 喜欢学习中文'],
            ['zifang.zhang56', '重名太多,已经排到56号了, gg'],
            ['Kelly Jackson', "I don't know who is it"],
            ['123456', '一串数字']]

画板 = 打印模板()

画板.添加一行('项目', '内容', '->这一行是青色的,是标题哦').修饰行(青字)
for 项目 in 示例数据:
    画板.添加一行(项目[0], 项目[1])

画板.展示表格()
```
![输入图片说明](demo%20%E8%A1%A8%E6%A0%BC%20%E5%AF%B9%E9%BD%90%E6%89%93%E5%8D%B0%E6%95%88%E6%9E%9C.jpg)  
上图我们可以观察到,打印输出的第二列很整齐的对齐到了一起,不受第一列中内容的影响.
上面的代码和输出中,我们观察到我们对第一行的内容进行了修饰操作,这将使得第一行的内容高亮显示,这个效果可以做为标题的效果使用.

🎯 事实上,对齐二维list对象,是可以更灵活的添加到表格行中,如下演示了两种方法
```python
# -*- coding:UTF-8 -*-

# region 引入必要依赖
from DebugInfo.DebugInfo import *

# endregion

示例数据 = [['小张', '18745986526'],
            ['刘Sire', '技术宅,大牛'],
            ['中村 くみ子', '一个来自日本的同学, 喜欢学习中文'],
            ['zifang.zhang56', '重名太多,已经排到56号了, gg'],
            ['Kelly Jackson', "I don't know who is it"],
            ['123456', '一串数字']]

画板 = 打印模板()

# 方法一: 添加一行(list), 如下
for 数据行 in 示例数据:
    # 数据是个 list 对象
    画板.添加一行(数据行)

# 方法二: 添加多行(list[list]], 如下:
画板.添加多行(示例数据)
```

🎯 表格数据支持左右颠倒操作,例如下面的代码, 以及打印效果
```python
# -*- coding:UTF-8 -*-

# region 引入必要依赖
from DebugInfo.DebugInfo import *

# endregion

示例数据 = [['小张', '18745986526'],
            ['刘Sire', '技术宅,大牛'],
            ['中村 くみ子', '一个来自日本的同学, 喜欢学习中文'],
            ['zifang.zhang56', '重名太多,已经排到56号了, gg'],
            ['Kelly Jackson', "I don't know who is it"],
            ['123456', '一串数字']]

画板 = 打印模板()

画板.添加一行('项目', '内容').修饰行(青字)
画板.添加多行(示例数据)

画板.左右颠倒表格().展示表格()
```  
![输入图片说明](demo%20%E8%A1%A8%E6%A0%BC%20%E5%B7%A6%E5%8F%B3%E9%A2%A0%E5%80%92%E6%93%8D%E4%BD%9C.jpg)  


🎯 表格支持指定列宽操作,如下的代码里在准备表格时,指定了第2列的宽度为50,观察其效果:
```python
# -*- coding:UTF-8 -*-

# region 引入必要依赖
from DebugInfo.DebugInfo import *

# endregion

示例数据 = [['小张', '18745986526', '|'],
            ['刘Sire', '技术宅,大牛', '|'],
            ['中村 くみ子', '一个来自日本的同学, 喜欢学习中文', '|'],
            ['zifang.zhang56', '重名太多,已经排到56号了, gg', '|'],
            ['Kelly Jackson', "I don't know who is it", '|'],
            ['123456', '一串数字', '|']]

画板 = 打印模板()

画板.准备表格(列宽控制表=[0, 50])
画板.添加一行('项目', '内容', '参考列').修饰行(青字)
画板.添加多行(示例数据)

画板.展示表格()
```  
![输入图片说明](demo%20%E8%A1%A8%E6%A0%BC%20%E6%8C%87%E5%AE%9A%E5%88%97%E5%AE%BD.jpg)  
上图, 我们观察第三列的参考列,可以明显发现第2列的宽度是变宽了(实际上是指定数量的英文空格宽度)

🎯 表格支持指定列对齐方式,下面的代码中,我们在准备表格时指定列第2列的对齐方式为 'c': 居中对齐:
```python
# -*- coding:UTF-8 -*-

# region 引入必要依赖
from DebugInfo.DebugInfo import *

# endregion

示例数据 = [['小张', '18745986526', '|'],
            ['刘Sire', '技术宅,大牛', '|'],
            ['中村 くみ子', '一个来自日本的同学, 喜欢学习中文', '|'],
            ['zifang.zhang56', '重名太多,已经排到56号了, gg', '|'],
            ['Kelly Jackson', "I don't know who is it", '|'],
            ['123456', '一串数字', '|']]

画板 = 打印模板()

画板.准备表格(对齐控制串='lc', 列宽控制表=[0, 50])
画板.添加一行('项目', '内容', '参考列').修饰行(青字)
画板.添加多行(示例数据)

画板.展示表格()
```
观察下图, 第2列的内容相对于其指定的列宽,进行了居中对齐:  
![输入图片说明](demo%20%E8%A1%A8%E6%A0%BC%20%E5%88%97%E5%B1%85%E4%B8%AD%E5%AF%B9%E9%BD%90.jpg)  

🎯 事实上,表格还支持指定列间距,如下代码指定了第一个列间距为15, 第一个列间距为第2列与第1列之间的间距:
```python
# -*- coding:UTF-8 -*-

# region 引入必要依赖
from DebugInfo.DebugInfo import *

# endregion

示例数据 = [['小张', '18745986526', '|'],
            ['刘Sire', '技术宅,大牛', '|'],
            ['中村 くみ子', '一个来自日本的同学, 喜欢学习中文', '|'],
            ['zifang.zhang56', '重名太多,已经排到56号了, gg', '|'],
            ['Kelly Jackson', "I don't know who is it", '|'],
            ['123456', '一串数字', '|']]

画板 = 打印模板()

画板.准备表格()
画板.添加一行('项目', '内容', '参考列').修饰行(青字)
画板.添加多行(示例数据)

画板.表格列间距 = [15]
画板.展示表格()
```  
![输入图片说明](demo%20%E8%A1%A8%E6%A0%BC%20%E6%8C%87%E5%AE%9A%E5%88%97%E9%97%B4%E8%B7%9D.jpg)

🎯 表格数据支持上下颠倒操作,例如下面的代码, 以及打印效果
```python
# -*- coding:UTF-8 -*-

# region 引入必要依赖
from DebugInfo.DebugInfo import *

# endregion

示例数据 = [['小张', '18745986526'],
            ['刘Sire', '技术宅,大牛'],
            ['中村 くみ子', '一个来自日本的同学, 喜欢学习中文'],
            ['zifang.zhang56', '重名太多,已经排到56号了, gg'],
            ['Kelly Jackson', "I don't know who is it"],
            ['123456', '一串数字']]

画板 = 打印模板()

画板.添加一行('项目', '内容').修饰行(青字)
画板.添加多行(示例数据)

画板.上下颠倒表格().展示表格()
```  
![输入图片说明](demo%20%E8%A1%A8%E6%A0%BC%20%E4%B8%8A%E4%B8%8B%E9%A2%A0%E5%80%92%E6%93%8D%E4%BD%9C.jpg)  
我们观察到,第一行的**标题**行也被调整到了最后一行,这是因为模板中的表格并没有严格的标题概念,所有内容都是普通行,这是需要注意的一点.
这情况下,我们把**标题**行的内容放到其它内容之后添加,再上下颠倒操作,就可以解决.

🎯 表格支持修饰列操作,如下的代码将第2列(列索引号自0开始,所以第2列的列索引号是1,程序猿都懂)修饰为黄色的文字:
```python
# -*- coding:UTF-8 -*-

# region 引入必要依赖
from DebugInfo.DebugInfo import *

# endregion

示例数据 = [['小张', '18745986526', '第3列'],
            ['刘Sire', '技术宅,大牛', '第3列'],
            ['中村 くみ子', '一个来自日本的同学, 喜欢学习中文', '第3列'],
            ['zifang.zhang56', '重名太多,已经排到56号了, gg', '第3列'],
            ['Kelly Jackson', "I don't know who is it", '第3列'],
            ['123456', '一串数字', '第3列']]

画板 = 打印模板()

画板.添加一行('项目', '内容').修饰行(青字)
画板.添加多行(示例数据)

画板.修饰列(1, 黄字).展示表格()
```
上面的代码在**展示表格**前进行了**修饰列**操作,将指定的列使用方法 黄字 进行修饰,效果如下:  
![输入图片说明](demo%20%E8%A1%A8%E6%A0%BC%20%E4%BF%AE%E9%A5%B0%E5%88%97%E6%93%8D%E4%BD%9C.jpg)

🎯 表格支持添加分隔行操作,以下代码演示了如何为表格添加一个分隔行; 
代码先添加了部分数据,然后添加了一个分隔行,然后断续添加剩下的数据,最后展示表格内容
```python
# -*- coding:UTF-8 -*-

# region 引入必要依赖
from DebugInfo.DebugInfo import *

# endregion

示例数据 = [['小张', '18745986526'],
            ['刘Sire', '技术宅,大牛'],
            ['中村 くみ子', '一个来自日本的同学, 喜欢学习中文'],
            ['zifang.zhang56', '重名太多,已经排到56号了, gg'],
            ['Kelly Jackson', "I don't know who is it"],
            ['123456', '一串数字']]

画板 = 打印模板()
画板.添加一行('项目', '内容').修饰行(青字)

# 先添加一部分数据
for 序号 in range(3):
    画板.添加一行(示例数据[序号])

# 这里添加一个分隔行
画板.添加分隔行('-', 绿字)

# 继续添加行数据
for 序号 in range(3, len(示例数据)):
    画板.添加一行(示例数据[序号])

画板.展示表格()
```  
![输入图片说明](demo%20%E8%A1%A8%E6%A0%BC%20%E6%B7%BB%E5%8A%A0%E5%88%86%E9%9A%94%E8%A1%8C.jpg)  

表格还有一些其它的小功能支持,这里就不列举了,欢迎大家探索.

***
### 秒表计时器
**DebugInfo**模块封装 一个秒表计时器,这是一个装饰器,为快速函数性能测试提示了便利,下面是一个演示代码:

```python
# -*- coding:UTF-8 -*-

# region 引入必要依赖
from DebugInfo.DebugInfo import *

# endregion


@秒表
def 待测试的方法():
    # 打印 hello world 10 次
    for _ in range(10):
        print('hello world')


待测试的方法()
```
秒表装饰器提供的计算信息如下:
![输入图片说明](demo%20%E7%A7%92%E8%A1%A8.jpg)

***
### 语义日期
**DebugInfo**模块封装了一个语义日期模板,可以为指定的时间提供相对于今天的语义日期翻译.演示代码如下:

```python
# -*- coding:UTF-8 -*-

# region 引入必要依赖
from DebugInfo.DebugInfo import *
from datetime import datetime, timedelta

# endregion

画板 = 打印模板()

画板.添加一行('日期', '', '日期语义').修饰行(青字)
画板.添加一行(datetime.now().date() + timedelta(days=-365 * 5), '->', 语义日期模板(datetime.now() + timedelta(days=-365 * 5)))
画板.添加一行(datetime.now().date() + timedelta(days=-365), '->', 语义日期模板(datetime.now() + timedelta(days=-365)))
画板.添加一行(datetime.now().date() + timedelta(days=-180), '->', 语义日期模板(datetime.now() + timedelta(days=-180)))
画板.添加一行(datetime.now().date() + timedelta(days=-40), '->', 语义日期模板(datetime.now() + timedelta(days=-40)))
画板.添加一行(datetime.now().date() + timedelta(days=-20), '->', 语义日期模板(datetime.now() + timedelta(days=-20)))
画板.添加一行(datetime.now().date() + timedelta(days=-8), '->', 语义日期模板(datetime.now() + timedelta(days=-8)))
画板.添加一行(datetime.now().date() + timedelta(days=-2), '->', 语义日期模板(datetime.now() + timedelta(days=-2)))
画板.添加一行(datetime.now().date() + timedelta(days=-1), '->', 语义日期模板(datetime.now() + timedelta(days=-1)))
画板.添加一行(datetime.now().date() + timedelta(days=-0), '->', 语义日期模板(datetime.now() + timedelta(days=-0)))
画板.添加一行(datetime.now().date() + timedelta(days=1), '->', 语义日期模板(datetime.now() + timedelta(days=1)))
画板.添加一行(datetime.now().date() + timedelta(days=2), '->', 语义日期模板(datetime.now() + timedelta(days=2)))
画板.添加一行(datetime.now().date() + timedelta(days=3), '->', 语义日期模板(datetime.now() + timedelta(days=3)))
画板.添加一行(datetime.now().date() + timedelta(days=9), '->', 语义日期模板(datetime.now() + timedelta(days=9)))
画板.添加一行(datetime.now().date() + timedelta(days=18), '->', 语义日期模板(datetime.now() + timedelta(days=18)))
画板.添加一行(datetime.now().date() + timedelta(days=40), '->', 语义日期模板(datetime.now() + timedelta(days=40)))
画板.添加一行(datetime.now().date() + timedelta(days=180), '->', 语义日期模板(datetime.now() + timedelta(days=180)))
画板.添加一行(datetime.now().date() + timedelta(days=365), '->', 语义日期模板(datetime.now() + timedelta(days=365)))
画板.添加一行(datetime.now().date() + timedelta(days=365 * 4), '->', 语义日期模板(datetime.now() + timedelta(days=365 * 4)))

画板.分隔线.提示内容('语义日期演示').总长度(画板.表格宽度()).修饰(红字).展示()

画板.修饰列(1, 绿字).展示表格()

```
上述代码构造了18个日期,分别显示了其对应的语义日期,效果如下:  
![输入图片说明](demo%20%E8%AF%AD%E4%B9%89%E6%97%A5%E6%9C%9F.jpg)  

***


#### 参与贡献

1. Fork 本仓库
2. 新建 Feat_xxx 分支
3. 提交代码
4. 新建 Pull Request

#### 特技

1. 使用 Readme\_XXX.md 来支持不同的语言，例如 Readme\_en.md, Readme\_zh.md
2. Gitee 官方博客 [blog.gitee.com](https://blog.gitee.com)
3. 你可以 [https://gitee.com/explore](https://gitee.com/explore) 这个地址来了解 Gitee 上的优秀开源项目
4. [GVP](https://gitee.com/gvp) 全称是 Gitee 最有价值开源项目，是综合评定出的优秀开源项目
5. Gitee 官方提供的使用手册 [https://gitee.com/help](https://gitee.com/help)
6. Gitee 封面人物是一档用来展示 Gitee 会员风采的栏目 [https://gitee.com/gitee-stars/](https://gitee.com/gitee-stars/)
