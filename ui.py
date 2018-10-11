#!/usr/bin/python
# -*- coding: UTF-8 -*-

from tkinter import *  # 导入 Tkinter 库
import image  # 处理图片
import music  # 处理音频
import video  # 处理视频


def start():
    # 处理图片
    if first_first_bool.get() == True and first_second_bool.get() == False and first_third_bool.get() == False:
        if second_first_bool.get() == True and second_second_bool.get() == False:
            # 图片水印加密
            image_file = file_text.get()  # 获得文件地址
            message = water_text.get()  # 获得水印
            output = "ok.jpg"  # 输出文件
            alpha = 5  # 加密系数
            image.SpreadSpectrumEmbed(image_file, output, message, alpha)
        elif second_first_bool.get() == False and second_second_bool.get() == True:
            makefile = file_text.get()
            bigger_x = 2
            bigger_y = 4
            more_number = 1
            string = image.decode_get_watermark(makefile, more_number, bigger_y, bigger_x)
            encode_text.set(string)
        else:
            print("不能同时加、解密")
    # 处理音频
    elif first_first_bool.get() == False and first_second_bool.get() == True and first_third_bool.get() == False:
        if second_first_bool.get() == True and second_second_bool.get() == False:
            message = water_text.get()  # 获得水印
            cover_audio = file_text.get()  # 获得文件地址
            output = "ok.wav"  # 输出文件
            music.lsb_watermark(cover_audio, message, output)
        elif second_first_bool.get() == False and second_second_bool.get() == True:
            message = file_text.get()
            string = music.recover_lsb_watermark(message)
            encode_text.set(string)
        else:
            print("不能同时加、解密")
    # 处理视频
    elif first_first_bool.get() == False and first_second_bool.get() == False and first_third_bool.get() == True:
        if second_first_bool.get() == True and second_second_bool.get() == False:
            input_video = file_text.get()  # 获得文件地址
            watermark_string = water_text.get()  # 获得水印
            output_video = 'ok.mp4'  # 输出文件
            video.embed_video(input_video, watermark_string, output_video)
        elif second_first_bool.get() == False and second_second_bool.get() == True:
            makefile = file_text.get()
            more_number = 1
            bigger_x = 4
            bigger_y = 3
            string = video.decode(makefile, more_number, bigger_y, bigger_x)
            encode_text.set(string)
        else:
            print("不能同时加、解密")
    else:
        print("参数设置错误")


if __name__ == '__main__':
    root = Tk()  # 创建窗口对象的背景色
    root.title("python水印整合")  # 窗口标题
    root.geometry("500x500")  # 窗口大小
    # 第一块选择区
    text1 = Label(root, text="Please check")  # 标题
    text1.pack()

    first_first_bool = BooleanVar()
    first_first = Checkbutton(root, text="图片", variable=first_first_bool)
    first_first.pack()

    first_second_bool = BooleanVar()
    first_second = Checkbutton(root, text="音频", variable=first_second_bool)
    first_second.pack()

    first_third_bool = BooleanVar()
    first_third = Checkbutton(root, text="视频", variable=first_third_bool)
    first_third.pack()

    # 第二块选择区
    text2 = Label(root, text="Please check")  # 标题
    text2.pack()

    second_first_bool = BooleanVar()
    second_first = Checkbutton(root, text="嵌入", variable=second_first_bool)
    second_first.pack()

    second_second_bool = BooleanVar()
    second_second = Checkbutton(root, text="提取", variable=second_second_bool)
    second_second.pack()

    # 输入文件名字
    l1 = Label(root, text="输入文件")
    l1.pack()  # 这里的side可以赋值为LEFT  RTGHT TOP  BOTTOM
    file_text = StringVar()
    file = Entry(root, textvariable=file_text)
    file.pack()
    # 输入水印
    l2 = Label(root, text="输入水印")
    l2.pack()  # 这里的side可以赋值为LEFT  RTGHT TOP  BOTTOM
    water_text = StringVar()
    water = Entry(root, textvariable=water_text)
    water.pack()
    # 解密得到的水印
    l3 = Label(root, text="得到的水印")
    l3.pack()
    encode_text = StringVar()
    encode = Entry(root, textvariable=encode_text)
    encode.pack()
    # 确认按钮
    l3 = Label(root, text="是否确认")
    l3.pack()  # 这里的side可以赋值为LEFT  RTGHT TOP  BOTTOM
    right = Button(root, text="确认", width=19, relief=GROOVE, bg="blue", command=start)  # 按下时触发事件
    right.pack()

    # 循环
    root.mainloop()
