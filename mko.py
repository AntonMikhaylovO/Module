from WDMTMKv2 import *
import time
import crc16
import struct
import os
import kpa_bdk2_parcer
#  класс работы с МКО #
mass=[]


class TA1:

    def init(self):
        global name
        self.TTml_obj = TTmkEventData()
        state = TmkOpen()  # функция подключает драйвер к вызвавшему функцию процессу
        tmkdone(ALL_TMKS)
        tmkconfig(0)
        bcreset()
        bcgetstate()
        bcdefbase(1)
        bcgetbase()
        bcdefbus(BUS_1)
        bcgetbus()
        tmkgethwver()
        t = time.strftime('%d_%m_%Y_%H_%M_%S')
        dir = os.getcwd()
        name=dir + '\\MKO_Log\\' + t + '.txt'
        mko_log = open(name, 'a')
        mko_log.write(t+' '+ str(state))
        mko_log.close()
       # print(state)
        return state
    read_status = 0x0000
    answer_word = 0x0000
    command_word = 0x0000

    def disconnect(self):
        close_status = TmkClose()
        return close_status

    def SendToRT(self, Data, adr, sub, leng):

          try:
            adres=int(adr)
            subadr = int(sub)
            Len = int(leng)
          except:
              adres=0
              subadr=0
              Len=0
          Read=[adres, subadr, Len]
          self.control_word = ((Read[0] & 0x1F) << 11) + (0x00 << 10) + ((Read[1] & 0x1F) << 5) + (Read[2]& 0x1F)
          print('control word', "0x{:04X}".format(self.control_word))
          bcputw(0, self.control_word)
        #  print(Data)
          for i in range(len(Data)):
            bcputw(i+1, Data[i])
          bcstart(1, DATA_BC_RT)
          self.state = bcgetansw(DATA_BC_RT)
          print('answer', "0x{:04X}".format(self.state))
          frame=[]
          for i in range(0,64):
              word = bcgetw(i)
              frame.append(word)
          Log(self.control_word, self.state>>16, adres, subadr, frame)
          if bin(self.state)[len(bin(self.state))-1::]=='1':
              return 1
          else:
              return 0
    def ReadFromRT(self, adr, sub):
        try:
           adres = int(adr)
           print(hex(adres))
           subadr = int(sub)
           print(hex(subadr))
        except:
            adres=19
            subadr=30
        Read = [adres, subadr]
        control_word = ((adres & 0x1F) << 11) + (0x01 << 10) + ((subadr & 0x1F) << 5) + (32 & 0x1F)
        bcputw(0, control_word)
        bcstart(1, DATA_RT_BC)
        self.command_word = bcgetw(0)
        print('command', hex(self.command_word))
        self.answer_word = bcgetw(DATA_RT_BC)
        print('answer', hex(self.answer_word))
        if bin(self.answer_word)[len(bin(self.answer_word))-1::]!=bin(1):
            frame = []
            for i in range(2, 2+32+1):
                word = bcgetw(i)
                frame.append(word)
            Log(self.command_word, self.answer_word, adres, subadr, frame)
            return frame
        else:
             return 0x1

    def ADII_sub(self,stop):
        if (stop==bin(1)):
            time.sleep(10)
        stop_flag=bin(1)
        while (stop_flag==bin(1)):
            frame = TA1.ReadFromRT(self, 19, 5)
            if frame[0]!=bin(1):
                stop_flag=0
            else:
                time.sleep(10)
        ppp=Data_struct.ADII_struct(self, frame)
        return ppp
    def all_sub(self,stop):
        if (stop==bin(1)):
            time.sleep(10)
        stop_flag=bin(1)
        while (stop_flag==bin(1)):
            frame = TA1.ReadFromRT(self, 19, 6)
            if frame[0]!=bin(1):
                stop_flag=0
            else:
                time.sleep(10)
        ppp=Data_struct.all_struct(self,frame)
        return ppp
    def RP_DEP_sub(self,stop):
        if (stop==bin(1)):
            time.sleep(10)
        stop_flag=bin(1)
        while (stop_flag==bin(1)):
            frame = TA1.ReadFromRT(self, 19, 7)
            if frame[0]!=bin(1):
                stop_flag=0
            else:
                time.sleep(10)
        ppp = Data_struct.mpp_struct(self, frame,4)
        return ppp
    def MPP1_sub(self,stop):
        if (stop==bin(1)):
            time.sleep(10)
        stop_flag=bin(1)
        while (stop_flag==bin(1)):
            frame = TA1.ReadFromRT(self, 19, 8)
            if frame[0]!=bin(1):
                stop_flag=0
            else:
                time.sleep(10)
        ppp = Data_struct.mpp_struct(self, frame,1)
        return ppp
    def MPP2_sub(self,stop):
        if (stop==bin(1)):
            time.sleep(10)
        stop_flag=bin(1)
        while (stop_flag==bin(1)):
            frame = TA1.ReadFromRT(self, 19, 9)
            if frame[0]!=bin(1):
                stop_flag=0
            else:
                time.sleep(10)
        ppp = Data_struct.mpp_struct(self, frame,2)
        return ppp
    def MPP3_sub(self,stop):
        if (stop==bin(1)):
            time.sleep(10)
        stop_flag=bin(1)
        while (stop_flag==bin(1)):
            frame = TA1.ReadFromRT(self, 19, 10)
            if frame[0]!=bin(1):
                stop_flag=0
            else:
                time.sleep(10)
        ppp = Data_struct.mpp_struct(self, frame,3)
        return ppp
    def Fast_DEP(self,stop):

        if (stop==bin(1)):
            time.sleep(10)
        stop_flag=bin(1)
        while (stop_flag==bin(1)):
            frame=TA1.ReadFromRT(self,19,11)
            if frame[0]!=bin(1):
                stop_flag=0
            else:
                time.sleep(10)
        ppp=Data_struct.Fast_DEP(self,frame)
        return ppp
    def BDK2(self,stop):
        if (stop==bin(1)):
            time.sleep(10)
        stop_flag=bin(1)
        while (stop_flag==bin(1)):
            frame = TA1.ReadFromRT(self, 19, 12)
            if frame[0]!=bin(1):
                stop_flag=0
            else:
                time.sleep(10)
        ppp=Data_struct.BDK2_struct(self, frame)
        return ppp
    def BDD1_sub(self,stop):
        if (stop==bin(1)):
            time.sleep(10)
        stop_flag=bin(1)
        while (stop_flag==bin(1)):
            frame = TA1.ReadFromRT(self, 19, 13)
            if frame[0]!=bin(1):
                stop_flag=0
            else:
                time.sleep(10)
        ppp=Data_struct.BDD_struct(self, frame)
        return ppp
    def BDD2_sub(self,stop):
        if (stop==bin(1)):
            time.sleep(10)
        stop_flag=bin(1)
        while (stop_flag==bin(1)):
            frame = TA1.ReadFromRT(self, 19, 14)
            if frame[0]!=bin(1):
                stop_flag=0
            else:
                time.sleep(10)
        ppp=Data_struct.BDD_struct(self, frame)
        return ppp
    def STM_control(self, check):
        Read = [19, 30, 32]
        TA1.SendToRT(self, [0x0002], 19, 30,1)
        TA1.SendToRT(self, [0x0000], 19,30,1)

    def Module_control(self, check):
        Read = [19, 30, 32]
        TA1.SendToRT(self, [0x0003],19,30,1)
        TA1.SendToRT(self, [0x0003],19,30,1)


