
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
        b'eJzNfAlc1Nf1729WBoZ9XwQHBGTYF3HfEBeQzYWJQQ0wwiCjCDiLuESjxIUdXBAQRXAFFVlV3JN70/7bpE2hpAFpmiZNm6RN2mJia5q0zTv33t8gqGmb9/re580n+THn'
        b'd+8999zlnPM9597xI27cR8T//XI7PGq51ZyOC+N0gtUCd04nXC9aZc4981ktjBawbwH8G7Uc3orWS3y4aP7NHPg/G9rGCtdLfbjVYlMLjWC9mQ+3foyDgtsoMc9RSr/O'
        b'sYhfFJOs2FKQbczTKApyFIZcjWLFDkNuQb5iqTbfoMnKVRSqszarN2pCLSxSc7V6U91sTY42X6NX5Bjzswzagny9wlCgyMrVZG1WqPOzFVk6jdqgURDu+lCLrEnjBuIJ'
        b'/8vJ2N+GRzqXLkgXpovSxemSdGm6Wbos3TzdIl2ebplulW6dbpNum26Xbp/ukO6Y7pTunO6S7prulu6e7pE+qZZTeahcVPYqmcpMZaUSq2xUFioHlaXKXOWk4lQila3K'
        b'VeWokqisVc4qucpNJVUJVQKVu2qSym6aJ5npTbJ8z1SPJ7OX7+XFqTyf0CqvJ98VXIxnjJcv5/2ctzncPNFkLkcAMypMzhq/ZlbwvwMZqpgu80ZOaZ6cJ4Pv0c4izhBG'
        b'ijMTb0+VcUZ/+Ipu4YowXI5LUxJX4hJ8CF/FlSlKXBmvWhEi5aYuEeP7qegybf9IIOVcF3mABJmWHr4FnDGdtD+I6rJxj7nVyjjgUhGvikPtAbgkeHkSPrwan0QdMlwa'
        b'pwLOVbg6CHrBVXFJuOqFgLhEXJWcmKIKgIKSMOhvZdxyVUBIXHywAF0ScwZU6jT9hVnGaaSLns3ewHsiA+BYHrYyLjgBV0CvibgsXsLt0G5D1ebrcTu+kyUYNyPWphnZ'
        b'CY/5VukwK3SxxLBQUlhIGSyfBSyXJSyptcpmmjW/UIJU8biFEsJCCcYtlHDCkghihHShnnk7tlD7n14o+TML1cYW6miGGWfJcds/V2Zatr8SwtGXcjshBxULB6wzE1/Y'
        b'vZC9lPiac7bwd4c2M7F/+zL2smCymCN//5GSGbwgJJ1r4/IsgLxV6CruT/qTH8d9OPUL4fWI7lnZgjyi82+GNAg6zThFszIn8r3Il31/xtHXny370uaYjSDAVvWx4J+u'
        b'lw3zuRHOGAoF3gtxF6wHTH9AAC4LiwvBZagtNQBWvDo4ND4EFaODy5MEXL6N+Tx0PVIZZnSCRhFQqVFvKfBYyHG4nkPH0UV0z+gIJRvRq+v1OgmqdoaScg6VSFETLUBn'
        b'pq/S68zC9fC+kkNl6C7uNjqTglOe6JIeX+fIdOIaDlXgVlxHuzHb5ahHVWIPvBdKWqAmvoe7jK6k3n0XdBfKhPgAvgfkGQ41oRZ8yUiWAF0O26LfKvHD+6CkGvrKNKfs'
        b'cNdaVKPHXdK0CCBqOVSDjqQb7aHEH5U76Y2Swnh4f5hD5V6BtAE6g4/gRr2VNMcABac51CDGF2kX+ISySI97xLuS4XsdcEraxkZ5Yt12PargwnfB+5NASlA9LYiUolq9'
        b'XIivJ0BBM3DCVzjax8v4LK7QF4k2orNQcpxDVfjudtpHjjk6pLfhlqFLrEn9OnvaQiRW4R4rMarZAO/bOXQaHUDHaCe42X6eHCb//hb4fhlaLMXtRhdScAnvtUbllgK0'
        b'H/dxAhmHruLbuJFOJeqEYXbocbcgFyTm8BEOVaNq3MkaHsAl6CzuMYpgJi6wiT42/UXacAtsnINy3CnBd3EFFHWQNWiGhkSUQnwf9eqLhPNWMJZl6N5UutxB+HyKHt8Q'
        b'o0ZEFq6BQ4dRewQd8C5cFqy3EQpwJ+voRIE9W+yrsO6duEcmREfRMaDPcajRHV+l/PDZCNgXPTIJPhEC1EUQAl9U0SIFPrkE9xgkqG0366ka9eHLVLz1nkG4x1KaBruK'
        b'tjnliLqoDD6o6WUoEaxfCwWtwMxBQSdCj3thznpwlxgdJ7vkLGx63B1PmeXgZlswmoIgVEuE5VBLFMfWo0UBTXrMJeHJbH7OZLhQycwmwfT3mItQ8VQo6OTQWdSBmqkA'
        b'M9ehvTDfUqKcZMsdzshi4+zD17fAugtQL2w42uhMvgdbwVOiPaQfATqHLpPFhulBZ1AFFdwH1aHzpNTM04/tlyZ8GZ9h+oWOLIcFFASKmNynUDc+wCTvscUVcpkAHVwG'
        b'xHUOnU+IYCpxLCNTjrvNIhBRrmsghBqXsJKDuDlLvk0iQmdYPw3hfDdT8GHcK8fXxTJYOdBC6CjCigqHyvJyoUCKuujW6yGbuQufpwPOxV3Q03XJYnSF9dSCelA325VH'
        b'8DV8V28Q4FtFQJUQv9WBmQFyxedRr1wvVvizKa9H5wPpxO7Ge2G7WkhDCIObHLqwa5ER3B8nRTdWovLpuAZdQxUSToTP4Cv4iiAF9QbS8gx8SY7Kt+FjqBKVSThxLizd'
        b'fQHahy5ZG70JrxK8bxFfIZLngu5GcuaoUuiCb+BepYhZn6P4hCMuF+FGmGqugCvAF9B9ox2ZhSZbXJcgjgCJN3AbVDB+4gUKoEKCFB8QAiDjsndtpSMPwR3oKhl4K1US'
        b'MnLootgIS8u95OIDfZSgy7rJ01GbRJ2EKvG5TbHo7NokbppegmrxAXSKirJ7Gz6rB73owb3ApJRDh1LArinpLgtYz5hMh+1ei4/Rr9PQZVwr5iZhYGgQm6NifI5tvBbc'
        b'hk6CaghQOT7GrHeVB9iVIDoqdAGfYMzQddRKuMWhq2PMwAHcRnfEItQmpAs3c4MXeBTcQzWc+JRI1GkMJIza1iaaZGofJ9MVJhPsBfARUrCo95minMFtdmCDhajKF6gm'
        b'Dp0MgxminMpRTxQ+GoeuwASNcYoksgGnEFSGD4hAz6rxIbbNbqNWdFavE4P4+4E8xKH9qFtLkdZKXLp5bKLoXK91QXc2yRW4HLW+4MAtV5jJw/fQjTd/Gd5PXGK7Ne8S'
        b'i3yNwfD+hT0whKfnOls9HbZyJXl3iUgVopNsRYecmIZ1rMGHwId6oGLeiQrxESPZzxrcEEjHhRp3kaFVijaARCAP2O4TsAlQOeyBONwnxddmTGEWCN1DLWD0ObSXOMMq'
        b'mBvcHEOHBktQCUvMTxM6uNa0cuJVnAfuEYEpvoCq6dBm47Lpegvhrt1syWpRjcg4E96H4mZcM27pK59eu9YkwvxKkqWDdEMStxWAJbqJT8cwRWncYKFHZWK8D99gNvDk'
        b'KqkxjAwTrOQdItjVsfUTEe97BJfiWnQwB3TvBGCT0xJUBRb1DvPIPfZLCLoIEpvQxf5NdJjrXRMm7Cq2Ny+xvXnUBd0S4TvTZ1KJ5kLFc3prYTYiLvAEwTun0ukmF+A6'
        b'ItGzCtPGNuchgFYtYjN8BPUxsFM23Y5AGvCrTTymyUQNFIgl4JsiXAa8xrhVPiUb1ZtpuySoYYeBbYh7fqiboCDUGMeDIE2yMYpp5lWY9xrcYWL3ZL8Dn0q2CIRfJK6W'
        b'gNeuWMKU5ybqcwbs5E19DMFOgEf2U9OATuKbkRPV2bSYbKztL3qKZVp0nE67VbieIC1YmFd5rGW+yxhJ3YQnNHxaKNinN4HrFTZmqtmgjhI9voBPMl08UwgwCXeZSSkY'
        b'BGd+DF1C5XQaElC7BNCbO6gEg2+wJNfp8uBbk1GpqbNLpDNwqDN9dpDdgg4q0BnQ1CR81yxycS7zR+AZUQcAPqjcwkM+M7DH1J4dwsUvWUvHRKdKDyqGX10bMJ3NgR6d'
        b'luEKgZbx6gXUcpyARHQC9IvBRL+NVF+XoT6JidFl0xwsdh9TfX4Cjkv0qNXAFmYvOi0FZmZ5qA+oUwR+HPKnUy2D9QNoia758NDyRRh9MMUFuMsJ7OOBsX0+5hRiFfgo'
        b'tVMpuMksNBLV8ui1cC5gNg0dOwFteJ85lbdgMSijyW5SCS9vhRDOtHjX2fBD0W3JpulbGQbvnaXXF0lylWz1K3FVlnEqeX/ED7wIY3XpGQczNdpGhG8vxsfZmDutJQQq'
        b'4tPoGg8V8cUCI0leoJvhW8YbcqYg7YSJB74Oaw6GoQt172BKV6PYCXwE7ugOQ+XH0BHUS0c8BR/bAJATRGnkMWfSUmpqduNX8SV0I/UpbWx7Whu3AsDH9xzY9HWHBelt'
        b'BFri3wlGPemGblPPjJpesRtvtsg3k9cRuW8W4Y4k3MQ0utfHngBdfFjA49xIfIyq307YTWPK3PGs9p0FryA2s8DlVBQxPrKVgOKkCB4TR+E7LPxuWonOMTYA+SaOizIU'
        b'o27LpJjFqN2f0+FaGa7xmm/CXE3xBE3j1iQeTeMWfIMB9C4LDBgccAA+jJrYLjyO7gQafUmPV/0tJ3pKUJpYhYSbhppTEySA+F7Vsem7vygOoLcY3wRYhc/D2HeJqWWM'
        b'R1dRW6xo4gYcb2yp0Y7CjRJ0JGse8yEVYFFOEohvoeMR/pwMZn8ug20sfmKAKsdMA30jguFbbYoWrJSgso1mMwGL32YM78Ti+yQwSMFn+cggQUV1Q2RnTCBy3QegDXr7'
        b'tKZR+LUKVZp5Q0kZnUoL1AgYowdQdDw6zYZ6Atd4UoiyCV2EgHBspODHt+MmnhNx4lHoGng3QPC1VKzoDFfcY22GOtcwtHsWBnedpYKuzl74tIZEspnywF0vLYZNN4+H'
        b'09shgGwGr18lTKUAHUDBBbCUdOu+jG6qn+jAoRXjsMAkVAzKCkbmMtu6xXMgvOrZKkT3rZiaVa+QUmVdhU7jOxNM/ngFQIfE6LYI30pbxgxHa9yLwEVqa83MXE2h2jgF'
        b'3vsCYKk1DUiabOIiJJjkBij7UlzGEhBTN9IwbUEIH6UFA1glVsAFwFsXCdPQvQg+TMNNLFBEd0I2kzCtkPp3EqfBWE/TopWoN51GasdojEtCtWQeK6Nr4J3uPGuFrrI5'
        b'7nwFNcAk4+JtlFE2bjGQuA61z+YDOzBX5Uy1umAaj0ChIB4dYtpzBN/fxDrpXExQIrUdl0x9oF6T8QAjd0iEe0MQy6UYcbcc+EhQXR5DF0chdr5M9z2+iErRqwUwBc9B'
        b'K1fHIc4IfEICMeKp3VS2PYBXYT6vSXHvXKZIDVC41xhOtxhu9FwH5HiObA5axzNcI0E1sHoldH1WrkOvQhgrDIpni9AcC0CNgvNWwzx0KnyiryKmYsxXrUg0m4UrYOfT'
        b'SWv0jKHh8EXUyofDAFYOU+MtQ0dmouLEiQaj/enZi0L3JagaNempXBLUCcGHlQRXWLIY9azYl07cToAE9ygrAL7FJnbCLF46WxCub7odKokWoMaFFslFEGu4EQsM8OQe'
        b'jcrxPVTJR+UAcu5SN7gL12x6JhAx2XIlvhEngrDuDgMSaj+QnQTw+CJuM4Xw7W7U+BRBAHb8GTSlm2sCeTySMEoKXRHTjwXOdhDyS9F5VMF4nYxLogYjS7Tm2b18me3l'
        b'm7g0W4S7cXkSVXUVqokjeQNUM5NPHOALcVTVk+Rgd5+HEfkA8n6RjdgaXbJjBr8C7Vsrl0kXmLMA/9xkdJ1yUTmCZj1ju64wWa4CEK0S4avJuIrZnX3o1g6SqqjR8qmK'
        b'ZegK3VHe4ObPoibfZyDbuC0VbDYDH9hFxUnKwdVygxj6aWNG+eicSGb7D0wyJzkPfDSEz3ngY8Gs7y4IPtvlFlJ5Hp9USIaIjJixaSBlsXybWCyHgjYIjSIMdOE34OPy'
        b'CYB0gj6jQ69YivB9fyfKwxmVBMi3SXGFgaXz6nbL6PZGZ2NVdHpW2D6zHVHPWsBX+zfhs2s53WaIqlzd2BiqYAkOyLdJ8LkwPj0zXUa9axqqnPeMTYCw5i5ZNYk9H1Nd'
        b'AZCJDiGW0DGsEpJ0Di5dwKdzwIk3GCMIsNWDQE/H6vCq60kYyMJadFRiwPshKqK6fBzfC6B5oBo0lge6nUf7SlOvJlkgfFHFZ4EglmphqOMgsL0otxbgNjCZ4KHBhOBi'
        b'1MHM3V10Ox6QYMvzg7Px5q4FMAg+7ETlh0FWmAI66KiSVHoGblyVbI0WrJCZTQ+G4IQY6Th0seDpWHI1Pg7aJ9kAC5LERbpIUIUtKqaK5qfXTsD+/A5g6QzU7bpdLBaC'
        b'i6Ew99XtqO55I2hn6lSGrmSKZZ5r6dZKnm54jklhijcHH8b3RPiuHh3jx4nrPXGT4tno8CnbjY9K0MlYdEwpY2Edvp8ltwZvSLKT9ziodFNJPc8KME6lctwlwGeWMDVs'
        b'QUcUtM1CX3wOSkTpgSS/BLsXH2AukdigbLm5cAvNZ8DyXQRf083jYHzTS24ELEgxO2zXus27aEmyNTor14txT6gpv3cWs2QErl+Cjsj1ZolKtlOaFMksS3UHnwPfX06s'
        b'XpmabA0wNTG4wTidNKpcg25B2VFUwqf4UDvTzFqwesdQCU0MilFPKipXcWtekkIwckCmFNN9W4BaXHB54nLH5bhCxInwPXABWlxBB7cRzGVHAi5LRD2oUsoJ0wVhuNTT'
        b'6A5F6xS4JAFXheHKICU5HrO0dZWLnPBZxKDmHNRjF5Qcgvv2xIk58UIBumSDjmeRYyXThxzo0LOmbfCYLzWdgNZyKgE9ABOqOHoIJlLJp5nzx1/iVOm44y+JF6cadxym'
        b'kkw46BLHSOjx1zNvx46/NiqF6rlCgLKx5LxWr1Dn04NaRU6BTrFNnafN1hp2hFpYxLPj4MDNBfmGAnq0G2g6DFZoodU2tTZPvSFPE0wbLtPotvCM9KSdxQZ1/mZFVkG2'
        b'hh4IE06Uh964xXTQrM7KKjDmGxT5xi0bNDqFWsdX0WQr1HqLIk1eHkgxu1CtU29RaIHdbEVqLjtTJofNG8Zqh5oqbdBmzVaA2Bu12zT5wawm6XxRfOwE7tp8KqECPlkw'
        b'OM12AxFJo87KVRRAgW6MIZVPt2M8U4NJBJiCf83PQI7LeQ6hiiSj3kBkJnO0OiUkKmL6dEVM4oq4GEUk3zBbM9avXlOopp0Gkm+BCg0si1Ft0NBT9szMVJ1Rk5k5QRbG'
        b'g5eHzQ5dSl42xWpt/sY8jWKJUVegWKHesUWTb9ArYnQaNfSp0xiMunz97DHOioL8sY0QDG+XqvP09DWZnCKtHgSdcHwq4Z4+PrVLXspQQrNx7Rpcp98q4TNS+NIcejKa'
        b'NtuNC89LM+MyMycdjMnlaNY8YBHqQOXwxWZLGpf2UjCtKXK34Bxla4WcbWbwqrjt7GD1XUcbblKAWMSFZ1q6rnZkp3H4QjYqXYIO6OVCPpnijw8pbZhNKkE3Ic5OfFIW'
        b'gCqpiPFgXffOi9IXkXMUcoQXwGet0DkXiOe60D69Dcfa1KMqxLIbRWDjANclkbM8ZuJO4y4Z7ckH1+WDIaqU6yTM89fj3vWUoQDwfC8qxmfkhSIWhtbhG+gUM6dn0YHZ'
        b'4Eob5VtFDBE34lZ3ahqnSBe/HEzO//izv+P4IHO8NyYtwecx4FS9lAUMRyD6rGHDvQno5sJqP3IyyNJB1XNeYq0qyekVvp5MzgVZ2uTYNtzBcjYX/dE5dDCanAsyA920'
        b'B52nDD1xyU4HfFtOZ+k6OR+oxExyu1iYoyMI4ms64EaI+qToKBvUJXxhI741SV9kxlJo1RArXWJr1YRrN+JOVKMvEvL5qojJShE738NHVqbaPSnAB3AXlR1ABz6PDhJo'
        b'PtYXPsIOVgtwnQbfR83j+qpJYVKcxF2eqbEkmccn8qDsrJIdXETPCZxfNK4I3OdFBlAO4xJ8fDLsJoK12XkwzHU33X5+s6Sc5XqVkFNkBq+Nd+KYC7uDKsFhhEeFAzN0'
        b'lNuQu0Db+clHYr0ClkCa9OXuVV2rcLhlrcNbyWuFQ6XtB7xE8qzjOkPOR6GrFiiK7qKfe3ncfx19u+Fa12flR7eXBt99/IXvjnX/FDRu7Dt5V/hVap675Mdtt/88UPjx'
        b'wz/O4DYe/bRiy8ICz5FpO8ouXPnTNOG7koTMX2aW5Xw08Kdfb1sYMvWljXXbv/yo9+2Xdr+39d42y6UZnxkrP6w6kxi3FNt1/O2vQ7/b2r1u0u9/5v8Pp5DgM0t+cNni'
        b'n7n711UVbrS74fXh28v6Ztg93lP/2cfvfLRNH/jqcSfH/5nvvNLo3+jTvDy24uGshuDPAjrcNA9++vJrCcNfmW/bvWDo8TVuR8QvHL+Nn+u978v9YZ9YqPa7+85Xhr7b'
        b'udor4UZjkXpu2abDl9bm/uo9r8zfrZ/0QUjG6zG1Gd/+MH6u55vLlGaPGKqweSkoJCAuRIgOF3BSdEIYgssWPZpEF2Q5ursVHw4KjQ8OVIbi6mBcynGuCnH63LhH5KwP'
        b'XYhBBxNSAH02hqDSFPDeUk6+UoirfF0eEc8djo7Dpi3HpYEhoQLUiq4C/2JhlAB3P6KnZ4fw1VmgGexySxG73LLNFbWEBOKyMCEXiu5KcK8b7ntEIsTp6AboUXlScDw5'
        b'frkK20M6TWiNOn0eKaA0VopPLsaHExgTBCwTKcpwwvtFuC+1SCkfEQYodeT2wvd66MlFFYVir+kz4jQ3R1ewU5OvyGG3tUKJn5w/YkE9QQYhdGSXC0nb67ANv9rL/XWF'
        b'hHN0HXaZNOzgUjf78Oyjc0sWv29jP+zsVqc9rD26uUb0voNns+/FsJawTt8hnxkDPjNGhWInv2EPvyGPkAGPkNbsQY+oTv2NHV07XrN/bfXgjPhBj/jhKQGjIm7ScsFD'
        b'Gec+pTmq1WzILXzALXzYQ/G+i9ewl3ezd3NMfW7NsvdtnIfdvU+HNIQ0htWYERkWHF7QPG3IIWDAIWDYxWuUE0xdIfiSE7iuEHww2XdUQr6MSjln97qMwxnNqUNOgQNO'
        b'gVCx33/6oMv0Yagi4lxnfODk9lR58+ZBlwi+OPIDN8/Tkxsmt7oMuUUMuEUQqRxc6pe1zh+cNAuIr963c6r3rdc1C+oDWkMH3WeS6XF2r4+sj6nJLVk2bONcrx20mUre'
        b'OnrWbxxw9B9yDB5wDG5NHXSMLFnyvgOZz/dt3IZdvIdcggdcSIFLZL9t5AeOrvV29fY1cfVF0KjVsVXdKWh1G3CMrBE8cAlotRt0CWo1DLhE9dtGfTW6RMBN8h/yiB7w'
        b'iIbxO/k9IMLD36/1ZO1ft/Fbas/90N52qZ/oh74CeOrA0nFKyxExWecREaCfETMeb4yICXAYMcvI0BnzMzJG5BkZWXkadb6xEN786y1mCY9M+Ji2mY7YNrqL6OM4qTML'
        b'Hn/fyz3WigUC/79w8PjQ2qV88175qFAicHwgty+f9aHYZn/SsMzmgczhq4cSTmJror7WEwt6UhrMXZHPEIHJJ7qL6xIcEkBFcHkyrkqJl+DrKznrQtFMdLWIlifMwg0J'
        b'ickMdws4+Vq8z1OIr6K7uJVdeWiXRxO8DlFpFcPrjqlZpluW5CM2QZRNBHULGeqmmJsDxC2dJuaRtih1HG7OFwPSFo1D2uIJmFoUI6ZI+5m3E5D2dgFB2vQ+5DiorSvY'
        b'olCbQPNEqDwRFtN7l9+NwnWarUatjmG+Qo0OkPgWBjxNFzNDLVJMqA06DFwFnLVbNEt0ugJdIGWghpLsJ0CbyEJEYWD7aQHHECovJKv1tMTj4fjSPPVGhZYB/qwCnU6j'
        b'LyzIzwY0SlG5PrfAmJdN0CoDoRT6Kxj0f4JLl2jJEJ7AXQg31IrIEIOxECAtD3DpyAF1B5AawYS58t+iVEmykVyZhQC6cyt/rTHZfMLFxtLEwOXB6FIqu+NIXqQkxicJ'
        b'yEFEqXxWwvpUbVjk/4j0yQRHegf0ZDW8aYsuvc4JlO9ZWg5UrLCODT+rPHbqTVfk/sZP9goW1cfWFzcktkSeT7S0lFR4B4cP2u/7jV2F/zrvxEDLFstAy5Naru89WdZL'
        b'dkrhI1+KyKbgenkgbHpcCoHwJVyRZOT90WTUI8Ydfuge9ThKdB2dSAhdDg4JnBxxNw2ZxOO4o15xfgq6opT+G7WXjnkWqvAjcnaFl/mQySYfQqaL+JClZpyj13vOPv1T'
        b'Fg06x/bbxg67TRlyCxtwC+uU9U19bdqgW1zpcuZXXDxqdvbbeoOlL0n4kqwDM1tmIzLTVhsx4zeQjkAAHXGvOveJ0pkxo0QEZPZosukxZLJH34A92iwVCHzBgwh8v689'
        b'Oi715y7II0TGeWTWr+OrIc/kFdpwLblCgipQc7DopYRpqGoragf6LrqA7lpwG/ARK3xq8m6GpBtRlVG+zXoL2gewHcIKfFmFihkcLUfFwfJtWx1QHSkqIdAS97FkR9da'
        b'VK7H121QD7ocKeaE+IjAOZ6/g5nrhHr0kTr0arqQExRw6IY33kcZigGzlsm3bVu9SQr8DnD4BL6M28CwksI41JtMExm9qIxPZFwEtE8A1RaIOU5NTGXEoRsiJ3QNXaOQ'
        b'Oi4YXwkCm5tmFHBCVCWIxe2oc4JVlZlUSsc9yWWAVZWoTNkMc7CuFtNkY9ZV+l+0rjlgXdXj8xjUpDyVxRhvi4itIlWenz34jmCfNPi/Gutn5dEu9RrDs9H9U52TsRVk'
        b'ZRnBjOZnMSFM8f2SFTGKWHDxOmJaF4NLyDIU6CB6LzRuyNPqc6Hxhh20Jm/SYzUgqzqP8lgEihg6TgY1mUAj/UFA4OrY1MBg+LN4MfkTm7IqAv6CGIGLIhfRgtjYwGDK'
        b'ZZy86jx9wXOzEWQAdK4KWQ4COGUTy76jECaEMPmPfN0Yl4JC5uJIy//Mzf2fJzvGkMSYG7FJXkr9SCE6s/N5t+NL/VHZv/Qj6Wk0qixZ47b4liCTWLpJStFcluk4udth'
        b'+1VhHLF/c99/eR0LNdFhJT5DMyVp3BzcnbYd3aEa6xCQCualBJVwYZs5oYPAHPXhvZTNH8Jt/O24mRAFZSb+bh4ILWSMLuKjaeTOUQSHW3BfBOrwNpJsB7q9LC0KBhjJ'
        b'vbA2coGOsvhttN38s9xCGGemZZlgMsdH0GAgy1Ar44GuoLoII+6lvB1xC4d7wHKv4HBv9gp8C/dRPk4b5MEl5FcstpnBbp75XKqWK8gQ6geh6KcBdbsPJ1nn3iwOtz2Q'
        b'sa45dVqo8XcZG34jGc58ZPtH16QXD7deMXwWf6ejd8WGhSeTjs749a5T2uqHHm8UtX725t4jdkOWd5c3fvl6/M57M0WO1/8k/tGBT6xSGo95rEs9Zv1NwzuRKSs6BfFl'
        b'q9OD/ui57gNx+56+88kHP3n041O/qm/6e+PZ2GWNHU12D86f2KjZ4TBsTPz0WIPqUe/pzWf2rc8/9+X/7LqsrGs9Gdm9fOXqM7tfvTnFfoqo5qvHcx68dfuth+47fvuN'
        b'/ZK/RAUFX37b06zrjVNtX4jebfBRz4xWyh7RE0p8NZQFtjSqdfEOWWlDHfcU3OZMHbyLA7j4p927hfERvdV3LzSCWGIIa1Mgtg2DGiG4NB534ooEMy4CN0vjPdFJGgUn'
        b'hsR6xMsTcIVyjJUTOiSWJeCOR2SLLEZn0LGElBDBNnSbE24TxKAe3PyIeB8DvoaKSXwclkKk3CNEt/CZwBlJNHhG53H5IlO8S2JdXIZuWJNL2Y/ID3pQMeoNTMCVCSQw'
        b'x2ddaWxuEy7aiPtwrdL8+wW5JEM+FuMyNGLOAlqw4roQExb5PY9FXgYs4kJCM3unOuVh5dGgkljAHe+7eL/n7t8/demg+7J+x2WjQpGd97BXwJDXzAGvmX0Og17zapY9'
        b'lAKKqc9qjhpymDrgMHXYw+f0nIY5zfqLO1p2nN015BE14BEFEeQHDl5DDr4DDr7Nq4cclAMOSujsgY19TVT59vrI8j3NU5rVLf6tsWdD+kT3LW9avqYampkwMDOBiAS1'
        b'Ikq31bsN2vg0Z7V6t+R0mg/6z6LBonN9VP3WZrv6mc1FF3e37D77yqDHdBaVfwVT6uoDIaCd9wMPBYSAdt5f68ld41672FAOh1rEzhHh2QJ4MiglZ7iJZMhGROBOnoeg'
        b'vjOb8EykF2J6/Gk8skozEwgmPwJkNfn7IqsT0kDukjxapBTQ8xPchrvyyblLIKp5cvCCDqEDE34oNGZlN3AsXqM/FBJPE479IEj0X/xBECCJnU0Wq5hr+I5QJYdGHRQY'
        b'jD/s+H8Vn03wQaJnfJA02TgXvr9QFP6sBzqMOv5tKBPC53lxjeUCPTrv9yRhfxG3sQuJ3f7oEhgOXJaEK1bjkkSh/RLUhg6g86hhyS70KmpTcitszdB1fNlJ25aSK9av'
        b'gFbZH3f0ZJ2AqKh1LCrS7BoXF9mSuCixxRAqWtHktHp+vXmOsMzq88IdOb4erq/OjEiSqfe2rVB/8BPYiq+Zx6u2KCWPyL196ZQZpqiIN5k6ALImq7kc36ZG10sY/cTm'
        b'+gUIQxaiC4+8OJoSrkOVTzKJC9BRUzIR1QupRROgW+jAODuKKzeZTGm6J7W0+ehVfHoeup6QMjHdiLsNSuE4LSPGymTHzDZqDNSKTTdZsUTeiu2RPR1RPUnPPZUle89Z'
        b'0e89Y9B5Zr/tzGEHzyEHvwEHv+bsQYegfssgHXEqzC5IdGRFnxtPkVh4XDQ13fRwBR3Uk6uGfwORtsgEAvvvoe5fEnU/Agj/jDxE9G+1Wazi/i9q806L1YV5WoN+TGXZ'
        b'ORnoqIK8zdGpN9IzMFBfk9qrFdOem1KwCIhNUSWnrkoLVsTGLYlNWK1KClYAt4SM2JTFS4IVMbG0PCNZlbRoySrlv9dUioJGxWac5QpvEafIzFsas4MzzoaXq+NRN/nt'
        b'ZhD5LWVp4so41IxOP4nQ8BElarNADTvg/3hUuoNDp6QWAPc60AX6a5aI6IzxrUFHadbZC7eKpwWhM6FTtT/+qQo8BFTNmLOV6eWkN37EFFAv04fHhk+Rx3rFBsTKduiP'
        b'Rq/Y4jNDFDstKlETflSZ+kpglmx1gCioxumNMu0GWVTiS15ZAWelqdMkvwjO2Z/WUhHzed+vzqPXHgi5ry9ZWh48ohQ/Ii5pWRZuCQLocu8J+gnZBGCF7FOIXK+j0+O1'
        b'7AwYJ17NcMMmiks0+B64inJvVPEEfVjPxN00D4+v4PqZCQwQ9dkHSDlzVyFqwReVSvFzXR5ZhrF9P2IBIZiez3HMN2lkBtPI0XRzztF1TAWfzQZTNVww6Lyw33bhd6WF'
        b'oU6z16BzeL9t+LCDa93cw3OPzu+39P7fUtL5pkfAeCVNMv9+SqqbQXoVGIkEYTPWEU+MK1A5vk3utYahMmbI3F8R5zrOer4O5xAdFps8Mvnh7lj29L+rx7kQ3zuR7Ol4'
        b'x0xTkfnqLTQ6fY4/JrEpOeUu1MAL8NuhFvFMm/PUBgOEmllqcLQTGVE3rc5mSdlngmmLsWD638XSLI7+/wMPyBgeWGiMH48HpPjmf5bZRO24ipqp2+6uXDhEjeF7Vm7M'
        b'CAjiD9oP4tu4ih3qtzGY4LuT3torQPvTnsIIAYljKOEJROh1otz7t0vJz6ttw3M+z50VGsFpP7f8VqwvgJKEoessm3ruednUK2/YCj8xi0pLiwj3tYjk/iKNiMrk9i93'
        b'UswpcVp9QHns7Y/nacRv9mS9aRaFExdu9Zi6vkny4y3BAflZkrQ6M53bjAs3WyxldVsvCLjf6K3R8lGl9BG5p4zb0hKfwhVha9FdE65Ad1ALOys8uccsKBnGtG8sJkuh'
        b'pxe4CmxZkoSbkSzdg0/gvfRQMyVaFhTihU49sX/oIL5GDzV9rHHVxAPNbZMpCjmOjlOkYoGbMiZGc+gmukXtI7pe9Ijd0U9ABxKelgF3pEhA7CNifMoFd4GZ+c4ogJiZ'
        b'cYlfSwpRYCcT3dAtM1nFPRyf+bV4CqeQSGjOoM3k5shBGz96ABY54BLZOWfQZUG/7YIPvJRDXmEDXmGDXhE18mEXnyGXkAGXkNbsIZeoAZeo99x9+/3mDLrP7Xec+8DD'
        b'r3nzoEdkZ8SAR3SNjLIKHXAJbd0+6EKgzjijaTYiJzY7o0BHwdS/jHdY7nhcapuOiT5mC/gIBwzp461gSN1I7tjt+0Y4x6S+3Dl5mEgpSk5eqhQsVQqTl2o9lB2c/hBM'
        b'XS3+5MA7h9bZqyeZjT62jvmAc5q6dqb79RVBnZ3TPI6lvfDF3aC3ioOXpdVY9WzZ9efuu0O/fvA4fVZv88WPdswv+vM/fvjN7V17rTNQbeHU3v1TPzxlf2pJTEvdDNmv'
        b'XFbun9vcmySLcHVo+GbFH+80Vo5k99YO/KEhwCLnk3q74fban9hYDJxOK3+vqcq2LsCyYejtGp+o7GU92xZmtf/00oG3LrmvKn6QrMzo2fvu5XN3Rl+TTy47kacd8FlR'
        b'ceSccMFyrdubWkmg1knY6x5tsP7454pNWs8/aEUfD/ztxYUuZw6Hog23xAm/j9yf63BCKz8+1elPPYv+uq40vLK59ira5B79US52v+X8x17RZ7lT3x20irxl15hr2fh7'
        b'Z8NA+6cXfpn9z22P+j2HG1L/HrXh4+Tb/W8ZJzXPtrzlsSt38l9/vvvTi99s3ev/29/G/+2OmcbAHfpUPeunioOfhi/91G7S+bMzl1ZPqX2grHRYX/2h77wDg48sf/j7'
        b'tMR+/cyUsA987vp2hL31qdODrfZrfh+9/uKMwqPvoy07l927fVv39a6cLYkx3OOHnM1DWfVDccrDKz92W73qxNUfyJe8bffjkwlL1tTZfnTJNmtP7N+n9vgcdZv+Tl/Q'
        b'jJ6wSSsvdvx8U0qt7YlWh+35rd6HdizrKNt8M/rgiX9c33zw5z/Spzw2nE9vqxuts6uZvCB9sXwUB0x/72DOMTengzM+f+2tTRF/mKS6Yt6uH5l/+d3qtlarBWlpzi88'
        b'/MNkp6q/D354LfqlN/+y7GcztpcXba+2OfmbKd98G7n+vZZjR2s9BO9/c+yV08d++Yfin630ixp0iZqx8Qy6Hxmds+endQ1fZEfdT3r8W8umQsG9T/742SS7v3z8y3at'
        b'7T/++rn+VvsnJ/+2JvfGL8rUP4j+wsPq03dDnNzAwtGE36FcO/D5grB8TjCTw1XxqJPaGYfJeO8EOzMLzDqDYd2o5JEPMXrNRUXEOCaglqDnpKpQqzm1dgkCMS4HoFYZ'
        b'IuWk6ehisHBKDnqVxlQQiV7HTUHLQ3BJfGKyhJOjLsBvzUJ8ahU6SO2h3BodSSD+CqrginhSpSNJIcSXQvBB5aTvd2FC9l2P733t4rlmhYirMH0Wks/eCR9mTWUZGXkF'
        b'6uyMDF2KyZLaSjnuH4Avlwo4KycIA8xdiAmNLC+q9y5/uUHfHNmsbolu3Nm6svGVLt9OXZ93l7FvZdf2ntDXF//IHscNRia+50rAqLohutG8efmAa2iny4DrzP65yQMu'
        b'yf2rUvtVLwysWjPosoaAT/uj+f229A7Ei4JRC87esSbmsFPJoi+kUneLEutRR87ebdjOddjO46GZ2M2ixGrUOkngZDFsadtv7zcqIt8/sLStCRuVkK+jUs7KDggzSsgY'
        b'YU4JC0bIKWEJRL99wKgVpawp5TtqQylbvsyOUvasmQMlHGlRyKgTpZwp5TfqQilXVtGNEu6M8KDEJL6eJ6W8eGoypRSsojclfJgcD6dQypcV+VHCnxYpR6dSKoCXQ0mp'
        b'QF78IEoF81QIpUL5dmGUCufLIigVyTqIosQ0RkRTYjpfbwalZvISz6LUbFZxDiXmMmIeJebzUi2g1EIBzyRGQOlFAp5NLKMX8/QXSxi9VMCLuozRcSY6ntHLTe0TGJ0o'
        b'YH0nMTKZJ1MYuYInVzJyFU+uZmQqT6oY+QJPrmHkizyZxsi1PLmOketNcr3E6HS+OIORmSYx1YzeYKKzGJ1taq5hdI5pGjYyOpfREaNaRm/i2W9mZJ5pVrcwOp8vLmBk'
        b'IU9uZaSOJ/WMNJj6NjJ6G19cxMjtPLmDkTtNku9i9Mt88W5G7hHwy/0KoxcK+eoxQrbeQl7SWEYvNpUvYfRSoWm9GR3H0w/jGb1cyDn4DNv7Ddsr6dPb9J/fF2m0Ron5'
        b'6Hoh5+F7Oqwh7F33oNLlJbHDrn5DrkEDrkHvuoYcFtcIhl09T1s1WDWrB12Djkgeiji30A8cQzudBhynlywZ9px8em3D2lbJoGdoSXxNVnnyQ3POIxisgYXtA3Pbmqx6'
        b'fWtsZ/aA+ZzHwnnm077kyEPEWcwlD9tRMZBkEmjl+inN+k7xgHn0Y6GduSupMJ2vBSQor4tb3abDm/q9UwedVSXyD8xtSAerm6e0Lu506jT2vfDakh/59QetGDBf+Vjo'
        b'Dww4f8ZllYBnAzTZ07xkA+bufxFamgeTQg++BpBgacZXsDb3GV8BSDA3TNzVA+bej4X25rNIGa1l+1AM5FejWTKBebzggf3kc5b9IUsHFcsG7eP6LeO+preuSmMmxXty'
        b'P/Z0iA/nM/u2I0LwHP9hOv8/cVq2T7DwREdF3RN9kDhIP58HxbECgcD2MYBi2y/I4/si4yZpKHdVPkukXWUDcd0P4M2b8jJjzU8tihc6Hvjz39skdk5/XdYWU/7X33Wn'
        b'K3I/3L6m2Hb/4vBim8Fvpk8rqx3Me9vy5K57UY9739a+rfunON73ZIt4//6YT7Lv3PzBG7nxNb75a24MKX9/qM69MnH2mvWL/IRf6hwT0iI/93/j2guLHJYeD/3Hr0Pt'
        b'Pj1Xel7+je6rb9Nury04cbEtKsG5oKfmzEKzeZO8ccTXfQurgizD51qe69l/6GLu8hud+/Le/8ntwlP3ZgjKHnzrtyRB9mF32Ac/WhQQ9+d/Ct2+9Kr4zT+UVhQzOXmi'
        b'E/Tfa0vB1fQgTo660bk1QtyK76JihnhqV9F4uIvUIsdq5qF2+I4IteB2VEuZONrHoHJUjatJ0IYqUbUZZ22PG81FXrgP3aVp7EjchC+lLkyITwpMMuOkYqEsfz0Fc/bR'
        b'uDZoucBGwgkSOFyPO/DhR6EUZ+F6MQkEpxrHnwSgqrAEgGxVECRWi7hlqMsMVaOy9TShvgSV4DrSpAidGd9GyrksFgfi5uU01Iwjv16moeZ4Th6oUYxb0T50Ad/Ap+lx'
        b'Ib6Rg3pJLjIBl5txEP4Xi0MEqN0Ln2H590p4tQ+XK4ETzF1pCrgbm5VTckUqdA7doV0ZUONOU4VgIjnNaQo4VB6jwNck5B+76Ka81uNDqCQoJRiX0f5gFfA9ETojBFla'
        b'oAq5I4QrvOnPOSsAVYYFbuVhq7tRvLMAHczxUfp8N2r8r2DF/+JD70Nh5zNo86nPGPjU5msNYELSTeDzdY6e533pzkkchq0ch6y8Bqy8Tm4ftArYu3RYbHEocV9iv533'
        b'uZnviIN/KbYCwOfu1S92HhVaSNYKfilzA5znFTDkGTXgGTXoGd0vcx+WWVfLS+XvOPq/I5s6LLMfknkMyDzqY96ReQ3buA3Z+A/Y+A/ZBAzYBAxb2lcnlyb3e7z4jmXa'
        b'Y+lmsWTWY448H9Ln6FpzztJxb8pXj7bCF5cvOaEkfNjJrcSC76HfMfRdGeBQeM0OQ2+LF4VxKMwz1kaErQXwZCZz8ogoT5M/IiZXSkYkNJ8/Is7T6g0j4mxtFjwLCqFY'
        b'pDfoRiQbdhg0+hHxhoKCvBGRNt8wIskBsA5/dOr8jdBam19oNIyIsnJ1I6ICXfaINEebZ9AAsUVdOCLaqS0ckaj1WVrtiChXsx2qAHsLrV6brzeo87M0I1KaL8yi19s0'
        b'hQb9iN2WguxZMzLYWXa2dqPWMCLX52pzDBkakt8bsTLmZ+Wqtfma7AzN9qwR84wMvcZAruyOSI35Rr0m+4kr0JN9nfmvPgoFM+zppgf5lwf1xMJ/++235PKunUCQKyK2'
        b'feLzIX1+H0tPfNfrMmmMK/e6qzxmiuhrmek2+ohtRgb/nQ+DvnbPmfjviiryCwwKUqbJTlbKyI3l7IIsGDF8Uefl8VuX7GSSjoL3FjC5OoO+SGvIHZHmFWSp8/QjluOz'
        b'pLrdHJ8mYgkjpglz2b9bOl93AEiS1qYHb6Mi8G8PhWKBGGIWudVesy+kS2HAo6ssOHM7fisvH5JNHZBN7Q+e/7o/DhgMXj4ss31g4dzvEjVoMa1fPO0BZ1vj+gvOnfb2'
        b'vwC7HHyE'
    ))))
