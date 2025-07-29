
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
        b'eJzsvQdYVFf6OHzvncLQESvWsTPADL3bQFQ6KKAGVBiYAUaHGZyCil1QUMSKvXexothFTc7ZZJNs6mZ3k7D5pWyqKbvZzWaLm/K959yZYcaZISbf/r7n/z3PX+RyT2/v'
        b'edt533M/ZB77J4DfKfBrnAAPFVPMVDHFrIpVcY1MMacWHBWqBMdYwxiVUC1qYOoYo6KEU4tVogZ2Hav2UHMNLMuoxAWMZ6PM49FKr7SUwmmzpTV6lVmrluorpaZqtTR/'
        b'malar5NO1+hM6opqaa2yYpGySq3w8iqs1hiteVXqSo1ObZRWmnUVJo1eZ5QqdSpphVZpNKqNXia9tMKgVprUUr4BldKklKqXVlQrdVVqaaVGqzYqvCqG2g1rBPwOg19v'
        b'MrRaeDQxTWwT1yRoEjaJmsRNHk2SJs8mrybvJp8m3ya/Jv+mgKY+TYFNfZv6NfVvGtA0sGlQU1DT4KYhTUMrh9HpkKwc1sw0MCuH1weuGNbAzGFWDG9gWGbVsFXDC+ze'
        b'I2ASYToqZYLcCvt55uB3MPz2JR0S0rkuYGTeuVoJvHvJOYbEMWW1PkeHVjHmUfA+fx6+jVvwxri6vOyZuBm35slwa0ZRvlzMjJ8mxA8EZhlrHgIZ/VATPmXMyMFb8OYc'
        b'vFmMTrCMVwaHOpYtl3HmQZADH+mPj2VloL2oOSxDxAiFLDqCjuObtPgCdD00KyMsQ443Qnkt3ihi/PAmQS66OQiKj6DF0TkP1II3hdVChzZn4EN4q4jxQp0cujYEP6C9'
        b'5czoFGS56oOalyw2487FPovNIvSAZQbirQK0Ge/Mgd6SjHH42AzUgraGZ8lDSI/xVhLyYIaMEeKDk1FDSXwF+xh8DrHOm5YsJL+MzM9byMohlkVkmwGOV3KwiCxdRI4u'
        b'HLuKK7B7tyxi1eOLSDozwGkRR/CLOLhKzPjAZtKGlGXPXpjG0MjQaQKyspI3vMp8apeH8ZHq+Z5MAMPk36kpC2tMns1H+nMiBv4uHZlb5rM8vJBpZ7ReEF1XMEj490Bm'
        b'ytd9/+39Gncj0ljYwGg9IeGyYt/qbWyZPzOlLOqdKEWMiI/unPNNYtuI4BFc/vvsD4MGTFYz3Yw5AhLQg+GIwFNL+MzgYLwJn8F3w9PleBNqLwzOzMFbwxQZ8swcltH5'
        b'e05EDfiG0yp4Wweeza+C41ZiyBpUettmmXviWXa5VcROs+yTayC9MJPYxImGglny2RzD4XV9BAw+tCTWHEAA9cqiogJuOUzjaGZ0NL5Q7z8sMbZgFlRYzcTVTdMX0tIy'
        b'fBRmYqcAt4UwTDgTjlsmmwNJ6Q3F+CDeydahNoaRM/ISvrHxaPvqgpyZuFXEcGPFy9mh/SrNY0n2qyNxE9kPoVkAxRuzZwaj9rB0sj9zpzEK3C5C65Zn0RrwUS98AnWK'
        b'8a4ShpnATPDEDzRHfnzAGQ9A4lcNq+e/HOmHInzWK/+Y093YXuD/TNCgfXOfUrYuTRlQXlN0wzRy1re3puGM+phZ27a9+NEHyx9s9lL87Y1vr70z8dCnO31iastOJZtL'
        b'1LemJC9c1Lb2gxMmj11P9110bFzG1NCbb4d/vfbDO9FHz6uGPNi96Lx6x+83dD54X7nn2dLw4EnfH5zcMvvhmZXH/A6cqg7+W8Mfi79XvR844oX33v18e8I3W+fJRCay'
        b'/dEdfB01ZeHWUNyaI89cEkBwSCC+JYDhX8d7TGR7ojbcFT8S7QzNlOPmjOxcEeONrnCAKHYMNRE8jFuGeYUqZJmhFMmI0DZ0kfHHawR6vBN3mIaTHHfCsrzJDJrlIegG'
        b'2oU3hXNMH3xHgC6iqxoTwZ0GfCYbJnwT3oo3w7ZC19CdRBZdwbtTZFw3FywzEGCRedM/v+BB4O7RgAmVBn29WgdUhdIrBdAadd2kbl+DWqdSG0oN6gq9QUWyGqUEWCdJ'
        b'2ABWwnrBzwD49YMf8jcQ/gZwgaxBbK1ZJugW84W7PUpLDWZdaWm3d2lphVat1JlrS0t/cb9lrMGDvIvIgzQ3mXSOEkMs5cQsx4rpk/uO42DnscwPJGQeDem+6DA6G5qJ'
        b'W7My5GhTOKCBLeGZLG5FW5mx6IqoFO00OuxM8k9o+WusJpiMMAvAKKjYYgH8CjVMsQj+ilVcsYfKr4mpZFVClajRs1hC38Uqj0ZJsSd9l6g84d2Lp8uVApWXyhvC3hAG'
        b'xAJhH5UvhH1ULGUu/LvFs+jk5dLJfPgDYKcKgV23yOg9rEiD8DK2inmMJGgWAEYSAkYSUIwkpFhIsEpYYPfeG0YSOGEkIY/3N+RSxJ0wPa1Mu1van9GkLlGIjHmQ8qP0'
        b'N1+UvVT+WdkOVbPy87LNVRfUn0G4+Ol5uGNb5PqZB4/t7vOrPOVZpVZ0jj1X9qJwe9gwn3fN0xTDNnvPTV7z+aCgWYPWBSWUMLUfBxxo5mRiupXQFXSpNjQrEO21EtBQ'
        b'MeOPTgvqcXsB3SeTi9GxUAt5rUEngQAzPmECD3xkuomABbpdj9qycAtswqZsYClkYkaCNnFL8Q7cZaLswhl8FK8lqC0rY1Ax7FRGnMAF1U41BZHE8wH4PGrJywhDu/GN'
        b'DCEjwgdZfCc2k6bm4zNzQuWV6EJ6BsESEnyNQ434ALop4+wgVuBq61EA7paUlmp0GlNpKd1iPmT2iwNY8iNmhWy9Pw8FCmsufmuJuoVGtbayW0gYw26POrXBCDykgayO'
        b'gRDFdtbarh+J8iUPf9ueIY2U2PbMmQC3e8ap9QrusY1hg8AkCwRWchb44yhFFAD8cRT+BBTmuFWCArt3d3wH4wb+zKFkOU8Dgt7ljVthwbYAecdbC9JxC1nYmfmUSMZG'
        b'T8bHxH2C8HHNvLmlAiPhBo4seO+LMgKMwRVhgaHKbOWXZQEV1ZXacuGm0LRIedmfy+Y+P+ilp/exzNH5kjVefjIhXd7UUHQ+i68coAa1pFHACUOnTSMhNWUx3oY7AcNv'
        b'xVsVcnwIHawFICR4fPAqIVq/soSSCim+CbBHACgD7UddVgDCjXifqR+k98Hn8MmsPDnL4Lt4O1fHpgycxC8z5xJiAIlWqU0ak7rGAjQEBzLlXqwPWx9oWzBbFr4qIQWC'
        b'bqFOWaPugRNDAN9MoA1KKID0gUeFDUCO+LkHEBft/a9hqeonhpIQAiVr0vBOJyBJD+oBEwok5XiXJrl/NWuMgjIjal53DSRflnGboswRb0WcjBBG195gPt7GXJJL1ppO'
        b'yAR0ic1o8+IeMCEwghrQ2aUgzxyhgIK7VPhWD6T0QMmSMQAnYbidoqGSSegWDydCBiCliYeTKrOFnLrHIQARRmeIqHoMIoyOECHiF5wsfbeoTqk1O8GFwA4u+tmAg8x2'
        b'tQ049veCPVw07R6BTOKBgzDZbKXwv4FEWEsTjuAhyjVHkhVZgw+jTiIGFuJmuVwxMz2zCDfnFQTj7egq5WvTgcVVsIwJ3/MUp6K1FKjwrbHonHvMo4zggQrvLNN0zszi'
        b'jLkESfw6/4uyzwGstJUhA0KU6UotBahaZfOuc+qzy4KUn5W9Uh5GAS5TeU4ZUMG8MGATO23fwA5TRJhKpUpXSirffwnkyKH+x/sIgEUlzKMvOjDfxjzeBPGlh3lcje5S'
        b'oojuKNF6G1Dq0D2e6GlRq4mIpXm4E8RXZ5DE+9QEd/XF1ylMssOH2kByTyoPkegGvkOxI1C6LnOonJI+dH+khfqhO1NkFvojdMt38oArNtcSdrOH9Gm9gLeUUL6y3tcC'
        b'PnweezTGUzUbtDptDcBoPXSPAm1/eNTYgHZXoHugdWzVSSh0RGZUMLchM7aZfWIhsPFxaBW6hFZBrkZZUMMaMyGivKoqS5leNemzLwGYXiyvruynPCu6MmhghFxFgGmj'
        b'8pz6gpp7QV52STnv+bm/mYcLcT7W4vzg3z8zV/C7Pi89/TbHiD/0b72+HogbhZAto9E+C4Sgw9lWtigNN5gGQnI/dHMlakFrZ/LLz699cKqJKAR8V+NTuEWADodl4Fa5'
        b'mBEv4EYPD6LF6qvxAdwy1ocwU1ZWyoS2u4aF3rAaSA1Gk8GC0YhqgDEFgJzhA9BR79eDWkgWWqpdwC+4e7gAtqgHJMgwzDaQaO0Fjz3WmIzLNRDdgMyXMG+EoIJk41Va'
        b'ymv24N2ntHSxWanlU3gEK6kAYKrSG5Z1SyzMmpEyZN3iSo1aqzJSnozSXYpfKbzSHlpxda9CHD8gMkUFZEAEV0s4IWv54fwkPiIfUYCEqsbQBXQG3/amog+HzmWyjMSH'
        b'K0ta5F7uUTCPyT1csVAlIHLOQa5Y1MaoxEdBzjnGNrAgA0moOOHZLZ6mA5S/7FG/NHW5xqQHYTI8y6BW8a8PebbjIWniUeBstaHeXGWsVZqNFdVKrVoaDUlkRI98stWm'
        b'epNaOt2gMZraOTrrD5+DEX+7D2Y1S68z6ZNzYZalwSkqg9pohDnWmZbVSotAkjXo1NU1ap0s2S5grFJXwdOk1KlcltMpTbjLoFVI82GN9FB2tt6ge5J8ripbpNbo1NIU'
        b'XZWyXC1LdkhLzjIb6svV9WpNRbXOrKtKnlYkzyadgr9FBSZ5Bkh9iuQUHUyYOrkQKKc2PGWRUqWQzjAoVVCVWmsk9FRL29UZ6/QGqLne2obBlFxgMijxEXVyvt5oqlRW'
        b'VNMXrVpjqldWa5PzIAdtDmbeCH/rzXbFrYHyJaR3RAcgtXQEohTSYrMRGtbadV4a6TYlKjlLrdPVK6RZegPUXauH2nT1StqO2tKeWjoDd2lNmippnV7nFFeuMSYXqrXq'
        b'SkhLVQPruojUG2yJklnTpDPUADv4ZKXJSEZJptQ5t3RGtix5mjxHqdHap/IxsuQMHk5M9mnWOFnydOVS+wQIypILYBdDJ9X2CdY4WXKqUrfIOuUwRyToOGskZhGBYXmu'
        b'uQYqgKhsfJIoXRaRWeOnHyIzUlNySZpabagEXAGvBXMyphfKp+phbSyTT/eCRlcNsEbqsUx7utJca5KTdgDplCssbVreHebdVTyZe4dBRDkNIsp5EFGuBhHFDyKqZxBR'
        b'9oOIcjGIKHeDiLLrbJSbQUS5H0S00yCinQcR7WoQ0fwgonsGEW0/iGgXg4h2N4hou85GuxlEtPtBxDgNIsZ5EDGuBhHDDyKmZxAx9oOIcTGIGHeDiLHrbIybQcS4H0Ss'
        b'0yBinQcR62oQsfwgYnsGEWs/iFgXg4h1N4hYu87GuhlErMMgejYi7CeDRl2p5PHjDIMZH6nUG2oAMWeZCarT0TEANlaDcGUN1BoAIQP20xlrDeqK6lrA1zqIB1xsMqhN'
        b'JAekl6uVhnKYKAimaQjHoJbz5C7FbCQEpR64huQ5+GS1AebNaKQNEKzH01itpkZjkgZbSK8suRimm+Qrh0RdFck3HZ/UajVVQKNMUo1OWqgEumhXoICuAUnJp8ph+8p6'
        b'yLi8GHoBCCOYFHdIsJSHpLHOBaLcF4hyWSBammowmyDZuRxNj3FfYYzLCmPdF4ilBXKUPF2mcw58CfAnNM6kXmqyvQAmsr1G22c12rLxC5GqBnJcZRcxNrlYo4PVIOtP'
        b'2yFJ9RBFSC9gaYdglGMQ0I/SaAJqZ9BUmgjUVCqrof+QSadSQmd05QC2thU3GfDJKgCiDJ1KU6eQTufph30oyiEU7RCKcQjFOoTiHELxDqEEh1CiY+sRjkHH3kQ6difS'
        b'sT+Rjh2KjHXBpkiDZ1lm1WhhNGQ9jJGrRAuv5CrJyj65S7OhMhfpea5bI3yXq3gHVsz9GHpJd8ed/ZzMUe5bduDTniQboEpX2RxIQJwTCYhzJgFxrkhAHE8C4nqwcZw9'
        b'CYhzQQLi3JGAODtUH+eGBMS5p2PxToOIdx5EvKtBxPODiO8ZRLz9IOJdDCLe3SDi7Tob72YQ8e4HkeA0iATnQSS4GkQCP4iEnkEk2A8iwcUgEtwNIsGuswluBpHgfhCJ'
        b'ToNIdB5EoqtBJPKDSOwZRKL9IBJdDCLR3SAS7Tqb6GYQie4HAQjSSVaIcCEsRLiUFiIs4kKEHZsS4SAwRLiSGCLcigwR9rJBhDuhIcJhPJYuTjeoa1TGZYBlagBvG/Xa'
        b'OuAkkgum5afIKbUyGQ3qSiCCOkLzXEZHuY6Odh0d4zo61nV0nOvoeNfRCa6jE90MJ4Ig9EU63FVbaVIbpXn5eQUWBo4Qc2OtGuRhnpnsIeZ2sVbybRc1Q12Ouwilf4xt'
        b'qOLjLVyDNRTlEIpOzrcoV+wKO6ldIp2jopyjQMzREqFYaSJ8qbTADNUpa9RARpUms5GwtfxopDVKnRnIi7RKzYMpkENXagCZXRENIe4aFS32k5ld1O+CKLmu2zkjVTH1'
        b'zI4UmG+pheWlU1lJ0i2TzL9H2b0TmbBHU/WITc5tlxiIhtxAzTjIERF/lkJ0jQZyqN0tMtZqNSbDcJsOL8BRm0cMUVY6aPMEHMt9LxZxHPcDF829bCb1jxH4Gomdysaw'
        b'ufgUahcykjhuFT6N9vyX1XleKRUVerPOBOJDt18qrDkvdihr1dqH/XllHtGMPxqcBlBQA6wF0ZdKecEHYFgDmAeyEKVst5CwQIZx8PptF0QU1fAcjb5ap5YW6LXa8HRA'
        b'STp5Vj1RsPQEe5Bc8pysYilfjCjSCPo0aoxmPoKk2Yf5TTeD6P14Bp9vKLVIXlBRrcVdsPhaYErsg8mpaq26SkUGwr9atC4971EWASnZOhOU4Sccodqyt61Sm5Tniiyy'
        b'X4+WyiL1UV6dyHuQGXaXicoFlhpoc1oNZKBvGl2lXiqXphhM1q5YYjJ0pORjkSRblKtsUU7Zol1li3bKFuMqW4xTtlhX2WKdssW5yhbnlC3eVbZ4p2wJrrIBk5FXUBgJ'
        b'EVn8whBmV00jo5wiISDNUQPCtKpipWaFtEcVC5E8LFt1owopYditYjevc+1ZRml2aHbydLNuEbXsVRuqAEPVE6xC4lOLpDGJPJ2ttGYhOmFX8Ra44ZNcVJhcTOUBMnBD'
        b'jZIk2kDEVYoNVNwVi+qtmOtEHoR6KeY6kQepXoq5TuRBrJdirhN5kOulmOtEHgR7KeY6kQfJXoq5TiTFEnsr5jqRLndEr+vtOpUW7B1Q3ENKZK+g4iaVFuwVWNyk0oK9'
        b'goubVFqwV4Bxk0oL9goyblJpwV6Bxk0qLdgr2LhJpQV7BRw3qXTH9wo5kFpgwl0Vi4B0LQHia6Kc6RK1xqhOng4kvgf7ATpU6rRKolw0LlRWG6DWKjXk0KkJV9SjbbRQ'
        b'ToLwUsyVRC9mQ3JWWgpJBPP2EGRpcIqunueIyYEeIOMcjQlIo1oFHIjS9FjyY3jYuXAPJn88zaDFN4wWNsEhJZ0e71SagCuxyVWUksgpv+NSCLCM1ELNgfQDpSE8dCXl'
        b'nmsIgTepNTAtJpuiOANYXZOmUrNIaY/9i6kcaFMg27MZvPRod5BozyZNV/OihVpTTpKyYdXIyZiR52zcM2r2ymHoN7Ss1JprFqmrrZpsSgQpFycDLi7XEOKOhw2DR5db'
        b'HnYI97GZsL/T0W69MTsXbwmnnCzenOXB9Ef3J5ULfaRovRMj62NlZBeyjoxsm7jNu81bxbX1bevLM7StHqqwJlGTb1PfSoHKW+XT6AlMrVAtUvmq/BoZlb8qoJUrFkO4'
        b'Dw0H0rAHhPvScD8alkC4Pw0PoGFPCA+k4UE07AXhIBoeTMPeEB5Cw0Np2If0oJJTDVMNb5QU+9Je9n3sx1M1otVLJW/iLL0VqqSqkbS3fvyo2rza2EoyMg/6tJYa1eqp'
        b'UlCTOhF1BwmAsh6q0aoxtKy/KhzSRE0S6iwSSNPGqsY1ehYHQGwf6NN4VTD0qQ+00Vcla7W6OPg1+VeKVCGq0EYJ1BJIhYBGWUS3JI2Yhk8tmP0o3Etq988aLeUxCO/F'
        b'5JCjXWQgNkeGMeQAn1qIh5M3aqlBJAGZz0NiaPOQmjoTM5ue7IZ4a3ZDAnkQ462HxNThIbUGINAg8+j2UqrqACkZSjWqbs8KQA06E3n1U/JiS6kWeDtTdbekwgy7Rlex'
        b'rFtCDFo1Sq3FDMO7UgPsXGkN7Nhq2na3YFrRLN7Ow5AIjwqJHQh6WX6prQ4xzXFwtvJsEjd5NXlUelnMgiTNkgZmpWd94AoJNQvypKZAklWeBXbvEYxKQG0chd/uhAlw'
        b'mD3yL4PvrqZebaROZrY511B7hgq1wqmIU0QSSB3KGmnPVCVZ3MsAsxAtkMV/zTJnSp3JqQbyLzgVEILJio5kCmkKKQ+oo0JKrQil5lopINB4qUpTpTEZnftl6YZtlVz3'
        b'gk923QPbWcdP9CH2p/rgCB5J0mz6l3RhRni2NdXSMaPrvhByQxA9kAmFtLAaUD/sArXUaC7XqlVVMJ4nqoU3JOFlVKhJqoQqIMz3X6rVAxkyKKQZJmmNGSSVcrXLWpSW'
        b'wZerTUvU5KxXGqxSVyrNWpOMehcmuF8Ly7ZIkk61vEkriLIw2HbEaKdklLmrxbqlkqzQarQtJnFm1BukwbzByiLcZagHudtdRRYTqSQqZBGGBKrhYcSCYYLVVQppbGRE'
        b'mDQ+MsJtNXZ7Okk6nQSkNECqq9ToYNdAH6XL1EroWIhOvYScd9bFKWIUkSEy56l6AtNjH95BoiE/gJEyTO3upWXa6WHDGTOxbUXHS4C2teSgC/m4OQO3ZoXjjfnE4jQ9'
        b'ey5qkeGWsFw52oS3Zs9MRxfTc3NyMnJYBm9HR33043ELrffWeF9mEMMk/HNemY967gjGPIUhJqm4eYXLevEWvDEbSCra6FAruo27oObGZT4MuobO0prvz5QQB70AP12Z'
        b'dunIcsZMCDs+gzbr7P290hXyELwRdRD/GXRJyMTNExtxM7pK/dRoPZ8t8SD0uTotpEy7b47QMvILs2pddRA3Q7UtYaSTm2Wz7Ud9bia6bfBGV9EB1Kh5J+afQmM91PP7'
        b'3/kMe+mPnmsifNZ/cPrmtTsbdt5aJ5DM+tVvWpr7Bqc/91rOxA1o5NffF16t1Td2jJm547X1c6q/XW58qzw8KSPsd+3FRR41xxb8fuIPscGc1wJuwgXdiPdnTtQWfDB+'
        b'Ie6O2N84WRfz1IH3dizVHv7x7m8vtjz8alL28MlHZbJbFzNlPtToFnWOmIxawvFZdNrmyylg/McKKtEDvMckJVkOhOO9qCUv225BWcYDbx2MG4T13iOoP4p8PDrtDXMq'
        b'yzFbrG5R06L+qEkoqaqgDmjBAZVQh8P6sYwZHxwwUuiN74w2EY1bHbocEKrSy4PT5RwjRvs5Odo4iXdfO4xPLoXysFrWlQpEl/C9OAFumYceULNeE76Ntoeiu7UKGd4E'
        b'bJoYXeCi++DdtIL+eJsAtRCnM9vyiJnAuiGjBOheEr5qGk+A4+DUqWScFraN9NGytgy+V8JE4PViBbo23US8rlagNrSWDKglLERBcuJWvHUk3gDMHsNIjSLfyEG8lfwF'
        b'vAE3koxUowkty6FdtCcIHxLg9eiG1kTcENEddBsAo6dtC8uIry4ZjG4JoeMP8GnebNLrFzrF9bjJUNtTwoYwq5kVYlZMfd/EFg84P3gS/zcJR1LEbH0fK1W2OczkWjtC'
        b'7U6Jo5qBbFpDCnmkksdUxuqbk8b0btQs4Uv1VJJqK0UrceHl85B0n4Aus4bZN9y9hatzxx0Mn1nLL7UuJT1cwSzk/cbYXBnb7V3aw1IYBtkm0c7HaYJWWVOuUk7qA7V8'
        b'Q2q0a9Ga9siC4i11WdmBYCAdKrlep10ma2e7BSp9xRN1rZHvmlepjc1w1TNDOjz6QXlDBrw8GsH3gC/iogNP1HIV37J/qSNz4bb5gbbmZb2yHz+7I9V8RzxLrdTdbRcG'
        b'27oQlKo0qm3swC9v0sZdu2tymK3J0W6ZhV828ZJSqzucu7alPW27ZTB+Wds+pfZyhLv2R/es+E9wJW564eCIQD3vuCbG5nn3c9wQntCnSpCrqXznnIh6AD/3+WzeSaq6'
        b'8kvm9c0vb/6TzzM+B4OYSVuunBD+MW2XjKPIHG0bCrwC4PJ1KY+hc8Dl+AQ6ZSJoFd3Jx9d4XH6x1gGd87gcnUHbe/OF8ygl28ve62k1/IyvD7BDaDQDX2bg4zUNsi3M'
        b'U/AYx1q9nNfAzzu9+L051S/z6vawbFje4l9sNBnUalO3pFZvNBFmultYoTEt6/bg8yzrFtcpqYzqXQEsvb6Gl10FJmVVt0gP28BQ4W23JAS3+1mXZRZZcW+bzOlru5fA'
        b'j78botLPAgnezT4ACT4ACd4UEnzo6nuv8imwe7dInlUgef6PyIXkmaJSGUG0IPyxSl1ONib8r7AYzknV1Mz/CYRPKhpRuUYprTZXqe3EPZghowbEJSnvC0EkN6PapJDm'
        b'AeA71UMwRA05rtHU1OoNREq1FqtQ6kD0IUVBbDKoK0zaZdLyZaSAUyXKOqVGqyRNUkmBmF0aFWSkGqJ4g+1nqdIibZE6neqAqs1Gja6K9shWjTSELl7IE8zIdMtoq4nK'
        b'xLnvTvmDTUpDFbShsqIqUl5KVIlGIrkYF5vJ7JYblBWL1CajLOnJFQI83CZJUxwojrSEHp7Od1eMtJwkpa4PJT/pAOG2Fn6bJEkL6F9picUcz21+63ZKkhJFKCwVFVRL'
        b'7M3x3JYlGxBEXHhKS/IMJvf5+C0KWfkX2kaYNKMgTx4dGRcnLSHKT7el+X0NwmtKoTwjTVpiOVGcH1pi797hvvEedEDEcT4gJRXZGxW7LQ4IBCazGrYGbFdjhUFTa7IQ'
        b'OAKnxF+c7q0UrVEP8KtWudQkADiR3IQcael1Q3SxFdI0Xp1At+ioApOypoY4yelGuVUs0M0AgAUdqLVsLZWGXnikhGldogGyp14KK27ZcM71kH+5epOa3yZ086tN1XoV'
        b'YJIqcw0AGvRFuQg2IGwaNcxOhVqqB/rvsh5+SGTTUD2JkR+mxmjXJYV0OiA1K0JyWYv9tiNaFQB1cp1ThRYGzN/kZFS7LllmucxJX0F7zp+1TKg2mWqNSeHhS5Ys4e/e'
        b'UKjU4SqdVr1UXxPOs6LhytracA0s/lJFtalGOzrcWkV4ZEREdFRUZHhaZEJEZExMRExCdExkRGx8dOKkstKf0GEQiujscRiYS5XynAnfMGbLMuWKXF90i3j5haJ2EBTH'
        b'FIiqZ043E081dCTMHA1/Ixm/0EiQgBuoCuC5DOGYcC6AYaaUZX9UNIwxE61tXiBen2WV12biZnKxSqZ8FnGanRVMXFDn4GbyB+g+2oEue6A1nnjXatRIbVyGDgGxsBOk'
        b'4a1o/0RgDzwYEd7H+QxL4G+l2YBvZeNOBQifArQ9g/jmQu3k4haOGYFOCfEdNbpI9RD4EloXgztB8M4pwttqYXBo83AYn3Vw+bg5F0puziqqhUdedibeJWTwJrTOG5/0'
        b'GE67gnfhNl9vhSwzfy7qQke8GM9MDh95Ct2jF0vhazHoLO7MQMfxTqiBZQRoD4vWoA24nd4+gi72Xe2Nm8MVoWgv3githqH2TBCym1lGOkMkxPfwenp9zsypZtwZHsKi'
        b'w8kMl87GoZuz6NSaWI8FXUQDJC3zeWbKUsZMjIvwXTN+YPSFnl3PoI1K0rLncTPQmRQz4WQyZ88nib6oocRXgbfj69n4SijeIWAGLhOgC4yE3neFruPbpd4KKA/zlhE2'
        b'Fh2GzgmY/vi20L8vPqhJ3/mFgN7dE/td3PFP5a9keaEpAcLXPn/ho+h/f5b7wisNt/7mteBYyuutws6sOL/UI6mBXx/9w5q//2nm1NcnikPl7wT8z2bPkIn9Rm9ouNO2'
        b'peOdhTufV2bF/PHDPze98UZ7/NsjX8zKfuult/9+7ahIrpkauv/1KaHFb1y7fex/vr6Se+yrP377sG7Pu9eKvvtmw+2VK8zJZ/749p/G3y4zZ01S9v9g8quSN0dk3gid'
        b'/6sKmZjqLvBadH4pauEv20IN+HKPkgbDpFPdBerMH5r1uOYCr8WHifaCCY0WAaQ14i1UVwOLstXbpqzJeIqqa6iuJiSR1/gcGo1P2eksxuELdnxux0p6P8AwdGVZaK48'
        b'IyMnKwy1jsOtMpYZgLuEUaYIml6E76DDWWHB6Xg/gEYrWUV0nluGdqPTDveI+P3Sq37cOtl6KVWqUp6Jozz0OCsPne7D+rASdgB92v8I6eUkEra+r40H7qnDou/w5ZUR'
        b'xYzV7o1cN2KYRx7zyWMBeZSSRxl5KMmjnHFQf7h2F/bm6+yppMzWRLmtCV9bi0pbO5THV5EqHHj8t8e55/FdjU/m2e2jImaBFp6p25fnhK1BsbKG/iUXs6i7PS1nwRXq'
        b'bm/CtwC3SCzF+B7ZBl3hZYeUidYmwIqUZxNG38uB1fcDZt/fwu4HEHa/MsDC7HtRZt8bmH0vyux7Uwbfa5V3gd27hdmvBGZ/q0fvzL7SZvEn5a9xegKWdhpxluBzS4Gu'
        b'wrwBtwq8gtL+HkPCT4RJqwx6cy2kAhutdKZT+ppyjU5p5VxCgKkJoSSXp7hESWCzDiUdtMnNTjUROfr/Sif/f5ZO7LdbElkoPsamHvsJKcVhf/Ll+ShrBS5ZtZKfsBh1'
        b'2xy///l2LFveEsdzuzo9UfcYKD+rc82lLtETdlJTo9S64YdLerGZBSnDtdWs2x4TTMX3t1yvX0T6S2IU0hwLdClpWKovXwgLD7K/66NHHZGOEuIiIi0aNAIIINqR6kp6'
        b'7GnddsKGKJOkRUazUqulOwMAp06vqbDtxhI7c9xeBUQLonVcBuqoV2JvsvuTIhwp/pgY52AY+n+AFJaqXqKuspj1/F9J7P8ASSw6LiIqISEiOjomOjY6Li420qUkRv71'
        b'Lp6JXIpnUv6ImZlE7+CTvta/TFsd48mYYyAuUIs6sjJyQM7ZjzeFZdjkLVdi1mp0zzPGA5+jMgS66FXPS1g28Qp1KH36Q3IcJE9kxVmKzBxgb2md6JDAbbWoBbd4ojP4'
        b'Lm6mMteyeajBmJeTZ7kyidQ/B2+D7FtxM8hZXnWLQDaBOiHmdsE8dBDtRyc8GXQe7/bO9QyiEgyCuucZM3FrRk5eFlqPmsh1SxFCZlCqAG/ORftpJnxJjO8ay9HWkBy8'
        b'JZgcRCoy0MVglhlRJRIZ0F2aaXYpvu+Nb6It+HL5LAluleeCAMYxgdECdAytwzfMwaS5kxPwfpiMnlNvcm/b9VnkGuJI1CLCXfjY0mrITJXct3E77iSdQ0c00L+MMBm5'
        b'NrUfPiHAd9E5dIsu1vRx9E5c5jXPhdoBSg3DS88nJFLvFeVihilkCqGWE1SWRpe8c73JRMF8bsc300EIbQVh8joRTFvmTkDnIZyNt6QT8WxekGQGXptLa/NGjUW4U0M4'
        b'5wwmYzm+SWOH4ZaMaBW+zxAhPVKHt/LXvu7AbXF455QSAb0Ndj4+rv3Xjz/+OHiEkILUlKd02e8Kg/kD/Xx/eqAfMCXTrB254inGTI4g5SoRmZtWizCfHjab3NYcnlkE'
        b'wJCONwfiPQXBMoCKdNsVzTJ0g06gWOc73w9Wg9xss9w0pADvis4UVKKzDIsvkOPfjmozOc5gmXneluWZxUOLSUzgReJiZtAlvEPIoKYiz6emgCxMLgj0y15MBeLtaB8v'
        b'FM8MxrsKJI7y7+T+Yr8iGZXLATTP4ovGTHleTjgBndwMohIQoJt6Rob3itC18DIq33tFi0Mzc1AT2kquDZWJYdYfcLgTXUFN9CridYI87ldiZmlHxleD3hiUOMnPYv/Q'
        b'HhCCOy0qD94yAwALbwzPy5kZzF9Bam/+gJvQDgYfQmd88LYavJdqBAaWKUMVGWEhLCNGW7mcieGVE83EphJdGDIzywMdpCIjZ2AT0Jo0mYDe8+OHHmTalYF5OxmOm1GT'
        b'mRgP4GN43ZSsqajLVhBvyqTFDPhgPAxyVYLDEE0BmtFzRguMk0F4OnKrev62ibmCyID1VVp93IHVP+wIawzNLzj5vl/M0LJ+Jy80vhZ4asq74viGtD4zC7TFW6Y8e3vW'
        b'X+Pe3fRc9F9ePvPplV3XzjfEigq2n0763ZjasoSwCSfQrvgho6fvlIlWVeRM2Dh/+m9/GD1iStJ1uSZlnPQ/Z4f9bvjCTUlz43cq7mxJGiYuWFV9WvH13YJ/zho9emqc'
        b'6cCHU/45ZcjDgYU/PM/U3zp55tLmco9u4aVDm/8570r2BH37hOrPb+eqrlYlvrB9zJm3vl7z9+j3xumTXjRcOj1z7Xbz2gt/3fKb9VuOnc4XNekOzRZXfTP1qZS9/1M/'
        b'esL4WyeGTX7vhQvKrqfefrHe+9zNmrN/Of1N3JkXlf7jv/lQvGx72T/uPPyN+j9R4+ckDjNOPoHunv61jn3vmR9bQx59Pjzj0gOtKPzdjpN7F3w45x8vjTHlvf25/z/y'
        b'DJf+c0zmy9/+24l3LwdseQpvDn/cmORCCX82diSp2ElNQVQUlXgdr6VYmkN1FH4D8AaiotBW9FiUUBUF2hhMrT04dG9OVs5yO4MQ/9kC7TwfegsY3oDO4rbQEN4SBK1f'
        b'xHg+xaFT/fAxep3XInxmZKiCIPgwAklbOHR0nlzf10QwCSDO5qzZc7NDxAw3n43Hp9S0iLQInUXns3PCOMCkxxlhFouujsEd/J1jF/Ftei13KyUGDCNewaHO1PFDzPyY'
        b'T+IHxIRj/yJHaxGbqQg+OYnalKA1SYN6bEBQU7jjuSE+i07Qa+6UaA/abSSbS05IFZlk3Aid6kNsXDrQBtRCZ2gwuoa2UgUMbIgB6Byvfxmc18vNW7KA/5IyxpVaxo+o'
        b'HHokcKqaKSR0fzX94Xwsipke9Qy5kJlXztAQR0xThkNqP1ZMDVSIsQp/eVoghP2o+YoXRy9TG+ig6Ohp1aLM8eEVKmryqCSPKvIgV0AaNOSx0KZkcaXH8XiSG529+Dor'
        b'bRWrbTUttLXja2uiR6NDLsgvdtDonA1xr9FxN9AKkR3fRQ7WHa9+FzV5NDH0aJVt8qJ6GO8moe3qd1GzuIFZKa4PXCGiehcx1bWIVokL7N7dXbRMGhvBPM7k+fFMnrme'
        b'fCWhehHDlPksGKdhCmnsyoGE9dsW7DelTLtAupShND2gb64RtUoWC8IHMgI/NkEy2Uy2E94yZm4Bai1cjlpxa1HOTHw9H18v8o2LiADmYKAArZ2JTlMOcHx/fLEAtxbG'
        b'j4+NwJtigL2SLGbx0ZloO9V7K9FFf1IPqYRlROgQXhPCov0r+1MqtEqFL6NOMXBD6DK57h2dQUdogvdofA6fKAQyfAogaRwzqBLt4L/PcM8LrclSRMRExXKMuD86sopF'
        b'h/HNfEpm0e2wbMdr1Rfia0AQm1C7Zu3K74TGTyBT8/3N0/KSc4WRPtc/zPik82lFYOqUqb9JOVvd/vCCyDew+eJXCwfvGTryYQLncfT48Y8SEjo7U3cf+WbB4a9+FTGV'
        b'FS0Ki1qw7pl+dTty4v/QevazQTG1+fVvSwqfvRJydMwz3dsPK5eMf97Ebnrn1tXsoA9nvTGrZPTadxaHJYzEk955b7nf9IPCL7pqEpraD89OvTxi+h+W5ZUsP7g6yd9D'
        b'13B3y7zvyw3fffL5v/b99U39Fv/kHyqWX3x5dHXb3rywjGhlSuOLt37zxceHDkSdH6D/4IPsN778auxX9/7yr7pnVy5o+XHUkb89fT7wz8dWPxIc/V3+CxqJLJC/n7oB'
        b'7cC76bcMJuBmD8Dnx9kidDGXv4SzBZ9GG3l8i84V8+gWH8dr+dT2gOkO2BY1o33c+MRx1JYOb9aspoZ5+AbudIluj+EHvB78cBE6TfTq6ESVI7lKrqEq7MnodkxWblgf'
        b'vB+4vq3h6JwQWJD7glLUtJTeGInWBazALeTwRWQKYYTDWXQcH+IoTSibjy6E2hFBnzBBGd7hgTuKadPivvhUKFCn1qHW2/QtN+nfRQepzt+UPCoL7UYNjkaXA9BF4RDc'
        b'gXdQehvMZeCLgOIfM6oMXChAF5RxlKTMEqp5cus54TGCy1NbX3yEVlWPTwA5bCHWkWiLh81A0n+4YMEcYJUoTb2G1qFtWUBwSx1IbriBv1J8E5D/S1Zyw0gm4V2E3CR5'
        b'8oUfoFsgQFnv/Q9GpxkhufZ/NT9b+K4/3mh32XAZ8LnkMvNLk2jdw/GW+ixynrElj9xHPnIk2sbp0Q1048kw8f+rjwlYbXL4TwdQolXZQ7TCCUmilpLUXlJICBbHwV+e'
        b'gPkQfE1/hJSM8ecMJMRbV0ps6bafD4QjhZwfN4AjpM3eJofvAE++PHoIR7cHr5s2douMJqXB1C2AfD+XVokM5PM6Bp2NJOltdImSJHLN7EVCkkZZSdIa5vfuv0vg3O3/'
        b'BVMvAbWIFD762EnlwPt3maxeJRbVrdaiUTGoTWaDjqbVSJXkZMBOQfNEWnXpIvUyI9RTa1AbiVElr/mxqLKMNnW+RQ3kShv+uKZfy+vPSHfKl5nULjRVDhRWbD+Bdpb6'
        b'/CXhbRJimYx3o62AQq+ge2l4B7o6B12F9/MzUbOIGYTWCJbjy7y4BVv+ZhjeKcLrUBfDKBgFupLHH6BemutF6S9qmSPHu7Nq0XqFQsD0QxsFqH3yKEq3By6lWoDgKv8y'
        b'n81qPUNPr9E5tGGuraR4FN5Vju7hk/h4FGDPLSGxooQYdIqKy2h3aN8eeQ4dTOLCo9FBM+G3S8cCfllhR58JbS5K5RmDxOwsXsgbhE+AnDfMzNfWII8q4HMDutzDoVZ2'
        b'6MiVmgm7DnDGBkgfPbAq56WRfhwIeR/8M0neIc64uud94fP9qzveH5dTN2zVc3MWb4j74GjMSe6fB34s+aBtWPA7+W93vL9slfBM07rBbYM358wrzM6tlV0ov/baumc+'
        b'WvfmlSOLD95cNT1vQOwrtQsfxYc91E3PuaP/cuW/vv3d3qa75njj+lP+7w199PvaX7c9yB069l9bGmVier46Lh2fsx2vojbc5mBHeKsPJZDocA7eB8jfehmxDDDiaHQi'
        b'nVrK46OoJS1UkcMB3ewIRmfZrDR8m/8wxEnUic8AVeO/CMIxgCfPe6s5fDRJSUlCPF6rd7A0Rxtwg52YoUDXKUkohHXcA1JSA7orcyRSqB2tk4l/AqW4sW1UGkvJdqN4'
        b'dFQPHtUKBYE8Ow9/CVYkJ7U+34tFgzg7ZGIpnPuTho8GeHz0GL46/ESmj5Ym2tluYa3SVO3+bvdUxnJXNjm3JB+JENvudxc+0f3uFte4DwSsizPLHhRGsIlRWUfetFp7'
        b'ZPbkznFkIEnSjEppCHkLkQJGNvLacYKm1EuJ6y1RFoco6jW1IWG0IQu+NLjWNRvJ/YIqm4Zbaaio1tSpFdI8opBfojGqbTiR1kEHQLMrpZV6LdCDn0BwZBE9nRCcJNcs'
        b'JxB+CoTcrtB04FLy04FNyczJRu2F6egiuoQO4OYwBXAQ6XiDRy2w32fN5GqYYHwab8+CvZaZo8AbgY8rJMxO+Mx0dBdYolZ5MLllJgvf8ACOa8tqys2nzYzCl6rwTnSe'
        b'+pIItCxah7eiB/wnqs6jzj6avFAAhqXM0ukmqpjsU4m3h+aFBwBczWLw/rCnNKP+9RlrvEGA5ptDE1uTyeehNqxOluUvKBifyx5kF7PixsIbzWtZzxf3hrU9MyRwdIFB'
        b'9krDG5nPt3w/eVJL4ugdb6Xd/PyVLcX121Qvm7qLs699f1qxRNenpZG5snhbQNMrZ7+YFvSKV3Hf50dvCYxLmB3r4fdcQdjE5Tv31l78dvD4AMWZP7865o0DN3/Y90nr'
        b'13r9f27U7jmw8duDb/W/sFz+YMAz9UM+zfzdd8P9Zp+Jzfzxwmsr9mS+apwye2hd8JHJ04YnLf82TObPo5qdubG1+DSdb9gD8Sy6tLqGsmUhKd6An0bjY7n0i3LkSzEt'
        b'3MqReA9FRAvxhiJgCa8tsWhvPNEZbmE5OoHuA4vLC0zT0Y0UfJkwuLA2IDTlckM51EU5QvH0ieS7eWGKDJrkjTs4oQl39UPredb96FB0NysMbcnjv2jgPYWLAjZ4L/D2'
        b'9yhrPp4bGArMZgtRSRJnolVciBTtp1z9BJC6LuMtEkJDZAq8lY7LP0JQ5V3Jixf7KvH1YgIhdhfBA/d7jrYcCQhxW6xfaDg5jpArZBzgxCMCtB4dQft4bdB+1IA6xuBT'
        b'lC8PB3FPPIEbiM7gdTyfvHFMUha6OAWmhgdVz34cOoa75vNIf30obozFh4h4Y5mUVG5QuI6v+QaIQNeKh9p9Povw0EvQWaqiwpt1yegoPsB3DZpFZ7mwYYLe1D0/gcTt'
        b'ELeQbGFHaxry48krbCTUa8gHeFurAiYAYut9bWiVlObRdrvlcwcmxkGl4r6T7Ryft+eW+zp4/PgYdm8Y0MvnDxy6IbP4bU9jiJ+/zRkasIvln0zE/+Hgt+9jN14R43yV'
        b'vqK0lLoidUtqDfpatcG07EncoIg1PjXXoRoeylNTQkXHw/P1/f7r6rdeV9VATtg+ZCwijYQTCr1Y8Y9CMnc/9hsLs8lyP4gFP/Ov0E8AAGCpZUA4AMWPQgHz49CZg+P9'
        b'hkj4r12infgKPm0kH6w0+vkJ8DWG8R3G4WN6tJfynj64I88bwJrgFW9y4pJPTlqGRgnTU0fjNZ7/X36yyfm40oM/nkKXuZUFDL66lGFGMiPnoU1UqwTc1qGFWQogRE2o'
        b'IyIWyuMb7OJgtJmqpIywcc9SPVAh3mv3hT3ddDP9wN65PvgWbskII9xWtJCRABt/BNrJxBfQTc2q709zRgK1f/Hf/EXZvKc7th3bGbl+MVvh8SF3er2Pd1ByStgn/U73'
        b'+2R9dllc1qW+Xt5z2449f7ohcv2xhmO7MnawY/q+9PQ+P2bhlD4lJ7plIooMcRP5SBiweZvxHju3SZAVblA8GjWMfC500zDWDuEMHEzxjV+eIlQRhq/b6dHlXvggj+Uu'
        b'SArsJHa0LQZf5PTF6DCP5Y6gNbiZHOvyyfPRdR9OrfDszSvGB6QtYGfUpcTIgSKiAfaIaAzR/xLEI4SnYbltRwm7haRAt9jiseb0mShyH51hhW1HkJIjOauD5BrLzwfu'
        b'eUdqWSychS+EBmfK08MyUWs4f0orxbtFBfh0P0bmBFP9LX+Nf7O/7iOUXHkBgMupBI2exQK1kH52jyEf3GvlikUQltCwJw2LIexFw9407AFhHxr2pWEJhP1o2J+GPSEc'
        b'QMN9aNgLWvOA1gJVfckn+1RhsGlYVX/VAGjbx5I2UDWIXO+hktO0waohkOanUkCqmPrkCFVDVcMgjlzKwTYJocQIlZRcxdHm1ca1CSoFbcI2EflRBVVyEEf+Cmx/+Vj+'
        b'KeRz2D2Fj7+rRh70h7q8eup5vIxqlHPcL3uqRh/sqxpzkCvuow5U91GNDWKO9j3GNLA0NM4aojn6UTNG3ltJAnPiYbmApD81cPSg8yRSyVQhEDdAFUTRTES3ZynQJOV0'
        b'YJCpo7mTst5RzOBNJcX0o4pim4pe9MQq+if0iPPiVfTtq/hD84i4PdM08Qv4Q3M2fjMziGWCIwa2psmNdXxkh3Al+y+OmdsxTB49u6+Jocx2xCjU5eBh7+DTjG4GASZp'
        b'8WAKqiQB+P4SWk9s8WiGkMiIkUcN/wgfzHxq7SP1KNScfmoDS79hOefNU8M2X/FdE+EjfG/L1HenlglvHH1puM+UipTtigi2z463Bzd98ufS+nvbXxB7DyjJ+8izdcGg'
        b'Nq9Xnn152sK6psCF9+eeej1HXOpRsf65pk/fTUv+8NUUj6rfmv7+5swr5d2Tzx4KmvvaXZknxVBB+OpA/htRcuC5LggYSSFnKkPbKOIz4vt4B2pBl7NzworKgUUbz/VB'
        b'J7W8rfYZfB4fshhXF+E2+6PLVWg7PRAMjMp6zNUb3QvJ4qdlbJCoGrjTZiqCC6QgalOn9dBg+TIBnUCSaeBQ4YT4MKpKCEdd0SL8wPIpvlaq6gY83QcfEKBjJegK77d4'
        b'EbWiZnxF0JMtB10gX+nbJQCGfMc4/vOvV9G1THIXwMZwYjXfPIEFhn4ThxoNg0zEBAHvrI9ALUugAkqXSTXt+D7amgdEbWMe3qIQM4lZYhCh7kh53PvE3GWPW/pwe5we'
        b'JWa9RBJ2EHVPt6hZ2fpA29Z57AOSvFK0W0TNnLqFxEq226fnQEyn7/bU6GrNJnorWA/naW+LLjKsI+9ryIOojHimc61DP8OdqMMbvfCeLnr7c3y9RaVkGG69blM4yx6x'
        b'b8fmfD6054JTJ99bhSGL4J2f0RXfUvu5dNulNGuXHg23a97Z71zx81zee1bOXcMzbA0Py7Bmtppr/tJ2PUsJMJXWaNw7Xmfamh1AxAxppUFf8/Pbq3ZsT7nUbXs5tvb6'
        b'0faIMe/Pbc3i2S0uNelNSq3bpvJtTQUVkoxWo1+37f0v+3BzjPOHDyn9eC9KMEHPkbeysAOxY3ni9Mlkj8G+LPUsyn65JIDRYNVtxkgugfn49DzySd90ZZsq+JMspU/l'
        b'Z2WfMX87ENT1ecHeXwWtC0qIZspuir6QfCxjTeS6N3y9/1JHxPcY0kOd6CJBfDfQ+V5YWCoAUixHvJ5tWG424Vnr+9jjiSf37i5wQkaXe1FzOjfy8Ef4978kTrlcQ2dx'
        b'yrKGpYuExEmk7JFkjXZQtslIJ+nTse+SGl5qhzG8eUXzxt/fEBmJQeOcLybyH2Xeppr79F60F13b1i546aaSflcyW8Ck/Xthl3jttSUyzkSORAIT/R8jXJdTXdCtLegu'
        b'Jf4hLCJnoRtD5AqWwfdKxWgdF433aHsTT/xLqUmzpl5dWq7VVyzq+cCfdZ3n1QfZTb9jbofv2YqoLa6zpLKDcdCCbIfHXKflP9fL8rtv32EXWyGAsjqW79sKAAYEvwAG'
        b'nIxDWMb10RWFgSED/jF6PvuWB5NfNuKFiMEMtROcAhzQOXQe8tYz2fhoPVrvR+VvfItTovMwAcuZsOTl+MFT1O6xfuD0HuZTVsGbuhYG58pZJgZtFPvhrQy1DP3zYFHm'
        b'Vt6lU2uKB5RBZvpQZi41dlxTX9P3j4O8B0QwZqIawo0achLD3/bkYPNoASCrpSPjTa56QsfwPi+8H58dR5GnmWgNK/FpYiFmkezxGgkV7kGw340bNKOOHxIaN0IuzcU9'
        b'Y18meuJBgrLkrakDZ/8uOWJ2ufIj8Uthnw0U7NtfmP0wdU9zwZj4sccOjP3Pzr6Xbq0emNaIVYGjZ3sd8jzT7DNzvXJzwFfXRlRteurfyvJZ4WPrzv7xKM4Z+vrm1TdP'
        b'P3pF9uPe61/+sGhXDvt69o2r4e9cndty7IdPch+h6BjF3s3vb/jh34L3tozaNKNR5sF/pfy0EF+1qknRNXzJpipFN8L466PajZnA7O6ZY3/zE2+ntwMf4NnG4xp0xS36'
        b'DJJadh/ej25S7pgc/aPj3iEW1thSK+6KJL6vnUJ8Gd8IoRVPxHuKeEMP4Io3Q/egSnQBBHBr5WImAp0TD52H71G2faV/mcU8AV/C+y3uiMtMlPddio7jNqvCogKdpzoL'
        b'To/uokMy23fH3SpHxaVLDBrLJ18dONhSYr3GscOBgx1ssWrzYesD7PYhLej4OWulocrohj/lDG2OSGAnPOY5IYHTvXz406nx3Aqh3f50OFq2fL+Y+unZvl8spOdbItj+'
        b'Qrr9RXTLC1eJCuzee9OoiZy2vzjXTNSktWVRaOf8gQJiPjZCO4lKxvQwuAJtWBQ6Uz5bjq/hm8TuxKMPN3x+rEZ+sklgJJdnXl7+P0Qjtg299cw7z3Rsu73zdsPtuWHr'
        b'ZXtHrr/d0N6QeP8frRmbR+5d2yliLiRJlsWcA8ouhXLheBs6DCIP0digjXmrFvImKCwzpFqImgurrAvTu25cXEq9NujyB9gvv9aP2n04zDnNymvCxXbmf/Rb1FQX5Yj3'
        b'24V87GM56eLvIijDafH39fIhYKeOuF97Io83iWD1xVSNQSDA4xdAwBOqHkS5/GpTFepewPfr0IHJBbDiaDfLCPBdNkeMmjR/jdnKUY3ISEHIF2VZymB18J8yeP6t7Isy'
        b'TWXI7i8O7S57WLao8kvVF2Xcpoi4aPPVUxHmjrqOU5EbI4XRtZUMY3rg8x9c3cPvPpGFjMOHyYlC0W7J+9kvuUHCGwERG9T+drPdU4avard7wNpjW+C98NA7LfDOQe4X'
        b'2HWTD8mpg/ulnsJvc5Flo4t+wTI70XnXG926zPS4ajvepYYlxrui0wWMyIMNX4HWBY3UfOF/jjMSv5Gu6P98UZZhW+R05edlCuVnZV/CQn9ZFpCdr6yuzK4IrOA5vrNZ'
        b'Ho+Yi7CtiYHILNyBT2Vl1y+1GHHPHfHknxzu9iu1XLtqt8QODHs9WeL6QXYz7VDAqvtw3LHd4kplhUlvcIPYhYYD7nb5fngscQKCln7ugcBt12T+vCVyj2EysUnu9u0R'
        b'7Bepl3X71unNFdVqAy0S6RiM6vauIJfVqMlHZCPtA1HdEpXGyN8yQ+ybu0V1ShO5uVhtNoE4S27XJTu320e9tKJaSe5+hSiZhJ69GYicYUgmDxd3JJNTuGJaI7Gviuz2'
        b'st4mo1HZud+X0BwmjUmr7paQb5CQzN3e5M3qyE6j6bVVtKYow3FSxoP4Upbrl1Lf+25RbbVep+4WVCqXdovUNUqNtluogXLdgnJNhYzr9kiZOjWvKLewWzg1b9Y0w1XS'
        b'dCfzmCaFLCnlZwnsTCe7S2C7z4qQU0ml5L8hTwksTTjusQqel57DrViez34tYiKUy3eWV/N7ToLX4EYjvuFvwFfTRAyHT7MhJnSCsqgmfBitNZrqIBVfh815x5tc8rmf'
        b'80M7hlIPpiB8bVUoMfy8GJyeo8jImYmbc9FFfAu1hOGt4Zkz08Myw4E5Br7N6hqFd5b4TMXXBlA+fiVqQ2fx7TK8cyZDePmc1DTKx4vjFujzo4l5NjueQTsncbw3Txe+'
        b'jNZHA9xHM3gbXhuN1uErtJ7ZI1UzcBcUAJAPZqDSfaH0bG0yvt7P6lqyCO0OZRnvYg5fQg2z+QrX4G21eENfKChmWBmDdonQA1qwGB3WQe2neUveWPJV+Css3ilGbXQi'
        b'3/IJnVfEnWWYgLLyV6YqGWo1NxqdMuNTaC3UBvsuhEG7E+J5p70u4FCuovWAfxRyBfEgzJHjTdksMxCdFE4ZPohW+UOldPo73BrC8cyblbSQoR1E11OBC76H7kCdAoYN'
        b'AzrYJ4k/FtyahXaEkktWMvAW1D6EnJn5o1ZBOfDMF2iF4/oPSMhl5hJdx4Q3Z/tZKjwhl+CTMIkxER4MK2fQPnxxGQWDXHQEdQKrG4ba0UGVkBGGsejOjDxa1T3FpH6X'
        b'uX8xTESZIb0glx9uBNqAO4YNj45BHSDCKRi0XyGgNQ3XojP4sDFUIcvMARHLM5Ijd32MpDVJF2b2e1cQzMLELby5cAkPgen4GPF2RFdJXbDk4Qw6sBzt42+i2Tcfd65C'
        b'N/lLR6gFwwZuNL4totW9oxYWRwp4iW1E/UC+YyYT3jh8YnRMHENnbBc6i07yc3YBHQ/KIjfRtOAtWfOmUus1P9QomDQE7aL1aRYnFq9m32eYsrKoDnmhZc6uoONoR0kK'
        b'1MjRge7B96ebCVJKisH7sjLRNoATqDPXqr1nmcGoTYg2zUZraAXT0MXh+fgilBfTwe1Fm/BFur/Qhf51fIegaD/UTlbRr1aQgLaik7RDh7z6Dv8jQxRvZfPql3gzvFHj'
        b'RnQK75DnRkcRsIUh7saN+DLPJx3ALUwBSJs83HIAt1dZ3NZfZbGtRFdkaJM5OjYC5iaKhB/ATqfHr7fQORBo13mEZhFLb5YRa7ggdCaClluJz+GLaD++Fx1PCibAEMz4'
        b'HB0BfoAOojsWQNyENuIN6DLD+EwQBExYTQ0zhyjq1GgDFIS5SwIg8RXxdwitkaCDWfx8yfDVFcSO3idA0L8O76cDrxwrSXqZk5KV0LI+1fxK4MO5y/B6c3R8DEMrA+BF'
        b'nXTcUdqxgHTuQz+IF2UWgEkFNwTvQHt498GDQ4finZOgHEBXMrHG2T6Fr7Adn0wtQtezssjRB6dnpwyFofFm/JWw6i14PxSCnk+AmUVnQmlSn/IJUeIsgtU2480wUX05'
        b'TxD1aa9fG1E//CH7GQHv2VMK9JblOuu3El0ACbczIkbEsKkMOhKN23noPof2gwCcDSCAThYLgKu9z0JDt71pbX9KmsFMICds0rLMwUGr+TkIkeD9Y2GPQmWAEaYy6Ogg'
        b'3MYP5pa41gvdyQLUAizOAjYcNaK9tKJNeUELxgjKyGTO279sOt8tfBRt9coCCbz8KREjFLLoCG7AByk6hZG346t4p4gY/4ajS4raQnpTtr8cthBxwJiVDsK0fDZvMYeb'
        b'c8IACTHMjEAPtB2fGzIonR6AQ3Vn0Qm8G1+xedGS06O9HNo1Ed/suUw7kuVCXmV4Te0GxpffxGMWowbAtwwD4L0BrwlDp9FFaklcjG5AhQ7nh3gr0BwhOolPMGPROYCv'
        b'IfxeOA44G0S5fbhlJvH2AZwWyM5/Cp/kAf42Xoc2oQv4bFYhbgW4wPsY3FFYSDc24OqzABV2zuC09/iSnBmbJ9JI0HF+xnevJsZV3lDgPoPv+KD7aANDUX7BXGMozE0O'
        b'3pIuz+QFyEghvlTAjCsURZXidfwt4qLBcXqumlCRFW9WJVjWdxE+hQ8AH44eMKhjNnqA7+FO2qlSgPD1TrVy/dE6ZlyRKBrvWkVnLrhgOj6D72bNBGJL3Y3vDcmkqzrV'
        b'6FcABLrVazFQ+eXsUHTenwfC06gFbQBMsD2riJ+JU8Sxo6mcun7jxhnJY/BBYphh52vPMiNQixDfQHfm0rrLV6K7+ACwqqiLkRSgLtQ1lRrtDMGNRbDLE9FawA+5UDBD'
        b'HiVkhqD9Qi06hA9QQBTPQufxAQAHdI9cPHYC3UOdeA1vb96JL+OdUIEirac8B+UPCGsG4L2UV8iNTAacB7ibwRs9NNW4gcesjahlMjHvJB0eDiib9Nm/r2AhavKieKlM'
        b'MxTtpGoFdMlvBLS7jk6yD8D+VUAjmWh7uIJCl8V0Yyi6LsSbpkD1/em4OlEjPgAbBN0FLukouitDl+lM1MIA7uAWYFIWMegYOrpIGEwR3ugCfD9LLs9AF4IzwzIWoSMi'
        b'pu8UAW5LwMdouWrhHHzAB+q7xoyE+q6hLck8orwPxGBPFu/Tim9U2HxspuTS5V68Gt1nZxh9fQFLwSYEjHh/Mk9qh3lLL3LBBLrCPMqHM9RKNRiGgVtg2Hom1aRPzeb5'
        b'k334WGIGugZcXDrxud+clSfPJNaC0iFC3FEeRvWgi73Gsq9BQekS3YQXy3f5vsnv06H4tsSiiAVKe7ceUOYOzdOBH4uM/wHud1zmqvm/fVv3Rn6A+P3EX29541rOnzYE'
        b'lte9eP8v/boDg9tWnvmy5NYgT1lKUb+Pf3t7pPRQqOqvwkmXn8ZfSyZ4PBh/Zvez09pe+jTxwxcORqbsmfvt348+d2fE1fjjx6JOFZYMDu1rurd31MLX059d+NrwR18a'
        b'ZfJnXzw37vDqgsgrf36Y5rvqgNR31Hdfy4xPq89//Gbb66d/tUuyL/d0n1fTftX5h523NsXnLH455FKy57RPpL7jS9I+GVlyKGbajZTi3FHbv9o2LLdu05frvqy7OkOl'
        b'P/a3SdtFz68a75HmlxqXPGGM4dZrH/TZfmJ90q/TtkzNTUiUGc7lf3rt+X3rDvZP9Ej8y0frnp/2/NjxLaP2jJxzoerT/mMXfrj1rxHPnmrOXnYw54fLIz/8zUll9jv/'
        b'OjY6M7RL+/u5P558aU71364ltw459HDZxuGv1e6ec3VIY2Gfm/Ny0iamdnUELTnXMVgle/Xstyt+tWjZ9JfLKv61sO7VE18eFujOjF3xZsXLb57snrMg17S64fKvBx/Y'
        b'9v2ZovPve7637ZU5nZ05qn+sXnxAv+lijo859f7YKl2F3xJV1Mj3+t+O73N/8sOxhz70eLvyb1Pbvz6b/8GVjya/8Jekj86MetXQ/o1xuzn57T9sK03/Luq9rm2l39/0'
        b'Na+S/23c5G9m/2nJd+8u/OF9w6RNK1G7X/33341NuzHrs9+c0Y3+Q8vJ9jfKis+8+M/VIfLvW8SvyvpSz4IlBtgPj91hT60a8NFV1LAhy89EdrFnRb++hlCikufQfjZH'
        b'WkMtzYomRwBrhC6GoaZ0MSNMY9G9iWgjb79wDbcBJ9viH4kO1foYAGG1+tf5eoqZfuiIQI82+fDfCLgUgnZ4o/awdF5lzOJrHNMH3xGAkLId3+VNaC/gvfi21YC2T5jF'
        b'og3vq6MKb3wQnSsGvn4Dagm3WNFK8AkOcOZ1fIev4CRumoY7n6KKZ15XKMnhVMV4u4lskQFoCzqKDi2AXQWjq2NTcMsE3jj3amXOiFgHp3M52ldKRy5FpyMoqVWqON7V'
        b'EdDAA1oMkFnL9BXDLcYmvKnJNHSFdja7BF0Lw02OX13gde9HF/Hztgs1DXU0DcHrRFbrEHRrAVWCKoeBqGVvGIK3ovVW4xB8z4P3qjyBG1KJLQpIgFFKKtMQ42vLFIQm'
        b'itCNvHEUCvDmFfg6zB/aEGVRqzooVXEHus2bm7QNxPuI4ACAUuLV413ijXbxjix7cQPq8kbrbSYpVnsUtdjVhwR+tvVrt0Cp4tU7S+FhU++sZhSB7ABWyAZSa0LiWx4A'
        b'v5YfLpB1+iFxn0uGBbBjiB86OwjKkF8fVsINZqWsHy1DTKNJ3gCaP4DtByHuS8mAet8ebQ30x/4owEA0dD/XlY/jS/UcEVyDxznOari9xvbz1uBeLKYd+uT+jH8KPJr4'
        b'T2wxTSKb5pClWo0nO+l3eUIoZR7XaozntRrH0zmqXYkY0Lm6VjyX4dWJgfxOufNURSAijOxwZjjaW05p1mx8DWTmtSBxkqOSICYIdQr4/B2TgZ/bhdZFQ31RTNTK0fxX'
        b'Y8T0qzEREXGJxsA+K/nDwnNTPPlI8UzNx320PCv7WqjF+G3isMXCMTMs8uMOkBDPR4PsAZsP/pdX4B0S2pEgtH98dIyYdJRB25ep0Tp8iVcGRPHX0UTMbjW/mR3NV95v'
        b'Mf3cTkJEZX7QwIm+fDdWT7NGpgQ8WDWQzzlbQj+gExwx7rXKqKB6PueL8ZZIcbV/0ECWz7lzqhcDPZFEzB5r/LR8FJ8zcaYlsjLEb6y2hI/0yBLzXYozVz2rXclL7n4R'
        b'6DLwlNPTcGsRsOCMqI5Fd56KpcNOQe1sdARR4VTixjEwCyA7nKGNFiwfZTHtm5f3dYovv1YsiOm7l2dZeIn6laiRZ7HvrwRucifg+gNexJIa/nt7ULYRpEbg4DdC2gEy'
        b'gzfhfxy6SXkpWMKzyeheLN4JgCNn5Oh8Am34m6EiixXj9tQ1E2osF8vuR+2VeCdwgPAD8pk5EG9g0HV0u5z2KyIoHbVoEalpGDMMnUR3qS4BNaF7xE0lIwzfxJd6bLO5'
        b'zOmonZev9uDDaH2BnPBr7GjItZ0N7JtBubAin0C8P8TiKiTETbShDHR2HuoMQufhfRmzDO3xoWMRoTa0dSXx06TH2svxzX70CJkuypsiy4BmH/B4OW0Wr5ROvPMOulhB'
        b'dw2bdFvTlD9PZIyB7nvmvFWzPTkXTwnYUFX3YdfBpm8MER/4ekz53WsjFdtCv5s15syVeVPVI2+/1Kdu+a/Y4D5nmhPYPwVsfjO3I+DlV757789ddYZXzM+9fz1TcHbs'
        b'x0njRg9+Mbg65n3P1xfjpdXF073/fuH4n4r6fnU99y+vZwx/7eVdy3+/7ojsjQ36tx9uSft2zLkHW3+7eM5bU97qKG8dNee5VMGxE4O/HbZr3qAf2x8pFrz698grB1dM'
        b'+erfs7tSnp286DvvNz4qMb39ccDaL2Z97jnypYP7E099+P6c0e+o36qtb/33hp1Dhj499aNHb/z1/2nuSuCaOvb1yUmAAAEiRbGgEjdKWFREEVQUFK2soiiuBQJJIBoW'
        b'E+JCXSq4gYAo7gtFrVXUKhT39XamvV6fvb1tr/e2TZd7u++tXaw+b1vf/GdOQggJYtv3e8/IJGeb7cyZ+ebM//t/U1bWlc7+8afxOP17/nHpLM8b2pr8G1mtqarg3BuH'
        b'Cqqasz5Oe9PvMcMra9Y97+97ryKz+Zfqtoo5Paf3jHtpWZzPkNTI1e+MOx9X8W3yk+fbeuyKPfHO4sR3Xx8Y0dx2T/TFyMqCsW8qmZkjOl5ioMvVruiqM4MfWK+uxBV0'
        b'HFuGD+AmanNAmuex9IhQGKZO82j7wv5sCN/mpbBh7Lh4AuDIzmcUqGeBfAmDryuuD0+KYHambpF0fI+LDoUBNw3mpeD9Gaj9uM4nQYxOFM1jdvTr8p4A91nA268SceN6'
        b'ua7kBxShQ3TEXon3kmdmI8E/DhAZhWOp6DCNZhjejY9BJsLgrcRzJK0TItSU6EfBCR+0zGoLkxxKTWHQvkeZeUCbS7lVF4rM5I6wN529ZksCI40UWsDzZrKRfaJvm3zT'
        b'3AaL0XEyIT/KKqgCHeetCEc8FTBOOT7BEMxT6Gmus3Hr6TyKYPBF5moYVw6fIyAJcM212QIlItEzzFEC2hxnb/qaPZ3im0K8i5WldnwhARpTwocMgZfZUNXb+uBmMeks'
        b'Lo1m3nm24Ra8y2qOi6uWoV029rikBusZ9aEVn4ymp9WluHAStHo0D28mNnkz/Hhk2kSwMyBz/RYrOYIvQevCqaWSMugJMps9127W4NikYTnaR9Pq0ROfB6iK9gfZotW4'
        b'hUzPaktSlADZALAFoeZOmA2dJa0F0FbobADYBGgR7LbVFmzh0y6sWEfxQSl4VELHGE+EelQajg5b7CO6tbgmAdNBeycKdN1UJpLwFncJfhRx+ZFPL/LpTT6w7U1dJ/jR'
        b'M3yFP/r52LUP/5FrX/APJOMJ9rovFcMKrIyXUnJauXc7moHkbQzrushzu53daRJ84wBAbe1iCc4uSVJHAFTIVz39Sqf/Dbtgw9+OYkaNjA0gDscMj6lFMhgjm6UWY1TL'
        b'L1ijYiaclFsGFmHUIoRaBtDVY7p6aJblZCRMT0jLmTEnY1KmWWzUlJkl4MPA7CkcyJw0I5MCRVpYhkF/v9cMw0oShEPNgemaVCzv8dBUMhdvibeXt6ufVO5m8ZXhSs1o'
        b'XDt+vpP4wjHLft7+uOXzteQb11Bvkfevri69E9ngfgU1JtqaJ7lwqMlPPkM8tx8+3mlJ26JfYxxnL9Qr2epDhWx9LN9q3vpLXOumHkRQMrBBfLQStZtaapXtdVd7UA6P'
        b'TJDt9aLb3nQbZHt96LacbkuprK8HlfWVCbK9j9BtP7rtQWV9Paisr0yQ7fWn273ptmyrRMtBrtSP7uW3ugJLZ4GXOuBRrskb+CzCdqBl25/8PSOqE6kHC0R3N+owynO9'
        b'z3q51p2K/1JJXnLMnQrsSij/RzpXDrWh7l8rWs9mB7L1XmRuMEA9kIrv9lD3obg/WBDfTUmfdG97Bz74DIsYLDnElHcVISCGAiJYqmI1NH6dvWZnh43QGUBLF3SvyK+S'
        b'PGOJHlS7gU0P7oqZ+ii4S9aUljGP3ZRab+dF2gCuQpVuZndBwA2kjYSfdHlZyjyogsiRWrvYLF5YTPYVadQ6UxHZJy0lOV9SYlAb2uV/HerudnTNZXGM7k5mVR7CqrGn'
        b'1TXXwyjvFigl73/XbeVdqOzfrLz7YOHdTiK7Dj0L/EbhXZubYs0HuFbvIhfksLM8FCtU+tJCVYSjrMQq8gtJkvnUgXnXOsBdywA7kPx9iBp5oAwwaY/M13Pi5CyFXpUH'
        b'kvPkp637bOUQO8fUTLPOYS46Zp3Wbchwm6pwkHkhI+SZeIAIsTPBYceuJ5yJEHdTcNhhpO0ixL9DcNjy3LNqZ1sKnVq4YVEPumGWzkJw8C1sKQyaAp2R1DDppEhfRptT'
        b'uMIk3DZTMTja/k26vj7shUpFEbxTiC/xKc0N18vncKY4jq6XbcSXHAv7Mn9kBOh30PTdgNfjtfEyeTzaQqMdMKInF8I9FecSnzt/T1GKIOt7JAy1dh0rFbKhEeMTfYW4'
        b'ny6VEWxahbfTmP89FV5t/CnBOyNXn9lzNmcCC/WCIFTZpV4wJSJa8ps+SwRr4Bs8yQyizZ3GuiYd3ngUmnhFrkwTO5wzgfURPqEl8wVHKr+n0eUpSWGZNjWAnsKb3NE2'
        b'1ILYW50/hcF7pMIlsKZ9m/cUvObW4oNotWPd4PZpXntGHwmhGT3jiQ6mCVYLby2E9zUtPUTyXP2Hc9M4E1hNoaszTI5iDbFMZ9qjxJfQORHozR7zxBvQlkRdceonEmMN'
        b'RKIeFPHyxR58pGzStOurIrYm9P+xxaU+JHdHzX4+tWl4kyh5f3DjSO+Rn457K+/6EWNBg+ecyLcWKf/1+i8/5nrte1qPKwKLa1uiws/Xrtj5n8/SEhteC9n9Qdrywz4v'
        b'tD25btZdz/feiTp+9/Do8TOHLmpu+vnA/Ev6HzKN1+b63Ar6OWZ5YHBy2PXbPltXuGyMyeczlR5Mh2Y1qicfq/SwML3Ee1G1JBC1LaWTuz7T8N5O78D7oaMSKZkbXaQr'
        b'A/HBM2wjoY1sjgsXhHdK8MkVglDvRlTvgaqB2Gk3XYXJahFeT6fKA9DB2WFWfeFmMos9zkdNwTVsOr6tHB/DZ1ZYp9IwjUbnkunBcQUuqBGfaJ8Y0llhC89Yo3uk6Eg5'
        b'uSv2832Y7I+ZQcupR3vxHrzL126WClPUdPx8GVjK4VpU486wbATe44Xb8BkjfXdBdqRScBvhyqWhNW5oHzqK2/4wnG+lb4I/CZtJ3SpuAtUSFrm26wozjWHqvNW6ZRHr'
        b'JQjEicrwVQj+BMELECAIMAQvQvASxz1YZkfanUi8OpRJSbpNyjeymfU9xb3VheO7zuV4OJqjFU05JeXNJHlilM/2tGzkhmFXF3LD3Wd9FlrUX22gldNMzbZk6l4/uxxQ'
        b'oPCQwrNW8qUFRjlNd5413SCW7u+TORbKLMkh4MlpmtnWNANZmjYA6yHT01rSIxjJaXoqa3oh7ShKZU+t/R1Syhbc4jQHamsOAuCthg20+Y2Swu451pmRszQLOqRJatkK'
        b'iGzSVPKMpU1fkVhNcdPzxTZZAUt3eJapLW46CehaFXiw4IX5rAd1fizTyqx27y7dsnsXHFDedvHttuiUBpQ3u6s5RU9+GMkpW4mpTlGC5JSVRB0argi1ZXOTbUoQJyfZ'
        b'CuZQwMuyATok3Z8UWhMarcgsKYKpBZuLg5c5gZKtyisxlQlKTkYCYp3VDfwD1RQNVIlap6WaOmUCSO9YKKG+qTtNUm0Fgg89B/gY/iVZNaBUXc33IqNtZjmKEIvQjPP5'
        b'jm29Mizf6WFVhCTkGTT5hcWgcSNM/qgnPYcZbW8HRqOuoJg2BaYk00nOzKjQ2ZZKR+ZBBU7kaizzm0h6k6NjrdMcSClSGQ5vTyziyHCGVR0539nMjLZKHb0eVLWg7mJi'
        b'u6/Kpe1YICi1TmP84zS1QkBDiqpfKRWhoUUw9ybFWRYa+ptVthQhVFErgglTPUzUXShqdev6h9W3UjjR5XKmbzWke9noQBTpUuUqxKpyFalUzIsc7lylypZsItxGk4YV'
        b'R1dMM0qF7RPT0ubMgZI5cq8L/0pVy4qoc16NAYaqcCphZ50y22RoeNcZ6lJ6q+MLFPa0DLU8KQ6zxQCRrWAXST5qmHPtNVtqjuV1ks1jQvaSJ7LYqGOZKtE6ljJTLyAt'
        b'g9YHXEA9FKuWwu9uqjjBv4QOkRjpmzRdfmGZjkp1GduF5Do/s07jjFBEgky2xkQ6V2sEpAXrFEIVkR6qiDxxk2ZGzFCV5Wng7aRjYbEIBWkuzG2q3lS0UFPouP4jFFF2'
        b'p9HUVCZtualMQ0YO8FatyCoxGGmmnMQxYrQiwaQt1OSZ4NEjFySYykpgfFvo5IKRoxVJxWrdYh1pzHo9uYDJ3RntSu7k6mhHWX74ChrlKBqdTbaKHi5bMY7ie7h6iaUV'
        b'2V71D6h5hztnsJYMrxHt8v3QLdG2+FoDKU0I1K01T6q8clOB0nnzs71cMWqw8wbY4cTIWGdnkmZWPLSzkig7ONI+mmhn0UR3FQ1pFNbydRFHjO1pTosW2yEyB+VyOqAJ'
        b'1EHSwwm/KB4gmJT0rZauPCSTjbFOB+x2ZiLI3JOhkG0RjBOSQjY1xeSPNHMFjEExztU12zmNHaMZbhfN8C6jofTHDnKLIVRjMRHGm5FOL7PSJdmlk2bSnhp2KELIQy40'
        b'cXLbnVeDyQCyk2S0mCj8ClfYYLtJM6crQmbhZwoN5CEleRnhPCs2TM32yKy7hUxZojIuNBmMnTPVFdxzBi8plOw+8rNCtIQOKwLdwzCUUzpakQ5finnDhz3R/cuGs8uG'
        b'08uc3w0LWVWAkMI2TJ+7ageUyUougS9yYufznPdiUzQGQ/HQyQaViQT6IUMn6wi6c95r0dOd91UQj/P+CRJw3kF1lTLplSYVEhBG+n7nXRPNG8FsasfZcFZ5BMVqNGWA'
        b'LOCbAKzoLvFdXsnS0QpYYCb4SQuolewgde78psJFQCRmV6n0Ctjo8op8XRk8kCTsEu4x/jScyX7QiMMBp0dERUZHk5bmPE9AXCYZgq8uW6RWRUo7mXQqXZ1Eqc/kDsGX'
        b'Yl608xOFbs6iKNtFi7aQskcrJpBfDAnPGz6qy/Otjza9pOOKX5f1baF6C1ey++O8swaKN4FoExLSye1x3iPm6fJJhEkTSdIOnshO5GxY23eoguW7lJoxZ7wjzpV9JurN'
        b'/F7IfTI7kucMeB+PthmepJesHEG9cso/npib+kWhVCBJblEnpiTNBE/lAq9vFG6gp282+nPhJIW24Nw+nw7NZwQetDkZ1+EGFz3eQqU+cCM6Imhh7cuz8OzwgX4W7rRW'
        b'TeP659jlYOnM3Y9UBX7eN5czgVM0n6XhYSSjoPU4FT+FmsGsEB1PTmMOlzjcijZO55aOcC8YjxopqehAVjofkrjRiytVPfL27IBpoWztyhfvy3LkWwli8UfnprBliyzb'
        b'xcZatEumxNXLdQeSR4mM4Cz00OoXa+vq6q8mi1XyFwt+unhfF1FzWlPvt30Zn+JS+Yvhz9LHYzbFo31r17foKjbVT2lMXy69OvQOn3Xxq5d/XlxzLPH8werrAbcPfvf1'
        b'9Hfrtu8sHLGu5+WbSz4Jb1t6LmTEr1sjvV/96C/ZP0nvPOpquu79j9PPFsz9WndI2/iJt6HPqeOLdt/5Odfz4KRDX775+veaU9pfFureLF/wXejt5iqT3963wyo//tt7'
        b'd/765N1V7/3dsC72aNKa4Ld+lu+Tv+0ZeNrX1zj2vxv3XUqZKTNWK8d+uvfHiL/7Dr3yXdWTw0uL+U837nn7/mY/n7/4r/o0K7l/xjmllKklPY0bcBXjkuCLmVY6yclo'
        b'tgy1huy+jI6lokp8HkwqKaWktCc96BOPd4bhqqlJLmgDOi7hXPX8AFSPzzBvTifR9lDPlBT0TGdKyfGYMhBfwCem5QkrTOgw3t7VEpNhGl1YGzrQZO/MiXpyisYnJPik'
        b'HFfQpAtkqMEqaZjbi4lmMUFDXJFDhQjQRUpbT00Scfx0dBbXikK18zszQWR/kG90MIeji1qwctthUWsVN1VKdQklIm/RIOrXCX6DvaGHsKDFiwKoViF8y0XlMutSjUqt'
        b'Tu/gIaT9BTbYc9usYrk/VMaVEptI2l2XWkuywOFS1s4BzpeyOuTZOQWE+ogCcyVuvcTqI+phNJwKSdYXkUg69J5QpM4agoMFDcEcCVdf9Ah4Akj9Oj2Kmfaj6r6o0WgC'
        b'9m+thJOA9MRJ0Qp8DNW0c0RwRTCq8SSbs2LLuFmklVczevAG0nVVZ7IrRW74Ar7I4VMTFtDEvslfIfoo4Q740RjjnaQTaN5rcCVqo3QOfA5fRTs4DT44nukp1aPGAEoA'
        b'wav7om1cPtrNtJJ+HeXG3Z0QCD4a9H4ZAxkn47nhcu4j33jwBJF6vLiIWfrPeqwH9/KgSXSn++Qh7Ez1fBl3XBlNuvRcWdS0ZHbmohwvrjA7CnaGr+lbzs5ckufJvRkf'
        b'Tsmgv4bHsDNfGebBvbwkjO5EAdls5/1sV25pcB/IkmxQSSYrW/w01JKZkZEBNI2ncXMih1YvxrspBUSCa4DmMYweQm34GVJG3JTPxpZKZV5mBjcNbQJa37PkSMoCemOm'
        b'ovrplIvMWCO4Kh+II2gtrmVugCrRaryLxEpu1QFS/cAeyUatrC6voqv4ACwi9Ud7fElwDNUx3/s1KxMpb0fzBDccncStjNJzOB9XMB6I7kkuIhivpqzaAHQWbbEhfaDn'
        b'elLWB147kuZgMtqLazIzFMBKbpNl9XRF+/FafJgNjKNVtv74Z+AGoH1Eov2MlwHV/d8yKVc6dzAQ7sPr+8lYzV6PdOfGBgykLg0+KBzLhl/DZFxJataIW2m5yai7jZGO'
        b'Ivv05DKGzYIGPTZjtIyN7TFR0swM1KTkuNEBaMcKT7wfr3mSxpOIW8cbvaKGSTg+aDA6xuHLydG6y7N2Soxk4OZyzmQUbY4D6sfagn+6V/0QtD5m0M9r91ZuqWjsdaRx'
        b'gzSN//rC8/XzDWve/Y8iPf6v7kd6lHwtn5YYNmfM05d+eO/Ssq2p27foVFkf3Lyx7dLn75q0Hq3Bb+x4Kfj9NMPa9EEbjy/6c9u61mmhO/L+MWnDfK+RN8Wt2pnXXmhY'
        b'dmVS/opN2h73+s0foHildqHip/0LLvSOOFk4MfuvM6bMHdR3yzfbE/ennHgm7vVfx5uHKP+Tm/HavvfGrPvSZ9DFe48cvO1/rO7LD179sm5Vw/2WL2b2+fB1VdDl11Wv'
        b'HpvVcLgicnrq0rrqDfdlO1fHV34xrkK5bmdEQfa78mvZl4/qffee2/1xXOaN+Z9vmfOdBinTm01Zaat/iDsvyRn4ckqO8ftTyUv/c3l29P2t4aNwbfg5r/Ob777v7z+j'
        b'7F8pl5R+dExbugzVWKwmbMezQNAl7zCkjcdNdBRdhJt7hVGbE3JIqs3GF3m0GTUuoePUrMB0AotSReRx2RXZX4T24ZOC7nBoj8fbBRJRw0xwQNgPVzNiQBs+F2/DE+mL'
        b'9gJRpATtpaOot8tsAtDQxphOTA7FJBd3dG4RTSAT71FYrU9OpVADlJn4JM1zWSo4DCkiTywjc1AqRypeSw1QfNDqHvZ2NmR8r54tCUSt6ARlWQwbjVaTJ7AJbbEyToBv'
        b'gg+hCmatc3Ue2t7JembaSkr2aMPP08oZ0FNwK0FgiZeKynpW96RZGEIASXUK5WjMpbVAuR7eqFI8geCSQ5SlMZX0tkco0wNVeneQJNuBNzNhoDNo73IWCzrdWyB7eK8Q'
        b'J7ribYzosTVvREcTGigRNaPpt4Lhp1Pj5O1mOvPQc2Cpg7cvpLdpAd6PKmyULfDRfsDfwOeZIY90MfgTtDPiQU1DwI5nKb5E5ZsTNGAhlIoa1LYGSRZzJHQY1TqxYHmA'
        b'H0IqJkMRS3lnxFIqEXSUeYJT5LyUmsjLBWYrsCzklGfBk28PGzlKufBHP5+4BvIfS/t4ELwgERgYcsHUnr/r6s7f4cmf1ENQU6PIobNgm+NC2Em3AVgJtQcrT3GNXbk2'
        b'tE/UYARQ4dS18QTuj9FvM5jssYtj8TK3dBPAL3zSgGqYdllmYAf1MlvlsnJ3OjKhU+j8SIsGWZwbUyFziWGDXTXekxjmRhr+VUotzH6C7taT5/ty2FQ+53GOypAVLtZN'
        b'PGMWG4HXMas1N652jAefIFt3X639x+2Zc+bMnft53xc9QzY0vZur6v9Zcezfz/V6YfItSZT/96narPoROVvu9/+kZkreIzOjrr+8q8QY+drPR87UBVxo8GudIpUHjnFv'
        b'/XL21dNH3ng0IZ9f9mI28rh2fbXY7UPl9sbLSannik1fggrZmYJXF487XbCz6taSk6uK388a5ftlbGub19VnXyh/6ZXAa7uP3Ovb53h6/ohfLifenlNY3hj3/Uuqyu+/'
        b'c6l4P0ZdnqD0oTS0PnI/pkCG29AVpkLWA51mRPL1aHd/KiLWrkL2BKpYgdeq2PN8uDc+IIiMLUINTGfMDTE+P342epSt0FjqYyA1hi8Zx9LeQoubCmxFzObhC6Bjhg6i'
        b'9fgK7XCC8FbSFbcrkRGgscMznsc7FWgLEwmuUvcWdMjwGk8mRbZgIb12EZnFrLWVIUMXJMy9boWc8QNPgOtjQYgsL51JkWXjOuas4HIw3t+uQ4YPPGGRIjskDFMExuxC'
        b'6wUdsly8lkmRPRZLCV1GvBdfSrG2O3c/Hm+bhvbPHEVz7S9NsGiQ4YYCJkNWUk6rLBA3jLUOVGiPv+BCgQBieuVyf/Q8yxVaPUdQIUvJ+ENUyKhSFu3hQjv3cKu4iAFd'
        b'C5FB59AuRGZYwnXNAFvaIdkgss8Y3rlPeor78IHSY5aESW/RkQnCWGE8/UpX+tozwZZxnC0drBv2i+c56kC8TFNkZHwuO4GxHr9rctyNO3SZA++spKqyOKoo5ioXyaj+'
        b'Vy/lb9UTk8E4c19CYlEs8R0jFdFZhTva7Wa0IjaXKHyF8wrgcYPnTKUoXec1cJiLMZCA4UuDP5pUd57xoN9Y/MHA9V/f3WD891h+U/w1cQb3RHVO8YBD3KwNI44fal12'
        b'1rRAW+ti1n665/7Ob299+M6nK3L9br60bFXrqs+q1Yv/fP7Xfe/P/ecbt14+svDzqaNuSH/Y8u/xs4MvbPxhcXHPQT+kxP3ddOwvV369uWDN5Dn3kt+4tTK5N9+46MWw'
        b'bOPLypKYDys2zR/VY0D46FW3+iX9VHVr7+U/Y99jr1z7r88Cr39yYtrsgb18V21Z5DqyVdLcUqa++e3aLT+GNLYN1d1ojdh1z/Ce4aUx41quXQvGrruWRh2svaD86JcD'
        b'TQkf/mnzR71CLuaWDp6a8sr9v8bu+Kp6DOq17VzYQbeCr07XvnJzV6p5ws0zmX2WL/D9qsX/byv1N5se87gQ9Ogy7eBl7yjFFJD54mfd8EYCU0SJeE0Mh+vQRnSJ9S/H'
        b'SjR2htVFeDe8DMIXC5i6eAra7/DdjoR0QmcJ7D1b3vn9TOD/ThN86IB0O2LLI+gwoIRVaU6OvkSlzsmh3Q7oG3EBPM+LRoj63edJB+Mq8uWlAQq/gFC/8X6P8aLR0BGN'
        b'lYq9PYNXcYt5keEN67MnNvM5OTYveAL+H9SByPCm9dGFnFKROhiauM/inUue0dZRP5Bg7Y1oExkGqgiarUKb+ge7cd6PivtGDtJNv/6qyLiJnBbz2rd9q2K90TA/l/t3'
        b'vpHHT9FXx+fF+s5qmZC/ZGvS+h/vnpWOGnxu96NpHyTumhxQ+MGOe9//RVzVPHV081s9M+/lDLzyevLO5raw7CPjGiZW5aXIZ739ybPhiduyzp25ceN5XyzhJyYMRE0J'
        b'np7rR0a/mbc+zjvmQOU19wLJ/NKXvO5cSRm3don8l9d8qv8WJM0MeQv1J2gCSrdwPBm1yZg8dSoMYino5ONunCd6nsdHxsygbT9fi/elkAG7Fc4BAdEeM0bgS0A5fwaf'
        b'oUg/GF9Fbaz8AN9hzhiLd5AK8BX3Q3tSygD9uS6ISUlKC01z41wl/Ips6QK0kyGSM6iODNIbh6JDqNqVE2WCe51avIOOn/gsehpXhSWj1jEunCiFwztxK2pik5vn+sqp'
        b'ah6w3Guy8XkR50kG/nrcjI5RKKTELY8ZrSeQydqzIs4jiUctwY+zR3ob3o4OptB+Ex7Z3vBCxBtXi9Pxob409aA4tDElCV9ALdYlhVJ0lLHsLyYtplCUvZPHz5HpkewR'
        b'Hp+a6CLMIc+jnWTyUx1eSk8Ygc+6cB6ojUen8NPoDJ37EOB0tBc553kZ2rBkkQm3LZItMmWhCyLOH28So5qywTSfj7uVpFCXClAW9BQi6NUT7SYQB20TIurv7wWVPzSF'
        b'dDp18LYYtty4wEGS2XgHquyJL3Xwr9z3//5Zs3/03B/Q/TjojdqJFpSK7iVlXoaoqgDM5WTicfaYaBDDD7QDCjKL9ZpiswRsec0uZaZSvcYs0euMZWYJTJjMkpJSclhs'
        b'LDOYXagMvVmSV1KiN4t1xWVmFy3pB8mXAZb+QaOk1FRmFucXGsziEoPa7KrV6cs0ZKNIVWoWl+tKzS4qY75OZxYXapaSU0j0HjqjhV5qdi015el1+WY3xsA1mj2NhTpt'
        b'WY7GYCgxmL1KVQajJkdnLAHrRLOXqTi/UKUr1qhzNEvzze45OUYNyX1OjtmVWfPZ+Mzn2d3+EX7fguBLCN6H4N8QfALBuxB8BgGInxq+guBjCD6A4BsI3oLgHQg+h+Br'
        b'CN6DAJabDN9D8C0EH0HwHQT/guBtCMwQ/ADBbQi+6HD7PKw97N1Epz0sPfOeVAsGvPmFQ8zynBzhtzAa3QsQthWlqvyFqgKNwGpWqTXqdKWUIkfQqlXp9YJWLcWWZg9S'
        b'/4YyI4h/m131JfkqvdEsmw62hEWaSVD3hjuWWrSzyjdLxxaVqE16DTDfWQkkbhJeat/gRvlRHv7/AFDy4nw='
    ))))
