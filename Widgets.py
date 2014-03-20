#!/usr/bin/env python
# -*- coding: utf-8 -*-

#   Widgets.py por:
#   Cristian García <cristian99garcia@gmail.com>

import os

import gtk
#from gi.repository import gtk.gdk.Pixbuf
import gobject


class Toolbar(gtk.Toolbar):

    __gsignals__ = {
        'save': (gobject.SIGNAL_RUN_FIRST, None, []),
        'new-variable': (gobject.SIGNAL_RUN_FIRST, None, []),
        'new-column': (gobject.SIGNAL_RUN_FIRST, None, []),
        'settings-dialog': (gobject.SIGNAL_RUN_FIRST, None, []),
        'change-plot': (gobject.SIGNAL_RUN_FIRST, None, []),
        'remove-column': (gobject.SIGNAL_RUN_FIRST, None, []),

        }

    def __init__(self):

        gtk.Toolbar.__init__(self)

        self.lista = [
            'torta', 'barras horizontales', 'barras verticales',
            'puntos', 'anillo'
            ]

        boton_configuraciones = gtk.ToolButton(gtk.STOCK_PREFERENCES)
        boton_guardar = gtk.ToolButton(gtk.STOCK_SAVE)
        boton_variable = gtk.ToolButton(gtk.STOCK_ADD)
        boton_columna = gtk.ToolButton(gtk.STOCK_ADD)
        boton_borrar = gtk.ToolButton(gtk.STOCK_REMOVE)
        modelo = gtk.ListStore(gtk.gdk.Pixbuf, str)
        renderer_pixbuf = gtk.CellRendererPixbuf()
        renderer_text = gtk.CellRendererText()
        item1 = gtk.ToolItem()
        item2 = gtk.ToolItem()
        item3 = gtk.ToolItem()

        boton_guardar.set_tooltip_text('Guardar gráfica en un archivo, todos los cambios posteriores serán guardados automáticamente')
        boton_variable.set_tooltip_text('Crear nueva variable')
        boton_columna.set_tooltip_text('Agregar columna a las variables')
        boton_borrar.set_tooltip_text('Borrar la columna seleccionada')
        boton_borrar.set_sensitive(False)

        for x in self.lista:
            if ' ' in x:
                nombre = x.split(' ')[-1]
            
            else:
                nombre = x

            direccion = os.path.join(os.path.dirname(__file__), 'images/' + nombre + '.png')
            imagen = gtk.Image()
            imagen.set_from_file(direccion)
            pix = imagen.get_pixbuf() #gtk.gdk.Pixbuf.new_from_file_at_size(direccion, 20, 20)
            modelo.append([pix, x])

        self.combo_graficas = gtk.ComboBox(model=modelo)
        self.combo_borrar = gtk.combo_box_new_text() #gtk.ComboBoxText()
        self.combo_borrar.boton = boton_borrar

        self.combo_graficas.pack_start(renderer_pixbuf, False)
        self.combo_graficas.pack_start(renderer_text, False)
        self.combo_borrar.append_text('Columna 1')

        self.combo_graficas.add_attribute(renderer_pixbuf, 'pixbuf', 0)
        self.combo_graficas.add_attribute(renderer_text ,'text', 1)

        self.combo_borrar.set_active(0)
        self.combo_borrar.set_sensitive(False)
        self.combo_graficas.set_active(0)

        boton_guardar.connect('clicked', lambda x: self.emit('save'))
        boton_variable.connect('clicked', lambda x: self.emit('new-variable'))
        boton_columna.connect('clicked', lambda x: self.emit('new-column'))
        boton_configuraciones.connect('clicked', lambda x: self.emit('settings-dialog'))
        self.combo_graficas.connect('changed', lambda x: self.emit('change-plot'))
        boton_borrar.connect('clicked', lambda x: self.emit('remove-column'))

        item1.add(gtk.Label('Gráfica de: '))
        item2.add(self.combo_graficas)
        item3.add(self.combo_borrar)
        self.add(boton_configuraciones)
        self.add(gtk.SeparatorToolItem())
        self.add(boton_guardar)
        self.add(gtk.SeparatorToolItem())
        self.add(boton_variable)
        self.add(boton_columna)
        #self.add(gtk.Label('Gráfica de:  '))
        #self.add(self.combo_graficas)
        #self.add(self.combo_borrar)
        self.add(item1)
        self.add(item2)
        self.add(item3)
        self.add(boton_borrar)

        #self.actualizar_combo_borrar()

        #self.set_show_close_button(True)

    def get_plot_combo(self):

        return self.combo_graficas

    def get_background_combo(self):

        return self.combo_colores


