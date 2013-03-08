#!/usr/bin/env python
# -*- coding: UTF8 -*-

import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email.MIMEText import MIMEText
#from email.Message  import Message
from email.Utils import COMMASPACE, formatdate
from email import Encoders
import os

def sendMail(smtp_server, smtp_user, smtp_pass, from_email, to_email, subject, text, files=[]):
  assert type(to_email)==list
  assert type(files)==list
  recievers = []
  recievers.extend(to_email)
  #recievers.extend(cc)
  

  msg = MIMEMultipart()
  msg['From'] = from_email
  msg['To'] = COMMASPACE.join(to_email)
  #msg['Cc'] = COMMASPACE.join(cc)
  msg['Date'] = formatdate(localtime=True)
  msg['Subject'] = subject

  #msg.attach( MIMEText(text) )
  msg.attach( MIMEText(text,'html') )

  if not len(files):
    pass
  else:
    for file in files:
      part = MIMEBase('application', "octet-stream")
      part.set_payload( open(file,"rb").read() )
      Encoders.encode_base64(part)
      part.add_header('Content-Disposition', 'attachment; filename="%s"'
                                 % os.path.basename(file))
      msg.attach(part)

  smtp = smtplib.SMTP(smtp_server, 587)
  smtp.set_debuglevel(0)
  smtp.ehlo()
  smtp.starttls()
  smtp.ehlo()
  smtp.login(smtp_user, smtp_pass)
  #body = MIMEText(text,_subtype='html', _charset = 'utf-8')
  #msg.attach(body)
  #smtp.sendmail(fro, recievers, msg.as_string())
  smtp.sendmail(from_email, recievers, msg.as_string())
  smtp.close()
