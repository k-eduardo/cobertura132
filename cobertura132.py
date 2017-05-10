#!/usr/bin/python
# -*- coding: latin1 -*-

import imaplib, email, getpass, imaplib, os, re, random
from email.header import Header,decode_header
import smtplib
from email.mime.text import MIMEText


def Email(to, subject, text,gmail_user,gmail_pwd):

   msg = MIMEText(text)

   msg['From'] = gmail_user
   msg['To'] = to
   msg['Subject'] = subject
 
   s = smtplib.SMTP('smtp.gmail.com', 587)  
   s.ehlo()
   s.starttls()
   s.ehlo()
   s.login(gmail_user,gmail_pwd)
   s.sendmail(gmail_user, to, msg.as_string())
   s.close()



def get_subjects(email_ids):
    subjects = []
    for e_id in email_ids:
        _, response = imap_server.fetch(e_id, '(body.peek[header.fields (subject)])')
        subjects.append( response[0][1][9:] )
    return subjects

def get_emails(email_ids):
    data = []
    for e_id in email_ids:
        _, response = imap_server.fetch(e_id, '(UID BODY[TEXT])')
        data.append(response[0][1])
    return data

def decode_subject(subject):
	decoded = ''
	for p in decode_header(subject):
		if p[1] is None:
			decoded += p[0]
		else:
			decoded += p[0].decode(p[1])
	return decoded

username = raw_input('Usuario de la siguiente forma: correo@gmail.com: ')
password = getpass.getpass("Escribe la contraseña: ")
detach_dir = './imagenes'

FiLe=open("./datos","a")
log=open("./log","a")

imap_server = imaplib.IMAP4_SSL("imap.gmail.com",993)
imap_server.login(username, password)

imap_server.select('INBOX')

#Busca los nuevos correos
status, email_ids = imap_server.search(None, '(UNSEEN)')
#print email_ids
b=email_ids[0].split(' ')

#print email_ids

status, response = imap_server.status('INBOX', "(UNSEEN)")
unreadcount = int(response[0].split()[2].strip(').,]'))
get_subjects(b)[0]

for emailid in b:
    resp, data = imap_server.fetch(emailid, "(RFC822)") # recoge el correo, "`(RFC822)`" significa tomar todo el correo
    email_body = data[0][1] # obtiene el texto que forma el correo
    mail = email.message_from_string(email_body) # se transforma a un objeto, una lista
    addss = re.search(r"(?<=<)(.*?)(?=>)",mail['From'])
    addss = addss.group(0)
#    print "addss ",addss

    #Revisa si existen archivos adjuntos
    if mail.get_content_maintype() != 'multipart':

        GS = str(mail["Subject"])
        reg = re.findall(r"([a-zA-Z\s]*\d*)\W+", GS)
        print addss, " no tiene mensaje adjunto. Asunto: ", reg
        GS=str(reg)
        log.write(addss+' no tiene mensajes adjuntos\n')
        mensaje = "Hola, te pedimos de favor que verifiques el correo con asunto %s que nos enviaste, no tiene algún archivo adjunto.\nTe recordamos que el formato es: edo-casilla-tipo de casilla (datos de la sábana separados por comas -Pon mucha atención, son 14 datos dentro del paréntesis.)\nNo olvides ingresar los datos sólo en el asunto del mensaje.\nMuchas gracias por tu participación\n#Cobertura132" % GS
        Email(addss,"Revisa los datos que ingresaste al sistema fotoxcasilla a través de #Cobertura132",mensaje,username,password)
        continue

#    print "["+mail["From"]+"] :" + mail["Subject"]
#    print type(mail["Subject"])
    GS = str(mail["Subject"])
    reg = re.findall(r"([a-zA-Z\s]*\d*)\W+", GS)
#    print len(reg),reg
    if len(reg) == 17:
     print "Desde ", addss, " asunto: ", reg, "len", len(reg)
     GS=str(reg)
#     print GS
     # we use walk to create a generator so we can iterate on the parts and forget about the recursive headach
     for part in mail.walk():
        # multipart no son contienen el archivo
        if part.get_content_maintype() == 'multipart':
            continue

        # es esto un archivo adjunto?
        if part.get('Content-Disposition') is None:
            continue
        ran1=str(int(random.random()*10))
        ran2=str(int(random.random()*10))
        ran3=str(int(random.random()*10))
        filename=str(reg[0].zfill(2))+str(reg[1].zfill(4))+ran1+ran2+ran3+".jpeg"
#        print "Este es el nombre: "+" "+filename

        escrito = GS+' '+filename+' '+addss+'\n'
        FiLe.write(escrito)
        log.write(addss+' sí satisface los criterios de formato\n')
        att_path = os.path.join(detach_dir, filename)

        #Revisa si ya existe
        if not os.path.isfile(att_path) :
            # escribe el archivo
            fp = open(att_path, 'wb')
            fp.write(part.get_payload(decode=True))
            fp.close()
    else:
        print addss+' NO satisface el formato: ',reg
        log.write(addss+' no satisface los criterios de formato\n')
        mensaje = "Hola, te pedimos de favor que rectifiques los datos que introdujiste en el correo con asunto %s que nos enviaste.\nTe recordamos que el formato es: edo,casilla,tipo de casilla, (datos de la sábana separados por comas -Pon mucha atención, son 14 datos dentro del paréntesis.)\nTampoco olvides adjuntar tu foto e ingresar los datos sólo en el asunto del mensaje.\nMuchas gracias por tu participación\n#Cobertura132" % GS
        Email(addss,"Revisa los datos que ingresaste al sistema fotoxcasilla a través de #Cobertura132",mensaje,username,password)

