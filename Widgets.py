#!/usr/bin/env python
# -*- coding: utf-8 -*-

#   Widgets.py por:
#   Cristian García <cristian99garcia@gmail.com>

import os

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


class PlotArea(Gtk.Image):

    def __init__(self):

        Gtk.Image.__init__(self)

    def set_plot(self, filename):

        if os.path.exists(filename):
            self.set_from_file(filename)


class SettingsDialog(Gtk.Dialog):

    __gsignals__ = {
        'settings-changed': (GObject.SIGNAL_RUN_FIRST, None, [object]),
        }

    def __init__(self, dicc):

        Gtk.Dialog.__init__(self)

        self.diccionario = dicc
        self.listbox = Gtk.ListBox()

        self.set_modal(True)
        self.set_title('Configuraciones')
        self.set_resizable(False)
        self.listbox.set_selection_mode(Gtk.SelectionMode.NONE)

        row = Gtk.ListBoxRow()
        hbox = Gtk.HBox()
        spin_x = Gtk.SpinButton()
        spin_y = Gtk.SpinButton()
        adj_x = Gtk.Adjustment(dicc['tamanyo_x'], 50, 5000, 1, 10, 0)
        adj_y = Gtk.Adjustment(dicc['tamanyo_y'], 50, 5000, 1, 10, 0)

        spin_x.set_adjustment(adj_x)
        spin_x.set_value(dicc['tamanyo_x'])
        spin_x.connect('value-changed', self.set_var_spin, 'tamanyo_x')

        spin_y.set_adjustment(adj_y)
        spin_y.set_value(dicc['tamanyo_y'])
        spin_y.connect('value-changed', self.set_var_spin, 'tamanyo_y')

        hbox.pack_start(Gtk.Label(label='Tamaño de la gráfica:'),
            False, False, 10)
        hbox.pack_end(spin_y, False, False, 0)
        hbox.pack_end(spin_x, False, False, 10)

        row.add(hbox)
        self.listbox.add(row)

        row = Gtk.ListBoxRow()
        hbox = Gtk.HBox()
        spin = Gtk.SpinButton()
        adj = Gtk.Adjustment(dicc['borde'], 0, 200, 1, 10, 0)

        spin.set_adjustment(adj)
        spin.set_value(dicc['borde'])
        spin.set_tooltip_text('Esta opción solo se habilitará, cuando esté seleccionada la "Gráfica de anillo"')
        spin.connect('value-changed', self.set_var_spin, 'borde')

        hbox.pack_start(Gtk.Label(label='Borde'), False, False, 10)
        hbox.pack_end(spin, False, False, 0)

        row.add(hbox)
        self.listbox.add(row)

        row = Gtk.ListBoxRow()
        hbox = Gtk.HBox()
        spin = Gtk.SpinButton()
        adj = Gtk.Adjustment(dicc['inner_radius'], 0.1, 0.9, 0.1, 0)

        spin.set_digits(1)
        spin.set_adjustment(adj)
        spin.set_sensitive(dicc['grafica'] == 'Gráfica de anillo')
        spin.set_value(dicc['inner_radius'])
        spin.set_tooltip_text('Esta opción solo estará habilitada si la gráfica seleccionada es la "Gráfica de anillo"')

        spin.connect('value-changed', self.set_var_spin, 'inner_radius')

        hbox.pack_start(Gtk.Label(
            label='Tamaño del centro de la gráfica de anillo'), False, False, 0)
        hbox.pack_start(spin, True, True, 0)

        row.add(hbox)
        self.listbox.add(row)

        s_ejes = self.hbox_with_switch('Presencia de los ejes', dicc['axis'], dicc['grafica'] == 'Gráfica de puntos')
        s_esquinas = self.hbox_with_switch('Bordes redondeados', dicc['rounded_corners'], dicc['grafica'] in ['Gráfica de barras verticales', 'Gráfica de barras horizontales'])
        s_esquinas = self.hbox_with_switch('Mostrar valores', dicc['display_values'], dicc['grafica'] in ['Gráfica de barras verticales', 'Gráfica de barras horizontales'])
        s_cuadricula = self.hbox_with_switch('Mostrar Cuadricula', dicc['rounded_corners'], dicc['grafica'] in ['Gráfica de puntos', 'Gráfica de barras verticales', 'Gráfica de barras horizontales'])

        #s_ejes.connect('notify::active', self.__set_axis)
        #s_esquinas.connect('notify::active', self.__set_rounded_corners)
        #s_cuadricula.connect('notify::active', self.__set_gird)

        self.vbox.pack_start(self.listbox, True, True, 10)
        #dialogo.show_all()


    def hbox_with_switch(self, label, variable, ifvar):

        row = Gtk.HBox()
        hbox = Gtk.HBox()
        switch = Gtk.Switch()

        switch.set_active(variable)
        switch.set_use_action_appearance(True)
        row.set_sensitive(ifvar)

        if label == 'Presencia de los ejes':
            switch.set_tooltip_text('Esta opción solo se habilitará si está seleccionada la "Gráfica de puntos"')

        elif label == 'Bordes redondeados' or label == 'Mostrar valores':
            switch.set_tooltip_text('Esta opción solo se habilitará si está seleccionada una gráfica de barras(horizontales o vérticales)')

        elif label == 'Mostrar Cuadricula':
            switch.set_tooltip_text('Esta opción solo estará habilitada si la gráfica seleccionada, está entre las siguientes opciones: "Gráfica de puntos", "Gráfica de barras verticales" o la "Gráfica de barras horizontales')

        hbox.pack_start(Gtk.Label(label=label), False, False, 0)
        hbox.pack_end(switch, False, False, 0)

        row.add(hbox)
        self.listbox.add(row)

        return switch

    def set_var_spin(self, widget, variable):

        self.diccionario[variable] = widget.get_value()

        self.emit('settings-changed', self.diccionario)