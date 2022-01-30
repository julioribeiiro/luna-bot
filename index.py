from socket import timeout
from src.logger import logger
import pyautogui as py
import yaml
from os import listdir
from cv2 import cv2
import mss
import numpy as np
import time
import sys
from random import randint
from random import random

stream = open("config.yaml", 'r')
c = yaml.safe_load(stream)
ct = c['threshold']
ch = c['home']
pause = c['time_intervals']['interval_between_moviments']
py.PAUSE = pause

cat = """
                                                _
                                                \`*-.
                                                 )  _`-.
                                                .  : `. .
                                                : _   '  \\
                                                ; *` _.   `*-._
                                                `-.-'          `-.
                                                  ;       `       `.
                                                  :.       .        \\
                                                  . \  .   :   .-'   .
                                                  '  `+.;  ;  '      :
                                                  :  '  |    ;       ;-.
                                                  ; '   : :`-:     _.`* ;
                                               .*' /  .*' ; .*`- +'  `*'
                                               `*-*   `*-*  `*-*'
=========================================================================
========== 💰 Have I helped you in any way? All I ask is a tip! 💰 ======
========== ✨ Faça sua boa ação de hoje, manda aquela gorjeta! 😊 =======
=========================================================================
======================== vvv BCOIN BUSD BNB vvv =========================
============== 0xbd06182D8360FB7AC1B05e871e56c76372510dDf ===============
=========================================================================
===== https://www.paypal.com/donate?hosted_button_id=JVYSC6ZYCNQQQ ======
=========================================================================

>>---> Press ctrl + c to kill the bot.

>>---> Some configs can be found in the config.yaml file."""


def printScreen():
    with mss.mss() as sct:
        monitor = sct.monitors[0]
        sct_img = np.array(sct.grab(monitor))
        # The screen part to capture
        # monitor = {"top": 160, "left": 160, "width": 1000, "height": 135}

        # Grab the data
        return sct_img[:, :, :3]


def positions(target, threshold=ct['default'], img=None):
    if img is None:
        img = printScreen()
    result = cv2.matchTemplate(img, target, cv2.TM_CCOEFF_NORMED)
    w = target.shape[1]
    h = target.shape[0]

    yloc, xloc = np.where(result >= threshold)

    rectangles = []
    for (x, y) in zip(xloc, yloc):
        rectangles.append([int(x), int(y), int(w), int(h)])
        rectangles.append([int(x), int(y), int(w), int(h)])

    rectangles, weights = cv2.groupRectangles(rectangles, 1, 0.2)
    return rectangles


def clickBtn(img, timeout=3, threshold=ct['default']):
    """Search for img in the scree, if found moves the cursor over it and clicks.
    Parameters:
        img: The image that will be used as an template to find where to click.
        timeout (int): Time in seconds that it will keep looking for the img before returning with fail
        threshold(float): How confident the bot needs to be to click the buttons (values from 0 to 1)
    """

    start = time.time()
    has_timed_out = False
    while(not has_timed_out):
        matches = positions(img, threshold=threshold)

        if(len(matches) == 0):
            has_timed_out = time.time()-start > timeout
            continue

        x, y, w, h = matches[0]
        pos_click_x = x+w/2
        pos_click_y = y+h/2
        moveToWithRandomness(pos_click_x, pos_click_y, 1)
        py.click()
        return True

    return False


def findImage(img, timeout=3, threshold=ct['default']):
    start = time.time()
    has_timed_out = False
    while(not has_timed_out):
        matches = positions(img, threshold=threshold)

        if(len(matches) == 0):
            has_timed_out = time.time()-start > timeout
            continue

        return True

    return False


def addRandomness(n, randomn_factor_size=None):
    """Returns n with randomness
    Parameters:
        n (int): A decimal integer
        randomn_factor_size (int): The maximum value+- of randomness that will be
            added to n

    Returns:
        int: n with randomness
    """

    if randomn_factor_size is None:
        randomness_percentage = 0.1
        randomn_factor_size = randomness_percentage * n

    random_factor = 2 * random() * randomn_factor_size
    if random_factor > 5:
        random_factor = 5
    without_average_random_factor = n - randomn_factor_size
    randomized_n = int(without_average_random_factor + random_factor)
    # logger('{} with randomness -> {}'.format(int(n), randomized_n))
    return int(randomized_n)


