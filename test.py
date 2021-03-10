import pygame
import random
import pygame._sdl2
import itertools

pygame.init()

random_queue = itertools.cycle((-1, 0, 1, 0, 0, 1, 1, -1, -1))

cache = {}

class GameObject:
    def __init__(self, renderer):
        color = random.choice(('white', 'red', 'blue', 'yellow'))
        self.color = color
        if not color in cache:
            surface = pygame.Surface((64, 64))
            surface.set_colorkey((1,2,3))
            surface.fill((1,2,3))
            pygame.draw.circle(surface, color, (32, 32), 6)
            cache[color] = pygame._sdl2.Texture.from_surface(renderer, surface)
        
        self.rect = pygame.Rect((random.randrange(0, 800), random.randrange(0, 800), 64, 64))
        self.image = cache[color]
    
    def update(self):
        self.rect.move_ip(next(random_queue), next(random_queue))
    
def main():        
    window = pygame._sdl2.Window("SDL2", size=(800, 800))
    renderer = pygame._sdl2.Renderer(window, vsync=False)
    renderer.draw_color = (0,0,0,255) 
    buffer = pygame._sdl2.Texture(renderer, (800, 800), target=True)
    buffer.blend_mode = 1

    font = pygame.font.SysFont('Arial', 35)

    clock = pygame.time.Clock()

    objects = [GameObject(renderer) for _ in range(20000)]
    #objects = sorted([GameObject(renderer) for _ in range(20000)], key=lambda x: x.color)
   
    old_time = pygame.time.get_ticks()
    acc = 0.
    while True:
        renderer.target = buffer 
        
        renderer.clear()
        
        new_time = pygame.time.get_ticks()
        delta_time = new_time - old_time
        old_time = new_time
        acc += delta_time
        
        events = pygame.event.get()
        for e in events:
            if e.type == pygame.QUIT: return
            if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE: return

        while acc > 1000./31.:
            for o in objects:
                o.update()
            acc -= 1000./29.
            if acc < 0: 
                acc = 0

        for o in objects:
            o.image.draw(dstrect=o.rect)

        tmp = font.render(f'{clock.get_fps():.2f}', True, 'black')
        pygame._sdl2.Texture.from_surface(renderer, tmp).draw(dstrect=(10, 10))
        tmp = font.render(f'{clock.get_fps():.2f}', True, 'white')
        pygame._sdl2.Texture.from_surface(renderer, tmp).draw(dstrect=(11, 11))

        renderer.target = None
        
        buffer.draw()
        renderer.present() 
        clock.tick()

main()