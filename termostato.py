
#imports for thermometer reading
import os
import glob
import time
#imports for gmail reading
import imaplib
import email
#import for Telegram API
import sys
import pprint
import telepot

###################### gestisce i comandi inviati al Telegram Bot
def handle(msg):
    global Ferruccio_at_home, Claudia_at_home, Lorenzo_at_home, Riccardo_at_home
    global last_report, report_interval     #parametri per il monitoraggio su file delle temperature
    global heating_status, heating_standby  #stato di accensione dei termosifoni
    global who_is_at_home, how_many_at_home

    msg_type, chat_type, chat_id = telepot.glance2(msg)

    # ignore non-text message
    if msg_type != 'text':
        return

    command = msg['text'].strip().lower()
    CurTemp = read_temp()

    if command == '/now':
        bot.sendMessage(chat_id, "La temperatura misurata e' di "+str("%0.1f" % CurTemp)+" C, Padrone")
    elif command == '/5m':
        bot.sendMessage(chat_id, "Avvio il monitoraggio ogni 5 minuti, Padrone")
        last_report = time.time()
        report_interval = 300    # report every 60 seconds
    elif command == '/1h':
        bot.sendMessage(chat_id, "Avvio il monitoraggio ogni ora, Padrone")
        last_report = time.time()
        report_interval = 3600  # report every 3600 seconds
    elif command == '/annulla':
        last_report = None
        report_interval = None  # clear periodic reporting
        bot.sendMessage(chat_id, "Certamente, Padrone")
    elif command == '/ho_freddo':
        if heating_status:
            bot.sendMessage(chat_id, "Sto facendo del mio meglio, Padrone")
        else:
            GPIO.output(17, 1) # sets port 0 to 1 (3.3V, on) per accendere i termosifoni
            heating_status = True #print "HEATING ON "+localtime+"\n"
            bot.sendMessage(chat_id, "Accendo il riscaldamento, Padrone")
    elif command == '/ho_caldo':
        if heating_status:
            GPIO.output(17, 0) # sets port 0 to 0 (3.3V, off) per spengere i termosifoni
            heating_status = False #print "HEATING OFF "+localtime+"\n"
            bot.sendMessage(chat_id, "Spengo il riscaldamento, Padrone")
        else:      
            bot.sendMessage(chat_id, "Dovresti aprire le finestre, Padrone")
    elif command == '/casa':
        who_is_at_home=""
        how_many_at_home=0
        if Claudia_at_home:
            who_is_at_home=who_is_at_home+"Claudia "
            how_many_at_home=how_many_at_home+1
        if Ferruccio_at_home:
            who_is_at_home=who_is_at_home+"Ferruccio "
            how_many_at_home=how_many_at_home+1
        if Lorenzo_at_home:
            who_is_at_home=who_is_at_home+"Lorenzo "
            how_many_at_home=how_many_at_home+1
        if Riccardo_at_home:
            who_is_at_home=who_is_at_home+"Riccardo "
            how_many_at_home=how_many_at_home+1
        if how_many_at_home != 0:
            if how_many_at_home == 1:
                bot.sendMessage(chat_id, who_is_at_home+"e' a casa")
            else:
                bot.sendMessage(chat_id, who_is_at_home+"sono a casa")
        else:
            bot.sendMessage(chat_id, "Sono solo a casa, Padrone")
    elif command == '/help':
        # send message for help
        bot.sendMessage(chat_id, "Sono il Maggiordomo e custodisco la casa. Attendo i suoi comandi Padrone per eseguirli prontamente e rendere la sua vita piacevole e felice.\n/now - mostra la temperatura\n/ho_freddo - accende il riscaldamento\n/ho_caldo - spegne il riscaldamento\n/casa - chi e' a casa?")

    elif command == '/ferin': #forza Ferruccio a casa
        Ferruccio_at_home = True
        f = open("Ferruccio_at_home","w")  #apre il file dei dati in write mode, se il file non esiste lo crea
        f.write("IN")  #scrive la info di presence sul file
        f.close()  #chiude il file dei dati e lo salva
    elif command == '/clain': #forza Claudia a casa
        Claudia_at_home = True
        f = open("Claudia_at_home","w")  #apre il file dei dati in write mode, se il file non esiste lo crea
        f.write("IN")  #scrive la info di presence sul file
        f.close()  #chiude il file dei dati e lo salva
    elif command == '/lalloin': #forza Lorenzo a casa
        Lorenzo_at_home = True
        f = open("Lorenzo_at_home","w")  #apre il file dei dati in write mode, se il file non esiste lo crea
        f.write("IN")  #scrive la info di presence sul file
        f.close()  #chiude il file dei dati e lo salva
    elif command == '/rickyin': #forza Riccardo a casa
        Riccardo_at_home = True
        f = open("Riccardo_at_home","w")  #apre il file dei dati in write mode, se il file non esiste lo crea
        f.write("IN")  #scrive la info di presence sul file
        f.close()  #chiude il file dei dati e lo salva
       
    else:
        bot.sendMessage(chat_id, "Puoi ripetere, Padrone? I miei circuiti sono un po' arrugginiti")



