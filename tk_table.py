#!/usr/bin/python
# -*- encoding: UTF-8 -*-

from tkinter import *

###  описание отдельной клетки будущей таблицы ###
class cell(Widget):
    def __init__(self, parent, type = "entry", **kw):
        self.value = StringVar() # каждой клетке таблице сопостовляется переменная StringVar
        if type == "entry":  #  всего используются(пока что) две версии клеток - срьствено окошко ввода entry
            Widget.__init__(self, parent, 'entry', kw)
            self.configure(textvariable = self.value)
        elif type == "label":  #  всего используются(пока что) две версии клеток - срьствено окошко ввода entry
            Widget.__init__(self, parent, 'label', kw)
            self.configure(textvariable = self.value, relief = "groove", borderwidth = 1)
        elif type == "checkbutton":  # и галочка на проверку
            Widget.__init__(self, parent, 'checkbutton', kw)
            self.configure(variable = self.value)
            self.value.set(0)
        else:
            Widget.__init__(self, parent, 'entry', kw)
            self.configure(textvariable = self.value)

###  описание таблице, состоящей из клеток  и чекбоксов   ###
class table(Frame): # не забываем, что таблица наследуется от Фрэйма
    def __init__(self, parent, columns = 1, rows = 1): # указываем родителя + указываем количество строк и столбцов
        Frame.__init__(self, parent) # дял начала инициализируем родительский фрэйм
        self.cells = [] # теперь создаем лист под будущие ячейки таблицы. В будущем этот лист будет двумерным
        for j in range(columns):
            self.cells.append([])  # тут как раз и делаем лист для ячеек двумерным
            for i in range(rows):  #  в данном цикле мы указываем тип ячейки который будет стоять по координате (j, i)
                if j == 0:		self.cells[j].append(cell(self, height = 0, type = "checkbutton"))
                elif j == 1:	self.cells[j].append(cell(self, width = 30, justify = "left", type = "entry"))
                else:			self.cells[j].append(cell(self, width = 15, justify = "center", type = "entry"))
        [self.cells[j][i].grid(row = i, column = j) for i in range(rows) for j in range(columns)]  #  а тут, с помощью пакера grid мы пакуем ячейки по сетке

###  описание таблице, состоящей из клеток ###
###  тоже самое, что и в предыдущем случае, только раскрашиваем первый столбец и строку в другой цвет  ###
class array_table(Frame):
    def __init__(self, parent, columns = 1, rows = 1):
        Frame.__init__(self, parent)
        self.cells = []
        for j in range(columns):
            self.cells.append([])
            for i in range(rows):
                if j == 0:	    self.cells[j].append(cell(self, width = 20, justify = "left", type = "entry"))
                else:			self.cells[j].append(cell(self, width = 15, justify = "center", type = "entry"))
        [self.cells[j][i].grid(row = i, column = j) for i in range(rows) for j in range(columns)]
        [self.cells[0][i].configure(bg="gray90") for i in range(rows)]  # тут раскрашиваем первый столбец
        [self.cells[j][0].configure(bg="gray80") for j in range(columns)]  # тут раскрашиваем первую строку

###  описание таблице, состоящей из клеток для вывода массива данных###
###  тоже самое, что и в предыдущем случае, только раскрашиваем первый столбец и строку в другой цвет  ###
class data_table(Frame):
    def __init__(self, parent, columns=9, rows=2, word_len=2):

        Frame.__init__(self, parent)

        self.word_len = word_len
        self.columns = columns
        self.rows = rows
        self._frame_position = [0, 0, 0, 0]

        self.cells = []
        for j in range(columns):
            self.cells.append([])
            for i in range(rows):
                if j == 0:
                    self.cells[j].append(cell(self, width=7, justify="center", type="entry"))
                elif i == 0:
                    self.cells[j].append(cell(self, width=2 + 2*word_len, justify="center", type="entry"))
                else:
                    self.cells[j].append(cell(self, width=2 + 2*word_len, justify="center", type="entry", borderwidth=1))

        [self.cells[i][j].grid(row = j, column = i) for j in range(rows) for i in range(columns)]  # пакуем клетки

        [self.cells[0][i].configure(bg="gray90") for i in range(rows)]  # тут раскрашиваем первый столбец
        [self.cells[0][i].value.set("+{0:d}".format((i-1)*8)) for i in range(1, rows)]  # тут именуем ячей первого столбца начиная с первой строки
        [self.cells[j][0].configure(bg="gray80") for j in range(columns)]  # тут раскрашиваем первую строку
        [self.cells[j][0].value.set("{0:d}".format((j-1))) for j in range(1, columns)]  # тут раскрашиваем первую строку

        #self.InsertData([i for i in range((self.columns - 1)*(self.rows - 1))])

    def InsertData(self, data):  # data лист данных
        for i in range(len(data)):
            hex_value = " "
            for k in range(self.word_len):
                hex_value += "{0:02X} ".format(int((data[i] >> (8*(self.word_len - k - 1))) & 0xFF))
            #print(hex_value)
            try:
                self.cells[1 + i % 8][1 + i // 8].value.set(hex_value)
            except IndexError as error:
                print(error)
                break
        pass

    def GetData(self):  # data лист данных
        data_len = (self.columns - 1)*(self.rows - 1)

        data = []
        for i in range(data_len):
            hex_str = self.cells[1 + i % 8][1 + i // 8].value.get().strip().split(" ")
            hex_value = 0
            for j in range(len(hex_str)):
                try:
                    hex_value += int(hex_str[j], base=16)*(2**(8*(len(hex_str) - j - 1)))
                except ValueError as error:
                    #print(error)
                    hex_value += 0
            data.append(hex_value)
        return data

    def GetTableSize(self):
        self.update_idletasks()  # обновляем фрэйм, что бы получить актуальные размеры и координаты
        self._frame_position = [self.winfo_x(),
                                self.winfo_y(),
                                self.winfo_x() + self.winfo_reqwidth(),
                                self.winfo_y() + self.winfo_reqheight()]
        return self._frame_position


