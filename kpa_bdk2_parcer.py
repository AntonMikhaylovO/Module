
class data():
    def __init__(self):
        self.row_data = []
        self.gpio = 0x00  # [2,1,0]=[P_ON30N, P_ON30P, P_ON27]
        self.ku_pulse = 0x00  # [9..3]=[BDD_TRK_OFF, BDD_TRK_ON, BDD_MRK_OFF, BDD_MRK_ON, BE_MRK_OFF, BE_MRK_ON2, BE_MRK_ON1]
        self.pulse_time = 0x0000  # значение в мс
        self.adc_list_1 = [0 for i in range(32)]
        self.adc_list_2 = [0 for i in range(32)]
        self.bdd1_curr = 0
        self.bdd2_curr = 0
        self.be_curr = 0
        self.kpa_volt = 0
        self.kpa_be_a=0
        self.kpa_be_b=0
        self.kpa_bdd1_a=0
        self.kpa_bdd2_a=0
        self.kpa_bdd1_b=0
        self.kpa_bdd2_b=0
        self.kpa_data_status = {"kpa_volt": 0,
                                "bdd2_curr": 0,
                                "bdd1_curr": 0,
                                "be_curr": 0,
                                "bdd1_temp": 0,
                                "bdd2_temp": 0,
                                "bdd1_pressure": 0,
                                "bdd2_pressure": 0}
        self.bdd1_status = [0, 0, 0, 0]
        self.bdd2_status = [0, 0, 0, 0]
        self.muart_data = []
        self.bdd1_pressure = 0
        self.bdd2_pressure = 0
        self.bdd1_temp = 0
        self.bdd2_temp = 0
        self.bdd1_kkdd = "error"
        self.bdd2_kkdd = "error"
        self.stm_be_row = [0 for i in range(38)]
        self.stm_bdd1_row = [0 for i in range(10)]
        self.stm_bdd2_row = [0 for i in range(10)]
        pass

    def parsing(self, row_data):
        return_str = ""
        self.row_data = row_data
        if len(self.row_data) < 6:
            return_str = "ANKNOWN COMMAND"
        elif self.row_data[0] == 0xEE:
            if self.row_data[1] == 0xB0 and self.row_data[5] == 0x0E:  # команда для проверки работоспособности БДД
                return_str = "Ack OK"
            elif self.row_data[1] == 0xB1 and self.row_data[5] == 0x0E:  # команда для установки статических портов [2,1,0]=[P_ON30N, P_ON30P, P_ON27]
                return_str = "GPIO SET"
            elif self.row_data[1] == 0xB2 and self.row_data[5] == 0x0E:  # запрос сотстояни статических портов [2,1,0]=[P_ON30N, P_ON30P, P_ON27]
                self.gpio = self.row_data[3]
                return_str = "GPIO GET"
            elif self.row_data[1] == 0xB3 and self.row_data[5] == 0x0E:  # импульс на портах : [9..3]=[BDD_TRK_OFF, BDD_TRK_ON, BDD_MRK_OFF, BDD_MRK_ON, BE_MRK_OFF, BE_MRK_ON2, BE_MRK_ON1]
                self.ku_pulse = int.from_bytes(self.row_data[3:5], byteorder="big", signed=False)
                return_str = "KU START"
            elif self.row_data[1] == 0xB4 and self.row_data[5] == 0x0E:  # установка времени импульса КУ
                self.pulse_time = int.from_bytes(self.row_data[3:5], byteorder="big", signed=False)
                return_str = "SET KU TIME"
            elif self.row_data[1] == 0xB5 and self.row_data[70] == 0x0E:  # получение всех данных с АЦП
                self.bdd1_curr =  self.kpa_bdd1_a*(int.from_bytes(self.row_data[29:31], byteorder='big') & 0x0FFF)+self.kpa_bdd1_b
                #self.bdd1_curr = self.bdd1_curr if self.bdd1_curr > 30 else 0
                self.bdd2_curr =  self.kpa_bdd2_a*(int.from_bytes(self.row_data[31:33], byteorder='big') & 0x0FFF)+self.kpa_bdd2_b
                #self.bdd2_curr = self.bdd2_curr if self.bdd2_curr > 30 else 0
                self.be_curr =  self.kpa_be_a*(int.from_bytes(self.row_data[33:35], byteorder='big') & 0x0FFF)+self.kpa_be_b
                #self.be_curr = self.be_curr if self.be_curr > 30 else 0
                self.kpa_volt = 0.0176 * (int.from_bytes(self.row_data[35:37], byteorder='big') & 0x0FFF) + 0.32
                self.kpa_volt = self.kpa_volt if self.kpa_volt > 10 else 0
                self.adc_list_1 = [(int.from_bytes(self.row_data[5 + i * 2:7 + i * 2], byteorder='big') & 0x0FFF) for i
                                   in range(32)]
                self.stm_be_row, self.stm_bdd1_row, self.stm_bdd2_row = stm_list_form(self.adc_list_1, self.adc_list_2)
                self.bdd1_kkdd = "error" if self.adc_list_1[16] > 1800 else "on"
                self.bdd2_kkdd = "error" if self.adc_list_1[17] > 1800 else "on"
                return_str = "ADC GET 1"
            elif self.row_data[1] == 0xC5 and self.row_data[70] == 0x0E:  # получение всех данных с АЦП
                self.adc_list_2 = [(int.from_bytes(self.row_data[5 + i * 2:7 + i * 2], byteorder='big') & 0x0FFF) for i
                                   in range(32)]
                self.stm_be_row, self.stm_bdd1_row, self.stm_bdd2_row = stm_list_form(self.adc_list_1, self.adc_list_2)
                return_str = "ADC GET 2"
            elif self.row_data[1] == 0xB6 and self.row_data[13] == 0x0E:  # получение данных с АЦП - напряжение и мощность
                for var in self.row_data[31:35]:
                    var &= 0x0F
                self.bdd1_curr = 0.45 * int.from_bytes(self.row_data[31:33], byteorder='big') + 32.4
                self.bdd2_curr = 0.45 * int.from_bytes(self.row_data[31:33], byteorder='big') + 32.4
                self.be_curr = 0.45 * int.from_bytes(self.row_data[31:33], byteorder='big') + 32.4
                self.kpa_volt = 0.01767 * int.from_bytes(self.row_data[35:37], byteorder='big') + 0.42
                return_str = "ADC_POWER GET"
            elif self.row_data[1] == 0xB7 and self.row_data[5] == 0x0E:  # отправка данных в UMART
                return_str = "SEND UMART"
            elif self.row_data[1] == 0xB8:  # прием данных из UMART
                try:
                    if self.row_data[5 + self.row_data[4]] == 0x0E:
                        self.muart_data = self.row_data[5:(5 + self.row_data[4])]
                        if len(self.muart_data) > 5:
                                if self.muart_data[3] == 0x03:
                                    if self.muart_data[4] == 0x01:  # давление
                                        row_data = self.muart_data[6:8]
                                        if self.muart_data[1] == 0x02:
                                            self.bdd1_pressure = process_row_data(row_data)
                                        elif self.muart_data[1] == 0x03:
                                            self.bdd2_pressure = process_row_data(row_data)
                                    elif self.muart_data[4] == 0x02:  # темепратура бдд Pt1000
                                        if self.muart_data[1] == 0x02:
                                            self.bdd1_temp = (int.from_bytes(self.muart_data[6:8], byteorder='big', signed=True)) / 256
                                        elif self.muart_data[1] == 0x03:
                                            self.bdd2_temp = (int.from_bytes(self.muart_data[6:8], byteorder='big', signed=True)) / 256
                        return_str = "RECEIVE UMART"
                except IndexError:
                    self.muart_data = []
                    return_str = "ANKNOWN COMMAND"
        else:
            return_str = "ANKNOWN COMMAND"
        self.status_calculate()
        return return_str

    def status_calculate(self):
        for key, var in self.kpa_data_status.items():
            #print(key, var)
            if key == "kpa_volt":
                status = 1 if 23 < self.kpa_volt < 32 else 0
            elif key == "bdd1_curr":
                status = 1 if 80 < self.bdd1_curr < 150 else 0
            elif key == "bdd2_curr":
                status = 1 if 80 < self.bdd2_curr < 150 else 0
            elif key == "be_curr":
                status = 1 if 300 < self.be_curr < 600 else 0
            elif key == "bdd1_temp":
                status = 1 if 20 < self.bdd1_temp < 45 else 0
            elif key == "bdd2_temp":
                status = 1 if 20 < self.bdd2_temp < 45 else 0
            elif key == "bdd1_pressure":
                status = 1 if 500 < self.bdd1_pressure < 950 else 0
            elif key == "bdd2_pressure":
                status = 1 if 500 < self.bdd2_pressure < 950 else 0
            else:
                status = 0
                pass
            self.kpa_data_status[key] = status
        pass

    def bdd_status_refresh(self):
        self.bdd1_status = [self.kpa_data_status["bdd1_pressure"], self.kpa_data_status["bdd1_temp"],
                            self.kpa_data_status["kpa_volt"], self.kpa_data_status["bdd1_curr"]]
        self.bdd2_status = [self.kpa_data_status["bdd2_pressure"], self.kpa_data_status["bdd2_temp"],
                            self.kpa_data_status["kpa_volt"], self.kpa_data_status["bdd2_curr"]]
        pass



