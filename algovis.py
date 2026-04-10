import pygame
WIDTH, HEIGHT = 1024, 768
FPS = 60
#import os
def rgb_hlight(clr, hlight):
    return (max(min(clr[0]+hlight, 255), 0), max(min(clr[1]+hlight, 255), 0), max(min(clr[2]+hlight, 255), 0))
class Scene:
    def __init__(self, controls):
        self.controls = controls
    def show(self, screen):
        rects = []
        for control in self.controls:
            rects.extend(control.show(screen))
        return rects
    def undraw(self, screen):
        rects = []
        for control in self.controls:
            pygame.draw.rect(screen, pygame.Color("black"), control.rect)
            rects.append(control.rect)
        return rects
    def on_event(self, event):
        newScene = None
        if event.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP, pygame.MOUSEMOTION):
            for control in self.controls:
                s = control.on_mouse_event(event, pygame.mouse.get_pos(), pygame.mouse.get_pressed())
                if not s is None: newScene = s
        return newScene
    def on_animate(self, elapsed):
        for control in self.controls:
            control.on_animate(elapsed)
class MainScene(Scene):
    def __init__(self, font):
        controls = [Button("Information", (200, 200), font, self.infoClick, bg="gray", hoverbg="red"), #"ℹ"
                    Button("Insert Sort", (200, 250), font, self.insertSortClick, bg="gray", hoverbg="red")]
        super().__init__(controls)
    def infoClick(self): return InfoScene
    def insertSortClick(self): return InsertSortScene
class InfoScene(Scene):
    def __init__(self, font=None):
        controls = [Label(InfoScene.getInfoStrs(), (400, 0), font),
                    BackButton((960, 10), MainScene)]
        super().__init__(controls)
    def getInfoStrs():
        strs = ["Driver: " + pygame.display.get_driver(),
                    "Number of Displays: " + str(pygame.display.get_num_displays()),
                    ]
        info = pygame.display.Info()
        strs.extend(str(info).replace("<", "").replace(">", "").split("\n")[:-2])
        """
        openGLAttrs = ["GL_RED_SIZE", "GL_GREEN_SIZE", "GL_BLUE_SIZE",
            "GL_ALPHA_SIZE", "GL_BUFFER_SIZE", "GL_DOUBLEBUFFER",
            "GL_DEPTH_SIZE", "GL_STENCIL_SIZE", "GL_ACCUM_RED_SIZE",
            "GL_ACCUM_GREEN_SIZE", "GL_ACCUM_BLUE_SIZE", "GL_ACCUM_ALPHA_SIZE",
            "GL_ACCELERATED_VISUAL", "GL_CONTEXT_MAJOR_VERSION", "GL_CONTEXT_MINOR_VERSION",
            "GL_SHARE_WITH_CURRENT_CONTEXT", "GL_CONTEXT_FLAGS",
            "GL_CONTEXT_DEBUG_FLAG", "GL_CONTEXT_FORWARD_COMPATIBLE_FLAG",
            "GL_CONTEXT_ROBUST_ACCESS_FLAG", "GL_CONTEXT_RESET_ISOLATION_FLAG",
            "GL_CONTEXT_PROFILE_MASK",
            "GL_CONTEXT_PROFILE_CORE", "GL_CONTEXT_PROFILE_COMPATIBILITY",
            "GL_CONTEXT_PROFILE_ES", "GL_FRAMEBUFFER_SRGB_CAPABLE",
            "GL_CONTEXT_RELEASE_BEHAVIOR",
            "GL_CONTEXT_RELEASE_BEHAVIOR_NONE", "GL_CONTEXT_RELEASE_BEHAVIOR_FLUSH",
            "GL_STEREO", "GL_MULTISAMPLEBUFFERS", "GL_MULTISAMPLESAMPLES",
            "GL_SWAP_CONTROL", "GL_ACCELERATED_VISUAL"]
        for s in openGLAttrs:
            strs.append(s + ": " + pygame.display.gl_get_attribute(getattr(pygame, s)))
        """
        wminfo = pygame.display.get_wm_info()
        for key in wminfo:
            strs.append(key + ": " + str(wminfo[key]))
        modes = pygame.display.list_modes()
        strs.append("Display modes: " + str(modes[0]))
        for idx in range(1, len(modes), 3):
            strs.append(",".join(str(mode) for mode in modes[idx:idx+3]))
        dsizes = pygame.display.get_desktop_sizes()
        strs.append("Desktop sizes: " + str(dsizes[0]))
        for idx in range(1, len(dsizes), 3):
            strs.append(",".join(str(dsize) for dsize in dsizes[idx:idx+3]))
        return strs
