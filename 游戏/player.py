import pygame
import os
from utils import load_sprite_sheets
from constants import PLAYER_SPEED, GRAVITY, JUMP_POWER, SCREEN_WIDTH, SCREEN_HEIGHT, CHARACTER_SCALE


class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height):
        super().__init__()
        # 加载所有精灵表
        self.SPRITES = load_sprite_sheets("MainCharacters", "Mario", 16, 16, True)

        # 新增：死亡图片（单独加载）
        self.death_image = self.load_death_image()
        self.is_dead = False
        self.death_time = 0
        self.DEATH_DURATION = 2000  # 死亡画面显示时间（毫秒）

        scaled_width = int(width * CHARACTER_SCALE)
        scaled_height = int(height * CHARACTER_SCALE)
        self.rect = pygame.Rect(x, y, scaled_width, scaled_height)
        self.speed = PLAYER_SPEED
        self.animation_count = 0
        self.sprite = self.SPRITES["idle_right"][0]
        self.velocity_x = 0
        self.velocity_y = 0
        self.direction = "right"
        self.on_ground = False

        # 血量系统
        self.health = 3
        self.invincible = False
        self.invincible_time = 0
        self.INVINCIBLE_DURATION = 1000  # 无敌时间（毫秒）

        self.update_sprite()

    def load_death_image(self):
        """加载单独的死亡图片"""
        try:
            death_path = os.path.join("assets", "MainCharacters", "Mario", "death.png")
            death_image = pygame.image.load(death_path).convert_alpha()
            # 缩放图片到角色大小
            scaled_width = int(16 * CHARACTER_SCALE)
            scaled_height = int(16 * CHARACTER_SCALE)
            return pygame.transform.scale(death_image, (scaled_width, scaled_height))
        except Exception as e:
            print(f"警告: 加载死亡图片失败: {e}")
            return None

    def update_sprite(self):
        """更新角色精灵动画（正常状态）"""
        if self.is_dead:
            return  # 死亡状态由专门方法处理

        if not self.on_ground:
            sprite_sheet = "jump"
        else:
            sprite_sheet = "idle" if self.velocity_x == 0 else "run"

        sprite_key = f"{sprite_sheet}_{self.direction}"
        sprite_index = (self.animation_count // 5) % len(self.SPRITES[sprite_key])
        self.sprite = self.SPRITES[sprite_key][sprite_index]
        self.animation_count += 1

    def draw(self, screen):
        """绘制角色到屏幕（处理死亡状态）"""
        if self.is_dead:
            if self.death_image:
                screen.blit(self.death_image, (self.rect.x, self.rect.y))
            return

        # 正常状态下的绘制逻辑
        if not self.invincible or (pygame.time.get_ticks() // 100) % 2 == 0:
            screen.blit(self.sprite, (self.rect.x, self.rect.y))

    def move(self, blocks):
        """处理角色移动和碰撞检测（死亡状态下不移动）"""
        if self.is_dead:
            return

        self.velocity_x = 0
        keys = pygame.key.get_pressed()

        if keys[pygame.K_LEFT]:
            self.move_left()
        if keys[pygame.K_RIGHT]:
            self.move_right()
        if keys[pygame.K_SPACE] and self.on_ground:
            self.jump()

        # 更新无敌状态
        if self.invincible and pygame.time.get_ticks() - self.invincible_time > self.INVINCIBLE_DURATION:
            self.invincible = False

        # 应用重力
        self.velocity_y += GRAVITY
        self.on_ground = False

        # 水平移动和碰撞检测
        self.rect.x += self.velocity_x
        self.handle_collision("x", blocks)
        self.keep_within_screen()

        # 垂直移动和碰撞检测
        self.rect.y += self.velocity_y
        self.handle_collision("y", blocks)
        self.keep_within_screen()

        self.update_sprite()

    def move_left(self):
        """向左移动"""
        self.velocity_x = -self.speed
        if self.direction != "left":
            self.direction = "left"
            self.animation_count = 0

    def move_right(self):
        """向右移动"""
        self.velocity_x = self.speed
        if self.direction != "right":
            self.direction = "right"
            self.animation_count = 0

    def jump(self):
        """跳跃"""
        self.velocity_y = JUMP_POWER
        self.on_ground = False

    def handle_collision(self, direction, blocks):
        """处理与方块的碰撞"""
        for block in blocks:
            if self.rect.colliderect(block.rect):
                if direction == "x":
                    if self.velocity_x > 0:  # 向右移动
                        self.rect.right = block.rect.left
                    if self.velocity_x < 0:  # 向左移动
                        self.rect.left = block.rect.right
                elif direction == "y":
                    if self.velocity_y > 0:  # 下落
                        self.rect.bottom = block.rect.top
                        self.on_ground = True
                        self.velocity_y = 0
                    if self.velocity_y < 0:  # 上升
                        self.rect.top = block.rect.bottom
                        self.velocity_y = 0

    def keep_within_screen(self):
        """确保角色在屏幕范围内"""
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH
        if self.rect.top < 0:
            self.rect.top = 0
            self.velocity_y = 0  # 防止飞出屏幕顶部后卡住
        if self.rect.bottom > SCREEN_HEIGHT:
            self.rect.bottom = SCREEN_HEIGHT
            self.on_ground = True
            self.velocity_y = 0

    def hit(self):
        """玩家受伤"""
        if not self.invincible:
            self.health -= 1
            self.invincible = True
            self.invincible_time = pygame.time.get_ticks()
            self.velocity_y = -5  # 被击中后向上反弹

            # 检查是否死亡
            if self.health <= 0:
                self.die()  # 调用死亡方法
                return True
        return False

    def die(self):
        """玩家死亡处理"""
        self.is_dead = True
        self.death_time = pygame.time.get_ticks()  # 记录死亡时间
        self.invincible = True  # 死亡后无敌，防止重复触发

