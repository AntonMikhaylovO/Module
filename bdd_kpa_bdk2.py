import stm_bdk2
import tkinter
import tk_table


class Led(tkinter.Canvas):
    def __init__(self, root, color_error="DeppSkyBlue3", color_on="PaleGreen3", color_off="gray97", **kw):
        tkinter.Canvas.__init__(self, root, kw, relief="raised", bg=color_off, bd=2)
        self.color_on = color_on
        self.color_error = color_error
        self.color_off = color_off

    def on(self, state = "on"):
        if state == "on":
            self.config(bg = self.color_on)
        elif state == "error":
            self.config(bg = self.color_error)
        else:
            self.config(bg = self.color_on)
        pass

    def off(self):
        self.config(bg = self.color_off)
        pass

    def color(self, color_error = "DeppSkyBlue3", color_on = "dark sea green", color_off = "black"):
        self.color_on = color_on
        self.color_error = color_error
        self.color_off = color_off
        pass


class BddDataTable(tkinter.Frame):
    def __init__(self, cnf={}, **kw):
        self.title_text = "Empty"
        self.data_num = 4
        for key in sorted(kw):
            if key == "title_text":
                self.title_text = kw.pop(key)
            elif key == "data_num":
                self.data_num = kw.pop(key)

        tkinter.Frame.__init__(self, cnf, kw)

        self.titles = ["Название", "Значение"]
        self.data_names = ["Давление, мм рт.ст.", "Температура, °С", "Напряжение питания, В", "Ток потребления, мА"]

        self.bdd_table_label = tkinter.Label(self, text=self.title_text, width=35, justify="center", font="Arial 11")
        self.bdd_table_label.place(x=0, y=0, width = 225)
        self.bdd_table = tk_table.array_table(self, columns=2, rows=self.data_num+1)
        [self.bdd_table.cells[j][i].configure(width=10+(1-j)*10) for i in range(self.data_num+1) for j in range(2)]
        self.bdd_table.place(x=0, y=40)
        self._insert_name()

        self.width = 225
        self.height = 20*(self.data_num + 1) + 45
        self.config(width=self.width, height=self.height)

    def insert_data(self, data, state=[]):  # data - лист с данными для БДД в формате заголовка к таблице
        if data is not None:
            for i in range(len(data)):
                self.bdd_table.cells[1][i+1].value.set(data[i])
        if state is not None:
            for i in range(len(state)):
                color = "DeppSkyBlue3" if state[i] == 0 else "dark sea green"
                self.bdd_table.cells[1][i + 1].configure(bg=color)
        else:
            for i in range(len(data)):
                color = "gray95"
                self.bdd_table.cells[1][i + 1].configure(bg=color)
            pass

    def _insert_name(self):
        for i in range(len(self.titles)):
            self.bdd_table.cells[i][0].value.set(self.titles[i])
            self.bdd_table.cells[i][0].configure(justify="center")
        for i in range(len(self.data_names)):
            self.bdd_table.cells[0][i+1].value.set(self.data_names[i])
        pass