def process_row_data(row_pr):
    # reestr
    curr_a = [+5.338E-7, +5.345E-8, +5.344E-9, +5.339E-10]
    curr_b = [-9.369E-6, -9.301E-7, -7.367 - 8, +1.571E-8]

    # версия по кал. кривой ПММ
    # #cal_pressure = [1.00E-3, 4.00E-4, 2.00E-4, 4.00E-5, 1.00E-5, 4.00E-7, 5.30E-8, 2.00E-8, 8.00E-9]
    # 2.5kV
    cal_pressure_0 = [1.00E-3, 2.43E-4, 2.11E-4, 1.01E-4, 8.25E-5, 6.26E-5, 3.69E-5, 2.50E-5, 1.27E-6, 8.72E-6,
                      7.02E-6, 5.74E-6, 4.21E-6, 3.51E-6, 3.24E-6, 1.00E-9]
    cal_current_0 = [1.00E-3, 3.18E-4, 2.65E-4, 1.13E-4, 1.02E-4, 8.06E-5, 4.56E-5, 2.70E-5, 1.62E-5, 1.47E-5,
                     1.12E-5, 9.62E-6, 7.04E-6, 6.12E-6, 5.64E-6, 1.00E-9]
    # 1.5kV
    cal_pressure_1 = [1.00E-2, 1.01E-3, 9.25E-4, 8.10E-4, 7.13E-4, 6.19E-4, 5.05E-4, 4.01E-4, 3.10E-4, 2.00E-4,
                      1.04E-4, 9.14E-5, 8.32E-5, 7.67E-5, 6.18E-5, 5.13E-5, 4.06E-5, 3.01E-5, 2.01E-5, 1.06E-5,
                      9.53E-6, 8.86E-6, 8.03E-6, 7.06E-6, 6.15E-6, 5.25E-6, 4.14E-6, 1.00E-9]
    cal_current_1 = [1.00E-3, 3.22E-4, 2.90E-4, 2.56E-4, 2.11E-4, 1.80E-4, 1.30E-4, 9.77E-5, 7.07E-5, 3.55E-5,
                     1.20E-5, 1.02E-5, 9.57E-6, 8.18E-6, 6.46E-6, 4.95E-6, 4.85E-6, 3.64E-6, 2.50E-6, 1.74E-6,
                     1.64E-6, 1.59E-6, 1.54E-6, 1.45E-6, 1.39E-6, 1.28E-6, 1.14E-6, 1.00E-9]
    pressure_tmp = 1E-8
    if row_pr != b"\x00\x00" or row_pr != b"\xFF\xFF" or row_pr != b"\xFE\xFE":
        if (row_pr[0] >> 7) != 0:
            if (row_pr[
                    0] & 0x0F) > 7:  # крайне топорный способ сделать знаковое число, желатеьлно найти способ получше
                uP_pow = (row_pr[0] & 0x0F) - 16
            else:
                uP_pow = row_pr[0] & 0x0F
            pressure_tmp = (row_pr[1]) * (10 ** uP_pow)
        else:
            KU = 10 ** ((row_pr[0] & 0x30) >> 4)
            adc_data = ((row_pr[0] & 0x07) << 8) + row_pr[1]
            hv_mean = (row_pr[0] & 0x08) >> 3
            if KU == 1:
                curr_IMS = curr_a[0] * adc_data + curr_a[0]
            elif KU == 10:
                curr_IMS = curr_a[1] * adc_data + curr_a[1]
            elif KU == 100:
                curr_IMS = curr_a[2] * adc_data + curr_a[2]
            elif KU == 1000:
                curr_IMS = curr_a[3] * adc_data + curr_a[3]
            else:
                pass
            if hv_mean == 0:  # 2.5kV
                for i in range(len(cal_pressure_0) - 2):
                    if cal_current_0[i] >= curr_IMS > cal_current_0[i + 1]:
                        pressure_tmp = cal_pressure_0[i + 1] + \
                                       (curr_IMS - cal_current_0[i + 1]) * (
                                       (cal_current_0[i] - cal_current_0[i + 1]) / (
                                       cal_current_0[i] - cal_current_0[i + 1]))
                    else:
                        pass
            else:  # 1.5kV
                for i in range(len(cal_pressure_1) - 2):
                    if cal_current_1[i] >= curr_IMS > cal_current_1[i + 1]:
                        pressure_tmp = cal_pressure_1[i + 1] + \
                                       (curr_IMS - cal_current_1[i + 1]) * (
                                       (cal_current_1[i] - cal_current_1[i + 1]) / (
                                        cal_current_1[i] - cal_current_1[i + 1]))
                    else:
                        pass
    else:
        pressure_tmp = 1E-8
    return pressure_tmp


def stm_list_form(adc1, adc2):
    bdd1_list = [adc2[12], adc2[13], adc2[28], adc2[29], adc2[30], adc2[31], adc2[0], adc2[1], adc2[2], adc2[3]]
    bdd2_list = [adc2[14], adc2[15], adc2[4], adc2[5], adc2[6], adc2[7], adc2[8], adc2[9], adc2[10], adc2[11]]
    be_list = [adc1[20], adc1[21], adc1[22], adc1[23], adc1[24], adc1[25], adc1[26], adc1[27], adc1[28], adc1[29],
               adc1[30], adc1[31], adc1[0], adc1[1], adc1[2], adc1[3], adc1[4], adc1[5], adc1[6], adc1[7],
               adc1[8], adc1[9], adc1[10], adc1[11], adc2[20], adc2[21], adc2[22], adc2[23], adc2[24], adc2[25],
               adc2[26], adc2[27], adc2[16], adc2[17], adc2[18], adc2[19], adc1[18], adc1[19]]
    return be_list, bdd1_list, bdd2_list
