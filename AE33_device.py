import sys
import socket
import time
import datetime
from datetime import datetime
import matplotlib.pyplot as plt
import pandas as pd
import os


class AE33_device:
    def __init__(self):
        self.MINID = 0
        self.MAXID = 0

        ## for data files
        self.yy = '0'        ##  year for filename of raw file
        self.mm = '0'        ## month for filename of raw file
        self.yy_D = '0'      ##  year for filename of D-file
        self.mm_D = '0'      ## month for filename of D-file 
        self.pathfile = ''   ## work directory name
        self.xlsfilename = ''      ## exl file name
        self.file_raw = None       ## file for raw data
        self.file_format_D = None  ## file for raw data
        self.file_header = ''

        self.run_mode = 0

        self.buff = ''
        self.info = ''
        self.IPname = '192.168.1.62'
        self.IsConnected = 1
        self.Port = 8002  ## port number
        self.sock = None  ## socket
        #sock = socket.socket()
        self.fill_header()


    def fill_header(self):
        self.file_header = "AETHALOMETER\nSerial number = AE33-S08-01006\nApplication version = 1.6.7.0\nNumber of channels = 7\n\nDate(yyyy/MM/dd); Time(hh:mm:ss); Timebase; RefCh1; Sen1Ch1; Sen2Ch1; RefCh2; Sen1Ch2; Sen2Ch2; RefCh3; Sen1Ch3; Sen2Ch3; RefCh4; Sen1Ch4; Sen2Ch4; RefCh5; Sen1Ch5; Sen2Ch5; RefCh6; Sen1Ch6; Sen2Ch6; RefCh7; Sen1Ch7; Sen2Ch7; Flow1; Flow2; FlowC; Pressure(Pa); Temperature(°C); BB(%); ContTemp; SupplyTemp; Status; ContStatus; DetectStatus; LedStatus; ValveStatus; LedTemp; BC11; BC12; BC1; BC21; BC22; BC2; BC31; BC32; BC3; BC41; BC42; BC4; BC51; BC52; BC5; BC61; BC62; BC6; BC71; BC72; BC7; K1; K2; K3; K4; K5; K6; K7; TapeAdvCount;\n\n\n"


    def read_path_file(self):
        # check file
        #print("read file")
        try:
            f = open("PATHFILES.CNF")
        except:
            print("Error!! No file PATHFILES.CNF\n\n")
            return -1
        
        params = [x.replace('\n','') for x in f.readlines() if x[0] != '#']
        f.close()
        #print(params)
        
        for param in params:
            if "RUN" in param:
                self.run_mode = int(param.split('=')[1])
            elif "IP" in param:
                self.IPname = param.split('=')[1].split()[0]
                self.Port   = int(param.split('=')[1].split()[1])
            elif "MINID" in param:
                self.MINID = int(param.split('=')[1])
                self.MAXID = self.MINID
            else:
                self.pathfile = param
                os.system("mkdir " + param)
                path = self.pathfile + '\\raw\\'
                os.system("mkdir " + path)
                path = self.pathfile + '\ddat\\'
                os.system("mkdir " + path)
                path = self.pathfile + '\wdat\\'
                os.system("mkdir " + path)
                path = self.pathfile + '\\table\\'
                os.system("mkdir " + path)
    # \todo ПОПРАВИТЬ в конфигурацилонном файле СЛЕШИ В ИМЕНИ ДИРЕКТОРИИ  !!!   для ВИНДА


    def write_path_file(self):
        f = open("PATHFILES.CNF.bak", 'w')
        f.write("#\n")
        f.write("# Programm mode:\n")
        f.write("#   1 - for MAIN-menu,  0 - Auto RUN\n")
        f.write("#\n")
        f.write("RUN=" + str(self.run_mode) + "\n")
        f.write("#\n")
        f.write("# Directory for DATA:\n")
        f.write("#\n")
        f.write(self.pathfile + '\n')
        f.write("#\n")
        f.write("# AE33:   IP address and Port:\n")
        f.write("#\n")
        f.write("IP=" + self.IPname + '  ' + str(self.Port) +"\n")
        f.write("#\n")
        f.write("# AE33:  Last Records:\n")
        f.write("#\n")
        f.write("MINID=" + str(self.MAXID) + "\n")
        f.write("#\n")
        f.close()


    def print_params(self):
        print("RUN = ", self.run_mode)
        print("IP = ", self.IPname)
        print("Port = ", self.Port)
        print("pathfile = ", self.pathfile)
        print("MINID = ", self.MINID)


    def connect(self):
        #if self.active == -1:
        #    return -1
        #socket.socket(family='AF_INET', type='SOCK_STREAM', proto=0, fileno=None)
        #self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM | socket.SOCK_NONBLOCK)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #self.sock = socket.socket()
        #sock = socket.socket()
        self.sock.connect((self.IPname, self.Port))
        #sock.connect(('localhost', 3000)) 
        ## \todo проверить, что связь установлена


    def unconnect(self):
        ##  socket.shutdown(self.sock, SHUT_RD|SHUT_WR)
        self.sock.close()


    def request(self, command, start, stop):
        if command == 'FETCH DATA':
            command += ' ' + str(start) + ' ' + str(stop)
        command += '\r\n'
        print(command)

        ## --- send command ---
        time.sleep(1)
        ##self.sock.send(bytes(command))
        bytes = self.sock.send(command.encode())
        print(bytes)
        ## \todo проверить, что все отправилось
        if bytes != len(command):
            print("request: Error in sending data!! ") 
        print('sent ', bytes, ' to socket')

        if "CLOSE" in command:
            return 1

        ## --- read data ---
        time.sleep(1)
        attempts = 0
        buf = self.sock.recv(2000000)
        print('qq,  buf(bytes)=',len(buf))
        #print(buf)

        buff2 = buf.decode("UTF-8")
        buff2 = buff2.split("\r\nAE33>")
        #print('qq,  buff2=',len(buff2),buff2)

        #self.buff = buf.decode("UTF-8")
        if "HELLO" in command:
            self.buff = buff2[1]
        else:
            self.buff = buff2[0]

        #print('qq,  self.buff=',len(self.buff))
        #print(self.buff)
        #self.buff = self.buff.split("AE33>")
        #print(self.buff)

        while(len(buf) == 0 and attempts < 10):
            print('not data,  buf=',len(buf))
            time.sleep(1)
            buf = self.sock.recv(2000000)
            print('qq,  buf(bytes)=',len(buf))
            #print(buf)
            buff2 = buf.decode("UTF-8")
            buff2 = buff2.split("\r\nAE33>")
            #self.buff = buf.decode("UTF-8")
            if "HELLO" in command:
                self.buff = buff2[1]
            else:
                self.buff = buff2[0]
            #self.buff = self.buff.split("AE33>")
            #print(self.buff)
            attempts += 1
        if attempts >= 10:
            print("request: Error in receive")
            self.sock.unconnect()
            return 2
        
        if "MAXID" in command:
            #self.buff = self.buff.split("AE33>")
            #print(self.buff)
            self.MAXID = int(self.buff)
            print(self.MAXID)
        if "MINID" in command:
            #self.buff = self.buff.split("AE33>")
            #print(self.buff)
            self.MINID = int(self.buff)
            print(self.MINID)
        if '?' in command:
            self.info = self.buff
        if "FETCH" in command:
            self.parse_raw_data()
        if "AE33" in command:
            if "AE33:D":
                self.parse_format_D_data()            
        return 0


    def parse_raw_data(self):
        if len(self.buff) < 10:
            return
        #self.buff = self.buff.split("AE33>")
        print(self.buff)
        for line in self.buff:
            if len(line) < 50:
                continue
            print(line)
            mm, dd, yy = line.split("|")[2][:10].split('/')
            if mm != self.mm or yy != self.yy:
                filename = '_'.join((yy, mm)) + '_AE33-S08-01006.raw'
                filename = self.pathfile +'\\raw\\' + filename
                print(filename)
                if self.file_raw:
                    self.file_raw.close()
                self.file_raw = open(filename, "a")
            self.file_raw.write(line)
            self.file_raw.write('\n')
            
        self.file_raw.flush()
        self.mm = mm
        self.yy = yy


    def parse_format_D_data(self):
        ## main
        if len(self.buff) < 10:
            return
        #self.buff = self.buff.split("AE33>")
        if 'ix' in os.name:
            self.buff = self.buff.split("\n")  ## for Linux
        else:
            self.buff = self.buff.split("\r\n") ## for Windows

        lastmm, lastyy = '0', '0'
        filename = ''
        lastline = ''
        need_check = True
        dateformat = "%Y/%m/%d %H:%M:%S"
        #print('lines:')
        #print(self.buff)

        ## for excel data
        header = self.file_header[self.file_header.find("Date"):].split("; ")
        columns = ['Date(yyyy/MM/dd)', 'Time(hh:mm:ss)', 'BC1', 'BC2', 'BC3', 'BC4', 'BC5', 'BC6', 'BC7', 'BB(%)']
        colnums = [header.index(x) for x in columns]      
        rows_list = []
        
        for line in self.buff[::-1]:
            #print('line:   ',line)
            yy, mm, _ = line.split()[0].split('/')
            #print(yy, mm)

            # for first line or new file
            if mm != lastmm or yy != lastyy:
                ##### ddat file 
                filename = '_'.join((yy, mm)) + '_AE33-S08-01006.ddat'
                filename = self.pathfile +'\ddat\\' + filename
                print(filename,mm,yy,lastmm,lastyy)
                try:
                    ## ddat file exists
                    f = open(filename, 'r')
                    lastline = f.readlines()[-1].split()
                    #print(lastline)
                    f.close()
                    print('3')
                    lasttime = lastline[0] + ' ' + lastline[1]
                    print('1  ',lasttime)
                    lasttime = datetime.strptime(lasttime, dateformat)
                    print('4',lastmm,lastyy,mm,yy)
                    need_check = True
                except:
                    ## no file
                    print('NOT FILE', filename)
                    f = open(filename, 'a')        
                    f.write(self.file_header)
                    f.close()
                    lastline = []
                    need_check = False 
                lastmm = mm
                lastyy = yy
              
            ## add line data to dataframe 
            line_to_dataframe = [line.split()[i] for i in colnums]
            #print("line_to_dataframe:>",line_to_dataframe)
            line_to_dataframe = line_to_dataframe[:2]\
                                + [int(x) for x in line_to_dataframe[2:-1]]\
                                + [float(line_to_dataframe[-1])]
            rows_list.append(line_to_dataframe)
            #print(rows_list)
               

            ## check line to be added to datafile
            if need_check: # and len(lastline):
                #print(line)
                nowtime  = line.split()[0] + ' ' + line.split()[1]
                #print(nowtime)
                nowtime  = datetime.strptime(nowtime,  dateformat)
                print(nowtime - lasttime)
                ## if line was printed earlier
                if nowtime <= lasttime:
                    continue

            need_check = False

            ## write to file
            f = open(filename, 'a')
            f.write(line+'\n')
            f.close()
            

        ## ##### write dataframe to excel file
        ## make dataFrame from list
        excel_columns = ['Date', 'Time (Moscow)', 'BC1', 'BC2', 'BC3', 'BC4', 'BC5', 'BC6',
            'BC7', 'BB(%)', 'BCbb', 'BCff', 'Date.1', 'Time (Moscow).1']
        dataframe_from_buffer = pd.DataFrame(rows_list, columns=excel_columns[:-4])
        ## add columns
        dataframe_from_buffer['BCbb'] = dataframe_from_buffer['BB(%)'].astype(float) * dataframe_from_buffer['BC5'].astype(float) / 100
        dataframe_from_buffer['BCff'] = (100 - dataframe_from_buffer['BB(%)'].astype(float)) / 100 *  dataframe_from_buffer['BC5'].astype(float)
        dataframe_from_buffer['Date.1'] = dataframe_from_buffer['Date']
        dataframe_from_buffer['Time (Moscow).1'] = dataframe_from_buffer['Time (Moscow)']
        print(dataframe_from_buffer.head())

        ##### excel file #####                
        xlsfilename = yy + '_AE33-S08-01006.xlsx'
        xlsfilename = self.pathfile + 'table/' + xlsfilename
        self.xlsfilename = xlsfilename
        ## read or cleate datafame
        xlsdata = self.read_dataframe_from_excel_file(xlsfilename)
        print(xlsdata.head())
        if xlsdata.shape[0]:
            dropset = ['Date', 'Time (Moscow)']
            xlsdata = xlsdata.append(dataframe_from_buffer, ignore_index=True).drop_duplicates(subset=dropset, keep='last')
            #print("Append:", xlsdata)
            xlsdata.set_index('Date').to_excel(xlsfilename, engine='openpyxl')
        else:
            print("New data:")
            dataframe_from_buffer.set_index('Date').to_excel(xlsfilename, engine='openpyxl')
            #dataframe_from_buffer.to_excel(xlsfilename, engine='openpyxl')


    def read_dataframe_from_excel_file(self, xlsfilename):
        columns = ['Date', 'Time (Moscow)', 'BC1', 'BC2', 'BC3', 'BC4', 'BC5', 'BC6',
            'BC7', 'BB(%)', 'BCbb', 'BCff', 'Date.1', 'Time (Moscow).1']
        try:
            ## read excel file to dataframe
            ## need to make "pip install openpyxl==3.0.9" if there are problems with excel file reading
            datum = pd.read_excel(xlsfilename)
            print(xlsfilename, "read")
        except:
            # create excel 
            datum = pd.DataFrame(columns=columns)
            print("No file", xlsfilename)
            
        return datum


    def plot_from_excel_file(self, xlsfilename):
        try:
            ## read excel file to dataframe
            ## need to make "pip install openpyxl==3.0.9" if there are problems with excel file reading
            datum = pd.read_excel(xlsfilename)
        except:
            print("Error! No excel data file:", xlsfilename)
            return

        fig = plt.figure(figsize=(14, 5))
        plt.plot(datum["BCff"][-2880:], 'k', label='BCff')
        plt.plot(datum["BCbb"][-2880:], 'orange', label='BCbb')
        plt.legend()
        plt.grid()
        plt.savefig('Moscow_bb.png', bbox_inches='tight')