class Frame(tkinter.Frame):
    def __init__(self, cnf={}, **kw):
        self.serial_port = None
        for key in sorted(kw):
            if key == "serial_port":
                self.serial_port = kw.pop(key)
        tkinter.Frame.__init__(self, cnf, kw)
        # отображение СТМ для БДД1 и БДД2
        self.stm_bdd_1_frame = stm_bdk2.stm_bdd(self, set_enable=False, bdd_id=0x02, text="СТМ БДД 1")
        self.stm_bdd_1_frame.place(x=440, y=10)
        self.stm_bdd_2_frame = stm_bdk2.stm_bdd(self, set_enable=False, bdd_id=0x03, text="СТМ БДД 2")
        self.stm_bdd_2_frame.place(x=720, y=10)
        # команды управления
        self.KU_label = tkinter.Label(self, text="Команды управления", font="Arial 11")
        self.KU_label.place(x=10, y=10, width=180)
        self.KU_on_button = tkinter.Button(self, text="ВКЛ", bg="grey90",
                                           command=lambda: self.ku_command(ku_type="mku_on"))
        self.KU_on_button.place(x=10, y=40, width=70, height=30)
        self.KU_on_button = tkinter.Button(self, text="ВЫКЛ", bg="grey90",
                                           command=lambda: self.ku_command(ku_type="mku_off"))
        self.KU_on_button.place(x=110, y=40, width=70, height=30)
        # технологические команды
        self.TKU_label = tkinter.Label(self, text="Технологические команды", font="Arial 11")
        self.TKU_label.place(x=220, y=10, width=180)
        self.KU_on_button = tkinter.Button(self, text="ВКЛ", bg="grey90",
                                           command=lambda: self.ku_command(ku_type="tku_on"))
        self.KU_on_button.place(x=220, y=40, width=70, height=30)
        self.KU_on_button = tkinter.Button(self, text="ВЫКЛ", bg="grey90",
                                           command=lambda: self.ku_command(ku_type="tku_off"))
        self.KU_on_button.place(x=320, y=40, width=70, height=30)
        # label_frame для БДД1
        self.bdd1_label_frame = tkinter.LabelFrame(self, text="БДД1", width=425, height=200)
        self.bdd1_label_frame.place(x=10, y=100)
        # запросы данных БДД1
        self.bdd1_data_request_label = tkinter.Label(self.bdd1_label_frame, text="Запрос данных", font="Arial 11")
        self.bdd1_data_request_label.place(x=0, y=0, width=160)
        self.bdd1_press_req_button = tkinter.Button(self.bdd1_label_frame, text="Давление", bg="grey90",
                                                    command=lambda: self.bdd_request(bdd_id=0x02, com_type="pressure"))
        self.bdd1_press_req_button.place(x=30, y=35, width=100, height=30)
        self.bdd1_temp_req_button = tkinter.Button(self.bdd1_label_frame, text="Температура", bg="grey90",
                                                   command=lambda: self.bdd_request(bdd_id=0x02, com_type="temp"))
        self.bdd1_temp_req_button.place(x=30, y=70, width=100, height=30)
        self.bdd1_temp_req_button = tkinter.Button(self.bdd1_label_frame, text="Кадр", bg="grey90",
                                                   command=lambda: self.bdd_request(bdd_id=0x02, com_type="frame"))
        self.bdd1_temp_req_button.place(x=30, y=105, width=100, height=30)
        # таблица отображения данных БДД1
        self.bdd1_table = BddDataTable(self.bdd1_label_frame, title_text="Данные")
        self.bdd1_table.place(x=190, y=0)
        # отбражение ККДД1
        tkinter.Label(self.bdd1_label_frame, text="ККДД", ).place(x=10, y=155)
        self.kkdd1_led = Led(self.bdd1_label_frame, color_error="orange2", width=30, height=20)
        self.kkdd1_led.place(x=60, y=150)
        # label_frame для БДД2
        self.bdd2_label_frame = tkinter.LabelFrame(self, text="БДД2", width=425, height=200)
        self.bdd2_label_frame.place(x=10, y=350)
        # запросы данных БДД2
        self.bdd2_data_request_label = tkinter.Label(self.bdd2_label_frame, text="Запрос данных", font="Arial 11")
        self.bdd2_data_request_label.place(x=0, y=0, width=160)
        self.bdd2_press_req_button = tkinter.Button(self.bdd2_label_frame, text="Давление", bg="grey90",
                                                    command=lambda: self.bdd_request(bdd_id=0x03, com_type="pressure"))
        self.bdd2_press_req_button.place(x=30, y=35, width=100, height=30)
        self.bdd2_temp_req_button = tkinter.Button(self.bdd2_label_frame, text="Температура", bg="grey90",
                                                   command=lambda: self.bdd_request(bdd_id=0x03, com_type="temp"))
        self.bdd2_temp_req_button.place(x=30, y=70, width=100, height=30)
        self.bdd2_temp_req_button = tkinter.Button(self.bdd2_label_frame, text="Кадр", bg="grey90",
                                                   command=lambda: self.bdd_request(bdd_id=0x03, com_type="frame"))
        self.bdd2_temp_req_button.place(x=30, y=105, width=100, height=30)
        # таблица отображения данных БДД2
        self.bdd2_table = BddDataTable(self.bdd2_label_frame, title_text="Данные")
        self.bdd2_table.place(x=190, y=0)
        # отбражение ККДД2
        tkinter.Label(self.bdd2_label_frame, text="ККДД", ).place(x=10, y=155)
        self.kkdd2_led = Led(self.bdd2_label_frame, color_error="orange2", width=30, height=20)
        self.kkdd2_led.place(x=60, y=150)
        pass

    def ku_command(self, ku_type="mku_on"):
        if ku_type == "mku_on":
            self.serial_port.kpa_request(req_type="kpa_bdd_mku_on")
            pass
        elif ku_type == "mku_off":
            self.serial_port.kpa_request(req_type="kpa_bdd_mku_off")
            pass
        elif ku_type == "tku_on":
            self.serial_port.kpa_request(req_type="kpa_bdd_tku_on")
            pass
        elif ku_type == "tku_off":
            self.serial_port.kpa_request(req_type="kpa_bdd_tku_off")
            pass
        pass

    def bdd_request(self, bdd_id=0x02, com_type="pressure"):
        if com_type == "pressure":
            self.serial_port.kpa_request(req_type="bdd_pressure", bdd_id="0x{:02X}".format(bdd_id))
            pass
        elif com_type == "temp":
            self.serial_port.kpa_request(req_type="bdd_temp", bdd_id="0x{:02X}".format(bdd_id))
            pass
        elif com_type == "frame":
            self.serial_port.kpa_request(req_type="bdd_frame", bdd_id="0x{:02X}".format(bdd_id))
            pass
        pass

    def refresh_data(self):
        # заолняем СТМ данные
        self.stm_bdd_1_frame.insert_row_adc_data(type="bdd_1",
                                                 adc1=self.serial_port.kpa_data.adc_list_1,
                                                 adc2=self.serial_port.kpa_data.adc_list_2)
        self.stm_bdd_2_frame.insert_row_adc_data(type="bdd_2",
                                                 adc1=self.serial_port.kpa_data.adc_list_1,
                                                 adc2=self.serial_port.kpa_data.adc_list_2)
        # заполняем таблицы с данными БДД1 и БДД2
        self.serial_port.kpa_data.bdd_status_refresh()
        self.bdd1_table.insert_data(self.serial_port.form_bdd_data(bdd_id="0x02"),
                                    state=self.serial_port.kpa_data.bdd1_status)
        self.bdd2_table.insert_data(self.serial_port.form_bdd_data(bdd_id="0x03"),
                                    state=self.serial_port.kpa_data.bdd2_status)
        # отбражение состояния ККДД
        self.kkdd1_led.on(state=self.serial_port.kpa_data.bdd1_kkdd)
        self.kkdd2_led.on(state=self.serial_port.kpa_data.bdd2_kkdd)
        pass


