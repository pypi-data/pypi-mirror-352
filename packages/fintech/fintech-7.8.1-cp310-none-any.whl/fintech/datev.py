
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
        b'eJzsvQdcW9fZOHzv1UBCYhpj8JQ3AiQ2GPDCExDDNuCBBwgkgYwQWAPbeMUTbMDYxnvvvfd2c076fkmb1SRtUzKaJmmz3DZJm1E3ib/nnCsJYUlO0vd9v9//+/3+xlzu'
        b'2es5zzrPc+4HzBP/BPA7Fn6tI+GhY0qZKqaU1bE6bg1TyukFB4U6wSHWEqoT6kWrmQbG2ms2pxfrRKvZVazeT8+tZllGJy5ipNVKv0fL/CdkFU+crqit09lNekWdQWGr'
        b'1iumLLZV15kVk4xmm76yWlGvrazRVunV/v7F1UarM69ObzCa9VaFwW6utBnrzFaF1qxTVJq0Vqve6m+rU1Ra9FqbXsE3oNPatAr9ospqrblKrzAYTXqr2r+yr9uwBsBv'
        b'P/iVkaGZ4NHENLFNXJOgSdgkahI3+TVJmqRN/k2yJnlTQFNgU1BTcFNIU2hTj6awpp5N4U29miKaIpt6N/Vp6mvoR6dDsqxfM7OaWda/Ubq032pmBrO0/2qGZZb3W96/'
        b'yO19ISM1KAUFle5zzMFvb/jtQTojpPNcxChlBSYJvAuDBIyQuTiBYcrlpcoSxj6UdB1vb8AteH1h3lTcjNsKlbgtp2SKSswMn4g2rxDiB+gcalOy9j6QV5+An7Hm5OON'
        b'uDUft5b2Yxn/HA5dRLtxm5Kz94Ic6AJ6UKLJic0RMUIhOonOsOgAurKMlsbXzBEkSYXXQ3kRw6GOQLxBUDAL3YbSZBrRWXRuAWrBG2LroUutOeiWWMT4oyscuorO4532'
        b'QZBHuxBfhiyX5ah54QI7vrJAvsDeJ5xleuF2AWrFl/Al6OxgyBiOW6pQC2qP06iiSY9xOwn5MX3w+rQhQrQarU2vZJ8Azz7Oqasm68ivIvPz1tHQx7GGbDOA8TIO1pCl'
        b'a8jRdWOXc0Vu797WkHQk3GMNB/BrWDnQb9I4JoJhFOV59Q2RDI1UJAv6vycgb+WxK4Ym85G9xFKDiVVAXLlpQFw0H/l9qWhOKBMMG7E81jiymDnFmPwhuq0iQvjPUGbs'
        b'50VfRH3JXU9gRUsZkxQS/jh7F3vRj1HER5oj35/xQ83v+egPjf8I2hrERn3OrDBN7JHV/yOmk7HHQkJVSTKsXEvc1KgovCEuW4U3oFPFUejm4tx83B6rzlHl5rOMOUg6'
        b'Cl/q6TH7Muegs/nZ776DGDL3BplrdrmfNLvV3naI2GN25QUW0gM7mfcK3IHPFE1TTS9F9zmGEzB4Hz4+0x5MhhfPFKGzNqhjMDMYr8myhxG4fsaMbhRNg8jqaeg6MxEg'
        b'/pI9FBIitPge7kCbwqHqOCauHrXbSatz0WEjRN/Ch2ECVIwKnxpsjyC9Qs1oTVH+VNwGgHoE9scSti+6gjfbh0NiLt45nuyJGA1A8nrYq8fwpSh0Kjab7lU1PiVCqyaj'
        b'nbRdtEHRHwreGA7jHMmMHIluGkfLjgisOyBt3l/mzX0pIRDFy9dq38p5a82+d58RXLzyrCg4RiI+k1nyh9fWxrbPTk4bykqVef3vf/Prj98b9ODtCX/u/7Fl1K/zkvym'
        b'Nw7vePXm9HWyq0fujO8TMfpXN6dK717sfS2n8fTdF+6vDer72curxC9cf1x6vk9tR3Gfl5evmVwUvuLeL5Y+mv1DbOexAwWT+k0/9rHyy47fxoWrv1j/3efiTdNTnzEw'
        b'SpGN4FB0T6vW4LYY3JavyiVIJBTfFLAjcRPajo/ayCThdRNjY3JVsdNxc05egYiRoUsc3heZayNbF50vb4hRK3NjKIbJxDdFTBB+RlCHjtn46i9w6LKMzJodcMKGOI4J'
        b'wbcFMVXoHD4TayN4czZuRZthnjfgdni7uAwQZjqLLqHtM5RcJxeltBCIUcron//gQYDvUfhIg6WuUW8GakLplBpojL5hdGeARW/W6S1lFn1lnUVHslph9zKS0cGshPWH'
        b'n3D4DYQf8jcU/gazwZw/axE7a1YKOsV84U6/sjKL3VxW1ikrK6s06bVme31Z2X/cbyVr8SPvIvIgzY0hnSOwr8BijmPFLHkKWfEP5EnR9CR8TBOTi9fn4jZNjgptiAME'
        b'sDEul2WGokuiMrQJt3bbleSf0PGXIl894Q2AL9CxpQL4FRqZUhH8Feu4Uj9dYBNjYHVCnWiNtFRC38U6vzWSUil9l+ik8O7Pk2GDQOevk0FYBmFAKBCW6wIgLNexlJcI'
        b'6hRPo3NWQOfwkx9gU1YK3LpFBu3nRBgjGCd9h4p4TCRoFgAmEgImElBMJKTYR7BcWOT27gsTCTwwkZDH879VChn4q4ifPjKgs3wZY7RqenDWKZByo8eQz8pfrPi4fIuu'
        b'WftpeWvVWf3HEC79xRx8cVPC2ql7D20Pea5Qe1JrEp1mT5f/Srg51hLeTz4xul+rbGbmM59GRE6LWPXszisi5vLAkMT/p5dSbCPsjAxfHxPjIpXi9BgxE4SOCxrRLtxG'
        b'M+AtZryX5riEd/C5BIw8VuCXgdfZCO0fV44eaHBLHjAQSnHCeEaCNnCLZs22RULaQPwM3k/wlyYHHR+NzgG2G8FF2qEk2dQr0MEG1FKYE4tWjcsRMiK8l8W3x6MmWrQK'
        b'gOVmjCqbMBXoAD7NSPBVDq0pz1BybhAq8LbVKMB2SsrKjGajrayMbqlAeASXwtYBqBXCJhI+bgziAUDtzMdvJlGn0Ko3GTqFhAXs9GvQW6zALVrI4lgIDTzFOlsmVVoC'
        b'yCPItUvkBJk4d0nwCc9d4tFqJffEXnABXaoD6AycA+Q4SvwEAHIcBTkBBTNuuaDI7d0byDE+QM4eA+8p6GyuDLfBKm0ECo7bi7L5xZw6BWghx+Ab+N4YfEgc0ge1Gq/e'
        b'Oy+yxkOh4uH1n5UT+IuqjH1frc3TPiwPrqw2mCqEGxJU5X8rn/l8xIu/UFzYxTIHkiX23n9XCumiZqjwaResAOVbRYEF7c6yDYRUaT5ah68AEm8Hpu0gp1bVO9B17+VC'
        b'tBY36yjUTEjApynU5AhRc4QDaobik6XBhbUCTaGKZbgGdnRMFlfELyjnFToAQVbpbUabvtYBIAS/+VfIWTnbGOpaIlcWviohXe5OoVlbq++CCEsw30yoCx4oKITAo9IJ'
        b'CoEHvICCl3b+V1CQB6vpEx4ILwe7fAN+4AMiYCeeJFBBISJUa4x4I0VgTSRQlP8LAIjgTi8g8bCc25Boj38z/mi8MKn+OMucfVUyU/m+UkBJL7CK+wJ5mMjLJVBBQQLf'
        b'Rg9shJ3H25aN42ECNQEotj8JFPsBTVEG4fig6Q6oAJC4F0GhIhvfcVBI32gCAMHqCQhVcsARbgtk7Q4IIn6dyYp3ihq0JrsHOAjcwCHMBRNkwqtd6GH3U2HC1aRvDJHB'
        b'wwRhmFmD8L+LJVhH9d2hQlRgj4P38Qkj8U28iQhyxbhZpVJPzc4twc2FRTw3mg3MqZplbPieVIz2o1a7EspE16E2Bxzlcd5wC4UitC3cKAwTsNYCKPJZ7M3Pyj8FzGIy'
        b'ZPSL/kusNltroiBUr23+8zn9Se3H5S9XxFbGbonS5mpPa4MrmRfCLYKJu3pdtMXH6nS6bK3E8J6JZRLygw7MSwb2ksiXeCXejM4/yQCa8FUBCLnbKihmWtgPBkc7twRf'
        b'7ALDZ6bwmCky3omYnACIdy1zwmALuk/rmIlO46suIBwGpJIAIX5goIDeGx8EPh4I2lC0jfC4PD3DZ/BlpYOkCH0yjzyoiu31hGd00TN/k4SyiHKWexzMNQY4QIfP5Y6x'
        b'eFLlglCP7QDIq4uYUUDtCY9aJ6CGbvMCqN1b8xDquuMtKlC78BbbzP5nQpzQK4QKCoxHFn/EWHMhov3B2xptdtVDgKBfVVQbwrQnRS99fCmiV7xKRyCoRXtaf1bPvaAq'
        b'P6+d8/zMX8/BxXgKNuEpz7/17EzBGyEv/gIoljA8aDrOAopFVg2tRuv6d5EsAhXoSOgifGgpRTsTlVldWGcvuonXw4rX4kM2MoHTJi7CLbE5uA1ENfG86Gnc4Ap8nUIK'
        b'ascP0EYHY0S5ovAULhLvzPcOA0/DX8DyW20WB+4iQn2wLRQgwh8gozGwC5mQLLTUKQG/zL6hATicLkAgkrHdhbHavADCE40ouQILkeiVAYQDI5QSxBH/sjJeDQfv8rKy'
        b'BXatiU/hUaikEkCoqs6yuFPi4LeslKfqFBuMepPOStkqSlApBqXQSXvmxMZPlbz4gZCpKSIDIeUkjJATsvxPICeXyEXBojAJVQPg3cunjcEnZU7BRSLnygeF+pZa1MwT'
        b'UgtXKtQJiJSylysVbWV04oMgpRxiV7MgwUhA9lijlHaKJ5oBuS9+FDZBX2G01YEEGKex6HX86yc8P/EJaeJR6HS9pdFeZa3X2q2V1VqTXpEESWREj+R5elujTa+YZDFa'
        b'bac4Ouuf/BeM+KtdMKuaOrOtLrMAZlkRlaWz6K1WmGOzbXG9ogTET4tZX12rNysz3QLWKn0VPG1as85rObPWhu9aTGrFFFijOig7vc5i/in5vFVWozea9Yosc5W2Qq/M'
        b'7JaWqbFbGiv0jXpjZbXZbq7KnFiiyiOdgr8lRTZVDshs6swsM0yYPrMYaKQpLqtGq1MrJlu0OqhKb7ISymmi7ZqtDXUWqLnR2YbFlllks2jxAX3mlDqrzaCtrKYvJr3R'
        b'1qitNmUWQg7aHMy8Ff422t2KOwMVC0nviOCucHQEotSKUrsVGja5dV6R4DMlMVOjN5sb1QpNnQXqrq+D2syNWtqO3tGeXjEZ3zXZjFWKhjqzR1yF0ZpZrDfpDZA2Tg88'
        b'aQ2pN8oRpXSmKSbrAXbwUYPNSkZJptQzt2JynjJzoipfazS5p/IxyswcHk5s7mnOOGXmJO0i9wQIKjOLYBdDJ/XuCc44ZeY4rbnGOeUwRyTYfdZITA2BYVWBvRYqgKg8'
        b'fJRoSmrIrPHTD5E547IKSJpebzEAroDXohk5k4pV4+tgbRyTT/eC0VwNsEbqcUx7ttZeb1ORdgDpVKgdbTreu827t3gy990GkegxiETPQSR6G0QiP4jErkEkug8i0csg'
        b'En0NItGts4k+BpHoexBJHoNI8hxEkrdBJPGDSOoaRJL7IJK8DCLJ1yCS3Dqb5GMQSb4HkewxiGTPQSR7G0QyP4jkrkEkuw8i2csgkn0NItmts8k+BpHsexApHoNI8RxE'
        b'irdBpPCDSOkaRIr7IFK8DCLF1yBS3Dqb4mMQKd0G0bURYT9ZjHqDlsePky12fMBQZ6kFxKyxE1RnpmMAbKwH8ckZqLcAQgbsZ7bWW/SV1fWAr80QD7jYZtHbSA5Ir9Br'
        b'LRUwURCcYCQcg17Fk7ssu5UQlEbgGjJn4KPVFpg3q5U2QLAeT2NNxlqjTRHlIL3KzFKYbpKvAhLNVSTfJHzUZDJWAY2yKYxmRbEW6KJbgSK6BiRlCtXoulfWRcZVpdAL'
        b'QBhRpHi3BEd5SBrqWSDRd4FErwWSFOMsdhske5aj6cm+K0z2WmGK7wIptEC+lqfLdM6BLwH+hMbZ9ItsrhfARK7XJPesVlc2fiHG6YEcV7lFDM0sNZphNcj603ZIUiNE'
        b'EdILWLpbMLF7ENCP1moDamcxGmwEagzaaug/ZDLrtNAZcwWArWvFbRZ8tAqAKMesMzaoFZN4+uEeSuwWSuoWSu4WSukWSu0WSusWGtEtlN699fjuwe69SejenYTu/Uno'
        b'3qGEFC9siiJqmmNWrQ5GQ9nFGHlLdPBK3pKc7JOvNBcq85Je6L01wnd5i+/Givkew1PSfXFnPydzou+Wu/FpPyUboEpv2bqRgFQPEpDqSQJSvZGAVJ4EpHZh41R3EpDq'
        b'hQSk+iIBqW6oPtUHCUj1TcfSPAaR5jmING+DSOMHkdY1iDT3QaR5GUSar0GkuXU2zccg0nwPYoTHIEZ4DmKEt0GM4AcxomsQI9wHMcLLIEb4GsQIt86O8DGIEb4Hke4x'
        b'iHTPQaR7G0Q6P4j0rkGkuw8i3csg0n0NIt2ts+k+BpHuexCAID1khXgvwkK8V2kh3iEuxLuxKfHdBIZ4bxJDvE+RId5dNoj3JTTEdxuPo4uTLPpanXUxYJlawNvWOlMD'
        b'cBKZRROnZKkotbJZLXoDEEEzoXleoxO9Ryd5j072Hp3iPTrVe3Sa9+gR3qPTfQwnniD0GjO+W2+w6a2KwimFRQ4GjhBza70e5GGemewi5m6xTvLtFjVZX4HvEkr/BNtQ'
        b'xcc7uAZnKLFbKClzikO54lbYQ+2S4BmV6BkFYo6JCMVaG+FLFUV2qE5bqwcyqrXZrYSt5UejqNWa7UBeFFV6HkyBHHpTAyjdihgJcTfqaLEfzeylfi9EyXvdnhmpiqlr'
        b'dhTAfCscLC+dSgNJd0wy/57o9k5kwi5N1SM2s+CUxELUoBaiYbUQEw7+tIScN1uIxUanyFpvMtos/V06vODu2jyi1l/mVEvy2jxOwLHi7zkRx4kTJC/ZSdUqvBndmo/b'
        b'rMS2ZH0sOiVkJKnccrw+5X9Yn+efVVlZZzfbQH7oDBwHi87LHdp6vemTnrw2jyjEH/WeAGBQC7wFUZgqeMkHgNgIqAeyEG1sp5DwQJZh8PrVXYgoqeVZmrpqs15RVGcy'
        b'xWUDTjKrNI1Ew9IV7MJymTM0pQq+GNGkEfxpNVrtfARJcw/zu24yUfzxHD7f0LgSVVFltQnfhdU3AVfiHswcpzfpq3RkIPyrQ+3S9Z7okJAynTNBOX7CEuodm9sptil4'
        b'tsgh/HWpqRxiH2XWicAHmWF72ahg4KiBNmcyQgb6ZjQb6hQqRZbF5uyKIybHTEo+EUmyJXrLluiRLclbtiSPbMnesiV7ZEvxli3FI1uqt2ypHtnSvGVL88g2wls24DIK'
        b'i4oTIELDLwzhdvU0MtEjEgKKfD1gTKcuVmFXK7p0sRDJw7JTOapWEI7dKXfzSteuZVTkxeRlTrKba6gdrt5SBSiqkaAVEj+uRJGczhNagzMLUQp7i3fADZ/kpcLMUioQ'
        b'kIFbarUk0QUi3lJcoOKrWOLTinlP5EHoKcW8J/Ig9ZRi3hN5EHtKMe+JPMg9pZj3RB4En1LMeyIPkk8p5j2RFEt/WjHviXS545+63t5TacGnA4pvSEl4Kqj4SKUFnwos'
        b'PlJpwaeCi49UWvCpAOMjlRZ8Ksj4SKUFnwo0PlJpwaeCjY9UWvCpgOMjle74p0IOpBbZ8N3KGiBdC4H42ihrulBvtOozJwGJ78J+gA61ZpOWaBet87XVFqi1Sg85zHrC'
        b'FnWpGx2UkyC8LLuBKMZcSM5JSyGJYN4ugqyIyjI38iwxOdEDZJxvtAFp1OuAA9Hankh+Ag97Fu7C5E+mWUz4utXBJnRLyabnOwYbcCUuwYpSEhXld7xKAY6ROqg5kH6g'
        b'NISJNlD2uZYQeJveCNNic2mKc4DXtRkNxhqtO/YvpYKgS4Pszmbw4qPbSaI7mzRJz8sWemMFScqDVSNHY1aes/HNqLlrh6Hf0LLWZK+t0Vc7VdmUCFIujhjBFFiifTGx'
        b'xNrqrk8mNlLyZzvhf9HJfhnWvAK8MY5ysbhV48egK/hQzwqhfHmeByMrdzKyNrY7I7tVvFW2VabjtvbY2oNnaNv8pGKpvy62SdQU0NTDINDJdPI1UmBshXqRLkAXuIbR'
        b'BemC27hSMYRDaDiUhv0g3IOGw2hYAuGeNBxOw1II96LhCBr2h3AkDfemYRmE+9BwXxqWkx4YOF0/Xf81ktIA2tMeT/xIdQPa/KUSqUSnauIcPRbqFLqBtMeB/Oi2+m9l'
        b'DWSEfvTpLDmoTQrl1NR8TkT9OIKhtJ9usG4ILR2ki4M0UZOEenmE0rShumFrpKXBEBsCPRuui4KehUArPXTKNqePQmBTkEGki9bFrJFALaEOcSC+UzKBmHaPL5r+KM5f'
        b'4fbPGa3gcQnvfdQtxymRhZhRW4aQs3xq4U2Mrz6hxhpEJlDKPyGWNp9Qm2ViZ9OV3ZLmzG4hNjeWBJKFWD18Qg0DCFwo/Tr9tboGQE+WMqOuU1oJSMJsI6+BWl6AKTMB'
        b'l2er7pRU2mH/mCsXd0qImapRa3JYZMgMRmDsymph71bTtjsFE0um8SYflnR4VErcgNHf8UsNdiYxTzhJSZvETf5NfgZ/h12QpFmymlkmbZQulVC7ICm1BZIslxa5vS9k'
        b'pFVKwVcdMPhuM0f+5fBdNTbqrdQxzDXfRmrWUKlXexTxiMgA2UNbq+iapgyHSxjgF6IMcvicOeZLa7Z51ED+RY0DtGBzIiWlWpFFygMCqVRQc0GFvV4BaDRNoTNWGW1W'
        b'z345uuFaIe+94JO998B15PEjfUj5sT50B40MRR79S7owOS7PmeromNV7XwjRIegeiIVaUVwNBAB2gF5htVeY9LoqGM9PqoW3J+ElVahJoYUqIMz3X2GqA2JkUStybIpa'
        b'O8grFXqvtWgdg6/Q2xbqyZGvIkqnN2jtJpuSegSO8L0Wji2RoRjveFNUEp1hlOuk0U3XqPRVi3M7ZTih1epaTOKAWGdRRPF2KzX4rqURpG9fFTkspTKoqEXYEqiGhxEH'
        b'donSV6kVKQnxsYq0hHif1bjt5wzFJBJQ0ACpzmA0w66BPioW67XQsWizfiE59mxIVSerE6KVnlP1E8yM5bynwwxjMKNgmBHxhmdFG1P8GXsmRK4oM+KWfHR2Cm7OwW2a'
        b'OLx+CrExzc5T4pbYAhXagNvzpmajc+gwk12Qn5+TzzJ4Mzoor2sw0Ervy+TESS4qXrx14Xulcxl7FkTic7iDeKc9Ue9OiCd14414fR6QVrTeUbmr5jWL5QxqxVto1ddH'
        b'S4gDXXx8+MAUtCSTsROcizcVD3R3z8pWq6Jzh0yDJtB5IZM6R2wNHEU9zGgVU4ViQp6D4ye1BFn10xg78afBZ9HGCOgcXg/DenLguBnqbYklHWxVTnfrG7plkaHLY/Aq'
        b'40exbULrcqgoVPx1vxd/LX0mPnjib/KWd3z8cmBs1kWB5iKTxk5NGzT94B7l+Myv0oX9BR+FvoA6QtCWCTnj0uYdemnAS8aWe58MujTlxO4780v6XV3bWPLNt78/KIla'
        b'FPD5xVtHVk/+6uI3aw+cDKjB1aE/RLyqq12uef/S4n/9PfeG2pC8+AemUhv1rnCeUk69ReS4BZ1ELU7ny9ThxFskaKjAgA9n2Qg3M3WRBrUUuq8nizbPZnrj1cLG8kG0'
        b'DrRxVLoMJlSZb1fhXdW8wW5P1CSUSAdSe14VuowuQC3OlYueRteOZcIHCmXSYhv1zrsxdlCMSjwgKlvFMWK0m1ONGENr16M9esV4KE2WyrFQoei8ALfESWzEALAmiYlR'
        b'h+DTSrwhlnjnneWSgO2inU8Pzh9fgVqIk5hrVcRMaIMA3RuINtuIX610Cm7tlU6G6ODYSNccSwrQg9eK1QtjqGW7ALWQfAA+Z1fERqtJPtyG22NIPoVVFJCEz1PbY3QU'
        b'HbNjx4ipHhMaVkGzaIcArx2IztsIGa5WFbs1yrOJaDW+wfRGN4XQ5f09eVtJ///Qfa3LvYUamhLgZ1aIl4pZ4qXGP4mXmoR6qkEMJ4ZYf7YxxEmDn3Cz8edtTMkOsIwl'
        b'D7JTLePIYzzjdKmZwDzdbFnCl+qqZJyrFK3Ei3POJ4zDBJRZ2X+nF2tWz/52M21mHb/UkpT0bCkzn6FcH1ugZDtlZV18gyXCNXduTkkjTdraCp12dAjU8g/eKdWtTWfq'
        b'Iwcmd9TmpPpRQCF0qjqzabHyFNsp0NVV/qTOVfOd8y9zcRPe+mYh7rdhUN6SAy+PBvA94It46cDPmZagsu48hM/me7maVz6Vy/jZHTHwHZGWOYm4zy70dnUhcpzWqndR'
        b'/f+8SRcD7avJfq4mB/vkCX5m41V845Iyp/+ar7YVXW375CP+s4HLy9xFBV/tD+5a8R9hPnz0opuzAXWZ45oYl8vcf+xq4Kzaw9Vg+85gljro1o1+g7jAvfP2ixXVhofM'
        b'b1pfan1f/qx8byQz+ojwrYcrlBxF37hZAuSKom60C+9+An3X4KOUGPQbjHZ74G9mJr7uQN/n8ZqnebP5lZGd5ebAxKxgVoQNbwx2w2Y0A1+m15M1RbjWZBY8hsH8WkkU'
        b's5JZGdjpBUt61Kv07/Rz7FHepF9stVn0elunpL7OaiNscqew0mhb3OnH51ncKW7QUslTVgnMel0tL5EKbNqqTlEdQL6lUua2EgSRBzpXg/gJNclckmSA67qAQP6qBkOg'
        b'Y/FlzXJYfDksvowuvpwuuGy5vMjtnV/8r94ReZEns3Q6KwgMhOvV6SvIPoT/lQ6rOIWe2vD/BJGSCjxUWtEqqu1VejchDmbHagQhSME7OhB5zKq3qRWFAOce9RCEUEuO'
        b'Yoy19XUWIns6i1VqzSDQkKIgDFn0lTbTYkXFYlLAoxJtg9Zo0pImKf9PbCqtajJSI1GqwW5zVOmQoUidHnVA1Xar0VxFe+SqRhFNFy76J8zIJMdoq4kSxLPvHvmjbFpL'
        b'FbShc2ImUl5B1IRWIo9YF9jJ7FZYtJU1eptVmfHTxXweZjMUWd0IjGI2PRid66sYaTlDQf0aZv+od4PPWvgtkqEoon8Vsx22dj7zO7dShoIoOWGpqPg5293WzmdZsvlA'
        b'cIWnYnahxeY7H789ISv/QtuIVeQUFaqSElJTFbOJYtNnaX5Pg0iaVazKmaCY7TgtnBsz2913w3fjXaiACNl8QEEqcrcY9lkckAdMZjVsDdiu1kqLsd7moGcETok/N91b'
        b'WSZrHcCvXudVPwDgRHIT6mOiF//QxVYrJvBKArpFBxXZtLW1xO/NPMinuoBuBgAs6EC9Y2vpjPTqIS1M60IjUDn9Ilhxx4bzrIf8K6iz6fltQje/3lZdpwNMUmWvBUCD'
        b'vmhrYAPCptHD7FTqFXVA7r3Www+JbBqq/bDywzRa3bqkVkwCpOZESF5rcd92RFcCoE4uVqo0wYD5O5Wseu8lyx3XKtVV0p7z5ygjq222emtGXNzChQv52zDUOn2czmzS'
        b'L6qrjeM5zzhtfX2cERZ/kbraVmsaHOesIi4hPj4pMTEhbkLCiPiE5OT45BFJyQnxKWlJ6aPLy35EM0GooKcjYWgBvY5IhvYNtOYpc+fg4yp1AfHfi0GnQBQcUiSqHoY3'
        b'8Het3K+YmAR/Exi8DjUl4C2xVMJfslCo4Ph7dvJOGcoYO9GIojtMgsZJ2afiZnLNSa5qGnGBRUfx1mlRxLF0Boj68Ifo9regC1K8bT5eZSc2Mjp8MwxfAVGXSIZ+jAh1'
        b'zMK7OHltiJ3og9FtfBatwVfU5L4N4mqLro6D+slFKhwzAB0T4tu4ZQmvaDiOO4ADuYLaK0C4zi/Bm+phkG4jnIKbC6Boq6akHh6Febl4m5C4Z6+S4aPL5lODGnR1XqRM'
        b'rcxFd9EBf7ShipHmcvgA/Fznk0+h3SX4Sg4UZ9HqISDi7mDRM+gYOkwvB0mt0Mpwc5waryddPYzvx6JTuSBKN7OMYrJIOB2t5i/WOYCuomP4Slw0y3DZ0RY2NWIRnV2t'
        b'VVxwREAvQTK9MHEpQ+dHE15inT0+AG/D12i7jGQONxntQKvobVDoxgB81AqpAQFqvBmdHoGv5eFLMXiLgOm1WIDOon1m/pDlTAbaLVNDDTB1OWRGBExPfEu4fECQBd8x'
        b'PtBksNZdkO/j535QvZzvj+KDRe+lGV97fDrG/6Vjmr//qZ/wHhqblTbtU/U7M9ekT1pSVDbW8MUXqHKYOOZsY/mCpEHFjVHvRgR9Ou32L1b9dpisSfWbh2tODHilo6jO'
        b'8tygAQnapIufGAuspa+u2558pKfKmP/6X9Y1fPDbjLXXy35/4q25ja9P/+KVzL98bX/9+73mqjPtieXWmuY3J3z7SubpP/kFHYje8MUXjus8FqH1eGWX/sWhfVmqMqCV'
        b'1TZyoRA+pinVeNNNoBv4KBOTJMLteB1eTdUdaF/NMKcipksLg9arJXg3Ose7Vq/N1XfXSxSgzQ7eFp/T0Ot38I4RU2MKVDk5+ZpY3KZkmXB8V4gvo/WJ+OZA3nn/HDo2'
        b'QRMblQ19YfEljpGgM9zi4KpuV30E/qe37/h0nfXX6nRlPBdHGedhDsZZni1nJWw4S57uP0Jy9Q78jWAbe7gY4K46eAY9gNc6lDJOozZyHYhlDnnMJY955FFGHuXkoSWP'
        b'CqabnsO7D7CMr7OrknJXExWuJgJcLWpd7VC+XkeqcOfrh/3eC1/vbVhKaadcR2z9HLxSZwDPATuDYm0t/UsuTNF3Sh3nu5X6ThnhV4BLJNZffE9cg630d0PGRC0T7ETG'
        b'0whz79+NvQ8EBj/IweIHExbfEOxg8P0pgy8DBt+fMvgyytT7L5cVub07Doza/Z7O4GtdFnwK/jKln8DGTiTeD3xuBdBSmDPgUIE/0LrfIkh4iFhFlaXOXg+pwDprPWlT'
        b'XW2F0ax1civRwMhEUzLLU1miB3CZe5IOukRjj5qIqPx/JZL/P0sk7lstgywUH+PSgP2IZNJtb/Ll+ShnBV7Zs9k/YgHqszl+7/PtOLa7I47ncM11RKNjoTys2TtnurCO'
        b'sJDGWq3JBw88+yk2sCBZeLeC9dljgqX4/lbU1dWQ/pIYtSLfAV1aGlbUVcyHhQd53/shoplIRCNS4xMcSjICCCDOkepmd9nH+uyEC0lmKEqsdq3JRHcGAE5DnbHStRtn'
        b'u5nXPlUodCDZ7stAPe9mu5vg/qjYRoo/Ibp1M/T8P0DyGqdfqK9ymOn8X+nr/wDpKyk1PnHEiPikpOSklKTU1JQEr9IX+fd0kUzkVSRT8IfFcfNEg34noHKVqbXAztjJ'
        b'lVN4l7afJicfb4jNyWNXOOUrIlY9KVKtQPekyWhtPn8f7e1CfKRLokIPShgRkagK8Ek70R+jFrxvhUadmw8cbS9RTt7TKoa8LVJ0Au8toifNkcD0HrIW5hc6Ls8iDczA'
        b'myB7O24eio+AZOUPogjUCFG3iuagvWg3OiIF6QNvlxWgkyyVP/E2dAXdsObitpz8Qg25LWmmJF7IRIwT4FYD3kHzTCvFm6zR+XhjFGHf1TnoXBTLDMBXKqtEoum43U41'
        b'z3eBv78mwzfQxmkS3KYqqisAgYtjQpME6BC6h67SG0bx9mK8F6aj6wwbxB90bdoUlRhfx5uZBNQiWiTpR1sdBiLUNkfHcnoWxipxm4gJw0cE+A6+gFbRpXoo5fqfZ+il'
        b'tPLV4dEMvUA1b2w/mZhhikEk7Si24wt0/VKC82VkkmAuN+Mb2SBvtuEOfK2AirFnIJSHN2YTQWxOpGTC4Mkh+KKdXAGD1i3Eq/EVeMthaotz5mbTFhYN7MPL4+gQPpFQ'
        b'tIDe5YJWwRAO4w56ESs6jS/F4V3okunbx48fyyaIlpfyEJU3RLqMP6CXm8UR0/lbduWvZtcz9omkkl3oLL5FJqfNIcBnk2tIIZRbAuCQjVuLopQAFNmuG5KV6Po8fJPM'
        b'ICM2B8xF91EzvSUZg2TfswhvS8oVzOzFsPgsOfw/MMs+CtKmgiS/VQarRNZo8OhpTqjRlEi8zBE6j7cIGdRUIp2Fm9A+O3Fa6R+AN1tdcvDUKLytSEKE3i6Jd0xPMTqC'
        b'VwUCYGyl0vH4QPzAmqsqzI8jUFTAy7347jBGiXeKQAjfim5Qud46CB2I4S/EUYoZGXrADV8CILML36XXAs+ZUcg9F14pY+q1Pd6KeDfgA4YOKcYIc3bFoe3gTS0AwPD6'
        b'uGq8qTB/apSjQnezBrwPnZDjTWhvpJ24zejQqQUx6pzYaLYHvsSIUTsXFx5FdQTj0Ua0V0PERYYbFWRhR6A91UoBVQj443v4Nl8KrUQb+GJoNXqGVoma0PYJjoJj0X5S'
        b'ct88ihdkaPXQ7oMciS6SW7/QfeOJnF8IrCNAfIo/s2XuplEFgiz52r9G1qXuyc/+VnP5u7f/eOeZwUePTzp8/MqqrdkSVchv83Dy8fc4ydEPw//5Rv2wdw03Du/65uHi'
        b'RyMrB3/2Vv3EFyZefnvS9qEFrYExr1SrvjJ98Mas1GPPxZlmKb5qSf3k8dALm8L+Mfe1wbsGzhq35FU2uSlwxkv5A85XVRz58NOamLzQBxteeD0gQvTmycyNilFjO423'
        b'jj8qaDo5WdYYPKq632vqL6bb7n7wfIb0uzz71ZGfp77+wsavLnI57Z8jyaMFHz+/Z/+l/TtrTj9Xvm9Vyvk/muRj1u4o6d/vZcMYkeGB34mRw/8Z2H+M/Xdv+93452/8'
        b'2p9jilb0Cbh/OGpnXMYfC8//btb315Rfnf13+8eLJ7637Eb/Fbv+9s7E35q+OPHVx9vfbH+7Y97yb5vn/XrelF+/UxGUaZh2+1jFv/xCC8zZPb5UBvDqgv2VaJ2HegK2'
        b'82YDgWOqoaA6qi3edRT7rQ4VxUk1VXdoAfM4NRShS90sRULwFno1sAbtx9s1bqYeQdMFOXiTCV+pppoHNgSdi4lWh6l5aw/pLA4dw0fxXmoJIlYYYtQE18ey6PgKAKSN'
        b'nCpqoo2I3PPRLosmL1rMcP74yFw2raeN3oVaDGXXoTN5+bFcYgoj1LDoMtqBdtM7vwrRUUTIgsPGI3s+I17KDdfg8zYF2f+DZ1FjEA9LkNGxVlHAiAzeFORan6FPnBLi'
        b'fcOADvGnhCl6OsnzkqfDJO+3km2liqKZYJ5D8CYBuojWxdJxI8CwRZrYKKuA6lx4hQu6qn/KXVrK4P8hBYw3VUwg0Td0ieBUHTOdsAUrqEKG45UxXSoZf3rBmZCqY0hI'
        b'wgWy/SE1DOKI9QnJF0xzkRxyzp+W5J4hb6FsY69ueo6udnkVjpxXo+jJw0AeVeRB7m20GMljvku14k174/dTblb25+s0uCrWu2qa72onwNVElx6HfGmg1F2PE33cix7H'
        b'1/gqRW4cFzk17373uqjJr4mhh6hskz/VvsiahK6710XN4tXMMnGjdKmIalvEVMMiWi4ucntfSIw+njhLJw153r0eyLN2n04RzD/K8wt50/o0MsU0tqNA2DfEQZ7fDIrl'
        b'b2hHh3rh61bUJlkgYEahbYJAQN5npdQQbzQ+F1uE2opxW0n+8OVT8bUp+FpJQGp8PMP06yVAK/FNfNBOrzNejXaainBbcUo83mDFN5OBs5IsYPFBfHQopXXkGna1bZGz'
        b'MpYRAR3ZDbt6o51YEo1crkZX6AXr1UtH9hHzCuuLCQZgKY9xDGoLY4YxEaV4A73aXYh2paKVCzTq+OTEFI4RL2fRfrQTbaENaYlFV0yuit5onobWOS81nzzJOGHll5z1'
        b'M8jz+Wd/rW3PyhUmBE88s6Ug45Opk7MmBL2XP3Ll+bmz3nx1w/vPyA5dvpR27a99hvh9vnH6a7j540EPli/vf2Br+TpOerTH5EUi7sof9ml2xh86nbMu73LcykPDTqes'
        b'1P0he8wfhr85N2nLvTVrBk+5cfB4yezffxj48oA5F15O/HDs+fdaZaHfje4M3hO4bcgrv31rspXdNv3BrE1//Wz1TGnnaxdUu0fWVCwPjey97I13333h+r+yYvZ8/Y+i'
        b'9R88WPHt398e9+mk7I1zR4e88k6rKOTTtnHvqh/87UamStVzoeCbhH/916SvY/799cSEulnfvFyV/OrxnZnNH6R92rt83VRGGUrvTFThc73ppwSWzfJjOHSYLSnFq2mK'
        b'IQit4VErg8+Nobh1bi+KzMRLSni8Cj9rKdYkmDWkgeLM0gZ8wgtmLc7krexyKinOjEfALDsJE1qF1ruIkwGdQh2U2KgAjI5rCmKBz2svQcfi0GkhE4juC8p0+DCvxj6N'
        b'1ytxi4Z+5iJ5qbA/iw6jHbiNv+f2Ct4t67ppOyCUv0U7Aq/ide3rs9BK5yX2K9FmWge9xR5Y1tO0j8DDdKzQENNJdFfvsp5kwtE5YR8zvkl17fEitE/jtIusHeOwiwyd'
        b'L0BnGxfwBwBX8El0zit5ZSaU8tT1EN7Ht3gsSEfMWx3GjjthFxGDx6D+gnkwjUf4cd3DhyIdFBbv7O0ksqbyiXROcvGB0hB81anc5wlNGtrBl12PNkc7r90XMEUj+Fv3'
        b'LwL9pcdJHei+BN2Xdr9+c5ECreRLr+7ZC2/zI8wc3lhIblRFm7g6dBSv/Wk4+L91nb/T7oa/vJ/Sq6MueiWJCyQYmWJlct04oVUc+Xks5LgfJALue4mQ+04i4v4tF3OP'
        b'OD/uX5yE+5aTct9w/tzXQhn3lVDO/TM4gPuHMJD7MjiI+yI4mPucC+H+Lgzl/ibuwf1VHMY9FPfkPpOEc59yvbhPuAjuYy6S+4jrzf2F68P9mevLfcj14z7g+nPvcwPE'
        b'fxIODOTCoZFgQv3crHf47vNkz6+L4HT68Vpta6fIatNabJ0CyPdzaZzIUk/ezS5SVueiZ5SUkftlzxFS1ttBypiViteebmzEd/d/x/7r0Z89FBS8d5fN6U3iUPSaHPoX'
        b'i95mt5hpWq1CS84R3NQ5P0kHr6jRL7ZCPfUWvZVYWfJ6Iofiy+pS/juURt5050+eC5h4bRvpTsVim96LXqsbZRa7T56bhT69vlkIG/8AasHbUTvgxksgvV6egS6L4mGH'
        b'npmKmkVMBHpGsKQQneaJ81l8EPjbDlhatAVfVjNq4IVP2BUUt+WOomQbtcxQEXZ8Bt6uFjBhaL0AncLHxlOKP8bAMcIp3/sRvUFTcgT/laJsQLnbXUXFg/C2Cj2H7kHN'
        b'hxOZ6BTRCPwMPk/lOrx9zAwi9C32j2Z5kS8Rb+QJ+m60Eze56Hl8Lk/RR+MHlHiPRC0hVB5EzXgXw4FAOG8cHVDZHL8idL6CZwI41Mb2Bfx+wLhiZrnIuhrSd2zfnv/i'
        b'wEA0Nnjtn74xNCjvMUf7436b3mZk5tdezfiu9cL78jtSP/346e8t/8cKGddnRtj0OV+MeHdoxOVDzb95blbKG2989cyrbRP3qUv6nu91d13D8eX739o1aMnl5IHV//rj'
        b'56Y70qFvTflD4+PPLln+9rfOt3fJRq5AKd8afl+4sc9/fdRL/cnQ9h0NSjGlHfjiwhTUkg0itqd9eIUfFT7wGXxHyV9GjFYL6H3E3GAQuY5RaSZ/sjlGnc9NRUdgoCdZ'
        b'DdubIlg5sQYAopg7qJF+zoNjZHoOHwzHHdRmMWKg+QlhBK2B1XVKI+g0Okjp5nJ0G53t+j4LIWtHpxLKNggdUYp/BIn4sHfUWsvIZqN4d5AL7wpNoQJifR7KhgoIxpXT'
        b'H/H3ESIh54ZGHIV/1BbSAo8PuyOowD1PRVCOmk+xncJ6ra3a983toxnHrdjkWJN840Hsur1d+JNub69SCv4kYL0caXbhLII+rNoG8mYyuWOvn+4FRwaRocgxKKLJW7QC'
        b'0K+VV54TvKRfRDxtiS45Wt1orI+OpQ05EKTFuyraSu4T1LkU4FpLZbWxQa9WFBJ9/UKjVe9CgrQOOgCaXasw1JkA+f8IRiMLJ/XAaJICexRBRNel9THZsD+mZAMjk5uv'
        b'mZ6HThVno3O4OVYN7EU2XudXj9dMot9BsAzSaWAz5ear8Xrg9YqT8VXcTL5xBYyMKorcJaPB1/3QdnQLH6HcvgJtqcUd6AzRJIQvYQQmFhjJDegC/foTupyNzsf4EQuN'
        b'OzJmET4NUkAPunfHzoop5PCVUIadBrhqEdpo/ODZ3kLrDUh8bDCOyk/w57LkeZeXNC5s/Pp3X6+Ku3jp8sVLwVl3VBMmjCi8+Ifat4ftK3v+hzce+icKt+x6Ub4nRnI5'
        b'/9vqAx/Gv98n3Xq83ppasWLP6eI3ck8L2Td/FbWydd9U+0u7/xQ7Ppkdlb2vXPDR1xNWrvoiqm14XejAf2rudQolgV9P2T0sfcWb819PrpOsePz+R1XRK/rNLlw/p+cn'
        b'r4s+O/fibGly0eOg3fqev1G8/VlP+Y0dlyMn71u+Y8/uX/d6yW9E+LffKYOoMqRX4Cg62Qy+hR4wwjQWnQc6cp3qZfBxvLUX8QHCh9B5+tE3ciF+C7dsZgn/4ZgFycCo'
        b'Xl2oip6VTrU6UnSCQ0cae9CaodAuwGik+HqjBgQCcQHXN6mSYpteNbTC9bHqHNwxGP4C1sIXOXy3D9rJc5X3gxHwo2hjIbCftzjy2QLZWA7vDNbwV7PvR2sWkQriCtHR'
        b'KOI8tJyLRg8Q/zUcQGsdJYRcKNXT8DncTobHBMULqljUSnVGswsATCieHYF2OfBs2lD+Szp30V57TBw5r8DrilRqJQeY8IAArZ2LtvBNH0zEtyn3HleLthSIGPFIrhc6'
        b'hlbTfs9Fd/AxDYHVMDmFVmkYhw6hy2gTnZMY1GonUhBMyZg0MiXjuAh0MIfnlFeijcDUOxlt+SjH56221dI+Q+LRvrRjpUmwDmJ0kotNkj1NFfQjWNsNUwvJBqZoOtaF'
        b'ppkVcilR5kiou5CcDaZPopoJpiqevo+5Z4SPGwNcaJXUwV9e7/iegY3ppnLx3dNTHJ+360L7BrKvCFLv60LqzMrwx96+cNCtfaXDM5scCbi5OwNqcfxTivg/HPz2eOJ6'
        b'K2Kgr6urLCujPkidknpLXb3eYlv8U/yfiEU+Nd+huh/KNVPKREfCc+5h/+OauacuqiUZHh8wjk92kYsL/IUg5jzmYPbCHnNDxUB6YQ4FP+9voFAu8HfUEv5YHhdM3gV9'
        b'H/eeGpgm6dObpTgWnYidbyUfk7RaUgIDBUxAPw4fKgNcSrXL94Ync7UydNJGMIqMnMdMIYcwfROFg9HN/P+vvrTkeYrpV0DPqBrY5CIGnQI5fSAzEF020kOhEnQUAUuM'
        b'LsankLselgjxdXZBUSY9yqhZXOZUEOF1Q5wKItQ2hWdsNw4bgFtyYglXlSQE6belHJ/hctF1xjg/Ss1aCaQ+J332s/I5v7i46VBHwtoFbKXfB9zxtXJZZGZW7F/Cjof9'
        b'ZW1eearGXzZz6+8CDmWfX52w9tDqQ9tytrBDetBPYVT7hYzO6K0UUTSBb8+eGuNQlNvxHuoZWTyGSvnDTIDQXXK8MD0ONwF+MUyjibPxWbzZqUhnxk6kenS8zUBxnj/a'
        b'iw93E+Hr5FxdPb7J4+oWvA5tJoe8fOpctG0Ip0d38bmnecPIQZ4C/kVfRoweKO4Jd8M9kiGBHPk+hhAwjZC1LHHtImGnkBToFDuc1Dw+8EQunLMsde0CUnIg9wQmCXzH'
        b'y5fxqO6+HR2bh9bhNTFRuars2FzUFsef2irwdlHYcrTaA46CHX+tGZzbTR4jyR0WAKicTrBGWirQC+kH8RjyKbw2rlQEYQkNS2lYDGF/GpbRsB+E5TQcQMMSCAfScBAN'
        b'SyEcTMMhNOwPrflBa6G6HuRjerpRsElYXU9dOLQtd6T10kWQWzt0o2lab10fSAskIWBtiTuOUNdX1w/ignRjIE4IJQboFORuja3+W7mtAoNgq3CriPzoIg0cxJG/Atdf'
        b'PpZ/Cvkcbk/hk++6gXuDjIxu0FZRB6sbvNUfnkOcdcH7UD4vvA1zvQ13vUXplPCMdoVjXG+xrjeV603teotzvcW73hJcb4mutyTnm/sYdMl7uWOsLmUvVxqiD9WH6FIj'
        b'mYM9DjGrWRpKc4ZojjBqFck7PElgbv10I3TpMPs9qb2kH51vkS5Dlwlx4bpI6oI5tlNaBqRMOwmYauqM7nEK0F0s4S0vxfSziWKX7l/0k3T/P/FTY/687v8v0BPytcNX'
        b'Y+rlaZlD+EP4VviJYJmoz0fbzJOV0/jI0QOWsd9yzMyDSxbNXjIlnbGT203Q1Qn4Wjf3+27+c4CMWvyYoipg3u5IglEHXk+r6owZxBDCOjbLyImnDGA+cnbzH+RhfOPg'
        b'boGVHMTg/Zv7tT4b8Ey8XLDv6rGLbPY7G9hvJ3x65AESFmdra0JHL7yum5XzARuwe93wy2uy4sLGBXw0f9L2v4QvSWgKb7w18/2De8KuB/6Kywmqe/fwiNdfyRlWuX3O'
        b'9/bwhzM/9etQR0rT5UopfxbXvAjEBPIVoYlpOSoBIynmbPgw3skn3kXbc4HrvJDXW0NU3+LhXAjehzfx54E70QPcRA9A8TF0rZuZtgQY5K3UJR2fnohOPOlcGAKMJJ2f'
        b'oZGiaj16hh5CGvH5SN69HWb0ZJSKn0bI1KuvcORsdIF3aLwfjQ7S7uI1g3JQG1Wpt5IDxj0CdAgf6cnn2o+O9udz3UababZ8dJaBXNsE6AiDO3gxYC1qrUQtccDxTlDm'
        b'4FYWhIANHFrTiB7YyLcJ8aoCfBi1LASKb+M/Dd2G2guBzqwvxBvVYiYdb++hEaPty9ENHof/ZMa0y5W9vxttECf6sxJRBHVpd6pwyQcBXfvnCS92XmXaKaLmU51CYn3b'
        b'Ke86bjPXdUqN5nq7jd4e1sWvupu1iyxEmWRZSR5rGCeruqpbP+OepDLhr3j7dJxnL3+Ov66ojHTfp6NuFgSpo657Oy5/9b5dF6B6uOuqLRqCdH5GVwLK3OfQZ5cmOLv0'
        b'qL9b856u6uqf4zLtX9a1Yr4anuxquF+OM7PT/PNnt1vt9BMnQFRWa/Ttq53rajaciCYKg6Wu9ue3Z+jennaRz/byXe2F0faIcfB/2Jq4zFZn05p8NjXF1VRkMcnoNCL2'
        b'2d7/jNq/yhu54hjPbyBSyjE7j5tZwn9vPW9A+HKeMp0YI56zj6M2Y7HXKsSMcdFXGayV6M+XjnuOfLE3W7tVF2Uo1MoNH5cfvfQx8+WeyKKdz0WuihwxmykfK2YOXVey'
        b'FNktsaBVqCUDt/tGdwTX4SbU+hTul8qLrk8EOhGb/3Ty0dvGEHcU8dMdwos8uNwz3q7O8Kj8k8fw739B7PKwMHBW7XXZUnuJmDkLydnnM6Y3dc9m0ImJ2HIDani2N1TK'
        b'HtcaX94cwlmJinDxsWGfDQijH1repJv5i51AYq9uOiV48YaWflryRYaZf1+8euZhJWejH0s9MhOtfSqBWoU7yKotxa28Iv5kbRlkvDwfr49WqclRxSouCW1E254m0ASV'
        b'UaNoY6O+rMJUV1nj+tafc3n7zmmMdJv97rm7fbtWRK15PWWbDqablmQLPGZ6rLo3UxPf7Xbbr86FJ5Dm/JatAJZe8DOX3oPBZBnvR1h06RVFXwcdELzpx0wpXzFwVjFv'
        b'jNqgsKEzkLOR8U9rTMBNvB72MDA1N9AZGPMS4KtUS5hl/A1PNxWD3FnMmHJiH1scVaBimWS0Xhy4AG+iBqV9S4T1bzpMlEPnrWCoZaTcv4B7zvKWhLeMHDJ/BmMnt/TJ'
        b'MlKd11F1M490gI3TIjJkNL3q6RDe5Y934xv5lmegLG/DfGJJsUv0x0fxOSr+c7kqvNb48rSpAus6yLTo76FDX0oIXRUfJnz1nQPCD7mMelmMTPWV8HcND+rzJo6L7G20'
        b'tH54fJUt88q/DUl/WzTKMOS5hq0vrlmbW/dBwqGxxxIDpfPvSvGEa7IHL774ZYj9+9vv/FK6J/yy9PfnZi37YOje4Uf+ukL1y+nBe5QFQduWTP/o1QsPjv3m/Jfc6j6T'
        b'po78zb0V9ucGrjv7qdKP5/Qu4b0crzjF7WE9XXpTtHshNTWYhe4s9PA1BF70ATCym/EOnhtsxSBEP223WdE5stlqWHonEr6bim/Joh0sbw3e7ap7ALoixBf0pbRatBLv'
        b'juFvYgJut7UaH8Hr0VkQ0J01i5l4dFrcF68s4808blSg0w6Dhhx03WHTMGs6TVSjIxlOdQa+P8RhlBBXpnR9NtynqlRcttBidHzeVeG2uSVlQpZj+wNT2tth/yaHN+HX'
        b'jcFuW48W7f6Vaq2lyuqD6eQs27rv963wmPPkfg8+7O2w68lGCyqFbtux24my4/vE1JHP9X1iIT3hEsFOF9KdLqK7W7hcVOT27ku3JvLY6eICahUehjvQvsRARGy9BzAD'
        b'QsuopMvrya6j9TUxU1XTVcQ2xQ+vw8dDuP4gYd01fj+zVmClouS8V4mebBN689m3n7246VbHrdW3dmauVc5p3jlw7a3Vp1ant+W0Dty5MimAOaORTDlwHGg2EXOyGMDd'
        b'LVSTgwBUqJ0KvlPEMn2qhagZnTM4l+TpWnJxGXXuoEsf7Lb0gSYh1VN1m3WalVeHi91sBOlXpqmKqjtyPyXkY5/ISZd9OzyMTy6718/9enTA96qPZagpIdMkpioJsvZ+'
        b'P3PtvRJ4TzWCqIBfZbor2wprilTonhCWeTvLCPAdNh9E4HNG4229yEoU6y9I4z4r12ij9FEVGsqNfVz+WbnREP2Xv5d/Ul5jeKj7rPzz/tyG+NQk++Vj8faLDRePJaxP'
        b'IJ8sFzALrsn//M26Ls71J1nAdPvKOFEtuq1ymPsGt/AmQsRItbGn20R3leGr2uEblna61pS4qdc9uaYR7V7W1HtTn5CzBt+rO5Lf0yLHrhb9zJX1qiDy3NXOlSXswgJ0'
        b'ckKRajrelp6flC1gRH4sWpWJzhq/q5aKrMTpY6HW/Fl5jmths7Wflqu1H5c/hMV9WB6srTbkVQ67FFoJ7FuegDmx2e+fJV/D9iVYQ7DMxFtxz0W3h7Jpy0N/+geFOwPL'
        b'HLepuq2qO8staRQST/EIt0nuVsCpsOi+LzvFBm2lrc7iA3ELLXt97eU9ZCaeXPewJi/r7rNLyiDeGLnLNpmYJXcGdEnjNfrFnQENdfbKar2FFknoHkzslFWSW2r05NOw'
        b'Ce6BxE6Jzmjlr5chJs6dogatjVxCrLfbQAYll+WSTdop1y+qrNaSq1xJVCnNScyhEjr9ndfDGHVu/vSzaQ6b0WbSKyX0SM5CyI6FXCfq7XLkgk4J+awIqbJTRt6cfuw0'
        b'mt5URdtLtBwhNfsRd8qKukXU5b5TVF9dZ9Z3CgzaRZ0ifS35Mi7XKTRCyU5BhbESAn5Z48cXlhQUdwrHF06baCFuSparzBPqD7KUZH0JY0RRk+NCZDG1v2abJAbJf/cg'
        b'SuCovvu2quTZ4t+NWcZ+m3GLY+K1s98co+O3GWpWCqz4ehBAE4ePs3gL3hONLhZRq2m0djFuseIjaL+tAbLgazIWCOluLhBtmko5WrypoiCGuFici8rOV+fkT8XNBehc'
        b'LG6Py52aHZsbB1wusGFKdH35ZOoXhTtmy8fLJlDSjS/llOKOxdqpDOHJ83sMpAZdC/qjXUl4J9pDLLTZ4cQYdG0uZdUbUTs+lASQjs/jM0lM0lx8jBpszcAH0aEkvCkz'
        b'OZ5j2CgGbUUn8C7KAgwVIejbHZVTBcoyslIOih9Lpm1pgFTvTIrSJceLGVbJoG1Q0yr+vHFlwCDeojeFfOH9Els+FneU4pt0Gkuyo5nicpBig8u5YeNTGWpPJhqOLyWN'
        b'QeeT40GyjGbQ9mrUzLvjHcE7sjTAfbSrVWriP5ivwhvyWKYXOiocCzzKDVrnd8xAkCAWiZn68r7vKQY5luaeGW1MQlfx+uR4AcPGgoCC7+LDPHdzvK84htyqksOfkQWh'
        b'Cw2oTVAxfgmtL7KhFxM7AfCCoryvMF7E9xFtCclJGoGuJcf7MayKeNxsUNMpjCnHR4F1pV9KEsaykUPQbXy/lFZ0VTiaWdrXJGDiy0PfnJnNV1QRa0lC94uS0UUQxNQM'
        b'2o22z3P0Cu/BZ2LwObRarczNB2FJmsBBr69H0sp2ZuUyWyPeFsPM5b4wf7jDvH/VGLwtqQBdh+pgyeMYtAc3V/IXy1ysQk28aRs1UFjHheL7g/Ehh89hBAvyz0i5iHgL'
        b'/CCcxfAWge3GrCQQ6a4lwwqROdu2BN/gj+I24pt4l4ZcPdOCN/Lm2oFoOzqN1ghGA89/gFYaK0ln6uc0cUx5eej7w/o7Kr2H16iTQPZKTuXoiHfg7b3o5Ta5+HylJh3d'
        b'p7UWdAFab7RViKBOtI8f5Lri4UnQxrHkVDEd4050HG3iB3mtSM53qoBfykD8ILteMCJiCu3PSHMPZkjEadjY5SOtFju/AJXouDxpHLqWSCAXxrgdb1pEj47LoOKVDsjl'
        b'AHIvs/i0CG8tjabXF6nD5EnxlpR4mJhEUuhsDe1cnALdidEQ+0GWERs53Dw4shAdpyVqltcmaWLSSIkRBPwupVJBtBGGsi6mBJabQuAGdAGE3pEgBqMO3jVie3V5Ugze'
        b'lUa2ZAYBkA2htH9x+H61RoxX8tOkJLb08mBBT0M6HesfxkqZYOFSAcy9/PXeNn7u0Rl0B21OGjclLZmhle3C6yU873cOr1PCJiAukxqAj0pOkNVnOKAFKtlf0QckNQ5N'
        b'SwaYyoQe4Au8c6FChS5q0Dp8VkPOJbg6dmwYvkZTekNLx5NQmyUtGXo9EuAwGK+hvS6NJfsDcFkrOasQ9+AAHrZK0WZ+i/xh9BLmn9kswQepKeP9+BUSoKvoJrpS0jM+'
        b'WcSw4xh0YPJg2ullpegUCAy55OxEgO+zeA2+hvYsnkGrOpk/iWnN+7sfbNvoV4Fe8mjgCN6Jt6IriRHxyYAGxjPoILqHrvOAuQmvxrc1C9ElQCrA0Mxj4wQ83JRCa/Fz'
        b'DohhLpeeHKl1zOXxHrEaEKNFjFDI9sdr0AF0v5oudG4yvkOtePEBvEPNqKMCqDEwaumPb1P3i2p8Y1o2yMWq6bw5HG7OjwXcwzCTQ/36jO5D6UUYXotOaPzRWafXLDnY'
        b'2cmhbRn4etd92C9WCRhh/b+ExOS3WahmHNQgOQd3iIm7RUssE9svhhoCa9GOPprup3un0HncDkRGyAxFp0X2ZNxBJ2k2fkC8sqcS/x5AYqFso2ZuEDpF0+bhXWiVBh9V'
        b'FuM2gAa8i8EX0Z1R1Ei5AXDBAYfbN3X6HjKY7/jQQpERX5nMT9vOcIC6PTKGeBM3ofsMul9qo8X7ohYEPWuJy8cbs1W5sLABSpAFE4TMsGJRor+QDnhcRW8mue92DgBk'
        b'6XOLonkAgam6BfhoD3DYgzj0gEEPBs+iGAU3LUDru1WJ2yaSOjlmWIkoCR+U8sj85FBAYtLoqUBWqU/xPcN4HtVsL0Sni4AUtwFFX8KiK4V9YVHoOKqr8V3NeK6En4Zj'
        b'DL5K8Aa9MGuLlWCNtXiHw7PehcgGoBYhkKmtoXRXxQ/G2/Ee4EOnxaC7DLo7Cx/nqdwVvClRg7ahc1BOnVMARXNUiUKmD9otNIGMvoZ2rR6WECiEgGD2dHQPCBy+j0/a'
        b'6W1Re/IYTfxE99IclN4jrB2NT/EDfoAuJOAW8rZaa2SMqBWv44nOamURMdl0dTnIPrOHYD6HH9AuL8SX8SqqIMDbpw9gBuCDM6jZkMLaP6ZHH/5iMgAsh1lGX3RNiDcM'
        b'Qm28+ebBGfg03iMiWlF0h0F3Ak08QLTAgLfiFsKNrAquYWrQHrSOv1FsI/SrTaNS5aCjuAWdjcolu63HWAFkP2+moG7JkOA9coaJSkdXGXTVNIz3UNs+lOnmsYpv4+bp'
        b'AhO6gnfTvlT4451WZc+AAEBOsO/wucyRFLpO62RMWN8TQoCu2My0NH47obbRaC9ugUEvm1/H1OUtpUMO6oNuaRYp0bls4mLfqilU0d4p+ghhQ7RPp7rL+RFD2VehnGLh'
        b'+bx/Lfq07ihDW9fiQ/ge1Z+i/fpGphH2hnHgzQes9RtAfH96M2nua7PqXh8b7Pf5H+wPh9R23Dy05nbfQ29/89txK7dvHzf7b1fenrEoQrr17oSp/ff1GnR02bjvJe/W'
        b'/fL37wkUX3yzqGbWyAkvfDcyc//DVunt506f8NP/7nv/JYN7R38wvPO1mbsOfvbLsN/EthWfFf9Vu17zcPjys2fn/+lfQT171Oz9vnbVkF+ceJHdcW57Wc8jba/8VrK4'
        b'YFhw4aTnin7XcXPdN8U3zT3T9q4Z9Pqm4x2jBiVtuldQOujfiisFgzanP798uN+EwHGB6caWvuri/b3SufRPP9z5/ILnzU3DJxSEZ4wcark95aPW52c9nz78o4nqsE/n'
        b'hN0q3vTrQTMUsoLwiefHnU+fFXor8JZ2VOaRZuOe1qbZdyM3K9u/eq99YNGWJeviF/zjxMaoU19eLqn8vmVa2aGHxoXc63sfLl79ACvn5VQ13bx+RFwyI2hqe/DvF35Q'
        b'EDC96cU/R341T7og85WTfR76/zG3amRuVd/P57//wZ2Qmnkd82V37x75pflRy9LM37256p+Pz84W/fHDzNe+aWy8vvbFH8IvfDn3UtuLU4Z/mJ9+ZW3mzeE3Qr9cttlv'
        b'1+f47A7d7gHHMl9oP4Y6xq09seVx7AHr869MnPfha+/tGPRW6ltvbCrL+S7jj7c3/fG7G9KA5TFfqsf8Y977Qd/9Zv4PH1pGtyx79lRg4/ePVBOuT/v4zIR3DGd3ZBed'
        b'2FVw7dH3Ax6+9GjwXKGyB3UIQNdxS+kThgZxRk2XnUHkSHo3/xJ0CJ2JKV9KdOgc2s3m4/2jqItf1UQggi1EcBAzwglspgHdC0/hLR1WgTxyCnbb3RFB9XILvoraghoC'
        b'pGImDB0Q1GWgs7x7+fEGvFKGTsVm4zNAsR3K3hB8W4DO6dFdXhF9AV9Bm92N1Vi0ezKQzStCekCTsTgFUPmugjhqqEusko9wENHeh1rZDsWr1KhFM9Kh6gOyls/pos3U'
        b'i2IFOmLRhJYXklE1sFnoyly+wXPoJDrqsn8j1m9D8CkVuoIe0NlYga5FOfwahRq2MRJdnjaezgZa1cdKLT8cdh/LVoT0W86P8w6gIlkFvulxOZ8E3UJbaJ6e+QN584vd'
        b'eZ5GGqsGUQU5cf4D9pNky0AbnzTSQPfRJhu9ZPIwvppE7ELIYQURWgC37S51TUFMughdbxhC18kPtYyBnCsHdVeJOvWhq7W8Wd+a6fndHELmzCf+ICWIt/pLzgQAaUHr'
        b'gohdiJtViHqUt08A/Gzz1U6BVseraxYxjEtdw6wIVYezQjaU+pUTL3HiK+f64UJZjx+Ik3wa2G+I41JAf/pLNPS9OQUbSNOJaTPJG0zKc8FsGLxzrORhaHhjQJcWBvrj'
        b'rrq3EGXbz/W24/hSXSr9a4QkcE4Dl5XOn96vezN17tYX3wftVPnHf/2KaRK5lH8s1VL8B8ftpCEF86SWYjivpbgXzDGflxKVWnns30qnMLxGkLL0l1PxYUSY1P7++BbT'
        b'H29eQHnXFFkMIgeZkegM3sdE1gDbRzTgeENMQBLUngjAyCQWq2ntxoUSZua8IVB5eey5+jiGHuK9NVnCZE8dTiMH10U7TvjDlrEjU74UEW3J96kqB11tt1UmgUjBhISg'
        b'bUxlRqSDTVgclJQMzCu6aUA7GD3eJuM1BRI/Ji+ENxLokzqOr9eaF8IMaRwL3FC56bPIGr4HD6H2vDkTSWRs2ZQ0Pqc5NYBZUw1Sz5Ty2BGlCj4n7hHAFBclkkjTc0vi'
        b'+ZxtZn/mn4Y4IoKY2meJ+ZyPtP7MhBw1iYwdOreRj/xDmh8TUdmXdml66FD+MlW8YWwK5RhLQHzfTXhrUQOLbo/s4RAayvH6pPh4IUhEOnYI8IqZ+Aw/RQ2DmSFTNpCl'
        b'4jYaVzB0NXTT8WX+oLXveBAUzwIrRSWVq+h0Dd7jT+nFSg6eaOMSnhPekg8y6x4yfTdwuxaes+fyt+2ezuyFOwBYVEV4FaPCR+bw39OJFjHNXDi9JEBW7M/w7NMNaHUz'
        b'7sDbyI8I7bUCl7QOhGt0I5qukbkvcLGksn6AmS8x/TLRdirKatGFcOeZKlqFziU5zlTRNQstZ+pdXkRPkHriwyzezIYONPOdu4ZPoE3UtQdviWEWCa00GirfNBmdgbfF'
        b'+QAKi/tE0Vrk0Kub/DEzXqWBx9559FiXrsmvxgmZPLYXHVCfXqG8PnlPQxDZM2x2HcOG1hgnftJXZCU3eWo3DqjdnF+A44PXjmp4bVj+itdSc6R/vvHniPoN+5l/Hs09'
        b'NXbqkJnPRo/7lbS8ZoB0+qjAHieOhlRUvvLvh7sWf11cfGrL2Mz/t7krgWvq2Po3NwEChE3BBUQiFSSsgqKAVgWBimwKuKLFQAJEWbMoblUUFUTEBTeQCoq4FhHcQKvt'
        b'zOv2nq+vtr62pu2zrbV71VqrvtbWb5abkECC2Pb7fR/5Mbn3Zu7M3Ln3njln5vzPf07JFrfpRxJy398yN+rV0n9EyzcvvjKqbMLfzid8l/5sybgZxz/9apHIV1H4s1NN'
        b'ynKhaM4Pqve3tMfm7/y75eXXL3tbfXn19NRM15D6xbkLJB+A75M/WL55/bKyjsZHvLab1UOqHB4dgfucbgYdd9vVv+x9rwdZno7pLukH2+4c3nrKZULrmxOL2YFHfm5u'
        b'kzyufUXxw3er1nu9vSVv1/p7oq/Wbxr+QumLa0WhW53UK957Ma7M9vmsbOvkaOeMc5cvFc9Y9Ez/4jcriz55uO2l1TtaVv70TV390K9brn1wabnvPXbsYu/jBa8d+1C4'
        b'6lf+g7sv3Gr7l2SQGlMwwjWwRU0XjxNgh3n/Gnc1BeNsXzqcLPwnBfiDCl88Bp1mwc68YjKoPwe3Juh1CHgenOMQNdWgkyJuLqCDJ8jIGgcbZ3NeneBF0EIQm67PafB4'
        b'moiMzWnB/jheM0bpR/JBC9gC11HHz9rYdAcHHAcLA/AreBiH5JkM95MRGdmeRydTTesw2NDD5xXrWmCjP/HaH4feNtwOP773CoYPW3igAdTnkSoGgHZp7FKMdTJwRTkD'
        b'1tCovS87yTmmJtgc7J9EJysHzBa4wV3xZKx3x1Go9DRML6L+xY3AF+LFB8eFSN/CGtM42LDcxcVQj3ECx8ApUkIg3OtF+8gCqRvdlBR0b+ppSw6hny4RfUGCxFJFV2iE'
        b'seAoBcAizYIraOgz3bQY8UAayqBajSRQZdAU/0C4KyEQT0yjhsIjfGSTtiG9AxczRxTJeb/6gEvWxt6vqWOo5tKOGn+Y5NocbwEOzmQELA+8qIEnyc88sA6c5pb/M0CZ'
        b'LiYBPOpCH8F2uBr7eFFXgwwLfGNNeRq4DiMPWSQ4BQ+iNmNNFFyANXptdJwDcewFF8C5QJ1eVpxMNTNjtWyBGykpuwTUUDfbONgq6NKowF4l9Uq6NCPQzxdjO8A5f30c'
        b'pOOwQue20KcVMQF21iOKVbaRYiVSCngilgRAQAoQVquc0WcA+gxCH7xvj1KW/LNEQepHwyWgj+Cm5RDBFzbuQtaGZ8M684SPbfjYAULIYgQZUl3su1QXXL2BP1svbe5y'
        b'bzuDkls9tSRnU+ul3apCfYM1EvS1lXwloa1avDWwG/qL+PAql+GE+PUSh1/s66sV6nw+dVt4XYl6ShLYF3bDIr4ZZKWeLO2SdT6tKGNaZEpkYkbanGkxqVq+Sq7WCnAw'
        b'Aa0t90NqTFoqUQHJFVLt8s8HvFBiojl/3F3nGLyE5chnnZ4W5WVvgf7tnC0dhUIreo8tiVOLZbeP4EfWScCFzLAxCJkhtGR/EVix/xUK2YdCa/aB0Ia9L7RlfxaK2HtC'
        b'O/YnoT17V+jA/ih0ZO8Indjblv1QaT9Y3rL3tUf1D7IYFE3mmcA2IRqI0XAAG+FOnT+RBeOYxp/7wtweK9Q6MhrVpO6suoIaB8I266D7lrH6LX6VlbVANhzpyxiZ4ZAt'
        b'kFnJhHqGXWuZDcHliDiGXTuyb0/2McOuA9l3JPtCwsBrQxh4RRzDbn+y70z2bQgDrw1h4BVxDLsDyf4gsi+qEci8cLtkg/eyNZYYebPQTuY6mGmwx9gSbt9Ntz8Q/Tfx'
        b'NvNk3hxI3YpEhbLd4LDBMdua8PQS3lz0mzVhwRUQTI9wriPuD9mwKt4GaieINtghK8FT9gxhyHWSDSEOzyM4htz4pJhfdhrhudN0rK3oJ0qPK/bB/CaYxkpaIMMviaI7'
        b'uabRjm8ahpVzzFVoqzBTVZiHSbYxGh5HI6Y0oTgasrxITQNyE2h8tyDRSuycKrHSWnMUbJipiNskS8dCGiAVcxbJshdr+YsK0LF8uUyhyUfHhEWo5UsKlTJlF0evSXJc'
        b'4/hbupjn1si+suHWg2318bf6So9bJuF/9mOf6XFxR/9hetwns+P2YMI1GRXgD7LjGtwQfTtw1PReWoF+NteGArE0ryhXGmCqKeHirFxUZRaJTd47WW/vXL0meHmfokee'
        b'yNWLnkUaxjk6dqY4T5qJ2eHRpmFkbElgt5jTlHHOZCuMm0761ifEoCtMNJ5rCHofnsAUbI4V2HTYCHNMwX1kBTZZaBdT8J9gBda987Tb6Z5YIeNu2Kgn3TCdoOBid3N7'
        b'YqU8R6FCPYwEFJJj5HHyF2u426YpwDG0/xD5rgOdWgnwdmLE86p4eJahPsWa0UQQGeRtlnwXVKBBktgARgy56yaJHEHNUFLm117OjI/PZRYZr/Oy++dSQt9J9km9EfrC'
        b'jYSKhhSpjucK3Vckgk1MMCn0u0ARM2jIUQtm2gLRKd5KjtB3F1LCW0yWqwt9RtCABnS550A5tvZtQSPcDdtJ0atHWDIiwX1LPAEyetx0RoNR7aB8JDxnsuQ4v1TDAlfD'
        b'aiuZNdjhD0+R0rZYIm1oGsvDK9bZEyJoBNx8uwJTZcFybPhRs69bK88gC7DGFhxwARco5Y2nLeMsqMOOEqLZqnxKKAQ7np1nqlwfZNwEUpcbg0I7wTG4fZYtypChuPj3'
        b'O3zVJlTEeJffAi6ft2MjRTHTl//+fPnh1a4+patuDBAKx548NfdNR5eRFf9YnbQ0KzG3/te8Sq8Db9cnzmzLvPvKwUcJJ96rC1X/3mpnW3AuFLzd+sWY+9JbB8Y6Jcaq'
        b'IlMvVFy/90zJ4n/dsbkE6pavd3mc9tWhb70CXWqW1FTuyn9h4a3Z3/EuvloNH0j3q5+59vuu78b8Xvq8xIbYTrNEk7qYgTlj0zZS4CZxICZMqr1nD/9w2DlEIPSZqMYe'
        b'XgKwkcASuQJwUOuN1LXDA+4WwBN4zYFYghL4EmzUm61NnkZWq3I5MVoTFoAtfoNhR6ABCTA8O4dODDTNh23oNrVRq1pnU2/3JmdmuiVm9dPZh9Q4RLZdKbEvPVNhs87s'
        b'H5FrZPYHwuPUkm2Jguc5M3XLAiMzFZ63UmMHNlTGCXCcTmQEIIsSR8QE1cj2BRcz4xKIGhtgySSCMitQD9dP+MtUfz1gEr8nXcYds8o+yp4DTOrYf204DmDDPT0XMFI4'
        b'THMBv4KTV3ECcAJx8jecvIaT1xnmyRw5wr4UYmd0SRK+zt2+tOsjNjVJ3rP5T4cr1OtMZlFwM1BbKMayqy4DSmB8qBdK4L7DLMt0DK0GCpTZRs3WNeqXod1aQNSBP8YI'
        b'bJ2hU5bM1puur9eD1vuXUBELMpCKZLbO5/V1utE6DdSoP1of0oTM1ifV1+fTpStJu2NZ/wTdsU47MdsCmb4Frnhyw0CB+cN16m0fc3XmGNWJelmv9hjUKWEpHJpMlujd'
        b'aJOy+AZNwY7p+B0mfrRTUULWpXDcCZazWG1IDGNRtkjvpm7RJzd1zBhl0a/PjFFyTJXZV8Iokvlp+KIM+aF6FIn5ovSIZV9/sa8hdBrtEzQ2ymTIdkNUWtoMTCLSd7NP'
        b'X1GEOLUwHxsP1NLGMeA4/LM0s1Cj5miYVEhNNdc3+A9Tnshxl8gU2YQQR82p4cYXxfU3iW6Jui2Hi3BnQgPGf3F6AidpbxZd8BgDO0bso2OJMW/RGPYr1dZ7vKhin8hM'
        b'pTwrtwAT1HDmHYlzZ7KhXc+BSqXIKSCPAqWB6cFFphIrDK9KgSydHDNcMzoLJpjc5DHhekMG1xQs8cdzIzo2Y5xDT2ecZc72Ik+lgpyPKbFw34WF951SK9v4gvBVK+Sq'
        b'v44QywcTQBHqKonY1zcfW9focpb6+v5hiiyxD6HDCqCsUk9TdC90WH06/2nJqcRmSLXMkVMF9q0ZRgCPXimqfPQUVcEScXpwiHmKKUOQCHcbNXJ6OYoC0lBCPB+dmDhn'
        b'Dr4yU9Fu8V+RdGk+iZUrV+Jhyp/wz+mNYoMGhfTeoF55s4ynSOjbEqR7U0w2iypDhmxbqPpRI80TpxlCanQTRgavCTqK3sgClYI2qjDbNA+ZbCF6Mkh/4BNIwGBpCd7u'
        b'IwUT/os0KkRF5soUWblqBeHZUnWxwPV8Z82WGSAOxrzWcg0SrvoC0BOsEHNdhCRUPnrjYmYEpEnVmXI8/2iaFSxAjB4XGtQ0T5O/SJ5ruv8DxKO6ZSO1STXZyzRqORo5'
        b'cOBo8cxCpYo0ykwZoyPEkZrsXHmmBr966IRIjboQj2+LzJwQGiGOK5ApFivQw5yXh06gXHWqbldu5uwxppr89B001lQxCoNm5T9ds8JMlfd0/RJOOrKr65/Q8yYPptEn'
        b'GU8Udmv3Uz+JhpefrURX44P7Vt8maeYyTY7E/ONneLp4rJf5B9AoY3C4uZzoMSsI6kkDSn8M7V7MGHPFjOmtGPRQ6K+vlzLCDLOZvbRwo8JMXJfZAY2D/CEJx20RfQDp'
        b'pEi26kS5TyodY80O2F2IQsxLj4ZCuod0HJ94tCsvQP/oMRfjMSisF2p7PRbRuJiQbsWE9FoMgS0acSX6EILEaDzehJo9TQ9zpKfGzCCSGh8Q+6CXnHvE0W033w0aJeaM'
        b'RKPFZG7LX2yg28XMSBH7zIJNuUr0kqK2jDbfFAOEZVdh+sNco3RFqRZplKqejepN3TOnXhJVsu+an15FizSa8++bDkMwoxHiJPwlTg8ZOb/vp4XQ00LIaebvhg6MyqmQ'
        b'3D42nXt7DghSFZ2Cv1DGnvnMS7EpcqWyIChWKdWgJC8wKFaBtDvzUotkNy+rcDnm5ROuwLyA6q1mJJVicpEShmS/edFE2oZ0NpnpZpjrPKTFyuVqrFngb6RgjelVv8ss'
        b'LIkQ4+VjpD9lY60VHUB9bv6m4pMwBJieJc0T451ez8hSqPELidJe1T2Ke8Y56QYp2B/r6QGjgseMQU+a+TZhyDFqEP7q9YnMlqKrjUVCpbdMBLSM7hD+EqePMZ+RE3M6'
        b'OthenmgdnDpCHIW2qCacHjK21/z6V5ucYrym12t/60Da3Jn0/pgX1hiajVS0qMgkdHvMS8RMRRYqMG4yqtrEG9kDWI1X7k2uq42ewjKCIZ4Y0ea/1OI5RsP5rx2H5fEG'
        b'UDhwDmwicLiAleS0X3MsGKGo0xL7ffL4KRwcdiN4kcdh9GAFOCvggX2yPJLfYfhAxj9vGwH1xrrNoO62WXBPOgXurfcIZALBGiGt/QTcBg7FGyGfE0AdbIGlcAcp7fml'
        b'K3gPY/Oxf7NbTYGQ0QTgyxsKD/mh/JgQMRl7FYLjUxMJN2gaA0+CSrgfdqQwJaOtcxaBaoIXGpyZxP7NkimZlL+s/0ezI8deoSuAC2Er3N4j2lHSIrykhgqbQhcsjEgg'
        b'q8AekQQ0hJNpQ0V423YL1TW09dMHMzSbX00CCxzLcu4//ihlUtaFH5m945eFfCa586lt3sioNU1jHGvfX1v1lvKbUat/jPzk3fazn9QXZr9xzvbv/Wck3PcZuskj1W7E'
        b'3IX7iy3dzqZcDvjwzW2f7X/ni/TssMnv2aZ/8871gYOuhrrl3Q493/zsUu2BzeMD9t4MyT0pqj37KNPuwGszcme/d1fzcfuHc95PDtBc2Jo5xzvim7e+fX3Bf4+pJs4D'
        b'j8NTVaUD8257/v3ew6TRUWlXvE/fs//5t1T78Q2d7rmFO7+598/039ue+eRYyev//uS322/PWtV+w3ZJ1HWrhRIhWVgaAfbCXQQn0gxP67EiAYMdCBokFJSO08FEQtMx'
        b'+xUsLSZunEGwbJAfrEgGFZI4cFzAWOaxnrAG7CbOk9MYw2UzT7BbDxTZBFtJ+KMZ88UmFpO6rSTtyQH1gQICGpkCzkfioEpw3yiK3zAOquQAO0jFbBG/OwNhooZyEG5b'
        b'TK4IlsHN8Hx8QhyoC+QxbArPdwnc2BPhIfqLgpZjZziyfhWLX+NVhh9hMsZ84Ah5wwl+gwbdIS6HZO2K5bmSb+Fq9jHLDtFvLxPpl2n0EA4uoEfX3DX24TZYuLJ+qvZL'
        b'BAaFkDKNAR4LTa1eeW4zsXpl1FTzCA8Ssgn7IDEbBPqQTU/BoqQsxqLIUGDiy/DoITC9qMD82A9HAJ6Kkft5YQMSuehmrfC8Am4FFSoNhvFWCZAAPMFbCfbDHRQDQgAY'
        b'ndErbTGAtGXKLGaWFzhJKXYrJ01KDVWDqpEU2nqegac08DCpq2HsSt7D7EgrLOfYJblcKITGFBuM2IC7wV4GQzZmcIQdKlAeiwEec+EBBiM8wJEcUkq81JIRRVdjtwFR'
        b'2goVhV2cftaJETuuxaiNhM6QpdSb/4E1Oji8RYAOivb79aM5i0vsmEHCiQIM5fhgIo/mfDRExAzyryUHkwuyac43CmwYZ8fbFhi18dxKH5pzs4MtOjiYhw4mvOFoQw9e'
        b'nmnFiBZswE3KG+uopmBxW9AAL6ZOg3Ue06YxDC+aAaVgO+ygkQa2gPVgzaiR4AI8jykSebCJQcPBUVhJRh41bIOtNmBv6jQGA/SaMX9EhTuF2K6ZAg5mgE0UJKIHiCTC'
        b'AwTbkREF9k2AWwhGhABEwAFYTm7XEjR64RUj2LJgGDNsNjxHjoamwyMYmZMBOkOYkBRYTXEmTUgSdRDAhyOoDWAC4HF4njwZz4MDsQTaUYFHL7jDgsN2jIfrKLbk0FK/'
        b'1Gn58IgYPxntLpag0duKIFtCQNWKWHjWOF4+OzVNStEXuMMFC3DQgUoLZsGChI8TwmnfjhUJGUfxj1b44NVlRRQ9z4L1haABrEvFXcvAtYx0GmwmZeQGOTM+YU3YCWbF'
        b'IGkEF5rqKGwHL6VOS4XrQYOEYSJW2sLG6aCKPrGb3OEpld0EWDkKdRoLjjHwZbBJrSjzjuKpvDDDT2px/tZ4jPNYn7O3KfGXhLm17971/f4zgX8Hb9HiidHOww5K133R'
        b'WrFFKUr/PHdI042maH/f+Pcf7fv+v1/9ONVLnqZ86Yzsw3f5z/5Wc9T7Jd/fy5dsjU4LLok7eGjH9Jmja+6ndI745+trc1Y8FA65stCt4UHzxvR7P40rO/0P7eQ0yXvP'
        b'yeptEstK5aLI6wtjoiyjYqNet/q8w9/Ftl5Y//sBuH7q0L8F/PDoxa1fBO3W/OL+0wXH0JCsvbNvPTx0J2j69p1ZV9LCXms68s5/LfK/kkhLnePDD50eUZi5h1da/13w'
        b'Gpd+xzUj2k/Lt396uU3ePL9MdWNRRfz7aY864966tOde0bCkXfkO5yJCXGb9e0hd89GqO6fqb3928W0w0SNg+daVH78Z+PXW/XkOpVHFbHilxFmNtRZwwEdpPJiNXWRq'
        b'OKsHp0E58dcIls+C+xR+ZIhEvwrheRZsjWbIAOXhNd9vKjgEqhMTeIxgGA/Uw73PE2eUGFgPWuEGeMGY1xAegS9S+MfJcFCL8SEeIV0o05NwO9hDcZfly0vAmVnxJsKV'
        b'i2MsrEH9EuppsgfsQMNxZTJohKu7XE1WZZJfS+BuTDXTBd4AW+FxdlSiO3UkKYUNJdQd5qVxhi41AjdQNoNiGargxXlGABPYIGY9x4L9xE8mBNQE6N1kdD4y8BSoxn4y'
        b'oRrSQ14Zo5FOAnaC3Rx8FbTZeJCznZDWuQZrrxGgowvZYQ/W8qNAM6AqAriIJNJ+DOwAHfl+hsAO2DiC5BgPL4FyXAqolehxHfYr+dHgKOikuI598KiAOszovGWQoKsk'
        b'HjND4UGKbjifLSEuOR2gs8stZxA4SO6lCBxGPQKOduORhCdhM+lJ26EzdU47epedVbANe+2MhqUE+BwMLsI2b7jX0H/J0PfoGaTXmHZYeUJgQEL0QpSWxT2UFkGRgFNO'
        b'RDxHVkhGfEcOtIqxFY4EXcESGmRW/+nCWRB0xZeWbpY3bYYghYeluAtH4o+PffUFD4XWwgcCG47ejGgOPYjTTLe/G4UaX0fSVmr46bfLLJWaYV0qrE+YDSH8p3nUsMqi'
        b'6a6ymCYRs0rSkCik++DhFEMWse4cYlXwIOER65CRkWcFeho4VjCGD07AlzEvGNwDWylM8CQ4CNb5WTFLYANTwpQ429DDRwf380tmGV4KMy8V1jKwSfG4OIyvwj4QwDLx'
        b'2cSXbcCkV1aKkpRHzvzbxn5CaV1d+7GwcxHlDR8N+1x81SZwSeVZ2U8ut/5zdZ7tXaeH21ZMzLzlOD1MOnbXZclPX0UljOYvP/naao8azwHW44VvTF8TdqbpetXhD1xL'
        b'F4yPKJevCZj37aild1+XHh8Svl3YOP+bmSMmtRatvqh49+ytU4raweD6pSGPol5ucVpc86ayofDGteK9iuZvq2tf27jAcehN186P0k8MHlG/eF/d0e8c7M+Mcd02QOJA'
        b'maaa0zwpJxgjADsmYEqwGPgSkUbD4E4ZYfQiOAxkXtZSQjCFlPrVeYBzmIZ2f1IS4fTCjF+x8AiVIx3wxEB4CF7S8X51kX650+iySIBuRvJ39SqOVMyAUgzWwe1ESvQP'
        b'BftSkAygzGB6WjC5gArLTngEB/JAlngz3BKUzBGDwdZUKm7bkKRqJiJkTxgOcasPcItD1pIrKIyfjC4AWd5b4mAVxwwGdvMpxK0mC9ZiBi5QkYLGri5qMKQLnCFG3lDY'
        b'IsbUYIdgE6wI0nGDbQwnRcfFwOZ43RMYm0aZwbxSyYk24JI75gVbDI5xPYeJwTosyY+eS5YYREJAekozHqeezyIdMnUOqPYLQtK0jkZCILxg8By8+JcwgxH6KiLaRvYQ'
        b'bcwqz4A+kYNhQaEnB1MuYXpHfZUY1e2BjqmG9xBLTOmAj8ySgenqQ3LPGNhBd7kQ3ng7SdKvOwpsKcMYQsFeYZ7oqdjJkIjdanm+imK5uvF+Of0p07gP9+gifjGx+J7N'
        b'UKIvR0sRoeUa8JiV/DGaL5EADzKCx4LHYn6/JcJxrjwK226EHTNVVHGbCy8i3c2CsXNlkeQ8ZSXhJSn23h4jUA1E6nCo8mTM5nEFaychdXhg66sfDhrpkPX9p/ymO07v'
        b'3mQkSo8ppRmjd6YMT5v+sWyrpfLby5k1uXX1hb+/8ej4hKDJEwSxkfPrq5/7dUPLlOyc2rpfRR+0NZbmeM9/blVnTOzsnYLHb4VcmV//IP6QeM/1b3f8h425b/dVUpa8'
        b'5uCS24PurJm8ueQfwYcu3NhkO6H4vfXCk7d+u7Lc+9oIoLo/18Et+uXqN792e+vLxhkfeg7ot2prcWxou+BIqzpz9NWouGXOQdd2nfrn1Z2XV4bf7vic73HtRmqddEPC'
        b'hT1XYj9xviud/87h4i+mKW1rVo7s3HbI66vHX+6NX/yae2b11I93XDkw6mdtbM6thOz8YQs/kthPOGttf/i11OQq13tRkY9tWY0s+NICCZ/GDDmlgOtgJdJRwjx4YQwS'
        b'GA2glROBYGOSsQc1vACa6FzQNgklbdkI978wZ4g+ZHa3qZ2SpJ6zM27/O4/gUydI8PD176GphCBUhRkZeYVSWUYGETyBWAK5suxonhhP+jy2ZPGkj9jV1dnZ13kiOyKC'
        b'RyaHxtvzvW2ZVeziMJ7yQ/27x9eyGRkG8zqu/w/6gKe8pn91cUux7CGRhid9bYKVjAydm+CuLBzeBg0BFckJoAJUWzGJ+faD+e4r/BSu0yCrqsbSbIKne0W4PRjpbPH4'
        b'wS3HSVPyNk7KDO83qzXlmrv83Zhlj9LL6vrN++cm7+L9Cc/Yjf4pfeXSL0pz6q9+vlHy2wmnDIWX/9VrLkFp+95qjD7pVX4sX5U6c//U2uf85n10U3OtXMqWNjY4Sd9p'
        b'WLcODhj3ffErTiP2Xnn1xho/tuDcjdKc6177gHP0qnuVn9/jC4t87i8PQdoEGTXPgE7UcjQmJ+Mp6k3x4wZZMbagjYWHbSUkRxbSt1rikwPskpE6j3LhYdsJXuCDRiUa'
        b'V0kZxyIZev1YYceTn1aMHBy078cfGhZByUZ3g/3gTHxcom+iFeMOX7YUsEK4JpPE7gH7CkAFrAwabGPJ8FJxiM/V1DDKgS+BGr+psAVusmB48aiQXHCIKBIrMgYSPjtU'
        b'G9wkAu1IzZCwcAvc4k5JQg8i0/KsSp8D7EImjU0cC1rt+pMMSx1I4L4AzlwC60CbPdzITwI18CxtbxUsB1W64H7PgkM8sA/UrSBqCtKD2uF5oozSiXdwfKAFI+rPIkvy'
        b'kobGFtoF1uOY5ihLEcmSDtdaIC2inQWnYN0UYu/4LZqMMrSJQPmSYg1sLxahtBxu4TEDYTUfkKiaVDE7kK6JJ0EUyPWsBRvxvFQti7S7bcMI41TUgkDc+0HxSNBsJvH9'
        b'K/EdcMsNHS4AazUuRsGP3f/vX7Hub5z1E6SOCSHUBaTAkRyEdjb6oP7YehPxJvC7K0OC4VRtIHLHQ8vPkxdoBdhxV2uh1hTlybWCPIVKrRVge0krKCxCP/NVaqXWglDA'
        b'awWZhYV5Wr6iQK21yEbiD30p8To/5gIp0qi1/KxcpZZfqJRpLbMVeWo52smXFmn5yxRFWgupKkuh0PJz5SUoCyreRqHSoUW1lkWazDxFltaKgmlVWltVriJbnSFXKguV'
        b'WrsiqVIlz1CoCrErotZOU5CVK1UUyGUZ8pIsrXVGhkqOWp+RobWkrnsGYetZerd/xts/4uR7nHyOk89wginblP/ByTc4+QInP+DkS5xgZlLlbZxocfIJTr7FyS2cXMfJ'
        b'1zjBfG/KOzi5iZO7OPkUJx/j5COc3MPJfZx8Z3T7bHSCNfphT8FKcvwizMZeulm5gVrHjAxumxt8fnHl9sVF0qxF0hw5B0yWyuSyJImQKIqYMVaal8cxxhJVUmuD+l2p'
        b'VmH+ba1lXmGWNE+lFaVgh8F8eQzuc+VDXe91c7vXCsfnF8o0efIJeOKfxDoQMAIrIdv9UXMey5JH8X8ABhqqsA=='
    ))))
