
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
        b'eJzVvAlcVEfyON5vLo7hPgcYYJRzmGE4BhHxAgXlGMADFU/OQUaGAecQ71sZRRQ8B8/xBhUdxQNv7M5hskmWEY0Dye5qdjebZJNdTMy5Sfx3vwfe2f93P7/v93ewm2e/'
        b'7qruquqq6uruevNn8Nwfu//fb+bhxy5QBmaAuWAGVUatBTNYSvY8B/DKXxnrJMWUtA5lbBZQck/2tywAOoeZLFzDK+MMwKym8Lud8ikOBRZxHdaKeT8pHSdPyxyXL6qq'
        b'LjOolaLqcpG+QimasEhfUa0RjVNp9MrSClFNcWll8VylzNExv0KlG4AtU5arNEqdqNygKdWrqjU6kb4ag2p1SlF/n0qdDqPpZI6lgc9RHoT/4xNmu/CjDtRRdaw6dh2n'
        b'jlvHq7Ors69zqHOs49c51TnXudS51rnVudd51HnWedV51/nU+dYJ6vzq/OsC6oR1gbuAUWj0NXoY7Y12RoHR2cgxuhodjZ5GJ6OD0dsIjGyjm9HLyDW6GP2MPka+0d/I'
        b'M7KMlDHAGGh0Lw/C4rVfFsQCG4QDolsW7ABYYGnQwDsuBw+UKbA8aHnwZBDymtpasJA9HdRSDuViVm7p89Pkjv/zJMxy6JldBMR2uWp7XF65jA1IXSyvK/STocOAIRS/'
        b'6JEJ1eP/bchTTERG1JAnRg2ZUxJ0E6J5ICKdg24qkUVMGYRk/udN02XmoM1oUw7aBOvhdQo4ZrKgBV2Am0qp5yjwGKBgJX7scK/DVGDBACwsLhaHHRaeAxYaHwvNGQvK'
        b'FYvMHYvUs9yDFg/Wmw1PNWsZixYP9Zx4WM8JglrO6hfPS7VPxbP2/188CkY8lpF2wAkAt6IstVoVVAvoSnlov8zG1SoOOyczlZti7YEbrjOPqFDIZ+QzlTftuAD/K0qZ'
        b'UyH9XLoYtAK1I65+5OTHeewBUvo8F1EfqU7EZWXcoNTEuI5UNVMWOyCK9dMMU0Z+PuYbQFfPcv3GdbsrFdkHViiKPFTpl0EvMMTgBnSzEK0lUxUzMTISbYzJiEYbYWt+'
        b'ZFYO2iKVZUZn5VBA4+oA2+GOkXDdrBcmhDPAcwmZEDY9IWQyQDn7qcjZ/20if0Uj7V4ROZ8R+UW+C8CalSQdUqRey+UzjE5FHagNM7pJko02oQ2KiRmZ0swpID4b7YId'
        b'k73h9nysezvAXK4dOoAu+BhIz1VyJVUrh5fwALAVzIcn4VqDD2EcXVagE/CEHJ4nTftAJTwATxu8cZMKXkZ70Bl4UR6P3+BOUFoEO+jOsBlsQjvQNi47HAAZkOXBmzS1'
        b'Sxz5wAuAlC98ihQsXgoz7V+O8ADYjpI4nCKhcLgeqApKEVu3ELdEBQzZ8+6Ifas2HNx2dtuiISFswZHY8j3yWK9HO1J+THE/lvtpVCKPZ9oYbv7C61O1L2+941uDw8et'
        b'99rp+FaJ2/szfjcBgXx+fvebe+HON99bSa1M9ptkO5qSsMQxxFSueNhYklH30Z/edNK7esKRt5z2fg5cClMDfa3RHmLWY2KtEfZj+ViA4hxDdBQ6DtdhlWEBb1jHsY9M'
        b'fOxH2NyYXzJuHBb0RrQFbcJqPoyCZ9EVtFrM6WVFirXOGObZQ0fmTrRy5cqffEaUa6sXKzWicsZXy3S1qnL9qF5H2hEXlhXrlYufK7MIcg1+/LASPEqjgJtn45D6xaaJ'
        b'G1d87CPqGpTcMcU6aEy3z9gut7E2nwBTWZP6jo/ErL/jI2/RG8fbvAJMyqY8Y7rNy3dXRlOGSWkeY55oUrV4t8y3uLf4W6Z0xHVMtMzoCkzp9ko1pvd4isze3Z4RXU4R'
        b'3xDV0xLdE/N6uQuK1QZlr11hodagKSzs5RcWlqqVxRpDDa55iVMefhSJCK9aF1Lpih/PcxRCgBLw48eV4LuxFEV5PnTxra9cye9jcSmvHr5H/bCHHNe1OTZ71x57zx8e'
        b'cQHXbeDtJx1Rmq28weAQP5pdynqdkZYRI2WRZYo2U+qpmbJe8IxshxeMEJfZzxkkazm730xfqn1qpnNfNtOnBDw1U16uAfs54BgxCm2bDFuxS4kG0fJ5BuJD4Y4wJdoW'
        b'Mh4HEjEgBnaMMhC3D49Lc9A2bGStXNp2QJAqCg1i6ZJwm/qzh8QgDm4T1zdR7COxx2LbyldbrpqS7ev96gsmm4Y3n+gcEb4+13z63oTZtEpPWOfQwkFi6nEARhfkQUsC'
        b'Oi3JikbGTEUuF/DhWRbah53APjH75Tkk4c3ABPbymbkrV1cX6xc//0LrppTRzb58Cnj778ppyjGHmHXdXhKsTK5eNgHWv2Z+I7fH0980ZNuoLqdBWrdneqUlkujllilL'
        b'VHot4V/r+RpdopWJ0SVfokvPkyAZUKafsDJNxsrk/58q0zZeCDjMl7Fpd/T3+Z5UAksQ5TShs0pguJVKe0GpIzyj0yfGwpsyDmCVAHQM1qNWGv6duV5UEmvhdJfYziqT'
        b'eOk0Gh7ugA1FBGE6rKcASwlQK7q0gIZfmupLjWAt1FI1nVUFQx6Mol0pOoe2lhN4HjKyAWsuQCfdEmnw2iV+VArrsxwW6FxmWx5QayD8wzXohEqnHxoLV8L1mCANQCcy'
        b'4Q4awXlwAJXGKlrokNK5TOAVnUM75JigVBp8oxcLsKpx7yJvGvjrKiGVwSpwdBFh4GkCH5r40Rnoug6dHxJbiI5h4uEagNqTGeLXrAimFKyWxc5FnctMqfoYgwBXzsCx'
        b'zBYaYcxsLoZfC9B5tBddojE+VIqoCazGMq5b57IClbsPza4bPBCo0w6JhVf0FE3PqQi0jgafxAqh8lmCSewJGNzvTpCB9rONiXg1aTfExaKV8AjmFy9eqB3ur6VREqvC'
        b'qALWg0i7WEzT7D+Np0eQDUP7aYwZMzDHeG1C53VjaHBFfjg1i/VDpn0NHkETrmMImjlWp5PHws1Lce8rADoNN6O9NPhnjpFUEeuzAA7o1Am08RMZ+Z90wACke3gwCc8X'
        b'3A1QR6qWRljkGUWVsVKwpd/SCZS9YpoDvFKa0Q0Gwwyv2WGUPQBdjppMowRypVQFq3EkO6VTV+C9NIAmSaFBZ1C7zskxVIE5QBeoBHhtAg3OGS+j1Kwaln3KLZ1JFsKm'
        b'Jw0dN6A2vjYx1n0CEdAxgC6hehENf9QljqphfTaaJcLdl0MxPWlwlT88x0dnh8SiNYMxBtpEseF1xOiQ3iCn9CyBykGER0iw1zAjNMNr8DTfMT52tBueNbSTcoAbC2ha'
        b'7dARDz66GBcbpCJdraMoeCDC4EU8pnahDrXXusDVUwkXBymJxIEZ3wIPo8s6B2dkERC/yEI3qcR4dJ6WrzgGXeTPN6CL8Cq6gh0zOkuF+aNTdI9D4FF0TMfX6kXxBMtE'
        b'BU13pukbik776vToEh8diSAtDZSkBO1jzPEw3LVE5+Ls6A8vsgCbS41E19BNujt0YNh03OKC2qIpwHagUpB5KkPgNmiCFtw0H6sO4aqDkqHdaBtNIFqJ1Ws737kGborI'
        b'5QB2CJUCd8FtjJyuTphLK/c1DbaGGoDacFCwkW6aHAhPYCtPQGun8wCrnHiFjWgVM9xGeKyW1sGLsJnLWN25RfAGoz5GdCBdh86idlc/tJoI8jSVgNXDTBMzBe7216GL'
        b'uDFORtpOUHJkhufFrvRc/uwwhFrIsgSyi/DsD/vAk650WJJILWXZy1lFWEmdPtLTlVHhSdRK1m0tx61TZ+L7KBh3OGg4tZZlSWK5YVUo8Y5kKp1HUEaWyJc/ARvFVE0p'
        b'XXk6aTS1iWVzsJ9wS1ewtIBPV34iTqUaWfbO2Dh1BWXiZMamosZQ21nGcn4shvRfWkRXNkxKo0ws+yVONXj0ZFYmXRkcM57ay+pU8Gtu6WyzR2noyj1umZSZ1RnlAjor'
        b'C0pPLKYrnyQoqBbWbal9SmelaVyxI+N8ivOoU6y+aZyUW5UFS0fPoCu/mTeBsrBa/PkiDFlqH0tXZqRMos6zYsN4IgwZvldB6wbssIO7dXxHlxloF1YOJypluTc9j0lw'
        b'FWzga12c0YVwrE/uWJ82wot0U2gcWoPa0aVaHSuaTWu1JABtYaa4FW1FJ7E5YF+pgfuIjm6nBudJxRyahNWz36L2ss2AqrlVWzDzQyY4bs9+hzKzzQJH0Fld4OpQQlcG'
        b'+L1LHWGbljuCW9UFC7+LpyvnLnyfamFPKHdKwZAzflz8wvaFOxCYlOPHDm7/fpJD7yVBOfd/YNf4yhaGB16OjcJzDSIiloNo1VhYn4fOwQa8Nd6CNmTmyNAGHGv7FHEi'
        b'nNxp7jKHscDHPiQgKFLPCVAxwtmjcwCP2WEkPlDUZA0HtDX4wr0p2TFZ6FI22pyXiXeUaC1rUU4WY5p7nefi7d15tDKIbGeo6QCe8rBj1pgDlWi1JBJH+saY3CB0nAuc'
        b'5rJdY7EDIUQvjY+D7ZjwZLQaHQTJcAc6qSUU0GRkj+OA8xE4dkkpUrdmpTKVptF24G52II74i5zeWjoe0N3gZWAtvCyPXRJGXraCYsESA13cDnfD+my0cRlsxALYQk4I'
        b'suGWmEzYFkkBkZ7rIkJXGHfVnGUvT0CtDjQWKMHbr2u0FBfB80sleFdLHy3gLW4mB3iK2fAAqsOr8yV0iAkzTlXAs/J4BWwHzIYNbYVn6H6F9qhJDs/hZfYA2eYdAOrK'
        b'KhoFnkDnPORy2Aavkbf9YO54eIUOX/PQyQS5XJbDI1MI5mln0h3JUQM6JE/0RXUE3ATK0NXRBn9c1qrggewsQlsuMzEuNQFwKzuJZUeLpgJd48oT4SF4kIzfDJRpAfS8'
        b'ePjOyVZgjBjUIElZRAH+DOz8sGc+J2bR4bIyBjbKE8fD/TgSxctw+Qwx3V1+wTh5YjRcS4jbA+biCbtJs8MpsUNY0JtyeOgGF3CCKHhoVDqzRrTDdtQuT8Ru9RI2HbgX'
        b'VMQiE006zwtdkZC5QBtyYdsweIwDnEayXdGaVJrlIrgWbZDDi8Js0o0ZqKEpg8ZDLXAz7ED1Csy2E2plAza6QcE9cHuGIZeAtqFjIp0iMzOHnBs93axHysRROTJxNMsR'
        b'HlXCYzjUPBIZCVt9JGK4HR2ReMHtPgnwijc64guPs/C64eWGQ4rzPPUPT548mT+fA770dSOqKP2XfDGgOXPGCr9RkhudgW5IOICTQsET0Fgm9qKJj1M66py1BngNnSfu'
        b'aj8VsqCMiXEsU+Ap1O6iNYQuIi0XKTG6ClfRUhwHjcGoHaMt8CFNNyjJcniYwTKG1OowDl5f9zAOLhjdgKeZRbMFm/op3XyDI7KgtSSyvEqJFsyk21ZMycdLWC06j4Vy'
        b'lUuHI4PQeh1Nv1CCFbMdtznHocMUHQ3ECyqYSds+BzXzXfhwS6oQO+IZ1ExsOm00je48HJTqHWvhOS8SEF2nhNGogUYKssc94xbUCg+SoVZRIrTViyH/AtoD61C7XovO'
        b'BySSyO4GFTBhMI1WjY7gNfgc1pNLeh6gsCmgLRXMQoFOlKH1fHtnRy1aCwB7KJUhC6IbKmctwEHffKfYAkL3bioC1VcynsjijI7yXZwcXOE5jDGcyoTnYQfd5A/3wyN4'
        b'Mde6YEU/j7lyoYZmFTHkXcY62oDb0Dln1DYLtw2mUkemMLa9He6V6ebPd2LDDUS2F6kglpYx4dN+CTpHrWEGPElmayslUqA9NHmzsLR38HGTDF7H2ulBxdrl01blFIp1'
        b'cRs2HunwwUAKr0MTbYxatB6ehfWujkHO8xdQgIPDENgAt2IWSW+OqBldIDylLe5nqWOi6uuQU0D3R2xQWb67GyarorI1d1Pc2n61Bf0+YpsDJ/5TT6hubEyi3PdkqG3t'
        b'mYlHQteOL4kLSad67Sx363vMwsGfKDLUPYNcOv+u7XU6t+6TdbN/OfHFvZPab+//ZeMXjxyqHve4TEzfXPC+w07HD+OGvZm8d3q7ePX9G2+Il7JnRH0x4v7QP31r2pY4'
        b'ynL0Vm/LljMfqbvf//TLn9brLtz/MFGxLvLzmsBHZsUVaW66z+ODtozxva3xf99wL27nNxMiyvZ29cSUCereHcEpL3Z+s3LvX61f+z0++kHKO0mRj+xSImZ+ttnMN3f/'
        b'VdzF+fAf5zrz11vKV3tbvmNd7HUNfCft66Bl4V9M/sufRH/7YOq+q5P+Ft31S/Tj/eZ/rvzjzQqbq+bNX7l+uod+lSfqViwrilzbHfLJralH61bPGfavmzkVJfvUq59M'
        b'3fLuxKE7g4f9a1h67sm3VKJDsdcknnPP706vDy78IrvH7Q2F8YP3L6uNT5b/fdGvFx8P0tcKvv4hc0fsFNV7b/kID2s/Pae9c/iHyK/3lmyRzFRV3J0wd+rkubNXv7Ol'
        b'bFzdIctlu4tZv+h2nd6xwrr4zsX6Lw/I5kxvXtJ3l2356sM1C/cPfZL29Y8qne/PWxKTb5ov8L6Wv7W9O+iX+u+Ofd7w3YkPlvT4wtO/vHcn4t0/PaE6Zux12Pqp2J4+'
        b'MoPr0c4ZqF6aix0Z2iJNG40dNjxJPPb6CTQAuuIyWCILRtczpVFiGQZBGwAQiDhzpsJL9BnFdLwCrh44UoOtpf2nanA1PEi34x3BuVCJDBlxCNaCNkgpwIObWdFoPTpN'
        b'n8nBlSnwWLYUneJGZqCGbArY4/EXIaP4MW1A6+HVtOzMHLgRNUXl2AEeh2WP9pU9DsZtfnCDRpIhjcKdog1Y/bewgedwNrqOnc8etLH0MW1kF+HpCdl5eCt3EG8XWAuo'
        b'VHSxTOz80tnJf/7QkYeo/2/lyqfnLh7MOYdeW6zRFTMXNotfU0efwlxm0acwj9NYwC+skWPzDTAprL5iXPISmIRdXuG2QWHm4oO+Le4tcWZhI6exoMmFAGU0Lb/vG231'
        b'jb7rG/MgLKoxzSRoyrWFk4Lftjybt58psmnOfW+Z1VvWorvrLX8QNNgc1zzXXGwuMVViIPem8U+h+3hAGHRgaPNQc8KekY1pNv8g0/zmiMaxtoDgA8nNyebSPaNb4lri'
        b'uwJkjWkfDQozcW2iMHOJeb7ZgSniPuligMictnukTZ5kSjMH3RHG2gIHm8t2z7bFDsEVAXeE0bagELN+d5WF2+F1ztkWKm7JP5RjUXboz1XZhCKzX3PefWG8VRhvGXJP'
        b'OGwAOSYBI/vfEUoHKmRyXOG3O4+8q62B8QTVp1lxXxhjFcZYuPeEif2QD2VxlrCT855BE2xJLH732a3A7wdmN8/eW/ggKgbXeO/O7nMBgSEHFM2KPkBFpVK2sRmP2FRU'
        b'JvUYUIFZ1IPQiJawg9mWMGvoUFO6LTjEnLl7hU0Uap5+0NXC6hbJLQaraMRdkfwBU3dflGgVJVoM90Qj+zIpMDi8T4FjwsF4Aqc2OfWxuP4ejbw+JxAS0ehK8743Dws+'
        b'UnrGpdXFouuOHG71CmtMN8nN3B5f/2ZDi7clvDWYsM4xTW12Mk+xCiS2qJhm116/SJtASNcVdguGdHhZBSPvCob0OYNAKWYI65BD0+iu8GSrZ/IDaUqnV6fqVrBVOhHP'
        b'u0+Twuzb7SUmqiJuKuyKHNXtPQrPuJnXPOJ+gMQaIGkZ92GA3BaT3ll2e9itamvM1P7Bp3YLpI+mEX197kjQvtfped1+3aHgy9ZDAu6i5w1HS06YX2cpYwn4MECfPH8/'
        b'lkVR/niO/vMTw+28UHCEH8MWU/SSzUPHUFN2pjQTh+MWHGLh6GDP8lEv7MCcB7Y/C/Bjh3P/Dozc5oFX7/PKnZ/uyDj/nfd431ZhMhxFz/1NIBLSiYpfvP2lr5QX1ShF'
        b'OfnDEmJF1Vq6EC97AfWFl0y9SKvUG7Qa0pdapdOTLkqKNZWi4tLSaoNGL9Lpi/XKKqVGrxPVVqhKK0TFWiXGqdEqdbhSWfZCd8U6kUFnKFaLylT0vBVrVUqdTJSq1lWL'
        b'itVq0eT0CamicpVSXaaj+1EuxJNcinshMOoXuqKvLRio0mrNAqUWQ5FLb4NGVVpdpsR0aVWaubp/w1vqMyoWiSowaeS2vbxara6uxZikA0MpZl2Z/NtdRGMZlim1hVpl'
        b'uVKr1JQqk/vHFUWmGsox7XN1uv62xeKXMF/FwfNRVJRbrVEWFYkixygXG+b+JjKZAsLms/HG4Bq1UqVfXFyhfhm6f66eAWdXa/TVGkNVlVL7MiyuLVFqn+dDRwh5PXBJ'
        b'sboYc1BYXaPUJNPixAia8mIseF2xuqz6Rfh+YqoYWtKUpaoqrAqYUyKo14GWGrREQoueUTMNHanQGjSvhSY3UMn0E/dpKK3AYDr8Zqj6LapL1dU65QDZ6Zqy/wdILqmu'
        b'rlSW9dP8gr5MxfagV2poHkRzlSW4N/3/3bxoqvX/BVYWVGvnYv+irfy/lBudoaqwVKssU+l1r+NlMrEb0XiDXldaoVWVY7ZEMYzXFVVr1Iv+t/LU7wRUGtpKiaMQ9bOm'
        b'1LyOLfry7t9wNUapLtbpafT/N5h6PmJIfrqcPb8WPfV3NdU6/csd9GuGUleqVdUQlN/y3GSulaqS36CYrFz64gHlmoZXLjyUWv0bGtY/6DN1fHGs31bN/1juWiVeRbHR'
        b'JYuwl8GQk9C10soSZoDXwRNfhJkvrFQ+N1UDBGERqNE1nU6p/neoerzA/4YQ+/shEK8n9pUVN9ugKVNqXr9i9g+L18jXrNUvDoxh/l0fcxe8uO6OJ7ONjpTrddhTleMg'
        b'hjS/DrFGiycA+7zi1487ob9ZqYnO1cp+i/oXxn6F7tev//2K8FIM8ALyb8YDDK4KD/16xMwxqbm/rXaF1VrVXJWGqNSrPiSvv62EVkhswKJxWmVVWe1v2vrzPf8XFJoB'
        b'/w+dSUUxXm1e6/LGK0vQNWzWr/EJ/xsII2ZA2xnxcy/QlY9b/r2xaYqrlM+8XX9cLIrMxdWv1VODtoaOi17BmKrU1io1ZcQsF9cqSytfh61T1hQnPx9Y4w6ei+pfgzFT'
        b'o5mdLJqiqdRU12qeRd1lz+8DisvKcEWtSl9BgnSVlkSpSq2qVKQq+3cRfjLeKBZXEbeJacqveCkX9kXE5P59TjLeF7xuZXgR+oUrMBfw8hVYDpPFl2fHIrlDBRz7Iul5'
        b'hZS5QXKYyCHpkG7bsoucJtfkAPrShV0yH7az0C5ygzMcDPcR06Au3nTiZUqEqEidGjAFMIfSl1Fb4kBqXhjaXloCdxkGk9fNyAQ3SMRZaJNkAWzKVciY8y4JDwwK5vqj'
        b'K5liJwPZQKOTQ+ElVB+DNkmzMqPhxpisnOzoLNSQncsFcaiBJ8lcQqe15sbpJVlotf2zVg+4nw0taA1cQ1+EzFKjxufvfoLgOuBSw05aJjbQZ3rH4EHYka3Iq+i/6Om/'
        b'5kEHs+n+4WV0mofqJaghJyuaBezRZRa8htbBjehimWEQBohEHTLSfybaNMcnOxc2oC0xGaiBDYI9OMiETuTQfKN2H3k/FIHJQ5vRhphcV3SSC0Il3BGobSGdzzthuO4p'
        b'1ApvAkfOIrfk5lBADK9x4W7YwaZHDV6Ozj7XHwaqj8nMCZpJgdAibko4vMqMeg5unSSRoQbckywrB22QTobXxDwQgPZw4GG0Gl5ibkGPwob8frDMHLRRikF8vTlwE1oZ'
        b'C1fDCzSQcjY8xcwb3LDg5XmDzU70vE+VoovyeHKLtgvAa7CuDB2NMgTRlyV4vDpJVjqsf3mm4LHpzI336RHolDyeS9+awX36Cg1cT+td4RC0HW2zK8kEIBbETodHDYH0'
        b'YSy8CU88P7OoLZye2SGwgb6xkJQHZysmzXxxXic4iFn0uYlHDayTw3M1PEwrOkEp8PhofSp9gScT6uTkaoRcOZajHZUqdI0Zsg5ughdeVIYRsB3rwkl0TMxjNP/YHE+5'
        b'vIYN4jlUNrlm64D76YZSdF0glyMLF/BCqEkAnneBrcw90pGlaINcrmXj/iuoPADPYMau0Rz4w51wNUY6xwWwGR6lpgJ4Ee0Oo69JkLkK7ZXLyXXhIZARUVnKJL2gq8no'
        b'plxOpHgYwIMctQxeY9KehT5ACkDGVzFFwsCJuYC5nrmMrqCjOgrPciMA6SAd6+VOGhw5uAM87bGb5hc5fUnFATGbvoWJSCogV4UNjETtkYmVg1rhDk4c3TqCj81GFh1F'
        b'5hee5iSXANepbDW6MYW5d7oAt04mJ1VcwIGHvDgUPICOlPTfpQZGoP203Jx9aLl55DI4p+H1fEZscM8YWm6T0D5auQPDYX2/CYyCl16xvAVof/9MR8JDSxj5nkVnGAGv'
        b'h4eY7hu8khn5ojWomZavGu1mbGcl6pj1qsmizeMYk+VSTLrxlhlw38A0oF2RldJQQySpb4J1E5+ik4vIV40ZM7ed6WQHapo/MGlT4QF1iD9t5fNna141cm+4h7Fyd7SS'
        b'uX3bhtYJ5XLm7hya4ckK2FRLuxOsl4fhtezM6FwZtupI2mTbysjtQgCs48CjeNw9tKLp4A4VuQMWR2dygIMdK38qdtRH5LQmfJ/lStK83Y6NLFJMjqliHDy86o3M/XMp'
        b'DyJTOcaV9qfzNMqXFGQRugZ3wH3oOnMvfR6Z4SpJVnR2dFQu2kTBs2HAdS5bKfSksxFY8CrqyGYE1Z+JgCWGOibCNg4IUHDg1lnIREOiffBiwlPIZejsy2kL5MaalsIc'
        b'7OGPMI4Cbo7JioVbnrmgqFIuPJkGjcwl8Zbx2dkxz+Vu5MCji7KLDeSGBu12VEoi0XXU8nKeA9oEt42kk2wcsUQ3MVfubMAeNou+cRdhfZIyC40RtWLZxMB6RjxwA1ZY'
        b'tFFBbptwPQXi4S5eJl5fzbSk4FYVH9MCD+VlSLPyonmAn81C+7FvqKNtzQ/tDJdk5iwaSA1g8gL80RpsqfR10+EkuJ7JNyD2ttOO5BsEDWEmYXcWWo+5uYnqmKQTJuME'
        b'nVtG8wovDfEmSTEvJ8QIkDkiHR5jUoVvujjwWcWoHoDJYDJqRXuwtdG6fAavj1d0FFonoT1KOLxCI6jYSXwtD7e3ArTKE+70jGKU9+RgdAhto/Bis5VOUMYybKf1TkA5'
        b'kO80CspLiqQzPGYxDguZhAQc7bLDJGwBi0YWpqLLtCmPhEf9YXssG9e3AHQAmqrheWgyTMFNFQkrdHhaUEPmxAnwXOzkSchIf4ghi47EzEf150BMJvZhlMahK1MzCOt0'
        b'1sXEDClpxIaTPWUCauBgvpe4wwZ4tpLOeYiJouMk0Y68Iul1lT2g17okdDP0deKbXRxRBHdhMdEGdEU4GLYn4OVn1DxqInZ4i+AmZt5a8FpZT5oosnxsID7vdEC1gQRT'
        b'471q0TZozERNaCfaDo0L8KMBboRtifA0F54rmaQvgReGUNjY2vC886Y7x9FCC0mAW/s7PJJC9ydHp8T9uZs3WKrsgRUyVMYrZEXBw+NoUy6BJ+HR59x5gS/tzuE62Ea3'
        b'RyyAJ1+y9WB0Be5A7cNpFsOrQxgOB42gOcSIHbR+acbhKOL5qGQIeBaUtJXTQkTrZ8Izr8Yks9GmWBFqE3MYbTgyfLQ8cT4boDZ0ncrCjME6MWPKa/Cy1CFP4NGhCDoK'
        b'9yiRGZ2lNTQJnomVJyyggIBPpQDYuhC7JloUHct9MMHIgnFO8clicK4S7RJT9FAUbB+DG+MAqEXrqHE4NIAnhhjGELSjlaV81IDq8YTjeHXLZGRxhmcT4iZkDOjcpOip'
        b'k17WI28/7I0OOKLd6LITbR+TinBEc5KHzsK1ACwFS5cH0D4FXVkIz8GTifAsC6BmdJjlQ/Ktsc4TTrJQGw4JT3LRSWcAloPlyBxniCVIe7B+HNBh294YMymS3CsTVzrt'
        b'RQLgjmnRdtgzX0E3DSOI4m1Cm0fy58JduTmoIXpqv42gDdMysqZk5DNMwdYJyJgTLctV5OEF+TiyOMJ12Bo7sFKTSC0lbD7axp2FVtJfD8CrRbQepPnIsNa2cUkGGRiu'
        b'hCeF6CpGCKC5g7tqn1MxvDSfp5VMak9H3246aHxJxfCCsBNT3a5nUufa4OZxJEHnojNJPNmEnf4lKgEeC6VntASrgUmHLta48kg+0FBsTeH2+XT2nCpv3z227s/YXQQ3'
        b'XDg69X3d5KFuux6XjR69otEWnpj4I3Q4IF4H1rFU4oQu2FCcFMu2Wx/IOvZnpItYOOLOwevNj27JA4+NXOv5eLvntF+lv7KmVmYu+PPfulYtPJc345fzhb2zPzc8rP7w'
        b'ZMKwPT98dOFP03ZEH/OLff9RIbifeubcO7yvrQFvnfc6VZvxzh9vzY5Le9vvL++JL1eGzWstk5tkgffZbrPljtvV3/yqeuN4+CO3pA1s9xVpCtNa6vMvFxqTDVnHDS13'
        b'GhfPZ0UPP7xwxJYP35e4fL777K2svyjOlieI8x7Fpdmrv770pujjdypHubXVtkSMXTzG+9D6ijXqql/W/Cx9tGVs7rqPpPunFR/6dtjxrw7GXhl0MzUx5VbWvG2zhv7L'
        b'+a9BtgW95dLv47Rzm5b4/jJiU6LvqnsNX338Az+stK7eTfu7CafkaR/Ol5pnfe++as1wKl3zQWVLgfPcppnffjx25xKvyxfi/vn3nYVjfy1Gb0+WdL97bfY7f36X1db3'
        b'w686Xn3nr59YytoeWkac4/04vuJCqn7dZ1HWw2khh942BkUsXl2xv2LVZ5mHjhtPu//yVld0+fKaxRE/7Pq707w5iU3zPg3//dtK9axvTW8kZm386tyGklrpgXzeZkHM'
        b'wZbDU33mZl+Y/49zm2M93PfdvhTO6jg3Zm5gc9PD2oXSJHbPw6pvAj8c/+GXk3qS18g/UpTKWr/8m7rqeP4Cde2HZWvG/c4QNPfH3//jgySvvUfbq1qu7fju5ndvXyv8'
        b'KGTV9wHv9PxzPpwWu9yQWrf9He6ObxbtWcVL/93ezsV/eG/aV0v/8MN9qSKrTnfjImtryr1W1wefmdriv7DfMFsk/4LV9r3pwt/e2TYkLHZFzMPIOp+dD1c7Xvl8osvP'
        b'7+xT/LD5szdbv0ZxP64w/5xdMDtvSf37zZzRN8afb1izP/X6lCHd0vAHa7d9rov3+9u/EtKH+bX/Q3nk4dcL7VZJLmbPOmo80npjqGLETH7Cr6vempL2s3HUo6kO4+9X'
        b'5JtNvxy5E7Uw6rs3otveFH12RvLHG/K/yjr+0fUoavC7DsYAF6ssN/XnL5WCqt9vH/72+9f/lvHxntLvMjvWjUq48Th8/lDxvGV//+7S8c9+rXYpXuGB9vutMHn4rah7'
        b'g5323ld14FGJ53zH+fd+qXl/BvxiWN+3HU9mH5trbefGTjzVOv3MzH/0Dr0VvmTtkCP17pPbT2Qs87iJZGNH1V35S9Qf/qjK/+ucOzHDWToL5+ZPwvc6xdtqf9gaeasK'
        b'vTntzUWfnHF/cu6N+9lP4j7wFX8n7ih9665d30fugakLbssWbI245Zk6dOeXtXE/od4zIs3ikb+zTv/z6fvvREh6pl0fZxt5ES4/c/XCFJ9dHRt+P2nrxaYPd53yHFEU'
        b's+j8tw4XU2u+37NW7PKYbGHtkgDJ3mGSbIgnxEGVL7zIYaM1GThe3/uYxEZ4VUaNkiiZGK85ADhMJxHpcRyU7HWik4hGoy3pEtlLGUTwBLwyJzTjMfE5kjHQ1D8KBZKG'
        b'0BlC+ePo/KA4tEWYLX0uNwg2I+MiuGVkf/4SbAhF9VK4Rt6fwjSQwGQ/5jHZfo6bXCDJCJv0SpbQHrgf1T2mF4tmdHaYJDdHmoU2AzzCZRbcoKstcqIb2fAivJGNA86Y'
        b'aLJZwbFmLUuG1tnRXKNGg382pmuAK7huPnCNZc8tjqZzl9ARdGX40zAhZi4JEzzheZrhKZPgDkm/uNBNDx48xZLnB9AU4337UbRakgVPub/02VcT2vqYPhe4TKlRO54K'
        b'HGzV0OsVC3iP4MCbqI2dPV0s+l/ObvoffuiIXr16dMqkgwz8vfAdW5V+WELs4udf6AyqX3nMd2waHvAS7BrdNLrbM9SYZvP2NY6zeQmM6Ta/QGOWzcfXOP5jgbCR0+MZ'
        b'aCozp9/1jOoJiGjhdAdEN6bZfAN2LWlasm1ZI8fmP8ic2ixptOvxDbB5CW2evqRLs/yeZ4QtPOr4vIPzLJ6W4u7wpKa8xtRGg0n5wFdo5mxd1hMg6hHKWgyWOdaYtLvC'
        b'dJtw8IGc5pyWsLvC2AcxCTZxtC1SaouQ4E5s0lhbdJxNFk+ekhhblMwmlT3ycx7kv5vbJwT+webQ3YG26HgT11TZLYiy+QXRFQFB5rDmEbYx49+W3JLcLu0eM8kqHG1K'
        b'N0dZhdF43OndMaPxQLhC3C2UEqRoqx/uPAZ3U7HHFVd0Dc6y+mU9DI+zhHWwOtiWqA5lZ+rlitshl6u7w3NtkdEtxRZWC78nlLAx0TK/ZXF3aPIjO84gfxO3zxEIB5lz'
        b'rQHxtoRheAxZtzCOpFRprIEJtiHJuCamWxg/kGSVONyU3jU4vlsop2v2zH4OhHCzJ7CP5SPytwnFLQl9bFx6IAzFgvW2zO9wt/h3h4/o4+LKPh4IDDGn9dmRsj0IDDOX'
        b'9TmQsiMIxDPXxydlFxAYhTtxJWU3EChpSetzJ2UPEBjZ4tXnScpeIDC6pazPm5R9mH58SVnAwPiRsj/TZwApC0FguFnfF0jKQQwNwaQsAoGyFn3fIFIezMCEkHIoUw4j'
        b'5XAQFmGLENuipF9L8LuJ0ycjknNvTmKSqu4GRPdIhliUHakdxZZ5nUNuu9+O7xxuTcztluSRzLRmhS00vDn9gSTGYt86aqAmzJRuk+J5a1V0jLVKR5s4phlWQSSdTteS'
        b'ZY0YeidiZEfqnYgxne7WoLEmNpbcoHCzsmVslyjWkt0lGm3i2oJDzZObF98PjrMGx90Nlj8YHNZCHYwwjSUJfKXmMjMfwwQFm9ik07HN8+4HxVqDYu8GxWNSx56d1zn2'
        b'TuJ42wBOHxvg7p5C3XsG1Z04/kFk9Bl+K9+S3hFyNquT6o4c0+xs4pm5PeIEy9SOKd3isZj8gmYXm0xuSbUUt8zDr7OtAsmDxOFYKGMsqvuJmdbEzNuh3Yl5j9iUX4LJ'
        b'y1Rp9YtqGWsTiroGxVmxEgkCTRqrIPq+IMEqSLDk3xMkP7WSsBavO1jGg+P7AJWQSdmyJ+FOEiZT3wAqJJ/ClYH51IN+/JYSqyDOIrUKRt8XjLMKxnUa7glySE8yq1/s'
        b'A2HQgczmzK7wlM6wbmGGiXoYFtnifsa31dfiftL/cKEtUnzGrtXOQp107ME2NehSxNmIjkHtxKoMlzXd4TkvmE767lEkMTLdHH0HO4T4obgkvSOMoc1ypNVv5AOBkAwc'
        b'iRnFxYdBMkxpbLJt5JjO8V0jFJiF2BzCQnAuYcEvl3owKHxr1kO/IOK6VjStMOvu+kosXpcCzwZ2GO7Gpd/2+n3gO4Fd02bczZz5UCDq8Q3sCZJ1xYy77WuNmdAdNLFL'
        b'MLHHP6pLouj2z+nyyiFJgDOt3pE9XuFmQ8sca8SIu14jbV7MZ8Fhd70isegb022DwrZmPQgQmYPuBMS+0h9J/wyyBsRaPKwBCcSnDjLn3/EVkyTS0c2jW+R3A2IsaZey'
        b'zmZ16NrzOovvJIy3hUYezzqY1aI7nHc/dLg1dHhHWmdId+i4+6EKa6ji9uTu0Imm9J6wqJa41lKSydkx6MOwEWaqj8MZpKBs8UM7qLORHemdgzqLb4VdVrSEYTt1BHGJ'
        b'luIOyuLYIxvWEdZJdbI6xN2ytEdctniwmYvdSGhkS+KhUbZRY81pXeLkO6HDbWHilqmH52CnZU5r8TuU93UgCB+JbR0DOt8JSbQlJpk55tlWkZzkaQZ2C2MsCVbh0Htk'
        b'7rD53fGTkATMWVZB1H1BHFGn0A8FQx++LJy+iVzgF/gonwvcvHvcBpuHtARZQ5Luug2zufnscm5yNinvuoU+8PQz5vzwOA5Exn8NWJjHnqih1qQMW+TozghrZOY3bGpY'
        b'NlECiYIoQRh+sgnUTzonvA5auc6TAzndgQGTk+yYlEy3Xg65G/svpGL+l9dsku9Z9Lo1WpsInn3gTa/NWwn8KMDkbBZzKMrje4AfJHHT4z9N3NzLk4JT/KHsF+7lBvI0'
        b'vyH87QJK8is+YAarjJrBXsRyWCtm97rRF4J0sqQ2Xaut1v4UzFwR0mRq+3MflWWiYo1ISdpluWJOr31hIblTLSzsdSwsZH6AB5edCgvnG4rV/S12hYVl1aWFhbSgmSxY'
        b'WgokR3XxK8NuwaTqyMd8a8EnTnE0OHPI3AAPjuO7oEt6vkOGNCo3WptS3h/JxaADPC5sRQfE1DjVqY/mcHTzcCebtqiVTePzUIrX2to/lBz/nrXWZ3HMwe8nsEav+tdt'
        b'1nx2dkqo7PbW+58a3XbNGrYu+J32DWz74FH//Md7S64O/9dOQ0fIsHOHk04cvt7ui4o8dN2n//hQ+kNndaLgauXSM2NOdM3I28Zuy50hvmv+ecEPjndrfDpOTq19y3Zz'
        b'+YzssHEzfi2oftTp/vgbSXXpTuFUaF+5/7L173/+fHDUncGV7xp7rhx/MCYt7e52t0vOedfLM0Q/vts0Zrcpdadp7P6ClKaCMc0FqcFng9lvRPE2jBWEby7aXoAE84We'
        b'b2Qq3I/Hjd37pnB+EP+NdGmxn6QgPbCy4G1e3AeJZ9dVfVnku8RWfXxUR8RDUJc0hv121Zvb1oWWJS+ZVKbwjtAveP/9iQviLn32Vs7n3yRca3vwl431nGGT9ZPTW8Z4'
        b'LproppSvks/8p/4bhyd57/2zu6yi1+lvO30+vd/05KcRv96et+lf/5xy8e6cd601fzpwPvgv2Qt+33Ay5h+11QvDvhdzHpMDGNclNaheQQEPtJVKAmgzrEe7HpP7BXQa'
        b'nkXbn/3QCJkztAvW0T80AhvwjohcxUrYeJ9yCa3mR+Hon2w8nsIGw3YOOjMZ7aM/YjAkCnWwLSM3mrlo2JIIT7GBO2okd3yH0HmxH2OC9v/28T8XqZMdmCiF/lv5yh8T'
        b'omOjUVcXlxUWLn5aooPzn7HW/oqDcylw9u7j2Dn49rh6NMbX15oGbVzarDPHm4sPDtmzuGXi7hVnQy3ajkFnDR0Tzy5sl91Ku+2BMu7EKz4W+JviTcXNQ/Y4mLOsApnF'
        b'1ypI6hqRa/XN7ZqU3zVlqnXStDu+0z72EZk9tmm63EJxbCIooPBC4OHVmNrkbRzzHYfnEPmdG8dhcJ+TvcjR5uTa6NPHJiU/oamcKYWLWxKZkjyxg8eUUsZ2TqVLD2gM'
        b'LinRGHSJxqBLNAZdojFICcdfzm4Yx44p+wdirP5yRBTG6y8nDMWY/eVUKo3C2PSbPYPtwJRp7P6yNL6D1znV5u5rKm9JfF3xa1cM2GUvxLGthwDXMP9/xOcNxrVB37sp'
        b'KIdpePFg/pnDAo5uPQ5ujTrTkMbKuw6Dv2ctZDv4fw/I8xs2cAwhD7c+DnnvW2CHy49ZlEP83kV4EXKIpxsfkYof+pR8yiGT6vEIPuLUFT2uWzS+2yOjyymDWZo2pgrS'
        b'eOANnmeaH5tZmrx6Wdh5/vctTK9VW6/XLFbPFizyTcEzZSXbcd3I/tVKTFFuZLFy+5Y8/tPF6iAvDpzlj2CrPnNbSemW4povvCOUDSMd16QI0m6OHtLbnJ/ZtTDijCXD'
        b'rfuoIrn47a/W1PVtHZydUrN76Juln05b8t0n9z5SbA50fnzU9dusumsOW776k89mp2TVgcCciOHTBi+aef/WnMyizXmq2FiOw6S/RE74ZBPfa9rHNXUHITtnWnJAXmq4'
        b'Srzi9B8vBBzgPRHb0ecJ8NpMNv1rZ3nMndnxSDvAh+dYqCUc7qGPeOBKeAQdz86DrfB0NDpLQPOiWdgLXWPDg6hDTgNpUNscdBjuhfXkdpHckGFft8UOuHiwg7BvXMV8'
        b'brVTlJ+dmUO+1NLBDvKxFlw7k/4MLGCiOPvZL6kdQq0U4ItZqBE1KB8zF3d+8Nqz31pbmtH/S2tZZY+JmrDxwK0BaL0kiwuobIBM06LEIb/tGv+PH3G8VitDBpzpq670'
        b'tW5VpVHpGbfKlGi3Oh4/fl4JvvEHXE+bs9d95yCrc9Dehd3OkSvH2TiOdYpVii73QUeS7nKkf+AEf8Rx/p63hMuN/x6Q52P62beYD5y8VuY99w2PqJetVmp6OeQjkl6u'
        b'3lCjVvZySLYUDiRVpfhJPgToZev02l5uySK9UtfLIbmkvWyVRt/LpX/Wp5erLdbMxdgqTY1B38surdD2squ1Zb28cpVar8QvVcU1vezFqppebrGuVKXqZVcoF2IQ3L2j'
        b'SqfS6PQke7yXV2MoUatKe+2KS0uVNXpdrxM9YDyTrdbrzASaKl11UmJsXC9fV6Eq1xfSMVyvs0FTWlGswnFdoXJhaa9DYaEOx3k1OGrjGTQGnbLsmd+hz6CK/u2fSMS4'
        b'C8XAg3zDr8vDjydPnvyCnYUrRWnZxFu8+HxEP/8T30E85S0HXqofuOXHTw1l/2Q/8ENjvW6Fhf3lfnf1k3/5iz8YKdJU60WkTVmWK7bXkribBKnFajX2szTtw0mVIxav'
        b'Vq8jqXa9PHV1abEaS3aSQaNXVSnpUFWrHtCGZ1Ftr/0IJgwepdUCJu7WZeJHH5uiqEcsDsXpcwJ855V2X3OyeJRX3wwn4OB+3z7Aah9gyrprH9ElHXUrHEVapVk2e7ce'
        b'R58uX3m3Y0IXJ6EHuDUK7gF/eqj/DySrAGM='
    ))))
