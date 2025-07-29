import os
import sdl2
import sdl2.ext
import time

QUIT = sdl2.SDL_QUIT

K_w = sdl2.SDLK_w
K_a = sdl2.SDLK_a
K_s = sdl2.SDLK_s
K_d = sdl2.SDLK_d
K_UP = sdl2.SDLK_UP
K_DOWN = sdl2.SDLK_DOWN
K_LEFT = sdl2.SDLK_LEFT
K_RIGHT = sdl2.SDLK_RIGHT
K_ESCAPE = sdl2.SDLK_ESCAPE

class Rect:
    def __init__(self, x, y, w, h):
        self.x, self.y, self.w, self.h = x, y, w, h

    def move_ip(self, dx, dy):
        self.x += dx
        self.y += dy

    def colliderect(self, other):
        return not (self.x + self.w <= other.x or
                    self.x >= other.x + other.w or
                    self.y + self.h <= other.y or
                    self.y >= other.y + other.h)

    def copy(self):
        return Rect(self.x, self.y, self.w, self.h)

class Surface:
    def __init__(self, width, height, renderer=None):
        self.width = width
        self.height = height
        self.renderer = renderer
        self.color = sdl2.ext.Color(0, 0, 0)
        self.rect = Rect(0, 0, width, height)

    def paint(self, color):
        self.color = sdl2.ext.Color(*color)
        if self.renderer:
            sdl2.SDL_SetRenderDrawColor(self.renderer, *color, 255)
            sdl2.SDL_RenderClear(self.renderer)

    def flash(self, source, pos):
        if not self.renderer:
            raise RuntimeError("No renderer set for target surface")
        x, y = pos
        rect = sdl2.SDL_Rect(x, y, source.width, source.height)
        sdl2.SDL_SetRenderDrawColor(self.renderer,
                                   source.color.r,
                                   source.color.g,
                                   source.color.b,
                                   255)
        sdl2.SDL_RenderFillRect(self.renderer, rect)

class Display:
    def __init__(self):
        self.window = None
        self.renderer = None
        self.surface = None
        self.key_state = {}

    def set_mode(self, size):
        sdl2.SDL_Init(sdl2.SDL_INIT_VIDEO | sdl2.SDL_INIT_EVENTS)
        width, height = size
        self.window = sdl2.SDL_CreateWindow(b"Velox SDL2",
                                            sdl2.SDL_WINDOWPOS_CENTERED,
                                            sdl2.SDL_WINDOWPOS_CENTERED,
                                            width, height,
                                            sdl2.SDL_WINDOW_SHOWN)
        if not self.window:
            raise Exception("Could not create SDL2 window")
        icon_path = os.path.join(os.path.dirname(__file__), "velox_icon.png")
        if os.path.exists(icon_path):
            icon_surface = sdl2.ext.load_image(icon_path)
            if icon_surface:
                sdl2.SDL_SetWindowIcon(self.window, icon_surface)
        self.renderer = sdl2.SDL_CreateRenderer(self.window, -1, sdl2.SDL_RENDERER_ACCELERATED)
        if not self.renderer:
            raise Exception("Could not create SDL2 renderer")
        self.surface = Surface(width, height, self.renderer)
        return self.surface

    def set_caption(self, title):
        sdl2.SDL_SetWindowTitle(self.window, title.encode('utf-8'))

    def flip(self):
        sdl2.SDL_RenderPresent(self.renderer)

    def poll_events(self):
        events = []
        event = sdl2.SDL_Event()
        while sdl2.SDL_PollEvent(event) != 0:
            if event.type == QUIT:
                events.append(event)
            elif event.type == sdl2.SDL_KEYDOWN:
                self.key_state[event.key.keysym.sym] = True
            elif event.type == sdl2.SDL_KEYUP:
                self.key_state[event.key.keysym.sym] = False
        return events

    def get_pressed(self):
        return self.key_state.copy()

    def quit(self):
        sdl2.SDL_DestroyRenderer(self.renderer)
        sdl2.SDL_DestroyWindow(self.window)
        sdl2.SDL_Quit()

class Clock:
    def __init__(self):
        self.last_tick = time.time()
        self.fps = 0
        self.delay = 0

    def tick(self, target_fps=60):
        current = time.time()
        elapsed = current - self.last_tick
        target_delay = 1.0 / target_fps
        to_sleep = target_delay - elapsed
        if to_sleep > 0:
            time.sleep(to_sleep)
            self.fps = target_fps
        else:
            self.fps = int(1 / elapsed) if elapsed > 0 else 0
        self.last_tick = time.time()
        return self.fps

_display = Display()

def init():
    pass

def quit():
    _display.quit()

def display_set_mode(size):
    return _display.set_mode(size)

def display_set_caption(title):
    _display.set_caption(title)

def display_flip():
    _display.flip()

def event_get():
    return _display.poll_events()

def key_get_pressed():
    return _display.get_pressed()

Surface.paint = Surface.paint
Surface.flash = Surface.flash

Rect.move_ip = Rect.move_ip
Rect.colliderect = Rect.colliderect
Rect.copy = Rect.copy

Clock.tick = Clock.tick
