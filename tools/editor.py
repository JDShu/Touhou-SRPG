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

        builder = gtk.Builder()
        builder.add_from_file("tools/editor.glade") 
        
        builder.connect_signals(self)
        self.window = builder.get_object("window")
        self.drawing_area = builder.get_object("drawingarea")
        gtk.gtkgl.widget_set_gl_capability(self.drawing_area, self.glconfig)
        self.drawing_area.set_events(gtk.gdk.BUTTON_PRESS_MASK|gtk.gdk.POINTER_MOTION_MASK)
        self.drawing_area.connect_after("realize", self.setup_gl, None)
        self.drawing_area.connect("expose_event", self.expose, None)
        self.drawing_area.connect("button_press_event", self.mouse_test, None)
        self.drawing_area.connect("motion_notify_event", self.mouse_test, None)
               
        self.spritesheet = None
        #gtk.timeout_add(1000, self.test, None)

    def change_orientation(self, data):
        print "changed"
        
    def test(self, data):
        print "data"
        return True

    def test2(self, data,a,b):
        print "data"
        return True

    def mouse_test(self, drawing, event, data):
        print "mouse position: ", event.x, event.y

    def load_sprite(self, data):
        self.image_file = data.get_preview_filename()
        
        if self.image_file[-4:] != ".png":
            self.image_file = None
        else:
            self.spritesheet = Graphic("./tools/reimu.png")
            print self.image_file
            print self.spritesheet
            self.gldrawable.gl_begin(self.glcontext)
            self.spritesheet.draw()
            if self.gldrawable.is_double_buffered():
                self.gldrawable.swap_buffers()
            else:
                glFlush()

            self.gldrawable.gl_end()
            print "drawn"
    
    def setup_gl(self, drawing, event):
        print "init"
        self.glcontext = gtk.gtkgl.widget_get_gl_context(drawing)
        self.gldrawable = gtk.gtkgl.widget_get_gl_drawable(drawing)
        
        self.gldrawable.gl_begin(self.glcontext)
        glOrtho(0.0, 800.0, 0.0, 600.0,-1.0,1.0)
        glClearColor(0.0,1.0,0.0,0.0)
        
        self.gldrawable.gl_end()

    def expose(self, drawing, event, data):
        print "expose"
        glcontext = gtk.gtkgl.widget_get_gl_context(drawing)
        gldrawable = gtk.gtkgl.widget_get_gl_drawable(drawing)
        gldrawable.gl_begin(glcontext)
        glClear(GL_COLOR_BUFFER_BIT)
        #print self.spritesheet
        if self.spritesheet:
            self.spritesheet.draw()
        if gldrawable.is_double_buffered():
            gldrawable.swap_buffers()
        else:
            glFlush()
        gldrawable.gl_end()
        #return True

def run():
    editor = EditorWindow()
    editor.window.show()
    
    gtk.main()
    
