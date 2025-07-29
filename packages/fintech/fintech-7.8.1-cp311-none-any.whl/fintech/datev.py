
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
        b'eJzsfQlck0f68JuT+zLcCLzIGSDhvtWKKHKj4om2EEiAaAiYwwOr9SaIByhWUKyoVPFGbS1a29qZbrfbvYibrlna7trd7mG73y7dtf92+99v95uZNwkJCdZ2u/v9v9/v'
        b'C2Ey71zvMzPPzHPMzDO/oaw+HNPvX/cg5yglpaqpRqqaJWXtoqrZMs4Al3LwkbLPsijqIsv8rHKXctiUjHcW+S9aUq2n1O6r2CicL+Xapt/BQqFOskmlsCgpr4pyaRTy'
        b'v9riOi9/yfxldHOLVKuQ0S0NtKZJRi/cpGlqUdKFcqVGVt9Et0rq10oaZWJX1yVNcrU5rVTWIFfK1HSDVlmvkbco1bREKaXrFRK1WqZ21bTQ9SqZRCOjmRdIJRoJLdtY'
        b'3yRRNsroBrlCpha71k+3qmso+nfDDfQxctqpdlY7u53Tzm3ntfPbndqd213aXdvd2t3bPdo9273avdt92qe1C9p92/3a/dsD2gPbg9qD20Papx+ldCG6AN00nbPOSeeh'
        b'4+q8dK46gc5d56Lz01E6js5b56vj6Tx1QTp/nZsuUMfXsXUsXbBuus6nIRR1h/OWUDbVEWLbxFvCXCg29WyobSgKCbMNYVFbQ7eGVVGRU8ZtoDZyVlIbWC5NQnZFvXVn'
        b'B6N/AW4AvglDqiiha4XCGT3NlLEphCB0snOtwjkngtLGoEB4HlyYATthB+xZWVm2COrg/koh3F+8dKGIT8XO58I3wA7wspClDUGJ/eBQqLq4HB6A+8rhtkK4j0W5FrPB'
        b'cBTQCdnaAJQCXF0DL5YWJ4ORxGIexeWywEmwB+7VYrAyweHk0uLQ6MRiEXrdvnIe5Qn3cirAdTXKjDsR7AZX60En3JvYiiDalyhFRbiCG2zw0ixn7QyUoABcBFdQgutR'
        b'8LQ70G1Yp4U31rmv07KoAHiQA/Y1uyBAo1BCT2dwDXSCg0ml4BR4TRSPIYYHcYgTFRLFBTvBrfh6llWzhZib7QJyjgS3o6ZDvcxFfUyhvnVCeOCCMMANYYAH6nUv1P8+'
        b'CDsECAv8EAYEIAwIQr0fopveEEJ6Hw2ZDqdJvc8mvc+y6322XQ+ztrJNve8wztL7DZN7P8BB74cyvQ/UTpQ7taKNomvLtkyLp0hgaRMHocR4PIuqTdyzdDkTmKBwobwp'
        b'52fYtbXuLhmhTKBCy6Wcqexg9zm1ZW1ZydR5SuGKguXeQdxHuQWocz6K/Qv7Zoq3OodC2dF00tLH+uPsBi9qTm3qB6ovuDOY4Da/v3iNb44PZy98wPrHilj6VWqM0iZh'
        b'8A7MrUWd3pm0KC4ODiHf3qQiEdwLzi+JKymHBxPFxaKSchal9HKZBU/AHTad52au9V7ceW6mzuPZdByFu67BzdI53H975zRO7hwnB53jXqHCrcuMnT2wM7lqsWgZm2LD'
        b'a1DHoVBNX8/V4jzwIhoEVWwKvVgBzkaiFtqjnYbCmws1VaDPfzGKaaLmgzPgttYHBfPgnqfgYUQtkigR0CW5UaSQZbA3Ax5GLSeiwB1wQwRfmEVeDI/BnUlV5Yvgfh56'
        b'sw68upk1vRIe1MbigQF3b8WDMaEUjaCOskVx4Hxi0VJ4Bg7iCUIMz/PAjpXgIAEmOWQZuIEqN5NaDffPhAfhBTnryh2u2oDint01cvzdWSe2d5w6fOPw2qBIDlxD79km'
        b'vjIt+/h21tM/3x3xX5vcBZwCUYGo3qOes8q1Pna5x06PhWfbA5qCF3jUx36ROvD3NTG9B2b8wvds8Nu8ooYZc1zVrm4XPonP7DqxUPDjgZjrZ/re8fL9/RXJPG3Q6uX0'
        b'koBVsVXBgmMVMkXuupH9Gbs9lmZ9sCdmyONHTWdLt5U51a3XhLSOaIIM05+vWOZ+tIQN3X9SsC4gz/NnP3l+OPL8r6ljP975J8+Ffzi9Nz3l7N7/bhXXvtng1fYjp7TW'
        b'Boq61F0k/EOBkPcI05sUeB12lcL9CXB/uagE6sLx1DcNjnBgO3vOIzyzgIs1soQSETgHBqGuuKyCR7mBa2x4ApwsICXAAcolQSwsSTDNi15wGwccgXtawAg4/AhPjfDy'
        b'etoNN71WFL+2Ag0ONuUDb3PAZV+4/VEgShAMXg7Cowa1+j40plsjc1hoCnxhhtBjjB0nVHmjJN/SUXsgh6a3TXy+8p/ZoGppkykRCSbEXYwIs2z97DEPlUwplalqVLL6'
        b'FpW0zfaRjctqRNj35TZq/FkW5R/ctaQ3pnt1z2pd4YfTowca9NNFhumiccrTYz6Lcbudu1hdGUZBYNcsIz2jq7A3pbu4q9joF95VPcAbUOv9Egx+CeOUm898lpGOGfK7'
        b'GnohdFg9Mk8vzDcI8/V0/pRZXEiWyAHOwPxTroOuk9IN8YY2jMZm6f2yDX7Z45STbeL7dOo9OnU4bYSjp2ca6JmTX6LR+yUa/BLHKZ4lX8FAwRDvVMlgySmvQa/JL+MO'
        b'NVm9jEMyRZ/zPO05tF5PZxroTHOG3wZHjkZljHDR39Jbbnfc9FEF+uB5huB5o77zjAL/o9mHsnsL9YJIgyBy1D3yr3jOUeFJR+g5xmf6YMyppkalVdbUjLnV1NQrZBKl'
        b'thWFfEvE8EROrQ1mqPDko8JzwaTOfwqn70XOl7j3N7NYLN9x6rtwHngG6OQda/et3eY2zuaxfI1u03RZHTn7ch5wvbaVbi/fVb6t3OjsZXQW6Ny+HOdRPG/b0G2VzJ8a'
        b'U6cTLmnUDc98Fsdm3rYw3XWYvPCOUjLMciOGW8qq5qB/rpyq5qFfvpRd7SR10VENLCl3l0u1M/HxdjlXM2F85HNFhIilYzdwpE7oyY3wklz05Iye3KUsxFDvErqO8ReT'
        b'RqsgvffwH2jM1HOsAOKaCclWDBCLYXOP4oIpUjSmcYjD75jE4W/hEhrHsaNxXDs6xtnKNdE4h3FT0ziOAxrHZRiQW2u5lLEN4cacWsXK8GxKPuu/b3LVaDKlOjlvH393'
        b'5olTh3M6WfzclVEf/TEwhj6Z84LP21d556U7fpb7mX9yWi0rw/2H2z5ZDj8fTF62XZM649MyyZBEIZtr5LzEER91+fW1u7LevW/l9QUM1904f9jlvZjCgVtv1v6oj0/J'
        b'anyD/tkn5D8Kw3PxZcTSHkkoxUxhIbiD+cIEPuUFznLa1sKTj4JQkqLcXCYeR3Iod3BpfSLHCXaGk1jYCY6D/aWwswyxyUI+5ZxRDvayN7q4kdgG8MYaTC9Li8FliuKD'
        b'F8CubHbQajhIYkEfOMUCnZXFicVcRKRfa4H9LHgb8aNMybeyWhJERcWYfjiD9mXwJTbYBW6CI0Le1IOQZ56dydgbc66pkSvlmpqaNi8GicTmADL/ailm/tWwqcTkS7NG'
        b'AgwJ+XrvuC5uj3vvGqNvYE/pfd/oe77RA2v0vikG35ThfL1vRhfLGDajf+3QjKGUoRn9LSixmzE0HP24GgUBaBT6xKCcR0sPlQ5w9b7RBt/oUfN3nIMiSQqVwDIb8ce4'
        b'apmiYYyLxbkxp/UylRpJfio/nMDfUi+MQLW1eHphJhXM/9vVaRVOqSLTCplY1GwWKwLPC1M739WE8VeM00ddRNRlzzxOPdvR8GyzDE9mcDawydBkO2A/OS4OGEr7wYqG'
        b'H3srxzQ0HcZZhuauyUPTApbN0NTGo6eNq9LcwHAu3I8w9wDiweHBqiIGvxctJPzoU/AU3wfxK2fkmy78jKOeh/KU3750/N10NGhPHU5Bw/bdwM5dJb0frd7j+3bFnvhM'
        b'/h7Zvs+XubtfDJKcLt83Z1ZZ8i/ZUZ87j3acje3dfoNHfflnt1fmRgq5hD2CF+Eun9IkcGBiTOERBQfBsUcRKH4uvJMAbyDe6CA8KBa1opGJ+B/QtZkK3soFu6Eugowe'
        b'DejdQIYWuA5HyPDCY2spuPEI0yMw6JpVWilirc+i2OtZ+WDgaSHbahTh/jMPIUQaG2UauUbWjEbRNAvGWcLIQMozDaR5HMo3sFfTv3lUEI++HwZHj8bkjizRx+Trg+ca'
        b'gueO+s41BoT0tB3demjrgFQfkGAISBj1TrAaDjxVJH4rVylplk0eBDwyCCxjQITHgAOIcD+rFcwwQDAVcFisQIzsDp3vdAAccUmgLnrmcP5foU9TDALcsCvACdDuRsbA'
        b'GXDlcePgCrgg/3SzP5eMg7LKLoZ4WY+DUwKbkWAeByfK5jxdlrw1dqdHkaggmdPIp/6Y7KqfvkfIeYQVJGBvHLxICMtxhdU4AINcMgzCXalJo2AJeAUJAmQUgB4wzMga'
        b'Bzzh7QkS0wX2kXEA+mCfkDOZeHAI2k/gvdoB3qtt8D7HhPcVT4D3kZiuuPam673pUfK1JgIE61Vi/GLeeolCa4f7kwlAhi3yW8BqomxpQDnC/nCM6VM739UQUGENmuO5'
        b'n6A+xzL3Y2UE1cD9vzn/8xygPq9Ci3vAPUpRWpzoB/qKl0CdSCReVFSyFOoqqxhhvwjJ/WIWpYGvufBhOzxJSAbcXx3hhtCq42uIhpuXXFi0h6OWozxvP9h9/N1UogO4'
        b'dfjaYXmQAGsBfvi7Pdvq/jGtkJ9dJFnN//jyns70lPWpt5PfevfnqYZkzXXpm9/7IR5UK7ofpbyXvORaSvLAp3/q5nxSt+ezgOHkWtaJpvWpqYPJXCKYC7f5Hrj5JRLM'
        b'MavnDw67mYVmTDLgYdhnEpvh6UBmyPWCy0+XonqM2NKelPhHmOEoBAfAy3akB/ZXM4OuHhx/RDQ3I+7TyJArBLcslGfFKiKYw1OLmhIifMxsHeHpYC848LU8nUWeGuNr'
        b'W7GA3eZhQn7mkQzHLabhuIJDBc7oahuIGuLqA0SGABFmuvJZH2KJ8Sl98BxD8JxR3znG6fQ4xfZZwGLcrnmINA2kD+aNBojR98Mw4Wj87Lu++vj5+rBCQ1jhaGDhOCo3'
        b'6YG3b4/rfe+Ie94RA1F671iDd+yo+Ws1pJ2YIY31r5PGslXVnCgTRTMLi7PxsLatWTNOuJ4yk7PljyVn3z1hY0a1tYLRlqPjEAUj0Q2biBlWKE4ajf8GhaKdrt8RMeNU'
        b'yH/cUcNR41lx/sNYTJoidkec6EZj7sXDIkSgnk9JTb7UsOuzCyuCAtcEbftLazev7Ad69xV3U+lnPH5/K/mtC29R772X+vPUiOOvbQs6/svgwiV5a/vW9q4JXNPbvO2P'
        b'YUsH/nvF2tHVfj+6iySrS4G+VWfViI3DmB4yG+wziUXwWKh5JBX7kEgwsgAOgU746jwzZcJjJGkdGT9+aEDshZ0rWxKL4X4Rn+I/w44E19sYkek2PAyuwU4O8pilKiRR'
        b'JbkhfHsCHQXGN5q2EpCcEOnQqBCF85wgJfiZDKcW03Bq4lAh4b3+A5HoTzq4Vj8j1TAjVR+U2sU3RsYO5t6PTLsXmaaPzDBEZuChFEOc7tKueb3RxsDp/W73A4X3AoVD'
        b'UfrAJENgUle+kY62aH0Corq2DCzTByQaAhJHvRPtaeKUY4dQRKuhMx8PnUnVwAKeupUyKVoa0dCZhgfH1M53NmqwFh9hqAp3mtADC6KYo62pGXOtqWFW+5DfvaZmnVai'
        b'YGIY6u9cj4Z8Y4tq05izSRRUq6LJtNcglymkaiL5EdaXsABkwiBV/7oZ1EojhTGwzaRVqcLxbzEdbf57IAjQ4clQV2QMCEKOf7BugdEvQFc4zuV7oN6dyvHmeCSOUw4c'
        b'V46HEPvsHFe+RxzO+xjHm+eBpu8ncwj2ECV+rX+aWxvsKCmHB5JKWJSzO7sW7ASDdiwA/vy1Fs9jrEmaLHY1V8qRcqW8fnY1j031UFL+AJ9y8JE62S4F2z5VO0mdqyg0'
        b'W7mM8ecrEZO26SvfebI6uaZFJVMmlapkUsb70JsgzEM8i301bZlM1aZtVLdKtOr6JolCRqehKAzvV+5lMk2bRkYXquRqzXk2wa+Hb6Ph+nkfEuxKW5SalrwKhE90XL5U'
        b'JVOrETYpNZta6aVKjUyllDU1y5TCPKsHdaOsEbkaiVLqMJ9SooF3VAoxvRBhYwvKu6xFpXySdI4KWyuTK2V0vrJRUicT5tnE5ZVqVW11sjaZvL5JqVU25s1fKirDQKHf'
        b'pVUaUbG0QiXOy1eiBpPlLUG8riIpf61EKqYXqCRSVJRMocYcsIK8V6le36JCJbeZ36HS5FVpVBJ4Upa3sEWtaZDUNxGPQibXtEmaFHmVKAV5HWp5Nfpt01plNz/UbcDQ'
        b'YUUubQIEBYnpaq0avVhhBTydMmVMal6pTKlsE9OlLSpUdmsLKk3ZJiHvkZneJ6MXwDsKjbyRXt+itAurk6vzlsgUsgYUN1eGpOS1uNw4U5DQHEcvkCHcgYMNGjWuJW5S'
        b'+9T0gjJh3nxRuUSusI5lQoR5xQyeaKzjzGHCvELJRusI9CjMq0LzFQJSZh1hDhPmzZUo15qbHLURfrRtNRyyFuOwqELbjApAQWVwEGvO1+JWY5ofBRbPza/AcTKZqgHN'
        b'ishbtby4cImooAX1janxyViQK5sQruFyTM1eJNG2akT4PWh6rROb3mny27S7o3Dc9jaVSLWrRKp9JVIdVSKVqUTqRCVSrSuR6qASqVNVItUK2NQpKpE6dSXS7CqRZl+J'
        b'NEeVSGMqkTZRiTTrSqQ5qETaVJVIswI2bYpKpE1diXS7SqTbVyLdUSXSmUqkT1Qi3boS6Q4qkT5VJdKtgE2fohLpU1ciw64SGfaVyHBUiQymEhkTlciwrkSGg0pkTFWJ'
        b'DCtgM6aoRIZNJSYGIhpPKrmsQcLMjwtUWniyoUXVjCbmUi2e6pSkDmg2lmnRNGJ6aFWhCRnNfkp1q0pW39SK5mslCkdzsUYl0+AUKL5OJlHVoYZCj/PkmDeSiRhyl69V'
        b'Y4LShvijvOVwsEmF2k2tJi/Asx5DYxXyZrmGjjORXmFeNWpunK4ORSobcbpCOKhQyBsRjdLQciW9RILoolWGKtIHOGYhWe21LmyCjIuqERRowojD2W0iTPlRVLR9htSp'
        b'M6Q6zJBGz1VpNSjaPh+JT5+6wHSHBWZMnSGDZCiXMHSZtDniSxB/QsI0so0aiwfNRBZvmnVStSUZ0xFzZYgcN1oFROdVy5WoN3D/k/fgqDYUhEkvmqVtHlNtH9H0I1Fr'
        b'ELVTyRs0GGsaJE0IfpRIKZUgYJR1CG0tPa5RwcFGhETFSql8vZguZOiH9VOqzVOazVO6zVOGzVOmzVOWzVO2zVOO7duTbR9toUmxBSfFFp4UW4BSMhywKXTcYlOrqk2M'
        b'hnCCMXIUaeKVHEWZ2aep4ixTmYP4Ssdvw3yXo3AbVmzqOjwmfiru7JskTp36zTZ82pMkQ1Olo2Q2JCDTjgRk2pOATEckIJMhAZkTs3GmNQnIdEACMqciAZlWU33mFCQg'
        b'c2o6lmVXiSz7SmQ5qkQWU4msiUpkWVciy0ElsqaqRJYVsFlTVCJr6kpk21Ui274S2Y4qkc1UInuiEtnWlch2UInsqSqRbQVs9hSVyJ66Ejl2lcixr0SOo0rkMJXImahE'
        b'jnUlchxUImeqSuRYAZszRSVypq4EmiDtZIVkB8JCskNpIdkkLiRbsSnJNgJDsiOJIXlKkSHZWjZInkpoSLapjwnEQpWsWarehGaZZjRvq1sU6xEnkVc1f2G+iFArjVol'
        b'a0BEUIlpnsPgVMfBaY6D0x0HZzgOznQcnOU4ONtxcM4U1UnGE/paJbzT2qCRqenKhZVVJgYOE3N1qwzJwwwzOUHMrULN5NsqaIGsDt7BlH4S29DIhJu4BvNTqs1TWt5C'
        b'k3LFKrOd2iXFPijVPgiJOQosFEs0mC+lq7SoOEmzDJFRiUarxmwtUxu6WaLUIvJCN8oYNEXk0JEaQGiVRY6Ju1xKsn1tYgflOyBKjsu2T0hUTBOtQyPmmzaxvKQpG3C8'
        b'qZEZf6qVH8uEE5qqr1h5FeedVYVY/bgAO0WUab1TVYydEqzi5KlbFXKNqhRrwliM5hLr0Uxay3KitWR0aHihR710stZSiLWWQbqicT7ln2T0ixt34gZ6jlPIQWGulH9I'
        b'19JxbrJPAeuLOhbl5btX1lXQsWbfms8aWWn+wY8o5OgK8R+jRiR7MW7CV8BuNTwLTuIdrR2J4DyXcs5kbw0K+7+qSnTNr69v0aKmUDaOec5F+MaIPJJWmeKhH6NIxDr0'
        b'r4LnIQxsRmwN1onTjNCFxo8czXooCd7kN8bF7JdqCfJ+fgcFLG1muKmWJqWMrmpRKJKK0HSoFJW2YeXOxOPEBJu3vLSaZrJhJR6eutVytZYJwHHWz8yAX4B1joxwwbxo'
        b'7lJRVX2TAt5BiKdADJH1Y95cmULWKMUVYbwmjc+EP9UknOWZW4IIG5gblZnmFbPESDMcmUnunNCQmSROIidgWRMlRiNbQ2QSUwnkdQo5SkB8cmVDCy2i81UaMyimkGIl'
        b'zjkpECdLdZQs1S5ZmqNkaXbJ0h0lS7dLluEoWYZdskxHyTLtkmU5SpZllyzbUTLE4FRWLUlBAaVMx2BGW0YCU+0C0QNdLkOTtVkNTGvF9IQaGAUyuGzWy4ppLCyYRX5G'
        b'3zvRjXRZQlleoVa5lpypkqka0ezYhmc0HD53KZ2ew9D4BnMSrI92FG7CGybKQYF51UQWwRVXNUtwpAVFHMVYUGWqbKmPy+Y4kkGhx2RzHMmg1GOyOY5kUOwx2RxHMij3'
        b'mGyOIxkUfEw2x5EMSj4mm+NInC3ncdkcR5LuTn5sfzuOJRkfjyhTY0rKY1FliliS8bHIMkUsyfhYdJkilmR8LMJMEUsyPhZlpoglGR+LNFPEkoyPRZspYknGxyLOFLFk'
        b'xD8Wc1BslQbeqV+LSNcGRHw1hCveIJOrZXmFiMRPzH5oOpQoFRKs2FSvkTSpUKmNMpRCKcMc2YSm00Q58YSXr23AOjnLJGempSgKz7wTBJmOy1e2Mdw4XkxEk3G5XINI'
        b'o0yKOBCJZlL0pHnYPvPETD45TqWAN9UmNsEmpogsLTVoEFdikekIJRERfsehAGKqqYmaI9KPKA3m3xsI596MCbxGJkfNorEoqYsRm62RN8jXSqxn/2oig1qU19ZsBiO5'
        b'Wi1iWrNJhTJGrJHJ63BUGeo1vCqnZjibqRk1a8U0ghu9WaLQNq+VNZm16IQIEi5uOeLiKlQrHPPPeHd4mxXjeAfHL57MQ0da8dBZRj/aIQ8d6DPzi1RrDjorBDPQIbYM'
        b'ND7LBU6C88+pyyrggSTCQMN9dHypE+VXx3WfactCu5tZ6Bg2YqF9bVloxDTze9x63KTsHkGPADPTl3hnEYd70cmc3QX9SaN0PJ2HTtDAkbrtcrHdPVTNxYe8pe67KKnH'
        b'Jc+z6B0XLTsVq/kkzgvFedvFOZE4HxQ3zS7OmcQJUJyvXZwLifNDcf52ca4kLgDFBdrFuZG4IBQXbBfnjuvXwJaG7HKu9jC1iWDSn8ul6WddUS5Xm5aJ1rFNbcOVhtq1'
        b'jae5fXtce1gNuI2diGsuMewskgwuukyUKI3RMfs48Qlgb1SqkzTcrlQvaSxKxdM5k5PC00gqepdLtTcK80G1iEC18CFvFlyaYSvqmE4be+q8GnjSyF3Ok0qeRgShXcK4'
        b'Med5+KxdQdWyr5JcaauPOZhmZlHmDL1NivM81UI8LPAIeIilMdUz2Ie3cRNpSOj+EIPzELf+Q7wzeCK5qtGcXIU3lqlqcRLc3g/x2duHGJOFTmOuEul6NDGrauTSMZd6'
        b'ND0qNdjrKWFGYI0C8beapjHnei2aOZT1m8ac8SkOuURh2vDj1iBHLG1NM5q1msi7xzjzly5mdhSp8AbSemdq4oNfT3a/PU+Zt9paH/YnZ4BZCAm4OifUsMwJYH6DK9mw'
        b'h9C4w3XShj0XsmHP2W7DnovdpjznrS6mDXsO46x3n3+OD+Ha9AL+FDPVlrfJ1MRUgqXv5GRfSr1MbJfFLiAXSXCSZnqiyXNNRhLQLI21eSYrDKa2lyg1diXgT9xcNLlq'
        b'zFO7UEzn4/xoGq6nyaZsWttKI2KURUvljXKN2h4uExiW3nYMBRPtGALLmtXXwJDxdTDYolkuXUZ+MQgLksrMsSbA1I5hwaQbE01EcsX0kiZERtFoktFqbZ1CJm1E9Xmi'
        b'UpgNQYy8j0qiJagI9MzATytaEElXieliDd2sRVJfncxhKRJT5etkmg0yvGZPx0llDRKtQiMkNjKyp+4L0/DKpQtMProeK33jLEvFVspi4VSlmIdmrhlb1ZbOxCY5WlR0'
        b'HLPxaC28o2qTKaYsyLSpL5cIrJi5Q8UwOGKaqeJkjWI6IyU5kc5KSZ6yGKu5IZcuxA80ecDFNciVaNQgGOlNMgkCLF4p24DXrddnitPFKfFC+6b62p3x7syhxX3rvZ3b'
        b'qDkU1Vqb+JlPOqWdhQLhGQq8CjvLwaWFUFcM9xfC/aVJsGMh3jJfVCaEnYkVIrAXHixbVAQuF1WUlxeXsyjYDQbcWypzSbHvc9yfqWQlU9TC2jJpTgmlxZsateB5eNWq'
        b'WFImeN6bFAsPwI4yxFCAjsnl7trkTtXCblJuQKDLHAlF4y3WicpZz1LkCD+4UQjPWJ/hL4ouE4viS9AbwBUulbmar4aD8AQxREBKKcnjl3mwAimKrk3Md5tjqvRJ0Mex'
        b'hq660lxnqEPldiZiAPcJl1nBBm6p3MB1eLtYXqXMZqkHUDErX9y+/2CeKzvFe07jX35avTHba7jcWxPiU1mb5eT9/uWbvyjNFaYe8qqjd2W5/Ln7/iP+3o8b4zq7XNyE'
        b'9PfzvJUz35c9UwW+9/Fftz67wid/8ecXYw/VvfKnDz45t8rrw7PqT9+7W9t854vZs/78578nPv9B7HN+ytvr9TuvfHr7v/b84Oqfrt5sGQPlee7/nP7q+vX8z0LOrvjD'
        b'oT+f3etZt0Pw1l+dYHla6EKZ0J05JXoevpwAOpOsjoF6RXOKwd4GeBaefkTjBnkdnIsHnZXWHc7y3UAFw53ctlhwgpzsX1EIL7rhZu9JEJabjiFQfqCd6yyGF8kRA9AN'
        b'bmlQMeg1O0GvVSezKP8Irhu4kvYI7wVW1GQniOKKRGyKD46BLnCTLYJnxaQEeBG8DI+hIiY6FV6G56hp4ArqMHAV9jElVMPLCWIh3JuIz6VeghdXsNNSakhVwPBM0A86'
        b'se0ASz/yV0ZT09ZzwGv+YPgRJs/TGgF+iZmzxTBiNBC7IDSgqGS4my+e3/oI72BeCq4/h2vUmRgvBh2u8AgqeD88mIDT0Wqex3TwPGlkeGdeCU5H9MzorSI+6FyIwD7K'
        b'gbspb1IU6PIAfVZvxfx0qdO0OCoYjHARxCfBQaHrtzi6jpmHycfWyQlTHzMttj0362GyW7DeiYrAp5o8jJGiLq7BmzYK/LvSutRd6t7c7ud6ntMLYg2C2KGIe4KEUUHC'
        b'h8FRo9FF+uBiQ3DxqG+xcUYCyuo1kSWne2vPVr0gxiCIGfK5ZzpIhbIs0AcXGYKLRn2LjBHCc2Gnw/QRKYaIFJTZk8mssWSzflOWPjjbEJw96pttnBE/IB6qux+RdS8i'
        b'Sx+RY4jIcZTZ+p2F+uAFhuAFo74LHsRm4KpFGaOS8G+EMSKSZI6MJjW2O8rlwWxbx3vnVXjnuWoddvCJLJUaOxh5VBrqcTvbsYmJWtPHaoP7FD3yEGcZopgTX1+ajn1V'
        b'OrFY9Sy8pf27c79T4wJnXHKoW575ThyboyUsM+2ZRmjPs9QaSxRi+BuErAoha8ytZoLNQ3Iubm4i59Kkmb5ynqmQNNdJJbOt2soc5IPSkddvo3qXGEJF2yjSc1+ZSLCp'
        b'XDO7FodIu1TUolRsEp5njXGkLfXfANhGBljXGgszaA+rqt22S81g+qIk5EApBrO/xgxlOAMlU6ADIL8BdE0MdF41tmzik4MYYNuSKWYYhY/lM/81aF1qzMzck8MZbNOU'
        b'z5jBDJorUcssvOG3BKvRDJaZO3xysEJRElUPTkDAiZySq/xWgJkGinONidt8crho3K2W5nra3FyRU3Kr3wq+XQx87jVWbOyTwxiJu3QC9cQW1PsaPngKUC3nxjYi5wjb'
        b'dJzNbJ7gP3OYzc502RSH2Z5LgpQar5q3/u0DbG8AHx5lTlqbD7INXN9nlF3clp35g97taRyq+IDztOFYIZuwX89tnGvDYCQu5Jv4C3CGJgxGeQkYsuMvwGtwu4nDAK9V'
        b'TmkowKkGTyI1NW3eViSKhBCeAR+TxZSpxIUKDEHUPr1/tj4g3hAQP1Q1VDXsa0jJ14vmGkRz9QFzR73n2lkEcEQtGYMAmEIy+DKI8cXu7TEYpddSpjNgxS7/ieNfZMbp'
        b'cYmnLnhmc4SuY06meZA548VXa1QymWbMubVFrcHC6Bi3Xq7ZNObEpNk0xl8vIboit3okErc0MzokjkbSOMZrQbODqt7NClU8zaiCq3+E69jMI8JpD9PBa2edl46tc8U4'
        b'rvPWcXQuOqcGT4LrbgjXPSfhujvBdTc7XHe3w2e3re4mXHcYZ43rn3/Ic6AHypdK1UjQx9KqVFaHZz/0rTdtR6ZlZOPHE6iCiKKCaBkkdJO2UWalfEHtrZbXKbCxTHyW'
        b'DutR1DKNmK5Ek4JdOXgabsYL0fLm1hYV1hmZs9VLlHSdDGelpXKVrF6j2ETXbcIZ7AqRrJfIFRL8SiK3483sajGuqRwvKaCpyVSkSfeBy7QrAxWtVcuVjQQiSzF0PEGF'
        b'+CdokUJTbZuwItQedrv0cRqJqhG9Q2qe63F+Gi+SqLEeQb1Oi1u3TiWpXyvTqIW5T66eY0ZBLp1vwxbQq8i2kKenyobfnEuTA2WrvvZY2ZSlMIMul64iv/Qq0ybnKdOb'
        b'B2cujZd4UFcRtdEq603OU+bFwzmXLkAuvapSpZk6HTPgUVLGQ96RSBdXVYrSUjIz6VV4WWfK3MwskUsvy18iKp5HrzLtlXg6YZX1obmpXz4xuWDlGPNA44Ksj2pMmR1N'
        b'R6gxm9DQQMNVXa+St2pMHALGU2zNiIytfIW6BeGvTOpQr4fQCafGpFpBTNiSzhbT8xjlHhmiM6o0kuZmfBReOWNKNR8ZDAixEACtpqEllRMjuhLUrBvkiCWQbUQ9bhpw'
        b'9uXgT0WLRsYMEzL4ZZqmFimaSRq1zQjRECyStWgAokEjQ61TL6NbEHvlsBymSnjQEK2lmqmmXG0FkpguRJOaeUJyWIr1sMM6ToTq2ERwvQJVmLEOrJY5zllrMhDcUk8g'
        b'Z1aRZzZpNK3q3KSkDRs2MCYKxVJZklSpkG1saU5ihIokSWtrkhx1/kZxk6ZZEZlkLiIpJTk5LTU1JWleSnZySnp6cnp2WnpKckZWWs7s2ppvoVGcVqGl0RO8BnfCY+oy'
        b'YYlIXJFYDF7OxcqU84kUFVXFa+JKif1OcBDuhUfSKCqyjEqhUlrZRC/X08ijnCnnp6g5tWUlvBWUFhtjAS8sBldLzfzLIqjDZihLRIuxDQ4J3L44DhuvWA51+KfUiQKH'
        b'wFUXeAQcfEaLD0XPnw1fgDdm8+EBop9xoniwj+2+tU2LhXbYNxNbvxDD/aXF2MwHKhmbuGQXAB0VDl7kwts+4JQWm/YrChPDG6VwX/lS2NXKVA2chDp8nB/XbSHUVaC8'
        b'+0qXtiKnsqwEHuFScC/Y4QYH4R14W0usn+1Shbo5wwtiYQm4A066Ui4lbHgS7q8jsTVwB7gAbxSj/CyKUwV2gqMssC0WDJNG9QF3XN2gLkkMO9ArE8H5ErgP6lhuPhS9'
        b'gMdt8tL6YuYJ3gG74Y2keBa4jGh8ESsTMdi4XW/QfMqd+sNTbLo28eHCRmYj5HrYLQPH4C21BzwCX2be67yavWAW2K7F7Bk8C16AL+FYDw8x7IYvl8FrCfAQB/QkUAGb'
        b'OOBS3jQtVnLlgjdC3MQoP2q6YtTfF5bA/RzKD97ieoFrXPnf/jZCqQFKp30jtHm01BXMcec/kIZteeruiRe+t2rj7jn5WYtXH/Hf+2CGk/crT2t/E12+IPfXo9ufb/mq'
        b'MnXwp5/wXFese/dvQT/PSNj2SvUGzqM5I188bCoW1RyoO7//t8IVP43L+EPe3//X4CtZDyt+GXBj5MMPL7W4SVdsWLRi84Kfq44/rfxNkW9O9Gnjed/oimU9ubLTP/qB'
        b'TnXu9qzW8jnfK/jfDd0v/f3sEm9u8W8PZa78ZO8Sr7i0P2Qcd1dcCjv+4Kfl6/+6OjmC/abLvd9x+nYmux0eF/KJqdI22LMZa05hu8xGedoAjzo9IvrobngV3C6drEgk'
        b'asQE2C1K48GD8EwjKSw+FfRi/alJeQo7w836U3/qUTgu7Cy8ybPi8eGdrWUiM5OvjWWMp3aAnTMSKkTFxeWliXB/ZbWQRfnDO9xUcG0TUY3GxMDdpayCxLgiBAfqZnCR'
        b'valYIPT+V8ymOlQ7YsfGYKbFLIWrRCqtYTi+NoGFoZ8ItNFClrlSwXSv/wBvQDO4RR+UYQjK6OIbBUG9SQas0Es1ilO6Cnuf0vsmTOgas7qf7XlWL4gyCKIGNIbY3JFF'
        b'+tjZ9wSzRwWzif6v4G6jPrpcH1xhCK4Y9a0wzhB28bs2dHsZhenIs1XvHWOcPbeLPxqQq/fOM0bFo8BNeqwcjEO+9d2eRmGKOR0dhXzabg8EETaMkW2MEw+phllDqkvY'
        b'0GqO3jfaKEobzh+eOzz3UjUKma33jTf6B436C3tXd3GM3r49nve9hfe8hUORQyq9d6rBO/W+d84975yRGL13vsE7f9T8tRKafBihCTPizC7rc9jBWkLVeexgw94qzKKr'
        b'LmHnMnauTCFmWfUY7pzaiQ89YZZHNYKR3VFfCbH8BSkr/aRJReny3aso/+2qSyx4XXDJp6g3Kc98T47QZcxdirfEmzjbMQ9GXjE/8iXN5Bcbd5SNuZj2ItXLxtwwd4l4'
        b'erxTmekHSxfUW3ZuoI+3mXTinjzi5Ei4O0qMeSNBDi/us4g1dhedDxL0sLV2YrO/wZuId64OxDs3It652ol3bnYinOtWN5N45zDORrw76PR48U5i2YREMwZxn0CImY8P'
        b'HTKpacRJIfxC8gniDiXWtyFgDjKRblS1aFtRLBKcJPacSUtznVwpMfOq8YiNjSdMFsNjYd2b5ZQFBtCiRbIrCWuV/r88+v+yPGo9dHNxRzEhFq3118ilNmOdyc8EmQtw'
        b'yJyv+prTD1O+jplLmPeYpg9TGCPfKFuw8lNFJBilY7lkQwsWIOTNEsUUEtCqx5z/QHKl4xMgU0KMZz0G3rqWlrUYXhwipstN2CUhz3RL3RrU8XSLY2EKIQiSh7Mzk1NM'
        b'SmeMCEiYx8WtmjgbMiUQlkk3l16q1koUCjIyEOKsb5HXW0bjKqujJY9VCZgmbdtuIAfeV1kfP/laoR1nnyS42xxy+B8gd8+VbZA1mrao/n/Z+3+A7J2WmZyanZ2clpae'
        b'lpGWmZmR4lD2xp/HC+R8BwI5zWzx8dnCrSjHbMecWvfCVCdKm4bFio7miNLicrg3sZiRU/aBESxeY6l6skj9HHjNJT2MT+64ca+B/fAGOOtnK1DDM/7aLMxOlsPXS8Ul'
        b'5UhUMZW7H56H5x2XCzphpws4txle1OZjkHTS5erK8kqTwU1c+nLYhVIfhDokWLsiQRSViJ5vVa0G/eAYOCMHZ10ocBE+71YBdPANcsdOCtzNU5fA/cXllaXYVKeHezKX'
        b'CpzLgftiZ2qxQBWiLlPHl8MDcVgkExeDy3HgjVgWFd7I48FTYIjcwwMPgiE45AZfAQcWO8P9ogokccNTm9nUtDQOOAVOwxtk45FfGDwLb1jtO0LybzHK+/JifHdICujk'
        b'bQT7wfOMWuRleBNcMUFWnChEtbwFh3iULzzDga8Gridd9evN7LlJLOyrLftFjYq51QQOoPa45YY6dgkllC8BPaBbm4nD+wVwnxtuKdSe3fAVf9hbVIbKh4fhy1gb0Qku'
        b'oqcyeKAIC+Srg5wXwH5whahf4M0i0ANvIF8xtWx9sVc8Cc2H+5UYN1KoxSUp4AboIq/fCtrBQdNdK+BgWpIb6FZ8+c9//lPZyqU+YhG0SpxWLGV2Vv28lK/aRzE7q36+'
        b'pInSFqDAQthRhFtoP1mAugNeXgR1RYnL8FVMSSVLEVIUwX1VcUKEGkXmu5f2CcFN0oh8pcfTcEcNc43LSVfQNRceq4JH0ko4FAteouCl54LJ7i1wBRwBPW6mvlpswRv4'
        b'6uylzhNtZGkgcAUe4lKgfanLyhYFMY+MQi9ETihDFsXBI8+CU1XONsoP6ik/vmc06CdYAi7MA6fVJaLK8iSMSxVgv6gYa4Q4lBD28sBLHA6j9zmzZlUCY7ZOyKfcPPPB'
        b'G2yMNUHkwqD3oyvZb/GpjbV16wTvB64ouMzsRgPds6fDGyZVF96Dtg6gfkRYBjuSKssXxZnKs96MBk+Ac+6wywee1GJpTwOP5yagwdchLk6MZ1F8cJCd5Ldci6XBzaAd'
        b'Xkejo5RXw6LYKlY2OAN2CjkkWzUYgBcTCmirXKDvaYIJlbCrCedSgstMthYp0SSpwGvhVhUEB8EAU8WdtNz14R2ueguSFw2/+eHlxaUVMNn786yOn9Uc8y8RKrIL31tF'
        b'K5PZhhLn3Xvn/1Zh7JtVB09fVI5ECc5V/KZ2/YqSRw1//90Xb4f/IlbyVlFa8m8y1v3+rvPfGn4Sn1AYfszzjQ8GnfZmvfTRJv+GpuTR0H9knQbzXz9Svob9o8FXh0L+'
        b'u7D8gsu436/PVv/F671dxTvem3Yp5uKamALflelzfa9+8sEH6/RHp7/6SZBMVXP8dPs/Ti3a+o8NMsMPwacFv+jIvVPb6Jpw9mZnYNvx2yXcLY884/98eNcpmNn4x0Yk'
        b'aGYn/2Vl9O6yny1fnJjwcsaHP6xd8rsFb2785Qda5V8GvhKUF6QpnWI9f36wds2vfzXzV6Dvp5fifzb3mLD69z9f/OlIX8epI9luG4amz74QlwGPHqr+3cd94FLo5V/M'
        b'Srr1u8CjueGfqO/fzHjqxzWuF/u3dT6V0ddyyf97TXlr5aog48i27wk739/0v17Je+Palxe+d/6951/+lSr12ROfbL/7eUDSbv+tv/KDf9b+Knb7mby0heyPnx/6fvgd'
        b'162Pun8p9CCrxSUpsNey529XwYTmCs1SFx9hq7Co869W22quwK0Qi/KKaK6uryWFLUPBVpqrpBx4x6S5glfWEkvd/oiqlDJ79uBLsIdsxvRaxlFsBANEK5Wa65MQTzbs'
        b'ZYP9FOWykg1enBZJrKmmwusLEfKDA2JMLRIxIh5gi8p4j7CeMwkbWi0tiy+D3XyK/TQrC+4vYEwRHw+B2+AVeARcLCtPZFPcUha4HgJuETureaA7HHaGwB7LVj3+s+xY'
        b'eDbhETboO5dKmtjRZ9nOB96AOmZLHzgE+pnNiIcWgHOTFtRbwCFEzpj19BYfZn/lK888Da4Eq/HwFGG6R9raB3ZxwHBJIDEKC4fK6FJGJeecaVLKgXOU0O+71spNra7D'
        b'kwHhJbZtc6Sz88QqnwnJvi3ARhc0EUF0dzfZjO5uqxsVHNUbPDB/KP3SLH1QjiEoB+vuzGq6mfqAOENAnF4gNAiEQ/MMiU/djdAnFtwTFIwKCoiiLv9umT56oT54kSF4'
        b'0ajvIuMMsUlRZyljlj5AaAgQ6gXxBkH80BKDaM7dFL1o3j3BvFHBPFLG3LtP66MX64OrDMFVo75VxpnFWLOXrffOMcZhNd4WvXe0leIvNmFwC/I/q/eOMgpCu3J7pQMF'
        b'ekGcQRCHzUwnGUPiemcN+epDxIYQMTEqjYPns5hNiSOR6E96S3hHqI+2uq8oNsFSYlBv/qHcrlxjVm5X4WhImt43fdQ3/cHEkzGU7q0a8O9b1b/qfmjSvdCkYY4+NN0Q'
        b'mt7liirdGz8qiELfIQH6q74vmnVPNGukntlacTfVICrUCxcYhAveibgnLB0VlhKgyt5p00ev1AdXG4KrR32rP8zOG1kwsuBu4TvL3qzUz1ximLlEn73UkL0Ut0q63juD'
        b'aDJZPjONGXkYqBS9b+qDiOjBoC5PoyCgJ3eAa6BT7glSRgUpxui0YYk+OqurwhgQjO1qh4mHuS+5jMwe9S/p4mBwowzB8YzRfGPYDEOYeEhtCEvrWoCSYy3tQI4hRKQP'
        b'EBsCxMPR9wKyRgOyPgyLHY0r04eVG8LKRwPLHwSE9DYONKKc94jZbmNCUq/TgJM+MG40MM4YFDrgNMQb9LwXJB4NEhuFIhTH6/P88kFc4vCSu3WjYcXoi96WmNY1z+Ab'
        b'NVCl9xUavQN6XQzeM0xK1xi9d4rBO2XU/LVSsgoYJest7NzGzqvYwefqVK9h53XKrGR9Qv3q5BGHXzVZ22pRuP4UOVMOsmqsdP0JZaN0RcNtnSuLJSc60f+s+53qXy+6'
        b'5LOoN1me+V6cerPhDfyxXHx4iLLVlR6ldE46Fx2XXH3I1rmTe6Y8dCzTBYg8NtUx6aDTFj7Ri/Ls9KJ8O90nbyvfpBd1GDe1vXJHQpgnI4S1L+RQ3EQvDubsQzbGU0tI'
        b'6FvruZRz+g9ZmIc2NARShDuLgYPgphrsh9fXO6/jUBxPVnZALXOX6QtgG9xWBfYvgfuXli+CLy+ELy/1yExOpqhQ8HJFAAdsb4F7iBgEdzfDPVVw/5IMuG9GMtybjqQg'
        b'53UsOOAGzzEJRsB2eA1eaTUXx6J48SxwDL4GjzJix2vgylZy3SF8FZydSc30YRPwQHeWCJ6BL7IpuAccp2KowEZwhKy1gle9wOHiZaXi5PTUDDbF38oCL4AjsJ+8rwwM'
        b'IjmwRGS6H7AVvmC6InA/eFEe9fdOnhpvVNxX8OMTVa9WvJXsvfr9a3+9M/PdhK4HNV+yhx4um+c6ragn9r85ifrV606XH/nd1kOz6NezjULdS9ffzruR96nx3F8Eisy5'
        b'fzge9xPPoAe1pasi3n911vGK/uxn3/7ziWb+73z3df0w6MAHuvvL4KH8ph9QkemvfE7/7rWjJ28vTvNt//XpP7AOR0ZWpKqdN13hB/14qCnmtYamn8yFvbt/wv3tvD/9'
        b'VMkODw26suPZ33W+8PnCL7cslN/s/6Iv3PCrC2/FXS3qfOV4588zfQ4+vLng3E//ee6VD1858+7Fon/+foPslxd0tzpPVsaF3Y2aFXj+tyva/979xYmKmzNTdfKUkOOj'
        b'//hk2ZuZL310+1Pxzdvt51adyey/Wd18/8sROPOPxVf/NGbkxcYPP6r5KPLj/x1w78vm2D1ewmnMfQxXweEqcpuoE8VuLAanWUvBRXCWMUS/H96JQQwQvA7OW5ggF3iE'
        b'ZPSYHeQSgDLasEAH5pPzD3A3vAq6zVxQbL0VH8TwQPAa6GPWG48F1BI+Eu6EvTZLoI0x5NaJ+oC5pRWJxevBK+XwYBK4wKU8weucGvi8N8P5vLRyKewshVdWktsguWEs'
        b'JFJfkpGsiumzrO8mA7cj3fHdZLfBTcJ1BuGq46sk4eFo69skW8CLcDsBDhyMlpXiMytJAsupFcofXOaGrFaRIgTgQnCpzXEjFjWtpGANB1ziVhAeTxuQZ7d6+6z/BAs8'
        b'jWGn4SEKyZmdzJmSA2tNx0oorzDOM97zCCwBcBvYgVlg8CrPfBwJc8CIs32V6ayrqe5wT3qpzcpsJDzG3N3xEmrxm/jSy1h/07WX+NJLeG4mYWijwXGwZ/OSUtuLPcDx'
        b'TFJyMuheqNmAxTV4oJLct9bFboG9ycJp/0Z+Em8NNmmn7JhJpxrmwkTr7ZxMCGEf3zOxjys8qIDwo4pDim5ljxIzFJgdaxyQ9K8ZitcLMgyCDHxfZbgxhO7PRazY9Ij+'
        b'0q75xuCwroKuggchYf3ZODC8v9gUaBQE9qYbQhLvCRJHBYnGkPCBiD6UZJxNB08z+gaPc9DvA9/AnvJxHvKN8ym/6b35PSUG39hxJxzgbAroqRx3wc+ulgQx4244wJ3y'
        b'C+wq6OWcdD/mPhqdqQ/MMgRm6X2zDb7Z4x44gSflFzTuhX3e2OeDfdOwT4B9vtjnh33+yIfeEoD9gdhfMR6E/cHMC1wHpJhbnjUaPVsfOFvv+5TB96nxEJxgOkqM4Q3F'
        b'D2Eo9ahvTm9Bb8EAj9yxuVFPZxvobP30HMP0nPFwnIgmibJIIs4599PuQyuYizj107MM07PGI3CiGSjReCT2RWFoysejsT8GQ1Pcmz8ei5/izE9C/BRvfkrAT4nkJcLe'
        b'ef3l4yIcIMZVTcK+ZOxLwb5U7EvDvnTsy8C+TOzLwr5s7MvBvlzsy8O+mdg3C/tmY99T2Echp4s/PpdFBYV08R54+x11P+Te+3Tv00OZ+tBUQ2iq3jvN4J026p1mjqs6'
        b'ueLYioHGIcngGkNMlj402xCKhQODd86od86DsGjMDIuJ01Vo9A06WnaobECA/padChkM0fuKDL6iUfI1BoQe3Xxo80AGI5LcD0i+F5A8HDiSow+YbwiYP+o934q79GS4'
        b'y8tkODALn+oxnlojUWnGOGgofDNW0tPMSk7iIvHN8PaD7DJmH/st7CO+dsaDxUrEzNy/7nxnm6yxRuyUSxb1imc+j/M/bk9/o5D91W/t9PCMAQ+N+ai7aT1TYVpmUMk0'
        b'WpWSxDXTErxcbrVq8URLzfRa2SY1KqdVJVPjU0LMcohpfUdtWeM2rY04WiKevPytYBaVMDh1mxDgX7PZz9khW6tNwCTqAOyGfaATPg8Ogg5Emw6BjtXg+nJwHVwDFxcB'
        b'HY8KBNs4m2XgFrlB2xMeEcPDiMUX441Nx8RbWEQ5Dl6FB59DLK/zOtAZDl9YLoLPl4rFHMoXdHDA+c1awix3KNlhz7AZ5XhJ2gyKKFcTVoDbpoxOFBecaQQvssBRETg3'
        b'xqoh+kywM7oywaTMdEf86EF20nPwDZL3afi6E+F+b8KXrDjg5SlMRh14A+zFBDRtBqPuhOfgNRIFb7Ezq5gc7DrQDvazpvuDl0hUEDiPKnOYQM/xhl35rM2b4UF5wJ9u'
        b'ctVYoHwQAY50z8LHgwsbU/+27nPuM/NFr22/vH7n9WVj735MudXF+s8Y7ErfXHwDNOSzr3MKDrn8+TfdH7zHWTM+OhL5yM/b1a/qlb+9tOfDuovUzLb3jAMl3MiEN4s6'
        b'zmz9XUfxH+peffo37CPZ+YtSom/mLJ3TdOTnn6Zu+qT7hXNXz/1XYfqnm17/7J2GfX8T/OLktb2SrChulTQ2ZdPL2a0dF/6x+Gc1exuTPi3WPnU4lPvFip29Wb9MfuMH'
        b'K2s5733E2XYkecZzm4R8cpR2Djwmsz3TSk2De1yYMye3wA7CucDbqK2OILbIdN0RfKMI33jUDoYZ/u91sB3cTBCXg7P+bIoNhlil4CQ4xVzvdxycT0LMJWaXikVsyk22'
        b'FfSw4QDY5U7eL5uVY9K+yYsmDrSYj8seYzSP4E4UPDv5wvEg8EpLzAqh8xNzM84WbsbCw0jUNXj4Wk2vphDCw/iZtq8t9iKECHET0cLBivtR2feisvVRuYaoXHz9dT6L'
        b'cbvLEFkPMIZHnFx/bP1oTOYIZ6RKH55vCM/vKjKGJyLCHZ6FfDHx5xSnFcNpI076mDmGmDld83vjuiu7Kknphqj0+1G596Jy9VEzDVEzMWtUwGJcU/HBob2S/hjCHQUG'
        b'n+Qf44+GJw0Lhuv1gbmGwNxR8jUGhg84GQLj7gem3AtMGY7TB+YZAvNGA/NwBK/f835g0r3ApGE+w9yMku+4E5f278IGhGLTBqSDCMDRmLnoOxLL/JrBfBAwvcv9W539'
        b'+astHTM19Mc2Z3/me/1Hrn56Eb3vPGuM2yrRNNlch2iR+HdgqsQzXYeIDd046ZzJlbh8y5WIk5QJ/4YrERF9+ojDcrBRa4JEYWqhlqzHPoXCmlg9uUUW3Ai5dHEDHY99'
        b'8TRiL9TMlgBMhmQbse0svEIeL26Tt8YnkheZ6KHK8QK7Gl9OILUs60tU9U3y9TIxXYl3IWyQq2UWmkfKIBUgySV0Q4sCMTdfQ8CcHBAw5wrGdsTZ2SUJRWgiW1iEhLeS'
        b'8jJwfkkRuLwpFOoSxUimKoJ7nFpXKgmxg6eTPUrRrFdSLoYdSXijsw5JmYuKwOFsNM3FYUOypfCmE3g+fhpDJi5FRspi4WFwkdgk4ChYYEfyMrLUqgJX4cUEBJcEDm2k'
        b'NgbEkwxpcBc8gcjpGwmVbIq1GMnZ4DB4TT76VSJHjUfDyqxNJxbleYJk95cPP1rwt7Ky4Td5gSOsrNptJcOyOe7u27gFt4fn182/1Hf740OBg/4vzluz+4z7zZNP/flv'
        b'PrPzv7857sf0xrJY3veaj+R5/uTNrAT9j3+ZHT768J1V2v5PjLqnGm6c/EWoYNv3Xb+6+RfVJ2tBQ3/Hs4E/WJsnCvrDwtjFfxigX7/56/4zbEHWT1feXf+SZFdjzvKm'
        b'aTW76/YG7Lp2aR/9wfd3/Sn9iwVdw5qkE19d+GTNyT2ao8qQqLlrz148JDzvn5P3+d8P+6o3/fDu57/vcosu+9Xyyxu3VP5tkzba6yG3oXVawPrfBq32jjgTJ7yzNeHo'
        b'H5/x/1XR+5sOC72Ym8PvQMRbwFvgRdJZiB3MYoErcMds5gq9a7PBG9hIBex8SgP3kWsoO9lbwtVkBzW8EgL2wRvwpQ1kh/URcDSJTbmAc2xwBtwEg4QiuaWD10kBiKZt'
        b'm8um+BXs6avhNUbMvwhuzUdSeEeiuBh2zAE3ExFVgsNseOcZcJOQm5np+aWJ4EAlIodgB9whZlFuc9iwFxwCtxnoz4DbW3EJSZUieBXsxLoxdvxa8AJDLM81ijCbIWTP'
        b'FMODpHZeyZxGcJxRloBz8KjSREqd4A7m8sCmpYyuo98dnktIQuilBPuKRWIhG1G6kxywWwtvM/qFI4vqiK4jqQLcgH08ij+THQCubCAvZsMjslJwGWE6fBm+gLHdxZcN'
        b'TqnhGebW6kF4EbV7J9yPm2UBeAGBPZcdCM6CsyT7gufgaxtgP9ZPWGsnLoNjzGLcNnC+mMBW/BQ8h94MhtiJoHeh0O3bahfcKJvVKoYkc/Fk0OZhIRP4kRDj6yZiXOJN'
        b'+fr3ZB2dfWj2QBRjvgILdjkfBkeMzrCyKCHwQ4lmHZo14MsYjyCJhlKv5l7IHZbqE/IMCXkO8wVOx6J/n2e/ZxfPKAg4mnsot3tmz8z7grh7grghf70g2SBIHqdcfRKM'
        b'wRG9sQNRQ5yh1frgXENwbleBMSbh3NrTa081Dzajwv1SiNPn2svtlRoDQ3DBA0uG0vWByYbA5FHyNfoGHC0+VNxd2lPaRf4ehIT2Z52cfWz2UJQ+JMkQkoTLiDUiYu98'
        b'zHnAFwPW62nzHrZfAnFM7wmN6F0yMGMw9lzi6cQhzfAS/Yxcw4zckXn60HxDaD4qLSjh7mLj9LCTRceKBpb0VfRX9FaMc1AoiSLOZ9h5RNmEOXKQ4OkweJxjhomokL4X'
        b'5V/I573N5xa6urztwUIuwzu4MLzD51MwEJPxBQuTFumY4SmcWfgyVhtk+SdmKLZR5stYN3s92WWs/6b7xvtckqirnrM4QpMtO3zdpZWBOES2TB8hj/lho3/BJCvs+OC2'
        b'tKW+poYYGBlzblW1tMpUmk1PYsIEHzkmO//JahRRJhBOjDSd0Pc/siyNF/knr0hP9KEUOW0WK4G/wRnKODY2L8e5bA9vhE7IcaY8/XTLBzhD6rt5oytXG8MihnJG5z6D'
        b'8NezloXQFrmPiPtgfqFx0eJxTiS++vJxzme8iUzjXBxawqKCZ/QGGr1Fo94io2/mOI8dnP0ZhZxH2NGVIFY9KKLX2eiN70M1+magBEFZKEFQ1iPs6IpRgrCY3hVGshxp'
        b'9H0KJQjLR+Bh9xFxdRUoTSDdtdHonTDqnWD0TUJpAlNQksCUR9gh9j2tE+TgBHk4QR5OkEcSBIR3NRm940e945kEAThBAE4QkKdbgBKERPbGGb3Fo95iBowQAkYIAQO5'
        b'utJxZ5YHFjEe6/JJq/dWDaiH0+4K3kkzhtJDgpHIu2nvSHHLLyEtv4Q04hLWg0VLjStWj3NEHnNR/id1cTeYSxjnkvBnWExnRw5X3Y1+x+luuDEkrFfTGz/MQTBUjS5b'
        b'OSqR4dc3ktc3ksyNGNgafKqEU8nySB2nvr2LIbIUyiXhdewMj0IE8L/sKllBHqHj1FROJtPekaMeYXqPMINH2Djb3wNNqF/rfMahPMPt009cl4DE8b3gVXVxonJpsUjt'
        b'6cmhPELZ8BR8A2wnp/+qk2a5gSENXgVxK46VlMMDC/G2vemp3EhwY4Hjq+PJJdMsy9XxZh3ef+ba+Ce6ZNqpQuuFpxr3pfgy3YgUcJ2KCPUhmxDXIr7mLLwgKhWD4eQM'
        b'lB3eZK17JpZsjl0BbsPT5jVOcSOPMi1xHsok0bB7pQp2rgDHivE5vn1pXMoZdLJLcuBNef7mFJb6aZTG0MPBVkBOHV5XcZbFyRx21y2Hm57eJ9znFnjtPOeTxhmXngta'
        b'+Oc1I/8QFw6IGxS3F/cu7j3K+vGqH+86/TzvYrW/e1XQ3pHcoKrA3KDqvqigrnLnhgc/oqiyf/j9osEo5BF2tAoMgf1VWAFjMZbGToPH4AESu05awbB0YB9iZs1snQBe'
        b'YhjKHeBSeBS8nWCzMSuslVmw2gnOg77S6OdsV51k8CDhZCPgsaBSeCwJb/IkkU+zZeBowpTmR9xbVTIkcspq8O77NpsnwuFhAzSYZM/xoXwDzXyXbt4Dgf/R7EPZvfNO'
        b'lhwr6SvrL2P2GunmYe4s71Be74YhF70g1SBInQjayOz2QQFefngOizYGhPQu6F3Wu6BnSxcXpdKVWuswxrgYiDE+Y2JpEi/C6DEw38HQKwHmOWygj0DgqxWUmeV4zpvF'
        b'CsashEPnO72/2gbzvU2/f32A7TO7WdlnTsWGRdCwZO9ywZaaZVwpZxdFLDTbWi/mkTg+inOyi+OTOGcU52IX50TiXFGcm12cM4ljrDpPjnMhcZ4ozssuzhXB7IRg9t7l'
        b'XO0mTdOxGljSaQh+d1O4AFtYlqaTcD8U7on9Or7ORefawJX6oxAvaQYK4aK0gdimcY9rD7uH08Dp4fbw8J/Ut4GNwvAvx/LLhDIul0lh5XIn+6VB/V5yShrcwzvMkob0'
        b'uCJ3urks5A9l0iJfmMUXbvHR0gjkzrA8R1p8URZftMUXY/HFWnxxFp/Q4ou3+BLMPus6SBP72S+ypKJ+NrbsLJsm85GKgywoNCCgHHxsJ2BbO9CmMpL+lTIINL4m48eM'
        b'ARzXBidpMuphP2LF2on0Kk+agkL8pb7EsFfmmEsNYholhXKFjJgCtdlpZFHk6ShmeclqpxE2s8xF76B0bJM6D+8vcvq37y9qnEyqOJQ9qXJl9hd5yLHphNZnnebUKlwl'
        b'bsxu/O/l7KMCWU11TgtrKwpKW5nAc4ufZX3JbhLzkiV570m1lDYZBW5thS/aWFC1sReFxPtOJwpegT1Vjc7e8Ai4RErq95xBzaPeieJRtTOeC+dSvzfDSaZK+Yo1Mo4a'
        b'60Uzh350/N1MRNOuHY5+gcXvDczty1t5lLFu1cH6bdCij4MW/vZVRLEWB9548491YfRx4XHeW+JpvOt9N/reVPxj2rKRaHdh4lBMesr6HQrJnvff6QFdYOzdKJf7rB7Z'
        b'9k/5n61YtFHRGhbSdenE9z1/f+3czme/v31hyI/u9nlSPzwz/fScPKELo0oZhD3PgM7K4sRN8HixiEM5L2FrRD6EsHnAi/AW6ARXyc5hfiybBwZ84EEhcwh/KAwOTGx2'
        b'PtUyYeYU7gc7iKGthMYtk7YFZyJayDRddBCvaQXofhSB0vnDQ6sZU6QJcSKcDPSDk6U4VcB07swY0MdsM76yAFFTDGox2E/24ezD24ePR4AzHHAKdoDTBDBeK3xlIlU5'
        b'uEShREeaGjjgDLgN3mCUROc8wWnQmQQ7kuD25cVwH4tyhnvZYBe83viInHwYgWc8QecGVAph5FBZ4GAlYgE6KuEBcBUOiPlUTikfPI9YmWNC/tcIbxg37ayOTrMMPVuz'
        b'o9heHiaBq32o8Kgubo8bsxXWt29l/0r06DruStGRveqBmfrwZEN4cpe7URA+EHFPEDkqiBxyH1bdi8sZjcsZUbxTf2/2otHZi8jm1zx98ExD8MxR35nG6BRs0nOGcUbC'
        b'UMHQ4qGCQTExUBoRTQx+mn7CaPLmiKgBHrZ82oX+rIg9o3QY45EzXmNcfER4zH1iW6ayZcxFrmzVasj1Ho6WNRg1hGmd/vFtkoQZg52U1SL9Kh8WKxvzAU/sfKdr8f0u'
        b'qdR1z3zqm9j0NJl25NXgpprKBqBV5c1GAPPZ1oYKq7eZbABOn7jfws7qn1jVgSfyb2ym0KPGugO/AYzz2DY2MpPMQIZZAWlvxVP8zVvPtcaCVN8AvAUIPNV+8wz8VWix'
        b'uQzz6dpvCVSD2SwmHgQ1zfIpzU86gKkEwzRhF9MfK27oBlVL87/YQmZgJBu/ATDltsD4EmDwqe1/CRR+jaZFI1F8AzgW2uD6KjMaBS3B5ZiPgE8J1P+EvTC7noQ54THM'
        b'SfR6NoE5eZl7il6uYPiQs65O+IYY7+Rlv519fEYTJd/9z48oNT7Y+CW3jJGBsRXMxYHRH/2x7qzv27X8mD0Vvn4/DAwKXJYG3ktbyvpBLf8nGmr+kTMa54LaUSHrETZI'
        b'Ca74ixEtCwXXHJIzMykD12umkjsZo5M+1rPzhM3LFIohWNJpVOD0ni0DiwwBZDkh1BgyvTeFOeOQ3m86oDKUrw/AOsFvb/rSHooqtvX6d/20/9j698N/os//QIXOExla'
        b'NSFiJJfr+gm+PoDapliRIttM9tB1VdyufyWbFMzidMvfKBhlETS8MPunE2iYGxT10R95+9xXzHGtd/1Zagx/z3tlrbPiGt//qnnOmsAdQdk/o/YWOMvKxUL2IyHK7AcH'
        b'axyyVFvAVSs0VD1FdC65cBi+ihcI40PBKZEYa1V2sNPWgK4pdSNeNeSgv7xNVlOnaKlf2xZkhSm2UQRvk0x42zqNiksc3DK81BCbdz82/15s/t3Iuxv0sZWG2ErM/PTK'
        b'9N5Ro+Rrh7VjPHKW/WvUHQVY3TE1NCtsdR/NCIHx0SPHzner+5g8hWKR4K/PUmZ57yhz/xHVwPkPYq+djOdor4Lpro6l8i9YHy/7hRO1sPa5E55LKLKjDtxc7AwucvFF'
        b'YLVUG7gDDpPgrcUhACtHNvuA16nN8CQY0OJjjmjagztsBL0Z0QhHl8RViFhUOujge8ZUkNPdX5RxqUSxPzEa8MX8RRQ5q/xpZAU7avkBD6pVInh/hctqZ4oc+i+XrDPf'
        b'm2F1YLnIPOPaXJhxCvYFtrrCY9FwG6NkJuv32xRgL+yc42KrGOXmyh+uucFT49Wov9fsOP7uTDQY9bsj/qtQVOBRkFLvlSAoiK3ygKmFaDTOcWcJ9/0ikb694vYeCYuT'
        b'2QV2XTiz4qU9Ebtzjge9Jf51kqRw8Q92XLje4SOtj1X7C1bzLkatzrhQrVBenKuq6fZ6KzH9/g1ZWv6Hbx74P9V9CUCTR9r/m4sb5AgQOcNNJOG+ReQWCJdcHlW5EiTK'
        b'JQHEqx5Vi+KB4hEUNVisUVHxLN50pt217W6b0HRlad26vXe720J1227br/3PzBsgIFi7293v+0uc5H1n3nnneOaZZ56Z5/d8ZNFYv7I+OKD45U9eksbddHizTBLX+Dmz'
        b'sLvz5Y3Lwk8f5f7B5EUT1Vnvza4bS17f+g43K/TYV8GBniE+IX+k/jgrIg+zg2eoZWn+axr9BYbkDAHYAU6Am2SX378S3Nbb5m8CR4nBqCW8DTrGIcHBnSNrzGxbMrXB'
        b'jWmmUy3TMEOZ40QWaS/CG2RBCveBtjmmM3SL0Uwm2Dbin8MVXGLD82lw2yMhLtsteA3uJXYfeK2PyAJ0p4OdIzkbUIHgNNwMtho4UZ70wQAVbIc3xOCMxzizBXAOXqZP'
        b'370YAU+IzcBLE4wPOuBmAXvSNSMejaNeEZA4tbJOVi9dbanHRMgdwsmYI54qrClnN7yvPpsErUkDjq5469ttgMfXzcN7Vu1bpQzZu751var+/LrT63rzNAHx2oD41vV9'
        b'krtlYHnf8vsuvmrBTI1LjNYlRs2LGZ2/VdZaRyGavLX2oh4W+ku6YHzZWGMf1ZvYbz9bbT8b7yyFKOrbozqiVJx+R5HaUXTf3V8dkKVxz9a6Z6udsgd4Tvd4wn6eUMPz'
        b'1/L81Tx/dKfDnL6nytPwgrS8IDUvaAAbHyjd1Vwv9NFyvVTc846nHXvmawSxWkGshhtLx2hIOGQ7Ul095mxAM2d2Sd1S+aSChcEIg9Zx6CzMoR9r3EWYMa8YZcwN1v/d'
        b'je8DxkKq2yKalVXGnmwuJ+frGCNqOaKUw+yaWc4mzJo9yfk6DmHW7MeYNecxhsx+lqNj1pPGTb13NBkMqmEWOeFVCtpjAEbNcKXWc1zh5jqicyTbSjGe5X6oCxqofMcG'
        b'0JlMkrvmzKO5OAWOQOVqrzWyklmdDHkcivJvZR1+PRhvCRG2NvCa+5b3XuvZ0b6xJCwko7vlWts1hWCLQOG25VqbLDzn1crfcA9cE75s1iGjtt81fbQmCgnGBK2itQxr'
        b'lAII4gka2MRqiEE5zp1WwQbN4DzofsLg3KA3OAmQzjj6IXfI4MTlxdSTY0NNd77H8+3n+arsemx7DTS82Vre7FbOgL0TFpddBhydFcFDLPTrgYe3MkTFwX/YnNjSX4+0'
        b'DccMJuqwSFaHT9hOlD8MKVq/MiqB5E+kb1I+GabvJkqnW8FohTYMBj7l83PBryaEGKNyjaPu0bmeKJ3ZetRtiOgbK5yNCY0b/hdp/DGBZHJxmqZm3NzTwRlv0MageHAf'
        b'5Uw5m1GypOTjtBvS19yaD78eiyj37EbBliDFxm2f/rnT5u4XkgW/eaWvx6HZTalw9H2z/7WrO6x8Xzey+Xspa3swoyDk+OkvSj+XHPn9wGvhh4O2yPzlaJY0oBYssHK3'
        b'e3uELJ7iEIkhNXqIhKZcU7L3piNfWz3yGLtNaDhPR8OLbCju9NZZhFIH7N1aVyu9VDb0nIBJ2GfAyRUbWbWnd6S3Jg/wPBVmygJVioYXouWFIEL38lXmqbzwn9o+UG0Z'
        b'qEfWJk9B1hOrYzJG5aOq1XmY0CevSQ2m9uf1qP2Zp6T2/xTx+6Ky/gUf3Rk3AkYZ6GZKf9uF8HdDHYfn/G9y+MnE8RHqJ1veCngSXM8TFcL9IaksihMLtxsyMO7zAVna'
        b'qna2HINHX2xXH349Gg2DE2QYuG051XZt8x6GhYIXPX3mggOM5EKYPHP66fnTeTmvFh3rV5we4GERMoT6qNPkbf/diH/jA1HwCLxSKM6YAXrAQRr2JN0PLcympH/OCP3r'
        b'sDyKdD4ndQOAp0c242LIGAjTjYHKcWPAVRlylqVKViX3eJ3K6M7oDdcI4zW+CVrfBLV7osY+UW2ZqEflRhOofNCgvKSsvqZuUhnFSI+8aeJehIl7ylKuxPS9To++l/8S'
        b'+v7VwAtwsQ8ZB1I9FrEswTQaKIJARhDwCAwjMWg+pmpeLl01aN5Y01BWIa0jtQgafxk8aFqGXRRIq+uldUH6F8GDRhKZnPYtgDEoBjmNJfXYC620ob6kiXg4xYf5Bs2k'
        b'TWUVJdj/Jr71IkmJzcSCBk1GfAPIJHqgwSdJinpZfaUU9Rc+YViHFZx1WME0mXfcrEGj0pLq5TjLQVP8awQWl9wmjk/I+4LrJAx8DhGjKZbWNBFw4kFObUVNtXSQVV7S'
        b'NMiRVpXIKgXMQbYMPTnIKpWVoQvD+MTE7IKs/EF2YnZucl09ZosNjAlLd9zmeJnxcCs1AgpxkCLbwNjmAs+YVLNJudF/cRH/mC7UcRKuUUYv4ndPX8v4ttSOQwWWODrM'
        b'z6DIoSJwurBMDq9Oq+NQ8HoTE77ImAG7wAGyOLaPBOfl9Y0oFl4xZVArTQzhIabFPLCboOOXEmCynWIk1KVm+qdlzoXNWeCsEO4OSJ+bKkwPgDvBRptMtAYcAVSDbc+Y'
        b'JfrDawTjAWwDp+Ahy+mwbS6FZc9MmQHBeCiBxx1DQgPZQAE2UgwfCrSBU1VErxAJd8JtIWjwScDBECoE7HYg0PNACbdboSeY6y0phi8F9q0BBwl/LLQwGDWlZ1Cwx9B0'
        b'IROeA1vALvIcvFEmR48ZrAWbKIaAAvuhyo2cO1ubBS9iiIAdmWFs1BRtFAdeYMA2tDp9gTTj9CY/Kp+7lU1ZFicUxztRJDcLcEyGcmMsAHsoxgwKHFgFNpFTanOgKkfs'
        b'L/LHwIOZIrg3EW7PYFD2oIsdB7dZkwxL3N2oOKc8FlVbvKgqpZzOUDwzBOXHAttgO8UQIma/Fh4kxZsN97L8MB7/EoDW0WSNOw3sZJVS4A7JLbDKjhI6fWdA8YvXCvhs'
        b'updhJ+gxRPkZglawhWKIKNAOzoLbxPRjDXM5WisLiQ0JWvILGeA6PJxH8np9/mxqrfChIRVYHOyX7EqDhMCzjnUhoaCHAt1wK8Xwp8ChWcvot2yBrbnY9q0hIVPEoIyD'
        b'mEAxH1wgWX1WL6b21foaolYzqV4bTpFX+8Hd4BTOi70SdlKMAAocLgGttA3kvgwz2s4vjcMXUQZgK9ODSXt4/V0GG43Er5hYQcSYt5rOCp6Kh6qQ0HAqHHaRBtsPtwEa'
        b'/8O5FJwQY68FLWmucJeYWOVZgM2sWCtwi2S40D6KquVuNUTTQHBRQzCdIRe+hMsWzkQrlJOkmgeL4QFalbUNNM+ic8waozAHsI8NuuBFsB29+zQh8rnZs1EOBubwKKmc'
        b'IgFcJKRZAU9G0883BWfRfWhRy4qEexNIed63sqY8az3RNFrsdLYmnMZiBHtT3UKCAw0soIrU74CNJ4E+sQEvlevIlWndhIj1IgPuA1csCBXZWy4OCQvEBT5HMYLRQ0vA'
        b'dRowpR3usfITYzNKBjwAmikDGXN6CjhK46ycDAY7QiICKfjcOooRiQqeBw/rsF3AcXNCfWlwOziPUSRgt1kMy9IC3KJJYJs/PIgeZYKr4DmKEY2IA14Apwk7WVc7U0w3'
        b'lgDjcsAWeMXMkmXrU0Iq/ckSY8rS8wMm6gSznRULdLR2Bh5Dgz4ilCoLILm1wztppAJO1UCBCoKxFsUcxANQDcqYjs4GpK3MwW4ueogtwqNxJiqDrzPpUwF8Dr4kFoNu'
        b'KgUqKWYNIw6eBS+RlsqEu+eiR5ir4UWKEYMIMQYeIi9CzODyOjHcmYm6awcDbrKgDGyYxiuWkEI3i9dQjzLqMVUXflIcTPdUQXAYuBQYypnlRzESKHAMKkJoNMYbcFMN'
        b'Wvym4wMVAbEseJsBDsMXwT4av9I5hdox/zILjdsZEZxiHVXfAEpwGufGAjfXU4xExO4W+JOmmQU21okRMzGAB6op5hJGAOKUO0lO3xbzqEBhNQO15NpXylfQHCAKboUH'
        b'xWlCRGrgDDjAZjPAMTfUaYSF7oQvFBHbaLgz15/yh5dBbwPWz0EluMUniHa5qeAI2A23ZYsKadMz2JwpROwHMThrQ0fYBmjmZL4I7NbhbXaADWRYGEEFE+yfsXDMB7Ld'
        b'WibFjnsfcfJiYcsyJq1MhudngS2wDc1a5h5CSggvBdFDTWGTRHNxA3B07FAQmmjYlBc4zWmAV6xpmm2WxsOWuWGBcDs7tYpiWzMWr6ilSfIS7Jglzoc72RHwGMVA/BT2'
        b'gN1NDfhETAM8D7fSqLHwdtoocCwqtlc2RzYHnKLbZ+/ycHjYFP3YYgNuU+A2uFVIG48/lyj1Q62RCXfx56eK0mnNRhCb8s7nBMPLi0h1s6McqFD2XQrRyNr3RcY0eweb'
        b'UkEnPIyk1RWe4A7i3XBjIO375BbYDdp1mcIzQDGWLZPyLuCEeAtJrTBe0kXxXJEBOAmO0ICkt+BmCT2nHwCbYXcempF3cvD8eJy5huHkmke3xkvLmOIC1BigJRo9doJC'
        b'nX0InifvBhdgcxWB5oWbgUK/NVxBCxteBRdKad580QRcgofNCbTsDXCTAjfhdtoFDyLCjaAbD3P/tCz0aJoomE05gkNsuH9FpRG4QPqqAVzjwcMslPq2M7hFgVuIWZxv'
        b'wMpqB9hsPu5hJnr4MBtsmluVvoLQyTOgdyFswRV5Dh6UUbKVswhHjYZ7ONhAMis/daTM02xYy8DB5URTwILHlxOV2OwgV8oVXqgk9U1HY/u6H+3bBpEV0U8xKCdwBdtz'
        b'H4Tb8+A+ur474F7E6A7jAXLUCNygwI1lYCc9QNvBdngYtjAxccA7y6nl6M4GwiujwEuoJfjwiEiUBrp90/HQs4ljwX3J4BJNsi+5IJZw2AwNC7ALXMagO72LyKNgaxG8'
        b'jsF7kLyyYRx6z518ugWTl8jNzZlgEzyPOnEXmpOTYCuhtmSJKcVdFM1E1JZRSaXr5o4rqFTPwRbUAJzCGqomFz5PyD8X9MKjSIBDbVYJN6diB0IiUk6+IxsNkhMLyN7L'
        b'30y9GGoWFeliEFd9v+m2nTdNwnCLCPYSzSE4Aq+uplbDDUWyZr95HPkG1BofxRSd+MOcmncDuVTx3q9aO6Kv5q3sWuN5f+b9tLYX15yvD7D/LNH07sGEoc7Aj8QbXeoF'
        b'qwWr33nN/qfXYr2uegavtet0CLROz3Z1FRzavf5vd4S1i8K/o2paPjvvE7f2w+J/zP/t9pqLfRact9d+962zp2iXyGX2h70XHlz6S+TpZ0q6f7vui983diRtYnLh8XPT'
        b'jr1R/VLX14+e+97slYU/3hHVeNeCvVngc+n9Bt/4a7uzpyWVd4nm55hV1u4dvnuNF20b6m3NCn+04pxB4SfygrU2V79+s6vDUGv2arQgnLvi9Zz3UrdnJr8n8a32flW0'
        b'vfednA7vV6u2997PaTjxXvz2mbYrDnb2HuZ+89HakDVpK465fxHBXZq6otAqc963jNwYhXyLq/urMOrTYSOBS8ErZVs/WJEbs0fukr33g1MdH8hyY15olm/9YEFuzMnm'
        b'T81fNe1qmmsV8FrpnW1nP1G9Or3Hduuadcbf/OWN12Kd8z/6n/uHIc/0zsfvnG7dzl6UOTu53yLviv/+d37o/etwS/InCdrzkhv7JS7vbdP89Pd3LjRdybK+Wxx/dt+3'
        b'SWFv3u7c4d9w/pbd3AKPhe/kP/qIJ7h9z98y12njw3l9N+apDg3a5Cc/n/w/7YwPl1///PaGE3++y/7dh1Gfng7Ytz3z7DFplM9543tbl26Uzvjys65N64TgHyUf7Vyx'
        b'RyFf/O7DzOCTz7x+6PatL+Ydt/+y9YP7w+7vtb1fOqCe8c293RYuZp8+KDkX1ZRU/kPkpbq/vOrT9W1onvacqCllu9/0pUnrtr6V9mXyJ1HpAbd/2D142vWhX+7aI8t/'
        b'V5P6pehmm3lTjeJDw/4fVDuun+j+Orvo89d9u+x+G3tHvnKZ9utk+5W/feu4bdG2080PP3bt+l1AzdLdAptHvhQxIjmNBEH6dCR4Hh6fcLIUH48EL8IDRM8hBFsb/LJE'
        b'jGi4j2KCQ4zMCHiFwMXGwTsRSNZDqxsDKiaUncRAEwB4gT6feduhALRMqzWrQ4x057RGc2MDiguOseJBS00qOEpvwR1iwWOmq5aDU8LUkY0wK3idBc5GgW20IW4L2Lhm'
        b'zJx1YSxt0KoCrWRbKwec5YKWgAC4vQScERIj4xeYiEe9AG+Qx93hVUuyi5YBbnkT3bpRJlOCePFLj8jwR4woCQ1tBrxTTjEbGfHVRbRFxZkwsHnEnCKqnDaomAXv0CdW'
        b'T8gcdGC2aHo/TLDcwAtCurht8CXrkROrKHYHPrVqhYTD27TZ8m521Nh+4kb/sSOr6+A5chIVXgJHPECLI7j22DFTFugMAptJ25aLOOglJ+HeiadMWeAFQ7iHQMdFRmNm'
        b'vRvv/oqQNIRNoXXbC/D8Er8oDppa7pTTm5K74aWoSXYhKthowdMLmt3AMdLYNbPd8RrGGd4cj/K2E/UmbfkMD4t1h1pvpegdap0Be/5tC+PxwGWsEolktfmYIgpdEh3Z'
        b'nzk6tA9bysVd6xzQE9LvHK52ju9FQVbfglaT+1x7hcEx00Om7eYd5hqut5brreJqBVG9M7SCZA03uZUxYMPFquR5jPsOHmrPlLvct6a/Pl2dl/+a0++cNJ4FGodCrUOh'
        b'mls4YOOstOu38dHY+AxweQfFe8XY7BjlrExWhWh4AVpegN4N9NfYI9MGxGn84rV+8RpegpaXMBYf3uPTPbs3gd6R0btNLJ0rNX6JWr/EvlwNL1XLS50YvYzOsi9Yw0vR'
        b'8lImRpdr/GZp/Wb11j32ThJdofGbrfWb3Wet4SVpeUkTo5dq/GK1frF9DPrpB7/s3VUavyStX1JfqYaXpuWlTVXyIA0vWctLnurdTA0vUctL/IXRMo1fnNYvrs998sxH'
        b'ot2eXO8pMpdq/GK0fjG9qGLxWl78zzw9sdV+pksmZD4scrS1e0ShYGhCEE3x3FtXK71Vdl3+PR4a+3CtfTjebl/AGBCIVFyVXCXvCek16G28adEnv8vsk2sjxfci5/ZH'
        b'zlXnFmgiC7WRhZqAedqAeWrBfIWBorHdYsDeWVG+71nsL1rSvazfPlJtH0n242M1LrO1LrPViDodXTti8VsiVYU9Kd1LeiU3q/tFGWpRxoAgoMeg20XB7rB4ukTO7ooC'
        b'ZbjKV+sRosNWTtENJSXzpOFxwwd4v96vn+enSumZezpdLYztDVELk/s8+ho1vCwtL2uA53LM5JCJcja9w6PmLek1RLEefeV3i7QpizUJS7QJSzSRS9Q8ibpUMsBzVrLQ'
        b'X4pqttZzpoYfo+XHaHgx5C26XVG7lxwuOvRma4IytEEZd1EHzNXy5g78fAJnpYGyscviHj+inx/Ra6Dhz9byUaFmj70yVusZreHP1PJnajCGz8QcMzVB6dqg9LvxIxX7'
        b'mQRjTZOoS5CuCZqjDZozyiOmeB7xmGwtL/vxSs/RBCVpg/TH6oQXiDVBqdqgVL3occ+n3+VogrK0QVnqnLkaXq6Wl/t4FlmaILE2SHx3noZXoOUVDPAchwS2ArthytbN'
        b'/hEO0C9b3iMcDJFASNlObxXvEyvDNVxBqw5fQW8/w5Tez8Ayyi8D6sOzymMofS0EiWDcrHIa72lsp0ZOYMy1fZJZ4JODX3WD47BxEHXBYvZ4G4DRnbtnKRr5iOzZYS08'
        b'1Wyo27NjTKJ9/y+cROZTj2vffWjtu7eARbEzNFipJ7xR30jRG3lEF7AdLfpPAqJ/US1woVyMYDtZtS5NBvtAGxGXkqZT0+eHNeBOza2bE4IXXXssg6lgAewguT9kG1GW'
        b'kc9jFWblybXRFDlJ96PEmLJM+pGFbma8VuRHa1++dVzL+DYFiWmBJTNdBUb0TrrUxjEkFGXKgS+A/VRZZDR9wO+EFTgSEorqMncNOEhJZxaSHKh6Q8rM9zjWMGcc959O'
        b'Z/sT24riZ6iZVG2xcL64ji7AqkR0cy3g4JvJNlw65UbKjOLFBBlQOcUZnzLkdMq4InTTrIyDbgqnMebTKbtc0Vo28iWsOcn4MdCQThm0CC9w/0huDlI59M07RahIZq+y'
        b'cZHWuy2kdDbRW0uIEqQAiai7sMaI08gA1+1AG73TADrA9ZDAQDYFXgxgeFJgL+ylu6oi0Z1Kyv8B1bvY/YuGWN1y944Y4ymhRmKDXrTaBYfALrK4DoR3DOFhE4ryZYCr'
        b'FLjKAYdp1cDZLCRZHzbA8rc3eAlL4Up4mAa4vkzB27ANETUftogo0Up4lLxYZcmmjGohi4orrvRwXUlXwy2umpT/DNyP/zhowb8VrejB6QTSSV7oJafwKQgqN8yZcraH'
        b'12hN7akEeAC20McawWXHkZON8Dl4la7P2TpmnggrFlbyGXAPw3omPEsXrpUHVRggCtwJbKKaYCfYTF40E2ysB3gowI0rVlGr0uFpQo7gtqWQnPc0q1tDrXEKI2yLdMq3'
        b'C9BCpamY1KbLdh4NG1rp64xHTGY9g2LseCibtcqeIV+FCr+pp+XsPnHuc3GWW5capCYc/YgRtK1m1tbV2xZ1nunetPPj/v4j/nXUGyK/8EX9WWbwkTo/MN3WbWjl+ocr'
        b'v9GuXV2UsG3nYG871/2333/KbFf9/eGCjQtbdjrab0pt2LFqI3v/jMIVfZxpxlnDXo1hb5SFLDxwMLx52hV19MWFCz/3fPNPJ3/y7Gy5Eik5e3XX36SfBdxzedviRuPu'
        b'c5nzf2S8v+6Nb5Qf3JA0TOvZarc8acH8k0u/3phyL5DVElXefqso6OyzL3e93H3g2yvnr7EOzDyxqOPsaan5T9tOFF99Z8Ya2dWKLo/nUtbc/evDXT5ulfscg69VO/G+'
        b's+I2L/vrkbJbPg9eLp39/cVPVgy/5W48/9DD/xF7dz/gHv/t/itveVcmLw3d3hj/Qaz4ZOXRrlX/2DP9T9cCP1TsmlX89Y7Fnzrtb81rtdlfvfe+zcz1G4/cCQ1bqBG/'
        b'8cX7b0bd+fqdC2EgbH354U9nSe9YmX80a92dC++/seqk/A/fV318M+zil0PfFHRv+elH8+xte9qe+VDAe0QQxu7Ag1WTHvEEW+30jo0jSqUN7i/NAgfJcd4s0QJwcgZe'
        b'BF1hggPrjeiDmPsR6zqNlrXdnuMwmtyAgsbNurwAXqXNBxnghM4eEtyEbeREKqLYa2l4WZeJ3Xlh19gZDCp3rXU8C5zLougXKFLhXuxmCoNgb2NQBs+CnnlMd3gMnCde'
        b'VdDa+GzABKvIsTV/cFMFVNH+XuAup2K0ytwBn8tO82NRLHiOAZQlcAsNn3VkCXyRnI7XHY2HZ1cyQ8AhGxqM/IwbaMXvEGAALxHZ2bMLjZjPdjSqI/Uoq4S78bpch/iN'
        b'N1uouQJrLxbohq0m5PW5KMVVPePP9fAk0+oZsJ9eJu9aCS5PNMUEbevoZXIt0MGOd+SD4+MhJ7fADrxmdcinm3P/s9wJpppB5fQyGr40g+TBBOd4aE2bKvT3xxu4DCoM'
        b'HLCGp1iwbXkRXZTrUrh/nPEobTgKNlBO7Biw41lSm5XgNtyMUjUvQgl3iTkUm8kAR6PrSWM2WsDLOlTwRXDT6NncjQXkiLGvAFx4/CRwMryqfxjYwKkenCD0ZwzOO9Aq'
        b'ESHuu1GdSMU0ovcphIewrxyU0cZJlQNEMyCF1wktuS8U0ev5NLBfrGekegscp4n1INxsQPsLgifhRaHOYVC19VNZpOqBQA2ysV3Vaosx2QtfkyX9MzSO0NBCe4pr3xrS'
        b'Wr8nal+UkrE3tjWWHIF5YMndZ37P0rPf0lM5V8U8b3jacIDrQD72+CCvWMsV3OMG9HMDehgabrCWG9wT3BPSE6LlRqBovP736Mew0eE9nmpubK/nAJffmqHkdjlq3YJ6'
        b'gjTcMC037B53Zj93Zm+8hhur5cbqcp1xjxvYzw3ssdJwUWYhPQk9iT2JWm7kz77UvjVRwdbyZmi4flqu3z1uUD83qMdNww3VckN7cnvyevK03Chdsg6TPdn7su9xBf1c'
        b'gQqlEWq5QlWuKk+F0gSNK39ej+dl/3vBaf3BaXd9NcF52uA8NXeBet6CfyFVRI+XmjurN1ivLcJ7UUWitdzoe9y4fm5cH6o1qmwincJJVUfX8h43sp8b2Wut4cZouTEj'
        b'j7v2uI9rxwQaKp3uoLG3RvZ4q7kJvSnkvv1IA5hqeb5I+EcNqnJXBanctVzRU8TqCGAowinIephyEtg8wsE3kRTXYW+4wldj46G18RiOcrLyQhFWXkMkiKasbEcoSWPp'
        b'o7X0UVv6IPqi72ksvbWW3mpL7wEbe62Nl8qGxq9/oFuxclTse74z+33x4q7DVFlyaJqaF6BKVPPC0RqcfdN0mMUQJGMoIhQOUww3Etqm4Du2GFOIhAaoBAdN95oqEjWW'
        b'fK0lX23JH3j8/fYOB5v2NinZXea0055WNoHLV7qpuZ5jZ9cHPH27MnvctZ5h9zxj+j1jeudpPJO1nsnEpKgUu1G3d2w1ffxw2FOguJGTYeNA3DAYxMTh+wVeO2E7NLJ0'
        b'WmD/JLO4/5SVHHbRImCQJQX6isV4adg8tG4+/mU/AaON2IDXmeITTl448MaBDz40ZTRiZDvyCx+XIgamNDgbNrAiZ/jJQWdyCJQclhs0K8qJz43PLMpfkJOcN8iSS+sH'
        b'2Rg7fNBUF5GXnJ9HFp6kCf89NeljsGz2uFfGIDaEuEOC2ONx2QymYRC1JwbuFNepNXKADIcBbvAQh8kNHaZQ8AgHzUmIbJ08FShBgNoyYIAbihI4haMETuGPcNCcMQFs'
        b'LQSDrYVhsLUwDLYWRsDW9HHShBgnzR/jpPljnDT/x4DUZuAEQpxAiBMISQJb59bUAUtftaUvDcVmi6HYbDEUm21Qc/KQEcvcf4iaKjBhmucwMD7dE0IjU/PZQ9RUgQPb'
        b'PGCImiowMzAPGqKeMrBkmSdhROqfDy0oFzclV1mhdgoYcPEY8PId8PQZ8BaoPJUL8ZeHSqJcMvbD00fFVkaPfLl5K+uVZiNXKB9PxcIBd3zlhIEX8pUmA14zVKHKjCFX'
        b'Syc0LnHgzp1uPcB1VsiHWOjXA66jIm+Ig37h5ndThijlKL3/kCG+Y0TZuiptcDZDxvjahLJ1xDgSivQhU3xthjpMIVeGKpYNmeNrC8rWSe0cNDQNX1iOPWyFr60pW3dl'
        b'Ii7okA2+5o7F2+JrO+wDpAzXYMgeX/PGrqfjawfK1kXJUiYpVg854munsWtnfO0ylt4VX/MpWwdFopKtiB5yw9fuY/Ee+NqTtLsifcDJlSTywTep0cDLx8liiEIBon3E'
        b'EZxcFSGKtao0rWv4PdeZ/a4zNa6ztK6zNI6xWsfYAZ6jgqXIUNlpnQLvOYX1O4XRLj80vEgtL3KIw3JEWaGgWTxkksAwnzFE/RthKjPQ3GmI+qUBbRdItuw6EkDv6HJo'
        b'/iwC7WuZz1oI22DXOJWPqe774RIMZWWlB2XFwABW+9j7pu0zLGeiUPctYY786ma9iGakM4YjWRlTEldy+ty4eVo5W2K42Xi89mkhm0lJOTpgK5NJQK84ElMUZ/ZYnCGJ'
        b'M0dxFo/FGZG4aSjO8rE4YxJnheKsH4szIXE2KI77WJwpibNFcXaPxZnhNpHwcRtI7DuY6AqVHANeLTMfSSPh6UE0WVCT/HsyzNOE3Kb/O7mtfuxOF2MXQ+LWzCQ6R/rc'
        b'r2nztGbLcmOJ42M9Ng2lMm62IP3ptNlooSVNEd3O4/Mk9gasZrNm83KOxGXzBAdyC60kDgRBxH2QBh8VZyV/d2Ac8Dh21jESxS+rLJHL+b45NfL6RmmdvKRagmdzmbRa'
        b'MO6ZcRcz8jH+eXlNXVVJPR/9qimV11RK66UEtr26pp5fWYPPdvNLysqktfVSCb90FY3hPmM8AnpdOYXNZAaNSySNMjk+8z1oqvtJjm4b0f7J0W2WpLxxkLW8Gt2rkkpk'
        b'DVXonlEtKvnKmjoJEWXoY+D4aHiZkV53jbrmU1D6tkvPs5/nPG/wvCExpsa9w0b9wkFtakDsOcx1DvoQvW8zmaAZNiaaYaPHNMPGj2l/jZ411mmGJ40bh4c/zJoEDz+t'
        b'WlYvI0bpOqctI50mq5bXl1SXSZ8eDX+0haN1aPo6+JeacpKz7nx8CYbzSKBP5aMEVdI6weRe3uP5OjMH2p8Lv6EWw5NE8CWypbL6SUD6x5cCd+5oOdDvJ5UCRU9Vhmp+'
        b'SWVtRYlosqJE8csq0CvLUBZTF2eEvCZvEzqW75uJqBoVSVr9L7RI2M+1CKLraHpAphTyK0tKpZV8X/RTJEavWy2VlVWggejPL5A3lFRWriLFktFEIZ+0FOOLTtrWN1iv'
        b'KSYpvK4gaGxF8zMIUCTOZU5Axkh36JoFMYm8krKK5TW4KVCZUKHrpIgHTOEroaG0UirRMYHxueSgsKZaWq3LibhKQNd0S+lYx+RtnFbPr2qQ1/NLEanomrlUWr9SKq3m'
        b'h/J9JdLykobKegHhQpFTVnSEf9DNTl/xZRJdh4X8XIeNMB368ZErfp10qUyOWhgxO8QTCTkJ+Q26bmuobpBLJT/j/WEyI91p9B7DD0mWFN8JGFC1xRl9ZQVUQwy6aVIC'
        b'WkbwDNJo19fgELidQ0ANxrSMc/Vdr2+JM7MEe8CJSixGvCTlUr5rT3GouOJFzrkNcejWUkt4e0KeE/LDZ8cL9LM8VgvOwx4z2AUvwjOktLERZhSv9gUmlVNcmd6YTzuK'
        b'h535oklzxvpOe3hJp/LULy2SqZpNQWcx7CLZFpkZUmaeQRTFLzb7ZCmPxnQAN1yBYtJ80/zySF7wFmjV5bcB7jYG+0G37ujzT6nGlGXOMbwNZrYoajXVEIszPOLvNVl+'
        b'sDkzE7TCzhEV84SCXjUFL4ArESTfG0xTilv8T3yqstI9yYnurWfARnBhsox9U4VITLxGq1LH5XodnDGFzVVgg6zQ5jhDfhXlslh7aOfuWdizxpYjP3Ulf1DrpBRvZTp+'
        b'wK6Mokqlf+0Xf6AqvrLrhPVr6ce++i72ztKfmOYn4AWONyfwQ+HSM+kOzx77x7Sifo5kaeG8Z758d7j6LnNBzeJpBdzyZQfSDkkdgt7+KuOvx1dez3n94HLJ0kb3exGL'
        b'f/fuplrvjnZunfOHewcCyt/j15XBBsVf5rWLv+95O7ZHtOlvv0t77/jyq83rr+7eIT60Ys2eNQ/ek/8+45GFT+qHhpf/OafI7nmBCVEbi+M9RvTfiFBPjejA57MdmXza'
        b'GfnGMkPdUTDQBg7qDr+Rs2A5cB+xDq+NAef1lehiD3iaqLFdoYINzweDVuJ9CfR6wTsTlenWXjlgLwt0m8Fr9KG1jplwp/Xc8fDCl9NI3HxwhWSg0/Ibw3YGUNYxaQ3v'
        b'ZnCjkWi3aaV1IjzJAEdXgav0q8/XwJ0TtyOs48EmHgucAxv4RCGdXWA9ToFuDU8lGLNgW5j1IwxzaQpOg030gkIEL0HsZRfsxir5DNgJjpEdF5EBlQk2G4Ij8AbY8Cur'
        b'SAjsn9WIsDEeCXGFDtaiaTrl4a30UJYpy1SCzuquao17mNY9jMAWEgfo9fvW014sVG79Nn5qGz+CeThH45CqdUhVc1MHPAMw5qGbLvWYr/X4fhuR2kZEkqdpHNK1Dulq'
        b'bjpefdso85R5Kl7n4q7FGrcQrVsIgUXUve1Z2h2Gyqqf+PQmj6doHOZoHeaouXPQmvRY2qG0dnGHGD1kPPLQqj2x+2KV6I1eahsv2qu7xiFB65Cg5iY8cHIlSf/NF7sJ'
        b'Trocd9G4BWndgn7BYx5euHWwshN9HvfNeAFrx7DrkLpLOLiMgys4uIqDl37eTnvUK+MEW+0p+l6AxFM5diOu79M7ezqDkUv8bP/a4a92LgQfSe8yjqauW8Qb/RJwyM0j'
        b'8IajcvNUqHljbTUCmleA2koP3ZCW2kdE30lgF38pOKQOzc+sSE+afvrSzcelOzpaOpcJpSMS41jZ/hW8wxGp+unLhPez9OAOXekyjQixjzXYL0eEZBchOfvpy7MElefh'
        b'KOzhgg26cjnS5dKT1P+9MiGR++nLVILbSM0YaSPfMVG9ZCKmp/xfLNjSkR4cEZGfvnSS8T3ogNXrerL1v0lRI1L205dn6ePlQT03Kq3rlUfAJNsZ9MbGqCV3VhlLr5hm'
        b'lM6Uey8K9hvrwT8YEOUBdqFn3GzSbNpshpUHzRblZqNgEBPxt/8jUCj/4FhPoj6Il0iwI9dq6Up9GkFj6qlcuiajxR6dGKt4SiQStLRBC6QS3VqZeGbFvu6E/KV1NQ21'
        b'tJanhF9WU1Uqqy7BrmMfyxIR64xRvNgZQv4MfXhbdE1wc1Gi0pqa5bioWBNFVnN0MepX1f4Cjcfoi6L5eTVVeN1MK6ywzz8dzGxJaU0D7agWU4ZUMlXb4H8pNXV8KW4S'
        b'iay8HK3zEGeiV6DjK6Vrb+K8FjXbUp1Hw0kWf/gfWtCWlVST9eyTlBlB4XpLeL5vTS1xzFs59WJev13phepjTILvG19aJy2rqG6oXirXaTaIX8NJCzpGB3K5bGk1IQV/'
        b'0iZ6GetcRfNl+rWSoUU+WtBPmuvI4j2IdHJ41OgaHr8pSCDEKka+RFpaj9+DUpSh5bUMX5RNpXYgVCkjz8ul9aTtIqOegmZSMK4FUWlOHCoyqTz6qWkOlVVWr8uAbndy'
        b'Z1QH4ptXU1mJ9R41Av6MGVVYsYSqs2rGjCk1VKTG43Kkb41lOQc1b7UoIBXNSNW/JGsavVenxqiRkwrrEH2f6nk8OOmn9YerPz9zVENDhm9N6TJpWT2f9ODkYyAvOzI8'
        b'MEinTsbaYnp0+j9dMcbhlERP0JQ11sjKpKMEnyCtlC4tx+kE/GeCghc/TZbBum5skNLVkVWTguJRn5SUmblgAa7ZZM6s8b/aklVVxBW2tA5Pg0J+FWrnUX2QXoGCn1wg'
        b'Xfdg2KTx/YXvjNcO0qMlYGSkTFosWshLQJXEYx/ngV4fEjjl68chw4zoSvWGCbqLRmS1XEYXqqZ80reWSJYhyiDtgR8g/sBLmvDvyXnj5FrWcZnIiZpYVlZRL1uKqyIv'
        b'q6iENxEnrxQ8PmanzFPER3STVy9tQMx1NANEwTK+rokQh6pCIy65QJRfUl8qxap3yRQ5IXKhndhWNlQtl1ZM3v4ifsiEZORtJQ3lqxvqpWjmqJYgci2sqZOTQk2RR2g0'
        b'P76hvEJa2oCHHnogvqG+Bs9vy6d4ICyan1YtkTXKEDFXVqIHCqrkJfWr5RNqPsXT4ZMV+Zc3UMRk2cj0ilX1y4oVOVl+v6xdokhDjjX9z7T8pDfzaUrGOvIJ5f7FlKhf'
        b'/fI6VBtf3LajZSopXd2wVDA1+ek/zo/wmpoAxyUMipoqJSKz6oCSqUlqfDbhU2UT/qRsEFGM1u8JeUTqJ5uyalHjMpukXlNOaDrkKsThdL+IPIBkUsRbR1i5bx49x045'
        b'YY8BY0XzE9EFn75CMo6vGF1Kq9F/ROZ8PAdFTsly9SC1xmcTPCGb4CdmQ9C36CmjMD5flJbE9y3Iq0ffeL4Jm/KxUbQu+tHkAsKp8Q2+LxrkOhJH3T51MzTUIRG5DM0W'
        b'ibpfQr6ebJdckMv3nQe7KurQIEVlCZ26KHpAYWOZjd7WFWokK/nyhjr544V6krg3lXhJRMmnl/xGRbT4cdtdTyfDEOizaH4W/uI/Exy4+OkfC6YfCyaPTd0bI5hqOhFS'
        b'd42X5k+iAwK4hh7BXyjh4+mm5mKp0rq66oCUupIGFFT6B6TIkHQ3NdciyafmVTifqfkTfsHUDOpJb0ZcKbkCCWGI90/NmkjZkMwmmbwYUzUekmKl0nosWeBvJGCFP1G+'
        b'K61piubjUxhIfirHUiu6gdp86k7FD2EkO/qpkko+vnjiE2WyejwgUfhEcY+G78Mp6R8kYyGW00UhQeHhiNKmLhNGzkMFwl9PpMjyElTbFMRUnpSIYO+hHsJf/GfCp06o'
        b'Y3M6Fvckih5BBYzmJ6BftCT8THDEE9OPDm3yyPjt7Ce29wjWoO5Jun+mZtYYYRCJaAnxWah7puaIpbIylGFaInr1JCNy3JayETXllvK1Mhbt62Td6oyGlVk0wL3AuUEH'
        b'yLSzcvEoHBNspvGr2iuw7zaK/8B1lZBR6EBDRc2OgydopCg26ASdGCkKXofnyQPRHvaUkKIsLSvWx6jyzXXwMruCQQtsS4PnOBSF8aO2xdAwNm1QKdTD4DONA5cxBh88'
        b'DNtIbuULsUM4av6GhcvWlIgWUAR0CmW1gSAL+qVjb53YZgd0p2fOTcXeAih4AbTkUk2hxpFrl1K2BJ/mi5nZGR0GzbRvAF6X4w2qYSa6DQ/AraLJvAPgfFLJjhts5Yn0'
        b'fQTAnaDdTOA1l+zLyK6s/itHbo43x1piT+y5kAXjzLZWfbo3NFPZ7Vy80T6uO4bjbHkjOXnP6b82O2zdzNj28vTrbn8w6RSuS+tQdq0siBCuGjry5ffrv4+9FGB5KeE3'
        b'g4FpvQZrAj7ZEqky3+hpfbE9wbWu37Jv13eDf6rI7mp//e6XkgdDz339D7tdnDnmM6Z9P3iyRin909XrLmuCHs3ruflJr3yd5prLOynH/x5X+4LmPeelGV8NDO/79uif'
        b'LmjN037g5c8/LjF9+/1uzZv1X19Y88mdj4fln76a9ZV2buo0W+ucLP4fF9neHj535L2SAwNfFK961njV1ZOLNs46k/r+kQP1d8tUn+00ET4Ia9rwwe4vrY5UWVySt57/'
        b'uuvwjy+bH//xfbMfOyN+4ohcxSxXpsCI3jG98wxHBx3iCfbpnLGCLnic7LV6eYEuHXgIG24Dewh4yK35JM7IErT4wW3ZaaDbkcWmDCqZ7lABWwhyiBPcw6W3i8Glkgb9'
        b'3eLF4Owj7EqDtRJunHwbdXQL9QDsJduoYCtUkh3m3CZwfcwbgb4rAg48D8/nw5doKJfjzjlycNYrKTVL5IuTwt0YkaSVBXowJCYNpbK1BLSJM9IYFDOX4V8+oxEqBdN+'
        b'TQfkGKWdP4YDMsFq22xUKz4CBXJBt3mb40LxhWrXQNUK7KnOUVGvJp7qBhyxjyBbwYCPr8KMhpL2VDZ2CXtYGvtQrX0ojixgDPj4KeuxtU2PTY+kN/xyZV9IX0JfiDZ8'
        b'zr3wzP7wzLtlmvBcbXiuRpSnFeWpffIVbEVhu9mAo6vSoCNG6yhsTWpNGrB1UXqqbb3RR/dWvwGfGQqc6lj0oej2mNGUH+ON0dkahzitQ5yaG4cd3i5SRantwlpZAzZ2'
        b'ConWxV9tgz86pwhaRz+NvVBrL+zh9NuHqe3D7rvMUPtlaVyytS7Zal72EJNlGzQQGNVj3OupDkzus0EB/cEGSL4qGw1PpOaJvr3v6ImLFTQWDLj4KapUiRqXQK1LoJoX'
        b'iHdBh1goAn+zWVaiAa6oNUnL9VTmabH5jUjNDUOfHjb9Pfr59r49H8OpiMaCAQcfhUjF0jgItQ5CNVeoy9pKhL7l+EQAZFsl2lHQziQxkAX5pol+LOjHwb9DeUkW1CsW'
        b'Jkm+rFd4pkkerFc8OOg3vVk8jd4sHtvfwMaOvwgUYAKxje0WP5HYluHdYiU1hno815HBwI34awW/mi3MZ9QkDnfIlEkc7rB1Pss4zVSzgc6Hw3/Hb9lSAbPur9QET8iu'
        b'k8znXvR8HmLLCd3LsMSOcCr/HsSjaODOi/CAibwBAx3uZCPmep7hAg6s8zQYQ8VH07WnKeqteRTYsGheI2glk7psKdicRz/EgC/Ck/AGBS8HziEvCl24zvknaggDA68J'
        b'rvDRoRJ0zl4SEmoAn4c7sQUkJXWFd4jBN0PkEhLKLgzERr5UmbsDyeJduaGlmMnDJ7kqoXkIbb8fK7bKyGDEUfiMW8yietoqvE1s2XiJRW5Wfp63iE7ZKTYrFlEoy5zi'
        b'DKNsLzrlsLeZcBuL3Ky8GL6STvnhfNNKf4YvMf/fs7aJTulpbBJ3iyI3Kz9LrqJvpiYYhs+iSJHMkqOW07VaH22bl5OTg2oBLzOTKLARdi6kMRN7wXlGSGAgeh2DA2/D'
        b'LgpudANXaBTSU+nwYF4O6k8meJEytocbYVcYsc23dwVXaYiBEXiBFrAHXF8B99BteK5gKUEYYHhSNaAd7IU315A2jMnyJ+7dKTTNbHRjmtBi1JkC2IOhHYIpsB3cCs6H'
        b'ShqGYXsUmtOwhb+I8s8TgTMNhBJcnbJg2ygmQCW4RmABmuTkzUGl8EReDh9jLF56dp6tAeh0qqBlsqMymxFYAB0mALwDNqeDU/A8bbqPW/nNBUYWBM2iuFjY5hNDN+j0'
        b'JOOkIga5WVlSFqdDaG0ryM7DDUrB5yiMLlwCLnmTPByibFM+Z+Zg8l20cr0NDWgKtsAb6Xk5QClAsmTminWmsLMOttA9cNYM9srNQ1BzMWt8wBkMaLkdXpG1VX3JlNei'
        b'2i+2zD2Rfw2JYZZHFr9/zcnH80Et5/Zze2crX3R8zfKQb73melfzvk0GGrd51T+07ci8+fq5P3huvVK5/NMm+VvP/4/xW60JTMG7vaaq7N/01datNl114/mVP97NfbOk'
        b'zPRoW4rblSV/DO/+TNm/5+xfDi/ctPSHHg7j7pYrjYwvXnd8Q9hmsbC9quvdz36oML1de+czz3fWnRKej1wt3hq76i85H537yDBq2PQviz+ZfoEV5p8wdCKlWPtZRftn'
        b'7jeH539l3CmnOk+6PSpgb3/l3d35+6v7nCoUnVaX3jXJe8PcouB3W5cl5e+cy6q5uWPb222N36fc8Dl9v+iCwd97ai9+3paTazDnH9uOFv02VCTd/QH7ZFP6Wwva5RdD'
        b'u685MH+vfjb83TfKdli9ube98I27n/10bcaJP/GqNpzdYv/JP20y9me1b3hn3tuXc9kef2m5dt7/yt1z2tvg85+y/3zu9bLXjrkWfHxta/TZiN0/vO/5Y9FXotPr0tYM'
        b'XR3cMES9/HaE9WvNRX1OAi6RuNZCJTyOhXJw7YliFzm5dr2Klg6fswXH/Yggh+KM4A1mcAnYw0FSHkHG2LcKXkfSfQYDrTDuxLkxwJEqsINEuRbBXrG+b6fiZ1ZRy8gB'
        b'O09w2WQMIo8NT8kJRt5pcIR2MrOzKUg8ibU/P5nDA0eNwcFqIn2agCv1I4cAF4FbxNrfG+6n8fBOokF0bcTcP6+e9oXn1URE0/xIuAcfU2TC3frm/vPZjqB1DTEj94Pn'
        b'5GOIBFABnqMMnmW6gxvgNimhHTwBt+MTjCfAwQmnGDEgwCZ4haAQWkokI6JzLbyNJeel1TozfuymaxwWgAV4jgVOLUsA2xNJu1uC5+ePRwLYwKpcUOPtTQMFXIcvOon1'
        b'YQAs1rHAaVFSBNxFJOA0eBOb7wcgZjLuICMLtoH9YAONl3DGa9bYSUlwnIMt/O3hXjqygz9dPM73VrWkhg8UBEJAjLjtRfwoEzSPP0mJj1FegJ00TN+Jmvpxx0FHz4Ii'
        b'JgbPgytwk8DoqSUczIj4fP3TcA8p7KJnTLSRF0lkZfVElp6ms8HPdaWmO7ZysHdm0wG+p5YfSCNeafhRWn7UEOVuJRjGQWsq7YyrqX1Wx6xRB2DEjbRt+8KOhSq39iWt'
        b'KQ8CIrAHsFPru9e3Jit8lYUaBz8NV/iA63qP693P9VbWnVx5fOUAz3GA56K0a5+G8tDyRD02/bxQNW9WL1fNS+7j0k5e8rsW9DA0vGAtL/geL7KfF9lrpeHN1BKkrY5p'
        b'93iifp5IVaLhBWp5gT3WSJi30fLCcJyFzvnXXBqxr4eJXYtpeaG0UV6q1iloslx7E3oTexO1vDhdso5MDW+GljfjHi+wn4cRAQgcmQ4RgBc5ruBxvfZqXnpfyuM3K/pS'
        b'tUkF95KW9CctURct1SRVaJMqnjqZ80hLLOlBlYnQ8iLu8Wb1o3ZC1Y4jRXVR2qC/+Z3OXc4a7PrMmTTt2AfVJKkjrd2iw0JZp2Io61CFnhzhMsBzReUbCnMMtBumHH3t'
        b'H+Hgm3CK57K3UVGhsffR2vsMRzjaCjB8nQCD1iH6wL8iKVf3YxWHKpRrNC4hWpcQRE42vCHK1Cr8gaf3yTnH5zy5b1yf3K2kHbReGLKAF63lRd/jxfXzMGSBDstvjKBG'
        b'6GrIyliEqmDshaqAgm+sx1VB5TdsY+wVjojUe0/mEJfiObeaPe4R68lnUIlHrJ8fbh/h1UQDpbOZT3b9L5vL5+CF0yMsius7lTWg9D2+cXTePdg6Kz/sXNZg1LPHRH9A'
        b'/xH3nHXfUBNWC5P5BDLMaiAAPlutwTm/VCTbtyPhLicVzb1ohgWn8lPBWdgs9BcYUKlwq2GtAGwi4uMzaFrvwYhW5KQ8Cx5yqGSATcu9aDR21TpAMKCaKuBFqkkObhIJ'
        b'1QRsL/TLZsKWCoqRS8FDcIuJ7N0X53HkwyjySJJq59wbJ05hU4bLbbeBvHSTeeMrfa5Dhs5K68rpliwW/+VWYeWe+VbLX/T/nzSz3JZc9yu7gl+5LV/76dJHzDYnpVnL'
        b'A2OPutftC/4eszKy2/zT0JBtH59thS3fFnhdf2fmoV3m69bVXU/+R7/2XsrvIx2/D9z7Tnn6dMVdo9cyFW3bj+cen7sx89BPC16uvul1MvTtRZ22sVtLt3+6WTBjjpWL'
        b'TcLKQ997pKbeX9y4rvvO4l0VAbfCUzf/If3eidw6UWP5X79fn/u7d0Ssb26xnVV9Fmsrv+oOP/nD0ettv/2Ca1drce5vvwnpdU9IWVDX9HBF1t/eN1SkpOztFkyjpZlW'
        b'jpFfKvGqyYZbLSMY4NxCqKIn3BfBhlQ8j4ELOURQwig1Lcx1qNEv0vYKNzGoPk6BpkMmlbjEIIvp5O1IowttnAb2YWFEuGC6fxqJN4U9TDRFn1tIBKLQslgki11e6QSP'
        b'6lRaxuAkE7ywwJSII07wMkMsBLuQVHM6G8kZ/lgBy4SKFfAm/e4X4Q5LnH9AtohJmZQgWWUG2DFfV3AZuED7DHWCp/R8hnLhSfKwTR0pdhrcieS7RWyDJUwPuAXe1mE/'
        b'2WT4YWCeNCa4I/IXMJEYcowFtjwD99CgSvtQvS6LsQgUkMWh4uAGgximfTy4Q2q1FpyEm8SYZgGiL0K3xlwm6KyaR3sAbcPeqLCLUrrJbOEdgwQmD16HR0j8QjQAOvXF'
        b'xJvwDpYTg8FFurd2GsLNdOk4VAbPAKiYQo75v43bO6JBoZmeEUFYHGV68pJG2oHocZ2yLt2N4trtizgYuzdW6UmbVGCdUZQqoXvO+czTmb2eGuFsrXA2udmX8Nt0kH63'
        b'XpOUr03KJ7fuO7ip3SM0DpFah0g1NxIjq5odMsMzF5JabOwPRu+N3hOzL+aejW+/ja/KTmMTqLUJxM47/QYc3BQ+Sk8VS7VI4xCtdYhuTRzw9ju5/PjyzqquqjHFWLuJ'
        b'gq2QoDkEZ6zMV4XSs4+afAa49gfT9qbt0QFVtoofODp3RByLPRSr8tQ4BmgdA3AePgM8h2NGh4yUXFwwhcW49zBt/Uige4+zmyJf6d7lc1J4XKiq78nXuEdr3aN7kzTO'
        b'8VrneJTbdL++3AEnl2Oph1KV+e1ZHVmKrCEWukuiSDCMg0fUuHuTBVgNN9ntIdZImeSYA75qa5ccwXk1gp080/jVWAYK6VnQmJ4F//GzUyFNHnh/YlS/NiVxuKJFv3wD'
        b'NQK/uYb/sw5Q/0P+UImjSAF7gvU1fUmqzyS/swTWEzFlTBiUPrDMUxiznGYQv9710io5jQzzcKR1BFa/okZdrzNw82+Y+I/ulPO4U0aN692wePIWczyCDJttbolBTiyH'
        b'zCgL2+Z5SpYyUbGqp6wv765NX9rAdCelX69Nb16v8d1ERJoWczHwEQofkXDIgIqNYwyxfDDYzM8Gwxy9J9n4bi5jHLRMOIaWicTQMpEYWiaSQMs4eih8ByyxH1ManMYR'
        b'g9M4YnAax/Bm8QRomTAMLROBoWUiMLRMBIGWsXFsRTkQ8CVuEEpgE4IS2IQ8wkFz4oQEsThBHAOniGM8IiFJo/+WQPyWYPyWYPyW4McQbiZJYERaF41Ei0yGQt5jQ/+i'
        b'Q4zlVK9IUiQpp2vdInqNtW4J99xS+91SNW7pWrd0jZNY6yQecHFXSJRRWo+oXm+tR/w9jzn9HnM0HmlajzSNS7rWJX2YxXAW4+7hZeBGRiEa/KPvGDJoYJiLhqhfJxw2'
        b'xHk+0s+5mhVl7jxE/XzQyCBNofBQm7tozF205i5DTK45YlI/GwyzKAvXx9PT+CZkjr4JexrkaUInD51Ch0OZO2Ao/8NJAkaWzHivM0u+AA9QxbR1u7Ozn4uzfHXpArsD'
        b'/T+dEF0uXL5m+HDT8CevvfDa5pZthlXH3b4uPRT44I/fmvc+EkfnpIt3ei3gP/zT979/90uZsCyk8ILtuxd+3Hj+AMvA89n+37H7Drz1Rfyw58MvP/8wK9ljQFz7wb4T'
        b'D3cdablu8/ufcq/ZF6wrrKsufIf94G/lfrk/XH3hh6I5x2tdq94bXhLtt+pBZ97StSafSuYMrj0qiv/I/KBfw75KbdvJjpX/pGo2OS3L2/1dqNJtZ0UG4/cyq+ufVdef'
        b'Nu/l/GHW0e+7Erf8fudvCssDXxto+0NO77nEjVWFM11bV/xU1fC8tvuR/+e3Zl/P8Dd9/iN/77C7H0dY77x/fM+8xq9k6fahL/j1h06b9beQpTk1e4b/WLiyyPTR3ixJ'
        b'0OI/bx68uaZ3Re6NgRcU63vPZ9tcbP/rB82nPowOu/J69Sq/M3/7eP+1DW2rArLeDv5b51v/fFDpx/qzS8eQ/ZsZDevrlghYj/A04xrFgi3GERkM7GcLSUS9bCJ/JTbB'
        b'M/oe2U/5juyDSp8lWhLQLuaNbWnCw0A53sM6PCQXeE5kgkZPDP4TLPdfYNKetEAVR/49xq0n8O1Bo6KiypoSSVHR6tFfRNL6A2vUrhGx7lDK3HaIbWhsPzDNulneGrxt'
        b'5Y6VCrfta5vXKuQKuTJYWdIV1r66Y7Vq7qH1ivU9nuivrtftckPv3MtNF/wv+/cl9SXdtX459ZXU/uAMdXDGfZ6DIlhR0hHWbtxhrEzX8Px77DW8SHVMlsY+S52bry4o'
        b'1ObO67efp7afd9+Or7TeU72vWm3pOcSiePMZQyaUNbc1fp9tc0JzwrdDhgzjNMaAtWur6ISZWpSi4c/R8udorFO11qlqs1QsrkRaGXsOUb9K4OtjjBjTLw2GcfBo7F4+'
        b'I8bYYYh6UtBaOIy/Ho3dfZbhiX8+KVDYDeOvR2N3sxiUieUQs45tjDjY/8VwmISP6N8sVNgddrri1htTPG+VqcY+pNlsyMDIGElqUwV2dSxjJ5TffzQcJuEj/fvLDEnr'
        b'5pLa/O+HwyR8RP8eacuJieTYcm97/OwEGwrYOCSIdPvizoPMoqJ/cR/8P8PI8KZB8fiTHJNJnlZMLHmOMC+8ApZ/SukUY0EMhiWW7//vBb+aNTdeP581jmdRL7Ms4q1Y'
        b'sr3KG2z5FXTzj2mvV+2MMmHGWyavKfoNJ6kWchZlfWRrEPTZm2a/zVDVfFy6TPKBl3NKPtvvn/9Q/aR6YwdXFix5bc/JuD3bz/hKBXsjt6e/1/VtiOHD+182fDgsc5Z6'
        b'1Xx3LO+0q/idA6vb1q4LdTp8eZH2VNsbRwvkIYKP7sYaWpi/m/+R3eH3yu/3iI+8J/Xh9Ku4oWbChbUVL5ju3uDyHa+42eo3iuLtzVF2vj2vmCyvbGzrP8Z899L97b3r'
        b'mX29gesXzxdMI9O3E+wgSoht2fj42o5nxGJDyhRcZEKVfQrZaIHnCuEmcTZohS0ieAGnwzoYK3iTBToboII+jrTFLBS0gN1l+CAS3gXBe26GlIU1ywXsAOfJcaQlptXi'
        b'tMwZmYaUAegJZTONimc+Iq7lNoIuJFgEhMUbUIw8DIZ9CR6nDzDdXgLO+qXzEzkUQ0xBBdgUTyttTi+WYdd/u/CLzuViFGRTARO2csFFopaR5GbIddHTwREcbZLGBD18'
        b'cJ1EW8TCTnGa6RK8P0hvPVnA7ays+eAKXZ7mRVJxmhy0kFOF+EThMnBQp+WKjSQ6SHIirxT2oARmNkx4GV4MIAVLToEdoAUlqMUJ7NegeBNwiQkuz0slu2pL3ADGpb7Y'
        b'NNcMNK9c0QAvrTBb0cCg7OFuFmqn7eAG2b5bC66CjWICWJ6WWZuCPVeagkNMeBz2gNsEMTwrHHbh9g4Qw/NyJEztwu2ObxhSjp5s8By8Al4U+D61OPV/UrrSY0++RM6K'
        b'G/n3BElrHI6E0TjokBKGHnwE5lgOFMdmQxb+GzDn3jN36Td3OdKkMffVmvtuSBlgmzyfsSlDbeV2IlLDFmrZQjVbOMA235CG//R+uKrHfwbYPurJPgNskXqyzwDbQz3+'
        b'M2Sw0JKDZpD/r8ImPmXG3ZCttwfjOsiqlFYPsrHZ9CCnvqG2UjrIrpTJ6wfZeFtlkF1Ti6JZ8vq6QU7pqnqpfJBdWlNTOciSVdcPcsrRHIO+6rCVxSCHGDgPssoq6gZZ'
        b'NXWSQYNyWWW9FF1UldQOslbLagc5JfIymWyQVSFtQklQ9iYy+QhM3aBBbUNppaxs0JBGBJQPmsorZOX1RdK6upq6QfPakjq5tEgmr8GGoIPmDdVlFSWyaqmkSNpUNmhc'
        b'VCSXotIXFQ0a0IaTYzO3HPO+4if94/PH6JEEJvgx0ThSnOQfok4rBkPCwvPX/8/hrzb1YkHqZRPjeD71Mt8i3p/1nVE5tuwuq/AftCwq0v3WySXfOeiu+bUlZctLlkp1'
        b'mJAlEqkkS2BE1H+DhkVFJZWVSAwjPYMVhIMmiFrq6uUrZfUVgwaVNWUllfJBs1xsZFolTcaUUhfH1BE3Tea4Z78ziqmqkTRUSmPrUpg0ooR8HQqGWAwGA9eZPUThwIIy'
        b'Nd9gOMSutGRwhyi9cIkbZWx1z8ix38hRka4x8tEa+QxRTEaYWhjb593n/bLvK75qYTr6DBhZDpjYNQvV9iEak1CtSaiaHTpAWaopy1aehnLQUg7qkQ8p3v8DECd3mw=='
    ))))
