
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
        b'eJzNfAlYlMm19tcrSyOgouKCNuNGs4rivosLO264K7TQSCtrf91u44KyNLuIiqKoIKKyuEAjbqgz59wkM5M7M7mZ3MyEm5tkkky2STI3k5tMMv8/yX+qvqbpRieTPH+e'
        b'5158umm+qjp16tQ571mq2p8IQ34U9FpGL3ERvWUI24Q9wjZZhixDXixskxsUTcoMRbPMNCVDaVAVCfvUYvh2uUGdoSqSnZQZ3AzyIplMyFBvEDyKdW6fZ3rGrliepM3J'
        b'y7BkG7R5mVpzlkG79pA5Ky9Xu9qYazakZ2nz9en79HsM4Z6eG7OM4kDfDEOmMdcgajMtuelmY16uqDXnadOzDOn7tPrcDG26yaA3G7SMuhjumT7Bif9J9Aqgl4atIYve'
        b'rIJVZpVbFValVWVVW92s7lYPq6dVY/WyDrN6W32svtbh1hHWkVY/6yjraOsYq791rHWcdbx1QmYAX7f70YAyoUg4OvGw55GAImGzcE2+QTgysUiQCccCjk3cQlKi9Wbq'
        b'FEnpzoKU02sYvUYyRpRcmBsEnWdStjt9nk5yVgY1ygQhLWFs9nbBMoUeYjs2YBlWYnlywjr6UJ2sw+rYlLVhamH6KqV8HT5fsNMyhzrC01g8Tf1q8FQIdcaamESs2cSG'
        b'RqyLCY3HqmxswarYBKyIVQn74ZTHDuiCMj6xbIJa8BJS1II2zcu8yUuw7KSHHj4paPMYti6GaFYZ8VFsSgzcDsKy0LhEPL3BHctjUoi462xBMQlYk5SQnBJEDWURxOi6'
        b'mLiUoLCY2FAZtCsFM5SPmoPX8Wy6bIh2eQ8IJe4rdifT2y5/WZmc5C8n+csc8pdz+cuOye3y3zNU/h70SnxB/hcl+W+JciMxCMLoyWkJ5UlygT8MlNGmCMKMdJ+00Gkp'
        b'Culhqdpd8BUE/48z0kJ/vXSC9PCvw1QC/daOSk4L9Tq6RmgTsj2Z3qWMVf67xy+mCsKH0z+V90ZeVfYI2YyPz1Y1TC0U0nyEZWkzv2+6tqlAeqyQ/T5kx4SgSfK1P5L9'
        b'xT/QO07oFywh1BC9PI22ojJCTF4XFIQVETFhWAFtG4NoP06FhseGxSXKhFwfj8UKsFpGUf8E7IVHogUveJGw8YIA9dATbmErx5q4daLPCpOKPlYKUIaPVlrGsOdnsBc7'
        b'RTwFdSY3+rNagApoNUttl/E53BLhOlzBXvZ3rQBVwYF8Jr85fiLe1UINCQqbBbgMJ/ESHwWVUGkS4dp4qCHVx2sCXCEKLbwtFIrxkkiK0lDAGDnFJuvFXstoNs4GxVNE'
        b'3w3YpaamcwLUUmOTxY+aYqFigogVgRY26DTNsIsaGBdwRucrog1vDGNjrgrQsAirJd5P4oUDIjR7oY1xeJ7IYSdU8pnSyQrOitA0EapYz0YBLsK1PIn5ariJjSJ1eKZh'
        b'3DcRySh4xLmYolXQkvH5AVJerBegJhYecC6wdqVenASPfQRpxAXapCt8yHgLtKJNC/eHMSZuC3B1goY3bAYbntYUiHw/OtiQewLfpyg8mwWVq8y0gTJ3Ae4UwBn+fExe'
        b'iKgha+5mG1snwKmAufy5bGscrb96skUhyfrsiOF8jdjjCx2aUXgP77Ep7tIuhKNNYrcIyuC8CA3yA3KJWEV4sMWfrb4KiqBCxE5CoAeM4wYBTgdCK2cZT2ZCrYiP3Xzs'
        b'23rRaz6fSgctBQQbeMedNVwX4BK04XWJYC3UEy0b9OBtd8bHTaYNdVmc4LJheBFtexaYVdJMpzTYJm1Co57WZMMGby+1NOYydOBtzrw7nFlD9GpncQ2/ReTwQqY0Vx9U'
        b'4G20pdPILsZ8C6n/FOyQxNHrDpep4SF0e7CBdwRoPqznbKjh/Ga0rYGTHnZBXdszSlKumwroRlvccQ8m23sCtEDhbEm5OoLwLNqmQ6nFrnen0QpFfKYYeD6WaSTUDZNJ'
        b'w67hxeESh4Vz8DHaAuAG2lhbO4kKS7FJWnQZPNtBKyt+FW1ukrJc2QPdEif3t2C5JmEx3rPzfnk/1HHml4zP0uBjsLqzhl4BWo/DHc5GGN6CBg3WwUXsZuTuEx/bd0tQ'
        b'0DUbujVrA/arpGka9CmSXjydflCzJgV7mfC6mNAbsNAyls1fhOXQqMG7ZES9bMU20mS8BL2c3tHx0K4poOlV0jzNa/P58xyPsSI+wyYz461MgNKVcr5SHyzCQg3WYyuD'
        b'YybxCwQLLZKSVUPlPk36XE82yyMBbiyjDRzHGu5CZyZUzsFauA9VKkGB12RT4WpyQKLUfBKfhEDlfjxLFlyhEpRZMjlehBN5YRYWBPjMhJv21pl2CrN8BA+olo9Zc0Cn'
        b'kJbfTWh5DysV5KyeCEKekPcqaTEX2PMx2BKvJBJXBGG3sBuawiy+7Hm5akW8GjsWM5+SkRdumc4ePporwzNwdx+WQcccaFPpE6Ear++NhpZtiUKUqIJzeA6eWoJY3+Yg'
        b'OE8IzHvewXOkVORBK+ivKFL4c0phAlYrPaapLcGs8y0klJB6Qy/cYt1j8App5R1Hd3iqVGyTupvwJs1kp31bon0ErnHanRLtOqUaa/GiRceoly3HJjwTA53Es9SbjLaY'
        b'us9kU1H3MAU+HIP3JcYvRyxx8M1XCH17NVqshFubRgpxWjd4sF2DPQmWCKY9zWYCeddVso93abPpVzujHmZSBUJZAfaRo5jBJqgMIOQYYKdasVuaAloIMq7vhUotlJA0'
        b'Y/ChGu/jTbzK46ZVcBWeO68hBp9CO4lHuV4YjzYF3lPnWOYxjhoSaE84Rz4RXJbVTlLiIrqVyKh0Jqp3JwoFcNcdHsHjvZYwNvh2DkHJmZixJPs7DmEpoA7LaWNLM0m7'
        b'LgqReFUFNSaBS8tANM+4bEWMDNv5trVL23ZGgX05c/hGwA24s3SItPD+cM5Um7RvVqWbGW5awqn3XEKXosHeg8uIGdSKqFdXZ6rIli+v4Nuh9QLHiLbB3ejgg6OkzZ6J'
        b'p/DqPhU0HR7NVzB3aYqr4tHny3B2cMAEvK10n5Ig7V0Rtqe8MAON7JT449oXRlYK1YtEfL7LEsoGPcaLBwcGtbNBBKqHmEChVAvXSKsS8akbNoyYOS6Tb0McOZJ2xywD'
        b'OohF24LmSCyJBFHt0OiOVQuncr6iSTlaBkZ0vKCHdrbqVSvRJtLqivjKx6vSHTvnMOVoLVk40/RkvKKEYrfwxA3SypsIQmoH1dZlIkl0SiEcnqgWTdkLD6BLsryzeIX+'
        b'SYPa7b1ryFMNosB0BT6JOGaZRr1XQnn0EBUP5Ft9m/Ucj70K7AoK4rqBJUnDhqhG21DVKICTgoqij8dbOPVxM8joz8Q49DpGuZY+DyCAQkHhTyn2cLYXQ9HyAep37Wpq'
        b'g0ZnlWhRutH+WmYyAPbb6crK5ilOyqeEbq/E5Svh9jSCrXPuWKuCW5apHCA9j7ngzHmSC9vnaK1KiIImFVxdt5mLfiq2Odl+tSvU2O1sFl5aBN0qstQ+Hy6hyF2xg3pa'
        b'7dC8pCX8GXl/r2F7Z8vWqdzmkS494BH5QeiNj+fQQD2HqAW0TMXHBEvrodot8LgkUT/yf8SW50FnJOOdK6nnLLhPMDHxFa5qcCJ2KHzZsIrLv13a3C7agJRpXDK7wLrR'
        b'BSVo0+CehHUT4CQpjAzqOcdQH0F0nM0xBu/DE6d9BauCzO8Z9HEUXYyNmS5cUFjVR73lDEQfkHphyyTJITXgGTfXnj14gSvXHYnfe0xhHsJtrjDzoYsCf0m5uJhj5sMp'
        b'9kfPoHr1kAU9sszikSPenf6i04ga0GQukUhy8R14SUVQQJEx31LVdOwbKheukU6jNtPzGyqozZ3I1zGZHF+Nq5EzDXMY+dqEnCC3+Syql8zqmUbmqmgOwB1Yyix4vhbP'
        b'quDU/BEcct1yGFQ5DdHslKfbp/GlWR7OGQ5ls2VwaZlnEj6bwxVnIRZtdPXHq3KdjEunwAd4I5aT34wnvL4U0e24ZlHRXzfzybuc4uRHHpnvsnUjoHsQFsbjIwWFQw+X'
        b'SnrZafYbiv57BOcg5bnSm4JHHv7kH0h1VYl2eMpVrVMifEeBd+CpJHgsxPotL0C4k+BDCU6r3OZG7ON8yOeOdnEQMUuDndWHafFz2qVujgdr3La5blI7XnXIHGzbsBqL'
        b'92LLNsG0j3x78E7OUEpkCJsB6/2Hal2HaoTdr3eSV5y4kIMaVOFl/yEhll1ITpENnFFRpFBtxjt4kw+jABMaX6babS6q3UyRXS8BXDBc5ysilL0BDwcl8ALG3VHBsy0F'
        b's2Vr3d3mQPduvqKlm+E6X5IVn7iqaqdqN4khUZg5RgVViXCSi3g2lq528ZAxHnBGErIUM0K3Ugm99u07QXFQydBQ5fRezsxtSTMqlO65eJJrHAXGw10Veu8xJyVaqMCn'
        b'sfiMm9jMY/4v6vMQI8YzYZTaQmPqFl0Cj9+z9uI9ETqOOtIN0uAHPKmACyGTqAWf8kyzXACrbiwfMj1suAh3dmCPTCpu1GAJ3LeMYElh5gFxE5Y4yihjJ3FK26E9XXQT'
        b'oYplulcoUfWCBil7u4xty0WohEYTy2msAhTTHpfxWRZQ7HVXPLptsPbyHJqkzJkF2CL0bXWUXig3v8kHbVJAp7gZu7GbF28EqDxsH5REO3lShHKtp1xi7hwlZ21Sllsa'
        b'CZdFPKeDCqWUlzbCrYkSg3cOYINIwfKJwVLODCizJ10h88Wd0O7NCF6k1QZgo5QSlc0cL4ZAzWCVBx/mSjOVY/VBcfvswRoPdmCJ1NQGFatEenDKUePBlp0SvaspySJW'
        b'YeNgjSdUyj0PQ6kowo0o7HKTigFnoS+Zt7wKF0mwd+IdtR9Sg9M8Lcudh+dEX5Oj9LMDLvLncHPjSjF/y2DhR5spMXYGm1aI7jSeJ9iXWXWsKopvt2rBZBFsexwlnwMh'
        b'Er8lc6FOdIty1EmgnFJCLrI7uXPFA1kHVNIyqqEVb0mpeucoUsNMko+jgPKKVtqBm3vwvkjmZMMHMqnsdBartvJR08heWsWRcM1RW9kHjRLTxRQTdIrqKB+ZVFxphLsE'
        b'CGzQGE06RVyn8Jaj7nKUkn9en7gPlSNY1QXaHVUXbI2T2LBiey61NWCHo/CSDpd5gQJvRVNuj6fxkWQSJIp6sr4+Pl3QVPI4NriBD73YylppPv9M3pKPXQRMtldHOco1'
        b'nihp1qgg2gZawiNHtWaEB1/WUcIGG+FnlVSdIGIX8dE6Tu3IQprUNg0febtJ1YEWqJkjsX4Nzx5Fm5ayAq523SxZunXAXj3EJzk019ORBXJJuKeOQyFnwlM8RnM9h0sF'
        b'amnba9Nf5WUNrCErbaBBFyjacJSMduATzsdOKJlKbY1Q6agYxQdJ4r1N2WAv2kKx3lEz0mClvYowjtTb9uq4waIReTvGxtx0rETbLMtgyahrDWd9GvWhFeNtSsXtUq9b'
        b'v4OrclioL9o8CRVVkv2dGbeED4nDZ5TK2OB8EN63y7xhdwZnQDYa7qEtG7qHySWumyZgqaRKhVA3j4WUeNJRmpqmkrh+krUfbVHYM0wl1X5awvAyX+vCzUi8URbWOViz'
        b'grJtdjXD27FE8MSqwZIVKQunmIIPAzRKCgHVUkMjQWuNtIu11OusJiB8sJrFKiv2qiXZ5HXNUrzrrpaKSdexJZOb6MIxao2f0VHnwnvh/PGOLQc086DbbFfJMz7RnFAW'
        b'9k3XECQVDla/1kOtZKG2ELyjycIOR40JHk+175033NJASeR+Rq2NkBXa19rNPUqhcYOK/WxIhwDnh8Mz3nCcAgYNntvuqKXhFcmiyVefhucarfdgOW35dAnqvKFTo6ck'
        b'ZLCS9lwpjTnzSpwmhhyeo5K2CC5Ikr5O+vtEQ6y2eTMJ9AlwaxVekni7nZmmGY0nvJnCPRMo4OqaKFnzefp8S4O3NmOXXWzN0EQOjrueSCzUwEk4Q0kFtT2kLR9HKsyU'
        b'TjHPTxMNxR5yaaKbwyhkZOxtgfteGlphg8VezD6PhcckFmzY46eJOOao563CuxLfz+AxlGhysVu0b8MVfASnpbbekHFQuQaeSTrylO11HWVZ/GCrCe9lQiXFgWUDJT28'
        b'B7ftgR+U8TKgEmwboTJF2LxTjVcJS206pWU8I9xBOUc5VqZAV0IcViko4HpGsTVB7FO+jrFz8Vk8ViSoBfkuGVTOi8CntEJeoH2atjQeayLIIeqgPTRHKXj5KkbN9+SL'
        b'lONpqA6JCUgKi1EKymUyaF+kX53ODpQGfmgZ/LSJnzQtE/ihFjvMYgdb7EBLYfXI9LAfZSnLlEXCUdVhzyNKx1GWih9lKY+ptggZCn6Upfzwv2gXPLVOP9Hs8FPU6nP5'
        b'qac2M8+k3a/PNmYYzYfCXTq6/BErnbkG78vLNefx89PggRNXrZGo7dcbs/W7sw2hnOAagynHPoHIxrmQ2q3P3adNz8sw8BNYRpXTEy05Aye7+vT0PEuuWZtrydltMGn1'
        b'JnsXQ4ZWL7rQOmDIzg73dHm0IF9v0udojTTNAu3GLOlwl5367nZQCX/ZgN3G9AVsmXuM+w25odIoxuCK2GgXDoy5L6yI/aSTYAwHzWwJBn16ljaPOpleOhFfm+mQ82Tm'
        b'ATZJlH//PGZ2zm2nFq5NtIhmtkYm9w3JYbMi58zRLk9YG7NcO/MlRDIML+VNNOTrOWPB7FOw1kCqYdGbDfzYPC1to8liSEtz4fdF2nb+JYlz1bKvRbvBmLsn26BdZTHl'
        b'adfqD+UYcs2idrnJoB/Ci8lgtphyxQWOGbV5uQ4lDaWnq/XZIn/MhHzAKA5ZzAvH5+7C0OPb4UmrJTCvhAa4L0qRZngMhWi+0MOPZmdpxwoz/D4XhLS0CT/a7C6drunJ'
        b'0bdBJQOJa0u2ClvzsJZ3nr3IU/Dzi5MLvmkkcqV0uPswwkeY4NUqF2akZbesCBU4CoxYhCdEKU7cmcfw/hze1Pnwplmb8+0taFvOmhrwjMTkebyHj0Xp3FB/kOUZZw9K'
        b'UUsxNi8TpXPDGAbeF7AOyjk87gkhZLRJ54bkaCmMvkrxZxcfFk9pV51GOjtUQB0b9gxb+Qo3LcAWTT6b6ZYRKNU5v0yUILoELk7RFPCgZBmwYHFGqgTDRJbwspIfOFJq'
        b'UUWpwgS4yxnfFUsYbBMZPDcbmUOsG4nt0pLqoVgl2k8j16kp2lqPddKSSuDaZrRJ55E7gZKksyaol/KwE4t2aeznkdsOs5PAEink8wjBhxounl4C71bmJXpW8iELfeEE'
        b'2vhKL8GTWAoewkdJ66mMXSUecONerimC5sduKZSh1dwxi1LEDk/zWdDeEq5TSAwUekCrvU2YQE1T8aEkhEKsVzvmOcVSu1ofvCYRvAc3dPapxFg2UzNekKKVi8fhkWjP'
        b'M6AVKBerXZmjk/Nh+/CZaqBtMVBgWRtNUTYneM4Drov2s+c0eEKx7zET17jWvWrBa96f5YI2LbtBkSjpLDyAS6mzZijZaXfmYmH3CLhmfMejVCWyIA5GJyyujUxSLPda'
        b'9Zvf/WvuiDc2nb4W47fx7IQTI/7t7sqmVd8d3elX/r2NQW3yuvc+cn8S8I0f+TcWTl559oPVK9/74JN3P3sQ2jU+8rvaLqvsj+u0zz0ODqsztUyY73Xh0vvxsUdr5zX9'
        b'6l/+pcA97KMnUy8c94j4+FbNzz9I+nTkyadrNk9MSyk/XLy/efuroy0XXy+v/Oxe4WKPjyYFvjvl3ZDZn0SXrclpeP521+OCJZv+0nbE9OPN77x79rhu6dLfvfXwW4WX'
        b'P1v/s5baD/paPh6zfuKMd6fM/K/v9M54+40fhv2l7TfTXj+3b/PJb8k/z9j8Aai9P/jPBcmf/2TXnD98suHCj0eOKHq39ZFlQ9J339ZXrs/Ot+6436wuHff1tyPebMn8'
        b'MPwtnZuZbabXIrgfQiHltbCgmDC5oIaL8rD52GRmB4HQvQ1uh4THhgbrwvFUKJYLgr8Wr25V7orGOjO7P3SE8q2b8clhUJ48F/t4mKBZJ+cFwtNmFiQsTI7CSkpdnmN5'
        b'cFi4jOiflM/ahO1mnZRSnCigcEi6I3NAuiOzPywYKyLkQnjAYXiqohj3CnSZmQKN1kML0bowNjE0lnJ8QR0l9z623jyZ4wGhRnG8RIAA45QUyoyiZKpEpsCHgXhJJ++X'
        b'B+mYzgo6D/7r735joPr5qEWZprzDhlxtpnQFK5z53CX9ntwDpLI/WDdxE0Ph44JOKVPK3PnLWyaXjZZ5ynzp5Sljz734c0+Zu1zN3mWD76xNLfPnv9lf3vSXkrXIJ8hY'
        b'1UNI4szo1P1KNmO/gvx4v5vdK/YrmRvrd0tNNVlyU1P7Namp6dkGfa4lPzVVp/7ba9QpTSwWM7H7OCZmXCZ2E8zEYjQ+bz1bGzvFFQqFX08gvuXEE3u3BDIYpQTKRfjQ'
        b'za5S8Q0g6bsnE6IwbZlNcXg87QxWJmFNcqyK0OqR4J2vmIcnBJ5jTli5Jz4hSYopoQs6ZIJmmxzvzDkmheitWA9Oweh5KI/AO1idrnDygGw1bgMecI7guCulzFTag0lF'
        b'mYKCSSUFkwpHMKnkwaTimNIeTGZSMPmBbGgwye/POUWTprwcrX4g/nON9FyjuiFR28a/EVyaDAUWo0kKKfINJgowc6TYZ+BSn6v3Tx4ICoiR4PU0ozHHsMpkyjMFc2J6'
        b'asl4eczI+GXsSnHj0EW8NGCyL0oaMXSFL5uCRZmrs/V7tEYp1k3PM5kMYn5ebgYFRzzYFLPyLNkZLHiS4iAe9doj3ZeHSauMbMmDURlF4HrtzDCzJZ+iLXvsxaVGQWMQ'
        b'6xHKJtJ9RdCkeiFoUiVZFtLnELSqXnZpsDwhOC4U2jdK9wfZA7w8LjkhNlEmQAeUa+ZPUG403t/ZIxMXE5W0P6z6OC38Zzp9jD47M3v3r9N2vfbB6x+8Xgs9tfNL2+qb'
        b'67uK2mI6SptLI6t1P/S50FwaeOHErAAh1F1zvfWxTm5mVnYUmvw1wWQZWO6+FqsSLXagnAQ2Jd71xSozu8W5Clr94sPjCCOhegAHoSlxHPQoc+HOaJ3cxei/DO645fdr'
        b'pBujg+jmLaFbBsOvERzFTD6DqKTqdx9Qqn43u3pIsMIuDZrYtU6X6RWm4ewzgxWpG4cbRvB9J7jpGOEMN68wHGjGE1A1uEhKfMulhfJVTsYaC5M5nj2W4ZIVw20oX8GL'
        b'5FAM3VAFTaGKnfFRUFNALTfgqaewG+uGIbvJI+XwULJkjma/N8V67AYbS/87hDE8zPDf7qvZX8AaygTPGdi4Fut5aDQberBOhKszsddnppKy4DrZaLweyccskm0TZ5Kk'
        b'ZHnCWmyEB3h9pRQYdUDzJs3+/WqiViIk5eNFeA4P7EEY2pKwzwF5E6E9IlngWBpPoVvJYPqNT+z5N3neUs58XCb0hhCWygQ51MiwVRYNnYdfgEpHsrCEQaWCg6V0pVRu'
        b'dc90d0Cm8ishs5gg84svy7+5rbtm318KGAxcWPevzmK/JLlkg//Hc8v0bM6WaDC/mE0OYZDJJS893ULYmJv+IqMD+eSqtcu10eTQTQw7V5KPSDfnmShDzLfszjaKWURo'
        b'9yHe047l0ZRxmvTZL9BbQTYa7sSbnm2Khd80D94QvTE4lH6tXMl+RSevj6TfxF7wipkreEN0dHDoCxSd1kS5at5Ls2K2SC7nfCkXJqoZDMYP5Q8RIPv5uxykg2Je/ot+'
        b'kf38fb7RZfP+qcm4THhZMu5DyTgzNhaxjvr7PEsm1Dp7FnyMj3gG9G2FvzBjSrWCsvYj395WICXiBxaOFKZE3SfjTjvyu+B9Ar98tzPmkJTI22ZSIp82QaroU64GTVAJ'
        b'ZexWDZSRJxwp89Dbs/z9Bkrop2xSU0LvlZiSTNDNS8hYizc2sDsHCbMjhUh2KGQZzgljdeoslr/diZkpzAzfxGn4TfEVtMoLciE/LeHDxMOMBuuc6F7Aby08WMZIPKYs'
        b'md/OhJNYx2vjlI6UrCWQbE3hVLa+4in4Rf1VEHzTQp+OCRY2Gre+2aUQe6jJNq9zak2kN8ygjG5KYv9J/9OPC/xzvyXbEuITc9o3bkHKvbWBDRpzUvhrry0/PK1u064f'
        b'fPbZgyUtER7b07x8Pyzq3PmNtyYdnhL5Y401oEPrP3nJh8oHT0/u6u8PGP7pDu2ed1+rm31p3cPfypZ3ea8qLlu74tn2JdHfmv/JJ5XB/mumGEsu+cfOXva1t16vTdr8'
        b'Xn9pgimu44u5Bece9vZ/MTr54fzfzMn4wbXY4M96v/3291pyNP/+B5+lyXPmf9Gnc+fpDJzDm/tDoFTrlHglzzLzrzTc0YDN7uoHHD2UBjl8PbbBTTO7P7B6Gd5jGE/p'
        b'F8vBIigewFKsD2PD4t2ESGxSx2Lbah4YULjcgfc08Vilkygm43OiOAqsSvcIqDXzzbWBdX18sjY6jLzGftlyy0SeI8LdeSFYuR1KsDwimfF6TB6MxbFmdpeUAv4WfEp6'
        b'XAY3nRKzLVBiZuXlFfhkYzxWxzsSSJ/FUDZDsQefvaKTSWGA+z+UiEmRiYeUdpG/4HHJDCkuOS4IA3kXe5dT/uTNMy1vmVLO8qlX6OVvf5lGOkUug9lPv4Kg2ylg+arE'
        b'SeGUOPk5ghhG+7dOQczZcc5BzER6NmkBVDpypmTu4N0mD0erAqoWYolOxi3Um31nhVJe7HOuzaMt6oWvhzhSHnZngry4PFPu+BqI7G9+DcReO//8HRcgWy8B4ZdE7Zk8'
        b'6OYu17n8/T+d5nwpEg9IyRWJ1VKEj+dMW11xeJrnlyGxMwzPglrpwnN9wC57TZUmobCs3cSvkmGLLC0+OQwrErFqA5YlyEesgjYoCYQyaIUG+qwT1vq6QS9e2GOs375J'
        b'LjJmTlRP/Dgt1ClR2PLaw9rmM7KYWa0zwjJCN4Xok/Tqb84IT/tl2pY3/P/1tYYRY9XChqnDVP/6Z52K10Lg4pH1mmBi45oLfjjAA3pmc/yJ2Y/NIQPYc9eTwY8SenlV'
        b'J2oFXJTKPokZg4Uf5S58AsUcS/Ah2KbYoWQEVtrpcyjBPugxM93Ng2KlVBki5cZbi+yVoemSGTsnAk527bbHYHZYte+AVQcya+YVE5lptMNq2xRSpeKlyUWbTGrk1sjG'
        b'+JPFiCMkaywUfuXtbI8MxxLx0YhBds/BVTu/0Su+wtbkVuEfsrVMsrV2F1XdkJ9tNIsOg5LOGshqtOxppkm/h58dDDGuAQPVa6Nemvu6dA6KTk5J2rh+a6g2OmZVdPyG'
        b'lERKipcnxadGJ69cFapdHs3bU5NSElesWq/725nyy+yIu+kWgjCvqHoVq8fGH9otWOYzmIMbgez7cSGkLNvgJpnUuhhH0qLEOh20eULDIXrFQvkhAS6rPdnXrbBOugX1'
        b'GPrg/sB4NpjcTMM0CQwn4i0lXMO+0caPCgtl4jrqH5fy64/Tdrx2jyymqyiyJLCk61xsXXN9c2lzUeClpzGtxZElbQ1d5V2KoFfevFfYVpT1tYLA9LD0YeldAWtLx07Z'
        b'gA8LDwVGk3taIFQGDr9b84VOyR3gZKjNCRn001gOtrBXsYcXSfEU1OJjyRgyjlucbSFjhpllYhoPBVYO+kYZtnuPzuY2gs+xC07HM78dFqQWPMI2+8uheR4+dcmTX24q'
        b'npRoiE65ud+AtUS6y7y4vXhLGfo4h8WYxgwl5++wEdYryMVG+r2H+izoCpKFxIQGJ0mlhbWebBtGwxPlKAoN2slnMWzwmH4MK9kOUe59KgIqTHBacm/jjiuzjkd+uTXZ'
        b'i3X8a42OYt3fY1Es89w5tFjn7MB4VStXn8NznJf4LZbhsHO6fAM9IP/m6kliJbvK1pvNlLCk68kJuRLl7kyfIdUDX0jVXGg50ravytqkLO1/qz+VvRQH3JOkxKZ8GXmf'
        b'r0xs4EHgUI8KN/AEhxIv/ViBYrqsg3vTdkw6ckiQLnw0WWaJBZvxsuPLkD14U/K0d4JT45PxGjS/4G1dXa15Byd/dgn/HmtM4bS07Ov+6YKxe8ltQdxKLd/c91dX9/ur'
        b'tKzMBP1bmaHrf0XA8sHr92ojLzQX6WXvrShN8n27Efpquz64UTy1RNV5ZeyTis4rKQQ3sltX7qs7l5RINbz//sFodfvnOjWP7A+OgKtOgT1ewNuuzrkSLpnZ3dLVi4Y5'
        b'BfbJvGiONQQyiSoKx+H83CT1MSzGNg4wULt5oR2e4PkGnkls8JdOcDoOrQwJJ3PtcT3EUe46Aid4jxTo9NPEJ1LaMJAXDKDXVGwx868VlJA9xw+yAY2jBjiZBHVKvAzl'
        b'UDMQzH9VSdGLO3jSbWY5HLdGD+DWKoZWXoQ3kqf3kpkmOJBLp+jXMKRLzTOx8MDJ5790QuImwIFsjMoCF2R7Y8TQEwy4PkmIf1HSbH171+NlL7NOkZS0WidbrZMnrTa+'
        b'+bsPleKnRPL6j/6Ycvr9DSPX+Vk/efrEQ3dWGVn49MDXdq1T7P5GhWdQ1nfebVKv0875fsC5lQfGVO/+7IT1p28vfe/Jm94t4s/eaUxd7HNg2qJzBR//59rlr4hf/2nh'
        b'85b+kq+vHjV9n/97P//+lP5f/v5Q5CeaB+6/2qY63fOuMfWdC2/8dOq/nWys/2J3Z6Ln8e//rO+VTbVLFgZ9fbdiedGYV5IWD4v69sqTU94ObSopuZ7VWr1/dNeFqaGG'
        b'sd/c+nrcpq6LszsNAR9/77XVc7oawrIN4wOy97gt/N7Xcv947/zRX//8tRjrHlNttNl08J17qjXz4i6GP56/2ucb81+PTSq4OKux9bzY+P5bqnBTbN75X/7Ec/Mf9lcf'
        b'U/t/508L5vrvvnDp+69gzm9/kX3+B7/dO/f7k7/p/tmh16JNVZ+WRU78eG77uelVs16//mxm56PcTxd9NPbdQ6/H3zg4+/2PdZvPVVf8Yjj+MtAQv33rK6/pqof9R8/G'
        b'7/V4fbMzaPvbb/1u6Zb6OI/tjxI/qm0N/nZK/a/9tv35N3MeD5+77nLQ/jd/ag3/dMPPY9bML7j5eqRNv+v3N/z/8Ff0fvvVlr6wsf/3O+8c3BSZGJhf/MWxilG/LD/e'
        b'98nBU0WVN/8j0/zb85PNM29EfGehx9tHf5Qe9smb2yrWx6r/8+qfdlRtfPLxX947+93MP69/b9Hkbz37runx+29cPPKTV2urtZ+v7PnTmP/ufW/Wf1nJjrnF3QVrElZq'
        b'sC5BJsjmCQRy8MTMfKQ3nKf0fTDLVk0csCdK+G9Jp5U392L1kPTejgB7oJx9b9SLT5J8dCZWUthQHaYW1LvkW7Fx8sHpPKvGVjiDNSFxYVgWm5Akm6gSNNAlx8vYPZwz'
        b'oYU+rI9nCEw9sCoWL6pYl7tybIdi93/w/FPn/Y8dl34pHZWJ+YyXvnFscE9Nzc7TZ6SmclxYyZzMZLlcLouSTfyrXM5ORkfI3ZVy4SX/ZP+kp/9H6UmfZPIv1O789/++'
        b'fz3qJF8Z++cuG6FgFY4JS+WElX4jPUlS/rIJQXLW4s3ffdm7aeIAAhOIylNTnbBz2P//nspMkxxAyyZi+i0dE/1wmjPIaunJvlgoJQd3Ck8xt09e45QbmcsFvD9WEQBN'
        b'0Gd0e/JtldhAPQ8Y3wirXOwJy/yKf54z5/lqv1Dlv3195MExmnTdop6167OCYxfoux+sSHzjB9/ZedqY+ezUunWLZjR9Y8rl382MidhwbZp58reybs+qiP/8zvEQ0bTi'
        b'yYNffPrqH7KVkZ5jjpdM26Xc02NVtyS0+jx/40nUp8uC7/91zu8PVr/+75+LypHbMnesffjTin3jch9+9NsF7yf8PvnDGT8u+/SPqombdT9suKUbJuW/ZXgTHvP/cySZ'
        b'VsNqbRroxvqDcrwViM+5Y/WJhLMs/e+akce6sbrZcOxTQDOcIqjgmUP7pDhJHszbQLUkjzOeIxQT49dIhbc6sI2Lj00MTnQT1Fg8SSl3x0Jyy/x6ziWwLQyJUwmyeAEe'
        b'bqNQ4ma4mX/15eQSCqSc4i+4BrelOlNEPGFNDXm4UwphDXS50dyPAs3sTA3uwa1kl0GXxrIxamHMSmUwwUmJVESs3bIQbR5RWEXAEhFcYIeucRYllGLfIn7lA9qXF7CU'
        b'LR4r3QRlmAwK8RHcXj3BzHTAPWpkPJw08WqlEzPj4ZKSmH6cwOFt2yYzVuqoi6QpMsEHz2P9OkVK4GHOrDZq7EB7KNSkw5UIKTuUCVq8rxKSsIOjIJyH+3A+JDkUKzg/'
        b'tEn4zAi9cnwAdWqXFCvgnwNx/8Q3neLLMNKYazTbMZLlyMIwFi9RxqdQyhgSsKzPl8dQLIryVExhsVWESetAgUn9imxDbr+SHb30q3jtoF9JuYi5X5lhTKd3yoNy+xWi'
        b'2dSv2n3IbBD7lbvz8rL7FcZcc78qkyCafpn0uXtotDE332LuV6RnmfoVeaaMfnWmMZuypH5Fjj6/X3HYmN+v0ovpRmO/IstwkLoQeU+jaMwVzfrcdEO/mmdB6fy02JBv'
        b'FvuH5+RlzJ+bKlV3M4x7jOZ+jZhlzDSnGlh20j+MspksvTHXkJFqOJje75GaKlKel5+a2q+25FooaRlEN2mxASb2PzKZ2PfYTezMwcTuHZlYhG1i350ysQDXxKzGxBIJ'
        b'UxR7Y1+YNvH/FYClpCYWH5pY8G6KZG+sqmGazd6Y9E3sK4WmueyNfTHbtIC9sdK8iSGhiWmridX1TOxE2jTTgZVsOzwdWPmnlU5Yyds+dx+4Z9Tvm5pq/2x3j5+Py3T9'
        b'b6C0uXlmLWszZCTp3NkNoIy8dJIJfdBnZxPka+2qw4Jueu5J4jeZxQNGc1a/OjsvXZ8t9ns5Z4GmpQMCdHqT9G+R9H9NLWHemVfolGqlwp3pWLyfjPmb/wdq7AHY'
    ))))
