# Copyright 2025 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)

from lino.api import dd, _


assets = dd.plugins.assets


class PartnerAsset(dd.Model):

    class Meta:
        app_label = 'assets'
        verbose_name = assets.asset_name
        verbose_name_plural = assets.asset_name_plural
        abstract = dd.is_abstract_model(__name__, 'PartnerAsset')
        ordering = ["partner", "name"]
        unique_together = ("partner", "name")

    partner = dd.ForeignKey(assets.partner_model, blank=True, null=True)
    name = dd.CharField(assets.asset_name_short, blank=True, max_length=200)

    def __str__(self):
        return self.name


class PartnerAssets(dd.Table):
    model = 'assets.PartnerAsset'
    required_roles = dd.login_required(dd.SiteStaff)
    column_names = 'partner name *'
    # order_by = ["ref", "partner", "designation"]

    insert_layout = """
    name
    """

    # detail_layout = """
    # id name
    # partner
    # """


class AssetsByPartner(PartnerAssets):
    master_key = 'partner'
    column_names = 'name *'
