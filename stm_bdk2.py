import tkinter
import kpa_bdk2_parcer


##  описание отдельной клетки будущей таблицы ##
class cell(tkinter.Widget):
    def __init__(self, parent, type="entry", **kw):
        self.value = tkinter.StringVar()
        if type == "entry":
            tkinter.Widget.__init__(self, parent, 'entry', kw)
            self.configure(textvariable=self.value)
        elif type == "label":
            tkinter.Widget.__init__(self, parent, 'label', kw)
            self.configure(textvariable=self.value, borderwidth=1)
        elif type == "checkbutton":
            tkinter.Widget.__init__(self, parent, 'checkbutton', kw)
            self.configure(variable=self.value,)
            self.value.set(0)
        else:
            tkinter.Widget.__init__(self, parent, 'entry', kw)
            self.configure(textvariable=self.value)

######## БДД #########
### класс с фрэймом для вывод сырых данных СТМ БДД
class stm_bdd_indicator(tkinter.Frame):
    def __init__(self, cnf={}, **kw):
        self.mko = None
        self.set_enable = True
        for key in sorted(kw):
            if key == "mko":
                self.mko = kw.pop(key)
            elif key == "set_enable":
                self.set_enable = kw.pop(key)
            else:
                pass

        tkinter.Frame.__init__(self, cnf, kw)
        self.columns = 3
        self.rows = 11
        self.names_list = ["КПДД", "МСоб", "БД_С01", "БД_С02", "БД_С03", "БД_С04", "БД_С05", "БД_С06",
                           "БД_С07", "БД_С08"]
        self.title_list = ["Имя", "Напр.,В", "0"]
        self.row_data_len = 10
        self.row_data_list = [0 for i in range(self.row_data_len)]  # value matches "nd"
        self.logical_data = ["nd" for i in range(self.row_data_len)]  # logical meaning; z - meaning undefined
        self.bound = [[1800, 1900],
                      [1800, 1900],
                      [1900, 1950],
                      [1900, 1950],
                      [1900, 1950],
                      [1900, 1950],
                      [1900, 1950],
                      [1900, 1950],
                      [1900, 1950],
                      [1900, 1950]]
        self.used_colors = {"nd": "Coral2", "1": "DeepSkyBlue3", "0": "PaleGreen3", "default": "gray90"}
        self._construct()
        self._insert_name()
        self.parsing()
        pass

    def _construct(self):
        self.cells = []  # теперь создаем лист под будущие ячейки таблицы. В будущем этот лист будет двумерным
        for j in range(self.columns):
            self.cells.append([])  # тут как раз и делаем лист для ячеек двумерным
            for i in range(self.rows):  # в данном цикле мы указываем тип ячейки который будет стоять по координате (j, i)
                if j == 0:
                    self.cells[j].append(cell(self, type="label", justify="center", relief="groove", width=6))
                elif j == 1:
                    if i == 0: self.cells[j].append(cell(self, type="label", justify="center", relief="groove", width=6))
                    else:
                        self.cells[j].append(cell(self, type="label", justify="center", relief="raised", width=6))
                elif j == 2:
                    self.cells[j].append(cell(self, type="checkbutton", justify="center", relief="flat"))
        [self.cells[j][i].place(x=j * 50, y=i * 25, height=22, width=47) for i in range(self.rows)
         for j in range(self.columns-1)]
        if self.set_enable is True:
            [self.cells[2][i].place(x=2*50, y=i * 25, height=22, width=22) for i in range(self.rows)]
            self.cells[2][0].bind('<Button-1>', self.all_ch_but_set)
        self.config(width=50*2+25, height=11*25)
        pass

    def all_ch_but_set(self, event):
        if self.cells[2][0].value.get() == "1":
            [self.cells[2][i+1].value.set("0") for i in range(self.rows-1)]
        else:
            [self.cells[2][i+1].value.set("1") for i in range(self.rows-1)]

    def parsing(self):
        self.logical_data = []
        for i in range(len(self.row_data_list)):
            if self.row_data_list[i] < self.bound[i][0]:  # check excess 100kOhm level
                self.logical_data.append("1")
            elif self.row_data_list[i] > self.bound[i][1]:  # lower than 10kOhm
                self.logical_data.append("0")
            else:  # check that value is in range 10-100kOhm
                self.logical_data.append("nd")
            self.cells[1][i + 1].configure(bg=self.used_colors[self.logical_data[i]])
            self.cells[1][i + 1].value.set(self.row_data_list[i])
        #print(self.logical_data)
        pass

    def insert_data(self, data):
        #print(type(data), isinstance(data, list))
        if isinstance(data, list) is False:
            raise TypeError("Incorrect type")
        elif len(data) != self.row_data_len:
            raise ValueError("Incorrect length")
        else:
            self.row_data_list = data
            self.parsing()
        pass

    def _insert_name(self):
        [self.cells[0][i].value.set(self.names_list[i-1]) for i in range(1, self.rows)]
        [self.cells[i][0].value.set(self.title_list[i]) for i in range(self.columns - 1)]
        [self.cells[i][0].configure(bg="gray80") for i in range(self.columns - 1)]
        pass