def moveToWithRandomness(x, y, t):
    py.moveTo(addRandomness(x, 10), addRandomness(y, 10), t+random()/2)


def remove_suffix(input_string, suffix):
    """Returns the input_string without the suffix"""

    if suffix and input_string.endswith(suffix):
        return input_string[:-len(suffix)]
    return input_string


def load_images(dir_path='./targets/'):
    """ Programatically loads all images of dir_path as a key:value where the
        key is the file name without the .png suffix

    Returns:
        dict: dictionary containing the loaded images as key:value pairs.
    """

    file_names = listdir(dir_path)
    targets = {}
    for file in file_names:
        path = 'targets/' + file
        targets[remove_suffix(file, '.png')] = cv2.imread(path)

    return targets


def login():
    global login_attempts
    logger('😿 Checking if game has disconnected')

    if clickBtn(images['ok-error-btn'], timeout=5):
        print('Game disconnected, wait screen loads again')
        py.hotkey('ctrl', 'f5')
        time.sleep(60)

    if login_attempts > 3:
        logger('🔃 Too many login attempts, refreshing')
        login_attempts = 0
        py.hotkey('ctrl', 'f5')
        last['login'] = 0
        return

    if clickBtn(images['login-with-metamask'], timeout=10):
        logger('🎉 Connect wallet button detected, logging in!')
        login_attempts += 1
        if clickBtn(images['sign-in-btn'], timeout=60):
            login_attempts = login_attempts + 1
            time.sleep(5)
            if clickBtn(images['boss-hunt-main-page'], timeout=60):
                login_attempts = 0
                return

    if clickBtn(images['ok-error-btn'], timeout=10):
        logger('❌ Login failed! Trying again')
        login_attempts += 1
        last['login'] = 0
        pass


def sendHeroesToFight():
    if findImage(images['boss-hunt-choose-boss-page'], timeout=10):
        clickBtn(images['select-boss-green-area'], timeout=30)
        time.sleep(5)

# def sendSpaceshipToWork():
#     # filtra por descending ammo
#     hasAllships = False
#     scrollDown = 0
#     logger('Sending 15 ships to work')

#     # verifica se ja tem 15 naves para batalhar
#     if findImage(images['15-ships'], timeout=10, threshold=0.9):
#         hasAllships = True

#     if not hasAllships:
#         clickBtn(images['newest-btn'], timeout=3)
#         #clickBtn(images['descending-ammo'], timeout=10)
#         for _ in range(3):
#             py.press('down')
#         py.press('enter')
#         for _ in range(20):
#             if scrollDown < 3:
#                 if not clickBtn(images['fight-ship-btn'], timeout=5, threshold=0.97):
#                     clickBtn(images['fight-ship-btn-deactivated'],
#                              timeout=5, threshold=0.97)
#                     py.scroll(-80)
#                     scrollDown += 1
#     py.scroll(240)

#     # verifica se ja tem 15 naves para batalhar
#     if findImage(images['15-ships'], timeout=10, threshold=0.9):
#         hasAllships = True

#     # se tiver as 15 naves se inicia a batalha
#     if hasAllships:
#         if clickBtn(images['fight-boss-btn'], timeout=5):
#             logger('🚀 Started fighting boss')
#             clickBtn(images['confirm-lose-btn'], timeout=15)

#     else:
#         logger('There isn`t 15 ships available, trying again in 10 minutes')
#         for _ in range(20):
#             clickBtn(images['remove-ship-btn'], timeout=5, threshold=1)


# def checkFightingBoss():
#     logger('⚔ In battle')
#     time.sleep(5)
#     global bosses_killed
#     global last
#     global last_update_bosses_killed
#     t = c['time_intervals']

#     while (1):
#         now = time.time()
#         # Check if won battle and continues
#         if findImage(images['reward-label'], timeout=2):
#             clickBtn(images['confirm-lose-btn'], timeout=2)

