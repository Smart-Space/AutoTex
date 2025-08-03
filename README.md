![](https://github.com/Smart-Space/AutoTex/blob/main/asset/LOGO.png?raw=true)

# AutoTex

基于[UniMERNet](https://github.com/opendatalab/UniMERNet)的公式识别应用。

灵感来自[zstar1003/FreeTex](https://github.com/zstar1003/FreeTex)。

>[!WARNING]
>
>由于本项目使用tkinter，支持mathml困难，使用的webviewpy虽然跨平台，但是webview控件随着窗口变换而改变尺寸的操作仅在Windows下通过User32实现，其他平台不支持也无法测试。

此前，就图片底色影响识别、图片上传流程便捷性的问题，我单独fork了一个分支[Smart-Space/FreeTex](https://github.com/Smart-Space/FreeTex)并进行了一定的改写。不过原软件使用GPL协议，且当前在功能上已经足够完善，现单独使用MIT协议重新开发了一个简单的公式识别应用（注意UniMERNet本身协议限制），这么做是为了更适合我自己的使用习惯<del>（其实是为了展示TinUI的面板布局能力😋）</del>。

**普通用户，请使用FreeTex作者提供的发行版软件。**

## 特点

<img width="2004" height="1464" alt="image" src="https://github.com/user-attachments/assets/a727df7c-8969-4d65-8e79-cc53e54bef12" />


### 可支持独立gpu

如果使用了支持gpu的pytorch，就可以使用gpu。

### 图片展示与公式预览区域

AutoTex的图片展示与公式预览区域在右侧水平等分排列，latex文本框和工具栏在左侧，我个人认为这样的布局比FreeTex好看一点，我自己在使用FreeTex的时候感觉公式预览区域有点挤，文本框倒无所谓，并不是重点。

FreeTex的图片展示区域虽然也是能对图片等比缩放，但是总感觉无法高效利用这个空间，可能是和控件过大的尺寸或长宽比有关，AutoTex是能填充就填充，当长宽均小于展示区时显示原图。此外，FreeTex预览区域对大段公式不是很友好。AutoTex没有对web视图的硬性范围控制，可以随意滑动。

### 图片底色识别

UniMERNet在浅色背景图片上训练，因此当输入为暗色背景图片时，识别成功率大打折扣。

AutoTex的底色识别和FreeTex没有关系，使用的是我的分支（[Smart-Space/FreeTex](https://github.com/Smart-Space/FreeTex)）中的处理方法，即判断**灰度颜色均值**区分暗色和亮色，并检查暗色像素和亮色像素的多少，少的色域为文本，以此自动判断是否需要反转图片颜色。同时和我的FreeTex分支一样，仍然保留用户对于是否反转图片颜色的手动控制选项，不过一般情况下，“色域像素少的代表文本”是没有错的。

### 仅支持通过粘贴上传图片

AutoTex不提供图片文件上传和截图功能。选择图片文件上传动作太慢，拖动和复制粘贴在效率上没有本质区别，而且我自己是几乎不可能把公式图片单存为一个文件的，即便是手写稿，也是存一大段，干脆打开截图。然而，截图功能，就交给系统或者专业软件吧。

### 静默运行

只有在托盘图标菜单中点击“退出”才会真正退出AutoTex。

### 简单易懂的源码

UI框架使用tkinter(TinUI)，使用面板布局，结构非常清晰。

模型加载和识别使用线程，不影响软件使用（虽然这期间没什么可用的）。

使用事件和中间数据文件(`data.py`)管理流程，看起来比pyQt简单。

## 运行

克隆本仓库后，新建`models`文件夹：

```bash
cd models
git clone https://huggingface.co/wanderkid/unimernet_base
```

> 可以自行选择其他unimernet模型。

安装unimernet的依赖：

```bash
pip install -U "unimernet[full]"
# 默认下载cpu版本pytorch，可自行安装支持gpu的pytorch
```

安装AutoTex的依赖：

```bash
pip install tinui, pystray, webviewpy, latex2mathml
```

理论上，就可以运行了（对了，本项目在python3.10环境中运行）：

```bash
python main.py
```

## 题外话

好吧，我承认，是为了展示TinUI的面板布局，顺带制作一个匹配我习惯的公式识别软件。
