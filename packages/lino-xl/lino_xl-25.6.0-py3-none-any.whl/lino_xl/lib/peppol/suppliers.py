# -*- coding: UTF-8 -*-
# Copyright 2025 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)
# Developer docs: https://dev.lino-framework.org/plugins/peppol.html

# from datetime import datetime
from dateutil.parser import isoparse

from django.utils import timezone
from django.conf import settings
from django.db import models
from lino.api import dd, rt, _
from lino import logger
from lino.mixins import Contactable, Phonable
from lino.modlib.checkdata.choicelists import Checker
# from lino.mixins.periods import DateRange
from lino_xl.lib.accounting.roles import LedgerStaff
from lino_xl.lib.accounting.choicelists import VoucherStates
# from lino_xl.lib.contacts.mixins import ContactRelated
from lino_xl.lib.countries.mixins import AddressLocation
from lino_xl.lib.vat.choicelists import VatSubjectable

# TODO: move babelfilter to lino core.utils.mldbc


def babelfilter(name, value, **kwargs):
    flt = models.Q()
    for k, v in dd.str2kw(name, value).items():
        flt |= models.Q(**{k: v})
    if kwargs:
        flt &= models.Q(**kwargs)
    return flt


with_suppliers = dd.get_plugin_setting("peppol", "with_suppliers", False)
# outbound_model = dd.get_plugin_setting("peppol", "outbound_model", None)
# inbound_model = dd.get_plugin_setting("peppol", "inbound_model", None)
# supplier_id = dd.get_plugin_setting("peppol", "supplier_id", None)

peppol = dd.plugins.peppol


class OnboardingStates(dd.ChoiceList):
    verbose_name = _("Onboarding state")
    verbose_name_plural = _("Onboarding states")
    required_roles = dd.login_required(LedgerStaff)


add = OnboardingStates.add_item
add('10', _("Draft"), 'draft')
add('20', _("Created"), 'created')
add('30', _("Approved"), 'approved')
add('40', _("Rejected"), 'rejected')
add('50', _("Onboarded"), 'onboarded')
add('60', _("Offboarded"), 'offboarded')

# add('10', _("Active"), 'active')
# add('20', _("Potential"), 'potential')
# add('30', _("Unreachable"), 'unreachable')

COMPANY_TO_SUPPLIER = ('vat_id', 'country', 'city', 'zip_code',
                       'street', 'email', 'street_no', 'phone', 'url')

# class Supplier(AddressLocation, ContactRelated, Contactable, Phonable):


class Supplier(AddressLocation, Contactable, Phonable):

    class Meta:
        app_label = 'peppol'
        verbose_name = _("Ibanity supplier")
        verbose_name_plural = _("Ibanity suppliers")

    quickfix_checkdata_label = _("Sync to Ibanity")
    # preferred_foreignkey_width = 10

    supplier_id = models.CharField(_("Supplier ID"), max_length=50, blank=True)
    company = dd.ForeignKey(
        "contacts.Company",
        related_name="peppol_suppliers_by_company",
        verbose_name=_("Organization"),
        blank=True, null=True)
    names = models.CharField(_('Names'), max_length=200, blank=True)
    ibans = models.CharField(_('IBANs'), max_length=200, blank=True)
    vat_id = models.CharField(_("VAT id"), max_length=200, blank=True)
    onboarding_state = OnboardingStates.field(default='draft')
    peppol_receiver = models.BooleanField(_("Peppol receiver"), default=False)
    last_sync = models.DateTimeField(_("Last sync"), editable=False, null=True)

    @classmethod
    def get_simple_parameters(cls):
        yield super().get_simple_parameters()
        yield "onboarding_state"

    def full_clean(self):
        if not self.supplier_id and self.company_id:
            if not self.names:
                self.names = self.company.name
            if not self.ibans:
                Account = rt.models.sepa.Account
                qs = Account.objects.filter(partner=self.company, primary=True)
                self.ibans = "; ".join([o.iban for o in qs])
            for k in COMPANY_TO_SUPPLIER:
                if not getattr(self, k):
                    setattr(self, k, getattr(self.company, k))
        if self.vat_id and self.country_id:
            mod = self.country.get_stdnum_module("vat")
            self.vat_id = self.country.isocode + mod.compact(self.vat_id)
        super().full_clean()

    def create_supplier_data(self):
        d = {}
        d["enterpriseIdentification"] = {
            "enterpriseNumber": self.vat_id[2:],
            "vatNumber": self.vat_id}
        d["contactEmail"] = self.email
        d["names"] = [{"value": name.strip()} for name in self.names.split(";")]
        d["ibans"] = [{"value": i.strip()} for i in self.ibans.split(";")]
        d["city"] = str(self.city)
        d["country"] = str(self.country)
        if self.url:
            d["homepage"] = self.url
        d["phoneNumber"] = self.phone
        d["street"] = self.street
        d["streetNumber"] = self.street_no
        d["email"] = self.email
        if (site_company := settings.SITE.site_config.site_company):
            d["supportEmail"] = site_company.email
            d["supportPhone"] = site_company.phone
            d["supportUrl"] = site_company.url
        d["zip"] = self.zip_code
        d["peppolReceiver"] = self.peppol_receiver
        return d


