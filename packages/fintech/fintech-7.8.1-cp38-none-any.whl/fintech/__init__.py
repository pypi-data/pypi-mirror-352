
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


"""The Python Fintech package"""

__version__ = '7.8.1'

__all__ = ['register', 'LicenseManager', 'FintechLicenseError']

def register(name=None, keycode=None, users=None):
    """
    Registers the Fintech package.

    It is required to call this function once before any submodule
    can be imported. Without a valid license the functionality is
    restricted.

    :param name: The name of the licensee.
    :param keycode: The keycode of the licensed version.
    :param users: The licensed EBICS user ids (Teilnehmer-IDs).
        It must be a string or a list of user ids. Not applicable
        if a license is based on subscription.
    """
    ...


class LicenseManager:
    """
    The LicenseManager class

    The LicenseManager is used to dynamically add or remove EBICS users
    to or from the list of licensed users. Please note that the usage
    is not enabled by default. It is activated upon request only.
    Users that are licensed this way are verified remotely on each
    restricted EBICS request. The transfered data is limited to the
    information which is required to uniquely identify the user.
    """

    def __init__(self, password):
        """
        Initializes a LicenseManager instance.

        :param password: The assigned API password.
        """
        ...

    @property
    def licensee(self):
        """The name of the licensee."""
        ...

    @property
    def keycode(self):
        """The license keycode."""
        ...

    @property
    def userids(self):
        """The registered EBICS user ids (client-side)."""
        ...

    @property
    def expiration(self):
        """The expiration date of the license."""
        ...

    def change_password(self, password):
        """
        Changes the password of the LicenseManager API.

        :param password: The new password.
        """
        ...

    def add_ebics_user(self, hostid, partnerid, userid):
        """
        Adds a new EBICS user to the license.

        :param hostid: The HostID of the bank.
        :param partnerid: The PartnerID (Kunden-ID).
        :param userid: The UserID (Teilnehmer-ID).

        :returns: `True` if created, `False` if already existent.
        """
        ...

    def remove_ebics_user(self, hostid, partnerid, userid):
        """
        Removes an existing EBICS user from the license.

        :param hostid: The HostID of the bank.
        :param partnerid: The PartnerID (Kunden-ID).
        :param userid: The UserID (Teilnehmer-ID).

        :returns: The ISO formatted date of final deletion.
        """
        ...

    def count_ebics_users(self):
        """Returns the number of EBICS users that are currently registered."""
        ...

    def list_ebics_users(self):
        """Returns a list of EBICS users that are currently registered (*new in v6.4*)."""
        ...


class FintechLicenseError(Exception):
    """Exception concerning the license"""
    ...



