# -*- coding: utf-8 -*-
# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.10.2
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# +
default_dir = './'
divide_num = 3

import random
import json
from matplotlib import pyplot as plt
import matplotlib.font_manager as fm
import datetime
import os
from PIL import Image
import random
import tweepy
import csv


def question_choice(question_json, question_log):
    with open(question_log, 'r') as f_in:
        reader = csv.reader(f_in)
        
        for row in reader:
            prev_question = row[1]
    
    with open(question_json, 'r') as f_in:
        question_list = json.load(f_in)

    question = question_list[random.choice(list(question_list))]
    
    return question, prev_question

def font_choice(fonts_json, default_dir):
    with open(fonts_json, 'r') as f_in:
        fonts_list = json.load(f_in)
    
    font_name = random.choice(list(fonts_list))
    font_path = os.path.join(default_dir, fonts_list[font_name])
    
    return font_name, font_path

def log_write(question_log, timenow, question, font_name):
    with open(question_log, 'a') as f_in:
        row = f'{timenow},{question},{font_name}\n'
        f_in.write(row)

def fig_make(output_original_path, font_path, question):
    fp = fm.FontProperties(fname=font_path)
    
    fig = plt.figure(figsize=(6,6))
    plt.clf()

    plt.text(0.5, 0.4, question, horizontalalignment='center', verticalalignment='center', fontsize=400, fontproperties=fp)

    plt.axis('off')
    plt.savefig(output_original_path, facecolor="white", pad_inches = 0)
    
def banner_make(output_banner_path, font_path):
    fp = fm.FontProperties(fname=font_path)
    
    fig = plt.figure(figsize=(6,0.6))
    plt.clf()

    plt.text(0,0.3, "3PySci https://3pysci.com", fontsize=20, fontproperties=fp)

    plt.axis('off')
    plt.savefig(output_banner_path, facecolor="white", pad_inches = 0)
    
def divide_image(divide_num, output_original_path, output_dir):

    im = Image.open(output_original_path)

    size = im.size[0]

    divide_size = int(size/divide_num)

    left_upper = []
    for i in range(divide_num):
        for j in range(divide_num):
            left_upper.append([i*divide_size,j*divide_size])

    right_bottom = []
    for i in range(1, divide_num+1):
        for j in range(1, divide_num+1):
            right_bottom.append([i*divide_size,j*divide_size])

    crop_list = []
    for lu, rb in zip(left_upper, right_bottom):
        crop_list.append([lu[0], lu[1], rb[0], rb[1]])

    img_num = []
    for i in range(len(crop_list)):
        crop_im = im.crop(crop_list[i])
        output_file_name = os.path.join(output_dir, f'{i}.png')
        crop_im.save(output_file_name)
        img_num.append(i)
    
    return img_num, crop_list, size

def shuffle_image(img_num, output_dir, crop_list, size, output_question_path):
    random.shuffle(img_num)
    
    new_im = Image.new('RGB', (size, size))

    for i, place in zip(img_num, crop_list):
        paste_file_name = os.path.join(output_dir, f'{i}.png')
        paste_img = Image.open(paste_file_name)
        new_im.paste(paste_img, (place[0], place[1]))

    new_im.save(output_question_path)
    
def add_banner(output_question_path, output_banner_path):
    
    question_im = Image.open(output_question_path)
    banner_im = Image.open(output_banner_path)
    
    question_im_width = question_im.size[0]
    question_im_height = question_im.size[1]
    banner_im_height = banner_im.size[1]
    
    new_im = Image.new('RGB', (question_im_width, question_im_height + banner_im_height))
    
    new_im.paste(question_im, (0, 0))
    new_im.paste(banner_im, (0, question_im_height))
    
    new_im.save(output_question_path)
    
def applytotwitter(settings_json, output_question_path, prev_question):
    
    text = f'前回の答えは「{prev_question}」でした。\nこのシャッフルされた漢字はなんでしょう？😆\n#分かったらRT\n#脳トレ\n#クイズ\n#パズル\n#アハ体験\n#Python\n#プログラミング'
    
    with open(settings_json, 'r') as f_in:
        settings = json.load(f_in)

    auth = tweepy.OAuthHandler(settings['consumer_key'], settings['consumer_secret'])
    auth.set_access_token(settings['access_token'], settings['access_token_secret'])

    api = tweepy.API(auth, wait_on_rate_limit = True)

    api.update_with_media(status = text, filename = output_question_path)


# -

def main():
    question_json = os.path.join(default_dir, 'question.json')
    fonts_json = os.path.join(default_dir, 'fonts.json')
    settings_json = os.path.join(default_dir, 'settings.json')
    question_log = os.path.join(default_dir, 'question_log.txt')
    
    timenow = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    
    question_dir = os.path.join(default_dir, 'question')
    
    output_dir = os.path.join(question_dir, timenow)
    os.mkdir(output_dir)
    
    output_original_name = timenow + '.png'
    output_original_path = os.path.join(output_dir, output_original_name)
    
    output_banner_name = 'banner_' + timenow + '.png'
    output_banner_path = os.path.join(output_dir, output_banner_name)
    
    output_question_name = 'question_' + timenow + '.png'
    output_question_path = os.path.join(output_dir, output_question_name)
    
    question, prev_question = question_choice(question_json, question_log)
    font_name, font_path = font_choice(fonts_json, default_dir)
    log_write(question_log, timenow, question, font_name)
    fig_make(output_original_path, font_path, question)
    banner_make(output_banner_path, font_path)
    img_num, crop_list, size = divide_image(divide_num, output_original_path, output_dir)
    shuffle_image(img_num, output_dir, crop_list, size, output_question_path)
    add_banner(output_question_path, output_banner_path)
    applytotwitter(settings_json, output_question_path, prev_question)


if __name__ == '__main__':
    main()