### для таблицы разобранных адресов и кусков данных СТМ БДД
class stm_bdd_addr_table(tkinter.Frame):
    def __init__(self, cnf={}, **kw):
        tkinter.Frame.__init__(self, cnf, kw)
        #
        self.title_list = ["Адрес", "Данные"]
        self.names_list = ["{}".format(i) for i in range(16)]
        self.stm_list = ["{:#02X}".format(0) for i in range(16)]
        #
        self.columns = len(self.title_list)
        self.rows = len(self.names_list) + 1
        self.row_data_len = 10
        #
        self._construct()
        self._insert_name()
        #
        self.stm_addr = 0
        self.stm_data = 0
        self.stm_addr_list = []
        self.stm_data_list = []
        self.stm_msob = 0
        self.stm_kpdd = 0
        # stm_data
        self.pressure_1 = 0
        self.temperature_1 = 0
        self.voltage_1 = 0
        self.pressure_2 = 0
        self.temperature_2 = 0
        self.voltage_2 = 0
        self.final_data_list = [0 for i in range(6)]
        self._error_counter = 0  # variable for error stm setting count
        #
        self.stm_addr_pool = 0  # variable, which storage state filling all address (15 - address pool is fool)
        self.used_colors = {"nd": "Coral2", "1": "DeepSkyBlue3", "0": "PaleGreen3"}

    def _construct(self):
        self.cells = []  # теперь создаем лист под будущие ячейки таблицы. В будущем этот лист будет двумерным
        for j in range(self.columns):
            self.cells.append([])  # тут как раз и делаем лист для ячеек двумерным
            for i in range(self.rows):  # в данном цикле мы указываем тип ячейки который будет стоять по координате (j, i)
                if j == 0:
                    self.cells[j].append(cell(self, type="label", justify="center", relief="groove", width=15))
                elif j == 1:
                    if i == 0: self.cells[j].append(cell(self, type="label", justify="center", relief="groove", width=15))
                    else:
                        self.cells[j].append(cell(self, type="label", justify="center", relief="groove", width=15))
        [self.cells[j][i].place(x=j * 55, y=i * 25, height=22, width=52) for i in range(self.rows)
         for j in range(self.columns)]
        self.config(width=55*self.columns, height=self.rows*25)
        pass

    def _insert_name(self):
        [self.cells[0][i].value.set(self.names_list[i-1]) for i in range(1, self.rows)]
        [self.cells[i][0].value.set(self.title_list[i]) for i in range(self.columns)]
        [self.cells[i][0].configure(bg="gray80") for i in range(self.columns)]
        pass

    def insert_data(self, data):
        if isinstance(data, list) is False:
            raise TypeError("Incorrect type")
        elif len(data) != self.row_data_len:
            raise ValueError("Incorrect length")
        else:
            self.stm_list = data
            self.parsing()
        pass

    def parsing(self):
        self.stm_data = 0
        self.stm_addr = 0
        for i in range(len(self.stm_list)):
            if self.stm_list[i] == "nd" and self._error_counter >= 1:
                [self.cells[i][j].configure(bg=self.used_colors[self.stm_list[i]])
                    for i in range(self.columns) for j in range(1, self.rows)]
                return
            elif self.stm_list[i] == "nd":
                self._error_counter += 1
            else:
                self._error_counter = 0
                if i == 0:
                    self.stm_kpdd = int(self.stm_list[i])
                elif i == 1:
                    self.stm_msob = int(self.stm_list[i])
                elif 2 <= i < 6:
                    self.stm_addr += ((int(self.stm_list[i])) << (i-2))
                elif 6 <= i < 10:
                    self.stm_data += ((int(self.stm_list[i])) << (i-6))
        if self._error_counter == 0:
            if self.stm_addr == self.stm_addr_pool:
                self.stm_addr_pool += 1
                self.stm_data_list.append(self.stm_data)
            [self.cells[i][j].configure(bg="gray95")
             for i in range(self.columns) for j in range(1, self.rows)]
            self.cells[1][self.stm_addr + 1].value.set("0x {:01X}".format(self.stm_data))
            self.cells[0][self.stm_addr + 1].configure(bg=self.used_colors["0"])
            self.cells[1][self.stm_addr + 1].configure(bg=self.used_colors["0"])
            # print(self.stm_addr, self.stm_addr_pool)
            if self.stm_addr == 0x0F and self.stm_addr_pool == 16:
                self.stm_addr_pool = 0
                self.pressure_1 = bytes([(self.stm_data_list[0] << 4) + (self.stm_data_list[1] << 0),
                                        (self.stm_data_list[2] << 4) + (self.stm_data_list[3] << 0)])
                self.pressure_1 = kpa_bdk2_parcer.process_row_data(self.pressure_1)
                self.temperature_1 = (self.stm_data_list[4] << 4) + (self.stm_data_list[5] << 0)
                self.voltage_1 = (self.stm_data_list[6] << 4) + (self.stm_data_list[7] << 0)
                self.pressure_2 = bytes([(self.stm_data_list[8] << 4) + (self.stm_data_list[9] << 0),
                                        (self.stm_data_list[10] << 4) + (self.stm_data_list[11] << 0)])
                self.pressure_2 = kpa_bdk2_parcer.process_row_data(self.pressure_2)
                self.temperature_2 = (self.stm_data_list[12] << 4) + (self.stm_data_list[13] << 0)
                self.voltage_2 = (self.stm_data_list[14] << 4) + (self.stm_data_list[15] << 0)
                self.stm_data_list = []
                self.final_data_list = [self.pressure_1, self.temperature_1, self.voltage_1, self.pressure_2, self.temperature_2, self.voltage_2]
            elif self.stm_addr == 0x0F:
                self.stm_addr_pool = 0
                self.stm_data_list = []
        pass

