import os
from PIL import Image
import subprocess
import urllib
import requests
import time
import lcddriver
import RPi.GPIO as GPIO
import time

# INITIAL VALUES
http_url = 'http://192.168.0.108:8000/'
secret_code = '1515'
ms_office = ['docx', 'doc', 'xls', 'xlsx', 'ppt',
             'odt', 'ods']
pngs = ['png']


lcd = lcddriver.lcd()
lcd.lcd_clear()
lcd.lcd_display_string('   Loading...', 1)
lcd.lcd_display_string('   Please Wait  ', 2)
time.sleep(3)
lcd.lcd_clear()
subprocess.call('lpoptions -d l130', shell=True)


# function png to jpg
def png_to_jpg(file_name):
    jpg_file = file_name[:file_name.find('.')] + '.jpg'
    png_file = Image.open(file_name)
    bground = Image.new('RGB', png_file.size, (255, 255, 255))
    bground.paste(png_file, (0, 0), png_file)
    bground.save(jpg_file, quality=95)
    return jpg_file


# function ms office files to pdf
def ms_to_pdf(file_name):
    command1 = 'doc2pdf ' + file_name
    subprocess.call(command1, shell=True)
    pdf_file = file_name[:file_name.find('.')] + '.pdf'
    return pdf_file


# function to give print command
def take_print(file_name, color_mode):
    try:
        file_type = file_name[file_name.find('.') + 1:]
        if file_type in pngs:
            file_to_print = png_to_jpg(file_name)
        elif file_type in ms_office:
            file_to_print = ms_to_pdf(file_name)
        else:
            file_to_print = file_name
        color_model = ' -o ColorModel=RGB ' if color_mode == 'color' else ''
        print_command = 'lp {color_model} {file_to_print} '.format(
                                                        file_to_print=file_to_print,
                                                        color_model=color_model)
        subprocess.call(print_command, shell=True)
        lcd.lcd_clear()
        lcd.lcd_display_string('   Please ', 1)
        lcd.lcd_display_string('   Wait .....', 2)
        time.sleep(3)
        lcd.lcd_display_string('   Printed', 1)
        lcd.lcd_display_string('   Successfully', 2)
        time.sleep(8)
        lcd.lcd_clear()
        try:
            os.remove(str(file_to_print))
        except:
            pass
        take_otp()
    except:
        lcd.lcd_clear()
        lcd.lcd_display_string(' Getting Issues', 1)
        lcd.lcd_display_string('Please Try Again', 2)
        time.sleep(3)
        lcd.lcd_clear()
        take_otp()


def secret_enter():
    import socket
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    local_ip = s.getsockname()[0]
    lcd.lcd_clear()
    lcd.lcd_display_string('LOCAL IP : ', 1)
    lcd.lcd_display_string(str(local_ip), 2)
    s.close()
    time.sleep(7)
    take_otp()


