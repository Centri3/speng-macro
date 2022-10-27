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
SELECTED_OBJECT_CODE = 0x19A8AB0
STAR_BROWSER_SYSTEMS_FOUND = 0x1022DC8
STAR_BROWSER_SEARCHING = 0x1048E31

# Pointers
SELECTED_OBJECT_POINTER = 0x19A8B30

# Pointers offsets
OBJECT_MASS = 0x11F8
OBJECT_EQUAT_RADIUS = 0x1CA4
OBJECT_AVG_TEMP = 0x1248
OBJECT_OBLATENESS = 0x120C
OBJECT_LIFE = 0x11BC
OBJECT_CLASS = 0x34
GALAXY_TYPE = 0x8
GALAXY_SIZE = 0x20

# Coordinates
STAR_BROWSER_COORDS = [0x1022D80, 0x1022D84]
SEARCH_BUTTON_COORDS = [0x1024728, 0x102472C]
CLEAR_BUTTON_COORDS = [0x1024A10, 0x1024A14]
FILTER_BUTTON_COORDS = [0x1028A98, 0x1028A9C]
FILTER_SORT_COORDS = [0x1026720, 0x1026724]

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

                select_milky_way = False

            octree_level = random.randint(1, 4)
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

                if selected_object_address > 2 ** 24:
                    break

            # If galaxy is E0 to E3 and galaxy is close enough to max size
            if int.from_bytes(handle.read_bytes(selected_object_address + 0x8, 1), 'little') in range(1, 4) and handle.read_float(selected_object_address + 0x20) >= 37500.0:
                with open("goto_selected.se", 'w') as file:
                    file.write("Goto { Time 0 Dist 10 }")

                time.sleep(0.1)

                os.startfile("goto_selected.se")
            else:
                continue

            select_milky_way = True

            for _ in range(0, 3):
                pyautogui.click(handle.read_float(handle.base_address + CLEAR_BUTTON_COORDS[0]) + COORDS_OFFSET,
                                handle.read_float(handle.base_address + CLEAR_BUTTON_COORDS[1]) + COORDS_OFFSET + WINDOWED_OFFSET)

                time.sleep(3.0 / 60.0)

            time.sleep(0.3)

            pyautogui.click(handle.read_float(handle.base_address + SEARCH_BUTTON_COORDS[0]) + COORDS_OFFSET,
                            handle.read_float(handle.base_address + SEARCH_BUTTON_COORDS[1]) + COORDS_OFFSET + WINDOWED_OFFSET)

            time.sleep(0.1)

            while not int.from_bytes(handle.read_bytes(handle.base_address + STAR_BROWSER_SEARCHING, 1), 'little'):
                if handle.read_int(
                        handle.base_address + STAR_BROWSER_SYSTEMS_FOUND) > 22:

                    pyautogui.click(handle.read_float(handle.base_address + CLEAR_BUTTON_COORDS[0]) + COORDS_OFFSET,
                                    handle.read_float(handle.base_address + CLEAR_BUTTON_COORDS[1]) + COORDS_OFFSET + WINDOWED_OFFSET)

                    time.sleep(0.1)

                    pyautogui.doubleClick(handle.read_float(handle.base_address + FILTER_BUTTON_COORDS[0]) + COORDS_OFFSET, handle.read_float(
                        handle.base_address + FILTER_BUTTON_COORDS[1]) + COORDS_OFFSET + WINDOWED_OFFSET)

            time.sleep(0.1)

            systems_found = handle.read_int(
                handle.base_address + STAR_BROWSER_SYSTEMS_FOUND)

            pyautogui.moveTo(handle.read_float(handle.base_address + FILTER_SORT_COORDS[0]) + COORDS_OFFSET,
                             handle.read_float(handle.base_address + FILTER_SORT_COORDS[1]) + FILTER_OFFSET + COORDS_OFFSET + WINDOWED_OFFSET + 1)

            for i in range(0, min(systems_found, 22)):
                pyautogui.moveRel(0, SYSTEMS_OFFSET)
                pyautogui.click()

                time.sleep(0.1)

                for i in range(0, 60):
                    selected_object_address = handle.read_longlong(
                        handle.base_address + SELECTED_OBJECT_POINTER)

                    if selected_object_address == 0:
                        continue
                    else: break

                print(selected_object_address)

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
                # Magic numbers
                elif (life == 1703936 or life == 1075445760) and object_class == 3:
                    with pyautogui.hold("ctrl"):
                        pyautogui.press("f12")

                pyautogui.press("h")


if __name__ == "__main__":
    main()
