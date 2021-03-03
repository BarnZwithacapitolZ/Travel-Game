import random
# import pygame as pg

# class Rectangle(pg.sprite.Sprite):
#     def __init__(self):
#         pg.sprite.Sprite.__init__(self)
#         self.original_image = pg.Surface((100, 100))
#         self.original_image.fill((4, 0, 0))
#         self.image = self.original_image
#         self.rect = self.image.get_rect()

#     def set_rounded(self, roundness):
#         size = self.original_image.get_size()
#         self.rect_image = pg.Surface(size, pg.SRCALPHA)
#         pg.draw.rect(self.rect_image, (255, 255, 255), (0, 0, *size), border_radius=roundness)

#         self.image = self.original_image.copy().convert_alpha()
#         self.image.blit(self.rect_image, (0, 0), None, pg.BLEND_RGBA_MIN) 

# pg.init()
# window = pg.display.set_mode((500, 500))

# SIZE = 500, 500
# SCANLINES = pg.Surface(SIZE).convert_alpha()
# SCANLINES.fill((0,0,0,0))
# for j in range(0, SIZE[1], 2):
#     SCANLINES.fill((0,0,0, 255), (0, j, SIZE[0], 1)) # or slightly transparent if desired.


# run = True
# while run:
#     for event in pg.event.get():
#         if event.type == pg.QUIT:
#             run = False

#     window.fill((246, 246, 238))
#     window.blit(SCANLINES, (0, 0))
#     pg.display.flip()


weights = [0, 100]
values = ['a', 'b']

picks = [v for v, d in zip(values, weights) for _ in range(d)]

print(picks)

for _ in range(12):
    print(random.choice(picks))