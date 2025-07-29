
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
        b'eJzsvXlck0f+OP7kBBKOCOE+fLgJkHDfasUDuUFD1CqCAQJEQsAcKnjUuyiioLWCF6CtYrUVq1Ws1tqZttvt9tMPKW1Bttt1r+52t7tf29q6291tfzPzJCFIsNvufr6f'
        b'3x9fXjqZ+3zP+5r3zPMbyuaPY/79cgNyDlNySkfFUTqWnOVH6djlnCVO1JQ/OTuFxfiizDFKIYrllPNCqBRzTBb6X4PKzmeX80MoOddSQsUqdwihyq010FQdz6lWwv9m'
        b's2BBdtnCpXRjU41Ro6KbamlDvYoubTHUN2npHLXWoKqup5uV1Q3KOpVMICirV+steWtUtWqtSk/XGrXVBnWTVk8rtTV0tUap16v0AkMTXa1TKQ0qmmmgRmlQ0qoN1fVK'
        b'bZ2KrlVrVHqZoDrAZnyB6L8QT8m7yKmgKlgV7ApOBbeCV8GvcKhwrHCqEFQIK5wrXCpcK9wqRBUzKtwrPCrEFZ4VXhXeFT4VvhV+Ff4VAYcphb/CW+GucFQ4KFwUXIWb'
        b'QqDwUDgrnBSeCkrBUYgUYgVP4arwVXgphAofBV/BVrAUfooAxYzkQLwAaxy1gWX+E5OqDQqiFIETYUXQhJ+msgOzg8KoYDuxtdRszkyqluVUJ2EXV9supR/674GHyiWr'
        b'X0dJBMUaR+RXR3EoHNcXYCyknNZTxnAUMIJby2E73FNSuBi2wY4SCezIgxfBRUWplE9FLuTCV9ngloRlxJOZCXc4pYJL+rwiuB/uK4L7WJQgjw0GwTPgsIRt9EJZROB0'
        b'TkER2JEXm8ejuFwW6IUvw31G3Kcyv1kFK8BhlCKFe1BxHuUK93KKU2EnKhuEMmyBl+A5eI0C7XBvbDPq1D5UhwBcZoMr8ECCMRRlSSuNQKkvOoO29WuN8PJauA284rzW'
        b'yKK84QEO2AdugoOoryEo5wbwMjgP2sGBuFqPAmk07jA8gMMOlH8YF+yQplazbCbN3zJpTyFnjl8Fmji0mly0lhRaQwe03k5opYVopV3Q6rqhdZ6BoMADrbYnWmlvtNK+'
        b'aJX9FQHJ/uZVZpU52KwyG60yy2aV2ZPWk5XNJqs8Jda6yrUPr7L3lFUOZFaZt9iBcqao3DPhq2P/WL+WIpE/W8jGS5++V7Ba83pNExP5dqYTJUIzdWnN6tiiFTOYyK5I'
        b'HoV+5x4oWq35oklPnaM0AhTdkevDve9Ozb3n0RIP2VcT/plfR2kwHtmX2sMadKBomrUl8SPdgzgHJnpd3ZduT7mxokQb/8T61ueFpOepccoYhxLgLjAAt6LFbY+rgAcX'
        b'R0XBvXG5UrgXnCuLyi+CB2JledL8IhaldXOaDW66TVokoWXMBrxIQvMi8SYtEIWXKFloXQTu/+QiOExZBOdiHZ5FI47V58ySw6G6JdKlbIrNoeCJohijO4ovRWD6vJyN'
        b'5uKp+aFUqAw8R7KjXfc82CZfghLqqY3w2kLFQpIdDsFdq+AhhNQD8uOouFKwzTgDR7/osgEeQtOjhFellDR0Adl/xkzQJgd74ctFi2EHj2JvZAXArRpjBEqKBHsX4U0V'
        b'UwBvgetoO+wpXBwFzsXmkq0ug+d4YLuXntTtvuxxcJlPUaDfdxY1SwmOqp/46mmu/gOUdOGT7Y1dNwQg3mdXyXsF4zlro9Idt4uzvdPaj11uL5DJI2e8trB57deSjzb7'
        b'9b72k4SXimLP9GzRvfu3b+e/+Du3gStb387f/n+u1yiy+vXHqh/wteIh96L9zp0LVH7C039e9GaPeHjB5wdTv1UVpBfuO7QmhL1hET/xyreK8qaGFv+fVAc11SdXNFzt'
        b'KXA6stdzqe8qeVzGP0u+Xre3RnNo/6b1v719+hMXxSXZnT99bdhZunD2L96MP9rW+k38ga/Y0Z/cX+Dy8rE/rb/y5Z7md2h51zcf/fK/3+06+dirP42SPa+W8O5j/EaD'
        b'AzUF8Nwy2BEDO4qk+RiHucMhDnzyiU33MQqDZxvg0zH5UtiWtDqvsJhHCcElNjwBOrmkPNg2H7THyCT5MWYE5zYPXoFbOU16+Ox9jOHgq7PChQjWb+FpNyKstDeOTc2A'
        b'L3PA83B7LWliSywcRKvUwYF74QG4D2HsDBa4BI/ACxKXcXaURId2LPUjHb0LHiS9deJv3GtWra6pVaVFRJOQYxkipap1c8ZddCptjUpXqVNVN+lqdBgO2bgGNgK4v26l'
        b'Pt/Eorz8uiMOlbflfBQQ3lf7YYC0y7GTNebh0zV7jA7pzOlOOJR3x3NmH69PP+oZY/KMGaMjBjwvBp4LHNQPLRiRZJvobDu57tChfQtPC2xSBngD64cj00Y9002e6ebk'
        b'UTrRRCcOJg1xRuhZtrUYRj1jTZ6xKFv//AHe6fzTbrY1cQfqrTWN0eFnXftdB9aN0KlMnt/6hQ6HpVznDiluCE1h80f8FgyLF3weSAXK7gVRYu8j6V3p3TkjHqHDzqFf'
        b'4s2vw7tf4jrOZ+Zo3KGyUmfUVlaOCysrqzUqpdbYjGJ+5Eq5Imf1pKXS4Y1JFoI4j+FcGcj521bqwUYWiyV+QCHnV67e7Q1bhffYPJb4jtC9PeNXXLedRWOObnccPf76'
        b'OY/iiSyhb/QYUR3jx1DnhamcSWjNyj8SPMs7TJVj7hHxjnKWjiNn67joPy+e0vHRr4Oco3OUCxRUMkvOxTh3DUvnREI8HNIxKXzix9iZpWAnc+QOJOxMWCYuCjuSsIvc'
        b'Sedax0YsjXCcv4TM6qdy1IViMtXVHJsuci2Ytx53kcVwdIdx9RRpgEH/nDIb9lXLReifY4P+uZMQPSebS9D/lNjpOS3OFPTPZWjw5QYudWUVWqa5qzUv5zVRaudxOU+v'
        b'RCkx+YcuV598WwQCXt/qNG/58m01Eo/ON45DR4//4pyrfa0s8PX9Eq+3Vws+8H5nQPjez9pWNcWnOs2PChW+5RXR3cZqc1jmC55hqcIF28o9Xu9446XC+Btin/e2dSYF'
        b'Uo/vdb6QtkvCJ5gGnFwH98dYGZ8YPuUGzsAjLpxWcAOeue9PsNVaeN6cZUcOzsWhnGM5DovA2fs+KJ0Fj7bCExEFsL0Q8YQSPuUI9rI3BKy/74sx2dZG0ImpSUEeeJ6i'
        b'+C4u6WxfsBdsJUXzwaky0F6CWD0uxatZC4+zEBe4E+wiiX6x8CTohzdjpLmES3SEV9hg51KVhDf9duBZEBfZBeOOlZVqrdqA9pobAyYySwRBUqspgqTuGdhUbPzF2edm'
        b'D3mbYrJNoqhO7lPO3WvGxD5HCroKRsXhJnF435oRccJgtkmcgrBXUEhvQ0/DQMhAQncTyiscC5yJfgQfe3iby/RxPxCH3+NQYh+dhxUF8Me5epWmdpyLxZBxh3UqnR5J'
        b'LDpPnMHLOgQ+3tGr8Z5mdjJmUnWYp12JU5OR83e0kxGCZQX/gE38JQa3w/xw6llhPKeabW+H1Fh3CLM/ktnm3cGexBxxgiaxPrY7Be0DdjaH7I4psdbdUf/w7rB2wGZ3'
        b'GKMx7NwAN+KFsAOBz37EBsID8lwGxhaXLpE+7oW4pcdgP38G6ElXZ3wTyNbPQ2X2nmi9XH0U7RsR8EE754Kvr4/733x8TvUoQ17bF+z8suaDHc7OZ/aJtkSHlkYKz7xL'
        b'ryu8JBqSefLfNVBv/ZOvP39KwmVI+A5wotoM02XOFqgGJ+GB+8EoOfEJxDxdRuT7ADwgkzabSbTfFtAfwgW7xPB5AsLwBT/dAnDWCuIEwKPA0/fxmqs2weMFJaAbnJWy'
        b'KPY6VjY8CA9K2DbQjJfJAsqIWNSpDGqDqhFBs7sVmq1xBKBTzQC9AENet6F3Y8/GEY/oj/zChyMyh8pMEdkjfvOGxfPGvP2PtHa1HtnStaWvZsQ7ZlgUYwOmPF0YbpCr'
        b'VTaqHgZOHgFOK2zKsIO59WoLbH6zlfp6PofF8vmhsHmIH0qdFso4///D3nbhMwb5m5fBM6ALnp0ORK0A+lSYem74aQ4BUJe/zWcQ+zQA+rVaYwbQakeP0jjhmY9FfCPd'
        b'8+7tHha1vJF/JkEg4TAAurccXADP+T+Ed/0QC4mxRTyS0p+fAqFgEF5FUIpANAQ+x2DZdast4Ak7wHYGROHVNRLOw7iVQ6BxAhz1dsBRPwkcE8zgWPw94BiKEO4RQZeg'
        b'O/k9EW2LMAkk6uJxg7x1So1xCjw+jCzTsJNOYcnIBlkWIYCc+QMAUheJQdoukiSAyLEiSSxTUsnc/xFEOUWK5E0BRF6xEW9B7WL4bAFawjLYJpXKFufmK+AtuBO2lcgZ'
        b'uS0XiXAyFmWArzjxG1RGCSriswAemQK3HggDTQZd5xnqy2e6KX0TKnLn3YHL1T0Ici+8jmAX1Lz9OsX3E+0N3nVsW/DRGW8rHWuTd70o953vs8t3ltjX5wufeb7zlm/v'
        b'9onfmlLaKCj9aJm4nh/zkfOZUv6qVD7f6+mdeR85C2iPsfgix1+/LhZuu5G9LfjEtiQOJeoTflaJBncfK+MWwaFFQnAObgddD4tC+QJmI1wF54sm74IUsH0DaK8mmNoI'
        b't2VY9oEr7LNF1mgbgBNB97GKJA/sBG22eDqjFWHq4vtEVgbbW22ZkPUSsFPT+L1siJUZH+cbm7G4NO5i3idMkGyRFcwW+Xw5h/IJ6Qsb4I56S03e0o+wjPHYiN/cYfHc'
        b'nwfQnQsQyu5LPpvVn/WBt+yjIMlw9JzbYlP0wpGgnGGfHAS9gcH3+NQMT7yLRkXBJlFwX9gHokibveTA7CWsyntoE9n024Eyo3eLGJGNHYy2GimzGIEQ/INlGMHfo34Y'
        b'lmc2la2aZjLnwSFqGqJJs2J2VhnnP6iW2fn9mJ1TrK68EsvS4x59KzcSTP1O33/7gFMI5r0Qvi70Db4ii+HMD8p18ThzlF4a+03flfgdTwo48yWly7aJ1vlvH0t4Y56v'
        b'8utPEhZF7Uw8z3n81hpnZwTozsEX8p37m9efi2+upaieJwpoYSb9Z8RsYBYbHlbBI5NBGB6HlzY0gyeZ9CF4Eb6CwBM+DfpsWAm4fRlB4qWwD3Ht7bFwgJUHO6R8il/B'
        b'DgU7V5LEhqpgzICDw6DTzIQjFjwbtCGQ+BcETAwSNG3DUyPxVW/QIazvOoH1cZiAczkDzvfqOZT/zG6v/tC+mrMN/Q0jIYkm38RO/lho5NnM/szR0CRTaNKHoSldBQiy'
        b'fQJ6hT3CUR+JyUcyEDbiE9eZjYRuLGkjAApL/ZxP+YT3LR3xjh0WxU4lDtPCMiENNqCch518vJ0pM2nAEnEdAmX3HwLFmKZJOOO8SsLE82vVKk2NXof1Zgi6Pv0WwbfE'
        b'DcsdmHtCkySorGROKpDfubJyrVGpMae4VVbWqnV6g0atVWmbKisZMudYjTBDXZOuZdzRLB8wlesKKYssQJiuNOvuxOMa98SLoDSoqyuVBoNOXWU0qPSVld+Homz0BT4W'
        b'B8vR+ky8jLupux7ebRjztOWOefsix8uvbdGYp3dbzgMu3yXiKxHHJfYrAcdF8kDAd4l6IOK5SL+gkEMWyUj435PgANwmzC+C++PyG9JYlKMzezW47jGFrOG/LzEunMOy'
        b'o0Xg6Hhyrpwn58vYOr4v9TgVQskdlrhRU/7kjpazJcuvzlHupHOqE6DNLxznL9Qi9qTl080o4RvxAlWV2tCkU2njCnSqGsb7qYgs5KcYIXzjvlSlazXW6ZuVRn11vVKj'
        b'opNQEu7uN86FKkOrQUXn6NR6wzm2rghFfvom2gJf9SBpvqBJa2jKKkbrTEdl1+hUej1aVK2hpZlWaA0qnVZV36jSSrJsAvo6VR1yDUptjd1yWqUB3tRpZHQpAoomVHZp'
        b'k077r+SzV1mDCoEcna2tU1apJFmT0rIKjLrWKlWrSl1drzVq67IWKqSFuFPoVyE3SPNqinWyrGwtmjBVVhli9TRx2Q3KGhm9SKesQVWpNHrMAGpIu1r9uiYdqrnV0obO'
        b'kCU36JSwV5VV2qQ31Cqr64lHo1IbWpX1mqwSlIM0h2Zej35bjTbFLYGq9bh3WO1ImzuComT0CqMeNayx6TydMG1KYlaBSqttldEFTTpUd3MTqk3bqiTtqMztqehF8KbG'
        b'oK6j1zVpp8RVqfVZZSqNqhalzVMhSakB1xtljpJY0uhFKgQ78Jlagx6PEk/p1Nz0okJJ1kJpkVKtsU1lYiRZeQycGGzTLHGSrBzlBtsEFJRkyRHaQJ1U2SZY4iRZ85Ta'
        b'BsuUoznCwcmzhmMaMAxLi42NqAIUVQifwXreBjxrzPSjyLx52cU4TaXS1SI0iLzyZXk5ZdL5TWhtzJNP9oJaW49gDddjnvZcpbHZIMXtICxXJTO3afZPmnd78XjuJw0i'
        b'ccogEqcOItHeIBKZQSRODCLRdhCJdgaRON0gEm06mzjNIBKnH0TSlEEkTR1Ekr1BJDGDSJoYRJLtIJLsDCJpukEk2XQ2aZpBJE0/iOQpg0ieOohke4NIZgaRPDGIZNtB'
        b'JNsZRPJ0g0i26WzyNINInn4QKVMGkTJ1ECn2BpHCDCJlYhAptoNIsTOIlOkGkWLT2ZRpBpEyaRATGxHtJ51aVatk8OMinRH21jbpGhFiLjBiVKclY0DYWIVkakugWYcQ'
        b'MsJ+Wn2zTlVd34zwtRbFI1xs0KkMOAdKr1IpdVVoolBwgRqzKCopQ+6yjXpMUFoRQ5S1DD5Tr0PzpteTBjDWY2isRt2oNtBRZtIryVqBphvnq0KJ2jqcLwc+o9Go6xCN'
        b'MtBqLV2mRHTRpoCcrAFOKSXnUbaVTZBx6QrUC4QwonDxSQnm8igpfGqBxOkLJNotkETP0xkNKHlqOZKePH2FyXYrTJm+QAopUKRk6DKZc8SXIP6ExBlUGwxWD8JEVm+S'
        b'bVa9NRuzEPNUiBzX2USEZ61Qa9Fq4PUn7eCkVhSFSS/C0pOCiZODCP0o9QZE7XTqWgOGmlplPeo/yqStUaLOaKsQ2FpX3KCDz9QhIMrT1qjXyegchn7YhhInhZImhZIn'
        b'hVImhVInhdImhdInhTImtx4/OTi5NwmTu5MwuT8JkzuUkGKHTaGjlphnVW9mNCQTjJG9RDOvZC/Jwj5Nl2ZFZXbSS+y3hvkue/GTWLHpx/CI9Om4sx+SOXH6lifxaf9K'
        b'NoQq7WWbRAJSp5CA1KkkINUeCUhlSEDqBDZOtSUBqXZIQOp0JCDVBtWnTkMCUqenY2lTBpE2dRBp9gaRxgwibWIQabaDSLMziLTpBpFm09m0aQaRNv0g0qcMIn3qINLt'
        b'DSKdGUT6xCDSbQeRbmcQ6dMNIt2ms+nTDCJ9+kFkTBlExtRBZNgbRAYziIyJQWTYDiLDziAyphtEhk1nM6YZRMb0g0AIcoqsEG9HWIi3Ky3Em8WFeBs2JX6SwBBvT2KI'
        b'n1ZkiLeVDeKnExriJ43H3MUcnaqxRt+CsEwjwtv6Js06xElkyReWZksJtTLodapaRAS1mObZjU60H51kPzrZfnSK/ehU+9Fp9qPT7UdnTDOceIzQG7TwZnOtQaWnS0pL'
        b'5GYGDhNzfbMKycMMMzlBzG1iLeTbJmqRqgrexJT+Ibahjok3cw2WUOKkUFJWqVm5YlN4itolYWpU4tQoJOZosFCsNGC+lJYbUXXKRhUio0qDUY/ZWmY0dKNSa0Tkha5T'
        b'MWCKyKE9NYDEpogaE3d1DSn2vZnt1G+HKNmve2pGomKamB0aMd+0meUlU1mL082TzPgTbfxYJpzQVI2zsojytPicQFeMtWMl2CnFzmLKfNKmW4IdrAYc5+mbNWoDo3os'
        b'w4oxFqM7xLo1s95wqcXBOjV9lkVvKMF6Q9+23Ht8yituzDPqcweuj2tb7hcCysv/Hjd+xnzWgyoW5Sbeo+qc377myzpWkpdfe86E4lA6M0KPrev2xIJzW0q5lGMqewvc'
        b'BXr+FxSH9RLhuCC7urrJqDUgGeXTm3hmXOch6GIEHGWzSvOpJ6M2xHP7jd8CBG+NiInBynGaEbHQblEjHIeyYKPXcS5mtnQVyPvVTRShaGR4p6Z6rYqWN2k0cbkI+Wml'
        b'Ba1YlTMRnECnWcsKVtBMMayyw4har9YbmQicZhtmtvcirGFkRAmmoXkKqby6XgNvIjDTIPbHNpg1T6VR1dXggTBes35nwp9oFsWyLDNBRAvMe6rMWMQiH9IM/2WWMif0'
        b'YWb5kkgFWLJEmdE+NhAJxFwDaU6jRhmIT62tbaKldLbOYOmKOSZPi0s+FImzJdrLljglW5K9bElTsiXby5Y8JVuKvWwpU7Kl2suWOiVbmr1saVOypdvLhtiZEnlZAooo'
        b'YBYGs9UqEpk4JRIF6CIVQs0WpS9tlNETSl8UycCyRQsro7FoYBHwGe3uxDLShTGFWTlGbQO5laHS1SFc2IrxF46fp6CTMxiKXmvJgrXP9uLNcMMk2akwawWRPPDAdY1K'
        b'nGgFEXspVlCZrljio4rZT2RA6BHF7CcyIPWIYvYTGRB7RDH7iQzIPaKY/UQGBB9RzH4iA5KPKGY/ERfLeFQx+4lkueMfud72U0nBRwPK9JCS8EhQmSaVFHwksEyTSgo+'
        b'ElymSSUFHwkw06SSgo8EmWlSScFHAs00qaTgI8FmmlRS8JGAM00q2fGPhByUKjfAm9UNiHStR8TXQHjg9Sq1XpWVg0j8BPZD6FCp1SixGlO/RlmvQ7XWqVAOrQrzXxN6'
        b'TTPlxAgv21iLNXBWJGehpSgJY94JgkxHZWtbGd4bHx0iZFykNiDSqKpBHIjS8FDyQ3h4auEJTP5wmk4Dr+rNbMKklFxykFRrQFyJVYIjlERK+B274oZ5pGZqjkg/ojSY'
        b'W68lfHojJvAGlRpNi8Gqks5DTLVBXatuUNpi/xVE4rSqqm3ZDEZOtTmytGWTclSMEKNSV+GkQrRq+AxOz3A20zNqtmpo1G/UslJjbGxQ1Vt05oQIEi4OW2szTLWuyj6P'
        b'rLI4mHXUp1t45FAbHjltzJOezCP7zJj1IHGCQ07zn2CQaeSAQ3HgrL6wGO6Pgx3gNDhCrpIUOFCeVVzn9fDCJEbZxcIo/xr1ao54KqOMWGN+CIVcIf4v5yDXA/9nmOcM'
        b'hyAqiJKHKHgKF4WHxQp/DctiZqPjkXueTn6UXCAXZrB1DiTsjMIuJOxIwq4o7EbCTiQsQuEZJCwgYXcU9iBhIQmLUdiThJ1J2AuFvUnYBfckmS33IbcBXCf13uN7/jvJ'
        b'fTMEZDyhCrZ5RFy530Mjcps8I+i/AP1nJbPNtThYfZPr9s9wQjWHKRjbQHwJUITqd5AHPFS/SB6O8vAUjuSqoDvJE2i+FTEDxc9Aowsio3O39sRDPjODZb5s6KpwS+bJ'
        b'aZzDWqeHPFgnrnNwqpNEjDsuwNdz5suXfvoblNTqLbCEaQbDMTdkBed4Oiw76bDZzqfYYEanxj5sj0ukE4nzpxiOP8W2PZ9i+8+J7DqdJbtOj50GnAXfAPwU37771BmX'
        b'dhgXKGvWIUSpq1TXjDtVI3SlNWCvq5KRpyo1iN801I87VhvRTtZWt4w7YvN8tVLDWL2MC4mJTGUjwiL1xdWONjCNmyK2W1spi0Wm7VVdcuOPhVaYq3BA88Xc9+MnC8yG'
        b'ZY5lAhvDMrRmCkcbwzKnSSZkjtlOxLBsSqytSbvxNJojQR7TeXWrSk+uMFtnXU1sO6rx7eVMJPcoG+mJick0X05GuA1rvMy3n80zpNQaBNj8KmoeQkEGCwKUyOhsnB8h'
        b'q2qaGMbSxmYaoew0ukZdpzboZZZmrHNuvxUmmWnBek7zPW2kPNzG5MXMpAvJL25iUVyhJdXcsJ5pCxMoTBoQYZHRZfWIWCC4VNF6Y5VGVVOH+me3FGPUwkixqCStREVQ'
        b'mOkPrWlChEono/MMdKMRyTJVKlJKae58lcqwXoXPmemoGlWt0qgxSMhd8fSJuTIDYSY93+yjq7FiMsp6nGmj0JRYSlkANpM2r77eOrn46nmTjo5ijGEa4E1dK5K0LQXN'
        b'9l2ZRIzCLAcqxqyReY9GqepkdEpCfCydlhBvLWazIzLpHBygSQAXr1VrEZShPtAtKiVqOFqrWo/PStelypJlCdESmeB7DIqdmXtJ76yagWCcSi913qwZYG+hjHNRJLwM'
        b'toHnYXuRAL4ILpTCtjzYURAH95RiQ+PcQglsjy2Wgr3wQOHiXPB8bnFRUV4Ri4JdoM+5CV4Ht0jNTYudKR+KihrO2RzbGZlAGedgYnYe7nVHFU+tFe6HewphRwzYY60W'
        b'HJaYa97Z4kzNgRdIvXeCyB3l+NWFqsIrC/wpI36eAO4NArux7SN8ATwZU8BcZc2VSaPzURvgBS6VWs7XrwNHyVVcUk0ZRS5Fi+45bnK+M28+ZZyFIpPh82p7vYNtqMb2'
        b'WNzDfZKlm6JtRg2u64TgRTXcpo7/eThX/yyq5S+yocu/wTdTfMFJSHGC980NCj3+kzOviwDr9X1nShN8At+pT9m1LbgLm1N7nsnsdoo49rYP4CY/6QsDIpz13Ze64fYa'
        b'V70oksOP39Xzs5OcUd7VHbPbhO1rulddWPo7n3WXgu+8seZnAyzPEmXV6tLVjrVuv36jISvr6J83bdD8/vav5cVhP8+szf5k7e3/qmZ9cXdOGvXTtf33hpQ3Dfx3vagL'
        b'9TP/rlsocSZG17ANDKaB9jjrvbBqMMih3MI5tSvARWJVHeYGt2F71FtFtgvPovzgDm4reBmeuD8T5fIB++H5cLhPiOZeUmSx3vYET3Id4Sn47H3MySDPEfEsIa7MdrFZ'
        b'lFcwV5gCuol5ticcSo6RwlPzo3KlbIoPjrKlYAjuJFfYVoDBWFTavKy+8Hm8su7gBQ5sBxdbiAV3WnhkjAz2gT0SuDeWQuUvsJOMQeSeBNyeAw+CdnyH1rKW8AC4IOFT'
        b'7us44BU4BAbu48tICJAugHOoHTPPFeMNj+COmgECX7jYxZfBI3D/fWxjDQ/DAXABD6o9NlqGM0b5ww54IAZnpfU8F3gLHCHj94b9dTgf0Xai9hPg81LUODjCgbvgIOgl'
        b'0w2Oq8FllItbZWnezO75gSEuaF/qJhH8iMujmIY+fHEUm5iOz7AQrsn35UwUY927zoEKxnfkXMZCpZ3c90X0HQ+vLn135qEnRjwiB4JHPGI+8gsbDs8d8csbFueNhcSg'
        b'vG5MnoxDW0Y8IgZmkHsgKM+iEb/cYXHuWLDkbFB/0EhwAsrqirJ2GvDtJJzVWl3aiF/6sDh9LCT6rGygajQ4zRScNhKcMaWAte6cEb9Fw+JFdyNTcCfDxsLi8G/wWHAo'
        b'LjMWGt7J/WDSfRMXxqS4FTsbsbMJO1izrduCHWKI+wT1KKtjzGqvNv/ZGB8Tw939mDHCmTBS+Q5N5IMSBxarmvU1hd0feiO3n59AXRLO4kwyqWdZMHoAwegKagk19S+M'
        b'ctopYRVLWOPCygk2BAkuePREcKHN1ydnaZSNVTXKOTYAYYmawbIAENVdNhoofS+Qsfv9xkzDzBVb+I0oRAtrpE1aTYvkHGucU9NU/aP6Xcf0W1Bp5WumdlvXhZ2DyBGj'
        b'SHK5DPext/JoJdPDmUwPmSrsdPBH9ayW6Zlb5WRu6FHd8548hQnvBSYwHZQ8koP6t7tqnkSnSgvD86hO+k2aw4qjFUwXfecp9Sorx/Rvd6ne0iULN/WoLgWiSF0vDpGu'
        b'hE7Ld/1nOuVYaebUHtUnGq+ldZpWHV1l7tu0vN1/BtycK23YwUf1LxQv4wSsyd4LlJlh7XtYyGn6ab06g3Uec9jmuzsTd4b/szd3/oU7mZxidVxPEEuPaXXB4kPMJeAT'
        b'p/peZ+5ZFvoGJ5fxPLSeL8+9AG7fYVPvvsktfw3VS/gU+MwCcvuLIcJ5qYgMT9Dgg8vv42kFPSvhUzb0HxNgeM3RSoPBc3DXtLd3HSoxPqisHBfZUFYSQwgr5hjwLbB8'
        b'J8rHvzu5d07PnBHv6HPyQfFoQrYpIXtEOs/kPW9YNG/KNV17lIi5pYupDwMEF7EziJwI1sTNl6/znH7YzReCBA7yQ6hTQilHIhh3MKMl5t4KX2/QqVSGccfmJr0BS03j'
        b'3Gq1oWXcgcnTMs5fpySiv7AayWZNjYxKgGNQ1o3zmtCm1VULbZbX1bK8mGTO4dp/hwtBnIv5Cqajwg2J+gIMgQoREvydFA7JrmZIFJa52kCiM4JEoQ0kOk+COWG2M4HE'
        b'KbG2kGicjYBOkF1To0eyJRawalRVGN2gf9Vmq01aRS6akLfKkGxLBFUlXW+sU9nI32im9Gok79LMHSIsWutVBhldgjabAOOxRnwip25sbtJhNYAlW7VSi2RZnBXJvTpV'
        b'tUHTQle1YMQnUK5TqjVKXCURFbHNrh5J8TWoTwgHoS1trsIsHuM6BKioUa/W1hHMaS1GR5NFiUYjyDH3rh5rjaa2LYgyKHV1qEyNBcHh/DTW7uqx6Klfa8Sjr9IpqxtU'
        b'Br0kU/CQ2iCTzp5E3+iV5Lx6lSUbrimTJvdYVn7vbRZrKQYcM2k5+aVXmm0prekWMM2ksS4ZTQ2R9Ffa2k5a82JAzqTnI5deWaIzTMQzoI2SGA+pI5bOk5dIkxJSU+mV'
        b'WD9szc3AP5L2s8ukeQvoleZD1lUxK23v1kxUPrFNsD6CCdC4oK0FtzU72khosPUIVBA46qt16maDmezgdcV31QhsZWv0TWi9VTVENYKWB6dilK8hr+GRyZbRCxj9CAHJ'
        b'ELlB2diI76tqQ6yaEgIcaOFQA81m0KpRk/f3lGga1qsRKVFtQDNuBjgZaa24yaBiwIgAt8pQ31SDdkadsREtJGpL2YAAEAGVCo2uWkU3IapLyjFdxEBFFDl6pttqvU2T'
        b'MjoHbTrLhiKlbMEQq3kQqODXAqs1aADMQ4F6FZNztfltwKZq0hPm+GdWvcHQrM+Mi1u/fj3z1pGsRhVXo9WoNjQ1xjGsY5yyuTlOjRZjg6ze0KgJjbNUEZcQH5+UmJgQ'
        b'tyAhPT4hOTk+OT0pOSE+JS0pY87qyu9VwrgXExX/4+As3K0vRHJktyRfKiuOzcOy8Tkkv4bJefV0ihHbsTSo4MtJ6DeBqqtP8F9BlBh/EPLEX3JE5FWZJK6BMuJnIdZv'
        b'gdsLLLRrMWzDL1flS5fgu95LovDt6GWwDf8klCKKBg6Ci07w8EaNkdw+vfoYIm6XkXiOxVcHigd72At9neFx0G9kZF3BGnhZhgThPHyjHLzSiCrHD2OxqZngWS58GTwL'
        b'u434IaJIuANchZcL4L4iBexsLpw0rlLYVozK7StQNCOnpDAfHuZScC/YDl9ZKoTPrIVdRvyiTB3cGywsgy/IJPngJugVUE75bNgLLlQxNw47leBJeDkP7gM7mwpYFAcc'
        b'YYGt/uXkrb/EOPCkELbFyeAe1Kbz2lhwLh8R8TYWRS/iccEAfIW8jQaHDPAZeDkumkWxc8FOcJqVCm5lk6ndtJK/iYcVWPRqzULWCorMjyM4UKJ3QRL/S6hZ1KZjOdwF'
        b'+tmL4CtbjFh4ryh0wMkuLjLYNQu+CF8qhJdi4EEO5d3CARfgrhoj5kGKwZ44oQzVgGYuLzYPXAc9sINDecLrXLd02K7uWdNL6W+jjMsfxDV2Frhvj3fe/frakafZv1s8'
        b'i/2bnLR9Manv/iG4/vHrVZv+nN7x8Wjv1qGBE+ov/5l3KHn2z9Naroc3bfp48dCKjJ93term7Xgh/fjx913fjnxLOqiIeXrfG6dOOv8p44O7s2618QsMpvOPffHcnifu'
        b'rP+VZ2v9X2bsqDojfir+cN9TeTuc5fy3u0NK3y378xFXWLtkf/mMostP6d/33L985Ydfh9160LRhc9ELfryIPTAv0+Ob1rXLn7jws+9eH/3bmtaDLZuo2KeD1kBvCZ9c'
        b'249r5dtqmIh6KTGjNgg+eR/L2XCHN9htBdgJTcvhRViDEpPEgweE8DrRoIBd8BK4ZqNjgk+DfRY9UzF8jrB4YfNTbbUsDHsHngHHMIvX5cu8dNSbB27EFEvz8ooKYmFH'
        b'eoGERXnBm9zEjY1ECxXhpS5YHh8blYt6gpYZnGe3gL2gVyL6dx5bs6uZwc6kV72s168FypqaSoa9GPewMpMTkYSf/IOZnywUUH50H6/PcHZz/+YR35RO/piHb3ecySPa'
        b'5JE4JkvozOl+zCSOYVQzaYc2jXiE9RlGIzNNkZlDi02Rc0Y85hBNyvzbdabwohG/4mFx8ViIpJPfub7LbUySjDxbTKKIsTnzOvnD3pkmUdZYWDSKbDFhNUsU8q3rch2T'
        b'JFjy0WHIZ+xy+djDdyxKNqAbZA3gJ9wyTOLwMWnSYPbgvIEVKDzHJI4e8/Id9ZJ0l3dyxkTiI65drqMiiUkkGQgd0I2IEkdFGSZRxlDEB6JsG5Z4BsMSv0hZTBkvY+cK'
        b'dl7CzlXsXMPOEHauY+flaZhom8XA87564o+eeNlBB7HzOm4bs9b4oYTv8IMjJU5Yo/OA6HW++MHaHWwiOMBPp4aE2RyOxGncuQabe5rZpXEXhsm0BPnKRvLLJS9MOJlP'
        b'3qtV40LM4iDGDtvlMYO2jrdaYEN/RBb604l5bQd7vPZh8lgm4qvxcRqLvGrqpJiB+G786il54zZZZOa2BZO4bSHitm0O2mw5b8RXC7KFhNueEjuJ227iTea2lVZTTJp5'
        b'UA/xqAvxVRgmRCPGAO0GxI4i5kVp++4vZnBi6Tpdk7EZpSK+VymobmqsUmuVFlYpGnFR0YRnYFgGrEuw2vriBq3CsQALx/+PvX8Ue28LtJn4jI+JsWqzHmLzJ0E1k5+J'
        b'shQgvNrK77FitVbH7AqmHvNGMMcx7Km2Ces8dIQh1TJs5vomzB+qG5UaM8O68hF2uYhtt2+Za+0B3o9M+1VNTQ24fRwjo4vMq6MkYbqpag2aaCQ8MoeVWiw+pKfGJ5gV'
        b'RXjikSyDi6+csMm1NmLd7pm0Qm9UajQEUtDCrGtSV1uhcaWNCe8kCciMHiZPE7k2uNLWrHeKDIOzPyTHTDIW/b8glsxTrVfVmU15/p9o8iNEk6TU+MT09PikpOSklKTU'
        b'1JQEIprgVifLJ/wp8gnNHBK/yefmnGQTMcO5rKWOMmI5ZGHO8oK8Irg3No+wbuBoNhY3pkgZSMZ4ArzilAxehDcJVy8Vp8DL6eGTZAxn+BJ8wYhJw+LS+gJZfhHWzVlF'
        b'GJs6+RprraAdtjshwekGOEkkjqULQae+pKjE/NQVrnwZ7ETZD8A2JGgIEFuOKkTh6/LsNeXgODgKTjvhA+mnhcWZsJ88Zy4PASf1+bAjQJ5XVFKAX8iK51I+8zhwX6M/'
        b'kdTg7jzwrD66CO6Pwjwq6GmW5YHno1jUzDoebx4YYDL1wmfhCSG8BvYvcYQd0mIkfaypZ1PuSRzQD095kbeXZY6RSNDaZz2rRoIAvLwMvLQEP72cANp5G8A2cJbIC82w'
        b'B3TgbqFO5cVKYMcqeIRHieFpDryxGBwiS9S/gpP4Vxb2rXY+UJ5GGcW4Iy+A7WCPkI9PuxPBC2VIYttN1g6e8FkixJOE5rILXgsS5SIZrAMegi8VE7nuPAoVwv25WCwp'
        b'93VcBK4vJg9PKwxoGTGrlUeBW7l54FAeeaca7ISvwB5GOAX74Z6EgPnMg9S3nGXkmeo4aj2arDMZmr9+9913rzvwimeyGGhK0tUyx/ErjfzoSA4Rt2JDDfmUEXNYzoYg'
        b'PD0dZkEWHgO9ubFL8aP0cfkKBBC5cJ88SoLAItf6/rwEXCUzyNe6rMoCh8kz8/AW6tRuOTyclA+3B3AoFrxAwQugA24jh/7yDeCy0LxMSyYgxnFifsjseIIDeILAC/Ag'
        b'lwJPKpweB11lxlg8/Esbwe4JsXBxFDwsd8QioEX+i4LXOdRjnnzXPDWRTtG6vBipz5eWFMVhKCrGa98hZ3MoCezmgSsLYR/T7+3wOXgshnlTR7JlMZ8SglfZ8PKiRvKg'
        b'elpzie6kQ5sL1az0+Pny3y/uoYyzcW/ac/GDlWapn7GtQCAG98SVFC2OMle21GrBALZrWAgewFln2KmQG7Hw4wZeBb0x1XCfLC8WScZ8cIAd5w0PE5ACfY9lFhChiK1j'
        b'gRs+6XCHg4RDisE+0DkzJg102RTzhPuNmOUG+0Gbq7Uc7ATX0qNVBB0sN8KD1iE6WYboCF5QC5x/ytI/ibjtXSfLnl1SVALmik78+YFX1LPiGY+5z8u9R7d2CXMuBhW9'
        b'fCOyOMyv+OvRu69+/pOMrD8v/dmHh8IGf/6g9pPZH9/P+Cf307i5rr8doP5+ee1zl7l3fvKc86uf7/6gfHPV2er1gqtv/vLPM1b3Up/9g7++5qbrlpd/2bPP03H9s5G+'
        b'HX/o9Tu5rzg55P17eaFvrJx7LfhjoEiZPXg21H/Gz+cvKq+NaD929JeL3go/mpQ5s1wHb/1Ouuj4t8vkLb/ef3pp4Yr+PzQmHe+4+YfQzOE/nI9z15/N6P9UumFR9Hz4'
        b'dOEze2evuXhN8fJez1f273/f0NZ19aNZqsA7+z0bbvzSxTlyB6+tfPerLfpT3zn97b+P/WPTP3f+1fdXN3M1dc/u2LDmN74NQ5feyZFkHH8uYFNS1R+DHrtUGzr0akab'
        b'+tpBXdBH7ylkxe82Pp24KfgXrkuvZ5587/TO2Ws/frv56j9BReHmtJSvfn3qpY0l5d+8ubnv0LDjnzfnPYipOmCs2inKeu3awV/uGLqlLyhpeaJl5KU3FQl/Gqi/+e6v'
        b'qH/cczl3o/SJtU4SF2IxMg/0ofWzyPO7wWGrTF8r9iYWEavBLXc78vyeEPCUWZ7Pg33keXS/+mxbg5HqFRaTEbT1iOpACU54FDD2HmgXHyamPG5LOZqZaeTBs+TYvJho'
        b'uAc8LWPMPZweZ4Nn4eFlxBSEs1Adk5YkwwQjFoPjfrYU7na8Tx7WvxTrXVAYzafYq1jwfH0aeGENeah1LhwEfeB8YVFsVASb4hawwItzmJb0FHwa0ZWT5VbTDv4mdmRT'
        b'3X2ynw/M09gagJTBvkkWIHO2EAMU0A12w2fxwVKD1J5tBzzLIloOTjJ4Ro/3pzSKHD2h2Z0BOznwaVTBIOiZRZ5bBk/Co4qC2IVwq62Swgsclnj+p3UU0ysv8JzR5jfj'
        b'7GgwXLGyYkKKG/eepMWYSCCajGw2o8nYIqT8wvoWDiTjZ5pHfDM6+YzSYtaId9SIh2RgwWjsY6bYx24Hm2Lnj3jMJ1qL7NuFpvDSEb/Fw+LFYyEyRmvBFJs94i0Z8Yge'
        b'KBuVzjVJ595OMEkXjHgsIMXm3V5lCl8y4icfFsvHZuVhzUa6SZQxFoXVGJtNonAbxUdkDNasoNAmkyjsjkdgd03f/FGPKJNH1B3/qAHxiL+sc8HH3v6M/cr10KGaGxJT'
        b'uPnJeFTYXBArZbIPZY6lZXbmDPsnvSdOvmv2msTJdwLpPq9jK0cD40yBcYOckcDkTsGYh1d39IhH2DmPgRWj0tkm6eyh6hHpvNuJJmnOiGTRW8EjkgLSZuFbrabwx0f8'
        b'VgyLV3yUnnV90e2ct5a+VjIyq2wkXYFHlmwSpWBtTEoWbi/BJE68Gxx+1rfft9N1zMP7SGZXZh93lE4w0QkjHglj4UmDSlN4WmfxmLffqLdsOEg2yL3mdMlpaM6wV34n'
        b'B3crbNQv2uSHOhc9FhQyGiQzBckG9KagpM5Fd7z9utP6Mkz+0hFv2WD4iHfaR0GRw1GFI0FFwz5Fd739u+v66lB2lDoWE9ft0Ofwnk/UmG9gn8MAr991xFc2JpGiWF6P'
        b'61/vRsUOlt2uMgXldS4ai03qXDAqDjOJw/rkJrFkTOTd7WQShZj1RREfiBJsVEQejIroDey8iZ2fYOct7PwUO29TFhXRv6gdehj4cVMP64qs6qJx7PwcOSus6iL8nuZa'
        b'AYulJuoiNes+cX+ouugcP4O6Lszmcqotl2Lxn/U7KNiOyVa1c5hSOCicFFzyJRS2gnlf30XBsn4PhVdmYw+t5QdRCpsnlhX8SQobXjafqHGmxE7/8OZUmcKVkSn+sYV8'
        b'f4aK53PrUhr0VBmJFZaQb83Q8fzRpGf4BoowFuDVMPiUHnQ4rgUHczgUx5WVDrsR80ZOJK6AV6PloKMMdiiKFsOXSuFLCpfUeNiTF09Rgd4csG0NfJF8SwiegOcRx30e'
        b'HpDDjrKUeLg3GTH3jmtZCFnvrSe8CA1Ow5dRZVkSUh2L4kWzwFG4exPz1ZULLesQb3yYfAdlFjXLm01YG7gvci48jTj+l2YhDBZB+YBr8DrDv11ENOPZAhkSbrbHJyem'
        b'sCn+FhY4ScPtJFmlBhdjfNzxt0NsvhwCe0Gvejz4Nyx9IoKcykRjRxmSaeKdje+l/sl7lwu3fusA30E2IjsfEfxaj7Bq76GZtzvk37p8573+isdzv7iUv/j9B5/9/vfp'
        b'bzd87iJ7STA2athILYu9fXjA/Rv9oZzvfl0S+F3L/D+c+6A8OApUs0YH5t9PeEDXzZDVZbfdXHc45fjmk10eiX/wzPnZTcXjrDdXLjRJDkTc/NNPPnG48wW9co/mFvXH'
        b'1W9nFB79y/G/bz7fPPjW/ykse/6zN5anJFf89OyLHxZ8ec1v4ar86Dmti//eUsF6f/iP791/RhZxs73rH5+NbUr7RcuNb0ePaV9KcF9sFK/4y0eKdbIP/Irnr/D3+LXn'
        b'ztcjv97fMORxdMuszwb5GX7yjYKDcfX3H5z/JGDZut9l3Fyc9tq+9MzQRbt//8ov2eI/O6kOOrz66vmvs++dqDa9yjnQufmf1NgbC46IsyXu9zGfGhDvR74o5IAglA1O'
        b'sRR58BLR7MNtVUhkxCR+9XIziQf74CGGpt5cm7pyFf7Wig2NR6LNKwz5vroQdNiSeWu25SJM5beAPYSpCQHP1paWTDnxqIVPguMkQ/nyjWAr3FlQHIvElgNx4Dku5Qpu'
        b'cSqRWNDNPCb/FOgFV2A7Pj2DXeU8ihvEAqcyZpOjCxpcBYdj4ECBTfX4Iw3wVTlJN+Yh9v/J6EkfncFfnNmMJoBYwPTAZxQFtra8G+ErLMoLPM/1h31rCI/nWQKOFTxk'
        b'pOu+hqOVgQs1WYyNzAWn1fZ4PHAj0szjiaqZ5m7CNtAPDtQR62yLDTWfcgviVIDnowmX5+C5CuwGHQU29tqYyVsCe5llORIAdhXEgmNetqwOvFVMCld5wR2obvJtHLBn'
        b'mfnzOOBpMMisd+fjsQWwvbLa9un0yKWkYj8wsBIJJeCpDWiwJfjNZ9DJboKvhknc/weZJncL0zT1Yy7jDpXMV3ZsrYeYGMIj9TI80r3lLpT3zCOaLs0hbScHMyN1fcqe'
        b'NQPRox4pJo+UMX+6N7Mns3PBWEBwb0FPQefCMb+grvl3/YN603vScfTM3ryePBLdOX/Mw6c7edQ/1uQfO+IRO+Y/sy8YZ7rHpv3cx8R+9zjo967Y50hRV9E9HvLf41Oe'
        b'Ad3ZXfmj4kiTOPKeA45zNMcdKekqueeEYwTWXBEmccQ9IYr73Jny9Onm9Dr3OA+Hp474pI2I0++54MyulKfvPTfsE2HfDOxzxz4P7BNjnyf2eSEfacIbh3xwqLir+J4v'
        b'rtwPVy7oq8EM4mxT7Ozh8Dkmnzkj4sfu+ePMASizuceBOByEso+KM3rm9/HIV382jNDpIwEZ92biRJokpqFEzlnnfueB5SN06khA2r1gnBiCEu+FYl8Y7gCel3AcikDx'
        b'R/K6s+9F4lCUJSTBoWhLKAaHYkn1ku4FvUU9RfekOEqGxxiHffHYl4B9idiXhH3J2JeCfanYl4Z96diXgX2Z2JeFfbOwbzb2zUG+zx9Dvk7+vXksyte/k3dX5HnEucu5'
        b'Z9VA6khg4vuiJHNEt7x3ec/yvroBZf+a0Yg0U0TaSGD6+6KM3wSFd+aMiX2PFHYV9nv0LT3t/6FY+jmHmhlx1zvwyMaujX0piLce9Y43eccP+gxljHgvHBYttOHAXBkO'
        b'7DoBbObMRj/O0xuUOsM4BwH1D2O3XC3s1kOc1j3sfI6c51nmh8v/iR8ud2GxYjGfFftDDd96+XHURWEm53/XCPKbwwLmMqrBcsHMfCajMauSdSqDUaclaY20Eh+Z2Wii'
        b'yXEV3aBq0aN8zTqVHps/Mypss45dbz33Muuz8bHTw0dgGkZxj6uvajGQL2ja8naOdng7I377fUOoGkmzT4MDYA+4BA+CF5chInsJnF8M2niIP9q6ER7ibExsIjpCkVsK'
        b'PIRYWZnvGgpRVdBDVKiV8TUMw9e+TAqfLpDJEMPXxqHEYA8HnIPPthBm8WI1m/IpJ3b4sbeqAxhm0TneE15NMxd2oLjgWRY4UrRknFVJLD7yQY8c9DXF2OionMCrxLjD'
        b'ARyETyPuD1GrS5P4v35fUjQkF3YxKiywDWxn61jpYBs8y9iiHEds4VnYy5Iz5diggxUAtyUyRibPgTPgRoQUHkLjQOxrNmtjFuxVf7K5maPHB9jHu8KwDevq250/EYGg'
        b'17c6be9OeKOwHz82z+LMl3hw5m8rdVwpijnz9uo3V58pzZEP+La889o7/e+8rKG9hlPXFX41Y96ZwlKvy5md91OqVt+tLaWud+youRae/YtP/N52f4etKw+qjo9J+MsV'
        b'5W+rHWuFKpdaB4nLr988dRI+NaPfa+Cgx9l8Wc1bXx9+7aM3Natfvax8rqzKUZWsTKaOfgLq33T86gnB69/1O0c7H/+U+u8r/lF9fRI+wxBdg8fQZJltLRDLsjt2kjnt'
        b'IGwnWpUasG+9MRjR/okX6+uKiB4GHEufESMrYlOPe7HBAKsAnNnCfDav1wM/gh+HuAGwT12QJ2VTQhUb9gFE4xn24wZ4CkHUZBvdgiR8nsDoUnIQt0O4/m7QDW8+xAwh'
        b'lq6D0wQuaSWO/zLVdrRSbSutVuor8Z6zodXmGEKr36cYWr3EjWBfRDbDJWeL+4tHw9JNYekfhmV2FSLiOzO4d13PuuGI1CHOkHxkZnZn7tjM2IENpplpyBcRfVbTrxlM'
        b'GomY27nwUMnnDlR41j1nVM9oWLIpLHk0LNMUlvlh2CxSk19gt7InApF5H79efg9/eGbcoMdg9Yc+mWM+M/scTD5Roz4JJp+EwagPfLJwFJKuR33iTD5xg/wPfdLuOXBp'
        b'r85cRLYjY85qTqFGTRHzhiKRQ1p2o8JnI4rsE9jp/KMMk7G1u46FnN/aGiYvdPuBT/JfQgXPsca5zUpD/aSvtljFTA3GzzzzV1vw/Wn8HVD8iSu+9cst/P/gl1uQvPvN'
        b'ZRtMjZGqXrkO+zQaW5w9cR0Y9z2Tzqulo7EvmkaEUM+cVmJsrNqAnzvAh3/RslZ1c3QsqciM9nXMWaEevxZbYz2BVOqq69XrVDK6BB+IrlfrVVZUT8qQDpHsSrq2SYN4'
        b'yYfw+NRvljoWk0/HgEucwJhctKlLcxHPnl9UCM6V5YLnYVusbBU8iZjpXLjboflxeJF8myYW7ADXCuCe2PwiGdyDxJoy2IYksMWIZ5dGwWNIqDnHpQrgVQfwdBpsIwI3'
        b'7Ef44yA8hK+FxlIUR+MHzrHA9uxQYvFY6bs0xgF/t7czm9qgcGA+ibptVWxMCZtCEvcQawkFj/q5qK98OYej/wol/my124nFr60Bc8XHfxE2nuz3itgpu1HyxoK4oJuf'
        b'LHc7dfeNn2mvilujr3zidfOvkm+beiMKdv5+6doHgwfS4M2Wy1++y3pjB/uxt3/zSsg7C1cVHXt3PXcTz2sU/PpV0D/+Sl4KNCk2PMlp+eTu4oXlwU0f773y/iH/ZbP3'
        b'qw8UVXadfbf7ypVKbsuhx8Odyz77sHgwiNro9FlEzsDOpMcir184Lz5WR5860r35Wu3e9746NP/j32R8+/rZdyq//c3BJxs2Sj+rWLj+sy++bFXv7lpXHTiWf+qLjosf'
        b'p/9yw/ORm1+ua5H+6WZ+TfdLf5/xRIx8n2Pwuw73/tIx6Kn8m0MXJ3IVJ1PiRrTdcWHwMlkrxKykKcpZ4AU4BF4mEpIzeHImlvbM30+G1x0dYTt7cwo4QYQ9cDJyEbwM'
        b'r6xnLm3CjiWUEzjLBqfR6pxmPu3XEaMiFeyJxVcyd8LLxewALMISCQ+JWluN+IPRsbI8nAMRgluUEA6y4U1wDRwmCB3eQL05iWS4/SXkC0XgsislnMuG3emoEtLERXAO'
        b'4JPbPXEl+N6ncf0WdjQ4A9vICIJqyzHllcjgATJCt3gaDnHqwGFXUtgVdoF9E/QF7gLbEI3hgfOk7VUacDwmDh9US2USNsL/vfASPMkBuzxR25hl2CiCvUTajSvmUfxF'
        b'8Pwstjd8iaka9IelFDAgj+BdA7c7idmgH+6nSMn1qAdYXWCeGXhMM4/tsyCaCPEVG/EHlya+2Qp72EgujdeQRNCnrGL6xMMTGgQG2LFIrj8tEf5YqVJITVLFMySKi7f+'
        b'uIuVPuEgIU5uzEdb7+WLKLHXkbSutCNzuub0hY16RJo8Ij/yCx4OsdzB9PAkybO7ZveJRz0iTB4RA4kXM89lDtaMxmSZYrImZfYJwMLdMddOnlmlfGgWoyMf8Br1iDd5'
        b'xN/xC+4LG+AMlI/4ZSKaFRGDvxlzprFH0M0d8/HHhfvKPvSJR1JGZPJdsfeRvK68wwV3/QN703rS8F2ZgbBR/ziTf9wYInKOPY594uOukyq5ExjcF3I2sj/ybGx/7IBh'
        b'sGwkJHNowfuB2beXjAUE9eb25PaVHS9+wKGC5rFMgdlf4HZ+GZj9YWD2N3r8kMUbIveFcbw34gQL5zgxNM6JoXEc1r+kHiYqWquIwtA+L1wU3wD8ziKgYE3wRkT7fL74'
        b'gV9WIgLKEX4kdVaYyEFdO0aRD7RNnKTosGmf7gh2TuI0J8ZWVK3S6wZw5CnsPMvQbvzAxzhnoWJJMfmoiQ5/2hVhfvOfhMf8sNF/T3tPSOKbTjVN1ZWVzEVix2ZdU7NK'
        b'Z2j5Vy7VkntKxKKS6MnvWVkEMlfkAUrx/5UDLKwqfPjsamLlmiwOflpFv5lFnvP5nMt2EX3hSLl69nPO6W9nmR4vvxMUPJAxPK/icw7LdTXr7sKcscVLHnBCXSLuUcj5'
        b'kodj73GR9/N8FuUXckckHROnfs5j+6W35X/Op3yD74hix8QpKMY3rS0PxQRF3BEljIkfQzFB2ay2YvxlJPqOKGZMHIeifBLacidiMnBMFonxnnlHFM3EeGe1LUIx/qF3'
        b'RDKmIn9UUcHXjiyX+awv+Kj3PfJ+/aWk1zx+mnQnkD7ncT30taSf1uARlLHuLlaMLS9/wJG6zGN9TmEXj6EMjQH7v6hg4cGHXpK/Fv5Th9sz7/gH9Ri6oy9xUF1y09LH'
        b'TUoVrqaOhVjeSmwcyylhuSTep7CL60EJXOx/UMVOcclhfUVh92sty9cl8ItU3LFQk0vQA7aXS8w9CjlfcijXmV/iIPMmEtGsn1wKdujzNoMbCKnrXV05lEsgG5Grnmwi'
        b'PS4QlQvBgAHTOyG2DCktlYaBl/hUQCI3FFyAx/9Xv4o65WN/U284OhQbMXTCbY7l8iqMb4KpYLBVTVgmJGjeAmcKZGCwBNyKR21w4VXWWnA+1kiec7iAJO1nY2zOFJ4u'
        b'ZD5I/iI4QkycEFE6kgzb8+BZ0B+LRaIkLuUI2tn5tWCvWrdlDVeP76Gefu4Kc6/S5/W3trIK+w2y6vhqUdKZWaXeMdpVZ/bF/2Ku8bPuP27v2d5T1NP5fnPVYri9pmSH'
        b'YAe/LLnLs2Z9/HxHjnD5WQGnjk/91yZh4lddEh6hmA6+4CiSxpBE3D7xQEOajNDapQvg4HJ40JZoIoq5BXaQkmsWaGNksK2Ba3OcfwIcZ6j03kK4C3EIqbNsFbmgXUK4'
        b'B3AEieCnC/LAjawic/Iqtgqcg4emvcXp3KxTIXZdVUlsqsNZ5m+d4+dvMdmcO4MS+zD0rW3BXQ8v8iXwBb35PfnHCkfIk7iI/GV1ZXWvH3Aa8UicCG8Y8YhqW/Cxm+eY'
        b't3/3ou6lnZs7uSitrcBWqhrn4lbH+cy98u/5MCvuG3GC2TYfZn1CxGL5/dCPnU2CSpH598uPUb1zhA+9JJaAr2OiDcI2v2TFLeeFUHKOH4XfEctg6/gkzEdhBxJ2IGFH'
        b'FHYiYUcSFqCwkISdSJh5R4xH3gnjWd8Rw2Ehas8BtSdivhIuT1SwklnyGebWXcyp7swrYfIkkio2p7rhsIKvcFIIkrlyT3OsSJ6MYrmolJflNS7z21/4vS9OMn4ZDb+W'
        b'xrP8l3uQl8AEZj/nIb8l3fLLteR/6PfheBKWe8vc4im5Dy5fyZL74nT062fbBgr7W8ohf4CNP9DGHySfiVzaJibYxh9i4w+18YfZ+MNt/BE2/kgbf5SNXzLhf3i88mgZ'
        b'eyFLHiNj69zLPUKocnd5LIbfJRJqyp8FXVqeZTbnl/6r+UkrnuaXwJirwoJkB7mMwIQXeafNgcAATx5H4rzl8TqfOg+nOkkK4pMQj6zMQSKzGjHy1KSzdatuAb+DhnW/'
        b'Nmfr+OUxLmoJf6SYbz1Rd/gPnqhP+Yj21E/MC5gTdVkLj/rHak9sVxn7xrpoxq4yPmgflVueyKZKVxe/5RHIRHbP3sQ67nSfR8UrV7bkCSgj/rDzigIkpLVbLFLBVdhf'
        b'uDh3knoNIeV2B0pe5yiiwUukosbAEKqQvwdjpKqRzVLq95ZOEnSmvndoM0+POUGB9meXq4+9LVmCPyd7EL+J9E6+c/CFM/tKgwpcQ/c6cwojvN9yrb3iXrU691dK6lLP'
        b'hTPx8WGC7XfeWfq7ualpnPnJMYXr44WFddHVjm+V1w5dL3zN+bULsXSC19Aa0QHPXT/h//4Sq+Wz5qAbc976Z0D8lkxMd16TiAWaP0icmAtfl8AAfIF89hWeB4fypBzK'
        b'sYxtgKfAdiI+R+mXgHZwsbAoFrwIzyBZLpI9Y/YTzLNFPaATHpsFL9h72+gGEjKJLvTl/Mrm1IcVksyMhfvy6jPBS6SyKNSNbZ4LmGeIYqKkTDaUyTuAO2seZJ5cio6C'
        b't5gv1CKRGFUBTuDbktgK7BgH9DcD82W4w4GIGbBm2wS3FYELFMp0mANOzwY9RLhHdcMdoD0OCbdI6r2WB/exKEe4lw12KsHR+1I8vHZwCEnq7etRPYRlynsMnAcd4EAJ'
        b'IsN7SuB+GZ/KKOAjKX8IPCfhfw9DjTfLlEeG3K27a/IrQy0UQ07LZ1Azwzq5TwmxBZT42OPIK/hcQNGhfbNGZsZ3Oo95zOwLHvEIHXAe1I1EZQxp3qoembOYmD1ljfjN'
        b'GhbPGgtPwC/+hIyFxAzMH1jSJ8PvEI0Fh5Pnf8w/QTRuYiw4rI/XyT3sYkNxGRlvnEdM7Me5+MbPuPOEUKVtGndSa5uNBvJqrD1tJyP1mc+mbN4BSkW4KY5tcyy1cgaL'
        b'lY6lvvQfKvUd5UdTzwlTftwjQOZ3YHiVeGjTPB5iu0qWp3+wTd7EWycrjq5gXhIJmHgkf8rbITLdU9RDX//9ga+wuFTaTv10T53MQREL2JOe1Yl7LzCO6WCQTQenvvoj'
        b'+3d6J6i0gsKjurYIdU3XTZkx4TeBeZZCljs+/3Z/rG/7YKitbFRP+2gN7k4+7s7EQzpeWCNE1+qaGv/9ftRO7odyw6P6UTS5H2LSD3zD6z+0OvxKQ5NBqXlUF0onwfTK'
        b'oyvNzxyV4YKWm2PT9uf/7kHwv0D8eQzxvzyHmNPRvxeudu6VKhk6n9bAx28cls6Qrda4hRZR6pTWv7L0uK2CI5st8t1Wp+2+j297hv/UEfDW7c53fUDfzvkvSULLvLe5'
        b'HJJ1linvvkNR36byUmJflbDux6CyiBoeTLKlF6BjLWibSi/CwPnp5CuiABqfYUsWJp7Iwbwepgo17pRPwJHNXZv7Fo96R475B2Cz0uTe2T3YpHcg2+QtHRZJf/wzOUvQ'
        b'ssrZNqdR1e4/4jTqf1WVMAU8pqoSzODRms2jYp/ACritmjH/6zHEmqLw5EJcmkW5/oPF/bn627lxXH08itD8zmuLZAI85vks31aDZP/C+Or4QxKPMk/XV/44N/HEtqRA'
        b'6sFrPG4XJWHfx9dgYkAXbJsMF+AAOAtPPgwYcH86o/O/BZ7Nwir/aKkMS/Tb4Vlwk520csa0YrlbJbkqqG5VVVZpmqobxn1tQGhyEgGlaDMoNbtTUbHYfntQYYrMGo3M'
        b'NkVm3w69vX4ksqSTe8Sly6Vb9Z4obAosjfPIxbrvkcCXYQl8OXKW20rgjQiafH+wBP4wqsGKjy9rKYvccZh5bZpK5vyPwNMU692pJ4PmZ2N7W75mfcahou5lbX5M5lpJ'
        b'MQayT3rCreB8UjbK3Uq1xsDjxMIjCuwWg/Ma+Dyano3URtqB2Ig0wMuwd0LeYG7AlUUVS8FJuINFJYM9fNcZ4GlyY8xDwlgFD6+vKnySrqDI9adDmcXs1/nUhsG8xsI6'
        b'aiGlo4z4Y+aInT0Ob1kecZ10C8oMhRN3n7Swj0WBftgjgEdXNzDqRQyYm0IiYHseox2DL2aZFWQUPKBecq2Tp38FZfnusdDL1SfRDol65/Nbd9ce3BZ8IPip7B0s9pJu'
        b'H59NLT4+87qf2nrqzD6RaXXOecncDF9+33JRmbMvN+m1MvBfM7jnXGqvRtetzv1t7eq22t3nVdvOFam4d9xBwOvb31iwdCntJN/zR79VQ+3uJ2hd8DvNR158fOHcxpon'
        b'j72xvyZUL4o803imdAXryYbtQ5eGOjm10bJVr124Wni1kH6Cmt/h3T4r8qNFc+9UfVIVYaR//iCZw0kbfsfAfzeZmvOzgI8/K5M4kIOxpfA6vGVzrlYL9+GjNU5dAnyF'
        b'MZ44B/t8hAWgu3WK4JMDTzCPpW6H1xMe3vTMhl8Ndk/seQ82uSlTD0/BPnhjjTDaLCJZa50JLnPhRUXAfYz+4VbHcGJpi4UjLI1eyAcdFjQCtrnzqXjwHD/AsIDgERU3'
        b'vIB5qgMcBB0W89CXwRBz9HgNYaVePEys+wPHyy3awefg8xKuXSEGQ7v1RU/EU6zXqQ2qcZENriExBMVcZlDMl+vcqcDgzgUf+8+840MTSnWopS/p0BMDhoubz20eko/G'
        b'ZZvism/XvFUNGz4KihqWZI0EzRr2mWUlagPu2ALTW3qJM7jgspPJO2No/oj3Y3f8g7oNxzIGeCP+0o9CZMNxxSMhJcMBJWM+AaM+sSaf2Pd9ZPjYzaXHhQkPyN/3SRhj'
        b'7DX7QkbE4QPii/7n/AeXj0jmmMRzPhCHf+GJemqD6/gMruMqdXV6u9STb8F3ZoSHsZSuBjnlNgjvgdH9R5xlPcUPo54RxnGKq7n2yBix5mBZNC5E34IxIDuZa8Z/3EnW'
        b'HDyE/2zwoa3eBWE6bjaP4L8psdOr5qe+2ORQzBj994WCfQBfbZ1JIYL21Ex4Guwmj0szF1/Pekti0AQZKT68bgSHUkkhBTwNnwPnCXZEhXpa4UlwQ70xrJqjz0bJ/19z'
        b'7wEX5bH9Dz9bWXpbYKUunaU3AVGRLt0C2BUWWGAFAXdBscYuigVEI4jKYl2si5XYM5ObmM5mkyxsei83ycVoJO3G/8w8Cyxo2r33935eQwbmeWbmmXKmnDPnfM/dHd9f'
        b'LG4bkrlvGDfZJKk1SZDV5n5jwedWpebKLJPpdbG5oXJei7mnWxIvosGsNKx0BjmfmQYZhc5go/MZHkm4Ec2R7Yjnx5bJYBvcBC+jmYTVnxmUUzkbNMDG0D8g/HUGhE/s'
        b'10cRPnlCCD+UJvyB6bbUOBetwE8t8FPaq+x6uBrBlCbO+w7OfU4uAyxK4PKxp89pTq9DcK9VsAHVGY0oh8owdyzzffyGVW5E0Xz18F67GCeqQIF0iKv+FYOw2DIYPgOI'
        b'q/b5OxuuABUziuyGdzsi6GMbkJ0RIjws5DMmxGf0f0J8f+kwR5MYse2+HQXbQQtqgwsFtsMOl2zQJb2yq4Mpx3e180U3LxZ3IFp6+hX9oZ5dslXVGh62bj13U1HaR4WF'
        b'PDHjxbbwxGRZf2LrncXjxIvXe5yJ2rE6Psxq3Cslr2DkzL0KJtX/s/ELi8RDI/YXLlSNqOELVZqITMkVip6S7AwoaeQxIaeJenJaYEvxxzVPRsTT7+Cu8Fbaah2C0FG/'
        b'39lNwWnPaErpF3gp8pWpGkFEE0fn7Xfau9chtNcq1ICyTP4CZY2ttskIoQ2LrqpwtmoUVBvS2nxMa/f/Lq1NHEtrwytLFWUoVCZLnJF+keP8f0Nnjx/yhuiMXLXuA1vB'
        b'8dygWXBfRBoLNrMojhED7fpb0qTV4BhLjs9cB36bd7H4EKK2PTS1yWte4QNn85KEeN5Rm+nP81+yFPdKJIXr7mW11vYLBHmCGA318XgOyJuClixaDxRcq8QGuV7TsElu'
        b'NGyZjY7gv0tknCEi05uZFuidV+ipTGBAZaPeEEIL1BNa5TCh9Tm4KSLOsLpSVN6ns3qi1IEJGr/EXo8ktUNSr1WSAWXxxlCWjlsqLq6tlj1x1+QZkBRNUFgcIatFwXJD'
        b'gqrABHXvbxIUKb2V60cpTSNYIkvarJEYOBJTR2z0qDMfEaNVSFbozJdV1xWXS2SkJ8JGR8N1psUYJlNSVSuRhRlGwnW8Eqmcxr/EFpM6zjJxLXbxIqmrFdcTRyVYwUNn'
        b'JqkvLhdjtxz40QWSEuuZh+lMhvAtpSUGAF0XSYpaaW2lBHUrVj2R1eFgGQ6e4HomR8fD7iNxkTpT/NcQKhZ5TGBoyffCZasZWDcFQ9wUVdcTIDAdp6a8ukqiY5WK63Uc'
        b'yRKxtFLE1LGlKKeOVSQtRhGjhKSkafk5eTp20rSZKbIdeKR2MsYwZLjP8V3C/RpqyMhyH0WumrCSKd4bqHyTSN7/CWv2GC6y02OztphmzX5zW8P4kUnNUbm8bHd7UgXN'
        b'0cDdsBvulsMrljIOOhkfopjwBMM/FF4icxwch93u8tpl6DW8bMoAZ6ZQRvAA02JJah1eluFZ2GQZgI/XZ/3SsoPTs2fAhhxwNhDuDsmYkRaYEYKYLHScF4Er6OCxlcBv'
        b'wJb5Zkng7BwaM+IYvLUQtmCloZVU9ZRs0Aav0rghZ0sDIrAVJsOXmgSugJaAcsJIhoH9s8AZ2BaB5kkEFQF3h9HJuyNAK0rPpBh+VGQU2BuZQVQawC0PcGrYGI2xCl6l'
        b'TOcx4TnEinSQg9dqcGQxyselGCIKXIIbwT54yYwo7heHwH16O7s96ePZFAd2M2BLWS7pya8qAqg8NOyh4u+CPU3H6ffd4wywERXGoBj+1BJbfC0SQ5RO8mET3JMZHBSM'
        b'8Wmy0d58KQhuz2JQDuAYOx6ucyJF5rKFVDxFxYRWXVv+ilkqRar3FDqtdaIiWRQjkJpVDVoRy7KJDExBVG4ARrFMR6yLMdyXzqEswU5W0URwgL7Hy7Wn0HJmFRqcwU2a'
        b'VkSRXqpLCUJlGVGMINTxRaBtHOwkTUV87gXCBAWCLjboWkCxAxngmu9qUtIJhzhqNUUJQkVr/Xc+lUPXy8bJIiISqCiKEUyB23ATOLAUXiBlOcMmcBQr1WcHMSjjMKYH'
        b'PAFaa8BRUlZWZga1F3db3VK3F1OltFnGdHAIdOHS0GCHUHALaAPtcD2PEOcU+DS8TqM11oHzRCNyC9MTHBeT4hr5bNok2Ocl0/UmfvQomCzGlBBF4R4DnVZg3yJ4hlaA'
        b'2T8lOhNDfTbCXWhYsVFGNoeyAJtYcWu5tOFxSgyFJnBo6IrN1bViG7qpsCHIB5XHJE1tTAH7wWXYSiA9Y8qhii4wJwicGyYyyhHsZaNxO1tE6rMCHrJB+bm4cRU80Ar2'
        b'wt10fbrATkd9fjSI4EwIap9FDSsGtVlF6sMzsqXwthLq+k30T+xCPZUpE1ZHhGOKDUSVb0fcQsNkuufBwfE0weZljWcier3AgHvt4QF6grT4GUWMRwdzRjhie6eCp0Pd'
        b'SWklpYEBmah3UxcgeuRKmeOyEU2QzxyNWxERjTPEUGJwDbQmgS20ltBhsBne0NPednCeAh1gE2U2iWWV70k+5RQDLqGcqMNiKXhiLjjg5kcfF7Z752XSfSQCpxBHn0OZ'
        b'WbHsQEcwaeyzHjzivCc0atf89+3T6c6fBprhxYhoxEiiwizhJUQbPcW0XU0b2BOKaoExeRaVZCLKKGY6wfOR9LJya/palAsR1ER0SpGAA1HgJqlbeii4mJmJ70KZ1Yzp'
        b'5fGxsIce5Bv+4BjKgSo9iVoGr4L2Bfp5hvq3BVzLxOvYjiAGviPl2jKN4V6wm6511UrqAaZo0+DZzWmZFDHrKbYQgIuhkRyKkUgBFYbMgYcQs4erXbjaCjFcaNBZq8EV'
        b'igVvMRCxH4PP0DfyQVOpHXjS1u1N77JbQ3eBS345LgytAEmUHTwJFGiZOkgPUTNoQesKWkq4FHMRw2FpSC2PlOO2aBwVirsyJ6ysnuNJlwO2LuBnpgemczByE5vNAB0m'
        b'cB9NG41wz8QIDPKEja2o4Gi4k+j4w/0LXIg59Mw0uG1a0CxaZx82ZAeiRYeCjbbUVBsjJ3B7MbGRKrCDW4chmfBNcisTHC9H6+nBeSOulZ7nsmjT/lnyuT+yLPQUfRru'
        b'cAFK1JgWLoVWrUD4TDEBwoLHoWJ15uhr86vgLNyNthg25Q1OceqAcgo9TN2Ig94PG2eMDwWK1XA7m2LbMNDOArfS1NKTDNZn5sGdiCRgGwXaVkEV2Aq7aVCudq8MQ2Qx'
        b'2AFP0Y3wnsaRsspI93mCg8agB26H7aaYvtAP2JxEQzatgw1VAahrsuGutKAMNLwFYDdiqcPYlE8eJ1wETpCmi/OcqEhMKYs+nRMdtIJu+opVeaiRqFAjjGVAYYCjvaRQ'
        b'mzJ4flSZUXAzLpNJ+eRzItAnb5P80wTmmTPQpopxq1aVw5uo8k2EBHNK4PFctBvv5IATdRRzFcMZNIEr5FVVhigzn+6J46gnEIFfcgMt5KsJYBNQGUK3kV5wA41sl0Xw'
        b'CjgDzpOv2gnBTaYctptju3j0g3a6W/SSdrvEFk/x4PRAuDkHZU4PCmdTTuAAuzJqKj3WJ+zAAaiYC9tZKPNN9DMzmmAwmBXl0TkRlV3TZ2WirO3sJW7gINn7U0BrPNgB'
        b'FLARRaSUdL4H/dFdcA/a5NHo0TWGDbao0pa2rMUp8ApN4M/4JaF5uF4vlXGDN8vJAh6xCp4KoKGg0a51C5FXCA3Z5gwus+F2l2kkt4sxaLaFPbCdg43L0I+xDWlKPtwX'
        b'jXr8FmxEZ5EKqgLNcyVZIbkyuC4zKCgdnEkHnX4ZWJHfNp6FLffRIkBYBng0Nn0GbDdDBV5CP+XwHJlCoFUOrw2buh8BR4fM3ReWky/mRJbJzc3RGoWn3xkLeDYD9BDa'
        b'Ws40ofiYtlKvFmUKrOndPgvusEanrr2wEbW6mqoGT2cTzDiPYLRtgbNpGMRtR+a0IFJBoRMbqsZB1Wp7IkH/IsPbbQ1Lgagyvuq9mIlRebQYvwy0zIxN0MupVsLr8Lp0'
        b'dmEmU16JeuDFnUH7np6fq5lu9UK0NPeAB0e3fYOQc+rD4x8HKZ+1n/FMvfZgsnplcepWhxMhcT9+96P1g19W2siixr0W7LvsRMtXrz169M57Gs17D08/5V7L6i0A3y9n'
        b'rHw74+cVH3DLN6ou3r16NE3K27hHtvmtO+q5h1fO63rJ3P+a/4Y+3VmG2Vm/lycahdZ0n7pQs2EGqBAtu7rns5+qUi4UPWVZ+ML7j/Z96qK5GR6b86DA2vPwmiNHHGMb'
        b'LxR/FPvM+2aHD7y5+/mVS18KOKR0bimbkP7cP/1bBNFWPgLgZePITWxxv9RUo4tvLeKVNdW8Hd9ayotIiykTvhK+aYLXwWirz8clXh9IDw7dlOIVOI7nsqWGYXzCqa7Z'
        b'PdDh1owAs49mfiTvecXqnPCjU+t7JTytSQf0T+pZ1Fqz0f3dZBDE+igqaaBJVSp8V8xb3lwzzfrG2+qL5kZWs/a0ffZChN+ZLulmzRXPo95dgubqqV9tOnL910UvW0Vu'
        b'q/znC1+8Py+xYNdXXRPLv4rr1+x1/eGpl0w+rXXL8ny0Nurl42Wpg4WfvRroefaB08z8l09bLHVKe6FSHNX54FH5N7EXXn5x2+D384vKNdfTHnR963P5/srIC//YUm07'
        b'ceXCd9SWHk6DNmsqovIlE+ZNvheXdfXd0lu/1b+8eO7PH884tWb1goCJc4QXqsLeqvzE5f0X/23iB4KT6o/YPpd7ozlz0ydzby26N+nbT1OezVkUXnfD44uJKfWvWr3f'
        b'xP44rmGdO+/j28b5CXd/9JS9k7vp6qPLYqXr+2Gbbm6YfKPsV7fn4if8Y2qSeYfg+bJvPjZ9v+v8ads5c3+uzKx63SQ21v3C9e+jH8G4SuVdRs/tR4yctK5rl9NFtkSc'
        b'GS7Dt4qj9KrAzWwD1SrYZk8gP8C2RaUBOUHY+vYAwxRezwaXlhDdrlngeCE6fiGOhVu5hGInM8BNuMmM1qFq43BBo2WNmQx2WaCTx07LZebGXIoPOljV4BDcTq5BVsH1'
        b'K0xBV2BaXSLcqr+usIbXWGiTugFbaRXjTi7sHFZcBjezaN1lZ/3rYnhiMmgM0Rv88OBRZhXsBo3TwU5ygTEDnJ1CrjtoIS0vmwnXg5slxv4P8HwEXV4WaAajdi1juMCT'
        b'CblmNEhIB+wJDyDwZlzWkEa0IzhIPggbwTHQQvZ1JrgOevRAJzfBKaJLvYLJpbXd0K58JZDWdgMdWXpzLrTZDam6gRvwsMGtD1AmEAU12DML5SeqZ5HjiY6agX4aWmWb'
        b'6VTH0Tm6iU6WBM/jdAYaav6w5wF23bgAboQ9WB8O39VhlgnbiNE9kQgOUwETOIgzRLsvXaRqAdigF217+oBtowXbiNOizYfProL7hm1+y0YwUErheZKAZw4v00pxwwpx'
        b'sBnuQxvj1cL/2gRrNKIHS1xSojMfkUihKBFDPcvWmwfbUa4eesivCLVLlNYloQcFOXfmNpm8y3do5XaYtpm2m2v4Pkq+VjRBLZrQ468Wpaj5KU2M92357zp69nql3uW/'
        b'Pu7Fcb25eS87q73yNY6zevmz+mxdFPZv2vriu6DM5kx8SYRKUqQoIzSCkOFYV4RymUqqDonXBCRoBIkjqaJUvl1TehI1gikGz4jhV6UmIOnOTI0gbeyLxaiMO+EaQerY'
        b'F6WagMk9stHFkxflmoApd2w0guSxL8o0AXF3GCjHh3/1G0s0Acl3ijSC9CfWKkwjSHniN5gaQdJffiHVBMTf8XhCUeSF+++140lFSTQBk3pQdRN+N8fYlv9uJw4X9UOQ'
        b'k539vVhK4KHwUdp3Bqs8tQ5RaoeoflFQl1wV0cPtWfaMxR35XWZvTKY2ZoY6ZkbvzHxNzCxNyOxe0ZxWbuuyNos+B5fW0ua1Wgd/tYO/suT84q7FGocYcmEZp3Gd0ovI'
        b'wcmtI64jTjlLldq1qKfkdtUzVZqgrD5RiIrb5drKPmjxpwn6XTwUUUo/tWcEhrhL1ROognnSqNPoQ3yvGaAWBChTVTO6MrSBcT0R2sCUO553lmkEOX0C1w6TNhPFFI0g'
        b'QitY1GP0rOed0rsF6tSFmsRF6phFWkFJb1FJn8Clk6VIVU5Re03UCCepBZNIqfobKvurjt2OPdM0YVl3UafN6PujVy4KrmJZp4VWGK0WRvdwNcIpajwf6OLj1F6xGuFE'
        b'NTanH1tGtiYs424CqfHvvhppapL+VYYmbCo9r56UB83FaY83ZKombJjuxxSXqQlLG3oxKk/GXY4mLKd3+gyNYObj2XI0YZl3Z2sE+X0CpwGRncj+PmXn7vCAsrMTYOSa'
        b'cfsz92QqotR80dOGViumtGwcb8R/D9cFr5qPgbocxQLYYyg4NSQqx1fMM+wYDEcMm/d3TFuIqLyNK6K6TCNHa88O38GUUzRoALl9wfJcKt9o+PaFMUqO+z/3byekxspx'
        b'fWk57gYprdH3kUlhlsSnkBq5+kudjvbAFg48hVgrypVyBc3gNK2AowqsAi1UFGrYOGocuDgEvnsaMSUNEWx8LYzOU1Q44iwvkG98UU98Kceclhaa3ZoXSxFtm4g1REZT'
        b'IykvNNsmCKV5em3aaixV5nmPF8//ZYU1XRF0ANooiohkY/HeOrCPKq6FWwhXMiM9KyISsflwcw3YT0kQE76VlFLsRhQS/fYEFWbJSsLoot82t8K9IJy9sjBw86w5dCVW'
        b'2JCHPEVtoVlf6lN0yu/CiUvp6ZsWFlYuDIihU4Is8rB+2fTCyiKvJXTKRaaEVxKWuRSa/ZQ9iU4ZPpc89AscV1iZGcmnH36YS/xAC/y8CiuflzvTl17ooLRrEuGs87EQ'
        b'gpMP9i1jgGvwQB3Nap4XTosIDSXMdZQXBfZkpNPOtGM8qGSKmjPVuNBDNYNHc2jgHLiNjhan2XmraYaq2YnuvCPRFrDdZBI8h6Hl0E892EuGi4HOu8dhOzccbMIYK+gH'
        b'nKugi7pg4QNbGAmggaKCqCDQBo+Q73oUEv2o+oVZhVm3HWvoNrA8wXXYAvfh/zjgKGxBBW+hwOWV1YRWHCJhB2hhLIC78Q2ySxXcSaMk7kTUtG9Y+4mNzkbdcCtWfwKb'
        b'YA8NwdAlS8sNwlwrI6weNjNsVjrQtVPA7SUBRqjuG1FdqPpMsJ4oQ+R4ogJOU9nz0LmTWrEMHCBPfcD1+eA00282UQpzg+vIWkKG5LMyWuKbnVFodtu+nIZ++kHLL6Ym'
        b'vYfVFRmiK1K7w0dZ8no0m89m7r+Z/3IOiOffjLjE28DjNdh3ztrhOP5MX9OXbj1t822vevl88+7PrN82PPrnpVruKwfdI32WaeWvTR5sezjh1xN5Pnu58oSfYNG91Etv'
        b'Vge0cbe/OzV/wQ5Oph3zBmBs1Z00Wb0Y8f27T539dp2o9/Ipn+lv2Qcc+czXd+n8GyHeM7IWfCD8V8WnoWdL/g22z7tzNWw/5531lTPaX+g2DX2zWPOwPu9Bw7srV127'
        b'fOadpd/Z+xzuGudSK52//7WnX1YcazxktTyzMuSlZccvJ80+7WH1VNGFmF+e9o7Y9VvQJ/PeY937zdSF9cHD10wvz39lIWdw+alfbr+5fntnaYiR694DsCtiq/vW1bMW'
        b'uBxI+bgoKvreivindn7eMHVSa8rDW+cToh22jM998fyXXL/NM37my3Uf3/s07ocbi74//6rLhy843l6+dGecYqW9zTfij79xf/7eiQ9e+LpU1n3+wsv/XvUF+9/pA7fv'
        b'9qytr7evc5N/VnbhwWJu61dva11TS3fefGPv1wVTFnvP/2LTfJGAWI+AbqjAxpxPUgAj2l9wuz9tPXJCf/ZGi0Yr2E40/3KC/NHhOw6cgZeZ4Olg2E3zUpvA2RXDvFR+'
        b'Ns1KwY3gMGGWMtEHb9NMBTbiQQm7sSHPZTPCq4EzlfPSFmJ2IhuL+rB3MoxdmMAC5ybA9TRvtBWcccMQ9xiQcBtinKLXrGV6wC3wCq0+c71mlPfv0YY88LRxuT2LxnA4'
        b'CU6IcEUCWPBCCMWC5xhoCqjk5GUKXGc5otrqB/eDDcyIWHiC5jpPwN2oR9A3RIhRuwV2B+bQd0X2c9hOc+A1wuosQLMVnqWdleqRGFGI2uKNXYkdBnsIb2vrhLgj2nAJ'
        b'sXELrBAjZ6l3lrUStJmil90GlkQGXBqnjNhFOT812wAcCa0YO2lOaTU4TfpzojfcA2+WjZRhwMGND6O1BLvD56Zh26qQtMDgYHwpiCoJu1ho8dkLbhO1P3AkDqiGbJ7A'
        b'toWjzZ5QFXfRPXrMNIek2pXJmYRWPjaTAQ6DwwVk3G3hJvshLT6swteBKKKJWc0oJ3qItgVoBxqtMbgcqkaUBvUag2CrD6GBKsdyA34cdKGeOcpE/bjblLgkm5XFHeJI'
        b'EQe8ezRXSrOk8HYpIWdveA2vjwa8ZAvYTQysgiPpRt0MogL8hwDK4R5/glHe4PeXTKkMcCR0bGyToLMYYSVxnPCSPBYNnT3PgeI7NNW2TFAwWuL6nFw+tOJj5WatlZfa'
        b'yksxQ8k8b9Rl1Md3JD8O+nO3li9CZzktP0TND1ExNPxwVbgqopcfjV7T2I1KTzU/SMuPUnlp+XE9Xv18oYJ/0qnTSesepnYPU4Vp+OO1/Ilq/sSeBA0/brhUfzXfX8sP'
        b'VfNDVdYafoQqUZWEIUL++KP9iONlawX+aoG/hh+g5Yep+WEqdw0/UjVTldvLn0DeYxagZRpdhBK9DFTOVKKXYWNrnKvyuhrcHawNT1eHp9/104Tnavlze2fP/U/TRau8'
        b'tfzJPeEGPRCldo/qQfWP1fLj1fz4O6ilSfi1s1KGGqXlx6j5MT02Gv4kOo9bp5vKY6S/EjX8KfRAjPpOjMpHy0/sSSWvHOgmI4aPPsRrUJs9lGG9/KA/eTc8zgPRzmE2'
        b'9ylnke1gDMV3bI5q9dPYej6Y4GztPRBLWdsNkcebVr6IYOjYm1Y+fbYOWltvta230lZjG/ihnknjKNlav4lqv4lDXKi4zVIrCFEmaQVRiMVk3zZ9xvQ+iyFKYdyjGO4p'
        b'GOTaLhUjQVjb7TdtNm1NetNK2Gf4FQfH/fXN9Qr2SfNOc41DcBNbjzWqcO/lew3rsfbyvfu8/E5md2arPNRe47Vek9Rek3pma7xS9Pr7RdgPnYNTk+nj6jp/AbWF6OqM'
        b'Am25jRmQOyj4bogB+QkxIHMdGAwbrKvzt+xEfElldLwC2jJBLkvAhWfgYCqD6FkSw0NZMn6SjYPJDOxnjpz4RYyv0JHoETFv+grblYjGPQmNhbY3JP7SY3AwAQexuHTe'
        b'kH3Y0F9YCYZYSdF2MMR8gaj0EuVKovWGNZV0ZgXTE2YmZBfkzZ2ekqtjySW1OjaGlNSZ6l/kpuTl0pza7WHYlv9KePYYAAv2tUcCbJQtX8ckACyDXEuMrIKCex4U37nf'
        b'yrePH36Pw+RHNiTf41LOXv1WIX38SPTEOaohawRfJQLjq4wn+Cp66JRADJ0SbAim4o+fBJIndi79Vn404IpdWEPKQx7LPHjQhGk+nfGQZ2o+ZdCRbR4yaMY1D/ueQsGg'
        b'Fcs8mTFA4fCeBeXq3snvLO91Dul39ez39uv38u33ESm9FPPQry5PZYli0cgfXr5KtiJ26Je7j6JWYTYUc3VXeLXO6/fAMed+dy9FnsKk39tfGanIuudm5Wwz4MEfZ9PH'
        b'd2mTD7DQXx/yndpyBzjoL4zS694Z0SlHSYMHjPATHmXn1mmLSxgwxnETyg6lVvBbMwZMcdwMNblNrohsXTxgjuMWlJ1zr0vYgCWOWI1ktsZxG8rOozMJ13HAFsf5I+/t'
        b'cNweZW4rxpUfcMBxwUh8HI47UnaunSxFcuvKASccdx6Ju+C460h6NxwXUnaObUkKdmvsgDuOe4y890Txe16oy3FTsJ4oSvS9L37o7etsgSggj0E5u7WuVqar3aK0bhPV'
        b'bhM1bpM1TnH9AqfWLKW92jlU6zxe7Txe4xytEcTc47CcLBoyB00SGeb+9ykcDqYxQ82dH1AooI1E8I1kWA7YaHjuRScgJYeyymPNS4c3R7H4Q/7O72MQkTjrMVAaTBmG'
        b'mWB7IJZ9riX634jAJ1iOjuWyxsTZE4xcqVxXoi1qnG8Zyc7l0DAWQ3IHGWcBdxiCg0cgOHDcGMVNSJxH4qYobkbixiRujuIWJG5C4pYobkXipiRujeI2JG5G4rYozidx'
        b'c7oVuW5DNc21C8Z15ZKWmZCQOdOZeuxfrj2BeHB7/M1YiIc/Kcfhr5YTZPB3MiOKkSvMZxLJD63HZ4r9XkYa544b06O0v3kL0tuOBELCemTkcp0mMIjeLgt70Izk5Drj'
        b'FMN5bXJdZLZlAuMykbuOR/DYMnNSpO7o4LaylID1Dj0TFleK5XKhH/ZPvkwik4urSvCyLZVUiUxM/PMw4CPtLxC7v6wukldXSmppJ5bY0WFlNVbBxI4UJTW1tO9LAkLp'
        b'H2wiW0phJW6dsbhkmVSO1TF1pvo/iVYlj/Ynhx6zSkqX6VgVVejZEkmJtG4JesarQbVaXi0rKeaNoWwivNpAGWrMD3kUJeZquGfZqE85qF+4RLfZfNj5BC/PwGdolbEr'
        b'lW/gjCLfeJQUjZdgTGRrjz011GwW30NTzCS9SlorJbaAeuzkob6VVslrxVXFkhE0zuHOiNWjdY649cQ59Vqm2GunXyKt20q7YxfRDvQShHoFYxpGWVhXg62Zo4Ul0jJp'
        b'rTx4zFdoB/f672Dfo3/wFfR66BtVQnFlTbk46EmfmiAsLkefKCYeQoc9bOpH8sltot8K/bIR0aBPDjmY/8MWjR/bIkQitHPI5NRZwkpxkaRS6If+NPSPKQoe46mSDIqc'
        b'fGV0VUhf+IUbNEU0/CFEhrHCLIKEhHNNDcka9itKNwvNlVxxcTn2FEq+SRy1oimix0qtK6qUlOjnxOhc01FYXUX7GEU5CVQqitMt1c8kuk/Sa4c9rYr13VIkqV0ukVQJ'
        b'I4V+JbSzShGZhDHDFR+aOnQ30TGhtETfoRFjO3Rofuk9dOpjQpmkTCpHPYLmMpryZDgDhXX6bq2rwp40/9TLvCUtUK6swCLV+EWMmsJAY69Eqg6fautWwO4hY0m9C4fp'
        b'xFpS7yACcb4zaHtJz9LsdHQ4hZvjzaxM4T5SZO8UO8qPUjhT8YULEsT5FHHECNuSYNNQmXALaH5yucQ1/LApJiq4o8YMHlsiIwVPrMVC3Z611PTCrIjlblRdHC74KLw4'
        b'Ae21R52fUF8DGckMg1JBD2gwBZ1mev2s6hIs7b3rbiQsrLxVGkkRn5OwEWyuGq6wApweVXB6QK5heevgbmOwb9FEUtyAHIvKp0czCwsrv/F9St/+o9j3fCPYC9Y9Xk/Y'
        b'MCKXGlPPK6bgqBc4TQqum2NK8an6SjOrwsCYJB+K1sPeD/fC27DRHux4vGC/IeHLqFKvgdOmsMGRknovt2bKT6NCrnycs/n1yRaJ7mZGA99nPyt4/UPjBQucJz23qjLH'
        b'4vnPXKDnl2tSipsLc9uttoBHWtf7rAxdYvcPdxY9e/3L4B4q/94PnJyB+Q9Wzto68c4E1kGzH0qz32v0P/X5V+6vm6x4ZmDLixcXur56tu2Zd3bv/oTzQtiufzlHuN9v'
        b'/37p0o372AGhs74JnH1fd2YJvFMp4NYFKe8qu3I/6TD/pHAJOyDi7a8rvl20Ivs68/3Dt539zeHHIhNapLfHFV7SC8t8wHpDWRncFkOSrAE3wAVaZwHejBllqApOBdJi'
        b'vY4qcERfyjD9ccC2ZZQbbGXD8+AM2EA7LNljumqMzE0Qppe63Qb7iUzHFOUP0It0EEUcJih28GwiLb/sgFeBUi8YbAc9Q5LBjkIicYNnrMGBISkXOA836sVch6CKiO3q'
        b'awLHiC/RuN+gRZhY1kfL3A4Vsg0FbkDpNiRzuw6uPcBwzOAoVDHpA2oQvAivyIlgFsWyYCOvGh1Yg7hUNthkBA6B1v8WePYxxo3A/lgP7bujUX8caOzZe/XjKE+fzmKl'
        b'6GiVxmM8Buzpt7Vvqt3/VPNTGltfpbvGNoBA/EzVOKb18tP6vEIwxI87SaR18FPT7uASNLZBJFm6xjGjl5+BmKTOXKXg6EKNewSG/aHLXNu8VmPro7TW2PqTxKkax6m9'
        b'/Kl6TyjtmSilMZ1yRfOKljgFKtWb9iyncUzs5Sd+6OxGkvytwt1FJ107XTXuYX+e1NO7if2WlfBx5xmvYQ74dRz04kCNgzdwoMHBm39u2TbsNmOMdRuRF3yE5QzoDCrH'
        b'flAf/YhNKccxGDOJg7KZf8s1GV60jnDDqQumk/8ziKJNQ/A6wyey38MpGiGrIZiifNQEA7Ad+rw3dOh6AgDQfw1RZFZgcKL7PbAZDHU/B9esa7hmrmNqRs49I/X673CA'
        b'hk59f1Sf+bg+I/g7bnR9ho5hj3XUfzOS7AJ0RvyjuixCdbk/DMQz98Bcuk5OdJ0MzpX/q/qgo+Qf1UeM++Y7xlDf+I0cOsVj0aTk/3WlyodGbeiY+Ec1Kxk9ao74BsDg'
        b'RPk/6iDjgqFT5x/VpezxuqDRGj6vGtRFxCQCSFoUOWxRl1PMMvg6xtwmJnXEb6GxgRkslzCO2HeDMfFdiD0XmudbRJoNG8Ua/Q+NYjeJmHX5qDImCSUl2JdOlWS54aij'
        b'2UG86qQgRoOOYO5bXFKCjuXoMC/W81nEWQ72uxAoLJNV19XQDLhYWFy9pEhaRXy6myBy8h9GEPMPFPobgp2hOMFTQ4mKqqsr8Kcx8084C/qz2IP8CPc6XFCsMLd6Ceax'
        b'aNkA9h+hxxkTF1XX0b5/8BhJSobagvka7K9egptUIi0tRTwGWgNo7mZ0JfX9QfwBoWaX6b1dlAwzR8XiKsIb/RGjGhZlwN4J/apriK+iyhFGz7AfaCbosWkn9EsokkmK'
        b'y6vqqsrkeq6V+MAgFRkZF7lcWlZFhiaYtNGgIL0bKqHUsNZSxAAiZo+UMsTYhZFOj5owzN/hksNEgVj6IiyRFNXiclGKYsSaSXGkeIjlJFQgJenlklrS9pgJaMxSsaUt'
        b'kd6MJS2pRB47PKaobGmtPgHdD+TJMP/ql1tdWYl51mqR0N9/CWbi0edX+PsPc/+kRqNKoB+NFDEVNbcqKCQNra9Vf1QUjYamZ0mr5aTCeoS0J6bHxEqnNiTfYGH2MPdM'
        b'yLm6aLGkuFZIepCmodxpMVGhYXrJFhZc0dQb/OTPjLJkjh0jZVhWLS2WDBNMoqRSUlaK04mE88PCFz6piHB9N9dJ6OpJq0hF8CxITs7OnjsX1xT7x8JVrRGvWEK8aUlk'
        b'ePENFC5B/TLMixt8MHz0B/Xdh1EPRvcnfjJaUkJTV8gQZZHP0keFRFRpTPs4Dyo+InTh47OnQrJiSO5jQGboKaLQKrmU/mh1KSlVXLIYjQxpD05AXIKJ6/Hf9NymJUKj'
        b'EsmJiEpaXF4rLcNVkReXV8IbaGWpFMWO5AkSonHJrZXUock+nABRgFSobwKaYUsQRabkB+WJa4skWCxXos+JhoN2qFNZt6RCUi7TP44Y85iUJq4rXVlXK0ErE/aRKJxV'
        b'LZOTj+rzRMYKE+pKyyVFdZgUUYKEutpqvD5W6BOMjxWmV5VIl0nR4FdWogT5S+Ti2pXyMTXXp456UhX+vEHRT8omNfjskj/+bMyT8v9xuyaQho90zZieIUEePdJYfjbm'
        b'u4+NpGH1SmXo6364rcNliotW1pWJRobPMLkw2ntkAEe9CJvgPTJMVSHikSEZnSzKe6T7R5KhTh3+vkGaGMPHw5+eMCox+u7wgqXHNkAzRv8XWZ/RHozm4tBU98ul18jh'
        b'BXYEKiFWmIQiQjqG9gy/TBSVVKH/0bAK8ZoTs/DxbOGjs4WPyRY+KhvBW6CXjFkJeUHpyUK//Nxa9BuvL+OHkw3jMdBJU/LJTMYPhH6IKPVDjLp1pBl1MrTlF6PVIkn/'
        b'V6DQYK9LyZ8p9JsNj5XLEJGhb0WOfMoA6mEk8/Bj/UeHssor6mRy0ajt7/e2T7J1juyEw1tYwijR7ZP3BAI2ESvMwb+E88NDF/5+snA6WThJNtIbQygV+i1TH8cHbMN+'
        b'JpAVKAn+hV4sNBmZJWkSmawqJFUmrkNBZXBIqhTtZiOzgrwemQs43Qj94wwjE8AwJ6L6lHK0qaC5PEL6pCy055TQxQxVDu2aEkktXnnxb7RBRI3af4qq62OF+GIJrf+l'
        b'eJdED1AbQkclwlgadCpxpRBHRqUoltZigkHhqO2HBgjBb+g/SMZAvK8HRYRFRaGeHvkGxuJAH8C/Ro1AqRjVLhURreFDgtaBegD/Es6PCh07LfRTwnCEhnBCYoWJ6C96'
        b'55wfHj3q/TBpkSSjrwZGtXcIXUSfku6PkcmJMUTQFpKYkIO6Y2SGFEmLUYb0JFQUopA/cZqpF8+vTmEJ/RlEE8XsXWYFRaxMzeE6cBArtHWAPaOMrvet5ZBcJ1ezbaKZ'
        b'Vhj0Pcshzl7vMP0ZsA0oiR04Fc0gZuBAAW+TDOPm26/ezJyDOKDC1UuWJ+uRG3fOAT16y3CvkmALcJmYqsJ2sCV5BFgDo2rMnQXPgYOglZRVY7PG8ydqAOPIO3EW+FHE'
        b'DZzlfLAhACXPwL42iFPmk7ARnMnIphEeKWz4NpOqjzQugxtgAzFEnV0+LYbPbjCnasS278z5t2UZVTeZIoqgl8C2J0E54oLSyK170CzDK4SdoM0M7Ie3RT7LiBRNuviC'
        b'jCU3QmznDiPhoekvZ8B4/uTl4S1TWx7a6hxNrmk2byvqEtaebZ3IcD+97sTph9W/FlTrsgJ29MeEmh3UTpZ3XKyec7PT6eBrJ5lPF+oqZr19hiMtcN/+wSSjVUtanN9W'
        b'RW3ol3bmnMm9HJCQNOOYrPhksUqt5PHC3/9IJZi+P89Vc/6XB88uFH2w/M78Z9W98s9+2HG8bM64D2ab/SutVJf8Rem2iocplz9958u4mOnZUaeLPrhuv+QXv8k+3/9r'
        b'il3wTt9pbkey1/tMfj0j5OLnqoSOpQEX3//KPXDq94u/Xh7pJtnd3v5TlsVr35Vcne8v3eZyrrdkV2NvjsTypddkb379xjbOqhkudX1s09oHbtMu/MLwnhM69ZMWEY9o'
        b'jRanrqQtB2m7wRR4lBlEzSfOOsX58BZtN0jFwBZiNmjmSztZOYC6dn8A3DYtHZxhU9zKenCQ6VEBmx7Q6hDwgCFAPtjvoZfAjwPdD7CDAfg0OIMoYaxEugA+TQulDUXS'
        b'YaCVKI5mwMPwaQOwSHA+YBRepKuIltlvjVopx3QQ5IfTYZfoa+F+a9jEAqoKeJCYh8JN48G1zKx0BsWcyYANKf5ieEpk+b90JoV9FhrY/422ZtGZDYsth0wAMxh6BD1X'
        b'ShiodQtVLsVQ906ttRpbz/edfPt8/VrNMAial2JZZ6CKpXWIVDtE9vsGdOWqbFUlPVHdlXci7iT2Rk3VRmWro7LvFmuiZmqCcnt981rZrbPazLAvb27bJNq3d3Nyn52r'
        b'wktj50OK9m/Fr7Gb8PbhBJ9iifQUjWN8Lz8e+6dZoJzQaz++idVna99aonUNVrsGa2yDCWCl1ilA7RSgcQhUcTQO49919e8NyNG4TusVTBtgsuzC+kMn9Hj1hqbcsX0j'
        b'NAUrdBLzI1u1IGiAy7IOIgqPXmq+lyKXaIEGvcEPUvPHq9ga/vgfHxhRzt73KQYqxTVAmaRxDe0VhP4ywEIPfnnAowTu6J11UL+jr5KlcQzs5Qfid9ZBPxNAQmhun8ym'
        b'oJdbsiv1HNsk2Yn1nAUv2Z71nD0H/+1qkjye9ZwfLzmU9VwoB/1Ny9otaVn7iLTKm/pLeoO/SwWj3FSPsmlioZFfjCXu+EITw3/NcGIwwrC8PQwDGIb9Hb1C7PLyyeDk'
        b'BDGYrQcn5+RT+dxhxMz/uadq2SA1xnWQ22NbnDe9xV0K1kP5pMbN7khMomjUjmYP+Iy8bsZ4c3goFCNWoGnNWGOdR9s74S4FbeGmeTJT1GuzqdmzwA4azug0PA235o4n'
        b'WQKMGPA6BS+VgC3kQ8+VDGFg9RX8FF1Db3LThOCSL9hODJOwVVKYNbHDKUA7Xxvap44TQyZsxZSQSQpxdiWWQVahUQ0CuWQtbVg0s84a2yXFhNpbpxqz02mDlY1Z+odR'
        b'K32cZIl0ymkcc2yX5Bfqs5K7QDiTTtkaoH846zmJuX8UnfIipQd2KBXa62bm0Sl7pfqHy0JmrbFbSD8M4OmrZG8av6Q2lAaigU114Eju9OnT0eZuwUjG3qmPwWbSSTKw'
        b'rjAiNDQUQwOBBgY8RsH14DjYR+yM3MENVu50CtvLnwDn4Hb0zkFE7/sbYAs8QeyfwPlptAkUtn+yAKdIl3HZNbT5kxfcCTdR6GhyIYUY9WTapI0De3Mp4rEMXgObyPgF'
        b'p4XGxUWwiekZOpg00FZE18HpyXATOA8xhmUQFWRXTsCgVmTaDlstUWhoumirJTGHtDXNNjh3upCF8UD8wEU7LuhESQ6RjCywcQ5ttzS7dMSrmTtQ0YZFuKPdHfToQz6x'
        b'838yr6T7NMZ06OECySJ5IA3gupxD5eIOpeDGAE9KXCMk+csqsLoDot+cOHa6Zbn+sHXQHZzPnQ4UIopKBVtj15jCzgnoAEUQh5oDQKvcPAL1lWkCE5ym4E2+mZR3+SFD'
        b'jmHqrnc9Op6XOQ3EWx1+78qNz8SMFcaXbX5IHAD/SD4v++gCfD7C+F5fwcdvPfpn5TsLQ69bOeqO7W776dahwa2PTM833bGxuRJkrAr5qP9C/m8WH7Wc30oZf/BzWNqt'
        b'orZfvbX/mnDHh512WXH5rv2DrEkvptQcmM+UfRWUQb3+9e5tF5Y0HlbGHovjjtuTo5zw4PjV8XcmahZ9d/dlnmp10zcR6RKn5+LnSmNiTgUcXrPt6dz2FzK+vHLWoZOV'
        b'G/FTl+ePJv03rfpD77bz5+5S905LPvftwcBs+EZs0VcOJWHNxfO7+afiXzh1Z4n76vpNbgHGnUZR83a47Fj47eBbvjnbDzfcvPH6CYvTn/fHTXwz8Mcp60/90r11zY2j'
        b'qxSL039tfrVwIHJfHL/7OfdlNZec26rqa3+Mfnvev3eVF1f6JdXtu7mtYqW35opxS2nLN2tzsieumHj1+Gvv34gOy8qv/vib7V+94v/wU9WO12YFhk9aY3brjaDjV+3i'
        b'AgP2S3JPOO2NKjn4XWpr0g+/WM7pn3Hi1UwRn9ySm8IL2DLF8ExSgXGfpj1+JgGNeldCe+1TMWi5CMPmZaPXPHidCZqhAlwjhyvYMCkUnX6zGGhiWLHdGShnBzhH9AZy'
        b'KuMJUvVtuIU4kidI1SlDQNWd6MNNI97v4H64jTZ9Op1Hmw11zPXPfIJZkjDFVcoxTkqirZvOo0nbQ2sfUOCwO618gGZJJznESU1QKw0h958Bu5kRVpD2FgQvhtC2T7SS'
        b'BEb0G1K1cIugG78RnlthaDy1Fh3rtjI9wBUTchKLng/aQSM6Kh58gtVS/iTaIuYchhfTHzIjwX4am2KnO32Uu2YDL8GDsCFzlNGSBdjISgSKTFqF4qSFCHalj/Hqzqou'
        b'gTtpDYw2uJnhXZtpaLJksYaVLKeI8kQ8KnIfaPTze8xgCa2NXXQJDTnYJxKtpEGhQ+htWklDNZduwTpLf9oWKcRj2N0g3FtKip+TAY+BxgDOE0zQ4NUi2n39nvG2j+mi'
        b'YEUU1OG3sDLK06DzP/BNP3LWwHd/er/05MRp4Jf+NFMPPOFG/NJjt0imfUIvrTBULQylLd21wglNaRh5vB4Dk2M8cxehwq59ntK9bVFT6och0RjS/PRTTSmtfopZascA'
        b'NT/wQ74bbcOikJ1c3rm8T+DUJ3BV2LdZ9gmEWkEQOvmp0PEvUiuY3MPXClLu8DGOb97JuZ1zVQyNIFwriFELYnqsNcSYvsMSG5XgTEqxRhCqslHZ9grG4xcW2Gk9gTmf'
        b'oRGEqJgqVq8gEutxp2mdw9TOYaOL6knsSeoVxJP3Hdlt2RqBv1YQqhZgiyQBbZEkiBlbwfgeB60g407qE5+X30nTJuerk/O1yYvUyYt6C8o0yeV/J6UL3e5FnYtUqAXR'
        b'qD/UqEtQK+NRf3XaKuYcdVFjRHcX0oP6H9yAZKKoYqGQKRm9Av/fe4gK6RO4oQoNjHcKtb9POfk5DEZRAtfmZa3lGgffwWgnO9E9S8o9diCVQbl5dJS3lStWaVwjmkzf'
        b'txV86OVzcmrn1N/tZ1Ly7wwOaZbWO0rtje2hBLGoF9QCbA+FoS9GaGGIJAasjYNQ9Yy9HQZtRqqnDLhna+wdhejKpzl7gE8JXJrMHocM/2N9FwIZPnYqyBwR0X/KMrDk'
        b'SXFjMGwG/q4lTykui8kY4/Zl2EEggavn6HFh2Xp9cuz+hTuMCcv9H2LCbkKHbw5jzOH7cTRno5w6jHmMVuwT4DZxET8bnJ6ehjYwtEmBrry0YffmaXCLUQ28DK6QA9U8'
        b'cCwULYmniZYbqxItf7AdbLACLeSEVG7qEoDx7JpC66l6eAqdyvFXLb3hgYBpTHh1EsWYScED4Mp0qW0MmyN/gF5+fjULewG0AtbY6VBr2D8SY7LHuQeaK9O2j2MF//vM'
        b'c19Oy2P/s8w3Iwh7/PPNimu19ul4SQDsntsp3SDa+xrrgN1zjfPjGtxyg1uN4bLZiva+vetKORFbVeuUBxKTfHeH7XVPs7raD8xci8zMjmeZmXFe6tyRAFr9PfdmtwkD'
        b'OdwCYy63SmieJ9r+ThZnS+0CcfAu0Rbv19jPioO3TQvqNd/062fs+7N5122CB9OKL3ruNf78k0J7QeM2993ee73T7HPX+EWA7GcLG/iLgpsGMsqml/Qm/GipjNuZvj7B'
        b'1Y+VZ/v8ncKXA19vev5umwUVGe0TrZktsiSAS7BdNpV0PWLSohlog7wJzoFdHHoz2eSQhPcBowRy3sD4UI3MNU4RtI8cBTwAr+HX2MW8EbxFcXOYzvC2K9mvI+AVtEmh'
        b'7TwwOB0FJeA6E51oVEy0dx3KJCnAVuJl5SK8tJwITqCSwaSMwUkmOOoxjt7qTi2ZnxmIzVu3ZQXDbmsGZRrPhK0VeqioNcIo/IGQaUFMd7ge7fdMf1T1fSRrDQW6DPyH'
        b'oOG3XxXKKoMHlxJR0sJQY1TxdLgziOsZT3EXMT1Xw0skoxM8AzsDiPltULCISVkKBbCDBTazjGhoq06wD52w0PkhJIdTCrop7iSmAzg+neSVecF9mZhkEdHtJmRrzGeC'
        b'TthNa18y4wE6FMGdpL/gTXCS4iYyBfAqeJouekNsxigHw76OoDsNbqJH4gTsKKSrxTGCTeh8pGQGgouV/zUk1JAsYMQhvM58eHOWi5fRrkSYenlQhjvFt98f3Ry9P645'
        b'TuGltfVV2/oqE89P7Zp6Prsru8dLGzhFHTjlTuILGc9m3K3VJuepk/PedXTv9YjWOMZgI1u0Spu1mbVboO3d1oH2U6y19VPb+inttbahatvQfkd3hZeSpVygcYxtSurz'
        b'CThZ0VlxYkmbSSsbLdc4syLvbUHoPRblG/kh32F/enP6vswPnVw6otuiO+La4pReWqcQtVNIn8Cxg9fGU/APWowqpN/FXeFx0rfT92RgZ6CyVpWn8YjtSX7TJeHOzD5n'
        b'1460tjRF3sGcQRblmshQuyR8j7/zgUvC2y4JP8uxTtA/ODYpXpx/eJmkRBgb+miUsf5U45HueNoj4yiTTuJbHhsSurENMGVWCRkMAfbI+Hd8lxDfESKezrQAm26KsWaM'
        b'XPYJLv8LHHyNg29xcA8HD3AwiHOwiVCDxjcnmOe84c2NSf7OEfGfaN3pzKAMTTz/glboXQbxX1UrWSKnJU9kH7QfNtS0/h9KPg36Hff0urH/6P5/laEPsNWTvJJBjDnv'
        b'sdnmVt+bYYfyrM6k1hXdxc/mvmh7J71/nLMi4BnbZ3J7jF9Mwu7kZ2Aj4rh4xiDL19znHoUC7EsePWXj+EzGkJVnFLbyjCFWnk6e/VbBtCWoU1RD5oiV53hs5RlNrDxt'
        b'nfqtfPr4YeiJbURD0siTOPwknkEe6bOF4mzhhuaiQ0++56EGDFBMi2xGm7zb9h75S+fgdCC5c5zWPVrtHt1jrHZP1Lqnqd3TNO4ZGudMnatH5wSt5wS154QeH7VngtZz'
        b'qtpzqsYzXeOagdrrksm4TzEEWYx7LFzWILeOYR70kMLhfSP8ZIA8GaxiTTB3GaBQ8P0yBqpEm6fa3HWQyTcPGKBQcB9xTm73cZQ2XCQs3OVscEuO2N1DQzwvhzJ3ZMIW'
        b'Qb6IkSPlZlqw5SlodLYvzZHMeLVqQ7zVYTv76b862F1O+UdE9Jed6e2LfmbDg1lpBx74hj1bUaA43zv47Te1CbYTvn1l8PrL90/I/K++sW/2T/kDpiEb2S/FbL5Q4Ndk'
        b'+dYn0Xd+CeibvCyyev6b1g/Wqx9sOLLq1TDe16U2a5k1lyLeXbly3O4vyz53LskQfFx+qdq94lBq43upP3Tuebvru9z9WyI7Ra+W55jOe2P7sr2fu2+piOHUWSWZvNIg'
        b'2Ca6O/7hq65GKV988K0Z6PvCZOuGHTyT9nnXg6LsK2WbJ0g8lNB8wdcz7oqKv7Lu9wlb8uWu76SZjG+/5538OKxij+mqixeB0lniumrxAk2T5vMtK2ZeDjE+cCiE9cZg'
        b'ozQ77pfNPVa3JZ/MXnWl+auP+6Oa3zozR6JT7bH4iV2sPld1rfZWoeVEP0uRc90vD29+/m3Iow9f7Acnv/7tV8a39pnmXedELPpWBewG+2Ej4gMZMWFeGM32EjhLNug4'
        b'cBn26C9OQEeOoenCXHPiWng56HnMX9Z8cGDoCgTsACdFXmMnI+8Pg/+Lqf8fLBZe9O4YT/49tmqMWT+w/XxltbikoEAWjhZxsmMmIjL9De2YkZS53QDbyNih39KmKbxx'
        b'eat74+o2uSJcIe4c375SOaP9qW4vlazHvbuuZ0Z3/cXgZ5Pv2sA0TXjWuwLH1vBWcdv4dmNFBmK8VA6Id+ydlKN2yOmdmdebP0s9c7bGYfa79kKFTUtVr5UX9mg0hzFg'
        b'QtnwmxKa7RoSByOtjb0GKRz4+RoHDVIoGMDBYB5jkrFj06wHFPo1uJbhZezYav+AQr8GchiUidUgU8Y2DhikRsKHJERT1sRqgLwcqDWmBD5KU7VDRIPZIJdnLBi0l7GM'
        b'nVFyFD4k4cBiI1LYTFLMSHifDnFh98jLHwcSBAzjdEa/jdsxs96gVI1wqsYmrdcsjd5xtyc4J9tRz9nZJvvpb0VcdEzU1//ZLcj/Db3g+VI4+oLtSRsNJg8SOBIaoWiO'
        b'L4zBsML3LAbB3zFwwAeK09yJ1HXTBC5LClfNZcvPokfvW+okO9JNQDw/+amV33mZeMSwfZ2rFPMte29GvJ3xY6YDGIx6f3a6Fbvi/inlkdcyZ53pV0leOMyaGlzwpn2Q'
        b'ZKXNl0e+mhZ9v+7kkS8uxi+99+jlWf+uzH89+1GV17JLM9cqL2YuytO2Oc/kd2zYFPzOghMZWadSlvd/luC4/R0rfqRZoH/MmwLgWbgpzKe1aMsEx0CrbuDofaVPvDtr'
        b'K+yWrknaLXy4eJD/r+qejz2yV3UjZgRvAHbwckDqUnyqn0Yu6DONKFNwgQmVayqIACsYtHMzpwXBbpQA3AY3p6GzP2UNb7BA5xRwg7bJUtiBk6DRFBxHp+3dWHyF73KN'
        b'KAsblis/4QHtUqGkMDM92z/biOKymfB6FQ9eYBOWAhwCV+Fe2BjChfvXUoxcbNh3Am4lYLezssoDMjh1cBPFyKRgK7g+nxY7boO7/MxAD4Yt34W9dexAbIqICZueCiSy'
        b'Uy83tIzuAVflBu9N0plABbtSSYJyLlBkwtOgkwh6aZmhBdzOyoG7FpDr4bmseZngYi7RmSAaE3CXP2mqD+iBKhe4mzDCaXoWzcyWiVbwTriH1K7cdVlOHmLEtgfW6N+b'
        b'gItMcAkcmEpWcBvYNh+9vmAGGpYvrYMXl6LSj5gtrWNQDnA3C+zwA+touaYqv9J/UibBxsINodC4HGDCI9PhblIOD1yqwCBFIVLjTLQN7MI33ThuRDl5scFGtBM8LfL7'
        b'y5vA/y/3BIPZ7kd2h/ihf3+wP4yyacIB2RzwKfsRmvn3HSmObZ85X2vuis5GB+s15n7rUvvYJluz1mf1Wrsfi3mTHfgO2xz9vMd2+4Dt+wE76D225yB3nhUHraUj4UMS'
        b'DtQLKTP+umkGcik3HatSUqVjY918Hae2rqZSomNXSuW1OjaWuurY1TXoNUteK9NxilbUSuQ6dlF1daWOJa2q1XFK0aaGfsmw6hx2OFtTV6tjFZfLdKxqWYmOi3iLWgmK'
        b'LBHX6FgrpTU6jlheLJXqWOWSepQEFW8ilQ/Zteu4NXVFldJinRGNACDXmcrLpaW1BRKZrFqmM68Ry+SSAqm8Gmtb68zrqorLxdIqSUmBpL5YZ1xQIJeg2hcU6Li0NvPI'
        b'4i/HovnCP/onFI4ZA+xSTY7ZmEePHuGLbmsGo4SFl93R4T0S/p2VGO9Wz/K4CQLqWYFpgifrZ14pVuAvLg/WWRUU6P/WHxV+dtTHhTXi4gpxmUSPkiAukZTkiHiEr9IZ'
        b'FRSIKyvRXkfqjtkvnQnqT1mtfLm0tlzHrawuFlfKdWYzsS71EkkK7kuZmKkffpoQ6BPKpCXVJXWVkjhZGZM2v5FnoWCAxWAw7qGmsQcsKFPzdUbfsyutGPyBRe6UsbWW'
        b'56TmObVmaHm+ap5vb2Dcsz7QTxOY0cez6jex73WI0JhE9rIj+ymrJsFblCP52v8DxYB64Q=='
    ))))
