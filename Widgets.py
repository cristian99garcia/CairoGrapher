#!/usr/bin/env python
# -*- coding: utf-8 -*-

#   Widgets.py por:
#   Cristian García <cristian99garcia@gmail.com>

from gi.repository import Gtk
from gi.repository import GObject


class Toolbar(Gtk.HeaderBar):

    __gsignals__ = {
        'save': (GObject.SIGNAL_RUN_FIRST, None, []),
        'new-variable': (GObject.SIGNAL_RUN_FIRST, None, []),
        'new-column': (GObject.SIGNAL_RUN_FIRST, None, []),
        'settings-dialog': (GObject.SIGNAL_RUN_FIRST, None, []),
        'change-plot': (GObject.SIGNAL_RUN_FIRST, None, []),
        'remove-column': (GObject.SIGNAL_RUN_FIRST, None, []),
        'background-changed': (GObject.SIGNAL_RUN_FIRST, None, []),

        }

    def __init__(self):

        Gtk.HeaderBar.__init__(self)

        self.lista = [
            'torta', 'barras horizontales', 'barras verticales',
            'puntos', 'anillo'
            ]

        self.fondos = [
            'Blanco', 'Negro', 'Rojo', 'Azúl', 'Verde',
            'Amalliro', 'Naranja'
            ]

        boton_configuraciones = Gtk.ToolButton(Gtk.STOCK_PREFERENCES)
        boton_guardar = Gtk.ToolButton(Gtk.STOCK_SAVE)
        boton_variable = Gtk.ToolButton(Gtk.STOCK_ADD)
        boton_columna = Gtk.ToolButton(Gtk.STOCK_ADD)
        boton_borrar = Gtk.ToolButton(Gtk.STOCK_REMOVE)
        self.combo_graficas = Gtk.ComboBoxText()
        self.combo_borrar = Gtk.ComboBoxText()
        self.combo_borrar.boton = boton_borrar
        self.combo_colores = Gtk.ComboBoxText()

        boton_guardar.set_tooltip_text('Guardar gráfica en un archivo, todos los cambios posteriores serán guardados automáticamente')
        boton_variable.set_tooltip_text('Crear nueva variable')
        boton_columna.set_tooltip_text('Agregar columna a las variables')
        boton_borrar.set_tooltip_text('Borrar la columna seleccionada')
        self.combo_colores.set_tooltip_text('Color del fondo de la gráfica')

        for x in self.lista:
            self.combo_graficas.append_text(x)

        for x in self.fondos:
            self.combo_colores.append_text(x)

        self.combo_graficas.set_active(0)
        self.combo_colores.set_active(0)

        boton_guardar.connect('clicked', lambda x: self.emit('save'))
        boton_variable.connect('clicked', lambda x: self.emit('new-variable'))
        boton_columna.connect('clicked', lambda x: self.emit('new-column'))
        boton_configuraciones.connect('clicked', lambda x: self.emit('settings-dialog'))
        self.combo_graficas.connect('changed', lambda x: self.emit('change-plot'))
        boton_borrar.connect('clicked', lambda x: self.emit('remove-column'))
        self.combo_colores.connect('changed', lambda x: self.emit('background-changed'))

        self.add(boton_configuraciones)
        self.add(Gtk.SeparatorToolItem())
        self.add(boton_guardar)
        self.add(Gtk.SeparatorToolItem())
        self.add(boton_variable)
        self.add(boton_columna)
        self.add(Gtk.Label(label='Gráfica de:  '))
        self.add(self.combo_graficas)
        self.add(self.combo_borrar)
        self.add(boton_borrar)
        self.add(Gtk.SeparatorToolItem())
        self.add(Gtk.Label('Color del fondo: '))
        self.add(self.combo_colores)

        #self.actualizar_combo_borrar()

        self.set_show_close_button(True)

    def get_plot_combo(self):

        return self.combo_graficas

    def get_background_combo(self):

        return self.combo_colores