class SupplierDetail(dd.DetailLayout):
    main = """
    supplier_id company id
    vat_id names
    peppol_receiver onboarding_state last_sync
    ibans
    country region city
    zip_code street street_no
    email phone url
    checkdata.MessagesByOwner
    """


class Suppliers(dd.Table):
    required_roles = dd.login_required(LedgerStaff)
    model = "peppol.Supplier"
    column_names = "supplier_id company names vat_id onboarding_state last_sync *"
    insert_layout = """
    company
    supplier_id
    """
    detail_layout = "peppol.SupplierDetail"


class SuppliersListChecker(Checker):
    verbose_name = _("Check for missing or invalid suppliers")
    model = None

    def get_checkdata_problems(self, ar, obj, fix=False):
        if not peppol.credentials:
            logger.info("No Ibanity credentials")
            return

        existing = [o.supplier_id for o in
                    Supplier.objects.exclude(supplier_id='')]

        ses = peppol.get_ibanity_session(ar)
        for sup_info in ses.list_suppliers()['data']:
            if sup_info['type'] != "supplier":
                logger.info("Invalid supplier type '%s'", sup_info['type'])
                continue
            sup_id = sup_info['id']
            if sup_id in existing:
                existing.remove(sup_id)
                continue
            else:
                yield True, _("No entry for {sup_id}.").format(sup_id=sup_id)
                if fix:
                    sup = Supplier(supplier_id=sup_id)
                    sup.full_clean()
                    sup.save()
                    rt.models.checkdata.check_instance(ar, sup, fix=True)
        for sup_id in existing:
            yield False, _("Supplier {} doesn't exist on Ibanity.").format(sup_id)


# if peppol.credentials:
SuppliersListChecker.activate(no_auto=True)


REMOVE = "/data/attributes/"


def format_errors(errors):
    parts = []
    for e in errors:
        if e['code'] == 'validationError':
            fld = e['source']['pointer']
            if fld.startswith(REMOVE):
                fld = fld[len(REMOVE):]
            parts.append(f"{fld}: {e['detail']}")
        else:
            parts.append(str(e))
    msg = ", ".join(parts)
    return _("Failed to create supplier: {}").format(msg)


def update_id_list(oldlist, value, sep=";"):
    """
    Return a list of dicts to send to Ibanity API in order to update
    the fields :attr:`names` and :attr:`ibans`.

    - `value` is the current Lino value, a string containing one or more names
      or ibans separated by `sep`.

    - `oldlist` is the list returned by get_supplier()

    Each item of oldlist is a list of `{'id': x, 'value': y }`.

    """
    newlist = []
    values = {v.strip() for v in value.split(sep) if v}
    for item in oldlist:
        if (v := item['value']) in values:
            newlist.append(item)
            values.remove(v)
    for v in values:
        newlist.append({'value': v})
    newlist.sort(key=lambda x: x['value'])
    return newlist


