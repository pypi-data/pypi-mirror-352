
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
        b'eJzVfAlcU1e6+Lk3CzGEHcUFIW6VAAEkLoiiSFWWsIiiuEMgASIhhHsTUFFwBwQEFRVccEUFREBcceuc0/a1006X+Xday3Nau7xpZ6adzrRWq11855wbFBT7n/fe773f'
        b'e/rLNTnrt3/f+c53/Qw89UeEP5H4w0/HDz1YCrLBUkbP6NktYClrEB0R60VHGc5dLzZINoNCwHstYw1SvWQzs4kxOBjYzQwD9NIFYFC2yuGhQb4gNXZuijIvX28zGZT5'
        b'WUprjkE5b401J9+snGs0Ww2ZOUqLLjNXl20IkstTcox871i9IctoNvDKLJs502rMN/NKaz4eyvEGpX1NA8/jaXyQPHNkH/CV+OODP44EBTN+lIEypowtE5WJyyRl0jKH'
        b'MlnZoDJ5mWOZosypzLnMpcy1zK3MvcyjzLNscNmQMq+yoWXDyoaXjSjzLhuZ5UMRl633KQebwXrftYPW+WwGqWCd72bAgBKfEt8Ffb4XEaRFiZl9qcngjxv+eBBwxJSi'
        b'C4BKlmiS4e8zPEWAtIVMniL6zcIoYBuLf6BNbkZUiSpGwI6k+GRUjqqTVKg6duE8tRSMnyNGN9Fuo4qxEZzDYa2Bj01AO1BVAqpigDwW7UO7WNiBTsELmcxTTHXvBWMR'
        b'oQqD6fL/oUqWux17plyEsWcx9gzFnqUYMyXsgj7fMfY5/xz2yQL20UAKFAC4hkh7NMaAAkAbL3J2kkjNM97xtTe2FQ8CrrgtpFCj7oxdLDTmKsUA/6sMyfKRvD58LmgG'
        b'Jjlu/mTKMPFddxD5d4+GwG/YixOc0qYwpkG44+XEeqbDAeT8Epceejt0iTgV0Obg+d+51Lkw83Spd5hfhn6q/xn0AFsg7sg3wKOYD5XByX5+aHtwjBpth80pfnEJqCYw'
        b'KFYdl6CARxhgdhkU4T/5GVo79CIdRmhN6AyyRI+pyfxT1MwaiJqPF35MTUeBmpdmuIAwyTRMpXTFmTHJAg4FxWkYhaoALapCFfHoyNTkmNjA2IUgVLtgMKxLgZVwD8iW'
        b'OKDDsGWObTARvo6hSRp4CS8OO+BO2AwKEuE2myfucR3FaOB53IE2wr3wEMiFBwttBBJ4FV4crQnF31Z6wb0gUwbP2oio+UhQO9otASAoGdWCINhgoXAeTHMESqUfXjA9'
        b'PilntsBL76Ue4HNdEv6W7v3TqnXAeMGlkeF1+LfxUNpf079MX5UVr3szK+hTlS5G95d098ycLFPGV5ri9DjdW1kq9zidyjVR12Y4zbR4ZH+pj9MtA7syY3T5hl3i7U0d'
        b'p0KillSpvJWLwr+LejXxpPPc2iu/URxUg7n/GPy7nadVrJWoknIs3OWIyaRKgDvQTpvaH7OcBYNhmVgWtd46guB5Fh6BFZic21ENqhLBk0OAeCoDO1eiFhXTw/qpVCKO'
        b'MKXPg8WPh0OmZ3H5aw1mZZZg74L4ImOWdUaPnBqzNL3OaiDjeKwKQDFawbgyMsYPfzhp7xIqUY+kUGeyGXoc0tI4mzktrccxLS3TZNCZbZa0tGf2VTEcERNOQh5klTFk'
        b'fcrEj6Usy0gZ8hQz0l/Ik1oSOaxGnQExgf6JsDoJiwg8OUoChqCN4mHOsGJuJttHCsUDiDc2J4/Fm6XGQoTFm6XiLaIizZaIFvT5PpB49y7eX7yliYKUXdPDA2g3aoP7'
        b'sRqogTophYolrEN1EJtEeD0Y610wCC6Bl+kEdAk2StHuxXAvEUEQ5Au7jCOGdrB8EO68vybqr+lLX6qF9fB8bfPu5s2d5eO3Xtl9bnPsQea1LCJuiqw78Q5gb7PM6/Rh'
        b'FUNFBF6DV1B3QJwalcfGw6OjEiXAEXay6BCqRxV2Rg0kAZQPPY4Cu7NM+Tor5TeRe4W/GHMa81r+mNdiyrseid6QYbRyZBBHzJSK7cNfliPerQ+TyfSAx0z+YAAm++IO'
        b'sxZdC4gpSRS4THxMUiADRuSJ4U7sN2qoJpqC3ZmJLPBTWnry6p3mJ1KrAJtS4THeOjlEDELhTTYDoJPpK+nwguzBTBgLhloC/pBXv9wj0TYEN5ZiLh0mwxmgRjtZA0DN'
        b'RegwHR/KDGGmsyBsntPv8+rDjhZQVs2IspDRIlCwms0GqJWDO+ngyaVDmUhMlDtuf1g/dG1dgM2LwHITdWp56xQMCzwBL7FmgFqS0DU6gVs8gpnNAuVLjr9ffytfNp1O'
        b'iMDusI5MYAGsRFfZfLwDOpJPJ5zM9mZiWOAamfz79YuX1TrbhpEduli0lUfnJ2H40V7YzcLNAHWhSwl0SvY4HyaeBSGWQR+uv5V32J/ugW4mwZN0igR48izcAtB5dHwK'
        b'nbB/ppKZxwJZh//762+N+7cZdILfbFTJc2QH2IBOE5jOoA7YRCe8nDGaScEsqDVjLOZWO9IJs+BGtAt12SZgvFcMYbHdRl162EIn3Fs+llmMmXAn/Hfrh0rbCgVL3mpZ'
        b'RMezYGQBiw0zOh89kw4fZR7PLMc8SC/BGBgmFFEeWFajGzyvwauPWsWWAnQ2wIsO/kHmx6RjHnSkvsEPdbVIKTB6uAe208VFYCo8wsL9AF0e7U0ndPj7YzsAIu/4/oa/'
        b'NdFptm0oIWk1avCjExwweRNYeACgK2tRgxAFTVUzOZhrYMZv+VtB29YKTLgmgY2oi1fIWYAaUDmLLjATMePO0CntOcGMiQXpIYte5he7V1sFJlwaji47ckRKk+B2Fp4k'
        b'NmDHODrBxSOEsWBGpy/+mF8cMdsmiNJ+dANdcESdk/CURdNZHEKJLOgsnSAZFcpgPZ339xFv8UMnp6ykNPWOhmcc5aGEa9f1LNrLDFKjairygSkpjugiYQ7cgjqw/DDM'
        b'UniRdsGuRBOPuoqcsfy1TmHRUSYAtaTRrgmY+TX8ICfUwYDCQBbdZCbbULmAzA0N6nIssKGLAJTAbSzqZMbBI27U5i0Uo1rekbMywBTEonrGB9aNFPT0zDwDb0WXHDGA'
        b'lzE+1UzAi/PWukWMcuadnTAh2RdEEibC6E05XrrQH7c6M+BFWCsaxESaYLl9ET94FvcUiAEDr7HoMhMUNUXA5OQMeNLRyQKrxES+N4jGMJGrJRTcFFiLMeGI/HvBK6wF'
        b'YBNwppcA51PhNqzgE6W4Vc5mYXOQjTbRaSMwR/cRsZMAdCqIKtq5DLiB9jnA6/E86kRdLlgC9iNsaM8yEy1ZdEl0PWE1jy7SPli1kkUtjGaRSeVCWRcRM4lZjTX0iA5L'
        b'4NgoljbGgcnMOhZY/s4i/pbTKTFt/NOaqcwGrJpgzvv8rcnfldDGP6ROY7awIEbp8hJ/qyBWTRt/njadKSc6KfmYr7fscKWN1/1mMlUsyOkY/Bp/a/xv82hjg34WU4uV'
        b'8e96LGnjJqXTxj97RzF1LFg8b8jLfH16z0TauHrUHKYe66Fryof8Yr+/qGjjhrHRzEEWrH4n4F1+8cqkSNp4JTyGOYKV8J2gj3MXj+hKpY2f+sUzp7HavDP0t7mLZYfk'
        b'tLElIJE5gxXjpVyYu3jO0TG00VqQzHRg4VcGvpVbr/RdRBszDfOZ81jAXbPeyV0c1Thc4H0nvICO8I5yLBaLZogUTCRsSKDSwg5xc+ScnVgwf6jIjYlAFWgz1ezxUWgn'
        b'MY5FvAioYB2R4QDUhPZRFsbNcMWSj+0ilscmKYvqmNE4impXCdT/zepXmYMisPrOlFeLhkrWCGFsTuzrzBHsyZXqN/NveQUZaeO/RP+WOSECkRvcXsuvH1qioI3hwW8y'
        b'p0UY/5hX8ustH016fgxODrL0DEjOOiBL8h881TwTqJDdpc8EKi8k2pRENJucY2BlEj6T1aCK2IQgVIHjyCHpYh3aMh6eQrUU9oUj8SnHzxWzNN3ErCkWguBGV3zKScd0'
        b'S08PtI6eBmzDCUcaYRnq0AZr4aF0tCMpVgJkaAu7Bl3RUwqvhO0ZsAueJ5E5w3ktwdoLt8DNwtTOKfBygB8OZcuD0T54GMcrimyRy3RssmjktAE3boRdJNY/qQgH4TJ0'
        b'hSN0o8CcTcCnq5TfAhCZbroWFCc0rl2DT2yucQ5AmR7v7zIBCI5mF6xP04SQFXcRU12hg82hthdITyc6jDZoacBcQw6pWlgTHAvb/BigHIQ2WSXOqAofFggwmegc2qyZ'
        b'SBapA8OWZsAj6KZtFDUebrA9AB/A6BEXw7wNn8hixcBDJcI/d8FqKp0riuE2egTBfg7uWZcZCc9T2JLRrvkaeI6geBigblRlKkAX6OkEnVii1mgogcHwguylsJ02j5eN'
        b'02gwb+FR7B0cVqGrqTZyfs3N0Ggmk8H1AO1J1cdyNnIiKIZN6Lg2Dp+tKhMF3jgnrrKIwlCbo6BNN2D7EM1ksnsDwMTeZAhDu+hM7A+rSrXxeFYwqlbOD2CA41Js39AW'
        b'VK9i6Vx/7Ms0k1nipADaBE9nwTZ0hIIIt5p9NZMJjAcwiwuyRwpxkXa9BVXCU6PxGSZBAsQ+DDwGD6IOSl3seddqJmP9gAeBO2zMwUQ8ZfMmHRWRaG8AYQmqSET74WnY'
        b'JgaKCJFLCdxFCeuFtqVq4EWy7REco7iafAx0t+BVOBqvLDTGY+xFQIRuMPAAPFZkSyQjq9DBCD4+NjaBZC+qAuCmBcL5M9kvSOWfEKRSs3LYZIAn0Ul4ws8PNg8JwJYD'
        b'nQjwhHVDBqMTXvAUturbPV3xeWt3nOmHR48edQzH0ri61QFLY/yY6fhwS913A2rGsrEQnUpUx4iBOJKBLcPQQZUnxXlc4VAe1aLdTpxNBFjUyIwZlU2nTTPmoy5MzTZn'
        b'oecio8Lxb7Ugy/W+E1HX8tn2STeYAFjrQz3O4BWwjccgH8CzGEBMmS/cVSj4txNoA9zMO6JjBTY57oNXGeUMBwHE8qXY9cHTS9HFInReAkiIMUrGCTHRxhVY6LuK4CHc'
        b'5UTW7GRCUWcSXXMOujLSEZ+fzzs7whoWiJYyy2CLQvB9R2fBozyqYKzyIjHe7TrjnQJbBT6f45151BSBe8heGxnl0kEUDinctB51+S21cug8RgzeYEbAbWirAEc7bEF7'
        b'eHTOKgXMGOwBGgGqwfGTYCRaRs5yhBf8ZE74iCGawsS4ox0CPYZpidnHWlqgILDvZ8aj8kxKxMGoReSI/f8lZwU+uYimMbHwhFYIas7Dregk6goMdOFwOCRyZqZgHblC'
        b'Z4V5STFb9ipd0DnsZUSjmVlyVCcg3A1voI28b1gB3QpeZHxGICG0QGXogpVPgPVygWG7GCWPzgjKd2AmLHMcpqA9IncmBB6CZVSZWXRyNtqNFSh8USAIjMHjCWzL4qSw'
        b'0kVeEA2PFzJAjIMNWB2LnRylwjUbbHd0nvQEoVY3o8tbVRK+BivVQcnCFbuuJL4cqdj2dUMs+8aF5Ve3/Og62Gmk5OiyUXlzZjke2hq5M1I/Lmf6scjyumWj3h0nGeyk'
        b'Hjdd5vIbjzsN8RsvVnz29s3S4hdUCS7bVpeYNm4MkVQG+TBjmj1jdpbs8ntT/0tDlGSSolAlf/PPnynO3owarGruDFP8vP+l+9p7ST8mZu7JOJN8cpSxwX9J05I/xHyW'
        b'UNZ6985Pr6wa4vL2g1Vrsj6/Pvgv+50SPm+5nK4+u3vY7UZZgzv32etWpWZNym2t6Yuw1bVhAQ+6Xr7iPe63M851/fB+eXXJSu9tH+lGhQXK13x/wiPmvvP2Ka/vm7t2'
        b'QXJJ3fbvj0/7MzevXfbz3Z9bnQqmLF43Db66c36qW1vnnzfwGa+cdDxz9W9VJTc/PVVx3mfj7aYZwOkjo/7HgPtbJ4ceSRjhduty8xvqv324Zbf/ybbhb5+ftKiia3jG'
        b'u1lfH952fFoO90Xtw+u3bv1wb1/mJ7kbXy0pcf/To27NyXmbvvlj8NHXf/549KqeIdXy4Xf3lyxodu9pLijfXFIxJmLa2bI7nq8GPwI1+Qe69xxRyWi6JtaG9bIyMJHk'
        b'vWqi4S580nWErdjIDldYSX4YbocNIQFBsYH+qiBUE4gqABiqFKNjqGklbJlqJZoxo5h4m3mJ9oyPkO4Zh8qtXlTKT6LqgCBs4SomkGO0FO5g1TGetM/DCXZqA/3k02JQ'
        b'tZYBMrzvGnRsFu1Dh5agq9rYBH+4D25NcABSMSuzwkNWckC3QezhSBYGVQSierQbR1lVqEYEPKaJ0IGCGVYiizp0eYU2SU10rhVdKGRmof0SlezpvMPzHirJ8/uf5Crc'
        b'hVyFldOZeZ2Qfacpi9X4IY+SMVLGk1EwMlbOODOe+CkXyRh3RobbcCsjpx9X+rf3l4x+d2btv1mpA8tIHynw7yGMKytjxYxYSlJfQ/AKUro+u8GZGcI64zbyXXyBU4An'
        b'6TBFX9D6JEmej52K4Zx68aNLvQjs6RLPmwOkS/xJLADrI+0psWAV8fLdsD4gMT5I4EqAFODToAOsW4vqVAw1IUmRqFMbG4ijE+zfj5Lj0wHYDA88E5g69caO8YAGpiQJ'
        b'D55Nw2c5PQ5U2X8qUN2iEn2fhxeXK/v8mUdYySt1/W9N6FXMGotBmZAydWKIMp+jX0KD+k3t9yPWquQMVhtnJmuZjLyVLJGhM+cqdZmZ+TazVclbdVZDnsFs5ZVFOcbM'
        b'HKWOM+A5Fs7A40aDvt9yOl5p4206k1JvpFzUcUYDH6ScZeLzlTqTSblgzrxZyiyjwaTn6TqG1ZjlmXgVMsbUbymaGhVGZeabCw0cHkUui2xmY2a+3oDh4ozmbP5XcJv1'
        b'BIo1yhwMGrmlyso3mfKL8EyygC0To24If/4SakxDvYFL4wxZBs5gzjSE2/dV+s2yZWHYs3ne3rdW9dTMZ+dgfqSnJ+abDenpSr8ow1pb9nMnExYQNJ/sF4VbTAajda0u'
        b'x/T0aDuvngzW5put+WZbXp6Be3osbs0wcH3x4AkgAw/O0Jl0GIO0fIvBHE7JiSeYs3SY8LzOpM/vP94OTJ4Ay2xDpjEPiwLGlBBqoKGZNo5QaM0TaFLRiRzOZh5wNMmp'
        b'h9MnXtOWmYOH8fiXLe95UGea8nlDL9hzzPr/AyBn5OfnGvR2mPvJyyKsD1aDmeKgzDZk4NWs/7txMedb/wlUCvO5bGxfuNz/pdjwtry0TM6gN1r5gXBZQPRGGW2z8pk5'
        b'nDELo6UMFqyuMt9sWvM/ipPdCBjNVEuJoVDaUTOYB0KLXkb8ClZRBpOOt9Lp/zeQ6hs/hD92Z3190WN7Z8nnrU8vYJcMA5/JGS1kyvMsN+G1wZjxHIiJ57LqeoUrFXsu'
        b'vJXJ9BwJs2/6RBz77/V80fwP050zYC+KlS5cia0MHjkfXcvMzRA2GGg8sUUY+bRcQx9W9QKESWBC13jeYPq1qVbs4J9DRPs6ZMTAwD7jcbU2s95gHthj2rfFPnIAX91/'
        b'Yzzm19bILuzvd6MJt9GJLCuPLVUWDmJI90ATLRxmALZ5uoH3nWfvNpjViVzQ86Dvt/czcA/s/+2C8FQM0G/yc+MBYa4Rbz3wxNioWYnPF7u0fM6YbTQTkXrWhiTZ+zKo'
        b'QGIFVs7lDHn6oufqet+V/wmBFob/B41Jjg57mwFNXrQhA13Daj2ATfgfAIyoAdUzYuf6wZWCe35d2cy6PMMTa2ePi5V+ibh5QDm1cRYaFz0zY5GBKzKY9UQt1xYZMnMH'
        b'ms0bLLrwvoE1XqBPVD/AjGVm84pw5UJzrjm/yPwk6tb3PQfo9HrcUGS05pAg3ciRKNXAGTOVRv2vRfjh+ESryyNmE8OUkvNUDVn/ieH2c044PhcM5Bn6j+53M0BOdc7g'
        b'6ZuBBOFqY+UkFojTx5Kkf+BEUZiQUnd2Inn2PRIQmR54R+4DaIZqEdqSA7vwQO3MaWCaIzxPh5rHOQCFghOR7Lsuay4Q6iLOFcNKjQc8aM9+Z87NpnlzHdoITwaQY2vf'
        b'I6s73A1G+UqGy+FJlcJGykJGuMJ2VBkcFwsvoINquD04LkGrjkPV2kQJmICqpQEZkTRTPAZ1Dwuw96FtwaTbHTaKYAc8b6MVJHHZ8ED/XDjciqpJNrwSVdIlYAuqgud7'
        b's94k5z01nGS94RG0hV5YBHLoBqqUpAag6oQ4NQtk6AoLt8NdqNk2mmR0UDOGC28Ri6q0+FCOaoJjULVorhH4uotJumQpvYDx9Xe2D3KbpqWFDjtQRTCGd2yAZDo6Lbb5'
        b'EVi6olf2WSpJuKNITGCACh6H7eT2eT/ahAEnNILHYO1o+2i0QynsTa4h8PCx6ZJIGTxOAURlruhSQBCqxgsGxSWgikAVOgL3SsEIdEAMj5vQDiH5X8mH2kfFJqDtgYMK'
        b'VVLgNVgcEqulCEyIcH+GcVGojDIOc7VMSEkehN1DNCmwI5RcL+wD+tlwI+UDJtIl2N3LKg947gmrUmcLSe7TsBXWaNDxvFAJvUXImQ1306uFqfCYDe12wEP2mUNACOpO'
        b'pYxbifai7v68RSccCGs7HSlGuOegS1/GFqBNhLOD4W77dQbcO2qYBp6zSOPRRcDEA3gWHcwScta74S6TBl12hecAvY3JDQmhFQCoLDEZVcI6W39xiElVSenEGLR5ikZj'
        b'EWlRB2C0ALbBvRbakZHso9GgDokWNQJmPoDnYfd0+60x2ues0XAiL7QfMEkk830FVdGu8bBpJJ50ThIPNwFmEYAXYRc6IWjYXld0Q5OKrmnIBcoxkLswweaK21c7WzWJ'
        b'ARpCwuPAJBKqH3zXe4FA8Xyio97bFCWAjpTCxkyeTK6cNAfMKTLQkTdfdANKcaAIWNIVLrHTgEokKEkF2j5GC7utmKbVAjVlqJ6Fe1CdPyVLPCpHzdogtT9RUnhWDFyK'
        b'hywSmWzJlM6icGeSgZIAMaxB18UMPFwIK1VCLh9ds8IjhGKpaKtAMQ8vOsl9JbxJKYY6pQLFVsA2Wouq9YINz2ocVo1yQefgIdiOV6dkOpoyndB2GNoh0HZUIN01LjqP'
        b'EhYr8gmBskM9Ba3aAXeiCvvqWRnPqCqsWidwbQe8iY5o0NbIXgbgXeupFq+FN9Cm56lxI9xC1RiecrPfbaPtxRp4M6SXZXAnbKWQKMegg73qfQQ2PqPf6NIwysewuEUa'
        b't3CNcJuYM2aKgEYtOo9OaGPViUFYl/0EhS2Ee0VgBCwTw6ZA1ClcBV2McwwoiiQlhupYMRjkwMIdOnsBz7IoF+AdX+sAQtLjFy/LEiy7O9pTaOflqgLCyRSJoGwNRSVa'
        b'DtPkKQEpRrvpRqPcrQFxaq3aP5GUBLtMiswWGWCT2jaOAHEGVs7sfyGLyQXbimG1GIyIF2NbeylQqELugB3owkB3t8psoLRKnGG9luIf7SkQD6vqjr7Owx/uW5wpwZZm'
        b'73p6zRQN21O06PyYYG2fa2w93ESNVhK8MvXxJS+q9J/55Ip3h1GwBteiCU/s940KVCZcOR5fTOtcPdBltFsrUKQcHsZUwXpUE4y2x5PMvZYQIhTuk8bC3aiBQpOTlITh'
        b'iAmMS1JLgaMGdWlZ1IjKXakfkmJbcq73VpTeiL4A90SIXIJnYSWlOfy2cNSJKu1XrWjnYHLbutxRuHU/iol42H7tTq7c0QW4I1vk4pZP/TI2Wi/0Lw+AN+ExoURgPLyM'
        b'aijvPVEDvOTIEluNri0AC8SwEasZCQ1QdynaToxJ0TpsSyB2Z1S2j6ItKx0X6ki1J2rGJgttg5XCbfFVvNQVtBvPKJyvBuoUoRxm/eBBwNX7dVJroNAogwBVVT9YR6rL'
        b'HbPQPuwDYA1IC0wQlq9CrbAWdnnHhIjwr9Mg3wZ32VJwz6QsC4+5gqpjk+fBcyEL5mPrRCqmg9R+GH1/+xXwAqIW5YGLYgjalLDJMYFe8ATpxPqiXTgPYfmDN4vdYHV0'
        b'Ib3xve6LRQRcFuO4SFExYTmgnhF22dCh/tRTjLPTDh2HW+2Gbkr4ZNg10SKF+1YAJpl4hkvRlOtoA7yINpM+Bm7ypKbuLHYCW2yk8MAL3jBgZ1Qei3aiy7nY5dXB8kL8'
        b'qMaWq20yPCuB5zLmWzPghUkMZrx0CRa5o5RZMrRzDV1z7GhhyVHALicl8AJs1vZ6RWnaEnSd9V9soGo8cwbq7GfGo2EHtuMYjUtUJeCpINiuhRth9zOeoGKY4MdPJaoo'
        b'nqgdVgqILllGAxEM84URTwUitfBibyAC9zkJoUL38uS+gUgxOmePRCbCJpVYcBon5OGayQUitAvTKw4jtwjZy8TOowtoh0aBrk+U0gjEABvNVORKrXCzZmIhkxMHmEgA'
        b'm1cVC+A2DgrA4GJvrVtJHcG5F+ERFSNcobeVEJZNwEZ6EmDmkqqXZszsKNwVgU6NdcQxZyVmemUwqlmAOpxg58QJ82Ko3M0chSVvvnrR/JjA/tKE7dFhOdoPr48S9KBt'
        b'DOqCrRjUufDEOrBu8XDBWMLWfNg6GXayPvAMYIcA1IK60GGqav6wRQRbsbOYhG6WgJL0CTY1bjVineNJebgCHQue70cu64h1TO23earaAe6Bh1faSOkRbq/OdExMQNXq'
        b'RXb1QBWpMXELY1IEXGDzPFSeoA5KjE+SYLVDTfAU6pDDrUthd6/rroKnUTetpp8Jm4JAUARqo4TzhTsXYqG9Bm/ANgnxDQC2TvXEs4gpikKX5vYTMQaewSKmR/XUpHqk'
        b'GbQpqqelaxQ2QYQyUT6k3rQIXSSlCbACoEvMxATYLviy7lgNjy5aXKSARbV4XAXzAjoWSquHjMZF41l+K/76LxHX1qf8rsZzjmfp9xP+3x81EV0ax3POd86ta+k4/cal'
        b'kE2+V8tXxk98d/a+LegN85tjPU6lfnB6odf4LX96eezBmMmdP26ITvIOa8gJc0uYvmbSP74qvfNK2vVGSdXL1offt5f8/FFranvJwiuq0ycOZB2aPmHN1tSub1+Y8sbE'
        b'd1Mf3Z3cPvVAa+dbhV/0fNj57fsfRu3Z0q6LiP4o7GrB6vekrR/WrTrWNTUdbctrTq1uf9Bds/xQrujQ+i9TLu4an1hwPTqz6bVk3SF/0fb6X3484xG9rDnVY9JPblMz'
        b'Pr/8p9Evj1/PFrksF92ectv67guGtMsyzRTthZZPdt8bdHFc48exKVu/UbY4ffNX+DtZkeNyh9vBa6riuuM/sAW/d2Lty12iiPdfmnZ5xK3p7PvXxtzp/PTQsrnv31cc'
        b'K62tujr2s+GXp1ruby1edHmhJeK9H7ssV7cW+972sbhs/deA24MtbzvdnW24P2NcY3Z32+rDb7auPrrf682ST1zKI/zu1d5CGR6d0S/PCL4n6Wy+tfeW1ys+g4vjv8ro'
        b'+Kunz4wbhr/5+z7sfOf4sUXHzpkKlm49dC/76F9e9/bnJnzzjUfR+tCqjfc/KX0l8Adxrvad1/dJh9+e9ZXW/cb12oKtX89eX7jk/HuykrNuod++ceDzztaznRH3Xx1/'
        b'9h+vtSZ/XRutnvFK2PrPJ7XM/Wn73fyv5lc88D0c4v9m3bvvnLmn9p3loP7Au2yty905g66Nzd3xoLZqX4t8e/jhDR8pVuf8/tI/IkZ3b4ZHvw7LKV7t9OORsDXz//Lg'
        b'd8avzjBraz0Oc1le4ffbWn56MPEjjbtX7O3QT98yfzo2q25KZfnbGz8oeeGS+WR5cmvUB6JzTVHXGfUe+YR26SvfPmgODX7tzdLKGw/XD78nvi4971EaHPfLww6ndbGW'
        b'8Krkf/3r2b+9ub/x/dT7w7O9TxV/du3g3Smfn/B1SPzhdxumDJHcXPiPvzs1vKV8+9t7wzemjt33b2+Evl2cdHPQxW+OhqT9UHnbd2bDFwXtRxLUX8zOLo1ZmNDwc+qd'
        b'uS+dcSgMN28r2PntoHU2W/QPiR+l7/lghcOpWzsKPlux4t4f25ed/az7VvatIwd9jF9nr7/r5jRt74z8hLupHwfIkxpnnPV/7/t/8/DfuUzf4qovLdZmjs96sP29hx4P'
        b'fb9LPmiN6GbujdT5yovPZETPiv7u3L2PH/xxw4+z1nw36b3PvloS+t74H3KS97z1C7wZN2Wy1fLeL0U3X5A+XPOwTes779w9lw8ebNr3zk6VM60siJo9VKhVCMTWiNgp'
        b'2B6MIx8veFEcswodsNLIZSPajfYEwH2w0j9Ihf0BAIOWsLApZajw+kPtGNT0pGACBxWH7EUTK2f5WGmMVo7KV9u3oQUR6CSsY9WKGbTwwd9YrJ0/MdCvT00EtnUddO3x'
        b'qA3VPa7WIKUaC9S0WAMehpsoAugmNoqHemsjKqaa+lRGFMFTtF4joiAyAG1kExMC4/AhBG9xhS3ChvGylbifIBOq1+KIMBgbcWlR4Xg2qBTVCohd8cGnCAzV40IQF7h5'
        b'YYgoG58YttGF0YkxaF8fP47aZ7L+6Hqk0HlmProaYCeYFJ6Ro9OsJhZVUJoulKIO+xsj5HUR7Uz6wgg5q9IiFFSTD0n5bJUWB0UW4lVQ/Ury3tF0sagwUeXxz5Z1/Ccf'
        b'Kqf/+jrPvOGSZ506MYSWi5hJ4UOpbLGYEf7KafEH+StmWEZBSkZYMf5XzrAsywz0V35X5qygM4YzpFiEfB9Ky06kP8skCkZoEUaIN+B1yMqPXFn2F7GI/VksZn8SS9gf'
        b'xQ7sA7GM/UE8iL0vlrP3xI7s92IFe1fsxH4ndma/Fbuw/xC7sn8Xu7HfiN3Zv7EeZG/ZX529lIwU7ytmXJmhjKvIGcOrwDt44928H3nS4hRXVv5Iiv8luBGspI8IfAqW'
        b'QOuOoZRLcA9LMCQfMSvFI6SslB2Lf0nt5TIKOleKxynod2+8myfuH47xJO3SR+wjuRjj/ItcrKA0FG9gv5W7kh1IoY0Cr0fXYDmXXpaoRD1iku3sUxzzX2e2iuFce9lN'
        b't9pF2EziELBx7DcDlNEQGV8Az+QFxCxX0kIaVKMmwRsAwy0idMUbXXjmDTAiM5FkWRK1Gcirx2Apq2eWivTsAlqL3eNKc7e0roWbw3H53ENfIZtL5Y+zl6kY9EqdWWkg'
        b'/UGJKnGPLC2NpL/T0nrkaWnCO8b4uyItrcCmM9l7HNLS9PmZaWmCUD95UHxJSEjK/WheVwZkLA2181c7ODqjS1bHQaRSSM1hHb4poe8OBqPDUkk0LFMxc43DPypl+Eg8'
        b'OS/kjxHv/EsiinSV3lmx7+VEvnvQ9Q/A0SLZpPOWT15y/Ck0amfYhqSY5R1NS8YUfLo/4JvXw2JympKmdT2K6/rReH1S3fFdG7d89WX796td2l64/H6x7fv2bW73U2pe'
        b'GZz1zhsPPp25z89x7Aqmddj9sA/eTRt+Y8vI11weKBvzVJ82LU970b+24P435rqxB7z9V4f//rUti058tsNdXzycs0RNC20Uf+u3TuuZnPHG6Y6Fl02+q0wzpbdmKTrR'
        b'UF30hFd3ZG469LLntOphhUP4r6YPuRU+5MNxgV1OZzpaF6PwyR0ValOmw9VbaIazpXzMxILbthL92IJNCw5+4u21YszvY3a9+l226puGnE92fTFlYXJTypymB5LUtF3i'
        b'w6dUqMH75oLxm+P9kxuWB1fm3t6y6KcR30QNXsZeyilj89Jc7kbOZT9deavmZuraVVmRLSqxlRy5FgejzTj8nz+KAUwYyRA1ThTsaUsgvCm8xim8wjkC1tvf4lTDk1aa'
        b'pD2Wi4+4/tiS+48nnjCh911PX9glxiep3eFWJRm2E218kUfb9bAtJlHt11uJ54ZqRbBDC69hVaAa4f7faJ2lNKB+/oNaXSzXpnydPi2NmtwSQF7VYNmJjJKYiUfEMMhY'
        b'V9ZVxkqJaXzmQ0zl0x9iOp/+EFOKP1KxYOhkD7CFoyZa+qOnjE1SMH4MKGXXDWE4rz4miMW69MQAuf33kInhhj5WUrI5sUe0si/oqwFMEmXukVGwAm3AJ+FKkgBDFUnx'
        b'sALWOADnYaKRsDXCuPY1McMb8Ej/ByNHvjrBeVOk67Z3S7OKnKwZW7d9efQa3LLqa79OzYNby+4kTLjxl61bWz5aeuFfP03LvfGgEZYWLVh8Yn9a059L/7BAKxuz4Msv'
        b'p2osvxlW8fUVbsyEgi8muOw8vq4760DEH952eOWtoRfDDqschBAHx17l9K3MJJq1cgCO8NxKeJZFp2EjuiwI+Hl0Q6xNUqNOMixJzQI3Z3gRXRPBo/DcehrOjEPbYNPY'
        b'IgE1kqKC1RQ1d5GPxslKT9tn5IBUoKJL/vYCVFgPrwgvOTenrNP2+R8FHFU4OinDh7yYUNpfCOvH9P8fByaNJ//fwGZ4kFan4qjwcGxAHKoKlpAUM6pXwKO9quLz3xzN'
        b'/GflR/yrymU0G6125SIeSeYkt5e5BopAKSgVl3LDHgu8skdkMph7xKSyskditVlMhh4xuULEvtiYiZ+kOq5HxFu5HknGGquB7xGTAosekdFs7ZHQV4N7JJzOnI1nG80W'
        b'm7VHlJnD9YjyOX2PNMtoshrwjzydpUe01mjpkej4TKOxR5RjWI2H4OXlRt5o5q2kpKpHarFlmIyZPQ66zEyDxcr3KOiGocIVbo+TEKsZ+fywySETehz5HGOWNY16yx4n'
        b'mzkzR2fEHjTNsDqzZ1BaGo89qgX7R6nNbOMN+icqLaDtw5F3Y7gJ5EGysRyxsxzJdnLkVpIbTx5EejkVeZD0MkdSKRx5SYgjSWQumDxIwMwREeZI+S1HXtTmiGJwJNfP'
        b'kZd1OPKaEUcy2RxJ2XFEmTlybcIR4eQmkccU8gh4bBEIdwb1WoS5D561CHTEQ1nv2/k9rmlp9u92w/pweFb//6lEac63KkmfQZ+oknFEpUjooDOZsLmj0kB8VI8cs4Kz'
        b'8uSuukdqys/UmTAX5tvMVmOegcYt3NReEj4Va/TIpgsRygymF3IxEEtlLJE4UOrpytKo998BAqzhjg=='
    ))))
