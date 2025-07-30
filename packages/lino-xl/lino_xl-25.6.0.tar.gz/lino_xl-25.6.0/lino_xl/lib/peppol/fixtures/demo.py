# -*- coding: UTF-8 -*-
# Copyright 2025 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)

from lino.api import dd, rt, _
from lino_xl.lib.accounting.choicelists import JournalGroups
from lino_xl.lib.accounting.utils import DC, ZERO


def objects():
    if dd.plugins.peppol.supplier_id:
        qs = rt.models.contacts.Company.objects.exclude(
            vat_id="").filter(country__isocode="BE")
        qs.update(send_peppol=True)
        jnl = rt.models.accounting.Journal.get_by_ref("SLS")
        jnl.is_outbound = True
        yield jnl

        kw = dict()
        kw.update(journal_group=JournalGroups.purchases)
        kw.update(trade_type='purchases',
                  ref=dd.plugins.peppol.inbound_journal)
        kw.update(dd.str2kw('name', _("Inbound documents")))
        kw.update(dd.str2kw('printed_name', _("Invoice")))
        kw.update(dc=DC.debit)
        yield rt.models.peppol.ReceivedInvoicesByJournal.create_journal(**kw)