class PlotArea(gtk.Image):

    def __init__(self):

        gtk.Image.__init__(self)

    def set_plot(self, filename):

        if os.path.exists(filename):
            self.set_from_file(filename)


class SettingsDialog(gtk.Dialog):

    __gsignals__ = {
        'settings-changed': (gobject.SIGNAL_RUN_FIRST, None, [object]),
        }

    def __init__(self, dicc):

        gtk.Dialog.__init__(self)

        self.diccionario = dicc
        self.listbox = gtk.VBox() # gtk.ListBox()

        self.set_modal(True)
        self.set_title('Configuraciones')
        self.set_resizable(False)
        #self.listbox.set_selection_mode(gtk.SelectionMode.NONE)

        #row = gtk.ListBoxRow()
        hbox = gtk.HBox()
        spin_x = gtk.SpinButton()
        spin_y = gtk.SpinButton()
        adj_x = gtk.Adjustment(dicc['tamanyo_x'], 50, 5000, 1, 10, 0)
        adj_y = gtk.Adjustment(dicc['tamanyo_y'], 50, 5000, 1, 10, 0)

        spin_x.set_adjustment(adj_x)
        spin_x.set_value(dicc['tamanyo_x'])
        spin_x.connect('value-changed', self.set_var_spin, 'tamanyo_x')

        spin_y.set_adjustment(adj_y)
        spin_y.set_value(dicc['tamanyo_y'])
        spin_y.connect('value-changed', self.set_var_spin, 'tamanyo_y')

        hbox.pack_start(gtk.Label('Tamaño de la gráfica:'),
            False, False, 10)
        hbox.pack_end(spin_y, False, False, 0)
        hbox.pack_end(spin_x, False, False, 10)

        #row.add(hbox)
        #self.listbox.add(row)
        self.listbox.pack_start(hbox, False, False, 5)

        #row = gtk.ListBoxRow()
        hbox = gtk.HBox()
        spin = gtk.SpinButton()
        adj = gtk.Adjustment(dicc['borde'], 0, 200, 1, 10, 0)

        spin.set_adjustment(adj)
        spin.set_value(dicc['borde'])
        spin.set_tooltip_text('Esta opción solo se habilitará, cuando esté seleccionada la "Gráfica de anillo"')
        spin.connect('value-changed', self.set_var_spin, 'borde')

        hbox.pack_start(gtk.Label('Borde'), False, False, 10)
        hbox.pack_end(spin, False, False, 0)

        #row.add(hbox)
        #self.listbox.add(row)
        self.listbox.pack_start(hbox, False, False, 5)

        #row = gtk.ListBoxRow()
        hbox = gtk.HBox()
        spin = gtk.SpinButton()
        adj = gtk.Adjustment(dicc['inner_radius'], 0.1, 0.9, 0.1, 0)

        spin.set_digits(1)
        spin.set_adjustment(adj)
        spin.set_sensitive(dicc['grafica'] == 'Gráfica de anillo')
        spin.set_value(dicc['inner_radius'])
        spin.set_tooltip_text('Esta opción solo estará habilitada si la gráfica seleccionada es la "Gráfica de anillo"')

        spin.connect('value-changed', self.set_var_spin, 'inner_radius')

        hbox.pack_start(gtk.Label('Tamaño del centro de la gráfica de anillo'), False, False, 0)
        hbox.pack_start(spin, True, True, 0)

        #row.add(hbox)
        #self.listbox.add(row)
        self.listbox.pack_start(hbox, False, False, 5)

        #row = gtk.ListBoxRow()
        hbox = gtk.HBox()
        adj = gtk.Adjustment(dicc['fondo'][0], 0.0, 1.0, 0.1, 0)
        scale = gtk.HScale(adjustment=adj)
        
        scale.connect('value-changed', self.set_background, 'r')

        hbox.pack_start(gtk.Label('Cantidad de rojo en el fondo: '), False, False, 10)
        hbox.pack_end(scale, True, True, 0)

        #row.add(hbox)
        #self.listbox.add(row)
        self.listbox.pack_start(hbox, False, False, 5)

        #row = gtk.ListBoxRow()
        hbox = gtk.HBox()
        adj = gtk.Adjustment(dicc['fondo'][1], 0.0, 1.0, 0.1, 0)
        scale = gtk.HScale(adjustment=adj)
        
        scale.connect('value-changed', self.set_background, 'g')

        hbox.pack_start(gtk.Label('Cantidad de verde en el fondo: '), False, False, 10)
        hbox.pack_end(scale, True, True, 0)

        #row.add(hbox)
        #self.listbox.add(row)
        self.listbox.pack_start(hbox, False, False, 5)

        #row = gtk.ListBoxRow()
        hbox = gtk.HBox()
        adj = gtk.Adjustment(dicc['fondo'][2], 0.0, 1.0, 0.1, 0)
        scale = gtk.HScale(adjustment=adj)
        
        scale.connect('value-changed', self.set_background, 'b')

        hbox.pack_start(gtk.Label('Cantidad de azúl en el fondo: '), False, False, 10)
        hbox.pack_end(scale, True, True, 0)
        
        #row.add(hbox)
        #self.listbox.add(row)
        self.listbox.pack_start(hbox, False, False, 5)

        s_ejes = self.hbox_with_switch('Presencia de los ejes', dicc['axis'], dicc['grafica'] == 'Gráfica de puntos')
        s_esquinas = self.hbox_with_switch('Bordes redondeados', dicc['rounded_corners'], dicc['grafica'] in ['Gráfica de barras verticales', 'Gráfica de barras horizontales'])
        s_esquinas = self.hbox_with_switch('Mostrar valores', dicc['display_values'], dicc['grafica'] in ['Gráfica de barras verticales', 'Gráfica de barras horizontales'])
        s_cuadricula = self.hbox_with_switch('Mostrar Cuadricula', dicc['rounded_corners'], dicc['grafica'] in ['Gráfica de puntos', 'Gráfica de barras verticales', 'Gráfica de barras horizontales'])

        s_ejes.connect('notify::active', self.set_var_switch, 'axis')
        s_esquinas.connect('notify::active', self.set_var_switch, 'rounded_corners')
        s_cuadricula.connect('notify::active', self.set_var_switch, 'gird')

        hbox = gtk.HBox()
        boton = gtk.Button(stock=gtk.STOCK_CLOSE)
        
        boton.connect('clicked', lambda x: self.destroy())

        hbox.pack_end(boton, False, False, 0)
        self.vbox.pack_end(hbox, False, False, 0)

        self.vbox.pack_start(self.listbox, True, True, 10)

    def hbox_with_switch(self, label, variable, ifvar):

        #row = gtk.HBox()
        hbox = gtk.HBox()
        switch = gtk.CheckButton()

        switch.set_active(variable)
        switch.set_use_action_appearance(True)
        #row.set_sensitive(ifvar)
        hbox.set_sensitive(ifvar)

        if label == 'Presencia de los ejes':
            switch.set_tooltip_text('Esta opción solo se habilitará si está seleccionada la "Gráfica de puntos"')

        elif label == 'Bordes redondeados' or label == 'Mostrar valores':
            switch.set_tooltip_text('Esta opción solo se habilitará si está seleccionada una gráfica de barras(horizontales o vérticales)')

        elif label == 'Mostrar Cuadricula':
            switch.set_tooltip_text('Esta opción solo estará habilitada si la gráfica seleccionada, está entre las siguientes opciones: "Gráfica de puntos", "Gráfica de barras verticales" o la "Gráfica de barras horizontales')

        hbox.pack_start(gtk.Label(label), False, False, 0)
        hbox.pack_end(switch, False, False, 0)

        #row.add(hbox)
        #self.listbox.add(row)
        self.listbox.pack_start(hbox, False, False, 5)

        return switch

    def set_var_spin(self, widget, variable):

        self.diccionario[variable] = widget.get_value()
        self.emit('settings-changed', self.diccionario)

    def set_var_switch(self, widget, gparam, variable):

        self.diccionario[variable] = widget.get_active()
        self.emit('settings-changed', self.diccionario)

    def set_background(self, widget, color):
        
        actual = self.diccionario['fondo']
        cantidad = widget.get_value()

        if color == 'r':
            color = (cantidad,) + actual[1:]

        elif color == 'g':
            color = actual[:1] + (cantidad,) + actual[2:]

        elif color == 'b':
            color =  actual[:2] + (cantidad,)

        self.diccionario['fondo'] = color
        
        self.emit('settings-changed', self.diccionario)


