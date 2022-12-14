# Standard library
import math
import os
import random
import time

# 3rd-party modules
import keyboard
import pyautogui
import pymem
import pymem.exception

# Local modules
# ...

# Globals
paused = False

# Earth constants
EARTH_MASS = 5.9724e+24
EARTH_EQUAT_RADIUS = 6378.14
EARTH_MEAN_RADIUS = 6371.0
EARTH_DENSITY = 5.51363
EARTH_GRAVITY = 9.80665
EARTH_ESC_VEL = 11.1784
EARTH_AVG_TEMP = 288.0

# Addresses
SELECTED_OBJECT_CODE = 0x19A9EA0
STAR_BROWSER_SYSTEMS_FOUND = 0x1024178
STAR_BROWSER_SEARCHING = 0x104A1E1

# Pointers
SELECTED_OBJECT_POINTER = 0x19A9F20

# Pointers offsets
OBJECT_MASS = 0x11F8
OBJECT_EQUAT_RADIUS = 0x1CA4
OBJECT_AVG_TEMP = 0x1248
OBJECT_OBLATENESS = 0x120C
OBJECT_LIFE = 0x11BC
OBJECT_CLASS = 0x34
OBJECT_ATM_PRESSURE = 0x17D8
GALAXY_TYPE = 0x8
GALAXY_SIZE = 0x20

# Coordinates
STAR_BROWSER_COORDS = [0x1023D60, 0x1023D64]
SEARCH_BUTTON_COORDS = [0x1025AD8, 0x1025ADC]
CLEAR_BUTTON_COORDS = [0x1025DC0, 0x1025DC4]
FILTER_BUTTON_COORDS = [0x1029E48, 0x1029E4C]
FILTER_SORT_COORDS = [0x1027AD0, 0x1027AD4]

# Coordinates offsets
COORDS_OFFSET = 0xA
FILTER_OFFSET = 0x6
SYSTEMS_OFFSET = 0x19
WINDOWED_OFFSET = 0x14


def toggle_execution():
    global paused

    paused = not paused


