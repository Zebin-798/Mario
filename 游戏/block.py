import pygame
import os


class Block(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height):
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)
        self.image_path = os.path.join('assets', 'Terrain', 'Ground.png')  # 更新路径
        try:
            self.image = pygame.image.load(self.image_path).convert_alpha()
            self.image = pygame.transform.scale(self.image, (width, height))
        except FileNotFoundError:
            print(f"找不到方块图片文件: {self.image_path}")
            self.image = pygame.Surface((width, height))
            pygame.draw.rect(self.image, (0, 255, 0), (0, 0, width, height))
            pygame.draw.rect(self.image, (0, 200, 0), (0, 0, width, height), 2)

    def draw(self, screen):
        """绘制方块到屏幕"""
        screen.blit(self.image, (self.rect.x, self.rect.y))