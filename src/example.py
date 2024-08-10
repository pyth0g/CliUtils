from cliutils import SelList, List, Draw, Table, Ansi, TextObfTransition, ProgressBar, Loader, Animate, VideoToText, ImageToText, UI, Figlet, Container, pprint, silent, cprint
import time

input(f"{Ansi.Color.yellow("Maximize terminal please.")}")

d = lambda text: input(f"\n{Ansi.Color.cyan(f'+--{Ansi.bold(text)}{Ansi.Color.CYAN}--+')}\n")

#SelList
d("SelList")
SelList(["SelList example (1)", "SelList example (2)"]).display()
print("")
SelList(["SelList example (3)", "SelList example (4)"], SelList.Type.NUM).display(SelList.DisplayType.KEY)
print("")
SelList(["SelList example (3)", "SelList example (4)"], SelList.Type.CHR).display(SelList.DisplayType.KEY)

#List
d("List")
List(["List example (1)", "List example (2)"]).display()
print("")
List(["List example (3)", "List example (4)"], "num").display()

#Draw
d("Draw")
Draw.Circle(12).display()
Draw.FullCircle(12).display()
Draw.Rectangle(20, 10).display()
Draw.FullRectangle(20, 10).display()
Draw.Triangle(12).display()
Draw.FullTriangle(12).display()

#Container
d("Container")
Container.Box("Box example (1)").display()
Container.Box("Box example (2)", ["+", "+", "+", "+"], ["-", "|"]).display()

#Table
d("Table")
Table([[(True, True), ["TITLE"]], [(False, True), ["row 1, column 0", "row 1, column 1", "row 1, column 2"]], [(False, True), ["row 2, column 0", "row 2, column 1", "row 2, column 2"]]]).display()

#TextObfTransition
d("TextObfTransition")
TextObfTransition("TextObfTransition example", "TextObfTransition finished", input=True).display()

#ProgressBar
d("ProgressBar")
p = ProgressBar(20, "ProgressBar example ", "(1)", ProgressBar.NUMBER)
p.start()
for _ in range(20):
    p.next()
    time.sleep(0.2)

l = Loader(Loader.DOTS, 3)

def box(x, y, z):
    c = 0
    t = 0
    p = ProgressBar(z, f"{l.get_next()} ", full="#", empty="-")
    r = 0
    for _ in range(z):    
        r += x + y
        x += r
        y += r
        if t == 500:
            t = 0
            p.set_prepend(l.get_next() + " ")
            c += 1
        silent(p.next)
        pprint(Container.Box(p.get()).get())
        t += 1
    
    time.sleep(0.2)
    p.set_prepend(f"{"▃" * len(l.get_next())} ")
    Container.Box(p.get()).display()

box(24, 56, 10000)

#Loader
d("Loader")
l = Loader(Loader.SPINNER)
l.start()
time.sleep(3)
l.stop()
cprint("Loader example (1)")
l = Loader(Loader.DOTS, sleep=0.3)
l.start()
time.sleep(3)
l.stop()
cprint("Loader example (2)")

#Ansi
d("Ansi")
Ansi.Cursor.up()
print(f'{Ansi.Color.yellow("Text")}{Ansi.rgb(255,165,0)} in {Ansi.END}{Ansi.Color.red("different")} {Ansi.Color.rainbow("colors", bold=True)}.')
print(f"{Ansi.BgColor.red("Look!")} {Ansi.BgColor.cyan("Background colors.")}")

#Animate
d("Animate")
width = 20
height = 10

ball_x = round(width / 2)
ball_y = round(height / 2)
velocity_x = 1
velocity_y = 1

num_frames = 100

def generate_frame(ball_x, ball_y):
    frame = [[" " for _ in range(width)] for _ in range(height)]
    frame[ball_y][ball_x] = "O"
    return "\n".join("".join(row) for row in frame)

def update_ball(ball_x, ball_y, velocity_x, velocity_y):
    ball_x += velocity_x
    ball_y += velocity_y
    
    if ball_x <= 0 or ball_x >= width - 1:
        velocity_x = -velocity_x
    if ball_y <= 0 or ball_y >= height - 1:
        velocity_y = -velocity_y
    
    return ball_x, ball_y, velocity_x, velocity_y

frames = []
for _ in range(num_frames):
    frame = generate_frame(ball_x, ball_y)
    frames.append(frame)
    ball_x, ball_y, velocity_x, velocity_y = update_ball(ball_x, ball_y, velocity_x, velocity_y)


Animate(frames).once(0.05, True)

d("ImageToText")
ImageToText.Color("./image.png").display()
ImageToText.Monochrome("./image.png").display()

d("VideoToText")
VideoToText.Color("./video.mp4").display()

d("Figlet")
font = Figlet("3-d")
font.display("Hello, world!", padding=2, width=200)

d("UI")
ui = UI((153, 204, 255), (58, 25))
ui.title("TEST", "shadow")
ui.center("hello world")
pad = 20
ui.interaction((ui.get_pad("[ ] Test", pad), ui.get_pad("[>] Test", pad), 10, ui.bottom, ("hi",)), (ui.get_pad("[ ] Example", pad), ui.get_pad("[>] Example", pad), 11, ui.bottom, ("no",)), (ui.get_pad("[ ] Exit", pad), ui.get_pad("[>] Exit", pad), 12, ui.stop, ""))
ui.display()