class SupplierChecker(Checker):
    verbose_name = _("Check for differences between our copy and Ibanity")
    model = Supplier
    msg_needs_update = _("Some fields need update: {changed}")

    def get_checkdata_problems(self, ar, obj, fix=False):

        if obj.company:
            ctx = dict(
                model=rt.models.contacts.Company._meta.verbose_name, obj=obj)
            if obj.company.name not in obj.names:
                msg = _("{model} name {obj.company.name} missing in supplier names")
                yield (False, msg.format(**ctx))

            mod = obj.country.get_stdnum_module("vat")
            if mod.compact(obj.company.vat_id) != obj.vat_id:
                msg = _("{model} VAT id {obj.company.vat_id} ≠ {obj.vat_id}")
                yield (False, msg.format(**ctx))

        if not peppol.credentials:
            ar.logger.info("No Ibanity credentials")
            return

        Country = rt.models.countries.Country
        Place = rt.models.countries.Place

        def save():
            obj.last_sync = dd.now()
            obj.full_clean()
            obj.save()

        ses = peppol.get_ibanity_session(ar)

        if obj.supplier_id:
            sup_info = ses.get_supplier(obj.supplier_id)
            sup_id = sup_info['data']['id']
            if sup_id != obj.supplier_id:
                yield False, _("Supplier {} doesn't exist on Ibanity.").format(sup_id)
                save()
                return
        elif not obj.company_id:
            yield True, _("Dangling supplier row should get deleted")
            if fix:
                obj.delete()
            return
        if obj.company and not (obj.names and obj.vat_id):
            yield True, _("Must fill supplier from company")
            if fix:
                obj.vat_id = obj.company.vat_id
                obj.names = obj.company.name
                save()
            else:
                return
        if not obj.supplier_id:
            yield True, _("Must create supplier on Ibanity")
            if fix:
                data = obj.create_supplier_data()
                sup_info = ses.create_supplier(**data)
                if (errors := sup_info.get('errors', None)):
                    yield False, format_errors(errors)
                    return
                sup_id = sup_info['data']['id']
                obj.supplier_id = sup_id
                save()
            else:
                return

        assert sup_info

        # Synchronize supplier data between Ibanity and our data

        attrs = sup_info['data']['attributes']
        p2l = dict()  # Peppol to Lino
        l2p = dict()  # Lino to Peppol

        if obj.peppol_receiver != attrs['peppolReceiver']:
            l2p['peppolReceiver'] = obj.peppol_receiver
        if obj.street != attrs['street']:
            l2p['street'] = obj.street
        if obj.street_no != attrs['streetNumber']:
            l2p['streetNumber'] = obj.street_no
        if obj.phone != attrs['phoneNumber']:
            l2p['phoneNumber'] = obj.phone
        if obj.email != attrs['email']:
            l2p['email'] = obj.email
        if obj.zip_code != attrs['zip']:
            l2p['zip'] = obj.zip_code
        if obj.url != attrs['homepage']:
            l2p['homepage'] = obj.url

        p2l['onboarding_state'] = OnboardingStates.get_by_name(
            attrs['onboardingStatus'].lower())
        if obj.names:
            l2p['names'] = update_id_list(attrs['names'], obj.names)
        else:
            p2l['names'] = "; ".join([i['value'] for i in attrs['names']])
        if obj.ibans:
            l2p['ibans'] = update_id_list(attrs['ibans'], obj.ibans)
        else:
            p2l['ibans'] = "; ".join([i['value'] for i in attrs['ibans']])

        if obj.country_id:
            l2p['country'] = str(obj.country)
        else:
            try:
                country = Country.objects.get(babelfilter('name', attrs['country']))
            except Country.DoesNotExist:
                yield (False, _("Unknown country {country}").format(**attrs))
            else:
                p2l['country'] = country

        if obj.vat_id != attrs['enterpriseIdentification']['vatNumber']:
            p2l['vat_id'] = attrs['enterpriseIdentification']['vatNumber']

        if obj.city_id:
            l2p['city'] = str(obj.city)
        else:
            try:
                city = Place.objects.get(
                    babelfilter('name', attrs['city'], country=country))
            except Place.DoesNotExist:
                yield (True, _("Unknown city {city} ((in {country})").format(**attrs))
                if fix:
                    city = Place(name=attrs['city'], country=country)
                    city.full_clean()
                    city.save()
                    p2l['city'] = city
            else:
                p2l['city'] = city

        changed = []
        for k, v in p2l.items():
            if getattr(obj, k) != v:
                changed.append(k)
        changed.sort()
        if len(changed):
            msg = self.msg_needs_update.format(changed=", ".join(changed))
            yield (True, msg)
            if fix:
                for k in changed:
                    setattr(obj, k, p2l[k])

        if len(l2p):
            ses.update_supplier(obj.supplier_id, **l2p)

        # We call save() even when there are no changes because we want
        # last_sync to reflect each online check.
        save()

# On a site without Ibanity credentials we don't need to activate this
# checker. SupplierChecker.activate() sets no_auto to True because we do not
# want this checker to run automatically (i.e. during checkdata). It should
# run only when called manually because it requires Ibanity credentials,
# which are not available e.g. on GitLab.


# if peppol.credentials:
SupplierChecker.activate(no_auto=True)
