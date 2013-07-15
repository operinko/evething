from .apitask import APITask

from thing.models import Character, Corporation

# ---------------------------------------------------------------------------

class CharacterInfo(APITask):
    name = 'thing.character_info'

    def run(self, url, taskstate_id, apikey_id, character_id):
        if self.init(taskstate_id, apikey_id) is False:
            return

        try:
            character = Character.objects.select_related('details').get(pk=character_id)
        except Character.DoesNotExist:
            self.log_warn('Character %s does not exist!', character_id)
            return

        # Fetch the API data
        params = { 'characterID': character_id }
        if self.fetch_api(url, params) is False or self.root is None:
            return

        # Update character details from the API data
        ship_type_id = self.root.findtext('result/shipTypeID')
        ship_name = self.root.findtext('result/shipName')
        if ship_type_id is not None and ship_type_id.isdigit() and int(ship_type_id) > 0:
            character.details.ship_item_id = ship_type_id
            character.details.ship_name = ship_name or ''
        else:
            character.details.ship_item_id = None
            character.details.ship_name = ''

        character.details.last_known_location = self.root.findtext('result/lastKnownLocation')
        character.details.security_status = self.root.findtext('result/securityStatus')

        # Save the character details
        character.details.save()

        return True

# ---------------------------------------------------------------------------

class NewCharacter(APITask):
    name = 'thing.new_character_info'
    
    def run(self, url, character_id):
        if self.init() is False:
            return
        
        try:
            character = Character.objects.get(pk=character_id)
        except Character.DoesNotExist:
            params = { 'characterID': character_id }
            if self.fetch_api(url, params, False) is False or self.root is None:
                return
            
            corp_id = self.root.findtext('result/corporationID')
            corp_name = self.root.findtext('result/corporation')
            try:
                corporation = Corporation.objects.get(pk=corp_id)
            except Corporation.DoesNotExist:
                corporation = Corporation(
                    id=corp_id,
                    name=corp_name,
                )
                corporation.save()

            character = Character(
                id=int(self.root.findtext('result/characterID')),
                name=self.root.findtext('result/characterName'),
                corporation_id=self.root.findtext('result/corporationID'),
            )
            character.save()
        
        return True