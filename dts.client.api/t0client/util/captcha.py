#!/usr/bin/python
# -*- coding:utf-8 -*-

import os
import math
import random, string
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from ..config.config import *
# from config.config import *

# abcdefghjkmnpqrstuvwxy
_letter_cases = "abdefghmnpqrstvwxyz"  # 小写字母，去除可能干扰的c i j k l o u v
_upper_cases = "ABDEFHMNPQRSTWXYZ"  # 大写字母，去除可能干扰的C G I J K L O U V
_numbers = ''.join(map(str, range(2, 10)))  # 数字，去除0，1
init_chars = ''.join((_letter_cases, _upper_cases, _numbers))
fontType = CAPTCHA_FONT
bg_image = "/www/bg.png"
out_dir = "/Users/admin/Downloads/captcha"


def create_validate_code(size=(170, 84),
                         chars=init_chars,
                         img_type="jpg",
                         mode="RGB",
                         bg_image=bg_image,
                         fg_color=(255, 255, 255),
                         font_size=50,
                         font_type=fontType,
                         char_length=4,
                         draw_lines=True,
                         n_line=(10, 16),
                         min_length=1,
                         max_length=12,
                         draw_points=False,
                         point_chance=2):
    '''
    生成验证码图片
    @param size: 图片的大小，格式（宽，高），默认为(120, 30)
    @param chars: 允许的字符集合，格式字符串
    @param img_type: 图片保存的格式，默认为GIF，可选的为GIF，JPEG，TIFF，PNG
    @param mode: 图片模式，默认为RGB
    @param bg_color: 背景颜色，默认为白色
    @param fg_color: 前景色，验证码字符颜色，默认为白色#FFFFFF
    @param font_size: 验证码字体大小
    @param font_type: 验证码字体，默认为 ae_AlArabiya.ttf
    @param length: 验证码字符个数
    @param draw_lines: 是否划干扰线
    @param n_lines: 干扰线的条数范围，格式元组，默认为(1, 2)，只有draw_lines为True时有效
    @param min_length: 干扰线的最小长度
    @param max_length: 干扰线的最大长度
    @param draw_points: 是否画干扰点
    @param point_chance: 干扰点出现的概率，大小范围[0, 100]
    @return: [0]: PIL Image实例
    @return: [1]: 验证码图片中的字符串
    '''
    bg_num = random.randint(1, 5)
    bg_image = CAPTCHA_BGPATH + "bg%s.png" % (str(bg_num))
    if bg_num in (2, 4):
        fg_color = (245, 93, 93)
        line_color = (255, 255, 255)
    else:
        fg_color = (255, 255, 255)
        line_color = (245, 93, 93)

    width, height = size  # 宽， 高
    img = Image.open(bg_image)  # 创建图形
    draw = ImageDraw.Draw(img)  # 创建画笔
    if draw_lines:
        create_lines(draw, min_length, max_length, n_line, width, height, line_color)
    if draw_points:
        create_points(draw, point_chance, width, height)
    strs = create_strs(draw, chars, char_length, font_type, font_size, width, height, fg_color)
    # # 图形扭曲参数
    # params = [1 - float(random.randint(1, 2)) / 100,
    #           0,
    #           0,
    #           0,
    #           1 - float(random.randint(1, 10)) / 100,
    #           float(random.randint(1, 2)) / 500,
    #           0.001,
    #           float(random.randint(1, 2)) / 500
    #           ]
    # img = img.transform(size, Image.PERSPECTIVE, params) # 创建扭曲
    img = img.filter(ImageFilter.DETAIL)  # 滤镜，边界加强（阈值更大）
    return img, strs


def create_lines(draw, min_length, max_length, n_line, width, height, line_color):
    '''绘制干扰线'''
    line_num = random.randint(n_line[0], n_line[1])  # 干扰线条数
    for i in range(line_num):
        # 起始点
        begin = (random.randint(0, width), random.randint(0, height))
        # 长度
        length = min_length + random.random() * (max_length - min_length)
        # 角度
        alpha = random.randrange(0, 360)
        # 结束点
        end = (begin[0] + length * math.cos(math.radians(alpha)),
               begin[1] - length * math.sin(math.radians(alpha)))
        draw.line([begin, end], fill=line_color)


def create_points(draw, point_chance, width, height):
    '''绘制干扰点'''
    chance = min(100, max(0, int(point_chance)))  # 大小限制在[0, 100]

    for w in xrange(width):
        for h in xrange(height):
            tmp = random.randint(0, 100)
            if tmp > 100 - chance:
                draw.point((w, h), fill=(0, 0, 0))


def create_strs(draw, chars, char_length, font_type, font_size, width, height, fg_color):
    '''绘制验证码字符'''
    '''生成给定长度的字符串，返回列表格式'''
    # c_chars = random.sample(chars, length) # sample产生的是unique的char
    flag = False
    while not flag:
        # c_chars = np.random.choice(list(chars), char_length).tolist()
        # strs = ''.join(c_chars) # 每个字符前后以空格隔开
        strs = getCode(char_length)

        font = ImageFont.truetype(font_type, font_size)
        font_width, font_height = font.getsize(strs)

        try:
            start_x = (width - font_width) / 2
            start_y = (height - font_height) / 2
        except ValueError as e:
            print
            e
            print
            strs
            print
            width, font_width, height, font_height
        else:
            flag = True

    draw.text((start_x, start_y), strs, font=font, fill=fg_color)
    return strs


def getCode(length):
    # 随机出数字的个数
    # numOfNum = random.randint(1,length-1)
    # numOfLetter = length - numOfNum
    # 选中numOfNum个数字
    slcNum = [random.choice(string.digits) for i in range(length)]
    # 选中numOfLetter个字母
    # slcLetter = [random.choice(string.ascii_letters) for i in range(numOfLetter)]
    # 打乱这个组合
    # slcChar = slcNum + slcLetter
    random.shuffle(slcNum)
    # 生成编码
    code = ''.join([i for i in slcNum])
    return code


if __name__ == "__main__":
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)
    for _ in range(2):
        code_img, code_str = create_validate_code()
        code_img.save("%s/%s.jpg" % (out_dir, code_str))