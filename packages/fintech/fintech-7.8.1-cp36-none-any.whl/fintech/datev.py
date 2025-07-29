
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
        b'eJzsvQdYm9fZMHyeRwMBYhjjgae8ESCxt/cExLLBI3iAQBLICIE1bIy3sQ02ywNP7HjvvbfdnpM2SZumfTvyJrRp0zZt4iRN2jTt26brv895JCEZiTi53v+/vv+6Pss8'
        b'0tnrPvc6932e3yK3fzz8TYU/60R46FAJqkQlnI7T8VtQCa8XLRfrRI1c7WidWC9pRNVSq3oxr5fqJI3cZk7vp+cbOQ7ppEXIf4vS78t1ATOnFc9aoKip1dlNekWtQWGr'
        b'0isKV9uqas2K2UazTV9RpajTVlRrK/XqgIDiKqPVmVenNxjNeqvCYDdX2Iy1ZqtCa9YpKkxaq1VvDbDVKioseq1NrxAa0GltWoW+vqJKa67UKwxGk96qDqgY5hjSSPgb'
        b'Dn+BdFg6eDShJq6JbxI1iZskTdImvyZZk39TQFNgk7wpqCm4KaQptKlfU1hT/6bwpgFNA5sGNQ1uimga0jS0aZhhOJsK2brhzagRrRvRIF07vBEVobUjGhGH1g9fP2IR'
        b'TBobvii/wn1Oh8Bff9oBMZvXIqQMzDfJ4Ld/pShrL09/lcm76pYj+zj4iXeTveQ6aSHbC3LnkmbSVqAkbdnzC1VSFInbJ8wSk6eDMpWcfSjkHZYYbs3OI+2kNY+0cuRg'
        b'OgrI5vE1coWcUvJ22qYGX0zQZMdkS9CKarGYw0f7D7TTCcFNHL5GE1RkOz4zHSqQoGCyQ5RPzuFmKMsmbcQS3EJ2xNRBZ1qzJfhgPgrAN3l8C5/DbfbxtJat5Dy+DJlu'
        b'yHHzqhV2cnOFHJ47yFUODSIdItxKjuBT0NnRNPOFjHDcgjtiNTXrVFG006SDhv3Q0LFi3Ii7RlZwjlkTwd9Q56yV0WUTFg19vWUzDHUsGdcMELuOhyXj2JLxbMm49bxj'
        b'yQzuS0YbH9ZryUYIS/Z2hRTJEUqboC6LicuYj1jk++EiBBmn7g4pi7lfoRIiN8/2R6EIhd7Vlsn/NnmpEJm0Qozgu64su8y0TToAmQIg8lDVYPEXYWjqe5Y/TvicvxM/'
        b'e/xBZPKHhH8uOMhd80OKuIgr5a9YTodqhWiZ9c8hnSFc5B/Rryb8ctEa8V9RN7LH0hl+GpgFa9USOzcykuyIzVKRHfh8cWROHumIUWeTG6RdlZPHIXOI/yR8lBzzmO5A'
        b'54inCtPtuUMQnWxDoGs6+T6ns9cOkPSaTnm+hSbYB8JDTo6Sl4vmqRbwiBchvJdcJEfK4uxhkEQ2AQBdLIKs+OGEMWhMiQDV6eQ8eVBkGzAPEqrQLHwA32XZrSvwKbIH'
        b'hlOI22JRLH5kYNkLyZ4RZA+MFlJ3q5BqKX5oH0Brb189sShvLmmTIH4Nh/eKhi0mJxhg+0faKNBHa/BpcgwAdXvu3Eh8PiaLbUM1OS/Bm9PwHXs4nfQ95BLejm9K6dYt'
        b'n4gm4oMzjHOPNomtRyH1lZjCpT8cFYbjQrf++t287vGv7Xh58xjFrjSx9BfBJ86tjAo9P6r51UlpssbfF45VHHhv5e9/vmHl1KkDg5a835X5dPz3fnIouOPxG0nWstN7'
        b'hu7/Xt2mBUm3zonInIjUqE1rFpxMyZmzdeHrAybXxWQGZuQkrFX9bO9bc3cMz1/fNGdv6r8bNv39ix/aXrr192e6n2p3tbSPLq2vWnXqyd2/d6n+/vHQMHu65dW3lBIb'
        b'xU4jatI0pC2atAWNzFPlUGwRRu6JSFNkvY0iAtjkB/H26BwVac7OzZegQHJ+Jr7OkyOwPGdYDrwXH8dbotXKnGiynSGTkIKRZKOoFt/Bu2wjKIaDhewMpHNIbi22w/7f'
        b'EcujfuSBCF8ehE+xXuBdYnINpn0H6SCtsKPSORG5iK/jVj8l381HKi0UTpWB7OvrP86jLwdONFhqG/RmIBOMAKmBeOhXTu4OsujNOr2l1KKvqLXoKFxaFRR0J8u4ME7G'
        b'BcBnIPwFw4d+h8F3KB/OWaS0bgrSSlG3VCjc7VdaarGbS0u7A0tLK0x6rdleV1r6jTut5Cx+9DfdQKy5KbRzwbRzRMFLOZ6TsqeAYG9n4AfROaRNk63CO2Jh27fH5nBo'
        b'HL5Odq+TlJIurWtT0n9ix7e1Ch56SuqBzOu4EhH8iY2oRALfUgMq8dMFNSEDpxPpxFv8S2Tst0Qn3SIr8We//XQy+B0gUFaDSOevC4BwIIQBh0A4UCeHsFzHAWaoVAZ3'
        b'S+exmcp/9m/YkRUiRy/oCAOcaCIOOSk1lBdwjqhZBDhHDDhHxHCOmOEc0XqxA+dUPY9zRL1wjlhA4buHSVDSQkiaWmaqnW9Hxro/fM5Z8yHlwo0pH5e9Uf5h2W5ds/aj'
        b'7P+UtVZe0n8IMd8rv6KtMuRqwyvP6cV/Khq8fPDiTcs3Rh1ImDZW4zdjV2Dhttuic+27Rm0ddWBT4nC0uCrkrcnvK6U2SkbwvRkzojVOghctRSH4TABuEzXgx7EM7AuB'
        b'Al/sySEirUORPEbkN9JiozQQNyeQWxrSkkvaAINvyVZKkQzv4OtHkPO2wTT9wpglFFdpSnFzNr6MkDSNjyCXZgpb6ixpLcYtBdnkKbkRky1GEnKYIw9w5zSh7pNrcWe0'
        b'KisbkNwWuu1l5BaPt5AtlH9wg0LR87ApdgJlt6y01Gg22kpL2baR09kvCeXoR8qJuYYQYbHVzlzCdpF0i616k6FbTLm3br+VeosVGD0LXR2LvwD2jnYpqFuC6CPEtQ9o'
        b'I4td++BsqNs+6NVeBe8G7S74Ujvgy8A7oItnFE0E0MUz6BIx6OLXi7xBF/IBXfZoOqWn8VZjIKxVCyxnSyzpKMpia5c9twofLmREbgo5Lu2HTxYYv7vq+xzrS/UTycdl'
        b'FNBeM8SGRWtztZ+UhVZUGYrumcrFO+L18avQO9+WH1ahI0GyGT99XykW1vY+3o8PAmTgloG0ASdgTNbaRtHky2tGkJuAjTtIh1pVxzAuINMLPBqyXoy3hsbZIugUD8Nd'
        b'pDODgogbeJwi+2x0dPjSYnxHU6DiEL+Si5w4LZ5cERaQ9woLgPIq9TajTV/jAAeKsVB5ACfnGsJcC+PKIlQlZsvbLTZra/S9IYC39HNBAFt8YKlQhWvxjwa7L76XNv7f'
        b'wS8+ISAGfpNjA/D55yFAT+4xIHCDANKF7xlLBt7jrQlQ6rtitTcQMJV/UsbvSLDHvR13Kk6cuGFd3R2ELjfJ1oY8VIrYHq7AB8ME9OCAAKDFLXw9fohvCXDwhLw8xAMQ'
        b'ipSM+DIwSCIHGTBFZJBtTiDAO/FGByAcww8dBM43BoBVt/Ze9crnVt3queoSYUnp4nZLVmpNdi9rL3Jb+/4uAKB8XpULAA6FegcAV3PeEUCCAACUyeUM4hdEAh5SAueo'
        b'0hMEJPn2eDrnT8lZcpmKV8WkWaVSz83KmU+aC4oEHjIL2Ek1h2z4GLlNHvtL1eSiXclQx4AyL5gjH1/zgJuqFcZ//uyO2FoARZI0Iz8u+wjgxmSIGhilzdKaAGIuFX5U'
        b'Vqdt3ntBf077Ydmb5W8YYndHanO0F7ShFej1QTlbGl85eHNRxsa1szMHbgvfViZ9U45WTw2dnBEN7CAFqeSafoxTs6vI6bHunNpkmYB5rkWQw2PwdQ+w4+vJyxG2MTT5'
        b'RhLZ74I4fJM8cKAfB8zNxp0M96yy490uxKMEuZeB3Da8z0algikz+eHkMSVOPYSpcLoTNsReWaYeoJTa6yhz10OUTAEOTi6UawhygImQxx0NCfSmBxKfB3vARz0UiYEj'
        b'FQFqXOC4N8wdHD3b8RC3PFERk21dqIhr5voUryrd4VDsFQ5F+ca/co8R42rO/O7vGm1W5Z+WfQJw8r3yKkO49pz+3I/4GxE3DxyKWDK4XF9+YHlE9cGpN156I7n1B623'
        b'30jOTZYnv5Ei35rwa/nw1uSpSxnxSU4MeS/kL0B86NrNIw9Heiz/RNwGEHCymKXiy+TabMZ2bM11Iyv71zLwIk0g8J0hLTHZAOr7SRuIVNJl/Bi8jxywDYL04WQnvspY'
        b'miHJLo5msI817wszAS9utVkcWInOOLKFcuGAlwAzBfegCprFieWCvmL9ObelpyKk3bX0bR6Y6LnqlXy+hUrYyiDKMFFSBxJCQGmpoPKC3/LS0hV2rUlIEdCirAKAprLW'
        b'srpb5mCQrIwJ6pYajHqTzsr4IEYPGU5kkMj65MSwPiUL1wxZ6KQU0SHQwjJezDk+fLBMLpFLQmV2ymKSG0PqAx3iBDlN2pBMzpfhK5m96CH9xxgaD3GCLxFTIUDnd5gv'
        b'kXQinWy5VOffyDVyIFoEMLwa1C2dZQaEvfrL8Jn6cqOtFgSyWI1FrxN+PqODfEZ7/WXYAr2lwV5prdParRVVWpNekfiMjuRLea7e1mDTK2ZbjFabkmfCxbPvwsr/5SDM'
        b'jqbWbKvNzIfZVURO01n0VivMrdm2uk4xHyRBi1lfVaM3KzPdAtZKfSU8bVqzzms5s9ZGHllMakUhrE0tlF1QazG/SD5vlVXrjWa9Ypq5UluuV2Z6pGVq7JaGcn2D3lhR'
        b'ZbabKzNnzVfl0k7B9/wimypbl29RZ04zw2TpM4uB5plip1VrdWrFHItWB1XpTVZKCU2sXbN1Za0Fam5wtmGxZRbZLFpyVJ9ZWGu1GbQVVeyHSW+0NWirTJkFkIM1B/Nu'
        b'he8Gu1txZ6B8Fe0dlaEVjo5AlFpRYrdCwya3zivifaYkZGr0ZnODWqGptUDddbVQm7lBy9rRO9rTK+aQRyabsVKxstbcK67caM0s1pv0BkibrgdmsprWG+mIUjrTFHP0'
        b'ADnklMFmpaOkU9o7t2JOrjJzlipPazS5pwoxysxsAU5s7mnOOGXmbG29ewIElZlFsHuhk3r3BGecMnO61lztnHKYIxr0nDUaU01hWJVvr4EKICqXnKJKi2o6a8L0Q2T2'
        b'9Gn5NE2vtxgAR8DPooXZs4tVM2phbRyTz/aC0VwFsEbrcUx7ltZeZ1PRdgDZlKsdbTp+e8y7t3g69x6DSOg1iITeg0jwNogEYRAJPYNIcB9EgpdBJPgaRIJbZxN8DCLB'
        b'9yASew0isfcgEr0NIlEYRGLPIBLdB5HoZRCJvgaR6NbZRB+DSPQ9iKReg0jqPYgkb4NIEgaR1DOIJPdBJHkZRJKvQSS5dTbJxyCSfA8iudcgknsPItnbIJKFQST3DCLZ'
        b'fRDJXgaR7GsQyW6dTfYxiGSPQfRsRNhPFqPeoBXw4xyLnRw11FpqADFr7BTVmdkYABvrQRRyBuosgJAB+5mtdRZ9RVUd4GszxAMutln0NpoD0sv1Wks5TBQEZxopp6BX'
        b'CeRumt1KCUoDcAuZC8mpKgvMm9XKGqBYT6CvJmON0aaIdJBdZWYJTDfNVw6J5kqabzY5ZTIZK4FG2RRGs6JYC3TRrUARWwOaUsiUq+6V9ZBwVQn0AhBGJC3ukeAoD0nj'
        b'ehdI8F0gwWuBRMV0i90Gyb3LsfQk3xUmea0w2XeBZFYgTyvQZTbnwJUAd8LibPp6m+sHYCLXz0T3rFZXNmEhpuuBHFe6RYzLLDGaYTXo+rN2aFIDRFHSC1jaI5jgGQT0'
        b'o7XagNpZjAYbhRqDtgr6D5nMOi10xlwOYOtacZuFnKoEIMo264wr1YrZAv1wDyV4hBI9QkkeoWSPUIpHKNUjlOYRSvdsPc4z6NmbeM/uxHv2J96zQ/HJXtgUReQ8x6xa'
        b'HYyGsocx8pbo4JW8JTnZJ19pLlTmJb3Ae2uU7/IW78GK+R5DH+m+uLOvkznBd8sefNqLZANU6S2bBwlI6UUCUnqTgBRvJCBFIAEpPdg4xZ0EpHghASm+SECKG6pP8UEC'
        b'UnzTsdReg0jtPYhUb4NIFQaR2jOIVPdBpHoZRKqvQaS6dTbVxyBSfQ8irdcg0noPIs3bINKEQaT1DCLNfRBpXgaR5msQaW6dTfMxiDTfg0jvNYj03oNI9zaIdGEQ6T2D'
        b'SHcfRLqXQaT7GkS6W2fTfQwi3fcgAEH2khXivAgLcV6lhTiHuBDnxqbEeQgMcd4khjifIkOcu2wQ50toiPMYj6OLsy36Gp11NWCZGsDb1lrTSuAkMotmFU5TMWpls1r0'
        b'BiCCZkrzvEYneI9O9B6d5D062Xt0ivfoVO/Rad6j030MJ44i9GozeVRnsOmtioLCgiIHA0eJubVOD/KwwEz2EHO3WCf5douaoy8njyilf45tqBTiHVyDM5TgEUrMLHSo'
        b'VtwK91K6xPeOSugdBWKOiQrFWhvlSxVFdqhOW6MHMqq12a2UrRVGo6jRmu1AXhSVegFMgRx6UwMo3YoYKXE36lixr8zspX4vRMl73b0zMhVTz+wogPlWOFheNpUGmu6Y'
        b'ZOF3gttvKhP2aKq+5DLzlbyF2qlZFIKCmR7aWOh5vlJmoYpwC9WJWqgeTjgPoQpWC1XDd0usdSajzTLUpfPjntfv0QPodU4VJdPviXhOxvO8OF7Q7O2pnGellh/bY/B5'
        b'sYh0IlkKvz4u/n9Js1elDOoOmFZRUWs320Ca6A6eDiAgSCHaOr3pGdVWPqMGDl8OmQkgUQN8BlWaKgQpCADaCGjoGdXEdospN+Sh13sE8fNrBB6ntsqsVxTVmkyxWYCk'
        b'zCpNA1W59AR70F7mQk2JQihGVWsUoVqNVrsQQdPcw8I2nEM1gQLLLzQ0fb6qqKLKRB4BOJiATXEPZk7Xm/SVOjoa4adDD9PzO8EhMmU6J4OJAJRH1Dt2u1OOUwh8kkMa'
        b'7NFbOeRAxr1TCRAyw36zMUnBUQNrzmSEDOyX0WyoVagU0yw2Z1ccMdlmWvK5SJotwVu2hF7ZEr1lS+yVLclbtqRe2ZK9ZUvulS3FW7aUXtlSvWVL7ZUtzVs2YDsKiorj'
        b'IUIjLAxlf/UsMqFXJAQUeXpAoU7lrMKuVvQoZyFSAGintlStoCy8UxAXtLA9y6jIjc7NnG03VzPjV72lEnBWA8UzNH76fEVSukB5Dc4sVEvsLd4BN0KSlwozS5iEQAdu'
        b'qdHSRBeIeEtxgYqvYgl9FfOeKIBQH8W8Jwog1Ucx74kCiPVRzHuiAHJ9FPOeKIBgH8W8Jwog2Ucx74m0WHpfxbwnsuWO63O9vaeygn0Dim9Iie8TVHyksoJ9AouPVFaw'
        b'T3DxkcoK9gkwPlJZwT5BxkcqK9gn0PhIZQX7BBsfqaxgn4DjI5Xt+D4hB1KLbORRRTWQrlVAfG2MV12lN1r1mbOBzvdgP0CHWrNJS9WN1uXaKgvUWqmHHGY95ZN69I8O'
        b'ykkR3jS7gWrKXEjOSUshiWLeHoKsiJxmbhB4ZHrEB8g4z2gD0qjXAROitT2X/Bwe7l24B5M/n2YxkTtWB5vgkZLFDnwMNuBKXJIWoyQqxvR4FQscI3VQcyD9QGkoV21g'
        b'/HQNJfA2vRGmxeZSHWcD82szGozVWnfsX8IkQ5dK2Z3NEORJt6NFdzZptl4QNvTGcpqUC6tGz8qsAmfjm1tzVxdDv6FlrcleU62vcuq2GRGkRNJCDa0p80vN5iwxAvOr'
        b'or/VL8D8WibQRx+sbyQ8HnllfSOYd8NqxUBrbj5pj2XsL2nV+KEB5WK8CbfI1w/y4H/7O/nf5Zwn/9sp7QzsDNQldfbv7K9L1qXoQtv8dKlNkqagpv4Gka6/LnwLcMMl'
        b'Yr1EN0A3cAvSDdINbuNLpBCOYOEhLOwH4aEsPIyFZRAezsIjWNgfwiNZWMHCARAexcKjWTgQwmNYeCwLy2kPDLxunG78FllJEOtl/+c+/roJbQG6tCbe0VuxLlKnZL0N'
        b'FkbVGdDJGXjI6ceezlJRbf66dGY6J2G+F6FQ1k8XrYthZUN0GZAmaZIxz4wwlqbSqbf4l4RCbD/oU6wuDvrUD9ror4tvc7oZBDeFGCS6BF3iFhnUEqYLY1Yumd2ymdRA'
        b'e0bRgi9jAxRu/5zRCgHrCM5BHjkEiYqKUs+YlTaFsWfUrqNHgHhG7XGeUduQZwx0KOg9owYRz6ilxjNqXaH06w7Q6lYCwrKUGnXd/hWANsw2+jNYK0g1pSbg+2xV3bIK'
        b'O+woc8Xqbhk1PDVqTQ5jjUCDEVi90hrYzVXdolnz5+VXyBzwFIDc7IAmo+eck/ybpE0BTX6GAIdVkKxZ1ojW+TdI18qYVZA/swqSrfdfhHQiZkUh/gt1ffCYBvovW+iP'
        b'sUFvZU5YrskzMvOGCr26V5FeERkgcmhrFD1zkeFwvwK0QpVCDv8ux6RozbZeNdB/kdMBG9icuEipVkyj5QFvVCiYCaDCXqcA7Jmq0BkrjTZr7345uuFaBu+9EJK998B1'
        b'9PEVfUj+qj54rn+GIpd90y7Mic11pjo6ZvXeF0prKJYHGqFWFFcB3gdw1ius9nKTXlcJ43mhWgS7EkFAhZoUWqgCwkL/FaZaoEEWtSLbpqixg5hSrvdai9Yx+HK9bZWe'
        b'Hv0qInV6g9ZusimZ912a77VwwH2GYobjl6KC6g4jXSeObjpHpa9anHsmwwmtVtdiUme/WosiUrBfqSaPLA0gdPuqyGEplcEkLMqNQDUCjDhQRaS+Uq1Ijo+LUaTGx/ms'
        b'xm3TZihm04CCBWh1BqMZdg30UbFar4WORZn1q+jx58oUdZI6PkrZe6q+wm5YLvglGBL6IYXtE+odJv9NdQKyT6KEayTeQ1ry8KVC0pxN2jSxZDv8ws2ZBUVZuUrSEpOv'
        b'wjtIR+7cLHw5Kz8vLzuPQ2QXPiavDST3WLUf64LQ4Jg3eVRYlhup4YRqJ+Jz03pXC3WSdrI9Fygi3u5ZKXkYhsiW1XJkINdZtb+Y4o9CwwM5VFaW+4RfhJgFK3mCj0JJ'
        b'5jkleE1l4asValUUdUrBV8QoZYnUiu+Sx8z5i9XzrtEPySMPSZCizPRrgwjZKSIk+2fiG976R5qh2pYY2sdW5YIscWLPqPF9SyAUOkC2GlcPC+Os9VDPou+NHv7GH/w3'
        b'xsln/deZUqM9aMIKiV/oqea3pozOL5uWcOeHhfXiN0/v3lo5Zsu47bu3DFl2nJSSmpaaL3YuOld0+0JwxvTHFy4+iQjnJP+NQpoeDqwvDvlgwb3ZNYuGzt7zx1ffNbSM'
        b'r/7z4rCOH/xjw6oH6+L3vP6xX80KZehcmVIu+E0dEZFW3BLb49uBQsjlpeNEhnXkCDPOJmdTq3FLgftKcmgIaSSbyCVxA76RzlxIovLIjUCYUGUec5xaHxPLowG4SSzj'
        b'yVUb1RpOr8btUI374pEb+BLUNXCUOHCFRnAUuRyJ90WrIrNUPJLiQ9TKm1fF4F02SirJGXzRH6pQQx1He9YrDF8RkZaoccyqcwU+TK5Hq5VkBzBrUnyJw/v4RNyBN7Gh'
        b'1JOz+CFuob5bCxJdayRFYStF+DHZgR/aKMeG7+XU0QE7GC/aU8f6IhQHgzhJtkrV86JsYyGvcYGBDqolJkrNRtSG95Em0hFN8yqskiB8izxivmU1uDWU5mzDNzdQVSY0'
        b'rYKG8X4R2ZqaxmZoSni4W7MOfm8Ivjd1gxi3LHS6NQR8AzetHo6TcgzM1JR2Hm1Aa6WclAvlZI4ndSCTMScyGU9TpFxDPyctdvmr5Ds7wsxM6V6wUJcvy1T6mEYf05HT'
        b'GWYG6ttWVSaU6qlkmqsUq8SLW80z2n1qbYk2ooMj3A1ae3fVZc/MOf6YISntz1q0XLBT5vKVXHdgaQ/b4LSfFXvMXLdsoklbU67TTu4H9VhpnW7tOdO+dCByR21Ooh8J'
        b'BEKnqjWbViuhMZGutuIrO1YldCyg1MVIeO+XZQ48wp1d+nKk0L5QyEvzLzohIaWezEMfjQ9yNa7sk8H4Jt3wL3XS7j46MMTVgYjpWqveRe6/VoMGZ4NOMt9Hg8NdDY7x'
        b'yQp8/bHKSh2MQR8tK3pa9sk8fI2Wtwgty0vdeIk+Wh/Ts9JfwW946YOHRwFzbuObkMu57av8CV7AtUmUb/zLzA4Rc4stPTNY8FSqMnyC/qv1B62/kX9bfvgZmnxCfPn9'
        b'7t82KXmBorSOIwcZVnaiZN1wJ1LuRy4zTxFyDniZpmCtV9QMiJlcj+jL38yvlO4gd6+jDfCZ0BDqhqtYBh/W/bwPw/4F8BhP14Pa1QMm3Ih+4eFn1qt+ZUC3n2NHCrb7'
        b'UqvNotfbumV1tVYb5Ye7xRVG2+puPyHP6m7pSi2TIwMrgCuvrRHkS5FNW9ktqQVYt1QEOtaC9irYuR6z6dIGusTEIJePfrBwIYIh2LHkgc1yWHI5LHkgW3I5W/LA9XKH'
        b'sFgFwuK7Ei/C4jSdzgrSAGVpdfpyutvgf4XD9E2hZ0b6LyAvMmmGiSJaRZW9Uu8mocGMWI0g4SgELwYqbFn1NrWiACC6Vz1029fQ4xVjTV2thQqWzmIVWjNIK7QoSDoW'
        b'fYXNtFpRvpoW6FWJdqXWaNLSJhlzTw0nrWo6UiNVlMG+clTpEJBonb3qgKrtVqO5kvXIVY0iii1W1AvMyGzHaKuouqJ333vlj7RpLZXQhs6JgWh5BVX9WamwYV1hp7Nb'
        b'btFWVOttVmXGi8vwApxmKKZ5kBDFYnbYudRXMdpyhoI5Lyz+ShcGn7UI2yJDUcS+FYsdBnU+8zu3T4aCKi5hqZhsudjdoM5nWbrhQCqFp2JxgcXmO5+wJSGr8IO1EaPI'
        b'LipQJcanpCgWU2Wlz9LCPgZ5c1qxKnumYrHjBHBp9GJ3Bw3fjfdsfypBCwEFrcjdLNhncUAYMJlVsDVgu1orLMY6m4NuUTil3tVsb00zWWsBfvU6r8I/gBPNTemMid2g'
        b'wxZbrZgpaADYFh1dZNPW1FA3NvNon7oAthkAsKADdY6tpTOyO3y0MK2rjEDP9PWw4o4N17se+i+/1qYXtgnb/HpbVa0OMEmlHcR/2hdtNWxA2DR6mJ0KvaIWCLvXeoQh'
        b'0U3DVBtWYZhGq1uX1IrZgNScCMlrLe7bjipCANTpDUUVJhiwcDmRVe+9ZJnjfqLaCtZz4WxkYpXNVmfNiI1dtWqVcPuEWqeP1ZlN+vramliBs4zV1tXFGmHx69VVthrT'
        b'mFhnFbHxcXGJCQnxsTPj0+Lik5LiktISk+LjklMT0yeXlfahdvB+HUJYvp2S80DSji9bc5U5KvXQmfkx2VQqOw8C3tgiSRV+RK7aKUHDFyeVJcJ3PL6Gr6F4w2Qmu58f'
        b'LEGdLw2iNynEvDZ2JrKn0awXIuM0ufn5+KFA0OeS5mjSlpejmkd9WOdFUrfQhSDHwxfQebwbX/Une/H1HDsVMdfgl3XkJsigVMrzQxJykBzZwMvzA9jVSOQxiK0nyE0D'
        b'r6aXXFBXWagaKgeJdiQ+LSYP8GkdUyDgznUgTN8EmTlvPtlZx0bnGlvK2ELSnA8FWzXz6+BRkJtD9ooRyKibA8kp0hVsp4cOxrDEwIYQtTIHP8JHA5B/Dk+Okl0hgtlM'
        b'J9moIjezoTCHRLi9BO/n8MbFBjtlaky4E3cGqkGEb45Vk+3QaAw+nwPifzOHFHMkYjNpFG6fuTRKRG7Owk9iozjEZ3EpZBs5yeZ1TpofmpgM86EoM8WVTkZ2qgQgXeRU'
        b'njWI7CW3oV1grY5D27Il/JyXSCdrl1xeho9aF+EjkCcoSE12kdu5IK+T3SI0aLUIXxpBnrIFx2dBir4aSM6tV9OK2vKy6cSI0AByXxxC2oON8Us7eetByDn1jyWqN6cF'
        b'4L8kxYVKfnQwybgn5b+O/PiI34rfDXiEpx5/N6vuoFmOD+O9fn/xG9vyqvzoP+f+eBrJ+dknxVn144//4IOWAylLs4+0f29AiHLfp7ldP7h7tt/FtSe+F7tg9o9HGbUh'
        b'a9K+5d/w9rfRpGHaf6zerNyQ5J+9tuu+/eydPZFfHA058NvfRr/62L7qourRe2/+bMAXCZ8+Klq0fvL1qBtfNiilzJG0tpo0CuqVrDyXgmWcyIAfD7BReKnE7Xirxquu'
        b'IVo9NFFCOvzwTaZBkOE9ZH9gAjnao2Vx6lhW4lOCqqYVN/q58bOkkRzvUTOsJJuFi3DaqCYmulaUr8rOztPEkDYlhwaSR+IEEb7CvFv746f4gsagiInMgs7AEuKL/Oq6'
        b'dA9mNPgbXhfj2xU2QKvTlQrsG+OWxzu55SzqDSvjBrKn+0fMLvGQcQ39XdxuTx0ONUWQwDQvRM7juUX08RJ9lNAHvaXDsoQ+ltLHMvoo9eTBvTv1Bgp19lSy1NVEqauJ'
        b'IFeLy1ztMP5dyxh6d/79nfHu/Lu3ESn9u+U6asTn4I+6gwSu1xmUamvYN72yRN/t7zinrdB3B1IeBThDasUl9ME1zIoABwKmqpVQJwLOoUx8gAcbHwyMfIiDlQ+lrLwh'
        b'1MHIBzBGPhAY+QDGyAcyRj5gfaCDka8ERr7Dr29GXusywFMIlxS9ALs6i7oyCLkVQDNhnoATBT5A637tHuUVYhSVllp7HaQCi6ztTYNqa8qNZq2TK4kChiWKkVOBmlKp'
        b'3mW7STvoEnZ71USF3/8refz/WfJw314ZdKGEGJcu6yskEI/9KJQXopwVeGXDFn+F9abP5oT9LrTj2OKOOIGTNddSHY2F8apm7xzoqlrKKhprtCYfvO7iPuxXQYLwbsHq'
        b's8cUMwn9La+trab9pTFqRZ4DurQsrKgtXw4LD3K995NAM5V80lLi4h1KLwoIILbR6hb32Lb67IQLMWYo5lvtWpOJ7QwAnJW1xgrXblzsZhrbp/DnQKyey8Dc6Ba7m89+'
        b'pXhGiz8nonkYaf4fIGFN16/SVzpMbP6vlPV/gJSVmBKXkJYWl5iYlJicmJKSHO9VyqL/fItelB/pfT2LQjjxNS6XINnaIxJ6E13u8EXITkUssjmgUpOdR3bEZOfm47vz'
        b'HVKUN+FpA37sn0QvuWS3quwbGOESnfAVfISJT7x8ON5rT6ac6Z0gfFWjzskD7jXbyRN7qXb6cpDKWkiLPz6rKLXTcyOQpLZOtRbkFTjuJqINLCQ7CzZAiQ7SDEJUAEgc'
        b'UCOE7xctAYHgED7pDzIj2ReYX1Rspwz2pLn51hzSlp1XoKHXYMWJ0eDp+FwRPR+9SA7bGYN9hJwjV61RwMpHUjZdnY0vR5LjpIVDIyslkkErWK44cnJpILmL2+fJSJsq'
        b'H2StsyBe8SgsUYSP4yfkqJ0afo3G98kTmI2ec2gQcvDteYUqfJg0SUGObZHUS6Bh2jfShvcYHb3LjilNVtILQcPJSRF5iG+L2EpFFYiQeNiv4VeZKaRmARKE4rND8alA'
        b'KUJr04tRMdmxlK1fDUhUgXSWYDYf2kEKu5sF8mUb2UNuU5mzBV+EUC5pz6Iy15II2Zyi9ezuUv/F5Dq5SdsiXdkoOw03CzegHgjEjQwuTtjjUTx5OZhFj8qSs4tOcRe5'
        b'H4ti68kR1s9fB0iRvPgvHJUcJ4wpR3Z60JcYGEVnoc0hjWfFLKDXCuPT1bE582Hps0hrUaQSACDLdZWwEt+ZR286lZqDlpLzZAeTzfEhcj+wiOxNzME3ykSII5dAhCW3'
        b'8BHhyH4HbtoQSJcElmMe2emEDZljKtznAV8hu8mVaWKEm+b7v4SPkNvs4rQ6fGemS8DVzI2EXy0FRTJPUXbKAGlwOb7GJF7cVsRZc1QFsaQ5L5aCTL5DlFWSAxJ8i+zF'
        b'rXZqKxiUGhEtXF+jlKJAchUA5SkP0NFYx+7TvbUqn39FiurRInv/nw/2D9wnGCGohpPb5KZDdyEYRwAoke2xBXlzI4XqyOlo5QJ3y4sj+Kwcxn4Z72E6BLwbH8Gno9XZ'
        b'MVFTyS0OSXEHH5uO2KW0a2ZO09BT9gchIP1buLT++IpSxG6UHbS+HytCuhY7ioSkCtVtxmfwEVqKXCgSSuHjMHlMPXBvPLnjNkq8Ee9iowwjt01/+89//oNLxEgWfklE'
        b'kY20JhMZP/z0P2LrJBCT8o/Llu6clE+mhm6tXPnqysMjw/69ezAecE45r85vSHBcwG7VKN2843aS0jiz39yiQs1Nqzjqzb07Pnh7wA/efJR69JdvXtkVZFoyzxb0kqG/'
        b'ZvScbeR7gRdOPfllhn3fG8rPoxeHZf3rwZh/Tfl8xKkDn2WHJHDp0/PmNp2L+OieaYLIdn573omLv1Klbv/n+PE/LH3ttV1B734g+3BU1dmTOz4aOXxGwVtfpP3o5BXR'
        b'H0bvP/GT14I+jqnb+9aa7/P7t785+uP5m8ZO+u62NaeObpm8umvIx+fvL5g1+62IG2cyryxM2ZrRtDuhetibf236fEfcQ//81dl1HSv/abv4533+5t8OHTnxnHbv5i/N'
        b'D98LXC5e06wOHhpzUXxz/x+yWv6tPzFIMtwyJWPrqh+EvDtu7ab//Pz8m6mrFUvXfSldtoocevBF2NOwg9nP2j//wcjZuStOD1mjDBLk/p34LKALqoxYhE9HuWsjUkOZ'
        b'NYO+CtaN4l1yN7O3OoIqIxoMzNpjKT4v67H2ODKuRxURuFK4P+shubRWo1ZF4RPznYYaIQtEJnxDzQw9yFayzULO1UZHOWw1/F/i8enC1Uz9sHwWtK2muD5mbAIFr3Ze'
        b'lYo72HWPOsCImtwoO9knRfxSLhVfX8oqtERgQFu5eTFkM37CI7GGwzfIJnyPXQYnxpfJIaALbYwukMZghKRr+Qk5ZLONOrHFLxvqacTBsilJu2DDQW4Fs2xJ5L7e6ymg'
        b'lWwU45bFpJllIzvxabLfSnecilItmGRykZwQoX5kpwhf05D9gqnLsanxsFE0HjoWvG9MH5diKUP/l3Qu3rQvwVTP0COGMw1MsVMDswHxcof+pUcLQ2+qE3QwLMRTw5ER'
        b'kBrOSZn5CDUlCYMwvY1Yxgcz45IAnoYbBnloN3padehs5ILepJw+KJtiodfiW/T0YaCPSpcuxZu6xu9FLi0OEOqscFVc7qqp0tVOkBfFjREeJR6Km3NR7oobX0OrkDjY'
        b'LepL6HmTuaTJrwmx01GuKYCpWwKbxK6bzCXN0ka0TtogXSth6hUpU69I1ku9XflIKx/Zi5cLFni5wYN4yuhFisVlMaPXzkTFLPYNmYTe9x4p15TlHjaLhfvO8U18ZDrZ'
        b'V2zFbbIVIiQK5tLkuNFOkQQXhu8V4bZF5FAxaZufN5fcLiS35welxMUhNHyQCG+aRQ4wbk+Cj+KLRaRNrSlOjiM7koChkq3gyLFM0s6IdYUJN0FFrBYOxZokURxwZWfJ'
        b'Oca5DMokp/FNqQFGMxFNJMcrhH7dSMbbyElymkfkgRGNR4PJBXKMUZ4huDFEo45LSkjmUUSJdD2HX8YPyFXWFNm1Nku4G3zMMnY7OLsavIacMcr7f4GsH0KWiKaUWQUP'
        b'82fEy2//tusXczYNPD9dMb/8dzMOLIo48PalBTnjQo9kvF00sGPt7CnHR37rlVde++C9L34Z8FL6m+mTVw4jckn4peuv1ftJx30y4tL3z304OKmusGGxrPg716OOjf12'
        b'd+7ityf5J7y7eXTqldwiy2HLIUv1+4+Hv7pZEvHdug2fVcb9ZuyiDy6ToM6GLv/HI1vXNrb/vPu3//xw4uH7QZ8+qPtLy+t/6rr42w+2PF12f+LTP438eE1NyrG55U9u'
        b'jM07srkwYtXqyafUf7g/+Gf/+t5vxjxSJx/5xeNTc//zSsfPAuuOfvCbKa//98Q/XtpS+WHqBtvQ/Bp7kTKMXV0pIrt5dg+/H7BvgHtPcPMnAbZkuHlTFjkgw/sYOnWi'
        b'0s3kGkPsA8m2eS5MytAo2Y9bJpAr+IaA/baMWOgFmSKk1jF7uEfLGQEZsb4/ECJ8mzxyNzwESqQkN1gGcqaSnNTkkwPkUgzwfB2x+IIYBeMnolJjOCMSM/BFfQhw4y0a'
        b'dpe7eASHTxjwduHyz52mZOG26kTSKdRNb6smt2pY8sS5g6LVGZFuF8Gza+BPkV3CEC7gu+SoxtPgEe8n9wfiy+KhZD85wfTx/vhOgMZhzrhQKlijcihsuQhfIudG2aj2'
        b'2gTE6BjZN9qHfp8SVDXez2rDx8YNpEap5BS+4GaZGDJCtGwhPimMauMUuUaNr5T32D4yktocyEwfLSOGuYgJvko6BIJynTQJ110ezsOH58zxuLoeX1+Eb7Gq55FDmp6r'
        b'MsmTWHZZKrCGd1kyeZlsnMB4uvaCbAmw+figDO/ka1dOejFk+02vlvewoxEuwGd0SddDl2Ip1WGmisxgUUxpEs/Dt0Cj5ICShY+YUSrhxICGBPNGmSvd+ZHyYj6YH8gH'
        b'AB1zt6IRmhfok18PZej2EzTQ1m6J1aa12LpFkO/rEiOJhV7Paql20RyTi/AwmrMcHpc5xxWYjOZsRD9T+DD3ETr6v2B35dDdf/m7XqoDwWfK5nTWcKhgTQ7NiEVvs1vM'
        b'LK1GoaUafjdFywtpxxXV+tVWqKfOordSO0ZBg+NQSVldanmHOsebVvt5jb1J0IPR7pSvtum9aJxcJFTq+HveAF64//juKCtuIftwB95O31mAbywExEcO4+v44lzcLEGD'
        b'8UbRGrxrjXB8eg93lZM9sIZqBNTosRpfwBcFRcJdMbnNiCtuWagi+zRqtQifwIdRON4uwucjUxhpTgkTJdxD7OU7uf+zSoYY/cWH1pGDrqLS0WSvKrscPyanyIkEFJUs'
        b'ScN3QhlBXIp3kVNUSsPXXopySGlryVYmbpJ23JQMxLdsuYP8CsT3IT7OOo6bx+OjGgGVdJQzIe6GnB0r493j8S3csbhIKMbjNm4YYLntRj4zRGzdCjk++0CT13o8uHFq'
        b'6MzKVZ/lrJif97ft67kbQ4o2HTfP+InV3rzULv1O6qoZofdef+PR/2yteLYwKrL4T6/8I/76nj/vwDnfmz1/SXHup3Xbjw6OWJhy4Iu/vTs7pujWs2NNx/ZUag5lpBkn'
        b'r4n5+PSM17uLd6x9mvGudbFx8v0PFqVkfEJkJPAPH4TkZo1957hRKRVwNOka7TwPrSJPPayuC4sYIYzCzSPYPb9tDSGOW36nkLtM1lgVqohW5/Gokpzh8TlOQxqjBeFm'
        b'O+lMB/IlvMaCR4ESi54nx8gVoJFshTpVAb0EBViMWw6TQXwX72R4FXgVx/tIoslpN0p0bpxS+hUow4e1odZaSjdbz/tBBCxpEovCGT8eDt8U59ET1TDAcm6Iw1E0/2sa'
        b'ItbC4/3ncNPLPkwRHU0ouW5xndZW5f3e8xTkuG2anjXSFyBIXXefi33efS5i1qziX4s4L+eMPeiKYg6rdiX9ZTK5I64X9y+jHc9QZBsUUfRXlAKwrVXQaFOUpK+nrqtU'
        b'wRulbjDWRcWwhhy40eJdP2ylN/bpXFppraWiyrhSr1YUUCX6KqNV78J/rA42AJZdqzDUmgDX94HMPF4p4EJmMgGZTSSPSGd0FuyKwizgNnLycvH54iyQlZtj1EppOnmK'
        b'ssg2v7qgajulGxbSjJ9qQCbPyVOT7cCPFYOE3hI7FzgOVSQ+L8ZHipCG3PEDxvEx2c2QhYEczZtSSfbgi0zGF5k4vJnsJW1MPRiPD5PGEeRENMgs9ah+IDnPoheSJ0Oi'
        b'CxJBVOHmIXIIt0wznvihhrNeg7QPBkye1KZ/ZVIwjpNvPXokPHJD+Ydc2oyQb70iQdsTUNEZeZZkW/D2LXEzUlIM7Tm7c0xH//XJZxK9Vll1vNpeOWN6QYDx7OdX2i+t'
        b'2aH84Na1rd8aU5UZ+vbxufHrtnwYlzG186z5Wdmczcn5P9s1ac3vXtvXfiRs/K0PpCtGBMr2r/v00KltP5/weVK/44v/FWSvlR2OrZyWOTBl6x/X/Pr2T1aOuPynk5u+'
        b'LV087Efr+39W+GT9qkPJQ7deVoYwFGOowwdIxwI20wDsqRy+greECm9euV6npmym8PoyJCMt+B7ZygOGx/cFvvAcuU3OkpvkFu40r3IYffjjszw+qQTWjvHrx8mRAcX0'
        b'OnKoZztw7NJ8fhg5PI6hmKmKavqetpgN9O1aNDGQXOPJIxs+wdjCBeRRrSYmFB/E7QXClf+BU3lyYH6yUPNpvB8/XttAa4gtoD456/kofLOWYcEU8oTDx4solVCqSQcb'
        b'W0icqHIZeVlgGjvwIeBmTwFhYujVgVxF5LzwXped4/GNAbnRsfQUQaVW8oD7jorwVnI6n03a+PkDJpPNjMGOBYlNOpEfhLumC5P2hDzCNzVOQEX+4XgHbuXxcfKwmskG'
        b'qzNUSfgKFVMcEzKdH7yEXGFjGp2hIl2Bz/HB5Ph6VtCOb+Nby8kRoVfQKj7Hx0xK6Usn8xWI2g05i+nG9bRsoR9/QasiY443gJWBPxW0JGEQ2xDkQp60dL7HiwDqPDF0'
        b'H53khbw9WNsCj/88h7UbB3q8GMCjYajc5a1sSaIP5hGfLFROUbYlFTHNDbWvs6TTRwZ9+ColeNFn0gd9laNlkjACln0mPPKFSmltgK4c/5QS4YuHv/7P+d5TS3tdbUVp'
        b'KXMS6pbVWWrr9Bbb6hdxUKLG9Mwih2l3GLvN6BqbJmHKw//XVW99AouFvv3jt8hhiiMTi3mqbUNc+FjeIbV85ZMPFskBohA3UC3nwvlhhUNSg4cyxcxQwD/tVvpiRWtw'
        b'sKicHENBw3nAIhfITeHM4iBg8JZA2AtN+Bx7yVwgPXYppMctwxLEYwbgC/9L7yza8tVuHX757CiiP6CSg0UgJpM9CI1Co+bjE4KZ420YCkjF1+KS8TF8FjpE7nAr9LGM'
        b'y52ZTzY5XgkXine69D7kxjJ2HjGPntGRlmxqKdeaCARsLpLhFj4HP8CPjb+ynuSsFBLfmRn5MfMk+VCXq32j/BP4vdxQZfhEfP3Ah9FFB+Yd6Dr4LdO+8IHXImfsyvOr'
        b'CJjhNyN6z1hR1nj2nq1hr4Tc/U2XUsKwLbkH6Oyh4J5I9o1kHop8It5lZpgpCz+udsNLZOMMipoqBDtCch/vIVscWnGgxA8cenFyWc+qnjhmhEtAp8dhiAno+FIWw2uh'
        b'5PYUemBLU/E+wNSypbx+w9S+HFfkIHwBx6MvpbYLDGsNdMdaY6lGl2IpMTwtdtc+EXeLaYFuqeA35u1tSato1EoXpNOyo3hn/Rsdn1+7s5DMJpRcWzY4Gl9eFJmjyorJ'
        b'wW2x9OyVQwqyTxKO95MODzga4Pi2fu5+H0YcvRMCgJPXibb4l4j0Yp1YJ9mCdFKdXxtfIoGwjIX9WVgK4QAWDmRhPwjLWTiIhWUQDmbhEBb2h3AoC/dj4QBozQ9aC9P1'
        b'py+b0yXAxuDYLRv+JXJH2iDdYHr/hS6RpQ3RDYW0YF0SpEqZs4xYN0w3HOJCdMkQJ4YSI3UKeldFZ0An3ykyiDrFnRL60UUYeIij3yLXtxArPMVCDren+PnfulGHQ6Cu'
        b'gJ56ni+jS+kd982eusjD/XXKw3xJP32Yvp8uKgIt79+IGjkWinaGWI5wZoMouBHJYE78dDE6FczaAGad6MfmSaJT62IhbqAugrkOpXb7lwIB084GrpnpjDzU756yhmDj'
        b'KGWvApS6lO6SPpXuL+CPFiAo3W0qiTiRC6UG6PJf54QJHuV3c1tD3+HiqMO7esu0EULksfB1mnf4P0pQnHbokPrRiHHdpBFvXuHhrZ6bn5XkJlgCtmjxQ0WVslA1ucPq'
        b'uZ8xOvypqBl+lY1+sm42+sDZxz/Th/EPn+yQWGnf9U/nDW+9HrQxTi7+Vf70MvGdY2+MkE+tUM568C3xzCxDtenQww3P/pIzJKTqR0kTd42TT8hqOB66PC018e7bLem3'
        b'fvT974T5vXvqmr1wYFZD/V8Gfufg+vyEiJvvf3T1Ztmr86aceznipY43lf7CWdeDeGpybMCH6ZuUVCIkK+Zt5GQyY/TIAytuxS2FI/FVpm+WTuD7RUwSTixbB+YEepo7'
        b'+5Or9JiRnEyyUSMKsh8q3uburX2DnHCbl3ERkipyBW9jDtbrFpN2wfs7OlIlZIIsg4bji8PEE2vIJcEncE8aOY5b1hloV3Eb02C30sO7LhE+rtYxpjxCi1/GLRGhzix5'
        b'+BKCHHtF+GQsfpnhaxPZMQ63qEhjLPCv2aSVA95+B4+3DCZtNvYOvkOkMxC3rIIaGIWFenBHASD/7QWkXS1F6RrpNHIEcPWhcgGxvjCf2ePjPcIdYSdIuQCJjBvMfL0d'
        b'KlOuIcy1S557/aGg4uyWMNOkbjG1bO2W95xmmWu7/Y3mOruN3arlXUsgsdBrPS1r6GM9crKfaz36GdsL8f/Egwv10r8XdeWVlNJO9+HOOo13OnK7teLy5B7WcydoL6dW'
        b'NdSaTZHKC3YlqNR95vro0kxnl74c4dZ8bzdu9Yu69gaUulapj2bnuJodnu3M7jSo/Fqtuty2KdiU1hj78mXOcTU6kIoaCoOltubrtVbl2Zq2vo/W8lythbPWqKnt12nL'
        b'sZLSUlutTWvqo6FCV0MRxTSr0yDXa2vfXDnf6yVr9B+Per/sj5GEw/H05DcrVo7KTGOzpAK9mZFP3xOeZQpWlJmSl4Qi49//cV9spYqhgn9NpyxvlrZTFxn12e81Wrnh'
        b'w7IP0eddEUUHXonYHJH2E67sjuSj3XYlZ4tC1K2nvsgHLju6yInO8L4Z+EIfHCeTwhjeYu8qc+KtBZTFbOjnjge+qb90US9kc9VDUemlESp//n8n6zhWK2KFhLpiVDWg'
        b'jabBRf8VwSbkZ2Q6Lc2lz0fcdzqM/xgq5q30tpI3G0OEFwLv1L1WnqvN1S43fIT+XDN43mBYp8VvJiHdAqnm3+eUPCM7pImcwTfd1gp3+XkhPXhf/gTh2HAPOT+Mqn+i'
        b'VDVT1FTm2Mwnkpv4RF+iQ0gpsyI2NuhLy021FdU977ZzLuqShgi3ufbM7fHKVQkzf/UmRbQiD4VGCzwW9VrfCx7r67tN14Z0LjEVmpyvYBXBIou+yUt4aaW9T5Icxhj/'
        b'CPsr94novQnywrIpZ2aoEFN+ppAj9fiiGJVJUANqwMfxYTv1ySHNJePxRR7NHorWoDUTprD3v+OOEmbU5GE/WhyZr+JQEt4urZ4RjB/jTtZW4wZq4nFgvnhqmWmFOAMx'
        b'k8Ld9QXUpLBw3xpt/58vCsn/KbJTjQ1HzuGdznuNBMtCGTnrMC50wIi7PSE+Tg4GQEdODbI0QHGmYJhbQTb1yNXkAr4lCNZkdz2z8xu0mPanOUs6tSzXujwEschD42jk'
        b'1Cg/YJTPKLOQcdXQBSJrO1T32euh49qOB/PxoTMr7z7GHD/n09i6w1M/95OFm0XZF6+s2ryzfFHRpvcbjemprz9K/fPfDIfr/vVoZ5zZb79yWnbk2yuOvjfq0q1pn/R/'
        b'Rdz/H9tfiXqsLDL88MZHAZMyM4ujJ1cXDVzyXn1Xa8y/k9ZcVBS/mnqj+NDNS0Ntv3sn07g3OC6tvG6Q7M2qz35SOuXl2tE/2r5Y6Scct6/KYLaRT4M8tJ8x0xjnOmsY'
        b'7nByriWwe3oM5Mj+yTZqSRpDNuHTfTGA5PQwuhHJU/yQmSVU5pPbgVEOtt/JEC9bjkbim2JyFXjFRzaKu+eXZDP7C8rdAljgSyAqR2c6K5aiOHxBOgwfJnsZ841frmtw'
        b'Wg0snSoYocUuEpS/jeTsHJdOYVyVoFEoHdPz6lufmk5p6SqL0fFmUw8mtJQic55TABM6xGFHJucaQt32JSvo+dZlraXS6gPD85Z2TzTQBo8lvdDAGY/3XvZqLr9C7Nix'
        b'UtT7BbzMAc71Al4xO4SSAAIQMwQgYQhAvF7iiyb3tqyXChqtafioFdDrXpGImmyNxFvwKSapMoMlE3WejZ6rWqCiZh5+/chu0siPEOE7xvZXV4ut9AW+H7x7UyDSn5R9'
        b'WlZl+FT3aZl6oEYbYHjjSZb207KPyvIrwipkhvdyRej4+zK/HymBWLOj581JFPCY+gRvL9BOE+w+ODS0Soyb8cuLnLPftzZbWso8Itgah7qvsSmY2Vp4TDPL6pRjeqzq'
        b'2BuTmTqoF4IXC/HP5WVr3AEPY681Phjma41Z496XmJL3JgksspRpEuhC+33ThfZGzoUFpbspDdb3YRFdz33UHXtrNHnI5a0gZ41rDSMlVqqPnvD+6o/LNNrXfh/5m2yB'
        b'4Sr7uMxoiNr3cdmzsmrDJ7qPy/gdcSmJ9hun4+zXVl47Hb/97H/HixPrDAjZiuR//8mnPezoC5mdeLwfmyrt3FY03H1FLTLBroZabg5wm9ieMi+2tN79aPtY6Z3wqO21'
        b'0nsGu6+09w49oyZC3tc8SdjWEsfGlrzgevdi3yQ+15uqnlX4aX9YbrI3MUuEJH7kANnI4c14Jz5jzP9JhMRK3SV035/0cVm2a8WztB+VqbUfln0Cq/5JWf+CUG2VIVfY'
        b'wyYOnRsuG3jqZ7CHaZtlNWSLJjdKutTIjKDJZXzwxd+o2x1c6rhO1G3BPXjuBrrgDYPdZtajgPfV7pYatBW2WosPVC227PG1zLvhsarXMreEuy+zz84oQwT73R5zXmrJ'
        b'2x3UI3FX61d3B62stVdU6S2sSLxnMKE7sILe4aKnb0eNdw8kdMt0Rqtw+Qq1CqavgbfRS3b1dpu2nt0TS4+TuuX6+ooqLb3FlEb1efil7M/cxrsl1JQpvjvAebmKUefm'
        b'k76I5bAZbSZ9t4y+QoNm7g6kv5y+3iya3drEakqwHKJl/Kj7YXltPXNI75bUVdWa9d0ig7a+W6Kv0RpN3WIjlOsWlRsrlHy337QZMwrm5xd3i2cUzJtluUCbvojc1BpO'
        b'bpjydFY6Ise9v1JmsMw1yQyybyL8UHgY3Gv3VAh88eWkddzf+NAaUZw2MyVltmCOHAoM5kHShKzkTgjADE/OcFFJieyObNICzMxhq20lJAGDxCE/oJVbySE+GD8KZBwt'
        b'2VsUEk1ZtcuRWXnq7Ly5pDkfX44hHbE5c7NicmKBxwWuyulPRPYsxufJRfkMfCaO8eT48OpxZM/cxfR8sAHlkR0TmQcMOY13r0xMKqmPEyNuAghKg0gjSwA+7gy5lcij'
        b'WvIYJaJE/JjcZgkrFtQnJpF2fCeOR1wkwp2BuIOdQ+H9+Mx4l40ohwJBRrtfwpMrQfg0YxVGkkuJUPRBfZwUcUqE96pWMSSDu8idFMECNpm+wfzoS+Q6R/bgnTFsKldl'
        b'RqFitKhEGlo2XV20CAndOzUbn0hM4irjOMRFIbxvCjkquJjtJ0cHaNT9SaNKTb3s8lRkRy6HBuFT4qnLhrIKf1+kQFNRWrGkrmzYT2eNESocitvmJiZlhcaJEBeD8AF8'
        b'Hp8VvP1OFuEH0fSGkWzBbhTvSw7BbaLySiOrbZl8EIpB1+ZJFGVLZmYWIWZ5NgzfDUlMysT34vwQp0L4IDV+YOZsSpiVzfipH/Cj9EVASBzD4QfB0awq2bDJaC1Km+QX'
        b'V2bZOn60QHKByzlGGmHeri/D10CwUVOl60XczCBqHL4+LFotxg+VOXkgMfnH8/jAXJ5VdkavQZ3o2oDA0LKc3JWJDoP4k+Qhbk9Mwl3J+BqseCxMvnUkaycb360R7tug'
        b'FgOjyFa8jR+zFF9llaljxCDVvJZF759JWyV3rMF+0oV3JybFK1IQm7S96+1sDRKyx2joNSwtpF0wawZwORiMt4gmA7idYRVenJmO6tC3lsjLysKGT35JmDVyhpwiG6F3'
        b'9yNTeDbS/bmlrMbMBSlCjfkMvjKTGYQNwZ1ivCN8MOtNEdkshll6WJ8iZeM6MI84FvBI5mhHYccCPlgTXCdKIxdyWVdCJGFoLMqqDUFlaz8PmyxMVAQ+ivclJuBL8RRY'
        b'YWz7QP67x5ja5VnkigNaeSQZhTvIDY50xuNrDMj5QnIqMTk8GKRuLoEWax7CurdkWWK0hlrucUgaxRv5iGpyiLW0EHfgHYmpsKjbaJk06DnpXM42RvxUvNkBeTvwVYTk'
        b'E8jLE0Wh+EgAKxmJL+O9iakScoJuxQyAC3wLCx6EeanjNMI+VFKLc/ls3BoqGgACLBvxj8QyFIreLhOVleX+MjQSMcBcR56QY4mppA03AZqn1R3Ep/ABp53ldQX0hLoa'
        b'agA6YJmuVPBDS2FG6NgWWfGRxNRgcioJQCqTwuedfJagxVuiNRrFS/Rgga/lpuJT5AxLGLaaHE9MnVKTBB2fSBFAK+w21tLTSnxTQ3FZKz1tkJJ7wIHw/uT6Gtbz5CUN'
        b'6AuUtYYLLVvwu+EjBf++7EXkAL4ZVzAqSYK46QgfzQxmkxBKLpL9uGssSAY59PBDRE19ushGf1bVR9wc1IrqlwQrygKa50uEScAP5WQj1IV34c1JgAlmIHwsELrWn01C'
        b'jERDdozLzJUifhkXG4gvsooOBUWgOPStnMCysom/GZnkgJ9J+CpAxilNNjXAEYs5fJQ8GSdg4tuSLGpNO4l0IDVSj8O7hBudO4tWMV+FeVkg46oW4JtLBMs00pwXk029'
        b'uOaE+Q0lTcvZ2BJnxQEEjp8p+JrSY5kDPN5bTbp67ntuDqfa0qo64LNiFk5ZKKhmjHqyj+yRIrwlFrBWDL4TzLQweryXXNN4mHqSDiAvYsAwF8gV/FRiT3FcpqTiqU3S'
        b'XOoLA9grd2oYt9SsYpMH3T1g0hTjlnGkDQCBHETkGm6dIRx7PwFR8OLzTtEcGlewKExi9F/HZhgfHxNDugJRVBzCT+B/EGA5yndA5zZao2Eu8kh7lipHkPTixWh8cZpc'
        b'khCOm9l4Pxg2FCWhb6Wg0LK1x0oHCSgF3y4m20iXH8LtaxB+Cv/JLQmrdAZulfeqk0fj50eRNkmiBN8QAKKVXIrWzMV7RgNRZY64j/FOoIS07pD5gP9OlhUBKW4Dar6G'
        b'G5YLlI6WSgnDBzTzAZ1tEWbiNCK3DPionSpACslmslGTLSb3HZ7nzqkYiVvE5E4uvijgwl39EkhXEIqFlceP4D/egzcxVmEQaa6nm1udnQ/lssmlfqoEMdCvQ2LTsgEC'
        b'UW+VrCRdIoR3T0H4MfzHl/zt7FSwjTwudCsrxRdUCTyU7RLX5OHzrHAwoUbYLcw++DgyIiM5nMy2pmJgDbWbdPUXt/qH9Bctn0FOMshahk/X4D3UI7iNKgLI4SDhrqwt'
        b'gLv2RAs3dAFYgcB+mBxiNg/D8G0x2SFbysa7DuDyKukCWnFzKGxD+F+Ptwn77pg/cE0tPCLXK1A1qs4kh9kWkKwlWzUqVTa+NHtsZA7dZv2nikjn0HnC/D2FDfiQdMkR'
        b'udofAebDt9RRAp+yFz+crHG7Kh1m9gJ1QckjnQKRfDKLPLAG1ZJNQYCeYP7J5bF4I4OxG4sDUDganCoJLcsNNycjB9iSR/gIaYEJP/USqkW19loBbG+pyFNq33eAXMmi'
        b'buitmgIV66hiqJhcK8xmCsw40TjuR8BLKhYetb9bvyizwkFcL+fhI1SJmk3OMC3qedJsLFcXiax/B752eeChpT9+x/yTwlDpe+mvarpSVvyicPrSt6a/8z+3p2qOFR77'
        b'RPPO3br4sNf2hYws1Fme/aJuy/vR7we+0vjHtInoh9/+7PXz+hX9xv15tSHhZatlyvgF2/NFbzXuPNIvaP6n3+neOff+yMyIWUlzxuw9fyvV9o4+9q8J+uJBP3x6vnXR'
        b'hAeFz2rf//Jvudd+2H/296++vuSDEamjdSUHp08c3i+1bcyKwP8kvb5p7i/uhO14Y2rGgjvNb0y/U/Jsh6nxjZe2z/z9qJ9f/iT0Hf939Pq7r71c8oFk1+Od6xYMnPXX'
        b'GSkTJios11J+PWoXuT15zsz26e0vpastJ9764NRr5w8dHpguSq/+3eHXVr8midaMHjRqf2uFYcCAj75/9BffHhg7p7Pih2//81eHLQtTgip+8+aq4XN/8d7vLB9POffF'
        b'gCFT2s7+yJ6xIuDIj6+9Hv07/+kleVFf/Pfqnw9YsTlt6S9a/6FapEh/HDUha8n7lxamT2tfTBZ+7+aIvZV/sMb+9Y/vvplUune9aJn6C8Xvqg9+tybyV9U/i/xbwRP1'
        b'T67uu71UF7x+RUdt8+W2oHXTnyiT715r+fmNIzv/e9anrVs/6151+Ndr9EG/2h8csnz4iJx/n/zo0Yz1MZ+f2p0yZcA711JT3q8Mm3LVXPpa7L8f9qtZr/z8woXVqj8N'
        b'XV+d9PRm+mffmXzsQsdLU9YH7Loc/nuL8lNdw/akv2TmDv3p3/4ZMnb8h1xzpbI/u28NcEjz4OeN8522AvjQOkkVeVkp2CXsonYA0fmjSJeKOjoc4vJG4dPMnKpqxTqy'
        b'Az4tVI6QIvFMDpj8e2uZbUAhuRuLW0Lq5BZyC7eFrCwl94L8pSgcHxXVzo1hyuFFdeRCID4fk2WX4NMOw4Z+5IEIX15NjjDb2XF1UnqJ4PNWqjvJbsE57qAcSEtLrBjf'
        b'chiqyshJHrcA690qGJo9WhQNg8Q36C0ZgnZPlsfrBslsjI52aiM1BTFFdFgruWn4UrJNoEJzYxwGZsA/mMgDal+2JJ4pg1eQ8+QJMONb3J0CcUe+oCk+swRvgdYd9ht1'
        b'ZP8Evh8wlMyeIrMYHw7UkHPAnD1/bR3eiBuZSlI6DFBdC7OmaMa3nze6WEyOMfMNvIs8mi9kWwBihqfdBb4ZxFzugHQci6NGHvTogkowuL3An5x2zkJ0ugTfSc8TFKHH'
        b'cOuYHkUoZKnFZ3s0oX4rhLk+R/Y6vTQYSw4czjXmpmFKZ6vpR27ZqC/jJeiRh6kHfNq93Xj/tY1Bu0VanaClscHDpaXZgNTURFjMhTEzvABmOhzm/PBhXK8PxA3xC+XG'
        b'UodsbgiUoH9yTsYP4RRcMCsRygWznKEsdygXTmvnG4J61C/QFw8rZGpQ9XUd3nihVI/eHtYRXaAqIApPLhXQRvT2EA+bZI9eeD9FZ+o94aVNqEniUu9xTEHxgheM04pH'
        b'oOcVFEpBQZHB0XtWQHAA7rBo5Ewk6PzovrLj0+Mw9fZaTB6OQCNIs5hROTu+mYyp8gsA6FQEiiB7jMK1KXvwZXsiVD/bnoAS6BUFrP7160HGmDlEjMrK5Nw6LXJYka3l'
        b'/hYAfGOcdrE6dYRA6WrTyVMQ3K6QB2JKnFEFPl7DWoxMBoEkibwcJaWyJtIPINdYLfRCHvlYuxQpoOqKWULVTxpCkaJ+NE/f6VI1olCI/M5gORqsGyhBhWUxh9XzhMiS'
        b'PKDh4YUS4BNNr0xYLzD+5HKAvigvtxBYufmU7ZWsBLFcHMU6mBIRmRhH9SNjEbC+5/DuAeRlVlNlyBg0M2kLTFXZ9PYRaxyE+wgg5+2UciMr2QSUewzID2ycpCOedAXQ'
        b'WyPi8R2E72STE4xV4RfiPaRLKljH4rsI3y3CV9kMxCrxHbKHowdc5KkKqfDFINbw1WDAlYpmnt4wEhNfK+hqx5Crkfj8TLKH7KUfkIXINuB/R+FGtk6x5CG9LYWjzs+X'
        b'h6Ph4+awUvPwdnKCtGRHzHGccwpnnOuAW6U9WJuGNxWx0xuO7OJmJIcN3CDcyNOFj4ymPi/4wLJ6VL9IzmJl+dmYqt4K5q9Gq8kD8lhg4HYoyG568ItGk0dr0JokvIcd'
        b'sjJtbUndQQqw+Occ4gasZ0eo24z+KFR8kYGOdEO+cK46NZ6+s2cGe2dP/kuzhMiFVbC+ZbyUvnEnsaxciFxdBOsbKhHD+ub+MqFCiCw0AMws+pYfwEzuhzUThchlZnpW'
        b'W+NHp3H1ao0QqbRCZIyZg8jc9AGThUipHiJ1A2hkjFI6DRlLXtOLrUB50I9Vr9bsys4XxYfOuvjJGxWV47esLhnz1rUZSxQL/xa2+6ZRHxTd+NPvDxOvQPuaixT5G9PE'
        b'v8rvX9K89Q9f/jD5QsIPLi38EMf0P3Bf99b2k9tWSAeO68y+FH0/IeqLnzdNPGT844Vj/097Vx7X1LG2TzYIECAiCoJo3NmV1Q2LIqiILAWtuBIgASKBQEIEFVdERUUr'
        b'4o6CorZuWAQVRfQ6c283u1rb2tRWb+t2a1u73mu9tf1mOQlJSCL29vt93x/XyCRnmzNnzpyZ5z3zPu9z/pUr+deuel8L69lxNK/sywUXIr4a07h745jrsbM+luRv8bl7'
        b'3F29aEjB1n698sJS74Lv64+ebJ3dVL3p45+cc+BNhVb92/O36u8fzrj2ILj9uPt52Ti3CW4z3LZp3zg56eEwOHXHvfsnwzv+wshF2cs/+vn+IM/Kz3/L9cxe9fk3G7f+'
        b'1HznQ2/nNFHD/I+3e2yL2eahmzht0eayV29sePG5zD2n60Oc3trTfPv9iV+7/yj9uNLh0ZL+/xJ2zL407JclY3qNvDz/xqZbX6f6VX0rC/55rcqdX943vMrPk3oN1nhx'
        b'6ZwxPAl2WHMcBNu9YB1V92mxRzAGu3kcgFsCkoL88dh0mgu2w2ZwgtJwXoJ1sN4h3QxqINv1HAEFfNBAdGv2ZXV6bg6Bp8jQDi6Mho14rE1MxBPNYwNxoGPMgZ/AA03j'
        b'S8nwiYWCkP06FQ2GtYTfXsXBLKKBCL80kQEb7CrB7p8mgAysBRVGDpyOcCNBZNnwlJ0AaxHFB+B3Ek0c0ACq+hHA4x4FV2A3FbB3sH+Q3k8F1MP1pBochoCKTgkjBAqW'
        b'gA0cpnc63xvsiCOobdzQNL040TBUUFwMfCFDeGhY39yb1MRShD8qMMrJDzL4qYJzwwiUyEKo6RiLYHYlmgOY+bCa1DVnehgGEsjm2WwSeUAO95BcyuEl2EJzQffnpBnC'
        b'mQhXUfZTHdznhgDHlMDgRFUwfouNCgqP8ODW6GTiKAA2gZUIrJk5uoJ98+0Zj778KLhhALmewAAEuhqWk/02JQgYPpcD9nHtCaITeg5MgNWg7QWW8U+m/svAaeJhEOvi'
        b'18XDIDlXZeZhcAQeIVB2OmyA21FxI1UmUHUeXEFdx+rgXnS7TQEbWIOapTFiAydhC23QWxjQhnKDh0GNGdrapKS+xs3RQwP854PtxoGF0mGTfmK5WzNkfOysRxCX1BRx'
        b'qUUcPlcfVMCd4C139OmNPp7og5ddSIABd7KHG/uHP/ogOSKuI0fCxdOpIq6QUL8Wu3TiGnxiK65tNvhdxp5uJ1DyrQUoVWsyn2Z2SpQDUZn8HffjHHUTyTSJ/FdvYQhs'
        b'fTqxK8nPw1wQFfv4qjFqpX6/xCEY+wLrhHoPUf0vPEdFfCspGwv7cxFvDjLdT2aCyTyhTpSRMiF1QmLG9FkpcWk6nkZeouPjcAE6J3ZDWtz0NIInSU3QuvzPA1CosVZb'
        b'IK5WXHwhT9yjWxQsgQvfxdnFzl0otteHmrAjLcHO5OPIoy2ELnHNtuo/YoELx53nGUte7IPVcF2Asf+QANQiCCSezpsNNjmbzFTrdVo0z5mLw/JrXYl4qqv+WzbM8Mu+'
        b'2l7mi3A0Jli45mAqjJNBKlYkc17NyFxkrqxUrJgs9yDLWCrWjSz3JMtYKtadLPciy1gqtjdZ9iDLWCrWkyz3IctYKtaLLHuTZVEtP4fBpZL1rePW2mHiywJnmU8fZoEL'
        b'poiwy/30yx7obwd3E0fmx5LI7UlkJae1rmvFOQ4yiWwAlYFF2xyIqCtfNlA2aLVwthjXhmxwNWcttR9Ea52R9UAEatH+PWT9iRewPyv4mpAU93i7Ce96ul63FG2iaq8S'
        b'XywCglWdMgtluJUrzOUlTRb8p2P6NyvjhH6psjQqJVaXxqx1HMqXCmXiUMLyohIazZpQ2M0iLFtnatrrHFhlMizrw/4kc8tCGnEUC/zIchbqePmFaF2BXKbQFqB1wiJ0'
        b'NaUqtYx0EtQp1lgh1jSclT5muAMywRzZ2WInQzirp2nE5vnx//49r7sasbiu/7BG7NMlYrvIwVok8P9BiVij+jeUA0cdt1EKtNlaGQolmcqivMwgS0UZLcnOQ6fMJrG9'
        b'bSvW2hastSBO+ww18lTBWtT0aBjk2EkvSJSZWVgZHf00jiztF2wWs5nqr1kshWnRSd36hhpVhYXCswVBzf8pcrnWpHEtR3iwJpfbTWlci5l2yuVK/rg0rv4Rp9VOlyQK'
        b'GXvDwp52w/T9Ahv7ml2SqOW5Cg2qYdRHoa6MNKdAiZa9bdpCHIP6mRVoXenbl372yJplGGneQqny2HAP6rOsGpFqQYD2JVjTqUCLgKWJ/mzleJEYbEwnedpluDO+aFC/'
        b'HCct/1XUi4ZWlfuD82aZgotgJZWgNWRK1FuM860vEsGDPexIvi3jRNjPpcgnTRrYL2gxlbVVlY63qWpLFWkvpBl5WLeBdU5gP0LUNIDuQBnmbTDplYOkgb8UuTBa3Mv7'
        b'5eJQtBbyjQ9Ig+eExg7bK+BmB7Atg33ddNjDAZMNPD9TSANVixWMFtPxhWB3T8vattjUo3be81MSYbtJKc84gcaoKJLrpSQ83cOM4vlIRZP4fEaLmf6wdUGBpVx9kSkT'
        b'TN1xwIvIouzM8zw45gTX+YBWRWrE3xnNetwynhwIeuuK81uSmBBR7Pujlkf7VsTcX8m9nj4lauE6R6HTzIl+1/4qqz2k/fb6yHf7rREVd9idbBobvHXysn3zs4pfn1M+'
        b'++Dfz/DHwtCCb7/UDYt0SJyQnee/p/Vej1uV8285/7aydPHKGcsWPEjLrrrifsfjzqunTibv3XTa51b0o+LHS3fPbuN3POFc9Rp5btkNP0dij0X1lWBzqELd2dKobQn3'
        b'ZBKbZWwfP6eEpeB41/ffbbCeTkq8Ai7Co3oLFWwDVfq2JWD6w53Yvbsxh5jcZeBssmOikY6ukZ36Iqgmhh2oBIfg1pxpRjK43LCQucQ6mt0frgC7cRRYIyM6HR4lG5eB'
        b'8ypQBbabmoTT41jjdBPcC8/DNXqD38Ta7wP2Ejsatg8EF+CJZGqfmlinYH9xCQ76MK83tvcxbg2CLfCMhry/GJSLlqcRHBtkxySC1fZgL2yG9X8afDeQIvHDYmTQLWdi'
        b'iNwtx65T+pbK4JIIpoYlvbosAhxWhHDbcHIOJ+dx0o6TCzjpwMlFhnm6K6ywO5k4m1yTHzpQg+1sI0tvBfOJSXC4riXvLpHPMcMAlWxQ3mbwTBVx8ZmMFHHxKpuKuN3j'
        b'UubpxUqNcJONQqXrC/W4n1kJCA54BpVUA81Qj5BsnHWO4az96Vn/uBIvyzjkZyBUZOOM8w1n9KZnNMJOzy4Fy89A0MfG2TINZ/PthEeZ5lTVZ9P6NUjv6sGIjfPLDOf3'
        b'wu8vjBDLH7qjesRi44y5JmdE9WtAOcZtmEsZzuT9hsGPNimbxxYEO6Djp5U40mJnfzI7hYM8cFn71JFE/RXliAzu6AKr7uh6dVSBW7dFleRYNbK7mkpk52eRVDKWUOqS'
        b'JZZUMpCQ/QMl/sZcaLRMyNVoJ2NBGIJaaTGwzkb3LTvDicZI0lQF2D6g9jSOyMYSmjOzVNoSVqlIg5CotbrB/7AqiBxXiUyRQzRjSlikbXpRbH2TMJOo2nLZeHMWQC7+'
        b'F2/QOMq0ZbSFRBqZKhJfvZCKdaPFuF4pIO/yYEp8J2Sp5dl5hVjDhbXgSNQ5iwXtbAcajSK3kDQFqpTSRa5LI1EYX5UCGTO5VuRY9EZKCLnJkaMNtgo+U4hfIH4Dohf2'
        b'xXsYlH2zrZlXpFUqyPFYNQrX3ajR3VedyjG9IHzVCrnmz9OM8sUaSUTdyU/i71+ADWh0OYv8/f+wipTElyhGBVHhpWfJ2oZiVLeOf1b9JokV3Slr+k3B3SuGCZvDpoqT'
        b'r0HFKcRPMick1LoKkzEjhL2NWjm9HEUhKSjRWo9NTJw1C1+ZpbCz+F9R5qICErRWrsYDUyCRaDPYvUYFCrVdIJvSUqZvQejTMlz/pFgsFoU9xoJU6PRhI6xrixnzZ/Tv'
        b'hIweE7QWPZGFGgUtlCrHslSXbAFqGaQ+8AEkcm9mGf7dTZUi/G+CSSYa8jpMkZ1XoiBSVJpOobSuz6zVPIMkIVjiWa5FnashA9SCFRK2ilAPVYCeuLgZQdMzS7Lk+BWj'
        b'ZeGsIAlqLjTEqFJbkC/Ps1z/QZIws93I2TK1OYu1JXI0cuCozZIXVGoNKZSVPMLHSCZoc/LkWVr86KEDJmhLVHh8y7dyQMQYSXyhTLFQgRqzUokOoHJuGrMrt3J0pKUi'
        b'P3sFjbSUjcKoWAXPVqxRlvJ7tnoZTSqys+qfUvMWV06nLRm/CzQr9zO3ROPLz1Gjq/HFdWsoU2bWYm2un/XmZ3y4ZOQQ6w3QZMeQ0db2RM2scHhXpUy6McI8m0hr2UTa'
        b'ygY1CsP12chjlPFuVi9ttElmFq7L6oDG8vtQD8f+IngAYVLUt+q7ct80OsZaHbA76YNYoh0NhXQJYRzfBLQoL0R/qJlL8Bg0yobKu4F4aJpNqFk2oTazIRxFEzlBX6Ih'
        b'GIvHmwirhxk4jfTQuBmkp8YrJL7oIWebOLrt1qtBq8ayilimnv0VKDHCdnEzUiW+M+HBPDV6SFFZwq0XxYhO2ZmZYTVbKH1WmnytWtO1ULbgnjV4SaBk95GfAaJNMHmt'
        b'3z0MQwigYyRJ+EsyJ3TEvO4fFkoPCyWHWb8bemYpCyHZZWws22oHhHaKDsFfaMeu+1nvxabI1erC4ZPUmVqUKIOHT1IgdGe91yK7W++rcD7W+yd8AusdlK0zo14pLg+B'
        b'MNT3W++aSNkQZpNZLoa1ykMoVi4vwcgCfyOAFWkT32WpysZI8CQxwk85GLWiFajOrd9UfBBm/dKjMpUSvGDziGxFCX4gUWoT7lGSM96T/iAZB2KcHhQWEhmJWpr1MmGW'
        b'MSoQ/rLZInMy0dVOQp2KrZ0ITxndIfwlmRNpfUe2m9Mrptpo0XoG9RhJDPpFkfCc0JE29zc82uQQ02k7m/Wt52WzR9L7Y72zxnxsBNFiJiSh22O9R8xSZKMM4yeiU1t4'
        b'Ik2Y1V0dl9mIQ+/F85iUHBz1WBoIHXg0VE/USHiYKC+CQz2NCXEpoJIcVNhbwIjme+DwldPWhLO8nfLQwoTZQ4wIeutdyM7NSz2Ysoh5DCORzn21ZAnduT84xlANDNAE'
        b'O1C6ooycGTRGwKMJ0/qDA53EZ0x6hg10CqkjsZzzk+BHHA5zbLN3CQ2HCS7C/XjWA/2vDMdKgsnYTRAcn5pIwx8xsBlsSGXKwh1y4eEUQhO6YE/iHJW9NxJLJ07O+ppO'
        b'canhRUfTMEdsjKP6WTijKXQuwkQ5sRrsEvmBvbBBUfptBl+DpTYbnyys3DSuEIwXV957W/eg/8HaHj8dEU++xVcMEtyffOCbYOUb6yML1ykdt0+ZWKFeNb3OuVi0sMV+'
        b'SsjV+x0jb0b9bW2vugHHb8z6V9Ojug2jJ544JXO6qmtZMqPx0N34HjW/7vG4VpPu+q7H+se7az7NOvBb3Pro3U6tk94cHxb079vbKra8+eW6Le67I3KA8ITueMCNeRva'
        b'Fk35rLnd5dxbWeromVePOpy7+Sho8KTjiolPQhsvLzzdvnKo3dJx/1DeLmveP+/rPtd4qiOuLcuTSvdnvr+6yUPi9kLVd7yzv9YP+GnSh//gzJdPztmxz09I55SqQZUP'
        b'JodMTKL0EMwNicsi29LAy2AnOFYKDxjpRa3rQ4PAnwRtoDkAViWD1fBIPDjOZ+yU3IF94S4a3f4iOAXW6gMl9YDnjWbHygNKSADUfWArqOsyYYR9JI/6ms0YjYiiDpDY'
        b'jfw4jpU0N8okWhIbK8m/B5mXe37YEFalbww4T4X69CJ9PgklhApXDfbOS5gWD/dP4TDcVI4/qIY1XSkdoj8p5jd2WiNzVHj+2WSOajmTLCRae3yOC2cwiZyEf2MHQkd2'
        b'fopL3A+90HdvjhtnscgwE5MpkyWZROzofFON3ciNJqUcnqngfnyjTDrjexquZIHFmamdA41npkxKaZnPQaIwYXciZi3fEIXpv7JFXbp+vsWun+WsjOuPoxCkezmNlyp/'
        b'dYpjKdvVM8M0WsxHruYzg+AK9GRwlg4aSvksmJTgGpvkxCMBNpiZzMxBoJUc9pywHOwGJ9LocRzYzsDWcLCaChb1Lec84n630GlE5pJ4gSMbnGADevZfAq2LwsJZPspy'
        b'0EgZH5VcbTDcEBbO8lfgDriGBsebac+ImJRwJ4lU6bNoPqWfbOuHXT/aHERF0mlXvBzpyjZnZ8aTeU/GpEhFZbwYutIzHHsf3IqwF0sDK5ekUXYObOyTk0ZIOE3MAGYA'
        b'qJIRMmwp2Aca4EF4MGwEVjDkwIMMXAnPg/0kp+8HuTB9mfTBziOkyoO+4TQ4F1wF9k0i5GXCeIFHnyekF4ETvdwzcCulvfgEY+JLDawDa0h9jgGbe4Sh/c/mMZjwU9mP'
        b'kjyOhcVgqgrq1g4wQUxQDqykbNsqsApV9GE04JkRU/y8KA8/QslcZ3Y6CFOkk8Y7pdPxHNYE5HSG3mOmgpU0pP0lsI1QR+igrsU+Hy+qHaXSwAqPvnSl76BejC/z3SjX'
        b'8dKoXK/ldOWbbpeZFRyxt2ORtPhhMRvioRSuD38uTuMchq6Ri0f3DrgLthK6R1OIGN2jUfacImngveT+lAPSkY3vUTpfkCJVfpDqQlfmezihe5Se7SiWKiPzvenKrzyw'
        b'a8t7A/kSqegzfiLlBcE18WBVT1laSkoKuj+xDFg5sC8N8NG2BB5MS0GPPrq8l7jgMLpzYC9YSQqphLXz6LYKuIPdtq2UqkQ3wgNgPzgHdxnlCVrRLcdluC/BMR7ui0VS'
        b'qUhQPowN/1EH2sHGNLw3XBXCwAomE+71Ift/FI2bZYPcuUgqutPLh1F895qfQDMWdWaPD5QWbDmXBMe7x930fu0Tn9dXTQQX7wT4/sIMdvQ/KJznl5VX917K9Q+FbxyK'
        b'DvqCJ464Of7y3lFVqZKEQTfDVJ8vvbJBFrp1mtPS+ruvrp8xrDT1/gdLc9Tx1R+cfSPqbv2oSpchTqnZ1Y1r4ivSC4fM8Ja80mu6eDH4t/jDmS07D2yPatwX8OML7xe9'
        b'+lHZ4hlnncN3PfT8IXNSzNXBii11x6tKHfbWnIlPLs3Lj9tVFW2fO+Szx0HF+8oPtHx4s23Kspd1keDiB87DZd9vuBKz1T/+pQsTS2fc6fdZ+bbPwwLbNwvmxd7//sE9'
        b'TnZ56/iOH5fzeXNDfpNKWkICvhm48Kvp8n7RjmvO1KTKd6vBhuHRERcfNtdPvNsW/O/Lb7+zeuiDd5Zql2584cPq1xvVHz0IAzuX/Vyd8ea44ujJN6qjpmT/0/7HZDWn'
        b'z1t+7mTw7wM60K3tOvaDqnnm3iLgdDQVSjgL9j8XQBAFjuazDZwUwnYu2KIC5wiJZN5CeADWwHMBUxOncRj+AA6mnU0jJJJx9rDNIKEI28EaEg6xB2wjWzkJsCMdnjDn'
        b'5K6JLRlEgc6LQ8zjQGACixvYKokTOIDDXiSXwbARVMIjOAKfkQeOGzxBChfplk2DrbIUFlgzLyxwCWW/ouYLtsFDs0yILKyn0U64h0pENsDjaMdjU42oNikuAwtBO8kD'
        b'tvVNNfgOvQQvmvgP+YEmUoYgWA8bgheYEH1XuFL2xeGA5xNMwqLDC6DaBVTwYsaGkwJ4it1MuLJn4EFCcZkzl7KNDk+EWxOMo6YHveCylBfbG1RQsu2RRCV1HYIdU028'
        b'h6bMohd4FtTBWoTLqkydlMRTKO95c2lpp06lA6ggxJVY0EzQZjhok+q9l1KBqQOTzJvexhpwUGZcw9QJC+yGzdQRq0+u1TB2tsGdSg/uCruCuyIM5lhhNq6YS9kDYpbN'
        b'i7klYgTu+qK1YgT2OqUqxewflxV0c8TilSznRMyyCLAEDKvARmCWbZE3y5fWRe4NI7u+5shuBbPPNASj+UlRPliF6E9Wfcv5r+pbFyxoWfXNnqq+eYBKHzPRN9Be0Kn7'
        b'RkXfwK7hBM3INNOxfptS3Kng5hmjxS8RCudJAuwTkUWP1duYGTSgR+0SWB+QzGVgvSuRb4sYoeg74i5Hgw2Cy8fmjnubaLcJbuUOE7xZ7zmKyZLdZqbNZV705Sl3hUp6'
        b'eY4Z7JTzHT/gtSGKIWfePXWzxcs1eUHltwlv3/36U/9PShanT45Jvgo8VglPXxz23dLXFJ/mvTmmUdzzyCz+o5XSDVd+fWtLo8PtK3+5LOz5VXZluKtg9YPmJxELfr+4'
        b'9bVZq3N+VKWXOr/5zZ3YAmlmbmV0S17Fzx9c2+3Wq+/C61+ufrxn6Yg74395zHl/bZi7XX8/VzYkwlTQETBl4oRO5TZ4GK4jXZEU7GeodNtscEmv3sZdCvbLSTeaBSox'
        b'4zEwKXSYQZRN4U57uYa+C4goG5FkA+uG6VXZYBsNEAFeKURQuAW2UsG3mbF6yTdwFDQQV00pJzUhkNVsi1azqm1xoIWW+lLgMCLZBtbBQ3rZtsGjaAfamDcD9ZA+vUxF'
        b'28DmcdRer0O96l4s2AaOIBisF20D20JY5cueTgHDHcFGM9E2cFZOz3xMBHYQzTa/2XrVNtihIH1zshu8SDXb4EHQRnXbuGB//1nkgia5L6B6bQeXGCTb0Ji6jZzWG9aj'
        b'4qCBNw+NdEZjL0LI9O1EE9gVhDXbesYaVNvAurw/RbaNaICRjtu/a8e9nAkaaFu5Dfd/f7pyW3++PrDyCrPPlxY03PRFsKXhxqfMHrKdEP249OT4K8nPzZzWhx3ijLh9'
        b'3fBaPcWQaO4l8gINJeeZ6av1+I/eoXTjNp5ByQAe+3JFaMfnovGV29u3+3Jq+AZ7ciSlbmMJ/24EMuwuaQzAVIDMyCrG2YuLjLVNYIcfJ0lxadpQgcYbDU21W53iNr2d'
        b'BMa7Vz6cNue+a4rjk8mrJxff47WJSwOTvHq69dZVVynrhp79+UhHmvfbg9++ofp2dMYluFlT//PK51M87j2RPXyv1xtfb/zx76Vr8mctz7udvyhh+ZL5U3f2Wv1LxSUP'
        b'+anS4s/fObFKdW3H4sP5R17f99v1Beteu+pxfs1LRzKFZa/2ODnqboSq7IrfvQv3JvYcEHvtl4p/Tflhn/Dd6/lRga98XR5YfXHLhRsjHQP+GvNFcug7DUPPTBoY2KfP'
        b'z2P3D+73N80/DxWM1tW8saP4jV4fl7/W7+Eed2/lkPYI3ct7YnTD1V7hC/vGq9ZccLKb+bj1p19/17wqaK/ZlNJQW6L46dbG+fklQ3NDv7l7qmBvza3srQ0xQbsWhy94'
        b'r6fgZHTgjhxx/Dt+PLbHApvmwg0IjOEwfvVgH6rDSriPdIa9xeCAmQgQWMsH2xYJXeFaCtrWgyM8J7Bnsnl0dH1s9FPlXV/aef/vNLhnTlBPxNU/cBYTQkgWZmQoVZmy'
        b'jAzSE2HlI8aLy+VywjkS1PPYcdy4Qi+Ju5e/e7T7sCjcL40T8lychi5nFqqvGp4xno6bkWHU7Xj9P7h6jvoDwyOKS4oHIRqM+P54YwU4ErCnvhQNHRvAZjQGVCVPg2vh'
        b'CmQHbLZnXPrwfMB2eEHxesMxhkgGcC91+FS94QjGiwXtufWevS5XN9z6If43cOoj8eC3bkQNHVaZ+/vp4qQZcUOSahUHttgtOzIyOeqHhq2754Uc+j3ii4ATq3eNaf+i'
        b'8quw0bW+Z/jFpwsK34yZrqjMb78QGBAyTTLCPXygyKv1laL07IogBB9WDBpTVlc06S+CmTeKHrbfTnvEfz/jScOjXzmN53xD3+mN0ASJl7DWEb6CB+ZkPGuxMcEeVoJj'
        b'jBM4xYUvZ4AVZJ9c0ACaEpKDYDNm0+8Fp5LxAN4DXuCB/YNhA9lnAbryJloP2DwZ1x9bxagW3Hj90Pi6isCPYNielRCf6J9oj4bDJriSzxWCI8H0rfa6sv7gYjncMNyO'
        b'4aQxxCCtLiFvWtbB7fnwxeSAqQJk7jJwJzhNYcG8CBGRD0Rngxs5QWAj4+THhS+6w81kczmyjTSd2+FBD8YxngtekVOR2whYNTOB9JRV4OBkYlC5wPW8JHAa2aW4sDJ4'
        b'JpLGe0TDfBOZUhoCK8jTPwGuhs1EP5jOyAgWwdOMqCcXtkpgLQEHZeO8kVG3PrCIbl8mZBxBCxe0wm2TqRp3B3w5F+1xSgTWlRZrYUuxqFhbBGs5jAfczENQph2ep4EV'
        b'dsO6yQlEUQNfCxP7PLo3u7nwADgeSWg6EtCKiozqfXiCFDagLmYTnjPAK+wZ78F8UAFPgAqToNc+//dPmPkD5/CU7sZC79NJniHCtc5CGjWKiDdgK1XEe84cFg2m6IB0'
        b'O/11PKW8UMfHntw6QYm2SCnX8ZUKTYmOj81CHV9VhDbzNCVqnYC85dbxs1QqpY6nKCzRCXJQv4e+1NjxA8vBFGlLdLzsPLWOp1LLdHbIQCqRo4WCzCIdD9leOkGmJluh'
        b'0PHy5GVoF5S9o0KjZwjr7Iq0WUpFts6ecqg1OidNniKnJEOuVqvUOmdk62nkGQqNCvum6py1hdl5mYpCuSxDXpatc8jI0MhR6TMydHbUl7OzK6UX6qN+iH8/wMldnNzA'
        b'yac4wXOF6us4+RInn+ME6/Kpb+HkM5z8AyfXcPIxTm7j5D5OPsHJFzj5Bidf4eQmTr7GiQ4nH+HkQ5x8i5PvcHLH5PY5GvrVR7FG/SrZ9liYgx22s/OCdeKMDPY3O948'
        b'9mKXkQmcnZ+ZK2eZ6JkyuSzJT0iQIJbeRQYvK71LsKLOEdW4ukSDTWSdnVKVnanU6ESp2He0QB6Ha1v9g77ezFgXOmFUgUqmVcqfw6wJ8p6Bz0Xdl3kTG+lOQib8D5Vt'
        b'1/Y='
    ))))