# function to call server with otp1 and otp2
def request_otp(otp_1, otp_2):
    lcd.lcd_clear()
    lcd.lcd_display_string('  Please Wait..', 2)
    try:
        url = '{http_url}getprint/{otp_1}/{otp_2}'.format(http_url=http_url, otp_1=otp_1, otp_2=otp_2)
        response = requests.get(url)
        all_text = response.text
        response.close()
        if '<h6>' in all_text:
            link_text = http_url + 'media/' + (all_text[all_text.find('<h6>') + 4:all_text.find('</h6>')])
            ext = link_text[link_text.rfind('.'):]
            file_name = 'file_tobe_print' + ext
            color_mode = all_text[all_text.find('<h5>') + 4:all_text.find('</h5>')]
            if 'olor' in color_mode:
                color_mode = 'color'
            else:
                color_mode = 'b&w'
            payment_mode = all_text[all_text.find('<h4>') + 4:all_text.find('</h4>')]
            amount = float(all_text[all_text.find('<h3>') + 4:all_text.find('</h3>')])
            urllib.request.urlretrieve(link_text, file_name)
            if payment_mode == 'Coin':
                lcd.lcd_clear()
                lcd.lcd_display_string('Put {0} rs'.format(amount), 1)
                lcd.lcd_display_string('in Coinbox', 2)
                input_amount = 0
                GPIO.setup(13, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
                while input_amount < amount:
                    pulse = GPIO.input(13)
                    if pulse == 0:
                        print('coin accepted')
                        input_amount += 1
                        lcd.lcd_clear()
                        lcd.lcd_display_string(str(amount), 1)
                        lcd.lcd_display_string(str(input_amount), 2)
                        time.sleep(0.5)
                else:
                    take_print(file_name, color_mode)
            elif payment_mode == 'Account':
                take_print(file_name, color_mode)
            else:
                lcd.lcd_clear()
                lcd.lcd_display_string(' Getting Issues', 1)
                lcd.lcd_display_string('Please Try Again', 2)
                time.sleep(3)
                take_otp()
        elif '<h1>' in all_text:
            lcd.lcd_clear()
            lcd.lcd_display_string('   Wrong OTP ', 2)
            time.sleep(3)
            take_otp()
        else:
            lcd.lcd_clear()
            lcd.lcd_display_string(' Getting Issues', 1)
            lcd.lcd_display_string('Please Try Again', 2)
            time.sleep(3)
            take_otp()
    except:
        lcd.lcd_clear()
        lcd.lcd_display_string(' Getting Issues', 1)
        lcd.lcd_display_string('Please Try Again', 2)
        time.sleep(3)
        take_otp()


# function to take otp1 and otp2
def take_otp():
    otp_1 = ''
    otp_2 = ''
    lcd.lcd_clear()
    lcd.lcd_display_string('OTP 1 : ', 1)
    lcd.lcd_display_string('OTP 2 : ', 2)
    GPIO.setmode(GPIO.BOARD)
    MATRIX = [['1', '2', '3', 'A'],
              ['4', '5', '6', 'B'],
              ['7', '8', '9', 'C'],
              ['*', '0', '#', 'D']]
    ROW = [37, 35, 33, 31]
    COL = [29, 40, 38, 36]
    for j in range(4):
        GPIO.setup(COL[j], GPIO.OUT)
        GPIO.output(COL[j], 1)
    for i in range(4):
        GPIO.setup(ROW[i], GPIO.IN, pull_up_down=GPIO.PUD_UP)
    try:
        while True:
            for j in range(4):
                GPIO.output(COL[j], 0)
                for i in range(4):
                    if GPIO.input(ROW[i]) == 0:
                        number = MATRIX[i][j]
                        time.sleep(0.3)
                        if number == 'D':
                            if len(otp_1) == 4 and len(otp_2) == 4:
                                if otp_1 == otp_2 == secret_code:
                                    secret_enter()
                                else:
                                    request_otp(otp_1, otp_2)
                            else:
                                pass
                        elif number == 'C':
                            if len(otp_2) == 0 and len(otp_1) > 0:
                                otp_1 = otp_1[:-1]
                                lcd.lcd_clear()
                                lcd.lcd_display_string(('OTP 1 : ' + otp_1), 1)
                                lcd.lcd_display_string(('OTP 2 : ' + otp_2), 2)
                            elif len(otp_1) == 4 and len(otp_2) > 0:
                                otp_2 = otp_2[:-1]
                                lcd.lcd_clear()
                                lcd.lcd_display_string(('OTP 1 : ' + otp_1), 1)
                                lcd.lcd_display_string(('OTP 2 : ' + otp_2), 2)
                            else:
                                pass
                        elif number in ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0']:
                            if len(otp_1) < 4 and len(otp_2) == 0:
                                otp_1 += number
                                lcd.lcd_display_string(('OTP 1 : ' + otp_1), 1)
                                lcd.lcd_display_string(('OTP 2 : ' + otp_2), 2)
                            elif len(otp_1) == 4 and len(otp_2) < 4:
                                otp_2 += number
                                lcd.lcd_display_string(('OTP 1 : ' + otp_1), 1)
                                lcd.lcd_display_string(('OTP 2 : ' + otp_2), 2)
                            else:
                                pass
                        else:
                            pass
                        while GPIO.input(ROW[i] == 0):
                            pass
                GPIO.output(COL[j], 1)
    except KeyboardInterrupt:
        GPIO.cleanup()

take_otp()



###############################################################################################################
############################## FOR OTP1 THEN ENTER THEN OTP2 THEN ENTER FUNCTIONALITY   #######################
###############################################################################################################
# import os
# from PIL import Image
# import subprocess
# import urllib
# import requests
# import time
# import lcddriver
# import RPi.GPIO as GPIO
# import time
#
# lcd = lcddriver.lcd()
# lcd.lcd_clear()
# lcd.lcd_display_string('   Loading...', 1)
# lcd.lcd_display_string('   Please Wait  ', 2)
# time.sleep(3)
# lcd.lcd_clear()
# subprocess.call('lpoptions -d e130', shell=True)
# ms_office = ['docx', 'doc', 'xls', 'xlsx', 'ppt',
#              'odt', 'ods']
# pngs = ['png']
#
#
# # function png to jpg
# def png_to_jpg(file_name):
#     jpg_file = file_name[:file_name.find('.')] + '.jpg'
#     png_file = Image.open(file_name)
#     bground = Image.new('RGB', png_file.size, (255, 255, 255))
#     bground.paste(png_file, (0, 0), png_file)
#     bground.save(jpg_file, quality=95)
#     return jpg_file
#
#
# # function ms office files to pdf
# def ms_to_pdf(file_name):
#     command1 = 'doc2pdf ' + file_name
#     subprocess.call(command1, shell=True)
#     pdf_file = file_name[:file_name.find('.')] + '.pdf'
#     return pdf_file
#
#
# # function to give print command
# def take_print(file_name, color_mode):
#     try:
#         file_type = file_name[file_name.find('.') + 1:]
#         if file_type in pngs:
#             file_to_print = png_to_jpg(file_name)
#         elif file_type in ms_office:
#             file_to_print = ms_to_pdf(file_name)
#         else:
#             file_to_print = file_name
#         color_model = ' -o ColorModel=RGB ' if color_mode == 'color' else ''
#         print_command = 'lp -o page-ranges=1 {color_model} {file_to_print} '.format(
#             file_to_print=file_to_print,
#             color_model=color_model)
#         subprocess.call(print_command, shell=True)
#         lcd.lcd_clear()
#         lcd.lcd_display_string('   Please ', 1)
#         lcd.lcd_display_string('   Wait .....', 2)
#         time.sleep(3)
#         lcd.lcd_display_string('   Printed', 1)
#         lcd.lcd_display_string('   Successfully', 2)
#         time.sleep(8)
#         lcd.lcd_clear()
#         try:
#             os.remove(str(file_to_print))
#         except:
#             pass
#         take_otp()
#     except:
#         lcd.lcd_clear()
#         lcd.lcd_display_string(' Getting Issues', 1)
#         lcd.lcd_display_string('Please Try Again', 2)
#         time.sleep(3)
#         lcd.lcd_clear()
#         take_otp()
#
#
# def secret_enter():
#     import socket
#     s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#     s.connect(("8.8.8.8", 80))
#     local_ip = s.getsockname()[0]
#     lcd.lcd_clear()
#     lcd.lcd_display_string('LOCAL IP : ', 1)
#     lcd.lcd_display_string(str(local_ip), 2)
#     s.close()
#     time.sleep(7)
#     take_otp()
#
#
# # function to call server with otp1 and otp2
# def request_otp(otp_1, otp_2):
#     lcd.lcd_clear()
#     lcd.lcd_display_string('  Please Wait..', 2)
#     try:
#         http_url = 'http://192.168.0.108:8000/'
#         url = '{http_url}getprint/{otp_1}/{otp_2}'.format(http_url=http_url, otp_1=otp_1, otp_2=otp_2)
#         print(url)
#         response = requests.get(url)
#         all_text = response.text
#         response.close()
#         if '<h6>' in all_text:
#             link_text = http_url + 'media/' + (all_text[all_text.find('<h6>') + 4:all_text.find('</h6>')])
#             ext = link_text[link_text.rfind('.'):]
#             file_name = 'file_tobe_print' + ext
#             color_mode = all_text[all_text.find('<h5>') + 4:all_text.find('</h5>')]
#             if 'olor' in color_mode:
#                 color_mode = 'color'
#             else:
#                 color_mode = 'b&w'
#             payment_mode = all_text[all_text.find('<h4>') + 4:all_text.find('</h4>')]
#             print(payment_mode)
#             amount = float(all_text[all_text.find('<h3>') + 4:all_text.find('</h3>')])
#             print(amount)
#             print(link_text)
#             urllib.request.urlretrieve(link_text, file_name)
#
#             if payment_mode == 'Coin':
#                 print('coin separate')
#                 lcd.lcd_clear()
#                 lcd.lcd_display_string('Put {0} rs'.format(amount), 1)
#                 lcd.lcd_display_string('in Coinbox', 2)
#                 input_amount = 0
#                 GPIO.setup(13, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
#                 while input_amount < amount:
#                     pulse = GPIO.input(13)
#                     if pulse == 0:
#                         print('coin accepted')
#                         input_amount += 1
#                         lcd.lcd_clear()
#                         lcd.lcd_display_string(str(amount), 1)
#                         lcd.lcd_display_string(str(input_amount), 2)
#                         time.sleep(0.5)
#                 else:
#                     take_print(file_name, color_mode)
#             else:
#                 take_print(file_name, color_mode)
#         elif '<h1>' in all_text:
#             lcd.lcd_clear()
#             lcd.lcd_display_string('   Wrong OTP ', 2)
#             time.sleep(3)
#             take_otp()
#         else:
#             lcd.lcd_clear()
#             lcd.lcd_display_string(' Getting Issues', 1)
#             lcd.lcd_display_string('Please Try Again', 2)
#             time.sleep(3)
#             take_otp()
#     except:
#         lcd.lcd_clear()
#         lcd.lcd_display_string(' Getting Issues', 1)
#         lcd.lcd_display_string('Please Try Again', 2)
#         time.sleep(3)
#         take_otp()
#
#
# # function to take otp1 and otp2
# def take_otp():
#     otp_1 = ''
#     otp_2 = ''
#     current_otp = 1
#     lcd.lcd_clear()
#     lcd.lcd_display_string('OTP 1 : ', 1)
#     lcd.lcd_display_string('OTP 2 : ', 2)
#     GPIO.setmode(GPIO.BOARD)
#     MATRIX = [['1', '2', '3', 'A'],
#               ['4', '5', '6', 'B'],
#               ['7', '8', '9', 'C'],
#               ['*', '0', '#', 'D']]
#     ROW = [37, 35, 33, 31]
#     COL = [29, 40, 38, 36]
#     for j in range(4):
#         GPIO.setup(COL[j], GPIO.OUT)
#         GPIO.output(COL[j], 1)
#     for i in range(4):
#         GPIO.setup(ROW[i], GPIO.IN, pull_up_down=GPIO.PUD_UP)
#     try:
#         while True:
#             for j in range(4):
#                 GPIO.output(COL[j], 0)
#                 for i in range(4):
#                     if GPIO.input(ROW[i]) == 0:
#                         number = MATRIX[i][j]
#                         time.sleep(0.3)
#                         if number == 'D':
#                             if current_otp == 1 and len(otp_1) > 0:
#                                 current_otp = 2
#                             elif current_otp == 2 and len(otp_2) > 0:
#                                 if str(otp_1) == '1515' and str(otp_2) == '1515':
#                                     secret_enter()
#                                 else:
#                                     request_otp(otp_1, otp_2)
#                             else:
#                                 pass
#                         elif number == 'C':
#                             if current_otp == 1 and len(otp_1) > 0:
#                                 otp_1 = otp_1[:-1]
#                                 lcd.lcd_clear()
#                                 lcd.lcd_display_string(('OTP 1 : ' + otp_1), 1)
#                                 lcd.lcd_display_string(('OTP 2 : ' + otp_2), 2)
#                             elif current_otp == 2 and len(otp_2) > 0:
#                                 otp_2 = otp_2[:-1]
#                                 lcd.lcd_clear()
#                                 lcd.lcd_display_string(('OTP 1 : ' + otp_1), 1)
#                                 lcd.lcd_display_string(('OTP 2 : ' + otp_2), 2)
#                             else:
#                                 pass
#                         else:
#                             if number in ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0']:
#                                 if current_otp == 1:
#                                     otp_1 += number
#                                     lcd.lcd_display_string(('OTP 1 : ' + otp_1), 1)
#                                     lcd.lcd_display_string(('OTP 2 : ' + otp_2), 2)
#                                 elif current_otp == 2:
#                                     otp_2 += number
#                                     lcd.lcd_display_string(('OTP 1 : ' + otp_1), 1)
#                                     lcd.lcd_display_string(('OTP 2 : ' + otp_2), 2)
#                                 else:
#                                     pass
#                             else:
#                                 pass
#                         while GPIO.input(ROW[i] == 0):
#                             pass
#                 GPIO.output(COL[j], 1)
#     except KeyboardInterrupt:
#         GPIO.cleanup()
#
# take_otp()



####################################################################################################
############################################ END POINT #############################################
####################################################################################################







