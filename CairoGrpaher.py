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

from Widgets import Toolbar
from Widgets import PlotArea
from Widgets import SettingsDialog
from Widgets import SaveFilesDialog

import gtk
import gobject


class CairoGrapher(gtk.Window):

    __gsignals__ = {
        'reload': (gobject.SIGNAL_RUN_FIRST, None, []),
            }

    def __init__(self):

        gtk.Window.__init__(self)

        self.cargar_configuracion()

        self.set_size_request(600, 480)
        self.set_title('CairoGrapher')

        self.vbox = gtk.VBox()
        self._vbox = gtk.VBox()
        self.paned = gtk.HPaned()
        self.area = PlotArea()

        scrolled = gtk.ScrolledWindow()

        self.crear_barra()
        self.crear_scrolled_variables()
        self.crear_grafica()

        self.area.set_plot(self.direccion)

        self.connect('reload', self.__recargar)
        #self.connect('reload', self.actualizar_combo_borrar, self.combo_borrar)
        self.connect('delete-event', self.salir)

        scrolled.add_with_viewport(self.area)
        self.paned.pack1(scrolled, 300, -1)
        self.paned.pack2(self._vbox)
        self.vbox.pack_start(self.paned, True, True, 0)

        self.add(self.vbox)
        self.show_all()

    def actualizar_combo_borrar(self, *args):

        self.l_valores = sorted(self.valores.keys())
        boton = self.toolbar.get_children()[5]

        if self.l_valores:
            columnas = len(self.valores[self.l_valores[0]])

            self.combo_borrar.get_model().clear()
            #self.combo_borrar.remove_all()

            for x in range(1, columnas + 1):
                self.combo_borrar.append_text('Columna ' + str(x))

            self.combo_borrar.set_active(0)
            self.combo_borrar.set_sensitive(columnas > 1)
            self.combo_borrar.boton.set_sensitive(columnas > 1)
            boton.set_sensitive(True)

        else:
            self.combo_borrar.set_sensitive(False)
            self.combo_borrar.boton.set_sensitive(False)
            boton.set_sensitive(False)

    def crear_barra(self):

        self.toolbar = Toolbar()
        self.combo_borrar = self.toolbar.combo_borrar

        self.toolbar.connect('save', self.guardar_archivo)
        self.toolbar.connect('new-variable', self.crear_variable)
        self.toolbar.connect('new-variable', self.actualizar_combo_borrar)
        self.toolbar.connect('new-column', self.aniadir_a_variable)
        self.toolbar.connect('settings-dialog', self.dialogo_configuraciones)
        self.toolbar.connect('change-plot', self.cambiar_tipo)
        self.toolbar.connect('remove-column', self.borrar_columna)
        self.toolbar.connect('remove-column', self.actualizar_combo_borrar)

        self.vbox.pack_start(self.toolbar, False, False, 0)
        #self.set_titlebar(toolbar)

    def guardar_archivo(self, *args):

        def save_file(widget, direccion):
            
            self.direccion = direccion
            self.emit('reload')

        d = SaveFilesDialog()
        d.connect('save-file', save_file)

    def cambiar_tipo(self, toolbar):

        combo = toolbar.get_plot_combo()
        lista = toolbar.lista
        self.grafica = 'Gráfica de ' + lista[combo.get_active()]

        self.emit('reload')

    def dialogo_configuraciones(self, *args):

        dialogo = SettingsDialog(self.cargar_configuracion(True))
        dialogo.connect('settings-changed', self.settings_changed)
        dialogo.show_all()

    def settings_changed(self, widget, dicc):

        self.direccion = dicc['direccion']
        self.grafica = dicc['grafica']
        self.nombre = dicc['nombre']
        self.titulo_x = dicc['titulo_x']
        self.titulo_y = dicc['titulo_y']
        self.tamanyo_x = int(dicc['tamanyo_x'])
        self.tamanyo_y = int(dicc['tamanyo_y'])
        self.inner_radius = dicc['inner_radius']
        self.borde = dicc['borde']
        self.axis = dicc['axis']
        self.rounded_corners = dicc['rounded_corners']
        self.display_values = dicc['display_values']
        self.cuadricula = dicc['gird']
        self.fondo = dicc['fondo']

        self.emit('reload')

    def crear_grafica(self, grafica=None):

        if not grafica:
            grafica = self.grafica

        self.grafica = grafica
        pasar = False

        self.cargar_colores()

        for x in self.l_valores:
            for i in self.valores[x]:
                if i >= 1:
                    pasar = True
                    break

        if not pasar and self.l_valores:
            self.valores[self.l_valores[0]] = [1]

        if grafica == 'Gráfica de barras horizontales':
            y_labels = self.l_valores
            y_labels.sort()

            if self.valores:
                if len(self.valores[self.l_valores[0]]) == 1:
                    valores = self.transformar_a_barras()

                else:
                    valores = self.valores

                CairoPlot.horizontal_bar_plot(
                    self.direccion,
                    valores,
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
                    x_labels=[],
                    y_labels=y_labels,
                    x_bounds=None,
                    y_bounds=None,
                    colors=self.colores)

        elif grafica == 'Gráfica de barras verticales':
            x_labels = self.l_valores
            y_labels = []
            x_labels.sort()

            if self.valores:
                if len(self.valores[self.l_valores[0]]) == 1:
                    valores = self.transformar_a_barras()

                else:
                    valores = self.valores

                CairoPlot.vertical_bar_plot(
                    self.direccion,
                    valores,
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
                    x_labels=x_labels,
                    y_labels=y_labels,
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

        self.area.set_plot(self.direccion)

    def transformar_a_barras(self):

        lista = []
        valores = self.valores.keys()
        valores.sort()

        for x in valores:
            lista += self.valores[x]

        while len(self.colores) < len(lista):
            self.colores += [self.get_color()]

        return lista

    def cargar_colores(self):

        self.colores = []

        if self._vbox.get_children():
            listbox = self._vbox.get_children()[0]

            for x in listbox.get_children():
                self.colores += [self.colors[x]]

            if listbox.get_children() and len(self.colores) < len(listbox.get_children()[0].get_children()):
                while len(self.colores) < len(listbox.get_children()[0].get_children()):
                    self.colores += [self.get_color()]

    def borrar_columna(self, widget):

        columna = self.combo_borrar.get_active()
        cambiar = True

        if self.l_valores and len(self.valores[self.l_valores[0]]) >= columna:
            self.limpiar_vbox()
            self.l_valores = sorted(self.valores.keys())

            for x in self.l_valores:
                self.valores[x].remove(self.valores[x][columna])

                c = True

                for i in self.valores[x]:
                    if i > 0:
                        c = False
                        break
                
                if c and cambiar:
                    self.valores[x][0] = 1.0
                    cambiar = False

            self.cargar_variables()

        self.actualizar_combo_borrar()

    def cargar_variables(self, actualizar=True):

        #self.l_valores = self.ordenar_lista()
        #self.l_valores = sorted(self.valores.keys())
        self.colors = {}
        lista = []
        #listbox = gtk.ListBox()
        listbox = gtk.VBox()

        #listbox.set_selection_mode(gtk.SelectionMode.NONE)
        self.limpiar_vbox()

        for _x in self.l_valores:
            #row = gtk.ListBoxRow()
            hbox = gtk.HBox()
            label = gtk.Label(_x)
            entrada = gtk.Entry()
            numero = 0
            #self.colors[row] = self.get_color()
            self.colors[hbox] = self.get_color()

            self.widgets['Entrys'].append(entrada)

            entrada.connect('changed', self.cambiar_nombre_variable, label, hbox)

            entrada.set_text(_x)

            hbox.pack_start(entrada, False, False, 0)

            for x in self.valores[_x]:
                if len(self.valores) == 1 and len(self.valores[_x]) == 1:
                    _min = 1
                    self.valores[_x][0] = 1

                else:
                    _min = 0

                spin = gtk.SpinButton()
                adj = gtk.Adjustment(x, _min, 10000000, 1, 10, 0)
                spin.variable = _x

                spin.set_digits(1)
                spin.set_adjustment(adj)
                spin.set_value(x)

                spin.connect('value-changed', self.__change_value, numero)
                self.widgets['SpinButtons'].append(spin)
                hbox.pack_start(spin, False, False, 10)

                numero += 1

            color = self.colors[hbox]

            boton_cerrar = gtk.Button()
            boton_cerrar.img = gtk.Image()
            boton_mas = gtk.Button()
            boton_mas.img = gtk.Image()
            hbox_mas = gtk.HBox()
            r_adj = gtk.Adjustment(color[0], 0.0, 1.0, 0.1, 0)
            g_adj = gtk.Adjustment(color[1], 0.0, 1.0, 0.1)
            b_adj = gtk.Adjustment(color[2], 0.0, 1.0, 0.1)
            r_scale = gtk.VScale() #orientation=gtk.ORIENTATION_VERTICAL, adjustment=r_adj)
            g_scale = gtk.VScale() #orientation=gtk.ORIENTATION_VERTICAL, adjustment=g_adj)
            b_scale = gtk.VScale() #orientation=gtk.ORIENTATION_VERTICAL, adjustment=b_adj)

            boton_cerrar.img.set_from_stock(gtk.STOCK_CLOSE, gtk.ICON_SIZE_BUTTON)
            boton_mas.img.set_from_stock(gtk.STOCK_ADD, gtk.ICON_SIZE_BUTTON)
            boton_cerrar.set_image(boton_cerrar.img)
            boton_mas.set_image(boton_mas.img)
            boton_mas.set_tooltip_text('Mostrar los controles de color')
            r_scale.set_adjustment(r_adj)
            g_scale.set_adjustment(g_adj)
            b_scale.set_adjustment(b_adj)
            r_scale.set_value(color[0])
            g_scale.set_value(color[1])
            b_scale.set_value(color[2])
            r_scale.set_size_request(-1, 100)
            g_scale.set_size_request(-1, 100)
            b_scale.set_size_request(-1, 100)

            boton_cerrar.connect('clicked', self.borrar_valor, label, entrada, spin, listbox, hbox)

            boton_mas.connect('clicked', self.mostrar, hbox_mas)
            r_scale.connect('value-changed', self.setear_color, 'Rojo', hbox)
            g_scale.connect('value-changed', self.setear_color, 'Verde', hbox)
            b_scale.connect('value-changed', self.setear_color, 'Azúl', hbox)

            hbox_mas.pack_start(r_scale, False, False, 5)
            hbox_mas.pack_start(g_scale, False, False, 5)
            hbox_mas.pack_start(b_scale, False, False, 5)

            lista.append(hbox_mas)

            self.widgets['ClouseButtons'].append(boton_cerrar)
            hbox.pack_end(boton_cerrar, False, False, 0)
            hbox.pack_end(hbox_mas, True, True, 0)
            hbox.pack_end(boton_mas, False, False, 10)
            #row.add(hbox)
            #listbox.add(row)
            listbox.pack_start(hbox, False, False, 2)
            listbox.show_all()
            hbox_mas.hide()

        self._vbox.pack_start(listbox, False, False, 10)

        if actualizar:
            self.emit('reload')
            self.show_all()

            for x in lista:
                x.hide()

    def mostrar(self, boton, widget):

        if widget.get_visible():
            imagen = gtk.Image()
            
            imagen.set_from_stock(gtk.STOCK_ADD, gtk.ICON_SIZE_BUTTON)

            widget.hide()
            boton.set_image(imagen)
            boton.set_tooltip_text('Mostrar los controles de color')

        else:
            imagen = gtk.Image()

            imagen.set_from_stock(gtk.STOCK_REMOVE, gtk.ICON_SIZE_BUTTON)

            widget.show_all()
            boton.set_image(imagen)
            boton.set_tooltip_text('Ocultar los controles de color')

    def setear_color(self, widget, label, listbox):

        cantidad = widget.get_value()

        if label == 'Rojo':
            self.colors[listbox] = (cantidad,) + self.colors[listbox][1:]

        elif label == 'Verde':
            self.colors[listbox] = self.colors[listbox][:1] + (cantidad,) + self.colors[listbox][2:]

        elif label == 'Azúl':
            self.colors[listbox] =  self.colors[listbox][:2] + (cantidad,)

        self.emit('reload')

    def borrar_valor(self, widget, label, entrada, spin, listbox, row):

        listbox.remove(row)
        del self.colors[row]
        del self.valores[label.get_label()]
        self.l_valores = self.ordenar_lista()

        self.widgets['Entrys'].remove(entrada)
        self.widgets['SpinButtons'].remove(spin)
        self.widgets['ClouseButtons'].remove(widget)

        self.emit('reload')
        self.actualizar_combo_borrar()

    def cargar_configuracion(self, devolver=False):

        if not devolver:
            self.widgets = {'SpinButtons': [], 'Entrys': [], 'ClouseButtons': []}
            self.colors = {}
            self.botones = []
            self.colores = []
            self.valores = {}
            self.direccion = os.path.expanduser('~/Grafica.png')
            self.grafica = 'Gráfica de torta'
            self.nombre = 'Grafica'
            self.titulo_x = 'Gráfica'
            self.titulo_y = ''
            self.tamanyo_x = 600
            self.tamanyo_y = 600
            self.fondo = (1, 1, 1)
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

        else:
            return {
                'direccion': self.direccion,
                'grafica': self.grafica,
                'nombre': self.nombre,
                'titulo_x': self.titulo_x,
                'titulo_y': self.titulo_y,
                'tamanyo_x': self.tamanyo_x,
                'tamanyo_y': self.tamanyo_y,
                'inner_radius': self.inner_radius,
                'borde': self.borde,
                'axis': self.axis,
                'rounded_corners': self.rounded_corners,
                'display_values': self.display_values,
                'gird': self.cuadricula,
                'fondo': self.fondo,
                }

    def cambiar_nombre_variable(self, widget, label, row):

        nombre_nuevo = widget.get_text()
        nombre_antiguo = label.get_label()
        valores = self.valores[nombre_antiguo]

        if (nombre_nuevo == nombre_antiguo) or \
            (nombre_nuevo in self.valores.keys()) or \
            (nombre_nuevo == ''):

            return

        label.set_label(nombre_nuevo)
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
        self.colores += [self.get_color()]

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

        if self.grafica.startswith('Gráfica de barras'):
            self.colores += self.get_color()

        self.cargar_variables()

    def crear_scrolled_variables(self):

        scrolled = gtk.ScrolledWindow()

        self.cargar_variables()
        scrolled.add_with_viewport(self._vbox)
        self.paned.pack2(scrolled)

    def get_color(self):

        random.seed()

        num1 = random.randint(0, 100) / 100.0
        num2 = random.randint(0, 100) / 100.0
        num3 = random.randint(0, 100) / 100.0
        color = (num1, num2, num3)

        return color

    def __set_value(self, widget, gparam=None):

        if not gparam:
            exec(widget.variable + ' = %d' % widget.get_value())

        elif gparam:
            exec(widget.variable + ' = ' + str(widget.get_active()))

        self.emit('reload')

    def __recargar(self, *args):

        self.crear_grafica()

    def __change_value(self, widget, valor):

        conjunto = widget.variable
        self.valores[conjunto][valor] = widget.get_value()
        self.emit('reload')

    def salir(self, *args):

        gtk.main_quit()


if __name__ == '__main__':

    CairoGrapher()
    gtk.main()