class SortControl:
    def __init__(self, data, pos, fg="white", bg="black"):
        self.x, self.y = pos; self.data = data
        self.fg, self.bg = pygame.Color(fg), pygame.Color(bg)
        self.currentItem = 0
        self.animState = 0
        self.redraw(self.data[0][0])
    def redraw(self, l):
        self.isDrawn = False
        self.rects = []
        for i, val in enumerate(l):
            self.rects.append(pygame.Rect(self.x + 10*i, self.y, 10, val*10))
        self.rect = pygame.Rect(self.x, self.y, 10*len(l), max(l)*10)
    def show(self, screen):
        if self.isDrawn: return []
        self.isDrawn = True
        for rect in self.rects:
            pygame.draw.rect(screen, self.bg, [rect[0], rect[1]+rect[3], rect[2], self.rect.height])
            pygame.draw.rect(screen, self.fg, rect)
        return [self.rect]
    def on_mouse_event(self, event, pos, pressed): pass
    def on_animate(self, elapsed):
        self.animState += elapsed * self.state.speed
        if self.animState < 0: self.animState = 0
        if self.animState > len(self.data) * 500 - 1: self.animState = len(self.data) * 500 - 1
        currentItem = int(self.animState / 500)
        self.redraw(self.data[currentItem][0])
class InsertSortScene(Scene):
    def __init__(self, font):
        #print(InsertSortScene.insert_sort([3, 10, 2, 9, 1, 0, 2, 4, 8, 9, 10, 2, 4, 6]))
        controls = [LatexLabel("$\mathcal{O}(n^2)$", (60, 40), font),
                    BackButton((960, 10), MainScene),
                    MediaControlPanel((400, 660)),
                    SortControl(InsertSortScene.meta_insert_sort([3, 10, 2, 9, 1, 0, 2, 4, 8, 9, 10, 2, 4, 6]), (100, 100))]
        controls[3].state = controls[2].state
        super().__init__(controls)
    def insert_sort(l):
        for i in range(1, len(l)):
            for j in range(i):
                if l[j] > l[i]: break
            else: continue
            l[j:i+1] = [l[i], *l[j:i]]
        return l
    def meta_insert_sort(l):
        ll = []
        for i in range(1, len(l)):
            for j in range(i):
                if l[j] > l[i]: break
            else:
                ll.append((l.copy(), i, None))
                continue
            l[j:i+1] = [l[i], *l[j:i]]
            ll.append((l.copy(), i, j))
        return ll
class LatexLabel:
    def __init__(self, ltx, pos, font, fg="red", bg="white"):
        self.x, self.y = pos; self.ltx = ltx
        self.fg, self.bg, self.font = fg, bg, font
        self.redraw()
    def redraw(self):
        self.isDrawn = False
        self.surf = LatexLabel.latexToPyGameSurface(self.ltx, self.fg, self.bg)
        self.rect = pygame.Rect(self.x, self.y, self.surf.get_width(), self.surf.get_height())
    def show(self, screen):
        if self.isDrawn: return []
        self.isDrawn = True
        screen.blit(self.surf, (self.x, self.y))
        return [self.rect]
    def on_mouse_event(self, event, pos, pressed): pass
    def on_animate(self, elapsed): pass
    def latexToPyGameSurface(ltx, color="red", bgcolor="white"):
        import matplotlib
        #matplotlib.use("Agg")
        import matplotlib.backends.backend_agg as agg
        from matplotlib.figure import Figure
        #plt.rcParams['text.usetex'] = True
        dpi = 100
        fig = Figure()
        tx = matplotlib.text.Text(0, 1, ltx, color, usetex=None, horizontalalignment="left", verticalalignment="top")
        fig.add_artist(tx)
        memrenderer = agg.RendererAgg(WIDTH, HEIGHT, dpi)
        fig.draw(memrenderer)
        extent = tx.get_window_extent(renderer=memrenderer, dpi=dpi)
        fig = Figure(figsize=((extent.x1-extent.x0)/dpi, (extent.y1-extent.y0)/dpi), dpi=dpi)
        fig.patch.set_facecolor(bgcolor)
        tx = matplotlib.text.Text(0, 1, ltx, color, usetex=None, horizontalalignment="left", verticalalignment="top")
        fig.add_artist(tx)
        canvas = agg.FigureCanvasAgg(fig)
        canvas.draw()
        renderer = canvas.get_renderer()
        raw_data = renderer.tostring_rgb()
        size = canvas.get_width_height()
        return pygame.image.fromstring(raw_data, size, "RGB")
