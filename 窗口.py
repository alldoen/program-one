from tkinter import *
import tkinter.messagebox
import pyttsx3


def show1():
    print("文本:%s" % e1.get())
    # e1.delete(0, "end")

    engine = pyttsx3.init()
    note = e1.get()
    # print(note)

    # 获取当前语音速率
    rate = engine.getProperty('rate')
    print(f'语音速率：{rate}')
    # 设置新的语音速率
    engine.setProperty('rate', 150)

    # 获取当前语音音量
    volume = engine.getProperty('volume')
    print(f'语音音量：{volume}')
    # 设置新的语音音量，音量最小为 0，最大为 1
    engine.setProperty('volume', 1.0)

    # 获取当前语音声音的详细信息
    voices = engine.getProperty('voices')
    print(f'语音声音详细信息：{voices}')
    # 设置当前语音声音为女性，当前声音不能读中文
    engine.setProperty('voice', voices[1].id)
    # 设置当前语音声音为男性，当前声音可以读中文
    engine.setProperty('voice', voices[0].id)
    # 获取当前语音声音
    voice = engine.getProperty('voice')
    print(f'语音声音：{voice}')

    # 语音文本
    words = note

    if words == '':
        tkinter.messagebox.showinfo('提示', '输入为空！')
    # 将语音文本说出来
    #a = engine.say(words)
    #engine.runAndWait()
    #engine.stop()
    # 保存音频
    else:
        engine.save_to_file(words, filename='go_out.wav', name='test')
        engine.runAndWait()
        e1.delete(0, "end")
        tkinter.messagebox.showinfo('提示', '转译成功！')


def sayit():
    engine = pyttsx3.init()
    note = e1.get()
    if note == '':
        tkinter.messagebox.showinfo('提示', '输入为空！')
        return
    # 获取当前语音速率
    rate = engine.getProperty('rate')
    print(f'语音速率：{rate}')
    # 设置新的语音速率
    engine.setProperty('rate', 150)

    # 获取当前语音音量
    volume = engine.getProperty('volume')
    print(f'语音音量：{volume}')
    # 设置新的语音音量，音量最小为 0，最大为 1
    engine.setProperty('volume', 1.0)

    # 获取当前语音声音的详细信息
    voices = engine.getProperty('voices')
    print(f'语音声音详细信息：{voices}')
    # 设置当前语音声音为女性，当前声音不能读中文
    engine.setProperty('voice', voices[1].id)
    # 设置当前语音声音为男性，当前声音可以读中文
    engine.setProperty('voice', voices[0].id)
    # 获取当前语音声音
    voice = engine.getProperty('voice')
    print(f'语音声音：{voice}')

    a = engine.say(note)
    engine.runAndWait()
    engine.stop()

if __name__ == '__main__':
    root = Tk()
    root.title('python文字转语音')
    root.geometry("+800+400")
    Label(root, text="文本").grid(row=0, column=0)
    e1 = Entry(root)
    e1.grid(row=0, column=1, padx=15, pady=10)
    Button(root, text="获取信息", width=10, command=show1) \
        .grid(row=3, column=0, sticky=W, padx=10, pady=5)
    Button(root, text="朗读信息", width=10, command=sayit) \
        .grid(row=3, column=1, sticky=W, padx=10, pady=5)
    Button(root, text="退出", width=10, command=root.quit) \
        .grid(row=3, column=2, sticky=E, padx=10, pady=5)


    root.mainloop()