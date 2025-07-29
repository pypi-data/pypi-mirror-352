
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
        b'eJzcfXdcW0e28G0qSKIYYwy4yQUbgSSwwb0RV6rA4ErsIIEEyIAAFdtg4YZtUW3ccO8VXAD3GtszSTZts1knu3FI8lI3GyfeJJvNy+7zpnwzcyUhmu1k3/vnQz+uruZO'
        b'OTP39Dkz8ynV6U+C/mPRv2UduuipDEpPZ9B65hBjYA2cga5gDtMZglwqQ6hn9dx6SifSC/RC9C0u87GKrOIKqoKmqQWUKZajDF6lZTSVIaGpsjC9yCDJlOrF6Coj997k'
        b'6mOQrKMXUIsovShD8qzEJOG/o6golJJOeeUovB71l8zNM8hTS615RSb5LKPJasjOkxfrsvN1uQaJgn0gQoA+EOMLjS5ttDqb9ugPi/5Fzm/LOHRxUDm0HvVovbicrqQq'
        b'qHKmzN9OVyCY7UwFRVOr6FVMusc9goRCkOQqWE2250DhSsei/964Yo4MVjqlkGvaqH/gx3MLMEjfG7mE7bQfGlJt0oF0f+qvfNlvpzZS3UJJKpuEoWQclIPNYd2Q0k8N'
        b'6frOkLoa6Agpp7FFoftEsBtsTVfBBlj/nH0urFTOh5WwJnJO3Ny4cFgHaxWwCtay1Ix5QtgMz8EW458KTIwlApX85seyr7RfagtyHmrDDMqt4et+0sXpHmpfzwrIzssp'
        b'YM6vCx4XTa0rFS2K81cw1mG4LXgRnpWiaiNwpck2VTisjmTguiHUIHCBQ/XvgjesA1DGeEMsqAGb4eZElA3Ugc0iysefTQA3B3qBo2YvlEPBtjFhCjPGVv6CEx/5Tcox'
        b'F5UZTPIcHk2mtPnoLBaD2ZqZZTMWWI0mBg+BEA9IsIz2oc0yV9FGto3LsZmy20SZmWabKTOzTZqZmV1g0JlsxZmZCtajJXxppM0++F6KL7iSEFxxf1zxF36MkGZoIbky'
        b'PzIMejs09TP+ZRuKnttGgRuJSrVGFQ6qUjyHWBktAIeGwEb50gIM0Qder9CvC6jYPbY79L+DItIeUASjqBCbjy/3hR+lXZt1YOJSjROjPppKnn6oyF/+OnVKQMm1/RLy'
        b'ZXyRhUXswKM0vtMqx6zO5xM/yRZan6GDKJRTdvfZAMoWiRJBI2wcKQWnlAiiSrg5PSqNR4YwtSoMVkaGxyfT1OJnxfAY2JL0DLyhoG2DUakM4IAOKepQokoCrvYPg9Wg'
        b'GZziqBBwiwN7MuFtWz+Uy6QB6/BLnTwtEvUa34koaQoDt45bYhuInsPrOXBzN28dHAgfKJ2oYG2BKBMHboHqRJUiIXJSsoASpjOBcB88SeoPnguOJ4avBufxkMbHqxhK'
        b'CnYx8FQ8XGeT476tWwk3wpoUWJ0wFDyfrIZVSeA0R/mDChaugWvGohbwS5wCToQmxivjVQRFBZQPrGbB0aWa+aG2PhjKo5MW4McCiuNoeApeBgdNUbZBuP7DcC/YyGP2'
        b'QGVyPKxTxKPq4TYWXF8MbqKxwugxDeyGDYmjouPhvihYlwg3paCqfAezE+ExnTNL8mq4BecAB4Ljk/kMPvAcOxLV/LyC4ftSA7fDq9I49J6KYQ2sNQxOxB0OgPtYeAKc'
        b'ibZhaoM7weUiKdwUqUrQ2HCueHgJVqUkxWdLUd7Rzwrjp4xDncZNgtsD0bjXKMExVgM3xSvVQjR4Fxh4AdZNIp2Dx8FBUBEBNyXBzfAgOJqoVKgSBFTvgSzcBteNIWiw'
        b'OBhsSExRxUegF1AVr0yIVMclCyklJcgEl+BuWJdOXtPcIVoMCxqG2xEog5qmpPAIA6/AVs4Wjp6X4MyJOEsE7v1wn9SwRMQnNsFahI+pKiE1nRPCNWAHaCLU9Cy8Afag'
        b'3Khfc8LikuAmTVLKPLAJ7MFZlRMEM2WhHXgh48m1jxFx4KARs2UdnEPgEDpEDrHDyyFxSB0yh7fDx+Hr8HP0cvg7ejsCHH0cgY6+jiBHsCPE0c/R3zHAMdAxyCF3DHYM'
        b'cQx1DHOEOoY7RjjCHApHuCPCoXSoHGpHpCPKMdIxyhHtiHGMdozJGetk6FQlhxg6jRg6RRg6TZg4YuPpHvdOhp7XmaH7OhlOR4a+TsO/9tawuT3wF3hAJ4CN8XAjIbje'
        b'oGk8prdIjUqhApWY3Py1sNHGgnPwmtYWgLJkgRPoVSBUZilmNWig6djMHFtfwihSYWMEaFTGIUIA64vm0rACnJ9gC8bPTsKj4FKEQgUrEerCmlQhaGIi4KlBtiCM3RBx'
        b'AfzClOjVc/Gz4A4a3BoNT5CHGZnwQCIiTPzIC2HfThocRy+4lm9z32IGMaM4DA0Xl6akwQV4E27gybJhAayMUCsYigGXi8FpOiMU7iFPkuE1UyJoQgQtpODBeGEBE0b1'
        b'4eG8CHb1SYTVCKM3o/aGwkOlNDgLbplJOW9wpBfBQhpVuWk8aKGTzAJSDu5AIB1OJEinpClQAaqFY5i+A1aSLqDknaA5IgHWJqYIKLCpjzCW8dGDreShHdQNJpWGqWgK'
        b'tqQKVzAjUQ+rbPhNlvohAbkpDHXBNARsoqdowV6+b3uCk1C/EzAgu8LM9CxwHpwm1YXAQ/GEVBSY+sXgtrk/AxxL80l1YD/cvgLWJCsR0tvnc/TUOb1JoRxQKQWnYTVO'
        b'RyO4EVym54Jz4AIZY7jFb2miUoPJjaPKwQlhCCMBpzIJ7/VBsqAK1sSBs6hkOdw3jJ41E14neDJ97GTEWdUYwmpveIueDdessmFB3nt8LmIr0AFacZUR6ng0LBoB1TeP'
        b'G9VrNeEHiHqbQX1iBBYaCfjVegn9ihiwA26YlM144DxG844aEtKPHLRbQ2IqkR5UziKCYghBsYSImFVsusd9T7oc/uuqIbEa47uln9CWKSjhxeiVX2lfzfpCW5n7Bfrm'
        b'7tXG7vGKi6aNOXLvFxYppQvXTmrYUFsrGxD7Pzn1Ey77VIZv1ArfkFFvPfBZ/XWrQmTFzApUrEYIRkQcrEtRwLp4UDcX8UJEeYGhHAtOwOtWIgp3Z7HdSMJ+4PpAeHuc'
        b'dQTKMhxeATcJ9SqTEWusAi2gqT3zILCFg1vAbbuVSIv6KUg0obwpCGMRb0QZgAPsl8B6hADTQAPfZhOoZpyZktSgirTJsr6wYbAMNFsxuwGbQwoj4Dq4RRVHJKAYXmTA'
        b'engNHiPaHdgPdgURkIiYICICsZLNPEih4YIUrxyn7tZJmyKpRJdq4wp1lnyipWH9ilolpvmPDy2hzb1deRVcG6u3WNtYiznbjLmh2Q+nMu1VonuMmOY+rppJ4dWUS0ur'
        b'eIyWhqkkBq6VYeKBm4QUp4SHwEXEG/rBbT1r7RN4nGRymN+gs3eLkVx3GFk57w2BZQhKmDP3m6+0i++8eTdma/2L9+/Wv3Sxfkuvl31yPkpiqdix3KOJv0daN6Zb/zh6'
        b'KDiXqAxDnDORRmziNFMaTBHMsGNdjUc0cAjRqAeyDYRbYQM/2Ez3b8pmNRa069OrKbEfbQ6k2vVptihrafcvB2nPQe73gotU4mowFlJrqEc+Pb8ZwqJOBmVEEO0MMW3z'
        b'CnCQBrfBFrbDi6Gd/+ku8Oy8YURr+A4Eu7vS3h8fU1FmUVaOzZKtsxqLTLW4KGFAjC0MY/elJHAM8VoyWikJESqNBmvJSCthqQjER3fDZgHcwyU9BRw5j4XDywWEod4D'
        b'BEKie8HO1YjP8o0jAvRHQneflkU6cQO82DNmYv6FlBxsU7I53P8GdtJUd/xS0DGTi2MPcsNAOLaDc8Pwa3h2F6sWwyDpjkK+7PsXxpKEEoJWDTvt/4X2ofZl/RfaDHD/'
        b'd0Fv+L1+B6SC1Ad3Xr5amPranZdTQ/94dzF88/WFr6XCN7ntdfo4uvqdkZ+VPJPHypPoLz9OElGzBvgO/VuDgrZiHRceBidAqwWcjdMgiwi//gtgL0aBXrCeBS2LUhU0'
        b'z364ziyuE/UIMrN1BTz5yHjyCWRoP8TmxHRZiCXPmGPNNJjNRWb1pIIilNMyRU0KuLgfpzPnWtqE+cvxtweRdbFTGTMWw+aBbnLD3K/Bg9we+vdMbmMw3t9UgFqk+MPK'
        b'pAikUBKTHW5FCF+FhIkGqR7gMtwGakRp4ylQnTx9qhe8UgiqjeV/+ZmzKFD5lbK5+bl5uQW5mmyNLkm39ONThi9+GK5t0n2hLciR5Hz0OkUZWoXNd9byXXvK4ZN6DJEn'
        b'D+rjJzTL3Vm9uxsScy/3WOCc2z3G4uvHjAV+++Jg4Og0FAyFpDIHW43gVA483zMNdvE8/YeygemC+ZxmrvHrmnW0BctiZcLXe8cl6rC6EqfjttYq5GN679J/rRUj8SCi'
        b'cu8LVzdJFRyP0g1wcyER/BqlSsPz/17gItLZdrNIWXh+oVWFc50RI7sPC3e1KiwsAakb11VqsCkFjcbmiHhwNozXGBZminOCi61YPmXlx/PqRMccIXCHdwkH1sFDz/E6'
        b'0YHhJaReRUKSJjkBWXC8hjJsqADuenYA3AC3eWKGBw5420zZeTqjyaDPNKzI9iSlQUKa/5gHu4ookDxCudpJpdGJabR5iBsfcO4DHvjwmaxnfMCjPBE2w50RxIyHl5bE'
        b'IW5Qm5iMMAOxByEVWiZIMYAbHd6cCyWwHHOxRGJ7/ia2nNMZMTiqO6VBrCnA4/LiYC+xfhYlPz7j3VV7Le8ufi53TL/MXI4iNk2/crg2QhWPKPkSqEyhKAE8QoNLC2E1'
        b'cUUND/gu9PLAsEFM6kf0z0Ewug/vQqrzRmjIUSv8gg2Zi8vG8YmvWXpTeGwOTc9bvD1sNmV889BbAosJpXwZEpq49N86ve6U4ZThobZYV6k6ZfgScYIvtaac8LRGXcad'
        b'enCxvlf4S+IAaZOOadraaDinO6MLFH3J3JMN0U7Y8C4d1zekz3dvR/X5O/Xi7rSF/YNaGulXW9qi3x7VR0j/aZQwuvgyIo2VAz7/cB1i2LhjC2ciC8nlZ4HXs8WgnimC'
        b't8CW7lnMExkPl6ez5BFck/O4NgJrpxLy4TVVGcPRMv6ONg9rxz+eEbez6u7bp/lsBB1x4RMe6Pj+Y9gT1qJAixTUIwMNKa0ID/oEBSDrebbxCX5mupOfmfntfmY8LF5d'
        b'0E+msWGOGw+PTob7I+A2BEIkFTmmiGDLL3nIjKAoedSsN1d9kZHCo9CiDJagcdQsa2ZvTSZlxsy9u0sbnWm0fZvHWqrRjxkJXqrXR/qAKL8Zf9x9af8LAW9/xry9b530'
        b'WOzcmIj162bQxsp91S99EvBDcuvMiy9GLPv+r4XbX+41OXDft/cXJe37LPybyXO+kb24hmVm/XPWhaioRccTAkdPHvL156VnfkkrbpxzWp3YuqhwwY2ln72444Pb95r+'
        b'YC9PvJQ4JWrbrjH02i2D4L1+HxVNHX92qL/giEJqJT6zy8/Ndxt7I7x5c89l60mKeNNsd9lqi1KhgNVJ4ap4IeV0iVPhzwrA7UVgtxWbyMKhCfCCBpy14odgczB67g3X'
        b'sDHwWAnxlsMKg8HTXPR/zqXDF8BGK9a0V/cBFyPU2H5X0rnQQQnBJkZFgWvW4ehhgB02eliSHa1IcHkq3ALPwwPEAhw0CW6JSMCOHbA+LgkZ8lLQysD9sDGJADpCq0Im'
        b'vjIcHolRqOFmpB8jJUzOPWeCzaS3GeBKCi8TUDvwuJyXCMQOvQxvgnpCsQpkhzTz1goDb7gMFtg4nDxF2Wp0ERpVvBI0ItVEwVAyMSseDc50MP4eY2AKi21ZBUZeXCh5'
        b'Ep7AIL3LDxGskA6gOXTlfuEY7meO5X7iOO5HoUCIiFuGyXm4u66+3TYT7KZdnPOaB+2+8hh7E4+sP6Lc8xFhybAamd9CZFq3xD/LgDX+ThssW+hBZ/7oX+yiszAWWxV2'
        b'OpgqF1aK7MJKqoIpF9lFlqQyHzt7iLILD9Pl4gWUyZ+jrHTpGJo0vIgyBUYhJdsuxuXsQlzDJEpP45Lmn+2C4vlGqlxgFxxiDlMzqCW7FjPlXuUSXL/dq4Ixa0lLHLo7'
        b'ZRceYg+TOg5xJG9QubSSRfmkdiaHNVJ2yTF6E01TJbWmGaSUDMEnq/SyCytoBLGkUozvKmhSUkxKijuVfMkuMz+slPElXLCi9Ecl2nrGNIzUKq1g6tH7qaQrqWUUvkPw'
        b'CPTMYZrPXU+bfiT5aKswhyF5UyulzryplQyu253zHskpJLmWVQqcudBdh1xn9OwhkZ7TC9Yj83UGVUGjcfbWCw+J7N6HxHqRXnyYwSl2b1S2Se9l9w6kyr0dIocUqYGs'
        b'XoLKie0sLlfug8bAp4LWi/Nxi/ftPnopeis+piHudA6l/6CX4RbtPofpQPyU03uX+9iZesYci+ClCbyMeaDex45K9EXsOodB+XxNcjttZ/JZ9GyM3hffO9PFej87fzfE'
        b'o3yGvhdf3p0Ht+Zr99X7j8Xf3ihPpd2HXH31ve0+dm9cH35m8rH74ifFW+3e+LeVf8d+qBd+qBcBqBeM+Xu7H+6dvg8aU8b8Av8LlfkvdCd2p7/P/8LpqJe99IHoN6Xv'
        b'u4EJpuy9CPx+qPWgSm/cwlKJ3c8Fg52tZ80hVtruW0Gvo01iq5S/c+pLwZq5j0QFyL43qUY+YpTyDrKRccpHYqxj51EuIqwlknLaTi+ltjAlHNbFnbpomzgz06QrNGRm'
        b'Kpg2Rh3VRls72/GSSQVGizW7qLB4yr9wIha7Zf2z8wzZ+choa7fr2rM9YuVF5ke00oyF3yNJUY7cWlpskIdauoApcFG/3AVmIJ7MtmPxzVi4SgRyBe0EeX07YIhHhhOx'
        b'uewxHNKMueKPLogf4CYf+erky3QFNoMcwRQWalEQ6fsoyGIosRlM2Qa50WoolIca8eMRoZYRj3qRBHzrTuLItbdHTlfpR17yQpvFKs8yyB/5GozWPIMZ9RkNBbo+4F1H'
        b'j+gRj+ghj7xCLc+q1eolKB1rtI96KeW5SI46R2kC+lfI2gRGk96wok0yHwM8ExuIKAm1amnjsouKS9u4fEMpMp1Ry0V6Q5tXVqnVoDObdejB0iKjqU1othQXGK1tnNlQ'
        b'bDZjC7bNay5qgNSk8G/zyi4yWbHVYW5jUU1tHEaDNiEZHkubAMNiaRNbbFn8nYA8wAlGqy6rwNBGG9tY9KhNaOEz0PltYqMl02orRg85q8VqbuOW4StbaMlFxTEYbYIS'
        b'W5HVoPDuVjn9NRekX2rcGCp2IePvMSptJMiFdVmOxgJRRgtZrMVy6CNG4pHXcGV0ECMhvwNJOsrPBNL+dAhJ8RMGoHshSg0kHlskVhksUGUoFf1isBj1YXjd2J/xIX7d'
        b'IDrgF9TiLwwTgEohUcvw8wJNYMsIpLfHJcNNGmWCGjqQSpPJjoctszrMC2BBKHSRwyfoggQXY6cOUUQYvYEEF1vO2VlLSInMinRa/G9Egm4fi8WbnbGzkxDZmFORKKSX'
        b'UegbCY1g6hCDGCUbTB1G4geJJA4JAQ6LDYvezuXSqD4O1Z2KxBeLRQoSg3sQ8WHhINDj+gR6DtXB4l/oG4lFXE9JHi9mzCf0XPEpPRbSAruItCV0PhfwrZN6mEkU+c05'
        b'f3OTqBKZnSHTgQINot9k/B7Jy0zBl2T3HU5TCMzP4FfMWgzWNlan17cJbcV6ndVgno6fittEGPsKdcVtYr0hR2crsCKkxUl6Y7bVnOSqsE1sWFFsyLYa9OZUnJaICwuf'
        b'gGceLlUcdaHPdNU7ELExy3CCZhxCF4xmfjwqIDQQEjMKo5cfjT/+tA1nBVvgiZBEMo0ZD6oi8YxjMj9BGAGuiBIFsAEcA5e7mCG4eYxFpLkuE7wUnuLNkbpsHjvt8rJ0'
        b'NpXcWpYeXSrxq6arkLRfShX7ITRDBc0xCDW8UQqNZWgFLUU2D5FSCCmQ7KMr2Uopvq/C4TwcAgQ3L0HgyHLEbieol53BSNSdqwdjNh5U4kP9HgPB2bHKQJU1oYZZfE9U'
        b'p7kI5xnUGAKtgs6nEFjozo4AKWdNgQQ8IcLuWfgOpXAI2wrsLEkLrMQqDaIDrHJVCjHWO9WuQDuueUo5ayf1orzVlUKErSxSaziTDN+jdPLLzpmLsdBBVETqsXPOOoqR'
        b'4hmFFE/OKshhSj+hkVJJU2UBaLAEWCyTyC+UtkpgkvDfOPIL0QmiUTuN6yD4TmsQ0mFLp020TGcmrk82FyE2Yq7m/OXmWIxw8Txqtns70/CFYHI2oQQD4ubip2aW7Ugs'
        b'yyRsshg1XGh5xo3CCF0Zxo/wScQPGcwLQwj3lDEyhNohCIEH0mVRuuxsQ7HV0i7u9YbsIrPO2tGz294AEtE63DTuByJyEmREEow4Qfpb2T7bJsLDhmiZrzLL3T0vN0Dj'
        b'aNesG8tLgYGIF4cEl4X03AeXVqHF1eXje8lvkklaNzgiZ2OjaacPgWLlQ/np+ltyUJmYpNGowhRCSqoGR8oZeAxUlXXxjXo5vy1x6GKgMpD2l8FsF/GuDsQCxDkCnvYq'
        b'6AyWpJNgOyeD8EKUiUMb8VPOQXFUhoA4OwRtvZzBh7OMBYakIp3eYO55hnoaRfGuPQEJMBHmCN3kzv1ncx5d511EGhIUBB3gOLjYHjoD61kK3E73AU2sH9wDakm43wR4'
        b'vQTPYpEAP5IVXBuGc6fCStec9CVEOovDRHD7AHjapkaFlvrBNXwhcBA0hIXB6sg4FawGjXPDEpKRna+OVyUk05TJ12vyQlBP+HZfcFadrpofB2sVCclJKCd2PqQk4QAy'
        b'cBxeiQENwmEhXsafnznKWrDC/f6dRV9pX8k6ZTilW3hnF7ha37rwxHrFhsaNzA/P7Du8u7WqtaJxIftyrrA1P2jCwteCqgvW2BtChCNb7F4W0XSRJfotpsGnYUPtXdk+'
        b'FfVdQ2+pNUYhsGIrPR5sBa0rZLAmkcRzcQNpcKQvdBCHBTwDq3KJy8LDXxFi556bMpL4xkHdItAML8BaFY5+K1GFww0TiH8mxMaBjaNgM/GuDEEjfyNCrYpTMeB4FCUE'
        b'x5gocAJcJm7w/H7gYKI6IQY2JCvjQZ175l9Ahc4WZMDb4KxrzuPp5ap3ttmAZHlmYZHeVmAgrgxsr1Cr0SeXOCsYzumBLBvUBWnVHUq7Z5QshoIcdMUsot1JKeiZahlz'
        b'Eb4vdkFlxj5ePe3yjK5BnwOBPTo9nghXF9Jyz/UluEjLU6DTiG4lbhIT/PZQEAHlYV65ScxHQ8JZYEOQjSew/JEuEiP0Bc6CatsoCkfXtIITHQnMg7rAUYT8nhQGmuMJ'
        b'WcLr45GmQ4p1S17webjDRWJgJ7j9+FlmZ8+cs8zIWqVzOlun4kkFusIsvW7KStpp6dkWYoSvhA5YbXHDXewZN6iCWxPB2bhksAlWgFNuTIY7OswGsqP8LWBbmj88S4Ez'
        b'cGMvsAZeWUlGLxocz3I6RGuLbTjckI8ySWNHLgvu0CMB5TF1TFgprz0x+I27WSlbid5mOYfeM0veM0feLbsKWb3t949jpW71zpOVjsfDsBueD0jEMztqfo4/PS4CB4rN'
        b'Q2xApYCbkuLnudmlIA/sosAhgwQ+n6Yn/usDCzni1I6Ns8lOLpVThIeC+uHpHWrkI2thJT+dLwNXlJg5Fq72ChLD4yQa1w+sS00MhDsT8cRSfPKcMFi1gGejc9ytz0OI'
        b'BFtFsHm6xajau561FKKCA66+f9r8gIQrvZKj9lfoknQFOQVZD7VK85fa32e9mvR+1htZ8bqt+pezzhq+iP3kT1HUvIn0vOiKuY7oz15pjdreMm/4yFFr5Kn7jlfM3EcP'
        b'6/tK/e/01Nvv3a1/5c27N9e3bh65a230AIoLDZb/aZBCRFilqhTe6hTaRHzd8+HFUI5dBPYQbgg2wONwZweOitipCh7iOepwsJOEEsFr2eA24podWCa8CNe72OY+0MhH'
        b'LZ0FB+aCmn7pZKIxxdmoNzzPBsEm3g0flQkuITuSn4k8Bxrg5gg1UiD8V7GwFmyXW0n8654VGa48KWCrADUjHcvAOrAHVBIXezhD85P+I0aHuaI++Cl/0GD59QzcB8/l'
        b'ZxabkVGPjSvCwUNcHHw1JWaIrY2MJMafOJ796bLRXfmlYYUh28kt23WzjjXzDEDAK33tuvGTZqGck1U+7gKEwVvQZQNm8ENcDH4N9VPPLN62BL8gNMZJPfOT2eg1O1lK'
        b'D+wEx09vHQ9bBTPhtVhwKRQ0KpDA3RGwNAjUFmBgfwgN5r73p2JjTQ9HfMdcHnmB0VFk1tL83G66RUTJoxRfT3l/1GhmJZ+8d8o/fLf70mHfpi5nfw7aNWQyZbx3IVRg'
        b'aULPnteL+tROJHNIywtG/Hxs5pGPqf4VE4uptDPriuOHNF29u+VmzL5RDwZvGRemGXnPfmDW4mO+Xme1BUEp27JCrcdqx76w6a97/vvrd4sv1F/de6A21j4/f6iJXfpO'
        b'fklr8rClJ/JOL56/o+Da2VurPw7efW5uklHaZ2rQ5YeBO1PfqQ9/1xF8IeRbuXGY/sdvZ95LHzGm4qe14/ordr+a13rh46+nVbwquXj70b8H9fpO9ebpnxQyMqOCKGkN'
        b'uO6a/HHAPR1CuDSB/PzQ1eHgVoQ6cEVHPYd7DhyEhwlZzgS74HY3VcJGcMpJmTxZwudT+CCA/XAvYv1kBsf1RpHE2IzfJubl4KRdRI3RC5eAW+AGUY3A+n5gH1GNwAWw'
        b'jeF1I3hEQYBXpYIq99sHx8a4NaN+ozlQExzKxwdso+AV0sF6sI1vKl4FqnEX+8C1LLw4zZe0BG+Ck/4uJQ/WpRI9TwLOWXEE4NyM3Ig40m1wQsuNpcG5XrCGMBBwE56d'
        b'7Qx7FMR6BD4OhhvgfpIldmG0S2pxWER7iC1QqyA6JhqU3WArrEkCrUKE/+MoNC43wPrHqU+/zVASulmI1IP6Cf8Ic/EPq1sDZCTYzYJI0w/dcYy/rxBdA5DVWjbgsdzE'
        b'qRMSBa9N6Exr5xlPbUUjHdGG74vcLMSKLiUddMQtA3vWER8PJeK3xD0ryXQmZGYiYz2zxKYr4F3zRCMlTbZ548U8Oosl24C4YybfP69fNfiNdJuXsxJUAekMFrVZuDNY'
        b'6IsZhg6UIa6HYUpllnbleWDDMB57GWoCuCVEGFPTv4vtKnZ+W7DO4LJdDcgedTqxsB4kQBoQo2fXe3WwUHM8LNRUnRUNmgkNmCab86gdo497hh5bx24dmmjQJEDQy6ld'
        b'cZVipF0JkHbFEe1KQDQqbhVqq/2+pxUKWLvqqkULeC0a1IIDEqRGL5F7WKq8Gn1ioS0W56iDhxcggRsWl6xGio/TdlSlIW0pPQz7AOeJO65roRMpahSogk29fb3gxQVG'
        b'au9ygSUD1dR/wbCvtEvu1GOL8uXm9a0VrRXHdxvpdFG+aKXod9M+z9gYsnFIs8/lkI3Kz31O5JzIuuDfEHAi56XhL/kI6xcGRuzS5+c06Spzz+nEOXF01huB1Ov/6jOv'
        b'xnS3Huk9hIEcAweTEG+60dmMROy11kBY00rYAK/w9iFhgHAHPBKVBs+R8gFDQD0xKRJBFV4xA3eIkXJiYMEZcB7xKGKlrpkIryOmvJNf58LH+h9nVoBTWlKF0lrerlFp'
        b'wQVP1h04heeOrfPBPp47zgZHnFawCW7k47pPgfVgHWGQSJ9qRuYW5pBgHTzo0mx+Hal4BrPmICzMxEZlRyt1NTVEIsOT7TLEpQLosn5dEFftLslTq7CNzS6wtIlzbAWE'
        b'vNu4YpS3TWjVmXMNVg/u9AQtDLG1cny/Cl9wPLh5jZs72dHlYCcF59P+PfOnx0GtYDQaJ4cyL8OX5Xg8pISBFBqseUV60px5hWvAHiMszKVuEFeiy36XbwzzHLJo6hkk'
        b'+q+0cxwxWRiGdNNrBLEwwkyUC8FJL3iBGCirTXyAzZrFBllLajrVxX3udmPNoDqvkMoRuVcw0U+9gqlLpFoHRuTmD8EaYvfACtgyzIJQ+qK0xAYvIw3jCmy1LoOXpMtA'
        b'nW+xDLZSVEjUZHhCAFtWwhYbDqQDe+DlSahIVZIG1kVo5hHTO35e3Ax4FdGMyrWoFZyFlUo1aE3Dy8PARXBdAm/D5w1PXIvLkkn7/6XYzW4ZI+ElW8D5PhHgVBKsmTXT'
        b'+S5R1rksrBkGT9swVgrgVqQG1bj6CXdEgMYwpKo00lQI2MKZTb2NP+05z1nw7M0Xoc1faV/965fajDst9Ye3NVY0vtxYMbKmhK6/VN/rZVHr7om70oLSdwWOqnhP+9nE'
        b'oFeDah5OCApsWTM3apQ1ShB9LIoj8XT3fvC/sPptpzdNA25OQPYTrFb6o/cnBGeYaLgWVlv5BVpwXaFTz0IspE8iYiInXYba9eHwJHFwwGoVn8V3uS9Yyy5FmTYRNgTr'
        b'vSDiUWRBVi1C0PG0vgy0wqugmjwWo7sDiQVwe4eFDEhtvfbERSVSXXGxAdEl5hid+dAsGeFCfmT6qSwc8ZLMAmO2wWQxZOaYiwozc4ye1pVHRa5WCQ/pOQIbsdDVburF'
        b'a+pf6MRgnn9MZBCeyhuM1OLEFBUSbptdbx3UpRB3BPruw/ASsLPR5FzugWQKP9h6cMCvMAucJ3OrsMkA1kbgYY4ewyCUOgDWwkM0Ioe6fH4p654FyNy+AFuXL4MXSxZb'
        b'ZOLiElkJRwVOZHNBbQ5x8ArgWbjPgmzyVi/vZd4SH7BxghieX46ptkRADfPnysFW4CCxTfBI/9WJOCwMNQi3wZMsenUtDNhomG+biB5P7490o9PowRXUv/AEJWgaAA/C'
        b'7cuVYVjuJ7mWWaSLnYuQaSxzL0inQwdLyoMd4NhSz+KPL9tQAHbAZgncAPYOIczTNgXbNMUlYPNyeBmz0QugJsGKFP4rsAVesaHOpHNgLcLkbWRwCsCZWQTcnTjsF1ld'
        b'NUkLYIOI8oVb2DTBfLJYJBQ0IyOhQ53w3BAr/tUqkwipYfEcqB4HjxF9nl+t1xALT4ALzAi4k6ImUhNh1Qh+4e05WLkKbkvBiwpV8bABNMfFiyjZZAa9tIOgxjYS5YkA'
        b'x81S1TJkw21C3H4B33MPLgguEXa3BK4VgZvI4DlCAjKR8Xd0cbowAGnow6hhc8FmIhr+WCimEB6nUnnagn5Tl/ABmYNKhZSMoqI+H65V3suVI72eJC/pj8N/qbw7Iq3y'
        b'wuTpfF51kAjnjfUfrFVOn+BH2aJRYgA8KMcqSgR2ZVUR91U3IIKqyUKqCKwRl8OmEOPWqpusZSYillsTP01ObdXAqAD7HzT3TiRLA059NMKvQNand5a26YU1QfcPhC09'
        b'HpccOjzXWL808IsR96WfSP/lP3z4lKNDv7lmnLdo2dfWf6qnbP7Iu2CU0LF+YGJU6vtRCzT9/AYWD1sxpmVLTXzwF9HTX342cHEW89wpgXLriOQ9R97Jqbo80pQ6ac6L'
        b'72v3H1hx5v61v9SN/sM/Pio8/8/ovFdHKz5Y0dhn0pX3Gn/QVI+7MLr5Tz62W2bF30pvbvxd7XuH6D+evL3vUmQed/z8nS//bbqS9eIHGdaWBznZu/89TnHpj+f+drj2'
        b'67XyT+YZn0/5hmkYd2OCSPbV2itViz8P/eeZ2uSHEybBD0MDp+cs+bJUv1hZMiGmOlPVcFssPbn/3JkxTdMm7Av7oTx45uyTH6X5rhPWZ/750d+l/645ePbZ+/32Hhzm'
        b'/3bVh6U5Wx7dOwbGh9hED/4xddqF0ou3PlP4EleAGFSAa4l4A4YaJeYgeIYIHpTC8yzD9bfiwEKwdsUixG5oionNX0Y/A27Pt2JuKYmN4xXEbZlO/dAcSZTTJQjRdyYm'
        b'hat5PgMrVNICBh6D58E+4lqbB48gMqpRang+dXkEXjdYw5SD02ADySDPB7ciUjA0WFcRUcnLpPB5vCC8DhzjfQg7YZXVyc+KTU6+D6qXkdIL4fUlEbAS7ATn45XxRLwI'
        b'KN9JbA68FEt6vBTZEo5EJPerC1ANtYkKlQapQ32TuNhQcIbUHyoTu2JjcWAsvAiuMip4PYOPNz3uRRzztYjOkUl/UERxKhqcXazm7f71JeBAREJy0gBYQ1PcYBrsB9uR'
        b'1o4dFwjTm8D6CPUgeIBUjtkzqgYRYl9wmYtDGv0lvoUNKMMBXqYSiQprRzLRMrCH718IbETQXRF3Ni6GwmNPVHVFv9ap0Kdb8UdEZlq7yJyEBSZHHJN+jITxk6B/xp/G'
        b'Vwnrh9KC3FPiMhIGFEYC4v1RGR+U7sPgeA8cGiRjzBUuSd3IeAjRpwHcI2INV3K9k1h9OahnsUq2utjGRPcgVmevRHcEXQXUc1YxEhcNsxQsWRY6D5yAW9unEtHr3oAM'
        b'Kd85xK5NyADNsEYDzibxyw2k4BIiA4TLx0fBJj5Cfze4ao1AGBgupODNxUJwiIlOs2SznZTDQJeCiKfpu2xNQLk3J6A7bE/AOPrkBLqnRgRPNTXCEuWc+3gYescSucdf'
        b'miHXaLEazBa5Nc/QedcdtaRD3nir3GiRmw0lNqPZoJdbi+TYCY0KolS8pwpeTikvwnGCWYacIrNBrjOVyi22LN5r06GqbJ0JxwEaC4uLzFaDXi1fYESmks0qJwGIRr3c'
        b'iZwEKlfd6IG1FIHQoSazwWI1G7EPvBO0E0ighRzbkBPkeGchfIfjEXGVzupRD7spkm8oxTGDfCnnj04F9fJlaMwQTN1WYLOgh3xxd/6Z0+Knp5MncqPeIg+bazAWmAx5'
        b'hQazKn6GRdGxHudou8IldXLcR1MujpXUyXEcKQbHVZdarilCA1dcjNrCoYddajLmkFL8gKJ3laXDAKF3hd6NJdtsLLZ26UgXJ48P1dmWkWpso9H9UHAuPD3SNX+ZtiBO'
        b'A9dFwtr0uARB2vjxoFEhgddKx4MdsUPG90GqPzwlC04P60IJfq7q53ekBMpJC7SbFhiHb47f/8bEIGYrXTfXUGlQPsJyukaJdQ364MGk3DOV//Fi266rugTOJcSYeRv3'
        b'jz9LW8zo7p/jZ36lVX0ep5PlfKF9oC3MeaiN13FbHsh+X2tMMshmZgyolf9d88Pnf5502efPVvkHd9++S/kbc6y6yj+dFnx1Wlevp74yLM1RGpTVWXpqrzgw806L3+vn'
        b'dWEXH2iX3Llav3bL4Ypg/bQoNjeEOpAx4MeiKwrGym/AMa1XhCqMd3HtWYXn9DbnkifWxeBGBNwUWRaPtG/ORkOkL0h+/ZSZIHO5WVdMRNHAdlG0mgrB8alI4GAvNx1A'
        b'C5GYEdNlCrOTf3lEWTkx3SMF1+hcrc7HNz61F6mR5gsQ8YMjZ/siyMjKS6f4WUN99ZiZMWy2rBwJ1kS45/fJitoVeR3W1LZLppn+isgEpB3MAqd8jWmlPYcdTeHJhPrN'
        b'y6y7eHK7j4cQaWyz8Fs/OhXURUfFjBozcnQ0uAJarFbzshKbhZhOF+F5ZPu0wkvwgq9YJvGBh4Ve3lKwGVSCWgbZcPCKFzwLjsKrxG74S58EvBZX/mqQNjw6fTxvTHxr'
        b'jqPqKar43watZNG4fk5sv6mdylnw5OJr/eP6/G6w/5ooGXfnRoywhn5+XezfWeXVN+Sph3rPm3Hwjz9vP7JszL0SsHt6w+vDIr6zbSrt29c3ePicrTHwG2rBW0Hq8oYT'
        b'tb8s0kbtT41/v/ztadl/2fj1T9RVGFAxcAZCbMwGnkOmdQvcAtd33EAhHp7jfafb4R68K4rLa7FYw42nQSvcI3vc5M+TVhmKM81F1swsbJ2jUQ/yxPcwjO/+CNPFJAq7'
        b'TPlUmO6szjWx4w7mfZzjguFztOM50jyp0C54/sFjViXOxCN0CmnyZyMSwHXQ0gHbe8Z1WB0JqlJGjWGpZaDGTw1ucQQbJD4sxdlviPA+Zj/FRFM2DHcWvBIEtyEMLVip'
        b'ptQZMSRnqhwZoYtnMJRcW3AlbQaPTK96c5Q46LiQitUW0NkiHpnIk/9BVz/uLEdptQW26BF84p6JidR2qw9N+WklE7ztfGLQ2F6UvGAqRxVrlTMDVlP87lnnQLN3OqyD'
        b'2+eNjgJns2E1RwnTaHAmH/D+1hdH9qNior4Roar6f6Px5qv6i72VXtN7LoL8o+VBOZ/OJK4SUIvs8zPpANcF6wQUC9fCi1p6SgFrw7tW6RcTY8RtO4OzYbBSCQ7B+gTs'
        b'4kRmThgJDYGbI8hkZ1WERAHrhpF577EzRNTr46bi3R1l7wa9l9CPIsuCd0QNF4sXUWEX9UmJ5mzV2OLUN8YMKerDka2H0Ds7lQgvIAkEb4DzyVQyWA9PEuhvmSdSVioC'
        b'j86o1blRfJfKSqZQ6+XHRFTqGnOQ7avRJPFg4hTKHrNdREVp/V9XM3xOXV8VrZ3wkKbkayz35/XqTxJXeP+ZvjhiP0P5rS26n7slkiT+NG02vV3ti4Zpbf793DgLSfwu'
        b'uw8dZYpEmLCmfGHqhlEk0W+6lfq2P3aQr1m2K+hFJe/qjphHnxrIoqHXRfw4Yzbf+k/BW+iwiTKW0q7JXZjxyjKSeLl0IXV18QoRAqksaOUPLEn8Q78hdNKEePS+UUMF'
        b'i0pI4tjIQdQM7gaDumkPKoV8YkxiMn1o/iohKp6/MHvbLJIoWxxIK8cMw3g4+eI4pzcldvgf6UPRj1DrusjtUyP4RGn4C1SlrplGyKmYF76QTxxqL6f+JV6I8Fk75psl'
        b'Nj5xZ94H1NV5n6HWtaUP1OXOxP4yKmjGa0KUKJNmq/nEhz4l1JrCUYhiP8raPnPYbGPy9OO05Sh6m/PVx+bNSS56O8pvf+uAEQ+WXXhtQYPyw4vb1437XlT8MFLrK+au'
        b'nPxLy72EgqsB754MePHW3PE/7Ppe9Pf8cUNfUkyb1pD7+a1JU/8wbnDzXwdvWfK25dvqjKWFey9vW3Z7/zlVwPelnw/Nb3s3A8p7vT5g9W1zwHcbI7+rh/OtW6Rqru/W'
        b'3q/Exw35sPc93YzJQ/vdP73Q+7NL+tF+2z7td/wFe+2imdKlc/Uf+v9QNmeTz0utNQ+576fPO3Jn1dEXIr869N2Ru99PfW5iXUH8yIZjn00pWvfFmBOflqnL/iv1DANN'
        b'byeHtq7/77J/e23Yt1fl9Y+Z1l071tufyZ9Xvbm34wP1qf+SvT3iamh0qObGsOsPp2w8c+Xq5JbXd/x4q3DiquMrwq87bmmPPfug1/LiK3/8L2HdyrDWO+VzF35CD/yk'
        b'18BPvQ58Enzg09jhE62SyM+Obz62d+cbH/0rsU91/qrZOz976/6cn3rfe29l28CQRw3L7D/UKNR/PzDmYforzcPe8704b0TA8BUffKsoV9sDLyYePfJp8+39tgezljet'
        b'ip7/ffOo/W3718yPGRL6xdyfN9y8l9Ec9t3//M+gceM2L58xViEmHoYViJwPtbsnFnvjlbuBWUSzSgeteGuOyki8k9dh0DyHTh3Ql5RKhNdFEQmqRFW43zCNgJIJGXgL'
        b'Nkj5WKft8BISUC6JBfbB2xSRWWHgCvGHLEAiuh7xj5R4cAYxsjlgSwEzBJws5f34FaAObI1QKxIinBsk+sKNsBGuYYvghTR+urJmdLLboZMGriWKKN6jM2M+Cfswglvw'
        b'iucWKpvZ3mC7K5yqxe9XzjYq/H59JMVTa51ilywlgjjLUxAHymiOCfTxk3C05yZV+Hsg+g5CH396GJKL/ZFS6kOWTwXQHOtPB6Jvyc8Mw/wsZoWklJgsI5ChchyehAjp'
        b'WaTz2qqArGtoEzlt0DYBMSw9ZPl/vlAMacR4ByR+AUWdWwWoRhf/LirAt+GPV3VB1ejlnVTdrsIf4Us9EWsCvDsZ0g1vIkthMwmnABfA5XlkdtPtP273skSCiwi5awTw'
        b'TPAS4jKPBa1m50zgFor4dXC4rR/cwA6EN8ERwhp7I83q/lQ8YFrl9mQnY16A9Nu8Gf5ks96TtgF84s+hQmqXdiDeJ7UADu1FGQMDVwgsBzE6fPbTABwsFiub8beCKXuT'
        b'wVhxyYgJGcdi5vvEhq1dNzPkG9VHkn1+2z5560/xP/yrNGZxW4TX7FXnz9XfHTy7SjI65OJCbZX35ft1+/WfPDflu/0X9276su6/wobsX/Ll1pSffq/+8tJm9QaRcdes'
        b'0Ff++vkPv0/7IqNiu6j65knfC+/ubC7L1uxwvP5zafGf704/V/eXP314+WzLu3/QKKxHyn6kv6YjF/ebrhBZQ/HYVSDjurHDpruDQD0JEHBuutsM1xG6nzwSvRje02kA'
        b'u52OznnwAB9odtzb11NLw2GZSXjO8QCnVhTF9+Iz7UHqyi1ntuHgMsmJWIR/OAtOjQQOnoNUg41DcJ72V+gDzsFjaewMsHcFz0E2jkkFNZEqjQpWJymElG9/0AxOs5nP'
        b'wRukT8i4WDsX1KTw6k+Cex+ufmTbuyHgKDgF6lwmZuD/Ont4aubhomPCPMI9mUcvHJ3F0MNnyQjhM3gtJRNI1g8JCbswb0a5nSZ+De5G7/9ruDe5iRw3/WMnd+rGMT2T'
        b'OH5l5cjYO+WmcbALXmEo3zFsjhQe6Hb+G/9ZZHR7jJOezmD1TAanZzMEei5DiP5F6F+cS2V4oW/JdnY7pxfU8duY4TgETi/Ui8gqHalBphfrvdZTeoleWsdkeKPfMvLb'
        b'm/z2Qb99yG9f8tsX/fYjv3uR336oRuJcRXX663uvF2f0crdGu1sL0PchrfmjZ2L80QfW4e3M8IZ/ffVB5Fnvbp4F60PIswDn7376/qiFPs5fA/QD0a9APUds70FtPkk8'
        b'o0/WmXS5BvPHos6OWew87JhHTmJKOmR6UgmjBXsJiatWX2rSFRqxw7ZUrtPrsSvRbCgsWmbw8Ex2rBwVQpnw7IDT88m7Hd0eTVJCLU8tMOgsBrmpyIq9tToryWyz4E3b'
        b'OzghLTiL3GDCLkq9PKtU7lyQqnb6lXXZVuMynRVXXFxkIm5mA27RVFDa0Tc5z8K7q1FTOrOHh5X4oZfrSknqMoPZmGNEqbiTVgPqNKrToMvO68F57BwFZ6tqMphWs85k'
        b'yTFgX7deZ9VhIAuMhUYrP6Comx07aMopMheSPQXly/OM2XmdneU2kxFVjiAx6g0mqzGn1DlSSP53qOjRgDyrtdgyITJSV2xULy0qMhktar0h0rnX+aPhrsc56GVm6bLz'
        b'u+ZRZ+caNXj3gmKEMcuLzPqePUmxFPFlcvwCNteKuXKGuFaf7EtyTiw82tDVf20yWo26AmOZAb3bLohpslh1puzOMwz4z+lDd0HOu9HRD2OuCY3jM6nx7kddfeZPsbWm'
        b'UGPDIc5LkSzZ6l6I09z/MUvdJPx+yyNm2jxVk7A4pVoNN2vB83jH3jFgp3BlOqug+W27DweI8PbGKSq8CKQuhab8YRO4CfZhM98BW41rnv0HZcEOl6vRC/FyuLBPHqCr'
        b'MvCBNs65gkM9P0yXoGMuBPeNWh4VqV9853z94W3XKhQ1lyquVYysUW24trOxIvTA5A2Dd62N9qbWXRmypNf+wgxkTRBlAEcp3+QFNNi8vIsoL4IHwS0ipQ1gG9jRVUq3'
        b'ytgZy8EWfn8jrC00g0twixT1XeHazp/qAxycOCCPmCg6eGlIBNwEmgbExXAUC2/QpkUW3nHWHAaRybHWOR7YrVbPgLU5oMaKX8xksGMprElUiSjGmwGb6MTUPD5IqAE1'
        b'WwkdvqjWuJhRo1lKVEbDPTORcoEnU8VDQknvKqeBXclJQgpphTS8Bm7Ynhhi56nzZxoRjmZmErEd6Cm2V1NeMrIwA2vsZX07Iq/aVY4X2418/LQZbzD4pAUXjQyfrT1Q'
        b'Gm/RuLqLol0R0HMwYk/Q9LxUDKu3dmop5VpjjSOcXRNgjTQPTMdlY2Y8x7AJgcXvZtK5SdeaskfBPc6roUZYfVH2UwG1ngdKnOm0c8x7eoBoiwuiRwEec2uuKTr1rxkB'
        b'cSZmvEa9pcfGtrsbU+LGXDpeN1N52QVGxNBVFsTXFU8HRA4PhDTTsKLYaCYyo0c4drrhGIrhaC+BhVLnge/YvIvRk20IY6n2nVkdAg9G/x/sp91hjxpPFoupaQo4CyvS'
        b'YV0gdHB4X10KbM4AV0gUVB6sTACnacQLNyKVkirPBZf5CLLG8XZYE08U/WgOsYoapOPvZBJGqo2ffDGHIZHeN/4VPKDmFe87chm33Ht8nrzuuCBg2NKoZvvijQ9ifJoH'
        b'1C1L+G/lbuvNgv6p47y3/Rgfrlq552pD4yeLKoS1Ib8sfLD3m94VCVOPjMvfs3j0LeWg71+uuzfFLzCYfe4LhYQskhkHz/TuzgRaEoU5J9gOGwiHWoIM2YvYExvPzxbA'
        b'G8JJDKgC18cT14yhmPWcSQibxJTCnbCC7NRcsFLn8qrA6mmchgYtYrCdMDawP5Brn2WAFbCJ+GwKhvH7u81GLUTznK+d7XnZSYtjwd6JiXBTJD6SAzaO48bQ4CZsERJL'
        b'C+wE63Mj2vfzRiy+Ge/p3Qr5Lb/HjgZH2/dPRCwaHgFrmKI+YAcx+PrCswsRVJXgUBw4G+fi5P7IVoMbQRNo6bAp21MyX4Mp21xabCXMl2zV3c58B+K9FvyJk0VCIja7'
        b'Mj1nac8VLE+38aJzo9x2DnwUXfYwru0e1rg/X/waHuwE5/9UzVrfrZo1PU9nyjXw4RsuxcjFFDopXUh3elp9y2RY/rRqFu5y1wW2HOJvfGDjOnhShoT/DFjhqQ/xulDF'
        b'CONDnyscWcxquLCzT+1g/4qoAMGHr/2S+mXTeMEtZkGstWnpqMrKPRmpuxbMuTrN/NbGdxddyHpRtujjdz7bfb6/RLJA/J2+3+ZVfwGfSZf5+c5YYYj+pPzGp9E+lw5M'
        b'Op0aJGlsdFyOTdr5cmb97euVXu/8j+8/twUqBQsUXoQQwTpQPRVpGEHz3GqLEh4l7lN4vXc6qEnBNHF+pRo0KcNoygfWsQZ4RkDUouVIwToKa+IKwPEuNFEEnueXY+yG'
        b'uwJBTSS4BfYi7ZKmuEgaXJjmz3s3aqWwGe98hI+QAHWRSKGEjaAFKZVYo4yCh4Tj02IJmKNgFdI9ExNgA9aTsJaE1LuzhHDLwZZQt2oF9oFTvHoFrwbyMXU1drVbgxoD'
        b'KogSFQ0reR3reXic68BMwPVixE/GB/16evbNJniY6UKazuHX+BMpIf7PMLpsYCf66VTY6Q/Z2SMVm3e5yfc4uhzvhnw/eAz5PqF5BdsmzCuyWI36Ni9EHFYTVhTahLzC'
        b'0GWdVUcS51yrKNwkzpEQrSevr2KJgOU+nkZ38gTgv2f0emxFYbL00D54K9Qt+3ukbb4zPGXHofv4GS4OkaUz5XelbzdLcPadL5nK/0SFwxJtJmTDquJndBO35BED5SqJ'
        b'LXZcrEPMk6I7eM0Gq81sskyQa+eabQYtDl3id4vQK+XaWboCC5+mK0CJ+lKkDGGdzGT9TSyK1Rj/WfVHliyh+OrbbV9pn7vz5t37d9++e77+WsPhisMV42tad7dmNjW0'
        b'bhxZ07jx8ObB+9ZWDd6wViDeuzs4eF2wLLhaJQsKuhvlX5n+6mdrsvapqKRC77mh0xUsiUjtXQov8RxEnQouenAQ9OMqkdjZg5BZWAMcaZHtzEEBdpOw0mR4ZXFiUjyo'
        b'SkmG1UlqgOT6kXEkplUBagVItWot+PVU6qPT6zMNWcZsC1F/CZH6dSTSWEyiZQM6UUjHck7DR8hLUbx1sfkkvpzqKIA9T4LgPLIVufMSCm5Cl/PdUPCbj6Hgx8P3f06j'
        b's7uj0TTiTkNkauLxEgfseRCrhyPt/z9yxcXi01PkvAvMynvMiHGSYzTpCuR6Q4Gha5Th0xNq/chvGUKoNfbz7YSa+dpvIFVEqMFU0hzvcfveQ4SK5WBByRgnnfJEmpLA'
        b'C/qG8UT6ZoPrc4rFeJ7CTaSwWkJO50F6+i3YEJEA62BdZCKoc9MqIdSpYNPEJSJ/b/OvJ9RevG/2CbSaQmi1k5qn7lLUKU5Pd6JJ8xk3CZ5Dl7vdkODdx5DgE5t9whE6'
        b'tIPyOELn6bYjZ4kBzz3K6ob4CCYSKjHZCrMQwSHk83BttzuMs21mM5IZBaUeNv1vxcu3qvwZy2yU8MzA1/ApPS31hwk+juTxUZj+GIys88DIB9T9SGnNR61O0QF3IROt'
        b'qgNSYpQEl+INs5byit0O0DyS4ORhuMONl/HzyU7fxWXx2BBExqtTfJjBQSdWhgsRWl4TyUEr3ekYpW7RMLvIZrJ6vFNLd2i4QNwdGnYpqnGFYBb1KCZ4JwhByRZ0ebMb'
        b'lDzf87FBTwbh/wglsWVm6hEl2yO2nxod5WHhWNUzmuTLxqhjwrth20+HntfGS2iCntMvD+wGPZ8OOU9X7DNS99XS6h/7IPQkttEeWP1cO3Z6wT0u1SY2hcfOenC6CGNn'
        b'GmhyI2c6bCGb/kQzUv5cwHbdZtgIJ26OAw4huDBu/FPgph8e1SehZia/N1onvOhc0skgW3vGxgvocr8bbGx6DDY+qVVF386rxkWZmfqi7MzMNi7TZi5o88bXTNcsT5vU'
        b'vWLHqDfvxoX24wsOUTAfppy+5DZxsbmo2GC2lraJXc5YEuHRJnI6PNskHk5H7PwgJhTRwogcIJRHOsw7V37DBiYeHkx8ttVSPHA4jFjMcFKO9vgwYjrAGw0fzfwsZHv4'
        b'5vylKJdMRvv54H8fMZmNARfA8wnt68DhpWRkRSMrmKHCwFrdasHqQtB1QhpTfyzGErwAruOENL9CoK23cwWM89WRzaAfyWeuwHtVYpdrNl7eYjZh1c5DldMgK7XjqzRf'
        b'dA9DJ5fuTXT5iHEv7OdoG96HG1yGzflkYb8J3uT3ymhx9c0135IgEYHN8GKaDS/WN+TApscGZAcmeYRkdxOPfRYc68INpS4egqOBnAscqI7Hpbbvpvsrljp0CTbHjXX1'
        b'G8s0Cj4a82CslAqjdoVTlLxgYZFyMIlrXR0jpBDzkbcUSWXvBuUH36IKsEJYaJwseBB0LfeXmf0U1/JTM5sGncq/vnBd2B7NS+NiFtUp96ecnXi8bPSy6xNOzJsx89+L'
        b'vu/3S8jrY0PKSiN0c8Si/IA/DPgHAyfLYgLGXR25IeZ35cuSx4WuDus9MWzeiqmXuUz/48XNg7Iy3zNeFA2Zd0xrGJeQ/7rX3+InR3j3zVtoFqwZ8vmMZZIvLcuKw/q+'
        b'O7NJGux9ffUvyOYY1+88ReIlIjKgA9ZldXRqMwngIODD4TdNYsJ0DDmzWZaaOZaPRfLy9p92iML7tmgnTYjqxSf26RuYOoReiAOUFs9aHskvuAVrwRYa1iSr1Pg83LB4'
        b'cNK5dxzcnCiCW0BjKayaCXYIQimwfrgX0hWappHKtksF89+kyHnlBbdjJvItbJgqjPqUPypaGbNawW8Sm+pTkk1IZ1EEnZpiPDP5A8biQAnXT04PrbvhzY6UTVe88s+S'
        b'wHH9Fg2fqBcMTr4+PeFGVT+DdOVbL1+d9cJQQVojCOx9Y2LJ6Cnb4h3fHTq4MCz1lTeLZx9NuLwnJvxYIpi4b7Pvg7Yvvnpjx7AvGlLfvVp89PSLP3wd89MzoiSfFZG/'
        b'L3on7xPpsxs/nHy0auV7r1//V0L/h7WvpLzwzqDTm4ZvzUlQcLx/e5sAnOfgrQ4+bKYIPA+aiDUtBw54rvOJ5LABNrmiowo0RLIVLPONUOEzXfEICsAG0EJJ4XUGXgFX'
        b'iogxMBRu7GUOjIDV4djhhhf2jYfNxq5B9b91B1/P3QzMFl0HLzkJ02mXbSUcCTbEm2iLGT9ajpkpujc/76oGn3WOAxc8dK3fClYjbb7jZmG4ga+6EYY75T3HDslRTmHZ'
        b'uIhwDaj10Gr7gf0cWO8FTqP3c60LP+q4hVEXfuTewujX8KJuTzPqyoskLl60K09C4aX+fmOUAYeTUyWEF4XMF2FelDcrkZK9u/Bn+i7Pi5amTnoyL5qwZMBb4UeyflI+'
        b'Sl7t/Xk/7/Kb81rC1k8fnfBXTekzHw8Uhkj6v79wWsanU24M35c2dW7VgO3hNwc9Oy0yPm3FO76tRX+LaWO3hKcVj+p/fPTnM37QH5i3URqjvMbE9oqUds+L/FTz+K5I'
        b'Mljq4mi8GECbNLBsCE/07yT3plrm87xmaVoSP9VInrwUylGvzyE8ImlOrxI+8bxSRF0tJ2GSSSNHFFP8tN0eeAOfuY55HBPfzuXGCo0txxfSlgKU517hIdVrrd4Qr+E5'
        b'+dz5h73WX3z35YgWy1/DZy5W0FOevb93I/N+/UcfvvW3NfJl/55jeDh20uhxg+5fnTq5OfV6eeD0xOmvNx6OPv+gdMfl8LL7Y1fdGBCYbKmNUNacP/DDzhXgq9GPFrfa'
        b'fx6dP+BSzBQFTdxrdnAR7k3EwnRMPmEJSxgD3J7YQbf8zTseEerUG9qpc1hH6lyND47HFEmUHEKhMkKvZuCu6PZvgOCumwxxPT91Q4Ybet7JiMzIqG2giqfD+GQXGWo5'
        b'HWgAh+E+uL7LIkn8TzZonYvos1LA70tvpw9RmPoOM+UMuWf1HLpnrTR+PoOqp5fIFjPlXDnevV5QSVkZfK6C2VTmYxccYvWCw3S5YAFl6o/3jC9dyh9WRJ7gY4wEiygT'
        b'olfTHTs+KEdNasClW+ysuRrlEhzmDy0SkrMfQlA7wnJRJW0X4f3t9aI6lN8unESVbDWtImUFqOxDVPYlfNICgl6AoBSQ/fRxWXGXsmJU9g3TNFKWPx5I3aVk/55K1tMl'
        b'4kohnxulUHZ8okMYv5+/8+gfjZ3SewUjNuM8JlaiQYzaYCieZcYrS+c+EtisOapxZuxhQsgK8cvGD8h5MWa8E4hCZM7BSOhlMNkKDWZ83gNegtUmxDu26w1tsnkmI74h'
        b'+itf9hke19r3Bm2vluygT5Z/zcMXvE9xG730Vy7Ob5PhE1Yso/iVyr6s06bGe8zLnEc/8KeN4HNDJM6zRgI97mTObzE5T0TMn8QJb6ZZ+VPdx4TjnRPIzhHygeAGrOFg'
        b'K1hn6hJu4d42nZzDTlnEejqdwsdFkfFnKhinPkrG0Tze1Qe8ebKlB0vTm/Qs01qUWVBkyo1iXceQstiGseGpvFVh8wmUUrBOBTZF4qArHD+AlTBqONggKIXr4akup/u4'
        b'g9NiCKh6Op82y7Apomft+FwmWs8dovBpPwhwQSB1mLbTfSks7HAKQRyhsxskPIQJXUGWuj1g+P4IynKMBQUKpo02tdF5PfUNdwl3jfRxLO6bxPnaOHK8C7G2AhYlY5Md'
        b'Hx9dAdbjk79RD1PIexFSwwei/j3v94Tl0nS3y6X/g1MIac8mPBasti/3qwsspmQpv6OpYu2szUwcn5g8+wXqkE9vFkm1+MNzQ/jEj5Ft4dc3hGi+jtIplHH2y8+x5DCQ'
        b'tLhqvK8g3lfrUkVjxaXdf9ww+M9NDYc3Hq44XNsad7rCRmd7T5d8Ou2E5s/T1oZsFCR9XC0NrhbIjwxQDnh9tOz3tYok/1j/I0zYS+JRoRsWycIurxm/wTA4O4rNnUBN'
        b'CgtephiCdFgyWbwVbgUNEaqwseXO5dWMCpwEx4mPWjgc7uVP5HMex4dI4BoD95dz/O6E58FxsJ9sv1KVBDcraZTl9GhwhoHn4MEhvIp8BqyF18HpBPQmzylwECPSX1cx'
        b'QyRgz69fpd2rsEg/fix/oEWm3phrtHbe29i565aY0DWm5xDafM9dieNpmqt0NUcKxrKuzU/XeHzAY1Zfh+NBvQKrfFCP61JAawzZ9xkfNAQ2zTGmuEZqHDgpXOWV2zMn'
        b'wZozzz+wzDtME2xkNG0CnSXbaESq8UuUSzAP7ThMojzDigJjTmkChp3EhrD8Cd9VYybCGrJLHYICnOaQlbFBD28w6AUd6d8zJLgsPseFSMMAfPoRhqfcCR1hCYzG/BZF'
        b'FPYZLqget2Wal83khDGlna9hNYVo7KtGgdYIWNcR1N5zwQ64hYX7haN/1ZjlumAzv93TeHlljYnhD+ya7zFi2DAbCvaOSxwVHe+273wHB8Bj7ESE35f/g/HKc8P056ca'
        b'LQQfL2Kf7TRa/P6aWbAFA4lVThJJC895ZbIj50/uEpXnPn8OH72tpxGrx3oUZQ6zYkHAVjBIu6DKWf50KjuD2D5TIrYzxaPsND4pit8GVtM2LGrkqOiY0WPGjhv/zLTp'
        b'M2bOmh0Xn5CYlKxJSZ2Tlj533vwFCxdl8EIBs3Fed6CRmmBchghYwbUJ+bmSNkF2ns5saRPirUGix/AagVfnvkeP4d9NFu47OYKZ5f14eJcfMgKDQNO8xFFj2q1w375w'
        b'h4SdoJzZ8zuSOTFFTztlM3oj77maRpzpg27xJHoM/x4KOuEJqIdr4QkMQ/tLOGaBVWxUVG7P21+SU7tp96ndCJ6n3vKyi2+Loro7u4Xjw84ngQp42bXsG+6Yl+wFr8GG'
        b'OfASaElDl0tpeN0nFQavcoXPlRurtvyOsWCNTfQv+ivtQiSFdHQ2kjUvaYVvxFAjsuF7XMxbYc4NDGBz4gp8tPMmWBMporwGwrPReLXoAXiGsP+hoLm8w3JOX7ARr+ZU'
        b'wNM9nbtttBRlWo2FBotVV8jvyEFODfLk78vNn7gLrad68tWTTCXd8u8tjzl6m5wLtgkegdvwLmabkE61H66PJPCr1MjMRAM63CxYDW8qZnUJvOvoymSdgXcejkz0uqX/'
        b'GyGwWH3w7fK6e/EhsOmwtk8iksmbYG0J3MdRwhBGoptOVA6qXyClpNbIWbnWPmeVD388NzgINwXmw7XRiO+OiqKGUCINDfZmwRriS+RAzcoyUIMeXh4FLnHoKdhJg8vw'
        b'JFhLomqn5SEFeRtZVnmIUlNqeHsgaWr+9CAqijrlz2m1kz70d653fGQIo1KpXQtR4rQVAzmK7BUYJoTPgwsMJU3CexMuBrdI1rN2vFdgi4XWapXzgor48pLe+PCL+0OZ'
        b'WG3BsMQIhD82bHMrwTV4NQecS4wHZ5RCiutPg/MRYAMpMjU8Fr3xejlTrDWv0Uzm61k7cAoi/l1TJFFa/7tDp/CJIB5vRBiXjgZHeWX2KspYH65lLZgTTLzxwszUuwkv'
        b'xMqSR721e8z8Pyzx2zzwRd9vIydVfjRS+ck03z/VbL02TvxuxScjLq5e+qo64uPJTGRk5Av/utTnqii/1js8eedL0WL11VzpW3Wta97sW6j9Q/Y3IQn1V+tPv5tR88uj'
        b'pHvKhY1ZdOJLfTYsi5ncL7B/c50k/PWPP0vYuvncDx9l+H1c8aeTqz66G1n9beDqv/8k0akEf3gw/3fpYXOnVW1MuOf1jvYN8w917M2Y41ueG2Be9ULjez+EGu/JJ90R'
        b'JvxZOOBU6V+93jr07pXM9+8Onnj36MnVEzZbpV8VXf/boEM3p73yqE4h5Heb2wNvx8JzI9wsDDsuslP4Vd37wBW41qUJDoTbXWcz/7/2vgQ8iiprtLZe0+msZGEJARLI'
        b'zi6yI0tICCQICAJqT5LqhJBOJ1R3WGLHDbG72QVkExFcAXVcQBBF/afKdfRX543j0s6o8+uojPsy6qCj75xzqzodkqDOP+9/873vkY/qulW37nruueecexb1wDJGRR7x'
        b'mXQ7cu3URJ6FgJ6q3kvaxeO1G/y+5k5Ky6iyfNVMZtZ5/yXaI9phbWs3dh6w/x8jv4Hna+uqK8hiXMgbtZyfXL7mF/iJ/xdIReNbYKNyuwA3nX/esOGElcadjZUul3gm'
        b'G4WtSXTwfTHGpSDxA3mBeMtkPoOesTiXyjtGBbrDlIi9rlmpdbsojGKH6PSfceQvKO9yXKxrFayrtVtEuOkcwlMU/Garx5IKy4oKJPVG0khHhHhi2MhhEpfDS+oNF2m7'
        b'yE1KgbtmvnYPBn8cwA1QN7bXGkaY+K+TKtQyDmkjjJ8ZBj4MQx6GkOk0BSSlKGCC/xLsyqYMLhVypUOegHCAJ91l/YQ8JMqi8d1akQVGhlyiUhOSDsDzgHhQgJIZtSxV'
        b'duF+o8E8kUij2LapjLcNQIHpFF2xx8i2RKD0sNfgcdpeUWeK27JrPM3AojC9pO6C8TKaSIyYWlta3IqCx5QRiRhnc0Tyu1f7gdjAInwNbe6IzedGdSk/xppd1SD7lynv'
        b'YX5RdneNtAvN+wDv34+CriO2LdtEQ0FWtOqyD4nP+lES0eEiMd3anegUpgIjhVchy1JFXi/nAMfSX9ufO1jSjjXO7kJYRkcVpxcJSyJ/OSB/M0hMh7GqYboP4DjDViWL'
        b'OM4kxBOUGphiQZYghxgQMdo3hjRtF3EqqYQl8JRibeN7yA37o2zS5RBn8iZcMnl1k6ekcDIRiQ3e+olLBw65NG/pZXAtzMf7koLJl0yeROT2aWwsk2c9wREriNxKxOxz'
        b'Vyu1yyKmeqW5tSViQmES/HiaV8HUPEVLNCJCLRFLC2qZKd6ICYYSPrAalZ6Lek9Er5fwtcvIfEA0vC6JkuG4gYKTMtwhMRZyinr3YPIgqd6LPnfUcBUjb8nNpwXQ46Pn'
        b'55vVXeqeCZ2okE5nnDtoNoB4F1I5JOYZA6L40R5IycHrAf4g5ysJCDIQ+wHOhZZCgjIJr/RmegDYAxf8n85dmtxOTA2UJqbDvPDcijLK7Ynm3sxye3sHeGUzvQud/U73'
        b'1y5VRnj7GSE7myYDRo/A9XNaBf7qBg+sDMntcTfBJLhXuj3nWHgRR4vi9qNdK47xfR1D69DDCidS7Fd2XJXKkJq2Vd1aUpg3qzifeEt1IxtiHlDXLfVlprwrRvVsVI7B'
        b'tjvO8AEjcUtEt0QhHWFol5h2iMvNyy1LrPDMJJvpmcVtWW6TLUYKSEILYDM0KbcuscsDMTwkpONkx7W2JXHyID0dLzsh7dDDR0oUVjJBToRv4js9S5KT4Zkz+kSSU+RU'
        b'eJLQKVcvOQ2eJZIpObckSc4JisB3oLG4bUmynEupLLk/pFLkwfCNGVqQLQ+AdCqFAOlFROiQSNwMmBW31z8VOLZOcGdIFucbuLVDVE9hijlZMu71IMMRvp1m//SP8O8M'
        b'Pw5YAdQZOqxH/psbneaYpeSipUmx0X0t1bXuJ6N8mNDWN6ZpJWdn7JYRpLYic4EsOkCqIWThKwHWRB5RrL+6vjsTuYitxVPd4HXB62djmtArtgnRHF3qFoy6kzlmm9fs'
        b'NNaiXv9hIWJy4TZAa6JbIz1cMS91sKFtibF146ddpidarYOmB5e7bJgFHuYVC4bqE/jua/pDRy+7MD1RgbInOu2E7nkmRKZzizI8r2ERgwOiLDQKyigZ5QzCBIwEDKtn'
        b'JedLk00BEX8B4fN4IgNPLOyrNM7IK/MYPfsgkzpZK8/wQyN8wRmhZChMGXkaxpWq8Dh5/OVnTJcXtOf6cJ9lYdftwFQqft+qBthDcc81bLjIhz4imQjf0pPI2gWIBrZh'
        b'N7nnf100tL50WzGMhtRbSObbMjuBYew3lZ38j4qxI5dlACGNnJ+dGwgUJxwWjQGUopKE/TL5WoFmQHLBKxt6jdiBiD0K7j2cKSgp8P1fRJ1lxKZ3Bhss8b/RyPqORirJ'
        b'2FILFljt8SipfI+EUxq8Ot2pSSlnNwlK6BbXUKswklEIQCkkIbURIsBeDiC4SaA28kYbMQh6wBCiHuYjJq+vqboFmpsRba6ZxV/QY49GLG7Wjp+lO61kQgkfi7rBLcei'
        b'0/NtybF9YcX3PMDDWFeEaFeEaFeE2K7gcENnonKrdJ720JiONKAzJ3++DhyT8dKb/5la4EofyPll554kn9UTVn6XSYkKoDCuSQhaGhKhJwUGTlCykRRhIczboTdIDuJK'
        b'9gs6KInRlS3Cyp7CiANJScCO4ckj612cywUkVYPf3eRyGbtFBffTfi+VfvD136NnTURuIdHVlt5pyXYU3vNMXRYLdCXn6h+bK29BdF5L9XmFrZDmVdTnVTLy6udOUqXS'
        b'lzeo1XQ2eTQQ6Jo0Zq5hNHxGg40Jj3rW/HkT3l/3AcwEbfq4OAU7eSHoPDbRqn4iRKwh5V7AquluC7W6XDXNzR6Xyy517KCpnatjGYhYX9BpNgymAwVUZMdLEem5OiR2'
        b'eSRn98E+o0d4R2gqhaH5mouSi2sAMTd4/ZEEpMtld62nmmmmoom+v5kdJht7A36mDMTxpgPss2TCZsWNkZmcUhSsHLzwowT/O68Ylq20204QSGVHOyET2MjCJok4Ip4p'
        b'ORhUk1Q7fJQXbQVZmKeIzb261tPqa1jpjsTjvuYC/hJr9X2JjcyGDnp9EwcOJL4UMNsgwsuwK3lgmzC6OAR7l4eXL7t2UcmFF8lSDD4QfjQLnTcObFMnbIBDEWVDXoBL'
        b'A4cnDcj3AzVwGesYbSQSwD9w7gfxnJzP5C4R2k3t5oApIKzkgKfHtWLKxGBQgm8eu6/n8XeC/gZwhhlR+wpHwMyewx23XEJtDagpC8qztFuhZnPAArVZAlYc2oAlnYOc'
        b'KyGnpd0WsCnHA7zvEDCjDwRs8F6cwHmlgA1pFp8aEHyqTK1fDt82MMiW9CNwXKJnTIOQ3sq3RRywNoCRbPDIMN0Ri7/ZJTfU+kkJgvYH2GH8AFs1ERtmxIXkIzqTsT8m'
        b'nuQ9tPfYa5u9PmZlGOFlPCiBQiN8rSJhMUKtzFznEZH8Ptfj5loMudMlQ/BDURXs5NyXRUiw88m0ys2kLmSnmArSWRuw3glyHYF0Ma3FfKG0NJ8vzU87WwGZevOQ0Rvl'
        b'B6N9RF0io438M6MQkBah3Z+GhnYdwtCEjpRsvOTwOvhRR2KCmf1s2V9MbDNsiyrqiktW0SoJvF1CN2l2Cdhv0elIlBKlVHOqOdmSardKTslpolPTcerDGLN6U7m2aY62'
        b'qXDFrKJKE5c5RVqzpFQNjl+Qz3Qx1I2NVYVZ2uEOoyyNgs7iJ/lmboRsXpDL57PzqkH2sRXR8ngu7oqAtk7Q7pqjBbucFSGKIC2o5Ch6aAAyJorZmEOPpupGt06sKP27'
        b'QVIWfULP68C0dGwlSFrYF9MSu7o/Xz0kaBumqse6PV3Cf74FXAwLnEixIlGZHRheYC0lYF555jttiYlZPNaJOrNrRg9qkMciO+R4+LXKTjnhWvTAxhZVUsQxvbWpaY3e'
        b'2u7p5ej5JeNgYO/lY9hMvoPNZOIGuIokepD0fdVUqfzIGfsq7lrELMBGiSuLOFAGuu/TwLmQevdGKSlafWb27Gw2Ce0gJnWgSTOfBf/besX26Jd5zWEOapSxfA8bqA0I'
        b'FdaU6dF55dvSOlUYzdIzraafhBIVonuqMUKmUJ9ndwNQjARDZOZyzYypPOOs3kYz9Vz9JJpKmQeW0IGKaUQ2ArpXckI0EMiXY8NgogWUAiojcCI7NViMQcYwUzSRNGpE'
        b'L2Xx5zxdJ5wzq4P6sZIwzkmiuO7684vIH9auHkkgi8vlcXtdrvkxQ5h6VpWUoWcRAnbGz9UzvYJ6hg8k3F16ornwncu1MKbGLiBKOX5GD1G1orTH3hEKX3yOehhxh022'
        b'n72N4FpSxuPsTYxuC5PwMiW6N/xEVD7lfMg03phWq2g3W0WHmGgDxC8SwpbLtEd8GPd9k3qPPwYHZqknc9TtkrZLW6/e0zMSxJ3XQII7xOXicmmJyc00zFDKJ7ml5RYg'
        b'3PQUnfIjgrQusTK5HCBFhiRtJF+z03q3RpKrapa7a/3kRFAfqV8oPsI9QTH3gDMIq9VG50RsS+9a3y8THhG6sJ5LdLSsY9P52Uio3kBCygS+K0GKMOGJAaysbjpxLtwT'
        b'NVpEgGtL9nM6C0YE6SLolQQs6ZpRTD2YsJAYoFOJtYKZW8zem9Z4dfVh/oCZmL9fQR5LBwN4kGd5jV6xVIz6Rgd7B+RMsgHmEXs5MAqrmQotYTJcBhHnBUQ4tvp15doO'
        b'lvjnoLdmKSqtEoCXdwAJiIRg2jmGTmco485emRdEyVVLlNQb3XmhdpBpXZrVQY1hOZdGl2cMHeYQmQbdTSPUI9rRKm39rDklqDO3YXaOtmvOipiVOlW90zKopq3nNdo7'
        b'Zo0SWUIniECq6AbdkT5G7w2sNA19nc5ubm5sbel0hGnSIScluuz0HSsEs6kTFoDte0cRk4mR8ZJ/TYtb2Ye3tqhwrtsd1eyhWtulqCTMyrcNPEf7StgH3RgBzowuxLPW'
        b'zXR40WasG0CDqIasrc1u7hhm7Zai2epdHehwhba5vKhEO45KuNqWkmK0AF9h1/Y6tM1dTp2iwhE8GIddnCNxR19aWzxj/gJ4igdjpxSFkP3jQmbka0Mc3Zs6ZIgCO5cT'
        b'L54zG2AIedJIXHMHoBJL/kujuJVB56+ToipkzMsXnXqSCsyxSeoxdYN2n/YgLGrt/hmTOO0BbbN6oAt0mQ3ouiwGuuSOMxlznYlOg2xLRFIAMgOmx5MgK+wCEp39iLJF'
        b'tiJ5LNtkO5C/5pgTIOsSC+0HVoJQZ8ShT/wcoPCVytIuLkaig34bhzpADTCYMr9PBK7akE7lAA3MN6CuH3DOJIVHqllQQlGJ1KSAoL8BAiuTA8pZQg44IPq8eEdpKRNK'
        b'R54b+sLkW0JAmI6H5yb4zmTkIf5bMWSVy4U65FYk5FZ4Q5HJjCLiUgRRkmGdhxeikjqesTPBiN1FIloXCpAJPyJVkK+7f6GMvUgA1qK46xpWu1CJkAwNIoLX9/MEX1jg'
        b'DZJhRQMoCP7+YTYhbKCfbIn8ZeMJeaIeYjB6wkPz0UHOx64FCxej7oDuZ+phSm7BARZQ/MFDGlUsYfCuY8IPPOX2jSCBiESijAy/EJDwJJx4K06WNuFQLzREIwckNGRR'
        b'/PQFgBabEFhx5rUw0VRCKTy3AH7aiHnYG/05rTs0VFkrsCcrMgIMHVoBlURM8/GAJCLO8MoRqRIDoZsWVntau56fRekBdn6GohtZWGmozDP1BkGpwlm6MIoV+e5UPMnd'
        b'5HE8mCfVieLOI1zb7F3pVvwkg/DFalIwX6BQJAk7O0SlhcTNoYgLY+W5dbmLjwL+MUkM7p2APQhBiz73ioipWZHdCoryfK0eP5HPTR3ylXOd7Ts7t++IZNhLUqAGFKfY'
        b'BTsvCGhUbv7BKdqFvmiTZceY9OfoZ5cjtqiUsJTgCRcrQMR57SJQF6QOQ2ZORQhhJHYWD7L5tgZEmV/JK1bUscCn9EzQVbaRfEdJItB7bphvq6vOg/oNXhozQzaI5lfK'
        b'Qrws+glKYwm8f7aDkWJubJNJ2+nsdaNX1O0eQlCFSvgxxl5wDWA/MgKkDHsAqSzxIKorwzsmTl+JKwLvRLgr8wM6CghpsPNcw5MOAqCtgzxRcrBWYGXIKNLzJhpPMA8e'
        b'MMomdgdPYEzTGDybK9mBouByEYydSbvI2+htXuXNju7p2QNzfQPPmC/P9eF5o1kpwAFzEugxLKZUEPvC6WSbIVAgKJvTlXKOxLu8qLCDjqyhgP+Fw0q+gnnmIThRl9Kn'
        b'8WYhkW/r3Xl4Yz/tgpuiIqU6LvY8j+AG92fcqQV218C1S0wnRzdaQ/yDX5AhXcAckAjhF/gldoCzHDYDFM/ews+LIn5DTGVWXLwOJMrFeKG1SEcYwJWih3ggNy0xYhar'
        b'IUhVSjBpY6JT6FHM0uxe6vkryP92B8kLIyWibJONWRcUrlctVsJisHXLiF4cbTh14VedidyfRYd0EL6z4OvrjdMCq5TWK7E/cKVOUkxRr9dOaSc7JHLa/XO0jejTKSt9'
        b'2AJJfaSfp1tX4/iPIuhGyZEEYjgNMoTFAjCIEHxzNgGCxLFOfpDiCcrmmAwjMWKd3VzbWNrgcVcqSPl2IkE6Hf/P4piIkvFRvlS/IPO0/hi3KNA7OuJLQ7EcQBZcTSSc'
        b'M5OgzoIWaC5r9ADsTArGB86Wm926F3/0b3bGkusrQY02nC069jY3+DAfLa6IpbrGh4ftEStpvckNSsSC2uTNrf6IydVE8Wwo7HDE4sIcbjlWByAiYQ6loRumEyHhiw6g'
        b'chCNkEx0gplvSzIGqXsRH+I2OxejlcVUIFG2hbZ1bYkhXHOAixBDL+K8NWSgehUPOIrn2mYFYGUBvyEq467Bb8xK5SLgJhGDXUEaVXppfKOk1PgtsoCjDs+ssl6ekXeF'
        b'k/0OQz5UYuM+n8On+unS6SRCb7XNrR6Zhry6liIJZONQvb93D/47PHlBvg04GxhUGqiIqakRhllZRidLVfOJQY2Y3IoCaMiDDx3zWr2YXX/j87jdLToCjFhg56GilvW4'
        b'niMS1v69ZFh68U7YTxNJRCdQNBOcC9RjbYuPzgJ+0bPxRxHHBCfKYJlgEyCTN8ZfGQxzIRlzEeXtSoGixM4wMDE1+KJdNilNeE/SlrOZulYvNiTeFCMVxga3JUQbynL8'
        b'FHnFCMeowAWonst7kgqjNx83ILQUU4eAJDEGOullz0NTEFMfgqcuhhWYGJak6TA0URtiHvnP1diW5cbgKI3Rpp1tP+NyAd5F4WKaKXpcaiUSGyYvOaaRerYu2rv4fxGn'
        b'E+w0g2mG6AuHh2kw4mFi7GCJ1KKIqdbTDPQgDpyh4SG53Ktru5GRAqKBFdwvdtrsZ69ylge5fsSKPewcNDI0VQG8tOPlqp8jvcSef2Jwq1bJaXcmOVCCaWHejddqN5Sh'
        b'G6IqbfNKCiWunlJPmbj45aI9S93TZZOw6L9kWxqViKBetQTcaFQqgjqMSyQ5McjC4IhBc9BaZyY5pQ02iyTGv1IgGzzAscHGwXyX4TFOZ841OSKVzp1e2gUJRokPdP3g'
        b'53SyAbYIIBcExicaEwi/0LaQsFxCI2RKm2TBb2YpfcPgDG2RuLlrsMIR2StzfWfiIaHHFIekIV5jjqrQZ2dLdb074vC5/a4WpVlurQXi34FfuxbOmDe/vKoyEofvyAUs'
        b'IKw4l0sPu+1yMV1sF0ZdMUi4qG37ueYT687rAPo0UkkFRBCP1XbPR/YkddUl72eS5kNLspuqveTzEj2uIF4Id4A3851yNl2JPYv2YWgUSQhtydSUTq8rOzUIhWBR0em+'
        b'mPnD5Yc+xQMCE/QsF5TLQsDA4h2qbQMDKgLTChv/WqbkTfftIhD1YjqH6sT0FEiBA2am7EBkKK/sDAFBKZvWClt6AyEqHbAEBLahyQBIErdW5Dlv4nDOt3EYx4Sxi7mo'
        b'XpSZWVh+SVZDubnzZ8y9IPtLHAKmA7hacdfZiZqPCKtqdBCJmIFMaGn10yhGTHJrU4uPGbQi30WHgxHTKjy41wV8DOHRONMnQt2yn2/OrGyBT0aaDI1lMlc2o+YNUfbJ'
        b'JJzK49viaF5YwyK2MrdnpdvfUFutTMQiyMgSJ6bWkEvhPzQfiXqxQcQcIAIBiHye5gqJeNJehnkQ9ZVG4073wDgBYS/imxDvNwELaUrlUI8T/U6wdB+Wtsrmdptsabcz'
        b'EUN7HMBAHOl7ftGO+hiOTK49PmBTnjDyBeJhhq2wye6Wbe3x3ixK2yF9XI6Dt0bdVqx7RUvntgQcASBRM7hGTvkjli070rlMruVNKMkZcG7llQlyfMC5kse7gJPVA/dZ'
        b'AQdcsWyLjlWgTNkZsGCZsthug1Y4WSvoS3iPetasTnyPeh+yJWAKxAfsQCjYluM1brlDTtpkhvLsSgvmgtaaGearPI32FadxDhacxhl/P5j2+gvfzP/b5FISi5wRJ06c'
        b'SBMXEV2AUfgFjKnksyP81IhlWnOr0gAIiS/PFyImr3uVazX7WZMfzzTk7aTL6mnwun0MUTVVK/UNXl8kBRPVrf5mQnCuGsBfjRErPqxr9gL5qzS3emV2dHAtQqtU6/Z4'
        b'ItLFc5t9EWn2jNIFEWkx3VfOuHhBfgKDcDoHl6gAiaxRTD7/GiCf47ABrmXuhvplUDRrjR0zuDzQHLd+D6wvVGFS3NCKiLmGCVps3tYmF33BdG4lvIen7tV+evyTAazj'
        b'mCYlaUhfYNLNLTk9SKaDNC8TyZLCqrPLki7LI9ss9Agi9CWZHguQyRYdLjfHj2ixBTt9Ii26mGq6FcnQTraa67y+6DCoLx1XIxs0SxbCHBoX+UVis3CXtaL4Zq3uYCMT'
        b'TTN42Rzg05jWoCRbEMv5TboU1dyJqRZ1aaqVtgHbmd5TqxU0Sc4e2Vw3Nhs1wLLJP4KvtUmxwyyfKfw51trFJdk5QwtzuxBcUR0uRFFkLuVsh74woUEnQynYe1DP1DCV'
        b'GtkNC4VkdzOUyAR9/WmIsekjx3ZnInW6EFeFVJDrK6B1Uwmc9l84XX6Hpjcy6XFHROhpxElQ3gCcfG2zp1nRsTkr3GDw6NSqY7eO9cfEK29GW/kf8GmDyRBjoRslMuLD'
        b'4wIdF+vFEu27nc6+DFSs7OB7pAU38DrKVx7i9WpipAi/0B9ThzzhaignxxSVJyRarFKGMzWPBdh+TLttni+uZYXICdpeWbuPHzAoEXXXokQBKXWJlZWVqM0ltiIpK2rr'
        b'iuarB70cM+Y7pt2Bb1ng82kCwf7c1MDsu+WZMG6lDf/1u1Mm33qg7cyPN89Z8PdFKfWpNz0r78n56Lus1BWH4+66av3wwQ/YeieKHzdUvfrhxfMbmyruaRryccKzYz/9'
        b'i+UHy/dVj7719KpIlnPXnm8+eeNTztU83Zbj35mxbM/ulwfVzGp84tjCUOalA697eM7zy2/Y/fuxNZc1J48/VvbRy71qdn2S9MjfJt0/8/3wow9P++j3bzxxxZ+ynR8M'
        b'XzH33pTgV1krLj4RGrRk4Oa/LtmxeuzbLZH92xav+e03wzeeUL+2vnXHt+dd/ezC1z6rSZifd+zUHW999vcJm+K+Hpt0+bubnpme+vbAuiXVv2/e0mfpu+8k13383bWb'
        b't48cknu4tPySp3o19sv+MPljy8ZT6xufesVa0//Kra8XP/pATuE8efbiggeGXHT42QtfDn/40O9+O+LhXc9Pvn3D3ZZ3F9yWdvuKlBN331v4dc3Nk7a/s3lT/+rrbGM3'
        b'K7u1U4enL7ziue3Hnr9vbe7i7QMyd4kv3PikkLZ0QFrrHZnHfr8zZcnC/FnVtue+Kv7QdGbqn+69vH6St/HbAX++fNuAO4u2yEuznrtix2/sC08+OWn1xwfPf+nUwo+r'
        b'Nj3e657HZrUcbbyT/6Hmkp3XvypfcEa+KmXX6xXr1qx8/ctv//7Hj071X9Xy6uyni3Pf+dVzLz/yzEMTTrQuesW98flpL6xK+PCjlkf3vH3tYk1rT12atX5IuG7KUnNC'
        b'5NTtj5bd+dUzp974fNgjb/6l/Yu8Px9846Xd77TeV7ql9uNnSlYtKP3Lvt+XvX7pjRuKTy79w/nfDfI81PdPr0zOK733xteUV7Iai5/LueeN11a8Ul2gHjr8TNH4j3I3'
        b'Pf3agw+XLf3houXLE6r6Xv5SZNL9R+yfpV5Uf/Oxrwvf/eSd/3h93D0fP/DOJO3g0VUZ4/ffWnfs+XGZzxWO+Nr6tFd9qSBw/U1XrH/RM2bxXycfX3/Z1ievHP3wgBdP'
        b'/vji5+tOzhtUP3LMB69vr7/777mPKa8+98imG961fex6p8+rFY9v+vbGpFvv/lvxY+PfPzGz9uZXK8uyn/uxPf5C69umof+YuuvDqx/1/MedOQNPTfjbG6bifbd/u/8V'
        b'7q2bz/QPvPVyUcuvFx16496h1UfP3HH5ys/Fy0a+2nhX77fWKA+Uv7hl9bQX+/zp7vpRywaffnHxlZtPXqEuPfPmA5XLxi3zf3/v2oabJlU82W/Oi6+ct/0f2g/fjf3N'
        b'4BuWbG048m799/+1subT2jtnL+l30cZPnv2215C7W2458dfF86/+w/bNDY89MO3rb/q8ef3nL/hfmHDpCzfecvx9+YbfT3z3qePuLXv/0e/TZwP33vW3fc89+eOJcU8+'
        b'Pv8z56OeDwflX3D/H2+7Mz+OQsUMq9OuQSed5erGoWVFWpjjktXr1Hu1A6J6TL16Hplmj1GD2RRfsLK4AA2zHxzqFNSd6uZqcgierR6a3jmUNsbRHpguqvcljaQcfYq1'
        b'Xd3oRk7WtpZOYAHBF/eez85VbWVFBSjLTFAf1x63ia556nb/CMiwRj1kg+rJwFEvB+/x4FndzPxZsaPnwLjk3nbpEm2zH7eDNvWai2JqLp9TUaRtyu96YH1lhbb1UjsX'
        b'mOHH/WQicM3HOqsVtC3sqlUAfT3lR0+nw9XHJV8JBRDa0nqOY/FV2t4JmTb1uHaskaJ5abs8jm7luOotoyX1EY96HcUhdAxvjaLn1nR+wGXqTqC7ftFOcM5L/ph/YWH/'
        b'r1zyB7C9+t/9YkijPM3Vsh4uEskartpM9vq/4O89qZ/T5kSFZ5H9T7YBDWwR+NRkuE8R+Ly5At87Dc+/BxbmjO+b4TRlTJEEgc/gz/MI/OBWyGWV6Hw8JxGv2XTt2x+v'
        b'ySa6QmkZNrxLFPGaajr73mE1nuD/gX0xleag9066QpmDmx1Iqf8oQQ5sb8YAgc+CnBkWoM2prCyqY/BSvPYehdeCSuU30QO0a/8/0Pdw6SDDcbR+xel2M9wtq8/tPvdy'
        b'Najdpm5grgWrZqthdYuFc2aK6l71QL8EbVfDmD37ON8QAM/04duKtz3rfWNY4nXl5TtPPf3dJ09sThl/4zueWQ9nnXE8+vWCxJKCDbtGfVz+wkHnZz5v+7Xfxrd9cOtX'
        b'V4+rEfnvJ72wrHTa1JvXbUuanLp37rObbvPdoRWNvLTu6tPDg887jj771Z4xg78v2D065Yrykze/MrPBbVuVN+CShwvmvn5n0V8u2iykHPrectDe+ptJo35T+ut1tuT7'
        b'lcf/cTx16Fe7q9V+//nZI7Nrj+x+b8HvpMJPf9hScOFneQvKw6/dvm7x9P0FresK7t333eMJmQ8evX7y7f95prHhi/DGbytGHd3pfqP6vQ9e/uTLU/2Hxb389oNlllM7'
        b'P3jlvd/ue27xO5tfPrqw+kbl01mX/GH0tnmvLbvp1stf6e2Z+cpez5BXlnhqG5sm3X/rkbrP/3jhmwtL/9T/mi8ikfDRpMYxKy66p/CZB33ffPDaA1WLnm+b8NK0Ix9e'
        b'WvDXieN2nH62z+dlWw4deXrB777zF//41lPXlhQnHHKvKRv0XP5Ni1841LhmenvdyEmvDNlx/4PFX8//4rIz++6ZuP/VDe9NONn88b7i506uPPVSes5XuWO//lNl4PZ7'
        b'Gxa99dIlwZf//N3umSeOPKJcOfabm3ccOPnxqhMv5Ox5f9HSAaYvH1xxYtvgui++L/1b1pvekynfjf/D+6v/uuGDiZdOmaJe/dyP1wcdAemZgcEJ9rxbNvZbMHdGfOuo'
        b'l6bHNflfmpHQ7hj2RMnXw9SM73a/zQV311w3qO870p3na33fv/htYddD6mhv4n+tXHOnefm3Oy79Lvz4n/P7t+dOWv/HL/r/+b3XXn2pIX8SuX25RNur3a3D1UZtQ5EO'
        b'WPNEYfhw7R7tRiJhZmdmYRagBsao+4kgwExJ6ilR3a5uHUEkTJF6U1ZH7EppLK/dnKPeXwg7LHm1CTdopwrVXxeZZ6snYJu9mv+VdqP6IAuFt1U7tqqworgAPSVpWygm'
        b'3cYKbQM6vN/IDZhvSl6obWeRjferDwlnO/IWtIfUR3RH3toD6klyiQjPgtrdFZBV25iPmQvNXMIYUTt5YeMCdS016WIggLZrG4aWaZugvWX8Ku0e9eiIXHL0rW1XDw2p'
        b'0DbnCeqeqZzg5ScBDXQ7ixp4uB5d8EAL27UjVSbOPEVwlmex8J0H1F3AqCEdl5egHivmOfNqYbhX20tvtaBQUIEv88uLBe3BIZxVfVxQg1P8FEP50n7qWqASizj1Vu0U'
        b'JwT4ya3aXVRhfoEaVO/S1sOre5s4QT3KLxihhsndT5b6yEjyMKXer96ibWQuprRj86hE7ei4GeS7j7Or13BCO1+qPb6MSmzV7gP6c0NVCa/+Wn0MilzPz8xNpRGuU2+E'
        b'PtyFfhjyC8q0nRXq7ertMC9AoiFVljvKNL1oKQHOMPU67Xgc0KsVxfbiXnnaevVejD3aW31UUveatC3MM+XWfPUB8t8FY1JSDsAA4wa0afoyacTUKmpmPfT7MEzDLH7V'
        b'CmjKbr5U3RFPE6Su19aptxZqoaGWqfPg1SF+kXoKYIbgab96NUzJBqDsxInqXk64kp+ibRjOvCSd0nZeWKFtKUavpVUwU/lmLk69WtBuv2QZeUMboT6co26oqipW99jK'
        b'cSrnmLjk8aJ610jmT35xRW4FiwFbVUlfO68Q+2m3TVcPVxgNuy0dmmzm+Pmc9rB2ULtV3aqGWMP2LFpseFmTKvlL1Pvgb38tC+xzn7pDDWsb1MPMz4VUw8M8HFcf0+5S'
        b'j9PMlMEw7q8ozp81RL0PCjDPF9LUh3NZrw6oB9VNFQUTyxCmywGGoFO7Be2QdqwvC0nZboU5BYoamn4/UdXorzFZXStqVy0B4MUW4IpKrigvKi/Wm+jU1osDtOOV0P6d'
        b'DGoOtmsbKihSrCTx49WQenO/S9m3D5U7WM+0266cAwOfXw7Fa9tF9eFZ57H+XZ+iHi4sV+/Jyx86q4jjErRbRXXjKPUqbYe2jUq/QLvLUlFYVg4LrjevPqSdUA8OLmdr'
        b'J6RuXqxtQBwA7I10Id8yWn0EkNFtRKDnTncVzjJxfAU3HkZrt3aL9jDNVJ56dCnC+HXNCGLooxJGJSBo+y60Un1iXQ1GrsUAl1Ii79Q2qntXD2ORya8bqW2rAEZp9Ege'
        b'wwxzFm2bYNYe0XZRwYBIjqjr0Z1j9eUxXifF8f4xLAjOSVHdgK/V8IQYh4/i8DXqVhqLUVnqlgpyWcw8wEmcUz0gAtuzY9q4EpqvOO3avtD2RvVEZ0+gAkDUBu1B5pRr'
        b'R0A7zHxwLoS1GuuGU9RumlXlR7N7bd+YAYhXimGlFMAEwVrdBqhktrZ5vg0+2FhRrB6RuDnqXRbt6hkLWbn71d2D45AbbcEv1d2AKxGiUrV9onaHm8WRHzVaXRenbR5a'
        b'PKuylU43tQeR9ChP026DrKOXmssvVjfQaFkuU2/GHPHqzsKSsjklPPTjFkE7ATwsG+zgTHUfoIHx5ZXEsuF6PCpoR+vGEZZYCj2+v1DbPBuW3H3OiqL8YpjrlCwR0PN9'
        b'6j5i5GYAqKyrqCoux8EIlxfNGgr1mLkizjRLe0jbc7m2nrLVaXeV6ZvZpqp8bZO6TjtRrm7C3SotVxK1HYyhjmuYiLgBMM/uqirabSzQogdgMamPjqYmTVPX1QJ0QJtW'
        b'apvHjdRgLjfMtnCZ2lFpcQWDdkXbtwhapN1/gfowjEsVhp9J0mBLPKgFJ9KwVKg3q1fjuOBmxknFPCC6beo96nH1ZopL4WwQsbFD2dZ3h7afbX/Y2j45ErTupJvhm/ua'
        b'h1eUzykAOL12joUzS4IV1saNBIhxaggDKm0aPwv7ix6Z47TbEYRu1H79s3SiDPe/Y/4NWK1/u0v00JjYviMcDrggWPmz/+xCokmiQ44MYJuAjGf/BYnH3E6WRz/6YMyg'
        b'nWkOCnb9DkoA0t9KZaeSbXDHn4NKpjxkMiIJrDx4LpjF1VdyXf+yzTwTdzMNB9T58Ln9rS0uV4dTO+O8QOVje4o3jCX5pmfvnJSzk35DPPxHZITaBb4n4FrDyfxy+Asv'
        b'DC1EBbTwEPgV4FeAXxF+0+BXgt+LQgsbOPi1hxai/Vy4P+Zfjjn5IB9caKjMtXOoLucRm6RwQpOpnW8ytwtNlnY8HbTINo+1ydYu0b3dY2+KazfRfZzH0RTfbqZ7h8fZ'
        b'lNBuwbNHfyKU3gt+k+A3BX6T4TcLflPgF97jKWp4QIALJcBvQoD854TjAuiXnA8nQr5U+E2G317w64TfNPjNRYVu+LUEpPBA2RJOl8VwhhwfzpSd4T5yQrivnBjuJye1'
        b'W+XkdpucEu4dEGUulIlK4+FBcmo4X+4VLpHTwlVyeniOnBGeK2eGZ8q9w+Vyn3CB3DdcJPcLF8pZ4Ty5f7hUzg6PkAeEx8kDw5PkQeHJck74fDk3PEoeHB4tDwlPlPPC'
        b'U+T88HlyQXiCXBgeIxeFx8vF4bFySXikPDQ8XB4WrpCHh4fKI8Kz5JHh+fKocJk8OjxDPi98gTwmXCyfH75QHhueJ48LV4bsa7lwjjw+PNWfDndJ8oTwbHlieJo8KbxA'
        b'nhweJvPh6QELvMkOCQFrwFaHo5QadAbTg/2Dc+okeYp8AcyfPWAPO0ijpcMRqzOYEEwNpkHOjGBmsHewTzALvhkQHBIsCQ4NDgteEJwRLA2WBWcFK4LzgwuCFwE8DJCn'
        b'Rsuzhpwhayh/rRC2BVmEdVaug0pODCYFk4O99NL7QdkDg7nBwcH8YEGwKDgiODI4Kjg6eF5wTPD84NjguOD44ITgxOCk4OTglODU4HSouTw4O1gFdZbI06J1mqBOE9Vp'
        b'hvpYTVj+4GAhfDEzWF4XJ0+P5o4PiuT3Ph7yJQdT9NZkB3OgJUOgJdOghsrg3LoUeYbxTXtcyBmIoxoG07dxUEs8jWcGjFBf+HoQfZ8H3xcGi4PDob2lVM6FwXl1mXJp'
        b'tHYR2ipSSdIVdpzHdkcoN+QIFYQcAUeofK2Auhv0pIieFLEnVzgCcaRwN5M51KeTQqbXjzijZ7U1pC2YpVGIa+WV3n70osEt5w0NcF3j/UyvXF9efnYD0yetzq5pbfD4'
        b'G7z5gtKKuIiO7XCD7NEHlKvOS/I41E4Lm3RjWI7Oj5UnDFOWfAnQXr3bX6egAYXVvbqWtGnIYBtPxZvrIg5Do4g0iXj05tEEeBLu7OhhuqlFcft8kBI9zfVo0YuKZ8p/'
        b'csxVEnea1D6wXafxBPE0KuOc5gxV6mbZDdiWnCqgGnpEbGluidihdNldV40GDtY6FztuZRaEHU4Xohg6Yq6jciJxtc2uaqWeQlpiXE5X46pmr2dN9JEdHnlZYREH3Pv8'
        b'1brTSiuk6jzV9b6IBe6oMBvdeH1+H70l5XmqYWW10pFA5VxM0Xd046Snio90HrzNVI4HJrC6hn2guN0r0Y84JlClgRKmWo+7WomYPdUwwcMjYk1DPamco4MXFnYiYsfg'
        b'yOyeafk8pU+yX6mudWP0Q5cLste42ERa4A51FCKSS3HXRZwuucFXXeNxu2qra5cxfWIADJl5IEM69oyQl98lAB0CM9JWzNuTwOLaoB4V+kpCv6aoAzAdz9kFMh0V1gIH'
        b'vaJ3wHBN173q4E/6PkLgfCeqgKbTBg4GtJ3aiJpmZqONp+BtyAKYzgELKxNbEuABBwl1aG6RJVMsGTLCEEPZpP0lBaSQvZVTrgk52k0BIRTXKChlcG/25lGKUy4LOeK4'
        b'dlOIY9piIXsoGd44oe+OdBwLc8gC6X5rhYA51AtqFLy3BQRlGzzLCqXVoVeYnajhBfWkQD2/ptwZ8HVfLM27Gp73DyVRvvdCSYB3LGSnltFuhZyWUCrklGCvgLFei8Yw'
        b'TwQk2EF4Ks/cym1F9V8zfGWjcvtALsOLjB1K0L8M2ODOjncUdwfS8znW/xBPZVwB3yaE4uMMSzkxlEhv4zPQ1y3wiTIXiMN3AQHwbXw6x0y4yEWnjfndj2rT0XhCmfth'
        b'Huyh3lC7gOMSMKWiAUsGGwd4f5xanG6MRKCTL4d8x3/zwOT/vvz6F4m4Eao/RmivJPTsZLSrYBhlmQUrqf4kw1+iyEIBMWUgFgjIDNRuBi+JTsEJlG9f/E60U9ggp9Bp'
        b'sSTp+w8tlpcFfbE4Yarz9cWSGrtY4K2IkxeSYI8a1mn54OQVwjcS3SHgmwKS7wOKEG8O4V8aTLqISngBi3JNwELWONYA1MaAB5ZL7wmcVw71CQ0KDYZFkFlnQtdGAL5z'
        b'2+0hVGCzQ6lxAXuoDyzKVwDwEuK4TNyYRbh34n3AQcsOygnEAYmYoAMwqfWxdwH7BG7FDq83lBOKD/WR+dAg+D8Y/vcP5dXxoSSsJ9QfF1cqkJjwvHeIDyWGEpE0a7DQ'
        b'4jYhEMNiSgpYoTfxAPDwG4ClEXJmcO3OUDIQBPjEmc7BsoknQiEOviqikFirqQS4J9NSMypDtZu8H8FTc6gAyk0IJIQyKA8gBWhxQiibUtl6KodSOXoql1K5eiqLUll6'
        b'qrfRVkr1oVQfPTWIUoP01GBKDdZTfSnVV08NpNRAPdWPUv301ABKDdBT/aNjh6lMSmViqi4BNohiJPED3GZEnYgIoK+hIaF46HFiIHGr4DsSkOhqwSvBSzrCC5QB41+H'
        b'7rL13qRzaCsIY5qCcAaliuTjQMLRRwROzwsDEj4PSIZle4cr7KT/I2s3v+TfAH/8z+OowbDT+tZ34ChUQxSsuiNos+gkbJUskWEy/n0nWfEtOhtNReNKsxHRGF1IO76V'
        b'HGi6jF6sHEKaaAfs5eR7/PtMSnaIiXyyaMWD2B8kk0NEfr8TfjPsuwi/MaeOgMGAeQ5ZdfxmDnEx+E0MmWhTB7IlZAOyH/AaU/mO9enRPa3yL/DST0O6w2zY+LMhFXFA'
        b'unTKanQKAyOHJFgkSIEIgJaTWUfWkjYnUAMm6GQierGk51KAckIX40Nm3KFhKBIAUcUj2sYU6rKH7FuG8VhqXCgZFyEOFiEx0QRINmQbA4TghK5a7OtjtdgBCQI6BYQv'
        b'6veJUAppZGN0Hiov6u3lHIOa8j8Lz7eaDRkOQTLaOkkWO99XRBufEhEhzN4Zwuyxk7ESyU0gDUMJSApHJ0PSJyOPJqMXEGiir4jeYDoN0+RJfjpAnQOtf+mdfUsODR3a'
        b'xlsyyMQAU90M/MpOAw8kX8iSiZavEuw3LQHRt98gxHmsUQKyEndnk/JXDM+IeBb2NRPsPzDZ7ZY2O4okyIovWeL83Jo/GmVjcEn6IgO/X3GIGHRnMBGY89Rgep1Fjwtj'
        b'janDilh/K/Y8Hp8ZX7M9ESgNW53QyFppwmu0dBuKQ+jLGvgSnsEbW/TLaBuAeD2vI8xdd7Y6Ub+00ZiGyKlAd2HIKWwCepDAUDbor7G5CKnWlVwn11D5YkTw1yivIn/5'
        b'Nv+L/XZEnA0+V3NNnWuVgtrYyqfmqBGNpPszJMjL54mF/6fiZWT+O20JGnZweswSSoSrgzYH1FMfDKjfjI5yBNwi7KKdoosA8WpziBkWfJpscepi3mQ+P4NJJdqwdAoy'
        b'IfrW+JQn8dlTeHkaL88wZWn0VeNTniXLgDZPQ43yW7ptqvYvU54jE2y4cVdjCAPlebJ2aZCVHCoUOPaIWF0DvP6yah8aakcsuvuliMVn3NR7mmuqPb78+H/NkOUv+jeQ'
        b'0///yz9zsIEw2YbsWQThXBCksw81nKYMOnzAg4auhx5W3btG1z9Ht0//+T+z/j+aNjvEZIskzh6Na69uOV6zHZI4rC/eTZiG61KwmomxFATqZyVa0hzjKHqBK1bq53Lp'
        b'K7KpugWWpV9RQjyz3yWHBOwU5QladzNW17pb0D+xgmeNeKZSW93qc7tckVSXy9faQtJCFK2hpQo8jXN1JJSPOnuXiDF0ndDULLd63OhYj0WDlQCxJApAMnV3srNGfzoQ'
        b'A+o6owqI/xvANStR'
    ))))
