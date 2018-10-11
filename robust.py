import numpy as np
import cv2
import os

#扩频的鲁棒性LSB水印
#扩频次数
enlarge_size = 5

#鲁棒系数
alpha = 1

# 转8位二进制
def bin_value(value, bitsize):
    binval = bin(value)[2:]
    if len(binval) > bitsize:
        print("Larger than expexted size")
    while len(binval) < bitsize:
        binval = "0" + binval
    return binval


# 将整串水印转化为二维码形式
def watermark_to_encode(watermark):
    binval = bin(0)[2:0]
    data_length = len(watermark)  # 获取字符串长度
    bindata = bin_value(data_length, 8)  # 将十进制的水印长度转化为8位二进制
    for c in bindata:
        for i in range(0, enlarge_size):
            binval = binval + c
    for char in watermark:
        # ord函数将当前字符转化为整数
        # bin_value将字符对应的整数转化为二进制字符串
        # 然后用for循环逐一去除二进制字符串的单个字符为C
        for c in bin_value(ord(char), 8):
            for i in range(0, enlarge_size):
                binval = binval + c
    return binval


# 得到水印中1多还0多
def get_moer_number_markwater(watermark):
    one_count = 0
    zero_count = 0
    data_length = len(watermark)  # 获取字符串长度
    bindata = bin_value(data_length, 8)  # 将十进制的水印长度转化为8位二进制
    for i in range(0, data_length):
        if i == 0:
            zero_count += 1
        else:
            one_count += 1
    for char in watermark:
        # ord函数将当前字符转化为整数
        # bin_value将字符对应的整数转化为二进制字符串
        # 然后用for循环逐一去除二进制字符串的单个字符为C
        for c in bin_value(ord(char), 8):
            if int(c) == 0:
                zero_count += 1
            else:
                one_count += 1

    if zero_count > one_count:
        return 0
    else:
        return 1


# 求数组中次数大小出现频率的情况
def get_max_lineandcow(array):
    index = 0
    max_value = 0
    max_x = 0
    max_y = 0
    for y in range(0, len(array)):
        for x in range(index, len(array)):
            if (array[y][x] > max_value):
                max_x = x
                max_y = y
                max_value = array[y][x]
        index += 1
    return max_y, max_x


def embed_watermark(image_a_pipe,watermark,alpha):
    # rgb_image = cv2.imread(origfile, cv2.IMREAD_COLOR)
    #
    # ycbcr_image = cv2.cvtColor(rgb_image, cv2.COLOR_BGR2YCR_CB)
    #
    # y = ycbcr_image[:, :, 0]
    yf = np.float32(image_a_pipe)
    dct_image = cv2.dct(yf)
    iheight, iwidth = image_a_pipe.shape
    img2 = np.empty(shape=(iheight, iwidth))

    block = []

    index = 0

    # 计算两个位置，哪个位置大的次数多

    more_top = 0
    more_left = 0

    # y用于记录哪个位置比较合适做嵌入
    list_best_temp = [[0 for y in range(8)] for x in range(8)]
    list_best = np.array(list_best_temp)

    # 计算得出哪个位置最适合做嵌入
    for y in range(0, int(iheight / 8) * 8, 8):
        for x in range(0, int(iwidth / 8) * 8, 8):
            block.append(dct_image[y:y + 8, x:x + 8])
            # block[index] = cv2.dct(block[index])
            for y1 in range(0, 8):
                for x1 in range(0, 8):
                    if (block[index][x1][y1] != block[index][y1][x1] and block[index][x1][y1] > 10 and block[index][y1][
                        x1] > 10):
                        list_best[y1][x1] += 1
            index += 1
    # 获得最适合加密的两个位置
    max_y, max_x = get_max_lineandcow(list_best)
    # 获得最适合的加密方式，避免不必要的数值调换
    for i in range(0, len(block)):
        if block[i][max_y][max_x] > block[i][max_x][max_y]:
            more_top += 1
        else:
            more_left += 1

    # 较大的那个位置，
    bigger_x = 0
    bigger_y = 0

    if more_top > more_left:
        bigger_x = max_x
        bigger_y = max_y
    else:
        bigger_y = max_x
        bigger_x = max_y

    # 水印中较多的那个字母（0与1）
    more_number = get_moer_number_markwater(watermark)

    index = 0
    # 将水印和它的长度全部转为二进制
    bindata = watermark_to_encode(watermark)
    bigger_x = 4
    bigger_y = 3
    more_number = 1
    # 先将水印长度存进去,每个二进制扩写为10位

    for c in bindata:
        temp = block[index]
        if int(c) == more_number:
            if block[index][bigger_y][bigger_x] < block[index][bigger_x][bigger_y]:
                block[index][bigger_y][bigger_x], block[index][bigger_x][bigger_y] = block[index][bigger_x][
                                                                                         bigger_y], \
                                                                                     block[index][bigger_y][
                                                                                         bigger_x]
            if block[index][bigger_y][bigger_x] - block[index][bigger_x][bigger_y] < alpha:
                block[index][bigger_y][bigger_x] = (block[index][bigger_y][bigger_x]+block[index][bigger_x][bigger_y])/2+alpha
                block[index][bigger_x][bigger_y] = (block[index][bigger_y][bigger_x]+block[index][bigger_x][bigger_y])/2-alpha
        else:
            if block[index][bigger_y][bigger_x] > block[index][bigger_x][bigger_y]:
                block[index][bigger_y][bigger_x], block[index][bigger_x][bigger_y] = block[index][bigger_x][
                                                                                         bigger_y], \
                                                                                     block[index][bigger_y][
                                                                                         bigger_x]
            if block[index][bigger_x][bigger_y] - block[index][bigger_y][bigger_x] < alpha:
                block[index][bigger_x][bigger_y] = (block[index][bigger_y][bigger_x]+block[index][bigger_x][bigger_y])/2+alpha
                block[index][bigger_y][bigger_x] = (block[index][bigger_y][bigger_x]+block[index][bigger_x][bigger_y])/2-alpha
        temp1 = block[index]
        index += 1

    index = 0
    for y in range(0, int(iheight / 8) * 8, 8):
        for x in range(0, int(iwidth / 8) * 8, 8):
            img2[y:y + 8, x:x + 8] = block[index]
            index += 1

    # block = []
    # for y in range(0, int(iheight / 8) * 8, 8):
    #     for x in range(0, int(iwidth / 8) * 8, 8):
    #         block.append(img2[y:y + 8, x:x + 8])
    # index = 0
    # length = ''
    # for i in range(0, enlarge_size * 8):
    #     if (block[index][bigger_y][bigger_x] > block[index][bigger_x][bigger_y]):
    #         length = length + str(more_number)
    #     else:
    #         length = length + str((int(more_number) + 1) % 2)
    #     index += 1

    watermarked_dct_imagef = np.float32(img2)
    inverse_dct_image = cv2.idct(watermarked_dct_imagef)
    # new_ycbcr_image = ycbcr_image
    # new_ycbcr_image[:, :, 0] = inverse_dct_image
    # watermarked_rgb = cv2.cvtColor(new_ycbcr_image, cv2.COLOR_YCR_CB2BGR)
    # decode_get_watermark(inverse_dct_image, more_number, bigger_y, bigger_x)

    return more_number, bigger_y, bigger_x, inverse_dct_image


