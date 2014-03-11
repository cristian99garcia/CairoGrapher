#!/usr/bin/env python
# -*- coding: utf-8 -*-

#   CairoGrapher.py por:
#   Cristian García <cristian99garcia@gmail.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

import os
import random
import CairoPlot

from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GObject


class CairoGrapher(Gtk.Window):

    __gsignals__ = {
        'reload': (GObject.SIGNAL_RUN_FIRST, None, []),
            }

    def __init__(self):

        Gtk.Window.__init__(self)

        self.cargar_configuracion()

        self.vbox = Gtk.VBox()
        self._vbox = Gtk.VBox()
        self.paned = Gtk.HPaned()
        self.area = Gtk.Image()
        self.barra = self.crear_barra()

        scrolled = Gtk.ScrolledWindow()

        self.crear_scrolled_variables()
        self.crear_grafica()

        if os.path.exists(os.path.expanduser('~/' + self.nombre + '.png')):
            self.area.set_from_file(os.path.expanduser(
                '~/' + self.nombre + '.png'))

        self.connect('reload', self.__recargar)
        self.connect('reload', self.actualizar_combo_borrar, self.combo_borrar)
        self.connect('delete-event', self.salir)

        scrolled.add(self.area)
        self.paned.pack1(scrolled, 300, -1)
        self.paned.pack2(self._vbox)
        self.vbox.pack_start(self.paned, True, True, 0)

        self.add(self.vbox)
        self.show_all()

    def actualizar_combo_borrar(self, *args):

        if self.l_valores:
            columnas = len(self.valores[self.l_valores[0]])

            self.combo_borrar.remove_all()

            for x in range(1, columnas + 1):
                self.combo_borrar.append_text('Columna ' + str(x))

            self.combo_borrar.set_active(0)
            self.combo_borrar.set_sensitive(columnas > 1)
            self.combo_borrar.boton.set_sensitive(columnas > 1)

        else:
            self.combo_borrar.set_sensitive(False)
            self.combo_borrar.boton.set_sensitive(False)

    def crear_barra(self):

        toolbar = Gtk.HeaderBar()

        lista = [
            'torta', 'barras horizontales', 'barras verticales',
            'puntos', 'anillo'
            ]

        boton_configuraciones = Gtk.ToolButton(Gtk.STOCK_PREFERENCES)
        boton_guardar = Gtk.ToolButton(Gtk.STOCK_SAVE)
        boton_agregar = Gtk.ToolButton(Gtk.STOCK_ADD)
        boton_aniadir = Gtk.ToolButton(Gtk.STOCK_ADD)
        boton_borrar = Gtk.ToolButton(Gtk.STOCK_REMOVE)
        combo_graficas = Gtk.ComboBoxText()
        self.combo_borrar = Gtk.ComboBoxText()
        self.combo_borrar.boton = boton_borrar
        combo_colores = Gtk.ComboBoxText()
        separador = Gtk.SeparatorToolItem()
        #stop_button = StopButton(self)
        item1 = Gtk.ToolItem()
        item2 = Gtk.ToolItem()
        item3 = Gtk.ToolItem()
        item4 = Gtk.ToolItem()
        _hbox = Gtk.HBox()

        boton_guardar.set_tooltip_text('Guardar gráfica en un archivo, todos los cambios posteriores serán guardados automáticamente')
        boton_agregar.set_tooltip_text('Crear nueva variable')
        boton_aniadir.set_tooltip_text('Agregar columna a las variables')
        boton_borrar.set_tooltip_text('Borrar la columna seleccionada')
        separador.set_draw(False)
        separador.set_expand(True)
        combo_colores.set_tooltip_text('Color del fondo de la gráfica')

        for x in lista:
            combo_graficas.append_text(x)

        for x in self.fondos:
            combo_colores.append_text(x)

        combo_graficas.set_active(0)
        combo_colores.set_active(0)

        boton_guardar.connect('clicked', self.guardar_archivo)
        boton_agregar.connect('clicked', self.crear_variable)
        boton_agregar.connect('clicked', self.actualizar_combo_borrar)
        boton_aniadir.connect('clicked', self.aniadir_a_variable)
        boton_configuraciones.connect('clicked', self.dialogo_configuraciones)
        combo_graficas.connect('changed', self.cambiar_tipo)
        boton_borrar.connect('clicked', self.borrar_columna)
        boton_borrar.connect('clicked', self.actualizar_combo_borrar)
        combo_colores.connect('changed', self.__set_background)

        _hbox.pack_start(self.combo_borrar, False, False, 0)

        item1.add(Gtk.Label(label='Gráfica de:  '))
        item2.add(combo_graficas)
        item3.add(_hbox)
        item4.add(combo_colores)

        toolbar.add(boton_configuraciones)
        toolbar.add(Gtk.SeparatorToolItem())
        toolbar.add(boton_guardar)
        toolbar.add(Gtk.SeparatorToolItem())
        toolbar.add(boton_agregar)
        toolbar.add(boton_aniadir)
        toolbar.add(item1)
        toolbar.add(item2)
        toolbar.add(item3)
        toolbar.add(boton_borrar)
        toolbar.add(Gtk.SeparatorToolItem())
        toolbar.add(item4)
        toolbar.add(separador)

        self.actualizar_combo_borrar()

        toolbar.set_show_close_button(True)
        self.set_titlebar(toolbar)

        return toolbar

    def guardar_archivo(self, *args):

        dialogo = Gtk.FileChooserDialog(
            buttons=(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
            Gtk.STOCK_SAVE, Gtk.ResponseType.ACCEPT))

        dialogo.set_transient_for(self)
        dialogo.set_modal(True)
        dialogo.set_title('Guardar gráfica')
        dialogo.set_current_folder(os.path.expanduser('~/'))
        dialogo.set_action(Gtk.FileChooserAction.SAVE)

        respuesta = dialogo.run()

        if respuesta == Gtk.ResponseType.ACCEPT:
            direccion = dialogo.get_uri()
            direccion = direccion.split('file://')[1]

            if not direccion.endswith('.png'):
                direccion += '.png'

            self.direccion = direccion
            self.emit('reload')

        dialogo.destroy()

    def cambiar_tipo(self, combo):

        lista = [
        'torta', 'barras horizontales', 'barras verticales', 'puntos',
        'anillo'
        ]

        self.grafica = 'Gráfica de ' + lista[combo.get_active()]

        self.emit('reload')

    def dialogo_configuraciones(self, *args):

        def hbox_with_switch(label, variable, listbox, ifvar):

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
            listbox.add(row)

            return switch

        dialogo = Gtk.Dialog()
        vbox = dialogo.get_content_area()
        listbox = Gtk.VBox()

        dialogo.set_resizable(False)
        dialogo.set_transient_for(self)
        dialogo.set_modal(True)
        dialogo.set_title('Configuraciones')
        #listbox.set_selection_mode(Gtk.SelectionMode.NONE)

        row = Gtk.HBox()
        hbox = Gtk.HBox()
        spin_x = Gtk.SpinButton()
        spin_y = Gtk.SpinButton()
        adj_x = Gtk.Adjustment(self.tamanyo_x, 50, 5000, 1, 10, 0)
        adj_y = Gtk.Adjustment(self.tamanyo_y, 50, 5000, 1, 10, 0)

        spin_x.set_adjustment(adj_x)
        spin_x.set_value(self.tamanyo_x)
        spin_x.connect('value-changed', self.set_var_spin, 'self.tamanyo_x')

        spin_y.set_adjustment(adj_y)
        spin_y.set_value(self.tamanyo_y)
        spin_y.connect('value-changed', self.set_var_spin, 'self.tamanyo_y')

        hbox.pack_start(Gtk.Label(label='Tamaño de la gráfica:'),
            False, False, 10)
        hbox.pack_end(spin_y, False, False, 0)
        hbox.pack_end(spin_x, False, False, 10)

        row.add(hbox)
        listbox.add(row)

        row = Gtk.HBox()
        hbox = Gtk.HBox()
        spin = Gtk.SpinButton()
        adj = Gtk.Adjustment(self.borde, 0, 200, 1, 10, 0)

        spin.set_adjustment(adj)
        spin.set_value(self.borde)
        spin.set_tooltip_text('Esta opción solo se habilitará, cuando esté seleccionada la "Gráfica de anillo"')
        spin.connect('value-changed', self.set_var_spin, 'self.borde')

        hbox.pack_start(Gtk.Label(label='Borde'), False, False, 10)
        hbox.pack_end(spin, False, False, 0)

        row.add(hbox)
        listbox.add(row)

        row = Gtk.HBox()
        hbox = Gtk.HBox()
        spin = Gtk.SpinButton()
        adj = Gtk.Adjustment(self.inner_radius, 0.1, 0.9, 0.1, 0)

        spin.set_digits(1)
        spin.set_adjustment(adj)
        spin.set_sensitive(self.grafica == 'Gráfica de anillo')
        spin.set_value(self.inner_radius)
        spin.set_tooltip_text('Esta opción solo estará habilitada si la gráfica seleccionada es la "Gráfica de anillo"')

        spin.connect('value-changed', self.__set_inner_radius)

        hbox.pack_start(Gtk.Label(
            label='Tamaño del centro de la gráfica de anillo'), False, False, 0)
        hbox.pack_start(spin, True, True, 0)

        row.add(hbox)
        listbox.add(row)

        s_ejes = hbox_with_switch('Presencia de los ejes',
            self.axis, listbox, self.grafica == 'Gráfica de puntos')

        s_esquinas = hbox_with_switch('Bordes redondeados',
            self.rounded_corners, listbox, self.grafica in
            ['Gráfica de barras verticales', 'Gráfica de barras horizontales'])

        s_esquinas = hbox_with_switch('Mostrar valores',
            self.display_values, listbox, self.grafica in
            ['Gráfica de barras verticales', 'Gráfica de barras horizontales'])

        s_cuadricula = hbox_with_switch('Mostrar Cuadricula',
            self.rounded_corners, listbox, self.grafica in
            ['Gráfica de puntos', 'Gráfica de barras verticales',
                'Gráfica de barras horizontales'])

        s_ejes.connect('notify::active', self.__set_axis)
        s_esquinas.connect('notify::active', self.__set_rounded_corners)
        s_cuadricula.connect('notify::active', self.__set_gird)

        vbox.pack_start(listbox, True, True, 10)
        dialogo.show_all()

    def set_var_spin(self, widget, variable):

        exec(variable + ' = %d' % widget.get_value())
        self.emit('reload')

    def crear_grafica(self, grafica=None):

        if not grafica:
            grafica = self.grafica

        self.grafica = grafica
        pasar = False

        for x in self.l_valores:
            for i in self.valores[x]:
                if i >= 1:
                    pasar = True
                    break

        if not pasar and self.l_valores:
            self.valores[self.l_valores[0]] = [1]

        if grafica == 'Gráfica de barras horizontales':
            CairoPlot.horizontal_bar_plot(
                self.direccion,
                self.valores,
                self.tamanyo_x,
                self.tamanyo_y,
                background=self.fondo,
                border=self.borde,
                display_values=self.display_values,
                grid=self.cuadricula,
                rounded_corners=self.rounded_corners,
                stack=False,
                three_dimension=True,
                series_labels=None,
                x_labels=self.x_labels,
                y_labels=self.y_labels,
                x_bounds=None,
                y_bounds=None,
                colors=self.colores)

        elif grafica == 'Gráfica de barras verticales':
            CairoPlot.vertical_bar_plot(
                self.direccion,
                self.valores,
                self.tamanyo_x,
                self.tamanyo_y,
                background=self.fondo,
                border=self.borde,
                display_values=self.display_values,
                grid=self.cuadricula,
                rounded_corners=self.rounded_corners,
                stack=False,
                three_dimension=True,
                series_labels=None,
                x_labels=self.x_labels,
                y_labels=self.y_labels,
                x_bounds=None,
                y_bounds=None,
                colors=self.colores)

        elif grafica == 'Gráfica de torta':
            CairoPlot.pie_plot(
                self.direccion,
                self.valores,
                self.tamanyo_x,
                self.tamanyo_y,
                background=self.fondo,
                gradient=True,
                shadow=False,
                colors=self.colores)

        elif grafica == 'Gráfica de puntos':
            CairoPlot.dot_line_plot(
                self.direccion,
                self.valores,
                self.tamanyo_x,
                self.tamanyo_y,
                background=self.fondo,
                border=self.borde,
                axis=self.axis,
                dots=False,
                grid=self.cuadricula,
                series_legend=self.grupos,
                x_labels=self.x_labels,
                y_labels=self.y_labels,
                x_bounds=None,
                y_bounds=None,
                x_title=self.titulo_x,
                y_title=self.titulo_y,
                series_colors=self.colores)

        elif grafica == 'Gráfica de anillo':
            CairoPlot.donut_plot(
                self.direccion,
                self.valores,
                self.tamanyo_x,
                self.tamanyo_y,
                background=self.fondo,
                gradient=True,
                shadow=False,
                colors=self.colores,
                inner_radius=self.inner_radius)

        self.area.set_from_file(self.direccion)

    def transformar_valores_a_gantt(self):

        lista = []

        for x in self.l_valores:
            lista += [[()]]

            for i in self.valores[x]:
                lista[-1][-1] += (int(i),)

        return lista

    def borrar_columna(self, widget):

        columna = self.combo_borrar.get_active()

        if self.l_valores and len(self.valores[self.l_valores[0]]) >= columna:
            self.limpiar_vbox()

            for x in self.l_valores:
                lista = self.valores[x]
                lista = lista[:columna] + lista[columna + 1:]
                self.valores[x] = lista

            if not self.valores or self.valores[self.l_valores[0]] == []:
                for x in self.l_valores[1:]:
                    self.valores[x] = [0]

                self.valores[self.l_valores[0]] = [1]

            self.cargar_variables()

        self.actualizar_combo_borrar()
        self.show_all()

    def cargar_variables(self, actualizar=True):

        self.l_valores = self.ordenar_lista()
        lista = []
        self.colores += self.get_color()
        listbox = Gtk.ListBox()

        listbox.set_selection_mode(Gtk.SelectionMode.NONE)
        self.limpiar_vbox()

        for _x in self.l_valores:
            row = Gtk.ListBoxRow()
            hbox = Gtk.HBox()
            label = Gtk.Label(_x)
            entrada = Gtk.Entry()
            numero = 0

            self.widgets['Entrys'].append(entrada)

            entrada.connect('changed', self.cambiar_nombre_variable, label)

            entrada.set_text(_x)
            hbox.set_spacing(20)

            hbox.pack_start(entrada, False, False, 0)

            for x in self.valores[_x]:
                if len(self.valores) == 1 and len(self.valores[_x]) == 1:
                    _min = 1
                    self.valores[_x][0] = 1

                else:
                    _min = 0

                spin = Gtk.SpinButton()
                adj = Gtk.Adjustment(x, _min, 10000000, 1, 10, 0)
                spin.variable = _x

                spin.set_digits(1)
                spin.set_adjustment(adj)
                spin.set_value(x)

                spin.connect('value-changed', self.__change_value, numero)
                self.widgets['SpinButtons'].append(spin)
                hbox.pack_start(spin, False, False, 10)

                numero += 1

            color = self.colores[self.l_valores.index(_x)]

            boton_cerrar = Gtk.Button()
            boton_cerrar.img = Gtk.Image.new_from_stock(Gtk.STOCK_CLOSE, Gtk.IconSize.BUTTON)
            boton_mas = Gtk.Button()
            boton_mas.img = Gtk.Image.new_from_stock(Gtk.STOCK_ADD, Gtk.IconSize.BUTTON)
            hbox_mas = Gtk.HBox()
            r_adj = Gtk.Adjustment(color[0], 0.0, 1.0, 0.1, 0)
            g_adj = Gtk.Adjustment(color[1], 0.0, 1.0, 0.1)
            b_adj = Gtk.Adjustment(color[2], 0.0, 1.0, 0.1)
            r_scale = Gtk.Scale(
                orientation=Gtk.Orientation.VERTICAL, adjustment=r_adj)
            g_scale = Gtk.Scale(
                orientation=Gtk.Orientation.VERTICAL, adjustment=g_adj)
            b_scale = Gtk.Scale(
                orientation=Gtk.Orientation.VERTICAL, adjustment=b_adj)

            boton_cerrar.set_image(boton_cerrar.img)
            boton_mas.set_image(boton_mas.img)
            boton_mas.set_tooltip_text('Mostrar los controles de color')
            r_scale.set_value(color[0])
            g_scale.set_value(color[1])
            b_scale.set_value(color[2])
            r_scale.set_size_request(-1, 200)
            g_scale.set_size_request(-1, 200)
            b_scale.set_size_request(-1, 200)
            hbox_mas.set_size_request(-1, 200)

            boton_cerrar.connect('clicked', self.borrar_valor,
                self._vbox, label, entrada, spin)

            boton_mas.connect('clicked', self.mostrar, hbox_mas)
            r_scale.connect('value-changed', self.setear_color, 'Rojo', label)
            g_scale.connect('value-changed', self.setear_color, 'Verde', label)
            b_scale.connect('value-changed', self.setear_color, 'Azúl', label)

            hbox_mas.pack_start(r_scale, True, True, 5)
            hbox_mas.pack_start(g_scale, True, True, 5)
            hbox_mas.pack_start(b_scale, True, True, 5)

            lista.append(hbox_mas)

            self.widgets['ClouseButtons'].append(boton_cerrar)
            hbox.pack_end(boton_cerrar, False, False, 0)
            hbox.pack_end(hbox_mas, True, True, 0)
            hbox.pack_end(boton_mas, False, False, 10)
            row.add(hbox)
            listbox.add(row)
            self._vbox.pack_start(listbox, False, False, 10)

        if actualizar:
            self.emit('reload')
            self.show_all()

            for x in lista:
                x.hide()

    def mostrar(self, boton, widget):

        if widget.get_visible():
            imagen = Gtk.Image.new_from_stock(Gtk.STOCK_ADD,
                Gtk.IconSize.BUTTON)

            widget.hide()
            boton.set_image(imagen)
            boton.set_tooltip_text('Mostrar los controles de color')

        else:
            imagen = Gtk.Image.new_from_stock(Gtk.STOCK_REMOVE,
                Gtk.IconSize.BUTTON)

            widget.show_all()
            boton.set_image(imagen)
            boton.set_tooltip_text('Ocultar los controles de color')

    def setear_color(self, widget, label, frame):

        valor = self.l_valores[self.l_valores.index(frame.get_label())]
        cantidad = widget.get_value()

        if label == 'Rojo':
            self.colores[self.l_valores.index(valor)] = \
            (cantidad,) + self.colores[self.l_valores.index(valor)][1:]

        elif label == 'Verde':
            self.colores[self.l_valores.index(valor)] = \
            self.colores[self.l_valores.index(valor)][:1] + \
            (cantidad,) + self.colores[self.l_valores.index(valor)][2:]

        elif label == 'Azúl':
            self.colores[self.l_valores.index(valor)] = \
            self.colores[self.l_valores.index(valor)][:2] + (cantidad,)

        self.emit('reload')

    def borrar_valor(self, widget, vbox, frame, entrada, spin):

        vbox.remove(frame)
        del self.valores[frame.get_label()]
        self.l_valores = self.ordenar_lista()

        self.widgets['Entrys'].remove(entrada)
        self.widgets['SpinButtons'].remove(spin)
        self.widgets['ClouseButtons'].remove(widget)

        self.emit('reload')

    def cargar_configuracion(self):

        self.widgets = {'SpinButtons': [], 'Entrys': [], 'ClouseButtons': []}
        self.botones = []
        self.colores = []
        self.valores = {}
        self.fondos = ['Blanco', 'Negro', 'Rojo', 'Azúl', 'Verde',
            'Amalliro', 'Naranja']
        self.direccion = os.path.expanduser('~/Grafica.png')
        self.grafica = 'Gráfica de torta'
        self.nombre = 'Grafica'
        self.titulo_x = 'Gráfica'
        self.titulo_y = ''
        self.tamanyo_x = 600
        self.tamanyo_y = 600
        self.fondo = 'white light_gray'
        self.borde = 0
        self.display_values = False
        self.axis = True
        self.cuadricula = True
        self.grupos = True
        self.rounded_corners = True
        self.inner_radius = 0.3
        self.x_labels = []
        self.y_labels = []
        self.l_valores = self.ordenar_lista()

    def cambiar_nombre_variable(self, widget, frame):

        nombre_nuevo = widget.get_text()
        nombre_antiguo = frame.get_label()
        valores = self.valores[nombre_antiguo]

        if (nombre_nuevo == nombre_antiguo) or \
            (nombre_nuevo in self.valores.keys()) or \
            (nombre_nuevo == ''):

            return

        frame.set_label(nombre_nuevo)
        del self.valores[nombre_antiguo]
        self.valores[nombre_nuevo] = valores
        self.l_valores = self.valores.keys()
        self.l_valores = self.ordenar_lista()

        for x in self.widgets['SpinButtons']:
            if x.variable == nombre_antiguo:
                x.variable = nombre_nuevo

        self.emit('reload')

    def crear_variable(self, *args):

        lista = self._vbox.get_children()

        self.limpiar_vbox()

        if self.l_valores:
            cantidad = len(self.valores[self.l_valores[0]])
            lista = []

            for x in range(0, cantidad):
                lista += [0]

        else:
            lista = [0]

        num = (len(self.valores) + 1)
        valor = 'Variable %d' % num

        while True:
            num = int(valor.split(' ')[-1])
            valor = 'Variable %d' % num

            if not valor in self.valores:
                break

            else:
                num += 1
                valor = 'Variable %d' % num

        self.valores[valor] = lista
        self.l_valores = self.ordenar_lista()

        self.cargar_variables()

    def ordenar_lista(self):

        self.l_valores = self.valores.keys()
        self.l_valores.sort()

        return self.l_valores

    def limpiar_vbox(self):

        while True:
            if len(self._vbox.get_children()) == 0:
                break

            for x in self._vbox.get_children():
                self._vbox.remove(x)

    def aniadir_a_variable(self, widget):

        for x in self.l_valores:
            self.valores[x] += [0]

        self.cargar_variables()

    def crear_scrolled_variables(self):

        scrolled = Gtk.ScrolledWindow()

        self.cargar_variables()
        scrolled.add_with_viewport(self._vbox)
        self.paned.pack2(scrolled)

    def get_color(self):

        random.seed()

        num1 = random.randint(0, 100) / 100.0
        num2 = random.randint(0, 100) / 100.0
        num3 = random.randint(0, 100) / 100.0
        color = [(num1, num2, num3)]

        return color

    def __set_value(self, widget, gparam=None):

        if not gparam:
            exec(widget.variable + ' = %d' % widget.get_value())

        elif gparam:
            exec(widget.variable + ' = ' + str(widget.get_active()))

        self.emit('reload')

    def __set_inner_radius(self, widget):

        self.inner_radius = widget.get_value()
        self.emit('reload')

    def __recargar(self, *args):

        self.crear_grafica()

    def __change_value(self, widget, valor):

        conjunto = widget.variable
        self.valores[conjunto][valor] = widget.get_value()
        self.emit('reload')

    def __set_rounded_corners(self, widget, gparam):

        self.rounded_corners = widget.get_active()
        self.emit('reload')

    def __set_axis(self, widget, gparam):

        self.axis = widget.get_active()
        self.emit('reload')

    def __set_gird(self, widget, gparam):

        self.cuadricula = widget.get_active()
        self.emit('reload')

    def __set_background(self, combo):

        lista = ['white', 'black', 'red', 'blue', 'green', 'yellow', 'orange']
        self.fondo = lista[combo.get_active()]
        self.fondo += ' light_gray'

        self.emit('reload')

    def salir(self, *args):

        #self.close()
        Gtk.main_quit()


if __name__ == '__main__':

    CairoGrapher()
    Gtk.main()