### для таблицы разобранных данных СТМ БДД
class stm_bdd_data_table(tkinter.Frame):
    def __init__(self, cnf={}, **kw):
        tkinter.Frame.__init__(self, cnf, kw)
        #
        self.title_list = ["Название", "Измер. 1", "Измер. 2"]
        self.names_list = ["Давление, мм рт.мт.", "Темпер.,°С", "Ток потр., 24В, мА"]
        self.data_list = ["{:#02X}".format(0) for i in range(6)]
        #
        self.columns = 3
        self.rows = 4
        self.row_data_len = 3
        #
        self._construct()
        self._insert_name()

    def _construct(self):
        self.cells = []  # теперь создаем лист под будущие ячейки таблицы. В будущем этот лист будет двумерным
        for j in range(self.columns):
            self.cells.append([])  # тут как раз и делаем лист для ячеек двумерным
            for i in range(self.rows):  # в данном цикле мы указываем тип ячейки который будет стоять по координате (j, i)
                if j == 0:
                    self.cells[j].append(cell(self, type="label", justify="center", relief="groove", width=15))
                else:
                    if i == 0: self.cells[j].append(cell(self, type="label", justify="center", relief="groove", width=15))
                    else:
                        self.cells[j].append(cell(self, type="label", justify="center", relief="groove", width=15))
        [self.cells[0][i].place(x=0 * 135, y=i * 25, height=22, width=132) for i in range(self.rows)]
        [self.cells[j][i].place(x=135 + (j-1) * 60, y=i * 25, height=22, width=57) for i in range(self.rows)
         for j in range(1, self.columns)]
        self.config(width=60*(self.columns - 1) + 135, height=self.rows*25)
        pass

    def _insert_name(self):
        [self.cells[0][i].value.set(self.names_list[i-1]) for i in range(1, self.rows)]
        [self.cells[i][0].value.set(self.title_list[i]) for i in range(self.columns)]
        [self.cells[i][0].configure(bg="gray80") for i in range(self.columns)]
        pass

    def insert_data(self, data):
        if isinstance(data, list) is False:
            raise TypeError("Incorrect type")
        elif len(data) != 6:
            raise ValueError("Incorrect length")
        else:
            self.data_list = data
            self.cells[1][1].value.set("{:.2E}".format(self.data_list[0]))
            self.cells[1][2].value.set("{:d}".format(self.data_list[1]))
            self.cells[1][3].value.set("{:d}".format(self.data_list[2]))
            self.cells[2][1].value.set("{:.2E}".format(self.data_list[3]))
            self.cells[2][2].value.set("{:d}".format(self.data_list[4]))
            self.cells[2][3].value.set("{:d}".format(self.data_list[5]))
        pass

