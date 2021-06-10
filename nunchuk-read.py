import smbus
import time
import sys
import argparse


NUNCHUK_I2C_ADDR = 0x52
JOYSTICK_X = 0x00
JOYSTICK_Y = 0x01
ACCEL_X = 0x02
ACCEL_Y = 0x03
ACCEL_Z = 0x04
BUTTONS_ACCEL = 0x05


def nunchuk_read_once(i2c, round_accel):
    data_all = i2c.read_i2c_block_data(NUNCHUK_I2C_ADDR, 0x00, 6)

    # joystick
    joystick_x = data_all[JOYSTICK_X]
    joystick_y = data_all[JOYSTICK_Y]

    buttons_accel = data_all[BUTTONS_ACCEL]
    # accelerometer
    if round_accel:  # we want 8-bit instead of 10-bit values
        accel_x = data_all[ACCEL_X]
        accel_y = data_all[ACCEL_Y]
        accel_z = data_all[ACCEL_Z]
    else:
        accel_x = (((buttons_accel & 0b11000000) >> 6) | data_all[ACCEL_X] << 2)
        accel_y = (((buttons_accel & 0b00110000) >> 4) | data_all[ACCEL_Y] << 2)
        accel_z = (((buttons_accel & 0b00001100) >> 2) | data_all[ACCEL_Z] << 2)
    # buttons
    button_c = 1 - ((buttons_accel & 0b00000010) >> 1)  # inverted by default
    button_z = 1 - (buttons_accel & 0b00000001)

    # print
    print("joystick X (0-255): {}".format(str(joystick_x).zfill(3)))
    print("joystick Y (0-255): {}".format(str(joystick_y).zfill(3)))
    if round_accel:
        print("accel X (0-255):    {}".format(str(accel_x).zfill(3)))
        print("accel Y (0-255):    {}".format(str(accel_y).zfill(3)))
        print("accel Z (0-255):    {}".format(str(accel_z).zfill(3)))
    else:
        print("accel X (0-1023):   {}".format(str(accel_x).zfill(4)))
        print("accel Y (0-1023):   {}".format(str(accel_y).zfill(4)))
        print("accel Z (0-1023):   {}".format(str(accel_z).zfill(4)))
    print("button C (0-1):     {}".format(button_c))
    print("button Z (0-1):     {}".format(button_z))
    # reset line
    print("\033[A\033[A\033[A\033[A\033[A\033[A\033[A\033[A\033[A")


def nunchuk_set_encryption(i2c):
    # disable encryption for easier parsing
    i2c.write_i2c_block_data(NUNCHUK_I2C_ADDR, 0xF0, [0x55])
    i2c.write_i2c_block_data(NUNCHUK_I2C_ADDR, 0xFB, [0x00])
    return


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Read values from a Wii Nunchuk controller")
    parser.add_argument('--i2c', '-i', type=int, help='I2C bus. Default is 1', default=1)
    parser.add_argument('--delay', '-d', type=float, help='Delay between readings, in seconds. Default is 0.01 (<0.005 usually results in an error)', default=0.01)
    parser.add_argument('--round-accel', '-r', action='store_true', help='Set accelerometer values to be 8-bit instead of 10-bit. Default is False')
    args = parser.parse_args()

    print("Got i2c={}, delay={}s, round-accel={}".format(args.i2c, args.delay, args.round_accel))
    i2c = smbus.SMBus(args.i2c)
    nunchuk_set_encryption(i2c)

    print("Starting loop. Terminate with Ctrl+C\n")
    try:
        while True:
            nunchuk_read_once(i2c, args.round_accel)
            print("")
            time.sleep(args.delay)
    except KeyboardInterrupt:
        print(7*'\n')  # skip past read info
        print("KeyboardInterrupt detected")

    print("Finished")
    i2c.close()
    sys.exit(0)
