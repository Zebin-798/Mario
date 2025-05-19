import pygame
import os
from constants import CHARACTER_SCALE, GRAVITY


class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height):
        super().__init__()
        self.width = width
        self.height = height
        self.rect = pygame.Rect(x, y, width * CHARACTER_SCALE, height * CHARACTER_SCALE)
        self.speed = 2
        self.direction = "left"
        self.on_ground = False
        self.velocity_y = 0

        # 动画相关变量
        self.animation_frame = 0
        self.animation_speed = 8
        self.current_sprite = None
        self.stomped = False  # 新增被踩状态

        # 加载精灵图片
        self.load_sprites()

        # 用于追踪连续碰撞，避免无限循环
        self.consecutive_collisions = 0

    def load_sprites(self):
        """加载并切割蘑菇怪图片为三个动作"""
        try:
            # 尝试加载图片
            image_path = os.path.join("assets", "Enemies", "Goombas.png")
            self.sprite_sheet = pygame.image.load(image_path).convert_alpha()

            # 获取精灵表实际尺寸
            sheet_width, sheet_height = self.sprite_sheet.get_size()

            # 计算实际精灵尺寸（考虑缩放）
            actual_width = self.width * CHARACTER_SCALE
            actual_height = self.height * CHARACTER_SCALE

            # 切割图片为三个动作帧（假设图片是水平排列的三个相同大小的帧）
            frame_width = sheet_width // 3
            frame_height = sheet_height

            # 向右走（第一帧）
            walk_right_frame = self.sprite_sheet.subsurface(pygame.Rect(0, 0, frame_width, frame_height))
            self.walk_right = pygame.transform.scale(walk_right_frame, (actual_width, actual_height))

            # 向左走（第二帧）
            walk_left_frame = self.sprite_sheet.subsurface(pygame.Rect(frame_width, 0, frame_width, frame_height))
            self.walk_left = pygame.transform.scale(walk_left_frame, (actual_width, actual_height))

            # 被踩扁（第三帧）
            stomped_frame = self.sprite_sheet.subsurface(pygame.Rect(frame_width * 2, 0, frame_width, frame_height))
            self.stomped_sprite = pygame.transform.scale(stomped_frame, (actual_width, actual_height))

            self.current_sprite = self.walk_left  # 默认向左走
            print(f"敌人精灵加载成功: {image_path}")
        except Exception as e:
            # 加载失败时创建默认方块
            print(f"警告: 加载敌人图片失败: {e}")
            self.create_default_sprites()

    def create_default_sprites(self):
        """创建默认的纯色精灵，用于图片加载失败时"""
        actual_width = self.width * CHARACTER_SCALE
        actual_height = self.height * CHARACTER_SCALE

        # 向右走（绿色）
        self.walk_right = pygame.Surface((actual_width, actual_height), pygame.SRCALPHA)
        self.walk_right.fill((0, 128, 0))

        # 向左走（深绿色）
        self.walk_left = pygame.Surface((actual_width, actual_height), pygame.SRCALPHA)
        self.walk_left.fill((0, 64, 0))

        # 被踩扁（暗红色）
        self.stomped_sprite = pygame.Surface((actual_width, actual_height), pygame.SRCALPHA)
        self.stomped_sprite.fill((128, 0, 0))

        self.current_sprite = self.walk_left

    def draw(self, screen):
        if self.current_sprite:
            screen.blit(self.current_sprite, (self.rect.x, self.rect.y))

    def apply_gravity(self, blocks):
        self.velocity_y += GRAVITY
        self.rect.y += self.velocity_y
        self.on_ground = False

        for block in blocks:
            if self.rect.colliderect(block.rect):
                if self.velocity_y > 0:
                    self.rect.bottom = block.rect.top
                    self.on_ground = True
                    self.velocity_y = 0
                elif self.velocity_y < 0:
                    self.rect.top = block.rect.bottom
                    self.velocity_y = 0

    def move(self, blocks, screen_width):
        if self.stomped:  # 被踩后不再移动
            return

        # 应用重力
        self.apply_gravity(blocks)

        if not self.on_ground:
            return  # 不在地面上时不移动

        # 更新动画帧
        self.animation_frame = (self.animation_frame + 1) % self.animation_speed

        # 尝试水平移动
        old_x = self.rect.x

        if self.direction == "left":
            self.rect.x -= self.speed
            self.current_sprite = self.walk_left
        else:
            self.rect.x += self.speed
            self.current_sprite = self.walk_right

        # 检查与方块的碰撞
        collision = False
        for block in blocks:
            if self.rect.colliderect(block.rect):
                collision = True
                break

        if collision:
            # 回退并改变方向
            self.rect.x = old_x
            self.direction = "right" if self.direction == "left" else "left"
            self.consecutive_collisions += 1

            # 如果连续碰撞太多次，可能是卡在了某个地方，强制移动
            if self.consecutive_collisions > 3:
                self.rect.y -= 1  # 尝试向上移动一点
                self.consecutive_collisions = 0
        else:
            self.consecutive_collisions = 0

            # 简单的边缘检测：检查底部是否悬空
            edge_test_rect = pygame.Rect(self.rect.x, self.rect.bottom, self.rect.width, 1)
            on_ground = False

            for block in blocks:
                if edge_test_rect.colliderect(block.rect):
                    on_ground = True
                    break

            if not on_ground:
                self.direction = "right" if self.direction == "left" else "left"

        # 确保敌人不会移出屏幕
        if self.rect.left < 0:
            self.rect.left = 0
            self.direction = "right"
        elif self.rect.right > screen_width:
            self.rect.right = screen_width
            self.direction = "left"

    def check_collision_with_player(self, player):
        """检查与玩家的碰撞"""
        if self.stomped:  # 已经被踩过则忽略
            return False

        # 如果玩家从上方踩下，敌人立即消失
        if (player.rect.bottom < self.rect.centery and
                player.rect.bottom + player.velocity_y >= self.rect.top and
                player.rect.right > self.rect.left and
                player.rect.left < self.rect.right):
            player.velocity_y = -5  # 给玩家一个小反弹
            self.stomped = True
            self.current_sprite = self.stomped_sprite  # 显示被踩扁的动画
            return True
        return False