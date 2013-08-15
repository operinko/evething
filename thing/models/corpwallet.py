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

from django.contrib.auth.models import User
from django.db import models

from thing.models.corporation import Corporation

# ------------------------------------------------------------------------------
# Corporation wallets
class CorpWallet(models.Model):
    account_id = models.IntegerField(primary_key=True)
    corporation = models.ForeignKey(Corporation)
    account_key = models.IntegerField()
    description = models.CharField(max_length=64)
    balance = models.DecimalField(max_digits=18, decimal_places=2)

    class Meta:
        app_label = 'thing'
        ordering = ('corporation', 'account_id')

    def __html__(self):
        if self.corporation.ticker:
            return '[<span class="tip" rel="tooltip" title="%s">%s</span>] %s' % (
                self.corporation.name,
                self.corporation.ticker,
                self.description,
            )
        else:
            return self.__unicode__()

    def __unicode__(self):
        if self.corporation.ticker:
            return '[%s] %s' % (self.corporation.ticker, self.description)
        else:
            return '%s [%s] %s' % (self.corporation.name, self.account_key, self.description)

# ------------------------------------------------------------------------------