class SaveFilesDialog(gtk.FileChooserDialog):
    
    __gsignals__ = {
        'save-file': (gobject.SIGNAL_RUN_FIRST, None, [str]),
        }
    
    def __init__(self):
        
        gtk.FileChooserDialog.__init__(self)

        self.add_buttons(gtk.STOCK_CANCEL, gtk.ResponseType.CANCEL, gtk.STOCK_SAVE, gtk.ResponseType.ACCEPT)

        self.set_modal(True)
        self.set_title('Guardar gráfica')
        self.set_current_folder(os.path.expanduser('~/'))
        self.set_action(gtk.FileChooserAction.SAVE)

        self.boton_guardar = self.get_children()[0].get_children()[1].get_children()[0]
        self.boton_cancelar = self.get_children()[0].get_children()[1].get_children()[1]

        self.boton_guardar.connect('clicked', self.file_save)
        self.boton_cancelar.connect('clicked', lambda x: self.destroy())
    
        self.show_all()

    def file_save(self, widget, reemplazar=False):
        
        direccion = self.get_uri()
        direccion = direccion.split('file://')[1]

        if not direccion.endswith('.png'):
            direccion += '.png'

        if not os.path.exists(direccion) or reemplazar:
            self.emit('save-file', direccion)
            self.destroy()
        
        else:
            dialogo = gtk.Dialog()
            vbox = dialogo.get_content_area()
            hbox = gtk.HBox()
            boton_si = gtk.Button.new_from_stock(gtk.STOCK_YES)
            boton_no = gtk.Button.new_from_stock(gtk.STOCK_NO)

            dialogo.set_transient_for(self)
            dialogo.set_modal(True)
            dialogo.set_title('El archivo seleccionado ya existe')
            
            boton_si.connect('clicked', self.file_save, True)
            boton_si.connect('clicked', lambda x: dialogo.destroy())
            boton_no.connect('clicked', lambda x: dialogo.destroy())

            hbox.pack_start(boton_si, False, False, 20)
            hbox.pack_start(boton_no, False, False, 0)
            vbox.pack_start(gtk.Label('¿Desea reemplazarlo?'), False, False, 10)
            vbox.pack_start(hbox, False, False, 0)
            
            dialogo.show_all()
