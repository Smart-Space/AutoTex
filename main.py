import os
os.environ['NO_ALBUMENTATIONS_UPDATE']="1"
os.chdir(os.path.dirname(__file__))
from tkinter import Tk
from concurrent.futures import ThreadPoolExecutor
from PIL import Image, ImageGrab, ImageTk
from latex2mathml.converter import convert
from tkwebview import TkWebview as Webview
from pystray import Icon, MenuItem
from tinui import *

import data
from process import load_model, process_img


def model_loaded(e):
    change_info(f'准备就绪({data.device})')
    root.bind("<Control-v>", cli_get)
    root.bind("<<ImageInverted>>", img_inverted)
    root.bind("<<ImageNotInverted>>", img_not_inverted)
    root.bind("<<ImageProcessed>>", load_latex)

def img_inverted(e):
    onoff.on()

def img_not_inverted(e):
    onoff.off()

def load_latex(e):
    global do_process
    change_info('正在渲染公式')
    data.reverse=0
    root.bind("<Control-v>", cli_get)
    text.config(state='normal')
    text.delete(1.0, 'end')
    text.insert('end', data.latexstring.replace('\\\\', '\\\\\n'))
    text.config(state='disabled')
    text.update()
    result=data.latexstring.replace('\\', '\\\\').replace("'", "\\'").replace('"', '\\"')
    web.eval(f'render("$${result}$$")')
    change_info('已完成识别')
    do_process=True

def cli_get(e=None):
    # 剪切板获取数据
    global do_process
    do_process=False
    im=ImageGrab.grabclipboard()
    if not isinstance(im, Image.Image):
        return
    change_info('正在处理图片')
    data.orimg=im.copy()
    width=canvas.winfo_width()
    height=canvas.winfo_height()
    w, h = im.size
    if w>width or h>height:
        k=min(width/w, height/h)
        im=im.resize((int(w*k),int(h*k)), Image.Resampling.LANCZOS)
    img=ImageTk.PhotoImage(im)
    canvas.delete('all')
    canvas.image=img
    canvas.create_image(width/2, height/2, anchor='center', image=img)
    canvas.update()
    threadpool.submit(process_img)
    root.unbind("<Control-v>")

def copy(e):
    root.clipboard_clear()
    text=data.latexstring.replace('\\\\', '\\\\\n')
    if latex_add_code==0:
        root.clipboard_append(text)
    elif latex_add_code==1:
        root.clipboard_append(f"$${text}$$")
    elif latex_add_code:
        root.clipboard_append(f"\\begin{{equation}}{text}\\end{{equation}}")

def copy_mathml(e):
    if not data.latexstring:
        return
    root.clipboard_clear()
    root.clipboard_append(convert(data.latexstring))

do_process=False
def set_reverse(flag):
    global do_process
    if flag:
        data.reverse=1
        ui.itemconfig(para, text='反转颜色')
    else:
        data.reverse=2
        ui.itemconfig(para, text='原图')
    if do_process:
        do_process=False
        change_info('正在处理图片')
        threadpool.submit(process_img)
        root.unbind("<Control-v>")

latex_add_dict={
    '公式包裹(默认无)': 0,
    '无包裹': 0,
    '$$...$$': 1,
    '\\begin{equation}...': 2
}
latex_add_code=0
def latex_add(string):
    global latex_add_code
    latex_add_code=latex_add_dict[string]


def change_info(text):
    ui.itemconfig(info, text=text)

def updateExpand(e):
    rp.update_layout(0, 0, e.width, e.height)

def showabout():
    # 托盘在子线程中，为了防止出错，这里同样使用事件触发机制
    root.event_generate("<<ShowAbout>>")
def __showabout(e):
    show_info(root, 'AutoTex', '一个简单易用的本地公式识别工具。')

def quitApp():
    threadpool.shutdown(wait=False, cancel_futures=True)
    icon.visible=False
    icon.stop()
    root.destroy()
    root.quit()

root=Tk()
# 居中显示
screenwidth = root.winfo_screenwidth()
screenheight = root.winfo_screenheight()
width = 1000
height = 700
x = (screenwidth - width) / 2
y = (screenheight - height) / 2 -50
root.geometry('%dx%d+%d+%d' % (width, height, x, y))
root.title("AutoTex")
root.iconbitmap('./asset/icon.ico')
data.root=root

root.bind("<<ModelLoaded>>", model_loaded)
root.protocol("WM_DELETE_WINDOW", lambda: root.withdraw())
root.update()

threadpool=ThreadPoolExecutor(max_workers=1)

threadpool.submit(load_model)

ui=BasicTinUI(root, bg='#f3f3f3')
ui.pack(fill='both', expand=True)
rp=ExpandPanel(ui, padding=(5, 5, 5, 5))
ui.bind("<Configure>", updateExpand)
hp=HorizonPanel(ui, spacing=5)
rp.set_child(hp)

vp=VerticalPanel(ui)
hp.add_child(vp,400)

top=HorizonPanel(ui, spacing=5, padding=(0, 5, 0, 5))
vp.add_child(top,50)
btn=ui.add_button2((0,0), text='复制', command=copy, anchor='w')[-1]
top.add_child(btn,50)
btn=ui.add_button2((0,0), text='复制MathML(Word)', command=copy_mathml, anchor='w')[-1]
top.add_child(btn,200)
info=ui.add_paragraph((0,0), text='模型加载中...', anchor='w')
top.add_child(info,200)

ep=ExpandPanel(ui)
vp.add_child(ep,weight=1)
textitem=ui.add_textbox((0,0), scrollbar=True)
text=textitem[0]
text.config(state='disabled')
text.focus_set()
textid=textitem[-1]
del textitem
ep.set_child(textid)

bop=HorizonPanel(ui, spacing=5, padding=(0, 5, 0, 5))
vp.add_child(bop,40)
onoff,onoffid=ui.add_onoff((0,0), bd=30, command=set_reverse, anchor='w')[-2:]
bop.add_child(onoffid,40)
para=ui.add_paragraph((0,0), text='原图', anchor='w')
bop.add_child(para,160)
combobutton=ui.add_combobox((0,0), width=150, height=115, text='公式包裹(默认无)', content=('无包裹','$$...$$','\\begin{equation}...'), command=latex_add, anchor='w')[-1]
bop.add_child(combobutton,120)

canvasitem=ui.add_ui((0,0), bg='#fafbfd')# 用于存放图片
canvas=canvasitem[0]
canvasid=canvasitem[-1]
del canvasitem

dispitem=ui.add_ui((0,0))# 用于显示效果
disp=dispitem[0]
dispid=dispitem[-1]
del dispitem

vp2=VerticalPanel(ui,spacing=5)
hp.add_child(vp2,weight=1)
ep2=ExpandPanel(ui)
vp2.add_child(ep2,weight=1)
ep3=ExpandPanel(ui)
vp2.add_child(ep3,weight=1)

ep2.set_child(canvasid)
ep3.set_child(dispid)

menu=(MenuItem('显示', lambda: root.deiconify(), default=True), MenuItem('关于', showabout), MenuItem('退出', quitApp))
iconimage=Image.open('./asset/icon.ico')
icon=Icon('AutoTex', iconimage, 'AutoTex', menu)
icon.run_detached()

root.bind('<Button-1>',lambda e: text.focus_force())
root.bind("<<ShowAbout>>", __showabout)

web=Webview(disp)
web.pack(fill='both', expand=True)
web.navigate(f"file:///{os.path.dirname(__file__)}/libs/index.html")
web.bindjs('get_ctrl_v', cli_get, True)

root.mainloop()
