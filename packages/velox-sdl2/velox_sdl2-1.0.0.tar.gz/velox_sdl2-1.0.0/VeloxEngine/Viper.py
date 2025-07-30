import sdl2
import sdl2.ext
import ctypes
import os
from PIL import Image

class Surface:
    def __init__(self, texture, width, height):
        self.texture = texture
        self.width = width
        self.height = height
    def get_width(self):
        return self.width
    def get_height(self):
        return self.height

class Rect:
    def __init__(self, x, y, w, h):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
    def to_sdl_rect(self):
        return sdl2.SDL_Rect(self.x, self.y, self.w, self.h)
    def colliderect(self, other):
        return (self.x < other.x + other.w and
                self.x + self.w > other.x and
                self.y < other.y + other.h and
                self.y + self.h > other.y)

class Display:
    def __init__(self):
        self.window = None
        self.renderer = None
        self.width = 0
        self.height = 0
        self.running = False
        self.clear_color = sdl2.ext.Color(0,0,0)
    def set_mode(self, size):
        w, h = size
        self.width = w
        self.height = h
        if self.window:
            sdl2.SDL_DestroyRenderer(self.renderer)
            sdl2.SDL_DestroyWindow(self.window)
        self.window = sdl2.SDL_CreateWindow(b"Viper Engine", sdl2.SDL_WINDOWPOS_CENTERED, sdl2.SDL_WINDOWPOS_CENTERED, w, h, sdl2.SDL_WINDOW_SHOWN)
        self.renderer = sdl2.SDL_CreateRenderer(self.window, -1, sdl2.SDL_RENDERER_ACCELERATED | sdl2.SDL_RENDERER_PRESENTVSYNC)
        sdl2.SDL_SetRenderDrawBlendMode(self.renderer, sdl2.SDL_BLENDMODE_BLEND)
        self.running = True
        set_window_icon(self)
        return self
    def set_caption(self, title):
        if self.window:
            sdl2.SDL_SetWindowTitle(self.window, title.encode("utf-8"))
    def paint(self, color):
        r, g, b = color
        sdl2.SDL_SetRenderDrawColor(self.renderer, r, g, b, 255)
        sdl2.SDL_RenderClear(self.renderer)
    def update(self):
        sdl2.SDL_RenderPresent(self.renderer)
    def flash(self, surface, dest):
        if not isinstance(dest, Rect):
            dest = Rect(dest[0], dest[1], surface.get_width(), surface.get_height())
        sdl_rect = dest.to_sdl_rect()
        sdl2.SDL_RenderCopy(self.renderer, surface.texture, None, sdl_rect)
    def draw_rect(self, color, rect, width=0):
        r, g, b = color
        sdl2.SDL_SetRenderDrawColor(self.renderer, r, g, b, 255)
        sdl_rect = rect.to_sdl_rect()
        if width == 0:
            sdl2.SDL_RenderFillRect(self.renderer, sdl_rect)
        else:
            for i in range(width):
                rct = sdl2.SDL_Rect(rect.x+i, rect.y+i, rect.w-2*i, rect.h-2*i)
                sdl2.SDL_RenderDrawRect(self.renderer, rct)
    def draw_line(self, color, start_pos, end_pos):
        r, g, b = color
        sdl2.SDL_SetRenderDrawColor(self.renderer, r, g, b, 255)
        sdl2.SDL_RenderDrawLine(self.renderer, start_pos[0], start_pos[1], end_pos[0], end_pos[1])
    def draw_point(self, color, pos):
        r, g, b = color
        sdl2.SDL_SetRenderDrawColor(self.renderer, r, g, b, 255)
        sdl2.SDL_RenderDrawPoint(self.renderer, pos[0], pos[1])

def set_window_icon(display):
    path = os.path.join(os.path.dirname(__file__), "Viper.png")
    image = Image.open(path)
    image = image.convert("RGBA")
    w, h = image.size
    data = image.tobytes()
    surf = sdl2.SDL_CreateRGBSurfaceFrom(data, w, h, 32, w * 4, 0x000000FF, 0x0000FF00, 0x00FF0000, 0xFF000000)
    sdl2.SDL_SetWindowIcon(display.window, surf)
    sdl2.SDL_FreeSurface(surf)

def init():
    return sdl2.SDL_Init(sdl2.SDL_INIT_VIDEO | sdl2.SDL_INIT_AUDIO) == 0

def quit():
    sdl2.SDL_Quit()

def load_image(path, display):
    surface = sdl2.ext.load_image(path)
    texture = sdl2.SDL_CreateTextureFromSurface(display.renderer, surface)
    width = surface.contents.w
    height = surface.contents.h
    sdl2.SDL_FreeSurface(surface)
    return Surface(texture, width, height)

def poll_event():
    event = sdl2.SDL_Event()
    if sdl2.SDL_PollEvent(event):
        etype = event.type
        if etype == sdl2.SDL_QUIT:
            return {"type": "QUIT"}
        if etype == sdl2.SDL_KEYDOWN:
            return {"type": "KEYDOWN", "key": event.key.keysym.sym}
        if etype == sdl2.SDL_KEYUP:
            return {"type": "KEYUP", "key": event.key.keysym.sym}
        if etype == sdl2.SDL_MOUSEBUTTONDOWN:
            return {"type": "MOUSEBUTTONDOWN", "pos": (event.button.x, event.button.y), "button": event.button.button}
        if etype == sdl2.SDL_MOUSEBUTTONUP:
            return {"type": "MOUSEBUTTONUP", "pos": (event.button.x, event.button.y), "button": event.button.button}
        if etype == sdl2.SDL_MOUSEMOTION:
            return {"type": "MOUSEMOTION", "pos": (event.motion.x, event.motion.y), "rel": (event.motion.xrel, event.motion.yrel)}
    return None

