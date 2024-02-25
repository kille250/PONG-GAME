import pygame, sys, random, time


class Player:
    def __init__(self, x, y, width, height, speed, is_bot=False):
        self.rect = pygame.Rect(x, y, width, height)
        self.speed = speed
        self.is_bot = is_bot

    def move(self, screen_height, ball=None):
        if self.is_bot and ball is not None:
            if self.rect.centery < ball.rect.centery:
                self.rect.move_ip(0, self.speed)
            elif self.rect.centery > ball.rect.centery:
                self.rect.move_ip(0, -self.speed)
        else:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_UP]:
                self.rect.move_ip(0, -self.speed)
            if keys[pygame.K_DOWN]:
                self.rect.move_ip(0, self.speed)
        if self.rect.top <= 0:
            self.rect.top = 0
        if self.rect.bottom >= screen_height:
            self.rect.bottom = screen_height


class Ball:
    def __init__(self, x, y, size, speed_x, speed_y):
        self.rect = pygame.Rect(x, y, size, size)
        self.speed_x = speed_x
        self.speed_y = speed_y

    def move(self, screen_height, screen_width, player, opponent):
        self.rect.x += self.speed_x
        self.rect.y += self.speed_y

        if self.rect.top <= 0 or self.rect.bottom >= screen_height:
            self.speed_y *= -1

        if self.rect.left <= 0:
            self.speed_x *= -1
            return 1, opponent
        if self.rect.right >= screen_width:
            self.speed_x *= -1
            return 1, player

        if self.rect.colliderect(player.rect):
            self.speed_x *= -1
            if self.rect.right > player.rect.left:
                self.rect.right = player.rect.left
        if self.rect.colliderect(opponent.rect):
            self.speed_x *= -1
            if self.rect.left < opponent.rect.right:
                self.rect.left = opponent.rect.right

        return 0, None

    def increase_speed(self):
        self.speed_x *= 1.1
        self.speed_y *= 1.1

    def reset(self, screen_width, screen_height):
        self.rect.center = (screen_width / 2, screen_height / 2)
        self.speed_x = 7 * random.choice((-1, 1))
        self.speed_y = 7 * random.choice((-1, 1))


class Game:
    def __init__(
        self,
        screen_width,
        screen_height,
        player_speed,
        opponent_speed,
        ball_speed,
        player_color,
        opponent_color,
        ball_color,
        background_color,
    ):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.screen = pygame.display.set_mode((screen_width, screen_height))
        self.clock = pygame.time.Clock()
        self.player = Player(
            screen_width - 20, screen_height / 2 - 70, 10, 140, player_speed
        )
        self.opponent = Player(
            10, screen_height / 2 - 70, 10, 140, opponent_speed, is_bot=True
        )
        self.ball = Ball(
            screen_width / 2 - 15,
            screen_height / 2 - 15,
            30,
            ball_speed * random.choice((-1, 1)),
            ball_speed * random.choice((-1, 1)),
        )
        self.player_score = 0
        self.opponent_score = 0
        self.start_time = pygame.time.get_ticks()

        self.player_color = player_color
        self.opponent_color = opponent_color
        self.ball_color = ball_color
        self.background_color = background_color

        self.logo = pygame.image.load("perfact-logo.png")
        logo_width, logo_height = self.logo.get_size()
        new_width = 50
        new_height = int(logo_height * new_width / logo_width)
        self.logo = pygame.transform.smoothscale(self.logo, (new_width, new_height))
        self.logo_rect = self.logo.get_rect(
            bottomright=(screen_width - 10, screen_height - 10)
        )

    def update_screen(self):
        self.screen.fill(self.background_color)
        pygame.draw.rect(self.screen, self.player_color, self.player.rect)
        pygame.draw.rect(self.screen, self.opponent_color, self.opponent.rect)
        pygame.draw.ellipse(self.screen, self.ball_color, self.ball.rect)
        pygame.draw.aaline(
            self.screen,
            (0, 0, 0),
            (self.screen_width / 2, 0),
            (self.screen_width / 2, self.screen_height),
        )
        self.draw_score()
        self.screen.blit(self.logo, self.logo_rect)
        pygame.display.flip()

    def countdown(self):
        # Reset the ball and player positions
        self.ball.reset(self.screen_width, self.screen_height)
        self.player.rect.centery = self.screen_height / 2
        self.opponent.rect.centery = self.screen_height / 2

        # Update the screen before starting the countdown
        self.update_screen()

        font = pygame.font.Font(None, 72)
        for i in range(3, 0, -1):
            countdown_surface = font.render(str(i), True, (0, 0, 0))
            rect = pygame.Rect(
                (
                    self.screen_width / 2 - countdown_surface.get_width() / 2,
                    self.screen_height / 2 - countdown_surface.get_height() / 2,
                ),
                countdown_surface.get_size(),
            )
            self.screen.fill((255, 255, 255), rect)
            self.screen.blit(countdown_surface, rect.topleft)
            pygame.display.update(rect)
            time.sleep(1)

    def draw_score(self):
        score_text = f"Opponent: {self.player_score} - Player: {self.opponent_score}"
        self.score_surface = pygame.font.Font(None, 36).render(
            score_text, True, (0, 0, 0)
        )
        self.score_rect = self.score_surface.get_rect(
            center=(self.screen_width / 2, 10)
        )
        self.screen.blit(self.score_surface, self.score_rect)

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            self.player.move(self.screen_height)
            self.opponent.move(self.screen_height, self.ball)
            score, scorer = self.ball.move(
                self.screen_height, self.screen_width, self.player, self.opponent
            )
            if scorer is not None:
                if scorer == self.player:
                    self.player_score += score
                elif scorer == self.opponent:
                    self.opponent_score += score
                self.countdown()

            current_time = pygame.time.get_ticks()
            if current_time - self.start_time >= 10000:  # 10 seconds
                self.ball.increase_speed()
                self.start_time = current_time

            self.update_screen()

            pygame.display.flip()
            self.clock.tick(60)


if __name__ == "__main__":
    pygame.init()

    screen_width = 640
    screen_height = 480
    player_speed = 7
    opponent_speed = 7
    ball_speed = 7
    player_color = (255, 0, 0)  # Rot
    opponent_color = (0, 255, 0)  # Grün
    ball_color = (0, 0, 255)  # Blau
    background_color = (255, 255, 255)  # Weiß

    game = Game(
        screen_width,
        screen_height,
        player_speed,
        opponent_speed,
        ball_speed,
        player_color,
        opponent_color,
        ball_color,
        background_color,
    )

    game.run()
