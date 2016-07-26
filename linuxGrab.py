from Xlib.display import Display
import time
import ctypes
import os
from PIL import Image

# Define ctypes
LibName = 'prtscn.so'
AbsLibPath = os.path.dirname(os.path.abspath(__file__)) + os.path.sep + LibName
grab = ctypes.CDLL(AbsLibPath)
# The root of the
root_window = Display().screen().root


def grab_screen(title):
    # Would really like to find a way to grab below without using protected members.
    w, h = root_window.get_geometry()._data['width'], root_window.get_geometry()._data['height']
    size = w * h  # Area of the window
    object_length = size * 3  # 3 color values needs * 3 the space.
    grab.getScreen.argtypes = []
    result = (ctypes.c_ubyte * object_length)()  # C will put our image in this array
    # Prepare a C string that is the title of our window.
    b = title.encode('utf8')
    t = ctypes.create_string_buffer(b)

    width = ctypes.c_int(-1)
    height = ctypes.c_int(-1)

    grab.getScreen(t, result, ctypes.byref(width), ctypes.byref(height))

    object_length = (width.value * height.value * 3)  # Application window size instead of full screen.

    resized_result = (object_length * ctypes.c_ubyte)  # New result array that is size of application window.
    resized_result = resized_result.from_address(ctypes.addressof(result))

    # print(Image.frombuffer('RGB', (w, h), result, 'raw', 'RGB', 0, 1))
    # print(Image.frombuffer('RGB', (width.value, height.value), resized_result, 'raw', 'RGB', 0, 1))

    return Image.frombuffer('RGB', (width.value, height.value), resized_result, 'raw', 'RGB', 0, 1)


start = time.time()
im = grab_screen("OSBuddy Pro - Stunt")
im.show()

print(time.time() - start)
