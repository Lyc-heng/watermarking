# 指定ffmpeg文件位置
FFMPEG_BIN = "ffmpeg"
# 视频水印加密算法
import subprocess as sp
import numpy
# 使用该库去获得加密的谁赢，不知道是否是mp4压缩太厉害或视频本身的问题，只要把alpha设为100时能解析出部分加密的水印，
# 但还是有部分错误的解析信息，因此在这里调用该库去获得真正的水印
from collections import Counter
# 自己编写的鲁棒性图像水印算法
import robust

# 视频的长宽高
width = 640
height = 360


# 嵌入水印算法
def embed_video(input_video, watermark_string, output_video):
    # ffmpeg -i input_video -f image2pipe -pix_fmt yuv420p -c:v rawvideo -
    command_read = [FFMPEG_BIN,
                    '-i', input_video,
                    '-f', 'image2pipe',
                    '-pix_fmt', 'yuv420p',
                    '-c:v', 'rawvideo', '-']
    # 运行以上命令并重定向命令输出到管道
    pipe_read = sp.Popen(command_read, stdout=sp.PIPE, bufsize=10 ** 9)

    # ffmpge -y -f rawvideo -c:v rawvideo -s 1920x1080 -pix_fmt yuv420p -i - -q:v 2 output_video
    command_write = [FFMPEG_BIN,
                     '-y',  # (optional) overwrite output file if it exists
                     '-f', 'rawvideo',
                     '-c:v', 'rawvideo',
                     '-s', '640x360',
                     '-pix_fmt', 'yuv420p',
                     '-i', '-',  # The input comes from a pipe
                     '-q:v', '2',
                     '-r', '25',
                     output_video]
    # 运行以上命令并重定向输入到管道
    pipe_write = sp.Popen(command_write, stdin=sp.PIPE)

    raw_image = pipe_read.stdout.read(width * height * 3)

    while raw_image != None and len(raw_image) != 0:
        # 将读取到的二进制数据转化为numpy中的array
        image = numpy.fromstring(raw_image, dtype='uint8')
        image = image.reshape((height, width, 3))
        # 清空已读取的数据
        pipe_read.stdout.flush()

        # 嵌入水印
        img_tmp = image[:height, :width, 0]
        # 嵌入水印算法，因为视频压缩太厉害，只有在alpha极大的可能下，才能获得加密的水印
        more_number, bigger_y, bigger_x, inverse_dct_image = robust.embed_watermark(img_tmp, watermark_string, 100)

        img_tmp = inverse_dct_image

        image[:height, :width, 0] = img_tmp

        # 将嵌入后的图像写入到合成视频的ffmpeg管道中
        pipe_write.stdin.write(image.tostring())

        # 读取下一帧
        raw_image = pipe_read.stdout.read(width * height * 3)

    return more_number, bigger_y, bigger_x


def decode(input_video, more_number, bigger_y, bigger_x):
    # ffmpeg -i input_video -f image2pipe -pix_fmt yuv420p -c:v rawvideo -
    end_String = []
    command_read = [FFMPEG_BIN,
                    '-i', input_video,
                    '-f', 'image2pipe',
                    '-pix_fmt', 'yuv420p',
                    '-c:v', 'rawvideo', '-']
    # 运行以上命令并重定向命令输出到管道
    pipe_read = sp.Popen(command_read, stdout=sp.PIPE, bufsize=10 ** 9)

    raw_image = pipe_read.stdout.read(width * height * 3)

    while raw_image != None and len(raw_image) != 0:
        # 将读取到的二进制数据转化为numpy中的array
        image = numpy.fromstring(raw_image, dtype='uint8')
        image = image.reshape((height, width, 3))
        # 清空已读取的数据
        pipe_read.stdout.flush()

        img_tmp = image[:height, :width, 0]
        # 提取水印
        string = robust.decode_get_watermark(img_tmp, more_number, bigger_y, bigger_x)
        end_String.append(string)
        # 读取下一帧
        raw_image = pipe_read.stdout.read(width * height * 3)
    # 返回出现频率最高的那串字符，有极高可能性就是为加密的水印
    return Counter(end_String).most_common(1)[0][0]


if __name__ == '__main__':
    # 嵌入水印
    more_number, bigger_y, bigger_x = embed_video('start.mp4', 'hello', 'new.mp4')
    # 提取水印，因为不知道加密时最佳的情况是怎样的，所以修改了图片的加密算法，直接确定了加密的位置和出现频率较高的水印字母
    # 在这里就是设为最佳的加密位置是（4，3）和（3，4），上面较大时规定为1.
    # 但实际上最佳的位置和大小关系并不是这样
    more_number = 1
    bigger_x = 4
    bigger_y = 3
    decode('new.mp4', more_number, bigger_y, bigger_x)