def main():
    keyboard.add_hotkey("shift+p", toggle_execution)

    # Open a handle to SE
    handle = pymem.Pymem("SpaceEngine.exe")

    # Look I'm really tired and don't feel like rewriting parts of my code to make it not spaghetti ok??? This works fine for now
    select_milky_way = True

    while True:
        if not paused:
            if select_milky_way:
                with open("select_rg_397.se", 'w') as file:
                    file.write("Select \"RG 0-3-397-1581\"")

                os.startfile("select_rg_397.se")

                time.sleep(1.0)

                select_milky_way = False

            octree_level = random.randint(1, 7)
            octree_block = random.randint(0, 8 ** octree_level)
            number = random.randint(0, 2500)

            handle.write_int(handle.base_address +
                             SELECTED_OBJECT_CODE + 0x0, 0)
            handle.write_int(handle.base_address +
                             SELECTED_OBJECT_CODE + 0x4, octree_level)
            handle.write_int(handle.base_address +
                             SELECTED_OBJECT_CODE + 0x8, octree_block)
            handle.write_int(handle.base_address +
                             SELECTED_OBJECT_CODE + 0x10, number)

            time.sleep(1.0 / 60.0)

            # Either my code is too fast, or the object doesn't exist. Either way, skip
            if not handle.read_longlong(handle.base_address + SELECTED_OBJECT_POINTER):
                continue

            for i in range(0, 60):
                selected_object_address = handle.read_longlong(
                    handle.base_address + SELECTED_OBJECT_POINTER)

                if selected_object_address == 0:
                    continue
                else:
                    break

            if selected_object_address == 0:
                continue

            with open("goto_selected.se", 'w') as file:
                file.write("Goto { Time 0 Dist 10 }")

            time.sleep(0.1)

            os.startfile("goto_selected.se")

            select_milky_way = True

            for _ in range(0, 3):
                pyautogui.click(handle.read_float(handle.base_address + CLEAR_BUTTON_COORDS[0]) + COORDS_OFFSET,
                                handle.read_float(handle.base_address + CLEAR_BUTTON_COORDS[1]) + COORDS_OFFSET + WINDOWED_OFFSET)

                time.sleep(3.0 / 60.0)

            time.sleep(0.3)

            pyautogui.click(handle.read_float(handle.base_address + SEARCH_BUTTON_COORDS[0]) + COORDS_OFFSET,
                            handle.read_float(handle.base_address + SEARCH_BUTTON_COORDS[1]) + COORDS_OFFSET + WINDOWED_OFFSET)

            time.sleep(0.1)

            for i in range(0, 180):
                if not int.from_bytes(handle.read_bytes(handle.base_address + STAR_BROWSER_SEARCHING, 1), 'little'):
                    if handle.read_int(
                         handle.base_address + STAR_BROWSER_SYSTEMS_FOUND) > 22:

                        pyautogui.click(handle.read_float(handle.base_address + CLEAR_BUTTON_COORDS[0]) + COORDS_OFFSET,
                                handle.read_float(handle.base_address + CLEAR_BUTTON_COORDS[1]) + COORDS_OFFSET + WINDOWED_OFFSET)

                        time.sleep(0.1)

                        pyautogui.doubleClick(handle.read_float(handle.base_address + FILTER_BUTTON_COORDS[0]) + COORDS_OFFSET, handle.read_float(
                            handle.base_address + FILTER_BUTTON_COORDS[1]) + COORDS_OFFSET + WINDOWED_OFFSET)

                        break

                    time.sleep(1.0)

                    continue
                else:
                    break

            time.sleep(0.1)

            systems_found = handle.read_int(
                handle.base_address + STAR_BROWSER_SYSTEMS_FOUND)

            pyautogui.moveTo(handle.read_float(handle.base_address + FILTER_SORT_COORDS[0]) + COORDS_OFFSET,
                             handle.read_float(handle.base_address + FILTER_SORT_COORDS[1]) + FILTER_OFFSET + COORDS_OFFSET + WINDOWED_OFFSET + 1)

            for i in range(0, min(systems_found, 22)):
                pyautogui.moveRel(0, SYSTEMS_OFFSET)
                pyautogui.click()

                time.sleep(0.05)

                pyautogui.click()

                time.sleep(0.05)

                for i in range(0, 60):
                    selected_object_address = handle.read_longlong(
                        handle.base_address + SELECTED_OBJECT_POINTER)

                    if selected_object_address == 0:
                        continue
                    else:
                        break

                if selected_object_address == 0:
                    continue

                mass = handle.read_float(
                    selected_object_address + OBJECT_MASS) * EARTH_MASS
                equat_radius = handle.read_float(
                    selected_object_address + OBJECT_EQUAT_RADIUS)
                avg_temp = handle.read_float(
                    selected_object_address + OBJECT_AVG_TEMP)
                oblateness = handle.read_float(
                    selected_object_address + OBJECT_OBLATENESS)
                life = handle.read_int(
                    selected_object_address + OBJECT_LIFE)
                object_class = handle.read_int(selected_object_address + OBJECT_CLASS)
                atm_pressure = handle.read_float(selected_object_address + OBJECT_ATM_PRESSURE)

                polar_radius = equat_radius * (1.0 - oblateness)
                mean_radius = ((equat_radius ** 2.0)
                               * polar_radius) ** 0.3333333333333333333333333333333333
                gravity = (mass / EARTH_MASS) / (mean_radius /
                                                 EARTH_MEAN_RADIUS) ** 2.0 * EARTH_GRAVITY

                density = mass * 1.0e-12 / \
                    (4.0 / 3.0 * math.pi * mean_radius ** 3)
                esc_vel = math.sqrt(
                    2.0 * gravity * equat_radius * 1000.0) * 0.001

                n = 1.0 / 4.0

                # autopep8 failed me
                esi = math.pow(1.0 - math.fabs((equat_radius - EARTH_EQUAT_RADIUS) / (equat_radius + EARTH_EQUAT_RADIUS)), 0.57 * n) * math.pow(1.0 - math.fabs((density - EARTH_DENSITY) / (density + EARTH_DENSITY)),
                                                                                                                                                1.07 * n) * math.pow(1.0 - math.fabs((esc_vel - EARTH_ESC_VEL) / (esc_vel + EARTH_ESC_VEL)), 0.70 * n) * math.pow(1.0 - math.fabs((avg_temp - EARTH_AVG_TEMP) / (avg_temp + EARTH_AVG_TEMP)), 5.58 * n)

                if esi > 0.9975:
                    with pyautogui.hold("ctrl"):
                        pyautogui.press("f12")
                elif esi > 0.9875 and atm_pressure > 1000.0:
                    with pyautogui.hold("ctrl"):
                        pyautogui.press("f12")
                elif 0.999995 < mass and mass < 1.00005 and 6370.97 < equat_radius and equat_radius < 6371.31:
                    with pyautogui.hold("ctrl"):
                        pyautogui.press("f12")
                # Magic numbers
                elif (life == 1703936 or life == 1075445760) and object_class == 3:
                    with pyautogui.hold("ctrl"):
                        pyautogui.press("f12")

                pyautogui.keyDown("h")

                time.sleep(0.1)

                pyautogui.keyUp("h")

if __name__ == "__main__":
    main()
