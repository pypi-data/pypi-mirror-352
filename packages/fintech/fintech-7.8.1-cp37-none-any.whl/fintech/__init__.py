
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
        b'eJzcvXdck9f+OP6sDCAMERFxRUUlkAQExa24mUHFgTggkASiGCBDRYOiqGGLew+cuEUF9zqn7bWt3b0daXvb2962atvbcT+3n15vb/s95zxJSABXf/f7/eMnL5884+zz'
        b'3ud93ucLyu2fN/ofj/6bytBFQ2VSGjqT1jAHGC2r5bR0OdNAZwryqEyhhtVwaym1SCPQCNGvuMTPLDKLy6lymqZmU4YxHKX1WuRtXEZTmd40tVyqEWm9s3w0YnSVkHtf'
        b'cvXTeq+hZ1MakUaU6T3XO4OaQxmYDPScTnmtlXk96uE9I18rnVpizi80SCfrDWZtbr60SJ27SJ2n9ZaxD0SomQ/E+EKji51W5tKOnrDov8jxa5Kji43S0RrUl7XiUrqC'
        b'KqdKmeVCK11OpVNWppyiqZX0SlwzevbKk7GqXOeQ4EKGov+dcUEcGZZ0SiZV2al/4M8zCnD1Q/oIKPQrjZ4lWxIwk6G+5vP+MPY41a5FpKBo3CLGRtlYHetqFf3srXIW'
        b'6NkqTmXBBYNd4HpSugJug/Vwa8oMWCGfBStgddS0hBkJEbAW1shgJaxhqYkzhfAs2DVDP8cnRWCKRDkvjhzwTfbD7ALdt9l3v5Jvilifpk5Qf5t9LycoN19XwJxf023Y'
        b'O/SaeNGsBJOMMffFdR0yKHxQoZG4yFSLIgJWRTHesJnqDS5w8Cxcx5p7o2TwBDjZC1SDDXBDMihLRklBLdggovwC2V4SWG30QmlkrJ0JlxkxDPIX/PJRwCidsXC51iDV'
        b'8dM/xu6nNpm0RnNWjkVfYNYbGDwEQjwg3SS0H22UOLOi8jidxZBrF2VlGS2GrCy7T1ZWboFWbbAUZWXJWLea8EVGG33xvQ++4EJCccF+uOD7AYyQZmghuVpIt3frJifL'
        b'lSpFhEYBKtPcR1UeK4DHB9EFuAmZRXfpewJq2Gfxo5f8mvHlnNUUAZe0gRbm1OzvA6js1TkL4pMjHODy2Vjytat4If0uQwWcW7xR926vBD6LZBpL4XmO1pUkfJE6kH/5'
        b'VYaIQi0NiI6riIXhKyiLEr1UgxPhPqBRjlpTATekR0/n5z4cXJiiVITDiqiIxFSamjdXnIJmY7+MtvRBmUaCjWCTD+pOsgKcgo3e4bAKnAWNHBUKbnBg1+DeFjyLaM4O'
        b'mfAsRqEO419wFV4RUT5pDNxkAdstPVGanFx4E5wvcMy1x0TLh8pYSxeUJhDaRsNbfZIVsqRUASVMZ4LBcS8LHu++oGZOMhnNxERFwnyG8gE7GNgIdvWzSNHnlbAKroHV'
        b'sLp3GqxKSlXCyhRwkqMCQTkLy0bDq6j8XridNZFgLzwJziUnyhMVBDIFlB+sYlVgPVhnCcFJLsALOfizgAJbwVmOo8F+eAM2kj5EwH1gdeQMM8mZmghrZYmoEriZBVfD'
        b'lqMR647SRIEyUTJCn5sxsShBMqxLQ0X592FHDpnvSAE3roRrk7PAZZQiMZVP4AfPsIN6essYMp5wP2wJ9UlAU1UEq0H1RFiTnKhgqCC4h4VHg2Mt/VCajOFUXrQPrItS'
        b'JKksqOs1ibAZVqal4IRD5goTc2Ez6jVuNdwALwM013IVrEuUK0GNXIiG7wIDL6SCeksPlKI/rMNDc60Y1qWgyZHLFEkCqnMvFm5WTyRgMATcAuXJaYrESFg7GOyBlYny'
        b'pChlQqqQklMCuFOSRTrWeyGFGxKJPigRcDXRlA88yMBL4OgoiwyP7bWw/GSSAnd7angyogp1sAYB41SFkJrAQVtnISwDFVbSQVi9VI0Soy5NC08AJ6akwDpVStpMnFQ+'
        b'QjAJXIYbXGSPcSfGOwhVt9GIjrI2ziawCW0im9jmZfO2+dgkNl+bn83fFmDrZAu0dbYF2brYgm1dbSG2brZQW3dbD1tPWy9bb5vU1sfW19bPFmbrbxtgG2gLt8lsEbZI'
        b'm9ymsCltUbZo2yBbjC3WNtg2xBanG+qg1VQFh2g1jWg1RWg1TWg1otYd0Wp/By3xpNVrVJb+uPf7QBW0EVIyb25ER6RkPlhLprdkah5BPZUC2AbLFKACo1VgNgvOwOOF'
        b'BK0myOEtWI2gkaWYVXSP0fFgC1xr6YoJDriYFQmOyxMETBLFgbU0LAcX4QnybQ7YhoBdpoAVCD6F4AQTAeojezKkxIVjwWE8N3Il3X86xSXS4Aa7yBKM270ZVGUmI/xT'
        b'0qKpFOdFgyNwjdjSDU//JXgEnkI0JwG1BL0+Q3EJNLgwqjspEh4sgi2RShlDMaCFNsLTmQGgli9y56JByeAEwlghJSxgikBTuABeJm0Eh0sWJyPcRySFngz2UFw/Gpz2'
        b'CiXfJg0AtQTYaFRiHY3G6HiKF9hMsBxeNsH1yQS65DQljGMQ2drdVdqTfFwC60F5ZBJCujTU8XgGnADb/GC9mjSGhdumkFLDFSjjMibAZxA44+jBYdhUiBA+HHXBQCPO'
        b'VjGmbwjfzC1gDTyEep6E27KDhudlk3WgmeAerF8GbAQrZInwKFyL0FcMbjHABm5FWoJQgoAlaOarU5GswljpUeDGWFiuIqX6gDULwElYhb+ACzTclDYDDcU2fszWpI9N'
        b'xggPazhKGIq+M96T5pFmmkDDIlidAE6jbKW0GG6dDA9lky9zNbARVqcpcSOraLApaIoPGi+M//AU2AtuIBKCC4xUJqKxAQhAVQKqaz4XA3YsI0Qa7oNHOidHYhaRBK8u'
        b'w/DmJWTAVsOEXMYB81w7YQeJOjbaJewwFUi8KWURAjEEgViCQMxK9tmFHValzxOPEpjGoBcbk6zfZL+Scz+7Iu8++uXeronf5ZUQSwc06HVS3xfmyH0yVo/atq6mRtIz'
        b'/l+6+hEtfuuzha8Ppt752q90Q3eZyIwJkS9YiyCC8C1YmyZDoFIH9yby7Cu4P8fCDXoiywxNRVSyGk3BifYsDpy1mAeSeQHHRhJ0laciylfJp0J4QbC2N9jIwY25cCMp'
        b'D1StisdJ0xCUgjr8HSHNaW9Yj2YTnEzj5aejhXAbSrRbT9KlKEElqZJl+8Az4JYZT8sksKkwUpFAeJoYXmTAJXAMrEV4Xke6B48MTSEtaiX+fLv7g4tgd4QgrcdSh9jU'
        b'RjAib4lYZOcWq02LGJdctFJM839+tDdt7OQSvDg7qzGZ7azJmGvECY2YBMoYN1mLMQbi+87OkknmVa6Cyz0ELsJMyxExI/gB64RwO6YBckQDQCPc27GEreSBjtExf1S+'
        b'5joCuS+/XseZsAS4sU/SN9nzbr95p/7FD+7Uv3SxfmOnu35Fn+s+SxFR8cO4f+/3QRIynhY0ARfB6WR5OCKHyTSamcrZ4CRTAlfn87PfkAE3tJGWwKV4Ak0RsIIfUKbj'
        b'2bCY9QWt4u8qShxAG4OoVvGXLcxZ+JgJoI1dXGOPs1TgYgJwMWXUIz/30SeErRFuDIokkhStsVKckUYocGaMa+Rpx/90Z2OsFNHgaBXfFEdtXp7t9zMUZhXm6CymXLVZ'
        b'X2iowZkJAWEIa+yim45FPTwyaZ26JkUqVCos1CI5gqUiwQUB3DUX1D+lCbqnNMHLWb+23q12zG7BdrUCEUlULdyQiGpGSBUIy1lEHY/C2o5BLgaDHI2BDql13DOCnc4d'
        b'7GiqI0onaE3gpKu9XfURumrjXPU9jbLmt63PuyMw39Bdz5iS0Itfx7x08m8Ps7/Nvp/9MFeiy1aHq+9+FXE+W9OozdaU328MvJ99Rp2vO6VtVOfnSPIQo89cP2K9eH3C'
        b'+lFHxdKoHasvIAH7oO8qS5aMNksxIjd2h9tM4HSCCikjlaVgGz+hnWA9C87BTQPQRBEA5dpSoTbAL8jKVRfw0C/hoT+YQVQoAFGj5aGmfL3OnKU1GguNylEFhSilaYyS'
        b'ZHASKE5tzDPZhYuW4l83HGmnFTJGLNMYQ13YgkWHbW7Y8m2gO7Zg6bQIrB+PdPBtkYiLVqREIqGOqMVwE1I6KhGRVyEZALQgCapaNH04Iv9jveClMHhNLyn/gDZhAdru'
        b'k7IoLz+vIE+Vq1KnqBf+tVF7P/uE+tV195Fq7q37rICmtK8JX30hyAnazzRiPm6j4k41ugQIjd1bqQavBT9hRNz1ZJxvi9tg/N1jMLBIgZhqJVwbKVrlORgM1R1c5UCj'
        b'uE/HuNTOZPNkLMpvS7yZdlDNqWboM0eGCkxh6M3o2vRkNRYXEtTcphqZNK7zDs3fs8VoaBfco6m8fwr35ByVcWZMCAbDfTmpXQiDVskVKp5ndgIXWVA3VGjGbAZJ4Efg'
        b'FqIPXwCnopCWHZ6kUIK6NNTlDZGJ4HQ4z60zssS6WQPMAzAWXAWHB/FMvzUNvIC4HEoXCrdyYA0HL5hxU7PAOqShYsYtS0pRoYe1qUlIR+IlhbB+gp7gUoY7HLjNuK/F'
        b'kJuv1hu0miztslx3XOktpPk/Y4/WmbezKJXbzNPO+e7pmm+cep/bfP9N4j7fWMyIhC3DI4lCnIAwuyY5Fc04wnYh1X+5ADSOT4N7B7kmyjnjXd2oGVHmnpl6esw7R3XE'
        b'tMWqAtzptyeJxZrJlFS76rWSAuXZ2N/7xHVuDhFRvHSxE26PilQkws2ozVdBM4W03YM0aAbnpxM7DtPtJ/8t/nT4D9SqlDvpozNe5e0vd/0RnHHUss96Wca+pRHyL/+U'
        b'E0jhebttMM3bMHEMpb/xRQ/WVILe7Ppbr2S1Rt2obdSeyr+fXaSuON2ofYgQ+2G2QRcx/aQ683Y9uFjfKeIlcVB1o/i4mjmx+bj2jPqUOlj0kHtb0jd7xLoP6YSuu9bF'
        b'Bv00c3Ln++9Gd2mmvtwxPaNHyLnj7Cvn7LHvxnSZvPpdW+y70cLYohaK8prQ55v4RYj0YiI2FjT1SXbZKsRIht0G6pnCXtkdk46nEhQuX23KJ1Al5aFqoBhRYOcfkQsR'
        b'XEjIHZJMernRmG6eNKbj+mk+GQE8nPmoG+B97EFosCpkjUCSQnUCkg8pWCmiuC5IJV2V8wTzK93G/Mo8u3iIO+3VDtIkKqLIgRZQMQVuRhVGwevgDLruEfPgspyjCjoh'
        b'wTc+O+VY+jgeXOYPZakdM3B/s+WF3fIpI6bKHV3sdJZ+dVUNa6pED1+kNinuDfID0QET39rZvPcFWePLgmHeXRPonq95N0w8KDbU76l66fOgn1OLJ158MXLJ/3xqC6vs'
        b'LDx1+bOSi2KJcfuVLNULS74rqeo0e2KKTqtpSdrad6Ew7J5ueOHvmUVXpp08k9D84eKl1157YffJa6uOzMz65dF7C7eXavp0elRx94UN6u9qf9jQe/Yn/VSPZsh8zJjK'
        b'hw2SIXA6CQ+0ak9umtNMsJakGo70yy0muUwGq3xKUyIUiQ57MRUxVwBuwUOzCMG1wqPgOLygAqfNCrBrOZ/CF5axg6PAcTMGBFgGV89zycyZMW4KmBY2mDE0TNOaI5Ww'
        b'YgLYASux6g/qGIUpxIzlynHg8oJ2qplTLZsOTsGNefA4QRh4I4yB66Mik7BxJAVpwT6giYF7oxaZiUZ/KBS0RM4E5cpEeYRMCTcg6ZSiQqTcgrhxvNK2Gu7rC6456Dyq'
        b'imcDRLNrSRhJ2jlWDFp43WCaEGsHWDWYHWPGFDEG7rMkw52RKkUiGjKGkohZMVhj8BDjn6CrCYssOQV6nuqH8fg5gkGaWiCh+0E0h6689uaN7rwRnkpoo9QNR7t44mgH'
        b'ckCrCoHzXXFDz5fbKXClcK9XZHgqUpsrI8GhFCFShM4xoAxshi2kwlyhA7ewYih24paSxYK8le5GlQorRFZhBVXOlIqsIpOqxM/KHqCswga6VDybMgRxlJle5G0cRlP4'
        b'bw5lCM5Awq9VjHNahbiMUZSGxnnraSNnFRRl6qlSwbKDVsEBpoGaSM3fNo8p9Sr1xrVYvcoZo47Ux6G7M1bhAbYBlbNMh+44kjqo1KeCRSl9rIyOtXrX0TRVvAW1YyLJ'
        b'JUGtlFR4WYXlNMoVVuFdIcb35TTJKSY5xW45X59NWSXGnyokfA5ne6dSxbrZVD1jCCOl+pQzqO3yCrqCWiTEd6g1Ag3TQPOp62nDryQdbRbqGJJ2VoWPI+2sCgaX7Ur5'
        b'NkkpJKmsFQJHKnTnkeqUhj0g0nAawVqkIE6kymk02r4a4QGR1feAWCPSiBsY/Mbqi/Ke03hZfYOpUl+byOaDRDdW443yia0szlfqh0bAr5zWiBfhGv9i9dP4oJnxM/R1'
        b'vefQ+181Elyj1a+BDsZfOY1vqZ+VqWeMk1F7adJexhim8bOiHF0RkdYxKJ2/QWqlrcwiFn0bpfHH9473Yk2Alb/r65Y/W9OJz+9Kg2vzt/prAofiX1+Ups7qR67+ms5W'
        b'P6svLg9/M/hZ/fGXoh1WX/xs5uc4APUiAPUiCPWCMT6yBuDeabqgMWWMr/BPKM/f0J3Y9f5z/gm/R73spAlGz5Sm6zqmG2XtRNofgGoPqfDFNSz0tgY422Bl61mj1Exb'
        b'/cvpNbRBbPbh7xzqZDfVjEeiAqRRGxSDHjFyqYsDMg4uSDRkzKjyEGrN9y6lrfRCaiNTzGGV3SFJ2sVZWQb1Ym1WloyxM8poO21uozo/8h5VoDeZcwsXF435hXLozkJq'
        b'eY/cfG3uIqRVtSperQkfsdJC4yNabuRICYU6qbmkSCvtb/JopMCJ/VJnI4Pxmq0Vs2jGxFWgBpfTjgbntTYLEcYwwieXPIEsGrH0/Wtrex/gSh/5q6VL1AUWrRS1KLy/'
        b'SUYY7qMQk7bYojXkaqV6s3axtL8efx7Y3zTwUSfyAt+6XnHk2tktpTP3Iy/pYovJLM3RSh/5a/XmfK0R9RgNBLo+CCANf0QPfET3feTV3zRXqVTOR++xyPqok1yaV2h2'
        b'jtEI9F8msQv0Bo12md17Fm7wJKzMoVeoVpOdyy0sKrFzi7QlSLNFNRdqtHavnBKzVm00qtGHhYV6g11oNBUV6M12zqgtMhqxxG73moEqICXJAu1euYUGM9YZjHYWlWTn'
        b'MBjYhWR4THYBbovJLjZZcvg7AfmAX+jN6pwCrZ3W21n0yS408QnoRXax3pRlthShj5zZZDbauSX4yi425aHsuBl2QbGl0KyV+XYocD7PBTGlBBcHFDtB8TXK4dJAMZjb'
        b'cTTmg360kMXcj+eDgQ6Z1Y8OZrzJM+aQhDsywegpFEmwwXSAMIjwTzG6xzZPPzqAwfklJL8fg7moH4NzoTeMHykvhO6BygrGPJYhnJAD9eAE1o/0vqmwTiVPQpJLFjsc'
        b'tsBbLvu5mACnAw0eogtiVsyyv1ipAxRhP28jZsWWclbW1KPYz4wkVvxfjxjcHrZUYBVYGSs7CiGMcTpigfQiIfpFjKIbdYBBxJHtRjUgpoOYEIcIP4dZhUln5fLoUm5Z'
        b'hpVDpU9FzJbFjAQxv30I8TBLEGhwiQINh0ph8RP6RawQl1RcwDMX4wkNV3RKgxm0wCoitQn577MpxFhIC0hJzCj+mXM8c6OoYj/EAhkiZwtUCH+n4FkkU5mIL1Ncd/id'
        b'TGAciSeYNWnNdlat0diFliKN2qw1jsZfxXYRhr3F6iK7WKPVqS0FZgSy+JVGn2s2TnYWaBdrlxVpc81ajRGbuoyTcGbhU6DMzXyJHRA0Wc5yeyESZhpAgIxD4ICBLIAH'
        b'BAxqBLwkdAgTgJ4DEEBYcFJwlIHnHevdOrAJVEbhRbpUsqxGRYJLAritD2jwUDtw1RiKSFXtFj8pvPyp83HqNFbaaWF0V4Nc0pUGXSrwNNOViL8vpIoCEJihTMbBCDB8'
        b'0Rsac81y2gfpN4QvIYBA3I6uYCt88H0l9mDhUCNw1d6oKRKd2GWG9LIyGICIHdhNdcJQjQeSWDC/xQ3grFhAoEoaly1A1bL4iQhKqlIGFcHihpXTiyhjHL6zomaUsoYg'
        b'0jghguwEfIfeMFORuEfehFRgAQZhgA49Y2gnIlbIbGrZeCsud0QpayWlorRVFUIEpSwSYjiDBN+j9+TJyhmLMKNB+IPKsXKkjKLZ2LlJiURNzizQMUjc/AuNhEiaWi5B'
        b'AyXATHg2GioNerdS4HRmQriBBq6OJtYKWoUADKsWdtEStZHYINk8BMSIjBoXLTWOwMA1gQfDVrNjCr4QqJ1PoF5rNMrEz0wWWwFWkkUIYhGqeLFpnAtcEZAyDAZSCaaA'
        b'DIOeQxgCrowEgXEIAtZQenm0OjdXW2Q2tbJ1jTa30Kg2e5pYWytA7Hgurhr3w2lVJC8wKMh8/iiBZ+0iPGwIb/ki57m65+Vq0DDauZDE8vS+F6K9od2Whz6+D04JIhMX'
        b'p8X33n+I+2S6miNyVDaEdtgIKFbaj6yfTgfroS05RaVShMuEsNqf8lEy8DA8AfZ7mDC9HL8mTPK0VCYS8DKZLSLeboHwXawT8MhWTmey5D1xKHNQAy+EithJD3/lbBRH'
        b'ZQp46mrv5HCkm6wv0KYUqjVaY8fLtnEUxZvjBMTLQqgTunCbe+ISw9qnL2mIVGRRfDKsAc3JsFo73eEsAutZyg+cYAO8sizYIAi3gu2wAS8DEe+1VqcSWAFrU5bzdobm'
        b'6RQ1L1wEt4C1oN6iQNmmguMynIkdHzUtPBxWRSUoYBU4PiM8KRWp6cpERVIqTRn8vUbDatBCKHEfcBBWpytmJcAaWVJqCkqLasBuNqn00LHUYLBNGLYYbtDHJ89gTFiA'
        b'/k0r+ib75ZxGbaM64/YOcLm+KePoWtm64+vH7WnY2VTZVH48g72bJ2xaFDIi48KHVQVl1m2hwkHnXp1k9TKJJohMse8w2/y2rau5I9mjoH78qrMw52WZgKj9sAlejhg7'
        b'EVYnE7clrheNmrZDS0wjQ8HelfBE38h2FgfQAs7w/njXwC64Fl6ANQpYoUyKiih2mFhCLRxYD2rBDjPW2oew8yOVigQFQwnBYQZsDYkeAdcTG8182NQtWZmUKk8EtS5T'
        b'jgBUD6T6TxFkjoX7nGbhZ2eUvrlGLWLOWYsLNZYCLTFIYPWDWoX+8ojpgeFFLQm9vHc74FR65Hat35i0BTp0xXSg1UYheDxqMkY9vl/obJUxH8Mixk1scKDK0N++YDej'
        b'xVNb4oE0rkW0MU6kcefJNMJGbxfyCJ59fU5AuWlDLuTxUxEvt5BMuKfVzQqvn22CF3js8YXHLbEYlprBFnjaA31K4fFWDGqLP5XwGPEhDIEn4TU+W3i4L7j4BAzqD3c/'
        b'fg3WYTl1rcHaaV3bFVjxqAL14hyNeswKlNOIiY9lJrpIYb3E5OpckYfjG9yUDE4npII6J3wuzU9EhMJ9cY2NCTSBzdMD4WkKnILrO4EyWAa3Eh9CeAMeASccfh41sFpO'
        b'rHLwqBflN50dFLLE1RsB5bbWSoghL+wweGZdxJCtQDNYyqH5ZMl8cmQ+2ZXc44ihS/pyJ4Z42TC+cFIyXjlR8ovc6QmR2ONpJqyIUshgXUopWJs40zVpAgoc0HrDm6ae'
        b'xIp82UdAlXXvik3Lkq8m5vOeoGAtDXZ5FMm7gsKKvOFp/Ho6dgVdvMorZBDcYolCWSbMG56cjNdtElOnhcPK2TwRnOaqFk3NPNgUD46L4Fm4d6V+07wK1rQIZfx187CT'
        b'5gfEB+dlnTJQpk5RF+gKcr7NlhsfZr+W80rO6zmJ6k2auzmntffj33jw+Z+jqZkj6Zmx5TNssX+TnYveck5r6nIkOqZMOnX9kfJJe+iw7i/X/ymIfveTO2/e+fhPIfdu'
        b'f8hQf54VcvdclExECJUgI4FMYhPc14HJGR7jl5tBBTwKjhB6GLEAO7960MMBQmKoXaySIJIXDXa3oXqE5PWZTUhv9lzY4FiwS3PU4wvP+0xkQybDg6QUPdgNtyG9Dv1s'
        b'di7sKWVCKnAlC2smTTFjqb0P3A7P4jR8OXmTBJTPUAbJ/2cXkuaOBedgiwmcVsKT/AK5++r4MlD+/MTXD696ZxUZkX6NNR1CfUOd1HcVJWaI2sshRTYQK69IO1k+pD3l'
        b'0y7T5jroXqvw5Fkyj+ICXiprFV6ftsjjWAvydWUgxHkxuqyjnYyijPz9x508WxZQ2B34Eqj2pBJb4LonUYq2dAL79G4aDpsEk+CVeNDcH8kNVF+4NWghONmlALcvalA3'
        b'7n8CqfgfOpcIXmFaBv1zxC6KLAn+ItxBnxNR4i8TsmM+jpnuE8C/nrecrBRm9572Gf1bxlvT11P6OW/YBKZj6NsuztylZiRZtFn6vurXxOqJkB4mXPoZdThD8LI57Mgn'
        b'nyUsCH29/uMtqYPevrf7rYq0HwSrfbst3RPlM8hrT8Pnohdfm/3aVz8UXJk77lconzV1/JHTnW/1i+he+8u7XQNeqd/zyuy3tW/c+OkH4/cvFNl0cz89sO7l87m3Hq2x'
        b'v3Tw1UHdlLp7gxvMgZG/nduhDZi9EXoN29eQ8V3t5YKSy3cmbg2o+9MPv7JTs+U3VtyVScgiCzgNmma0cUyaC1eTVZbFPfkFjuPgFDjnJo00wb0uiWSXmi/mak/KIY44'
        b'kU+S6EC/4NFmvM4/H6wGFTxunQYnXNOJUHcDnkZ+1SROI5y/AtQR6YXNhPuQ+BLW3SnARIMbaiL+wJsacKXtnEcmCKjuQziAocNG1tR7IrZY42ABBFBAVQCsx9V0gatZ'
        b'eBF9OkOWZ0aDnQtgtTjSTRYD1bPNGCp7BXlF+i1MICIYN5QGZ+DaVYRSdIIn5Q5/PoefXgZoIq56LLhBUhRljmvLf3z9CfsB6xeSHsJd8LIXEk4vdUmhKXoYhYjJoa5P'
        b'Em/+mLYidJEJHzcMJzQi3EkjzC4JjcHuNRxCvwB0xzGB/kJ0DWAC6OU9n0gxHDIbEcDsQse7VrrwzKoskuEK8b3eRSYM6FLsIcNt7OUuwz25XYiKEvund5bjRVYW0pGz'
        b'ii3qAt72TWREUondF28dUZtMuVpE87L4Hnk953DbvRyFoAJI8/PQJcepHoqZEF8LRge4ZbixveiDMGS30+9/BLghBDthBdjooTCKHb/E99GpMGqREugwE2HxRYAEF0bD'
        b'rvXyUAvz3dTCqWozGi8DGitVLucoEcOJa717FLq4xFsi3BKHNy+HQMRViJFAJEACEUcEIgERiDhsEOlYIGov4Ap4ARcx9mZ4xSnigoMWN/0wPdSCRe1ZfSYhbhmekKpE'
        b'AotDY1NMhxVp6eHYkjZTzG+cANeSnXsn6GSKiuns7wUPgjP6u0NeY01YZT9mTfome/7teqzI3T27tqm8qfzITj2dLlokWvHAIPrT+K8y14eu73vWryV0vfwrv6O6ozkX'
        b'ArcFHdW9NOAlP2F9RnDkDs0i3Ql1Rd4ZtViXQOe8Ppi6Z+8yNUCNpBWyOeM8XB3sopTp+a2a23awz0x2pJwCVwe5lLI1IzFZgza4ms/evLIzGYhkUMlvyAC3QFmglgWn'
        b'0pVkrRqsTwDr+X0UBES0YnCEWQZtK3gx6JrAD1NhuHm4op0UBNYvJkSnR8gIp9a5BBwixE7fj3wJQSSxMpKndQUjCLVjwp2yyPOhgbvzpQ6BWRZW4Tx1wlVUX28JNr9L'
        b'EM0Jopd3bweZSldOHhOFdja3wGQX6ywFBHXtXBFKaxea1cY8rdmN1jxFbkJEagm+X4ovy/ClxEVrLOiyv41I8kUPd2rzpHbKGJXKQW+MRfhSTKguIQeLteb8Qg2pwGh0'
        b'DtGTiD1tNLmaZUaXva00BElG2IPQVAg3tdIQMdlihPjfHgJCGD5GSoXgGNw8iWgPE/zw5rLsAAmVLfmy2zTKw+DssgcNo9rut9GJXPth6Cfuh8nvyALsifPdVEQBAfsm'
        b'wksmBKoXfYotsAXJAJdgk3kJbPZZAmr9iySwCTHlAlADjwrgudyRFkyM1KC2COWoTFHB2kjVTKLmJqKfyjQFv/ER7IiblgBOwwq5EjRNxzuLwEVw1RvemjnkidszWbKM'
        b'/Qfdxzska1gHkOfER4LGFMfsjFbCOpRwBguruf68x+RRsAZcwqjMdwhujQTHU+ThNBUKNnLGdIv+o09GcqZUlHT0w7e/yX7l64fZmbfP1TdsPl5+/O7x8kHVxXR9c32n'
        b'u6KmnSN3TA9J3xEcU/63kSHnP6z+dkRI8LmyGdEx5mhB7OFoLrboP1OP0tTbmYH19VUyAaFDuWDTcqS3DETCMd5yIgSnmFhwHO4hhKAIHhYiOpBb2ir1XFvAU5jVsAo0'
        b'EpsBrFIkyFPAdZzGH6xmF8KzoIwQqcEaiDuG1NrYcLzBiRtOgybE2+qIpzwCWXCm1VEenGTATb8ScA7UPnVjgo+6qEiLUA2jfVtiMllCSEkA8XRZHoEIQlaBPldrMGmz'
        b'dMbCxVk6vbtS41aQs1ZCCJ7oCLPMhY4r0OWFNlTipoczzFTc0y3ghjU5TQEqsQDKTzOoTSMKP/rlWVVbTcUxMogBEEKMvjZSGrAvYDEzkexnWgHPiiLhhmywFdbExjGU'
        b'AO6jwUVJZ2L1ABWT4UaEJE1Ll8CLxRJxUbGkmANbwAkqeCSbN24m2dXqu2CSCV6ETV5wV3ffJb7efmJ4finGxWIBFRbIlUoK+Q1eNcGaZMTJsPzKdi5GM3WOQbxn/1CC'
        b'jaAeHgOHwUm4Gc11ZUpEkhzJ9FuWKsEteTjm0ClOL/50sWM/Kk2h9Bd8JgR1tWAaM3eIqE1eOdhpeHzebQXecN18UGnBO5jhOXgZ7ATVRcVgA7jYYylsIeTEjKTtS+jb'
        b'JQvqSTqHgPV6BtmCaQWrheDkcgTHm+H2ZKyzIzabIqL84UZ2erzFgjfzgAuxU/gS4U6wza3IpbBJ4i2kwhI5UFU0h0jTFryRBVb0jQEXEByOmj2SGpmImoaN3WPAIQPc'
        b'nKZIhNvA2YREESXJHTeagfvABVBD9m3DK6B8uI8C771Kns13F9bmd3eRNNBMaNd8uFqEkOvmNOJtCMvhcXgzHdUNr8PDYVSYEewlRP1iqZgKkO+iqezsFL+AKN7bsMaC'
        b'dwx3EVDSbMn7mSwSqfn965MRLgb8RGMnxLjMHnzaTzvhtNNw2pSr8hmUZTCurm46PAovCMkGMWwpqiTWIU/a62hoISgTl3YF5foVqQ9YsuD0IFOQWn8tiR0Xsu6NsSsS'
        b'44Z+T69I/pEOmxmQ/OP0U7WfbFjNBZ+Pm3tvTdjqmq3vzYqtXeef89fYX+R3VsXtrl/4+l+tph2x/a7feSE3I8c4Y3y/W8FnCw5ctvy19MiEs1nCARc7RdbeHDb+vZhz'
        b'TWf+Z7qiqWY/6zds3uDkmNri8kOVr+TtevjzB2/Nu3u68FTpttkF6R+cjUhvefnl9V/OevHjgsLmpZmjPpzz789PvX7tY9MrA65/fd87reeHE0L37fjtyM3CT7/plDTz'
        b'eqh42rfKe7PPn3tRtHvdgJ+WfrpCe4D9aEk4DKoZ+fEXnV484rf4T/+qq455e+N3ScqvRV9OKB49xhy2a2z+iHeTfpP9VPuXI5dfNG8FXOZrlRsGJF1OO/3LL0FxxT8s'
        b'LCuY+vXAzRk/ffq59dXk5N++GNnN8vXSqlO5Ff/+7UvTro2z/BOCfw98tHyyykvmT1wPwV5oG5qMd91XyzHNYCmfTCk8zzJzQTlRTuEl32hEX2h4Gq6jmCX0uHSwhqwu'
        b'mMBNTWQaqHLTWxG9uMbT30bEI7cmp0Qo+a8+XeYWMPAw2BRFbFfgQj+O7C7GUyxYAVsoMaxmSpEq3cLvZDoIToCmyDTcIixmiPC2YAQhNxl4aSCs5oXcS/B0byeJB+f0'
        b'vMOjRksqgGvjB0XCikR5ImEiAsQ8rsCmUaxOE056rUnRJmNhH5UtU6gUDDwKLlFdU7h4sMdIOpc5AZZFKsGevhginV6fvt34bVhH4VXU1Gp4WYbyw2oRxSlocDoOniCK'
        b'vgBVdT4SXuySlIo0bq4PDfZa4D6+X8dg/WzsTIrKxAQZZVcIV9FUV9DCJWQPInzRLwyciFRmR8paeWbPyaTRFnAxwmO9pjPcSwR/eGzkU8VR0fOq8V065G6EI05v5Yij'
        b'MD/kiMcnUuWZAG/0nwmk8dWbDUDvQonozRGXBezngleHxcSpIQCxMT+yWhxABzISxmh1MmKknbfyyGdpuJtTFi7kahuueTfEnWti+ihSdnPjmYHwZkdsU0AtMIvBVrAJ'
        b'HpKxZPOaqLfUodbAEyWO9bSNcBe/Z76mH7qvVoHTKcQrfiY8Q/mAZgYeQTyabJYFF9LhjUgEbhFCNK8HmLRhsb0jclk3IS/YKejNwlJj263olGszOu2xHZ2xddEFu9YQ'
        b'BI9dQ2CJysz9NQxNorfU7d90bZ7eZNYaTVJzvrZtcBSlt0faRLNUb5IatcUWvVGrkZoLpdh2izKitzhEBt5+Jy3Enm45Wl2hUStVG0qkJksObxbxKCpXbcCebPrFRYVG'
        b's1ajlM7WI+3FYpYSFzq9RuqAPtIqZ9nog7kENcGjJKPWZDbqsem4TWtHEAcCKVbkRkhxABh8hz3qcJGO4lEPO8iySFuCvd74XI6HNhk10iVozFCbOizAYkIf+eyu9JPG'
        b'J05IJ1+keo1JGj5Dqy8waPMXa42KxIkmmWc5jtF2OvyppbiPhjzs7aeWYj9I3BxnWUqpqhANXFERqgs7z7UrSa8jufgBRXOVo8YNQnOF5saUa9QXmdt1xMO04tdOB/FR'
        b'WYZguG9Y7pMe5VzLmz47AQmZ6QlJgunDh4PjMm94pWQ42Brfd3gXCtbDRh9YK+mW1tMD6gOcRSd5Qj3lgHvaBfeMzV8X8IyrZR6KIqYP7QMnKFQoDaEdqo6VN5ffAt8k'
        b'yrVU91wqHC66/WYiAV8zobj6K/2/oUxYE/844otvshVfJagluvvZD7IX677NTlRzGx9IXqvRp3xYMCmzZ430R9V7o1r83jNL56vfufPuHSpwkc6srvjzccE3p9T1Guob'
        b'3ULdva/kVcxucfD82+cC7p1Xh1/0EZ0PjlZqsjX3s4Wf39kZcO/2TiH1a0Sv3339ZQxhW7mzYyIV/cDFcN5qtItRgP3gLPkEWlbA3ZGwDsvIXB/YbKFh5bAez7+AJMha'
        b'alQXERbSq5WFrKJCOeIc5I3oM+8sGYS3XsqMDrLk5hTkAGC3N7hEp3aF4ec5LDQ0n4GwjZXo0hW1zBTcyjbKqG881onGYmjfDcvAsUgnuE9FMnP7vZitmtikQFlUEmLj'
        b'k0Gjvz4dHujYPSaGh3vquXbf5j19dV+kskxE9zHdwMHY6MExcYOGxIJL4JzZbFxSbDERLeYiPI+UEKQ4wwtgE7juL5Z4+3n5+iCNpwLUMEibgpe84GnrICLGfz03mdrS'
        b'Q0dTAdlJ16wBvGxfF51A1VPfcEg5WBjM+ToAOu29SwKTGt19kHezy58aguPjAwRv/q/u2P3X75xNWHPAx3ux/7i+XrGJH77xWdpp8xu15oKiBRO8EwMLHzRdvHB5WUJ0'
        b'pTE57tdZRUOuT6xVv3/h1aT/7PeXHPVdEDhleJ+HE754tdOLj+iwA13KTC859savxCsyLnFwcxAvDiJdcicvs22AjULE1U/D1ST4h9NiMC3xSdaxp21bE2cZC81ZOVhF'
        b'RuMe4g7T4RyB4yDijRJIL5c/EzQ7inMucxD4nOQJ1R1sKyYpWmEZBz/o3w6WP/HY5oY9AzP84C0XJLuDMTjIdQTJsCoKVKbFxLHUElAdoISN8AqBgJ9CGWpqF1x1dsql'
        b'pV0oC4ZCeRwsg5sRTCpBMzxFKeFhHUncsliIdAU0VEhtHJSfycNQwWIBdTeSbGeTVGoH8DBEvoxL96Lik/uhorMlFbFj+JcB85IoTacIDIfee/Km8S/P9OhEySegfhVl'
        b'Sz7qsYLiQ6XsFwvSYS3cMhPchAeHRMMqjhJOp8GpNFBGcg0LDKXenWtAZWZbMyVD+aLiFjbRZYgR/DDy3kpV9msa3lRxRAuPpQNcFqwVUGm5bDY9Bq4HO4ilAd4AZ0e2'
        b'GtpmJiDtAlbIk7DZEGsaxO8BiZYt8FQkVohAZaS3DLbMJSu9QXFCCrV22fUplOTDjJQleyiyz/QHdoBYPIeKPtp/Z1p6rmJo0dTX43oVxVP81kCkzyCx9QJiLqlycJVK'
        b'lYJLpPH7Z46gvh37EPco8Gh4Ed+jJfPHUGspKjx+uHzeu37X+E2EB7uPoQ6P/zdFRWcbR2s0fMqLtILOZqiA28MLVhwIuR9NXsqHvk9fZKmE20NTSqRZU/jsDewUegtD'
        b'xd8eIlEcE5Zlk5eXgrvQ0Qj2bo+RZOqC+68gLz8Sm6kf0G/8yHsjzD5dafLyDcUMOiV/toAKUCf3CO3G1/4/8+rpcJaKvh17yvzq8jGRfIyz+RnUZdSf+NHfpv+8sMSf'
        b'vPw1ti+dwlDDUEXLTieF8u2MyOtNTcTdHJPSTVlaEkNezslMoQ/gHg1JMSfmrVlFXs7SBNPW3pkcAsPR80L9+doHxr5Fv7lynIjKVvt/PyOcf/nv0S9Sbw4OYBFsejUq'
        b'HTHUhFGl1P2J/6SpqdmzwgQ6/mXppI+phJlLWfSy247AWP7lGL0vVZAymEIvU4rn9udf/m4qpsrQzBUNqlL07iecqt9Bb+NMh9GbU2e/njntWt278QHfltj/cuOfStGy'
        b'H38aseBP/fpKw8Kkn35GjZsVs/rI1oys24mxG8ftS1bViTf+Z6zVr3f8hq59+rw6/5Mvdz38e/HdXTOjf/3qNe+c5J6WluSrJUvfVUT4eP1T8c+Nf/7k/PQ3o+dVL5j3'
        b'a1HQ+VnzdH3KFQ9ivhjx9Yi8wTUDdtz1X6vZc2KctOe67YO6vxw5efgm6UC/pLoPg97Z9N67r9y9OeCecJbKz+7V9cPh96/J56w+NOt81t/mlL+46rrR+8H6HHmCcexZ'
        b'9puFn1TrXlw+Lf3emrLTX/b5IuP28uZ/V+x5QzF07Z9HjJD7jG85mhT87RcfqG/5G9/s5yt8f9nAL7bEvqX93Xasz+HyF38MXxb1j0sfGR4l/TjD7H/hQEnmvk7vFx+a'
        b'+Rfhut3h515SbPngs7i/f6b8+1/HqH6g/H+sGLri27B9P6Tu/2lw2t6XLpyQ/CutZNKYyn8MvnV78963/j7jnZLpb1x+v3Dcj+rvJ0VawS973rp5bK91StZQdV3X08sm'
        b'7DfuF365qfHBl11H9MubP/3kgrioYzW/aa9u//fsA9+N63Nl+au/lxeemD63yvrzv/xV1zZsfsckE/M2jjPgQrBDmacpULaE2AjgTXCV2E1SR4LqSFgRRc0aQTGggZ4K'
        b'qxP55bXtwYMjkxTJ8BIoV0SoBJREyMAbSnCLt8echVfALmzZHoGIRSujAjfBNWKZAC0mcBnRkLREcIqjRgGbsIDp2z2Xz7wFbgWNkUpZUqQjVJ0/LCswsoWTYBVxoRgG'
        b'doMzxK4SQ5b4eNMKNquAfWATb6M4A1tiXFE1lhs83IZg8/MuVQc8vzfBM8uTYicHJex3njv7DZbQHBPsF+DN0e6RhfBvL/Qbgv4C6TDEDXvQQvLFGwuebCAdTJi2kOwz'
        b'F5O9PX4oB7ZfLA99PAt3rrNh13q7yKEu2gVEB3Tj3f+FXUmscTW+Jz78a1wsvwxdAtux/B8i3Fk+3udihEfA6Q55PmL4YMsMT54voIANIPnvOtwGTpPFwBi4D+4iy00u'
        b'g63T4AFOwO0CKgpcFMBT4yfzJpG9o1FheDltRiC/MIH9QwPgOrZXooUQwmljGCIK3+5lkswIHeXg+YV8CNQ3h5nlr2h8+Zei3nyAyjcNJkkL0tb005ZsYk370Zcfx43s'
        b'iX2h4iUTvysYszsVDBUXDxyReXjwLL/48NVrJoV+r/jMe0/A5s8Tf/6lZPA8e6TXlJXnz9Tf6TOl0ntI6MWM7Erflg9q92o+XzDmp70Xd9c9rP1LeN+98x9uSvvPa78U'
        b'Kh82b1CuE+l3TO7/8tdf/fza9PuZ5VtEVdeP+V/4cPvZ5bmqrbZ7v5UUvXdnwpnaL//8acvpcx++oZKZDy7/lf47HTVPf9zhYzhfb8TBTeFxUOcR4NQR3dRPS2jDIOwH'
        b'xS/O14JtLtPigMnEJWkQmrCt7hMUNQP7GKbg5bx9XGEy2M/HxdkPDmXxycANcJFPimhBYAQLGmlQwTtT1cJ6CajOGQ43uExWlB84w06E+2ElLzNfyU8A1Tp4NEqhUsCq'
        b'FJmQ8u/BZs2FR0kUsB7x8ByoTnMIOnLfbk4Xw+5gIwcOwU2IWDhUxOD/OhF4ZhLhxFlPTyT81wn7IYVPkRDjJYO36DHBDL+FHZMEYzlKq3JHbB7zCNK1onTn/8t9eQzC'
        b'48b92sbMuT7OHd0xOKkTRiJkB9dx+FaM8AzlH8fq4Nru7ZaX8T+ThG519tHQmayGyeQ0bKZAw2UK0X8R+i/OozK90K/3FnYLpxHU8jGq8AI+pxFqRGSPiI9WohFrvNZS'
        b'Gm+NTy2T6YueJeTZlzz7oWc/8uxPnv3RcwB57kSeA1CJxOaJygzUdF4rzuzkqo121Rak6UJqC0TfxPhPE1yL41fhMG1dNSHkW+cOvnXThJJvQY7n7poeqIYujqeeml7o'
        b'KVjDEQtSb7tfCk/gU9UGdZ7W+FdRW9sptu95ppESTwyPRE/LoTdhQx6xpmpKDOrFemxTLZGqNRps7TNqFxcu0boZDz0LR5lQImyhdxgnecugy+hIciilUwu0apNWaig0'
        b'Y4Oq2kwSW0w4/LWHndCEk0i1BmxF1EhzSqSOfY9Kh+lXnWvWL1GbccFFhQZiCdbiGg0FJZ7mw5km3qKMqlIb3YygxFS8VF1C3i7RGvU6PXqLO2nWok6jMrXq3PzH2Hcd'
        b'o+CoVUkG02xUG0w6LTZHa9RmNW5kgX6x3swPKOqmZwcNukLjYhImTro0X5+b39aebTHoUeGoJXqN1mDW60ocI4X4vkdBj3rmm81FphFRUeoivXJhYaFBb1JqtFGO6NKP'
        b'Bjg/69Bk5qhzF7VPo8zN06vwFvkiBDFLC42aju1DeLUUwT3Hb59y7tUqZYgFtGMLEUt2a3KP1rU3KRv0Zr26QL9ci+ayHSAaTGa1Ibet0R//c5i1nS3lLdvoQZ9nQOM2'
        b'bmqi61N7M/ZTgiEK+WDj8CCoVzm3ivD7RPaDq4/ZbbUGHrDw4TF75+bA1e4ySXiCXKmEG3Do1DiwXbgCHgJVMppIJIOmwmPJhukoVZoC72SoTaOpQLCHRQWcn61fe+q+'
        b'wISdKjR9j+MtWeGfP0BXefDxkgfZCY5NCMpZ4eokNXOhW9fopdFRmnm3z9c3bL5SLqtuLr9SPqhase7K9uPl/feNXtdnx+rYntSaBZ32/UWINAYSobcOHM1z599O7g3r'
        b'Ud8RB4c7YDkfKSwPXsUJnaw5DjY4uHMK3EtSKMFGsQ/qsGww2OGSJboAGycuBgf43V/XA+GmSFiXMJhDIkFPFl6jDeBiKGHts8EaeBHH3E2D18YolNhFpp4Bq33gBaK7'
        b'LAVns2F1MdiarBCRULjJfcWkzGVg01BSZLZPzBCWEi2n4a44uIGsuc5BM7UDXh9GOliRmiKkkCRIwytLwcWnuaF5yPRZegShWVmEYQe7M+xVlJeEbDDAcvnyrp6gq3Tm'
        b'U7n7CBsrPLl1xxsHGD5ZqzNwFa61nThdHuTuove4+jvewoRFWCu10BlIknjwOtefkJSkdw1C60pmAbrUoUaQnUztqnPudXrU7bHLWqgSVlOY+6wNEmc59JYntGejsz2P'
        b'gtwWtpzrY8qnVpXnrAqTU73G9ISqtriqkuOqnHJcB6touQV6RKgVJkSvZc/cBJ8s7bIivZHwgSe0YrurFf1wK1rzYFbTdshbK3eS764u8u0IrmkTuJHvJxv4dW3DhLU3'
        b'8Av5sM5hoAW2pMNa9B40U+AGPAs2+IKN/KLzfnB5LjiJGgarYEMpVYqQ8zxxHhwI9oXD6kT5YnAES+6xHI7jxiSBDfC0ftXcs7w38yuvN/esftn3tlTCLfUdni+tPSKY'
        b'GLYw+qx13voHg/3O9qxdIt9pvm4ddqAodMC/Ns/I/HlwsSL9xQtC35AhvzW9PfTTgcKtKycWvzf4ysLlc8Y0vvxx59q3xwR06cZM9JV5k/0TFnClxEUSt8Imd7JISGIF'
        b'uM67dBw0gT3YlLoU7kp0xL+9xoBK0NCLJ3eX5Ipkebjf7FafvxKwdTFvcjk4Cm6OxOtZDrMIp6LBuWJwlNdzVk9Aykr1IqnHygA4Aup4o8pOpBXfakPVVmvhFbB/FPHY'
        b'WEQtTc6AR2BdFD7mgIujwfXSWL7kW/DKvEhFArzSszWW8lpwGBwhzUoCJyeSKHqI2joC6dUzhfBSMenwwGwJCbqdgIam68I0TKUDwUkWrjd29wjc9YxkVWvINZYUmQlZ'
        b'7eFJVntJiGOGN3FrJGFP2xE3R24P2vpMkfccQU9baSuO8bmLcS6XlLn+7j+Zujoa8P9AQJqQrzbkaXlfCKdI40T0NuISknqeVVIyaJc+i4DUcThATuWQX4TwPNyZzIsv'
        b'ZoGHAKOO1RvWHONMs1Gy/WujfF+JZMqkQdzt+b1+2zU7vTzOpzI2/u1zwn96F6XvHZWz+tRPMf8aP6e4y9Zua6wXy7nPv9+xM6QUsDmTbq/t1v1vOf/4vmV8zfzPvvvb'
        b'/47JvlO0sjE96FpVg8yLYNr0xfCiQ64ANtBEBIswsJXfXbB/aAE2CiAigjeLghPY2dgP1rJaUJXA2xeb4dZFLsAGR3zdIBtuWMLbOC+shJWgOkoBq2hqZC4XRYMLYEsC'
        b'H+8Uu19u5oOCJqeB2qiE+eCYS+CLhgeEw8HmaDPexuM7PAdWJyu0YQ4hpreKN9zWgOu5jkEERyVO4acTvMg7p10Em8Ap0sGYITgUoUPOgeeiSXahl68nMQDN4BKiBk0l'
        b'z4+W/rkE2LKckNHW4Rj/RXmTgBpB9PJebZCiTeb/huSDwxEf6QA7P/HAzqc0RMbahfmFJrNeY/dCuGA2YF5vF/I832MnkCcGc849AS4M5og7U8c7gFiionN/HU+3Ucnx'
        b'v3EaDVZvMNa5iQu8Ouhi149FXb7xPOImoPvEiU4CkKM2LGqPvi6Md/SVzzmVf0SZw5MtBqRMKhInduDj4+Yv5MyJVWeczcM/SNZRe41as8VoMI2QZs8wWrTZ2M2HDy2g'
        b'kUuzJ6sLTPw7dQF6qSlB8gsWogzm56ZArEr/s+QUS3ZsrftC+E32gttv3vngzrt3zl//uv7KtobyhvLh1U07m/Yf29a0flD18fUNG/rs6FPfp6LPmj6Cu5+nsFScr49B'
        b'XyZjCY7FZCsRlcAu6CdWehCJ1ZN5j5OTsGGqkwBwUVOjEQEIKSVG0BBuWHJKIqhMS4VVKUpQh42TDCUDNX1hvQCcBjcGPD8a+qk1mixtjj7XRARTgoUBnlgYj3Fwec82'
        b'gO+Zz4GAQh6ftuMLPlnGuNMTFd2bx7kl07vSElTcjS7nO0DFNz1Q8ckt+q8iG/YdnNIRsk0nBiqEbwYewLCXmhvWuZmm/v+HdzhbYnqalDcqmXkbFFEMdHqDukCq0RZo'
        b'27vWPRvGya/dYQjGzXuryA3j2uHbvv0dYJyIivPzKawLdWBcyYiFPMbBW+C8O8qpRGb+jJftQ50I56smHNekIQwX6RP7dJFJsBbWZs2NSga1npg3FtSJAsOsz490nXi7'
        b'5lPwLo3gXRvBS9ku638X9faiy50OUO+OB+o9tVFPOE6EtlFux4k8Pl60U0zN6QDpCAQS7DBYFucgRENA52YkbjW95lqMRkT0C0rctOg/Ao9rF3zE+0R+8+8f8Ikl5+ob'
        b'CCQO6oDyHwhyQmIBTT2UeH01xIAgEYuIw6bBgzwoEjAEq8FuByiOADW8a38TrIFlxUgHc3EABI6T/M14/QYphAdCkPgXhTRFTy4AVg+PECJ4vCKSwpsD2xwS0yEE5hZa'
        b'DGa3CTN1BIGzxR1BYLusKqcXov7xIEe7SVp46fLNDmDsvN+TYKxdtf8lGMtDMGZ4LIy1+hs/M3xJwyOw8KU3SJfEKQdHdEB/nw5vnYfsZgm8iQMGPgHe3v+6LeV78L3X'
        b'y93tCN6I/l6bCw85AG54oRvlS4F1zjBZB6McoNbNmwc20OzFE7+TYwbwx5a1gbVtqQjWhgGbEFzQ+j8DrAXgEXwaqGXxgavazHnbnM8LaQ3o8kEHkHbCA9KeVqusa9st'
        b'x6KsLE1hblaWncuyGAvsvvia5VzssPu4No/oNcZqnKkOX/DhOMZNlMPIahcXGQuLtEZziV3stFuS9U67yGEhtHu32tyI7YCoKEQ4ImSa4BHpIj8qfyB6hZvJby26LGQc'
        b'nt9iH47BXpyuP6aHH0NcQ9pdmUCfHr49/Hv4+4n5aJxnR8Jbzo3EsGlspAo2pyJ9FamcDIVInmAV3Aw3eSyLYDyOpxwBKDxXYXljoL2zY2eGY6JImN1H0knLcGxAbJHM'
        b'xdsujAYsfblJWyrE6DwnznjQ1ek2Fs8T6PIZ49oBztEkigSwIY35QOsecHjOuX5hCezvWHlI8hbhMCW7LNgXFevPYHsHLsdeXm2djh/jcAyPzvUgbD5O8oBHyOGRT3me'
        b'09gaqvR5jknChbe3q0pUMtZxGq83hZlOQFzN4h+NQxnirnmCFmF3TSk1uSAlSxo8bxVVgHdQN84aJXgQciXv90ndZVcWTc060btx0dWMNeG7VC8NGzynVr437fTIIyPm'
        b'93wn4mDOf+SPUlf5ftXdt/T6zHPhaycMSfpaVTLur72Eod49Ps4Yn/nFmGsD9kwfO6Oy55aI673n5vwWmhV4pOhs75ysj/QXRX1nHs7WDktadM/ru8TRkb5d8zOMgrK+'
        b'X01c4v3QtKQovOuHk074dPO9uup3JPfXj7pNk1CRRb1Hwutx2ODrbu2FDWAj6ekdL3Z8C4n7kS3pa5zNO930nRAon8LioJHZ8zb6F/Avp43qGrwRDSYlzZ73YdFCfjMn'
        b'aAaNqNzqVIUSH7npDPgFNySL4EZwvARWTgJbBf0psHaAF1grhQ0c3MSXphUEvMwEYNdfeQ9uBV9FQh/RgkkMcRJOCZYt5yNwXt78Sy7Bk38cp9em66fOjOFMNvTi0vcf'
        b'9K+95ssOkkyQvfy/xcHDus8ZMFIj6JN6dULStcruWp8V79y9PPmFfoLpx0Fw52tDxmxOtP10YH9G+NSX3yyaciipZdfgiMPJYOSeDf4P7Pe/eX1r2P33pNumfni56NDJ'
        b'F3/+++D/jBOl+C2Leq3w/fzPfeau/3T0ocoVH927+ktSj29rXk574f3eJ+sGbKr8l4zjTb4HosEtcAzHomw9HqWeKRwTR5xm+k6CJ8FueLrdQccOPyBwTk+EpLHwfNdI'
        b'BT5REg+igPKBV+EpeI6Bl8bDc0Rgj58Hr0bCKmZ5BLaf4f1kw2d0b+8d/kejo7rviDea1B7m476eXKuYI/5zAdh0zATQUkZMB+FTWk65iDJr5/DKvBuv+sNBW2njaRe5'
        b'whV80wFj2y51d4TBqwxwF8BHR8HDoD5CBWrSWm2T3cFeDpwEF+AJD4LjGaKmHcFxhah5ro1AHS/ieDuJzXvjfHhik6YoCEn7aBUhNi90wcRm2RxxPCX5MGSTfD1PbBaU'
        b'/F8gNiW/jQqfuWxsC/dHic0PA3d68w7jyY4zpuNemzFvfgyP1c19+OOMolVz0v82mOHX1ciXN1WOQ8+D9/st0XbhXx7QOY6kFuokg33CHMcrbQH7GETEwNqxHnQMHNXr'
        b'H5qkAhMO93ZvsFLxapMvjJZwt48tOL+n09qLH96NDDC8fSVJPXt82RvBPx9toIaG/fK/5pHSik9Wzui2wnZM+HXnQkPUGz5bDPtffPPtANPC+zUFV09X9fq59lODbdI7'
        b'O9f1+ML71YOnjn3Xb98Py2vHdB313tghqT23H7ono3mTdW3fEcmJ8HSw43hm8XxGmwF3eAhlfzi8DcFAjbYVA8M8MXAVxeFV8SAkouArxkIJwUnjmVYc5BGnFQWfN+aU'
        b'G+LhUv/TAeKtcw9iw0cgaYZXQVUkYvVbCeIlpjrxLpsDDdHgrMcWPfyfxMjMR7hYIeCjeVvpAxTGtgamlCH3rIZD92w9vSzcTOM0E6l6en7oPKaUK8VRvwUVlJnBseiR'
        b'WOlnFRxgNYIGulQwmzL0wvG2F3kbi/ijXcg3fOyLgI+vbbhnxUeKxJMycP6rVtZYj1IJGvABL2fQnZDEzMd1CUtFFbRVhKODa0S1KIdVOIoq3oVqWU/yC8rx8R2s8U0c'
        b'nx71Q7DMgForIPHIcX5xu/xilN+O8k8m+fkDVeJducNduXs8Lnc9jWOTVwj5HOgdZcXx8OWzHZHRHUem5FgpjVc3TK14cchbhcizVls02YiJ3YxHAotZpxjmOvkDgfBZ'
        b'POn4Izltw4ijY8hExmwMml5ag2Wx1ogj5uP9cXYhjoOt0dolMw16fEOkVD7vSB7qWgM6thZL4pIn4UsavkTgkuiFz7n32y7BJ1SYYvh9sv6IjJtGEHouJi6e+JwF/rSG'
        b'QBJEnyMbs0Lc7iSOXzHZqy6m+dBh21Uq/izpuAilDFYRn3lpLy5lAmzqb/VwN3AFp8ZoYaVMYg2dTuEzdsjgMySCPd6WSgbQGOtCTdpOmx6jNvqSLmWZC7MKCg150azz'
        b'rEUWKyS8A9QJsBUe41uIdFNYyYcixJIXNQCsEwAktpfMSPU4FsXlgjWYNFRDL6KNEqxnaFgrPsqG1nAHKHxMCmq2IJhqoK10VwrzOvyGWIKFjk4Q1wim/zKyY+sBw/dG'
        b'sFynLyiQMXbaYKfzH9cz3CHcMdLDobhn3o7Z4sipGOTk1slGSEKRoe7g84ZR59Ic53oP6CVAPP1WCSx70uZdusPNu89xPhvtXqTbzsrWLWqDC4uoz5C61FKUPeBds2Mj'
        b'U5L2BTTz1NTPkrL1Ndpe/MupwwhHC58szZZ/tHAFpW+c8k+BCYfue+OuFw4ahyMvNYPT5cfLm3e+ta7Peye2NaxvKO+z+0bCsXILnes7wfuL8UdV741vCF0vSPHpVrVO'
        b'erCnvOe9IZLXamQpgfGBB/v2CHvlg1fEMQPXzZGEXy0bvk7bJzeazRNSl7eGbghLRDIqOcu8HG4dGqkIT/ABa5ybfeFNsJX3s2gAx+YumNP2pDJ4CuzgI3XWgXUkptRx'
        b'EsGjMgVukNMo0UkGnoFHQohjw1yyn/RkElYZgQ0lQgLqSqZvXtjz7xnutLhQM3wofxpAlkafpze3jTvrCM0kpvlDUsR0D9p4y4Vb/592BeNi4llndWVuf8BjZzDeGgGa'
        b'xoxH/a1NA02DSUzeBBx4tG7ewDTnGA0Dx4QrjdEdkwxsCeIJBeZ2DTyWMSq7QG3K1etRqy5QLibc/nhOUb52WYFeV5LEOo4jolgSk0jXBzSQtXYSWAec5ODVBUiXWMcg'
        b'deII3N9xUzDVwwdfEBYYhA+KwQ0qdTSP0DBGZbzNN2SMW7OeEFXLy2JwNDGtlYZhCYWElFKDFlAWiQ/lRk0FZ2XO1pJgZnun937mIdO5teyJA+aVEzeYP9doltuQYc1r'
        b'AVLQGpNjYhNhLbg00qHC+fdhR4KD8Pr/wwFDDeRZ6dw2A4Ztmrqe83ETE4ENnnUInH7wDDsIXAdXPJzQXKd0YU6ooRFlR1LUsr5WxGPNmPKz5QySJqhSlj/Nx8ogOs8U'
        b'e+MTdIrirDQ+V4dAokBlD4seFBM7eEjc0GHDx42fMHHS5CkJiUnJKamqtKnTpqfPmDlrdsacTJ4PYPGUlxJoJBDolyAclnF2Ib9MYRfk5quNJrsQh6CIjeN5v1fb3sfG'
        b'8dOTg3tPjpolLE9IwsUQg0Z/b11yTBxSs+X45EV+mrqyI0aAox3PksQBLhrawYjRnLzkohO08e5jACU2jp+HAjdAwfVHd5mB608ENxNdU3CYjV4KDnYc9JCcQ0y7ziFG'
        b'bXn2QIcU1dHRF5yKHFEB1yOk2eXcmgy3zkz1mgabU1aBc9NhM2ie7gvqGCocXuYWwy1Zep+f5bQJA3rxl1O/yc5APEdN5yK+8lK28PXgudepgf/ipr8aIWN4ZnAyBV7G'
        b'p9nWweooEeUVy8DTAkRSNoADvK/M7oBxbbYbst3A8UIFXP+4g4T1psIss36x1mRWL+ZjQZDjVdxp+VLja655YTo2cLsZLXHa4g6J9EZJWzsA2A43j8GRruqINIHarFAm'
        b'who0igOMglJ4cpUSXJzs4WPmaXlkHT5mbnZHNKU+f+TAdCwQ+Leb0k4qsnEH1s2Fp5MRi12NWGwdrOEoYSjjvRiu5YWLecGUOItY4EatnLiMIjH74LWeoCk2BjTFRFN9'
        b'qQS4VqSiwe5YjhA1NbgBtqKPLTGgmeuLZFrYKALbabwdHV4lgebmgvWT+f36PnAbpcyRkZqSZ4ZQOwqy8fb7Hlqx45xZvSmcSpl7AL/s+0NGCUX8TOFGcBGWkVB1I+E6'
        b'UEmNBPt5s8YcLzEVXjyQbOEfLQnky+g+EHVZ0IWY/b4fG44AhZy8i6bkQmFyYuRIcEoupLgeNDgPboWQHP2C4qlvl4hoqig7Rh40iS/mz8ox1ODi/+At7IEb+hfyL30L'
        b'hdTEDGI9LPhopJ7SX35vHGf6CH35aXTCpPo7SS/ES9b/rjm6N25W2ooPurzRq5T5FPwrtHrNn6Q5DbaHk+7OOzX+5wO/iL/bPeJFS/8w7jfrvybM29f9Rd/rxuKUUQsu'
        b'35uamR/V66XIrut+En1/bntDZKj+zctF0zYP7fX7P3c2Z+Z/XhlzfcnOhCtf//iW7J2iB3tejrb1m7loxNTXopoD/trcFPPPmX+vXFZ5w/rOMlUGnGq1b73sv9N0962X'
        b'M+ZulS07vvynxLmjZl55+/Wkhw/6bPhkwvZFJxWNBU0TVMGKfzYNK5Bv/S7v/V/+sRL2FN588dH2n/8jOvz9+Ouv/a9MSEQ7NTjIJDvpEWgowmYIuBOu47F5ezJodgl2'
        b'cMcUh2wHqkYSsS0DbgcHI8HeXkr3qGcauINYNrv5w63Y/5Z3vi2Ex3j/Wx24TCyWU8ERjmxIwBZNUDWjdUMC3J5LLJbgaK+eyWTXMjgKNzEL6bHwUtFzxOz+L5gyfYsQ'
        b'59FmIRo0LC56EKE+I9pSnxUczRs0OdqPlSBpUoIoCEf3pRmyKTiQHMMncWwmNr7uolR8uA67t67QmKvNImfItZKuPxJUnTG+QVHugT1wXZYOKV1tO4tnJ3Ad7o1MkEcQ'
        b'b2pM8C5Fx0ZzVBjNwQaEqFsHgXME8cF+K1yPRARfb6oP1QdcnZTr3A/o4TOE45dX0PjMwEqkP+GD3iqwpiiwcsb/096XgEdRZQvX1tVLOp2VkIQQwhIgK5uKyhIUiIRA'
        b'ooAgoLZJqgMhnU6o7kCI3W6g3c0uMCigAq6ACyqigqAzVY7LjOO4orbr05lxXGfUcRl09D/n3KpOBwKD88//3nz/98hHdd2qW3c5995zzzn3LKVBC/yXYG+1ZHOZkKs3'
        b'5AkKO3hSxjVOoCOiIprfLRdZAFjIJar1EWkHPA+KOwUomdG9Uk03djUevhAJLYrimcmY0SAU1pviyXULOpoYw5PIixPsHHhSt9Xc1WWus6De2wpcBlPl6SnoKKNpxJil'
        b'va3No6q4JcQk4nXlmBTwdASAXMAi/E2dnpjd70ENowBG1VzapAQWqi9iflHxHB9VFBr4Mt6/FJ+pzsS2bBBNx/Qky8BpCBNSQL97xCVr27SN86oxIHIt8hy15PRwOizg'
        b'fvotkvZEg/6QdkO/bnRhHKQsdhGBEykSQc0mGRsG44Vx3oFAxjh0IgKZJHCCWg9jKygS5BCDIoYzxuiNIRHHkEqYB08pmDC+h9ziTE6xEHEu1xwdOvbiio4Wb3lJBdF3'
        b'Tb4F4+YPGHLJ0PmXwrWkCO/LiysurhhP9PJH2FgW4pVJpYB9QwI6Jvs9dWrDwphlgdra3hazoMwHfrytS2FciPKXYiLUE7O2oVaW6otZAI7wgc2s9mTEdyr6PoSv3Wbm'
        b'HaIp7BQl01kAuTRkeELiyWOsdjipidwKanvR3YsWrWVnQOTo0cpB4/WdPu0G7Q5tVZzG6HYAeSMNBpDdQiaHhDhjINQONF1RB+F1B7+T85cHBQUI9SDnRqMWQR2PV3oz'
        b'KSjAU6EjN4hiyvQQsSVQntgbBobnFk+dw75oi3+xgX3hyw3y6gZ6t/rYdwbtItXEeMdRoaCAxgPAR5P1bVoDgbomL57yeLyeFhgFzxKP9yQLL+ZsUz0BNK1EIN/fBVs2'
        b'tfEoSSaLhFTy2t6OB2f6w9r6y0uGTi0rItZQW81gzGO4NctI/c6hA6/s2agZIwp3HacDKuLmiR6JAtoBbOdZNomL5EXWeTZ4ZlFkemb1WBfZFauZAorPCmgMTZpt8xzK'
        b'AAyOB+kkxbnCPi9JGWikkxUXpJ1G8DyJguqlKKnwTXK3Z2lKOjxzxZ9ISoaSCU9SuuXqpWTBs1QyZebmpSmDwiKwDmisbJ+XrhRSKl/pB6kMZTB8I0MLCpT+kM6kWAy9'
        b'aMENiSVNhiHx+ALnArMVn3SmDHCmiVS7ZOwUjZVTJPOehXSAoQ/RsH/0E/w7yp8NhP05XFcstKnx8U1YRG5alBT82d9W1+D5dZyBEjrzEppVfmzG4/g3aidupshbw/Rk'
        b'zD5Zcgnq54RVA3ULejbjitnbvHVNPjdkeDahAb0SGxDP0a1mwaw5nWPWY60ucwmaVnNCzOJGvE/L4ARmZLhMXujiHTtTE2vGj7sNS7xSJw0LrvF46DOo4IuTA50qe7Wr'
        b'm91YmbjUty0+4ojlOy4iETVvxEqdgqcsLDZqUFSEZkE9Q0HpgDCWW5wNT6Rm2Z+tWIIi/gKm5/EEBZ5Y2VdZnJl3DpSPUYINwYyt5ig/LMYXHxXKh0EPyNEsLlL1Mxwk'
        b'/vKjlsuLQ4V+3F1ZWGkHcIhqwL+0CXbOCVyXYQN5SJ9GH7WdSLbsBgQDm6+HnK+/IZqaVoRUbBR+JhfDQeR0m4WJ39TEPVSKiZDLN+cgQS7ARPsCxUKG9WLOClE9iq2w'
        b'+NuBSkACwaeY2lrY+JgjPtNPIPZXMaz4H0WDMcRmd581WOK/2MAFXQ1Uv8fGWLGwOiBhElqo/oM7IdH0I2KBbk3LOLZpUNpxqCaulhiByRSRkNCI0PxeBNNkjUBt5c22'
        b'YqjnoCnPwwMFn7+lrg1a+FO82TLzrm+shZjVw9pwSqrHKi7vz0TDLpRj0bf5zvTEfrDiewbycNYNId4NId4NIbEbCHKexaJmHaH2d+9GE3oPCpjAPwsv0PlTU6FWoXTu'
        b'q+79SD+mH6z8bsMRFyTh0VsE2hkRoR/FJkZQC5AAYWGaQ9AXpAFxDQcEYzKJxppGccZRfgIjByQVN1o6E2Q9S3K7gYrCcPJut4mxJnP/3KmiKkGn/h4/DjKiXcM0691t'
        b'sXYV3vMYXZo41cpP1jc2Sr7i+IhWGiMK+x+NqGiMqGTmNYIPSTWqyBvkqTm2FgYGNMJLGGWAhT8OC7ELFoTCT22oLYYXWSYtM6CCYeJdx0EmXtVJommai2uWKabraee0'
        b'ud31ra1et9shdW2cmd0rYxkM6nxWfCxMHoPii6PEmiJuc41I3PJIvt4Eu8sNwlozqnglgOV9Lk4aLgNk3OQLxFKQCFc8Dd4601I7Zgu0sgNecz94nxqNA5HL9SRxlFUP'
        b'BtBxSXGc5TxmjbAMlcc1niZSQbzxCk0WRVgjEePDM0UEUzwuNYw4zYeWbywGT8zu6WjwtvublnhiybiHuYGDxBr9X2HTCqBjPv+4AQPoBBVRLY9YDHYgL2wLZtdc2KsU'
        b'vLzbU9dUdNiTLpnHAySS6L5RYJviax8/jrMaR+DSBCxGxyLcLkir4VLWLdo6JJjzwJfvxINrPoe7WAhZQnLQEhSaZVWh9WHJwVA9gn8Wu1/A4+9Y4w3gCBmR+GJXUGbP'
        b'F7vmcB2lsKok1KaA2vKhTGvIBrXLQSvUaA3aELhBa28OcgeJUbGG7EG7+niQ998fRG0MO+QQx3I+KWhHKsX/m6Dg/40CvYC88HWTKT1gZ9O4OI9aBiKJVWSPOWFNAMfY'
        b'5FVguGPWQKtbaWoIkFIC7QewowRgXtXH7JgRF5CfSEvG5qD7yiIH22scDa0+P7Oji/EKHmdAoTG+Qf0LvhUaFOasaar58Qk20kyotLdkeqVCaRPxlczpXKrg5DMFxgmh'
        b'Uo+D4hpLx2y2RieINERS2ApFzioSKiuL+MqirGPVfqk3d5q9UT+Od+4LjnHUyCgzygDpD9rpCTS0zxBeJjSkynhJ4o0JSB1JiDZ16gK9xOBT2BpNNNabTbRJTotNcFpc'
        b'ksuZKqVKmXKmnG7NdNgkeGKhQ8Nh+r3aSn+Ttgtjca6Zrq8pWTy1tMbC5UyQKvX7tYOzinjSxU7XN+iPMPslsl7SKZwj5i+SuWJtz0hFnnV6bRE7WMvT7tTvq46XyI/Q'
        b'b+eSrhD0u/V7At2OdRBXkKqSK44fgvxaNgGZg4mWumaPSZUIXVovPRzeGkN6RheWJaF9rr7yHH9XU7S79Yc5B6m/TdQOHXc0hP/8s7gEZjeVwvOhBjmwtsBESsCm8sxL'
        b'1zwWiF1oFA22VkZfXZDHqjiVZPi1KS4lZQX6+mI7fVrMOam9pWWZ0dTjyWPaWlDlgvEssOHyCQwl38VQMokCXEWSLkiKecCofsIZm6n6KWfwBbA34qIiXpPN2pcIYm4k'
        b'1H1xsokWnsyeHcsRrYTLeClOI8l8Pvzv7JXYm1P33bKQcWEF/An3TDvQJawhk+LDyXdmdasunqVnssw4qCSiw5hPpkSTaqzscRYxegtxmNt9XkLV2cf0NJ6p58rH0xAq'
        b'PPB9TtQPI/oQ8Lw6KEJAQO4bmwUDLKCMTx2JA9ituWIC/oURogFEiBFp1I0UPLEIjrDN1C56x0byNhdJ23rq0ikRPAvwyLfErOcEA2h1u70en9s9MwGGmcdUSBl6lhVg'
        b'NwLcAvPcn1CBhDvKiWksfOt2z06o77jZSTlOoXeVJ+kZoe25J6mFkXLYZMexWwcuInUAjuHA+FYwCC+D4/uB/Z8MaD/INMYcUJvokG2iU0y1A6oXSYat36k9qq/0FyGe'
        b'1u4NdOE9Ll87IA2+UL9B3za1Z6yHLrtMrLdJXCQukuZZPEzbCwV4kkdaZAVizUjRGTxiRNs8GxO5ARZkWNFOojMHzWJbLL22fpGnIUD+6Qwo/Wz5EO2t/0w61BAfFLGz'
        b'9/GVnrqQaMWpC4kWdm02p4SFGk8JC9H08CbMsfweunMiHBQPZ4+Ol5alBjiD7zL4Twk40GaHOpzp7hI2EoN09oANhLcWeKsYmr38Dpn4vXmQw9rF82E5XZ1KCCObwMnZ'
        b'iGejOR5zVAFn0MF0WP9iroGY6xyiFNsDhnZrnPP9OcitVYpLpQQg81z0H+VTJ4aZwUAmHbs6h/CJlBwj8fK6L9Yu8qyHmINdVBiWdIlkoDGbxCgwp8hON27U71H1fbX6'
        b'yqnTy1GnbdW06YvNZTorHxbqudpd1oHaAe3unpdpbsIyJVKEDgaBPDGMnGN9zI6bSGkietKc1tra3N4WP5W0GLMlI77yjN0qAmNpHFUAmufjOMnCqHYpsKzNo67BW3tc'
        b'/naCvVT2Up2hLpYRGKsBJ2ldOfugB1u7sng7jlsrxfCq01wrgAWRFUnVr9ZXJwBZu7sLEy7W11aVlusPozasvq68DIbkF4sdelS7Vd8q6zd3O1KKy0HweBv2cI4kG3m0'
        b'onjkl3YAp7aTtOvV0ghyfVxERmY2wtG9ZadJesCcphM38aLp02DyICMaS2rtmqHEf//cKF3l0PXrpLhmF/M8RceZpFV0m/6Qvl1bpd+v74fVrD+AAeGu0R/U99i6zSzZ'
        b'nFmXJswspeu0RW600DmPfZ5ImjsyIHo847HBJiDRqY6oWBUbksOKXXEAuSsnnO3Y5llpO7DR7HTFnMawTwe6Xq2p7OZaIw7u2zlU5GkCMCr8TSKw0aYIahDQvHwTKuAB'
        b'q0widqSSBXV1XOw0PigYb4CwyuGAUpaQ2Q2Kfh/eUVrKgdKRyYZ+MCGW0JEXFCbhibgFvrSYuYjlDszhTHHkIqER3qzledMGUkYpcClOThJT9cU7Io26nrFjvpjDTdJX'
        b'd53XyzAjEgOmpwXK+A+aE22qp7Gpw41afcTtxASf/9RkW1jgLyTTsEwQUNNCwDmBnpgl8sicSgHjnMQhx89uaCS6iHdz/lu5BL2FB3FAEP/DRFgg4fk1Sjt4oNBCYseG'
        b'IJ54rGTSDjy79p9JEhCJZBf5Hb6AEJTwhJsdDSrWNQjq2aY0ZIek2GCPCdI3OIVoSGC1ycthqKmMGnjuAOy0CfOwN8ZzWnNoNbJcYE/mQI1zuCCzxk+qiVlm4vlHTJzs'
        b'U2JSDYaitsyu87Z7eqZB2OkYymoUoVk2pGpMX0FQT8cxHZ2AiXrQuSR3hw/jcTv5myzrDuOGVt8SjxogcYM/UTWCeaGEIkmeGd9FTbmLBWVaGCbNYwhZ/BTrjYldvmOY'
        b'g9Cz6PcsjllaVcWjosTO3+4NEN3c0iVMOdmJvat7C/dIhiSB450G7+CAGSUIqEGaCfd5aCTlyOY7+5ykn91Oz+ICQWzKAlx442n2nBESgaIg3RayOSrHGUaSZXEnG2tH'
        b'UIQdCjAk6k3gU3w2h50LINGOdDsKDgFeHhhrm7vRizoLPoKYKQocg5Adh5fx/MmJi3Pg/bNdnJNkHAuQ09RjVo5R0XE7B80o9AyWYHsF1yD2IhsPZoi9hzW1E7WH4R2T'
        b'l8PbAN2JcDclAIgoKGTBfnMNTyoFgLJ28kS1wSqBNaGg5M6Xaj7BPHhyqFjYHTwBiGaxw0+5hp0TCm43m19ZF/qafa1LfQXxvbxgQKF/wFH58kI/HiPKahoC61v8SGYY'
        b'TB2BT3BDZMSa2EXIqqP44xZELNntQ+0bdJUMBbyEIM1KmFKphhA+i5eFVL4ztztoEz/thpmw9SQ4UrjEozqaMbgj494ssLsmLiR1DGY6NobVGOId/IYs2oJyUCJEXwqI'
        b'XmKnM4tgG2iEkm4REN2bfIisVvLG1FAr8ELrj84mgAFFb+NAV1oThCk2U1Kq9sJla2eyUehLwnLsWayJHqLe66JtAUYiCi/TCVbHoW6jarEGloC9R66zIt5w6sJ53anZ'
        b'Uwxr2kXhAvvAXd9F4Wb1Su0HTKiLjBXHaquu6BK46Q9M11ejh6P83pJD26I9dtrQ4/xY4z8KhxqnPlKIvTSpDuZU3qQ58M2x9AbSwQa1QRokKHpj3HxqzDattaG5ssnr'
        b'qfmQVfVeRZzq6Hagj8MRIdYTJ5M/MyAoPC07xhoK9I6O7bJQ8iYFgXFyW0j+JpMszoqGX25bXNPnaAYGey1QWj2GO3h063XUWugvR600HCo6yJab/JiP1lTMWlfvx6Pz'
        b'mI0015QmNWZFRe/W9kDM4m6hgCgUQzZmdWMOj5J4oh+TMId6Ad8TpYwT4cuuOeUk0iCdyAOZ70wzwXS8HA8RmsOE0mrOVGFEIRYatHUsWZYaweUGKAjR8hzON9swEV3C'
        b'A3Liuc4zg7CkAH2L6vhr8DtZnUICL1YO3yypFwesioDQhmc2xShH4RC5oUnZXG5xKjCaEoP1TEjNMWkwS81HaYTLGlrbvQoBuq6BHNEXIIA+3LoF/+2umFVkB/YFQEng'
        b'iVlamgG46vl0YlQ7k3jQmMWjqoBzZuFD54x2H2Y33vi9Hk+bge1iVthiqKj6Ey7hmIS1/yAZJ3cc2U0KZN/vIHcnEo0A2vp2Jsdhj9/0bHhRyjHxiDpYofkIs5E3Ya4O'
        b'BvhLJvzj7FslEI7YFTY1LE3+eIctagvcG8KUHji3dh82JNmSIPBFm5HOlHhDWY6TUVGMQlQSBL4NJxb4ohccD+CwDEuX1CM1YUbSy54BU5xQG05JQ8YqMBkricgBMHE7'
        b'XR7Zy8sQKjNM0KgzuxrWg+2K2w2oFkWHWZb4ebqNqGkYuvSERhrZumnd4n88xyZjcxq/LFO8hcBh2od4RJgIKpFaFLM0eFsNB2imhobk9nQ09CD9BNQCK7Zv4oA5jl3V'
        b'LA+y9dU82RD3tFEQZLBGFAJxqgcvC09FMjkVMn1uMqM2yeVwpTlROmmlUxiPdq22HV351E6o0dcuMSJDJy8SHfq27gY6VuOXdva4oAO1oCVgNOPCDlQ8nCcpqWEWO0UM'
        b'y2Fbo0wSSDtsDGmMNaXoJ3gWY4dNgnnywhOZRKZ0QVF6TKo8f1JlN3QXpy8mcSiJNqgCOrpG9s8cMviFNkWERRLa91LaoggBmaWMTcG0hj2adP4yrGhkwZJC/9FkSBgx'
        b'oiFpystW0nii+8m2ugWemNPvCbjb1FalvQEoeid+7Z49ecbMqtqaWBK+IzelgJ6S3G4jjLLbzXSm3Riiw6TOus7NTjKCWPfQrimeTmqksOiTsdrjGcQTiVANpYijaTOh'
        b'FQUtdT5y5YieSxAHLO6azMwVwrHkIvYq3v5hcXQgdKZTM7q9rok3BuVZdhMjRBLGDBcaurAOCkxis0hQL40AN4p3qFsN3KQIHChs6suZJjbdh0Sg08XeHKr80lPY5nfI'
        b'TFWBqEtevSYCNKJiWS6sSw1JwN9ag4K5aV3AzeAuMjWWZGaz+BUuS0dh4czJ559T8BV2lWnmdQC/7yBiPCYsrTemQUyG7b6tPUDQilmU9pY2P8mPSIWPzvFilqV4vG7I'
        b'5RgaI3jSJ0LjwlO3DlaXwiejLKb+MFn/ykageScFmSe/yUkEf9awmH2Kx7vEE2hqqFNHYxFksIiD0GCKk1ISR6SNZ1zQTtQX4mlMkAInVWKAt2isJIIv3QPPA1S5iG8i'
        b'fMACvJ8lk0PdSvTYwNJ9WNqmyCG7Yg05mFwglLSe6/gRxjuJ9DC/DDmBvnfmcKHkoF19xswbTIbRRKnDTYo9lOzLp7QD0geVJHhr1m/D+hcHurcn6AwCqZnNNXPqe1i2'
        b'4uzN5XBt70NJrqALvU0oyUFXsxXvgi5WD9wPCDrh6kJJuoE5oEzFFbRimYoYskMrXKwV9CW8R8VnVie+R+0MxRq0BJODDtj87YvwmrTIqaStkaE8hxrAXCiuCsoMr9V8'
        b'hE6wP8KRmPURjvmH4aw3nv925tcVlSTTOCqOGzeOhi4mugFv8LMYV8gXxPhzY9aJre1qE6Advgo1dH2epe4O9rOsKJlprDtIx9Tb5PP4GTpqqVMXNPn8sQxM1LUHWgmN'
        b'uesBSzXHbPiwsdUHhKza2u5TmMTfi/NVavB4vTHpovNb/TFp2uTKWTFpLt3XTL5oVlEKm+N0aC1RARLZhlj8gWVACCdhA9wLPU0LFkLRrDUOzOD2QnM8xj3wrlCFRfVA'
        b'K2JyPZOR2H3tLW76gunCSngPTz0dAXr8T2MXJzENR1JfPsdiMBGcESnRSecRqWTawCIhMhd4DsNzBnnSEPJIJCfTF2zZScayQz0kWnQJlRwnTaFdSuW6ry86tcmj02Vk'
        b'ZaYqQpRDM5+ASKwS7p42lLssN3xT5KChBK/IQT6LafRJihWxWcBiCD7lOD8skvjTRqSK/WjuuXUqmvUWjGptPKsANbQKyMmAv71F/QrnUsmp2DuXlRcMGlZS2I1wiutY'
        b'IVIicyVXCHrAOH3DUKnRlMShxqdpqpTbI/ODOiyt5m4ic539CLDY9FFn9WSk9BEtEKm40F9Ma6UGmOQXOEPchvYvCulUx0ToacxFM7sJmPCGVm+rauBwVrjJnr3UfR/u'
        b'7mby2Xg7d0Hrmyym3AkdEZHVHEr2DQxsFEt07OUkkjQRsBo8MV3n5w1Er+7gjWoSBAA/24tRlyigCUoaZImLAlKtNinblTmUwivnarsH+JPaFovzL+UEfSvfP187jIpl'
        b'8T2fNK7EmpoaVLUSmSVdeLC+F2iKZn0rmtKVFeNLskjtey66w/qzYucu8+6fkw/NqGxqWl8o+VcDxRZ6+rrps/4+J2NB5s3PKlsGfTpGElY++sq1hbZd2SOun34rP+KF'
        b'W74JHF67dV7z/EUt2x6qGPThoRv6fdfvrxWf/WP84y9/0/boc4eWvnuF9bvOgSv73+l/ckL1k4/mp2XMGzh4/7RpTVdnf+wace+F9ZUfRucervr0pQEPzJ8TGTev/zcf'
        b'h+q3l6d+337DmTseiS4/WJX3UsP79186ZO2fx72/y5fxdGD5mfc1X/DpHzuGDPN/uekvGc/s15/PfvfL4LYnZ43xdianLJv2yOHN7/7t72OXJ31z1pG/PtNn47NDfzn5'
        b'uYf1ze8+mzP/Dx+k/+nT72//0zNbbkjeXbn44qd6Nfcd8En6Z9bVh1Y2P3XEmTv+iiH75hy9o6BkhjKt6jczrt/zyh+GfvxU+1sL78p5u/ZP/V6aeERUfzNj1YZHo/OP'
        b'vPbyX3PHhwY/3bdPxVPOjWqeZ/g6y8zoPZ8+PKRqi8dqmbsx7dln+Q+nN6RVf5ZaffabjrOrfmsvax44dcdVnqObvxZCOz9/7fCofo+c/kP2V+Oqrp+54bwHB67zVEyt'
        b's9z91vvcoeenDHzhntmf1a55wnPv42sX72u+i/9RuXjr9a8pF8hKJOOG16u3LPvmdf/nQd+S8ZExjzbf+cHm99dc9uYrjz3zaOkj7XOOeK55buLzS1M++bTtcK8PVjTp'
        b'eijzzfyVQx6YPWG+I+XsQ3ccnvLI35695s0vhj72zgehB1//5cRHdtqf/qR+zfinY78Y9/muFV+eddeW+x87o3fJo/NfPfP7gd6DeYePVJRW7p3/+pIj45vLns28d8zr'
        b'7UcuKNZ27X6m9LFPC6NPv77v4JR5P164aM81Q9aO87Zsv+hCS8fKPftq537fS/128Xvet48seWPx9v964Y3HVvf9/QWj5jXevOmPvXIuX9Ewum5hr8efrKn49YKHt532'
        b'9bv3r7x00x1Xnn6w6PcHfvr9F9cemDGqYdToj3Y/M+rID+nuA5943n7qjD/YP3N/0Oe13+5Y892qtA/u+brs8TEfLn2qz/i9fTdO2PzT97m3pv4y6dKj15a/Jl7+xlW1'
        b'iyd1LPt46Z3tR0t/9e3tckf7x1f+LTTTv9V/uPLtK0Ijtr06+u19q/7yxXUH3rno1e+e33h9WecVv5zf+c7Hs8fdcU5JzZVPHR313NcD33nx27Xt5758zr5Pruz73J+f'
        b'm3vri69+6W0Z9ca7n165PsN7we6XR078xQ8rtr9d82no002L777twRfH5Tzx3opeNX+bPa6l+P7Ot0b8bs6SZ3684tfO9ZePfGfb81vuenpZxivfHLpHPRh+6/W1s3a9'
        b'8e5fr34u5eC83z968Q9X3r3sx9/pY/720t4f+aLCB375K74oiYKj6of1rdo+9GZZpa12LRw2pRRjtqdr14naQ3MVFuhkg7Zbf4R8otaUDdbvKMZ4RPsFbTN8dyOFYdUO'
        b'awevYIGU9WsGDjWjo7JIytqWJMpUoe3X7/dr6/WretBi1FaeSXVpG2eJ7DTUPmWx/khpMUolU7QnRLf28IgA+pHSb2keAe3QorU+bW28JDRAxCNjbS3zCMUOjYNnOyS3'
        b'diiAvp9U7S5V26RFuqSei6umV5fqa4qOP2y+strBaddoOwIottCfGJd8Il2ANqupC6A/qF9L9VzZoW/3l2PIPW2P9oS+rv0kh9pL9a127eHaDor2IF2g7+pZJKtvOEN7'
        b'7EJ9JQWsS61uJWyt7dfuZ/j6tCuB+Po5W8M/2ThG/xsL+//lUtSfbd7/6RdT1ORtrVOMwIJvwYWrk8li/tT/HKLL7pKc8JfpSLVlZWRmCvzQ8wU+N0vgB5UOGpOX7bJk'
        b'T5AEgc/mz/AOXeLkbTZMDU4T+AHwP79A4DNl+G/LdQh8uiTwWXLXr8uO95gakIcC1ywn/E/Bu8zUfN7R6kTCW0i15A7I5J15qbzD6uSdIr7Phy/zeOd8uJ4u8AW8s0bd'
        b'HZd8JXpQ+d9Z3MOli9RGoF3GmSTsrR2JThVY0Gz5PNgbrtNWMSd7tdO0qLbOyrlyxL7C8KbN7/6B8w+G+fXinaVlG571vTk89bqqqs2Hnv7+89ej+96IfuadejD/qPPw'
        b'N7NSi4pX3XDaeWeFz/7l7w98nfbp6D/vXPeS9eNIsvTX78+8LSfZHuo1tfKH8xeeWzh6Q9a08NzGg88JLze4tuQ0bvxoVOv07y4Z3jz4h81fDr933Uu/Sf/8gnO/e2/P'
        b'BI/7wU1zznJM2/Hl9hXFr1i+f0HqcyBr8JQnf/OPL96cceilhuvsS0/TLyxfs7t+61W2mZMz7jn0dMWeSb/ad35hYf0Nmxtzlu15pdeeQ2r+T+M9r7xT+eOmMz7Ze8ez'
        b'Q0a+P+zF3ftL38wfdd6HS7Z/+I+r5u6Q904++/39k5aeMedPFz+fu/T2W/Y73rR/e9+TF14ysOjaNUfOOvvBI5eN2XdE2Ta3+YG+FzV/Fe174em/bTlv2Zic9jnj92cs'
        b'GHjE9/6eeXPWN3/4+YuvPFj72nOdY1+YuOeTUPHHaX1/+7c/rOm45+lZr1pnvRgODPzp3adW3Fe6bpdn2bSG32YcvH/sHff9MefrLb/r2LNg0wP7y77xf3np9xffM+6W'
        b'11b9aeyB1pZfbf7jxWMu/bg6/ejKvO99Qx4/Mvqhva1N9038+K+h524b8+olB5646elhU19465vH3As2PPfN72qm/CrY/NbNt0e3eN/d/c7L3/ddWv/TjqN5taGc0O3V'
        b'tilntv294sv1V6/j5v5h/Xn85E0PhB17du1cK29duHON6yAMGX/d60/bGvLeS83I+6/sIWf+OufOG/8rr/eNDVcXli++tvmt97L6f57/+asTkt0PNld8MXrsH/ftfXLB'
        b'9Zd/Z33l0Osv3DC+aDxFhtfC2lXa6hr9BmNWrdZXlRrTaoY4Qr9PoI3wshztNshwn7adnMvRro550rRDorYR3aczFy8HtEf0XwBZYoQyHKVtomiGrdq15IOlSntMX1Fy'
        b'5VnafaUybJRX85edr0epgjn6dQUl1WXF6G5IX0cRzlbP0fdVYxD6/jMt6U6OHFjrG7VNcjfv1Zefl+i/+jptBSOhrg7oYf2urGoMer+6CDOXyFzKaLEZKJ4N5G5Gv1m/'
        b'2aevGjZFXyNyA/THpSkYeOGAFqaWAgW2XttZ3WeGvnaowAk+fvxUbS8LD7JVuzYTOvhYCfrHrrVw8gTBlaNfz3wbHtR3a3dMP4sos6FlPCd3CCOW6uvp5cXO4mp8UYSh'
        b'0G1AiOzgBC1cnUcxp/Rt+vV+fdUU/a7ppcC/BvkK7WptHatxpXYLgP7u+frt+kp8qe3jZwn63azGtdDmlUP0bdWJvpoqG5lb4NtH6lv1Vdomff0U7V74MsRXFmqHiWgZ'
        b'oD84A6Abqi3nocSV/Hn6bR0E4yHagQLtbnRvUFQ8Rd9cDaVGtci4aaQNXXiaZZLtChqyi7VD2oqkmrLi6rJmfZtjqL5S24shKHO1w5K2FcC/h4ZC263tuJicXgFIyhX9'
        b'oSoAG5CYvRdKIysqCNgdeiQIgLlWuwGD6AnajXxlMQtuWQJk7o0lI7Wr9cgwDKO3i58z9XSCV6d2swN69oB+bxUOoHAlP6FE38aI49Vz9VXVhCGn4uA/PkvmkrSrBf0O'
        b'fe9cNk/X1i7SVg3UDtXWllXhOE63cOljRO3u1FmM5L0726et1m6uZrFBa2ugGJlzXSFOUrXrmDehu3CgYfrIHD9TW17K6bdNSGLRPrdrN2eYHsm0J86mYJ/6Pv0WGpGK'
        b'Eu0+aPZu5j1i5lypntcen8ix1ZGqHXZrkeqyoqnwqTxTyGrQ7yHnR2dP0g6wqVxVVaZvTROgPzcK+q6hOeQUc+ZID4BvY1qC3qYE/MJyUb9K26k/woCyzgVLfbl+a3VV'
        b'KZTBmufSV4o1GboRsfl6/YY51RQpFFDCRknicbX3pxoal+n3lcwAghq/mw4QL6qCGvSNonZQXw8zkSKdrL2iVd8N67tKu3do0bCpMFNT9NtE7Sr98DQGs4eSr6gumVIl'
        b'cvr2TCmX13aWattZTMQDHm2zvgpXP/Ao2p36ZukCXntsuH5nAEVZ+YHpJVMtHA9TUeH0G/V79DtoGKdpBypgyeDUQpeNvVSAS1DQb1oC6IiGItpLfxQgQ7ESATvcJqXy'
        b'MDP3V7KVc62+xV0N7M7po3jOqm8Y3SrIsJq2sc7cqD2eV61fNZlcMSb4YVykb6Qm1y/qrG7UtqEbxG4uEK+dSd8PsF02fGw1+es116VL2yFO1A7oK5gj06i+B53LdnnH'
        b'tOdLpnPMVRzDzTdO1K4tsQBeXtPNjSZzTKkd5AJoC366BKsV0EoZrJFiKBb4oQ3APE4jqKyuLtP2SFx/fed07W6rfvUMfTmr/qoKbUMScpZt+qrTFkA+REqZ+k2ifueZ'
        b'+nYKjjuuVNs3SYsm6WuHlU2taaezR30/0h2Y9/T5clX1COoszJybHITyyqdMLz9XB0ImSb9VAAb15mLKUK1t0PaQw1Zit9bV4YLcJ+j7tF0L2ey8v9/ZJb20m/W10/R1'
        b'1aVFZTDcGfmivhHqu4OwjXZI35ZZjctVXzNR36tHq0qnDoPqZK6Us+hb0vTNBLLOxgpjI1tTWwSfHwbuTVuDW1VWoSSeqR+k9kzrq9+Cfn1ra3GfqR6o3WSFBj0IK6rK'
        b'TozxkAvzYWZAa5ZoO504KwFxT7NyOfo+aa6+WbuFGu2UpOoObW9tmf4AFoXBVdJ02A93ag9oqwlJDdHu4hEutI31K5fKeO3e89oJy6ZcAmw4tHQYbno3w8I0Nj5sap9B'
        b'kra8uYmKmAm8+d3aQzXVVdOLp1s5WRJsA4HtJKA9rq23ktPXIuhlmb7rIgCrfgdOoJUtp6qbZLCX//Ns0n/cJX62SyzbDrhwSYJg44/9cwBTxHRS0DWbxGMeF3tjnFgY'
        b'7BvT2BMcxh18J2DwHhv5zs/sVqaTyqM88MZJRrg2OlZ0CrLYcSV3/F+BzDOJNVM4QPULvyfQ3uZ2d3Fgpth/D5/YP7xhPMe3iS4r6V1cxSAZ/qMDDTzk9z8J13pO4RfB'
        b'X3R2ZDbqe0WHwK8AvwL8ivCbBb8S/F4Ymd3Ewa8jMhsN06L9MP8izMmH+fBsU0MtxKF2mldskaIpLZYQ3yKHhBZrCA/xrIrda2uxhyS6d3gdLUkhC90neZ0tySGZ7p1e'
        b'V0tKyIpHhIFUKL0X/KbBbwb8psNvPvxmwC/aysrw2z/IRVLgNyVI7meiSUF0xs1HUyFfJvymw28v+HXBbxb8FqLCNPxag1J0gGKN9lbEaLaSHM1RXNE+Sko0T0mN9lXS'
        b'QjYlPWRXMqK5QVHhIjmolB0dqGRGi5Re0XIlK1qr9I5OV7Kj5ys50fOU3GiV0idarORFS5W+0RIlPzpU6RetVAqiI5X+0bOVAdHxysBohTIoeqZSGD1NGRw9XRkSHacM'
        b'jU5QiqJnKMXRsUpJdLRSGh2jlEXPUsqjo5Rh0RHK8Gi1MiI6TBkZnaqMis5UTotOUU6PTlbOiJ6jjI6WKWdGL1DOis5Qzo7WRBzLueggZUz03EBvuEtTxkanKeOiE5Xx'
        b'0VlKRXS4wkcnBa3wpiAiBG1BeyNCKTPsCvcO9wtPb5SUCco5MH6OoCPqJKWSLv+krnBKODOcBTmzwznh3HCfcD580z88JFweHhYeHj4nPDlcGZ4SnhquDs8MzwpfCPOh'
        b'v3JuvDxbxBWxRYqWC1F7mMXYZuU6qeTUcFo4PdzLKL0vlD0gXBgeHC4KF4dLwyPDo8KnhU8PnxEeHT4zDMxueEx4bHhceHy4IjwhfG54EtRcFZ4WroU6y5WJ8TotUKeF'
        b'6pShPlYTlj84XAJfnBeuakxSJsVzJ4dFcvCeDPnSwxlGawrCg6AlQ6AlE6GGmvD5jRnKZPObUFLEFUyiGgbTt0lQSzLBMxsglAdfD6Tvh8L3JeGy8AhobyWVc0F4RmOO'
        b'UhmvXYS2ilSSdIUDxzHkjBRGnJHiiDPojFQtF5ajIgA+KaUnpezJFc5gEh1Ensc8yZPSPTN+RgzRs74Y7ovMgifCNdvV3AC6pOAW8aaOtaFPfrRXoX9oUUETU92sK6hv'
        b'b/IGmnxFgnoJGYUlbDsncp/kbvSRtAyVwqKWuIMJPOJV7zFNRYokQHELPIFGFY0TbJ6OBlJtIRNoPLhubYw5TdUeUunh0TlGC+BEuHOgU+WWNtXj90NK9LYuQENZ1PlS'
        b'D3LMwxD3EelmYLs+Qi2Rj27CC5kRoNJyq+IBzEr+CVDVOya2tbbFHFC64mmsQ/MBW6ObnY4yrzRd/gvi2DgmN1I5saSGVneduoCiK2JYSHfz0lafd1n8kQMe+VhhMSfc'
        b'+wN1hpdHG6QavXUL/DEr3FFhdrrx+QN+eksK6lTDkjq1K4GasJii7+jGRU9VP6kl+FqpHC8MYV09+0D1eJag42xMoNYBJSwNXk+dGpMpWMeImFjftICUu9FPCgutEHNg'
        b'AF52z1Rx9hmDHFDrGjwYrM/thuz1bjaQVrhDNYKY5FY9jTGXW2ny19V7Pe6GuoaFTHkXJobCnHchJXtUGFrULaAaTmPkZyi8BBqfLTecoaOjIXQBGuI7sshDoYt8HPKA'
        b'9YExXpw3h3l9Whi3NT3OWPGfOQ/CyflBXBOM6ACHOWnjbUSVL9ls45PwJmIFHOeEZZWD7QjygH2ERjRnyFcoTAoZOYiRAlLFkoJSxNFsU6+JOEOWoBBJahbUKXAv+4ZS'
        b'ilMvjTiTuJAlwjHVrYgjkg5vXNB3Z2+EhRyxQrrvciEoR3pBjYLvnqCgboBn+ZGsRnSxshlVsKCeDKjnPsqdDV/nYWm+q+B5v0ga5fs4kgYYx9pRQDZg2SEb5LVGMiGv'
        b'BPsEQHs5Gps8BXCVYP/gqUy52baeV8sjMnxp7yin0vtATtMpiwNKMb4O2uHOgXcUXMYG5dhncgwOEZ7KuQ6+TokkJxnWaEExkkpvk7PRPSwwgwoXTMJ3QQEwbnJvjhlJ'
        b'kXdLO3M3H1dxI7hCmXfCeDgiuVC/gPAJWjLRUCSbwQPeP05t7m1CJGj6NWNzxvl/eaTxPy+Q/lkya5zZn+GMryEU7WK0KlGrqIcjCzbS0ElHd5oi0+ZxEi2cTfSszGfx'
        b'ubwkugQXULp5+J3ogGewaoT4gkkzdiBaMK8IxoJxwTAXGQsmM3HBwFsRBy4iwS41vNsSwoErgW8kusPJbwlK/k8p8rgcwb8sGHARteWCVvWaoJVsXmxBqI1NHFgyuWM5'
        b'38JIn8jAyGBYCDmNFpjGzwTtMH3PDzkiqGfmgHKTgo5IH1iar8O0S0nicnBjFuHehfdBJy0+KCmYBCRiijF9kzAHexd0jOUWb57D+XyRQZHkSB+FjwyE/4Phf7/I0EY+'
        b'koY1RfrhEssEIhOe50b4SGokFYmzJistcgtOYlhOaUEb9CgZJjz8BmFpRFzZXMgVSQeSAJ+4enOwbJKJVEiCr0op9lMHlQD3jdDrtXzI4vsUnsiRYigzJZgSyab3gBig'
        b'vSmRAkoVGKlBlBpkpAopVWik8imVb6RyzXZSqg+l+hipgZQaaKQGU2qwkcqjVJ6RGkCpAUaqL6X6Gqn+lOpvpPrF4YapHErlYKoxBTaJMiTwg9xaRJ+IBKCvkSGRZOhx'
        b'ajB1veDfE5ToasUrzZfeOF+gDIB9I3qXNnrTm0NrPIBnBs4zKFUknwESQh6ROD0vCUr4PCiZzkHi6j1Faf9P1m1R+X8A7vjvx0+DYbf1X9OFn1BTULAZzpNl0cUicEkC'
        b'z/5kCnSCJsCZkDNTNsPvotPlVAkNg9EhlFNIFx2AtVz8if7SBaeYyqeLGKQ3V3SKyNPHcZppQEU4jXlCBKwF7HLEZuA0OcIl4DQxYqHNHIiViB0IfcBlTO+62+bTI33y'
        b'b/BcT2DcJJsW8wyMIgKiW4fsZod2YYckWBRIdQiAhtNZJ5aTmqU6GFXAI6no9pGeS0HKCd1LjmD0ClxIKYCUkhFNYwqVySOOdYN5LDUpko6LDgFFCEu0AEqN2EcD8Tc2'
        b'QY0ckBugSUDmuPTwPhW+ILVoDDZD33LdPIv0DLyM/965epucYPckCWg8JFkdfJ6IZjNsFjm6ZpEjEeioEAykIwo1YJ7EgS4ZQB9KQO8FhJfoL6U3mM7CNPlVnwQzy4mW'
        b's/TOsS6XwIYW5dZs0uXHVDcAA9EWscK+BSQp7BeNQdG/0iSneSxdAvIQ9s+OyqBFjWEkQcSWsDNZYBeBIQxZlzlQrECGb5kSF+CaHepzzIMKi4hI32RjGbgXEqPtAqY/'
        b'I5wZ7t1oNcKe2LpqArIRVgm0JTeSjM/M79nOBjSDHVYUtbVjbNACv0q8BjsKNujb2fAtPIM39vi38XYAGVo8p8tvy3GmL3EHrfH4e8h3QJcByBQzAH0tYKQWdGXYWoq0'
        b'J5nLr+jyniTGhEC9+gRyis/wP9u3RczV5He31je6l6qo/Kz+RY7bpUikH+1g3Aiw4MiO/0uRIXL+k5C7LhvGRuaCSYWrk9A8KoWnAxqXJYns71GDBk0IkSWT7S4x24pP'
        b'060uQ1SbzhdlM/kCaelO4MgxwDK/ei8+uw8ve/FyP7kSaECPLn71AVLD7/Q21asP0m1LXWChuo/MluHGU4cO/NWHyLikSVHzqVDgvWNiXT1w7Qvr/GjcHLMaToliVr95'
        b's8DbWg8cf1HyvwdkRXP+A2Tq/3v5Vw4hcE52IpMVw3kuCNKxBxAuSzYdGeDxwPEHFOxP6uHP2ePTf/1PNv7H07JTTLdK4rTTYQWKjYvwWuCUxOF5eDd2Iq5LwSYTeygI'
        b'1M8aNFu5lSMP/u5E+Z3bbazIlro2WJYBFePokgEsGfGzs497aN1N7mjwtKHDXhWPyfAkpKGu3e9xu2OZbre/vY3kfigkQ8MQeJrk7kqor3T3xZBgLTq2pVVp93rG0xEI'
        b'CpckAShCAQihns5jlhlPBwjkUNVU4vs/K7a3iw=='
    ))))