############ legge da file il token del Telegram Bot e della chat id
import logging

tokenpath = os.path.dirname(os.path.realpath(__file__)) + "/token"
chatidpath = os.path.dirname(os.path.realpath(__file__)) + "/chatid"

logging.basicConfig(filename='termostato.log', level=logging.WARNING)

import requests

try:
    tokenFile = open(tokenpath,'r')
    TOKEN = tokenFile.read().strip()
    tokenFile.close()
except IOError: 
    logging.error("Non ho trovato il file di token. E' necessario creare un file 'token' con la token telegram per il bot. In ogni caso questo file NON deve essere tracciato da git - viene ignorato perche' menzionato nel .gitignore.")
    exit()

logging.info("caricata token.")
        
try:
    chatidFile = open(chatidpath,'r')
    CHAT_ID = chatidFile.read().strip()
    chatidFile.close()
except IOError:
    logging.error("Non ho trovato il file di chatId. E' necessario creare un file 'chatid' con la chatid telegram per il bot")
    # In ogni caso questo file NON deve essere tracciato da git - viene ignorato perche' menzionato nel .gitignore.")

logging.info("caricata chatId.")
    
    #-94452612 # magic number: chat_id del gruppo termostato antonelli
        

# variables for periodic reporting
last_report = None
report_interval = None

# variable for heating status
heating_status = False
heating_standby = False


################# gestione della interfaccia di GPIO   
# wiringpi numbers  
import RPi.GPIO as GPIO
##import wiringpi2 as wiringpi
##wiringpi.wiringPiSetup()
##wiringpi.pinMode(0, 1) # sets WP pin 0 to output
GPIO.setmode(GPIO.BCM)
GPIO.setup(17,GPIO.OUT)

#Find temperature from thermometer
os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')

base_dir = '/sys/bus/w1/devices/'
device_folder = glob.glob(base_dir + '28*')[0]
device_file = device_folder + '/w1_slave'

def read_temp_raw():
    f = open(device_file, 'r')
    lines = f.readlines()
    f.close()
    return lines

def read_temp():
    lines = read_temp_raw()
    while lines[0].strip()[-3:] != 'YES':
        time.sleep(0.2)
        lines = read_temp_raw()
    equals_pos = lines[1].find('t=')
    if equals_pos != -1:
        temp_string = lines[1][equals_pos+2:]
        temp_c = float(temp_string) / 1000.0
        temp_f = temp_c * 9.0 / 5.0 + 32.0
        return temp_c #, temp_f

