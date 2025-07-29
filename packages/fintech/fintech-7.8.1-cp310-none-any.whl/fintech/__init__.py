
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
        b'eJzcvXdck0n+OP60FEIIiEizRWwEEooV0bUXakARRSwQSAJRCJii4gZFAUORYu8Kdqxgr6vOrNvb7e7tKnfb77bv3e7tlT23+J2ZJwmhuLr7+Xx+f/z0xZOnTHnPzLvP'
        b'e2Y+obr8k6C/yejPbEEXLZVJaelMWss0MTpWx+nocqaZzhTkUZlCLavlKiiNSCvQCtGveLXYIrKIy6lymqbmU1pRGsVROo+SGJrKlNDUaplWpJNkeWrF6Col917kKtNJ'
        b'1tNaUaZkoWQlvZLy0Cs8HvSTzM3XyVNLLPlFRvlMg9Giy82XF2tyl2nydBIF+4UIgfaFGF9odGmnI3Jptxaw6E/k+DWPQhc7pae1qA0V4lK6iiqnSpnVHja6HEFpY8op'
        b'mlpDr2HS3O4RFPkKVp3r3i24wLHorzculCNdk0Yp5Op26nv8eW4BBofKFVDoV946pqTgK7/R1Gd83m8ntVA9QkgKi8EQMnbKzupZF5T0E0Gp7wqls/DOUHJqaySuEZyB'
        b'LWkquB02zoVVynmwCtZGzo6bGxcG6+BGBayGG1lqerowzBOehReMhq0+awXmcNxubsFX2V9mF+i/zv7v3FCd8mOVJk7zdfYrOX65+foC5tz6oJi36HV5osTQfykYy2CU'
        b'A9wUFXiiYsNxocnWUnhMFQZrIhlqIDjPwbPgALxkGYDSjUy3glrQMBm0wYZElBLUgQYRJfNlB4BjcJ3JAyVRsO1MqMKE0ZK/4JcPfCboTUWrdUa5nseOie0yjdmsM1my'
        b'cqyGAovByOAeEKKLNEhGc7RJ6szawrZzeqsxt12UlWWyGrOy2j2zsnILdBqjtTgrS8G61YQvLbRJhu898QUXEowL9kMXn8+FDEMLaXzlaOEv+GodghvfQoHqROV8eChC'
        b'rQoD1Snu/ascKYAtU+kCDEp13gv0KwIq5sPJpUqTMSk6lyJYtGSyhbGIqeLbyoacAUUXZQ4s+nAS+TooYSn9NkP5REkK+qaIxvBZ7stZCg/3G7N1yi0xAfzL7AwhhSD2'
        b'Sc1eqrzlvZgiSACug4ZcT3BcicCpgg1pUXN4NAiNUIXCqsiw+GQZuExTixaKk+A2WK+grXKcqwLu13qi1iSqJGsKQ2ENOAuOc1QwuMmB3fCC1DoQJYK7or3xaEai9uJf'
        b'EQVr4GbPFAZuhhfBQSse8Dx4AVbjjx3jPRNu5Yd8IadgrX1wQecneySqFAnJAioIXhGmMf4BwG7th+E4A87lJ5L+jI9XMZQRHPYEOxl4HJzP5mEoCwP7YG0KrElIjoDV'
        b'SeAkR/kO9wTlLCwDFYmogiCUavXqAYnxyngVwc7FqBoZrGHVUnDV6o/L2AMPgGOJ8TZwWRkvoDiOBgdGp1gHkaGFR2EVj9XJ8bBOEY+Kh5egHW5hwbUicBj1V3+UTgcu'
        b'odpGjERJEmF9CirFGzbBG4PY8engMkqDkaiYhpdwkvhkPoWsoBCeYaP1oFzB8J1+A7SEeMahkSqGtXBjYrzKAvYylB/cy8KjU8FW6zCcaGsk3OcJ6yNVCWorThYPL8Lq'
        b'lCTcOzQ1eqEwHtH7UdTuvihxXAo4DmuValgfr4wQUrAVbPME5xl43rM/GR24D+wH68JhfRIaHqVClSCgegfDqgEs3BILtpEOjgbn+iemjO2rig9Ho1Adr0yIjIhLFlJK'
        b'SgB3ec8n1YyMg/sxKOHoSwRNjQfnPeFBBl4GTcOsYej7VLAbXEskKXDjU0MTEXeohxsROqaqvAuF1DROiIbrGthiJcxkIzwViFKjVs0OjUuC9eqklPRUFeJmjajeWMGM'
        b'6MJOTJBxZ9VNhP/bacRhWTtnF9iFdpFdbPewS+yedqndyy6ze9t97L3svvbedj97H7u/PcAeaA+yB9v72vvZ+9sH2Afa5fZB9hD7YPsQ+1D7MPtwe6hdYQ+zh9uVdpU9'
        b'wh5pj7JH20fYR9pH2Ufbx+jHOrg4VcUhLk4jLk4RLk4Tzo14d5rbfU+yxtvBZjpz8XVqvjcuagclKqdlPoq3iGEFTwkbY/0INapVChW4AJ8BVZgkfbNZcEYIKqy4cBMj'
        b'grXUJISlLMWspSeL4AZrAM67FY1KOGhBnEwZhygAVNCwXB9H0BY8Aw6CW+EKFawC+2EdQlwhOMGEg2eyrIH481l4CNzCo/V0LyUafC6eBjeXwouEssAleHBIIqwuBNVJ'
        b'+JsHDY70zearPAxbliBGBA6ExWFwuDganJ8r5LPtBzvGhoMrsC1CwVAMuERngmfm8rR6aiTYkghOKOOV8LRKSAkLmFB6GCFyDThYkIg4VTV8BiJ2g6obTIPTPqCG8JjR'
        b'8/xgLcG6cBoVWU8necNqko+LBacSCbqBI/CykqaEY5gA2AyqSIVWdNcUnoDIcWZaCmr7ZEYWifCUNH1zBFhHsDr06TwVyreKiYa7YZkVS4sCeGVJIjgJm2F9KGqDkZ6o'
        b'HEIaPgZe64Uy7QBXIhMwJDvpmWAP3Mizu/XRawidKDA5i8Et0ATXM8AO1oO9JLMJtoHLsBaNyflkJcJ8Gz0J7HK0A96KgrtRjYdAOazBH8F5ei5ixNdIO9IlvRMxIxiB'
        b'RO9GjhIGMxK4P5WAmmLDA2gCDXHgNMpWSs/MUZA+AzvhBhWsjSpMicCQ1tCzQG0kYRzgaIwRMRZBLunQiHjUPWoBFZDPjYBN4CxhCginKgMTw7HoSMAD7CH0gXsYsA3W'
        b'DMtl3JAf43tn3QhpRnbapRsxVUgDKmURVTGEqlhCScwaNs3tHlFVxZPpRqza0Pfoeto8Eb2Yuf/Hr7Jfyvk8uyrvc/TLvblx8m6PuJG0QS/3enaB0jNj3YTtlRs3SvtP'
        b'Xrbrv/rG2EuyDdnC1/yptwWyPRMGKUQWTHe+oGouL+BgXYoCEQjRabLCKP+hHLvaZHGI08vgvLsYXNzbpfiUw71Eh0qF23oTAlYmI9ZYjdKNGe9QkAaCTRzcFDCPFDYT'
        b'7AUNoHYk3AAaUjDW1uMkEtiIBhxcgxUEKpSiAt7ExaEkSRGgGlyNIDWy7CC4e5YFIwz7NNwfroqDVcvjsdwTwwsMqEDocdYylNAuqEgg8HSIB1AHW+AxXM7QMEEKPNHH'
        b'obF10aHIW6JBtXOFGvMyopthrUq8Rkzj/zJagnW03s60Cq6d1Zot7azZlGvC3NDkg98yHUWie4yqpj7OkknmtZRTNyvvQTfDNBoOKpHcqE0eZVXCeiHFKRFLAK3w7KPV'
        b'8zE8CjJ65n9DOed6QsB39phocwh6cWd49FfZi26/cafx7r07jc9d6HeqcVOvF2T6D5NE1OQY7sdJl5B+Tbhl89PwZqIyFLHKRBoxhpOpC5gS3yJ+qKvgJrjTDbl2T+tQ'
        b'q4Pj+Q5meh4dq8VQ4NKcqbU+YjQq/lSH5swW5SzteUCQnhzoGgucpQoXg2+odbL/9jAauBnx4MbacBXc2w/LL8SgTTRicc8wnQaDdvylOcGyoVtE3bSaBzzI1YSOdsiM'
        b'RVlFOXqrOVdjMRQZN6J33+NmcYw1FPfQrXR4CLHV2klgA+6llIRwlVqNNWKkgrAIR84LEOc8q3gCOPJ+FQ4PJxC6RvwOs0HC173hbhlSUkm140oxsfnCchbchDfA1Udj'
        b'YizGRBrjIjIVud+Ijd2UDJrqiR0KOidyMuOBrvoJM7ZzrvqflB3n9VS/pCdqqLSIGfN09CJUu+nkx59nf539gvbz7Exw7/nA13xeuQ1SQari7gupL99+IfXuO94H7iyC'
        b'b7yS8XIqfOPZnYzfydzQPGXeh0kspamXjqzYoaAJTWhB1XAzOB2nngSfQXaOY6B7wUYWEb99oYLmmQrXlXF1oQ9BVq6mgCcQH0IgjL8PYl5ihM/iMuaX1cHmfIPekqUz'
        b'mYpMERMKilBq88QIksnJ1ziNKc/cLly2Ev+6kVI3u5MxYcFqGugiKmxXbO8gKt+veiAqzKwWqOEWpMLDqqRwpB8Su3sgqISbwXnU7uoUNdImkB62BdSK5oyjQM0kD3hZ'
        b'BS4b0qdpGLMC5X9+2gvL8vLzCvLUuWpNkmbpTdNHx3WfZ5/QfJ5doJfoP3wFmTdtwrP2E3yTnrDrPN26xp3D9JEITYNcSb166gpTL1cf4JRb3frgmx76gAjhsTFuXWAE'
        b'Zbz3oS+4xoHjkfSjaaybu+h3Uhf+x3TDbk4913B34mDajN0EcmZhogbrGnEabvNGhXxM753av2WLCbPPuyfs3bb2SH8FR9A3U8wz9BS1UqUmzBycGEv1AhdYUC+H+y3Y'
        b'SZOfhscUi+caG7LlQxNUEaA+BXVCQ3g8OB2KJD4SARlZYn0WY8HVD4etyGwmCgFOMwse6UgWDLdxYH1hHNEvPNZKSLmKhKTY+erkBGSA8SrGkMGC/vDgIHc0cBtwL6sx'
        b'N19jMOq0WbpVRMMzS8mQCwcK8ZBhgR/izKJAogWl6qCHFgda0abBrsHHqfd3DL70k0f4X5DmdS0hnFjecbmDEKlvTExGaIDIX0gNXY30lAvgVKfBcmIAFklOLkfMxd/M'
        b'ZbvJfI7qSeaL1QW4L96QicXamZRct/bVkgLj68YleWNyIyeLeBkBz2mRKa4CF0FDPBrZixQysA/S4CJsgg3EezRB/b332z6KgUzqh/QvGVmZm3mvz+2VNENxL0SLijVr'
        b'31sl5F9mCXpTQyjxMorK7lcR4UsZ1n76EWcuQl/u3tmfqNFqjuuO677OLtZUXTyl+xLR+pfZRn2Y7wlN5u1GcKGxV9hzYr+3TmmYEx+f1J3RnNL4i75khgjelIZkx1be'
        b'p+MCEvzP/TGqz3327q45Gf0CW1vol1rbR77NvKp8R3hCL9Vjfiz17X/250mIH2MpGI5Qb0+i0zkC98KdSIlpZIpgs6hnTvJY/sLla8z5BMuGESwTDxcjpRL/51VMCc38'
        b'zAmkjifuJ6aME5iGduAfz207+HHPUNB8MoKOOPNRN170p0coOWPA9ZmwNm6oEmmcCBn6IJsXbIfNj3EI010cwswT4V83owf3iEc3/JOqeXvuMjIfNyPkQjYagiCSipwL'
        b'Kgm+CDiOOLKjBusLRg0z8Ui0LZMhuExxhUnBqmzKhFl4T5d2Osvw1idfsmasA366y1f1SrSEifap/Og/w17UD14xb+HT/imtlRn3q32lkvCMz9eH3n9p2PNxxqXrX/bL'
        b'im54+MmWIerA1g+rfnwn51NlQMnfq1YMD515wyd6V+Wm+2HpNceDGotHNpT++O76l/dlWmeceO9E1jd7qvPmr3xY827qDxPeXnpgmnZQdFFISO9bGy6ODVm0Nloc8pL/'
        b'CIWnhXjw9sWCA7xyPEDlbqER+wxWCAjD1Y9bblYqFLAmKUwVb+V91/B8IBW2UABuWXtZsCwGbTrUgefBkTVqcNri8G97wTJ21Eq4ldfEt8KNyGSSg2Z3fyeviKeB8xas'
        b'ME8pBq3hEbAKVmNPA6hn4EFYr5qTZxmOecBVWKnpbAO6LMBTNmIEgutgvQX7ZeCW+MXhCSpYFZ+kFoCyUMoTtDFw31x4nnBxeA27bJFpjjj8TWWYIgI2IIWXogLl3BKw'
        b'Hl4j7viZcE8mLxJQZUQURE/lLclL4ARFKBfugBeVyPKAjfCEy/pgSuAJWEeMyAVIs24JV6viUfcxCLlOUFIxK/aH1Z2st1+xEIXF1pwCAy8wQgkpM7Ey2gdRFvNQyPgh'
        b'quIcRIzJWCiQ0FL0HwmT4a5yAnqsIshFuTjl1Q7K9XnhEcZi3JCV4aHJsAZZzEJkDrf6xTOgbDo4RmrJFbqRmS/6EzvJzJfFxoGNDqJKhVUim7CKKmdKRTaRedhqkY1t'
        b'omzCZrpUPJ8yenCUhS7pS1P4/wLK6LkS6cw2Mc5nE+ISJlBaGuc0ldkExeEGqlRgEzQxzdR0anHyIqbUo1SCy7d5lDOmUlITh+7m2oRNbDMpo4kjaaWlnlUsSudpY/Ss'
        b'gbJJDtP1NE0tn2kMIbmkCD5plYdNWE4jiCVVYnxXTpOcYpJT3CVnrk1qWlEl5XM4YaUJc1keha+kXE8EzeYquopaQZk2I2gEWqaZdrTLmYa2CPUMSnekypOkO1LF4FK7'
        b'pBKiFJeqBCQF+u2cQss2ibScVlCBbM7pVDmNetdLK2wS2byaxFqRVtzM4Dc2L9PrWg+blz9V6mUX2T2RlsdqJSiX2MbiXKUy1G5ZOa0VL2NMf7XJtJ5oHGRGH9dbzvS9'
        b'VorrssmaaX/8jdF6lcpsTCMyfRGUNIYS3Yu0MhtKH4A4s55B6byNITbaxixj0bfeWm9873jvr/Wx8Xe93PIP1fbi85MvHEqDa/O2eWt9x+JfL5Rmgk1Grt7a3jaZzQuX'
        b'h78ZRTZv/KV4is0LP1v4McVt8EFt8FvGoVwmmw9um7bPCgo9ZfJPKE8euhM73xdp+Sf8HrWyl9YfPVPagEomiLL1IvD7oNoDq7xwDUslNh8nDDbczgoLbfMup9fTFk/+'
        b'F2lGQeq5D0QFyCA3qqIfMEp5JwHIOIQgsa6xBycPkdBiQSlto5dSm5jlDLa1HZpmuzgry6gp1GVlKZh2JiKqnbZ0NbwlEwoMZktuUWHxxB9wiQyh0dX9cvN1ucuQ5dVh'
        b'nHUkfMDKi0wPaKUJy7gHkiK93FJSrJMPNXcDVOCkdLkTUE88sWzDUpoxM1UI6HLaAbS+AzTEAcOJdFzxK/zPpEKXn5wwD6C+wJU+8NbIV2gKrDo5gip0qFlBxOyDQLNu'
        b'uVVnzNXJDRZdoXyoAX8ePtQ8/EEv8gLful5x5NrbLaUz9wMPeaHVbJHn6OQPvHUGS77OhFqNOgNdv+D9PA/o4Q/okAceQ80LIyIiFqP3WH990EspzyuyOPspFv0ppO0C'
        b'g1GrW9UumYcBnoHtPfQK1Wpu53KLikvauWW6EmQBo5qLtLp2j5wSi05jMmnQh6VFBmO70GQuLjBY2jmTrthkwtNF7R5zUQWkJIVvu0dukdGC7QpTO4tKaucwKrQLSfeY'
        b'2wUYFnO72GzN4e8E5AN+YbBocgp07bShnUWf2oVmPgG9rF1sMGdZrMXoI2cxW0zt3Ap8ZQvNeSg7BqNdsNxaZNEpvHpUQn/LBWmQKS4sFTvR8VU83vVYhjDYEcrQMiLS'
        b'mIdiTuwQeD4OXVZK+6P3Eha/8XeIQiQav+ce+vr4ojc+tC/68xP6km/+KD0WkD40xwjRry96ktESRoq9FoyYvJEx2AEbSCPR+pBBZfsx/qhEVC5DphFA2SRYj02pZFiv'
        b'ViaUKJH+ksWO6x/ayWuPhZ/QSRYfowsSVoyNaqKIAMpDwoot5Wys2Wu50IJUWPxnQMJtL4tFmo2xsRMQ+ZhCkfijEYsPtSFREUQ1MYhZskFUMxI5SAxxSABwWFiYR9i4'
        b'PBqVx6GyQ5HIYrEgQSIiGREhFg0CLS5PoOVQGSx+Qr9IFOJylo/iBYwpTcsVz9ViwSywiUhdQsd3AV87KYeZQJFnzvHMTaCWC22YsPMVAjWiYzUeTTKkqfiidt3hdwqB'
        b'aSoeaNass7SzGq22XWgt1mosOhP2bynE7SKMg4Wa4naxVqfXWAssCHXxK60h12JKdhbYLtatKtblWnRa02z8LglnFj4G29y8oTgkQpvlLHcA7TCSOMaHIJsP7UAEMuwY'
        b'XQJpH/QNoxLShMgs8/nh4GBiGNgdQabeQXUkaFEijCDTeOHgsgBuBwe13SwPXD1WGkl13eZgKTwLq/d0mjg2Os1hQHe1jFyalRZdqvBQ09VI1i+lisUIzVBGUzBCDS/0'
        b'hsZytJz2RHoBkVQIKZD8o6vYKk98X43DbDgECK5egsCR6sUuP6aHjcFIlNaDrxJjNu5U4gb9HAPB2bDKQK1ORxWz+J6oS2EI5xlUGQKtnF5GIbDQnQ0BUsoaPQl4QoTd'
        b'g/EdesPQlLGXjSXvRldhhQbRAVazqoQY6x2qFgIclTywlLWRclHaGVVChK0sUmo4oxDfo/fkycaZ5mPhg6iIlGPjHGXEIGXTFymbnEWgZ0qW0UiRpKnVHOosARbOWvS8'
        b'RoCjrxBtILq00TgfGQ1ajRANmwbtohUaE/FdsnkImRFbNS1baZqCkSyBR8cOdyUW4jz2agn260wmhfiJ2WQH4kqzCIMsRhUXmqdgtI3C2IBRlpERzoa4I+JegTRThjkn'
        b'MgQYDvExZNs/8BWJsU/2oYxZHaXJzdUVW8wdQl+ryy0yaSydnbQdVSFBnYOBwC1CJE7if8iLpfiF5+9l/Wy7CHcgomS+yFxXQz1cAMXQzqkxFkuCAaiNwYwkaHXwo9vg'
        b'1C00uLgCfC/5XXJJ4wJH5KhsNO1wGshZbjARBgJwemgivAzLktRqVahCSHlGMPAwuFDQzfnp4fg1x6GLjspESJbJbBXxfg3EAMR6AU955XQmS96TEDgHe/BAdInDC/FX'
        b'zk5xVKaAZ7ntvRzhgDMNBbqkIo1WZ3r07DGe0yU8R0AiQIR6oYvYud83h9zzpIlITZzOoAacCXCEtcDdsUhewkaWkoETrA88CbZbo1EaWF8MqvDUEwm86wiBgVW8LwIc'
        b'XB0PLs6hqEWhIrgVbp5qjUC5MsAueJzPBQ6NCw2FNZFxKlgDWuaGJiQjQz4iXpWQjLiJt8dTsGG2Fdu3qeDS0jTVvDi4UZGQnIRSgtrl2MuQkhSPUo4C24VDwDbYaHh4'
        b'rpA1Y4KtW/PZV9kv5hzXHddk3N4JrjS27Txboahs2TBlb/Outuq28pYM7oU8YduywNiMlwNr/lJm2x4sjG61eZhF00TmkW8x22XbKzfWfXNHuldFffaO78vZHykExMVR'
        b'CJ8Bx2Atdl4IgB22UtwAGhykIizYzbl0Xv/wiPjODgmwH55b4g3sxIlCW+FueB42WOBGFQ5QW+7wtARbObDBawGZDgVXQxPDI1QIEy/GqRhKCA4zUbBtmAV7jMEF2KhJ'
        b'jEhIVsaDOjIpPwzUKEjgytBZgky4xzX78+QS1SvXpENSPKuwSGst0BFXBbZZqLXUWmEe5kOYK4mJ3rV6YDeEjeiU2zUxZNYV6NEVs4cON6Tg0RTLmIrx/XInVCbsztVi'
        b'ksWdTq2j1vnv7e7YeCw83cjJNUk300lO7iKcRrQqcZGV4PfNBQooN6PKRVYyNR9b0gROgsvOcDEzKHejK5mYp6rdEyOcRAUvZvZAV25EBdaDdVZsZQ0NKeIzPYKgwDl4'
        b'0kFUF4f9+lywttNcMDJRaX1Xk1Q8oUBTmKPVTHyadhh3HGVNx+QRBvebXRAXd4rhg5sTwek4hLU3k0G9K6IEbus0l8eO8DWDLXN84WkKnIIbeoEyOpEEEMITg6WOUJSN'
        b'sFaJbqv4+R3ZHDaaBmWd2iSg3KZ6CefkVSUGD7aLc7JVaCBLOTTELBlijgwru4ZLc7t/FOd06XHunBPPtywFFeAMvB6SiGdtIvjp2bS4cFgDG9IRzasUsD4pPt01lgKE'
        b'EzoJfAZWZBHHdJ03CbsuzkrITvprdhJFRlcErk7oVB4f5wqrHLP9mA0WrvWA1xYGpokIFoHDkfBsYiK8kY3njOKTZ4fC6vk8z5ztqhuN2CLYJoJnwZUEw4jdUoHZgLJK'
        b'5ftPzvnhxy9J9NCL+oiPwzRJmgJ9Qc7X2co5X2e/mvNSzms58ZrN2hdyTus+n/zxH6Oo9HAmfWT5XPvIv3x3Lmpra/qXI0eUyVP3HimfsZceMl/29rt3Gl98486NiraG'
        b'6J3rRnpRq+oCvvJoUYiIF3vxVH6yTwDPdY4z4r3YpxbyrO8caIatSHbUIQbaA/ect5y4hgfo4PlODFJRONPFH1PgZuIaRsLtJriG6wybkYJnbfjqvOA5NnC+hTjE86aA'
        b'NmQoOmcUI5B6EFzsu4aFGyOhw0d9yX+QM0VKvEAKTlKeYxlYJ5Xx8O4CB2A5mafvmKQHDSp+nh7sgxd/O6uW4cn3rGITMt+xAUV49QAHr6bWMmKiQ2JTB3Fsrgy7konO'
        b'OLo7l9St0uU6eGSHFta5dJ76Bbx616EPP25WyTH5JHNlIOwcr7+oxLwi2MHOEUN/0IOnejHu2MtwG/XrTKRHBuKvdYYDsGDzONgmmAGvTgYXh4IWBRUCt/ktBVvAMwUY'
        b'yNg1gdw/fanJ3/Yuof8UKJ+4NuvffBB7s2In3Sqi5G9ErR3x5xEbM+op8nrpsn94b/WmQ98Y9Bn9S8amUhll+NK3t8B8An27UVXcZ+N4WXmUz/SVBZ94x7U0xsQ/+PMg'
        b'kfiuZOhW+si5PYHVyVtGlm0tf85v8KufGZ5t+OegZq+N/d8yzDtVEfvSqml/fnv7KV8f79c3nKx89oN/FnC+59rDvhufem1J7cDCkNmbZs7/y/mww7qFD74F379iOfLH'
        b'UyuOjJZu6P/j3eFbL6orv/6q6rhwQlxYy8g1P4R8cbXXjjvNQ8+MTzgalblo1J8X5acuWFf/bvFD9vP+qtVLIxRSHvlr+8HrHRFVa2Z0zOPAdRPJvMjEOXC7uyKjieLn'
        b'VmDNLEKxcD0ao60OOrQs60KJQlhtwa4ueNI/Ax6y8XMwztFECmMDHkmed4/RChevBueJ3pMDL4BKsF2PdJ8OveeKkFB1eGBfMuywop/byAuovqM5VHzLWAKVzhMxMl5C'
        b'EFRBVN4gATdEVB+4joUXhHl8tJk9zMehv1Fp8DBR30DDNAuJzd0Ob5rC44jq9jRo48bS4MywSKK5IfZ9ADZ3xBzuCHBIH5YdFARO8JGQuxNK3EQUvA4PdYgoeCWDr/8y'
        b'qAyGtUnwGNhKU3QM0qJBCzz2a8rR7zOBhC624elG7W5TUUi/szj1OwlxnwjRVYKsTl9G6I1sT8aH8adX9/9V7uHQ+Ij61i50vOvgEU9sKSMNcAW+L3axDCu6LHfXAAc0'
        b'9KAB/jp0iLcSp6sky/EiKwsZ4lnLrZoC3ulO9ExSVbsXXjmjMZtzdYgLZvHt8vhNnd5Ct3s4CkEFkEYYMWLjRkiIysCgDmWkQ2gr9p2DHfAc2NEzo4M71DhKOhbcFIJd'
        b'Bq9uFqnY8WvGFpXTItUhK9PhmMLqjgApOoyWrfB4pN2ZqrGgjjOiTlPncm6lY9RxTbRj755LSyY6MonZ83AoUVyVGClRAqREcUSJEhDFiVuD6uq47ymaBCtR3fVkgZqs'
        b'OTHDA6scWnJfeM3d+kRGoPUplGLSPLgZSdfQuOQIpN04rEHVHKQSpYX6JGKPXrq480oSOpGiRvT29oBHVxnGVX5LmTNRMQ9PN36Vvfh2I7YR425WtJW3lR/ZZaDTRMtE'
        b'T4uen/pp5obgDSF/lF0K3qD8VHZUfzTnC9/tG970O6p/bthzMmFjhn/4Tu0y/QlNVd4ZjVgfR+e8ZqEu/sPvy7/nIe0GC7s4JIw6eOl0hXOe2uBN2IE5Hpzu4HjwMNzO'
        b'RE0CO4k5OW0JaCWdkAiqycKUgXAH5atjwSnZWlK2EvGOJlgrQaqOY5WMGBxhVsHtfXiuCa8hHuTQlsaATZ3ZtDWP53mnYONaB0McvZI3Z/X+BLYUsM3Gc0NwAjZShB0W'
        b'wRNOveW3EYd7JKke4VwWNg4JN/J3cCNqrSTET8rROK7FD3Eh7m+r+3ZD1AhXXp5Che1sboG5Xay3FhCSbueKUdp2oUVjytNZ3DjRY7QsxMLW4HscdW0qw5d1Lk5Uii4H'
        b'Oisv/T7sgRf9GrQKRq12cCPTSnxZhXvCkzCLQp0lv0hLqjGVOLvqVwSCabULNBu67KMdhhvmLyE08ZgsmgFudXAWcce6qxIWo8l4uRAcA82jicXxYJFjvd1Ei7RcWUR1'
        b'83y7fFCTqa7rj/Qi1/og+onWB3VjA514jYsNBKmJ3SMYN82MEPiC53IrODQAXkLaw2XYZlkBL3quAHXexVLYRlFPwaMC2Dotn7CFDLBzKspRnaSGdeHqdGw9b/VE5I/u'
        b'qlNUzmWi4DSsUkaAtjmpKiEFLoBrEngL2Oc+dl0rSybaf1sYXTcHAfVrjM8EnlkYDo4n4cGC14aS4UNJ57Kwdky2lRgWx+CtbLykBzXxKiJM1Ey4LRy0hNJUMNjEmRaJ'
        b'DP3snzJmPLHy2XRdn5o7XmVR0mcj5q+KEuQcPePjUe09Z+C+j+6F3N/6ad7L/h8slg6ZWPPJ5qf8a9/cHjD2D6/uqqo7fS2qcO/UAmvgs7JZzy9/+Pxe39n7LysEhCn0'
        b'Xx6CrCFYo4R2eAYNHzjFjATbhhPnGKwCW+DVOZRDhSIMA5aBW7zeuQ5UDCc+ClijwgnYPhTlDdaxS8FZeJHonaBtEiiHN+AxlKwGa1EIMcfRoG0BOMTrTjsRJ3KtFIiL'
        b'I9E6uQMfu1DDU1NcrEOEiFlDF5YjnckR15aYrNrgflwdhthGVoEhV2c067L0pqLCLL3B3UhyK8pZL2EXj45+RvyyzEWw5ejybGde4nO9B0MIz7hFw+a5iSkqUI01Wh6h'
        b'ka5+i00hzgRQl8ILtm1dgqEdHYRkBj8MWrDfpxDsEZAVb9OQEXQmHPftyDEMJfABJ+F+GlyIBqd4t+8eGbwINixAJNS2cgW8sFwqLl4uXc5R/uPZPA1HFu3p+2ab4QXY'
        b'5uG1wksiE8NzKzGJLs8C5wXUEF+uNB9c4IM+d88CV/PgiUQk/PjBFINWBmzAOGsdjxOsHwG2IQC2IKKuTgpLUILKAejj1pXKUCzPk5yrGNLEjvW8NAUOg/Oe0yaNIJ4W'
        b'ZETvyXfL7cjapHlk7u0FElg5AZzk9a9jsEoNaouXg4aV8BK8jDiNBSnvl2ErvGydBbej1qRxCGu3gO2kbxQacJJAu4MFlYnYLYCEc5KI8oab2DnjxltxvDk8gXS6Xd0K'
        b'XQnbpBIbOCukhsRzoEYDdhD1nKxbXDgS3gDnQQvYh1BzPDU+Fe4mnACphwfEcEuKKh5uB2fj4uEVo4iSPsXA/YPgViuePBqN7J1GTxVeppZIfDtF8LIb39uI/YSYwS2G'
        b'60TgxtLeVoyeT00ypyFNA1U/hBoCTiwmIuDkQA8KfYy6HZ+tHCuazIdILp8oIkuubw9ZXfCCtBCp6OT18WW8uPBZW5h0UjeYT7vAh1+e3WSxKVNGL6GsI9DLoMxsrH2E'
        b'J+IIPOJ2cmPLK2B5B4RFoExc+jQ8abDRtxjzZEQfETMPJKeOV8PJfraiSfX7Yj7qXTV9BitqOthML2cbfQTv9d6+3u/Feu5VY/mmc3P7rXsvIqBsc3gxtfrZ6FXLhs+7'
        b'kPn3jXnv5+eNDP2wz6IRgoYKWhV4vH6nZ6TX9Pez+3z30xuKs/GBO6Om7TSIJkZ7LakSKDc/Hb/57cSlf/jX0afe9D54LepKQgrzztdfrzr71/NvPbfn3H+u/aEiRbHw'
        b'6ZYPVtXPHXu95c7MBMunqqyWacGCj0a2S1Z5rPS4PIWdHZm392L/2fS8mOx/2c4v/Nfd9x5cOP+3Ty17n3759Kg3vZkMK8vVzFf9d+IXHq98cOBewLuqokO2ATlf3lt6'
        b'6OfG4T+cmhjYkL/j+0kvH+n1U2bs0R2Jr91+M9YwvW7Up3/7YOYb79M/KCdPz/vp5vptzzwU/zHrs8ovxw6b/fTrf/v7T8d2Td79rGz0xNx5P7HG4dbx31kV3kSF9OwH'
        b'jiXirQuQOVozLgr7oDzhOZYBp8ERC1mefgAZpM3QHoAYDU0xK+gpKbCGKIZwRyGodXFyTTjm5RcZoneCm8AOLycmhUXEKbOQ9YpSeBYw8HDMU0QMaGFdUlFvsjYbYyFe'
        b'fVfLlPbty/P442p4KjwFgYM/LhyaKEIQPcPAy6YFJLM0HV7pB4+7rwdjSsCuXNIcUAFvLAuHVfHKeCJHwHV4VUB5T2D1U/g4VnjIC7YlYrMA0YRCpUa6DrxsCEjiJoPd'
        b'+XyzrvfWdcSo5kWDekaVlE/CPRGjbZ1NtCRYK6I4FbioocHpQHCdV5QbguD28ITkJJriBg2G52iwLxV1IvGHXIab5jkKxawYlYD1iubEAHCJi5ODc0R6MVK4nhedWGxW'
        b'hmLJORd1NoZ7wVPenWeOEKM5RVwup+CNx+quot/qEejTo5AjonERhpTmhSM3HkfuSImAlDA+jETiw/gyEhrdMT6sDx3IOGetpWTZo4Tu91BKInAYPubnP1JPH4YTSR+Q'
        b'yJ2HnED6i6nCKZtbGDeh+SRNcAssw4Vc6yxGA+/2IEZH4oGrHAyvJYK98FpXWdpZkAqoJRYxEki7Qa2CJdHu4Bq4ildBJwbNIP4iYhwtXsIvAb6aMBRl275KDU4n8Zse'
        b'eIKLDDwyLYasSV6aBZvDEQJOBK1hQjTeTUhNumXIZbsogf5ORXAJunRb1U+51vXTnVb2M/Y+en/XLIbgiWYx8hXsR0PQEEvkbv/m6PIMZovOZJZb8nVdd6eJkHRKG2+R'
        b'G8xyk2651WDSaeWWIjl2GKOM6C3ehASvTpQX4Qi+HJ2+yKSTa4wlcrM1h/e8dCoqV2PEEXqGwuIik0WnjZDPNyATyGqRk9BAg1buwE0ClbNs9MFSgkDoVJJJZ7aYDNhf'
        b'3QXaWBL+IMc2Yawc78CD73CkIC7SUTxqYQ9ZlulKcDQfn8vx0CWjVr4C9RmCqccCrGb0kc/uSj9javy0NPJFbtCa5aFzdYYCoy6/UGdSxU83KzqX4+htZyCjRo7baMzD'
        b'UYwaOY7xxOA4y4qQq4tQxxUXo7pwUGC3kgx6kovvUDRWORoMEBorNDbmXJOh2NKtId0cNTKqq73iqbbifSnADURQJ9IinTONc+bHIT00LS5BMGfcONCikMCrJePAtskh'
        b'4/pQsBEeXyKRBk0Fx7rRgY+zgjmd6YByUALtogTG7q33+Y0zeN2WtGFO0n1XCpUapSNcpnvcVvdADB5EyjWd+KQGYY/Tid3XVQkca3Ex1zaA6ac4M54dj30/8atslT5e'
        b'I9V/nv1FdqH+a+rcFG3stJG5wWlB0zbliwbH3dgyuuFq+ej+cSujrFFl03cHLQ7MubvszoOlgUOCbq/etTsoMajWEhR0e9j6uwFRSu58QaDkr7EZAVER2mzt59nCXT6v'
        b'3L7PUBUh39L99/5c6VikDSrMA8NVocRPBa/BarCbUfnBdUQypoAKsDEc1mMVm7Omgos0rA5M+e3TW4KslSZNcZdZLSSFgjk6EMkP7J32Qwzel8SJrlaYHLzLLe7JgeVu'
        b'b3CJjgXffLzhE3uEWmg+A5E3dnQJQJCZ+7nkDbXO/7MeJA42bIxh48LB4XwnTfSwXLVDCs3wVUQmKPHOB8e9DekrHx0AFMsTBvW7Vix3I4CeoxREaus0Cu9ZBHeFjYwa'
        b'NWJM9OiR4DJotViWZZlWLLeaiXV0AZ5Dpk0bvAjPe4ulEpmHlydoAFVgI4PsM3jZA54OLSBWQcuyBOrbfuE05ZMd9iObyJsKDeY46gf/EJrKzk4wRg9xIPiS6+s4onto'
        b'jGf7PN/cqyzKh7t9/fU9cynxBv3nlGfEyF6hbzwMG6Ybss/37deGxY7YO3pui/LcJ5kpy79L1Ww+/ELUT+ri0ckfvbOy70s/HfASviXY92zvLfMnjQke7/3sT/TJk36D'
        b'wpIQLmMVUwNvwZ0OBVM7wLnop3EA+Th7qNDpffAGmx0OiBi4/dcmaB63nk+cZSqyZOVgi9s5n+HE7VAO4bMfwWgcFb1a+URY7SjOOfniCqT9NS8Ew6fowOkadBnaFad9'
        b'7/eA0zjutxCeAOfCnxSlYU0kqE4ZMYaleoevALU+EaBmKBn9Wan8urso/Q7Pw4GzKLJJSwxsBfvB1lFwC0LJCCoCGSVNJLVwPG+CRo2JCX6GHssj0One/MZ0USuCVy/I'
        b'MvIIRL6syhUTMzZqmG/hueHp/MtnVyTiZdbiqHSu147Fa/iXr/XtRclRxVFj6kqm6wdSvEp3BNb0gvaYNFgHt6aPjoI1HCWcQ4NTY0NJpp0BfalRuKSI3LlHzaV8Sca0'
        b'NroMCYhvFwbn3ZtQkk8Ux5LA2WkAFwLrBBQ8mc1m0xORbc5LzEu+axzuO2IKI2MFVikTsG8SHAE7sPFCIjRgQzgxBKrDJQp4fQSZiKYXCik0WjFXZlHS+xlvDPyJImtv'
        b'5QOHi+UlASPo7KREU65qbHHqa2OemzedtuKlXKvgaXA1VADPIzGTTCVrwV4Cd/iqWMqCGxOfnRowegLfmINxkyikWodOHpe0IoN7K5y8/GLMJMpGUYFRBmbE6zZ/PuW6'
        b'2So6m6F8bhv65d+LiFlLXp4a8C59gaXibg8Ptd4b99eZ5KU8ZBa9laEm306PWX1v6qsryMv1Ij86CuHebVnKyntxzXzKhnwL9S36neyZqs3opRtEXq5VptPHGSqudcZ8'
        b'o0Rv5Wu/3G8THcpSUbfNsfqdXjcG8mO6NoO6gpBl8uIXlmfIB/PhNNkTQ+gkhoq5vabX0p2yEfPJy5g1A6npuJnGgzk7hX8cTF5GDUmim3CLZqjNgSP9fMnLHVp/Wole'
        b'tkbIYv7cT8rX/hX3B7qJpYpbAwYU/2ulB//y+qi7VBVNyVv9huVHler5l9qnbdQPqKKop/8+6uPpDgYY5vln6gpNhbbaPlxVlJHJv2znpFQgTjmvbvaoAbH8y6rhy6ky'
        b'NGzF0VOW+63YmmPodTaDNe9Gb07J/paeGl//9mSfV069uiLSuOFu3R7dvR0l7Kwlkwf6iIzNwhfnJF7Y5HP8S+3t0QGjUlrHFU//XvT+nb5XvqXObayoSHjthSpJnk6v'
        b'bJ+Q+d+XxoiKWo69/68Fk/4e8LPps6amkU9P+nRQy9Gsb0ZJTxX/8i1MU8ZOVOXQ898yDLrht0SSOaVv4ZuiqWPUBdl/GSzadm7Tev+5g6NLfvlqa0ZS9FlD8r6EL3uD'
        b'Ap/P5t5Z9e/4feUTWzL7ZVgSvhy6eELGL8eWnd1UFHq3Zuu32Qd/CH5rxcefbmiPGLHokO+lAx+tf/9Ak9/DpdOutKrXngmb2nZ034nDWUWyz2Z76Q/f+ThuWNuSp/90'
        b'HF7e6S0LmLV9wdf/BP/5YoPss5ale2cMfi8+5UrFy/tkEUsXTakcfebgc8J3i/uPLe79/JXKP10pvz7ixafOFmeN+XHytVWfew24eSL3v9sO/CFAsmvsNylxs143rNV+'
        b'XvjvXwLSYuesvL/8BW6g57WAC5+t9Pss5osfFDctgxra81787tPLKycu+2fQ5fOKQ2t3jfsEMheOVCs02woW//vcWwsTVn/3wDvuo5q3zfsUYt5FssEL2X9OPwPYB/fj'
        b'9bCqKHDCgjkeuMAMD4dVkRRsw7tPNdOppcv4fNeWQLwvX214gipRFaYWUFIhA28+BU8RF4Uelqfw4glcm+3yj4NjEt6Bsc0LtCKukRIPTnE4yumssIAJ0YFTxHkyEpmz'
        b'leERigSy5d8YcD0Z7+RXxhYNhJd478rJRZPz4FmXc8blmoFNa/kAh43D4a0uIU29YOMMeIxFVi7c+xunBBU+vz2w4YmVSbFTbBKZm+8mc6X+HO3P+MgYiXPprcyxsh5H'
        b'qAei/750PyQC+zEc2Q9Fglcc0b6sP5LTEpr5hWHEv3AsRyKssOeD+UXKSlBejnhAuIergx8tw3lVVEAWFLSLHMZlu4BYjG7C+3++Ngupu3X4nqxcqHfJ/Fp08e0q88O+'
        b'7kHmT8DjXTseiZ8nkPmwDO4JR7gK7ACpfzfgXniVd4dvgVdyFgJ+A0WXG7jDYxIJLgjgqafgbhIcOw2cBHWuybugUWoS5+oDK9kBT8FjhCN+78M7n6OG1Xonjx7Ks8mx'
        b'nk6F4NMFL5sL+JcvZThVh4FPLUGs13BP+SxlPoS+TLxTM3pjsmz9ZOnMhcINGmpt9HOeq+iGj+d47RH+58M5i2OGffPnqUVL715ZFf/jv/7V+4M/efoIbU2vxGigYuFr'
        b'Vz/cHL7/260BN/6SPj9t6qdfMO9P/lITrjZsVd7+w7Ox1+4t+leIenf2wVvlP2iGT/7i3qKbjR+sHrGrdvj1dWXLVg0+8d7AZ/91LCvs3rAHDaf/ICtIU4x+/dYl467X'
        b'jBblnQG/+H3m/d1fIi2W+woRv01ZHTi5FDSDbW7bz3baexap4OsJ5cONoAzxDafvEtgHcyoanLbFkHIGgZvgnLuGhmMjk2gqGOldJ8B+rghZ5vvIJB2sXWHsSAiuRoWr'
        b'EZfwDWPBcXhMTTjUuNScxL44TccwysAZdrr/QN4DeyUS7kf1bQO1kSq1CtYkKYSUdz82C6k3B8hecEUjQT2oTXHoPa6dqvoqUEs3ceDQUNDktB39/9cZxBOzDycNE/ah'
        b'dGMfXC8xzTDDaOlMEmDJL01k8JIdvBGMDLOMH02NrtLwfl2K3v/XgDe4KBzX/FNnz+iYnjaQwwqvL7wJyjro+zrSdLzHsHpkyh3rccYa/zNL6Y6IIy2dyWqZTE7LZgq0'
        b'XKYQ/YnQnziPyvRAv5Kt7FZOK6jj9/nC4QKcVqgVkZUwnjqpVqz1qKC0Eq1nHZPphZ6l5NmLPMvQs4w8e5Nnb/TsQ557kWcfVCJxk6IyfbW9K8SZvVy10a7a/LR9SG2+'
        b'6JsY/9f61+E9v/AOeAHaQPKtdw/fgrTB5Juf47mvth+qoY/jqb92AHry13JkWdnAdlkSz92TNUZNns70kairmxW7AjunkZPIj06JHpfDYMY+P+J41ZYYNYUG7H4tkWu0'
        b'WuwYNOkKi1bo3PyMnQtHmVAi7Op3+DF5J6LLP0lyRMhTC3Qas05uLLJg36vGQhJbzXir8k4uRTNOItcZscNRK88pkTuWfEY4vMSaXIthhcaCCy4uMhKnsQ7XaCwo6exp'
        b'TDfzzmdUlcbk5i8lXuWVmhLydoXOZNAb0FvcSIsONRqVqdPk5j/CFezoBUetEaQzLSaN0azXYc+1VmPRYCALDIUGC9+hqJmdG2jUF5kKyYZ78pX5htz8rq5vq9GACkeQ'
        b'GLQ6o8WgL3H0FBL6nQp60D/fYik2x0ZGaooNEUuLiowGc4RWF+nY6vvBMOdnPRrMHE3usu5pInLzDGq8U0AxwpiVRSbto31EWGgj3Of4RWLOVWmlDHGTPpGX6EFld0+0'
        b'0WAxaAoMq3VoXLshpdFs0Rhzu84V4H8Ob7gTat4hjh4MeUbUh1NS412funu/n2CvSaHaitnykCy/Ry18AZthm9tqsrFeZMNEOTwAnulQSOD12XgnZmVEBGzAm9aOATuE'
        b'T8OtcKeC330tfQWoSUTiMEWF117Uwb0eKTTlC/aycB1YB9oMoY2fMGa8SNp/20i85iw0B1+Vn36ZHedYNBFhm+QfqknQMOeDAqJWRkVqF90+19i85Wq5ovZi+dXy6FpV'
        b'5dUdLeVD9z9VOYisjnh6V6/S6U3IkMDSEu6HR2mnSI7xdJfeRHLvhHuI3I3JG+YulCeAqw65jGC+wIcwH4fX4XFP1GoFViNyBxBFog+wc2KkPtziI2zKh6aHw/q4URzF'
        b'wuul0E4bwS14i5+5XaeGmxxdgUyaWrABb3MF1sGbBuIGDgBN8BSsTRwJ16tEZBviRHCpD1FPdOBiKil2xGiWwkvgRKtpuDsPtvHb8LTOgc+QJlYlJwl9wEEKKYU0vAqr'
        b'Ch8bCueu8GcZEKZmZXWJ8CEqvwfZ1hDJZn96dUBnFI5w5uN1cz6U2bSNoh671qGF4ZN1xCzvwJUyTv/1Oud/v196iBZ8FBiPXpyF1VobtZRyLmbG4cbOmawWmgej80It'
        b'kxld6hnHjqFCqlulznVcD4IeOUWGqmG1RblPBFYFD5Y4y2HZmPY8AqZNCB7TXnTzwM9tmsw52xbxRJXlOyvDXNegNT+ysq2uypS4Mqdm18OsXG6BAXFzlRkxdcVvAsIz'
        b'S7eq2GAiAuORcOxwwTEYw9GRA0ukrh3fuXonlychw4TLO/YutQvcuPzv3Ey60zYw7vyV7C0Ot4PtabCOw7u1By6mQEMMOEkci8PmceAkArIU7AZ70HXbcKJUhoC6GFgb'
        b'T/T6kfAWrOQoMahlEuCmPoZ5H/1DYF6IEk04eap/7Ys4MJFbua/4MB18qFJ8+O0Pb3z40Yi96uiSb/Iv5L54+KOPXpVVvhX1woHDb547ti53d9j+0ceH/gMe/65h26Uf'
        b'Yt9o+aeq5ubROwveevmfU3bsDf27yGdkkDxkgELCn9pR67WwJ5NnMNhP+OY2cJ0wHy94mHe64uMNBOAATYnhdQZUg7bhxNyZBZBt5JgsQOZsi2O6IARe4+fFGuH+Ybxp'
        b'JqA4NajOpUFrlIBwPQ94SuMeyQhrxtKgbRS8yXt6Lo1GVTu4XlSh0MH0+sAtpOCMNQsTYX0kPpmCGwP29KLBDWTvXeIZ5nZwAJ4JV8XhOJhTWa7trW+Ayzyn3gDLQYtz'
        b'S0IveEHA70iohZf53d4ugLNTYW0cOD1xUpyTofuCkyzcYEnrtLfZE3JenTHXVFJsIZyXeBY6OO8ACdmohXejkIm7bozPkdt9KcmT7WDo2Fa2g/8eQZfdPfDfHnbXfCQY'
        b'/x9rV9PyNcY8HR9/4dSHnKygi66FVKYnVbOMupVPql3h5nZfzMqpHad/gKvBcW76D1F+Wq1E/+mdavglehhtxvs0vFNW3+eVQf4gym/6H3b9lLVb4n/H99p2iTo9eS53'
        b'lHnrRIiQLhh03wCvfnZ/uP8LYR8Mi9y6LXX21WmNeeN/uP63P+8shQHP9vd4v9/MCR9X/evfQ74be9nP9K5shyT6P9XjzhyQZ+WAio+szA+H/Re9aVd4EArxA8dy8Ma4'
        b'16Hdoa/QRnhjHI/hh8DuBFCbEg224VWz4IQylKZksI7VrYX7+XDkI2DfLEIDbhRwZQAhgpmOeLAT8Bg8B2oj48A6pFfSFBdJg/NgfxTZc3YA3A7L8V5CcGNiCqiLjBu0'
        b'2qVERsEm4bjB8BQJsYsGB59GahHWiSaBLVgtgjeTyVxj1FJ/Z9dektIUr06FIXUNay9xvec5VKZZs1iKKExwWzoP2IUFpWCXxqUyOVjH7MW/nXa9cwn+ZTmRpQflSRIp'
        b'IzFg/R4GM6sHdKGaLtn5knc+kmRNu1y0egxdjvRAq/d6oNXH1Kpg24X5RWaLQdvugajBYsT6QLuQ1wu6rWzqTM+cc0GDi545ElD1+BVNeQr2o6l0F0sf/5ui1WJLCdOg'
        b'm4LBW5ku8f5IQuYbwpNxHLqPn+5kBzka47LuxOyif0e7+Zyp/CPKHJpoNSIbVRU/vYcoI7eIJWdObJHjbJ0ilBQ9wWvSWawmozlWnj3XZNVl40AjfvcFrVKePVNTYObf'
        b'aQrQS20J0new2mW0/C5+xKoNz874njPjLaTM85CNteT2G3eY4ffuvH3nXOPV7c3lzeXjatt2tR24vL1tQ3Rty4bmhkF711UPqlwnEO/ZFRS0PkgaVKN7KSgoaHKUb1Va'
        b'Wc7eICrpda/5ohUKlkx+wB0LARLHKR3sYjmoIhyjL784NBYehpWIGcye2sELZAN4XWMfrAatiUnxoDolGdYkRYD6SFWRL44+VYCNAnC6qPS3U6ZMo9Vm6XIMuWai4BLC'
        b'9O1EmLLJeAJiyMPV/buQR+ecvF0j5MXkcXxpwZcTnSWs+/EHnFuyYldaQrWn0OVcD1T7ck9rM38VrP8zutQjupzVE13OIS4yRJpGHhdxSJ0bgbo5x/7/R6I4W3xaipx3'
        b'a1l4LxixOfQGo6ZArtUV6LrHAT45cY498AZPnAVfNPHEiUhzsfl/RpzbEYvlxbldEeqgTSTub7qJ82nwFhGlgilIo68FzaAxsoM8+8FjFjINdRqpxtXhCbAO1kWCtoGJ'
        b'oK6DTjGVTgL1Il+43++3U2kv3u/6GEJNcRBqF40uoltmvuTTXQjSdMZFf63ocqcH+rvRA/09trbHHBRD2ym3g2KebNNuRHwPcnqgPIKGhESM1sIcRG0I89x81R0e4Fyr'
        b'yYSEREGJm53+e5FywooBDNmz6+a1cnwWTeuFkMZmgo7Rj0XHoS93Qsd7n3meiZUhdMT2VSkNz7hExbK5LmQcBbcRzbQfeAZeUeKzAd2QcWyUBe8cWACvwjNIbZwaHInM'
        b'UneBoVaFCREmXhXJFwq7HA/UI+blFlmNFrfRNPeAeeL5j8C8bpmdQZLFjxQLvF+DYOE5dHmjOxbKTj8BFnar+f8ACysQFhofiYUdMdRPjIHy0DCszhmM8hVjIkaF9cCm'
        b'nwwjR/z7KE0w0n8jRTDy1/BxxK1HY6SKus96vnS92qG9LPaGTQgjBfBKF3MnGRzmV68cEFk70BFsWYBPpFtFuCM4DQ+n44g0ZYQTHXPgLhdGxgC7EFk9x2DTEyClD+7Z'
        b'x+FklgMnB3bBjK55+XLPPxoNL6LLvR7Q8EhPW4U9pjJFQNfF2aKsLG1RblZWO5dlNRW0e+FrlnOapt3TtX7GoDXtxpkO4EszvuAoA+ILbhcXm4qKdSZLSbvY6VAlcRnt'
        b'IofTsl3i5jjE7gtiFxE1i/B6Qmqkobx75HfsBeLmhdyELksZx0aGYopjOE+O7vgvZvxoxktIM7jT2J5/fTmxpx8tlfrQUpkPLZP5ismCc2SLXsRxw9XIID/Be9zgxWRk'
        b'GiPrlqFCwTrBWmSsbug2r4Npf7ITRzpPK/M7qLb3dqxKcYwf2Tr5gXzGKryrI/ad5uIlJyYjVubclDc1sj87j6fpkqsvuvhmn0GXDxnXInrUKzRZfQ4vwau+HavowTN4'
        b'ByqnP9EZiJEgEYEGcHyIdQbuhfVwLzzSOXK6S9y0Emz91dDpmand+KGnk5PgUXMsPaA6n/7ZsfPs7z3kB1fU3QksVStYEk5TvVBC4dkzH6HYFji2NpqEo94ZJqLk+ePw'
        b'CErvZ5zzN1EFON7oD7lPCb4IvJr3cEZfxdVlqVknBh5fdi1jfehu9XMxoxbUKfelnB5/JHZx/7fCDub8rHyQvNbr075epTfSW0Mrpo1O+ExdMuWjAcJgSb8/Z0zN/GTi'
        b'9WF750yaW91/a9iNgQunRsbPWfWud1vRN6Pa2U1hc4pH9Dsy+tPpCWv+Fv9UuFdAfoZJUBby6fQVki/NK4pDA+7POOEZ5HVt7UNkYaQGcTL+IMoyuB20wtoZYLPDS+3w'
        b'UC+HJ0hbn17ERIWwJHpUaQ1yxPnGCH0n5LN4BLL75cZGOQKOhwbMuUNlUJQ8e9G7S2h+2eukzDGwNlkVoU6CV8JT0p0br8GGRBHcBFpKYPUMsE0wlAIVwzxgM6iBZ0hZ'
        b'f7NwcfcYJHQnZysH5gbyFfwlVhQ3nwnEFUhvJpXy26neuRyYS0jn+ddoz3TDuOfH02a8QGHQ89FD69pkUC6d/vrOilSr9/HEhy23Pjy98O1e29+887PnD28F6r774r0F'
        b'K6f2uRb61emrn5z58yDjGwf+GCDOqzr02dqm2UMXb+vbZ/PQj75p+MyuLfzn6M8SfIcMmXvszJWZ82uN7+U/KF8R+vfWJbs/ODr7vv/UDe+pDrWVaPT7CofK8ja+GPns'
        b'Bx7bm4ZV6O8rOH5/tAvwJJO4Fhx1HRvMn4qzPoSsmVwDm2Z3hDUF9+sc2DQIHOBDEusK4N5wFT6iFPeggPKE1wzgMgMvx3JE7we7ZvQKhzWJ4FQYduHhdXbj4BHY2D3+'
        b'/fdudeu+j4DJrOnk68b7MXQINm65hHi5sZ/bh5ETdorvTbedxeDzunH0gZuC9XvBaqFNwMXBcAVfdReE8s09BP6QPSTwqT03wsPUYCPRYqfCSl5n6Av2ceAkKOvbjQl1'
        b'3g+oGxNy7Qf0uxlQz7NQEicDGmn0pEInz0Ef5AX3Jo5JIwzoxaUkHl5OzUyyvB9YHNjMM6CMtEczoAs+GSP6LogduHBlgvVa7NH06TN+XPDPvg+DXxkbvLokXDNbLFrm'
        b'93r/7xn4lHSUX8yV6MpRz5euSI4Zuja09/jQ9FWTLnFZvkeKzw7MyfqT4YIoJP1wti4mYdkrHt88lgHF2K7xRO1jYCkuqoHD/OW+ZR7/MmScLzUk+wXU7dkTfhbNpUxY'
        b'C+aDyC2IdFb14RBjSPpkhhf/snC2kJJmDxcgxqBUsasoB2cDp1hYCxpBc2fOBg7FG0qfvysw4/2oNqibVS+3ecEoKXf72JJzH4/Z92H6ucr52Rr5vmXXfRnbpaqxXoL0'
        b'168MunPr2J88pnz97yMv3RNNGB0TcOPqpKfOpl77edCG7Rt2pk3L075VmP7P1pSfVoxX7f40cH6Gv+6pbyK/E51993Pz3Rs/02FH+ic2fa+giUkUGwh2JoLaDOcB4eLF'
        b'jM4A2zqplL97QyFCl1pdB10O6USXiDI5MT4SgFAkpk0pH6pLm551FXTnd0AAXQSIy/mZcZyi0UGA1Lp+D3sgQUylK+ARsIOnwPjkCFjb10GA2Rxoto3utlgR/5HdTOMQ'
        b'hlQJ+B3bbXQThcmumSllyD2r5dA9a6Hx9+nU4vWLmFKuFO/qLqiiLAw5nGb0apFN0MRqBc10qWA+ZVyG91IvGcUf3EO+4CN9BAso45KViGRNm0lunDPdxpqmohSCZv7w'
        b'HiE5D8EL1SEsFVXRNhHe810rqkPpbcIJ+Eiep0heAcprRnmz8ekDCG4Bgk9A4MN5xd3yilFerXEgySskx+48eb6yKiGfFj1TNnzCgR+/vz05CqfZRmk9ghBfsfFz9xI1'
        b'4sc6XfFME172NveBwGrRq2JMWNFBmHkXjyz+QE5RMWHZrhCZ8jDGeeiM1kKdCZ9+gHcSbhfiHcy1unZputGAb4iWyuedyiNWxw6aHcWSveXJgqx5+IL3bW2nl/7GtfDt'
        b'UnzqiHkEv0bYm3Xs0yRm+XX7MscJHOj3IUdO5MArzfzwuRuM+z1/xx+ZgINlSPDTGHAsixxIrhoThncuWKUnqwLkAzikw+6Z1i1CwrWdOBbNNsTGtXQahQ9NIiPAlPNn'
        b'TbBq0pemWGc78B7D5kdYlF6kdVmWoqyCImNeFOtQ03EAvow/ItEL7gC7eShF/shshdX8HpBY4aKGgUpBSeHqbsfeuOLJRhFItfQy2iTENoeWteHDimgt10ThY3AQ3AJ/'
        b'qpm20QEUFm74DdkfWehoBebTD5ihq8gytC8YvjmC1XpDQYGCaaeN7XT+o5qGW4RbRpo4lnVuE8jyp52IHcdV7BtB9kvH7SENW09amEIaLKSGDRCUBMJbj1mvTPe4XvnJ'
        b'nCk9nnbrKt5t7WjHQryU1GLqQ7y8bvDHqg/7R/Av45ln+RVSc98ZW5eyln9ZNMcZpv/x+FOhsyjDqy/e5s/G2LDQA+/M19rYvOVieUv5xV1/qBw079L25g3N5c0b2+Iu'
        b'lFvpXK9pkk+mHlW/M7U+eIMgyTOoJn3Qwf7K/q+MVp6TvrpRkeQ72fcgE/qceMTQygXS0Etl4yp1g3Kj2DxPKqI4SO/dD6mqWDj1hU2gjl/dDMsCkBK5m1GBej3vem4G'
        b'TeByeIJqPLzGn0fnOIwO7gO7eR3VPrAv3uwkCFxExiFsUNIoxUkGnpkCm4i7sADaYQs4mUD29KqmwTZvSriGCUFWyK3fvki6V2GRdtxY/oSHLK0hz9BT1AW1VjxTSuLd'
        b'+AMl/GnT265iqp6kwmpnhSTjZLYH0ebfg8+ZbKwEW8eAjaixdSmgbRTZHxmft4MPcK1OmpdMOigGHBOuAXtXPZqDYOWY5xtYxjXThHMw6naBxpxrMCDt9wXKKYGHdO4h'
        b'Ub5uVYFBX5LAOuLeZCy/t9X+eDRqtUhJOko2gEPQgJMcsigqGXhNOvfRoGDWjY80IUJQgg8CwgCVOsAjzIBRm/5IEaV8hhOsX9uQzMNqdACZgoEkR7KwOEjGSo51PBSS'
        b'EQ7rSHACBhPUGgmkeBe4fbAV7vtNveYCzvTOo3rMI2fMKP4Iq3moJNM99I6EcgXDc9mJI0bGEwsObANlWHPzHsSO9x3wv9FbpvtP1FcIOF66LsTA/QkDx2+lj3qmHoOH'
        b'dUp4GOwkS1HgGTYaXp3cLXrOdSAb3spPSyMGj5UmytTHgtk/W84glYIqZflDmmxMADnyySy0McXBNhofmUTcUQJ1+5Co6BEjR40eMzZm3JSp06bPmDkrLj4hMSlZnZI6'
        b'e07a3PR58zMWZPLCgHQzURtopCEYViDSVXDtQn4GpF2Qm68xmduFeD+OkWN4ZaDrmes5I8fwA5PDOs5SISvP+DO1fpGyZE83Qf/liSPG8OFei8EtMkgBbOx4cO7RoyR1'
        b'IIqWdghlNCYfOCtHXOmjHtFk5Bh+JApYx7b/EpYECSWATeAWhoEMxXHQwg/FYTYqBTY+ej9JckA17TqgGgH0+/aQpKieTjLh+ABxeGAEaHWuxobb0pM9ZsOLoHUOulyc'
        b'4wXqGaUHFQqvcIVwc5Bhy8czWDNmFpWD736i/Tw7A8kfDZ2LpMxz2cLXLC/3pkLLuInBYgXDB9pVLQO7wlXxqNG1kSKwH+ylPEYySGRUevLCo8IAml1LLpMFoAHY+TWX'
        b'4Bj9qLOmDeaiLIuhUGe2aAqLXeezO/dkcsworjB96spWST3KH08SLe+JeUtre2DeOJaByYSb8W5h9fj07QZ4kwCuioiHG1UUNcwkWLt85cxuIXKdPZSsI0TOzT+JRtnz'
        b'f7plBVYXvLuNci81Od7UE5yC6xLxKCvVeEM8jhIGM5KZk4mSIWL8KYQKqz4Pyba9u2AoRXKAir6KkSNA24goKoSCJ+eL1DTYA3fNIJwPbJsO7OjrpRHgIhdCpWeLwA4a'
        b'XEIJDpDYV3BImAG3CGCFhWxY0AdcIxXdSw6ioigq9e7S7Anf5c3kVZw73qFUKkVl+BZlh8yQLKWs+Ah4cAJWDQfnmUGZZNM/zwSS9A0z2cBAvLQgW/kP9QA+//v9yfLG'
        b'jK3qbOlZ+RiEMjz8N8DuOYnx4JQSNoBbQorrR4Nz8Aq/vp4Jn0yVUVT2fnO26e0JfnxBazPIQv6MM+OzfZ81xPAvMxRk5764k4ps5SuFQsqgPb6dNr+FvvyUPHaG+tUE'
        b'dor0l8277n9RfzHAu/ADeKjooylcw5Rnp3qflG975e6UuD6lG94bO/rIEd9nfH74JeevQyVGzYs1zd+1to6Ymn+wtC1KeVpcMamkrvT+itc2cdW9x+8p1H93YOCCN6fX'
        b'9U3fGd7Xo2jVlTEnLtwcceZwILz/x/iJV/Wz3p1e8Z/DZx7c3bfW77vglR9UwNAbRyZ9PnDqX4OXjpqzfUmC56cLI9bkV342d8srfxzk/Zcdw/eefb7kmwtvyXWVo5e+'
        b'c7yktz3y1f03r9xpuwxvjl37odfPbw1Uvzf57f/X3peAR1FlC9fWazqdkIQsEEJYAnRCWEWQXYFIEgg7DKC2SaoDCZ1OqO6wxI6CKN3NKiIiCAgoAgoqAiKI4FSpOE9H'
        b'HZ/j0m9mdMaZcXAdddxQh3fOuVWdDkkcnH/+98/3f498VNetunXXc88959yzTE9zmYne66TuTik1JBHqwQkojNDusrMlu0N9Ul0XCz7M3aju1Om9+9X9zMvp2eyGAu3J'
        b'6fGBjgvz1AeY1PNu7bGJhjoxz2lbHEyduMccVvrdy7UImWCox6+LGXOSDUa/QqZQfELdpx0vJQvuoHpKqOHHaGe0oz/Bk/q/QNCZWA87k8cNmGjYlQMGEg5CpZwWIpWb'
        b'dHtn3IvEbNiPzLwkdAdu004B+DL5bJ5FKEcjSeEb5X2jCt1hSdReVadUetwUQrBZHvrPOLsXFIxjF+faBOtqaAvt5YbaQXuVGN+6YGLf/DI1pKEZ8kZEgScGDB4gcT15'
        b'Sd3SwDdgI9OzrpgxDC34u3HdFGC7DLNI/NdCiQktzsM8xoyMAKOFYf7CyFeagpKSHjTBfwm2X1Mmlwa5MiBPUNjNk1qxftYdFmXR+G6VyEIBQy5RGRiWdmNYVnGPACUz'
        b'gkoqa8XgxgJYIq1EcV3tjH0NQoEZFFGw3aiuRIu0s6Pgwdh2Y/vP5hpzK7x1wIkwvaK2QtEyAkiMmhrq6z2Kci1OvUTcsTkqBTzLAkBXYBH+6kZP1Ob3oLpTAOOsLq2W'
        b'AwuVDzC/KHtax5mFBn6E9x/GwNYR35Y7RT2SFUpCrGTDn8NLFyURPRPSmaV2q7pWfaAUY2JPYfwJ+pScpG6YDKu6q7ZL0o6p69Q7WpGSsaHFOUZSkshdDshdB0nhMEQz'
        b'zPluHGzYpGQRB5tkdIIyEOZZkCXIIQZFDG2NsTybRJxPKqEQnlJoaXwPuWFXlE1kWWMuu9Bn5HVjltV6+xWMIaKw2rdg1Pzuva/vM/8GuBa48L5f/pjrxowm8vo8NpaJ'
        b'rp7niOVD3iRq9nvKlcqFUdMCpa6hPmpCuRH8eOuWwuy8QOszKkItUUs9KoopvqgJRhM+sBqV/hi1noyeJeFrt5F5t6iLgyQR0UUauUkw5K/414DHtDcNXsw8HR/UVquP'
        b'ovsbNTKFHRyRO00LN8xlRjuNx1rQHi0OLffSbACxLqRxSL4zhkMZhZY6Sgped/N7OH9GUJCBvA9ybrThEZSueKU33YNA8rvh/3juelsTMTFQmpgB88Jzi3tS7itjuUew'
        b'3BS0GyWKvDKJclwby1HWMoceV0sqi/L2C0JuLk0NjCXB75e0LALl1V5YKpLH66mFKfEs8Xh/ZC1GHfWKJ4DGpzjij4m6GMAhMl9SyRQCNZnupYtpyF9eJFxX3n1oQZ+S'
        b'QhcxwADhj6r3A1cJY85z3dS9pj6z1bvbN//GENTN5/SAqbh5okeiAIcw2vNMd4k15hrLPCs8M8lmembxWGpsssVIAW1oASyHxt/WeXa5OwZLhHSC7LjNNi8hlk6UnZB2'
        b'6MEUJQqymCQnwzeJLZ51kFPgmTP2RJJT5TR4ktQiV0c5HZ4lk9E3N6+D3CMkAt+BZt22eSlyT0rlyF0hlSrnwTdmaEGu3A3SaRQ6oyOtwV7RhAkwNR5f4Bpg2lqAoiFU'
        b'nGHg3GbhPIXs5WTJuNcD7kb5JgKB8xfh3wV+OLACSD4f1GPhTYvNddzqctNqpYjh/vrySs9zMUwsNGbHNa3fpRnb5ASprchUIpcOYGuIWfgyADgLj4g3UL6gLXu2qK3e'
        b'W17tc8PrXxhNcAiNHeObEMvRqm7BqDuFY4Z0dRZjeepGhAeFqMmNmwMtjDYt6nDZvGqIeJLFxuT4uvHTVtMTq9ZB04MYQI5VyCsJ0DTFzLdd06+NmuxCK+4nJkv2xqad'
        b'dgCeyY/pxKInntCw6LlBURYWCUonGYUNwkiMigurZwnn7y+bgiL+wh7A4ykMPLGwr9I5I6/MYyRpfaKsZRf4/lE+/4LQrz9MGTn4NdEFJ4+/6YLppvymPD/uviwQuR2Y'
        b'SiXgX1oNOyvuxIa51QpO3/WjfH170mo3YBvYnD3k+/5tUZ8+w6zLLnTikwVhhZ1vzGoBiPFflbXw+ynGj12OAYY0dgF2ZiBQ1GxYNgZYikoG9szkbwBaAskIn2zoLGIX'
        b'ovYYwLdznqBkwfd/wsmkcJBAqLYEHCzxX9NIJRNbasECy71epRPfLknVBV6dR9lWNtw0pl7aHPi6TUxDLcL4P2EApLCE5EeYwLoGAHC9QO3jjfZhOPCgIUQ9yEdNPn9t'
        b'eT00tWusqWYW2kCPxRm1eFg7LksPWsmFEj4WddtYjMuO9FZjSnxfWPHtD+4A1hUh1hUh1hUhvis41NAZgVauUKZgDPCWHalGT0sBlw4YY/HSjb9MjW6lO+T8Ir4nKa16'
        b'wspvNSkxERTySmFoaViEnnQ0MIKSjLQJC+bdBL1B+hDXcUDQwUgMGhJbEdb1WEYfSEpH7BieOrLeJbjdQGNVBzy1brexV0zi/rEXSqUnfP2tcchk16mwZL4xo8VybS68'
        b'/Zm6MR7oMn+sf2yuEMvGZranPrOwFdLMivrMSvG5bVVAJyk9eIOAzWHTR0OBnrLjZhvGw2802ZjymKfLy5vyXroHXtoL2cigw3PmLaDl6MSq+gcxVHkdOmeyatraQq1u'
        b'd0VdndfttiOdjlKnxrSWlbHXRL3PbDEbBhdC8eiR5qPY7FwVUr880rc7YJfR456jHK0IBuYCF6MYlwNSrvYFoklIqMueSm85U0BFa/pAHTtINnYG/Exx4WjT4fUlImGz'
        b'4sE4R05JBytyiHQROOyLLVcMy1bUZicIpHJjnZAJbGRhvUQsEs+UGgzpu1Q58Aof2vuxoElRm2dZpbfBX73EE03EXc0NPCfW6v8CG5kLHfT5R3XvTqe0gNnyCSfDjuSF'
        b'LcLoYj/sXX+8fN26iwrwglyKFMMH2DegdFpsGtimFtgAhyLGl7wMl2o6TkBpANAC/VnHaBORAPqBn9+D5+N8Fned0GRqMgdNQWEJB5w+rhRTFsZWEvwudr+Ax9+R+hvA'
        b'GWZE7YvNQTN7DndcjYQ6GlBTEpRnabJCzeagBWqzBK04tEFLBgc5R0BOS5MtaFPmB3n/TOBO5wZt8F4cyfmEoA0pFn95UPCXy9T6Gvi22pA3sLNvXKAXTD2Q2nLZog5Y'
        b'GcBZVntlmO6oJVDnlqsrA6QAQfsD7DABgK2KqA0z4jLyE5XJOCAbT9If2nvslXU+P7MWjPIynpRAoVG+UrFiMUKlzPzaEYn8IdfuxnoF5M7AqUOFDonwXRqdijppfafQ'
        b'GjeTXpCdwhggb9pyA9Y7cZBIYlqILqGoyMUXudIv1S+mrpwyuqIIsZ4l8IztRm6akQZIhNC2T+NCWw6hZ8JESm+8FPA67FEv4uKCXbYgMC5MGLZFFfWBsHJWUZCAG5QE'
        b'7DbcOcVkR7KUJqWZU8xpFqvdKTmlTBM7ZbvPtsCPUVbXT9bWFyweo4VL+paZuKyxUpG22zHTxXQURl6jnizAwFTMxArtqzSK04kfuczcINk8s8MiyIy4al5nb6l2r7Y9'
        b'VirPJdwsaA9rx7V9rc6KEEmQ3lNKDEFUAyETw23M+0Zt+SKPTq4ouW2gKYs+pVdKOq+SLFBTRpjUx/3qPdrquLbY1V2CtjblujZPmPCffyYXxwInU4xFVFgHhhdYSwmY'
        b'V555OZtnYjaMVaLO7JrR1xnkscgOORF+rbJTTroNfaWx7aJD1DG+obZ2ud7atqll2mPQMoZxMLD78nFsJt/MZjLZA1xFkkNIsnGEqYixfVXidWYBNkpcW8SBMvj9kAbO'
        b'jbS7L0ZL0fozs2eXsklo8DDaQJRmPgdWFqymjvE9+mlObhbQ7CpX8+1soDYgVVhTxhvzauYb01tUGMvSPrWmH4USFaJzg0Z8Eurz5DYAihFhiM7c7mslgzXkGzMv6W0s'
        b'U/vVj6aplHlgCc2olkaEIyB8JSVMA4F8OTYMJlpAwaCSReRUc4ObFap6MEqYJpJGjeilPP5HD9gJ8ZQY1A/DgU6SzrXdn8smf6qQOB8Uq6utGbS43V6Pz+2eYQwhUNpp'
        b'l1RJGdoXIWBnAtwCplqg+x+ScH9pj+bCd273bANirG2AKOW4zB4Wtds7wuNzkbZDnc1WtejE3Ui27V2yl+BaUsbh7E2I7Q1o06yUxDYI2gx+ZFoxitYIST89tnJ20Wp2'
        b'iMmi1WYVHSLJATupW0b4XYix1cMBhgFzKwkH5qgnJW2rdAk+5rg4JIguzwwkeJdYI9ZI80weplqGUj7JI9VYgHTTU3TKjwjSOs/K5HKAFBmStJF8zU7r3RpNmVJR46kM'
        b'kLs/faz+CfGRYm8HZxBWQ8tzBd1YNma0ru2niY5wA1ISf0xwtBArc8LLy0ZAVQYCUsbzrclRhAcvllmEHchpowM/hnViRokKXBptAU5nvogYnQM9koAdXd6JKQMT/hGD'
        b'dESxSjBzc9l70/KhurIwv9tMjN8AyGNpZv728Cyv0SeW0o/0m5k6oGQyDeCO2ouBQVjG1GYJfyHwR51XE8HYENAVaptZ4ctBanWSDiMC8PAOIP2QAExHTdgf2h84nZFM'
        b'uHRFlrYg5xidN6rlAm2m0Vo1rJkUw3Kub16WzUSYQ8wUSX2u5gr1oHZ0iramZHI/VChcO0k7oD00eXEcjXKNut/SQ3t8dvvLs1Pc8iSKhA4VgUoRCWqlaGdjAAyUNA4d'
        b'kk6qq1vUUN/iVNOkg05qbMXpm1W4+UwDEH23GE4yMRpeCiyv9yi78NYWk8q1uZmavVRrk2SY4OG50MXG7j/Swn7skzas/KbF1uElC6cM14ukq45YuWSxATXBBqjrathg'
        b'BzrScKsPB5rJXW1Dcd9+2hOoe6tt7FeIeiGL7UC53u1qdQwVE46gVjPs4RwJO5y0vnjG/AXxWA8PitLDyP5xYTPytWGO7k3N8kOBHdSJP5s8CSAJedJoQl0zuBJL/lMD'
        b'pk2H3q+WdGQDewFt8KghThpk6kmvdp+6Vj2rPaI9ph2Hxa0d4bTH+6pnW0GY2YCwG+IgTG4+kjFXmegwyDZPJEUgMyB6PAiywiYg0dGPKFtkK1LHsk22A/VrjjsAss6z'
        b'0HZgJTzojDr0qZ8MBL5SVtTKZ0hs1B/gUB+oGkZT5neIwFYb4qkUIIH5atT3A9aZhPBINAvK+JhAqmtQ0N8AfZXFAeEsIQscFP1D8Y7SUhaUjkw39IUJuISgMB7P1E3w'
        b'ncnIQwz4VYawskaQzcCsSMis8MZSsaB8eCrJU/AyGi9EJDU/k5rxSNTuJkGtG0XIhC2RMnDpzlwod2cSgtUrnqrqZW7UJSRTg6jg81+e8AsL3CLpRjOCIKCE4we7yUru'
        b'rJEINJMsN5m0OVL4TnzslIcmpZmkj18RFi5OFeJBDjUQZH4vjrKAQhAe0qhrCSM4jolA8PDbn0ViEYkEGo6AEJTwgJz4K06W1uN4FxgCkt0SGrAow+kLgC82K7DuzKtg'
        b'tqmEHvDcAoiqCPOwN/pzWn1opLJKYE8WO4KifqACqNE0Aw9JouIEnxyVyjCouGl2ubeh9RlajCpgZ2gowJGFJYwI0WlyWMxzcZbmx9Aj35amJ/mHfMKgSR1cY2HLMa6s'
        b'8y3xKAGSRfjjtSyY+04olESezQLTQcTToagLI9V5dPmLn8LtMYkM7qWARQhXi37P4qipTpE9Cor0/A3eABHRtc1ylh879He2bN9DBjRZeeZ21c7bEa4EcpD+d7uYjdYm'
        b'Qopd+ERKbez8Iz1tddQWkxcWEUzhqgWo6NwkAq1B6jJk4pSOUEYCaHEPm3MpKMr8Eh7X+m4Bn9IzQ/MVyXiUKQLl54E5t7qrvKj64KNRM6SEN+DY3oiX8n9Ae8jw/hfG'
        b'Fs/czqbQKAgrpFarR6+qzf2EYAvV9eMMveAaxJ44gqQWuxupLnEPai/DOyZYX4LrAu9EuOsZAMwUFNJhF7qVJ9UEwGB7eKLsYMXA+hiE4j2f1XiCefCoUTaxO3gCo5rO'
        b'hAfmMna0KADngi28kD7Lt8hXt9SXG9vic7vn+btfMN+U58eTR7MyEIcsjcCP4TJlFvGnnE7KGaIFgrQ5ranoaKLbhwo96IAaCngNBxY9WjAzpWSeyevTEU0JKXxjp5bD'
        b'G/9pKwwVEy5VcfHnegQ5uFfjri2wu2quSWIKO7r5GWIh/ILM6ILmoES4v2NAYoc5NbAvoKh2Lz+dM/YAg0E1K9W8DiZKBV5oPdJhBvCn6NUdCFBLnMDFaghVlSGYtDEx'
        b'KvQobnm2LQGtgfzvGqCII2UXJYGNWU5rRK5XLZbBcrC1yZJWxBpOXahpSfZeFk3STArPhK83GTSJlUuXkjsmd7Xa0p1koyxoZ9Rws+hROzJZW6ceHY7umnIyJPWpDEub'
        b'TsLxHwWRjNEmScR8GjQJ8+BvUCT45lJqBKllnRYhJRSU0zGxd3LUOqmuclFRtddTpiAp3IIeaaEKUMIxcSXjrPz2gCDztAIZ7yjQOzrwS0cRHcAWXE0kqDOT0M6Chmhu'
        b'a0xp6EIqhujNles8uu999GB2wZLn74c6bzhfKzg6+/RjPlpeUUt5hR+P3aNW0ouTq5WoBTXL6xoCUZO7lkLPUOTfqMWNOTxyvD5AVMIcir8NJhRh4XMDrHAhYlRGM/3Z'
        b'+cYOxiC1Le5D7GY3xulOzlCTRDkXmtjZuEZrGNcd4CPE03M430AyUb2aBzzFc415QVhdsrBIVHJuxa/MSp85wGEiFruZlK308vhFkjIoAOOI4w7PrLLEyjPy+uzsdym/'
        b'FE+daORncIutJCSdeb4D4bfKugavTCNeXknu/3NxpN7fvg3/HRzjsgGjA0NKwxQ11S6CQVYUvLdMmUFMa9TkURRAQ0vwoWN6gw+z62/8Xo+nXkeAUQvsPVRUdbvrOSph'
        b'5d9LuusBtO0UyMaTzqXIKoQsB1cI35ptEi980ZgYmwv8sn17EGYGWQNkAY0Ewi5vzIGSAfMhGfNxiTobbp0m6hwDGlO1PzYEJqUW70kOcynP1+DDBiWa9OXPYqcAofmD'
        b'JDQmxRrNcv0jwouRlDFdHqCGbm9PZoxOfTyA5FJNBq3FNybHwSu9bH+Y8uPqQ4DVhbQCE9KSrB2GSbcvJiftknIrtiVgDJDSEGvapeY1bjfgYhQ9ppsMU1Aivs2kgBDX'
        b'SD1bK51f/D+H04kvms0EQzCGw8NUHvGwMXbITtoqDTRXld46oBNx4AwNEMntWVbZhgQVUA+s6S6mmKgfeQRHy3XP8qBgAPFkO7sJjQxN1Wq8hPCy5nJkm7WQ6ZOYyJpz'
        b'Sk67owPKNx0WMt/IGelGX0RTtA1LKLR3QF1p4hJrRHtecatNw6L/ktFpTGSCutgSsKoxsQnqN86T5OQQC2Yjhswha5WZZJg22Dw6MOaWwtHg4Y4NNhLmuQyPeOLZ2gWu'
        b'lKhUNHV8USukGCNH8BAmwOmEBGwZQEAIjIk0pg9+oW1hoUZC22RKA0oMmFlK30DYFItlFxKmLscKB+UuyfNfSISEHucbkoYQjnmrQg+d9eULPFGH3xNw1yt1ckMlsAQO'
        b'/No9e8L0GcVTyqIJ+I4cvQIKS3C79VDYbjfT3nZj7BSDqItZvf/YbGLdfQyQTyedVcRojYlYbdv8ZXsyWd2+8EKHGdCS3NpyH3m5RJcriBU2NwM3c55yKaWJPYv1oT80'
        b'iSS3jSnUkBYvy1o0x8TFiVZ3xc0eLj10EB4UmBCoRlD6h4GtxTvU8Qa2VARWFsiAVUwjnO6bRCDyxQwOdY/pKRAGu81MEYLIUmD3wkBgyqZVwkYnEKbSbktQYJubDGAk'
        b'catEpiE1kPNfu5Rn4tq5nK41RWQ8aoh/QSoNeXkzJky9OvcLHAKmH7hM8VTZib6PCksrdBCJmoFsqG8I0ChGTXJDbb2fWbuiIiEdHEZNS/FYX5cAMnRH40yfCFULL9/O'
        b'WdkGnww26Tp3TiIxHAQWDlLIQtGV/SLQsn+H/SKB5oc1L2qb6PEu8QSqK8sVPFpjlpg4QZWG6Ar/oS1HzKUNcnVBIhqA+OdpzpC4J/1mmA9RX280/nQPDBUQ/CK+CfMB'
        b'EzCXpjQONT3RJwVLd2Zpq2xussmWJjsTQDQlACwkkEZooMkBbIMji2tKDNqUCiNfMBFm2gqb7iTZ1pToS6K0HdLz5YQme6xuK9a9eFjLtgQdQSBcM7lFnOLDsmVHBpfF'
        b'1ddBSc6gU9kmJwadwBJuCzr1OtYGHcpKFN7rOAXKkp1BC5Yli002n5NyYu3b8C3qX7Oa8C1qhMiWoCmYGLQDuWCrwWtCjUPusN4MpdmVQ5gL2mimfTml7DxaY5zHkZ95'
        b'Hmf7/VD62y9/PePLMUUkKrkgjho1iqYrKroBm/AzGYvJ50b5a6KWcXUNSjUgI77YJURNPs9S9zL2s9yVyNTn7aTj6q32efwMSdWWKwuqff5oKibKGwJ1hNzcFYC7FkWt'
        b'+LCqzgeksFLX4JPZ4cIGhFSp0uP1RqWfTa3zR6VJE4pmRqW5dF824WczXUkMuul8XKICJLJdMfkDy4GUTsAGuBd6qhcshKJZa+yYwe2F5nj0e2CEoQqT4oFWRM0VTPRi'
        b'8zXUuukLposr4T089SwL0ON/GGg6gelYkub01bh40CMvi3DpIPIqmfn50318SLp8j1lxoZ+QbHKNw2QWZjoIZkvNfBG94pH8IpkWW1xFbQppaB9bxrVcV3RY5KSDbGSK'
        b'8mQhwqE5UkAkpgv3WCsKdFbpXjey0I6Dl81BPp1pFEqyBbFcwKQLWM0tmGxRF7RaSaxju9DpmnIFrZVzB9dVXZWL2mG55DbB31CrJMM8Xyi4HFPuwn65PfsX5LUitmL6'
        b'XWjcQgZWliboCxMi6KZVCwyR31iu2bhqeBsMFVpV1RkkaTrX2JUGGRs/+Kq2jKrOY0kXpPw8fz6tnTLgvc9zulQPLXVk0vGOitDXqJMgvRp4+8o6b52iY3NWuMHw0clW'
        b'824d75aJV/4Qa+d/wKfVJoPwEtLI5A9FW915HQuzYtmxtqTsJBm3gYaVXXy7tOAWXkf6isrrFcVJFn6iY6ZmGcNaKKenKSZjSJaslkwpzZnepwFlSPPHa7v9Cer6BfWL'
        b'RU7QtvPdtF3aClRvi1EGZUQjl5WVoc6X2IAMr/bgOHmGdifW1I3r1m0oviNb2lUzWHTSZ8oCfU8OyeKq7zwwjvevBdpubcbvJs/8dk7qgrSdv5C39fzoO+eaJ1+/fdbY'
        b'5zJT3+7ZKVn8uHrKmx9OnbGotvRwbe8f8q56/+nvn7m44mL1p19/tvOJkOb589PffTVCHvVNY0FJ7h7/s2NLn30gp8PPXp8xr8eDxye99JdBA1/vUjH74Wd3vJz6ReO9'
        b'b+0xVex/JOWpY9d89Ebo2Zzrc7/6oN+RKZ+mfNewedjuc89e/XRx9muWZ8t/22vDwk3DHvpw2h/kY6Py/J/v+LQys+72jzucmfxZrbD58GO/fy7nwQG//Xz7zdr7Xzj6'
        b'vf3++I82De2eOm3Fi/fU3j757Cifd9PGgnuOfpo6vOzl02n7OuUt7vjmoYYVhwqOdR3w+XBf5vwe4abvr6468bf/ePxQycqBea7SCQ9N33z/gdShix/e4gn033ZLScbc'
        b'jS+4SgtL3rvyk5+553z03OimXudGdR6jOlKV7D8N2GiaETn0/RO9q7d5LC8+3m/coH6WHUPXTuh7/Jq+572DF+4v7H3sUMVd6qDZf5n/q9K/3X7K/fXLTb/59V8r1a97'
        b'jisr3vXChpFbfuizatahxWub/hodt3j38sPR+zrd8uK8pp3vVr35ivD9c0/27VH3wt6//YLr3e/I1kFffHTk/c/Wnnx7+ZhPfn9m24b5Jc///ImDS7ctXu778Iz3hcxt'
        b'oR2f8le+9fuiwT+3HV0dCvU5NjKtLPWXK55w5BxfXnrTprLzm0wn3itf8vS57/447dnKE3sGnvvwxvU556JbRn1y4LbPTfs3Pf7UlRnzl5x4aPFXvd8KXHXq8C1T191w'
        b'4rGPD416Y96dxfOWPvbhIW3mbdNmrJy75O3STlOOLGjY9MT3H74+0/RK9k2vRkcfecj+1+xZC+479tWiP37y3jNvDz/88UPvnXlmz9GlmSNu2Ft17KXhWS8WDPjKes6n'
        b'vpofjOy8ec0r3qFzPxjzxJob7tp3y5BTrv4nL77y2e0np/dYMHjoXw6+kPDG9ynukx/+6bfPr/l83VePfrb+w33vFH3/y/C0Ny6kv3P9X//r/iOvLOrd844tF8+s7iP9'
        b'dc3Wm/cVfPnMDVe+OyOlQ9nL3391rOy+/d/seoN7575vuza98/qOP1/36LQTbrda9eXkrz/6g+V0+SNDZw8588Uf5bW7un52964Tp2a9svDVSa/dd/Tv2f4fblv6t6cr'
        b'd74aePUv37gtg4f7d60ZsX3X4dpea9++ZUzvt/ZO3+9Znf9t1tknd7713VuuzbOv9dx/06Cbn3MV7PhgZ+MbM2/88oHK7Y9+dMcPP6z+Wj49dOfgKVu/ePDAx8vnvhfY'
        b'ePJIl4NTj559T9zWNXB4l//kNxdn7/9mqf13e7aO+tYy9/CR5+TTLt01w6l8G7rpLFbX9Z+orZH7ahGOS1FXi+qx9AwWEeIh7Uhv8v5aVpiPYaGOa3u1rYJ6t7rNy0LI'
        b'nK0paI6GvT43FhBbVB+b2IG8XGob1HXag3EKlOrZjGYFyvvVA+RGwpmRp67Fg1fbxL752tmZKONMUs+KbmVkAAUz2vpUdRW0gmwi9ZLwHk+n1Q3M15W2Ee348Iw6ONwu'
        b'TbAEcFtQ7x5cE1d58eTSvtp6V+tj7Vu0p/qU2jl186xAPvW84VIVBHX1oNYaCI3BwBCs5TFtpXaHvx9FCNrY0M7x+aghWNNSbbtNfUJQ76IYOqK2Rz19iYy3Qb0jJuNV'
        b'bzXcV6+fo97vT5ijnolh6iHqfiDFftK28KMX19B/YWH/v1xc3djG/e9+MURT3rpyWY8AiUdOAm++EY39zfzl/0l/dnZx2lBBWhDxfwov2IA4tqTxQgrcp/bhhamdeCFd'
        b'AJqnZ0H2CGdmpkkaKwiZ/JW84O3FCw3An1rxIL0nLyQLfC5ds3mhK6ohCSa6WjKhVBTdCqKADvhMLe8dvGBlT/B/d17IFvh0XnDQeyddk3vxjjqJTHsFEdonQYndciBn'
        b'Ju+wOKisHKoDWjRf4KHFVwh8Pu8oU16MnbHd/r9g386lmTLH0bqR010JLNvbhvsI2k3u4/PVtczv4JRJakTdmD/WwjmzxC7aU+OrL5gfEfzdACpXFo4rvPMXvv8akLy6'
        b'uPTu0+e+++TZ0tPykZ2Ti98cd9+erXvP3Tpx2tzTD1RPUZwNK+7zf9jj2bpoh87Wd79eXDS4U8qFXnc5vt3zjFTySc/D97iqIucHfDFp61U3Prgt8cFzpwf+POnnh7a/'
        b'e5O6eHrXXlsm/GZP+N3fTTvzHyMX9Nn/+B87u/802rblUdtXKz9bqhSs67p2/RdfrN23bN+LjopPFprPyikzbu+53/78O08muWdt+r73njUl452Hfzk8MOtIj5nVmxut'
        b'Xf/zgxt7X5x475dPvPbHiqzPty70FWpLnnnptW2/fX/ZOwv+fPDlRSs3LC987fAvtwzbevz5LgcXHX7pyvd+96cDex/uue+xX3W6duOhX7+d/kYn7/43tnt7LCocvbhk'
        b'1ksX9h3+zdOOEWdNx//wepl351vTfr0h99zLv92X+mLO9QMXTXMnHXgw6eDujQvzN29+8/49OdMnbDxw6Fyg8OI7z9/Wr3Djweqr9u3507qXC99//ch1Uze+HS77m2tf'
        b'be3mH9b95s3R78/f+n6Dljflk7nzj3iGvbnmjQu33nbmgbuaTnS5/vyi4a8PPfY6f/zb0Xf//vAH3h1nPy/fJxXWnn2qdnjZ2dNvJ7juqVt/dOsVAzdvXfrQd9/c/MrO'
        b't8YceHx8zrlUd6jreUFIcQ37vuvJidqqjY7HX+i2USgZNjar48xp47okXvGrazp3CfxqXFcx+w/WcesGPC+du6di9VXpw37uerl+Q97sn70nbH1SHeJLfverv5d9+et3'
        b'rzr6ZUXduRmjl5cE099+/5btY94oEcKu0URZjLZrm3RwWqet7Yvw1HE+wNN0caD2YEGAXDjv1e6ch3kMMkDdaOE6qJvUbeppUd08UD1LoeIS543FEJRAtBwxwlDy6pGA'
        b'upOF+71VOzWgu3a0QH2krxm21ZX8jdombSftzSnayeXaSXV7QWlhPnpUAgID482tK9XWWrhuM0wpbm0DZdQeK1BXamFPszfvlr681Xu1e4mgKtLCXUohk7bOhdkK1IM3'
        b'mLmkoeKimeoG5vtmi0MNaWv7q6fGTdTWQ1sn8upRX0kAl9602SO1e/NLtQ19BE7w8aPV4+opeqE9MnFSAToIn2LiliwyjxWcPa6k0hZpT6lhot/6FPJc+jLzMmFgjXY7'
        b'UVw3V6mPlOI7V3Ghuk49LnBW9ayghtQdngAy9XPS6rXDg4A+7AubSJAfoz7ckWL5XV/cmKyF1Ye1NfhCPcrP1Pb1IQoloJ7RdpUazqc6DUb3U8Pz6ZV2sHxaQFtB/vzg'
        b'qya+SH1cO0OvCioEdZu2WVs7pR8P5a3hr9WOw/SQ38+H1SfV26CqMJBs+RO1u6HvMGzbSicRAZZ3hWm89kCQwcJRdbN2OAHI1NJCu3pK6AMT/ihGDu2kPi2p2x3abSwA'
        b'9JbMzuTaC4YEHXqVlkFXDpu4jIXSIPWe2dSgSereadp+DWehBFt0DzT26Dzqu7atfKG2zVSghftjeOcD/JwR2lYaraz8YPBGbW0xzplwCz92kcpiUo8B+NpeSjgRJshl'
        b'Rr/jDyWoKwVt38wSAnTt1goA2LVTphQW4xxONgEJfkxbOUJUH56jrqCpssxSw6UskuuUMihlYj8z57xZHJ8N77FZ6vYG7QQ0d2qhmeNncEBUP6zdRQAw4BbtNACkevcN'
        b'enRWXn2sNww8CmxE7V6TtlY9aG9gji+kCl490xXocRyETG2NdqC00FUCX12hnTDPENK1Q8OYx7ddN01lMFxcDFQqkMk7EtR7BO1Ar0k0Fdp+dKgB82nQzui4MUU7oa5X'
        b'V4naCnVPGStmLz+jtLhvcSGtF22l+iT6y1sjli0xUwuuTYaJLlZXq8f7FkPLJV69b7m6gwa1j7Z7Pltmk2HAXcVYfFjRNovqqalBNqhh7TbtiYJi9XAfV/+Svuo24ESS'
        b'tPtFdQUMlB62doN2u3pPaYG6v8vEYlhonXh1T6IaoqFp0g7eoK3NV7SzaMMFL6fxQImHsgIptIZDFQUlc9QHTRxfymn3SDdSoxaqJ4sAvhG20K8mDMyj6qMJQUHbMUfb'
        b'xFDNwT4eWHBh7fE0jFgpJfPq9hHabuptn8JppcAVDRms3dqZ5yzanYJZ23sz4Yyp2pqEmAtK5n5SXddNHKFt1+6gkczLbDJ8QDKng1sb0QWkehJQHHFxOyb0RRc/6/S1'
        b'qYWnSJxT3S2OG9GXRqtJu9URc7VJ07VY28icgmaou4mLq1K3A46M88jJ3HFq28ajR87e0BJ03aw9pN6q3Y9IpRCWSD7wk+p6ZJ7uBDQyiQZmXWmh+pDETVYftmgrh3KB'
        b'XPzq+AhtdQKMXKQePy0FkFg9R+DStB2i9qB2YlGAPBWt0vYXJWgb+heWlDXQiSYwo0BoIAgCwO8ZMt9crG1fTAOyVH24H2G9fhMnA1LR9ssJ2l4BIPBuP3NXe0rbqR1B'
        b'h7W0cZg5s5SgHhW0o+oZP6EJ9UHtPu3OAm3DJG1jaV9XYYkJurpT25kjapsXq08xMIftwFE6RbtN3QQrF0YmUty3pD/UaOb6ciaA3Z6U7Qp1/Th9H1s/xQV8HiyDjeqO'
        b'IguXnieJ2jHtJEHPVOCk0cPxlCm0wVg49YQtQX0cVpV6yEGjpD5iVw8AjECjlmgb5msPQ9OAK7VwWdpRae6EeipGOzJkcOmUQugclIRhZzqMVu/SYDfco24dQN7ZrldP'
        b'zcSxQf9etI9Jhbx6GFj0p6m5UzntNDa3P215iRzb9HBj7dxTUldpGypYzIkj2in17tLiyfmTLcDQ7jJLAgoH1hA4Tdfu1e4h57fYX8BJM7X1Cdo+gCbtUW37ZalIGU6B'
        b'h/4bMFb/dpfYiTExebvxJsEqWPmWf3Y+WZBMDnJ/nA1EusBbBaf+hp14GNpKuiMEwa7fJwtmLE3AgAFpLcp00KkJy4O2JBLlsrPzEWGZGO8dz/gz55p5Jt/W9blt5EKg'
        b'od7tbvZ5ZxwSvMTH9w9viOlwfN2a6aAcLVQZEjn0RMkUCfzPwrWCk/ka+IvMDs9G3bNIb/gV4FeAXxF+0+FXgt9Z4dnVHPzaw7PRjC7SFfPXYE4+xIdmG9pyTRxqynnF'
        b'WimSVGtq4mvNTUKtpQkPAy2yzWuttTVJdG/32msTmkx0n+B11CY2mene4XXWJjVZ8KAxkAyld4TfDvCbCr8p8JsDv6nwC+/xqDTSLciFk+A3KUhudCIJQfRLzkeSIV8a'
        b'/KbAb0f4dcJvOvzmoU43/FqCUqS7bIlkyGIkU06MZMnOSGc5KZItJ0e6yB2arHJKk01OjXQKijIXzkK98UgPOS3ikjtG+snpkSlyRmSynBmZKmdFrpU7RYrlzpF8OTvS'
        b'V+4SKZBzIn3krpEiOTcySO4WGS53j4yWe0TGyD0jw+S8yBVyr8gQuXdklNwnMlZ2Ra6U8yMj5YLIULlvZIRcGLlK7hcZLPePDJQHRErlgZH+8qBIiTw4MkO+IjJRHhKZ'
        b'IF8ZuVoeGimUh0WmyVdFpsvDI2Vh+you0lMeEbkmkAF3HeSRkUnyqMg4eXRkpjwmMkDmI+ODFniTGxaC1qCtCkcpLeQMZYS6hiZXSfJY+WqYP3vQHnGQ8kqzY1ZnKCmU'
        b'FkqHnJmhrFCnUOdQDnzTLdQ71C/UPzQgdHVoQqgoNDFUEioNzQjNDM0CeOgmXxMrzxp2hq1h1yohYgux2OisXAeVnBzqEEoJddRL7wJldw/lhXqFXKH8UN/QoNDg0BWh'
        b'IaErQ0NDw0JXhYaHRoRGhkaFRofGhMaGrgmNh5qLQ5NCU6DOfvK4WJ0mqNNEdZqhPlYTlt8rVABfXBsqrkqQx8dyJ4ZE8nufCPlSQql6a3JDPaElvaEl46CGstDUqlR5'
        b'gvFNU0LYGUygGnrRtwlQSyKNZyaMUDZ83YO+7wPfF4QKQwOhvUVUzrTQ9KosuShWuwhtFakk6WY7zmOTI5wXdoTzw46gI1y8SkBFDXrSl570ZU9udgQTSJPlWuZUn9xX'
        b'NNuFtK+fhnslMzkKcw28khggxcYa3lD/1o1WL3TM8/dx5VYzVdLy3IqGam+g2ucSlFsQB+VjRcjatesKyl3lI1kbqqFFTLrdloOOi5WXDZMWlwToboEnUKWgDYXVs6yS'
        b'VGfIbhsPweuqog5DeYiUhnh061EL+BHu7OhpurZe8fj9kBK9dQvQsBc1zJRXOOYviTtPuh3YrvN4kHh+B144Q4+6TvYAliUHC6iDHhXr6+qjdihd9lSVo4WDtcrNTlaZ'
        b'SWGzA4YYZo6aq6icaEJlnbtcWUCxKzHypnvR0jqfd3nskR0e+VhhUQfc+wPlukdLK6SqvOUL/FEL3FFhNrrx+QN+ekua81TDknKlOYF6uZii7+jGSU8VP6k4+OqoHC9M'
        b'YHkF+0DxeJagR3FMoAYDJUyVXk+5EjV7y2GCB0bFiuoFpG+Onl5Y4ImoHSMfs3um0POCPskBpbzSg9EO3W7IXuFmE2mBO1RJiEpuxVMVdbrlan95hdfjriyvXMhUiQEw'
        b'ZOaIDDnZC0IfV6tYcwjMyBcwt08CC2iDSlPoNAndnuKB/3g8VBfIjlRYBYzz4sQgrzsGaFtH8B86QULgfC+mXkk0gcMA2hZtJKVUo43H4G3YApjOAQsrC1sS5AEHCVVo'
        b'a5FE7h85ssAQw7mk6iUFpbC9gVOuDjuaTEEhnLAIHR85msy+NEpxSv+wI4FrMoU5phoWtodT4I0T+u7IwLEwhy2Q7rJKCJrDHaFGwTc1KCjF8CwnnF6F7mFKUZkL6kmF'
        b'euZQ7kz4OhtL8w2H513DHSifP9wB8I6F7NUcTVbIaQmnQU4J9goY61VoC1MRlGAH4ak8M5S3KWyGb2xUamfIgzPhhB7a4Xv9u6AN7ux4h2F3grYZHOt7mIfvT8N3SeHE'
        b'BMNWTgwn07vETHSCC4yhzAUT8F1QAEybmMEx+y1y22lj3vdjSnNsJF+C8beHO0G9Ao5H0JRGNnixEXiT2pphjAApujXDieP/8BDk/71E+icJrRGaPzbpVvpOg1YVmDWW'
        b'Ge7NZMuXgvpA5C3UQb5C04nONQPdm456P6JTSBayicq1imm8JFl/AAQvtFgmHfSdh5bJa4K+TJww1S59maTFLxN4K+L0hSXYnTJbLBycvgL4RqI7BHlTUPIHKOi7OYx/'
        b'6TDtIurYBS3K1UELGeFYg1AbAx5YKJ1Gcr6acOdwj3AvAP+sKhN6NwLQ7dNkD6Ommh1KTQjaw51hOS4CwEtK4LJwSxbh3on3QQctOCgnmADEYZIOwKS1x94F7QDuJb6h'
        b'4Z7hxHBnmQ/3gP+94H/XcJ8qPtwB6wl3xWWVBsQlPO8U5sPJ4WQkyqottKxNCMawkDoErdCbRAB4+A3C0gg7M7kmZzgFSAF84szgYNkkEomQAF8BcaA8Rd/DnYxawWbU'
        b'eGoy+ZbAU3M4H0pNCiaFMykPIANob1I4l1K5eqonpXrqqTxK5empHErl6KlORksp1ZlSnfVUD0r10FO9KNVLT2VTKltPdadUdz3VhVJd9FQ3SnXTU11jI4epLEplYaoq'
        b'CTaGQiTtg9wGRJmICKCv4d7hROhxcjD5DvReJdHVgleClgyEFigDRr8KvWjrvcng0EQQRjQVoQxKFcnRgYRjj4ibnhcEJdKglYzQGM0esjv8X1m7rn7/Bvjjfx5H9YId'
        b'1r8uhqOcuisu1EA0806Kg5XCC5LAsz/pO6vVTr5G00ibUfhWSmRajGkC6ilK39gdFMdMspvTBTvgL/jj2/uT/upISRZTALfh4ar0d4fJQb7BW+A3w6iL8Bvz6wgYDNjm'
        b'sFXHb+YwF4ffxLCJtnMgWMI2IPgBrzHN7hbbUZtUyr/AcT8N6l1mXd1NR/wiIHmpVaesRqdOY6ckWCZIewiAlm2sI6tIaVNJRUXzcDI6sqTnUpByQhcTw2bcoWEokgBR'
        b'JSLaxhSqrIftGzN5LDUhnILLEAeLkJhoAiQbtg0FEnBkC2V1n3Ug558Qr6oOSBDQKSB8Ub9PhlJI4Rpj9FB5MQ8sPzKoqf+zEH2/OaayDjAs4NVuyebNMAkpfDbBmP1S'
        b'GLPHT0cjkppAFoaTkAyOTYekT0caTUdHIM9Efzq9wXQ6psm/fHeAOwea/dI7+8YUGjw0jbdkki0BptoY+hEthh4IvrAlC01eJeWJoOgvM0hwHuuTgKDE3dmkNGBkRsS0'
        b'sK+ZYAeCyW6yNJpQGEGGezaJC3DLa42SffxSjr7IZN/7ZxFz7gwlA2OeFsqosugxYqxxtVgR8yubw4n4xPia7YlAadiqhEWS8iS05VSsZBsKQeCbw/ANPIHnttg38bXf'
        b'G2/KppuziWVtmuXEHNTGghoipwKdhmGnqAroSQJD26Djxrp0pF2XGMx2kSH7EwIVyu+Rv/yA/8kOPKLOar+7rqLKvVRB1WvlU7POw0i8pDtyJfhz8cTC/1NhNLL+nbYG'
        b'zazb8bKFhIrrDsFBGwN2N/vvdkkivzkYxhLtmlngEQmDWdqlTzPT7BarkMI7LPgWtxG4fi+9JhVKvCuTyShuwrooHoXoX+5XXsFnr+LlV3h5jWlJoxcbv/KfZBbQ6K2u'
        b'UF6n29rywELl12SNDTeecgx1oLxBZi7VspJHhQL/HhXLK4DzX1juR5vtqEX3zBS1+I2bBd66inKv35X4rxlA15x/Axn9/17+mUMNhMlGZNqiHDpisUotDzScQqbJwbO/'
        b'1gce7E9q48/R5tN//s+s/29OO8wpomSZJEpD7HyVKNXY+VxRcgwQpWw7P1KUxtnR9YcV2U0g4QTqZxma0TzBUUgDd7wM0O3WV2RteT0sy4Ci3Mkzs13yTcDOUl6mdTdh'
        b'WaWnHt0WK+jMDk9WKssb/B63O5rmdvsb6kl2iII2NFKBpwnu5oTyVUtHE3H2rSNr6+QGrwcd8zBnTrBPSsnoHrbNEx7rcvYrdEerRUPVUEIb7Av/DYfJ84I='
    ))))
