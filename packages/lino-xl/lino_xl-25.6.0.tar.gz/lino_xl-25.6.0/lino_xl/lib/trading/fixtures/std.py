# -*- coding: UTF-8 -*-
# Copyright 2016 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)

from lino.api import dd, rt, _


def objects():

    PaperType = rt.models.trading.PaperType
    bm = rt.models.printing.BuildMethods.get_system_default()
    yield PaperType(template="DefaultLetter" + bm.template_ext,
                    **dd.str2kw('name', _("Letter paper")))
    yield PaperType(template="DefaultBlank" + bm.template_ext,
                    **dd.str2kw('name', _("Blank paper")))
