import os
import sys

import pygame

pygame.init()
fps = 30
size = width, height = 550, 550
screen = pygame.display.set_mode(size)


def load_image(filename: str | os.PathLike, colorkey=None) -> pygame.Surface:
    """Функция для получения изображения из файла"""
    fullname = filename
    image = pygame.image.load(fullname)
    if colorkey is not None:
        image = image.convert()
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image


def load_level(filename: str | os.PathLike) -> list[str]:
    # читаем уровень, убирая символы перевода строки
    with open(filename) as mapFile:
        level_map = [line.strip() for line in mapFile]

    # и подсчитываем максимальную длину
    max_width = max(map(len, level_map))

    # дополняем каждую строку пустыми клетками ('.')
    return list(map(lambda x: x.ljust(max_width, '.'), level_map))


tile_images: dict[str, pygame.Surface] = {
    'wall': load_image('data/box.png'),
    'empty': load_image('data/grass.png')
}
player_image = load_image('data/mar.png')

tile_width = tile_height = 50


class SpriteGroups:
    main_group = pygame.sprite.Group()
    tiles_group = pygame.sprite.Group()
    boxes_group = pygame.sprite.Group()
    grass_group = pygame.sprite.Group()
    player_group = pygame.sprite.Group()


class Level:
    def __init__(self, level_structure: list[str]):
        self.field = []
        for row in range(len(level_structure)):
            self.field.append([])
            for col in range(len(level_structure[row])):
                if level_structure[row][col] == '.':
                    Tile('empty', col, row)
                    self.field[-1].append('.')
                elif level_structure[row][col] == '#':
                    Tile('wall', col, row)
                    self.field[-1].append('#')
                elif level_structure[row][col] == '@':
                    Tile('empty', col, row)
                    Player(col, row, self)
                    self.field[-1].append('.')

    def get_cell(self, row: int, col: int):
        return self.field[row][col]


class Tile(pygame.sprite.Sprite):
    def __init__(self, tile_type: str, pos_x: int, pos_y: int):
        if tile_type == 'wall':
            super().__init__(SpriteGroups.main_group, SpriteGroups.tiles_group, SpriteGroups.boxes_group)
        if tile_type == 'empty':
            super().__init__(SpriteGroups.main_group, SpriteGroups.tiles_group, SpriteGroups.grass_group)
        self.image = tile_images[tile_type]
        self.rect = self.image.get_rect().move(tile_width * pos_x, tile_height * pos_y)
        self.x, self.y = pos_x * tile_width, pos_y * tile_height


class Player(pygame.sprite.Sprite):
    def __init__(self, col: int, row: int, level: Level):
        super().__init__(SpriteGroups.main_group, SpriteGroups.player_group)
        self.image = player_image
        self.rect = self.image.get_rect().move(tile_width * col + 15, tile_height * row + 5)
        self.row = row
        self.col = col
        self.x = tile_width * col + 15
        self.y = tile_height * row + 5
        self.level = level

    def move_player(self, way: str):
        cords_dict = {'down': (self.row + 1, self.col),
                      'up': (self.row - 1, self.col),
                      'left': (self.row, self.col - 1),
                      'right': (self.row, self.col + 1)}
        new_row, new_col = cords_dict[way]
        if self.level.get_cell(new_row, new_col) == '.':
            self.row, self.col = new_row, new_col
            self.update_rect()

    def update_rect(self):
        self.x = tile_width * self.col + 15
        self.y = tile_height * self.row + 5
        self.rect.x = self.col * tile_width + 15
        self.rect.y = self.row * tile_height + 5

    def update(self, *args, **kwargs):
        if args:
            event: pygame.event.Event = args[0]
            way_dict = {pygame.K_DOWN: 'down',
                        pygame.K_UP: 'up',
                        pygame.K_LEFT: 'left',
                        pygame.K_RIGHT: 'right'}
            if event.type == pygame.KEYDOWN:
                way = way_dict.get(event.key)
                if way:
                    self.move_player(way)


class Camera:
    def __init__(self):
        self.dx = self.dy = 0

    def apply(self, sprite):
        sprite.rect.x = sprite.x + self.dx
        sprite.rect.y = sprite.y + self.dy

    def update(self, target):
        self.dx = -(target.col * tile_width + target.rect.w // 2) + width // 2
        self.dy = -(target.row * tile_height + target.rect.h // 2) + height // 2


class MainWindow:
    def __init__(self):
        self.level = Level(load_level('data/map.txt'))
        self.camera = Camera()

    def show_intro(self):
        image = pygame.transform.scale(load_image('data/fon.jpg'), (width, height))
        screen.blit(image, (0, 0))
        pygame.display.flip()
        while True:
            event = pygame.event.wait()
            if event.type == pygame.QUIT:
                self.terminate()
            if event.type in (pygame.MOUSEBUTTONDOWN, pygame.KEYDOWN):
                break

    def run(self):
        self.show_intro()

        player = SpriteGroups.player_group.sprites()[0]

        clock = pygame.time.Clock()
        running = True

        while running:
            screen.fill((0, 0, 0))
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.terminate()
                SpriteGroups.main_group.update(event)
            SpriteGroups.main_group.update()

            self.camera.update(player)
            for sprite in SpriteGroups.main_group:
                self.camera.apply(sprite)

            SpriteGroups.main_group.draw(screen)
            SpriteGroups.player_group.draw(screen)
            pygame.display.flip()
            clock.tick(fps)

    def terminate(self):
        pygame.quit()
        sys.exit()


if __name__ == '__main__':
    window = MainWindow()
    window.run()
