
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
        b'eJzNfAdclNm59zuVMnRRsaBjWWWoAvbVtSAuSBOxNxhggFEEnIJiV9ShV0VQqopKVYoddfd57ibZ3M2XbHa/ZC+be3ezuWmb3Gz6vckmm/uc886MgJhNvi+/3734m2F4'
        b'T3vO0//POeMPhDE/MnqtppdxBb2lCzuFTGGnJF2SLj0r7JTqZK3ydFmbxDA3Xa5TFAr5gjF4l1SnTFcUSs5IdA46aaFEIqQrkwSnLI3DHzOco9euiVcfyE03Z+vUuRlq'
        b'U5ZOvbHAlJWbo16vzzHp0rLUedq0/dpMXbCz8+YsvdHWN12Xoc/RGdUZ5pw0kz43x6g25arTsnRp+9XanHR1mkGnNenUbHZjsHPa9BH0z6SXL71UbA959GYRLBKL1CKz'
        b'yC0Ki9LiYHG0OFmcLSqLi8XV4mZxt3hYPC1elgkWb8tEyyTLZIuPZYplqmWaZXqGL9+343HfIqFQOD7jiNcx30Jhm3BsRqEgEU74npiRNOLzAuIW7TtDI4tPG8lQKb1c'
        b'6TWBESTnTE0SNM7x2Y70efY8qXDH4E6fUgKXJqQJ5nn08RBe94XbWI6lWJwQm4hFWJ6gwfLoLRuDlML8SDk+g3PQbl5EXbEHruVgN9ZQ3wqsDKABWBEVhxVbaVRpSGJU'
        b'YAyWYVl0LJZEK4R8qHTaPTOGrxwboRQ+nk/cUqdkn5bnC+ZkegiNG7AeB5xcE6NowrLoLVHQ44dFgRvisDrJEYujttC0o9bxgBtb/aJisSI+NmGLH7UVhRCliVEbtvgF'
        b'RUUHSqBTLpigeOJiPAe9aZIxiuZm48umLxFUhptVFJIiKYlCSqKQcFFIOfslJ6RJIz5bRXF2rCic6BX3giiyRVF4CUoha880xhCXT7YdFvjDfzFKBfkGNi7FZVuMn/jw'
        b'ZKqjcCdlFj1Lcfk061XxoTRFLsjNXmQ8KbH70hKFDiHbmR4/UfvIf+slrP7lhALJhz5vb3Xdqhay2XxnEuoldxwE9QJN4PzvhWUsHRIfrz/xa/cL7hK/X6pThS981uWt'
        b'FYYFcwg1rAuEDpIJydTPD0tCooKwBDo2+5FkKgODo4M2xEkE0oqLOe5OK+EUPNCEMFqE5cE7jC7EdawPmylAHV7bYZ7M5PwU78Ejo0FBLaWTsFWAIrgLbWZvajsAV1cb'
        b'DQ7UUo7NuwQowd495klsUA2exm4j3mN6VwUPUwUoWxVgnkh/vnripBEqiKPYFg1nBWjCx3CaD5qw2ItayAbwKvTiQwGaoRK7zEwC2OY3y3iQkVBpzqR1dkGZ2Yet00qd'
        b'yozYp6Smi1gNRQJUYd8svhJ0owXPG81sWLXTFgFK4XwBb8F+GvbQ6MpGtcyGcwI0TJ8jjmny2mvEAUbeJbwDl2i6Las4dXgJhqYaoYx9bITaEAEu41MnzgbsxEo3o4pR'
        b'3rpoFk22kEyO8+4e1mKT8RDpL9bhQJIAFbSzej5oCVZKjcyasRVaVwpQj+07+ELu8Agf4ICrnJtsBw4J0HJ0A2dDSjA2qbgkuo4Sb6FerhfXGYKyE1BK0pM4Qhcb0Ys3'
        b'4S5fZ03OdiP2M7nWQMUaASplWChu9VTQZBwwM9qu4vWpAlwIgG6x5ZkE+lR4hy10W7aDCaIlgk+2OwiuGA9J+WQXs5jA+6aLQ2rCEox4n9HcoMJBAapXYzUXEbZDH/YY'
        b'3blcaWO3iHH0ZIgTbtYSiwYcWdt1qIVqAa5AGd7ifHgdazTUxoi4iQO7iQp8ij2cDNlyUu8BE2tqwO6jtKldqZyMmF3zcMBFyYfcx1oSZwg8EkV+HZunUBtjxK2NkWy2'
        b'Nme+TsJsbMIB7GO0X9sJbaT7Qdgm8rVoB6nQgBMb1BuK3QK0QQvW8mH52Idt1MaZlCAV4CqchU5xrUtQBhepjfH2jvMJAa7NSOIC3Dv/GLGcq52ZFKUaHyr5QhNIhWgy'
        b'V7bQHWI36d3VVXCBt2EX3EsjAgckXNNaoIG4NDuct+2EUxrWxEywpwBvMFE14mlRJBfxkoGkyImfd4hZ2uB+3rKjACpUjuz5PVI7suh2LIkRN3wtBlpV2M/muwvNCrar'
        b'h3iNM/0EDM5U5bPt9syCctJyuCZOh6cmeKrwHuNfnxavsIV63DmPgrEISqmJbXgAislyW+C+O58tLNKBGthsd/ER3CTOmn1Fk7YQTRVGEyOvCKqhXoDzFCueiUv1HMlW'
        b'MXeMt/OxjgwA+uG6yKXTWI2lKme21MNJcFuAG9iIJXzKQ8ehcGcIlC4mV3QXyhSCDK9KElZvM09lLFyJ1yhS3YDSfLwA5VCiEORZEjgdozWrqTkcKl6zNoXZhjtB+T7s'
        b'l04mVR3SyMyebPkazSIsJXnnwt14Idd3oui2yqB/ZwyRm0rE1Qmp8NCZP1+BQ/AohkhN30/OJx1v4RXzfLb3Qu/t5DGKmIVA12LoUGjjoByv74uAazvjhIVGBQn18Ure'
        b'9xUcXMX7XtzJuvaS+7tAf3UtXkge4KJcmI7lciffnbwvNkFFNuvssw9Im+AW6xwFvfa+8EQum3TIHMD6PnaCTtaXUodSNnPPiJm7xZlr5Eqsg4d87mCoOoK1UUugG7qJ'
        b'YnvnMLYKdQ6SkdFX7jNruHrNgIbNZP21vAv08v3B0D6VGkvh1tYJwga1g2oDKXAQ9d6MfRQojtg726dmCQ/71ckWCDIoDhqxwhzM5r8cQcpXGyVSUi5LFWeHa3g5GdqI'
        b'j1BKbIzCB0q8m59ofoUNGYRnpCi2MbTEJmfGGfkmYRoOyPAO+ZFT5uWMMb3QC6dEajgPy8dy51Ycm6Q7TpkaJ0TD/YNw2xEewuBW8wI2/AItVMcW6qWF4CnRw0fKKFYW'
        b'40U4n0HKdVkIxRYFRYnTi0WGXT5OYYaWVLjYFxPl1inKrVaGQ+RWm83+XBRX6C/qvRmejNWJDlFyFrkD3MGHnKIZidD/nLm23cAFuDRKORYeVUADuednPLdIoz0M2UY9'
        b'l/a0mdS5XOQCGxSGlQpodfXjKgUXjpMXYWP6yKvYFdDGNZGyHrnjNHK7C7hXu4Y1M9e8sAoN7Bbp5HoYRLZqhCLaDdOWI2Z8TJbcaRvVyUaRiy1gvIXzarhK6hWHTxzC'
        b'4G44H3EAew/a17BqIknm0T4s3Om3WKTLCC2OlBUX5XH9wrJkGMQzKtuorhdU0kpYncKYH8xlgs3Qu9vWv8dqzwvw2r6ICDXWcp1PwGaH4KAAvkIItmf6UzZl1+FRy4ic'
        b'k5OgHyv2bcZ2boDOWH+C9b9HuVy3dd+jHMF8GT523c/7ekHxLuqL/WRuNn0XRd3Duk7DezLsO+HN2YMPZ5nHqAf1dygYrRwHFeSun+4z+4l5Uds0Nv0FF67kttltrkAm'
        b'w9tkEBaOXFLwwgE2/QJPkX0vKMQ1uUOQP0cuh/Ayhe8XSLEOkEO/S9yadQUUdXvmCQa86Eh+uiaGWzeWzsdeNrJg1Sh/E6FWCAuhVQEtDtAommc7PEofzXYyn6N43k4W'
        b't7hwvKKAmh3Yaw5lgyxQmP5cTcvtesefyIgw132LJIlroU3hsJTE1ysy9uZEbQz3FNR1lF5gabrV1W+CcodZlNzc4oyFzmNyO221SVbPxuMCc2jhcJd8hgKvi86+MQ7O'
        b'UW9X11EiDhM3MA37SAo74R4XApQ5sIRmpIMthDar/5sOZ0hzVJRAMVekJsMvYl034AO7AEZKFywyfLQEz5rnMCLOJawa6VSJ2hrWWcrc6n1SsvnpIrGncuECdZy7aow+'
        b'9orE3iFi86GG931NFs+Uq/IIU65OW1dy4HbtGiQed3E3tWvPiRfjxtqpC23qw3kRipcVlAfWwQ2uAhsIiZSPGsXnb3RdaHP24qhtCsIYLXiX23f2OkpFR5k3DGEXdo2w'
        b'742xDssIV3D7XgxD+0drGRnebunorYTDMwVBn+ZIcxhjUR+BteJRg6RpVjX2oCUeLPaEmrlQtEgCV1Y7x8NNV9EYe0ilyRtGvU6Ba1RktlmYRob3N0ziKgmP58cQ6jr3'
        b'omO3unWrYzMr8vT+XB1mQSORSOLonDFGcl2i5B7KyMuUwXlOjOLYNj71Nah7wf9bs5VncrcJfiLlTZSQdjHKJ43R4G5x6l4Z9qZhI+d/MoWz+rFeXH5kJPsDHZbgoDVE'
        b'QkcBuXPW/SrTlvH0iOnxs21y0Ss8Tpw+PudhYCe56bP7VmsJNAiG/RTpsStGzELuO8FZux7BXTLjEbtVeFnjfDcFSH+oE9dpwgpJPtiDV88ojz8i2YFahQkrjXzQIRco'
        b'HSc5uhq/cIQvYlreRn7OkfJkJukQSfbzCFk+emgwXicDURxcJNno6LAYyreIEeyMdsNzuvqn2RnWrUglLsQJYZMVlAm30lZ4sC+Cx5TpsASyhuRtC19WFosJJPTL5VMo'
        b'2HMPcC5yD+st9xmbsvSIilEid1yNT3nfaAIdl5i3wPtjVVrUoldl+MRdzn0zNJueW+bznpTV1o+xZ6xVQOPho5pYDkzglpPKhj7ajhP4yIQ7Yk2jDJuSjBx0FlOCTvDb'
        b'kkm5BxtzdB/eNOIgG1SVv51QfiReEosGV0J11qIKVkMJK6sUQTuHMhOwZpIRyhj0bd4OVQI0zoMWPtsWrMgwGuQ8vJQvFghWnjLxhlDafrO1EjPbkzi9FGpFMIUDR611'
        b'mHnYRbB8GzGM09wWHkDon1FSAZVsldIpFLs4aYVQiCVGZ0ZA/Um4RnjxJLbySlDUpGlGKGEEtIRMI8LmbhCRWTU8wHZbUWcV0mxlZEaVHNLs9sNHRjc22eUJDP/XuawU'
        b'cVnDSWywFXzwOjG0iZhwX6Tu8fRQW8XnID5g4PU0XrXyoAlKrBWf7ZGs0FAeJ6LQKfm2cs8UvC5AFXRpOT9z4AF0UhPjQgM05VPWucSZtxyktG7AWgbyRAurA7Wv5y1k'
        b'cVBlLQPhQCLDtHWZItl90SftdaAKhk+r4DQUiyD5MVyEYqOIupvwko6JtTWeb2kh3iQ+iKWg16GTZiTA3igy/DQ8wlvW6skmfEybUhLEZ5taDxfzjYcUvIZ1/zWBolD/'
        b'ERHvPsShbFtd5ZgnE8EZsUoEDxKhiFokPO3qltF2XfCBqMGV0dut9ZZX17Nqy0O4xGU0zRhsdJfwWkgtrdIIvXo+wIxnKHO2lmEKdglwJb1AXKRjUbatBAMVe5mAnhLs'
        b'Y8oQRy6ux16DaWVVhErC4EN8wgwPGibaQ+tWE7HHB8XK0hYHVjN2kfN8qxqbaSnjbLGGVpg8yVa6MceyGsLNHbxhNl7YZqvbwDXaZ/P0QFEMJVC7lpbhxYr27VDLKnJX'
        b'lJzwJVh/AAfcWMttbPci4EnK3mZlnPYgDoha178dT7FCQf1+sRp1krzLwEHW0oin8D5tCVrxMidjGT5SURujr+l1ViSq0iTxhn0pcfbqETYcps1qvTm3oWZhmq125K4n'
        b'U5wncnsKVofb6kab4KkAV6f68IaCJYttNSM1K7Bc22dVjy1YQ+RY60b+CtKCbVJxidNJmfSc89lXQyvOkvA97gij7Q5wjW8jh9MhQC0+FM0kFfuPE713OaPXkhY0HAGx'
        b'UOdJXrIaB1zZ9nuxG2+z6modXhCHxWTbylNarCeaiaQiUQy1+FRObWyxPvpHYriGdf581Mzte+2FqwWsqHXlOOVabEt+gT72utXCCdzyJ3Hfk77qqArvMOp6tpC+N4al'
        b'8ZnCoHyqrZa1n9UJmyIJR3CzujATnqgclbxi9eSkANcpiIgyS9wGD6x1LoG0sJ1CcTHnmwQr9qtMohaW7qEt6ES1IRV+AtW2+tc8JSt/DfjxplC4BB3W8hJlALTLG8th'
        b'kM8WjY8jVflstg5lOLlRqMjlz+cQyKpR5bMhXZPTBLg0NV7k2APshjprKQ3PBjC30wM3Rdu9swce24ppS4gBTcoIzoCkPXjbVkmLw9MCtKyBVnFIUU6WrZSWjxWkaBl5'
        b'1rmgNFPlxvY/pA6mwEbaJW7zRhj2qdyYpj31YlGpk4xZjD3Qs4Im6+M8i1hFc6Flq2ifjzJnUgMb8wAfslJOxEnekI7VR1VOTGmGJHBDgJvYsotL8ogT3FKZeRV7w3La'
        b'vfcJ0aXdCYZT1hqejpFbHw2iZeIp0wyVUSw9nmVTNZM7rBPd8VPsI6wjKsaTSVqSMmV3reaFYu500ZtlQlAkVvBajpFr6LGmdlDEq35yGNgMpVuEbXuU2CI1aOTmKTQ0'
        b'AevnYmksc18bsEwmyPApJdFYJBN1LhTPx2AJlu2JVQrSvZIQMotq83Seh1yC2zFYEYLlARocgtvs6MrFQzYRmw7yocnr4X5AfBr2BUXJBflqCdHSHr0+jZ0j2X5oJ/yQ'
        b'iR8wRQn8TIudZbFzLXaeJbM4ZThZT7LkRfJC4bjiiNcxOT/JUvDTK/kJRdKIzwuEdBk/yZJ//5ckDmf1iJ8IdhxqVGtz+DmoOiPXoM7XZuvT9aaC4FEdR/0RLZ7C+u/P'
        b'zTHl8hNVf9sZrFpPs+Vr9dna1GxdIJ/wdZ3hgHUBIxs3aqpUbc5+dVpuuo6fybJZ+XxG8wHbWa82LS3XnGNS55gPpOoMaq3B2kWXrtYaR811SJedHew86tHyPK1Be0Ct'
        b'p2WWqzdnice97Bw41T5L8HgDUvVpy9k2M/X5upxAcRQjcG10xCgK9Dkv7Ij9pBFjdIdNbAs6bVqWOpc6GcZdiO/NUDByMZONTGLl376OiZ18W2cLVseZjSa2R8b3pISg'
        b'8NDFi9VrYjdGrVGHjTNJum5c2oy6PC0nzJ998lfrSDXMWpOOH6SnpGw2mHUpKaPofXFuK/0ix7lqWfeiTtLnZGbr1JFmQ656o7bggC7HZFSvMei0Y2gx6ExmQ45xuX1F'
        b'dW6OXUkD6el6bbaRP2ZMPqQ3jtnMCwfpjsLY01vPeDHt2xGOZ1hu6YUdlF6yRKIPu/nJ7KbjPoIpK50d1x7bHuIpiH6piVxnN5SykVBDae8OqMdTvL9+nbPwxhHCwx4p'
        b'sZnb88Xj3ZhX3ITDe1cJwoKUQEVsjiCexvTm4mmWGMJ9bBFYutSw84BGPAsJnArXWVM+PhNb9lDwZg0zoHMxOz3E0jkCO+6omIIdPLTk4+2F7PBwmZ4PqE/Gx3yAk24B'
        b'PznE22pyuxQksslJ8uWvRGAzOzoMo8cMItSnEHZgLe5QDI9UeTJ2zvRIYMdzl7au5Itkzl+gOigT9kEdOW12Mnd5CR+xFNoK+GEjPt4kcaSdQT/c5256NeG7ThwwUuAs'
        b'LKDcQ+C1bSsUKiVowk8i5VhMGTAF2yRCVhP5Ns/iZX4UCUXJlLVSLrvUGsJuOs/lB5H6WQJLSJpPUMzl+2l1xX4VscZFy6I75Q/X8a4Y3KpxaA0O0FYJQNJer1CqtneT'
        b'GMPuubobDzlQDvSA0noiYJGVz3jPATpYZn50C6esBHv0GhlvStqZyRqgtsDacp1EwPZ6LB+KxWW6iAC+DNZBkwhSpP5sHbjoL65D0LFfBH2hUM1hRbqWt1RhD9RppGJg'
        b'fEb5MG9MPiQ2rsQG3uKNg+H85Dk2lDJTltHfgLtc1S5SdlGVwm9muPxf30UCl9s2KFSGL5ALrzDVqBVSof2E/qxhpdTI8rd3fxm7sio0XrbGJfI/fvVOjjRdddlvk7O/'
        b'v3P86sg1z6I8fc8FzI5MXb/WecNUac17P3R87PrVj30aT81Z9/4H64tv9H3U8lnujtQpC+6p+wpn3EtUP3M67FoTFvC628qME0+q3lcUr+yMj53++YKbx5bIfvPNj5e9'
        b'bl7x1g/nnHni8OPv3sla57v2ysb++YnvyuN3Hz/rlB3t9xfngtkFO3v0LWtXHH7zT2kVb5X/pu3XIT+c//obU0/89E+b/3D/1wNzcstUv9s+dGn5Z+f+6Uf/sadlwxM8'
        b'Flx9+vV75/Trvwg52Hrvinxb726ntRN+UvOvKa4BH2gfmpt/+9Une2+GvTV/rrIlJu1n6xu7p+HU9p3fVz5ssEzy2enz9C+SD/0ydr07Q+NgYvzd6YUPAoL8ooKkghIu'
        b'SzdOCzqCl03sZhBWr4GWgODowP2J/ppgrAwk1RV81PK9lBh3m1gKMQluxMckBEHxHuhNwBLKFFSJUqwIX2ViObXWEy6wqzn+QcESmvuMFDuPhcP5QBOrZki8dlEOLF6R'
        b'OSRekckPIh0q8seSEKkQDE8UJPgjJnZKiR14Cs5haVxgNOVMgnKhFB9Avds2rDepqdlld0IMmyGXct8KoCljeT4zEc/KqN/14xrpsNRPwyoHgsaJ//qb35gr/ePEFRmG'
        b'3CO6HHWGeBUrmEXa14adud9PZn+wbsatzPeeFDRyiVziyF9uEqlkksSZfjvTP/bchT93ljhKlexd8vydtSklPvw3+8uN/pKzFul0CStuCPGcGI1yWM5WHJZR9B52sMbC'
        b'YTkLXsMOyckGc05y8rAqOTktW6fNMeclJ2uUf32PGrmBZWIGdgnHwMzKwG6EGViGxtetY3ubwfZ2Svj5dKJbKlHyd+mfpFLKviTCF+wv82wmqFvkAatjRHGOksSkw0wW'
        b'Lf7kWKZxn7N3WQy1YWk8ViREKwS3PANUy5YuJlzFFGtpIBbGxMbzJDMW2wIkgmqnFHuTlKLHupLvSblpIlTYctMieZpsRARk+3KwRcDXBPuVKXmG3JpUyopklFTKKamU'
        b'8aRSzhNJ2Ql50ojP1qQyk5LKDyRjk0p+s25EVmnIPaDW2vLA0Rnf6OxuTPa2+a8kmQbdQbPeIKYWeToDJZoHxBzIdt1vdBaQYEsOiBD/TbSi/oAu0mDINfjzybTUkj5+'
        b'7sjoZeSK+ePYTYybOFk3JY4Yu8PxlmDZ5vpsbaZaL+a8abkGg86Yl5uTTkkSTzqNWbnm7HSWRIn5EM9+rRnv+OlSpJ5t+Xl2Rpm4Vh0WZDLnUdZlzcE41yh59GM9AtlC'
        b'mi9JnhQvJE+KePNKFl6L45zGu0BYHOu/IRA6N4t3CdmDDexGYjS7a9YFxapleA6ebNZPd6yUGNk8PX13fpYS/CONNkqbnZGd+vOUvW988OYHb1bBYNWy8x11bXV9hR1R'
        b'XeeX/bbtfGi5pr7t/Kz60+G+QqCj6nrqCY3UNFfgR+rXsA6bsUXlT0iMUo2yOHOQ6D1nwoAcbyfkmJjdHt66LSZ4A/lOKGcGCYPezCanwqA8RwmlGukoV/AyJ8j9wbBK'
        b'vE/63Oe5iT4vnXk1L+7b+B1Nq69SDDvaFGvYwaoiorNxYW/ssueo5WUGdpvE4MHenOxOiE343RFOqMvr5U6IdVk0GW7aNrxGZ/NBfL8z8bz5VeoSfOyVkZiZA+YOvChQ'
        b'anGW8rkyaA2U7YlZCBUHoYeePXGmrKnGFZtmW6+2YRfh7seq/MVQ5EaLU3ZK+WOr9fbf2ZlLVPmUK3UeZE1FlLTkoTUPbd2I5414b5qje5hckGKNZJK3WOqENopxTcYw'
        b'CbYQ6yS5lChv3CzWS9opAy9V5R/CU5TuSPCcQNnijWkaEaUnBsEZ8oQBcNnmCa/hGX6zZwsW59hAOtyKt2H0JOjnVCZBJV4OiJ9GaWKFRJBChSQiFp+94ETtMGI9c6Iy'
        b'7kbFO6dSi2OGo92Zyv9mZ5pFzvTPL0Po3AuMxucvdSXM7bDuX45zXwI/2eD/cfSZls3JMupML+LNMQQyvuSmpZnJa+akvUioDXFGblyjjqDgb2BedR1FjzRTroEwZJ45'
        b'NVtvzKKJUgt4T6uXjyBMatBmvzDfWrLc4BG0aZlQzPx2un9SxGb/QPq1bh37FZGwKZR+E3n+a8PW8oaICP/AF2YcsSdCs7nj4ma2Sc7nPBEt06zpzMEX5I1hIPv5m0Kn'
        b'fcbcvBcjJvv526LmKOH9Q+G6RBgPrrsTXGeh4rVEAndiyInAx18SdUaGHIKs1RwmLVZOERYs3edAsH6F62SNCNNTJ3gJc4V/JRtPORYomyJiJ7iNpxI41IdGfLZD2LFy'
        b'r4he78Jjvc8qKIUiKKIQOUHihD35fJ5Xd7kJ0z02OxDcj5WemEf+3Mz89a7F+nA2zePloUJowiFeEt0cDFXhtD9owcYwISwK+/kMQz4egnp6qCDkpWRP3pXDZuC3BwcJ'
        b'Pj9ik3gG0BzYg2X8uYuEwhgvnbdg50Zh4ytYzKcxpjgL3j6vSwSPFJdvK/cJm/UHhufJjYPU1D1nyysVoW5nVntE/iXwn6X7urN/suJM5i+dvb9SkZoasbYvJnbhcFTs'
        b'V5plgU/OOXx/4y/W3ig4+cWf3p5sWJakmFXpOdMrbf+7OR95djXvNX1U8vsNWdfnx2cdmrrH8KrXJ42etQ5Rs9f37/2XP0puv/Vfpn+K6m3+C1ypz/+P7k1tzUv1F3zP'
        b'br/0sUnb0ue0Db99buDjf9/2IPfj2b/81PnzKyt1N+/sMv5+q25jX/hb5toPNEeGOjbu/uLN3y6qdvPTOHII5UDC7yF0xq5+2RBa0AosMbFs2wf6UkbGfl+oGBn+scLX'
        b'xK4BLcJWrAmgXBqKExhWC6E+QWxIjIMQKluJrcroacc54AtdPVkVg2Uaex4xEZ6tB4vckR0rmHhJwnIg+STcI8xHQSNfsgbOYxknlF0+oz8I7YU4oSWBkXpC6r8yx8Qv'
        b'GR9fzsDbUkcbfHMjBNksYsxSPLU2Bstj7ADTHS/ggwWyTCh110jEvMDx78JrYqriJKIzChU8UVkgJionBcEGz9i7lGCWCwdkbhK5lMGu2fTysb4ME0akMs9B0rCMvPaI'
        b'DObL8JVsBL7ytmc1bO5fjMhqLkx9eVbDvqqDT4GwLEV02UIRXIl42xMtMihL8dVIOG7CO/hkEZbGwvX4ETV9OKd64RsldnjEbndSXJdmSO3fHJH8Td8ckfEv8cj/+H9G'
        b'ubZNomt8SYafwRN0HoRHlsz/pyHRS32zjVujfbNSRAN4FW4qmG+eAw1fjghG+ubN1vLj9pnwxKiHDvGonxXYHmIxv3fiOOkVMjIsicOyJCyKPSxIvSKhg32dCRrog0bY'
        b'6OEA9+AZnNVP2Z8hM7Ks9n5t7M9SAkegiu1vPKhqq5VEhbcvCEoP3Bqgjdcq/3lBcMpPU7Z/zeedNxqUQtLnT19xVZirNAoTu7i2PgWrRnoUWrF3pEsJggu8ZuQ13Y05'
        b'pQtqu0+C+l3cnsm9wHlWMxIrRlAcbCsaYYcz75GRQOr43MvMd+F+hpwMuZALvNyz1xfO8qqStaSUjHWsqgTPfERblI5r8A6ZOpPd3D1s5j6LmTmvuEgMk+zm3CETKx3j'
        b'wpAOidjIzZSN8SHbMapFMz0lfOr2ckNlx2NwEWuibeRDDbTZqmJrse5LrFBqEf6frbBzlBIn5WXrTUa7qYknF2RPavY0w6DN5CcRY8zOZrpa9cJxEfSozn4RCVviN2/a'
        b'EaiOiIqMiEnaEkfQek18THJEwrrIQPWaCN6eHL8lbm3kJs1fx9vjWRgP6q1hSoFkNNNdnRL4aFOBYF5CDw+6x7Lv3AWwL+wVxyZGEcg5Anc4zumUY40GOpyhoYBe0VBc'
        b'wM6QnaEIm7Tilc+n2LBx5GiyLe4oZxDOuoi35HAVH87VB5z8UGLcSP0HOo5NfLvP9ZTaO/LdQ20G+ZEfpzhtU7u1fuXT97Jin+5640bq0Yr33v/dJ94Tm6s26wxN2b9Z'
        b'47Rk8mtzOxQ3k0J/v2JeYcsXaYMf3M3auapskufAOxEauRgtL8P91IAgOA0tfs9NqC6L43UT3DGOCsNQCU+sJtLyKq+7QjE+wacUU+FBsr0m6uYGZ7l1ZnkciaEg73M0'
        b'JMhPKTj5SKEt8cQooD2+BTkTJjGOAPfeNiMKdeRRkhU0OcSfajckw+Sx0/nYTYf18htlOsN/xXRYjINbWHk4ICrQP14sVTDBTILH4XhdPjEBz1KMY06KIHknVlKQo3ZC'
        b'8ZUheBEuQYnoLKaelGftzXu5nVmLgfzbk/Zi4N9jawy/7hlbDBwZ9HjVLEd7gCOlcWIdw0nsPDBPRw8oJo6OPtGixWVrTSaCPWlaClyjJ+UhUJsu1htfAHyj5rKDvy/D'
        b'fiLW+98agyXjegjHeDP74vUmrMn40oqc+8oXIjAFuOsiOgokdCQIC1onH57etO+QCITwwsYZRg/187B8P51f79w5F7pGhmU4M2PcuIwDAXzyM1ruvzw8vI9n15qWC/rE'
        b'DG+5cQe11Nz88+hY/WlKVkas9usZgZs+Tdn9xgdv3qkKrW8r1EreW3s+3uMbjTBU1bfnax/cOPvKOUV385Tu5i01bXWSW813ld2vnROrg7/9t0nKJXEaJY/kG/OwlEXy'
        b'vXh9vNIgXkWLiV+uL4U2uDkCHSTwqjxWkANKgpY4hbAkXnki/aRJ/GLrcS07KoJmqLB5rcgYHtXnJMHdAGJCjz302+L+bqzibm3CEehUwU1sHYMwyK0pKfAzQAN35sJt'
        b'4q86fBQdRMRMqJFj02sONkTwZYVKF54MkFYzm+HObJLNmUUyF+YicZaKWYGLxDDd7s40smEVc3/JuQaWSozID8ZdkKjxtbs7NsvyUe7ua3+lUMlk5JSHT2MSlmJt0Pjb'
        b'nQF3NbL4+PUayXqNNH69/mnGQpmR3Sv0MZm2VO1ImJDo/dXPnoTvuRH0rbVBHz/9zLnk8fbOTyp8IhXeg59+c83atVd///Y7Q9trGkL1nzh83Pa72iM3wmddrr3S+Jcj'
        b'NZ8HfH5tSh3E7rq2pPuzmF9VTNl2pue13rk+r/4InD8p+0Pd8K90XSXfuzX7o6Jlvzqw/bPdH10OKn/vO6t+d3V4+nv+zXkPdH6D5neCu74B6cMeuu94v7Vqeb8m9A11'
        b'xId1t/2StPWenT+/+hW/tLKBKyt/rpv5+bI31iS6Hayf0+/7Q5+vLpv1YXT8wcvhZ75pqPhN7IK3FcFhb73ydsXX8nd8b9uDry/qNRZeiTWWLg9f+CDodvDXfX8R9s8r'
        b'H4bN2n3x8xUfz6o8/M6EHx1+tHJyw7dMPc2Xt3SVT/zB/o8O+7+16M263KM39h+ty/zPstwTP7v9m3eO3rhxbIKbObz5pz/91uEjO4s3uTvgse2/qMSBim/srFKZUs6k'
        b'LvD4IKfux0MfGD5J/k34q3st5yremnxw0h6M2dtekf29b/6sueL9Vf8WWbf9R6657QciDT87XZO+JvjCmf68rqGYX1fHbxr67CeDj9+29Bx79up/tmSs+/xrN9eVdm+e'
        b'83b07R8OH/tK3EDB+2cM33s2fPXGz3/qTnbJj66ue5H1lcaSJizFm6kCVkxTcQNKhnurxoJviwJ75Y6BOMCtA8vxoUHlH3py/Go/3jSLucHAMWjYSgC7lDKD8iCloNwr'
        b'nUNQoczEDt6gFXrlARuCsCg6dgFejlcIKuiTYhNe9zYxDV6ddCyGeVPqgGWTJ0az9ttSwva90Pl3Hp5q3P6+s9aXzqMwMPc/7hs3dsfk5OxcbXpyMjf0HzHzmyOVSiUL'
        b'JTP+IpWyY1UvqaPM0VnKzPDPSkf++3/fv0FlvIeE/XOUeMlYZWL6Kim5J+8JzrQXH8l0PylrcePvHuzdMMPm9MhvSZOTR7gr1/9/rksMM+2+jS3EPJaR/wciH817uV9j'
        b'qjxhIlyhuFJJSRrFXCiGSgfBbUqej8x3MgzoW7+zXWa8RN2qFv8gqHSlM6z2PvvjA4tPTk2847HuzTn/HnwmVbNisHrhjcSa+MafB/UvMS/52sLwj756y2/GT97VXvjO'
        b'4Z+214YmTnjkmTX4nSlvLTq+7b2vNza+Oz1w+E9mr3/y231s4uXDnru/9f4i5ZSYmW7v7a2+r//30++8/8WH3/vBH1x7v/22Z2xWw8Ho75fsz8l68MOKzz9cG/6NVefw'
        b'1Jyvf+7+xqAm4t53Na78UgH2s69UQ58X/89FEmgvrF6mgn4p3sISbODW4jcPalOhj6UEfawXq3t54pAM2qYEmGaxWdqPYq/IC+bZoZzzwgu6sEo2A85CO3cKgVu8Y6Lj'
        b'aDWLf5yDoJRLHfd7m1geMhErNlO+UhqwQSFIYgSszzxg4t+YOaPBQQIBfWNTH6gIiSGvUEHBpFImvA59DlCZjdXcf/jDNRiCG/xOxqhBSmHyOrk/tOvEIHx2nhcOYBl5'
        b'gBB/KMSGg1Y3M9Ush/P4CGtNLOmPTICGqEUMSsVgqYMgD5JAD1aLZQTyNjegnWPgkBhd7HOCpsEVOTWdgic8JYBqrCFsVqqhjqKySAT3RDe4JNsCt6abOGArjEN7j0Di'
        b'3zW2RY7dJIIa7yrYNwvKuTDc4Oorx6YHJASSeEpFaeFTKfufELBrFPrx/cf4pX/gm0b2Msemz9GbrI6NsUNwZVkLgTGZXMKcA7tP4sEzGZbLOMvmsgwnxKC2O4aZw7Js'
        b'Xc6wnB2gDCs4qh+WExYwDcvT9Wn0TjgkZ1hmNBmGFakFJp1xWJ6am5s9LNPnmIYVGeRX6ZdBm5NJo/U5eWbTsCwtyzAsyzWkDysz9NmEUoZlB7R5w7Ij+rxhhdaYptcP'
        b'y7J0h6kLTe+sN+pzjCZtTppuWMlRSBo/CdblmYzDngdy05ctSRYLten6TL1pWGXM0meYknUMHQy7EprI0upzdOnJusNpw07JyUbCWXnJycNKc46ZQMNzhydu1tfAIIFh'
        b'KXtjJwcG9l09A0tzDeyraQZWDTcw+zGwZN7A7k8b2NfCDKziZljM3pjRGtjxuoF9jcqwjL2xb+EaGPcN7MuVBlaDMASyN1a0MbDLTAam9QZmPQZWiDOw6qAhzO4+mTic'
        b'7e7zv9a91H3ynn90tN0zGvZITrZ+tka4P07NGP3fQalzck1q1qZLj9c4shtA6blpxCH6oM3OppigtioSS4TpuTMJw2AyHtKbsoaV2blp2mzjsMtITGZYZWPniDdRG1eI'
        b'/+fUawyQ8QqbXCmXOTKNi/GWsID03/Fo+r8='
    ))))
