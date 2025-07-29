
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
        b'eJzVvAlAVEe2MHxvL+z72uzNTtN0szS7yiYoOwqKu4jQLIIN9uKCGnGlUVBQog2itHsrLs2i4pJIqsyM2btNJ/aQMWGyzGQfkjiJk8kkX9W9qBAx37z/n3nve+21qFt1'
        b'qurUqbPVrXPvR8SEH3P873e7UHKIKCcWE5XEYrKc3EEsZoiZahYxxa+ccZokiF7y0b3UqpzJIMTs0yjf+xhqLSGzWsJA5SblrMnw20hUair+VS8kUc4uIswreSY/ii2K'
        b'FmTNmsddXVeuqBVz6yq48ioxd84GeVWdhDurWiIXl1Vx60vLakorxUILi3lV1bJHsOXiimqJWMatUEjK5NV1EhlXXodApTIxd7xPsUyGmsmEFmVeE+bkjf5bYkJ8ipIm'
        b'oolsYjQxm1hN7CaTJtMmsybzJosmyyarJusmmybbJrsm+yaHJscmpybnJpcm1yZOk1uTe5NHk2eT1yFC6al0VToozZSmSo7SWslS2iotlI5KK6W50llJKJlKO6WTkq20'
        b'UbopXZSWSneliZKhJJUeSi+lfYU3Ir3ZZm8G0ew5mZybfcwJBrHJe3IpKvGZXEISz3k/51NE+D+zbh2xnrmIWEeaV/EY+WUTF9Ye/XfERDAZ54YigmeaX2uG7lJzGARi'
        b'hvVFZity/xEWRSj8USE4GQ12wT2wuSB3LlTC1gIebGWmZs2fIzAhgjNY8Ja5BY9UeGLIswGwSZaVB/fCljxwC2pgC0lYZDGA1jeujJyAgsMjFFQoed6+CaGBKEYgKrIR'
        b'nUwRVc0RNS0RNa0RBW0RLe0RrR0rHCi6IcZq/hUbbmZQdCOfohvjKdqQzzHG6TZl3WO6VfwrdMuj6fZmuMn0MgaHILgrrOoScgiq0ChgxqoZOLciN81JThduX2TudJrk'
        b'orIVuX+yrKULp8exCvcy7QgiZUVu/yopcZaotUDFPyVyWA8ciJQxxw1kCftK5PLQGLLWHFVEZHaSWlOCm5Imi/qjNNefQVDFcPq3th22ZMjYnJ/InxdyOSHECKGIQBXL'
        b'4QV4FK3gnvC5ISFwd3imAO6G2+FucHZeSHYe3BcmzBJk55GExNZ8BtwBOyatFevRtBvwWjGptcLrRFQwH68G8z++GpW/Xg3TKVbDkl6N7y1sCcSOnIji8HnH5kwnFOGY'
        b'xuAaHEA0aOHnwBbYDPqW587NzArLmk9E5RQ5g455YA94nqhkm8IesBMeVDhhgp5ds0oErrIwZxPwiOcaU3iFqgBtbHBWBAZxzRFiA79GCo8qMDaBoAWcEkVhkIMEvGpd'
        b'JnFQoHUlnNYuXo6E6ACbIISE0MGEwlOyzoJAvZlFFF+pfdGmiOaFP5k7EAF4jb3/su65cD5RXXk7iylbj0qiH7x1+NXpR7Y2HzvQd2CDmz8TruLuanQyrPldbYXdsoB5'
        b'DFfm7ihF1IK+yAj1udWMz/NL36wgeyuzS3krcksviDWlxDn2bnnkGa0gJYpJNl7nFBqXdAa0ZxiLOPp0TlF8W8Zd/dKRl63kyY7X/7HdLX4Jwe9x//TTPh7jAdabZqAH'
        b'HLJExOPlKQRWNaGIjxiEM2himQEVGHzggUC858BDiMS74T7YwgQX4CmClUCCPrgTNvFYI4wQntQaQT1JZJi3uI2NjT+6TK+Q1jWIJdwKWu8LZeuqK+RJIxaUUi8pL5WL'
        b'GybkGbhxE0oeNhJj6SRh56iUtcU0N7Q0qObu3qLcct+Fq/NNHJqv903Tu8w0uMzU2c00unioyvfX6lz4arnORaSRK2cbnTxU4vYCZYbRyfVQ5v5MlVidpp6rTuuu1jhr'
        b'1mjtNbLz7tr5Q5FDc4dEg4t1Xil6p1SDUyqCd+S2zVA76x2DDY7BOqvg7zBHSjFL8kxG2GtLaxXiEdOSEqlCUlIyYllSUlYrLpUo6lHJrwiAmXcFF5NAaoMLbVEycaJY'
        b'/8rq8UTxTGeSJOk4RvxWMmrjqqxurmmpabQcY7BJJ6OlgzKuOaElYZRl25izNW9HXmOe0czWaOaotHw4xibYdpNLGwvofzLMi8+b84lemwTmrDLGVAphEwZhYDNKqQTy'
        b'sUpgTKGgmeZTCDkqYT4l9oznmOMqYcq6Zxu2x4hNUAkm+ZT8sTci8T+A1Jpg1TxCUGCtwMpcBK/nwQPIOQqfN4cItwP9FCjcOyOSFtQ8U0K4eGN1K7uVKUvB2AoisQAe'
        b'O1BNMmPbMNe3NG8tjXHMPbnn7IE+ZczOawfOWrxetvLT3m9Zny//ndk8aFbk+Ppwpw0xMs0yzLaURz5wQ91krYE9/GUV2QKozMrNZxOWoI8Bj8AXnXjMX7MHdtwe8caI'
        b'Jc0WFbV1pfKGiTeUNMSPS8M8knB2P5S3P0/tr5bpnfgGJz7iV1snxB3WAUYOYvhOyza20dG9LU4V057UkaSz8pXaPWFfKabMCLtcvLJaLsV2Wuo4BctSPEuzrCtm2Yno'
        b'8DHUGopnMUJFiGndMW8+O/m3Mu1B8zDivE0ik9Kmb7k5ktGMejZjzvDqhQHx1gqMrQccAgdlcnAR9MZGsAjGSgKetgPnqQZ+fs5kPEPFZEQMrzYy3nagtHpNHFsmT+PF'
        b'RpAEQ4ysQjIYoIAPmLmQ0xkP003rh1ertsysUrhgxa8G6miZXFEZG8EkGJUE7IWd8DQFP/qcG5nCaFxmTQxvXih8YzVtS3YvkSFkdojiMC4SAp6zFVLQr3u6k+kMsyiz'
        b'lOHNnMLbFVTvXqDLXCa3BC/ERTAIRh3u/QK8RMH/xdqTzGTc8TLjIvjo7lJqrimwuUwGB8Hu9TEYe7CdgAPFsINq8I2PN5nLGJWbrBjebBRJ5iswd4JmcBXeRE0Y8FhM'
        b'BBs12UHAQdiRSTX50tGXnMNQp9jYoSbmJVsUzrjJYXiBJUMmMIEaAyF13qmSArdS+JPzGNzFpnMQShbhNPlBG8sKDihA05pIPGNkdeHAXHiAarA6JZBcyIjPtYkY3qwy'
        b'+QePmvOGPHcE7wPPRuI5Y8M6CM4UUPAnRUHkUsZwLqMe4cNY6EnB28BusFsmY8EDIjzAFgJenAaHKPg9KTxyBcMYziSGZQv9w/kU/g1g1xo0QKx7JF4x0EXAIX4WBe62'
        b'MJQsZ4z6mBAvyVS8wTSq+2TY6YbAE8FgZIQpgj9MwGsryij4o5ZhZBWDmG2aMiwzrl1hSXUfYjkTDsjAC6DPygLhDy+T0TNoR2VGhpCsZXBXEikvyTi1o3lU98+hJb1m'
        b'KXUvoHgTnEZuBGgMpOCXL4wk6xmq2QQXYe9pvoqCr3CG1y1hXwq4GYMbIJebGQYHKXgWQ0TKGarFbO5LsoVB+U4UOvC6DbhqaSGrisKLBQ+S5uBEMMWJYZU2lvDKSqCk'
        b'1gXuJMn69dSKwbaUEBnynvaCo+ts8BSOkXzQaarg4NXcAbeCPTLzSpE11OIOb5Gx8AxsoytVJNxruSYBHlfAK0iBwj4yEGyDF6lK2AMv+siQ9gPXpHLcUkV6AxVsH1+T'
        b'vcEyeSY4BK9a4rpWkl8XQAljPjgLO2U2ZcnWiJpMNjmj0oPmwt1gd6jMBraAk9Y2JME0J1Nil1AUgtcLCFRxKMN6DZ7XECkE10Aj1UiUCXosrcFVfj1oYRFMfzJlGuyk'
        b'akxgM7wgk8Yso4SgnoAXSsEgLeBtZvCkTG4ti402IRgVSB/AF2EHPVIXGIqQyQS5IkpykLD18+HztFztAseAVgb75OASHLDFVLxIRruCbfSi9GbyZPAKaTpedY4UVTnw'
        b'bKlVnOUYQ65ncGPJFcMyVemQN60c5LHkJgZhaboCsU5ROYMqbFsUTzYy7hSa2SFIB4MHVdiwPJHcwdBNt7FDkIuFi6hC+XMzSCXjzjJiDmLU9G+TqMKCkCSyhfFws80c'
        b'xO02f62iCn/ySiXbGA8XmkegPmNfzqMKv1gwk+xgfMq2ikCQcY2WVGG4PINUMZSLresRpGdINVX4nMNsspsx7GhVj1gw3LGGKoyvzCLVjKE1VsRwjbFBY0oVvp+QS2oY'
        b'xjKk7mpUm7fwqMLrq/LJ84z45eYpL9VwzP5UThWaB80htQxdOMkdrllY0V5Hq5qEQnKQsXCRNfelmoXF6evppdrpCm7ILBVgtwVmCSsyBd4Elyg2ggeC4UlLaUyIjTVi'
        b'I3tyhh1Ja6fTYBcb8fpV2CtYhwwwZmh+cCq9hkNb4ItIEMAlOVKQmC07SD+0m1DxWBQOSeTvyG7mp37M+pfWqYikcKrQsv4VUs3U5rKI4Toj58QqqvDmnFfJk0xlBZt4'
        b'qY6zujCZKlwX+wapYXKyyJThOo5zGGvSNoz9yLl5DiXPs8e3zCxqu0xUsP8nN8YmxNN+V1C+govuysAVeArsKYB70Z6gOcsUXs4Twma0cXBZwQoGg5upeWfGUU8diIi1'
        b'F4K+zRjfPR+fZkYgtyQiwqV8i404g6AX4Fgo3JYTngP3FmSxCTO0V+2by9gAu11phXKNi2RsAAyijRlUggMEuYgA5xsW001fQPrmMj9EEJq5BSrDkd9lVcm0VUAlxQ3g'
        b'ZLQXGECoDiBEEolEcCpbirGgULnHR2OhjUpERbjQ3dqOLvTNNyGsCMIuIrbB7su5LIISYznogv0ivOUG+9GehyhF2HQoAtH9XNABz+dQW6N94AA4gR+R5IB94VngQghJ'
        b'cOVsGzBkQW8690G1rSga99EB9oFWYuU8e4UvrrgJL4AdfLSBhy15iOv2hGexWPAc4chjIqV3Fl6i3YmT8HLs+A4UamzRCuxJoFWMGp6qFIF+vGftAWp4laiNK6JHbIaX'
        b'OSIRbnK0AfYRlbXgFlXhxWeIRCaY7PAY7CJWIaHooA3COeQknBPFUioengD9RDloh9cU+Fkb2I7mdwYem5aTjZHMp9fKpp4ZHw1bFQ6U4s8rE8ViPDpXrifE/qBL4Y6L'
        b'X5gDm3JyUQN4qDActvJJwnIx0pJxgTwGjecQPDRNFIvcXdAlBD1EBWzfRE/tOPrXLIrFqB5eA68RleAUm1IApZuA0jYZ7kHb1jw2wfImwfECsIsm1PbixaJYJGKgG+6w'
        b'IKqQqTlF4bESKfRePl6YzWWwOR9cYBFWM5i2oYDW8UALz4LjInAF59VrwXGidjk8Q/GYBPYuRtS4DPfkorkzCSZ8kQSH5fCwIo9ijmakjHKzsvLwY7Tx5xC5c0OEvNA8'
        b'IU/AsACnxOA0PA1OhoSAsy78dXIeYpqTfCfQ4eIMT7qCMwxk5JzskIN5taz24S+//CIkWTRjuhSnzl2VQ/Pg7BgwiFRUPz9fkMkiWCkkODeznOdE26cXQC/cD/aWyqyl'
        b'CqzbjpL+JWbj9q4NqF0L4YANXXOF5HGjaCM+AJ6fiZb5HBwYb/UiMv8Hl9JUvL4caqzlMtSK1oc+nIVUxbzVAfORX7BGYYHdzhskF/YupOnXzJjrA08ga7cODrIph8W3'
        b'cCON3sHVnOqlcABVWJOUtxAFjm6g0IuHR6YpwBlLG0uwD+nrxeQS0DOT5sWjyWAPPJIok1usww7TC6QnkpQhqsNNWxCf7gEncB0eaivJ9QDdVIeFW0ryc+GAXAoHsdP3'
        b'IukBWqOoRktWwnYZ7Jeb2NkRJDiKBBJJ9fNUVSzaMzQ7gvOWZtYWBMGMIzORJLfSduM6OFoCzoA+5BquscLYd5HB6Y4N9unz51RZWtpYmaMG08isRCE1/Cp7N7RM7cjc'
        b'S5FHxbQh42C/lOqIk8FG3ZxANbAfmyY/MhXsgxdogUwGNxd7yNZQA4ArpDfcxqIlYE/icnCUL7OgF2g/yY0A5xrsxVacgHmWVCHTgYzYuIna4Yrg0fJFz8EDSFzCiDD3'
        b'tRTvQs0McFGxAeyxtVizliRYyDsBrchXO0ZbS22udQM8+2QabMvqtSMES/YpEqDCj08cmTejwCPV7v6lGwOtfea+Jtsdh38m7XVBXtaD1R+9+jY3JzUxx6z9vtApeFnq'
        b'9pCqi6Mn1H8yHZv2cMbrXy/78vAbLvbBf3h/88B37x/+Q0LJ7LiwGp9+fuSLcbmi0c3f/xD5x69vid5IDZtjxw2v2Tj9xIvzb1kOrjj2FzK54Lv75631099b9fJaxctb'
        b'7m9YOv02+xXmhwXfLbz+2d87hpUFLT+fkFu0pu0wxpz50mhp0/+ux7ENvts7t1WkHfhRm2usS3pfVHhidlW7Ju38J+LMCyuqP990uu/gp7dW//Mv/rcPmb+/5uGC2zfe'
        b'1gDn87lHDi/yuOcTukn5xTsOBaZX/C8/17ti2f53X16UlLp3X/qWNz7r8fu5eXRG0y+zNv3zvOG99U3vC/78A//9iysWvZa8/ebh/M/cCiT2psymW1Xzd9y++UqYbPDw'
        b'6z/FLAk9Psdm07uf+/1u6VtnXJQ3LL682j544zOT+/CQbM3ynqINfa8b0/PTE05s+OuiaZuvbu80Db7i/95B07W5rNdvd3zR1rov9/gBP5t3r+YkbMme1jNrRYbfsrej'
        b'lr2TPXt9j9e9P3212PqTaRdyu//6WfxXG/TG3vizC7p93luyNH3AJPTBgEnGK78UtHrsuljjl/zNwq47/QVvuWRpP7e/0HDlaMwvRRvnVScz/vFS15b3ic+/OdXfK+CZ'
        b'UQ8Ci8A5JGB7wvJhcyg8lQv3hSFFDXqRpoYHYPsDfBCwFuwy5wuzwkJ5oaBViCBgM2JsLmt5FrzyAOvYMthvzoO7Hj8sHH9Q2Av3UNU2oNcZtCLdJ0Sashn1bwL2MgRI'
        b'Xw4+wBqphpWeExaSCVtzSMIM9IaDJuQEnAAnHmAZjQe7U/NAY05WXmieKWHCYpihPm49wN4I3B4GjvMzw0JRn8jotcB9THhzDeE4jQkPoz3jiw+wjC1GSiGnQEAWgU6C'
        b'sRYJXwfU8qx/9WTmv57IcMId/zU2Pn6q40A/OZFLSyWyUvowq2GKMuoZTxdz/Ikng3ALHCNySOsF5Df0nzaW0dVDlWtw5aGcE0flqXMKMvoGqktPumrsNZEax5Oebay2'
        b'he02GCyz47l7roK7rgK9a7jBNXyMiLRPGg0MbUtXcdrzjUE449Ze0F5gdHZThXQsv+csvOss1Mj0ziKDs2iMECBobz91ZHelulS9Ur2yuwY1sG+fPaHlmAnh6d0T1xWn'
        b'ju6c0T2jLd3o7q1a0x3cNtPo4dOT2JWoLutM7k5GiEVpogweQgTgi2YU4Jz0DU5UbCM3EHW9Rr3ypDl9Q41E3Xhw1eldM1QzjKJ4VbraW+8ZofOMMHr5qcu7lqmWGSNi'
        b'UKmH3lOg8xQYvf3V8q7VqtVa9pBTv7XW2hjA08w7nqfO04qH5P2rtauNnly1W3fBPc+ou55R2hi9Z4LBM0FHXU+6DI9GXbrrPcN0nmFPSoUiVOrWWaAqwGW1Oq8odOH+'
        b'XLpz73mG3/UM17L1nrEGz1gddT1uOSqM1JRpA8+uOr9qYg90r/wIVObSmavKRWU9y7qWdZZ0l4wRtm5Jo6HhqMq5M0eVM2ZDePn35HbljhFkaCppnJn5DZMMzULMQHpl'
        b'kw+odIxKRwOCNYHHcrSB+oA4VYbRx1+d1b1ljGB6JRm5AepFJ23RRoorQpeBK9Iq9Nzp9J2eukZpkHvc2LvcWFw7w8CdoePOQJlRH1/ET8XtVmMMtrtDm8mYFeEf3GY7'
        b'Ts4xwsQ+iUrQwoaEXbI5Z6OV6UOmGUKm6Z0C2zJUIjXb6Oo+RrDQWiuoPxpnbZDGR+ODycpSFXdbqefrOXwjmrOtytboFoKm45xk5HhSVSU6Tgy6DJyYISc9ZwZ9p+fE'
        b'PDQ6uqrMO5J1QYk6R3yNhqUMOw1X3/YxhM1FvOnSkat21Tvx0IV5m9dRogtJ0jnjC/Gl2qR7+j0P/l0PvmaW3kNk8BDhQReQxvCM4fI7CbfrDOHF47gV6zlhfx9bwKBk'
        b'b1wSJzxFNRuxmii8Uz1H/bV6oM4JJ2oGKX72P5UqmInB8WEcfSbA+L8+Xv0PPWg9ZC4gLthMY/JIykUomA2252Rt9g7LQl4ncpwOB82ZtIG1frRL3IuS563HN7D4vJd4'
        b'+sS3wvrxhpb1H9/QVvEYf1uN0LPgTvjNwXSXcUsnBxRQUQob6sXcvHkJ0RHcOimViRJOajrpJkvOlYrlCqkE91VbLZPjLlaWSmq4pWVldQqJnCuTl8rFq8USuYy7rqq6'
        b'rIpbKhWjNvVSsQwVissndVcq4ypkitJabnk1xQ2l0mqxTMhNrZXVcUtra7lFGXNSuRXV4tpyGdWPeD1inTLUC4apndQVdUxFQ5XVSdaKpQgKx1EoJNVldeVihJe0WlIp'
        b'+425pT7BYgO3CqGGAzgq6mpr69ahlrgDRRmaujjx2V0IEA3LxdISqbhCLBVLysSJ4+NyQ1IVFQj3SplsvK6B96uWT7dB67FiRX6dRLxiBTckTdygqHxmY7wEeJpPxktD'
        b'JbXianlDaVXtr6HH1+oJcE6dRF4nUaxeLZb+GhaVrhRLJ85DhhGZGnhlaW0pmkFJXb1YkkiREzWQVJQiwstKa8vrJsOPI7OaxiVdXFa9GrECmikm1FSgZQopptCGJ9gs'
        b'gCerpArJlND4xDGRSlGfirIqBCZDd4rVz8K6rLZOJn6Edoak/H8Byivr6mrE5eM4T+KXYiQPcrGEmgO3UrwS9Sb/f3sukjr5vzCVtXXSSqRfpDX/j85GplhdUiYVl1fL'
        b'ZVPNpQjLDXe2Qi4rq5JWV6BpccNprcutk9Ru+G+d07gSqJZQUooVBXd8amLJVNOiTlF/Y1Zp4tpSmZxq/r9jUhP9kMTH5myiLXqs7+rrZPJfdzDOGWJZmbS6Hjd5lubG'
        b'ay2uXvkMjLHlkpc+Yq4FyHKhoWprn8Fh44M+YcfJYz2bNf/LdJeKkRVFQpfIRVoGQRbCm2U1K+kBpoLHughNvqRGPGGpHiGESFALb8pk4trfaipHBv4ZRBzvB0NMjexT'
        b'FjdHISkXS6a2mOPDIhs5ha2ePDCC+a0+KtdOtruz8WrDkxVyGdJUFciJwdVTNayXogVAOq906nHnjFeLJYJ8qfBZ2E8a+ym8p7b/44zwKx9gUuNn+gN022o09NQNs9JS'
        b'85/NdiV10urKaglmqad1SMF43UqKIZEAc2dJxavL1z1T1if2/C8wNA3+X1QmVaXI2kyp8maLV8KbSKyn0An/DYhhMaDkDOu5SXjNQzW/LWyS0tXiJ9pu3C/mhuSj4in5'
        b'VCGtp/yip1oUi6XrxJJyLJYN68RlNVO1lonrSxMnOtaogwle/RQtlkgkyxK58yU1krp1kided/nEfUBpeTkqWFctr8JOerUUe6liaXUZt7r8tzz8RLT9LF2N1SbCaV7V'
        b'r8KrJzdMHN/nJKJ9wVSWYTL0pBNEG+KZobXD5Yzij5jU7jjMPHw9ffj2eQ0r9A8MKmC2dkfNBoI+iujOhSfAAIMgphGwE+6btgxupaC7Y00KPyKp6NywN1ZZE/SJ37m1'
        b'sb5w76NYzTK4w5c6vhJFFi0u4/OyYQs/P1dIPyXkmxC+Pmz3pdN5VgocmymFR5hwT3h2lgDsjoUvhGfn5QiyYWtOPpuIhK0mfHgMnqHPwlRwD2xSwIP8CSAO4CgTaMNq'
        b'6EMvbbL/44MyuFvx6KzMO56qBv0N2bbgFHUqNuFILAnspqu3wjNJ8pVwDx+25mULGIQZvMYAuyXgsMIPVfuRm/zBUdx9FmzJyQetcF94JmxlEj4OLKiCSnCDOpuEV+Bu'
        b'2QQofFrbHJ4Pt8HrbCKAz56OAK4oeNQxA7jMgKfBoUnQ1KFmfh5J8MBNNuiCp8AJikzwYD7omjQ6PrPMcwLXSCJgBTsFHICN1MlmGLy5gi+EragzYXYe1MITsDmMZ0J4'
        b'wMMscAJcTlLg585LLUDfOFRWHtwN2mIwjKszKwJqwSk6VL0NKuGRRXDX1AuI0N9LLX46vA7OgRYvURQ+hUQMVxkyfnY5pw52w91PLxcYiKOYLBZchj3wLDwnimLj00ai'
        b'KoigDjVtbZzgAVOCiMBI7IgwBz0KHBILdsSVPl7fOHjy0fqKwX6qPhrRBmrjf73AoBcM8Rh0XEszPOUjtRWB/noTgswlwEVwTkozfHOiHXihBtXgm6NETQZiO4qp9oK9'
        b'4Mxch1/zRUgMz4RqqcgGvfA8PCgS1TMJMocAFzaL6cO5EzaFYKuFSAS1bIIsJMAguIpoRh0x9cBTxeBFeFUkkqJGBQS4lORJH32dhV1w65b5qFU/alVMgCvwKLxBkUVW'
        b'tNY0XCTCx6zHiRp4FvSOn7dXxtZ5i0SYhieIWngJNlKiWmnnsrKTWIhFddPLRU4EFac5E55JkKEeMoil4EBGBWyiQDsa7LidRApB1K8I+2BTLMFjUnN3ZzuDq774bLWV'
        b'pqcZVDHA8+C0BUVv2Fa5JEcoCEWLmwZP54CLLMK2mFkLtwM6sntp0nS4A3TkZIWhhWKxSNAzdwtaCPrg0hS+KITXnhANsUozfQbZi9h0G9i1YiLhWvwoIUyJ9Easf+lZ'
        b'Ugj2Lx5faHgM3IQX0zc+oW8s3E51vwi+iMNVjk4k8DYwSLP8+UjzKWS3a8O46L4ImqmFAFp4NLY44fFShKYqgvGg+yuREump+E2B7uTQBLgId3iCk7Dp8bqBA2AXhQUy'
        b'nrDpaVGH52AvLeur82lmPpMBNBXghkhEhSEQVaADdFE6wBxub8jJEuQL4e6wENAO9o8f0BAeoIkFTi12plY3Bm5FwnFyFT485wmyWIS5KQPsRUp2H8UTovk20w8w45EU'
        b'rggbEC6lD8SFUUiaVPDAhDWNZ9HMcKAGNIN9bk9xi9CaOvleA06v4mcLcgShsKUhH7/MYlvJFIdmU1N2tAba8YCO8WAO0CpFZMPxAh65LLDfl0lNbKnIenXBZMCJUR87'
        b'c2ldeRh2WayA12hdAfZOtCmhZWzQK4Iv0HEse3jwEGhmTYyCYWywAi3UGziSxb4z4I3JMSJ0gAiHSbESKwVcXJEzOUABXNqoCEV1G8Fp2PiYFvBQGlI9+8Lh7lx8RJeD'
        b'px8FDplkpcIdNCZXGAG28BZCIzMsu0BgQljmMJDc3zSlFd++teAGOAqPU5EUE+Io7NhIUjF1RWCXGWiBL0yKzvACdOTgkkRwnAl24XidJ9E6SBipqCJk5tXwwJOwojyh'
        b'Izj8OKyoWKbAYfTBzAZL5AsUEWFgW1GFJxIy/HzeQ5ZIqxLQZJEB9vMpbSTkb0mGg5ZSE/zKB/IG4qCGPvU+g/QmHTZOwKHFAhZoptjM09VM+CGDS73Es2lNGTEe1gqu'
        b'wcMiZB8OwEOmmABESRjoo0Mo9sMecAT2It4diGCiew1RhzFXFOPKw+BongwtCWzNmjsH9EcUFSIrht/VEQpC0ORDxwNGihAVoTKsOBPPmqLq3MwwXIMEJWf+HNjKcWYR'
        b'4NZGe9AK2hyoABG2hC23pV8sstq+zoVQ+KDxArLkE0mHdEnLk5CsU1vGg22qy5lAvQgMRGOrMxcpO9A7n5pnhAxp+91IYaIqklJ1F5E9PKyg4oeeL9+AFkaZBdvhQdgB'
        b'lGthB9zDRQjtBhdiwUU26F9ZKF8JLseQaM1NFsnA85SIrgUt4Ji/YEKXYJ87YhOKzbbDA6tyKOsIbsFjSEZNShihsDGWYrNQ0Af2jyt02Md7otA7E6l6iZmFDzj7lIDD'
        b'PriVmqbPUnAld8mEacKBMIrHAjblTXBJtiElM8ElkcJeipTIEgPlBJ8kBXQ/9klOIklljdtp0JjiCFpEsWuQYs9Gs4un+a4Abl9uD7aKok0oL0QML/tR5EgBjcgw9PBE'
        b'0WsROVKQgQVa+XiAKTzjZR+C8IVagrIE/eB8Oe9x6OJ50BwNz6PqSFQ7CzkF7uCWYiZlJlYGWiIS7UHrvicc7iuCWmvQFx05J/MR4xUKkuHZ4sLJLMXCLl+PBRpWPYOO'
        b'wRqAl8JBL0J4E7b7xzaBy7MpnM2FNeAK2A56Y0Efg2C4EPBcUQEd7tUN+5Gh6EU24zki3vW5GJZCgIrjQGuUTIBfIyoMyQyDA7NCKe24YNLoCwSm4PkQeEiRiDvaCS5Z'
        b'WObnwVZB8biEwOYFmdnzM+fFg230hMDZOVCZJxDm5xawkbWBWguws1iOeBrTezNsB53jL2HBgUVC2L2WFs+DCMdLjqGIdS+gSthJIPdIDbejZrhaIoOqcRaLinvMYdIU'
        b'2obcgIdmu1o8xWFFyAHCixKbzEVyvxMHNV2hgpquktEh4CC9mjc9RSmzZPBKva0Jqmkmg8AJeIQKPKyOZ25ny1jISsYf+/iCS16dR4a84vv3fLK6o6v3xza/fbK6Oi3H'
        b'wsliq4uZQDBbyD11Jikm7fmwhSeid1fEc+M5i4BD2tJNRstr89TLh4bdJD+xH1r+RNhs/kdUzV9b1r3n9M7Bnsr3f7h5qdPn8+T+N3PB7qSmhxvjjZunDbzmxDwd/zOr'
        b'/hN5xZVFb934rkfK/uL17KuyD+eod9wJ+DD0wzOnNt6xf010Pv8j6anD9cVjkV/59jA/5C5LuLv6u6+dOxwzpKMql4b8n/jfJr58c7Rr+dfcnm87LjE+276uZ+yb+a98'
        b'FPPg58GPR9+ynhH9ZX3Qog9dFrVv2iEiYn+8L7Z7ULP7h+53f181w/Au0019v2rPm3d/tOM55y1qOmf1/cI/dqS+8vdzpz/xam9gXhZ8a/H54r9ELbqz9ruq0trwgWkX'
        b'+z5SHkkJ6/q6O+0Xj+EX7eFC7i7bdREbPj7mtuTjzm2zllso3vAvHp7nXfOjVfCPNuKyhtG3rf4esHgL9/uPiWm9fbd8176pvH/z9E8tHUVdH9p/Mng6IHNR/PEH63/6'
        b'xxkrl62b3yrN2njn2KKvfb8VOP7gto3PWmB+NJBjv9R//d7RDdtitim2hdvdTKk/MjrLYt2iH3e6/uPNgqU7P82SfZrxofMnf/zy8HpFPePeqwvefv3ll+5cKzd7rXqT'
        b'+tjxYq91OQl/b3l3nv2sqFc/+fnDuZ7tZTs/D8teMLMhbPifLV8sv3iyv3//D0zhV5E7FQL+W2vvXgnmJ1xwHkhynpXyjl3JxlkXDlrd7Pjb0fPVNb/M/OLEqZUX9r37'
        b'WuIfPnR91wCeP9fb2DAg7C3+YGf9rqj24pdOz2X7nl/16mm3S7fDv2UIl3x329cr+rCBc/HdB+Wv5L2yv5MzIur7W9z3o68lXl9SuCK5MODDyOnvON30O8L84KLu0lC1'
        b'5fI3Llya/k7TittNST+Oued3hE/bkzWHs/Xe3FeVF91n/5L/6jcBYR+7nrbuha+ePL9k/7eLf3ej+rMHf1qlf7Az7oHn5qLfG8+YDz1fcf6dk39bMpj/l1/e4zDf7/rd'
        b'OzGL8+bYXMwpSfwhvdR7U2CDxPU7/fu8Fzo/iDz1ofXHLRYJH8QkvPf2qe6/LkosCr8iLo557+X5Mwd/mP3mKLCe/tXvvrv52YCrQ8Pfjpwd+Ge67WtfuNeR7Td6T2ef'
        b'WH3/n98k31mUYBOs/If8+sOCDo33bL+zztJlJjUOXn99/vjdVUsao3NkUvDtGzPSvWxNG6784chb8/1XStNipTLrdbPfTtjC1Lzy7h+cv3/5J923oXsqN4wsy/nkmlb0'
        b'XeNX03q0ppvkXZ8fao/JEvxS9z177Z8CNrV9AeyEJ4/ce6Hp4ZJrP2SZfbFj38blP7j+UfDnc7/f/h5v158FP/91zz9/WrrO9vOW+4qvLRo+WH//lrai/w/XG38q6Gm9'
        b'uOwVzScfBC/4Uvac/8C+hQ/+VpbMOHL8xG2eDR2/dCSpYjwkCulIpCXnwF05yPFyBVdYmTlw5wOscBJSQb9HKD9UyEOeNNLLixjglBDsouKyFA5pdFiWEO6rAtsfh2XB'
        b'66gxNraLcPgwPQToL3sUeOUCdlNxV1VAHTYLdE+MvWJskMGhB17UJuXmKnDDjQ4MmxQVdhqcoyDAUY9VcOvcyQFYdPRVGYvCHe53mFXpy8/PC8uGe/Erp9cY6zig6wE2'
        b'MC7L4fEc5I2GM0uQ+TBZxxDC40UU0lXrg3IQPnhSzvnUnGwjmJWF8CaFNLi4oZ52H+AgaH3kPnQkUJXIIWss4GNSIUO6HZHLBJxniCzTqMri+Yoae/6v39M7M4uKglPA'
        b'rWAXsoYtOcgTqxeEeiItT70RO53FXBXP4/7/Dhj7DycyzFBPP1alA1Ae/Sa9eLhanhAd0TDxhgpK8zKng9IkJoQT51Dy/mS9Y4DBMUCZbnR2Vc4yOnGUGUY3L2W20cVV'
        b'OdvI8RwjqhjWheQ39J82ltHRqy1RVa7O0DuGGhxDxwjSXmj0CFZN17D0HgKDh6At3ejqcWjj/o3tmzs2I3h3X3VqJ7/NFJViYC+jk6fR0RWPrBbRb+R+Q5Qy7AtJY1Do'
        b'mVXHV2kdtaX6oHhDUHx7QVtqm0IlHnX1VLP2b27bbPTgjhEMt0ijp1DnKdQotMsN4el6zwyDZ4bOM8Po6deT15WnCdR7RhioKLPR8GgjT2AMCTMG81HvxrAIoyDSKIzC'
        b'KT/cGCo0hgnH3Kx93ccIlKjYnewxT8LdRx3Q5aXyMgqiVGxVjZ4Tii6jm/d4qYe3OlA1XTXdmDb793zAv1OmTys0pBXqPZNVGepQvacAobVIH56MLjQ8KuPpPcPQhXsQ'
        b'6NzC0YWjpNiqqk7bTltUqvPL1rnhazQoUl2jDRxiDDGHmIOhQ+Lh1JtVd/yv1+mD8g1B+cYQgaZUy9CUn7c0BgjV2Wicudo12qLzDfqARENA4pgpC0+EhScyZkF4+qrz'
        b'dR5R6DJGJyA0hHrPSHThyDWJzisaXcaYRFQerveMQteTiLbYaaoMnR8qE6HrSfFj4L+P06LTa4zhwnU3evI00WNMlBv1DFCvUq/SOmvXDNlrZYPu+qDphqDpY2xUN2ZC'
        b'ePmr08dMcd6M8ApUl4+Z47wF4RWsYY1Z4rwN4RWK+rLFeTvCi69JH7PHeQfCK0TjNOaI806El0BTPuaM8y50P644z6Fh3HDene7TA+c9Ca8gtXzMC+e9aRx8cJ5LeAk1'
        b'8jFfnPejYfxxPoDOB+J8EBEYbAzmGUPDxvj4nniUqFhjQkxg++54OgCN5vwxgu0WZOTHaBK14qHUodKhmYOrhmPu2N+JuuN0e5o+Nl/PLzDwC+iAQWNAkCpDlTHKD9ea'
        b'nU96VBaoyjCGRWoDz+cOzbwblqxiqRbrOSFUXKQm2xAcpwueMZSqC04bttd7z1QxEVl9g9RizUx1tYEboc3RcZNVbKNPgLqou+GeT+Rdn0i9j8jgI8JSEzrqF6ghjwWr'
        b'ZuL4zDJ1ubr8pCWC9vZRMfEAM7tX3fOOuOsdofeOMnhHIVl1C0XzwHOYeTd2ti52tvFRB2NMAo3xf28wGiK4ZHnOUpsx5D+YPUzqQ9IMIWmd1ioTNdvIi9Z4aIuH5ut5'
        b'Mw28mWiiCzttjEKRNlVbqp15fhUqWKbn8EdjpyFKpg2lDVbfi826G5t1J0AfW2CILfiGSbpFq5yQfLqFamYaPbk630jMxhwvlcTAEdzjRN/lRGvn6TmJBk6ijromyHCg'
        b'xumuh0DnITD6RSFeR6hHZ5HGnELUa3QRDsv0n4fDMlGKwzLnkaPj3WpWGjiR2jADJ/keZ9ZdzqxhhZ6TZ+Dk6agLDyDUuUWga9TTuyerK0sXlDKM1FGmwTNTRY4GhqiL'
        b'NPaXXM+5au3Pup93P1ZyssQYwrtkes5US561OG9hpDSA79Xg/uAh375QSgcorkv0QXmGoLyn5TujK0mVhMNqM9QCOqx2NCoO3SB1E67zDKd0ywydG75GOZ4YuxCdWyi6'
        b'0N2ot1DnLUSzi0g0zkgbnq2bnosmH5GHJ++TjyePUryk+eSob1Bbdnv2qJv3GMHDehqp9y37t6hlele+wZWPeMvZV+t01avfa0ihj8wwRGZQRXec3vJ61Uu3YLE+a4kh'
        b'awlV9icO1+jqhcM0UTcUBrrwWXdc9eFz9N5zDd5zdZy5RvdQHbr4uXr3PIN7ns4pD4d+LtE5h6DL6BSkcwpSKzTLDcHT9U4zDE4zdE4zjE70G/SBeqcQg1OIzikE8UNb'
        b'htE3kMLbg6v2NnhE/Pao40BaB4NHNLZgvup5d115elceDoBO7krWiPQe4QaP8DHCyS1em341uz97SNZXMFgwXHo3erYuerYxIORM9vFsjexYwcmCewHT7gZMG0of9tcH'
        b'zDIEzLoXkHs3IPdOkT5griFgLpLxwFD1fE2kpuxRYPGQrz5wuiFw+hhh40UnanKMxfLNJY1RcUPkYMhQxrDvcOlLgTdzNYHqdHX6w/vBkYikCGBiagyN0wh08ZnoMoYk'
        b'DwfrQ7LQqibk4PVEKVpbfi7O83EDMhClTNzs4cOHSClHxmpLh0ht2aCFUZigqRkKHCaHGcOMmzy9MN0gTB9jM3l+YwRK1GwEHRCiiT2epE4yJs1Up+t4ifqAabqAacZA'
        b'nqb4+HL1cmRG1Okat2MFD7/xwlPi4gbWBv9YLFAJxth4NUu9TM8V4QhkLx3FrwbPcG203jOOvtNTl9ENab67bnydGx8HEy81cELvcSLvIiEM0HPiDJw4HScOZUanXtVR'
        b'/B0FhnWg0c5PZ+enjtF4G/zj9XYJBrsEnV2C0c7lkPV+a5VYbxdgsAvQ2QWMOrop82RWyE16x8txfiTrnUi/YkdTOkbYboSFj1X/hdjgf9mlww84V0zlwknxm3qTXLf9'
        b'GP44MR5EXMoiSQccIfzvTP5twcb420Y95jHEZZtUJnPSufGj+OLv8KOpQ4QYf9SMWMwoJxczyxlFhPkOHnPEjjqypsJ5pRlSaZ30Rx/6EJuihnQ8Oldczi2VcMW4XpjP'
        b'Y42YlZTgU/+SkhGLkhL6q2Mob1VSskZRWjteY1pSUl5XVlJCrScd/U0ROwET+6lh9yFkZfipT+Pjf6NWkbpHF9WeOgoAe3xhj6UNOL4OXpVbmqPdUr5AKqC/txMOe0zY'
        b'MtjHI2dVBzhWsGXbUK9vOVRvbs8qgBF2O7+KzzqQtq7qtcIr/R2bP/jhcuPQmg+VD5x2tMWnBM4JFGoKu+vTlZYLGnjJ+83Z2aHc/cnTvj8cJ/q+6I9/vrLScsnlmCVb'
        b'KmxPv+L053SvE6+79eo0z426gsOXCnrPzFn84t6FRwo3he7L7PyWf+xn50+qj/39h6TN0p1/9frdz2+cd41Zqf70QqvfL3N+ubPwbzd2O6W/YXv6g4+OHlYkLP0o6oD4'
        b'j70Ry3TPpZv8s/1vSVc/3HG/3q1jrttVlnv2rt4P55iU6wrtQjsvrn3TbtbH7f67OZF7WX3mb9wOKLwdvVh5ocr/iv/ML1OC+yzv3/Yub37hU//vyxpVkLvGDN62b3H4'
        b'fUR+93DA6YhWt9dX2ny3cNjvoLbF+fxK6y/C2xd8HWocDrqibT3i+o5zYfu2VbavqU6VHlp17wjrfsr2A3J3wSer3/rgwoMfazt8787WlMxfVXgor3/R6Qudy+y+DTyR'
        b'25X91Tubtqx7Xfam6MtDHBuLhq92vfYg3/mbjR2vvbS3c8P3Nq9Hrpd8u5THoraooAmcqId7ckkCno0h4wm4F96kd4te8Bw4T308CVyyzFMIJn49aQfvAV72UtgPNZah'
        b'+OQF7YzHYVbBXgbhAwZY8BI8hzba+KFzJWwD52TgQma+IOTRJtoe7EiAbUygjZzNc6M1gtlvJv+5fSXekXNTqF/jUz96Q4mEq7autLykpOFxjtpKCpjUR2Me0h+OCSOs'
        b'ncdYpuauRlsHpawtqnldyzqV7+5Nyk0qmUqmjlKXnozpbOhu0Mzt2qLaog1A/6RDvoOKobmD6/uEg8Lh9OH0Ow4vZd7OvBuVq4vKvc9xV0WpSrtjOs27zdXZeo5Q66rn'
        b'xOum5+td83WF83Tziw2FC+66LtC5LrjvwlU7tEs6JEiJI+eUs5BEHpKDU1tqh7MyTZn2cMyUNEcOnoNPm+CUlU4wS8+dbeDO1jtkGhwydVaZlP0zMQ8ZI34zsWOZIwP4'
        b'm4mVGdfCaGXb5jLGxDk3T1UFnQviaWLpnCh2yITOpcwcLqZyo1QLNs5RLagc1YLKUS2oHNUC55Djb22H2pjSeXcv1Go8HxyK2o3no+NQy/F8KplOotbUnRnd2pzOU63H'
        b'82FRQybDxUZ7V1WFJnaq7JgtBiQeJTozT7T3cuCgOvoaszTxQ1Uo0Zl5j9nlkub4jZv/j3+WMwgLO6O5ndK1TaaKaavRmfvpzf0MiNCM9Uxz5A3/p9JvmISFPxoH/7Vr'
        b'cRljUVVrTdHdGIM0xzuGp5IjG77Bfx7g5FG7ybCUa7E7NTnNkQCO7mkCJu1aOI0wkFX69zkWU8q50xTOxhOHA585PZFubPZk1x95GzyStMMewn9L8m/1Qk6aJxLXbVLN'
        b'mNUvXrcmZdtQ0csm361unWGzLYWTfivZzOjrzHl+2pqdrc5rD95t/1L7Qt+p49/sT1M6OJzuynr/tZvCo5KrL6z/2/dBv9/rvuqzLObb+d5Xvl/jl7QltOrS9q8T8mMP'
        b'5h78yeWtfSPGGRavv7bR08oqdQeHZ3OnPt0mY6tDMOfNoePXxW9eD8gMjzl13zXnoFf9jUqeKf1w+Ba4bE99prMAn9eDY/ByjilhCfoZUAMPwGP0I9jW9Zlz4ZWcAgHs'
        b'w5AFAgZhD28y8bdpCinrIoG7IsAesA+chI1wHz6ZB61gnylh48D0Xg47qFdkffwCc5hg75M3bMF1HvUBwKyl8FbO+Pc/Yd9SHDJgyWMge9UaTj1/BgcDYfejD4TCDrDn'
        b'8QdCrZlUz+A8GJrHz2YTZA44AxsJqGKU8PyfbdD+xx+jTika/o9M4NMGcEpjWC2pltPGkM5RxvA9YtwYIolxJ9iOjfn4n9Ha6Z61911r7yPr9dYhBuuQxllGlkVT7rZc'
        b'nb3vqXg9K8zACtOxwowsH93ky8iybszC/8ZMNrLZSH/8D6UNloSVU2PBhLcluSPMWrFkhIVfrBthyxX1teIRFo4gRTuk6jKU4pejRpgyuXSEvXKDXCwbYeH4+hFmtUQ+'
        b'wqa+OTfClpZKKlHrakm9Qj7CLKuSjjDrpOUjJhXVtXIxulldWj/CbKiuH2GXysqqq0eYVeL1CAR1b1Etq5bI5PiNmhGTesXK2uqyEdPSsjJxvVw2YkUNGEVH8I5Y0zuo'
        b'alldfGxE5IilrKq6Ql5C7RpGrBWSsqrSarSTKBGvLxsxLymRoZ1FPdonmCgkCpm4/IlCpp69r/jNH5dL69HcRwlWP7Jo8rGD9IwfYhZbkpQyse7735/+25Q3tpMvWZmn'
        b'+hEv+dmkRjB/NHv0odERu5KS8fy4sfrRvWLyx6e5kjo5F9eJy/N5ZtIkLLVo71daW4usLLVA03CRBeIhqVyGY6xHTGrrykprEfsUKiTy6tViagcorX3E8k82iz+aTad3'
        b'l0lSKUFvaGWbUTLGJElyjMEiWcgPRIkVYWndaDrGyjYhncaICeliK8Lc/p6Zx10zD1W23izYYBY8RjDIGF1Y0nDQcNBLIbdDdGHZ6DKa2RktXJRhOleR3iLaYBGtY0Ub'
        b'CTsdYdfG0RPuBsJd9+ii0Ps/iiKfRQ=='
    ))))
