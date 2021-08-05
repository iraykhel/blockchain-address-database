import decimal
import time
from collections import defaultdict
import datetime
import pprint
import pickle

Q = [decimal.Decimal(10) ** 0, decimal.Decimal(10) ** -1, decimal.Decimal(10) ** -2, decimal.Decimal(10) ** -3,
     decimal.Decimal(10) ** -4, decimal.Decimal(10) ** -5, decimal.Decimal(10) ** -6, decimal.Decimal(10) ** -7,
     decimal.Decimal(10) ** -8,
     decimal.Decimal(10) ** -9, decimal.Decimal(10) ** -10, decimal.Decimal(10) ** -11, decimal.Decimal(10) ** -12]



def dec(num, places=None):
    if places is None:
        # print("dec",num)
        return decimal.Decimal(num)
    else:
        return decimal.Decimal(num).quantize(Q[places], rounding=decimal.ROUND_HALF_EVEN)


logger = None
class Logger:
    def __init__(self, write_frequency=1):
        self.files = defaultdict(dict)
        self.write_frequency = write_frequency


    def log(self,*args, **kwargs):
        t = time.time()
        if 'WRITE ALL' in args:
            for filename in self.files:
                self.buf_to_file(filename)
                # self.files[filename]['file_object'].close()
            # self.files = defaultdict(dict)
            return

        if 'buffer' in kwargs and kwargs['buffer'] != None:
            buffer = kwargs['buffer']
            strings = []
            if 'ignore_time' not in kwargs:
                tm = str(datetime.datetime.now())
                strings.append(tm)

            for s in args:
                if 'prettify' in kwargs:
                    s = pprint.pformat(s)
                strings.append(str(s))
            buffer.append(" ".join(strings))
        else:
            if 'file' in kwargs:
                filename = kwargs['file']
            else:
                filename = "log.txt"
            if filename not in self.files:
                # myfile = open('logs/' + filename, "a", encoding="utf-8")
                # self.files[filename]['file_object'] = myfile
                self.files[filename]['last_write'] = t
                self.files[filename]['buffer'] = []


            buffer = self.files[filename]['buffer']
            # myfile = self.files[filename]['file_object']
            if 'ignore_time' not in kwargs:
                tm = str(datetime.datetime.now())
                if 'print_only' not in kwargs:
                    buffer.append(tm + " ")
                    # myfile.write(tm + " ")
                if 'log_only' not in kwargs:
                    self.lprint(tm)

            for s in args:
                if 'prettify' in kwargs:
                    s = pprint.pformat(s)
                if 'print_only' not in kwargs:
                    # myfile.write(str(s) + " ")
                    buffer.append(str(s) + " ")
                if 'log_only' not in kwargs:
                    self.lprint(s)

            if 'print_only' not in kwargs:
                # myfile.write("\n")
                buffer.append("\n")
            if 'log_only' not in kwargs:
                self.lprint("", same_line=False)

            self.buf_to_file(filename)
            # if 'force_write' in kwargs:
            # # if 1:
            #     self.buf_to_file(filename)
            #
            # elif self.files[filename]['last_write'] + self.write_frequency < t:
            #     self.buf_to_file(filename)

            # myfile.close()

    def buf_to_file(self,filename):
        buffer = self.files[filename]['buffer']
        if len(buffer) > 0:
            myfile = open('logs/' + filename, "a", encoding="utf-8")
            myfile.write(''.join(buffer))
            myfile.close()
        self.files[filename]['buffer'] = []
        self.files[filename]['last_write'] = time.time()

    def lprint(self,p, same_line=True):
        try:
            if same_line:
                print(p, end=' ')
            else:
                print(p)
        except Exception:
            pass


def log(*args,**kwargs):
    global logger
    if logger is None:
        logger = Logger()

    logger.log(*args,**kwargs)
