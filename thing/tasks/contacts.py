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
        results = self.root.find('result')
        contactrowsets = results.findall('rowset')
        
        for contactrowset in contactrowsets:
            rows = contactrowset.findall('row')
            for row in rows:
                contact = Contact(
                    id=row.get('contactID'),
                    character_id=character.id,
                    contact_name=row.get('contactName'),
                    standing=row.get('standing'),
                )
                contactlist.append(contact)
            
            for con in contactlist:
                try:
                    contact = Contact.objects.get(pk=con.id)
                except Contact.DoesNotExist:
                    contact = Contact(
                        id=con.id,
                        character_id=con.character_id,
                        contact_name=con.contact_name,
                        standing=con.standing,
                    )
                    new.append(contact)
            
            # Bulk create any new Contact objects
            if new:
                Contact.objects.bulk_create(new)
            else:
                contact.character_id = con.character_id
                contact.contact_name = con.contact_name
                contact.standing = con.standing
                contact.save()
        
        return True
        