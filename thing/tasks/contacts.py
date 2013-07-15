from .apitask import APITask

from thing.models import APIKey, Character, Contact

class ContactList(APITask):
    name = 'thing.contact_list'

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
        if self.fetch_api(url, params) is False or self.root is None:
            return False

        new = []
        contactlist = []
        result = self.root.find('result')
        rowsets = result.findall('rowset')

        for rowset in rowsets:
            contact_type = rowset.get('name')
            rows = rowset.findall('row')
            for row in rows:
                standing = float(row.get('standing'))
                typeid = float(row.get('contactTypeID'))
                if typeid == 2:
                    contact_who = 'corp'
                elif typeid == 16159:
                    contact_who = 'alli'
                else:
                    contact_who = 'pilot'

                # High, Good, Neutral, Bad, Horrible
                if standing == 10:
                    contact_class = "standing-high"
                elif 5 < standing < 10:
                    contact_class = "standing-high"
                elif standing == 5:
                    contact_class = "standing-good"
                elif 0 < standing < 5:
                    contact_class = "standing-good"
                elif standing == 0.0:
                    contact_class = "standing-neutral"
                elif 0 > standing > -5:
                    contact_class = "standing-bad"
                elif standing == -5:
                    contact_class = "standing-bad"
                elif -5 > standing > -10:
                    contact_class="standing-horrible"
                elif standing == -10:
                    contact_class="standing-horrible"
                else:
                    contact_class="standing-unknown"

                contact = Contact(
                    contact_id=row.get('contactID'),
                    character=character,
                    contact_name=row.get('contactName'),
                    standing=standing,
                    contact_type=contact_type,
                    contact_class=contact_class,
                    contact_who=contact_who,
                )
                contactlist.append(contact)

            for con in contactlist:
                try:
                    contact = Contact.objects.get(contact_id=con.contact_id, character__id=character.id)
                    contact.character = character
                    contact.contact_name = con.contact_name
                    contact.standing = con.standing
                    contact.contact_type=con.contact_type
                    contact.contact_class=con.contact_class
                    contact.contact_who=con.contact_who
                    contact.save()
                except Contact.DoesNotExist:
                    contact = Contact(
                        contact_id=con.contact_id,
                        character=character,
                        contact_name=con.contact_name,
                        standing=con.standing,
                        contact_type=con.contact_type,
                        contact_class=con.contact_class,
                        contact_who=con.contact_who,
                    )
                    contact.save()

        return True
