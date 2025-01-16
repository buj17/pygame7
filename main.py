import os
import sys

import pygame

pygame.init()
fps = 30
size = width, height = 550, 550
drawing_distance = 5
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


class Field:
    def __init__(self, field: list[str]):
        self.field: list[list[str]] = []

        for row, line in enumerate(field):
            self.field.append([])
            for col, element in enumerate(line):
                self.field[-1].append(element)
                if element == '@':
                    self.player_row, self.player_col = row, col

        self.row_count = len(self.field)
        self.col_count = len(self.field[0])

    def get_cell(self, row: int, col: int):
        return self.field[row % self.row_count][col % self.col_count]

    def get_drawing_field(self, distance: int):
        start_row, stop_row = self.player_row - distance, self.player_row + distance
        start_col, stop_col = self.player_col - distance, self.player_col + distance

        drawing_field = []
        for row in range(start_row, stop_row + 1):
            drawing_field.append([])
            for col in range(start_col, stop_col + 1):
                drawing_field[-1].append(self.get_cell(row, col))

        return drawing_field

    def move_player(self, way: str):
        way_dict = {'up': (self.player_row - 1, self.player_col),
                    'down': (self.player_row + 1, self.player_col),
                    'left': (self.player_row, self.player_col - 1),
                    'right': (self.player_row, self.player_col + 1)}
        new_row, new_col = way_dict.get(way)
        if new_row is new_col is None:
            return
        if self.field[new_row % self.row_count][new_col % self.col_count] == '#':
            return

        self.field[self.player_row][self.player_col] = '.'
        self.player_row, self.player_col = way_dict[way]
        self.player_row %= self.row_count
        self.player_col %= self.col_count
        self.field[self.player_row][self.player_col] = '@'

    def render(self):
        for sprite in SpriteGroups.main_group.sprites():
            sprite.kill()

        drawing_field = self.get_drawing_field(drawing_distance)
        for row, line in enumerate(drawing_field):
            for col, element in enumerate(line):
                if element == '.':
                    Tile('empty', row, col)
                elif element == '#':
                    Tile('wall', row, col)
                elif element == '@':
                    Tile('empty', row, col)
                    Player(row, col, self)


class Tile(pygame.sprite.Sprite):
    def __init__(self, tile_type: str, row: int, col: int):
        super().__init__(SpriteGroups.main_group, SpriteGroups.tiles_group)
        self.image = tile_images[tile_type]
        self.rect = self.image.get_rect().move(tile_width * col, tile_height * row)


class Player(pygame.sprite.Sprite):
    def __init__(self, row: int, col: int, field: Field):
        super().__init__(SpriteGroups.main_group, SpriteGroups.player_group)
        self.image = player_image
        self.rect = self.image.get_rect().move(tile_width * col + 15, tile_height * row + 5)
        self.row = row
        self.col = col
        self.field = field

    def move_player(self, way: str):
        self.field.move_player(way)

    def update_rect(self):
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


class MainWindow:
    def __init__(self):
        self.field = Field(load_level('data/map.txt'))

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

        clock = pygame.time.Clock()
        running = True

        while running:
            screen.fill((0, 0, 0))
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.terminate()
                SpriteGroups.main_group.update(event)

            self.field.render()
            SpriteGroups.main_group.update()
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
