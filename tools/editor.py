import sys
import gtk
import gtk.gtkgl
import pickle
import gobject

from OpenGL.GL import *

from sprite_rules import *

from core.graphics.graphic import Graphic
from core.graphics.animated import Animated

PLAY, STOP = range(2)

class EditorWindow:

    def on_window_destroy(self, widget, data=None):
        gtk.main_quit()

    def __init__(self):
        display_mode = gtk.gdkgl.MODE_RGB|gtk.gdkgl.MODE_DEPTH|gtk.gdkgl.MODE_SINGLE
        self.glconfig = gtk.gdkgl.Config(mode=display_mode)

        self.image_file = None
        self.make_rect = False

        builder = gtk.Builder()
        builder.add_from_file("tools/editor.glade")
        
        self.builder = builder

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

        save_frame = builder.get_object("save_frame")
        save_frame.set_sensitive(False)
        self.builder.get_object("action").set_sensitive(False)
        self.builder.get_object("preview_frame").set_sensitive(False)

        gtk.gtkgl.widget_set_gl_capability(self.drawing_area, self.glconfig)
        gtk.gtkgl.widget_set_gl_capability(self.preview_gl, self.glconfig)
        self.drawing_area.set_events(gtk.gdk.BUTTON_PRESS_MASK|gtk.gdk.POINTER_MOTION_MASK|
                                     gtk.gdk.BUTTON_RELEASE_MASK)
        self.drawing_area.connect_after("realize", self.setup_gl, None)
        self.preview_gl.connect_after("realize", self.setup_gl, None)
        self.preview_gl.connect("expose_event", self.expose, None)

        self.drawing_area.connect("expose_event", self.expose, None)
        self.drawing_area.connect("button_press_event", self.mouse_button_down, None)
        self.drawing_area.connect("motion_notify_event", self.mouse_move, None)
        self.drawing_area.connect("button_release_event", self.mouse_button_release, None)
        self.spritesheet = None
        self.sprite_dialog = builder.get_object("sprite_dialog")
        self.load_sprdata_dialog = builder.get_object("load_sprdata_dialog")

        self.new_action_dialog = builder.get_object("new_action_dialog")
        
        self.new_action_name = builder.get_object("action_name_entry")

        gtk.timeout_add(500, self.draw_preview, None)
        gtk.idle_add(self.refresh, None)

        hbox = builder.get_object("box2")

        self.select_action = gtk.combo_box_new_text()
        self.select_action.set_tooltip_text("Action")
        self.select_facing = gtk.combo_box_new_text()
        self.select_action.set_tooltip_text("Direction")
        self.select_action.connect("changed",self.enable_save_frame, None)
        self.select_action.connect("changed",self.change_action, None)
        self.select_facing.connect("changed",self.enable_save_frame, None)
        self.select_facing.connect("changed",self.change_orientation, None)

        self.enable_directions()

        hbox.add(self.select_action)
        hbox.add(self.select_facing)
        
        self.select_action.show()
        self.select_facing.show()

        self.sprite = Sprite()
        self.preview = None

        self.mode = STOP
        self.show_preview = False

    def refresh(self, data):
        self.draw()
    
    def draw_preview(self, obj):
        glcontext = gtk.gtkgl.widget_get_gl_context(self.preview_gl)
        gldrawable = gtk.gtkgl.widget_get_gl_drawable(self.preview_gl)
        gldrawable.gl_begin(glcontext)        
        glClear(GL_COLOR_BUFFER_BIT)
        if self.preview and self.show_preview:
            if self.mode == PLAY:
                self.preview.update()
            self.preview.draw()            
        glFlush()
        gldrawable.gl_end()
        return True

    def change_orientation(self, combobox, data):
        if self.preview:
            facing = convert(self.select_facing.get_active_text())
            try:
                self.preview.set_facing(facing)
                self.show_preview = True
                self.draw_preview(None)
                self.copy_frame()
            except AttributeError:
                self.show_preview = False
    
    def change_action(self, combobox, data):
        if self.preview:
            action = self.select_action.get_active_text()
            try:
                self.preview.set_action(action)
                if not self.select_facing.get_active_text():
                    self.preview.set_facing(N)
                self.show_preview = True
                self.draw_preview(None)
                frame_length= len(self.sprite.frames[action][N]) - 1
                self.builder.get_object("adjustmentf").set_upper(frame_length)
                self.copy_frame()
            except AttributeError:
                self.show_preview = False

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

    def set_box_coords(self,x1,y1,x2,y2):
        if x1 < x2:
            x = x1
            w = x2-x1
        else:
            x = x2
            w = x1-x2

        if y1 < y2:
            y = y1
            h = y2-y1
        else:
            y = y2
            h = y1-y2

        self.x_button.set_value(x)
        self.y_button.set_value(y)
        self.w_button.set_value(w)
        self.h_button.set_value(h)

    def draw(self, button=None):
        x = self.x_button.get_value()
        y = self.y_button.get_value()
        w = self.w_button.get_value()
        h = self.h_button.get_value()

        x2 = x+w
        y2 = y+h

        drawing = self.builder.get_object("drawingarea")
        glcontext = gtk.gtkgl.widget_get_gl_context(drawing)
        gldrawable = gtk.gtkgl.widget_get_gl_drawable(drawing)
        
        gldrawable.gl_begin(glcontext)
        glClear(GL_COLOR_BUFFER_BIT)
        
        if self.spritesheet:
            self.spritesheet.draw()
            
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
        
    def mouse_move(self, drawing, event, data):
        if self.make_rect:
            self.w, self.h = drawing.get_window().get_size()
            glcontext = gtk.gtkgl.widget_get_gl_context(drawing)
            gldrawable = gtk.gtkgl.widget_get_gl_drawable(drawing)
            
            x2, y2 = event.x, event.y
            y2 = self.h - y2
            
            x,y = self.x,self.y
            y = self.h - y

            self.set_box_coords(x,y,x2,y2)
            self.draw()
           
    def load_spritesheet(self, filename):
        if filename[-4:] == ".png":            
            
            glcontext = gtk.gtkgl.widget_get_gl_context(self.drawing_area)
            gldrawable = gtk.gtkgl.widget_get_gl_drawable(self.drawing_area)
            gldrawable.gl_begin(glcontext)

            #construction uses OpenGL so needs to be in GL context.
            self.spritesheet = Graphic(filename)
            self.spritesheet.draw()
            if gldrawable.is_double_buffered():
                gldrawable.swap_buffers()
            else:
                glFlush()
            
            gldrawable.gl_end()

            glcontext = gtk.gtkgl.widget_get_gl_context(self.preview_gl)
            gldrawable = gtk.gtkgl.widget_get_gl_drawable(self.preview_gl)
            gldrawable.gl_begin(glcontext)
            self.preview = Animated(filename)
            gldrawable.gl_end()

            self.builder.get_object("action").set_sensitive(True)
            self.builder.get_object("preview_frame").set_sensitive(True)

    def setup_gl(self, drawing, event):
        glcontext = gtk.gtkgl.widget_get_gl_context(drawing)
        gldrawable = gtk.gtkgl.widget_get_gl_drawable(drawing)

        w, h = drawing.get_window().get_size()

        gldrawable.gl_begin(glcontext)
        
        glClearColor(0.0,0.0,0.0,0.0)
        glClear(GL_COLOR_BUFFER_BIT)
        glViewport (0, 0, w, h)
        glMatrixMode (GL_PROJECTION)
        glLoadIdentity ()
        glOrtho (0.0, w, 0.0, h, -1.0, 1.0)
        glMatrixMode (GL_MODELVIEW)
        glLoadIdentity ()

        gldrawable.gl_end()

    def expose(self, drawing, event, data):
        w, h = drawing.get_window().get_size()

        glcontext = gtk.gtkgl.widget_get_gl_context(drawing)
        gldrawable = gtk.gtkgl.widget_get_gl_drawable(drawing)
        gldrawable.gl_begin(glcontext)
        
        glViewport (0, 0, w, h)
        glMatrixMode (GL_PROJECTION)
        glLoadIdentity ()
        glOrtho (0.0, w, 0.0, h, -1.0, 1.0)
        glMatrixMode (GL_MODELVIEW)
        glLoadIdentity ()

        if gldrawable.is_double_buffered():
            gldrawable.swap_buffers()
        else:
            glFlush()

        gldrawable.gl_end()
        
        self.draw()

        return True

    def open_sprite_dialog(self, event):
        r = self.sprite_dialog.run()
        if r == gtk.RESPONSE_ACCEPT:
            f = self.sprite_dialog.get_filename()
            self.load_spritesheet(f)
        else:
            pass
        self.sprite_dialog.hide()

    def open_sprdata_dialog(self, event):
        r = self.load_sprdata_dialog.run()
        if r == gtk.RESPONSE_ACCEPT:
            f = self.load_sprdata_dialog.get_filename()
            self.sprite = load_data(f)
            self.preview.set_data(self.sprite)
            for action in self.sprite.frames:
                self.select_action.append_text(action)
                self.builder.get_object("adjustmentf").set_upper(len(action)-1)
        self.load_sprdata_dialog.hide()

    def new_action_dialog(self, event):
        r = self.new_action_dialog.run()
        if r == gtk.RESPONSE_ACCEPT:
            action_name = self.new_action_name.get_text()
            if action_name:
                num_frames = self.builder.get_object("number_frames").get_value_as_int()
                self.sprite.new_action(action_name, num_frames)
                self.select_action.append_text(action_name)
            else:
                print "inappropriate action name"
        else:
            pass
        self.new_action_dialog.hide()

    def save_as_dialog(self, event):
        dialog = self.builder.get_object("save_as_dialog")
        r = dialog.run()
        if r == gtk.RESPONSE_ACCEPT:
            filename = dialog.get_filename()
            if filename[-4:] != ".spr":
                filename = filename + ".spr"
            save_sprite(filename, self.sprite)
        else:
            pass
        dialog.hide()

    def close_sprite_dialog(self, event):
        self.sprite_dialog.response(gtk.RESPONSE_CANCEL)

    def load_sprite(self, event):
        self.sprite_dialog.response(gtk.RESPONSE_ACCEPT)
        
    def load_sprdata_dialog(self, event):
        self.load_sprdata_dialog.response(gtk.RESPONSE_ACCEPT)

    def close_sprdata_dialog(self, event):
        self.load_sprdata_dialog.response(gtk.RESPONSE_CANCEL)

    def close_save_as(self, event):
        self.load_sprdata_dialog.response(gtk.RESPONSE_CANCEL)

    def save_as(self, event):
        self.load_sprdata_dialog.response(gtk.RESPONSE_ACCEPT)

    def enable_directions(self):
        self.select_facing.append_text("N")
        self.select_facing.append_text("S")
        self.select_facing.append_text("E")
        self.select_facing.append_text("W")

    def save_frame(self, button):
        x = self.x_button.get_value()
        y = self.y_button.get_value()
        w = self.w_button.get_value()
        h = self.h_button.get_value()

        data = FrameData()
        data.set_pos((x,y))
        data.set_dim((w,h))
        action = self.select_action.get_active_text()
        facing = self.select_facing.get_active_text()
        frame = self.frame_button.get_value_as_int()

        facing = convert(facing)

        self.sprite.set_frame(action,facing,frame,data)
        self.preview.set_data(self.sprite)
        self.preview.set_action(action)
        self.preview.set_facing(facing)
        self.preview.set_current_frame(frame)
        self.show_preview = True

    def enable_save_frame(self, cb, data):
        if self.select_action.get_active_text() and self.select_facing.get_active_text():
            save_frame = self.builder.get_object("save_frame")
            save_frame.set_sensitive(True)

    def toggle_play(self, button):
        if self.mode == PLAY:
            self.mode = STOP
            button.set_label("Play")
            self.builder.get_object("preview_frame").set_sensitive(True)
        else:
            self.mode = PLAY
            self.builder.get_object("preview_frame").set_sensitive(False)
            button.set_label("Stop")

    def set_preview_frame(self, button):
        try:
            self.preview.set_current_frame(button.get_value_as_int())
            self.show_preview = True
            self.draw_preview(None)
        except AttributeError:
            self.show_preview = False

    # Put frame values into the spinners
    def copy_frame(self, button=None):
        frame_number = self.frame_button.get_value_as_int()
        action = self.select_action.get_active_text()
        facing = self.select_facing.get_active_text()
        t = self.sprite.frames[action][convert(facing)][frame_number].get_tuple()
        if t:
            x,y,w,h = t
            self.x_button.set_value(x) 
            self.y_button.set_value(y)
            self.w_button.set_value(w)
            self.h_button.set_value(h)

def convert(facing):
    if facing == "N":
        return N
    elif facing == "S":
        return S
    elif facing == "E":
        return E
    elif facing == "W":
        return W
    else:
        try:
            raise ConvertError(facing)
        except ConvertError as c:
            print c.value, "not a valid direction label."

def save_sprite(filename, sprite):
    F = open(filename, "w")
    pickle.dump(sprite, F)

def load_data(filename):
    F = open(filename, "r")
    return pickle.load(F)

class ConvertError(Exception):
    def __init__(self, value):
        self.value = value

def run():
    editor = EditorWindow()
    editor.window.show()
    editor.window2.show()

    gtk.main()
