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

# ------------------------------------------------------------------------------
class SkillPlan(models.Model):
    PRIVATE_VISIBILITY = 1
    PUBLIC_VISIBILITY = 2
    GLOBAL_VISIBILITY = 3
    VISIBILITY_CHOICES = (
        (PRIVATE_VISIBILITY, 'Private'),
        (PUBLIC_VISIBILITY, 'Public'),
        (GLOBAL_VISIBILITY, 'Global'),
    )

    user = models.ForeignKey(User)

    name = models.CharField(max_length=64)
    visibility = models.IntegerField(default=1, choices=VISIBILITY_CHOICES)

    class Meta:
        app_label = 'thing'
        ordering = ('name',)

    def __unicode__(self):
        return '%s - %s' % (self.user.username, self.name)

# ------------------------------------------------------------------------------