class Data_struct():

    def parse(self, mass):
        self.Time =(mass[0]<<16)+mass[1]
        self.acp0=mass[7]
        self.acp2=mass[8]
        tmp=mass[9]>>8
        self.temp=tmp
        self.MKO_fail=mass[9]&0xff
        bits3=[str((mass[17]>>i)&0x1) for i in range(16)]
        self.RS_Stats3=format(mass[17]>>8, '#04x')
        self.RS_Stats2=format(mass[17]&0xff,'#04x')
        bits2=[str((mass[18]>>i)&0x1) for i in range(16)]
        self.RS_Stats1=format(mass[18]>>8, '#04x')
        self.Diff=mass[22]
        self.MKO_count=mass[9]&0xff
        self.MKO_on_count=mass[13]>>8
        self.MKO_work=mass[13]&0xff
        self.RS_fail=mass[15]&0xff
        self.RS_answ=mass[16]>>8
        bits1=[str((mass[16]>>i)&0x1) for i in range(16)]
        self.modstats=format(mass[16]>>8, '#04x')
        self.izmr=mass[22]
        self.mko_ans=mass[31]
        self.amper=Data_struct.amperage(self, mass[2:7], self.acp0, self.acp2)
        list=[self.Time, self.amper, self.temp, self.MKO_count, self.RS_Stats3, self.RS_Stats2, self.RS_Stats1,self.Diff,
              self.MKO_on_count,self.MKO_work, self.RS_fail, self.RS_answ, self.modstats, self.izmr, self.mko_ans, self.MKO_fail]
        return list

    def mpp_struct(self, mass, num):
        a1=0
        b1=0
        a2=0
        b2=0
        if num==1:
            a1=0.0107
            b1=-2.2674
            a2=0.000681
            b2=-1.386
        elif num==2 :
            a1=0.0107
            b1=-2.2533
            a2=0.0108
            b2=-2.1211
        elif num==3:
            a1=0.0365
            b1=-7.6027
            a2=0.0364
            b2=-7.687
        elif num==4:
            a1=0.0010383
            b1=-2.132
            a2=0.0010301
            b2=-2.111683
        self.time=(mass[2]<<16)+mass[3]
        self.num_chan=mass[5]&0xFF
        self.Reg_time=(mass[6]<<48)+(mass[7]<<32)+(mass[8]<<16)+mass[9]
        self.Width=((mass[10]<<16)+mass[11])/(10**7)
        self.ZeroCount=mass[12]
        self.Peak=0.01*mass[13]
        self.Power=(mass[14]<<16)+mass[15]
        if mass[16]!=0:
            self.Signal=(mass[16])*a1+b1
        else: self.Signal=0
        if mass[17]!=0:
            self.Mean=mass[17]*a1+b1
        else: self.Mean=0
        self.num_chan1=mass[18]&0xFF
        self.Reg_time1=(mass[19]<<48)+(mass[20]<<32)+(mass[21]<<16)+mass[22]
        self.Width1=((mass[23]<<16)+mass[24])/(10**7)
        self.ZeroCount1=mass[25]
        self.Peak1=0.01*mass[26]
        self.Power1=mass[27]<<16+mass[28]
        if mass[29]!=0:
            self.Signal1=mass[29]*a2+b2
        else: self.Signal1=0
        if mass[30]!=0:
            self.Mean1=mass[30]*a2+b2
        else: self.Mean1=0
        self.crc=mass[31]
        self.crc1=mass[:len(mass)-2]
        mas=[]
        for i in range(len(mass)-1):
            mas.append("0x{:04X}".format(mass[i]))
        print(mas)
        list=[self.time, self.Reg_time, self.num_chan, self.Width,self.ZeroCount, self.Peak, self.Power, self.Signal,self.Mean, self.num_chan1,
              self.Reg_time1, self.Width1, self.ZeroCount1, self.Peak1, self.Power1, self.Signal1, self.Mean1, self.crc,self.crc1]
        return list

    def dep_struct(self, mass):
        self.RunCount=mass[0]
        self.AcqCount=mass[1]
        self.CurrentMax=mass[4]
        self.CurrentMin=mass[5]
        self.CurrentPeriod=mass[6]
        return list

    def dep_formul(self,a, A=0.1, B=0):
            Scaler = a >> 15
            Mantissa = (a & 0x3FF)
            if (Mantissa & 0x200) == 0:
                Mantissa = - Mantissa
            else:
                Mantissa = (((~Mantissa) + 1) & 0x3FF)
            Degree = (a >> 10) & 0x1F
            #Sign = (a >> 9) & 1
            Field = (Mantissa * (2 **(23 - Degree)) * (10 ** (-Scaler)) / (2 ** 18)) * A + B
            return Field

    def parsFreq(self,delta):
            if delta > 127:
                delta -= 256
            freq = 5e6 / (33333 + (delta * (2 ** 7)))
            return freq

    def all_struct(self, mass):
        self.Time = (mass[2] << 16) + mass[3]
        self.field1DEP1=Data_struct.dep_formul(self,mass[5])
        self.freaq1DEP1=Data_struct.parsFreq(self,mass[6]>>8)
        self.field1DEP2=Data_struct.dep_formul(self,(((mass[6]&0xff)<<8)+(mass[7]>>8)))
        self.freaq1DEP2=Data_struct.parsFreq(self,mass[7]&0xff)
        self.field2DEP1=Data_struct.dep_formul(self,mass[8])
        self.freaq2DEP1=Data_struct.parsFreq(self,mass[9]>>8)
        self.field2DEP2=Data_struct.dep_formul(self,(((mass[9]&0xff)<<8)+(mass[10]>>8)))
        self.freaq2DEP2=Data_struct.parsFreq(self,mass[10]&0xff)
        self.field3DEP1=Data_struct.dep_formul(self,mass[11])
        self.freaq3DEP1=Data_struct.parsFreq(self,mass[12]>>8)
        self.field3DEP2=Data_struct.dep_formul(self,(((mass[12]&0xff)<<8)+(mass[13]>>8)))
        self.freaq3DEP2=Data_struct.parsFreq(self,mass[13]&0xff)
        if mass[14]!=0:
            self.fielDIR0=(5.283E-4*mass[14])-4.329
        else:
            self.fielDIR0=0
        if mass[15] != 0:
            self.tempDIR0=(4.818E-5*mass[15])-0.394
        else:
            self.tempDIR0=0
        if mass[16] != 0:
            self.fielDIR1=(5.283E-4*mass[16])-4.329
        else:
            self.fielDIR1=0
        if mass[17] != 0:
            self.tempDIR1=(4.818E-5*mass[17])-0.394
        else:
            self.tempDIR1=0
        if mass[18] != 0:
            self.fielDIR2=(5.345E-4*mass[18])-4.356
        else:
            self.fielDIR2=0
        if mass[19] != 0:
            self.tempDIR2=(4.867E-5*mass[19])-0.397
        else:
            self.tempDIR2=0
        if mass[20] != 0:
            self.fielDIR3=(5.104E-4*mass[20])-4.171
        else:
            self.fielDIR3=0
        if mass[21] != 0:
            self.tempDIR3=(4.704E-5*mass[21])-0.384
        else:
            self.tempDIR3=0
        if mass[22] != 0:
            self.fielDIR4=(5.401E-4*mass[22])-4.404
        else:
            self.fielDIR4=0
        if mass[23] != 0:
            self.tempDIR4=(4.927E-5*mass[23])-0.402
        else:
            self.tempDIR4=0
        self.BDD1_pressure=mass[24]
        self.hi=mass[24]>>8
        self.lo=mass[24]&0xff
        self.barray=[self.hi, self.lo]
        self.BDD1_pressure=kpa_bdk2_parcer.process_row_data(bytearray(self.barray))
        self.BDD1_temp=mass[25]>>8
        self.hi=mass[25]&0xff
        self.lo=mass[26]>>8
        self.barray=[self.hi, self.lo]
        self.BDD2_pressure=kpa_bdk2_parcer.process_row_data(bytearray(self.barray))
        self.BDD2_temp=mass[26]&0xff
        self.maxRP=(mass[26]<<16)+mass[27]
        self.crc=mass[31]
        self.crc1=mass[:len(mass)-2]
        list=[self.Time, self.field1DEP1, self.freaq1DEP1, self.field1DEP2, self.freaq1DEP2, self.field2DEP1, self.freaq2DEP1,
              self.field2DEP2, self.freaq2DEP2, self.field3DEP1, self.freaq3DEP1, self.field3DEP2, self.freaq3DEP2,
              self.fielDIR0, self.tempDIR0, self.fielDIR1, self.tempDIR1,self.fielDIR2,
              self.tempDIR2, self.fielDIR3, self.tempDIR3, self.fielDIR4, self.tempDIR4,
             self.BDD1_pressure,self.BDD1_temp, self.BDD2_pressure, self.BDD2_temp, self.crc,self.crc1]
        return list

    def Fast_DEP(self, mass):
        self.fieldDEP1=Data_struct.dep_formul(self,mass[5])
        self.freaqDEP1=Data_struct.parsFreq(self,mass[6]>>8)
        self.fieldDEP21=Data_struct.dep_formul(self,((mass[6]&0xff)<<8)+(mass[7]>>8))
        self.freaqDEP21=Data_struct.parsFreq(self,mass[7]&0xff)
        self.fieldDEP12=Data_struct.dep_formul(self,mass[8])
        self.freaqDEP12=Data_struct.parsFreq(self,mass[9]>>8)
        self.fieldDEP23=Data_struct.dep_formul(self,((mass[9]&0xff)<<8)+(mass[10]>>8))
        self.freaqDEP23=Data_struct.parsFreq(self,mass[10]&0xff)
        self.fieldDEP14=Data_struct.dep_formul(self,mass[11])
        self.freaqDEP14=Data_struct.parsFreq(self,mass[12]>>8)
        self.fieldDEP25=Data_struct.dep_formul(self,((mass[12]&0xff)<<8)+(mass[13]>>8))
        self.freaqDEP25=Data_struct.parsFreq(self,mass[13]&0xff)
        self.fieldDEP16=Data_struct.dep_formul(self,mass[14])
        self.freaqDEP16=Data_struct.parsFreq(self,mass[15]>>8)
        self.fieldDEP27=Data_struct.dep_formul(self,((mass[15]&0xff)<<8)+(mass[16]>>8))
        self.freaqDEP27=Data_struct.parsFreq(self,mass[16]&0xff)
        self.fieldDEP18=Data_struct.dep_formul(self,mass[17])
        self.freaqDEP18=Data_struct.parsFreq(self,mass[18]>>8)
        self.fieldDEP29=Data_struct.dep_formul(self,((mass[18]&0xff)<<8)+(mass[19]>>8))
        self.freaqDEP29=Data_struct.parsFreq(self,mass[19]&0xff)
        self.fieldDEP110=Data_struct.dep_formul(self,mass[20])
        self.freaqDEP110=Data_struct.parsFreq(self,mass[21]>>8)
        self.fieldDEP211=Data_struct.dep_formul(self,((mass[21]&0xff)<<8)+(mass[22]>>8))
        self.freaqDEP211=Data_struct.parsFreq(self,mass[22]&0xff)
        self.fieldDEP112=Data_struct.dep_formul(self,mass[23])
        self.freaqDEP112=Data_struct.parsFreq(self,mass[24]>>8)
        self.fieldDEP213=Data_struct.dep_formul(self,((mass[24]&0xff)<<8)+(mass[25]>>8))
        self.freaqDEP213=Data_struct.parsFreq(self,mass[25]&0xff)
        self.fieldDEP114=Data_struct.dep_formul(self,mass[26])
        self.freaqDEP114=Data_struct.parsFreq(self,mass[27]>>8)
        self.fieldDEP215=Data_struct.dep_formul(self,((mass[27]&0xff)<<8)+(mass[28]>>8))
        self.freaqDEP215=Data_struct.parsFreq(self,mass[28]&0xff)
        self.crc=mass[31]
        self.crc1=mass[:len(mass)-2]
        list=[self.fieldDEP1, self.freaqDEP1,self.fieldDEP21, self.freaqDEP21,self.fieldDEP12, self.freaqDEP12,self.fieldDEP23, self.freaqDEP23,
              self.fieldDEP14, self.freaqDEP14,self.fieldDEP25, self.freaqDEP25,self.fieldDEP16, self.freaqDEP16,self.fieldDEP27, self.freaqDEP27,
              self.fieldDEP18, self.freaqDEP18,self.fieldDEP29, self.freaqDEP29,self.fieldDEP110, self.freaqDEP110,self.fieldDEP211, self.freaqDEP211,
              self.fieldDEP112, self.freaqDEP112,self.fieldDEP213, self.freaqDEP213, self.fieldDEP114,self.freaqDEP114,self.fieldDEP215,self.freaqDEP215, self.crc, self.crc1]
        return list

    def BDD_struct(self,mass):
        bytes_string = "0x"
        for i in range(len(mass)):
            byte_str = (" %02X" % mass[i])
            bytes_string += byte_str
        #print(bytes_string)
        self.time=(mass[2]<<16)+mass[3]
        self.adr=mass[4]
        self.stats=hex(mass[5]>>8)
        self.frame_num1=(mass[5]&0xff)<<16+mass[6]
        self.temp=mass[7]>>8
        self.bar=mass[7]&0xff+mass[8]>>8
        self.hi=mass[7]&0xff
        self.lo=mass[8]>>8
        self.barray=[self.hi, self.lo]
        #print(self.barray)
        self.bar3=kpa_bdk2_parcer.process_row_data(bytearray(self.barray))
        self.crc=mass[31]
        self.crc1=mass[:len(mass)-2]
        list=[self.time, self.adr, self.stats, self.frame_num1, self.temp, self.bar3, self.crc,self.crc1]
        return list

    def ADII_struct(self, mass):
        self.fk=mass[4]>>8
        self.ps1=mass[4]&0xff+mass[5]
        self.ps2=mass[6]+mass[7]>>8
        self.ps3=mass[7]&0xff+mass[8]
        self.ps4=mass[9]+mass[10]>>8
        self.ps5=mass[10]&0xff+mass[11]
        self.ps6=mass[12]+mass[13]>>8
        self.ps7=mass[13]&0xff+mass[14]
        self.ps8=mass[15]+mass[16]>>8
        self.ps9=mass[16]&0xff+mass[17]
        self.ps10=mass[18]+mass[19]>>8
        self.ps11=mass[19]&0xff+mass[20]
        self.ps12=mass[21]+mass[22]>>8
        self.ps13=mass[22]&0xff+mass[23]
        self.ps14=mass[24]+mass[25]>>8
        self.ps15=mass[25]&0xff+mass[26]>>8
        self.ps16=mass[26]&0xff+mass[27]>>8
        self.ps17=mass[27]&0xff+mass[28]>>8
        self.ps18=mass[28]&0xff+mass[29]>>8
        self.ps19=mass[29]&0xff+mass[30]>>8
        self.crc=mass[31]
        self.crc1=mass[:len(mass)-2]
        list=[self.fk,self.ps1,self.ps2,self.ps3,self.ps4,self.ps5,self.ps6,self.ps7,self.ps8,self.ps9,self.ps10,self.ps11,self.ps12,
              self.ps13,self.ps14,self.ps15,self.ps16,self.ps17,self.ps18,self.ps19,self.crc, self.crc1]
        return list

    def BDK2_struct(self,mass):
        self.frame_name=mass[1]#format(mass[1], '#04x')
        self.Time =(mass[2]<<16)+mass[3]
        self.frame_number=mass[4]
        self.acp0=mass[10]
        self.acp2=mass[11]
        self.amper=Data_struct.amperage(self,mass[5:10], self.acp0, self.acp2)
        self.mko_fail_counter=mass[12]>>8
        self.MKO_fail=mass[12]&0xff
        self.writer=mass[13]
        self.reader=mass[14]
        self.turn_on_counter=mass[15]&0xff
        self.cm_number=mass[16]>>8
        self.time_dif=(mass[16]&0xff)+(mass[17]>>8)
        self.RS_fail=(mass[17]&0xff)
        self.RS_answ=mass[18]>>8
        self.module_stats=mass[18]&0xff
        bits3=[str((mass[17]>>i)&0x1) for i in range(16)]
        self.RS_Stats3=format(mass[19]>>8, '#04x')
        self.RS_Stats2=format(mass[19]&0xff,'#04x')
        bits2=[str((mass[18]>>i)&0x1) for i in range(16)]
        self.RS_Stats1=format(mass[20]>>8, '#04x')
        self.dep_turn=mass[20]&0xff
        self.turn_mpp6=mass[21]>>8
        self.turn_mpp5=mass[21]&0xff
        self.turn_mpp4=mass[22]>>8
        self.turn_mpp3=mass[22]&0xff
        self.turn_mpp2=mass[23]>>8
        self.turn_mpp1=mass[23]&0xff
        self.gate=mass[24]
        self.ust1=mass[25]
        self.ust2=mass[26]
        self.ust3=mass[27]
        self.ust4=mass[28]
        self.ust5=mass[29]
        self.ust6=mass[30]
        bits1=[str((mass[16]>>i)&0x1) for i in range(16)]
        self.crc = mass[31]
        self.crc1 = mass[:len(mass) - 2]
        mas = []
        for i in range(len(mass) - 1):
            mas.append("0x{:04X}".format(mass[i]))
        self.list=[self.frame_name,self.Time,self.frame_number, self.amper,self.acp0,self.acp2, self.mko_fail_counter, self.MKO_fail,
                   self.writer,self.reader,self.turn_on_counter,self.cm_number,self.time_dif, self.RS_fail, self.RS_answ,
                   self.module_stats,self.RS_Stats3, self.RS_Stats2, self.RS_Stats1,self.dep_turn,
        self.turn_mpp6,self.turn_mpp5,self.turn_mpp4,self.turn_mpp3,self.turn_mpp2,self.turn_mpp1,self.gate,self.ust1,self.ust2,
        self.ust3,self.ust4,self.ust5,self.ust6,self.crc,self.crc1]
        return self.list

    def amperage(self, data, acp, acp_b):
        a=[]
        for i in range (len(data)):
            try:
                if i==0 :
                    Ros = 1
                    Ri=5.1
                elif i==1:
                    Ros = 10
                    Ri=4.7
                elif i==2:
                    Ros = 10
                    Ri=4.7
                elif i==3:
                    Ri=4.7
                    Ros=10
                elif i==4:
                    Ri=4.7
                    Ros=10
                else:
                    Ri=4.7
                    Ros=10

                #b=((((data[i]-acp)/(acp_b-acp))*(2.5/Ri))/Ros)*1000
                b=((data[i]-acp)*(2.5/(acp_b-acp))*(1000/(Ri*Ros)))
                print(Ros)
                print(Ri)
                print(b)
            except ZeroDivisionError:
                b=0
            a.append(b)
        return a


class Log ():

    def __init__(self, answer, command, adres, subadr, frame):
        global name
        try:
            mko_log=open(name, 'a')
        except:
            pass
        t = time.strftime('%d_%m_%Y_%H_%M_%S')
        fr='0x'
        for i in range(len(frame)):
            fr+=' '+str("{:04X}".format(frame[i]))
        try:
            mko_log.write('\n Time: ' + time.strftime('%H_%M_%S') + ' Adr: ' + str("0x{:04X}".format(adres)) + ' Sub: ' + str("0x{:04X}".format(subadr)) + ' C.W.: ' +
                          str("0x{:04X}".format(answer)) + ' A.W: ' + str("0x{:04X}".format(command)) +
                          ' Data: ' + fr)
            mko_log.close()
        except:
            pass














