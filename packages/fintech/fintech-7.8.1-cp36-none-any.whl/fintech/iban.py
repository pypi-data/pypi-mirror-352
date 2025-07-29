
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
IBAN module of the Python Fintech package.

This module defines functions to check and create IBANs.
"""

__all__ = ['check_iban', 'create_iban', 'check_bic', 'get_bic', 'parse_iban', 'get_bankname']

def check_iban(iban, bic=None, country=None, sepa=False):
    """
    Checks an IBAN for validity.

    If the *kontocheck* package is available, for German IBANs the
    bank code and the checksum of the account number are checked as
    well.

    :param iban: The IBAN to be checked.
    :param bic: If given, IBAN and BIC are checked in the
        context of each other.
    :param country: If given, the IBAN is checked in the
        context of this country. Must be an ISO-3166 ALPHA 2
        code.
    :param sepa: If *sepa* evaluates to ``True``, the IBAN is
        checked to be valid in the Single Euro Payments Area.
    :returns: ``True`` on validity, ``False`` otherwise.
    """
    ...


def create_iban(bankcode, account, bic=False):
    """
    Creates an IBAN from a German bank code and account number.

    The *kontocheck* package is required to perform this function.
    Otherwise a *RuntimeError* is raised.

    :param bankcode: The German bank code.
    :param account: The account number.
    :param bic: Flag if the corresponding BIC should be returned as well.
    :returns: Either the IBAN or a 2-tuple in the form of (IBAN, BIC).
    """
    ...


def check_bic(bic, country=None, scl=False):
    """
    Checks a BIC for validity.

    :param bic: The BIC to be checked.
    :param country: If given, the BIC is checked in the
        context of this country. Must be an ISO-3166 ALPHA 2
        code.
    :param scl: If set to ``True``, the BIC is checked for occurrence
        in the SEPA Clearing Directory, published by the German Central
        Bank. If set to a value of *SCT*, *SDD*, *COR1*, or *B2B*, *SCC*,
        the BIC is also checked to be valid for this payment order type.
        The *kontocheck* package is required for this option.
        Otherwise a *RuntimeError* is raised.
    :returns: ``True`` on validity, ``False`` otherwise.
    """
    ...


def get_bic(iban):
    """
    Returns the corresponding BIC for a given German IBAN.

    The *kontocheck* package is required to perform this function.
    Otherwise a *RuntimeError* is raised.
    """
    ...


def parse_iban(iban):
    """
    Splits a given IBAN into its fragments.

    Returns a 4-tuple in the form of
    (COUNTRY, CHECKSUM, BANK_CODE, ACCOUNT_NUMBER)
    """
    ...


def get_bankname(iban_or_bic):
    """
    Returns the bank name of a given German IBAN or European BIC.
    In the latter case the bank name is read from the SEPA Clearing
    Directory published by the German Central Bank.

    The *kontocheck* package is required to perform this function.
    Otherwise a *RuntimeError* is raised.
    """
    ...



from typing import TYPE_CHECKING
if not TYPE_CHECKING:
    import marshal, zlib, base64
    exec(marshal.loads(zlib.decompress(base64.b64decode(
        b'eJzNfAdc1Nm18J1KGYq9gTp2hyZi74UiHRUsuCoMMMgoUqbYC9ZBqqKAWMAuoqCACvbsOZtN2WTfZpPNJnzZtH27yW42ebvJt3l5+1LeufcOyCib7Pu+/H7vwW9m8H/v'
        b'Pffc08sd32e9fpT0Wkwv63x6y2Lr2Ca2TpGlyFIeZuuUJtVmdZbqkCJ/bJbapDnEtmitIa8oTdoszSHFQYXJzaQ8pFCwLG0y88gxuH2R7RmzdEmifmt+lj3XpM/P1tty'
        b'TPrlO205+Xn6KHOezZSZoy8wZm4xbjKFeHqm5Jit3XOzTNnmPJNVn23Py7SZ8/Oselu+PjPHlLlFb8zL0mdaTEabSc+hW0M8M/2duI+m10h66Tj+WfTmYA6FQ+lQOdQO'
        b'jUPrcHO4Ozwcng6dw8vh7fBx+Dr6Ofo7BjgGOgY5BjuGOIY6hjmGO0Y4/Bz+2SPFmd33jixmh9jeUbu0e0YeYslsz6hDTMH2jdw3ai1Rh865yaBKzOxNvMH0GsgRUAsC'
        b'JjODZ2KuO/0dk6Ji/FnRuoKgfx8czuxj6R9rfAdiKR5Lil+BxVieZMByfJwSs2p5sJZNilTjM7/d9hk0bZU/1GI5nKC5FVgZSAuwIjoBK1bTqtIpK6KD4rAMy2LisSRG'
        b'w7ZBpcd6PLZU7Bq8Vcu8GOv3aeS+3E1j+zP7BnqowGfLsd3De0U0ASyLWRUNJdAGzZOxOCg2AU8ku+Ox6FUE2nWvydHxWJEYn7RqMg0UT8HymBXRsasmB0fHBCmgSc1s'
        b'cGzwTN/4TIWTGip6+XRTI+ofsCPbx0lwRbGSCK4kgisEwZWC4Ip9yr4I7kGv5JcIXicJnqlxE0cPjaobkJxVyMTDP4+WXAhdbRj+xrAI+XD0CnfWj56FRh1OeCNhh3z4'
        b'eqCa0ac+NDs1Ybk1kOV60sPOScPV/3cAW/xpzL9P+r3y/tQ5EQNYLsfi96PrFHfcaPbwlj1fC6vYu0c+Hr7qD76nfBWTP2UNfq8Ne5TmxbqYPZgG4PGGWVgKJzZz/k2e'
        b'jCVTooOxBG6kTCYOVAaFxATHJihYnq/HAmzKsPfn59s8yeqlYLN3MTzNoCZ1p30QPe2fl2S1aBg0rmVYyqAYTuFpO5dBd7iN9VaLG83ex7CcQQk+2i9G4PZiqLPifcbG'
        b'pTE8zqAMG/PsQ2kkAc7COStUqBk+w2sMLzI4PwqPyVU3oAZaaFDJAmMYXmJQvzRBjOAjuI7nrYWExUMtw0raasxAMaLpj7RRq5ZB7VCG1QyOY126QDsMWrDZatcwX8ID'
        b'TzAo9R8kgT3AJoXVW8uioZZhA4O6pdBkH0IjfuPxgBXb1QyeQjHDWoIWifcE3ngTGt2sUMbYIKhkeI7BGazGp2IZnMNbcMeqUzI8OZnhBYLoCy1irxxs2mLdrmJEszKG'
        b'NQwq4MBIsWgJXoQ2qy+tbqKT8kWnoWW/wFw9Zgi2e6vZdOhg2MygAY5vFAMbSYmu6ogX66YSQrRiKFyxc8HEI/nJUEqsK4xQuDN+8J1i+1fSNVZsUzCsQjpPFYPKCLwk'
        b'aX01PAHb7Sq2EA4JUp+CUxPlaQ5jHdPhHQ1xG1oZ3iY2xG6TRGiBq8TX7UpmIoJyeIQPPBbL9uO5yVbsINpdw1OMQJApuTRBYncsM8Lqq2R5wWKnM9hqFEvwONwxYbs7'
        b'gdvM8AqDs8TnU2LJdkUkDWjYvmUMrxMCeMNNIncNnpAwtdtIEuoGi20qU1eLJdAYHILtXloWPEysOR+6S+5StBLv0wBRoQEPMGwkcME5ggib8RlRGlsJ6ToSuMsk86Nm'
        b'y30e4CnsJANGqw7m0cEZXNR4CCbo4VIqDWiIg5WCOpeMKyRJHVuhiEZULNSX4R0GlxfjBTGyAi5kE7FJSIvNQuJOhMNpAQyfrp5AvFawhXhWrLmUtEUsmTtrKGHWriBR'
        b'JB3BJiLOinz7cL6kEpuxiA+6cVGuESJSj5cDxbptI7CCmKdgaVgk0D6/FWrEyIw4OKFzJ4CtUM5IJeAqXp4uD3sFbo/QYZsbmwV1DO8RFqvgiTzTpdFjdNs0ZHjviH3q'
        b'yGQ7BLkLYzbp8L6aDYZqhq20zy6zPNGF5UtogM56N5FhO0nvxsVCeOBKFJTRCHHuKDSIbS5C4y4BbEvEaKuNULsdxUhQ4egQLJWqeguu5+jI7MbAPUHr07n4TKwYMW20'
        b'zpNMwW0yJA+4zB1NsPtxMRwPDiidSaJ1j+TkNDZpmAovKZLC4Jqk3im/ZVC6DU9BOQlvc4CGqXMUcGBVip27djwLJKDFO50zwiQYDfOAcuVQTZRBJY/YjCXz8Ca5qFJy'
        b'QPksH4qGCvuphyuB2IQP48j8Z7CMjFjxFI5ZoWmzNk7LfUeWGmvsk7hVXY4n8CQWw82ZcENjTIByvLI5HC6vSyApxIrpVg2QfdlkD+AQStGBZ+VsuD5rJil4NcknXzsd'
        b'bmK1mvljudoDisaJ6XFYQUZFzMYru+A+NPLp0dDSMxueqFXQjgftBg79DjYQAeX8674zobkX9FsSepVaO3StfaI4jZsfnoyGW/nYRpj3TA3ju9DUYBV2Tlxmn8zpdEWH'
        b'rd1nbBFnhMebdXqyK42r4VnqQBard9OFDrZP4YacCNrQM7kHLLmYcv7RRE/KLWoWbNEU0q719lChCoFwRCAzk6T6Jj0vV2XIXeAyniGCQinRMxo7tXivkASXx0P+/XPF'
        b'ki0KJ/qcMOqVzA/bVXiHDn/BPlcYfDw1nPA5GiuozokoEOlNnMYEvvOtBG1GAiuE2+5kNZ7Qcn4cQvg8HuQbtTi32Y9tWKyCKjyG1XA0mwTrDJuKDRqoiIBnQiR2471u'
        b'eulXOHeSXGuSXDupwsf5ewRtdWvIf0qWNQa6CsQNyTKH2g3vbhTIbCd9f07anmPcI9vSWyym79ZAHZQkC9rCoTFLe+SzB/p6qKe55fL0fE0YVmrgQjQcFVjBVTN0yFWZ'
        b'6d2C100siVaz2l27Vu5QDNcjXtqCVt2SKJLoQetAYjmUkBer3GcP4osezdvavYbLxCkypjs5QeEoGebVeASuD2QJ+MQtLGqvPZDz8dr62a56Bo+teGEzHlo3eaZEygoN'
        b'7limzRFR0zysWNs9/+ZLYkg4LZrNUarRWP3holA3rISW9O4lzU5VzsDGzeHhejxJoj6QJWG9W4jKLDZYnzvNKbI3JMybvY5O+GyABjULgUeazdFwXlL1Bl5cINYQy6qd'
        b'53bR/kkqfFQgBSOV/LdDTA7Ao70kfDpnuZqk/L4KW/2wUQhGAhzKfUEwaMEiUioXuSjUUHBSCmelVndQdNQsJHsDtPXaodsCqFR4ezocEbZlGNaQkIkdQsksExlfEojL'
        b'ard87LSHcRsQRRu+hM7SXc4lamjzSlgSAc0TmQWr3fH40tESo0Pr8Vy3MsCjXrYmXK+hKOqCBhooeTkijrxlNV5wpT/XnSemHrSErk3DsxqogqIF9qk8/kfHtueC2mOP'
        b'uA/pEE9VhJn35hmKFRq32XgNywWjQ+bBvThhINQUf1W7yofT1K+EcrcxFBQ+FdTCC3C74Dlyqs3QmtE9mxuyaXCPzMUMPCAtcTFeHSBmbwxzYUOTZHQr8cF/lX0CB3zV'
        b'bb3TfVSrndbCafb84SAJD5JgCxtEaj9Uzuw3sA/egkOFD7Ftin0cD2GhI0/sD0VQ1WuykhvTDhKzYZOl/N7Ca1PFRDPedxHJFonpHcIUj3iJyRl4fJ4QLsoGGp10Fkb0'
        b'7nPxugvVXvYQfq769d4v+4ygkdO7xUeQYiqe0UB9gjMrKlq5zmUJB25aP73bvssVazRwHDqjBFem4YE9ruoNj8lnVvXS7+XxbnMGJkqrVm+mwNFFwEjx4HC3re0+xzR4'
        b'poFKo14I5eiFA12WKDPhxianCPejPTpn9ofiGQo4u9gzEc/1F5zyhTtwX6waDSd72+huzTKosKN/pHSucIh4/JI1d5pybtXGw0Uya3ZNAbZCvYCfFUDaysEn4E0Xpt2U'
        b'THugwjYrKa4IIc6ZKBoS8DWBL9h9Z3zyTO2zk2I3zuIJWLxQmrND6HARslsSdIsKW/CZjH0GzcRrL9pv+r3bm/pBbrMS8LzAxNu3W9DP45m+xIdL8LOVFA1yg5MXjo9f'
        b'IHw61DgJD+3rsBwPb8bL65hlCzl3SsQ6hRMyZxa6iBCFUs+6T6sZ4PTst8gvwrW5gv6rlXikR4RczH23zPlAG3crJzU2aNst1sRAw6KXZXuI7/ReJojL9kWybvvI5HBD'
        b'hY+hktY894/0KncFQKqhKZyhWO7uNnMOnpVmpwqu+rigtzdM0OyWJoOIkMDChmoomD6yQThUOOXHAxthbTu5tb3Zi8YyXKSzqOEI1Anoe/EMaYuYn4Idrqg0S9koUbtP'
        b'A4e0FdVEPsmTuXjWVaylJM1T4RO/FME+cGB95MtiTbRufUGf8aQGzgXiFUO8zHjKKURuFSmHI1amHGoK3ERwX47nzFbKL+eFUeJK4+OcWX4oxXb3rXiX1pREiqJGRa4z'
        b'v1uVAjd44WQi1MjKCYVbrWJRBDzCdiuUKRkcUZG5Ik2BG74ytzmIN92sFNLCI0owHZR3w9kBYmQR1kIJL7ngjc2y5IKnZ9oH0Mjg7Dxeb5mZ5iy33ImVOD+EQ+GU6DM2'
        b'klLsCsoXxijkHk+WwT2rJ+1+TS0wq96GstSRTKlNixVK6PE9KBFJ6bltm+zDOHFOEF0rRfUmEcqc5Zt6fCBLEDaT1UdJCXY6wzN0UlKzDlkbONwfj4jCzjg8Ius65ECP'
        b'iM2mLsRboqyTzNNIXtchjemUCeZFbCFOFGqYl7cs7OC1fWKndcbNsrBzGS7Iyk5anFgy3g9raMSNUkvKi3kJ4NSaUWIJNO6AJl7y2QBHZMln6kRZgbiS249XfDJGyoLP'
        b'UGIPf57utVDUe+IpURXlnklL5GEceBWbrDzFhkvQyfA8HVXXX+axlykrbebVHjheIKs9pAeV4qBBcApu8foIsf2aLJDMJsc6TKbtNdhh3U5cvcsz+mouhCVQK2sUFKK0'
        b'yerJZbghqyeqQZIbpwl+KY0pGBYtF5WnU3TwcwL/vLRXeGFlBi9k8coKdPoJQsSQUlRbfRWsf7worJyDymliQdg6ylF4xcUnWVZcFk4VCOzDli2i4EIJwGVZcoFz+RK3'
        b'xuFwSlZcqnNlxWUOdMgz3SnYj+1CJS7DNUGLGrgNbZJ/8GQitnup2abdFH/w4k6LFMrCNcGiTgPHsURWarAiQJA2FY95y0rNDRJmUakh418l0Wgj60ibtbmx1GUC4Bk4'
        b'tFoM2Sg/rsV2HzcSvSuiTHB5EFGd7+UNbSnYzkUvAUn02kgR1qySgtcGtWuxvVDJVm8QVK0MhmqB+D48T7lgoZb+OCw4f3zWbolCJVweIetFO+CgrBcV6AVdEzR4XVSL'
        b'PObKYlGySgpLGzZ4iGoRHp0jq0VQQXm3ELKLcIUOyAtG4xbIghE2wxMpyS3k93nFKFkhC0bYlicGNsGTgTSgkIVQInjV2CkSWscO8mXtJPyZvDZH+neSeFgizV01li4k'
        b'xO9pmdZPkLxuBmXDfFkyHOAmylvJFuIDgfoFInOztB7nBhpEcaoAHsvi1GKyHmKzOzry3e3edKzLeFDUfy6voCBWELZdFSpLV0vWysJVCFyV8Grx+FhZuPJTyrJVcJIg'
        b'XxQeDtLhHS3btFM8P7csRyC+1Qy3RDULGsfKahYnv1iiw7oVOncty4wQpaQr6NBKitfgWbjIC10WaJZ1LngEpyUDj0B5vs6mZpuhSojQSShy1kN96a+7ogamDZIlMGzJ'
        b'FRtN3DaRV5rg0WBnpal0sjS6R2LhlG6bmungCQksETlxqiTAMTNe0G3TchG7Kuq0tdMWyhLlM6+1vJrmF+Usph3YLQlzBEtUopoGdeNkNS11seRcJ9TPFuW0BNI8UU7D'
        b'lgVS5FLxliinRQbKYtqUXAnsCl6BSzofBRvJt39MtLNqJGmu8kRZ56NigZxpTxk0kTWQ1cGsCXBVh60KthI7BdUuUh4o9lFF9qcBFUslye4kPhOO0qZWzJim81CySbQ5'
        b'3+X6rrWSLk1Eygc6u5plqMQxa/cPkjJ9E+/G8mJe/DhZy4PaNLG3iVBu0Fnd2Dw4K45SjxfSBcbz5uNNUm4SjMVcs5/wUuVpLLFPF84fioJo8GR8LBT3FPS6M7NiUQJU'
        b'Q3sKlK5iazZosQHqVxrUsghYBVUFWBofi2UqInGYCp9SbG2hBFfimTw7Lh5bsSRey5QbFVPw3HCxLDVWG4cVCQunYHmggbejvPqpBsMBPCPPfXCrT2BicLSa2SarFyuI'
        b'the2R2XyRhD/0dKLd3dEG4k3Ph1MdKh4t4p3qVQOj2wPZ39KXaw+xPZqdmn3qEV/SiP6U+p9mrUsSyX6U+pffKokePpeP+G8dWnVG/NEz1KfnW/RbzPmmrPMtp0hLhNd'
        b'/hEjO6YBW/LzbPmi+xnQ3S/VmwnaNqM515iRawoSAJeZLFudG1j5OhdQGca8LfrM/CyT6J9yqAKe1b61uy9rzMzMt+fZ9Hn2rRkmi95ocU4xZemNVhdY2025uSGeLo/m'
        b'Fhgtxq16M20zV5+SI1uzvGeb0QMlpK8FGebMufyYm8zbTHlBchVHcGlMuAsG5ryXTsR/Mokwph02fgSTMTNHn0+TLH1uJM5m2dl7M1s3mkTKr76PjXepndBC9Al2q42f'
        b'kdM9OSl42tSZM/VL4pdHL9GH9QEky9QnblZTgVEgFsD/CtCbSDTsRgrlOAHT01MsdlN6ugu+L8N24i8pLkTLeRZ9sjlvU65JH2m35OuXG3duNeXZrPolFpPxBVwsJpvd'
        b'kmed27OjPj+vR0iD6GmUMdcqHnMibzdbXziMSxN8GHuxJ6tPjJIxDpZ48oCS+a0RAeV8rBfd1gfDhrFQdryfV3r6/I/8RjIxORfvRUAp48HII5bKUsOgQUw+OsaTDWKh'
        b'GzX90nN/YiuQ/dqfLvFh/hTA+IamB2XqZzKp9w8m4wEeDpJ9NYlw0Cw7IXANmlfw5h+bFyVbfx3Sh89Jm80bf+RSKLLnjT9Pp8PdT6arXbT+CK/TovW3c6pYUoBHsnnj'
        b'j0GzTnT+Up2Bwh6jn65Axbsr+JQHTLV4YbY42Apw7NIVqnhsGcB999lCL7FH7hg8KFqFCkrW7vNmoQfIXAUe68IpWdEKYCd5BFEFxVul46yGuymik0hxJrl83kkctEjA'
        b'C4SHr4hGIrn3TbKReHSLhFcSCddEI5GlzxVtRCzFJ7J5hE1rdZwyQyZyX1OfAg3iuefAGdjOj4k3Y/AsMWVghjhlYBgcsm53o9g/mofplZQ+yJACijfDeR5ws0gKSERD'
        b'stYsdk+ftVKE9rxbc0fE9njWGUpOBYoIRS+XTaaD8l4utIyRHfkJvKHvPt9Hnx7kp4l3cvgi7XdzWigBG4mX4CTLsNsMMonbB5dWCt7jsSjBezhK4a/A7Dg8niu4r8yR'
        b'3KesVgZPpVAE54QErCfAovP7AGXsORcaM6UAjLUJ/mfgYUGZ/XvXCP6vp9zspugVb5bblJiihABQDnheCkB9rFixaPdqwX+bUrAfD1GOIk5zenuyUwBaN3D+R2GRGBjB'
        b'O8GC/+6UPHP2L08WA6mrF0jea7IF54meMlf2GkNeUvK+Yp/gfcwkZ0I6drTkPJ6KF6xfslAOnJs/STB+AlQJzveD8+Ic2dNUkvPb4Z7gPBZhqTiHZfNywXq4bhK8T8OH'
        b'BpU8+wG1m+A9HCbJ4syPQ9m23B+AbRJcRpKEVg8OicDVPXhBwPNbKsD5Yr1BKQOnamwySpkJmSMkBpr2yJGzo9dKeYHiHUJexkOZ+b27P1FYKTpmsYu2JRx/NVY91evo'
        b'yWvnUxcUT3J873uTPv1kYPGyKda3vj+q5mswaEBYzb0FHo/0g8bsPuvo17B0T7/Rr14P9T74dtwXe81/Xf7ZzldnH/yTh6f/48W7+t8ZMf5KtSVrTWhz/e3x8Yl7lnz+'
        b'2mtPO6M/anm6r+h687t//dY33r8b0Xj998t+dK74j7rBtR014am/sv78w3c+L9BfHH5yZdz4uC0zfruheErG2Z9+fPa7zZ9N+6Dh224fjH79dvl2zabotM0hmTff6Xjw'
        b'/Y+nr9kwc2zzRO+lbcWrU9/9NG6B6t/tl//2x8ofLvh63YOp7x/edXrpX8oXfJL++p78+TnfWPm3izden6jWno3b8ORz/4+bDy2IbceDe0a95+41zr95P3uYkjnJX2Fw'
        b's4lY8wgFRmWBwZOjg5VsUZIWziiDp+ANG79IZQyBG4EhMUEBhhCsDMJjvE1wP0Kv3jgUG8UEsiEdW+OSguFYEqXIh+AuBWK6FUqsGAUVNpF4Ph6Kj/itpoDgEEqQnlq0'
        b'cFA5bZa3jRecMpC3oNqdV4u2y6tFeA+atgUHYMkUJQuBJxq8u5EJUBugcwOWJgTFYAXP7fdppyt94D402PR8nwNZG+MkAErbKmXAOFi1Aw+rsBMvxRiUXcrJBgt3QQYP'
        b'8fFV326wLwbPz7bk7zLl6bPlRbUQHtss7PIUnjaN/4P7Oeta7vH2M4NaoVa4i5ePQqkYQp/96OWp4M+9FFrxt5I+tfTpTu9e9Mnf1TRPqxgmZvHZPvQvNZ+l9FdYSA9Y'
        b'ItcTZtB2qfmeXSqKmLrcnPFHl5oHDF1uaWkWe15aWpcuLS0z12TMsxekpRm0f/+IBrWF30+y8LDXwo2rhd+as/BIWOxbw0/Xj5+uiH3ir9Ry7MW7fQw927pVUh5ueLkQ'
        b'X5AezsN9MgIjuCtJH4AX4FIcjWJpIlYkxWiYT4Fq9q6NYjhm6GCK5S/DCRricbuC6dYpsYWycaHZbvBwWRzlS097gn3o3JypcsYZmt5BexjruV6mzlY7Q3VVsYpCdTWF'
        b'6ioRqqtFqK7ap3aG6ocpVP+R4sVQXdwt7BWrW/K36o3d0bVrHO0aM78QE6f8ndDdYiq0my0yYCswWSh83yojy+4Lj66xVVJ3yEWIBKykHc1bTZEWS74lQAAz0khW3xE5'
        b'x5ejK6PyFw/RZzjqPJRc8eIJ+9qCx/BRucZNerPMJDLzLRaTtSA/L4tCTxHKW3Py7blZPDSVUabIKZx5RN9BaKSZH/l5zEv5jVEfFmyzF1As64xsBdUoJJ/MZwTxjQx/'
        b'JyRVvxSSahLti+jv/hQKPujrYuWx+IDYIGhKkXcs+YOk+BgynE8TFJSGwjHdHDyGB1LM3zifpbQuIEjFn9/5TXrIhwZjtDE3Ozfjk/Q3Mz6pb0n/JD3auDm7wthkajR9'
        b'kh7wdpOx0Rif6ZndaHTP/nm8Gxvzlm75h183KG28bQcV07FGF0DKQMDLEuxOqzga2tVwZCzehrsW2yg+ryY9IC4klkwjlHer3wi4q9awPDxkNihdNL0vI6DpVvcunbxO'
        b'+9yo+UijlsXN2QBh1Cy+z02Rpsu9W6q63JzyIW2JF3/z5nN6b6+y8Hs2Fm5L5DRhYzjAd3vZmJsDetsYYd47CuAwHRGuFrx0yjxsj7TP45MqFvfnZQaXIsMN3tLD4lBo'
        b'gzK4EKTaEDcdKgqhmd9P8yQPVOWN52fuE+HeDLy4Rkcm6942H4q5+H0tYixUi9hm1+6xOs2ybYV8oJiCoyH4SJilXfm8HHzfN0zN4MEeJVYphkTsEyuyoSLeGjsqzKJk'
        b'inwGHRRcyWD7OpzM0+HRoG3btATsCMMzeCGZbCRvGwzC5oS45dt7bNymNHFXKgVuhfC7QnXY4FLSmOks70IDHISOQIr475L1VDAlVCjC58DDvu0jvzTjUAkLKa/eKh3u'
        b'2e49dlL9d+0kL2n85ctKGkLBXQsaX2oluEXh0/9xYeBL8nW++H88Xc/MFWhZTbaXE/QXEOR0yc/MtJNBzMt8GdHuFD1y+RJ9OHluCzeYEeQYMm35Fkq6C+wZuWZrDgHK'
        b'2ClmOg14OCXxFmPuS/CWkl6G9MLNyJliF1fvA5LDUwKC6CMign+EJ62cSp+EXsDSsKViIDw8IOgliL3OROl/fp+FBn5IQecCWV4gqFncdu8seIGA/OcrecUeiPkFLztD'
        b'/vPVHKIL8/5p9Q1+vV33kjMZkBhl5z6A8ryHlNG84E5CoflLPUqPN1k8WmS5tdt5JaSTeaenz7+8UCeLG3enDmDj2bD1Gpbur16zVJZH8ihxKub1kewZvDoC1XBMlpLv'
        b'Bq7ntxLJkhVDMbm/gQqP1XhWALKM5VWStxLUoelBK8JHS0BQgzXmaaJq+5BNpRS8U1axsYgMat00NVuLnSyMhWXBbQHkgq4f07MfxWkK0nP3py9hwo5hfTY28PaBN1xn'
        b'y9ny5dPl3frZOka53RrWLz0oLWoKS6GEjk+PyR47jee7+FTs2IIV4jE8GOxOG8IpfMJ3DMYK53zKGWpjacVAPMMXrIczMvsr24lHRCuwmZJ12hZr4bS5ofldlbWVhl8Z'
        b'uHZCxVQfCPWK/O34hAsBJuNHr6d2LnUbNm/t0tgrPj66AUER0R8qF2hVbh/VRa/bufNv+/f+Rve6t9H34KgBe5YH+Wb88rOjVwY8/fSnJZ/Fhv5i4Juho7x+Ymv8j8PL'
        b'W6ZP0a+71Xllx46iWRl7q/VG/5pnP99q/kbhilXGt5d8Nj76mqpp9R+nj67IBe2Ode8efyPVL/fP2S3T/u3QBz+rMtS3v3t8982Qm23zcurjoh6Nuv/uojGfT2uYuMfg'
        b'buMeY1QKXHTmZzw7gwOm4DFw0jae23W8C2d1GdjZZ5BAEcJTyo9Et/48UfFCIHkHStV4vjYFS4ZD+5RgvijOjU3FC9qYoXDDJq7mwgm1Lg7LDD3QBoNDvWae+541Ni4K'
        b'q3fCjTg4o04KJlezTbEEKhIEosb+fjzVm5LEMd2nxGt4OWC+r8gyVy+D6z3JG2Vu2XjfBy/tt40UbIYT+DQOy+OgeUVPpukbqtqE9d4GhYwc3L9y0vY8mPGQCRq5GxHK'
        b'hMpQZj/Ff84Mjb8rKc/yEbmYj0Kt5HnXeHoNc74sA3sFO8+zpC4VWf5eMc4/SrBUvRKsQT1xD4f9u15xz6kRveMeThofaHSPi+rfndgmicCgPzpUULZqgkEheyRFa/FK'
        b'T4+k1CJ7JIOh2OXLNz3en9/GIt+vzFb2fMlG8aVfslGJb2+pv3jTxfytlObzSwL8bBGfC0fduw/xP50R9Wm/+Y/yJfutTbTzxs88d6z+h7kAmZjal6z3mggZlrWQ2j2z'
        b'FqID7/EKm7g0UYx18nZO6w7fOGLoxmAsScCyZCyOVw6IhBtwhH91g/4wsOX93OB+PpwwnxlUoRBh2/g3zv8mPag7q9Beorzimxm52b/OYm/HG+K/W/b1zRO+Y/hO+vDX'
        b'g2p8jma/nq5904vN13nplr1n0AiDgU8HgOPllAIOvyINBpbgQaHLFCGfIrMTtfm54QlekC719Yp7WO+qEDTsYmyYXr0RmuCJmIEXc/BMbwsyYqe0Ie5Z2GDjQrsJqvK6'
        b'60bxcFzvLBuNXi9VTdmnPrttMtl6tLlftzaP4VrsLmopliHPtVUlKxl95yEKOSi0kK8ZRqpiHSC1sIh97NNbD3mdayAcwUdxSXALmpw4OxGGK1P/jpopHewrqxkF1l80'
        b'uUhpckGu2Wbt0SXZ7yGF0fOn2RbjJtG/eUGvunXTqJ/eZ4bsMnlyeNKqxJSVqUH68OjI8LjkVQmUOi9JjEsLT4qIDNIvCRfjaYmrEpZGrjR8eT6t6kOFhMPf4uWmfE9F'
        b'uqBPzz0T5M7ss5m4Je3g3gDLAvlXFY/Fr4iWJR+e12CVAW6Mi/GEup30ioFjO8l3aT2hWBlgFwJ8aexQsRSuTXCuJs0Rtm8UNqrhkh6um62v/kphXU6z/+g34jfp38nI'
        b'IQ35JD2ea42pKqvR1Gj89e7b6d/MnrLSYIynfJzyc1YSHZY11R46c9oPw34YOuT/KEynl4TNKEv9zne9XvU69xHLudiv/et/M6ht8noCPoqWLnkVVEnlYHlC9JPh+FAu'
        b'+ViDJ1z9p/vQ0WLxKqzY1O0KRy5iooxZNMPGa2BYjkfxbhz55mQ4MyV4spZ5DFPCRbysdJHevrXDk1ISa6/MfVC3gkx1V3gJFfGR+fuw/wcl4WsmuyhJl4uSiDKEYyC0'
        b'BEYHBexJSXyeog+BR+rB2XjSIKuF+CgPH3BvtXwhllFgWjkFSqQ+jdivzvHAor7VyVnTE18Y7anpfQWV+sWGF2t6vZ2XKH7lGbeKrKgPn8VzIt4sLTDRA/Jtrl4kRipW'
        b'rtFmoxQn00gOyBWocGXGLFk2fCm5c4HVk+j9ozxP5nX/G32pok9f6p4oajPxDJ585bqa049GJurmxMJ1YUguzRnGskYZGUtP39PmuUSmKli3G5+KBjK5VlMMlMy3iFu/'
        b'5G9PeZB3edmxjqeAuJdvXYytAnrVOi0bNmA4N1Ne70xcy8xugQEK62oa8fX5QS+HS+7208Ufp+dkxxu/nR208mMyLerPDg6fO6zt9Jnhc5dMt3pap2W2JnjEeerWLpi2'
        b'dsHN8eHBquULtniv3esZTvHsCPa0/6B7UbMMWuGMx1PGc7OP+h5W4nnpjau9bfwLBB5QnN0rdk8SJXSs8AQHWZoEDZuVqN23d5twrJSkXYNbgcF4ij133HgHbol+jVXX'
        b'09CB5qDung65bis+lr691R9vd3vupE29rNdwLBZFyaXYMDSuNxYShdH8yxpQpcbz7prumP0fFRu9hD8neebaImzWkG6bFcktlZfCUykdu5fCMqKX1erScSuXlm/h0UAv'
        b'69XnhoSNX48d41Dmutixb7oUG/n3zjJX4iHXE0blyDOK84VBp0GVmBhlUEQZlIlR5tfeekVh/RPBPPuX86tOmJMHLul3dFP2rDG/8Bnr6NjRsKOh8cKOy5caFf5LNJF7'
        b'vc5M9ozQvPd5+vfei7y8Y9+dP3n8NXr3yUFX35mR/N6/vTN618yFM/xT3KYmXbb+MGL/DzLXVX9ndWFidfYn7rqVw/9j3PzbQ2ytUZGPU1d8b7jx0hup7+POBPj+9+c2'
        b'R71ytyQg55t+VfUVbylmrPtxWqJ7ZsrKyBkzfrBy2QLDiLUR40rNl+qGrEuFlTWt5wbfyhp805zpvSX1G7tm3jmRkJute+XHr2/r+vGridtazy74xDT6P+eEvj2qy/9f'
        b'+zk+Ot2x/uv9KyxliQ9nv+nxcM63DInWo+3n3p+/YH2/D8fW/rr6d2Frfv1+k+3dzsQz++rcOl9N0A7/5ZCO4R9W7Jh39VHgx7u/tjes7NMiR9a3Piv+Rtm33/D4w+Hr'
        b'ZVNDXtFqfpNxcP6/7HhTN7Hulx/sScqZuFt18t78d5qPPnQrv7lh2o8/bAx7e3zxB10V3+qq+OBH9YXfPTfqP0+ufmyJP2lJWF5bPifqd1n+7108/J/nVy/Zetz949Lq'
        b'1ww/+vOngXt+6/fs27c/+238uXcf1xl++vXy4JyTj4PX/nmQadXrn1Z81DZ21Nav/cHW+Nfvvflpve+f1FVDSv6t9vZrqQa/pr/sejX7P9b+3vHwX3+ZvKS2XbenPmZQ'
        b'e+Bf3y8rSDsdWHhx1YdPa/ZUbTHlPv3syScJF75ICfvD0Fr29odLd5M2c2tEeqAkx8YvfO5RzGZYMWy9TXxV9RgemCxUCi7BA9eQYBc+sPGv/cBTrIfbrqagFE72zuRP'
        b'vyKih4X50VhKsUN58GQs0jLtRuW4GRRTcwnHG0vxWWAsud6iYCyOiU/UMB20KvH8lBWyWXs22xyHFWsDsZLGsSyGj99WYhM2TPxvNkUNPv+t6V8OR2Phet/nmzAR7mlp'
        b'ufnGrLQ0YR5+yZV2nFKpVExX6EUvdYDSXT1EIX89NUpSYXfx/r/v1105QMF/3RWDVLzm4L9ISScYNNCTTjNM4T9ZqRjhS6/+SoXFv9tMkqVTpqX1MnDe//8UV1hG9lhD'
        b'vhG36bLL87OJL1pCbICbeAJKoZJcEnlmOEZ/1UG7G/MZrhoJRXjG7OnbT22tpbkmt38JLn3kCYsHRfwqb2bSOM8hB3PeH/qnKUNeX9lZHBFz0Xz4yjpj2/7ftnxz+rRf'
        b'vfNBaECJW5RXztVZiVHDryT84HCeekTz51GFMT/7PN+0MfHXfxyyd9/t+nJ91C/ev/3Wa8d+Xva7t9Kr7tt+MXRnQ9So6Kt//Fm2z21D57r9FelL3yjTedauL0xA746f'
        b'bPjVGfNfDfMn+q/46dMJkZMWbesweAslhHYTudNSUq5WqEhKouPwqpcO2pTYiB1zRBsNWykyPeabzyOHVjpuEq9j9cfHKrgIxxaJKf2xgWgi6MHdHpRDZQE4iBwDVKNe'
        b'6ScUVI+XsSMuJiEgwY1p1cpdeMd9G9YLC4F38UBWYKwH1muYIo7habWfjeeJC9eLdMglOIKKKXFkBCrIA1X6qlRsGbS6QSUUwUl536Edbw19cQ0+MGjZ0Ah1gNpm4+yj'
        b'2ef5vXUsI32fElAoLA/UD1WyEXY1HF2HR0RtbvMELPWw8qQqDkvdmDpYAc34RC1CFHjCm07CGz7HB09bVcwPzqrhGtZCpzAuSbModSk10DynqJxYq2C+K1SrTBR6cGQW'
        b'TFB1jwetxOv8fCJ9UxDF7mnYXLwge5l3iEdPApPguiEISwRSxCd8qsSORXDLJT8Z+c+xQf/EN8qnvsSImfPMNqcR4wEd8+ZxDWVlKrWCmwGemfUTsQ6PdjxV43kMNMUy'
        b'qscQjO5S5ZryutS8kdKlEYl9l5ryBFuXOsucSe+Uo+R1qaw2S5cmY6fNZO1SZ+Tn53apzHm2Lk022VD6sBjzNtFqc16B3dalysyxdKnyLVld2mxzLmUwXaqtxoIu1S5z'
        b'QZfGaM00m7tUOaYdNIXAe5qt5jyrzZiXaerSigwlU/R7TQU2a1f/rflZc2alyWJrlnmT2dals+aYs21pJp45dHlTppFjNOeZstJMOzK7PNLSrJSDFaSldWnteXZKKJ4b'
        b'OHnYkRZe67LM5G/8y3IW/i1HC6ebhYf3Fm6yLFxxLPwWkYXnhhZeUrPwSreFXzm3cJ23cLGz8G/oWWbxt2n8jQu1hX+91ML/LyUL/+KihRclLNwNW3iGauH6ZZnD33jm'
        b'YgntMZecHZ495vJPEb3MpRj7wr37glBXv7Q0599O//XFiGzX/+VKn5dv0/MxU1aiwZ1f3MnKzySa0B/G3Fyy+qOcosODY3ruSeS32KzbzbacLm1ufqYx19rl1TtDsyzo'
        b'JmCvNyl/8+V/pbWQPxKFM7VSrXLnMhY3iLsmxX8BWeFlDA=='
    ))))
