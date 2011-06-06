import sys
import gtk
import gtk.gtkgl
import pickle

from OpenGL.GL import *

#import sprite_rules
#import objects
from core.graphics.graphic import Graphic
	
class EditorWindow:

    def on_window_destroy(self, widget, data=None):
        gtk.main_quit()
             
    def __init__(self):
        self.display_mode = gtk.gdkgl.MODE_RGB|gtk.gdkgl.MODE_DEPTH|gtk.gdkgl.MODE_SINGLE
        self.glconfig = gtk.gdkgl.Config(mode=self.display_mode)

        self.image_file = None
        self.make_rect = False

        builder = gtk.Builder()
        builder.add_from_file("tools/editor.glade") 
        
        builder.connect_signals(self)
        self.window = builder.get_object("window")
        self.drawing_area = builder.get_object("drawingarea")
        gtk.gtkgl.widget_set_gl_capability(self.drawing_area, self.glconfig)
        self.drawing_area.set_events(gtk.gdk.BUTTON_PRESS_MASK|gtk.gdk.POINTER_MOTION_MASK|
                                     gtk.gdk.BUTTON_RELEASE_MASK)
        self.drawing_area.connect_after("realize", self.setup_gl, None)
        
        self.drawing_area.connect("expose_event", self.expose, None)
        self.drawing_area.connect("button_press_event", self.mouse_button_down, None)
        self.drawing_area.connect("motion_notify_event", self.mouse_move, None)
        self.drawing_area.connect("button_release_event", self.mouse_button_release, None)               
        self.spritesheet = None
        #gtk.timeout_add(1000, self.test, None)

    def test(self, button):
        print "clicked"

    def change_orientation(self, combobox):
        print "changed"

    def mouse_button_down(self, drawing, event, data):
        self.make_rect = True
        self.x, self.y = event.x, event.y
        self.x2, self.y2 = event.x, event.y
        
    def mouse_button_release(self, drawing, event, data):
        self.make_rect = False
        x,y = self.x, self.y
        x2,y2 = self.x2, self.y2
        if x < x2:
            self.frame_x = x
            self.frame_w = x2-x
        else:
            self.frame_x = x2
            self.frame_w = x-x2

        if y < y2:
            self.frame_y = y
            self.frame_h = y2-y
        else:
            self.frame_y = y2
            self.frame_h = y-y2

    def mouse_move(self, drawing, event, data):
        if self.make_rect:
            x2, y2 = event.x, event.y
            x,y = self.x,self.y
            self.gldrawable.gl_begin(self.glcontext)
            glClear(GL_COLOR_BUFFER_BIT)
            
            if self.spritesheet:
                self.spritesheet.draw()
            y = self.h - y
            y2 = self.h - y2
            
            glBegin(GL_LINE_LOOP)
            glVertex(x, y, 0)
            glVertex(x2, y, 0)
            glVertex(x2, y2, 0)
            glVertex(x, y2, 0)
            glEnd()        
            
            if self.gldrawable.is_double_buffered():
                self.gldrawable.swap_buffers()
            else:
                glFlush()
            self.gldrawable.gl_end()
            self.x2, self.y2 = x2,y2

    def load_sprite(self, data):
        self.image_file = data.get_preview_filename()
        
        if self.image_file[-4:] != ".png":
            self.image_file = None
        else:
            self.spritesheet = Graphic("./tools/reimu.png")
            self.gldrawable.gl_begin(self.glcontext)
            glClear(GL_COLOR_BUFFER_BIT)
            self.spritesheet.draw()
            if self.gldrawable.is_double_buffered():
                self.gldrawable.swap_buffers()
            else:
                glFlush()

            self.gldrawable.gl_end()
                
    def setup_gl(self, drawing, event):
        self.glcontext = gtk.gtkgl.widget_get_gl_context(drawing)
        self.gldrawable = gtk.gtkgl.widget_get_gl_drawable(drawing)

        self.gldrawable.gl_begin(self.glcontext)
        
        glClearColor(0.0,0.0,0.0,0.0)
        glClear(GL_COLOR_BUFFER_BIT)
        self.gldrawable.gl_end()

    def expose(self, drawing, event, data):
        w, h = drawing.get_window().get_size()
        
        self.gldrawable.gl_begin(self.glcontext)
        
        glClear(GL_COLOR_BUFFER_BIT)
        glViewport (0, 0, w, h)
        glMatrixMode (GL_PROJECTION)
        glLoadIdentity ()
        glOrtho (0.0, w, 0.0, h, -1.0, 1.0)
        glMatrixMode (GL_MODELVIEW)
        glLoadIdentity ()

        if self.spritesheet:
            self.spritesheet.draw()
        if self.gldrawable.is_double_buffered():
            self.gldrawable.swap_buffers()
        else:
            glFlush()
        self.gldrawable.gl_end()
        self.w, self.h = w,h
        return True

def run():
    editor = EditorWindow()
    editor.window.show()
    
    gtk.main()
    