class Clock:
    def __init__(self):
        self.last = sdl2.SDL_GetTicks()
    def tick(self, fps):
        now = sdl2.SDL_GetTicks()
        delay = int(1000/fps) - (now - self.last)
        if delay > 0:
            sdl2.SDL_Delay(delay)
        self.last = sdl2.SDL_GetTicks()

def key_get_pressed():
    sdl2.SDL_PumpEvents()
    numkeys = ctypes.c_int(0)
    keys = sdl2.SDL_GetKeyboardState(ctypes.byref(numkeys))
    pressed = set()
    for i in range(numkeys.value):
        if keys[i]:
            pressed.add(i)
    return pressed

K_ESCAPE = sdl2.SDLK_ESCAPE
K_RETURN = sdl2.SDLK_RETURN
K_SPACE = sdl2.SDLK_SPACE
K_BACKSPACE = sdl2.SDLK_BACKSPACE
K_TAB = sdl2.SDLK_TAB
K_CAPSLOCK = sdl2.SDLK_CAPSLOCK
K_LSHIFT = sdl2.SDLK_LSHIFT
K_RSHIFT = sdl2.SDLK_RSHIFT
K_LCTRL = sdl2.SDLK_LCTRL
K_RCTRL = sdl2.SDLK_RCTRL
K_LALT = sdl2.SDLK_LALT
K_RALT = sdl2.SDLK_RALT
K_UP = sdl2.SDLK_UP
K_DOWN = sdl2.SDLK_DOWN
K_LEFT = sdl2.SDLK_LEFT
K_RIGHT = sdl2.SDLK_RIGHT
K_0 = sdl2.SDLK_0
K_1 = sdl2.SDLK_1
K_2 = sdl2.SDLK_2
K_3 = sdl2.SDLK_3
K_4 = sdl2.SDLK_4
K_5 = sdl2.SDLK_5
K_6 = sdl2.SDLK_6
K_7 = sdl2.SDLK_7
K_8 = sdl2.SDLK_8
K_9 = sdl2.SDLK_9
K_a = sdl2.SDLK_a
K_b = sdl2.SDLK_b
K_c = sdl2.SDLK_c
K_d = sdl2.SDLK_d
K_e = sdl2.SDLK_e
K_f = sdl2.SDLK_f
K_g = sdl2.SDLK_g
K_h = sdl2.SDLK_h
K_i = sdl2.SDLK_i
K_j = sdl2.SDLK_j
K_k = sdl2.SDLK_k
K_l = sdl2.SDLK_l
K_m = sdl2.SDLK_m
K_n = sdl2.SDLK_n
K_o = sdl2.SDLK_o
K_p = sdl2.SDLK_p
K_q = sdl2.SDLK_q
K_r = sdl2.SDLK_r
K_s = sdl2.SDLK_s
K_t = sdl2.SDLK_t
K_u = sdl2.SDLK_u
K_v = sdl2.SDLK_v
K_w = sdl2.SDLK_w
K_x = sdl2.SDLK_x
K_y = sdl2.SDLK_y
K_z = sdl2.SDLK_z
K_F1 = sdl2.SDLK_F1
K_F2 = sdl2.SDLK_F2
K_F3 = sdl2.SDLK_F3
K_F4 = sdl2.SDLK_F4
K_F5 = sdl2.SDLK_F5
K_F6 = sdl2.SDLK_F6
K_F7 = sdl2.SDLK_F7
K_F8 = sdl2.SDLK_F8
K_F9 = sdl2.SDLK_F9
K_F10 = sdl2.SDLK_F10
K_F11 = sdl2.SDLK_F11
K_F12 = sdl2.SDLK_F12
K_PRINTSCREEN = sdl2.SDLK_PRINTSCREEN
K_SCROLLLOCK = sdl2.SDLK_SCROLLLOCK
K_PAUSE = sdl2.SDLK_PAUSE
K_INSERT = sdl2.SDLK_INSERT
K_HOME = sdl2.SDLK_HOME
K_PAGEUP = sdl2.SDLK_PAGEUP
K_DELETE = sdl2.SDLK_DELETE
K_END = sdl2.SDLK_END
K_PAGEDOWN = sdl2.SDLK_PAGEDOWN
K_NUMLOCKCLEAR = sdl2.SDLK_NUMLOCKCLEAR
K_KP_DIVIDE = sdl2.SDLK_KP_DIVIDE
K_KP_MULTIPLY = sdl2.SDLK_KP_MULTIPLY
K_KP_MINUS = sdl2.SDLK_KP_MINUS
K_KP_PLUS = sdl2.SDLK_KP_PLUS
K_KP_ENTER = sdl2.SDLK_KP_ENTER
K_KP_1 = sdl2.SDLK_KP_1
K_KP_2 = sdl2.SDLK_KP_2
K_KP_3 = sdl2.SDLK_KP_3
K_KP_4 = sdl2.SDLK_KP_4
K_KP_5 = sdl2.SDLK_KP_5
K_KP_6 = sdl2.SDLK_KP_6
K_KP_7 = sdl2.SDLK_KP_7
K_KP_8 = sdl2.SDLK_KP_8
K_KP_9 = sdl2.SDLK_KP_9
K_KP_0 = sdl2.SDLK_KP_0
K_KP_PERIOD = sdl2.SDLK_KP_PERIOD
