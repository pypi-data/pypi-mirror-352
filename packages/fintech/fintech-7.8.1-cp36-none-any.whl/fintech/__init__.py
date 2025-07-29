
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
        b'eJzcfXdck9ce97MSQghDRAREjZsAARTFrbiBQMCNOEjIgDACZChocAEGBBH3nnXgHoh79ZwOu/dty217bW+H2t7b3vb2Dm97+55zniQkgKvvff955eOT5Hmes3+/72+c'
        b'3znnz5TbvwD0PxH9N69EFy2VRWl9smgtl8/oWB2noyuZSjpLkEtlCbUCrbCKUntpvbQi9Ckq97N4WUSVVCVNU3Mp4ziO0nkXiE1lNJUlpqmlfbXeOnG2j1aMrhLy3Zdc'
        b'/XTi1fRcah6l9dZ6Z4nnizMpI5OJfs2kvKtkkofh4ll5OmlGuSWv2CidajBadJo8aYlaU6DO1Ynve6FK3hfhC40urXSMhna0g0X/xY5PczS62Ck9raW1TJWogq6hKqkK'
        b'ZqnQRldSMykbU0nR1HJ6OS4X/fbOk7FKjbNDcBHD0f+uOCOOdMpMStZb2Ur9hB/PKsTF/22ygOIGBKGuU0Xn5k2kvuHT/jC+Q31INnG4PoydsrN61lUn+unr5MzQs06c'
        b'0oozBueiQdNMOdwKG2fBmug5sAbWxU5PmpUUCdfBelku3ANrYT1LTZ4thGcGgL2G/oY42hyFUt4r+v5b1QNVof471Z2vozdGqpPU36lezwnS5OkLmfOrBx8MHRFPrZ7g'
        b'NfeF92WMpQ9K0WsKPOWD8o3CWaZZ5ZEF8XBtLEP1Bs0cPAP3s5ae6C14NqZ3yFJQB9bD9Qr0HlgH1ntRfoFsL9Ay7xglY1uZCJkJ9w5/8UaXhwFj9KbipTqjVM8P+rhW'
        b'P7XZrDNZsnOshkKLwcjgxgtxV4RKaD/aJHEmRflxeqtR0+qVnW2yGrOzW32yszWFOrXRWpKdLWPdSsIXGW3yxd998AVnEoYz9sMZ3wtghDRDC8nVOgDdyQYnYYMiOkYp'
        b'jwS16XyPwoNwA9+l0fECeKwrXYhrUbLkFfp1AZXRVHGb/k/mS92qKUIpEakWxiJKLPJVrcrpVZg52kEpd8eTp0Xd82nb8OMCSqoabV4RyifhSliK0+LqqVKXxE7mb9YL'
        b'hNS/poRQ6M3o2vxMyipHN22geYYPaIpGtamB62fGzSBjDxrAtukRMfIIWBMbmZxGUwvmi1ID02W0FQ+OIaOHz8BC1B6FXBwB14IzoImjwsANDuwsi7BKMUFtAqfAeTx8'
        b'sbjBK2Ez/u5F+aQzcCM4EEeyGQaOMh1HOHMJGmP7SBlr7Y7p4CZsXqqQy1K6gvNpAko4kwmGV+Flaw/0rBDUT1WQ/kwGG6cmyxnKB2xnYBM4EGvtjdPuKdXAunS4NiUt'
        b'Btb26ZoKTnBUIKhk4UpwGV5BJeBhmwEP5yuSo5PlhB4FlB9cqwhllcNAizUIk6sfOK5IhruGRycjfuVosE+/nNQeHBgm5mk4LRnV4ZJcloxyh5tYcFWQhjoqHNdg16Rl'
        b'iiHx6LkCNoAqeDwdZeLfhx0NVyWiV0LRK4qcZPxGchpsgNU5+LkfPM0OVi+XMaQnl4Cz4JhPEhofsG9pCayD9Qrc0iC4m4VHwH4rITFwy7fEBzbEylPhthSlFb+VDFtg'
        b'bXoqfnfYfGHyMlCH2kvqdAiNwClYF62EDckUFR0jRN3WzMDmsbCeb9gWsGtxFGxIReMSLYMbe8pTBFTXXizcBG8OtmIWhsemjlWky5OjULtrk6NTYmPgZVVSmpCKpgRw'
        b'BzzYw9oL53MdPrccVyUqJgkN48a0GJrygQcZeAleAKusMpxRrd9YBXklHd7AXZARoZBHop6oR6SYIRdSkzghXKmETda++O198EgBehs1a3pEUipsUKamz8ZvRY8ClxSC'
        b'KdPCXGjHuCPwdgLldhrBJ2vn7AK70O5lF9m97WK7j11i97X72f3tAfYu9kB7V3uQvZs92N7dHmIPtYfZe9jD7T3tvey97VJ7H3tfez97f/sA+0D7IHuEXWaPtEfZo+1y'
        b'e4w91h5nH2wfYo+3D7UPsyfohzsgmqrhEETTCKIpAtE0gWgE0p1BtL8DSDwheqWSDDGCxusL2qMIRhCwGm7jUSTCSMZvdp6OMJ5SLpODGsRU4LkiKlDFgtMh8IY1GOd1'
        b'EjwnhXWILFmKWTEGbKET4fYgawgetJPgWGEUOBadJIC1CygOVNGwsjfczKfb0396FMr0TDKsQYQqBMeZKG8RSTdKB/bjoYmOoWeBNRSXTIMboBFUkofwArw2XAFrU2No'
        b'uMVIcd40OAx3g82E/+B+BIbbEeYkoeqAukUUl0SDZngC1llxRxQM7hIVI2MoBlwcHUpnwVPgEAGGfivgZQU4Hg33gOPJiAaEhUxED9BIytMMAYcVcC1EyELPCqG4fjQi'
        b'+IPgKmkEAzf3JSRHozwbwF4/OhWcsZJHYwbEY2qshWf806NpSpjAdIc3FNZuuJY7JkRGpSC6PEor0lHTExm/nqV84w6UZ5H8wMUVEXKUqowZDHaBDaT2S8Blb8T6Eaj+'
        b'RiqSHgerlpDsRIsRJtbFpuA6bAfbJfTUIHCY747LPqCR8IQM8e4isJcSgVsMsJdlEDgCB/zgXliXhtQTxjY0lR7fF17nx+YqbAoGJ+Ba/AQ09xXRs1LhdvLIm4OXFIjd'
        b'DwsxZ3GUMIwRq7qTR2BvJBqKuiRwCqWqCOpGTwWo/TzybkG4vhnhZwyu5NphfvQ0UAuv8qy9owDUIwjB+UXFJCNMUgqo7nlcWL8hcP0IAs7g6FxoV0Rh6ZCCB3bDfMpb'
        b'yIAtSaBZwzgInuug4CD1xk67FBymBqk0FSziHoZwD0u4h1nOOrgnt72Cw3TgHlZp+OKQlDWPRTcms/HdXj3nS0kDmMSy7K7fmKnRddlwTUvYuRdXLxBFiMGag3kGuKbo'
        b'D8dO/nXrtqrrf/qtBwBj/F/v6iebvk3mZcFwPG3YFCKyVlUg6lqXLoPrknnBFTyAY4eCVZZePBOdAqcdoq37QA/1Jd7L0h+94rdcQJ43gkOx0WmIrmrbZGBvsIGDGwoL'
        b'SYFgHzyDpCl6Nx0BHyLY9bB6nBclho1olMfDoxaM6QGgboLjlRRYmRoDaklxLNtn5FALGY0aBORRcpTZhqRkLMlE8AKDBNIhcNMykIfWFrAHZwGOgMZYJ/jLU/gaDYgU'
        b'pIO9eQ5VqZ0yRO4SVaiVK1KbCxiXLrRcRPN/frSYNnVxvivjWlmt2dLKmk0aE37RhJFPxrjpV4wpEH/v6syZJF7hyrjSQ8nC1NoTnhqJ2QI2CH3GUFw05vg98ErnunQM'
        b'T2qMnnlKTVr/ZE0aERob3cCZsXw885+Yb5ESfE91J+c7VZImX6/lzldiRXiUZfoHXFN1HlKFMa+DNfAy3KmIjkDQp6ARku1BzH6CKR8mJjowZ0xxqUdgrdFdBz4/me9J'
        b'pvNhsFoMhW267gpKFECbgqg2XZctzsl/RM/Tpm6uTsdJanA22MKjVlIP/dy7HWsvcD04CC5EEd2JRhzRQHEmGtzKS3V1PO34P9NZHRtFzDRayVfGUZ63Zwv8jMXZxTl6'
        b'q1mjthiKjfU4MUENxhqBruMGIgWuDpLOSU+JkiuVWH9FSgMLr8DNVBRoFsCd4MqMJ9RC/4RaeDuroGt0qwDhp1VhgQga+aKTBSJ4DKl+lSy4IRR0TnJDMMnRmOiQAcc9'
        b'JdlVuZMd3SnZCdpecKJpb1d5BE3tnKu8J+Gpvn15AZ2ReWJuLmdOQTfe7zv7xJcPVN+p7qkeaCR6lTpCfefryPMqbZMO/Q98oDqtztOf1DWp83IkuTVaJNazZu1cM2qN'
        b'aM2YIyLp6O2r4n0pEOir+WirjCZY5wtqJ5vBqSRlf3gdmR78iFJdYCMLzsJqcBQNE6FRrj0CtaN/QbZGXcgzgIRngGAGIVAAQqKlYeY8g96SrTOZik0xYwqL0ZvmcTEk'
        b'gROcOLUp19wqLFiCP93YpIMVyJgwD5jCXAyD9YGtbgzzXaA7wyRghjmfbUK6NaxJjUJqHNJ118YidbwZtbU2XYlVump4GFyECPC9ZoykwNrx3vCSdJrhrZW+tBlrzB9/'
        b'FleQm5dbmKvUKOM/UKeq8z9v0t1THVffQza4WH83laV0Z4SnvtY76fqpOszHrVPccaNbgNDUow03eKP3MR3ibhbjdJvd+uKvHn3RjyJG4i6wEfVGNjzp3iEM1QNc5UBT'
        b'JDjfOTN18M08ox+ko5rAKWcZjOazjBnL5vuTpQp1/4h7qprcJDW3sV4mTei6XftXlQh1rxeV+5FwhbFVxhGK7YVGq4VIXmW0XMkDdBdwIQg0sADpRomWWNzOY+AyuEB0'
        b'cmRRR6TIY0BDOqKB9VHJ4FQEL6szs8HxGJEeodYOoh+kI7NvKy/SPV6E6/ypMLiFA6vDYi3ELrjEwCskb1lKKirlpDItBZlGWFHwovr3E/SEB8Ahd2JwG3Zfq1GTpzYY'
        b'ddpsXZnGnV96C2n+zxTeNvytLHrLbfhp56D3dA06fnuv26B/KWk/6DHgKtgfRQziJMTf9Yo0NOzgFAvrk4TUgKWC9Phw11g5B727G6IRG+6pEdQD0TjHf8+hFykLcaO/'
        b'zxSJtFMpqS42N3+X+eMFi3ITRspHchQRc7FwZ2qUPBmxZQsFqmlk5R6kQQs8t4y4bcpH/uS/2f9vwWzGXfq/mQbBcd7dcnIizaDyys4Wf6epixrF34zyC6Tw+Mb5pRWt'
        b'8amgDHs+f0Cby9Cd3jeHK9RadZOuSXcy756qRF1zqkn3AHH2A5VRHznjhPrVnCR1vr5q7WDmxb6RE/O3r3ygzd9REFKw/cVVo1YNrRRtV6oXU+9W6z+XVNu6jRqWOkWe'
        b'OPJIULCXsDB11oOVQ07+Q9KSWj1d+vPnkmH1z0t2h1JfRvRZ9kMtwl7cRHBgGtirIOOSXjYca4igkSleBg90Dh5PhBQuT23OIyQl5UlqkAhBsPOPKIWIKCTkG9JOermh'
        b'TKgnynRePs2/RqgOJz7iRnWfBHbUU/KxjZmE9ENkcCKjiuuGbNAcuP8xzla6nbOVeXpKw+2WdKA0iZLYhODCCmQ8bUIFxlJDwa5YIdhESONhhMBvAxuAHcKp/5Yv4+nl'
        b'kC+bN4DB31SSrsaplAkjc2eXVjrbMOF8C21eg35Y5jPy1wf7gbiAye/sUN1p2fOCrOkVwYiUmEZm1M5uSQ2Tu3wiHbmlR91MTV1e3dzv7q1QThGzA7+7/IX1Yk39j43W'
        b'T2Imj35xdY/A1R/vCDk5Y0DdTm/BiY+//scZQfdRLQ/Oz7oG/1uSF/zZwk9/jbrx8PV/Xppjv9s1vnbEwP7Betg6/+6+8S//rQ/93YcyH+LwLQa7QRVCqH3JWF3rYDQN'
        b'EZK34DavRHO0TIYMxk2gMTVSnmx1CIPI+QJwS1JADB1wujwUNivBKYvjoS9cyQ4H+4ZmgHUWrPiALXAVKq+j33gp2NBryFie1JvAMbh37NyoGFgDa7GhDxoYOdxSRkwh'
        b'sDIYYS8GVA+77Bq41WabRYmJ/i4AK0ujwHlQnyKHNcmpyAb2AecYuGd8H97oOl0+N4qaHpMcHSmLgeuRikpRIVJuUSS8QsxEeDi7BNSZyzDIo4J4QUAMu4vgwkALRj29'
        b'UMubB+DcIAXNWwfweC55tiwb1kWZs5TyZNRtDCURsSKkOaz20OYfY6sJS6w5hQYe9fvzLDqKQZZaIMH9IJpDV956E6NvYsSqEtokdWPTbp5s2oky0GZJ4HRX3Dj0FQ8D'
        b'joxsZRGsiopIg2thbapQBi8hE/UsA1bCm2CXRujgK2wU+jn5KobFaryNDqUqhDVeNmENVclUeNm8zMpyPxubT9mElXSFaC5lDOIoC10gNo2gKfw3jzIGZyLl1ybCKW1C'
        b'nMcYSkvjtI20ibMJSrIMVIWg7KBNkI/YfDK1cOsCpsK7QoxLsXlXMiY9KY9D307bhPlIja4QlunRN468HVThU8OiN31sjJ61iRtomirdjOoxmaSSoFpKarxJ7YRl/WvE'
        b'NSL8vZImKUUkpcgt5ZtzKZvE9GONhE/hrG8GVaqfSzUyxv4kV59KBtU9uoauoQqE+BuqjUDLVNL824208RfyHm0R6hny7pwaH8e7c2oYnLfrzXfJm0Lylq1G4HgLffN4'
        b'66SWzffSclpBFbIRJ1O4BRW+WmG+l803X4Rn+PC8X4WvzRelPav1tvkGUxW+di+7D9LcWK0YpRPZWJyuwg/1gF8lrRUV4BI/s/lpfdDI+Bn7uu5z6P4vWgkuEd8Jxk85'
        b'rW+Fn41pZExTUX1pUl/G1F/rZ0MpuiOA1jPoPX+j1EbbmAIWPRuj9cffHfdF2gAb/62vW3qVtguf3vUOLs3f5q8NHI4/fdE7DTY/cvXXdrX52XxxfviZ0c/mj5+UbLf5'
        b'4t8WfowDUCsCUCuCUCsY00NbAG6dNgz1KWN6lf+F0nyJviF61PYg97/gf+H7qJVdtN3Rb0obUs2EUrYupP4BqPTQGl9cQr7YFuCsg41tZE1SC23zr6RX00aRxYf/5jAn'
        b'w5WzHnoVIpPaKB/8kImWuqQf45CAxD7GZn8uYq2F4graRudTG5hSDks4hxbZKsrONqqLdNnZMqaViYlrpS3tDOeH4jGFBrNFU1xUMu5flMNyFlJLwzV5Ok0BsqraDK+2'
        b'Fx+y0mLTQzraxJEcivVSS3mJTjrA7FFJgZP7pc5KBuO5WRsWz4yZq0EVrqQ9Kux0lPQnQnLxYyDRhOH/l7b63seFPvRXSxerC606KapRxACzjEjbhyFmXalVZ9TopAaL'
        b'rkg6wIAfDxpgHvSwC7mBv7puceTa1e1NZ+qH3tIiq9kizdFJH/rrDJY8nQm1GHUEut7HWPmQHvSQ7vvQe4B5fkxMzEJ0F+sVD7tES3OLLc4eGoX+oxYOxW0Yxre27buk'
        b'VWAwanVlreI5uBlTsI2HbqG6mFs5TXFJeStXoCtH9i6qT7FW1+qdU27RqU0mNXqQX2wwtgpN5pJCg6WVM+lKTCasw7d6z0IFk5xkga3emmKjBVsRplYW5dTKYeJoFZJO'
        b'M7cKcB3NrSKzNYf/JiAP8A2DRZ1TqGulDa0setQqNPMv0AWtIoM522ItQQ85i9liauUW4ytbZM5FyXE1WgWl1mKLTubbqRb6LBckppJcMlHkJNA3KEc4A8Vg+cfRWDL6'
        b'0UIWy0NeMgY6FFk/OpgRk99YZhJ5yQSjX2FIrQ2mA4RBRKKK0HfsBfWjAxicXkLS+zFYrvoxOBW6w/iR/ELocJRXMJa6DD8n0JInUAiQwdGQlAYblNEpSKPJZkfGwpMu'
        b'V7rInTceoAuSYEzZZzYqnyIy6V0kwdgKzsaaw0v9LEiFxf8NSOrtZisENoGNsbFjEBeZZiC5SBcI0SeSHqFUPoMQkw0lERpIMnFIGnBYfpj1Ni6XruDKMm0cyj0DSWAW'
        b'SxckEffWEMmL0uMcBVoO5cLiX+iT42M9Sgt5iWM6ruVKTmqx1BbYvEhpQv75XApJG1IDkhMzhv/NOX5zY6hSPyQXGTIJIFAipp6GB5GMZDK+THN9w/dkAtNoPL6sWWdp'
        b'ZdVabavQWqJVW3QmPC8gE7V6YdIrUpe0irQ6vdpaaEEUi29pDRqLaaozw1aRrqxEp7HotCbs/zJNwYmFTyAyN6cmjkLQZjvz7YVwzTyQ0BiHqAHTWABPB5jSCHVJ6BAm'
        b'AP0OQPRgHYS1pBNwW6lzzrs2Fs/TpZF5NXAEnKGiwCUB3ArqxB6GCC4bq6OkrA6zoBSeB9X7OK0cG+20ZdwNI5GTsrToUoPHma5FUj+fKglAdIYSmYYiyvBFd2gsSytp'
        b'H2TxEGlFon8QQrM1Pvh7LY5g4VAlcNFiVBWJXuRyTnrbGExB7Y0pjLfY/U/8mt/hCnA2rDZQ5U1li1CxrI1yqE/KCgZlweKKVdIFlCkBf7OhalSwxiBSOSEi7ST8Dd1h'
        b'MpASSO6E1GC1BrGAHv3G5E4Ur5C5VNlEG853VAVrI7mid9fWCBGZsqh8zijB39F98svGmUqw+EEMhPKxcSSPkrk4sCkGKaCcRaBnkBL6GY1US5pa6oc6SoBFMwlkQn8V'
        b'guUCPpAJMQfquAba4aFGFIatllavxWoT8UyyuYiKEYyaCpaYRmHqmsTTYZszMhVfCNkuJGSvM5lkoqeGxTaKlWQTQCxBBReZJ7joFVEpw2AqlWAEZBj0O4Qh9MpIEB2H'
        b'IGoNo5fGqTUaXYnF3CbstTpNsUlt8XS8thWAxNZ8XDRuh9PZSG5gUpD5/F6AZ1u9cLchxuWzXOBqnrerQiNo59QSy+N9L4S9YaFLwx7dBqdekYWz0+Hv4t8lfbJc1fFy'
        b'FDaMdngNKFbaj7gvwM5IcESRqlTKI/KGyoSUTwwDDyF5sMnDrent+DRjyNNRWUjry2I2e/GODMTuIr2A57VKOosl90k8mQMMvBEnslqOPOXsFEdlCXh0be3iiKGbaijU'
        b'pRartTpT5zO42L9N0EVAoi2EyHh1sjb32HmHp5jn8FKSied+cBdYxUeMJINb8DKOmmlkKT9wnA3I8SexbPC8biieG4qdnmQAG2cl8S/j2BJk7TucDy0zKGpBhBfcDA+O'
        b'I1FQYH8O3ManioiAa2OT5HAtODYrIiUN2e0x0TnJ8pQ0mjL6e48Fp7PIFBSsAdfgvpnyOUmwXpaSlorehjUhYCsJukHvDgVbhf2F8Lwh1PsT2oz16kWaL79VvZLTpGtS'
        b'38lJVRfqo7fK1Cnq4+qA3Dx9Yc53qsg/UD/umPBd2Bq/PxRe7NtDuu/wmgmS6GzwyfNvP//J65tffPf5d18Pef32Dpr66N8XlwZObHpeJiCeADWsz4Z12FEhgLvhSYrr'
        b'RYODEYHECeGTNzuqzQPRMNjphADHsojDBEmPsaXdYDOsl+NYr1KHXyXMyoE1cEepBdvwGhpcjIoJSpcnyRlKCA4xcXC73EJCcnbDw1MVMSlp0clgncu5I6AGgJPCaYKs'
        b'GXCt00v89GLSV2PSIdGcXVSstRbqiH8CWyTUCvSXSzwRDK9nSeilvTuQZoxHateUjllXqEdXDAJtLgvBo/mSMRnw93xnrUx5mBIxY2IfBLUS/e0NdvNhPLEmnbPMOCfL'
        b'uAtkGvGi2MU6gseyjsfchoByUwJdrOOnJA4WaySsIZxjtBJ2cPGNDF4mPLC4TwrhgNxoHPn5WLbpPcSK52CYLHilU6bpA49gvmnjmtLwR0/FattNCLfS+vYTsaIxheqi'
        b'HK163DI8AjgX6yx06QGvjTC7KlriEfYGNyrAqaQ00OCiSrjFbZ4NXGSHBJrBphmB8BQFTsI1vrFdwMpp8BqJNANbYCO8wHsRl4DnII51ccRUzGAHoxvVruYIKLdZV4KA'
        b'vILD4AF1ISBbg51EHBpGlgwjR4aRXc51FsmCs/bpDAFH4g4JB6cUeP4kBtaCA0UkUi4pCgc7zUb8K5fBhtTk2a4hEyBk04nhTXidI+7k8BkCrMxJbyfnFP7YLYuyDiZM'
        b'DNbCtc5MSY58ADCsITPcsBnsVEZjUCta4R0Cji214rmY5XANOKpQ4Dmc5LTpEbB2LvampqdOdxU+G+wBlYhi4DkveEYE1xsuvkdx5gKU9vthfics91Wv5txTvaKPCZSp'
        b'MRxiCIw2PVC9kfNqzps5yeqN2js5p3T3Er/4II6aPZqeHV85yx7/pexs3Oazus8V5m6H44aslGasOVw5ZTfdv8crjS8H0e9/iqHyZQSSHzPUB3NC7sj8ZF68e/nmLLCK'
        b'H1Bcu3E2Dx80vFVM3uoGNsINLiwEawZ4wKER3uJDcuo0A5OKOkM9BHnwhJG8NGgFOOaYv0snJcGjoN6L8oXn2RCko9cQD/DMZDSYsME5yxcLz8Yg6R64nMX+4Cl8LNE6'
        b'eMnieuckuIxDRH2GM8gEOA34+sBGcAM0kYlzMmteHeE+ca6c+ewQ7Ienw7NLTMjExtYOweAwJwavoEQMsXw5ZMsGYvsVWShLh3XEP12ZTuNAvzb9yTNnnuUFvGLWpr8+'
        b'afLHMUfk60pAILoIXappp7hYSf5+dQdpK9aGwckkWElQA+4P/z3AgUN8N46E5wRT4JVE0DIAHJNRfeGWoHxwqKQQVy+tPJT7eyCV+MOku7E/MhcHv5HxHh/fXWzdQZ/1'
        b'okSyVNWQT0xp840Uud0YgucP6cz3F+L5w/UB5ynDsjnPc+bn0LPfUiu71Y/2A4mSyUXfD/xPct1kSI8QLrlLHTrb94Kl/1fGyn6nDCPilYPffX3XO3nRPwiqV9ev/lbX'
        b'b2B1vGh5Blza8p3fW3vtPYeO++TrbsO8t0x4Thq2a89LQxIyjmeslok/Nn35TtnS6iXqy5P+WfHd2+99MbLkE82kAvOP3zd/tTtqTlaG1xurxxcadw0VmUbR38QPLb7x'
        b'XsbY9OGZSaLPy1LfGv9gVHTwx7/JJCRaqRTsGsIzmGi8Z8Q+rF5ASDkBVkF7lPt0CNwO9xNtJAieJfoEqEsC2zpRRqaCK1gfuQJuWPCqA3jFBi/y3OVEf1CDxgsNIKgt'
        b'hsdwyQla4cIpYKUFE8OyrOFRMfKkyWCbU4HpmcXrLzvSwNX24y2gegyTwo0cqEsG18lr3nC9Cz0IkYC1qIiSNKobXMXCC7CyjwWHfgwBzaWoQlXTiCrGq2HwLNxFHqKv'
        b'1aj5TNckMhHEDafBaSR4dhPgAUfhZWgnLUKypwab9G0xfHAjvEIYfRmiw02OahyEm9qJpeVy0lawGu5Xw7pUWulP0SMo1DMbxz1O0/l9VovQhRU+bmxOgCLCCRQWl7LG'
        b'4OAbDvFgAPrGMYH+QnQNYALopT0fCxsO9Y3oYq1Cx702cHhqkxapc8X4u8GFFUZMsR7q3IZe7urc4+uFoJT4QcXZjhvZ2chWzi61qgt5zzhRF0khrb54IYnabNboEPBl'
        b'8y3yfsbubvV2ZIIyINXPRZccp5koYkJ8rZgtwA5wCVx0akTJXdtDG0ONAjeE6K3nUj0MR5HjkwRGOg1HHTIGHd4irNEIkC7DaNkqbw/zUO9mHmaoLai7jKirlBrOkSMm'
        b'E5eyOwZdXIouUXNJNJy3Q0fiakRIRxIgHYkjOpKA6Egc9op0Hp3WMZZDwKu6FXBLGW8k6np7qLqZoMU6Hr0QB+vBXiQwI5LSYpDyAs5G8rpLsnwG0nlmRmC/2mwRXlDR'
        b'tpqCViAG7+rvHQaqDJK8vwvMmSgj1u9yzzuy4JVxAdw7e19hFtRMksaFU12f7xHat1Kd2nvXlPe7v6iN+GLGhwODps6dOZD9zC987IJ7TT5mu+D4tyMvZb7/VfAXy7Yu'
        b'by54udeohM2X7pdRey4EHU+4j7QWjJglSMfa5oGYCCnAKmK/3ehvwY2flpKCoa0f5UQ2vzBi9w1a0Y10gQLUIgs1NgYvzwjUseCk3MzD0flwIb+WAtNFfLYIHGbKQHV/'
        b'HoZbwLZ+bjAMVoMtbooQaNAQuxDa+8+XxDksTx7urCZikYLnhoGbsAmei3JDu8U5Tk3k2ejfPSJTjwgsG5txnnbhCqqvWIL97xIENkH00h4daDLGlZJnQWErqyk0t4r0'
        b'1kLCs61cCXq3VWhRm3J1FjeQeYLWhNBpMf6+BF9wHI+p3AUyVnTZ104h+XO4O8w8rp4yRql0AI2pBF9KCdwSHCjSWfKKtaQAk8nZRY9DedpkdlXLgi572sAD6UXEoVEP'
        b'VyU7sQNsssIGER67tiVHo6VCcDQ4mdgRR80MYb/EJaZUZtRQysPh7GL4EVT7hTd6L9fCGPqxC2Ny23uAOxpEYUoria47bYAnzYhYL/iUWpFWUAMvwXOWxbBl3iCfxWCd'
        b'f4kEnqOosfCIAJ6dBdZbsckNrib2QSlqU5VwXZRyNjF2k9FHbTrYXyR3Ln8Ep2BNdAw4NwOvMQIXwFUxvIU+HhFU7ligyZLp7aeLTuuwfqFTRCNWwMVl2ijQlOpSdyhw'
        b'U0d1ncXCujJw1Nqf8GwYOIQ5mjQK1oHNSrglChyLoKkwsIEzgXNwpSEtcyVjVmAEvHOj29pzvivjJNyfevefvOagqvrk3VeDkuY9H/TWH174dM9fXzhat+qFaaWLzp/N'
        b'3Hzx+uVa45uFH1Qv23c0YH7PD9cLS28PLrk+fuf7XRZRtTIBiaqB5+F1xO8xMrIEpSdYKwQnmXiw1mTBC026CeFKHgumgls8HEwCdQ4PlAjuRBU/hHKoi4Vr5Txk+INV'
        b'bH4QaCB4ErJYid7AK3rq2bnwMsWNpMG54gKCZCH94RUF2DPSEUbvCJKp6v/E1Qo+6pISHWI2zPjt4WSqhIBJAAl/WRqJICG70KDRGc26bL2puChbb3A3atwycpZKoOCx'
        b'0TFlLoZchi4vtMOJmx4RMumY16LhQUW6HNRiJZSnXLAunZj+6JOXUu0tFcfaAlAby3eqFuwN6A7OFRnBaTKzCFYtHRiFezUK7I1PYCgB3EsDpM/CU2Sh31iklR5HjHJu'
        b'yWJ4wQucLZWISkolpRwVPJrNBfWg0ornA0yoAmfMSA0+5+272Fe8AFb5ieD5JZglSwVU/0CuAlTCHY7FXqYwBRJnZCDRSJ1lgsFKJFBq51uxdgC3wSvwMjiBdNtLqI2R'
        b'KdGgzgSOw81LoiOIVuyM858pcqxNpSlwCDT7TKrwsWK0gc3FKW6JnSlFXR6RdmuhGFYnIw6KRIkjwapyUFdSCtYvgRfhJTM8BJpgswWp25eQFn/JitoykwOr8uE2Kx9q'
        b'pswnVd2mwNY7krapSalelD/cwM6AVfkkS3gYbBnnkWctQhWc5xJ4TiIWUv2TObAW2uFmolFbsTaqBNXxaBhXCxFNjqZGg+0asqzPH64aiQq7VpwuT4ZbwZmkZC9KMpaB'
        b'e8E+2MR7vqviFvjI8ZosxVy+t3h080b9gKkDtBAkWwhXeYHrs8AaK6ZMYC/pM1M8DZXen+o/Noegu0jhjUP/48720KT200XzkYjzcHkUFRBnLpF8Nr8nf9PmzxLQilte'
        b'VBjTdzFFPEMFXfOw7hCFfUO1xB/kCbS4Hr0rUE2KwUpRBbgMmmQMyW25lpcqP0QXRffts5AvYj16kZQbVh49Ue9LGf70xR6GTEYVfXksrfGGEsYFVb9l/e/OBPmtyJxc'
        b'7V16yJz6ptsBwRej1i6QzXhvQCXM6Jc/8EdR6utjRKz/7eZZHyVnWX8cOW7f+r/+LPk+TvHBgar+A9O6Ba0t+Lb670G7iy98//chw25KMiPqT/X7soINPT71zIth3/7w'
        b'imb9rx8umjJwYxcv8/STQda/HBg47a+29x9ez/tor+7WztQ7vV6ev/U/vubmZcM+KijVvvvwx4Ov2ce8O/El237D6pdf+Oukv1TV3Xr9556jxk4a8OpwVnH9u+LM5z76'
        b'qOd/bBc+fYf76381s8pf3cSue/Wt25df7Nkr48ir22oXy+fO3s+MvHBlbNf3L+zOHP+F5o/JL5rT6moD/3GG+fD+gjWy/OiE0PqjVQPH7fBRLI98/ug3jefWzJT9eOG1'
        b't74+8MaK117rWbxsbe8PX72XdSv+y9o+vS69dyapdtkLzSusFsuRPcNk/kTLDIDHwVVwaKqCyI1oDCgs5QPPsww8D04R+AaX4AF4HKEP4pl9k5nF9ARwGq7nVb0NwfEI'
        b'2cFlTZtZexAeJAGSyOK9CfYrFipSI2N4APIpxDNXzV3I4yRwnCMLkTFV4DVpdUxOcAWilx18fOQGcBA0g6veUem4UlgP8UL1usnASwvBeV6L3deji8Id+DXJ5cg2v0qC'
        b'RbNiQWUU3A6vwZrk6GQiWwSU/xhWDw7KSQE9wGW4RYHNAJS1TK5ESk73VA5Wdk+El8BxXqo1j4PVJFB0t8wtVrROyUeSHgObEUbgmqmRbPaiODkNTvnC66TThsI9qEdT'
        b'0iJlqTTF9aHBHrgbdUwfPmG1xRF/igEbZYDIvDu4yM1OTQKrwF7SOsTu68AaJFIn5hKhSiRqADhBFPzYRdKo9qGl8IZyEdg69ok6q9ezGvndOhWARGjOaBOaY7DI5Eik'
        b'KDL0mQAx+s8E0vgqZgPQvTCin3MkDgZHw+A5ZBGJm0GClvEjc8oBdCAjYUw2p6xGtnubGH2airsFdOFMrrYTrHdC3AUrxs0ERK+bnyBZBdQiyyKLCGyB+wOcWxNcTQ93'
        b'zro9l8GbP2rYQPQ1HyQNzyIqAadSYUM6gvzr2GsLWhh4WAlXk+TFcEscdq7fhM/JI4VobPcz8QvhVg3r0AXxxEKwUx+cg5XL9ovXKdfyddpjATtj76YPdk08CB458cCS'
        b'+SPu8/5oHMVSt38zdLkGs0VnMkstebr2O6jEiD3eTbZIDWapSVdqNZh0WqmlWIo9vCghuot31MDL96TFOFAuR6cvNumkamO51GzN4f0mHllp1EYcCGcoKik2WXTaGOlc'
        b'A7JyrBYpicAzaKUOAiS1cuaNHljKURU8cjLpzBaTATuY29V2FIk0kGKDb5QU7xKDv+GAPJylI3vUwk6SFOjKcXgcn8rxo11CrXQx6jNUp04zsJrRQz656/0pE5MnzSRP'
        b'pAatWRoxS2coNOryinQmefJks8wzH0dvO+MF1VLcRmMuDhZUS3EYJa6OM68YqbIYdVxJCSoLR9l1yMmgJ6n4DkVjlaPGFUJjhcbGrDEZSiwdGuLhfHGFYbtMFR+lFQcc'
        b'zp6smhnLz5sny2fMTUKq6MwksC40RTBj5EhwTCaGV8pHgi2JfUd2o2AjbJKEhsHzHlTvWnWY4kn1lIPuaRfdM3Z/fcBTTrF5BBlgiJB2aEG0snPTzhXYwNeEck3rPdPK'
        b's85dVpySwKzh3dCvKDM286WvHP1WJf86SSPS31PdVxXpv1Mla6gN9xOHrJPtOpV0orJL/89e2fnyH57f6XcoqnDU9lEhiTlv1MdIzo1qUe0ZJtmoqpAlvlP45sGIs7Wq'
        b'd6LX6ONeW3Pg7ZjwO6/mFOqlqSrtPZVwRwCZIPvLvV5LhjwvY4gYN8CNYHWUPAJsKOBn+Xcy8lh4gDxLWQhPRsGG2MhAsA9JMiuNBNY2uOrZ55UE2UtM6hIiNnq1iY0V'
        b'VBhHwobECJP5MMogvFRTZnLgkFu4kINi3e7gHJ1GFyaYZ3Dd0HwCIiqWo0t3VDNzcJuoWEl96zF9hGMIh/cbGOWkbo+Vm/yqzTYJMiVQljI+NgWJ7amgyd8AdkzoPARg'
        b'CE/k1DOt1H2KaX8vpRXHJyL1pAVsjo8bOiRh8LB4cAmctVhMi0utZmLUXEA290V4DrbAZn+RROzn7esD1oMaUM8guwpe8rZQ8FQpPEQUcXVQSuQAOoKmAlTi92IlvHb+'
        b'9nBk87BSmlKpIgdkTuHXIhmm/+kTypyNvsUsG9Xt5QOBiYlBgreX/enmwV3Pn0lavd9HXGTfsSUJLDO8tjzh3R1d74+4azsSuDZIH3ru5xOXyyLiajd+Ff/L3QkJJcPW'
        b'ff7+sn9t/sf4rpIjPYfUnlgUMOyd7SOfa80ObQz6qLyPg3alcGMkrwVOA3VOD0DaIqImicE2lct1QPwGm+EtcA7PMj3OX/ak5W2ibFOxJTsH28yo00PciTmCIwQcRGJU'
        b'Auml0U9Fxo7snDMehDCneJJzJ+uPyRttRIx3SBjQgYg/9VgONxEzNNgJrj2RjBW9nYQM18aC2vQhCSy1GNQFxHjDM/zgS5G9xoUhklNFH8+cwZuv4HApCzcJ8IQXqI6h'
        b'YkZ157ep4pD5mDiTpaSq1J/m0zz1DOjLUaIQuxeVqCpsipjIUw95Mj5GRAWU2FHOqlSmyzz+5opiBbV5wQ0kIVSR14rG8zfzp3ahpLZTLFWiKjxQMYbiVxOtgquGzoTr'
        b'4ObZw+LgWg7h2brJM2hwEuwNIKkSBoZRQwPQgwCVLXbwDD6rod7n6JUI+X/wsVoyJz1I5GPvtsEt6TMBzgquE1Csah44SY8zw2Yr3mAItqjwwsI2C3cW3I4MClgTnYL9'
        b'iNi4IAERcH0U8d7XRollc+EpMu+bahBSqLKZwomU5OOQVXFLKLISNV4/SNQ4NmAIrUpVmDTy4SUZbyYcT05n+N69iGyIJtiMhElBSBqVtiSe1Lx//CjKsqBGiJoz48ue'
        b'Pfjm5JWNp6ooKiJx3q6cEEXIOHJz1uhxlC3jFDLZVTPKcubzb5aXRtMqhgq4LZuh+ShpA7+x2KSxf6AvsFTS7e7+OduNFUV8bw+cSm9mqMTbAmVhiHXJRHLzQ59udBwi'
        b'u9u9IqwfBf42hR/b8RbqB/SZqPhYm5nxfBq5OUUwm27KOSagAtQFI8YM4ktv8GukI1gq7rY5w5q58GRXcjNo2DzqMhrpxJ7vLM4MHBRKbqry+tKpDDXitnFe/nbJrh7k'
        b'ZuOw3tRk3MyYHy0h8efyyc37hlR6P25Rtz3Wj7rmTSA33/TrTkf3us8hGuy5d5Fjq7Qf+75N78/9VUCp1OkPV+TxN3+2vkjVjJRziDC90yeV8Te/ZGzUvyT/ZKgMVfC+'
        b'mXr+pmDRJ9Rl60MO3Zw3c1QUfzNdIKFCFoxh0U2Jt5/DkfFTcSm1Eo1bSZeEZbMELVqD978+5szH0J1loX6zZ6QVvx8X0HP9X0Z8/OmRzesLmxMPHL7wg/+Iv9/xT3xw'
        b'QPq8YOyUiA1zztYFzHrzlf2Xu2/ud/S/kcv9vF661i1w7Xc7ysvLfxq4OHqc8uCW2aejMiad//tI36Hayh5HYOFHhiERP/zzenpT6OIevr79WsI+uJS9N6fL+7O7+Hy0'
        b'87T4mOKYonbOwXUJn8v7/HHOqdU+x7/ZLHjQMtnv0J0T8pn/sDVf2/l10IgDuVUHPxi+9KWofW973/P6ENweevbegAUjtv9qLzjzefDmf6zNfPjzQPGZ+OeyvvfJtm4+'
        b'36Qa/Zk+fsIcr7M3Ft18scE2L0Z07adD0+dU2ZS+cw9+OUVjDb0ybFVW3fwhW35uLbbM+V7zmf4jn5SBzcN/vVn42cCfXzvUa9A7NdmltX+83NWyb8q6a5ftYvN3z720'
        b'+2Xmn3+j/EtXTiurnxT+SmH6mD9n/vfnmaXmL3yVu0Zt/fCXTUu3/XJyxaTdC9/+8YW3cz9MO/Rh7yn3u/xlxwhL4L7k1z97e2P2ex9O2f1FeUbs/YUffzP9P5YE45fp'
        b'/xb8+/VryvXXl5975V62fuqiPavevCTZ+mDL7qT71qsjvWPH/SLYX9SQ+/NFmYj4LUbDA2Ct++rRLvAWI4cHQTOx++F+cByuiYI1sRQWpAw4QGdE9ubdCWcGzY9KkSvk'
        b'kUoBJYGbLUIG3gAr4WXy1Kv7WF5UgR1gp1NcnQO7hxFvwFxwNAaBSHoyOInwrBDuX870BQfAduLroP3gkagYWUqUYxc7f7A5Gq5ki+EVcJnIQaYrWOXhR/ECV4krJauC'
        b'eOHFGbC5LYTIGT+kgftZcHYprHnWKeuAZ48qeGotUuQUn0T2LnCXvcESvPrGL0DM0e57D+HPXugzBP0F0gORKAynheSJGKubbCAdTCS2kCxGFxHvhB9KgT0VS8MeLb+d'
        b'02441L7Vy2EVtgqIqecmuP8Hq5RY0yr8ncT0r3bJ+5XoEthB3v8Q6S7vsVs8ekCXJ0n7CXAjL8IEFLCDS97w+hB4g0wMWtLJ9IzDnwu3dcMuXYdnI1lAxYILAngS7pPx'
        b'kZNHwGVQCTeAk23zayRuNABWs73gCVBPsLDSm+k7iSaQXlhiGc4DpLKbYOivDL8A/m/+s/ibvSK8At5nyKaVqf2oHMrQ7YfTlPkAejLyJtvTERr1l8Jxu9LAcFFpqDJx'
        b'Wt1mfbcpsyIOcOLgV5o//Lxqe1D6eUOvl99ih/9hyY/h/3ojM7nv1BmvHG6cEXlM10fx8Z05iyv+3LV4XMIPm97+pOFsyug9jYKr2z+a3OOP9kWqd4RdP627e6TXl+9d'
        b'uXLz/Ftn1/z071XM993mLPsFRJrFfw389Zs387yWyCLfqLt1av6R5j17Pnlvx6ufe71wK+beyn0yLzKZrgHHyvCGp+WUa8tTtw1PwRFYR9h7QU/QQngT1nmB4/14V+JM'
        b'uMtCtkqpscEGd+sCxx3qYGMqntzbyxWDA1NJEFZmGtyZNcD9RYQFgZEssgL25fIL5E+Aw+AqfqNtCP3AaRZelkyOB88RHBJLYSOoi5Ur5XBtqkxI+Yez0VOzc0AlqQvc'
        b'Cu0LQV26Q80hsyr0JAwYPcAGDuA9H52WYfD/HAWeGiOcTOsZkoT/uuCApIhpEuKnZPCaPSaY4Ve5Y0wwVWJSdOdsnvUI17XxdNf/x215BMfjyv3SzqO5JsGd34lbfJNO'
        b'FJVNOVmeofwTWH1/2OAx2SxwfJoldFvUj5bOYrVMFqdlswRaLkuI/nuh/6JcKssbfYo3s5s5rWAdv5MVntDntEKtF1k04qOTaEVa7ypKK9b6rGOyfNFvCfntS377od9+'
        b'5Lc/+e2PfgeQ313I7wCUI3FtojwDtV2rRFldXKXRrtKCtN1IaYHomQj/aYPX4V2u8GZu3bUh5FnXTp6FasPIsyDH7x7acFRCN8evntpe6FewliOOot6tfqk8wKepjepc'
        b'nelzr/YuUuzG83xHSgIzPF56UgqDGfvriNNUW25UFxmw67RcqtZqsVPPpCsqXqxz8xF6Zo4SoZewL97hg+QdgC7fIkkRI80o1KnNOqmx2IL9pmoLedlqxlthe7gDzfgV'
        b'qc6InYVaaU651LEQMsbh4VVrLIbFagvOuKTYSBy+OlyisbDc00s428w7jlFRapObr5N4hJeoy8ndxTqTQW9Ad3EjLTrUaJSnTq3Je4Qb19ELjlJjSGdaTGqjWa/DXmet'
        b'2qLGlSw0FBksfIeiZno20KgvNhWR3eSkS/IMmrz2bmur0YAyRzUxaHVGi0Ff7ugpJPc9MnrYM89iKTGPio1Vlxhi8ouLjQZzjFYX69hz+uFA52M9Gswctaag4zsxmlyD'
        b'Ei+kL0EUs6TYpO3cM4TXcCO65/j1VM7FWxUMcXR27htiSVQJ97C6o+fYaLAY1IWGpTo0lh0I0Wi2qI2a9r59/M/hvXbWlHdgox+GXCPqtwkZya5HHb3VT4htESr5tVc1'
        b'4NyoR669cq0h8QEnxw7LIgEHjBfYAOsmCdrmmCOSomNi4Hq8oWoC2CZcBlfCwzKaTMXA1QojrIYb8f6z6XK8wGFdOk0Fgt0sXDUzwmAIPkWZlei9Lco/4eVZd755oCrY'
        b'80pOdPB9VZJjVULMnAh1ipppDm3ePnr7rtDmzJ2ho3aM3n4+c/T2VTmFstdvpPaM/tt3Msnzkt1yqnB8F79f9yBLgcjtW+AMbGovuFOnxDrkdn+4gWjn+ugoN5FcoXMI'
        b'5ckGyO8o2htsglt8UGNlvPoQDhuRBtEN2DkRPK7mJwsvd58dBRuShnKwBRymWHiNNsJ98ADJHy/WqHH0AE2J4Cq8yQ4DVvkh/QJLkiGwul8vPGOlkHvhbXFpRflI4lqb'
        b'T8FLJNchw1jKC+6zLaXhTpuQZFrgB7bhWoO9qHk1aalCCimCNLyyCJ54UjyahzafbUC0mZ1NJHWwu6ReQXlLyDoDrJEv7e5JtDHOdEr3KGFTjaeY7nz9AMO/1hYOvBaX'
        b'2kGRrgxyj9V7VPmdr2wi0RFUPu+spZUkhtc5wYTUI4OrE9pmKwvRpYFxLHDqUJxzCdTD0EfOW6FCWG2x5okV0vMVEmU7LJbH1GeDsz4Pg9xmrpwTYDFPLKrKWRQGUoPW'
        b'/JiiNruKisZFORW4TqbJNIUGBNFyM0Jq2ZOrkMtXwSdbV1ZiMBEJ8JhabHPVoh+uRVsaLGTad3lb4U7g7u4Cbsfmm3aBG3A/w/abzh1ZOkAmmXpeCW4MnAnXcSRUdz24'
        b'QeGthJeS7cUy0uBecIKmYCXcRVVQFXB7X14nrCoeAeuSiboez1EipOD3ZFJWLDFMXXCfMc9Fb2x9M0v+2ms4JrDy8xHy9TG3c05m0D9K7ssMf95Wn9Y04t+bDo9PiXix'
        b'VFPj3cVge7ehKTrmZdvV81n5SXezvwIf6G7fltfd6P7yyecTfnv/8NEL3wjq7yKNqp9MzENhNaxe1IaE8BjtAEOnCXNCTIwPPdw6CbtNk/mYDnhNE8GAWnDJykdcbAbH'
        b'QJN7yAeoH8WUj5vCh4PsAsdWICsLbJvHhyQraXAWNi7nd9tdBW9iawuu1Y1rmw04twhu4l0zuxfO8wUHSQ3dwGxELMHBFXA1jcO8DnSNxYcdcAk0uC4HO3nkvWCGTVFy'
        b'18bKA4oZUNUD2VIYJJG1tA5WOzbW47fVWwAuMMVgq4q3x1rKJ5ANuJMwOuvhFgzQgeAEixB7FdjpsZvXU+KpzqgxlZdYCJ6Ge+JpLwmJuhCTsEayH2oHVHOk9gDVp9qR'
        b'z7Ebahuo4t0/dzLO6ZGVrr97j4dVRwX+pzpRVac60aQ8tTFXx0c5OLUYJ4e305CQovO0ypFRt+RpdCLn1hztp4MdastAeHRRB5Vl0WSktMAj8IQhK1zPkqiQ1/fF+b4a'
        b'FUhWIOzo/0v4XJYbkSo+l5v0/s4J1NyB57Nb8jIsn+2cO/2VprznPz8ZkDX8t69fnagQxNb0DPWZE55x9vSnNyZd6POTd8o328+pry7PEnRNKzon8yZUL4CH4RZeqcAK'
        b'BTjVlzYWwSZC2BP6wSOgLh0vGgXHoyNoCqzU+sF1rK7ncELYi5MK2ujaQdTwGjyACXst4jkSVmafjnc5jUUaH01xsZSQBs1zZvJehjWz+/B7hCrSwbrYpOjB05waXhzc'
        b'LxwZButJFoPgabwVPQWbXKpLKdzDY8WZQeFtOg9onAvWIJUHbhlN2tZnSlCbYrPUiCAT7gQXMvjTZ6pAPdjfBgXos46Hg1S47tlZ0l9DCC3bSRXtg43xX6yY7KcRRC/t'
        b'1Y4h2iX+X6g7eI/iw51w5qcenPmEisjYVmFesdli0LZ6Iz6wGLGAbxXygr7zFUCEeznnkgAX93IkSKnzlT8O7v18It3OAsf/Jmi12JrBHOemI/DWn0tGP5Jt+crzTJuE'
        b'vidPdjJ/jtpY0JF1XdzuaCufMoP/iRJHKKxGZDvKkyd3ErnjFgXkTIktZZzMI+pH1ll9TTqL1WQ0j5KqZpmsOhUO3uE3F9BGS1VT1YVm/p66EN3UliOlBWtORssT0Me7'
        b'A/qwSkN0rx20GQc6nPsi7VvVmzn3VN+pHqgM+tO6e6p76PerHxbqv/vmmO6k+vWc4+p7GpFepBXl1KiS6PMj3qMGfeUTZhosY/mly/YucAeGiAZkjrlggmAEBbfxQvcS'
        b'OIf+uxAAnIINCAOUK8gmyFPBrmJFajKoTU+Da1PB9cQY0BBLwjRloF4AToFK0Pjs3Oin1mqzdTkGjZkopYQZAzyZMRGz4tKe7ejfM52DD4U8W23DF3zQjGmHJ0e6V49z'
        b'e83gepdw5C50Od8JR77twZGPr9H/lOdyEc9N64znZhC3FGI7I09nOATNjfncHFL//7EfTpY8M13Ku5IsvOeJGAV6g1FdKNXqCnUd4+aejvFKv6piCeP1vLqvM8YjbLf1'
        b's04ZL54a9I1P+OA4xHhYNFtGhoO6bLg+vR3XFYIGXk2+PtDk4rl4sDsWH7hzCK7ijwKpgpULo1KQ1rouVgHWEdZz8d140ODlPz5w7IpnZ7suvD/zCZyXTjivnfYV0yHp'
        b'/5b59qDL850w3/MezPfESj3msBHaTrkdNvLonaQdIbkPczphO0KDhD+M1qIcxGqI7Nycw20uV43VZELoX1juZkP/Hor8dl2+wIxDOiPiu+HzTPL0TYQWX895tAiIpz6V'
        b'eLfELJ48FdEiicTZ2AscAHXzx7UnRrBDwxPjXrgv10WNcBtsweSoGWLBkzaTkU52AqmBsXBdlEMMOGgxUoiI8YpXBiNFlLu23eExndKfpthqtLgNl7kz+psr6oz+OiRV'
        b'OiMODY8mONpN4dqHLm93QmHn/R5HYR2K/R9RGPYQGx9JYW3BxE9NXdKISKyDGYzSxQkxQyM7wd8nU9uCCdk0oTZNdfPTUtt7dPpvn/p4W7fucVLbnlmBvFECrvf0oLY9'
        b'A4m5sALh2v42faNcj2gtYwmhNXgsHGEfOcPMg9TAra6Y2kYAuxDPnC94CloLwD34JFLL5newajfm7VM+K6XhmfGPOqG04x6U9qRSZd3brzv2ys7WFmuys1u5bKupsNUX'
        b'X7OdUxytPq7FIQatqQ4nasAXfGyOaSPlcLC2ikpMxSU6k6W8VeT0WZJJzlYvh3ewVdzmbyPuA2KpEOWIgDThI9JEvld+x94Vbu6+KnTJZxzx3SIfjsGBm64/JtyPIQEh'
        b'Ha5MoE+4b7h/uL+fiExHgAYzssld4Q6wJQ0ZrcjqZJCde46KAKsEK3qDlR6TIZiPEynH9hOec6+8I7C1q2PZhWOgyGa7D6VTyvAOgdgbqcFrKkxGrH25aVtKJOY8B850'
        b'0NXodt7O4+hyl3EtA+dosqeXnwHuw2fTte2rBc86W+aMXEgRe4H1sDmYBBjDhgU+8fC07ndGGMNTYCXY4wFsLq8I7iFH3D3leWxj24alz3KEEs68Y6C0v5IPOEwRUxgG'
        b'AhKK9JmFKyUkRHN6JgnRlN71E0k+Dvmj9ARVmIYzGDhGcD/kSu5vU3rIrhRkZB/v3VRwNXN1xE7lSyOGzlsXvSf91OjDoxb2fC/yYM6v0Q/TVvh+3cO3dPnS8ij1dJFX'
        b'QdBbPX9i4FjJ0KARlwdXD325YnHaiAErIrqOjphdNv4ilx14uORM75zsPxouePWdfUilG5FS8Lr3X5LHRvl2z8s0CVb2/XryYvED8+KSiO4fTznuE+p7dcVvSOsvkTeL'
        b'yelUSiQ1G919vaNjQR2TAlrgWdLU4TlknaVop69KIpgylw+08U3uik8mkWq8VQt+KRnrCGT0CaYQVSTdHqRa0DxOyq/vlMGN82BdmjwGn7/p3PgLrlf0AUe94AZwrBzW'
        b'TgFbBAMoUDXQGx4AN/rx8aQ+HN5pRLUlRVXYX5zDF7BOQVaVhhT1V0k2i8fzm3CC1+ZqqHeqMJvQVXUylj8vOcCHH5/Fb5Z+lLY5mIxP71n8+JQIeqDxCTLf58fnZ9HY'
        b'Zx8f7/HL/9+OT17aWdYweFsAS87okP6r24B1o/1gnGSS7LV/j/hLrx43Ur9/Oyov4hP5vbzYDw5+NmrI+ZqyQ4mv3oADNX8cGv7x5YkH390nT7gzS/oTK7yRsqcwYU5+'
        b'f8VLg3q9FfvK8b+bv0kZ0l/3d9UBweETL/7hwVDb4Z4vjb6+7aVLBUP+UT3r7pKojMXFofN02VcMJS/d7f7uf7iZoQN0J/4h43gv9RUNnh90OanhkSX4+Be4Ba4lMUwj'
        b'R8M6HMMEDo3vNIjp+ESSjSh2QJQ8JYTBUUyIIgSUD7zKIPu+CR7m14M+B3bOjwLV8CBcG4m9cnjV20hwGSlwHYLbf+9+r+4L/E1mtYc3vK+nBC7lSARgAFl9GEBLGbwW'
        b'MYA2nXQJGLaVw7EFbnL3d29DS5tOuaAXF/BtJ0J6m9Q9kgcvFA0A+0BNVKQQ3FKCejcVugfYw4ETWnipc5VwTKfI6dpq55nWLXlsu+9CTV8eNVsHENQsWctJC0Oiv4oi'
        b'XLltjhfmygBlIg5s/9Tmy3PlOP/fwZUV12efjaiaNCzlG2X5hM97CcPE4Z9kTsz687hrA3fPGD+rtufmyOu950+MTZ5R9qH/ueK/DG1lN0TOKDmfnfaUXDlCdUdMmrI9'
        b'F69lvxMlpFSpKayKx6ckX4yK2zUiSmXzXayhTPhsd/JkJIPhrClNlKhKvTGmyBE3TmE4G+HFSVWpy0dN4Bcj9EMS9VYbHIOT4CqefmNSxoPtDnArCSXdOKLGF3XjrLDB'
        b'pBvDZ5NulM5XoG7MjC4N5rtRNut3CJ/f2Y0/hk95ym4sm9XiZ1CkZfIbPB7Ytln+KgE3NuPV19+6suqdluGvdvMaxHFJw9N7bnwl4vZnV1M+n1L1r3vfCiYU/uPwS6PT'
        b'/5Vx989s7B+OpvfYfDU2596CgCWyvHrjg4S6Xv9IfuePunNDX/612vfgycMPg/3L/vv9lT7fjx9Z0XN++SjH+VXwCtxkUmB9BQHYZNBAiRYyOtgMdnloyr974yECJVpd'
        b'G5T094SSFfhscLKUmYAIhhMJARfT6TYw4RGgDUuedRswNwTBuf7aCYJUu28vxMe/XJbAC1GRtkwMIMlpTvxQceAAvDbZY0UkXn1C9jHNQ6BSI+B3WccngGDYqGQqGPKd'
        b'1XLoO9tIl0VYaPzOZKqRXhi2gKngKvBu7IIaysLgQwKQou9nE+SzWgHKRzCXMvbC+6AXiE0l/EE85Bk+IkUwj+x7bnzdhg+ASSR54PRXbaypEb1FPJVlp9E3ITnMAJcl'
        b'rPCqoW1eeNd2rdc6lMImHEOV7kSlrCHpBZX4sBXW9DY+OACXUWZEtRWQfeJxelGH9CKUvhWln0rS88ffJLpSR7hShz8qdSON94yvEfIp0D3Khg8qiJ7r2LHeccBNjo3S'
        b'eodi2OWhVqxEQkanK5lqwqg966HAatHLR7jOaUH0ewaPOH5IzkYx4a3eZF4mFaZLb53RWqQz4aMM8MZmrUK8P7lW1yqZbTTgL8Ru4NOO5kmubZfNtmzJfvEp+II3mjFF'
        b'4pzo/Gdcbd8qwSeHmIfwy5L9kTwyjyKCSUQibfH5F/wpGoHkdAOOrI4LcfsmcXyKyJ6iIpoElJtBM7Djg76T5QmRcD/cgDcYIisYpL04eA7sDfQIAHGFTGC+sFFmkZae'
        b'SeFTkcgAMK7TBUgnmuJdvEm30uZHGPO+pFnZluLswmJjbhzrPB6TxWYi2XpJBK6l8lUEDbGwlt8mEq6PSUK1HAiqBeUmtw2DPQI7hpJaaukC2iTBpp+WteGTh2gtl0/h'
        b'U21QnQXB+MwLujuFpTa+Qxw4QkcLsDh6yAwoIyvn7jN8UwRL9YbCQhnTShtb6bxHNQu3BreKNG84bpbYMVwcOa6EHDtfgBqzg5yJvl4B1pPGpeOWDoc1ciE1sJegvM+j'
        b'Tukkq6bpTldNP/4ovQ6bIQupjotb25YKXokope4i2Rk386PUB90d61J3er+Ahp2Snu0/MnFPgWNBXEuuYwubqbMM5xKllGHKl7sZsx492bQw5FvVGzl5+nvaUyXfqh6o'
        b'ivQWdU3LcV2T+p7qjj723fvo6Uk1Dgh8oJUHHVffycnXRwSvrll81hL3YdzQ+CNxyW8EU8k1a0saI/rd2R2kH7w/L9gsVsRr4thcIbWgOuTbm2VI2SbRO6tBdVdwJjNK'
        b'HuFaaj0W1BANeTLYvjQKHycHLnRxO1HO5Igmqegyi2yYUgsqYU0qXB9NoxdOMPD06GEkuRXsg8fBWbADnEghW9zWIh17OdO3x7RnX6zdpahYO3I4f0BDttaQa7C03wfY'
        b'sVWWiObPrRHR4bTploul/q+WY+NsEllncSvd/oDHkmyy7eVN0OSDWrsuHZwbCtarR6XzB+XgU1Zr+U4aAY4Kl+vgVg+scB0Dix1zPEJgUUc4DHGNslWgNmsMBlSvZsol'
        b'fjueouqVpysrNOjLU1jHyVEUa5XiatXAs6NJCATZAakCXgAnOGQRVTPwKrTDq53jFhbZ+DgSIgCDcAgbrlGFo36EOxil6TZfk3Fu9XrMRmfeVqOjjult6IWVE7KPlXce'
        b'sunWtVUU1RLh7Bayu9ye2V2eusuq3Cr22A7zzkkYyh82Ncety/BAT2TLFEPik5126MIKyr8POxrsBmd+Z2dV/Y7OQrXjhej8dp1FIkOqYYMJ19GhaYKL8CTlB0+zgy3g'
        b'hkc0oOs4NSwEtTTCdKRAlfW1IfFqwZjPVjJIkaAqWP6EJRuDEJ4pFeNTjUoSbDQ+68hxulFr/7jBQ+KHDksYPmLkhImTJk+ZOi0pOUWRmqZMz5g+Y+as2XPmZs7L4iUA'
        b'Fke8gkAjXcCwGPGwjGsV8jNGrQJNntpkbhXizT7iE3ix792++fEJ/ODk4OaT84CJpBOSvXn41dWHwXGtYkiCy2EQCa9T/t3ZUbC+T+cDJXGQi5Y/34fQ8EsupKBNdx5B'
        b'KPEJ/FAUuhEKqcFRsAo24Co4xmHpVDQKh9g4cGNu53tRkjOjadeZ0ag2j91/8qnOjObR59C0aOfycLhldpr3dNgSUA7OzoAtoGWGL2hgqAh4mSuCp7SGuuZEzozJ6NiK'
        b'Hd+q7iB5c+f2f8hZIBJytrT0LLtuaImM4X0ydlgHqvGxww2wLtaL8o5nQC3cBQ6EjeeDlBrhBvica9HnQHgBr/vEiz7BlUGPOvHZYC7OthiKdGaLuojfiIOceuOO50tM'
        b'b7hGhul8xsHNi4zfLe0UqDd4nP1MppbPoBadx1uMNRBdAtanyWOSYT04wsopaqBJsAJcgpunekT+eTqDWUfkn5srGA2qz+/ZNQMrBIEdBrWL0op3th02c7ECidkGWM9R'
        b'wjAGrJGJZxcSHeL5Ud2ps5mZeD2ibd88BcXH1p4FDYXxQ8C5IXFDwXNUX8pLSYNd2QMIqK0AdcCOHl4cAlrAjekcegq20eBi/9EkXjcMXksm+yXEwG3wBBUDtpeTgkr9'
        b'Q6mmEC3eAWHMT/0H8hrM3bII6n3fA/gmMybH5Nhx4VIweA404+0CxbCWGj1kOHn3NauI+qGsL35Xckzr2C1BtoKjXojqgtdYSrr4FCAS4Tc5aAE74D5FMjgZLaS4FfB4'
        b'OI0Gqhls5fdFiEqkVAUcTZWohvQKcOwH+N9x46nvlL/ijQQCD/Wfyd/80zIhFTGiB1mteS9oEGWY9wstMH+Enmxi35vSeC6FmyBZ85tWv2Txn/N1pUsy5z/kblavW60b'
        b'oe1+MbOoKtVc2RgV1PvjeWPSJ068+9a28S981TJzzO0e3ad9/tVLuqoZB54ry/zrgqBXe19/cfrXB/IPTdB8fnzg92P++22/gplNJQckISuLF4pl6devj9DtLN4TH/pS'
        b'yZGstEHH/3NY3OWz0SdmZv+8t+bSiFeGy0eDsDUP3jvzgvnO7kkNypdaT2y+2/LgxUFFcQlX3nk+/8FXsrc+XX7nVEvwrISP+g6q23oks+dp+Qd/mfvPf/007q53/Pic'
        b'XxW3fqMVfokPb/0mE/K74DXBq1oejAS9sQcVex8OjidK2TDzsijPE4JXIc7dAzbG8GGKO8HpAR5nEQfB7fJ54DpBgShgB+cc8dBgmxcfEo2AIApsIkFWhmSw021hSDHY'
        b'6VoY0gRryeKObqAR7FIkT+uGF44z+fR4eCb0GfZO/x84Yn1LkNjRZSPwGZEQN5jAzqj2sLOMo3l3LEf7sRKkSkoQdHB0X5ohi7IDybGIkv/T3peAR1FlC9fW1Ws6CyEk'
        b'IYawE7IgICI7skRCIKBsCmqTpDoQ6HQn1R0IsdsF1O5mHwQVRFTcFREEFXF7r8pxfzqj4zjT4+74O7jO4ozKmxn/c86t6gWC4rz535vv/x756Kpbdevu59xzzj2LYcyt'
        b'vpJEUcxXSsLRHFCbvB4K6pfCWf+Ic3tBfZXj0r2qYF0d3aK4TRnyWlJb3dapH62YUTmUdNsR0T165shK7YYzJW4AL2k7tDumEMw2jNWOztM3nAu3fbm++t36lU2mPabM'
        b'pXE86Ec+xmMQxziwTRh4L4YMoiUsqZVhC/yXYFu1FHL5kKsX5AnD/JJmtKELEBMV0fxuncjC9EIuUW2MSSvgOeBIAUpmhKVUn8GlJhuB64xireYzHjQMhfWi+H6njLRK'
        b'tMUptgzcCnaZG7rMdZU1+gLAYjClqu5CwzKCRkxYOtravKqKO0FCIhZXTkghb2cIKAUsItjS5U3Yg17U9QphlNPVLUpoufpzzC8q3pNjv0IDX8f715Ir1ZXelm2iGSCA'
        b'ZBi4DGFBCujhkPj+Fv3uGXUYsHoOMRvtWoycTM4GMO6j75H0wxfp6zNowqQYnUWTotFESkRQC0m0xmIlwhTCGGNQQBHHmARvgtoIUysoEuQQwyLGnF5BQdVwCqmExfCU'
        b'Ij7je8gtzuMUC216cv3xIeMvntTZ6quumES0XYt/2YQl/QZfMmTJpfBbUY731UMnXTxpIhHLx7CxLA4vE0YB64bUc0IOehvUpuUJyzI10NGWsKCoBy6+wGqYFqL5pYQI'
        b'9SSsbagep/oTFhhG+MBmVvt9lHcOOpmErz1m5ltFU8ApSqavBoqKydCEcWLtAY73cN2cKn0bbFhx7UF0t6PF5zDalFxrWjnogXaDdnXPJGmRcRR8D80G0NxCPodUOGMf'
        b'1KuRoXBxwSF4XQEUootTR4QFBSj1MOdB8yIB3tbg1Xg7KyzAG6GzOIxiyrwIMSdQrtgLZojn2i9YZH4VTvtqL/vKXxrm4Z69333ye0M2ItUneMdxoayMJgjGkxbv2wQT'
        b'oYYWH55ZeX3eVpgW7yqv73sAMeFqU70hNHXFUT+QGmwXSbId5BDDQR7ZbEIhW/L6ph5nVQyZWVUOjOJwWPX3axvZiPNcX22vZYj+hHYKK3MMBJ3SdADcxC0WvRKFHITB'
        b'XmzZLq6QV1gX2+CZRZHpmdVrXWFXrGYKKD8r4DW0Mbctdij9MHwhpJ2K62r7YqfS30hnKW5Iu4zwhhKFPcxWcuCbrIxnuUoePHMnn0hKDyUfnmRn5OqpFMCzHLIt5xbn'
        b'KgOiIjARaD1uX5ynDKRUqdIHUj2UQfCNDC0oU/pCOp+iZPQkLnRwwjkd5sTrD00B1iu5CjPCbiOWTQnbKW4uCtvx3lLEGZCc4CMMMPmxx76Df+rnHNH553KpoHUzk7Oc'
        b'BlseglUK3B1sa2jy/jTJUQldJWltqz4x40n8PzUWt1gEizACBm8aOQrqF4RrQw3LujexS9jbfA0tfg9keCGtAT3TG5DM0b1lX55Rc8BtgmWy9oTFg7sBAcMpTPwQWH6W'
        b'Yia7ctJrxo8z5ibZXRfNDUK9krLoVP/w/YNOlb2R6mYGX5M0h25LTjsi/84LSVjNGxFtZ+CZC4tgG4alsFJQz1ZQYCCM59oL4Yl9pdxWr8hhEa+wAfCKdR0fLFRs7KsC'
        b'zsy7CMrHYM6GCMlRf5wfluCHHheqhzE3vwinKkbXTfCXHbdcNjRCIcWTr3D3ZWHAHcA6qqHg6hbYWSdzKUsUcmc/iwpoO5XI2QMIBzZnL3nK/7Vo6sQRkrFRmKBijN5R'
        b'lLEe07+pTzoKFbkT5EC0GmkMQ0zcL1DwaibyJzNUUT2OrbAEO4CKQALCr5h6ddj4hCO55k9xFKBicPiPRINfxGZnrh8s8b/eQPU/sTFWLKwBSJy0Fqp/405JVP0dfo5l'
        b'NK3HiU2D0jJWd3IJogJpDJZVTEJKJEYrHRfkJoHaypttxdjcYVOshucM/mBrQxu08Ltks2UWCsGAioTVy9pwWiriKgL556JhvcuxaOl8V156P1jxGYOc7MaZrBtCshtC'
        b'shtCejdwyHkzeDh2hNqf2Y0W9O4UMgefAi9C509P1V2F0rk/ZfYj74R+sPJP2giSyhsxaGcMaHN1qIkb1DIkUFhY7QhOkHEYFBKMxSQmoVsE6J7MyANJxX2XzgpZz5we'
        b'D5BZLSFvq8dj4q7p3A97vFSB/ee+TZ4SGeHJYZn1ygDWVOHdz9Gl6Uut+vv6xmbJPzQ5ozXGjAqKSDMqGjMqmXkNhT+pXhV5g34159bChgGtnNNmGcYimBwLMTUWhMxP'
        b'b6othldfJkYzRsUtOMhhQebIJKv6nlCoLOa3UD/flN91t4faPJ7GQMDn8Tik1Baan1kZy2CQ7/OTc4FjghVRPHgUpFKEdK4ZiV8eSdvdsM/cIGw211ENDMsHXJJUXAPI'
        b'uMUfSmQjla54m3wNpj19whYKsINfcz/4gBqNE1HMdSeKlFUvxjtyS0mc5ToBRliGmpMaTwupLNl4hRaLImySiDPimYICLQVLfUJqGn6WH00VWcikhN3b2eTrCLas8iay'
        b'cA/zAIeJNQb/RD6hoWP+4IR+/ehgFVEtj1gMdiAfbAtm19zYq2z8ebe7rqnoUClPMg8PSGSRuVFgm5Kwjx8nWZEE/LQAC9K5AnEXaTtcyrpFW4cEax749nV4mM0XcRcL'
        b'EUtEDlvCwkpZVQg+gFQEbl8Izmf3y3i8jjfeAI6QEYm3u8Mye97uXsR1VkJdEmpZQG2lUKY1YoMnchhoiYg1bMPBDVt7cZA7TAyMNWIP29WnwnzwQBi1NOyQQxzP+aWw'
        b'HekVYFleCQv4q0BPID+U0MJWtmQcWyOAHrf0R4Kr3J5wAVwAW9niU2DKE9ZQwKO0NIVIYYH2BNhVQrC2GhN2zIhAFCRCk7E+6GS03MH2G0dTwB9kxo8JXsHzDig0wTep'
        b'X+JboUlh/rRmmh+fYjPNh0p7SabjMJRIETfEHAPmCC4+nyIayqTt4xBY2IPMDdfoBBGKSBhbocj55UJNTTlfU15wopI29eYuszfqJ8nO/YFjbDdy04w6QBqEdnsaGtpr'
        b'CDcTKlJl/HHyxiKkjqQFCDt9oV96vDBsjSYaMGcTbZLLYhNcFrfkduVIOVK+nC/nWfMdNgmeWOiUzNo+IghM+N6ltfqm2fqmivaZlfUWrmiyVHOWtnd+OTsNkAu0xyqU'
        b'mpSlmU4hODF/ucyNUOT52n79QLlx7vaEVztQh8FYMYN2nXa4gueclwv6/dX6dSc5zSAlJncSQ4T5zXzKF4mztWGl16RLhJQ+TDcnu8aEnp3Cs6Rf3Ve7sjxotiWrD7TE'
        b'oe0R9A1jtBsyeF8TcQUxWHWS982hOIqo6w+cLvCUEnCtPPOittjC7DSbRYPLldGXGuSxKi4lC642xa1kX42+2BiGzk24pnW0tq4xGnoyeUxbC2piMO4FNlw+jb/kU/wl'
        b'kzDAr0jSBkkxOU71U87YTIk9IIaTcZ0WgipiPdmyfY0GzYPUuj9JOxHkyezZiQzSeviZKCUJJZkvhf9dPdO7dPpudphXG7WMP+XGaQfihDVkWnJG+a6CjOqSWbqnzYyD'
        b'TKI8jDpNsSfVWNPtQmJEFyIxj+e8tKoLT+hpMlP3lU+keVR4YANdqDxGRCIge3VALMWMC3iaCUSSAGTVCJzFtOZendR8QgQMM0QTiCNG9FEGPXhqQR2hm5kposfGs4gu'
        b'KJPrrkunTfWwpn0P5WP1eHxev8czL20M80+okDJ0L7TAboS4ZaYeBWEDCbeUUxNa+NbjWZhW30mrk3L8QO9QnaTme3pGePui76mF0XPYZMeJewcCkdoP57B/ci8YgD+D'
        b'khuC/QcmtA9kGmdOqE10yDbRJebYAdeLJPW7LFfbESxHRK09EIKfm842EDvPlWqPodHm4aLuMd9cLoX5tosrxBXSYouXKYKhTE/ySiusiIRYig7oESvaFtuYFA4wIcOM'
        b'dpKmOWgsbYm8OY0rvE0h8iFoDNKPkBYtY1sy7q0/JCtqSs6J2NXr5EpPX2R09emLjJantpvTQkJXnxYSotXhS1tipd1051QoKHkKjy6y1uSEOIP3MnhQCbjQlQ71TKbX'
        b'S8hIDNMBBTYQ3lrgrWJo/fIrZOL5FiMlmeL7sJxUp9JcYqVxczbi22iJJxy1wB10Mv3WL00QSLjPJUqxI2Rovia53x+D2wJSUjIlAJnnpv8oozr1mBlMpPNE4BzMp1Ny'
        b'jMQryYTVFHnWTZDIFBWGJV0iGVjMJjEKzCWSDkpWtXalfmiOvn7mbPQWtEO7cpa+YdbsdpNGATidot1t7S/r+7sH0+I0MCVyhA4PgUQx3K8kepsdN3HSVPR2OisQWNnR'
        b'ljy5tHBpejIEecZmFYO5NAgKwPJ8EiVZGNUuhda0edVNeGtPyuBOsZXKPqozkmIbgbnq9z2tq2YfdGMZWZVsx0mwMhRedZmwAkgQnWhrV4+dlRrkWdr9oeTwtuubayur'
        b'9UdQTRb+DmRXV2F8yHaHvuuKvhlnTkkYxvNv2L85Em2UEDjxxCyhPiyp3auVMWT7OFRFR9Cge0tKWiiwMznxwtmzYOUgJ5pwBlLLkxjwHxswrRr6fa2U1PtifsLovBNP'
        b'hgomjdU26Af0hwGO9YPaNn0HRn19sDVjTcnmmro0bU0pqaMXudlChz72xSKp88iA4vHAxwboX6IjHlGxKjYkhhW74gBiV0476LEtttJGYKNRcCdcxoTPBppera/JcIGS'
        b'FDrdwaF2TwuMocLvFoGJNgVQA4Di5VtQNw8YZRK1I40sqBuTQqeJYcF4AxRVEQd0soSsblgM+vGO0kBJKxyy2NAPJsISOkvCwjQ8L7fAlxYzFzHcoUVcShjZDG8280nR'
        b'lYwy4EpcliSkOgPviCZKPWOHfgmHh2Svngafj+FEpAJMfxiU8W+0INpUb3NLpwcV/ojTSQj+4OlJtrDAHZJpNCcIqIch4IJAN9kSucvOocB9LuKNk2c4NBMpqt1c/FYu'
        b'TXjzEE4IYn5YCMskPN5GWQcPpFlE7NwWxpOP9UzWgUfbwXNI/iGR5KK00x8SwhIegLNzQsW6CYd6oSkLWSEpNthdwvQNLiGaEgA1eR1MNZVRD88dgJe2Yx72xnhOAIe2'
        b'JOsE9mQR1LiICzO/HM76hGUenn4kxOl+JSHVY9xwy8IGX4f3JLXHtFMylNQo0krZUOdkMzoKZ3Q0TxtT8t7ERt0oZpJzykdwPrCWrqrM0W4K+Fd51RCJHILpKhTMZygU'
        b'SXLN5E5qyl4sKNvCqHVeQ9ASpNB7TPTyDUMghKLFoLc9YQmoildFyV2wwxci0rk1JVD5vqN9d2YL75MMaQLHuwz2wQFrSxBQzTQf7kvQgspRyHf1/p5+ZpynJSVo2JRl'
        b'CIITaR2dHRGBqiAdGLJJqsa1RhJm0Zh1B52sAaJEBQt8is8WsfOBZpKBCigHTcgwYF6Ydpun2YfaDX4aMlMmOA6HdgL+TOS/n8I4F96/kOKeJON8gHzcngBERkUn7SC0'
        b'uNCnW5pxFvyGeehGIZ7QEJ8vGDrG8I4JzuFtiO5EuJsRApwUFtC6ZC1P2gaAvdbxRLoBwAB4KCi+8+eYTzAPHiYqFnYHT2BICxiZJtezw0PB42ELrGCBf6U/sNpfltzQ'
        b'y/oNDPY7Ll82MIhni7Kai4P1NX4kM2SmDscnuDEyik1MUbPqSP4kiEhkefyopoM+raGA13BIC9LWVI4hjS/gZSGH7yrOHNr0TzOQFLae5EcKl35mR0tGMPZogd21cBGp'
        b'cxDTxjHMyhAF4TfMBEwOS4TzKwHnS8YxDewIzVDSHgExv8mMyGoNbywNdRL+EADSIQUwoegWHohLa5pAxWaKS9WeCLd2JiCFvqTBY/eyTXTq9V6KwIUxElGCmUdjdRIW'
        b'N6oW6wEE7N1ynpOSDacunJdJ0p5mpNkUmQs8BPeTFJlb0DOnDzCibjKGbtXuqEnK3Sr0tX30g7P1jeiXqrSXpD0+7tKTHI7jP4pQmyREsonHNAkQ5v3fJD/wzYmkBxLD'
        b'BuFBmiUog2PTlpOwzQo0raxp8XnrP2ZVvTcpSYCYJgBJnBQj/hMXUzA/JCAHtJY3+EOB3tH5XQGK4KQwcE8eCwniZBLKWdEwzGMzeCKp/ngPjL9bpgS8ht9+9MR23Dow'
        b'WI3qazhVdKIttwQxH8FUwtrQGMQz9ISNVNyUFjVhRVXwQEcoYfG0UuQaCuubsHowh1dJP9pPSJhDPZ/vjlzGhfDH1JpyEZWQR5SCzHflmsN0siwPRygZ7nMjZ+o6IrCh'
        b'wVvnqjU5MQQ3GB3Ey4s4/0LDhnQVD8iJ57rGhhFx8StFdeJa/E5WZ5DQi5XDr5TUi0NWFIatBaJrhU0xyrkI1eugBDQ6a88BblNiYz0PUotM3tNSfyyXcFlToMOn0EA3'
        b'NFHEgDIcoI937cR/906aX24HHgaGkoYnYWldCYOrzqWjoznziBFNWLyqCjhnPj50XdDhx+zGm6DP620zsF3CClsMFdV4ShBOSFj7XyXjCI8jw0qB3Bg4yEONRDOAlsBd'
        b'Wcmxx2+6t+WpNBCdOkih9Yishjnm6iBISeb4G+OC+6GFusKWhqUlmOywRW2Fe0Oi0g371uHHhmRZ0oS+aFnSlZ1sKMvRvTjHVDtCYjFdE6fp1EJfdFzkBRzWw5ISfeSk'
        b'rUh62b3VytC02nBJGnJWgclZSVYOA2MY8hIel9SlOCoXmEOjzks1rBv7Fo8HUC2KDwssyYN1GxHWMHV5aY00smWo5+J/PNAmU3SavwJTxoWDY6ooZg6VSC1KWJp8AcNj'
        b'namqIXm8nU3dSEABtQDEnpE+YY4ToZrlQd6+jicj4+42ChoZrBElQZzqxZ/lpyOdnAmZvjCZUpvkdrhzXSihtNLJkHZAApb70AjtUdLDXWWE685aITo6hmZsCFbjSjt7'
        b'UtqB6tIS8JxJiQcqJC6WlJwoC3IjRuWorVkmMaQdNoZcxqVSmBo8lLHDJsGcr+HRTDp/urw8LyHVzJ1Wk4HukudT0ziURhtUAZ1hIydoThmuLAV1gSWk0ChtUYSQzFLG'
        b'pmAatRx3zl2DFY0oWzUweDwLEkbMbkiaQrP1NJ/oMbStYZk34Qp6Q542NaB0NAFJ78KvPQunXzCvdk59wonvyMEsoCenx2OEtfZ4mHK1B2OpmNRZ6vjse2YQ6x6SWuJ5'
        b'pEoNQJ+F1Z7MK55KjmqYPx7PnQetKGtt8JP3TXTQgjigPbWYmaOEE8lF7FWy/cOS6EDoyqNmZLyuTzYGGQu7iRFiGXOGVswoKTCpQvXSmESCT9LCBsZSBGaUVPnoCJ/u'
        b'I8BshMVeHOoE01PY5lfITGeByuHVtTGgERXLOmFLTkQCVtcaFtimpXDncxdwF5qsicxMG/+EYOkYOHDe9Lnnlv0Ju8pU9DqB9XcQMZ4QVjcayyAhw3bf1hGi0UpYlI7W'
        b'tiDJkUiXj87yEpbVeMZuCOcYGqPxpE+E5uWnb0OsroZPRlpMxWKyEZbJuh+JzTzaqPL5LieNP2tYwj7D61vlDbU0NagYYJWZNeIkNJmSpez0GfHxjAtCaz7keuAqk5IQ'
        b'8j/8OtGAJBpfugeeB6hyEd/E+JAFmD9LPplFoEsHlu7N0jZFjtgVa8TBRAQRZ+dfYbadpJj5+4gLqHtXERfJCtvVZ82c4SyYSxQ/7FLskSx/KaUdkD6iOOGtWbsNa29X'
        b'M1sTdoWB0CzkVnLqO1i24urFFXFt70FJ7rA78JmSFXavtG7l1fFhN6sF7kvDLvjFkq0G1oASFXfYiiUqYsQObXCzNtCX8B6VoVmN+B7VMxRr2BLOCjtgq7evwF/nCpeS'
        b'u0mG8hyqirnaVWCIZZJR5dUfQ6OiYzgL84/hfH8cLfj1K1/P+/OkGhJtHBcnTJhA05YQPYAz+PmGxnJZgp+SsE4NdKgtgHL4WlTY9XtXezrZZU15FlNjd5Ciqa/F7w0y'
        b'VNTaoC5r8QcTPTDR0BEKEArzNAKGWpmw4cPmgB+IWDXQ4VeYyB+XRUJq8vp8CenCuYFgQpo1vWZ+QrqI7uunXzi/PJutbzq0lqgAiQxILMHQGiCCndgAz3Jvy7LlUDRr'
        b'jQMzeHzQHK9xD3wrVGFRvdCKhNzIBCR2f0erh75gCrES3sNTb2eIHv9gdGknU3MkbeZzLQYDwRnhLF10IJFDBhDM7J55LHQYbjXIzYZQQjllysFATjJADpWRCODSKskQ'
        b'pcjmDqVymbCF+CtQTKfLyMbMVIQ4h7ZAIZHYJNw5bSh0WWf4rShCawpekcN8AVPrk1A9medCFkP+KSd5YZGkoEyqaz9ePKVBRbPfspGB5jFlqKZVRm4Igh2t6p9wLVWc'
        b'jkV0VXXZgGEVAzOIpqRMGBES2TS5I3zM4PINa6ZlphgO1T5Ne6bibhkf1GMJmDuJzHX1oYHFpo8c050l0zECEGnowOBQgpV6YJB/xhmyNrSSUUixOiFCTxNuWtktwIA3'
        b'BXwB1cDfrHCTNXstcw/O9Ar6QrKd90DrWyymzAldFJFpHUr3DexrFEs07GUkjzSRrxo+NU0X5A0kr97KG9WkMf8/2r9RSgzQAiUNsCTFADlWm1Tozh/SYcTXvX1o0NnW'
        b'Lq50coK+i++rHdS2EHVbX1+P+lUiWdaG9X1Z8/TbMe42Gdkd1H6Cr1kw5g6R1sLS6RHXQ/PqofKali/b37UEY0Cf3Sa9NHt+S7DHeTlvv/HJhWc8FXjpetezb7039dmz'
        b'C3v3fd/pVJqUu7e9+LeHpNwpeWW/3TqxdsHbx9/7bvfoD+8d8PCdd9/8xZurX9Xe/M35ruGXlMmL+z775+03/kwefu+Cxpl1z8z9Ot7yQI+RR2e8/MkZjfWPxiNHaz57'
        b's7h98qOxdUenlbwmfnDgnf6bf+dun/9qrKlrwzn7b3rG/nb/+hU7z7mz9/mfvTH/wTLnH3d/3PLbxxsC2+4W5oy88fNrWx/86LYrG9/89JvWW74MHlHebara8kTtzrhw'
        b'8bPh0Z998+QTP5k+cf/Sf9+z7Kw5r+zdfmfpT9t7vrkvtH1fxfY+r/9xrL/wonHLv/19v4nPnFMlKzNmPjToN4cfmLFgxQU3XLu7JnIkvuTts550/fyD7GODP80ds6Bl'
        b'Wu1bz55x/6eBNVW3jP3ww6cevuWOaNGYDSOObJje4yf7PtszuHbnskEDf721/YWXhn9a32R/6e2cl8a+a++qfcledX/JwANr8zoGPjntknvOm/3gsaYFev3LXw+YXj99'
        b'z/NPjd9x+5BrLruwaXT0/T8/u+Sq5of9t8hXLHjg6c0H9U8/5v9+xyW7rh+tXHStd3vPRTfW7bjcvTP4973+5olrs94a/cbBJX9YeGDZB5fcdcn1b3eVZXt3vdzjl19z'
        b'N73cdqhH0zUtuj7V1zHBF4l1CC9e8Ksv2u9aNSIyYkjd/ud6vHx8a/DFD3Jf3D/19c03NG0897mxW6f+5XfDh/bavUr7S2LWvt82v7H08wXj2yfK+y6f9fI7Xyx9s9b6'
        b'wOF+h7Z/0fBu7eAjRc33P3LsoysfG9B+5d2rJm27/oqbH++I7WractGvZz9+Cb/n/ceue3Xxt6PUT89RH5pY8fgnR57rfP+3Y/o/Z790180P72jevf2j1tcfuWreoobl'
        b'oyPX7Nzz/sibZu/6+r1hj//6pYf++OXmL56v+8t3wXDDXb945cJXr5g377peG78d+JT6+ktHN+/4qOgjz4e9b3gp9vDynzeuP/jUT1f3+us781/6+HBT3vOfXPFoX8cf'
        b'Jvxb7dRFN111s+/fHj3n8smhL75ev9g3qLN+xZWLPv7qg5tunP7LP/e/9DdLCg9dGrluwqHlH2RFnjy45MNxs2tW3futPXDvmvsf/4/t8s3n/Lno/ld/9uarnee9Pe5Z'
        b'+2z587e+G3Hj6481793xaefZj9y77z/+et6F/149+uEhwbe2eX5//6fxm7c8MML/9T0r/rJn47u/35P7zqdvNyemLf3qSNOuJau0v058r39Rn9n/56vXvzxs/+Ive/cd'
        b'OvrcZ7966hdHDj39YY+dt4Se3Nn+1DdvvyF85/x9/ROhr7L54oOXT1tc7gyVIbwfHKYfRIejtdrGYTMqAZ61Xdq1XJ52ragd1p7MJSvqWn3PbHJZW181lNefquNs+sOC'
        b'dv2sNWQlPWmRKzO4dan2IMa3FrUD+sGxIRQu6o/pt+lXotriNv2xk/QWtQ1t5GB6ov7ECHYGakcj3yqhTbuDy9aeBkpnXAi9OZXC27XQCLJANIrBezwg1jYzx1D6luoq'
        b'Tt+pP8iFxzqk1TNCw+HDRcP0/SnhZnvt7LpKfVN55skyfNZYzF1R5wBsFg+heCKSrd2XOpQO6Ae7P/iv17aG0Lc29O4x7ZpgNQUV2tJxigNsqEbb2Itbre+ya4+sWkbD'
        b'U7G8Ik30ut6SKXrVb80h99oXtukPEmbWbl5ioOabtU1Aav2YjeAHtonR/8TC/n/5Ke/Ltup/9R9TqOQLNChGxMe34IdrkMmI/vT/HKLb7pZc8JfvyLEV9MjPF/gz5wp8'
        b'cYHAD6gcMK6k0G0pnCwJAl/In+0bssrF22yYGpQr8P3gf2mZwOfL8N9W7BD4PEngC+TU1W3He0z1K0HRaoEL/mfjXX5OKe8IoLq3W8ixFPfL510lObzD6uJdIr4vhS9L'
        b'eNcS+B0l8GW8q169NynjSvem8r+ruJufFGGNg7aUMwnWvZ3pfhZQ6lc9/GJtA3O0N2eWFte2WDl3Ua72lHjGEO3Jlu2PfswFS2F55TTtqtr2gv83Z+ZcW1t7/RPP/qf/'
        b'uSULH/z19tCEr4q6Pr+37OL5BcNaNqvujitvCX56+1c/O++Y2PGMLHwT2d33vKlrPddsy70if9fcF9bdMer1htLhlzRfdWx49GXXoRbtgaXv7Pz9ZS/usj995+67/vP2'
        b'0DJ79pC+bx19cdG/113/x6F1V9nnf3Hd3G+PLu2z672yrzUp/qvHJl2+ZP2irpfPfH9985GX7hy+YEbwvqVrb/76m/N6lncW3HfPtM9ee9bXb07Px6fsWPXKh+/evXHs'
        b'2Odvea35b0+e9e20mr8OHvvo9d6KkcHDB/40/lXry8KozsrX7FsGHn10zP6pY1Z6H9nzsOM3RW9WP7fgkv7l12z65ZixD/1y6eMHfqnctGTlwdn7Hv72mc33tT1381cT'
        b'b//ilbtXfVDyzDuzL17wuUNtfXfC0cOfvZ51qCD7q62fHL9xfde0u0dMWDOh9NPhC/589dCumY/+8bvWl3+X+OPVi6+/+6xHxt9+50djOqqG3fOq75kbuuqLHn/0hafK'
        b'vnz4FfXL9qcvPfzBK5GVKx+p/HjxH2q+ftbzk5+9+dtfPfz5NzXvvnbwqdt3uO/Vvz64/osFyz7+u1r69JBzK5Z82XBL7Yif37Ru69pvf3lHYEVz88/HvRHpuuK9mZ/1'
        b'mb/lw3sDe7eELLzdWv10/+yib2xbp7vX5M99JvfFe25dX/zJ8lvjBYnf3bqh9Hjh0ljTxjOflea93LZ23u73S3odeabEWXlQK+598fvFo4/89IwpbwX6zPdkXfrQZZP+'
        b'8Hr1LZGBEze89dKkfh+9WTzgqvKJtLUN027Q1xuraaO+odJYThegG3xxuHbLUso1Sr8HI0doW9he3qBt1TZjvlztCVG7bpx+EwsyuWscejiC8h7RD6VFmSwrCaFfoYHa'
        b'Xu1ohba/UtbuOgM2yKv4pSWjiMhZ0tdRUVc1dMpYdDqkb6HYcxvr9A1Wru88S95igcXm2apdo8fQEXeFfoe2uxtP3PpV2h4iVPQnztOvqYOc+sZyzFchc9mjBW2/uDLc'
        b'xeKu7ID+QQ+HzdMem6FvgnbO4LVDlxdSO6FrV+t76/TNQwTtnpGc4OcnLhpFzmTOatD2VsyEprV1zrFw8mTBrU5mUTBv029GN3JQ1RDtgYuqeE7uFIafz+JylOi3a7fU'
        b'4cty7ah+AEPS27SnBS2q37GKKhyuPxgGEq+Sg7Y+yAlhfpK2vpNIikuLLtLu19fDm41ajBO0Q/x8fZdMr/Q7VueSm6aFFxmOmhxL9N0ssuAhbetl5NOO0/bDSEf4Gn3L'
        b'GKpq1hx9u75hTjWvXdMO5a3nz7Ppd4bQ2eUQGPuboLIYEF5DZ2u7ZujXY8zP+CwipAaeZZnGazex6ISbtZh2p1N/WN8H9GZdlWMIzPiDGBm0WHtS0nbpN/alIIh99OgV'
        b'5O8KGr9dP1yB3q7qgKTstVwaMRNqpaYeLi6BaZjJQxF7oUE3QlN39KExvUS/Vb+zQo8Ns2pHtCPw7h5+kb5W30ozcaG+zqVvAIpM1Ha2csIV/ORhleQyaMokVx0hxpmL'
        b'9SdhxGXOqV0l6HeW6jfS+1X6ndqT2oY5c6pqK2ZetpgipeaNE7X7J5Qxx2MbLxlUxyK1zqmn792XDwiJ06q1nVSxb+IoaK/MefXH+XkcMNgP6JuIBi/Rj+h70RnZVn1f'
        b'Kv5qjXYbi80C1KV2rb5Bu1d7GCCOfEZIjbz21AjDT1FggLWuqnxmpQpfyvOEAu0eqBAbpO2v1e5ma7m242xcPE7tRkG/Z6F+DcGOtk1AH2kmFVys3YpODIFBWCfCCr+7'
        b'iBWyOdCvrraytoqgxsK59fVzy8R64Cx2Mg9Oj+o39Kir1Z/QDmIcV0nitVss2h3kas12gbaD+b2fDePduKq8FkrXrxO1o5dpjxHcLx4JVH+t9sCQ8mEzKzkuW7/9whxR'
        b'u3Ka/hCtucu1W311FQu0ozNqAdCKee22UdqdDE4f166BqjcMBVbmNrSAgvfn80hRQ+dokT+orx1SMdMCN9pBvo7Tb9SfhpWDXM1S7cklsMZxecUAYrfCSoWhCQv6bv0G'
        b'aBdBebQdV7seu0Bbi5EspRwemKd9U6nLsrbWVwcszuWXjRrJc1Z9myDrj8Fs0bFaXNs9M+mMsVS7FuMCkDfG9dpRhuqearnc9ISo31KH78kR4mWDqWMXL1hdR556TT9q'
        b'bu1WbZ1dnKofnUk1nK3vW5r0Olk9fFbKO6ZXf5LmdbW2R9+f7pvSMo9ykWdK/YBAfNPAqYAIAbFUAZgMhTkCaN0GmES/85xZOC7QgCrtPombrd1vBeS4H2YUi9b3XpLn'
        b'RF5Se7q9DT+vw2WVr+8W9bsAfG8ODcZMRyZocae+eViVduvlM+s76GgRYB5IDsw9aolcC7kPsNAGT4wYQ8ivesZo5+xqHrqyV9Af1bcsZzB1s/8K8ty6ubb+7MpqBMlD'
        b'gn4IeM119H7O3Asr9M2z9C11leWyfkMVzHePUlG/brC2gdo7qlZ/qA4BFkYjXls5c1h1WN8+Y7bMVXIWfWeWTFhpurZPv8XYyDZpW2bMKQeOTduEu1TBQEmEZfEAjXyX'
        b'vnUK+vSdMwcy/mQZechxag8BRGn3DabqRmC0+b7axpmwtmatwmUJyHuWlSvSD0kXlQKOJc/im/Udjeh45yAVtX7CHBiUXB22w9sW6zvYpnD3BBuOyqXaE7SXSVW89oD2'
        b'xGIK76jfxs+B1q4D3LZlGOx95s6H7e09QNLWBfQbQijIC/Do2X3olKWzrZwsCbbJ2uM0aO45bnL7Ct0E1jpaWwXDqt8JC2he++kqHhkc5f88Z/Qv95M8uCUu7Vb44ZyC'
        b'YONP/HMAH8QUTtBBm8RjHjd7YxxJGBwbU8cTHMYdfCdgMCUbORvKzyjTReVRHnjjIjNbG50ZugRZ7LyCO/mvTOaZSJppE6BuRdAb6mjzeFJMlynXv49P7x/eMDbj63SP'
        b'lfQuqT+QBf/RTQae3gefgd9GdKgCf/GFsYV4GhIfDFcBrgJcRbgWxBY2c3BdEFvYgldHbCFansX7YH48IY7zUT66sFlgBk8RDjUMfGKrFM9utUT4VjkitFojeEonKzaf'
        b'rdUekeje7nO0OiMWunf4XK1ZEZnunT53a3bEimeAoRwovSdcc+HaA655cC2Faw+4oj2sDNe+YS6WDdfsMJ19xJ1hsjyI50C+fLjmwbUnXN1wLYDrwDBpNcatYSneT5Hj'
        b'vRQxXqi44kVKVry34o6XKNnxM5SciE3JjdiVvHhxWFS4WBEqX8f7Kz3i5Up+vFrpGZ+jFMRnK73ic5XC+HlKUbxWKY4PVXrHK5WSeIVyRnyIUhqvUfrERyhl8bFK3/hE'
        b'pV98ktI/fo4yIH6WMjA+ShkUn6AMjk9WhsTPVsrj45Wh8dFKRXycUhkfo1TFRyrV8eHKsHidcmZ8mDI8PlMZEZ+njIzPUM6KT1dGxc9Vzo5XKaPj5yvnxC9QxsTrY451'
        b'XHyAMjY+JdQL7nKVcfFZyvj4VGVCfL4yMX6mwsenha3wpiwmhG1hezOOUn7UHe0V7ROd3Swpk5TJMH+OsCPuIo2RlHNSdzQ7mh8tgJyF0aJocbR3tBS+6RsdHK2ODoue'
        b'GT03Oj1aE50RnRmti86Lzo8ugPXQVzk3WZ4t5o7ZYuXrhLg9ysKes3JdVHJONDeaF+1plH4GlN0vOjA6KFoeHRqtjI6IjoyeFR0VPTs6OnpOdEx0bHRcdHx0QnRidFJ0'
        b'cnRKdBrUXBudFZ0DdVYrU5J1WqBOC9UpQ32sJix/ULQCvjgvWtvsVKYmc2dFRfLungX58qI9jNaURQdASwZDS6ZCDfXRuc09lGnmNxFnzB12Ug2D6Fsn1JJF41kII1QC'
        b'X/en74fA9xXRquhwaG8NlXN+9ILmImV6snYR2ipSSdLlDpzHiCs2MOaKDY25wq5Y7TqBTvnxSSU9qWRPLneFnaRKUsPcyJOzBzqk7l4PDHdEZqET41ba1eIQ+pzgVvCm'
        b'7rThSOZ4z4HBIeVlLUwls6GssaPFF2rxlwvqJWTxlbbjnMo/kqfZT7IxVPaKW5IeJPD4Vt1nWoOUS4DdlnlDzSraH9i8nU2kskLmzXgoHWhOuEyVHVLV4dH7RSugQ7hz'
        b'oEPl1jbVGwxCSvQFlqERLOpyqUc55kKIO0Y6F9iuY6j9cWw3/pB9ACojBxQvIFVyPoAq3AmxLdCWcEDpire5Ae0CbM0edvLJ3M6knBMkEXFCbqZyEs6mgKdBXUaBLjFC'
        b'p2fl6oDftyb5yAGP/KywhAvug6EGw82jDVLNvoZlwYQV7qgwO934g6EgvSXFc6phVYOaSqCGK6boO7px01M1SCoH/gCV44MpbGhkH6he7yp0m40J1CighKXJ521QEzJF'
        b'6RieEBtblpHSNjpCYSEVEg6MhczumYrNIWOSQ2pDkxfjJno8kL3RwybSCneoIpCQPKq3OeH2KC3Bhkaf19PU0LScKeXCwlCYpy5kLo8LQ8ozYtvhCka6nsJKoHGZ6Qsd'
        b'PQnFmH+xAnJN6CYnh+Q3J8K3lyxibp2WJw1JT7JE/CHvQLg4P0xqeBEJ4DAXbbKNqMolm218Ft7ErIDeXABWRdiOMA+IR2hGM4VSheKjkPGCGCsjFSspLMUcK23q2pgr'
        b'YgkLMedKQZ0B97J/CKU49dKYy8lFLDFmQifEHLE8eOOGvrt64VjIMSukz1gnhOVYT3Sr6d+PfkqC2+FpaaygGb2o3IjKVVBTD6jpAOUvhO9LsDz/lfC8TyyX8n0WywV0'
        b'Y+0sI0OvwogN8lpj+ZBXgk1CNOyHnoeRldCPCpUpr7Rt5dUzYzJ8ae+sptJ7Q07T74oDSjG+DtvhzoF3FFcG7VHs8zg2EjGeyonB19mxLKdhchYWYzn0NqsQPcQCG6hw'
        b'YSe+CwuAbrN6ccwSihxc2pm7+aTyGo0slHkPzIgjVgz1CzhCYUs+moAUsvGA9/9Gbe5ljggpoqVWjeu/eITxPy+A/lEyalzbn+Oaryck7WaEKpGqqGUjCzbSv8nDP1Ei'
        b'nUcXEcKFRMzKfAFfzEuiW3ADmVuC34kOeAZwIyRBJtfYgwhkfiEYIOOGaS43QCY/HWTgrYgTF5NgnzozA4hw4irgG4nucPlbwlLwMwoDL8fwr2AdmT9FYCGra8NWsmax'
        b'haE2tnAAaIrHc/7lsd6x/rFBAAhFzRZYxs+H7bB850YcMdQic0C5zrAj1huA81ew7LKdXBHuyiLcu/E+7CLwg5LCTqAPs43l68Qc7F3YMZ5rv34R5/fHBsSyYr2buVh/'
        b'+D8I/veJDWnmY7lYU6wPglg+UJjwvDjGx3JiOUiZtVgJzC24iAGccsM26FEWLHi4hgE0Yu5CLuKO5QE9gE/cvTgAmyyiE5zwVSWFfeqkEuC+GXq9mY9Y/J/BEzk2FMrM'
        b'DmfHCuk9IAZob3asjFJlRmoApQYYqYGUGmikSilVaqSKzXZSqjelehup/pTqb6QGUWqQkSqhVImR6kepfkbqDEqdYaT6UqqvkeqTHDdMFVGqCFPN2bBNVCF1H+Y2IwJF'
        b'JAB9jQ2OZUGPc8I5W4W2tWGJfq1bheB9tF564XqBMmDsm9HBtNGbXlwzuWOL9cB1BqWK5BJAwpEnF1b4vCIskc6jlIFAcv+fgGx59b8A2vjvR02DYKsNrk2hJlQBFGyG'
        b'72RZdLO4W5LAsz+ZgpygiW8+5MyXzTDI6HM5R0LDX3T15BLyRAcgLDd/qr88wSXmAMLDYMnFoktEXj6JzkzPp4TOmJ9DQFgSLB6bgc7kGJeGzsSYhXZyoFRidiDwAY0x'
        b'ZeoM3zvdEif/BL/1NIzbZdMcng2jiAOR0SGn2aH7sEMSwAOSHAJg4DzWCaY/iZ6kUbM7lrNOUCvpjRSmvNDBrBgGrUAoygaMlBWzshTqiMccWwbxWK4zlocQh0NF2Eq0'
        b'AD6N2UcD7Tc+TTscMBvgSEPDGe9zYjam7Rwmd+8IjacxfD3+e1fr7XKaOZMkkHG51cGXiHjH1pEjtY6wgDxz2P1ISQLVF8tGKjc57BIb9sAgGvSeQHWJQTbsmC7ANFIw'
        b'5MIbKERYczPprWNLMQ0cWo1bC0lJH1MZQww0W8wK2xbQpLBdLA+LwY0mPc1j+RJQh7B9dtaELepbGEMQkSVsTBbYRGASI9Y1jjApbMM2ly9xIW6lQ32F+UdhsRDpm0Is'
        b'o/3GRRwx2W5g+HtE86O9mq1GvBNbqiagGi2k4l0Sy8Jn5vdsYwOSwQ5QRW3tHB+2wLU5WYMdhRr07YXwLTyDN/bkt8l2ABVauSjllSXDpiXDBWsy6h4yHtBlGGaKGoD+'
        b'FDBECzorDFQi6WmYxCddI4kJIdSoPo2s4vP8j3ZekXC3BD2BxmbPahU1m9Uv5aTBiUTKzw7GjgAPjvz4PxQbouhfCcHrsmFFlAYyAtP0Ro3vPEDlsiSRZT0qzKBtIPJk'
        b'st0tFlrxaZ7VbYhp8/jyQiZgIBXcyRyZ/K8Jqg/gs/348yD+HCAnAU3oryWoHiQd+y5fS6P6EN22NoSWq4fIHhluvA3ow189TFYjLYpaSoUC850QGxqBbV/eEESr5YTV'
        b'cDmUsAbNm2W+QCOw/OVZ/5whK1/0LyBP/9+ff+QAAtdkl8VwjMoJgnTi4YPbUkjHBXg0cPLhBPuTuvlzdfv0H/+Tjf/JtOwS86ySOGsUQKDYvAJ/y1ySeGYJ3o2finAp'
        b'2GTiDgWB+lk/v1xU8bRFRZzKPL1kq3s5ct/vSZfoeTwGiLY2tAGchlQMqUumrmSuzw5C9hEgTu9s8rahj14VT/7wWKSpoSPo9XgS+R5PsKONJIEoNkMzEHjq9KQS6i8y'
        b'vS6k2YWObw0oHT7vRDoPQXGTJACZKAB11N3hzBrjaT+B/KeaSnz/F9a47Aw='
    ))))