#         # Check if won battle and continues
#         if findImage(images['reward-label'], timeout=2):
#             clickBtn(images['confirm-lose-btn'], timeout=2)
#             bosses_killed += 1

#         # # Check if is in level 9
#         if findImage(images['final-boss'], timeout=2, threshold=1):
#             logger('Final fevel reached, reseting to level 1')
#             clickBtn(images['surrender-btn'], timeout=10)
#             clickBtn(images['surrender-confirm-btn'], timeout=10)

#         # Check if won battle and continues
#         if findImage(images['reward-label'], timeout=2):
#             clickBtn(images['confirm-lose-btn'], timeout=2)
#             bosses_killed += 1

#         # Check if already loss
#         if findImage(images['lose-img'], timeout=2):
#             logger('Battle ended, reloading page')
#             py.hotkey('ctrl', 'f5')
#             last['login'] = 0
#             last['spaceships'] = 0
#             time.sleep(15)
#             break

#         # Check if won battle and continues
#         if findImage(images['reward-label'], timeout=2):
#             clickBtn(images['confirm-lose-btn'], timeout=2)
#             bosses_killed += 1

#         # Check if has no spaceships anymore
#         if findImage(images['0-spaceships-img'], timeout=2, threshold=0.9):
#             logger('Battle ended, no spaceships anymore, reloading page')
#             py.hotkey('ctrl', 'f5')
#             last['login'] = 0
#             last['spaceships'] = 0
#             time.sleep(15)
#             break

#         # Check if won battle and continues
#         if findImage(images['reward-label'], timeout=2):
#             clickBtn(images['confirm-lose-btn'], timeout=2)
#             bosses_killed += 1

#         # # Check if is in final level
#         if findImage(images['final-boss'], timeout=2, threshold=1):
#             logger('Final level reached, reseting to level 1')
#             clickBtn(images['surrender-btn'], timeout=10)
#             clickBtn(images['surrender-confirm-btn'], timeout=10)

#         # Check idle error in combat screen
#         if now - last["check_idle"] > addRandomness(t['check_idle_in_spaceships_screen'] * 60):
#             last["check_idle"] = now
#             if last_update_bosses_killed == bosses_killed:
#                 logger('Idle error identified, refreshing page')
#                 py.hotkey('ctrl', 'f5')
#                 break
#             logger(
#                 f'Checking idle error, bosses killed: {bosses_killed}, last count: {last_update_bosses_killed}')
#             last_update_bosses_killed = bosses_killed


def main():
    global login_attempts
    global images
    login_attempts = 0
    images = load_images()
    global last
    global bosses_killed
    global last_update_bosses_killed

    print('\n')

    print(cat)
    time.sleep(7)
    t = c['time_intervals']

    last = {
        "login": 0,
        "sendHeroesToBattle": 0,
        "in_battle": 0,
        "check_idle": 0
    }
    bosses_killed = 0
    last_update_bosses_killed = -1
    # =========

    while True:
        now = time.time()

        if now - last["login"] > addRandomness(t['check_for_login'] * 60):
            sys.stdout.flush()
            last["login"] = now
            login()

        if now - last['send_heroes_to_battle'] > addRandomness(t['send_to_battle']):
            last['send_heroes_to_battle'] = now
            sendHeroesToFight()

        # if now - last["spaceships"] > addRandomness(t['send_spaceships_for_work'] * 60):
        #     last["spaceships"] = now
        #     sendSpaceshipToWork()

        # if now - last["in_battle"] > addRandomness(t['check_spaceships_in_battle'] * 60):
        #     last["in_battle"] = now
        #     checkFightingBoss()

        # if now - last["check_idle"] > addRandomness(t['check_idle_in_spaceships_screen'] * 60):
        #     last["check_idle"] = now
        #     if last_update_bosses_killed == bosses_killed:
        #         py.hotkey('ctrl', 'f5')
        #     last_update_bosses_killed = bosses_killed

        logger(None, progress_indicator=True)

        sys.stdout.flush()

        time.sleep(1)


if __name__ == '__main__':
    main()
