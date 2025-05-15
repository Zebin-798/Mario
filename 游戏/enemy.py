import pygame
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
        self.create_enemy_sprite()

        # 用于追踪连续碰撞，避免无限循环
        self.consecutive_collisions = 0

    def create_enemy_sprite(self):
        self.sprite = pygame.Surface((self.width * CHARACTER_SCALE, self.height * CHARACTER_SCALE), pygame.SRCALPHA)
        pygame.draw.rect(self.sprite, (255, 0, 0),
                         (0, 0, self.width * CHARACTER_SCALE, self.height * CHARACTER_SCALE))

        eye_size = int(3 * CHARACTER_SCALE)
        eye_y = int(5 * CHARACTER_SCALE)

        if self.direction == "left":
            pygame.draw.circle(self.sprite, (255, 255, 255),
                               (eye_size + 2, eye_y), eye_size)
        else:
            pygame.draw.circle(self.sprite, (255, 255, 255),
                               (self.width * CHARACTER_SCALE - eye_size - 2, eye_y), eye_size)

    def draw(self, screen):
        screen.blit(self.sprite, (self.rect.x, self.rect.y))

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
        # 应用重力
        self.apply_gravity(blocks)

        if not self.on_ground:
            return  # 不在地面上时不移动

        # 尝试水平移动
        old_x = self.rect.x

        if self.direction == "left":
            self.rect.x -= self.speed
        else:
            self.rect.x += self.speed

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

        # 更新精灵方向
        self.create_enemy_sprite()

    def check_collision_with_player(self, player):
        """检查与玩家的碰撞"""
        # 如果玩家从上方踩下，敌人立即消失
        if (player.rect.bottom < self.rect.centery and
                player.rect.bottom + player.velocity_y >= self.rect.top and
                player.rect.right > self.rect.left and
                player.rect.left < self.rect.right):
            player.velocity_y = -5  # 给玩家一个小反弹
            return True
        return False