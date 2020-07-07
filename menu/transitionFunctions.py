import pygame 
from pygame.locals import *
from config import *

def transitionAnimationOpen(obj, menu, animation):
    obj.x += 100

    if obj.x >= 0:
        obj.animations.remove(animation)
        menu.close()
        menu.transition()

    obj.rect.x = obj.x * menu.renderer.getScale()


def transitionAnimationClose(obj, menu, animation):
    obj.x += 100

    if obj.x >= config["graphics"]["displayWidth"]:
        obj.animations.remove(animation)
        menu.close()

    obj.rect.x = obj.x * menu.renderer.getScale()


def transitionFadeIn(obj, menu, animation):
    obj.setAlpha(obj.getAlpha() + 20)
    obj.dirty = True

    if obj.getAlpha() >= 255:
        obj.animations.remove(animation)
        menu.close()
        menu.transition()


def transitionFadeOut(obj, menu, animation):
    obj.setAlpha(obj.getAlpha() - 20)
    obj.dirty = True

    if obj.getAlpha() <= 0:
        obj.animations.remove(animation)
        menu.close()




transitionspeed = 40

def transitionLeft(obj, menu, animation):
    obj.x -= transitionspeed * 100 * menu.game.dt

    if obj.x < -500:
        obj.animations.remove(animation)
        menu.close()

    obj.rect.x = obj.x * menu.renderer.getScale()
    

def transitionLeftUnpause(obj, menu, animation):
    obj.x -= transitionspeed * 100 * menu.game.dt

    if obj.x < -500:
        obj.animations.remove(animation)
        menu.close()
        menu.game.paused = False

    obj.rect.x = obj.x * menu.renderer.getScale()


def transitionRight(obj, menu, animation):
    obj.x += transitionspeed * 100 * menu.game.dt

    if obj.x >= 100:
        obj.x = 100
        obj.animations.remove(animation)

    obj.rect.x = obj.x * menu.renderer.getScale()

def transitionRightBackground(obj, menu, animation):
    obj.x += transitionspeed * 100 * menu.game.dt

    if obj.x >= 0:
        obj.x = 0
        obj.animations.remove(animation)

    obj.rect.x = obj.x * menu.renderer.getScale()



#### Text hover animations ####
hoverspeed = 10

def hoverOverAnimation(obj, menu, animation):
    obj.x += hoverspeed * 10 * menu.game.dt

    if obj.x >= 110:
        obj.animations.remove(animation)
    obj.rect.x = obj.x * menu.renderer.getScale()


def hoverOutAnimation(obj, menu, animation):
    obj.x -= hoverspeed * 10 * menu.game.dt

    if obj.x <= 100:
        obj.animations.remove(animation)
    obj.rect.x = obj.x * menu.renderer.getScale()