### Фрэйм для отдельного БДД
class stm_bdd(tkinter.LabelFrame):
    def __init__(self, cnf={}, **kw):
        self.bdd_id = 0x02
        self.set_enable = True
        for key in sorted(kw):
            if key == "mko":
                self.mko = kw.pop(key)
            elif key == "bdd_id":
                self.bdd_id = kw.pop(key)
            elif key == "set_enable":
                self.set_enable = kw.pop(key)
            else:
                pass

        tkinter.LabelFrame.__init__(self, cnf, kw)
        #
        self.stm_ind_block = stm_bdd_indicator(self, set_enable=self.set_enable)
        self.stm_ind_block.place(x=10, y=10)

        self.stm_row_data_table = stm_bdd_addr_table(self)
        self.stm_row_data_table.place(x=150, y=10)

        self.stm_data_table = stm_bdd_data_table(self)
        self.stm_data_table.place(x=10, y=450)

        self.stm_set_button = tkinter.Button(self, text="Установить СТМ", command=self.set_stm)
        if self.set_enable is True:
            self.stm_set_button.place(x=10, y=300, height=25, width=100)

        self.width = 275
        self.height = 575
        self.config(width=275, height=575)


    def get_data(self):
        list = [self.stm_ind_block.cells[2][i].value.get() for i in range(1, self.stm_ind_block.rows)]
        return list

    def set_stm(self):
        data = self.get_data()
        STM = 0
        for i in range(len(data)):
            STM += (2**(i)) * int(data[i])
        if self.mko:
            self.mko.init()
            self.mko.SendToRT([0x0001, (self.bdd_id << 8), 0x0006, 0x0202, STM], 19, 30, 5)
            pass
        #print(STM)
        pass

    def insert_row_adc_data(self, type="bdd_1", adc1=[0 for i in range(32)], adc2=[0 for i in range(32)]):
        bdd1_list = [adc2[12], adc2[13], adc2[28], adc2[29], adc2[30], adc2[31], adc2[0], adc2[1], adc2[2], adc2[3]]
        bdd2_list = [adc2[14], adc2[15], adc2[4], adc2[5], adc2[6], adc2[7], adc2[8], adc2[9], adc2[10], adc2[11]]
        if type == "bdd_1":
            self.insert_data(bdd1_list)
        elif type == "bdd_2":
            self.insert_data(bdd2_list)
        pass

    def insert_data(self, data):
        if isinstance(data, list) is False:
            raise TypeError("Incorrect type")
        elif len(data) != 10:
            raise ValueError("Incorrect length")
        else:
            self.stm_ind_block.insert_data(data)
            self.stm_row_data_table.insert_data(self.stm_ind_block.logical_data)
            self.stm_data_table.insert_data(self.stm_row_data_table.final_data_list)
        pass

