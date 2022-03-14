import board
import digitalio

button = digitalio.DigitalInOut(board.D26)
button.direction = digitalio.Direction.INPUT
button.pull = digitalio.Pull.DOWN


def get_button_value():
    return button.value
