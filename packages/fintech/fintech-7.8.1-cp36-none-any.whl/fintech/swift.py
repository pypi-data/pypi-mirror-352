
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
        b'eJzVfAlYVFeW/3uvikV2ERU3KHEJxS6FG26IGzsIuC9QFAWUFFVlLSDugMouioIoCu6CiAooinvOzfSkO+lOMulsJJmkO52lk3SS7mxm/597X4GCmn/PzDfzzaQ+Xsq7'
        b'nnvO7yz33vPqPe6h/wT8i8A/02x8ZHKruWxuNZ/JZwq7uNWCWrJBmikp4fU+mVK1TQmXa2sKWiOobTNtSvhiXm2nFkp4nsu0TeGG5Mjtvlc7pKyIXpwqy9NnWrRqmT5L'
        b'Zs5Ry5IKzTl6nWyxRmdWq3JkBqUqV5mtDnJwSM3RmPraZqqzNDq1SZZl0anMGr3OJDPrsanRpJZZx1SbTNjNFOSgGmclXYZ/XvjnSMnPwkcpV8qXCqWSUmmpTaltqV2p'
        b'femQUodSx1KnUudSl1LXUrfSoaXupcNKPUqHl44oHVnqWTqqdHTpmNKxpeOyvNii7bd5lXEl3DbvzbZbvUq4FG6rdwnHc9u9tnuvRPbgQrPkkgRVH/d4/BuKf8MoCVLG'
        b'wRRObp+gtcfvH/kKXMPqIfgtPW7PAl/OMgm/bibHyW5SScoT45aSMlKdKCfV0cuSAm1XJXJPLZKSu6SenJXzlrF0gTFQZIqOJ3tJVTxpSSZVPOcQLcBlsoecVPFWEiT4'
        b'595HQgLlAo98+P9wIcvdulq+TIKrFXC1PFutwFbLbxesq80ZvNqnHlntPHG1l4JtOSfO3tlelh43ymMWxwqH20k4KWdvpizID4sUC9fa23NunCyMS08PeMczUCyMW4rt'
        b'OG62U0R6QL1LCqd1oC2ne0q/cucivhj2XdS3QveUMUv+ymkpQ/8xt4G/bMfJdnptDn0r9E+TJorFPpO/dD3oyvtenvAu/7Onq8rC9XKWAKyAk1NmItMrg+fFLvX1JRXB'
        b'UYGkAlpTfWPiSU1AUHRgTDzP6VyHzBkO7QM469C33BDKWcpVLkvSzzv+V3mXPZh3to/wzlHkXf1MF8NLwgyOC0nXnp3gK9I8IxSKSOUS0kyq/GNJFSmPWxoVHRC9jAuN'
        b'TRkOB1OhEuq4bBs70hw/0zIcOyQM9VXANRwbWkkHHOc2kkNw2zISa8gZcpaUK+AKrTwGZ0gFlxtCii0etK5eINWKUMqketJF2jnV2hGsQiCHySVywIbjgjg4MyaIHIVy'
        b'Ru32TMfJEzhfjnNLdxoyfL0ov280w2T+XBQF+1i5jwun+eClDs6kxH/bTOv9JP2j9A1Zccrns4JqfZVRyo/T3VU5WdqMT9NjlH/IkidHK+VJscp2dQt/flj2R+2fZcYo'
        b'nxN+O+X05Wuh0cK/JL+e4nki4DceLm7+x3oOdxxoLRmaqQuRZI/movYMr/LeLxfM1AzwcNDgiIySx1vgBtQE+qGYBW44lErt15M282hsEhJJahEGFaSGVEk4KCVF0pk8'
        b'dESTCjnfK/jK5RIjFfqDRyv3/YjZWUb9ZrVOliUasCBTgSbLPLfXgVmntEylWU1tqMmJStnHiXfi3Xh73pc3UmkbqaTlkl6bfKXWou61S0szWnRpab2OaWkqrVqpsxjS'
        b'0h6ZVM4b7eh3G/qgo0yg47vQ8d9xE2x5gbdlTws1hGFwcqR/VIAfVJN9CVCdiAix4UbgwkYFwZHFKsEKP+ljsIyWoh/LArMDEsSywLAsYVgWtkseZwf6lGMglm0TLNQU'
        b'zhs5kxxAtMNeWSAXmAvVrHTKEATzAeykmB/MBWdBvYXarAAE9zEGsW0FQVwQaXHUHKiyF0yBWLfvuT99kv67jChlnHJD1seZH6cH1EalX1d+lu6ezXWOCm84Mqpk1IyX'
        b'+eqn7V5Y1CnnzZ7Yx39DvH9M4LwAUhYdl2DDOUKHgON3z7SKYRCfWSnjcq+jKMwsrV5pZtKkkOb8nHgpytLo0C9JKZNMr02mOkNjNtJGRmp35MJD0hOM1CE9JELa3b9f'
        b'hK8NEKE3lsxMh2tUhAlQkogSZM4hgOfG5ElhPxyNEDV4Fyr1DZN5WogfdEs5IYMjZ3WklClqPmlzozVhbjwnqDnSOhRaLCNop4NwAk7RKjtyXsIJ2RxpGxHJ+kCJV6jJ'
        b'PD0kYxkOpuPI+VyoECeq3wTNtAbukP0CJ+ixD7m+jtV5TxxnIlemhuSSczgTlHBoL1rIGXGuuuXQxGpXz7fByl0cueKnY3YJSqGHtJiMU0NCh/BsxAv5ORaqj6QFjVgP'
        b'6bJMCSE3yGEkBU0aDlo01ELFOQrK4RirVcqQFKjHMclFcocRA2eTod1kUoRMI+3YcQdHLkIFaRPrTkauYf3ghjOuG45w5DrsW8jqtoTyYtVtpR1WNXKkhxSRdkapPnIE'
        b'6TI5OZBiF5yPXOXDyN4ERgp0kWqoczROC4G7aymdZzlyLY5cEnlWKYUKR9IxNWS2BOvQT0ugilxmfIFTE+C2o0NoyGZyGhdP6vkhcLCQjelCGqDckXTj4kvJBdpxN8+v'
        b'hDuMlEIoyTWRrgKXcDhBaTnB+4/0t1CN81rpahriTC4vG0fHu8tP27GEzWS3DSfaaCHdpEdNrXcHP2ktOc2qHEmR0uRoNI8lx2mfBt4L7pJmNs9oaHIwmck1R59ZtKqa'
        b'988jR0WJNpN90GBycXYgl4cJnMSGnwOnExl64peTTqxwIbekPCcZwkdkkYOsIgn2kotYs3GsP13PdT4o2JsNtjaA3HV0NkAVdJCrUk4ygY+AVokIxUtwbQhFRxyHwDFw'
        b'pN1uBiMtZgxSNi2M7CMNtpyQhcCGu9NEpu6bHUZFj+g4YSMisTPDUwTblWHhJtJBulxtZ1O+XeTDXOWWUXQ9O8nBSBOyp8uVtMFdWnmeV2whx+Uy5sG+mjeMDxPs5zkk'
        b'3ctbGVa7nhWu8PTgZwjp01xCsHBRlYUVPr1gJD9byClwMGDhlOylrLDXzpOPEGb423H3tnkWhMaLXnHpGH6h4Duej8DCybdcWOGahWP5KOG4v7Ps3rbX7RoLxPBpgjcf'
        b'J9irndOx0LvOjRWqA2R8knB9kZMbFg7du44Vrhzuw6cK9r7SJCyc/2/jWOEHaybxK4XjSueQe9tWpl4JZYUB4yfza4WGNYIBZ5/zpZkV/snNl08XylAv7plWGnu8WWHs'
        b'Aj/0A75ZjtzTpobVa31Y4Z2xAXyO8KKHNOKeydNmz1pWOHRREK9F4h0jnja9vnrhdFb4x7EhvEF4V+Uiu2dq2PhHsbB6sYI3Cy0hvAzHHOIwhRXmJYTxm4TrU+3TseWs'
        b'2nBWWGUzjd8qPBsxJP1pk2fCSFEcX0pn8DuFlpG4dlNDrmwOK3whcha/SyhLcXTDMWfecmKFBp/ZfJnwusImCenMdhe7B+fO5auE9G0OSThmzrtyVhi/fT6/T/CcJAnB'
        b'MUeQ1ayweMIC/qDQkmwXgi3XzhMnenHGIr5BaNmKrDN5pqhFLpXrF/NHhZaZEgPOnns2lhU2RUXzx4UItPn3cl/X3Mxjhdnz4/kWISnPIeJeboNHsjjRpVWJ/AXh+DqX'
        b'iKdzVwYm86ywY8JS/rLwUYEgu5e7MkoazQptjSn8FcGwxFn2dO7rBp2bGKid2+RqcnRwWU4uodI58RGkPJ1VrIF6f0ejizPcTEM1HcrPId0jRKO1E87NQnN6rcAEhxIk'
        b'zFr4Q+dIVkmOOo9EA4Mmm5xGS4eVB3kfcnmhXMpI6PT6V/6oJGqVo+HpAs8pQoCICOmz/HGJbCTP3dOvzIqdywp/Hv8cf1oSFeLMPa1viJwvQs9ZeJ5vkdyf7hyBLeef'
        b'Knh8UB3GceKWjW5VuCybf3JTMmALxrYZjwQjsxKYa4XuGHIFKhNxC1VDyqPjg0h5sGyGwI1Ilz5FujIZqdxwCQuPXkzL0VZsWyyGs19to3sULuQLc36c++ppHLPzMUFj'
        b'YoNjyd7EaDggs+HsyS6hcCRcEnl9TQ37oAuu4GcnuSTl+FUcXIgJYaYngdwO9vfFiLQsOAHOQKMN55QtcYUe0aCTWihH79IFLSqkI5wLTwwz0iCEEeI6y4YuUbZzzoaA'
        b'I/4WsfCDGXa41+LcXhyWqfWJX8IxGGRPhn1oEk9BJyWnllOSYyssNHTUQFd4LAt6a+hWMhZqgqOh3XcJKeM5mdnGhRzIY3QsWwAdijA77Ir9D3IZw8k+Cw2s4eiyHf64'
        b'aaK70CrcQ0XbkztSbphcQqpWkBOsqxucnqYInQ5VtHk9p5qPGw9KUyQ5MFkBnavhMt15NHNaKBopmulrMXBcoSDnyS36ryYuex7cEmF+KTpRocBlHMbQF05wG4aQDhYs'
        b'6rXkkmIaqYujHRq4zB02LIaITCPnYmMoYQlMMsVuNpyLQTKjUM4mIjfHQ4NiWjwpoxQc5tRwGE6zjnA01Dk2DjsFk2p//XKec1yN7gLOWqdz3lSgmLZ4FgoCw4cs0gMn'
        b'RG/VExWHVDSQa5S8Ri5bC3UMAP6kGy6SyljKpROhNpzUi4eTcMXE+LNZTXoU05ySaFx8lMvBmKfTMoZFB9BMDvtTcZDyBGifLJdyTnMkrqRzjsiMOz5QrIDubUG08XFO'
        b'60oOicRXp8NVUhmHC7eHwxJOQu7w0Ig7tp2WJMZQ2A3NUEIaTXHR0fH0pKF/E+kbJPeLD5IHCg5wRo3LPQunfX2hdYS/HA6S0/4ecHDEcHJ6JJwTOKjwcIPj0Ogmet0T'
        b'6IHr/RMCo7KhScpJI3g4L01iXPYljStNzkYLubqMmpkmfsIqOGyNJ+GQlHS5GC0quEbrunn5BDjJVuewYTXpwl6hTrTiDu8fBQdZp3jYRy6YsA8p8hMtkzephBusU0Tg'
        b'OtNGi4OSoleAm7yMnBsvzrQ7YQi69wJyRQM1NiwMGx8MTUwBs2EP7j+6sM4ZzkIXz8KjULiVz6ifsxW6HV0coSZ0CRrQ1fwa6CTV4pJ7oHWCyexQYDHQoO82PxaVvF5E'
        b'cJUb6aFVGmiisxXxspmCSMhpaPQlXWYjueLmRcPPO/wYOJ7IBlyKm+xyE+k02+ptccfaxJEaqE5lGAmB4zmO9s4OkbgH5yTT+agloqp4Dd2IAetGJ6lopY/wT2FUx3rE'
        b'K8gVRxenIWQXAlYyi49W24tUt7g7Y5RjdFkKB3BBLvx0cpecY4OtooYAA6BO56WkFOt8+Pku3qzGwynNtHGjk4G0UL52Y4hYDsVsPSlQBDUmB6NlCLlDBVWLPL9NKhgJ'
        b'cGM+XHfEusjNCEJ3PiTfxLQnGS6sJQfIJXvUkgAuYDl0ibCtJ0fR1FW6OmzM57lMKJFigAbVweSmXGD9lgSTFsW0ZHLSqneGWUzosXAQ9WDa9Bir0qE6lmnv//LLLwui'
        b'RfP44twM7WRbAyf3YO31UIwRKkIr3M+Kx42irwwd/xQDIxy3sYLRrVCMdu8WQhlDY7KHFY3kUpYo6Usb4BxFo1uUFYxQMVs0+j1wN4qikTRDbR8cD6F9YfFma9Q8EY+k'
        b'jrRZAQktKAjW9Qwa/TsiJMmVFCsiXReLRqYlZDoDJJweKyKycA6jcth00k0xR27ABSsg89EiUCoFUjGGVkGtwQpHclDCphpt0YpoJPWkqw+Pt6GbTWU3P4/CcVVuHxzJ'
        b'iWVsqjjYE0LhCCXQIeIRatBqMYCfhMtpDJPk+HYrJqFMLXJ+83QGySK9CEmU+ElxwYfIjWSGSnIVDouwxM1Ajbhh68SQvEoE5g5yQwSmeb4omeKFCRSZZmiyIpO0Q4M4'
        b'ZgluUoooNHFpNVZsQqN4fgUXJ5FLFJpO5ISITcNUzepXDwum82iGA9d+vq72bsJbEW6/yc5/7ZuNM38+MGuUEPbH1PFJY51PHr/uk1wRu/+TxfszYqPu+15sODMlKsj3'
        b'wuzICo/WlkIPP6+dpc9+umnMxTeOffe36e/84cLbR/7F9F7QialdT7k67Zq5yemHmSG1vy1yesPujd09HRdneiSRH/0n7bfZFr5nxKVfnjGdvvCbj4PCVwqWfZ8e+75+'
        b'827lhaW6hZ3Grszd6pQJ7eapXmvWxnmeWXB03abn/rxo25yN7t+e+l3nKdczretfr/gh3Wn6L7suOBSmdI747ebDV1YWLRxzZsYLBRN7U/MnvrQ83T16R2jJ/dfK1r2d'
        b'r/nLX+Ju5598bYl6mJo8e+dg6+XmyH9MKl237J2pk0NmvlM5vPngL8sP/bR392vDv5kekl80tTvqo51vuxV7j8mfkD7LwZR76eT2v/mEx0es720qtrGsOaJ2uAvTZ4+V'
        b'HPtu171zjh+HHQr54TPFHyoOzn3tPtn8YfX9xldTV2gtlqPPbj1iV7P2purDlz9Z57LVTXN+TuY61/aeUXHk2JaZYce/rol//utLtQ7h+9dvWVqiXv11+PrMIq157Xu3'
        b'Xnu39ucZH52L+MJ5+We/SLIKzzq98Yrc3kxd5ZYhpJ1UBiSgCyM1AUYN+mtoQ4dNuiLZ8R/ZmTfFPyg6wE8ehPWkHHVzL8d5yqTrcZd428w0smJZbN/xH7nqgmEfPf1L'
        b'JUVsAoJGH2r9g9BXlgfwaBDgrC3sFQInkNPscAlRd5Icjg3wjSLVsbrVPGeP8xfOsTUzk9uYSjpjo+P94u04cou3lQr2C0mLWUar2kywm57v4LCkHGeugUoolnDDZklI'
        b'I1wZb2YqdYI669jEQNSEdoR5Pj+fbm7l9oPPrJ70kNs8uf7BOZe7eM5lNip1JqV40cKOu/JpHBzpwtvztrwH7yTY8068i4DfJA5Y5s678PRg0553YH8e+HHD//d98Lvg'
        b'In4XHOxsedrbgR8huAv2Akbu+JEKUhzDjR+BNbb4GY2j0+8uvNGJe3BM6vQwYQ8drz15bXLe6Ny3OjbUAq7voO2ux8MHbXJmSXhb8aCtOliOkZN/wnSyMy5IFIq/LbcE'
        b'LthhDHRrgZwXLU+7DXTFRgdEG3BjgRE9NEIdnBqwlaGTs53HQo5tZeitC/fovUuWc//WRnji1kaCW5tdcunXeTiog+yh/5Ko0Ewy5cCrMHa/VmhQy+JTZ4aFyPRG9iU0'
        b'aEDXAf+INsuMarPFqKNjaTUmMx0iQ6nLlSlVKr1FZ5aZzEqzOk+tM5tkBTkaVY5MaVRjH4NRbcJCdeaA4ZQmmcVkUWplmRomMaVRozYFyeZrTXqZUquVpSxKmi/L0qi1'
        b'mSY2jnoTileFo9A22gFDseNxsZVKr8tXG7EVvQG06DQqfaYa6TJqdNmmX1nb/AdUFMpykDR69Zil12r1BdiTDmBR4dLV4U8eIhB5mKk2phnVWWqjWqdSh1vnlfnOt2Qh'
        b'7dkmk7Vus3xQz0f7oDzS0xP0OnV6usw3Ur3Zkv3EzlQEdJkP5ovEEq1aY96szNEObm2V1YPGsXqdWa+z5OWpjYPbYmmG2vjwOkyUkMc3zlBqlbiCNL1BrQtn7MQOuiwl'
        b'Mt6k1GbqB7a3EpMn0rJQrdLkIRRwpZRRj2uqshgphwofULOCnM4xWnSPbU3vVcLZE8e0qHKwmQn/Zcl7EtUqrd6k7iN7kS7z/wDJGXp9rjrTSvMAvCxHfTCrdWwNsmx1'
        b'Bo5m/t+9Fp3e/E8sJV9vzEb7Ysz9X7oakyUvTWVUZ2rMpsetJYXqjWyJxWxS5Rg1WbgsWbBodWV6nbbwf3RNViOg0TEtpYZCZl2aWve4ZbErq19ZVaRaqzSZWff/G4t6'
        b'OFYI73dnD/uifntn0JvMgwewIkNtUhk1BtrlSZabylqtyXgCxdRzmZV94FqBngun0mqfgDDrpA/gOHCuJ0PzP8x3oxq9KCpduAytDLZMJrdUuRniBI9rT20RLj4tV/2Q'
        b'qPoIQhZoyS2TSa39ta5mdPBPYKJ1HNri8cQ+4nFjLbpMte7xHtM6LfrIx/jqgRNjm18bIzt/oN9dQqVNTmeZTWipsjCIodWP62gwogDQ5ikfP2+StVqtC0wwBj2J+gFz'
        b'P0L34/2/FQiDYoABnZ8YD4h9NTj14ztGR85PeDLs0vRGTbZGRyH1qA1JtNZlMECiAssWG9V5mQVP1PWHR/4nAC02/w8akxwlepvHmrwl6gxyC9X6MTbhf4AwqgZMz6id'
        b'G0BXKtb8urLplHnqB9bOGhfLfBOw+LE4tRgNLC56pMdytbFArcukarm5QK3KfVxvk9qgDH84sMYBHorqH9NjjU63Lly2TJer0xfoHkTdmQ/vA5SZmVhQoDHn0CBdY6RR'
        b'qtqoUck0mb8W4Yfj3lWZR80m0pSaMygxcGDHcOs+Jxz3BY/zDANb998l0Z3cCG7wXdIKMUmrMEBg90RuBrPT4ky5eBPTVCieP172NDn55s7ixAPDblJCuqALWnNwdz2L'
        b'm0VOklLWfGKILbu4SXLPCpiWOVW8uMkgO8lFawYWB1U61Wi4Y/Gh+89uW1LrL+5U+7appH0H7lTHe9uMJh2wV+7EGq5KgVJSGRwTHQgVwTFwckl8bGAMqY5NsOGmkGpb'
        b'//Dl7CKH1JEGcsk/hjS7P2jgDk0SuBxKqtmFBCmWTIhdTIoeXKiItymbSAk7wA2HnVAJhz36L06s1yYRMSxjEc7lkyJS6U+q42MCBc6e9AjkMFyECg25ZpmIDSykFE7T'
        b'65poUhWL+3BSExwFTbjprpZw3u5S0pAMZ9iSvCZC7UPtEsneIDhMyoOR4on+NrP94SwbLwvOD+tvluVEG7KLroR4npPDLRs44ufDxpsJTZkD5iWV5AJUBUdjw4npNhEL'
        b'jayZK+kk+/2DSDWOFBQTT8oD5LbcGHLAiTRK4RS5RYrYOqdNIMXWVtHxpII2GjlcaskK0cNuCz308YqLHiQ4OAZXrZKD/ctEnOyEug2KUHoxdYgjd8i1zDiyh91bkhY4'
        b'CPUoqW4oGSyqZeS8eLN1ZB3UKkJt2In4UFKeQ47BTXYoH0RqM8gB0gqVdhwXwiFRxSxXzBtbNMdGwaHB0oUSq/jhbna+HNoGS5fcJPvFc9orUrimgE5oDjDYcnwcB1gH'
        b'LSI910iHRSHePjZhRVAuzeNhoKr1GDoQFCqyByrgFPZklwh1cJxXKJK2GiQcH8tBu3uheM58AaduVCjIMfx22Ybjk5GAcSLvNls4hQKq4IYR+yRycImcJ7vYqc1caCXn'
        b'se4ENJJO7LQc9XHeEqZpZnIHjigU9BbuJGoa6cktUDEKbNzhokJBWXmKI53TtBmwl+lr5eIRXADq63FBt/bN7cM4iysW+s3eZCLdRhxlEbdoWApr2DbXjeYjzzietk37'
        b'aeRmTi5h6hInVdNbt2qRl/akQSDXBKhbTm6L1yGnoFgTS44FBgX6URnDRSnnulyi3RHEVuICV+xjWUKfFPZBjZSHZlKUw3APB0gjVA1SJLJ3dr8ewZ6tog2pMyUN1CNy'
        b'KeaBHo2BK+J43X5j+pslJjxGj/I8xfEaIjwH6ZGEtPerEVxazhhqGE1uKxTipe8KaMkZQW6KmSK5rhwqkKchsFAbGzeH3tfQUdNIE6p7dGBCECqTr6gwEm6ME5RAqRTO'
        b'kAsr2ZWKGc6TBnqPKQ+MlnJD7ARoToG9OQh7dlx3B3qgwcowCblO+WXYxhA4X+Y9SA6wNxNhdwEusIEDPaDHP8QcExgb6JdA86xdsyVqtNpdjDnxZJdy4AU6MgbapdyY'
        b'7bArTgq1UDLbMp6eQDq6PHrRLonw5dk9+0bYy9QQmuHUItTt2rWDVRtujGXs8I0m+8Q7bdgbHENKZz1o6KeygTZvE9OPrVC3zZqQIGYjZMQUJpFi0dY3k2u8v+8odt7d'
        b'd3FvvbVfPlNUy+PrUmOH+j9iDE6hEWL1lbDfGdW0brA5GCuq51A4tUa8gqb3z/uz2BW0NIIdtY4jxfn9HIdyZMguj2BSEUeP3mMpg0PhkG001OUw9msF6JmajguJCohJ'
        b'DLTlHGMFBEQPKjTTkkbSkDZnxoNbcvGO3BtNLRP7DWmKeO+OYie7Q+m9++odjMJIaIXi0cP7Ui/EtIvxSxiP0fheRc8zMDeEZYZA+dqnEBliFhx0QEWhFVPuUE8xlU/q'
        b'xQu+miAoG4DGu9CNcFzOrMTqKaTW0WUZBgApXIp+FeuRBBVoB+HGjIFAK/QWL/u71gU60oRf0sop1kE9etJjYkWLA5xAg94QSS+uuEBog9tiZkaZOzk/2MCchXOI7Kvk'
        b'AlO4M0vERBbDlm1O72/Qcwyn9nmyx+PZexKF85hEMUPoCCLgCM57CN0I1HDkLqlKW0qamU6QqyifxgcgzSKHBoGU28qIn1JA6qErREJvNbmZ5LgezgyzrKAjNJK9Y0wI'
        b'IFIdvTQJOkNSkkkZonSpb1CgL4rLz5q3kOILR2agSSgLWB5FZcVwsDQqgFaioYhdlkSqpei5tgxFc3QlizFGR3omPE60OnL9qQkTGV2BaZ7QFaaFE9SRLUWnswrOi16n'
        b'h9yYgVVocq8aeOZ0LibDVYuCMhyR7EQOQFk02U/qyUEoy8dHNSpJ+zS4aAOdGcnmjIBUuDqVR7HYroIDc9ATMF9fos6MHZ7Zp0e2aYLf5M2iml1EYZ2KjS4Y5ASga6EY'
        b'UzXTPP5BUs6YBHXkTo6Y5HR8KTQ9ErO4iyFLWixjSAHcJAcejVigzCEEakxiDsfSEMU00g5HNqJHjcFFo3fdy4y5TxrcUoTZsjDFiVPDNYzRaPm6bTGKMDg7Px+5FMGh'
        b'rtW5isDZCUfhPGVhVSS5zDEX3El2TxbVtTQDymnd7uApWLUYg4XF0GCJxKqxue6OpBot1l6EAalJIZedoSNsSlJUH0iSA5cnDxY8wq/ZAdqM5IjJmlVOuu0U0JZAGpHi'
        b'rWgki+aJl8Xnp6J6tk3TIcM7BE4YwWHIsJucEYOXFmTNEVSsYlKBYcB2bju0jbPQPHSzhbSa2MsEyb70Eo8qzIp+CujrO1JuRaAdiqMVQTKToyn5+2IdE+JJdeByK6BJ'
        b'+YqomGVRqeKC8izQmkTK4gODEuISbTBmJpcdYPcIOMyYOtSXtKHOHV7PXrwIwloxLypjiwsCrx1LyWEM945DmypSLogOpXI6FMeSZoy5BkHoNPSIhqIzmBwb7AFPk5No'
        b'KEqR+cyaVZEzsJ8mJHQ703v2U2PRgYTBgQKLH8dyf0pcBxh0uJv8qEEnpWK6OhzG0OYYRkkGV1tOGOlHyvnJK0glq8uGhtH+xkHGfkYwC5uHkGPpj4YBUC1nYcDIqSwv'
        b'Ti6m2SBA90IlBpweE/tj0Yt9uct7SBkc7Q9GySlSnBvgI7dl+JCtdlYo5sG5vmgzJ0XExyVoGoHBZgdCsC/YhD2wR3QDB+CiIwaVd+FCX8CZj7yl/bzILqjBqlZyuz/e'
        b'xIC6TkxC2KmBpv6Is2heLmncINr0A9CCobQ15nRI0U6GC7gwRvwVOETqccQ2RR+JpEJMpX+KnKfDTR3XT6ELOW7tBndUUKJQjCRH+0Pi/dZceW9oIodxacXof/pJ7FmH'
        b'HRkpezbAdRM2PiaGtHAZHRwj5HLwmD6HhPZjD7okjNRZ3s2F+ex1LZnbkC1O4aFKzkrDdNiHyOgKI6ehtc+umuaKrxPpWQ00b+kzqqGL5FImkFy/ZYppyV59dicYaljx'
        b'nCVkZ5/ZkZOr6qnrRUt6GwOCi4owqV+/3WlJFemtX7cJp5iHjqvf6hzJl/OihteqVViZW9hndcg5aLJmHcWjv0eBnFos6hypWcwkmwZ3cOfTr3ToC+ugjZyNYBw4wok7'
        b'/+OWwrjvcuI4zd21ZRITvZT+/acXLalrKscu8phr+esnz08+MOmN3z7Toqo6Eh93q903fMO9he/duHjIfunrEfZ2kpdDZtzuvJBkk+F/xf30jntzy+5/VFJT+Cwq2/ai'
        b'xD8nPuv6xZS0Y5+tG1kV9vbXr6xY9uHR8A9nrWuUL/uqpGdRU8MtaFtV+PLCN9/54wfuU1/6OlD/ybNvrF52Y+vVV/+w/Hdrss+d96na8/W+WxvzTdvm2ra9kXp+yvtp'
        b'9/Y4vxmj/+1vPb2/e/2poA9aXnz/84S6ea8cThlb05JcMTa+PaXY/ewvc6+VHTh2p/SVNzSvRylVr02a0Rxv/xa31uUz7896Tpc990NQ0Yfrz0wL++arp3Z9DruyWo/y'
        b'G776VH90VeCfF9eV7hpnv8X10x/g57Wq6a6H77x2yq1u9FDvYPOZoiWznbTHuFwvm7XyuR2qv+zJNf58duU26fo0ybdFhjVwTPpt2HXVbttvTxlqitdIr0n/cHCHw7cN'
        b'C68I32xU1hg/Wfr361/e3xc37vlVm+6XHzs1963M2Sc1qU9nFN7qyrjZWP3mm07Kl85s3RA5+6tRxiP/OLBSf7jjBbeUPWOPBoVdP7fv5YCqU+kb6/JO3V07bNxflM3P'
        b'lSxaH5xRU3F96wvfflD/3LcF7+fp5mT8/ae/daV//8MP2/Oyf3TSeX31b4dSflr8wie5HuffbD/lNaY3+L70ldWG237P5Gf5fP1ndU/a77LVd97a3PibrS43Qt49MW6H'
        b'/XtdJ119h46OK7HN3iH78MNJH+YmTPjBNufM5DvvPu/e+VX7hm+/LN3UfMBUfrRt42cTUnsP3n3ltgaCi1/72ZD39p80FStPGOZ/5P3MmBdDGxrS7G/8+VD4T7ODm3YM'
        b'db7wads36uOKlT+t/PSdw8ekPy/84jPtztfXF3Qo0j4KuvN67lcnN3ya9eb+YebTgQteyPpx8Zldv7//+/p/SYDrUn/93952u5/huWDJl8vud7z/MZmV/3nz0B93L7t/'
        b'a+OLyYfaEpf+NbWztbElYJKf2feLcINXyCeQ/+X6hsQftrqc0m15w7W74JOjy8bd5L/pdfjl7CfXftp/KfF60azimPfGpIb6xG9/6anXXlTX31nta3x94qTEt3+Z3un2'
        b'5odhLzePS6r8aus5j/ubtiw55VO5NTpj/fxxyXcCjt149vOdXe+v+9O/LzrX+926TbN3vzH8L7LeW09/bjN7iMMt9/F+2WnjFwyLbLrS4u+nV7W/UuN8+GiN6wd5c/f8'
        b'24Ltn/34QnPtxeRv3pak3spyWzVX7mJme9MmNDF7rRk86D2oi0YHMxK6pUPgZJQeqs3slZdVY/39guToYtDhrBImrMKIdDvLIYJ6NHPnH84iYhlE62DX+lBoZok6UD42'
        b'w3+ld1+WEMsQIpeyzaLXiV1izQ8Ss4P88gpTA83URQtrLXAS7j5IYOpLX0KD2claaMkuR/+oHCh5KFHImiS0dgxLX5qPEXOHf0J8QAzZizE89AhYsK9gtg8jbCLGqwdi'
        b'yZkt6JWDMXCxLRCCoDqVjQ270DMejCU1s5C0/pW5hkiyg0kdezOSnNNDdyzpRKfxUIRKTkATm3oFXCPt/k5wyMo2W7ggKDDguGIey/wEqRvtTM76xwQOfPOuCTrY/LwP'
        b'jSxQGhi6G/pezJwtdXGTGEmtfNg/m+P0n3zInf/r4zzyqmCeeWZYCMudCqD5QDu4lfa81PpxYXlS9CPlBd6JdxfoNyfeQRD4x33EfCva3lOgmVO0pSfNsxIc+Ic/4ggu'
        b'Yq8njCV+7AUXXsbbCvQFRjfeU+LGu7A5pLwX9veguViCzJrDRV9xxNkEJ8GJUcCyuNhM+CdQumkKlQ/+25bldTE6sJet4MCywhz4sdh/BNaPxhGluNoHlLsJYv4Y/Ubf'
        b'e6QrMNLdcUJfypeUnuc/lOr1X5eVnDe69UmLzUXfZzDRIm4n98XEwW9fksuwazTLCvMy0POsQLrlQCNhkJCeLXBhwEuvVNIRdDQaNKjpDyVwq4VMfrUkUxDf9+51Y5cS'
        b'LGHLuMho1Bu/9xavKRhqjNb8K3WmTKmTqWl9UIJc2muflkbvddLSeh3S0sRfRMDvTmlpGy1KrbXGLi0tU69KSxOh+ODBlklfsa1B6lg2n70gHnBUrM9zdCHXzI5D6OoC'
        b'jah4u7Yy3QsmzbY2NjI5v1hzxWO11DQau/Ihc+fU9CSQCI9F2bM3ZjyVmXb08p5t7xREzv9XuyS3Gx5LzpYdFN5KejE9VrH4z67/6KjiT+xv+qCp4OvPtjT/+5vPpsaP'
        b'r3+2Y/O4rB1Hmy6v/umjP1yafGjKy0Pyfr9p4s/bdLH7XKW7b1atemfl7Sqf8pHPuX7nO3mdvDO7+Nmna9SLm585PePHxn0jrlxqu+HlV3HQPXjZWx/f+mZBaWjdM4mm'
        b'1Nal5+YfGJEXLjX/dcpzY78MuPys+7b6Vcq6qa++kd7qcCCw+w3loTnfzHzX0Js4aclYE8izX177cU7ruMY1r1598f2jjo2fHNkjP9Itf+MvzwW37v7boa+qvk79dHvM'
        b'h1faGm+cKbn8/PDXyg+9/Y+guPfWG4hsqJPP8LaVZ4W/y378UD9/3fJRzsvkUjMLkztGxeNGlOfioJifweFG8NhcM0PQUYwRd7JXzzmfeMvDL57DHagSXVM9WkZHP7Ss'
        b'1LJbG5GeNQLG5l1ScmnzeOaAJpPiSSZoj0oItO5+xsVJcLO3TwKXN5E6RDYDuPt/o620ZVusJz+YDUS8avXKzLQ0ZgCnUdUYQQ1SGBodmuBJEz/d7N3sBpgvG6tpkngk'
        b'Yssd3DYn3jiyD8aoOgJi+4EdGPrfszze6NmvNHRy6rbFdNFPgx62DCwaaINKchMq6fEYKU+cszAOyqHGjnMZJRmXE6h581UHwZSJ7ZZeeGfcb6a4FEe47XlpR1aBsznj'
        b'zJ53T9yCZ4oDxp1ZXrv10/aptz7evfv83M253a/cfXXrtzN3//L52ctRU4PP/PX6x62TjqzYtV9u/uroqOvvru3Z+NSU0L9vct5/Sruu6+2mj6951yR5BjjGyu1EqF2I'
        b'm8reD0+k+25ogtJYO3S2nQJpIXWkTMxjPrlpXGxiIO5jsVlioDBmMyLolgROLF3PMJZMdtOrIboqhOxW53ioZqtyl3itJSdYIDM2lXTQZGZyHarj7TiazWwi9Wx0qFSR'
        b'm7F9P0rSGkW3/o5ygexLV4v1B7PgYt+Plkzx7v/NkpWwkwVf5BJubi/6x9jAbgXd25KGOKjtA7bXf3Mk8J9FjfRXVUGj05itqkDtBOdsz4ue0V4SsIOjH844qh/osl6J'
        b'Vq3rldLU3V4bs8WgVfdK6R01ukKNCp80/bJXYjIbe20yCs1qU6+UZvD0SjQ6c68N+4WCXhujUpeNvTU6g8XcK1HlGHslemNmr22WRmtW4z/ylIZeyWaNoddGaVJpNL2S'
        b'HPUmbILDO2hMGp3JTHP2em0NlgytRtVrp1Sp1AazqdeJTRgq5gj0OouRjsaknzEtZEqvoylHk2VOY16r19miU+UoNejJ0tSbVL1D0tJM6NkM6KdsLTqLSZ35QJXFZXsZ'
        b'qZkwTqEP+usmRmoVjezShN58G+nvyhgpPI30+sBIj5iN9PjNOJk+JtBHMH3QYNVIY0ojPZYy0vfijFQzjL70Qc9ojfTnLYz0t3aM9P1So4w+aJhqpPg0TqWP6fTh328J'
        b'qHSG9FuC7xY/ZAlY3ff2fT/+0euWlmb9bjWB34/OGvjLRjKd3iyjderMBLm9keoTdd5KrRYNHMMBPebrdUAhGM0mmgbRa6vVq5Ra5H+yRWfW5KlZ5GCc2ce8Qd6+1362'
        b'GCPMpf9isYhUQBUVsebmQY0s//8AgM2k0A=='
    ))))
