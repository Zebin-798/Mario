# main.py
import pygame
import os
import random
from player import Player
from enemy import Enemy
from block import Block
from constants import *


def main():
    pygame.init()

    # 初始化字体（保持原代码不变）
    font_names = ["SimHei", "WenQuanYi Micro Hei", "Heiti TC", "Microsoft YaHei"]
    font = None
    for name in font_names:
        try:
            font = pygame.font.SysFont(name, 36)
            print(f"使用系统字体: {name}")
            break
        except:
            continue
    if not font:
        print("警告：未找到中文字体，使用默认字体")
        font = pygame.font.SysFont(None, 36)

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("踩踩棒")
    clock = pygame.time.Clock()

    # 游戏难度设置（保持原代码不变）
    difficulty_level = 1
    SCORE_TO_INCREASE_DIFFICULTY = 10

    # 平台生成函数（保持原代码不变）
    def is_overlapping(new_platform, existing_platforms):
        new_x, new_y, new_length = new_platform
        new_rect = pygame.Rect(new_x, new_y, new_length * BLOCK_SIZE, BLOCK_SIZE)
        for plat in existing_platforms:
            x, y, length = plat
            rect = pygame.Rect(x, y, length * BLOCK_SIZE, BLOCK_SIZE)
            if new_rect.colliderect(rect):
                return True
        return False

    def generate_platforms(num_platforms, difficulty):
        platforms = []
        max_attempts = 100
        for _ in range(num_platforms):
            attempt = 0
            while attempt < max_attempts:
                min_width = max(3 - (difficulty - 1), 1)
                max_width = max(10 - (difficulty - 1), 3)
                platform_width = random.randint(min_width, max_width) * BLOCK_SIZE
                platform_x = random.randint(0, SCREEN_WIDTH - platform_width)
                platform_y = random.randint(100, SCREEN_HEIGHT - 3 * BLOCK_SIZE)
                platform_length = platform_width // BLOCK_SIZE
                new_platform = (platform_x, platform_y, platform_length)
                if not is_overlapping(new_platform, platforms):
                    platforms.append(new_platform)
                    break
                attempt += 1
        return platforms

    # 生成初始平台（保持原代码不变）
    platforms = generate_platforms(5, difficulty_level)

    # 创建地图（保持原代码不变）
    blocks = []
    for x in range(0, SCREEN_WIDTH, BLOCK_SIZE):
        blocks.append(Block(x, SCREEN_HEIGHT - BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE))
    for plat in platforms:
        x, y, length = plat
        for i in range(length):
            blocks.append(Block(x + i * BLOCK_SIZE, y, BLOCK_SIZE, BLOCK_SIZE))

    # 初始化玩家（保持原代码不变）
    player = Player(100, SCREEN_HEIGHT - BLOCK_SIZE - int(16 * CHARACTER_SCALE), 16, 16)

    # 初始化敌人（保持原代码不变）
    enemies = [
        Enemy(200, SCREEN_HEIGHT - BLOCK_SIZE - int(16 * CHARACTER_SCALE), 16, 16),
        Enemy(400, SCREEN_HEIGHT - 150 - int(16 * CHARACTER_SCALE), 16, 16),
        Enemy(600, SCREEN_HEIGHT - 250 - int(16 * CHARACTER_SCALE), 16, 16)
    ]

    # 游戏状态
    score = 0
    game_over = False
    max_health = 5  # 最大生命值限制

    # 敌人生成计时器（保持原代码不变）
    enemy_spawn_timer = 0
    ENEMY_SPAWN_DELAY = 5000

    # 生命加成相关变量
    health_added = False  # 是否添加了生命
    health_added_timer = 0  # 生命加成提示计时器
    HEALTH_ADD_DURATION = 2000  # 提示显示时间（毫秒）
    HEALTH_ADD_PROBABILITY = 0.1  # 杀怪加血概率（10%）

    # 主游戏循环
    running = True
    while running:
        current_time = pygame.time.get_ticks()

        # 处理事件（保持原代码不变）
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        if not game_over:
            # 游戏逻辑更新（保持原代码不变）
            player.move(blocks)

            # 检查是否需要提升难度（保持原代码不变）
            if score % SCORE_TO_INCREASE_DIFFICULTY == 0 and score > 0:
                new_difficulty = (score // SCORE_TO_INCREASE_DIFFICULTY) + 1
                if new_difficulty > difficulty_level:
                    difficulty_level = new_difficulty
                    platforms = generate_platforms(5, difficulty_level)
                    blocks = []
                    for x in range(0, SCREEN_WIDTH, BLOCK_SIZE):
                        blocks.append(Block(x, SCREEN_HEIGHT - BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE))
                    for plat in platforms:
                        x, y, length = plat
                        for i in range(length):
                            blocks.append(Block(x + i * BLOCK_SIZE, y, BLOCK_SIZE, BLOCK_SIZE))

            # 更新敌人
            for enemy in enemies[:]:
                enemy.move(blocks, SCREEN_WIDTH)
                if enemy.check_collision_with_player(player):
                    enemies.remove(enemy)
                    score += 1

                    # 新增功能：随机加命
                    if random.random() < HEALTH_ADD_PROBABILITY and player.health < max_health:
                        player.health += 1
                        health_added = True
                        health_added_timer = current_time

            # 检查敌人是否碰到玩家侧面（保持原代码不变）
            for enemy in enemies:
                if (player.rect.right > enemy.rect.left and
                        player.rect.left < enemy.rect.right and
                        player.rect.bottom > enemy.rect.top + 10 and
                        player.rect.top < enemy.rect.bottom):
                    if player.hit():
                        if player.health <= 0:
                            game_over = True

            # 敌人生成（保持原代码不变）
            if current_time - enemy_spawn_timer > ENEMY_SPAWN_DELAY:
                spawn_positions = [
                    (100, SCREEN_HEIGHT - BLOCK_SIZE - int(16 * CHARACTER_SCALE)),
                    (300, SCREEN_HEIGHT - 200 - int(16 * CHARACTER_SCALE)),
                    (500, SCREEN_HEIGHT - 150 - int(16 * CHARACTER_SCALE)),
                    (700, SCREEN_HEIGHT - 250 - int(16 * CHARACTER_SCALE))
                ]
                spawn_pos = spawn_positions[random.randint(0, len(spawn_positions) - 1)]
                enemies.append(Enemy(spawn_pos[0], spawn_pos[1], 16, 16))
                enemy_spawn_timer = current_time

            # 检查生命加成提示是否过期
            if health_added and current_time - health_added_timer > HEALTH_ADD_DURATION:
                health_added = False

        # 绘制游戏
        screen.fill(SKY_BLUE)

        # 绘制玩家和敌人（保持原代码不变）
        player.draw(screen)
        for block in blocks:
            block.draw(screen)
        for enemy in enemies:
            enemy.draw(screen)

        # 绘制分数和血量（保持原代码不变）
        score_text = font.render(f"分数: {score}", True, (255, 255, 255))
        screen.blit(score_text, (10, 10))

        health_text = font.render(f"生命: {player.health}", True, (255, 255, 255))
        screen.blit(health_text, (10, 50))

        difficulty_text = font.render(f"难度: {difficulty_level}", True, (255, 255, 255))
        screen.blit(difficulty_text, (10, 90))

        # 绘制生命加成提示
        if health_added:
            add_health_text = font.render("+1 生命!", True, (0, 255, 0))
            screen.blit(add_health_text, (SCREEN_WIDTH // 2 - 50, SCREEN_HEIGHT // 2 - 100))

        # 游戏结束显示（保持原代码不变）
        if game_over:
            game_over_text = font.render("游戏结束", True, (255, 0, 0))
            restart_text = font.render("按 R 键重新开始", True, (255, 255, 255))
            screen.blit(game_over_text, (SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 50))
            screen.blit(restart_text, (SCREEN_WIDTH // 2 - 120, SCREEN_HEIGHT // 2))

            # 检查重新开始（保持原代码不变）
            keys = pygame.key.get_pressed()
            if keys[pygame.K_r]:
                player.health = 3
                score = 0
                game_over = False
                difficulty_level = 1
                platforms = generate_platforms(5, difficulty_level)
                blocks = []
                for x in range(0, SCREEN_WIDTH, BLOCK_SIZE):
                    blocks.append(Block(x, SCREEN_HEIGHT - BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE))
                for plat in platforms:
                    x, y, length = plat
                    for i in range(length):
                        blocks.append(Block(x + i * BLOCK_SIZE, y, BLOCK_SIZE, BLOCK_SIZE))
                enemies.clear()
                enemies.extend([
                    Enemy(200, SCREEN_HEIGHT - BLOCK_SIZE - int(16 * CHARACTER_SCALE), 16, 16),
                    Enemy(400, SCREEN_HEIGHT - 150 - int(16 * CHARACTER_SCALE), 16, 16),
                    Enemy(600, SCREEN_HEIGHT - 250 - int(16 * CHARACTER_SCALE), 16, 16)
                ])

        # 更新显示（保持原代码不变）
        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()


if __name__ == "__main__":
    main()

