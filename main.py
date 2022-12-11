import asyncio
import math

import pygame
import requests
from rich import inspect

from world_map import WorldMap
from settings import RESOLUTION


class Player(pygame.sprite.Sprite):
    def __init__(self, player):
        super().__init__()
        x = player['x'] * RESOLUTION
        y = player['y'] * RESOLUTION
        dx = player['dx']
        dy = player['dy']
        w = 10
        h = 10
        color = player['color[]']
        # self.angle = 0
        # self.angle = math.degrees(math.atan2(dy, dx))
        # create surface that player marker will exist on (size of marker)
        self.player_surf = pygame.Surface([w, h], pygame.SRCALPHA)
        # draw the polygon the pepresent that player marker onto the surface
        self.player_icon = pygame.draw.polygon(self.player_surf, color, [(0, 10), (5, 0), (10, 10), (5, 5), (0, 10)], 0)
        # self.image & self.rect are required for sprite class
        self.rotate(player)

    def update(self, player):
        self.rotate(player)

    def rotate(self, player):
        x = player['x'] * RESOLUTION
        y = player['y'] * RESOLUTION
        dx = player['dx']
        dy = player['dy']
        angle = math.degrees(math.atan2(dy, dx)) + 270
        if angle < 0.0:
            angle += 360.0
        # print(x, y, angle)
        copy = self.player_surf.copy()
        self.image = pygame.transform.rotate(copy, angle)
        self.rect = self.image.get_rect(center=(x, y))
        self.mask = pygame.mask.from_surface(self.image)


class Airfield(pygame.sprite.Sprite):
    def __init__(self, airfield):
        self.name = id(self)
        self.is_selected = False
        super().__init__()
        self.angle = 0
        self.color = airfield['color[]']
        self.sx = airfield['sx'] * RESOLUTION
        self.sy = airfield['sy'] * RESOLUTION
        self.ex = airfield['ex'] * RESOLUTION
        self.ey = airfield['ey'] * RESOLUTION
        self.vec_beg = pygame.Vector2(self.sx, self.sy)
        self.vec_end = pygame.Vector2(self.ex, self.ey)
        self.vec_dir = self.vec_end - self.vec_beg
        self.w = self.vec_dir.length()
        self.h = 5
        self.vec_dir_n = self.vec_dir.normalize()
        self.vec_dir = math.degrees(math.atan2(-self.vec_dir_n.y, self.vec_dir_n.x))
        self.airstrip_rect = pygame.Surface([self.w, self.h], pygame.SRCALPHA)

        self.update()
        # self.airstrip_rect.fill((0, 0, 0))
        # self.airstrip_border_rect = self.airstrip_rect.get_rect()
        # pygame.draw.rect(self.airstrip_rect, self.color, [self.airstrip_border_rect.x + 1, self.airstrip_border_rect.y + 1, self.airstrip_border_rect.w - 2, self.airstrip_border_rect.h - 2])
        #
        #
        # self.image = self.airstrip_rect
        #
        # self.rect = self.image.get_rect(center=((self.sx+self.ex)/2, (self.sy+self.ey)/2))
        # self.rotate(self.vec_dir)
        # self.mask = pygame.mask.from_surface(self.image)

    # def update(self, airfields):
    #     for airfield in [el for el in war.map_obj if el['type'] == 'airfield']:
    #         print(self.name)
    #         sx = airfield['sx'] * RESOLUTION
    #         sy = airfield['sy'] * RESOLUTION
    #         ex = airfield['ex'] * RESOLUTION
    #         ey = airfield['ey'] * RESOLUTION
    #         vec_beg = pygame.Vector2(sx, sy)
    #         vec_end = pygame.Vector2(ex, ey)
    #         vec_dir = vec_end - vec_beg
    #         vec_dir = vec_dir.normalize()
    #         vec_dir = math.degrees(math.atan2(vec_dir.x, vec_dir.y)) + 90
    #         self.rect.center = ((sx+ex)/2, (sy+ey)/2)
    #         # angle = math.degrees(math.atan2(dy, dx)) + 270
    #         # if angle < 0.0:
    #         #     angle += 360.0
    #         self.rotate(vec_dir)
    def draw(self):
        pass

    def update(self):
        # pygame.draw.rect(self.original_image, self.color, [self.border.x+1, self.border.y+1, self.border.w-2, self.border.h-2])
        # self.image = self.original_image
        # self.airstrip_rect.fill((0, 0, 0))
        self.airstrip_border_rect = self.airstrip_rect.get_rect()
        pygame.draw.rect(self.airstrip_rect, self.color, [self.airstrip_border_rect.x + 1, self.airstrip_border_rect.y + 1, self.airstrip_border_rect.w - 2, self.airstrip_border_rect.h - 2])
        self.image = self.airstrip_rect

        self.rect = self.image.get_rect(center=((self.sx+self.ex)/2, (self.sy+self.ey)/2))
        self.rotate(self.vec_dir)
        self.mask = pygame.mask.from_surface(self.image)

    def select_check(self, mouse):
        if self.rect.collidepoint(mouse):
            # print(self.sx, self.sy)
            # print(self.ex, self.ey)
            # print(self.rect)
            # print(self.name)
            self.airstrip_rect.fill((144, 144, 144))
            self.rotate(self.vec_dir)
            self.mask = pygame.mask.from_surface(self.image)
            self.is_selected = True
            # return self.is_selected
            ils_vector = self.vec_beg + self.vec_dir_n * -100
            # print(ils_vector)
            # pygame.draw.line(war.background_copy, (255, 255, 255), self.vec_beg, self.vec_end, 1)
            return self.is_selected, self.vec_beg, ils_vector
        else:
            self.airstrip_rect.fill(self.color)
            self.rotate(self.vec_dir)
            self.mask = pygame.mask.from_surface(self.image)
            self.is_selected = False
            return self.is_selected, None, None
        # self.image = self.original_image
        # self.rotate(self.vec_dir)
        # self.mask = pygame.mask.from_surface(self.image)

    def rotate(self, angle):
        self.image = pygame.transform.rotate(self.airstrip_rect, angle)
        self.rect = self.image.get_rect(center=self.rect.center)
        self.mask = pygame.mask.from_surface(self.image)


