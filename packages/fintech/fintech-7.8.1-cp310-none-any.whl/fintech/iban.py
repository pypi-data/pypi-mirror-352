
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
        b'eJzNfAdYlFfW/zvvvDMMDE0ExZqxRBmqIPaKqAFpKrZoFAYYBEXAKVgSlaIMHbuIFUFFRYoIlohmz8m6JWVTtuRjUzeb3Wyym3xZs81sku/c+w4wKNnsPv/veb6/Pgzj'
        b'3Pc999xz7/md3+/ed/xQeOSPkn7m0495Nr2kCWuFjcJaRZoiTdwrrBWNyrNSmrJOYfJKk4yqIiFPMA9dJxrVaaoiRaHC6GQUixQKIU2dKDhn6J0eprtEL4iI123JSbNm'
        b'GXU56TpLhlG3dIclIydbtzgz22JMzdDlGlI3GzYag11cVmRkmnuuTTOmZ2Ybzbp0a3aqJTMn26yz5OhSM4ypm3WG7DRdqslosBh1zLo52CV1pIP/T9DPKPrRsjFk0YtN'
        b'sClsok1pk2wqm9rmZNPYnG0uNq3N1eZmc7d52Dxtg2xetsE2b5uPbYhtqM3XNsw23DbCNjJ9FB+3ZteoEqFI2DV6p/Nzo4qE1cJzo4sEhbB71O7RiQ7vt7ExK+NTHYMp'
        b'0o8b/Qxmzkg8oImC3iU+S0PvN65WrtIJ7F1y1mdxcYJ1Ar2F/Xh3HZZjaULsMizBygQ9VkavXBoEF7FBLUxcJOG9eLhhnUqXYnUittGlVVgdQNdjVVQcVq2im8pDlkUF'
        b'xmAFVkTHYlk01EGRSsiDaudndHCHd31shjpvo9JXEHTJge6T5gjWDcxeg48B253dlkWR0YrolVFw1Q9LApfE4YFEDZZGrSTT/fvyi4rFqvjYhJV+1FASQp4ui1qy0i8o'
        b'ahe2RQcq4LIkWKDUZyqUYUuq4pFF5t4Tl/jvmaR0d/s0KEpEmgaRpkHBp0HkoVfsFhMd3g80Dc704/LYNLTK0/DmBCfB1fd5BcXCtXLQToF/uDlCFKT5Rpq/5Njf+2TL'
        b'H34UpxE8R15XC8nJsVvXR8ofdphUgsb7H0phfnLWUdcA4ZKQxbpqTRkmfeklJL8ifjDxz2Jn6NrtdxVZzI/8544rWp0EnbAwNeztsIJNxwX+sXLnnz0Oeyj8zpofKL5Z'
        b'4+y1Q+gWrEHMd78naTpoSv38sCwkKgjL4NIKP5qUW4uxOjA4OmhJnELI9nCegzVQpg+x+rCZLPXGthQ8aXaloGONAEclbLJ6s5byOc46tJnJaXovQMkYOGRlYcGmWcOn'
        b'42mzyYneVwpQtnaJbGofnJwxVmfGTvaP/QJUwPFUbmqmJxyNGGaGKgoo1glwCm4a+S0j8RAcXQDF1ETxw3MCnH7O0+rFUgHPjJiSbN7KOq+mPkK2WYeyNX8Xa6bgUbxo'
        b'xjY1NR2hLID2SbwXOLQTry0xmq3sngMClC+E83LDkadGR8IFsxu744wAx7XQzq0NhiYoxVN4yIztzLVjZM0HWq1DqE2Bh56CDosZKthoTgpQC3uhifu2aBHsc91t1jKX'
        b'z5I5xQI+GLiFpVi3xs28jdYsHhWgCqr1/Aa4Fm3YGWz2EOQbaoSRvIs9cAf2xdBt7W6s96sCnJGwgN+xehXkzwnV8thfoTsWqayD6OP16wZ7LoFymiuFRoBmX1+54wI4'
        b'9+yQNDNeY3N4UIBqKBV4SwRFp21lHrZblXJ4D0P9KN43XISijZuxToutrI8Wijw05cjmiqElEY6J5m2ibK4sGKrk6BfAaWzFy7DXjDeYy8cFOKA18LvGYh0WbsQms4d9'
        b'JmvnYTHvCu9A7eRhUIntGtbUIMAJqA+RF8b0MVBmoQbmw0XyIRXL5ClrFBa6rsB2i0rupToSDnAXPH2wFm9AK7a7quV7TmERBY0tTLj3XFTOZGphYWgkaxmC7HbNmB3Y'
        b'uh7bsY05XU+LHDtoSDwOt6Ed6lSRhGbsrmYB6tLhmNWXNV3Hq/S3kRaHsz1G57ADq3gjVk/Ha3gb71Eji22rAPWUb1e59xGLlBM3UdDt6+0A2LBCDsVhPO6aPZcmXCHf'
        b'cw4OQqlssH4XXoRCPEtutrPWyxSnWXBTHkHzOrwVT8GnNid5qZxejpd54KdQZG9gkUQzaR/BKWUYX0QrjFgZEaDVsI87BTg/RycPudaVRn1nixavMVsdzIuGaDmFC3cE'
        b'jYFL2jyV3MlxqjHn5UVxYOR8yggtdrIQtrGwlw62I0heMFzD49TExttOqzh5qtxSkBQfhzeoQSX3U5dI2MJcCMPTcHUSNJgtzLcStuRuQIkMO1d3YCPenKBl6MtiXrM8'
        b'k1tbBUUWqMWTWhfWzS0BLkCXwjqMWtZi59NQPhX3QwdUqILwhKDEc4qEDfOsI5jBo3BhEJTn4WGohDJVANYKUoYCCrDc38qq/6qnzfZW4/Iwuw3BGSrFoX7YqlfySOLt'
        b'xVOxnOZZEZsj5FBiN8q+XqGZvRJDjkpQkyKkYD1UW1mWx2XtiGFets5LE9IWrZEj2JJC6+eOh8OYDw6zTmRmLikpeQ5hCVyZCpdUhjia0YZNkc/AeahfGyeEm1VwJAhu'
        b'8zUej3uneMARM0+MUgFsJlerntk4gXeUPTaa8QitNPY2HK7gEUkYuZUWbqXkvAkOyhDetdASn2vG6woZqavmLrL6MWRLxpuyEeiERmYlCpp7jcDendAlKeHsZHnFdoKN'
        b'kqcNK/qKB91WYw2gxpVog8M9/lx18KdJNnUNi/GgpCZULZczo5jS6VCCB+EtA4nTApycjZU8PD5WyrNDUdBEwek1FMbcI0M+C4OUeBPO4jl5ydVi9dNQqjab2OqxCbB3'
        b'DxzmVpKxdlVvfFSRSSzKcGeTVofl0LhqsLBE56TFlrV8XnfT+KvXLu8rfTNhnzWYGpbDPb1jkG1r7O5AC1ayX5eZU0Em1VY4gXvlUJdvXJEj9RXLQLxhDWGf38CLeFFD'
        b'oe0ZWqUyRfaJkKSWFgCU0+RH4U01dkx+igcpmtKxDg6uJqRnFqqoxsH+dOuTbHVdgPZIPAJnHCPFJk9aLozAdiW2woU4biQFnocuqqOHzS6iPGtHoCPdOp1ZfB4LTA7z'
        b'X/no5DVa9sQx601x6pQ4YSu0aOCWB5by0I96hnw7ucUMZZIMeyfh8lOcl8B1pSdzq7l3ApVwkGrlEShOp3SrFUKJKlzCMyqocg3heId78UQUxafWgUx4Qi1fo6nTCQUd'
        b'F5a8RHnkRyYsh0NKKjj34C53avnTsHcslprd2VBrGfCfoBRgAXMLnz9QulziZjI80CY5jfHjq8EPjsGZkWkO9CVnrXUSo4ZQMbTHRjENvtkhYA55E/6sCo5T0Xyeh9+P'
        b'uBDeyHZgPNAAV6xhbJgtNJ8H7BajsMhhuZOlSnkGmMUwrFbRki8X5RWWv3qWf2QfVYIj3lwf6NcF9s/lnknkQ3x6BF6VNLG53CkjXoqErnmOpKoKa6yhnHFBfXovODEz'
        b'lMKH7Wab5BHznA4icCVEieNxD8HLWOUjkUEnuYAfhusaufrYoCEWm5b10TT6e5pjRsK2nT0d0Ww+uwcPU9nZwZYJFOvgHCVpHHY5hcEFrJVNncKTeBIK5/Yxu83QJS+5'
        b'GqgnjJGtLUu2oyrlFhat9Zsqh8AMZzRYMZZIHV9yZ7GaJroEzzqQQS8PnvYu42kCD/VMxJE1RED7p709AEdVZmiWs2xblpVo2BmzXK9PMWisJTzjbldgI9zNJkLayyCx'
        b'Y5o1kAkd4u/n7T2xRX+1txhE6ogqM5xKwNNOwXgX82XYzJcoaa9DUR9ZU8N+7jQej1T2YYsbRUT2vnfyeBCC4XnVJupLZl1lUDfEO8i8TSWvgkrcP02WmmdXz7XbuvxY'
        b'bXkqd6KSnOgYzz3KwjK8p8pyIIh4Brs4BK+LwX2PwlM4SxdJGEF4eQ47ldjmsZJX3KEJi4UMMqKQyfdh9z18re9+Bpvg3PY+krnYn6OpG94O6pmh+o09mXjp0UzcqoIa'
        b'rMTj3FZahE8mdpg9FDIpPRmLdfJg26EjzxGv2LueerNrmlKJLXj0OXnRtBFydWKzlwO3zcIWXpGdgCasx6eWx/Ivh+awXnKCjhEy2exUUyS6yHQfGSY6cdw6hTUWYfHw'
        b'PrTqGxuW7MIC+pcE11zjIhbC1QmCCY9ocH84Xpex4cDEuK2rHXh0bhLPT6162jqas3aZAdASPDoWD/PRR2ghv69O2rMmUqcSwjfQaM+q4AycJ77NGU2ZKVpJAW13ZVN9'
        b'nsY+GQ/ytQcVQyif+FRHTGDL71GY5Wg9GU+o4GDyUHklX6aRFD1Jyd3H7LVRHGexBk8t64OgnkJrN6aksbttmqJYNjRW5TSdtEWRzAQuQxkWRD3hIAeGZnFs8IH940nJ'
        b'VMXwSkZ25FLSm2qcdC2HSqcxpLC4b17QOc+fZEa7zJhppLXxYOPVyDIRrz9SwbkNVrsnwyVi0B1U1jZF8fzKwlrt+DBsd3eSqW29lRQqWytEDA/jwUdzI0wO04jR0IBt'
        b'tOpWkADnq64obA7eIT0j15BrVPzxEtyxjqU285I1eF7qV9nsLGAkFFKaLhkuR6csajGcm4ntW0U5waqTqS6yAU2wzuuH9o6Ln2J6D2xKvP0UecIn7SBcT8LTJGi2qmWY'
        b'278ULlrHsyGdJsAiDB7y6KhERkhuUKZPHMbZOxQ8QxB/g+bfQZ9RUl3jji6j+ti6hehCnz4bOVTOmNInoY2mu9lRnl0FWT/6uOKhVQsctBnczOWRjoKLux/HoGYeZ2zG'
        b'O9jK0vsIJR4zMygrCiomOig5PDlEXvpNS0PVWE0t9vw5CEeX8fjhXaWrHTwu93QA1+0BpIksIPy4rrWz3nU0hydJpZEdlcwtDq0j5sIX/TEsXmmfCT1pGMfsaXYgm6FY'
        b'qyKlm8FXRmIQUeU7cyiSHfYcOk70toUv+7w1vfy3bXXfygjv4XmytdUq4piHXfggSUXBLcjPIrkqyrE/uzNWXq8HsN5gt+Y3xp47DCd6y9TSWKcZKwhQGQgtmDl+SoKD'
        b'5sWqVXyIVAjJhDwbeVt6Mvvqo1GbDPdUUJ2AjXyIT2+jenKQimm7m0pWovXE95o4VyEJcSGiLxvJmpjKEvII0Q9yjkgo3Jw6CEqmKODEfJf4mBF8mCO2jB1F5cdBdkNV'
        b'COeIAcsWPiY8evA7eLVeiTfmUx3mi7GIInUjYLqjQCdtc0quxLfw1FyHpAoi7taP1tn5g1WVC+0K7tNOOO0NV11I06tlayeJfcqhJxga+/gKviKv4BPU1y0lXosCOX10'
        b'eIuSpMnHYXOAQJWRLQrbcTw9IEG0q72ro/Ge5I4VRpm17MXGUdiZodWoZTHfQGO9bPXnJAQLqHQ9hl5Nsk+0HpuVlFtn0K7wr0H+gjmBffsSWLmUu6Sm9LP1sJ/C4D7S'
        b'5rCsAp2mQQce4BxhuOswt9Vai734HIrCZm5/wZRYD6xx2N1YjzY+hNGwDwuxdZzDDsJ+ot7snrUS7scbO7V5zNglkkResJePbR2eynUgpY/kM9p2MTy8h7Vwgtt5CjoS'
        b'RmORNo/1cEWAY+PhDOf2Sjw1/PGVCV14mo0P2tcSCOzdhPVrBdNmElVW+w6DG3Z6J8IRhw2ZtrU8VnNG7B5Q7au8ZEWFh3yxiUQCNE+Xd5AqiTjVYxdccdjCyRA5eYKK'
        b'MdjhIKlWKxw4ooOshUMqSwael4nF5ZgF4asc9nwy4+TJPTvuWcjf5rDns9TCG6YRHeqY4ql1Z7N+R4DG7VBqnUwNq6EUr/T0fppmpL8cc0S6OmIfFKdKjmcbIX8NXh7c'
        b'NzmPkYxm1dYpiqUap6l+GfKSb4tzeUw5QpMqhcIfJ4RBG7YPVREonSGJzvdU6jGfln0f8e+dfXkTYwO0wjVJShrHVwotBHh+oDm5KqdTcwyWSRospsXIWeaF5FUDgIuc'
        b'eyvyZimx62laBGzteGJFdo9h4l6PgJFjgA6p4CSehWt6DY+5F9GcwsETtO6sCt4V4HIgsQS7BLm+C855a7HNnoR1SrjN79mah/mU3NTCbrrJSMogPuNzJwzGOsorZ1Ge'
        b'wIurtNzWBje4TvWpUmu1b2IfI3lzQO7mKNZOTcWuvr08PEAeyLuG2DI3Ik5rtifpaSLSp3iLaTucGT8ZymXo62JAk58tb09coBVZTS2HoMS+nQdX7WkJJXz/T4J2Kg4H'
        b'VkD5SmH1ejWeIRGYr5d4CgzbsAzLYwPw2BKsUFJC3qUqAB3+fHDL03EvzU9s+BS1IG5QhMSTImJHhUuc4VIMVoVgZQBUQZOenVO5eip9yNuD8jiKoX1aQPz8VUFRkiDN'
        b'V5A3V9SLU9nJUc8fGgY/VuJHSgsFfoLFTq7YKRY7vVLanNOd7edWUolUJOxS7XR+TuLnVip+ViXtViU6vN8mOO/VKz/4b5oIF53Dn0h26GnWGbL5aacuPcekyzNkZaZl'
        b'WnYE97uw3z+i5bNW/8052ZYcfm7q33PSqsska3mGzCxDSpYxkBt8ymjaYu/AzO7rZyrFkL1Zl5qTZuQnr8wqt2e2buk50TWkpuZYsy26bOuWFKNJZzDZLzGm6Qzmfra2'
        b'GbOygl36fTQz12AybNFlUjczdSsy5ENddtqb0msleKAbUjJTZ7JhbszMM2YHyncxBxdER/bzIDP7sRGxP6kUGON2CxuC0ZCaocuhi0wDdsTHZtrh2Jmlx00K5b/fj4Wd'
        b'b9utBevirGYLGyOLe2JC0OTQqVN1EbFLoyJ0YQMYSTMO6JvZmGvgjvmzd/46Iy0Nq8Fi5MflyckrTFZjcnI/fx+3bfdfjjhfWvax6BIzszdmGXWLrKYc3VLDji3GbItZ'
        b'F2EyGh7xxWS0WE3Z5pm9PepysnsXaSB9utiQZeYfsyBvyzQ/MpjHjsw1wqNntYPiF8uV6HZwBtsU27xd3haj2tfOj2HfXugrEP3UTchMfiZw0hCBc4lUAjEblAtYTv96'
        b'Wnh6fBS/dkq0VmDGtE8kZ/0k5Un5HLd1tIdA4DDpVmhyllGZJh+1rYRjz7ANHQK2u/KmTjQ26j24K9vc1rMmuA1n5CaoiZc3XDqwLIOdF05MtJ8YtiyVkfMcObyfnRgu'
        b'IQjkh4aeRHK59LjoFshPDKFDxtsz7lRJWQyiZk5lJ4awD6rlU8ONe3gvY4gEntXmKoUnoZ0r4WPjNvHjxGzvrdqtSuG5jZyXn5ixUO6A4HU+P2TcmsqPGanUyNx7LOST'
        b'W+1mNdsjKeJ65eBmPCF7XLX1SX4CiQUL5ENIkkeXuEHVCCpZ7AgSSxfIp5ALqIZzJVs/hcgSO4Ik1VEkH0NOJHbH3WiMg0YtxWZmBK9Qp/F5OMzHM5/KC7bTSEfgMQFP'
        b'0L1TnpVvKcHbVvM2J2ErVvINvGrYP5m3OGGtG9sig0Iok7fJ8MZ2vVJeKLUBg1nbLLgkN80iEcmH1ICtgbwjkoStck/aCbLjt4j0VrCu4MJIe1etWCNTrXwo9eKbiOTz'
        b'BXkjkSZXL8qSeT/c8+ato9hyY43R9sMLkZhFDT9wdkuWj5xd4SZfcQGiWnAVhO1jdclZPntGCjIFu0Ky9vTkSZKg30yTJqSE+2Y2jZmmMFOZEL5YmjLltbYlyghP9fvH'
        b'T70zq760ZMiYI5UeyTNjkiISpfI1boXO0tuqjxYsV2FDx9DsHzhZ0xd23vo6feM3XUfWjP3Qdfxfl37gq/pzV/6eoobZK59y93lgMY+55OEVsOlUzfRftp57brLTp2fw'
        b'YdimH4Xl3dB0nn573vwv77w29/Csn9WdezBj64NhE3LH190Z9OfZf25a1T56399/O+pBkbWp5R2nT372ycVPtH8L+Nvkv5x/uPTrX3RNGXp5zbuz2145tf+tO69+Gnmk'
        b'aKF69H+NumP6+7NFe9qfjV76rcljwaHswR8f+vor986ld9cnfvP60MzYrmmhf589/NfZL/4kL/WtuvB1b4870wKu6pB7l7PW14W9rHey8DOqM3gdywOwIj3ILypIFNRQ'
        b'Kwbh+SjLSC6BxFUBwdGB/vpgrA7EUnZCA4W+OmlDrsXCjg6JnhdjQ0xCEJQmEDlQC9plcFMnYlXiLgvfumgngliI5enErkv9g4IVZL9QnCzlWth2Z0QQidt2+3Mw29hz'
        b'MIrZWJUX5I9lIaIQDF0q8q3GZBnOLB3GCleS6tfxRFxgNFYRawgX3UkptVjG8F2L9sUx8pM0QPZiOYPBVjzrg3uVeHP7Sr3YLfrp2XmVoHfmv/7tF4aiD31mp5tydhqz'
        b'denys1bBrMjO7XbhkJ/E/sEuM6cw2N0j6SWFRsF+3BWiYohCrZC+dRfVCvFbF1Giz115mwu7RhS/cVGya1lbz2/5CjHfm1/LPnVXSPyvi2Kk6KpgZ2WyX3p1t8Q671ZS'
        b'De92slfEbomVsG6npCSTNTspqVublJSaZTRkW3OTkvTqfz1cvWRiXMzEHrwxsdQysae/TIyj8W6PsmGyPBUKRn6qFkUaHHuVFOpv2Kt1jLwsbmRonR+bEHkyPPAgAQtb'
        b'X4lYhPtjqIkmtmZ1PFYlRKsE91zldCN0WdmsL02A6phYaggZPZ8YpkLQrhWxmZCzhOOBq7+RcVKwQafMSgm9jqQqHSogG5FTTwWcKfQ+HCWlS3ZCqSxREqGUiFAqOaGU'
        b'OIlU7pYSHd7LD0J98JbiUULJn51zYJSmnC06Qw8H7M/2+jO7R5jbin9BME3GrdZMk0wrco0mIplbZP7T80BffwaQ0EMMyBH/5dRj5hbjIpMpx+TPjRmoJW1g3sj8Ze7K'
        b'3PHRQQxImuyDku94dIQDdcGY5uIsw0Zdpsx3U3NMJqM5Nyc7jQgSJ5zmjBxrVhojUDIX4szXznYHpkqLMtmQ+5gZsXCDLizIYs0lxmXnXzxqRBz92BWBrCP99xAn1WPE'
        b'SRVvnUPvV5BKOznAs4LOtC5LY/2XBMLlFfKTg/RamhAbHacQ4AqUamf4YtmKzHsvnJfMzM7Hk3Z+mhycHmCIMmSlZ6X8MXnDC2/94K0f7PepgOv7ZxRfOlp3tK3oUtT1'
        b'4rri0Ep9TV3xmJqCyUpB/4K2bMZ2vWhhu9lwZQt0av2xcgQ+T85gRZzVDp9PQLuELf7RFvYIR+DaJTHBSwg4CYerp2KtnI7D4bqUbbLoxX7Z/10QyCGgWys/LtqHeO4y'
        b'4qVpFF4KGfVMHr3opOrW9Cyqbif78pDhxZW9sMc5+/WuNDHWZfJkL869sMPs/aoPdrwuDwA77FFVxTKshSO7+0bqMEy8KFrn0jUaOIjHHlPIl/AI7IVrJFrPBirXx4QT'
        b'VwNS9lfZIzQuQgoedMNT1Gh/0qfSy0Ob5z4PihWCgngL0Yz8ZJm6lPhiozZvaybWsqYS4iijoIPfNB7qJpmxc5nVI0wSRDyoGIL5Y3mLGhtSzGEmvEeVV1DkCHADKwN5'
        b'Syx2Omvz8pZhlZqs7SMeZsV7BJ1sVc4bksKg72m4KSPfSjjHIRXOYgGetSvy8O19evwWFMrEbF8oFAYQpM7BowpiVFWKSCL+dx5DzV7dsIChppLjpvw4qWjTpGt60VP6'
        b't9AzndDz6++S4zzt+4vx78QOhjPs8u8Xtd+hNdnN/+dSMzWLu2U2Wh4Xl484yOKSk5pqJZjMTn3c0R55uWhphC6SaryJwehCKheplhwTCcZca0pWpjmDDKXs4FfaYT2S'
        b'BKjJkPWYvQWUrsEOvhnYpFj5A+f+iZEr/APp18KF7FdkwvJQ+k3u+S8IW8AbIiP9Ax+z6DAmkq45A4pkNkge51xZGpPVNIboO3IfCSD782/Vyl6LObmPl0j2598rk/0m'
        b'739VmyuEgbS5B2lzVhvwONTC1YEeSO+rMG6bB6oxcM2XKyLD4mGmCYpkQUhOHrnWbZQszFvmei3+SIiid8nPFC9zE7jIJdw7n05Si8n6qBVPR1ntz5uFL4ByKIESIRMK'
        b'BHGwwhkPG7gVS7THhBWK6STwk7MiVFom3PhO31323CrbsQ5lIr84FG8TjeNPB14koXdwMo0yTNBjTVjsMm5nifugNS8p5wtCbnLssVnezA6LRhyR/BuymeFYE4o3IV8+'
        b'tiBN3cpPj5YKUOeylClibid0sHbhUaWfIHgmx9ZtXCKsyHz3g3rB3ExNE47NfbKqyx0mue79WWbta/BC94FpH9+fZbn64s+yrZde3L9ikW5N4/6X1zXkLHnjpy9tm3vG'
        b'umDD5A5Pl5ovxoU2D/nT35RttR9HJgTM9Ks7/u70D1dtcv2vD+dHmRcteXeLz5jjvm2HTH/RRpQ7/6Pi+HNd/1w0Sf+n6vKf7pvwm6bVzYNS1hc8OFJkHNxS26H99cdZ'
        b'i/+e+NuxphmwfkjCreDPOrPuXS7z7/hs8q+erN4WVPaZx3vTw8xt2/UaWZPVYvHsgD49Bq1QEbQAC7nSwdoxwazgB0DzsgEKfsg8CzuY84OGEAbypMuYOAuhK4KwdJYb'
        b'VsQ4CaF4Vh2NFd6W0ZxB4J1gbQxW6Hst+YAtAwslTTzctbDpm4ctc0njKZ7MFcQ8RUQc2LibIaTOLrOvV4QkMEd3i3AeDvqvG2ZhZSYOS8OwvE+qYUu0OzTP47ISW/Cc'
        b'IQYrY5isxHtbuLL0mKTcOBe69AqZCWj+I3kmcxNnWYxRneDMZJLMTPbIrIS9iqSjXBWyDmOKiimtsfTb1/5D3GVwH3fp00HdSkJsB8ryfRJK6SChvHtpDDP9WR+NGX7o'
        b'O2iMO+RDV692knX1IP9NaFNChQ7P6uVnev3xNl7B8lg8P9phux4vRj325ZBe/cO+6EJ1XEwXe78Eovi3vgSyV698+Go/KFsuQ+F3UPh0zsB50XXcD/+/1jzficU9keqP'
        b'xep4zhixdSKe/ddI3IvD7OzNAYtj0CYjYyu0QGfvA4jFS6HsyYX8xC0OLuJ1yi0si8OKRCj0xpJY0WsRXIJ9lE3H6Y1eWOrpBJ1jVme+d18rmWfRTd98XP9pcqCDcFjz'
        b'ws39dYcUUZPPTwpKC68IHBJsiDeoX5oUnPyH5DU/9n35hePuwtJdrn9qmaBXcdmgi8a7HEQ4grhia38Qgc4tFu73xYxVAcOxzGFraEOOjBp1cDqk/9aQr06CGri7AfbN'
        b'4JpjehhcfAxXJLwwRYOFMfLuUFlOWkw2nnDcPhKxamiCnIDigEnutNFo6U1xT57ilORjNPYNFReFaUjPDZeU8gbGgFrjkkJu5KnJbvGlvDH78tQUCtw/HiA5mc8i3E2Q'
        b'97vGiH0u4+2R35N2ok34j9OOSPPDy/1WbWJuVqbF3Jtb8jkEJZCOfZpuMmzk5wqP5FlPrhp04QNq4n4X+0UmrIxfsfzpQF1k1KLImMSVcSSWI+JjkiITFi4K1EVE8vak'
        b'+JVxCxYt1/9rBT1QSvGCPTzFSXDNmsy/Mhes0gv88BLqhsPdYH/2fbkA9oW70thlUbKMYSIGD+rhkgsc30E/0VC6Q4BTahdiJ3cX8ycn4Qg2ZOFBttfYdzvlEofG0dgo'
        b'wTmiJ1WZ709PUpoT6IakKZ6pT/j8pM0tX+e96PVtddc66lP8Vuvcz97/5M2M2LvrXriQ8mzVmz//y2+8fU7vX2E0ncp6EOE8bejc8ZdUFxND/zp7wjep19/qyFg7r/jM'
        b'oEJLml7iCQPXInoL9wQsYQmzMYRnAxTCmSE+IY8nhGY5FvByCvWQP6OvZFL6Xw8X3ZUb5FTJV4zETlMML+R+asHZV4Q6PI1V/eTzwBnjQqLD7KDYve1Jowlle4savrfI'
        b'fpuG99439FFrvr2pwi7y65cqbw2QKmzIe/zmjg8MiAr0j+/T4kPgecmHJuswVbFxPCwT4ChUraFCRu2ky6tDoEzGguF7pAwaYcN3J5Z9P49/1bF3P+8/SK4P1j+6n+dY'
        b'1vjGV7ZhC9c+A1QzpnzYcV6ukT6gqte/vkTLKZZlsFhIyKQaqDT1N8qLnCFN3jJ8TML1s9Ur575Pzcnq7f/XKqsYEBI08VZW07BgzHa5yG5Y/L1l1qHEGqGYQ0pm8jBh'
        b'klCyyT05+bm1Bi+BK4aJlILnzVvx5OqeR/+fSZAfOKti3/Dsrbus6JqwaKC6i+VQxzvYt40wS/jYKBFmCWOGCplLal5VmFdQy86v2kb9dIxX/iRX6YXnrxvVpS/+t/6u'
        b'p63+SLJfhTD2n+e+1nt2pFfu8Fu6akN46IrLWW9PTK2vM++ri/7RgxHhlt+dX1j5TdG34R+++Lc3P9hzJ+mwi8+0faf1agt7RhSvzHHpq9MMNo6DzaFQ4008beEPy1Sq'
        b'RwbE50X1Mv4EvquOVYQ3cSphWrx6Nzy/QcaZNmzAwwFBT0FjX1mH9skyNS+DO1rHuj7Ek1f2DXjcmZ/4hEJNtiOI+a+zw1i8ExceC/AUtsT08wCO4S3uxRNwUKLmksE9'
        b'JP/7Nhtdea2nNc0yhmPXkJ6Cv0hDTJ4KvsiKPntnGtlzr17ZrWVgl5RjYkTBofwP2B85M6oX3ZiRmY7o5nV/AHRjA8U7eHd4zKOhpvg39Q70VJpeGR+/WK9YrBfjF2fO'
        b'/2SmwryYPPTecGTlG06JgyN81e+/0xUTpVkvtaXkNC5rqz+X8vm5FMWnmz2XeZe4fR4odc0KL0v/47LB4Xnf1n++Jazi1Vdmm5Pe6YotLlIuu/Gi2/jxaTdef+/9e5G/'
        b'cL5fXBXwIDR23u9XFZ7aPTf4/sPCX4iLOsS69Hk/uptdHzL8mGbib89mDZ5j0P/zR1fLArwnNpx55Wc7C+ILftz4Zezhs95Gv4QRnR97Nc43Ljnn8mHGlPtvDv/5G86N'
        b'9YNDS+Pve8/0eTNjzoU3h9VEbzRMPVV0yzL6d2+q1kSNaC0Jvu81/IdvHP7tjJe+vPtRRkNA68Fm2HT7fktq0C9fn9B0cUTrgampg99purLutQU3Uka8UzXKMjHv9Xdu'
        b'7/H46xu73jpzcMa3DcrpP/6759o/GEbWPfX64uoPps8pOHR91KgvD9/9R+bXXRstfwl89fUHD6e+oBoeObGrJHin8ztfhjV7x3/yg5X3f/VazFevJXx4Mz7n/Qld+35t'
        b'EbY1nn9vy/quK9PexV0PhaLwgjEPPasb6/fMWv3euw82di41e1l976fOjvBK+MJ13PbT7h81XHzmSOi1c4ssP78RsK77p177psNbrXExxtiXWl9uuvaLkj9ueVEb8wvN'
        b'ulsfHc8/f+2NlUezvJrCbxqzf3z1tQTfSw2lSfEHxo36aOHJ5T+qUH3h1VIM33z7E/eKvxR/MTPz/WmzxoXum7Z93ceah199ERww54uEz59t+ELxxBelvw47+dWHmvgh'
        b'D/Z6XSy8Fbj4wYPTLyd8YF4+JG9PRLZfw7ahX69ObNr1wxvPvTLZpePzf8z4bErKhN3vU+Sl1/3h1B5FYf2gqVf3EUQwJPXErt0LJKqfCkExnYANaiTO0PFoDtwJhMYB'
        b'GAd2KPlWQgQ2rOuPLmUhc/x7sEWCSxZ+yH8vNxrLiZVUBqndfQT1BnEcXvHlpAaPYv2agCVBWBINtVTi41WCFtpEWvonoYBfYYQbXjEM1ekaaKXrK6LZNS0iXo4f9B8e'
        b'xOrd/7Nz2++0ozKxMjTgC4cdTVJSVo4hLSmJQ04uwYE4ThTDFTq2kfCtWiTaJGqUoouoIGT4WnRih7bsIFdSil9LkvhPSSV+JanFh5KT+A9JI/5dchb/JrmIf5W04l8k'
        b'V/FLyU18ILmLf5Y8xC8kT/G/pUHS55KX+Jk0WPyT5C3+UfIRP5WGiJ9IQ8U/SL7ix9Iw8ffScPF30gjxI2mk+FtplPihNFr8jfSE+IGkE9+XxojvSWPV70rjxHek8eLb'
        b'0pPir6UJYrc0UfwvyU98S9KLv5L8xV9KAeIvpEDx51KQ+KYULL4hhYivS5PE16RQ8WdSmPiqNFn9ihQuvixNEV+Spoo/laaJP5Gmiz+WZog/kmaK96VZ4g+l2eKL0hwR'
        b'pbkiSPPEH0jzxRekCPGetEC8K0WKXdJC6Y64iEWm76/mume8p8JTwY6IRKW7YqRCnOeq8Fa4DBZFX/YvP97izl89NYrhCtNoBzAXk5IcMNzt/33+FaYnegGfdcSIKGfF'
        b'E977ji0ZKFuE1VDOH9kh+pHMvpQO1U6C+zDlqCFQkTm10yiaa+jCyIr3g8rjXGCS997fn8/sflikGlr2sfPs4qdyxwTvswX84X6h35+aJ70SVHuituTl9N995evzQ+Wc'
        b'mbFv1Oq6LGHGTSnTxLhf7qy/+dETf1v36kuquC2vD/m8Xrfogzev/Dyw5P2y9K/AL9HnNwFfTE2YffB4954TTrMTXg/6Utf2e036dcszy9aYX3Fz2/b2g9yky2+m+M1Z'
        b'fHKZW9J5g16b+oneTQaFzjXYyP9HlAQaSUWMUygUUzpeE7ERrs628KGWQIeBMaM2dhXVtyq4KQqD8I6SNP+pEA4cUAkF0+VwsKIHbdBCH7F4eClHk9Jp5sCh2TwoBo5i'
        b'V3Scf5yToJZEDZbCfg5a0AlFQwOWqARFjCZXwBoDHLCwr/fFBS/o22mBjlE9m2AhMQROVVRmq5XCU9DmBNVuT1p0nG4UwIG+W8bNke9QC0MXSv7QtEV2dx8NohDbsYJQ'
        b'KMR/qx0Lh1ulaZAPxfM85F3XU8MimXqMwfL0jU6CFKSAqxSM67yfcaNH81rv6MgIOCG5sy/P4/n18qbIPdy7Esv1dB1bJxaoTCBU9limXIn7scjC9Q7B5JaeSwLDotnQ'
        b'uFhVCDrsUAnQOJP3B4fwGh4ISAjEMu6TE56CA4IW74p4A22Y30/2jfrfwcX/xRe98ruANTM702IHVvZlII2bi/yEi1Kk3678SRfxG43kYt/MGa/kbC/EpOsFhCe6lVnG'
        b'7G6JHQ51q/iGRrdEqsjSLaVlptIrKbLsbqXZYupWpeywGM3dUkpOTla3MjPb0q1KJ2SnXyZD9ka6OzM712rpVqZmmLqVOaa0bnV6ZhbptW7lFkNut3JnZm63ymBOzczs'
        b'VmYYt9MlZN4l05yZbbYYslON3Wqux1L50bYx12LuHrQlJ23GtCR5Hzotc2OmpVtrzshMtyQZmU7qdiNdlWHIzDamJRm3p3Y7JyWZSXHmJiV1q63ZVpJPfUAnD3aUif3X'
        b'USa2P2JiRyIm9ti9iUXOxHSMiTFRE9voNrHdRFM4e2HP/pvYA/cmtvNkYhlgYmLCxL4BZJrBXth3Jk1MN5jY1xtM09gLyz8Tk9QmtqFiYqvVxPYKTUyemdihlCmsFzbZ'
        b'dLj0wObCvz8Om/yKh5qep6W6PZOS7O/ttfXh8PT+/2uVLjvHomNtxrR4vYY9vJSWk0qRoTeGrCyqATr7EmJigD53oUkwWczbMi0Z3eqsnFRDlrnb1VGVmub1hNHhRV6H'
        b's+X/Gmsuk6RmdsQhCZJaw9ead4zIFcX/AA6rYUg='
    ))))