def decode_get_watermark(y, more_number, bigger_y, bigger_x):
    # rgb_image = cv2.imread(makefile, cv2.IMREAD_COLOR)
    #
    # ycbcr_image = cv2.cvtColor(rgb_image, cv2.COLOR_BGR2YCR_CB)
    #
    # y = ycbcr_image[:, :, 0]
    yf = np.float32(y)
    dct_image = cv2.dct(yf)
    iheight, iwidth = y.shape

    block = []
    length = bin(0)[2:0]
    index = 0

    list_best_temp = [[0 for y in range(8)] for x in range(8)]
    list_best = np.array(list_best_temp)

    # 计算得出哪个位置最适合做嵌入
    for y in range(0, int(iheight / 8) * 8, 8):
        for x in range(0, int(iwidth / 8) * 8, 8):
            block.append(dct_image[y:y + 8, x:x + 8])
            index += 1
    index = 0
    for i in range(0, enlarge_size*8):
        if (block[index][bigger_y][bigger_x] > block[index][bigger_x][bigger_y]):
            length = length + str(more_number)
        else:
            length = length + str((int(more_number) + 1) % 2)
        index += 1
    # print(transform_code(length))
    watermark = ""
    temp_code = bin(0)[2:0]
    watermark_length = transform_code(length)
    for i in range(0, 5):
        for a in range(0, enlarge_size*8):
            if (block[index][bigger_y][bigger_x] > block[index][bigger_x][bigger_y]):
                temp_code = temp_code + str(more_number)
            else:
                temp_code = temp_code + str((int(more_number) + 1) % 2)
            index += 1
        watermark += chr(transform_code(temp_code))
        temp_code = bin(0)[2:0]
    a = 0
    return watermark
    # print("得出的水印:%s" % watermark)


def transform_code(binval):
    zero_count = 0
    one_count = 0
    rebinval = bin(0)[2:0]
    index = 0
    for c in binval:
        if c == '1':
            one_count += 1
        else:
            zero_count += 1
        index += 1
        if index == enlarge_size:
            if zero_count >= one_count:
                rebinval = rebinval + '0'
            else:
                rebinval = rebinval + '1'
            zero_count = 0
            one_count = 0
            index = 0
    return int(rebinval, 2)


# if __name__ == "__main__":
#     more_number, bigger_y, bigger_x = embed_watermark('lena.jpg', 'lena-a.jpg', 'hello')
#     decode_get_watermark('lena-a.jpg', more_number, bigger_y, bigger_x)