class War:
    def __init__(self):

        self.ils_background = None
        self.web_request()

        pygame.init()
        self.selected = None
        self.clock = pygame.time.Clock()
        self.window = pygame.display.set_mode((1024, 1024))
        self.background = pygame.image.load('map.jpg').convert()
        self.background = pygame.transform.scale(self.background.copy(), (RESOLUTION, RESOLUTION))
        self.player = Player([el for el in self.map_obj if el['icon'] == 'Player'][0])
        self.airfields = [Airfield(el) for el in self.map_obj if el['type'] == 'airfield']
        self.all_sprites = pygame.sprite.Group([self.player, self.airfields])
        self.static_sprites = pygame.sprite.Group(self.airfields)
        self.running = True

    def run(self):
        while self.running:
            self.clock.tick(60)
            self.events()
            self.web_request()
            self.draw()
        pygame.quit()
        exit()

    def web_request(self):
        # self.all_sprites.update()
        asyncio.run(self.main())

    def events(self):

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                _ = {}
                for sprite in self.static_sprites:
                    self.selected, ils_beg, ils_end = sprite.select_check(event.pos)
                    _[sprite.name] = {'selected': self.selected, 'ils_beg': ils_beg, 'ils_end': ils_end}
                    self.ils_background = self.background.copy()
                    if self.selected: # if self.ils_beg is not None:
                        # inspect(sprite)
                        pygame.draw.line(self.ils_background, (0, 0, 0), _[sprite.name]['ils_beg'], _[sprite.name]['ils_end'], 5)
                        self.window.blit(self.ils_background, [0, 0])
                        self.selected = False
                    else:
                        self.window.blit(self.background, [0, 0])

                    pygame.display.flip()

                print(_)

    def draw(self):
        # print(self.selected)
        # self.player.rect.center = pygame.mouse.get_pos()
        # self.all_sprites.update(self.player)
        # self.static_sprites.update()
        self.background_copy = self.background.copy()
        collide = pygame.sprite.spritecollide(self.player, self.static_sprites, False, pygame.sprite.collide_mask)
        player_obj = [el for el in self.map_obj if el['icon'] == 'Player'][0]
        # # self.window.fill((69, 69, 69)) if collide else self.window.blit(self.background, [0, 0])
        # if self.selected:
        #     self.window.blit(self.ils_background, [0, 0])
        self.player.update(player_obj)
        # self.static_sprites.update()
        self.all_sprites.draw(self.window)
        pygame.display.flip()

    async def main(self):
        url = 'http://www.localhost:8111'
        loop = asyncio.get_event_loop()
        indicators = loop.run_in_executor(None, requests.get, f'{url}/indicators')
        # state = loop.run_in_executor(None, requests.get, f'{url}/state')
        map_obj = loop.run_in_executor(None, requests.get, f'{url}/map_obj.json')
        indicators = await indicators
        # state = await state
        map_obj = await map_obj
        self.indicators = indicators.json()
        # self.state = state.json()
        self.map_obj = map_obj.json()


if __name__ == '__main__':
    world_map = WorldMap()
    war = War()
    war.run()