##################### funzione per la gestione dei messaggi di presence
def set_presence(presence_msg):
    global Ferruccio_at_home, Claudia_at_home, Lorenzo_at_home, Riccardo_at_home, who_is_at_home, how_many_at_home
    global heating_status, heating_standby
    
    if len(presence_msg) !=0:
        words = presence_msg.split(' ', 2)
        nome = words[0]
        status = words[1]
        try:
            IFTTTtime = words[2]
            logging.info("IFTTTtime "+IFTTTtime)
            orario = time.strptime(IFTTTtime, "%B %d, %Y at %I:%M%p")
            logging.info("orario letto da mail "+time.asctime(orario))
        except:
            e = sys.exc_info()[0]
            logging.error( "<p>Error: %s</p>" % e )
            orario = time.localtime(now)
        # scrive la info di presence su file

        localtime = time.asctime( orario )
        filepresence = open("filepresence","a")  #apre il file dei dati in append mode, se il file non esiste lo crea
        filepresence.write(presence_msg+" "+localtime+"\n")  #scrive la info di presence ed il timestam sul file
        filepresence.close()  #chiude il file dei dati e lo salva

        if nome == 'Ferruccio':
            if status == 'IN':
                if Ferruccio_at_home == False:
                    Ferruccio_at_home = True
                    bot.sendMessage(CHAT_ID, "Benvenuto a casa "+nome)
                    f = open("Ferruccio_at_home","w")  #apre il file dei dati in write mode, se il file non esiste lo crea
                    f.write("IN")  #scrive la info di presence sul file
                    f.close()  #chiude il file dei dati e lo salva
            elif Ferruccio_at_home:
                Ferruccio_at_home = False
                bot.sendMessage(CHAT_ID, "Arrivederci a presto "+nome)
                f = open("Ferruccio_at_home","w")  #apre il file dei dati in write mode, se il file non esiste lo crea
                f.write("OUT")  #scrive la info di presence sul file
                f.close()  #chiude il file dei dati e lo salva
        elif nome == 'Claudia':
            if status == 'IN':
                if Claudia_at_home == False:
                    Claudia_at_home = True
                    bot.sendMessage(CHAT_ID, "Benvenuto a casa "+nome)
                    f = open("Claudia_at_home","w")  #apre il file dei dati in write mode, se il file non esiste lo crea
                    f.write("IN")  #scrive la info di presence sul file
                    f.close()  #chiude il file dei dati e lo salva
            elif Claudia_at_home:
                Claudia_at_home = False
                bot.sendMessage(CHAT_ID, "Arrivederci a presto "+nome)
                f = open("Claudia_at_home","w")  #apre il file dei dati in write mode, se il file non esiste lo crea
                f.write("OUT")  #scrive la info di presence sul file
                f.close()  #chiude il file dei dati e lo salva
        elif nome == 'Lorenzo':
            if status == 'IN':
                if Lorenzo_at_home == False:
                    Lorenzo_at_home = True
                    bot.sendMessage(CHAT_ID, "Benvenuto a casa "+nome)
                    f = open("Lorenzo_at_home","w")  #apre il file dei dati in write mode, se il file non esiste lo crea
                    f.write("IN")  #scrive la info di presence sul file
                    f.close()  #chiude il file dei dati e lo salva
            elif Lorenzo_at_home:
                Lorenzo_at_home = False
                bot.sendMessage(CHAT_ID, "Arrivederci a presto "+nome)
                f = open("Lorenzo_at_home","w")  #apre il file dei dati in write mode, se il file non esiste lo crea
                f.write("OUT")  #scrive la info di presence sul file
                f.close()  #chiude il file dei dati e lo salva
        elif nome == 'Riccardo':
            if status == 'IN':
                if Riccardo_at_home == False:
                    Riccardo_at_home = True
                    bot.sendMessage(CHAT_ID, "Benvenuto a casa "+nome)
                    f = open("Riccardo_at_home","w")  #apre il file dei dati in write mode, se il file non esiste lo crea
                    f.write("IN")  #scrive la info di presence sul file
                    f.close()  #chiude il file dei dati e lo salva
            elif Riccardo_at_home:
                Riccardo_at_home = False
                bot.sendMessage(CHAT_ID, "Arrivederci a presto "+nome)
                f = open("Riccardo_at_home","w")  #apre il file dei dati in write mode, se il file non esiste lo crea
                f.write("OUT")  #scrive la info di presence sul file
                f.close()  #chiude il file dei dati e lo salva
        else:
            bot.sendMessage(CHAT_ID, "Padrone verifica se ci sono sconosciuti in casa!")
    # calcola chi e' a casa
    who_is_at_home=""
    how_many_at_home=0
    if Claudia_at_home:
        who_is_at_home=who_is_at_home+"Claudia "
        how_many_at_home=how_many_at_home+1
    if Ferruccio_at_home:
        who_is_at_home=who_is_at_home+"Ferruccio "
        how_many_at_home=how_many_at_home+1
    if Lorenzo_at_home:
        who_is_at_home=who_is_at_home+"Lorenzo "
        how_many_at_home=how_many_at_home+1
    if Riccardo_at_home:
        who_is_at_home=who_is_at_home+"Riccardo "
        how_many_at_home=how_many_at_home+1
    if how_many_at_home == 0: #nessuno in casa
        if heating_standby == False:  #standby termosifoni non attivo
            heating_standby = True
            if heating_status: #se termosifoni attivi
                GPIO.output(17, 0) # spenge i termosifoni
                bot.sendMessage(CHAT_ID, "Ho messo in stand by il riscaldamento in attesa che rientri qualcuno a casa")
    else: #almeno una persona in casa
        if heating_standby: #se standby attivo
            heating_standby = False
            if heating_status: #se termosifoni attivi prima dello standby
                GPIO.output(17, 1) # riaccende i termosifoni
                bot.sendMessage(CHAT_ID, "Ho riavviato il riscaldamento per il tuo confort, Padrone")
    #return set_presence            




