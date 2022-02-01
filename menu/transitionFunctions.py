from config import config


def transitionX(
        obj, menu, animation, speed, transitionDirection, x, callback,
        dirty=False):
    obj.x += speed * 100 * menu.game.dt

    if (transitionDirection == "left" and obj.x >= x) or (
            transitionDirection == "right" and obj.x < x):
        obj.removeAnimation(animation)
        callback(obj, menu, x)

    obj.rect.x = obj.x * menu.renderer.getScale()

    # For components that need to be redrawn (such as sliders)
    if dirty:
        obj.dirty = True


def transitionY(
        obj, menu, animation, speed, transitionDirection, y, callback,
        dirty=False):
    obj.y += speed * 100 * menu.game.dt

    if (transitionDirection == "down" and obj.y >= y) or (
            transitionDirection == "up" and obj.y < y):
        obj.removeAnimation(animation)
        callback(obj, menu, y)

    obj.rect.y = obj.y * menu.renderer.getScale()

    # For components that need to be redrawn (such as sliders)
    if dirty:
        obj.dirty = True


def transitionMessageDown(obj, menu, animation, speed, transitionDirection, y):
    # obj.y += speed * 100 * menu.game.dt
    obj.setPos((obj.x, obj.y + speed * 100 * menu.game.dt))

    if (transitionDirection == "down" and obj.y >= y) or (
            transitionDirection == "up" and obj.y < y):
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


# Text hover animations
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


def slideTransitionY(
        obj, menu, animation, speed, half, callback, transitionDirection='up'):
    obj.y += speed * 100 * menu.game.dt

    if transitionDirection == 'up':
        if (half == 'first' and obj.y <= 0) or (
                half == 'second' and obj.y + obj.height <= 0):
            callback(obj, menu, animation)

    else:
        if (half == 'first' and obj.y >= 0) or (
                half == 'second'
                and obj.y >= config["graphics"]["displayHeight"]):
            callback(obj, menu, animation)

    obj.rect.y = obj.y * menu.renderer.getScale()


def slideTransitionX(obj, menu, animation, speed, half, callback):
    obj.x += speed * 100 * menu.game.dt

    if (half == 'first' and obj.x >= 0) or (
            half == 'second' and obj.x >= config["graphics"]["displayWidth"]):
        obj.removeAnimation(animation)
        callback(obj, menu)

    obj.rect.x = obj.x * menu.renderer.getScale()


def increaseTimer(
        obj, menu, animation, speed, finish, direction="forwards",
        callback=None):
    obj.timer += speed * 100 * menu.game.dt * menu.game.spriteRenderer.getDt()

    if (obj.timer >= finish and direction == "forwards" or obj.timer <= finish
            and direction == "backwards"):
        obj.removeAnimation(animation)
        if callback is not None:
            callback(obj, menu)

    obj.dirty = True


# TODO: Put these into one function
def increaseKeys(obj, menu, animation, levelSelectButton, retryButton, x=1):
    if menu.game.audioLoader.getChannelBusy():
        return

    obj.timer += menu.game.dt

    if obj.timer > 0.2:
        obj.timer = 0
        total = int(obj.getText()) + 1
        obj.setText(str(total))
        obj.dirty = True

        # TODO: Fix this sound so it plays on each point given
        menu.game.audioLoader.playSound("success" + str(x), x)

        if total >= config["player"]["keys"]:
            obj.removeAnimation(animation)
            # Add the navigation buttons when the animation is complete
            menu.add(levelSelectButton)
            menu.add(retryButton)

        else:
            obj.removeAnimation(animation)
            obj.addAnimation(
                increaseKeys, 'onLoad', levelSelectButton=levelSelectButton,
                retryButton=retryButton, x=x + 1)


def decreaseKeys(obj, menu, animation):
    if menu.game.audioLoader.getChannelBusy():
        return

    obj.timer += menu.game.dt

    if obj.timer > 0.2:
        obj.timer = 0
        total = int(obj.getText()) - 1
        obj.setText("+" + str(total))
        obj.dirty = True

        if total <= 0:
            obj.removeAnimation(animation)


def increaseMeter(obj, menu, animation, fromAmount, toAmount):
    if menu.game.audioLoader.getChannelBusy():
        return

    obj.timer += menu.game.dt

    if obj.timer > 0.2:
        obj.timer = 0
        obj.setAmount(fromAmount + 1)
        obj.dirty = True

        if obj.getAmount() >= toAmount:
            obj.removeAnimation(animation)

        else:
            obj.removeAnimation(animation)
            obj.addAnimation(
                increaseMeter, 'onLoad', fromAmount=fromAmount + 1,
                toAmount=toAmount)
