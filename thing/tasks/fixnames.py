# ------------------------------------------------------------------------------
# Copyright (c) 2010-2013, EVEthing team
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification,
# are permitted provided that the following conditions are met:
#
#     Redistributions of source code must retain the above copyright notice, this
#       list of conditions and the following disclaimer.
#     Redistributions in binary form must reproduce the above copyright notice,
#       this list of conditions and the following disclaimer in the documentation
#       and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.
# IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT,
# INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT
# NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
# PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
# WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY
# OF SUCH DAMAGE.
# ------------------------------------------------------------------------------

from .apitask import APITask

from thing.models import Character, Corporation

# ---------------------------------------------------------------------------
# Periodic task to try to fix *UNKNOWN* Character objects
CHAR_NAME_URL = '/eve/CharacterName.xml.aspx'
CORP_SHEET_URL = '/corp/CorporationSheet.xml.aspx'

class FixNames(APITask):
    name = 'thing.fix_names'

    def run(self):
        self.init()

        # Fetch all unknown Character objects
        char_map = {}
        for char in Character.objects.filter(name='*UNKNOWN*'):
            char_map[char.id] = char

        # Fetch all unknown Corporation objects
        corp_map = {}
        for corp in Corporation.objects.filter(name='*UNKNOWN*'):
            corp_map[corp.id] = corp

        ids = list(set(char_map.keys()) | set(corp_map.keys()))
        if len(ids) == 0:
            return

        # Go fetch names for them
        name_map = {}
        for i in range(0, len(ids), 100):
            params = { 'ids': ','.join(map(str, ids[i:i+100])) }

            if self.fetch_api(CHAR_NAME_URL, params, use_auth=False) is False or self.root is None:
                return False

            # <row name="Tazuki Falorn" characterID="1759080617"/>
            for row in self.root.findall('result/rowset/row'):
                name_map[int(row.attrib['characterID'])] = row.attrib['name']

        if len(name_map) == 0:
            return

        # Fix corporation names first
        for id, corp in corp_map.items():
            corp_name = name_map.get(id)
            if corp_name is not None:
                corp.name = corp_name
                corp.save()
                del name_map[id]

        # Fix character names
        for id, name in name_map.items():
            char = char_map.get(id)
            if char is not None:
                char.name = name
                char.save()

        # # Ugh, now go look up all of the damn names just in case they're corporations
        # new_corps = []
        # for id, name in name_map.items():
        #     params = { 'corporationID': id }

        #     # Not a corporation, update the Character object
        #     if self.fetch_api(CORP_SHEET_URL, params, use_auth=False) is False or self.root is None:
        #         char = char_map.get(id)
        #         char.name = name
        #         char.save()
        #     else:
        #         new_corps.append(Corporation(
        #             id=id,
        #             name=name,
        #             ticker=self.root.find('result/ticker').text,
        #         ))

        # Now we can create the new corporation objects
        #corp_map = Corporation.objects.in_bulk([c.id for c in new_corps])
        #new_corps = [c for c in new_corps if c.id not in corp_map]
        #Corporation.objects.bulk_create(new_corps)

        # And finally delete any characters that have equivalent corporations now
        cursor = self.get_cursor()
        cursor.execute('DELETE FROM thing_character WHERE id IN (SELECT id FROM thing_corporation)')
        cursor.close()

        return True
