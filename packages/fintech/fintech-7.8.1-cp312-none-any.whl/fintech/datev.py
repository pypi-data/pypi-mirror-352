
###########################################################################
#
# LICENSE AGREEMENT
#
# Copyright (c) 2014-2024 joonis new media, Thimo Kraemer
#
# 1. Recitals
#
# joonis new media, Inh. Thimo Kraemer ("Licensor"), provides you
# ("Licensee") the program "PyFinTech" and associated documentation files
# (collectively, the "Software"). The Software is protected by German
# copyright laws and international treaties.
#
# 2. Public License
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this Software, to install and use the Software, copy, publish
# and distribute copies of the Software at any time, provided that this
# License Agreement is included in all copies or substantial portions of
# the Software, subject to the terms and conditions hereinafter set forth.
#
# 3. Temporary Multi-User/Multi-CPU License
#
# Licensor hereby grants to Licensee a temporary, non-exclusive license to
# install and use this Software according to the purpose agreed on up to
# an unlimited number of computers in its possession, subject to the terms
# and conditions hereinafter set forth. As consideration for this temporary
# license to use the Software granted to Licensee herein, Licensee shall
# pay to Licensor the agreed license fee.
#
# 4. Restrictions
#
# You may not use this Software in a way other than allowed in this
# license. You may not:
#
# - modify or adapt the Software or merge it into another program,
# - reverse engineer, disassemble, decompile or make any attempt to
#   discover the source code of the Software,
# - sublicense, rent, lease or lend any portion of the Software,
# - publish or distribute the associated license keycode.
#
# 5. Warranty and Remedy
#
# To the extent permitted by law, THE SOFTWARE IS PROVIDED "AS IS",
# WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT
# LIMITED TO THE WARRANTIES OF QUALITY, TITLE, NONINFRINGEMENT,
# MERCHANTABILITY OR FITNESS FOR A PARTICULAR PURPOSE, regardless of
# whether Licensor knows or had reason to know of Licensee particular
# needs. No employee, agent, or distributor of Licensor is authorized
# to modify this warranty, nor to make any additional warranties.
#
# IN NO EVENT WILL LICENSOR BE LIABLE TO LICENSEE FOR ANY DAMAGES,
# INCLUDING ANY LOST PROFITS, LOST SAVINGS, OR OTHER INCIDENTAL OR
# CONSEQUENTIAL DAMAGES ARISING FROM THE USE OR THE INABILITY TO USE THE
# SOFTWARE, EVEN IF LICENSOR OR AN AUTHORIZED DEALER OR DISTRIBUTOR HAS
# BEEN ADVISED OF THE POSSIBILITY OF THESE DAMAGES, OR FOR ANY CLAIM BY
# ANY OTHER PARTY. This does not apply if liability is mandatory due to
# intent or gross negligence.


"""
DATEV module of the Python Fintech package.

This module defines functions and classes
to create DATEV data exchange files.
"""

__all__ = ['DatevCSV', 'DatevKNE']

class DatevCSV:
    """DatevCSV format class"""

    def __init__(self, adviser_id, client_id, account_length=4, currency='EUR', initials=None, version=510, first_month=1):
        """
        Initializes the DatevCSV instance.

        :param adviser_id: DATEV number of the accountant
            (Beraternummer). A numeric value up to 7 digits.
        :param client_id: DATEV number of the client
            (Mandantennummer). A numeric value up to 5 digits.
        :param account_length: Length of G/L account numbers
            (Sachkonten). Therefore subledger account numbers
            (Personenkonten) are one digit longer. It must be
            a value between 4 (default) and 8.
        :param currency: Currency code (Währungskennzeichen)
        :param initials: Initials of the creator (Namenskürzel)
        :param version: Version of DATEV format (eg. 510, 710)
        :param first_month: First month of financial year (*new in v6.4.1*).
        """
        ...

    @property
    def adviser_id(self):
        """DATEV adviser number (read-only)"""
        ...

    @property
    def client_id(self):
        """DATEV client number (read-only)"""
        ...

    @property
    def account_length(self):
        """Length of G/L account numbers (read-only)"""
        ...

    @property
    def currency(self):
        """Base currency (read-only)"""
        ...

    @property
    def initials(self):
        """Initials of the creator (read-only)"""
        ...

    @property
    def version(self):
        """Version of DATEV format (read-only)"""
        ...

    @property
    def first_month(self):
        """First month of financial year (read-only)"""
        ...

    def add_entity(self, account, name, street=None, postcode=None, city=None, country=None, vat_id=None, customer_id=None, tag=None, other=None):
        """
        Adds a new debtor or creditor entity.

        There are a huge number of possible fields to set. Only
        the most important fields can be set directly by the
        available parameters. Additional fields must be set
        by using the parameter *other*.

        Fields that can be set directly
        (targeted DATEV field names in square brackets):

        :param account: Account number [Konto]
        :param name: Name [Name (Adressatentyp keine Angabe)]
        :param street: Street [Straße]
        :param postcode: Postal code [Postleitzahl]
        :param city: City [Ort]
        :param country: Country code, ISO-3166 [Land]
        :param vat_id: VAT-ID [EU-Land]+[EU-USt-IdNr.]
        :param customer_id: Customer ID [Kundennummer]
        :param tag: Short description of the dataset. Also used
            in the final file name. Defaults to "Stammdaten".
        :param other: An optional dictionary with extra fields.
            Note that the method arguments take precedence over
            the field values in this dictionary. For possible
            field names and type declarations see
            `DATEV documentation <https://www.datev.de/dnlexom/client/app/index.html#/document/1003221/D18014404834105739>`_.
        """
        ...

    def add_accounting(self, debitaccount, creditaccount, amount, date, reference=None, postingtext=None, vat_id=None, tag=None, other=None):
        """
        Adds a new accounting record.

        Each record is added to a DATEV data file, grouped by a
        combination of *tag* name and the corresponding financial
        year.

        There are a huge number of possible fields to set. Only
        the most important fields can be set directly by the
        available parameters. Additional fields must be set
        by using the parameter *other*.

        Fields that can be set directly
        (targeted DATEV field names in square brackets):

        :param debitaccount: The debit account [Konto]
        :param creditaccount: The credit account
            [Gegenkonto (ohne BU-Schlüssel)]
        :param amount: The posting amount with not more than
            two decimals.
            [Umsatz (ohne Soll/Haben-Kz)]+[Soll/Haben-Kennzeichen]
        :param date: The booking date. Must be a date object or
            an ISO8601 formatted string [Belegdatum]
        :param reference: Usually the invoice number [Belegfeld 1]
        :param postingtext: The posting text [Buchungstext]
        :param vat_id: The VAT-ID [EU-Land u. USt-IdNr.]
        :param tag: Short description of the dataset. Also used
            in the final file name. Defaults to "Bewegungsdaten".
        :param other: An optional dictionary with extra fields.
            Note that the method arguments take precedence over
            the field values in this dictionary. For possible
            field names and type declarations see
            `DATEV documentation <https://www.datev.de/dnlexom/client/app/index.html#/document/1003221/D36028803343536651>`_.
    
        """
        ...

    def as_dict(self):
        """
        Generates the DATEV files and returns them as a dictionary.

        The keys represent the file names and the values the
        corresponding file data as bytes.
        """
        ...

    def save(self, path):
        """
        Generates and saves all DATEV files.

        :param path: If *path* ends with the extension *.zip*, all files are
            stored in this archive. Otherwise the files are saved in a folder.
        """
        ...


class DatevKNE:
    """
    The DatevKNE class (Postversanddateien)

    *This format is obsolete and not longer accepted by DATEV*.
    """

    def __init__(self, adviserid, advisername, clientid, dfv='', kne=4, mediumid=1, password=''):
        """
        Initializes the DatevKNE instance.

        :param adviserid: DATEV number of the accountant (Beraternummer).
            A numeric value up to 7 digits.
        :param advisername: DATEV name of the accountant (Beratername).
            An alpha-numeric value up to 9 characters.
        :param clientid: DATEV number of the client (Mandantennummer).
            A numeric value up to 5 digits.
        :param dfv: The DFV label (DFV-Kennzeichen). Usually the initials
            of the client name (2 characters).
        :param kne: Length of G/L account numbers (Sachkonten). Therefore
            subledger account numbers (Personenkonten) are one digit longer.
            It must be a value between 4 (default) and 8.
        :param mediumid: The medium id up to 3 digits.
        :param password: The password registered at DATEV, usually unused.
        """
        ...

    @property
    def adviserid(self):
        """Datev adviser number (read-only)"""
        ...

    @property
    def advisername(self):
        """Datev adviser name (read-only)"""
        ...

    @property
    def clientid(self):
        """Datev client number (read-only)"""
        ...

    @property
    def dfv(self):
        """Datev DFV label (read-only)"""
        ...

    @property
    def kne(self):
        """Length of accounting numbers (read-only)"""
        ...

    @property
    def mediumid(self):
        """Data medium id (read-only)"""
        ...

    @property
    def password(self):
        """Datev password (read-only)"""
        ...

    def add(self, inputinfo='', accountingno=None, **data):
        """
        Adds a new accounting entry.

        Each entry is added to a DATEV data file, grouped by a combination
        of *inputinfo*, *accountingno*, year of booking date and entry type.

        :param inputinfo: Some information string about the passed entry.
            For each different value of *inputinfo* a new file is generated.
            It can be an alpha-numeric value up to 16 characters (optional).
        :param accountingno: The accounting number (Abrechnungsnummer) this
            entry is assigned to. For accounting records it can be an integer
            between 1 and 69 (default is 1), for debtor and creditor core
            data it is set to 189.

        Fields for accounting entries:

        :param debitaccount: The debit account (Sollkonto) **mandatory**
        :param creditaccount: The credit account (Gegen-/Habenkonto) **mandatory**
        :param amount: The posting amount **mandatory**
        :param date: The booking date. Must be a date object or an
            ISO8601 formatted string. **mandatory**
        :param voucherfield1: Usually the invoice number (Belegfeld1) [12]
        :param voucherfield2: The due date in form of DDMMYY or the
            payment term id, mostly unused (Belegfeld2) [12]
        :param postingtext: The posting text. Usually the debtor/creditor
            name (Buchungstext) [30]
        :param accountingkey: DATEV accounting key consisting of
            adjustment key and tax key.
    
            Adjustment keys (Berichtigungsschlüssel):
    
            - 1: Steuerschlüssel bei Buchungen mit EU-Tatbestand
            - 2: Generalumkehr
            - 3: Generalumkehr bei aufzuteilender Vorsteuer
            - 4: Aufhebung der Automatik
            - 5: Individueller Umsatzsteuerschlüssel
            - 6: Generalumkehr bei Buchungen mit EU-Tatbestand
            - 7: Generalumkehr bei individuellem Umsatzsteuerschlüssel
            - 8: Generalumkehr bei Aufhebung der Automatik
            - 9: Aufzuteilende Vorsteuer
    
            Tax keys (Steuerschlüssel):
    
            - 1: Umsatzsteuerfrei (mit Vorsteuerabzug)
            - 2: Umsatzsteuer 7%
            - 3: Umsatzsteuer 19%
            - 4: n/a
            - 5: Umsatzsteuer 16%
            - 6: n/a
            - 7: Vorsteuer 16%
            - 8: Vorsteuer 7%
            - 9: Vorsteuer 19%

        :param discount: Discount for early payment (Skonto)
        :param costcenter1: Cost center 1 (Kostenstelle 1) [8]
        :param costcenter2: Cost center 2 (Kostenstelle 2) [8]
        :param vatid: The VAT-ID (USt-ID) [15]
        :param eutaxrate: The EU tax rate (EU-Steuersatz)
        :param currency: Currency, default is EUR (Währung) [4]
        :param exchangerate: Currency exchange rate (Währungskurs)

        Fields for debtor and creditor core data:

        :param account: Account number **mandatory**
        :param name1: Name1 [20] **mandatory**
        :param name2: Name2 [20]
        :param customerid: The customer id [15]
        :param title: Title [1]

            - 1: Herrn/Frau/Frl./Firma
            - 2: Herrn
            - 3: Frau
            - 4: Frl.
            - 5: Firma
            - 6: Eheleute
            - 7: Herrn und Frau

        :param street: Street [36]
        :param postbox: Post office box [10]
        :param postcode: Postal code [10]
        :param city: City [30]
        :param country: Country code, ISO-3166 [2]
        :param phone: Phone [20]
        :param fax: Fax [20]
        :param email: Email [60]
        :param vatid: VAT-ID [15]
        :param bankname: Bank name [27]
        :param bankaccount: Bank account number [10]
        :param bankcode: Bank code [8]
        :param iban: IBAN [34]
        :param bic: BIC [11]
        """
        ...

    def as_dict(self):
        """
        Generates the DATEV files and returns them as a dictionary.

        The keys represent the file names and the values the
        corresponding file data as bytes.
        """
        ...

    def save(self, path):
        """
        Generates and saves all DATEV files.

        :param path: If *path* ends with the extension *.zip*, all files are
            stored in this archive. Otherwise the files are saved in a folder.
        """
        ...



