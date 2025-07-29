
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
        b'eJzsfQdYVFfa8L13CgMMCIgVy9gZYIZeFBvYGLqCJVhgmAKjw4BTELGLBhRRFKzYsGFvaOwxe052N9nUTbYkbEncZDdxk93NZr982U12k/89594ZZmQgJv/3P8//P88v'
        b'crmnt/e87bzvuR8wbv9E8Dsdfm2T4aFnipgypojVs3puC1PEGUTHxXpRO2sdqxcbJHXMCqlNvZgzSPWSOnYza/AxcHUsy+ilBYyvUenz1Tq/mWmFsxYoKir1DrNBUWlU'
        b'2MsNivzV9vJKi2K2yWI36MoVVVrdCm2ZQe3nV1husjnz6g1Gk8VgUxgdFp3dVGmxKbQWvUJn1tpsBpufvVKhsxq0doOCb0CvtWsVhhpdudZSZlAYTWaDTe2nGyYMaST8'
        b'DodffzIsPTzqmXq2nqsX1YvrJfXSep96Wb1vvV+9f728PqA+sL5ffVB9cH1Iff/60PoB9QPrB9UPrh9SP7Q+rH6YcTidCtm64Q1MHbNuRK107fA6poBZO6KOYZn1w9eP'
        b'WASTBsMvV4pydc455eB3KPz2Jx0Q03ktYJT+uWYZvL83g2MgbvoinxLzpw5/xjEWIkPW4n24EW8bhs7nZc/FDbgpT4mbNPPzVVJmwiwxfogvlyhZBxkh3on2jrBpcvBO'
        b'vCMH72AZP3QKPa/h0FWfRCXnGAhZslCnf5YGbRwfpZEwYjGLjqFbuMMRBkkrq0VZGg4/F6VR4W1QgYQJxNtFufgWugCFFZADdaLN6CBqxNujqqBLO6AKP3wZnUSdHLqR'
        b'gjodoyDTHHRBDlmuy1HD+IWrVjpw50r5SgfLDMK7RGjHYLwfOkvyaQbMRI1oV3SWKoL0F+8iIR8mbCw6nS5GdemFOtYNDsOcc1ZCFo1fMub7LZoxTFgwtgHgdR0HC8bS'
        b'BePogrHrOWHBtrgvGGl8YI8FG8kvWMMsKfOqBvqmKMlOkK1laOQvE0TM1XzyVhKl27CIj4yaJGPGchMgriQ7UbWSj9y9XsxEFYbCipfIZSkxzDnG7AfRsumDxf8V8uYz'
        b'fsyjCZ9zz8WGhR1izL6kD5UH2Ks+jOKFjJK431q/yDTw0RuYz/u19mPDY6o+ZL9Z9PXEDqaLccQQeNiNr+CbsFKN0XPDw/H26AwV3o7OFYZn5uBdUWqNKjOHZfBttNvS'
        b'z3cK2t3fY8b9nYOezs+45xZhyHwb/V0zyvU5oz22gLTHjMpzraRVxyACZ6fxrvUF81QLONTpy3AiBh9BTeikI5iM6W5h/wKOGYO2M2OYMfjaEhorw1tLC+ZBzahjXDkz'
        b'KyPDEUrquYMfoMO4BSo4r2GimehwfIRmD8sfhltg6CeKGRWjwpvmOwZAbBw+PrMgZy5ukqCDYQy3hh2Gm5bQPTgdn0ogAB+ZG5YFoLote244OheVQfegGp+ToM2ZWgcZ'
        b'T2o/shukDGrMYyYzk9F2tMf0n2UO1tYOic/MCl/62qhAND1o66ODplu/m7Xgv0KHsdteHBXz/vjEs0kDGi7lrNe+9sHA322pC0qoL/X3ffkP4//1+2NpAWH/NEZf2b1v'
        b'RVbHT+eOP/RO51vvBq4wLMoL+3NY4dFHm+WpA96IX9FuaN0Xl/zygNdtL90L+YUmbq3ql7MvhL/7bMt7j0r2/bg4Onzqf+LXDbz0Qd5P01ULsn4+7/3IL1/b9IvXxpk/'
        b'nHLnrwFr50w6dbtNKbGPIFPciW+sA8RwNws3ReKmHFUmQRYh+LYI108Nt5OtiI4rTJGZKtygyc6VoFNFjD+6xuEjMN2X7RQTXR1qjFQrl6MHmZECMumHN4oq0Sa0lWYI'
        b'mrUYbyr0J7PoAASwPZpjgvFdEbqEH6yzD4YM6wrxZpjy7XgX3iHC5zIZ8UQWXYsFPNbFhSutBG6U/vTPD3gQEPxq4GSjtbLWYAEiQcmPGkiHoXpqV4DVYNEbrMVWg67S'
        b'qidZbQT5MVNlbAgrY/3gZyD8BsIP+RsCf4O4UNYqddasFHVJ+cJdPsXFVoeluLjLv7hYZzZoLY6q4uIf3G8la/Uh7xLyIM1NI50LJJ3DCk7KcqyUPh1jyBKdWoH2oq1o'
        b'S2QmbsrSqND2aNj2O6MzWWYcuiYpRvVi15Yk/8TCX1s5PAyE0gOV17NFIvgVm5giCfyV6rkiH31gPWNk9WK9ZItvkYy+S/U+W2RFvvRdpveFdz+esBpFej+9P4T9IQwY'
        b'BMJyfQCE5XqW4oV+XdJ5dKpy6dQ9/gZQkE4kdIWM08eJKQhCc1XKox1RgwjQjhjQjoiiHTFFO6L1YgHtlD2JdkQ90I6YR+QDg8WT6kRBFBP/IWkUYyqYkSKx5UHKlnUR'
        b'n5S8WvpxyR59g/bPJTvKLho+Lnm1/N3SoheW4KvNsVvnHm7fF/xinvas1iw5z54v+Zl4d9Rw+Sz18B3+i1I3/nnwkHmDNw9JiWeqXg7a8K9SpZTfH5vxDW2ki/RFSpl+'
        b'6IxoCXpYu3ipnTAoaM9SdCQS7cbPuzKJGHmUyAc14Bv8FjwIm6UlCzdmAzeglKK2WkaGtnM1WnTEPoSkb8ZtUBCwFtD7S4ByU7hSbsho1Gon/Ae6scAASEoTpREzEnyY'
        b'hZ17Ft9F51C9naDCQZNDI1UZkCrZEAnI9QaHtoSPUXJuoCjytqcoZHbJiotNFpO9uJjuHTmZ/KIglvxIWTFb249fcLUzF79nJF1im8Fs7BITBq7Lp9pgtQGvZyWLY/Xl'
        b'YV9ol8C7NYA8+rk2A2lksWszdAS5bYYe7ek4N4h3gZdaAC8jJwAXR2maCICLo8AlosDFrRd5Ay6mF+ByKOl7vj9ugpWA1YjGuwoy+DWbm08oHCPHrdNwuzQYXas2fdhv'
        b'CEsB/fWQn3xSAnBW+pIxOiRSm639tCRIV240l4q31+6NVZX8tWTRS4NffeEgyxz7kWzNO18qxXbCpJRUmV0AwVRGUniYXmYn6GAqeoAfAGbfBgh1l1pVJSDdoejg5PVi'
        b'QBN3cSMFG3wHH0C7XaCBDg4l0HF3wnDaQATah/Zn5alYBh1BF7hqNg0fwmf5FeS8AgMgvjKD3WQ3VAjwQPAWU+rHytnaENfKuLLwVYnp+naJLdoKQ08Q4KzBLhCgqw/7'
        b'ltG5Vv9YoPvqe2nj/wx+6RUEIklLaCM+SIGgAtd5hwMKBBp00JRavlhsi4NCu+csdQOCilI3MPi0hNse54h5J+ZUjDi+ysgwl1bISnb8VSmimzsMePo7FBAua3hYoJCA'
        b'd66wjyZ7H4jsLB4UMkGecIcGCgrNlXSt0YUQS8JEDyRxtzZYoHC9735YcFvPBS97YsFtngsu4VeTrGuXpFprdnhZdpHbsvd3rX0IPMpda38oyPvau5rzvvnj+LUnLC5r'
        b'FP8QBMAKVXquviTXoYL36CRA1DCLhbhBpVLPzcicjxvyCngWMgO4STXL2PEDX9TmIw0udkSQuT+Yj9ufRBo++MyT8GKZbTpk6xDZ5kKZD2yDPyn5MwCM2Rgx8EZ2hDZD'
        b'awZQuZj/55IqbcPe84az2o9LXi991Ri9J1ybqT2vDdIxLw/K3FL34sFBV+0xUXq9PkMrM77/KjBfJUF7LmYAO0hIEW7Vp1NGbRBuf4JXu19AeTXUkIoPdiMeALaIPK5m'
        b'yjgKbcAV3gvxgngGoJsE2objk7SOiGwtBTV8NM8Fbegc3ksBOh1fwHsFgkTIEbqMbgNJwsemOIFD3Cufx0Ol1FFF2LtuimT2E3i5ILY2QIATPo87CuKJTTcoPgn3gIu6'
        b'yRGFRyJ3VLjgcW+IOzx6tuMhbXmiISrdutAQ28A+vbwq9gqIolzTtNxzDOVoArZtzdJmlH0KkPKz0nJjqPas4eyb3PUhg2JUegIo27TnDRcN3MvqksvaJS8temUJLsT5'
        b'2Izzw2uu93/9zR8tEv1iwKsvvMsxuYOCGv7WDqSHsCOwuvWozQUE1jwe56BOfJWur8aIL5AFxncAlFwr7DeBJuK2fim4MUqD6gFMmkCoki7jxnC4mWdkjsegzZSPGZHk'
        b'5GSGAPAd977ofeEmYMdtdquAl4iozdiD2FDATICbAruRBcnixHMB3wEArNvaE87J4Vr7Jg9c9ET1Si7XSiRsZQBhlwidAyHBr7iY13nBu7y4eKVDa+ZTeMQo0wHUlFVa'
        b'V3fJBPbIRlmgLqnRZDDrbZQLosSQYkUKirRPThzbpzzED4FMSgEZAiks48Ss8MMFyuQSuSRIRgV0/FzNaP/MHHQSn+ElCpmcK1mZ7F2eIJyVhzzBFYn1IiI/HOaKJK2M'
        b'Xnoc5Id2to4F2UJGEatvl3SWBTD26q9CZxpKTfZKEMmis6wGPf/6OIhuvcekia9CFhistY4yW5XWYdOVa80GRTwkkcF8Jc822GvtBsVsq8lmh0giXDz+CQz2i4MwQVmV'
        b'Fntlai5MsCI8TW812GwwvRb76irFfJAHrRZDeYXBokx1C9jKDGXwtGsteq/lLFo7vm81qxX5sDyVUHZBpdXyNPm8VbbCYLIYFGmWMm2pQZnqkZaa5bDWlhpqDSZducVh'
        b'KUudNV+VTToFf+cX2FUakKbUqWkWmDBDaiEQPnN02gqtXq2YY9XqoSqD2UbIoZm2a7FVV1qh5lpnG1Z7aoHdqsXHDKn5lTa7Uasrpy9mg8leqy03p+ZBDtoczLwN/tY6'
        b'3Io7A6WrSO+IJK0QOgJRakWRwwYNm906r4jtNSUuNctgsdSqFVmVVqi7qhJqs9RqaTsGoT2DYg6+b7abyhTVlZYecaUmW2qhwWwwQlq6AZjJFaTecCFK6UxTzDEA7OBT'
        b'RruNjJJMac/cijnZytRZqhytyeyeyscoUzU8nNjd05xxytTZ2hr3BAgqUwtgA0MnDe4JzjhlarrWssI55TBHJOg5ayRmBYFhVa6jAiqAqGx8iqguVpBZ46cfIjXpabkk'
        b'zWCwGgFNwGvBQs3sQtWMSlgbYfLpXjBZygHWSD3CtGdoHVV2FWkH8E2pWmhTePeYd2/xZO49BhHXYxBxPQcR520Qcfwg4roHEec+iDgvg4jrbRBxbp2N62UQcb0PIr7H'
        b'IOJ7DiLe2yDi+UHEdw8i3n0Q8V4GEd/bIOLdOhvfyyDiex9EQo9BJPQcRIK3QSTwg0joHkSC+yASvAwiobdBJLh1NqGXQST0PojEHoNI7DmIRG+DSOQHkdg9iET3QSR6'
        b'GURib4NIdOtsYi+DSPQYRPdGhP1kNRmMWh4/zrE68DFjpbUCEHOWg6A6Cx0DYGMDyEPOQJUVEDJgP4utymrQlVcBvrZAPOBiu9VgJzkgvdSgtZbCREFwpokwCwYVT+7S'
        b'HDZCUGqBYUhdiE+VW2HebDbaAMF6PI01mypMdkW4QHqVqUUw3SRfKSRayki+2fiU2WwqAxplV5gsikIt0EW3AgV0DUhKPlWxulfWTcZVRdALQBjhpLhHglAeksb1LBDX'
        b'e4E4rwXiFelWhx2Se5aj6Qm9V5jgtcLE3gsk0gI5Wp4u0zkHvgT4ExpnN9TYXS+AiVyv8e5Zba5s/EKkG4Acl7lFjEstMllgNcj603ZIUi1EEdILWNojGOcZBPSjtdmB'
        b'2llNRjuBGqO2HPoPmSx6LXTGUgpg61pxuxWfKgMg0lj0pmq1YjZPP9xDcR6heI9Qgkco0SOU5BFK9gileIQmerYe4xn07E2sZ3diPfsT69mh2EQvbIoifJ4wqzaB0VB2'
        b'M0beEgVeyVuSk33qLc2Fyryk53lvjfBd3uI9WLHex9BHem/c2ffJHNd7yx582tNkA1TpLZsHCUjqQQKSepKAJG8kIIknAUnd2DjJnQQkeSEBSb2RgCQ3VJ/UCwlI6p2O'
        b'JfcYRHLPQSR7G0QyP4jk7kEkuw8i2csgknsbRLJbZ5N7GURy74NI6TGIlJ6DSPE2iBR+ECndg0hxH0SKl0Gk9DaIFLfOpvQyiJTeBzGxxyAm9hzERG+DmMgPYmL3ICa6'
        b'D2Kil0FM7G0QE906O7GXQUzsfRCAIHvICjFehIUYr9JCjCAuxLixKTEeAkOMN4khpleRIcZdNojpTWiI8RiP0MXZVkOF3rYasEwF4G1bpbkaOInUgln5aSpKrew2q8EI'
        b'RNBCaJ7X6Djv0fHeoxO8Ryd6j07yHp3sPTrFe/TEXoYTQxD6Cgu+X2W0G2yKvPy8AoGBI8TcVmUAeZhnJruJuVusk3y7Rc0xlOL7hNI/wTaU8fEC1+AMxXmE4lPzBeWK'
        b'W+EeapfYnlFxPaNAzDEToVhrJ3yposAB1WkrDEBGtXaHjbC1/GgUFVqLA8iLoszAgymQQ29qAKVbERMh7iY9Lfadmb3U74Uoea+7Z0aqYuqeHQUw3wqB5aVTaSTpwiTz'
        b'73Fu70Qm7NZUfcWm5iplVnIGYyXaNitRkfKHH0QfaiUa8S6JrcpsslvDXOo99klVHjlnXufURlJVnohjZRzHiWMdpMZZaPtiG26KnDoUb4tC58SMLIlbjy70YhXwvbV4'
        b'RqVvl1+aTlfpsNhBaugKTIel5qUNbZXB/HgAr8Mjiu+vhs6Exa8AjoJoSBW8vAOgawKEA1mI4rVLTDgfDx3efYifX8HzM5XlFoOioNJsjs4AhGRRZdUS9Up3sBvFpS7M'
        b'KlLwxYgajSBPm8nm4CNImnuY33JziNaPZ+/5htLnqwp05WZ8H5beDCyJezA13WA2lOnJePhXQefS/R4niEepzgmh7D7hBw3CznbKbAqeJxIkv24dlSDzUU6dSHuQGfaW'
        b'nUoFQg20ObMJMtA3k8VYqVAp0qx2Z1eEGI2FlHwikmSL85Ytrke2eG/Z4ntkS/CWLaFHtkRv2RJ7ZEvyli2pR7Zkb9mSe2RL8ZYNWIy8gsJYiMjiF4awugYaGdcjEgKK'
        b'HAOgS6ciVuFQK7oVsRDJg7RTM6pWEHbdKXTzGtfuZVRkR2anznZYVlBjV4O1DPBTLcEpJD59viJhIk9ljc4sRCPsLV6AGz7JS4WpRVQaIAO3VmhJogtEvKW4QKW3YnF9'
        b'FfOeyINQH8W8J/Ig1Ucx74k8iPVRzHsiD3J9FPOeyINgH8W8J/Ig2Ucx74mk2MS+inlPpMsd0+d6e0+lBfsGlN4hJbZPUOkllRbsE1h6SaUF+wSXXlJpwT4BppdUWrBP'
        b'kOkllRbsE2h6SaUF+wSbXlJpwT4Bp5dUuuP7hBxILbDj+7oVQLpWAfG1U750lcFkM6TOBkrfjf0AHWotZi1RLdqWa8utUGuZAXJYDIQn6tY1CpSTILw0h5FoxVxIzklL'
        b'IYlg3m6CrAhPs9Ty/DA5zgNknGOyA2k06IER0dqfSH4CD/cs3I3Jn0yzmvFzNoFN8EjJoIc7RjtwJS6pilISFWV7vIoAwkgFag6kHygN4aCNlHeuIATebjDBtNhdamIN'
        b'MLp2k9G0QuuO/YuoFOhSH7uzGbzs6HaM6M4mzTbwgoXBVEqSsmHVyLmYjedseufX3FXD0G9oWWt2VKwwlDv12JQIEiJpHQ983XcyutYJ5NEHmxsOj/te2dwh1GnBhg5M'
        b'tWXn4p3RxJp5G96R5YO24ZPMgFKxHN3DbR7srtzJ7i5nPdndVmmrf6u/nmvt39qfZ3ubfPRR9ZL6gPr+RpHeXy/f4gusr9gg0QfoA7cw+n76oCauSArhYBoOoWEfCPen'
        b'4VAalkF4AA0PpGFfCA+i4cE07AfhITQ8lIb9IRxGw8NoWE56YOT0w/UjtsiKAmgv+z/x46sf2eSnV9VzQm/FeoV+FO1tID+qVr9W1khG5kOfzlKjm3z1amoRJ6GOFUFQ'
        b'1kc/Rj+Wlu2nj4Y0Sb2Mul2E0LRx+vFbfIuCIDYY+jRBHw59CoY2+uuVTU4HgsD6fkaJPkIfuUUGtYQIB/4xXbKZxPp6RsGCr6L9FG7/nNEKHsHwfj8eOZQSK3HrsRKn'
        b'ksfUCJtY3D2W8fKFS15Qyh8Tg5vH1MyYmNx0l7ImOEtZE8mD2Gw9JpYQj4mJxmMCFEqfLj+tvhpQl7XYpO/y1QECsdjJa6CWl3GKzcAB2su7ZDoH7C2LbnWXjNibmrRm'
        b'wUrD32gCpq+4AvZ1OW27SzRr/rxc2kNrCoR1MgH6/IRfasMzlXnCS8m3XlrvV+9j9BPMg2QNsjpmnW+tdK2Mmgf5UvMg2XrfRYxeRM2DxF+0wIA9Jo380/DdM9UabNQb'
        b'yzXVJmrjoDOoexTpETEJZBFthaJ7aiYJfliAb4hmSHD0EuZIa7H3qIH8C08HNGF3IimlWpFGygNC0SmoMaDCUaUAtJqs0JvKTHZbz34J3XCtivde8Mnee+A6//iOPiR+'
        b'Vx88wWGSIpv+JV2YE53tTBU6ZvPeF0KECPoH4qFWFJYDQQDgNyhsjlKzQV8G43mqWnjjEl5yhZoUWqgCwnz/FeZKIE5WtUJjV1Q4QH4pNXitRSsMvtRgX2Ug57+KcL3B'
        b'qHWY7UrqhpfS+1oI22CSYobwptARBWK469jRTfGo7K0W5xaa5IRWm2sxiddfpVURzhuxrMD3rbUgjfdWkWAxNYmKXoRNgWp4GBEQS7ihTK1IjI2JUiTHxvRajdsenqSY'
        b'TQIKGiDVGU0W2DXQR8VqgxY6FmExrCJnoNVJ6gR1bISy51R9h/GwnHdOWBoeNOlD0XSGqSqRD6+OZBwEJeShY8QvMAddzMcNGtyUFY235ROz0oxspQ96iBujclVoO96V'
        b'PTcDXcrIzcnREF+v3ei4vBI1L6L1fpopLznGxTBMfon89Jo8xkH8PNGx/BSv1eKdeFs2kFAgnkKlifiqs94tq+VMwlha6/CxvrM/5hTE003+SLeccRAy748vaqkDleA+'
        b'laFWRRC3FHRZzCShBnR8idQ2Nop6gJmJRugf46WTPmUGE8e6qE9q6IDRbnQIN3jrGsTugPGS7u1QLqDDXZrDdwzdsfqj62ij1CSZ/g1jq4V6Rlirh7/6G9+NMfKtj87c'
        b'unH32Zbbm0WyeS++0tjQPzzjJ2/mTHkWjfrsP4XXqyq3XB07d8+bWxeWf7HG9k5p9CRN1C/OFc33qWhf9ssp7/T/JjGc81vGTb5oGfn+3CnmgkcTluOumENbplkSnml7'
        b'b0+N+ei399661Pg4e8S040rl7fgqpdxO0D5+iO7nocZoN8eOfuNE+CDaZkQNeCfNU4Z3zx2OW1BjXrayeylZZiiuE9dOMVG73Bn4wlh/mE9lDtpkcBrmDkD1Ylke6rQT'
        b'1gcm7BK0lEeXDp1e61w9lhk4SuzfL4zaXq5G59DmSFV4hopjpGjnEnSIU+FTeCPf1zaYveehCmG98nEnWbIQdFmEG2Nt1D5TjU4mRaqVeHsUAxWchJ+LXDw+g0/YCW1F'
        b'mwPQTtRI3LicayQdppQyIdUi9AB14rt2wuDhLfi0ioxW4NNIN4UlZpgYvFWKTwaqV0VTTwbDVAcZU2NUxGR8W01y4ia8K5LkVNgkAfgAvk9bxneC0TaSk7B9pGVobYsK'
        b'Wkb7RXgr7iyk5sl23Bw2Ru/WNM8iMkPRbTF0eysSvBv8fqCbWbd/CjU6Jd6EzAZmrZSVskGsTHgSbzIZ9SiTcSRFytYGO6mxy28l19kRanBKtoSV+H9Zp5NHGnmkM06n'
        b'mBlM31arMr5UdyVprlK0Ei/uNY9J94nhJbOROTjC3bS1Z1ddps2s8EtNSkl/1jLLeYdQNlfJdvkXdzMOTktazmPmumSTzdqKUr12ajDU8w9Sp1t7zrSvBFQu1OYk++FA'
        b'IvSqSot5tRIaE+krdd/ZsS18x/yKXayE935ZM+ARSjg3Dbx8NZJvny/kpfmnnZB+xZ7sQx+ND3I1ruyTxfgh3fAtdlLvPjow1NWBIelam8FF8H9Yg05C30eDw10NjumV'
        b'GfgeTRv5pmXFAmvQR8uK7pZ7ZR++R8sCkMmL3biJPlof073S38FxeOmDh3MBdXLj6hmXk9v3ci1wVtfDtaBu5WmO+sjq/v4R77H0m8Xlxk+Zn+94bccf5D+SH1YxUx+K'
        b'v/wK5DFKl/BFfMHswsyD8F1Azi7EHAXom2BJdBZvQzsIYg5e4A01o7v4cF+OZz7FZA+5+yBtgJ8JtUFu2Ipm6MXSn+vFyH8RPMbD7NqIjT3gwo3Mbz0cznrUr/Tr8hH2'
        b'JG/HL7XZrQaDvUtWVWmzE564S6wz2Vd3+fB5VndJq7VUtPTXAWdeWcGLnCK7tqxLUgnQbtX5C6tBehXoXJHZZHH9XaJigMtfP5C/H8EYKCy6f4McFl0Oi+5PF11OF91/'
        b'vdxNYPydxIvAmKbX20AiIGyt3lBK9hv81wk2cAoDtdh/CpmRSjRUHNEqyh1lBjcpDWbEZgIpR8F7NBCBy2awqxV5ANM96iEbv4KcvZgqqiqtRLh0FtNpLSCxkKIg7VgN'
        b'Ort5taJ0NSnQoxJttdZk1pImKYNPLChtajJSE9Giwc4SqhSEJFJnjzqgaofNZCmjPXJVo4igixXxFDMyWxhtOVFw9Ox7j/zhdq21DNrQO3EQKa8gekEbEThsKx1kdkut'
        b'Wt0Kg92mnPT0cjwPp5MUaR5ERLGYnoQu7a0YaXmSgnoxLP5OX4Zea+G3xSRFAf2rWCxY1vWa37l9JimIVhOWisqXi90t63otSzYcSKbwVCzOs9p7z8dvScjKv9A2ohSa'
        b'gjxVfGxSkmIx0WT2WprfxyBzphWqNDMVi4XjwaWRi909NXpvvHv7EymaDyhIRe72wb0WB4QBk1kOWwO2q01nNVXZBcpF4JT4WdO9lWa2VQL8GvReFQAATiQ3oTRmep0O'
        b'XWy1YiavBaBbdHSBXVtRQXzaLKN71QfQzQCABR2oEraW3kQv9NHCtK4yAUUz1MCKCxuuZz3kX26l3cBvE7r5DfbySj1gkjJHBQAa9EW7AjYgbBoDzI7OoKgE0u61Hn5I'
        b'ZNNQ9YaNH6bJ5tYltWI2IDUnQvJai/u2I8oQAHVyXZHODAPmbyqyGbyXLBEuK6rU0Z7zByeTy+32Ktuk6OhVq1bxl1Go9YZovcVsqKmsiOZ5y2htVVW0CRa/Rl1urzCP'
        b'iXZWER0bExMfFxcbPTM2JSY2ISEmISU+ITYmMTl+4tSS4j5UD4T69XQYDMmlynPckjzDlq3MVKlzozRELjsHQt7Yghlou6Qc1+NT9NKTfugavhgvQg/hPZaJxa34HtUE'
        b'nFNJGPirqFKtMl9a4cM4kiFyEDo6NMspa83FDeSCkUzVPOLTOi+cOIkuBHEe/mSloz0+DNqDrvjivboFDnIWMBVd0+NOkGaJtOfDSNLRVnyQk+M2f3rjxTN442LcqQax'
        b'cS2+rSHOs1A5ub+EY0ai02J8N3mgg8g56DA6go/iTpCdc+bj5irP8eXjhlwotiNrfhU88rIz8V4xPl3F4O1osz8Ixs2ozUHEXgW+N8tfrczE+/AudB8d82N8Mzl8bKSM'
        b'dlWK70SjZ9Ep3KmBWlhGhPazaCM+jDbSC2XQFtyw2B83RKvRaX+8DZqOQucyQURuYBnFHIkY38H36Z00JYPQfdwZHcHiA6iN4TLYpDK0mc7uiwOk5LgiKL9cGxUwQsfQ'
        b'G6By0W60wxaA9+KbtF18Eh9mZEu4OehYpoOIu0PQFjlJD0jE2wPUeDe+mY2vReI9ImbQahG6OBt1OIjcH4g68DF/NdQB86eJgomCLoqYAfiOuB86mm565/cvcbZDkPHN'
        b'3M9Ur+f4oZggyfvJmq/e+zj38et1tz/3W3YuXTv9aphS/ZucCzEdzQMnn41WdP6z5lFs/7oBC3537bbvmMJJ4V9ZU85lPZa/cjHpmRTztq/GfBWz5Ghu3cts46ulyPgT'
        b'4/GJr5nSworm5UUWvXXozGsBTfinJ9J/c+uTt/5y4Pc35v/7HzvvrFvrmHb6N+sDTv726p3EsGvbPju2sPDKSI01cpV9tlLKX6RxPhdvdNe2sGKqbzGizfiunRweocsj'
        b'UT06gfZkedU+RMZL8C78PL7BV7cvGl/ntS5E5XIhuFvrkr6SqkxWA+Pa5q52UEnxTj+BuR0t3LCzey7qiMxVaTQ5WVG4DV/ATUqWGYjvi+PQdR3vw49b0PasqPAMtBs3'
        b'Q19YRoYucKunoec8ONPAH3oFTq8+sn5avb6Y5+Uo6zzeyTpnEDdZGTuQPt1/xPRuDxlb29/F+nbXIWgtAngO+hnGecBXRB7kyg7rEvJYSh7LyKOYPErIQ+vJkHv39vXn'
        b'6+yupNjVhNbVRICrxRJXO5SZ11Hu3p2Zf3e8OzPvbURK3y65npj2CcxSVwDPAjuDUm0F/UtuMjF0+QonujpDlz9hWIBNJPZefB9cw9T5CdiYaFqCnNg4k3D0fh48fSBw'
        b'9f0Evj6I8PXGIIGr96NcvT9w9X6Uq/enXL3fen83rn6XT99cvdZlrqfgLzB6Ct51FnFw4HMrgIDCPAFbCkyB1v1CPsI4RCnKrJWOKkgFflnbkyBVVpSaLFonixIB3EsE'
        b'pa08aSVCvsuik3TQJfv2qInIwv9fDPl/WQxx316TyELxMS7V1neIIx77kS/PRzkr8MqTLf4OO89em+P3O9+OsMWFOJ6ttVQSlY2VMq4W7+zoqkrCN5oqtOZeGN/FfVi6'
        b'gjjh3da11x4TzMT3t7SycgXpL4lRK3IE6NLSsKKydDksPAj53o8GLUQMSkmKiRV0YAQQQIYj1S3utoLttRMuxDhJMd/m0JrNdGcA4FRXmnSu3bjYzYi2T0lQQKyey0Cd'
        b'6xa7G9p+p6xGij8hr3mYc/5fIG6lG1YZygRjnP8vcv1fIHLFJ8XEpaTExMcnxCfGJyUlxnoVuci/3uUwiVc5TMEfAb85WMx8toS/KTQjUMM4iMUKugVyx80sTQ7eHqVx'
        b'iVQ9JanQKB9mA3rgm5CNO6hwgrbOi3KXo0CIGow2ydGxmY4kSF6En7dlqTNzgH2l1eKt5b3UDAJaI270RR2L0UEqWi1EFwfa8nLyhJuLSP0LgX1tAA66AQQqPxA8SIUN'
        b'+E7BEhDDDqGTvgy6gPetxJf8c/FJdJmXOh/ga3iXLRM3wdju4mN5WeTaoxgxMzhdhHdMTaYiShRqk9oicvDOcMKpqzXoUjjLjCzDBwskEj90nlY0Cp+p8ce30M55Mtyk'
        b'ygUZC4a9iWNCQFptR89OoGfTqK10JUR3n01rcLMiSoNuziPXe8aiRklNITrNd+wSurWW71eeJkoJo2wFSZgJxSdF+F4MPk3XqrS/iHnfRBi5EvPXo+MYRwgdUih+4C9l'
        b'mEJ85hmmcD46SqeaQ+34vD+ZKZjP3fhWBoibTbgF3yQiaCO6AKFsvDODyF5LhoCYcEE2B52w8zW2DCnCnfCiQZtnMxpcN52P7kQPpsUTSTwX72diN+DNVEZfUoiuk4tQ'
        b'mWi8CXUy0Xp0wPzPb7/9dmyQhKnKoRcfRn07VMrfS1uR48OUlNJrbaOatWMZxww6TVq0g0xRkyC5Z0Shh1ULyIXE0ZnzASwy8I6CcCUAR4brBmIleo5OotQSsHQkvuXg'
        b'7/pBdzUFeG98JjqYL2JYfJHBF224mVofZOPNiNyTRtdqHg85C0MJ7Mi8TBK6jPeIGVQ/3/cZvHkGvWoLFrIT7euWgOeG470FsgD1xNHusu60AdLAAHSdSsTD0EN02pap'
        b'ysuJJoCUqyGKgEWMiFHiAxJ0A3dk0j0zDm/KjlyCn+Xv0FRKGX/0kIO2ri+kd/Cm++dxoZObApgqbf/fLHp7dj+G7gfocDO+ijsFLQdvSAFQhrdF5+XMDRcqW+Ay0UB7'
        b'cCtLrrvtkONm1IkfUCVAILqP90aqNVERLCNFu7jJxdFps2hKyjT0bBaVDjlrIbrGpsAsXVGK6FXPeCs+XepWCh2riR4whl6Mm4WO+DuLoRsr2RR0aaqDCqY78Wl8LxLd'
        b'xteeGCh+gE6bJm2+L7JNBXkpMe4XS5un5OLpQVvLqn9dfXjDN3sGowFnlfOqfIYGxoyeFzVKP6/dgZPqZgbPLUhRzTn+hyXnal6/e+Ldg1/+6e3fvDv/raOByaHZOYce'
        b'Z7S8sOnR1c8OZy78nblpcI4x9J9NiX8fWz1A8/WutczjX1SfkhzcOOz4mbPrfiF33DZNmGI/N2m4pGBd+WX1Z/cKvnxLMWZOkn3/B9O/TAsb0lr4n5eCam+c6Di6Q+fT'
        b'JbYczv7vJZ3ZU/abHG++amt5yf6GdZ5Ck3vtEfu47Pms35/5mfXymfmbdjs2XXx554XTuceN+ZaWX0rLvp6xWnPgd7Vj7itufzB82nsv3zfcX33j5hcDCx9mp627deSW'
        b'5JeBa1KeGZYc/jNx56//Ml19b//EOxEfH/h6yIDfJ6ZWZ/0z8JvKwlUrf77w1vg731xPvF+Dt5fW1hW/G9/y5pQ/fjLtr1etp/EwZQC9Mitpsu5JM5DZeKPIWIQO2wli'
        b'whfR7dHelBLxs51qCcDNVC0hVeJt3VqJ7dH4SKiglYiGyvhbtDJ9stysbvotwLdGi8wDR1BtA94PIHY6MkIw4/B9xoj3cug02qqxE8Pc9Bi8O1JNkH4UgaWdHH6wQRUZ'
        b'YiewNCRLkZUdIWW4pfg62ssmA9jto3eITkC3RqEL2TlRZnSJY8RZLLqem85fPnpvOGyLRpfZhnQtZ8qYgK7gK9QkY73DRzDweNK6A7UFSgLwfhs9IMR78EOrYLiBm57p'
        b'eUDYiDZTjUxB8mQb2WDoeqKKkC8618G4WYSu4nrUyE9AmxY/S9QtTlULOo1Pc6vxnqI+7s1SBv0PaV+86WECicahWyCnuphCwihsoD+cXNDEdOtjyG12vDaGhjhiUTIC'
        b'UkNZKbUrITYmIRAmdxbLuEBqdeLHkXDtIA89R3ergvZGzmtQ9ORhIA8jeZSRB7l70WpyaVVcGg03xY3P01xt7MfXaXBVrHfVZHK1E+BqoluFswIeRR4qnLMR7iqc3oam'
        b'kwiMFzkd97zsXFLvU8/QQ1O23o8qXvzrxa7LziUN0jpmnbRWulZCFS1SqmiRrJd6u+ycVD6SeZKrC+S5uhNB9L5/ZvoaS9Rr1sVMIY3tGCWmavMgX518QjnwD2QzmVfG'
        b'2FCTLAhfWCliRIGAsY+hdsc4SJmBDg0sQHukqKkQN83PmYtv5uOb8wOSYmIYZvggEdqED6P9lIT5oXuBBWFRuKkwMQZvTwB+SraSxceHoStUoT1ZHFIgVMImoE2MJIJF'
        b'h3A77qR8xdgZuAN1osP4HDAxk5nJeUH8FevNE5bik7BVfPFGhhnPDE7CR/k73K/h/fYsdUxCXCKXXs1I17PoaB56nrZkmIgbIzNVGuH+cOfl4c0Rpq8nLhHZ/gJZ8loO'
        b'zsp7kCuKlT/XkvXXjumNhaOaI659rsi+KM82L4hcOi7oyKR33laNWL1F/0FwjfJFZvyZneuGHf5k/kuff7S2eOpvtpVulnNFJsV90dYf/WXEjcdz33xz25gJ31T8KD8U'
        b'n9hYU1305Xr/exNmf35LkbFX+Xbr1OzE3JsL3mge6jfEZ2zK1n8tfiV3yqyfxFX+xVIS3jHk6y+jv+halLe0dseGsFVll4/cUWf/Z1TlP7N+vHLw38uT9380/Ntrz+9f'
        b'LgpJORXZtCTgQHB7zPK31tZ+NHrXn9effhS8bH/InFWv/P3Db17c9Uv//LY/madpfv2Ln0fdKytP3vDRwLk3L32mDOFvQXwetfoBWtyPWnFjtA8whyfY+fjMXD7xLj6p'
        b'J+gU2JWOKAGfotNrKfYauwFfxmeBX/DAqRPwoRJqMZcJXBUgOnQ92CtWlQTkBvNq6Ru4fhxqlKPjTxgnGgFd7xeuefSJyQKu6GhuFHB5u6LReTGwJ8+LinVFlMz44Ifo'
        b'AW4kfOItRK59F49g0Ql0YBxfeifetjoySwVE0eNS61V4G08Yjm7QRc4fq1Z63ho/At2hiBy1WdOyPAwi0UEA1IHokjgMn5VQ25K0kXhvloetKsuELM9H10ToIr6HjvCU'
        b'dWs2YPvsXHR3WG8af9Qwh87JKNhot3FjHjrrZmQqZfqNEC1bg+voqFZLCrLQbnzMg7qKzLgd7aZzYkEg8Thpi3gyr8hH+9FOfsy30TXUxF91nxOEd4j4m+7RvVhaeA06'
        b'gM64rtXEV+38vZrVg2nqyNSVhI/DO/M0kvnoPKQ1c5VApx8+HdL937pA32lmw1+XT+mTvps+RRPqQ20ZqUWjmNAmjoO/PK2SA2rmf8SUYvFnCCTE2z/KXOnOHykn5gK5'
        b'gZwf0DN3Ixu+eZ5O+XRTiC4fXidt65LY7FqrvUsE+b4vUZJYK8l7hYv2WFwEiNIeMzwuscJtmZT2bGR+qejFGojv6P+AYZaIEhnxV3/soUzg/a3sTn8OQSlrFnQlVoPd'
        b'YbXQtAqFluj83VQvT6UvV6wwrLZBPVVWg40YOvI6HUFJZXMp6gUFjzc995M6fDOvGSPdKV1tN3jRQblIqdR9wtxs5PkLk3fhq4C68D60Kw+dQtuA/OwB2QxQ5DV0YS5q'
        b'kDCD0UbRmnn4PKVmxXjrStwCa6hm8Dn8rHrwOodwV/FlOaGzK6Gq9vELVXhfllotYkLRNhE6Bxi2kVLon48XjT7K0i+8yNMWj+RN3NFzBnxdKLtQJR2N95YCJjyFT8Qx'
        b'EYkS9By6k4IPqKgIPAWfwMcil6I93cIZIFJ8lxLOnFELCRmen0cJMU+F04GCEy4A7eyH7tENf1JKZDc2JQOdoCQV78NNCwr4IhxqYtEOtHEYasA3TWGj/iixAVZjXk9a'
        b'n/Oq8PmR5Ph704dvP7X/ffHejw9tP/SH8QG/eBRh/HfE61fXFCTpZ/0ua9k3fwv46dSxXc3n3t/00TrthI+2vJr5s9mzlhRmW6o0rT9+6fbVH+lf+GiSrnj58KIpv5pU'
        b'c+N4e33LT07q5uZNsf7C1n43+tvfDShqezB/zaU39h+y3p/6ekz2x8umjdkxYfyf9yqlFJvPWUKIkts5qQgdchoBTsPH6B3kuNEYgxvRxXVEKBfuBR5eaCcgEIA6FZHq'
        b'nIxpHAz4LJuFdg2jhDJk9GSQqlKm81+94Bh/A4ePo+vzKSUMQxuBFvIygz6jp7n3KdROUXpQCBG4PcnQ8AGVuA6dUkq/A2n0Yo6otRWT7db9PREeT5rFolDKmYfCX4L1'
        b'yClrCOA5N9QhFM39npaKK+Hx4RPY6WgvtopCE0q2S1yltZd7vyY9iRHupibnj+RbCVLXVeniXq9KF7DVIxHr5eyxG2ER3GHTVpM3s9kddT29Exrp+CSFxqiIIG8RCsC3'
        b'Nl7LTZCSoYY4vhKlb4S61lQVEUUbErCj1bvO2Ebu9tO7NNVaq67cVG1QK/KIYn2VyWZwYUBaBx0Aza5VGCvNgO37QGdkiVxOfi50Jst1EH+I2XEhkRmwKfIzgNvIzMlG'
        b'5woz0KVlNtwQpQbuIwM/61OFHo52gKzOlC9AN7NgC2XmqPE2wCOFxEsmem7G6LGwZcLJxS5Z+DkftA8Yso1UDsgCmWBfIj6PW9AFKu6LzCzajG/iVoob+xGTm7r0SFj2'
        b'GqYGOKPDNHrIqgGRefj+eI5h5zH40Eh81NTV/InIRlSQX18bNKUpNZCLlc/8ae7ARetPvCOqkgZO/7GE8Q3fGBESIgk5Vto4M938wc6dXXeUL4/+eVPZTypfPNw+Numt'
        b'S7VXTz67bOy78ZeS+5/87455P6soKg8OVixIDe5yjD+dp5GXSZp8C/Om3Bh07YX2Ltv7JZNNj99te2nLJysb7V+Oke3PuZf4kv+XeV1DjbPOfrQBfTonyNI25trRMfdO'
        b'PPpy7KJKx+Gzj3X+9Vsc4xa88+j8M1fmHn3+QvHEffZAZT/+Iwf3UdsgOzpFZxvAPZlFl8OqKCKxJQ0lnCb90Bna6UMunm/k1knm0g+4rEVH8G7yoaRVguONL+rgEmFG'
        b'TyaH0tLh+ehZWnwbMOtSfMovlyOaxk38518Oj7aTb7pFqTU03R9f5fC15fg+3jiB4p+C+bglKwrtzOO/DuA/nUPHQBQ7MF/Ai4loVzKpIDqPeO1I8fb1XETKOP66/sYi'
        b'dAFtqyJkQqnGu+i4+sWIyoBE7qbanAG6fuSydR6hojoz4FS0Cx2jPasdho/hQyCeRZNDBZVayQHuOyZCW1PQc7wcsgvdX0AZ7GiQ3KRoX+xkbhC6FcNrUR7gttQsdImC'
        b'KW5KlDK+oRxqz8PNtOxS3BRERBTnpOzDd9K5wcmT+Q+PXFmRjg+GuL75xLPBuEFF+7wM5nof3ylodcFEdJaLWoof9KWc+Q487YabxWTfehq7kB9fXr0io645gJSBQeXV'
        b'JSEQWxvgwp2kdK7HVwOsngi6j05yfN5upG2Hx7dPIO26gR5fEfBo2On9PBMeudZZ5JX4EgMiEf4pJfwfDn77P+FrT4zk9ZW64mLq4dMlq7JWVhms9tVP411E7OCp/QzV'
        b'wFBWmFIcOgJ+NkL/x9Vjfa6jlXzG4wNGMJyRicUc0YgxbOhYTpAovvPJBYrksNgMO1AtZ0O5YflDkwPD+DOz69WozqaBPTEDnbMFBoqYgOEcbMkzaynniK5PQdf90Vk7'
        b'RB0hKMOfHILkk8OPYXHiMbhl8P/QZ4d6eGT0PDP0yeVPgi7gzfh6AYiwacwoZpQcd1Ae8pk51iw1uhqTCEXxcyzu1K2cvZZ+ABKY1R3Zrq+6Ua0MiTuCmlWUxzSaE3Gj'
        b'JoqwRPFihkWHZaiRy0TXJpiihv9bbCOw11JU9UnJkheuNre3xG5dyep8PuDObJX7D0lNi/pT6JnQP23NLknK8vNf1Dq6X/tLZ+pit7bXte/V7GHH9n/1hYNSZvm04KK/'
        b'+yolPELoQNfxpW7PwovAJDfFB6NO/psjW1fYnLhCuljAFpPQPppYiS+EeOir0Q10RbXWztd7WKl0Cc0MG0NlZsjQSDHrWBluJ0eqNDENH5Ut5QxsTF+OJnKQhoABMRQT'
        b'8wKKRQa6Y5GxRNVKsIYYntZVrs0h7hKTAl1S3tPL22eOVpOoGhd4k7KjOGf9G4WfR+4cHf2yJt6LOyIjwzOT0XFVRlQmaormD0cVeJ8kFF3G2z3gZ4Dw1/a5+5UXkeTa'
        b'BwBKTi/a4lskMojp994Y8qW3Jq5IAmEZDfvSsBTCfjTsT8M+EJbTcAANyyAcSMP9aNgXwkE0HEzDftCaD7QWou9PvhWnj4INweoH6AdC23IhbZB+MLniQq+iaUP1YZAW'
        b'qFdDqpR6t4j1w/TDIY5cTMHWi6HESL2CXEfR6tfKtYqMolZxq4T86IcYOYgjf0Wuv3ws/xTzOdye4iff9aMO94O6/LrrebKMfnTPuB/21I853F8/9jBXFGwIMQTrxw1h'
        b'jvdvZ+pYGhrvDNEcodROkPf7kcGc+AiXcAygFoQ+dJ4keqU+AuIG6ocIV2/4FgNF0c4GLpY6YHsoxj15f94OUUq/5Cd1qcMlfarDn8KFzI9Xh/9hnYSxl/JGDv8ADEMj'
        b'587cwbw6N55j8kvU7xUn8pG5aWvZ9+f+t4SJ0aaWDV/GOAgarZkP7Gy3jzlqw9fmZnh49QKuaPRhCspkQeMraD0rpo1mylfugreS9EvWOcxHzj5SdzvT764niG2k7/uD'
        b'3hq+41rAxhi5+L3c9BLxc8dfHSGfrlPOuvuCeGaGcYX50L0Nj7/IHNqv/M2EybvHyWvbg5anJMffeqdx4o03X/lxiM/vTl115A/MqK35YuCPD67PjRvS+eGfr3SW/HTe'
        b'tLNf/+vokGcu/0rpy2sDd6Fb6BL/0S18GVg0ESMr5Oxy/JAitnx8EV0uJW7N6Ep2DmGiJnDB6IqVcn4J5fiQ+yEgxwxYig+TQ8C1+CI9WVuI7gyCuh1JXqZl3BBJ+ZT+'
        b'1HN6Fgjme3mf7chwFZ8HcgyS4HvDxJPxFX/eN7wlU8p3VDEMNVGN8g5yrtZGbCvulvN5jqGjgcJotk8luXLQRQYy7RWhk2FzeB1mdi4I7MBPagwZ5KPFMrydQ1tQ8wI7'
        b'UexYcAfeiRpXQQ12nhVvQrvyAO9vy8M71VJmYm1xFnCh+EE4j1afmuvr9ske4Y6u46Ssn0TGDqa+2YIGk60NcW2RJz5byGscuyTUdqhLTExPu+Tdh0yWyi5fk6XKYacX'
        b'ZHkX2SXW9eR9LXlsYJzM4DqPfkb3QPtve/CEXvr3tP6vkmLS6T7cT9M4YT+4t+LyvB7WfcVnDydUNdSaRTDKU3YloNh95vro0kxnl74a4dZ8T7dr9Xe2XOb093atUh/N'
        b'znE1O1zjzO60ePxerW5xej0TsCmuMPXle5zpanQgYfwVRmtlxfdrrdyzNW1NH63luFoLpa0RW9gf0Ja02F5p15r7aCjf1dCQQpLVaTHrtbX/PSfm8icpEMf0/FAfpQdD'
        b'7CL+QDbcFhWcEsITm7IIH+po88Kk5eY3ZpYypveOfiaykQ97RubUkG/DZmhb9eF/ytLKjR+XfMx83jak4MCLQzYPSXl7/l2m5Kbk8aw1StZObpfCZ1G7tFdchi5VADoj'
        b'yGwKPtgHw0klL4q46GfGnIhrAeEwa4PdEcEPdW8u6IFtrnioDXs28vhb+Pc/JOH0WK6eEo6wXOlaMRPEvB8UyGw0HxgYMoROyNmo4r23dBQ8Wb9XTeLzzayNuPmM/M0U'
        b'/kO+zfpFLxxAB9CN5nOiV29pM3KjyFcPs0XM8vvSTW/8UcnRtUrxwbf6Ijt4E2qnhOdQJE+4GxT4WXRpMtHKRKjUROzYzMXjB3hHX7JDv2Jq6WuqNRSXmit1K7o/TOdc'
        b'1iW1Q9xm2zO3x8dSJdRE1ZsYsZPx0DA0wWNRjxU+77HCvbfp2pPORSbKBOfHU0WwzKKnXGbjk5/P9Ha2Q5e5deWX7I6Vv/cBFnDaP3wHMNSgMW08voMuQNZa9ABtZ2rT'
        b'8G36affCWmADYXRrhiQya9BDfJW6BuLdOZM87h8iX+MMz1WxTALaJp0RERiZTs0h93FiJkU9gLKgq4uyGGrbt31WLveilKm5qqmY92jRfw/4hnFMJHW2LMHXnfcRuQz8'
        b'7MuIiZ8AJwvc7l5C7figHz40Ch2gaI+XuG8PIp82nIaaXGI1lalnoDMmzf5XGBtZq6hXRo97TRWCYkLF76+LnpZfr6v11cdmWDZOv/jbR0dLGpbPm7t76PK4jNzm37Zu'
        b'uXvk3f8YP6pEA3a9sbmhanDFiYa9Ww4HdjTIH6VrG4L+2DpyfMiDt9pCxq2/duB5S/LKmfHrLTlf/Orafs3Lf334p4v+stf0Y75OXzxQ9+av3zOfjrQ/iyQnH8yomvHl'
        b'v9mfXRjzn4+1Sh8e2g/PGcArGOOmuqkYGZC/FQS80Gl0zo0VxdvRVqebHD6F9lDOLh9dG+7aYXJ8wssmoxvsjJEe3QzCt/FVfw06HiHwrS4udyTqFOMr6EYWdecTxYRR'
        b'6zFMjVW3oYsgADvrlDIx6LwK35QOC53Lj6Mdb8Xbsubia26mX9xqvK2Gsqbp+OzCrFXoqEtbwOsKToZ3f5O2V6WitHiV1SR8cdSDwywmiJpjRwCHOVSw3ZKztUFuO44W'
        b'9PwSstZaZusFe3PWZs8NTuSZJT02+BmPz1H2aC5XJxb2osc5q/BlXOp+5voyrpge90hga4vp1pbQrS1eL+lN5JP02NrSXGo+BDj2Pr6AiGFyCbowkhnpi29TIZTq3LT4'
        b'LN4fOVe1QEVsKnyCOXQLXx+Bn0e3TGE//ZvEFgt5qpJ+QzROzeidH/32R1fXX2q+03Kn7s6iqK3KA6O23qk7VzexSbNj1IFN8QHMxWGyxWvHAS2mR70t6AAIR41UN4IA'
        b'OKiFRTIg7rByMWqYjLc6F6Bv3bG0mLok0GUOcl9mcyA1bfCYaZrVKad0G7PRrxlTZU8P7C3m45/IS5d5NzxMPZb5YEhvy0wb977KRGNcL4F1llI1AVlrn6dc66f4BrYk'
        b'l19SqrbbiK5lFZAV3ccyog3oPL7H5thwo+nVl3w4G1Ex/63S8ElJlvalP4X/QcOzVCWflJiMEfs+KXlcssL4qf6TEm57TFK84/rpGMfV6qunY7fFiuOrzvimsYx9rvzL'
        b'f2V1s5tPZeXh8e1qopJzW9FQ9xW1yngzFmIwOcBtYrvLPN3Sendk7WOl98CjssdKtwx2X2nvHXqshwLe1zyB39kSYW9LnnK9jd+9t53rTb8Uu6MC1cF6473xGSJGUjPU'
        b'h0WbNww1Dfj6DdZG3BRGD2//pETjWu6MgZ9o/1yi1n5c8iks+qclQdpyY7YuRMd/l/os6/PVgi7YwURpuR4Ifz06jM4J5sdsMrpW+fSfuu0KLBbu93Rbbw+Oupasd+1g'
        b't4n1KOB9sbukRq3OXmntBVmLrXt7W+VWeKzqscqNoe6r3GtnlP14q9luI1qy8l0B3QL1CsPqroDqSoeu3GClRWI9g3Fd/jpyoYqBfLM01j0Q1yXTm2z8TSjEFpd8od1O'
        b'LsE1OOzaGnpxKzkg6pIbanTlWnKtKEQpZfQcyko4Jesk8vBy3S45kXqG1kgMiGK7/Jw3npj0br7hRTSH3WQ3G7pk5KMXJHOXP3lz+lzTaHqVEq0pznqYlPEhboCllTXU'
        b'MbxLUlVeaTF0iYzami6JoUJrMneJTVCuS1Rq0im5Lp+0GTPy5ucWdoln5M2bZb1Imr7EuGkvyAKSVSWcm40MSbiQV0rNhdl6mVH2Qw5xREKVnptIx/O+s/3WAbv7GdV0'
        b'HlRW85vKkYmP2/Bz/QBuOPwQPY/PsBEzcCulmTpgpK7a7NWQjG/6o85slvHBh7hAv1EO0mV8Y4wqkhgpXgrPyFFrcubihlwL2osuReFd0ZlzM6Iyo4GTBQ7L6bqDWxbL'
        b'Z+C96Bql15PxVbwft8xl8HXoci2TU473UHYctw17Jp6YFOfGshMY1ILvhNBDKFSXCVsfoDoeeEO8NT5xKD2EqkEX8SbIzzHjlrDhDGrFu1Gzg16wcAbdje52etiFbrGM'
        b'fxGHL6N2dI8nIXtwIzoFhaFzD1Abq2Sg//XoOE1ciQ8OouanOYli6EagBF9jcUuOP53MXcaIZQOYsyDLl4w+ljKPt6zGB4tLoDKWgYmrYyOgm2J8k3p7LcYn0PkstUpN'
        b'fN1yVHh7Nos24WeZQeiUeDo+UErr/NcMxcx3uY3kcta1N9Kr+TpXo8sboE4Rg4+j02wUA6zG9UF0eSbOlkeSaz80PD/ZDzWJ0FZ8p3TJaFqb/ZmB4e0AJYyiZHJmgYSh'
        b'jjxoUzS+AtX5QD3oCKti0EG0fygdrm5dOHCm9Os9YnQdn41i0V2Ys8u0ss1R08IHif7JMDEl1vWWNIau4CgxuhGfgK4yTEAaq2bQIXRrNe0ZMEMPlxCbpxyQinxjOXQW'
        b'nYf2DiLeq21zdJbs10w4C3MXkTBzFj9O6Ppt/JBUJ2aKV7PRDGor4p2PElBHJm/XBaPMzJaiZ7kxC020pht+EkseS13OsiXLhvBjxMfwTnQwPiGJGAHjm2TO9mbnUp+k'
        b'0Ex0PYvcjdKId2ZRa6xAtEWEm/CmqehULK1y56yURWnM++TO2biOglChc/WKkVAhxyzDzWSk+1EjSIP0TtLnUfsivsrc7NhIAdZYZihqFaPt6KKWB4zL8H4fapAyEbPJ'
        b'2A4MwpfoLSv48jKrUJxfxsAqkRzvTcGd+AjtT/H8kJRfMkTNVbJ2n4+Vl1jR3UXT4uMAav3QBTK+fRWz6cTX4HrcIcAsx8zAHRJ8ncWt+BxHi2WM849PjCH34UWzcVAK'
        b'nVpGZ2xwcXJkFrGbA8g9ECg1cUOg+Yf8yC/h9uT4ZChkxbvZFOh5KL5Ge44uAQPWLEDgdnQF1VcwjHyyKCgCXeaLbsEXx0BRjsFXzewkAh97N9DT33yJPIufKCU6X4o3'
        b'ihl5kGgAOpLOL2p/2aJBwq2/FQ6jsLWOjh4dn5xArTOPkcoO4vPx/B4+W1sLvSDufVkSYjbSLtVxYXmBvFCwJ2Y1FIP9eyyMTSW32O4cT+sLR7dBqssiJwhp6A5XyU6f'
        b'jrbSSVoBgt5VKMMxG1LYyQCGawbRdowafDmLILQd5GRhOLor7c/5OnA77fO3S2rlIvZjAtLV2eYYYbO14tZpqDMmQcJoYO+mQyc4QH704PhGFKoHOSGTnHOI8G0Zfp5F'
        b'bUvQRVrbJt85Uzewg1nYusu/WCDA4Gy0BV0ktQEquDSPncGg44UzaDsxgPG2ZQFOASxWh29zy9joVbiF1qQJGcy9LCohczlsY9Qyvl/J63BdloZYv4jxwUIxi46h/biZ'
        b'Dj4mGD1wGrO2zlCjq6jTQdSTICg1BKAL2WhbYE7UvAyQgFULeNsw3JATBRiIYeaE+IQFhPJA3UpgzuXgSc5hDnC4eRbaqx3PX8xM+taoEa39DcObvtpjK3nn1rxVuA23'
        b'AHcZxdj7RYHQdpl6pgzDW/CprCeOmnLRpamVYmYcOi9xAFq8RWc2CJDPLtw4l/iliBkl2i4OYZfio+gIjxtaIodmFeImMRMtYvFBgExUB0lkJwehM/iGu68ybekwOsky'
        b'4/IkJl1/ngk9RtyUcZs/2foAlbgVMMCpav6w/DZqx22RMCs5eGeGKpOXA2PnrRQz4wslcSuG02GXzwmbVMCVE8oxeeLAmQJ4Px+8ArcBQ40eMkDP9qGH+FQIrTQSn13S'
        b'o0q0ayLHjJ8via9Gh2h5H7wX38qaS4jsAwP1g31QOox2WIVu5BYAbW4CAg8i0v417DDUii7StJXBaGPWfDIb6BzexOLTxG2jNYJSrDk+Zt4dHFD3c675YJmRqFGMn6so'
        b'4D1zTqFNqA23BRDrN6BQz4AIvhG2P8G1iWr0HNnlak3uBH8oqlHFiZkwdEhsRqfRWbo70/ApvA+3AUSgB0zMBvRgDbrLO0ffUOFNQmF8Bx/hi3NQvE1ckYPb+L19CD+P'
        b't+NGeDUxsJ23mkYNpCDwzKrlxIjR1eV+/UW4YcXyBb58sY1Z+ApVE4xkluJrI2GyW2ijE3GHgqIzAl7i3CzB1GEYuimGZppH8pi3KTQOt0mI4yFwMG3oXpCDX8DnYLff'
        b'w43AnqxgBqLTKwAs6njF3O4q1JylGo5OqTToYngm2Xf9p4tw65IZ/BxeBoTTgdvk8HqDwe0z0A18C7VSnDOspsbT0VK0Rmsehc7z+HX/EHzPFhDAMUkTWNiB+BI6oaYg'
        b'dqDQf1kcE05AzKxeM5qh2syEFXrcCKOuZPCuSZWoNYe6vg+WoYfAwWUAdA0bTS4pU9EOKsLEsDXuSKjSsnDCWPZNUf4CH2a65Xc1rwTJ+a1qx1f68WpToLPLa9HDYpP/'
        b'hkKJ7Wtgcm8H3Fv61ruWt/ODpO9P/OnOt2/k/OHZkNLqnz3/t9CukPDWdR2fLr492FeZNj/0j2/dGaU4Eqn/u3jqlRfwZ7LJPg8ndOz78azWVz+a+MHLh2PT9i/64r+O'
        b'/+TuyOvJJ9rjThcuHhrZ3/7gwOjlP8/48fI3R3z1qU2p+vHPzo8/uqEg9tpfH88MWN+mCPhMaXvlXy8YLvzx160/P/PiXtnB3DPBb8x8sfNXLbe3J+esfC3icqrvrD8p'
        b'AiYsnvmnUYuPJMx6Lq0od/TuvzQPz63e/unmT6uvz9FXtn8+dbfkpfUTfGYGpielTh5rvf3mo+DdJ7dO+unMnTNyUyYqrefzP7rx0sHNhwdM9Jn4tw83vzTrpXETGkfv'
        b'H7XwYtlHA8Yt/2DX32N+fLohe/XhnG+ujPrglVPa7N/+s31MZuR98y8XfXvq1YXln99IbQo78nj1thFvVu1beD1sS2HwrSU5M6ek3786ZNX5q0P1yjfOfrH2xRWrZ79W'
        b'ovvn8uo3Tn56VGTpGLf217rXfn2qa+GyXPuGuis/HdrW/J+O+Rfe932v+fWFnZ05+v/esLKtcvulHLkj/flxZRZd4Cp93Kj3BtxJDn5+2uNxRz7wedf4+Yxzn53Nf3Tt'
        b'w2kv/23Shx2j37Ce+4dttyP13V81F2f8O+69+83F/7kV4Fiv+nz8tH8s+MOqf/9++TfvW6duX4fOBdb+59/jZj437+NXOixjftV46tzbJUUdP/tyQ4TqP41bViv5g//S'
        b'1aOfvAmdGAekTOHNAyQLqeAdBZRnWyRRngPW28GhQ2zO3LHUPCEplPj1AoqPkgKZumecydI73g/zt9EfBe75PGrsVyW34huB+DRq6lcd4CtlQtExUaWed7fCgM/F/ujc'
        b'aHQ3KsOp4A3Gd0XA03QkUaXsTGIs220lim/lUH+py+t4F7O9+LmpqDFaMBWV4ZOcA51Djeh+AC09qXAGVQ8TlAw0LofDQJ/1YfgiHRq+uRbVw34Cnuqaiqtm04h6npYL'
        b'G4Ced5mUVaJmYlWmoia1A3lSe6WWOjtzjJhbQXzz/NBtarmK9lRXucw18J5qYrERjE7yo72ebfWw2BDjy7yWHBB4HZ21gUAk70OPA4jpneZJO4vBS2gm88j1ZFDb0QEh'
        b'j5uVBdqNrlDF+Bh8bCYx6iBHFSqSF13MJhbGwlRETiROKvfwQV49uh91gCjhVI+uRMddGal+NHYwNRd2aFHdk34SNXh/Jch6O+hyPBOaLRh3OE075gMC3gLNH/V2K/33'
        b'tvnsEmn1vOqGmJ26VDcbGDUx0hWzIdTwzo8a74Y4f7gQtscPxA31CWLHEt9o4OL86K+clXFDWQUbSEsEsYE0ZxDNHcSGktq52oBunQz0xcMOmCjbvq/PGceX6lbnX4bH'
        b'eaIXIjvMpRfayLwz1MMq2KMX3k/OqcqP/xATUy9xqfxYqq14ykvAScUK5kltxQReW7Enmzo058dyJdmzCzQMrwckhCxLg1tQC0BYFcOMYEZwKQ6iLB8XNBq1MImwv4Yw'
        b'Q8bgg7zK4MCa8Hgx3oq3MkwcExeDGmjdtwb7kpvxFGJDSZTMmMbQ8zpdHI1MqTaVmD8ZZOJ5VN+Kdew/OSa8I0WbWr5hKi99DQFJ9VY8ESoujgDZktGVL6WtDcWN6+IT'
        b'gAW7aAbizBj6R9M6mlT00F92J6rEHCcz8BW3LA4mY89Yu7ZEfi5lKd+FmxVBJLImsqYk29/fX7BamxhAvl4Ss3heSTabYOBzRpbKSeR036KSqPdnjeFzrq32Z4DDyXg9'
        b'uCR7YO5YPufQ1TRy0fChJeaihev4yEv5tEsxkgkl5h8F5vGqIA1qnGiVUF5xProkZiTVLLqrDKFMUzC6HbEIX4yPiREz7Fhyl+q+QbTNaf3HMDOBg/+cKyld6RvNKwbE'
        b'+FnUCawBPoGOE/agNhW18SzLfXRyKG7z80GdxMsN/ttAICJYrxYkzsu4TToKN5HbiMiFRC3oHp3W1fjYaNzCJkI2FbCzjWgTbfnRSOrbHrRrdom5NamaoaxfvzQQ+VsA'
        b'cZOfW/MkDIufZdDNuSt4cDgYjJpQC4sPw5YYzgyX+vCS7LmBw9Bx4jjreXQKjNgOOp7BILq11BTQoyMWxOAQdDOKAh2+PALvjfQZKKX+LeF5fCu3ULsOXWBw5zToPLN6'
        b'VARvQ33YFoEugBiE7zLMGmbNgDn08JauR+BAOpbpfukl5kXDjbzy+E8b4nTMzTpqfbBZY5osHim2JcCeMVd9WbE7lVyY8mxZ9Qf3D9f/wxrzKMBn+i/eHKVujvz3vLEd'
        b'15bMMIy682pw9ZoX2fDgjoYU9g9BO36dezXotdeHTvz3e3+9X2193fGT929mis6O++Ok8WOG/iy8POF935+vxDXlRbP9/+viiT/M7/+Xm7l/+7lmxJuv7V3zy83HlG8/'
        b'W/nu450zvxh7/uGut1YufGf6O1dLm0Yv/Em6qP3k0C+G710y+NtzX6mXvfFfsdcOr53+l38tuJ/242kr/u3/9oeL7e/+MWjTJ/P+7Dvq1cOHJp7+4P2FY35reKeqtulf'
        b'z7aEDXthxodfvf33jPU7qxb9r/auPK6pY/vfLOxboCCKUiOisgsoCG4VBBXZVLSIWDGQANGwmBBwqSsobgha3HABFVDRuuC+v87U91rt/vpaTat2f772dX92se3rb87M'
        b'TUhCkmJff5/f749nZJKb3DtzZu7cmXNmzvd8//XdE1g40THb5WbhxoKbT55Mkw2ee7OtaN3hJz9Ov+U9RP1KzZpOX6+Hq7IO/7L+1Kocn2k+Y64vGuMRkRa18t2xF8as'
        b'+nLykgunPHfGH3u3MunOGwPDD596KPg0prpo9pzg3rzXDG5ztuWKkWqfgvagbQvRKgZCabf3Q8e96XZ/RngIzDpnhGgbOupDdZQFqDlIrz4Mma1HWx/WMK/ymtG4Yxgx'
        b'2qnLIu986YP38bO1OAom0HSwNiGycFpekoDzShChY+5oO/Mtb3hqFkRt2gBbzwLOvhgfWCYMCEN7KsAgzkbbiaAWFCx8KJZpWKj1SSrHsL5khiQyhPqilbDWcEyAWnAr'
        b'usA2rXeiK0u7/EzG49PgakJq2EDFROsGoctdzEGwbMnh47i510xxX+8AOm0PmlGspwWiYqSVqUlFBonQ0QhfVo/2Yryzy8kUN+ITRG0h9h1VN55CB/BB1kR6hQStGqHX'
        b'STyyaRlk3l9CFKbT6LIZmj8U1TA567OJUWvIhagsgxz0SktJPFMZa9BqtI8oEJPCIiJggRrXuxNB8WERmU30qooM78KHu3urot0xvuCt2oJaaZOG4mt+9KxNqahTZUfU'
        b'NAHa2xevpU3qhdtUeAXelWq605+EdlTASkoivjTFzKmgINjMrcC+H95vR3We+fg86shDK0y1UNKa5/tTsiNPdK2QV8QqcDVdWO6mh20laifk5b+YVKgWHH5NlChUUzyA'
        b'AcHw2UWZRUaBe4Sozbevfve4R/tgYvC4oyrUXFMVSu0qEAv1QH1vqkB5k1cv8upNXnDsTkH73vQML/4PXvoANK5CZ4FUCHumrkJHiqZa7N6lqEDBVtzTbECmjL3VjpPk'
        b'Cwu6UaPJrplZkSQHEctoI33LoP/Vz8CBrzkbKXjfqishoR651FUXvHR1jnrfTf0n2FaiXo8MGgWuO9QVg27U0z1cusWnc82bkjAtIT1ves6U5CydSKOo0IkBV69z4X/I'
        b'Sp6eRbU+Wj3WQP95pAY1kJ+FQVtBHRxFEs8e4aHs3MXubu723o4SB31MBnt6e+1NXs4idtvZkdDsV/1LYucu8Bb1TqIzeEwOMU2MhnU7tMmOk0wXzUKnS0x2mPVsJzTy'
        b'mAkpq7jRg5KWeujf5ULDJ1GdgzyQ6LqAevAoFMsd5I4GilYnuTPFqrjyFK1u9NidHgNFqwc9ltBjR0rh6kwpXF15itbH6LE3PXamFK7OlMLVlado9aXHvemxa6O4kAOp'
        b'5H12CxvtAY0yz03u14drcQfcBn/cV3/sS/62CzcJ5IN4pLUDDUTkUutRKyl0okSvlH6V/OZEyVTFFOfiOEsCrSEfUCeoZTq+a60b0fAD5AMp0aqnvB91rRzME62mZiQ/'
        b'3GYCTp6uZwAlPzGWVWkQUGkAO5KsVA59XGlO1GhyEDIdMNI8HRL5VJavKVMBgTNAuyEGLqOchBi8ivIKFgaa4rzNQhMb87maMbMGO+iceI4voMfhP9LtYEcWrBOIcuSF'
        b'lTrR/FLyXYlCrtSWkO8cy0l9qsrUcnUX82s3ylXTIFD6mNtOxFpy5nd5XQxBoH6LdLUoWPz+1z0mXYUm/92kq7/NudqNX9Ui2P13cq4a3QSDHBC124YU5GdrMpRKZary'
        b'Ylm4JVHipQXFpMgCGhvbNgWsbQZYC2yvj9Aiv8kAS/ofCyOcNOFJqUqWDxzk5KNxZObgCLOYx4zOzKIUpqLTtg2KNmoKC8LzgpBn4Df4Z61xzVqOhmCNf7aHXLMWM+3i'
        b'n/0PuGb1zzlrdnYkVcr5Gzbst26YfnDgY0fzR1K1okipIS1MhioyotHuFCbV8rdNWwoxnB+Z0tWDLZSMUtNFgzipeGHarYEunJZitqMmWaA3rcTHgNNVr8ub0LmuHucq'
        b'CWC0q2v6+cDmgbRhSMno7AWxnHYMVdT3oUNWSGL5DCkJij7P0f6Qa3O5K26d78P2IoPomkXQn5SVrsFzcjktgMLxOaKfVltjiW1EHQa7wlhadB6tdUH7ho+hGc8rYPQl'
        b'LYFPh8nlmRwNh4ubyLWbLWacEoovK7OMs1uB653Q1oGomebnUUFXgiLfG7XY9eXFExlJbgraSuwmi5Sx6agT1RsMOTM5z7qgAxpPmu+Nhc6wFOMomVOUpvLL4agXTSE6'
        b'iE9YyheciDneVjHJ8yI64oLXLgtSLvjIX6QBvfPVuSnhL11yEya4Jk9d8u85QdWJ92Uu0pMNlS9KfCLFESK/Fu95H9TF7NN+cSp828aRVbEXGnye8d/+TfidTI+3Xvvx'
        b'xdiw8++/5TgKb3nnVu2F+rtJw/vU7Q+++3zVQ8noS0ULV1977+UxeP3yjm+zHnhtd74x9Mb1m7FPxFQdfcD9+lw9Pifbf3pL/d9m/2q3Lk72yY/BzhStF4GaIWwm3hpi'
        b'YjyC4YguoC3MCK4XRbvgs2iDKdCQrlmv1lBPbdwUmWCwP0ejWr6X2XH98Q5w1G4ktg3det2Hm83sULBCUQc6D8HaTmczU3QvrnbmUeDEEjpAkeDDEogtTH9dgRpEYESC'
        b'd1Go3lR2QbvYUsBlvFfAjD50ujiVN/rwQdxKBSXVbSfdwMSkB4Oe9O1NxKgnPXk3s1RXLIGoQQYrlJqg6GgKWKFnplBn9kkzwpkuG45P4bMaukRBjtKoZhsdEW7PpaMa'
        b'B7Qnesofps8b8IugIxmZbcu5RMokK7DvYpVlDLM0BqjhSE/cSpQPKxyzFyC5CMklSC5DcgWSq5AA3dNverU69iQTN5M6BZNRUwN3z8ieW8HdNgmr1l3yniP9DGqTDXTa'
        b'DCIDwzx2lWRENgtf2SSb7RnssVjPA2qkQ9kQaqZeqIePm0lAdYJHJyB1ytNrSzZKzTWU2p+V+vtJbvlbIM4jGpKNEucYSuzLSjTSox6dWlacR9QgG6XJDKUFdalKMnNU'
        b'6aPR6Bbq21evmNgoX24o3w9WKYy0l991R/Xai40Si0xKJO1r0HiM+7CQgZHpgofBFzajQMQLAr7k8LRSZ1jw26ebShCMQcibrM40bq5roavBs9zOqmc5bzI9sPPqMUGR'
        b'AugYe8pPRE9+FHoiYzqiblkCPZEBLxwSJg0xhi2TY4qDJicZk6tQDZaJAZwVPbfyDAWNlGaVlYCtwExsiGTGY49l+WXaCp71R0O0UmttA/+AYUMBTSJXFlL+lQpe6zat'
        b'FN/eNEAjabYiPk6bBYUX/qUY+IJktgy4qFgjs0UapCclsW7AGLcrU867PZjSoIR8taKguBT4UHhrjkZrsyhoVz/QaJRFpbQrMNaRbtRXGqnSuFZKYtgUWaE20RssUfQm'
        b'x8Yb7BYoKSo4DBZF9Iy5cIaBMrfAmqlFe6WSXg8MTNB2cfE9Z3AqNK0Q1Fqp0Pxx/EtBwDdEmZKCpSEhJWBMk+osCgn53YxM0iDKvhTOSIweJWsb7Es9uv5RuZCkVjic'
        b'rHEhRfRMDBNkhk1GpCADI1JUsDQ3Kto6o5ExuoO/jVoFq46ylApKacyT0tNzcqBmlgK2wr9y2aISGu5VoYaJKYzSnRlsYCOBom0LZJOmyXRFhD0tQ/VPikWxmNpjTO5E'
        b'ih8WaZ2nyxgLo18fMnpMyLfkiSzVKJlQZYWWaa/k80jPoO0BF9CYt7KF8LmHjD/wL8EkEw1dGlMWFFcoKa2Tpot0rPszazXPcGkUcCcrtGRwNWRAerBSyjcRGaFKyBOX'
        b'PCN8uqwiXwHLjZZJqMKlpLuw0Jwqbcl8RbHl9g+XDjM7jZYm0xYu1lYoyMwB8Y6lT5apNVQoK3kMHylN0BYWK/K18OiRCxK0FWUwv823ckHMSGlKqVxZqSSdWaUiFzBq'
        b'NI1Zza1cHWtJ5EdvoBGWslEaiVXyaGLFWcrv0dolnjZkV9P/Rstb/HI668mwLmgm9yP3ROPqF6pJbYKgbQ0yyfIXa4uCrXc/48ulIwZZ74AmJ0bFWzuTdLPSod1ZJ9mP'
        b'MebZxFrLJtZWNqRTGOpnI48449OsVi3eJDML9bI6ofFYPTLC8Z+oPkB0UjK26ofyoCw2x1qdsLuggMB9TqZCdkR0nKBUcqgoJX+km0thDoqzQZ9uABGaZhNtlk20zWwo'
        b'3tCEmi+I8vElwXwTY/UyAz6RXZo8g47U8IU0iDzkfBcnt916M2jVQFEI/O/8pzCpkW6XPGOaNCgbtxaryUNKZBluXRQjaGRXZoaveaH0WWnma9Wa7kLZUvesqZdUley5'
        b'5mdQ0RJMlvh7psNQEOdIaQa8SXOjI5/q+WXR7LJoepn1u6FHh/IqJH8MxrKtfkCho+QSeCMndj/P+ig2SaFWlw6doJZpSaKKGDpBSbQ766MWPd36WAX5WB+foADrA5St'
        b'ksmolFxMlDAy9lsfmqhsRGeTWxbDWuMRLVahqADNAt6JghVrU7/LL1s4Ugr7xkR/KgStlXxB2tz6TYWLALnLrpKppHBg84oCZQU8kCS1qe4xwDKcyT7QjMNATw8fFhUb'
        b'S3qadZkAKUwEgjebPbJQRmo7gQwqtk6iWGNyh+BNmhtr/UR+mNOzj9ro0XoU9EhpIvnENOHc6BE2zzc82vQS0y08m+2tx1bzV7L7Y32wBkw1UdESEzLI7bE+IuYrC0iG'
        b'KeNJ0RaeSBN0dPcw6TyB0pB8RqAUWRidPHtJAYsaopU6p+JWfMgUyYa2zsuk1+x1ZvRKkb0+y/dwmM3DT7fj6iEUXof35nBiCq/bPJCe/9NMXy6M4ySRcyYG2ttP57Gl'
        b'5/HZJegMvsTj7iJwE75EkUNTp+HNFPOG6tBVVjyFLydi5sb8rIo6J8884VbnsTRGzkJXoiYX1BRKTgbSvUzwCERHJ6dDlCLchg+mTOfwSbRhGrdwuFMRblxA8T3VT2cK'
        b'G7QbeMJBbvg2jhIo9sos4Pel1qBdRmGJYActLGX6JLofEW4clwjXoZ2uwWgzalMm17jbad4nueTfvbx6U/pk0VRJzZGHL1/+cd38lO+OrZr4gtO7zhO+f1nap/dH8bte'
        b'2OjisO+U095xXl+pPoh6+tX4FbvaD3f8++LGzDmLWtanfIb3fL3o8Bfjvh3c9OzcB4Hv/3n31m2vrk/8tirnffGDogx10hsjdtzxn1iRPevn1xNbY2ZNaBr14qLvbtxV'
        b'xnxdJ9q4Lab02GsfjTtSmZNb0z/0jdipnz2Jsps/Cxj0fWr1jPSXlraXRUWVV4df1K65e077w+AJA+ZEqKImXbzVvm3qkq1LRrds0CyPv3d9TfJjlx5/Men8Xqf+rp/9'
        b'2md97vT6a19fmPjFL58FO7L9oVbAEbcKTGIFh6MjuJ7FcMfbyV2kqA50Aq/gOZcac6jnXUX08pFw09ZlpqCjYs5eJQx4DLexqJdNo/EJhutArXijySYZbvCoAKJKVN23'
        b'yNqO0bYpcJP0W0aoegrNVStY5mKIfeQTZhr96OlU6jBZCSHmKNmdgekOH8b1PNvdpHDK2BeJ9uArqWkpAk44DbegDYKQOeXdwRiuf1BQbnBko9tUsCFrsk21nMt0pIR1'
        b'YoG7IJCGQoLP4CnozG9RCamfoR957yXwEix2NWzGyOTyDJMAHF2L1eCGbbQv5fRIggeLjTLpisZpqMk8i5tTOwKMN6dMpLSMxKBhlcC7iKsVG8Iq/Zfzp9voD7ekO33e'
        b'IDb6B88mI7mqUwDctW87BbCRPDCCPABaQBLXiTnyYAhmKJY6iRgQBYLXO0jRVRdyNN4um8v2d2L44OPorE8Wu0SAL3H4lByfrgqlheQGPi34oXK5iIuULcmz5+MekKes'
        b'E9cPG26P6hM5ChvpjeoYH97aTNwxbLh4Fr7KUZgJ2pVK8wnPB/TGtw6cdK7Kz0vCwB+3Ezw5abG9PVc+V+UeFM1wBbsGky8nveEAX8YNSWVnLi9w5XrHjRdwU+aqXps8'
        b'mJ1ZLXbjegd9AV+G9Qvry870GeLMeZfHO3CSuWnfzIlgZ87rTb5MkgC4NO29aW7sy7NJRKSK14REpLQtEQEMBuLgh3ZkTZkyheMESZxqMVqJ9wnYFHns8cXDIoFVUIBb'
        b'uShPvBK34820OSbjq7OzppDOmo43C1E7R37aOJ8FldhXjJ8xQafgBnwAXcwoYzDaXUPRSopPQTtQM8OoHEX1FDGUjI4Gwy7XRNQ2gBsgwiwACb6IVuG1w8R0835/NBeN'
        b'aiMpvqc/GdR24mfI0xaPNodz4bhmMp2PM9F2VK9HlzBoiSc+i85o0B6aYSA+kpw1RQpw5lM+9kOfQvvSk6nok3A1YINN0CXo2QGTs5cxCAi0tTDakZOULxVyc+emOaRH'
        b'smY9nE++9PYE+L4q21PKekwQye1UFjSrFz7C4WpOJke1NI/L6d5ckLwaenG/9j59GCQGN0BIlKwpqCWY40YudcHr0SG8Lxd3smbbNw6v1rgNI+0mREe4gFJ8BV1DW5XV'
        b'Bzg7TRxpgg+nfVmymafnfavS6+9PRC2Y9IOL9+5VW9ZvEzo5Oe0bklPzZye36xc7G2Z/4nhpxHqJQ8snjtNf0j23f21YzrJ7x/7+8uVF7Ru9bizEZd+vnrVFlvr26fdr'
        b'd6X5tM545fj2IzOvBhV91RidGXrgaHHQ59crkpvqHF794SvPuP1/ix73YfKz/V9Pa34tZOansZJPbgz3nHVw1uCkd6JHtlTFDBxQMuCpAVf8v569dffq71a7//v1jJQ2'
        b'9zU+z0bO/eVs77b+vd9+6DL1YXjH/MVxJ2Z/2z+pb8bS13/5VPxM518EDxX1r0QdKqx3euz5HTc0Mxeqi4KCJbd+/GLgDlnNouhzqglxnaqdSp97npvqjicrjg5658HB'
        b'm6n/9r8ZOOSDylnpq06NuX3+lYCwG6/0Qh+GfHznp9HKXxYpb29SfZwYm3jOe/C1N9WViueGBHtXQCRLtBJdw1utzM69QLPsmp1xM9pFlYVZJbgtlM755DdHfEmYi9ah'
        b'zb2SqbLwdDy+QJS7NAEnHiDANaiDXHikhEFOzvpONiaeFeK6/EXZuIEpKAcTSXHGlChjktFJot3WMpRmTUwgC7CAjoaYhvOWJts5RaLjjPv3HMlkG8WTMA8ZH7wWtaC9'
        b'EgYnaUHnAObK40nQvggautQVn6TOL47ZEH87M20BPmTmE4T34r1Myn34ImMr53EvaKfQfpkwYPkERtvYgtvndvfzESXGkId9P2MYlvQfpIfPUiVrO3A/4HYa19wXnX8s'
        b'1QT86i4gMlWLEkejUwz0uwatrDLBofYfC1CTElzHHHhWAR94qjE41h21li8VJRHFuonWwd/XzdzDR7RgMH5m6eNUvsmjPHnwCHMiqkar0N5UF3ppP1SfZAocQfvQrrJ5'
        b'+Dytvj9qndbdx0iEm0vRMbx/CNXbfAMG8R5T8XiPwS9P7zGV42k1Zpxt3WuBXvcq7a57lYOuxVOOCSVC5vAv4WGygPGQEN0LNC8J0cW6aBgl/B9z9wdeC3uhmMd+SHjH'
        b'f3A64rnFqBZkm77MctW6EZmB4tXPXPFawe01jXdoXijJBwh2/mA+s5r/8pl1U9Us85k5MHpG5xmxlGELHULtppxmxoxmuAm10elvON6Jmnh6MnwNneEpysShVIUrHCkP'
        b'dcjPovDN2bxeMKLIPzSTKCtXeHoy1IQalfO2Bok1J8ivle8uB34yFClJKnrbXbJs/3vc2i1bRFMWCMZNDmrRrAxqEHoH/3PN8NyEVOU971Gb79+dV3R37UX0zP1x9W2B'
        b'nzz//dag4yMXzxvvdmVSdLNd3NrvrnD3RvS7dub5Y1NXTYjv8O21THLi+qJl+X/JyPnmguKI8LGO/UmXa52eE9Tkvl5ap7tT9a7fkIA3d12T3elT885HSac//tOEET/v'
        b'jC850zxhvqox8pasfmBH2Qeib256CC+PaLh/LdiDOTdujELHaLvhC+gkz05GxtgLdNCbjlYNJgMy0ZyOMJIynqFsJq5mV9fiE/hAFwdZBtqNzgv79bajgyo6KkPNZhxk'
        b'aCfaJsSXi+xp/rm5MWYEZ0NUQnSACHOaDnvFZSNNKMpQS4oQ78A15GdKFLbGCxjQ9Bxly4idKQxR4rP02scnppER0wG3mFKUDcKNbMI6ROzmtV0kZXNQu5dwYA5qpYKF'
        b'4hNVoUMT0HYzijJ8nM2oo4Cwt4uibDRqVwp9cVsSzTosFx8FhrLNei49ylD2NLpG5RqLO9EFI4qyRLQeHxH2XoC30JylqM5AUJYyVo8d3a9lFd6IO1CLgaMMHZKNFYYt'
        b'Rtf+EI4yyqpFh/KQ7kP5ci48wDZNGYyIfzhNWX+xPrTxCrPXhxYIy/QikMJNMTgMjCekbxnBXuYAPC3HGaPweuBOCoyEOjtlhaJEw2B0ZrRknv/RykYP7tU5kgwQ8Use'
        b'jvZiIZlWhb2Ces5CBnext0Ba5TWKmiLj+qJmSj2WOodqo3acm5+Q2DRNlcGCDOXNn8QCTV8yG+X1ejx50wWGMX+78oOBtZ//sFbz3mhnf49xCfen/dzZENDGjZjUKhtY'
        b'93LWsPlHW0oqr/5Y/6PTE5lP3bWbkLBnT/2BX8ZnB54a9tKDe65vdx5bU2T/VGrVncCBaamrfi3eef+VV346PKPhpQH3yx4kbj8T8NPF8Uc8/RT/CH0KfbjjNYfR76/1'
        b'vfzRjqw5C/5s9+WF0oCkHXd+vrsk4PYQpPnOz0MTVjq214S8lFiPOuR1suGHDRv/emTzoEmr20QHSkMbWyd+3bg0ZZdHyYu3tn/bFHr3q01j7o7o8+QLz+/qU/LmjAFf'
        b'Fto98Bu1KfDcuEUui7O/Of3Rz/d2a148dn7g0anrLkVfrFoz5537G/e8eCg8qWTU9edqBz9nn/u1qnaC2+L29z73TbpeGOmqDhbR8C7JC4bgDWkCdBp3cII4oCM/gnfS'
        b'4TDe288kEAta1593at+E1lLwNj5HTIJGWIEjQ9xlSxHIC1FH92W0vv87ne2REzLUiPQPm8WEYoEd8/JUZTJ5Xh4daiBqDOcnFAoFwwVSMrTYC7yEjn5Sb78Q7ye8h4yG'
        b'gWeMo8jdZfByrlL9V8PzJdIJ8/KMxhW//we1F6jfNDyeICk8Viza7/1xxvxpLAZR5Ey0AdVnkRmmHq/LTCOGXL0D595H5I/O2il1nnc5DQB73f+03H9dPNEqvO1+/f4L'
        b'ybhJqvXj8uO9sk8kFlQ1ptT+64dzjiMGnW/qk/5B0s4JfsUfbH/4zQuizJGHb/tkPcwbePWNyTsOnwq92zHn0Nhnxq/LT5Vkv/NJe1jS1ifPn715s9MLi4XjEwailgQX'
        b'l9qY2Fv5tWPc4/ZX/8WpSDy7/Lrb91dTx66ukvzyusf6V/s7ZgXddh1MlAYpSP8s2orbYOLNhJ0EIDd28UFnUKcQHyIV2sQMovOK+NTMcHwSzhqPV8EU7YkvA3PTFryD'
        b'PhHe+OBoaIW+03E9GCNgApNG8BI9rsLnqE1EbKc6tDIVdw5NSQ9Jd+DIQOfohTpYIKVLaL0/3jCU6As19pwgi8MHAssrYF2nb2VW6OSqBDtOkMoRdaEzh8FKzqFmdJIS'
        b'75GyAObuUolXB0PkjZWomU776FyAr8boBGeiIxxIEaITkipGfLq2EjWmpkSg/WC1MzvQHa8XZZD2OEGFch+A16SmxOO9NIwibPKU4hpGyNqCtrhQdXMSr0q5zrN/TIhP'
        b'o6ODWeY1aEUiseLWh5XzJzjjHYvRKSE6ndeXtntx5DDye6crWluaW7VAi08tcF2gFXC+uF6ENgYQvYeGQ0I1aE0qDU0BNeE4F+/lqEmI94+Po4OMnGgfu6DVh6aSoWUT'
        b'LODDkQPXNxBvrxKjalyHdpsElPb/v3+4zJ81p98YaSwMPF1gFsrA6ubIgi9RCxNsUlfRWHOVJ5ApBXTE6a8TqRSlOjF4VuvsKrTlKoVOrFJqKnRiMAJ14rJy8rNIU6HW'
        b'2dElZ504v6xMpRMpSyt0doVkyCNvanDEABqVcm2FTlRQrNaJytRynT0xhyoU5KBEVq4TEUtLZyfTFCiVOlGxYiE5hWTvrNTo0bs6+3JtvkpZoHNgMGeNzkVTrCysyFOo'
        b'1WVqnRux7DSKPKWmDHxFdW7a0oJimbJUIc9TLCzQOeXlaRRE+rw8nT3zrewaRVlF/dVfwed/QgJkdeo7kLwLyQeQ3IbkI0juQXIfEtjQU9+F5FNI/gbJLUg+huQfkOgg'
        b'AeZU9ReQfAbJe5B8Dsk7kLwNyVuQfAnJ15B8YnL7nA1D6g9JRkMq/e2hYyE4UBcUR+gkeXn8Z36qeejHHxODt2C+rEjBg8VlcoU8I9iRKoBAVEvMW56olqqIOmfS4uoK'
        b'DRjEOntVWYFMpdG5TgNfzhJFMrS2+lt9u5mhIHSOo0vK5FqVYiygGOiqglhIBi/zLjbCmy5y/A/vTc/v'
    ))))
