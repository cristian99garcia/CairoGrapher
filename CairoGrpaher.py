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
from Widgets import HelpDialog

from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GObject


class CairoGrapher(Gtk.Window):

    __gsignals__ = {
        'reload': (GObject.SIGNAL_RUN_FIRST, None, []),
        'save-changes': (GObject.SIGNAL_RUN_FIRST, None, []),
            }

    def __init__(self):

        Gtk.Window.__init__(self)

        self.set_size_request(600, 480)

        self.vbox = Gtk.VBox()
        self.listbox = Gtk.ListBox()
        self.paned = Gtk.HPaned()
        self.area = PlotArea()

        self.listbox.set_selection_mode(Gtk.SelectionMode.NONE)

        scrolled1 = Gtk.ScrolledWindow()
        scrolled2 = Gtk.ScrolledWindow()

        self.cargar_configuracion()
        self.crear_barra()
        self.cargar_variables()

        self.connect('reload', self.__recargar)
        self.connect('reload', self.actualizar_widgets, self.combo_borrar)
        self.connect('save-changes', self.guardar_configuracion)
        self.connect('delete-event', self.salir)

        scrolled1.add(self.area)
        scrolled2.add(self.listbox)
        self.paned.pack1(scrolled1, 300, -1)
        self.paned.pack2(scrolled2)
        self.vbox.pack_start(self.paned, True, True, 0)

        self.add(self.vbox)
        self.vbox.show()
        self.paned.show()
        scrolled1.show_all()
        scrolled2.show()

        self.emit('reload')

    def transformar_colores(self):

        if len(self.colores) >= len(self.colors.keys()):
            for x in self.listbox.get_children():
                self.colors[x] = (self.colores[self.listbox.get_children().index(x)])

    def actualizar_widgets(self, *args):

        boton = self.toolbar.get_children()[3]
        columnas = 0

        if self.valores.keys():
            columnas = len(self.valores[self.valores.keys()[0]])

            self.combo_borrar.remove_all()

            for x in range(1, columnas + 1):
                self.combo_borrar.append_text('Columna ' + str(x))

        self.combo_borrar.set_active(0)
        self.combo_borrar.set_sensitive(columnas > 1)
        self.combo_borrar.boton.set_sensitive(columnas > 1)
        boton.set_sensitive(bool(self.valores.keys()))

        for x in self.toolbar.lista:
            if self.grafica.endswith(x):
                self.toolbar.combo_graficas.set_active(self.toolbar.lista.index(x))
                break

    def crear_barra(self):

        self.toolbar = Toolbar()
        self.combo_borrar = self.toolbar.combo_borrar

        self.toolbar.connect('save', self.guardar_archivo)
        self.toolbar.connect('new-variable', self.crear_variable)
        self.toolbar.connect('new-variable', self.actualizar_widgets)
        self.toolbar.connect('new-column', self.aniadir_a_variable)
        self.toolbar.connect('settings-dialog', self.dialogo_configuraciones)
        self.toolbar.connect('change-plot', self.cambiar_tipo)
        self.toolbar.connect('remove-column', self.borrar_columna)
        self.toolbar.connect('remove-column', self.actualizar_widgets)
        self.toolbar.connect('help-request', self.dialogo_ayuda)

        for x in range(0, len(self.toolbar.lista)):
            if self.grafica.endswith(self.toolbar.lista[x]):
                self.combo_borrar.set_active(x)
                self.combo_borrar.emit('changed')
                break

        self.set_titlebar(self.toolbar)

    def ocultar_controles_de_colores(self, *args):

        for x in self.listbox.get_children():
            hbox = x.get_children()[0]
            controles = hbox.get_children()[-2]
            controles.hide()

    def guardar_archivo(self, *args):

        def save_file(widget, direccion):

            self.direccion = direccion
            self._direccion = direccion
            self.emit('reload')
            self.direccion = os.path.expanduser('~/.cairographer/Grafica.png')

        d = SaveFilesDialog(self._direccion)
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

    def dialogo_ayuda(self, *args):

        HelpDialog(self)

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

        texto = str(dicc)
        archivo = os.path.expanduser('~/.cairographer/config.json')
        archivo = open(archivo, 'w')

        archivo.write(texto)
        archivo.close()

        self.emit('reload')

    def crear_grafica(self, grafica=None):

        if not grafica:
            grafica = self.grafica

        self.grafica = grafica
        pasar = False

        #self.cargar_colores()

        if self.colores and type(self.colores[-1]) == float:
            c1 = self.colores[-3]
            c2 = self.colores[-2]
            c3 = self.colores[-1]

            self.colores.remove(self.colores[-1])
            self.colores.remove(self.colores[-1])
            self.colores.remove(self.colores[-1])

            self.colores.insert(-1, (c1, c2, c3))

        for x in self.valores.keys():
            for i in self.valores[x]:
                if i >= 1:
                    pasar = True
                    break

        if not pasar and self.valores.keys():
            self.valores[sorted(self.valores.keys())[0]] = [1]

        if grafica == 'Gráfica de barras horizontales':
            y_labels = sorted(self.valores.keys())
            y_labels.sort()

            if self.valores:
                if len(self.valores[sorted(self.valores.keys())[0]]) == 1:
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
            x_labels = sorted(self.valores.keys()) #self.l_valores
            y_labels = []
            x_labels.sort()

            if self.valores:
                if len(self.valores[sorted(self.valores.keys())[0]]) == 1:
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

        elif grafica == 'Gráfica de ecuaciones':
            valores, rectas = self.transformar_a_ecuaciones()

            CairoPlot.dot_ecuations_plot(self.direccion, valores, rectas=rectas, width=self.tamanyo_x, height=self.tamanyo_y)

        self.area.set_plot(self.direccion)

        self.emit('save-changes')

    def transformar_a_barras(self):

        lista = []
        valores = self.valores.keys()
        valores.sort()

        for x in valores:
            lista += self.valores[x]

        while len(self.colores) < len(lista):
            self.colores += [self.get_color()]

        return lista

    def transformar_a_ecuaciones(self):

        lista = []
        rectas = []
        colores = {}
        rows = self.listbox.get_children()

        for row in rows:
            if len(row.get_children()[0].get_children()) >= 6:
                spins = row.get_children()[0].get_children()[1:3]
                hbox =  row.get_children()[0].get_children()[-2]
                num1 = spins[0].get_value()
                num2 = spins[1].get_value()
                adj1 = Gtk.Adjustment(num1 if num1 <= 20 else 20, -20, 20, 1, 0)
                adj2 = Gtk.Adjustment(num2 if num2 <= 20 else 20, -20, 20, 1, 0)
                spins[0].set_adjustment(adj1)
                spins[1].set_adjustment(adj2)
                spins[0].set_value(num1 if num1 <= 20 else 20)
                spins[1].set_value(num2 if num2 <= 20 else 20)

                r = hbox.get_children()[0].get_value()
                g = hbox.get_children()[1].get_value()
                b = hbox.get_children()[2].get_value()
                color = (r, g, b)
                #print r, g, b
                #for x in hbox.get_children():
                #    color += (x.get_value() * 1.0,)

                lista += [(spins[0].get_value(), spins[1].get_value(), color)]

                if not color in colores:
                    colores[color] = spins[0].get_value(), spins[1].get_value(), color

                else:
                    rectas += [[spins[0].get_value(), spins[1].get_value(), colores[color]]]

        return lista, rectas

    def cargar_colores(self):

        self.colores = []

        for x in self.listbox.get_children():
            self.colores += [self.colors[x]]

        if self.listbox.get_children() and len(self.colores) < len(self.listbox.get_children()[0].get_children()[0]):
            while len(self.colores) < len(self.listbox.get_children()[0].get_children()[0]):
                self.colores += [self.get_color()]

    def borrar_columna(self, widget):

        columna = self.combo_borrar.get_active()
        cambiar = True

        if self.valores.keys() and len(self.valores[sorted(self.valores.keys())[0]]) >= columna:
            self.limpiar_vbox()
            valores = sorted(self.valores.keys())

            for x in valores:
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

        self.actualizar_widgets()

    def cargar_variables(self, actualizar=True):

        #if actualizar:
        self.colors = {}
        lista = []
        n = 0

        self.limpiar_vbox()

        for _x in sorted(self.valores.keys()):
            row = Gtk.ListBoxRow()
            hbox = Gtk.HBox()
            label = Gtk.Label(_x)
            entrada = Gtk.Entry()
            numero = 0
            n += 1

            if len(self.colores) >= n:
                self.colors[row] = self.colores[n - 1]

            else:
                self.colors[row] = self.get_color()
                self.colores.append(self.colors[row])

            self.widgets['Entrys'].append(entrada)

            entrada.connect('changed', self.cambiar_nombre_variable, label, row)

            entrada.set_text(_x)

            hbox.pack_start(entrada, False, False, 0)

            for x in self.valores[_x]:
                if len(self.valores) == 1 and len(self.valores[_x]) == 1:
                    _min = 1
                    self.valores[_x][0] = 1

                else:
                    _min = 0

                if self.grafica == 'Gráfica de ecuaciones':
                    _min = -20

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

            color = self.colors[row]

            boton_cerrar = Gtk.Button()
            boton_cerrar.img = Gtk.Image.new_from_stock(Gtk.STOCK_CLOSE, Gtk.IconSize.BUTTON)
            boton_mas = Gtk.Button()
            boton_mas.img = Gtk.Image.new_from_stock(Gtk.STOCK_ADD, Gtk.IconSize.BUTTON)
            hbox_mas = Gtk.HBox()
            r_adj = Gtk.Adjustment(color[0], 0.0, 1.0, 0.1, 0)
            g_adj = Gtk.Adjustment(color[1], 0.0, 1.0, 0.1)
            b_adj = Gtk.Adjustment(color[2], 0.0, 1.0, 0.1)
            r_scale = Gtk.Scale(orientation=Gtk.Orientation.VERTICAL, adjustment=r_adj)
            g_scale = Gtk.Scale(orientation=Gtk.Orientation.VERTICAL, adjustment=g_adj)
            b_scale = Gtk.Scale(orientation=Gtk.Orientation.VERTICAL, adjustment=b_adj)

            boton_cerrar.set_image(boton_cerrar.img)
            boton_mas.set_image(boton_mas.img)
            boton_mas.set_tooltip_text('Mostrar los controles de color')
            r_scale.set_value(color[0])
            g_scale.set_value(color[1])
            b_scale.set_value(color[2])
            r_scale.set_size_request(-1, 100)
            g_scale.set_size_request(-1, 100)
            b_scale.set_size_request(-1, 100)

            boton_cerrar.connect('clicked', self.borrar_valor, label, entrada, spin, row)

            boton_mas.connect('clicked', self.mostrar, hbox_mas)
            r_scale.connect('value-changed', self.setear_color, 'Rojo', row)
            g_scale.connect('value-changed', self.setear_color, 'Verde', row)
            b_scale.connect('value-changed', self.setear_color, 'Azúl', row)

            hbox_mas.pack_start(r_scale, False, False, 5)
            hbox_mas.pack_start(g_scale, False, False, 5)
            hbox_mas.pack_start(b_scale, False, False, 5)

            lista.append(hbox_mas)

            self.widgets['ClouseButtons'].append(boton_cerrar)
            hbox.pack_end(boton_cerrar, False, False, 0)
            hbox.pack_end(hbox_mas, True, True, 0)
            hbox.pack_end(boton_mas, False, False, 10)
            row.add(hbox)
            self.listbox.add(row)
            self.listbox.show_all()
            self.ocultar_controles_de_colores()

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

    def setear_color(self, widget, label, row):

        cantidad = widget.get_value()

        if label == 'Rojo':
            color = (cantidad,) + self.colors[row][1:]

        elif label == 'Verde':
            color = self.colors[row][:1] + (cantidad,) + self.colors[row][2:]

        elif label == 'Azúl':
            color =  self.colors[row][:2] + (cantidad,)

        self.colors[row] = color
        self.colores = []

        for x in self.listbox.get_children():
            self.colores.append(self.colors[x])

        self.emit('reload')

    def borrar_valor(self, widget, label, entrada, spin, row):

        self.listbox.remove(row)
        del self.colors[row]
        del self.valores[label.get_label()]

        self.widgets['Entrys'].remove(entrada)
        self.widgets['SpinButtons'].remove(spin)
        self.widgets['ClouseButtons'].remove(widget)

        self.emit('reload')

    def cargar_configuracion(self, devolver=False):

        direccion = os.path.expanduser('~/.cairographer')

        if not os.path.exists(direccion):
            os.mkdir(direccion)

        if not devolver:
            self.widgets = {'SpinButtons': [], 'Entrys': [], 'ClouseButtons': []}
            self.botones = []
            self.grupos = False
            self.colors = {}
            self.x_labels = []
            self.y_labels = []
            self._direccion = os.path.expanduser('~/Grafica.png')

            if not os.path.exists(os.path.join(direccion, 'config.json')):
                self.direccion = os.path.join(direccion, 'Grafica.png')
                self.grafica = 'Gráfica de torta'
                self.valores = {}
                #self.colors = {}
                self.colores = []
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
                self.rounded_corners = True
                self.inner_radius = 0.3

                self.emit('save-changes')

            elif os.path.exists(os.path.join(direccion, 'config.json')):
                texto = open(os.path.join(direccion, 'config.json')).read()
                dicc = eval(texto)

                self.direccion = dicc['direccion']
                self.grafica = dicc['grafica']
                self.valores = dicc['valores']
                #self.colors = dicc['colors']
                self.colores = dicc['colores']
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

                if '\xc3\xa1' in self.grafica:
                    self.grafica = self.grafica.replace('\xc3\xa1', 'á')

                #self.transformar_colores()
                self.emit('reload')

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
                'valores': self.valores,
                'colors': self.colors,
                'colores': self.colores,
                }

        self.ocultar_controles_de_colores()

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

        for x in self.widgets['SpinButtons']:
            if x.variable == nombre_antiguo:
                x.variable = nombre_nuevo

        self.emit('reload')

    def crear_variable(self, *args):

        self.colores += [self.get_color()]
        a = self.valores.keys()

        self.limpiar_vbox()

        if self.valores.keys():
            cantidad = len(self.valores[sorted(self.valores.keys())[0]])
            lista = []

            for x in range(0, cantidad):
                lista += [0.0]

        else:
            lista = [0.0]

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

        self.cargar_variables()
        self.emit('save-changes')

    def limpiar_vbox(self):

        while True:
            if len(self.listbox.get_children()) == 0:
                break

            for x in self.listbox.get_children():
                self.listbox.remove(x)

    def aniadir_a_variable(self, widget):

        for x in self.valores.keys(): #self.l_valores:
            self.valores[x] += [0]

        if self.grafica.startswith('Gráfica de barras'):
            self.colores += self.get_color()

        self.cargar_variables()

    def get_color(self):

        random.seed()

        num1 = random.randint(0, 100) / 100.0
        num2 = random.randint(0, 100) / 100.0
        num3 = random.randint(0, 100) / 100.0
        color = (num1, num2, num3)

        return color

    def guardar_configuracion(self, *args):

        dicc = self.cargar_configuracion(devolver=True)
        archivo = open(os.path.expanduser('~/.cairographer/config.json'), 'w')
        texto = '{\n'

        for x in sorted(dicc.keys()):
            if type(dicc[x]) != list and type(dicc[x]) != dict:
                if type(dicc[x]) == str:
                    texto += '    "' + x + '": ' + '"' + str(dicc[x]) + '",\n'

                elif type(dicc[x]) != str:
                    texto += '    "' + x + '": ' + str(dicc[x]) + ',\n'

            else:
                if type(dicc[x]) == dict and x != 'colors':
                    texto += '    "' + x + '": {\n'
                    for i in sorted(dicc[x].keys()):
                        texto += '        "' + i + '": ' + str(dicc[x][i]) + ',\n'

                    texto += '    },\n'

                elif type(dicc[x]) == list:
                    texto += '    "' + x + '": [\n'
                    for i in sorted(dicc[x]):
                        texto += '        ' + str(i) + ',\n'

                    texto += '    ],\n'

        texto += '}'

        archivo.write(texto)
        archivo.close()

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

        Gtk.main_quit()


if __name__ == '__main__':

    CairoGrapher()
    Gtk.main()
