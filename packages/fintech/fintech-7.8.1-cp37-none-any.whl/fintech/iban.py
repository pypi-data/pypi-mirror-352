
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
        b'eJzNfAdYnNeV9jcVxAACNSTURs1iaAKEimVZEkYFRBWoNxiGQSChAU0RalZDYuggkBACFVAFIboKKgj7HMdpXv9xHG8SvInjjR3v2s46cZLNxsk6/7n3DjBIcuz8f55n'
        b'F54pfPfec88995z3lPt9/FJy+lHQaxm9LIvpLV3aLO2QNsvSZenyE9JmuVHRoExXNMrMM9OVRlW+tEttCd4iN6rTVfmy4zKji1GeL5NJ6epkaUSmzuWLDLfolyLitbtz'
        b'0m3ZRm1OhtaaadQm7rdm5pi0K7NMVqMhU5urN+zS7zAGu7mtzcyyDPRNN2ZkmYwWbYbNZLBm5ZgsWmuO1pBpNOzS6k3pWoPZqLcatYy6JdjNMMnB+1R6TaaXhvGfTm92'
        b'yS6zy+0Ku9KusqvtLnZX+wi7m11jd7d72D3tI+1edm/7KPto+xj7WPs4u499vH2C3dc+0T4pYzJfs+vLkwulfOnlKQfUhybnS8nSoSn5kkw6PPnwlI0kHb5ORbxhQHhy'
        b'ennQazRjQMkFmCzp3OKzXen7Xw7IJeXMWJUkpcbOy3GXbDPoYoRLMJZgERZCe0LsGizEsgQdlkWvSwxSS7NXKLFvy3hbOPXTQgn2UM9yrAjAogQsj4rD8vXUv2TOmqjA'
        b'GCzF0uhYzXwsjlZJe6FixNY07OWzVix2kdy1AXJJmxp4OWKmZEuhi1AIddCJ3SPSgzzWRBHZ0uh1UdDqh4WBq+PwVLIrFkWtI+LDZ/OLisXy+NiEdX7UUDiH2FwTtXqd'
        b'X1BUdKAMbiolKxSNnY8n8ZZB5qRMngPyWPk1G5Lh6RC5rFBOIpeTyGVc5HIuctlhuUPkGc4iH0GvuKdEXidEvtSiltwlyStk/btbN65YIvGLf0ykfaDPkIwbXrdXe4uL'
        b'ymBXyYuuhaxP3VLp4SUurk9TSvSpDVnfu1U9Ok1qlrLd6HKaywTl70dJy34zer/s3Y2HksZ5vyLLZnw8nH9O1uGSuUixLDXsX8yvhfhI/PK3zZ+PPD2yeZyU+AvZl+ND'
        b'Xv5E6pdsIWwbLtHvLRI/baKfHxbPiQrCYmhe6wctUE0bUREYHB20Ok4mmUaOeFGBJ2xj2aAWrJ8KzSst7iRlrJWgBvO9bGz5cPQ5NXb4WcykYlhCm3zAR4w4IW2ADqi2'
        b'mF2ooUyCYjx9mLccwcfeusMWvEvfsVKCUjyDpzgtvJc4bnagBcpJUtgowYUXJtrGMFq18c/LptF1UnW8LMFFPBPBByzIXA4lWyx72NwVNAUULONTbPZYimUWC3aqqeGM'
        b'BJX4CKt4C96Iwxtj8JLFxsackqDEBXr4JOYl+6Hax+LBhlyS4Bw8wGYxpNekDIDzFuxmbJ1l1HrG85ZQ6MFjeExngVLW77wEdZnLbeMYxz14Cnrg8TKLhvHcwOj1HBFN'
        b'ZQuwG25ihyWPNBVrJCjHznFipmo4lrgBuywjJTGoFjt3cOYU2p0H4DF2ezAWWmkPY/GWGFI/7zDUw2MNl38LDYGCFDHPgw14AuvwOJTQpslcJWgzQC+ndhiOz4FzZgt2'
        b'sd2skqAifZcYcwbbD23CGuy2KYSoT6+BPj5mTfIceOClwQ42TzvtgS9UCw6uQju2YOESS55cUCtelWLzoZaxeA3LoAiLLHiP8X1OglPQESXU4y62HoCudMtIx57WWaCb'
        b'84DVeBsrZy7GblfWdFWCeivYeVPomA14mWbrdmVM3GCKcAzLxaguuJNjIa3utqrEVBVQESqarmFX0jq4g93uajHsAjSk2sYzLs5iEVRBG96nRiaLJkbzitDTMfBwSsAa'
        b'7MZOxvwV0vkZWMAXhscM0IzXsYrAjI1qk6ARajbx2Rab8Ra2L6UWh6Augx2v8KZxs2hl9XCN2ph0OyS4MgvyhRDvz1fhqVSSu0P9TkGfTLDYgp0vwVFopM2XiVGXoQFq'
        b'OMVcuBiOD0ghu7GbNd4kYXmtElt5bkLIQqhgLS5CZy7q8Rpv2oenoXbOSNpLB/MXsA9b+MrgOF7Ae6R3TRpX1nhXgmvQuofzqE9NNcMDDXYxeneIDayFCjFXNbZBc+xa'
        b'zV6VmOocLbSdD5JRp2ujpmjwLhNiJ5P94wBh1MfmBOXiDWphS+4mnZ6dx3kIJ0To3oZV1KISMzXiaXzMB8Vha4gb1lusjLlCCQrgmoIjweqF0ISnN2oYGjOp1yaHDyyo'
        b'BOpGwx2NG5vmvgTXSbYltgmsLX+hF3YaoWQ+VsIdKFVJCrwsS4iYYvNlW9K2cZ8L9EHJXhJXGRSrJGWmDI6p4LiNufyg2VgKd4IczWEDFEZAmdwH7szWKWyjqNdKaJlL'
        b'jrYCS2jHc6QcU5TNm9F+uHS/x6QY4jVNSiP9KOCd4f58vBDuEqNm/iQdT5LlPcc6P4JTEWQVhdAyH5pV+jgow6s7IyVC7Sub46RwiwrOpIfYdIxCRx7mi674GIrnk2af'
        b'IdmxkeF06YxSmoRlyhGJh3hv9xmk7KLzeWiFuyRB6h0FbYOdoVepwJNWQfvY1kTRm6RxfD60OpG+JUhXKdXxhLOsdwYp+jGsjqKmvnBie7BzGJuFOgcpsIeigWOCdrkE'
        b'XdCaO7DKNr5KeLRTo6Xta1o/WlqtddHgTaMtmHoHkLrWYR2cHuw+SJ3AoYx93GRzBJlVe3aF24JoyCgoWsS5YayUKdI2ww0xAVwhUld3QglJMgp71KRu02wzmdQrgoMG'
        b'RzjEokyS6I++iditwA7ozbItpI5bZ5C5CLkwCfLph2SjwMZwaIpjZG7FqdPipD3Q7gr3yWPypUBTBhazadoGZaSAKtKYM1CQMWs16VSdFIqXVFAO9/CebTYNicdjcF1M'
        b'OHKDYyqxZzfFnlUr8NEaOe8LDT6jRFfXI8OVoVnsmF1JKq6xzWELboTz84YkytbhSsJvfUInwg+qyLwbn7eFsqAE2+IGNVNQx2ZX9lcLJxAuNjsMK1TQQOB8lXMVYYh3'
        b'qF3+ugGtc7AldANbla4+L4hopTfDHW7NfWISLutbQtZc94LIPi2kw8VCquWrX4YbBH6OUTfZKMLU/UysUKCFy6RRcdjrEkaSPmULoCHJKmLPycZswVw9MH+z33zBlQUu'
        b'uWKpFaq4tKi1BE9pnxsY0/KUCjr4qlFZsMhsC2Rjbr2MDwYGtDIV7ya/wY05Uku+n+l5Al50CZ6OtWKS6nhyW00zhzR32FRCdkopGB6qdkK+2ubHgPAFvCns7soax8qH'
        b'2f9sBT7EE3COd16eyIyIOu/EHic9D2e7rpQm4l0FdlIQZxfcXE2aMlw/wE78Nz+pIHtUUBsB17hhU2BejEe5glNs0e00xwAOKBTYvhBv2vxZ72KC+i4xR0wek+RTmnGF'
        b'FPYmnLfNY93PhEHXIEfEc7ngaghslNDlHhexHFqfk8x4xhUrFyVy407GoxMdJhTvhDaRWhV5nwYVBcjlm8Sa6zN9h0v/xNJhdsRtbi7WqyiMKNkpVPYE9TzGyCcsE+yU'
        b'DSqhwATiymPnPNkalcvCUaSyDKDgJN6AxhiOE9SRddsYK5SEKwiH+iQoc5mmhXt878IsUOcMaQMdS7BmL/WdC3cINfBxPDe5CRvwrNCKUrw0bBduip3upG1IEn0pjL5J'
        b'duyMrQ7woytHJ8FxpkGnQjkT2BKT5AC/U9pn7C7YFfhgPTRyqWeOpDjxCUiVE9VLWDIR75Gq6fC84OCCJOcdTR7DtLJN8NpBvOJZeMT7jnODbq5feDrUIWSOpreH9Os2'
        b'3p9uC6O+O/AK9RvuNPDaWL6RbU6OIxTrVHCR4vcijg3h8dJwacSv4Ow0OQ/ZoIJKt3Su9NY9bs5WzhJooV6DVp4Y6/L8AqjnYBU6JvIJ+94yBLoDy5gLfSqKaB9YhIbd'
        b'3m8bGLOcnAEbJjc4dNiL5uiZ7w2F82RQv8wtHsr3c0HhjVRydmyUr8HZRgZMS6egwO9YFNdGSmiwKnvrU6g7gOsOcLOpcrVwTChC90IKbBn1IDw9/ylQmIj3Fdg1hWCH'
        b'CXQW2skFcuJL4N4TLsARpvQpPaEXLgriDbSHXZz6djw/TM1uCeptCmxbb+Lh0suTlzoDeeruJ2Uf6LJgTRzHm7nbCWKEJyqAY8/SHqa/fVhp4OpDIcrVISy+jk8IHro3'
        b'Yxme2IlXNkvmXeTkE/bzDY7AenxS68RKVaMoALvncPK3yEWSMxawc0eBTeGECQNqNAzynSIcqFZZFwYL//1YueGJWY74Ony9s2o3MngriOT7rMXHcUNOkvWaQImqM49t'
        b'qj3zZImuLvNHTeK67foC3h/GFRfXLVUa+bITDHfCfFSkPDfXcwFDBxaMc+BDu8bhuhwCFjEjdCmVlEm0i+7Hc0cM7seZ4cJqFWpRrHSljKRKwERPUCDfjgVHhiu0UKEX'
        b'FNhLXF3ie4dX8KEAZWeFvkIep+VJS8ZqFZxPm6eL5blNjA8luJfwzlDKgQ2UP/Acthk6Ny/MsPCMs0gib1hM0QRriQ+hqLJqswVvy0SNo3wM3heJ3kM/uLw8z6mOcoHy'
        b'aJ6ptC0lXC3CfDI+lvhelOA8Nk0Uo65sWYQtFouZZTd25mFOUP7P8p5VUCPDirVD5RfFfJH0Hp1OunUXupzqL+URIlujyGhSKtyh9J91pNC7ZCqWiJzsUeLzJPWLFje5'
        b'YO/MRgVnwP3ADrwOdgsUK0V+ej4Ia/iQ3cFQaclyquaEUANbzyKS/VGKWussnoxYHa0VrsAZsdaz1HDWE0qdaj2LoJazF0tx2/nJ0OJU7plPDoTn3c1wCi9PxfNOFZ86'
        b'bBMLPk4hQN8WD6eijyd0chbxljvc3ptGLS6iNHA6JkeI9TKlzhUzRg8Vg5IoD2YtJjgdjJ34aKgcZHOUiZ7f4xMGx52KQXDDJtbUgkVQNw3qLSLjvsA2tzdbcPB4yct4'
        b'1XWoGLSF4iPWsO2QCXrnDVVOsIa8AtetK3BLBwVuljyVWE3ZVqznWSt16SHHXoQ1zmWVvoFCXTEp6GP5GmqTiZLU6VUruKbkLJ4BhdgwVHBRz+AjEknt88kOzltGykS9'
        b'5fxBhVCUllgssZLNDFVidjqKNHnQpsdOg1MlhmypRgi1HE9sg95Ap0rMvmlcQl5ReBcf4XHsFnZBgqhZga1irltJRry/BLvd2ZKu0VRwHkoFwVroylZjh1P9xs/LUeOA'
        b'U9sowHzkVL2ZkyjKJpexZzdZSSNNxgsWRLIOCmO5KEaZtMtWYbeni6gVXIHybWILy6F3VBqJtlvoXpdEzvWiL+fCO90bGpZh9x65EGsF8XeKc+HLM4fmBGpTi32vxLp0'
        b'TvBFqDaTht5yLiLhsWSxU02H4bgL3HCqIW0M57xjLTFeP4okOlREQjsWco1JwF6z2uxUQoKCBZyNDG88ReF2hVMNaQH2cTZ2kbWdxDLaEptD7lV0JV/YVIPvZPLcFJxz'
        b'I2hkxZxH+Fgw0ow3sGYOKUg33nHI/pwHCPsmELVjn1GO3R5ywX8D1uBFUci9Ejc7Se5UsVI5VlZCGFw8hgnEQyXqQVfATlEfV+zrWAVHXSkjcapmwX2yOzZdHiH4HfIC'
        b'rc4VrQV+XJRueXh6CtRrsEMtGs6nYYcQ8n1shY6VJqdaV4KFF1tmeJk8czSualFhujqV7Icj4JUZYw5CuVP1q9SFU1oPt+PXwiON1aGf1ZSmC0hXYvcKKIS7TpWxg4c5'
        b'MTefVXgSuodKTwvgMZfPGhcKadp8NXsZsWYGs1peF0qavtk9WbOXdW8hkNTv4WSS8T4U7lo/VF2DS2v5zHMpsSYAOu1UXZs6VWxOBcHA0eWbnaprUIQXhNXcSYfmGdjm'
        b'VF/bTh6VF/ObRyrGB2o82eIfkYZ6wX2BX3cCdumwVePJlO6xBDcXOiqyBkpoG+FcpAY7HQKj8OICZy5pZBgljz3Uwgb1kGTXYQVvSaZN7CDLbNeMkIuJbmTH8fk94Pyh'
        b'KVs1NkeV+ywej+TXYynq02UMFfdmQSWXl+qFOdmHNRaH2C9OG+NwBbHwGE6mUyrEFaKX9jfDRaSMTVAuo+vVUOgo60GrI+6DQopo4Bwr5Cmhey2UrJM2bFPjJfeFOuVA'
        b'JfYh6WhJbED6aixVSAp8TBH2NlHVT4ZevB+DxbFqyYZ18u2yOZSatvBCYu6GvTFQSp6rfA6WBejYoZW7l2JsMAp/hy20zu6AeCyYEBSllJTLZHDTJ2WlgZ0WsR9aAT9v'
        b'4mdN7HzULvFjLHakxY6yFPYRGSMch1jKQmW+9LLqgPqQkh9iqfghlvKwaqOUruDnhsr3f0Myd9M6/USyE06LVm/iR5vajByzdq8+Oys9y7o/eFjHYX9Ei4NV/105JmsO'
        b'PyT1HzhW1WYRtb36rGx9WrYxkBNcZTTvdkxgYeOGkUrTm3ZpDTnpRn7Myqhyehbb7oHjW73BkGMzWbUm2+40o1mrNzu6GNO1esswWnnG7Oxgt2GXFuXqzfrd2iyaZpF2'
        b'baY4wWVHu2mDVIKfNSAty7CILXNH1l6jKVCMYgy+FB05jIMs01MrYj8GEoxxn5Utwag3ZGpzqJP5mRPxtZn3O09mHWCTRPnN57Gyw2wHtWBtnM1iZWtkck9OCJobOn++'
        b'NiI2MSpCG/YMIunGZ/JmMebqOWP+7Ju/1kiqYdNbjfxsPDV1rdlmTE0dxu/TtB38C4lz1XKsRZucZdqRbdSusJlztIn6/buNJqtFG2E26p/gxWy02swmy6LBGbU5pkEl'
        b'DaSrK/XZFn6ZCTkvy/LEYoadlbtKTx7cesev5D5h23jKsPeYtgwEl/GJ/ET253kTpFLvVElKTV3ct8Ak8b6RUH0YSujLpjBolDZNh7O878ehbpI0jdI+r9Tsd1c8L450'
        b'u4I9pYUryHZDUmPHeS2VhGs6Z5lu0UzGEwMxIaHlUd1Igbc1esoDNFvg+kBjUipvCIAray15cD5q4OgQHk/ggD+O0psay0jCt5uSGFJLyVclR5gUrNpEDpcd1wweH0KT'
        b'cNRlpuUacwL2DZweBorQj2Xc0ZpcaIJihQiszm6C2w5qXVmaPXAcbjkikHpKKM6JSO22FyVLJe7YsNhx4piEd3nLHLiSg90Win4eqEWUUTV5u/BUDw6ys9UuKPceOIyE'
        b'h+SO2FQjKKQooMAkHCsHjiOxdxMXxCIvKCKnDmUHB84jjSMFDwUroUSTtxrbFcIhXZzu4GHlHizEbvPS7WxEPYvSSrFZrLYcr4+y5GFbkosI6ivIuXeIppvQAZep7bj/'
        b'QIwO9ZMdpzshihjajAebBlp8Zogxp1Jn0URwFx8OTlXhy+U9MtOFIvoNA9NQEuqIwi4r0E6JA54TrpwlFm54UScXQUmXPo8a0/YONOnwJl/SeJ/FrFTTRxskotK6iVjE'
        b'Ve5f1S7SMq9JlOKnZr/itVzidLJIYE1zQyYy/wrVUhqcgDtZYUlzZRYWqE30bnmxMmJ1ZIR7QfV33zi4+87IvGva4G37XH2CFx/NaQzwmaX9r4Yf7Q9oVDW6/nvbqn2K'
        b'KWjYJ69IXHw0+rWw+u/+cfZfp07vnBp6V7vnqPyhX+V7yr+MrPr8pefNfrU+7T5VBdrOho9fe63zRPnnrXHv4ff9d/7V8ulzf/J+9eJvXTbOv/zfL737g/bF9gOps//w'
        b'0WvvHKzF8hOfV1R+dGrHO3V/mPbalbY335vf+WjvkvVfNh8yf3D2zYTTR3RLX/z89Z7EV3++q/l3EVFvfPaLL+7/6OAbO0ZN2LdzS23GB595/vVHe6t/8b0zARGZnpFd'
        b'muxUj4Of5pyf/euet99de70nMi03pW7TvA/T33Gf7/eO773vxPlsTs3U/+X3mjUxxne8XtC5WEUcNQdOBqz0CvKLCpJLaqiTB5FOtlmnsLbCjNEBwXAUq6MD/XXBWBGI'
        b'RbQlWuV2CoquWpnrh9vQJsUkBEFRAhbb1BQcaNbIsRyKQqzi+HldFIXEt7yxyD8oWEb0j8vnQq3Oyqobh/HxfFIIcTdMnrgbZm+QPxbPkUvB0OubqsLb4XjUyg/GsWQl'
        b'lhwcERcYTfm8pA6Xe0LxIesMkRffMcQQmXw4zkhQ6lgRy+OXsXiCncHd26mT98v9dKyCIOlG8I9v/Mbw9IuxizPMOQeMJm2GuL0qmLnaJf1uHPhT2B+sm2U9A+Ajkk4p'
        b'U8pc+ctTJpeNo08vernJ2HV3ft1N5ipXs3fZ0DtrU8vG80/2lyf9pWQt8kkyVuKQ4jkzOnW/ks3YryD33e/icIb9Sua9+l1SUsw2U0pKvyYlxZBt1JtsuSkpOvXfXqNO'
        b'aWbhl5ndhGNmpmVmd3qZWVjG561ha/NiazsqfTqJ+JbL1PzdNp2nUC9jS4zYPS56P7Q7SR87cwhLJjJduDcRStflxFAjlsRjeUK0SvLMVSwMgEs8itzpnREDZaGx8SKM'
        b'lEmazXJso6TIAeRd45eL8NN9CYs+sd3DoHA4PbYKlwGnFyYN3hClzFA64kZFoYLiRiXFjQoeNyp53Kg4rHTEjRkUN/5E9mTcyO+HcwoczTm7tfqBUG94UDc8gHsiQFv7'
        b'N+JIs3GPLcssoodco5liyd0izBm4SW+4o08Y8P/EiH8SzZi127jCbM4x+3NiempJf3Z4yPhl7IoQ8clFPDM2cixKjHhyhc+aggWUK7P1O7RZIqw15JjNRktujimd4iAe'
        b'V1oyc2zZ6SxOEiEPD3AdQe2zI6IVWWzJQwEYBdt6bViQ1ZZLgZUjzOJSo/jQj/UIZBPp/kZ8pHoqPlLF215kDXvg8bC7AaEHKxx3BBbF+q8OhJtrxc2B7EJCbHScjJIm'
        b'8tPPY51mbZbsxT/ILIyOHf75k9TgX+n0UfrsjOy0T1O3v/KTV3/yaiXcrny+oLmmsaYzvzmqxb+poLEgtExX21gwrfZYt0oKnKV5ddUCndw6jWhshvurNP5kCFiEpXE2'
        b'By5OhW7lpJ3Yjm0HOERv2b86JhhuTFpNwAhlA8DnC7eVpqlwUycfZuVfhW/c1Ps14vbPITjzFHCWzgBrFIct88ghGFL1uw5oVL+LQzcEjrizN3a/5rDpFWaWz5oZjohu'
        b'HF8YwR874UvLKGd80dK11YQhDTHBwxfoD318jRKl4i9IrGbUs+KppLcZz5D/76LMtCFQsS0mHMr3xJGTaIXr0OsmpWGVB16YJ4Kt5blJmr2eMikCzsoo6sQWbDDxAEi2'
        b'LVCzd49M2h8iw0IKQIwrRIXh6HPrLHgX7uaNDFNKcqySjdsBvRynnl861RJGIoKiWbIcAj3oc3GEet3pmr171RSe4iUZnpSwDo5u1InqczQ82iTALQ+vc3S7D2c4Ks7B'
        b'e+aYVXDtidz6sCOsgnYsGU+pdbmMHdhflFPyHzkPLgxDxsF0YBFTTQXHRnGbqNzumuE6iJDKr0XI//6qzJqb9vC8+ivxgWEJ6/71+elXpI1s8P941mjI5mxZjNan88Qn'
        b'GGRyyTEYbASFJsPTjA5kiisSI7SR5LPNDCqXk0swWHPMlPvl2tKysyyZRChtP+/pgO5IyiXN+uyn6L1EVhnsxJuebYqN3yjunxy51j+QPpYvZx+RCUmh9Ens+b8U9hJv'
        b'iIz0D3yKotOaKAvNeWa+yxbJ5Zwrslyims5Qe3/uEwJkP9/IHw5SzMl92g2yn2/mCodt3j8szZZJz0qzR1KazYxsX9JaZzeiwtqob+RF1i/jqc2XsROkEHbX9OGt1syw'
        b'NJFiJ+4bLbF7DEJMEVY3mZ/EwUYPNyi8rnQVebq0CXoCBCy07kzIg2tQAoVQSE5vtGwEXsUWTmj3dE+J0qbxIRnjtrlEuhJK80rjeBPaKRcsmMuibSl0WbSNQXKYN7sL'
        b'KWkuLTFMCktMFuWCdd4SQfPCkHGLVl/1XMYo8Lv77C5QNtrLQYDy5E5+eQ48wnNbY3lNO1FKhJptnEj2bjeJoNc1ZGXA6CMbtkprs/7wlkJl6aSmlFc/nlUe6gkh7it+'
        b'PTOu/3jtxgd7xrX9QPa6+8+n26IeaF99KSLs4MjKTyePcJ901T4968MPXz5y5JO5BXUdLq+7jljynf4t698Pn1404tK+FzqKj4e+rwgOmTS29Id3vixNvD6z/ZWqefXR'
        b'+w7amzZ+2z8CUn/c52WLtuvXjf3liZkXfjN3RrNnU/9C3x/+aefPH1R+N/7X1v/KMIXdi//zex+P6PvgZ+VvbLFuOvPP8V9c23f7s8b9/y37YNG8992zda4il6rB6+tm'
        b'YkOAUzKFjTutLEyGM1i9wdmfw8npQy4d21fO4TkR3IJWn70LGKJTSsXyqjnUKYiNiXEhoTaoo/EsnrMyzwhNi7BYE4Olujh8CGUDIcJYsCtd4TQ0WJn0DXAH8yekU4om'
        b'k+R7ZRELU3liNg0qFkL3LPaQxJwExuthuT9chAK+jqlr12IXu3/eKduSMN/KovjJUOIbg2UxPB2c7MYSwpEhih1Yi3U6mfD0rn9XciWCjxEilSIHwUOPEBF6HJGkgVyK'
        b'vcspJ/LkuZKnTClnOdJ0eo13vMyjnYKToYymX0FY7RSTfF0ypHBKhsYMximM9n84xSmnfZ3jFJaGQj3UwQ2Wh3ZBs0iGErhH90a7gmIQO3TqZPwYKIkikwYsiYVKrVOZ'
        b'Ha8lD3vAYzCfYXdYkM+WZ8gHH+SQfeWDHA5P/cWbw2ArScDeV4TkGTyi5g7WuYz9P53DPBN3B6QzHHfV8bYl9D0GL1AQ+IyneZ6FunASuoaQdxG2i0JU8SJ3x9n77n2s'
        b'FHYeTvIbSdjJbi9ZERbHYWkyFsbKR62AZiJyDc7RF52U6AVNWO0Cd+FESlawb67CwgLTD0Pmf5Ia6JQJbHylp7KxWhY191pIUHrg+gB9vF4dUPb9kODUf0/d+J3xb7zy'
        b'U7mUHOkxI6Zcp+JWPndC8LA0IGW3E2pkYB0vj4z3w0uEOt7QNgQ8l725wW7Ds9MCgocXcOC8t3L7ARcre6pLHwqPBIg4AYivhiCkA9p5jWcynMK6gRpPrHrjElHjwZqF'
        b'wtjkz7Rolx1G66A9ew3Y8zRmx7z+ITOPG7JXhag7PDtzkIlGbod8sWQmllHCDo9KH3s6WyIvNFRj0cqYpLmDHDtqUjfx7t+wMLld+sYWlkkWdnOYgibnZmdZLYNmJE4K'
        b'yFa07GqGWb+DV/6fMKkBs9Rrw5+Zzg7r7BeZsC5+bdKmQG1k1IrImOR1cZTnRsTHpEQmLF8RqI2I5O0p8eviXlqRpPvq5PdZ1sMd8p35jqe6Mt5c9HBkgmR7nsmyDh9N'
        b'Z0+yBbCH4Ypi10QNJiJYBpeVWKWDZjc4t59e0VC0nxIytRsUepl5bWgrPn7eeTCZzeodAQzzpmCTEi57Hsn6zPCSwrKG+haE136SuvWVDrKOzvzQL6ecnHay80x0VWNN'
        b'Y0Fj/rT63qhrJ0JPNp/rLOpU+E3/bsfR5vw90wxBBg9D5+TEggkzk7Hn6P5pkeSK1FLJdO+OcfN0Squ472J/ZkAEtjoXOB+querjLU3EU6qvBDu2u47eyz3htn2UrZWs'
        b'hWonT4gXX7YyGM8x4KMY7p391NKI8XK4Cu3Q6AP2Ycr7bONwoyzC4pRqjxmwj1BXmTu3EE+RcI//f7ARNsZvmI30D7MR9nDHWl88GhAV6B/Pc+rp+Jh7onHwUDkWmqBa'
        b'56jt9ULfIvJU1EjAWjEHioU94dlFvkeUmVC/8tkG5SjB8ScSB0twX2dUOyjB3PZkCc7Zc/FalUm/m6cyz3BYLJFhB225RrpAjm24C4kWppWtt1opLzHoyfsMJ8r9mD5d'
        b'VPmeysiG0RrMzr4uORPJ2P9GRyp7JhS4Ckfqj7eXDvOjFA5+szoYucQOjia+ieN5DiPJ9FtDg/PE8UwQHsfCVdqhm9sOYy1/cABPwY2JeuXf9q8u/JGIbk7+DZULByvt'
        b'PIt79oR5UtYPfl4mt2yilk8KPYd73I9TMzNi9d/LCEz6mPDlJ692VIbWNubrZW+/VBDv9U/n4VFl50+un5h1UnXr4oRbF9cR4siaLt5R31pyclrtsbkK6dtxv39vnEvO'
        b'Ep1aHDdclWHfoEc+kDysNIftUAFXrPyhplbvxU5hfPTqBF74xnICnDiVtCBefRg65nGIGjUyaiBlGIXVHKGO4jEOUfunEAAVYNOTHly5HduieQXQEx7B/dHQ+TSQueKd'
        b'HMcJyTy4Jxz4arzyojMbU6FKiRf2ugzE7l9XJHTnXp2UmpkMh65xA9C1ggGWu8xNLty7u8zs6wRe/RoGdik5ZhYTOIHYMyckbiYOwhmjsmgYnH1nWJFwFlthIVYdHlih'
        b'0/KwzFusEPoI1BTx8St1spU6efzKrPEvn1FaviCy9eox6079OHn0mjH2z3ofNt8+Ov6V4P8s7r0sf728+LJ6zJg/zG3Qui33ePCCf9F/BPt+a8kvf1P56M+rDpz9NGTR'
        b'jv9440/v/C53B74daboz8XsxHzSFvvPRZ03jGjs7j34SMP7tj/7lwO23P+pOe8vHNGZ5nfItz0tvP15jMPsFFH34YWlsyW8zdH/ZM7GreN/2L7L7xlf8UeWxvdD/ZnNj'
        b'zaJRP3r7lVG+m1ZXPVeXpZ/w/U2vrl7fWTfv1rUztls7FBN/+lrG3Y4zu7N3uLyQZfB5+FPc/p+dlxSTPvCy299dXD1j0rULht8VBC18c8Sif7taUn114bey3sytsZz/'
        b'SP6zrR9UrQ9+G8f2brt2dtfWH7/r8cPfv9X+2zhT6Cvae/fRK+/+je4LBx62/+w3R92x9DeVq0rDXje8vv/ye7XrL4a9OjP5i+81/OrBdz4v/eiR9tvhc/bPe+/XzVsr'
        b'Wlav3HT1tdSdy376w/X318coY5PmFuzefDN9c4Gx5kzrrz547dLtV7rWJv3ke60BJwPX1bR1pT/8Qf9nG165nbvrZ031G2vH733rA/voPVevnPe/8XroXP323133+t1f'
        b'v+UZdMDwKMj3Lz9682ZpWsGhX7j+2cfv9LXZX/728S9f9Ay+aKp/535K+Q++2/M48dczw/94rOLMo9kBuuIVE6xH/tUy7cEPJv8pIXlz/S9jVvyudNmfN3/337fPMHxe'
        b'9lnE/OJ/G9t5qm/53HdCPkUyaH4PGzQYST2qyM/JJNlCCctDXLhlsaf/oXLQrvyhfci0Yrx5cL7EsuLpGn1EpIACbJwgDkEfwn20bzmEJRRElAWpJfV2+QyoOMTD8y1w'
        b'NSAAm7xWB2FhdGy8StJAp5z09QTc5QBACNizPWY2XGdoTH2wNJr1aZfjzTDN33mYqfP8+84+v5KOysxcxzPfOEq4pqRk5+jTU1I4Qvwrs9sZcrlcFi7T8kPOUXJX5TiZ'
        b'+HVTycmKXfn7/75fV/koGft1lY1RsPLDpKVyWsGY0W60mvGySX5yme9IennLZeZJA0hJYCdPSXHCOI//f4nLzJMHAZFNxGBdHNC895wzGPKwtlzjCyVQgRVYFBlFmW4R'
        b'VLhInhMUk+GCKgue61NazlG326O3B5W86AbLxpz4aPf8vpVjApVvvT56n4/GoPvw3cXZp8fUrYx68Ep6zqne5ofT337j0NQrl/elLavYtOiXxsrtv1oe928rG97avGPM'
        b'vd8n/3X9rz44/p+Zb31Y8fE7rmljgr90i3vk2paZ4PHcuZiph0/lZX1wbO3Ov+5+/7cXj7f84SPX526/0XM595887oX/y57/gy83n/uV4f2Q90vNf5FP/lT35+9f1HkI'
        b'8zuxZTSrTyUk0EJKY1ywG0tI87vk2AR9OmEcLVijZUFDJ+92fQ0rZXnjIwU0rploZXKatDxHiCImIIpMFMq4KEYppizA49z6dxPZ8zFJB6Pj/ONcJLVS7jory8qOZKKw'
        b'OCFgNXRht0qSxbB7tOuxz8oKU2vwWN6TVQaiUgXlc2IIAsoJNyoU0irodKFgoBNvc6TASyFaNog9S+s0Ti35LFf6Q9My7qjhJBZToN2N7I6XZrL2Of57HKDia1NCQQC2'
        b'CkTpU0MxS6zyoDEGS1wkZZAMWg9F84NDDd7DOzEJAXiKVQ+dOJoI9Uq4vkzFRedBwFKGJTrqEwH5TFUSCP5GrlGss2Idr1hi0ah9osNSCtYC2ep4FieTtHhHJflgD9+m'
        b'EMzHuoCEQOQM0Tbdx3bi4bGc2OgcnqRM/sfAzz/wjZKqr8CvLFOW1YFfLJqTPFhUQ6mZQiljCMDSMy8e6bBYx00xk0VAc8xTBjFgar8i22jqV7IDkH4Vz+77lZQqWPuV'
        b'6VkGeqc0xdSvsFjN/aq0/VajpV+ZlpOT3a/IMln7VRkEn/Rh1pt20OgsU67N2q8wZJr7FTnm9H51RlY2JTH9it363H7FgazcfpXeYsjK6ldkGvdRFyLvlmXJMlmsepPB'
        b'2K/mSYqBn9Iac62Wfu/dOenPL0gRJdf0rB1Z1n6NJTMrw5piZMlDvwclG5n6LJMxPcW4z9A/IiXFQmlYbkpKv9pmslFOMYRtYrGTzezUwzyfvbGnps2slG1mcjOz6N7M'
        b'dNvMqixm9oSVmaWHZvaYnJk9+2Zm/4jHzJJSM1M7M3vUy7yAvbGTBDM78zCzCpyZ3d5sZk9RmdlT6WYW95mZwpuZfZlZtcLMSm7mkEGkZNvhNoiU/7XcCSl52xeuAzf0'
        b'9HulpDi+O1zXF74Zw/+XktaUY9WyNmN6vM6V3WqTnmMgmdAXfXY2Af4Uh+qw0Jiuu5H4zVZLXpY1s1+dnWPQZ1v63Z2TNPOLAwJ0ehP6t1j8w6YlTEd58UwpVypcmY7F'
        b'jGFeSfZ/ATiX+jw='
    ))))
