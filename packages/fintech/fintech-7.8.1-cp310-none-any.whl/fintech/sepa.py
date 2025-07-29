
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
SEPA module of the Python Fintech package.

This module defines functions and classes to work with SEPA.
"""

__all__ = ['Account', 'Amount', 'SEPATransaction', 'SEPACreditTransfer', 'SEPADirectDebit', 'CAMTDocument', 'Mandate', 'MandateManager']

class Account:
    """Account class"""

    def __init__(self, iban, name, country=None, city=None, postcode=None, street=None):
        """
        Initializes the account instance.

        :param iban: Either the IBAN or a 2-tuple in the form of
            either (IBAN, BIC) or (ACCOUNT_NUMBER, BANK_CODE).
            The latter will be converted to the corresponding
            IBAN automatically. An IBAN is checked for validity.
        :param name: The name of the account holder.
        :param country: The country (ISO-3166 ALPHA 2) of the account
            holder (optional).
        :param city: The city of the account holder (optional).
        :param postcode: The postcode of the account holder (optional).
        :param street: The street of the account holder (optional).
        """
        ...

    @property
    def iban(self):
        """The IBAN of this account (read-only)."""
        ...

    @property
    def bic(self):
        """The BIC of this account (read-only)."""
        ...

    @property
    def name(self):
        """The name of the account holder (read-only)."""
        ...

    @property
    def country(self):
        """The country of the account holder (read-only)."""
        ...

    @property
    def city(self):
        """The city of the account holder (read-only)."""
        ...

    @property
    def postcode(self):
        """The postcode of the account holder (read-only)."""
        ...

    @property
    def street(self):
        """The street of the account holder (read-only)."""
        ...

    @property
    def address(self):
        """Tuple of unstructured address lines (read-only)."""
        ...

    def is_sepa(self):
        """
        Checks if this account seems to be valid
        within the Single Euro Payments Area.
        (added in v6.2.0)
        """
        ...

    def set_ultimate_name(self, name):
        """
        Sets the ultimate name used for SEPA transactions and by
        the :class:`MandateManager`.
        """
        ...

    @property
    def ultimate_name(self):
        """The ultimate name used for SEPA transactions."""
        ...

    def set_originator_id(self, cid=None, cuc=None):
        """
        Sets the originator id of the account holder (new in v6.1.1).

        :param cid: The SEPA creditor id. Required for direct debits
            and in some countries also for credit transfers.
        :param cuc: The CBI unique code (only required in Italy).
        """
        ...

    @property
    def cid(self):
        """The creditor id of the account holder (readonly)."""
        ...

    @property
    def cuc(self):
        """The CBI unique code (CUC) of the account holder (readonly)."""
        ...

    def set_mandate(self, mref, signed, recurrent=False):
        """
        Sets the SEPA mandate for this account.

        :param mref: The mandate reference.
        :param signed: The date of signature. Can be a date object
            or an ISO8601 formatted string.
        :param recurrent: Flag whether this is a recurrent mandate
            or not.
        :returns: A :class:`Mandate` object.
        """
        ...

    @property
    def mandate(self):
        """The assigned mandate (read-only)."""
        ...


class Amount:
    """
    The Amount class with an integrated currency converter.

    Arithmetic operations can be performed directly on this object.
    """

    default_currency = 'EUR'

    exchange_rates = {}

    implicit_conversion = False

    def __init__(self, value, currency=None):
        """
        Initializes the Amount instance.

        :param value: The amount value.
        :param currency: An ISO-4217 currency code. If not specified,
            it is set to the value of the class attribute
            :attr:`default_currency` which is initially set to EUR.
        """
        ...

    @property
    def value(self):
        """The amount value of type ``decimal.Decimal``."""
        ...

    @property
    def currency(self):
        """The ISO-4217 currency code."""
        ...

    @property
    def decimals(self):
        """The number of decimal places (at least 2). Use the built-in ``round`` to adjust the decimal places."""
        ...

    @classmethod
    def update_exchange_rates(cls):
        """
        Updates the exchange rates based on the data provided by the
        European Central Bank and stores it in the class attribute
        :attr:`exchange_rates`. Usually it is not required to call
        this method directly, since it is called automatically by the
        method :func:`convert`.

        :returns: A boolean flag whether updated exchange rates
            were available or not.
        """
        ...

    def convert(self, currency):
        """
        Converts the amount to another currency on the bases of the
        current exchange rates provided by the European Central Bank.
        The exchange rates are automatically updated once a day and
        cached in memory for further usage.

        :param currency: The ISO-4217 code of the target currency.
        :returns: An :class:`Amount` object in the requested currency.
        """
        ...


class SEPATransaction:
    """
    The SEPATransaction class

    This class cannot be instantiated directly. An instance is returned
    by the method :func:`add_transaction` of a SEPA document instance
    or by the iterator of a :class:`CAMTDocument` instance.

    If it is a batch of other transactions, the instance can be treated
    as an iterable over all underlying transactions.
    """

    @property
    def bank_reference(self):
        """The bank reference, used to uniquely identify a transaction."""
        ...

    @property
    def iban(self):
        """The IBAN of the remote account (IBAN)."""
        ...

    @property
    def bic(self):
        """The BIC of the remote account (BIC)."""
        ...

    @property
    def name(self):
        """The name of the remote account holder."""
        ...

    @property
    def country(self):
        """The country of the remote account holder."""
        ...

    @property
    def address(self):
        """A tuple subclass which holds the address of the remote account holder. The tuple values represent the unstructured address. Structured fields can be accessed by the attributes *country*, *city*, *postcode* and *street*."""
        ...

    @property
    def ultimate_name(self):
        """The ultimate name of the remote account (ABWA/ABWE)."""
        ...

    @property
    def originator_id(self):
        """The creditor or debtor id of the remote account (CRED/DEBT)."""
        ...

    @property
    def amount(self):
        """The transaction amount of type :class:`Amount`. Debits are always signed negative."""
        ...

    @property
    def purpose(self):
        """A tuple of the transaction purpose (SVWZ)."""
        ...

    @property
    def date(self):
        """The booking date or appointed due date."""
        ...

    @property
    def valuta(self):
        """The value date."""
        ...

    @property
    def msgid(self):
        """The message id of the physical PAIN file."""
        ...

    @property
    def kref(self):
        """The id of the logical PAIN file (KREF)."""
        ...

    @property
    def eref(self):
        """The end-to-end reference (EREF)."""
        ...

    @property
    def mref(self):
        """The mandate reference (MREF)."""
        ...

    @property
    def purpose_code(self):
        """The external purpose code (PURP)."""
        ...

    @property
    def cheque(self):
        """The cheque number."""
        ...

    @property
    def info(self):
        """The transaction information (BOOKINGTEXT)."""
        ...

    @property
    def classification(self):
        """The transaction classification. For German banks it is a tuple in the form of (SWIFTCODE, GVC, PRIMANOTA, TEXTKEY), for French banks a tuple in the form of (DOMAINCODE, FAMILYCODE, SUBFAMILYCODE, TRANSACTIONCODE), otherwise a plain string."""
        ...

    @property
    def return_info(self):
        """A tuple of return code and reason."""
        ...

    @property
    def status(self):
        """The transaction status. A value of INFO, PDNG or BOOK."""
        ...

    @property
    def reversal(self):
        """The reversal indicator."""
        ...

    @property
    def batch(self):
        """Flag which indicates a batch transaction."""
        ...

    @property
    def camt_reference(self):
        """The reference to a CAMT file."""
        ...

    def get_account(self):
        """Returns an :class:`Account` instance of the remote account."""
        ...


class SEPACreditTransfer:
    """SEPACreditTransfer class"""

    def __init__(self, account, type='NORM', cutoff=14, batch=True, cat_purpose=None, scheme=None, currency=None):
        """
        Initializes the SEPA credit transfer instance.

        Supported pain schemes:

        - pain.001.003.03 (DE)
        - pain.001.001.03
        - pain.001.001.09 (*since v7.6*)
        - pain.001.001.03.ch.02 (CH)
        - pain.001.001.09.ch.03 (CH, *since v7.6*)
        - CBIPaymentRequest.00.04.00 (IT)
        - CBIPaymentRequest.00.04.01 (IT)
        - CBICrossBorderPaymentRequestLogMsg.00.01.01 (IT, *since v7.6*)

        :param account: The local debtor account.
        :param type: The credit transfer priority type (*NORM*, *HIGH*,
            *URGP*, *INST* or *SDVA*). (new in v6.2.0: *INST*,
            new in v7.0.0: *URGP*, new in v7.6.0: *SDVA*)
        :param cutoff: The cut-off time of the debtor's bank.
        :param batch: Flag whether SEPA batch mode is enabled or not.
        :param cat_purpose: The SEPA category purpose code. This code
            is used for special treatments by the local bank and is
            not forwarded to the remote bank. See module attribute
            CATEGORY_PURPOSE_CODES for possible values.
        :param scheme: The PAIN scheme of the document. If not
            specified, the scheme is set to *pain.001.001.03* for
            SEPA payments and *pain.001.001.09* for payments in
            currencies other than EUR.
            In Switzerland it is set to *pain.001.001.03.ch.02*,
            in Italy to *CBIPaymentRequest.00.04.00*.
        :param currency: The ISO-4217 code of the currency to use.
            It must match with the currency of the local account.
            If not specified, it defaults to the currency of the
            country the local IBAN belongs to.
        """
        ...

    @property
    def type(self):
        """The credit transfer priority type (read-only)."""
        ...

    def add_transaction(self, account, amount, purpose, eref=None, ext_purpose=None, due_date=None, charges='SHAR'):
        """
        Adds a transaction to the SEPACreditTransfer document.
        If :attr:`scl_check` is set to ``True``, it is verified that
        the transaction can be routed to the target bank.

        :param account: The remote creditor account.
        :param amount: The transaction amount as floating point number
            or an instance of :class:`Amount`.
        :param purpose: The transaction purpose text. If the value matches
            a valid ISO creditor reference number (starting with "RF..."),
            it is added as a structured reference. For other structured
            references a tuple can be passed in the form of
            (REFERENCE_NUMBER, PURPOSE_TEXT).
        :param eref: The end-to-end reference (optional).
        :param ext_purpose: The SEPA external purpose code (optional).
            This code is forwarded to the remote bank and the account
            holder. See module attribute EXTERNAL_PURPOSE_CODES for
            possible values.
        :param due_date: The due date. If it is an integer or ``None``,
            the next possible date is calculated starting from today
            plus the given number of days (considering holidays and
            the given cut-off time). If it is a date object or an
            ISO8601 formatted string, this date is used without
            further validation.
        :param charges: Specifies which party will bear the charges
            associated with the processing of an international
            transaction. Not applicable for SEPA transactions.
            Can be a value of SHAR (SHA), DEBT (OUR) or CRED (BEN).
            *(new in v7.6)*

        :returns: A :class:`SEPATransaction` instance.
        """
        ...

    def render(self):
        """Renders the SEPACreditTransfer document and returns it as XML."""
        ...

    @property
    def scheme(self):
        """The document scheme version (read-only)."""
        ...

    @property
    def message_id(self):
        """The message id of this document (read-only)."""
        ...

    @property
    def account(self):
        """The local account (read-only)."""
        ...

    @property
    def cutoff(self):
        """The cut-off time of the local bank (read-only)."""
        ...

    @property
    def batch(self):
        """Flag if batch mode is enabled (read-only)."""
        ...

    @property
    def cat_purpose(self):
        """The category purpose (read-only)."""
        ...

    @property
    def currency(self):
        """The ISO-4217 currency code (read-only)."""
        ...

    @property
    def scl_check(self):
        """
        Flag whether remote accounts should be verified against
        the SEPA Clearing Directory or not. The initial value is
        set to ``True`` if the *kontocheck* library is available
        and the local account is originated in Germany, otherwise
        it is set to ``False``.
        """
        ...

    def new_batch(self, kref=None):
        """
        After calling this method additional transactions are added to a new
        batch (``PmtInf`` block). This could be useful if you want to divide
        transactions into different batches with unique KREF ids.

        :param kref: It is possible to set a custom KREF (``PmtInfId``) for
            the new batch (new in v7.2). Be aware that KREF ids should be
            unique over time and that all transactions must be grouped by
            particular SEPA specifications (date, sequence type, etc.) into
            separate batches. This is done automatically if you do not pass
            a custom KREF.
        """
        ...

    def send(self, ebics_client, use_ful=None):
        """
        Sends the SEPA document using the passed EBICS instance.

        :param ebics_client: The :class:`fintech.ebics.EbicsClient` instance.
        :param use_ful: Flag, whether to use the order type
            :func:`fintech.ebics.EbicsClient.FUL` for uploading the document
            or otherwise one of the suitable order types
            :func:`fintech.ebics.EbicsClient.CCT`,
            :func:`fintech.ebics.EbicsClient.CCU`,
            :func:`fintech.ebics.EbicsClient.CIP`,
            :func:`fintech.ebics.EbicsClient.AXZ`,
            :func:`fintech.ebics.EbicsClient.CDD`,
            :func:`fintech.ebics.EbicsClient.CDB`,
            :func:`fintech.ebics.EbicsClient.XE2`,
            :func:`fintech.ebics.EbicsClient.XE3` or
            :func:`fintech.ebics.EbicsClient.XE4`.
            If not specified, *use_ful* is set to ``True`` if the local
            account is originated in France, otherwise it is set to ``False``.
            With EBICS v3.0 the document is always uploaded via
            :func:`fintech.ebics.EbicsClient.BTU`.
        :returns: The EBICS order id.
        """
        ...


class SEPADirectDebit:
    """SEPADirectDebit class"""

    def __init__(self, account, type='CORE', cutoff=36, batch=True, cat_purpose=None, scheme=None, currency=None):
        """
        Initializes the SEPA direct debit instance.

        Supported pain schemes:

        - pain.008.003.02 (DE)
        - pain.008.001.02
        - pain.008.001.08 (*since v7.6*)
        - pain.008.001.02.ch.01 (CH)
        - CBISDDReqLogMsg.00.01.00 (IT)
        - CBISDDReqLogMsg.00.01.01 (IT)

        :param account: The local creditor account with an appointed
            creditor id.
        :param type: The direct debit type (*CORE* or *B2B*).
        :param cutoff: The cut-off time of the creditor's bank.
        :param batch: Flag if SEPA batch mode is enabled or not.
        :param cat_purpose: The SEPA category purpose code. This code
            is used for special treatments by the local bank and is
            not forwarded to the remote bank. See module attribute
            CATEGORY_PURPOSE_CODES for possible values.
        :param scheme: The PAIN scheme of the document. If not
            specified, the scheme is set to *pain.008.001.02*.
            In Switzerland it is set to *pain.008.001.02.ch.01*,
            in Italy to *CBISDDReqLogMsg.00.01.00*.
        :param currency: The ISO-4217 code of the currency to use.
            It must match with the currency of the local account.
            If not specified, it defaults to the currency of the
            country the local IBAN belongs to.
        """
        ...

    @property
    def type(self):
        """The direct debit type (read-only)."""
        ...

    def add_transaction(self, account, amount, purpose, eref=None, ext_purpose=None, due_date=None):
        """
        Adds a transaction to the SEPADirectDebit document.
        If :attr:`scl_check` is set to ``True``, it is verified that
        the transaction can be routed to the target bank.

        :param account: The remote debtor account with a valid mandate.
        :param amount: The transaction amount as floating point number
            or an instance of :class:`Amount`.
        :param purpose: The transaction purpose text. If the value matches
            a valid ISO creditor reference number (starting with "RF..."),
            it is added as a structured reference. For other structured
            references a tuple can be passed in the form of
            (REFERENCE_NUMBER, PURPOSE_TEXT).
        :param eref: The end-to-end reference (optional).
        :param ext_purpose: The SEPA external purpose code (optional).
            This code is forwarded to the remote bank and the account
            holder. See module attribute EXTERNAL_PURPOSE_CODES for
            possible values.
        :param due_date: The due date. If it is an integer or ``None``,
            the next possible date is calculated starting from today
            plus the given number of days (considering holidays, the
            lead time and the given cut-off time). If it is a date object
            or an ISO8601 formatted string, this date is used without
            further validation.

        :returns: A :class:`SEPATransaction` instance.
        """
        ...

    def render(self):
        """Renders the SEPADirectDebit document and returns it as XML."""
        ...

    @property
    def scheme(self):
        """The document scheme version (read-only)."""
        ...

    @property
    def message_id(self):
        """The message id of this document (read-only)."""
        ...

    @property
    def account(self):
        """The local account (read-only)."""
        ...

    @property
    def cutoff(self):
        """The cut-off time of the local bank (read-only)."""
        ...

    @property
    def batch(self):
        """Flag if batch mode is enabled (read-only)."""
        ...

    @property
    def cat_purpose(self):
        """The category purpose (read-only)."""
        ...

    @property
    def currency(self):
        """The ISO-4217 currency code (read-only)."""
        ...

    @property
    def scl_check(self):
        """
        Flag whether remote accounts should be verified against
        the SEPA Clearing Directory or not. The initial value is
        set to ``True`` if the *kontocheck* library is available
        and the local account is originated in Germany, otherwise
        it is set to ``False``.
        """
        ...

    def new_batch(self, kref=None):
        """
        After calling this method additional transactions are added to a new
        batch (``PmtInf`` block). This could be useful if you want to divide
        transactions into different batches with unique KREF ids.

        :param kref: It is possible to set a custom KREF (``PmtInfId``) for
            the new batch (new in v7.2). Be aware that KREF ids should be
            unique over time and that all transactions must be grouped by
            particular SEPA specifications (date, sequence type, etc.) into
            separate batches. This is done automatically if you do not pass
            a custom KREF.
        """
        ...

    def send(self, ebics_client, use_ful=None):
        """
        Sends the SEPA document using the passed EBICS instance.

        :param ebics_client: The :class:`fintech.ebics.EbicsClient` instance.
        :param use_ful: Flag, whether to use the order type
            :func:`fintech.ebics.EbicsClient.FUL` for uploading the document
            or otherwise one of the suitable order types
            :func:`fintech.ebics.EbicsClient.CCT`,
            :func:`fintech.ebics.EbicsClient.CCU`,
            :func:`fintech.ebics.EbicsClient.CIP`,
            :func:`fintech.ebics.EbicsClient.AXZ`,
            :func:`fintech.ebics.EbicsClient.CDD`,
            :func:`fintech.ebics.EbicsClient.CDB`,
            :func:`fintech.ebics.EbicsClient.XE2`,
            :func:`fintech.ebics.EbicsClient.XE3` or
            :func:`fintech.ebics.EbicsClient.XE4`.
            If not specified, *use_ful* is set to ``True`` if the local
            account is originated in France, otherwise it is set to ``False``.
            With EBICS v3.0 the document is always uploaded via
            :func:`fintech.ebics.EbicsClient.BTU`.
        :returns: The EBICS order id.
        """
        ...


class CAMTDocument:
    """
    The CAMTDocument class is used to parse CAMT52, CAMT53 or CAMT54
    documents. An instance can be treated as an iterable over its
    transactions, each represented as an instance of type
    :class:`SEPATransaction`.

    Note: If orders were submitted in batch mode, there are three
    methods to resolve the underlying transactions. Either (A) directly
    within the CAMT52/CAMT53 document, (B) within a separate CAMT54
    document or (C) by a reference to the originally transfered PAIN
    message. The applied method depends on the bank (method B is most
    commonly used).
    """

    def __init__(self, xml, camt54=None):
        """
        Initializes the CAMTDocument instance.

        :param xml: The XML string of a CAMT document to be parsed
            (either CAMT52, CAMT53 or CAMT54).
        :param camt54: In case `xml` is a CAMT52 or CAMT53 document, an
            additional CAMT54 document or a sequence of such documents
            can be passed which are automatically merged with the
            corresponding batch transactions.
        """
        ...

    @property
    def type(self):
        """The CAMT type, eg. *camt.053.001.02* (read-only)."""
        ...

    @property
    def message_id(self):
        """The message id (read-only)."""
        ...

    @property
    def created(self):
        """The date of creation (read-only)."""
        ...

    @property
    def reference_id(self):
        """A unique reference number (read-only)."""
        ...

    @property
    def sequence_id(self):
        """The statement sequence number (read-only)."""
        ...

    @property
    def info(self):
        """Some info text about the document (read-only)."""
        ...

    @property
    def iban(self):
        """The local IBAN (read-only)."""
        ...

    @property
    def bic(self):
        """The local BIC (read-only)."""
        ...

    @property
    def name(self):
        """The name of the account holder (read-only)."""
        ...

    @property
    def currency(self):
        """The currency of the account (read-only)."""
        ...

    @property
    def date_from(self):
        """The start date (read-only)."""
        ...

    @property
    def date_to(self):
        """The end date (read-only)."""
        ...

    @property
    def balance_open(self):
        """The opening balance of type :class:`Amount` (read-only)."""
        ...

    @property
    def balance_close(self):
        """The closing balance of type :class:`Amount` (read-only)."""
        ...


class Mandate:
    """SEPA mandate class."""

    def __init__(self, path):
        """
        Initializes the SEPA mandate instance.

        :param path: The path to a SEPA PDF file.
        """
        ...

    @property
    def mref(self):
        """The mandate reference (read-only)."""
        ...

    @property
    def signed(self):
        """The date of signature (read-only)."""
        ...

    @property
    def b2b(self):
        """Flag if it is a B2B mandate (read-only)."""
        ...

    @property
    def cid(self):
        """The creditor id (read-only)."""
        ...

    @property
    def created(self):
        """The creation date (read-only)."""
        ...

    @property
    def modified(self):
        """The last modification date (read-only)."""
        ...

    @property
    def executed(self):
        """The last execution date (read-only)."""
        ...

    @property
    def closed(self):
        """Flag if the mandate is closed (read-only)."""
        ...

    @property
    def debtor(self):
        """The debtor account (read-only)."""
        ...

    @property
    def creditor(self):
        """The creditor account (read-only)."""
        ...

    @property
    def pdf_path(self):
        """The path to the PDF file (read-only)."""
        ...

    @property
    def recurrent(self):
        """Flag whether this mandate is recurrent or not."""
        ...

    def is_valid(self):
        """Checks if this SEPA mandate is still valid."""
        ...


class MandateManager:
    """
    A MandateManager manages all SEPA mandates that are required
    for SEPA direct debit transactions.

    It stores all mandates as PDF files in a given directory.

    .. warning::

        The MandateManager is still BETA. Don't use for production!
    """

    def __init__(self, path, account):
        """
        Initializes the mandate manager instance.

        :param path: The path to a directory where all mandates
            are stored. If it does not exist it will be created.
        :param account: The creditor account with the full address
            and an appointed creditor id.
        """
        ...

    @property
    def path(self):
        """The path where all mandates are stored (read-only)."""
        ...

    @property
    def account(self):
        """The creditor account (read-only)."""
        ...

    @property
    def scl_check(self):
        """
        Flag whether remote accounts should be verified against
        the SEPA Clearing Directory or not. The initial value is
        set to ``True`` if the *kontocheck* library is available
        and the local account is originated in Germany, otherwise
        it is set to ``False``.
        """
        ...

    def get_mandate(self, mref):
        """
        Get a stored SEPA mandate.

        :param mref: The mandate reference.
        :returns: A :class:`Mandate` object.
        """
        ...

    def get_account(self, mref):
        """
        Get the debtor account of a SEPA mandate.

        :param mref: The mandate reference.
        :returns: A :class:`Account` object.
        """
        ...

    def get_pdf(self, mref, save_as=None):
        """
        Get the PDF document of a SEPA mandate.

        All SEPA meta data is removed from the PDF.

        :param mref: The mandate reference.
        :param save_as: If given, it must be the destination path
            where the PDF file is saved.
        :returns: The raw PDF data.
        """
        ...

    def add_mandate(self, account, mref=None, signature=None, recurrent=True, b2b=False, lang=None):
        """
        Adds a new SEPA mandate and creates the corresponding PDF file.
        If :attr:`scl_check` is set to ``True``, it is verified that
        a direct debit transaction can be routed to the target bank.

        :param account: The debtor account with the full address.
        :param mref: The mandate reference. If not specified, a new
            reference number will be created.
        :param signature: The signature which must be the full name
            of the account holder. If given, the mandate is marked
            as signed. Otherwise the method :func:`sign_mandate`
            must be called before the mandate can be used for a
            direct debit.
        :param recurrent: Flag if it is a recurrent mandate or not.
        :param b2b: Flag if it is a B2B mandate or not.
        :param lang: ISO 639-1 language code of the mandate to create.
            Defaults to the language of the account holder's country.
        :returns: The created or passed mandate reference.
        """
        ...

    def sign_mandate(self, document, mref=None, signed=None):
        """
        Updates a SEPA mandate with a signed document.

        :param document: The path to the signed document, which can
            be an image or PDF file.
        :param mref: The mandate reference. If not specified and
            *document* points to an image, the image is scanned for
            a Code39 barcode which represents the mandate reference.
        :param signed: The date of signature. If not specified, the
            current date is used.
        :returns: The mandate reference.
        """
        ...

    def update_mandate(self, mref, executed=None, closed=None):
        """
        Updates the SEPA meta data of a mandate.

        :param mref: The mandate reference.
        :param executed: The last execution date. Can be a date
            object or an ISO8601 formatted string.
        :param closed: Flag if this mandate is closed.
        """
        ...

    def archive_mandates(self, zipfile):
        """
        Archives all closed SEPA mandates.

        Currently not implemented!

        :param zipfile: The path to a zip file.
        """
        ...



from typing import TYPE_CHECKING
if not TYPE_CHECKING:
    import marshal, zlib, base64
    exec(marshal.loads(zlib.decompress(base64.b64decode(
        b'eJy0vQd8U9f1OP6GJMuyPLCNMVtsy5Zks8GMYMzwtvEAYgiS7CfbAtkyGqwYAtgggzEmzIQRRlgOI4AJEGZyb5umaZqkIx1qv23SmaQZbb9tvwlNw//c+55kyZYNpL8/'
        b'fHz17nv33XPHuWfdc8/7PdPlHw9/s+DPOR0SgSlnqplyVmAFrokp5yz8MZnAH2cdsYLMIm9kVjHOfks4i0KQN7KbWUuYhWtkWUZQlDDhTdqw+8tVJXOLMjS1dsFts2js'
        b'VRpXjUVTtNZVY6/TzLPWuSyVNZp6c+UKc7XFoFKV1lidvrKCpcpaZ3Fqqtx1lS6rvc6pMdcJmkqb2emEuy67ZrXdsUKz2uqq0RAQBlXlmIA+JMNfEvxFkH5shsTDeFgP'
        b'5+E9Mo/co/CEeZSecI/KE+FReyI9UZ5oT4ynjyfWE+eJ9/T1JHj6eRI9/T0DPAM9gzyDPUM8Qz0azzDPcM8Iz0jPKM9oz5iqJDoiyvVJzbJGZr12XXhDUiOziGnQNjIs'
        b'syFpg7Yk4Ho1E16l5QsqA4eZhb9x8BdHmiijQ13CaKMLbEq4ds/mGRkzxcExJluizsC4R8DNwphq3IK3FeYtwM24tVCLW7PLivSKdLyPGTNXhu/NRme0vHsIlMSH8XZ0'
        b'ODdbh4+i89l6vA3vyJczUXg7XxCJtrr7QZEG1IiPQYlsOX4ObWJkMhYdXY5u0NdT0Cv4Rgp9Kz8bt2qzZei5OiYW7+HRzUnjtZx7EBRCz6ELS3LHjYcCuXhnYbZ82Uwm'
        b'ehg/DR1Abe6BpBHHKuLI8+x8+hhdTIcWXOTH4p0TpSqwB99EdwyznaQIAMM7WEaVzaFLo9CrtMd1NnQ8Al+Jxq840TZ8vR5fXYlaoiPxKXSPYQaNkIVNTNey7r5QcoO1'
        b'CLfk5eAdfN9whsd3WXRoXiQ8I0iBn1PNykUXkmAgtufiHWhbIWkQak0t0GsVScOY+XPDGsrQPSjdn/TrxhC8FXcIw6FBeYVyRt7A4pPoOtoEz8nAPYkPLqlFe1Jy9Lp8'
        b'vYFl1H151Xh0B54OJrBeQk08vP9sSpYuGW/LI12KwLs4fFGHTleyXZbZeN/8P0dQNBhBmf8WRT1JHq0n2ZPi0Xn0HoMn1ZPmGesZVzVeQly2ORwQlwPEZSnichRZ2Q1c'
        b'ScD1arKMuyAuafjAboi7TETcobVhjJphYtISfsCXueIYejNmBMFmhkkbbXfmz39avHl3hpKJgXtpCz+YvDJ8iXjzbzFyBn41aQtXJZyfsYJpZ2wquH10ZqLsH7HMrL+O'
        b'r5n5d+7a2H6TL7K2cIKpDc+zO5It0cws07hfO95yWhh6Oyzlf6N3peiHckUfsN8sfietmfEybgOZni0z8BlYRC2pC5KS8PbULH0fRNZKe2lSTj5u0xmy9Tn5LFMXHT6j'
        b'DF9yzyb4cDN9odPlWLXS7cTX8SV8FV/B1/Bl/AruiFaqVVHhkRGoDTWjHePSKgonjJs0duJ4wJZLMgbdXRKOL6zF+905UA2sniG5eTkF2fm5uA3W7w68HXB+G26FtiTp'
        b'kg1afQp6GZ1F54vh7SuoDZbwAfws3od34f14D967iGH6pUXG4q3FQVhEhjUM/ghmOqf4CB1fxUuzzDXDXK7nYZY5Oss8nVluA18ScA2zXB2KPMm6zbKswEGm37ri1A3G'
        b'ORWu3ppRkWte+tp7r1/adXn/MPmbL5kXv3Yj5s0lP3n/tau7ju8/3mhlnWGVkXj2aV3Crqw0vlrB5NRFDhIatHJXIrwfjk6pcUsdaoHhaIPVy8imsuhyjcM1AB7Oxyfw'
        b'cykG3DwGwVDpWEaBdnJ63IQuuBLgcRa6lZ2iT5o0NEvPwaOD8OgMvkEfDUV36lP0uHVsRt5YOaMoZ/EFdGOai1CKqdPX45YsdAHunGEYbj07Lx09q2W9XJJWyztITwMS'
        b'DpL7fadXOezrLHWaKpFjGZyWevNML++2CuS5UwGJKjOWjWUdCt9LWpk3vM5ca3ECd7N4ZWZHtdMbZjQ63HVGozfCaKy0Wcx17nqjUct1goNrsggcZEIdcpKQ+uYQGPFk'
        b'Gd1VcByrYEkqYxXfkNRNeouP4A50NwW35rEMh57DF4ezmSXT51VyIRCFzmc6QRSOooqsSuZHFf7boQrBCFU3VIkrcMdRcnmuzpkHncHtDDpvQmdkY9ykM/hQ9IBcuM9q'
        b'GUD0k9iDro6gL0C5mbgDCC8rZ2p16BV0VCG+cAVtnYNbyIO5DN40HO+z9KcPIvFN3BgB/I3tw+DL6Bq6ZXDTB2hXTGQKub+AQW1L8CF8EL/sjoUHmlHodIpBwbBLmKzl'
        b'+EwuuiiWv4GfX4P3LIDLdcwktD1fDrySgj4+EJ3Ce2AydAx68WkdegE1acPFR9dQy7xpHKEsDLCoRrwleimdE3Qe3UN3nyZPTjF460B8Ct/CLfTRCLwN6MUtqA4fYIqB'
        b'kBwAenCUsjF8NmUJpk+uM/gVdBpfH4zP0mFBW1cPRLd4MtkMi3bhI2H5tAFrjegopvfvMOnoBXwHX10uNuDeAtSIbkUTRgwcsQUfQy/jXWJHT6B7eCN+kSMCUt2MCHwb'
        b'XXX3IQ/a8M3SEqhsDOnPmPT+InqdRHvRRbwH0CeNQWdQRxq+i14U27sRHR8B5OlAGHmZeeJJ40h0xU0WNumWC3c4cQc+lL4K8BKfZUfiLVZKP4JIGBdIaciyr2YamKeA'
        b'QTWwzSBfOrgG9lluJbCl8Cq6tGjSznk5Q5qXrWxnO1cqXTNe1XSb1emqtNfWz1xMqiRPEhn3DPiZhTfjk7mSwEIFgCy8F3XMNAEh3lZYgHdo0TV+3DjUkot2Q9sj8HkG'
        b'3cY3I9ClQeiGtd/IbNa5Haq59B3zxNZpUSgtZs7q7yl+FzNz8rHTHyS8mlH+0bzmhOELpvbNsn0+y/zb+EFzJv/vPyZUfnTneFxyxvx3+/956aUK03+iGhN3C/3N6351'
        b'4G3Lz/rY1Kufb77y1bivn7zXsnvXqX0l679zjN8eN/HElJ83vvqHG1faVx75OvedtyKvv/vWe29l/uD+Fx1zfrSn/itmmTNpiqwMqCih/GPxnVUp+LmnDFq8XccALTzP'
        b'jccnl7qokNWEb60EaQU3Z+cVyNFefJGJQJc5fGQkbqQvo61Q5C5u6Z+pA1lOr2AUy7gRjNM1FJ6ZZk2j3BJvB+EM0PZ8jpyJm4Bbcni8uwS/6KIC0wF8cSamBHzJQD8J'
        b'R/uzupFTrawrfe0ydRGWukq7YDESAktJ63CCG1kyVgn/gfR9o+RlrAqu1azyQQwfBb+JkHPEBJBd1ulV1dmNTtAUaixOBxEHHIQ6dW8N5yDEwNHHT21JNdk+ahv7aghq'
        b'S6Rj1Vp97hOTgpBIxgzAu2WrodeXH0J0KXcOIrqPxp9Dqg/d+XO4KIX1jY4douKyyAROLx6wSJStvifLMvyG07CMyZSTONfMzKN3nx3UZ7SMm8Uw9Sab2jBKLDo0LGLD'
        b'VzwoUDEm3Zn1axlKgTLRybnj02RMA1AgtIepmIUbrb/+6Sbe+SQ8jN8x8S+mT0w1VXnmt6uS/vTxxkvPX3ly+5fFzzX2T09MSNMJHwkfmXS7J0UorvSflthvXEJuplC8'
        b'uDix/PmRGbqt8Qtjcg8TaeFVhcAtmVQCcsIAJnZk37Q2s5ajXBt3GIcCr6ecPsJFeH023u4iYiiHjtanGLJ1yVoDCHB4GyDkzhmJGtmyQUO17KOhXZ/KGkvlCmOlwyJY'
        b'XXaHUeLrUYRwlBPki4K5TwRkc8QFIBpfaRW8YZV2d53LsbZ3PCP45OjrxzNSyxI/np0JgWc60uUbsOReBizLAu0I7Sw0zEcbQUjdBn1MRbDYgNnPQIcU+LQLbe6mWfix'
        b'jsqELOBdp0zIUpx7uOTfDedI45XdcG6OiHPfTIxlRsLvX4esH2TNFyT0ylDGMBqGmfLaE0/bbkUbmVLKgKPxHbRvPH6W0OexQL22CrTwoWoZlf6LMky6+/VDGHc0AWaJ'
        b'Go/bnpQRbXlczQBa8ONkjiL/X9nVeWerpjG00jITfnF8Bb7HEb1qPMgBl2jZYemRQP6ZpDTjM3nL5ySJZReGoc3j0R4gdswEZgI6iC6J/G8Haowen4Euw3BOhP+JtIYv'
        b'ouKJMUFTP6B+6ZOO4WIN6FVglnfHV6fDoExiJq1GJ2nZ+TGDGBjypI2jVjd89aSdEYWE7XgP2jIeuOYVmJvJzOTl+DYtPWHaMGJqmbJx1obpfzSHizUPRVeM49EF1ARz'
        b'OIWZsgh7aNly7UgGVrTmtdr64SvlLnFNRgMD7kAdlXgfZKYyU3PQCVp4wJokpgjY9ax+1bOPjlWKhaF3F4GXd7jwNhi8dCa9RBzNsbF6BmYiaZdpw/A71lFiK+bh04IT'
        b'XUTXoOhsZja6oxJH6N5qdMxZQ9ZAJpMZje7Ru0l4xxQnahqnINLqHHxsqSgc3MKH0T4nzEQLjOdcZi7M+imxloP4TINzBt4DgzePmZfD0LvL4+c7QeE5CmM0n5mPbo+m'
        b'd41lnBPtngmDkcVkgcp0mjYPHy4cgzsyxlCKnQ1s/bZ4+7wGncEdFjO0OofJwY08rWM9uxgKs9DoXCYXxJVbtH0gOG3Xg+Tsweeg4XlMHrqED9MRqY4WtdgYzRpdTeZA'
        b'aRbbJ6Am3LEYPwe9yWfyMYhTtPSDMSoGCihNZkdeWpleLI1uootPgvCzEV+BThYwBbn4Oi39dfYYgMXEaNLXVYyC1SEKvVcrMqDw+TjoeyFTiPfiyyKCrElhSqHqWYue'
        b'5t6bO1acmkjcuB4KX1oHY1LEFLnxTlq2ZH1/kM9gzgvN08/OKBbHdHQ2vh2BX7HC5QJmAT63nhbdUxROde/6QrfuJ30kjM5yoe0Rafg4DF0xiKXP43207J8HRDEgRyTG'
        b'6Ey6MUK1uCjN6Hh8xKonYEBLmBJbEQVlWIHORaA7qB0Gs5Qpjcymr/8pYQAsMUYZM3v99PeGTGDchMmircvRzgilAANZxpTpF9KS25VDmekASDNr/dKfPDNJbH/+4qgI'
        b'tNsNQ7iQWQhC2TVa9PzsEVQtMqlrOI5npfnZhVrxqxGgLr8Eo7iIWYSvTqGlXytNAMGdiTkmcw3yxk8Qe6AePzNiBj4BQ7iYWbxwFC0YHZbKLIUWHNM9zZXy8dLUXMfN'
        b'A0E/vYafh9yTzJMTltPC19MnMjWwHj+Y+0zxnZm1IuOM0I8HogggM+rGfWGfJt7UrB7LmGAt76pdU6FaugAYAu1aWd1a1DIDXYXxLmfKc/Er4iI9khkF0NrwQY4wiSWg'
        b'49q+fPDgQbRTtIyYVOvVv0idKNb8Uf0kxka49Oja4t/Z7Iz1/hfnGOcwGNbX9JEz3vt+Dp8Rv+XDp8+V5x9u9Z4+MvGdjnmtHX0a+H7DP/pcF7/ojY1J75/TXJ02bEm/'
        b'bbtW/5VtSCv8+ewBMz9K3qAqqIi9oP3HjxaOS1u0O0n2r/+Z8+Ndp6f/OeZkdWTtW56ZSu97yxa5NJkdH5186tLVgTOu9lt/dSg/wZOR3mQeUNH0p/UDv1r10+uVdwf/'
        b'32dN9jE/2f9F3lfrvD8ff/eFuZveMb9gMD1rMD9/0bTvovlInWlPXcbHk1bV9Lnliv731SZ+XfOIdTv23LwWf2YK/uqA1ap78zv3F54fcG/W1KeOnT7gOHBv4q8/vrzt'
        b'wvikpuKvVh3Mwum/Kl3aVLx78dGZR9JXTrr/INf+O02ffnM+fuGPWTc+f/eVk/8uNgzImrjmP2XZ9wY+883wX/77iUPqig0TUkByJtLxijFK3KIDLa69gFjr2nQsSMfn'
        b'OHwR310iSse70D68xyd6oINyfILTW0uofUIzLa/SDuoEaN75+hxdtpyJxTd47Fk3gto2QExJBLl4R242ugBC+ZR4vInrvwi/4hpG0QodByUYA328kFWgTyLWVtzGM33w'
        b'Lh5dQneLtfKQUosslIgRIMtESbKMu9JIRGkqyFwl+C7I2BhORuVoGcs9eKQ/jvsm9J8sOM9z/3mkPxn3deefDP6UX8sUHJXh47koXsnGgCAEcGXqb8ivI8HXNy0P4pa7'
        b'sjcpi3X08w0CfY8sQ9Fs8kIIAWs0mdq2aLw/QL7Kh4SaqhktkO32Wjnak4ReeIhoRUy2TIBoxT6SaPWI5rYwUbQqGqAGEebNOqbIZEsZXS2JVm+aI4DtvDmFizHlzeB4'
        b'ie3sDcO78A4FEdSplI7Pj7Z+JL/KODPh6YGtP/6Lqfy1S7uO72lvPN7Ibm9/fuyWsYeON4/Zok18M9dcYK6x7JZdTix+LkO3cmv51qg3BiiOpe+3HRvwjpr54d8i9/4l'
        b'TMtS3B6Md+N2/6rYbCMSOTDSDp/I3QuGDhAx1OlyuCtdbpC5jQ5LlcUBqp+IrWoyHs8oObVP6E4MwAKZEwr3jgb9/WhAXiSbP06CD8ymmAchEIGY4NHL6Fm0048JqQZt'
        b'cr5Bq0+y5uSjbak5+bn6HFD3CuQMFNuuwpuexvsfihXBAve3xApf5cFYoSgQxasr6LYhwsEvG0LkHgY9j5vRPYoZb7Aia2IqzMWXhWhmnrXxXH+ZczI86r/ywl9MSykG'
        b'XG5cyVaqfj/7jeHf6LKjTke9UfVG/Gnb/uGvx//JtDVKEfPEc5vGD2YivopQ5t0GLYwM63DArYudtBDEw4ucHrfjgy6y91EE/HkrqGIOtDFAGyOqGL6wVprAntEisYsS'
        b'FowUKhEpwhNYQsIcAwJRovKhKDHQjxLkxW0BKPFlCJQYC09sQOYDSEOn3hWIDmtRuwkdCcfNpbjpoXo/38XY+mh6f00oQtEdJcIKSunMTx1JhTUlN8OUt332ZFFK2JJO'
        b'1SrlHzNM6kWJbvFmroXuySj/JTPpJk+NZqxfvHFd7gTBlPk0dtrvQVn/1PRmRU3VectHprPm5LFJlbrdn5sWv3Zj17At2kPsm1U55v2mjwTuxzrNzDFFZWkxq9POpE0e'
        b'v328a1z8OEcVw0x/O/r5sW9I2vtMlwWdy8vXcRx+iZHlsugK3hlFDUzIg27glwgL3plamI9bC7LReRnTr1g2C+2ZxJc9qgYfWWdZ4zIKbotRMLtEjImnGMNFq9h4yXwk'
        b'49QPuPuOQX7ckXllpLg33GYxC/Dm2oeYiwiSO4b4cYlU1NaJS7F/D4FLhNWjc0kFuIXsQKJthdp81FpItl2ZUbCAD/eTl0+pr+QDJlgeiDszRdyR0b1BuUdRpZDwh6fG'
        b'ehngD0/xR0Zxht8gKwm47kmHV3TDH7nIaJJVoviaFn7J1couEzHljFrUytMUCzOfSx/HWOO+mSF3muFJ9p+2DN5xOXJjmlr22+vHVxWnZXg/nZPbf8GsfqeunptQ1XJJ'
        b'm/D+x/884yxfYy7SqXa/+PPXd87bEz1p0soFhjVzVm5768jTZX//9Zri8GdGFl62OP5qX/OvB4cWXDpp/d6qDbo9ib/aZQYhjUxjfuxgRxq1Q4YxHDrBluHjwyleDc7G'
        b'7XQPm+xf44PloNGdj6FWIbQLbzHkwqKdvwxebC1kGSXewaEm1Gam/AvfwS+uhyfNqUDKZPksugqK4L2EGrp7NBJdLEGX1+KWfHSeGJia2PnoWlFvApmix0ddMVVdbemC'
        b'qANE0tZfCQgaBYiqAp7HcUoulgMJSeEY6kdXOUFXwFGCgV5FpdtlrwqkeyHXCKAxQUGHJhh1SaXPd6Juwkc9oC5uLkJ3cwv1QYg7FJ0oRi/J8KF+uKNnPki8R/wb2kyV'
        b'/DF5YTfEjYS/vt0Qd6iIuMKQHzB7WaboQoIpe2ndfBFx/zqBWleSdm8wNaw1Fok3r6ip6lt/STDp5KqB4s3fPE01eI0s3qS+ph0u3oyrjiMGraK3lKaGyPgM6fVB1L5T'
        b'NLbM1HA8kpdKmii/LZLNNTnY6pHiTbmK2hDq+4DenNR3jXhz/QgtscvU/I/NNFsRzok3T8Y9wTSAnDouzVScNmWqpDTOn8GsAaW8cpHJ8Z7KId5UlaYzLlB7f5Ngcjw1'
        b'Wbq5a1Ei0fvrb9WZGrgYhXjzk3wdsekwu580Df9d8TzxpjK3DzHGzTq4waSeHVcg3ny/chazEdj0T1aaHEUxZeLNRQ1U2yyaUmjSjU2XxvO9dCKGMllflJpsmX2rxZtf'
        b'K6l+r/l+jGnphoGp4s1n500memnNzFGmcWNTasSbf5+1gDkGdb7mMi1/2ThdvDlmkIV5E0pOm2OaN2edxLBej69i3gaFuSnVVBU3UfIXQDOoFj9r53BTw8E6taRvZ0VT'
        b'48T70022NyoixZu/XfM08w8YkP8ZbFpVslCauKrMcYS0Fb2rNsVGDZ0g+SDMHk7sCBqj2sT1f3ooY7108LyoPw99N63s2fy6xrSYLd/7xdeJh2OLVd/5bMG6lqXmk7rh'
        b'7oyTF99ImfS5Hr2+buNvTlT+POPjN775ze3n/xb35dvn5jZoX779ZdMv13z4fp+CD/qqIqLSMrPf49/qU/TkB+PbbpqS9XkfyBY+ePrGG0sWRH8wcvnuGbtMZ6ouZJkr'
        b'NxXGvTvatec7R/74VZ+lOwtPzjt2+NXX9pe031uk/X3kZzGrDvyiOOOPrp/3Pbf93xOtvzb+tOGfw+6olm+ee/P+i819s9PPvjl4VctJb+75hNfDP3nzf9DUF59RbjhZ'
        b'rZv8yU/ezv2oZUK8wzahriPurQk/+nBs/i9++MOxuZ83/XvOLc/Pl02u+L+G+vxP1vz+061vRy785p1+Ux/senXMhvPGe+2vho87F/Pa3gsxn/910W+/mrlp5gPOvmv5'
        b'v/7wWy3vIjRlJj6BD9bjIyE4+CR0Fx+nxDZiYm2uLikLt6EdIDgBKQYNe+0yvIUq2PgUvjExBe+MRK2pySwjc7N4Gzo2Shv5EJL68KQXgh1o/CcEucJct8JYY7dZCYGl'
        b'VHmxSJWnKkErVfIjqRARw2rojlMMFShiWTWnkqlAsFD5/vNdfumV7M/qQWp4T/1ABVRdCTq4Y7ifpoP4utZidgSQ8V64DOsY4afgpIqLnRQ8/ichKLieDO8Lw+aJBDwH'
        b'78AtMAPb0U7qgdKGt+XBXOkUzAx8WYFvxKHd3ZQPmfTrXA6JhfgBMuVcOBvOChF0U4EDHYcT+Kbwct4iE2SCvIlpZMvlcK2QrhVwHSZdh8G1UrpWWmSEO1RxQrigalLC'
        b'nXAPgCtXkX1erdobliEIDovTWVCpCGiPkgnYgSDeOZKrlN91qkop8RlFsxL4TBjwGQXlM2GUtyg2hJUEXPfkzdBdE5eL3gzo8HLcWEKtQpuZYcwwI7okOsRsKerHOp2E'
        b'zvz9ucHbx5K9YdkXP7s8uN+ErJ+6GprD3jvx9eKmceP2/nl71VHzg70RPzy/asIhl3n5d4UvC8rMDUebV11I37vyiUUx/z71u23tT7W94zK9de+Hn/1pdNrQLzqKEu8m'
        b'Pvu6cKKx5cNnldVVrot571TcyF37H+ZI+pBX0k5pVaKlavdQtJGuM7rG4iLJKps3hypupahjJe70sZn1DNmixZfQC+IS7IgfkmLAJyYHbB8/hY5TpQ5fjkBHqfecWC2+'
        b'B3Xc4tA2tB3vo9KSy4V2pxhK4vWiVniSS0Nb8ElqIIuqXRubh1pQG27L1aM21BbGRCRw2DMr0UVkEQV64WnUUoh3QkvOpOLWFC2IFUx0OO/Cu3ELJR0TslZCCfQSaLc7'
        b'dahdxiiUXP/B+BRtW9no1aglFWQ4Q7Zot4kFErMVn+LxpvUbRDFwZ8M4oii3gE6fk68nvngtHL6O96PN3QV85SNTl07qEWY01llWG42UZgyhNEO2XtyjTqDbhiqgEwrp'
        b'v4xdFy2htUF6T6QCSi9faXPSHUJQZ62utV5lvZ34MAgWr8LpclgsLq/aXddpMulNT1E4yK6Ig1i4xD1H4gjr0JIk2U8+RkHydSf5GLClO/no1tYgWY+V/kpIJWRJNjDL'
        b'IQMKK1vQznqVRmljFK5lTostwHVDHDjldJu5tkIwz4yEWv6X3Fcw62J8EH0PHwlkNYDUsl65kYycQ++H4wfmSCW4CK86QE5iHqnOKrHOcKNvHnqsN/rb1BtmFGe1x1pj'
        b'QtYaJGBPYkRDE5DQ/1K0Jv84pivJ4wusP/3xE6yT0I+D9S9fWvMX00emtytqqtRVH9hYJj6K+6D1rGQOXDYuky5kskRheT1Ll2kZ2iiiNxdy6URanQFGQL8nHfMM84wq'
        b'YV1fHyoElRJ9f3gH8eUMWAOBAPT+cQSxlImF4XMmUhxnNkV9HgLLQwMCgk/+aSMAk43Ekc9o9KqMRtE5Ha7VRuNKt9kmPqGrCZasw15vcQAK0lVHF2Hn0ptAu0wc/8xO'
        b'Z6XFZvOt/a7rt51gnVgMitCOkG31/2Mkm4aS4eQcG/tA3YcKFaAqJrLU4yoD3x7vzMvW5ugNCkaV+fRyILRAc1/sNtUR0q9zF9vJ1AW2nN/L743eGwN/kXujrVwVB1fS'
        b'f4FrVYTz4bygI0w/wC85BhguYfvhwMBlFjmw/bAmBph8eCsHrF8uqGg+gubDIK+m+UiaV0I+iuajaT4c8jE034fmVZCPpfk4mo+AfDzN96V5NeQTaL4fzUdCy1SwGhKF'
        b'/k3K8ijSG4EIGANaWdpmNQgrA4VBVNiIhncHk3ct0cIQeJsvj6G9jxaGtnKCXrK28IJGGEb71gfKD6ewRlBYsZAfSfOjaD5OfHtv2F5lFb9XJoxu5QUDFUvEowZktKI8'
        b'0VXhQpKgpTXGQw3JtIYUWkNfgaf0IRVEn0pKPO+PUWkC/kl3xTMQQU+0Cq/MCiKsV0bwMRT6FVSGBSAAWThRvvVeQMiIKEOFkwGUJtbniB5VFSWRlzAqUSmBvIRR8qKk'
        b'JCVsg7Ik4Fo0WX74FaB2UBPJv+w6q8tqtlnXkQMcNRaNWeqQFRibua6SnADp+kp6vdlhrtWQzqVr5lrhLQd9NXt2RoHG7tCYNeP0Lne9zQKV0AdVdketxl7VrSLyzyK+'
        b'n0Re1mlmZ2dqSRVJGZmZhWUFpcaCsvzZc4vhQUZBrjGzcM5crSFkNaUAxmZ2uaCq1VabTVNh0VTa61bByrcI5GAKaUal3QE0pd5eJ1jrqkPWQntgdrvstWaXtdJss601'
        b'aDLqxNtWp4Yaw6E+6I9mFYyZAKyte3Ok4SGznk7bRa58x2x8wwtqDbCvHl+W+LT4vpSBMSop1I8fO2mSJiOvKCtDM07bpdaQfRIhaZLs9eTEjtkWYgB9QKE7EkS4Ct3i'
        b'R6nHx53Funy5b1+fyJXF2sTrb1FXN3t9d3uruoCeb8l0JBPrpM5Ajr/kLsLNufSgzlB0wpImQ7fxWXyR2ileHdHGDGKZxF39LIYPlo5m3GQr54kx+DlqoizCzUQ4T8Xb'
        b'4KqwRKylLIvsK+fnZ+ezDIjqoKU/FY6vTUenaIW/6i86uBzLt9n2LR3OiA5nt5agvWTDOiWXOHvmLcgClV6SyvFuLWpnSjJq0Eth+MDUXFrLqsmiG9YHU+15Lw+skNwM'
        b'c0VHhdciV9sWWCYybiLOoHNo95TAqnEzOawDbU0tzsLb8xR4E97KzMenFPjyLLxF3MrcjTpwm3Ml8R1v0z0NvchSWye9f5d3/hCerm9IG9U2o44bG7Ple//6tK3fpJht'
        b'W3c6i/4gc13NyjYvkG1DJ5cO+PXtO9+9f3r6tB9O/vv/vVE4YMqXQlX0g8RvRj4nLFM8tfL130z4/KOl7klDPtLf+c3S6e9N/m7YWlV50rx/LDpk+3rz1lWpLd+PbatJ'
        b'+MHq6weeOfTZ+dVblk35qrDfAcvCuh/l5w0d869/nVq9e80LJ/9Q+Grbr22b3x39zbGvaiMORB3M//i1T24dbfpD5B+Y3Iuzx/7lrct/f9HBmz9/bdr3jzuO5CXrf3Xz'
        b'b/3/oPvmvqJNs3LL/A++O14bS/WZiih0MQIGSJvvxucy9Ml4eyrH9EUemRLvW0/1GbwPH6rELTq/s4JhiuiusGQs1agWGdfkxuJnDTn5umzUitvoiShmALoqq0MHCqmy'
        b'V4YvZHdu4eFzZZwen0X3XETIQHfRLXzJv++FX+rnq6IvbuLxDVAgL4la4ZXikaLTJUgYzwZu9fVHO1xp4uydRedhynfithRMjlxJm6u50K+doq/DfHQ53xJG/OhA2aTd'
        b'O4g9CaK1giAFM3FqxAKOqIf4VapP4o5RscQ5RmyTHB9Ep7NYfNOI20RP5JfRbavGQiRR8jaPD7FoJzqB7ogvn8EXcsnb4iKT45voLL7KsfKnqCeIMRZdpzKshPL42ABR'
        b'F0U3ORfhpgPtiUTbbNXSg3F0fO+S3onVpaAOOd6CzseJsF6ciTwgCN+kNeax0JajLNpVjY+KDT1ShA5NxefhqSGfNPQaiw6h07idvlyGbplIO/OJ64gue0m9nImq5tPR'
        b'HgOVtedk4dPwoijpzRmrYKIy+XkadIROzHS8lfjbwYTAUBfosxbgzTImCp3l56Ajg3y7aVH/tWmtqywPQrIVuLukB2dJYrxyrEz01eaIxUwG+rCaS4AcvUd14xj4U3T5'
        b'z7Gc7/prlQJ0QpHyGnwgRLE5XNQBniDJLMan6nYRujs1hEfW7bVhYiV9g2undRr8FVOxnNifhgbqF6M/DKFfdGv/I+mJTaIaLTcS0adHLXGxT0vshOLTnO+PKvXLSYSD'
        b'gUzhY2FJDotZ0NvrbGu1BoDBC/bKR9aziTpvrLBW9tikJb4m3R9JGgBSVq/wH8emIKeKWI+Ql/khp/QuCj1+A4jW7khhfNplCOBmP3BDoBz138BXSfCXsz4bBwfrzCxq'
        b'qyKS9tQawWdTUUqD0ZuU9fiNqaGNcRT6F0ZP7agmo1JERiX1UeSzx29JVUBLtL21ZLm/JfqHy3bfDj/FVvTUgFo/gqSVUoUFYAda9DTSxGps9Nh7j234f2MCAh3t/olu'
        b'gmsmUTqcGmuX9eq0WGrpkXvQdKgu0u1FcgxfUsBKQOGB3s11O+yaIvPaWkudy6nJgN50l5OToMvQcXhx1STDOEOatndJmvyTM90N86XSEXDUtghfSCnIfYKcx5HNYoGF'
        b'b6u1JqcfZp3knP3o13f8xfR2RZY5yZIU+5HpzYpPIcdV/Cn+jfjTy45v/FPUG2sUmrZhz23qkDN4aHhm2yitjMpUs0egS36Oik+ig6R+kaWeQCfpLlipFh/slJqoeIL3'
        b'jfdJTTPiKNOfiZrDcEsevjeVSi/iIXV8Cp+jPg46vBs15VK5hVvGGvArqdn1vVnPwoi5yndMSvSOYp5RrUoA9rMu2scMpDLiaxO7VtZpKVsESX2QpWxXSHtwcLUgTsyC'
        b'4g/xfCKGBMbDfpsTT/c93TCixOISjQdum8sKqrNE591OSVem4SZcDnOd0xwQNqJibbeKSB3p1JSSbsqHMlAV/JirLQ7TQzQ68q+7tVTyoElZ0MbE9J/KMWmmqH8UgPZD'
        b'3AHRZbxv+qOpan3RHaKtgaqWje9YX1jP8tSh8OXXZX8x5QDq6mI/MX1k2pO4vOpT4ROT7EfaHb/UzZ09Sq2dtSqu6GTj1BfGbhlG/fZG/y1i1ZGRWk4U1/eOTpMUi06t'
        b'Am/hZEp0ZqGLkHB8GL+IO0C+rewbJOEGSbd45xOS49TD9lSdFpfRN0OUa1M0jZHQFCRDUS4E6W9dfx9WdXvHB4uKXQTTevfOoiUMfpwmp9LWBeJ07NYQON0z9McRiaK6'
        b'NLwnJrDVzwQoF3pUHDb4jpAR/a1nZzHqcUO9bYjh0e9x86iuYsRuB5pKd7udf83ZHdZqa53ZBW20Cj0xzzrLaomkjzWMDWEd6dkkJIh2F9p9nxsoADJoii0r3VaHNDoC'
        b'XFW6NIKlwupyhjRDkRUPLXDaa32CmBU4qtnmtNMKxKrFAa6yOJw9G6nclWKLMmdnA6+2rnST+kB8SSJ8WePwtQpgZbvMhFM/nHB0d91UFrjJxOFDS9Ht3AKyR49bUpW4'
        b'ZUFSgX5Blt/ztBg35y3I4ou1qD1bs6zC4dhgXRbOzK6Orl26mHqsVk7EWwMsLBMXB77MoCt4XxlwsX3sSvyKchFokAfphvZSuwV3qNl4tJEcPmfQC+Hl7lmUHsxFB51R'
        b'7oVZZGe1DDfrFlKXgRbUXpqlIyB2ZOfh7SzabpyDT2rXoP0j8elSjsH70HV1Uelq0fdgD/bkBrQJksML6v2VFi3SLwxjip5RoJOzcaN1yfj+cmc9IR9Xfq5/+xZxK7Qf'
        b'm7vgGVT4jwl5r8nUiJlgiBm1SZ71v7/gJn1XNWH/H19c0fyj15e0Xfrxzz63Hf5SeFMf/RS3+UbN7l988brsxwtW/fD9jxb++tTHeGV99NE/Lvxwye+m3L+z8ZsjzxxK'
        b'Ofuut+ZE1Vp25AtD8fT3tOGi8eEFtKk/UGmqdeOj+Gy2nImo4/ChMo4yeXx0UEpEMjntQahjrMpHSoeiDhl+OeYZal0ZPBAf7bSucMiDPHp0uIJaGND1ueh0rmRgwE2o'
        b'mex2q2P4vvjscFogrA/aE0Smq1eL5h+0aT1V/XVaGFIxzA3DD8FnqAiBXoml7U9Fh4YFHYRN7ys6X+9dJrrsTx/daY3Yis5Ti4QLXRP9IT0j0U6/OYJYNohJYo1D8jx8'
        b'JEcaQkI7SYTvFO3wTqIfp2BFwq+WyL+YU3RjA0G1+JpASbufDPbGC/iAYp0MYRkk21ifw+Um8j/+Xw9jCUEteRzNXWYEgtYjIzjuZwRjqXrWSe1600keU2PV0la4e9bV'
        b'T/pbMS0kmcssy+xq9w/RHuLDVOuwVHkVTmt1nUXwhgOBdjscIPnPq5QFtJWYwdU++pcjMqvOUFyMJ0Jy41FXqSXWJWuWA+uSA+uSUdYlp+xKtkFeEnAtyoofPt8r6xLD'
        b'kIlyHuUCgRpOzxtPpF8iD/C96z+W0PMeAh0F8S36CowguWcmep5Bk2muI4qUWXpWsRy4WUg2Rra3gLOUFE6ZlDaWbmyRTSeB6K6gY/UI3j/46Zp5NnO1ZnWNRdo2gw6T'
        b'PneW8HWqJ/B1dlcIMA4LdKTOma7J6CpAm6TuPAIf7K7IqQrcGYRBlkzzc0HKAnGzZActQ43ofBbcLpYYGzsuFu1Be3BHLu7IYUbhk1H44Iw4GugDih7E+3MN+uQcILYB'
        b'dWSRuncWidVn5ZQlSYExQPTGpwar8VkWtVJBvrYqi9klJMkZk0k1yJDMuImujfai5qcDBflIfKRTltfn5JcE7rq0lITje+hVm3savLq2oRC30BLUIp5NOGgK4amBuy1Z'
        b'upw8A26dla1PVjC4RateCcrAbXpGCW+a8lTQ3gwdEQ9I7QA7Cag6iOo6rT5HzqzDZ8JBct82X8tTvdiJj4KeSWDzjGwmywxA5/ovc1Mr9f4F6FaK+G4+8e16nsObJj+N'
        b'X46nsczW4BfwiZScfGkUWSZuDE8G+xA6ip+zpvCfcs5mKPZxYdTgd1JicZpaVvT93y42v/7dU8e/e2d2dEzFH9LyC4r6nV2ddMle/kvh9UO/PLKvdOPvt/RPubugeOzt'
        b'Vt3+yWXj3889e/7nz3328ZerXv30tPxyZuEPVk984ofh3y+P/CJ2S/IG6/YFa5UTf5uxRbbko2NLCj/b8kv+qRcTpr25+/fvLvzPSt3vvxvx4z9HzxyQnBfxBbBxQvEF'
        b'dA2151I2x1WwIBPtGEsGyUX4UAK0/HgnDw/k4E68G7+cVUA5qQwdxvvxNnTEJw34JIGSaApi/Yp+udn5ySBYcYwStXC1GWhTGLooSgk38TF8O4iLo8350i7OVXSOnlsQ'
        b'5hd2Hlu4Uo2OouP4rrg7gw7Fku0S6kSrQLdRm40bXp0uHhltJtYC6mlbKMZk0cGcpPL4ZgGIXefxJtr4+HGTAzYP5ExUATpFdg+2oL0iJ1X/P7L5RxD+KFEQyukNfk6v'
        b'mEBiZij9fF4l/anpORyOGvlV/1HI18UF8lqpLrGVCpFzCySxkKQqmOmHP54rsEysiVZi8NdJOWENJGeC5YLhvwghF4Rq6yObB7XEJc7XwZ748Zt+fjyMMA8grZSV+HlP'
        b'oFFQKyP+Se1cAVQ9T5vgIOTJQbaFHcReQPwSBXul0Ug3KRwkUhvdzPDyxHY/i2RD7Jd4w3zWZWIQohq0NzJYsyVCVIB0VUPfCpq4Pv+PNpd6wjsHoe/9yXxtYIiBW8bF'
        b'yxSs7AEHczXkATdJQQMFcfy3+42SqVWxLKcSww2pZPEslxBcIlamYbmhFIO/oVTUvR5dd+YViHI9y6iq8d11HN45FF3rxvVU0q/zmy6eVwJXLhP4crmVKVcIsvIw+FMK'
        b'8vJwQVGuEsLKI/bK9yr3xuxlq/i9MYKylRMKQVaK8MRU8dR9mvgTqS2RQoSgpt5VUa1ceRTko2k+huajId+H5mNpPmZvlKWPGI0IZDDi8hPt6VOlFOKEeOIhBTXG7o0C'
        b'uDFC31bq6k3L9akiPlf9pBJxUCfxtiIO3fFQhnhfDRAGNinL+0LbWGGQMBiuE4QhwtAmprwf9aZiyhOF4cII+O0vvTFSGAWlBgijhTFwdyD1kGLKBwnJQgr8DvYooCad'
        b'oIcyQzwMXBuEVLgeKqQJY+G5ht4bJ4yHe8OECcJEuDdcqnmSMBnujhCmCFPh7kjpbrowDe6OknLThRmQGy3lZgpPQG6MlJslZEAuiUKYLWTCtZZezxHmwnUyvZ4nzIfr'
        b'FE84XGcJ2XCt8yjhOkfIhWu9UCSZY3ghXyhoCi83CDJKExZ4FRm11M3rpSBxiax88YHo6SXGuAVJkAQfrHaYiQgoym+Va/2OR13ce4L9xhxQQa3FZa3UEP9Es2gWrRTF'
        b'ULhBJEuoU7Sr2NZq7HWirBhKltNyXoVxldnmtnjDjb5WePm5ZcUF96fXuFz16ampq1evNlgqKwwWt8Neb4afVKfL7HKmknzVGpCfO6/0gtlqW2tYU2vTKrx8Zl6Rl88q'
        b'm+fls+cUe/mcoie9fG7xIi9fNn/xvHbOKxcBK31wgyxhQfsiDYT4ck45IcDruWa2gWtkBXYF74xu4I6xxxlnXxcncA1cAkOiFjdzDYDM61mBb2BXMQ59A0tcGuEt9hhP'
        b'Yh0Liv5QLpGJZyYz69k6GTwPI1fNDHmvgTHKoFb5cSD3RoWgpMpX+IfGUOpIVw84aZ47HeC6vtCTkE9HQlQxzGId9E4vpixxyNKpj1lJoX7CuLGTA9FIAM0ku4pI/Bpn'
        b'vaXSWmW1CLqQeoHVRbQI4IE+XzcK2acmiigLiorDWuHuQbNIJ4/TTYKlygzMxY9GJlBVrJU1pHarOE6AjBIcQLDuffuYzPn9vtY6uinV2Zsxo5xjvKzBy6Z9TLjGxw/g'
        b'333ekJZWoA3zxnQFS3ZSzLb6GrNXtZD0ZK7DYXd45c56m9XlICc6vHJ3PSwTh4uhpgUqPRDW43iG6fVEO2W9v2Elt12ZSsHGS0YPDavkVCAgrYsWEeDxXQO0LG1aj5LE'
        b'P/2OAT4Qfr8AfVekoVO3tt6iMcGUVAKvtxnmiL8mk8Exj3kMz/Z2lo5Sj8360i/gDKTeCaERsRs4zgcuRgJH1vByLsLv/M/TCfEqzU4j9Qb1Ki1r6u11oOL22JR/s1Jo'
        b'yCjmfiX1F3DXVoCaDIMhjYKm3mauJFuxZpfGZjE7XZpxWoOmzGmhiF7httpcemsdjJoDxlIwmQiemoXlbihICgTX0n0TN/gYE0tDRviDk/uPMbHUeP9IoSM+/DwUySmr'
        b'J6KZSG4sayprzHXVFo2D3qowkx0Hu7hvC6XMmnqHfZWV7MlWrCU3u1VGdnXrLcA5MsnQQudmm+tWUHu702UHwZESh7pHIgQSEfA1yUibZCLj66YLXyQzhB757ewwvsRR'
        b'NsRWHgkbb3HV2Du5mE7jtAJFlaohr5Et9kB32576KFWUTgLPp5skBhtiT7BXw0iF3U4C/GqqAi0wbjoVQpdpCEkiV1scsEhXAXc0VxBfgR5sMUECJkGo7gfXogqoKX4V'
        b'vmxM0Wdl64jim7uImCnwziy4LCxLytFl6xVMbSw6XaPE95BH5yYawYrsMNAjL+FXFiTl6A3E+J9SgNtnoVfwiWI9Ps0xE+bLq1FHDZWBh+GbqU5Dfg7etxptjFLEMtHo'
        b'AG/Ar+KTovvnzYTBgcYLdBpvTSrQJ+fqi32V58pBUFUS90O8l4aPRzvwaXwtD11zJknx6+WojcWXdPiAW4wcgbfpS1Ar3luGW/G+snzUiA6zjLKQBTX7Tvg8Gqx9IGrP'
        b'IO2SMzx6Dh9DZ1m0UYZOiEHyj6G9i51ZonUjN9yELsqYPtBsdB5txK+4xQjTx1D7THzbmUSjO8nXs/jChIhS6/Rze2XO70KBHRNe6ts6o3i2WT13zxcHvldyeX3rlr9s'
        b'3Nm35rP3BGGebdb8Qyc3jf5B1qqcu58XfP7qmPJI5eA+V/svv5+zc/9g2dXy49/5QJsu3Dj+i2NMY9lbOzfveOLle61vRb589pfpI96Xn117pez8nlWHBk0Y/LMPD48q'
        b'OeCQte/416yU781ouK2OyI/IKmm+uuyNtnd+OeTVqY4n/viDgT8snlL362uvvf/CvMb636xUfTG6+d1now69bt32WYdn1KcdE+qWPvjr35/42bTE73x16AfT8r437d4/'
        b'Z6xSxmn7ULdD1BYOI07iVeGWMEYGc4yOs+jC0/gm3SHIYfCZFD3ejrelZg0fgVt5Rj2PV/Qvow9ROz6ZjFpS4TnLyFLxPtTCoo5R6WLsziMTqlNy8vPgybByfJlFR1Ro'
        b'Iz06iLb3Q88uwMeJNSU/jFHIOCXaN1Q8k9iEto6gm0e58F6/CctYdALvXEkNIdXjFBHJaLMilB0Hv4z2zhT3c45gz5IUgzZZxJ/oYXImGl/h1+JdAgVuQSem+awwqA1d'
        b'ZdHRQryfdmdaHDqVImGdrABG5TSLLsXgqzRkSRhqTSEWFvPkbJ0BbUslqwoq0Whk+NpifM5FDgPNxvvpqUnfIkPPo1OoNVVcacn4thxvHt9H3BQ6OfRJsZvZeMdcdAZv'
        b'Y5kIgcOH5uMOF1nKI9Hd2bmFeBtq17MMt4rNUFZTd5KhRbjdf9oTHS2mh6rRSbzbRTzL7Qy6kpufm5tvwNt06C7emeuL3pCMdsrRy+jMHDoIwgrUgVsK0AWdgpHNQa+o'
        b'WXQnfdljuEt+m0OTfUVKaAwm/tSGNItQsmfE/6qoGMl6RNxI46mrqIy6kRJLUhQrOpeKd4mDKfnlNsrYdYMkmSckGN+pK3o+8ts4iLLiq1SS2AvJAyJJkKkUbUfMpgEh'
        b'4kz13iaokwiTPXvS0DgwNNQYSAhsQBwYjn5+5JG8aT78WSj5IFNkcNKJHFEsJIIM8BvCs/ySmSQmEJnBKQn73dmRtK3QRc7oIlWEliK6M7fS7hKLmXDFICbu46l2wuzJ'
        b'nspaIo50b5m5skbcqa+11Noda+kWUJXbIfJlJ/38zMMZfFddKliGDXBsdJkd1aC4+Er2uolS599FETHEt4niE6SI+GNxBmr9D5EDQh9gV4r+SQOXRjZkkXAhRSbbl0VS'
        b'uOdFmYMUuXw9uTn9o/UzxJvFVdeYNWzSYoaZtXKxfbCW7iXUoWN9nZGROrSLY1i8k8EX4tBxN4mZjV5BTfG5XcSKMmm7RmSx6GIp2fJfBOyebL50ehFkp5NtiyEx6egE'
        b'um6VXXLJnGehyg//VJ7fKh6l/793omK4wbPnTN88vO3Yi9m5W3SqXz/Z/MmPd/3pyy3/KbH95L0fXqx65a0+4UMXLvy35t3jJdOGjy8sistHczbXv9Xad3v+5vmJ4/Sx'
        b'g/7z5WXXp7WJV7edK732GfvOT99445Pvurl9Fw990tjxm6bcYa+3oK9eXZmf/fTb/xht1hr+OWX4v5d+dsjhfvn9Pz6x5+lPr4wZdP2PGdqVyzL+7vhTn8/+E+H+3STb'
        b'nxdroyjHMgLXa07h0Kud2/96dFUvOmBtxc/i56T9KNSOtuQSaSN6IW/DdwyUY2xA+yzJ6EggzwjmF+gwukLZac5k1ET3r3LxJikeUpmFbm+gO+jF2WPX+Ol+V5rf6KQV'
        b'oD3L+5TE+Tcg0FG0CTWJx+UPxuNDKYX5tlJfHI8IdIXD5yKRh/KccrSbBpFoC4ycdA+dmkx5yQy8Cwr26WScwDRz4yg7AmHtqo0wzQCWiTfh7RLbRLfQThfxr3ahm6gZ'
        b'nV5JRdVsaH7QcHD4CtrOGlOV6OQTfSlIfA2/+GQKfj6D7rfIGcVybggr+rxF4st2ug0D1V8N9HuTKVcoqMCj15Wk6PJBKgXmulWgse2j0R7ekVgX6lD9ozK3MElloOxs'
        b'XAA7U04ijEwhnYRIYGMpyyJRQqIoSxMdI6KIM0SUxCykqoIc4Z4J5lu9hAvhxLKdHhD7IUniunCrhJ+F4FZdGtBNIyc0hmrkJKIA0cjhj9jOIgXWxcE138gmQAGBC8zR'
        b'YHb3uVHW+7JRhnFV0CHSPq/aWGc3Stqy08ubK5yieSWE5u6NMfr3wUUzZA4nHRtXczCK3Lp+PotKl3LdbIX+DWgS8q6ZfmuikXOMaGBpX5gVvEND+uTo28AeI31gjrPr'
        b'2boIFy+wDTRPSlbxogURrmXkexXUOsMV3B/jZ5u1Vic0o7KGMpxRQO+JcYpqzOQCZo8OQZy1tt5mrbS6jOKAO632Ojpb3vDStfWiSYoOimR/8sopd/YqRYOu3dGDk3CU'
        b'sd5B/H8tRlp+ARksEupZRb1uokhEPFYB0go9Bi8NXNAbISeeDhsVHokJFIaCGEGXs1WcNMkwALFibUmkkzqxq471/kmNCm6l0mgEmA6jcSkn2WTiA01j4rOeUTCWtsSH'
        b'hFIrqkkrwgiawagHgO6CT2FGcubfSM8t0QMTMZ24Lz0KEsrItcwHOJHi/jHABIE9zq2ng9DArhCNYQCend7OOY4zkrkQrulKPBqiGQqj0eYyGitIK0j1RKpdF+lvB3n2'
        b'2M1gfXPBTZ/hIOzU0d4DZIvRWAV3HOfgRiBUSwio/vk3BC6bPr4FsYKzx4jwl7MriI2K3idX1FAnTgRpRw8IC82xrDQal3OSU7uKCvjcAxUX0DBSolvD/DZCNR0OAlTt'
        b'23wVAfTQ/TroZr1v+oOGvS7UADxs2GU+5GNn9jrq1TCnzhCjXv1t5lrun+uZvc81KBzG1aGgWkKsML+TOxlS30r3e7gFEOnu65nYv4xG8vUjxyUmwArtexLUwyCBdWTI'
        b'HvYj2zgMJbxcI+cf4pR2vnOBUVLqiw1y1H+3S+NgxZsFwWjcQKacMg4acDFg1dPHIRE/AL9IA4+znWbvmz0NOiFutMbGEIPh6A7rEQYjsetgUJ7D6h03CNRXQ3fa6a4w'
        b'GreSNtwibQggcuRBz92Nok2I6OwwmX3H7d66S2ts8dFydRAt7w6NZwKoCtGs/VQlzMVQCgL5+O5dJmZ/b1SB3ZUNvNNCzhlZhE48oMPQ09EZo7HWDUi4k5N2MFT0LGoQ'
        b'EtACj4UEoMOj3kaF1rg3FBJ0hxWEBFMCxySmOzoM9I/SwNCIkdqJGD2MSITR6HK4LYJ1ldF4gCyMTtqrAhFhXay/sf5i3769A/ztHRCyvVzqwxusBpZls9sdtClHyaC+'
        b'QQY1zt/OzqffvqEJ/oYmhB7YUQ9tZxgNGWQ0nvE3MQDF7F3XviywdUFyaZ/A1rlI+8ieNbSk83opt55bz0ut5BtJe3nxqspHML0KGBEAC5I3pZo/YAJJp0/BIKTTK19d'
        b'Y7dZiCtvrdlaJ1h6kjBVRqNYp9H4MieRCxVVZGI4otrIHqzr4++xr2TPUiWR5UROE0GHvjFYcgjFbWgEtmqj8QYZ4tPBQ0wfPAo01WNAq7c7jcZbIaDRBz1Di6fQXCIk'
        b'1o9KNeIG5sGguegJNihHRuNdn7QSG8S2KkJB742HO17pBZK1DgSR1/3kqhMOffDIcKp6hRNOF6oZKvyOH1JM4BomjxxbmBCmUf86IYdnyMpYwTiULtA4qUcHK/CCjLCN'
        b'ftCM9WRFEC2Oa+aOi2tEWhl0uuUFH5NK7w+n+7jWumpNvX21uBM8Nk30iHDX19tJeJ/7XJrBy46FlbLdN11e5Uq3uc5lXWcJXETeMKip2uoCfdaypt6nuvVoM4BxoMCN'
        b'xu/5JF8ljTdKvnAXMCJSoXbKbciwaFO7OP45bFJ9TpvdRQKIEQ9db1SwuRnyVVWWSpd1lRiGGsipzex0GUVjqldmdDtsDhIe2nGEJJ0uhH789Cr9CnsEtV6Ku6bUHk4V'
        b'V8chklAq8yJJTpHkJZJcIAmJXOp4mSRXSEI+UOK4RhIqR90hyT2SvEYSylYxSciWm+NNkrxFkndI8i5J3iPJj0jyE5L8lCS/9o2xNvb/H5fELu4eKyF5m+wFEBcIJSPj'
        b'ZXIZJ2M7/8dw8SzXtwf/QznHDmG5MUo2keU0KjZKoY5Q8vBfFiVTKsivWqbmlXLyF8UrFVF8lJL8V4erefF/Ai9+U7sZbcP7nXgHbhX9EZWJ6Hoi50anUUfP4V1/0cUf'
        b'0RdQtUpGw7sqaWw3Gt6VRHiTYrvRUK5COM2H0VhvchrrLUyK7aam+UiaD6ex3uQ01luYFNsthub70HwEjfUmp7HewqTYbvE035fmI2msNzmN9RZGvRvlQiLN96d5Es9t'
        b'AM0PpPkYyA+i+cE0T+K3DaH5oTRP4rdpaH4YzcfR+G5yGt+N5ONpfDc5je9G8n0hP5rmx9B8AuSTaF5L8/1oNDc5jeZG8omQ19G8nub7Q95A86k0PwDyaTQ/luYHQn4c'
        b'zY+n+UGQn0DzE2l+MOQn0fxkmhc9IYlfI/GEJB6NTLmG+jIy5cOoFyNTPlyYRQlchjeaHH8p7TxR+uGlrltBvoOXAYWkQHNdihFvCuraUWmuI7SxwiK5r7msdCPG54BB'
        b'o5n5HNuID4a442EJ3puRdoSCfS6IUhRw/NVEKLFZPMEj2CvdRNT31xxUm93hq9DqEu1i4qu+DZbMjPzSOVINph687oIy2VWSA4lZU0GteFCduC8WeDxXJ4L09VXyrHQ5'
        b'LGRAguozO6kjJ2kcdetYBTWZbTaNm0hYtrWE9wSd+w16OYjnEs2VUB2yIe0sZwkLdCgJG+zPNHNu1qH2sUIXNV8eZ9fzArA9o5jKaCqnqYKmYTRV0jScpioQPMlvBM2p'
        b'aRpJ0yiBhzSaXsfQtA9NY2kaR9N4mvalaQJN+9E0kab9aTqApgNpOoimg2k6hKZDgYHzRo3AQjqM3hnewB0bcZyZwzyVAsKubL28QXYM1uhx1tkkwHU/Zr2sTk3vKY6z'
        b'jl1CGDD5UQ0yYhFcL3ONBqYva+Sch1xjBGWDTDTcupLI3QZ5I88yK1c1Q7+WRzWDHOh8KYfZDJCpfBZe4HifCAgTRcTvtkx6XwiUQ8zzskYvZzTelxtHOUc574/qWkmN'
        b'mTg7dfpLiTZTrVddDJzfWit5JSrErUEx3ihvtApeudFtcTlIXBjxcII3Woxl7j+m5phDeBPZoXMQjcJBAr2JkUqWUMkg+IQjSH7iHjDUWO92gERrARBUKgijhnSX2asw'
        b'1jqrKegV5NSf3GgRf+gZwEjfa/TrY/BSZQ3Zv6QBb80utxNEE4eFWLjNNhLcqK7KDi2m42qtslZS32SQRkRa4X9srnV1dsgbb7TZK8224CP3JOBwDdl1dUL76FqFauiv'
        b'GIjYO8jYZchBkoV1KJWVw3Wt06uCRjpcTuJxTeUqbxjMC5kTb1SGb2bEmQhzWlzkgVYhegMQM4JXsWI1+dB7QMCCDczDoyXQ2fwtkfvKGWKAVoaIiaXsdqfH/xxJY6T4'
        b'81HUrhEFeRm7rl+XEXisuM6S1+nfGKZn985Y0HVEr9PErqD87qfTS6kXQd2KzpOUOjH0gcsunT4l3n8CkGhr1VogvAEE8TG8Ual+k9lbY/v6Gnt/dHCkLLLlXmt3dR55'
        b'pQFDHydSVFZvcBP9cIMDZHUHSyKUPhpU2tvc3qAODO5tYHCsLmClcKGPHP6i97hYQ/xwtSHiYv23oEt7Az3MD/pXGRoxSKzTXSGdqaCe5gSe5PgiBV/qtV1USBIronuK'
        b'RKaph9eIPEJD0oQI52TQlHTeq7JaCEBJQIDaoUCnW4yf9js1ydI4Jevg0uqiv77gWcl09zBZjGCV/BiDVd7bYCX5B2tC98gkPeBnxuxFGamQzH1ELBXjtDv+3ls7Uvzt'
        b'mB50MJ4E/rBUBB+R79qezOK5c1LnzJ1d+hirBtrzv721x+BvTzGd/QCWLTlL+bznu3jxGDRzaIQS0WfJttq81imdDNfUWarNRPd+rFb+o7dWjvO3MtmH6j5PpIAGS5xZ'
        b'k1SycFH5Y8URcPyzN+gT/dDHUOJut68gkqx4vh0E3Pp6Ozm7BCKRWzwR/+hR1QD0v3oDPcUPOrrUfxTl0UFIGPl/vYGYFkzBamHNmqstAWhYX7PWSbzRNEUZ2QWwxm2P'
        b'0b921vFlb8BnBg9tJ1CbvToYpiYpt3juvMfD/K96A53hBy164tUJepddDz+djFuTNPfRYUrdvd8bzDl+mINDxlzQJOU/HkDo5L97AzjfD3CY6G4IImEdObQhLRUxDkZR'
        b'WXHR4wH9ujegOX6gsZTGUQlZOn/y6PMHY/mgNyj5nTShK+UicjXxjiHXSbMLC3OzC+aXzl38qHRT6iN51iP0Ij/0L7pCD5b2DZp5QCPmW6A9dVQudPpV7lCB3YF4Lcqe'
        b'V0rCs+s08xdm6jRFxdn5GQWFpRk6DelD7twntTrqbTOPoEyNVGdPtc0pzIcVJFY3LyM/O+9J8bqkbHZgtrQ4o6AkI7M0u5CWBQjUDLDa6iRep/U2M4k3JcbleBzCw/Y2'
        b'hAv9Qzg8gKiLqpGImGa6GM1OGMXHWfb/6Q1tnvRDndR14kQNzqDJ6Dw3ll0wrxCmYE7BfELpCSo9Vku+6a0lS/0t6VdKub2oNsIUCgR37I+4ViS6I+9tqI2dNF6KmUIP'
        b'IoqALJ3mn0Bd5HGWCtcb8IpgotdJ7IgbtobYrEIwFZ9XCN0CWSgBdI6hLmtquiVIfaHqo8i1eFSVbHnAn6wRUiMpL6cubvSQrJGmxxSQhh0HrOzk/venFYuuysRy5Zdx'
        b'RJGr04YWWiQzaJWOv5Ju1pKkS6hmaoMgIQYcdobun3bGc+6ySxRBvtAmVWnhpU1GBZdIv6xEdFwFu25gV4Uz4J2eZ4pY0QRW8tcqFUGGmiayNWHnpV030KS7qbd+v5Ye'
        b'jy4mSnPkCCNbuccZsnVb3blHBv0PY8nXn4hRIqSrmlIyWBjJB8doy8VoWqEaIxbsud/xAY0RI+kKPncxaurytUYu6iE9eM7ZLHVG4+rA1oQ2MtByBdoRobaqqPGDbi55'
        b'o7oYrp7wY04n0tT58MUbGWy3UkhmqzCJc9Nv9XoVkslKLlqsZNRgJSP2KhoOxKsOMlYpJFuVjNqdorpYpSICjVIKyZql7DRmiYakqGBjlUPHSujjSCVXY1lpEB8ppJrj'
        b'j5D8iFiGfsaIW0qxEdy4xwxsEdbDfdl/Fyijx1/Fo5VTy5QqJa+WuwkCoI2FYRGrIuvV2hx8Dt/AO1IK8gzEjZx8JSC5Ro4uoda8kLEUyT/nGiZw90rgmhj6OUJekPk/'
        b'RyiXrhX004TidZgQJiihrNLDVbHiZwjLw8UYGuUqGrOWI7E04G4ELREtxMC1WugjxEKJSCGOLpl4b1wXlM+zgqYuC2ioLJAQkKOHhBgbqaeGkSV70UaumkQP4AW/yiWj'
        b'eoE33P+pYListQtmG/k43PCutkwC0Ri4Z+L0OXNMYelmra8Spa+OrhSO7PFu5CXmJVoSVey6QSHgPN5hdWoPG9gb+9vqNxqGhPZYX4KTxIo5vcHz+OA9To1ze6uxucca'
        b'/ZNOvCJ8nh++WoHjkVrn9Vg1PNhOqr7U4+D0SOl7c8eA7nTCDGa1lD61+mF2ZaoSTErPH4GpVj+cqe4isPRsz/2T2GpX732/Uw35epXPS8oZ7gLAkj8+9eFawTsHwDX1'
        b'iKLX5Eq2gncMccnF7THIK46FETc+lpFWH19wXx8o9taSE/0VnWESxnRp6Zjg4oLdIp5bF/3+afQW38E4yiNAKHqBkZam+En5+eQqiyTUrYTMDjC0+npQtn0O/xEBIGjR'
        b'HvyxeLMg7PHJSCrpTImK+pJ0Y810iKF8z9ijkrCn0Rf1P2A2u2BOGrx4mJd8PkEq6R8KWGhxzO9VGU9XiUjBG5g5TCMrAeYLugm//pfIQQRCPZ9SkBMYRJp5lltJHatE'
        b'Rss5JpCR3SBek/XgZV1dcTEakmO+1scz6/ShWu+yu8w2IEhk98k5Ey4InbfX1s/Usl7e6a4NKSfJ6VtHCZ7/mKypkONCyxRoo7pKSJ2eNxRZOvGkU5igskU+K82Ao8gv'
        b'YPQSmCQTCq3npbFTMsCGFTQmK6fmlXwUT3xK3ORgz6qnsnxcWeLI6HwEYcq4A2/TAfWagy+E5eEWdKcbb06Qfp172SDeDHNL//OH5eU88Sgh/iTke4GCinBe8mVAIYpw'
        b'WqHP4ahy8olgOXDhWCEOOK+cnn5VkjhVnlhP/6owIV7oC/cVljAak0r8rHCYkEiuhf7CAOp3EiYMpPlBNK+C/GCaH0LzEZAfSvMamldDfhjND6f5SMiPoPmRNB8F+VE0'
        b'P5rmo8UWVfHCGCEJ2hIDz6daGUtMI3OS3cmWx8DzWOiBVkiGp32gN6yQIujgOpZe6wUDXMeFpwrpUiwuEgGk8/uKUdDbGNrfOE+8p68nwdPPk1jVl8a+Ci+P3xu2N0EY'
        b'18oK0wgcGBOeRsAi8cD6km8RCpPEZwBpsjCF3k8QxlMONN2rJqjo84fwskVetlAr93LzZ3u57Llebm4J/JZ6ucwsLz97foGXn5Ob6+Xnzy7y8tklcJVVDElm1jwvX1AI'
        b'V0V5UKS4EJKSueRBea5jDaVI87OLtFFebvZ8Lzcn11FKiBuXDXVnFXu5vGwvV1Do5YryvFwx/JbMdSymBTLLoUAZNCY7aOX74p1Ttwfp8wJieC2ZP9q57JGinYf8CGr3'
        b'6NyyAvd8QpUG1pCV4MLbCg24NZ/EFM3yRymlQTwN2fQgYZ4uO38IOrAgCxZIDjmESb5ZPBNvjkZXq/AW659HYsZJQu0dT+z4i+mT8cdNSZak3yWZs8y2KluFzrz0tZ++'
        b'fnXX2Oc2jY9kqtsVf76xScvTk5lPLUKbI1C7Lst3kLHPeAHf5NGFvOFisIOj+PwqTD58hU6gEwCZfGX9ELcmBR2kQQvwDS35LlTgl5ifRk30Y8zoJXTEd8Lw4RvVnI9Q'
        b'+441Socbp9Bg/vGBKBX8jWN550a5g3zzN/TnW4Fs0RKj/cX8kK/wvmjSmwL/x34/xPnFkO2oVAZMNQEc/A1MJcUklfQlcXH5ieF4Or+BqWwOB+wKB+xSUuwKpxil3BBe'
        b'EnC9WmJZgZhF+tb9M4CDCmhY2Sp0ZWCuL4IgoJNebyCxaWlkVzLnZUWZyatRUxY6yzN4Z30E3oWO4ctuwhjQVrwjrfNdQLtC/ULpgHUObgUdqi13URLetmjZYiUgsIxB'
        b'r6KXIyJnpdEz3lXVYYxaVsUzGpONX2pjaMyUFLQRHXVW4WORkb5D3ugOeom+8GBIOBOTtIllTCbdwGWDGDfZ/EWbJvcLCk1rwE2yoCPfYcyTJWFrcXsNBeCsXpSbnZ+r'
        b'w6082qJlmYgCDp8ud9CoLvjcstSULHIwHO+ZmDA+LQ01mXKZ4egVHt3Fz8toNJnKZNSYUkCOBbfml/lPlKPmIakLkgz6JNycmkzi79q1StzhRAfc9Itr+/AhfCMXt2Tn'
        b'pSoYRT8LPsxF4fMS5tNmoXvopimFjLceSqCb+FY8N+mJOTQ6/7whJSniTHQeYO+EtSDJ6KIh14uSxGahLVk8MwRtiUTXl1TTSDKodUiU04p2rsJXZAyLnmcwrEEbDbU/'
        b'dviQwI9A1kOR0iSYuhadLr9MjJSfVYMP0pP0nWEm8UleDYy4GbfRWL0yaP1Zf2z57Xl6hQ3vZ+Lm8/hI6mw3oZSoAx1ZlAJtu+ofOn1nTP+AzpAz+xzazpEj/fciJi4V'
        b'6NcY5QWoCe9ZQCo62H8dk4+u4WfdwyA7Gp1HL4JAcHn1KnwVbVuNr7gUaCu6y0QO5NDzyJNGP4GCT81Ezzvh2ULyKYGkHD3MPhBICqxYGjW8H10nrVIwaA++oWLwDtTk'
        b'Jt9NRluWojMpZEhgiFpScVtJUhKQweZUF3SmLPBjAoC67eEMtGgvbRs6xS2OGL8eX8NXnfj6StS62qFeiUFk6jeeR03j8UYxENCpRegl3EK+dKI3wBDLUVsFE4v28ehi'
        b'NBajQVuGyxnlrHsM8/+x9x5wUZ3ZG/C9d4ahDE0URUXFztCxYq8oHaXYCyigKILOANYoCErvqKDYAEUUFERRFCU5J2U3Mdkkm2qa6b0nG2OK31tmhjYYk939f9/v+22I'
        b'cGfuvW8v55z3nOeZGeFydfcy7YA5RWZGGiOohINBWCBANlzH7FjbxDmiJoasXXtvfhC+sIVyVP742vVHB7/58UfDfA85PfKd7NPhp071/3DJCJv6XkZjAhdUn/Sfk/C9'
        b'+OvM3W5Nzwx9YerOL356e2pB7eyZa1RJHrYm/ncVkjLok4/CKl02rLZS+R340SRkiNHZIeUmP1Ss+LlPYZv8h6f83ilK8K+7vm5l1q/HHC+d3D1syI3GW4Nfq8r9cO6u'
        b'aWuih3732UsvmCSb//TxyTQju+fdv+i74KpmbMQ0c0+1eqiq2Xb0Is8nFB5Bj5tfNNWc6xN618nqrU0p441fr/glfcdzP/1YFZw2xbHq4o++iiemb/xovOrxg3m56s2b'
        b'sblobNGmsiGfW2gmZ6z4IHr5d6fDX4n/udX/7VUvOPfZE9Z31+Xxo1/ccayscuHayoYlFh4TJu2Z8ffP+64rmLfpvf65k42qlkck1Hy88njNP2fcM3d8dXTYmqnD/74t'
        b'X/ak8js7959nJLeeK7DPSJi0qqRSveN75fExeyb+Y/SWXz/fpcl5b6n86/tvRmSlfLlLNZzF+8O+XuYdd8jpsE/oxbZIaFVzqJ1MPLSTTCvGjAhnvHwovMEFCU/BSQ1j'
        b'evKFfDzNoZvnxXZCDMDr0MbSWD6/H+REQfZWSwszNV7WYHOihULos0UWOn8DBzvai0fgtL/b5mAtXA9maAGUkuAQ7tOyN0zBa1oCKFtHlm6kHx2CLkEUryDTeREr2nkJ'
        b'q/AoXGBgBbPw9G7IsUrG5s14OYnkqYT8Kf2k9RPVHC7pQBBebieemAhVkmtfqGEtEwPFwxkxBF5cqurI1UnWuMMMRmEQmVeZ/liILZT/QdouTiWr7XWW8EgTYzLtssky'
        b'kSvDnAGCfJIIjTtiGTTRtgUe/ttJm2lJq9yhdXoi1VZD8QTc0CSbb0nCK1ZkUuRamViYYYNVMpmA2Lx1Cyl9IF6IlyugZTnwEqjhyHJnV8wLIEqNYimc3iFindcMdksB'
        b'aZiOORPxhA/UEwHkEXEeVs7nsBJpWOEBOXI8H0xWsTqfQCD7nRsFOh8Al+VbIRMaec+nOCxm3BeUzyhnPTQGGAvKmRIenKptomECFOmoQcdAIV8GhL4BcgsskbN2mIU3'
        b'sRZy3OkIMxIUEQvgojTMfyrrm9VQGE9u8VXMY06gkaAMlvAA3BzHWFU91FhDRK+2kYxDLJjuyWShITulQhiCp+Rk7cxczQcBFD/SgbtTLlj2IWvgGdlcPBvGhtAErIQy'
        b'BrOVF0DayRcqV0j9sFTDGgOb4QpZgXOgHs+wHIICghkHrCgMwAr5lqlYy3LZBQd7U/5Q/VZiSZbptFBZIKZu4CggDdhsSrlAXClv66VZ/jIy2LIlrNnYl7OXXjM3I8U8'
        b'hvuD/Vx8iYAgmHhJa5RkLFHpzGUp5JKXyZ25EZgPmVpGVV8yMJ0cjTC1dyTHSa8dPpokcsInOMgFstz5ek7afAheMTIKwtNMavUZBcdYQbTChByObCMr83kyErEFzybS'
        b'nSUZM8neR2ZGJ/EcsqDAvV1vpUqrM9lX8oZbm5jBcThNpjPV1te4bDT8KtRiZgA04T6VQggQjOGiCxaysR1kNcoQqS2keXfitTUmMvY+KGdwZdZkO7vAxwdJu1TUvqYg'
        b'SrIM2xLwhmHB+z9P08rsCUyA39xNgDebZsKYWeWSHcMplUt9RTvRXJKLWtOAaC1ak/tm5HsaLWty31JG7kj0no1MISmkdq9VfibX/on+HizusO0ilHegc60104ZN6dyY'
        b'5dTUpqatp55FFULl2shEvUeyQrN2ffSm6K5QKMYP0Ri1Jmq1qE1UnUh/sURYRkn0I7Oaa8SOLXbFsOIx6nEDiofhOv4ZllPj1dra9QiiqjeYd87sT1nKmTFv64Os2vf0'
        b'x9KOjMlEF3nBS+egRSnphEn/8O652roqV2vdqVY/gCvnN31BXAw5YMVq2sv2p5k7OX8bP6TuKX+qu/H8B4cxzyvqd/WXuWz5gQJ1jE9KTIiJ6TFXmT5XRp1KnnYljzvQ'
        b'WIB2HzBaEuZL/dcYbR0f1P8KfQGcmE9EbIzWCWITdT0hrR4dT4NYov5ao5MmMF/dYU73WAxTfTGYhxb1x1hHAdz0zox/pQPU+Q/qcHN9lqN7RinunHGHfNkCqwfuozuU'
        b'HgCe2xAEGljziLjDdJfAbAgisxsIu8XQDteGbAg6s3dXYLee+WHHsdxjxD/JDpuukr1LF0OD0LSdSIU6+3toHDTrE5LiohhRbLSagYg7RK6LpF4iBtPSMzPNiYuOpN5T'
        b'DnNZ1AztYC3mLXM+1OKBa/2OYg1j5mqhwiMiwtRJ0RERnMY22sFpY0J8YsJaSm3r5BAXu0YdSRKn/mU6dN0eOQQTu812ioqvdTvgaILcb217B3ewP8ZMj4iYFxmnISXs'
        b'juPHwryELv+J3bpcFhT7+pzX5Bqqb8ytfvHziL+tMYm5Q2Rak1GvZInN8f1VIpOxYrCaUsVzwYNJHf0xTS942Jlyw5zY9QxJHrMumsGXfU8D5DuLCcIexeAdIzrtO5q1'
        b'catZ87YfjdAEeIKUdJYfFbWzzVIWTGu5Ft6k854qpJp/1n1XTfImz0VA8dwuNlgscqbgrHn66hEB7CAR2rLII1STgmYs8fenihg24BULj1Xz/0tctd2mqm66djMmU2MS'
        b'FGNKUFchkppisgKc/FzgbBi3L9EvgkdCawAjkzoHWcpJSzbGnn0BJQ1dpaQdSz6PcHuPshg7fuQSGcAsyF9EfBIRH/NFxN3J2ev8IvmgKO1tIniPVckS6ZIGFURFuGJI'
        b'gtWJr5PwuE6CNcYbTLOYshIL9KxJWNMdcbckhonrUzAdbnQab5jvaK4dbt42D2VkJqNPox19fQ2MPrOhlFnoIUagRjsCa+UdEPt75gzUoXPt1o/STDJKB/Q0Sm3uGBil'
        b'VPrBE4PxtKFhepaopg8aps5BdJg2DrSYuhGbVRI3MJVBHtTwESzHFDxpJULNYG9mUDQlw6ONvyWHM3h8rAhNK4XYtX8/L2PL/pM/Wr0ftX6dz9oAMjQ2vHvG6OIb/d8o'
        b'f7EstCx0ScouuyNPDtg/4Mk+r0wKeMy84lPhyRrTWEVv3YFpR2t8z5gF+lZnGgVVTyWxa3eZ21qbmcl39DXcXbyDpAd0S4edOZf0h1VP/WH9uQFZvIdc/wt06usebv6T'
        b'dbsx8Ue5hirRU76v/5xM1ltr1seYx9xZd/YWefg76fFBL5O1mx4AY53L2M6qqRecfJBiS9RaPDqtWxd2ce5gfWVoWTdz7HZowvw82pfxHrjDaapDe+oXy9cf4nCmuz/J'
        b'f0KIMXjA130vlQeFxUb7XzLS0K+b7Ef6rxkdSTokQCbIR4uOVlbtAmK3jZKdvfe4T8qduymD3Jml542Rpjeix43REE6n4Rz+421pcHx3F0XJ+G6y+UGmoRa1fy3/zjny'
        b'EyKZrHj0UuHJcs8tpoyWfPjPsu/+fotsRnR9M8ZrcBhzXKhtSD5TjIPjcPkRSGXjPw6OYOsfmXWMlJ3G/xasYWayYEwbRg+jPGxUga4KwQSvS1AEZ6166Eb3B80LS7fu'
        b'Oj13w+2xG2l6o3vsxn8+jNVA7+grdDu0tNc1+waBHVpSXwFzpmLovAWkjF5MkunkM5BhlNGfHWYOyBiYYR9jrz/QVD7UgWZ61xFg3nFY6UfA1KAkRgdQADUj2w/boAFa'
        b'JUtrbOGHbYy9oW7QAqtApRov42UrejBDj40Ea6iW8NoIzGGUmXiY7HGV7NDIh2yTwdswFep6OjziB0e4f5sSLjvtVCnYJkl23ZyhUBqloWc+AhYKkNsb9jHia7ywIj5w'
        b'DjYlKejhuQBFCYvZOZe1m7UAl5XYTLoSLwtw0hJvsBvuuG+VM2RqqNEIMwXYD9XuSQx71NzfeaOStgFeIFt2HBxmUNlYA6eNYq01FG4Ri+nZ0DG4xg6Txg41FhqEgYLg'
        b'EBHw6kgLgRU1Dk6EwDlLepBGU6oS4OAGTOUptXq5BsGRDpUwwv1JdJJMhZSBrH26tAk2JKrxUqiPMzXc8xO1QijDSswzfQSuGzHhAsvibcdi4VgPuSDi8YgVAhEwKrGQ'
        b'nbBi/eb1uhNdIoQc4/SkWkiZhQsW44GxfqHGQjiWKfCyTRRrBm88hScoU6nnI1GCJ1bCadbOU0iNTiF1SXNX4AnSimes4u7ev3//zAAj4ZK5NTtRe2WBm5BEcQrW4XnI'
        b'9ddnhJk+jHY8z90P62eFO2IWKUSoowoLFvv4UikqN5CJTyG0hop4i5V4Am8m0ahvPAL7Eql3RscH6SjCLEsswyz3YG1LdcQmp+PnHFw3x4tYAAeSKNXhpK12FmSTLbKA'
        b'FKiz9zAxwpRwPKbA/DCLeTYDTKaGwHW4gcfwgve6baYx/baYYatiqwlkmwabQwPRtao98MZO1RDMnOKGhxVwaI4KmqaPw3I7KOsDlUnhdCZcwBtQZoSpmGoheJrIoCEc'
        b'Li7DAwoiMGbAASco2wDpeIMUKT9sYOxuIuulDIQbG4YNhCuQC/ugOWYnpss8HUkp8oZg49zegXBoD1s62GA7YDFATNkUKxesIwatmh8ucK+B8oELO9LY6jhstceqQeEd'
        b'aGxXkKXzPF5RroVSSGVJuvTyEXaZD6VOAGaV/cn4XUC+3AS1eJDWotxUcDAnF4tWbYRiqMNreFL0hL14aspY0iElEXAZ6/Bw+GisWkaKnGIbBnujIXMd6bqrfYYar4dW'
        b'6+1wEeqT6MqKFaPwiKGC+rj6GdnYUu8aqFWR/+ePJhMMz5nilaSNYSqRHesSJQVOL6GDgOwZmO/rQtYJ0sX9TOQeUDqfrTBQtw0y/F3HYN7DEPNyVt5slXlsIOQwUl5K'
        b'VwPNhk6mOx1L78Gj2pPpbeNJ4ehqgrWho6kPg0gnnwT54pyE6UzNHR8M15x9SLvlBvIp4O7n6xrC3ECmQn54N9cDH6IvbqZLwIIQ10WSsD3MarvKMokavSKxFi5ylwDf'
        b'hVqXEK2u6RMQzKrpttAkGZsX+vgFBrm4BoVzGmNhVAdnBLYsY25ILziFzRas+5dvkgTr3kpyFeEitzcjGyqjAIJMvIr1/uzQyJ9IT5NNsEGCTMi0ZOMDj24yDw1WBTJI'
        b'+iFTfMMXG/BzEciYPwsppF+LMXeFA1F6r0K1z1Bo8xk6Fi7IBTIzU22gHEvwaJIDTfRUxHSyvjRZmZrgRStsStyShJlmotBHIwsmu0cKX+gOwgXrULpkyUhj10GVORGu'
        b'bZYkUX0PDsOZMf4qV6prQzWcCghy8Q137Cxey4SVDiawF65HM08LqCGLS1Eo5IVhXjiljW7FNCMnkaTUjGWsby3mE1092VIUVi4U8SBZU/rgQXZj6DpyAWSwBJBu9xKI'
        b'PtgUydpu6yqs0jvxiAswW1Auk8haeCCWOa+QdbnKSntyTI+NsXGTCEeSYT/bHnbMmObPjmBJSU6wY9g2bOFOJw1QlMQdG4wE+WDTHSJUGs3lSe53j9C5i8BZolwOE8yt'
        b'ZbYx/ZOo5xUWY4UFHdZl2KRicP4UjJ8fjxoJoyDFKMYPLnK8sWMuo/3b0cawCFpNsEyCA7jXhTf/XmtPZ93xnhm0CObrZFaxo1nR4Zg/HNIREVjNEYkKc2wJK18YHl+A'
        b'Oa5B7PhSsZLIfeWSLZyBUyxNeyyUYQ476JVPIKOkWYRaL7Lv0kYmK32MPye7HrwJD4pQtSqJV7muN9GgdDzYZBE6IJJXS+EaWy0i5u7WlZIMUTp3jUiDikOhxMjUdkyS'
        b'J9sxyU52iUx1prZDFqlxl8bB0kTSPkGQaoyF47CNyUJOLv3o4buK7i4HMMd0kgSnoAZu8knTDC3byAi+pMEmY0HC+tVQLrpiOun5R2fGS5oKIjzU2d/1Dn0mvrdnn8vT'
        b'CgJGlY94dmPxzdWtJ2du79t45vHmKc0N18M8iio3hCRF+2f2evHZStuQrQ3lRUuG30wZP+TRvrVDni+4s604+9lp//q25alXX51gZVPkX1xtFi2/nnX4i5KqJ7J8dj5l'
        b'2TLV582bf/tgtO+xorLtWcF7f/3HBsfcvb/fv/WC35Tho99aN/FCn2FvvZx/8JvXX812Gn7g5vOWRsPv4pWzR8udd7o43vrAp9r4zsYvnv156E7fwr+3+v04e8ChYV/C'
        b'M+snWqmcRoxvqHpq05fRxb8WHckvfOulrw5slGqqV8Vs2x41LUTm/cz5W+OV9t8P22oZfvrF3Q0Jb350NVH94thP+vp5/zqv/54BGu9fyit2Gb3T/OvVJ2+G17wzacL0'
        b'pNPfLln41N3b/6ia/UHebLu6NzzVGxeZVvy8deGn7nd/8Lvf/OOp6VffufNe8bmafs+/8vGvQ75J629VM9ki9tuwk08qv/EfOeTUIftBE4OjdpjGl1f9/KnC9/OcgOVN'
        b'18vybIzqtoxd2rDW8fYltVm8zTDNy+qmNxufeqt1zsZ9pXvnfGD+wrnC5eXPvvPR/g/zF8UOslx52yv8n5vtD2ZH1r727vT359WMPb9MvdP+o2k/vO/Xf0nyd59dDT4S'
        b'fdn/m+wvN743udVqfU7zl/537AZ9F+i9uGG6V+PH23KWXXg22OvxX496984dqCkY+t6aUS0Zgw59smPo2FflHy5NyI0bOcS3zGnnS59k105MbvxYfVGad1HjOMPkWq3z'
        b'x8XxjTnb3lgkb127U9aqXGH0tuy8uDXl80d/+WLo9Oen/7pn/Zu/DU2efM+09M4QdebVnAETUgoSU+6WfZ4ZnGj7rWp+5j+ebot+69g/326ZWjJK3lTuP+jOb68mWvx2'
        b'7xk/409WuWtcShJic5Uj951fWm+5yuyNml3LF3/x1qffXD5z877xwG+tbvt+rBrJXAocoNKm3b8iwDh5PnevwJOQl9iLjvOLe2YxM9aSIdQnxtOL+Y/A3phdfOmyxDq6'
        b'coX3Yd4YvlCyFvbO60SirvXDSXdjHhfy2VCucwE0EiAVTpnAZSl5JnKeEnO8ubl9PU3w4cvpUrjO7iaFEFmlfTWFJsgkyymW9ec0aNXb9U5CPvJZmKV1EnKKYTqrHZZi'
        b'vrOeboTIs9LgNdjGnXBb4HySs5ObCrNdGCNOvulSMtvJulHMHSeKoXqpM6W7y3IhqxrkyyFdcp2DzextJ6IiHPFv93UQrBZh5W5ZnBqqmRtJkCM0Uu8QKs8Et0u1CoEs'
        b'a0P85XhsGJ5g2WA5lOJRZ20xFESWyIc8aazNkES6Po4YOLPdT2j5eMm1L2YnUqF/HJYs1kCeyRYLvKihrnxWJhZQLXRz3LmsgJu7oYxZfOdhbj/ndnMvNW3nKwQbXxmc'
        b'IKU4z9wfBsNpU3+dnTmYaCQZkEm6vBdmyIgAS4rG+nyCKVndKam9uyujKDQWrIKhcKxsPVH6apl3FnnvPNQ7B7uQJChfmvGgqYISb0p4BU9iBVP81bFz9QJILKRoJZDK'
        b'TezmYrLF79MTvt2Eq5T55hIeYxVREEnyYrv7GFzFAupkzfzHQjGNd186EU0aO7rfnJ0g9cNDm5hlHS+QTepgu8UCa/FkN48SnTcJpK5gfQoleHkSnTkdvZfgILZpPZhI'
        b'zW4weiA4PQIucbca5lTTe3oXtxo8j2Vs/A70X0e63k/HwmOFKVDgJUsYDoWciegoXMFGIlNTxjnSFnB5sKCMl4iYTcrLRjjJ/sL49n2yHi6QfTJqIB9aR/AQpLWLFIFY'
        b'Qnn5jo3i4/8cuXuug1hhuoVJFXghkVViNRzFFCpWnIBzPYgVvj6sr2MnzsDr1COukxtTX9wvt8HWRcxAREZOuu0DDET9bLsbSH3JUKcLzyKxj3+Arygkwg0pRHQi8/I8'
        b'n/tVeHBTO6leKuYyVj057leZ/zsuOCr7/yIC7b/hEHTbqgvWJjODyan5sKsZbIxCMmGMMdaMrEghSvdpUBl3AaKgdZbMUagvJTMi30jkR37fREYj1MmTMkp8RNlmOM0R'
        b'/8c/03dpGjYS5fizpGQfMhtZX+1TZuyvjUSRxM0l7qJkyT/JmBuSJFFz2n25JP0ul0m/KeTSrwoj6ReFQrqnMJZ+VphId+Wm0k99zKQU6V9ypfSjwlz6QW4hfS+3lL6T'
        b'W0nfyq2lb0x6SV/LbeRfmfdVaAPmzBlnXyezXJem4sZE7rfEfYpYnNl4+msSc1mK3tbu3tAeutV+2GH7f9bjKpMOJZyvK6G6UF+o8XrXJ2bBLCAfnXqyYM5+3hC94YOa'
        b'SiWy+LWgPzh9peevIsMc/tOnr+++LhlwV5gVk0gpDCPj4hiyageaYFLAWFqyyLhOgKscrCsqiqMRRjrER2/tlih3gnGMiFiwKdE3PiYiwmFNXMLajSo3LTiuzgEiSRMd'
        b'kxRHvRC2JyQ5bI3kvIpRsZQKsTuFccdCxMazB2MYhoA2aDRawyNJOUKiA8V6coiN0jw8ayGFPpjs4MscEciI1MRSAFqSD3VKiHRYm6RJTNjEk9VXzTcqIkJFoXJ69N0g'
        b'7aNrD3oZG++QPNGNsmTPJs24lTZm4vrIRH1p291DDKaorRtDxWV+TtwJgyRAMXI7NZEuJnedOiFpM4PQM5giqXpi7NqkuEg1dzPRUttzRAeNgyONiXchTUCyZYAr2zeT'
        b'j9GJa91UrBN6cDOhDZoYresXbb8zN7T4rvSU2t6PSmARwZspnrKhNDt1wB/QO4qCIXpHM2543w2HoEFneCe67QlFP8kSigZywzv1YZyNB0cqDQRExEAbjYnArElJFCfW'
        b'ZQ5kaG2SDiYyavW8tsUDSwcM9uk9cssjeCEE9kH9HChdPts3Ec4ROb/BZFqQyyCsoLLYXLg+BM7g+R1w1tojiNshm/b4CoWC0FeKiPBLdlonJI1gAsOmOKbHQ4pjKKXp'
        b'LaCxNTRmyVgYtkGO55K1cUepznLBRLi73HxmREDsmElCrG9xraRJogXNeXfk01Ms0zysvV+YuPb7L0uKjRxOxQx1SfkoPKj3pEyncTM9X993I7Twk/P552Nn2piN/9zs'
        b'2pC+jz83bv2uW/m/O91/3O2I3c2jLWFR6WPC+++xW5Nw6Gt478u1M151+fr774cF1Dz50vM4/FKdwvH0QbsX7EcvOzbgq+e/VCmZlAJ1UEiU+Q6KD1F7IGMH0XwGYhFn'
        b'OKaRSRlM9ZEGQS2NByBtxQSY5UQUa+5JgInFywaPeCMCWM5W4hpHPK6hVlpXR52ZqhcWyqABz1tyYSxrIB5u15FMiEReQnUkvBrEAxWO9Vqm87hfNkaxVMS6gUZcACzF'
        b'wpmYw73toQiKqcd9lQ2vz96dPlr1YZ3IKC7xBlG6aJkGYVtyB5UtGc/otbaj2MJ8w1dgYd+u0i6XdPE85GzFbHUiNT8tGwX1Wlm3mBTbgBM57IVS7UHeHzqUmNLgPzZZ'
        b'mXRDA5u7SjdEvvFi/MGSnMkSljLm6izadHUi0Cel82XRg2w8wIlBJfEn2vfXYvKxSq7lO+q6vwqpNoaOensoCPUlJVvNarLXdEJJ0EXK9uSFKMuUPVScLN1c78oNbK6h'
        b'0fFa8NTOyOxJGr7ZRrPljqzN3rN954R2QFvvaYeKXhO7VrN6bVwsSYVz6+rgpmIofOTa9W7sCTdv+nsOe6wnEPcOqWrbZjLzW3TROy5SsGFNNCtmgjqKfkHWfoNrsxaU'
        b'vscyuM0LD4hggHNJm+MSIqN0tdc1iMFEKaKpHkCObhtal15NUmwih4bXF8rwjvGHpZozJyzC5a++Gv6XX/Vd8FdfnbVk2V/Ode7cv/7q7L/66hLvMX/91bERDj3IVQ/x'
        b'8rgeXEd9YzhdDZdyoqNcHJy0w9+pk/9pZwdZ5jJnWCzpye11njqS4Xa3j+E/4+G6mAqyfFVIHuvm0Wm2MM9cjpbLpxPJMDk28q+11OywcANFaOfepmsMLwefbrFRfyB7'
        b'yYUOxLF62as3p9Z+XWMsxBkNosf65lfWzhTY8XfyWs08KNIoqRPACQHKMW8sO8HYuh7OYpOHhwfWEkFLkHzJfjwQqvkx0TzIcw5yIxIDHBQhLcnfAurZccl2yIAi5yA/'
        b'idzZKyrhsBecDmOvuEFagHOQL30lU4STo6fCxR0qOctpJ14PZGdkeHHkTCNBNkCcBvV4nB0/YBumaMjNhkS8Alenku0eD4hDsRIaWH6LsGW3ZgzZ6sQEerCTA1fWIXdu'
        b'WKyEExpstlJjxhJSejwtOi2azEoyAKpIzdh5fyw0Ce7YghX8rKdxwURzbOzgxeCFV3WOjgd3Q462kBbYwEuZ3Jvdc4eC5doiYluwtoiyETyqOxtvQAEvSDGUa0uCpbwo'
        b'mG0L53Xl7xVBSg/7VTL+4uHdpC94hgps4hliAbSwu/MHbdY1Sg5W6lrlABSwLnUjYvE1ZbKpZrW9XJCZiu6Rm/lBVx0eGaO0UFthGdYJgsxFnAH52MQqPxkzhtBjHqXl'
        b'JhdRkJmTW1nLkhbTt2oS9vhTkTfU0or5/NJzZCIFC6QXincRKTsX06GViPIVYeRDKbZiNT2dw1JotTHCA2uMLMivQNiHuVMdehMh0cYKzjhheaz18rcFzbskg380/7Ty'
        b'H/4bYaa18Tflr9/12eW9b3abj+yJ4OfP3Wjeaz5prunV11Zda7lk8kbJusfwoyP/GvLPOYU3bv3+0RPb3M5EjPywZGqI96rS6X87nR+W/J3zqriPaq3HT1k7Nu+bHbdf'
        b'fWy82ZMaL9NeL69oXPtLNT6PbV979SvbZpl22Ol9lflRr9BnDj+9acrL55+eONezMnDsnJLgi+5ncqe92nr6SF7hI/tGDhqIb0dWvfL0x0eCnn9k5rjmnR+Muv9jn9NH'
        b'n1NNbotoyn82YvSSHVd+ND/yzqYbj/atH3To8IRDEybNb9l+YsjvH3ndl032XJQ+Y5SqDzuDcCHiba7O6I83HZ1FbvVndmjWP014+BFu9w+aItOG384aweyaHgHY5qx1'
        b'gbb0oMK0uYvMGAu3M3MhXoNLy/y1Ab1qqJ01OYq9FTQQ9zFYADJQzhoJckgXMQ2vQgm7u3AxVulCZwP7ynjkLFyEs6w0MURfaJfOR8az84ttai66VxDtqd6ZngNQiReO'
        b'hJhgjkRPOYyZEC7hRTyhUeJl6j2QI0TY4xlI5yT0UIflSLSKzeMpdkOGIE7CwkjYz14zX4L76B0FuZMpwE2oxqK1/dmhgOeE2fQOTS+L3LHDYsmcG90PYwrkdQ5KJYXL'
        b'3ymbi2WPMEXCZ9cSDT3tFuG0gPvhKh6BwkRmccfDGrK+QC5k0sIUCrN34CVoxBquSZyFAigkbxqRN2uE4SuwwhPKuGpyA/c9Qma1OdF24bxgQxSIXXa8erlYv1iTvIXm'
        b'VibgdTIhcl3hIHtrt6MVuUNygoOCMyWXJzOllYOfHMXq2YaUpUvboWHgph7CLx/g+yzXEOGXaRNRBrUJ6whq57Tk7F/3qQWU2k2pPVP6zUQuMYqP9h9Kb8yI4CUzsfOP'
        b'nGghErmvuL+jV2dnZpK/DlaFBU6ad5Se1SWdFBLmn0iqc1CvhJTo4xsPkKvHetZErK8a0ER6KorIvI7Ub9Hrfl2grG7LVwf7Bt1Wrp4THhLiHTTH1zuUQ3/qIa5uKzdH'
        b'xsbrgh9p+NFtsw7Rgcx+qY8H7RC6mdsZCoshY1H7JVOyWP146Qb8f8nwrl5INUCZdgCZCNbGZjKK0qb4zVJhZyTNJKrofUn6awic1nJra0uJUsJJ8gn3Tbb3EU0G9RGZ'
        b'8QevbMRzXaITRGHAfCJXHJHHwgnI7Obla679qxkjdqaIoyBeHMCrQq6F8OLXFMjLlPzQawroReG8+Pft19YURDOqN7vuE2Wrv+4b1Y9c27Hr/lEDogZG2VcoKflchiJG'
        b'jBoUNTjdhIJ4lhqXilHKUvNSk1Ib+hM1JM/YdJjp8CjPDAoSpiBa7oiokQzuypgRt41OF6Ico1SUmI6+W6oslWIk8mZv8s+61CaWf7IhKdqUmpaaxcijnKKcSZrDTV2i'
        b'xlAQMppqhmmGRYZNRp8YEwbbRVM3ZY62CuZ42ytGEeUe5ZFuQsFD5cIyJQs2HHvbhk6XOYzIguG+xUSr743pJGd2f0DLvdbxoXtuRGidHKtJmKxJjGJ/x3h4jBkzmcq+'
        b'k7dpoibT6ePm4eFJ/hGpeqxKdlseFBwSeFvu4zvf57Y8PGT+glrxtjTXm/w2pVmuDg4KWForV1MzwW0jpmveNuWIv7Hk0iiGaMyaP5OtJ81Wrj5G59xx+usEncVy36BQ'
        b'DgP5J9OaRBa3zmmpz7IEQ+cumnVv9vrExM2T3d23bt3qpond5kq1ADUNhnVdqw0mdFubsMk9Ktq9SwndiK7gMcaN5KeS2tOvlRjymDqWYiuSBgoInjMrYDVRDu6NooWe'
        b'M9uXlZD8XRC5nS58IdRqrEkkibp5jCO/yfJHE6sV1Ys5PGM1Lat5qG/Q/ADv1bNnhc3xecikPMlafaxTle9N7PLiHHWCRjObaS2d0whIWBeoWcdS8qQpSe0pkQJepGlZ'
        b'dWmPewN6rtQ9W4ONp1J2SoUON/VlA2lPUl+h33ZJZBJLZKy6md7rOXPPe85/oqa3jaOiYyKT4hJZ87O+/H8vpIR7mJ/bPtx4NXME5G6A65fHLkz6RsYiTXauGepP40zi'
        b'REEe+qK3OC/mjQdEmtw2odSviWRMM6HDUGAcCzmZzyFbO68lbrp3e45YuEkqMY1caRwNSgFCqvl1A3LAg/KqNeY7tsbAtp2k37vp2PyUliUsqFucg5muXWlYHYtzEHSs'
        b'pByWLcZMH8Ng9rAxDO/uNTZgyvTl4cWxO6I7GDQ59RA/dqIr8gMMmKE6fmCHzYwIgokwmsndH3R16DJrHBzneqse/BiddX/4xCQHRydNLD3DSp7oNsHpIZLkE9nBcY7P'
        b'Hz+snbD0YReHP8qn58XEwdE37E+94fmANx52XaBJdC10T7Zirb2LG4Z45LeWdEpHaNDTm3Tz5K91HTab1bEJ6tjE7Rw72NGJbsmUzotuyk6GzYdOdKumz9CN04naip3o'
        b'juekcms/Zp3gNsbNY7L2EcPJtJ/IerBHtam2fz2Bfc2T7qliHKVCWzUDGBS8fUZrGAxFj83DTiomd4YOYJPMMKKENvS/xzK1w0ZM1hPXdkeGoCgN+kN5A2fu9D9yj3EP'
        b'UvM9M5syh4DoyEQ6oDQ6ZrYOQBv0SLoH/AFqeiXpbI1Ua/0HOhBisNZxCI2OpnVNiutA9mYwqTmzwrznB4csXU2Zh4JDvVdT0plQVkr92T2noOuxkfgixNuHkURpcVt0'
        b'/aZT37RGY8NH3e2GZHY4wVNot/M6dVlTnHp0FmA9tJnPUw0nsOuyxDjx2ukeiY03DI7AITiIeKrj4V0fGe/gHR7Sg0E83iF0a2zijmh1HOu4xAcUni+IPcwlMmF8EyPj'
        b'trMXe17hnHoes1rsEN4h7ZAidORru0QPL8LPpnqoUSL3fegALt7p3U7QMD2uWiylbocFpHm0MpRGN3y7pGu4T7Scju35Mi7NNdFxCfHraEp/YFSnUolpNyHKKog77bdi'
        b'JaRgiT/mY6FMkLBKxLxVjv2dmbtDJBylvoj6OMMiuCxZ4uEt3N2BGrbC/PGMxsICTyzUYZn29uOq8EVshgyqC0MuXiE/TZAFac5ywQLTJcxRYz2LSIOsVVP8O8aILeoO'
        b'/tkJ+jPQyA9uQLMkjIc0S0zH83hAJXGb80G8GMaNwMwEDJVweQZW4U1eUDzgR43HzHAMB0NnBMGxJMqRAxl4068Dwmt7YfQBNJstLEIoxquja1C4oyNmY647ZrssGU1x'
        b'PTlqqSu1+R3qLQ4yncfLchRS4YQmmbRCGdTpEElnw2F2kpGzQUH1/gXznCPMXxnfW2CoFdhmD5c6ApX6jIR0N79AzCK1dw/BzICFPrIQyKKwBtgCp7aPFKBNrqRBEy6x'
        b'w71uC5qTJJXT/otH5jVa7p1pvv+NqSWDN9t7HLlr81x+3JOvP1t2dZzl1UH7Tfu+8MFPrncCv/z0+VHvvPqvr9NmOq5barc3RbLsP/W7l5t+Dpq+qv/uE6qi5WNsk84F'
        b'xJVuTN7a+PKuD1Lf+2rh+iKXXwMnjPu+pNdLbu+/PWokvJP30pUBC1b9duHQk8Z3R66/rJ7qdNTkxXC/ZW3RR3a/cnDzhFd/6PdMbMi82362q1ZfltxunB6osmCmS8im'
        b'sUbObq7cUbp6ip/kAechlUNNnrXbzbGUKQS0C3XZMLYzEixDZJ6mMcyRFEuwHpj3he9Qnf/FZSkZTvux25NCbTp7jUzn7vKX5ybSUEpTJ0zzD3Zdtp4jSMLJVcwsPHED'
        b'XOvgH74UKwWrRbI4Mgf2MlvtIqiWUQcMODe1i9s8XMVmbs5tJaP9ZEdzbm8LatCVzSWj8whzvrAndxv4E5mLDMIVQi0e4u1weh0UOLv5Dp7q4tQZWLIFL3KH2st4I7iD'
        b'r70IFG76iBeeZK3sqoFikhWdfpfI/UARL0HxPFU0s0lj2UQg7ZMfsBXKSEOsET1dIjuBU5j9WxY4PRbe7B60KZtd1AqnkFHXVjOKjEftc/dNJLnIHU4pqp2lJJcGUKfW'
        b'+4a1oY4Yd+otoiGrcnInrLnAB2lhg889rBb2Z3DnOJngbaPVDHKvJ1CsPHLFUecMZaind3Z7CBm4K2IctVSF+swKuS2n5K235ZTHVWVsyKeWe6xSB9bbxlq6b/UTooEg'
        b'eSvdfrJA0AfJc/XRXKtAWnBk7wyrGKs/GQofQ9TIM4bUyFlRUZrOhNW6bdSAgU8vgHXXRmMcJlPxcHKEHrIkwsDxvYtWnNEDbVFPye6OpV3JFzn3MNXS24XURNqSiVoR'
        b'/qGUI61Yq6fn/SP9iLNz8XcNcOhGahxi4hIiqeHAgZHFatkwe/KdiYzvxDzXlXq3p1J0UhoMMeMmRm/jEnGinkx2E/fy7MFtkzwTG0XFufamaOfv43VwcGSk8rRqTFwb'
        b'FjLPzc1tmKoHQZN7QDAX5Eg6mjpQSutT5pyZXABuv28wPf077RSY2iGg9c7qTIhpMA3HEO953vTQxnt1UHjgbO8QFwedXsJZQ3v06GI+xz2zxyZs5j7YD0hhmyFVrwea'
        b'1gckR//Ta4K0hR+kqOnB37Sj2mBqOk5wQzqdA2kV75CgWQHd9TfDbsoPqdPpaLx4U+jZlOmA1Y4bOi+IGhzNCLMjIoIS4ulK8QD/7W2J7bkzrl3aRpFx1GeaLhD6oRuj'
        b'TthEmioqsgdH67gkbjpbF5scHa8b+WRqRlFPHse1CfGaWNJcNCXScLHsW9LKPRaMJ9PR4KDqWE0tt/SaDdFrE/l6YFjFCQ32muDh6cDZbnl9aBlctLCh2voyCwCdm2RR'
        b'NJhOTJKazTU22zlrbY96Ht+VJjuEavUqHdc8dUXfTnKJiyOTL1LNtSv+sOG1RaNJWBvLOkGv5W1WJ1DKeNqKpGm1nU0mAh/2hhuzAxOjQxDR9yI3b46LXct8DKnCzeZT'
        b'R9d6w3Nnjpayvp35lW7YDo7kt8rFgW7bDo7B4SEq2hl0+3ZwnO0d1MM8dOoQKzBB5fQQEQx6h61Z+qW+C4vSgxxBOymbJgaVzSHcex4PQIYnkcjhAuZqVUrJcjjkM1GI'
        b'aUYLQphmZC247zAf038I5wGYQpS4C0TJhHovnZKJxXBzHoegqSLXh3ReT16QKkDucBP2nhfkxunxXsjFIaoiVg4I49QF1VZwRKeeenhxBVWnnUI+1DA3/WionY05Wg4H'
        b'SvARpgUv8Hd1WuTj4hfes55KlEI8CocVAlzw7gU5YaM4ck8GHk/QKalQsYO5KpXC8aQl5GYi0XQO/MnsODnOYLhJ+XEWOuqRLVQKYbJHH2zAs1DCFGA4utqWK8ARRB9x'
        b'EWcEQkoSZRDygHPm/gzpx9UvmKrAPBEjLMZ9ZiP7Q61Zu9I5E1OxgtyotIF9UB0GJ6IWQtbs3XAY9sI58lNF/u7fuA0K4fTsNasoRA9kz1bHLly4YZV65Aoo37jeWsD8'
        b'afZQYePEFOVkqMdCJTZvNpcELIVGCVtFdzwHB5LCaJlrMV3osWyY1R+yZkLRGtjXqVD7sBJLsSiZfqQuXhFWmOEgQN3CXnYzsJCPmmtwjuSbbErGKB6BCupmJrkm0aHc'
        b'ZxWc05sDVIuwdL0W5mdzUlIYFm62sMLiMG3jdzAWUBsB7SEdEEgubTL34EBIhTMmLB9LzOxLRu51vMhoSeDwLvN27CUDwEv0rbCOHQoHoFHAy5BhMR+ujGc4PHB1V19/'
        b'HVESVEZSB7c8qFvAxg5J2J8Bk5ABVWKk8YNsGzLIs7EkhCjX2SK2bbGYL8aycW5PFMnj/h0Zl2gqPu266SKfJREdk4N9SijtMxJP20INnOprKxOgPLAXRV6YlDSdKgmY'
        b'u9EAcpKEJ0nX5OKlqaRv9mI6aVjmakfU1FzIXSNgRoh5iNkoZpihLka9OhhmAnxVfq5uOn4TfzzVCZFJWy6LzpNGIeDRJBsogioF9wY8T+NndBATC316Sl2b9ACoeHDq'
        b'IX59oHWnyMaU9ThIYxaf9IU6g08s5DKfHQam4oSXJuiod8ZCCh7oRL6zVkbZHGP/deY5UUPUcWF19srAhTfi3/CwHqVaeMn17/lHj0/wfapy50/TZ/4krMqTMk43iP1O'
        b'2LhPc03au+LgiQKHTYN/lW9PC+o/Juabw0/9bf488WLhT7+9+e1XjjLfWz7e9YEHcmaH3er1zv7lE/ePK3/lJTPH8ppqx5YJT5195bvB/c80e9YtXzm6+DnbUxW/jnP+'
        b'sq24/p8fZo6PVr7f1ji0X/xnqYFLm5aWTT5Q/fdlP/7yy8ZRdv6PLHL+sCbu3Kf7qsTPfsp/adn9lzPvlVY96b5+xgnboqSXW6KePRF+Jf7nkTv8ttkdMzsW+cOSAa42'
        b'9423ud/5cMS9J795q/HHiXdGv3Do1vefWa5v2/n1pgEffp1qFnLodsLr++1+bH4rbuCdFxO86pv/Nu0TtfLiob+93/CszVc712fMmrNuyratW4yz3nli8f050z7bYXfP'
        b'uKLqs15vZpxfFnH8vWlnk+/MSN514fWq9xf9sq4xqXlcYsi6fmtTL054du43w4v9g++957Vx5ZePXzzy5dbtNfW/1/yW7vrcr5s0qUUh+5+dlVOPj9jdqwl2NvpwXMBY'
        b'5/cTL9z6uCFv6WNfBfx4YZVwsLx67hcFqr5aw4smvN1WREbHTTkzFs3bw5wlTYEhA3cKXJq1UKKwpIu4C94hTKcuj3BkoZbGZD+UcnaIYmlhO7aCoFwGJ/Ec9bNs6cND'
        b'xE/haVOdyWdZCHezJM9cYwaooSvJ4pnTzp4yDg/pCFQGwyVWNmyKxpR2BAYKv7AUyyhNy3U5D2EvwL1G2kij2dDW0dAl2HIHSjL/4azOvRKvuWntb9gynJcxFy5ChjPn'
        b'8tgAN7nn5i7gKAKmeAGqnTGLiAHXg32peVQRJw2zT2QNA9cwO5aCVmDFFC3ryWk7Vm45NtNgML1pDTNt5dy2NiuQWdZmkWyPaR/oYFbDLLmeCKQVjrEKRJIlIa1DIL1g'
        b'bj11h8wW6yCLe1a2GuNRct+F0suRvpG7iKRgNQG8fXLj8SojfFHB5cROdrlKkbtRVsiWOrspsFpn3pQ84ATsTRxN387HFrzoH+ALWV1wRqHOVUZ246sKd0wXWU6bIYMs'
        b'1XQYka2FDJZKOKsQLOfKpuFxaGRenjFroMnZdRoW6ahdRKzz9ON1SMNUoLwYs6wDXVWkGNMkByIN5KtMHjqs2eq/45xXoAOELKUiowHToLDHbLq5aClZS5aiOfmnkKzJ'
        b'PxOZjWhuTX0+FffNZHIW4W4iSilmEr2mkeuS9nsWSy/1kbGYd/LPWlJoY+Jp3Jm5EY1Es5G4+dGSGvvum9P4eolGp9N7O4YZsMH9yfj0dlua+m+d49cevv07hpX/zUBs'
        b'uYGw8kIjXQyeAQOnkOr4sQET50PUtmdfH7rbM8sfdxsRYhR6rx/Zw3r93IvoplWERMcThVbzR+Y9ZkvQ6i9Ue43UOCwJDPgDJYUi5gzupqS4BDG5bAekkvWnAw9lF9i6'
        b'nMU6/DIog+z2+FGsgHoLW/UifvqVgilwQ7/b050eWiBXv9sPtGQaSi+oDqYigxz3KbQiA9ZDHVNQZOHYTO+RBSbb3S15/k7yx4+6q49YZTQRD2ALS8EJLhKJhuQgh9N4'
        b'XBAHC1DoDOlM1xiZCDWdTvbWYaujHV5gmladmUyQC2V2ZkJEnLP/CIHHq1yFIjzMUCsFomkdowE1N6ENLwxgHldEeTkDBTT4ZB0WCO6C+8rFHECzZSOmKE3VMkgNJa/V'
        b'EgXN2J4jpOXAoTBnlRMFM9kuLiNCeupuvM5jUq6M6u1PN5kgI4pjKCj6SuYTyT0mnh/DvVAcim3TME9ON1sBClxD+claAVyKbEebIxupKdbhDTzH8yuBIk/9MZ8aDs/A'
        b'y1jOXtyK1yK1USc84kQN5UMxA46xtnoESrdr41VYsAqUrqBhPMWsfnOwSqNk7I4kTyKstjlhmoLdMV3r3+HEsW/cDDyHNQy3bWlkYCjkYekivBKOeXiAQtmZBIt4CQ+v'
        b'YB0QEl0g2It355t6RFh6Ozhw/XfghuHCXOF5TyshYvb+6TP4l+JYGtodYWwZEWFW5DBS6MbVrJ+LDoKWq1lJZp9wQtglRglR4j6pv3BSx9pMScM/pacClApnVpQ6IDY+'
        b'ulbL2yyPIx+6Ek9TU/9KhSB8L7FZw9SOIStcmJczP5401QnEWMxiKsQQrHOZMIlsc1mQNQn3Jc+cF7PFV707HlIHCbvGWEMjZIawmhU6mwt2gofMdEFE3PoxJry6Uzb1'
        b'E1yEuwHGDhG7Ti+KFxgqYD84Y6ZFIuwv12ERciDCODXv+jbXoVpFkiqR0Rp3stvXMtXXcgIcJre2WMgEWR9RYTsFLiWwrCxWUHNDir2VQ4T5v0ysBF24VCnRkyrbT4sr'
        b'oHzGFDzF0pITjZTrjURnVGGd+xjM5S/Vwc1J2ETeMhZko8QdkD2NjMYLKpFHZ12N2aoJogxbKdgsSErRAVJd/62OXE86Uv0M3QBu0V/PiUI3znDadfWk69TPi1oOzhho'
        b'wVRlMjZbSbT8ZM3I8LIjE4Q24BqswatKTAulKguZWWTu12GZFi3wKNHUmsyx2dgZz5J5V0IeICJUQRJdSi2M4ZKSUoDuFhYKC7FoK2+PfNveSgGzHZ2csTGADH4/aVkS'
        b'5rH0JuAVe2xy98MrAaLPcsEI0kQ8SIG/Yn1vJhhpJpE57/9OdHS4b5x9uPVv93/64p/Hyh/P+nJLhdczEVMiA+1HyyH+URfL1PSRQxWzs4VB7x77Ye6kE+/0e7JQIQ5I'
        b'l7/5ouuIeIdGHxOvDxSz33t03xTHFXey07023wlPmnixZE5g244Lu3+r/yw4LNPvkbfOVYRW/3Jv/KADUwcNHJNlGb5/0J0Kd2Hgud/y71ra9o7YuMJ2ctiar1rNil5w'
        b'vrsz7rF3LMLSF1Wrl2SPC7832WW+wuWjXaFLB7nM+9Ql+uyow09v2peZXZ/+8oc7qt8zqzt8Zq7XItwQdnixrClxUt3ry1b4hy25MnL5OxfgxZbJdhPfNT/vurzfitcX'
        b'vT/0g/WPHm7+6LKNxaX8Dd+tLCjPSJv+8nXnD0bd3rD456/3vjNzTvP0yjEfzfEYWBu5MjL7Rs6ilrNbi7Z+dN9y09zKm3tn+D071rIw+6nHNx71fKzfS5/t9v086oOt'
        b'S3O/3TM3YOCEY2Mf++mlL36f+Xnvo+vf3d/rR+WwCVv6WIx1/37F/smpq20TnnsyuOFgnzubGs/+VJO0ty1ldOMb9d9OuP3ohp+Ovzz4pS8bBtm98e35op8nv/3SzF8y'
        b'Hg1abjTO7c1cB9uvA6aFXPo26Z8fhd4p+zz9rZE+T7x6evCaeYuesE8pfnKlVfS48EffKnzu7wvdnnJdtaBmfN7CnaeGPZ33/dUnqsvsHn9b/obFG8OfjtttY5dk9sWq'
        b'Bs0dL/WQuLaXZYNazRLHfjFz8v4nY0Mnb5Uu/1LUcMXhq2mror/pOywhcNILxt9YffS7uv/bm1oVfsGHP3a3THT/qPzXhJNvHntnmPqR5/rvPL70sUv9X7/57id3Nt4e'
        b'dvWjt1LNk8J+KKw/WfxjiN2Eyr2btm391/hAv/zjr0+JhJjXlrmVmB35wv/HK18UvvT9yobrkT/NLD/U+0a/T6bf+sb4Qshzvyd4/PR9v8+ktbc+n+n5+/ScYx8k3D66'
        b'd8FT241wyPKVKOudu2BjxLWqFU9tdNr6+fZcy9N2c46f3rT0tyCHp94MH//Zncdz2wo/VY75+IBnxf1Un+1Wa56w2m71zNf2m/Y89bfaI195tux8//gHmoxrJjffHSR9'
        b'b1Y2/+r51w8t37AtY8szT+4Z+EVVyEC715v6TjFfdPe5f5q82fKp2sL+1m9xgwqiX7fUHPrbVrPXdz9z7fG7x80mYub1ET++kpj1rbvp9ZxeW30/q//U5v37j68c9rTt'
        b'yuLnypOyvt1zwO31x8jnz9wmFW/NcmxaenTM9Oyi+7O3/3r/LftnL41W5P/D/YuSXbIv1v2y++kJxkEN/T6x+8Lri9jXTLdnTR7TnLVHks2rMH1y66NuL4S9kvqP10YN'
        b'f2MvnNv+SvNrQ7xWfvXkx4//0/TtZXlm03Z++sWW1n+MzpryxfbXVGHi381WZVbs3qH4te+heSG3LmyehDUXdjwWsyW5ZFfyN6vmrpz8++jmO09PnDbwo1fnNdsGVt08'
        b'esfi8GMD3J9/rvXVhbVB39yc2yb/UDbL/ftn0nYN+Xiq9ddvvzvtXxb3v9u03tbW9fdPL1088Jr/S73CV/5s9eHnU8alXVBt5GyNFXss9ZwqOm8NuGakpVTBfZjKVLXN'
        b'G5TOI2I6wHhQN5ID67iiV+qAhVzRo1oeHHbTK3pHTbkifGwBXPMne94YrNF7aFh5yNb18eEpXIbrw5lKiteXdwjwk82FVhVDqMPUCKLMdVNaFb4LdDrrTX+eVBqcnKvj'
        b'0KQEmqHTdRSaWSJX+Bos9+jQD+GEFQVAlFzx4BxW0qExcFpDxNrlvfVxSRbYJpuJV0cx7Dhsw5MKjRvJ21UdpKJbehNzvsEs2UqVMA7PKUJHLmIt5oStRlrVWSTyU5mg'
        b'WC05JYUwnxJ/vBDqH+BE2Z2zBWmlOBEbolnZVk3HFtIV7kSOFncNJkUrkEZS1ZalmAhZ4f5emK0DhmOgcON5DOjaeEclVs7ETFdsxFx/mWCMl6RgvBnPzB3j4qFYSe5B'
        b'jhG7jU1kp7GATCIBLIU2lnNkAtzUY9mKRIQ9BLV4BU+z1APxCpxSehIhkabv6kvyNpMW78H9LPUkPLFO4+SL+ZPx6mYWaFoQZCxYQ4MsES+tY0XfQeT1M/6cptPRQzDC'
        b'G5IMS91Yk6/FUxbY5B+5Cy8GK6HWUSGY4hUJTk3G69yGVDtuucYNmmJVmG1KesVIMMN8CXPGu3P0mwLcO4VWjlTAVIUNrPYW0CrrjRnawbsLis20VhZqYokPJTp/G1Qy'
        b'c0lcMtKQ71xnt/6YrjJzdKKmDBs7GaYMGcV9qArhKqYr4UZvN39sVmEOqbyltBxuOPD40eNwHA9oZmFNkMjlgTM2UMV4r+CQmojSpMrYSHWWXAaFaST06iuDcorYw4rv'
        b'gDfU/ox7dGIvPfvoQNhLFJVNpGto64+OwWMaN98dRP6/YE6eIZKaQjZjPZxmA96BNECh0s81YMu2wVDvQ0amRiUK/cPk89dALS9iGtGyjmrgqrWKFvGmAC1j8Qg3cjVb'
        b'ePurAmEv5jFEbF8jMu1KZVOxgKROax/thkWk3KoVHZEcZQlYt50lndxPofF1UhEpCUpFOI+nKUTiaHYLm1buIfIhke0wx0gQlQLRCG748VwvjMUK/4BgTO9gv6NA06cg'
        b'mxuGisdQrl0dvKMIB52g0n8Ce1lGRKCrZGKRWtV0sEvJbKF+GRtPO+dCgdIRL9Om2BJAymaGhyW4TmZuNUvcKBpKnUmnN7qp/AJdRcHUU4KytSu4Ra5itK8SrkKtm8qJ'
        b'wlOSlS5WisXrU/jd9BEjnEkPuSW6+XJoZivIk61JkrEZ5ELUyDalo9uWIBFPwmEirtWIeDxazkfRwSAvpYpMjSaSKBxMJFOgTCTz6fok9q4vWSHSdIY0uYu4Q0mWhnJs'
        b'5FMTTkK5xo1VVEZWMTXUQtUEOMYS7osV2OwfoIJyZplXCEo/iUioxVDPwULL7ExIDxGhsUmlDqBoDhbuMpNFRL9j4T8riKrZZL4wgI6LqwKc3+DM3po0i+IgUPIGohHD'
        b'TRGasW0gnsK9vC5HVRT7tN2bDotj4QgcxWaWqO80uMpk+N4uTII3hWss0fHQNsDfzRXKbDpAy8riVnK8201Epc7Q+MIBuOJESuouCmYzJagdDuf5PlW8Da5oKOAqn6xk'
        b'MDbthDZS8D5k6cVD6/Awi7GGJjNBg/kqMzgPJ5e7YDNdxS+Sx/pby51CV/EI/MtkH2rS3pg/XjBaJGL2likcC/gaUfMpFjDWbGNmVZOd7J2ZQdb0nCYZm+SQjzWCvJe4'
        b'yoQsL1Rp2WmmpvcUgzCF6L3HqHXiykg+YG5i7QgiwWOWI5kieEwMINrAsX6Yyfp1KFwI1WyejvmOfludJMEYSqRJeAiz2bQWx1F0YMwLxoKl1KqSxYaGlSSLwjQXnvg1'
        b'mYezI5mfulWDIpoTXeQ8a4hhSzBNQ3coKJzhR5ZV7cJoB+fknmQcs0r1xlS5ki3pAWLgYjJgj5ABa2fEG/I0nhtA2xrSoIyuXLQRzfAyGQ5wCvP5FM/DC5voXhsgwhEL'
        b'QVokumKKmqHtQiteImsO6WdTzNpK/mBjv3kkhd5YIoPj60gCdB/s6wOFOpB0cXQcVE0kc5QtWYXJ9pDjTg2ycqJFUZss3JjGjwTaMAWPK5MsTEmTDhVtMGtWkjv31KwY'
        b'jVc1mOsq4t5NgtRHHB6/na83p7xGsGED9ZZuvlvoE2RXr5WN3A7n2ODz84zy3w5V7fjxHDt+KqazTd82DA8yvDB3zA50UfkGktWaQy+7+AteUxVQiZVa2eJgrAczRCui'
        b'mCmam6HXDEqkwO1kdYb9DDq5O3K7K2lmPQRtOJ43cYeLXqwj7LEVM5Xsyf5wwHULW257kZlJylsGl/gWeQXzjSmZtr9DO512qCwwahC7vQTSfMmMvIqXVNqp5S3BWVLq'
        b'g6zdZE6ryUhhi/hBcaEn5G+EajbCFsB1uEluQZunbvEYLzO1h1yGogZXkyc5d8Oe5wi6A92NYnoJbCDPlLvy0pNN94TrFpZRL2yWQTXmrWU1TDDCY11B7/FKhMBA7/sM'
        b'5XP2BF51VbLNT4ZXRDNogTNkEnOY7aFwRAllkILZOunHRJAW2szle8l+yCbjhSz2Inn1kog1K+HYhPGsbHM3KmnNzfwC2UivdCOv9oF0GWZCxTKOuVE3GFuUtpilIlNy'
        b'gID7+odzD+ZMOIsNmiBsdCcbNREb2OpsvUEG2WOAU9a70g2hycXNjU79cnE3nKAQxcNZsh54bbKSjHu4TCQDSSUO9pvOps0EqIZWTYAvaa4dUG/aXiE7LJRPpgsHnR0j'
        b'oB72K11plfDSIEExWOptByV8qFf1QrpuHNhObU2uTnQokzl7kOyWmayxxmLJHA3JNsvdCRt8VHTZaZV8oCmMrykpZHQewSbXIGpzSHYQjB4R8YA92Uxoc01PIDXogIW8'
        b'Bup1cMiuvfn7V5Yba9zm9vVLUpF5TyQ1SYJSPAE3uaN2naU1l5djdrr4WjnSFc0CW2ST4AYcZe8bkdtpnV2xs/3mLSWLO7MOneyN1f5ugQpIWSdI28WpkE5EUDqEzVeS'
        b'hQTzyTp0BduYk/ai2Xz/S1s23xmO4DkdigmHMNlho+r134G4VfzBfS06BQunVaiZ9Z6d8SwzgHas+zFxMmF4wBTXmKIByhkqoJyscPQURsEQjqlrOD+7ofdMyFP0pw95'
        b'xlqU7lMkY+m+nYm9KH1vbmXNsD6k3+Vyep4zQhwhDSBvknv3yHcWlGqdviH9KlfIyV2FNOq+lGIpSr9J961NBtP0flc8YzbFWqL07BT7mCIgW4t25Al7hbXYh+KMyOxp'
        b'fjLpZxtTa/aZfmtnYUexm0VHck2+M+o5d+m+vZGdSNNl2CUMvbkPKZGJQvrZ0lTxLxOl9IPZE9Jds1AzhpJMcZLNRQfye5RI8yZl+Z2WV/pN8YtJHxNxR38DZze89Tsw'
        b'C/5B33WIVH6B9Ja9gnSbC/lk+AhJSO1728AhUs8FIdmzIPlHRRqIHBSkkpNfzK+81rwLjIk6TmDR2KFzfLwDvUMZcAmLnuY4Jho9+Agtp5qiGvNjuD7/J/AiU/TNdIQO'
        b'anrStl+gPm9ySVJIHJP7V8n4P3eluCVNtBRNrEwYXIkk9rkvTeMgJHZyS/rc75JMEgffF/YMNmPEMkQbuLTEkGleEqYus9qjIOJtCZ7vFmNvpv2rsXkwCIksykR7bdrh'
        b'2oxcK6PM2bUFubbUfm/V4VoLSFJhqgcb6RNl2wFsRNYBbKRvnrFpf9MBUaP0YCMDo+z1YCMUpESIGhLl8CfARobmKUwHkBRH66FGLGKMooZFDTcIMkKhTTqDjDjetmKY'
        b'PIw8e270mtjEe+7dEEY63P034EW8eOT6GJV0Wz4nOMT7tmz2mNnqk3S4V9Ffp8SHx/nw4qGXY/4UOIj2Ja8/DwCiy45FenpSABD1eR6SQ6E61BcY5FCId2BwmDcD/hjR'
        b'BXQjdO7ckOgtnePLPdSNtMIP86inHh1DV5B7dj2lqofM6FxmlWmnNGg/qN/piLuhaxz1u7RGd+itnvLwVN+gz/z30DIekhTbKIgdx/htn8tx/JqgTYfjVwlp/Py2YJi5'
        b'UgElDPeLQuNVwN4tsT5v1hlpqOx2S7pLKdB9Im/FOK0Jjiz2NYv5RPhub3+vscIkG3n9iy+ouI5gCukzmTUK0sL0aG038EAPtKA3dV4gVObuSUJgviAOlN1gh12XSfaQ'
        b'uBs2pJ01Hg/YzRj+xnsGdrSeM2yjnfoqBdegJtz/E3ANGhU1VPGw4BpRrNQUPYB69P8nkTV08+IPkDV08+oPn/B6aGSNzlO1J2SNnmb8A6AuDM5ew8//CWSLrrFbPMwg'
        b'Mp5GCNAQrB4CivSvGQJL7YaG0amftQgYdNfgqBZk53DqOfbnj6AndCX5M+ATsTH/w534/w/uhG7GGYBdoP89DPpD50n7kOgPBifw/7Af/gL2A/2veziOUVBY0jS67zc7'
        b'9+uIOGCKrT56xAEsxrwALYlvuzsytGGGEk/B0ZjY+b97iRrqDWSUu5FSkX9yZ/1N95hlj7722EuPvf7YK4+9+diLj7392LXCo0VD9zWmDT9Wm6bKaVlSmT5yX215Y5bn'
        b'vqFlqWMthJSFFgPHFqiMmP1HHbgJsie1owJIHliE5ezMiRSnfhIHBRgT1g4LwEAB8Bpkc+NVsW8iP229BNmdjluxDmqZQWU4kXoOMIuKOoLZU7DQhb27DK8a6+gVSIJl'
        b'HbyeHfCwztvzPxIRb5gioUNk/DzumkqdVuX3Dcghfzrs3e5hhKDBbz6UEPRnYt/Xq8QgNYg6ocxA3PtsUjIe994tJ33Q+7Aetrpuge6KBzvirjXuMi2UuqnhQ8U04y6C'
        b'mpKKajFKraBmzAQ1EyKoGTNBzYQJZ8a7TUI7XGtR0B4xJKg9OHy9o/b4/4vY9c7IXlrpRxvQvYnsFzSy9n/h7P8LZ3f4Xzj7/8LZ/zic3aVHGSmO7AId+cz+VHT7A5aM'
        b'/8vo9v9qTLbMoBBow+1CcVHQAeELG/GQZBkHJznCFzW/T4NiPMOdIkJ9MCtYh9Dl44d5jEpsMYXGMkm2MIHczXLKwZtjCte2QxWLYojE83hEuRDSOgGB6eKsZXCFOVXH'
        b'46nVGgsLyVehi+8u25U0lgp0GbY0Dkt7fN0TOJdEeV6P7/In8mvCvCQqTMC+/nhEH0UHJzBzIWb6uPD4DczUkbMKq0ebzKLHx0lUFIFSPIg1/l0kYBoL64I1dpgfyLy8'
        b'hBClMal59k4exZuGZ6bo2V7DFyx2XbSYBvT6BQZAbZgP1PsEurn6BtJULse5S3BROQZyQkKFwVBhGYeXErn9rRUb4CJl0lBOpFwacAUOm7P6wxlsjsCcQZDeKQcapbp5'
        b'jJrGpbJYcbkQATnGcACK4FwSlbQsrENCtQ/abtB1WBh/RV/55THGcCocKjmZR/ocfyVWw161JWlPWS9xmiKY+3EXLbTDJhrDcGWrhsaRtInOYZDH/OdfXkBp4wQHj3mJ'
        b'20KC4oTYfmO+lTRPkDstuRPCc+wLptnsnWm+r2TlwdX7ngPlazukHRs3Xst9wi/1uo9R3rhv+24ObRpuEfhd8dc3bqWH5tvFfKhULGyx/c1iUD9vnw3hvRtW/WD2+5vz'
        b'q9f96uA93PyOm/1Sh+9f+mrYCMv0y+N7539y4aIvxMwdeH1yWEv5a0veTDoecm+d/6itCWPWvfe34IaRZnsnXpvg+KrPVzNbPhjwre3O4wkTz65w/qGhav5PlWs/PlPR'
        b'50j8ic823isu+n6pq+3Gnye8X9Z7QtWykilRBUMsrLwH/lyjsuZOCNdtsUIX7IkVzjoHn5iRTHGYCU3Mi2IUVHYM96TBnvVwkSkdcB0yginBhQek82jPk9NZ0hZ4MpCo'
        b'Ms5DOwRjSngKD2/g58rXFmzX6yQF2NpBJ+k/kB+Ln4FmTCMDMImMVm2/crrhAgXDOoMs6t5H1J2IeKbubPfk3qQ1RA+q8Q+ARqjr7KuGx4LZib2P79Ju/rO4b4PWf7Yf'
        b'FnNXwJNwDQp5NCmdp1nQgtcDRMESr8sCsHoNd6dptqTOiPuwXEt6LMK5sLHslgcWjvQf4ydhNbaQuX9BwCuxmM3MyQvgxgLn3kTl0/s3kopmYB6Pkq0ylzmPX+cXyLuF'
        b'FL73aBmpdQlksXQHhUMHdDloTpI89uBZHoB5gUyZvboAzN3kpQ4xmNoATAFyu9PMKf+DkY8Bf6ACmm2m8Y+U35fGMCoU9KS4DzsDt2Rn0pbsH3lCG8e4Y0hX7clguKLp'
        b'w4QrtkcqGvV83G/cM+OtgahE74fRPx0uGNA//6he/+XAxJV/GJhoSHH7S1GJ9Oyie1Ti8KAkqsCTvRVKKI/RWUx5iNDErmGJoXCYEYIahQ5oD0okt/KhQVgzZ5pMKQzD'
        b'OhmmU5csTraU44AFLDRRmI+NPDQxDtM4ZuhlPA9lLOhQgBy8xIIOIQXz2Z6QJ5cYj1eEMtLlpdBAHnckYZXZWHOo6hBZ2IYHFvGdp5AsoBewRAMtlNVKcIeSUBaQNJqs'
        b'JU0aat6AAzKy80IW3sRjLBJx5w6ochaW6wILMXWZmodZtbmHaYMKBcUsKOsrmfdTsVycdmFxKIsmVPmweEJMF3lAYaodVIfCfpsOMYV12AjFfPfLxvODKMhmvi7+zwkv'
        b'QQML8SOro0no2KU0yq9LiN8VE9YUTlNpiJ9gV5gUH/RxsB8Pb9uyhYb4kW3DeNOaL4TV/MvV0xl7q8eJyWqnF61D/70Qv/SHiwy7Ri0vLDKMWj+geiRc11KXuJBldYtv'
        b'IGa7YJEz5AjcxQiLST9lcRc/FTTLxhBJxp8Ih00aJWmzOZhpFRaF11h1pu2hcX2C42azWHNP2Uxex+9CaFyfYL1gevLUA+Nm8ri+yXuIBMXj+jpF9a2IDd6wk42C6Eg4'
        b'ocSqifr4vSnQBIUsxZsKLVpQ6HaXF8YmCSoOxAGXyMg+zDx1BdjvSF11reHs/0WTykx0TUrLYRmkUkIrntKH23mRkh1go3HMDGhUsji78mgWamcGN1kc6hTcm8AD7QQy'
        b'Bm/wSDtslCfRvRwPwDW8oXwEasiHhcJCl8HaoL7SUCULs4OGRG2kHbYa87laha1zdKF2gtF6iYXajYSM2H0zKuSaFFKE8+tvJYU9Fd9nlvWXX5UHvr3l0TsNzY+Nsivx'
        b'nDR/YInmybLX7OzSnqoTt3zy7qN77Sx9nrE60X9EkI/9XeVuIav36PP2vXwcvj27o29/64zD5386u2HyS5/nv+m4vKjk5+uzn8neNaKqzn3tqfBhc4ruWe6KjXr+76+9'
        b'4NbwYvnzWdXzNn0yz6zXlWHHTYc/s3H48kMvtMz9LMDXYfjaMZHJrXZZXspnRg6LzK+MnPC0ZfbZAS0DPwpwe270sFv/D3HvARflsf0PP8+zy7KwS5EmIiKiAstSVLBh'
        b'AVQUWIp0xQJIV4qwFLsiSO9SBAVFREBFFFCUIslMek80jSQ3JqYaTTPVaHyn7C5gyU3uvf/fqx9gZ59n6plyzpzzPWfy85+9W/gGa89MLNmi+dTZF5/LaG97sM3yy3et'
        b'9DbmvHbnvYK1h1+6Yu9d8nU//5ufV2zVuee0wen3kMo5Ok87bXndoCDbZco83jvHf5gfG6bxSXiSJPl579beu4a/ae9y/7A+NmN1yKdcxrSU2MWy+ScyPjpnFv3KL1/O'
        b'qHr+8tNZW++UCP/l+O2z1p/+/s67y+Yv9Z8Z1iZcOufdfP9nRGfKt1397re470X14fw9DZ8/bXfxzmrtkD9udxjX9K/123skbs+L5jsqo/UOvNJ6Lubc56Zft829qn16'
        b'TjwzwN3y2lp9WfPiyAunbH8F63jrtmz5SfzRpjhf3UbjiNbszCk/zpt8r827/hu753/weWry5m2L1Xsr3zm27nf+7fqkt5IWJ/uG9rXWPpuxbuFFrYsfZUr9EzrVl7xd'
        b'b5o+Y5V2/rMvzHXfu8r95i+zD9QsNk/feGDjGpemqxY/CXt+uekzRbrZKpGZV/CCfVOM8F/JZ+6qdfm9+WfOu9dSzDqT/7zGnLq3pH3km+9ufOe1YYfvl31TM5lM3VvT'
        b'Hpzbm/tgr5P78yetv1jw9bynk5bf4n/xO/PtjI6CWVkFm9EhdfRSqM2xD9KL/ji48iWXr29ZDRuP/Bp6c1/pVvU9q9U3/+YyZUHja1kFQS/fWP+KY2KGqKv88sYfPQaM'
        b'fN62t8gsW/qjxzD66GCx/ERE2b3WiEVtwbN+fO183iIPaFp/6hPHuVryEx9/m32/p32w/IXLHw8sPPxc3oTt/F8W/1y2tf+7CTeCg3+3GxSdKz4nO/fyvTnpaZ35dedE'
        b'X7bvr4vo+qr+6/uXNi8O8VhikbLvwrSkU6catqmnv7qm1Uhf8mb9one/E183nPz2pGfOwmRXl/nb1fZ8FnRr0hvFn5/4Tn8oOPlm+f07x3+6cWvk61v7kj+aGGz1VXfc'
        b'st9eL6l6o2fr5KDf8799bmTPzaawB81Jbeuv3/ogOA6c/mjupzkBpfmrBjLjUwyfzdLZUGEBFm18+l/elmZ+z6T6G99Xs7D43G25RJJCrI7hUChoV3Dc5nB4lOlWcNzC'
        b'XYTx5emqok6jI3S/CrLWCo4TaWQx+v4gwazBi+DUOK/B8MgeUsTE4NkymB+DNvVxkDV4BeQRmQJ0iTYrgWYTHTDUTAE0A2cNCGeuB4tgnxJpxgg2bcdAMyEsJ6Wrb0+X'
        b'g0LJ2ABYFGhW5ZiOHe+Cykh7Bc5M4oWOGQxHoUCztaE8ZhHIFaBj5gzMp26iK/fCBiXYDHHyeaHhnM0a2EENoMtCzZSYMkbAk2NMmSWgno+jQl1kBE6mA3OViDIkqxwj'
        b'HTRFVQ6IFJCyxWBAhSqrA0NUqimGp5aIQC5sVuLOxgDLPNAwkWihNguRIHEU9KuwZR0CD2qbW7piGy3eDg4uVYDKkIg/QEWv/nWwhcDKRjFlWVkEVTZhGzU2LkQ8UYEC'
        b'VcaowVwXDCubCQtJ/hCM0u6RgVydh3BlSJZrJiTYARsy5fag1PchYJkr7CTPZ8B91iILXdTCh3BlF6xI/dawnS8ioDBwaLUSFwZbQAsx8Y7DjIAcg8JkiQQWppNFowCW'
        b'gDZzBSxMhQmDNdsJLEw0i47MBTQ9B6WgDtaPFeuky9MVXtPb1ES+dmIJ6jUYigctLOI0j8EjRFZOdxbB4uDJsNRvPGzEkyMT33OLNoWbjQObwTpjcDILSX4UTQCGwFm5'
        b'K6i09xyLONtqT+3+m2FfCgGcOYdhzhriWYwxZ2Z8PhrbfDS6BJfXCgvAURkcgMUSn/HgshJQRwbYeia4KF1MgFjj0WXtFFsXawSOyFEBTSp0AiiL8KVAi0p9cImAqRgW'
        b'HIRtBF52CvSSGW87L1DmHSMZL7A7r6GDlw0OL0JSdjsoHYWXHQf5FMMFqqTz0TryWjsOWSZPoeNyzhn0i6x3worxyLKMNBoOExwMk2JMmalIiSozh42k2B0wJ0REIWX7'
        b'zJWoMrHCObmFHWiXmtpjXNlYVBk8rkA+lOluo6gyNMUv+xBQ2WJwkW5B3bBkuwpWxqgZw9MEVgYOwHqSOQKxeIUyeHbHKLQM9LuoUxjXEdChIYfH4dAotAy0gHpwibTZ'
        b'QA46ZN54YY7FlXW7kL7uBYPT5Pr2vpIxuBB2B73EadwD9pN9gNEzJqCyQB7tyD7XjYjFchuFlU2GA6CJkhPJa/7Y31z6GB/th30nUbP/Elg0g/KphqAD86mZqHuYmH6g'
        b'MV62VDrqjJ5cOCXDHLo/9DqEo2yNc8ahXlrgaTKNE+CRXSpAGTwzjWLKVIAyOOBF7nfiQQHIUyDKxsPJEkCPDWhcQGZyIBxCspkSU4ZWZRXcj1FlUWi3J12oioP5BFfG'
        b'OMGLGFe2F5RSUO8cYyWwDK3yM7BtArsR5k4gQ7lwOp8Ay5B45UWBZbu9yXBtRwRGY2y9ZBRZBprWwyE6hwvhEbGcoMoCBCpc2bAJ3X3Ow+KFBPOCVge+5LyAmmsMz/FB'
        b'+3qp+RoKvqqeuUHBKOdvVDDKKzzJNdnaqfA4uSZjzGfga7I1ntSgoGVGuMgX5jgpysSTURNUcag/B2AXKXQmqESHiQInI0hPN+IspoF22uAj4LhUam1uPQ7I1upDGmw7'
        b'0VqOD8Dl4ISnjYYKxzZlER9UgrwJZAyFkcuUMDZGTRctbYxjCzOls3zYNwxT2HPTeBDbigRCmKlwiEcRbIyrHgGw9YHLhPC+4mkK+BoW3iiETQVgQztGNclvtxQOydRB'
        b'mxLEBlrEoINMCSuQ6wt7fHbgPX4s5gx0LCXPg0DPcuWV/VJ4XAU6g7mz6P3bGZC74/GoM2YB6AaXMO4saAkpKyUuXE65BDRCeDae0IX7eelgH7xC0JNu/vAsnp0yiQYs'
        b'kngqMEWTQDYfbQKVq2An6jPB6ddPgq30RUT87ETUX3V4hHMDZ93J8ynwCuwGxZPW+nmPw5mBuk1kxW32iseX/Ps2j79jvUzNVvzd0LTFO+++0ftN/3W04hK1vXJUpx+a'
        b'ReVStLOi42yf7nbeLk9jMkV0LOFpKZp3iNtyAMP4AgHWczst1MnsmwqyV8qx989CzBXivrFoZwRFEwx5u62CCPTOEZZTp3iPgd7BPtOHoHcJsIwUHAkPWVLsmgK3Bjvg'
        b'QYpd84HHScN4YGCH3BNUw4tjUavbNejELoXNoFW+GR4ZxUiXwpa15OE2xJe2ytcEedqMAeYugaXU3cFBc9g5Cq5bBnrH4+vUYh0C6MprhPn2yjaSWjRgL0UHrocFZCIb'
        b'oIXSQPF1JomjCDsKrwNDULEI2+LgCZE2qFNh7EA7aIeVhK47QbWnSAFGA4VgvwJhF+xMEZmVFnYiNXUVwg40rQaHKYN4PgzWk91mI9xHQXajCLsStPdPpOdQCywTYYAd'
        b'4ufqMcgOLfNCZfdqJhGUnRJiJ4MFBGUHjsIieqAfAdXgCuwBuUtVWDtwHDZ6Ufxep8suDLRj3MAZjLNLBPsVsZjX7KQ4u4dAdsm7nX3BMOkXC46tpCg7xFKfgY1mnP5q'
        b'd1InB7sc8NEh9bWDJ9NVIDtdip6OSQEDcgKviwLlKoTdFYWjBcT/+igBduig6NmJEXZBCm8AqTHwEEXYgfoUCrJTIuxWg/PU04MvKJTbY89p40B204WE642XA7LSDYmw'
        b'MBZjtwzSAycGVqihldAmHgOyW7luGRktAeiChzHAjsmCZzHAbq0W3UQHAmA3DQQOSzNUKLqZiPXV/r/HzRFUE1EPhPwFaE4BnZtEoXO6LJ/3JNCc8CHQHJ+oDTQxJO2e'
        b'roBP8puz5pwx+mvyN0ByQnW+ArYmVkDXuD8xpI17IHhPc97DsDnuTz2+LoG38UnNWH2BSzEWGuHrfc6WlotK4Av+S8DcNe43zRVjAXPGTwbMGT2sUPgv0XIFWLUxB6X+'
        b'SrXBZBt98xjlxhPaglqAwQVpnysBczwMmHuLVdw3SvT/74Bu11Cln2A8YDLzvwK6Cd7jpNqsUG0MqM1qFNRGvzN+YOZGHCkaT4N9ylvpBNinuphmGWswrJbEwEuP2Ltq'
        b'K/7K9z8CZgvjV6tXa1Trx3L4d7W24rOB4q8m/ZvAi+VF80q5aBuV+gjHtxHna+Vr5+uSCNViDIoj4DG1GEG0IFo9l8ERuku5MHWU1iRpEUkLUVpM0lokrYHS2iStQ9Ka'
        b'KK1L0hNIWoTSeiStT9JilDYgaUOS1kJpI5KeSNLaKG1M0pNIWgelTUh6MknrorQpSU8h6QkobUbSU0laD6XNSXoaSeujtAVJTydpg3y1WFYBiTMkn3G0b2GYETGU5BHV'
        b'mjBfhMZGB43NBDI21tES9MbEaHxzHiuRjoiXu/kEKQPaf3KRe8g4ElsnjX2DoudUtjXpKTi4g5y+M3eOLf3rSEIh4E9O4wpTquDk9uZuY8z+FFZsBAOgsJVDT9Nj0kik'
        b'hpRMHIA2fbzZ3tioDbbmMZFR8eZpMVvTYuQxyWOKGGNXiI1Sx5XwJMOd8YrAcQnfFGyv5RlrTiKvys2zYtJizOUZm5ISiAVSQvIYaAUxiUKPI9FPenxazPjKk2LS41Oi'
        b'ibU5anNKYmYMUVlm4A0mcTs2rRoXlsLcPYFYKVm7SRSmtonjbbewiZPC+o8SwkFBB+WI25pbL5MoX4s0l8dgK7T0mL8iEqah9XIJxmNEjrH0U9jYpaQlxCUkRyZiYIAC'
        b'UYyGAIMeHuqoXB4ZRyAhMTT8BnqL9t48OmYr2lHl5im04cRcz1rxbBmeYUkp8vFWW1EpSUnYpJjMvYdMA30l3AhvW1LiiCAqMil9rlMUb8y2o6bYeohKyRf9UoC91POV'
        b'AbJEZAth0SbCxWordNG8AkEOs5u/Q2MXj+ii+UT/zNvDDxzzmYL9PrnL/g3417iF9GQDsSfZDKLeUXPBNT7eCns3EguFlDtKN0QhYhOKluXjDUmtY+h0etKa/QtYEhla'
        b'Z4wuiYpEqz4CNSmC2u3RwlSFjJ16T4hQExkdnUCtPBX1jpt6eJKmZsQolq88A60r1fbxeDjGOFtYGngGr77IjPSUpMj0hCgyWZNi0uLGhJV5ArAjDa3KrSnJ0XiE6Zr+'
        b'6zAx4845LcWEG28rMMVXjlnlktrEnjd/lUpOpUtelFwslrzTnS1nEnYLWya1zk66g7MTGzHETV8AWKdbCfvwlWA6khkk4CIolsBaJGXSPBEaSLzMhi2ESQ0iuvfFcBDk'
        b'gNOo+j0M7BLvWQsOEW1s/A5e7Pcs/hRh67/UlsYHhadBMzgNetCevwh7c7m8yGZn4m8PHjxonaaW3MnqMoxrRGJXqpz6H7aKB53EXTKsdpzFMWrwIDi+kF0NBh0kHLFf'
        b'WK0PjslhkTYszKIqBCRgathYs8wcWC2AtbBM6j2TehA+hwS68yL0CObBRobzYecHwjxUCvHLYpI+thBN/Ivd5MNYOKtZgE4XhfvSdYki8kCagUSvfiTdgGZ4FJUgxWNg'
        b'upmWAMsmK1riaYNEaXhe6ilDSR4TAg8JTUE+OJRBzJUGYBMa6R5QN0v5gnAul4ykwFoJj3Q9HJ6zwQE47GCl46y5HCPezSWDli2wMJzocYUOi0afChjxHk6+JREcBqfJ'
        b'0zQrUDH6mGXEeznHgCRwwCkDQ03koSSqDDEB9MBv+XuM0c6A8l3MCh31ibADXiFxKkClVEolSH87eBENYyesRDKkPijD90OdyRkYagEu+oLcsW6ylRFRYKG3TGbHpS4B'
        b'jaZwCBQZwm7YLTMARTKRJr5i8QoIjLRgYmJ158+FVWTe3Fmm5uTKIzPBe5GvGZOxHpd/3B32PKZ8bI3p4BVsDQs9YEkgtn+UBcNzqulLrGD8PNX0ZmrCYnAYCdytamrw'
        b'svtM0CFh3LMMYOMi2IRGHFM4COa5wR6drWksKICFSPS9xFquh0PEjmQ9HJwtEqZlsvBUFIPkFxvYAC6QiTVFRDzhpqJc3eAUynWGnZG5idrMDMBiHflWfJ8Lc9EznpiN'
        b'AIWK0EdD8Aq4IE+F3WI2FV5C+faxM2Yh6nPksRxUwVo5vIiK3Qj6GA4MskagBwyQxtiCy560ylRYQmu01iKTJhl0rXqI7jthT5IEdGRgvxopoEBnbFAXH7sJ27z8gj1U'
        b'ORSjCvbBHgYeTRSB9hS4PwObbvmBAtChyFuJHXbR/Cj3arsQmouBVUw0vCRkFjgnvK+3lpVj4eRVjeCkqkUp+m66z2d9986v3y/5MfNTXfPc/GzXrdwCHSvX7BWebrKC'
        b'3JWF3bVnfmPfToZzv3nN0NAjS03t+HVHV5/y6/qrVx5vjs7cnTpr9Yf/emXvnz13PhgKLCuqblxz28MwkDOwNYzJdNjcb9mXrZV2wNlAT6bnFnRuldonIZtzDvpvfZk/'
        b'XWf68Jkt3mpHWg/cmpG5b9D89pSW/tWvxLdLtfm6y/g/TF4X4BboMF3nxW/fCpSFvWU070q9bfpuN/7y/uVXNxiErFw0AN5adPTajNkvW1fGyq0TjMLK+9mSmT/VxIpb'
        b'pevNfjBe9Fxuy9rfL71o+WNi1fOrbMrbvGPCfn/PEd7I3RQCthktSVE3M554QM+tK/O1z3fHfCg3WzL1wQuvfyY3yhtZu6fs6Kp3v5wQ8+Yle/GFmXvetK7LeynmYDg7'
        b'8d2ird/XvnPCavES97tg/sG91xcdfWGiSeYfl3YaWr4yZds9k8xnutvX+3/2rr7mQa132pKKyiS34+8HsdMH92f8ZJneuCa666279qZH+kqyZl+/9HTKj2sesO1njd+e'
        b'f7OzOezVxtMLUmQCi+tb7s0bzvn56zq+1X6L9o8+P78x8qS3d6hWT8ZP1SZGO8wm15r8drjheF7b2q+vviY/MvF7rSsv3li6ZEfsp6WBJvff/qP3gvju8KmMvuq6q52W'
        b'Ts0P3njFpEHnQWtH+RuD85x+PnKyzCn4xHaXZXe+dWjY7HsVfbV8KFm6+8bwub1WdmD9ytl/XBtSj9n94CV/70iHzeEGsu/iTjzfkO2/xPDbdf1v/X7qPfb27Ge/dyqe'
        b'ExSUq1HTLPTLumV6o+zOjryQXzv1Zn/ssiJmco36B9tuvjPf3K9gz72cj5Pkwj2d30ncyJ2WJixbL7X34UDJFrR82lkZ6APnyI1YILwYAnDMsQJssO4HizhGtAa7o0Ir'
        b'SRN00PuhALTreXqrh8IOlLuAXSKYQzVj3aAIHhlVdYMyDhy2sINHM6mjO7yoQbED1WUKIrh1thagCR6lVq8n/OAprPpx8MNWqHu41f42c9el46NXZ4sWymUvgdUgFxZ5'
        b'24NCP6LsBQUOHrY2BIypzoTvFoJOMcgmDdGJo35mx2rs05fHwXoDcvdlBgfn4msxWGonYAQbOXhi0nQZOEjvEU9pwDMyPztPW3zTK3KdA3o5dIS3rKImxq3zYM6oj1sP'
        b'MKjycZs/i+qrK2cbKY2QbdDmd95faYPsBxSKmT7YBWrlMc7jXG85R5BhiF/kOXoruJudawhrwMGVVB9Tvmi91BN0WrOm8Qw/Dh3VoBe0kwvWpD3wCLnW3p8y6pYLlWAC'
        b'j/BTpbCG3s+WgSOgFvaELFH5eZySSPQC4Ey8JxphLx+ZHb7c86W50ZQoYWbAGrVFwaCY9G23wEIOSz2xrlqm7WsHe2Vckh1jtpIPWk3caO975oM8rNUu16DPGS13LhBt'
        b'9Zc3wytUbdzniNvq4Gtn6zNaF6xYxJjP5sPWXaBeYUUOL4FOub3qctMSHsD3m2mxhEoykKcJiv3svXxsPX1YRjuelwAGFsBjauSpnvpeeiQrLnS15vKsg9TXwlJS9EYw'
        b'YEQGq0QGi9UZgQa3HpSJwX7YRIY5BdYHyvFNPOI/jjK8LewucAbU0CvqooxQhT9MWAcHqfLSyI7UOX/6PIWHR4AoptDFIf7wHL0pnohZRdRTotZUgw2sMBP2r1J49A1f'
        b'mSayl9lz8CTEOU+xiHMoQ7MFj5cTOLDpIYeXcL+3Sj8JTnhR645s0AAuEzVh6HKF+0nQOYv0aOICzAYqlYsTWHN4YaMsjOpGK8AJEvwbu7psBudQ7YdZULZgA73v7UUr'
        b'ugd3q1zKGYNi9LSHBW1w3yJSbgzids7hZqmpXLtGgVKFTcVwstIoRg31t58Dw+iURhtAEfXReHrWTurg/5ga8Q66AlwiWgp4FF4E7Zi0KmUuqBUxeuAsD0dCBF1UH1Dn'
        b'B3HsomqQ56dUQAlBAwcKUSeGqKfQJk7wiEX+PNir9Gh9ROHFFLQvBKdgD9Hyp6GDnQcvsOAsKFeolqekZtCHhGESMNrRPAE86h4wPR1jYOA+UARwBKlMNFT94KhW6igP'
        b'hgHXDrDMw8cOZQt0F2rrUfXXis0R8hDE+WoihlrCMuq7OacFsIRSYwitUETEHDAoTaPzXj2GmyO1oJ2+7DsJDYwn9rHoJ4VFC9RhuRpjCE/xJ4DOKFLAJNi4TSRNwiXT'
        b'3OAUtwRRqYU8dVu4W5kfTVR1RtuXt36KqyE8RkhiFTVZjmYnCwcyGRb2sbrOoJM8WJ0MWkVqYFDp+hAJDqfpZtgG6oRjtTIWadT1IdplqL4bnveCnfINsE7lFBnWS+hS'
        b'qkMsE/XS6YCIgr10ogVfS0gnCdmL2ona4omWKNkgHDxgKSKMAzMdnlSb7wCqqM9mcAE2y30lCqsoGQ7QUMHoTuH5L5lHzqkMkLtdrgvKVP6OA0UKB4IMGJaTIZq3h+GB'
        b'A+wO5+lkb54FD8EWqZedzM7GF+0rOnG8xRqRsHkb0cYFgUI9RcMcQQVtG45ZVoiV1ZKNauDwXIN0LO/AQbR35KP5WWiAZ8bDs8JvHmI+F4GzAt8tTmQwAsGQPXVMDath'
        b'tsLKJ2odmZ+6coEIP1LM4EUBzATYzwOdgmSK7OiFV6ZKQbMROXLQcSaEAxwOS4NOBjJprsDetLHOGl0ylZqkBNAt0frvNTb/I83P45D/AP36a70Os1czRpfV5jRZAWvK'
        b'iqkmhSP35vd11YRExyFgNYk+hPtDqI4/a7Mm6MeUncFasnqKYFdC1pjofnSJxsQIfWeE/mtzevg3+i9kzbA+5a5AaPSY7wSoDm3idhGXIFAAT7DLRf7PfPUdhmNvmca7'
        b'I5CoUejHLaytuD0eTiL+r8jCo8WNlq4aWk+hwovWX6tgmGzLjscoYR7fmf+Re4NObBFO3BuMr0bl22C28vabXB/bmsfE2Zvb4Dsw+1lzHZX+Vx51dfC3mheHm7fjr5p3'
        b'Ttm8u5NxOxRXqeYJ0eNq/Ntj0cGOCMOj6B37E+vsUdU5jeCSCRg31pxkw+j6f1xzLKpZwo5ohatukMMTnlz9RVX1lm7mGckJqRkxjwHh/9M25NI2iMOVN4p/1YTLqibY'
        b'4BGQp6MhIHeSquvI/7QZhOIWf0XxQVXd9oEp2OtPcmwKcWRgHrkpJSN9nBOh/4wUadgnzBPrHx4/48Y4tfnPOuvxV5UBVWUmo5Ut81z+H3ZM9ld1PausK82H+Sfrs+yv'
        b'Cn1B1QHroMe4IlI61/hPl4wm8Q8QjtH6T2zCy+MJRiD+dNH+R1uEBG8RpNb0lCfW+ZqqzkkKdxD/XY1a4ZsiE7EiJDxla0zyE6t9U1XtAlwtfpfezieOVfE97D/kPx59'
        b'bVWrohJT5DFPbNa18c3CL/9XzfpfOJ/MfZzzSZZ5WCPB8024GazHk2MedZLrVuxGsuMnYez1RCTdnGSvan8lYQlPmOCpS7zLqwSfZHAJyT4LwfknOI+crbSUwWzsv+Oo'
        b'mL2CuB0GDx3ziTHJSg9Kj3MdiSt4F/MV+CL13/EVTLa44TGcxWOr/P+LFHzfoATbVT/x5PjrYt9rskhx7HVvHvPBx3wr1rqtY3TmPTraFxk62mll7COcTHj4ppSUxL8a'
        b'Spx75B8MZd3fYNJonePGErcZ14yFCKqAHfW3qXTuRJWwbL6WSgHLFaihUeahUebIKPPIyHJ7eIFjPmfhvfqhUcZWwzhqouO4UTb3peqnuoRoetlviYREctlvBgqI4uue'
        b'oZrCZ0Ko2YFp6xmKWy2fAHPk2mkabLQQvX6ctefgYaId+cpC6WKhbvUvgoUMdW/Ro41td2GJlGDuiZOKEhn64Iv9VgSsDrDzsQzhmI2u6qAZFoOeDHJ/0G61QOaFb/RB'
        b'mZ3x6N2YGmMTpYZk/m7YRdQY/mbwKNVigGp4iGoxcuAJoseClfAcKJONiSchW0aMe7cspXDD094Z+GoH30PBM6CA4duxoDMCVJBeroHHYTeJBhrmQmG7JnCA6D8SPECv'
        b'QkjdYIfhPEhOjQkH2UGkVNvUTNxRiZ0nn9FAwn+HOgfKQC+g7YXdoMmaWOXCMnCe4fPxZdMwjeQIh+JBH77dlCBBUsMvYCGGybQlUxqd18Z6MYze2alP8Tswd4UiAOQ0'
        b'rPOw8yV3joINnBy0GoYtoC6298/UksEyT1t70IPtO71hMRl26j1AukQNQ4HTHpmZIuXM9BidmePnJatyNfZ35+QjHoBxtzQemZP2vmTiHV6mmEmC+9J26V4lMPs07FQF'
        b'yVgLDrKgLAscoTqrC/AQ6FSFQUITpJYFpVNZAn6GbSAbdJmAKgXZlEQD+eAKURP7hoAhcuvI8LaAw3J21+StVCN8FFwGRXJsUswJWYddUxaAYvIAnHcAwxRKwG1kIyId'
        b'YJGMECpkh/WYoDxbDVlw2BycJE10B7W+o+GU9OBJbCGbD4aIdmwx6OModgwcWT4KeokChUSbTWJXgkNwAFxcZ4WP6GnMtMgZEjWSF1Sn+CjyVmwezbsNFJJ60fTbD7pG'
        b'4xqtEbGgPxl2k0USC0vWo7lxQvow8iWARzOfg4PzpIogTbpwH0HUrIDVxGEOWiIloE2KFpc9Wij2oByel9h5+bCMBTigthDWradrVNNU5u0pAfuWjkJYQJ4hJdtlLdis'
        b'iEzS446qEAi5ibNhTgY2vge9sBzWjotuAk7C8RbY8LIRnem54PJuYqXvTe6WbTHoqs8BFJFVYRmqtgV0gYsZJAJMCRjUxLqOR4zQR627fUG2J8xVhxWgC56kKxCViiYJ'
        b'2WvQPjMdNLMRE5PJGG5fMMbvD8vYSBUYgkaQQ9t2Eu4Hg8rtDG1m6rD/of3sPNp1yJ1vhxO8rNyU0IaEKHcObUqeaFskN3oFsEWsjNXjmsGiNZ0XTJoXugBHHFGY9Isx'
        b'iOh0NGgg47/JDh6l+wM8aUe3CENYOp3uOQdNYasq4lwCrMAbS9sEsijM42EfODgdTWeWYRcwsGxdFh2JISPYKyVh2vmRoB80oL1RbkEeLVkB+tBE87CzRWPotVMIarld'
        b'm33JXFkO8oNG48vAft9xBvCd4BApQCQFw/itpPWjIJR5hsScwsk6mG5lZBuL1Hp4I8O2GxKO7uyH9qKpUgy7M/kMC9vRXl4C21D3iyjkvgK2wytZqXJ4XoBx6tghRG0o'
        b'Xe8nYuFFTdgJD6IntowtOABqyckmFWoy6AXhLKOPNjlH2VMnATdWUe8Rs0KuG/6qr0u/fNlHcWQaPW+nMTeKfhlorEV8DMwyKnM5ZKl4M2qnBqOLcs+aN7LkJ7Hzo34U'
        b'CM+If0wIK7KL2aC+m93FblWPZkLQxprKRaukPcIKKSIjs5kPMeYjGovjYpJjtm1NWxqjodhsuX1GTMZa9GHKCiv5Q7eksJL6LsUBkYrQhzqFLwW0T/RSfwrwIA9HldOT'
        b'gSpH3U3zYAfo2A46DNXcM9Em5W+InnUkUJdTTWAoAKv00egftLP3JJAUL//VdiEe8JjdKDlVxAQ9nCaLEQenxBFg3xwydUBvMOxAW7cEHAuzg0VjtEemwXxwJjg04avn'
        b'5Zz8RdRhXm59TODl5A9cdT/aUKQnubk08eqvu7/obWzRFU/8NkBNsN9pZZFt9DY14+5cvnDWOr7v05Z5/b0zKix9KizCJ5hPrXDxaHR44Zbtqy+kTvthaH5KWePMj3va'
        b'tz2z8tPo9rXVxWuBU/niF4WTdm56o3qZ6Ov4LxfnP+Dqed6pjTx7+bTJ9tP0c3gvZFd8O0NUnxbke/n+0GQvs71nM58u1Tz1huMe9dynXgp6dXlc05ErNpu+vfOg1/Xy'
        b'e51vRPb1p6dkubXFNbbXBE3akBIQcrL9qLvUWWd78MwL70W2eU+seLfsPc/gndcjv6gRf7oDCI4e051fUrX1NfvjBfUlFc0Dhe9vfzvgrO2zSSv0D/3sLiiwnLC7xi10'
        b'xofXvtpbJ9bsvvdm+ulDk6IN+T7Jbfdmn3zPc8v7J8oaXvIN9ZM3nv/w46iiV5OOFXes9jld/+fUFY4j6nufUd/+fc2WpgnzhbveF7/fWjBYuzCwuDs2Y0LR5td+u5sR'
        b'9EFz4QXJPL+btj9qBFittjuldnOh57bK7w0+mZn23TSdF6dU9XvfZH9MCGjz3NA8OAmczo3T6JrQ1PLtN5tz0vyEKQHRTRbrnBfMvWBUobZ53e32Rb89V3MsN2533E8V'
        b'n2jVvuJzaNGM1zcMft1tH+f/4YcZu55xcNrxbWVL1UKb+aahlSnT6xbffuXa7gsdp1f7fHkv765FY+p5aGtW+LRjictT82O/7ow58bzO52kgwy6tOfPFz710Fon3uNkl'
        b'v/DUT5PfzXdptgydHTd/tuHi6C0v/PJcfYYwsmkKfMf53bnv7AR3P919761vvu4salbP2Nmy1uHGIqdXrt1tO/FR0jDs/SP5uXnLLHk3TL9dlzmleNdlSd/S606r1pRe'
        b'zNu5UOf4rnseyR90vpc0Q3v+Bwb9rNbPhy5K7jpo3Oj8xvK41W+JbvoDg3lGIS45lr393J2s7/kWaf33xFl/1oenfiQQ3A71a76//5Nfv/HIfOXe1eHfYmc/dzZVslCh'
        b'D4f7svDZDtrR0T0P7UxtOKh73kqifghNMxFhKJmGNWKnA2SIbZwA2njgCOwOJfoUkymwVmQjgd1ED4vW4hnhZC7EykOhhrHSAY0YqKJSSGeEkWwS2LF9TOBBkG3BTkbc'
        b'VQvRRxnP0aZqcIYftycGW6yV21IdaCs4bjgmzJ5xMAuakoKp0v00yLYfwxftFiK+KAIWEXnaDtTL0UGbR7qS6u0gETBa6D3LraZE7wOy0d5eM14J2wkGxqBEF66jY3U6'
        b'Ex6mUE2igW2DFVgnD8tpE+r85UQNCy5hoyiiit0Iu4KJVlCA9rhuEYHpcEEsbEhbCvLgPtJft4lGqWjD61EpWeEJCRl8H1AbILK2J8jE4jFAZHAymDZnEBwG5aMRI0G3'
        b'A0b2Vk4gT4USDbk3oswqOIA3PpkaoynmwDFmAVVFXobD4BKBpTtOtsWQoDOcI6JfAdXe9S2fKVPGnwVVfsRhgNoaopWLRbxVHQUjg3OxBI9MwcgD4CzpavjO+RjIDAcD'
        b'MJaZAJkFoIwMkRMfNqBhxjh/RCb+QlBmyYLz4lnk4d44eEykCsgZDgtITM4LgaS9Xi6gRw6LPD1hn4xjYC44rp7K2cAmdZLVA+TtFSlDq6NBKcNYVlDkQENnRsJBrIhM'
        b'FcADVMmrGcqBfnuYQzVsxaAK9IlAx1bEfrWDbDvcaMRxdEWKySxOhU2ghCgysRYz02s6qjyHqpYrUN6TIi8fqQBJBP2Ir2lgQSXikhooMpQPj2CWH5zZqGEvs9fEHJAx'
        b'uMCfP3kRMepYl5akgKYRuOsJlJHC5kp58OBUUEr05UZRsH5seMV83bHw1HZwgYyOHF7xVeI50dNQMEDwnNwOMjoT4Mkp1OjEARyhdiewZjLIJwrEcFuNlbBe9BjPDqhH'
        b'NRR+3gyO0sCK9l7Yl8UoutZ3DtHDpoI8e2WkRttw1m0LqCMDNBOtrH0Yogx7YT+sRoRTc2cRe90UT02CLoBhP1Wwv/VGLGhPBENUWQ2GI0AnPCNXKZbnyUgeP1gbg+HF'
        b'mbCKIIyNOIu1kNYmRvToFY3C/PhCDF5EEt0pMgpL4cEYVXhAUAlysf3GFdBEcYJn0P6QqwoSCDrYMRDGScYEFA1LbTcTjCEnYffCArNlW8gAalhtwWTcA3MfARk6BzlS'
        b'NXmV2BsjDGHeDgwyNOP0rVA/yRQ6huT1fmw8i+Yf6qszPKou46ZNVlrJnELr5dRodEHsfgIcB02KiLGg3x+2UXMs2D5fYZFlF+pN53X2LoDBgb6wcN0uJLKgxyK0jOHZ'
        b'NeuIdn8xKFlDHpdYwLMSWEDcLZ7lYAs8DI8Qsjq4wPNYasM+D5pZdvJqVoPMNqdldlI/W1gUk0DkCHVGBK9wsC/Yh+QKYcGQyAaW8bCZsdjKaTMYptjfk2jZwBr1hy13'
        b'1O3DKAnKJoJhpWWaMRoYhXEasUxbtlti9P8a5vWQgvW/9284ookhNeHEnJ1w2p8Stvjf388yezUNsI6ZTzCM+Lc2Z0m03LasDWtGtN58oukWs9w+cjuI36R68D/5PO4+'
        b'x+MEmncsdYxYS1aX02aNWQGHNd40uKCRIsygCdGNi9FvPYIS1OSMsYYcvWnMagux1l37gSlnwtNW4CbN0Tf8B/jHlMMliolffiNWgb3kBBxqc+UOycMqZDwK4faLicJJ'
        b'vtR+dFSoVMEf0UjfFh2THpmQKB9RD0/ftilSHjNGUf4fxBlAkgrajZg0Iae8dlXHvDuWTXBgvX9/7cpkm99+9OI1w4scnfq+f1egGS/MGIIjWJ5h5sF6HVtQFCKhNyC+'
        b'cnSoqdzbDHGYveLBy1MI5C8xEV6SKcwhqUoANE6XsowJaOEjOeUQ7CASzDK+y5gW+HmB08togVMX8WE16JimEFzBMFreRWNrS4ZdvCBwnEjAoBU2gMrx1aHso9XtB30Z'
        b'OBYi2Af7g6TYfqvT2sPH3tPHfyseERIgAxb5wGEPtN1EGApnOIHD1OS/f9cmlW02qIcHqX12kj84SW8wDsGLsFcGS+0QjxSECwsz1Zo9199D0VLnGQJm5l7imNgJbd41'
        b'YwN10KqtlVe42qACyfXrQYNQB+aDS7Rjp2ArGBo3Qjtmjhkg9P8QvUuu1QKn5eML9A3GRv8Kt8G4g5grit0rBMfn0dWe4HbuKU5eiz4+syU8JnAgWd/NoPH9xgu/fr3K'
        b'zHeezkaNFA/NkermFt60aTPTHLufWZM2L9PVwFHvXGVmQoV7I6g91vKlzjE/Nty1niusFr724Vw9vQPvZr2+5NcP5d+9cmVTzPH37CffuX80L+Hkgmfj8uouFDrGPPfm'
        b'+steHv/KypO+tR0Kbk/6lHu/givY+5ln17JFtl92Lfy0Qe/9Jbe9b3bP+3yk8sKUkDC7cI0/qn+u/tz3RSPjtD+1eUbHPmWD+UETdE3KzDwzv39m5VeTfpkSbRHv7mph'
        b'yCuWF898xte2asrqa6vBpeuXayuHzh25lrlFt6cjLOILA41jPss+2Pya0O7a4rTvXpAVD/ZWGG5mi5p+ydO/Hbml+NADXupIYHLq9yOONWVh3XddvxB+faihNHDe3VNb'
        b'lt+7Nufz23vv+vUum/B2bFt7S/v8q5JtnxgkT9PsEhad89AMcdrRfKRO9PyVjsCPg2/ULT1ytvnPVZPiXb5cOJ/98KzO3jokdzXdfyvbYHckcOOeCZ14zX2nTVTTgW3L'
        b'c4vAydX5UUsHU6y8Uqd2x0Tbv/97nOOm6bkpekv9FmQGPWdStORLifF3v69LPv5STll/nazvpx3rn3N+o3L94tS4kjV/OH+7cVJiqPcC+Rvbv4vPqd72+aSyRVa+wWzW'
        b'D8ye53ZVBzc8kB97yTP4eqz9+5MLtRJ9z770uWTVRwszM7S+Dd8cqdf43uU37pj+69NvM34rHpi/71/PBFV/s9A1OXh2erJLXG1Si6asPuGrvP7p7z54bejlX7J89PXn'
        b'yj/4Tn/9iZ82OL29YXCv20m3npErRys3nH/fLfqO3o70gfWf+T5/7/uWsrffid5Z1JW+N+H12XZX30l6senpZ78aWP+23Y/yvBG70sDziaU9rp/Pfy2et+Xaoj2vLFgk'
        b'1jkQrbN26z31YmdRct11ySxiZw1PG8BT1JjxcYaMs6eqTBkZpb+e7hUJCttJWKipsJ2EXWIqJPTCi3KF5JgIc4nOYDB0NmEZE/zBmUngxFjjPWK4h1gXGkx90+pdVMhD'
        b'jAs1dl4AzhGDWD5iynLGWnYu9Bvn+A3xlsQ4Mc8THMPsNeWtsemzkr/OjKLi51m0UVTMhfuxq2niZxrkrCLc5dx4MOgCC1VM/XTYv4hKgr1IXq1Wcii43wFOqJvEEw2s'
        b'4YNeV1hMmJnYreCCCMkbZeDCWkX3RPoczImANWTgsLrnBDYTT5UgfjuLtQEN8IgPPESq3wY7neRa8LLKbBE0x5NRE4LOeDn1ggYHwH5fbD+qmcWB00iwIDlDM8BBatc4'
        b'w5zaNerPIA/c4ZAePDIZ8bcChgtlF8EmJJQSNUJdBuJrHcAxFSMdnEJdZV9OQ5uhyvR1KrxIrV/d/UA24fIE4Gwm8cvGgCuwnLrl2g/qwDHC9WqCWvsxQgPMhpdUgoPR'
        b'WipiFsHB8LHG7rB5MawBfdNIASFJIbDYGQ3KWHt2YrcITkAqLSZGwtJR1ljdAZxFrLEBaKOXAeWgcavK0ZARB0sMLNwhZZv1FoNWOfbGj61KC8AganwHi3p7kspDvPmx'
        b'WNgvRcJ4CLiIHvay6ETq3kTYUFck+Oeh7lSI7H3S6FvpqPYJBrzNsA+0k/I59LwJS4xUnBRqgCEtLhrUormNp6YREgUuYrxWt184PDvOJ13RzHR8fK5aqEA8PIJ2AF2g'
        b'dyziYbk/Gcup9npEhJXAfWNEWHAxhrL6/eDwHCrBKqRXUOAGu0Ae2E9XagELhomcCnNkWFTFYuown6IOjtpYjboUDOdgo5PNKhmRPdeAg7BchRXJBkfHseRmaKoTMl8B'
        b'3ZawWEYWcx7IYfh+LNxnDIdI1aYp8Dg1fU2A9Uq35YfjSbMXTgmRbofHVWgLJdRCCqoplKAX5CDhaFReINHbD21Di804hm8BLiXSmVAfiITVYj8FpyCMM1nAbVoxlQZa'
        b'9+IpnxB+JlSXdnSqMR9thYVofEzpTL2wks7ULQaI5thZlqY3Byps4HEiqi9zWSndhgrCDAwoHKssnhUm0J8rSsfAQlDqDveN3V7nuD/OJng2rKTyzkn8fyzbeAkcJDG8'
        b'wnizJ4ZS4Ebe3gAZrZQBVeOU1LBADY1P9wTagZK0YFySHyzEEyo2jZTD402Dp8JokHpYunEsIgYURkyHl8Mkev8PBaj/lcuYsS5hHJSGLtf/piglThIT8URAfnQ5I84U'
        b'iT8mrAH6jwUhLOxQL/LYtzwWaYScJom+Lrxnpi5MM0D8vx5rwhNwxkjk0UNPiPuOB3wab5oT/CnEbjqwSfIDgeI7zT8FPDGWGh4g+eGBkCfktHliniYR0vQ4XWI6jOsT'
        b'qmkTc2Q9JOLpkQju/H18Fr/PZHMn+Q8etcUlgpRCaKKmv0TK+V/ZFCuEJvtxw/3R37dVsaz+OwbFtBMf4QqNHxvw3DAcQ+2j0qmMGI5x9TjMLIl5TkKgk8DnDejXiLrC'
        b'vHZEPNbadUQ01u50MX7bBedLwr9c8a+9uB4NlbnfiLrCBm9EPNY0bkRrvEkatoIi9jtkYCgdDP/vriVGLZBuournY7rsY6gfGr62LWfJcpuo5xiO93/zV8wX8yx5RMCC'
        b'DWg3u/CwWMwyk2A7OAeq+TEBsPDJtl6YJsR/CqOKCKyusvvi/jO7L3zCiJmH7b42+2ZgY6hAeByUO85ymjNv9lxHgo1MT8tMzUCCODyH+doNsBsd4efhBdijIxRramto'
        b'iRDDUQBKYBWsCVyNpMG6EDUGnoWXRSLtOQQovmK3hKghi6UOsDwRDEpxMBoeow8bebAfVEqIgQWsTInD5iizGcSfzAatG4nbdwkqbx95Xzp7LSzngf1pKF8XygdbwjN0'
        b'0RvxPjsdUR/mIIm9cg7ixkg21JZLabRG0Galyofrs7Ak1RnrSRw5bACzCZY7og4VEBOABSEgB9WG28ljGYM1oGUmbuJJcIb4VQ8FVeCSowAJ2sw6uRNoAqUZ1KXkUgzp'
        b'JvVtBhgzxtNDtRXjVp4EzaSZHqBlhSOi8lwmEZ6ZGyYh1c1KtqZ9E4N2nItjDPRRJmN4jhq6nIOHshzRtJ6HOGHYMQ82wqYM4ln2IOgxVXSvH7FLNCuLmzoI9tPhLPAN'
        b'dUQzaT6T6Dkf9a+JGOMk4JyKlqqDZjQmvn7gMspnDYYyaBQYWLHbEc2+BQzI9V8AW9OJqUJ88nLaUPXpM0AZrQr2BZMsK5aC86AHfVjIwPaAhdqgi5BAH7ZpKWh+Up8Q'
        b'3EJJuXNbSROTYc5yJLgwjDMTb+IMGz3JmISC88lSSjFzjtHXBvmEbGHwErXDqQqGrXjSLkN8btKy6WvoHQrqlBupDeWcjuFSdPijYDkdyQ5QBk7JEcGX4wuPjuWg25lm'
        b'PLAK5GGK4xqbFzMG4PxuTALQu4yQLXkmrJAjgq9gjFxXwPK1ZD7DGpibTEcR/W+G/VIH9U2MPhlIMARPUEu9A6hRHXg/dmcQ397sjhZ7KTUZOhJmS0YT/c9bh/Lq0QE1'
        b'nUid99e6gAY5ovpKBhzyWwmuzM+gbr9hBShX9FHqkOpAS+ApB/XSGtJgPa10OSL7KsYIlKxC/C7JCxpkODQXjqO1H15CPHg37AaDiPqgDTe5B2TTsT0OamfKEfE9GHiM'
        b'8Uh2o4ZG1XAQHqUkAS3wFM28WFFvBGylE6coBnRCPA08mThDT3DekIzvlnQfRZNBM4fnzybFMvR0InYu/rB3FlYIMl6ISQQdXqvQQsRD7Ab2hStHWOqwfK+DcsvAVPWH'
        b'tSQz7NOfDrHHEBkjAQMy0A6oXRXoMgYXSYNzYHcarIlWLsbeOSQfqN2zDvYgqnrjsFx93uBoIFnHUtg8TdFaeMYHj1V3moKs2Ec6GV+7hQ6wBxHVB3H3pj5yd7KswHAU'
        b'bKKzaIYZybeYklQTtJBcEdqbYA8iqS8zUc8X1kwk1W3PgsdVs6gNDqIVeVxJk3TQS0jCw4DFHkRQP2blTD9QpUHWFtoNev0UU0iqPg11r1CdzoICWEXycdZILulBpFzN'
        b'gMpNq+030HZeAOdhPc21DK8ueMiIbsIXqdkROA7PuGELRH/GHgz5g0ZEDqKhGFrqTudPNiY/aqW1C4610h+/g9rulMIT4IgI0TGAQSugPAC276Y1toIWJ0IKkhHNGnBB'
        b'TvfhcDpvTsKDfBGHbd+NYFMg7Mukk26fVE1JCvQHDIAqsikrKKlrkaFD1tiMDBGiYxBj7xu0haNeSc7AtlmqqQPLN29RZCR05BvRmX4Ftu0WITIGM8a6wTLYSG6AY5Cg'
        b'0E3eBjlpjuAopSESXQgNYyfDchGiYQgDjwSEREVSmzG0OBbRgw11EY3Lst2EEO6z6L5TDGrQuCD6hRJHpaHrQDWxg3KF+YzUAefiLcUb6nyUR7yO0MAOHgP1IkS6NUwI'
        b'bF8DzsKj1BLnNKyyVI5IPujhoeU6qDzVQDPoILkjXUEtKEYf1jLbQfdaeADU0l3lQCqaw8WIQmFoA1ILC6AEh8XhSN5Gw7+OgTmR69BB0U8GyA1tCg3wIOquPePLs3dY'
        b'Sd5eioTMU/Agib4Dj1o7wNo48naGlxe1i1SHpdOQpHtWMXfPhMGDqGwpw18rBWfmkYasQkdMVSAa+pnYzXrbTBc9MlJaaJOphgdRt2cxSNwrngXrbGkLTxqBYYVNGDgM'
        b'8m1tpXTiVAjXBKL2WSIazLNEE/+QRJMsK8SNdMBTUro/HoUXyDih9YhPctg4kc7n3MDdlGqw20Q6evImgDq6wx8H/bvpaYL27l68oulYk22kdDW1xctdG0MIz5kjXsHd'
        b'BRew2ouUH2e5jBYP9sFhsnA20clk6UAWsC+SPyklUWsvSdXhfuV+CnMEdIlXgSY12gKYTdqPRr6FFAFKaBsr0YD10eMAkX+Y7JCbFMWAQysIpwBPww5QpKgrfg1Z+Mop'
        b'M5xEd8tKBtQreYLli0CTspsn0iUsneSDydiPPY51iOOkCUHJdtDFgey9gi8JP1mR5irRJGZ1eXY8McsQ106Jm8z0qa3dsKs4voqdhfaiCO8jkhX0y40GQus9HOpHRIT3'
        b'xr2B9EvZGj2+Aw8bPkcs/sUjg345ezVfs406gPK+M3Mz/bJjnvaeBxwSjGZFeHetCKNfHnNRdz2Kbf3MI2zrzUUK8z933dh7jCvDbI2wNTDYRr8UuIhsNnPWDKMbId7v'
        b'qWjnBm8D815uNa5o1+qgEPrlThO1rVDhdMhkjQn98gsLLt6fR7u5bOJyhphNfxA0cdYhtGhR7ab5CZZIZgxaSR7M0VKzmMvQIq75yejbRXyBRzRta+InmhnMlw31+N+L'
        b'LqSCzgiBtg2PPn3eks986Uj+3XEhO9HUXXb4MGRS0DbSnrJdQhd4oY+fFC2fbYwLzNmG+NELCldcJBiIObbvJ5MgwGXsdPNdTOp7fvVEo17a9vV5gRa0lz4yw5CzdDxM'
        b'p61MftRGUuVYDF8dxilsJGlgJFVAJIUikx1RS0iOjtmWhg+Xx0VE0kFCOubPGCMmAwdkiwdNe6SgBmb7YkNhYnXo4+0Ha/4qtBTogg0iN5AHG0j7Lyxes82WF8GiKRa2'
        b'asYKRBBf34S3P7+pJu9AFfl8fr206kVfA3+DvO86b55vOHn45CrduBVHrJ5h1XVXHWHd2cIfRZoa57MbvzxrEnV+VtW5t08453Wuy0rczvv4qRqd6+88MFqxob/9u3/t'
        b'fG3vcwY/de/ovP7UhrcLzL2e07XS96gyC4jmvRU9fU60kU+09qvRZmrdBXprVx5IdJNe1kr6LPOWedamiZcn7wyZ+80t90Xhf7zx44Dbt6ustjPqLy5f4G32tP+PxmUH'
        b'rbZWLT5g/6NT/4uOC2RNcHu3+sQXii+t2LjS4f18abTL2bM355ZuuVQ2+VLhOuOnkj58esOH8L7fvxrmvVR+92xXXNCra9f8mHFsd9/Zug0fN6bqtn70bI6O729lJQtX'
        b'Tn4+Kyd+w6R3ywty8jtPnfTh59zf7F6u09A+tS2j/cwMm8pBG6n4RuXQ2x+ufnPLpqsvPdPx1tyPup67ajntB3PLs8+s+LJmhtep4zfDTt+cv1h7urN31QSzas/fU10s'
        b'f2i4+Dv8yveqeWpCu/XB2s/u6ex8vuLVCJMvTT0Pr/SUbX6n8cHM0nVtE5+ZFX3n6uFTeybqTPe/Ofta5/q3W5YV79/x5axVK+e4DZ5tf/WNX6KvfrHqveV5Sxa/+sGL'
        b'PVWVtivf3z7vZ6vN7g69ofON9EP6Ws22BHe+5HRAf9uFV98//N5Q3EDdybW+zh8X/2B4/6TO62cu5Ndunmi5/8S2jKS0Wx/2DN077xT1zGczrV4N1JZ3BlT29RxenOcz'
        b'zbNR4mXv8cllg5tlEg8WRtb8frnPeNbMK+GrN3yR0KIZcDxlw0u3HEKvNqc1vv9y5rsfvv7bmZ6vn5/xtqG/W87PXs++VqIRYu2pwWu++fL6wwatKzZU3n3V5kHl7k+m'
        b'WzWt9x4MDTR56uXWXIPLv05Y1xz+fmPkqXbvYoOc3q4Tz/5p9cqdO10vZc0IvxpYBpfc/0NrZMP+j+MzWu5euDvpao7N7zfne5WI5nd7SrSpSVtvILnlRatAbTboZ9R2'
        b'sTgKK2IVyU3vPjC8A50m1WrEYQTD92BBz9zdJKd4pqWMBAAETVYyOxuWEcHDPA4c0yU54+Q4boOOGJXdh6QOniY7G9QBGrXDAYn8l6UW6DwtA2e81Bh+NDaAPDhF4bEe'
        b'Lcpz2F8QkgkueNp68hlRJgcPR8Er1AQnx06gspQTguI4ElqnI4q29yIOICA1RkxGmQNqEj+DhYVaUekKa/99YaCAkZKINBzoYUNgVzhRL7iCFiQWoKzDo5ZyLDhvgKrE'
        b'MtcOfzlGmcQK7Gyw/bqAg0MLnWgsjxTYK0O8Zjmxy0H1TcQAkL6t1CXLEDgGWtCJrFKHrVtKNWkD0fDkw96U4OWYONgA6iST/2/Nbp58Oan+D++KRzTlUZHJ4QlJkXEx'
        b'5MrY9d96EVf+5/vgm0tyyUt/OO5P1Q+Pu6/64XP3VD9q3B+qHwF3ly/g3yV/1bnfVT9C7jfVjwb3q+pHk/tF9SPiflb9iPk/8cXUtkf4g3iCJvFXji12NFkLHvXsTT2B'
        b'Y2/ifA5fROM38DUzvfbWZfVYfFdnwNNlzUleTeIRHNsWceSTJvmLrY0sSVBVnCapu3yhBco/g+XfRv37nfsE9dE5zYhTXnzyRngJSXFj7p7/JoEmqkxycFkD2CTHGZ+1'
        b'f8Mkh8k27n2MUQ5mASf6IQ5z3CmqxhhtBAfgEF8YnPSIa1pN5aGOvUeMwUWyCgQaF6upcknL/1suaR9BROK7RyHz8P2jme+Tb0HxXThqAxfL/S8wr9wjdav5Eo7htj3a'
        b'UJitMWpMhHfB/EVMBo5DBtsnIMaiGAdNVYAorT2mw+OegR54L/FUY+bvFFiDGteES4aXOTl2gjPx5ZvfRHhEvhJr/enwM19HrH/qXEV2ZXPu7AMd9ecLz+dMO5TtqMUk'
        b'Dwte25At4RRqSFjlLVM61BEkWS/mJoL8YKrpKgAHfcdo/Z3BvnHx3mBvohKC8pgL8RFRVHxM1JZwwn2RxU6i6/6txc7sFVpTY7sdU8Oxm+Zw7ARi1FptTMnKic8mjJn2'
        b'3LjZPUk1u43RJ0PM7y3+27ObydZ+/zHz2xWPT4nHTuJVzQOUKMApjxiZYVyUDywTgCKzxaAVnAhB2YaMRbBxKbhC7+QOghMxMiTrHbLFYYFK+IzAhNNEr54lzHWUwNRD'
        b'TQqrfDmGm4BtjIvJfHHaiOfLmlABmi81zq44rqjC/GPYRObtGw8KfTHqTujHyWGzAcmyVwODmdpXiJHkMUeyjJFjSfnmD06BWltTeQwXwhY9w3z7PBERlrMYzVSwjUVy'
        b'Q/cudSYRj2yVCx9LDQyzMjExYW9Jsjkjxw1M5RUGqt8Ozvg5i8fw1NiZW1aR2j5zwEVYr9dwjRAnzHVn5Jjz3hQcc4NjIn9hRIzo5T/Je6JJOEDqgrnaSHKaOj+Avvfe'
        b'6o4bakzqCUab0e7xl2MuPeCrOTc+5z6YjsVu40/lcnx6HoD/CgzWytTaGoQ68o7Ajq1+KlaOz/FvDjxH/AV2WHv5xE/mMfrneZ+JHckxRLDlP2T+cFXnxQfQ9kW0iNRZ'
        b'bs6Xk0m9P31z7irDvB3BSBjJN7uCyHd57s9d5TPfL2NsGJvbh8hXtQ8OFrPMzTJmA7Nh65+keVrc98VvMtbo6afMgec/Jd9tWpFW/CZfbMswN5i89oPkoscA1IMyWOxp'
        b'G+qK15QjH/MnnNcEfkKL1etq8tNoH6oS+roHvJp8zVV8Me7TaMuBj2qP2kiWfC82rVgQNLhCOu3bk8KQMDcm9Ycj3Mj7vOPlFYPqoU25odefa/0leqbTW8/c/eLOl6+X'
        b'/Zqs01dW+VFfxb5pkZZ5DgvWfxG739vRzPpq7i1ZUIzJ7eLLn29Od3kws+7GTqvkHx1nJaxPvQ+nmp82mv/xR2pb37v7yQHm+Qn+PxTGevwpf3VG0wdmK+tsZg9+UhPU'
        b'M3m2v2Daxl93HF52qvWLg52T/2Ww6+rU8OK7HZ/sClmg4+xRKvGM8pJ4RIyAiom7Yxbfur5m+ccBrzjdqhv0nmIa31dZkeM0/VSA9Vq3zRoz4XvD19w+C1h4YeF7TjO8'
        b'vmrO7w3INHA4rR37TfWJ4A2rdV4antOZKbh2Ob5xMpzZ8Fpvwyfwu6yiL+5q5zvuOfEgIvWPbanr7hZ88NLGVyccPTx948TyEXfbpZcPtn+4xnTkVpHzr873hxfN8f79'
        b'hxtH3+54UKOv6bvlynX5q+s+tfpwyg39K0fOL3j/0DehNwfectyRu2GXIOu3r78Ovf3Wa1vOJb/90Z1b5X+4NQwnejs22q+bEb+z9Uyd86TBjHcb5Fo/3F7SuOnwnTkR'
        b'El1q1NTnB3JkRk4SbCkpYARxnI3jEsI12sMDsBqzcUbgCAU+CkEFlwIumhHe0AgeAoewPYsPmiT82SysmgrOrAXVhMuNk7rhDaUE9IL9nrAUA9+EoJnbA2rtiP1DJjjj'
        b'Kk/PzNTSBmU6OmlwGHaLU9XwXSYPNMJGRay+S0be0lEeGl6BFxAfXeND2N00WB89CQmtxT7gDLYnz2VXgdIsyvNXgkLYJwX1sMVLwbgKAjgDnVRa6kUwvEI2hqEdlIHj'
        b'6+FZantSjHj3A4gb3j1JUbGGiAMHDaOoe8NicAB0y2DrGlgsscO2IYIIbjroA7X0ODoF+9dKzWA3tsNRQmCEuynk4bw2uIjKhQWeONynL9wnAuc52Ig6VUj5/jzYPUWG'
        b'g2+Ac4rR3sDFuGaSzi6fBA/JwJmpqqMOHXTRa8mjYFhgCouzLNC27S1B9FvEGcyEJ/9Lvf1/YiA9jlMePffI4dn0Dw5PbSs+8cNG+VIj4mFNSCLrYI6TT7hQzFfSODnc'
        b'PjHiUPmEM9Um7wpYAxylh3C2uoQrFaO3MQ/K3ROriQmHqsmaXRPY0Vo0yVGdZqLiQ9VG+Fsj0+NH+NGR6ZEjGnEx6eHpCemJMf+UM+WlmeIyp+Bfk1WnOK7H4J+e4mYj'
        b'jznFye12DugBZx46x9UZIx/Ecp3nG8h5UdwYDg43S8UcYvMIoiBnY3kqxwjcf+asQ1n4wy5RJNSZQYrGBiQjYtw6vgz1jPFXY/RAHw/uj4CHEoQje1k5kYyXpHwT8VXE'
        b'U+03I7wjb8Voxl5/hWEmV/GCNpuOcZ7Ce6IRw4gWJtX4iWfzDyaeOD7NTDUJ+JRkU8Zbw4xlzbiHKYszB/9TyurWP4ayhH/tNgbn6aiNp+3M5bAOZqsF+a37v6Mt7xHa'
        b'8nwTXh28qUYCIni89xom3M2IxCvlsZuiPSKFsde91ZmpIzzPyot/k3Ty/4p02lvSpj5MOtO/Ip3peNLhzGv+Melqn0A62AZbA6W+jyEdPLpCWy0C1oc9mXRYdM3HxGPz'
        b'+bH8f0i8RzyWYMI9GshCk3rR0faE9bJRxj1KwGmuV1wCXw4x44QT/hQyWz/Ze2l192byZSqfOA+wfloUkTjs4qBQKbgz+Fvz77dH7p3iosZQFxzHQL5GIOjEg5ELDoMC'
        b'jOQ9CfNIjm+WYK6Z0S2dEZEYkLaT5ggA7XAo0A7kIlagVurhyWMEaznWdU3ClZ/tOHkWeuO13penlCzSBrN0V8S983uBaMWnwvXqYS8ZVgZUVQ/UHG79JOtT8TyrUp/5'
        b'O/xSlmnaLNUTS4JCYp21Z7dHv5l+IOrA1e+v3P+64nOJ9sQoT+cGW+sc3ws1uZHhJlOlI9/uKftioLDX5wPTNQn3fihLefAZr+5dDa3nzJY9GyYRkuOZAxfXS+2ssSJH'
        b'ABpgD+zl7ACOUUoO9yF4GPvTKAVXvGRjWCW4HzaQF8zBfpgtg4ULMm0xx+SHA/+VIJ4FnocVlCkpiI+W2cLBBaqLv9Pc9l0K1iDOWgJOE04GFiJWZg9ogsWcRSB1QLsT'
        b'DoJzCicxaowY5qTg+7vQyYQ5sEmGrVIPdZhLbuH481lwNgUUKWrcinXTRSa+Y24EZ8HhR1YpWk9/aTs2Isbb7tbo2HB8atKLsX+wdIXJ2qw2R0LYcehQv4+tH/Hhjs1Y'
        b'VAs6GtfDfwjF9UhDubRpOE+0smWkiHX/dFnrHXzCWcvB2jC6IXtg5+ceZEynwlwZqOLDk7vB8CPbpobir9zkoVBp1bxqcbV6LBfNlbLkkogbdVQUK4zmRfNzhTlsGD9G'
        b'LVotWpDLRKtHC0u5MAFKa5C0Jkmro7SIpMUkLURpLZLWJmkNlNYhaV2S1kTpCSStR9IilNYnaQOSFqO0IUkbkbQWSk8kaWOS1kbpSSRtQtI6KD2ZpE1JWheHc0O9mhJt'
        b'lisMm4CeWiQwMRNymBNsGRs2AT3Fl2IaaFubGm2O3tCLnka8gUwfUfeJTMYWk3ftxgXmwZG9zJPoIxq2bHzgHsR04k38kd1UQ7nlrWAU3qCIDSAZYnwoaqj2Vf7f2ldj'
        b'Jby7Of82NtS41o7GhnpSJCa8XGgwKPwJx3yKpEWsXrHSPDYh8TFhpcbNMDzFH3cfSILS+IKmZCk6e3DwaRI2xs8uRAE4A52wwNaeZVax6vMdYB0JVrQleJ5oa2ogeoDe'
        b'kqDdikSzEeLrCRyYWRGVN8pcKIZ5K6lLmsop4UrvPaDJHsfkhUWp5FZoGywA9Yqou4qQu7AGnN3pzFG9eGf4DqkXp+NDPbZLWUbfioc20I5oah9QuAC0yeas5bw4hoVd'
        b'DOyDdWCQGDVsNBXg277T4Kw3y+Aw0sGryOGhDgrNZfaga6XCu78ohYP1K0EzUeLyhXyy58JC7LQFds7F7v/hUd6yeUJyqxELr4AaGej0QO3xdOBjJ97TeWvCYC4pennc'
        b'AsUFI+4J6OPAsPbOYFBOe3IUScD1SGizQS9w5DbEdiHIhrnUA9oe52SZt2Ho2DjoYH8cKTYSHp4w6lyifA8JWw7KlxIbuO0asEkGi8JAN/XV5QD3gUZ6rvZuR+ek0iEX'
        b'3LcEx6DfAI+R+7OVCTgE/cbp40LQr9Qil2KbwhUufkIiTdINwqlzLnjRa8YMWKHwzQUOmpHj+cswpTegG7PnrbfGt3P4PnzzLJCtcpslsfMCXazSaxYomU5yuuxWOBfK'
        b'DLb6IVCXut5bbj9H5ceLC8Zh5DXhRSIVmGrB/SofXnNAgSqAfQ6spreLJ0ApGFJ68tKYjePInwaHgkF2xkw8503BESkSvgsf5w2LeNoKgkeoM7UGcAGdv/ZePkQAWQHz'
        b'ELW04THeBmFgwjfv/MknXgGcP/bfXbUkDbiKD7ReiHja9Td1h3rPmtOf8Rcyr2qruWvC1Z2HL01wj03jD7yWkNYS/+wXcZYapfeabG9/8HqU5cXEzYFfJEq/33rRb/K3'
        b't5rdLto1dW7W/zlS/srid34rOXK+8/x+Jv+P6dv1d7K7vti38wPtLPeDOSbPFiaf+a7X/9egrOBfg9e9vTD85A67m6+Z/77nR/jZnc9W3RT077wR9cWaRdBIKl5z5Q//'
        b'p/SrU8Ts/dLijFsRcZ8t9J9f80FMf/6ez5563dRJ3+XX4neC8mZn1Dmsian7uiKp7elnFvo7+kuD7zhtTy02j/v2+Q9adz0tfTHg3TBRp++3b5VmFQ686uU8Wd3u+Nav'
        b'E7bM1I2zrf4+RCh5Q1qrAzysdDOs1p5YW93t0fNVcbfu/Ykz7x87cbr6p+Juj+oHlrINW+x69wQYpYZaf3047eg323988OLOLz+ZcHdAp3BbbXBdr8SEcCCLQBcslNKz'
        b'ku8O6jALYk0vkGBXYIDMG1zZYGNPn4sSOXhC3YaqSU947CXOBKiygMQN7vbcjTitQqpjPLkAtv9/vH0HQJbntfC32HuIqKi4ZYrgQkDFwV4KKigqe4kgH6AIoiCy994g'
        b'e8uegiTntLlpbpP2prdpkjZpmqZJb5M2uU2btOnIf573/UBQTIy9/UuNn3zv+4zznH3Oc86Stim7RHBfn2+bIgjjbupcgH7Me6yhg8vGRf//EXm+IALRNtSxGI+ZC/Zg'
        b'JrEz5sLG3Ch+mlYstWKpwm0wucjQVOJFhFGzfE0anKNnHrp6Yq+bLAqKVVrcfRwoTYU8rkvKAqMLxjnm4pIcJCU3jw/aptMCqiHf05K4nXjHxmjhGezS4VxRmlDMmt94'
        b'0rSswkQxtGGzEEqEPvwNrR4ojFloaEJfzvJNTQ7gQ0POwbYP56GXC13dVVpkfvSM9n4xtGCRPjfIyUMnaAilszLmx75OERNF5eEIBxyPdThMD3iSHrvAAlVO0t7lDfk1'
        b'ZJsRB8z3hAb1BRaosk2E98JkTkArbMBSWTWJMuxaKCeBpdjGA3fKDzsW69Ia+WI741oaSuIEHLnNe/Km4AGJDvaIqS3UMiYiryhac/0od+PvGgyzzh+7IM91SSlAbewQ'
        b'Y3qENjeARoIKPRAIrTImokJ4hJMwx7dKoNkHuR24MR4Ndy4Rm1Y/Jna4HZrAQljQsjGYN+MIlSpW4jJHEhW0XK7Iqr6onWHw5oVlLFTTUtTDxQdToYXHhkrCoFoGrSr9'
        b'BUZEANM+IIZZJUjjAZLuwYrA7donXKJhaquLoVMDm4zknu5qUnreex/sCgynsk8xjeIZVXbBbWVlVkNClYsJK3I+Oa52hJjvmM1+VEl/Vua+EYnU+XoS/9BVUJd53Njf'
        b'i7/nf77SVFTk3pFf+t23vsO+SdaUaY+PtUqQ3What9wRoPjMHk0R/6r5MmhdZfYES7V6VntCkG7wjxVuMT2x5mfviLDhmwrQv0rr4zsiLM6w2AxhM9eEQKagPirK/3zd'
        b'D2Ql+RUuxUeGx3xDP4IfLyyIn36hHwF7KzAhUfocVcdlM0suBVkGPXXanyxOu9MhOjDcMDLMMDKB73N61PLoIhSeq+S59JLgG07gjcWZDbh64tLQkMiEWOlzdX3gStj/'
        b'8ZvO+63F2TbIZuPbPDzf7mSgVbp0JTYkMizyG471F4vz7uBq/wfGJxjyLwX/KwsIW1hAaFJocOI39bn45eICti4ugH/p+WePWMBp7nre0+d+f3Fu4wXkSlhCWoRl/AD/'
        b'wgpCQoMIaZ66gt8srmAjR1Xc0/9ywwKlSwvY+tSJf7s48aZl2P3cU4cvTL3gQnrq1B8vTr1tqdXMIL9gMi+ffsnsnJR7PDFGuJgYI8gRZAhShclKNwWcI0DIGf+CW0Lv'
        b'JZ9X8o6zYZ/0jit+Q1LOc5ahZy4I3xV7HXMYeD0ilGsInRDBum4/wkNpKN/UgmvIHBOb8KRP4Qm/wsJhPeHwD+z1l+NaDfTZv8haDSiGvRd+4ocCgWKecHJPmZGQc3Xa'
        b'4qAa5MOE1hK9l1d69Vc9pfx91sIdbCZpn10JEdyWV0jeuCDkFjf6KNEmLDw04ell89msnyoveCufWZgL0lVXEOeJzMNI5mmbCo7K3CVYabIIASx9PLOGy5k8j10wJ68C'
        b'cyFK//9iOU+mcdHR9jgWiLhYzvcPF7NYTlTYJwEF4U6Bii4fcF0MNk+IOz7zpyNmqux20uCblxg2MHpu4YyxA7O+LdgjzXne81ZX+ebzjl847zzhY4ld+cKlk3/xPMeu'
        b'+cUKx25DY5zDKt9nPHWyJoQCmDOm/6tg7o4wI76MvgqZl3d5lIAMnJJoCKELJqL4C5FdqyGXf1EnTGIlhNHTOBL5gdqYIN6Svk498eGvQyLCnYLdAt0Co37VLTfy8zU/'
        b'qfl++akab98025fWZq19SfcNa7cXVRv+RzAir/jLbeufyHpbOQNOGibDFY5hiYTf5ZxUReoKyqJkrSfOih++8PHTWT7pH57ndNT/uYKO/eQCns6Wubgb3zdAsBh3+w75'
        b'kl+5P8FZj7FEv3heOSBWvNw9HG8YnxAZHW14LTA6MuRbPL1CwUpCRt7Dx4Hzu+WYJwtePq9NUDS85usmPRh5xmaDXDzTUbMTHnwc8FrQzjD3QNWw39In0/fly9xOzBq5'
        b'BRyKH95ZEjIdZ6Sd+Uc/5fYjvVFrDtZE6R/Ur6/N84nS1xsyDxHkWZgGnH/ZCw1fLPl+EzS8eqpd43WxZfWonGBEc3XPf7xjpMgZ2bph5iZOEpx4ZLOqw4TYcZsP5+ax'
        b'U4biBWfwVijk/cEpDus5C1wNsrFnwcEKQ1DEO1lTDE/y3WEHiBDa7SHfxOVxb3F/BDf6PqzWdIUBqdqCB4M5b4Vwh/Ou7MJMdxhT4p3XXOMKLMACWfvTRFMTIk1n6JcI'
        b'5C9gZbRoszZmci4dm5tY7YLzrvSdqbxAYiCEkQu3ZGLrW6NhipHxl7gz5Wjn+HeVaDoSrhQj90fE1RARSpaZiwvDPxJsT1nSI0l3kB792/MQlfb/fpPhurASWSl3nZVK'
        b'byypscGF5UIZiMTMbmM5kFJ2g/VtxQVb423FBaX/bXlef35bnlds31Zc0DPfVlxUE8MW9sbP/693plzChzbTx8sMZGwSVg9DVWwgFJ3/91S9UJdoquiJuGDFRi14uChL'
        b'5ATK68+yltgPWDeEJwS5tuzv+LzHo4vyFfoVghBRIYu3KWSrZWtn64TJPXtUkX+LtA2VENW7ilxUcWukIFRRFsdTZOOHqBUKuSR3FRpbEqIeosGNrbT4nRxpuJohWtxv'
        b'lbkV6YdoF4pCtnHvaHNv6YasuqtE36vQ9wL2RIUC/eiH6BXKK+ko6YRs50p4yMkauKhlq2drZmtl62Trh6mGrAlZy72ryo9NP4oVSrTmdYXikB1cRFWOC/exhkTq2Rps'
        b'xmzd7FXZetmr6X3NEIOQ9dz7arL3ubcrFEI2cO/Lyd7U4N7SozeUuJgle0Od2+MmtkfahShkc8gWbpcaITqcObPzbXUZidBfgeGh0l/toQNaxuHtDZc/wcQC/R1vGEgS'
        b'YamcYIHFwATDQCnz18QlRhIVLBsojLR67vkQ+io4gdmBkQmGCdLAmPjAYGYIxz8Wf3ROILkTK5VNtThLYPyiCUUCK8Yw0DA88lpojGzYWOmNx4YxNze8Hihl7dsOHnwy'
        b'wMmss8c2uCjvjp7wsTc3PB4bsyPBMDE+lNvBVWlsSCK33E3Lw7syD5yU4PfEjYvltV4W67ywo1+s9SLOET/rXYtfnXv8kDhwPRbiXRDfVxa29VxR3kWoMrONjnbpUaxo'
        b'n7Hz544txNzQmXNkhcTSisieMwxNioxPYL+5zqAbJPMAha6gUsgWJDPU+TU9Yb5fj2SLpG/CEmm4wJAQQpWnrCkmhP4YBl69GhsZQxMudXR9iz4jFqwUuVbzSGRFlbiA'
        b'y9JqrE6L7nIsw0I3rmLqKSc3Dy5s4AElpBLAPGarYAcUYisXzj61xWfZCCLNxTHoTVlA9hpmK6VCrhIXq4056YLlpGU7OStJBHI7hFgDzdAgu+wPHdhnooCjOM4uCiep'
        b'2vF3zUdxRsfbDDtxBDssBWJzaIdugYataCt023E1jDSuuiztIraTKUdezuu9TpmdEQn2G8lBqbkXX0CiBedNTESYC32sf0q8K45xmt0NfTGXcZUsDlCd2a4r4ErlYgbc'
        b'xTQ+mnnOj9sT5nA9ygpNscidL1p3MlYB0wLD+YsVvTAH0/FxrAoDVGKxAPKwCpoi39lTI4l/gx4w/OHm0JIfRYnsVV+a/+HG6z+bmDmteVO1JdwzNe1O9uveu8Sga5og'
        b'sfvhxV+4fvL9szU3fhL2oU9JSckupfm7FrZH47c6brmQ86vTNbmnTq8ZLA+s/5+oyzFvHWz8aVrv9g6di2+1d4ZI3tB6reB3b2joGo2/pqxhUvGujUHBm91K2dcyhuyc'
        b'x9/M/suvOrQf7Bz9lfsXKimZyccC94G/z4d7ttjlHA6bulZo/07cP27HvLXxp9X/tFYZ7bP9z/LXXvhRl2KulXnca9975ctfzlv+rUEvpu43OqcuHfzkx7//WnBhrb3n'
        b'TJiRLndNURtaL7sy/fPOKT5pAPIO8NGWTKgOWBZCFKzy0WMRxFho4pTERKhZ7cqhC84thvAtrvJlDksgd+1CYHO/ENJ3wv19l/kk8h6xmaubsbkTlOLwo8jmlVtcoMgB'
        b'7p5d2rJAiPdwFIZhDPkm5Sr4AEdc+SQNI3mBEjRAsa6IMKQZ+eKC9Is0mMR80hI8GFIby3vfIo17THzScT+3bFVMhxmTXZhn6iy8JSeQh26RKcvaZ7NfwixW9edRYPUI'
        b'6wUhSvWGOn7txTCH3aRuuwkFkk1C7IYeaMRKKOe+NYFqV67Fgyk8hFxZhjtmYwcXc8TB3cl8uI91xmEtIszkBaux3hsmJE6XcYiP+nabqcjsBBwmXBTI64jUorGOi9ka'
        b'm9PW8j09XFnlQbZAmIciOYEWVIuhmH7a+VBb6zFrFrTzkFWZPBgtUPcWu2MjNiYwlwJ0qCXT2+zuLiswyd1hgqJdrnTIRXz3JUchPoRhBaAjuMFn3w+eubik2YcQ511Y'
        b'1QwzviV6B/ZikcnyspJR2GwouXgTB/mtZ+/UYVnYNNHCjPICPey8RaPNC6D8yWS1Z0khXylQd44x0O9iUVgrcg3GVbni7qzQu7bQ4GuWNq/KpdcbfK0sUpQF1AyEyauX'
        b'y+2Vm48vCuUlYbVviE6K+WdXCKatU3kOq0T/v1awSp627u/idJf7ZvezrYrM/fzEZIsBNqtFOf+kYF8ixP+FiJs09ZuCQYcXlijdy9LilsrcZf5vzqfI5R0u+hSf1QP+'
        b'RIrx/zcPOM0szRQ+tq0FeK2Qnf59Iees9p6M//inbby7Wuas/n2xkZAn25nd0PIk3VoZMLK1wL5vcVhLs1m/1u2PYUN8cPQl7o7nd/FEH3seSlDtWcEl6UhjuBmRiF90'
        b'SeYm4jj77OZphmUmS/dKasBKfmn9Dep2kI2D35KlzvnKsoXfOUs97Nnc0hKPRDt2RhmYo/E4O2e5jLluxi6m0OvDpzWyX3i6ObtjhaaQNW/KVbHGu6JIvU+3iOMZaYQc'
        b'Vv84wPz9TwJ+GLTzQ9NAt0AXueiw6KBPAn4bEBP2SUBeuEsgjyAVuopCz6NGYk6U2JF2l76iLLlm+0iacKJkN1RzRYZtN0OXijGO6yzLPFrMO5KQHGSoB2Ubohcxb7/y'
        b'Iu4xzIMirFtIYfhmsbDgSpfmPismLveRP+GlX+4od38erNRuXgErWXWiE5ZY8ggr63Hq2dGS83/rH1V3Jv0100jEqew2WHODw1d4iJkCzmnugtO8Pt0fF8e9s15OwPnM'
        b'lfUjsxW6edZz4mLfEy7zn9e+XuNd4+0raky7udRpbiZ46XtKWXfuPek0/4b4RoHw+T3nZzSVlSXJ+k87yCUO9G9ZwNHnOTrN3hVE61MXQ4yROfWeziVYUIylhBOXkCM+'
        b'IbfIJ8TPGr76qvMJS9IxNIFMaJkgXeoreboNfkUaGsbbu08kv6xgJktDExKlMfEHDe0Xe77LIBBgGBsURZb7t5i3K0tEOY9EVqjVCqoMON2dEcFpr7NmZ86ulJ19CZoF'
        b'kLZHKUoRSzmr75Ye9Lg+ZgnLTD7IFMqsvlMqCliYFBopj3cl8Z701vX32z8O+CTgdwE/CIoI6w1lIQDfF3xxqOQHlcO+3XeN5HZueenHP3zze2++6CVuv7zmsv5oTXqU'
        b'30jNaG2+rquvd82Rkb0FHBkU/lYr6MMRI3nO9jHbvdnECbpg9tG1EhxfxRcOL9rDrqcsTdy8jAWiVLJAS/gHJvbelBldwdCxYHcxq0telU+JzNxrzuw1IZnVxbzBVoHl'
        b'XLTAZjdmubp5KGHDQn15lXMivC+BTr7kQzpO+3IZn/uwbwXWi3XJy0j46Srr0kIQ7HaLDG1EC6LvO5H0VVXuxqo6XxJi7WPUtGR4btYeWdYa5y5/pF6vKAh6RPxjj5Rq'
        b'JxrC53koX7dmBcr/hrU+neifyK34DtHqr8ZXJPeEJzNcYsMWbkv8+6nfnp/zGal/5WAdaaRnzg/JxbP4+YizzccB/i/8+MWhkuGqlqxN+btr0q3WC3ZB+y8lKX/8s5GI'
        b'L+dfYpvsSkSWxq4cLeSVEkWtxUZJ8o0QzhI+zao2Lr1/gGNQLIJ0mFRaiFetHGc1XRBRlt8RmwW3WYbmipghOxp+FmfRgp7rIlo6acjzIKd6zjMip2wJRjxdvK0QH3gt'
        b'9FJgvMfTnccsk1MmoOQ5e0j+O7qOSZn9VdBKruMFxGV+9RBZtfpnQlv7xRhAaEIgS2QL5BN5rsReI4nHqssvjPt/hfP8OzJgHWQeZs77b8rcylcS4xOYW5mnwfiEyBg+'
        b'vY9ZuSv6hXnLd1lSFnP+0+Ar+aQXyY2tVRp4nQcX7flbqIzh85MuZGWPRKZzHcEWqP4mIWuDDQu3oDghi8WxXMEaT4mZCbt25CRwxntYCQXJXMkVvU+M+FotEoGkVtj0'
        b'asJmvt7k1mDuqozguHuAm9tuocBH+ilhAleY1dsEckw8aahT7DJsIdZh9rbIX7rGieJb6Nup7XtPv7pbWWSvKvfj5pA3TmuqqHxf5c2UKrPjxr/5scOpl/X07geURxrc'
        b'TbgY+GHna+eMmtud3jucXb7fTttx6k8vh+zcY/pp/wdjR1t3WK+r0Jn/qLRgRPf4u8e0oso07/9kfdbvMxSD1RML4r3+y+svL5e21XzgUH/0ZELZjjOH81bHWlwscH9j'
        b'/L/w958kXj7f8f2zUYWuV/4xXmDj8/s/DSbWXDhU85nRZMJlI0W+MtxOLDJxMk1VW5Tz67GZ4zwXscHvsfsZB7AjFduxknOu+mL1scd8qyTjndwVSTLzztVzWgQhF3eo'
        b'gBre1wiNWA05nKA/sP+oiTHvSRQKlGxEWIG50Ew6RB7HGu0UBE/6GWFCAgPXnWD0NJ86kAkjsNAbNo31E5bdcYUOyOJ9fi3ylibQJOEcpTI3Kaubv7KsNZJ/Vl/d2wqy'
        b'C7Ecg/X6zgxWVZNvpqgsNPhaU8x1DhFK+N98LRFp/lMiStZbgffRhMucdJxm4Cb6di2CLIlHzz5SJTzon7GMWx/9jtxakK739xX49VPWTHDlvIMcw1ZazArno/s2LD9A'
        b'Eh0YE+7jEKywhPzZlrQXyP8M4+HscifzaClzcVsWKxZla2RrZouztWShQe0wbRlvV8hRIt6uSLxdgePtihw/V7il6L3kM+9x+tUtyQq83T4khCWSx4ReX57Vw2JifPyN'
        b'DxcGx0qlofFXY2NCImPCv+FeJ3Hcg4EJCdKDAYvGVQDHNZkMiTUMCPCRJoYGBJjKUtivhUq5hAkuOPzEYIFPDQYbBgfGMF4ujWVJFgu5swmBUjoLw6DAmMtPFyjLooaP'
        b'6WIrxgyfKma+STQxQLCgZvzV0GBuh6Y8lFcUNI8uMMQkXgkKlT5zBHQRyfhlPLqJcD0iMjhimcTjdhQTeCV0xRXE8mnfC3CIiI0OIcReIj8fSwq/Eii9/FgAf/HQ4g35'
        b'exTmhp4skfd6ZDy/AlICImJDDA+GJcYEE3rQMwsqeMCKAy2sPjgwOprOOCg0LFYmjhfvUfNIkMjy01n0PXDFcZbi0FMhuZhXd9Dw8UsWjxKPF+Z9WgKybKwgy6AnR1l6'
        b'VeNb3mdcgnQXb0/DfVbWZru5fycSpyEiDAldOKqFsQj1eSxZOR/6eGhYYGJ0QvwCiSyOteKJ74g35DXfG9+m4Mgwk23lKpkW9OkZ1LNleo+GjOkt13t2evD9BO5YKcZb'
        b'SkV474BAGCtgF85u8pe1H0AD1qhcixNio6FAiDkCbPAxWqi7N+UIRcz/JsQu6BWIoEh4bDOMct6KG3Za9NZJXm3aaW62E3N2GTu7n3SCXmzCVp+rOJJwho9nQ4Wx0gFI'
        b'D+S8FTexlb2zEIK3h0zXs068nfIoAB98URFa1l/kVCkzM1WLIDFf7bzURo+vIQnDtzUkl5mKsRhC5xMJTY3MXOQEdibypFeNYCdfzQQrYNIEy+QFQi3IlLCKI1VQyw2u'
        b'ESZ/NEfE1wUfvWbBFy6JPis586qsQPpH6x1lpdSvi6M/EfElyr1VvQV8zfyieGjBNpJFKoJ47FXZs5MrdcXXMjyqdHBGbMgKsptuVVgjSGTuAZz0t+buxns7cZ5jZ5Z2'
        b'aMKUz8WN0BdOpi5u5s5mxluvyAsw30g1Dhuvcurr9ms4w2uv2Ou5RIEtMHJxd4MeH6fF4DDzeChB2zHscjBS5O9MZxFIpiDvwNJoJtRj5jUOSAm22OCKeW7ykI0z3N1y'
        b'KMVK7m75eug+ij04vXi9nN0tx5YEbtjDWLOOb+qHTVD86Hq513buXWd7qMCSvYsXvdk1b+jBRn5JhXHWC/e8Yyw8F655w7g69y6O7b/46I434U2HCGqu4yh3xxsK9CHf'
        b'5Mmrl1glJ7vjjWVqRir8QEPWUHUAHi5UJeBKEgxhDbeIk3Cf9RpZUpMA+qFGlLLxOPf1nr1bl6SY4r0rfJbpehjgwOYBM/6uli4iLRhcqElQgVmcq9kJZ1x5d9WD/Zy3'
        b'yuYWl7ctDtJi7rpVFx5VJDCStT2ZsnF4VJHAC7rcFioSxK/jkgCVIQfaZBUJcBwHF9JasS+WI9hdIb7LahJAr4Eo5aAjd03/MNHDmMxPCGnQzzkGuKvuUAbN3F5F0HRi'
        b'mc/gYayIEGkM+rh6CIdgCEdZWsspSIcZ0qzFoUIb2nAm93IiTOh7kx1VAtmKp71Y7z8zITRhKZRwdQY+ipI71yziiEp1dvtevrYPFkB7Cu243JOIuU0gUhXgPHGkAVnn'
        b'CbK0miXx6tJEHFbF4W04qwF5OJkgFOhEiZ336XN4EKd/fPEJ7ut4HEtkF4KZP6RTjMx0uMcVX7Lcj9Xco5kXFp6+nhCnJFVTlxfsFEvwzonNXB+IM1CMs4RlOBYfR6TX'
        b'TcZFoYY0USzQMRDv94HCRC6TIJ2shen4uERlAlAzN5gGjivhMM2uGkfIyK1DTnD4orzcqSN8nYQ46GcvcA/rByw8oRMqtneBNL5o2+yx3YuP0OKgDXL4BW6A+5LtEabc'
        b'QCetsW7xqYsHCSJSHKPlnRAfhClzvoKC1E72hNiVRiJeLC/QlBfhfagx5FKUYpSiVHAigRahqqQmlcMxrBeo3RLBKNzFPL6ERcEWzKcD9UrCei92nnI4LYRSyI7kBrCE'
        b'5iBvdyz1JsKvxJLd3lDIqn7WCXEidRW3BjsY2LR0jlgslU1RuzOR76a5CWp1b8bjhAYZFiLsFBoTUB9y4uVwgATziTu6wn0Y2+Xu5nmayZJTMivdlPHKAmc3zCOeAXdO'
        b'K8UT3+CILgxH/V1ZwXbhweRoAVYchHEOZsp+hIujTsQvXM2Iujwk0IXpAi1oEEOVPZ8sb3hgneiCOIL1sDBIEt7muXjkamMLc1E3+2VQmShSwDfoEPzlsOzDziNGEk7C'
        b'HsUuLGZJWoIbggBMuwElyHcA8yJkuAd9JJGTBdB+Lvm4hC+x0e0WwreXMIaeJOjle3/Z7qD3WLeZSIEdTkZCxwG+6/f2mVlxPPtY0/z5lVM/iPnvI5oDE3a/Tn2pdqtV'
        b'3BeVdqVTrZ8p/ELT8A/bJOprTzQdEYxbf0+UqJ7+1zSDX+TY/F37zo/ee+HjLyRKSn6n7/d+OZPc0/WVXOW0VFn46eqi3IrzX/gafPlW4JdQ+8EO85TOQ+3nGpSOvxui'
        b'M170qmXn2VZbr9JXol58Z4uxRtpf9VzTTv71pNJPdx00+O/XPvrbKueombq1G/Uieu/mtb9n4fjpKyfjjadeObD2xf0tCWMW48dGLd/3VQlsrSnfXno0368pSrv99c7s'
        b'qcEf+DRrlmcPXpMrzHiw50Z8Xu9fm+DA3o+t339XYYfC17Ync3/X3a7nGGP9/fVffaF+wedvJ87YVPa9vvnyh+19J/4ql9RZ9lZ+0quC/f/7wg9fiX398odxk3Lu//HL'
        b'Wh/Pad95X9WTjgN/drMN79vyceafXd/46I1d5+eD/tH758u2U6qffbHFZpPCUfvoLov481kDL5wJrMLPq+N+Gmlz5p1rV/5av/ptp2vN1seO2k1MZ5/98sbwO35f2f7w'
        b'B+9tP7j1qsF/Kr7wQozlX/IV9GI//el4+Wd7P7zymsWq//jb6Odmflt//P7vfvHCH/43x/viTEGvV6j3yUPvGcSOvPafAaET1182+a373tOl0heTvhf2TvDFgaBVm2/3'
        b'QNixn9zohnL3NR/9aW3Sjbu5/T1DjS8nBVz7nkl22MTXgfMf/flzv/v3JoxLc0+2/3X1+dkvRV1/MT6k9MHJUTOdd99z9xg/22FpfO3ex2Z/v37j8vHZV21mU/4rXb4t'
        b'zLPT4KMzKS/f7wnRuxDbtfs/Y14uyu2vi1m797Tdul+W2RWOut+a+7zl1z/fbrV2g4btwWmrVbG3J97+R/bffq16bkO+90+u//JPoibb9s/+uvFHal+Fq3kZmXPBa2Lk'
        b'k9C+LBgrT2IkV6DtLIZ7MIGtfOn/qtX+nBqBTb6cFhEM1XxCRQ7WxrkuhMk9OU0jX0mghdliKMAify6fap093pf5hqQ4szQERFrJOF+ZoTQK77PUO+LSpY/K52Dvec4B'
        b'dAjzvJblicm5qciyxEhgPuALcwyc1VSD2sVUNmjEe2e5LLbDeEeJy2IjPle0UKcV2zCTy0HDPLyf+si9dI++WOJicjp6hlvgWswknsVXZVPAGr4wm2hzBORwk1tvws5N'
        b'viYe7lgoL5DsEZIyNMcXp8X+EBjikvOgE9IW/E4w7s6ntg2c3kCqdfGyBEGuzAXvNIuz1XPlas9W4+BC/VnM8eLLz+ZfxklXE1J0ClzPuJJkviHaCnc1+XE7U6CTK3r7'
        b'qBovdl0S3drkwQfdmq5h//H9S/IZ73vgKP9qDmYaL8lH1IUmKUtHnIZmfto+GFZhhd53KfgbkXLRKjyNOTDCgcGFXqtyxeYlN3Dso7kTNIahRMw3RcKRfAKGuylJFOgR'
        b'6OwSk5zJOMLXgOmy3OnKsvxw4PqScB/kQi9fujg9Euc53QuKNnO6Vyzm8lVdChxZ3RnMWq4FJ2Idt9vAMEwP2rhM0Y3HPu5Nk0gc5hXd1C2P1Fxoh1HuTTnM2XZebZme'
        b'K4E07k03f5MFLRfy9y+quTgawr15OUn3kZar50E6LgxALtckXukQDq+g4wZjqUzH3YIZfOZnvStWs1FMMNecuTRp9RqYJo6Fyr3cWVhgbTQdRe4uT2y+zkoV3hIZw6hi'
        b'wnb67jZWQcaiwkPKThyOq+GQHUwLLeGO0BRb5ZSCgznfaRjcgUrXhYMhZbkO07BMBHlQAN08kQyux0FZmxLI3YEPdjmzdt2CdQ4SorNSGOKpuGEDZHMFEfcS6QgUsAUb'
        b'D4gUYToogcvSGIEeW5nMxM6w5JPEXRh/8NwCeXzdFb5erJwIKgQ6W8SECHNYz3fybmP6Kv+QufsWIoY8Ut9pfqyRkKlbDvl8DK0fuuA+95inKSn83aQV0BmJBKv3Sg5H'
        b'WnFR43C8d/XJYp2001yuYKdcgK46B/xNUO/LdfPKk4dxHnNUoFBEe2pX5oDv732Q84jnymOpKcHeQ2RAuFzEvXzivMNiwi4yUjKW51N2g7GKA5UL3r+GoxrXzI7Z8/xQ'
        b'CXtErDWkBcc1WNnIbjoQM6OdDIHCN7HykSNQ4Gak8a9fe3rkCf43du9eGlIPDAlZFlL/iulY381Hvk9fqM7lteoulodWFW7gSj4r0h+Dv2orqooUhbwnnRWh0eb6bPN5'
        b'rtwnkfzSUjJCyV8kKuym3ZKfv8h/orhRkRuZtUXR4/zZilxBaQnnk2etTeS/kFfVY53AudWwHFvR19pidSHfFIWVwlnLla5R53Jv1ekNde6H6+b9tbJ4hUjmEvDwHn0l'
        b'3i2/6CeXejJX/aKHXOq13Mv/r9X+VuDneTQwNyM3mfni3FyEwIc+5T1fhMD8V88Q0V0CByPx24oLQdRHNwmDJYJH/5MXLPGM+QoE/I0gPiygJAsLCLnAAAsLiLK1srWz'
        b'xdk6YTqyoIAkRz5DkCqXrMTCu2cFN+W4QIDklpz3ks+yoIC3aIWgwOmrsjzf5TEBzjseKPPuLkaCn+5pX3hi+aWhBJmjeskQpjJ/dXBgzIpOzCAWjzDk2hUxh+PTow/P'
        b'45hnoY4VZzVeWJ6xIXcxiPOhLqyD94jzS2LhDVp6DO+FXtkpbngsNiTUytowKFDKeXH5DUtDr0pD40O5sb9bhJsDoCyG8XgdopWCDzT8yvUyZK7tBcc+86V/m+/3u3p6'
        b'V273s5GPcEPjiXOuj9qin1wS4nbQeKzOJxQZKeGgt24iy/VIhmrsWepRdWIORszx9F7mWlWF4WTsUoLC9Tp8R9ZybIEOWWw84AJWemEzZzl/pqoi0I3OFJLl7HbqgjHf'
        b'mGXI3YhrzLL5b6w1i+Bn9YnH6beau4NNoJvp1DlY7M2coe5u0HSeE7hnn8jnXW79i0+rYWcC5HKuNazXxwqunTBkYrq7wB3TcYC37t2D/xb1H2JDicAiILTG6qE1b7+/'
        b'WXvEh/v6j6bn9omEU0JBQFpUUuCsM/+1Q+sRvpR1yGXhf29/RSwwDLD5+6YYAdc1EsfdrrNO6aYulgJLOchItGeySvXC0vtlmGPmEpHijuXMrUuqo7PMYc61OnI96eRi'
        b'6sLXpsNJLFZzwQGVRJYHTqZWWZwsTQGGaLhvyAfk8xTEMGok5Nu1NmlCOV+NWMFHpibJiurDHZzkPHnQbAKZj9VhLdydcjElcTd9uxbuaMgmd9n8pJN55+J7kA4PlVJv'
        b'XuFgtE1RJJDcHCZmG+D2I38/mafkSBQPQSOjM/pnRBFCwZG05Bq/j8OkrCgB5yw3kuPbbd7fIM+5T65A9w3BDQto4dGrG/MOcpogVFkmC5LxIWZz0Id8lUDmP8F0SZIg'
        b'KVGV98cPr8Yxzn/i6RQpiIRZJ97P3LkWppj2S3iTL4/z0CCQ7BPC4GkbDhqSQ+ddlxTeU4dGc+YWTXXgYdUTSZPyFgG23ZJ5v1thJHJj7mei+FaWL/V3L7uTNjE/P6LZ'
        b'+NaFW2faD1WE2OS906n+i67X5PwlQn917SMi/xLRL364LzDv5KatCleH+6V5DS9Wf2Zv6Wr1UtoLn8xOxv7S1mU8O+d9+U9+17bp9+Yt/7Fxp/ukls7vBV0fvuhqVNif'
        b'8pN3nczci7vCGnwbb5Zsn/ne65+/fHjqizbj2pOh24sq/nx5TdqmsPZPva5ZCOcF6T/5nRkcu6HyzkeOx53+fPrwSzGan/yhyPo3beovbb6hmuVu2pP0+y/++a5knUHl'
        b'pmDXi5cOubxYFBY9GNiXsvPDjA6XOMfx9w+vmtwTvv9XVVG/2Wp7+Ue9A/vfSrVyvvTu5M0vt8a/YfeHV3+Q3fD5F85rVpm9e9N0x7sb37m+96s/Db9hOhvyfuhw9rt3'
        b'j75018/u+u3Kn+U0a782fS/vjfC28xUvxjvXrx/70StvPYyrO7DRcFPznvIvTpyJ2+QxrnrHdPq9Ec/GeXH6BpHlS9sutK/dc3ZG1app+OdHX9ni4/9fP33xHy+98fqD'
        b'hKC+nO0tpr8YfLM95ZXBCMdPf3TjK5XhwMPvvTnwm9uTJw//zOZe/Xq3crNq7+ulX9xM/GD+a/HO0crEsi1GerxFWiaPebwpexgKeWsWOvfx5nd7QOBSY1a0BTKgBdrF'
        b'nOGjjCUw92TaykWsU1RU55NGcqKgRlY4Asp3SwTy0aLNZ8kE5BhTpg50cbbuXhjizV359Xy5iVEcxzHOF4EZMMz7I1J0E5hvmwh9CmYfq1SK7eaP8lazyOBlo7gfwkxi'
        b'CqxVJbZiHd+uUt6WM5YjiLfM8A0r+W6Va7GLNax0lzWlhNJEMpj4pjZwT55vSskqdXKG5X1og2rWnmax6Q2OQzOUr4V5bmYxzF0zIXhwdrzSerLCV0HJhvP8jb6mBBjg'
        b'auPD3HWuPD5X43OQL3vZjzNkqcosfSh1l9mUnKG/3ZqbXQzjjszmhm43WTqRBjwI2Sf2T8Jm3is1exxHTDxOXeAzIYmbkswwkResg3pmbs7DNL+QCpjZwUZwd/O8Bply'
        b'AnkDkcSUbGfuEl+zjSJv5rkz1wDPMHmjcham+CsZMziFZC1iuz1vVy4zKtVPcXD2PHtMZk8usSVVXQ7bEijZWs/GYP2iOenjtrz7g1yAFHL4yqYPsMFiiUEnIhv7AYzI'
        b'nfoXtXedf6MF95gZp7o0GYGz4+4zWfCd7DiSpOaqnCXFt5Lkm/uwIqIGX0tEfGFRZbGyUCJS5Jr5SIQLf0uErDml7F0R33CSt/Y0ZZ/4ZpQSDfnP1Rc+03/1uLm0uf+S'
        b'zbHu8csNS/bEG1/yvNlzetEUYpbHEmtL8/8axEaSJZOZL87ImVznmOGhulBY5juZXIJ0i/dWMLq+CQALmWF2bDmHRCsYXExJ5RRUFwGX9S1HJhZfaF/EGV1iZnaFqS6a'
        b'WJJnMrFYOQb7lXJqF0ysR9X2F1Nkucza/+NccP6dhaI0/Hsr1Jk0NzzGp9RwS3lKqhCXOs7sMHrU2dvzwD6L3czuuRKYwBJC4hOkkTHhT10CXw3nUXrM41X++O+f61qK'
        b'okciy9jHOejCqidzZjEHMp+ijMKI1IGL78rLQ4vrpvOPqkizYLUzDnJfkspszUWrE6B9sYh+ir09F16MkjBXdxhkLC1RzYXCMUsU+VHA+3Lxt+mx3p+NmOVt0gMLXcmX'
        b'sa8ftU9/4f2TTpLJ95RPrso5ciHK6fvS/A86737Ze+2jV1/u+ZnF5visfVvytvmkrP+lauc/70ZvLPdUbroSriPe8b34IyPv/SFpw/eSTu+Ial6z6+28tx7q5vdd3iJx'
        b'04v9ajQ2+vtn+x9ennX9fei5jzfoV220Uthi9OsxIznOg3sOp0n0O5mqQtaikzzlCue9C7EjeZxv6uGOlUsSYlOx8Qwne6DaRXdBq8AR6F4S8dhOop3zVDZdvM1JSRzF'
        b'kkWfOC8mj0EZr7tUHSOdlPO0C0Sk53dyvvZ8nFx2q+Vfkh9L2Lt6Ikdsyxi8x3MweGLxa3knHN8reIHJK3Id25LXP8Z/ls+6jAUv50VLWPB3K39N/JV73245k+X4qz/9'
        b'7oaqrI3vd+WvgvTNn63AYb95h6zYa3LkVeaZ+XfVgPyq58kEVmlwROQ1WRUgWa3aZXWHVmChx3inR/QNzksSeeVqdCjz84SGbHoqu5Vt7PH6N/TrZ2lwIliRYUk8EtkN'
        b'd3msxlo+ovWU/CiogTLS8YNWK0bisGJkm8O8JJ7lpqW5fMGql/q+8OaLYyWR7sM5XXeN5F7WDo4Iiw4yDYwJiwj6wE0syPyZQv+VC0YS3qJ4CMPJRPo2cY8uvPUBX6/D'
        b'ASZgeplJQfp6B9kUxTDO1xlpc9dn1H/edrlVoQglOM7dMiau8VCHCJ+ofhgLWI9I3q3j7B4ne94V+qDORwGG1kDOtzZT0wzkT3cBxeJFCzj0HLRrrcru+2x83DX72AzL'
        b'Cq5fWE6dy0tNPnqCI7hL9Kn2+QlO88crENwzLVb6DluPnIeHj4OH9LKAU+S+uYDdo6oX7H4td9WOu9LEZcpzznBOPeN4CLcvHihr/t0a+TMydOlR+qi+cP2K1bRTVtET'
        b'ijYur0WnKdHUVBTpChU11IXKynpCxbXyLFBB4N3+tfYtc6F2jKFQcaMu3xELR3dcfnShe+Eyt0iwc8fNG3LX8O7RxD/SnO7Q5wKNUGYXi/UWmiQ8J/HBqv37IC0YB+UP'
        b'koJRCmWKZNg14p2NakQTmXCP2dbHj0OrCpRBnnAdkd8kPlSD2oM4BkUwEgjj2OOjxmLBGThoZwsPYcgJHjrSU8WYdwMmoQf6zW9Cmxvct72Jc9ilgEPQSz8ze4k027Az'
        b'PM5yG9buxjRsiYEmvIs9ZKTW37SDfOjEXBhe7Rhn66kH+Vsw7VhqlBUWkn40GWmLWZcd124MXOtw0FXOzzLF3BPa/AzMoBzHbWEau2AUSmKgF0tZAWQnmLC+YozFlpew'
        b'QA07Q3BIh6T7PSgjVaEVH2BVwDGs87KKgsJgHJCHJpjArFgYJsu5yRsHYOj6FWyHh6lkKFb7QOkabL18Hqugff8qvO8EDyyggPZeCkVax2HQGzJ2uNICJrDuAAymYt9J'
        b'qBViJ9ThHbKJG+jvYni4JgK6sQ5ar28Qq0AFjGGzpSm24UTEAWVbMvazgw0gzfEK3A2hkavdYdYo2CF2owMWMb9YvQtW+unDQJI9TsEIndSQnTzUnDQ6TVvPh0rIVN7u'
        b'g6P62IKtrM+FO2RDgy/BoxKqTXHywKFtdlt1dXDkDP2iIWXHeROsxV5NHczGEhj3iafflqorb8Z5ln+Mw2Sej8OQAKutQm2w1h/qLWFWG5vVg9yhKDzhEKadwuoNkH9p'
        b'nyJZ/lMGOjAVDfPrICucXu+/SiprzW4DbA3ZfOac3S4sJ1SYgs74QMK6KqzzUV3jnxxjk4JjBhfWQ50HtK45j4MEomrsVqTNjBFK1WHrESxQhOwTOGNBJ1kFfda0y35a'
        b'3yRk+NIhFJsdJozIS4KR1eswj+DzAO+p3xLjLOY6boVJr8R8QnushspV0HjKHooI71VhFkdX3TxCB9x1AtI2sHxsM9U9eJ+OaBiaxCegMzhwixGUREgg3/D2Lug4kJgc'
        b'oUGSIZd0vm6CbMHVgLMwt8oX6o5AHQxDO2QEYoMxVptsxymcgUkxDClhxTqcCJS7io0wdtrv+mGsT/WOhj6sJ0DM7aRdEIrgQIyrDQ3RZAD1mO7lS2OX+UL1fpKX2UFE'
        b'e+kia3csgyEzemYEu6E39Xyqjqbv7aA9juHYoHVjjxYO0FbzCZcziCzu7CW6ynW8tm+j29Yb2wnfiqEW+3cTnvcRfk5hTiCWRcMs7eoEPoBcBew4hGUp0Jzoah+JAzsw'
        b'eycZF/M395vfhqyLSt4wpb+BFU3DLq0DklicD8AREZYk6QWewLswqgwFt5ygBtMNHKHID9IwM0QDmqHb0/u0ZbD29jXYY++orKttbiG3zuo0UVGjG+Z40wHXYK8+5BBb'
        b'SQvEzn10kg/gDmaKscyD1egyxAYPzPPFXhiVaBHy5a2GVtoG40yZlywZbCEH+2HsetIaKNxA8w0QTnUnETpkJ2spEjmMhmEFTt+01IVyguJdOp0h4lzjiuHqLti8hpSF'
        b'e+fOkMJQAZk4ufECzLm7wjx0KW2FsnjiCZ2QZR2Ko1cw1xfmzNcyJ6C/J0yuI5Trw8JTUObqouV/Hcdpvk5ChabzkE4ENE/bSrfEPp0d3ltXeUI6AXzcDzuiCXTdnjBi'
        b'hFNyUBO0FVp27Ev8bxFTQ+LIZmg8ZQfFDB9p1dMmMJZojQ3+Ehr1Ht6NCYR7cSpEldV7vUyhUzPAFXoOQQFOEKxmsXod4dFDyKONjcCgM2SdJ2LN3IxzTocO2WGNC7SF'
        b'aCpjJuFrB2HUJNzdAnWG1wiBq0WHYPaGYJ+5M5ZfTjChQxsl02UA82CGCKeMKK4+6PyFGGIdraZYH0XAfsBceXmEqb3QBlVY4X+CuOK8yeqzCRcuwj13WmE7luDYTtad'
        b'6fBmyyQs0FWC6aX4StRR5bWG1jF+HTPMlG7DWAzHMCvUb0AtccpOe7d9yZuCYcgj5aae+KIj5K+G9DDa2DwN0ElsKWPfIcLdGoUrUAhdl6BcjQ64x1ANyg9grRPcS6BH'
        b'0pHtpBmbSCR1QZqGCDPsiIF0rFKAyQM4o7+dUGEEZizxoe51bItZdUMSEY1pUEnUmoUVGgSodtpeJ87CqBedZasW5vmtjyBMy8DhI9BOIJ/130GC6b5fEnZIDAh5W67Y'
        b'YUkASbBqI+i5TvRQYE6n0WpvSUyO3Y8kyem/5/JeLN0Zhd2pR9WTaY0ZkEao3Aqjuw13hgTCKPGbSVVdLMcZzFDFHAdosvQhlICWG7SGXCzeCeOku/ZBcTK2KqzbSnB+'
        b'gO0OfrvgITYoOxjTnrOIQ94jsV1/HEYdw0/RWY7CnXg/OtFaEojN8CAZ869BzQWFUKyyC3M050R6sWsCCZusRJYpTs9U2Tqu9iUOWX8Z8kTX9KGB0JuASOgNTeeiaJXz'
        b'2CzeFuvigLkxalgaelZh/UUcWAvVDLl2ETm3OmjhsFfi64TYRpCeyPhsDKdezOKgCU4IT2wIgHsKWHtKWQjDLKG4iEimBkoSYERAvHbrKkzbTRCuMUjB+wowA+2hjjuh'
        b'7hj06ZAoqFtDjxepY4PCFYMowpo6DSLFGksjfHja3AnqT6ZghQEUuGzYT1JgUpkg8xDzFbygJ4ARS6Dwqj/ThRpjcBAfXDhLzIJx337iAqR/xO6Dep0jJqe0cdAPSgOO'
        b'w50TMKOJ9xxvnyew3NufogMF3m5+0LMNx26vPxZAXKOX6K41HPquEFj6oP78DSFWOVjBtI9FivoxTId6qDkUTHL5Dp1yq74WgTsL28Uwr4Vlp1drriXBl6cLJRfcAn2I'
        b'eOesTh6MJjIu94Vyc8hw092li93R0H+EyC8nCiq2451jQkyT84KZkKNQ6RAJo4c84AHkHLU+duLWWqwl/Ce22EHzZQuukAhoxWF5YBUMc/WIYEYIWsXYYAlzULCG6LRh'
        b'GzxIxYm4Q4S0NSToirDKNg5b7YmnpIWcTIIsx1iigXupUJW6itBqPOQG9oTrs3xKbCFGkWeDhWe19iHhewm2O5JmRBjdYbif1tBIn9qO7E9y1CSheHwtjHoTGk7C2I09'
        b'RPVz2HsMCwhymSTymvdvYBqZFArCDHcwVMRS3cMcN2ilZaZBUyRUBWklX3PHBppljMiqGsoiaTU9pBBkiKAokQBfsCaFtldP8rOPxGa8L7SYYxO263uqeZOc6IrSw5ZQ'
        b'rHSmI+7EB/7QGEBLvH8I7hMd51jDXWSEPodVp2mI7IsR15gEwvQra3D0KjGYEczc6nBOGYfW7XY4ud4lNrGU8euSaCbATtEOFhUIE5wSXsEiUiDsDpjApAUMXVPZYa0g'
        b'JQW2xuEMlh2lncA9ezrfOZp4VEowmmA8yHczZFlhxu5AFi0hxjt0NcVOdYMrzOFgEDbTM/dZMczbGyHN5Awd9pTkADHCKpg23ncY+y6QflaJ06GkXhaRCOtldVCR2FrG'
        b'bTOs0CaszTl6Ae65YNWpIyRWS0KPQO1pY9I42uEBa3RXRLrIPZjVINJuhBZN7HGCot1JWKbuvjH8CvG6dAWij6YU5UswtO3gcTd9OzXCr36oVDdbLyGQNSprW+PYxu2K'
        b'Yge8s4mgmLaNcL5Dax0Bp4jGHPDHjAtQYQ/Elg6RDCTORNoBzlzCBmwiez2LVt+FddtIX2knTX+IzknoZXYG8rfFkJiuh35PzDiHrf4HIc/N1J0glwG5x6LWeTqeZCpM'
        b'3oVb0BlkhHeCIU0nxRCrSV6VnscJKeFO1UnsC8AcMwuoFhGiNbthtj2h1zwx9oHwC2STlBDzzl2jT1AeC8ByG8yG5tgDBP1uS8g6RFjTjqW7/XTD9ll7BkF7AE7F+hNb'
        b'vmejobzNar/uGisj4uljqpirc9xjB0nD+W3QcJpGLVMj1Hp4BfJOnSEamfGHe9uhUzcEh2NownoSmo0XiRI6zoeuIv5TBgPmMKhC8MzD6nDI3QgjF65eXH0YeqPpoQGo'
        b'DSP2UCuOolWleRPCj1lBsR3M7SB5O413b+viQ0E01psQLjRfS3yLabUttmREEFamx3BIOUdImYR9odh9Q5GUngydFAJg+vb1pN+OGVhoY7kmKZJnTyU7QcntjdtSEiEr'
        b'UN/rkuopkuBt7Acy9hLnryI2Qq/ZMaXppqYa9CfR2c5g85nDKiQtJ2BeIwA7sDaKpG2XHKYlYqVPKMylxNBX9UEXSJW5z2kPQNrDA5iLJOwfDdLHTOlG7NhJiNFKtNPn'
        b'E4OlNw2JOTQwZTeCFpBz8eAVfRV6gyW9VxE08t39SM3rTfVOPRuRtFnVA0lbbcOOzcS6u/wPJakTcPOBUW4JTMVcPaQNExoJBJp0KWkUJb4eVkpbcSjIg7SsKm96ZALu'
        b'KmCvWijmnGSNU+nX2VehToOslLvQlIQjlwhXh3apmrgQd6qN1HSIunGI7KbW9clEsY0kjKcwf91OCYGz0oLUzZLVulARY7jxBNFr/3qcdiTOVUjWyRhJ5JkYlq+PZXHb'
        b'sHMLmbe9eDcV6naaEQOcUqD5MrDTyjHUKmmTfxhRejpRREYiUUKdMpTtxqLLVljvto2IYVRHKz6IGOAs9p7D3gtEOu2bCAcb9pPWMmkF2Th1NQbaEsgGzyFbebWFLjHM'
        b'6sPE5UdtttDKSyJY/WUFOew+TeIyh1C1/NBlHD+9BjMlUIGDoTRvI6FbnWDLdbur5+L1vOiIhzcbE700QmlIAjQcSoK8LZgr54/5UVBrS8+OwBhJv2rMPUNiIp8UkwZd'
        b'N3Vodtl+25NQtB/vJ/tFk65Y7X3oxH5mmfVZQ4e91NgfJgmrit1hOCVSN4yYUK0GYfiYGbadvOmI5Q7GhBT3V2/G9F1uUaeZzx3ajOS53KLzpMGOuTrLCYS7oOoGuwzQ'
        b'h93cnSMvOaiW3Tk6x2LNWL+Zvz47S0ypx9VEJBAeoYdzBESe6ZDJZyqV05rK2d0B4WGo1qCvsFOdvxV1h6jzHnPmCwVCl3AsFbDbhq3cWxZEC7WYb0rfOMH0UQEJmqLT'
        b'iU5igcAHWuUIWOVYyEoEHlEl2A/eUt54XgmqbE5pBOqQeCo1J5RoJWhVMr19O951dnCHrKhDekbEcSaxY00yyagWaHLWtD9PfLwEGoKwmPQWImRs3sccL2R/lyaZJx6D'
        b'Xj2m66VCR2ggZqtAizSQqKcc5g9B2tmTWOlB50nfE01mnqCP7dAlIE6bfVqbFLn6XXRsjZbnthL2pa8nmA4b+9G4xQJPmjMzlDjrIMnhcjpvsnMib0KWOcnYUh8o2U4G'
        b'wwhhxTlSYkq3EygHoMyajKXMhEvu8NCVUL6dxEU+IdeIARlOGWSc5Vgb3YRsK1LiWPx+iOTCPRjaRCpxN9QeCD1wTYzFCqEaWON0GXr24ZTUZCNOX8S+c86roEfhZmKo'
        b'u/QSMdJSaFdivgOoMViD6QTYPuJJ6cQkO/3P0VgFBM8qP90oot1pWkLJXtpqp91a5bOq2BQcwFlfdWLMsCRrJo2gMoDETuctoUCMQ37GnpaY6Uu8rcUGh7YT8XRZmQC7'
        b'4NEDJTakFBXTftKkqxMlJJ9K4mkP7TB3/DwpleUEnnaYN4YmBeyPxBInqDyM906TcVVAVsycwirMD9gUbHRsHfYrQmUAVEqJYOaM1BOxJ1gqxU76KUtVoyXn7jvjS7g5'
        b'QFy51ApHjjne1AoLgfGdajChjs1ORGB39uPALmfWjQWykHl4cjUIB8cgfS00XCJ+AFWHnc55nJeePbeaNKMckunTqw9ghXSXFTGMkWti4hMd0G+mB/OJEdi3n4yCEmMd'
        b'rFvNODoJvmyL20St43tJbcxlbikjjzASrDC5C+oTCKmyYfI8ZMeQOG+H3uNEMwOut2HgEtl+TXSsAy4HOTfMrJjETfP5cLKrOqB4/+p1t0xIAR3zYPYElobBA2y1oP/M'
        b'45yhHlSFxpsm6JPm1XcIpy6qYboazgqh6eLt81h6KrGbKVjN58Ie988QM71/yB2nDI9oXMN+Pfm117ElhOgjPYiY9LDXecxz0dWzJxNmHqqlBM0sFV25c5fcThEPKrFa'
        b'S9hTBYNrsHO3vusmWxhNIdMg21ff0yzYXoFoeurkGc5XM+K5keapg/J9BJNZZdrDSAyxp1YSL3MROJEIE0YwCPm2JnT8ndgQQ/8ovrYH6ki+EZ8vYdjaBsPGcN8ilpT+'
        b'poM4EnKe4JzlfmY10zqRGHbHWSHpfrNE1+kGRELDjiTumiQG2GVCLHgU23TOQPdm4q9FUH9E6kb6dlM4aaEZRxibHYb01GhS9NcdIaWhbY0G83C5YVey9jFl6L1ygThy'
        b'Ae8QiA8mIii5vI2WRbINW24RM5g2IFpoJHsXutwvCqIw+2g0cZ2Gi0fDSUKMYkMorbAsgSRyBr1B2jk2BofAYLTXfhxbrQkPt5wjXKjRxQ57cwYRY+xZHYrTkYQ2TN/v'
        b'JRtiVopzF+VsNbF23W4s87xKXK1AB1u1yRQrTyGVKg3m40jtGTsMPVqeOw9bbSU5fA8r/RSxxTGWgF6/c0fiBqNIPS9HbS28p3M78aAaZB0VeRDK9xL+5ULnLeIFLYln'
        b'nCD/PHHaOyYwpRtKlDlLZDGRevYKycwYKBLjMP27n/S96cBrxG8b7G76YoefGTGmOuwzggdHL8LAxm3OxBfK2QHTITwk1lZL/GFAi7Yxh/O3vNxo0Pa9UHZllaMnzT2z'
        b'juDx4BhM2RMTzr4kt/lwAknU5sQ3RFwj6gpPaPTG/EUz9yxNXwjVezYyS9fvlIoQxrUxxwMG5c1g4Ly8HvQgscGxvYQGg9ZncA7yzCOtCUFLOe9J72Yz4mTMV1erZQqZ'
        b'xNgIQ7NgiMwEfHjd08yIzqsPZw/ZQ48B1GoYrCXoF8BYCFFr22FbAfSsIb7Suw1qrTFtE/G7Eej3xebTUG/pR2wn2xkaQvxIKgyeYYpKK7b4SXfIiSNssWoXdiRhrjmM'
        b'bPHBjBgLaI86SpKhnbbcRQpsgwMxHJh2wzxTP5Id9cZEznfNNp2NwI79q85J8aEHYVsVSY/MPbqK0BwVA0PEvZpohiEPBSKC+aueZMCXEsIUQHsybZrk1Vrs3AWViSRR'
        b'qj2iCJ3IhKk2VYuBTGXDgzhgHYk1LnpXYBZ6ErHeGmbspVhNsCvGoTMbYN5HcADvqinivJhWmeW+CqblmIukzRo6w/WcoOrEurXWZH7lsRtZAzbEyWcJJwZZCT5ChLk4'
        b'skL7dVghiqBgRjhhETuJqRaK/O3D41Rh/Dx2Rnl6RIZdJI11RJ2WUEcSt0+Z1f/PD4bqMyargUyNO1gYpRqI/T5QrHMk4EIKNrm4r9+NpRY4vD7CH4usREyDJRaUSdZ0'
        b'M866Jd2k3ecHaZL0asGHGyTboErnFGYF+zpePOruQAReYIeV8QdCcHozy3ijI80nG1H+EvGGfhU/A46/MK5dQYCsCd4Dwzi+2YgItwbbbhC9FcHQTrKD8rUUSED2XvVd'
        b'RZPmh+CcVxydTSGSfjBGLLpECSa0bcyJqTXd0LmtsYMIrJY4zkNTzLkETfuvwIT7wcTjYpaSCd0Jy1Cb7NwJsWg1dmPpEQ0ptOvKR+0gntsIrE9CJ1btFrr4ODNDKhin'
        b'gnFUjUhrnLbfYmqjjiUG59ZLCMfrSIQXkDbfn0wAr9zjo3Qa7u/DOl9C7zpi3DMqzDaHPoPTBHGysKFIDzO9HZj2o0ODDVzaCB2WOHDCGEmlcVlPQMrfDM3mG4lCK22h'
        b'fhVBpz6exE5XKAz7GhCi14lO7VkHbWusIS0IcneRFmxH/HDjaaN1xCnKIjBDCYZDpbdJcmXAmN8+kimjoYyJ5yskeFlBj+p+gnIx1upfIhhNa2Nr+Cq8r7gz2d42bjU0'
        b'7odBt5uEVx0E13asXYMTCS7Yo03KTjFJ0QcRJAuSlY9J6RibaJCyzQcSoN1GshsHDm+F7kPK2JCA/ZphF/ShU0szDspXYYFrOA2UDhWmCpbudKSkaxBYpiSG7leP7D8V'
        b'hfc3s8qSREUNAZtx3oG4VzU0OtvbsahGHtElKeLEu8pgQiUMs/eSeCYkzT8GQ2uVhMQLJi/5E9/roCOZolEztVadJSleCG2KcDcCsqyxx4wEQM6ta1B2wB+Zt7xVAKMX'
        b'bdYRR5mBrMgdRGld+tBiRmReS0QxRNZ1Q4DSmr34YDVU+xxwvepI8rMbunFAQq/cgVFDXWvilG3QaQ+9cgZETA0wv23VGtJmC42x5CaWMNDkXocR8dXtNvTbUlto3XEW'
        b'p0lQYpXWVtut2HQAakJ9CW9ysEpKgmku6TwO7rE9DRnRCcQYK8wF+6AzMEk3KIigHh2BD6AwCIbiSH8uJQ2ukKA1fJD4auZWazIPpzFbetA1zI74QA7mpZgRcEdUhYR5'
        b'vapMN8bMq4TztSHxSakw5Um/aYM6N2Sd6AevOuH9s5xkHMMHtucPQfVO1mYGmx3tcMyFFLhBlZDdpMnV+BFxzCsEkbqWthnLvRK/Jhlh6RfGyCidsJnR0Rw+MCFWXEPI'
        b'OWGNY/qk7fpiuXLkMejbivXHdkGpmOTbPTX2hJ1mJNmNsynhTk6kDGS4nLY2xKzkWNKw57DLno5/BJqVcHafQjQJnT4htnjjzLZUSCMLsHK7g4aKN1aFcBG2Aebwv50C'
        b'FTDDPFttMH2KNkhU0sncRqTqdkCnkx7W3ji149wu2lol9tpi+m2ywcYNSDbm+EPzaVK1xs3kI2It9WHISZnIvp8eLLQkwGZFEwnMaeC9C5BJ+sAQiZai3ViyToH22KFk'
        b'hvdvRpACmBWUBHftSCgXwT0xjugrYf0ZfQd9wpf+nXKa63Hq8GkoUT+iSFxzBtMcSZnpYzxtL94XkPiuxGIL9VAvyDzvuvNAQpQyzmmeTd5BDH5qox+2H7riBcVXsdzS'
        b'm4xrpoeOWkfcJATJ3QFDWgddiYhbVsOMMkz43og2xu5txLYmsR4yL+JMkjJmnfAmwsgky6SbmE4pWS2bCNzVG7BRVVkcthrzz0VFXrhkhXWu6sITevTeAJTKQ5nWaiK4'
        b'cpiMUnU22YUTG5gTlAR3GsyuhUkWxesyWE9WX0HQYTvS3pv2EDRa4P56sxgoddtCZFFExk98ItTuoVPIcsZxWxXS3x+QXtBwInk1tqrekqMdlDlAnY7STaK4MvpXKcyb'
        b'xATcgKZNZFNmaB/whHF9aNDcb6d6He+4YKbBJQXs8oGyCGiCPkKjolN+zHGKXYnM8UUn/4B47xBJiQxsN8ecW5c2kZgmHegMPdvoQZu5cxYnks1JMYMOopdyktQ5Kn5B'
        b'ieeIIpuBSRPSR9v30d7mU6FiA5aFkso9Hkf4MnBdn9CqLxWzb0Mu8XHSPO74QnW4euKvmH9qhrhS5iIZHGEequKzJIWJg0UdNjylsRVLiATObk2hrxvWhAcr6WP7mgNb'
        b'6Xzn8X449Cs4BdAkE6QhdYj24cQ6mMeu/VEqtKNMvJcALA6cfs4WyiRQpU+sfPY61rpCq5g+dsJMKMma7lvEGYuJmiroLEqVN2CbC3HSPgJ9AZbdZJVvbHUxdx88MMPW'
        b're6YH80CXs7MZRXiRcDJ3E48JVdVgr2hawnxx24YEo1P7/aMJXxr17GktZVZ6GHVlo1GWL/9BCkMRBzHCBnmdCNwXBXrbDZhhxpZjpn+kHEMp49An1IS8ZZy0n4qiTW3'
        b'sSz3GXloNHCCahWyDzosNKDFfjfUWpGukKnvswq7t+yRl8eck8cwVwXvHPMiq/iBOSlY2dY4rHEVx3epulpCqxWW2x88QkAZhToJkX078fqs5ABDTXbFa5o4wTSkGxKq'
        b'DwhJLbt9bTdhW/kpyFThkGL6ErHv+cvbiR80YHYsQa2T8YFxC1I9ysMioO0AoTPzxJdj3moc3UdGTWk45MhDa4QhdEtg8NBBnGD2OaadJPY15nadpPlDK3lSq9ugYCdm'
        b'mBJgBvWgNRWqtQgrczazgLLcTfl94T40coWtOlaR4iB/nWlAGTp7Y8jWI3X+DrGIUujUwdrjq5NYeoU3KxoOMxevbYNeM5h1gDYjOVbPpgDqfaHnMtk7A9Bmdon0HxLa'
        b'+w7G7oEZlx1x2LoNalyg08TiBI7KkUSpdt5ENm0jjuxmZbEYhdR6ax+3Iv26zxznT28lzlZ9KhnvBqhfSvVZ60e4k4Npe91ompotdhuPpApIwcy5jD3YjN1GIu6+Er1S'
        b'jMWPiuoQrlUJjYmPcveppFo4zArBCYSxMHmSXTTL1TbiS+cQohVpuDLf0gElGBRgVagLV+LKFvpjXFlJCaEFcdVSAcNWnOQ9XC3EcDrZzSqJQHgsEWbpLXjgy/mqwm9h'
        b'Je8uI/puFiBzWLAGDWyqC0Q01a6sCK7lHm3mSut351Z3lpVTwHw3est6K94RYLGuOt/reJ6+mZA52QLMmZNtwIUGYy/dhKr1mG9E73iSmTIiwFaT3fxLRSrEovLdOR9b'
        b'A0wKsDRZgS+HV64H47xjTgo1zC9XZmIk5K6QBWL7bVcXGsxko6EAc1TwLu+vK0zwX/DJEXLVCrBeKdVI6MD1B+JL/vqKuNRMC/nfXDHX9xUYiblfj3uJZb+evvm9A6v5'
        b'qkJvqsievbYmMl/ZUeBhJPKgobj7cJFFrypI4vuIY/XeikktP+u5zl43M/z6BaE4Rv8nL+pbvPmnd1OydctKWm0N11u7lGze9r/ekl1+rtf3e/5V+Pc3G9YPuv3wWMiN'
        b'uS8b/vZqg9E/7f4e/7ZfgnRC+Os3vjr5p3cDw1Zddv1Z+PhaoWf8a5pjiZdO/PRvR40yrzpsGvl95CcPxh96nlU9fuXX1XEDDx3UfpPa8Hle7vaff/bfaz/+8MefGDu2'
        b'bGv7RVj47/ITdd6zStJ53+qmTumsf5X79358rnDqnaQtr/qYv6L3ttagwzuS+367XjGulJT5nDtxQ/lj3ddD3v74loJl/6/7f/32p8erEte9e8r5FaVK84T4ux6zbafK'
        b'PKKEf7pXfe53o1Irn/yyUr/f2f+ppTnhj065znNHkgUZP1WUb/T+udQ9/KyNffKWUyVnInecL7v7w5cNPjf9QZXBDyKtizZ94PSb6J/s88e3Et942e/1LRmWH4xuq/2w'
        b'YW+U3xu/Sfsgzjo98APnD+3K+v/sPG12KPZqmOu5kCJrR4tX7p+cN+n9R/f+tTrFLUcG730U87p/8fHf7ov7UM/u+rove6tsvv9BsVFC8v98+FZCoIGOQSjseyfn4njL'
        b'51+6vPyjS/2DARd/YlM3Z9rldTw35Ae5b+rp3F3728++/q1Uu7xms81vRgNvz5spWXztZff1lNu+9nerUl/t2l245o9Wyb8X/s+Xr/3401+YZO/Ot26K0fs0NO217oIf'
        b'iBpXHfzc973UnP/d/uG2l+qnc7a9sf7WeMH/a+7ag6I48vC8dtgFFlZ8cUJ4nGdkWRDI+jjjAzEqLvsghvgIiY7Lsgujy+4yOwtI8HkCAVzAeEYjSgTRswQFkZeP0tid'
        b'O5PyD+uqrNPMH96Zq+SSnHWVxJyn5ipc98yiSbx/7uqquNraj5menp6e7p7p32/p7/tNFtY/fL966dzz17rXHXvvwS3X9+dOmb74U03bnQ3vONZdY++7P1+Yc+Viy3n2'
        b'y8qTFVH8Ky0zz3Y86hE/Ss79qGji6/HO63GfbrDHLbj924QH5Ttgva7Zt2fi4U8i/3LhclWmt3Pk9trEf/xN+8Y38yq8azor2dG/3ug/1WJ9UFFypjv7s+Gk9nkPM9of'
        b'8pfcX/W2P9xyadNXXPbXUx/OOXrm1YHHU298Y+usHNaHy+o/WHEuBT2/+B1SCjsI2Jzrkle62msSniHPoSd6N6NOhL2KbsipNZE/YbopNLeCbAZZ+3stCt/rlANciRC0'
        b'Gi2a3JuihUAkmpCHaSK+GnZmMmp4sFLJ1pQLdjzJVgmHKsu1LBG7BP/zisbqPC6ZX4fe/0Mb/RWR5YIrAIejsYpJtFobDvuiK1SEPopBFu0hi5iKcnrLzDjfj3NtTI2u'
        b'AMGx0q0MC86rlyn6NPXISrkS8aQsdRF6b/+GyoBdJSIOOYScxt0JfhBUl6MK+tEk16CUOHHbj0qEgyzyv0aSlMo2bo1+KtKyN/aJTstTkZbsgmejyRnHd5HpuIM+Xn6r'
        b'/r+AEgmc49xeezHHycuvbyKgDBQ1m0zC2iGjLBVJqimGVpMszVIsFUXHqGJidBpdgi4shp0UzkycRMWaqJ/PJontlJEifynHEWJovBQ3AacZYsllM3AaxS0MxRiiHC/K'
        b'W9TasZRYdtpruhxUNk3p0vBZ05eN5Z1OpVJ69DVQemIn0y2nsVSanII+KO04XmHNPhpbCq7WqclY8odfZpR5JGx8stKZFr7AN/905fcL4z8wxm1AkkpjyCuvcRMZ8CDA'
        b'b0/frX8THiuJkK0fZBAiDwMZdvORN9KQbwENoCWMiPoZ/Rz8tZM3H5ut8k8mCeLK5qNzgiYbXKJb3r3oRrl7ZnmMWp2cpdEdi22+Sp0d/vDEAoN5woR7rdu+nHL3hDjt'
        b'WOElrvrvF+N+39qV8bgrWHo68erXL965HTx+bsbJjwvrC1468F1dwtRDQ9/uv3E5/HZB8oHP/rB3b+PHqzUL1s/79MPMP3/Qd42Ghw3WtQ9WX+3K+/676/v2T/OV9vfe'
        b'b6Vzuqsnf76odfrqc7pv85pudlT8M2vqwHP32+d6B3TXTweDZQvMoyv+WCt0njjcZvtF5c1ZJeu3/26Rri4252hdbZbbkllLTzWuZe/ZExNq4pPeT14afzd25lu+RuMH'
        b'K33NEW98Eq73tN6dUjmSGz3/cdWSnTEtVcCYGnmnt23EdJkeuvUgovY+N+fN1y8k3dAnynOQF9nW4OQmbK3m58vc2zAiAvRT8ORroE3hY7SD4URzfjo8i7Pkp1Nwp5GY'
        b'AC/RoCPaJoZ6IrhS6QhQj1kme6z4Jx7UEzF0AnzneZnsPVufZgYtoN9kTbWGESxDqUGTVj6yDRnMPbApg82ZQpAFBHJJhkG/wrM+CAZBmwE2p2Dy8B4SXlxPaGZR4FA+'
        b'bFdY2odBY5wyOapgF+whGBsJ+mYmy/PN3IWxZlMa6JlhSldyEFGwkbaBITCghKQ9sAlVFlO048CQQj8H9atkBpoLImdJKddqgkG9iZmwjIiB+2jkkNRvlTkuk2fYzXlp'
        b'tjlGsgb2EmHwbYrF6/GUenegRhs0v2BE58p6XipYm0NEJ9MLMtfI1LRXN9TgoyarcrD9JVS1M3QWu1ohO/eCE9mwCQfMa6GrbQSzigQXkT+0T77wvO24t4LWNAIciSGY'
        b'LBI13iDoFkOux244ZEiHQQtpBx0EU0aCkcTFSi+dhu/qDFjOzoKumgwaTFZ07wwRt5UBu+D+UOxW/KPpaeQ7HzHjymHp4D0kEaGnkJe9K0URuOsBIzQYzPL/IEO4iQJ9'
        b'eq0sEJYN3wLvRcD+aDjoBw1w2AcHypFVojVpCSJ+OhMG+jTypSzg8ivIAb0sk5IMuDACjbxDFGr6HlinMPh2OWwhSTrkj+8KydKBFo+I5a6LYCdoN4PTKah/G9GgkyUY'
        b'800gmGFL17Nwj0DkLg+rWbU9FJt4AF6MgH1wAJlhcK8JvE3AExQjjyKjCo7Ac4l49Fst+SpCVUPCrhmhULVe0LQYL7BOx1LecBgMj3GMpgUYULe0UGmT5nhwATV7Iw6w'
        b'YaHAES+heZ5Cj8TZQvkKufB4GRyEbYa89DRr+iySiJxMh1fBQ/IDRhvAeTPqGPMsdDZ6hvRsHnKlJhpp2F6RoYynUwWgPR917Mq0VMz7xF0CWyl4ZhsYlKXhCvOQf5en'
        b'Qu73WYI0E/BglXcsoFHK+L/c/0dTxJRxsEqeBhKuQKCOCg9xMbGQmi60pUieRcoyaaGtUWYHllOjRnHYYDXpof9zJtnYh8lUOFWyyZAq0W6nR/CjSU1SiQGf2ykxbt4v'
        b'Skwx70Do9Tk9Eu0XBUlVtEV0+iWmyOt1SzTvESWVC5lX6I9g95Q4JRXv8QVEiXaUChLtFYol1sW7RSfaKbP7JLqa90kqu9/B8xJd6qxCWVDx4byf9/hFu8fhlFhfoMjN'
        b'O6TI5Qqt0WrfjE6O9AlOUeRdW7iqMrektngdm1fwqJKaIuNcpwdrUkla3u/lRL7MiQoq80nMipeXrZC0Prvgd3LoECZ6SxPKvMXz5ymBPbhivoQXpTC7w+H0iX5JK98Y'
        b'J3qRtegpkeh1VosU4S/lXSLnFASvIGkDHkepnfc4izlnlUPScJzfiZqK46Qoj5fzFrkCfocck0nSjO2g2wl4sCjVU2NMae8UoRKbazUYtmDYiWE3hu0yvQ1DNYZSDCUY'
        b'dmAok8myGLwYNmHAvELBjYHHEMDwJgY7BsxmFXwYtmGoxVCHQcSA+cSCB8NWDFUYKjBsxrBL1rfDUCRfCLPsfoW36jGUP2EP4oGkGTOsCh89a1jJOR6rXWi8OB2lsyQd'
        b'x4W2Q7b542mh/SSf3bEZ65Jhcis+5iy26dUyB1AK4zi7281xysCVWYIaPGJZJaqqcA+nNIzZwT8JzCypF6LeD7idi3FkOD8OhMoQDKum/vtHaNJqSiZR/wvjqP8N'
    ))))
