import pygame

vec = pygame.math.Vector2


# Decorator function to define when a method is overriding an inherited
# classes method.
def overrides(interface_class):
    def overrider(method):
        assert(method.__name__ in dir(interface_class))
        return method
    return overrider


# Check if a key or nested keys exist in a dictionary
# If they do exist, return the value associated with the key
# Otherwise return None (couldn't find anything)
def checkKeyExist(dict, keys, i=0):
    if keys[i] in dict:
        if i + 1 == len(keys):
            return dict[keys[i]]
        return checkKeyExist(dict[keys[i]], keys, i+1)
    return None


# Get the current mouse position relative to the size of the scren
def getMousePos(game):
    mx, my = pygame.mouse.get_pos()
    difference = game.renderer.getDifference()
    mx -= difference[0]
    my -= difference[1]

    return mx, my


# Get the games scale relative to the screen and map size
def getScale(game, spriteRenderer):
    return game.renderer.getScale() * spriteRenderer.getFixedScale()
