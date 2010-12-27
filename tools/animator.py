import pygame
import glFreeType
import pickle
from OpenGL.GL import *
from pygame.locals import *

import os.path

import objects
import widgets
import sprite_rules

x, y   = None, None
w, h = None, None
widgets_list = {}
animated = None

def main():
    width, height = 640, 480
    pygame.display.init()
    pygame.display.set_caption("Animator")
    display = pygame.display.set_mode((width, height), OPENGL|DOUBLEBUF)
    running = True

    set_up(width, height)

    while running:
        running = process()
        draw()

def f():
    print "lol"

def set_up(width, height):
    font = glFreeType.font_data( "free_sans.ttf", 30 )
    glOrtho(0.0, width, 0.0, height,-1.0,1.0)
    glClearColor(0.0,0.0,0.0,0.0)    
    
    widgets_list["object_text"] = widgets.Text_Box(0,400, True, "reimu")
    widgets_list["object_button"] = widgets.Button(25, 360, "button", "button_down", load_spritesheet, (widgets_list["object_text"],))
    widgets_list["spritesheet"] = widgets.Null_Widget()
    
    widgets_list["action_name"] = widgets.Text_Box(200,400, True, "idle-s")
    widgets_list["frame_number"] = widgets.Int_Box(200,380, True, "0")
    widgets_list["frame_x"] = widgets.Int_Box(200,360, True, "0")
    widgets_list["frame_y"] = widgets.Int_Box(260,360, True, "0")
    widgets_list["frame_w"] = widgets.Int_Box(200,340, True, "0")
    widgets_list["frame_h"] = widgets.Int_Box(260,340, True, "0")
    widgets_list["selection"] = widgets.Selection_Box(10,10,100,100,widgets_list, "spritesheet")
    f = widgets_list["selection"].set_dimensions
    args = widgets_list["frame_x"], widgets_list["frame_y"], widgets_list["frame_w"], widgets_list["frame_h"]
    widgets_list["frame_button"] = widgets.Button(210, 320, "button", "button_down", f, args)
    widgets_list["save_button"] = widgets.Button(180, 250, "button", "button_down", save_frame,())
    pygame.time.set_timer(pygame.USEREVENT+1, 200)
    global animated
    try:
        animated = widgets.Animated(400,320,"reimu")
    except:
        print "None"
        animate = None
    

def process():
    for event in pygame.event.get():
        if event.type == QUIT:
            return False
        if event.type == KEYDOWN:
            for w in widgets_list:
                widgets_list[w].process_key(event)
        if event.type == MOUSEBUTTONDOWN:
            for w in widgets_list:
                widgets_list[w].process_click(*pygame.mouse.get_pos())
        if event.type == MOUSEBUTTONUP:
            for w in widgets_list:
                widgets_list[w].process_release(*pygame.mouse.get_pos())
        if event.type == USEREVENT + 1:
            global animated
            if animated:
                animated.update()
    
    
    return True
    
def draw():
    glClear(GL_COLOR_BUFFER_BIT)
        
    for w in widgets_list:
        widgets_list[w].draw()

    widgets_list["selection"].draw()
    global animated
    if animated:
        animated.draw()
    pygame.display.flip()

def load_spritesheet(spritesheet):
    
    filename = spritesheet.text()
    
    try:
        open(filename + ".png")
    except IOError:
        print "This file does not exist"
        return
    try:
        open(filename + ".spr")
        print "sprite file found"
    except IOError:
        print "No sprite file, creating new one"
        F = open(filename + ".spr", "wb")
        pickle.dump(sprite_rules.Sprite(filename))
        F.close()
    
    widgets_list["spritesheet"] = objects.Graphic(0,0,1.0, filename,1.0)
    print widgets_list["spritesheet"].filename

def save_frame():
    spritesheet = widgets_list["spritesheet"].filename
    action_name = widgets_list["action_name"].text()
    frame_number = widgets_list["frame_number"].current
    print spritesheet
    try:
        spr_file = open(spritesheet + ".spr")
    except IOError:
        print "No sprite file."
        return

    try:
        info = pickle.load(spr_file)
    except EOFError:
        info = sprite_rules.Sprite(spritesheet)

    dimensions = (widgets_list["frame_x"].current,widgets_list["frame_y"].current,widgets_list["frame_w"].current,widgets_list["frame_h"].current)
    info.set_frame(action_name, frame_number, dimensions)
    new_info = open(spritesheet + ".spr", "wb")
    pickle.dump(info, new_info)
    new_info.close()
    global animated
    animated = widgets.Animated(400,320,"reimu")
    
    print "frame written"

if __name__ == "__main__":
    main()
