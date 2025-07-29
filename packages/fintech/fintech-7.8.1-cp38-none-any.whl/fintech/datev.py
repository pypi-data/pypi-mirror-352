
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
        b'eJzsvQdYlFfaMHyeZwpDR2zYx84AM3RFMVGswFBURA0WGJgBRocBp4ASuyhIUVHsvYsVxV6Tc7Kb7CbZzWZL8rLZkmRLTLJJNltf393sd59zZoYZmTHJvntd//df1+fI'
        b'M3N6u8/dzn2f50P01D8J/E2BP+skeOhRASpDBYJe0It1qEA0SI5J9ZLjgmWUXmqQbULL5VbNItEg18s2CRsFg59B3CQISC/PQ/6lKr8nawKmp82bMV9ZUam3mwzKylKl'
        b'rdygnL3KVl5pVs40mm2GknJlla5kua7MoAkImFdutDrz6g2lRrPBqiy1m0tsxkqzVakz65UlJp3VarAG2CqVJRaDzmZQ8gb0OptOaVhZUq4zlxmUpUaTwaoJKBnsNqxh'
        b'8DcE/gLp0MrhUY/qhXqxXlIvrZfVy+v96hX1/vUB9YH1QfXB9SH1ofVh9b3qw+t71/ep71vfr75/fUT9gPqB9YPqB5cOYdOhWDOkAW1Ca4bWBqwesgktQCfEPLR66CYk'
        b'oLVD1g5dCJPHpkGSU+I+vyL8DYS/3rQjUjbHeUgVmGNSwO+9A0UkRV8UIFRken3+KGQfDZH4US1uJU1ka27WHNJAWnJVsVLSkpE/Wy1HY2dIySOymdxUCXY6PLKB3CYb'
        b'rRnZZBtpzibNAtkqoIAMEXfISbNKtPeBPJPJtSRtRkyGDEmlwsq++Ci+WG2nc2V4AZ+HhDDckKEmW6G8DIWQRkkO3o3vQtmhkGUoaSWHcRNpjKmCHjVnyPCtShSAO0V8'
        b'nRyW24dDlsXJmZDhWhBuqFlhJ50rglbYBdQ/OZFsl+BmshdvhK7SYUGvL0PbTXh7rFYdRftLttOQHxo0FB8fJcWb8NWMEuEp0BzknDo9XUO+gujbrWHpIMf6CQ0AwmtE'
        b'WD/BtX4iWz9hrehYv7qn1492ol+P9RvG1+/oGj8UpP+DBCmLYr6Ij0QscogWFnXUGMhbFJS/YgKPNGn8UVjVezJUVGTatiKGRy5KkiLF9FdgAxbF7I6bi9qRKQCi39QM'
        b'kP45HE35YtrDyV+KN+NjhVOCyR8SOpL2Cx1+SPmSzJLwXsI963cRi24Y+mVoW6gQeWzgZ8JXEf/IOIa6kF0DCUbdXFi1ptg5keQq3hRJGmPT1aQRt8+LzMwm22M0GerM'
        b'bAGZQ/2fw3dJe4+5D3QOezqfe8+9g+jMlwa65lb82rkt97Y35D3mNijHQltnsJs+e3TeXPV8EeETE0UJAljc1cseBgmVpK1P3tTZUMNINDKe3Lb3gkgNPl2WN1dExeQq'
        b'KkczRqyx05rJPrIPN5Jd5fgq1BuLYotTePxlfB3fIrv8x8LA1Ui9jNyy96WzNgafz8ueQ1pkCJ9cLb4oDMbHejEQnj93BN0F0VqA3a2wOR8qInF7TDrbmRrSLsMbR5KT'
        b'rCe4LjIedz5HdsHwJqFJ0wqMpp/8UWY9CElR8gtL3owPwXFBm3U/NxbUt+eFvjwgYv/CF3Rp8/ufmT/kx5vTd9+ZQTJqk8J37MC/ef/FRxdbLC+Nzd3xea/LP99cuu9H'
        b'J186/OqDY9fqJUGXfjb0p7KBuVOHLugzMv9USMCt71V+PGnLtQt9ajNvDq9erf7p/I/TvyPf9egn7W82PTryk9VP1GvGGD/IHTvy4r3FtrAvNkyLNl9qG3nk5b9UPpak'
        b'fP7LZJXMRje9FtfjPVrSEk1astWZFHEMmhZObktIPTlEHtgo6iBb8QlFNG4g2zLVpCEjK0eGAvFVkRweRXbbGGI6Tk4Nj9aoMqMZZsFt+JgMhZL1kkp8qpC1MhFm/0Yg'
        b'nT87oIPGWBFNMvcidyX4Er5NttroxlfjzfgozHgj2U6a6eqTG9IJAr5aiutVYpcYqbJQoFEFsq9/40Hh70m/SaWWylqDGcgII1AaIC6G6ue7gi0Gs95gKbQYSioteprV'
        b'qqRA+7xCCBMUQgB8+sFfCHzodzh8h4nhgkXurFkl6ZLzwl1+hYUWu7mwsCuwsLDEZNCZ7VWFhf92v1WCxY/+ltEHbW4y7VwI7RxRinJBFALY0z6SUQjcMSo6k7TgTrJb'
        b'm6HGjbGw+bfFZgpoNL4qKyS3FnnsSfpP6vhmhNNA+QHgBfRCgQT+pEZUIINvuV4s8NOH1KNSQS/Vy+r8CxTst1zvV6co8Ge/FXp/+B3ASW+pRB+gD4RwIIQBlUA4SB8M'
        b'4SC9wAhnaJd8LpuuHDZ9j7+CbVkicesWHa+fE10kISdNh4o4DpI0SAAHSQEHSVw4SMpwkGSt9Fn0WdIDB0k5fpcsliEFWhgKCNqkGlGLjJf7/lRmzYWUhwOtnxS9UfxR'
        b'0U59g+7jouayi4aPIFzw0mLSsSN+85xDx/f0eiVXd05nkp0Xzhd9X9oaMyRohmZIc+DC1PUfRwyYe+HXERsHpCSiqu+FrVO+rJKzbWXBW/tGu6hjtByRq9JQfEZSm4Tr'
        b'bJSLwFcj8ANnjmrYKNslKChG4pdrsA2A5FG6F7WkCchpFjAMKjlS4EZxJd5IztooCSNX584iTSWxpFmbgS8B6k0RB4SU83o7g/EVDCUP5wKnIEUyckggd8lJvJUnX8GH'
        b'ydFo9YRF6YyRUJDrIq7DD/BhlegGlxJvG4yBaZeisNBoNtoKC9lGCqIzXxAm0I9ckAq1oXzlNc5cfAPJuqRWg6m0S0r5vS6/aoPFCqyhha6MhRK+dsHZLgV+SzB9hLp2'
        b'Bm1kkWtnnA1z2xk92isRnwJ/F5wlOOCsVHRAmcgonQSgTHRBmYRBmbhW4ouLQD6gzB4Jv8eaFgSSFsBz24BWk+156aSJrt+c2XPV5MgaIH6TyXF5r/GZxqvv9BatcVCi'
        b'IuTwJ0UU3l4rjQ2P1mXpPi0KKykvNRVLG+PVRZ8VLXwt4o2X9ofEzkdHX1LU/jFPJWX4lNwg23CTlldvHO4CkDZ81UZZuewgfJ50AsLeTrZr8FmyT13lQM0D10rxZqMf'
        b'AzLc0Jccwk25/jnuoHIPN9vo6PRkW7o2FzjCR2oBidVCWn4+X0zRK1wAQiwz2Iw2Q4UDNCg+Q8UBQpBQG+5aJFcWXpWULXWX1KyrMHRDgyWMNxPuggUGBpQcl7jA4GiI'
        b'Oxh4aeE/jnF6cD0+YSEafq+Dmet0QQO+Rm48BRFOcJgw1Jj/8fekDD5fvlT0SVH2Um8A8WmR2Jhgj3s37lScNLGqFKFLyxVFtnCVhAEE3kpOzHLAQyre7gKIM0DFqQRF'
        b'LpRMdAFENzAMyqTgkJvMweEqpO8AeHBCgyKfwsMus4MI+sYJsPbWnmtf9tTaWz3XXsaXli5yl6xaZ7L3gACJGwT0cYEBne1yFxgcCPMOBq7GfCOEcRwMKDMslEq/BVLo'
        b'QXoER9WegCDLsasRZY+ulFOpbR5pUKs1c9Iz80lDbh7wm6vIHmA504EB1QjIRh74y43F9hi6WFfx2VoX6JCda3xADqzufePuFY9l1hwoddKv8JOijwGZmEqj+kXp0nUm'
        b'BjVVuobd5w3ndB8V/aD4jSsbGFRl6s7rwkrQ9/o1CjP29++wxcXo9fp0naL01yYBJa8NvWMbCRwkpWM5eK+Gs3ZLwhxAw1k7P9LOgKZMTg444M42wA3sNjCwm7CuwA3q'
        b'qjXuSGgRPstIErkM471IwY4cneuGhzaN5xSrXcTt0WogVyB37nSRrAqgWA6iIfXJEnLolNurKCfYTa9MAcD2KRjLVxvsgBiexx0rcVLkAske8A8IqptYMcikMkeFCzJ3'
        b'h7tDpmc7PSQ0T9zEZGMXbhIahK+VyHqApNQrSEpyjAsiN0ismRDx56VIa3xHl172KcDM94vLS/vozsmuRvSPU+spzGzVnTdcNIjfUxdd1i1+beHri8k8MpuYyOzIn768'
        b'UPKTXkCWBCR/NXRFWBsQJQoK5NyaXAcoqOSVax2gcAS38GU+ja/Bx4ldcNswvsz719oiaPLdEHKGNMVkkBaQweQBZMtScSQ+P4rVXLKWtFF5zcHtkCvkBHA8ErLF+9o/'
        b'C1UBA2+1WRxoisroyBYGLH8QQENtSDf2oFlYqXYJX2DfcAC8SzcIUO7M7gKBFg/k9FT1KjHHQgVzVTDlqSgFBLEioLCQ69Hgd1Bh4Qq7zsRTOJ5UlADwlFVaVnUpHDyU'
        b'lfFJXfJSo8GktzJWiRFKhiYZRLI+OVHuMyUoPgQ6KXl0CBTlKkSp4PiIIYogWZAsTGHvz7DapdmBXP7A7eS+gBRBYlGNzbcEQtUYHhKIWCDVS6jEcUgskLUhvfwYSBzH'
        b'hU0CSCMKRm79u+QzzIDGVz3pM91QbLRVgiAXq7UY9PznY84mPKZNPAmfb7DU2susVTq7taRcZzIoEyGJDuhJUJbBVmszKGdajFZbu8gm/fF3YcB/2Q+Tqq002ypTc2CS'
        b'lZFpeovBaoUpNttWVSnzQYq0mA3lFQazKtUtYC0zlMHTpjPrvZYz62zkvsWkUc6GJaqEsvMrLeZvks9bZcsNRrNBmWYu0xUbVKkeaalau6W22FBrMJaUm+3mstQZ+eos'
        b'2in4zs+zqTNA/tKkpplhwgyp84AammLTluv0GuUsi04PVRlMVkojTaxds7W60gI11zrbsNhS82wWHTlqSJ1dabWV6krK2Q+TwWir1ZWbUnMhB2sOZt4K37V2t+LOQHEN'
        b'7R2Vv5WOjkCURllgt0LDJrfOK+N9piSkag1mc61Gqa20QN1VlVCbuVbH2jE42jMoZ5H7JpuxTFldae4RV2y0ps4zmAylkDbVAKzmclpvpCNK5UxTzjIA7JBTpTYrHSWd'
        b'0p65lbOyVKkz1Nk6o8k9lceoUjM4nNjc05xxqtSZupXuCRBUpebBJoZOGtwTnHGq1Kk683LnlMMc0aDnrNGY5RSG1Tn2CqgAorLIKarwWE5njU8/RGZMTcuhaQaDpRRQ'
        b'BfzMW5Axc556WiWsjWPy2V4wmssB1mg9jmlP19mrbGraDuCcYo2jTcdvj3n3Fk/n3mMQCT0GkdBzEAneBpHAB5HQPYgE90EkeBlEgq9BJLh1NsHHIBJ8DyKxxyASew4i'
        b'0dsgEvkgErsHkeg+iEQvg0j0NYhEt84m+hhEou9BJPUYRFLPQSR5G0QSH0RS9yCS3AeR5GUQSb4GkeTW2SQfg0jyPYjkHoNI7jmIZG+DSOaDSO4eRLL7IJK9DCLZ1yCS'
        b'3Tqb7GMQyR6D6N6IsJ8sRkOpjuPHWRY7OVpaaakAxKy1U1RnZmMAbGwAEckZqLIAQgbsZ7ZWWQwl5VWAr80QD7jYZjHYaA5ILzboLMUwURCcbqQMg0HNyV2a3UoJSi0w'
        b'DakLyKlyC8yb1coaoFiP01iTscJoU0Y6SK8qtQCmm+YrhkRzGc03k5wymYxlQKNsSqNZOU8HdNGtQB5bA5oymylm3SvrJuPqAugFIIxIWtwjwVEekkb3LJDgu0CC1wKJ'
        b'yqkWuw2Se5Zj6Um+K0zyWmGy7wLJrEC2jtNlNufAlwB/wuJshpU21w/ARK6fie5Zra5sfCGmGoAcl7lFjE4tMJphNej6s3ZoUi1EUdILWNojmOAZBPSjs9qA2lmMpTYK'
        b'NaW6cug/ZDLrddAZczGArWvFbRZyqgyAKMOsN1ZrlDM5/XAPJXiEEj1CSR6hZI/QOI/QeI9QikdogmfrcZ5Bz97Ee3Yn3rM/8Z4dik/2wqYoI+c6ZtXqYDRU3YyRt0QH'
        b'r+Qtyck++UpzoTIv6bneW6N8l7d4D1bM9xieke6LO/s2mRN8t+zBp32TbIAqvWXzIAHjepCAcT1JwDhvJGAcJwHjurHxOHcSMM4LCRjniwSMc0P143yQgHG+6dj4HoMY'
        b'33MQ470NYjwfxPjuQYx3H8R4L4MY72sQ4906O97HIMb7HkRKj0Gk9BxEirdBpPBBpHQPIsV9ECleBpHiaxApbp1N8TGIFN+DmNBjEBN6DmKCt0FM4IOY0D2ICe6DmOBl'
        b'EBN8DWKCW2cn+BjEBN+DAATZQ1aI8yIsxHmVFuIc4kKcG5sS5yEwxHmTGOJ8igxx7rJBnC+hIc5jPI4uzrQYKvTWVYBlKgBvWytN1cBJpObNmJ2mZtTKZrUYSoEIminN'
        b'8xqd4D060Xt0kvfoZO/R47xHj/ceneI9eoKP4cRRhL7cTO5XldoMVmXu7Nw8BwNHibm1ygDyMGcmu4m5W6yTfLtFzTIUk/uU0j/FNpTxeAfX4AwleIQSU2c7lCtuhXuo'
        b'XeJ7RiX0jAIxx0SFYp2N8qXKPDtUp6swABnV2exWytby0SgrdGY7kBdlmYGDKZBDb2oAlVsRIyXuRj0r9rWZvdTvhSh5r7tnRqZi6p4dJTDfSgfLy6aylKY7Jpn/TnD7'
        b'TWXCbk3VEyE1p11hofpPC1WgWug5Dz8RYSfM1DijS2atMhltlqEuFV6YpzKPKuHXeCjzJKIg/lMuE0XxKzFRfNNOq15K6nGTldqJbI3B7fikKEWKceLaINLwH9Tnlar8'
        b'uwLSSkoq7WYbyA9dIVNh0bncoasymB735do8qgl/MnA6gEEF8BZUX6rkkg8AsRFQD2ShatguKeWBLGPg51/uQ0R+BWdpKsvNBmVepckUmw44yazW1lINS3ewG8ulLtAW'
        b'KHkxqkmj+NNqtNp5BE1zD/NdN4sq/jiHzxuamq/OKyk3kfuw+ibgStyDqVMNJkOZng6E/3SoXbp/JzgkpFTnTDCOn7KEBsfmdoptSs4WOYS/bjWVQ+xjzDoV+CAzbC8b'
        b'EwwcNbDmTEbIwH4ZzaWVSrUyzWJzdsURk2GmJZ+KpNkSvGVL6JEt0Vu2xB7ZkrxlS+qRLdlbtuQe2cZ5yzauR7bx3rKN75EtxVs24DJy8+bFQ4SWLwzldg0sMqFHJASU'
        b'2QbAmE5drNKuUXbrYiGSw7JTOapRUo7dKXdzpWv3MiqzorNSZ9rNy5kdrcFSBiiqlqIVGj81X5k0gRPaUmcWqhT2Fu+AG57kpcLUAiYQ0IFbKnQ00QUi3lJcoOKrWMKz'
        b'inlP5CD0jGLeEzlIPaOY90QOYs8o5j2Rg9wzinlP5CD4jGLeEzlIPqOY90RabMKzinlPZMsd98z19p7KCj4bUHxDSvwzQcVHKiv4TGDxkcoKPhNcfKSygs8EGB+prOAz'
        b'QcZHKiv4TKDxkcoKPhNsfKSygs8EHB+pbMc/E3IgNc9G7pcsB9JVA8TXxljTGoPRakidCSS+G/sBOtSZTTqqXbQu05VboNYyA+QwGyhb1K1udFBOivDS7KVUMeZCck5a'
        b'CkkU83YTZGVkmrmWs8T0RA+QcbbRBqTRoAcORGd7KvkpPNyzcDcmfzrNYiI3rQ42wSMlnZ3vlNqAK3EJVoySqBm/41UKcIzUQc2B9AOloUx0KWOfKyiBtxmMMC02l6Y4'
        b'A3hdm7HUuFznjv0LmCDo0iC7sxlcfHQ7SXRnk2YauGxhMBbTpCxYNXo0ZuWcjW9GzV07DP2GlnUme8VyQ7lTlc2IIOPiVMDF5ViifDGx1Cbmvk8mdpD4W7sSEvBZ0kQe'
        b'WbNyyLZY0hKEW5jBstYP9S2WBo0lW3qwskFOVnaZ4MnKtsnbAtsC9WJb77benKVt8dPH1Mvqg+t7l0r0gfqgOn9ga6UGmT5YH1KH9KH6sBaxQA7hXiwczsJ+EO7Nwn1Y'
        b'WAHhvizcj4X9IdyfhSNYOADCA1h4IAsHQngQCw9m4SDag1JRP0Q/tE5REMx62fupj79+WEuAXl0vOnor1Sv1w1lvQ/io2gLahFI6Mj/2dJYa0eKv1zCbOBnzwQiDsn76'
        b'kfpRrGyoPhbSZPUK5qERztJG68fU+ReEQWwv6NNYfST0qRe00VuvanF6GITUh5bK9FH66DoF1BLuEAPiuhTTqWX2tLz5T2IDlG7/nNFKjkO415BHjnaZZQQFiVH0DJ8Z'
        b'aMfSX8w6g8oCqqDH1LTmMbM7poY13dkt453ZLSn0EU+zUGOHx8wggEKDyq8rQKevBrRkKTTqu/xLADmYbfRniI4LLoUm4O5s5V2KEjvsG3PJqi4FtTs16kwOQ4zAUiMw'
        b'dIUVsGfLWdtdkhn5c7mlh2UCPEoUbiAY4PhjVjpT0VPOTf718vqAer/SAIchkKJBsQmt8a8NWK1wGQL5M0MgxVr/hUgvgektU0n/sgsG7jFr9F8G76ax1mBlzlyuuTYy'
        b'U4YSg6ZHkR4RE0He0FUou6doosONC3AKVQA5/MQcc6Uz23rUQP9FTgVUYHMiIpVGmUbLA9IoUTIzQKW9Sgmoc7xSbywz2qw9++Xohmt1vPeCJ3vvgeuY42v6kPx1ffAE'
        b'i4nKLPZNuzArNsuZ6uiY1XtfKKGhKB4IhEY5rxyQPkC/QWm1F5sM+jIYzzeqhduQcOkUalLqoAoI8/4rTZVAgCwaZYZNWWEHGaXY4LUWnWPwxQZbjYEe8yoj9YZSnd1k'
        b'UzEvvhTfa+HYDhOV0xy/lCVUTxjpOl100y+qfNXi3EoTndBqdS0mdRqstCgjua3KcnLfUgsSt6+KHMZRE5l4RVkRqIbDiAOzRBrKNMrk+LgY5fj4OJ/VuO3licqZNKBk'
        b'AVpdqdEMuwb6qFxl0EHHosyGGnrUWT1Ok6SJj1L1nKpvYDscxL0ViueGIUrSWtcWmR7aByD78xAgh3DDMNKUjS/OJg0ZpEUbS7bOpqak6Vkq0hSTYyxT40ayPWtOOr6U'
        b'npOdnZEtINKKjwVVkr24k9W7UBKMIuDrpaVFMfahMke9m0g93skqxm2Sp+sm28jWLNISjbc+XXXdqiCUmsbqXVPgj4BmLxQqi4IWzMlG9rG03vVkd4W7l1W6Rh2VCXXj'
        b'y1I0brGcNOJT1oKFzEWM1bKq0I/S5LAZyqKsf4Q9j+xTILIct+NH3kZNGqDWphjau2bVfLeO4TuWQHyYUGPDq/isMTrzNzLri1DTnNhJQ974uf/6uKDN75+5df3ull23'
        b'N0oUb/vFxo7IOTZiwLTxf4kIqH/pb3nfww964Z3TM6aOXXr8O5Vvmpuee6y8Ovvssvwh1zfX5v/t7+8cU0SuDPmi43bFkvD1s/7SsW3z0XPBy0l5+Fe3f6SvWKv94Oqq'
        b'J59n3tKcSfzvJ+jYLNXPzm5WBTEj7f7lY3FTt8+kBO8OQKGjJaV4f6SNcTCNmhjclMuXky1mSUWWgAaSTdJa3IxvMG8rGNY9cj0Q5lSV7fC3Ise0qC+ulypMA1g95HIo'
        b'PgMVeaydoMNNqN9waWCMzUb5qNol/tHqyHS1iOT4gNiXNKpnVrMGyBV8fiKUpsa699Y6FywcX5aQphGhzB5zENmFz0VrVKQRWDM5viiSW+RAImmOYs4Hg/B+XIebqKsX'
        b'DKRmBF8iOQqvluAHpB3vs1Hw0OArFtrHY3MdHBvrpmOFEYojm+Wa58hZViO+au1F8zbFRE1epqH5SAvZHk3zKa2y4CoFs1Ue9vwamonyfcmZFDDU0CbeKyGbjf68mvaw'
        b'Gjq/jvYoeziEXAcOcSC+LcVNYxdyK8mAf9MBrdtZhRmXUp4DrUOr5YKc+ZnJHd5mIfCkvmYKkabIhdpeTlLscmLJcXaEGZZSpzAL3QuWNPqgbIJlGnJ6yFCXzmdZKSt4'
        b'qe5KprpKsUq8+No8pt2nPDhaj/YPdTdh7dlVD0tmwfHHzEdpn1ajZdw6WchRCV2Bhd2cgyXCNW1uvkWTTLqKYr3u+V5Qy59ojW4tOtOeODC5oy4n1Y8ECqFXV5pNq1Tt'
        b'QpdEX1nyjbpWx7sWUOjiJrz1zJIOjz5Q3pIBP54M4z3gRbx04Bu1XMZbDi305CF8Nt/f1bzqmVzGt+6IY3X8C51E3GcXBrq6MGCqzmpwUf1v3WSds0kX8+yrySGuJkf6'
        b'5An+vfEqCp1uaL7aVna37ZOP+JZtl/O2gwrdxQRf7Y/sXvGvYT589MLDs4D5v4n1yOX/9m/5FTir7eFXMLHqJe5XW/mzK9ylrbz0U/Sj5jebPwh6ufj1oEMD0PMnpT8P'
        b'LVOJDBmT6+ToSsDGa/A5fvDkjrDxDrLJRqWnueQiWe/A2SNwqxNtu3B2ROyzfNL8CummcvdJWgefsbVhbmiMZeBl+j9dU4RrOV6AxxiYWis9fwO0uB695+F/1qNGVUCX'
        b'n2NjctN9udVmMRhsXYqqSquN8sZd0hKjbVWXH8+zqkterWOiZmAJcOiVFVwEldh0ZV2ySgB3S0mg2xJQrB3iXAbqzVEf6BIdg13e/SH8XoXSEMeKBzYEwYoHwYoHulY8'
        b'iK144NoghwBZBwLkL2ReBMg0vd4KEgJlc/WGYrrx4H+Jw/RNaWCG+t9AhmQSDhNPdMpye5nBTWqDmbEaQepRcmcGKoBZDTaNMhcAu0c9FANU0PMWY0VVpYUKm85iJToz'
        b'SDC0KEg/FkOJzbRKWbyKFuhRia5aZzTpaJOM4aeGk1YNHamRas5gezmqdAhNtM4edUDVdqvRXMZ65KpGGcUWLeobzMhMx2jLqcajZ9975I+06Sxl0IbeiYpoeSXVBVqp'
        b'AGJdYaezW2zRlSw32Kyqid9crufwOlGZ5kFRlIvY6ecSX8VoyxOVzHlh0de6MPishW+Pico89q1c5DCo85nfuY0mKqkmE5aKyZuL3A3qfJalGw8kVXgqF+VabL7z8a0J'
        b'WfkP1kaMMiMvV50YP26cchHVXvoszfczyKBp89QZ05WLHEeCS6IXuTto+G68Gw1QqZoHlLQid7Ngn8UBccBklsPWgO1qLbEYq2wOAkbhlPphs72VZrJWAvwa9F4VAgBO'
        b'NDclNyZ2Ow9bbI1yOtcKsC06Is+mq6igXm3mET71A2wzAGBBB6ocW0tvZPcD6WBaa4xA1gwrYcUdG65nPfRfTqXNwLcJ2/wGW3mlHjBJmb0CAA36olsOGxA2jQFmp8Sg'
        b'rAT67rUePiS6aZi6w8qHabS6dUmjnAlIzYmQvNbivu2ocgRAnd5+VGKCAfOLj6wG7yWLHHcfVZawnvPDkknlNluVdWJsbE1NDb+5QqM3xOrNJsPKyopYzmrG6qqqYo2w'
        b'+Cs15bYK08hYZxWx8XFxiQkJ8bHT41Pi4pOS4pJSEpPi45LHJ054vqjwa1QRlPb1dBUMz2H3BhXIZ1izVJlqTQ51zYvG7SDxjQLRdHeerNycxK9fOYUb8YZE+BWPcKc0'
        b'HrcVMHl+W6V07XpJGL0UJ6t9ZjiyU7Ur2T2WnNU6RbA5pIHeTZKpnkvdWudG4tuIeosuAOEevoDK4534ij/ZbVrJ7FTwHbItl3SOJw9BtKXynx+Skf1i0Gh+MVEF9KuB'
        b'dKqnaUCKzKD+s1A5vfpERMPwaSm5S92hmVYB3+6Pt5BOLb1q6XZ4PtlR5TnG2aQhB4o2a/Or4JGblUl2SxFpxBsDySnSge/YmRP+4XX4YWAu3qtRZeL7+GgA8s8UyVG8'
        b'F5/kvb1M6nA9tCLJgEoEJMF7BbweRtTG7/O4bSHHA9NrSUOshmyFhmNweyaIzA0CUs6SSclOctLOLnu4gQ9mkE5yPjg2SkBiujCO3MFn2AwPyPZb+o4EuBRlUdansqGI'
        b'NZtJtudZg8lucoNcxlt404rF4qxUiZ1yVPGj8CZrn8mQIThYQ1rJjSxyNZrslKD+qyT4IrlH1rN1JyeBC9sSqIHypGV0WHYGnRoJ6kvuSEOXhBvtA7uQ9QBl0M4I6h9k'
        b'B+C4MNmvx2c8+dVHOY9/sOn2lwFLdVM6Bqk0P8++EHd2R79J52KVnX9f+X5870195//i6m3/kfMmRj6xpLRrHwe9fnHcCymmrU9GPolbfORiQ86m7wlNbxTj0u+WHpvw'
        b'pjFtUMHc3OiCtw+ceTO4hbx6YurPb33y9h/2/fJ6/j/+tO3OmtX2yad/vjb45Hsdd5IHXd36xdEF864My7BE11xfrJKz+2vSnyP3PbQuVOVCduMTpfhKvo2eGcwnD/ER'
        b'LTlGjnvVREQnysj2sQpWGX4EQNDMlS/yhc7rbpjuZZSV6xjWA2C14Ca8bWhuT752JL7NVBUFeHt8dI46IwMAMVsbQ1pUAupH7ksTyLVUG2VD1+Dmydo0fC4mMh36AQuI'
        b'L4irxnlwp6qQf/e2HJ/OsQE6vb6Qc3KMZR7jZJnTg4QgQSH0Y0/3j5Td/KEQanu7GODuOhxqjGCuYyhATvM1epeHZTF9LKGPpfRRSB9F9KGjj2LkodXw7uYbyOvsrqTI'
        b'1USxq4lgV4s6VzuMpaf3kKk8WPr/GuPO0nsbkcq/K0hP7fkcrFJXMGeAnUG5roJ903tODF3+jjPcEkNXIGVXgEmkFl68D65hlgS44WKqfglz4mLq1c9uRevm7EOAtw91'
        b'cPdhlLsvDXPw9gGMtw8E3j7AxdsHMt4+YG2gg7cvBd5+u9+zeXudy0JPye88+gYc7Azq3cBzK4GMwnwBcwqsgc79lj/KPsQoyyyV9ipIBa5Z15MsVVYUG806J6MSBTxM'
        b'FKOwnMBSmd9lzkk76BKDe9RExeL/J4z8/1kYcd9mE+lC8RiXtutrhBKPfcnL8yhnBV45s0VfY+Hpszm+73k7jq3uiOPMrbmSam8sjH01e2dKayop92is0Jl8sL+LnmHj'
        b'CkKFdytXnz2mGIr3t7iycjntL43RKLMd0KVjYWVl8TJYeBD1vR8YmqkwlDIuLt6hEKOAAJIcrW5Rt/2rz064EOREZb7VrjOZ2M4AwKmuNJa4duMiN/PZZ8qDDgTruQzM'
        b's26Ru4nt10pstPhTUpuHIef/BULXVEONocxhhvP/BK//CwSvxHFxCSkpcYmJSYnJiePGJcd7Fbzov2dLYzKv0piSHwyfXUivsUPKuDGGjJNpQ5A9GSKn4AfknjYjmzTG'
        b'ZDAOdgi5TGUrLlJ5ylPr8AP/JHwT32b3xpJ7OnwSRAsuTOE2ctAhUOEtkUxawxvWLtZqMrOBjc1wyWw96yUHSAfIak2kyR+fJYfIISZkRffG+6252bmOi4xoEwvIDiiy'
        b'nTSAYDUOJCYQQqBWiLqTtxgfwgfwSX+EL5A9gTlkzxRm1TUFH8bHrJmkJSM7V0vvP4qT4o3kEoqYKgFu/pqWCSvFc+aX+lujssm2SMq1azLwpUgBDSuTyUCeucwut51G'
        b'zpP7geQW3jZXQVrUOdTP4bqfiMITJfg4OYIb+I29OxavgPnoPrIGsQffmDtbjY+JchSPm2QrZ+Sw+3oVM0iLo1sZMSoY4oElMtSHnJSQeyHVbK1+NljCFjJOfn1y7Bgd'
        b'YrIy3jMeP8J78OZAOULz0Lwx+JidSs74cHV5IJ0kmM9WcisdJM4WsovcACk0lewlTfgCRGSRbelUCFs8QDHrxQhW3xA9qce3Y0kn/M5AGbgTN7JbVce9gE+TXYVcKI+f'
        b'uYhlDoqrIYfJfrKL356K9+EDpr//61//Wj9TyqFq3Pykf0yZzk/jh8bK2Wl8XPX+In9NDLLTI0OQCU+Q9XRyWhzie3rMfHq1cWxmPkBEOmnOi1QBXKS77jFW4Ztz6a2q'
        b'cnNwcewSsg2fZdfHRCRY8sjuxEx8i1yXIIFcRORiCizCc7SRW6X4aqBjkeZ2Q4zCy/yAjL0zfIYU4fp8/xfwSZDMqbHgXPywiIvAVPydM+KFSLI7T+Ep7k7uKw/BB8hF'
        b'Oz2nJWdgYayZ6tzsWApAOUzaJZ1ZEqQi+2T4OtlA6u30NCBQvyaa33qjkvdbggLxI5F04mOj2fW9o+fmiq/I0cqOjArTl4EXwv6O7PQu7kHkznzS6dBzcKMKAC6yNTY3'
        b'e06ko7JuA4YUevEzOYzPBpEdIwezRiPX4bZoTUZMFDmGbwlIjreLsXg9OcAuuSXnq/De/rhVy+RE0SKk4D1alYQVHIr3kQ5WEreHOQqS23g91ys04EdysnFpd0FyhJxj'
        b'KoRpq/B61zBn4svOcZ5baWyc2yZYJ4PY1Ptv31my47kcMiVsc1n1O9WH1n21MwL3PaeaW+U3MCROVO0JS2h/665OJd864sSZqoJtU75zZ+4fD9lndCZ+/ubZW50XTj03'
        b'5LJq34GkH7eO2SAhuvcn7L58tysi/sAbkV9EL/8g49OonX8dtsrv7fY/pAcmCBOmZM/5n3MDPq76RU7tR3PtEwPOPHlr8ZJf15z97E7azG2mj97orXl1w2ebxiVEtj9p'
        b'Hf7n8hnbnxvwash1//dS9n96u3R/rebHy67s//2Y1sfbfntuys7BJeS5t3NX772fsfu387IviCM/CXphl3qB9vCUN4+9N/FC8A/+Wv/lzrh7f525Mq3q1UVr77auen2l'
        b'tXL5J+pza/dvfGJOrQw8P+SvVddSTLPb/EtjD244VBNrtcx5a/jfEqPuL6/+aM8XQ/7xq3Mnrny24Tdfvv6zLz4Ijm58HLzW8GrW1Fttj/4pfPamBX/3F6pgfrvuzoRZ'
        b'eD9VGDyloShF5BDTTuAOch/f1npRTdjTHMoJBTnNblsDmNiY4m4ZgrcXO7QTgKEv8ft+7+NruHEtIG03a5zQ+RLTWqiE3SR4E7fiY9FRzLqDbMJXEfJ/QcSncRO/JVAy'
        b'KDtaQ/F+DGyLcxSotolqQCoN/GbSuwI5QzaSDdqsKDkSlwjj8Sl8iCXllOAOfCErO0aKt4hIqhXwNbJjFW9zNwD8XaAS3KpjDNmPkHy1OBYfjmRKlQppWHqqwwCkp/kH'
        b'OTfTxhRqN16Aznvad2j9dPim46wQ7yxktSnIRXzNSvebmlIxenv5QdwuQb3IDgnuiMFH+IVkZ6VAXrj+ZQk55FDBPO//jEu0VGH/IY2MN91MCNVCdAvnTD8zjzIM69hH'
        b'DHJoZ7p1NPRiY66hYSGRmp0MhdQ+gpwZn1BDFH7zWTiEQ5hpSoDIbkLr76H76G7VodEJ4loVA32U0kcZfdBLGS1G+ljm0rR4U+b4fZObkQN4naWuig2umpa52gl2NdGt'
        b'1jHBo8BDrXMuyl2t42toJTI3Jowemntemi6r96tH7DhVqA9gypjAeqnr0nRZg3wTWiOvDVgtcylf5Ez5Ilsr93WUThsZhp7m9EI4p/fbhSLjHqYkrA6aN7gazWOxw8M4'
        b'/9cxVR9zL+IFxGgpUIUrZI8Vt+AromKFBElChJQp5DZjaPrjOtKeh1vmkZb87DnkBrlCTs8mN/KDx8XFAffQX4I3mLUM5880kK15pGVechxpTIojW6BHihUCOVYTyEgJ'
        b'uWLLd9YjIE1/WZSAD8wkjXY6zZHkOr6EOyXkIr8lfVIqI01avAMI50lyWkTQjcNoDIrIimO0J7F3kFYTl5SQTNHTbflaAR8hO0tZP0hneH40v4scn49wXUeO6wYbbX+8'
        b'g6y/hzxr41Qzch/kSOKDbn6o/ezslKa62T/fvNsPZN/Szstv50ed6Ez8xQets9LHDd3g99Err7z24a8XX5m6Z/Lv/+fL/8rp01vfcGx37XeDI5s/+/u5N9f3Cl5i+3TE'
        b'kPnijPiYgOnhZ/8y5cWU5wMTLg0fseDMG3nyye/EvVOQoUz+NHHba1Uhf7q153C438sJV2r+Frfnx1M/+kNexqBP2rXb/xj74Wf4xldLEt/Z3T52DKnUbDvqv+4Pv3ty'
        b'7cPJT+oX/kFZ+8fHMzfNG1k6PbL54PVDv7rz/V3nv/Jf+nnxvvuX6jr/JvnVrffOnH439m11zf3XPpN1fRV67O3ZrzYMU4VznPpgDGBUev2/HxLxCQHfK8pXVdjoDC8S'
        b'8SbAqWkzs2McKLWKXOPoqz0JN7swKkK2ERShzklnVhVy0uGBTodN8UCo6fgYI059yQnsoTsfjbdw4lSBdzJqYoWFuaDNiQF2b3ssPm8iDVIUgh9KCvH2RKbHxrvXLSNN'
        b'2pnAfdO3UkiHCsBAHuHmkLiTtBmdV2APxPedV2DHAyVipOo6PlvWffN8OdnkuHie7BvE6F0QaSrXUmvJGnLXYTCZJaB++JJ0ED5HDjJkL5ItEi2wnevJTndjSBS+jJ52'
        b'7CNHbZT/kweSCz1ILL43pPsA4PlifgCwF7dOpEatLtNTsjlOjkKHSpaaTIw+DjQA1XHRVtI4g5PXwLks1YpvQrxTqz8KH2JUZRl+xEaM14MIxO7Jx9fX8qvy2TX5wHpt'
        b'4pehbiSXZa47NhG5OZRdskl2yXjyvbkqys6RbbkZMtQbn1bgHWIl9OLwN0O6/6v7950mN/y2fUafSrvpUyylPszgkZk9SiltEkX45rQqCFAz/0gZxeLnCjTEjSQVrnTX'
        b'533pcKkYIvYTKRVzN8DhHeCUyq+bRnT5cQ21tUtmteksti4J5Pu2ZElmqaK/zS7qU+kiQYz60OtfLwkOVyVGfdajnyp9WArxjv4HLbYcDiBPfttDxcD9r2xO3w+Hqtbk'
        b'0KBYDDa7xczSKpQ6ehLgppD5Rlp05XLDKivUU2UxWKlNJNf0OFRXVpf63qH28ab9flqzb+L6Mtqd4lU2gxfNlAcxlbtPnJs9vZ36lpG2Ob1xE9mDt8PnCt4KO2onvraA'
        b'WYhfmIMbZCgCr5e8qFzAz7MfKvFBEC47esOSapBGhi8yVcQ0/IhcAjKrWIGbFqjJHq1GI0GVQh+8VYLbx+INjEJX1XK6vb6/Lut3qbMQFy8bwse5CspHkN3F+AE5RU4k'
        b'oKhkWdbkFHwIX7KzK3T39MYHmcDGpDXAvh0gsZ0nJ/g7gs4BInjgosK4Dm9DjA4DptzMuh61YJJTnMOd8SAKnsxnlNiPbJ2Ux0m3iFuE9H6DE/E24+9bXxGtGyA5+Pv5'
        b'2W8MD5kaH1b3/v5f9Fspz/hS87L/DkUfeaD5T+IP369Z07esvDJzWlTVrqyvPt885f3G729JHPrqPem0gPMR2Yeyp2UvCVWoL35sM35Q9dz7Dz43DPztjb2qa2O1iRv3'
        b'/Cv4hzf3z+msGPQ/v/zn1Bf/+pPbQTV/+Ozto6H1q1e8F/fco+vLRn20s49Kzg3XTwwh17gN90j88Kmz08n4ACMpxXgXcDGum4KX4r0zxZGD+7M0skVGBd5sEYZ5DuT/'
        b'U4IWZIt9DPVOJXXrgJhRvJyhLp0lokCDCKzTkTWMTtREAEg8LTuglaO56EAOJDGSJZA9KDoMb3ERJQdF6ot3qORfgzp8mCjqrIV0szF8OaIbX5qkknDOocM3xX70BDbo'
        b'n3JZH9ENhTgK53yt/aIFHr95Ci8d8WHB6Ki0XeiSVuls5b4vUJ+IHHdV0/NI+mYFuesSdekzL1F32Bm+LxG8nEV2oyqKNay6avrLZHJHWt/cVY0OYKIyo1QZRX9FKQHj'
        b'WrnWm6Ijw0rqAkuVwFGaWmNVVAxryIEXLd51yFZ60Z/epbnWWUrKjdUGjTKXKtprjFaDC/exOtgAWHadsrTSBPj+axAZXS6XS6ALkSlymGILPwKhe310OmyM2emkGT/E'
        b'G1SZ2Vm4fV46vkQaYjTAFKSTLX5VNrKPXyVfT26HamEnZWZryNZ5+ChwafNAem+KnQMsiDoSt0uRltz0w3tGDOPs93ryiLSSXfgCsOwXmIOHxCTgjcYajht3kB14XzSA'
        b'wMoZpBmtJNsUTAKoxA9GReeKSJi7eAYiB8iRScZ+aLbMeg7SmlZufy57QgiOCzu0JHXK7emte6d/4Ld6/ewpvSZq01/6rE+6kHlv+JvV6W3zPjn6QUr4L94b+buA0Vdb'
        b'P/vpriF/+fOIAUm7bhQ0d/UavbdzUXmvXsr5Y3tNtI+5s/TtLZ0bfyn98q0XXgn5/fnfvvTyyrff7hzf6r/k4LuTNlYt//KHxQvXrX77h5YpdevuDf05nnAr/JMJ16Jr'
        b'11Zu/Mv8d4zxv93+bvF2+VhbYb3k+6+Hvv3i+AWvr1GFMhwSm42vRKfjVrwhhnJ/0vECvqzExzmDtWFIPKAeM76cw9+ihhSkSVwzCF/jHGtDkpp0kus1XPuyH18XkT8+'
        b'K+KTk5MYDsoHEvKQevfAiojAhm/HR3LEwfhivNO1ZxOupy+Mi9FkwGMO3gRYinSI5D6+u4a3cItcB1Y1Bm/Lpe8NwBtIq4ACp4hk36r+/CUO20g7Pk/riM2lvj1k24K1'
        b'YlQ/fJ6xr9G4jdygFEKlIdvZ8ELj8B4gYGVhuJ6Xr494oRu5kjZ8eak4ktRDKi2fgY+tjI6lBw1qjUoE3HcU78A3JHgzeYDvM7kDH52Yo6WOR7EgusmBqW+ZJPZXk7Ms'
        b'0UquDdfiS2EyB6j69xHxcdJRxhJXqhOovOKcmhvk3lQxYgU5w7q1Jo26qJFGUq9z54svP8ckpP7lS3mvoMkI6Mo5MQafH/AsTc3XIGs3BC2lG9jTGoZ+/LmuRcGceYKA'
        b'V3XqTsIgtjbYhUxpaY6e2x2vFbAhD22I7062izxv9+3y1fD411NYfFM/j9cMeDSscnhLz0DUv97lggzYxPFPJeNfIvz1fuqqKWo9r68sKSxkPkFdiipLZZXBYlv1TfyR'
        b'qLk8M7Bh6hjGFTMSxEbAOfM+/3Fd2TPX0UJfrPAhXcadiF0iIA0QgEtA4r+kInJy4P/qM1oEYUP8Si75lt/SEEkQr+/pOqHWfrFBghy5pXa/meZfg+cMHB8ySCEwi0JM'
        b'zzQ6rBlUnr6itoaESFDwEJEcJ2cXM9s9wC37KwPxORtFPoH0jGX2bDXeTs7K0eAE6Ui8p/g//Pojr+4fPU8n/XLYu/LClo6g/i7DQdi+g4bPxFeY5ghvggFs0pK9vTS4'
        b'Iy4ZypObworqPmzEaXPIoejuN8/RQx2m7iGnkll6ETmfChzcdtKUEUMZrkQpUuAmMbMCdxr/UbVNsFLQfvhB0ydFi1/q2HF8V/zmFUKJ34fimc1BgQNSt69Ni/ldnzN9'
        b'frc5q2icNiBwYdvx185sit98fNPx3Rk7hVG933hpvxwtm9yrYItOJWMaFXxxYVi0MNTNtzHRHsmF853AstPXeTaWkt3uSOg+ucyK2vITowf24bpxh17cWMuVMQ9Himhg'
        b't2TOxPJAcoTTlDZyGZ9dQm7RI1yevEQ0APt78VmuLUEgaQGLYyikBg0MPVFE6EJPo6hCl6IjKTwtL7p2nbRLSgt0yR3OZj3euUQvi7Osdu0aWnK46Kx9vePzvjvnyE5g'
        b'8Q28c3h0ZKY6PSYTt8TSA9jCDAEpyR5Zn6p+PUCor+Pb+qX71RvR9PoJgE9RL6nzL5AYpOx9dIi+ia5FLJBBWMHC/iwsh3AACweysB+Eg1g4mIUVEA5h4VAW9odwGAv3'
        b'YuEAaM0PWgvX96bvstPHwN4Q9H31/aDtIEdaf30EvWpDr2ZpA/WDIC1Er4FUOXOskeoH64dAHL0gQ6iXQolheiW9FqMtoE1sk5RK2qRtMvrRDygVIY5+S1zfPJY/pTyH'
        b'21P69G/98EOhUFdAdz1Pl9GP6Bn37z31Iw/11o86JBb0MoQbeulHD0DHeh9HmwQWGuMMsRx9mHEidzlSwJz4OS4D6cvMFv3YPMn0Kn0UxPXTD3BcAeJfCJRKNxPYZOYA'
        b'3kP77ilkcANIOXvboNylc5d9rc697Ju5rwVwnfvdabD3FPek9CWBD9aZ+Tl46MRmFNE3U0Szi0KM/ZfwyJs5q4W/j1vlh+J0Lz7JF5CdXiZCTkpwi4fDO5Umgb1qcEmU'
        b'FJH5obwyRRhImwf5m4PTR6DpKd+FfVAkvpfTF/3e2U3m+WcMP/tX0UqHkFvfPqT5avD6uCDpr7ZNK5LePPbG0KApJWmtmjih187/Glj/u88Kax+0fk8e2G9R7m/8W5ZG'
        b'tAX84PMj33lzxrLq+vBlDxee/lG2vNCvZPN363//y+mpH/4wza/sbduf35lztbhr8rnDAxZmXVf5M24Kdw4o5O/pUUuQYl7tRNFmxG0sqQJvX4Kb8JWsbHJwLGXTxoq9'
        b'JvK3gKYCbjwfqF1DNrp5pjsOHx/FMxlbnzTyKRG7z3OOKRk9QFauVTIlwBx8Yyr1Hg8shZmMVPN5gyz9B0sn4YP4JKtKhw/TVxDTTsKc0/PAZnqAd5C+AU+Cj1fP4g71'
        b'd+ZHdWfKxhcR5Nmtxccl+CT0s5Wxllk5RtwUCwxrBmkWgJ9vxB0rRVy3doqNXkhEdpL2wbipBsjPtRcyGOGFyvD2XOBFt+aSbRo5mqCV4z2KpRzBfmPGsttRfKg74k6Q'
        b'CwEyhRDBHMYdGlOhNty1W556sSLXb3bJmN1Sl5SavXYFdR9qmSu7/I3mKruNXcvVzXS6m5HLLBvp7/X0sQk5+c0NHv2M7UECfuzBdnrp37fxgZYV0o779INNEx27wb0d'
        b'lzv44O47RXt4w2osWopcvoVnbnCh++z57NJ0Z5eeDHVrvqcnuObbTENAYfda+Wp4lqvhIRnOzE6Ly2/drsvzm4JPYYXRtyt0pqvZflTCUJZaKiu+fXt1nu3pVvpsL9vV'
        b'Xh/WHrXH/batOVZUXmirtOlMPpua7WpqwDya0Wm367O9/71XtVeyJKKeLxBkFKJymmTun+mxLyqKmV8TyilQ2nN+1XUCc/0xLRoUiYy6aX8SrVTZfaRr3CdvvVT0RnG6'
        b'rk0f+TutLqj0o6KP0JcHB+Tte2XAxgEpPxaKbso+7vOuSmAYLpc8IBcYhnOgNwV56A3DTc54Bj/KJD6GzdiLz5zYbD5lQGt7uWOHb+5vndcD6Vzx0Fj2rPbxv+Df/zci'
        b'kGOtFveTobCiv0H0etO71S3L2HSkWlpT2ksYlAoRPzI+l3FNZqWvi1277SR/9fAO/cKX9uF9+PqOdskbt3TsTYyflWdJ0LL78g0auUpkC7U0YoL7MrmvEX5AzjrXqQZv'
        b'5y/ca8GtTF7ZGqVeits1VCTZKCZWkXvPkitCC5ndsbHWUFhsqixZ3v2ePOeaLq4d4Dbxnrk93uoqYwazPUUMKoC7KTVa4bGwx1Kf91hq3y167EznalPAcr7lVQLrLfnf'
        b'vtzT28kSW+8/Lfqb8KkERXas2y2dkrMAMePLgXmDBgF/cgEy16LayOeZhhTfVOMG1Tp8AYb6InpxGT7EvADDdas5yyhZ1m1yOi8yRy2gJLxVHhKF65iNptnusPyd37Kg'
        b'IDYIMYPDIaYcanAYKVur6/3ziA965SM7ZZe1/uSI88okD7NDx4Z2GRuS/avphUnHyf4AcoAcw4cYHuTOjcdeoPcuUakbGL66bsnbYjT+I/+gYN0KmUa/8sfRb6aG4LgI'
        b'SVHq9qn95/8kNW5+se438jdiPhoWtv/AvKzHU/c25I0aP/r4wdH/s6v35dvr+k+vI/rwkfMDDvufbQias1nXHPaH68PKGl/4b13x3NjR1ed+nj34R83rbp158gPVv/bd'
        b'+PSr5buzhR9l3bwW+961hU3Hv/pdzhOcmLRurmZf86+3fPXfkl/tGNH80usq/kLj2fhKXsmCp/SbkrJAJRPgw1PIHo97kxBpD2AM6vMLbRRz4n1pNl87jO6uRLKfbrCo'
        b'Cdzc7B45RDoCo4CV9Ytnh0HOaofhTim5MpLU2+guH6OOYbYWlI2FFV62HF8EEdlZrxzF4fPywXhzb6Z8LiDbsrl5gKHb729sIVcUnEsjp7kSgZwvd+kRaskRlev12T7V'
        b'mPLCGovR8RJUD4azkJqIicJQYDgHOkzHgoTaMLcNxwp6vq9ZZymz+mAnRUub5/7eRdFij/19xuPVmD2ayymRum1Bj8Ndx2t7mUec67W9UnbiJIOdLXXtbBnb2dK1smdR'
        b'XVmPnS3P4ScdF3P98S4JwhftaBgs6T58nEmqXKd1vhdpjZ6jnq8mDwRqQenXSxyKW9OM7w8ukFqpMHhg4WSqk9qB3335vZc7dtzZdWfTnZ9kLozZrNo3fPOdTe2bJrRk'
        b'NA/ft6FThi5OVKxqvAHUmNq0DBmFQBqh+hO8NbfWYeohoEHlUtxADoxxLsOzddbyQuYjwRY7zH2xTSHMvsJjvllWrqGWu1nUsRcuM22QJwJvl/LYp3Kypd4ND2OPpd4f'
        b'7mupWdO+V5oaT9fLYK3lTJFA19vvW6z3N7y7RpbD15Vuv6Iyex4sKt4jkNP4EZKQe0I2PhVuvLv4lITdzxnyN+0nRVrda7+L/CCDM1ZFnxQZS6P2fFL0uGh56af6T4rE'
        b'xrhxifZrp+PsHdUdp+O3xksTq24iZKsMrn297+kD3SzoN7I48XjLNlXduS1tH/eltSi4UQ013+zrNsfdZXhVe3wD0F7XQu6DR2WPhdwV4b6Q3ht5TLX+vpc0hW9emWP7'
        b'yv63y9lz+zqXk2LMVHKX1MGCkt16fDsxXYJkfgLeiE/hbcZzA/QyK3WPGKGxfVKU4VrRdN3HRRrdR0Wfwqo+2PdpUZiuvDSrJLyEvxv73BBFv5ZA2Kq0zefW4EPagACX'
        b'ofMlcvWbv2a3K6TQceGo24J68M61dEFrI9xm2aOAU93guQ+75KW6ElulxQdylloO+tq71Jm/pseSN/VxX3KfnVGFciPdbptdaq7bFdwtSy83rOoKrq60l5QbLKxIvGcw'
        b'oSuwhN7oYqDvSo13DyR0KfRGK7+KhZr+0pfF2+jtvAa7DSRIepMs3ZldQYaVJeU6es8pRKkU7KTLQtkhSyp9eLkHmJ55FbAaqZVSfFeA88oVo97NPX0Ry2Ez2kyGLgV9'
        b'0wbN3BVIfzndvlk0u9OJ1ZRgOUHL+FEPxOLKlcw3vUtWVV5pNnRJSnUru2SGCp3R1CU1QrkuSbGxRCV2+aVNm5abnzOvSzotd+4MyzXaNPXq6cHg0pWlHJqVXt7puClY'
        b'zqyThXpFqeJbsLrlT+8oiaNqzx1Vwlnd72SsEf4uvhuN4nSLjPnTOMLElwbPsZKboRbcSS7KkEjOCFF23MSMmfDxzFirrRpS+00iNwIF5EcOiCH4kc1Ol6YUn0qOpjaS'
        b'lyLTszUZ2XNIQw6+FEO2x2bOSY/JjAW+FTgrFVkPwil3ISK7FgVNC1vGnVcOk2bcgOuBo9o1B1E+OzsZX2CEW1k+KDEpTopw20hhLMK7gIBygn6abCJ1iSLKwMdRIkrE'
        b'F5LsFPzxpoUjoYAIlJ5sFCKhXMkIfn9H+0Bg+Li6cnMmdEZAgQUiubzYj3dhN27Gl6GkHBhHQVAhvBvvX8TYg9oXCfDO9HaRZDm5Qt9of1WA3g9k85gzPArNQx3VsrAi'
        b'cVNoBOKdeEj2zYe6BJTVS4hCeE8JaeA2X9slVv3zWo1aQz3tstWkMUtA/fEp6ZSReBtflwQlmoLe6itUFS1epqlBzOBrMN4YBdUB+/IQ3xRioIcF5DC/2OMCzNu9aHrr'
        b'SAY/blLDCuEWSTG9AYPV+PzQ/igGofJAZdHg5ctf4J5rkWOqoUI/hLdbBDXC+8mtydxk7VE07gSWNAa3i8BLI2mMgO/iW2QXqyoBoHQ1apjpH1cUPkG+1DHYe2S9IjEJ'
        b'dwAUKAQNwgcmZbB561dGNlGD32yQfvBu8sA/XsT7huDbrKpBqkzUhv6+LCCsKODRGBsf5+p5y2lFUkTdF4VYRBXEvfnqdcCCN/MLODKmUxs/Od4ijsRXi1ltZDaVp9L7'
        b'yaYUZV0tHMdrm0QaVicmjaNeMivppO3GN/A97im5YTW5qKXXszSRbVpm+DUtPATXSZ4XArndX1QKqkKRaWJRUcJe3XLHQHcV45NQoYjW4jo60L36xdwgsBVq2sLry2EQ'
        b'hlunMQgbiNukuJHer8q9u87lLIIKAMQO4910fPvwFhUT0KpjcJujAr6MUrI1pEqSMhVfYh16XB6ORqEpfgpUtFooTuQDhBHVhyUmAMiWkFt0hHv8yEG+jJfTBjhANpTc'
        b'EwFkrwmkDTeH83I3VRGJyXH0rh+yS0iAcvhSKt8F6weS09FaZgx9fKyA5EZxgH84G/1afBtvThwPpWrwRiGFilczuI1R+8wqDoD4poE04isIBU2ShOGLCXzMu8kWfAMK'
        b'iii1TJgI4BGMm1nB2fjiCi0/PUjHu1T4vBQFhUn64m0L2JDH5tBriKsihKKirHLpQL4GmaQ1OXF8EozhVBWtbL8Gt7MJDMQnyX7oBnUv1ML0HgIIKREH4Q68gY3sBbye'
        b'nICSAFuXyR4hFfpBtlezHiaQM/icVkvPE1T4iFgpTCHX0/hEbSTNKVAIsElnX2ESwKNIHtkd6pjr5IGWorVm+HSQJpis3qL/oHUcHhW16M9ox8rAsKJ+I6dNdGDXa4Dl'
        b'LuLOuCQZGksOCVMRPhpD2ljayPQVIBwAAOC7yyTAqT4U8EFSb+Q3KafMRM1ofd9QZVHm21Idn4glk3EjrUqClgUI0xA+hs9a2M6uWDdNC2gFEOzeDHGpEIsPlrBa3pBH'
        b'oDh0Tg3TOTj0RdhwbL2vA0bepaWHQ/gsAJ1UwEeLZjp8WyWAo3bJkFFOzWbxdbyPWd9OA9TFHL/mpoPIq57Pzc+CbKQhOwZQEEKzwv0GkZO4lZ8kbycbyGWXiykgglvk'
        b'hILsEwEhNKq7b4t+UkMNbV9KDEBFMUsmZXMkVULu4SNkFwxlSxigsBhyXGtnTnTr5+GtWveTJ1gOehwHJEeKRuPzMvtKvJ9701zBe9NJ0xzqBzNIC/gsXFgSTm7yTXJn'
        b'HOyReaQFqMslfEIg+xHpAL7vGLfOaMfHyQE3d+lzmbw9AY3OlRl15Crro12Bb5ODgQi35gB2hv9rhjLz4pmlS6JhYrLJtnR1JmmS4aNU9IuXojHzZAm4KY6NenroIJSE'
        b'3hoohhUtHqvPc6CZfUPHUNdtsteCQGrBjybik3YqTJJtE4vd6xw4mFUpojH5skTLPLagK/Bm0qadQ+nrgV7MEfcB2Tud9bQ/6VTlAWFuydYBaX9RGBxh42B5m5x8UZvP'
        b'pqF1OohKABUFuI75WeNDSnzZ3RmdjZ8cmjAMN0nJzVHBTBk2MRbfJAeDKXOF78P/hCS+9u1rBtP9rcnIgWIZpC1enSBFg/ABqYm0F7KxzsH3leSgBJHzeAvCD+C/ZAAr'
        b'a8A7h7mVnVqgThCh6EFpBeCTi8w+hXTU0NNGmOqJyIiMS3sxPFCRpacGkq6+gpzdFtpbsoxsnMHRUXtfco5qAgC22pgqYCPuYLo7vH4ifhTN7+8izdrYDLIPWALqej4Y'
        b'35CSRiXZx2oA6rOAHJQhclQBtI+Sv1OwQHQ0AGj4MmkSYenkaDlaTvbjTk6ld5O6FVq1OgNfjMykdm29p0jIHnyItJHb+CIrOxnfXkcOBqFQcgjh6/A/hBznVkQHyUOA'
        b'djf/zt6DqQsK2bSYKy/q8RnSYA0OFtEyfEuAHUguAeRuZwD2y4AA1AelrJSEFWXZkvMRmzjcnlVEmmAGTs5FlahSmMTg3Qa93Qj8Wzp1S2/W5qpZR4FCNCgHSQHBHZAx'
        b'JaW+YrTwlqQjUoGmmH+xcv/MH/E6y55PphrSDHKCKknJjlrjr4d2Ctb/AXZ3+tlPlrz9X+Yfzw6T/3rCq9t+fD37gy3hxdXff/h5n67wyLY1Zz9ddDvCX5WW3+e3b98Z'
        b'rjwcrf+j9PkrL5EvFJP8Ho09u+c7M9re2f/G7yd8+L1D8Wl7F/7lz8e+e3fYtfEnjiecnrdoYHRv24N9I5b9KP07y94a+uRTq0r9ne+fH3NkXV781c8eTw9ee1AZ/IXK'
        b'+pLhwm/fafvRmVd2K/bnnOn1w+mvdP5s1+3G8dkr3oy6nOo/43fK4LGLpv9u+KLDSTNuphXkjGj9w44hOdWNn278tPraLH3l8S+fb5W9tnas3/SQqeNSJ42y3H7r/V6t'
        b'JzdPfHX6tmk5KRNUlvOzf3/9tf0bD/Wd4Dfh899sfG3Ga6PHNo3YO3zBxbLf9x297MPtf4z7zumGrFWHsr+6MvzD10/pst77+/GRmdH3TT9d+K9Tbywo//J6asugw49X'
        b'bR36VtWeBdcG1c3rdWtx9vTnpt7vGFBzvmOgXvXDc39Z/cryVTPfLCr5+7LqH5789IjEfHb06ndK3nznVNeCpTm2dZuuvDrw4I5/ns2/8Gv/X+34wYLOzmz9X9etOFjZ'
        b'eCk7yD714egyc0lIjT5h+K/63hnf6+Hkx6MPf+j3X6VfTmv/4tzs96/+ZvL3Pp/4m7Mjfmhp/5O11Z76Xz/bUZj+j4Rf3d9R+M9bwfa16i/HTP7T/A9q/vHLZV/92vJ8'
        b'4xrcHlL7z3+Mnn5z7kevnzWP/FnTqfYfFxWc/f7f1kWp/9k0vlLV28buYbiHb+R42ArQGwGa3YwFyMN5zCJhNvB5e6OpuhywUpOIDwjZgfgWdwbYX4LrgD0CqcI0UY6k'
        b'0wX8ADc+x12lryvwCdwUWhVkIddxS2i1NC/YX4764KOSypXkJs9zlWxPC8TtMelOxW4vclcCLOFdQPnXpUzjDB0C4kQNU7eT5sUrnSZhjan8CKYVbzHjpliHbSrZv0ZB'
        b'Toq4KUPFzMJm4pvLmGqY6/jI0VmKbFE/ZynTLpBHVQLsKRjXnjFitZBG9sfwOs+QR7jF4YJNWhc7PbDbJrA6B+NN+CajtqnkkdPN+iBu5TNyRD6dm2/E4KZybr5BLkQw'
        b'+405+BzINqTeU0PO1OP4cjJzGxwNXNIdL0YXEnxkAD4OFV9m8xaPLy7oaXUhGUAa8EktvsZU7eQYENBT1MyDXtF4mXQwyYZaNTsmI3qCDN+swXu4qv32aLKxWy0KeXDr'
        b'ODe96B18mGn4K8mGwdFuvhnk4gvcYfA+aWEZhuK25W7GHnFkt4I0irgOUOZ5b1fnf2sz0y6JTs91OSvh4dLlrEOacKGfIBXCmUke9bgOgz/HRwwXenxo3MeKIWHCKOqd'
        b'LURAGfoXJCjEgYJSCGFlqNUxzRvG8ocJfSAkfqroVxvcraiB/rjr7i1UFfdtvd5EXqpbp38dHuepsoiCnEtZtB69O9DDGNmjF77P0JlSkL8zCtXLXEpBgakwnn2SXuft'
        b'tE6JnlZhjOUqDPNifiWLcprBtGtUGuKaQsZC1eFjmXgX3jkRxjcU4OQIaWacSvpQfBTvIo30Lr4BaEAIkH52mrcfn9Un4p3UfwIloISZs1kDc9exF6HEFQ2qCTrrvxax'
        b'o7t2rYJFrn9uecxrAzI5+/rdNVSbghZO6bM69WbvAk4Ti0hnSmKStKQ/ldRQSXUSb+tI5NzEJHmGlbqfIgPZF85qmGjmF7T8uqo05sq0EF7thRr25piUOHm5Kb9GyzsQ'
        b'uZhHrp+3JugXq6bxnMa0IPoumEiUVpE1TTKD59z7IntBTGTHmJUxw0J68Zw/G0RZAqR4qcyU9eXUZJ6zYUUgi5wdbjIFT1vliIziXUJltUHJ1nVcCQti+CPSDHzkWmDM'
        b'8im/LasW8N1sfIwxR9Pw1tHAr+xIjIuTImEUwjsDcANrd/eakWg6W9RVxY8mDUFsMsitxVJ8gWwdwg9XyclCxsXiU+PJAXIQ5Or2ACquwn9yLpY1YE3DxwADHsdb5JBy'
        b'C/7jIwPZdIfjjTPIrgl2gBk1UpO9fLiXtfyk9aUia8wvIvT8OBSfwRsUZBewZfCRIQHfeYEA/3ljPr7FlUtN5DDgt10zs6CyIWjIaJAYmN7gODm5kh2jniG33Q2YbfgB'
        b'B7wt42QSvzw1ZdME0iqEk9al7BCZ3MKnn4sumEtdbdDKVQFcvGzELUB+LpCjmBporUKr8DkZm5dAsplswBfsNfx4uRe5ys5y2bKsHMDv95kSvdqkn5TI9czRqWtK1g5n'
        b'O0YgS4yffPousiZRf6xR+RWtqfRely1l1X8Y9YMfZwyuD/tlFZoePOQD8Q6O3XDou5bg3Zt/kzDr3T/08js2fYLsA2nDtLilY1+empT6p3X3/tSluv3WhE17owKP95v3'
        b'UV1zeeTJY++/3P9E7x/+vXzhzN5/vlj62wvyAu3hX4xI//wtTduLP50+dsGZzdsMZyVbP86cV9n/9K6bHQ87Xt6yynD50OYtU+uTu1bMs+j+fPbjeyuX/Ji8a7m7peuP'
        b'oX98MuirFz4sbHi78kf5eyV1l7XtY+v+T3NXAtfUle5vbgIECJvivsW17C4oKrUqCla2iALiVjGQBKJhMYugRZFFARFRQQFXEBVwqYBi3due006nYxfr66tjprWjrY6t'
        b'o1NrO/bZzvjOcrOSINrO7z0jJ7nbOd8599xzvu+e7//9x6xcfqtaApIrcndL37s+8qPvD/tLTrQ6DQm+tl+y8QdN8b/a33za786k6XnT3lTNmnRK1euyt0J0esnqnbXL'
        b'E28UR0zarhk2fufFrVf6DIy+n7Sn+sMjtSGfeknurc5W/Mn5m39+cN8rL/76o+N7t9XdAhmvfjbhlauFhSVDvgspSq/r7duXOGiAosmRndaPV4AmK0caHHeWLLGfi0EK'
        b'PV78hx29JIF+2Pmwg0XHyyeSmV4Gjww3qBZo3AIt4BxWLlzQZI6H3WjQHISnWbADnOBcNVmtEB4l/pF8V7gRz66x2BbFQZAx5B1shpvC+MjgOArXU13iHGgdh0NLYUB7'
        b'WQosRMrEOnYYLBpNQs/A7bBKA0qQ3WEFjDSpYV4oJ6xZ+Ksw5c+cSH/8KmIPevje4IH6oYNIKTxwEtRSP5Qg2ABqOEeUSfAMUReQ8VGaZKI9wi844QHQzvReIBgAd/ch'
        b'uKMMmc6MzwilqDbaCSMxhL89kggwCFSs5VSbXqCMqjauSC3AJYyQhHTSWsCb07Di0jANFFLv/mOgvLc/qM20hnaCw32omB2+4621miXgEFJsQCPcIiZiugbAaqRezA4I'
        b'CsLvsZGQGtTaLXw0cJzypbls9kTPLuFGMvNt7TWaeLeq59KYCRXOvcgpW9BIJBirZXlgnw50kD4zH2wlCF9Qg84wYQnALnhI64/zLxmGrDIzdwMLZ4NY0MH5G8AT4bQP'
        b'No1EYwrSUIeBjVRJpRoq6pmEpQk1+QkJp6ZhFQ2UgeZOalquH8WmHQctCqJdgX3uRm9apF05w4O0Ys1Z8f5+QS9lUnAFCSsEtw8zeC90a9lMgL3yiIKVbqlgqUU8AWsI'
        b'I+BN1Ctv9OmNPn3RB2+7k5AC3uSMHtwf+dx2HMh+4zgIh8gRsS48b0bwVMjHa6kiVkhgXmvcTaoMFsDMf60LqU3ubB0oeWBDX6q2WF6zKgS1C9ZP0NdW8iUh/9V1eKOP'
        b'FViLeOmq1+CEeO4Sl17szasXGnw7Db/w+hP1iCQoLex+RXw0yOo9Wfkla4F6UXJc2Lyw2OSEhXER8Xq+Rq7VCzDKX+/KHYiPSIgnmiCpHlUyf3sECfU6lASwBqAW39Pr'
        b'uaFYDu4Cdzd3R2+hp5MhboQjcWxxtPw8FPTAxwz7Wevjhs99wQNHP3ee+78dHfqGk2kdtL6+EM3nLeajvQPjmcBf5K7utEZt4G3RTLXmmRVUexAeVg/Dt4w1/uJXOMlG'
        b'IJ0YAyg8FAKZk0xoZJ11lrkQ2IuIY511I9vuZBuzznqQbU+yLSSstC6ElVbEsc72JNveZNuFsNK6EFZaEcc624ds9yXbomqBgsFSyfrtYasdMbBluZusfz+m3h1DQLjt'
        b'AYbtPuivht3Ck43kkOFOJGiSa4lHiafCmXDXEkZZdMyZ8MMKCGRGuMgTt4ZsaAWvhNoCohI3ZAkMkw0n3LFesoHEg2cUxx0bLYl4stMCSJ1g4DRFhyhxrNgHk4Fgkidp'
        b'pgz3faU19aTFhl8CxnNzvE7oV1aKJkuFaacxDB3H76Ukmjh+sDxbS0NYE0y6VVhlNXZQ8nXSO3MEZZjSh/tJVo6FNKQoJveRKVbp+Ssy0b4MuUypy0D7hNlI8pwstUxt'
        b'Yq+1SRtrGZ7KECHcGdlQLtyCsKsxPFV3iGPTfQU3H3abOBY38gsTxz6bN7YTR6xNKP4L8saa3QyjHDjGeBdSoMP2ZMgUS1XZ6dJAW6JMFqemoyJTSSTvrmlsu2axtcFY'
        b'+xwt8kwWW9QPadDj8FnzxSppCuZKRz/N40j7BllFaKZcbDalsBSdtK3POLOmsCE8Jwh6Fp7BoWuPL9d2rAZ7HLrd5Mu1mamJQ/c38OUannfa7HRLrJRxNyz4WTfMMEhw'
        b'ka65LbFanqbUoBZGgxMaw0h3ChDruNumy8QRp1+IltaDvj75TuTFevOmM0z2MlXecBWjw441oASc6gHLY3NguT1mWqzTW1DHbpgu8oTtL5FMW6Z4S27y4zBLTN6UxChG'
        b'h+HloNgL1nbBdYtyxNrtm7A+NtE84/3ZInhwjQ/J+OAgERvPjmGYuGUB65c6MzS2bClvsM18sW0BSnI488JcWnAGlLqChjTYTLKdFOW4VM9QzpX3cvIZHR7uQSnYqTDP'
        b'FxTDYmPekf7x5vmth5XOYMcCbsFl7HBhQl+emGGWLQvYPWIdV/9GUANP2aa9jY2dgg5yVp2VoKddQSNqG5Jx+6uus6YzPgzjuSwmqU8/erfgRdCKjAUbGfsgqyWD2i0W'
        b'mZ4DR11hKajTKJuv3BZoNmPt7Kko8MPzXuxYUcTcD/IDq8OG/tjqsNVnWc3mBjamflw9L6ph1L4J7hP+NvV6ygfNmrQq14Vjr6/0/erqv35c5rZ3vwoWDsisaA0OOFux'
        b'tvaXu7HhVZ/67LoVm9fk8c7J1zcm/ex644vgY3+N+bkpdFri6JUt9b8eWHJB9She8/4ij++H/Dopb8CoKP8PfvJwKJ+U+su3vi4U6bcbXoTFZlZkMygirjLYiuwLTxDz'
        b'bAVodje93i6EraZX3K/NIXHgYGsAMqe5XODFaVxHQ7bgEFgrgCeQwbaTvAoHR9xBraVJCo/AI8jiI0ZpPdxLVifiFWCTf9C6BWZo8hxQRtDi0xKJUeoPC0KxzYzt5aXU'
        b'/stYmcyZf7BKgixAbP+9As/RCElvueGQfOaGPTygQcViu14DtpNX+SNQV95gZoeKwAF0BrFDM+A+YiemwvbXqPKKA5ac1pBXFZEBrDoyhiizgY5MLCh2AnvHTvzdFHsj'
        b'4BEjM8wst3xmBuHD5TmauHEpTy4JUmrcMtDPIt3DDlPuWzh5Gyfv4ATgBOLkXZy8xzDP5pQRdicTN4s6+aIBU4MtMTPDbj1z3SLqW2fJn4+d1qg52YWxJSIpKEjSVJYZ'
        b'ZS7e1QVlbvdxkmkGBlMzNcquUAsMQj0ZbCUBUQpejDHXOdmgMtktd7Gx3CG03N9G1cvdBkEyUpTslrnUWOYAWqaZMvViDLWCZKQP2S1PaizPx6QxSa3BqM9PB5xuaGWD'
        b'jmJXAplRgv74xYWZGvPCd9Zo/dgrM82iTNTKRuXHrExfliKZyVsQoyetJJVvJgp2S8dPL3GlnYUSsvqEAzuwnM3qQoL8ihQio5O6Q5dO6gb2VIce3WZYkmNWye4SLJGT'
        b'n4dfyZxPqVOWmF/JCDf2CxD7meOe0TaBUqOTzNlhiFJLxcCkG903/IwFhYrjszKw+UDtbBx6jQMvS1OydFqOtkiDFFV7bYP/YYoQOW4SmVJBCGS0nCJuWSmuvUksSdRs'
        b'aVxgORs6MP4XaSQ8knZl040NMbNkxD4GVhX7No15u1J9vdNDKvYJS1HLU9MzMaELZ+CR8HI2BTX1A41GmZZJugKlTenE3aURK81rpUS2TpodbhaDDTOW3OSQyUZTBpc0'
        b'1jcAvxkxEP/iM4zMv6n2rC/SK5Xkekwhhdtu0uTuU1ApLCuEa62Ua34/AikfTJhEqJ58xX5+Gdi+RtVZ7ef3wpRSYh9CHxVIWZieJ+su6KO6df3zkjmJ7ZBQ2SNzCuqe'
        b'GBb4ji4pnXyMlE5jfcWLx46zT8lkjhHhbqNOTqujzCSCElL28NjYhQtxzWzFlsX/sqWrM0hkWrkaT1EBhK/NaBabCTSua4G65JmyfElCn5bRhifFplhUETJnp0LFB4+x'
        b'TzRmjqgxvDIye0zQXvREZmqUVKgshW3eLtly1DNIe+ALSHheaS7+3U3KIvwvzCITDXlbpkxN1yoJL5XGxJrW+Zm1m2egeCymgJbr0OBqzAD1YKWYayI0QmWgJy4iMTBB'
        b'qk2R4zeQtlm0AsWou9BYoipdxgp5uu32DxQHW51GSpPqFGt0WjmaOXCIZvH8LLWGCGUnj/Gh4jCdIl2eosOPHrogTKfNwvPbCjsXTAgVR2bKlKuUqDOrVOgCyu2msaq5'
        b'natDbIn8/A000VY2SjOxMp5PrEm28nu+dplMGtLU9M9oeZs7E2hPxq8KreR+7p5oXn2FGtXGB7etUSZpyhpdmq/97md+uXjiSPsd0OLEsZPtnYm6WebozrSZ9OAE62xC'
        b'7GUT0lU2qFMY69dFHpPMT7NbtckWmdmol90JjUP8oRGO+0X0AaSTorHVMJT7xNM51u6EbQIUYgp3NBXSLaTj+ESjTXkm+kPdXIznoEldsMAboYiW2YyzymZcl9kQ1KIF'
        b't6APIRQMx/PNBLuXGVGO9NKIRDJS4x1iH/SQc10c3Xb7zaBTY45FTGPP/QoQm+l2EYnzxD5J8GC6Gj2kSJbx9kUxA1iaMjPu5oQyZKVZoVNrOgvVlbpnT70kqmT3NT+j'
        b'ihZm8da/ezoMgYKGiiX4S7x43JjXun/ZOHrZOHKZ/bthwJhyKiS3jc3mrvoBAaCiS/AXOrHzefZHsdlytTpz9Cy1VIcSVdDoWUqk3dkftcjp9scqnI/98QkXYH+A6qpk'
        b'NCpFpCMlDI399ocmIhvS2WS2xbDXeEiLlcu1WLPA30jBCulSv0vJyg0V48VjpD8psNaKdqA2t39T8UUY/0uvkqrEeKPLK1KVWvxAorRLdY/CnvGZ9AfJOADr6YHBY0NC'
        b'UE+zLxPGGyOB8FeXPVIhRbWdhQaVrk4iiGV0h/CXeHGI/RO5Yc5An9pFjzZgqUPFM9AvqgkvHjexy/ONjza5xHJVr8v2NiC0uSvp/bE/WGNkNlLRZoRJ0O2xPyKmKFNR'
        b'hpEzUdE2nshO2OrOcd05tqfKhYQ1Yswd/jLVqNXTGepkcrI32GQAwsGy8f7Ynwrj4MTwPLlKk0Q9VQNiloneDlZTT+aE5XjJ4lJGJHbmIvC8uAxy9hy/3hjVK44ZuSyv'
        b'zN+Pc6etho1yWOUAa0cTrot8Dvpc7uhmgssdhaUc9HnOOpJVSVAedl6Oq50iXfxlMMvoAvE1G7zBDn90PiYOnAMrQRHYgtcEo2JpTCMGtoHyeUzueOe0QDVBBrEqyfxW'
        b'Qakbk43DF6k1f+fW6PYlgSpb8YtwLrMxUxFdophvvvJXAepEvoPAGeXN7VdYzS2UTd2iJRu2xEbx53oWH33yUf6S6PacXl+cu+z8hUvZg91e48b8UTMfbnZ1ajjpvG96'
        b'jz9efzf1530aZmLsfyX+pOuXPO52gd+o2Dtv/uHaoXP8wOBPZQ5HRz18fOdYq/aSz/h/be0lufL3DyO3lD52U+g+8bpfcSd//JD0jt4FEV/dkaj3dRzQLJLk/Y1pHNkx'
        b'YPKVP629+s2/3//hTOxnR7zyv533WnjaW+MXLHT6KunX3gP5E//c8NpLd9sP//DVuz7h+fLysJSUkvNXNNUTV7/bUz/ml3uT+/S/o7u7ZsTwm6tG5V098TTNZ3Dc1Kfs'
        b'DebVbSt6+QppdOG2fmAbBYQo3AyRh8GlGLKYJAfNLuAo+pyOMXJE+YEj5JgKnOntD8vmRIL96N4cEzCOKnbY8gSyhgQviuFhV3AQ1HfGgwjHasfgG14Pi7HXJ7eKBFrg'
        b'LtNKkvU6khI2kRU2UAMuZJGgSZ1CJq2D9fAEPAOaiQcraADHXCxY+vgMOA6PU5Y+sMedomSO5oRGx0TyGHYeD+wAxX7xbp1xHKLfKYQ49nUjC1g48oLFAlY+M0dIuPYE'
        b'PHfeCBJGCf/G7oMu3OIVS5wQ+6Pv3pivSGRcpJHKZBKLYB6mV9fYT9tsxcr5uQT3FZhlYgrsaazJcpvLVrXDzJetLKS0D+AgIZmw+xFTIjCGZOoOWVExEnIluthipMTC'
        b'd+bFG0lHyms9qS979kyl6t2XtQzB5Yaivleg0c2dAGsTx2BYqgCe4K1l4FkK8MC+/s7wsNh1eS7aTmKSwGF4nrLaHYqGJ+MnkGt48DwojWLgqXRYrsJVuxdBRrkFngmv'
        b'D6hX03ADoADuApuHB4935MAYhaCAeua3wnZ/sBm0BY8XUPQGaOxNJP7bWg4U4aEOyIiTUJCBYooXgWR831OnilRFUT/9V1+lO9+O04impuTRMxOiKU4je1GGinl1Kj2z'
        b'KJfiNOrZtarLg+bRM78VUkhGfU5KzJPoQHrmosHcTq9VAesSUujOt3OpSFujlwXkCz242AAn83zj4+LiGIYXDgr7M6iqpxNpK5XDI6uCx2DGQB48CJrgOQYWwFI3Mt+k'
        b'wap18UPHxzGYWugwPnBYQueQHdMI7ANWzGRMsA80Rmwhxa2CZeHBcKe/EfYBt3EBPEBlAiyMB6dxTx3KDIU74HGKiNjkMDgYrB9NETfpfSjwokCBBK1aCesoiiMf3Vlc'
        b'ejpo8DfDa8CNa2EbAzr6g9MELzIoBtTFx4n5uNq9wC5Y5wgaEtwoyPv4SNBII9/NcTMBNgJnUEAFifrnQBE92ZHagC9eW0Yb9deRdOf34zJUXoNm09kYNmfCynhwNgi3'
        b'KwOLGOnaAJKFU6A39s0Qt4avzftHFEv7sQS8Bc/Ex4F6X9Sn18INYIsrbAD1oJLeoD2jgzRuwai9WHC0bw725SgfoEzP7MXXINWAqU0bmLGNI+T93Lns0ZCSSSN+3bCn'
        b'aHvhvt7N+7yFsez9c+1bl6iLv/xFLJn+kXOzV9Z9z7nh/gtf3n/h0Y0Lq6tjdm5XSuff+uzyjgvffqlTuLSNulbz3qibseoNkhHlx1b+4eTGtrl+NSn/HVG6xG3CZ/w2'
        b'ReL771StvhSRurZS4fVksPjjihXifzYsP9c38ET6zKUfJcxeNGLQ9gc7wxui3zj4ytV/T9MH+f6yLO7TvTde3njPY8T5Jz0bf+pzdMu9W1fubcmvetr6XeLA0Ru/viod'
        b'cvGq9MrRpKqmwrHzYnK3bCp9KqotmF703dRC3421gWlLv/R8f+nFI6oee87suv1K/OUl325f+FAOfCUtuvmxBY9eOStIHv5hdLLmh1NRub9cXBDytDpgIqwIOON2dtvP'
        b'N/v0ma+9mRzm660NYjAj1FFQZ8MLIjIG7IQHLOcvNofCBM7CalCNA3z7wpaUWHRYCM+zYBtoAYXErSMdNqmQBhTDYwRDdUN5YC/YAM9TusMSpLhswMH9MP2YKbrfQthB'
        b'YBIJyjwztMdkpEDtwFDS06CczIf5c8EhiwgG0XELKQ5DHOHgHAtrqIv9ycRcIw7jDbdMHuo9l8Bxiv6sBJtXJyRySAwOhdE3nkz3SbAJXDS5z7wM9xq9Z2DjSCLfOnAQ'
        b'li9B8hjwIhQsAt5iCbIh1A+e6oTRGDkbtPLBsVDYQMlh2uFh/Jhzqgi8IMLo1Do30rRh48Fb0WYgDbgxhs+4gyL+DHEqcd/xhkemmdCdSCttNfBBNsGzFIHQCt4QRJsg'
        b'GjxQwTDua/nhoHUUpVveAbe6WyI0YMuUQXxYNQ1sJyKuBFVRJvAFCwvdeGAfODOfoH2Hg1K4nUZgnAfXG9EXvTKpD9L5PqJOmJuwbFDHB2+AalBJHYfawdFB5miX6HxQ'
        b'ZuZhlOxgxzHlGTH/CL0KUU7WdFZOsgUcDTCLVBJPVkhc3T05CCpGSHgSjASLvl3MKBY9uT/yueM4gL0tHOjCc2QFHHrCk3OZZ392dGYfs+hP6MLxiBGVoTM5me1KWNGU'
        b'Yb1koLVesp7ZZxlG0LoYtQbrEf8ZrrJ0JLjOWk2xTdTlJNFh/6oEuB7swTxdVZGUqss2TRdSn3eSkBqz4OYhmHQLPf+HQgycWw65dD48+RI4Tii30Nw0LReZOhvJ/tUJ'
        b'cIP/tF6EdQtzbjWCDuXQXMDTHEEHb26reaUCh2b1DE+75u657sBfBdXVs79Y7+q5tX79xxHhBd6zlRMPLvxUvLLwp9iVPcqqGx9UrLqxpXZA9buz1rxxUJ75P229Gw83'
        b'6UOX343YruztJZ7v5BWq3fNGx4hr/cJS2dV3fVJK7v0ACooeHjybljWs55HUqK+F4OLdVaO+vPPy/ZjFw369H5vlmnOxbsEn2/Zm/HxS+PnivU2VLfmg9+vekxqfhA7c'
        b'WjNt8pEJc+9n+HoQV7nXM0EzajAHzPvHsW6BZhr4FBbmLSKkWQbKLTT4lrNrneAmcqW21ywTpZaE7QdPDISb08nzvghuRI+8gVALvAU2BRgYtYRx1M7pgEUSI2cXrGFH'
        b'Gyi70HBZRwfu/Qlwn4FyC9bAQ0Ec5ZaXhJT/0ohME9/WOnb4bD9kDFWQ8uejYfWCdTxaeBiUpsFCIa1bI9yYZcZmyIIOcGg4UlBrKT5rl2aOJeEWXw2LwIYseJger4bn'
        b'aERYSrg1hYV74JY+yMo6RY/vfA0eizZ2Ome4LYJwbtVCSmgGC4Sg2Yx2awaLFLj2vrDRhR5uggdX01lpAagzUt5EcQYkKFzmYSTeAs1sLA7gViD/XYi3CFUUGdD8Og9o'
        b'+UzgsK65t/DIYOLeUucwXUO1ci2KHSIwRMldb/X52gbblqEoNEhYYjYofIslXxLfHtaQrdUMY47b6obf4VmGhNXWyjM0FHhlxanl9ZsM3W7ck4soGYrH5xSGkGg5ehLS'
        b'K0dzUqunvX1flERLhCeVpwKUlzinx8tCHomANwG0gU2YEwsUgYNUT3Ng3PqzsGoM2ODLkygdhW0CTX+kAe8p/SRiy3k1GvMikno4DnjUWvGPXhljKt9uOnjZ6aDwW58H'
        b'Z6QbhzX8qXhUiuJ4nm7+ppf6TdCffNz21deV8Um6ssS4tEfrfsy/u1EWIr3x9OO+uZ/f97pef/7q/swFPWZFz/j1bt3dj+/c1yZu/XD0TzNqdgx7eg4mpqp2NJ3Q9hvy'
        b'i6Dm+63x+x7uCQ7KfWfktQtfr9097L1vBp+/Wybb73pi0vLhMWPPv1+7cO3w61NOuWhkM9rntP+hZd9tn+JeBXPf9Iq62pj7btvB2JmLbzxOvHBr47ULt0tzMsocoh7u'
        b'nL9YF998LjJWknq55ZvPF9zoOXHrlMDJTycmXfim4Ez8sSul59v0dVfuDYj9qu6xftFnl+IH5qVrjrV5fTJq/PIrwSPve8xarBj9/hVfvpZE+gQnwSlYjvQS3qS1/Ri4'
        b'ZTAaRohae3gWPMW5Ro8TmL/rWSkgETjc+iNbxOqtDWjXGWJdw62gpPN7lwH/me743AkadPiGx9FmQpClwuRkVZZUlpxMBh1sHzD9WZbljecNfsqi4cWR14MV9hd79/fz'
        b'nub9EssLxcPQFCHf3XVUPrOK5amvGZ9Dvp5NTjZ7cdP//0Eb8NR/Nj7GWFI8DtGAs3enm7N54UduBjiAlGBQCSvTsKI/JwaUgUonxr0ff9DM6crbodMEmkp0mqI+fVAZ'
        b'Jvb0dnj6+IHn9NmqTdNTJvdIap2RmlMdWfLjz28KJ448s6tf7K3wuln902/VPPnhj/w5oS3Xe8U/SR5+6WpUbctJ/6XNU6tmlqVEeyb95c7hgPAd88+cvny5vQcUsDPD'
        b'hoP6MFfXkgkhf04pecV90oGi953TBEuy33N7fCl66oYcz3996rHpkyHClH3xPtfvVyFFgvTlHcFogkMT8pw52JaKdspOZVxBOwubAzVkUhbDE+Oj5wTCNnwK+i72xJF9'
        b'LvBBQyKyovCwPxy2+ND6w8Kl2P8fG4ao/j34g2H9cPLisSfrO1McHRnrF+vEOApY4ShQQvaP5GXD8tGODA/UvRyPZnfQNI7YhTjeHDzjH4VjR+zuH82gGXiXkqoXRUhF'
        b'INxv2KrZzBsIixlXXxZulYaQ406gFXZoTMejtYxLJIt2XlKQOdoVHEhHNg9sTYwM5IDr7nATX+IooDbXblAAm6MNywHzUHH7QQ0sp+pBVXAwVjoDZlPdShbIiHqy8NRC'
        b'2ELhBo2oBnuQUbMpIJuekQG3MS7gJAtOgQOgjb7SbYDbIAYltItAac5KHTy5UrRSx2P6eMJDsJIPNi9GyoyYnAg6YHE0CXmA60MsUiT/LhZZ29vASRr6qQbuzcWNPzoa'
        b'jTJb8ItfvOXEDEB6z+4RAlAUDKotghoP+r9/uqwfNudnDDg2xh8TPILwjLoJabQfEo4fm2oi/lRrHWgE1R7IkDNEz1fJM/UC7Jerd9DqslVyvUCl1Gj1Amwd6QVZ2egw'
        b'X6NV6x0In7pekJKVpdLzlZlavYMCjXzoS42X8TFvR7ZOq+enpqv1/Cy1TO+oUKq0crSRIc3W89cos/UOUk2qUqnnp8tz0SkoexelxgAH1Ttm61JUylS9E0XKavSumnSl'
        b'QpssV6uz1Hq3bKlaI09WarKwp6HeTZeZmi5VZsplyfLcVL1zcrJGjqRPTtY7Us88s/DzLL3bP+Lf3+PkHk5u4uSvOLmDky9xchcnmO1T/Xec3MYJXhNSP8DJdZx8gZNv'
        b'cXIfJzdwgrnX1D/g5B84+QYnD3HyFU7+ghM9Th7h5CecfGdx+1yMY+rP4WZjKjn2RKjA7rep6UF6z+Rk7jc34zzpz22Ls6WpK6Rpcg5vLJXJZRJfIdEUMR2rVKXi6FiJ'
        b'Lql3QS2u1mown7XeUZWVKlVp9KJ52BMwQx6BW1v92NBuVr70euGUjCyZTiXHmHRqbguc0DBm3cUmehOA/P8Cg26anA=='
    ))))
