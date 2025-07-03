import pygame
import random
import sys
from pygame.locals import *

# 初始化pygame
pygame.init()

# 游戏常量
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 600
GRID_SIZE = 30
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE
FPS = 60

# 颜色定义
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
LIGHT_GREEN = (100, 255, 100)
RED = (255, 0, 0)
GOLD = (255, 215, 0)
PURPLE = (128, 0, 128)
GRAY = (128, 128, 128)

# 方向
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)


class Snake:
    def __init__(self):
        """初始化蛇"""
        self.positions = [(GRID_WIDTH // 2, GRID_HEIGHT // 2)]  # 蛇初始位置在屏幕中央
        self.direction = RIGHT  # 初始方向向右
        self.length = 1  # 初始长度
        self.score = 0  # 初始分数
        self.color = GREEN  # 蛇头颜色
        self.body_color = LIGHT_GREEN  # 蛇身颜色

    def get_head_position(self):
        """获取蛇头位置"""
        return self.positions[0]

    def update(self):
        """更新蛇的位置"""
        head = self.get_head_position()
        x, y = self.direction
        new_head = ((head[0] + x) % GRID_WIDTH, (head[1] + y) % GRID_HEIGHT)

        # 检查是否撞到自己
        if new_head in self.positions[1:]:
            return True  # 游戏结束

        self.positions.insert(0, new_head)
        if len(self.positions) > self.length:
            self.positions.pop()
        return False  # 游戏继续

    def reset(self):
        """重置蛇的状态"""
        self.positions = [(GRID_WIDTH // 2, GRID_HEIGHT // 2)]
        self.direction = RIGHT
        self.length = 1
        self.score = 0

    def render(self, surface):
        """绘制蛇"""
        for i, p in enumerate(self.positions):
            color = self.color if i == 0 else self.body_color
            rect = pygame.Rect((p[0] * GRID_SIZE, p[1] * GRID_SIZE), (GRID_SIZE, GRID_SIZE))
            pygame.draw.rect(surface, color, rect)
            pygame.draw.rect(surface, BLACK, rect, 1)  # 边框


class Food:
    def __init__(self):
        """初始化食物"""
        self.position = (0, 0)
        self.color = RED
        self.type = "normal"  # normal/gold/purple
        self.randomize_position()

    def randomize_position(self, snake_positions=None, obstacles=None):
        """随机生成食物位置"""
        if snake_positions is None:
            snake_positions = []
        if obstacles is None:
            obstacles = []

        # 随机决定食物类型
        rand = random.random()
        if rand < 0.05:  # 5%紫色食物
            self.type = "purple"
            self.color = PURPLE
        elif rand < 0.15:  # 10%金色食物
            self.type = "gold"
            self.color = GOLD
        else:  # 85%普通食物
            self.type = "normal"
            self.color = RED

        while True:
            self.position = (random.randint(0, GRID_WIDTH - 1),
                             random.randint(0, GRID_HEIGHT - 1))
            if (self.position not in snake_positions and
                    self.position not in obstacles):
                break


class Obstacle:
    def __init__(self):
        """初始化障碍物"""
        self.positions = []
        self.color = GRAY

    def generate(self, count=5):
        """生成指定数量的障碍物"""
        self.positions = []
        for _ in range(count):
            while True:
                pos = (random.randint(0, GRID_WIDTH - 1), (random.randint(0, GRID_HEIGHT - 1)))
                if pos not in self.positions:
                    self.positions.append(pos)
                    break

    def render(self, surface):
        """绘制障碍物"""
        for p in self.positions:
            rect = pygame.Rect((p[0] * GRID_SIZE, p[1] * GRID_SIZE), (GRID_SIZE, GRID_SIZE))
            pygame.draw.rect(surface, self.color, rect)
            pygame.draw.rect(surface, BLACK, rect, 1)  # 边框


class Game:
    def __init__(self):
        """初始化游戏"""
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption('Snake Game')
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont('arial', 20)
        self.big_font = pygame.font.SysFont('arial', 50)

        self.snake = Snake()
        self.food = Food()
        self.obstacle = Obstacle()
        self.obstacle_mode = False  # 障碍物模式默认关闭
        self.speed = 10  # 初始速度
        self.game_over = False
        self.paused = False
        self.state = "MENU"  # MENU/PLAYING/GAME_OVER

    def draw_text(self, text, font, color, surface, x, y):
        """绘制文本"""
        text_obj = font.render(text, True, color)
        text_rect = text_obj.get_rect()
        text_rect.center = (x, y)
        surface.blit(text_obj, text_rect)

    def handle_events(self):
        """处理用户输入"""
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == KEYDOWN:
                if self.state == "MENU":
                    if event.key == K_RETURN:
                        self.state = "PLAYING"
                    elif event.key == K_o:
                        self.obstacle_mode = not self.obstacle_mode
                        if self.obstacle_mode:
                            self.obstacle.generate()
                    elif event.key == K_1:
                        self.speed = 5  # 慢速
                    elif event.key == K_2:
                        self.speed = 10  # 中速
                    elif event.key == K_3:
                        self.speed = 15  # 快速

                elif self.state == "PLAYING":
                    if event.key == K_p:
                        self.paused = not self.paused
                    elif event.key == K_UP and self.snake.direction != DOWN:
                        self.snake.direction = UP
                    elif event.key == K_DOWN and self.snake.direction != UP:
                        self.snake.direction = DOWN
                    elif event.key == K_LEFT and self.snake.direction != RIGHT:
                        self.snake.direction = LEFT
                    elif event.key == K_RIGHT and self.snake.direction != LEFT:
                        self.snake.direction = RIGHT

                elif self.state == "GAME_OVER":
                    if event.key == K_r:
                        self.reset_game()
                        self.state = "PLAYING"
                    elif event.key == K_m:
                        self.reset_game()
                        self.state = "MENU"

    def update(self):
        """更新游戏状态"""
        if self.state != "PLAYING" or self.paused:
            return

        # 控制游戏速度
        if pygame.time.get_ticks() % (1000 // self.speed) != 0:
            return

        # 更新蛇的位置
        game_over = self.snake.update()

        # 检查是否撞到障碍物
        if self.obstacle_mode and self.snake.get_head_position() in self.obstacle.positions:
            game_over = True

        if game_over:
            self.state = "GAME_OVER"
            return

        # 检查是否吃到食物
        if self.snake.get_head_position() == self.food.position:
            if self.food.type == "normal":
                self.snake.length += 1
                self.snake.score += 10
            elif self.food.type == "gold":
                self.snake.length += 1
                self.snake.score += 20
            elif self.food.type == "purple":
                self.snake.length = max(1, self.snake.length // 2)
                self.snake.score += 5

            # 根据分数调整速度
            self.speed = min(20, 10 + self.snake.score // 100)

            # 生成新食物
            snake_positions = self.snake.positions
            obstacles = self.obstacle.positions if self.obstacle_mode else []
            self.food.randomize_position(snake_positions, obstacles)

    def draw(self):
        """绘制游戏界面"""
        self.screen.fill(BLACK)

        if self.state == "MENU":
            self.draw_menu()
        elif self.state == "PLAYING":
            self.draw_game()
        elif self.state == "GAME_OVER":
            self.draw_game_over()

        pygame.display.update()

    def draw_menu(self):
        """绘制菜单界面"""
        self.draw_text("SNAKE GAME", self.big_font, WHITE, self.screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4)
        self.draw_text("Press ENTER to Start", self.font, WHITE, self.screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.draw_text("Press O to Toggle Obstacles: " + ("ON" if self.obstacle_mode else "OFF"),
                       self.font, WHITE, self.screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 40)
        self.draw_text("Press 1/2/3 to Set Speed: " + str(self.speed),
                       self.font, WHITE, self.screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 80)
        self.draw_text("Use Arrow Keys to Control", self.font, WHITE, self.screen, SCREEN_WIDTH // 2,
                       SCREEN_HEIGHT // 2 + 120)

    def draw_game(self):
        """绘制游戏界面"""
        # 绘制分数和速度
        self.draw_text(f"Score: {self.snake.score}", self.font, WHITE, self.screen, SCREEN_WIDTH - 80, 20)
        self.draw_text(f"Speed: {self.speed}", self.font, WHITE, self.screen, 60, 20)

        # 绘制障碍物
        if self.obstacle_mode:
            self.obstacle.render(self.screen)

        # 绘制食物
        food_rect = pygame.Rect((self.food.position[0] * GRID_SIZE, self.food.position[1] * GRID_SIZE),
                                (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(self.screen, self.food.color, food_rect)
        pygame.draw.rect(self.screen, BLACK, food_rect, 1)  # 边框

        # 绘制蛇
        self.snake.render(self.screen)

        # 暂停提示
        if self.paused:
            self.draw_text("PAUSED", self.big_font, WHITE, self.screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)

    def draw_game_over(self):
        """绘制游戏结束界面"""
        self.draw_text("GAME OVER", self.big_font, WHITE, self.screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3)
        self.draw_text(f"Final Score: {self.snake.score}", self.font, WHITE, self.screen, SCREEN_WIDTH // 2,
                       SCREEN_HEIGHT // 2)
        self.draw_text("Press R to Restart", self.font, WHITE, self.screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50)
        self.draw_text("Press M to Menu", self.font, WHITE, self.screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 90)

    def reset_game(self):
        """重置游戏状态"""
        self.snake.reset()
        self.food.randomize_position()
        if self.obstacle_mode:
            self.obstacle.generate()
        self.game_over = False
        self.paused = False

    def run(self):
        """运行游戏主循环"""
        while True:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)


# 启动游戏
if __name__ == "__main__":
    game = Game()
    game.run()