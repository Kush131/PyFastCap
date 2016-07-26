import cv2
import platform
import numpy as np
import time  # Eventually take this out when timing isn't needed
from PIL import Image
if platform.system() == "Darwin":  # Mac OS X
    # Finding windows on Mac
    from Quartz import CGWindowListCopyWindowInfo as copyWindowInfo
    from Quartz import kCGWindowListExcludeDesktopElements as deskElements
    from Quartz import kCGNullWindowID as nullWindow
    # Screenshot properties
    from Quartz import CGWindowListCreateImage
    from Quartz import kCGWindowListOptionIncludingWindow, CGRectNull
    from Quartz import kCGWindowImageBoundsIgnoreFraming
    # Convert OSX to CV2
    from Quartz import CGDataProviderCopyData, CGImageGetDataProvider
    from Quartz import CGImageGetHeight, CGImageGetWidth
    from Quartz import CGImageGetBytesPerRow
else:
    import ctypes
    import os
    # Load fast screenshot library
    LibName = 'prtscn.so'
    AbsLibPath = os.path.dirname(os.path.abspath(__file__)) + \
        os.path.sep + LibName
    grab = ctypes.CDLL(AbsLibPath)

# -----------------------------------------------------------------------------
# End of Imports
# -----------------------------------------------------------------------------

"""
grab_frame(wid)

Grabs a frame from the Runescape window and returns it as a numpy array.
wid - Window id of application window Runescape is running on.

For linux screenshotting, you currently can pass the four window params
you want to capture from
x1 - Horizontal offset
y1 - Vertical offset
x2 - Width - x1
y2 - Height - y1
"""


def grab_frame(wid=None, x1=None, y1=None, x2=None, y2=None):
    if platform.system() == "Darwin":  # Mac OS X
        image_ref = CGWindowListCreateImage(CGRectNull,
                                            kCGWindowListOptionIncludingWindow,
                                            wid,
                                            kCGWindowImageBoundsIgnoreFraming)

        pixeldata = CGDataProviderCopyData(CGImageGetDataProvider(image_ref))

        height = CGImageGetHeight(image_ref)
        width = CGImageGetWidth(image_ref)
        stride = CGImageGetBytesPerRow(image_ref)

        image = Image.frombuffer("RGBA", (width, height),
                                 pixeldata, "raw", "RGBA", stride, 1)

        return np.array(image)
    else:  # Linux
        w, h = x1 + x2, y1 + y2
        size = w * h
        objlength = size * 3

        grab.getScreen.argtypes = []
        result = (ctypes.c_ubyte * objlength)()

        grab.getScreen(x1, y1, w, h, result)
        return Image.frombuffer('RGB', (w, h), result, 'raw', 'RGB', 0, 1)


"""
find_wid()
Finds the window id of the Runescape window and returns it.

TODO: Add linux support
"""


def find_wid(app):
    if platform.system() == "Darwin":  # Mac OS X
        return app.objectForKey_("kCGWindowNumber")


"""
find_window()
Finds the Runescape window and returns a pointer to its information.

TODO: Add linux support
"""


def find_window(window_name):
    if platform.system() == "Darwin":  # Mac OS X
        window_list = copyWindowInfo(deskElements, nullWindow)
        for application in window_list:
            if application.objectForKey_("kCGWindowName") == window_name:
                return application
    else:  # Linux
        pass

"""
resize_image()
Resizes an image with OpenCV. Don't use unless you know what you are doing.
"""


def resize_image(image):
    r = 500.0 / image.shape[1]
    dim = (500, int(image.shape[0] * r))
    return cv2.resize(image, dim, interpolation=cv2.INTER_AREA)

# Start main stuff

window_name = "OSBuddy Pro v2.15.9 - Stunt"
runescape_window = find_window(window_name)

while True:
    start = time.time()
    image = grab_frame(find_wid(runescape_window))
    cv2.imshow("RuneScape", resize_image(image))
    cv2.waitKey(1)
    print(time.time() - start)
