
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
        b'eJzVfAlYVEe2cN3bC0uziYK4YauoNLs0oOAS3NlBccG4QNPdQEvbjbe7BRRxlx0UUVEUl+CCoCKoiAtm6iQZM5PJTCaZxGGSCclkMpksk31ikknyV9UFBZf889773vve'
        b'S3/cdNdy6uznVNW5/gUN+E9C/qLJn2UGeejQ0ygbPc3pOB2/Ez3N6yXHpTrJCU7w0Un1sh0oV24JWsnr5TrZDm47p7fT8zs4DunkqcghR2X3nd4xdXnsgiXKdWadzahX'
        b'mrOU1hy9MqXQmmM2KRcYTFa9NkeZp9HmarL1QY6OS3IMlv6xOn2WwaS3KLNsJq3VYDZZlFYzGSpY9Mo+mHqLhUyzBDlqx/ShriR/3uRPQdHPIo8SVMKV8CWSEmmJrERe'
        b'YldiX+JQ4liiKHEqcS5xKXEtcSsZUuJeMrRkWIlHiWfJ8BKvkhElI0tGlYwuGZPlzYi23+xdinagzWM3you8d6BUVDR2B+JQsXfx2DTCHkJotkqSpO3nHkf+hpC/oRQF'
        b'KeNgKlLZJxntyfe/r+cRaVPmSTMCXrIfimwTSSM+hW9YoQLKkhMWQSlUJdvBMRVUxS5NCZSjyfOlcNsfn1RxNkrkWNjjZIlNhGqoTIRKDjnG4hZcweM2fAW3aLkBEnTv'
        b'xyGJsoEjjPj/sCHLvY9crlRCyOUJuRwjl2fkcsV8H7k7HyZ33CPkRovkfrVYjkb7EoEoMwLm8RrEGq2ZPLqpdiXfMgKaVvuIjW2JDminagJpyzB6ufiJjXU+MuQr8yTa'
        b'mGH8cvJa1IyMjqQ5Ys0I6VfuKPqzoYXcn7w6goMdLyCjA+lYEX6Ia7NDypDIcf5vCiuKTorNk1d/4Vrnyvl+phzi+WOa/5ojqAfZgijjD61LJHyvCF7k6wvlwTGBUI6b'
        b'l/jGJUJNQFBsYBycxUcSOWRydZjJQ/Ug7tr1kxxCuUs5i7Ik9/nH/Sz/sh7mn90j/FOI/Juf5oI+RlEIhWQEnIsWkC2QNAZAt5xgXekfD5VQlrAoG3fGxAbELkWh8ake'
        b'uG4JrsD7UbaMKBG0OtgI99AkuIlvqnEnAY+bF8FZtB5qcQ3rwhfs8EU1vky7jsJVqEG5Ufi0jWKDKxeq1KH0ywE3KdJCI1ywuZGfptX4NuyTIRTktxoFxYximL4RpEBe'
        b'UwIQcstwqpy4RpSfJGwoesmUSCU9IyUwGxleP9ggtWjI7xv3hn6U8UHG2qwEzUtZQbW+mhjNhxnu2pwsY+bHGXGal7NUi2M1qpR4zXn9We7c0Lkrsz/QxWlWolptjMas'
        b'r5WWn2o7EzJnRaVqtHJZ1JdzXkg67bJgT9cvnI4Y0JI4j97NtSreSv1AOj6XpCB8UiXa8Fm7QD8iZR554BKpPT6GD1pHkCHS6ALCzXKoIdy8NVGCpJEcvoS7cYeK6+F9'
        b'VSqJQKUy4MGTx3eeM7IE80a9SZkl+rAgS74hyzqrx5E5qHSdxqqn4yxOVMbjnTgnzo2z53w5Qd4PQiXpkW3QGG36Hrv0dMFmSk/vUaSna416jcmWl57+yLoqTqB6Isjo'
        b'g0KZQOG7UPhvu/Fyjufk7GkbRVoWzMz1V+KbMQF+SbgqmWiHDHnCNumIyXBggZbvUz3pY/SYeIr7eswzPyAheswzPZYwPeaLJY9ze/0AB+uxPImpEuzL2Az7OPwM+R6I'
        b'AuEGvmWjPnKCCh+EfZKQTISCUbAzVNio1/LcPJboFz4LXUTHUNBQ6DR8vvssb6EmG/3UFx9lPP3sHlyPL+9p3te841LM+F1dO2KPcHeyqD69ccEpqzfBDh2ssp9weLGK'
        b's46my1eOg2r/uMB4fBxKYxOSZEiBL/FwFG5BTZ8sHidkxuoehSjRLKNZY2UipZqN/Jw4KRGo4HhfnFImnh6ZTp9psAp0kECdj4ofIEJeoIFpgBzpdP/7cnxjkBzHkpax'
        b'CbDLv0+K0DCVBYkADo1aJ8V74ZaFmfAEKMWlFmtEiBSujUd8JoLTcGiCyPfD40fRHk4ZiHg9guYpGbbhtL0pDl+gHRI5XEF8NoIW2I1LbMNIX5TEaLFOJcCuQB3iTQjO'
        b'BYfbPEjHlDn4AO3h17gi3kynXIIumxfpWQ8XcKUFLoeHcHAqDPF4B4KOQOIuaGcC3mZgfTJ8El8gnTsRXIZuK4M5zTbLIpBpcdDGYLZCG1xl0+DKhqegwzYlRIrPbSKz'
        b'9hOQuAXKRPyb8f4JrJcPWEw6DxCQuEnNQKZBY6jFog6RRuMmxG9BcEEO1WyWLYNgTCdJvMeRSYcRXCMM7WDL4e2RK1mfHRwk6PO4AUHXJryXdXqNJJrSYXFy5HEdnEE8'
        b'XOHC4ATppOz3WQRbFQLl/qF8Mu80gk58xpuhsiISyhRwKZzQcKuQTKvkJGuWsx5uVIHCMZSwq5USDgc4B9yYLJK2IxEfVcBVQjjsXEf6dnEc3unMlnKCY/iIBTryXfgi'
        b'Z9J1gvMPwofZNHx14kiLgzO0cXBtGem6zUVAG97KFvOdAV2K9Ta4ipwtpOsSNxEqfBhAaFDAdotCsHIx+Cjpque8i3GFCPCZ2RkWK3QquCX4IOmq4vzxRTjGAA7Fl+Gq'
        b'xcWZ8OPgFCSRcTNX4B2sZ2IaLicdLhy+PgFJHLhoXIt3s54lXkB71kvh4lQC7hoXVIhPsR44VrRG4ZyHK6V6wnnJBC4a6vJFHKpxA+ymCiKbCQSJPATncdkyEfUTy/Ax'
        b'osJhctiWhvgsohNq2GqjHh134Sp8nuqADO+Cw6I+ts/GO0VJ1xQSmFQTXHl8TklwucCFDcF1YucpNzhoIXGQdE6nfec4NXTDbpWSBTQfmTsXxiPf3qy/CF4Fp4pYY22i'
        b'BzeNR169nmhTmsPSKNa4SevJzeDRtN4Nu7PvzgyczxrnCl5cNHEWvUmfr0sL+UzBGvPzRnLzeKTsDXom6+7QhuWssWPMaC6GR269LsMz66OP61nj2jFjuQQehfQWb9B6'
        b'zQYra4yKVHIpPLLvTSrZ7BX1BylrzI6dwC2heCbdyU4LSB3CGj3G+nBpFE+XYmOarvUp1qhVTOJWUTyTzm6uzz6yUozbHioug+JZ+PmGepurkTV6OfmRsICie1XDiu/6'
        b'FS9ijeVjArkcivyKTIOXrVNE6ffLgzgjjzJ6Y+2K7o6dNo41GuZP4fIoRZHX8r3Ge4t4arzUHHGqKb2Gouy0CR3+rPHwyHCugJIZe954Nz9vOGu8HRTBFfEor9dweG19'
        b'eqUfa+wKj+S2UtojSzV3U9eI03+3YDq3k0cxvYXrs9KGvruUNabNnMGVUoYY6jR30z4qZo32Lk9xlTzK6VWdLLob+6mKNQYqZnN7KJcMsdlpEaHTWWO3Zi5Xx6O03sIR'
        b'eWkzQmexxpWq+Vw9ZZ2DveA1/Lsg1rhHs4A7wqOCXkN7Qdqa10TO19tiueOUnxMTLF4eXgGs0TcjkTtLWac/pk1zyR/NGj8ancS1UtYt/UZ/N21mPmuM9F7EtVHW2Z5d'
        b'7xXUK2GNb6Wncpcp6zx+Za4PHzdMNIp9xKHctCgciQHW4QokceKiR8RuHDIjepNCcHHmsw1IMoSbGTZTNK+to3A3dEBnvkWSCxXMa/hPHiLmhc3COuJpiOPmpBtJTx03'
        b'Hp9drhLF5rfoBe6IhBAZf76gfuanonbazbrDHSepce/w4Ewvq89q1mib9GuuSUKUZuodo9d6a4oodcVL3FkJoXzhiPX1o94wPz6xDkNI3LvRLQvKkv2bm5NByTVdTf5I'
        b'UjIpyaYk33MdcQ3JlZvwzWSynaqBstjEICgj+aFnhnQyXJzHcK2IkLC0JiTibPT2aTYxr63Y6IBIJhwSMmnLmPXukxDj2NKR8+OD46E6eXEoybbsYSdfqMG7mEOKGIOb'
        b'cQe+TNNsbgXCJ+EoboUm3M7EkDQC1/rjowt9SXpaGkySE6dsiWvCCDGAH8iEq554F+4gSEShqFh8RKBcYmhsXS2lFCpDNhxTLvUbLTa6pdghknS6hUS86OSyQYVYRmVa'
        b'MVNdhNtojodrkSadBAa68YQWPdyIZ7lvDd1RxuOa4Fh83pdDSquM7Axc4DC0sKRgE+zA5Wp8DpqoWHAdyizOY0x0hla83Z/snth+lGylYqVkT4FbhqokUIm7dWw2rrJz'
        b'U+NDqeJmAmmJV9/BOuAcMqqnFeF2uv04hoy4HK6I6tcAe/E1NckBd6rpz0aUDQeW9weFGlymhjo4pSayxSfQWrI1aWF0QoVuvnrazAg6rB7p4MwCG83/HDzwlfg4il4S'
        b'kQ/U43YiIZc8ybRsLJLnDBehjpCHr0VQTA4hfUgIy6PxTnwqMx5OSBLIzGCo8ueQ4mkSMZzwLRXPlsRt4yPUE5QRxLxJRpHlSlIiRvL2MKO6EJ+LoCg2EOxbQQw/c7xJ'
        b'ElpBfhLGVybKkNSbI3nR9QQ2a9ZGaFNDKbRGEJPAR1AOrkpjeKzGtbH++AjuoOKBsiR8XoqcZkpczXBANPxa3LlCXUSkdJUufhwZYTdcElm5bUEyVBTnJRAGSJAEujnc'
        b'sFBpS6azbq1VWBJiYxPpscP9/aRvkMovMUgVyDviU3p8Gk7jJl9f3OzpryLZT5P/MFzn6QFNw3E5ie1neITLh7nh44R3V4z3fvrpp64hMlEpJ/1y1UeTPRFTYy6xwH8j'
        b'7EkKjJGS/RaHz1m3qIaJ6U47bvKyZMFBZ8EmIX6mkZsANfigGIyPwBGiWB3jocJF7L3KERyKxM6LkdBAUsJ2ONE3tZvz94OjIs1H4YDE4h9PpnHMeY3FW4lgaLaBd3jF'
        b'WeCker3NkXThG5zSD3eKEPdBl5MleCpczYfLMpaujSM51DYGMZrPhI6pI0iPM8dyqFCC2S0R4sloOK2YPMFFgWt4JHmaW4kvrhHRuIQbF1jg+iKrY76ULHaLG21P9t1U'
        b'0tFK6LZMlpEOutI2TombNGxOdhRJ3zts0GkV4DIhC3dzo5CZ8YqDhgkWaLfKEUcMAo4VE6s9QnZSlMMaaB2jGOli70x2FJKpJJ1rMTBweXDNi3DpoN623okifpibjM8Y'
        b'RePrgD2rFerVLk5knyKZzsUuJxkts7BuXOZPJh3Bp10FF0KSCzcVnhE3G+PiycajIxiuuUK7M+kaz83GVSLm+SnTCK1Qtp6thK9y3nAIGkUWNeKOaRYPaHYURVXLKWfl'
        b'inZyfOgahRqfYh0Sdy4Ejs1jHZuJl6zmYCvsIxYUgALwGXyGOVM3vA3O4ApXx/W42nsDh6QkfyP53pVU0VHZQZsCb9PeJwqfcTTM/imFs7QQk7p9Z/fq2ttJb0a7vZC9'
        b'4Y1/zq6Ots/7nHsn/c9cefzQRSkpykWryldN5cfFx9zzvVB/anZMkG9A47NJs/f6hdfMeV7y3rj6MeZ9uRuyi7//Tac6942sfy7u0p79zXsX7eR49IzdP0wPqX1xm9Mf'
        b'7f64q2vvhciw3+GvKmvvbJ81ZnbVG7f/Ern49czC4WMCtkXF/PPYdwc2VmmMi0zz2oUOXZX+1fGB1nDv3CNHQ+NKuj+b9u07gRXDAz8s21cw5VzA9O9S6r/Yf/7aNwvz'
        b'vlx4p3bPlrhZC9pX+YQfUL4SN+7lV8PLZqm+n/TK2gz32C2hO+51lq5+62/4zot7N56ff9GmP/OriPGjhjW3Kcalvz9aWPr20t2fbC7Ypmm9u+THpqCVYxQX/T+ODNmw'
        b'benV2JyGt+TSpyI+lj+7we3919fM/+H1+V+Fc4WGTfaer60zHZiyapf5mprv+dphW3L2a4ZqzRevZh8JV31y5d6vN/6t6l5DT91ko8125E7RYbuaVTe0f3v1o3F2f64J'
        b'+4N3+4WSnje/+uU7L2tcPHJ+0HpYfmhp2v7PU2+seS1j74Fb1VNHjLk87ZOl0848Zf/dFLcjgP86fcXes1/7fKqyt1LHN2laMfGWxwsCkohrghqy91XgFuKA8e651pFU'
        b'ibe6Rvpr0oJiA/xUQaQfykimqpSu8R7PukcQv7QTKvBpfEk84uk739Hr2dkP2cNuhcP+QcT9lUHVLAJdjqv5wERfNhmXz4Kd8QG+MUC2E9AQzyF7snYhnFllZUrdPsU9'
        b'PjbRzxO3J9ohuZS3h7pFVnpIm5EBbXTXDmUEH+JUayQkBK4aOl0CDfOGW5ntbaMpR3xyILGUDdzM0NkeUKayf/gQ4kkPlezJ/Q8OLtzFgwuroDFZNOIJOju/yKOZ0RwX'
        b'zp6Tc8M4J96ec+JcePJN4kja3DkXjh5X2XOO7G8Y+biR//d/yHfeRfzOO9rJOTrbkfPk3Xl7XiqTktlunCdpk5PPSAKXfnfhBCf04NjLaSBKA05KnkyVihOc++lioOai'
        b'/jOT28MGnpmoSMs8vHd835lJsIoEPf+khCBRDFBGMi05Wohb7XCdl17FiV76LFyZGx8bECudAaUk2SPxEbYbBiWlzv055DwxKaXn6OjRk/Qs5/tJKv/EJFXCTs6kX68j'
        b'QB2VA/5LoeKyKDWDbzfYlUlhnl6ZuCQyLERpFtiX0KBBUwf9iLUqBb3VJpgoLKPBYqUgMjWmXKVGqzXbTFalxaqx6tfpTVaLMj/HoM1RagQ9mZMn6C2kUa8bBE5jUdos'
        b'No1RqTMwiWkEg94SpJxttJiVGqNRmTo/ZbYyy6A36iwMjr6AiFdLoNAxxkGg2HGnOEprNm3QC2QUvdSxmQxas05P8BIMpmzLz9A2+wEWhcocghq9TcoyG43mfDKTArBp'
        b'Cen6qCeDCCQ81OmFdEGfpRf0Jq0+qm9dpe9sWxbBPdti6evbqHpo5qNziDwyMpLMJn1GhtJ3jn6jLfuJk6kIKJkP1ptDWox6g3WjJsf48Og+WT0YHG82Wc0m27p1euHh'
        b'saQ1Uy8MpMNCEXn84EyNUUMoSDfn6U1RjJ1kgilLQxhv0Rh15sHj+5BZJ+IyT681rCOqQCiljHrcUK1NoBwqfIDNcmjKEWymx46m5+RR7Elg2rQ5ZJiF/LKtexLWWqPZ'
        b'ou9He75J938A5UyzOVev68N5kL4sI/Zg1ZsYDcpsfSaBZv3fTYvJbP03SNlgFrKJfxFy/5dSY7GtS9cKep3BankcLanUbpQLbVaLNkcwZBGylMGi11WaTcbC/1Ga+pyA'
        b'wcSslDoKZR9petPjyGK3Dz9D1Ry9UWOxsun/N4gamCtE3Q9nA2PRfX+XZ7ZYHwbQpxl6i1Yw5NEpT/LcVNZ6Q+YTMKaRy6rpV67lJHKRpYzGJ2hY36IP1HHwWk9Wzf8w'
        b'3wU9iaLE6KKUxMuQkYvhpjY3U1zgceOpLyLEp+fqB4iqHyHCAiPctFj0xp+baiUB/glM7INDRzwe2UcibrzNpNObHh8x+5YlMfIxsXrwwmTMz8HI3jA47i6k0oamLKuF'
        b'eKosksTQ7sdNzBOIAIjP0zx+3ZS+br0pMEkIehL2g9Z+BO/Hx/8+RXgoBxg0+Yn5gDjXQJZ+/MTYObOTnqx26WbBkG0wUZV61Ick9/VlMoUkBqxcIOjX6fKfaOsDIf8b'
        b'Ci0O/w86kxwNiTaPdXkL9Zlwk5j1Y3zC/wBi1AyYnVE/NwivJaTn543NpFmnf+Dt+vJipW8SaX6sntqEPJYXPTJjmV7I15t01Cw35uu1uY+bbdHnaaIGJtYEwICs/jEz'
        b'VppMq6OUS025JnO+6UHWrRu4D9DodKQh32DNoUm6QaBZql4waJUG3c9l+FFk16pZR90mwWlJzkO1XoMnRvXtc6LIvuBxkWHw6Pu3AnQn5/nIrUCMWHJT788j6bx7ZKua'
        b'kWBOn9V34K+RIfvRqRJaiGQI3ygeqsOtUKjBHWRkJK6ZjqbnTBUvpXLskFPaC3ZImZEQGalG4jFXEzT6qkPRUnxUPALPw2fZBX8Q7AnxH7xLXbeM7FHHjZWNxLe8VE42'
        b'H3r7MBH2Q0VwXGwgLg+OS4wPhGNQHwdV8UkyNAWq5P6wfRo76bY54RP+dEBfZ46vO26U4DY4j/ew+jGoD3J8cBROj8HhGtzKk0yDnfg6OwZNXQ634+lxN2cacOA9djE7'
        b'fIOuLbFQ4Q9ViXGBPLKHLn6qgMsj8DXbeNJrB3VmCjwWKuPJ7htqgmMKoB6qJGisu5R82b/cRotWZkMTPvFgXNkmWtxQDWX07sPHXzYDl422TWK3A+G4aQC8ZHqEM7UA'
        b'apISOaTCN2X48FQ4xFbGewLw6QdDm8x0dXobQUb6ZMii54cxbhd7S/1XRwRBFQEWFJcIZQEqORoFDVL8DD6En2FH7YErYK8/GZLqTStnEqGcjhnuIQ2JjGYwDCkrHxLY'
        b'0/hKv8TaitlprFMavqEOlUJzAkHtINKNx6cZ92fjI/jWQPnowvvk0wjb2MxV+BmZOlQGW4PYvUFOGL7MKmUcfPA22GeHUPCcEBQSjncxeLgZn4GKwfK0K6bSrOqjBk7B'
        b'1lVMnMLCAeIkQj+t4tnxhzuczFXjdlyLa/LkiEtA+AIcsTBkRuKLyaQLxRSzK5hcLd4u3oocHwEdg9UAKvJxOS5PU8lFfT8/xF9Npq7OkyAunvzEW8VDYjiFtwtq9QS4'
        b'CW0yxC1G+DLeLmFzpnvjVjLnxCyBzElG+KIbbhPPo4/j/UvUamhxgXYyZxnCV3F1H7/gSAbUqdWcNosexKNcV3yOnTgnwgk4pFbLoA7vp8UMyIgbxzP7DF3tiQKcxsqJ'
        b'fa4SpHLE2Dsd78GnLRxCG6FmPiK+jw212LshpbRSgvIyjCeWuCOVpM+GFk6ldyVVIkPtoZ6HffgE3o9v4WrbSAauVR0fFOhHpYwvSJErPlW4TGLEN/UiQdcIRvH40mZW'
        b'mCWVcvgYroFyIhBWd3d9rE6tLsBb+3mXsp6xbhO+CWfV6mVw5j7rVuCTzKImhuOqhwwPymLuGx5uhdsEOOXLRtgfSljZ6dPPZHyN6BIFH0uU+ZxarSDg73P5zEIGfgje'
        b'NvsB+ENw4CGDhdqnmEeUQa2JyCKO6AoThpOjbTJplvOxD1sxlBLFHGDH+BI+IhaDVOEa3E4Fd3GMKLdM3GCjBaaRUii/Dwa2mh6ycJ+F4vxS00q1WkrUs5ldKebgvfgM'
        b'E+YL/q5odFEWh0IyjD8mzkKqYQwsNKZtiRegJDYwKYjYum//ge0oXCLFp6LhBmNOHD4spfdjqsBYKXKw4wuKcLVZYGrLF8Lx+PjsB6KE7SuYL86CXRseVhNiWnh/Ed7K'
        b'tAS3F+AdtCwt0C+J1vK6BgRkS/SwHVrFsuAKvFUXD6eJPQ68oSVso7d/oxKkuDbRi3m/wpFpj97iQt1c8SLXZRW+xdZTpcUN9D2uK0Tf4wx1ors9AUfDRV+Cq1mUicM7'
        b'8W5xsJ9WhlvwbbgiXpV16XCneNvdd9cdDC2FCidmHoW89KELYQLwPLsQjniK+Y/F6+DiQ05rCnFaRL9PM0RHQsVq5rPwsewBTmsjsXm6+lJ8fQFUwGXJwCtNOeEaPf2F'
        b'VujS3Wc7LiO2AOUJi4fRw/94yuVQfFAe64Zviu6xEbrgAqEjJgBX4a645EA5UsTz0DhTKnq6Ci0c8meXrpVzBty74uqNzJInuVMlhJMFAy5zobKYxcp03Obh7xvoR6zv'
        b'6oOLfbioYVwa4T8LVxArciKm8FDtgWW66CoPr1wQD3XQ+kC1InCVGIbP4y58cKBC4roMXL1SJ15JV+F66FaQxMQPd6eiVGUMo8UDjuPmgeqGdyYTfcMVcJU4B+oF10dD'
        b'A3WC+Cy+SLxgYSwzqVm4A9coBDluois3k/QFOlcxT/U07DXBPo7hSss6O4nDZlytVTyi+Wfxabx/gSszxaKpDshN+Q2PMjKcYuasQUz9jHAV7yazQp+o7dDWV0vmg8/P'
        b'gX1w0C4Bn6EFXYTVO4zMEvQLpYM1+GntAP2Fk31lalESWuAbIoEdcIKSi8z4erFtOUW9HfY8bYGKBKiKXZSC20NSFxMB0QrxoEBfIkU/dlmOtw6FylTqK0oDlsXQqxym'
        b'I4tiAhaxq6TK+KUpUCVF+PamIbhqJsGOXo2f9SS2EnJeTrLIhGp1IWL+JxbOw2WmCbg2/JEqlNvwTF+Yhu3EGLtwR5hqJA3Ti2hM7Y5iHkgbTNKXjrC1fB7HwsIFqFHa'
        b'aK0Fn+JOAlNpLOyFAyQQlm4gjypcvikIn4/AF2S4PXOxNRNfCecI2+UrCBlXGTx/s5KAwxdwUz/AKTEk9DHDPwo3g+LFUggX3M4heTrvF9Xnz+BkEZwaFPYKcSkJe1Mi'
        b'xGTlBuHNzYf0QkFEtR/2jRedd9MsEkI7wgpi+0nchJuYXF2X4m5/oqltj8/ddsApcYk26FxEk7fMmQ8lb1ZcqpIy6ubilqHqCKjxWU8iYBwhzh5OivdA1bgUKtVhcrwP'
        b'72Z5mx63aplhLF4Qqw5bPmoDYUc0SbpGpYrMaIcrXgRd6F4GbYiFzHZohvq+e6V04s8u0e69IVNI7wKSQtmRdJVeXQ1di08qoIrQ3ryOsL0iGGpSoc0ZXwqbkhLTr3yL'
        b'A5ctflihyIxjjnAYrqXa6AsUcStsuEWOkIumCBWNntPnNnKI/bZEzMVb8SUe8Z40jw4Vs7LdRL0bcIuMlvA4FaNiOBXNXoRwwi3BFlYdv9iX3ltWE208ShZdPmjx5YF2'
        b'eL8Nl9voe0HT4UChIikRqgKX9RkIlC2PiVsas0QkBDenQGliYFBSQjIJLMdkiGSqbY54F76Ct/cnOp1rYRt7k0CGSb4b5IYrxR0Ivh1N9Pa8DNeTrRKCQ4iYbg1uJNNY'
        b'NXcLLvMYpGZQbaHZ1TEQs+xpcAZve0jPSIpRShK0C4FicXEDPjwHOkbBlXy4ygo6OrmwYdDCIkiyBnY+EkBIMtQxOIQ4hIg6WzYp3aJfCVfzXOUEThk3CRpVYpZXNmMW'
        b'iyyrUx/EFaVBzDr2+cGteLhofHzaMTudVXkZ9l1ykVgs5Osv/6GzLUmsGbZ02K1Pnzl3/dymrOsNmt0LRtvNk6dEW4c9t2zeC87jjGlbHXyee/POydrq1dpJc79YM8eY'
        b'6Dg34aetK5aMOBi0qj3jncx3g/P0/3L4ER1szG/JrpcmnPrwaP6fb4z9tNvSEubxh6+em+GTnLDmnT+03jy04E818R2zX/3gxwOd+veMzZOuX1u1Nnvyr1Zm+y8dugA2'
        b'Hrq5fsOXrxd4tGaltjSrfuQjjHdf/67x8701m9/NrBZW/+v9JZ+nHop6/vOtk+L2PvOrqKV2dSG3/jXDJ2lDlPeahZPfeUY29kbQts1RPnmr80Zc29L1Se2MoB/XO4zv'
        b'zLUla5OzY+697Gx4zX3U8WbvH5wbvp3ReC5zzV2Z5if0J4+rfpcaNiU89cHsO3HOpd93Neb0zn1TYTyEcmcN+2ze5+9W7x3q7fn9xec+cj+5husMePNA3sJnj/JT74Rf'
        b'G7truuMF13+E552+l3pNW/tK1N03dq1+b9LJd/eveG75kg8zfoPB/HHAd3m1+7mli5xrnt97aPj06X+MsxzWF1gD14xx/6ao/PDVe9NeH5X1/Jk7qvnOSe+NfLPhrGHk'
        b'C7M/K9jxyZItllTrnl2bgxTe3+q8N71ZOs3r1//MNJu6jFuWv/7a6xOGv/3HWYrTHbc/PZj1gvmd92YHj7n0YcLX127OfWdD9kcje35f/PLka+cj32jc+WaS81+7CxJf'
        b'fuPdV0PTc08unXJsW5BTQc4vf6ud4f/dVvcTv1j2u94P8l/717rmbxPPLNosubzG/fZfXnI/99XRtf/8MvLm354PGnLDfcPwvFdP37tiXO5wW7Hm+12/v77r3K5VHn6j'
        b'95z3+MI55/yyti4v6/Of/uarL7vn/bgirK37Yo/r1iTt13M//8lodbpX2/vWouFdqzdcUqd/tKL40hsfzA+/0pC4sHhn9eX5H/yx7uJrcXfrnjKlfexTGf9Z6JvTx302'
        b'WeM05jfHxlcHmm5e137z44hxa9Lmv2RnN/PWWQ/r2fm/XrQoZtkHKb0rn13xbKtlekMn3PzwsxGV1/+uf/utPweql+k/vv677qO9b1t/av50ZtSH1y+UNLww9awu+nDR'
        b'25Pzf6c/0H301+p7PhOT/1i4d8WdT+JH/v2G3WvjZz6V6pi56q1Xru2dtWVS5MW/eD9dlBh15bfHdnQ8b3nnwjOpn9yLHN/4rFESXhox9rPhnOsOfup43V8/nhga5vNa'
        b'bMX1k++qXh/5w92UFz//8BfXq5af+CrlWPZPX55p+lNd8U9jBZnxZdNNlYuVWupc2L2FFYjUwEmxnoM6RGLOw/FVaQx0RVip0w1VL/P3C1IRSyZb9RX8SFyHT81SsFeQ'
        b'JhJ/dcU/KBaXJz9Uo0ICdRsrNImDCpVYhBJA3O7uvioUsqMss1JHMh4upItlKH0lKHChsDArntXHTIS9Eqig1TG+ywbWx0TDCSs9rcC3SVi7/VAxyswQVosCe3LFOpcj'
        b'7viif1JiQBxUI7JAF78MuvOpa2Z1LpPwVft44gODA+Gshezm8vmgsUY2cQ3uWBpPsLpPlSu+ujREkh3PM7zhEPG5B/qyBadEMVlYvsVKPfBKfA6u+TOOpUI7gYpbeTXC'
        b'N8X3dVrJ5xRJVQlLqtcNeGHHCDcYT6EqeyHZ4lXGL4BbJPHK63+xa4ZUAlUxqqH/biHNf/Khcv6vw3nkBaN11siwEFagE0Az6i0ozZ6T9n1cWDEO/Ug5nnPi3Hn6zYlz'
        b'5HnucR+xqIeO9+JpeQ4d6UWLeXhHbuBHhOAiznoCLPFjz7twSk7O09ee3DgviRvnwtaQct5k/jBa9sMr+wqF6ItRZDXeiXdiGLBSIbYS+eMp3rRaZzz5LWfFQwwPMkvO'
        b'O7LSI0duNJnvSfpHEohSQu0DzN14sUiJfqNvS1EKBJoKJfVXF0np0fGAqqL/uqxUnODWLy22Vi2VEm1CW9FnPgPrj6jHwOX4QH5fARJJW+oTAmleR3a1eRLowu24btA7'
        b'c1TW0RQe3bnp6YvW6Glexz0t0fHiK3Y9buwEnFUHCfMFwSx8N1Y8E2d6I/QV++h1So1Jqaf9QUkqaY99ejq9REhP73FMTxffqCbfndLT19s0xr4eu/R0nVmbni4q44MH'
        b'I5TmvTUEO1Y0Zs+zgyA33MgpXKDTqnCg9AXKJgt9phcMx+QyshMuUXELDJqPT8osXmTuvtj6mTVdSZDiNv/tLzuGTv/+HzvDP/6+e+6eD+4hxzkH372T2DSsd/d2+cqN'
        b'v4351+xZntOVDlVhv3lz+kJLdveb3+xtPlzks1f7dcRLG1sbY64c/vvLF194ecarvyjLWuX7Y9eq+D3fyP4x9/1Tb6bdqp5TNvzF5G8DJq1WtYcW5ywq1b3fXRqrudc5'
        b'7sXc5OW2mSnDVM+bTl57I/ITmafHuUsH77529tXjsRURY4quf1WvbZR5rsg8NMu/tf2FqFHG9ucjpn/c/stZdqOF5z6/fCwmadpfKy1BpzdkGprPh3W25m6DicsNF7Qj'
        b'T2f0nK6flL4lPvD3hYsOLj5d++czl8+Peeu1wE/s9KZrVW99fNBVM7Jm+3T5pQy3czHzQ4eUTn5H9pTu02WpP2SqpCxqBJBd6DGocMXdCWRnMQ2RvHs7bmF+PSYPlyqG'
        b'q8VXVwe+t1qUaqUbooj1kxV+xK1Sly4OgJ1mMmYs7pDCRdiPj7FKxNFp8y34fExSILQU3M8xh8AeCW7zDyF6zdTb/b/RU8pZIvvkB/OARFeNZo0uPZ25P1q9jzypOwoj'
        b'LodWEtLaQjd7N7tBzkvW55gkw5LJyC1osxMnDO9XYWI2PNHrB15gyH8PeZzgdd9g6OJUqmJd4sdBD7/LibdPXo0rcA2cnUb3+ckJuAzX2CGXEZIxJJZ1GUaHvi/+mwWu'
        b'5y+PeWGKy/Zot92vbMnKd96DrZmndveeuInnNVzpqHv5Pa2Zm7r/3rnhnucOf/3KWvPbrd++m+v49qen22LCb8e9+tO5kgNuC07/7hWLrnen5X28/7k7z30yZV71F58c'
        b'Dtyw/Kd/cc//1qsz0VNlx2KtL259ir1Wmsy2N3Yk0rav1dPzmvZoNqAQ70iITw6ES3RM8rLlgTxRoJsSkp2c9mU6Bq0FUEoJ89NBDT0Hw1WMLneJd0o603Nc4QDdtFQW'
        b'n4eSvlrZTWFiqC+PmRY/4N8zUKjwGVzGwx44JRYAb4Kd2sH/4AHB8yKP2xbHWNlh15lNY/zjZCjHnotHUL8G7+tXa+//5izgP6sz0p81BIPJYO0zBLplR872nBgV7SUB'
        b'WxD9IGHEfTVX9kiMelOPlFaI9sistjyjvkdKr0JJGDRoyZNW+fVILFahR5ZZaNVbeqS0UKRHYjBZe2TsneYemaAxZZPZBlOezdoj0eYIPRKzoOuRZxmMVj35sU6T1yPZ'
        b'aMjrkWksWoOhR5KjLyBDCHhHg8VgslhpaViPPM+WaTRoe+w0Wq0+z2rpcWILhopX0T3OYpZjsJinRYRM6VFYcgxZ1nQWr3qcbSZtjsZAYli6vkDb45BOdtRW+hJ8j9xm'
        b'sln0ugeGLJLtLVAnIUyhjwD6oC5RoMFXoOdeAr11EGiiKNANvUCvUAX6TycI9KBRoJFMCKYPmsQKVIcFP/qgRyECNVXBlz7om0cCfWdKoMfxAn3zSVDSB1VcgSqnEE4f'
        b'U+nD/74foNJxuO8Hvl0wwA+wvu/s+//NgB639PS+730O8LuRWYP/TRSlyWxV0j69LkllL1BromFbYzQS98b0gJ6k9DgSIQhWC71t75EbzVqNkfB/sc1kNazTs5xBiOxn'
        b'3kNxvsd+hpgdzKK/WBYi5Yl9irrmNoy6WO7/AYtJPao='
    ))))
