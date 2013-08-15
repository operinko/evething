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

import datetime

from decimal import *

from celery.execute import send_task

from .apitask import APITask
from thing import queries
from thing.models import APIKey, Asset, AssetSummary, Character, InventoryFlag, Item, Station, System

# ---------------------------------------------------------------------------

class AssetList(APITask):
    name = 'thing.asset_list'

    def run(self, url, taskstate_id, apikey_id, character_id):
        if self.init(taskstate_id, apikey_id) is False:
            return

        # Make sure the character exists
        try:
            character = Character.objects.select_related('details').get(pk=character_id)
        except Character.DoesNotExist:
            self.log_warn('Character %s does not exist!', character_id)
            return

        # Initialise for corporate query
        if self.apikey.corp_character:
            a_filter = Asset.objects.filter(character=character, corporation_id=self.apikey.corp_character.corporation.id)
        # Initialise for character query
        else:
            a_filter = Asset.objects.filter(character=character, corporation_id=0)

        # Fetch the API data
        params = { 'characterID': character.id }
        if self.fetch_api(url, params) is False or self.root is None:
            return

        # ACTIVATE RECURSION :siren:
        data = {
            'assets': [],
            'locations': set(),
            'items': set(),
            'flags': set(),
        }
        self._find_assets(data, self.root.find('result/rowset'))

        # Bulk query data
        item_map = Item.objects.select_related('item_group__category').in_bulk(data['items'])
        station_map = Station.objects.select_related('system').in_bulk(data['locations'])
        system_map = System.objects.in_bulk(data['locations'])
        flag_map = InventoryFlag.objects.in_bulk(data['flags'])

        # Corporation ID
        if self.apikey.corp_character:
            corporation_id = self.apikey.corp_character.corporation.id
        else:
            corporation_id = 0

        # Build new Asset objects for each row
        assets = []
        totals = {}
        for asset_id, location_id, parent_id, item_id, flag_id, quantity, rawQuantity, singleton in data['assets']:
            system = system_map.get(location_id)
            station = station_map.get(location_id)
            if system is None:
                system = station.system

            if (system, station) not in totals:
                totals[(system, station)] = dict(items=0, volume=0, value=0)

            item = item_map.get(item_id)
            if item is None:
                self.log_warn('Invalid item_id %s', item_id)
                continue

            inv_flag = flag_map.get(flag_id)
            if inv_flag is None:
                self.log_warn('Invalid flag_id %s', flag_id)
                continue

            asset = Asset(
                asset_id=asset_id,
                parent=parent_id,
                character=character,
                corporation_id=corporation_id,
                system=system,
                station=station,
                item=item,
                inv_flag=inv_flag,
                quantity=quantity,
                raw_quantity=rawQuantity,
                singleton=singleton,
            )
            assets.append(asset)

            # Update totals
            totals[(system, station)]['items'] += quantity
            totals[(system, station)]['volume'] += quantity * item.volume
            totals[(system, station)]['value'] += quantity * asset.get_sell_price()

        # Create summary objects
        summaries = []
        for (system, station), data in totals.items():
            summary = AssetSummary(
                character=character,
                system=system,
                station=station,
                total_items=data['items'],
                total_value=data['value'],
                total_volume=data['volume'],
            )
            if self.apikey.corp_character:
                summary.corporation_id = self.apikey.corp_character.corporation.id

            summaries.append(summary)

        # Delete existing assets, it's way too painful trying to deal with changes
        cursor = self.get_cursor()
        if self.apikey.corp_character:
            cursor.execute(queries.asset_delete_corp, [self.apikey.corp_character.corporation.id])
            cursor.execute(queries.assetsummary_delete_corp, [self.apikey.corp_character.corporation.id])
        else:
            cursor.execute(queries.asset_delete_char, [character_id])
            cursor.execute(queries.assetsummary_delete_char, [character_id])

        # Bulk insert new assets
        Asset.objects.bulk_create(assets)
        AssetSummary.objects.bulk_create(summaries)

        # Clean up
        cursor.close()

        # Fetch names (via Locations API) for assets
        if self.apikey.corp_character is None and APIKey.CHAR_LOCATIONS_MASK in self.apikey.get_masks():
            a_filter = a_filter.filter(
                singleton=True,
                item__item_group__category__name='Ship'
            )

            for asset in a_filter:
                send_task(
                    'thing.locations',
                    args=(apikey_id, character_id, asset.asset_id),
                    kwargs={},
                    queue='et_medium',
                )

        return True

    # Recursively visit the assets tree and gather data
    def _find_assets(self, data, rowset, location_id=0, parent_id=0):
        for row in rowset.findall('row'):
            # No container_id (parent)
            if 'locationID' in row.attrib:
                location_id = int(row.attrib['locationID'])

                # :ccp: as fuck
                # http://wiki.eve-id.net/APIv2_Corp_AssetList_XML#officeID_to_stationID_conversion
                if 66000000 <= location_id <= 66014933:
                    location_id -= 6000001
                elif 66014934 <= location_id <= 67999999:
                    location_id -= 6000000

                data['locations'].add(location_id)

            asset_id = int(row.attrib['itemID'])

            item_id = int(row.attrib['typeID'])
            data['items'].add(item_id)

            flag_id = int(row.attrib['flag'])
            data['flags'].add(flag_id)

            data['assets'].append([
                asset_id,
                location_id,
                parent_id,
                item_id,
                flag_id,
                int(row.attrib.get('quantity', '0')),
                int(row.attrib.get('rawQuantity', '0')),
                int(row.attrib.get('singleton', '0')),
            ])

            # Now we need to recurse into children rowsets
            for rowset in row.findall('rowset'):
                self._find_assets(data, rowset, location_id, asset_id)

# ---------------------------------------------------------------------------
