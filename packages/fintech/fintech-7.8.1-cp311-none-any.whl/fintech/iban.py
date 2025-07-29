
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
        b'eJzVfAlc1Ne1/2/2GYZ9XwQGlGVYBQRxF1EE2cRdo2EdBEXAWVRccWXYEVBxQXBHQNnc99zbtEnT5g2WRkqT1jTJ62vaf0NebJ7NS9v/uffOEBbTNu+T997njeOPOb97'
        b'77nn3nvuOd9z7m/mI27US2D8+8URuJzgcrh13EZuHS+Hd4hbx1cJWoXcK145/Ms8juvgmWi1eY6Az6lEl+Fzx0itbZzG/DU+3BfnCMfWP8CDuxLVOC48Lke0nJNtVIq/'
        b'yjVLWBCTothSlKMrUCmKchXaPJViaYk2r6hQEZdfqFVl5ymKM7M3Z25UhZiZrcjL15jq5qhy8wtVGkWurjBbm19UqFFoixTZearszYrMwhxFtlqVqVUpCHdNiFn2pFGD'
        b'cof/cjITH8OljCvjlfHLBGXCMlGZuExSJi2TlZmVycvMyyzKLMusyqzLbMpsy+zK7MscyhzLnMqcy1zKXMvcyiad4PRueie9rV6ql+gt9EK9ld5Mb6c318v0DnpOL9Bb'
        b'65319nqR3lLvqJfrXfRiPV/P07vqJ+ltct1h3qV73PlcudvYudzjIeP43G73sXfhjsfYOzxur/tej+Xc5G8t287tEKzltvNkeUp+SvboVbWA/3ZkAsRGVVjOKWUpBVKg'
        b'5lsJOCEX7SngMszfXLua002Gm56oE7fjSlyempSG9bg6VYmrE1ZpVy4NFnN+i4T4cXoubYz5Ys6cM0RbKDKSbtolc7oNcBN1yZbjPplFWjxwqEpYGY+u+WN90JJkfHS5'
        b'FJfHr8R61D0D1+DaQOgA18Qn45pV/vFJuCYlKXWlPxToQ6G7tPglK/2D4xOCeKhdyGlRuUMUvlqoiyI99OBTaD9wH8sD318MwlaGpsUHJeIq6DoJVySIuG2oVrYeN+Vk'
        b'80bNiKVpRurgcsyiDGaFLqEQlk8MyyuFRTWDRTSHhbbUW+Va0uUD5S4Xjls+Pl0+3oTl409YIt5evnH5Xlk2snyHxi+f/BXL186WL3O6hHv+uhvHKTLMXaUKjt6U7eZz'
        b'TzLJp4wC7R53djN0mZRbunkK3IOaa6aymyKtkHtgZwNqkJG0RRzIXeUKzOD2ryXOeYPSf/PhuA/9/p1/K6xingWvQAYFh0JP8rpTf2sB9cPfD/9Su5Kjt7uSvrBqfO3y'
        b'JP7S57y/rnlnSRI3xOkCyUodd/SBdYI18fcM88cVofHBuAJdXeEP2lAbFJIQvCSZxxVayeZskSpDdQ7QIiQAN2jMUR06BcuFm4ADvieiJfhMDDqnUaMKHxEQlRzS43MC'
        b'nTMpuY8uoAaNGnejOgmQ1RyqQMdRrc4JCqfjLlylwbdQM+omdes4VCVGvTpHQpx1KtKgGtw4F4whPsehZnwW3aNF6B7qDYGyRHSaD2XnOXQW9yl19lAkhSE0aLbOW0vk'
        b'qIW+hKiPtanBbfiIBvfEwz7h8DEO1WXgMioFOgJDOqnRoVpcQ5od5VBlHGrX2ZKy7rz5GovIpaRNC4dO2iWxJgfRA3xWg/tw514i3glgh3qm0TJf3I0Pa1AVbKXrdGo4'
        b'dGoP7tQRLUHX80M0cl8dEbsV2GngPh1sJb6wR7Md61eBZ8DHibRNIB0ZEXqEq1w0VpOCONamKQQfpf3AeM4m4j4L6IWIcI1DLfg8ukLFtpw8Q67mzSej6YAm+NoCymsL'
        b'uoIaUaU56rDgcTwpiGPvRtdvLT7rrsG9HqiLrGw9h2qt8WXaBDfLVmGYwp0CNtONK/Fx2oVZgVSOu6cHkz66YAWU7kwTajjcq9mulfMZowrcgA8yTTiD79tr8G1UhiuI'
        b'wCc5dBTfRbdpMxXM5ymN1VxH44Kewp24h5ZsTlLjPukm3E5KLnLoNG6GQdIlLUOVkVBm60FkuAIyoEOogc7NZNToifu0+By+IWJd1aIGdJA160KVC3GfuS/uFLN2zYXo'
        b'LBURHcN1+ACUOeEWMhFtRLP24146EzszZLDePQH4MZH+Ami/uYJK6F6EH4NRxddRM2l0nUPn1OFsiU6nJkAJWOzLxmk6D7b7FmUXsXIXaVSD7pKZ7ebQhTnRbMF7FpIZ'
        b'90MtRqU7qthG+1kzGZ+C9cbX8CUea3JebMmGdH9zPMjWh+ttSUk7zNIafJc2Wo+bM0mRS5aEKclZMMlUF+1WrIYFDNlhlLk5HfXQ/tXofr5cChpIR3OLQ5ecF1FW6Fi2'
        b'XI570aUCwuomGcz1RFqyDB/FZ+TbCvAJEevkJDoeRku24tMqOWzwB7vJpPVAN/PQddrNLEsfKChGN8go+0B5HfBDOhgFMGuCIiluErF+zuHjebSNBl1HxzVaq2QimZ5s'
        b'3LtSOhZ81NlPrsmKELJZbsJH9rKJqUXdG+Vm+IQr6eUuhy4TE6dzJU2u6vBxVBmF69BNVCXiBPg8r8Q+FZ1boyP4BPbvWSdUuQ03ompUIeKEeTx0ygPtR2fwIZ0CKmzE'
        b'1bjTWCHcxESGqnPM+U6oFJcqBTorqBawYTquhBUuipjDFbk4062zFR8NTwRRs9bhXi4L3QHFtCESHX4N3U8EQXMW7ORyNLAB6dzCNNdqtDtwm2nQZuiEzp/UP4jvoduw'
        b'v/SoIwpdFWUmo2p8EVU4bIpFF9Ylc9M0InTMAZcyVexC9+QaLT6Jz5BZLYfdg9tg8wVQI8dbZ2JzHR/DjfTjNNSBjwm5SbhaiEpRsww2Vymb1NPZqRp8A5W685jNrsHn'
        b'8T3qU/DlPbiHsUK3UBvhFY+uj7BCD4XoIaoX4OP4GLN71XvRVY15BL494lH68G2dkhSd3I5HBndtlFSdTKp6YYGjGEx2PTPIjegcOgVWF12KJIbiLIfOJOKLdJ5m+qPH'
        b'uCEedcIkjfAJJ9IBn2DBMpjHO7B5O+l0l6DHqEKjFi0kqlTGoUP4AcjqCyXFi2aNTBKda/QAtby2Sa7AlahtlR23RCGRC1LYsK6jy0ivUQM0M/nDFbhSFwxFrugKvj9x'
        b'svPRfdSFq8nNdiJXsFq0VTaZ6nbMOk+NWogumrynB2wg4gz8p1mOjKpakEUF2oQugI24uAlVrpuDa5O5eHxHjG+WbGPrdhE9DAcrH72K2WlUictAlSZTm4PvS0bPEaxa'
        b'8ooo4TLODfcJcLcvzAGZnQ18fFtjhq/iFj5br2PopjfDfWfnz/tm4XeasbGMXre2ZMK9M1mclcxtRV1SdDcumTmGTnzfTgOw4DBuFDKTdwYdQDfpfOFydC6SSHZ9ZPUE'
        b'qB6X42OLl6IjubDtTnFhuEUESliuZpquR2XrAVTgB9YmTAEb9SJdQ3R5afAYnWLa2c60s0HgH4Qf7OAZ3QS4qm6NJa4JImM9Bbq5HnVRLrvzEl61Xa4yxSwT4rYUiZcv'
        b'4/IYN+NqwCo5W0ZgzGU7XQgx5/gCOoAb0KU0E6vqcWLRTTNtlwid1M6g3FbhR9MJJjqGTpqAz1p8QzeVjPPuzNm4AdwAMwYjYgGTajb9hFk4rhWhVnwJX2POusEe7OlW'
        b'CbpjgkvZ4OyISZgJ26xr7EY2LSMb5TWhrUxKV4luv7O4BT8EdGWDe03wyg6d1oVCWSpqXDpipEyM0C1c7gZ90CHTHR0MVhbGtoEaeltz3A3c3NZJmPdudEWVVGLAqfiA'
        b'Rodbg01ILRbdpYoSiA7iXlM/7aQf8JwlJFCC6TqCjijQedikyfihJNx2DXO0h/HNtRqLZYtN4C4bP6CsALTc3QwrUx4y2rTC7sIH1/lHsRnQoBYpBDKP7NlE1q7DjQAH'
        b'5+P7Jji4bi1bl8egoldMcnWMTCQgn/2mHW8c/3GRZreCSpabhS8AN9S6g4y/maieLbUFIWvSNHIYXa8JQEoX0OVyS8Y3QeDzrkbVNvqCTbGxCrhNrFMqPisJQQ1pVI/2'
        b'TcI1mu0AuVpNKA3cWhXVStQIU/+NXTEKjfrSTevGhh+C7os2ve5BB78H5qFRs12EekVs6atxh5/Oj+KfVR5GXu0T/IqfAPQVwoMOc8olFZ1HBwAe5mSNgMOeXOoJvFA5'
        b'PjzOOAGXa4SLG74lwFeguCcDt1FVtI/B1wnKPIYreAx9N4Lva2a78RFI3w5gevUIzKyG+ICu0zmYjkbcYIevj9mOV8dvx60i1JQO8QtZp8UQ59zXWPmhWzwGTs+EiXUQ'
        b'mXHb1+L60UaLfDJ5HIFgVhFI1L6WiVSH2p0AxOLW7SaAGwXSUr8FMVOzSXO6Jm7BC8JsXC1RM3PlDn73JvBxQPUmNByImnSRpIsz+CyEEyMWq9pu3VgbIUS95skxC9E1'
        b'X06Nj0kBzJycT9UtaDOobp82PdcEoj0X0rWywZdhzfvwjWX+PKaIx+fnUkeyuGTheCe5KVYh4qahVpFrEGpJQZcoZ/NkErOZz48li30JBr1QR9UvvGANKOzd3aP1b7SN'
        b'pZY6Ap8Wofp9gHDJyMUALoGVDO03wXlUA6aHcFM7eYxYHrQfUEr1iHGgdwUwcItNkbw0kSTaXMtcdwvgrZPAD/WsMoUArnzqcJfjh/h8InViwGHcRgPEtQvVJANcq5Z4'
        b'JURSXkvQfoD/uNcBX5KwYZ4Sg7kma4uaYieN897AZQ5uigXXncxFoJvg0dAlFl0H42uTcZ8laHyPhAHcCxlzqZ7lTHccvzHC2Ry54R5BFGC8LvO5DLxftOSBRQGvf5fo'
        b'WS+4woVzme8vjd87xp0BlzQ58f2T0AEBvs9DHXQ0jrNhH/ZtBZ91g882Vi3av5QByBbU5jHGxo9WeFQmgJYH8D1fvJ/FlH0ee4ATPuAvZuatbreDzpsUdMdNGzeeHV5R'
        b'fIJCbgtwjyvgVbpGXSozEorBOj0yxWKxaUaPhi4tIiFX+QpTLDbHkpZMhfD4IimpX2mKxbZ4s6k5FEOSYttQlykSQ9UxbJXO4TL7iZbnOpvgbsFiwKtdu/EZFjweRXew'
        b'HiI3CLJrTaEb6ohjvuYAPgjhoy5Bbtww9Y7mFEsscpEZDUW7qQN0Y8RSTAaRb4TCnqFyXvFQAAsJKhcxKNEQhLt009ioD+FauB4H2z0Bl1wfhSvD8CkR7Lw2fJ1Br+bF'
        b'AP368M1J+IFx95wEi3SC7h7BUvCeDRkQTY3RDWqARnFcLUJ1+yCmJMPU4XtbIUSVL+OzyW8NQdV076DDEJ0/ABUpBQc+ausQ8zDio5YmSWYUAE4mnNLmQERrscncFOni'
        b'u/g8NdQzwAU9BEZnzEfbiGvjJy8CPRaBgh5SGJMotl4kdH6oFbEw9MJKb10YKWj1Br0Y2YjxamDGzzYKZg1y3YmyQfpIHjo93ywFvEoXVcCQaYDqIKj2zTGF2zDzx1lQ'
        b'dtUP3Z8QbZhstlKwEtdAWHMqwRhJ+QNOBUaScFN0jjp9KQYJQ+0AaMbDpqjV8UZAZwQNOlHxJNifRD0EObgdAvrd5mLG6gxskDtMx9JCJypxB1Piu4L14Kp6iyGooOC5'
        b'LAffAS4QR7SZEgN7Ie4jfjgN3Uh+JSQ0xomPhfheluUkY6iwfE2MXArLXSlmQfxFfBM9oqhgzTrwRxOsVieT57rAwxFc8HFQKBIqJ0dMlUvRQytTKiJwAwsOmz0QoBRL'
        b'UOWxCG2UMgVJpqevYxunCz/0kEPsKzR6mwZUup0lIfJek+PeHNxmymiEo1baJAvfXis3w/tRz0ji4NhqZrxaVqBr8m24KoUwuwohkHA3XXnXmNwx8HPMViY2kIQCjy3y'
        b'WSKwA1W7yLdF0rxEB4dOeIYyGHI9a98o9HVu0Wh9RH3rcDU+tAlfWMepN0MAlS2mIr2OL+Cz8m3hiabsy1ZURXcdPmxDN93EyD5zlsjWGDt1QkSQCopNOLmgit1yfGt5'
        b'oilbg7vWUxAfB4ZIPyEaR7eEEMSMtgbBqEGkDd9Gx7hRYQa85E6mBA9+VMhs9DFcFQMl+N5MU4LHS8oM+2mIBVvllqiBphYecKgtBV/QhUPRCtwBkS2xH32virxGW7hz'
        b'ItRiD66C2LDgPFz3zapMgBPXRVuX4NORvKVSSRS+vobqViGuEkyIEVGnyGNTFixAMhfuJEJVYBQf0droyuZJY9C9cdlZlgL1CsGGVgtn406q+uvl+MSr1uMa20EVwiI7'
        b'aYwpAXIF3yEmYIIpYdttlkC6Gj8E2HCCKg66tCURNL8F7x9vMsaZa9wgQmeWuCuldH85Oc2QWy7FF4jne8ShdufFxngG9aHjctwTtMe4886VqNgSdeKKWVAwHR0hbe6A'
        b'KV2FmfLEZ8DGkOGOLD5buys6XE0VIUXjKteJAK8y9TyBemPYVjqOurfLNWtglox5O56Sdl+AKhLlGnwD3zTuy7Nz8H3aJCSGhypxd6KWKNVDsCrrAb8TkJumAxcD7grp'
        b'jSk7mNMO1GPci0hP83xC1LcCVa7kVm8Q45atuEEp1LmRuasEk30xG5amMmkJrD4nwI/A4oOFqWL2oxbdmJmIK5LEHH867nidF4rvF9EkYhrUepiIa0JxdaAStQvxkWjO'
        b'3FrgsCWENvTB5WpUii8GpgTHCznhfB5qt9PFZY8+3SVHNPT8qAoux8SmE9ATnJ5Hj7r4eo4edwn08lwZPegS8rly8biDLhE96Bp3/AV3xp0N87i9wr0i40HXK8tGH3R9'
        b'OAwLaaYY9YolJ7oaRWYhPcpV5BapFdsyC/Jz8rUlIWMqjiES2EFywOaiQm0RPRQOMB0jK/KB27bM/ILMrAJVEGW4WKXeYuxAQ9qNYZWVWbhZkV2Uo6LHyoQr5afRbTEd'
        b'V2dmZxfpCrWKQt2WLJVakak2VlHlKDI1Y3htVxUUhJiNuTWzOFOduUWRD93MVKzIYyfW5Cg7a4RLyKsaZOVnzyTD3Ji/TVUYxFoRARckxI6RIL9wwojIKxsmRrVDS4ag'
        b'yszOUxRBJfUrO6JjU5eM7kxrEhOm8p/vR0sO743cQhTJOo2WjJHM+/LU4IiwqChFTNLS+BhF+CuY5KheKZtGVZxJBQsgnwIUKlANXaZWRZ8FyMhYodapMjLGyDuRt1F+'
        b'NuNUtYxjUSzPL9xYoFIs0qmLFEszS7aoCrUaRYxalTlOFrVKq1MXamaO9KgoKhxR0iC4G5dZoKG3ySRvz9eMG8yYw10RN/Fw1yYljiGl8nW4VbNVxOFS1MiSZ2BAbtOj'
        b'2wfzXLip2hkSLiNj0tuT5nLU1OJ2dGgPqiSf6rav5dYumk7r2obJOXthBsdZZwR9uN2fnf0+8bXkJiXdFnNTMwp+HJfMsSRbDb6LrmnkfDC76CLL/yzFp5VWxtMZdH0Z'
        b'LexIYGXo+j5qfj2moEua7QLwu4HsbHHpHNrC2nOLxopYN7D89GQR3NZl2sKGHwhoWQgxfyo7WEwRMRjdjmty5WoRN9XReLDYMY1Z8hPgp+XFAg71zKQx84k5KxjOOTEz'
        b'T75VwGXIKYw/nWY83QXgVg62sxLwPSoT06NIT3SQDjMSRteC+zRigttqaaBTj66wBCguy7LV4F4eB8jsEjuoLEYn2Xoc8EC3ITwSAINmdlSJzgPipM1u4eqdgGpFEOu5'
        b'suNK3LqWrcpNz/lymJx1sdTNnfV2ZpAK3BXug5E6JgIqgQh1KjpPCwpTULtmuwSgogPN89WuMR4P4nZ8erFmO5/ba2E8+HxkoRSw06ljq3APKdq0hxVNV9MFcJFJaB/2'
        b'6C7rBJxrLzu1Q0e20l4q+awXcGyH2TAv4l6k1+A+WJ0aYEZzjWmvK/lUiDmF6AIt276QlZhhFjvOT0U1GlRFIKGMHUkXoONU1WZOEnPm67OEnCIjCG0JZLq6bEFYxFQh'
        b'J8adAJa5LC16nL/+/n6RxgPQwHOrT6qXPUzBU63npu/etiHvzQPWdoIHvKIn8qlTW/84Pe3qwcC0Q0MWwh/VrIlQvZ34m0MDVysnv7ks55NHLbP23Sv6D0HWe2996vW+'
        b'z8cpDo9m/nWPS8zfvKIrKrP+kj28ckZItsOnuh983Szo8fnXO1nLCv8tPWeO/L2VxW0X3un95M9fHu7o+L3hw4TPtGE9bsPr3uC7FghC3+RHmcWYxZwbuJSof295jG/U'
        b'Zzt+8bj+0NdXDG0L86Za7Go84vCbt/s+9X3sOXC3qtBVd/vgvYaqP077NOSI1uvkwmc+Hz2wqX/02dq2n7w5dfgPUzvOfu65WW3vvjV4INtHtXHGUIV7wX98sWafx7a3'
        b'q9Ju9lnHhvs9vJV0Nsz9vdOfXv/F0bdXXQqZnf6bltO7/lPkEJlzTRerlLwggfVSwE93A4MBst73jw/mc2J0ih+chCpeeHA0U3A6LDAkIShAGYJrg3A5iUp0zgrh6wjq'
        b'v6DHj00QvzUkpgaj8lQKPNBRkTyND0t+SvDChehBjdyeJLdBmQKCQ3jQwQF+BO7F518Q7JgHRmk/IGX2EM529hDOtjDcFByAK0L5XAh6KMI3ZqMrVFh0ftFuXJkMAdqh'
        b'oARcw3HiaXzLSHT8hSdB8VkAfWh7sD+1DB/hG9sd8CEBvuO2XCkf4vsr1UTNv9NFQx6cUShKTa+vHGbnqot2qgoVuexJsxDihecOmVGfkE6InaM+8wmL1+D6spQbXgpb'
        b'yHmY41m4DzpNqtMN2jmdmFk/8+jsxtn6hYNWtsOc3MJv0NHlRH59/tHNjZvrBIN27sOcxMardcqV0POh3VP6vacPeE+nt4b5QgefQTefZ27BT92C23L63SIG3CK6NbdL'
        b'ekue2D5Z3j89YWB6wlO3BINbwuBk/9bIYQE3aQnv5XM3nwG3SBDCweeby6DnlCZdk25YAJ9fvnz53MW7yaU1ok3S7zJ1wGUqVLHxGnRTNEUOOnkQwm/Qw6vVqzWmdfKZ'
        b'vLrFg1aOw5wNjMnVqyX4VPDJ0DOhdRIytnn181qn9dv5D9j5w9CABW3tt5QHV2fT9TnpelhEb4g5R9cT6fXprSv6HQIGHALoQKGVwTfK4ETeVE4YiPP05w4uY2sKac3W'
        b'zQanMHiPVAx/7uLe4nnKs82p3yVswCVs1FjsnCjRtLhtrmHSDHjT2y8HbRzoEjVNaVK38prUZ/zbQgyu0fBmi+bo2hTeFNMU3pinJ0NvyjdY+cGbFdq7N20csPd9Zh/0'
        b'1D6obUW/ffiAfbh+0aDd6GW3cgFxLaYNOnk9cwp66kTqOYUPOIUbrMOf2zs32TTZNtk2xjdt77f3bbNvy+zmtWV3ugCrOt6gk7/Byb/Npt8pcMApsE371CnCYB2hIZbw'
        b'DWlwTDT3RrTZArEAiXhwVUNMwinNh4RED4cEgP2GJEYkNSQk0GdIkp6u1hWmpw/J09OzC1SZhbpiuPP3t4M5R57+Alxi3BJq+igGMd2j1f44qXoULi/JC1Q/X8jj+cIc'
        b'/Jcvzy2d9Pnlm6s2l8qH+SKe/aDcVj+9fEbVjOdCq9LE/cmHkkuTB6VWg1I7vfzlsIgTWY+9W5rK/mlIIHNWNo27YRnDF4DjI0bKPW9LIhgMXJmCa1ITRJxlMa7xF0Sr'
        b'OBp2heDT6FJiUgoLn3je4LPl6/gk+ePFgtBrxbjDGHZF4WYIu5SoPNv06Cx5CU34rJQET3wWPNHQiYPASZwrpAGTAAKmccHOHiENmAQTAibhhKBIsFdoDJheWTYSMG2E'
        b'gGmQNz5gog++joqY1EVbFJmmGGdsNDM2chkXmaz4OwGUWrVVl69msLlYpYYgagvD96anccci3FQT8AVBApZBj/lbVIvU6iJ1AGWWCSU5r46LiLxEXBYbjR/EK4MC46BY'
        b'i/EjfFUXJJKKK8jcqMhn8Vx2kVqt0hQXFeZAAEADKk1eka4ghwQIDOvTyM4Yzb06FFiUT4b8TeQBUWamIjxYqyuGiMIYX9BZg8DIn9QIIh0pv2NgIErRzSFa24vaN098'
        b'/lWPy5MClgSh9hXsOVhyIzUpIRnwb0MM6kDl8hmoPXVF/rWPKvmaNOCz6dP7p38c3nyu4WbT40NHeZbLnE/wSjo+9E6uunKsuVNe97FNa8PdBuXhfJeIpZERSUFHyvef'
        b'O37ueE/DJf2lI+eOhFUrm84d8WraHyHgfvWl5ULNl0r+C3LGkopKHeUBsOFwOa5K1jFAMAtd4zxRnxB3LUHlFKPsXIc7E0OWJAcloGqT23edlYluCAuj0H6l+B+YM/GI'
        b'd6eGbEjOHgFnfnw0QR35Uo458jgJZ098mcVC3geO3obJC/odYwccYw3WsYMuk5+5hD51Ce2W3vF7Mq3fJX7AJb58iX5h3RTq4XkW3oNObk0r6nYarL3ABekTvyDrxGy1'
        b'ZEhqUt0hiVEJ1QRMq0kOR+02VnQJs8REemaEvch0jJb5Gam23WiFQezNYh5vCrGm/+DyvdlagtubZCHcdcvZAt1sonQtqyC8HJv+ojlAdAj1oirUGiTYkDhNY49qtqJr'
        b'6DJ6aMZl4XoL3DwddzNbexVd8JZvs+SBWcuGIBF3zMcPWKRWiS6ulW/bCiXoEG7FeggfzAtZUafOE93XavAtq3Ahx8f1PEdvfJ+FPJ3L92rC1XyOF4CuF3HodhHH+nns'
        b'OEW+bZuY4+EW1IcPc/hUUjZ4C1K2m4+ajeZejKrA3EM8epD6kTh8QDAqy4bOeNAsW/4U04OwN10DwY3wOD46gHpQDS82Cx0Y4ymkpg2r575Js4GnEOlNiTYZeAyzXOmI'
        b'xxifYvvv8Rh/+bYUGzV1YxNs32oviW0l1f9xoupb8kek8f96+ii7gIqlUWknJozGCUjmpSg7WweuoTB7oqCmlNGipTGKWMBfauI6FoKLzNYWqUuCFMW6rIJ8TR4wyiqh'
        b'NY2uLFYF48ksmMBvARiPkFGyZZJF0dFvyAQsj10REAR/Fi4kf2JTl4XBXxAvYEH4AloQGxsQNIHjqDFlFmiKXpn4IoOk81zM0l3ANYd4sZLicRNIXv8UPhjhWFQ8ERaQ'
        b'1z8HDcYs3veabxvBc6PcqlVKnG4WkJkSl+/kVcGlTkOP5DOw3pvmOYaSXLhSt1xi2yfhubtZni0p1I47JEogFn/9QY9QjmVyruMO/IBm6tbiho3cWjN8jdo7vidY1kqk'
        b'R2BE+HbmxTwZOojuUEa6ICsueg2Y4qkZ5o/d1JyST82gGWrDtyLgQxg+gI9xYRJ0it53RrdxJXlaORw9wFfheodP2XABNtwdyUKOK85IcndVEDbkyWBPfBFXUDaoxYkL'
        b'c+UxG3tEhqtxn4RkG67mc0sTcB1lwvM143I0wTSj6LVOy63Ij6vzFmk+gCL58Y2H03rM0FTrh+uHLl47EF3ece/lnOZ7ntFSy6ttB0MO4LuVmy+H/CUh+7XXLHgCr/c/'
        b'eGdXaGjtx7Iqn/q3Psj3uhFw+/eP7k3e3PfRnTN/+KTUq/NQbHnqHgdlcUHYD37k8SX//u9sv9w0v/PJQr7ZjvszUYJjsb10Us+/XlSf0f3L5vc2dqctXfTLl3/bvLdZ'
        b'O0PasWD6nl8HD/152V8PfXxra97xKvuf7hJX3P/rT1TXYl0vHqipe+GUqC4N1zx80XHC/cmNNfmOhf+aG+W9B2e++/TIxw+m3fpp7a3Z0971+uABF7luxqWgQqX0BXUH'
        b'+1FrWmAwS7vEYT3JvOAHO16QZ13Us9HxCeCHIB9Ujx4D+sFt0S/IiflMfHEr8SioPJWkYEKhWjBpkiiBlWwVuokTwI2eZsmcOj9cIU/EVcpk3SLUYGTpgMqEUnw15AVR'
        b'qCzcgNsTU4PBP21D7fa8GNS3mSZeps/Hj0gSJzSVyLoand3LD8BH0IEXNKHbN38urkw2ZmScldP4lt7xLwhikaEb+Fgirk4cSR9ZTY2PFWycFaWUfbckDAnaRnIwDKnJ'
        b'WLQJjmXnNx8pSkviMZS2G1Ca06i429bhhLJeeTSwMVAfS8GYzMIHgnCSBYjnfeDqa/CL63ddPOC62GC/eJgvsPEa9PB/5hH91CP6jl2/x5wBjzl1i+sWv/yANRl1oYmD'
        b'pshhAXwm6RM797qZTdmtEf12fgN2fsMc38Zn0M27ZdapWa2aKyXnS87turiL5Wu+yb48t/N4Zjflqd2U1uX9dsoBO+XohIGtXlMXUb6jakdTeMVe/d7Wya2ZF33bYs8H'
        b'twbfETw2v2f+ZGV/dOJAdGJrsKlFXVjVtiYXg5U3vFuz27wu5nbLDL4z4G2s4ciyHBFNW1ttmjRnolu3X9lzfs+5fRf3PXWLMrhFmVJUddM0ZGtfd4gRcm8IzWJsBW/Y'
        b'8ODKIKuc4VOiJEMCcI2vQqrfmlabkEYgB8SjVvOPpGLlN/h1rYTH8yQI9b9w+V7zB2dk4VyvZQwnUPLo8SpYyXJbtB+dH3cwe9l1zBcGR9zGDo6lAegXBoW5/JEvBo6D'
        b'bf8NXwwEMPfVu2M82zLmGb8lis2lQSjFYKOPPP+3w/5vdc2CV7hmcQr1zKhc7PfPuOaAtNHOWT5jOqpgp0qnrXCLJgAd3mp6Cn19CXu2ot5rD5hNXJGMq5ZjfRLfdhG6'
        b'ig6jS+jkIrU3uqrkllpL0K1g63xez68FNGreNyvp9I+nQdTcMz5qbjaX1914/LFNhot115Ev7jmXftrUfTUxc0GkTZ7nrPqgiCN7quRruk/+7O3S9nCImi24pR42Q5c/'
        b'U4pekPhvYxCqMjmOc6+N9R3gN3ZmUNeDbuIK78BgfHLXN0l/fHQZzaNDw1OoLBDdWDAm8U+z/jX4EMv6X8xEDfKdFsybjHYlrna0Qhy6ix/RUwFcidrZyQA9FhDhA0r+'
        b'KDNADLbJoks2qrTUnps+UGuexTFrvlf6rTH3mDz6+MQzz2LGB44Kg9f0fsfoAcdog3X0oJ37Mzufp3Y+rTn9doEDdoEG80A1STkwkyZSEwz1ypCbpFMyvgm4ZxJzZRLW'
        b'GXa6ZjM1ViDtFimPR8L9V1++L2P0BYFRjbIArt0yWvAPTY1Qz/2PmppcMDXtY3bq8uKCfK1mxJ6w43UwGgpyN1eduZEel4+zLSb7lKmY9spU2JjK/rGpK1NWLFsbpIiN'
        b'XxSbuHxlcpACeklMj01duChIERNLy9NTViYvWLRM+V3NCIWtz90knDnH5dUGZxTscC/hdNFkR9zFD/At8mX1QPK98fKktHiaB3ALYM/b1CvRVTN0sgT+J6DyEg41i82Q'
        b'fkqxbgo0to9dPbolWBAvfJT6EQ/cJkTnUTe6l98Z8gdOkwe1337Lk5mOEp4gqttcvxqXbPhJ80+U5sqqa0n1xT3rjrgeSbkc/kPvv9rmHnpkf1lVNb+5aupeu2y/5Raf'
        b'bBAseMb3LbilC7/wabuqMzMoLvKEywfvu/5Q9BPzNVz7OwddoiO44XOOOWcdlUKK/XAjPokqAKcq0f5vjEVFCgOVV+1xg3yMGcBdMdQSBOAD1NZsQQeiCTzEt2aMnNn5'
        b'YT09HFyA23BfIkGt3vhgsL+Ykznz0TkwX0rhK0ED0eqR7TdkBgG5xpiqG/WZWo1tRqvxuoyzdx5lHb7l9IZaiHn9jvMHHOcbrOf/g3OcMKje6tHvOHXAcarBeircPTG7'
        b'fvbRuY1zDeZe/yVLEkssyagx+I8xJsmy/wljoiY+EgANcQKRKzYwKIMqcW0oqkhFJ/dSI+66T5g3fc+rTc1uYmqEJlRDfgTBeLDxP4ZsPtww/mBjNLihJwCFmVtoQuQV'
        b'mIakQ8hzO8UquAHYZyzKSGBGpyBTq1WpFdmZAFDGMqVQJzOHnZ1MyOuM4TWS4/lHKR6W0vm/hLWkKbq5QE1ehVtHsBaoUdk/mQqRz8C1qJY9cBTiwl1UZJIwYXbYTjv2'
        b'wMdruJOnYfjLmnwBbvdM9k24W+gROv5tGIwhMHQFHwQUpnVnTy4VSTjpLlfyoxdBZQ5Tufy5X6eJNMVQ8lb2UXagcXU8NEsyb/5Jc955ZdIvMrYdzfP7Gb9t6ZQPpKXX'
        b'Jzv795bKTv9YNf+B67u/zxK2Z//wcshhl58vbL0/42jO2u47p0X4g876Yveb8x+HZryZu9xCcO+XM37G+/ebkzbeHlKKKXJbuNmOAbe+7eODfgBu23ALDfhxb6h4VMCf'
        b'ukSGz5CDS1wDRjhZxE1PEe+1S3xBHybqwcd9TPkFMNqoyy14y/oX5IdsYLJuoZ7AcQDPc7rwdT/0mBn2u7t3ycfDu43oklCKD+JeekCzVpfJEN6JpNQlo2XwRPVC8uMH'
        b'QWAAvzX+IwZw1LmLOUVRoOxkK+0cQ1F7fsloz+PMvhUF0ih5Vr+V54CVZ2v4Uysfg5UPPWMPf+oU3j2r32negNM8g/W85x7KZx6hTz1C+z3CBjzC6uSDTt7PnIKfOpGn'
        b'KJwiBpxIVG4z5wPXKQafWf2uswdcZxvsZw+6+TTNbN3c7xY+4BbeHTbgFlknpdxDnjqFtO3od4oecCLgcpT5lwzJiS1PL1ITfPj3I2N2mjPqJEqdTFzCmImYSZyCzuQU'
        b'toJTcCEO4B9cvtfDnOOyIK7TcqZAKUhJiVPy4pT8lLj8nS9/INSQb2jO/dyuuv63q+3SrN/8daHZ1ReOFRbyL3/Vk/0jcZT9iheuC+0dzmckBelzp2f8NCaozSb567qv'
        b'j/5qw4K34vSF7/71y4fTNb999+MH/V/XzflYOiP2erB93a4kc6fBw0ED4ZHzQmRHn8/68/xPo/J//ajmbf+cf1kRn6M6texk8k86w3PR7NNL3jn85o7j7cs/S2yRHv3Z'
        b'Lz69XVeyd8uWLxJ3bjvyUc7DX/Fb8u95/OGHrgfr57wz+cyvl7/mN+Ua3tTiE/u7qQF9vzdvWrfo8YDy+Zk6VHjnedxcsx8mx/T7LNWf1x/Kaqy75D/5nbSYVSh21blT'
        b'nTHBMySat0uaUkPmu9+1rnzrzTUL3stW3jV/522HNQnX0Sa1xXtxU77q/Nnvr/1IrJ4cdfR0z+H329/ssfjl2+I/KLZnOd112/XWw51aT9e3/xI93+MHXv8+taZu8Z++'
        b'9p00ufajhQsr8lP8tlb8Z+6Nuitbj8yu1HxccqPeqfhoQeyskoTPvu6d+5nDnKH9HR9HPnR7PvN3i/xKBBs+TtY23C6e9cnAwVnv//rNOb1Oey5a/cfbkn/zkwzXvfjI'
        b'xsXwLGbOV2u6XgpT397oPKUlW797/4mc+L99Zv9w18qf/XDKDusfTo0bNuv6XFz0eeH7jg0o5ecuP70z72epZ4q8H262/38/3dJrHaP0l/xgX0C77rAyz/KttC+SKkqV'
        b'GTURfl6pzcJPjro+sHprb8etVYEXjrvoej/f1v5u6cCTz+Ir172xa8PFnS/St4bbXiny/n/VTcvaou2vLGtvDCzscrgQuy372Q83GOrTuqL/7PXuXbvf/cJm481lXVU9'
        b'+1b0vBslmev6W+kvI/4yLGv5XPTRy09v+j5Wlfxt1R+0oR9OUVWUNez+lw9iB8NWznCJ3Hk592VYzjszYl+3fNjwVfn7X3UHXvvbn2/P21hc8tOXf6r1KLAORr/6s+RJ'
        b'VnDkwC2wtMSHeHLbAdzg3l08jhdNHlALpybPHJ+eN9rkoQczjUEtuowOUxvt6yYfycrilqRxNhofnMQeU6t3JaFAUAKuDhZz4tf5NvjRZB/c+oJsfnxGEBy4JBjrE5JS'
        b'RKgKV3By1MPHzbix4IWCNG7DJyCuBscJdXBVggidxJ1Qp4uP2/FldE856bs9wyb9tst3fhLulWaLBPsj4GA+eZWOeTHrLk1PLyjKzElP3znyiVr1KxLjE0LUtPM4C4dh'
        b'oUTmxEx5ePn2qu1NXhW79bubNE2a1vDWzIuRJ3ee2dmWdmpf077uKfBPfcfrhu5O2o0dPSE3Qp4sfLLwLds34n8Q/zQ8yRCe9IEzAfuZZyJPys7IWpf0O4d0O/U7Rxtm'
        b'p/Q7pRiWrTCsXDWwbPVTp9UGp9UE0dseLWwsNFhPIc+NreENm3G29nUxjQ76BfoFL4clPFkCb9DWsy74krkhOK5fsXhAsbjfNn7ANt5gHg8jGDYTu5oNc6aL3nLYnrN1'
        b'GbRxHrRxG5YIXeA2XPQWw5bJPAezQXNrg63PsIB8fm5uXRc6LCIfh8WchQ0QEkpIGSGjhBkj5JQwB8Jg6z9sQSlLSk0ZtqKUtbHMhlK2rJkdJexpUfCwA6UcKeUz7EQp'
        b'Z1bRhRKujHCjxCRjPXdKeRgpT0opWEUvSngb5ZhMKY5ep7AKPpTwpRWUw36U8jdKo6RUgLFxIKWCjFQwpUKM7UIpNdVYFkapcNZBBCWmMSKSElHGetMpFW2UewalZrKK'
        b'sygxmxFzKDHXKNU8Ss3nGZnE8Ci9gGdkE8vohSZ6EW/UoNk1jmcUezErizfRCYxeYmqbyOgkHpMjmZEpRjKVkUuNZBojlxnJ5YxcYSRXMnKVkVzNyDVGci0j1xnJ1xi5'
        b'3iTXBka/bixOZ2SGScxMRmeZ6GxG55iaqxidayrfOHFK8lhZ2HA+K9tk7GozIwtMs72F0YXG4iJGFhvJrYxUG0kNI7UmOXSM3mYs3s7IHUayhJE7TVLuYvRuY/EeRu7l'
        b'GdVgH6Pn843VY/hMD/hGSWMZvdBUvojRcXzT2jM63kQn8EdNxxI+Z+c9aOszaKukVy/T22d4LX/85Ollw+v5nNuUltBTof2ugQOugWBRZKH0Ur5EH1vnMOjs88w58Klz'
        b'YL9z8IBzMIHJQfRyVFjHqwsbdHZvsThl0ZrZZtPvHDjgHFgnqhMN2od0O/TbR+kXDbp7tqw7ta5N1O8eMuAeok+oyy5P0aeASTKzHpRZ653qsps0bbHdOQbZrH7ZrAHZ'
        b'rGH+HNm0Ye47XD4XcGazoSX5a13lOCwkBTDXxh6aJrdquoUGWWS/LHJAFjnMt5E5D3PfciE8oqDWCC9S4Ms5uZzYVL/J4LWi33HlgONKvfy5zIqJv7x1ctvCbodu3Z1V'
        b'Txa95WMIXGqQpfXL0gZkacN8X8L1O1xIr8t40HSke1KylPfNZBlkrv0y1wGZ6zDfXAbrMPFCmrpBhREWpGDSKzlYyryHuYmXCRxIgWJkOpcbZF79Mq8Bmdcw31Y2Y5j7'
        b'exfCwxuqjvAaU0of/C2PmbfAlkO2rguCjOd/1kP89PR/9tDvnwEU1t/EQWNBhHolCYhG8MNkih9MwVAsj8ezJuHO9375Xs8NW2VR3C3LGKEg/4T/RZ7mJySdZcPX1SXK'
        b'D8y3P/zZg6RqR9GCRbWLYua1HUvMzHMIWdJ9+I/Crn3v9NXeuv7+Sz+3OvtPoqZOlbz75z/e/eJXJx7YX/q6NNf1j3Wx4kjBb6aod0x/r//L62dUnY4r4r5Iq/il/d+U'
        b'7yU3xm3SNz5T/ki/ZCCi4ueDv/wyYNm2y4lfvvjbn3IyfuHxi+XWKS3qmtdmC36ZlWL7SaNzekpdp+RHLh6v/ack4wePk2+cCl+gV5mF2iz4cd2FBZIN688/cRDfiSmf'
        b'Nfv557cMKR+6vv554I43nVwjw371N4PSgmYXQtBZCf3hVz46k4pr6dMIctTLJ7nsh/R4CB+0XEGSNT1QKZU8UxCAH9vgBwJ0Tsenh1A7APseQpWoFppf3kTSCqga1Uo4'
        b'S1uBRy66R59WwHfR+dcTE5K3pAUkSzixkC/1tGIPJFxQ4vLAJSKOl8jNBKDehCrw2Rfk2+GoDrWRJ1rGngGimtBEAPI1ULVWwC1GPZLcfdDzw/UU86Nu3PXa6CZr8Q3S'
        b'Ssw5LRQGoBOxNBkShPZ70mzIaFZu6LQQ3cJV6DLu8aahgaMMGFeKyTd2E3GlhBMG89C11aiLnao1B6K7uFIZjEtnoXIYeXkqQAKrNMFKefALck4AUUWHN6lASoOI2OTA'
        b'IBS1QTUFviniUNdWugL4Dj4gDUwNQvVTcAU5WiArgB/x8W1824GFGT0r83EfroIgIzRgqzGMcdUJ0d3Z6Mgk1KL0/vYY4nuJHL7Hi8abBiETYo9xr5FQJL8wX8tCEfaJ'
        b'hiL5vJHHDFw5kV1pCvk3aGH/zMLjqYVH845+C/8BC//SuEGhWVnSgSSDjdel6H5h0IAwyCAMGhRalCaQf+AsXT0MQsdhvploHW9Q6mIwvQG/e/g/c4946h7R7x454B5p'
        b'kLoOSi1r5RXyn9v79kv9BqR+BqnfoNT2mdTtqdStKaZf6jEg9TBIPQatXJ5Z+T618u238h+wIkeaMuBtblubUpFicFvTb752wHytwXzty5d/suHMnYY5vmjqN5dBBxe9'
        b'mbEng31IvzR0QBpqML2HRVCFRC+Om4UisPT/zdd1Ms7cHowh/caKSLggikNRXrGuAuzCgytzKZ5DggJV4ZCQPEA4JKInfkPCgnyNdkiYk58N16JiKBZotOohUVaJVqUZ'
        b'EmYVFRUMCfILtUOiXHAP8EedWbgRWucXFuu0Q4LsPPWQoEidMyTOzS/QqoDYklk8JNiZXzwkytRk5+cPCfJUO6AKsDfL1+QXarSZhdmqITFNz2fTh7FVxVrNkM2WopwZ'
        b'09PZEyo5+RvztUNyTV5+rjZdRdLmQxa6wuy8zPxCVU66akf2kCw9XaPSkm/VDIl1hTqNKucbV6khdi7j770UCub4ckwX8rPKmmCeKWb+lhdosA2Plycg7uv/8vV787wE'
        b'ubxhJotRcG8oLGNCBF9JTV/dG7JOTzd+NsKKr1xzx/6AvKKwSKsgZaqcFKWUfGUqpygb1hM+ZBYUAPbJMVoVkqGF+2agOmqtZnu+Nm9IXFCUnVmgGTIffbSiPsgZE8Qs'
        b'VUyW+CvpbPYD9XPV5HEncrqm2QOXYQHgmmG+kCcElA8Xc05uUSoZFsfBdAxzo67LzDiZjdFwLGHGBDY/L9IQNPeJ7xPfN/x/4G8IWgLvQan1oJmjPsjgFNFvNm3AbJpB'
        b'OG2QszZw1nXO/ZzrAOdqML2peP8fdqtFag=='
    ))))
