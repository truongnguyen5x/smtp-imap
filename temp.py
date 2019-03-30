import imaplib

mail = imaplib.IMAP4_SSL('imap.gmail.com',993)

mail.login('truongnguyen5x','truongdi3n')
print(mail.list('/'))