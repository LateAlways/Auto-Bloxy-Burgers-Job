import copy
import os

import numpy as np
import pyautogui
import cv2
import time
import ait as autoit
from pynput.keyboard import Key, Listener
from colorama import init, Fore
init()
cv = cv2
data = {
    'burger1': {
        'color': (0, 0, 255),
        'threshold': 0.97
    },
    'burger2': {
        'color': (0, 165, 255),
        'threshold': 0.983
    },
    'burger3': {
        'color': (0, 255, 255),
        'threshold': 0.86
    },
    'fries': {
        'color': (0, 255, 0),
        'threshold': 0.95
    },
    'drink': {
        'color': (255, 0, 0),
        'threshold': 0.88
    }
}

positions = {
    'burger1': (0, 0),
    'burger2': (0, 0),
    'burger3': (0, 0),
    'fries': (0, 0),
    'drink': (0, 0)
}


def get_order(screen):
    orderData = copy.deepcopy(data)
    for i in orderData:
        template = cv.imread(f'detections/orders/{i}.png')
        result = cv.matchTemplate(screen, template, cv.TM_CCORR_NORMED)
        imageInfo = cv.minMaxLoc(result)

        confidence = imageInfo[1]
        topLeft = imageInfo[3]
        bottomRight = topLeft[0] + template.shape[0], topLeft[1] + template.shape[1]

        orderData[i]['confidence'] = confidence
        orderData[i]['topLeft'] = topLeft
        orderData[i]['bottomRight'] = bottomRight

    order = []
    highest_burger = [0, 1]
    for i in orderData:
        if i.startswith('burger') and orderData[i]['confidence'] >= orderData[i]['threshold'] and orderData[i]["confidence"] > highest_burger[0]:
            highest_burger = [orderData[i]["confidence"], i]

    if highest_burger[0] != 0:
        order.append(highest_burger[1])
    for i in orderData:
        if orderData[i]['confidence'] >= orderData[i]['threshold'] and not i.startswith('burger'):
            order.append(i)

    return orderData, order


# SETUP
input("Hover Classic Burger (burger1) icon and press enter")
positions["burger1"] = pyautogui.position()
input("Hover Double Burger (burger2) icon and press enter")
positions["burger2"] = pyautogui.position()

input("Hover Deluxe Burger (burger3) icon and press enter")
positions["burger3"] = pyautogui.position()
input("Hover Bloxy Fries icon and press enter")
positions["fries"] = pyautogui.position()
input("Hover Bloxy Cola icon and press enter")
positions["drink"] = pyautogui.position()
input("Hover over the Done button and press enter")
done = pyautogui.position()
input("Hover start (top left) of order pane and press enter")
start_selection = pyautogui.position()
input("Hover end (bottom right) of order pane and press enter")
end_selection = pyautogui.position()

running = True


def on_press(key):
    global running
    if key == Key.esc:
        running = False


listener = Listener(on_press=on_press)
listener.start()

while running:
    os.system("cls")
    if pyautogui.pixel(start_selection.x, start_selection.y) != (255, 255, 255):
        continue

    print(Fore.RED+"Order Detected:")
    screenshot = np.array(pyautogui.screenshot(region=(start_selection.x, start_selection.y, end_selection.x - start_selection.x, end_selection.y - start_selection.y)))[:, :, ::-1]
    order = get_order(screenshot)
    print(order)
    for item in order[1]:
        print("    - " + item.replace("burger1", "Hamburger").replace("burger2", "Double Burger").replace("burger3", "Deluxe Burger").replace("fries", "Bloxy Fries").replace("drink", "Bloxy Cola"))

    for item in order[1]:
        autoit.move(*positions[item])
        autoit.move(positions[item][0]+1, positions[item][1]+1)
        autoit.click()
        time.sleep(0.05)

    autoit.move(*done)
    autoit.move(done.x+1,done.y+1)
    autoit.click()
    print(Fore.GREEN+"Completed!")
    while pyautogui.pixel(start_selection.x, start_selection.y) != (255, 255, 255) and running:
        pass
    time.sleep(2.5)

listener.stop()
listener.join()