from typing import TYPE_CHECKING
if not TYPE_CHECKING:
    import marshal, zlib, base64
    exec(marshal.loads(zlib.decompress(base64.b64decode(
        b'eJzsvQlcVNfZMH5nB4ZVhn3xIusAM+w7GkFFdkRwQw0MzACjw+IsLiSu0TCIKLgBLgGiUVATUWM0bjHntM3SDcRUpDY1bfq1SdvUJGZp+rb9n3PuDNyRwWjb932//+/3'
        b'kXjn3Ocs9yzPebbznHN+S7H+eKbfL1ehRyelpMqoGqqMo+Rsp8q4Kt4qW2rSn5J7msOEtLZKHpdSCU6bYtZSOtvlXAQRKvnmNNs46F2kGs/DoTYIbGukwu822s3NKJ23'
        b'mK5rUBo0KrqhmtbXqugFG/S1DfV0lrper6qqpRsVVasVNSq5nV1prVpnTqtUVavrVTq62lBfpVc31OtoRb2SrtIodDqVzk7fQFdpVQq9imY+oFToFbRqfVWtor5GRVer'
        b'NSqd3K7Kl9UiP/RPjDvhJ+jRTDVzmrnNvGZ+s6BZ2Cxqtmm2bbZrFjfbNzs0OzY7NTs3uzRPa3ZtljS7Nbs3ezR7Nns1ezf7NPt2UkYfo4dxmtHGKDI6GPlGJ6Od0dVo'
        b'b7Q1uhkpI8/obJQYBUZHo5fR3Sg2ehqFRq6RY/Q2+hpdqv1Ql9ts9ONSLT7m7tzob0txqef9zO8o7G8Oc6hNfpv8S6hAK9B11HreMmodx7ZWyi2sYg+dN/rnihvKJ6O9'
        b'gZLaFWpsUNg9hUvxl/YIKKpCszhvM2UIREBwYuN02ApbivKLoRG2FUlhW86iBTIhFTrPZw4fvgXOpEg5Blxm3np4XJdTAHfDXQVwF4eyy+HCXTPA4Ao7KdfghhIsWRaQ'
        b'lxOZI6D4fDgo5IAeeBJcM/ijGNgG9oJWHAn7wBYZbEFFCChHuJNXCHfaouw+KJEgGnSBVrgzshHVZxcqxg5c4EbJweulCsMMXMgAPFCOEpy3B8Z1awzwwhr7NQYO5QH3'
        b'wEEPHthlJ0AVDUAJnSg5aAV7cpyi8mThuLpwD34XUT5BfPACDS9UcVjd5WPurr3occC7GXUZGkU+GkMKjZ0IjbMtGmExGmEHNKpOaHxd0Oi7olF2QyPsgUbYC42uj9G3'
        b'2oeMLpoKLaLx0eWS0eWwRpfLGkfOJq5pdB+Bjo9uzaOj6zFpdP2Y0f2wSETZZ3tyKLoiUr0hmyLAw7loyGcHIwJQkQ/yFzPA6xtsKOf4bxGswn56sJwBCr0FlM2KD0XU'
        b'7Ar7xZxF1AClsUPgVKUn/2FIDsKUj0K/4L4RM7KCS2kwvXiJ7uIMiig62qve68ukyJhbDPh51RdO+504YQ+ozfmrpx1dJaXGKEM0xrPD8Dg4gUa2NWoJ7CwOC4M7o7Jl'
        b'cCcYKA3LLYB7IuU5stwCDlXvZDsT3IAvWIyR2NxoLR4jsWmMBBbjQ+ERqhaPjwH/v28MRJPGwL5QizvR4I4e1eAQeKlkoWwxl+KC3fA8j4JHpY0GF4zCr8fC3SVc6fMU'
        b'+mIgOCgxSBB0MbgEXi5ZyMXzBB6ppeaBrXqSfCYYFMN9PI81FBVFRcEzzxmmIagCbN8I93GiKylKRsngZXiOlLIxLLikoBi2CdBXL818juMLXwk2BOOePz07Hs8oz4UR'
        b'eWgutOQXh4GByGwyyeVwQAC2hYG3DLg9sN3bFlwQwlZwhqLSqfT1cIt64/If83Q/RZG2Di6H3595dGtL374L+1YnBPI89WsOzF5mb29T7PHi6FF7+5h8e/uL9hd3Jexy'
        b'0Eh3HV2RYJ84+03/Wb22vgm7jt473U2fag0q6VrleaHLK3q2nc5OnL/IzeddYb+XcEHc6EfVD6j8efMur/ZUyLec1u84pfyjMrdq2+mDGYvaPqj/hSSxq+myOmXBSNdH'
        b'IbZb87mVa7erPetrmz+t/EQ5T/tC2NDPzyz9k+qdobeubfeT/5gT3ypSeISVVvwpJMv9RcnPIgvz41xiXH9ys9uRunQzrb2zWCp4iPkBH+wOzoNtC9ZEwLYCWS6mXdPg'
        b'ZR5shi+AQZICDMaBNyJyZdCYk18ooMBR8IYYnOPCo7AXXCUp4CEaXI2QS3MjGLIG9oAjlBPcwmuAZ2qYMs4tF4rBADxnH5ltQBRpZxSXcoFXeOBV0Oz+0BOlyFmOUB6R'
        b'PkTKdvEoPm9OCgecgzvcpQ5j3DCp1hkl+RcfOgf0oOktE3/fuadXaxuaVPWISxL+K0e8U7V21piDVlWvVGnLtaqqBq2yyfKVi8v6Cj2+3UJ9/jyHcvfuCtm3wph1zze4'
        b't/oXvrIOm3ZOe8Koq2f7zFF6RntWV8zenLtu03sFvbrbbhGjdEi/21m/Ab9B3eW5I9KMYTrj0SR36cDeecfsWOB+Qf+6odCk227Jprg7dOwwHTsYd5k3Qqez8+tvu0Wi'
        b'NH1z+gXHco85scvg99cyZYzSwScd+xz7147QiUyCj70Dh4IS3uRfXnRVPBw0Z8R77pBk7gM/yk/+wJ+SeHQmdyR3ZY24Bg7ZB36JZ70WT3up45iQ6ZExUXm51lBfXj4m'
        b'Li+v0qgU9YZGBPkXh8kRPSosxkmLKYAWT/hHhuIZnD4FPf66hfrmOQ6HI/maQo+PHD1aV28RP+AKOJK74mmtKR/xnbYXjNo43bVx/fZzASVwNr99p8O06pAwnDolTuBZ'
        b'ULZxSbECE1pBJ6XCciKSEpWcMh76x1dTZQL0K1Ryy0RKGyNVzVHyttuWMSH+dpsyWxISoJAdIskcI7eapxSiNzERjvjoTYTe7DdgwcV2TLiQNKmQ9G0Vj1UTvpnGVuOa'
        b'cBiBrROXSJEyMZlHcmnLuFy6kU/IPI9F5vksgs7bxDeR+Ueg42R++6NknjeJzPMZVhu0gk/Z4Gnl0mAf8ByfUj9zOYOnW4liXl7QfPj99KN9+1JaOa7689nc9zxDXrGl'
        b'W1NecgkpEy/86baB1Fa/kjMvKhJKy+2q3LKjAtdel9on7FpIL++qmNFN+69QhZZ0OC8ITXJPin1bU6Hs52f+zJ36ON1l+691UuFDLKwUPF8ZAQaV47JNhJByAid4TX6w'
        b'9SGW0+AbdXBrhDn6XAXcw6PsI3miZ1IfYuHBpwyeyYOt+XJPJOlJhZQN2Mldn7CYxCnd3DGnyMtBpOl6FhIKkrle5eDgQy9c7P4IxMFbi5AQBy6G8ikBPMKBV7zgUULB'
        b'FKDDJ0KWXQlOEwnQBr7OBdvXg9elgqlxXmAmTQTVx2zKy9X1an15eZMTgxVyM4AQnwqG+DzQc6nI6LMzB2Ze9hiOyBh2Dmvn77fvWjUq8ezM68i7IwkelgT3rhqRxAxm'
        b'DEsS2jmj/jN6Vnev7p/RH9PVgNKKR/2mox+7u64epjy9/A8kwQ94lMRT6zo+z4VjfJ1KUz3Gx5rFmGitSqtDSogWy7la9/EmCPG0rcATl5muWPycVP3lOGU8evxtC/W1'
        b'jsvhBDzFXP0SI9x+YRB1XBzFq+JamyGV4zOEmR/VXDI7uBZCEM/WQsRhzxQ0D7ibeKbZ8Qh06tkx/nnW7DCEY0QZnFcmRpJMK8K/1ii4pyQbYRvCteIFRCZ6BqkAb7oK'
        b'XcDh+erq7d/xdLNw/uc/Pvz+75Pj0czp2xeD5s7+GPfPD0TD9UiQsF+ksbc/7RXwXyFZvXL3/JXL/tRVebRx5dv2Rz6hXtXaefagLxPsBe3PS/KYbzF4XVjBXb9g5kOs'
        b'PIAW2gVeQBx6D9wjlzUSLmwLLnEp7018sAO2gz0EjbPBVmBESB7tg9DYjOOxYGDMOTcmO69IxqG4a6MzOBkRc6VcFibjYTGjMeIGNSq9Wq+qQ5g8bRwVxmEEmRNNyDwX'
        b'Y12Xvue57ueGXcPveQcPhaReLh0OyRjxzhySZI56+HQ2dTR1burY1Ksc8YgYco5goahAi1s2xq9X1KkeRUwBQcxxvIzEeGmlMlVm1PxuC/XVHB6H4/m0qLlXOIN6WSzj'
        b'/S8T70ky+pToGb8EbLWCnvDSKhaGCl3gfrk6vayFT9Bz+zYtQ9YfQc7PPmaj548KQ3pnuedvPIoE3/N7t8bxqH/ssP30B31SHqHbZeAqEiuPZVigKHc9vA7fejgdxT+j'
        b'mIUxNMgSSU0YKrAlZYA2cAn2M1TYhJ43bOAVpEb1SHmP0lcewcoJtNRZQUudBVrGmNCy8HvQMhAR3U67Druu+FvONJtoEozUyvAHBWsVGsMkvHyUYMZbIuZ4dWopFs0s'
        b'QIg5/SkQU4vVHuu0kiAkb5xWYhWSqub/T9BLwSSEFBQacIfDs0GwC9tGSqFRJpMXZ+cugsaiEqKkgR5wblE20tnkHEoPr9sKkdpxwBCBc50C25ZPwmOPJRaEFqFxJ3xR'
        b'ffiEmqtTokzKvuzD78cSHe7Nfef2qRNceZ4SXef7v4yOnZ1h99tVYVdbzu0b3hGwePfWvoN9L/btC25t4fAQusd9bXNgEBjiPoguPRcTTf+kgvOJEt7u/mGL9Be2lw53'
        b'9O3dekFA/ZenS/ONNSbVKgKebxTjJhCNR6Gf0Hla4HlGoHiRW2w5F8CL4PX1K5WEYMNXwAH4FkOyncST5oMUFYIJtmgJPI+mA+wBvSyKXVbzEKNcofMcJJOMCySFQrAd'
        b'Njd9r0gyLn2PCQ2NWDlqcjAhKPNKpsoSZqp8vpRHec7oDern3/aQ3cMaxTMj3rOHJLN/6Uu3z0X0uzf+ZFpf2i0P+T1/6VD4rJuS4fB5I/5ZQ55ZDwSUX8ADIeXihqfS'
        b'HeeAYeeA3qAPnENZE0rETChsqHtkJrEqLaJMtN6sNMzEk8qyznXUBKH/ZslTEnpmPrENMpayB48YZIjJzETcsQGG9x8zwDyB7MErVF/8a6KAYPlKx2uYWgfsCDjagTD9'
        b'lX0yRLPPVG8fWnQGWyhmJ+R3rTq/9NyfnP7wwi25/blT9vYxs1de3HUxf/TP71a+Izmt2H53xY9XwFK4AGp4ym/6L0RTv3q/jLduSTSvRkzt2ueygSdCIgfB4TbBWhYO'
        b'w4EMQtJ7lxFqvRzuBjtZxBrugFcRdoL94CWS24BCg7A1Mge2yYSU8FnwchE3ELwJrhE5HuwAR8EWszyOhXHwOrzB9QrJQGjxBColRguaZgnYSGHV6bWI/DtO0Fv8biFe'
        b'1/Ion+ld7n2BvcqTq/tWj8yIHfaKbReOBoaeTO1LvRMYNxwY94vAhI689rldwaOevj3ibvEdT+mwp7Q/aMQzqj0DKdqMfo3wOyjxcyHlGdy7eMQjcsg5cjKnmBKnCZ9g'
        b'ofRcjNKP1NtgxmmkCH9dg3B62tPgtBxXg1v4yT8QXksdsPaB5SikztuVlzNLEChsX16+xqDQMDEMX7OpQtOppkG7YczGpBTotEGEWFSrVRqljugAROAizI1MRlL976M7'
        b'LK0fU7Ymk25cguMT8Ohsp+67ehgxUTFmj3p4oYe7t3H+qJuHMesrvtAh5KEzzyHyoR3PQfq1ndAh7BtngYOMdDmxzi8GBzTi3AK4OyrXdRGHsrHnVmgaJnEo/PflQjyp'
        b'OY8o/9wyvpKn5CsFR7hlAi61hBqklMJVDtSkP6XIvAxk/i0TbbCxrcbq/rx6xN83fCeZq6pU6xu0qvqoPK1KyQQ/cSYj8gme099NW6zSNhlqdI0Kg66qVqFR0XEoCtfw'
        b'O/t8lb5Jr6KztGqdfoCrnYeAn/wIIfFX3dMoKq+hXt+QVogGjA7LUGpVOh0arnr9hkZ6Ub1epa1X1dap6qVprBddjaoGPfWKeqXVfPUKPbym1cjpBWi4G1DexQ3a+idJ'
        b'Z62w1Sp1vYrOqK9RVKqkaRZxaXkGbVOlqkmlrqqtN9TXpM1bJMvHlUK/i0r0shxloVaellGPOkyVVorEJE1UxmqFUk7P1yqUqCiVRoeFJw35br1ubYMWldxk/oZWn1ai'
        b'1ypgjyptQYNOX62oqiUBjUqtb1LUatKKUAryOdTzOvTbZGBlN79UrsO1w9Yo2lQRBJLTZQYd+rCGVXk6ZsqY2LQ8VX19k5zOa9CishsbUGn1TQryHZXpeyp6Prym0atr'
        b'6LUN9ZNglWpdWqlKo6pGcZkqpPysxuWGmUBScxw9X4VwBx6v1utwK3GXTk5Nz8+Xps2TFSjUGnYsA5Gm5TB4omfHmWHStCzFenYEepWmlSCCgCqpYkeYYdK0TEX9anOX'
        b'oz7Cr5a9hiGrMQ7LCg11qAAEyofHsflvNe41pvsRMCczoxDHqVTaakR2ULBkSU5WqWxOAxobU+eTuaCur0W4hssxdXu2wtCol+HvIPpVKTd90xS26HdrcNz3Fo2IndSI'
        b'2MmNiLXWiFimEbETjYhlNyLWSiNip2pELKuysVM0InbqRsRNakTc5EbEWWtEHNOIuIlGxLEbEWelEXFTNSKOVdm4KRoRN3Uj4ic1In5yI+KtNSKeaUT8RCPi2Y2It9KI'
        b'+KkaEc+qbPwUjYifuhEJkxqRMLkRCdYakcA0ImGiEQnsRiRYaUTCVI1IYFU2YYpGJFg0YmIiovmkVauqFQx9nK81wJ7qBm0dIsx5Bkzq6kkbEDVWIfXY/NKoRQQZUb96'
        b'XaNWVVXbiOh1PYIjWqzXqvQ4BYqvVCm0laij0OtcNRY+VDKG3WUYdJihNCEBJG0JPF6rRf2m05EPYKrH8FiNuk6tp8NMrFeaVoa6G6erRJH1NThdFjyu0ahrEI/S0+p6'
        b'ulSB+CIrQwkZAxyzgCwgsQubYOOyMlQLRDDCcHaLCFN+FBU8OUPs1BlirWaIozO1Bj2KnpyPxMdPXWC81QITps6QQDIUKBi+TPocySVIPiEwvWq9fjyAKNF4MI6dVDee'
        b'jBmITBVixzUsQHBamboejQYef/IdHNWEQJj1Iipt8Rpr+YrIj0KnR9xOq67WY6ypVtSi+qNE9UoFqkx9JULb8RHXa+HxGoREOfVK9Vo5ncXwD/ZbrMVbnMVbvMVbgsVb'
        b'osVbksVbssVbiuXXoy1fLWsTY1mdGMv6xFhWKCbBiphChy009arOJGhIJwQja5EmWclalFl8mipunJRZiS+y/jUsd1mDW4hiU7fhMfFTSWdPkzh26i9byGlPkgyRSmvJ'
        b'LFhA4iQWkDiZBSRaYwGJDAtInKDGiWwWkGiFBSROxQISWaQ+cQoWkDg1H0ua1IikyY1IstaIJKYRSRONSGI3IslKI5KmakQSq7JJUzQiaepGJE9qRPLkRiRba0Qy04jk'
        b'iUYksxuRbKURyVM1IplV2eQpGpE8dSNSJjUiZXIjUqw1IoVpRMpEI1LYjUix0oiUqRqRwqpsyhSNSJm6EYhATtIVoq0oC9FWtYVok7oQzRJToi0UhmhrGkP0lCpDNFs3'
        b'iJ5KaYi2aI+pillaVZ1StwFRmTpEt3UNmrVIkkgrmbcgQ0a4lV6nVVUjJliPeZ5VcKx1cJx1cLx1cIJ1cKJ1cJJ1cLJ1cMoUzYnGBH11PbzWWK1X6eiiBUUlJgEOM3Nd'
        b'owrpw4wwOcHMWVAz+2aB5qsq4TXM6R8RG2oYuElqML/FWrzFpS0wGVdYmSeZXWImg2Ing5Cao8FKsUKP5VK6xICKU9SpEBtV6A06LNYyraHrFPUGxF7oGhWDpogdWjMD'
        b'SFlZ1Ji5q5Uk2/cmtlK+FaZkvezJCYmJaaJ3aCR80yaRl3RlNY43dTITjmWFsU44Yaka46QVDthos7B9bz5+ZFOmpTJtDn7kYhuiQNeoUeu1edgSxmFMg9iGZjILFhCz'
        b'IGND24jj0sxmQSk2C3oZsx8IKfeoUbewz0V8T0dj9hd2lLvPA360yxzON5UcyknSomqf07rqyxpOnLt3SxZjHMSWavgmOAT7dLAtArZEggG41ZZP2SRyN8GXl/0Pmwjt'
        b'MqqqGgyoifU1Y46ZCI8YVUbRqNJ84sYYCLEB+TvvuQiz6pC4gg3CNKNMoXmhRtQMJcGuqGN8LFZpS1Hwq2sIsKiOkZIaautVdEmDRhOVjchcvSyvCRttJl4nCGfakrwy'
        b'msmGjXOYJOvUOgMDwHHsd2Yiz8e2REZpYD6UuUhWUlWrgdcQQmmQoMN+TctUaVQ1StwQJmiy5EyEY01KV5q5J4gSgaVMlYlemDVBmpG0TPrkhOXLpEkS+R/rkCgxmrF6'
        b'omuYSiCf06hRAhJS11c30DI6Q6s3V8UEyanHOR8B4mSx1pLFTkoWZy1Z3KRk8daSxU9KlmAtWcKkZInWkiVOSpZkLVnSpGTJ1pIhwaWopDQGAfKYgcECtIoAYycB0Qtd'
        b'oEJE2GzepQ1yesK8i4AMLpvtrXIaKwFmVZ6x404MI50fkZ+WZahfTXZIqLQ1iOo1YUqF4ZmL6PgUhndXm5NgO7M1uAlvmCgrBaaVER0DN1xbp8CR4yhiLWYcVabKFvu4'
        b'bNYjGRR6TDbrkQxKPSab9UgGxR6TzXokg3KPyWY9kkHBx2SzHsmg5GOyWY/E2VIel816JBnu6MeOt/VYkvHxiDI1psQ8FlWmiCUZH4ssU8SSjI9FlyliScbHIswUsSTj'
        b'Y1FmiliS8bFIM0UsyfhYtJkilmR8LOJMEUtm/GMxB8WW6OG1qtWIda1DzFdPpN11KrVOlZaFWPwE9UPkUFGvUWCDpW6VolaLSq1RoRT1KixpTVgwTZwTE7wMQzW2tY0T'
        b'OTMvRVGY8k4wZDoso76JkbLxIiEixgVqPWKNKiWSQBT6R6IfocOTM09Q8kfjtBr4hs4kJljEZJMlo2o9kkrGdTXCSWRE3rGqWJhaauLmiPUjToPl8moikddhBq9XqVG3'
        b'6MeNzzlIfNarq9WrFWzqX0Z0y3GjNFvMYDRS1uIkW0zKUjHqikpdiaPy0ajh1TYdI9lMLaixDc6o3ujLCo2hbrWq1mwdJ0yQSHHY3aZQu9S6XIwdbJtYguM1HJ9slo0D'
        b'WbJx0qgbbSkbe7qkfxM7IRkn+UwIxtiNyQe2e+nyC+HuKCIbw115IsqtEnav4NvXCi1EY3uzaCzkItFYYikaE2FYiP6J8T8lFz1d8T8sLp8RnBYxWW3Rf0raKDA6GF2J'
        b'o7yt2SGmjI+3YCpttlNK2zN2p02ubWVCAhUjqD0LKiJQBwR1ZEFtCNQJQZ1ZUFsCdUHQaSyoHYG6IqiEBRUTqBuCurOg9ri+1Vylx3abMgeLdrp+zz/bM56n7VgtDzBy'
        b'TW3nK71YbXe07D30zw7941Sbe1E0HrIs3fu0rbl05Qwj4+6Hd/E5oy+IlD6sLzgpA1G8wGhD9vlNI/G+223LnBHMBbXND7XNZbwWrmf8zWqLaaego9GpWqCcvt1mvMRp'
        b'G4S2NdKgMZu5eHPNnJLF30XZ0aw/M5hmaCGzr9UixYBAuwAjN9a0PsHuMNpncQj73BKdRmr/Ca7EJ3gcPsGunhPJtTXm5FrsR6mtwElwT3+CN9J9gjFVKhqzUyjXIvKq'
        b'LVcrx2yrEJGr1+Ogo4KZR+UaJKXqa8dsqgxo/tdXbRizwe7saoXG5O8irlYjwbS8DtGe2sIqG9ZUwJ8i7lmbKLO3JXuzLdm8x0GDzTeKUOcxW/eE1XbEcwyhaYvduOeY'
        b'LfEcs2F5jtmyfMRsNtmaPMcegbI9x77ahzrHomfxXw7TFHWTSke2JI+Ph5p4glSp5JOyTAKkIt1KUUdPdGOqaTMyop/Yfmba7WzqT0W9flIJ+C8sE5E9vZnoSuV0Bs6P'
        b'CGQVTTxoaUMjjdhEEq1U16j1usn1MlVjfASt14KJtl6D8VWi76lDwvfVwRJ1Uul88ourMD8q3xxrqpjOel0wU8XsDDFDOV1aixgcmiEqWmeo1KiUNag9T1QK44LDaOKo'
        b'JFqBikDvTP1pTQNitlo5naOn6wxIH6tUWS1FYWp8pUq/ToVXyekwpapaYdDopWQvevLUY2GaMqn0HFOIrsJm1rDxxVmWeVY6VSnm6ZZqxlbd+GDire8NWjqMcfVZDa9p'
        b'm1SaKQsy+amlElUSi12oGAZHTNQnTFUjpxNioiPppJjoKYthzfdUOgu/0OQFF1etrkezBtWR3qBSoIqF16vW4ZXitYnyeHlMuHRyV32Pc7Q9s9XqapgLRVNU8pDg+fzd'
        b'VZWUAe9+g9tBF7gEWwvAmQXQmAPb8qJgywLsNJ2dL4WtkYUysBPuyS/OBq86g47swoKCnAIOBTtAr30DfCOXFNwU70B5UlRYb6He/kcxqZQhAwHBFrAHGEnB4DDsfLRw'
        b'uBu25CM5ALSYSh8vevsGewpcgRdI0csX21JIRImmV26KtPGYRZFduCkNEuzKadqCWwevFmfLZeG5qHjwGp9KXCHUNcC9ZBMxKWO2iwhLFM6DtNKeVzqHMmA3Qh04oLPW'
        b'amhEhbZG4srtki4m9bLxZWoG3tSKwXnUXdfV3cF5Al0vKubPa/68cc/bDiDaft6fjw/sKx10FA/Oj3KZ9olD8s0Dh0Wz7YeDc4JW7PD+YKHk78//7a1v3X59c6uaL/3R'
        b'ywv2cz778ee7vvym4LPt3S0jLvdj7x15GBL4oevd/ZLTC3flngt/ZfVCjWPvqoM9ty7nL+KW7N58ZcfHJ+DO20lB6945nZG9f93huWUu3/jMPbtW7HDuxIY1lyNW3f1q'
        b'xfVvjwmLnWxOOt2/Genj9pHUntnrsB+0rgOt1byJbfw8yimYVx2V+RD7WAbBt+BW0FrEHnIO5Q1fgMfBAX5Tqj/ZVYH6ZmCtGPW6tIB4ohfCjigu5Qaa+TbgJXjsIUIu'
        b'at4acA47kbOGN9UbleUewBeDN+Bp4mkOznq7R8jCsmVcCu6HPUJwiCuD+2AL85Xt4CUD3LkIlcIa1WngNR5sBS9pyPakGnA6IkIuhTuxbyjcKQRnuHFgv4TkL0/hgUHQ'
        b'A1rxDuDxoRRS09bywPW8hQ+luALb4CFwAzfYJI7ieprQoDAc4RvcIZTDbvAK8Z+XgRt63KZWCjZHhstxWtgG9yAZlqJoncAhJ458OB+eBy2etTglsf2iD8vQZ0EnD+7I'
        b'BucfYs9z2Al3g0usD5vkYG9wOQxs54NW70yp3b+w5xWLCY/udyUb6FzM3NhyB+AwxbgorxVRAXjXn8NooKydf9uZvuvq3qHrSt23ecQ1tD/glmvEPe+goeDsEe+cIUnO'
        b'6IwIlNaJSZOyb9OIa0i/yy28qwWlmT/inT0kyR4NkJ707/MfCYhBSR1R0nY93nOFk44XlzTinTwkSR6dEf6yvL/yTkDScEDSSEDKpAzjZWeNeM8fksy/H5qAKxk0GhSF'
        b'fwNGAwJxntHA4Hb+Bxa7ZxwYn+gG/GjEjzX4gY880OrwA0tdWj31OLdpbGuvMP2xvKen6NVPcJZ09Pgn6tZvikQcThXnKwo/n3Yzca8wGknmaTyLTQIcM1H3JUT9eWoV'
        b'NfmvhEJyMqdQyhkTl09IUkjJw31BlDzatD00XaOoq1QqZrEaYga5cMzoRHWV3vGT3fJjHJ+/M7E5U8FmkSgMsU+lrKFes0E6wBnjKRuq/qV6VzP1tisfF70mV1v7omXX'
        b'm2ssQUnI/jlc457yQ+VMfacz9WUKtFLdf6d/ncotxbMnr6yHZffG3PKLYaorfayA929XvJapuG25WZ568ip7W/Tvs4eeZSrslanQqcbFs/9cBc2i2pNX0A8l0e7DCUjF'
        b'AqcU8f4zVbQpNwmBT15DGo/6eBeuPLTSVNMphcj/DJral7PkzCevbSAe8Akcld/yk5tw9Hsk1SlqPb7FqAI9DnBNO5zMe6v/s/ubqp9of9P7h5cJdHgHK+ez9sPvx5Nd'
        b'fH37YoLWmXY3LXDLv7yolLMmmleTSsXfE/4goVjKJfIN3DMLtCLZ4gp40Qqbn6F/GIITdcFueMOSy7eCg2ZOj9g83A92TLntWVSOyUp5eZMzi80QCOHdWATG2+VybSlP'
        b'n674nlnds0Y8wgdKBiV3YjKGYzJGZJnDHplDzpmT9jdbY3bM9mbM4BicOIZxYtKHQzgT+4O+yrF9uv1BhHh0CAOoPnEkT2o3JjIRN2YTkFCn16pU+jGbxgadHqt2Y/wq'
        b'tX7DmIhJs2FMuFZBrCniKqRgNtQxVhaeXlEzJmhA01tbJWYNt6N5uHdhXONbP5wM4Z+DaceqjdHJyDXaYXw0Oht5RlujqNqR4KUY4aXjOF7aE7wUs/DSnoWB4k32Jrx8'
        b'BMo+WuyrXwmsWE8ylEodUo+xjqdUVWIyhf6vMrnN0irioPAEBhSi3hPdXEHXGmpULJMF6ledGqn8NLOpClsfdCq9nC5CE3VSOZhe1uGFVXVdY4MWW1rM2aoU9Uh9x1mR'
        b'6q9VVek1G+jKDTjDpEIUaxVqjQJ/kmi72OlaJ8ctVWMTOSIXpiJNFgNc5qQyUNEGnbq+htRovBg6nAx5+BP0SJaptbXYJDi57pPSh+kV2hr0DaWZFOP8NDb667D2rVtj'
        b'wL1bqVVUrVbpddLUJzdqMdieSmdY8HR6OXFzWDlVNvzlVJpsfFr+vdufpiyFmVypdAn5pZebnHGnTG+ehKk0XrJAQ0WMLcvZzrhT5sXTNpWeg5708iKtfup0zMRGSZkA'
        b'+UYknVNSJIuLSUykl+NliilzM9QglV6cUSrLmUsvN639r4xYzt7cNfXHJ4gINikxLzQuiL2lYMrsiOygzqxFUwNNV12VVt2oNzFwjKf4gBMytzI0ugaEvyqlVWsYQiec'
        b'GrNPDTlgkQy2nJ7LmMTIFJ1RolfU1eH9xvUzpjSOkcmAEAtVoNE0tZRqcsSjAnXrOjVi06r1aMRNE25yOfivsEGvYqYJmfwqfW2DElGSGkMdQjRUF8VqNAHRpFGh3qlS'
        b'0Q1I+rFaDtMkPGmIrU/HNFOtY1VJTmchomYmSFZLYU87bBlEqI4PsKzSoAYzZ1fqVNZzVpiOr2yoIjVnVkXTa/X6Rl1qVNS6deuY07nkSlWUsl6jWt9QF8UoB1GKxsYo'
        b'NRr89fJafZ0mMMpcRFRMdHRcbGxM1NyY5OiY+Pjo+OS4+JjohKS4lFkV5U9th5tWaCAGju5VPrp8aa5MXoi3K0eAgUhwA3RRVFCJoDZxoQFzZXCgek4cRa3RUDFUDOwR'
        b'E0PWpjB8VtKCKtvZFfnH1gooQxJO2ZI5J88sZxRDIz5+LVe2EJ9bsDAM7/hfAo34B4keYC84Cy/m28ID7k4GvGkavLwYboMX4G5izBBRAthdWMq1N4QasH68HHaAt+AF'
        b'OWzLg2eFOfh8BFQ4Pt2NS00Hr/DhFVEoY0NsywcX4YU8uKtgEWxvZJoGuvjm1i2AxkKUcVfeokb0KMrPhQf4FNwJtonh8cXwgIGYhLaL8sRyaS64BnrsKNvcYgkX9sSB'
        b'fnJcJngB7kMy04UclB2eiORQPNDJAVtA+1pS0QJ4tkoMjVFyeBl2wBb01UgwkAt3QSOHoucL+LATHCTHCcI3wIUieCEqnAP321HcbE4iKvUi6VvJdCFlT/1BzqMr7D9d'
        b'qzG58nXDffD0s146B3gAXsRf51A2K7jz68AN5hjNQ/BaI4508Ix1kKNvX8yH5yLgXh7lsYEHzsDtUWTA7eAO2C+Wo/yo85LATnx2ZxuPcoNv8p3mgNfVicZ6vu4ySnj6'
        b'7s26oTzHbdHO1FD3Qe7vSu59umxF0/6c/MZm+f7Zlfd+ytnVfH+vI+/teXW3vjZ8d/hrv1kVWxyeky83/lh5cNN2js03L58MjPtb2MGj3bd3/nn7H7+72DmS/7z33WfH'
        b'fmzbK066NM/1jY3f/fJvmW9oXzjccL90/ylt8YlT8958v+XaKWe3U3NLTx1KA/XvOHAWNaf8ramleF7vb3t/2/jO6Yze6rnvpbTp6jf6+jy49vf85f/o/vWH2x5Qm//B'
        b'/ctYRNjyq1LhQ6yQwCOB0aCVbWLku2AjI2gB+x5iqTUQ9GTkWTG5lUEkrUXECeCeGHiIGCzXccF5k6VxXbLpsApiaJRUM0bCnSvjGEObDO5/RAhHPUyqA7aG2UQUynJy'
        b'CiLAS3mRsE3KodzhNX6sFBxnTvd6CQzK8iLDslEt0MCC0+nwIncDOAW7pc7/zkGBVi10+GFxKN34WQJ2CqWynBH0mlzHBe8JIBH6/2AS+vPtKG+6V9CrP7mxb+OIV0K7'
        b'cNTVqytq2DV8yDV2VB7TntX1zLAkgjHRJe17fsQ1qFd/JzR1ODT1cvFw6KxbrrOIRW3OzZrh4IIR78IhSeHoDGm7sH1dh9OoNB4FNg07h4zOymwXDnmkDjunjQaFI+CG'
        b'YWxuC0OhtR2Oo9IYczo6CIUMHQ53Xb1Gw+T92kFOPz54MGVYEjwqixvMGMzsL0Pvs4Yl4aPuXrfcpV0r2nmjzpJOxw7HO87SYWdpf2C/dsQ59o5zyrBzyuWQD5wzWHqL'
        b'C6O3vEKZ/XtP4MdJ/OjHjwH8OIUfWO7WnsGPV6fQdFiDgfu9YuKPnjinRHsJ6z/WhkGKVaBMFPvPv2ELny227X1DLHyfP7WdDy+mnxQmUZfEGVye1HbMXok9oU2C4pgD'
        b'I/6bX4WKOvKLj09TjdmaXFWqVGNiLKwhERk7sjKdMN7+KjsWJ3I2c6LdWCcSWdOJOsmRr0j/wSvJHHI0r63RBelH+OheckBztTPRiuwstCIx0YrsWFqRmKX/2G0Sm7Si'
        b'R6AWa8p7RI/XihTjvig0c2jjE8j+8/CeMiY1jQQQNIhIrEdClYJ9xDUWvCLpGm2DoRHFIn1DMZmhN9RVqusVZhEvHEl/4UQ2YUQTbFsad6LHFRw3iEwqCRtI/p8a9/9n'
        b'NY49RVPxQDGQcUvt96hzFnOayc+AzAVYlWmXf48T/JSfY2gG8x0TmTDBGLWgvgHb8bRE8K+3Ls6va8Byt7pOoZlCcVj+mG0ASB2zvhFgyhpj6sbUt7KhYTWuL4bI6QIT'
        b'dinIO91QuQoNPN1gXQdBCILUyOTE6BiTKRUjAtKBcXHLJ7YITFmJceKaSi/SGRQaDZkZCHHWNqirxmfjctYOg8dq0ibibDkMZD/zcvYuhO/VdXH2R/RdC1/3/wvU1UzV'
        b'OlWNyVPx/6ms/xeorHGJ0bHJydFxcfFxCXGJiQkxVlVW/Pd4PVY4SY+lGX+SWa58Kmw1Ei5mV2j+EOVIGfDJSstBO9iTl1MAd0bmjGulK8Cr1vTRzeC6bTwSwo8SZXQu'
        b'uLqYpYuWuCBtlGsfi2Kx+yk8B/thc548twBJ+xMl42Lnw92TNN1W2GoLToIzfMNslNkfvFmgKyooMh3xtycCbKNhyxLYjjLsgUakl9ohHQ6Vid7fLFkBjoBD4JgtBU7D'
        b'g+JC+KYNcV91CwWDulzYllNQlIdPBoyGL1TzKc9MHtw1w41czbBsGU8XXgB3h2GtRg5eT8oBr4ZxqOk1AkEFOGWgcTPOhkaK4SWwe6ENbJMVIj2Vi7SWt5bG8UAf0jGN'
        b'hlCc6BjYugp1hdnDxRFcLs4mZwUvxAfNx4BWwXp/0Ey+6bQeHDLVKidSio+sl6yBV+AxHrwKrywg4/R3EZe6n4gFwor80zlItcXy4Ep4MEiMhrYUbFtDlSptDPgYVXgU'
        b'7AaviHEXoY7sADu84KVspK63ITX4IlbhW8Fp9JYPd2djBXaFl818HhofLDc3LsG2AhTIKYY3qJwAXwIVJ4Ljceg3pimRioFbwD5y6n44bFdD7EoYtbyCikL5WjTf/vOf'
        b'/8x2F1CjGS4Yn+xFxc8wzjuvcJBerkXaGl2hOa5fQBkySS9WV+CuaTPZPLIjF+MLN6JyFyE8yIa7SsKkcA94i7cke/yODSl4g3SesN5hZRVkME4C98IjJfBAXC6P4sAj'
        b'8+AZCp6Br4K3iIfQangA9IhNo7RwAldszN0Dj61ndQ94De7lU6B5ke2yJXDAgB1TuKA3Z8J0UBwGD5TYWJoJnnETgh1OjrVwJ3FsQl88DE/qcmVFBVEYhwpNlgIp7EMY'
        b'3SUArzvCTgN2gOHX1UcwB5BJhZQYvMXVPAMvrFxK7o3YtLmQ+wMhtX4wpy4/ULtE4E2RSQAugN0okck+xDhhIeyCLVFFBcVhpsIWsz2xjsJr8Bo4aY/afgpcIDcjpBeJ'
        b'IuQ5keEcSp4uBHu4UXBnLolAzQDNAaA3j+jSXC0n2dVTyiNWF/EC8JopU5g9yQSugVdJlC3YBl8D1+HuiWzw5WeJQWh2rpNlC0vs4QVnMKCW/bOSr1uHlLFWr6BXFs4s'
        b'gtHOF48WhdYdOiENloRk/SPznX/YZ4mPz62c054dyD9wgT5YNT/yv174R87PCn3HUvPn5j5/Y903n/01pecTDwU/vQtcC/paV/GrsVOnbG94zRWNVf1959GffCbR7/n1'
        b'qrzso/Eftquc//z3X3+YZNcRBO5WpOfb/DPh7R0PNJlG1/QEzsJdz/v9NNou0e9Sgy7Q++tDlffbvaZ/6hxn2wj/8fbWv3xx7JMVPRU3f76/8eO2h7dn/8BN+4sbXRX1'
        b'p7RFL2Xnn1nGHVn2RcfIz+3HFnbkfpf/adrveo+r0hcePbQqJmr3Ebfu3/0681bJBz+9XfHuX1p9t1XdO9P//EDRwTv+H1++OpT2bMgbhw4qZl38cr1H99EPZm3Y+9HG'
        b'+VfWfZ65bte0c941nX96W+33Cb28/tgfRtb6duzWnjBcbH3tcvrnA/2fFc+7d0bY81rhZx+4/RHUfnX1+o2R5X7lq/NTrn/2tffy3/T8cHrL5b+uLVtyZfPAwotZRct2'
        b'ldqHSzcE/9ffRSUG7d7nXKQOxELjDfZGMMYe8LoX26WscS2x9cALkZXWbD0UFSFKwKYe+Ap4ldhy0Mx5FbzG8isjtp5XpmNzTzg4y5hqXof9c/KwP1g66DW5hDkt5mky'
        b'0pjotxAaGSPCTS5htuAcPLqMC17ReZDDIZ8FBz0j5Jg7RHIoF7BPCHZzZfAl+NZDjLpLYF88PFqblx8upLgrOUngEnydOQS7Z8kmcDq/IJJL8ZOx8Q+cRxPxDHFhgzcK'
        b'4QuIm5j9wHJrhc9zQ+fVMuu/3Yiy9BGXsXF/MUf8M+4yhjrsKnEIC4KXVj/qDgba4KvmhWIxOEk89EAnitquw7NThpkd6W4XsBMcgu08MFgiZGp1NtIwYdBCfXIUnOZu'
        b'4PpJ3f7T9qypDV3Y8kKkiC1brFm7HLFFZUKnb/KwMLVMRBCr10wuY/XaJKa8g3rn9cfjw+pHvFLahYyBK33EI2zEVdo/907kM8ORz9wMGI6cc8t1DrFwZdzMHw5eMOJd'
        b'PCQpHp0hZyxcTLaZIx7SEdfw/tI7stnDstk3Y4Zlc2+5ziXZMm+uHA5eOOJdMiQpGU3PwVaw5GHnlNEwbPLaOOwczDKShUZgKxx6e37YOeiuq1+XsnfObdewuz5h/ZIR'
        b'H3n73LsePozD25uBl5VXpcPBpqsxUE5TLmy9y9ibOpqU2p415BN3SxJ/3xQclsTf9aN73Q8vv+MXNewXNcgb8Ytvtxt1de8KH3YNGnDtL7sjmzksm3m5akSWeTN2WJY1'
        b'Ip3/bsAtaR75Zv67TcPBy0a8y4YkZfeS096cfzPr3cVvF42kl44kL8LNih92TsBmu4Q0/L2YYUns/YDgk159Xu2Oo64enakdqb38O3TMMB1zyzVmNDhuUDEcnNReOOrh'
        b'fctDPuQvH+Rfsj1ne3nWkHtuOw9XK+iOd/gw+t81fNR/xh1/+bC/vF837B/XPv+uh3dXUm/KsI9sxEM+GHzLI+mef+hQWP6If8GQZ8F9D5+umt4alBwVPBoR1SXqFd3y'
        b'DBv18usV9Qv6HG95yUelMgQVHHK8HxY5WHqzctg/p33+aGRc+9w7kqBhSVBvybBEOurs0WU77DzDZFcM+cA5hmVKdGVMidjOrn0TP67gx1X8wJuctNcpsynxCa2IjyI+'
        b'/tSjNsVxs+LP0GNKXC8bNy3iI4XX2HE4amJaVHO+JM+nNS32C5Opy+IMHq/KfMgA/hu/+amJsjQDdlJGkdHWyCd3P3GN9uR6EQcjx3QDlIBLtYxvG9koJCY/AcvkJ2QZ'
        b'9wSbhCaT3yPQqR10JusXjox+4SfjEu8dunZd5JoIF6qUQDdOE5ALQ7bYb9YMVGcyB7LKgZGng/uLQZvNGh7Fc+QkR4MbRKSqAANVJaCtFLYtKiiGFxfAi4scEqOjEeVG'
        b'4+3nwQNbs8BFInDMWDKvJDsUtpUmRMOd8dF8ymYNB/YqJGQFajbSP7aYy+FQArAbbg3ngEPxVeT7cACJ60hGgluchOS6JyTrnidyEdw6G+5EAv32AvgKImYhlOfcKCL6'
        b'cMHx7Dx5dHxsApcSNvls4oCXvOAOsuyUPw++PnFPErkjqQVchEerkfSj6PyM0iGlghJt8G8ryStE0s/RNdOS3hLudO5ZbHP82R0+g9VJL7+bHXk+88BGKk9zZbbvjN/s'
        b'zg94Nbd6oct757+s/vDw78/9vXhj5k/8tn17ZZNjBb34XMi1//NW8ic/ifpQ/puWuL0e7Z+Xvu3Q3X7tZzP/EPkjg/v2HxweTY44FnXmdrW/dFnn8ja3BVcyfvZTlfy3'
        b'f/dfsSG+bHpbYtn+tNLz/+zeVfyLr67/6qc+x9+ueKtm1U9/dHTPosA/Fv/lvX3LfglXHTH0DXz7scMv8+69VP9e6IkNPdl/2bz0h5uXrfn6t79ddbs5o/fjirb3r2RV'
        b'tL15IuZP/Yk3NNlLnGN73vQZePtv3d/p/+Cb8fMT936Vq988/zNlfvg73/n7p8wcLZ5/8sPcD/82Y3ubIPz17zZtvnNv4ecrFl587qrTgvTNvORnlTEjZ6XTCC+HzTYz'
        b'F6FBxJemiVDnv8xZBIxwkHDN2eDyLHAavAxaGV5PGP0JeJFk9HxuM4vNCwMwm4cXIwjzBs2NoM2SzTciRj3B5vlOjPv9dV46aC0veNT7fjPY9hArcUhnboFv5cFLusJI'
        b'pLHsiQKn+JQjuMErBy3gKDl/PbYuA1UDiTV55L4/vj8HvFzHXGTQiFS9/ghW0faRvHpwQwR3zyfCkbw8PQK+mj1xrRZzpVYYvMZ4tL0FjsCBPHAKvGTp/u8OXuX7yPWM'
        b'jNYrfibP7NSfD/eSbRscatoqHjgDLs8nEh94HZ4V5EFjrHWpD8t8c2yYW7zawN41SJnsVVl46Dv5856V1ZjW7sBr4HCeAR5k7QHAAh94ZQMR6dbCTnBoQtSZAQ5iSQd2'
        b'RzEdfhYJe2iw6+CR8ZvA8D1g4NQSkju9NJF91PgxsAWfNR4FD5FYMPgc2Io1Eri7CJ93X7UOtHMbKuAp6bT/Rrlpmllumnx11ZionLm2iu2Yx0CImHSEEZMeLHWgPKZ3'
        b'ajo0++rbeVgeqelVdK/qD7/tmjDqQ/ekdqe2zx31DejJ685rnzfq7d8x576Pf09ydzIGT+/J6c4h4PY5o66eXfF3fCKHfSJvuUaO+kzvDcCJHnBp72mjEu8HPPR7X+LZ'
        b'WdBR8ECAwg+ElJtvV0ZH7h1J6LAk9IEIw2xMsM6ijqIHthhiN54qZFgS8kCMYJ/bU26eXbwe+277oeDEEc+kEUnyAwec2JFy83rghEPOOOSCQ9NwyBWHJDjkhkPuKEQ+'
        b'4YHfPPFbYUfhAy9cuDcu3K5XiQXEmcORM4eCZw17zhqRPPPAByf2RYlNNfbD7/4o+S1JSvecXgG54Gz9CJ084pvyYDqOpElkEorknbTvs+9fOkInjvgmPQjAkTNQ5INA'
        b'HArCFcD9EozfQhB8b05XxoNQ/BZmfpPit3DzWwR+iyTFS7vm9hR0FzyQYZActzEKh6JxKAaHYnEoDoficSgBhxJxKAmHknEoBYdScSgNh9JxaCYOzUKhz59BoXbhg0wO'
        b'5eXTLrjv7NZp32HfvbI/ccQv9rZznAnQVdKztHtpb02/om/VnZCk4ZCkEb/k284pv/UPbs8alXh15nfk97n2Lj7m84FE9oBHTQ+57+HX+VzHc70JSLa+4xE97BE96Hk5'
        b'ZcRj3pDzPJYU5shIYWcIVjMrdLoxgU6v0OrHeAijn07kcjSLXI9IW7+lLJ1YmbnyKsd029vf8cUNDhxOJL7tLfJpPVlfEsqp18QpvP81H+daKfe7300y2jKb/vXmTbim'
        b'xS+NySatVekN2noSV0cr8Noqy8T9ROuS9GrVBh0qp1Gr0uEdFYzt3LQYoBtfEDUZ0q2tJz66VqphViBwdSo36FVWbP0WgqKNFUGR2EsDGiSgFR4EexC3PAd6chF7Or8E'
        b'nEfh08XAKKA8wRbec7n15F7OIthbBfchsVhOgQPwsBy0lZOLbtc7wGM6LD6C1iUyeDAPvMyXy3mUBLTwwADi6X1E+NxWwFul5uJQhWZrXAJzSWnDHBdTThHFj14DXuGA'
        b'zvmuY5xyIgAG5YM2k/VLSNVg65e0kZjwgsCgJyNRyuYRmRLLk/YOjDWtedNcYhKTwBPEKhYF+oig6bCwuoQRQeGWOC5o4/jOhtsZ36Yu2N8E9+XhWsOBWF4G57ksaFQv'
        b'fedlru4civ/2sveB9pl23BjnrJqQzVc/s7324tKyJt5yQUfGXd/nzmaEiJY6p51zTru64hb/ZfdlGSM/cf4w6C+HxSv7mqkXvlww/eynV5d+Oi0xbksCh28fv7Rh1cGO'
        b'nOiDS7ZVBn9aq+v8hy4hKkwy8JBe1fGp+rULK7+89Ks3Rj+pmHvhpWqe8svWTxzu7lR01jyflJnkUq78zdjZex/DNesuZRT/rPKdvX85J4pxSv9t2l8LT8rO9M5M5+zZ'
        b'Ee604TdSIePp07LkGdAKrsFmK/72zyQS4SgqxWHi6o/lQc9yA5HocfUhHu8UOOgeIS/gVsFjSOrr5+QlMDsiQzbB1xHStIFrUVi8yEG6hljFhb1w5yoi2lUiuabXwjCT'
        b'A4+xHPiXgh3MlaUnE8CbpitLwQ3w2oR8BY8ulNo8Mfe3Gef+4zxfoSvHc5RFx0wQwvPvUwzPX+hECDniwMHSk4V9hXeCkoeDkn8RlNqR3z6ny2N0ekDP2u61QyGJl3mX'
        b'S0amZ7Rnj06P7F8/PD0JhULCT2r6NINxl0UjIbPb53WF7S16IKKC0x7Yo9LuBMUPB8XfCUodDkr9RVC6qTxvvy5FdwiSHDy9e4TdwqHpUYOug1UfeKaOek7vFQ17ht3x'
        b'jBn2jBkMu+2ZhkGCbsc7nlHDnlGDwg88kx6I+LR7ezaSBELjepXMx4dDMi+Hoofp+05U8EzE6D392u3/pQ0MX1jSflOffczewDDP6SkvODmOMg5wxviNCn2txWVY48or'
        b'3ohzQGC6DAufY4FvU8YXCArHL8Qa14j/7QuxkA79EY9jxW1mggdgcqxTrMUhjYbNDZ78MAbc2FQ6p5oOx6FwGvFQHbNAi+m8aj0+0AavV4bLm9SN4ZHkQyaGo7W+3KnD'
        b'J4ErxxdZFdqqWvValZwuwmvC69Q61ThTIWWQBpDkCrq6QYM4+PdwiMmXSdsUGsIofPvz66qIbIkWEY8F2UjXyC3IBwOl2eBVaIyUIxUgG74oahTBw2TZxtbDOw9N5j3g'
        b'eGRugRy2IG2sFKkTrVHFSNmQhYEBPpUH3xAhjaNPTSwH8FKMHdwHThPbMw90izUcsA3siSWLXWXgIng1AtVsfVwStR5cgO2E+sOX4XXYHlHEhedBF8VZiH1JW4BR/cuW'
        b'LI7u9yhBTG5cW/E5OxDtfD3v1ipJx4wZ847+F1e0ebZ+rbv+x7TXq72ZVy4LVvxwzx+KmkZ/ZBezKvbj9d989qtf/Vh244W6VQ/2/J9Z1aqtqtcbps9oDtf/QcAraztb'
        b'Fnhq7+Z1VQ2/Krvy5ztuHxzet+2z7V9e+ePvJZu/WhE7eO5A7mh//7V3h7cUgp3iUUcqcVdX5O+Fhp//3rt6/dvve350yI5+9pkzLY2Ofx+6+c6qn5/ffupWg/32nl/+'
        b'5I9177ZlVez+6KT8xTdliz5+2etj8KDLZubXf33xTsnA7zd+WRvw7gu2+QEwcM5S16w/fPqDO41z33yOSvldSuentNSJMVxfQfrc1YjsSKwq8sPB6SQOUgD3TCf6GE+2'
        b'EOulzFX2oHca0thauRtBxwyiv4IXwFnQAy/A19eZFg9swUku7EJK5jE0KkcYla5Th1e7tpFyWpCSLyzk+oJXwSlG23xJG4VKb4mU55BIMRzkxpLFr7MLmPujBjKUeZFg'
        b'dxFzfZx4NtcNvoE+0RtF+A/cDfY4pMtxEVFFiJMIN3HD50sYn9gtq8AAZuVSOTiZC/eQBjpF82rWgDeZohEaodZfZ3EwzL9a4SDJHwba50RE4dV0hJB7ZXIpF3GXHh7Y'
        b'UQb2MosU18EJr2djiXIeVSighOlcD3hsCVP2pdVIIjBjeRY4RtlKuKCvCHY9ZNY/Txrg7hXYvGHqlEyuJ2hGsTjzRnhIxrpIG74JThIV+sD0h5gK+6alwtdWMFVDXwX9'
        b'3EiflVLxv6r9iimLVQOGBfIxAWhyGKfl+JUwPyGHYX65zpTEvTOpI6lzVses3qDbrqH3vAOGZpj3l7u6kbiZHTN7JbddQ/pjz6YOpA4qb0ekWSTz9MXq52HHdoHJ7r0v'
        b'/Y5r2LBrWL/7bdfou94BvUH9vP4VI96pSDMOicB3eZ2o67br4ncpRz19cN7e0v74DzyjkSIUGn9f4tGZ05FzIO++j19PUncS3p/XH3TbJ2oUcUybbpteyRHHR0q56xfQ'
        b'O+NkaF/oyci+yH79YOnIjNTLc2/7ZdxcOOrr35Pdnd1beqTwGx7ln8kZ8sv4HH/m134ZKPidDp9A9IPkafPcBD90E8zzt2XYpS3DLh9OwTMf7X1sNB5Xohg2KuLgi+8s'
        b'uv6fZv0JW6mfQzzUE3u+PvU1pweFIdQJcQxPypzKNMabt2hhIbl6SqvGdbcpNP1JBcwPF/1zfeS0X7xJUtlQVV5ONuSP2TRqGxpVWv2GJ9nyj7c4Ej9fYpUnyiKRGkib'
        b'pZL/kVUyLOU/ukA20fn46r2m8fOucAV1dRxyBtvnfK6D8xc2lKNbH29AdzNteNmKu/4B/SlDmc8+5HEcKzj352WNFi/8mhfoEPKlAAMe8FHw81wO5T3jrrNsVJL4UMD1'
        b'Tjbmfi6kvALuOkeOShIQxCvJmIMg/iF3nWNGJc8giH8Gx1iI75yj7zpHjEqiEMgzxpg9AUnBkDQC8Zh+1zmcgXikGecjiE/gXWc5U5APKijvKxuOwxzOF0JU8e6SPt25'
        b'uLdd34u760cPuL4Z+Hbce0pc+VLO/eJFo0tXfMOTOWRycO1LUe1x+ItnObjFgedK3g5+T3Rz+l0f/259V/g5HiqlZHjxsmGFChdQw0FicDn2y+YVcRxiv6DwE5eDIvg4'
        b'/E0lN8Ehi/MlhZ9f1XO8HPy+SMRVCrzt4P8N190h4kse5Tj9cxxiDq7DJDa0hKfLicxZYJDpHB15lIMfF/aBbWFkCwg4C1+Yh9hPvxj06zGHEmOXkwXY1cQ3lh+4BFz7'
        b'X7xo+glu8hUVErUYXncCL5VQoI2H1GkqALwFu5htOca5YGeeHAxGJ6Dc8A3ObNi7BpxJZrblXF/Es1in0MLTXHg0BGmkWMUqhjvAEdiaE4mtznF8CuyHZ21AKzc3z0/d'
        b'aLefq8Ozf/ef/fAGbHwZcAeHd+bFWyt3SXct+0nXF7NXnrlseLV6+yfCU1XvlHaC/eDaIdsch1D3hMjsE9GSc2tjT0TrY7O3fmD7jiiusZqi6ipcHOyrpQJGnjgOt8Mj'
        b'5iNi8Pkw4KxLXKQXiSyCWxoxZwtRs0zD8NpCwhSrZ8Ib474C2FHAGzFl2Ap2MRx1V6P3hGV4Edhtg03D4AV4glll2L8EdGDvNxLtCK7arOSq8hRT7vS2b9SqkLCtKsde'
        b'oE0Wb4TPLaYYPjfbhZJ4MpzJOPe+q3tnckdy19ye3O7cw/kj5MRyxLjSOtK61vXbjrjGTryvH3ENM8696+Q26uHTNb9rcfvGdj6KM+axVasxPv7gmJA5y+J7rr92xXzB'
        b'oqYBXNbF15udORzvp7070gJHnU2/X36ID38Usw5/jMJ7tslEscXHQKr4Su52Ssk7wx8/QFFAoAIEFbKgQgIVIagNCyoiUFsEtWNBbQiUOQaSb3G0I990DOQE1A7VR4Tq'
        b'47TdpkysjDZyqjlKZ1Q3exPcBR/jqIwhcFcEd8Rho9Boa7Sr5islCOKkjEUQPkrrho9INB3HiI9g5FXz0JOP/gnM/5TTyOGMdqYw75GwOd78yzenf+T3UTh5V7ofcVJT'
        b'Sg+cfx9H6Ynj0a8X+xvo3ducD4V9WGFfVthP6Y+e01kQmhUOYIVnsMKBrHAQKxzMCoewwqGscNhE+NH2KqVHuK9wlOFHuPjQSdU0lYsyAs/yVaHUpD8zETUfSGlKH/mk'
        b'6clXJKbTGJmzBeyqRUoZwgI3cmSmiIy8QClHEPcN0xB5jhuzLUdcXpGFVF6LtfpxuwKWZLA5mbVWjw985KPC8f3vwvEVetF/bIV+EtfgUY9yDTtmhf4rsiGVoivUz9sn'
        b'0vaMx6Y+vI3y5FBhVOlmx5Q1SxngwfKNnG+51NIhu/VpbuuiKKJoa1ctZ53jVpxt4QSFSHOriAKvCEpqbJwzniWl7NLPoPD1rxVKFVcVn0j93lxDQs3U1779AV+HnRuS'
        b'fD86/H4iYirn9gW/xBF2eaZ2py1bEpdZ/M362V5ZEi9hV77HnNA5dlWJrrw5MR7tP9z/Z3BzQRCljKk5zFt2L/hM9EZpZPTMgl1HadduRezRfKm99MxCOsb98irnPW47'
        b'3hH+/hxnw58a/Z9Lffd3vtGbgvFdxl1bvdeMekptCR9YA6+EQSNSzciFxTIeZVPK1UfKCIPJAi+C7aAVnCWLzcJQLuIeL7s8C1oZc+dL8A3QY+kMB9qDyN5HT3CF2CYb'
        b'N3DYR5ddW8LqsGAvQS3oyyXnloEz4CrczxyEFhEmY1LhTt0HTnn48tMbZcS1DPaDLWCAqSpo04FXyPFmiC+6wMM80LfWZIe94etjTpPXCPcUgDMUSnGAB44hBfMSWceG'
        b'N6bDbaALfzMKaaM5cBf2QtvJBdvhIDhPTl6LAZeKQes6VAyRllBhYE8RUjJbiuBuuZBKyQsC3UJwMFwtFX6PBI2nyKTjzqaNTyfL8842UAwjXeFCTQ9q5+8XY9cqyeFl'
        b'KGj3uR1FB/amj0yPbrcfdZ3eG3DLNbDfflB7Kyzlsubdqluziok/VdqId/qQJH00OAafPTZjdEZE/5z+hb1yfCLaaEAwOYjM9ONP40+MBgT1Ctr5BxxYvJbRy8YExK1/'
        b'jI93hY3ZTzgC1TeM2arrGw16crC3NWMno6mZVrwe3/AoLmu5a7kLh5OM1bXkp1XXuoVSakAc/6+dR2Y6MklQjls61QlErLqbjyDK4LIPTCo7VMYcQOQ7cTD1pCOH5Foj'
        b'9cjV6k95XJJDOXsknqK2c7kWh3pF3fKLYurrz6rv5BPI5P9SZbebj0obR5SnqOl8VFMtPhqHqZ9fjrkM8yapf7t64+d4YRQvr1NPeUqWldrl4tpNHOTljhVgulrbUPfv'
        b'V6vGslqK9U9RrQLLaklItfCGvP9QXwnL9Q16heYparTAYnosP7TcdCRbKS7HvM9vyur9D69Vf58wIWCEiWYnpIlRYc/aUxWaJcpQRm5wzMFnt2Y32tMVmuJqf0p9x/YK'
        b'TxeNYv4W8k+z4shxPV48EJ3Lfa/yR7lZIS8W+q5aHJf5QewiznsVwp/pqfRvRSvn2ko5D/GBX/Vgb9lj+A98a25KHuI/xXDfVEobc0KWC5veTpzNhVkc5jPKaZSnb+fG'
        b'jo29xbc8Qkd9fLEHbHzPzG7setyfMewhG3KW/evnc03+egmXtb5VNe1fWN/6X7RTPMGhbSYkec5dgBVEeim1RTPKhSLiAdL4jLiqdzkplrPwntp1zecUQZGAX8yYQBF9'
        b'bDb3vcjq/G7JjyQnPshfsCj54Rj1Xq5QsRehiM5RlO94XsolKLIMXoFbHiejTANGjCO10USeE4B91djyHy6Tcygh3BoCtnHj4Mtg75Rav1M52UqpblKVV2oaqlY3ebGG'
        b'0zKKIFW4Cakap1FhkdjjfHDRcGjandCM4dCMm4E3142EFrXzOx06HLpUt5yDJmHVmIBsFPwevT4T6/VTV2QpW8mvQ/jl9dRK/qMkCAvKX2JLJ6PfdDK3ClDVvP8JDJu8'
        b'VGg6Jft3RV9zfpAwJqIWVGzuDnWiyCKeqxicBKdR0iZ4A2ylmqrtyPa2NQHgZYDNAc/NTaWeC4LbDXj3RyTYvYCl18Ct8DrZvlcaVijjUPGgRegI3tpMtrztqUUUT+5M'
        b'trw9P381RfZv/bqiiPuDTcl2VKPC9ZdLG9MHKEMqAs9AGHjGfGS1xS4uBjPh3jA5e/sW6IPddvAQaJYwlkxs+VKCvnSWRc6mdhW2x82sUe+4tJFH3ET4QbGH309Hc2Z4'
        b'R8DaUN4c2RyHOTFVyiEnH9c5oSUOcFWWMDpb8ZO1ioow99OKd7ftpF+QhHRdqdzq/aLk/2h0whdnfDat+nK6OP9Gi4uyPlTnLnYvWRq8NSg/+NTfFzUmSVIy87dc3SVb'
        b'ztP4pN3zXbu9bvbh5Ji6ModXvLwGrwa1+rT+MbnixG9uHQBlb5e+zf+CF71//bl3dWAjb39BdWH1ec7559ZeiC6NbTzBod6pCq0IipGKmCW86+BUE7POtgmcYK2zwQub'
        b'iaNGOrhqw6hVsBv2Gthnyoi8mUOhj8FdTWjeq8RTaydo2tt4E+XKGbyxXhxu0lbHVbXpqPA+cIEPz9bFkUKfB6dnEA9hrHshdABnckEbKtIAzpNShVQ0OCX0zXMnlkkf'
        b'OAD3Tni1ZjkRp9YTCcwmpz7Yks5ySy1Belw7twFuzZLyrWpIxHl+fDFNWL5Oq9armpxZc5xACI0ZZGjMl2unUX4B7XPv+kwf9aQJ09q3oTdu7+Z+/dmNAxsvl9yOyrip'
        b'fLcKrL7nHzYkTRvxTx/yTB9nbv3Thn0iRzxk53iDcy/YDnukXJ5zy+OZuz7+XfrDKf2CWz6yezPkQ1GFIzOKhnyLRj1973hGDntG3vaU40U4h24H5r2/5LZnzCjjX9o7'
        b'Y0QS3C856zPgM7h0RDprWDLrtiT4czdUTRalEzKUjq/Q1uisclGhmdqZ73/E5G5SV6xgUbmvDdP+hcWtfcJA6phYzius4lvjZ8RNhGM25xBjDiZ73Go+IXp8CzcRASF6'
        b'fBbRE7DIG3+TwET0HoFOLXtNPpJMVMjsUmifDvbBreAcwNtyp1PTwVYxOUCfUL980ApfhpezI1CfGRAxgmcJ9ZOX+cKWJoYsIsL4ukwdOfRb5iLNlZ8NHX4/1mzVPx69'
        b'NnZd7JnqFx9c6UrrbvWK6F6Ifqt5Ko2kOu7E4E9UttX380VU3BW70fKTSE4jR2vtAC+hiROVA66JwKthAM0V4q/NoXxq+cC4Fr7wGKTfwkJ6sjnfYqQJhCB9NIP0Dxa4'
        b'Ul5+dzzDhj3D+t0H3S4LRzyfaRfc9fAd9fF7wKM8/T4KDDklGPKQDznLWUgnmvBl1eK971o3ziQZTieiGIV9nNGWPIp5pD5qM+b9Fz5cyJXDCXka/mqDyrRAuHH2RuyH'
        b'fBbCiRDKYduhLUE70X8D2j3BqpOgkMEu3EOyJbAX7ONQNSrKj/JbOlt9avBLjg7f4yoTRBx+fxbCole35vuf29vR0uf67qfKZT/9ASX8oe/s/6+594CL+kj/xz/b6GWB'
        b'BVbq0lk6LF1EkCJdpNlFygKrtLA0u0ZEFAuIIljCYl2s2LGbmeRicrkL62ooSS5eLskll1yCLSa5S/Kbmc8CC4LRu/v+X3+z+bCf+czMTnk+M8/zzPO8H6PWlEv3t3LX'
        b'mFs2fcDOeFMrXfH2h++G7jvbUhKYp6Nc+CXi/f2p2XYGf9/WMDxdL3Euq0mNnMvSFKRLzjhUZGSqNm2jyYSWglW0tNCE4k1pmoYoZ8DcTuYkN7ln7jlgZSvj7Etoihng'
        b'O8oy5bFKvgiRl5Prcadec59ero8aTem8BE2Nb7POKImNaMOyMJVN3NyyYb0QJrUFmNQeUa9Ib67j6W1kZSmm1PXVZIHTVC1xnP8DWnsJvm6Y1sgWegg0VYFL4Fy6Zxbc'
        b'LYpjURxNbKt1foHE59O32FLMZ+UE3Nv3XiiiuiPrz+703cjt7mq5UtfM0Gnjh06ZOi8r6qcDepkn9fR8Flukm1qyoghEdMoC7ZgfD6CliyymG2Cbe2KSG2hcTjsUJ8M2'
        b'xIpPSnKcYZJTOchmq+IFqWiOrzaJY54QsvNQkV3xCNn1m9vKRCdZXTHdTieSegIVHpFK1xm99lEK86hebpQaqWmNI7VBjYKcvMqyign3Ty01GqMpDDstTt64GnUiW4aJ'
        b'bOgViYz85B4NF+qYrh9LaEh7ahKfTeK9if04B/VHFXbLxMsH9avLqvKKxBWkBb5jb/0GdfMwtq24tFJc4at+4zeolS+R0qC02Al0kFOdU4kDeYmrKnNqSUApbEUyqCeu'
        b'zSvKweGOcNIRkhPbvvsO6gyDykry1bDpjpIclZLKYjEaa2zaUoG3/4pl+ILPvscFGEsZ1MKhhXGVg7r42zAAHEkmyNjk9/wqchnYAAbjCeWW1RIMvEFOeVFZqXiQVZBT'
        b'O8gRl+RIioXMQbYElRxk5Ury0I1mZFTUrMyUjEF21Ky0mIoKvK5gXdMYuQyPOT67f1xKDfuI7qHIYRa2Z8V7BtWgU6D1/4WtguVzb3IeLaG9WUOfJXWX1HhJgoxpI3xw'
        b'Ap73ksJLhmJuBYdiwqMMtyVwRxUxwbsEX9eTVlbDS4jDrzeEF3UZlCbcyzSAJ2dUYRJdVkVgMRLhpkrEasQle8Unz4YNKeCUB9zhnTA7ziPBG4lbiNUfBhGBLQv0omCj'
        b'hJhO1NTADtgym5rFxHxQMtwFjhBTfSQanncS+euArT5siuFCgRZX0EMYJ+EiuIcHWkWogIgSwQ3WtA9pt56uyB/ugmd8mBTDFcfs2V9Fd6AtFrQRLAXYBo/jMx8GpTuf'
        b'CU/DzStJUR64AltR2Y2aPhoUQ4g9GzY4DSOYdmnCRuw0GAAOg8tsigPPMmALbFhNxvKvbm5UBpp2n5x/u/TPj1eNZYvAQeQPtoILPgyK4UaBVlgH1hM3iXKwHdXmhcET'
        b'1nlhsJ1kT7gliUGZg8PsCHgTtpJafRYKqAiKCvYpbU09xw2hCI/psQYcQ21sNvJhUQwPCrSBSx6kjX5gY7k7hm+NR4INvBCBZBtDsI2VmwFP0n7AIeYUWua4PgaL5rw+'
        b'bSbt8Qvr4RbQLPKXwus+mhTDkwLt4iW0I8QhIahHMpLHIhY21WV7MMDVqdNp7VHVdGoVRfF94i9mOmvxVb29AFoWo4adEgEkBDG8KLAXbFxKG+luNoV7sXF/MhLctX2Z'
        b'C01AmwjUk7ouUonULjxyTn/UfF+XR7dqGtgCL+KJqAHdaNK9KbCvLI9gzWj6wz2090I8uAxPY4vJeqYDvBxGKtMPo52afapL8nUcdOgBW2ytJ/KvgG2BFBmv3bAbygkS'
        b'UZAzPJiI8W0bMXDKViwXJmNrkzpWODWP1DfoEkwhzs/HR/KrfcnKKro+s8IKNKsbwaZAJunmHtBYTCY1C55cQ9eXgokMyKGcJjILsIsNttgaEjqPyS9ExTvg5kAN0rO2'
        b'pTPI9ElhHWxRFUcTaFiKLV/KWcFTYTdpy1eFxhS2vfNZXGxQVYwGHVdmOBNcF/k5rcX0ivrWmg9ktCn1eniKp6LX2DQmotZzDLjLyYaWUg6vANdEAfDCXMS4M/xQsZUM'
        b'8sDUI8A9ETuGlIFzDEpDwpziNJWe2/XgEjwsCuKCdbhIMGo1PGdJmp2Fpnk7Ibtl4Eo8IqYzFKUXxuKugLvp13fjWiATBXlNw29jKCIKuAlcoc2etsBrVCI5fGUGozXh'
        b'OJvS47JMswEdsiwwlw5Z5hN4ZMV5cw967F8DLb6ioOXpiMPHlbWDy2iVwB1OsIZHUSswuFAi7OEiushjWsLLTDJKeeAokIuCSgz8ETFNRW1YwCJtW2s/MzERngKt+AyW'
        b'WcaIQEtbD6HYeMTMdIiCUPUyf9TuMESA6FU9RX7K2x7uTcQL2Va4dakhGicTpjZoAM30S8ZZQT3B5LyAveyJUzRNzsvAJndw3geenuXPoRgzKNBhj9ZUYhd2JQW0I4ks'
        b'oSIYnxSz4E0G2AcOaZC6vl8ZS23FL6xpZ+06ZwE9AjwuF1fVAPb4o/c/igKyEGfSyflJokQ0/JtSkxC3tJjhDddPI7VYLJxC+eBxLA13/ENkIl2LMTy8PDHeA9zCGhA2'
        b'mwE6KHMio/pHwkawHq2etG+XV4CwSkiWzixEAxjDJS0Obp7lmUUb8sOGZI94sN4ObqeomcaalvHhZKFdbjdlBFYKn1y3Ecd7sBvsh5tG48ntsqJxCXzM/l2bPcefJmjU'
        b'+53pleAYbNFASx3lAU9HV+Gzeul0KV65L6GXVN22AW0ubMoJHOdUlQbQA9oh0YeNszH2QBK8hZYtY8YiuBfsI4sHWn7bDRMzwFF4DG5DpADb0W4BNoA3CKaY/Sp4OdEr'
        b'Ad7yH4ONxqCcZnEksGclvZSdAnWo9BvgKtyni37uJvqAdcbk/a+p0XFHowL3g/pkuD3OM4EWtX3ZlHMGx285rCPdPrXKkvLHFLK4Yzo3Oo2eDxewkQmugi64D7GU4Bb6'
        b'6JeTRkleo+s8YTOmSiblnMkRwZsV9Ot5BTZrJc6GbcvRpsrA8Fs3loIuQnp2DO/05Nlgny+GNGOuZFiBa/AGvb5vhw12iZlgI4seiyMUvLAkq4qOrhY4fyz2HLwA16OR'
        b'sAWNbDQHN+B6Qiy6UsMaeAvu00dNuI4+MyMJTjc4sgp04hfbKz4FDeDcoHhPPzZlCfayi0ETXEd+fQm4hfbUrUAG97Gw1hF9akArWZaN0ABuHS3ulo6KM1HxfewS32Da'
        b'ynKbNbxeCM/DRjxClATIp5C1yASeBScT0eTRjQbrqlCbDU1YSx25dLmdaBkAHdYj2pmOZcT4tAJuLCFLGKEqb3gVrWQEcs4KXGSjd+rmbFJ8bha4LtSH+9CbAa6hD9hT'
        b'QSbPEvstFIE9sBFxIsuoZWg/qSfvgR44lZfo6RkPTromeKyB7ehdM4lgIc7mPNhE+ye+zoUNiXPgPj28f6IPB7xO1sZVmVaJwx77J+G6Ya99uHEtKWfrDTqk+uBitD5a'
        b'nNDLB09F+BHiWjpTh+Jh4tLYHvYHuySauOAxNOnX4c1S2Ij6XUaVgc6lhLgsYJdtIjgVh3HotibO8kzwyAXHUCMFlmzYnQfOEDX6V36OjF5UTlCTk/dJbXleKq3MmqUz'
        b'DxxDJDusttoZIkn/uI+SLkVjIINrd7fOkxpHct8prI+Y6+Nox+eY5OktvV52yNk59m+rP70894tdWZ5l7oZ18xc/uuTd6t1q+7q3pOxjievRqefTOOn3lb9l13zw5+rH'
        b'U3+bGf2G97c7Wv8UYzfol5pWdL91+mcBStNTWx82PFrz4YdP33cz8f7gg4HFnXJQdkwQPafer61kOb8muvAX+86m+v53n369wK/u28+S1nYt0c3dNpDQvd3k6RdPimZ9'
        b'V/bPr5rn2L8Xu/yfmZr/eK1I50H21l+enl5cMPMD3+Bb8WCxX/OTng0+b3Kdm1OruUf5Mzja16zrJPXdmtorrevcouR2OR0bfCC3oLn708i2PC3NtI7Pw6KCG+o4mp1/'
        b'5hrYvVl1yEBU59BVds8+Knjvz1bbfev+Fhf8V8H+fK1jaR1QUl/uHPBXj6jgTXWPDQCnvtxIe49VnVN9+RTtOXqdc366nHBWKCv8Qqa5aNvK1AyfT9zkG6axPlX8c/ul'
        b'Gyf+KvmwbnrMW3NtvqueHnNy/ub2zYNn+kPl+YOXAvcI1pzNjPk54dbKDQcL3F/3y4r4LsjuhKz3mWRJn+ZvUzR39JeV6j1MKNBMKWZ/26fhEjFHIY09kybVXfX34mXy'
        b'J/MXxvhl72n5acW0jODsr47dKj1HibV5QTunXAxvywmzM/ns+M322mK9lREFj6PrFiR9/lHt99/pfbxwS/keu4/Pa/8c/pdjnBkPl/hk/+LT9fns9xJsRMvD7Fb6xdS+'
        b'x32jmf1ZyDd/1/sr5+Ha19974HRobUxK0Zahn28dZWZCy/qhQLH+9/xfVv7ypuvTmTMNOvh/KDx5cH3NP/74TPt9j3lO5R/dPfNRXWrVg0W/HrcQ5w3w/nL5lqHo6ZLP'
        b'NYQmBDJjKugA9diWCx6pft74DdtywUYerVS4HIJY0ZT0CsSJMsFeRjJsU1k630CiD3qF0Y5S7uqhQbGjGeAG2mRp2I4GUG8BGg3L9SrgBbDNcCqrWl9bA8kLHawy0FBA'
        b'jLbSQQuU6YIujzhyiGECTnkz0Vp2lQVOrQEHyRGnCzi+gHYFAjtmjlhMC+Bmci4xgwM6QaO3yhNICx5imqEFqxE2ZZDCWaj+C+QIhNbfaiUzwW6t/IWexD8X7WlnkhNn'
        b'VfJwv6oZkWCdO+2wdQuxWZdVhthx4Ahti+1Za0/s6xaiZQTv6olw/QhgSz1sJM8CWCUq6zrQupYY2Bmhje8w7a3bWFOID4HAOnBLHWxuE1urNpGGdLmJ1oarw4Zu2BIO'
        b'7elbR63hQKOQtq3bjNr3+mi+5KUYbnTYIg62wpYn2PEQMY3NetgCzx2sg/tx7Ay0v2M/MtVguIdwwKUqeJR4sq0BjUyi8lbpu8FmAzWVd4YTDW2yTZTqPozlYgOaht2N'
        b'gTyLzAaatoBx5nf8alAHjuT+185ZYzFJWDn5+Sv0R/U/6JZopG6yVY7JppSNvQq6TKSwDrxrHdmDLim35zXpfMwzb9Po0G3X3aev5DnLeX3CEIUwpMdNIYxR8GKaGAMm'
        b'vI8tHHodY+/wPpjy7pTe9Iw/WikcM5UWWb28rH4Ta5mZ0sQFHxAlNifikyNUkyxGLlLyvUfuukTy6m6JwjtC6R6p5M8YzRXY7dI1vWeGkj9dLY04hhUr3aNupyn5ceMf'
        b'LEV13PZT8mPHPyhQuk/rqRhbPXlQpHSffttYyY8e/6BQ6R5+m4FKPHjZ3yhRukffzlXy4ydsla+SHzPhbzCV/KiXfiBRukfctp+gKvLAbrJ+TFSVWOke1oOaGzlpifE9'
        b'n3QQR6p66mlpavYwlOLby5zlZp1e3Q73zAMHhJ5d0m5Rj0ZP9RWD29I7zN7gxL7g2Yrg2b1pmcrgLKX3nF7h3DaNtup2g35z67aC5jV95m4Kczd5/pmlXUvvmgeTI8xw'
        b'pc30XkQLlrYd4XvD5VndsV2Le/JvlV4pveuZ1C/07tbosmlj7zf43QwD1vayQLmrwkGEcfpiVdQpYx7T7NR8gE863RV8d3ls9+yuhLse4T2iux4xtx1uVyv5Kf18mw6d'
        b'dh3ZdCVfdJe/uEfzTYfbBXeyFbGLlDMWK4IX3+Xn9+bm9/OtO1myWPl0heNUpSBMwQ8jtaoOrcwuW5y16Jml9E26g0Zsdv+LHlnLNGTVnQZ9giCFIKhHQymYrsAvA119'
        b'uMIxVCmYqsDe++PrSFb6JtyJJC2e9NFoV6NUjxKUvjPpl2qiMuhFnPV8R2YqfUeIflx1iUrfuOEHY8ok3OEofVN6U2cr+WnPF0tR+ibemaPkZ/bzLYeEpkKzx5SpnfkT'
        b'ytSUj7F3puxJ3JkoC1TwhK3qvjG6tI4c78CvhkyDl8znYGk2E5/KMUvm8WE9OfapnG3KYFhgyL9X8aAhevI2DVdKrisaa6Q7cihTQNHgBOQ4BitzqQZN1XEMY4wS97+1'
        b'9ntOiSugxitxXWgl7mdFtBA9lFWVlLawnKLPaPAo+RnCK6ClrAq13oayAft9yCkhP1QMWmqxcDKFmgLXO9MCQl0k2C5C2/VFVJUf5Qf3gMuk9jYjLaKDeTB3RRKfWkMR'
        b'Y5vvVtGJgoLa4jDbNFqYlwtpZbJPRsHKmlgflXJxPzgfK/Jn4zhcFNi7Og+JfNtI41jg3FqRvwZ2KKeSKXGCD6kkWaxBIsxTMwqLI5do0zW/EcbF3Q/mpog93l9rR7eh'
        b'2suIJFKrcjxE5dV0zm+m6FOIlXONsCssPrs8kM75cJYeSSzPWquXaJ5B57wu0SVi0hJRsYdzTQCd8zcHWnYqd1ytd7pQ9UOGhXSTuL5LPd50nE8RuQ7syAJHkFgNt2Vi'
        b'/QOnmgHawRE0ftdBDxnQJLh+tsjHh03pgNcZjhTYma5S4skXOBDPC9niVfZt4WW0fOYH64sQ89kAj6tkqeuggZ6Xs6YBcN9KDx30k5fQB3FBXeQBy0UC94EO2IpH8DL6'
        b'wFMOtPpkF9hiC1vgXktEwJ6UJzxHY5e/voD2MKG0lxWzZrrTp3hl8ATiKVu8Ea+F/+MgUbKeAhexOh9LePDgitmgJRt2o6qsKWvEXxElSnoqdv8ftX3CzNaRsITCWnrK'
        b'15vWpHtieXVVAQM2M4xhC7hBKwsilruDbeAmhnCgajEmPKEEuLsgBJyYg00IllPLK0AL3fOj8DwazRO52HJvJbUSvAGvkeWETIqliFbzcsNKi7MMa2n8KmX6g7yfNMi7'
        b'xIgyk7wzXcmS4nOZnls7Lu7+UwqI4G38PmktO5Jdp+NpfzB2m7PXJ1+9N3PItDQ3rbon8tDUoLB1D+1q44/96f2Gr6f4/aE/Zt/H0i+/mVbj/M+ZT+J3tlZMOc3ebd44'
        b'EKJYGHZifsp9d8PjAWYej7XusQxC0vbzy5fKPqS29ldfenvXzoMB608EXrOb33CF99bTjbVub3zkNu9B7UpdHwv3rvsGGVW2Brl9olnKLwcUy7mn/h6/bN5gaWT6Zocw'
        b'u79t2HXpSOWHru96C6tnfPy0vyuJtz3yfnPhkvtv5HxzY/fiJ4rpCt1ZH9QG7T/nu+RC0Bt+10ycMsvXHrr2G7T+0uSrh/blnzUvzy60KX8ranVC6neSiwWfRu0/+qTv'
        b'/v6HDS3vvP/GO+m9P62f/Sf2e6LXNPaD4EXbTU99/Wfhn77fvYJx7+zx7Kxvjq/YeLU9furDqGkPtX/Ym+/98NnW92xmm8/8Vfjz1uVbbv79xx1L5GUGB94+kBhS7R5V'
        b'9cGZ9RXnfrCudy+7/8tuG/mvv3Ke9q3+d4dAyH/ijolxE9yf/0InFY3KZaAVbAf1RFZJyAe7iMFfiqcb5rgvMgOQVNc6zYYw7LAHNOTCRju4fQwUIayDXUReSY83V3cT'
        b'QpLMocp40EG75qxHFW3D8kMy1u3h6HtJDKoK7jGOZIHT8IIeEQFtHGZhXP7GRNiGTcwYGH/CHtabPcFOa0bwIJFTJnCuQvIlPAP2FoFT4BQtS16TJCLZaSuonxXvjrW6'
        b'pxlAxoVnSC/hDoP5xM4VvQIHia0rNnQF7U40pONpeMUA/wyBkIRXF9LnQmZz2Za5JUQWFWBbSSwHqlAk0ZVBmU83dsKR8lrm0b/RuArDcCLpDUmu3Sr/KCPYYktqWAta'
        b'y9UlMzyWoK2CFszyVtB2gBdhd6l7DbwyHu4SysJouMsmcB4eVBPcsNQGT3jRgpvhXLo3+0ArH0lRcR5eXvgMkEGthJuNYRcLtnBfo+XEvfCAoZprFdgDr6vcq7BrFTys'
        b'wtgoQnOCxMkAgIMGbE/kUGwmA7wBdk8hT2NWgxNqFn2giQlkcEPZQitiiAxOmFWMtR20BAdp80F120FQn02LzB2ckLFyeALYBBo1mTQmeb2rJxFE1YVQPrikJofChgwa'
        b's6Qe7XbjZEh41h7UeYD1tCXiZbC3bBRtfR4TvA52o42kY81LeW2pwUwMsrGTwgqDUZ4I3xM5UotFY3/PN6d45k2VLSEyxs7wfkvrB1wetnXu4zoquI6y2XLmGc0uzX6e'
        b'BfmYq9juPp4QsXJ9PG8Fz7uboeT5dft1i3p5QegxDT4pd1DwPO/yArsd7/LCexwHeAIZ75hlp2Wfna/CzrfbV8kL6ONNVfCm9kQqeeEjtbopeG59PB8Fz6fbSMkTdc/o'
        b'jsIIIi/+0QEk7bL7+G4KvpuS597H81XwfLvtlDz/7rTu9F5eCHmOJYCWWXQVcvTQQ54mRw99x7c4vdvxstdZrz6/eIVf/B1XpV/6Xd683jnz/tN8Qd1Od3nTevzURiBQ'
        b'YRfYg9of2seLUPAibqOeRuHHVvIK1Kk+XrCCF9xjrOSF0WVsO2277UfHa4aSN52eiDG/E9ztfJc3oyeWPDKnu4yEPZqHV6I+28t9e3mev/NsZJ6Hgqx8jR9TVkKTZ8EU'
        b'z6I5sM1VaeLwJMTKyGkolDIyHSaPe1wXRDD03T2uc7+JeZ+Jk8LESW5y18TjgUpG48jZfa5TFa5ThyXQnHbDu3xvedRdfiCSMNm3dK/oPmYxhDE41J9dDOMJxTCNxVgT'
        b'RqZ7dJt126LucQX96r9ibrGntrlWxj6m36mvNPdqYqvAUmV2vTzHEcPWXp5Tv6PrseTO5G57hWNAn2OYwjGsZ47SMUZlzp+Lgy6aWzbpPm+18xKgLsRkZwymy2Esf4x7'
        b'174bFkB+QgLIPHMGwxgb6ryS9wjWZAoZhIMXMr7GHCnxa/oa2/YLzccBtxB3xQpdbH3ihC84snyFCzZo0Rr2GBv+hk1ZiGcUjdiCPRSI3S4xoSQWbsQIaVAvOzUyLTI5'
        b'O2Neakz6IEsqrhxkY7DKQV3Vg/SYjHQifJER+O/0YM9htZjjQR114/bA41nFJGAtP2gY6js/tKd4VgNcl36e3xMOk+ffEP1Qg7JyHOB69/P8UYpVYEPSKBaLCGOxBBAs'
        b'FhXMigeGWfFSB15xwykeJMXUeoDrSoOzmPo2xDzVYul7PdVh6qcynmrp6k9/asHW936mp6HvO0Shyw9cln4046EBZWPXyess6rXyHrBxGHByHXB0GXAWyh1l89GfLgd5'
        b'vmzx6BdHFzlbFjr8x85ZVinTG76zsZM5ts0fsMd3VgN2jrIMmc6Ak5vcX5b00JZrZTxkz5ti3M+zbpcOsdC3BzzL9vQhDvqGAYPtOkWdUpTVa0gTp2hRpradJriGIW18'
        b'r0OZotwyXlvCkC6+10OdbZfK/NuWDunjewPK1KrX2nfIEN9wRwsb4XtjytS+Mwq3ccgE3/NGn5viezNUuD0PN37IHN/zR++n4HsLytSmkyWLblsxZInvrUbvrfG9zWh+'
        b'W3wvoEwt2qNk7LbQITt8bz/63AHdP3REQ467gi1BUaZHLjjRycXKAM19BoOysm1bJY9X2Ab22U5V2E5V2k5TWoYP8C3bkuRmCiufPqsAhVWA0ipIyQ9+yGFZGjQkPtOZ'
        b'wdB3e0Th67M4po++1UMKXWhXD+KvfQRugusQ23BYnZPlUNwM1nxwdcoYKV1X9fexPYbcMFKD3GBgoA0VEIUh+l+TQCsYjr3LZ469P8k6oUlXqE3lWxELUO0GwwJ2PrtO'
        b'e1hxMJ/NpMQcFVSH5hioDk6+FkrVVkvVJKk6KFVXLVWLpOqhVH21VG2SaoBSDdVSdUgqF6UaqaXqklRjlGqilqpH9zjferhX+bz9TJKmQa4EomOpBfXcv3xTAhVh/fyT'
        b'56ElXliP2cvWs0Lt+2HGdka+TQOTqHhoaz1dHMi1QDufrzbuhui5doMBmY8pdVrzuaPze9JiuC5iscvCIWELOPmWdSPRH+YbLTfXrhPaDtLYVIkpMT+3joFkxDjBw48E'
        b'ecU5UqnANbVMWlktrpDmlObjdV0iLhWOKTPmxi0DI0PSsRtx6NayXGlZsbiSDriKg1YWl2ELTBw0U1xeScdtJeiW42KJVmCdl1BzUDsnv1oixZaZg7qqr8TAUouOo4eS'
        b'WfkF1YOsZaUorUScL6kqQWla5ajlNWUV+XlaaqM/EkBjHaVuVD8cR5c4sOHhZ6OB56DB0yCmz/qqMBqIXDePRMpdrU00bVpqmjZtNZ2a1hptlaZtXKp65Ny/PmRNAAEa'
        b'XyqplBDHPRUQ9PBsSEqllTmleeKXBwAdGbpQFYDoaDBaXLPKPBXHlnWdQRvFogwl4grhxGEGIwUqC2EaI1pQVY6dqIME+ZJCSeUEuKRjW4FnbaQdOALvC1qBHk/WhlJB'
        b'TnF5UY7nRE0JEeQVoZ/MI3FuJ43jqqKbiceEfipwTUbkipokLv0PRiTg90YEESwdEjQ6NktQnJMrLha4oq/qUVaFXuPilxKikE7YirFNJ2Pr6qc2FBM0XtUQ9NKECpII'
        b'ahSuZaZ30kg0XHpY0NufnpNXhOPXkjaR8Mbo5Z4EHrYqt1icr3q7x9aSiq5lpXQkXFQTQYdF9/RIqdaEicc4vnIkPnGOaphzxZU1YnGpwF/gmk+HMBWS5SV40o4OLwz0'
        b'sNN3Akm+asJEvzdhw6uJKg6s6k5QIS6USNEIo1UMLXaEnDwEVappqyrF8Vh/B/D2eYcuQ1q9ftUZ65kb8tnlS4p1KhdTJKJhJGyFN4kHKbxCvEhVwTlSiRupKvgH3JI0'
        b'Wz0I4MYIPS6oA7tItR/k8ChXij+VilhipWNhTVVNR4kOC7BRHbw6P/kFlWKLzkz1ejvK9eBhuB/SCvtT7lgF3jCXkbrE4+6UJKoqDCXOhLvMhh1e47081OtVUyKptxb0'
        b'gAZd0AkvlpJaM3WwEvzHGC3BEr3r06R0hFLYWeg6UiuucxrYOlxtvHu6em3r4A5tsBsN11ZS3RlNfIAQ4cpZskRvW9IUelDhtSIoH6lPG2xQayZsGFXbjWvmJV1wyJA2'
        b'1tUOw0r9OI4ud4nHACuaIjbpReDS0pFaI9DEjdbqOqyVGlPlVXBCFzbYUJLN16LZUuyAkO3atfGDRAOmnZ7Gg0dHl2zd9MjmfHvSZz2i0o+v/o36Q1RtvCJuU+rryVop'
        b'ho3gt4s7fmRrCz8/ZHKdverEx9ourruz++vch9zOFL4Wzlz4WebuP3skfu+1847kXLxyg//bd5+0xor++Of3n/ztWP/63LbcE+33txy4FbFTctinyapllVP7/ljp3erT'
        b'5w8se/+X29EF9e89WXvp8bZKflxz/LXk0NV371xleJVZrpvqn9Im1KF1bi1R3iMKREQxr4FWlQIRnPakcxyB26vVoJFKw4aNNxzBDdprsIcBz6pXQkfLsV1UBtvY8Azs'
        b'ZtPB9ORwD5SP6iIRpyyn9ZFEG8mXqkL8gbYMdQhBeI0pAqeTyMMV4AgTNIJb4ISaqnSKCiXQIxSeAY3wOLwyRul3CZ6nEYsPFUwb1ekemKZS6xKdLmpaA63IPJy3QKWB'
        b'nG9C6yBpBSTYKnqC/emzNMBNmrX3hOfhJSlRUseDnZYe8UmE1/fUoJJBnSY4AC/DM/9joZdgDhkN8xZjsZbMaXDeh7VTKAfnzjy58FCp0j4AwyQNmJg1Ve5Z27xWaeIi'
        b't7tr4k6AlWYqLeJ6eXH9jt4YWMmOZOozd1XQof0i75p4kmzxSouEXl4CkjI70+X8Q4uUdiIMtkTXuaZ5jdLEWW5018SNZI5VWszs5c1URbXZl4hyatM5lzcvbwmXoVqd'
        b'6CiBSosZvbwZD6xsSZZXqtxOeMym00Zp5/v7WR2cmtj3uYLnA6GcxVqJc/hyHl8u4MtFfLmEL5d/3/lvJATKOAfASWZIiHhGKV5cf/sRO5pOYTDSGDgKStorBZnDy1an'
        b'hi91Vjfsv8KF0ske4TEnQ78Z7cIw+E0m6oIahhHN4Q6ziRPALP3nuFCqVuplq/GgL9/OubidB0baaTOunYTPGm3lf4MFpZ09zJW+fOsW4NaNghrZ0q0bZgKfG8T/qHkF'
        b'dPPY2YhjffmWLUYtezwCbjRv7zy6hZZ0C9V43v9V6xAb+/Kty8Hj1ssYHjfXUfY3ZzzWl/S/buIImNYwA/ry7cwfO78WWD+pxrn+z1o2zM2+fMsKn28ZmtcRrlitZUIm'
        b'0QzTOuIRh8WUPJZaWzD+OfFYJFEttdU8jzWIMI6jcGiTyJY4rqV+g0GB3ogfsub/zA+5UMh8yjGeQByPzM/HwZZKxTXq9IHesZcKuxSDhCc6M9aF5OTnI1EBCRw5KtmT'
        b'RE/C4TI8BIUVZVXltDokR5BXVpIrKc3B4Z2eqxIRqtsIcpybh8BNHfMO3RNYPZQpt6xsGW4qVtkQ6YhuRuXy8lfQIIz8UKggvawEy6G0ZgeHDVEBzuXkllXRwaQwBYjz'
        b'Jxsb/C+2rEIgxkOSLykoQHITWqloiW5sp1TjTQJMoWErVAVFmUCYwv+QgJiXU0rkwxcpB3wD1URigWtZOQmeVTy5cKw+rrTg99wCIXCNzK0Q5xWVVpUWSlWaAhIaZcKG'
        b'jtKBVCopLCWk4EXGRK1iVUg1gUS9VxIkNCMBecJah4VhXzLJgSEjMjH+JV+hB9bFCfLFuZX4d1COPCSuSvBN3mRiPKFKCSkvFVeSsQsOeQmaicVu2kT3N/5VkYiloS9N'
        b'c6itkkpVBfS4k5QRnYJrellxMdYjlAkFbm4lWFGDurPczW1SjQ/p8Zga6aTRKmei4S319I5D+1Lpq1RNI/Wp1AJlUtJhFXrfS5XHLyddWv119RIkj2g8yOtblrtUnFcp'
        b'IDM48TuQPis40MdXpXfFalX67fR6uWaMcbsPHad5qi6T5IlHCH6GuFhcWIDzCQULfP0WvUyVfqpprBLT3ZGUkobitz46Ojl53jzcs4kCzuF/5TnLS0i4OnEF3vg8BCVo'
        b'nEf0K2oN8ntxg1TTg2E0xs4XThmrbaPfFu/hN2XCZtHs3wzUSfzu4zrQz4t8Jv35MUAHw7pHtdcEpaI3slQqoRtVVjDhr+bkL0WUQcYDFyAx+3Jq8feJ18aJtZZjKpES'
        b'taskr6hSUoi7Is0rKobX0UpeLHz+nZ20Tk8Bopv0SnEVWlxHKkAULBGohgitUCXojYvJ9MzIqcwVY1V2/iQ1IXKh42AVV5UsExdNPP6eAtG4bOTXcqoKVlRVitHOgQNG'
        b'CrLKKqSkUZPU4R8qiKwqKBLnVuFXDxWIrKosw/vbskkKBIQK4kvzJdUSRMzFxahAZok0p3KFdFzPJykdOFGTX32AgiaqRqLWrJJXa1bwRPW92riEkIEcHfrfGfkJEzNo'
        b'SsY653HtfmVKVO9+QQXqjSse25E25eSuqCoUTk5+6sUFQU6TE+CYjL4hk+VEZFbqnTM5SY2tJnCyagJfVA0iipH+vaCOYPVsk3YtZExlE/Rr0g1NBcSCVjjVN8IPIJ4U'
        b'ra3DS7lrOr3HTrphj+K8hAqi0I2AvkM8jmsiuhWXov8RmQvwHhQ86ZKrhhAzthq/cdX4vbAaAiZDbxlZkRme8dEC18z0SvQX7zcBkxYbAZ+hi8ZkkpUaJwhc0UuuInE0'
        b'7ZMPQ1UFYpHz0G4RpfrmIVDj7WIy0wSuc+Dhogr0kqK2+E/eFDXcm9HKRpJVjRquSrqsqkL6fKNexO5Nxl4SVvLlOb8RFi1yzPHRy/EwBMknVJCC/wgW+PksevlifnQx'
        b'P1Js8tkYhghSsZCqeyyMv4gOCH4QKoL/oIzP55t8FYsTV1SUesdW5FShS7GXd6wEcXeTr1ok++RrFa5n8vUJ/8DkC9SLfhmtSjFFiAlDa//kSxNpG+LZ8iduxmSDh7hY'
        b'sbgScxb4L2KwAl/I3+WW1YYKsLkC4p8KMNeKEtCYTz6puBAGZqJL5RQL8M0LS+RJKvELia4vZPdoNCqck/5CKvbAfLqnyDcwEFHa5G3CQFCoQfjPCymyIAf1NhYtKi/K'
        b'RKCk0AzhP4IFgZNnVC1zqiXuRRQ9DHIVKpiBvtGc8AK/oBfmH3m1SZGxx8MvHO9h6CxVSXp+Jl+sMWAWYtFmRKag6Zl8RcyV5KEK46PQT0/wRv5O1GrVEW0/h0XtijVE'
        b'35boBXjkqjx0DmTEjIUgEcF6JtgNtoOrpJRvMYd6spqHEYOLmRgMieBoHIuEBxKxQXsXOKnCRUnKIPn/EmVO9ZgvxkFawsxyxbSLlRY4kUMDpcCNxpSXDZvGijoGbkYR'
        b'mClvcN1IDWXqki6palHmKoaV6BGH8smZaugynaryxKo+uAHscUeZE3DQK+xXAE4mJNN4xxQ+i0tzWEnV+msXws2gneAy2KenMN/SoIoClueYfMSvcOLQh71gryVGlHke'
        b'3hjXFEcfaA3DG8Oj4CQ5RN4G2vWEWVbkREUSvuEPLCmTQVGfRfN2p15LgRHc/dM6skNcpvnzDsuSNx080vm5y1dzIvmbwdnPos+l955qrGywUcz7t8PfW7yFXsK5X1fe'
        b'/fOfv/12lVk298aRi/Y+T/fufssyY9bBvi2HFrvHefl+40752fIWZiZ+NOtb0c7lu958GJAwI3W/XnrfY0P+vB2HvnzLK/PON0NrPuh6LP3bv/NvtB7eCt/N+dlb3hY6'
        b'bcW7N/YYLv3nFztPH9w+f+fB92d8V39cc+UX34b9Y3ftD9WFIt+LIaW+xzxDTs5wfLvxk0fJtzbf+OXk/MQ8m9Kfmd9VzK/TMj8T+I5tKDdn04J7G2e2yr88cG5LY9YB'
        b'K9/Qi3P0A/pjPyj66retq55qZpyInnprh1CLHFKCU1xwejSYmQaaj+1Mz7hyErTUHF63IMg44IaTyoceXKog5VjgbJw73DwrHpxkUxpgMzhQzLS3hwcIXgB4HW60Hxug'
        b'xhRsggfhGbbWIssn3ihLNLw19/mjSdW5JNwLG9XOJk+Bw+RQdO4qcwKnXJg3FlCZgCmbwYv0yekbYL1YiolgOrzp6Ypzwh3YNb+JBbrByTU0pMD2XHA5MSmeYTSVYqYx'
        b'3LThMaHh/zJ2I35nBaPu8OP8O/VGFN7DHvHxqmilqTaUwOOurY/8NRxoxrKtUmHiMGDp0u/i2qaHwUIdZdWdHt2se+b+Ay7uXendJt35PYFni2+Lbs/oDZzZF5isCEy+'
        b'k6cMTFN6pve6ZLSx27La9fotbWUa7WF9lh4KS4/m6H5TG5mjwtSZ1OvWhh93hLaH7hvJ8Dk+lpyutIjo5UXgoHAL5SG9ZgFNrH4Ts7b8PhsvBfqYeBFE5z5Ld4Wlu9Lc'
        b'o5tz1zzgYxu3XvcUpc2sXv6sISbL1HfAJ6THsdcn5rbJXZ8Y7OBAvHFNFHzPIQ2WkWc/z7Mpuo/nqOA5ytKJX4SnAn8CutlKXsCPTzQpK6dHFAPVY+Muj1La+PTyff41'
        b'xEIJ/3qiRfHt0DMjzwELFzlLaeHRy/PAz4w8fyagvcDPLEpIQW3baCYFhdpR01nQTysqlAVDOej7W0ztaD7rLV2taBPWWyYc9J0+cjWkj1xHjxSwI88rufWOI4LRM9cX'
        b'EsFSlhoW5mxLBsP3GYUur2JijyNdTRzDgwDos1UxPDgNVIOGCkv6fx7Ho+JralyoPtvn9jYnem9LW8zRCGQSXPtiGfs1GnweNmSlSKswxNU2NoVeasbystWgCe6gXX9V'
        b'YCA7/HXRaM2hYCdongMvhtDgWF3MknS6HINgUV+j4AXY4Ep+a53V6lkUawhvSyuLjc3pmizhAbB72FE3ZqFYC8jonXIvbEF76rBr73W4NQ9eKCD1HFmmqZXP4uOdsviR'
        b'QTDtcPuFMbfcjRFBUeVLkt7iBNNunN9XGwnSKZKoZ5tnROd8a6Ve0kMGIs7UJR4D2AcY51yeru/FYtKJ72aX0DmXWehyZ1OuFMVdknRNO4zOab1MN6yATixeVVNEJ36R'
        b'oSloVTWJI7RRoSJthDtd01NTU9EcuU6JpsD6+dp03y5Dea7Ixwcj3em5w8MUXK8HWuhHspXwTHoqhbFjjlLwKjgP11tmkrGN1nptjEcwPKcBrmbADjKMSdXgCPEHZjhS'
        b'XFOwcxrYSbyxtadL0ikcKRTuAcfs5kaQzNpwO9glIp7Y88A1P3AZbKOR9I7BS2LYQhx7wT540BM2gC7CccyHe5ej+Rjx4u2aTzvyysBF0uy5YINmeqoAA22dDwLdphqg'
        b'cy3qEQHh2wlOsca58/plJ6TDA7S7LR7oeg8ts11MAX5P9SqLRPSYnhdpGc9k0IlHDTLpMa1BO1R7Oh5SCm6g3Jxy4PbXSBUFpqYLI6lUTMhhx3jedDxYM9ian54KZEKK'
        b'CoVHhat1YSe8DjbSpHoNbM+R6ovQmDF14UZwAgP0XAcXJX8/ep1J/HqDvkk7kPFuCvThWk+ND7p6d+PO1jQzu/DXHdbebv8ojiNd5p35RYP0iE2PIPzg2vp7a5fs/4PG'
        b'550JcUfmPtpifeuZ379W/sj4oOm2nvFZL+GQremPl0qq/wL31f6bHXe4rkr+Rda3/9Q9Kzls1m3Gc1/hsr7V7ecFs1gJ1icTqJovO1LFto3rj/t9yD00reVmat53id6X'
        b'qUTfPczu6zxdadaddxoOnhb9+I+sgoeX+z/y8Mq9/MvK++LggD2NDnX9PitD2qveKeY7L1/05aELwVlHvs6YPz1Dg5O58PP+QLeQc5+8e271ftZHTt/G8e937shwqP/k'
        b'/K+8NFvzzHfWfOhuonE/rN/90+U71sza/HXWt3+jZn0V5P9U8EvXmQc/+sf48iI/E1b7vPH26YNztq51WLlsVmT6jYGN6/JK717o7okuaiv7cbnjb6dXu380u/DP32z+'
        b'2jXst9+SxAFXc5qUGwL2hh5gxJ752ubsv9jeBbtX/aT8evsh6+r2Uu/adf9Qmuv/XPnJ9UAhj7AloBMeRxOFGBO4Z+aEvMkoXwLOFBFWSFcP7nEnzA56pAWvMUsQh9ts'
        b'SoMXBVCwHjG+SQyKrcO2Y4ADBjE037UeVb1+NI4DOMFcbLo8VJe4aa4CV5arx1XvADewP3BoFY0rtM4kM3ECX11BDAecjNQG56MJ81ZWjZrRSJueBYPjxPqs3JOOQXsw'
        b'TNtIOBqRBnvp1oLzxBfZ3hjcGjGPi0kb9dGdX0q7kJ4F5+CxFFfiTjzqSxwcS4f3q0/wQKUzfMa48BKTubXgFmlXcD6H8JSIoYSImyfATJedaL5xszE8lzjGedcAbGDp'
        b'Jc0A+8EGMm4Jlubu4/x2p5eVWefSftSb5uQlqjvtGqxmpcKL0TGIgSSt2xmIYae8E8D+Ubdd2mTOFWXBi0Z6KmwhPrvEJg9JEQeIXd5Z2Ez3frNx+lhvXFgXWQbOxdK+'
        b'2PvgYezKi4rXA7m6PzYx3JNqkfmzhbKECQwQsfnhLS48E4xWDa2X5jHwCiQQqFt14TDlK7ijzIU0O1+SR8cK7mKqcJdsqSmWTRwchFC3X+DYJ/BRCHxorJc+QUhTHI7G'
        b'Ubt/Gg7vYS2Qme6bL7drX9wU+8A7CEf4OLG2KabNVZalsHBX8Dwe8GxpJ05ZxbGazpp+vmU/30Zm1m6ISvfxPRGr1434Pf+7/Gk9vLv8mNs8DHCfcWxe57xuhpLv18cP'
        b'VvCDe4yUBEymw7DdkC4kz1HyfbqNu016+QH4gUG7gSrwx2wl37ub2c3q5ftj96e4PitfhZXv2Kp6ZvRE9fIjyPOO5PZkJd+tj++j4GOXXD7tkssPHt/AiB7zu/yE27ET'
        b'phfdjuuLzlREZ/ZFL1ZEL+7NLlRGF71KTmu634s7F3ejHgT18acp0JCgXkag8eo0kc09ZK3AMU6syQiqPrgD0cQ80UBWIWf08t0mS0SV9PNxQJahAEsfs8eUpav5s0CK'
        b'b9Nc3VakNHf5IcjSVDhkSNmFDsUyKFv7jqL2ItlKpY2oSXfAhP/A0fnYzM6Zk44zqXmSySHd6nMKVDhhh2B+aB8/QsHHDsEY92mUFoZJYshI2xM1T9vJ/JnxaPPk7g9N'
        b'tJ0CEV05NycP8Si+dZPe81E0XmzlSKJo/P6L8DlrNArasxjbV/RjnYVlgsfUuFBoI6F4SewWjgoSna1yssIh0TRG4NBHAxv8DwJWVfwwnt9+PriBZkoVRgpYjdbqU+5x'
        b'oH0q4odS49B2hXYl0JURB07BBg8voQYVB+s1y+GpTMLAhMevRAvhCXB5GrFtZhUzwOsliOUj6CkX0tCOR8BOauD2Wrhvngq6lAOPu89iUow0cNWKQozba5IvhStZ0i/x'
        b'RDS2b5x9Vgf4cG8k5i7jGRk1H0w57WXw67qvvl3Y65kea3q8yesz43LT6Qenf51jaZq71O9z48W1z/7yyY0/TluxrmTp0I4vwwvE68WVbZyMbaH31yQd72lVhCdscqv8'
        b'ilOSeHn1otk3QjJ7D5Qvrvllf+73byzTCDyX9tpHrm59IRa9N8rfNv22nloQm9Qq3XD1e8R6XV8i3lqeyOaWcU9vLjf45e3ed27+enDm8cPb1w/1/enR3+ovGWl+yf/l'
        b'H7lt0q66RrMmXYcnb/1dmfKX9K6+XwYVCb0GR302sQr07Jy29v5p87GmzuvhDK32oLfSnYSGTzCRLgzIQyN9QZdEmGIHMcBpcNqWhkWoLwanCfwF7WqpBRsZi5ir4a5c'
        b'sruVITYcNmbA8yjDZgxtkcK0QvO2nuxua4BMB+/ZHl7x5KERaNOF3Ux4Paic3j3PrwZXEVdxoUalGIGbwTVtcIwJDuWCE/T21aRNJXpgXIfNSWjjX5mtG8GEbbDDhOZJ'
        b'LmQhcadxrSnc7D3Lk4n3dTe0ObfSiA97o8FmOnoW3JEL5CPRs8CGgmFb+BvpsHEZzyMebkOckMZipgPcBTtJaUNDXXeCOuEJuuB2LyET7dwdLLARyME+GtZjE2yMTuSg'
        b'vRMxDt4pHEojjGkObkL6abYBOJM4QqjaPGsGE3SC1+EGws6Aep/ZsDE0CG5TjdoMJj8c7Fdt2DUOmJWyTFQDVgG70W6PSzrMBz3uYNNSFSCGBpAzPWBz1H8Ngzgs8dML'
        b'kSbB9BpZiKQ51XRArZ8oejtOsKN4ZnuCmoP2hDeHyxzvmbjIZ5yZ2TXzTHJXco/jPY/pt2e8k/Bmwp3Ke9EZH1vY9doHKS2CMaYEWpP12vX2GaCt3MR8T2hzaEtYn4mr'
        b'wsRVbnbPxGfAwk7mKGfJFyotQpui+p3djy3rXHa0pF2njd2Wj9ZmXFaWIfe/z/cZYlEu/g945nvim+N3Jz6wtO4Iag/qCG8Plzves/Tu51t0aLVryXj7DcbVMmBtJ7M/'
        b'5tLpcsyj00Ne2Z2htA/tib5nHXk7rd/KpiOuPU6WsT/lGYuymcHotY58iH/mU+tI9PVnKbbKfMvTOEaH87YOJ8ZEWz36ccWT313v6fGmYx2PQTCYYLRt2WoIaisFDAYf'
        b'hzl+lcBdJHySkE30EHRgDhKsQ2tki2KS7ylC4/FYBjoMSh3Q4CWM+Y8zSEDGSnGJlEYkeDTcLaHR/1BHqTaKeNzWjf9Hj+YZPJojrrx2ePNcxCDIBQ/ZbH3uIz3KwLST'
        b'1RnVtvxs3pvp75rcjh+YYiVzv2JyJb1H+92oJyyGwWwMgxEewXjGctF3fswhCWz09WEaYxjSIBBDGgQTSANLhwGuFw17YBnYkDgKaRCAIQ2CCKSBieUA17mf54tSTEQN'
        b'UaMp4TglgkGSVMV8cDE/dWyE4ZRHWqjtQxTTIJnRLj1r8pB8GzS33BvdOaXPLkhhF9SjrbCb0WcXp7CLU9olKK0SB23sO0P6HEIUDiE9zgqHyD6HmQqHmUqHeKVNwkMW'
        b'wzqR8Zhi8JMYD1m4rmcaVQx9zycUvj7WxClDJOVZKStE3/pRNQP9frvDPX2bZ0yevvtjJOzYPsTfaA99vF1kJ5pJkTwDW+JoSZRD6VswYQvcHi9kpEhutjcwpNFoNm4k'
        b'R4ibP0jZEMH9Q+H6jUeerJXonro/ePP1zTXe4RueaZuXDUY7/ZC71+fBwI/c6/mb/ulVkmZQd6Ds5qerpv7bU/fykM68H2NS5Wt//OfGBxHtuz6Zv25N6vVw5vXpB45/'
        b'dXjhsoA5ywxPlpys/4t45iHZBZdPbgy2m9w2/eADp1sbrv+UdaXXem9f8KcHDyw7wJ//wQ6tBSn3jzT97H/QN7koQbQ3PWHZYL5RrGamUPON9U9FH7d9o92VlPtM1j1n'
        b'qstdmwtrOrS/la4e0r/YPmf5Kb98cWVnzxenPlz4xrezN9l/afj03/2OcUXxQRcOTk278OdcK1FObuGHX4avXP9ayJ3VzgkLUztckg1zTIsu5X/5U6y2p+uStDqR8588'
        b'ux4l73TeUJb21h+azx2LfzN8sMAhqb99sbj85hLdgz8VfnSgOOiTs/vCy/6tXL3e0Khg5t9uL33veoGQRe8lW+AJsBs2IpmNEQxPOWEs+VZQTzYxHbi34PlTjWMUW6tg'
        b'MZHsDMzgBXufCUI+khMKtLdeEDqOfwG1Xnj5v3jd/4MFwpHe1iLIv+dWinFrxqBWdnZxWU5+dvaKkW9kv5uGSPVXtN/5U/qmQ2xNbfMBQ+Mmv8aaNrstq9qlMj9ZTmfA'
        b'vhXy2XvXnnXsruixO1vVM/ts7XmvN6PvGMO4u35JH/Mt2vzactoD9mnLEpC01G2OBL7esBSFeUpvWkZvZpYibc5d8zkfmwlkxi2lvVxHHJlvLmNIhzLmNUU2mzbMeOZv'
        b'pO34A4Uuz1xdtD2fUejyQwYjTNuiKesJhf78sIbhqG3RZvaEQn+GUhiUDvcZs4Kt7f6MGr0+JVf0wupwh8jDoUptiu8s11WYixr0nmpoafOfmVWwtK1QdnR9Sq5DSzVJ'
        b'ZWmkmtHrI3IllT0kD38ciuQztOMZA8a2h/V6PWOVgplK47hevTh6z9wSyY/Wot7SMom2VB1aWA8ys7P/w0OK/xt6wa6YS8Yef020uRjheEgjNIIXPOkMipbMfBkMLj4C'
        b'oS/Y/Yz7Kt5nmC84rhFKXdWN5LAkZksKWFIcxMwm4Qvx1ngdkMrf8GnYvfncN7U1y4Ob57jaf3HjwB+vmvz64/dvR9XGH4nhvv9lYtydvJgt/lPOfX4nXRb3dvq9c2bx'
        b'C2PcLTx/rfTNfrZz2plzu7f9lv3hPwpPrHjv10/Kv333etGVH1Nd9kw7cVok/PxOuKbBoktdd1iBV/I/Ee+pv5LrwuH563lolLvOftNhSZ2vc1tufYjZXPvcbfo6xWeh'
        b'zSblwR8u3/6hdIf9G58e2ez1nvCPSJbAi87S5Ri2HG6ehU/OtyZqUrrgHHNeNpTDBgnJsFIMTyfO8oRncR7MthvB67AjHuPdzSeYeJ6wKxU0gh1wRyJa2erRuoQVmpqU'
        b'gTHLBl4opDWCB8B+WAc64I3E+GS3ZE1Kg83UYhkTaWYtbK6Bjd4aFCMdboPdOELebi/yBJ6Gu8A69wQOxUj0hVspJEpstyOySg5sscJhNrajX8P4cLpC5my0tDbVwMs0'
        b'yvq1ENAiVcugE8+0hU2gG7TCMySHLzg/Devy4Clw1lOl7TOAW1gpsA3IiCIxF7TxcQ5szQD2mjFQ6+vhDTImyaB9LTiBmPo4lZylZ8IE3fPhBQ48R2sCb8ENBIF+i0e5'
        b'KosOOM9ka4ELcN1KAt8HL/tjLHd4Tg801LxWBc+/pvdaFYMyhzvAZXiABba6VdEux7e8wP5EAu6I+0OhCdrLtCiHBwEWfojC9ia4VYpnwILlnYi2hO34SBrfa1KWjmyw'
        b'gUUJXV96R/j/5Qah9uq7kq0iYvjfCzaLMW6oWmP8g+ejy29oGXhsQXFM+vV5ffo2Cn2b/bVKfdd1sf1snU1J65N6jewOB99je3zE1kefT9i2n7JdPmV7fsJ2eKYxn8tB'
        b'q+vo9Sm5DtUKKD3eullqmiXbQVaxuHSQjX2WBjmVVeXF4kF2sURaOcjGyqJBdlk5esySVlYMcnKXV4qlg+zcsrLiQZaktHKQU4AWLvSnAps44hDq5VWVg6y8oopBVllF'
        b'/qBGgaS4UoxuSnLKB1krJOWDnBxpnkQyyCoS16IsqHodiXQYc2VQo7wqt1iSN6hJ49ZIB3WlRZKCymxxRUVZxaB+eU6FVJwtkZZhL4xB/arSvKIcSak4P1tcmzeonZ0t'
        b'FaPWZ2cPatBeC6PbgRSvAUte9E8gGJ0IcsHRQqWz8Bz89hs+kDZiMPJZeCEeex0i11dZlvH+9aamRqQ59aa5bqQ962etAux4lFfkNcjNzlZ9V20HP1uo7gXlOXnLcgrF'
        b'KmyfnHxxfopQiwhWg5rZ2TnFxWj3I23HotegDhrPikppjaSyaFCjuCwvp1g6qJeGfSBKxDF4LCsimKrppwmB5lnCSsryq4rF4RWxTNrFkcSXHWIxGIyHqGvsIQNKV3+d'
        b'5iN2MZfBG1psR2kb9WlZKrQs2xLuabn0eoS/6QxdFR4J/VrcAR2zXnORUse/l+0/QHGb+PcpC/JT/w/w2F9T'
    ))))
