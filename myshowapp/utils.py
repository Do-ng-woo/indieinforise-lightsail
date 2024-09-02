#스탬프 이미지 만드는 함수---------------------------------------------------------------
from django.contrib.staticfiles.storage import staticfiles_storage
from PIL import Image, ImageDraw, ImageFont, ImageOps
import io
from django.core.files.base import ContentFile
import numpy as np
import random

def split_text(title):
    if len(title) > 45:
        first_part = title[:int(len(title) * 3 / 8)]
        second_part = title[int(len(title) * 3 / 8):int(len(title) * 6 / 8)]
        third_part = title[int(len(title) * 6 / 8):]
        return first_part, second_part, third_part
    elif len(title) > 25:
        half = len(title) // 2
        return title[:half], title[half:], None
    else:
        return title, None, None

def convert_image(image_path, color, size=(450, 450)):
    image = Image.open(staticfiles_storage.path(image_path)).resize(size).convert("RGBA")
    background = Image.new("RGBA", size, "white")
    white_bg_image = Image.alpha_composite(background, image).convert("RGB")
    grayscale = ImageOps.grayscale(white_bg_image)
    
    if color == "blue":
        return ImageOps.colorize(grayscale, black="blue", white="white")
    elif color == "yellow":
        return ImageOps.colorize(grayscale, black="yellow", white="white")
    elif color == "red":
        return ImageOps.colorize(grayscale, black="red", white="white")
    elif color == "black":
        return grayscale
    else:
        return white_bg_image

def draw_arc_text(draw, text, position, radius, start_angle, end_angle, font, color, clockwise=True):
    angle_step = (end_angle - start_angle) / (len(text) - 1)
    if clockwise:
        angle_step = -angle_step

    for i, char in enumerate(text):
        angle = start_angle + i * angle_step
        x = position[0] + radius * np.cos(np.radians(angle)) - draw.textsize(char, font=font)[0] / 2
        y = position[1] + radius * np.sin(np.radians(angle)) - draw.textsize(char, font=font)[1] / 2
        draw.text((x, y), char, font=font, fill=color)


def create_stamp_image(stamp):
    concert_name_parts = [part for part in [stamp.first_line, stamp.second_line, stamp.third_line] if part]
    date = stamp.date.strftime('%Y-%m-%d')
    color = stamp.color_choice
    font_choice = stamp.font_choice
    background_choice = stamp.background_choice
    center_image_choice = stamp.center_image_choice

    original_image_path = f"stamp_static/stamp_background/stamp_label_clean{background_choice}.png"
    background_image = convert_image(original_image_path, color)

    middle_image_paths = {
        1: "stamp_static/middle_image/bass_illustration_clean.png",
        2: "stamp_static/middle_image/guitar_illustration_clean.png",
        3: "stamp_static/middle_image/drums_illustration_clean.png",
        4: "stamp_static/middle_image/mike_illustration_clean.png",
    }
    center_image_path = middle_image_paths[center_image_choice]
    center_image = Image.open(staticfiles_storage.path(center_image_path)).resize((150, 150)).convert("RGBA")
    center_image = ImageOps.colorize(ImageOps.grayscale(center_image), black=color, white="white")

    mask = center_image.split()[3] if center_image.mode == 'RGBA' else None

    if stamp.third_line:
        font_large_size = 30
        radii = [160, 130, 110]
        angles = [-165, -165, -165]
        end_angles = [-15, -15, -15]
    elif stamp.second_line:
        font_large_size = 35
        radii = [150, 120]
        angles = [-165, -165]
        end_angles = [-15, -15]
    else:
        font_large_size = 45
        radii = [150]
        angles = [-165]
        end_angles = [-15]

    font_paths = {
        1: "stamp_static/stamp_fonts/kor_flower.ttf",
        2: "stamp_static/stamp_fonts/Dokdo-Regular.ttf",
        3: "stamp_static/stamp_fonts/NanumPenScript-Regular.ttf",
        4: "stamp_static/stamp_fonts/kor_happy_dobby.ttf",
        5: "stamp_static/stamp_fonts/kor_korea_hero.ttf",
        6: "stamp_static/stamp_fonts/kor_right_hippy.ttf",
    }
    font_large = ImageFont.truetype(staticfiles_storage.path(font_paths[font_choice]), font_large_size)
    font_small = ImageFont.truetype(staticfiles_storage.path(font_paths[font_choice]), 25)

    image = background_image.copy()
    draw = ImageDraw.Draw(image)
    image.paste(center_image, (225 - 75, 225 - 75), mask)

    for i, part in enumerate(concert_name_parts):
        draw_arc_text(draw, part, (225, 225), radii[i], angles[i], end_angles[i], font_large, color, clockwise=False)

    draw_arc_text(draw, date, (225, 225), 120, 150, 30, font_small, color, clockwise=False)

    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    image_content = ContentFile(buffer.getvalue(), 'stamp.png')

    return image_content