from typing import TYPE_CHECKING
if not TYPE_CHECKING:
    import marshal, zlib, base64
    exec(marshal.loads(zlib.decompress(base64.b64decode(
        b'eJzcfXlck0f+8HPlAMIpIh5ovAkhgKCIiopngXB5K2pJIAlEYoAcqBgUBA3IIXjfgjee4H0fM7237fbXay3bdm237dbW7W53t92u223fmXmSEA6rdn/v+8cLHx6Seeae'
        b'7z3f+c4fqS4/nugvAf2Zy9BDQ2VSGjqT1jBNjJbVclq6gmmmMwW5VKZQw2q4Skot0gg0QvRfXOJjEVnEFVQFTVMLKOMkjtJ65HuaVtJUpidNlUg1Iq1nlpdGjJ4S8tmb'
        b'PH20nuvoBdQYSiPK9FzsuZBaRBmZhejbHMqjUubxaIDn3DytNGOVJa/AKJ2pN1q0OXnSQnVOvjpX6yljH4hQNx+I8YNGj3Y6Iod2Gw2L/kSO/+Yo9LBTOlqDxlMpLqWr'
        b'qAqqlCnxtNEVqMcHmTmUjamgaGoNvQb3gEI90MnYtBz36cGVjUV/vXCFHJmiOZRMmtZO/R2/nmvAXZGlcENMjB+aSFW4KLCI+hNf9q+TW6gee0cqG417x9gpO6tjXT2k'
        b'n9jDvK49dFbcuYdcmjUSfQZ7wMG8OR5CBdwOG+bCqvD5sArWRM5KnJsYButgrQxWw1qWmj5PCM9OBk367//1FmuWo4Lrz330teorlUH3UPXKF6ZR4ZvD1Inqh6rXswNz'
        b'8nQG5ty6vnGLqXVLReYRO2WMZSgqsQiWw0NeqFY5rjPVqggDN01wYyRDDQLnOXg2CZ61hKB8EYFhoAZsgi0z4SYlygjqwCYR5RPADgTHh5k88HSy7UyozIQhk3/gxEd+'
        b'8TpTQYnWKNXxQDGp3UdtNmtNlqxsq95g0RsZPAFCPB19JbQPbZI4i7aw7ZzOasxpF2VlmazGrKx2r6ysHINWbbQWZmXJWLeW8KOFNvngz174gSvphyvGSdSXfoyQZmhP'
        b'8rQOQSnWPhZleEQaGmx1uvuMhifDmhgBbBlKGXAXXprwKv26gIpr0LxM/ztYETiVIoAztMjKWMRUYYK6UfdxwDWhA3DuTyZva0vycx/QxwWUVDVh9xAPvsigLGZhLIU/'
        b'qQzvepXyiTPmi4xr6WAK5ZSUr9ZRVgVK7O8N673A8XDUoSq4aU7UbH7pwZH+oRGKUFgVGZaUSlNLFotTpLBRRlsHozKwFV6Z4IWGo1R4hsKN4Cw4zlH9wE0OHPUBu8Eu'
        b'b+sgnOuSFV7GixiJhgxq4LUBeAm90hm4GR4CTVYpzrMFnoPbyEp3XuYkWDUQVE+SsdYglO35NH+lQpacKqCE8CQ4MYcJgrfBJSue8gWWEUoypUlJMrBJwVBeYCcDj8Pb'
        b'gXwD9XO9YU063JicGgGrU8BJjgoAe8eBChaWoZ7vRA3gWsC51QplUniSgkClgPKBG9nlq9Os4CRpn4MbQDl+L6A4P7CBo8EBDh60DkSvpoSE8qCcmgTrZEmoeli/Gm5h'
        b'wTV4E55AE4ahOR00UsroGJRDCevTUS2+8Da8MpidABphK8ozAAMRWG/GeZJS+Sw+sAXWwzPsKHi8r4zhZ3QLBcq9QJN/IlquQlgDa5VJaMSBcC8Lj2YMtA5DeQqmwFNe'
        b'sD5SkZxmxTmS4EVYnZ6C843R+C4WJg0CF9GgcYvzQFkkrAlPg/VJ4eAKqIsQosk7z8DzoCWGdBvsAjcny2F9ClqccJkiWUD1godEA1m0ao1SAtjwBNgJDyrTFUlytAbV'
        b'SeHJkRGJqUIqvBgepARw18IhZHqL4J7puDNy9BKUF0bQlBc8yMDLCQnWMFzL+tLRSvIeDz4jVAHOKBVhaPS1CCIzFEJqGieEZeA6PO1otBcCoRo8rFmhofLEFFiflpI+'
        b'D2cMHy+YAa/O6kT6GHfivJdQezuNaCpr5+wCu9AusovtHnZPu5ddYve2+9h97X52f3uAvZc90N7bHmTvYw+297X3s/e3D7CH2AfaB9ml9sH2Ifah9mH24fYR9pH2ULvM'
        b'HmaX28PtCnuEPdIeZR9lj7bH2Efbx9hjdWMddJuq4hDdphHdplx0myZ0G1FuB93O7Uq3fR2UpTPdXpdmxcR0HDjmpZSBqz2SFkxX1DkEbsC+54CdYGKaQjbWqABVGMsC'
        b'VCw4A4/BRmswntRtsBFcgDUIRlmKgdtC1tIJoA3ssvZBL6fDgxPkMxBqt4QnIhQAlTSsWAFuWvviyg/A0/CmXKaAVQhq4XV4WQhOMHJbL1JyLTgE9sGapXi5wtG6c0k0'
        b'uLliGmkyA71rVIKTWoSY+JUHDY7AJoTXuNoR4DQ8gkpdBtWRibhPXCINzoMD2dZA3Oj5QePkETKGYsBeFlyiM4PAdtIe2A3PDFGCEwiVhRTYAc4KDUzosJX8ECtAtVhJ'
        b'JcKNEJEb1OBQGpyeBg5Ye+OCJ8CeCQQGaYqJLAH1dErBKFIlrHsO7FESeAunKXWBMJbpA/ZnEMIgBQdhhTwZIWK6gCpQCxMYn4mQnxe4AZ62kApDFTQmmVeFK5lRU9Hw'
        b'8FrOmQ32I1oQikYQFWSkJ4EzSXw3DoDL8AqiwMmoG1nBYCc903cSQUZEDo7oCJbIMDKL0azvBrcZtLCbQBWpExwa3xvWpIYjkC+BW2z05LFxpJOD4GEanIQb8Qs92AvO'
        b'03PXgN1kbP5w40olpgCwluOnqx/jGZ5MuqJdDs/AmkRwGhVbHVdKz0RIt47MPpp0eBhRVbRoTKkEbKSfG5hAiOEgRA3OI5KC65NHJKFpiVySJqD65HHRYLuMp7SHA8BZ'
        b'pRxzjWS8rB5JsFnIgG3ZC3MYN7jHoN5ZCEIikJ12CUFMFRJ5SlmETIwLmViCTMwa1oFMlU8nBLFp+qDIENo8CSVM7fe3r1WvZX+pqsr9Ev3n3q5N2O2RGEPrdVLvFxaF'
        b'ey0sj9++vrZWEpLwL13D+EuR3/tsUAnflFDvPPBZWw5lIiLjIPLYMpHnabAuXQZvIDpWl8SztqDhHAv2B1kIG92M1nprV+YHawOJmFMBd1qGYxCDe0fPhLcI+oanoqqq'
        b'O/IOAo0cQtvdfSz9Uc6UyOA1s3G+dASqoB5n8IQNDDgf29+CVwetbzU87siQEgGqcY61a3xYdrAa2C0YRVIRBp6WKxIRq6PBBQGCsgsMqAyItmC6C+zw+DjSDwdLKKIR'
        b'U+B7MjxMkB6x2CGYdRGVSCoRlNq55WpzPhHBiKS0Rkzzvz60J23q5cwr49pZjdnSzppNOSZMAU1+OJXpqBJ9xoBo6u2smRRe66q4opMIhpEgZpYN1oBrVCoCTiHFhSPU'
        b'B1eTHi94R/Mwx+iYZxC7e4Q4rieIC/nsNGXGk7pj1favVUvuvHW34cV7dxteutDQ6P+Kj070u/uvI0VhHPfjf24jyRkjTikCllolAou28FBEEJU0JQYnmVULQSVZXHhz'
        b'iLwHOSrXOhBsAcf4aWV6XhOrRW/oEIvXUmI/2hREdYjFbEH2sp6XAQnBwa4VwEWqcDU4F1VGPfJxXwNMbYqGz5dHgKNEyELk10SD26AJ3Oy0CLTjb46zQzZe46LT+C73'
        b'dXW+YwQ+xoKsgmyd1ZyjtugLjLW4KCEmjDUUPRMQsdkPaxaVQDI/6clyRVoaFniReMFScnBeAHcjerb+v+6Hh7MT2ga3LhDUOxaJCSNpGmwGW9KwKBkAK1hwE26a9Hgo'
        b'jMVQSGM4RAog998ogDTVE+0TdM7kpLqDXG0TqmvnXG0/Dd3tph7jtj17woKwLD1rVuJGi4+d/PSB6qHqS9VXOZJcsU6lDlW/8kXYuWzNca1KczzgS9UZdZ7ulPa4Oo95'
        b'bU/0YerFr4OHBA/p+7edQ8q+2nwDEWEL9bv/eG8KOSmjLVI842fA5iVmcDoxTTG4f6hzsf1hAwtaQQVokNE8IeG6Eqsu2CHIylEbePSQ8OgRxNAS2g8RrZJ+5jy9zpKl'
        b'NZkKTBHxhgKU0zwpghRw0jFObco1twvzV+D/bkjUTZ1kTJjJmwa60AlL6Nvd0OlhgDs6jUFpBmDnkHQOqxaAwylyJP8hmXljJOIq59Fwq9PTkKQALsEtoEY0exwFNk72'
        b'gJejffTmxnmsWYaKT5wzKD83L9eQm5aTpk5RL/vkuPZL1Qn1l0id9yw9oLufIqK0rcIzh17ix/KU8+XlNifuRKW3n9AkdWX17mkOTP6uweOcW90G/02nwWPmORhcCZKH'
        b'gqN4/B2DZ6j+4BoHjsOm8Y9Hqm4WnyejUze5HP8w3UCaS5urPz14C2PGmph1wvdKNZYkEtXc5tpwiUwa22un5huVWHffQFO53wn3ap6XcQRYoR2eQoIZ5sxp4YhCYOqd'
        b'm0L5gwssqPcGFyxIdKNWDQZ7CPdVgSqkmocmKyJAfToa/yZ5EjgdyrPzhVli3SJwzoI7AK4LvXhu3zlPPyTrHwMnOLCuaC1h7EjgbBtEqgbrfGTJKWmpyUin4iWIYUMF'
        b'IWNF7iDgttjeVmNOnlpv1GqytCtz3JFkkJDmf02DnUVkiJOgXB1I0OIAKdo0xLXwOPd+t4X/TNLVlrIE7BuIlE3lUCQ+JyKsrlWmotVHiC6khpcI0sH1mZ0WyrnymP84'
        b'SRrR/Z6JnHZbf47qibGL0wx4/FNWiouv9npFQie8tmaP+YMlz+fGjnlVKaKsWEpDwHkW2OWKJISZFyl4VYP05IM0uAjqYogRaP/Uv/lu9X1V4ptxn/5p4Td+YbzxZhxL'
        b'zfZCAhlVqB50JcrqSJzXq9iHSkSfVDaxj4zSl+ZRnNmIvp+OLFaqNerj2uPGv2sfqgrVVYrj2q8Qen+lMurCZreoM+80gAsN/mEviQO9TqiZE5tbtGfUp9RBoq+YtyVD'
        b'VOPXf0An9unX+2/vRvX+lnpx1+yFA4JbW+jXWttj3o3uLaTfixbGFB5F8v/SkFeGX0I0F4soEfBaHyVv4xDCPYjDiUEDUwDWAXvPZOOJxITLU5vzCFhJebAaiYVFT/LL'
        b'C44ShkPUmHyiTcM6QI2nph30tuf2aT4bgTxc+Kgb5H0Y0FWEBE39JiERYvOoRCRDouXvjfRVL90TbLd0F9st8+zWZTwBHt1gTZJGdDF4bhC4BreghsHG2EgqEtTAmwQ2'
        b'nitC8++3TkglqCRvh+XwAOMZwVAcp0NdVoWHmUZTJkyde3q001n6Bfe2CMwb0ZeS2cmK1+UBICpw/Sfmv+Xt8bQtopV3F1CeZtH/vClNDtxyYsiQhdPPzdncbH5x5De7'
        b'fi6tCjOBst594jcJ9z8/8d0PI0ce/Nh7nf8CLqVEq4qeOmtR9UC/UV9/vuTnI+o5Q2ca5r+ou/zRn080rlhc/HOyPOLv3ynei7h6JwX8ky5v3LP+rO5BXeGBQZurh77+'
        b'ESXzIvRSt2yUm35VBzaEuKlXcnCQlwCOyeEJc7hMBjemhCmSrDyDiOhPhS0WgNtjdMTODM8tAFvg+TRw2uJgIN5meBaWsaMLIF8NvKhDEkNXyXoKOIKUNLgJHCCQD1pW'
        b'gm3yCFiFOO8msD6cpoSgnlGkgMOWEeh1b3B1nFOBuwQbe1LixoM6C2b54FwCOClPxtaUlDSkca0TUF6gjYH7imEb0fL6J8cj1To8TBYxC5TDTUiOpahgKfc8vN3XQoyE'
        b'l8P68VQftYIJ/njY5lAEL8Hra0l34b7SUUp3NQKchmWrQC3YYsF0MhU0zpenKZLw3G0ay1ASMSsGdSs6KWC/oOQJC63ZBj3PDkbzeDueQSpeAMJSIR1Ic+jJUMzPHIOe'
        b'P3Esev6H49DzR6FAiDBbgnF5hKvOPj0219eFuDjnVTfEfbWT7kcW+RpoAdvloalwI1J8hZR4BtwLWxlQBuphGWkkR+iGbwHoT+zEtyEsFv1tdF+qVFglsgmrqAqmVGQT'
        b'mdNKfGxsE2UTNtOl4gWUMZCjLHS+pymOpvDvIsoYtBDJxjYxLmkT4jriKQ2Ny5p+sAkKF+qpUoFN0MQ0U9OppQ1LmFKPUk/cgs2jgjFlk7Y49OmoTdjENpM6mjiSN7DU'
        b'q4pF+bxsjI61edbTNFVUb0wgJSSod5IqD5uwgkb99awS408VNCklJqXEbqVesElMX1RJ+NzOPqL0fxRlNzDGYaRGrwqmgTZJq+gqKl+IP6F+CDRMM83nbqCNP5J8tEWo'
        b'Y0je5CovR97kKgbX7cr5NskpJLkKqwSOXOhTp1ynNGyTSMNpBJVIn5xOVdBohr01wiaRzbtJrBFpxM0MTrF5o7KHNR427yCq1NsusnshoY7VeKJyYhuLy5X6oPH7VNAa'
        b'cT5u8W2bj8YLrYaPcYgrnUPpf9VIcIs2n2Y6CL/lNN6lPjamgTGNR/2lSX8ZU7DGx4ZK9EEEW8egfL5GqY22Mfksehel8cWfHelijZ+N/zTErfxcjT9f3pUHt+Zr89UE'
        b'jMX/vVGedTYf8vTV9LL52Lxxffid0cfmi98U1tq88XcLv75+aBR+aBSBaBSM6RubHx6dpjeaU8Z0i/+GytxDn8Su9Pf5bzgdjdJfE4S+U5o+65m+lM2f9N8PtR5c5Y1b'
        b'WOZp83P2wcY2sKZAC23zraDX0UaxxYv/5GBZfdPmPhIZkPptVIx6xIRLO3FFxsEZiS6NmVYuQqmlnqW0jV5GNTJFHJawHCJmuzgry6hers3KkjHtTERUO23pqmZ7xhv0'
        b'ZktOwfLCST84WaIQNVIyICdPm5OPNK0OZawj6yNWWmB6RIebcPZHngU6qWVVoVY63NytqwIn7kudXQ3C28I2zLwZM1eFul1Bd+q207wSRjhn8S8QRxOW5H+kHHoR7rUn'
        b'9QA3/MhXLS1WG6xaKepZ6HCzjLDhR8FmbZFVa8zRSvUW7XLpcD1+PXK4eeQjf5KAP7qSOPLs5ZbTWfqRh3S51WyRZmulj3y1ekue1oRGjiYEPR/wVp1H9MhH9JBHHsPN'
        b'iyMiIpaidCzKPvIPl+YWWJxzNR79ySTtAr1Ro13Z7jkfd3gGVvVQEmrV3M7lFBSuaufytauQ1otaLtBo2z2yV1m0apNJjV4sK9Ab24Umc6FBb2nnTNpCkwnrou0ec1ED'
        b'pCZZQLtHToHRgtUKUzuLamrnMEC0C8n0mNsFuC/mdrHZms1/EpAXOEFvUWcbtO20vp1Fr9qFZj4Dnd8u1puzLNZC9JKzmC2mdq4YP9nl5lxUHHejXVBkLbBoZd49iqTP'
        b'8kBSZZoLVsVOkHwDr/kGAmJYguVozBF9aCGLZVcO/YppP4dcK6EDGU/yPYCko/xMEPrcD6UE0X7CQPRZiFKDiNnUh/ZjMEeVoFT0jcH804fhJeIAxocYV4PpwJ9Riz8z'
        b'TCAqhXgsQ/iiBhyGVViNSoX1aeFIPLiWjESbLHYcPALOdzLHiwmwOtDiU/RAzIuxUU0UYUhvIubFlnI21tyvSGJBki3+0yNmt5fFLM7G2Nh4hD6mDMQO6Xwh+o8YSF+q'
        b'iUFEk+1LNSNWhFgThxgCh1mIWWPjcmlUH4fqzkBsjMXsBbHC3QgJMaMQaHB9Ag2H6mDxN/QfsUZcT1Eez3JMRzVc4XENZtUCm4i0JXS8F/Ctk3qYeIp85xzfuXiqSGJj'
        b'iClXkIbwOBWvJFnOdPxIdX3CaTKBaQpeZNastbSzao2mXWgt1KgtWtM0/FbcLsLwt1xd2C7WaHVqq8GCwBYnafQ5FlOKs8J2sXZloTbHotWYMnAaNojJhE+ANDfrJ/Zs'
        b'0GQ56x2IyJl5BAE0DgEMBjQ/HhgwuBH1SUIHM360HwEwsmlsA3tWKEHVQn4jHVRH4o2+VH5bTg4uC+D2gYZuKgluHAukpLFuO6oU3lPVeTn1HhvtNEp2VZdckpYGParw'
        b'QtPViO8vowr9EJChgqbRCDC8UQqNuWkF7YX0H8KvEEggLkhXsVVe+HM1dpPhUEdw856oOxKd2GW19LAxGIR6UuUxXOMpJUbPL3AnOBsWHqiSg6hhFn8mAlQGgngGNYa6'
        b'VkHnU6hb6JMNdaSUNQaR7gkRbM/En1AKh2HNxpK0oCos3CAs0KHvGOKJ8BVkw7WOL2VtpE6Ub0OVEMEpi4QbzijBn1E6+WbjTAbMdhD+oDpsHClvQEJnBBI6OYtAxyDB'
        b'8x6NBEqaKpGgaRJg1kz8p1DaGoHTfwrhBpq2en4t6DQEZJgMtIuK1SZip2RzESAjcmrKX2FKwACWxINih2lyNn4QyM0hkK9F9Fv81OSxA2glWYQwFqKGl5unuEAWgSeD'
        b'QNMHgSiigAymfkGEXkoYCQLlIKQ99KNLotQ5OdpCi7mDzWu0OQUmtaWzGbajAcSa1bhpPA6E1MRxhyTocYLXryX0bLsITxvCXb7KbNfwPFwdiqOde1IsT/cHIurbr29J'
        b'v8ePwSlNqHB1+fiz56/iQipXd0SOxsbQDnGJYqVDyZbMfHgiuQ/Yo0xJS1OEyoSUVwQDD+cv62br9HD8N2Njk5bKRHJfJrNVxJs3EMqLdQIe1yroTJakE6c1B0HwQJiI'
        b'HQPxW85OcVSmgICgoN3f4bw3U2/QphSoNVrT47eBx1MUb7sTEA8OoU7oQm/u2TeDe94QEaUR15gJ3ku08FaHTwpsYCkfcIL1Wwt3WLH9mAU7Jegt7yTX4boCK+E1WMVb'
        b'JZLARYQtS0JFcGvYTCuW+0Cduh9fKDQUboxMVMCNoGVuaHIqUuMjkhTJqTRl9PUA5d4Ti3IIXQ5LmDdHMT8R1sqSU1NQVmxfSE/BDlmjwXbh4v7D8mG9/rU7+zgzFq1j'
        b'Al/7WvVq9nHtcfXCOzvBlYa2hUcrZetbNkzZ27yrKKKtuq2iZSH7Sq6wLT94/MLzH2w0lNm29xOOarV5mEXTROaYd5jtPtvX196V7NVT374S8KX9c5mAGATy8tLBTlAF'
        b'a5TEO4obSIODcPcIYm8ATePBFodFgpgjwA5Y5jBJbAWniA3FBnbCE/A8rFVgh7IiYmkBt/MZqp+VAxumDCGNgGPgyGi4d6U8QpGoYCghOMxEgVOx/Fb5ZVAOTygjklPD'
        b'k0AdM8lp+UkSUMOfE2TOXeTcnnh6tumdY9IiVp21vEBjNWiJsQKrJtRa9JtLzBAM5zAslgzqBqURnUq7dnvMWoMOPTFF6LA9Ch6PpIypAH8udPbKhG23Goyl2AhBlaHf'
        b'/UFu5own9qQb9rj23aY6scedR9MINT1dWCR49q09AeWmL7mwyCeNyJdecH0GwaFYZWcsggfBZmsEyhFXmEMQAlaUdkGk7kg0Yi4pAi6Bm7DtiWgEdxg8Js5e/Mt7ug7K'
        b'4NjTRconreuqbIrjDerl2Rr1pNWopAnTIutc3Iva3hazq7uFnTzt4GYlOJ2YCurhJlC+2jEOuK3TthwbHWAGW2YHwNMUOAU3+IMyvYY4LIIG2JjMmxtBObbh1YTzuzY+'
        b's9lR4+HRTgMSUG77tYQ88hIQg5fYRR7ZKrSMpRxaWNa1sBxZWHYN97gNDtyMSzRzJ4/jMDpeTYNtSnky3AnrlBH85uqcRDl2rJqHMFwhg/UpSfNcayhARELrCW9NmkmM'
        b'0DtSOUos/gRbpsMPJoRSvA/ygTzYpMQbOxHggpejSt4XFVY5tuwx4Vu+1iMYnGFJmfkqo1KJt4CSUmeFwuoFPHmcRdodDu246XkIeGCbCJ5l4QE9uLeeNWOG+r1u3knT'
        b'A+Lo86ouIkCmTlEbdIbsh6pw01eqT8+9kf1a9pvZSerNmleyT2u/TPj0vShq3gR6XkzFXHvMZ7LWqK2tWnPvI1HRZdKMDUcqZuylh/V/teHlQPrdj+6+dffDl4Nfv7NL'
        b'SL13Ivjk0ninT1AZPINII2+03u4iXx1W69BsQin7RMBmTCjBngVutNJBKMG1aYTkrtEUOUmhs6asqQ5SCFujiGE7p4R3+cObf40x6Y6WvOE5NlidSzxGJoPjcCPS/hwb'
        b'hJNpeQQSAALWsKj1Y0uJMRq2DPFw5ugNrmO3VK+xDFIS9sPrpI6VM+BlfpM9dJV/l032uuxnJ8o+eO88q9CENHGsDxGq3M9JlddSYoYoyEivYQKwmov0l5Ix3SmidqU2'
        b'x0EPO8SrzjXzCC/g5bYO8fZJG0aOfSUfVwFCtM3osZ52MpAy8vsfd7JtzUTp8bJUQjF6ge2/TDR6phjYp3jzONiGHVwTwMXhoEVGDYHbApdNn2HAfZtRFJzxuseXwynq'
        b'k5F/Yy6Nmtjn3zTZUDwTs4tuHVTkg9At+sPoTeI/887mJ8f/zXer11f9GbzPGDzl+RpKv/rlWIEZ74EVfz2hd+11bxglmZ6UfGmSkb3ir3+V6jt0gqbsinRJ6NKHs5cN'
        b'YbN3v64q6Hct7v43H33ywsgf1t2prxVF/G7bTm7m8R+mFP0m9fy4iYu/ifX7efTJ3lsz9H95YVDVayOGTvpOUBk97Njftlk+MJ+Nv/HhhFHxTR+8PzZPfenhvYJbTZfa'
        b'vjRt7BvzRui+FzZODteFvDDvs0K6fmjgyZv+OxS+K3a2BIB/BV+anFEa3r6lVibhBZDj4IrMQTHPgWudTwvEJvHeUTVgP9zoLqVQ4OI0IqQUwJsE8zInre2QUGAjrHLH'
        b'PDXcbsGuRHNB42geq5ykH0lFm/AK8kQ6ViNMyV86McGC9wu92OVuskwoWB8FroITRJ7Jmap1W254YoyDTvYfw6HqK+EVsi8fGQ4uOkgGgRGwEbUB7D5Ub1jOwgvgajxx'
        b'2gM34A2wG9YUJLmJZ/GgmkhV8ADcBdfJ4S3iNI5kgrE0OBMSStA7ob8HP5jKAR0OgdgdsC/cyO8lXaFhpaMHF1VdmFFqroU4gw5NgDUpNFwPr1F0HAXrp4LmXxJ5fp0u'
        b'I3SRCC837Cb0IdRJHywuqY3xxJYPhHp+6BPHBPgK0dMPKZYlIb9ILRxyHBHK2oWOtA6a8NSKLpLrrPhzgYtEWNCjqJNc1zjQXa775X4hCkqspJ5ZjoSsLKRBZxVZ1Qbe'
        b'Vk7kRtJIuzc+taI2m3O0iN5l8SPyeKbpbqHbPRyVoApI95ejRzbuPubfYoahgySIquHzIxC7kLc6RCEJuNKNsDHUeHBTCHbBcnCwm1opdvw3Y8nOqVZqkarosCdhcUaA'
        b'BBlGw1Z6dFIec92Uxwy1BU2cEU1aWg7nVjsGGtfGeQJ6uGRfIvkSpzoPh5DEVYmRkCRAQhLnEpIEREjisP3k8UJSd+lXkMb7/LUMXurUIJfBQ+7i715wyzoZZRlIwduI'
        b'fYYmpkYgEcah3SlmI4FnDpJsR2Ar3Dxx58MctJKionshLfEUqNO/tGMoY8a8xX+Iz9eqpXfGvNaA1b5Xzla2VbRVHNmlp+eI8kWrRS9P/SJzQ78NQ876XOq3IfwLn6O6'
        b'o9nnA7YHHtW9NOIlH2HDwiD5Tk2+7oS6KveMWqxLpLPfDKJe/6G3cTmD5BciCewKHsWTT3gANEW47TsPTyfEDlwxg4tOcgdr47D21ncqr7xth+fgATIVSlDNHxBB/Kw8'
        b'QMuiURwE58metBpN0U7sZb9iNA82YnCEWQlqYSNPC0E52NNFhWS84UmHZHQDHLYQr/v1sKXIqaciqn+WEMNpcB//9hgi7JVynhIuAQcJMQTNoMIpqTwbori7fuoQ/GVh'
        b'xa+zJrmWGuIpwVveEkSVAumS/t1ANsJVksdVYTubYzC3i3VWA0Hudq4Q5W0XWtSmXK3FjRo9QapCZKwUf16DH9gz2lTmokY29DjQRWD54wB3evRL/ZQxaWkOimQqxo8V'
        b'eAa8CMFYrrXkFWhIA6aVzin6BXZgWuXq1Gr02Oc0UGEaY8UtwNvwaoiDvMDqtYi8iDuffpogFYJjMfAIUS2owQzReqNiU2275qdS3YzWLmNSPNX1IJBO5DqoQz/xoE43'
        b'RdhpRe5MCvqmEWsRKCuFJ8wIei94FVnhJSQzXIZtlmJ40asY1PkWSpCgVwXbKGoiPCqArR7F1ol45JfhQXgdFapOSYN18rR5RD1OmpcYH4LohMJ5RhOchlXhEaBtNj7/'
        b'BC6Aa57wNvvcE0+UsmSz/Ok94LoNmHoc7cOCgw5eBnVZ4KgcHE9xiUoo71wWfbs6jZxeAuuRbGHHGI/H1xdulafBbXLQEkpT/UAjZ8oBx/V56U2MGe+RpFzV//nNr1Wv'
        b'/ekrVead1obmLS0VLa+0VIyqKaIbLjb4vyJq2zVh5+zgOTuDois+mxB87oOah+ODg1rL5kZFW6IEMYejuJjCoyz19uKAxtH3ZQKeZJ2ZYUA6DzkYIwSnJGuYmOfgNQs+'
        b'U5AIb6eCKrncTWYSjeJFolZ4K8oX28Kw2WKjgs/hC8rZZXCf4xTFgtHgOryRjLLgk0a1LMWNo0FbwhDe9+bUfHh0NJJTO7nxg0bQ8sTTE17qwkItQkJMELqSmZkSQmT8'
        b'yAZPSRgiFVkGfY7WaNZm6UwFy7N0endlyK0iZ6uERDzeQRlRyLUuVF2HHi90oR+3Ornd4I0scDk6TJmuANVYfuVhGNSlEysB+k+AORRe66bmOCYGn/sic6sB+/2WIzG2'
        b'ihyrGgN2LpTjWY2Bu5+PZSgB3E8jqL8ymT8aeBCUPY9Qpm1FMbxQJBEXooU4WSQp4qigCWwuUq0vELvqlEBw0wwvwDYP72JvTx8xPLcCI2eRgBrWnw3gStFq1JPW1Ooo'
        b'JWJ6/CqKV4BroJUBG3xAuXUCbm1LLqgAJ+EWhKrVKWHJ4eAE3LrCyxYeill5ivOMwRyx4yQtTYHD4LzXNAruJOVV4AjY17k0ynBrxS+U327wRCxunz85NwlOl8CjoKaw'
        b'CGxaAS8hTRyetyBZ/TKC0ctWNJZisGEOB8p94VYyOeBIIbhEurtDiTV+WAb2Iq6cIqJ8YSM7OwgVwrI0qDYhdtq11hWwTeIppIYthA1JHNhYAnYRmZw/eGaHOxANQyA5'
        b'te8EagLi96eJ/S/UOwVuSVckwe3gbGKSiJKACnhtIgP3A6ReEcKoSYBXvBT4uJhyAT9mN0oHLhKathRUIc5fLgI3ZnhYsYu4P6wFZXOE+ECTdhg1TBtOSP+jODHlFx/G'
        b'USqVIVYSyvs7/sVHSEnmCvGRZ8MRgx4J5iT5hwEIJxMmCrEbZEqAms+7JRr1kJOyKG/K7OFhlBVTSqT8NIBtWO6QY0tTNbEude0mOBtAeloAysSlq0bp30tRMuaxCD9u'
        b'fTcxtWFiGjvKb/0fVq7dnLr9r4OqlW8Nbg4dfrCJ9Qxt6u8va5z/2tsZr8d6zE6Z8YLHww05hVT9naTZ0R8bDo7+fnXJH+JXxQORYfyGoSPSe3OfXyz545Apf71YX7Em'
        b'pP3ecANXaq08mPPJ7JbvQHhrYtaQ+rg1BQs0i/8YNLLXnDcrd3//7jtLXj1dcLp01ruGxR/8ZXzMmTc+2PB52hsfGo5dm6Aof/13t5L+eeVPdb9Z+Yc69Tu995s/2sAN'
        b'PvCT/ndTMobOfWnqO5c/+ui1bd+8/wl8wxjrYT5wM2zzK9aJJ36g+1x5MWTg4LbflObFnQ1I+nD/0ZLIlgHHv/62ceR76crdPi98+fOw5sgrj8KPyftX7+o1KL3WlJX9'
        b'w2eSiL+Ll1V9eu7V9JEtX0xenHnsN39465W8fksbF3+6ZuXf9+qGfTHwgy8HPcgqXj9yhMyXSGteXvlKHCigJhxuDByNLUte8BzL6BcRvRPeVKKFOTMOURiaYorpKeCq'
        b'it9HuAF2gFvylNluxBs2r+CJ71FQBg4rU8IiEsNL4Gb83svAwMMjBvGvdyrgcXIkGi+sgBIPC4Q1TOlMeJ3Y1MDZNeCSPB11B7/Xg+1KEerSLQZh3LW5vB/oTlAX40bZ'
        b'q0oJcT8By8nrPuD8cjmsSgpPIsxDQPkuTolndWCdlgjZA+DFHCVWBxB1y1TKFGlIvOmTwiUg/NpCGIt4HtzEe5mCsxFOJ1N4Zibf+apxmNeeBOsQNsEaEcUp8CG3C7CO'
        b'NwTYUTe2yGETuJmcmkJT3GAa7Bs/l/dx3ZEG9vAVh89ciakxqgIBdB9wiUsEjWtIBaWwaTRhlzMVPMNkYpCAfYVXDy7DOriXKAhpvWXu6oFQ9URBVfSsJoDePXI3whFn'
        b'd3DEeMwPOeJN6sd4Mn6e6I8JoPHTk/VDacGuPWYJ8aQJIJ7k2OfGB6X7MAHEQ8ePkTCmCicjbmHceOTTdNzN9QtXcq0L13wl2J1rElmxpV/AE7imgHoenIWnLGKwLSnC'
        b'ESIBXIiNgDVL4HE3G9DSlYQML5NNgafR+tSkgdMpfHABL3CRgUfgYXCMFPawwrNyBG5hSIK8DvcLQRMTkxuSw3YR9YKc4h5WObudn6dcJ+jpTmfoGXtvXZBrK0Lwi1sR'
        b'LNkW5j4ZhhbTU+r2M1ubqzdbtCaz1JKn7RrxJcKzU94ki1Rvlpq0RVa9SauRWgqk2PaLCqJUHOEDnxGUFmCfumytrsCklaqNq6RmazZvWulUVY7aiH3m9MsLC0wWrSZC'
        b'ukCP9BurRUqc9fQaqQMKSa+cdaMXllWoC51qMmnNFpMem5679HY8cVGQYlVvvBRHtcGfsO8ertJRPRphD0Xytauwfx1fyvGlS0GNtBjNGepTjxVYzeglX9yVf8bUpGlz'
        b'yBupXmOWhs7V6g1Gbd5yrUmRNN0s61yPY7adroVqKR6jMRf7Faql2PMSd8dZV4Q0rQBNXGEhagu76XWrSa8jpfgJRWuVrcYdQmuF1sacY9IXWroNpJs1xofqqpF4pVnj'
        b'KBx4phk0zYl0bhLOXpCI5M05icmC2ePGgRaZJ7y6ahzYljBkXG9woB8FG+BxSV8kTVZ2QwI/ZwtpnZGAcqAB7UIDxu6r8/tv9uAw6ege/EGRhvIRstLdmaq7rwTfPcq1'
        b'GfirdD3cTPfTTgLHUVhMmPWfDFByZhP6VPPSrK9Vii8S1RLdl6oHquW6h6okNddYdeGB5I1afcoHhhmZIbXSb9Pej7/k875F+tHdd+9SAXqdRV313knB1yfVDRrqa+0y'
        b'3etfhG/M1lB7xEFZd1r9Xj+nDr3wQLX0zpWG8sbmir6aqVFsrpDaKw7557X3ZAzR2eAOHdgpV4SukPAm992MIrcfeRM6kJbDeiw/c0OSrTTibhdx2JVn3ZwSZK0wqQsJ'
        b'mxnYwWbWUv2w+2YwoeF+dCAtJAcdSmQmB8lyc0lyALdbCq7Rcc6ad/57avtOC80XIKwFO5b2QT0zB3WwljLq6057UDi+ARICLsNbcicW9HBWtIPr6OCBGQGyyGTE7GeC'
        b'4756/4jHu+bE8rhAPfNZ4W4w37NDgSjNOhODOKiEu2OiRkfHjhoTAy6DVovFVFxkNROV5wI8By+BHWgAbWh9z/uKJZ4+Ht5eODwGqGWQ6gUve8DTa+AeIu2/syYZnzAV'
        b'Uxm6ZTsXZFEGPJbi5YlUA0VFqZ7TJw+y8IA9s8/fOfNS9CkorH/vlwf7lEX5cXc++rpvuPAHT+bFr0b5tt7fnbCOKT227FHt98cCx+xKfNkj12dR9JZTcV8sXRKv2Tk9'
        b'6W3JbXZJas6V75bujv4pt/yuZerwb/8xy6tuW/9rX7NXjgXm9vqd45A/2AwOqd0tA2jBapEAedPL+Xo32OqBBLnOpoVo/1/acXnSKTtxlqnAkpUdE0tAO9gdtEMxaAcg'
        b'oBYTf+SS8KcCakd1zt0Ul1PrL5kXGD5HB0gj+ZEa3g2kP+p0Kg+72WKZ9iyBaFijfyJQI4jGvkfV6dGxLFUMavwi4G0RAYghyxhdJkNCZqVEaDMpomrC01lIhUXwGEGB'
        b'i6kRkzNJ1uvjRPN/oEggLcNOvzxeffyTUWApY0l4N8O2tV48WSRvRg4Vh11jpRTWTJfMDOETK23KmWY6lKb8VGHVAwIc5zmT/cTj2QSKKlQZBFms48DozbxRaNl3zEEi'
        b'3NZ5Y6LgRo4SzqbBqcxBpFC8rd+kl9k8xJlU8QuN4Q5ldk4rnRHLIaC+v+KetX8Aib0CL3jDsjkAVwPrBKAljGJV9CRYARqtOEASbIa7cbCeDv0W6SKwKjwZ2xqxXoJ0'
        b'X3B9JurGJjkW70G13FM2fSDZTT5rFVIDqOBQKoGSfLDQv/A1ipyEDS0dIRYvCl0kUqUoTTmKsYUZb8bGWsfTVgwEq9NN8DxiLanULEnqJHCMdHxe0ITk2/SXeDQBb412'
        b'REDLCJ9Exfl70lRGmSk4+Pscknh65iRpBfsDRtcAbt58PuePGeH0PwYAjpKWme8N/64PSRyT/D4dnGMUUX7lBcE68WySWD5nJj19uRytbXl+sKKGn8vfB/WmVQINojtl'
        b'pfeURVqSmPychUpM+xT1tKw4eBicQRKboueNzWAzBJSf2mvRWh3fekBAAz0gc56QUpXlBq+5NpYkxnkvpP4xbgWNulRyz1MaQhK5wKF0gnI/RxWWle60rjWTROvQQVRc'
        b'CJrZjDLbvYnD4kji536p9OveUwWoeP7CxRvjeeiZGJQE2YVomKoQ4zBHfLfmZW/lHKISRJRK7VsRXcwnHg54ce6XjB+LwFJ2x0fBJyZRpQPK2b+i+VTNb/R35FQlfBQX'
        b'xxSyKLHvD6EL+MQ/Cryn3mKRXpKhktTPdSTuH1BEXVghRALH/ex3Q8fP039f2MCZm9EEvXfwwLxZrxrfTfA7/fzy32riYYDvwO8V4a8NHtSQ85PKh+YujzS3jg7ISTv+'
        b'b03DhD6f9XpO87PvgS3mrctEgwf/Zt53+7Nun1hmP7VIAAs+PiW99O6s3OuH96wQfXQwQHquIeMPcwYt+kghF3jDhf/49PeRzw3Of3FGUPS9zRHRL437497znxjWVf+Y'
        b'kPiShzfzIPRG7XuJzxdtH+ph+nTmq6P2ZGe+vTuz7wdzgEH1+WdN+wob91WseWVz77i84f+esX/Mwh9flh9rMIa+tG7YP/8+vvXM+zfz5p/qM+bFMPG9zI/nDvBaeLZ4'
        b'UOPfr36+oTXzObt2yivvz311XemACQ//OcWn5PDd+0F/0ew1jbj2cHKlpfXKRM+Pf/Pjny/tuTU7vvdHMDxv//bcF0I+XL7t8pRP/ATvX7EH9P/wZTb+haHxL/WKfzEm'
        b'/k9vPB9XvcP2znPxb8iPfXstbNpPi38aduCFVbsn33/1Tf2Kww/yZ//2yu+ONP3Q+s+DvSd98uOG86XpE/5VDwYULC6aecB0QPj55uNfvrhDnrt09snnY1+eM+PnsI9+'
        b'8x+PPGWvzbVv/pD1V8W8ZcrG307KYjOWbdrZ8BeZmOjymboAh7pPD4R23o4ghJuJYSVRvFYOqyKxMWM6A5rpDFghJdaHIHhA5QUOy5MVSkVYmoCSCBl4E173JMdS4T6w'
        b'C27r4EvAriCsCV5WkBb7o6wHENlITwKnOHDLlxIamCHBUv7Mqz0RVsojZMnoPWiAZ4gG6wvL2IKsOTzfO7R0uDjYZXlxmV2GzuTNF6eKgd3hhuR0QnoeHHX4Ie1b8Izb'
        b'ejK/Z3dReGohUuzkl4TZ2tyZbZCE5pggHz9PjnaPi4T/D0T/g9FvAD2MFjIDkIzpQw4LBdIcG0AH4eO0XX870n5iGOYnISskLFxMnOslqEYObxT0ezxD58VSAfH2bxc5'
        b'9Mt2AVEa3Tj5f39gCom+OGQPf6ygziUAbMQEtZsA8NcwdwEAqzmwaRWSAZ4g0jLgIs/UBAjaABIEb4DdcWSDEX29DhvJJpXLwpsBjnXYSiLBBQE8pRpDNvWnwyYt2ZLT'
        b'JvCmGeye6gfXswORlNlIqGP9LBYLx3EveqoMrGaNM4Ynjt1ALez3nMrwqnk0n+jbS0QhLindEqmSXBycSOnfK2c48wH05hP7b0JqJ/qAKMnMP4/Qv3Ph87HiopGx8w9H'
        b'zP9g8UyVNLHYSC+4X7nTJ/3c5MlrA1763rPS40CoPOJe6+eb5WeufrK9z43PvAtWjbXMbVj1r8oVDcbxGxcc/DRgb+o353777dE+3wZsefUTOuDolLJlax9++OGtxr2n'
        b'hmesKqtc/YP0xMQ1L8rNYff6PNp08398Hp4evXvB2sVjj50/sG/zfe67z0XfMJFLZ+U6nBoN00G9eyxXcBLsCHML5grLxhBDLjgOGnMI4i4GtS7LJGxcxbtGViOxo8ld'
        b'SNMy2LExBe8D7ucKOFDP+3CdL4zmc4HDK/mMiEwEhLHgONyVykc4OzEHHsF5XKsHb0ygfMAZdvoUcIqnNcdhE9gPaiIVaQq4MUUmBDezKd8BbBas8SRRU8YMmwBq0h2S'
        b'Tzg4A285SUp/0MiBQ/A0WO/UHYP+1wnFU5MRJ94SMhLmTkb8sQMUQ4+YKSGIzuAzhAx/ikZICIdpE8rt0N1r8DB6/d/ud70LqXHTP3axgW6IdUdpzEz8EcTscKI03OSP'
        b'9HnfWFYHtoErPe5B4x+zhO5wIdLQmayGyeQ0bCaS5jKF6E+E/sS5VKYH+u+5ld3KaQR1fGQtvPfPaYQaETmf4qWVaMQaj0pK46nxqmMyvdF3CfnuTb77oO8+5Lsv+e6L'
        b'vvuR7/7kux+qkZhEUZ0Bml6V4kx/V2u0q7VATW/SWgB6J8a/mqA6HGkLx5vrowkm73r18K6vph95F+j43l8zALXQ2/EtRDMQfQvSkJPJskHtPik8KU9VG9W5WtMnoq5m'
        b'VWz665xHStw4OmV6Ugm9Gdv4iKFVs8qoXq7H5tZVUrVGgw2BJu3ygmKtm12xc+WoEMqEjfgOuyVvNHTZI0mJCGmGQas2a6XGAgu2taotJLPVjMN9dzIhmnEWqdaIDYwa'
        b'afYqqePgZYTDKqzOseiL1RZccWGBkRiJtbhFo2FVZ8viPDNvbEZNqU1u9lFiRV6hXkVSi7UmvU6PUvEgLVo0aFSnVp2T9xjTr2MWHK1GkMm0mNRGs06LLdUatUWNO2nQ'
        b'L9db+AlFw+w8QKOuwLSchLmTrsjT5+R1NXVbjXpUOeqJXqM1WvS6VY6ZQhy+U0WPQvIslkLz+MhIdaE+YllBgVFvjtBoIx1xsx+NcL7WocXMVufkd88TkZOrT8Mn9gsR'
        b'xKwoMGkebx/CFlgE+xx/dMt5VqyUIVbRx1uIHNsBj9Z3tzob9Ra92qAv0aI17QaQRrNFbczpui+AfxyWb2ePeeM3+qLPNaL5m5KR5HrV3dL9FJEdhWlWHBfdd0GW44AK'
        b'PBP+C0e9JuatseJzj8Gg0puXQDzAbV4ICU0Mj4iAm3Ac2FiwQ7h6FMDRt3m/QrguT4nypCsiEC+8gHT5dBpHtWZh+XiJ/qHegzFjM8ohRQM+Dhb66QP0DA96oEp0HHKI'
        b'mB+qTlYz5/v2iVoRFalZcudcQ/OWqxWymosVVytG1SjWX93RUjF8/8T1g3eWx4RQ6573f+/q/mI7Uh1IVLHd4CA84c6ueWa9Ch7j+bUQ3iLMOAYekjt4MWwDOx3SFGHG'
        b'4JKCZBkIT4LzXkjskqU6wvNQ4PDU3sDOieG2qcRJxwzXw0Y5rJ8hTRzNUSy8ThvjYC3RR+B1CygjE5E5XBFBk2hToHzR8xa8JjoLDWvmhCkVIooB9bQStOTy/P8WrAc1'
        b'qMLE0WAvuBg9hqVEJTSSQKphJb+NetMjkoyuKhUiuSVFSCHpj4ZXdR5P9GVzl/Kz9AhCs7IIew5yZ89rKQ8JOcOAJfGSPp1BN8JZjmfPLbwrsgmHwnvS2YQWhs/W4XOM'
        b'oweu7SZAVwS6+/k9rv3Hn5vCgquNWuaMhinDzsLObaoWmm++8xkqE94WqEcdIcenujXpPGD1qO9jd79QI6ymIOepOlXJd0qc5dBYTLsf06NGZ48eBbrtgDk30iKeqrE8'
        b'Z2OYwOo15sc2ttXVWDhuzCm99bDhlmPQI8KtMCP6LXu6TjhG7JWlXVmoNxHe8Nh+7HD1YyjuR0cJzHy6Tnzn5p0EnUTSIwTdERzULnAj6E82+XcLTdop5oo7KcV7N0NW'
        b'g/NzwJkBsA69ARcpsCkPlBOvoxR4ZW5/cAicRJ0spUrBRXCaWDnHgmvJsCaJOE/FcNgJQwdqmGRwOV+/6JqSI5vXvQb/M6TmVe87Ugm3wntcnrTuiCBw2LKos7YlGx6M'
        b'9jkbUlccvstywzAgI857y49JYYrVu/f0urK95dNFFcLafj8vfLDnL70qkicfjMvfvWTMzfBB/3il7u1JfkF92RWJMk+i1BSCNq/uNJLqB8uHYxoJmkE1oTbL4NW12LSa'
        b'xBv84fph8DoDqseAq0RzCgZ1oK5jP0DDYHcSeACuJ7TxeVDrLXfcWMCl0b6jQStsGEfqFSOKVt55l+BMf9AmgCd5T5YN8PJwuAtscFA6F5WDh2Arr7MdBBulSlgfie92'
        b'4GJpuB/xmhvwxjzS8tzEYD5KNNJq+8A2EiU6xcL7WB/PBruUrpsOxBKwEUcBNE/glbh93GoSVDyRZ2DglBHzrpMs3ADXB3WKMPaUhFZrzDGtKrQQQosJvBuhHSghXh2e'
        b'xCeSRGztRu4cpd0Pfjxd6EBHvNYOansIPXYzzg2UMtfvl79Mbx0d+H8oOk3LUxtztbwjhVPYcSJ+F0EKyUNPK0MZtSueVnTqOZ4hh2gYf2XHOVgtdMg3fUlEvQ75Bh6E'
        b'zfo/2Gt4LH57jr/3axOCEqICubd23fjBGpszOPTL0eM2nhoc9kZo63rNsQ8fbex7DvzmsxjtB70DB/p9dmif7d8V1f8zMp5dIQ2SBI9Sr19y6qelfaraPG7s+/F94etf'
        b'fu/bvCvQyByXefCuZOdBpZccHJ2AxQWH9DEOiTcYwwYvAptATTo5sHoiPJROmEb5wDpWO0xIAF0TBra5AH1FfjoWUHg4B2dgI0Gied7FSBIB1yKRcEhTXCS+32AfSwIG'
        b'wtvwFGjlI5wq00FdZKIfsLsEwijYJBwHyxKJuTYlNwDWKBWh8KRD0oGXVUQ8ii1Q4FkcAKrSO6SjIaCZYOlIcHg1FoLggcLRHTLQcbiZFF3eT9FBGOCOGTxtUGQ+O376'
        b'5hBoy3KCRle3Zfwb6UlskoF0ycAu2NGlsMNmseOxWGna6ULHI+hxpAd0/KgTOj6hQRnbLswrMFv0mnYPBPQWI2by7UKe2Xc7atQZZTnn6QIXynLE+enxR4xYwsu5T6bS'
        b'XbR0/DNFo8GaDkYzN4mB1xBd/PqxuMoPgsfURPQ5aboT47PVxvzu+OpCcceY+ZIZ/FdUOFRpNSL9UpE0vQePIDfvImdJrE3jYp28iWQ99dektVhNRvN4qWquyapVYacg'
        b'PsCBJlyqmqk2mPk0tQElalYhAQbLUUbLU5Acz24kh03TR59uEpinowQtfPVr1fN33rp77+67d881LCm9ur25orliXE3brrasg9vbNoyqadnQvGnw3vLqu1sHNwyuUo+a'
        b'FrWzXpVIn4tbTL282tsgGyxjCXMdBnfATqSB6gOuEdpAw+O8L+YmIdyHbZA84sOjcxDuF6YQ/cprkbcyJQlUp6fCjSkRoD6SuIHKQC04Bo4JiC617dnx0Eet0WRps/U5'
        b'ZiKqEjT064yGCRgJS0K6YETncg61RMjzPXxU2HQMP453ZpnuVwRwbtkKXHkJjp5Aj3M94OhbnXD0l3v0fwULsQvicz1h4WxizEKIaOQhDzu7uaGjmxnr/z+ExMWS5qRL'
        b'eQOUhbdXEZVBpzeqDVKN1qDt7qH39Kj4ry0XWIKK7JFEd1R8BkSs/5936Jef906/8poDFWcPAvUEE8HlJCcyEkwE68BewggXgOP4kLWLBxfDneA8rIdbyeUrCWBbiDwZ'
        b'1sG6SCWo64ySk0G9qPeCAMnyZ8dGf94o+gSETCcI2UUmi+hW1MEVT3ZBPNMpF56dQY+7PeDZ3U549sSGnnBZCm2n3C5L+eU41ywxUHOPsnvAMAJuBBWM1uXZCKsQhLlZ'
        b'jztssjlWkwmRfsMqN3X61wLfJGUMQ24A+tirEt/H0trQTMBuVDews4l6ALwYKtfudeKuDYEdOSR2AlyA63kWoAHnOwFeGzzG84Arz4GmWVPdQA+ct8Eqy0j0bqkZ1GLd'
        b'C2mOnRlBmDBiGAK8qyIp2Ambu9yI0yOk5RRYjRa3RTT3BGkLxD1BWreiaU5PxYLHknve8ECgrhU93uoB6s75/BLUdWv0fxnqsE5kfCzUdXgtPzXESUPDsFCmN0qLYyNG'
        b'h/VAfp8OAl+d+xl/B9XEn/c8DgI/93ss6XuHzt3g1RL2NYJA4o5hBzvDOmSQkEwn/E1K47X0FtgwwQ32liB55DyilSdImAtYZ0zmb2xzBz9wC1SRMwJxwC4E59fAk08B'
        b'gH54Qp8Ef1l8lK0uoNC1pIPQtT0e5M6jx70eQO5EJ5B7UjuyPl3PNouysjQFOVlZ7VyW1WRo98bPLOfGSLuX6yyKXmPahQvtww+8j29qphyG2HZxoamgUGuyrGoXO+2a'
        b'xO2hXeSwHbZ7utnvsDWB6DBESCIUnCAUGSJvrfgVgTTcjIH4hqJleKqwX62Y4bw42u2XEdOB3gyO0/6TkH3Mfy7AC+WSSGg/H/znI7Zijum9GpTD80NBrdPyBS+mIh0W'
        b'KfMMFQrKBWsRkK3rtpOCcTyBcoTH6LyJy/ujt/dynPlwrB0JFfxIOmMljmuIzZc5+ECHyYgFMjcBLA3piZ3X0nTBNQ9dzKM30OM+4zp/ztH83ZSbPMFVs8anIxRgq3Nk'
        b'zi2LZE8R2DQxkvdGvRoK9v2Ch/J4C7z0i/7JhsHdCJ6Xk1xg4cjh1E91vrqyI9Dqr7nMBDfS3QArSZOxxE3l/ZleFKIKwfc8pIbg/ruKicOnLEJEDaBCl3hjh8/gKSJP'
        b'yoDPaa8dEy94EHw19+cZ/WVX8zOyTgw6nn9t4brQ3WkvxY1eVBe+L/30hCPjl4a8E3Zw6uCkfy/6R/+f+70+tl/JKrl6lliUH/jbkL8zcKJkdGDclVHrR79cWpwaN3xt'
        b'aK8JofNWTr7EZQUcKTw7KDvr9/oLoiHzDqu0ccn5r3v8OWmi3LtP3kKToGzIF9OLPb8yFxeG9vlgxgmvvt7X1v6M1IJ7HpM8eF/ao7BV0sk4XMNkggvJC+Et3ncnlqG4'
        b'8P8gKFBJZmRl8m46Z+cGUMNC8aBVS24tdfhAHmKDqHBLL3zt7oC/cYMcp0UbKByaLhXJlDsVEfhSUmdYMrhJKYKNoGUVrJ4BtgmGU6ByhAdsXg02k9reXC2gxGIfhkpQ'
        b'pYR6j+ObmCQTUhKxRIQPpH6SEcWHEX35vhGv3YgvaIoe95b+eo2eNdtRQopl/fC6697sKMk02av/LAqK679oxASNgJa9HTK7PfXD0MX39sx8acyQgbKG5N6Xdt47/e2u'
        b'lPFbRf95YWp58oYNE759p9+8c+8dnjV4acDHn9hsib+bmbXizLAplytfe2l9/6WKSyuOPfAdrzLdWa1fc31mr6x70T9+0zf1w9/r3n9xwaeq3JQ1Q279dHLTiC0XJ8s4'
        b'h8Me3A92ulmBQQOTDLcUzE8kwTyMoAxWOTyHbGAvfxG0m+PQmLm8O895WOUjB1dhswJfsYlnUUB5wWsMvAzqVxA+B07i2zLx6bjDoCEM27nw4bVx4BI8393H/NcGenU/'
        b'gm8yqzuZnPFw3DhZEUf88nBsZTHjR0sxIUWfTbec1eBrpvE+v5v49Gu71UKb7rioF27g6x5Y3w5p15uzQMvUIHk63BKWBmrdbBT9wT4OzeZZsKMbAeocQ6cbAXLF0PlV'
        b'VyT2vPvj6SQ+hrme1N6hC9AnRHxKv3+OEJ+fCjHxoaRlvUSI+Cxc/DFPfJjSiU9LfLL/E/4oda33F/29S2/Maw2tnDYm+U9pq6Z8MlDYz3PAhwunZv5x0vURe2dPnlsd'
        b'sjXsxqDFUyOTZvvN+VXEpynxcwnv2q5HxCVhFqYjkgQmyXEjz+xe1DCuBCfGa2cO4zfnyJvbGYg++S3DNMEwXzeDTxQhciBZeI7Bd3gfkvpSZMdLEQaOuIhaX3CWp2vJ'
        b'cP1w/ZszhgrMBpRnqNf7it+04ZBu3J1jz5976F954YNX5K3mP4XNWCKjJyHysIH5sOH+H975c5m0+N+ztA/Hxo+JG3TvyuSJZzOulQZNU057vaU55lzIkQeXwkrujV1z'
        b'PSQo1VwrD685t//7HSvB12MeLWmz/TQmP+RiyHwZzWs428SeSv4667jnEQ1YymjBFljVSWj81QF3CCJqtB2IOKwzIq6lOLzFHsjLMgQZJQQ1TcBV0e1f0YO7LozD9fyn'
        b'B4xb7x5Ih/fY2BkLt8iXKAnGJaU6EU7FgWbY4NHtyB/+IxE95yNErBLwwchtdBOF0ayZKWXIZ1bDoc+shcbvp1MN9FKfJUwpV4pDlguqKAuDQ+mbCkt8bIImViNopksF'
        b'CyjjQBwwPN/TZOBvqSHv8A02Aj5AuPGODd+UEkXqwOXP2VhTLcolaOZvqxGSgP/9UEvCUlEVbRPhsOYaUR3KbxPGU0VbjWtIWUEFvpGENb2Cw+uj/gtQPwUkjDouK+5W'
        b'VozKvmWcSsry98NEdSs54HElG+gizyohnxulUDYcxj+UD+PuuPslw0ZpPPoiyuK4xtMzDZFhrbZwpgnHxZ37SGC16BRxJqx8I/iEeH3xC3JZiGkURQ576zDceWiN1uVa'
        b'Ew7yPwN/F+Kw3Rptu2SeUY8/EMGULzuFB6+O6JId1ZIw6uSs0zz8wOe+2+llz3igvF2CL9YwR/OHbn1Zx7FPHGhc4oj3z18yga+L8HRcMRHk9kni+C8m10iIefYQBO1w'
        b'O3+DdmwYPu5P/O2lS8COgRwSbsqndfNJcEXRxohgo8xiDT2HwvcFkflnXFH3yTyaxjnHgMPtmh+jNXqTkWVZCrIMBcbcKNZ5jySLtRPiMjUCbqFQL+GOSaijSDuF1Xyc'
        b'RCxoUSPAesEquBte6Ha3i8tlazTpq4bOp00SrGRoWBu+mYfWcE0UvusF9VwQRDXTNroPhRkbTiHsS+gYB3GiYIavJOe8HjD8gAQlOr3BIGPaaWM7nfe4weEx4bGRQY7F'
        b'g/N0rBsJeE8TRWpk9iysgsNN4BoaE750GY0w3XGz+YiBaHznwbUnHACmezwA/OQr6HoMlu6q2u1UZschN2ZUIXWfouKi5qQtKCtxnEiaPukFBAiUtHX62F5nUtL4xFQ5'
        b'8Xr3i4p9I4ZZylB6L7WBJrc/RO14DUexw+GdLla0VFzc9T/rB79/YnvzhuaKwXtuJp6ssNI53tM8/zj1aNr7U8v7bRCkePXdKJAeDAkPeX3M5iDJG7WylICEgINM6Evi'
        b'6OHrF0lCL5WNW68dnEMOC48/1tc0Kh0JqCRm5nm4n5MrQmHrTNdpYXgV1hHjyAy4bXHiTOclbM4L2HqBLUS2jVbAbRlxJEpIdQrcFE6j9ycZeGZgCpFIx8CLq8FJbD65'
        b'BCqxLx8SSdcwQ+A2WPvsR479lxdoxo3lrzLI0uhz9ZauIXEd0Z/EBJkxEvejTW+7KrE/TXNVzuZIwQTW2UCZ2y/odJQY+zjCPWAHDoBTlw7aRo8LIDGC8UUy+E5Sx7zE'
        b'gWPCNWDT0MdTDCz/8nQCc7dm/mIKJq1doDbn6PVIwH2JcvLcoZ1nRpSnXWnQ61Yl4+4S5wmW57WVMQnL4A6y9U5C9YCTHA5EzsBr4Oz0x/cEl8XXdBCuF4ivtsH9KXX0'
        b'jlAwJs30DkXE7unOXv1StC4Pq9HRx/QO+oUlEEJmM8FObzkOysH385bQ0VUcIm0fOA02P9OkVTo7Z3r3cRPmkR07mr+Qab7blPF3IILNemV0DPZBAntBLa+y+Q5mJywD'
        b'm/6LGctzder9p5ov1EGemS7uMl8YGmNheT7uY1LqzBkOT1J4hh0FLizv5qTmumoMn0rX0IimY5mJMoVaMMVnKxgkR1ClLH/5kI1B9J0pEtuYwmgbjS8Cclz+0z4salR0'
        b'zOgxsWPjxk2ZOm36jJnPJSYlK1NS09IzZs2eM3fe/AULF2Xy1B/LnryUQCOBQF+MsFbGtQv5/Yt2QU6e2mRuF+J4FjGxPO/36Dr2mFh+cbLx2Mkluixvi8MMnMzANHCV'
        b'UkbHYqVaMMSxRn3Y8b5w2+PXSOIAFY3z7hu0Ir93No3I0Uc9AkpMLL8OBjdAwT2YP8OGO4BE+i3jnGtwmI1aDE4/Ps4iuWyZdl22jHrz7LEVKaqnqzq4NBKAtgjuUMAr'
        b'8JjzXDPcNi/VYxa8CFpno8fF2d6gnqFC4RVuObjsr//rrkjajIF+0IhPv1YtRLxGTecgjvKSSvjm8B+CqJH/4mZP+kHGEAVGvnLWjBX4pt56WBMpojxiGNAMWnx4C8dZ'
        b'YY48Imo5ObTYcWARXsx83F3JenNBlkW/XGu2qJfzUSTItTDuZHyF6VNXoUrqcTZ1kqmoRzLd2Om6ZCxGgDaE3m2IW2nAVRzJPZL0VhGRBGvR7I0wCdbC2rCZ3dzPOtsc'
        b'WYf7mZvFEa2p139zJzw5/9ZtTf3T+GBG1+C+lUrEYOthLbdqFCXsx3gqeSVanNqHmjtxET57P8C6bAp/RB5eBxXgUkw0aIuOosDNiCGUKI0GexBlrSFh/IaAnbAJvb4U'
        b'DS5yK7zQa7CDBpd6+/OH/NuYofwhf7hXRkUER5GGQvuikrkafGo/vrLI02EKHBNKhSYexYlT37aqKHIFL6KZjdBO4t9NyIFt1ARwSE5y91kophbmDCUH/ycoHNbEYxkC'
        b'6uGQABwnQBK12oAghVzEAy6DIzJlEjgVLkSsNZUbQINz4NhoUmTaiATqoSea0EJVdH0Uw9cjiJtEJS7+mRx/Z4Li+cSpHiIqJSkEz07K56oxlD76uaOc+WP0ZsKbb83I'
        b'aEvmpkhSo8/HXC+6eKuXl1x5+87t1oy70VVXWl9cNnzXS7Ne6b3xQOu/j+mu/nHYjefuf/75+uDbl5jLqrq2KUcegJXCu4IVBvW12CC/RwcVD1c+XDrNI6CPaczi/G+z'
        b'DiTtFsjnhatevXLwrYR3zqvvfvva8SYwoP7MsH/dX/bPMwL/jxeVfiX65seD4oKi+1l7I/zfn/3Xw8bv4jdMHb417/iwfYXeX4SP/MOV8h1HR799clqab1xxemnS7tHi'
        b'ApXX8Px346enx/3u4e9/a1S1/Hxg//27f5+897lr9u8mfPSnQeH7ppW/5SETEsFNDjeA3Q6TA2gDNxxGh4Y1BGWjBoKrLqEucqJDrANnwCEiEqauBeech6JBnZE/FD0c'
        b'7uPtjPVIYrQ7PXVD4D7srIs9dSeOIabKQnhsrpcSrAtwP8tADjIgfrqZnEgA57LhXrzCHMUsGLqMnhzc9xkiiv8v2C69CxEb0mYhOhQXGzWKUKDxXSnQao7mLZiI8bAS'
        b'egASK4UMRw/BRIXcFxdM0vhrCk1/dDbgiPLR7qkrMOVos8gdeB0Gzl8T8p0xfUZR7vFAcFvWHoleXScTJzlSeggRvZPyxFmzwsOI63U4In2Xo2KiOGoYzYFts+ExK+7e'
        b'wIXgmliBZYXB/6e9LwGPosoWrq2rl3Q6SSdkgRDCEiArIAgimwpGQiBBQRBQ2iTVCUk6C9UdCNgRFbS7WQKCgguyOaKguCGuoDNVrqNPZ0ZHtJ3FGfU5OOrozOhonNF3'
        b'zrlVnQ5JGH3//O+f7/8e+aiuW3Xr7vfcsx9u6KyqGtOWEP/10CVawSGug+EOI0A/YYy6MFKLlqCkFgUt8F+CU9aSyaVBrgzIExT28aSua4imw6Iimt+tF1lMW8glqtVh'
        b'aR88D4r7BSiZYU1SRS+yNRZ7EdcahSRNY0RpEArMoHB4/QYkJYSjn5MEo1LdJnJxMVRzq30tQGswJZ++4qgyPEeMWtpaW72qiuLDqERUrxyVAt72ACAQWIS/fq03avd7'
        b'UfcogAFCV9crgRUqBtiLioq3d5BUaOIf8P7D2IJ1xrdlu2hqjoo2g3Mh8TnfSSK6+COWgLZDf1C/rRyDPFcyOgSdLM4DQmSIfo++AQg+/ZExM3uhi7GxxUlGdJGQWg6Q'
        b'2kxitGGwYZj0fTjacEopIo42seEEtRomWlAkyCEGRQzTjHEoO0ScUCphKTylYMn4HnKLCzjFYrARukZPvXxGe5OvpHAGoX71zXXTlg0bdcXoZcvhWpiP9yUFMy6fMZ2Q'
        b'6FPYWMaPepYjqg6P5qjs91apNSuiljq1pa01akFmEPz4WlbD5DxPWzMqQi1RaysqbanNUQsMJnxgMys9E06ejJ4W4WuPmXmfaDI8Rcn0QEARJRnMMISmuUP1veTDUHsA'
        b'g/FoG7VdWqSSSYPIt6SVOydf1nYpw3sgHj3kkDfRbABKLqRxiKIzskINoNGLOgKv+/j9nL8kKCiAwgc5D5rDCOp0vNKbWUFA+j3wfxZ3hbuDSBUoTcyAeeG5lbMpty+W'
        b'u5Plbh4Y5NVOehc+/Z1hvSJVRHlHl5CbS5MBo0cL9nPaB4Gqeh/sDcnr8zbBJHhXeX1n2H5RZ6vqDaCRJo7xg91D6zSiwSbzzGlDMjmPJ9fF2vXarfMKR88pzieCUdvM'
        b'hpjnhurXaMe0A5bRc67q30Ya4yV3i9cBMnFLRa9EsflgcJdabhIb5AbrUhs8sygyPbN6rQ12xWqmAA+0AlRDC2nbUocyDOP8QTpBcW6wL01QhhvpRMUFaacRB1Ci+IBJ'
        b'SjJ8k9jjWYrihmeu2BNJSVXS4ElSj1wDlHR4lkyW0dzSFGVESASKAm2f7UvdSh6lcpQhkEpVRsI3MrQgVxkK6TQKGDGAaJ9R0YQLYV68zYELgBLrsfJM1uACE8Z2s9sp'
        b'uiynSOa9SR7yHTT/p76Df138uYDwX8SRFR4pR82PTXTcZvLQ5qTw1v7WqhrvczH6SlibHde0ktMz9kngUVuRhEDSG9Yq4wTUoTGYoIo8gtlAVV1flmBRe6uvqr7ZA69f'
        b'imvCgPgmxHL0qlsw63ZzzAStxWXuRsMi7pAQtXjwKKBd0actGu6Zn3WTl2uT4+vGT3tNT6xaJ00PbvhY+LZDvGrF8GwC33dNv+zuZS9KJ8YR9sWmnQA+z7jAJHmYjTIX'
        b'Fuo1KCpCo6BOUJB/IEzFMK6wexplf7piCYr4CyCfR5kKPLGyr9I5M6/CY9Bjg2Vjq+jix0T5gi6hZAxMGfm3xZ2q8jh5/FVdlqsKOvL8eNayeNkOIB3VgH91PZyjeO6a'
        b'BkvkmB3BTJRv7Y/n7AFQA0exl3y+vy2aOliGYRRGzBkouPm1WT2WYfw3FT08YYrxI5djLkIauQDj/AsU3hk2jWmhKKop2C+Lvw3wBkQZmhVTlRA7EHXElns/UgE1Fb7/'
        b'wMRWsOk9lw2W+K9ppOrGllqxwCqfT03j+0Wg0uHVqR5NSj29SVBCn7CGWoVxb8KwlMIS4hthWtgNsAS3CNRG3mwjxq4OmmzIQ3zU0uxvqmqF5mbGmiszp/5GTMmo1cva'
        b'8b00ktUsKOET0bAr5VhYcX6tO74vrPj+B3gs64oQ64oQ64oQ3xUcbugMU+wSKtQMnk7RuI7Uo/ehQL6xODBQjjqQ/5661eogyPmXnj1xn9YTVn6vSYmxmDA2SBhaGhah'
        b'JwUmTFBzERlhsac7oDeIEOJODgjGUhKNnY28ji7+PIYeSGoSdgxlh6x3CR4PIFX1AW+Tx2OeFuXcP3fTqA6Gr7+OCYsI4UK0a21Gjy3bXXj/M7U8ftGVnKl/bK6aC2Lz'
        b'WmrMKxyFNK+iMa+SmdeAyVKFms2b+GoGmzwaCPSkGTfXMBp+s8HmhMccQX6/CR9ieKdl7DRjXFyCg8zre45NrKp/EhbUZKkvZNX0dYTaPJ7qlhafx+OQuk/QtJ7VsQyE'
        b'ri/sMRsm2UHh09FolUKJc7WI7vKI0O6Gc2aX0GmuplIYmi+5GMK4BgBzfXMgmoSYueKt8VUxrVG0RA+0MHGweTbgZ+owHG8SQZ/G65VVL8b2cUmxZeXkhe8k+N9zx7Bs'
        b'pX12gpZUbqwTCi0bRdgiEU3EM0UFE2uSasZNaEazOhYoKGr3ttf42vz1q7zRRDzXPEBjYq3+v2Ajc6GDzf5pw4aRtBUg23CCy3Aq+eCYMLs4Cns3Gi9/6d1FNQ9euKU4'
        b'eCB8Jws9Dw5sUw9ogEMRI0RehUs9hxIEpP8BG1jOOkYHiQTrHyj4/Sjp5rO4y4UOS4cctASFRhloe9wrliyMJyT4L2H3dTz+TjXeAMyQEbSvdAZl9hzuuAYJ9S2gphwo'
        b'z9phg5rloBVqswZtOLRBawYHOVdBTmuHPWhXHw3y/nuCqK1hh/fiVK5ZCtoRZ/FrQcGvKdT6Bvi23uQwMBk2btEuy3DEt/LtUSfsDSAl630KTHfUGmjxKPU1AVJjoPMB'
        b'TpgArK3qqB0z4kbyE57JCCALT5weOnscNS3NfmaYF+UVFIBAoVG+RpWwGKFGYb7eCEn+kOv3cC2G3Bk4dRTij3z5O8gXLfPL7+DdtMtl0vFxkCd/6bQD2OgEeUhAvJj2'
        b'Yr5QWprPl+ann64bTL153OyN+q3ZPsIukdRGCpphCIiL0OlPQ0OnDkFoAkdqLl5G8Mbyo47EhcP63ly/uOhY2BYNoT9yOmyiTRJ4h4R+vhwSEOCiy5ksJUtpcprstqY5'
        b'bJJLclkokrldf6zA75uE8US3zNO3FK6cU1Rh4bLOk0pbAwvz+TbUeNGvceh3addqh+NMnShADH2RL3NnKfLCcWMhNzJZx6WtcbeXxwrkuYSrBf1efUNbLyEQQgtSZHLF'
        b'oEOQ7+S7/WYkNFU1eg08RR3SB3yyGnM5sRvIEsO/qZJzT/XHtcGh7REw+IW+oU/JEf7zY9zmGPGbTDEFUcMcSF0gKiUgW3nmBGwpiy8v1IoGmSujKzDIY1WcSiL82hSX'
        b'krQBXYkxAJ0Sdc5qa2paYzS2b0w5JpFktAucunwcgcl3E5iM1QBXkdgOkqGzbalQv+PMExXPKyIT4IjEPUW0J1u0H9K4eRBvb47hULTvZPbsdAIJrROmdwNImc+B/2sH'
        b'xPfoh7mFIRKUVyfz/RyddkBRWFNmxaaVX5veo8JYlv6xNEO2SfiHUasZooP6PLeP9cSQLwRjHs9FcZVnntbbWKb+q59OU6nwQAw6UamMEEYA9OqIMA0EUuTrSby5T0AO'
        b'oHoWTmRcg2tjKlHZDAOmiaRRI0wphz+jvJygzZxuvMdGjDgXseH66s/3RnxISDwuVldfM2j1eHzeZo9nQdwQpp1WJWXon3mAnQlwdZyhVUXgQMJzpT9sC995PIviauy1'
        b'RCnH9+xhab+9I+C95Az1MLQOm+w4/QDBvaROwdmbFjsQpuPlvNipQCfAGab1HMg0xZxWm+iQbaJTTLYDyBdJoNuo79H2+PMRUGtHAnEgMCdXf0J7QtJ3TdCP9g8E8cw1'
        b'geBNYoPYIC21eJluGPL3JK/UYAWUzUiR5B4BpG2pjXHkACgyIGknzpqDgLkt6q6sbvDWBMgbnjFSP5BxhM6kVLkfmEFQrSY2J+LajN71/TC2EVVnOxPTaEX3mfPDgZA6'
        b'le+NiuKa8MUtrJw+OnEm2GMza0V18bXuAGcQX4SKLoZeSUCMNjrUiUy5l+CQGCSZxHpB5pawHBbIoRrqv/w+mUg/BXJZu8m//TzLbfaMpeJE+d3EHSAzbnOpRx1lQCa0'
        b'MxVYgma4FaKu8wltbAsYyrHdBPH3AXEtUoxXJZBOaxoBufQzDJ9BTiacvjvPjyGr1hiid3bPzdqNpPVqVjcuhuVcEduicViYUyTxxyBtj00/WqlvnDOvBHXhNmkP60/P'
        b'nbcybrNeoN1tHb6krP99OjBunxJqQnJEQFcMI9boILP3JmSaiY4757a0NLa19hBkWozVkxrbesapFYbZNJALgPgDY8DJwpB4KbCm1avuxlt7jDXX56kq+6jWDinGB7Px'
        b'a4edoX0l7IM+rPMuim3G0/bOLHix1tw7AAop/uJW7S5tR9xIa/d2A8SVgMGGKsqKSvRHUYtW31pSDBj0zSsd+m2idnsvuVOMOYIicTjLOWJ3ZNMO4xnxF0Q5HoyeWhRG'
        b'8o8Ly0jXhjm6t+wXurnvJJkTL5s3F1YR0qTRhJbupUok+Q+NHTYbun+DFFMNYy6tSPKJKPk8fT16G3tQPwa7Wr8bA2CiG6UTSq/1JZvra3nc+lK6ZTJyrYWkQfalImn9'
        b'yADvURJkg7NAItmPqFgVGyLJil1xABIsx0mAbEutdCrYaI26ok5j6ucBmq9WlPby1REb9H0cKgDVw2Aq/G4RqGqTOzUCMGG+HnX4gHImLjzizoIajnGkpgcF4w2gWVkc'
        b'4M8SUsBB0d+Md5SWsqB0pLmhL4y/JQSFWShEt8B3FjMP0d+qyatsEGrheSfPm2BPRvZwKS5Q4l9NxAvhSd3PmEQw6vAQe9aDzGOCjogX5BteUyjjAGJ+tare2vp2DyoG'
        b'kplAVGj2fz+mFxZ4s2SavQAAgr9/yBZcF+jkWSJnzyghTzaC2sWkOzQX3Qh9/D6wcnEqD4dxSvBEgOVQJ+GAIfuDB5QNVSdh8G5gzA+Uc/snEkNEIlZGdkAISigLZyJE'
        b'xboFh3qRyRrZJyk2OHHa6QtcRDQhsOPk9TDRVMIceO4ACLUN87A3xnPad2hqsl5gT1ZmB5nbpISKqGUBikei4oXNSlSqwNDZlkVVvrbe0rMYTsCkZ8i4UYRGOR4nh01c'
        b'ifN0cQwq8n0pbpJPxUdRME+uLYt7jnFNS/MqrxogDoQ/XpeCObyEIonV2c0oLSSKDhlcGLbNa3Bd/BR7jvFh8OwE2EEAWvR7V0YtLariVZGR52/zBQiFburmrpxJtu/q'
        b'2b7DkmnNyJv+SR2CgxcENPeWv3WJDiEbzagcGMX8DP3sJWCL8QhRZFWHWw9Xz8QOEbALUoohQ6UiXF/EdBb3s9m2BUU4p6yqDXUs8Ck9M9VYEYVHPiLgfF6Yb5un1of6'
        b'Dc00ZiZncCGOLFpRqYv/CaaxFN6/1E1MMe+sbtJyOn3nGBX1eYLQqkJ9+jhzLbgGsR+ZKL8hsh/21H5UQoZ3jJkObwN0J8Ld7AAAo6CQDufOdTzpIADQ2s8TLgc7BfaF'
        b'ggy95mTzCeZB8aJiYXfwBMY03QRaTJwoeDy0xrrSL21ubG5Z3ZwbO9Nzh+X5h3XJV+X5UdooqwU4YC5aegyOqeVEwnAG2mYyFWiVzeuNPUcTPc2osoPemaGAX+Cwpsct'
        b'rGSDR5/Oy0Iyv3Zgz+GN/7QXdMIeEEfpSi5emkfrBk9nPKcFdlfPdUhMJ8cwOkPog1+QKVxQDkoE7gsCEhPfNMBRUAul7BEQ6JtEqax6eGN5qJfhhXYhiS6AJkVH54Bo'
        b'WuOYLDaTgaqWYNLOWKbQl7hN2Te380rI/243sgtjJCJPk41WL/BtVC1WwDaw90mGXhZrOHXhyp7o7ffCP7pR3jnw9Y2mlMAmpQ9IHgI0qYscNg5Ypx3q5sXpD83TN6N/'
        b'pJwh+RmS9tQkR59+s/EfRWuNISFJRGyayAdzaG+iHvjmdLQDkWID6SB1E+TLMX5cctQ2t6WmsbTe561QEePtgXj0EPrP4RhnktFQ/rSAoPC07xilKNA7EuylI0sOVhRc'
        b'LcSYk4lJZ0XDMY/NwKOliq5UjEWbq7R4DVf06Casy5rnL0FdNpwrEnbL9X7MR5sqaq2q9qOIPWojfTelXo1aUVO8pS0QtXiaKOwKhbiNWj2Yw6vES/6jEuZQ6/sgOHEd'
        b'/Ll7STkJO3AThiDza1PMQeqbvYcwzWGOE0ZwYAqQyNdCk7i1yWHcawCDEDIv5povN0xL1/IAnXhuLSBmDRaA4KI69Tr8SlbnLgY68sBI4oOxsvhGSb0yYFUEHHN4ZlOM'
        b'0s7mEMahQdoSbqULKE+JjfgCSMUYoqdSCKDVtLT5FBrsqhpyhJ+Lg/Thbbfiv0MzFubbgZaB4aQhilqaGmGA1RUkSapcQCRp1OJVVQA8PnzovKStGbMbb/w+r7fVAHlR'
        b'K5w1VNSKfvdxVMLa/y6Zmqq8C07QZNrGAtlh4iygifDaxNj44xf9G3EUcYxdoo5UaFXCmuTNkVdHwixI5iwYGmp4NFqoM2yBWOr9sS5b1Ca8Jx7L6WRcWzM2JNESxwvG'
        b'eCFrk2INZTn+GULFEMUYmwXwnKv64wWjZx0vALJUSzdbJDluXdLL/oemIK4+XJgG81VgzFfiocPQGFa/JHSQ1HZsS4M5OGpjrGmn28F4PABvkaWYbomJR22EVsPkueMa'
        b'aWTrpbWL/9FzASHpNIPpJsMLh4fpLKLwMH6wRGpR1FLjawEMEAfO1OiQPN72mj44owBiYO8Ojp82x+n7m+VBOh/hYT8nBo0MTVUQLx14ueb78Cyx55+a1KlNcjlcKU7k'
        b'W1pJBKU9eF4Nxkyq1DtXoRudC64os3CJDaJjlL6p19lgNX7JIDTGAEFlaglIzxgTBBUWl0pKcoiFcBFDcshWKxNr0g5nRAojVikIC8ps7HBeME9hKLmJJ1Pr8t1RqXT+'
        b'rNJesC+GayA1H+AMLIGk20gUmjMHv9CusNAgobkwpS2KEJBZyjgjTL5ZV8L8NVjZWbmr8vxdiZAwIllD0uSkMW9R6OWytarOG3X6vQFPq9qitNUAnu/Erz2LLrxkQVll'
        b'RTQB35F7VIBUCR6PEezZ42GK1x6MFmJiazEz9DNNJNY9unu1u0n7FCBAIlbbN9HYH5PVsADsSlkALcltqmomb5Ho+gQBQqR7XTMnJqejkNizWB/GxKCDsNZNTenxuqJH'
        b'g5DfFfNYEo6bO9x36Dc7KDCOToOgLg8DpYp3qKENlKYI1Cmc9euZPjfdd4iAv4sZHGoO01M4/ffJTKuBME5evS4MuKNiWS9sTQacU9pnDQrmKXYxdwl3GVN2WoG4OGpy'
        b'/4X8fuTlLbhw/vm5f8HuMsW+dtVb6yAkPSqsrjaWQ1QGLKC1LUAjFrUobU2tfmZ/iuQUyf2iltUojTf4dgyq0ZjSJ0Ltiu9vcKxuhU/GW0xFZDIollGdhs4tN3GcgP5L'
        b'oDlgDYvaZ3t9q7yB+poqdRoWQRaROAk1JrMJ/yXFzwpC3yBhAIC78zQviJuTSjKMuWjsKhpjugd6CPB1Ed+E+YAFKENLGofKmegOgqUHsbRNkTvsirXDwfgGHQkw3wmk'
        b'xPnnDlSycGZxHYlBu/qsmS+YCLOJHIlbFHtHYnMOpR2QflRJgLdm3Tase2Vrz7YEnUHAQDO5Rk79FZatODO4LK71N1CSK+jaxqtTlcSgq9GKd0EXqwfuc4JOuGLZVgOC'
        b'QJmKK2jFMhWxww6tcLFW0JfwHpWnWZ34HpU5FGvQEkwMOgAbsDfgNaHBqaRskaE8h9qKuaC1Mq07d8UpNJw4hXOw8BTO+Ieh9Ldf/duCL2aUErejS5w2bRpNXFT0APTg'
        b'FzJakc+N8hdErTNb2tR6AD58Wb4QtTR7V3va2c+a/ESm+O4gBVVffbPXz4BSU5VaV9/sj6Zioqot0ELAzFMNsKoxasOHtS3NgN2qLW3NCpMIbMDVKtV4fb6odNn8Fn9U'
        b'mnth6cKotITuKy68bGF+ElvhJOKWqACJzEws/sAawI4TsAGeFd76uhVQNGuNAzN4fNAcr3EPFC1UYVG90IqoXM34J/bmtiYPfcEUaSW8h6fe9gA9/qdBlBOYeiSpPZ+P'
        b'G6iCNpDNCLjoIhRQIsYCo4Ilg0lHplboqEPIJmadTF+wTYfbTebk79AECw70ZNp2cRX1yWuhM0vleu4wkvJkkywa6Zw5ihDh0HYoIBIdheepDfky6w3HF1loc8ErcpBP'
        b'Z8qAkmJFmBawGMxROUYti8QitdEJZ+8aeEGVirbDueNbaifnokpXLnkv8Lc1qQ6Y4a7C72NWXVySO2JMYV4vjCqmlIXgieygXB3QC8YHMCygVpj8OlQcNW2gxvdBHSFe'
        b'3WKJN34aQgOMzR8/uS/bp1Po+KBLKsjzF9C+qQAy+gPOYMuhRY1CytlREXobddEqrwcyvabF16Ia0JwVbtJvJIzqPpnjPSPx6m9iLf0xfFpvMblT6NCIbPJQBmDAYqNY'
        b'QnB3kEjLBMXqTXy/CN8m3gD56uO8UU0ci+AHekbqZhZcC+WMsMSYBclWm5TpShtN8Vy09Qtn+fXjNQmtK0VO0G/jh6brN6BCWgwBIE0tsaKiAlW0RIoUXZYgedYZZnra'
        b'Pu0IvmPes2wUa5Mbu6iunhtQCKNWWp81bb7FvxEwON/4Y/MWfr04tS7tjpeUW0d8/E1O2spDCfdes3HcyIftA5PFT+orT/7xsgWNTeVHmkZ9kvTS5D99YP3W+vfKE799'
        b'YXU0x7Xr1r99+s6fOE/LLPuIwM7MFbfe8sbw6jmNzz6yKJx1xbAbnpz3SsPNt7w+uXp5i3vKI7M/fmNA9a5PU576YvpDF30YOfHkzI9ff+fZq3+d6/rDuJXzH0gN/TVn'
        b'5WWPhYcvHdb50dKb2idH92xfsuanfxu3+THtS9tvD3418dqXFr31WXXSgtGPHD/428++nrol4cvJKVe9v+XFWWnvDqtdWvV6y9ZBy95/z137yTcbOneMH5V3qLTs8ucH'
        b'NA7O/aP7E+vm4xsbn3/TVj1k3ba3i088PKLwEmXukoKHR1166KWL34j88fGf//SsJ3e9MuOuTfdZ31/4o/S7VqY+dt8DhV9W752+473OLUOqbrBP7lRv0Y8fmrXo6pd3'
        b'PPLKg+vzluwYmrVLfPX254T0ZUPT2w5mPfL6ztSli/LnVNlf/mvxHy1dF/z6gavqpjc3fjX0d1dtH3p30VZlWc7LV9/0E8eiJ56b3v7J/nN+dnzRJ5Vbnhlw5Ok5rUcb'
        b'7+a/rb58540nlfO7lGtSd71dfv2aVW//5auvf/Xx8SGrW0/OfaE4770rX37jqRcfn/pY2+I3vZtfmfnq6qQ/ftx64tZ3NyzR9Y60ZTkbR0Vqz1smJ0WP33Vi9t1/ffH4'
        b'O5+Pfeo3H3T8efTv9r/zs1vea3uwdGvNJy+WrF5Y+sHu12e/fcXtm4qfWPbLc74Z7ns8+9dvzhhd+sDtb6lv5jQWvzziyDtvrXyzqkC759CLRVM+ztvywlvHnpy97NtL'
        b'GxqSKrOv+ll0+kOHHZ+lXVq395EvC9//9L0fv33ukU8efm+6vv/o6swpe+6sfeSVc7NeLjzrS9sLzdrPCoI33nH1xtd8k5Z8NOPRjcu3Pbfu7CeHvvbEd699fv0Tlwyv'
        b'Gz/pD2/vqLvv67yn1ZMvH5n/1Jab37d/4nlv0MnyZ7Z8dXvKnfd9Ufz0lA8fu6hm78mK2bkvf9eReLHtXcuYf1yw64/XnvD9+O4Rw45P/eIdS/Huu77a8yb3271dQ4K/'
        b'faOo9f7F97zzwJiqo10Hr1r1ubh8/MnGewf+do36cNlrW9tnvjbo1/fVTVgx8tRrS9Z1PnG1tqzrNw9XrDh3ReDvD6yvv2N6+XOD57325sQd/9C//WbyT0bevHRb/eH3'
        b'6/7++1XVf6q5e+7SwZdu/vSlrwaMuq/1wGMfLVlw7S93dNY//fDML/826Dc3fv5q4NWpV7x6+4FHP1Rufn3a+88/6t162z8G/+ml4AP3frH75ee+e+zc555Z8JnrhO+v'
        b'KfnDH3oaSJsEMpJ21mFMlHnFZdrmMUX6NbOLMIq8W7tB1B7RHs9ifov36Tvmk6/ViuICDFpyeLR+TNB2avtnkGftcdoevdMI9Vx0uRmZlUV6lrWNlEeR9bv9lZCxt86j'
        b'dlj7EXMteW/qXCYxtc8u0jZrBwuQZZmkPSN69EO+AOrp6Ru027XroB1kumgUhfedZUUlWidzNqVfpz/FRMvBcx3SFfqeAHqlLtV3ao92s0RXlq1cOK+8SN+Sv5I+jpdI'
        b'ryt3cPr9bQE8jLRr9VvcPRQH9Ju1g30oDqj6wwF0YKXfvyTdX4JhAPWtbfGS71gl2t0VrJ7V+m127VFtxyhywOm8Ur+nL5at9iPtGDJt65cFEFjrNzSt8Gs3aZ3d0Hp8'
        b'OmBhP+hcOOMlf9K/sLD/Xy75Q9nJ/e9+MRlQvpYqxQh1iEgOVyXzsiDzP+DvP6XBLrsLdZpF9t9tB4zYKvBpbrhPFfjR8wV+YDqKuYcVjpiSnemyZJ4nCQKfyU/0CfzI'
        b'Nshlk0gMPiIZr7l0zR6CV7eFrlBaph3vkkW8pllOv3fazCf4f1g2ptKd9N5FVyhzZIsT8fbvJMiB7c0cKvA5kDPT6uSdVFYO1TFyGV4HTsBrQYX6k5iUbMP/Lvp+Lt2I'
        b'OY7WlZyJ7h5oj3fvkAtPtP36zVXaJubwr3KuFtG2WjlXlqh1agcG1+t76lPSf2Lxj4QFubpmSvH2l5rfGZt8Q1nZzuMvfPPpW5Ed52za5ZvzZE6X88SXC5PzCzbtmnDR'
        b'5FD0x6898UXK7yf9Yf/WX1g/CidKn31zzp1ZifaOAXNK/z5/xQV5k7anzw0tqX3yFeH1GtetWbU7To1vmffVFWMbR/5955/HHtn6i5+6P734gq/ePXye97ElP7032zJy'
        b'/teVFwz46LqOFddtuTwhdUT1B99+1ZS//NQ4fcOU235XsOv5heP+49AB+6LfvDfk0gPvLrlnu/uh8vKjm6de+pHj0uWTt67be1ZDy/B1c27/4uQv3k/N+nzXiobilx99'
        b'Ydi2V35+/a8/XDPjyvR7ftJ4Y2d78c/v+I+bJ+86+vzgQ3VHtFXaicKVl56cPafqzrbOzvvOfqviyNlvv3rk2Fuu+459/Wzn4ds+KL9ozZSstsXTj6XWDX+z+feHly7e'
        b'1vjhpz+/1bv3/lu/aN8XWnjym4VvDD9356mXBn1+2dZDh5PuOZB0qvTbZ7bYr1iSc/HLf77l+Z2jJhzdfcnJP9/U9Upt8OBr+TWNyz7OeP/El7cembbn5Kb/nPpES9NP'
        b'dn5w+ZTlH5W7uzZmf9M86uk3Jz3yQEv9/TM/+qzjlTun/PKKJ57Z/cKYOT/71ZdPeeq2v/Ly7Xdsu+7rNx+fUpY6fs2au9dW/mn1ryL/WP+Rf+oX3r/eWDI093c//uC7'
        b'F2fK0wXlxpk5lrSLn88puOfADecOXHHg+onn/uFAaLqcWT1k+OaV18yc27qhZveVGxfs/l12xi1VnZadjz874P6V65dtePyqxxeLZ/+q9uTVv29p/2mdJ/LasMf+YX0j'
        b'+tanj36ZPz0wFJfVBu2hK4xltVnfVGSsq0vEmdrucfpRbRvl0u+4WH8Qc5mIAGZKKanXjovaDjhyn2L+BZ8anB8XflF/uGEyrz107mUU+O0yfUN7oXZ/UZK2F8hO/Vr+'
        b'Su0+bTvFjczOySgsL9a3pxSg7yMMI4UllOubrNzQBRa3dq32BLUiQfvRPHSgzWth5n+qpwPtiyawYLe71wwqh1z65nzMVChzSZNEp/ZI4wrtNhbl8T4tVKFvGjNb3wKt'
        b'1K7RN87mtaMX61sotJx+7BKpXO8cXdgqcEIzP137kX4/4QVp2taMQnTJXWnh5OVXnie49BuqjbCRpdpjhL+NLuY5WdZ3tgvjAIMIs/Y8OVrfUY6v88sA3bDpd8KrZwQt'
        b'pO+dxwLuPQgYzw2AIxbpJ1KA0g3yM6CJ26jSpVdfqt2rbyzSOq+GN9pRfqF2sJgFAn56rLbZdBfFycvSBwoOQBnvos+sSgJzsveAfh+6iOZLp+oP0TQUajdrYX1TZQkM'
        b'8TM8FLmRv6hxFcX94e36bVBZGFC2gtn6ThgERMcQ/8qbYNG2XzZLO65vDSAsmj/higRAVcuLHaP1jdoDGC1zoHZC0h+HIda26UdYuM37Zf1GfdOwYBE2sRCdb5UDRpqx'
        b'QjrLN41hWgf1cBpMxJxpq7Elt/Cl2hOrqJXaffoxDFgcHpOv3Ywh/u7hF+dU06tZMJJQLGBx+mHtUUDQ1vHnJYwhPHpZs35jOYFHmKZ27fF8GZbMtYJ+1/wZNBP6Q/rt'
        b'MLKbKiuLy3Am51k499rzp4javWNGUAaXvkW7vpyFMK2sgAmTOdfVoqJtmHV+Di0Ohx+Wy6Z07xiZ4xegx50tRvBAPawd0h+LxSWdqj9YwWsPDq9kcUfu7cD1ATnIaYU0'
        b'MK+ax7gi06hDDYv1u8qL8+fAd7K+X9+xQEjX9ucwwmCzdsdUtpbLylaOhdWToN0i6Pdcpt9ESL9duz0d5rJbE1Ti3Bna3dp6Ub9Gv9lO07AUhum+8rKismKjcS59o1is'
        b'b6zQntS2sm27Wdut31lOgU2l+fqNEq/t1Q9ox2iqtevqtKOsX/NgzPPLoAr9aFDfIWpP6tdACSjvvXpdRmGZdmR0/pg5gNIn6XeKgGlr16wCjJ3Ns5hWXji7DGHCrdoz'
        b'A3lt/5AWWvpV1UBJbMJtDwSNVKRfdzGvPVUxkcZae6Re7yycOGuOhePLOf0W/VrtBpqlCwf5YHHjqsIYA3fnzYVhCQr6bu0e/Rjr0EFtrwjLhCI5SjAUDyTz2m0Dx7DJ'
        b'uF87rG8vB+ro7PE8Zy3QNurbBXm+vp+N+LbqLMMrpOFt8Cx9w1BxirbbyZbQ+nU25pHR9AV4rUguGe/SO2m4k13ak+XkP9jcmi5tHzQmOBMICspRpd2hdHvqzIQRiTnr'
        b'zF5EhAps4736HXGOMg0vmfpN7eQo86AlMAayDViGlCUAzAO2YtgpBTAYsF+3AyCZS2OzubxYOyxx87R7rfq1FWfRiilL17ckaHvdSIa24sflCJPS9N0ibMYnvAQH9BPa'
        b'07MT9M4xxXMq2jBPmX4MUQ7MebZ+W8cyucy/gIG2jdqdMgG+ktnzYJx3lPDQkwOC/thZFloY69oXkM9YODRqJpTgdjwq6Ef1PfotRJBWNGr3F+qdc/Wt5UX5xTDRqfrT'
        b'+pYcUd8BoOYIwXyvVXuwHPcrjEakrGjOGKhJ5oq0h1ZyFv3WJv04rVKnHRbspvnafjrHtlTmA5mnbcFDKj1PEr2rGUDaMGc4eheurKTjRYuUW6FBD8N+0veOo2LaB6yD'
        b'hQENWoUrEmD2XCuXpR+F8+D6JXAKHaROl6xwQYMAlkBBGOAlZbS+V4dzcL9fv4ZW2Pn6/lIaWjzAABRsKuZhFg/qh1ko+WNrYefBUTqmvDh23mFLB40AUnqztj5F30vr'
        b'v6RGu6u8bF7BPCvAhWeWSIJtVAEb9fvXLSEftNhL2+JiGFb9LnT1ulW783upOJkueSf9G5BT/3aXmEiYSLvDHOIdgmDjT/9zCMkWicQamUAaCbzM/gsSj7ldLI8h7GAE'
        b'n4OpAAoO4w5KAPTeRmWnkYlv95+TSqY88MZJxr42kkc6BVlsX8f1/suVecbgZooLqMrh9wbaWj2ebq90ppRA4+N7ijeM7PhbvCtNetdDVyERlyXHNAX8z8K1mlP4BviL'
        b'LAovQh2yyCj4FeBXgF8RftPhV4LfS8OL6jn4dYQXoflbZAjmb8CcfIgPLTK13jo41HjziU1SJKnJ0sE3yR1Ck7UDJYBWxe6zNdk7JLp3+BxNCR0Wuk/wOZsSO2S6d/pc'
        b'TUkdVpQvBpKh9AHwmwK/qfDrht8c+E2FX7TKleF3aJALJ8FvUpAc30QSgugYnI8kQ740+HXD7wD4dcFvOvzmoSY2/FqDUmSYYo1kKGIkU0mMZCmuyCAlKZKtJEcGKykd'
        b'NsXdYVdSIwODosKFs1DbOzJcSYvkKwMiJUp6pFLJiMxTMiPzlazIRcrASJkyKFKgZEeKlMGRQiUnMloZEilVciNnKUMj5yrDItOV4ZEZyojIOUpeZIIyMnK2MioyTRkd'
        b'OU/Jj0xUCiJTlcLIJKUoMkUpjkxWSiLjlTGRccrYSLkyLjJGOSsyRxkfWaBMiMxWzo5cqEyMnK9MihQr50QuViZHLlHOjVSEHeu5yAhlSuSCQAbcpShTI3OVaZGZyvTI'
        b'QmVGZKzCR2YFrfAmNywEbUF7LY5SWsgVyggNCc2rlZTzlPNh/hxBR8RJ2indblNdoaRQWigdcmaGskIDQ4NCOfDN0NCoUEloTGhs6PzQhaHS0OzQnFB5aEFoYehSWA9D'
        b'lQti5dnCrrAtnL9eiNhDLCo4K9dJJSeHUkLu0ACj9MFQ9rBQXmhkKD9UECoKnRUaH5oQOjs0MTQpdE5ocujc0JTQ1NC00PTQjNB5oQtCs6DmstDcUCXUWaLMjNVpgTot'
        b'VKcM9bGasPyRoUL44qJQWW2CMiuWOzEkksP5RMjnDqUarckNjYCWjIKWzIQaKkLza1OVC81vOhLCrmAC1TCSvk2AWhJpPDNhhLLh6+H0/Wj4vjBUHBoH7S2lci4OXVKb'
        b'pZTGahehrSKVJF3twHnscIbzws5wQdgZdIbL1gvrUYMAnxTRkyL25GpnMIEk5Rcxj/akzc9U8hFK9K9/hiclMxEKc412dWAA3V9wDbypvG2o43UNyPOPzs+tZyqhVbnV'
        b'bfW+QH1zvqC2IfQh0RxSf/06b/LUNhOXDdXMIhbDlpUjGbH6rGmHki8BoKvzBmpVtH2wedtrSDuG7K1R8t1SG3WaGkKkGcSjG44mgIxw50CXz02tqtfvh5Toa6lDg1zU'
        b'IFP/g2M+jrhTpNqB7TqFUsJTaBt2ijN1oVsUL8BX8oaAGuRRsbWlNeqA0hVvbRXaJthqPUykyoz/ur0lxGByVK6lcqIJNS2eKrWOgkFiDEtP4+qWZt+a2CMHPGpmhUWd'
        b'cO8PVBkeJ22QqvVV1fmjVrijwux00+wP+Okt6b1TDauq1O4E6tdiir6jGxc9Vf2k19DcQuX4YAKrqtkHqte7Ch17YwLVFihhqfF5q9So7KuCCR4XFavr60hnHD2zsIAP'
        b'UQeGCWb3TJPneWOSA2pVjRdDCno8kL3awybSCneohxCVPKq3NuryKPX+qmqf11NTVbOCqQTDwlCY6zBEWruE0fm94rvhYkYyg7lpElhQGdSLQidH6JgUpfyzUJ4ukNWn'
        b'sB5I5ZUDg6YmfN86gP/UaREuzvdiCmUGNuBki7ZHG1FzTDbbeBzehq0A6ZywsbKwJUEeYJBQi5YSOQqFcSH7CTGcS9pcUlAKOxpt6nVhZ4clKIQTGgV1NtzLzaMpxanL'
        b'w84ErsMS5pj2V9gRdsMbF/TdmYFjIYetkB68XgjK4QFQo9D8o6CgbodnOeH0WnTnshO1uKCeVKjnfsqdCV9nY2nN7fB8SDiF8v1nOAXgjpUMzDI7bJDTGk6DnBKcFTDW'
        b'69GO5dmgBCcIT+XJjbZtqMcrw1d2KncQ5DLdvzigBOPLoB3uHHhHIW8gvYBj/Q/zVMbV8G1SODHBNHETw8n0NjETndUCYahwwQR8FxQA3iZmcMz2irxr2pkj/Jh2HI0n'
        b'lLkH5sERHgi1CzguQUsa2p5ksnGA949SizPMkQgKPdaL8/9QDPL/niv9gxjXuKo/6Vb+cTFslfBVVPyRBRup97jhL1lkUXiYwg+LwSMDfpvJS6JLcAGum43fiQ6K2OMS'
        b'emyWFOP8oc2CMXZps7hgqvONzZIWv1ngrYiTF5bgjBrbY/vg5BXCNxLd4cK3BCX/HyhGuhzGv3SYdBEV7YJW9bqglQxpbEGojS0e2C4Dp3LNSnhQeHh4JGyCrFoL+iSC'
        b'5Tu/wxFGJTUHlJoQdIQHwaZ8ExZeUgKXhQezCPcuvA86adtBOcEEQBGTjAVMqnvsXdBBsaWawyPCieFBCh8eDv9Hwv8h4dG1fDgF6wkPwc2VBigmPB8Y5sPJ4WREzeqt'
        b'tLktuIhhM6UEbdCbRFjw8BuErRF2ZXIdrrAbEAJ84srgYNskEqKQAF8VUTSqAJUA97XQ406+w9L8MTyRwwVQZlIwKZxJ7wEgQGuTwrmUyjVSIyg1wkjlUSrPSOVQKsdI'
        b'DTTbSalBlBpkpIZTariRGkmpkUYqm1LZRmoYpYYZqcGUGmykhlJqqJEaEhs3TGVRKgtTtUlwOBQjeh/kOhFsIhCAvoZHhROhx8nB5G2C/2BQoqsVr7RWMnCtQBkw9rXo'
        b'69roTQaHJn4wnqm4xqBUkZwTSDjyCLzpeWFQwudByYwc0u3HOuX/yr7NL/k3gB3/8/BpJJyy/lu64ROqGQo2w3+zLLoIUrklsijGv28kG75FD6HoecEtCxw87f4vCJzb'
        b'uHd8JTnRAhkdUTkFt+gAOObi+/37THI7xWTeLdpQ0PqtZHGKSOv3gHSmsRZBOuaXEWAZkNFhmwHp5DAXB+nEsIWOd0BgwnYgAADCMWXuHsdSn1jLv8DFPg3wTbJpps8G'
        b'WMQB6dUpu9mpe7BTEmwZxEUEANBu1pH1pLkJeIEFOpmMjijpuRSknNDFxLCMZzUMRRKArEQE4JhCLfWwY+tIHktNCLtxS+JgETgTLQBuw/ZJgBJOjdNPB9AHQBTAPG5M'
        b'vE+GL0jXGoPk0LcxnylnGMDU/9mVfKdseE/kaA2jqZJkdfDZIproDBRxNTl6riZH/MAriGQCQhhOQgQ4NvCSMfCjaeAHAFom+ovoDabTMU2u32fBCnOiuS69c2wdSEOH'
        b'puzWTDIUwFSPQQakLmzNQrNUCU6U5UHRv9FEtXksXQLEEc9fi/oWxj5EaAonlwVOGZjEDutaBzIdyNQuTeICXKND/Slz48JiN9I3mVjCypuICHeFkoEATwtl1FqNSC22'
        b'uFpsCN2hHenhRHxmfs3OPcAm7LCrWDsteI2VbkeWB305H76EZ/DGHvsy1gZAUEd0x5Lry7Ym5jQ2FjIQqRHoMAwwxTZA9w4YXAadKbYUIWbaKJv2bSZnTwhUqyeRhnyX'
        b'/8FONaKuer+npbrWs1pFnWr1T3LM8EUynA3SOsvniUz/b4WxyPp3Av26bFgzmRsmGa5OOgRQ3xy9Kcrox0bAo8AhOijoh4uX7U4x04pP3VaXwbx18/mZjPOAvohYFAjR'
        b'v8avPofPnsfLC3h5kSk9oysZv/oSafiv9dVX48pFw9WqwAr1ZbKThhtvFUYYUF8hq5V6RR1BhQJVHhWrqoGeX1HlR2vqqNXwkBS1+s2bOl9LdZXPn5/4rxmy/MX/Btz3'
        b'/738d8QVuCbXIgkWxXUuCNLpogqXJZNECig+6C3KYH9SH3/OPp/+9/9k438sLTtFt1US556Ne6+2Aa+5Tkkcm413U2fivhRsMhGPgkD9rECLmEc4Ci3giefseTzGjmyq'
        b'aoVtGVDVMM+MbclrAJONPEv77sL2Gm8rOg9WUdyKkpKaqja/1+OJpnk8/rZW4ggi+wztTeBpgqc7oX7c0/lDnFXq1KYWpc3nRd93LNaqBIAlWQBkqC95zRrj6TCBHLua'
        b'aoH/BRFfQzc='
    ))))