class Label:
    def __init__(self, strs, pos, font, fg="white", bg="black"):
        self.x, self.y = pos; self.strs = strs
        self.fg, self.bg, self.font = pygame.Color(fg), pygame.Color(bg), font
        self.redraw()
    def redraw(self):
        self.isDrawn = False
        self.surf = []
        self.tops = []; curheight = 0; curwidth = 0
        for s in self.strs:
            self.surf.append(self.font.render(s, 1, "white", "black"))
            self.tops.append(curheight)
            curwidth = max(curwidth, self.surf[-1].get_size()[0])
            curheight += self.surf[-1].get_size()[1]
        self.rect = pygame.Rect(self.x, self.y, curwidth, curheight)
    def show(self, screen):
        if self.isDrawn: return []
        self.isDrawn = True
        for i, surf in enumerate(self.surf):
            screen.blit(surf, (self.x, self.y+self.tops[i]))
        return [self.rect]
    def on_mouse_event(self, event, pos, pressed): pass
    def on_animate(self, elapsed): pass
class Button:
    def __init__(self, text, pos, font, click, fg="white", bg="black", hoverbg="gray"):
        self.x, self.y = pos; self.text = text
        self.fg, self.bg, self.hoverbg, self.font = pygame.Color(fg), pygame.Color(bg), pygame.Color(hoverbg), font
        self.isDown, self.isHover = False, False
        self.click = click
        self.redraw(self.bg)
    def redraw(self, bg):
        self.isDrawn = False
        self.textsurf = self.font.render(self.text, 1, self.fg, bg)
        self.size = self.textsurf.get_size()
        lwidth, hlight = 2, 40
        self.size = (self.size[0]+lwidth*2, self.size[1]+lwidth*2)
        self.surface = pygame.Surface(self.size)
        self.surface.fill(bg)
        pygame.draw.line(self.surface, rgb_hlight(bg, hlight), (0, 0), (0, self.size[1]), lwidth)
        pygame.draw.line(self.surface, rgb_hlight(bg, hlight), (0, 0), (self.size[0], 0), lwidth)
        pygame.draw.line(self.surface, rgb_hlight(bg, -hlight), (lwidth, self.size[1]-lwidth), (self.size[0], self.size[1]-lwidth), lwidth)
        pygame.draw.line(self.surface, rgb_hlight(bg, -hlight), (self.size[0]-lwidth, lwidth), (self.size[0]-lwidth, self.size[1]), lwidth)
        self.surface.blit(self.textsurf, (lwidth, lwidth))
        self.rect = pygame.Rect(self.x, self.y, self.size[0], self.size[1])
    def show(self, screen):
        if self.isDrawn: return []
        self.isDrawn = True
        screen.blit(self.surface, (self.x, self.y))
        return [self.rect]
    def on_mouse_event(self, event, pos, pressed):
        if event.type == pygame.MOUSEMOTION:
            x, y = pos
            if self.rect.collidepoint(x, y) ^ (not self.isHover): return
            self.isHover = not self.isHover
            self.redraw(self.hoverbg if self.isHover else self.bg)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if pressed[0]:
                x, y = pos
                if self.rect.collidepoint(x, y): self.isDown = True
        elif event.type == pygame.MOUSEBUTTONUP and self.isDown:
            if not pressed[0]:
                self.isDown = False
                x, y = pos
                if self.rect.collidepoint(x, y): return self.click()
        return None
    def on_animate(self, elapsed): pass
    def click(self): return None
class BackButton(Button):
    def __init__(self, pos, cls):
        self.cls = cls
        font = pygame.font.SysFont("Segoe UI Symbol", 30)
        super().__init__("←", pos, font, self.click)
    def click(self): return self.cls
class AnimationState:
    def __init__(self):
        self.speed = 0
class MediaControlPanel:
    def __init__(self, pos, fg="white", bg="black", hoverbg="gray"):
        font = pygame.font.SysFont("Segoe UI Symbol", 30)
        #https://en.wikipedia.org/wiki/Media_control_symbols
        x, y = pos
        fastBackward = Button("⏪", (x, y), font, self.fastBackwardClick, bg="gray", hoverbg="blue")
        x += fastBackward.size[0]
        stepBackButton = Button("⎹◀", (x, y), font, self.stepBackButtonClick, bg="gray", hoverbg="blue")
        x += stepBackButton.size[0]
        backButton = Button("⏴", (x, y), font, self.backButtonClick, bg="gray", hoverbg="blue")
        x += backButton.size[0]
        stopButton = Button("⏹", (x, y), font, self.stopButtonClick, bg="gray", hoverbg="blue")
        x += stopButton.size[0]
        playButton = Button("⏵", (x, y), font, self.playButtonClick, bg="gray", hoverbg="blue")
        x += playButton.size[0]
        stepForwardButton = Button("▶⎸", (x, y), font, self.stepForwardButtonClick, bg="gray", hoverbg="blue")
        x += stepForwardButton.size[0]
        fastForward = Button("⏩", (x, y), font, self.fastForwardClick, bg="gray", hoverbg="blue")
        self.buttons = [fastBackward, stepBackButton, backButton, stopButton, playButton, stepForwardButton, fastForward]
        self.rect = pygame.Rect(pos[0], y, sum(b.size[0] for b in self.buttons), max(b.size[1] for b in self.buttons))
        self.state = AnimationState()
    def show(self, screen):
        rects = []
        for button in self.buttons:
            rects.extend(button.show(screen))
        return rects
    def on_mouse_event(self, event, pos, pressed):
        for button in self.buttons:
            button.on_mouse_event(event, pygame.mouse.get_pos(), pygame.mouse.get_pressed())
    def on_animate(self, elapsed): pass
    def fastBackwardClick(self):
        self.state.speed = -5
    def backButtonClick(self):
        self.state.speed = -1
    def playButtonClick(self):
        if self.state.speed == 1:
            self.buttons[2].text = "⏵"
            self.state.speed = 0
        else:
            self.buttons[2].text = "⏸"
            self.state.speed = 1
        self.buttons[2].redraw(self.buttons[2].bg)
    def stopButtonClick(self):
        self.state.speed = 0
    def fastForwardClick(self):
        self.state.speed = 5
    def stepBackButtonClick(self): pass
    def stepForwardButtonClick(self): pass
    def doReset(self): return None
