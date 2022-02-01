from config import WHITE, BLACK
import transitionFunctions as tf


# hover over an object and set it to a specified color
def hoverColor(obj, menu, event, color=None):
    if color is not None:
        obj.setColor(color)


# hover over the object and add a hover animation
def hoverOver(obj, menu, event, speed=1, x=110, color=WHITE):
    if tf.hoverOverAnimation not in obj.getAnimations():
        obj.addAnimation(
            tf.hoverOverAnimation, 'onMouseOver', speed=speed, x=x)
    obj.setColor(color)


# remove the hover over animation on mouse out
def hoverOut(obj, menu, event, speed=1, x=100, color=BLACK):
    if tf.hoverOverAnimation in obj.getAnimations():
        obj.removeAnimation(tf.hoverOverAnimation)
    obj.addAnimation(tf.hoverOutAnimation, 'onMouseOut', speed=speed, x=x)
    obj.setColor(color)


def hoverImage(obj, menu, event, image=None):
    if image is not None:
        obj.setImageName(image)


# close and clear the menu
def clearMenu(obj, menu):
    menu.close()
    menu.main()


def defaultCallback(obj, menu, y):
    menu.game.paused = False
    menu.close()