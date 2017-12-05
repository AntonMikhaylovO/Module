
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
        self.muart_data = []
        self.bdd1_pressure = 0
        self.bdd2_pressure = 0
        self.bdd1_temp = 0
        self.bdd2_temp = 0
        pass

    def parsing(self, row_data):
        self.row_data = row_data
        if len(self.row_data) < 6:
            return "Error"
        elif self.row_data[0] == 0xEE:
            if self.row_data[1] == 0xB0 and self.row_data[5] == 0x0E:  # команда для проверки работоспособности БДД
                return "Ack OK"
            elif self.row_data[1] == 0xB1 and self.row_data[5] == 0x0E:  # команда для установки статических портов [2,1,0]=[P_ON30N, P_ON30P, P_ON27]
                return "GPIO SET"
            elif self.row_data[1] == 0xB2 and self.row_data[5] == 0x0E:  # запрос сотстояни статических портов [2,1,0]=[P_ON30N, P_ON30P, P_ON27]
                self.gpio = self.row_data[3]
                return "GPIO GET"
            elif self.row_data[1] == 0xB3 and self.row_data[5] == 0x0E:  # импульс на портах : [9..3]=[BDD_TRK_OFF, BDD_TRK_ON, BDD_MRK_OFF, BDD_MRK_ON, BE_MRK_OFF, BE_MRK_ON2, BE_MRK_ON1]
                self.ku_pulse = int.from_bytes(self.row_data[3:5], byteorder="big", signed=False)
                return "KU START"
            elif self.row_data[1] == 0xB4 and self.row_data[5] == 0x0E:  # установка времени импульса КУ
                self.pulse_time = int.from_bytes(self.row_data[3:5], byteorder="big", signed=False)
                return "SET KU TIME"
            elif self.row_data[1] == 0xB5 and self.row_data[70] == 0x0E:  # получение всех данных с АЦП
                self.bdd1_curr = 1 * (int.from_bytes(self.row_data[29:31], byteorder='big') & 0x0FFF) + 0
                self.bdd2_curr = 1 * (int.from_bytes(self.row_data[31:33], byteorder='big') & 0x0FFF) + 0
                self.be_curr = 2.35 * (int.from_bytes(self.row_data[33:35], byteorder='big') & 0x0FFF) - 0
                self.kpa_volt = 0.01767 * (int.from_bytes(self.row_data[35:37], byteorder='big') & 0x0FFF) + 0.48
                self.adc_list_1 = [(int.from_bytes(self.row_data[5 + i * 2:7 + i * 2], byteorder='big') & 0x0FFF) for i
                                  in range(32)]
                return "ADC GET 1"
            elif self.row_data[1] == 0xC5 and self.row_data[70] == 0x0E:  # получение всех данных с АЦП
                self.adc_list_2 = [(int.from_bytes(self.row_data[5 + i * 2:7 + i * 2], byteorder='big') & 0x0FFF) for i
                                  in range(32)]
                return "ADC GET 2"
            elif self.row_data[1] == 0xB6 and self.row_data[13] == 0x0E:  # получение данных с АЦП - напряжение и мощность
                for var in self.row_data[31:35]:
                    var &= 0x0F
                self.bdd1_curr = 1 * int.from_bytes(self.row_data[31:33], byteorder='big') + 0
                self.bdd2_curr = 1 * int.from_bytes(self.row_data[31:33], byteorder='big') + 0
                self.be_curr = 0.45 * int.from_bytes(self.row_data[31:33], byteorder='big') + 32.4
                self.kpa_volt = 0.01767 * int.from_bytes(self.row_data[35:37], byteorder='big') + 0.48
                return "ADC_POWER GET"
            elif self.row_data[1] == 0xB7 and self.row_data[5] == 0x0E:  # отправка данных в UMART
                return "SEND UMART"
            elif self.row_data[1] == 0xB8 and self.row_data[5 + self.row_data[4]] == 0x0E:  # прием данных из UMART
                try:
                    if (self.row_data[5 + self.row_data[4]] == 0x0E):
                        self.muart_data = self.row_data[5:(5 + self.row_data[4])]
                        if len(self.muart_data) > 5:
                                if self.muart_data[4] == 0x01:
                                    if self.muart_data[4] == 0x01:  # давление
                                        row_data = self.muart_data[6:8]
                                        if self.muart_data[1] == 0x02:
                                            self.bdd1_pressure = self._process_row_data(row_data)
                                        elif self.muart_data[1] == 0x03:
                                            self.bdd2_pressure = self._process_row_data(row_data)
                                elif self.muart_data[4] == 0x02:  # темепратура бдд Pt1000
                                    if self.muart_data[1] == 0x02:
                                            self.bdd1_temp = (int.from_bytes(self.muart_data[6:8], byteorder='big', signed=True)) / 256
                                    elif self.muart_data[1] == 0x03:
                                            self.bdd2_temp = (int.from_bytes(self.muart_data[6:8], byteorder='big', signed=True)) / 256
                        return "RECEIVE UMART"
                except IndexError:
                    self.muart_data = []
                    return "ANKNOWN COMMAND"
        else:
            return "ANKNOWN COMMAND"

    # reestr
    curr_a = [+5.338E-7, +5.345E-8, +5.344E-9, +5.339E-10]
    curr_b = [-9.369E-6, -9.301E-7, -7.367 - 8, +1.571E-8]

    # версия по кал. кривой ПММ #cal_pressure = [1.00E-3, 4.00E-4, 2.00E-4, 4.00E-5, 1.00E-5, 4.00E-7, 5.30E-8, 2.00E-8, 8.00E-9]
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

    def _process_row_data(self, row_pr):
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
                    curr_IMS = self.curr_a[0] * adc_data + self.curr_a[0]
                elif KU == 10:
                    curr_IMS = self.curr_a[1] * adc_data + self.curr_a[1]
                elif KU == 100:
                    curr_IMS = self.curr_a[2] * adc_data + self.curr_a[2]
                elif KU == 1000:
                    curr_IMS = self.curr_a[3] * adc_data + self.curr_a[3]
                else:
                    pass
                if hv_mean == 0:  # 2.5kV
                    for i in range(len(self.cal_pressure_0) - 2):
                        if self.cal_current_0[i] >= curr_IMS > self.cal_current_0[i + 1]:
                            pressure_tmp = self.cal_pressure_0[i + 1] + \
                                           (curr_IMS - self.cal_current_0[i + 1]) * (
                                           (self.cal_current_0[i] - self.cal_current_0[i + 1]) / (
                                           self.cal_current_0[i] - self.cal_current_0[i + 1]))
                        else:
                            pass
                else:  # 1.5kV
                    for i in range(len(self.cal_pressure_1) - 2):
                        if self.cal_current_1[i] >= curr_IMS > self.cal_current_1[i + 1]:
                            pressure_tmp = self.cal_pressure_1[i + 1] + \
                                           (curr_IMS - self.cal_current_1[i + 1]) * (
                                           (self.cal_current_1[i] - self.cal_current_1[i + 1]) / (
                                           self.cal_current_1[i] - self.cal_current_1[i + 1]))
                        else:
                            pass
        else:
            pressure_tmp = 1E-8
        return pressure_tmp


