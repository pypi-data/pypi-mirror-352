# -*- coding: UTF-8 -*-
# Copyright 2025 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)
# Developer docs: https://dev.lino-framework.org/plugins/peppol.html

import requests
import base64
import json
# from lino import logger

# import logging
# logger = logging.getLogger(__name__)


DEMO_SUPPLIER_ID = '273c1bdf-6258-4484-b6fb-74363721d51f'

# def get_cred_settings(cert_dir):
#     if cert_dir.exists():
#         yield ("ibanity", "cert_file", cert_dir / "certificate.pem")
#         yield ("ibanity", "key_file", cert_dir / "decrypted_private_key.pem")
#         credentials = (cert_dir / "credentials.txt").read_text().strip()
#         yield ("ibanity", "credentials", credentials)


root_url = "https://api.ibanity.com/einvoicing"

# client_id = dd.get_plugin_setting("peppol", "client_id", None)
# client_secret = dd.get_plugin_setting("peppol", "client_secret", None)
# cert_file = dd.get_plugin_setting("peppol", "cert_file", None)
# key_file = dd.get_plugin_setting("peppol", "key_file", None)
# credentials = f"{client_id}:{client_secret}"


class PeppolFailure(Warning):

    def __init__(self, request, response, kwargs):
        self.request = request
        self.response = response
        self.kwargs = kwargs
        super().__init__()

    def __str__(self):
        s = f"{self.request} returned "
        s += f"{self.response.status_code} {self.response.text}"
        if self.kwargs:
            s += f" (options were {self.kwargs})"
        return s


class Session:

    def __init__(self, ar, cert_file, key_file, credentials):
        if not cert_file.exists():
            raise Exception(f"Certificate file {cert_file} doesn't exist")
        if not key_file.exists():
            raise Exception(f"Key file {key_file} doesn't exist")
        self.ar = ar
        self.cert_file = cert_file
        self.key_file = key_file
        self.credentials = credentials
        # Create an HTTPS session
        self.session = requests.Session()
        # Attach client certificate and key
        self.session.cert = (self.cert_file, self.key_file)

    def get_response(self, meth_name, url, *args, **kwargs):
        meth = getattr(self.session, meth_name)
        request = f"{meth_name.upper()} {url} {args}"
        try:
            response = meth(url, *args, **kwargs)
        except Exception as e:
            raise Exception(f"{request} failed: {e}")
        if response.status_code not in {200, 201, 202, 400}:
            raise PeppolFailure(request, response, kwargs)
            # logger.warning(msg)
        return response

    def get_json_response(self, *args, **kwargs):
        response = self.get_response(*args, **kwargs)
        self.ar.logger.debug(
            "%s %s --> %s", args, ", ".join([k+"=..." for k in kwargs.keys()]),
            response.text)
        return json.loads(response.text)

    def get_access_token(self):
        # Base64 encode client_id and client_secret for Basic Auth
        creds = base64.b64encode(self.credentials.encode()).decode()
        headers = {
            "Authorization": f"Basic {creds}",
            "Content-Type": "application/x-www-form-urlencoded",  # Required for OAuth2 requests
        }
        url = f"{root_url}/oauth2/token"
        data = {"grant_type": "client_credentials"}
        return self.get_json_response('post', url, data=data, headers=headers)

    def get_xml_headers(self, filename="invoices.xml"):
        headers = self.get_json_headers()
        headers["Content-Type"] = "application/xml"
        headers["Content-Disposition"] = f"inline; filename={filename}"
        return headers

    def get_json_headers(self, accept="application/vnd.api+json"):
        headers = self.get_auth_headers()
        headers["Accept"] = accept
        return headers

    def get_auth_headers(self):
        rv = self.get_access_token()
        access_token = rv['access_token']
        headers = {
            "Authorization": f"Bearer {access_token}"
        }
        return headers

    def list_suppliers(self):
        # Get a list of suppliers
        url = f"{root_url}/suppliers"
        return self.get_json_response('get', url, headers=self.get_json_headers())

    def get_supplier(self, supplier_id):
        url = f"{root_url}/suppliers/{supplier_id}"
        return self.get_json_response('get', url, headers=self.get_json_headers())

    def create_supplier(self, **attributes):
        url = f"{root_url}/suppliers/"
        data = {
            "type": "supplier",
            "attributes": attributes}
        data = {"data": data}
        return self.get_json_response(
            'post', url, json=data, headers=self.get_json_headers())

    def update_supplier(self, supplier_id, **attributes):
        # https://documentation.ibanity.com/einvoicing/1/api/curl#update-supplier
        url = f"{root_url}/suppliers/{supplier_id}"
        data = {"data": {
            "id": supplier_id,
            "type": "supplier",
            "attributes": attributes
        }}
        return self.get_json_response(
            'patch', url, json=data, headers=self.get_json_headers())

    def list_registrations(self, supplier_id):
        url = f"{root_url}/peppol/suppliers/{supplier_id}/registrations"
        return self.get_json_response('get', url, headers=self.get_json_headers())

    def create_outbound_document(self, supplier_id, filename, credit_note=False):
        doc_type = 'credit-notes' if credit_note else 'invoices'
        url = f"{root_url}/peppol/suppliers/{supplier_id}/{doc_type}?"
        headers = self.get_xml_headers(filename.name)
        # data = filename.read_text()
        data = filename.read_bytes()
        return self.get_json_response('post', url, data=data, headers=headers)

    def get_outbound_document(self, supplier_id, doc_id, credit_note=False):
        doc_type = 'credit-notes' if credit_note else 'invoices'
        url = f"{root_url}/peppol/suppliers/{supplier_id}/{doc_type}/{doc_id}"
        return self.get_json_response('get', url, headers=self.get_json_headers())

    def list_outbound_documents(self, supplier_id, fromStatusChanged, **params):
        # fromStatusChanged must be a datetime.datetime instance
        # supported params include fromStatusChanged, toStatusChanged & more
        url = f"{root_url}/peppol/documents"
        params.update(fromStatusChanged=fromStatusChanged.isoformat())
        params.update(supplierId=supplier_id)
        return self.get_json_response(
            'get', url, headers=self.get_json_headers(), params=params)

    def list_inbound_documents(self, supplier_id, **params):
        url = f"{root_url}/peppol/inbound-documents"
        params.update(supplierId=supplier_id)
        return self.get_json_response(
            'get', url, headers=self.get_json_headers(), params=params)

    def get_inbound_document_xml(self, doc_id):
        url = f"{root_url}/peppol/inbound-documents/{doc_id}"
        rsp = self.get_response(
            'get', url, headers=self.get_json_headers("application/xml"))
        return rsp.text

    def get_inbound_document_json(self, doc_id):
        url = f"{root_url}/peppol/inbound-documents/{doc_id}"
        return self.get_json_response(
            'get', url, headers=self.get_json_headers())

    # Customer search. Check whether my customer exists.
    # Belgian participants are registered with the Belgian company number, for which
    # identifier 0208 can be used. Optionally, the customer can be registered with
    # their VAT number, for which identifier 9925 can be used.
    # The Flowin sandbox contains hard-coded fake data.  Using another reference as
    # customerReference will in result a 404
    def customer_search(self, customerReference):
        url = f"{root_url}/peppol/customer-searches"
        data = {
            "type": "peppolCustomerSearch",
            # "id": str(uuid.uuid4()),
            "attributes": {
                "customerReference": customerReference,
                # "supportedDocumentFormats": doc_formats
            }
        }
        data = {"data": data}
        # pprint(data)
        return self.get_json_response('post', url, headers=self.get_json_headers(), json=data)
