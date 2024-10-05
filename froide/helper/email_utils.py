"""

Original EmailParser Code by Ian Lewis:
http://www.ianlewis.org/en/parsing-email-attachments-python
Licensed under MIT

"""
from datetime import datetime, timedelta
import time

import base64

try:
    from email.header import decode_header
    from email.parser import BytesParser as Parser
except ImportError:
    from email.Header import decode_header
    from email.Parser import Parser

from email.utils import parseaddr, formataddr, parsedate_tz, getaddresses
import imaplib
import re

from django.utils.six import BytesIO, text_type as str, binary_type as bytes

import pytz


def get_unread_mails(host, port, user, password, ssl=True):
    klass = imaplib.IMAP4
    if ssl:
        klass = imaplib.IMAP4_SSL
    mail = klass(host, port)
    mail.login(user, password)
    try:
        status, count = mail.select('Inbox')
        typ, data = mail.search(None, 'UNSEEN')
        for num in data[0].split():
            status, data = mail.fetch(num, '(RFC822)')
            yield data[0][1]
    finally:
        mail.close()
        mail.logout()


def make_address(email, name=None):
    if name:
        return formataddr((name, email))
    return email


class UnsupportedMailFormat(Exception):
    pass


class EmailParser(object):

    def parse_dispositions(self, dispo):
        dispos = dispo.strip().split(";", 1)
        dispo_name = dispos[0].lower()
        dispo_dict = {}
        for param in dispos[1:]:
            name, value = param.split("=", 1)
            name = name.lower().strip()
            value = value.strip()
            if value.startswith('"') and value.endswith('"'):
                value = value[1:-1]
            dispo_dict[name] = self.parse_header_field(value)
        return dispo_name, dispo_dict

    def parse_attachment(self, message_part):
        content_disposition = message_part.get("Content-Disposition", None)
        if content_disposition:
            dispo_type, dispo_dict = self.parse_dispositions(content_disposition)
            if dispo_type == "attachment" or (dispo_type == 'inline' and
                    'filename' in dispo_dict):
                content_type = message_part.get("Content-Type", None)
                file_data = message_part.get_payload(decode=True)
                if file_data is None:
                    payloads = message_part.get_payload()
                    file_data = '\n\n'.join([p.as_string() for p in payloads]).encode('utf-8')
                attachment = BytesIO(file_data)
                attachment.content_type = message_part.get_content_type()
                attachment.size = len(file_data)
                attachment.name = None
                attachment.create_date = None
                attachment.mod_date = None
                attachment.read_date = None
                if "filename" in dispo_dict:
                    attachment.name = dispo_dict['filename']
                if content_type:
                    _, content_dict = self.parse_dispositions(content_type)
                    if 'name' in content_dict:
                        attachment.name = content_dict['name']
                if attachment.name is None and content_type == 'message/rfc822':
                    p = Parser()
                    msgobj = p.parse(BytesIO(attachment.getvalue()))
                    subject = self.parse_header_field(msgobj['Subject'])
                    if subject:
                        attachment.name = '%s.eml' % subject[:45]
                if "create-date" in dispo_dict:
                    attachment.create_date = dispo_dict['create-date']  # TODO: datetime
                if "modification-date" in dispo_dict:
                    attachment.mod_date = dispo_dict['modification-date']  # TODO: datetime
                if "read-date" in dispo_dict:
                    attachment.read_date = dispo_dict['read-date']  # TODO: datetime
                return attachment
        return None

    def parse_header_field(self, field):
        if field is None:
            return None

        # preprocess head field
        # see http://stackoverflow.com/questions/7331351/python-email-header-decoding-utf-8
        field = re.sub(r"(=\?.*\?=)(?!$)", r"\1 ", field)

        decodefrag = decode_header(field)
        fragments = []
        for s, enc in decodefrag:
            if enc:
                try:
                    s = str(s, enc, errors='replace')
                except UnicodeDecodeError:
                    # desperate move here
                    try:
                        s = s.decode("latin1")
                    except:
                        pass
            else:
                try:
                    if not isinstance(s, str):
                        s = s.decode("latin1")
                except UnicodeDecodeError:
                    s = str(s, errors='ignore')
            fragments.append(s.strip(' '))
        field = ' '.join(fragments)
        return field.replace('\n\t', " ").replace('\n', '').replace('\r', '')

    def get_address_list(self, values):
        address_list = getaddresses(values)
        fixed = []
        for addr in address_list:
            fixed.append((self.parse_header_field(addr[0]), addr[1].lower()))
        return fixed

    def parse_date(self, date_str):
        date_tuple = parsedate_tz(date_str)
        if date_tuple is None:
            return None
        date = datetime.fromtimestamp(time.mktime(date_tuple[:9]))
        offset = date_tuple[9]
        if offset is not None:
            date = date - timedelta(seconds=offset)
        return pytz.utc.localize(date)

    def parse_body(self, parts, attachments, body, html):
        for part in parts:
            attachment = self.parse_attachment(part)
            if attachment:
                attachments.append(attachment)
            elif part.get_content_type() == "text/plain":
                charset = part.get_content_charset() or 'ascii'
                body.append(str(
                    part.get_payload(decode=True),
                    charset, 'replace'))
            elif part.get_content_type() == "text/html":
                charset = part.get_content_charset() or 'ascii'
                html.append(str(
                    part.get_payload(decode=True),
                    charset, 'replace'))

    def get(self, field):
        if isinstance(field, bytes):
            return field
        return str(field)

    def parse(self, bytesfile):
        p = Parser()
        msgobj = p.parse(bytesfile)
        subject = self.parse_header_field(msgobj['Subject'])
        attachments = []
        body = []
        html = []
        self.parse_body(msgobj.walk(), attachments, body, html)
        body = '\n'.join(body)
        html = '\n'.join(html)

        tos = self.get_address_list(msgobj.get_all('To', []))
        tos.extend(self.get_address_list(msgobj.get_all('X-Original-To', [])))
        ccs = self.get_address_list(msgobj.get_all('Cc', []))
        resent_tos = self.get_address_list(msgobj.get_all('resent-to', []))
        resent_ccs = self.get_address_list(msgobj.get_all('resent-cc', []))

        from_field = parseaddr(self.get(msgobj.get('From')))
        from_field = (self.parse_header_field(from_field[0]),
                      from_field[1].lower() if from_field[1] else from_field[1])
        date = self.parse_date(self.get(msgobj.get("Date")))
        return {
            'msgobj': msgobj,
            'date': date,
            'subject': subject,
            'body': body,
            'html': html,
            'from': from_field,
            'to': tos,
            'cc': ccs,
            'resent_to': resent_tos,
            'resent_cc': resent_ccs,
            'attachments': attachments
        }

    def parse_postmark(self, obj):
        from_field = (obj['FromFull']['Name'], obj['FromFull']['Email'])
        tos = [(o['Name'], o['Email']) for o in obj['ToFull']]
        ccs = [(o['Name'], o['Email']) for o in obj['CcFull']]
        attachments = []
        for a in obj['Attachments']:
            attachment = BytesIO(base64.b64decode(a['Content']))
            attachment.content_type = a['ContentType']
            attachment.size = a['ContentLength']
            attachment.name = a['Name']
            attachment.create_date = None
            attachment.mod_date = None
            attachment.read_date = None
            attachments.append(attachment)

        return {
            'msgobj': obj,
            'date': self.parse_date(obj['Date']),
            'subject': obj['Subject'],
            'body': obj['TextBody'],
            'html': obj['HtmlBody'],
            'from': from_field,
            'to': tos,
            'cc': ccs,
            'resent_to': [],
            'resent_cc': [],
            'attachments': attachments
        }


if __name__ == '__main__':
    p = EmailParser()
    email = p.parse(open('../foirequest/tests/test_mail_03.txt').read())
    for i, at in enumerate(email['attachments']):
        open(getattr(at, 'name', 'test'), 'w').write(at.read())