##################### inizio gestione presence via email ################
#connect to gmail
def read_gmail():
    mail = imaplib.IMAP4_SSL('imap.gmail.com')
    mail.login('MaggiordomoBot@gmail.com','cldbzz00') #login e password da mettere su file successivamente
    mail.select('inbox')
    mail.list()

    # Any Emails? 
    n=0
    (retcode, messages) = mail.search(None, '(UNSEEN)')
    if retcode == 'OK':
        for num in messages[0].split() :
            logging.info('Processing new emails...')
            n=n+1
            typ, data = mail.fetch(num,'(RFC822)')
            for response_part in data:
                if isinstance(response_part, tuple):
                    original = email.message_from_string(response_part[1])
                    subject_text=str(original['Subject'])
                    set_presence(subject_text) #richiama la funzione per la gestisce della presence
                    typ, data = mail.store(num,'+FLAGS','\\Seen') #segna la mail come letta
            logging.info("Ho gestito "+str(n)+" messaggi di presence")
############################### fine gestione presence via email #######################


#inizio programma

try:
    f = open("Ferruccio_at_home","r")  #apre il file dei dati in read mode
    pres=f.read().strip()   #legge la info di presence sul file
    f.close()  #chiude il file dei dati e lo salva
    if pres == "IN":
        Ferruccio_at_home = True
    else:
        Ferruccio_at_home = False
except IOError:
    Ferruccio_at_home = False  #se il file non e' presente imposto la presence a False

try:
    f = open("Claudia_at_home","r")  #apre il file dei dati in read mode
    pres=f.read().strip()   #legge la info di presence sul file
    f.close()  #chiude il file dei dati e lo salva
    if pres == "IN":
        Claudia_at_home = True
    else:
        Claudia_at_home = False
except IOError:
    Claudia_at_home = False  #se il file non e' presente imposto la presence a False

try:
    f = open("Lorenzo_at_home","r")  #apre il file dei dati in read mode
    pres=f.read().strip()   #legge la info di presence sul file
    f.close()  #chiude il file dei dati e lo salva
    if pres == "IN":
        Lorenzo_at_home = True
    else:
        Lorenzo_at_home = False
except IOError:
    Lorenzo_at_home = False  #se il file non e' presente imposto la presence a False

try:
    f = open("Riccardo_at_home","r")  #apre il file dei dati in read mode
    pres=f.read().strip()   #legge la info di presence sul file
    f.close()  #chiude il file dei dati e lo salva
    if pres == "IN":
        Riccardo_at_home = True
    else:
        Riccardo_at_home = False
except IOError:
    Riccardo_at_home = False  #se il file non e' presente imposto la presence a False

bot = telepot.Bot(TOKEN)
bot.notifyOnMessage(handle)
logging.info("Listening ...")

show_keyboard = {'keyboard': [['/now','/casa'], ['/ho_caldo','/ho_freddo']]} #tastiera personalizzata
bot.sendMessage(CHAT_ID, 'Mi sono appena svegliato, Padrone')
bot.sendMessage(CHAT_ID, 'Come ti posso aiutare?', reply_markup=show_keyboard)

while True:
    #try:
        # Is it time to report again?
        now = time.time()
        localtime = time.asctime( time.localtime(now) )
        if report_interval is not None and last_report is not None and now - last_report >= report_interval:
            CurTemp = read_temp()
            #apre il file dei dati in append mode, se il file non esiste lo crea
            filedati = open("filedati","a")
            #scrive la temperatura coreente ed il timestam sul file
            filedati.write(str(CurTemp)+"@"+localtime+"\n")
            #chiude il file dei dati e lo salva
            filedati.close()
        
            last_report = now
        # verifica se ci sono nuovi aggiornamenti sulla presence (via email)
        read_gmail()
        time.sleep(60)
    #except Exception:
    #    logging.exception("C'e' stato un errore del programma termostato")
    
    #if (Tdes > CurTemp):#Compare varSubject to temp
    #    GPIO.output(17, 1) # sets port 0 to 1 (3.3V, on)
    #    print "HEATING ON "+localtime+"\n"
    #    bot.sendMessage("HEATING ON @ "+localtime)
    #else:
    #    GPIO.output(17, 0) # sets port 0 to 0 (3.3V, off)
    #    print "HEATING OFF "+localtime+"\n"
    #    bot.sendMessage("HEATING OFF @ "+localtime)
    #    time.sleep(300) #wait 5 minutes
    # manda un telegram con la temperatura ogni 12 x 5 minuti = 1 ora
    #bot.sendMessage(CHAT_ID, "La temperatura misurata e' di "+str(CurTemp)+" C, Padrone")
