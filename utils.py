import pygame

vec = pygame.math.Vector2


# Decorator function to define when a method is overriding an inherited
# classes method.
def overrides(interface_class):
    def overrider(method):
        assert(method.__name__ in dir(interface_class))
        return method
    return overrider