def main():
    pygame.init()
    #logo = pygame.image.load("logo32x32.png")
    #pygame.display.set_icon(logo)
    screen = pygame.display.set_mode((WIDTH,HEIGHT))
    clock = pygame.time.Clock()
    textFont = pygame.font.SysFont("Arial", 30)
    scene = MainScene(textFont)
    running = True
    scene.show(screen)
    pygame.display.update()
    elapsed = 0
    while running:
        #left, middle, right = pygame.mouse.get_pressed()
        #pygame.mouse.get_pos()
        rects, sceneChange = [], False
        for event in pygame.event.get():
            if event.type == pygame.QUIT: running = False; break
            newScene = scene.on_event(event)
            if not newScene is None:
                rects.extend(scene.undraw(screen))
                scene = newScene(textFont)
                sceneChange = True
        if elapsed != 0:
            if not sceneChange: scene.on_animate(elapsed)
            rects.extend(scene.show(screen))
        if len(rects) != 0: pygame.display.update(rects)        
        #pygame.display.update()
        elapsed = clock.tick(FPS) #FPS is Hz, 1/FPS=sleep time in seconds
    pygame.quit()

def d(x, y, nodeweight): return nodeweight[y] #infinity for walls
def hEuclidean(x, goal):
    return abs(x[0] - goal[0]) ** 2 + abs(x[1] - goal[1]) ** 2
def hManhattan(x, goal):
    return abs(x[0] - goal[0]) + abs(x[1] - goal[1])
def reconstruct_path(cameFrom, current):
    total_path = current
    while current in cameFrom:
        current = cameFrom[current]
        total_path.append(current)
    return total_path.reverse()
def A_star(start, goal, h, d, g, coord, nodeweight):
    openSet = {start}
    cameFrom = {}
    gScore = {n: None for n in g}
    gScore[start] = 0
    fScore = {n: None for n in g}
    fScore[start] = h(coord[start], coord[goal])
    while len(openSet) != 0:
        nonInf = list(filter(lambda n: not fScore[n] is None, openSet))        
        current = min(nonInf, key=lambda n: fScore[n]) if len(nonInf) != 0 else next(iter(openSet))
        if current == goal:
            return reconstruct_path(cameFrom, current)
        openSet.remove(current)
        for neighbor in g[current]:
            tentative_gScore = None if gScore[current] is None or d(coord[current], coord[neighbor], nodeweight) is None else gScore[current] + d(coord[current], coord[neighbor], nodeweight)
            if tentative_gScore < gScore[neighbor]:
                cameFrom[neighbor] = current
                gScore[neighbor] = tentative_gScore
                fScore[neighbor] = None if tentative_gScore is None else tentative_gScore + h(coord[neighbor], coord[goal])
                if neighbor not in openSet:
                    openSet.add(neighbor)
def make_grid(size):
    g = {} #adjacency list
    coord = {} #map node -> x, y coordinates
    for i in range(size):
        for j in range(size):
            n = len(g)
            g[n] = []
            if i != 0: g[n].append((i - 1) * size + j)
            if j != 0: g[n].append(i * size + j - 1)
            if i != size-1: g[n].append((i + 1) * size + j)
            if j != size-1: g[n].append(i * size + j + 1)
            coord[n] = (i, j)
    return g, coord
g, coord = make_grid(10)
nodeweight = {n: 1 if True else None for n in g}
A_star(1, 10, hManhattan, d, g, coord, nodeweight)

if __name__ == '__main__': main()