#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <X11/X.h>
#include <X11/Xlib.h>
#include <X11/Xutil.h>
//Compile: gcc -shared -O3 -fPIC -Wl,-soname,linuxGrab -o linuxGrab.so linuxGrab.c -lX11

//-----------------------------------------------------------------------------

void getScreen(char *, unsigned char *, unsigned int *, unsigned int *);

void findMyWindow(Display *, Window *, Window *, char *);

//-----------------------------------------------------------------------------

static Window test;

void findMyWindow(Display *d, Window *w, Window *r, char * title) {
    // d; Display we want to use
    // w; Window we want to explore deeper. Maybe has our desired title?
    // r; Result window. What we want
    Window rw; // Root window returned
    Window pw; // Parent window returned
    Window *c; // Children list of w
    unsigned int num;

    if(XQueryTree(d, *w, &rw, &pw, &c, &num)) { // The call did not fail.
        if(num > 0){
            for(int i = 0; i < num; i++) {
                char * name;
                if(XFetchName(d, c[i], &name)){
                    if(strcmp(name, title) == 0){
                        *r = c[i];
                    }
                }
                Window * newSearch = &c[i];
                findMyWindow(d, newSearch, r, title);
            }
        }
    }
}

void getScreen(char * title, unsigned char * data, unsigned int *w, unsigned int *h ) // Information is written to data
{
    Display *display = XOpenDisplay(NULL);
    Window root = DefaultRootWindow(display);
    Window result; // Output of findMyWindow
    findMyWindow(display, &root, &result, title);

    Window testRoot;
    int x_val;
    int y_val;
    int width;
    int height;
    unsigned int border_width;
    unsigned int depth_return;
    XGetGeometry(display, result,
                 &testRoot, // Returns root window
                 &x_val, &y_val, // X and Y value
                 &width, &height, // Width and height
                 &border_width, // Border width
                 &depth_return); // Depth return

    *w = width;
    *h = height;

    printf("Width is %d, Height is %d\n", width, height);
    printf("Width is %d, Height is %d\n", *w, *h);

    XImage *image = XGetImage(display, result, x_val, y_val,
                              width, height, AllPlanes, ZPixmap);

    unsigned long red_mask   = image->red_mask;
    unsigned long green_mask = image->green_mask;
    unsigned long blue_mask  = image->blue_mask;

    int x, y;
    int ii = 0;
    for (y = 0; y < height; y++) {
        for (x = 0; x < width; x++) {
            unsigned long pixel = XGetPixel(image,x,y);
            unsigned char blue  = (pixel & blue_mask);
            unsigned char green = (pixel & green_mask) >> 8;
            unsigned char red   = (pixel & red_mask) >> 16;

            data[ii + 2] = blue;
            data[ii + 1] = green;
            data[ii + 0] = red;
            ii += 3;
        }
    }
}
