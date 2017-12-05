import serial
import serial.tools.list_ports
import threading
import kpa_bdk2_parcer
import time


class MySerial(serial.Serial):
    def __init__(self, cnf={}, **kw):
        serial.Serial.__init__(self)
        self.serial_numbers = []  # это лист возможных серийников!!! (не строка)
        self.baudrate = 115200
        self.timeout = 0.1
        self.port = "COM0"
        self.row_data = b""
        for key in sorted(kw):
            if key == "serial_numbers":
                self.serial_numbers = kw.pop(key)
            elif key == "baudrate":
                self.baudrate = kw.pop(key)
            elif key == "timeout":
                self.baudrate = kw.pop(key)
            elif key == "port":
                self.baudrate = kw.pop(key)
            else:
                pass
        # данные для запоминания
        self.gpio = 0x00
        self.reading_thread = None
        self.kpa_data = kpa_bdk2_parcer.data()
        self._close_event = threading.Event()
        self.reading_thread = threading.Thread(target=self.reading_thread_function, args=())
        self.reading_thread.start()
        self.command_error = {"B0": 0, "B1": 0,  "B2": 0, "B3": 0, "B4": 0, "B5": 0, "C5": 0, "B6": 0, "B7": 0, "B8": 0}

    def open_id(self):  # функция для установки связи с КПА
        com_list = serial.tools.list_ports.comports()
        for com in com_list:
            for serial_number in self.serial_numbers:
                print(com.serial_number, serial_number)
                if com.serial_number.find(serial_number) >= 0:
                    #print(com.device)
                    self.port = com.device
                    self.open()
                    if com.serial_number == 'A90111MXA':
                        self.kpa_data.kpa_be_a = 2.3278
                        self.kpa_data.kpa_be_b = -12.128
                        self.kpa_data.kpa_bdd2_a = 2.4936
                        self.kpa_data.kpa_bdd1_a = 2.371
                        self.kpa_data.kpa_bdd2_b = -25.61
                        self.kpa_data.kpa_bdd1_b = -32.128
                    elif com.serial_number=='A90111MYA':
                        self.kpa_data.kpa_be_a = 2.5061
                        self.kpa_data.kpa_be_b = -56.758
                        self.kpa_data.kpa_bdd2_a = 2.4764
                        self.kpa_data.kpa_bdd1_a = 2.3292
                        self.kpa_data.kpa_bdd2_b = 3.9195
                        self.kpa_data.kpa_bdd1_b = -1.4497

                    return True
        return False
        pass

    def serial_close(self):
        self._close_event.set()
        self.reading_thread.join()
        self.close()

    def kpa_request(self, req_type="time_reset", fr_addr="00 00", stm="00 00", bdd_id="0x02", gpio="0x00", pulse_time=150):
        # bdd
        if req_type == "bdd_pressure":
            data_to_bdd = "E0 B7 00 00 08 " + bdd_id[2:5] + " 0A 00 03 01 00 00 00 0E"
        elif req_type == "bdd_temp":
            data_to_bdd = "E0 B7 00 00 08 " + bdd_id[2:5] + " 0A 00 03 02 00 00 00 0E"
        elif req_type == "bdd_frame":
            data_to_bdd = "E0 B7 00 00 08 " + bdd_id[2:5] + " 0A 00 03 04 00 00 00 0E"
        elif req_type == "bdd_read_pointer":
            data_to_bdd = "E0 B7 00 00 08 " + bdd_id[2:5] + " 0A 00 06 01 02 " + fr_addr + " 00 00 0E"
        elif req_type == "bdd_set_stm":
            data_to_bdd = "E0 B7 00 00 08 " + bdd_id[2:5] + " 0A 00 06 02 02 " + stm + " 00 00 0E"
        # be
        elif req_type == "be_change_mko_address":
            data_to_bdd = "E0 B7 00 00 04 " + "01 EA AE 05" + " 0E"
        # kpa
        elif req_type == "kpa_27V_on":
            self.gpio |= 0x01
            data_to_bdd = "E0 B1 00 00 " + "{:02X}".format(self.gpio) + " 0E"
        elif req_type == "kpa_27V_off":
            self.gpio &= ~0x01
            data_to_bdd = "E0 B1 00 00 " + "{:02X}".format(self.gpio) + " 0E"
        elif req_type == "kpa_+30V_on":
            self.gpio |= 0x02
            data_to_bdd = "E0 B1 00 00 " + "{:02X}".format(self.gpio) + " 0E"
        elif req_type == "kpa_+30V_off":
            self.gpio &= ~0x02
            data_to_bdd = "E0 B1 00 00 " + "{:02X}".format(self.gpio) + " 0E"
        elif req_type == "kpa_-30V_on":
            self.gpio |= 0x04
            data_to_bdd = "E0 B1 00 00 " + "{:02X}".format(self.gpio) + " 0E"
        elif req_type == "kpa_-30V_off":
            self.gpio &= ~0x04
            data_to_bdd = "E0 B1 00 00 " + "{:02X}".format(self.gpio) + " 0E"
        elif req_type == "kpa_bdd_mku_on":
            data_to_bdd = "E0 B3 00 00 40 0E"
        elif req_type == "kpa_bdd_mku_off":
            data_to_bdd = "E0 B3 00 00 80 0E"
        elif req_type == "kpa_bdd_tku_on":
            data_to_bdd = "E0 B3 00 01 00 0E"
        elif req_type == "kpa_bdd_tku_off":
            data_to_bdd = "E0 B3 00 02 00 0E"
        elif req_type == "kpa_be_ku_on_1":
            data_to_bdd = "E0 B3 00 00 08 0E"
        elif req_type == "kpa_be_ku_on_2":
            data_to_bdd = "E0 B3 00 00 10 0E"
        elif req_type == "kpa_be_ku_off":
            data_to_bdd = "E0 B3 00 00 20 0E"
        elif req_type == "kpa_ku_pulse_time":
            data_to_bdd = "E0 B4 00 " + "{:02X} {:02X}".format(pulse_time // 256, pulse_time % 256) + " 0E"
        elif req_type == "kpa_gpio":
            data_to_bdd = "E0 B1 00 00 " + gpio[2:5] + " 0E"
        elif req_type == "kpa_adc_1_2":
            data_to_bdd = "E0 B5 00 02 00 0E"
        elif req_type == "kpa_adc_3_4":
            data_to_bdd = "E0 C5 00 02 00 0E"
        #
        else:
            data_to_bdd = "E0 B7 00 00 08 " + bdd_id[2:5] + " 0A 00 03 01 00 00 00 0E"
            pass
        com_var = str_to_list(data_to_bdd)
        print("{:02X}".format(self.gpio))
        if self.is_open is True:
            self.write(com_var)
            self.command_error[data_to_bdd[3:5]] += 1
            #print("{:.3f} write: 0x {}".format(time.clock(), data_to_bdd))
            return data_to_bdd
        else:
            #raise SystemError("COM-port error")
            pass

    def reading_thread_function(self):
        buf = bytearray(b"")
        work_data = b""
        status = ""
        while True:
            time.sleep(0.01)
            if self.is_open is True:
                try:
                    read_data = self.read(128)
                    self.read_data=read_data
                except (TypeError, serial.serialutil.SerialException, AttributeError):
                    read_data = b""
                if read_data:
                    read_data = buf + bytes(read_data)  # прибавляем к новому куску старый кусок
                    #print(bytes_array_to_str(read_data))
                    buf = bytearray(b"")
                    while read_data:
                        #print(bytes_array_to_str(read_data))
                        if read_data[0] == 0xEE:
                            if len(read_data) >= 2:  # находим начало пакета
                                if read_data[1] in [0xB0, 0xB1, 0xB2, 0xB3, 0xB4, 0xB7]:
                                    if len(read_data) >= 6:
                                        if read_data[5] == 0x0E:
                                            work_data = read_data[0:6]
                                            read_data = read_data[6:len(read_data)]
                                elif read_data[1] in [0xB5, 0xC5]:
                                    if len(read_data) >= 71:
                                        if read_data[70] == 0x0E:
                                            work_data = read_data[0:71]
                                            read_data = read_data[71:len(read_data)]
                                elif read_data[1] == 0xB6:
                                    if len(read_data) >= 14:
                                        if read_data[13] == 0x0E:
                                            work_data = read_data[0:14]
                                            read_data = read_data[14:len(read_data)]
                                elif read_data[1] == 0xB8:
                                    if len(read_data) >= 5:
                                        data_len = read_data[4]
                                        if len(read_data) >= (5 + data_len + 1):
                                            if read_data[5 + data_len] == 0x0E:
                                                #print(bytes_array_to_str(read_data))
                                                work_data = read_data[0:5 + data_len + 1]
                                                read_data = read_data[(5 + data_len + 1):len(read_data)]
                                    pass
                                if work_data:
                                    status = self.kpa_data.parsing(work_data)
                                    self.command_error[bytes_array_to_str(work_data)[6:8]] -= 1
                                    # print("{:.3f} read {}: {}".format(time.clock(), status, bytes_array_to_str(work_data)))
                                    work_data = b""
                                    # print(self.command_error)
                                else:
                                    buf = read_data
                                    read_data = bytearray(b"")
                        else:
                            read_data.pop(0)
                        pass
            else:
                pass
            if self._close_event.is_set() is True:
                self._close_event.clear()
                return
        pass

    def form_bdd_data(self, bdd_id="0x02"):
        if bdd_id in "0x02":
            return ["{:.2E}".format(self.kpa_data.bdd1_pressure),
                    "{:.2f}".format(self.kpa_data.bdd1_temp),
                    "{:.2f}".format(self.kpa_data.kpa_volt),
                    "{:.2f}".format(self.kpa_data.bdd1_curr)]
        elif bdd_id in "0x03":
            return ["{:.2E}".format(self.kpa_data.bdd2_pressure),
                    "{:.2f}".format(self.kpa_data.bdd2_temp),
                    "{:.2f}".format(self.kpa_data.kpa_volt),
                    "{:.2f}".format(self.kpa_data.bdd2_curr)]



def str_to_list(send_str):  # функция, которая из последовательности шестнадцетиричных слов в строке без
    send_list = []  # идентификатора 0x делает лист шестнадцетиричных чисел
    send_str = send_str.split(' ')
    for i, ch in enumerate(send_str):
        send_str[i] = ch
        send_list.append(int(send_str[i], 16))
    return send_list


def bytes_array_to_str(bytes_array):
    bytes_string = "0x"
    for i, ch in enumerate(bytes_array):
        byte_str = (" %02X" % bytes_array[i])
        bytes_string += byte_str
    return bytes_string
