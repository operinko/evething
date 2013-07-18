from .apitask import APITask

from thing.models import APIKey, Character, MailMessage, MailBody

# ---------------------------------------------------------------------------
#class AccountStatus(APITask):
#    name = 'thing.account_status'
#
#    def run(self, url, taskstate_id, apikey_id, zero):
#        if self.init(taskstate_id, apikey_id) is False:
#            return
#
#        # Fetch the API data
#        if self.fetch_api(url, {}) is False or self.root is None:
#            return
#
#        # Update paid_until
#        paidUntil = self.parse_api_date(self.root.findtext('result/paidUntil'))
#        if paidUntil != self.apikey.paid_until:
#            self.apikey.paid_until = paidUntil
#            self.apikey.save()
#
#        return True
# ---------------------------------------------------------------------------

class MailMessages(APITask):
    name = 'thing.mail_messages'

    def run(self, url, taskstate_id, apikey_id, character_id):
        if self.init(taskstate_id, apikey_id) is False:
            return

        # Make sure the character exists
        try:
            character = Character.objects.select_related('details').get(pk=character_id)
        except Character.DoesNotExist:
            self.log_warn('Character %s does not exist!', character_id)
            return

        # Initialise stuff
        params = {
            'characterID': character.id,
        }

        # Fetch the API data
        if self.fetch_api(url, params) is False or self.root is None:
            return

        new = []
        messagelist = []
        mails = self.root.find('result/rowset').findall('row')

        for mail in mails:
            from_char = character.id
            to_chars = []
            to_chars_a = mail.get('toCharacterIDs')
            chars = to_chars_a.split(',')
            sender_id = int(mail.get('senderID'))
            try:
                sender = Character.objects.get(pk=sender_id)
                if sender.name == "":
                    send_task('thing.new_character_info', args=['/eve/CharacterInfo.xml.aspx', sender_id], kwargs={}, queue='et_high')
            except Character.DoesNotExist:
                from celery.execute import send_task
                send_task('thing.new_character_info', args=['/eve/CharacterInfo.xml.aspx', sender_id], kwargs={}, queue='et_high')

            for char in chars:
                if char != "":
                    from celery.execute import send_task
                    send_task('thing.new_character_info', args=['/eve/CharacterInfo.xml.aspx', char], kwargs={}, queue='et_high')

            corp = mail.get('toCorpOrAllianceID')
            if corp == '':
                corp = int()

            message = MailMessage(
                from_char_id = from_char,
                message_id=int(mail.get('messageID')),
                sender_id=int(mail.get('senderID')),
                sent_date=mail.get('sentDate'),
                title=mail.get('title'),
                to_corp_or_ally_id=int(corp),
                to_characters=mail.get('toCharacterIDs'),
                to_lists=mail.get('toListIDs'),
            )
            messagelist.append(message)
        
        bodies = []
        for msg in messagelist:
            bodies.append(msg.message_id)
            try:
                message = MailMessage.objects.get(message_id=msg.message_id, from_char_id=character.id)
            except MailMessage.DoesNotExist:
                msg.save()

        from celery.execute import send_task
        send_task('thing.mail_bodies', args=['/char/MailBodies.xml.aspx', apikey_id, character_id, bodies], kwargs={}, queue='et_medium')
        return True

# ---------------------------------------------------------------------------

class MailBodies(APITask):
    name = 'thing.mail_bodies'

    def run(self, url, apikey_id, character_id, mailmessage_ids):
        if self.init(apikey_id) is False:
            return
        # Implode the mail message ID list to a comma-seperated list.
        ids = ','.join(str(i) for i in mailmessage_ids)

        # Initialise stuff
        params = {
            'characterID': character_id,
            'ids': ids,
        }

        # Force getting the API Key
        self.apikey = APIKey.objects.select_related('corp_character__corporation').get(pk=apikey_id)

        # Fetch the API data
        if self.fetch_api(url, params) is False or self.root is None:
            return

        new = []
        mails = self.root.findall('result/rowset/row')
        for mail in mails:
          try:
              dbmail = MailBody.objects.get(pk=mail.attrib['messageID'])
              dbmail.body = mail.text
              dbmail.save()
          except MailBody.DoesNotExist:
              newmail = MailBody(
                  message_id = mail.attrib['messageID'],
                  body = mail.text,
              )
              new.append(newmail)

        if new:
            MailBody.objects.bulk_create(new)

        return True

# ---------------------------------------------------------------------------