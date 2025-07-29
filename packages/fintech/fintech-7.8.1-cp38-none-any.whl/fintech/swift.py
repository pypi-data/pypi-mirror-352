
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
SWIFT module of the Python Fintech package.

This module defines functions to parse SWIFT messages.
"""

__all__ = ['parse_mt940', 'SWIFTParserError']

def parse_mt940(data):
    """
    Parses a SWIFT message of type MT940 or MT942.

    It returns a list of bank account statements which are represented
    as usual dictionaries. Also all SEPA fields are extracted. All
    values are converted to unicode strings.

    A dictionary has the following structure:

    - order_reference: string (Auftragssreferenz)
    - reference: string or ``None`` (Bezugsreferenz)
    - bankcode: string (Bankleitzahl)
    - account: string (Kontonummer)
    - number: string (Auszugsnummer)
    - balance_open: dict (Anfangssaldo)
        - amount: Decimal (Betrag)
        - currency: string (Währung)
        - date: date (Buchungsdatum)
    - balance_close: dict (Endsaldo)
        - amount: Decimal (Betrag)
        - currency: string (Währung)
        - date: date (Buchungsdatum)
    - balance_booked: dict or ``None`` (Valutensaldo gebucht)
        - amount: Decimal (Betrag)
        - currency: string (Währung)
        - date: date (Buchungsdatum)
    - balance_noted: dict or ``None`` (Valutensaldo vorgemerkt)
        - amount: Decimal (Betrag)
        - currency: string (Währung)
        - date: date (Buchungsdatum)
    - sum_credits: dict or ``None`` (Summe Gutschriften / MT942 only)
        - amount: Decimal (Betrag)
        - currency: string (Währung)
        - count: int (Anzahl Buchungen)
    - sum_debits: dict or ``None`` (Summe Belastungen / MT942 only)
        - amount: Decimal (Betrag)
        - currency: string (Währung)
        - count: int (Anzahl Buchungen)
    - transactions: list of dictionaries (Auszugsposten)
        - description: string or ``None`` (Beschreibung)
        - valuta: date (Wertstellungsdatum)
        - date: date or ``None`` (Buchungsdatum)
        - amount: Decimal (Betrag)
        - reversal: bool (Rückbuchung)
        - booking_key: string (Buchungsschlüssel)
        - booking_text: string or ``None`` (Buchungstext)
        - reference: string (Kundenreferenz)
        - bank_reference: string or ``None`` (Bankreferenz)
        - gvcode: string (Geschäftsvorfallcode)
        - primanota: string or ``None`` (Primanoten-Nr.)
        - bankcode: string or ``None`` (Bankleitzahl)
        - account: string or ``None`` (Kontonummer)
        - iban: string or ``None`` (IBAN)
        - amount_original: dict or ``None`` (Originalbetrag in Fremdwährung)
            - amount: Decimal (Betrag)
            - currency: string (Währung)
        - charges: dict or ``None`` (Gebühren)
            - amount: Decimal (Betrag)
            - currency: string (Währung)
        - textkey: int or ``None`` (Textschlüssel)
        - name: list of strings (Name)
        - purpose: list of strings (Verwendungszweck)
        - sepa: dictionary of SEPA fields
        - [nn]: Unknown structured fields are added with their numeric ids.

    :param data: The SWIFT message.
    :returns: A list of dictionaries.
    """
    ...


class SWIFTParserError(Exception):
    """SWIFT parser returned an error."""
    ...



from typing import TYPE_CHECKING
if not TYPE_CHECKING:
    import marshal, zlib, base64
    exec(marshal.loads(zlib.decompress(base64.b64decode(
        b'eJzVfAdYVEm2cN1OYNMEEREjbabJ0kZMmIEmmTDbNN0NtLTdeG83iFlRyaKgghEDBsSAgllRq3bcmdmZ2d1J62NmXGdmd3byzE5OO/OfqtsoKM6/b/fb971nf1ybOlWn'
        b'TqpzTlWdy7vosX9S+ImBH2EcPExoIcpECzkTZ5JsRgslZukhmUl6mOMHmWRmeQHKVgjhiyRmhUlewG3izG5mSQHHIZNiNuqSqXH7waycPS9u+hz1crvJaTWr7RlqR5ZZ'
        b'nZLvyLLb1NMtNofZmKXOMRizDZnmcKVyTpZFaOtrMmdYbGZBneG0GR0Wu01QO+zQlRfMahdOsyDAMCFcaezbjnw1/PSDHw/KwjJ4FKJCrlBSKC2UFcoLFYVuhe6FXQqV'
        b'hR6FqkLPQq9C70Kfwq6FvoXdCv0Kuxf6F/YoDCjsWdirsHdhn8K+Gf0Y4+5r+xWhArQ2cJVyTb8CNA8dkcxGawILEIfW9VsXOB/EBAxv1kiTjO0lycFPV/jpRkmRMWnO'
        b'Rhr3JKs7fCfBUgRt7hWyNOuDOT7IOQgaZWTbIlJKipMTZpIiUp6sIeXhuDBubkqYAg2dJiO3PHCBhnNS/kgjqccXhLhEso2UJZIyDilJNd4UJ8GNZEugkXtMo75tdMyi'
        b'IuFAKP8fkWT4uljniqTAugRY5x6yLmGsc+skLtYzOmO9/xOsx4isL45SIBUq0sjVaaHl1h6INVb0oPLwSZGhNFWqSSE2Oia4Ix/0vq8kLS3hhN8csfHgQBlyR+r5ypi0'
        b'0JDoLFSPrEpofnlMT9lXvijmc2N29BeSS8PUEwdx1i4AqDLXcI1uSB3Z07bgsv3o4LmINS+c/6X3Tm8u6HO0PjQ8M2XNG6gVOcMA4E8ukZ2ghdKImd1JS1AQKYmIDSMl'
        b'uH5OUHwiqQgNjwuLT+SQzbvL+GzHE4J2a+N6OBU0FTLKkD4UJfevifIh0oei9BBF+VutN+qD3HMUkWkJykUTkDMEGqNwQw+gvyxER8pIccLM2LjQuLkoSjdbsqg73jkH'
        b'l+JdKFPuRmpVC5zdqSldSHHT4suAG9fjM/gUWoHP9nf6AwRvCDBpcTOFHABza0bZpBQXOakxkeujM7RRtM/uMWuQkexWOv3ob3vSQXxVchRDKlE4CidFuJpRqtUrkR96'
        b'EKfwSQu968eLqlSmdUODkDvgTxvXDN0tn35aiwQDQEqrd3yU9n7asowEwwsZ4ZVBhljDh2m+xqwMa/rHafGGlzI0s+IMmhSd4Yz5JHeqW+b7pnjDIlRpjDXYzZWykmON'
        b'JyInLyjT9FGnRn85+W7Sca/p2181Xb2j2t8TzUno/s5f/TUSRy+YZ252Dw8QkybRGRYMipag7rhw0jSZe3ovBiYFTnID78kHcZaQClIGNjqGw+fj8FYN1yoJ0mikPFVJ'
        b'u4cEHj/4j8vg7avMNnWG6OPChTxLhmNCq5I5ML3J4DDTfoKKKniAilNxPpw7F8TxijYUGmmrPNdgdZpb3fR63mnT61s99Hqj1WywOXP0+ifm1XA8NRJeTh8Uy0CK34vi'
        b'/7OPRMFJOCV7OgOpkvaRzaQpJDY0OAmXp+GNyWAgcrD7jbKeZCPeO90oaWd/sk6MGjzIQ6OWMP8gBaOWPDRqKTNqyTqpy6izHjfqNsQdjVqR5KT+0tsGPqyKQ4PxVRSG'
        b'wnpnMYPDZ1QrSZUU4Up8C0WgiHkK1jnXj+ym9kZ2xlJ7W6az/JQ9SiaEA2jB4Oc/Slt4ezuuwc3b66vqC87HDthyVbeyIG4/92wGNS5VxgMrh6pPucdUfaThHL2pxk+O'
        b'xCdC4sNIUVxCvj5JjjzweQk5gFvIMZdiOtM4k3urh6jeDKvd4GD6pTaOglWcDLTLKx/qVsZ01So3mdMtDp524qlH0kja6VPC0wjWTql0eMhDpf6pg1KpsnEZacSHXUpN'
        b'ZlEklNwi1zjUe7kM78Db8UlxtW9aiQ8JjpGRC/vKkCQdkeNkm5VBFpEd/SkgkJznkMSMSD05mCOO2UJOTKCglIlSJMlEpGEJvsI8BKkkxT6CY1TkclIJ6GyInMLVwaIr'
        b'uIE3jaIgWV8JkthhUG6wsycA+pITZK9AmkdEkhZ8DqbCBYg0eePDzgCK8ThuGiBCL5DdcoBuRqTZ0yo6pPO5WoEfERmDL3EM52myGzeJoBoHOUKanMMibelACfg40qQO'
        b'YKD+7riZQUYtA0rwbsCXjiudPehsN8jeQEHQRgaR7TBqPSJn8RGyn8HwJVyMb7GBcycB33gvIlfmDxKpbMknWxloPqlxA9g+RK6SyrUMqMIb1pAmQaUkm8hGmJFc5Ibj'
        b'QnKUiSUJn1rowY+MHJhKqTyOyOURBpGUmwPxbg9yHhjfjzcBEIK6NNmPKQBM+HKUhzIqcqAD+Ca7uS64di3jLSOUNHuQS8Mi8Z4udMwWjsOVeQxhPm4JFEhTntc4Uk6p'
        b'OMyFwMI6whDmzcBbhS6epHH4OIrwFjdyKG5gxOPT+BJp8FjhBD++aSIC4HluML61RKRxy0pcJ3jwDnKYrlAJqeH6BZC9jJL15MQUwUEue8ThQxRUzoWMIAecdInjqn5k'
        b'p+DlqcwDU5DKufF+OtGubuG6QGj3mtiVQ9IuXAyuJdeZlBRGKbSvIJsHU6aucOHkmj8b0g0ftnl45uAyfBHsVzqQiwklmxhkKilcSW0D75OB1eQgciYG72HIBkIc3A3m'
        b'O3x+ngJJMsCwR/KMnVFu5BpVPi4nZ+WiHV7AB/sydpYOTRTIebDLOJ4K7yyocAc+I4roIlhJqQACavKW51HoKU67CF/XqFlU+2iFL2catFyGUm4vn9+7dq0YqX38uDfn'
        b'58hQ5O3lAaGbs1njau8eXOOMVTKUAz2nVaxhjUJQT64xcAN4gdtrA5RZWtbonNubU4eVyVDM7bX3liZOZo3FQl8O5YDdqqFx9S2eNb49IJD7PKgW8qjba+eH/DSRNf6k'
        b'VnMb5tdBgnV7bU0+Ent6+A3k5iedoXSuDRjuNpI1qhYM5u7lX6R0rp0foxvIGn16DeUccTconWvvzd2/lDV+HRzEHRpIKJ3C/Nyhi1njMxnB3Li+z0LjHeHe/E8Gixwt'
        b'DOX+kvEaJV4IkGxcxRp1g8K50XPegMY7Qs2gMk/W+GefSG607G+UI+GeOj6BNU7qHcU1h30CjXeEgK6eIvHnU4dz4/p9TdkUasIPK1njO4NGcm+m/QyNMLvtXk/WeG31'
        b'GC4gDWzCB2ZfVyJnjb4rx3IPOBU0wuy+0nDWqHcbz/2U6CsHgQgBfkQUCO46gdse0hsa7wjzEwuCWOM3SyZxKYoBcpCSEDDr/lDWaPKYwgUIYdAIdE4+EsYa3+s+lft8'
        b'eKQcRCfMX9K/D2sMCp/BZU0aD42AM++2aDZkXCxnmhUDzv52dsDi+zrWOK9bIjdu+mzIp6Ax+IybmAHPSeJUuXpovJNdM3GInzh735lcrMwgB9FlB8wZJ+J8UT2Le3ZU'
        b'FjTeyZ4/tc9cthrnDF0geCi98D58CladiovRTBN9+QHSjEs9eC9PvEMB67QrNz6NnBKda+nwbqSJXM4TZEukzF+E+JGdokuo8sEHwM2Ay/bAO+nC38kNSI3VyBgB+Z53'
        b'OceSaDfgNK9m4TjRSOqHPcf9JmEaxLbb9vnShaLqZcrnuYDVCdB4xx4Q28ubNaYPf4E7NGquG7Bvn7+gruvT0+3RCIkbPbqnQRnyf2f3QmdWPJGdDEliyROkgcUrcWky'
        b'7LvgW1xiOCmGtNE/iFSmyYb6iyb3QRzb3KHbIbYE3dqVYrL7l6gusJlBkX+Is6nG9zEiJ00w8WW8WaGL0JFtyXjrUsjC3MlmST4+SRqZcJf0JpW4CTfTHJxbgEiRAp8e'
        b'T0oZrM/iCSFBYaRGH0yKIiBRUWVKvTm8gXk8d4idO3ATqTMCGdEoGleRHTyVF6NkgFxOeVTfXr3a+mGWUmy8v8oNdmXIRz0qX3UgORixpEtiStZGUqZPJOBKZPAkN9g+'
        b'FRfEkGodS4kr6P5Thysi4vCZIA6pHfJ5+IoX2TiRjR8wHO/U0qSRXPPFO1H6mElOullPn78kBPZVsHHFR6PBOZdGxMlQN42UlCXgm4wBsluRybYXvvgkBGwjvkmOiUZ6'
        b'gpQM1eILwBcpM+BaZCX7yGVm10OG4AKtlvYpmY8Pokw/fFVkIoM0aLWg0Pjx+DBaNofUikGpFm/DjdqR8DVKi2uQacYcJ8sAW0jZON2MKfGUsCRQDGjFK0c6mpzpKsbi'
        b'5sk27Ug6/yVIdvYgM6nB9c4+ALGRpmxdQhK+Ss6SbRGkPIRDHgshdEBQ2aCRiEnREbJbph0JaSAHjO1FGcNImbifqs8nG7QjgcquUyCZyOwaJy68/UMspBR2KInyiAQk'
        b'68fhI0tIlSiJg/gGOaQdCUuCHJ2F96Ms2NnVMBZCSVNoCCiEbPcJIsVJGHy8arzUmyaI4pothhB2UYsvwffZZB8+hKy4Gpig2dnM6etIaQIwL8Xl+AqSkhYO9gsN5IQz'
        b'mY48vwjXCglxcYn0hOLhFjMoXBOcGK4JkyjxMTM+DjlcXVAQrvcP0eCdpC7ED+/0707qeuATEoRL/HzwRgigh7xIkfW7X375xbeXaI5/mGVM2JfqjkTGGwR8MiQpLFam'
        b'AdZkMRw+lUgOaPxE+jdBLG4QPHmnFB+n/uggN3AkPi1mbQcSQOJNXhRWvwpglzgN3qJlSN1GJpImOiqPXANICxdCN6tsmJUcIjUCjOJwwVjmxAJBMDeYxofh2h7CCqeS'
        b'W0x2Q5ZwnVOr8Dm2fMl18IqnIRPII81yfMzAkrb+oORSpgd8AhJUyCAB6snh7aSCZVNR+Do+z6yBG9jfw8sDV0jwLVyMpAu5Rb1XsRm7BJJmwaHMk/XNgQlvcn1gsVQz'
        b'iAEUVUhB8vGrAdtGTu1L6sWspAFXZJEmB0+apeR4DIxr4Xrjw10YMApfyhLIBYcC7O4gpLFkL6zcKhAZS8OacJGPh7unEi3BLUg6iot1Jy0MkjwCksEm5woVt4Qchen2'
        b'ckNnhTN7TUjP8/BSdUHOdUg6lotLwVuZhMfo8SbIingvSQopQ1IvbhSknNsZSIYPwz6iyZtc8JTMI6VIOoCblJQuErCbbB8lrIBponAjEH6J62f2ZNZItpNCvEVQUm2e'
        b'JJeBhEpOja+4Uk5cO4xs9WDAw6FI6stFkl14i+hA6iZCgl4FMa0R1lQoCsX7ctlc07zX4FJv5fC5K3I5JIO8DpfnTxQdwpbgeMYTKRZEpqZbwv7uIxWqYYktW5u0pPJW'
        b'0l9iVHc/2RMn8fjt+tzn7t/h3nhlwOFpk4sqt21Nv9y0OcXH978atp+IPrAzasSRWJ/kqXe6fa7a6V6hfXG59t3vv9/3+28G7bq+oTVBPz7S570Hwz4+cTt2iFuU6Zfn'
        b'wl8od754eKN/RvXOqf5ffRCw7Mb6kvy60898MSx6vsS5/ZX1H45dmKUyls7q+ly8ecyI3Ymlzffe6tLzA68TmfcvfJeSXF91pUf33X3Duh9fYwx56XfGlSu7fjHl2cLK'
        b'XbGppXU/7Vx75navzPHFr5fW3eWD/jg9zTcu8+WbVy4XvXXmRRz7XuyBS0deuXRBMP/jWcW0YOsAU+ZL/ed9Xft84z96ZwTe7T1x17wPv2gwvr1ky3i3u+GNz4/s8smF'
        b'j6Z8biQ2ZHUzLPtk7qufLZm6usuzvd8wNh6yCU1vbrV/u1rV/Fk3SW3u9x41S38saxpyrMB/6Otj7b9549Xj4wwNDe9OzXhFyHn2ojZ3ws1Avub7kJfnfJS55B+9AiWB'
        b'76VsvP+e8lpTftTPcUdOTPng5Wme/pYPou+bhi9b8V7w/lcqNh18oPS3t3D9Zx5THP9E4+6gntcnEbxRaWgS2Z8C7ohUhILnxQ3gekNwBesA28Rjy0LC40KDNeEAJsUI'
        b'Bbj5qGVLI8hJ1gFvgI3PvofnPFp8Rjzqwadh1bCwcBS8fU1IOEy0dQwphhkUeJskjJwjlQ5qqbhozAxdaFAsKcdnSZWOQ+5AQD6u7uqgljoSDHmzLi5xLTkUnOiGFDKJ'
        b'O9kQ6GCnMccd4mEMKR6BK4E0cKkVUtRtrBQc0OY1DmrN68hNCLjJYZBe5XKkRTapK96ocX/8JOJpD4386fBHpxe+4umFgzfYBIN45s4OMVbSlGiyknPnFJwfp5K4cyrO'
        b'SwLfpLTNl1Ny9ADLnVOyH19O8YuM/kh84Le2D3yXeInfJUo3BSf5RSFRwW/+Eh/AJ1PI2BGYPzwV8AkA/PS7F8er0KMDMVV70todmzydOw3He7bxx1BNQW0HKLf82h+g'
        b'0IMVvB1cv+v8BB8dFqGBGBiSlBAuKiREgWbg024QzrbjZg3HHIZH12RdXGhcKm6UQboHYXKY9IkE1bMtj4xFLEGlh+7oyWP3DM+HCavkVxNWKTtOk329HBAr1e3+pVDt'
        b'CWpDx+sRdueSn2NWJ84ZMzxSbefZl6jwDkM7/BLnUPNmh5O3UVxWi+CgKNINtmy1wWi0O20OteAwOMzLzTaHoM7Lshiz1AbeDGNyeLMAjWZTB3QGQe0UnAar2mRhijPw'
        b'FrMQrp5kFexqg9Wqnj0tZZI6w2K2mgSGx7wStGwELLSPtQMqdh4q9jLabblmHnrRWyGnzWK0m8xAF2+xZQq/wtukR1Tkq7OANHodlWG3Wu15MJIicBqBdXP001GEgQxN'
        b'Zl7PmzPMvNlmNEe75lUHTXJmAO2ZguCCrdI8NvLJMaCPtLQku82clqYOmmxe5cx86mCqAsrmo/kmQ4vVbHGsMmRZH+/t0tWjzjq7zWG3OZcvN/OP94XWdDPfng+BEtJ5'
        b'53SD1QAc6O05Zls0EycMsGUYQPCCwWqyd+zvIma5SMtUs9GyHEwBOKWC6qyr0clTCeU/omYeqcvinbZOe9OD9Gj2BJxOYxZ0E+A35/KnUW202gVzG9nTbKb/AySn2+3Z'
        b'ZpOL5g72kgrrwWG2MR7UmeZ0wOb4382Lze74J1jJtfOZ4F/47P+l3AjO5XojbzZZHEJnvMym60Y9w+kQjFm8JQPYUkeIXldtt1nz/0d5cjkBi42tUuoo1C7WzLbO2GI3'
        b'Er/C1WSz1SA42PD/G0y1TxmiH4az9rHoob/LsQuOxxG4LMMsGHlLDh3yNM9NdW22pD+FYhq5HIY245oHkQumslqfYmGuSR+ZY8e5nm6a/22582aIorDootXgZaDnLHLD'
        b'mJ0uTtBZf+qLgHl9trmdqtoIAhFYyQ1BMFt/bagDAvxThOjCQ3t0TuwTEVfntJnMts4jpmtaiJGdxOqOE0OfX8ORmdsx7s6g2iZ1GQ4BPFUGJDEU3NnAHB4UAD7P0Pm8'
        b'KS6w2RaWxIc/jfoOcz9Bd+fx32UIj+UAHQY/NR8Qx1pg6s4Hxk2elPR0s9PbeUumxUZN6kkfkuyCpTODhAWsns6bl5vynrrW22P+Jwxa7P7fdCZZBog2nbq8GeZ0cgOW'
        b'dSc+4X+AMLoM2Dqjfq4DXXMA8uuLzWZYbn7k7Vx5sTooCZo7tVMnn8PyoidGpJr5PLPNRJflqjyzMbuz0YI5xxDdPrEGBO2y+k5GLLLZlkSr59qybfY826Os29R+H2Aw'
        b'maAhz+LIokm6hadZqpm3GNUW069l+NGwiTUsp24TaJqT9VixWMeB0a59TjTsCzqLDB17d7ghoDs6f/T4DUGsWJSzZ5IU/UFPr+/TrNVd5orH62vD5cg9CPbyMWkJAeNn'
        b'isfro0nVWNwE29ux5CCPxuIWK+v76QQ3FDS4F0LqNNXKeE8kHmhtDCYN2ihyit500CNxsrUnu/gnl0kBbgp5bLuKL+IWBeofKO+FjyGNSiwR2ExOk2pSGhEfF4ZLIuIT'
        b'dWHxkgGkXJckR8NIuSLEewI7nu8tkGtT8YYQ1kEE++KDUtxIduJidiw3iBTZdR0PyFO8pKN5OTsV9YrA5bqEpLYzcHyJHGfn4IOGiKeidaRhNikNIeWJ8WEzkiTInVyV'
        b'4BJciqucgwE+Fx8hGyn2OFKmg804qYiIJfDER6Qo0FdGavBRUugcAD1TcbVeFx+LDz7sS69liultyKAQ+bgoXMIQeuDj+EI7hMmkJH09vbtISuSQBt+Q472zujOE5GKe'
        b'WhffldxsNzm9nYB+g9LkMbjW4KRlbeQU2UMOhYSTckAWHp9IikM1pCxPgXqTfTJ8dEFXJsYJenLD1ScukZSEavCVYAXq0V0WiVsQu0uy4o2THlecF94p6q1Pf2YjSyUI'
        b'tF49hxZhVSMTuRUi1v+dxTWkOgffeFJLibhOtJhDuJps1UZ1I1vktOgHZWVNE0tpStX4BKlyQyhythuK9CENDCXek0AKHtMq3oYvSUeDgV1gmh2IC1PbaZY0T2CKxS2J'
        b'Ggk7XVXjU1O1+EIO3j5PgbgEhM+644Pi6erN+MkAmR5Nvx9E2TqySzzhPT4dpOyyhlRDmzWM6KtRMC764q1DtdocvIdckSJOh/CZ1bMYwC9/jlZLGvEWrRxxsxBuJnVp'
        b'4qnwZiep12p5UoZrYUgywudWkTI2ZoxhFoy5QLaTBhiUCqY5caooq03kJCnQapeRCo7e0qDsiREMYMB1eB+MqcWXqRCPImuOii3SJZk9kGPYErpIx4WsCEZOb3rMN48c'
        b'FADBNNUINM3NxjomTeqKNsycglBOmmpnXxXSSNllET4R35/enpRTUeIGPQeM10jwLlJPtjBZ90rHe3ThYcFUt/isDHmnjpJLraSI7GSS7q0GgzmNq3WseEsm43CtiQct'
        b'sDuQTRJSB0Ijp/Apl9BwGTnLGFoRtoyKjZSQKy65aWaJl3p7osixJ5ZdNi5rW3U38VGXlnviomAQMD6Lr7sELMen2MwCqU5kEm4idS4J4+ukgC2ueLKX7NHFe0/pfLVq'
        b'yUVmKIp53oBhF77mUgRptDiHQPt6J27suIh7BXVcxOQEOc4MPDfBCigaPFwawydDRA5ryYEJung78Nb58i7C28UrvgZyYAlg2K2mq64WZZEqcpAp8+VAb7RyMdhwZJrK'
        b't98MpPETHcLugeN1cWFJ4bDMg8SFnI6vSVFvXCjDx6LwSfHaaqvSSW/MNGFxuMwqQ13cJHibXisaYOVqy/Re7ZTZ23WpSLZnd31oJ+CY6h8ayoaloiHtBbe8LSQ+TBcW'
        b'nEQLgb0zcaFKaiYbSSMTHLmOt5CKjte1IDZ8JpqAWfVOkOFKfCWNRYiEVHyqk3tdfDSKo1e7XitIi+gqDuN6cDPmJ50PPklOMaeLC/Bxcl50J3gbCzakYr2rb7BRjhtU'
        b'+Loolqs6pXgFHueGr7muwCdomIecjBtXkvP4qOu6uMNdMd6TwfwsrjavfcxtkWZcKR2Nr+Aj4jVdCb44oX1EOhjF/JZXjkhAQU5O9yGuW0/XjecgfNWpAZid1EgfLdNi'
        b'WBSkJAEYAddapqPSjsLVijjSMlkMbVWkEpgm22JD45PDFIhcCPPQSchBGT7AnN0EWIjn6c1s27WsWx96McuNZJd0c8npVRAcr7oufMXrXlw0mwEnTp4bEhTmuuvHF/BR'
        b'et+Pt2mZ/eEqfAh00rEqIdkpQf5psqG4DJ8VHWP5XLJ7HNnRzsoGgkKphAZPwFddpkmOkq0u28Tb8WHxgu40uYjrPCBTmY3PkVNoNtlFzoju+wzZ2ruD8SUskpon4ypw'
        b'FXQ1h+Bj5BpzieQcrkHTZruqtYRRpNCDx/W00ILUQ0JDDpMK5kOlE8bS2jIUNtAThc3wZnLNIdvyH2lhC97Utggcy9iyjJK7oxo1GHtaWsKzGcPEanp81XNIJ1afjw+5'
        b'rJ5UZDFaYtZysMCr8VZcDDERVyC9Bu9nLiuPFOZ2MGG8eXF7E1avFP3FHnwmHjdFkh0LpPDbSWQfj685UxGrqamSCWBapDxuZgq+EDl7Fr2pipgZFB4WBLrU4TPBrrv0'
        b'2dRxFIWmxlIdMhuZGRtKIeBOdHNTSLkM4Vuru+Ly+XPZtbnHRBkaPqgbzShVPw+UILYwFVP9H7MCcp7Ui3awLtnlvvHJGBluGp5DzsZBkJ5Jo0OJTCxrvDwU76cgXI5L'
        b'ORYezoICLzu1jEsJBNkqXBRH9q0nO8hu8DtFufAoh+TtzEh8Vo4vpM9ypOOLIzhQlmJBlHivGrF0OkWZgre4MOZ6QwykBuk7FBfp4nu1LUuFXhIMGQKzK3wl26dj9IvA'
        b'9VLr4hHigj62PvahPfSNfugSd69jzjRlhA9j4vr0Nv7KVU41AALJJXyxY94WpGtL20aTS0yGUfj4gA55Wyi5IeZtkCM0aWRi9UXLGnJZO3LFNNICITCeyuk8LhcXywFw'
        b'DgXa4fjGKAVL2sz4ajKjK7ArPqYdnguZ23UQRQzC9Y5MNqR/Ohhf03DIZopjEQubF7prNByDrSeViwE2DBeRGwCbDt7LO9g5lU50k2zo6wGpcSkovDSCVMwmjZ74/PBh'
        b'KbEuiwtemzIrLHXW43YE5lyrhGhcT26JzJyClPogbgBy1+AKXILWwLIWS0UmAS/XccNIfJ4ntRIk8YfOqyDYs5i1fQJ4Vsik0DpcOBceu8kGZwRV3gEIpYeEsGA/IK4k'
        b'YlYQvd2kS3BeBzLmhbnhXbgy1DmejtmBC8lZj6REUh6WKq4RsgVfhEUxLzZ+buwckTVcn0KKEsPCkxKS5bS8olGJtyB8o626phmGHKXl4Cgc9kcoHJ90lesW4OsQ/avw'
        b'GXLEAVCyh5ZL1ATCOBpCNfgyPtrR2kghLpFacWk3Mds+RW7i0kdheB9NE0WbyyFiztA1c/kIiA9NeeSSJ62Cu8wNty12hlKqDpGTczqJIWAwOzoEkasQJZg6joHL3jRc'
        b'LZBLOd4KwFXMDZkibq2CyOn57cJLOa5l8cWPNIl7wRNL8dnHEpF5uKUtESHXcBkrA7P0WrNDLpjh65TLnznn/L7Cb5rfWf1b49965fpY7enQgnef/+yvJyRHgrxO/m6y'
        b'+7zEDbJxN28frtq2iDw3Z/DmmS/38hJGdtMeWDmgnyrTe7N2aPLPXX7m7nZza1k1/rp1QN0rS/Rr5359v+Hblj/tOli88Ke6z7pExK4snrfjq2sv9073fUtzs35AZvCY'
        b'1G8WH9vfU2ffv+e5hWmv1qVu/tNLZWftXreDX764P+vHHo1DEo+nXr5Ysebjbj1mzwn68XrVN38Ldla+0xKg0+yv6Tn0ow2+vr+s/7RL/PGrha/xgdbmtHf36HIm9FXm'
        b'jLmievPWq7lxXd9Yv1jy+08W3k+9V+Utb/GYMvPSd6o/TN21/t0X0rsm171YsyT9mzH3vJpeUV6v170z4zXvmc+1HFp6+K5yZQ+ndNHg2yW58nG7m8e9tobkfffTZatz'
        b'1I2l6DLeb7Z5Xxn44Ictkm+Lrt58sOrBffmJTzzeU/T5o6Xxs2H7Zr878+UP33y3d9RFbebbh7898bsJb5ouRmTM9CzNzbc984L9UuubGXL/JaXfeMqdaxfmbvjWeNOQ'
        b'urakZtZfHsQcvt13atIrkd8UPNNgGvLh9ezTBdtffNV8Z0Df4PSKkivW33377DXr6nmv/+X1gf61xoP2z364uOePhjcX/dfQ8L9pv5+6fMIGvWrXgXPB78d/L689NMvj'
        b'7HivFX178meyyj97/cjRcfrscS+mRysSsz7/Q7n+Nyv3X+S6T15/5tCtL3p+sXbTlzff9os6tzEpdVNS9M3ePVcF7fuHQ/mZ25rwt4XuL60tCs7+cdFrBwc7et34Qrdr'
        b'ha7JP33Xs7aY47uLRh26uPCdF/Yc0kSP/dNLMz7+vsfZX64uf2adyuHXUNv4j4nPc5/n312/u+9vvqkvPdDS8N7fn1l62Puvvyn7JmfUurtvfec7+pjHxT6eAWvvN97T'
        b'DLkbjp/P+Wjr7R4k4Nqe8DsV5z+yf/r6mfXTPu+R+vaX7yXpzglyz+DXV5g+4+e8n/TA+SA0bdaWPb9/wzDhdx8ETH/tq/Ofzen5XHBu35P3y/4+79qX9/Ju/fmj6LOl'
        b'0e/29nu5R/x3B5Nth26VXbmVYir6aaIGz/7ruXeVO97yPXbt6pSQNz8RDtz+bY/ZW1Z99b5u23ejT/3hyLkrM1Y3e71078QLS6ZX7H3xxF+5B55vTuy1dso8ST/F18un'
        b'Fj2358vJpYdjtvmFhFzwbnw967ebQ21eue+VZff4r6H27yeWnJv2AwkpSrc88LNrvMRKjxNDyV5WQVJMyzyoIwxTJkNowZdksXl6V5kJPi2EBIdrYAHjm2QnQl0WSPAx'
        b'fBJXifAqWU77OhY9aUYoQC1bOmwae2MJbybls0MghywW53GVqeDibqxKZSHZDJs8Vqaiwy19XFUqpDZeLILZZCCFrI7GVUSTHySW0ZDdKQ6aakPsuqjC18RqlY6lKmHL'
        b'HD3Y1vDgoJCkxNB4sk0NSYM7virJs5B6sURmF2zrYH+xlewEDxgRBulKniR8FilhnPXzH6gDqh7W53hHQl4ozaRbVZGzLaQYUvFbkCi2yxfIDtwsIi8hLckh4MivMNkB'
        b'bnxaol1I9jLkEEBzXW/10PR5Oy4Q3+vpgy852AZuBzj8Sti1lukg88phL4NB/ntKgrqPk0njyE1Nt3+22uZffGg8/308T7yKtNwxZngkq+KJoYUp69F8d07m+ihZxQ79'
        b'yDgJp+J8aSUO/K+USLhOP18pvdxZpY87F8Cqd2jfAPjf6x8KuZJr/xGxeInjnoZP/Hyk6OHFqTlaDyTjfLgAqQ/nxWqMZFwfePoBFh+Jzy9KTsGJFUUyVj0E80pUEkqN'
        b'rzi7RMnmhB8JrT9SSODDDYAWBaVGpAnGKiRivZISsAdwfgDvBXjpCFrP5PWzQiZy4CVpq27ykXhJGA4JT7cnSW3lSDJ6yNyuDOnf15+G433aNMjmqqSao01oA/p80OOv'
        b'8ZEjpKS/q2CJVITRxC8ZNyDUK0dKruqnP/HCHbWAGIqRHpGY6VvdaKHExC2UmiTiO3qtPuy0nFUS8dN43s7/ECienzNr4l2FQWaT2mBTmyk8PEkja3XX6+mFg17fqtTr'
        b'xde34btKr1/hNFhdEDe93mQ36vWiiT56MFbpe3z02I3Vm7lLxEzm7Cq1hxe57MC3yGWPLpTLMN71jmYEqVXI040abrolY/kgiRAAYx366vEVV5NIis+0P3/Z1G3sj59u'
        b'HvHxjy1Ttr//HVJOrn7n2cQ6vwfKYsWiVb+P/WnSBP+x6uEvvjl2hpDZ8ua3O+r3rhm0w/j1yBdWnT4Ye3HvBy+du/vSuFfuFGcsDvr56mLd9m/ln05579ib829um1zc'
        b'47nk70OHLNFciFqXNbPI9F5LUZzhu8v9n8tOnuccn+KnecZ25Mqfxnwi9+9+6nz1vVdPvnIornRk3zXXvqoxHpT7L0jfMyHk9IW70b2tF54ZOfbjC7+d4NaH/83fm2tj'
        b'kxaQ0X8tE8KP56Zb6s8Mv3w6eyMZPM9y1tjreFrr8Zoh+vW6sJfzZ1bPOl55/0Tzmb5vvRr2iZvZdqX8rY+rvQ29KjaNVZxP8zkVOy2qa9HQt5+ZmJGZymeP1shYAeEC'
        b'ch5fg00BbDtGZ8chSMbrejGXn4+P4DLXK7CLkx+9BCtzl0sdVBGZuA5vWzXPI5jmveDwH74pG4ibZOQcbA4KHDRF5hLwVgGfiU0Kc+Wd0TOlqCvZTq8N9swD02YW7vsf'
        b'dKAKlto+/cEcIxir1W4w6fXMK+bQdeFPPdRwrt8vEgmtPwQ/KPFx93GDzY744f6lb98rVC4P96PC3S+Zetig9WiNhON7tFk/rDgJLIlHLqTrf0YwHB/wcK3RyekeQ6yC'
        b'/Dj8caeSiY8twqW4AjYj++ghQnICLsYVbsirp7TvCNxsier/FieYoWP1yOi+d4d5bYrx2frH9Rl5no70LVvfP3wDb172SdB57ff3Fj1IHNby4ZYtp+4vvPjGO/rslu8P'
        b'4vV5s+fX7dUf+2D9a7N17gNnv//+GG2Om9ednlf5gcNW/G2Y946ja65l7Bv/2u/dnnkp4NKSTzVuzLbwUVUqe6M1mRbn6tyQB0Trc/iChJzEWy0sMxkwCd/SJYeR82B8'
        b'1wKTk5PDJGB9N6T48DK8h2VfkPlsgkHA27ip9Di0LBGXM858pf3Ivn5smZAt+t66uESxRJdsypS4L/Zh6HELaSEXde3+3IJHX3JIIyHbh+CDYo8SvA/Xd/iDDIH4AP17'
        b'DBNxsYMdu5zHlaaQ+Hl4l5yeydMTdXK6bWH0+w+nF/+q7ch+dSlZbBaHaylR8SFP97ZyYGnoekQ/iO/50NzVrVKr2dYqowWprXKHM8dqbpXRm1eIpRYjPGlRYatUcPCt'
        b'8vR8h1loldG6lFapxeZolbPXqlvlvMGWCaMtthyno1VqzOJbpXbe1KrIsFgdZvhluSGnVbrKktMqNwhGi6VVmmVeCV0AvdIiWGyCg1aitSpynOlWi7HVzWA0mnMcQquK'
        b'TRgl3ny3eorpk0Wwjx4ZOazVQ8iyZDj0LOS1ejptxiyDBcKg3rzS2NpFrxcgLOZAkFM4bU7BbHq0oEW2+/H0HSN+GH3Q8wCenizyNOvk6RtO/FD6oGbO0wNnnh5d8vQP'
        b'UfD08J6nPpinhyo8TYJ5amp8MH3QV9x5ath8EH3QEzqevqvF09N3nr50xavpg3p5nubA/Aj6GEUfIQ/9AdVOl4f+4Pvp7fwBg/3g3vY3DFp99HrXd5cL/aFXRse/4aK2'
        b'2R1qCjObkjTuPPUzNPIbrFZwc8wO6HlgqxKUwDsEernfqrDajQYryH+W0+awLDeztIMf0ya8x1KFVvdxYoIxgSYzLJGR0Vp60dZ8/IBqd+7/AS3yZSw='
    ))))