### БЭ ###
### класс с фрэймом для вывод сырых данных СТМ БЭ
class stm_be_indicator(tkinter.Frame):
    def __init__(self, cnf={}, **kw):
        self.mko = None
        self.set_enable = True
        for key in sorted(kw):
            if key == "mko":
                self.mko = kw.pop(key)
            elif key == "set_enable":
                self.set_enable = kw.pop(key)
            else:
                pass

        tkinter.Frame.__init__(self, cnf, kw)
        self.columns = 3
        self.rows = 40
        self.names_list = ["БЭ_С01", "БЭ_С02", "БЭ_С03", "БЭ_С04", "БЭ_С05", "БЭ_С06", "БЭ_С07", "БЭ_С08",
                           "БЭ_С09", "БЭ_С10", "БЭ_С11", "БЭ_С12", "БЭ_С13", "БЭ_С14", "БЭ_С15", "БЭ_С16",
                           "БЭ_С17", "БЭ_С18", "БЭ_С19", "БЭ_С20", "БЭ_С21", "БЭ_С22", "БЭ_С23", "БЭ_С24",
                           "БЭ_С25", "БЭ_С26", "БЭ_С27", "БЭ_С28", "БЭ_С29", "БЭ_С30", "БЭ_С31", "БЭ_С32",
                           "БЭ_С33", "БЭ_С34", "БЭ_С35", "БЭ_С36", "ПБЭБДК", "АМКО"]
        self.title_list = ["Имя", "Напр.,В"]
        self.row_data_len = 38
        self.row_data_list = [0 for i in range(self.row_data_len)]  # value matches "nd"
        self.logical_data = ["nd" for i in range(self.row_data_len)]  # logical meaning; z - meaning undefined
        self.bound = [[1900, 1950], [1900, 1950], # 1  # 2
                      [1900, 1950], [1900, 1950],
                      [1900, 1950], [1900, 1950],
                      [1900, 1950], [1900, 1950],
                      [1900, 1950], [1900, 1950],
                      [1900, 1950], [1900, 1950],
                      [1900, 1950], [1900, 1950],
                      [1900, 1950], [1900, 1950],
                      [1900, 1950], [1900, 1950],
                      [1900, 1950], [1900, 1950],
                      [1900, 1950], [1900, 1950],
                      [1900, 1950], [1900, 1950],
                      [1900, 1950], [1900, 1950],
                      [1900, 1950], [1900, 1950],
                      [1900, 1950], [1900, 1950],
                      [1900, 1950], [1900, 1950],
                      [1900, 1950], [1900, 1950],
                      [1900, 1950], [1900, 1950],
                      [1900, 1950], [1900, 1950],
                      [1900, 1950], [1900, 1950]] # 37 # 38
        self.used_colors = {"nd": "Coral2", "1": "DeepSkyBlue3", "0": "PaleGreen3"}
        self._construct()
        self._insert_name()
        self.parsing()

        pass

    def _construct(self):
        self.cells = []  # теперь создаем лист под будущие ячейки таблицы. В будущем этот лист будет двумерным
        for j in range(self.columns):
            self.cells.append([])  # тут как раз и делаем лист для ячеек двумерным
            for i in range(self.rows):  # в данном цикле мы указываем тип ячейки который будет стоять по координате (j, i)
                if j == 0:
                    self.cells[j].append(cell(self, type="label", justify="center", relief="groove", width=6 ))
                elif j == 1:
                    if i == 0: self.cells[j].append(cell(self, type="label", justify="center", relief="groove", width=6))
                    elif i == self.rows//2: self.cells[j].append(cell(self, type="label", justify="center", relief="groove", width=6))
                    else:
                        self.cells[j].append(cell(self, type="label", justify="center", relief="raised", width=5))
                elif j == 2:
                    self.cells[j].append(cell(self, type="checkbutton", justify="center", relief="flat"))
        [self.cells[j][i].place(x=j * 50, y=i * 25, height=22, width=47) for i in range(self.rows//2)
         for j in range(self.columns)]
        [self.cells[j][i].place(x=125 + j * 50, y=(i - self.rows//2) * 25, height=22, width=47) for i in range(self.rows//2, self.rows)
         for j in range(self.columns)]
        if self.set_enable is True:
            [self.cells[2][i].place(x=2 * 50, y=i * 25, height=22, width=22) for i in range(self.rows//2)]
            self.cells[2][0].bind('<Button-1>', self.all_ch_but_set_1)
            [self.cells[2][i].place(x=125 + 2 * 50, y=(i - self.rows//2) * 25, height=22, width=22) for i in range(self.rows//2, self.rows)]
            self.cells[2][self.rows//2].bind('<Button-1>', self.all_ch_but_set_2)
        self.config(width=50*2 + 50*2 + 25 + 25, height=20*25)
        pass

    def all_ch_but_set_1(self, event):
        if self.cells[2][0].value.get() == "1":
            [self.cells[2][i+1].value.set("0") for i in range((self.rows//2)-1)]
        else:
            [self.cells[2][i+1].value.set("1") for i in range((self.rows//2)-1)]

    def all_ch_but_set_2(self, event):
        if self.cells[2][self.rows//2].value.get() == "1":
            [self.cells[2][i+1].value.set("0") for i in range((self.rows//2), self.rows-1)]
        else:
            [self.cells[2][i+1].value.set("1") for i in range((self.rows//2), self.rows-1)]

    def parsing(self):
        self.logical_data = []
        for i in range(len(self.row_data_list)):
            if self.row_data_list[i] < self.bound[i][0]:  # check excess 100kOhm level
                self.logical_data.append("1")
            elif self.row_data_list[i] > self.bound[i][1]:  # lower than 10kOhm
                self.logical_data.append("0")
            else:  # check that value is in range 10-100kOhm
                self.logical_data.append("nd")
            if i < (self.row_data_len//2):
                self.cells[1][i + 1].configure(bg=self.used_colors[self.logical_data[i]])
                self.cells[1][i + 1].value.set(self.row_data_list[i])
            else:
                self.cells[1][i + 2].configure(bg=self.used_colors[self.logical_data[i]])
                self.cells[1][i + 2].value.set(self.row_data_list[i])
        #print(self.logical_data)
        pass

    def insert_data(self, data):
        #print(type(data), isinstance(data, list))
        if isinstance(data, list) is False:
            raise TypeError("Incorrect type")
        elif len(data) != self.row_data_len:
            raise ValueError("Incorrect length")
        else:
            self.row_data_list = data
            self.parsing()
        pass

    def _insert_name(self):
        [self.cells[0][i].value.set(self.names_list[i-1]) for i in range(1, self.rows//2)]
        [self.cells[0][i].value.set(self.names_list[i-2]) for i in range(self.rows // 2, self.rows)]
        [self.cells[i][0].value.set(self.title_list[i]) for i in range(self.columns-1)]
        [self.cells[i][self.rows // 2].value.set(self.title_list[i]) for i in range(self.columns-1)]
        [self.cells[i][0].configure(bg="gray80") for i in range(self.columns-1)]
        [self.cells[i][self.rows // 2].configure(bg="gray80") for i in range(self.columns-1)]
        pass

### для таблицы разобранных адресов и кусков данных СТМ БДД
class stm_be_addr_table(tkinter.Frame):
    def __init__(self, cnf={}, **kw):
        tkinter.Frame.__init__(self, cnf, kw)
        #
        self.title_list = ["Адрес", "Данные"]
        self.names_list = ["{}".format(i) for i in range(16)]
        self.stm_list = ["0x {:#04X}".format(0) for i in range(16)]
        #
        self.columns = len(self.title_list)
        self.rows = len(self.names_list) + 1
        self.row_data_len = 38
        #
        self._construct()
        self._insert_name()
        #
        self.stm_addr = 0
        self.stm_data = 0
        self.stm_addr_list = []
        self.stm_data_list = []
        self.stm_pbebdk = 0
        self.stm_amko = 0
        # stm_data todo: think about "How to construct correct data table?"
        #
        self.stm_addr_pool = 0  # variable, which storage state filling all address (15 - address pool is fool)
        self.used_colors = {"nd": "Coral2", "1": "DeepSkyBlue3", "0": "PaleGreen3"}

    def _construct(self):
        self.cells = []  # теперь создаем лист под будущие ячейки таблицы. В будущем этот лист будет двумерным
        for j in range(self.columns):
            self.cells.append([])  # тут как раз и делаем лист для ячеек двумерным
            for i in range(
                    self.rows):  # в данном цикле мы указываем тип ячейки который будет стоять по координате (j, i)
                if j == 0:
                    self.cells[j].append(
                        cell(self, type="label", justify="center", relief="groove", width=15 ))
                elif j == 1:
                    if i == 0:
                        self.cells[j].append(
                            cell(self, type="label", justify="center", relief="groove", width=15 ))
                    else:
                        self.cells[j].append(cell(self, type="label", justify="center", relief="groove", width=15))
        [self.cells[0][i].place(x=0, y=i * 25, height=22, width=47) for i in range(self.rows)]
        [self.cells[1][i].place(x=50, y=i * 25, height=22, width=72) for i in range(self.rows)]
        self.config(width=50 + 75, height=self.rows * 25)
        pass

    def _insert_name(self):
        [self.cells[0][i].value.set(self.names_list[i - 1]) for i in range(1, self.rows)]
        [self.cells[i][0].value.set(self.title_list[i]) for i in range(self.columns)]
        [self.cells[i][0].configure(bg="gray80") for i in range(self.columns)]
        pass

    def insert_data(self, data):
        if isinstance(data, list) is False:
            raise TypeError("Incorrect type")
        elif len(data) != self.row_data_len:
            raise ValueError("Incorrect length")
        else:
            self.stm_list = data
            self.parsing()
        pass

    def parsing(self):
        self.stm_data = 0
        self.stm_addr = 0
        # print(self.stm_list)
        for i in range(len(self.stm_list)):
            if self.stm_list[i] == "nd" and self._error_counter >= 1:
                [self.cells[i][j].configure(bg=self.used_colors[self.stm_list[i]])
                 for i in range(self.columns) for j in range(1, self.rows)]
                return
            elif self.stm_list[i] == "nd":
                self._error_counter += 1
            else:
                self._error_counter = 0
                if 0 <= i < 4:
                    # print(self.stm_addr)
                    self.stm_addr += ((int(self.stm_list[i])) << (i - 0))
                elif 4 <= i < 36:
                    self.stm_data += ((int(self.stm_list[i])) << (i - 4))
                elif i == 36:
                    self.stm_pbebdk = int(self.stm_list[i])
                elif i == 37:
                    self.stm_amko = int(self.stm_list[i])
        if self._error_counter == 0:
            if self.stm_addr == self.stm_addr_pool:
                self.stm_addr_pool += 1
                self.stm_data_list.append(self.stm_data)
            [self.cells[i][j].configure(bg="grey95")
             for i in range(self.columns) for j in range(1, self.rows)]
            stm_data_list = [(self.stm_data >> (i*8)) & 0xFF for i in range(4)]
            stm_data_list = tuple(stm_data_list)
            self.cells[1][self.stm_addr + 1].value.set("{0[0]:02X} {0[1]:02X} {0[2]:02X} {0[3]:02X}".format(stm_data_list))
            self.cells[0][self.stm_addr + 1].configure(bg=self.used_colors["0"])
            self.cells[1][self.stm_addr + 1].configure(bg=self.used_colors["0"])
            if self.stm_addr == 0x0F and self.stm_addr_pool == 16:  # место для парсинга всех накопленных данных
                self.stm_addr_pool = 0
                self.stm_data_list = []
            elif self.stm_addr == 0x0F:
                self.stm_addr_pool = 0
                self.stm_data_list = []
                pass
        pass

### Фрэйм для отдельного БЭ
class stm_be(tkinter.LabelFrame):
    def __init__(self, cnf={}, **kw):
        self.set_enable = True
        for key in sorted(kw):
            if key == "mko":
                self.mko = kw.pop(key)
            elif key == "set_enable":
                self.set_enable = kw.pop(key)
            else:
                pass

        tkinter.LabelFrame.__init__(self, cnf, kw)
        #
        self.stm_ind_block = stm_be_indicator(self)
        self.stm_ind_block.place(x=10, y=10)

        self.stm_addr_block = stm_be_addr_table(self)
        self.stm_addr_block.place(x=260, y=10)

        self.stm_set_button = tkinter.Button(self, text="Установить СТМ", command=self.set_stm)
        if self.set_enable is True:
            self.stm_set_button.place(x=10, y=525, height=25, width=100)

        self.config(width=395, height=575)

    def get_data(self):
        list = [self.stm_ind_block.cells[2][i].value.get() for i in range(1, self.stm_ind_block.rows//2)]
        list.extend([self.stm_ind_block.cells[2][i].value.get() for i in range(self.stm_ind_block.rows//2+1, self.stm_ind_block.rows)])
        return list

    def set_stm(self):
        data = self.get_data()
        STM = 0
        for i in range(len(data)):
            STM += (2**(i)) * int(data[i])
        if self.mko:
            self.mko.init()
            self.mko.SendToRT([0x0002, (STM >> 32) & 0xFFFF, (STM >> 16) & 0xFFFF, (STM >> 0) & 0xFFFF], 19, 30, 4)
            pass
        #print(hex(STM))
        pass


    def insert_data(self, data):
        if isinstance(data, list) is False:
            raise TypeError("Incorrect type")
        elif len(data) != 38:
            raise ValueError("Incorrect length")
        else:
            self.stm_ind_block.insert_data(data)
            self.stm_addr_block.insert_data(self.stm_ind_block.logical_data)
        pass

    def insert_row_adc_data(self, adc1=[0 for i in range(32)], adc2=[0 for i in range(32)]):
        bdd1_list = [adc2[12], adc2[13], adc2[28], adc2[29], adc2[30], adc2[31], adc2[0], adc2[1], adc2[2], adc2[3]]
        bdd2_list = [adc2[14], adc2[15], adc2[4], adc2[5], adc2[6], adc2[7], adc2[8], adc2[9], adc2[10], adc2[11]]
        be_list = [adc1[20], adc1[21], adc1[22], adc1[23], adc1[24], adc1[25], adc1[26], adc1[27], adc1[28], adc1[29],
                   adc1[30], adc1[31], adc1[0], adc1[1], adc1[2], adc1[3], adc1[4], adc1[5], adc1[6], adc1[7],
                   adc1[8], adc1[9], adc1[10], adc1[11], adc2[20], adc2[21], adc2[22], adc2[23], adc2[24], adc2[25],
                   adc2[26], adc2[27], adc2[16], adc2[17], adc2[18], adc2[19], adc1[18], adc1[19]]
        self.insert_data(be_list)
        pass

### окно для вывод СТМ БДК2
class window(tkinter.Toplevel):
    def __init__(self, cnf={}, **kw):
        # создание третьего окна для тестирования памяти БДД
        self.mko = None
        for key in sorted(kw):
            if key == "mko":
                self.mko = kw.pop(key)
            else:
                pass

        tkinter.Toplevel.__init__(self, cnf, kw)

        self.title("СТМ БДК2")
        self.geometry('1000x600')
        self.resizable(False, False)
        self.protocol("WM_DELETE_WINDOW", lambda: self.withdraw())
        self.withdraw()

        #fill window
        self.bdd1_stm = stm_bdd(self, text="БДД 1", mko=self.mko, bdd_id=0x02)
        self.bdd1_stm.place(x=10, y=10)

        self.bdd2_stm = stm_bdd(self, text="БДД 2", mko=self.mko, bdd_id=0x03)
        self.bdd2_stm.place(x=300, y=10)

        self.be_stm = stm_be(self, text="БЭ БДК2", mko=self.mko)
        self.be_stm.place(x=590, y=10)

    def insert_data(self, bdd1_data=[1900 for i in range(10)], bdd2_data=[1900 for i in range(10)], be_data=[1900 for i in range(38)]):
        self.bdd1_stm.insert_data(bdd1_data)
        self.bdd2_stm.insert_data(bdd2_data)
        self.be_stm.insert_data(be_data)
        #print(self.bdd1_stm.stm_ind_block.logical_data)
        pass

    def insert_row_adc_data(self, adc1=[0 for i in range(32)], adc2=[0 for i in range(32)]):
        bdd1_list = [adc2[12], adc2[13], adc2[28], adc2[29], adc2[30], adc2[31], adc2[0], adc2[1], adc2[2], adc2[3]]
        bdd2_list = [adc2[14], adc2[15], adc2[4], adc2[5], adc2[6], adc2[7], adc2[8], adc2[9], adc2[10], adc2[11]]
        be_list = [adc1[20], adc1[21], adc1[22], adc1[23], adc1[24], adc1[25], adc1[26], adc1[27], adc1[28], adc1[29],
                   adc1[30], adc1[31], adc1[0], adc1[1], adc1[2], adc1[3], adc1[4], adc1[5], adc1[6], adc1[7],
                   adc1[8], adc1[9], adc1[10], adc1[11], adc2[20], adc2[21], adc2[22], adc2[23], adc2[24], adc2[25],
                   adc2[26], adc2[27], adc2[16], adc2[17], adc2[18], adc2[19], adc1[18], adc1[19]]
        self.insert_data(bdd1_data=bdd1_list, bdd2_data=bdd2_list, be_data=be_list)
        pass

### фрэйм для вывода СТМ БДК2
class frame(tkinter.Frame):
    def __init__(self, cnf={}, **kw):
        # создание третьего окна для тестирования памяти БДД
        self.mko = None
        for key in sorted(kw):
            if key == "mko":
                self.mko = kw.pop(key)
            else:
                pass

        tkinter.Frame.__init__(self, cnf, kw)
        self.configure(height=1000, width=600)

        #fill window
        self.bdd1_stm = stm_bdd(self, text="БДД 1", mko=self.mko, bdd_id=0x02)
        self.bdd1_stm.place(x=10, y=10)

        self.bdd2_stm = stm_bdd(self, text="БДД 2", mko=self.mko, bdd_id=0x03)
        self.bdd2_stm.place(x=300, y=10)

        self.be_stm = stm_be(self, text="БЭ БДК2", mko=self.mko)
        self.be_stm.place(x=590, y=10)

    def insert_data(self, bdd1_data=[1900 for i in range(10)], bdd2_data=[1900 for i in range(10)], be_data=[1900 for i in range(38)]):
        self.bdd1_stm.insert_data(bdd1_data)
        self.bdd2_stm.insert_data(bdd2_data)
        self.be_stm.insert_data(be_data)
        pass

    def insert_row_adc_data(self, adc1=[0 for i in range(32)], adc2=[0 for i in range(32)]):
        bdd1_list = [adc2[12], adc2[13], adc2[28], adc2[29], adc2[30], adc2[31], adc2[0], adc2[1], adc2[2], adc2[3]]
        bdd2_list = [adc2[14], adc2[15], adc2[4], adc2[5], adc2[6], adc2[7], adc2[8], adc2[9], adc2[10], adc2[11]]
        be_list = [adc1[20], adc1[21], adc1[22], adc1[23], adc1[24], adc1[25], adc1[26], adc1[27], adc1[28], adc1[29],
                   adc1[30], adc1[31], adc1[0], adc1[1], adc1[2], adc1[3], adc1[4], adc1[5], adc1[6], adc1[7],
                   adc1[8], adc1[9], adc1[10], adc1[11], adc2[20], adc2[21], adc2[22], adc2[23], adc2[24], adc2[25],
                   adc2[26], adc2[27], adc2[16], adc2[17], adc2[18], adc2[19], adc1[18], adc1[19]]
        self.insert_data(bdd1_data=bdd1_list, bdd2_data=bdd2_list, be_data=be_list)
        pass
