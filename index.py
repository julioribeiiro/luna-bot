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


def scrollHeroesPage(direction):
    if clickBtn(images['warrior-title'], timeout=10):
        py.moveRel(0, 100)
        if direction == 'up':
            py.scroll(100)
        else:
            py.scroll(-100)


def chooseBossAndRemoveHeroes():
    # detect if have to choose new boss
    logger('Deselecting heroes')
    if findImage(images['boss-hunt-choose-boss-page'], timeout=10):
        logger('Choosing new boss to fight')
        clickBtn(images['choose-new-boss-to-fight'], timeout=30)
        time.sleep(5)

    # expand heroes page
    clickBtn(images['arrow-right'], timeout=10)

    # detect if already has heroes selected and disselect them
    # first scroll to bottom
    scrollHeroesPage('down')
    if findImage(images['selected-for-battle-mark'], timeout=10):
        for _ in range(3):
            clickBtn(images['selected-for-battle-mark'])
            time.sleep(2)
    # after that scroll to top and search again
    scrollHeroesPage('up')
    if findImage(images['selected-for-battle-mark'], timeout=10):
        for _ in range(3):
            clickBtn(images['selected-for-battle-mark'])
            time.sleep(2)


def battleWithTeam(team):
    time.sleep(3)
    clickBtn(images['vs-title'], timeout=40)
    time.sleep(60)

    if clickBtn(images['defeat-title'], timeout=60):
        logger('Battle ended with defeat, going back to heroes screen')
        return
    else:
        logger('Battle ended with victory, going back to heroes screen')
        clickBtn(images['tap-to-open-btn'], timeout=10)
        time.sleep(5)
        clickBtn(images['victory-title'], timeout=10)
        return


def chooseHeroesToBattle():
    choosenHeroes = 0

    # expand heroes page
    clickBtn(images['arrow-right'], timeout=10, threshold=0.8)

    for i in range(5):
        for j in range(3):
            if i == 4:
                scrollHeroesPage('down')
            else:
                scrollHeroesPage('up')
            if clickBtn(images[f'team-{str(i+1)}-{str(j+1)}'], threshold=0.95):
                choosenHeroes += 1
            time.sleep(3)
        if choosenHeroes == 3:
            logger(f'Starting battle with team {i}')
            clickBtn(images['boss-hunt-btn'], timeout=10)
            if clickBtn(images['notice-title'], timeout=10):
                clickBtn(images['x-close-notice'])
            else:
                battleWithTeam(i)
        time.sleep(5)
        chooseBossAndRemoveHeroes()
        choosenHeroes = 0
        time.sleep(5)


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
        "send_heroes_to_battle": 0,
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

        if now - last['send_heroes_to_battle'] > addRandomness(t['send_to_battle'] * 60):
            last['send_heroes_to_battle'] = now
            chooseBossAndRemoveHeroes()
            chooseHeroesToBattle()

        logger(None, progress_indicator=True)

        sys.stdout.flush()

        time.sleep(1)


if __name__ == '__main__':
    main()
