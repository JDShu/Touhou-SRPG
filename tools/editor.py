import sys
import gtk
import gtk.gtkgl
import pickle
import gobject

from OpenGL.GL import *

from sprite_rules import *
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
        self.window2 = builder.get_object("preview")
        
        self.drawing_area = builder.get_object("drawingarea")
        self.preview_gl = builder.get_object("preview_gl")

        self.x_button = builder.get_object("X")
        self.y_button = builder.get_object("Y")
        self.w_button = builder.get_object("W")
        self.h_button = builder.get_object("H")
        self.frame_button = builder.get_object("frame_number")
        
        self.save_frame = builder.get_object("save_frame")
        self.save_frame.set_sensitive(False)

        gtk.gtkgl.widget_set_gl_capability(self.drawing_area, self.glconfig)
        gtk.gtkgl.widget_set_gl_capability(self.preview_gl, self.glconfig)
        self.drawing_area.set_events(gtk.gdk.BUTTON_PRESS_MASK|gtk.gdk.POINTER_MOTION_MASK|
                                     gtk.gdk.BUTTON_RELEASE_MASK)
        self.drawing_area.connect_after("realize", self.setup_gl, None)
        self.preview_gl.connect_after("realize", self.setup_gl, None)
        #self.preview_gl.connect("expose_event", self.expose, None)

        self.drawing_area.connect("expose_event", self.expose, None)
        self.drawing_area.connect("button_press_event", self.mouse_button_down, None)
        self.drawing_area.connect("motion_notify_event", self.mouse_move, None)
        self.drawing_area.connect("button_release_event", self.mouse_button_release, None)               
        self.spritesheet = None
        self.sprite_dialog = builder.get_object("sprite_dialog")
        self.load_sprdata_dialog = builder.get_object("load_sprdata_dialog")
 
        self.new_action_dialog = builder.get_object("new_action_dialog")
        
        self.new_action_name = builder.get_object("action_name_entry")
 #gtk.timeout_add(1000, self.test, None)

        hbox = builder.get_object("box2")

        self.select_action = gtk.combo_box_new_text()
        self.select_action.set_tooltip_text("Action")
        self.select_facing = gtk.combo_box_new_text()
        self.select_action.set_tooltip_text("Direction")
        self.select_action.connect("changed",self.enable_save_frame, None)

        self.enable_directions()

        hbox.add(self.select_action)
        hbox.add(self.select_facing)
        
        self.select_action.show()
        self.select_facing.show()

        self.sprite = Sprite(None)

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
            glcontext = gtk.gtkgl.widget_get_gl_context(drawing)
            gldrawable = gtk.gtkgl.widget_get_gl_drawable(drawing)

            x2, y2 = event.x, event.y
            x,y = self.x,self.y
            gldrawable.gl_begin(glcontext)
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
            
            if gldrawable.is_double_buffered():
                gldrawable.swap_buffers()
            else:
                glFlush()
            gldrawable.gl_end()

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

            self.x2, self.y2 = x2,y2
            self.x_button.set_value(self.frame_x)
            self.y_button.set_value(self.frame_y)
            self.w_button.set_value(self.frame_w)
            self.h_button.set_value(self.frame_h)

    def load_spritesheet(self, filename):
        if filename[-4:] == ".png":
            self.spritesheet = Graphic(filename)
            glcontext = gtk.gtkgl.widget_get_gl_context(self.drawing_area)
            gldrawable = gtk.gtkgl.widget_get_gl_drawable(self.drawing_area)
            gldrawable.gl_begin(glcontext)
            glClear(GL_COLOR_BUFFER_BIT)
            self.spritesheet.draw()
            if gldrawable.is_double_buffered():
                gldrawable.swap_buffers()
            else:
                glFlush()

            gldrawable.gl_end()
                
    def setup_gl(self, drawing, event):
        glcontext = gtk.gtkgl.widget_get_gl_context(drawing)
        gldrawable = gtk.gtkgl.widget_get_gl_drawable(drawing)

        gldrawable.gl_begin(glcontext)
        
        glClearColor(0.0,0.0,0.0,0.0)
        glClear(GL_COLOR_BUFFER_BIT)
        gldrawable.gl_end()

    def expose(self, drawing, event, data):
        w, h = drawing.get_window().get_size()

        glcontext = gtk.gtkgl.widget_get_gl_context(drawing)
        gldrawable = gtk.gtkgl.widget_get_gl_drawable(drawing)
        gldrawable.gl_begin(glcontext)
        
        glClear(GL_COLOR_BUFFER_BIT)
        glViewport (0, 0, w, h)
        glMatrixMode (GL_PROJECTION)
        glLoadIdentity ()
        glOrtho (0.0, w, 0.0, h, -1.0, 1.0)
        glMatrixMode (GL_MODELVIEW)
        glLoadIdentity ()

        if self.spritesheet:
            self.spritesheet.draw()
        if gldrawable.is_double_buffered():
            gldrawable.swap_buffers()
        else:
            glFlush()
        gldrawable.gl_end()
        self.w, self.h = w,h
        return True

    def open_sprite_dialog(self, event):
        r = self.sprite_dialog.run()
        if r == gtk.RESPONSE_ACCEPT:
            f = self.sprite_dialog.get_filename()
            self.load_spritesheet(f)
        else:
            print "no"
        self.sprite_dialog.hide()

    def open_sprdata_dialog(self, event):
        r = self.load_sprdata_dialog.run()
        if r == gtk.RESPONSE_ACCEPT:
            print "yes"
        else:
            print "no"
        self.load_sprdata_dialog.hide()

    def new_action_dialog(self, event):
        print "action"
        r = self.new_action_dialog.run()
        if r == gtk.RESPONSE_ACCEPT:
            action_name = self.new_action_name.get_text()
            self.sprite.new_action(action_name)
            self.select_action.append_text(action_name)
            print self.sprite.frames
        else:
            print "no"
        self.new_action_dialog.hide()

    def close_sprite_dialog(self, event):
        self.sprite_dialog.response(gtk.RESPONSE_CANCEL)

    def load_sprite(self, event):
        self.sprite_dialog.response(gtk.RESPONSE_ACCEPT)
        
    def load_sprdata_dialog(self, event):
        self.load_sprdata_dialog.response(gtk.RESPONSE_ACCEPT)

    def close_sprdata_dialog(self, event):
        self.load_sprdata_dialog.response(gtk.RESPONSE_CANCEL)

    def enable_directions(self):
        self.select_facing.append_text("N")
        self.select_facing.append_text("S")
        self.select_facing.append_text("E")
        self.select_facing.append_text("W")

    def save_frame(self, button):
        x = self.x_button.get_value()
        y = self.x_button.get_value()
        data = FrameData()
        data.set_pos((x,y))
        action = self.select_action.get_active_text()
        facing = self.select_facing.get_active_text()
        frame = self.frame_button.get_value_as_int()
        print action, facing, frame
        self.sprite.set_frame(action,facing,frame,data)

    def enable_save_frame(self, cb, data):
        self.save_frame.set_sensitive(True)

def run():
    editor = EditorWindow()
    editor.window.show()
    editor.window2.show()
    
    gtk.main()
    
