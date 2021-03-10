import pygame 
from pygame.locals import *
from config import *

vec = pygame.math.Vector2

def transitionAnimationOpen(obj, menu, animation):
    obj.x += 100

    if obj.x >= 0:
        obj.removeAnimation(animation)
        menu.close()
        menu.transition()

    obj.rect.x = obj.x * menu.renderer.getScale()


def transitionAnimationClose(obj, menu, animation):
    obj.x += 100

    if obj.x >= config["graphics"]["displayWidth"]:
        obj.removeAnimation(animation)
        menu.close()

    obj.rect.x = obj.x * menu.renderer.getScale()


def transitionFadeIn(obj, menu, animation):
    obj.setAlpha(obj.getAlpha() + 20)
    obj.dirty = True

    if obj.getAlpha() >= 255:
        obj.removeAnimation(animation)
        menu.close()
        menu.transition()


def transitionFadeOut(obj, menu, animation):
    obj.setAlpha(obj.getAlpha() - 20)
    obj.dirty = True

    if obj.getAlpha() <= 0:
        obj.removeAnimation(animation)
        menu.close()




transitionspeed = 40


def transitionX(obj, menu, animation, speed, transitionDirection, x, callback):
    obj.x += speed * 100 * menu.game.dt

    if (transitionDirection == "left" and obj.x >= x) or (transitionDirection == "right" and obj.x < x):
        obj.removeAnimation(animation)
        callback(obj, menu, x)

    obj.rect.x = obj.x * menu.renderer.getScale()


def transitionY(obj, menu, animation, speed, transitionDirection, y, callback):
    obj.y += speed * 100 * menu.game.dt

    if (transitionDirection == "down" and obj.y >= y) or (transitionDirection == "up" and obj.y < y):
        obj.removeAnimation(animation)
        callback(obj, menu, y)

    obj.rect.y = obj.y * menu.renderer.getScale()


def transitionMessageDown(obj, menu, animation, speed, transitionDirection, y):
    # obj.y += speed * 100 * menu.game.dt
    obj.setPos((obj.x, obj.y + speed * 100 * menu.game.dt))

    if (transitionDirection == "down" and obj.y >= y) or (transitionDirection == "up" and obj.y < y):
        obj.removeAnimation(animation)
        obj.setPos((obj.x, y))

    # obj.rect.y = obj.y * menu.renderer.getScale()
    obj.setRectPos()

def transitionMessageRight(obj, menu, animation, speed, x):
    obj.setPos((obj.x + speed * 100 * menu.game.dt, obj.y))

    if obj.x >= x:
        obj.removeAnimation(animation)
        obj.remove()

    obj.setRectPos()

def transitionLeft(obj, menu, animation):
    obj.x -= transitionspeed * 100 * menu.game.dt

    if obj.x < -500:
        obj.removeAnimation(animation)
        menu.close()

    obj.rect.x = obj.x * menu.renderer.getScale()
    

def transitionLeftUnpause(obj, menu, animation):
    obj.x -= transitionspeed * 100 * menu.game.dt

    if obj.x < -500:
        obj.removeAnimation(animation)
        menu.close()
        menu.game.paused = False

    obj.rect.x = obj.x * menu.renderer.getScale()


def transitionRight(obj, menu, animation):
    obj.x += transitionspeed * 100 * menu.game.dt

    if obj.x >= 100:
        obj.x = 100
        obj.removeAnimation(animation)

    obj.rect.x = obj.x * menu.renderer.getScale()


def transitionRightBackground(obj, menu, animation):
    obj.x += transitionspeed * 100 * menu.game.dt

    if obj.x >= 0:
        obj.x = 0
        obj.removeAnimation(animation)

    obj.rect.x = obj.x * menu.renderer.getScale()



#### Text hover animations ####
hoverspeed = 10

def hoverOverAnimation(obj, menu, animation, speed, x):
    obj.x += speed * 100 * menu.game.dt

    if obj.x >= x:
        obj.removeAnimation(animation)
    obj.rect.x = obj.x * menu.renderer.getScale()


def hoverOutAnimation(obj, menu, animation, speed, x):
    obj.x -= speed * 100 * menu.game.dt

    if obj.x <= x:
        obj.removeAnimation(animation)
    obj.rect.x = obj.x * menu.renderer.getScale()


increaseSpeed = 5

def successAnimationUp(obj, menu, animation):
    obj.fontSize += increaseSpeed * 10 * menu.game.dt
    obj.y -= increaseSpeed * 10 * menu.game.dt

    #increase hight too so it stays put
    if obj.fontSize >= 35:
        obj.removeAnimation(animation)
        obj.addAnimation(successAnimationDown, 'onLoad')
    obj.dirty = True


def successAnimationDown(obj, menu, animation):
    obj.fontSize -= increaseSpeed * 10 * menu.game.dt
    obj.y += increaseSpeed * 10 * menu.game.dt


    if obj.fontSize <= 25:
        obj.removeAnimation(animation)
        obj.setColor(BLACK)
    obj.dirty = True





def slideTransitionY(obj, menu, animation, speed, half, callback, transitionDirection = 'up'):
    obj.y += speed * 100 * menu.game.dt

    if transitionDirection == 'up':
        if (half == 'first' and obj.y <= 0) or (half == 'second' and obj.y + obj.height <= 0):
            callback(obj, menu, animation)
    else:
        if (half == 'first' and obj.y >= 0) or (half == 'second' and obj.y >= config["graphics"]["displayHeight"]):
            callback(obj, menu, animation)

    obj.rect.y = obj.y * menu.renderer.getScale()


def slideTransitionX(obj, menu, animation, speed, half, callback):
    obj.x += speed * 100 * menu.game.dt

    if (half == 'first' and obj.x >= 0) or (half == 'second' and obj.x >= config["graphics"]["displayWidth"]):
        obj.removeAnimation(animation)
        callback(obj, menu)

    obj.rect.x = obj.x * menu.renderer.getScale()

