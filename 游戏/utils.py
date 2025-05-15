# utils.py
import pygame
import os
from constants import CHARACTER_SCALE

def flip(sprites):
    """翻转精灵列表，用于角色方向变化"""
    return [pygame.transform.flip(sprite, True, False) for sprite in sprites]

def load_sprite_sheets(dir1, dir2, width, height, direction=False):
    """
    加载并分割精灵表
    返回包含所有精灵帧的字典
    """
    path = os.path.join("assets", dir1, dir2)
    images = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]

    all_sprites = {}

    for image in images:
        sprite_sheet = pygame.image.load(os.path.join(path, image)).convert_alpha()
        sprites = []

        # 分割精灵表
        for i in range(sprite_sheet.get_width() // width):
            surface = pygame.Surface((width, height), pygame.SRCALPHA, 32)
            rect = pygame.Rect(i * width, 0, width, height)
            surface.blit(sprite_sheet, (0, 0), rect)
            # 使用缩放比例
            scaled_width = int(width * CHARACTER_SCALE)
            scaled_height = int(height * CHARACTER_SCALE)
            sprites.append(pygame.transform.scale(surface, (scaled_width, scaled_height)))

        # 根据方向需求处理精灵
        if direction:
            name = image.replace('.png', '')
            all_sprites[f"{name}_right"] = sprites
            all_sprites[f"{name}_left"] = flip(sprites)
        else:
            all_sprites[image.replace('.png', '')] = sprites

    return all_sprites