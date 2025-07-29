
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
        b'eJzVfAlclEeWeH1fH9yIKJd4tDdNQ4M2ouKFN9BcAh7RGGiaBlqabuxDFFFRVG5RREXBG1RElEsQPDD1Jk42m0mc3ZmNw2SS7OQ+JpOZTE4zyb+qPlBQzH9297f727V/'
        b'/dnU8erd71XV634XPfFPRN7h5G2ZTx5paD3KQOu5NC6N34vW8zrRGXGa6CxnnpIm1kkK0RZkUW7gddI0SSG3h9PZ6fhCjkNp0kTkkCG3+17nmLg2ckWSLNuUZjPoZKZ0'
        b'mTVTJ4vfZs00GWUr9EarTpspy9FoszQZOqWjY1Km3jIwNk2XrjfqLLJ0m1Fr1ZuMFpnVRIaaLTpZP0ydxUKmWZSO2nGD0JeR93jydqIkmMmjCBVxRXyRqEhcJCmSFtkV'
        b'2Rc5FDkWORU5F7kUuRaNKHIrGlnkXjSqaHSRR5FnkVeRd5FP0Zgi36KxRePSxzPC7XeML0aFaMeEPPf88YVoLcqfUIg4tHP8zgmJgz4HE3YRwtPloljtYI5y5D2SvEdR'
        b'lMSMq4lIbh9rsKd4WnlE2qZIUEqAxLAJ2aaRRriKe6EYyqAkztc7ehX5WBEnh4rI1fGBUjR9uRh68T58TM7ZxpLBuNIBblsiY+AAnPOA8hgo55BjJI9b8KU0LfeEZN0H'
        b'8FhPWcMR5vx/WJPu3s8CrlhEWMATFnCMBTwjm9vJJw76/HMsmPgUC8IFFvStt0OvZvsS2aUYXNdNQKxRkidC722mn1IMK8c9LzRuVTiglKmTSVtKdG+eTGj8e4YY3Ugk'
        b'DA5Pic6a6YQakcGRNDdGeYv/5o7Cvxj13baX+M4Z/JyXkMGBdLzhUMO12CFZsI/Rh49vmJUjNK+X/3VE9QjO7wu0K3qs+aESoz5kU5COOM6OSKIsaJWfH5QGRYzQB0Ip'
        b'bkzyi4qBygBlZGBUDIeMIxwWQM22p9htN0AzNSbGapQuesRQ7r/G0EfAHzHUSWDoa6GuaM66uQgFpxisYyYjWxBVk8v4AC4hlJQr1FC+FGqhJHpVRGRA5Go0U53ogauT'
        b'cBk+gjIkdnAaTnjbKGTNctygwl1iNP4FhBvR5qW40OZBYXXLs1W4Q4xwXSDCJ1EWvoA7bJ605zq0w17VTLbeMYSPIi3e7cQmkY4bE+GwBCElvgQNSEm0vI3hu36eE3pv'
        b'hhwhtxRD0zQnQayfZY1Cv7FGUwXI/9aajfR/q17BWzQUUND3n6Z8lLIpPVrzarqyyk9Tci5C80mKuzYz3ZD6WUqU5rV0eUKkRh6v1jTrLnGXR2V8lBal2YCqtBEak65K'
        b'XNrQcjF4yXPl8rGyNWFfLrkXe8F1xcHuF50JLUmZHj82RMp5K3UhQXDD1YnwSg5NuDbGFuhPxM8jD1wktsfHNlvHkCEu0IqvEp6WQiWUE/52iJB4Lodbo+fKuT7eTy4X'
        b'malwBj148vjec3662ZSnM8rSBR+otOTq060L+xyZg0tO01h1dJzFmYp6kjPnzLlx9pwfZ5YOgJCL+iRbNAabrs8uOdlsMyYn9zklJ2sNOo3RlpOc/NS6cs5M1cUsoQ8K'
        b'ZTKFT90HetuNl3I8J2VP/geeJ8rFoR/pX8y/OOAL0K2ICPCPxRVxRF8kKGKiJ+wW+8yCxhVafpBSiofReOJkHmk8z1yIiGg8zzRexLSc3ylKHPT5WRo/sMBQjZfG2qhr'
        b'hbMjZ8FhYhSByJAZmIgLbNTRbcd1PnCY2GEQwoeDg+DOVDY4BMFRQQ+Rz1TlYnxVv3FjosSiJF3vjm7/1GNVyvq7B3EN7jjYeLixsDVi0r7uwsg67uV0qnPO6e9E26Fj'
        b'FfaTj7nIOaYEuBt3QZnCb0FUIBRHRsdKkBNu5eFkQna/qIbTASaJPidB4OkGk8bKJE41H/k7c2Iib7PjI2mLmfT6JGm6VL3VTAeZqc+S84MkzJtpzBskZjpd8UjMb/yM'
        b'mKm2r10cNiBkFngCOORrl5gtxofwJbyfGTec9kqHKjhksYYGixGfiuACdDnYvKiSQA90wlGednGI1yFoxMdxL5uWGALd+DA00T4R4jMQNEGPjk2DfcQl9ZK/iyzW2RSm'
        b'EcFlY4bgL8qXwHl8NIj28Ig3kWlOIjZr6crl+BRUW6BjFl0MFxLfEo+LWV/62AWwdyXrkpCuvQg6iD9r7sffCtfEuMtiZvMIxCu42ZF1rVy5jgixA9ptMygaxBFC+4px'
        b'DGKgwYJvwm7WRfAgLg06gvFtAcc9uDFgFNRbLCo6bReJ3Okjbd60pwrfksF1XMnmEbLxCQQ38p0FRPYnLDLCQdZlR7pqEXT7ZLCuJOhcjA+nQ7vF2ZGsBte5ELiFBN/a'
        b'HQB7fOY4mRn38QUEXXB4oY2p4EXcgduJIt5ygtZZtJtkASK4iI8K/vomHMb7xZ5OjjMp4XCUc/DKZDDdONw8A19ygk5GN+zjOAm0Mgri8Wl8EO+BOgu057pSXM5yCnzR'
        b'V8ClFDpxywLO4uACLRRkLxe6JEWg/LAOWqZAj9NmG3Qi0tXKTcX7caltNJ3XPB8XrJNanMxWOquGG5+1nnFZD+0K3EY4aYUuJ9pVwSmmwHk2aWLEdnwOTllcXQhLRBJu'
        b'gQW3Mix0+Ayhu1ZBelw5JHLgwqEEbjB4uAC34XaZJ+naTAm7wSlxKWEHxRB3wDl8PQWqnVxycLkYiSaTiRV4N5tohXp8AG7iaqolRIVyEDTjG3NZPNwq8cWnpUSPQ6SI'
        b'Tyc6HtmvxsQO8G1okVA9kAga2ZZiZbwfEwmN8/ws0ArtIygTr3Ih49UM+wTo0UOBu4UYjtB1mVO5j5PLWPi7FujOhfAFW8Txd7NrHLVxrHHB6NHcHD5imXPw3Wzv4Lp0'
        b'1rhT6cnN5+9nopy72evGJc9hjX5TfLhwPj4Jobs7ahJmubHGaKMvt4yfY3IJv7tj3dS/TmGNouXjuAjee6Kz7O6OB7aIUazx8IYJXDSfEzEihUy3v+7BGku8JnLxfHwI'
        b'50Yb/3URa/zjoslcEv/RQkn83R3evnlK1lgpmcKt47+Isw8mI6UPPVlj2crp3PO8TCfNIauPTcsU0t8UPy6F/2iqI7pr8ZbGZLHGDEcFCRgo0xG9aFln/UTIB3ryArhM'
        b'vmUFF05GLskMZo1X05Scgc+JR+EvWh6kjtzIGuv8Z3A5fI7WVXbXsm6rYoyA57yZnJW/7ySVEZjZHwl4Ni8P4bbyX0wRpRCY6o5A1rg2M5TL59eFiFNetNTM/XALa0z0'
        b'ncMV8AW+UjcCM/t8OGvMWTiP28u7zebcyOozT01kjdYJ87lifutULp6M1CxYyhqvLFzElfP3J0jiycj4q9OFxHVOOHeQ/4KEPDLy+RgVa2ydsJSr5gt4STDBM/2+sFDt'
        b'zmVcDR+udc65a3mQOypXWF25kqvjH8x1yXnR4p09V4A5aUskd4b3W+SA7mY9cM/XCLoUHsNd4gvGS8LvZtVMtrMKnF8cx13h39lKWJe1bnroJNaoW7+Ka+FvGMWyu1ne'
        b'Qe/OYo0FoxO5Dj7Hh7Au64FkVSwzhVG4B+9fFGRxcqSW58yFLxvF2qEzMQDa1jqZXV2IrY7kFqTGMpsTxybieqgmSWBXrkXEHIaCgNjHLGEybpLDgWTiaIjjpsZfzU3a'
        b'YZaL2fJfb7jH1Ym2BohyXsxdFzRnB2v8Pupl7ozoEkmQ7pq8t3/vwhoDHF/h6kXeSSL0oqkmr0sQfFjeq9wl0cuLncLJyFyj7Nk5ejhCwl6RbodQuuQ/sfHJfDJroRhI'
        b'0ZNZy7RY2wTyORc3Ey9aFkd2bpVQEhmjhBKSYHquhSsp4unuJoY+SUaRWLyUBPSU6DVj+/dBJuSA3Nb9yo7sg5y/Wj8O2Xwo55snOKqD1HAgjqRo9iNxN+zlt+GjJDGn'
        b'/A+GI8kkQnSQ13HoFCPuOYSvzIbjbCq+Qfx8b4y3wo8kucVBJINxzhCNwHXLWb7kFeSF2wnuBM3SMBTmpjRTtglJugdZKn8TR/de/xLrKzR+s0yKnOd8xJH9nHPBlEDE'
        b'9CIf16xRBVMV0+IqpIEjuNlGd4TrxmxW0/Q5ahHhwQEoV+PKoEjc7EdmWyWuW2EPiwBuC8hGJIRiWkscezVKhfM5bDo+D6fwNQXZmbGd73Q4SXZqkWI0Si4iCXkBHBWi'
        b'1TEghNNdCXXmN+muJA13CrElCtpVuI2Sd2wCPo0MY+CAkFKWeXAqFfkw3wWfQhlTM1lKqZyEu1QqItFYJT6LNsHeHEZdykQ4ogqlzpjodA1KGwPXWO4MJaOC1FFQDmWx'
        b'glxcCcLlOaI5G3ELW34qwntVoXT142n4OAlot0iM8qUon4BTcBbvc1ZHk6lBUKHgkNN6Ej5iMuU8mzoK752hCiXpoYmMO4HSyVakW4j2R6AFylWhBMsZhO5alJGAS5ic'
        b'RZ64BcqIAnSQbU2MBInHc/gcvgNHGEAomYnPqkKJffiTfKIOZY6BNoGKI3CC5HdVcElBRQMlsbhZjJwXiEZMDxP4W4lroUCFO2kgxyfwGbIFx3sEOmrwMZJ+lMEJ3BJN'
        b'OCFCIrjDkeEdFlsM6Q9Zj+st0ZGRMfSUg21N6b7UTyn3j1HKA3lH3KAj+48LuN7PDzd6KuS4GopwE9QrRuNqTw+o98IXeZKNjHbDZ6xBhm9/+umnH5yJTiZlSYlOBtw2'
        b'ThZyJxns3aLIw8WxgRFiJA7nyO60ANrkoxnDlhhwpwUXJ7iYbdQzneImk3ySydVVkwTtO2JdhY5OTj5OzKxpFvTgCiDmNK5/zh1OQXKKq2wttdpswSfxYTJL8GUT4ACu'
        b'E1hczI21ZKRstjnSvPUmJ4PepUwyo2GvxAL1UAOdudAhYfnbRJIdX2D5xep0Ird2vHc06XPhWEo1M4/oKUtBL8x1ctqMr7g64UricddzG6aAMIsmMRstcBpfsjrm0ozx'
        b'NjcWmvKFFKiJ5Cwkg74hJX10ud2cjCRTFwVxFhsSoT0v32qGDpq53uF8XeGYAPPQc6st0GbFBV5SxBHDIFZ7EfcIetfmihuc8qDV3oVsPUSzuQg4J2UAd47aAO1B0G3b'
        b'7EyxP8FNJyl/l4D+HSjENU7rCbucyZZGNI+LdBjNUBwB++AyiRdnoGKEmeSfIlduNrHdFobHaML+csKSclw6AtpoqJnELc4TsdXMUIkrLBYo2cyWw53ceDi4SkC/2Akf'
        b'tXjhAkdBbFWE6uNQyzCx4iYnJ7IJuM36RO5ccCzJhN1IT3Y23g2HiTnNdwpAAbxeSLlvEFUsw2UjHEfhrs1bOCQmqR2uwFcTBGaU67OdpuHKR1SRdZr0f/d25i21xMLC'
        b'qxZsrFoQ92a42/6MLW+EPv/ttO6yykrx1YsVe10dJr5i1ft93nPIbWbYx/kfOYZsWH7o+Z4VcsMvgs69HPSyKcJnxry39mdtyTi97ZuTx68rcl2uH7+zNUX26ovaB0EF'
        b'h6Jd017+sWpjje+nJ5aKAgPuJLo/d/+i9tLmr0d/GfFc2ftaa4v4E9nF3E+2r89y1pYljPynKN3cWUdjyjre+oODz8euF4+91fZtfFzj4RteHkfH7fCL/u6VNXWz7wXv'
        b'8myTv3etqjmis6z+h+kPY3fPUua5/8kzsuL9+HO3706peq1++2bTyJsbHu479OrxsB3lsaerN8o/XRm6LurY+8te/tCj6Pnfjjiieah6dWH5bNfqtZ+YH7R+cRXvtLun'
        b'bHkl1GFc66dLv9CCERnsNJv+tPo3u3qKD4w6OLvz7bt7eppfNXvd+cOxGffXnnb7tuOfk+Fv9zLqZslPdsxpfWvb5LcuhL4/d8PGcdNn1p4qXHr1ZOuXHxtebvzNTxP0'
        b'l79qv7qz4su7RXOTznR17/n8yq6qjz5O6rGuKlT7bfxlbfmKQOXz+xTfr/IMuj/qh4Kvfj878LcNY46I5fbs9IfEmfNwG/fMhbKAWOKToJLsiJ1wE3HBuMadDSHqeRlK'
        b'FcrIAH+5kvRDCULe0LlCJn4B9oVYqV1nQJ0cyshGUzgi6j8esocqK1Vxx3x8RqGkx7s+UELAS/EBPhDv9bFSXfVKTlQH+EVAhZpD9tCymiy9ja5MtesFEue61ZEx23Cd'
        b'f4wdkop5+7RkhtNcNzhE9/EEHlzUkO1QOVSK0Kh5IqiFonVWlqLRaFiqjgtEqcQ8tnCLV0fK7Z88o3jWQy55dv/jcw134VzDatYYLRrh/J4db2ylOdESR86ek3KjOWfe'
        b'nnPmXHnySUTb3DlHjh522XOO7O3OSX8S0zfvRv4aeJHPvKvwmXe0k3L8T1LemfzlybsReGKpmB2XeZKnlLy8CXz62ZUzO6PHh2fOg1EbdKDybOrknNllgD4GaikaOFrp'
        b'Hf3soxV/0m/Exbii/3AlSE6CoCL2BdwTrRSko5CilfiKHa72gHI5JzjgK7gONwfCeXVkAElmSLaGa0eHPZW5ugwklvGIZa70IB89fZSf7vIok+X/oUxWRDLZvXLxV9lk'
        b'AUfZoH/xVKoWmWboFQy719mWo5PFJM0NCZaZzOzDTOWQqUP+iLTKzDqrzWyksAx6i5WCSNUYs2QardZkM1plFqvGqsvWGa0WWW6mXpsp05h1ZE6OWWchjbq0IeA0FpnN'
        b'YtMYZGl6JlCNWa+zKGWLDRaTTGMwyBKXxy+Wpet1hjQLg6PbSqSvJVDoGMMQUOxMVRilNRm36MxkFL15shn1WlOajuBl1hszLD9D2+LHWGyTZRLU6JVXuslgMOWSmRSA'
        b'TUtI14U9G0Qg4WGazpxs1qXrzDqjVhfWv67Mb7EtneCeYbH09+XJn5j59Bwij5SUWJNRl5Ii81uiy7NlPHMyFQEl8/F6S0iLQae35mkyDU+O7pfV48Fqk9FqMtqys3Xm'
        b'J8eS1lSdeTAdForI8INTNQYNoSDZlKMzhjF2kgnGdA1hvEVjSDMNHd+PTLaAyzKdVp9NVIFQShk13FCtzUw5tO0xNmuhPtNsMw47mh7Gh7EngWnTZpJhFvKXLftZWGsN'
        b'JotuAO3lxrT/AyinmkxZurR+nIfoyxpiD1adkdEgy9ClEmjW/920GE3Wf4CULSZzBvEv5qz/pdRYbNnJWrMuTW+1DEdLIrUb2Uqb1aLNNOvTCVmyIMHrykxGw7b/UZr6'
        b'nYDeyKyUOgpZP2k643BksTuMn6Fqic6gsVjZ9P8bRA1OJcIehbPBseiRv8sxWaxPAujXDJ1Fa9bn0CnP8txU1jp96jMwppHLqhlQrrUkcpGlDIZnaFj/oo/Vcehaz1bN'
        b'/zDfzToSRYnRhcmIlyEjE+CWNitVWGC48dQXEeKTs3SDRDWAEGGBAW5ZLDrDz021kgD/DCb2w6Ejhkf2qYirthnTdMbhI2b/siRGDhOrhy5MxvwcjIwtQ+PuSiptqE+3'
        b'WoinSidJDO0ebmKOmQiA+DzN8OvG93frjIGxZuWzsB+y9lN4Dx//+xXhiRxgyORn5gPCXD1ZeviJkUsWxz5b7ZJNZn2G3khV6mkfEtffl8oUkhiwbIVZl52W+0xbHwz5'
        b'H1BoYfh/0Jlkaki0GdblrdSlwi1i1sP4hP8BxKgZMDujfm4IXkmk5+eNzajJ1j32dv15scwvljQPq6c2cw7Li56asUZnztUZ06hZ5uXqtFnDzbbocjRhgxNrAmBQVj/M'
        b'jA1G48Yw2WpjltGUa3ycdacN3gdo0tJIQ67emkmTdL2ZZqk6s14r06f9XIYfRja3mmzqNglOSZlPFKQNnRjWv88JI/uC4SLD0NFDrg7ozs4TPXl1ECGU+BybTMvGtsbZ'
        b'oRTn5rBZwsF7k1qC7JH3KlF4SoBykUY4eMc3Y8h2sp1HaihB89A8fEa4Pvoy1Q45I7dpzrIUZ5fZi/oHF+9KZsfk/vSyFGlx7S6bjPy5YhnUKjRwSdi8Dtq5TpwgGQP7'
        b'J8mdbVPYRrcA10FZUFRkIC4NiopR44KNgVFQoY6VoBlQIVWsgRPsRDkJHxipwA0RZMhAvzs+JcItuHqLjZbz4f3QmkpPzvENWrQ0cHqeI5pjgQJ2/ua1EU6ro6GZH3o8'
        b'ji8FsXPnqXALX4KyeXBaARUxUYE8soduHpfChR02WvsydhTuVs+DPWSJSChXk505VAZFQIUITXAXQw0U4duMpCTcOYPiEYkP4pPCQHpfU0IvSaYoJPPhGD5lm04xPiRP'
        b'V+ND+OZjiHHs0KcyNoZDcnxLgk/gErltEh27Z+12BjQMmgcWp/cWZOCUFEk4PsCz+6GxcnuFEioIIGVUDJQEyKXIF2rF+CKcwudzl7OyDU8DoVAYhM9mRcZAKR3m5SEO'
        b'xoegkgkPenwnKLzg3LDCewEuM8mroBG6VDOJni0Zg4+hNHzRR6gubErYrFDsekpQUAiH+g9w8fkE1UwJQuvhCK5FmfgmvsFAqqEA98JhOzQSF6BgFAxVeUxydvjOekp9'
        b'AC2bGSTZEX7sKDw3Ai4SwfZGDhWswV/Os8ORqficjwrO41O4LUeKuGiEr+LdcQyXqSJ6C9HGDnqhF59CWdFwh5FhwNfhIC3jsw1VB0LINblUIKTHn1fh6vmqHBHi1Ag3'
        b'4y68h624C9+CJpWLhwpaJIhLoPUDJ/Bu1jUH1+EjZJZFZSaz4hC+BuehWTgBrlyBz6ugaKwK2si0NQh3proLK3XCRXuViiOfOlbjcygL78PnhTknl0K5SiWh9yZwAJ9H'
        b'BgUuZObqq/ZCASiYk8hS5svznZBQTXEbrkK9haPH+bvRcrQc71/CRpcuGolkKCXOKSfFUL9cguQiwaq68RF8Sh1MsCyHCoG59lDD4yMjoYmNGAO9cFStDITjUO9PBY6v'
        b'itGINSIDtMAphmI27tilziPioZVgYjGHT8P+3H7RbMVN+JiKiL3qERNXQT2b5rzOVwVd0x+zEJdDI1PPUbhwtnrJ5mcYYp6CwKbatBQK1CqV12M+n1jCANvw/p0qfE36'
        b'mMvecImZ7uZE3MisjHDy+nCmewTfEhR1ES5l4iAW3kTl4RvPTHorMe5raiXe83Mm3eokiOKK2yYmOCKRRio4qBhhm8psPQQfENC4g28MZ+3luFpQiyo7wj0VvQw8iC/g'
        b'08SU6nYKRQFhIxDR4jyX4JSAFJ0ayUcLbuSWFTeoIwNjlcTq/QbOen1xkXg8rsENgVAuXAzvfR5fUHDOtJQxMFKMHOx4fABq+m9S4CQ+Mk5NNWKQRGsnCRd/p0bCJTU+'
        b'OeVJdfHCTcyU5TLcqogKhOZV6kD/WFp5PCJDpIMyXMokAHc4T7XAsf67XcI6enfoGy2GNqL1VZu82EBcl4sPqRekDxk76B6YBIYKtuAiwyYFNKU95Y40nowjsVDFq7fD'
        b'JXblig8EDRrnr5XgpvFZQonS+dn4ghrfee7RdTm9K5fEMI86KdFfAbtFA1fKg+6ToQhKBKd4B7etozJdnjjEg+G9JBhQlovt4QzxYTeDhvqwMGdGBOxeCPXEGRXg64Ov'
        b'RBNxvU1OukOg3V89wHES/SqDoFQ0O5reH6gpi2fiY9JIfJ7EQbqUCQ4sIFTABbgUERAVFyhFTmoeTi2dwZaSLqKXtnAMDb239YGbTPjrcSN0EE6dHTvoQliRJ6jNAVyI'
        b'SxV+C+yHFAUcVrGLdyjbQKxjoHYB6iyPyhdSxNNJfLrMVHozXMpW2/Dux6qFry3vr1aAlkkKtdsQpcSF0M1u3PBF+3lOPBqdQFKeRFwR0H8lboUuqm1niNYPUjc9vkZ8'
        b'BL2zD/XEddQb9uJm6g19ZgpOtX7edida9EpdFTQifHQn8d7uTPcTpbRsNAT2oEAUCFUb2UJQIcd31OFLn9R6E3Qzc1xBnm4oU82lpAQ0emQjllAo1uK2Z+n6LnwSVy2N'
        b'Z45ixTSohcNwzA4h9wW4EiVDay4DsFOPj6mhd/KzdFeHexk5U3BXPm4PFtGLHFyGLyGTDa7Y1lK8z2yF0xYoi4YKqPCNXBWP24ITE+gXCYJW+SkD/YgU/fsv2hOpuygO'
        b'WBNB5cdu9VdFBNAe4kTUq+OhQky4uH0kcVWnOHarnj9fTHLL++Mcw1MM1+YmICGzuAPXcOUjLcC3Rw7WAn1Mf1iAypn2uB2q8IkQGrFXEWWEtiihqzuH5HjtSlwYksOx'
        b'wHCVx2dttO4idjTsg8O4OBIOwVGoxsVbyKOCJD+XSdhuDsVXJbgtNcGaiq/P4ogWSZ/znyyAPACFWbjdCcoegYTOZSQCMh2qJtBaqL3U4xJBttJk3p8ExmrhVvcc9I4g'
        b'8W+uZGj0u+XIuo0G3KReb35SMaBKSCHWPkcCYDsuCH1EZzKcZ44JinN3DJfLwWnoJKZcQiRIwy/cTljcP0yEywZnc3bQLRcLkeas1aaaAg2hm0kkjCLURcMxoaMI129T'
        b'hVBFv+JBcjjdFhKy2YXfbri8TeW4LmQL4Uc4wo2SJMapMVC9BLc7TA+BFsRCZxsuhvaBO6hWfNyZEFM2PWQG6V2BSMJV6GlbQuHdWrDFiehYGWFjWRBUJkKLC24NmREf'
        b'wXSPKF5C4JqEJ/Rp4zjiM/BpRzgBFUL2QnxgWyJukqIMaEf5KB9OQatQjnQQ355AOFmGT4TiVh7xnvSq9Sw+IRhtI64mFt4kQS+MQjvRzqylNlq6PTUGdltYjX6CH73/'
        b'rIGbzA7XDlHqtYF2JAWqXW6bh1iBRE2UU2wMVASu6bcSKFkbEbV6NvGlSQJRuDEeimMClbHRcRLilqDFEe+DfZ79DiceV5EtxWEJis1CSqT0E/TddyFhzWHcTNO4TrgF'
        b'x0l+tiWcTGEibtqADxMNw0QoQ3SMMLxK0MHDaLt68bQnlUxCwjn12XOkOmgPwQW50MlqQbq4EJK3nLAF0qnXCdt6nwweuBsOPRE+oLK/OBt3TMdHLa7roDNnhJRAK+Gm'
        b'wek1Ah5HcTeJCwfwuVmDIwt02bEIsGkKrh82+dhCrKlhBy5nZWL6fZ+ckFjSycd1H39gS4qp9F3u1vyjd+UvT/3h+smpvnbtUyamzXZL2R0u83bHe9xWzkEJuHHZwfIV'
        b'Bt9m8ScfuDmFvBeSkTax8hfcRFe/DNeRGbF13zr8UDB27hc9924+V7Ls/PGdf++5ebnnk99Wpy+etcNkTJBdOPPFpjUvVqcfu/zevQ9fPFrS1XBCn9v6m7deS2p5S5kU'
        b'4+3yqYvjvd9PSP54+/bJLSdimv3f/ZEPNTz4t+97HCIz9/2ma87xzG+a1n6+5fi2l5on/qp6UpzTp6vHrXrlbz99OG1z2OuiK54XU867+ObuKP3ydzV3338n7J3PN79x'
        b'8eF7P/5FPj83y7ZRG7dwWv7ae0kd7zvHN5T1bk63nfZ/PwxfdXho9+BUy5fuN7tf/1vz+HuXfnNwa/CvVS755Q8PBSam/OqXk07JXzjt2/3vk80/jmrNG/tCUOHv3V5z'
        b'yOXfnJsDJdJvTuZMf9Hl7gLH124s2ucbuWxeyoRRoR/eO//HXzX80i7tk8zX/giVr7+x9NY/fXDQM9KlzLhD/5LS1Pm7N9NFnjtq4ypKHk5U5N292PpWcO3EpdE+5pz0'
        b'cy8u2F2XvnnsirI/tzT/zevPpa6poaq3Szy/+2yhJOkXua75cSf/PPbzT0K6XYqnvlfzYdHNnYb0H6Z83vyHoIXHVNsavjG+9Ipy7SxrA0RFrGr0ePvkSzdeq2hYc2tq'
        b'btaXna92jYkr8zxdNM1560fTrqTmR3VwHkt2/elS7x+Vf/17x3vb38hKewtt9CsJ2moZ69PTcOLvPzi/lfH+8/4fRtVtd10d+vnFtpsR2+xuuWY1fJVVFpq6+mXjss41'
        b'xbPPNa//91e/XJX4A06YF1T64YT6H71GeDx0vx+6JtnzYa/H5HfUe3YF5RX/yePtv36QeLv8mkfI9/Grt+Qt6fnL6o/v7dqtuvN808cR97Ncyk4mPdflqHi30JfvHf/L'
        b'B7/64d7O53u/fse44Nu1y3Zt9li4KGzTxzuvnlkcGBY7Vp30Uew7TXdPFj8X95n5rYovl7/24YxPLlQuvfZZi/+GO3a//b3Pj1GzjUU/vjF9x+vfrMrIP79kf73cecn3'
        b'Ez0yAnd0J/zu2ufy0rjjb1f63/tqhkfeh8UJ9W8c899dpLBUbHL+9vIvblaM6fgu5uP7XLIo4w/j/v2tJUV9t+e95PPOxjcXHr/zumnl/AN9v49xO9R17OX7NQcnBvZE'
        b'vTl7XVa1Vuv6zYqVqmlH1G++PuK7ef9iV73j6wmqVH3Ulgq5q5UeHeBaixerLCkJwDcziHVSF0gs2At3iiMc3FltCnTEkXxqLe+vlBMTRsjhOR43kIDeaWV+qoA4/AZW'
        b'3DIPjj+ub5GJX5BsZ9UrMUvgqkK5mDnYR8UrzfgC63yeJmFqOJj6qISF1q+s8bGy/Pl6xhwoC1iFe5+orPGFI2zAVjgjUkxH/XUsg4tYdtoL37lpI4heVECNe2xMQBQc'
        b'QAR+N5+7CVqtzKs1bMXn1EE+JNEoDSKOUZrLK/2nWFkGcHkMLlETlODWmEdUjQgWZYyfxMpu8J3FSTQ/KFj1OD0Igx5GVCzxbLUKpQFXCxyT4iu8KgE6GUp2wVCtiLJA'
        b'zdBvAZmglEkEakn0OAvtRA4k3cpclDPwfbL5YhGPb8pH/aMVOP/Jh9zlvw7nqS8uZVvnhgSzyp5wWpyyC62z58T9L0dWxUNfYo7nnDl3Wp1D/nfkeW7Y198cXe1Z9Y89'
        b'580qeuhYb/K/69+lEkdu8EuA4irMexY84fWp1MuVk3G0RkjMuXHeIjfOldUdibmx5DmaQHHj3X5y5KScUGUkZhVFZF3emafYuAur845sTfLmaU2SlKflPpNIi5RiI+BE'
        b'5kp5oYbJkUD35kaT/jFkBTqD1ji5/igVCxS48gMVT268K89g8OYRVMcGSpTE9IB5UGnSf11+cs7sNiBBtlYVlRzd86IC9MWUZxcxUX+wFfeu7K9hgspAmu6RBDJ7So4I'
        b'up2nPvVNPaoN4RQ6zdh09BvkaD2fxq0XpfGsuEjU58ZOzVlFkXm52Wwyfz9BOEdnmmXuLxDSpck0RpmO9itj5eI+++RkevGQnNznmJwsfFWcfHZOTt5s0xj6e+ySk9NM'
        b'2uRkQV0fPxjZNGurJNixejR7nu288GVTppMrdFmdHCiBgWZimrVwhplnEJyWSl5Ik3Mr9Ldm1ossPmSuX8HRBZXdsRDvtvztL6se/C53+hXN2xM/23Dwo2+R4xn15vem'
        b'JTjm7FtWGHg7Y8qPsgn/bAnPPNGde+CD1/K3/Xnyxt9+t27SL7/+veXftF/t/fXX0bk7Z8V+8LGrcf67k/7y+vvr9+TLvvhc9XqO9qFtdOQP63a+Mn3Gx1GHjrhOKlsS'
        b'oPpmebRjYa+L/oXvLl+GWZ+cjTmU8MeG0Fz/iz/cP7dk1l8Si8bYxoTof31hafix8ZZX2+9OUgf8a8a+1f+2LqMwpvNBetHGrx98WLD0gHf0w8b3akbFzn03/5P6o1Wv'
        b'zOzWrXbaqLwR0n3V+NEe46fnIu98fzSqZtuqI86JM7753Surrm66fNQRz3zjzSkvfP3PRfcr7F4MhGXB5Z89OKDzd6vEI3ahJd+tCfjiolzMvG+MGqrJToBD5L9Obg7d'
        b'kfVALfOCs3Cjnn2n9tH3aWnAYd+phQu41so2wtC1HFrxfid/4oCp8380dgJuF8M1OJRjpQmoFW6TvWAdlFpwc0Rs4KMcdCQcFOGWRHyD6DtTe/f/Rq8qZVnusx/MWxKt'
        b'NZg0acnJzFUupAbiSd1WCDf+J56nhYrEOfJu9m52g52c+Dupc78Teyi1Hx1HnajfLpTPc2avAaUmhsQTTX/sJUb+95DJmb0fmRBdnIpZKH78TPlsv8EykQLtVLKTq4TK'
        b'1dAAJXHRuARX2iFXH9E4aIFCfdl5KdkfkIF2e3rH3Zvhuifcbf+vd6XnulhTG/a/U+J69hZeVnu9vfq197QmbvaRby97eV4+8dWvN5nevvLdH7Mc3/7zhZaIWb1R//rT'
        b'5aKjbisu3P+1Je2dvZYP8JFfvPyLP81YduCvfzoRuGXtTz9wL73u3VUnldux7GY9LiX7OPo917itRI3o3siOBOw2Hi4tTmUjJmTCTXVcILTSMXGBPFGrW1AAZSJ8dpkv'
        b'K7UlTjBfoMw2ih6f4QpGmLtoPL6Jy1mdLpyfCrfVkTHLIwfKdLfhOpbhjIXiOWr6ow1JuKf/Rxuc5DwcxLfgtFBcfA4aVexnHXAP7h38uw4k3yoUoO8m6cQhRZQEF8yg'
        b'p+1kmwiXB5R+/H9zPvGf1STxz5qJ3qi39psJPSJALvYDNcGigF2IvpDZ55Hyy/pEBp2xT0yrT/skVluOQdcnptesJHjqteRJKwj7RBaruU+Sus2qs/SJaRFKn0hvtPZJ'
        b'2Leu+yRmjTGDzNYbc2zWPpE209wnMpnT+qTpeoNVR/7I1uT0ifL0OX0SjUWr1/eJMnVbyRAC3lFv0RstVlp21ifNsaUa9No+O41Wq8uxWvqc2YIzhWvuPhchX9JbTHNC'
        b'g2f0OVky9enWZBbX+lxsRm2mRk9iXbJuq7bPITnZQmJfDolkUpvRZtGlPTZvgezxZvpVI/MM+gigD3rCZKYu0Uzvbs307sJMdchMj5PN9IDdTE8HzPS3RczUxZrpL0KY'
        b'adZqprpuplXKZnqKYqYma/ajD3oGZ6bf2DLTawwz/faVWUYfVH3NNJU2z6KP2fSheOQdqHQcHnmH71Y80zuwkd/bD/wEQp9bcnL/535n+f2Y9KE/ESMzmqwy2qdLi5Xb'
        b'm6kPosFeYzAQF8i0gp529TkSkZitFnqv3yc1mLQaA5FGgs1o1WfrWKZhnjvAyieygz77+UJOsZDmLyx3EVOjFTTPbTTB2p77f5c6jWg='
    ))))
