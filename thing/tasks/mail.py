from .apitask import APITask

from thing.models import APIKey, Character

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

        # Fetch the API data
        if self.fetch_api(url, {}) is False or self.root is None:
            return

        # We do nothing yet. Just return
        return True

# ---------------------------------------------------------------------------

class MailBodies(APITask):
    name = 'thing.mail_bodies'

    def run(self, url, taskstate_id, apikey_id, character_id):
        if self.init(taskstate_id, apikey_id) is False:
            return

        # Fetch the API data
        if self.fetch_api(url, {}) is False or self.root is None:
            return

        # We do nothing yet. Just return
        return True

# ---------------------------------------------------------------------------
