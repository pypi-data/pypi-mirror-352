
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
        b'eJzVfAlcVEfW7+2Vbpp9XxQbRaXZBdxXRBRkV3GNYguNtCJLL7jvC82+uYCAbC6oqCiKuCdVky+ZTCYDwUQkZl4y872Zl8x88zBxYpLJzLxTVbcR1MxM3m/e7/u9nsml'
        b'z617T52qOsv/nKr2t9ywj4j/+/UmuJzg0rnV3EZutSBdcIhbLdSINsm5Vz7pwosC9k0nTxcJOY3kIt+Sz+nla4RwR5ouNj9zQAC0hWboHQG3XSLPUEm/z7CMmR+RoNyS'
        b'k27M0ihzMpSGTI0yabshMydbuVCbbdCkZSpz1Wmb1Rs1QZaWyzK1evOz6ZoMbbZGr8wwZqcZtDnZeqUhR5mWqUnbrFRnpyvTdBq1QaMk3PVBlmmjhok+Gv5TkNG+D5cC'
        b'rkBQICwQFYgLJAXSAosCWYG8wLJAUWBVYF1gU2BbYFdgX+BQ4FjgVOBc4FLgWuBW4F7gUeBZMOoEZ/I0uZocTDKThcnaJDbZmixNjiYrk9zkbOJMIpOdyc3kZJKYbEwu'
        b'JoXJ3SQ1CU0Ck4dplMk+YzTMrWz3aCFX6Gmet91eck7I7RptpuG7l/m7gNszeo/XUm7ca+5u5baJVnFbBTCfwoS04WtkDf85koGK6bJu51TyhCwZfHdOEnLiaYNwe31A'
        b'inceZ/SBm7aoDO/HxbgwMc4yJxmbcGmiCpfGpCQFSrmJUWL8YBuqpW8vCpVyVrt2CTnl+oA1sQs54zq4iZv34lbcKbdOjgYeJTEp0eiSLzYFLI7HlUtluDA6BTiW4XJ/'
        b'4I/LouNx2XLf6Di0D3fisoS4xBRfaDQFQ3/J0YtTfAOjYwIE6IKYM6BC5ymuIuNU0kU1OogKgTtlU7f3BSdgXRycHB0Qi0ug6zhcFCPh8lG5/A3UgsrTBMOmxMY8Jdvg'
        b'csy6AKaFrpUY1kkK6yiD1bOE1bKCFbUx2WbY0HUC7S0UD62TkK6TYNg6CYetiGCPkF+nl+7++DopXlmn82ydOBuYaY6zC8k/HRsVl8fRmwscYfHgb8iElY5hKQZ2M3Cm'
        b'nLODeyETcrXHp8WxmzmuEg7+KkMyisdcD9/GneeyLOF2VIa72Crwy/Ec9/nEr4Rdk8KTcgRZxMR9ltcIOiw4t/j49aFPdONnTeXo7fG+X9ketRUo7yZ/Jvjbyk8s7nED'
        b'nDEQGt7AhagYk/+1RQUn+/riouDoQFyEzi/zhWUvDwiKCVwcL+CybeWzg7ergo3O8A6qn40L9FZb8RlYFlzDoeP4Gmd0gZZo3BWs16Fb6J4EWoo5ZMJn8QPahE6jItSo'
        b'13niEgtoK+VQEa5KMbqSpi5c5qDHXQJ0kqhIBYdKYNFbaF9SfCRNj8pQk5eYKCiHGvCBGeytshAf0lKPbgqhqYVDp/BldJZJeA93Ttfn4QJcQAQph86mLaYtXuh2nB5f'
        b'RXcipNBwjEMVuNWPtnjvQCV6I26cTt6o5FAxquZlWIGa8X69tW4teaWRQ7X4IK6gg8LF6Axq1ePOOBUR7wSw24Tr6UuB+PRKPSrB+yPJc/UcOokuTzc6AZG2Ad/TKyJQ'
        b'KRG7Cdih0pm0Ybxzkn4rbkd3wJfj4zBAfHQ2bcCtqGOp3nYXvsSxV2oUEbSTveEuuNMa38AdpPtLHGrEB7KMRA/X4eMWCp0St5PRXIQ3ZKvoGwn4LjKhYiu8L0DACWQc'
        b'uixBxWwsraEyPb6G6nAVWdYqDpXPQA20aRcug5XsNOLOcBGb6qPo6HwqmhzVyRS4I3sU6ecKWYNrYbQj3BjqBaO5iLuEjFuRCz7DFq4eH0VNenwzGx8iYtdyqDIJ1TMt'
        b'OYC6EvW2O1E5v6Yn8QF8y+gGTTJ8GqhOGT6Br5DG0xyqQxfwETrccKtI0tS6kohxDsTYto32hU/hzkTcacAlYySsq3JgU0zfWeAYiDut0NGdUvZOg2o7lXzH8ilwH5fs'
        b'INPQBrxgSu5REXB75DZwdlfxTdRCJG8lqn8YdI42FuL70Ngpx+1ryJuXOVCbGlxCG9E5eAtkkaPDqIafqhZcL6ZCuoWgKvLeLXSYTG8Hh1rhsXYqpNWuJDLxDbt43avM'
        b'UbHV6tqOL8Pae+IiAXunZSuuZHNYpV9DBMEHOdJ0gczTEQ1blFurZ5ImvY0F05dTuHUW41fq7ADriK6gw7zwDRtxDV1ia1yzRSFbiqhadHGg8dc9KLfZjvkKfM0OmQiz'
        b'G2RAdegqfWW6FJ9R5DtIJKyXWtyOq+kroxJRuQJ34f2om0zgVegmaikz2SOj8Vlomp9ERtpJVLmbiRaGbuFiaJmxU8L6acYP0F3ajxM6uklvEKAHRDQT8MhA3XTaXFBh'
        b'hkLvFyZmU12TggpYLyXjcL3CMhbfIL3c4tDZKajN6Mk0rxBdQMVTcAW6gUoknAi3xKNKQWJyqHEU1VpUgKE9H5S3FBVJOHEmuhMkQPvR/lHGseSBi/DeOdS+gn8m1MxI'
        b'Dpbuiq/hiyqR0QEeTMYH0Al8ZzMuhtXO4XJU8412RAvkuHwqro8FkTdwG1YY6DhQO+6ORw82xIK46Vw66uAdHBjB/Q16Q1aGeeCwxg+ME6garoX5rcYmdHEKOi9Rx6NS'
        b'fNoR3d8UiVpXx3Phegk6phpFmW/B1bl6A7q3i8xrIYcK5kiMfnDfgG+g/ZRFqYxwuYyP4aOUYTi6iI+JuVG4VCxHnfgclWU9PoOP6vF1VKUVMPddZrnI6EssDPxGPWGE'
        b'WxJgerpQG+EUjS4PMUL3xKIta6g0DmCap/RWc63NQWVnuFFFpqCSgw6ASQ4sEEhzaZg07UyaKrF0JzrP9PgSeMNycLwu+BLxEqdg4TasoowU6D46i6ujY9FV1A5zM8Qn'
        b'lMgFfAJFuBtfwVcoo2TQ2rN6Hb4aRXSogEOHcDk+wSRqjsd15im+TKcY3d2kUEI0aFvuyC1W4jqhhQIfV1EdRXd88E29LnyvOSTOwQXGYCLqfdyMW4b4DImDruBS8ucC'
        b'ESpQN2+uJA9kecB8Zzu+hLpBrCPogjmMQnQxBkFbJK5xgeGxsZWKNoBYm0JBMNSKT+LTm1AxLH807pbC6jbig1S2GVvxBfD5syj6K4OYhw9uMgKo4BLBYVUOMaOL9gAf'
        b'goUTL+E8cacIPEW1L139eRJ0WG8px/VCtmzHAEpcME6HliW+4P7I4lfhRn71S19ewLZ40kN7vHRDPJeHrsgAOtzaQ+c/Ct/El/WoaEKgmHm+epivNopZ/NGNbCLbZfMi'
        b'VkuwSQQ+tBAfIy7gBuCISbhRAuDg8DoqpGITNgHAgIh61Yww9mwxTiSTls6sZWHkkGhMPy8w/awWQcA8zewFn583T2+z24OM9CRx/ccCqD7MQnfQHbqOxdqX7eU809AC'
        b'sUUOvshc0Gl0wRKAi5PUjGjQ1WS6gBBnKiHEDSnEi9mK9tz4wmjCd0pQ7UYLplydeH8sMMubacZAsUbKS2ptGHICLzTrIi7FlwRs5gmrUFwuQU1ZOcynXMbdufq8FVPM'
        b'kAkCUiu1Y0AMlTMJu1VWL8zYvIJsgJfEspksMk0HnNdKIFYBKjdjrDwXqvESXD/2FamAXzsbKrXmQHjdNFGixyddqVSRqGI3cMP16J4Fi+BHDQJm6oWo3FZvXISPDyG2'
        b'QtxlDICmseiQu7mjC6Qj8CLbiXKgI0rUAjYaj+/hB/icRag8li3tEdQdo7d23WmGeEnb6TQuQUeAzwhvChaFD4KsHat9p7DR61GjDJfsRifYNB6KDgJEiM6MNkNCVL3D'
        b'GAIt07JeuI2Lr5g7P/rjEIguSfToPDrAkEMDLkD3KENvMgENRPGuIBZOt2zDNXoFOhtqhpK4G52hSxY5SmDu6hIfBDZFzpkcqYQMjDipRHzKIggdX8xAxqwd+q2oRmtG'
        b'aqhrN12vKfhSyguPMkJspgViLgh0//pSySbw9Lcoryh0DxXoty53l7C1L527kwYVsL4G4g+i0U2Ime38uoyIKhNFJCoeZ7NYYIEaACNu0Zoh4kTogFjsasCoB4FPOhjL'
        b'C+9ErOMS4eKJu0T4anQmVREDRO1m4CKdIWAgHIAneCfStBhWTW8L635zCGnegB7Iom/w2POSEbJOCHIcZoZ5ElSD6xOYLnZATnBLbws5t4Bh03o1OknlnQU+7SrIi08k'
        b'DnksIq856ohE+Io1RBa62EfAGwE+A1xeOoRx6wGh0LDTvoEFwoX4NtObV6ywVWyBjyynnmHnHAhlBC07mCHxTIVxCmFz0hG1vG589I4YXbOKj1iALk1AnegEp8PHZLhi'
        b'ATpNR+mHGh0ImC5cYgbT6AY+z9BvCaqWgejXwYvUC5g2Hscl/rQs4Zg6mXTojc+MiJiRSgkXjpokqDEHX+ahXpkHYG8ZPkNW/QwZ/U1cRo0HnOP93JHKyPvZsaBPF80e'
        b'OwzXSVAVOjiHucczyzIJxu9cbcb4y9dTbnNRURLq1r5wRqVDroLeEcE0WG+aLEiWWExD1wC8sjRMPxG4jTWYE4MoQMgkIKFja+NjaSADBrzNAQR8YLY7iryWoFIL7wTE'
        b'0MUUDUlRQZOrxBZspCddcLnRH5oy0UGYuRdxHJ/HFRvMjEgMD0M3ILSBQ7xELSVkG27AnTa6FAuGdVtxG9gQddsX1wFmBc07B66vfYTqXWCmchV0T7mCLqA7+OtL4GXK'
        b'cGkyUb1rgI1B4ffRBVTjy2kjgAqAqDKGBkahA2C2qwBf03yrApdA/515i1kGV0905OheJg5EyRUUENwf+8KohlkCKhDh2wYbBnQa0C0x8LFCZ6XM61WAv2+m0oSFEAUe'
        b'hk08wOdcniIk0OQmGD86Y645nBS9QfK1RYFD2doNSBAo/zZ0Dd2GrGucfChZ68K36YzqvNEBaHHFpeZMbQduZbH7XBok3HIhKjQnanGQnRHjTBkPwwaZSmH1Rnqly2yq'
        b'O2CqAeEeZdN0BdXbkbzuNm42J3ZrAMFSLTuQvpc0HXDhzajKfy5F9uhCJCxC9DaYx8u8rlIMdP2FI7num8hjzqVLgYccX5UwjFHtnEL1fhN+sOxVxAlCJoA+vkCdk/BJ'
        b'CTqVhIupasyCuSep7Q0lruLtqBYeP0VjhAc+Aq5vhG7QYbcBzrk+nOUKCapwzmfrsh+fhomzRi0qIZv8JlRgQyM3hOgi3DoydBFXgdrR3aHglRRnMX2UOd7s8CAlkNNZ'
        b'5jTYbacxFO5HgE4cHOkveHRXC2nci2kLQw8ksC6dkKhTR14O1lJDZLseLWEZauvuTMrRDuBxxwiOwjReOjsQrHuKPTJNxrelAlQ3zzKBoF2qMxs3gw8Dnz4TXTan42+k'
        b'M4PYhy/NA4buM0bmI2Z3rhLhm+gsYmxC5oKyAJv1082pO7rkzWDjNS3B6q8Dey9whTFziyQXrLOZTtq4FUsg2V+7Q8pY1eML81jyeHa3BATKR80vKfFFpsS3RPjarr3M'
        b'FK5ko0pgoke3zAWDGeupA4Mg9SCSyBMEi/YyXOTzxwdiGwBR51iOa3IQKmS4ieS4JL0/na2iiAEi8q1VxH2dAkg00n21M3EuiyDa3IHEl7J5sNlaIXPzM1cp0iAtIuIo'
        b'wY81vALhIvF16Qt9CrCYim6DC6N86tctUBhwl4oPQdV5AUxpizfg0wp8LRtVmesd4KDoXFjjZtSksNyL281VhQBUw8LiYfCH9Yp8cN8FhN95iBVgJZ0UGbhM9yFyacVD'
        b'sWeEPRN3+ECErjOLvmeH2hX5UyVSVs874QRxMYyuPvitH1FLiHsA+A9twq2r16ByTrcZ8qtsgMiE4ar8uYp8vF85VKJpwWeoBe6Ed5tHGHS4yrx4Egc+uWqHtAFfY5ED'
        b'dYHJ3FHgrtH4sLmoA4+VGyeRxqP4ATo9ZM8j4OOwLBdV40JPiSGat8LFEMKrgSNq3mKuBo2BrJnKjQ+PoxUkobkalLyTrc+xUFyosJmDDxENuEs8/A1UTH3UTHRoweu8'
        b'3vndsSOcXjNAEXR9FZ2GvG2SFxmEGW7IkOmFy5TkTRYkySymWDnR1Ux0nzNymOVJdDnbJRtgHeK5UFcJKtmZRnVSh+/iE/Tpw+jcEK7mV58VNdA1sRjVoHoGngsg/6Oh'
        b's8jt5UFcYhZVJJaBRV2hjoVUB3YQlbjj87JnYfY3U4TvoWoVdWuoaDTweMV9ECfUhE+OmJ9qCbiKzhkqGdX6sfgG7lbYJKEbJBjeh/iE7+qpCeUHbVfgq2GomrfF5mAh'
        b'D+pna6ABnbMkb3SDa3XDV2lLFr46SiHHN9OFbO3OAZ5kVVrPoCSFEQz4El/hPqFX85U8XBOs0KPuPeYa3yZ8i5WkAdkp9LhkHW+mp6zxYbaXgDpHEx++dBRRqnvgaZLR'
        b'NWM4tMTiJgCRxeAOTHx9D12CUa+GtB7mA5loUVCMOpeh4hRuxVopblybrWLFW7x/2oTlo3Fx3GJcIuJE+D64/wDUQit9Ae6oJRYXxUkTp3LCdYLg1dNpqRGX4YszY3FZ'
        b'MC71V5EdMqtk1G4ncsZnVjAE0JCOG60T/RMCo8WceJ4AXVAuTiPbReYP2dGhm00GuByTmvc/T3AmAd3/Epo4ugcmMiky5HT3SyzkCqVDu18SuvslHrb7JRm2zyXeI+F3'
        b'v166O3z36/NBWClL5bBPJNm31SvV2XTDVpmRo1Pmq7O06VrD9qARD44gYth2sd/mnGxDDt369TNvFiu1wC1frc1Sb8jSBFCGizS6LXwHevLeCFYb1NmblWk56Rq6eUy4'
        b'Un564xbzprQ6LS3HmG1QZhu3bNDolGod/4gmXanWj+C1VZOVFWQ54taMXLVOvUWphW5mKJdlsn1psmG9YYhL0Ote2KBNm0GGuVGbr8kOYG8RAefHRI6QQJv9yojIJw0m'
        b'RrPNQIagUadlKnPgId1rO6Jj020f3pnBLCZM5b/ej4Fs0fPcgpTxRr2BjJHM+9LEwLBJU6YoI+KSoiOUoa9hkq55rWx6Ta6aCuZHvvkpNaAaRrVBQ3f8169fpjNq1q8f'
        b'Ie+rvHn52YxT1eLHolyqzd6YpVFGGXU5yiT19i2abINeGaHTqF+SRacxGHXZ+hlDPSpzsoeUNADuLlRn6eltMslbtfqXBjNix1fCvbzja5+wkNnvwUB8Wp8nMaIyvpLm'
        b'MYtu5s7IcuNCsv6nBbd+/RvXlyzlqIPLwxDBUTFxaQfVq7hVa/Adth2caMk5yfYIOLv1WWV7dWw72MfVlhvl9p2EC1lvpUgfzXZdpegQLtMrhPg+us/XgSLwMZUt9UEr'
        b'yF6tQshF8S0zglh5GzzeXf1WETqBb3Jst3EsOkTd5HzU4au3BblK2Cs1gCFu0Zc8HUDWTmsxZPl3mDdunAOIkox57i5wujrJLmcGT2pwM787AMji0DRFrggXo2MsbT4x'
        b'x5lN0wVcuEaRJ3JFhQy614UZ6CtvoBuLULGVAN/Ep9ge5Th0lgqQDpnDXdypl05HFSyxqYpDF1hCVwsh7aYeXxOQeM0KWeU5tnzJ1RVSmE6jKJqv9RzdyO9s4ipcthJQ'
        b'rGQbqmVh5FQEbqLiOePGPMVWEUDrQyyKnXK0o9wmewDm6tRJtmAyoDqSmR6YSF9Zh+9a67daoKosVvkrV6NaHjviKnRBv1WI6rbzNTYNrlGJKL+IxbgWmvABdJBvmwgw'
        b'iLTMSYOph55WotN8T+jiJtqSAVCgGboKRZf5rlDNWDZFclSmx51iNT7Jlx9xO25QCdlwD/lOJo24iC4gba2aSZtW6HCjHpVwueg8y9tP4kZ8jCqdaIIFZ2UHoEi5PuD9'
        b'BCnHAOkRJ1wYFiJOBhCKqrkNuAYVavsmTRfobSHqf+n2w+7K2AQcYnfknfz/SPAQzm8/GRj9pnz9O94rU7IWrfVxUKzYpNpkG/LpOJvK2ND8qiI/25xZbgdPfffDr/4w'
        b'8S+SLs8bK7L8JQf7DM9/fu2bMe0b3X/5wYOiMvfQ03V/Orf3/X1rD0ce2fKraK+pLWpfrWHzo+AWn5S9QeEd6l/2L9oQ3B3x8aH02GnerVfcN/q/U3jh01ubkpsNF39Y'
        b'U//QrW5th0LdOPHxDwfuOXyTXXTsg4cPPgjdi9+NmF1+5WigwHn8gtQnaX+x2a3/8DuH/zjju+w709+2f7lo2vXp9Q+OWTvr/3inPzS14u63o8ctsztu98fWqobTFh91'
        b'GtbOPTzmufp/f5H0Z8Hd5I4D9wbeOrHqrQTNH+ZKipOT3ndQWTyjKqVW+Qf6RgcKOTd8TopOCgP3rH1GjjKh6zLU4B8Uk28R4KcKwuUBGEzCTSleh9tQAXviFL6cEZsY'
        b'iAoT0U1UR0AFp0gWApRoQfXP3AnoygQYXowL/QKDBGAyuF6KDgjD0G3/Z6Q+EQW6c4sc1KHHd7ayQzf5gX64KFjIBenBddyTgFmXznlGjClXiVpxcXxADAYPFqWRhgtt'
        b'AFPefkb2OXHlFrQf0Et0Zh6wQMCQQR9nfEiEu8H46lSKAaGvSkec20+66MkhGqVyn/nzvfOsDF3ODk22MoMdIwsiwXfOgCUNBamE2DHsu5CwqATl+3Yf9zRJwjm59buO'
        b'6nd0PTGjckb1LNOCx7YO/S7uJ7SV2urNFaLHjqObfM4FNwd3+DwcO3VQKHYe3+85/pFnYK9nYFt6n2dYh/7m9qvb33R4c2nf1JgPPWP6x/kOirhRiwVPZZzHuKawNouH'
        b'7iH9nsrHrl79Xt5N3k0RNZkVix7buvR7eDcG1gbWBVdYkN7nVs5tCn/o6Nvv6jXICSYmCZ5yArckwWdjfPqd3U+kVqY2LXvo7AetPROm9LpO6X/lftPmXtdJ5Lb76MYx'
        b'tWPaXB+6TyL9OrrWLGqb0ztqOiHsnWt8anRNghrftqBej2lk5C4eNaE1ERWZpkX9ti412l7bieSu0+iajb1OEx45BfQ6BbQt63MKNUU9diRT9djWvd/V+5FrQK8raXAN'
        b'7bEL/czJrca+xqEiumYrvNTm1KbuELS59zqFVggeu/q22fe5+rcZel3DeuzCvh2MEnCjJjzynNzrOfkrDizp8RifQRH8/V5vD0tzx2fBFO5nU2yjZKK3LQRw1QE+51RW'
        b'A2KyeAMiwEkDFjzqGBATmDBgkZqqM2anpg4oUlPTsjTqbGMu3PnHOmQFl/XwMeuRjhiejp7rGKYrx8mjZJPyh33cc61YIJjwjIPL5zauxZv3KQaFEoHTY4VD8fTPxbaH'
        b'4vtlto9ljt8+lXASOzP1vZ54xjqpP3dRMUUEnpycEcA3N6MrqEUcCwaBixNwWWKMhLPJFU1DzbZGaqOoGzfExiUw7C/gFGO2rBbiy3t2UZca5o8KaLqgw+dpvhCFb6eZ'
        b'z3WSj9gMOTIJ7hcy3E9RPweYX5ohplhfBFh/CLnvFlOsLxqG9cXDUL1oj5jH+i/dHcL6mYD1+wUvY316MnMY2NflbFGqzfB8JBAfCbpfAtXL/gH212nyjFodQ3y5Gh3g'
        b'/y0MmpqPi44EZ4lmzAaC+C2BHrVbNFE6XY7OjzJTQ0v66yE9kZeIy2D9y4N4LZ7lB8XeeHmEr+uCJAELs9QblVqWiqTl6HQafW5OdjpgV5oL6DNzjFnpBNsymEqTEj4R'
        b'eT2KjdKSIb8AzZAgqZWhgQZjLoBhHhrTWQNM70ueCCAdqX4SppUkGGcTzT6MqkLNxzbZmc2V6Bg7tlkY57c4AF1Yxk5wkhuJcTHxAnIgplAxfTZuXaYdV/E/hPrFwGfz'
        b'x5vq3gttaK6+UXPnUKXAconbisjH8SUN7avet3Jrqr7Va12tOqydvGzCkcL9zcebj1+tPmM6c6T5yKRSVU3zEe+a/WHWXPA2q9tWt1XCZ94Ed+IH4Qo/MCZcOBbiX0m8'
        b'kY9pYxDAnCs7pzxTEvG7LVFJbNBiiGio1BywICR6oOvi7BxUqJL+E68iHYpM1J8MKNjZZBaDhhM0CM3lWBBaaME5eT1xGdszbn6fS2SPXWS/+7hH7sG97sEdsu6Jb4b3'
        b'uUcXLjYtqPAhocnVs2ZZxY4eO28IGqbYr8lyMA9pMSAza+iABa9rOhKldR7k4jlSUgvm/4iwzPWRWRoh4iPyGKl6/AV832apQODzU93eMel47owiRGScCYTvIvUrlZPz'
        b'+BjkJHeS0TVUgpoCRGtjw1FZHrqEzqJ7loAVq6xxgwg10vznDSe1It9GsGYNJ4A0BF9EJXNYHbZULFfk5wkmT4YGE0DSZTv5g2Jb8fmYGXrcZRsq5oS4SuAyZxmFsONB'
        b'40r1oTohKtrFCXI4dBNXoC4GfI/b48uK/HxpIGQhAnyYwyfxvmxw2xSdX3XB56jjXQgZAHG8+CCqprXN3L0BIwo1tthkJ3IWL2dMjwD/ff7gzQX4lh8nRGWCyLRVIzy2'
        b'zGxQudyLSg14bInJXKuRg+e2zJANeW7pv81zkyrNX3+sSkNdzsgazY/6LeLjyOP/vNbxIyUI8vJ/ewUiLYuKpdcYXq05vCQgmZectDQjuOjstFcFNVcdopIilJEAS3TE'
        b'hS+AUJVmyNFtD1DmGjdkafWZwGjDdvokH1IiNTAeddYr/OaDdQcNk01NFsVIf0rhtzRymV8A/FmwgPyJTFwyCf6CeH7zQ+fThshIv4BXOA4bkzpLn/Pa2gkZJJ3nXFYx'
        b'Aa7pJJpsz31pAsnnX4rTQxxzcl8Nz+Tzr4XoEYv3by3ZDOGnofBmm7DQOJf6B1zuOzK+vRrc0ElU+mqAw2dxMU2Tv1W6cyHk/P4eb8tNSZGsYCMIdeTInnWI17sr3lyi'
        b'5mhNBtchk7dhFi36rOJWJaDTbLOoDl23R8XIhEwcasJnOKGjQI72Z1FGO21suFHkrPDyRfE/aGdykNGTU6N4Pzog9YshO0GTuEkh0fQmqp2BmiLSyenXUC50lTdlYDHN'
        b'noNYOC3E5bT2zVSNmYEO3VWgqhCegdM4dhyqG9U5zt+LOyGaJHFJqAWfZj9mmGXJQVCRhSz/dvVy6xBumTb0+HqJ/h1oefA8fHfSJBsUYmWoP6v1lRVKeuVy6Z43Xb+d'
        b'/9zK99MPL5xxCMjKWDSrpdHHOlDm/OX42zMbf/V09g5O/cGmhZluVhe++LVn1XULh+1vDK7r6zeU+S+dh0zNjb+e7TqvaZ9PlPV9tztzDibPnfXhz/4+9Yvff9dQW1uq'
        b'6ZodNPmHkJMbZ56ot/ty/UcbPn+K/rpnTv1pfCX84Yc7Wxx0X1R8lbnkwJaU7BNlxTfi9n3bH9g5e9ui2Z/Os//mS5eAjRVPb8//pd+0p05+Z8sSj30X9MO6PpXsGXHt'
        b'0xLRWUjVs9EVkq3TVB1ds6D5rxZX4RYKOVQiXPgK4sAHZj8jezAZY3EFCQ2QsEPW3gnaUxgMjwWSV2ItuEm4SRqDHqC2Z2PIghXi6zaKWHwfd+MS1RBHZ1QglqFmHS0e'
        b'4HoZqolNDBTEoQJOmC+ICEaHnxG1GYc6hSTxD8YH8IlEIu4eoV8g3s8yeVwURTJ5h200l6eZ/D7I5Ok+xDGjHepGDbG4NHao6mAbItrob6GS/7TMnexIDCXuDCLJWbYF'
        b'EWTHi68UHn3Kw6NdAI9cSU7q4HxCVamq9jdFAhB67Or9xGNCz8SFfR6LepwWDQpF9t79Xr6PvKb1ek3rduzzml2x6KkUgFVNWlPYQ8eJ/Z5jG2fWzmzSn9vevL1150PP'
        b'MMiVP3P0euTo0+vo07T0oaOKJrcOFWHF22pCi/Y0jWtSN09oi2wJ7BY9sLpl9WbKw2mxRAx4ZFJhfo17r+3YprQ27+aMDnnvhOn0ZZeasJq8JvuaaU1bz+1u3t2690PP'
        b'Kay68O2z0ZzbWMh37b0feyoh37X3ZvnuGfv5czk0Vx6pEGFLAVwZmlMw6EYWbkAEQel1IO5HiyOv5LXkTMew6f0Tx6e1BNqtshAIxnwNae2Yn4rvaqUq7rwiXKQSsKNB'
        b'uGt3CviAEXtcqMR2xK+yhnzreo7lpvRXWeIM4dCvr0T/tl9fbVQJv/9ghJtfwsLEj6RWGTQzooBk+BbSf3cu+qNxSvRKnJKyNCwZ7UcHfyxMAeK+++N5WLwNK7qTbc5L'
        b'q6fq88ynfEPGsS3m9qW4A9wLLorHJUuxyZAXJ3SIQufRYXQG1cIXFZdkZ4G6IuTaTMvtAprNuf/yXN17Ve7hkM9dHZnPWZF8bv3ko3/awL3XueG9cyFvxXEnf2HjqlkY'
        b'emJSsePS1ImiuCjwNB5c6xXrb58GqSTPSJTUoNPYBL61C3XTlO5V73pv6TOSBFgtRB18KXU9ekD985gI6tTi0L15/kExrI6KD+4eKqUaRtNCaqh2Hjha5mRd0L4XfhZf'
        b'QCXP6C89zqKjG1mp1VxmDUO14MmLcLlKOMwiiTMzezuLjRoD9XXmL9TTxfCebo/s5UTwRVlyeI3wiYuyx3tqn8u0Hrtp/Y6jHzmO73Uc35Te5+jfY+WvI9GHORGJjgSp'
        b'1+Z/JIVf/yL7m0EchFkmNwGf+X23j/vzFplA4PATPMPXxDNUSr25ZkWA6J+avtjE/T8x/Uww/QsjLGdpbpbWoB+yb7Z9CEasJHczdOqNdDvwJVs3+wu1Mvy19ZIRD/tG'
        b'JqYkLFuyKkAZGR0VGbs0JT5ACb3EpkYmLogKUEZE0vbUhJT4+VFLVD/NrCmsWiex8LkpciMbLFbLRo/l2E9lr43eSH6G609+EVsYlxzN8lDfWJKJ4ioVOm+JarfDfzGo'
        b'cDuHGqSWyGTEpfSEJD68Kn7YuwZ0AfwB895euE2MWlbhOu2WsRUS/Vp4WvbV7+veI0Y8vbhSIGo/8uHa9xveV1mpSpZY3bCabNUQpymJejL+/ZAUVdzF5h11bjNrN7n5'
        b'7G8PWB7XN6NW/eWmn/e7b3Yrroxfv7AmCde8XfbJ+Les6t25j39m/5dOJ5WYAip0fGYeGCw67DgEqOLQ1WdeRNhbC/D+IZtkBrkXtRObzMQtFMXI0YGJBMXkCF+gmDZc'
        b'S/c98Dl0NiPWF1VSeOUr5eRuQtSMLjurxK+No2Tyh+xjwBKyQz1fxxn2nVpvKrPewXVyzsltyFxfLatTq53b5zKvx27ej9XX4Zkmrz6XkB67kH5HtxOzKmdVz+mx8v6/'
        b'smnyi9LhwvoON+t4+U8zax2p4UCgJ4LsRPvXsCgPQaI8GBWhwmXMB3rsFWfiW+js6+0+ndi92Bzyyc+w+VL0v9f2SUFj7cul6OGRn9Zss9VbaOr8moBPEmdySCBXAzcA'
        b'GIwMwTHMA2SpDQbIg9PUEL1HMqU4QJ3Oqt2vVABG8BqqBvyzYgBL/v//ASIyBkRQhRKf+Wf5shmESHDDCxwyEd2nPq9uuVv6NMF6gmlHOSVP5+gmfgZkQKcZNDmKayk8'
        b'QXW4kJ0MvoVK0Z1hCOVVfJIRSBBKNKqgPVhFSMPLhdSrZv1uZzanLc2yF+jJP48x9ptKVoU+Pwy1eEbEl8RZNbzfkLvHcmmXkyiycv3EpS5hIum8NoX0WufKSSnEM5bM'
        b'254f951TRo183vNcFLUq6Qk+8J9ey2OUqxSGvS5Tz2onW8me52ZwnFOfizH/rErK9kzr41AdX6ammCZ583BUMw/df0aOEKKm5YYXOaNpPvylO0m4DLxjvISbmiDdk4zP'
        b'UgS02C+CB0AL8CXqT8PwOYpwwDNeRkVDGIgBIP+xAIH80X6abuIGdED6ksedhVsoCupCN5+RXwCiuuWojKEgXgb0AF9jcoxBVWLcMAF1gNP60XyFOK1hFXMrikFA2Ykp'
        b'7RhBUWe7k+Nr5pYvQSWSuc3ssx3TFPqh7Xi6QRna6xraMbPPdW6P3dzPvFSPvIJ7vYL7vCZVKPpdxz5yDex1DWxLf+ga9sTDp2f8zD6PWT1Osx57jm/a3OcZ2jGp13Ny'
        b'hYzyCep1DWrb1udK0NYwR2wxoCBeNTVHRzDTP87PWLl92M6ALp445xHDmzHMPT/PA/fs/lPzsWrpOK5VESRSiRISFqoEC1XChIXaTcLzIn0JzF3kr5sPP3y+tG+9m8Xg'
        b'1C+atKu/8TMpnnv5/ml/m2ln8YGvN1f+5pBf0hqL5XVO9c55n83/Q/B/jfniZnD8f63duXHH85hfz/rt7g9/oWkJP/v2k0mzf1e4feLbK2snLFN/XHNGFfWuaPHei3YH'
        b't4Rtbf5+W7Br589XKtKsl1t980NJnNhm8/jOugOPj9lJ/lrvbREo11xe6x2V8e6e2vcEszM7/ZpXTW4tOv4Hx+D/cu45d6zb1WtbctE11ZoFz+RHW8c2NzmkXPeYfN3F'
        b'eN1rzsC+hTMU8YYpv+u5VbPo9621QW/Ovy0r/sIh4MwvOuovv7n4tuXFLzza432fbGz4402vQINoyofLs1rqwvKy3lp+2/qTL2z+ePpOR13Xz/+X1/W+e/2Lnrce9Jo3'
        b'cbbv17afh8w+0CofX/v4C7cy/W7hxC9U9Wc35h4/Fek6u1xx3XP2s5b6H6p2/foXoTskK76YPN06t+H73ticpnJpT2LOb5bnn/ukG/957ZNWkdvpiCfnbEMWFEyaH7kt'
        b'Gn81Y2xrefo772yb37jh6JzIo3PeUXhU/73B+9zUsBsxkjk/m3Qk7+7P/O/+h+fdBt34Y93ZX+53SM49fe33+b193gtu+i1YUNimftr45HbW5cANthcFl0KmZik+Wfrl'
        b'+8YFo58/lvz68EcVYZ2hfxDtqLT8aIdj/Oz2rN9uv9sX9P6M+985n038m19f4dHZf/n136a8Z32z2fOjhZc+//PMp3MurPp61e9N467cDp1d+d79P0df6xq48pvISo+N'
        b'T78I0ca7Pvrqzm/Gzfk87P769/533N5f/tfgOz3di5zPXZy0q/5Paz5PyLv50cS/fvplQ8MfFj1MCVkR05vV8HiuovO3p974xrAnJ+G3Tz95ejF67yNTpsvi383sczP8'
        b'Z8umUwNbUv7+l8VWn9z+WUVL1N+Ff/3I9e2OKvB3dI/mJOqeB0gCl4sEnGAaOfF605JVuq7jw/jScN/jiJr4DCwIVT4bx7F/KmQR9Zaz0c3XJIGoNoNiSntcrMLFATG4'
        b'NFDKSddJ8WnhuInjWQ5XLkOt/osDsSkmLkHCKRaiLnRVCH6vFXVR0JmPGvGpWBK/4BlcEgPP4AOB6IoQX5iJq1WjftrpFdmPXX7yGZjXOhkyoqEAPY989o34MA8rS03N'
        b'ylGnp6buGPpGPauLlOP+CjB2oYCzdh4UW8hdiUsNLd5a4120q1bfFNqkbp5ct6Mt+eTeqz4dum7vq8bu5KvbOoPeWvCuA47+MDTuiRvBvOrayXXypsW9bkEdrr1u03pm'
        b'JfS6JvQsWdaTsrx3yYoPXVcQjOtQnd1j5zMo4txWCgYtOQeniohKZ9P8r6RSD0uTzaAT5+Deb+/Wb+/51ELsbmmyHrSJFzhb9lvZ9TiMHxSR759Z2VUED0rI10EpZ20P'
        b'hAUlZIyQU8KSEQpKWAHR4+A7aE0pG0r5DNpSyo5vs6eUA3vNkRJOtClw0JlSLpQaP+hKKTf2oDslPBjhSYlR/HOjKeXFU2MopWQPelNiLJPj6ThK+bCm8ZSYQJtUgxMp'
        b'5cvLoaKUHy++P6UCeCqQUkH8e8GUCuHbJlEqlHUQRolwRkymxBT+uamUmsZLPJ1SM9iDMykxixGzKTGHl2oupeYJeCYRAkrPF/BsIhm9gKe/imL0QgEv6iJGR5vpGEYv'
        b'Nr8fy+g4Aes7npEJPJnIyCSeTGbkEp5cyshlPJnCyOU8uYKRK3lyFSNX8+QaRr5hlmsto9fxzamMXG8WU83oDWY6jdHp5tc1jM4wT8NGRmcyetKgltGbePabGZllntUt'
        b'jM7mm3MYmcuTeYzU8aSekQZz30ZG5/PNWxm5jSe3M3KHWfKdjN7FN+9m5B4Bv9x7GT1PyD8eIWTrLeQljWT0AnN7FKMXCs3rzehonn4aw+jFQs5xbL/D+H4HFb16m/8/'
        b'/qtV9AmTfPANIefp0xhcG/yxh3/hYlNkhXO/2/hHbv69bv4fuwVWiisEFZP63UY3WtdaN6nb7Pvc/Csl4Gncgz5zCupw7nWaYorqHz2mcXXt6jZJ3+ggU0xFWlHCoJzz'
        b'DACfYGn3WG5XkVajb4vsSH8on/lcOFse/pSDy9ciznIWudgNioEkU0EfrhnXpO8QP5RP/rPQXu5GHpjCPwUkmLCr+4lNlZt6vJf1uaSYFJ/JbUkHS5vGtS3ocO4wdi9/'
        b'M+rd8T3+SQ/lyc+FE+RuT7kJjMsSAc8GaKLZvGQP5R7PhFbyANLoyT8BJPib4Q/YyMcOfwBIcDpM3KUP5d7fCB3k00kbfcruqRjIbwfTZAJ5jOCxw5jTVj2BC/uUi/oc'
        b'onusor+nh+UKI9xivLmfezvGhPNbFHYDwtTUf3Vf4l+JX3YvQPLImKVLIWh5KFyR4K+fwyPlSIFAYPecg8tTcvmpmLlBGshdUkwTaX1+dVWs/xncWXb8fp3fJx88/ODJ'
        b'B6EN3ocnHfYuaD7efMS7uFYgOtrx5sqL7t6GwDTrNJeZZ99zmuBzI87upP2GGbGusZaRY/0nHnrn47ef/Lz+7XIt2uTb8K7l9Qi74jXdPZ+id7nwGLfiNTXJy0y/6bq4'
        b'UpZ5YpqL40q7CbmhhhBjR36HMdcgyw/ZKjOa8qPzOwzvGt41vnvu6dmOG7mGScZQSZhv2NHoN59dDHEqFOz+Vc/bJZ8Gq9plX49z7yraYfULd7+ace7vuU8P47zL/B7m'
        b'/01lTVO8HHTHhv4zf+7obiIupzuKCnRNCKnfjd2sqFaOzgeSZPkqKkNX4MlEsjNoj++KUPMyPwbFruDj+DoqRuW4PHYNugU4CzLscgvOxkHkJdAzIHdHi+/HxsT7WXvG'
        b'W3BSsVC2B594RvewazPS/BdLuCiNIJbDNTa48BnZjMKVe9EBvjCAGtHVoeIAKguOBRRXBrlkuYhbhK5aoHJUZEslScCVe/h3dmUNvSHlXBeI/fJwCz3oJd+LD9F0dDgb'
        b'T1Qnlk9DZ1EdPkaLgagZ3UTkGHRJLC72CbDgxIECdGkFLmOTclVBhFMBF3R9FMxbYSLEHdtkUQpAThPdgbBeiS6xJyBzJjJDRyZaRBVwSnxDwqkghyZWMdN2i39iAOoA'
        b'LkW0P1gBfF+Ib9oZ6JGzSagLN5KfFQO+DPbL4wGsh1G8FpegI3bWqrE/jh//Lajx33jRj6UA9BXc+dJnCIZqs7UGBkPZNwpD73N0W/JrD07i2G/t9Mjaq9faq35bn7Xv'
        b'voX9YsuCuP1xPfbep6c9FAd8IrYG6Ofh1SN2GRRaSlYLPpG5A+Lz8n00Oqx3dFjf6Mk9Mo9+mU25olDx0GnCQ9nEfpnDI5lnr8yzJuKhzKvf1v2R7YRe2wkPbX37rRzK'
        b'EwoTejxXfmS16rl0s1gy/TlHroPsulrOWTntS/z2WR58cf2KE0pC+p3dTZY8+x6noI9lAEfhNn+MWTzfj0N+oyLlIiwTwJX5zDEDoixN9oCYHJ8ZkNAthQFxllZvGBCn'
        b'a9PgmpMLzSK9QTcg2bDdoNEPiDfk5GQNiLTZhgFJBvg/+KNTZ2+Et7XZuUbDgCgtUzcgytGlD0gztFkGDRBb1LkDoh3a3AGJWp+m1Q6IMjXb4BFgb6nVa7P1BnV2mmZA'
        b'SkuOafSsoCbXoB+w35KTPn1qKtslTtdu1BoGFPpMbYYhVUNKgQPWxuy0TLU2W5OeqtmWNiBPTdVrDOSo9YDUmG3Ua9JfxAI9Mdf1/+ijVDLPnm6+kH+uUp8Il7///e/k'
        b'tLW9QJApIn595HWQXn+KlyfB6y0LaYQr95arImKs6HuZ+WcCA3apqfx3PrJ875Ex8l+iVWbnGJSkTZOeoJKRk+bpOWkwYviizsqC8JfO6zKp4MB9S5hcnUG/VWvIHJBm'
        b'5aSps/QDVsMLqrqDHF9AYqUkZguz2L90O0dHjvqQ2jndEhwUQWx7KhQLxJC6KKz3WXwlXQgDHlxiycnteT1eDFrdEzDnrQnYtzdgcb/M7rGlS49rWJ9leI84/DFnV+H2'
        b'EedBu/o/9a8F0g=='
    ))))
