# -*- coding: UTF-8 -*-
# Copyright 2025 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)
# Developer docs: https://dev.lino-framework.org/plugins/peppol.html

from django.db import models
from django.contrib.humanize.templatetags.humanize import naturaltime
from lino.api import dd, rt, _, gettext


class PeppolJournal(dd.Model):

    class Meta:
        abstract = True

    if dd.is_installed('peppol'):
        is_outbound = dd.BooleanField(_("Send via Peppol"), default=False)
    else:
        is_outbound = dd.DummyField()


class PeppolPartner(dd.Model):

    class Meta:
        abstract = True

    if dd.is_installed('peppol'):
        send_peppol = dd.BooleanField(_("Send via Peppol"), default=False)
        peppol_id = models.CharField(_("Peppol ID"), max_length=50, blank=True)
    else:
        send_peppol = dd.DummyField()
        peppol_id = dd.DummyField()


class CreateOutbound(dd.Action):
    show_in_toolbar = True
    custom_handler = True
    label = _("Send now")
    # show_in_toolbar = False
    # action_name = "create_outbound"  # because...
    # button_text = _("Send")
    # select_rows = True
    # readonly = True
    # http_method = "POST"

    def run_from_ui(self, ar, **kw):
        # raise Exception("20250414 Hurra!")
        for obj in ar.selected_rows:
            Outbound = rt.models.peppol.OutboundDocument
            odoc = Outbound.objects.filter(voucher=obj).first()
            if odoc is None:
                odoc = Outbound.objects.create(voucher=obj)
                ar.success(_("Outbound document has been created"), refresh_all=True)
            else:
                odoc.resend_document.run_from_ui(ar)
            ar.goto_instance(odoc)


class PeppolSendable(dd.Model):

    class Meta:
        abstract = True

    # peppol_outbound = dd.ForeignKey(
    #     'peppol.OutboundDocument', null=True, blank=True, editable=False)

    if dd.is_installed('peppol'):

        @dd.displayfield(_("Sent"))
        def sent_to_peppol(self, ar):
            if ar is None:
                return ''
            obj = getattr(self, 'peppol_outbound', None)
            if obj is None:
                return ar.instance_action_button(self.create_outbound)
            return ar.obj2html(obj, naturaltime(obj.created_at))

        create_outbound = CreateOutbound()

    else:
        sent_to_peppol = dd.DummyField()
