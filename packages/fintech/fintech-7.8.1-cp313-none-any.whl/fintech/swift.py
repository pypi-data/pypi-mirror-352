
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
        b'eJzFfAdYlMe68HzbKEvvnQVpC+xSFguoCErvCKixACsssIK7sMVesGNBwRIXUVn7Yl1BBY0FZ1JMZ0MSVk6KyUlycm4aJp6Yk5yT/DPfByrqvc85/3/vf3mScXbmfae8'
        b'fWbe3T+DJ/7YI//+tAwX+0ARUIEooKKKKC+gYs1nz7QCz/wVscZTTC1spEXKx63s+dxAMH6kZTL+vxLjzmDN5wWCIs4ohoyabxEI5j8aQQCquVYbhbxfZdZFszPTigWL'
        b'lZXaOplAWSXQ1MgEBcs1NUqFIE2u0MgqagT10opaabVMbG1dXCNXj8JWyqrkCplaUKVVVGjkSoVaoFFiUJVaJhgZU6ZWYzS12LrC94l9+OH/+WTr7+GiFJRSpaxSdimn'
        b'lFvKK7UotSy1KrUu5ZfalNqW2pXalzqUOpY6lTqXupS6lrqVupd6lHqWepV6l/qU+u4DJT4l7iVOJZYlFiUeJbYlnBL7EusS5xKbEqsS1xJQwi5xKHEp4ZbYlXiWuJXw'
        b'S7xKeCWsEqrEu8S3xDHOjxB7kaXCr9jnMQEV/n6gxO/x5xL/x3UBSPZL9g8CAc9prQJT2f6girKqErLyKp5kmyP+35lsl0NzuhoILfLqLHF9hpINVrkRRpfbNEVZAe04'
        b'AomaGtB2tDV/BdqSU4iaUHO+EDVnlhSIeCA0lYNuORcKKa03mRc1V6ozc9FOtCMX7aAA3BtjncmCRku0qYJ6Yn6n0fnX4yLRsRSvARMGYGJxMTksMPGsMNH4mGi2mFD2'
        b'mGSOmKTOcU4j5KGKn5AvBQuTh3qCPKwxhKCSWTR5nmn9d8iTw5BnY5oFsKnk4RHK64YnrAZ0463lbMCpTMb7K8/5On8+0+haawUc6nQWoLw854bVZKbx72s4wLImkQ2S'
        b'ym28a8tAJ6izxs0BiR6JIuuvgwH4LPRH1pWYORn+VB3hgXB1G2W0cMiwSyqP/Sj2kzIVoJt/mPeT/V77iw7WBfeo3+c8WNYGhoBWjDvgdtSN9mNWbY8qDAtD26IyRGgb'
        b'7CwOy0KdDrloV6Q4U5SVSwGFvdXUEOUYjnBGt1xJOMKmOUK4AeLYj2jO/p+kucUzNOczNN+cYg98APCIrkqra3dczuw0HLZSeJ87IrLRDtQMD6GtOYUZmZGZJSA2u8gV'
        b'7i2G2yEehGuBOlag/VpXQpzzgfC4BPbg8WEnmIZONlSiU1oyJdQLkEECL5GeQ8DZtVadQ2MUwb3oqCSWQLwI4FW0t4KFxyKy6whb0IvLUS/awwVADMSTA+ml9lhYAxcA'
        b'LKPddscmeUYwTF+20BkE4X+jE//Q7JudC+QXmqaz1WtxS0eiVXfF4TccoOFlB1j3xh3Au71j1pc2NltX2diYChz1HkWW3WJvNjsnN7zCUh3dXcJnbxAd4xXnBjqzN7Bm'
        b'RPOnB3ED4YHXHKzjytzDdr/p85bby281Uo0nYzjd3Y01P5enBZ+NftvjrdtQb7+0RKy2dO6KKPGYNA9srnIcJ35ZyHpATOCy0gA+pqIwVysKxyLDAq5wCwddht2W8GTB'
        b'Ax+acugSOoPJvQ3tQjvYcAvsApx4Cl5EXSuFnCFWmFBli8EeF2rCQ0FjY+OQ25QqlXKFTCGoYsy2WL1UXqVJHLKmbXJZpVQjU9ljYBbBqsfFL43gfgoFHJxbxm9foSvc'
        b'vvYjN0F/QEJviSlg+oDbjH6HGWY3b11la92gW4ReM+gmMWia0s0u3jpZa35TqtnFfX9Ga4ZOpp+uL9TJDa6GBqOjwctY0hvTW2ic2++bNOCS3JR611mgdx1wDu23Cf2J'
        b'yJ6KCJ+QN8RdIq3TyoYsyspUWkVZ2RC/rKyiTiZVaOtxy1Nb5BEbKSCbVNmRRvvRglhMdRzR9kbwcAZFUc6f2blvr23kD7O4lMtdvtP2+M849htzzZb2dy2df7nPBVyH'
        b'0U+/qonE7OGNA8f4YnYF63kKWkUUlEV8FK2i1BMqyhpjFtl+YxSwhD1GGVnJbFpFn2n9z1X00RIeqSgvj1GgDrQP3kR7qGx4HAAREC1P1hIbKpKg42gP2xqdBziSiEpK'
        b'0TrgVhtlMdabPHiWVh3Hennt7Q6WmkQJb918gVEIl5fvNFLrPTe05bQJvp1/0iHN1rAsMKJgZ/zGTPdA3W/v6DnvK60/uAD72uyAVRGv5fJmIfXAC48wLRIejsgSoabM'
        b'nDwuCFnEhxdZ6BDai64I2U9zkIQ7o+wb4jMCWVWnlGpU7qMSGclI5HAxBVy99ue25urH6dUDLhFNqZ/Yu5g9sNS18Vu4d529dOP3JPbbBKgcHkuTilBgiFspWyjXqIjR'
        b'UDk/R4JoEWIkyH20iBiVoF+xBBVhCfL6dyVoLy8IHOdHsWkDlJfoTMWx5lhzC/oWm6uP5mndCMsMU2C7WjMhOsCNA1gLATqJzehxGj5/kSs1iWWptovuW6zzX72StoXl'
        b'aJOWgPuhExRgyQDqnAmv0eDvrXanprCaGqzqMXj0/VlasgV4DW2AGwkCOgFb2YBVDdAZVTSNEOLqQSWxWkoo0Lfa7J45RYtNJtBmwYtqzcToSLgHr0cB0OnMShp6fKI3'
        b'lcIyWFsk9a3WOYjDaOiwinAC7D6OBVhKPDLcCQ009B2xL5XBMmfbCTC0wjFF64Ebs+FGeEONLo2Phm0Arx5uAKgbdtfQGFNS/KgcVk0DrxyvRpPnS1PHBm2woxHk9lwM'
        b'vxGgS/B4PA3/dXAAVcCKtmA79K32WPY3C3o9angMnlKrxkc7xVL0is7OnUFDx7oEUsUsXCvA6wnNddJ64kbUgnr4qFsbE412wvN4u9hVoe45qIlGWTw/iJrDcgikovGC'
        b'Cl7h0yhwLzyyiEaBG5zxprFDwjZ5EzxIozhMCaHms8rd7OoxCnd6Js2CRWgP7FGrJdFwC7qMJ1kL0HnYVUQjaKcIqXJWDVb8PrWO83YuvWl0YRpcR8/hmY05Bg8A1Ju5'
        b'loY/RkVQlayCGgBuq83OftMZEepFBikNbyu0wPDtAF0NXUjDL/IRUTUsSyVmmlr3wmAC44Cvj5+GutU21jHwMN4CukzFjc+hwbeqxVQdy2DBSsLD847VMss5j5qm81VY'
        b'gvZzCY1OAtSzxpeGz06PoepZDlMsBH1qj7UbM2kuw+sCQtaLmMu30CGMgQNQdjg8QmMowmIpDcuSzxbcVusCUhfQXMMS3zqebx0bPdEecw29SFlNrmB2tgndgC/x0ZWY'
        b'6OVLyUibKKo6iuHdGdiF1qtR91I71AsPkX0coSLmoWs0ouYFidrKFhnR3lwy4i1qAlyPOuiuSm04v0GLrsBrcC+2LugiFQyPLaEJswjthpfUfJUGHgglaDrKTxFP8xBd'
        b'wWp0Rq3BG/OHe0hfMxURZkUPmI7WF6rtbK3hSXSFBdhcaipsRwbaHnMF8bjHjo3WUYBtRSXBm4ySwZfQngW4p6HBg+yqlxI7FNAdmegYOsi3rYc7xP4cwB5HJany6ZEK'
        b'y9cQscbChvWgHqBzy9wY/d6KjnGwesehnQ48gMM61Il06BDTd921jMjdMtjLZZStC/XgUIswyXkJ3KxGF1G3vT3qIMQ7T8XBS7CJ3lGDNFSNd9xt7wB7Sd9pSoLOq4X2'
        b'NAfX5sZRy1gZSlY5Fqnoh8F043bRRGoV685yq/Lb6jmzDEvoxjDpJKqRZWYDhz71nLqhuXSjc3ACtZFlDrZxuK32iNmdy1gi9ylUE0vP4hfgMdd82UA3fqFNpHawmiqp'
        b'AjzmvOEUurEuKolqYWXYcqOxxJWESunGQ1OnU3tZ5nJONIa0f6eAbvxQnErpWJYBVD2e3b/IkzED6jTqIKvFnlePZ1/25zq6kbssk9KzCpy4oK92jpNiOd34mncOZWBN'
        b'WmWV1FfrUR8gpxtXpOdTZ1kZCtuk27VzimyY2Zs9CygjyyGNEvTVmmeVTaAbXw+eSV1i9a+yF9yu1eWCuYw46+FWbIz51nYANWKJsMESsW0OLXo4oOsu5qvsbIvRBixE'
        b'jtRUdMaHUadutAtewueJnqVqdCuaTYtzxFIHekQBOhKMdQCbSNi+mojlXiqwbJmQQ6/BTvkadZDtsMay/vZSjzl/UdKNhtTXKT3bPJ4D+pS6rPUU3VggfoM6zrb05IHb'
        b'yjlhK+sZqqa+RRnYdypYSX1Kj+hLOWOOKdzREASbIpDIHTk4cuhDI4jj/o8cD6ufjoN44Ok4KCRP64/r82B3AD54bMzKxyfgXWhrZq4YbcURtVs5JxReL2f8jR8Lu2ZS'
        b'K6+bFejEnBFc4i3B9fhAEg/Y/G6TDmg9SoenONlR2Whn/pJJmVxgiTaylsPefLrPFrZCHezGqoNPLdQLIGwxPIs6yhn9a3FaFhGGg/mmKBwD2VSzUVOtveV8JlK7ZIGO'
        b'w2688AQHCUhAl5FORcs3KQ5gZ7dxNQ5bksojX3SxZxqrbCyAwzxv+sibMz4OMIakB12FuyVecGM0+bQbSGdFa4NJdd0LUJ9NHxR2kVuAbLgrKhOeC6OAQMNFW+FhO3h5'
        b'JSOUN2ei0xLYBg/G0f4NLMSmroMmI3rRenYEPr7Slwj4LIvF8FwmBzgL2WhHOrrOoO9D59BNyQzUNnI+q8B2+Qy9xyCkt5BM5MAucp7rAHXw1ET60DYbrV8jsS6REPjD'
        b'oBpeHQleT0WESuCuGglmKzwCFmnhUaZ9PdwcI0lmTyB1Hah0h2e05DTkgV5C3dlZZGV56BoOdHbmY+7Y1bMnTVlNz5MMDVKJrdUEMn0bkKGNzrTnsIS9sCc7Jw/tjELN'
        b'ERTgz2Wl1aDzVsuFLBqtfCU6IUmtmYADT+x6q+DJOTSpnVAr2iiBhuAJZH3teN0nbWg2r4EGiM/6+OiWHJ7LBRw/Ch6dCfX02vOgIVESHTgBqw48CGqwY9hFr6ES3kA9'
        b'EYQhaGsePMcBNlPZFdX2ciaqGgcvhkoq4HF4hTYamHLdibQtCEMbpqLtOVmugfj4B9joJgXb4U70kjafpv0S+KI6JzMzl1wNMSdyfBoPEwvDc8VCEcsanpBhH3USHg8L'
        b'g51uEUJ8qj4e4QL3urmi4+7wFAvAbS4OmPn7oN4CttX98scff/RlcEGxiwORxLqvNJaAXgU+gt6EOyPyRPBAQwYHcJIoeBodg0eELozB6oCG2WpbFbqAGUXM1WFqHObO'
        b'aS05F+CVGdCLqNtOBc/By3T3FUqI1qEjIy5rIXba3Ri504buvElFzIIHaarMXxqutlPZY0jG0PnDXlvGdm51nqVu0MKLUG9NosqXKAHbggldeuCm1diVLa2ZSDtOHIkE'
        b'CKLoVZZY4qV0L8XB2xXYbUvRgUAsOjad2eHmMnicb8eHu1EL3IXt8VxqHrqI10vWkeuKdqo11rbTSUQCb1A+Ptjb03FVlxTuxT0rYNdSMtk6SuBSxoy3PlGJujUqdADL'
        b'7CUS092kvOHZeTSaFm2KU6MuDQ9QWB3gVUu0K7WUkfz2wEC+pa0o3xoA9kQqA+oV9LZca1EbjvcakA4etyFLP0CFpqrpwVRV4Xw7G7gFnrDCOJOpTByb3mCodH7BCuzS'
        b'VXlwvR3ekR01ETYzR5CoSngZ9+DooAvesMV9gVSycyq911SXQnVDQy5sJ9PAK5QfarSjl+bE8lBbqxSWNJN2UwJ4S0wjFObV861VeKAruIftREXDw4U0Ao4ndqCzaA9W'
        b'nkh4yg1ENghpjqfCziS43d66YckMdI0CHByIwGanUsa6XV1Vg3fjjLaNbuZYmbyw5Quu+j5WqDM+xuail/K+SXI49PHf2K+9HhxwXdk7hRuXEReXfDxJfzxm/vKumVkt'
        b'LfokR6fP7cN+ocITGzv0n1/4Wuf5mr1x+/E77xw+pP7qrWU9f7kJjZ9svun3MqgwNr7B3eaSTs3ZdOChwTRp1X98a9o5O62Ce+JTU+XHHWcnBlz8eG/8oqOv1ZYt+EQW'
        b'fvLs+t9bf+1Uf7z+o+bk+sqH2d1bJBfnzeoOLzl208XrrwXzXH9zvZrw9iuNZ6I3fHWMZ/u5R/a+i2mGGYW57zRro7/deedIeqndxXdKj5bMVBkL+/6wvBnxS93DcbeF'
        b'iiUvxZ249rLo9mSnd2PW3Agb+LkyL3nTvD3XPm6sCbu+5MhX19+/7rTqSGOU9ZqoX96LqdS+eOr0T4HXXU3HOm1q521Sz3zB9W8TX/91nmHI8R+H7ssVebBLpTyaf9r5'
        b'VWnbptoP4/VvffRpzV+SfH6atvrQ6w9iP7i66ugvP6R03Gk+WvcfX5imvNG87ebJjhVlqbmNLUdnfHVW4j/xVTE0Z48fiu4VRN3825/TUi3aO4ecN6y9sXFL0Y9nJT3Z'
        b'80V/KjxhurrqQkHINfEneyb+dceNprSaG99+Kf+P46GHgpaXfnjuj2N/+mPr2t9VqxIOtlqLds58a9N8i54vLv/VwI4PLX+n2XHVtHebqyN+/Vh847uNS19N2OfaE+q6'
        b'+PMHbuv/otxU35Dl6SK0ZG7BjniiG2h7ZB62bmhXJDbg8AwLGuzQ+RIxDYAuoGuzIlhR4szIcKEYg6Ct2FsIOKWJcB99OZE6G7aN3KLdnEYsKX2JBg1o7wP6aNHlizZE'
        b'iLF92BqJbjhTgAd3skTw9PQHtC7fgLq87MiwDNRcDVuyKexPzrCWl9s9oO1XK7yWn52ZG54Lj6NDFoDHYVly4K0HxJumoevY3mZEhpNht6IdcA/qQLvYwHkyG7XP83xA'
        b'fM9ULmzKzhdhZVtCrZ2cjLaIhLZPXZf8+4WaFIKRv8bGR1ctTsxVi0YlVailzCuNilya0Tcu51n0jcuDFBbwDG7hmN29dTkmdyGuuXjofPpdQswBwXrpEXeDoyFG79PC'
        b'aZnTakeAMlrXDLqLTO6iQfcok3vUveDwlhSdR2ueOSRc57kn3+zqqQtrLR10FZtcxQb1oKvE5Cq55xeoj2mr1kv1C3W1GNyxNX0EfJgHfPw6JrZN1Me1T21JMXv56Rra'
        b'QltmmL39OxLaEvQV7dMMMYbYfm9xS8pHAcE6rlkQrF+ob9BbMVU8Il31FuhT2qeaJZP0fgM+0WbfQH1l+wJz9Hi994CPyOw3Tq9pX2zk9rp025qDhIbiY7lGWa+me7HZ'
        b'R6D3bMsf9Ik1+cQax3/oEz+KGhWn9xrwiRz9KJboPdvzyae6Ad9YgubWljPoE2XyiTJyP/SZMAL3mTjGGHxmkS5lFJrgRkTr3dpz8KeOBW0LOsrayu6FR+ld27OH7YDv'
        b'uI6ctpxhQIUnU+YZGffZVHgm9QBQvlnUvaDQI9nGYFPQRF2q2X+cPrNjrVkQpH/hiL2RNSCQGLUmwZQPBJJ7TNugYIJJMMGoHRRMvZ9JgcCQ4RwcCQZits1qtRlmcb2c'
        b'WnjDNmBcaIs9veeD+ZjYYZEX7DrtjOqBsMkml+CWVD33E3evw1qD6xl/vGHdrDYbfYnJI8IcHnXA/lPPMJ2/2cOHbi0b8Bjf62LymPqBx/j7tsA3Em8FS41V67T+kIQB'
        b'54R7kUl9Ln3y2/6myELMbrfWHL37+y5CIhvC1rL+sMQPXRMxh/W8timD3hEm7whD2qC35H1viTkqta/yTvxtpSlqlo5DzzXrfY/IH2cTIX3izs9yyGaMVD/n1u9pHaEP'
        b'Ak+qB60KdDGD9MeDkYtkFkV53Qf/F3eB+3jB4AQ/mi2kaK8bDq8EZ2dGZsLzQTiGwr6/HccGe8ccsmxHzzfkHTjRduSQRV7mwLNvc3G2jw5dnP/eQ5c2E8cf1gXEWKgF'
        b'0rHvt/Sj8PJ6mSC3OD4uWqBU0ZVYsbV1pkagkmm0KgXBqZOrNQR0oVRRK5BWVCi1Co1ArZFqZItlCo1asLRGXlEjkKpkGKdeJVPjRlmltVQt0Kq10jpBpZxmpFQll6nF'
        b'guQ6tVIgrasTFKUWJAuq5LK6SjWNK1uGuV6BMQlMnTX9iMD0VCgVS2Qq3EOeobUKeYWyUobnV8kV1Wq81uTHMywX1OBpyTt3lbKuTrkUQxBAbQXeiizB2lqE91gpU5Wp'
        b'ZFUylUxRIUsYGUcQlqytwvNXq9UjfSuEGPpZOEyj8vI8pUJWXi4Imy5boa0eg0BIRJb3eNzpuKVOJteskNbUEYgR+j0GyFYqNEqFdvFimYr049pCmerJdanJJI8BFkrr'
        b'pHhFZcp6mSKB3joGUlRJMTHU0rpKpdCaeAo80WJmnhRZhXwxZgNeLdngaHeFVkV2tvzxTLPR8RqVVvEIgjwrJdAlxtVW1OAuNf6kXfzkKirqlGrZ6DJSFZX/C0tYqFTW'
        b'yipH1jCGP7OwDGlkCnpNgmrZQjyC5v/v2hRKzb+wtCVKVTXWJVXt/6fVqbWLyypUskq5Rv28tRURWROkazXqihqVvAovUxDFWAaBUlG3/L9tjSOKIFfQEkwURDCyVJli'
        b'dJn0w89/scrpsjqpWkOj/O8s8klXlfDIVD5p8x7pcL1SrSFIIxySqStU8noC9p9ZF0J/mXzhE6shVlEjHWXsbGwV8ZB1dU9w9xn2jx1zrCj8SzRSybD1xYKaIMCahntn'
        b'ousVtQuZgUZhiA7iDZTVyp4g5ehkeBt16LpaLat7GlyDjf5/svkRXALxeCHPWO1sraJSpnhsgUeGxzb3OTZ+7AQY5mm86iVjbXc64QA6XqVRYw2twk6LdI8C16swsbB+'
        b'S58/fsFIt0whylOJn1zZmDmeWdNjXzHCnKf8xRiEMb6DgZfjKZ4PnDk9OW8sy8uUKnm1XEFY+6x+5Y/0LaSFASuAIE0lW1y5dIx+/AsC9C8rWo0UW8Hnqnq6bCG6jlVB'
        b'8d8+KREvWmaJfo+Zsxj3PCu4Culi2WMtH4lBBGF5uPmRXGhV9bRPfAZqlky1VKaoJGK9YqmsonYUQy2rlyY8GcRgpCeioxGoeQrFggRBiaJWoVyqeBzVVD4ZQ0krK3HD'
        b'UrmmhgRBchWJJmQqeYVAXkkipQR8ZpQuJmYBz1dc81Q2n9g6YSTmSxAkP9eSia3H3ODbgadv8HOZZKPbKjYwNpCkrPKcYakVcwVuB7jgH+OY28gXvaYDOrcB6kJzYTc+'
        b'rU5ekg4mz0brmbf2cB4oXuFDbstzOhLSGNB5XECyiGBLFn1R7bdcKyAH+i3uvhHCLLQjIi9HTA7maFcEOgZv8UCAP9dr2nKhjTaQzHNzlQ3aHpWVKYLborJys0VZi+FL'
        b'qDk7jwtiUDMvYnqMliQvwluwE96KoAEmow0MgBM8zIbGIniQufx1bBi9th65skYn7dmTSvh06h7cXKQdczsNN8MXWej8GriRxmahbp6jAG2PQM25WSIWsERXWXDbPNio'
        b'JclNaBPaji6T4TPRjuw82Ix2RWWg5lBoYAN/Jw7SvQB309thT4WHngAjDyVbyTNFJjoRFMGdgo44akMx2Ep0hLlkfwRHPynk5VLknvesEF7nwgOV05k3hz1oD9w/Zm5M'
        b'sEwMugbuCCrnJsHr6BBNcl44vIp6kiPEqBkPKc7KRVsjhTzgjdo58FgabGYoeRptcRgBycxF2wgEbETt7q6caI+l2gBAv5qd8n+ad1CHdjO8C11Ds31cwURJLAeIIgHc'
        b'DyrR9unM48ZG1Ai7GUbhs9exJzkF9xcyD9NnlsEeSSwXQIOE3PnXFMIL9JBKL6hHe/BZMxrurQXRc5LpFwlZALzxFGfV8DR7EjqEttK8RbtqYccY5vIqMGvhDngAH7Po'
        b'55QzaQkS2FUPT8NLPEDlAHh+DrzM3KDus7XCXRhmy2LycFIbtpIe1AkeRPvQodSnRQLtkgh5NKYVOsKTSOqTbNiAygbwXARqYW7bN8K9cLNEgoxoH9zBBdRMAC8FeNBb'
        b'V/oig0Sico7BOPkAXsB8P0kjzXZGGzFKFzwPGzHKLACv4AUwN+DIWAUPSCQUwEfZAwAeBbUl0EgTzH5WrETCBdOlAB4DdRJ4gHl5LXAHw5VlREtXvbpYAui0JDe4yUGN'
        b'j8GpUi5ItUFMPknMcgcwZ3U6APXlOV+KJgIhm6Y4fGmVNdoAr9DZhwxNLZGOBffB3S/QADPgi+hotlgUnoX5S3I87Geh6+giuw6t5zF5BAegHl4nB3HM5cvwJodDYcF+'
        b'EW3BDCG0q8+G1zDt0kjyDE28ORL6lSgpbyEhXEb9CNkW1dKSbYFupD+jfaupEeXzleBRCaEC4KXZmLqoHR4Yoe94eJSmO9+7mlDXA3WPEBddcmXsz1GokzxPYz3QVqKx'
        b'bq7Mk8dGeBNto3lwK51mAdoOt2pJVngRvIkp9Xxd3hPEqDI6jYz0OnKk8BjhGLqFbtE8K4An6SRkdBBuRJuep+Xz6oiSL0W3GFk4LIRnJBIOQBdI1mYHqEEdjswIzXAL'
        b'NC6CF7IzRXlirNhhjOaygTfcwoEn4N48WtJsshegHdPIO5ZQlMkBVhYsuHMhPEbLw3f19qDYbxJWwPK6+avKmYdadHI83DvCyktzaE5iZm9mJOU6ulkWha4/Iym1cA/9'
        b'MgUPRAZFZImyReF5JGPavhq21rJlWBKaaeOGzuDBTiN98dhHVUw+8nznncOBuws0zPZuCGHzc55eQ+BO+vXVzllFm+p8eBbuZswF3Ml4FMYGIWNyeAUXnkG3mFQXuBN1'
        b'ccolzBP06AM0ehG10xLHRidQ46NX2jS4hXBj5JEWbsP2ilxaywPdybshueuGe5eNPBxeQt3acLLgq7DF7hFd4FYstGhbDtoVPA8vntAiFu7nZUIddkCEyrKM6XghGZFZ'
        b'+SIe4Gdb2LMIqw/TRJwLdySOfdbELvAI2z6yAissfXveAbcTgcHj5nLBHLiVfi5dwDxvTsMOVf/ki7lLENveFZ6n7TVlh07A7U896ONd7CKP+rJYWinhKWyVzvJZRNZP'
        b'8UFRQSjWN2JTyvLQVdqm2LmA1HFoC/Ned1qLjvNVPDBfAVAnDgngOnRtNI9yB9qL9mAMkU0GEMGTalrqhgSWIE4aQqcHRK0JZqQONpVVoz1ovwWAJ9B6AHeBMtSJ6UGm'
        b'cIF7IPYy0WyALs7FXgQoV6EO7WzcEwW3w8tqzBTUnFlYALuii2aiJpIvjlrhvjCxKAzTIHzkKbeIKEhT5KwMsnmavIUZkaQHq012SQFq5uCwY6UjbC62oV9tDzpywMYp'
        b'riROyrnkMRvQcuKGDsPdzxBQig7TSRHnPDClaB1ajzbEw+64euwdt2APVIhNHjy5ciQRohGbSNJ3WErRZu883vglLbk6hDdqtNj9N+HVYRFsxeK5FzYtwUUzFsJzE+B5'
        b'LuxaOFOzEF4eT2Hm816AvWgPTaMs1OFNBsUGbuPIqElcLC606J+uhPuwpz6UPeoyeWWscCu0i5a25agX7hxr3IPQCXbdHLmWJFTjGdaj5tlw4zM6jzYrGNbtXon20xta'
        b'hy6MbFaFOml7i86ugieWwMvPD1KQHh2mJ0lGN+Y/FaRYhZAQBR2Bm4UceocN8Cg6JpnQkCfDxj6LUO0m3EALmnvAFEkcD7vwHSQ2kaFLI4ljMZJgSdwSrKEGTJEkADtd'
        b'1LR1nwKPOuL1IuNSdAXQ/qEL7nMUUsxuOleRkCYuBhpx6Eal4SABm4692hTaUaJWDh814+hwJ5YytKsIGW3hxbiYgoxRGZwpmjXzabHCpuksxJbPGh2osmTeZHfL0E54'
        b'hgfAKjbcBFZhcd3CRC4bFmTAMxPgRTE6yQIsN4BOj8dxBv0VDtTlC89wAVhTCq+DNfVh2ig6noEnUYcaa/sGd7QtamYYeRoj9nL2mCXMFllghl3I0ZIb+MVoF9zLz8tF'
        b'zaJZtLp4VxRi5ZidkVWSUczsCHYWoKZckTgvJx+7gVPIaA03ScQj3hxtQWfnMV8W8EHHgTgGHWC8ZlesH5becxijMwGgNhyHoS4KIxExs1XAc2OlLAwZ2XVs7BCJBKAr'
        b'cGsRug7PPiNm0dhiktEXr5lKUg2u2GJHe6CYhXqoOE/YwSRLnEZdmAjoSr09jm4PobMstJUKkcymk4Hk/zAtZKld8dnota97z836WOGd6pI4efLPv/Zs/e5VxXvvLznY'
        b'v/HSlXanLZ9/KHrwLvX6nKHu7bM+P9pVr2af3Xbaem4D26lnvuvL7Q82W4D7YP4wawp79sH4wwuU331sOOcVUV19M/63Qx3x6iql21rq1CJv44PBgXcvnFkwTN2e+HWZ'
        b'/rP2vMss9H6DY9/+d6669b4X/ydnyXdT//lhEPve2c7Lh7/6+UTEYsldu3PtYUOLKq/F3mtz+uFrL4ddh+aucX+7cWq//4E9uR9e+fxSIW9NYkC+3+qv5im8ilbv+sfU'
        b'4z07+ld+Xj/h9ZXsgTfqyk9Yic13ZVWDTTVzLN+8JdZ/IPzl1YIdfwjaPa+08dafG755+9vzP87bsTZ0ymuTrq5bPnjt/NSGc+aaH9e9HTp9eeOmBT9zth/4Ib7B4s8d'
        b'W3+z+entuvM1/0iHsz17hJ//JPpytVXy6VNHAl9T/aH7fPCFcZfWB1u9w6u1PnsneuKyKxWqxMHAJaeH3jm1cTDwl/jmT0NWTd293bbZ33HN4YbXfzn56kOrW/rhIzF/'
        b't75nXe772bp1tt+1rnv7avpG5f1F27+c8Kbviz8Y3+q6fke1/0u/N1lvBr659IXvu6+//GPX7gUF0+qWvrVyc0fAm7n7RJNvXc9PXr3lcgnb8sa+g389+YZ88sxqBa+n'
        b'+OU5P3b/2edtr86woQfdnxR9cmjnkC/scf3+n5v/ZO371jdzDNtS4tNPSiqXvKP6pGhiKPXSoup/XH/4bUmFbvfRdv4Lhzu33Rf63bq3+o83fN4PqBpaFmxY0aOPL9uQ'
        b'/sqk01H1wrqov35Rk+v4M2tF4q/zSm49zJ/zV8+6+8tnvqQRfLAq/V374ktLGtrcL2wOfa+Sl3j3d0+vBe9X73kps87i9bcm3/mFW/L3lT6vyeY6Ft//9D2d6rPiuY1b'
        b'zt/Ne7f2yyOOwwt3fVl41DZi4Z9Du+4ndtzZ8vK8ntkLP7+apvx61S8Rec2LlrwifuXrrY0Tz3667Maw+F6e8wW1g+r4/Q01P9y++X3UYLxE+D1/YnHpa7ZetssuJX8z'
        b'MT58oefsmiURB10nrfRfUeazbdM/TqyOiUsvS1M2/nXDy5P/cuyVydXvyT7O2vH9d6kfy8cXPnzH6ULn990m/oqKndyS+qUXrT1uuG/N+nz1ztW/vf1D170PQ6N+bx9U'
        b'emQfjYqaHfS39Jhvhvbccuo+ULbt99kfLpic6576R7z8974Dlwfivvub7oMzl86f+eaB94dlWnHBwc3decvn25578/Dvhzv7GjouZWnnarM/OvPX+G9kB6k3oywOpXza'
        b'9VHq9JPS9ILF++9Pus6/hVaXmI7ZNey7X7Hpp55+xwsLPr/sDZYPnTji88/X/3ny9/e+7+dMKwx76LfC7uUko7Ir9+NvLv59zvC58PQ/VPvbtAe9vgl56BB/Yad00d6s'
        b'0+DLwXm/Hl7va17/7sT14/khsk2Tm2ed/e6qfWh0tHf9wsr83y2m7nXxu1YjtHtAx5sn4Y700XSFrbTlxIEZPkBec4dXOBn4kNdLJy6wZPCSF9wUES4WYj+FT4UvsOCJ'
        b'EnSDyZlon+YWMSZhArZPJTkT49BJOikCn1G3wl0iuG9kppGsCNUseuwFc/F5CltJOi1iNCcCHsx9QA7yCnQcHX0qYQP7rYvk5Lt7xYMA2nmQ3MLR5IgD2OOPnAjo5IjJ'
        b'aAedt4Ha4CZ4ywcej8jLjcxCO0ku31XWUnhlHJ18UYsjuMYs1JmNw9coEQC8pSwx1AXSqEKeNBuv7NHu7KPRhrXsanjW9gHx0IqolahpypggQzmDSQa5Cc/jM0ptxAjV'
        b'ePAsSwIvwW66twQ22T7+mgsfXlTasNChZLTzAX2z1IN0CtSNGYKjovqRb3Whi6jZdQqHDY8vEAr+n3M7/ocLNdmG4Nm/xif/xnxxZ7EmPi5aRSJCOo3kGx7zxR0FD7h4'
        b'7J/WOm3AOagpxezq3pRmdvFoSjV7+jZlmd3cm9I/8vBp4dx19tVV6lMHncNNzuF3vUMNnAFvUUuK2d17/8rWlXtWt3DMXgH65LaIFotP3L3vuviYnd3JqHrJoHPoe86h'
        b'5pDwU4uOLDI6G6UDIZNa81uSdbJ77j56zp7Vn3gL7vqIDVpjqSkq5X2fVLNPYEduW64h+H2f6HtRcWahyBwWaQ6NwEOYI6PNohizOJaUEVHmcLE5Unzf0zbA6wB32Ad4'
        b'+euD2n3Nolhd7YBHuNnTj/7o7acPbp9inp7+WsTtiDsVA9Nnmnym6VL14SYfEZ71hYGoaXgavZBkjWAU0YAnHjhKV9Nujz/2B2YNeGZ9FhJjDO5l9bKN4b2yvuSrNXfG'
        b'XVUOhOSZw0QGqZFl4N8NIhsoNDYYVgwEJdy34AR46bjD1sAnQJ834B1rjovXiwd8YkhmiWLAN848PkEfNeATO5ppMmFyf2DsgI9k9DPpNvnE/p3ewkHfYZabwMvsIzTE'
        b'DbNx7Z5PEKakq7Gh19HoNRAyZZiLG4d5wHecPmXYgtQtgW+wvnLYitStgS/m1jCf1O2AbzgexJ7UHYBvhCFl2JHUnYBvmMFl2JnUXYCvyFA57Erqbsw47qTuwcB4kroX'
        b'M6Y3qfsA3xC9ZtiX1P2YNfiTugD4ig2a4QBSD2RgxpF6EFMPJvUQEBxqDhWawyN/jMCfdZxhMSGZY9skJr1k0Ftk8hbdjRhvlPUm90qNi/rG33G8E9s32TQhbyAiX5dC'
        b'snnMQSFtqfciooyWnYmjLcG6VHNkTGdO7wxT5DQdRzfX5BFm9htnyDKFThwMndqbPBg6vc/R5DdDx8aECwgxzOgXRBuzTYJpOq7ZP6htxaB/jMk/ZtBfYvKX3AsMNlBH'
        b'QnUzSOJSpZ6PQfz8dWw8XtuiQb9ok1/0oF+syS/WKLu4qG/GwIR08yjCMBvgwR4DDYwCfTAh/V6Y6AK/k29MvZjVRw2ETW+z1fHuCuOMswaEM/CK57TZmcUSY7JRaliE'
        b'Py4weUTcmzAZU2G6UT44IdM0IfNO0MCE/PtsyjNO56KrNXmGG2aYfQT9ATFYcswevjqFyUM06BFn8ogzFn/gkfBIHYINLlh37wbGDgMqLpMyZ8/Eg8QVUT8BalwxhRt9'
        b'i6l7I/iGhSaPGGOkyWPaoEeaySOtT/uBRy4ZSTzgGX3Px68jsy2zPySpL3jAJ0NHfRYcZnC84N7pbnQ843WszBwmvGDRaWGkzljfxQoU0BN6MbQ3oJuokPaqYiAkd4ye'
        b'pLYnkjQw0XtY62Mn6iPf84mi9W/qgOfUex4+ZNKwAc9wXP3MT4xXGZ1gnjq9f0oOXnx0Llm8fx5ZvGcedS8gZE/WV55+xDitbV2rVw+6R5jcI4wuPb4XfXu1gzGpppjU'
        b'Oy7v+r7u2z977mDmPFPmvM89BJ+4+971E/dHpd1xN0UVDPgV9nsU3vUK74/IGfDK7XfJJVlQ8wZcw+66hOi1hlJT6JT3XaaaXZhvPQa/7xKGqd+Sag4I3pN1z1ug9xv0'
        b'jn5mPJLv5mfyjjY6mbzjiPkM0BcPuAtJ1ty0tmkGyaB3lMk7ypjSk3Uxq1fdnd8nHYhLNweFnco6kmVQH8sfDJpsCprcm9I3biAobTAoxxSUc6doIKhQl3o3ONwQ01lB'
        b'sth6Az4MnqKnhjmcgBzKHDuxl7oY1pvaF9AnvR18NccQjDXUGsRMMEp7KaP1XXF8b3Af1cfqFQ6IU+5z2cJAPRcbkKAww4RjiebEGf3ChIGgyeZgoWHWiVJsqQyex/If'
        b'+IKQqVjDMZDt4LgJ5gmT9Bz9ApNAQnLUfAd8ooxxJp+JHxIOjtNrBjwjSALafJNH+KBHDBGooEGPiZ89TZv7hVzg6ftzMRc4uN51CNSPN/iZxk163yHe7OC237bVVid7'
        b'3yHonrNnU+4vD2JAWOxPgIX3dzd8omlShjlsWl+oKSzzJzYVn02EISKHCEMwLtkE6le1DXZ674XZljhzPnD2KYmyYPLRHIY45MXsX8hD+5cdM7nVKn+eI6Z9L13sJnCJ'
        b'gMlbk3IoyukhwAVJXnP6d5PXDvFE4Bx/EnvM691ortpPJMLaB+aT3ygBKlYRpWIXsVScIraKW82xqhFyhxzoZ0I6hUyVqlIpVfJdGPlXf+b1kI4cVCPpYrJKgVQhkBEg'
        b'MU29PCFvyLKsjLyblpUNWZeVMT8xgus2ZWUNWmndSI99WVmVXKXW1MkVMoUSN1iUlVUqK3DFtayM5JrJK8qkGo1KvlCrkanLyujBmaRBmm6TRguyNDX5gtNm8IVNDA2h'
        b'DSHh3H4cmV7n26EeDd8Kh6p5yOAqUo2EdVGog8eFu+EuIZUmj5Qkc9TVeJhvbk+Utb6QDwscNv1lybFvfwsMb/9tZoooLGwbX/zuqYdbj7+aEhzQeeF3pz8uDGxe/+pv'
        b'wx+/c0gd0jZw5mDE/FdKFrz9wYI/t6eZvOLb3OKrZhfUn1QKeGUpyooDt2aY/q41lWxQ7HrpS5n7kLL503V+s9bdTItrG3yw9qS0YWvTl2vbX7R0uZ3y6W9e1Re8Vjja'
        b'Lvjh6BXdF22xIZLY6jNNs+VVK7wOy1JereNa3Tpslf+Dw+6MG5bHW6VVrRVfFZa7FS58sVB6Xv/G/Fe81L7jq3xtq5xFX/EmtM0zV31fvv/qltVfUXZtbkNvjdPU73A+'
        b'CNPcpx78zGe1Tf26bJuGD/J2bTp1z2vcR/fcli5+u+hEYMknguDuKzt/K2ej1yc35PV+EbRse0NZxu1tG3O6wt9+adHM/Zsj7xw9a86c8svh76ccG/49KLQs4Hf3XSVw'
        b'4GVLyben12oP62bu8fqieG6cyT3zNXh8/1b7DxJWN339wOJwwcwZ19KFHDqKhxdzNGh7DgVwzL2VmgTQTnRw6QPyRjarOGvsbyt4+5FfV7CE2194QO7iKdiJOvnhOPgn'
        b'B49HUDao0x92c9AF1AHP0AcVFdoVp4bnMvJEjx4tHFELGx9YTkEj7IEdQk9GSS3/y+J/LmAnpxJBEv3X+MwfE6ljZapTSiuxBqSMhukWuPwdh+mRwNZ1mGNh5X7X3qkl'
        b'dvtSXcD2VW1qfaxeemR8+wpDYfvai0FGVW/ARW1v4cVl3eLbKXecUMZAbM5HHl66WJ20bXy7lT7L5CE2ups8JvVPyTO55/XPLO4vmWWaOXvAffZHbgK90x5Fv0MQjlk8'
        b'5lDYQzi5tCS3ujZNf8jhWYU9dOBYBQ4DUthYCqzNNvYtbsNsUvP00VUxtRChYQJTk0zo5TG1pBl9s+jaPRqDS2o0Bl2jMegajUHXaAxSw4GZrQPGsWDqXr4Ya6QeGo7x'
        b'RupxEzHmSD2ZSqEwNv3JksG2Yuo09kg9MraX1zfL7OiuqzJMeF71R3sM2G/pg2NeJw/cwvx3n88LxK1+Dx1yKKvZ1H1A/zNcygLWDnetHFrUuvEttSarwIesZWwrr4eA'
        b'lMN0+RMbWI8jhcMwh25dYoHrD1iUVezB5dhZWcXSnfdJwy/DMj5llUnddfI/btMvShsQpA84ZfTbZDAubFuyT4oNeNnGOcWfzbgwlyEWFpj/Pgf2XOF1eY5Te+zYUkYL'
        b'cqeqnjri2IQU5UD8msPPpPh3/dpRXizo4k9ly5f+04tL/xjMnepSWfNUu/VJHim3piV922hteW1Tev+H7KTXYve97tdXGc+dfe/mq3U5Obqvcu/H/nSdY+cUZ847PDX3'
        b'klPNrIQvZLd+vveyYfs7r5ge/PiXrKO/nf+mssLt7olTU7w81tvEZx0sPJLGTt1uN9WGff6Yqf7hG/PSfyjam6ooVvijq853PF8WWtD3McHwliP9U0/55Kdesi2AB+zk'
        b'wy4WMljI6V+LkcPTsCc7X4QuEqB8EQvboevZaBsbHtHEM7cPTWg7XA+3k0dKbPuWIn0ubIa7LICdE9svH62j70zQXgxymnxjBTZG5jJfWElHl+gp0GExbMx+8lekTsFL'
        b'fCELtQSh3bRZRTvnTnryZ6ZmwvX0z0zx0P4H9Pff1y6LyOLS7+Zd8ADSwVsRwnH/uX38X7/ueK5Qjhu1qM/a0+faVrlCrsGqkjtqW9Nx8Y9GEiRxnc22LoO2fiZbv4PL'
        b'BmzDGtPMHOstOety+h0Djk96nxP5Mcf/Txzbh7yVXG7sQ0DKv9Hl8Ao+sHFpzH/iKw6CIXadTDHEIcn3Q1yNtr5ONsQhGVc41JRX4JIkdw+x1RrVEHfhchzwDHFI7uUQ'
        b'W67QDHHpn1cZ4qqkimqMLVfUazVD7Ioa1RBbqaoc4lXJ6zQy/GGxtH6IvUJeP8SVqivk8iF2jWwZBsHDW8vVcgUOqhQVsiFevXZhnbxiyEJaUSGr16iHbOgJY5mstSFb'
        b'5mJIrlZOmhAdM8RX18irNGV0gDdkq1VU1EhxwFZZJltWMWSFAzUcBNbjmI2nVWjVssrHFoe+iir/L/8EAsZQ5I4W5Ee61OS7sX/88cc/sa2wp3BoSozF2PJHuvx3TAex'
        b'kbetecle4LYXPzmY/avl6O8qDTmQMJSuj3jZX72qxv5UnkCh1AhIn6wyT2ipIhE6iVWldXUjYqNKIE3WmLwqjZqk4g3x6pQV0jpM2ZlahUa+WEbH0KrFo9LwOIodspzC'
        b'hMeJKjVgInR1Di6G2RRF3WdxKM6wDeDbNlr8yMniUS7Dc22AleOgpbfJ0luXNWgZarIM7Y9MvB2CwgYis8yWDnet3frdJQPWcf2cuLvAocXjA+BFz/Z/AKbOar8='
    ))))
