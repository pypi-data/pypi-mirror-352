
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
        b'eJzMvQlAk0feP/48ubghkHBfQUEIJOH0QjwQUG6Uw1shkCCxyJEQD0TrTRDUgCgRscajioqKWpVar8603bbb7RI33eZl1137trs99ijd2t1ut9v+Z+ZJkMvW9u3u/4dx'
        b'8mRmnpnvMzPfmc/3mHnep4b9sa3fn+9GQQeloJZRq6lltILeSS1jKdlGDjXOn4J1mqao87Ttt9pZwWZRSu5pdH1+KNc6SuO8nIXieQrOyPzbaRRrpxxVCk0puAWUw2ox'
        b'76s1jgVpC5JFa6sV2kqlqLpcVFehFC3YWFdRXSWap6qqU5ZViGrkZc/IVytljo6FFSqNLa9CWa6qUmpE5dqqsjpVdZVGJK9SiMoq5RoNiq2rFq2vVj8jWq+qqxDhKmSO'
        b'ZeHDHiwC/XfCrcFHVDVSjXQjq5HdyGnkNvIa7RrtGx0aHRudGp0bXRpdG90a+Y3ujR6NgkZho2ejV6N3o0+jb6Nfo39jQGNgY1BjcKOoMaRxQuPExtDGsMZJjeEdlM5b'
        b'F6Dz1YXoQnXBOg+dn85eZ6cT6Vx0HJ2bzlEn0DnrHHSeOn8dpWPr+LogXZhukk6o4+pcdYE6H52Xzkk3QcfTsXS0bqIuXOdeHoH6yX5zBItqCh3Z9pvFDhSLaogYGYti'
        b'xCNjaGpLxBZxATXxiWnrqQ3spdR62qFCzMotGz4K4tB/AW4snnXoFFBi19xKe/TLfhabaohzQFclEu9JVZQ2FF3CNrC94lkubIZNedkLoQ7uzRPDvRlFC6Q8KjyNA+/C'
        b'mwvFbG0AygpehD3hWRmSDClsgi05XMoV7qkSsHPBRXhL64UyuIPWTe7wAs7CpTgcGhyDHWCHNgRXsw22gN1R5MacDLhXnMEBL4F9lAc8wAY3s6BRzCJ1wGsqcDkrLh5l'
        b'yYL78jK44EYc5RbCngEP+2n9cYaXnOBLOENGDkmXbUJkXGTHwhMcVIQfyuEZotLgRHgGHkS1wRaacsxggV6qWCtCyW6TfZzgFTd4TZNLgSZ4owa+UAua3VwoKmAixy62'
        b'UkxrfXATAYNbVCxszs6ELWyKDe/Q4AjsAtdQMh6PcJdDdBa4EJEBb8KTUrgnCz1eUx6mCOyNzpWKedT8NLuGwlCU3Rdl3wIPwwvwKiLHDxqy87gUt4GGpxJgq7U2cKQM'
        b'nIrKlErAS/ByjlRGU86ebEf1PJSMW2US0MEXo9IlkfA5BWzKxo/kBPUseBGcdiujh/V+vK33B1BwMK4RjQA0aDlosPLQoLZHA5lCQ9oJDWkXNHzd0HB2R0NegIazJxrI'
        b'3mg4+yIG8EcMEYgGejBigxA0uCci1sCDPlwXoRPrInVROolOqpPponUxulhdnC5el1AeTwY9mkKanEYNehYZ9PSYQc8aM7DpLSzroB83bWjQrx496APGGfQLmEG/NMyO'
        b'cqYofkz5dFGtgyvFcEIRm8JzaIyXT/wrMg4TubrAnuKjuJh120q3sZOZSOk8LoW+RTHlv8uJkudSZ6lKRxRdnOnLeSSDaGS/F/431vXYifXT6UrMWe1Oh93WsUvcqDkl'
        b'cb9V12ZrKRLNWfq3sheDIoJZCx7S3/ioGjqoAUorwx1/cw48tQS2IP5rjl4YEQH3RKej4QTOFkZk5sD9ElmGNDOHpqrcHGbCU17aueiWyug4TZ16Xa1WA2/AXvgCvAKv'
        b'w8vwWgQa8Ffd7J0dXR1cnMB+oAMtcTEJcVNiJ8eDG6CXQ4E7yx3gBW94UZuBiikAW2FPVnZmbkZOdGoW3I9YvwXuQWzTBPciWiIkkTKxNApcAt2gJx8VcAV2wFbEUXp4'
        b'CB6A7YspyjvGxSMYXBwxAHGreuOeaMADkIVnazQEaTTsuOVsMkTQ2tPEGTVE2A7jdDqKYY8ZBqwtbOsQGTdtaIiUjx4inHGGCCdXjftY9crBw5RmIbrylKiOvJl0NGRX'
        b'Lc2e0v9GX0vrtpx8+eSJLcXNBUoXyJpX+b8/37ph8vbG0gHWJJC4xjfxsHdMmda/wAXGGR3Ov3dacVlfqo5hr06kjlV71PmVirmPMPuDfeAYasBm1L778XTCmR4vpMHl'
        b'guBHhPnPgKvRUTLUAU0SmpoP9vHAPpZ0fg1JhMfRLb1R0oh0KYsCx0p4oJMlDYAtTKIO3gHGKCncmx3LpZY585bRaJppX/QIz8a8jQDNgJmwOR1cQK25mZ4He0CjmDPA'
        b'ihCr0UCnHgca3DqirVu3fuWZVK6urldWicqZBV2mUdbIZw2wtSpFPQ5YOPdKFHy5lRqcx6KEXh1T26YaElpnts/UpVoEnszPY4mdiYeTupJMggizIOJdgey+QGYSxJgF'
        b'MTiTd0diW6JB1S00CWRm/Il7VzDtvmCaSZBoFiT2Oyd+jntMbYcCMW/AoUq+VqlBwEI5wJGrV2sG7IqL1dqq4uIBp+LiskqlvEpbg2IePwzu4ZISEXoetTuO9EABIT4V'
        b'p9Zi4r/E5KexaDpwkPqu4KGrt07V9EzLM1udBllcWmhx8tBNbZreMv0hx21r1racnTlbcyz2bhZ7gc7py0E0rfNHxm7NY/59jsfZIQcJ1eOayJ5XxhpvYG7BHMO2cgyH'
        b'8AyvnDPEM9z/OM+MmVYdx+EZj1ytJ/pVAQ7DRk02F43Bs9DgicdwZ4YWt7S3n18WiqfF8JiGgo1w51RyAzgzZTO8ilY+mgt3gucocC0NbNUKUUoV7FwBm3FKGuiBJyl4'
        b'MDiXJMAu2JvqhHAG7Z6CoAJaGrcuYBLuZoETUThhYUUZBY9AHbjBVNIITsPGKBmPopeDO3AHBc/YLSe32K9Atx/APF7vALZROYj8S1o8OnJp0AEPoAeUpC+mJEsQMnEg'
        b'jwHPyKfOYOGFHrRFoHACi2RngaObNuHo5x23oCAlk9QLm1ciHPUSKgV2xMF2FDrCHpKyqQJcgiThhhNsQSHCCy8w9/S4oEn6JQT14VHYgao4Oh12E1o9J8HnIEm4jYh+'
        b'Hn0Vrib4CgGwXeAWeMkNJRnnTEIBbIfthC4ve9AHTyLCnLLXU04+oIXEKgtBbwEqKBxNGig4u1iLuxN0KRDsQtwVg5pOT8X4gG1aPGfDC2o0SR2AHSgJkdYILlLF6xB+'
        b'w6AK3AFHEX65qoFX14EWsI2mWLCbDpWAm2QKHbMGkGEThEc0Gs2rqQZqJQIHDXQTax11iddAt7JaHJBUsZPwOMPo7AGWLGaALmN4GEtAiIMJA3/lmFSp0tSVVa+tmVUf'
        b'rKwqq1Yoi/G8JEuqrC6TV2pmyR5nWILvDmImqH6f6czHUNvt3r2mO7g72OCOw+5gNSZQ5frbEo6mB135O5QfeTPu6PED1wxnD0w2hOyK3SXeNX1X2K7Ju6S7Zu6auCt+'
        b'1zOuq6ULtqB1oddZtxhuXNlzVJL2Wp/5dE10GedceWp37nsfK6RlEW2sT0peObfDrrvRAX1W/pJ31m83N9vyyHjz9V0hixJ53RcPXT7k0CGd3DI5+6Prj16vuyItee2T'
        b'Sb/LXeQ89TNpycunr++Yfst5b+yuu7tOHniH+4uVH4Ukr/iSF19Tjp4rIvoPJVfQmoIHw8zU+VEyMdwjQWMYHuKBHlZ8MDA+IiD6CrgL7iI4CXUZ2blcygktNY4seBTs'
        b'hs89wr25CVwDB2CzBKFsBPPBKbCXt4o1EfSC5x6JcGfvrQ8kgAQBkSNahKBhE+jJ5FKCBDZsWwmPM6vWHdrftqLBHcF4UUNLmmeu2G7U4jJeoLEj/YuXHKaPB5yG9Wv9'
        b'8B9kxfma6dDBBWjF8UQzs4uvxdtHb28JDOkW9hbeEz6+CAge5LK8QwYpFOjmD/Iod48Ouza7Vod2B12yxc13kGK7SC1Cz475bfMNKa3Z7dl62uLlZ5DrVXqVxcf3mEOn'
        b'gzG0m23ykZh9JPrkQTbl7c+kosKCwo6t7Fx5uLirGBMhJkGrg56jL8NFZrRlGBTGFJMwwiyM0NOoYL7/u/yw+/wwY3m33MSPMfNjEBF8QtHQ4EQfYzIKTD7TzSjkJ5r5'
        b'iSiXQIiX0tbp7dP7nQPIcGX4xG6A1gw4VlUXa5D4XKHUqPFgUHs/oY2ZddC6EGJ5b0TbYhyoWUfZFsQ8tCD643Xve4KfdFXscJBSF1xnsJ9iUcRAkjtiUfzPA8kxi+J4'
        b'QNKBkTVedPKgQkt+g+bCkqRfikSMBPFSSDqlr3sOd8WanyeFU/NIrHkSnxKlvsyhakqc/8pSMVkv1DpRQuH/cCl+ifODHDlFJn14C7S6xcegatG6qQMHqFLQDs+qlL84'
        b'xtHUoXTTKwY8dW1rOn7gxQO1vhPZcI1o91bha5UxK9/aX3RIfISb6h37fIxdfF2crOQe7xD92faVa6Zdar584Gx6QPch9yMDuZMK/fccn3Sm91TMC3EZE8yxp2NO9U5o'
        b'LqRrpa+7SSY7V1xU/LycZXrZuUtKHZzrd+asTswiU9CUWaAjqMKKTQkwBefBbTIFrQen3aNkGUhi3bpWLEOCDGyiKB8RZxVoocXcJ88LXIoBotZZwb2sQln2THGZWqlQ'
        b'1VWrixEKHRtFZogm6wxRx6L4Ap1GH9+0oWWDIWRPg67BoDFojPGHN3Rt6J7Qudmw2eIdoNdaPDw7xG3i1qj2KF2Kxc0Ls3KgQXNsS+eW7tWm4Cnm4CkkisnMF+iT9XP1'
        b'c9vtDBMNpYZaQ2lXuIkfgtk0tF8QalxoEoSbBeHdCfcF0f3O0SPYlV2mUgzYlVVrq+rUG38At0owt4592uUjeVaDeNYPc+X3BD8Vz6qxZm785b7eyqtE5/BY4KPH4dOf'
        b'XicwRuDjjsOnqQyf/mORx9wrrHTc4Ekna2OtLOlo5579Gj2HQiyZ3eQ+myokECotGR7EWpVYCl6Ez8duYDj1F/Ycr9tYWzCnpPK3xeUUgYy1XuBqPAer4BbBm3EIW21n'
        b'JoAF7IrjNL4qcY6bGkERjIdQ4R3YFc/CKhskiBviwe0pJLfPBBeeOzuGohaUSO65PksRIjYWwO549BwJFLjpm8CDx0msfTpsjEc9MZkCJ30nh8L9pICNSzw92lkLMGkr'
        b'WmLTGdIQMV2p8ahJpqC1f88UaBCTvNO1AesaWTW4shXi9amUFo/ERWGwOR7hr6mUN3hxasakSgbgiVJfZ23FjRNwwtWeyRkBbwJDPBq40yi2x7QtaSTngolhoku0Htc/'
        b'9yC3gCKQEwHaS4HgKq6SQhjz7PTplSTz0dXiuF9RRjzyS51qpjPFct19wFXUjolUAexNzKtlemehNPt9qheTOjdeiXIiEEwt9w7CoutcCjQXzK3yIlWlgq3gjAY1bAoC'
        b'sRtS4F54mpQKb9onYtEwFeFcXmp5NmkX8BySkU9qUCOmUeByadrMPNKyzpvAETwVzaPA9cp5K+ExEguOBKZiYDqfioY358NrXiQ2oDAd8246Gh/AmL4JnCBUFIBuVDN+'
        b'4AxqJjyWIQLdTEfcqkYQGtGcSYFdazPh7XoSvQneiYZXEdFZ1KbNWUhOb2VGCYL3SDq4isjOpvigO5sLT5HWcHa1W7GJjWCYqCR7c7CCGVPwFDi9Fl5FD5NDwZPwWg58'
        b'SUFyh3g4RaZiNTpaV/7XLsDaJfvjkHR2FT1lLgVPL8nNB+0ks2jLJK+1LAMueu5dRykzfqoQ/m+CV9HD51Flnnkr4BWSdzcrcsIiqhsXzLqeHsYUHIXw5IvwKmqTBRR8'
        b'IXgBPLCRZP4y2SeijirBfb1Cy8m10twDu8ARrN1fSMEXwZmFi+FlkjvTz0FymS3CubMHJysYPgDHwB5XJ9R6+UgokufnSEnWRgc315loDFIxJdkK0TMMxfVIHrrphFq0'
        b'gJonLIAvwWZmFPRMcXFCzVlIgd3uhaoEZhRG+CedoCvwYzSIC55hxtYcSu2EmrKIWg8PFNW7MAv8pGDFcvYGXFNSg6cjU5MS7AB7nVA7LqLgvoRFeeA4yVtTNkH2CAnx'
        b'6AlKl6b6Mm0jgMYQJ9SKiymwDRoXI+x8hmR+JctLomUtwY2+Yl1DJlNwFAU7nVAzLqHAbckScBduJXkvZ8gW1VJ9mAjWIM+T4ZmZ2RrQjL6XUuD5tKUhSpLz/fKEuBB2'
        b'P2bF/Okrwpmp64OauDle9OuYrvy4VVusICU8NnI5+x5mb5Y2YAElZjG9cwNcAWdBM2rxZYgVFi+D3ZOZgbmzFvSBZtS8y6mFcMdyJDV2V3757bffdgVyErhsMjE6TypY'
        b'x5T+jylT18lYFvx06hnoKVXtH3ZyNQtR6/bl8Xa1ZeSBBfyfrf7dM07d3X0n+7b3RT+8U/a/UwdTT9z4Nrnsf+mMmFMz67s/m9fi7bbiIeio+2pB82uvdNwq/jzx8z+9'
        b'EL/5nepTr+//MvdA07Irv3FqOLPjmYzklW2fbjUeK/xbVLb2q2cmK2/cyXNzXPTw1//89rerPzxUAs/GTvholc6x7COPdSlOm/jefz+RZ9m/s4baAUKcnebHRAbEV93v'
        b'e/+1ozFVb/YdeO2o44qz8Wv/7Fv2S79Nrio573Mg8drZvMRDVpbWt2fye4lTdh4pkbtufM/r+q4ZFs+/yos3bE15z33fM78t6XooXP3puZeDQj6pbXlz3Zf/Pn1m19vP'
        b'fdN1j7vyw4vC1jNJf4k8dX5f9sQ/XKl+94vif9d9ccnhObt5k2V5Dzt6fn5RsfParE8/XFn14cZD1S8t8um4EbXzzNvPvjer9bQ6oefI8bZXC0+JFh2fv/KUo51m/4MG'
        b'6vaS1ccbMpBwGIxaXA2OwGtIwMsFesQHTdkIgNFIDDzPQovYdrj/ERH3b86EBht4g9dhJwZwfM9HWHgGN4qTsuDeKLg3R5qJrTkesK8A9LLRjHEGHmF0mu3a9Uj+a8nK'
        b'wOpFXiDYPo3lC3fDk0wB5+oVGnAhPVcagW0+cD+bcof6yeAqG/SyasX2TyEjMrCITEki0WNcNOBqhUTasmIsyNSP+k3QYDeLQYPp7OFoMHbPZh2D/h4KvPRqA61Xt0/t'
        b'mN022yQINQtCMd4LsHj76+tGgEMEl3xdMQJcOMjGVz7+BuuVaKLRehUR1W29ionvtV5Nm9GXz1wlp94rZa4yc15XM1cFi/qXLGMuVxT3y8vI5UNSCxdfkVrIFamFXJFa'
        b'yBWphVyRWsgVqQVfDVL4J6mKJDBVkUumKpIJScZCVJkdc+0bYBi6Dgk15tuuI6Xdpbbr+Cm9att10ux7tO06lZ5Pvz70K5vOo/sXDBVWSC+mcfXWnyvpEhqTQH7aYxLy'
        b'Bx2Ya79AQ6nteuIko9p2LYnuZTHXFBORmHRvwrAIHOgyBp0pTy9d2iDL2SXwQXBEt6C7oLu0u6DHxxQcZw6OG6R47rEkaJ2PoHydxdvHENuqRTd7xj70CTT6vxsSdz8k'
        b'rjfBFDLNHDKtL84UMtPkM9PANXBx6wQZfbsTTgWbfGJwjCUgxDj3cKbewSIIMmw0C8TdBb0ePYvvCxL6BQkWf5Fh8iCbEk7+8g+CACJDPA7I4NNrB9noGuH3hwJvfYKG'
        b'6OSmJotS/ahX/BxTI9ivhNMotOm/2WhkP1lsIMruYVLDFLz2jWIJBc5Yg5dgovZm07Q7lgmeHPykAv5BhyjqvOt09vcKDdhMSQ0TGtj/caFhjPV8POHejhEaqrY4139J'
        b'EWDunOSy1io0dKxynPUFTaCV5Ist6QyokYCj8Fg8Hx7FUjuW2FmgVfXG5pO0BgtvD15YiI1Mxw9sZJSJBjlWJ76V7Xy05ehbP/fZdqIlxkTE91fagdA5Aeshjx/M8Ljo'
        b'FIEm8xZJPveVa85zrhrW+PS/VfoGI5f7UgnvuzfY7xHTjFnoaB64FiUFneDYY9G8GujEnHGnWJvxh5le/Zixo6lTa8vqtEjuLFYry5VqZVWZsv470si0u5Ript25HEro'
        b'g408rUntSbpUi5sHmoMTmja2bBw2B1v4aP7R5+vz2+0NCUaW0d3I6ppm4k98CqGaN8DRoJqfniuSMFd8B/XbR3BIMoemPTAjPDn4ycRpBFu/X5zmjBKn/3/gDPY4nMHL'
        b'JXYD0IMFFifQnKPGRoseChyG5yGDgvXzJ1MV2H6u+nZJCmcDNU/lezmF1mDFY96/cxg+qKXZqVdsavWWOdoWi/n5GBl7z6XdP/f8LD62Lk57oul0jPLqVuXhfMMO362R'
        b'Pv1FHKIQF/zZLb72HTGL4Jli2Am3P1ZGieFdlhR0THzkTziypYioo4gu6pmpNm0U7JOK2aMHD37UIXbwGaWAecwMT0whrJBjZYUFo1hB4I0BhzGBsYySRaE7pTull3M2'
        b'oyejj3UutzuX4Q6BtF8g7VaYBPFmQXy/c/zI4V/2g4Y/dht4Mr1NIwZ/3n978D+N3pero//Let+nciCwyy0ko7xutiv2QfHZmqWsfL0gipF6kpM4jOuIvNp5WepsJvLz'
        b'CSxSUolrgyQwPZRSec2q4WhUKGbdvxyIHvcA1uSePRDbTPMOxcbF9JTv/GyNb6LvMz5v+jQXJvp630trfTlOtMrlw+djlDs+nvBc7h+Ff4yU8XbLykXN3Mg3DT/7/Rv2'
        b'L7SG7fL91Z13nosU/bX0z7WfKpzLH75FUR/mCa/Nfx2xC7Y/qqGBDZ5HMkF2jgTRlEWDK7lCgt2XF4Yg0QHui87LWQhPwr25GaCHQ3nnc6bARrDvB2hvXaqUG+qKFVpl'
        b'sUJep6wf+ZNwyVorl6zg8FyiLP6Sfn9Jd2HPUpP/VLP/VL094hbDhn5BOPp0p17KO5dnksw0S2beo+9LkvslyRaRuDv5uIs+w+ItMsa2bdZvtvggiOVvUBlU3fThyq5K'
        b'k3eknjPoggofdEV8qMsaoZnlYDoGHCqVcgUiaeMPMaVg5eGoB9pPjVDMLud8r3fBT+piwChmbZ6j+I9nG7E7MTNxGM9JxE4sHY+YUux09uU8wlLscfwLOA7jMAmK4Yxh'
        b'G/YWjpWlxk0bYqmdo1nKYRyW4jJoqzQ1nsKwdRddkv+h9yaGeeQbGI66kVfi/M+ZyyhV3q13aQ1WexjAv468OQWtJWuHDLTXnCc7O/k0LfiZ5Y1liiVgj/5TRY58xWuc'
        b'QsgRNNFX1hxec3jG9DWGc1u/lu3z2y0pN1S6aKYsWe9e7DLxmzOClPDFjr+KM94+/966xdvWit9LtVCFry6Flje2rXFa0h4xdUflx4qfvcAt4rzzaNkhv0MlvLfrqG2z'
        b'J2jbX0MSOFkU28BL4DliRbWjWKErwAm6iA1uEbvJPLAXdGVlSJzA8zZHyVpwgCxU8FayVxZskswAO9G9e/Noyh62sNAP40ZyK9yVhK2uuug0cBetc5wcGtydxmNqfA4e'
        b'rofNOaAH9VMROA920vP58KTY6Wll7dGDHmvlbKL3EE87r1YOY+kRvxjJ28rRNRxK4N8haZO0ytpluhSLwKtjWtu01sT2RF3qQzfPQYrjEv3AO9BQbiw1eYvN3uJWjp7W'
        b'x1oCwhDn5mDRyqt9mqG2baZ+psU/2Cg2YlaXnJKY/GX61D94+z3kB+pdDApjhokvM/NlzM+yYxWdFYfXdK3pnt49vbfw7Oye2aagRBN/hpk/4zMHro/rIwoFunQkLAoD'
        b'dHnDJgMHPBmgGSATPyOvTFtXXf7k9ZVpHuJIa50UrLNCPp4VRrTJYZxzGzMp4GapRrNCGOb7pw5+Ulms0yGG6nWdNVIWG7KUkEWXOySLYZdRqpz7X0SdYxZdr3FmiGBm'
        b'hvi93c9lv2NFsJHkJfYrL2NmiN/OCom4Qm3Feswk8eY6JrJ6oYNMTYtwb1XGLkpiIsPKHUVKNhHcsrctnspEvponWKVmM4aho8+WMJEvTgncEE0zRpLXZ05gIj8JSuA/'
        b'yyKqVfXMtT5M5GahXeo9RitfuWDTDCbyqlocOZ82EhPHmvwiJvLWrNnlH1JfYh1uXNVqFyYy3WPmgmZqEFeU37dwMhP5YWxi7gz6I0xn3MmKSCayXuzrt5VVgstsMLKs'
        b'OVdyJQFSq4WEl7aeiYRu/A211BzcIJK/ZllJ+mBGcuj7NGr8mhKPzzemM5HBcznZahbR3Ga7zl5iJanMxUtkFXrNSdZWuinwX2ZmEXV5gKTcWrtr5JRsKZvoeOOEcaVM'
        b'5L55C31eYM/BFTnaudUykXtyFfXRtJ5GFZXP2RDARGqnlfuJKAONbp9k1HgwkXtTvBcsYBOteNLv1tgzkc1hbutKWUTbL/lTvRVrrY6pL5XSH9GIpCkfxlqJn90Q5/Up'
        b'o+mOa4ysYiIdMyfWfMuo5Sf8LamSUl28k8HRrED8UCkMPlgwowrGOD8v/fmz4Qv/cf6rrIG3p6dVt0bxX+cbU3a78jZT2uib5W+2PT9fcjYi+f3MiMgU/hdB/0xvHWz8'
        b'Zqfwz+bOFFbNB5uXffqa34yNO1aqwn8t+WVMz8t+2V8JS6jshe6P/KiiXwaUb5+RtSlp/Q3w3uSfhS7hle3MWvriJ5rrwkWnXmn0+LBgRsJJZ//P/nj1i9WafZN2Hb36'
        b'xdntye/vjLuc/tKmfV/Pe7vmbGv+mZmeazvu3hP/oVD3b7bUN+ro3DTPt68frpOv7lt9tNth0ha7Vx8UfChz+eKZD2cKi8rejv96ZXzoW84//1NG37vvPOefk/HJ39Z8'
        b'frnzZ9W9uoc3Xv7z+rvxG/44682k1PPLjI7lU/ucy59tiVRl78h06uJ+JhvYf8Z+1v3/eavxjye+SOqUZ/0laO6f7v1rw4vHB24aHuwZsHz9zfkvrp0oP7bz67O3F+Vt'
        b'nfmruwdfzfvmb96mil8vWHuHPjhwYMKkHWI2QZbwJl1sg5aPcaU/PMyZQsGzjO7i2pbYLElEOvb/PwVa0PoHzrM2hq8iS1weBQxR6O5IGhu4OjlaGjYVgwNijx+5xD3N'
        b'KogtMaLhf8MWQ3c81ZfKq54prqiuVOEFpH5sFFkW/8eqkK7hUkJvfby+Djv26FIHeRRfqN/c7xaKPhbvUGOh2Tuynx+JtbOeBnarE3EX0ssNIa1Kg7xVZUw2eYaZ+GHd'
        b'7t0Lz3r2epz162OZItAKhz2G+O76hQb31iLDwtalxliTMNTED8XRQr26FTs/uQv08lYvVJSfQc04L6A78lvtDLFG1uGpxoXdE44vNvlLet17Sy97m/ymm/jTR9ylm2tx'
        b'99ArDIXGhYeXmrwmdbubvCK75SbPaJN7NJNYaohrXW10b11pcp+AYjxw1eHows1dP3fPet16i2+gQYhW7WSjunvu8fUm32izb7Sep+c9fJxg8o00+0bqeVg97Knn6AsN'
        b'sQa5iS8y80UWvpfB1+BrjD0c0BWAmgH9HhslHH0PExGHH3qCmT9hTARubG9SSNzhwK5AE3+SrdAn/7YVUYsa0swPIf01Pq2j74k1lDL3fAdhY0r9DuLj/QiimTYmK+o7'
        b'D4ENgRmT73uE9XuEWYSeBgeDgzHksHOXMxoienqQTQmEo7M9dBbuz9uTZ0g2OQeZnYP6nYNwTM6enKa8ljxd3sMJkbocQ6jJOdgi8B+Bo+wHOBuVcvV3Q6fHlp2S4eyk'
        b'xtrRcRjoIs6NtWEEQS3lfq9+4j+gqSDC1XBkYtuC9zkGvIyaTom36FHLECxyoBT2xIGbVc5WsHY6LMMb8TgK9k5q5Oa6ZVwSzxkTzyPx3DHxdiSeNybeXslBYh27nKWw'
        b'22k/EmItc9BRG+hljgUUglcOA3bJCoVaqdHklvGGPQ3uC4Kz9lE2vYttkx0Cg3jfEIuIjGQvUbk9gYSIxibHUZDQjkBC3hhIaDcG9vG22Fkh4bhpP0wPw81lvDkuVYEb'
        b'BfjieZcQKmQ9uMLs7xBsW8DSdGBK9GXafbGuIMY5be3ijKN/XaGLqqEOOSaeAB8F3LOb03P4ygdtfek1cadecDxU+nHYtx9+G373oaN7wlt22zgXTHp348MO9/ZPT1XN'
        b'2mfo/fih/77TS/6+6/pfdd+qOYJrf7169Mr9Oz8fVP1u8ibnTV9M/PrWuk+uhh3q7FzxuXd07ztp91d99OfzwPeLgxZdFPdkZ2Td9pjbdCU3zHXCK2JH4pVrD1qA3rr2'
        b'MeseaIR7NoK9VWRlnK6C54a2kDiBfYzD7TIpSVRIwVHsDnwGthKXYOIPDK8UEVNt3XJULtmsRgqGL7Fgmwg0SRwYudHoGRUlk8LnYBujOj3FinkGiaPYjgy2ga3loBns'
        b'h/uzpPAYPAb2g/12lJMXCzaCm/OJqx8wgL75oDkPrctwb5QYnONQbnnwuAO7bgOfVA93zkF5cAZ70CEBZzkUz57luwpeI1Xkgt4ZoDkaibQyeIadQTb1UR7weTbcBrfD'
        b'HUQqBp1FApRHJs4EW2U5Urz7rZkFb8CL8OD/WbzdunW4eGtXXFylXF9cXO9m5ROZNYKs4q9RzCq+wY7yD9TbWQS+aJZxj7II/Tty23KNU0zCSLMwsl8YiabFQYrlHmuo'
        b'I18W/6Bj0zqnGZcYV/V69Bb2LuvL7w+dY/JPNvsn61NttyecSTyReDzpVJJJGGMWxvQLYyyCYFxBrC3H45QH3gGGxcYyk3ckAgzvesfd947rje+zM3nPMXvP0XMsonA9'
        b'p93FEhiCvhwtIWL05WoJDkNfztjC7TRsynYaYJdVatR4N9oAp0xVt3HAvqYae9MrlAM8TZ1aqawbcNZWPTabPFlNhpu0hPwNU5U9g4IxzYkdujWdFCMXM6Kx1o6m59B4'
        b'2v6/hT/VnE8E/GMOk6lrrsnskRIzbZuDPMgc1ECtGUoi0yyde5YesC+2+nyK6QGORllZjt3MKBGzpcE+qVK+tlQhn1XPt7WMLcaFti6OW6nu1J6crRTpqx9Q/2pUP6qT'
        b'W4w7U0yrsZfwsLrVWtwhY6p1RTk+t1Yr7PH70dU6FNtGz1NX7Tas6sKeVT+86p1M1XbFzHB96or5w5o6oSdpvIqHlpsNFLOhkTHHoZX2/zFjHDtX9eIcDlczCUWlTfrz'
        b'kTcTiE/48QM/2zTclrDdd1o8Vf0bzqsgT0yT+d8lAG4ns7N1as7PYPnClyaIWcMYG89+Q1p9lWaYDbXe09aoI6LJdIkXJszZFfaUT4C+zpDalWnyDjd7h/fzw4dNQFzS'
        b'W+PNKsSgMGwnH1akPaFCD9yVeKohc4nc/r+BCsmYbXeIpM65TmMjEIL/0HRqj+Y4+VplcfGAY3ExcwICunYuLq7VyiuZFDIponlWXV2jVNdtJJOvGhtD1FU4qLY97IAL'
        b'3uIo12jKlJWVxcViDmIvJmL4jsfHZvw5Q7PuKtxUNrD3D5z+urVxbP8GHak5dCptiZsyyHZzCRikvj+YQHkH6yv6g6ejj8kr0eyVqJuPljr9tP6AePQxCRLMggRdqgXl'
        b'2tAvmoE+Ju8ks3eSLt3iGahf0h80FX1MntPMntN08x66eA6y2C4ReEfO6OAzNuXq1bLkielk9JCd8zQfdGqyM8SZUhmPclzDAl2wEzZuchrBL07W78+3o3F50P0xVFfQ'
        b'GJq3s9vd2vnov0u7m4pVzkJX1n89rNOIxc4PQWUC7SdhYI8gsW0jPR8BYs5Oh1Gwm4PP3sAQXsHrsTuN6j0/ZOgk8J6rsEdpDmPS7EiaI0pzGpNmT9KcUZrLmDQHkuaK'
        b'0tzGpDmSND5Kcx+T5kTSPFCaYEyaM0kTojTPMWkuqA0c0TTotdN+mSvThgokgPR4jxRNSEs5IzHIZ4xg4kZK991JKd0Ufqh8NKudH7JfLeNb+8Wtx39kzYpwVCbeBsRW'
        b'BIxpdXdSZiCiOGgMxR4kLRilicakCWy1tdu125ez2zk9ISPpUUQg8YdlPUQB97urzq3cQTFxDAVCUksoqiVsTC2eCjZarSrEYiSGlRF08FW443DdkjWWORplRAo2+quQ'
        b'WDzAwTPIeBNGbpkd9fjPlbIuEV0oOGg/8tgUtIY5oFWMjR6EHjoLAjcqpeOh4exK1ja7ceQ7e4dxJDYUYz9m/bLbYm9d28ZNGy7fvfdP1EIjHhb/ZVSp6lTySlU9PiGm'
        b'QimSW5tGhZCovKoMHzEz+pbEGrlavlaEmylRlKZCd6nJrRlzk3NF1WqRXBQnrdPWVCpRISShvFq9VlRdPqYg/Kdk7o/AN0tEczNSxLiIiOSUlLyi3MLi3KKcuWn5KCE5'
        b'N6s4JS81TSwbt5hCVE2lvK4OFbVeVVkpKlWKyqqr1qFZX6nAJ99gMsqq1WiWrqmuUqiqVo9bCnkCubaueq28TlUmr6zcKBMlVzHRKo2IeHag8tDziNahNlMg4DeWHGvz'
        b'4PGTSOjCV7ZzfGzNW1FdqUDD60k3WyEtc7/1B2qjgjxpfOyUKaLk7AXpyaI48ahSx30mpiZRRHUNPhJIXjlOA9oqRY9jrRFdjU/x05RjA6ZMWbZfP748Bm0ypTHXP6Ks'
        b'EQvVkB5mGLBzziUH9QTDF8F1bBOWyJCkDQ7BlqzFUJdFDuIJBic44FahJ7FwnI7dTxk8ZrGomBLX2QVplBZ72SwFN7TENrwA6rAaIBo2oau8AlICPAgu5hSlY3ftnJyM'
        b'HJoCe+AJB3g9Ht4gJQ5OsaOWSAKxHUby/CxUohRPN7F12P07Ct/flL0w/bH4j7fCw5ticJYqSLaDHaAVXCPFXLFnUysqnCm8EYqeMo2xx7gHc6l+LwE2O0k8KoKZsu02'
        b'wOPDC4c6fAwPIjY6Px3uyeZRz4Dd8+HzPHh5Auglu+nFoBE2auARdS0+kmA/egKwS65qTY+hNT5oLVrr9MHeNmLb2a16428pGV11r/ONH7UJPnC8Pfdd1tKdzg765I8r'
        b'oh98dPujT95ojl765i7PAr7env/n/R/keUx49lwxf6v4k1m0z0ffHFt08s6Fu0lsw875DeGnouYede8wb5a+++aC5vt39n51r+x+c8tHRd1T+/vuaAqXyDd63BbdNXz9'
        b'98CDb6xb9ftfqB/k5a0fVPzDoJ3gNf/Fvz3oKj+88cGilZ7n8t77xm/Pnz94/+aFEzdVt6oCP3CblL/zUv6OB78ezH6Hd9Huk7xXJ+S88fnA4rfePnxG+sWRn/3rD4n/'
        b'YPUleQnenVP4VUXOqZkZJ3Z9ei9N5nvBp6jl1zmxAtO8/vK9/5JsiD651v3yhb4LZzKct/i1b4KRt3/7MfvNXwV/5bBYsOePYg+iwkkEp8FuJ/8Y1NziHK00Eu6JZlGe'
        b'oJFjX8djFDB7weEJsFni5pE7cjfB4pWP8PFOYF8AuJsly8yRZIC9cD/uLRdoZFN+4AVOFbgEWomS6ll4CDYzHnpgp5BxS4W94BDZdL4GXpyf5bAB7kvPgfvAPqYQNuUJ'
        b'd7JhXz48weiamsC1zVE+nCFXviFHvrP2j2JQhsngRXgUDR10fxTEBzIxpUVnoYfahwYTisd7EeaDy3ZgfzJoIYq3atDFz8oD3fCUFB/ihAeY00IW3LfAlXn4i57gFGi2'
        b'UrSJpriwk4Y3wW3YQgSo2onoR7PEk7mTDY/QYF8e3MXce3YeGv/oXsKo4HYAuvkmiwYG0MVYxG6lAb1NeQYuwa1WBZoDu44F9zzCwhx8ERo3gObiNSiHmBygxTQyw/pR'
        b'4CoX7lpQSxp4FehAs0SzcjUqL5tGpByjgb4QHmRI2Qeug0OIlgvgUp4sB1N6nQZHwEl4gaTPAK0BmNIcNLPU+5AzvFxXsxPhXdhGWiknBxxFlCKsrQA6ArddU9jz4A1w'
        b'jTl0YCs8kYPvl6DmBt2JudJ0DuUKutmpE/hit5/SIod3Zw2p7YYr75DgpUKoobgYSfrMBCyzxRB59C2akUdXOVA+E/WbjAkm7wizd4SeY/HGG9vdJz/wCzWuMvklmP0S'
        b'+oUJFoGXzVJnULfN0s/6g19of9hck1+K2S+lX5hiEeCtte4zyf7iqYcbuhq6a+8Hx/QHxzzAGWeY/JLMfkn9wiSLl5+ebREE6hMNCmNRd4Ix2ySINQtiBymuu/iht78h'
        b'uX19x7NtzzLkIAHHU2wJDn03OAaV1ivslb/g3RfaV3sr3BQ81xw818AxcB6GRhx2QBdliPKO+rb61ob2BvwYAe96h9/3Du/mdJeZvOPM3nGYwCRCTqLJb4bZb0a/cAZ6'
        b'LlSHu8ziF3hM3Ck+HNUVpU/Rp1g8fTuK24qNhSbPSLNnJL5T1q01R88nVxa/4GPSTmk3x+QnNftJUXarbjEgGH052H5Z9Y6TIvUcM3+iJUBEEq1folCSKAo32lmE/hZh'
        b'sD7LyDEJw8zCMOaHvUkoNgvFzA+eSRhuFoZ/5sAN8XhEoQDfPOhMhWAtpose/RumQ3BndAgtONiLg/Ek6u83So0eanhYlQzTaA4zVp2kiEZp1DgLxmqIC9SQXhMPt032'
        b'ND0bKx5+8uAnVXWedkiibrkmO/4QVWcFo+rkFmPM/WS1m7WRbGq3JY/1fYbCrmVWtdtXYYVDWB2jKIRrbTAqQq2UK6TVVZUbxTJUHVtRXfYDtYPoLk5xqarsqWlcPoLG'
        b'pTYaQzGNSBj4ThJ/TANiLP7UxK1COdRncDohKuq7wfyPpQ0rdNVqzF1PS5d8RKOttDWabLiw8GNJDBhD4hp6GLFEBcxCS4CcUXkR3n9qwhW01XrBEG4OjN46vG2/S+z4'
        b'vxJeQQhX91HWqeqpaV49muZ4G83RTyPe/JR0V/8QuteMpjvWRrf0+wWpHzeSGYsMofWpyVyLeewaZeOxmEKiOEBkDTeFiayjTVRJzrd9Inn/j1gRvjoxRvxMwaoDjUg1'
        b'ajrTKJVrycm8pUpGozDmRnxar1WNUqCqWo3aJk2rrhYtkG9cq6yq04iSUVuMlXYjUIOhZkM3rpsii5PFiL9bHh7vEA9ubqGYJrvpY2ZURhGYuSCKM4cG58CtdFX2PQtL'
        b'MwMl5t76ANtAjpOdFH7mGb5eMXEl9Jyi7PTKcp8Zu2pdfhUnqp4cb542d0rQUu+uwLfu/Q+L6lrqZH8rVswhlmm4PQXcsSJaeAy2Rj+GtAg27380AeVZCbaDU1mjhZZ5'
        b'iYzYgqD/KYKdYTNC/Bdsp8mCk07MgbJq0PwIbxjkLQQtKxOyiPzAWkVHw+3g+hPtL3bY7oFPyXKzDVlrBMG4eP8nsbk4UUKf9pn9gghLqPjd0IT7oQm9hS8svcd5xf71'
        b'uv7QBFNooTm0UJ/anoMgZPvmfn7oj7LIYKPCGEJqRthiVjr9Vzx0tjPMjcHfU2wpwt7NNGLA//JRUl81jhnvBco6RsGpraxTrZXXWVdyrcaqzyNnbtep5VUa+bCzs0s3'
        b'jikIl5FIFMeJJTkoDyoKfclXK9Ul36N1Gs+caN2HcV2yjwqYXIu9bXNfW5hOaafi0XwRSe13GHVS3eJxFErjKZNyfFQ/gx/TGnwI58rpHzDH7Z1deKDpuCA9ukxRssTl'
        b'FX7/qxyhMtU7R/5WOW1K+zqsJtYY0XlukvFO7h837JTtLuG97UXp97rW/2P3V+1iFiN2Hqxa62TVW8wFxmGqi2Uxj/BJzct9crF7yV7EnwefJD4j8f6l79gcO8zhU6Os'
        b'K7Z1FMFs9b62wT8mifBjhpUfGzA/9gsmWvwnGWYY60z+ErO/RJ9q8fbTawwJrRvbNxrj2rbotzwIiugXzzMFzTcHze/3mW+TpPrJZ/juJYZF9z6BT5+wbeltzK5Pprie'
        b'HrGFqRZxrg/m0u8J/nNnSz0VeHYd+RBPvcLvxmgVSz4YiJgDY0bAkKflRhmap7HKUo0ZY8T2q6G1azv12KeugyLbKrApyba14r+2+eq9bHocO8vQ/FOtVq1WVcnr0FOq'
        b'FE/CX1XK9dbFO1YWO442+8kqfAWjJycNaNuDiiqSifKVtVqV2tq+CnRVVidSKEtVdZpxzQZ49kMUaKrX2mQKFUJe8kpNNSmAKZrponKlWvNko4K2jKEoZW4GwnSqWi0u'
        b'D+HlCIzfRGobVaiujDo5RnTfPYmO55don6tNpPBZTw1ZuUNnfOdKF6bLMnNgkwQ2RedDXfbCdHa+GJzNEK0qVau3qFY5UHNXu00BHWvtPbRYp6ksxncOU7U/vhsfpnWQ'
        b'X1OEUMpBuhZes1+cDJqZo3CPOPDhVWc0/R7wo2A3PunqpFSbgmfMS3Cnq8ZVuygd+9oVQZ1kEdTB/QiinC1Ml+A6WjKy4R4azdunwE54RLwBHAqFpwtZaK4FN5wXwLtR'
        b'2mhcwx7QBY5aCdsNzzHE1QwVvGCxdJEdteBZHjgFb4JLKs6HUjbxwvz98eAjbyYe/cUUNP+bbhwIQ/hsz5dZhvcCdgtfU7Y4O5/3lX896bXc09xs5yX3yFZXbWxsbB3r'
        b'F7xO56lrfRf8fk3f70qPe+SGbjIkHj5n2bqmf21ZVQur82VHwdJ7u3/xV2F54eZXv44ov1rSmdkebNi2hTqXFu//zoOeo28teeDyaGPSjJbfv+H8Qe29L2I48TWnaert'
        b'reFFomSxA1GDTkTPfA2tbfhkG6wDdaqSwdMseAReyyaqbvTAVyc7RcK9USUuZDmx6cuDwVUOvLRmC+NUeYHNsWq6d02yno14HV4gYFABb8JLWcPcJZ35M+ezPcGtUkYl'
        b'rIeXZ5ElDXQuHKmNDwV65uieHVNlw15N4MRDWHILuMqoedui4T681z1xzUgV+drFTHorbLS6YzIq4nrYRgM9bIXdBIvWrl6MEq364RXhqGSO+Pv2/G4dtUI+nkrwiY0j'
        b'1psRSWSFNFlXyBJnvDViNoajDWhZ8VxCPwiK7I9aZApabA5a3O+zeIS+0rpZuKA39AWJyX+22R9rxDyzaLJ+ptwrM4kzTEGZ5qDMfp9MrMidbfEP7pr+rn/0ff/oXo7J'
        b'f7LZfzK+YwFzR64pKM8clNfvkzeqFrFhVvdEk7/M7C/D2dOZ7HPuxZuGr9JWJSjzpUf/hrvEMyv10CLx5OWaeMSPWK8fjlmvR7RfE16vG6ih3YV5zjSNj5x5quAn9YI6'
        b'7BBNXXKd+SPcJDnFaG146jX7OJbK8YYAZqmOJdqZx6vJd6kNfpRuTkwI1D693vDUSAJnjLvCpBSljDaRj0OqmD3AWatWlg/wNKrVVUrFgANaG7VqNRKv55UNfwWQs+0x'
        b'2ih83I7N14NgDfshRyVa50LO5WTpXMudCfLgIOQxypdjM9dhHCyBYrhj0AVnC9eKPMZNG+Hhcfg7kQfzWiFGZCGL+HBVxJP9PHDbMEu47d6hIy2ebLInLcncRW5BvYDj'
        b'5FidIxOlyKuwxkNuTStdg8DIuCgEe5MgYFCQN21KTCzxI8E+HgqsvVJVrX5i9UMdmCiaVylfLVpfobR6qaAHxs/8OIftoZ5UfVV13TjVqJXoQao0iaLk0bJgifVxvgfG'
        b'DB0aMAzGOOaSF484wmPw4kggA3XWdRLso4rSUWy+FZzQcR7gADgAr2bBq5lUGDzlCjvDM7T4HB7YFj9zHipIJo3MRCvg4zKK0ofKTs8sirAeX44kSPh8oDPsBgbYR2TS'
        b'LNf0RUaWiEZzpeNnqnhKO5nCNtzmBeM4OLisQxKpNDOnYLhA2lzgAO+iRb6H0JORCg/CZpKHmI0zMAKKwphouHNDuiQzW5YhjeQhZAUQlWLnWnCpUJuACphdBXtH4DP8'
        b'LFgWjkBLLBI0JWJ4BGyVZnKpenjGAewFLaBRzGZO9N8Pt4Edi2eS+tkUZxYNzs96hjg2VqWtiCL3g1bvrBy8beMwa9MScJV5FVMvaITPRWXmWBuRXpdPCcLZ8IgWGFT9'
        b'dmwW2TT1p9sRu1q3bZiJN7zsOjptds6eV8Cvy2qpQ7rjD/jhJfEzSuUftT/f8UrKbxJCug9JXv31v55b+wftBvaLQYf6Aj/t8+KnCqkDSz5pLLmw4tqD6598tr9RMjNU'
        b'P+nAerbrmvIHu4tmf+7yqyX32YuWrDx8/vUC/40filea1L9v++U7ebPPK4/Pag2eXDhBnavfUP5qxd8PvvNSDpId4NW/3Jk4+eUtMetF61X3Z/x7wPe3XzgFx0zhrZ+J'
        b'8BdzROb+aVkEm7BKF8ILdGzCzEfY/wUcmgyuE9w1GnXBDnACIS94s5Y5QmEb2Fc7DMCBo6lOVQjAgZ1a5uD6AyWwOSsjJ3JZIILQLMoeNLPAtpgcRp1wIAt2eC1xGusJ'
        b'Eb2CHJsiBHcRUm7yG/aSK9f55GiGpRFAh2gD+pw8srGVV8ma4BJNNIlrS+Aesu81jxyqnyOh4VE+JYhmI0S9CxgeBeKaD4NbIpv9PaMWHLQZ4MFJsE/s/H+ymOMFYqy5'
        b'3AnjCessUy8YDjKskQSeSa1G81IXrFCcho3B+fQDv0n94QtMfgvNfgv7hQstAu/2JJySQxtTT2WbQ6cyP0i2LJNfttkvu1+YPcag/mC0Qd3bMOOxduS+QNIvkJA8801+'
        b'6Wa/9H5hOmNGLzeWmQSRZgGxUsdbAiMNK7unmALjzIFx+nm2LBUmQbRZEM1s0QmceGx55/LDK7tW4gy+htRjmZ2Zh7O7su8LIvoFEaSWOSa/ZLNfcr8wmbFRB4gsQaHv'
        b'BsnuB8lMQTHmoBhLSOSgHUfsMUih4DOKEyJ4hANimHakfALaG0YqadwY6PcxDj7BwZ+oH2OGfuz2MNIQbQWJX2IgMl7/ncHw0EhZjdGoD7NcaDoKg7+fKPjJICTWwhx3'
        b'mErdcE3m/hAMad1zYm974qeGaa+PtO6EYDyAVkuCDobgxHBzjpiDvfvPsnJRffPEXuod+F58sI56F8XsG1NUlxUXE7cANX5tI/FFGGCXqsqe6JAwYGczVmI1OlHODbiM'
        b'0GURAWCY6PAlucv2sO7/mR3v7qNmi2FDbQ9FdhUwjemLh1cRm0wPQ5sKOCwX/iCFA3vK1VO32BBv5BrLukO7Nf3B8f1+CX3xr7ORiNXN7k0ZZNOu0z+jUPAIBw/jp1oS'
        b'Zw2yE1zCBqkfFXzGtZU1yMFxlTQlDNBPs/DxhhOLcMYglyWc+RmFgkc4INvvBf76CAt/Uj9/kkWYiDIIklAGQdIjHOhSUIbhJSTjElJoXEQK/YiEpBC8K8LCxxv3LcJU'
        b'/P6ReTgPCh+RkLyHhCknup8f/eRyfET6DRZ+fD8/3iJMQ3l85uM8KHxEQl06yuMVpF9i4cf282MtwhSUxysN50HhIxLq5o2iZx6mJ53Qk07oScf02NvjNntSILR1HccQ'
        b'1e8yyeQyyewyaZDl4ILY/gkB3rERPpRLSAWGGdIt/Jh+9IlLYSgNJJQGEkpRqMuxDRGBceKwWjxdRIPUdwWPq8IxkhFdOB93YQauB4WPSEh6cXiehThPAclTQPIU4DxW'
        b'WiYaNd0Jvfb9k6bfK+x3yTS5ZJpdMgdZQS6hg9SPDzDJWfRQSbNG9NBU3EPTcQdNx/0zXTcf/2O2uBBMcikdvqjJzmU0RjTlWM8C3c4Iq3aAI2Pe14X/Ps/F21w8Rm5z'
        b'UbCWcRTsZVwVtYyn4CyzQ//tFdxlDgreMkeFHd4G0s5tt2/nt9Pl7HZ+j/2oTRcxSH500vHL2QqHMVse8DYRF+uWFedRWx5cSZoLSnMdk+ZG0txQGn9MGr/dVelu3XFu'
        b'R/YouOncy+0V7qO3kYyixaPdlTwJv8dj1EYULPnistzLuQrB95QiQHQJd46OFeK3Z5azFJ477Zd5oragyeYXL4X3TmqZt8IHhT54O8syX2s+P5Tqp/BHMf6KABQG4I0p'
        b'ywJ1PHRnEEoL0lHoKhhdBStEKEVEfoeg3yGKCej3BGs5E1HMRLylZFmoNSYMxYRZryeh60nW63B0HW69jkDXEaREMboSk6tIdBVJrqLQVZTOAV1J0JVEZ4+upOhKqogl'
        b'O/3xyQXROx2WyRQc4l0TN8BLXkt2rJwbIUDihZNJYDatMG/xRbIxfn/garUcC8WMRFu2cWjnw6j9BSO3wKhRAWuVdaoyEd4cJ2dsnmWMYI4isKyNymQMBZUbRdVVjPQ8'
        b'nnQrZg3witfJK7XKAYdiGxUD7LSi/Nyvkirq6moSo6PXr18vU5aVypRadXWNHH1Fa+rkdZpo/Lt8g1pZ/vhKqpCrKjfKNqytxMcyp2QvGGCnF80bYGek5g+wMxcsHWBn'
        b'5S8eYBfNXzLvLGuAy1Rsb6t3hHFoyNEfnzx0kI2ADUtjNxzcMDbphlFvY1bQz5BSNMIGlnE4THrCQNZ41HEfpylYDax6JNePfe9zE7eBHhm7mVawG+h1CLc00AqOgkuo'
        b'oY3Dn+FxuexRVPJ8H9MzIqUeTVH1XHx0Iq6hCtWqsGOusQvMaBoaqOIhNRd63mFP8qTnRXcM7dVT2DNHXrxXPJ7yafT2IusYfry7aPQNT1LpkF5mFEpypgwS8x12J2Y4'
        b'JJINPAV50oS42KnDWUShlIkyyrF+R6SpUZapylVKhWRcLZCqDuuMEOC3bSQiNdsUiww7yuvq1KpS7RP0SIk4ObFEoSyXI9w5xCIlovUVqrIKXLqKaSfEaNZ6EPOMfbaP'
        b'8bj4ylNVRXyFHj9NeJgm/CtaNkDHfIyn9o+/RX9fsWUxMbliuwH+6Gqxa4u8sqZCPuC4CD9JmlpdrR7gamoqVXVqHurFAa62Bk0Bajsan4LLCFfuGMnj3b+jYSweCKJh'
        b'unTisOvG9POQv+7vMIZ9mWJEXCECYMQP3BI80RycoE9nBNYN+OWmxuT7grB+QVj3knelM+9LZ5qks83S2SiCSI5JfRtMw4VUH38D25B22LHLUc9FhRjC9En6JIvQ11Bg'
        b'TO5mo39pl7LOZfWxTZIksySpL98smWOKSDZHJJtCk02Bc03Cufo0fdpDdENRa64+zRIUZlhtVB6u6qpCsqaTJUR8JuhEkCkk1hwSi0920KN/P27PPGnWJ0lNtsayCU1f'
        b'jHDvXD7CXj587JMRuLFGKSpBI6sMSTOVslTmu6REpj77w+i0+u7Z/QA6vxxBp+08ga/8iX/x+Bw3giCWjaC5Ywh6mkl3zRCKcRqSUdlknA7YyzXFZAfigL1yQ011lbLq'
        b'iYcVjH6of+GR6sc8lKJrzbtBsfeDYk1B8Wb8SeoPtJ1e8FUZ8QbWri1VqnFHWHtAVFMpL8MuivI6UaVSrqkTxYlloiKNkswVpVpVZZ1UVYV6TI1qVZSUYFaXK9ZoUUac'
        b'YWQpI5traC0j58zaD710nBp66bij9cggehxXh5/e0RG7Ovx1vDm/qAaLzcx8r9xQViGvWq0UqUlUqRx7eFQz/owol1xUo65ep8K+iqUbceSYwrC3Y40SwZIU1Ilq1DRz'
        b'5VXPEO8ETV01EurJ7Fz1VDOxdRa2kVRMSCrBvaMlMy8zz+MFYcgrAfUO3gY6jhMYyonQU0X1Y4gkEWlUaEmzFoNvw46rwzeTPukZrQUllmuryhJLrOhtHG+y77RDlFZX'
        b'45c0i8qHGzy0pCsUo7ph3DVqvVKNppd1CHrJS7EH7hNMH9/rN+qaS9wWYA+4AzujpOkZEqxIzlqMLQNwXzq6zCuKyJRkSHnUWg97j1p4Fx6B57VifM8NeAacAc2wF15b'
        b'GJEplYVqsMtEVC64Bk/kSyGSXRLmc1eXFTPvym0HJ9I0spxMeHA9Dx7386DcQAdb5gpPEHcOsBvcAiMMBhG50sgsab4UXMZl45KzuEgmsgcvgWOwTYvB1PIC2K0hr9LJ'
        b'4cLDcBvFBftp2LtQqCVv29kOrsJzBfBIONgL24vgXniwCJsM8mj4QrnPPGJq4IPtakQUODMvk0uxgYEGW6eD21qsMV/PCdGky/zDiS0hC1zkUO6IYNAD9KHkgH+v2bBL'
        b'g5uGCy6AfRR3Mw0vJMG2QlXHaleuxhmxWvqKjXsXXs6FMcKGX14+Oi3Df9E33CmzqFdabi6ZG7k8OfuXTqWXzZ6X74iztni8NKE2ULIw69Cff/Xgn7/75/l/8u7KI6TN'
        b'E1nZ037v/vWhy688+suqtz5cAYuaZu+eKZ3qLXi9lJUcw/tQVTuf/9DlwqraOffOfbTggiH9y8Rba9/2iVvdYPy0T7bRfZn2aF1i3mu/4B5wnN37z2Mfagy/WXnk7X9V'
        b'mRZfX/c3364JH9z5oOxIQ+eMDTf3xy8/0DYjMLGS9etJle/k53ge07Z7fdyV8cXPP250A+ty8/tb7zT1/e9fwup3vs9uink/ZuLdLZNOvMTd+9cQbbB65cGGz7/5pq5/'
        b'ek6neUZQYfaGTX+b8ffQ4JcbvqE+8Mp48dnfiN2JmWEyfA52kBckBc+CzXYUR0qDC7B7IbOP8Ry4BG5HSeEe2BSdDvcqQA+bcp7H5i0CN4mZwcUPXAfN0dIQO7iHpjjR'
        b'NLg6u4CklKXB7qjMnCngxWyUEEKDo3CPE/EKCbCDp7BdI8cObINbKR6HZY8G7F7mWM0bi7VZmBrQB89moRu9aXACXq4kLi3LnEKHG1bg1aXDPVrs4F1Cc2DUs1HwFnxB'
        b'Jo60DkTKDV5hb4S7QQehDF6cAQ1ZGRJwJNRmGgnNJ6aRcHBTS0oX8tBdnFwa9E6Gu5mdoz1LJmOrR4ZEBpqipengDrhNTCsiEQdeB9eKHoXhXB0rwc4sxKiCECurgr3R'
        b'DK9GwltcuB0eg88RM0o4PA53ZTEvpsLcBa+AHTTlpGDBI/yFxMCUvNoPzQGoCClNsdbRyWusu1NzHNhZkojJsOPx+WsbwXlw5tFEQmYl7MzKyVLD5qwcGWySZIG9eYTO'
        b'SLCPCy4Vg32MZ84LAsSCzbmIUY4pJTyKk0qD2zkrxfyfXEuLA9vcN9Ku48lMrsUj15P6ACugGDeVmHoOWk09hXzK3bvDqc2pP2CyiT/FzJ/Sz59i8QrsqG6rNpadqjB5'
        b'RZu9ot/1SrjvlWDymmL2mqJnW/heHc5tzv2Bcb0pJv40M39aP3+axctXX2aY2FrRXoFyePt1bGjbYHQyeUvM3pKhXZfJjJlotslvjtlvTr9wjiUg9N0A6f0Aabeid2rP'
        b'2r5lpoB0c0D6uwE59wNyTAF55oA8vYNlYviZ6SemH59xaoaejY/b9PE3+0QitO0bpOdZ/AL02HxzLLszu9vLFBBjDojBL3+SkkCfivC9McscHIMQvv8Ew1RjQrfdqZkm'
        b'/1izfyx2yQ3o2Ni20ejDHK7WrbjvHdfvHWcJCTPwsDtumiGiNc92Its0k1BiFkr6ycciCDCyzaK4+4K4fkGcRRynTzELJ+GtkfMsolAjx1h0ZtmJZcdXnFphEsWhfHgX'
        b'5iQSIEK8g43r+71l6INfLxVhyCMVfmnxDhyx0dFJXUn9GBsSczbb6E2Mc1CPf/fA+Ja2vVyXbGV0+953Rz0x+Mm8hIsoIgpgmW+Ep/+Q6wJxuOVaPf055OUhdgiN2t52'
        b'gDUro46o/A94+2MU+uvxUGgKA6Osp5owYhMG2wjVYGQ0JJdYwShGphqrTD8W9Fh9RUah2VHYdXysOhZCFY7FxXKMvUZARRtyq8aQEjvKbMSgdyxl8rIKxnt2rXJttXoj'
        b'8esp16oZ9KeRr/4BKpbHKpOREtyw3W11cvVqZd1Qzu/0jKkaco1hBr7NM8YG1zHIVmqGKy5/lOsv8VX5e7lz9iAdQ17n22NfwJx5saE+wOMDqgZHJqWGPstE/s3+OrWB'
        b'7o9xoObUGirsJzIv/z4NdzlrXFxYFA33ZU2m4AUE9Y5psynygok7sCMLrVDPjQKwNkccG5wrxJ64ixGsxI41jx180dpVH8RPhFfgDlVo4GKWBluo1x08sSt/phOI4d9e'
        b'selCcJ9O5Dxh3zdsu/XP7txxPiW5dzm/sU1W9aHs4uGbj/LqXU7vPRGq12/67aZP/9o3/++cSU53cyfe+MvJGbG1WxbNkl3eNFl9x+5l0/uTa8oP9K264PzRyZiC/T5K'
        b'8dtRD867tR199arTF2//3lf79iZh1ofnbiRdOdm3p3D6379dM+HrD35RXFMVXnvnE+HpWediu8paD1Utqxec4F3MjI4+n3z5S8OWsNtTPa7NVBfwXHZOZ7/Ymbj4k9u/'
        b'zn5b/s0f5jyrFS84mfsL49F/f5L05/Zfzfv7icB1bPdpsflvhN9p/Oxj7o7fzzG986zYlbi7pk9BcEoaYTdr6EVp65UE7tSBbnjN6qQEngc3CC52W8SuVAAdgQRxHjOz'
        b'SMvDY0XjQRLQV8i8sqOtAZ6xvQgEnPAHh+iiuRFk9xi8i3ACAhRZWS4N46GKumxSAge+BDqIl1VLgRVYwR1qcraq12L/qFLQ+fg4dSdwhQXPL1lEbsyaqyYvC5GqwAvW'
        b'l4XArY7Moaxn4HFwgoF8meC6FZWB3WHkMA6NA+wYjsqsiMwXtiFQBvcpHmGTNOgtFhM5KgNR/XgMomZgIdS1hy6Otkcgdi9x/95N6EkGV8EOLPXUbhYjIMhbwwpaBboY'
        b'95cLE8OI1w0LXB/peEPBFtIh7h7wQJQkB4lNsCnYH/QgMcYNHGCrEYbeLXb4YeDJgRp29qt1W51VvK13tS6H1t8EGeVakZHCnQoIPTarc5bJP8rsH4XfUORvqOvazLiq'
        b'WPyD9VkWnwCzTxQCIl5BHZVtla1V7VUY+wQMUhz3WCaxu+xSxbmKs2t61tz3mdbvM80SEHwsqzPrcE5XTncywj39AdLeiS9E9OVfkfZKMYzJ6Mw4nNWV1R1qjpxhCpjR'
        b'V3Y/ILk/INki9HlXKLsvlD0+MNYngFE5erfPNKbdF4j7BWKyv687rd87Fn2I9/KS/uXF5uUVJnGFKUhlDlL1+6gw5kjrDu2RmkOnmQKm6dPwg2nvkxfxYWii7feWoI/t'
        b'9jKTuMwUpDAHKfp9FMy9EafyTAHx6EafwGOuna7GulP1vTNNPslmn2REEEIx6wxK4xKTt8yMQA5fNvzdK4wil+hwn+LccOa9KyMODs/HMGZUv0WgjtNspWx7mXLcf4Br'
        b'9E/qH61+j3rSmaIN1Gj9YsOwTdbrUEso6OEGHJQ6ZIAZZVjhYWWpgvVDcjtUiNm5X7HCVF9xwmRx5WIO6YIB5+Kq6mKrvk8zwJaXaojucqyecoBfPOT4yljZ6r3/P+re'
        b'BKCt49ofvlcSYt/BAgSI1SAEYjNe8IrNvgjbgHcbYwQYG4MtgfG+JI6Nd2zjWLZxLO/YxjHeiffMdEmTtJGo+kx4TeukL22atq8kddvUfW2+OXMlIQnh7aX9vy9Whnvv'
        b'zJ175sx2Zuac8zNtr9tE5ENlgB+qTcxj2jYzDVFpOl/4kU5zJlKrPL3kROLpRCKD6/ySH4vDz0zpEHS6nCgmjUqcqvPj0O+sTtDM4FF9DJhUH2K4E6rtfOuDZNW8dawV'
        b'e83X3EmaKsuS5SrxOlZrKVPafdP2pKw+stHC9Z6SXcc7yip5lm8cpadpVveCY46253Akhfm8az25o7vfDoo1w8wy4bJaNWFr5WIqTa3hp4fFrHGMoZuOMU/ZGKkDV4O+'
        b'tcuW19VW1jaWc31BXdtQT/tIn3Pp6uXcsQpXp5yhb58DFT37nLgDVxJpbd4RZrb37fMoX66qIlJZVTl9ZY2/qcKtHk+D6t7G0DGT08ar0s7Q+8YbfOP7GUfvWDIctm3o'
        b'8OsM6RGN1IlGkiZgEKeSATJwNtsbJT1XdLKoK+p6gj5qkiFqkiZLk/V5hEwr7U0c1bGqY1W3392QbvLvPYcPPd4j//r5bMIs9iuGjZzNPqEh6b0hs9nHweHtBWQ4EgW3'
        b'ug0+GzFvEE6A1kPWCUrYm2aHrmVjjVre84850O19gWKNE8eG2Jg1gph4Uim8GKkKnAtLedzYZjbiDhtwVUQYpqKOxk0nUtyDecC7KMaoVdWbmNKh7hpxPf38xs6NHeTf'
        b'Q8H33B+SfzqRQuelGFwwsy0vuI6CYg01ulTzjKNAjZSneOoII0BYtJqjenBXdywHX7uEXA8zufQeHCupYdAmpIrCtJmn87sE1911kRP0ogk6rwkcfXbNsbMZbuzTMvb+'
        b'W8cqWeuOvJ61pH4du5T+pQdZhH523HmeCg56uXZtZPt81sR2YzGE5eV14B/K3VwKuF1EkvwpiitEQPCjAFkPmaOzulL1AaMMAaNg9hK3rSHTqUiq85L+K4vEGosEoAdP'
        b'eePGq2qeV5gq68KQ22r7hRmhDxhtCBhtKkxZD8WZeUZh4JvGYZUMXdt5NsNqmFW7shjaltI0DZ7WRRu45uJLrGc91vSUczpDG6FgoNg29tgDwxFhQdUKKxbALRzAmQyv'
        b'Bw0/PO8pbG9IePucjrTOsT0hI2G0mMz2hkefDumKvi7vCZ9ERhT/KezjZ/PJfEZoOrQ0lcHNdGjJCTfPqLx668qD2+U8o6IvIVws0aYdGa8Txeq8Yv+VjU5g5DzXjyY8'
        b't83VWHcguIUkqlrWqE37L6LTwUgn1zkmPL9z1FjzF26bgdBlZkKHHDhhRnj2fGA2P7cacOyN83D+ZTXOcw/WQlXDtjk0UpHYnnt0+4xcbKTv1VkJWDp0F4y/DuY0czrr'
        b't2gJoUnIzvMHhlYqYVj1TW/Wum+aik6mjAql0mrKoPcbYIAabSy43eEWFjHaMj3dzjUuHEpPz9eLUg0i0I0dzBtz3YGS9bM4M6gOOd9gqg3PakowV3MlsZir6YPXoSiw'
        b'i0Cr8NC6/eu0Wdyu8bPH1u+gCl1esAppb2ETVOtfotrUTYusZ3q43wpdZ6PdPm5mf5KR/a4vVwGqzc9jP0eRBfvpg50WwkdgiMYBfChqm/SiBIMoQeeV8IwKWMQ8c83g'
        b'2GjxUgljw3qHF2Q91bDh93koGhrziEBeBX6RqpQWvcjBXnXYFbtJpSxrqrOqFHq/BzgwnrE/07HecZ+IpTo/6b+7QxH5cefzapQrjkWN0gdt0Mhef/ZE0vbsugv7X3Qq'
        b'Vzu17fpSY2Ui19FevGZdy8sbVU1VytqVhB0+ZnaYnx2CIWb2EDXs4D26NzjsUXBiT3Bil0OXWh881hA8lix6xJL29A4HvThB55fwODisPb/DXx8sh4hwzUhtNCy9OIxt'
        b'nd+o/zes5tlhNe8FWU1XLLzEl+a1G5GO6xoaVByzfc3MHnh4HPrTC3K7UR88zhA8zsRtf71YrvOTc9yO1gcn/l/ittAOt4UvNYNEvyyzHSn2ifWQBffnoIvvs9vFzYvy'
        b'LwY44UA4IbDhhOxlONFosWlkWc51rG1JXzTlPNpOqd8eAeXdwC6bVToazx86vppnbMt9QtL4CHPI/EzlrMPWwpZwgOd9Ds2LG+qqwBPAsoraemWV5VaNUeHVXAMu5eVc'
        b'vqQSvM2VYHp02bw/aqepC70nWDb1VfrgSYbgSa1Zn4jDtVGn4zqq9OIRBjE4Sf48JqFD2bmkO1ofM8kQMwkgJbM0Y3qDIzTZ2jTYUNYHjzYEj+YejCFJl3HdhiyygieA'
        b'R40Jz8BcAutqe6K4q1VbttNiTWvIocRyCvNWY9U46X03jLZiI1PoTNnYvkaztGNE53i9aIxBNEbnNeYV6HV5Nr1bXoTe5Q1qK3rp/R3oTMftrmfMnanQgqhGixRWJFlN'
        b'4y8g1ahmWrfRZxBesciacHp/H1qfxILRxyqhYR1uaG/oaOxcrxeNN4jG67zGfxfrNNocVj+Hytr6Risq6f27QKWviUrqqa09fd/Gto06r+HfBWVbnkuZM52dKjif5hbz'
        b'FTz5ntUKMri1CZwpcz7ETVsGKrDRtD/GXmCMhidkzOT20lSels1DybNnJqLkKwWcCLxmUIHWW22QDrGNztsutBmh+c8bJ43b4GBFzTyNoPrJtfU1YcsbmjkN5+Qkzlii'
        b'afnyBoBVecpLkvexyWQ0DTU10j6nFU0V9Y21a6q45sp5z+tzJDnV1Daq+/hVq5bbzGcDHvS4MXWgQigFVhVifPJDqJAFxgrxDdJM2z+2dSy1D8jTB+UbgvJ1fvm9w0Ja'
        b'azRKbWVHzoll+tAR+mFphmFprXwqoxvXwlO6QvQBEw0BE58hrp+nYjZUrzTRxhhZ9U8joeq6hkYACgsGDnhY6/WQ++rqqsrG2pVV5aDQQYSjugp1Yzmn3tEnKG9S1alm'
        b'AEfAE7aFWbO5z/c5mQ+JXKk+BactTHWK6GmDCvx8czNaBQTgZFm1GII6CBogWAEBNDtVMwTggJAuxlWvQQAe+lQtEMB6QrUbglYI2iA4BEE7BG9BcILSCcEZCMD4XdUF'
        b'/PlXo4MPspU2nkoKWDhp4xoJQA+oYwTWttJCAdhKQ+DCBCa15D2WROncgntDJC2K3pBwEoglLYW9vtNaMnvFWeQqIkbnJnns7tcyU5OljdTW6MTybl+d+3i9+3iD+/h+'
        b'nq97Sj/zrADMUCeYk8Yx/iGtub1eMFpwFrr+1ELXn1rokrAly2yTLNN5yXr9ksEmORVMklPBIjmVGiRzCcbpvMb189hhU9l+B37AdJIPhE9oSJK5MB6iXveAfl60e2g/'
        b'87IB0B24ay78Ee2a3S+A5wqWZgnMqNS5R+jdIwzuEWBemwgWt88JIKdIkt6cI0SQhusxrJ8ncB8BlTLCjEEHD9yc3UPAztl+MIx1L4ZjJ/uhkHUH52SmQMhzjwMLeWPg'
        b'xAMLanPgJICroQI31l0KuRiD52TFAlqenUDIhyLaCVxYeNccPCsdeEMzBUITy+wGbjaZCt1HEwFziMDrfxPr6E4kyqECH9Y9HSgYFAifEQES6uCARMTA1aBAaF09FhXl'
        b'ANx4iYCz/gZJ1AvtQTfUeJcPPop3cwbgTgG8JrQNn7UPSP5PHmg/Wht/U4ej/BZBtUDJ2+JkxCbkb2GUgk4Hu9iEQhLnOCjO0QK30DbOyQK30DbO2QK30DbOxQK30DbO'
        b'1QK30DbOzQK30DbO3QK30DbOg8YNI3GiQXEcImEAiQscFOdF44JInHhQHIc6GEziQgbFcaiDoSROMijOl8aFkbjwQXEcjmAEiYscFOdvgTFoGzeMxg0ncTGD4kQ0LpbE'
        b'SQfFBdC4OBInGxQXSOPiSVzCoLggGicncYmD4sQ0LonEJQ+KC6ZxKSQudVBcCI0bQeLSBsVxRvMjqdH8KDCaV44mYbhyDBjMK9Ppknpsnyf4lCsd8NP7KUgCgwzXbRIZ'
        b'YRdtkoHNFDXgqqyoBzlzUZXRSrixlirCmsysKCKfyX4YLK04jdMqa91Yo0autWUVHCZYOBVeCFJtBecWT9lQ2QQbx+acrXJrUJkyrG3kVDe4V00KrlMyikozjTksHMK4'
        b'2eomr9poJlYRtogqmpDsOL1kS6fH8dwnTWU1Guc3qqqAIVb5VaipLwAgjhpvrSQ5VdTVhTXB3kXdapDjrbwpW71stbqC3Q1YMP5pHVkmHBTAwkXlAouXAVvz7U5N7PMW'
        b'MY0Wy5KhNH1sljV8JbOOXz6ABAp3Aqs7B6s7odWdo9Wdk9Wds9WdyX0HM1g/ncS6WqV1s7pzt7rzMN/xyZ2nVZyX1Z231Z2P1Z2v1Z2f1Z2/1d0wqzuR1V2A1V2g1V2Q'
        b'1Z3Y6i7Y6i7E6i7U6k5iviOLyPIw8x1L7sKtUkaY7tbxtJGMnf+seZ7JzG+kW32C9Q7rBNooe28oHazbilqoJGnp+aqgPnzIt4TWb6ncyFvMkmjT/VF2neAoe4y/XtBY'
        b'NPAWWSLbbISqfRqLLXJ1JF+2492hcZp1HuscrJFtWWZXE2lxzuv4S8wtZ7sNcq2alw/6aRx6rZNCdZ7k/zSNGxYHDaLPHiapWkR2H1vexysvfxpt+/biCrB0HTCWpS4E'
        b'pNI+t+lkFVW7zOgTQMhp7HMw2vzyWmWfQ3lTVaMK8H8451R9nuWLKuqXlptdgqqgdlUAzaW6CoEaAopeAw6I+zysPev2OZZzphkkx+VNquUN6iryCbo0dqQqjY0VfcLy'
        b'Zeoa+uml4KXVobyK+0N9trqbXisHMwXyUuViMCugGPUVjU1qsj5XVYFuXkUdwGfVVzcQiilDa6trK6nXE7Ik56YQc3TFssaBAvX5ldc1VFbUWXu/J/SSZb6qhqzwheV0'
        b'CCfZ0L/lHF+Cy21YXl4Ow7MxrQO5XqbucyFEqhrV4MuFbi70OZJ6gTrp88gw1QxXE47qqkaIkLpwhkkwNPQJlzYTEtQWEAV29la4BTQMetxoP7BwhlpdI7Ihk27RNpeX'
        b'/xI2Wb5kTXoTcMy5kNU0ajPam3XyCToJ/KhB2QJ9ULkhqFznV/6JKOTQhv0btJXc2XyrABS1BW1OZtA6DpcuRgZQC1FmYLswK2C7Aey6E86nna1Q7kx/JZHksVtvWASN'
        b'Nb5ofBgaQT03GB9a/4mWwvsRpqTGPxTnzsOUxkRcVCz8DTffxyfBX6mRvsehkfQzUdFcKlPqSOm5cSfHnZhwGhZD3ok02FfQmqmJJqw4PvHIxI5UvTjRIE4E8MEJvZII'
        b'benhNQA02BsYclxyRNLhpw+UGwKpC2xu1743LqEzviO+W9At0EnGawSfiCO0I0gys6fs+ewnofG6hFLdzLn6hLn60HmG0Hm6gHmf+Ik1mdqoDge9n9zgBydm5NcrCm9d'
        b'o406Hd8l1ItGGUSjdF70JxoFmjGur+ja4gfs0C4jAmxbl8nNgg/fChTCjE01rpTaYtUvHXAyHM/BQjQ2GJ07g6W+kghatdWrifhkIda8tM8LqgR3hnkF8v35jCUy3HBr'
        b'SD2wbVrW0DjgdJqiW780lJaq81VICwDSBjxjWyPpDaYMELdfmrArr0KY2A7PLNH0bCgzImR/l0B6Q5IWCqQNuKmU2gHS+19TRxn34FWoC7em7j8zwjh0dXXTIqMvMOpF'
        b'CEgyWjsa0dKeSTpdmXEZUdsBWEgtJ6/BIojiJNnBX5OHlQw8q66tgg8aVyUkd5JgwBbSLFmow+KMrIyLJ5e1jfSvCTYvjmrVx3FodHEvXdu6V+FnLPCzx8zPEYNxaIbo'
        b'KxmTZ2YkkiDrpfEdCY0/fJVhUmZN6jgrP/yA41K1yNojvy3JU6ZnZSZmZk0ufelOTmh971VIlvMtvQLNMw3s02lzs5BAjSa5Jh9GNrai8rBMik3DWcbWNVesVhudyofV'
        b'V9VUwHnKy2MMqH70KgVKse5+cabuZzKJtSiTURYNiy2ZMXPOq3D8/VchMM16YI2hU2hDw1JY9XMO9lVhFcuXN4CrQLJAaOJc8r8CdR+8CnWjgbo/m87On3qWmh2ovSwV'
        b'xkr88FWoGAtURLBWI/wyMmBV1FRZ9J7li1erwf46bGpGnoIMcHUvRV8Np+T641ehb4KdOhygq66hxpqssNiC6VnZrwCzofrJq1CXYU0dZ8Fer0xobEggfwZEtbDYrJcl'
        b'y8i0j16FrExrskLsYlSExRa9LE3G5q57FZpyrAVbM8BtOGf1T5aA9eDfyzhQcDglU8umT30pAo2St/5VCMy37o8+dEqhi2ajN7OXJYTUnuFVCCmyrr042wkCVuNg3QjX'
        b'sZOLiwvyFDmlWbNebiYztvqfvQqBU4HA/zJz6o+2BFpvI8jDssk4m1NFSK6nKxi1eYuXmy+Mbg+gUNCvY0tm5mWXTinOzIoPy5kxJT5s6vS8ogxFcWlGfBgUsyBrtjSe'
        b'GiBmQztebMxzqNwyi4vI4MBll51RlFc4m7suKZtseVs6PUNRkjGlNK+YpiVfoNvOzbVq8DKxvK4CMN84cJWX5/J/vAqXZ1h3GLmpw0RYzLPc/gzXWyrogFOhJlm8fI/p'
        b'eRUKZ1v3mJG27YDbaZKHZQy4ZcxTZBeTGs1U5MDkC433Fcafn74KsfOA2OFmYkWlVCjkdsBIo1FCa2146WUV6eN9r0JNuc20a0TjoU5POVqqBs5ALJfyL9/4Hr0KfYus'
        b'u3gIxy3TzAHuYsLgbMeOKGBW8ALqOCOTAarUDVbWzh5Waq5WxqHLhZZx1HMjbx1rqaRFrs2nINY7yuuYcsYilfl0ROVteWdJV7ndp1rzSYrlfySF+UzFeq+btdNCno6d'
        b'zjl+gXMosyzPrUIGTsTsr1LkUifV96EOvgXiAc/BAsqBbh0DZIOKhQrmc5udNBHd2ARumI1qXGuqGk0702vEtpVuEVlFXlPD+cE3mxiwQFwPaue5LKiYj9aJx3f4dQZ2'
        b'ZV7P1cWO14nzH/p9L7A1szdKps3pyOyKui7tLr07Tx+Vb4jKNwM7w1bcxN7ktOshGkG7uyFA3usX0Fb0yC+1xy+1K9MwIlvvl2Pwy9H55VjhQNtv5rB6Aptio7VgKWfi'
        b'OLhtgxrX4LZtsnxrgIEV3jQavj1Dk3IWY9uvVH5DKX9bn95Yq3PXDNa9rOHw639OnvUJYAfcjtWzk3FvvNxeYbgYFVRYHFcYX5HBNwo2pBNJfT0Sx/eI47n9UJ2f/BOR'
        b'WDN536q2Va2ez2CwydzGorxulndLLEqgZI3K+fQ0xlQUB9qM7Ftw11XVk6LY2VinEc1QklCbkqRS2/x4gzhF55fSKwpoXUGpV0gj7Skd0p17qibY52Fz+kI7Bu1HA10I'
        b'yk17T5+79eGL0Hj24mgUR1VgzNsnNJ67OHDHLgJ66iKAQxeKsNPnZnXiIjQeuAjo4YmHzdGKq+XJitB4JOM0cCLDnYZ4WJ+4qCQ8Y+NWRcFVDI9aRAypHGgNjam6Db3C'
        b'VjFBD8cZv7cBURE6g2IgBMPk7sH9zPMDJcuEDteYgUGm9zvwQktBmY+ET2jYorABMxkHICQTAINkAkCQTHh5OBS7OVgiW0wEZIsMij2SQbFHMjgslIE0/TyBf2K/g1CU'
        b'9BVDgicQkCQeFvghvX75AB5SSMFDCil4SCGAhwit0kCJQ2iJQ2iJSUjTcHApYLjfz2P9x/Q78Ielf8WQ4AkELdn9TlYUTwKKJ1OKJ1OKJ1uit3DFHg/FngjFngjFnkiL'
        b'PfCdXr9ogGWJAVSWGABliaGYLJa6lsAXf8oXf8oXElJdy+d+xTLBSEgwGhKMhgSjByVIhQRpkCANEqTRBMFRGjMMDQCPBAPwSDAAjwSPaSm0KUgsFCQOChIHBYmjBbH8'
        b'BLDLj7LLj7KLhPQrA22xn8f3n8b2OziEgk4ohE9oSJqjGyOO1JDWBu6Aev1Gk6zEpGpI8ASClgIbYgqBGAUFu1FQsBsFB3ZjqaCaAAqqiaCgmggKqolUQfVFOG/ZeYBv'
        b'ocC3UOBbaBohdUi4HD8WeqA5EPIBo8YcuPDdA+HKNuC0+0A3IBnvQ0dcV7ovd5Pm410yRaEcPHLhLdl4L5+JW+yAumSJVmp+pkmNw/rkW6r5bWHm8HlMFaj42Ux3cxzo'
        b'c/6g50L6XDDouaPSgeTm1MKrZpXCLU5znJWO5N4FkEGqeUon8sSVxjmTKzdQ+pvjrnSl05Fbn6/NCFdYq260givlmWa7Sdxsx1rJizxyZyYEzALKzVJoDUiWFno4pllc'
        b'QLe2+pzLlU1GZXZnsDWrqKttXN0XYXveDfSUW6pbqU120XIe1Wo3ZeJkysNkIR1mASQQbCdXM6rAJphKo7mp1Hh+Gy6lp7nGP8PpuWykjv5e9niTHjAAF4daVdilzYx6'
        b'DyuLVQxjx2TohVaq4171w9vgw2tf4cPGddT4V/1wy9AfNgua8fTDL2YeZVoI81SRIAVMsE8XSAhDthIqOu7gG62LNjEgHWYaghP1oiSDCCa078q6iBBG6RvCvoiKMIMW'
        b'JEYqqVS4m2+0sR8wgSICrV6UaBDBJPJii4Xq5y4WhmAUt2BohQoM55kq0NILmNn0zsJk1I7xrNpaK5C143lrYMyxqHgj2o6YxFuuk/k28a7UDFRg/VTl2WjW2bOniUje'
        b'MK9vtRb+wwb+szWvZ7kxbwu4bUuw3OhZBjANiwZwN2JsuBljnVzZUMXBCXC+xChik8mTLBV8yboXcInogEhlb9VEuJoEAbWpgjZFpPTly6vqlSYnYq4Wn+CSDmkbzK9Q'
        b'KgetQ2iVk4gDfAvDVKoYIuvYqBdNNIjAgMK7jP0kKFIXVaIPKjUEler8Snt9Qw2+kdrG06t7fJN0vkm94uEGsQysCHvE43Ticb1iiCQ3I3TiEdQaq1QfVGYIKtP5lfV6'
        b'+ZFh+JFXXI9XXMdYvdcog5dJ98Rr1DP6IKgnDvRBu55hrNz/DOp3w6HfBdrjAF2/tfONOIwDvW7f6rbVOq+wZ1ifjmRsxzCQCdYxmTZLYztLYZ7CfjljaZYw7873AI90'
        b'9lai+3i7PKGPmwocB1VvdIoDfOpjGy29P6hgibkmwV7RGxsaK+rIsA1abeoJ5AIkh4ZlyycA7JQa8trE6MRjuF/HCk1Ge267wvyAckbK9vHVTcvsrH8daO72eU6jjvON'
        b'JqkwHAdxeXZlkkAvHmMgoSjdIErXeaUbF8AetgvgARM52m0Geox5rcgtHQt5xvpXTefRjSObVSMw37xmTId2Yk+iWg/U/pwZZFAmBaMbY+BGZXVdcCr56X1HGHxHtGT2'
        b'ktXOKl3YWPLTi8YZRONacu086hew7skg0hoDIeueBFeDAqGN/OsIxjhDBT6sezikGxSQXMbClW3AyckyEqA3GjGRk3PwJltReS++hrfHy1kmE19yLFyCr1mJyybd5D9B'
        b'qzwYZCkuk388+o/f7jCHDxhnSqHSUemkdFa6KF2Vbkp3cuWh9FR6Kb3bPeYIWngtDkT49SEirwMRhB1anACSsMWnJbDaEQAFqTDtSGEDrYVpJ/rcfwujHNYpsmMZ42i0'
        b'OLGNc6FxnMWJbZwrjeMsTmzj3GgcZ3FiG+dO4ziLE9s4DxrHWZzYxnly5a3mK6NISb1oysRaMv5VeVkPLqfZPewcL5LaxwhT6E24xlKQQh96BRCFvs4coCSfemcXAkJQ'
        b'iysFefQgPPWiXPVt8WvxbxnWImoJqPZXSrc4g0VMm2PbsM44G7S5ZPgaqQW+Mn4QNKU/fcepM2HwO4QW+aD0w5QyKq+k9LlBpzPZTvSxU/vYYqlDHy9nch8vL6uPl1VC'
        b'/pb28abk9vEn5yj6+JkFBX38nMlT+/h5JeQqdzoJpuRm9/EVxeRqaiFJMr2YBCVZEDGnQOUKaxZ+Tt5UqUcfb3JOHy+zQDUT5lVeHsk7d3ofrzCvj6co7uNNLezjTSd/'
        b'S7JUc2mCKXNIgjJCTN6gmYCaSGxiQBgCB/jbiEhEHeAzZL0moO7v+Xbc3wuc7Ti0J08Eg1zc8zcIjO7v7caZ3d+DO5xBC1c6p1g4SRcomnLJHd6KHyyCRXAj3l4sx7uL'
        b'8G7ZtFwF6dzgNXsabiHdXZ5HHT8XxucVTcslHf9efHw+uMxG5wXMBPyaJ7q+bFrtP3/2OwF1Mzvyg0tH3085duLA+QMn2k60PNiyj/WYHnCIXX3x04iiXdGFTh875NYJ'
        b'vlBO/pnvhw8PezBpezMjnE8XOUv5T2B6mo228l3xOfQaOh+fa3JG7Y1v89EldDbhCRgu4DsB6DLeWYx3EDIALeQovozP8FZ5Z1F31uj14aFoJ9qL9xYkoL1oL8M6Mq7D'
        b'eHgbvotuk/Wmve1CqD4bJWg/y0Zo0oCGXqlOYYyw7CGMn0gTr/MdTn5UMirWB001BE3V+U210Xs2+STjJmrHAX1t1WcwL9lxvUzN342Q48+j6ipMSM0MBzZOCKsIYVkJ'
        b'OFJ+TvCdYYjDekPjLGfe9hjHrzTb2ZD/PEwt7y3oFo5ct9jG3ybY5rBNuM2RdBAX0kEEZPxxaHEkYxI3CgkpYKxXtQftNGQM3+5q02mcaadxGtRpnAd1DKcNzsZOYzfO'
        b'3GlqbDuNGVrNotNIFE1p5G6+L2orMIECkz6SkCCflptfhluKS2JJsw1OyC2b2oy25KIOPoP3LHfFrai9vGkstM3b6BpqMb57qYB2NtLxEmYYIQLy8W7SwfYWzIzF22c6'
        b'kW4pYNA76LKruzKaIhWcK3Zk3BjGazmzqjDcYxVDMaJwF76FtpugCpixuBVfwpsX0xf+J9yJIc0pyStxVZ1k5EamCVbbuAN38ixRsGwACxyZ2SWOrvjq6kX4LoXVmlSA'
        b'Owryigri8W4py7gq0AlPHj6L96EtTWFQqgv4bfxGlZ8sFwAO8IHUpCS0ZWEBE4Fu8NF9hYrD3urCl9AFmQJc1e8uKrMARogdFSVPiMUtiXF5RSzTIHXC1/LxCQrC0OCD'
        b'rxfgnXmFiUImGx0RingeXqib9iJKGD6P2vF9GYwVCUIGd7sK0W3eSHwcv0E5U4EeONHIsqmOjLDcaQXPBe3DR5oA0B2dwUfwuRITDWYKpsXivfF4+9RYfLDETKwjg9rR'
        b'AZeZdf5N0DnRZZVHSVUGISOWiVXjHRxgxLEmtF+9El8VMCw6zKCzzXhvbErTFBjU8BvoLGH47ng53gPAZ8tJMnwQby+NJRW+Mz6+qCwX7yk2wUcM4E3j03w3vBe9SfIG'
        b'GbwBvR1XgPd4CiFWincUkkL75vDxMXx3Lk2A9qDtgWYeM4xrwTzczSPvb8NXmuCoDG9eh2+WAM4Z3onOl1oUm36aYYq9IsIdl+cS/kPjFyjRhXTCqQNgyLSGKULa0U3h'
        b'kM0hfADfIOLfFXx/UfNKfB1tb8ZXG4WMu5iHDmfii5TF48iI+5aaPCfNO35GbH4CaT9k6uA+FatA99BWE4NJQdAB3O1CRu+aphQ6MS3OlAFzCMN2JuK9JbGxZDJoSVSU'
        b'5UrmUl5xLRVtQuedGbQLaSlhhfm1rvgmvq7Gt1ag3c11+LbKbQW+yTCiVD7aQnKnbCJcacU7C8auxruKEuSE3w6MDzrIR2/jC1LabdwCHGAACHsYsKzw/KzVTBPsjuWN'
        b'KGparl5BFtR4L4N2TMA3ayf5RDqoQeWqL4Q92Da+ASV5bf3Dlkkf5vjcd9Z9tP1G5bZ/7vgnM+xi2euGGWxyacV5w6e3Z4Z4TR8+7J9KzwvzPns8493puvFf/e2/1y/b'
        b'lvibo4FuXy7MqF2adBP/pvnDTxxqRkT9MuIPX/x4rKPsJx+eq9z50R6ni7MOx/1gmn/y8U1izY+Odp++6DxjUlnUgV9v+/Rcmvr2RIentZumjs1buvKL5D9uavnAofGW'
        b'3ydVXg3dX+beS33ADy+4NuWvXZsVcdfP7l+y7vOeBVd+//vfToh880+/9ev4TceOmeM+G1PDCz52reV3svcvdJ5PnyFcdeXSB2XNT37KT/zs6lvpc77uOre4dtOtX/ew'
        b'jhs/2d109z+v6JZ8bfiwa9vfZxXFNvOPvnHspmptTXb1qr//0fnwF4tPNi6V3G1Ujnr7t2syz/ZV/njUmbsTPt65K9p1/e/nxRR/GfiXP9c4rRzNW5tcmDrt+G0Vc7P+'
        b'zBPP8Q3awLHpn3z5I2G9j/87jo8V96I2vJ37RuQeQ2Gexz9+f3vY90Odpk0/6vRgS+22cX9IvePy59hrrZJ5+uJfbfrswHqP2Jut77mU7vuiVLtrRMS9yNPJP/44tybz'
        b'5MJf/ilqQ99PsybvXXu70OnbaNlU17d9Nnx1rfnvexOXdf7C72DX07Sqq2uHh25gXL/W3v38M2kkFUcypnm7ovP4BHp9kDSyGW1/ApaTAcPJWBqP9iQqEnIBBOQyvodu'
        b'8PCZQHSLgmfgXWX4jZh6irBhDa+RLqDfwBdC0H60s9kjSezuosI31Phmo7uQ8VvBL0FvrKRQKelkjH/LBJtWuSYD3UKvU9AzYUUt3lmIu+PJuozP8PF9Fh1NQZ0crsc7'
        b'aFcpIY1Ic1LcQml7Gx9Er/HwqeQiLsVufJj03Z2eK/HN5fhGk7sbahcyriLe4kS0jSKzbUSb8GVZQixAtKAj6RSlBe3AJ+nrja7oOHoDvUkkxPg4qZyOm4QfYYIFqDWV'
        b'A2A5h3eh9gJ5kZDhrWbJQPL6ONSWSaW4RCe8j/TuHeg0PkNGI0K9YAyLrjDoBkW0Q8dxG5l2dhSSNxewuNMvEb254QmdSNrxa2RYWem2ognf8kQ7yIi+He3ydHJ3wV2e'
        b'K0mnxzebVxD+FQmE6B28SUazm+kokCXg3YXJLFOyVDibZIg1zpRE9BY+sgjvzEWXiASxnpWj7dkMeo0C5K0aiy8iImfuXFaPOnOLEJmZ5flFfCYI3RA043fwaVq/i4PG'
        b'QqI9ZNomVUFkzUnoegIPv4nu42OUTQtwqwifAVBBSGIecYYVCtwl8ZS6pcOIiLAzEWYqB6Z6nHAhL4JXT7kUqMojEcYB3YFxLZ6I2nlk5rjlQ8H58Pa15ZAtaX7FIDgU'
        b'4YsLE4hoTrgmwWcEZIB+C79JqZxChshDxqTQUrNxi4DxIBJKpq8jbUnNeGcswB4SJrHMInxAmMcT4QfZFJMGn55L6pG8XNTgnCBXFBaj3XgvSRaE2wUr8G53rp1vrUcP'
        b'CCdMsxd+m8gKHiX8ohC8meLeyCeTaXBnsTyBSDwFfNIad/hn8fC5iUs4VJwTy/FpEp0fn0eEGGaki9No3iLSPC9RuJ5pY8ea4lBLMfeBcehyHmmWcbEOePPkRRyqz37U'
        b'6kQSKuLR9sTYhJFoE50zHAg3bjk4oPtoH62RcmUzSRSCjsoHcDd90Nt80h5vVT6h0sGlsWHQL6wWRmg72ptovQMiEzJz0Rm0O9IFHZfhXbSBEqHkTSIb2X2bjCUthVIh'
        b'U8jE4M2O6Cp+gI88SaSiyhtNdLLbS5ZapIC5aJuoiBR2T2IBGTL2wLf4TA664kgWNkfRVlotGxegWyXDufaB6EvkDSEzjIwDD/AptO1f7n7JZDtq636JHtP52yxVuPM5'
        b'uoJayCld9NeFMAERrWu0MR2jOBdbsMucx+0yD0B6PxaFgnthzr0apMhl6V5ytj4oxxAE+lOPRbCg8S5iKXp44iNJao8ktSvneuFDn4fhD30MIzIfVuklhQZJ4asDiz8W'
        b'hYAH+3zyjZiOtB5Jki5U0aW8vuxhnmGkQhdaqZte2ZoD3u3nPwqR94TIO5o713VP7p7WPdmQOPGhSB+SZwjJa81+HBjSHvIoMK4nMK5jpD4wxRCY0irshbxZ7wKuXJMe'
        b'jtRbui2TRB9fc2RNR0xXil4y0iAZ2er2WCQ+tGb/mn3r2ta1Cnp9RZqV2pr2jTpfOfmRLDRxupKZxt/scuMveqE+qMIQVKHzq3jsG/jIN6rHN0pbpveVGXzBPZB3IUsY'
        b'VsBdUTLy9UEFhqACnV/B4+CI4/lH8rVr9cGphuDUVude32DgRSarFZ0O7ljUsaJjkSE8uTtQFz6Z/CgFvdEy7QztjI7Sy7MvzO5arU/IMCRk6BIy+vns8CmAGSLOBMwQ'
        b'EoKaHAnJhCfRxnNl6Gq+vpYrii468+FKfXSRPkhhCFLo/BSPfUOBxqmsduzPRhbqIuFn5NpYfbRCH1RsCCrW+RU/9g3XztP5JpMfyTo2/tyak2tOrDu9zhAz6lHM+J6Y'
        b'8fqYiYaYia2ZBr8onV/U4xgZvXwsiaYWwBGxHWJDRBq59jRbE3MxJrteo1VySPjxOUfmHJ7XPo8miow5nX56wqPIUT2Ro/SRYwyRYyB1WG9YDE1tzMNoKjw8hjNejkrk'
        b'srTFljedVfdKwjmihmujtE2Eal1MxcOc7xU+ypzbkzlXN2+hPrPCkFmhj1hkiFgEJLd6GlXduP0Gb6PLPZN9vgBOqlSlED8KNrVcKysazab2QnXl4qplVS+KCWUxIkDX'
        b'X2j8zzwuPHdAuAWbFw8ZbvPiG+MOxtIQlqVOvP4N4Xe1C0LRsc45j2fueWS48l9amRrcE1DOD3XQbs0+0wn7N1aK6C95tK86/YyDffvfe2qt+B4L2tFmRzlcAcKMuEdh'
        b'saqqCmVCQ33daulL22FXc0xxLTdaZJXXKl+O0H9Y2xAkbDJSHG/PzKtWPVAIS6pf3uzl+89QObdPKOwdW9gShpZS4y4w7TJbbL4aRZzyBvi/aGpsqK5+Oar4Aqt6TqQm'
        b'QU2NCSSjMHAGMmCGBpRS6/xXJJPq1AS+dEMUAoEDZgRx1IygttpoN7AMzEJIrVbVg/Mj5f+ShW7lFiPky5HpDGT6mBQoOJMvMHGoAWBWs23oqzc5VfRLNzg3IGnAHCTG'
        b'GtnVhHfGmaFZEmZB18DJN6gzgS6c0ckdn27ZwuG8DaDvepZu2TKDtmzZQduyzAbWuGVrN84S5vf55xxChf0T+5VAN7uNJKNOzYBqMLSwOYdZz3O2Q8dguGJCGbuBZ6Ta'
        b'bpzl6cynTawdcGL4z2gLU0XdfllbRKjD1IsbmuqUoGxCBtja6lqwwa+pADsKu3k1Gr2shU2pq6oA662wTOoHCBpegwqUUDh7f5iGa0kf5gyVatV2M1NXUaTkhQtLVU1V'
        b'ZHqv5Xp/3NKG+sYGMupXLo0Lq6tdpKogmYN928qK2jroeXYzA3OtxkGjHHnNpIrOoRdzdnOrLczR7ObGWdSZCcyuqFMTCgfjBsN/Vs3F3LksmgtfUfsfK0fx1bD2Dv1K'
        b'fPT90cdOHAjfyQpfCxydmnKAGb6T9/nKf0pZuv5KSECt5tWXS6j1+usovk26pZepWxrVbwTVNVWNa6Ks+qW6sq6csnBA/wJS0ZUSHKDQlVIYExzWPlHnZ3mOZNSdtBbS'
        b'6FnWQpP5i+ohaDG80Pe8yIvqasYINz4/jGV9QECyDb7TQ6MDzlLmvMcovn1Uhg3QR/lGMHEHeizEGk9SAT3B5hT0XwAk/qInqYBkiK/gPSqrFTxpDHCus70wLj8eXSiF'
        b'gwbYSqSnqtuLC+GwA11E213HVKHdtcyJL1n1RJLPFz86fWQ1d4L6Tm7ngWTS9nb8rUDzafBWvx9U7XJzuxhY8T/Ds4dvVWhDS/WKs6uGd3tsXSj8yQgmZrzLbz8/KOXT'
        b'7YTJ+D5+DZ+OtiXI3n5COe6mmyepI9Bh1zjYuYGtjR1+5s1KCbomwJfj8PEncMQ9G78TnLvY/q7DKtz5IiespBuoX6gbqI3dYJyxG6jCmABYKvsXstoyQ/R47vKT0Did'
        b'LF8fWmAILdAFFPQOj9MqO9JOLD29tDWzrbiV/LM6fKWdxvtZyxvj4euA73HVD1+sGxF6g6AbrWRM4LcrSD8KhI7znOA7g7yNgULy6IkUuotuStD92QV051jgyaJzM9Ep'
        b'7sxwJ94sx28sKZApICqVRdfQKXy1Nm5+M6uGM84/Bi0++v64Y5sPnHhdujv5jStvnBr28X+99+XC/16YV6mo4H0dsDRgSUCJ5jdJDqnLyaDxKMLZUGDk8HPMciw9upt5'
        b'uGaYfd7S2i/har9X4NQ/J8zJW9bP2An8+N4p/cwzAycmPLpDqROl6gacuZtIHrIpWJOseg8awhDEekLVNxib6lxS8c5QtUMH31mdv8YMpZhIxTMeFXMERNDh/RsFnRcS'
        b'z8h8+45grUANmtXKhwd/u/3o+yOObd5+4sAJOvK9mZyS1Fm95Ssy+/6UafhYgF8PIXPvGGjbHevwNbrHio+jw8/fpeW2aHHLQinPonJ5dFSy0Me21a+giti0EQYa63VS'
        b'OBMgtquLbWpKdiblgaZkodAx9AfDoSEtZYxT8cahpuLvdD5+RiP6fyYrD2pC9kQ2gaK09kLHt6wauP35WC3IbOFvJGs2p6Yvc2c87vPKjm41KcDbiGOcArztvhSn+U4r'
        b'3dVY6dmk0oON5rIvLns9I/coK2ErK/xfXbkAp/J/rHKrbSvXTJL1+HC3OUagBqPVv6MHR9/v+ZZI5KBTlh549fFdh0K3WQ9TwhbsfsyWXd76O6fqxx8yTHif8MTk7UQQ'
        b'gqO1aeiAch5oO8TDWZFgEotuTK99Aopq6JhitJ1DGnwLvz30AIJ2ibnDrjfxNdwqo2e6oLtwbJQTvsND+9B13G2nnVGLlEH7n9QUhbazSK6d/bkQ2hk1R3kUPLIneCSH'
        b'4GSNf/Ti7e8ZX42xan8F/5b2pwKJ30o9LNhU47ehEfrbVQ8D5VQP6kTfpJ4qbPGlyqtmJdWWwJagFscWcQufrBCCW0JaQquDzapj7v9y1bFBqwR7qmPjFJxIdrUMbyto'
        b'jjbqNIFCUw66wSk0wZEzutIwz1WFb+AbnqC/QnVqvNBp3Ibu8PBtdHtSE4jCdaShtVPFmlzSAItRpx3tGu7IGF3jlGvw1lWu6AY6ih5IhU3QL3KRRq4GxRgGtxagvQza'
        b'NRt3UxLnkibfiq81EeLxcXJ9nkH70ofTl0LRNrTTFd8EFZgb6SUMOiHAN6iiELqzNkoN9g+4pQqfYtBWkZBTiro6AT1whXaJL9fjqwzSEBpuU3UaNjxEDaDAeH9VMoN2'
        b'oDPLqepNy3xOxW3TlBWFp8LqORU3dCcSvQbqRpDRKSm+xaA3x+J7TaAbIYrCu00lWTKbFARfE1P1o0TCsKOUSzbMwV2NKny9JFeGd+C9hD14xyzShVuRxnk92hPQBHoP'
        b'aDc6l5KKW1OTwtARAcPi4wzehM7lc6psd/F5fMRKgY782Y2upFKFwKkz8cHU/BJHpgxrhPhG9WxaXMLTvWmpcgzNKJlJRkcYyrjVZGy6hQ/gBwiMIBKZxLDIum++/fbb'
        b'v5LhEDSQWmc1Fx6aNYOhemRomyt6DT6526h5mBsPK8zdifllsXg7IaIkVor3zsz1w3fzimCRV0SaB7o5HVqAsN59/iR8sWky0NIxjdPwnZmbV5RHxjxjUmhOpMa3JxYb'
        b'OWWpGAit6CK644avDsN7m8BsFF+vxefdyQv73NGmJCcHvKkMvyXEe0rds32CnMZNR3fQPfwWvpxVs8o5JrtatMIF3xU2O6EdzsVuqAu/jk8n4XtrpRLcMlaOjwjRoSlS'
        b'dG3CCHw4AGkW4P1NIPfXj0ZHHfBmvNmdSXbio64ydHUOPiicDOo3eBs6GIe24Ht4L9pTKq7dgDrwJjG6tyRCjG6hXegNdLN6Ld7CT44lVOyW4CuZvkXr0A46DtG2Nn1D'
        b'EDuCxzhpCzeOP5KQxjTBvLAmBu3AO4vCQlHnVNySR0qfiLdPpcqdZhU0dClXUVREV/Bv41uulXgL2kRz/NW0PKaVYZJaZ1a49EWkM01TgU8XRmRDGQ47M2Fu5GLGgqVo'
        b'P+rEt/EJNpm06zNjU0llHFiIbuBOtM0bHymLwafmEJo3+Zei16pQSw3W4m7Hxeiu12p0GB2grdsfn8skZA4icia+kpuQ7+DjDwra6LyU/EjvwhedSTN7B+8ulbJNoHTk'
        b'kBYIDYDMdHhPXjwZLEj1ipwm5AmS8BncSkcZfBd34q6ChPyikly6i5CHW9AdUPGUzaCK4ebGvyc3Pr9QnpcQR5rIDqlbrUMA1eFDJ/NT7OnwLUbtCqPCo6USXwA6SIij'
        b'yj/n8VYPmQJ1B+A9LMNDe9gpPOcmsIbDp5LQa7JcwrxdRVwXSMzPS5iOruD7sVTRc5A6Zy66ULocBoGp0xNm8JjVpZ6r0Tv4LG1cSXjTpAKqTJI3zaiBa9y3yS0spgXF'
        b'x0fLpzmtxDen5eYXKeITFFTLF/qcWZWTjtF413RvdCYRH6Gt4F1/PgcKM1Edv9WjiEieTbB8QO0ZSwvkWWirUQPGCXfxUAvqEDaBeiU6g9+ZW1IsLUK7i/Pi88pmDlIs'
        b'zi1jSKO/gDaRqt2Pd80LQxdRNzqdG44eoKuY/E1FlwVkyMWbfdDhumhaz/gA0oSQkfOap7MTvuqJrzWuaGIZP3XOBn7xtLl0jK7HpyJKYMhCR8r4ZKjrZHBnlXcTiFyo'
        b'O400LWkC3cZSEKJiS9Ata9GIz8wPc0KvoVPonSaqfk9GcrSzhAygV9G5Ury7jHQShzgWHcH7UAv9Xhh63c115XKs8WDJ196EUeUQukXHcjKyPhDinYUkYvQidI7Be9bV'
        b'UigeMpTvX1JQqFix1KQa6zqHh98mBbtLW0ypyxLyGiGsuNSkBpfOowPswjVoSwHeoVjIaZIl4pPF3JRyc9gqvBP0sdDB8Q6MIJRFJ9fhndzXNOguugotY4UHaNqiCwLG'
        b'zYvvj+66NIHaFRnWLq8nLVsKLCiKzwN1KLw1FDJzYIajTQ7VSFvDceM4af+tJAJ1JZkxhLCGhw6iHdkcHWfmSmSxCWivl1FVya2G7+kpoHHri/DxAtIWyLDwOiFRwJLs'
        b'yPTGzawatGU43ikkbZLqYgnn8/yZGMqM8hh0Ae+U5xeht0JJQxzJovO8Iu5jN8iwuB+6NB+Bxh0p9CnUOYvyPo0lvWgniQJPSIIJLLroH0TVu3MWp8hi8fk8bvAjrRN6'
        b'rgMTjg44OKO3SFei+rrXavED0tO3FytIYbcnDjAHX8IngEEcdxRosyOZCi+gO7RLVODzApkcdaKuvHgpGYKcx/CoYvYVrsO04W4EasbX1fja+ihHhocvsQn4yOTatz8S'
        b'8tRRZMYsvv/L3TMKGvomeS2YmPTr3eEBvk7OyXlPc58W/jT7wtOYC79YMy/8+7kzlBEe+qfTb2z7VFdQ+ucvfUVfR45lf/97udi/4OPff/iTUam/JDcb12x0duPv37A9'
        b'20/ys44Jj5xnf3F++PCpnim1qOPd99oy/3B03LYU/bXD+beGhauf3H8v4n90i+X/oRt+aAlPhn2W/KNn7OHLs364qvhyUGHND3pXaXJEU4u740MfjPlnQoo05fC7Iz58'
        b'56PGI5LEdzKHpXbcO1IcxDvESy11e6h3bqudZtg70zvTM3p5aajXRoFiYc1sl9/lZXx/y5tZF3tP+1dHHJKmHjjpM83b+/r7ZYnbxjyZrbja9YOzr2XtPvxluuBMKVo9'
        b'5lil4lz8odKbFeFNxcf++rfMz//ycFtlryTvk8D1qxcK/ik8VbbNsGX0T4Sib8eu2XHp8N4FRz70eRQTcTv8FBaeDFL9PtZxQ53+1x96NvXtSqg+vzTiL4un/+NBUd3m'
        b'B7svRx+92f5o+p3Z54/9+Rc7583dEfLFB38+8bbPf/6i4+qtX0Q3yO7e2l7+9VeLf7Nh5s/Xfy5vHtV/rMP12NF/nvpx6YE19xxDqi57vr4mLmvm3F+M/OU3f0+5vaX+'
        b's46pd/1/UHv6T38fv+9XmeNk60PPvT+m7t2MntKs038/eSn74e73P7j2+eTi9JkJhj++tvaSnv9hfcwH9WF9P/55172/LI9aHXvin17zzrt+cqOpYI9jfc/0qoQ/3xSv'
        b'fBS68nT6z+p/MvrtbTs8JmQM/0MpfpDyOLz4uMfMv478pve332zcd+mHq9/M6Tz0fsk7v9njd+zA/Dv7flxwJeStD96JL99a0XV0xbC77zJLf1r2s62hO99Ujyve+fuQ'
        b'PcvuX/7iR08/vybd7vpY92XC/R+kxsRXRq85X9Z16ISrpsxhSeQfduhq4jee0/9m6g+/cigf01b+dcj2r6Xvr1dMmLL6+IHyE+se/ujyu+9+5X6t/9gPxPWny383eknH'
        b'Wlf5nj+2fn/TtY0f1QV/9C7+ii97vIoNCZ7o8iDxG6fjX3x+7C9zd+5cvELz5c8ebNQk3LsVPeNIaZdPWXXlR+6/XvWreLcNaV8d3LAj7Jjf7i4fyfGPj//o6/+qmX/Q'
        b'7eBbX399vur7l0/3/0nypyU7GxPve7RKo6nWYx0+hq9yqqr3yABhVlfl4TcnlNHFMumqZ8cXFJPR/iSnapyBLpc+ofL9hfn4ChlGJXXGYXS6mh4G4DNoX94g1WZ8XSpw'
        b'wm+g21SHtQFp8G2ZohpvNamxOqEbvJVx6BSn+LltRi4Z2WeNsRrZ0fFyGhtOhrwD3NCOH6w1je2ZuIVmvWI0jFnxaI8Hum/Wv+bhM9nraHl4K9WyifgtSp4DI1zCCyVr'
        b'E6rtWrcM35fFBUbIpXhHPMM4zybDTjTaRzWCE4pHyyqFcpjz4sm4ivbwEnBHMqcwfYzInQcLzFIx7pwoYDxn8OvQPdRNNXLJhKz1AFXZADJNE/GqeEAQFzKSAgF+KxBf'
        b'pKrV6DDegd6RoQerjEQIUScv1TGF0ocPLUI3ZWnoDqd6TfWuC/DJJzApT3bBp9Vot9MKd3xVDaYXtrrP6K0yIVOEbwjR/cJsSnctPpIosz6v8cnjE4EYaUscOBXf/USI'
        b'uFdgOiUqpprX3ngbvzSOTBmbJnCmda346DxERLkdiQkwuheoZjsynsX8xUTmeINWSA2zQlYcryCD9g5YHxWQ9oXv8/Ct1Jk0Gr2zjHxEvpKUy1IEckFXaCtboFwK011O'
        b'iHGyC0JnqYZ8Oajbuw6yCNy9Fl0iAhrHzctocy7h+6FUowoz6C/Xoe2UY2PlZOKzq4+LN7EDKrmORGS5i+5S3e+G9WRBB7rftprf+HiToBnfCXoCW9Zo+wgiYNkqJucl'
        b'EKnuklEzGWlk1ExgBL43RiaX5tPTtSJ8YrUD44k38RvwkXzKmlWroJ2TdoLPbwQmODCu9Tx8FF2Np+XDb2LNODo9o7e9jfMz6a7nuMh7E0g8FWbIGzuN0kwVx/NyAdoO'
        b'oowSxP8BWYbMqbTBLgmvs5FkyNhwxlKU2YVv0SaCzhFh4SSh0VIFfBjeio7OEPjgbdOeUAu3A0iLrj1bdRpdIG3fZl/tDH5Am8A4b6+CQtIYO/LIADSdjcN76uk4gG7N'
        b'QzsK4lPmx5IhpACsPi/yVuOD6A1p7L9OyfnfG6jB5YOltsJgdFsbRes+Txv4Os6Zi3m3zyaWbjVuFHJb2qXhTFhU+7pHksQeSWKXY7ePXjLOIBkHysWhbWv7GRfvuWyv'
        b'KFK7jjsv+yQ0VictfK/xw7V66Rx96FxD6FxdwNzHsYU6v+jeqNjThYaotK5FXSu6FhmixrQW9UbHn57XFdGV3BVhiE5rVfSKojo8ekQjdaKRJOpc+clyffRIQ/TIfj4T'
        b'MKo3PVdXOF+XDr/e6JQuZU90ui46vXuDblpZz8Qy3cQy+vXc9ybopbP1oXMMoXN0AXMe+wZqcjQ52uzDxe3FPb4yna/MqLe9Uh+dpQ/KNgRl6/yye0PCNCXaYaeD9SFy'
        b'Q4j8UUhaT0haV6U+JN0Qkt7q0us7TBOn840iv16J1MgNvl4ywiAZ0TXdIBndmst5ARm9b33beu2KHlGsThRL6ZmqK5mvl87Xhy4whC7QBSzoFYW0bewYbogbrxPB72Hs'
        b'D+VIrptWqp9cZphcRp7Q1xS6aTMN0xbqpQv1oRWG0ApdQMVj35DWdE1Nh0OHUruOcxfRz7h7x3NfHgV63hZf7uexIVnsV3yeJBv8qJGwn+EFZoMKdeJIvZ+sVaHN6RWn'
        b'6cRpXfV6cZZBnAXH5AtZ+vUF+tByQ2i5LqC8nw8PwYtbkk5EWoBeNNogGt3PCPzje6VJGo/eiCiNo8bxsVRGrsMTH4Wn9YSn6cNHGcJHPQof3xM+Xh8+0RA+sdWjNyj8'
        b'eMKRhMOJ7Ymtjr1B0RqZtkYfJDcEyckt1bZv3jeubZw2ktO2p5VkUT80xQa973CD7/AOH4uKnK4PKjEElej8Sh77ighdoN8/4JBFm7J/Q+sGWqZsfWiOITRHFwCOVDVr'
        b'NWs7RnRn6iQZekmGQZLRI8rQiTJowgJ9aKEhtFAXUPjiauSitgngCHY+q60513CyQT98lGH4KO5JL9dTBP7kUhJ1fOORjR3NnWsfCr7nrtmolygMEgX5RuBS9pOIeF3C'
        b'XN2CKsOCWn1CrT5iiSFiiS54CakBEktqIFBy3OOIhy5mrj5gniEAsJqocz04tR6lTdemdyzu5usjxxkix9FHvRKZZl1HbkdRN/sw6nsynUTBfa01lzRWf0nrHK1TR6Te'
        b'X27wBzgoSB+vWd8xy2g9kNtLW9viDie9b7LBNxmyhALEHF9/ZP3hje0baTaBkZogbW6HUh+YagikdhnzObuMufqgeYageTq/eY+5ymhP1zafXtdVqkvL757fKw4nHXJi'
        b'R07Xgq/4bADAWUPYKiCMJEnH6XxjyI/rp/qg8Yag8Tq/8Y/B52kk1HA2S52eylozWzMfi0M1qZrG9jUdqeRfoyFxsl42xSCbAvYXAY+k6T3S9O7RemmmQZpJPhUMfQHC'
        b'VuqLMaBtvDarx1eq85UC4lhmb0ikdtHhua3ZrdmPxRHtEw3iRPKFgBiNZ69fVD/fN9CnnzEFj8Ezbr8D3AqZkChNTr8jXDsxQeHtwZrgfme4c2ECw9pdNa79rnDnZopz'
        b'hzsP8lZ7saa43xPuvJjIOEPEKF3EqH5vuPdhgiM0I/t94dqPCZHpgnO7PB466hJzdcEz3pv5Xv43/f4QN4wJitAE9IvgOoARS9oTNYn9gXAXxASFavz6xXAdzF2HwHUo'
        b'dy2B6zAmIkEr7g+H6whGmtDpZoidrIud3B8JT6I4GqLJdatDfzx5zxAY/ygwqScwqctPHzjSEDjSwiqlNyRJF0IiulY9DNCH5BtC8luze72GHXLZ76JJ08bqvWQGzglk'
        b'fAq1V9Bm6r2kvV5+bW6PvCJ7jPcGzpekKLjVzeIYS8IdYx2H4yHqvUgGQSK1SqhaZda5tXDp8zImCd/RvAwLnUGGDfbsnp6aHc8NNQXHwbmbH2tt7TAtnGVLqDXC/z/D'
        b'78yCAo7bbzhnuDLvunpkBPKlLPXnpHgB7UC2BRwDCf+t2oHVUt6nH/PsaPJmVDdWqcIqK+rqKMguWBcYQYdJa6iFZlBRZ4W9yyEaKZUcpF1FWH1V86BMOb322IULpy5r'
        b'zKuvJi1xUV1D5VKp3IiTbNINblJXVTfVgYLu6oamsOaKeqoXq6xdWascrD9rRURtPU1YTV0uG93RVak5H3UczF4YIMyE1SrVg7VrBz1IX16hqlgWBp6i08PyqI4u6cnq'
        b'WsAiJt8Bfd2KsMomdWPDMi5bc9HylAsXSgHFYki1ZsIfEz/gsrY+bOUoeQphxWTCxmZgZuPiikYztQOa03ZzNJaNAiRT0wZOP5lkAHDJViwyefurUTU0LafAZnZzJEVv'
        b'rK1sqqtQcRrY6uVVlWYH2OqwWPBxGk9YQD5LMQVWLye3VY2VcimthCE0sIGhjVWmejHWO7VcqSc0NxFGkvyh1a021b6ygfoaXA7Q2vbytKqAwXX6XO0MFwU9LMUXJqHO'
        b'AvORNrqCTvA8EtA+7lgbdBtGoNvovqVjhtLRln4Z8BV8mx7vSGMrjId9YU58OE68vSIJtwWF5vpGr1iPL7s7T0dvoEtTUNvcyXmNZAF8AnU5jVfEh+B2fAK3Z6I7kjXo'
        b'glfSYld6DKOan0sP4x67Lo5rLpnF0L37UrS5iW6Ol8SCxTT4/wCPK464XcJELBHgi+gKvkZfHynmnEA8zq+MT96YwtT+5Ys6gfokiXktGHEaumN2ssJhSSkLWekuaeEH'
        b'moCAGanvZi4JnK5ZGvB+wI67m29/ejLrs+jf596etUkVn7TAX8zHKdrfXvx05IjklSnDljZfjV/4/erfpIQtcP9N1ZV357+nmNUk0v1XxJjhWxVnFdmlY0tmXXtXHvdZ'
        b'onemSio++4FLQMmmcN+PnH1/p3x74Yefvfa7hZc/q1qYW70jpyVJAHqYn3zK5DZHRF5mpK6ca4E2fHC4tXU6voO6YcsPH2ToHtlItBPtNrkWgH2bDLRnLLWBVirQxWcs'
        b'5DeE29GvewN1PoEKR0fQ23iHGs5JE/BZdD7WdFjkjVv5qAtvR110c2Ic7oqSKergCNpiaxB1oquUOK855SazfeFsfFrK4s4VddQjQmac44DRfhhuzcZbF3B7Ia/hCzUy'
        b'87YZ7EPxEvD+Jm4L4w4+hF8z7lfizeiOpTsGfEJIt37wVR98ZdDeTxHq5gz/l03nTO/34YOo3XrvJxadpds/xq2foInP1YUdWMo7gysn2rdt1EvNz+ny/UOGW74viB5i'
        b'+d47YPhKVkMGURzgyhazn4fGkMlaOontnZz9PRkRmKXgz5uVFIPYLKG2kIHF7GOxBJKPJoJvWBRYHR9e176OWlSn9UjS9JJRBskojYAux1jvkZopmilaweG89rwO3hGF'
        b'RkHEem25PijNEJSm80vrjYzRjusYwdm/evnpvCJBNFyhB3fgkdYemK00s+XPkvIGa2a78Acp5Jo5dspaF3tKNMsGgMjynOC71cVm+xzJnFxOJmX77nOpHMOaPcZx/uL4'
        b'Zn9xDv8Of3GffiOwI8eUVNUb0UPpLGa2kGxSc3JNFZ1ZyDSYNTlvSokZ0UXuMpQwULWotlJdXllXS3JJp8ZHJliYagAirFwspynkWRBOockWWmQ7RK5G7qZT66l4s/kU'
        b'gAOrqyiZDSolPCDTrN1pML26qb7yGTTIs8sKF1LYrabldQ0VSlPpTQyxmymAcZphtGCGNhpMqptqG8EyyoIo+5Pzc6maMqV0Yfyrvlr2yq/mTX3VVzNmzXnlr2Zmvvqr'
        b'k1/11VlZKa/+aurCsCFE2Bd4ecQQBmx51VSiMwqUVcr4sDhj84+zsoKzNtOj9in2JcChjO+yVRUUZ3ugDb+Mnd1MWDNwo8LKVHmSVW+h9oEceivXncgHV9ZWvBqnJpeW'
        b'2SEhnYOYUXNjDEcH191qlc8Rc+3pbvorqDyYNkHIXB8dQmbthYXnFwYxVA1jdhp6oHZFJ9FRUGXUMugwOoM0nIZGJ96eia8lJSU5MOkkPo/Bb43mlFLwJTG+IVPI56SC'
        b'etObbEHcBk49dCu+ECBT5ON29A6PxLzGjh6GjlL9QfkGfFmmyFvlCW+0sOPGLZQK6DsrwcsSKPjgqw5MHt7MD2LH502g+hON+Bw6Q+K6GvEthnFE+3n4IBuO3p5NFT48'
        b'XdEpdYoKbULXeQzbwKBb0yI4eV6L749Q45ueKgeGCG8HePgsG4eO11PSA9EDfAaDp/BE1Ik7mMRZKZxqyS28bQF5Cd0DJ1AMbmXQLjnWSnmcJsfZpeiamUoiXp0AMtHR'
        b'JM4a6ZbvbDOZ5egCJbNyCacStCttpJGWuRMoJRPHc0pih9DlFUD/DrTTSH+zr5RPS8Cio+jUwOfuR8DX8KlxHC0avNXf/Llk6lCJcOV6FadOCsKc60pntYARrec7s4n4'
        b'nDv3vcNELL3v6q7yZJgUOT+enYjap9MaUOM2dAi0VFw9WAY/cOS7sROD1E05JCqWVHwBLDBKqNkf6MHBiuOMI4NPov3ryGpmF96C7qI21F5KbtrwXXwa7yfLmTZ014dQ'
        b'/ibqcpu1toDTsT1BUlwuwa1BICctYfImKak3O/waOkpyPgAWhrtK8B0i2TN8tJ3NQJuUtUtGfcNTi1iG2SE/c2z/vR1oktcP/yq7+NXcT11kBb9b61z+0LErcMvOhVda'
        b'fuYSMe/KjEfBw9Z0lR25u7n4N/+1/MDuTKc74T/6sH7Dt3/7qLV8Q/jw/Ja5zk3eXtpf1s1pD27Zl3Peucv9gz9dGzH9D7tyZ2X0u3/0yy9dBQu8cxd/suXz09UVRZ9+'
        b'5re0OuuTKaX8n5UmaJedGtXeeOXs0r+gFN+PZ4Qc+uzYwXvLI+vu/PfYH48ovnKq84sleRu+WLngL5cCfp364a9q7n+9dvNP3urwLN37u09m/kMuU2/675Lk34xl1330'
        b'qzs//uYP907qcv56vPun6rHfzvnH1gVbQgTdoave3sb+j+5XOezdiX9ewfyxeH3Prl/++IOSgL99++Qg6p35w3Unv/pbzMWgmKDLErV40Zkfbpb6UX1+dBCdUZl9erLg'
        b'rovTQ8hAJ7hlRVfSTE4Ngc+gq2M4NQR815ue7ZL16zF8VzZgWTl6BeMWz3dEJ2LpYsUBXcYXyBrLCd3k1Cqc8V7umH8r0qAWGef4K8RJgLaw+PV5S+mJ50x0eSk4SOOc'
        b'oyGNG/WPhh8UcOehb6LNE02eHke7GRdOMfhNSm1W2SwZaCjkJUxDXTzGiayB0GYn3E0/GoQvDFe74hsr0CFQwNsJ/kB3oLM0LhBrSDPbuTxtZCl4E90GastX8QVaigJ8'
        b'ZA1EOcYJSVQLWQFNUtGX0HXcEQcx/vgO5LidIU34zAhOY+JQZYGF2zHqc4x0lU5+5nh0l/MRdwh1Eindg2kg76KzDD6K30Jb6PKvCV/aqEa7UMucCqCmlcHXi8O5ly7W'
        b'VJJ3nPA5B/LSOYb0mLNoG8fTK/jNVDJiuC1F78BI8DZDKkeTSONScSv46FyBW6AmWKRh8K5Z+B7nce7gQj6JKsH3yLfQmwzekYy76IKwsRCd5JaysbibVIjVUhbtwXvI'
        b'0uUFtpFh6QLzzYAVrJoI2Gu8rY0JySO60IvlcQu9+uF0oWeQJHX5dIV3+RgkI2CRF9Q6sVci62jskaS25jz2Depngr1TNCRZatfKHsl4nWR8b3RcV1ZvlLQrrZ/PhqST'
        b'lU1I+i/Tx9+O7FberX1Hflfez2f8gx6LgmHFR9aFkcPPjT45uqO0c253tC5+kj4ywxCZoXHqlUQeX3tk7eH17es1AvJJ44rTqTtKL5lokEzUBUz8yhEy6HdihkVoS3v8'
        b'pTp/6cd+Ab3+4aY7wDdcrYsaoRPBbyATgV6SZpCk6QLSegND2gO11T2B8brA+KETVPUEynSBMnsJSGmC4h/7B7bN1kWk6/zhZ0Rh5PuPtPfCY3tfgfe1w3v8Y3X+sb3i'
        b'mEdiWY9Y1pGpFycbxMk6v+TvKkF0j3+Mzj/GXoLPh0laa3tTR10f20X+PRR8z/kh+debOrELQN/CM6wQ0sAN12TWYhEt5Hw9uVkutVSu/MGmQkLG5F+aW0dHwjp6cFt8'
        b'F5bQKsbsW3ojWUNLYZU8dPCdLp9Nlnt0P+8K+DoR2aA/9AnKi/MUfa7lU8qmT89STMnLKuHAEM2oEH2uyytq643ulVQn4XDJZcCtEHf4ZPaGpToBAfV+9Z41egQFk4Aj'
        b'HrrnQBkmDfo/oDYC+2jPURRRlcLJlJVf/VPgd2uVDfqhByMO1ZZ08btTH1bqfPPJjwMWDNamdTl0l70X3TtMPOiy31Eg9uhnSNBS0O/Gd5cB0Jr9wGWCeyVps/+LcBLP'
        b'CF0Hp4lf8VmxDLzIyVoKHvuHDADWTQDAukkUsG4SBaybxAHWwYlqr1eCziuh128ySROUCWmCwBUdhC35NiiKIwCTcCR0uJHQ30ZSQEJLZLws+FAO/VAO/VAOOwhyEJD6'
        b'/ClSnz/ttiSkwHeWEHyABygGPEAx4AGKx1AIPkt4PcAkDABMwgDAJAyY2JLb7+TpPqKfeWYQxgSGa5x0AYnkpx2jHXNi7Omx3F1LHgCN2EcWsQcvYgE0wrrDZDI4cGIy'
        b'2ClsP7+ZdQ/pZ/5Phio+4+HfMlMTqXMP1buHGtxD+3liwGx5VvAVeUliTprO5VCqc4/Qu0cY3CP6eWPdYSC2H8LLkXZTcQgrYSCxtIejNjMIgwjv47baWSYoR1A7CZ+y'
        b'WqC6Gf/+aR0Zkw76geHuALDKHD6AqnCAKu0CI6QKdw3AKs7kH1wDwArAq3DPB669lN5KH6UvvfZT+puvhylF5DqAXgcqg5RiZXC76xxBlUOLsJpVhmyxsaYEOJY2xzZW'
        b'6drm1ubU5gP/OkPPkpH8ohlsy5n8U8YbT235yshBcCCOPKbKQRm1hVFGdw63gURx4vJvc23jVfNI7r7kf682n1ruzod81afNuc2lWqCM6Yy1890EAJSBL7c4t7i3+LT4'
        b'VTsp4wZR4ExBUoQUksC7WqiUbXECHMZV7BxX6hpM3ucDA+oUVZWytpFiBFVXqZ6mWO0vDE4QRnc8rRI9lTep6tNr1Q3p6kYl/ZuSlJSSkg57Humr1Mp0mL7kSUnJ5P9U'
        b'eVKqlN8nUBRPL+oT5Obl5PYJyqbnTD3P9vEys0joDJ8sL1YUzj4vUIHY3udA9xj7nOlOj6qWXDpU11XUqF/ms8nwWYEqASY+OQSJfJh58xQlHLjcS+Y1Rupgk5dqDM2w'
        b'JHNGxtPJixsbl6cnJjY3N8vVtasSYPdHBS7mEiqNrqzklQ3LEpVViTYUyisXy5NS5OR7Ut5A/ud5FLtFVUd9zPU5FxZPySgsn5w35elwIHrK5DxKIfk7tWI1TI3T4WBW'
        b'3UgylSeNICERPyCz86xqDgfolwq0upXkKXIKs8onZ5ROyX3BrJKlfI4uc5GfjrJ5cYqqQa2eTHerrPMobKgpUtfQnJIhJ95AToTADMjL04YfT4OGLtRTf7vMk7pa5QLN'
        b'TZVpJ+8xqmx4apPJGJpJqioL4ob+ePJT2UuUtM9RWVVd0VTXSNlP6/L/mCuDQRbg9v1UcNtIry/FZ0umuK40W7/hW6tqG7LyeNSBhXf4zwccWJC54yHv6c9nZnz8/7H3'
        b'HnBRHmvD9zbqAoL0viBtgaWDVOm9d0WQ3hRFWLD3SlFEREVFXRAVEQUFFUWFzMREc/Iku5z7RFJMSE56ThI8MTmm6Tsz9y5FIeU5efI+3/udhN+Ad5l7yjXXzFwz879m'
        b'AVi8pZhdWV5dhVoE7UlyuqpxkN2cxrJYx2foGTdW/06WQDxb5q1ylm/4yU0lCqzm/xlEgXMK9OBdNMMIvn1iGI+byWcYpJYSN40+oCyrpEMM2U6iGegDTMIawM5piFua'
        b'IuUJsoDKn0EWeH+bwgwrc5E0s690XeGU9bl8UjH0hhXc0fzCelxy9cqV5ZXY1I/br5TbKvR+/kEB7xllwLMJCeX/8mNYmfzqE148G1thKd79smq+g4ftb4iS1k88m+CI'
        b'X39Yqofww/a8X/vO7DqSZxOZ8rvecP6FN36rusNRPJvo2ZY+pcs39DoHjVMsKMyrKq+U3Zl10RSPCejXnhWblZWl5ZWlVWtpf6Y2tnikYYsShMcatjOvhtniEQh+Bo8H'
        b'bPHSpy3uyG35DpMbtDwcXBycvKWPzBzN5F4uJ/KoNNbJyx7kMh31bBmjYbfSrM0ArKXLx1pImLWzFg/ZPuA9ncdJGtnMeFkpT3PWNE3SY+mE0e31WQwsRq5ObOebYbce'
        b'/g/dq8ZL7ng1mqwCkq2EhblVWKBQptY+S+XFm9lmgXrilUQUz+rcSunOQ/yqlDpKSoeXXFiI81pdVsjLrUJjx7zqqpmTFRyYEhoen7QoOyE1KSE+OTQ7OD4kNJmkcmLX'
        b'HwGMzrB1UFpItBKiyychMDJORpOW1ZvMKiVdA515k9zkuihZa6djmFy2tH1Gp9jOus2Q1NBKup0KSSE+866XLZ072SOlK2YmjtI8XTTqppdS8cbCFbzQ1KRZ1ndX8JJX'
        b'l1atK6wsIxVX9QuJpxXiLG0JNZjIqtyyteTF2TWc7ewyKwUB0xUyyQfGki+tkglWML3VYpYcVdG7Jqc4PJ727jSO9Kxai8T03No3Kh7p0FAoE99n4p25TshEaGpLiQwK'
        b'jOPlFZaVryjGMf3KGrHSDKM79TjikAwv/66CB2Af3BUNG2Ajm8GCp5g24eAoGfxxSuDZiY2Si510WWpgu4DeJklWNZqi4DGhKrwA9kuducELARHVeP+5IjyhgE0E+DQe'
        b'+r8P1HLw0UpVuIMF65UryDOwFXSD85OnU9GIaAlomwvb2WAPuOVQ7YoT2CcPDidPUDLWmj3r9mzSeRjYC68pKzmXypZw22EnvIy+fNmHXunEy5ywDhwhOUuAF9FVcMGb'
        b'rI/i1dEisKs6HqfqHOyxnHSXNwUpIwVcrHCJSl2pqpqEfd7ZCOJSbWxgHdzjCOvssYcy2n2bAC85HdZkhqwPIwu8q+Cl+cJVYAvslvlbg/vAObCbLNSLBDRCyMnq7fn2'
        b'1sqMam+c/BNxAVNdsEU4RMXCWpRlxyRYE5MY4Q6vs5NALcbfwOvg9FpLBhjicGGLRVppxcoLbOFbKI77IHp5wi1l4KR++8X+0qa0hATxJw9VNzAOswOvXa1Sz+LsFuoq'
        b'aLTeeNy0hKu010397kc/3vvXR7knE7iK9RZvprE2nB76XkXMjN9/as/cNoWoe40r3O36X+Y0+nF+fiDi/XX49OBxTrr7x3VzrR9+oftCl8XY56M+zYYxr7VvrczSZVd7'
        b'f3ibs9TF8WGaYP7jXTrpgWqub7w274LZ6ijmk+vFnWdK7n0VNLjplZ9efLzt1Zf3XK24tJivcfUnoYKh3pbvYy9u2/aNz+aPd0R//PGmi0WJ737gX/rJg+V9T5m7FTyS'
        b'xNv4qmRZLRxcBCI7BwHZPAnrFoMOllO8Or2VtF4rjHaridFB9qB24VqwT4GhlsR2jgTbyDIoGAQiUCddlAQieEK2n7Msl0QBLoNd/IndqJeQxEwcQDcFXY/wLodycBoe'
        b'iY7fHCk9f25ZRVY7LeHOlAm53m2M/fXgU9fRC8nibVkkPM+NB3XPe9iyX0CfUt8Dh8CNyWVIeLE6Qur9CLbAnkcW+JlaOIjxVlOcKWFPSo5uE76UQixIZDxwEB6zgyK4'
        b'73m3V7dhC71avNsVHoP1uUoxU/xywetc+qjykIYPqA/yJw25H92NZYaBraCedkclAsfhNaQ71OCWGFQGeUxneHMNX+XfWiHANsOpB1emOOWYcUo31VdPPJNG0xXYMTR0'
        b'xDo2nRYSdUdK3fG+uueIuueA7rDFXXlxQuqoV8hw0d2Sh2ymxkK8pRSF43QozzAwaTVslB/VNxV5iPX5jXKjpvNmPHiqqTvl1JauuahMrOuCfh6Y2LQsHfX0vak6gP4f'
        b'XjW8apzNtI0n21cTyPbVBLJ9NYE5pmsoNnUU6+IffFCSwbQlG15RqmzDyfMR5PkI8nwEc8yQN85gabuM2ghaOK2qo/bOLRxKjz+mqYcPo0UwW8LuGwlGjASdhRIjN8rI'
        b'jb46pqXXGDKqbdScKTIXOYvMKW3LTq1ufbG2C/oZmH/TB/16xkHROJuh40o/gH6mTL1Vp5x/+uVZ7Kw7YlUZz5xO+o21G4sn7J2M6UeR0m3/9zpYId48Til5Ma6rBSr8'
        b'HgcrUl8ictl4RjObr4SZikrmMWEvKqrKs/hR4jHB4TdMm551fYJttskRgUlvcUJCg1Le4gQnhYbwFWY6+Fb5o8yH/VsK+SW5lcWFwspi9jPkxDmyDItQcFBxVnIi5iYq'
        b'1KjVyBMrxhxCSFSv0Sia8yfyEXfwWe93zmTFCCwoQEPrqSdsZKO4GczmE+P/540hRTxvPDvxzpkgMefMsBnSXjqannCegI/4PH8iCn19aoLy0Wg9D82KyqurJudIVbhW'
        b'qqQzyN80N5fOqmih+Q3T89zlk+9OTQ59nZcr5BWVlediuxuaX5WiKyuql+cVzjyVwZ9bMWENwgNj2a7rQBLbTBso6VRMm7NOTYZsxlpVuIaekOFSoR1ILKePJ81y3gg9'
        b'U1qAZxOTRVFZSA6coZTReeDZoIRWkqyR2YJ5UpiDg4M5f5Z5Dr2flJydy8XSJKyqrM6vqkaxT8bswAuTbceecn/G+CbeIZJZvbKsUCYC0r3uaGKFM4vmfstRUc4Yh01S'
        b'aFgo3ooQmh2XGhsUmmTPk02LU0IXpvBnLe9CclgOF3bhigJBVbkA/ZpSPjblK+nDg78Qw5qZLA3oamElPnQ41dLwi9Hh/yYMEbiEf8lOMOHQQyrVM8ZWUl5WgFTqjCYF'
        b'HiqV0KS4wJjnzQczn6/7jSaFgurCbHzWji4K9C8e/hcRWKnc4HZRVViM5AIJSE5OXPkKrCl+4eDhmqrJr+PIcCxoBokP+2EFMSG6RZXly1FRFeTOckKwrJq23BaXripc'
        b'IZN81DQL8L5om/zyFcJSVFw4JlRwpeQqKuVZE0ZHM9XexZ+aTTqp5XlLC/OraH0w8ww7Od7Tw8mZCDeqHJIfnAZ7qYssaX6JAQq3TaQUZ4ynqLqStDXS2smhx9nNDHQP'
        b'581Llk7rhbzVJaX5JeQM5Vr0lbIy1PhyK+nJPf3wzLpFKCzPLyWVMGFkWFlZjhoyOa2CilZa2agh0GI/c2FOajkHXlw5UrUrV5aV5pMTG9jeQ9rT1DOhM7edYFpn5EqV'
        b'Ivo67vx5Nijk2/PwEIBnE5+axMeVgYcCPJug0LhZ2qHtlEOuHnzb33D0dmL7e+CEqsfpTplM9i8dq/lVW4eplGV8e24emqiAW1NhxhVkXEum4bszFBiZC/Twfnn7GnVT'
        b'BrET6DnDGqGqKhD5ywwcQfBkGL3Tu79Engb5uiiT7eOgPpxeMhvMgsel9F95W4wXPrRZkEI7Ij8J2uK5q1QXgyPTTCO0XQQ0ZFfHoqc2gaNZaO5P+zxXXKW6MsWGZhFF'
        b'C2zTIkBXmX1U6gwe4OOmeifvCdVA0992cIskaQ7Ynkl2fGfBPVJTiGJ2dRpO7IVUldm/NeOH8L5tZ9hj5xCJnku0maCb8uUZ3k5asFcf7iMfzQLHQBNXtXIZqJXaWEpB'
        b'VzV28eADTylGE+6zICoeW1lswKUKEo8cbII7lS31wTnlSeNGANwKW9GN9rlgJ+hIAaKCRFAbhEoJbAPn0f+n0O9dy9aARnAmKG8JqAuqLE1MXLqk0jITHFlWos6ADX5G'
        b'oHUdaCNykAM6Qrnw6ko9LRUWgwVvMh3hcXCxOgndSoG3Qev0hE1JFazVB7UBrBywPw/snJagnbAdNuO/8Rb5nDlwN48BuhM19Epd6Z3wB1dpclcpwUYXIYeB9+jzvKpz'
        b'8PUb7qETliZ+mhTwvLK6OgU2rlSdA5tSpCU+xQiFLU+4WqT81xL7CQQympN3KpKDAGqwRgdekPeoDsQidyAF7vxF+LYi6IO30Isp06oSXgG7VcODQF91KE7qUXN4MzqO'
        b'xjCTswF7QXeC4ip4JA6JDIo5mhBpkRwdkBNGgbq5SK7r4IEkJIN1TDhUoRoORBnV0SimpKXzcTy24OS0qCImTBgxadOiAzu5oFnLEp7RBmfBaR1tNgMcidUAp8G54Grs'
        b'gMgKngXdM2CzWbANNqP09oOT4JQvqpttcAcqX3JUATTlMeDuJJUkdyfS4FzSYD1dEZs0idEvJpIfJXBIgzXPFZYsWarTmwoqr+PVc8F+P3CuOh2XVx/cZinji6L4JsyJ'
        b'vylmeMxzeuRJUVoo1edpAC7Y5oh3hcPLoDNLZkzcuIpsOaXtqh1pyXYYjb0HHnB1cgI7cqIZ5jbgGrjCBrfNnfisuJTSC+ltLOHbaFJZ9XbNzpTBOOikVd26+oDbRguB'
        b'oIYpnxP0QfqNS1pm3I405aQMb14xo/aFf9S4Jx96YnEt9oMXa9/OqGv+0fuTxz+8NfTEFNSotvylW2Ve/07H7PMLHgvGFepHdr6452RWDP9C849f1Ntw6lOVttle6dcx'
        b'eD0k5OeXNJccsXnVa+6dLe2mn5yJkv/8amZuu8u1t7iSzh+2zY/qnusnaW+0fXHhVxV5x/LydJ7aXuItTdj5wTsHSl6NVNXPln/v0OJy4/0XOt+ojZXI39Hs6nlp2dAb'
        b'59T+cdf2wpwc9b9t5qtfW3s1+dNBOaPs4YrF1U9scx70CzO+2WeqsfWO3cIVGfYPdOrDf/roSWa+c9/9V/eYcBo23ZF0GvV7tu5MzlD1C4681lWy6Q2bE1vvC26dXJ3S'
        b'8/bOH/7yg0XAO3Z/dz6Tsd29sbfSt33o1JqoK967+oNzNeVu/KySGf/jub/Ymez7x0aLz5IPn/d44Z9zUhosfzg/uCh3YNtT9beOcPbGV70V3BRqlRfb7eLobB5zpvbS'
        b'7Yv/1Gvd8bihg61vIhy7Y3DZ5AvXkwZHlLSL9KNjPk4ULvjw+tm/HZ9PPYB7vEcMK+V6Cu+GlfKgRvmRGqU61B4X8D9kffy3d2Jff+f8nQdhQyeMrNZ8lbbQtWDoCdt0'
        b'wZmP9m3g69BnRfa5o6aLNQi4DA9K3Ydjc+RicJY2le60Bvue8QmPGs857BR+rwPB3MFGuZToeEEGPC/jbBbSfiWOgVpQP3kQhcHN0AV1mHQsyiEnGDauZ+FjKC65U+yK'
        b'+0EjsUzODV8H6lerqSpXwiuoI61SlWdoVcBd8BQ7Gen+Hjrxh+LyCDFzApcJj6ax4Gn0/236wMZ+sHPNM0RPJ1VsTDWEh2gz7/VNoMcubvLEfu1SbOSFZ8BtYsL0zgCH'
        b'8ZGWle4Rcgz6SAu4FkBbNzuSVtqlgwHUjCNBN4chX8YyX2hAjl+UFoDr0bAuBgzBSzRidC24TIy/EWsDZabb1SGyMyTskMwkYrddqRdC7sIueG6q4XbCbOsEbhLUAA92'
        b'gVPR0r6BpiDOgz1s7Y2JpGDTE/HSTIM96NIF5zgMjj0T3KiAg3StbF8Juu2mm3s3gm4eZ4lbOm3S3QpPe9iZgWap6RzbzVGCdtGQyIZS2BYdEwlqJwiIppjhTZ8icQID'
        b'8o7wrICk0RGK4CCRnAh7xYKoeDTwUAth+3mhdJCjLYPwpJ+dCuiYYCIwYbdHBV20ezfHgHoUsWOsgI+S4MfiwSZlvu7/jR3pOK2y0eTsoCTzGSxuMxELP5F6iy8S0N7i'
        b'rTqtJLrOlK4zNjD7jBrPa0kThXWGdMdKmX5hY7PYl3kWHSoUz1mKJeS5N6qOmtlMcWDeqDZmYUNZuN238Byx8BwwlliEUxbhYnWzUU39Zv9Od7FLsNg2RKyJf8bMrRuj'
        b'G6NHtc1FBSPatmJt285Nw1ojjqFix9Axcyt8b1yeYeHcGzcyLwg9Z2B20vGoo8TAjjKwExtE9Mr3zxl2H3GKaFQY503zfE77PUdZs/LANm/uQzbTKoQ4TCcwNRRiml8o'
        b'k6aceYnkRzStxJpWo4bm42RrudTuHUjM3UHE3B1EzN1BzDHDefhdp9F51me9273bfDt8WxQfj00/sUKiSZdFk0aiSSfRpJNo0pljuibo8UkO4iQOEtMc+XiHvMGUGHVN'
        b'cIxhshhDSYyE1kbIhUz9MCZGsvngpCXRkMIEiUkiZZIo1kuk1wRSxfZ+YosFYk38gzfGGzVvFOs69aZj1t6Ie6zYPXaMJ+jVGuG5i3nuAxaUdzT6LU5YjEIC30uVmKdR'
        b'5mlio7QxfCaoU06sK0A/vXbDWlRg0ohLktgliXx5Cl4Sp1tRI5gpWk//7t14V21kfpp4ftqoLLlxdHJjJCaxlEmsWC921GheazzOLnpcoV+F/kua8SCS8WCS8WCS8WDm'
        b'mBGvNYYycpK+ktKfSbmH/epb48q46n3ua/JHNPmdlhJNJ0rTCWP8zEdNrTC9b8zUrDHiI20DsaGgs0qi7UZpu93XDhnRDhlOv1skTssSZ+ePhiaIkzLEmQVIvnSKcPQo'
        b'bGShwkVRsJq5uOClXxDb+kg0fSlNX3zYyBk1mXE2/m3v1B05oDNi7y+29x81NW8RitxkUiUxdaJMnRqDmiMI2s+iU0Ws6YZ+Rm1cG0MoLctRUqsxYk0n9DNqYdcY0hw7'
        b'pqvfqDRlZWTurGS4SQN55dLnDzb9Fv2EVwmeB7r9PtXUiJdPXmJMXz7Jsmcyk8iyx58V/qGLK51KCxi31QJVpi+uyMtMAFtQcFCe7K+ld8Yr1CjWMIrkJ3baPssq+R9x'
        b'GvZDznMWi6TCFQWFlcJfWzogdkqpbQRbxnKFvIWxMb9iADFhPG8AsYsjbnQswKV10ZNopESZlxSZh5T6dOmUIwbNkmomWUmwFVxQ1UbTuf3EhuEGa8DFZ+cXsBvuNScT'
        b'DJ41fSj/NBobHMWzFA7s8ZRteWjJJXwt0A364X58s8oBDdkcVqEgCnOIwJlSiyVy8yvALmJBgAPgoCb+CGcjPMJgmjBAY0AJvXHlOhqSnIEHpLtW4FVwlexcKdMltpx8'
        b'VeLRJGerXE5Zm8FcqVemJjk+8ZGEp2c5THiCAYZAY3A1bmPgZqk8PMCOKiBOjUJ16P0tB8AZV65SJXt5CoMJz2HefC04Re+MgTVz7fi2aDy5EfZw1jLh1hJ4jnylCl4D'
        b'O6Ojl6Kh9h5+nBxDXoelshzsJG8tA0M6yXAvh5EK9zHAFTQ094LNdNqOgEY/4tWEzfDSpp2amIHdxHzgl7+CPsaPZoeHsBnF1IS84w1b0ie4ALlLCBZgI7xAkp6Qz5zg'
        b'CSyBWzBPYDFoJ9G5gP3FeGsOh1FQyEYqO1L6StBG0C6jAsyH57CNaBMcJG5BHCOdk8FeeBYVdnMq3AsPYi8pivFMNLneFUsKPKe4gWHEZJRs98pxqHdPoi1qpkrzGCHo'
        b'3lxmDqtA35C+2GdPXA55fr4sR/kb+9XT98YryKQ3Brdd5mFGMWMDI8t0I7OWJWLM9N8GZgGjgLmTpT9x5QyK7/xEnPtZe3hkSZUV91kYAx+KeEshsKAypnRFIZ9diQfL'
        b'b3HK0D9oRYuBRxNbyHFLWieYQbNWkuY76UbXt6xUWJVfvnzlgizU6L4RMMj4T+xYRP/c1eplXlO6rDRgMSAcZg0Ib/IlTiGUU8jEA6QXIWXTlaXCQI0nQicjJ+ZvNj70'
        b'xcdaOgx7BkP9klmO0Q82EfQZLNDmsXS6mxzYBC4QVznseG8kVLhAjOFuWItNXSoszLsYJMYuVMmXiTC6w9YwdLMCNRV4uJitxfSB5/TIF88Vy+MNSbwK65yYIi0P7J8X'
        b'Gzzhvk2WUkFszMdyGAgbyQ1mDDxHIyhQ+xBhA1ecLy3V3ShVHbAPvaXAyAOH2VZMP7DFhM8kr1mbwEFhHJqNgnMGDBaXycuGtX+KNODzD5W1uC+uw6dRaDmo3MOW9bf/'
        b'rhhcmCoGrqX0z92U3sBrkZcjBwqGXYeDhl1vlkrcIii3iIkH6AN2uCW6gm4d7ip4dQ6LAc+YovL0hCfBNtJ4M9fAK9xKNgOc1EIaAqkNF09aHx4SYhCgCryqAHbAG0hd'
        b'HcA6+TA8T2gsK8FxZy7DEmkdRiIjEc08j5D6sYSnHbk2tnZl8CS8FIOadBQroxjUEgUeojsX9jnCZqcoeA3dkgPbmfCQArhRGvPj13LCp0i7vvqp062Fi8rfDlNfkjSX'
        b'n6hgmV2X93K4mk/p8Q6vdafDR96I/dr1luG/3nlJVbVlm9bjtoW3tfgZ2mvvRovTmXIcrc+jt/507MmOJ7UNWsI7Wf/V2PwgZcv77/9jw3vzBz98TW3t6z9c/87QdVHx'
        b'1eSv9fd8+/7XL/R8+W6TR/47CeGb3byr45dUx+76aeBcHusQ64DEqbTqssFLWruGRGMuNg5nP9iQ3GKpUzCgfeeryzzu/UX6qeqLNqvv5/ptuVfh05ujfXbNkr/ckf/a'
        b'LWRxW7jx0ytWe97wfpFq3rDc7b1tdR+tCm4o7Vq7f46yT7HPlRUm+azNzG/+NdZjCvVTVZSP/yA/+EXZRbmGlTfiXLITtA7ZPEmQ/8uNVNNQ5g23Cg/L3PqRxr/o7Fxx'
        b'pKVw5/hgS7bnEu10dohq8Mpi+xXKqd3r/9r2wGXtpdLxpjqtsNrvq4dfF3kXLpwf/XpUXlFijNwbxUYHlvmwToxeNd647efNWwrV8vWXdgd338x+54HJV1ab5Zx217zZ'
        b'0H7+7Y/f7T7v9MVbCz1C967X+zKb85V88KYx/9bOz6Jidd3OpsR+2RBa8df1ny8TufjXep9s+KvexfflEjIU/Xrbr3y1X+kTa0lFhl9n8sZF57cs18jX7F5eF/OF2x7H'
        b'tr83XDN664G2/bbXXyyUlBk1M1186tqGN6t8e//W39u+PM7zPOV8vu2jp6qty/TO5jxZKydMyktjCm2d5+i/rn/y53sdXd+2vDav7rVTtd4uJlUf51XLb/iidsPZeRuq'
        b'j84ZeM2i8l71G0J96mL20vkqGJsS2Kp6QfVnzpZ1fzvsfl5h/RXHH5l3P3J2O5zxL6P3/U+2/Cjnu7pg9fwtX5u/8C/PF9o/ecrZ/8mBFtMbu6KdvtPauvboXbkjhuXj'
        b'8JHfG99VL35/QCvj1awLdtuuHAr415GQrFpJiy7z539skvhsr/vZqM7qK/+T+y60V/zL577Jo8PFW75fa/7ewwN3DdIyNeM6dp6ZVzn+NOKv2wzWHkmwB6kaptxXwNbb'
        b'dtfWunaq/LAq8eHFsf0bKuJv6e29rnZ7WLXLx2H3U4nG6cHzdS5vpt4KeJxt8ZNj7qaEd4e/kX/xL5wPlpbA6wv80x4cMvvg4Pi6AetsyzUFzVe/Er/56KNBltO7ul6j'
        b'Dzafe3D7qcLfBH7dCz4LeCAecVj2ZuKccUfrRyFPw8+2X7zyfnZqleOBZT/1/lOS/pN70EfVr855nTJs+/JW7bqPvMY/qcv48dsfRtw+PLItTS9nY/1w2s1rwevXfPKu'
        b'2cdbvktIrCqT617z9SuL7tX9o5z59fodJpt2+X0adE/Ivh+5fkVHoLUv82vNvra08o7wKlFUzCtqKS90fBrw8PGH6I/T+I+fV4uU32P6JGw4fk/t0adf3tw2Wq6wTvUv'
        b'hSNqKfcsUhUMvtmzUT3jiZf4x8a7875fe8hX6RXTyFuB337fIg7+okrreK+jf+DDFV8s2LMxqmRT2GN/65/uW987blqfpXv48Yq1mT8+8WT/dKzkw9odq3c7OjWv/HtC'
        b'uzf149zQtL83/hfzq/Mpnt92cdItN7y6peG7177L+uQ1fuKnm/ZWCA1Thl4IG34q+LxnvVE6+8XVeqwfPjsy0NPg/N4n3Q/Llztnf1zm9oO88+DTj+tf/nTvnHdV2t21'
        b'268GrT/8vd/+na889km99t3t1PJQMd8tTCf74PGvDKrara03CrfPf6+p/fuNJe71dU+LSj77+osnLg373tx8ZOBn9fv/VZrv/Mlu54Vveu2//6+dd1f72Vt/63XrJeXF'
        b'T1mh3yzm6IXxlz0yR3py04pUri0aTsPrmsQpicwKaQr60MgXnIVdxFQGaw1jaCNkKzw/BR26P42Y7IQZKIppFjvYpoL3aPqC7cSqqGmxLBruNfGKnnhgjhO7eDFoJDbO'
        b'DYvlsFURiJZMBdewQ2D7JmJ1tIbNclKjpCfYOYPVEZzVJBFpmYN+/CB2qCJwiIhBA1j1RJ0YjmpEFG3SO8QItHPIr5rqbQjUR5J3XQXBQrxGdlM2w2AyVOEQOwDsN3iE'
        b'2Rhgd66z0IEBRejDgso4vhKabfSR3bkQdcZu8Lx8MmgDh4h5sILpiIf27TG0WVk+m2VbCfoJ12dTLDwbHWMrj2YY9QxWFnN+NRyivfVcAL3wph2KDOxxRNManLx9LEt3'
        b'cJKUYCaqjTPR9jYRblZTXLJcBzSCaHGuBRfWCOClJWjQtCeazVCA/az4Uk1iIVdjZ6Cb4HoKuo9uwj7UIaqCGjSegrugiCb87AIdRgTUy2Y4gEbixU67iE5XMzgJ9tOx'
        b'rwGdgkj0bWVW+mLYRkfuB/cJY+BFNBBvWEn4SfviFBjqoJddJQ8b6FLvVEuOjgKNNpjdymDIwVssNrjuQjs52g8GXWBfNOhZBC/Hc8E5G3mGErzGAqfB0aW0x6qWVWVC'
        b'Bx0+H9YpoZqRYyjDBhasX2FDJM8FnnRFactQEyjxYS/Juiq4ydYEF+Ep8nE2aNKXIp/gNUPaQF4JzhMTPrgYg+ZhffAEvIImjg58ZRtbbI2eq8eGW0DLelIykdX+XIdo'
        b'eDUF7OPDepR3NdbihCWP8OAqTXG1MI7JcPYlY5nOKg3CLwJbsJfUvmR4DuUWF7gd9jglx9DQYYMj8BLYRvIdEwnPRMfZg1pH2kun4mYkq4ZgGweciYimy/0GvOkgdFgG'
        b'OyJBjwp6CpW1PNsf7GPQaUfN0IEbJYipABcikEgKkfxs4zMZ+imccNAWT2QNdFWwhehapA4D3kaTTrgdHCRlugINa09H84PTpO4v5VB7a2b7rl5IWkIxbHSzc1ixSeY+'
        b'Seo7CQzCG7Tx+5iRojDSlo/Gdwc92KCZCfaWgxqyrpBkoIrKs14OlQLczeSiiak8pBcEYHNoRnQMuJIdN92n5PVyeg/3jbXJtE8l9O52eJT4VLIEHTTxqwceVscNqgns'
        b'cpzqVslMicS9GeyH27g2CraoHCpiULqU4VEWGFwOt5P0ylWDo9gZlP28WAGToeTMAi2w3ZheSjigXMZ14NvqrkM1hZKtWMoqRSruKvlsVTU8ZQdrDMBWR4dI2g3jHLCX'
        b'nZcHO8nLauBCNNcGHIf7HCri8BjzLBONdHcmkjStXG7G5YMmMIBaBCkROdjChFfCkOhhsSyJggfJAgiSt4WGZP0D1Wg/XRb7wB7QLXQg2bRKYcNa7DjyqtsjqW/OAdgY'
        b'HYPqcg9ZjJVncKNY8GwuHKRRZf2gAbXISCbot+VXxsQ5oLbuyFYMXUW38+3whCNRAEh1bGfAAdQGmLTvdtChHIlmYpV4k7yRKgvcZhquySQvrbFbK4OxFcMuehnMYiM5'
        b'QWCsBprIJGiVL5kDCRh0ZW9BkhPtAC4ayFb+6TU7B3pZDWw3yRdGqoAOnEJHJkM5gAXOLfUkLGsv2Ar6hNidGdaudtiOg5MbDQe0kGqEhxcgPYqnkLA+tlwIG/jK4KI9'
        b'vIo19mVQA3rRo/rqHNsl86RtCJxcgOLZu8oc3cfzgDQmrEM9xAk6Hd3gKha6uhh5uMWMdlh6E7TRaucCvAIGhCjWrbCtahXs4zA4GswloXayUj4KevC6vTyaNLYzmOAE'
        b'rrZbwaSOlFHzqsfTj1ob1Eba4W42PIGeQA2Q1uVQZAK2osTbRBWCQ6ttWQwFcIDlVQZ20ecn6pTQdLce7oUN7vHYvlVLpGQOi10Aj8A+knIhaA+0s2HaCaa4MQVbC2js'
        b'difoCxGSDgrpU6wUVUAN0ot64DzHGZzMJEmwhW1CpDfhUJqAzJ3kwDEkvPFgJy1kx/A/Ufln5WPthUtOGV5BMjGPQYtRAzaj4J42Bk2JtzNYaUyBbxXpD7JcjYSoxpVg'
        b'7Wr0i8QND3M14QE2OMkNpx0ftqb5EK+oDGc34hQV75OhK+QmuJYG6h3tFk8uqx2ATWQRNxg2pXGrVZVYjDVr2WbMQHB9KS23u8rhcSHcI2DCS+kMlhZzHqyRpxdXd4Jm'
        b'HZwL0BGNRicV+BnUp59jWwYgASCLq/t1LGgP346gdqq72Nr5j/i4W4VnAfY4By6Cg9ipcl2sPT8yFiltqZNDT1950A67wQ5Spmxv2IUe9kLqCvtolq0nLi175ITu2sOh'
        b'zWSUMxA6g9/WSZ+tqfCioqMHoHtXMJgj5JqhiTB+UFBBlK4GaqFIH6DM0XmoUbBAX7UXTi5jqyWzY9H0uYPUFZoe3xDGrUvkS9taKAt0+avQHfO5ZeAKkhQUaRYab4FD'
        b'TNCgAi/K5P/YQmGcB2zjy9SIO1sJHJUOhvogUrl2z6Uf3Cqa8GR3AxUyyUODKrzFTQfHpJkg39OAV9mgIx49gkeh4GAcqLXDPeFxODiD39tWFq2t94PtACl63BdWhLHh'
        b'NSboROOdE/Raew/YBU9wYR0e5XTBHWQsoMhgJS6FrXS3tS0RdCJlH8VkOKmxYT9ukT0KtKScNzTF5aAcFYvlJRov9jdqgR1sWLM8mXSl8PYKcJ3Lx56MlzMNkGgpoM4F'
        b'504RdoItQhWwPw5eckQDCKK01ZeyQR3q3JpIMa9yyYJ99g4OLDyWOsiGR1DXBpuViFRvqgbHuagpBGQzWHymCWgAnWQUsRiVQ50wJhKVmBKdpT1Iyx3EzRg2crzX8kmW'
        b'CNKUK8gGR0i25E1YmuC6OVF9qhtQcdRjezjoVhLYYslGDfgQH9wmRelpjnoYR1ukHS7D+gg+VkE3WRFJqaTuTVavhn0C9L3mONp6spGJWvtV1HXR9bkBXn/GMWEh7NCB'
        b'uzhzCxNp4TkEe8EBoYO/IKqaj1QBGrSxWKB5/hyi4IzhNTiEy9kBdUf19pFzbLB+U4XX2V6gGdZKexAwABpRe5Ee2wInzPHJLXh7IamOhUgUWqIdYuXhfj0Gay3TNxMe'
        b'lIoIevMc6lljmGA37CBHusBxlGnawzGorSCoTnt/bK+nSZ3gmAtf739mfV7xVx8R4kQ/twk1YKrbQXnaVLdOf1YrHlm491aR0kA2ODH0DGWO2/CqfQzzgYGV2DpKYhBN'
        b'GUSLtaIx3tHwvr7jiL6j2ClQoh9E6Qc1yo/qGDQvu69jP6Jj35kq0XGldFwb2aN6Rq3c+3oOI3oOYkd/iV4ApRfQKDeqZyjWixRxOrj3eW4jPLfeVAnPh+L5oIvDocNK'
        b'+AETkUWHnVhPgP7Gi8Bi3ajOQrFD5ACH8owU86MaOWOmvEaVUVOrltWiVcQRmsqoFq8xRqTVYSrRcqa0nBuZY5o64wwFDetRA8MWs5aQ1mjpAbF8iZELZeTS60wZuUsM'
        b'PCgDj8bgUd68xsjGyDEDw5O2R21H9fTv69mO6NlK9OwpPfuHbJahDka96TQGj8szzCxEgR3y6GET83FGIkvD8CEJG8NG5/HP+rb7ti3oWNAYg5IjipFoOTXGPJhnJVp1'
        b'dkP7hrZNHZsk8zyoeR5Tb48aW903FowYCzpze0q6StC3TyofVRZ5dPhI9BwpPUd8QfGookj7yJzWOfgf3KNcUUhHlNjCq9dDbBEykC7RC6X0QkeNTFsUxHpBosCzke2R'
        b'nQW9mRKHQIlFEGURJL0VIr1V1LtB4hAssQihLELG9I3F+gGiNJEB+oU9twWMM9T0DYZzX14Klo6aWbSki4198ZG53qIRPl5VNjYZNnvZDtiN8iw6lDrTRniuYt6CAXkx'
        b'L2LYChVUMNMElRQKUUGZmIuNPUUpHYt6rUYsPcm7A7lDJTdKRnlmZzntnIlbYsvggTSxZezwKgkvjuLFoXj8cTT+JuPqKJbWRZ1WI8ZOYqP43txryy4vQwmwABbDq16w'
        b'f9Fe4hFPecSj6msJFxtld3IoG0/0eyBxKONGxl3m65xXOHdTqNgsScQSKmKJxC+b8st+aKgWzjR4xMDhuAlD3+Ck6lFV0SrR5l5tJO/W0UxZ8tI6su9b+o1Y+g0slVhG'
        b'UpaREl4UxYsaZ7OsQ5hjppatm++bzh8xnT+gLDENpkyDH8qx9VG8KBhXxNHKH5UfNTI+GXI0BImlEWXmIjFypYxcRyc2EigYm/QmXlt0edEoz0rMK+x06/al7Bagv4ad'
        b'X/YEnndDXo2hYrLFOfni3HwUUjEFkuBCKrhwDD9eQj8egP4aTnw5HaTfTXk1k4rNE+cXiQuKUEjFFktCS6jQEhJ7VKdzz/yu+b1u/b6Ua8hw8nDecDLlGimxi6LsonCO'
        b'5dvlRVUdGyhrHwnPl+L5jlrYipTFvKKJpRr8k5hKJWZRiYXob4ljEeVY9FBVwQNVFQoeyqng3KNg3ADnHgmxNPfTYveU8LwonheqYmNcxcYmpEXh2vPtZPbIdcl1FnQv'
        b'l9j4Uja+D5XkcIwoGFfBMSodVcIxxhyNQfUt5qWj51W7VJFMFF8uHii4WUYtiBcnJIqTUsQJKdSCVIlHGuWRJrFJp2zSkfCZLWGO2TniIvMZZzP5WcxOHTE/tjfwWvjl'
        b'8IGQmzGUb4zELZZyixXzS8SJSfcT00YS08Tpi6n0fCq9WJJYQiWWPB4NDHpZB+hIJQuJ1WIqYrEkMJMKzHyowME5QsFDtjxONwqQ+BqYtBiKNMexVHSa9dh02Ywam8kE'
        b'2jist6i3fFhObJR0NwxDf0OQ7FmI5qCU8YJ6Pfr9kUTZYYmyM3i4jOnliJQQCh4yvEx0H+GgMWx8FZNhaonUEFMbqyEUtrBoZ4yVreuO+Lf6d+aOGDqKDR1HPTz7lyL5'
        b'a4nrDO8MHxM4t8SNWtl0LO3V6FjeEj6mZ0IaQe7Z5e3LcRmHHw3HtabUrtRp3m0l4TlTPGd8QaVdpTOpO10sCB1QlfDCKF4YEa6ITpduT/RrgDkkf0N+oPLmGolnBOUZ'
        b'MVkmqAZNLMTGUZ0hnYro14AW5RUldo8aZygam6BKu5+QMZKQMWpm2aHfWTRi5obry3zAbMjuhh32WBvZqzNiMV9sETQQJraIGS5C0uNjjqTHxxxLj/lZxXbFUQvLsyHt'
        b'IeR0r0eYmI9+Uu66veol5i8RL1wiscimLLLRa2b4NTPymiXFc0JShFpgxuWMYebLHMAZTqFCUyUBaVRAmsQ9nXJPfzhHMRFrNByOz2UY84gWEyHN6UbrM40hgxsGuGSU'
        b'25VRC3PrcuvlUE4BErtAyi5QwguieEHoq95Y1L2xqBubnAw9Gip7waXbi7ILvevyqhcVnSVSlvCWULwlD9nKuNBQgBqSuZXIsFNTbCQQG4X3ml2zuWwz4HLTR+ISTrmE'
        b'jxqZIHUiNspDxc69wR0OfDkEhNydS0XmSEJyqZBciWce5ZmHnmqNxjudUC3Qi7HSihy1tBNld1aLLZJQQVvfsB42f9HuRUeJdxLlnSS2KBOnpd9PWzyStlicuYTKLKYy'
        b'l0nSyqi0sslCfMjmOOPadTYZV8YZCzsaJlOdSR2LKUt3Cc+D4nmM8sw7uBTPFek7VKfMIaUbSki3iC2KOyu711OOgegv1N2UgJK7la+up+JzxXmF4vxCFFLxRZKwYiqs'
        b'eAw/vpR+PBj9hZqfwisK4oQkKmExlVAgLiwRF5WgkEoolUQspSKWkvhjOyt6Vnet7q3sX0/ND7/Lvjv3LpuaHyNxjKUcY7G4hLWHoRrwQSpXYuFPWfiP2jiIULdaOrEq'
        b'iX9S06nUHCq1BP0tcS2lXEuRxvNC+UcB0ni4olRIRaH8Rx2NkuZ/Wuw+EgtfysJ3WrnJWgUqN9PWaDQQERsV0eKOiqIAFCCR8KGiCyRhhVRYocS7iPIuwvUYLzaKRXUo'
        b'f1m+t+Ja1eWqgaCb8ZL5MThXTrGUUyxuuhFHI0Z5DuMMrpl5r/M1j8seODEx7TGjNvweThdn1F7QE90VPerkfI1zmdObdkmlXwUlTeCAkiZwQBIq8LlvHzpiHzpcILGP'
        b'puyjxfZZpIGmjSQgdZgpSciiErKQaubbItXMt0UNm29L9PYKiY0fZeOHmoylFWoxllaowVjaiy3CUIpVL6sOFEucwiinsIfaXDdUDijAafQY12FYWZ9Nb0/vTJdYuiOh'
        b'eaiviksHBQ9XMyOZ1kj/4fAhCvUNH5FwnIT0lYcaWOuNF6FJocF9dd6IOk+kgcY5Ee0Ro1rah8ObwtHIL16iZU9p2eMLkU2RLctblh8pby2XaDlQWg6yiwWiTImJs0TL'
        b'hdJykV0rEm2QmLhKtNwoLTd8LaopCg/AOEc5LSmtmZSxg2yEZtSqQunxO807nTvNKT1Br1a/vljPe5yhrG8y7D6wlvwx2RmKmGh0y+8M6Y6h7P0G8gYqBvIo+0DKPGg4'
        b'f8Q8UmyedrdEbJ4rzshFtWFphQVJWnedyUjx0jsPQ8WCRXe1XjWiIhdJbDIom4xRGzuxTVIvp18FqR/0FxoTpIG0u6EvZL2YhboRXCUoeKiggIVQAQuhEi5mFDxUUNVG'
        b'PQsKHnI1Lec+YqDgIUNTQ/MRDsZJYMPQMG5UaUmWqJtR6mZ4m62uweF1Teuwu+vpnsGUZgIUzj6BwVvZJvb10ZsOfsT4wtmnK0by2DM6QzpdqXaaBV44a/CHUQ3XsgjD'
        b'nZA9E9kYWRgXx+eggCAAzqk8wz6vfMIgEMjk4IjQ2NBkQjsnqEYafi6aIJbj/FfuxmWpXVnzPzGvnKkesC0sYHYmuS2ukxkQugy8s7KLRVfGBJqcw1JVR90jClQY5knM'
        b'UWP3UTM07rEbV5KzQJWAAzX6ht+o2bwZb4SSG6bTbxShG4JRMwH9hi2+YTvxxow3otANK/Jxb3TDEd9wnLjhPtONxXRU6IYDuhGAhYaEagwjwaiOy6iOYLyU6a6nNs5A'
        b'QU3E+AomQ01nnEW41dMCTJPW2bOQvmVCk6jTxXbx4oWLRw1NO5MHNIeFaCCqFoN3DaPwEQnHwqJGA0PH2T6qEYQ9/WvhQ7nJd8c55Po6JkPLqNFzVN1arG49qhUyLsfS'
        b'CsNIcy3igx6FNSFogkInqLOwN6xzyXD+XXdxYoo4dZE4I0sctUQcmj1qYNzpOjBvIH/YYniN2Cth1NgVRaTmjuJRc3+EA6SdwpioHCPjx9nhLFWDcca/Gz5UmIybXE3i'
        b'BLFVLcYZf2RIbzUiZsh9GfAQdxW4Dq6prqyiGVNKsoNnLIZvhjysA0c3T9tiypX+/iYTI701fwXpzS5QlP6tNOVvZfQ3t0CF/K2K/laTXp8z5W8p3rtVaQLdrTUrups9'
        b'Bd2tPQNC22wC3W0wC7rbcAejwKjb+L+L7u42OYOU8nn5aV81nwB3qxbJFZj+KrKb9wyye95bc4gPhNLKwvyqkMK80qofHJ/jdU+5+2/Auj1pYKoLn/UWJzg+KfQtdpBL'
        b'UKUT1sMuOHBj/3ZqtidN/HP5Xaht6Uuevx+nLfscAQw6Y5x2pR+9rw+DrysXYPq1clJobHxKKMFoWzyDsE4OCUkqrJiONXWqDMAZ/i2POk+wpmUJ+UFvtlgnANTT08xX'
        b'mhYHrodKZc4UirWscCpV0NVKLr412zecK2Nwrv+3sqd3PMueZjGe37AuR5/Yh0cMQS1xppYOrsgxiDc1M136VmcSuMRdVcGkXTudArdhq2Jq6WsfpzOFWK+9djwCc6nb'
        b'DpjVM+WT9PqO5EkCqjSSlZOd6mKc2MXejGMvyL1xf4zPJDbvbHAMtJI9DrGgXnYIEDamP0+wpsHSes+0u+nkah6DPgBW4PnMkSdeizvtWkid99/BWc/61bkKU1nWuZ5/'
        b'Bsu6MgFLGQsl8zO8wej/c6zqIj7rfTP538qqLiCljmG8mFDyR4KqZe39V0DVMn3xq094/mZQ9XQVNBuoejZN9gvk6Bm10szP/w5Q9LMsKhqbkrsCE08wUmoWQNLEazO5'
        b'0nwOLj2tnqVAadwb0pBo1CPazs4y+jWSsywlv4flXFr0H4zz/zsYZ1mLm4FijP/7LTDl6Y32N8KUZ2zA/0Ep/0EoZbm4FAIiiQF7wfZJZG8QvDiV2gub4N4YGvQRMbnP'
        b'BAzB3Vx4GjtBLV3a/y+2MBtFtEPd+dgr93Ldj7ft2M9U89b39jrk7OzUXbSt1j6gKTTpZerem/feuPfOvZF77967sce4c7ux1ct3G8HoPY3XdyQcu6OSr/vN4ZXmMZG5'
        b'GfJuG93f2WX1ktauHPnXdBhzG9T/y+cjvhzZALCcD7fYOVSXThIA5FeQ/WPwGjgI2+AJuGsaP1dGz8UOX+ntIv3guhm8rPisu0x2SHkp2VuxEh5YhoFLl8CQFA0L9oDj'
        b'9A6tK/AgGJyKbQDnF0ohuKBzOV/5v2G+wWOOGZmxz4+bpgJjS+nR2rcrvRgaOo3loiqJuj2lbn9f3X1E3b23eKBqOO1u6qhH4LDHXU+Mi00luNhUgotNZZJFlEZOs+qo'
        b'rknzenwtgvkcTBVfpG/9eSjVWTOtpzADR3W55/9ejmplHvuZWcwv41OL+cy4ygLazdCM6NTnikbGTQ1CRTOFm2o+y4jgOVaq/C8f+85XmJJ27rSRsdz0kTEaFytJR8Ys'
        b'KQNVFTNQi7hkZKwww8hYkYyMFZ4bGSs+N/pV2KQoHRnPeG8a/3TjTCPjX+afTjVD/D8BP53umUQ63JQSQZejDhqjGf/DQ/0PD5X3Hx7qf3iov85DtZ91UFqG+hN6piir'
        b'iN+BR/0FlfFn4lH/dKjn3DhygtkXDqTQHkoWgVaa6Qkuw720jxJPFMiDLT702YvkCFgbL0iTghOj4F58Ci46HbvxwNxLDhzIYYAmUK+EzzzI0bjOEwtdJ72YgAv4WNIk'
        b'rjMW3KRRF6fAKXhIqKrKioCDUkoo7Aanq93xzSNp4AS9Q/4ZdyKBoF3qUYT4E2ExwAF4UgneBLdDqh3Qm86w3nvSDwmsibCnIR2wJhbuiQaD4CA5d5RtrRhoBc5U26JX'
        b'EtjB0WTG4b5mcs6BAYv2sCGWPjuWxFWAe/0MyIwF9pj4oWyg2FBMqQnpgrR0zIiMio0B51IiwIWIWAeBHdwSGYvicGSBy1wXUJ+UzDABrWplefA0qQCUs3ZwSOhSybKD'
        b'zQxmOQYN7AG3ql3wDOGqG94cLf0AD26jv4HZhytdKjHwkGBHOYwcUK8ADvJQeeKMz18Jr9qClmTZs9IaS6HfkcYmx1hcpABOL/clKIFNyXHcSjVUhmxwPkGD6QeuwOsE'
        b'geDqh+YrffDaaiGbwQJb0FRriGkHOsA+AjoQx3IYNXxtBiMgR6XW1ptRah3+FUfIRANGozmFB5v8uMBJfZdjaeyQIG7bmPkT85+5Rz43v+AZYax1+AuHi8dvPIpft8ki'
        b'dqmcn+J/rb+1/ivLe+43mAp7xMFn32cILqRrab7i0xzvcpA12L7up/yov3mX7ypoejsrPCDRJ/iK6oW08+YP5ORfLi1JOn/2+JGq6NHgBcE931iHH7P2urY+dEg31GNk'
        b'08J76/pubtp4z6Ut5bab9vF/ndpy9rustMEWvZSnBzIMk4dOQKqd4+aX8nmApsLNsKjjaWde0f3Q442O8S9HPg5/Ol6/YP8c9b+b1tR+d7fwcmHlhg8//ev8Cz89uJnf'
        b'Vl/789HPteRZcrfe1mOrSBzXBs+nPl+cEbzyOvufRfE631Xz1aU+UipAI4EHhqPmMnkOKQDeoLey79eFV2TsQNAWMOkiBe4DrfTG/8O5+dHxAmYhPEXYgfA02EMmkBvB'
        b'ftgihfvJg/1Svh8LnubDi/Q5nAYOPCibJKLW0j7FVQr66j4adnebD49LhQyKYC8WDe4KFjy2AZyjz2jUg+tgJ9nQDvvDpS5KQA99bKERnLOlGxnYixIzcaoOnAYnyWw4'
        b'GRxeR5/vnXK4F/SCZukBX13QRpJRAs5a03mJVkzHR47QlFcNDrJjWKCWPpnTBBuRFqknx3Y4iXELmOC8HbhETuCEKcBj0S5RrOIkpD560AwcCe0QubOgKFJ69pLjrE6W'
        b'JfzgFbpmhoKc7aJiCddxuzZJuaY1Gx4DXSVkTSMI3AQtxDcObAHXpFP8PHiQZvzdNgMD0xl/UwB/4BhL3hEMZvPV/qCdFdibJW8aW28KvMr02enYTFC9G7Rbl/EQn38P'
        b'qodpbKaHNzdtlujaULoYWaYRSk/YgyUGIZRBiFgrZEzTZIJv59HvP1w44hotdo0mTwVJDIIpg2CxVvC4CsPQvNWxUYEQ45ga/uS+n8RgAWWwQKy1YFTToNmH3BDN7/Dp'
        b'tei3p1yCRuYFiecFkcMEU57UNbmvaz2iay3R5VO6fPxOHn3gIFGcsphKyZFY50gMcimDXLFWLolWrGkrtTewtdOZoqqOtb2hI9ZeYmuvBya2YrvQuwqvqkjsUiQmqZRJ'
        b'qlgvddTYonUxJsClMztTuhcNWI4I/MUCf/Jw2F3dV40kdqkSkzTKJE2slzZmaE4Z2osN5/fqiA0DBzwaFccM57X4iSoaFT/SNWrJ7iyQ6LpSuq73dYNHdIOHw++miVMz'
        b'xUvyRkPixYmLxIvzH7KZeoXYSoJCnJnCqWYPtd/CSfv1nVNEpKYj0X6HSIViG8gFxqQNBElWuDeTGUlMF390+D9nCPnfhDor5rN+yPpV1NlMVoI/jHNmHlcdQIZc4Umz'
        b'cc6K108nnT1LOYNH4a5qoiGbwFFweBJzBnoZecF+bC7qlECrOexmwx1QlEhTjm6DI/A6QZ0Rzpm7APV9+8xpglkrOII0P0aYYX5ZygLQyCkhYw8NaxZZjhfrrVH5Nsmf'
        b'IRtN7fRx3QhO0JgymlGWYFWNRRvu1guFBwRWbIIog7eMycjHd32lMAk0VDDxmVIGNtPCkySq6EWwww4NQ68QShlBlMFuuJ+snrtrpkfjbhUchAeliDLYqUun4DrqTbck'
        b'wy5tzCmjIWWgMZ7cM9WDrcngnBuNKaMhZWBLFJ3RwZU8LjwLBwlZDHPFvGE3jaPeAWvzk+FO3MM+Qw9D/fAlUhh3i/ZhfJgeI2aFWmBoGg2+SnMzx/gwxrDT8qCTVpb0'
        b'RUqP4MOcnHLLlFly/n8OPmzH7wZG2T6rgWanRd3AVse9bKnVkWQy0U0Vc8BseoVrVLKtzeiLC91pDtjY0rWZXh6lNOvbxg32THDA4NBSggKTYsDgFU+aF36+MJwLroJO'
        b'GvZFSF/bzUicZ8to14O8itX2/0yoYPCZtAeDRnAJHiXH0vGhdHglkWcS9KeUdPH/ZEmzUZYr98lKmjSfUm+wjVsF99K0LYzaUpanGVyouezmgpOgsRK9QFBboN+VLs8T'
        b'TEcatUUwW8uQoINaf8LZsoc16VwwiJOKOVuHwJVqGj2yCxzFoC14CQ7AC1LSVhE4Vk1Gcq2L0Mf6HKPQuK8G3pyAbcE9uaXXjd7gCNehhngi7fqthYuEmuHq72aVVq9J'
        b'tzMFYR5XtR0U8pw8rvMsPnYqVuO9k8NWgvt3LnTwuhO89DvLj7Rs7rAdz/mOX05N+SzU9+P3Er53LOW/+/C1rvWr7qesPPjKhRNPbn+l/2XM5r7NH5/w2ly66w2jsrSM'
        b'G2euvP/Ne+8t/V43d5nBXz+SvPeo6I72exuCg5+0mOX7CphWmi98mtmTbpkpf6dwnuf2I0vkP04tun43Qufmz8Mtqr7/fGyqdt/wr+p/j1gU67ZsyUsufbYvmS+KXbHu'
        b'+kdHzvz9Eyer8U+cN3MXLJcr9jx1eFmaTv/hO6evLTnxyc9BvifTx/SXPL7CSZNXv8OpMX/9n3m6+z/yGtrXUh/6ePmrr3+zQumkGc9I5QVlv4pCt/w7X875x64X6uy8'
        b'vziwP/PalR8UxxTEvjrdcQ4ZB4dV2vUM3zirwJYEl+xsyDb7aXHCd02vvn2g0FPVsPt1xdcoOKgNoWP6HY0H7t6KP53aenaBqn0+/7xmSWq1YPTe8kvHti43TPxiTc6P'
        b'mgs5wrw3cpo6b4elPA3MGXxb6bWVrzYMdw3JvXb8U6P+H1p3vGnpNMjs87mqpvG6W9qTB6K48yd8k5NOzMn/pmbN3b/2vPrX99/W/Mu1+S/OD/iGeT/8Umbe8VNXqlZ9'
        b'K/xk62vy95Xn5nn36rR/4ly18+qnKoJPS5ZL/iY6tLFE0DB0cvz1F9/YxOgxfnN96tgxy8cfKx4q+Vmh1tv/pZ/E7nPgqDXn4+R2nYIVZTWpn7638MnVy7YVG3QW7j2V'
        b'uSwm6N3X879RjtmxliXe7VG/5ATrUa5W7E9Pyur/uSf5ZEy2aA/0qwgfSeE8cVTa3HUk8otvU3O+pTziV5rc+enzBTb+9/hvaD+KfPull28uOKFQXejw5bfdDUs+PrRe'
        b'ZV/BvH2D1w3TPIs0Npz48uChv6g82R1uoZr+wcaOLu+4x/HqT+RenXMk/oNq9gdaWz2NR0Wi9tfP9b8heiM+MmvzkrYNT0zd1Y//VT8vrpj9tt/udXf43xcte/3eY/fE'
        b'7+fveLq4fdfXIVe/ATcCXvswT/nQ1+xlBzI+mVtX1/mJzjt33vpggc5nQYfWe/UOvvW18ksR5846Zbz5BejTLX649Mzb7Gzmj6nmdu/ChKsvVVy8YPCO6Eelhui34ptE'
        b'7wn9r4cVdN15I94mi2/VNnLQSam5StXBxLSnyjKTdbr+5fIln0Vt+Lqz6mG11cEV1Rd4Zh7nq3ryr3Sk3kiyrG2++IH+oMbCbxfdXX2g85TO4t1jtfc2RH/4RWt1fciC'
        b'/r6dEucfK5XuvL13KPcfHvu/UXt/KPrx5ohkH8PUi/WxNz8yPPD3z7XHnmrsfUdHGH59d9vABcrm9IoFu8xP3UgKuli18l+a739YrrOhb9zZ2O2j+s8O39F9Ot76lPH3'
        b'IquCjTV7tzzV+LxnwP/9Nxnv5ykm9LO7Vu+tm1+g/2i57rcr7OvD/K2K0oN/Ln2vu+wd+8Bju19PqVk3dzT+yg/LPn8xY7PhTxY7oodv5156+K3h1hesAgLjz3z50cpr'
        b'V0+3+iu8UXfww1VyXTd3/V3bx/HUW0qvGB7yPfOp0briwt0D+g803nl0+NLRD60fNaVteOz4aKXlwttP+OU0YeDQGqfnJsL0JLjBFPbowT1k2jkHntWWwvZNE2WUK9iU'
        b'R7OKrnriOekE5monGhpJfZEu1JEChdAAYVs0OApPwb3TWVfwNuggzxRnwnNTGVXgFqxDoxhMqQLbYQs5qG4FjoEeOweMqQIHVWWkqlgooukc19cuEa5dNTlGlJKqkmE3'
        b'oVaAgWUJQgcH0I5GQ7WCSn6UQ0WkLSEI0KwqH7BDHvRZggaaNnMsFTTSpH5wM01KqzIF2+hj+CecQB0qM8dI2IhyK4NSgYsWNF+lTQccxlAqlO3L8KQMSwX6UolVYS08'
        b'AfbQ5Cj08WugTQamYoJB2v7SxAcnuGzQJ31mKpuKkUUbHlrBvjxYD4fgLUKnImgqLSNSTGFoWHCDjl8ADptKyVSwMYR2DHEKXIoVTudSwfPJBE3l6E7yvhnsBs3RUfaR'
        b'BqgLk6Gp4EAaKeY56lqwLxpejgc15dPAVK1RtOnmJOpUtwsx3WmRxlQ0lRk4TMvLWdAfzF28HiVwOpwKimA/ycAy2ITyj/FSfPtEGV0KHgYXabJJGzwG6oVp7nFMug/v'
        b'NIE3aNPSBTlwA/ZNB0yBEyWEMWUEj9N1dwhcLLQD58A1qQmGdg6xHwxI3Rt4a3DjBCqwDV5CUiMHTjHhRdVCknK2wgJU5B3o/73PEGjmwxM05ep4JjgnBVjx4EEZh4Ym'
        b'WME+sJemMbSAro3CjHKHaQirdQISBYr9+mZCsMIzHFjLh7UYVmXC4YToogHcbholAS5ZcqM9EvnTSVXL4GVSR35esN8OnDVxeIZVVQKbaFDN9Sh4QegA9hHoCE048Qwi'
        b'pasN+lEB981LwHAmgqqC3U6k4JjwOJNY1eBFzlRUVQNNIYG74CFXWB+AnY7jDxJUVQT6IGmbO8ClBXRrSgE7JklVS2Ez3WKuZEM0lsITtxMOU1hVWrokt3NRtW7HrKpY'
        b'2AkHZLSqBHiALosesBNux7wqVO2n42TAqkBDqQ1vaKEdZpqgqpjGqzIFZ2iBuAL7DdC3K8Au2DoJrLoKeqQmORVwgcvHvKp52Fu0DFllCWiMVi44pBVdpC+FVhFklS+o'
        b'I7IUBXaHCcG1WBpZRQOrDKRouip10BSNQSYDSyZpVWDXHHIzGfbYC8E+t7ipkJlKOEhMr4pgpy4SpZ3lMVj+MapqdQzJSBnohngtow6coXlVhFYFusBWWrK75mKA0tL0'
        b'qf6g1ZxJJnRBPbg2OTU4AI7zYLMfDS3ZZmwV7SrvMB1ZBXYHkUiN57MwIWbpykmKDlLy++g9R31wr+YzzKq1i1CqaWQVuriVSLzAD/bImFVgAG6XcqukzKpMeIykI8Qr'
        b'F0eIgVaD4KIMWgV3bKL1YR84hDQtZlZhYBU4B/c46oDT5M014CC4gqFUq3zwkJwmVoFt4JQUw4emtARZRXBVeujVfUthOy1ZtfDoOlSiOxg0tEoKrNrjRwttK3p2gACr'
        b'VpeDXhmwClytprdDNcBecJnwc+LS09G/amLhFZRuPdjLsbNdQyqaD7bCm9I5xAkz6RTCDG4nFZ2gUEQM3Ni6rQt6neEt1JqwCjfZAG5xcUOsQV3jFRQrlkpl0MTCCHY2'
        b'yVUCD55H8fJhFziEhU9eh2W+FJ4iuRKCbbCZYIV2rZvCyRJ5EiUaAA7D3UK6d1SiQVlIQRv7cBw3gP0CpOdwFAXhUMo+RB3ctglQlkBImkyFj5W0xo/xp2KyslGTIUXe'
        b'DUSggeZkYUiWMmgXwH0e5PMOeNf+NFSW72b0FE3Kgrey6QjaQUNaNBSBHtrwjmlZJXAb3XmeBtfRNKsvCGDT0DS+FTiZQXdRe8CJFbLlO6v5k3yrm+DCIxv8QD84HI8X'
        b'QJ6FW6Gp414Z4Ar0baJHNy1429tkiRFm5XV1uI1dBc8hhYybggvYggq9D49+lGAd5uTzI0nPzmbog62ccHDel6QsE+5HHQ95Dt3u8UQ5V4CtrED0xlXSBbmCBivUVg/B'
        b'Y/HTwVaocPaSqonMRlVGVk68YEfkxMJJIi0XsWiU1UI6sWa66PCKhYYtidsCHFokRN+NR7K1zw5zDE/Bg+pr2Rswb4iIa6D9AjskkWiUtgxcwfYeeIS13hZ0k5ozQW2w'
        b'XohdzWFmGMkdkxENTmloszeiRnb0kTPp3bgLccXPwvqCLfDwFN4XPGNN6rTaPIc7FZOFRoA9NCoLtoGzdJ0OIam6hvmLqPiOTfLzQBtSf2TYcNxcRwiPJxFYGI1nDGER'
        b'5ZdsUyyE+1wip4IBszUeWTIIK22Ly/M8L5S+Ynid8LzgmbX02KMFHACnuFOJZPAm2EJTyQLRIJcMt4/CC7DJjmZbTqd5oRruV1rnQiuzTrBXn5u3kgwNaJ4XuAJ76bHD'
        b'jQC2lOa1Rx+elcG8omiW16HcBVx7HqFe0SgvbEaitdEtP/YUlpcSPI9epVle4AboJQonFWmSBu46OTTuITAvMITGu7hwV8D2lcKpJC94O4CGee2IowcU20JKYd8ye4Lz'
        b'olFeoDeKXincD/t1McsLk7zA+VUmoMmQFEYYUgJ9MpZXC+rh6UzJWF6wseqRFGcOL3EFqA+9Bg7JaF7ta4kGtgZ75WmalwCNo2sncF5Zy+mefQesyyM4rwjcc8twXrBv'
        b'Dt2zHQR7lWGfIA6ztEwngF6DG+gK3YbdVEzheaEqGEQPEaAX6J9LokgCg6uEDlHVVuDQFKCXPxpZkKGHORP2eYJmMsWYyvOCVwpoPdbITQJoYHxOxvPCMC/XYoJAc10E'
        b'bmKUF+Z4BYObvrBzDXlnsyKDsLoiYb/mBKyrKIuv/efBuXBzmm7Fn0rmos+568xswSPrfj8rS081pfj+oUwuQ7Gez/P0rUa5cXkGz+x/mKplN6JnJ9ETUHqCX6JqbWRi'
        b'qhYOZ6VqzXb5N9K0tI6otar94TQt6eekGA5R4tmU9pROq7bMjky6dPCN6KPRnUxCc0jpXnRuTvcciZEnZeQppe6IwjriJUZulJHb72NaPYNKUjuqJlrVsfm+tf+Itf+w'
        b'ssQ6mrKOlujFUHoxOI3/IVP9/55MpYbTjVuCjkTPhtKzwWKhelR1SsFIoUpT8CMp3ZmUwE9is4CyWYCvKXUpYZxMeFd4b9i5+O54VHSYCoOCh3JymDiCgofsGYgjbC5O'
        b'BgoeJjLdMNbKDWOt3DDWyo1grcporFUQwVoF/ftYqxXtK34f1uqhHBsnFgXjin8M9inqaJSosmMtZR04XPniWip8UUuUxCiDMsqQKgUcm2q7Ki7yiPYIlJzFlCCAEoRK'
        b'LMIoizB8Obo9upfVz6WcgimnqPtOySNOyeKUJRKnbMopW2KRQ1nkyJ5SkFh4UhaeDxXkcNnL4bJXwNlBwbg6w9j0t2CjjE1bF7dmi43n9wb3Kowz5FCuE4cW3VgkLa8x'
        b'O0G3T7c/EljLTKaoSFTeKye2TB5wHpp/Y/6wy4s+L/pLfJIpn2Sx5XJx+sL76Zkj6ZnirGwqq4TKKpOkL6fSlz8eDQh8WR7ID1e8XAWq7sZKwjOo8AxJwGIqYDEqf5x0'
        b'Nk663AKUdBSgtvYfytR/KFN/NGVqEdMbQ6a8MWPKGyOmvDFhyhsDpnCggdXPeMT/Vr7Uf7BSvwcrNctwu0ZhKlMq1vf/NlMKowUqNTlSphQbM6V+wlsCtP4MIJQQT0dn'
        b'YkHR5fgUl+OzaJb3MZQr61c5UPazcaDsZ+NAzXijiL4hGDUOnY57ipj2DQG+IfjFG5jp5ISZTolMPmY68QnTKY1mOrFVzcYZ04IJphO+oCxDKC0YnvcbiE6WhNn06+F0'
        b'ohO5Hjed6OSJiU7eGOjkjXlO3v8dnBNOZxJJZxL5VhJzLDRy1Af15/6qeOfi7wtxmmXxjHPI9SBWGQsjl/7IkN66gg2FPhm++GxCFay1j4p1qIiMhXVgN9xpz2TYgCG5'
        b'5fA8vDRtx5ya9Pc3AUhGD2o/C23K4BDUkVKzZhELh81q0r+1/g9z7wEQ1ZX9j7+ZYehNAem9DsMMvffeO4IiVYqiCMIA9t5ALNgHRR0QdUDUQVBRUcm9ZkMSk50xb+PE'
        b'lDXZtE3Fjdlsyjf533vfgKDuftdv9vf9/mW88+bdfs6959137+eco/rWZr5rONWcAc5MM0mVzkRjEesrYv1F3Va9Vv1Ww9bZrcbVupVqz5g94rKpKvVK7laqUn1A4ymD'
        b'SxokThPFaT0Tp0nitFGczjNxWiROF8XpPROnTeL0UZzBM3E6JM4Qxc16Jk6XxM1GcUbPxOmROGMUZ/JMnD6Jm4PiTJ+JMyBxZijO/Jk4QxJngeIsn4mbReKsUJz1M3Gz'
        b'SZwNirN9Js6IxNmhOPtn4oxbudWsSoetmoUm5MoRXc1ppRAvOYiT6q2arTqIkwaIk7MIJ51QvGklm5imcnmgGxudnhenwnB+eIX9lMYoVtmanoKxTTWlcNRUb7e8vFHE'
        b'pPH38WC+fbHqErnym1HYJFRUJLSLnqYLqVLtI5YoVAqEKLapqhHbx7Crb6lqRL9m6jJOQwGLPOyqyisW2zVWLW+sElXVTStimrIl1vmdUcI/02aaCVid8SOjHiuxJVej'
        b'3hE07Iqqxio7UfPCZTVELaumbpqBD6InhqLL0f+mxY1VMytfVtW0uL6S2DxAba6vbaki0Npm/ASvXYX1zaZ3UGgXX0NUt9yieSpN5tqZCm1Y70ulEskwwlPFh0mKe9i5'
        b'xfAmk5Xbiaqwal5T1b9iEuahWywPWwUpn6b+qFI8rG+sWVRTV16LzVOoLCgiEmDTG091VCQqX0QMk1RhEy+1WAuY6b1dZdVytGQR2dUzDSc6jG6quBg8wpbVi2aqslXU'
        b'L1uGNbbJ2HtKXzKDx37AWbms9oF6RfmyJn+/Cs5TQpPgHA+i4JAuo659hCLTQwMJOzZR12YEngGaOoatrGp9grrmsKm2pxSt16kR1DXnGdS12jPIas56NRXq+rlxM5S1'
        b'f2L9G2aMZkzFf653989UMRF9GC3MeelpKjVCPDnKSblPOI94TFRt0cR+vn6uWxUzIP/ZrP8X5nUIc0KwlZSKciQ3ylCTyhh1SKawqUKmD97yuudrMldW1jDKs6p6Zwxe'
        b'PMwbmqtUAkDUjGbmlAB6vlmRGSrGKxbXoBx4/pY3N9UvK2+qqSDDfVlV4yKVquW/MFDSiOb18vq6SkxhRirMmNH/GhU/Bcudhoq3yRDhI7smn8NDih/4vP4m3qu8K+28'
        b'ty9tElE162r8NE9L65hVBR8Fa+Bx0Emc01zF2IsmHmzjgSugnQcPg0uAZLECEk1w2tCK7P/nMYDhM/Ag6AHnMuBWLkWtp9bDTeAcQRj/vICBuUfVlqXF1OVRxIstFM8H'
        b'p1Ele+zRUyOUCmWBrbX/+O233zYGcymUyS4rosHjp/IgiqhXAtnyWILAH070ggd9vdgUN5iV5VrAYzdjy2P+YJdIBHfqw7YVQuJYMC1DqOXuxqJ84MF14Iw6vwDuIdhc'
        b'E+twHXyfrZ+VzgoEvUCCSrBDESJ4DsimF6GNA9ZKV8ohhOvAiSSgX76fGZQW6pAYigOvY9zAHhdUAiZajgs+iGYKgK0xpBnJ7g0ZPDjIT04VYshYPhRrWpWCDgKkb4Sn'
        b'3OAQEwUO1XEoTX923TIej8P48r1dBztSM+AuAdzn6+VfyWNTuuvYS+tgJ4mGt+qXPImFezLUKd317Fp4roGQax3YsvhJtFE6i9LdwF7mF9OMgW2pfthfF6NOmYQTZWOl'
        b'WGEkuDWJg4sz0DD1BG0Mcv8Y7FzAHLtlY2c2u1K5+hzKCOzB5+u385tTKHLseRpuma5u4UYwe1mo4LTUVAG7IRwct4I3wU4TeAleSjUGO1N1tOEl0J6Sk0tVVWMHmYaB'
        b'8CBsI8OlKJAZAV659Wl3TWdTzYXopi0cwmepz1SBNVs9U+a6wbYkuCsXq5OmzoWyyWFrCQ7ziLJHZjJ3trM2biiXC6/FO4M+HhW/whget/JCFMfDNxCcYqHbcMhgeSMa'
        b'IHCE5bJmGcGHgx1+VXC7v45mYwtiuxrLHd7IJWRmgX3kqPU8HNJtIJkGWE7gcBGjEXIT7If7KuBm0XIClOHossrgSU0ykPxEoG05vCFqgJd0cbaNLCfYa4MGEi7VC56A'
        b'1/TAWRG8QgoFo6w5YAAOMjYPb2Vmx8OBGRUO15Ax4QS3uz9hugWUMlxfAzuaA3HOc1UlOJphPWxNN0kTpGTOTZrKoaIo9uVIwZO1OkAKr4LDzfhcGxyE18HFGblxXioM'
        b'bqQc16iheb8NdBOUezrsY+eqWCMCm5E00mIhxu8xr7GIlqiJWOi5OvvP31zOX7DUKNr4xPvpl67VHqi9V3S0f/eR/NEFnpdz4l/6lTXr8ctfbNnyMu/g/rh9PjovX+VF'
        b'n4yTaa96LdX2v7acGPjmnc53ktUfXeUWzwvy/e74t2tFb77zzo+FvybUOnzR49hfcawjduVvYTevLN7d+tfuOZfjF31FPWj79O+h757vW7mjev/K1sJZ1kfnnlLfaqRY'
        b'vyy+IsPswm6rhSsX1+l+HvtY8o1V8qPxpTbblJyFixYe6w5/7aj4DxM2Gd+9Ef/3koLyxt1Hd/a71IPtusNx4SGxr0d2jX30ttvJC1XHa2tHt97ltjxc7jrsE92StfdR'
        b'18Su/EeuO9/s4WlfnXt83ZF3/3Zr7x7Dz79c/b1ozjsX9Ev1CnOq3ZfcyZzzeOsOG+GKd9L8Fn4yzk432XXgwJrNc3cv3qB9/XDct/+wOHPiDvWX2srYs4HRVY5tOSvU'
        b'I9LzPryUP/v2W1mOb7n/8ZuYI0mFldyveWticl+Lf8Xw/Brd26tg18CHef3b31p8PHrph3FL0nSLTx0d6lvyZnfzB+PL7Q+VKz6/avwOvU3xsph7i/5j9InP0t/R0x4t'
        b'G0gz+TTX549e3y34kKc8p3uipyjmv+4UHFp0pGfW4kLdnfKrQ6PjwsShB33z333NbOWXId8uTx6OLNRdYXUpZTDvF+Ha1+u/CoqEnmEaP153WBV4+W5p/JeFPgY//cYd'
        b'ubC0iOt4f3dFw/u7atPfaqyMdrmt4Vyy8OryrwMKV+h6V0d2fGDjdox18sarzasOB3zUqlXF3/9KeGzXp/mt38yFX9gdndOytJybv1C43fxLzx3B/MG5laMnP97+zcFZ'
        b'55LvZM/dFBm1fmXUoXDdD/6S4Dp36eK5sPbczd49GUVtb0f23zn68b4SrbgK57dR9v/6uy1/k3dvimT7igMKTtzPN0slX5T7BfzZfPGC82pdZpuGQ86eNPtwHW3q/3XL'
        b'PcNfP9/XVnrzx69+fvfX0u3bxWuWnvNYl/iPY2/f8lz7+Q7TTRrjPj/kcTe9cvPAN323JV/1OS76ZKznO5+/bPre90DQuvCJsVH2Tw2VmS47/shbleBSX/5d4L2vrO6n'
        b'1/GiGRDEcXgT9vCF6WyK3Qw7gJSV6qVCpoZUg02gHWMQReAoNlKQCXeyKR0wiiY87IaXCVLCt9CYn5ymgQTEbtAFWlnhYNdSgvmY4+7CoJ4ZyDPcDDvYgkTAwJ6RUDoP'
        b'xaDdk4Gzqpch4XuG7QBPq7x7hRBzX+2wzTMT2wRbDzeCDra7Pdz/2APFJpfNR1kxUjYNHAG7haAtMwXbFACtnkke7tjkWaoGVbpOE5w38yaYioLVYCj1CYo7dQGD4w4E'
        b'Oxl4ykYdCoMd4G6BOqVeUg3FbEeCWyMPuU0+aqmZAtgLjid7YByPDhhmw1FwgGKAwVsMuNPdJZfCTQyMHGyHpxhsVyfcwZluYMwfHptUHd/EY+o4DpBEY0AfvEawR4X5'
        b'AJIYlcK2aCUD+SB4j1rYyYKH/A0J/wLhRdgJDuTzk8F5tKRQW8SC22utCf/iQDfsAV31GLo0w8ObBexSawi1YdAcG1PhfjiUhji8dxKaCbr8CdjFRj8J0TklPVWAsRsZ'
        b'TO5aMIqE/CFuKDgPhgkUkmsPT4vg7mTMEDAMTqbqZwjgcCqbsklQw75/rQnLo9hFGOW8V4tExoBtbEovng2vwS05DAp5vzk8i6rLEHikgxPcJxVSdt5q8HTtegaTewU9'
        b'6wZEwhSw32qGOzrAoLDBjRohaM8UpqR7JKfrgcssSn8xJ6gObmSU7HeBw7OZZQQDUe8DhzgYp6qhA/rIUCiKWUOQXiiuXYNS14oFUrYuvGDIOLtsE4KroIMvIogrzlLW'
        b'WrAziHAh02FZMTbvMA3C6gQHCIErk0CXXcSkB1EVGHOPM+lNIzyA7XygXhJ0KxcehZtELHgdSjXI5Jod1AIuc3SEqQSg1M8CJ40ZFYja6JKn/aqCvoxJkCqQwCskf0tJ'
        b'mgokCo+vJ25NI03JgEuCg0BC0KUMtBTeBrdZJXAE9JM2e0UVwuNxGEuIoakceIwF9rTADkKhZVngANjHwR3ay8fNGmKBs+BoOaGDYTN2lgrb0ZNYNonE3s7AhoLBzthJ'
        b'XQkMR77OW8Bm1dUxQqgbTZLTKigv2J+hw7KDbSlk9hgimTQY0YJ5+gTMOxtc4KBKjkUzXD0FhzcQyw8YWQi2gxtYd+EoG7TBQ7XE6fhcjM+cUhmpB7ee8o0Oh8Bx0rlK'
        b'FH/RpRKtiFXo58sscKFO5drcGHQXMDHkXQT19Ig6pV/JibcveozX3sbzEkH7ihY4rNfAgRufLBKxKqwn3JOULuCpU7nxmvoRBaTXS+G2OhFfGy3VeRi+TWmsY/sJ88hI'
        b'064xEfEb8fiGQ3pcSqOK7aO1mEHaXwWbiZ2LZAzsy+RjdQgeGOFSJrAf8XFLI4OkzcnRweWiArQsUX7Qzw4HBw0ZXYqLoBe9Z6hK8MTodbBDg9LP4ETVIZlHXqL2GoBu'
        b'UQrWEWE5LoBXWYbwMOMk2CfdQoe3AeydBNudCmKAjJdh54pCrugZx5lIUJORmDqvXJThDHsmtR+QvGcirO1UHl8R48+CfmOWo5czQTGawVYkidozUSuS0XQkwsAzCe7m'
        b'gBuwj3KEZ7iBzsmk8gY/sBk9YG6IMngq5ZhUFmVozckGQ0akjg1goETEA9fBZlw99p69gfGTXODvgETAJhEjSDhgG2u1SlUlDR7R5KcIUgXuGekJQSzKYBGnHAyWkdEE'
        b'T9hFzmhYpgG4jZ46bRiVzCvhgmN69UR5Z3kEe3JAzBwNmQH+gUhYh4IL6hngANzCIPs2sdAEHM3mT1fxQJPpPDPIb9vbwH5wSAfHTo7eWfA6B5x3NmZSXEDC6SyfPGgE'
        b'qEFn1ClNeION3g5OoqcqJpSoDNFuurPPJUtU0MDQYp7l/4Znk3/nwAtPtRn7Cs879yKWJU2mbyXNtKX5Ry5jpWNJDBKKNh0h4gqJv8KIRxvxJijOrESW0sLqpMtRF7l9'
        b'+IhoLFZhkURbJHXEdsQ+nLwfNrJwzFFhkUBbJHTEKueYd1SIHcVN++oO1nVwlLYOHWoHdZXWdl0FJ4uPFkt9FdaetLWnjEVb+9y3DrpnHTRipLAOp63DRxbS1tEosTZ2'
        b'NFfIgOGYxOSmkSltJJAb+SsDQoaX3A9IvheQPM5TBOTRAXlyn7yOONpY+NAuVGkXrLSLndBQM589QaGggzuhTTm4nrXssey27rWeoLRmhZFgX3JHrNhY6eCyLxVdzHnf'
        b'1EYsksROGhjhmtgobR27Vt+39btn6yfLVdgG07bBExTLXKDkeYjjulLet3GWVKDe2HjSNp5izvv2blIjabXC3p+29xerK82sxdwJHVTM9/qUpbPcOURhEUpbhMqNQ5Xm'
        b'Vl0WHepKR15vGO3o16FGG9opnfnS6N75vUW0cwC+4aB0cpd69ybTTiG0U6TcqXAsYNz+TjAdO5eOLcQJ7JV2AometHqgjhaqYDvEnqm1Y1cpbe0tty6U5Y9ED88fWTte'
        b'rYjMo/3n0v6FDG0dJdFd87tKaGshbe1LWwehtCMJY96jyaMZdFg6HZZDh82lw5jEVg4S767krgzaypO2CqGtImirWLnV8rGW8fI7q+6spzHupYpOXEonLkfptaYV7sUU'
        b'jkt5aO8qZfWa99rQ9r60Pb6lr7SxRV86KD2GZPqSoCNeaWnXFdIV3hGHcQNaXfpys1Cp0wBvwIN2Dx1Tu6N9zzRFbppC7J/MU9jMp23my83mK+1dei0mKLbJEhYTirlK'
        b'Arhq7lqvsBTSlkLZrHuWPnJLn/cdhHLPxQqHGtqhRm5VM8GhrHwfGpt1pB5Mlfiiv+be1d2RvZEKYx98qyNVaedCaOrgKRHI1GUNw1q0VxTtlUh7pY1XKhxyaYdcFG+g'
        b'4oQsZ2AJLYykhQm0MHU8T2GXQ9vl4PwPLe0l9l3BXeF42AlJgGaJqcXBFtrUlTZ1p0095b7JclP8UQp8pfmy2OHE4bQxxzuu4y53PBWCHFqQI1ajzdxRv7rCaUuBbM49'
        b'y0C5ZaDSyk5uJaSthDIHhZUfc4lH7QY8TqtZSmGodNlI7GjCaCodliYPK5Fn5dJZ+XTWfDqrRF5WqRBW0cIqjAJhRqseZZbCmjCk3IV4Mrl8YukoiZPESefI2AMWAzYM'
        b'MEthGUxbBuNOeJLg6Z7IIuWmMeijFPohkuQOFwwXjfneCRwPuBOpEObSwlzcEf5zO4JGmKfMR4GxPvgSd2Qd7kglS+kRLE0fcRx1GeXTISnykKLxirvVd2vu1slLFio8'
        b'KmiPCtSJ9KlOxOJO8D1xJ1yV1raM8DCfoHRmBRNHDvdN+fdM+dIUhWkgbRqIDexkst63cZW7pStsMmibDLlZhtLUnpgrclKYeqJeYYs97kp717PWPdbdtr22YnU0w61d'
        b'xYVSdZmxrEqmywgwXJS70sFNYoaiMQpQzSSYBGKO0sZdXPtEWiCp2LXyvq3PPVsfWYjCNoK2jcBdLWW978CX8MaN75qPoz95XgGdVyRHH49ihUMJ7VAitypR+geJ1bq0'
        b'Jb69EQozH7mZz4Qp6hjp3YT+ZIXT8CezGPyJFAMz+tT+fSTKf/PkwU+WJ1Z8/t3nTbIm9rpFMSZ80CMnM4bFYtliJMp/PPhPIVsIIqdHK4ga0Y9W57yARePF/51F45kk'
        b'mjRnfB6bu3hizth78kSWHGl62FUtEtq541MVoZe/76Rl+metG79AO6txO/vYL9pOGW4nPpZm2mmJ26k6/rOrqZzRohc0A93HeqBZWsGcDr9Ym4Zwmy5P0c6eGCAlVjer'
        b'7UiB2Izu/7BlW1HLeKwHeqVTZ6OlNS/YvCu4eZpTJHOJtmuuq2lornqONd7/WRurmTbqlk6ehL1wE6/hJs6eaqI7pqCoCZGQnLJNHbD9vmZiUjbqvfCIG505M4S59dhf'
        b'Q111PbGIbFe+sL65aYb7h/9p+8jMPU29aPtuz2yfZd5MdwW/pzEDL9wYgBtzYaoxFk8aE5Mc+3tmZ+PgC7fl5RmEaRyiXkg+kdHizHrRSsdxpS6sSQK45T3HicWklfDf'
        b'wRo03bSJueNSbHz4xZr4On4a4vOzjZQ4r6t04/SBQ2waM8LrdzCLh0UpaV1T/Yu17c2ZotRcZR/7d7Vo8aQIXVhei4EMpfXLq+perFmKmSI0CDcLl8Kcu9dOh/88bXD9'
        b'dwp+/alWV9TWi6perNk0bvY9akazcTG/q9n/927hqp92CzdFyWlIBk5GzbFyFzUR3kvd6tD/xMHb5q7l5kELKJezHNZfC3gs5rDjIheeJvuT8/wY3WfV7mSf2XPcurli'
        b's5HGT600a6vqVBsbBhSzsVGbwKLMrA6ukRs6vKAHt39ewX08dxdRKuD10gTW/4b7tv+fsX/Rv8N+tYy8mje0P2WJMI0lbasw/+23eYs3DXEp/du677FFZcUMQ57l72rW'
        b'c94kFtbX16oYrKticCNhcEfTC3L3XxT/YAZ7G/4P2IsxbHhGfLefmsSwIQarqTBsmq0sldMRBsVGtRqoEGxsxPqnHIus42g9h5nPYtoQe9nrOSrWPzfun898zArfp1hv'
        b'm0HgEVawD1zGyAmwC3ZPoidmg40EPHTAn0vV1hliY95p7TGLGaQRu8FWpN8orNXCiXtYwgDIWP7Oz1CjdG2NSWIjYQXV7IluonIvq5HDnVS4K8IathHj6btS0UUGtqee'
        b'k5UjyGdTJVEaoNsA9jJ2Qg/OBkdSUzA6AuyZOrWDUrglg0u5V3DBOXABbiKoEKPVcJtoeQYcAIenQCFH4GZiA5ALzmhNmpmAvXD7lKGJesYc4dowbXzylGpsgk/I1AQs'
        b'cB70ujHmCPeDk0v5PHe4U2/S0Cc4tZhE5dvZk+30ZbHuGfhYwWARp6rZNY+gNaBkPmgl+9YCeB0cTVajtDTYYA9vAQFLrbEzS032oCKTUYlqLHBSx4gpsAGO4nNXniNo'
        b'F6hTWsFscDo6jUTVlgApbBemwI6GSSNTsD2QVBUHtmDPWIIMcrCoXgzOrGKbILKMEoCJE95gT4V7krHfrDTYTmgNd4Eb6tgcNT+cC3drucwY0DqTA3oXHtDaMwb0zOE8'
        b'6Tnnf2coPyPFtJ8zlAUZZLQGhBKgU9KS+LK0DOdQikH4bIMXPEQZ8Lz9E2NLvnEkyk0Nbhcle5k/MUmB/jrJ2BGBfnianwKPziMnJ5OMBsNwgCn1PLjOEaXB83DX1Anq'
        b'LQb4xIOnuKI0Txa8AdoptibLGp6YtOt/DTGhlVjJgbs1sKEcT8TQLjINM+apIzbBAXh+mnkgdzhMmA1OgdtgB2xPhT1w4xPzTon5jK3LHngObGLMO5XmPrHuBA6uJHDC'
        b'ZvykBcfnleZSfssoyp6yT1jL4zK4t/4INyZjavyTjHAQdDBeGLrBDhZ2N9aqMrZF7CvxspoJGuA6PAJO8mFrDLg207QT3AuOMDDDDgpsJ4ajiNEoeAVcZANxUR5BwtWA'
        b'M2ArH60ihPjQi+eeLuQJUtJZlAPYxg12ticdj4mD/dhME7gEb0yz07StimnebVtsB2c3PGfAIxhCdU22Kbid0YwPljeUxT5rOWSOAaIdMRzChwcI1BH22YMBYmgmjRyW'
        b'Y5kEdqIeHPBC88qlgLs0W9CMTaeAk0vgIQzkeK7llFRwHWwinMkAmzRgBxxoIYNhNriWIFoOd7GnMGug1Ywh/QDcXjLlxIKIJpYBEk4ulQxE7FZ2HRKBVxnzFdPE4KQI'
        b'hJvgcUIFNSy/UKKd4FbqlCCDN6MYrF2HaHGqoBBumzLUs3wRI+EGI5cg8QEk4PiUIZr6DSTPnDhdFFM5JVrYJo0cMn6NQTu8iOQR2FY9ZfQODvFJJn/QA66hEcyiWEGg'
        b'w5mCe9SKmZlyBAyCfn66SFOApplaORalF1YzsD19ezS4kgQexKbh4ZgM9lpv2EHwo7CjrAUbavGOfMZUixbYBy6QnmvnqOE0YJAzzY7SFbiHeYhcQYPmPCrfN/YpKTgl'
        b'AmG7I49NWrLMFrahzl1qUauCoxQLSil4tjyFRGHEUI8IDqpjiyUhK7Ed31ugjzwIwSjohF3wgLojOE1RHpSHTzN5EA7n6FCIJsvXzirT5QdaMaaG12ly8KJw+Y+aZR7n'
        b'XcKZm9p1alhiafonlKVZ1GowN+tydLGlYupRbpmH28Ia5uZfozUp/By2XVJW+37ahpmrEfakTMSkS0UiFL8mFaOF5lrWclYllU8dYbGoXVqVU7sEZBHGJoaAH7BaRDi/'
        b'HfOe9JNW2KKquqqVyxsjVoc9vUvcVNVYWvrECjD5TfDU0ywDT+au0kK0w26jP0d/Gyl5XBn+5OaNZY/NH3dS/Zz2YeDSUZisQ83wAAZGogl5AAlsgTCZ+CdJyc4S5Cc9'
        b'81BDc3WIrc3C+K9+3TI4oEvczKxcq4Me0+g5vHMaCsZqLkp0VA1N+LbimguNfZRoHoeiTDtDbhakZr4bZVgSOnj8zqrbdpu2TmhePBwxvKd7edQX22Kd9xxy/37j6s8D'
        b'pAkxhxy/39hSH067L7uWlxT+SdYn+21+MgrN+Ory/c6N8acdNi1adKvz23ffebT9F6+9bTEX2t4Kdij46dWCjK5PN5ZFxv7Dus2koCtg7pt596/49zcecln5UZjWhrnz'
        b'nM0GjTel+2xzsXS4Wh+V933B33UOV7r/STim75UfMy+5vObW993rUvfs+UdcwH3xp8MesHTNjaRLapxPirjNvEh1j9VbnQUDuv0edVeCj+ut89F//7MN32hOnFn7QVZL'
        b'/rzgrYPG0Y5m0mMJX3y6rv3LtKvai0v+8Eao83tUnOIH230H1p1Y2Nehve3oltnR6z9edfnYXbOD3kUjDwyrW5w+zbc/ouHe8MWFo1Hhn/fZ7Ww+F/L16Xei9T6hz//k'
        b'9+B9nbhPJ5IyD/3p5Xf8P55V/cubet333N57/5eP8xZv6tvXdu3Hu+cW66//W/zHH29555jp28sOzJ9daLRCbvHGS5cPv2J1Z3bUOd4ANzt7UbdJ5tDwzT/ci7a+wX3L'
        b'x/TvMr/zau/FjixK+OgD0QPTB+IbXzR47nzN/PBg4fge3aj7MQc0+Z5XwznFR+Tfe4dUCLrDxd/1WPuFfBt/ZJGXv9OZ7TtKOjfVpXx+ZkdJfKfp6OcWFsWPe4r9Hvzt'
        b'pyFhj2VrT89WZRz/8s2UBbf2Hjt7YUPNV4Hnl+1rzpz3w1n+I4/XH4TWlcg3mf+QE/Cmpc3NQSfn0FvcHz4V/vHlhW9wC78FG65paNskjf44b/THDZ9sW1GfXL3f+6OB'
        b'1u/lP3AXvaEzsPHN7aHnrWsKQ3d84DtRwvt75vgGv+OZRyKvKzx91k+YvWtfvM/kO4evajaZVHkWh1tGfvgN76ObvdXDoYF/+pHT/Hlh0rtGA9Ufv/XY+uOm2ODMio+t'
        b'Xg/2+XLBn4ptM34p/qFtSckPvxZ8CT5YUf/Zx86/1H21dODjP+/wXe374Y9hbdsPvRn1d8fiXW/tu79P+Ie//iIaf0ezURr84beBVRsGCvV+ON597KTks8TAW6W/0ifr'
        b'g9q3hA/4vA8+Kz3xs/1asPfO2dEY8GfOys5D5xf1sNdn7pg1Hv4Gf6My8Ze5+X89N7DEcgD0h5vkLVuzKPJbv9WvrZH/mPrjmQkLx4G/fxolvXjT4f5O9p93CW/n/m1/'
        b'75oNrF9Mg8DEq7xgBg1yBF7VwosI6VxPIFUjj41RNGn3EWgfPAh6Qa8O3MlL1nJDQniHMA0tgmeBsxzQBU/BUwyssTfEXcedBy8R+1SaltxSdj5arI8QIA8vpoAYaKXg'
        b'SJYPBS6YcRj83Da0QLkAh5oE4PATLFs8aCWomFrPcH4yWkAffII1BLdQbVjiOy1fDoc85+LV2hTOzZdxAJMGT6UjwbOhetoiDWyGwwSKluwHT6COJMKzvOSGNE+eOqWH'
        b'UrkAqTkxQhccA3c8DXUjODc45ITtMZ4BewiUJxqe0ydYN7jHgNhEhHvzEkiXamEnOI6issDOSbgbqwSKwX6CDXJCJW3XwVau4FF9ip3HisjyJgXmwd1pGMqGYWzzCJCt'
        b'DxwhLdYAVxcTs5/CpdOsfsLLiLKEc3uanURC0AZHp1nQRC9fxxio51k3SpSGmAL6SrAcTuVS2rpsIGlazhhD229ixRf6Z/HgTg/sMmyA7asDLpMoj7WZjHlexjTv0gr2'
        b'KjjIWDmFu0Ffgg4PHAjHFj+fmPsUpBG2ZfvX6LhFw/PChilLofAoHGR8515ERMRQ252gF63U9mIOqQWz0OpjIIMZEXsRu/eqDJUSK6XO5uwacMKeie1H6+ijIrgzORle'
        b'TWVTGg3eoI/tznJmRmA7kEQxliKJmchwcIRdOAsMkKwxZnAAI78ashIwnE6d0i5go/XgqBWzabYDrUlO6IA+Jzi4nODDuOAoCy2k+hYQ9pSjemUEOAa3plJsY5ajM+xk'
        b'0LK3wSFHnRSwKT2dr47eUK5jBYmjQgb7tpMDr2D4ppYwVaiNl2Nm4DIcBrfVAlvgRsaE2im3dJWBtylDksZgd5EzBx5AD0UGGr1We94Mc4+MsUe0vOzCCin7CkkXfMBt'
        b'4hKB2EVkjCKGwRF2dAC8SBo6GwzpwyHBfItJYC8LHloHdzMTfAfYBTbpwFZR7DPWlGEvOEDYbhINjjPTwqR5uslKDRMytNPARtCm02yXraeFJqQ9Kxq055CKbcLhORHc'
        b'E5TpRmC63HgW3L0MdpO4quRSNBu6wLVpZvz64CiDFd6N/iQixoSxKeyk0Ht2BzjEDNwt4JqxjpsBlwH/YdOd8CwzOuvgjjidJ4byNPE+wQV2dgLoYPi1l8KGk0HXkicW'
        b'AOfCEwym7WQ9vDTNAiBj/k/dFy1dV4qIxTlwMrcBG+ozt8Om+mzAHrCXIGShGM3sSUN90430obl4QS0Enshnsg/nx+kI5nkT64PYSl89g82M35CB1ahA33LUW43UkMVs'
        b'e7ClhUSFxqPV65AH7GU9sRuYW0LG+wqwRxvJqPYNT3DvbEEZ2E7IMMcJDbV2jwzYVm2B3ppQtA44x4YX+KmMRc4R0LucxO+C10AbD7YSL2QX2PAUmplbHjPaQdsy0auj'
        b'JwU2wj4kmrtZWbPtCaECPWAPP9MDzeKrYC/Zn9GgdOAtNnoV2mjJkPkIuAkv67jDPRw46kyx01l+iGcqc8G9MfGiNNS8m1PQaAYWne3JGMW9CW6iSUR0AdAQkMIdM5UB'
        b'pEjW2f/fQwf/HYyHPfW0GcDnwAzJmv6B9pOV+mrev72oJ5u4yehV4R/MEn4iLolFefhPUPUsa49HJJRoKJ09zhb1FHWX9JZI2EpHV6lPT4gkRCnwlSQoPXwk8ZL4h1PX'
        b'Sndv2j1UovHQ0VmypDdiAk3lBJasYLiEuVLyfWQBIwmDkTQ/luYn0PxUmp8l56+V5y2QFy2UVy1VFC2l82rpvHo6r4nOW0HnrZXEKV350qaBVfdcg+SuQcqg8JEWGVeq'
        b'rvTwpT3CRvLHqq6V0B5ptEcB7bGA9iiboCjBAra8cild2SRvXoN+bmDFsR9RVAv6eoxkBiue+cpivvKZrwVsCVvi362lFPjJ8keqB0tpQTwtSKIF6bQgRy5YL88vlpdU'
        b'yhctU5Qso/Pr6PwGOr+Fzl9F569HGQO6tUnGgVJieSsW5ZQLKsYT5XmFdzPptBI6rUKVyt1b5jLgSbtHI7p6BWLbONEoJrhbT+mOSe3hO5CJ7brFsJgQ9d7NY0BLaiDL'
        b'ue8acc81QuEaRbtGTVAs5xiW0s3zon6/vqxpeJXCLZp2i5a7Rf8DlSpD5QilqwbSlTyvAWuaF4raNlBMCyKVfOHFoP4glG9An3YLRclHGmf8mOBy/F0eURwP18c4+EGd'
        b'chP0NHev6F0xocHxCJxQp3wDJ3Qpn+AJS31vh0cUCh7jgOnChA0VGDGyaFxdEZFBB2TSAbk0Nle3APEgMJotL62WL6qTN6xQLFpBl66kS9cgwpexojHhIxV2vsqA8JHq'
        b'4Xo6IInkzaMDCuiAosnIMOwyreqlTDosjw6bR4ctoMMwq8PjMavltSJ5yxpF7Rq6ci1duUHFZQlb7ogt8z1EVLCleRE0L0bOyx5bdGepBIM/EQ3tS1jS6oGlzJXSNxiN'
        b'TZdR/ljLePWd9QrffNo3Xz6/WOFbLImRrOxOe+gq7F0rUVMGhtKBiXRgmjywUp6VI8+toLMqcV2+Cjs/RGlEZ1oQJxfkjLPHA+5qT44Obzw2op/8WkALwlW/hD4DSwbq'
        b'5cK0sdljiXcs0d3Abh2cBvNMLkgf8xmrvhOiSsyY+wtDv/y6NXGi+QMlqihP34HVAxvQj6Bu3Yf+YcNFw6W0f7Lcv3K8AFtRLKXTUTslEQo7HzwwbBAVvHwYzqEJjBuE'
        b'xm0iLUiTaCsdBZgo6Sylk4tkVW/6faege05BIxb3g5PvBScrglPp4FSFUxrtlCZ3SlN6+mPDZwk4B/Fij0JJ4sycpqNW94NT76Fcwel0cLrCKYN2ypCTD667iKmNCZEU'
        b'mZHXZPT59eKqvfxlXNnCEfPhZQqvONorTtUd3D2aF456GBg+vGp4vTyweHy2PK2ITi6e4pSjs9wlgHYMfERZ2peyRlQgzaxieVixIqx4wpDy9JZ7R9PCmPvCpHvCpHEj'
        b'hTCdFqZLEh+6C6SO0kV9HgMeI7PuuYfI3UMmZ2Kjwi2EdguRu4VMcCi+8OlkaARJG3pX33cNvucarHANpV1DJygNNJPHNMZZd7TvR+Xci8pRROXRUXnMfTThYljJrPFZ'
        b'dyzGC+Rz8+8Wyt0ipBoyVp+2LHEkejAFzWipr3RFX9hA2Ij3PX6YnB+m9A25GnopdDB8OFwah37QvvG0bwoirQBJjPBoGVsWMKj90NVdIpIGdq/tXStrYCTrSO5I7pgp'
        b'rupa6WipPCv7Xni2PDwbyZMR1rD2fa+Ye14xDJFR3yJyWMrkLHl2zl2L+8kL7iUvUCQXI+IyMQ+9g0ZmDVuMNN7zjkYkHCsYz75TeD++4F58gSJ+Ph0/H91URsaNNKt2'
        b'huaVolARV0ajMLKMjiyTsuX8UIVbmNwt7KGbEFNWHrgAs5IYylMx8hGHxSvFloNQOMGE6hTfZ0CIxKi79wB/QEi7h8vdC8ZM71jS0Tl0dAGJoN1DaPdIdOnojodbKku6'
        b'iPlWBkeNucqDUtBkX6dw8n/oFig1kAclyd0y0Wc8hvmWcB96BUq4vXpKF75EB/9160yUcvCDknloTvfZ+ECraWVlVVN5Ta3ogUZp08qF5aKq34P+VHlvnP70Z85R87kU'
        b'9QJPfQ7etztKERAoeubHJrFYLDt8mvr7g//Ucex3GPR5QsuPGtaPZnN4HOYwQJwIidcUlcsUeGYxm8MHh8huIBhO5aSqNCv1YH/mpOl2C3BKDVuA3k5ScUEXPIrWhnvR'
        b'mjZZAHZmqkqzDVUrCoUH9TJVu8WgFW4Mm1ZVtSmbU1NKDjVMyuGFyYr8NjxVT5QZ8SjdvBCM8rH+13k3anlSujA5PXs5Vq3JTlIZvGdRZSaaThHgOjkoWFKPfZoQrXKw'
        b'Cch8vfwZRfSGZc14exVuRC+7slS4W4Be/e0s80hR3v7ZSar2hTipU7B9UTNWN41SC0Ar6t14/xT0B6G1cQFTsdu0w4UicFTTgA16CEVcwJay5xMkH71gH/SxYc54T4Id'
        b'waKnSpqrcjGN+7QbnnNE7/rVGzRBj0c2mQA16a3haiIbDkXd/uHW8fz0+reiDN9vtnqltM0osOaoy7KcW93yXzfZ8Bsetm7dGvcn7fOblSn2jf02/d+ztm7d4k5zpEds'
        b'GqOKfkocsX+z9Tdw59GFm49cND3i37H+4xrf76rf/vuR1zR+0wKfz959w/jRUtvizzVux9wxfHn/14mtryw10uNdqJ+4MedGVoV4zj/2fLE2fqJhl7523M+fG7SYrjTZ'
        b'ekS/5LiR6+7YnUvudrKCo67cd/jLCrOw3aOfyd4cTk6ey/GuVD8zq8LgV3+/C5wjnZ+9Vpjcd6if9WOpzvE//Drfu9r3h2qzL09eutQ4f77W3jeWOe6WBJa8vT/7rRN9'
        b'WkGufdWcsG1n6LllRdfYY4cPiD+pGimf+zfpx+Egxuq2l235vKN/SDLZWuzc9rnW4X6HHsdVn5uPHnm49KMLnpfknRkFxrXtN7LeaO62+O7L4QvSS+M7N8Gdy/st3jt8'
        b't6mifOtRq/LXWNlLrrnnv9zPy9euor50nbdJc3ef/9xVj/ebvzTL9/MHOWe++q+3N6y8wA8/Um2beS9n7603+bvye1bTrfmnquk9IdmBfztV8mcX/rdvyJx49+eEiL22'
        b'fSm/scfhkt4PD+4evOF931In5MZLKzYZtM55q+pk+b75cZF7VsWukVn/LG7Kjftq56GPXmWLlvV/JVqlvKtfkn7W6Wue26J7J6Lcz+SmmdydiOn6qKnIa6JzR0rA/LbO'
        b'dV/7K299lBnUlHfU+7Pl7Rc/XF/x3lcVH/m0B/eun5vUIfTtXLNyy896e/LSJH/56vF7Yas8Zqu/GaQzkGM7XF9UM2QmOnpti3X1noCVCRtiY7fPe01+4IPEc9/VW4t3'
        b'LVgbeG23sWnNa2KdsC/Guj6YdXwszeD1gYEv3ufq68rl4aPHPtW+sWZhwZkfvnPzLyjlfLzlk4isNwJKT/Y8XNNyMaHXyCRfEmvyUxb9/offXdqrH7Gj5L2azLcXOp27'
        b'cXjN2TWP9018/QfdQ+8N3Lmm5pO79ESN/G7jrPA3Fqxe8sqfLVgRG94sug7PHyjuHfm43k46+AP7TMDAdv/8NecONOeHH4/47ebBHVVvlh4++fJnX63V+WPmgtCzO37W'
        b'LV6oW7ros8gPfzgmOTv+xW+seaX6ovqVPK/H2H+7fTQ8/HwNPE+4B3bCvU90MsGgkNlKOwK3gKtYzTMCdDzRAXUBEvIG7lYGjuOjX5ekqU3ZpbZkI80ajoDLT1QQ4+AW'
        b'lRbiSnCD2T1pLYW3sZo22OE3tXvaX0B2K/TBDTDyfJ9ma53hRXjBiuwRrAcH4XZm+woOgatPtrDUAsEh2MrsaFyC21ZhL+fYxTkYdo3WL2fut1p7qBQtjVk1jo7gVjjR'
        b'ZrR0BdsmVaLxYTYcZnynwENqoahVw2AAjjI7hVLuah13PuOnCpwA+1D/dIzYcAt2FIFps9iehdXcG3gsirsCDM1lwa5kxp0CkLiAjdghFGVjS/Qv58NuRjf+FLyBdwEZ'
        b'n14rvMBGlEh7BRucw75aVU7DNmBnUlqg1WRKSVMf3iZ94iFuiXWEiIXsAlZibGgV3Eg2t9faaZBdKnDak2ibFrowvm+2L/dSKfBGwavMpiPW383zYzZut4LrK0TuyaAD'
        b'iV4krwnqYTMf3CK0DwU7wZZJB2j2oHv6jlwtuERKWAd7Tacp6teBjdg3wxE4QkrQBPt0Z6hfsqg5WfAMcc3QCneSEmzgQU3VxlMCOEb2ntj28BaQElqkasEDOm6TO2zg'
        b'3Hy2AyKdjMQlVy4UIR7uVVsJd3NQ2/tYYG88OED2dxxBO9yMd9F3h4GtGJHAAcMs0AmHQQezzXYCHIC3dITpjTgN6GtKBf2o7lnGnCUbkknpGWCzoQ5qFCJaMehFdNPU'
        b'Y1fWOJJ+ecIrcDvjXg0lQQ06OuVfDR4Do48FuIbzNfDIpNGGmQYbgiJmmGwAGxsIJRav0yC7w6hGsB9smtwfXpTL7FgdATvdcIMmt4ZBD9afvQhlGYxm71zQqZOSXug4'
        b'tQUMj+iQPbpQMIK9famWGOqli+BWtvsasJNsu4bBNp2pba62THgb9WZqmysdXnvMGNzZUwXb0UIEnp+FJ3ImC60mOsAgs+U9AKWgF+vwzps/pcUbDc6TKaQDr+hMNxaB'
        b'tZw3wet2aiVRoaT+aLD7iX2Cg+vIvi9RZzarUnNIhO3MnntXcg7WP/ZIBjJAfN1pBrEXglv6REHcEE2l3Uw0JvDUYsrWTG1uIez3nsVMvEst4KbKjUg7vIz4dxJvH6ex'
        b'kdC7GMD4fdkeMguVg9dQC+EN0DYdS+FVqG7UXEC03kE3OB6gErK2i59VdFapOcMBeIEZawPWupOLI3jAAK2PwF4NSr+Q4w1PaRKJhGTO+TiydptWKbyZgTEcsJULhquB'
        b'jHSiBhzFwFpUDWxLY4EtQlwlKovDsdcAFxl2dCICXptm3CNVne0INmb9P92u/O+9kfzO7cqn7AEzbyxO7OepqJE3FrInOVsdv52oNiVXJrAoG4eu4gmqkDPL6REJO+JV'
        b'eqfzOSboFg7FXKW921mrHqtum14bsTpWZo2kLT1lAfcsg+WWweiFXxwnjlNaOxANXVn+PetQuXWo0tEJ3/4E66Ymjjvf9aRTShSeJQqHUtqhVG5V+tA3iPaNo32T5b41'
        b'4/l/LHytUD5vsSK9hk6vEavLbT0VZl5Kvrc0QOY8zBsWjjnf4Y0n0DG5Cn4ezc+TFyxQ8BeI1cUrFWZuSp6Q5oXSvCg5L38s4ZUUkDLeoojLp+PyUYKWTn2l0HdgmVwY'
        b'O9IkFyxCLRHQKUXysup7KdUofrXCzF3JD5KGj5iMWo7a0MFYBZafS/NzJ0t3cO0V0A4+tEOg3CFnxH80nA5Np0NzxBpKXoDUWrZiTE3Bi6d58XLe/PE58qx5dPJ8Vb18'
        b'r4Fgsqkk52eMce9o3dFXlfnQzrlXn7bzRZTlCfGOSpiclzOm/oo20B4PUETl0FE5qiJQQh3azgsltHXCipRBUq7MeNj2nluU3C1K6eR+NqUnRbpC4RRIOwWK45Xunijf'
        b'ik4DRNzhCNo3ifbNoH2zad/8SZI+RMy1IkqceJPGNnCCUje3GUkgXw/tXHp1SLuU+ApViy5pu6Anv0Jou0j8S7fXgLbzk9uljnBHdUb16aDUCS1ukI04AW8BWflN6C9n'
        b'maP39v9oWMmhnN17M2inYLGW0oUnqZA6Dwho9zC5e8YYB/0lv6R/R1/hkkm7ZIp1Hlra0pb+WE++kqV05UuapPHda3rXyF3jZUvHoi/Vi5PESRPqlJsHikmmPcJpj1ja'
        b'I5H2SJN7LJRjNeJiOmuhwrWCdq0QJz20dJygTM2TWQ+FfrICvKFYOGZ+x4aOnktHF4oTJIGdmUqBryxhoEQuWDCyanQ9HZlPRy5AMQGdGUpHd0mgNES2Su6Yij5jCcw3'
        b'mi88D6mRdH6fzYAN1rpXOvlKMpV2XhMctnO4MihsnK8UeE9w0Y8JCgUP/UOf/BDHT2hSggBxfFe6OF1pbSfOlZh3lnSVSBvuWXvJrb0+cXKTWkgtlHY8VJp7LEvp7Y+1'
        b'eQcthy2VHoGoHHQPFYTCh6HR038+QqXHsR6TUByPqlGnHPgTlAbuO26f3C8O75AXsMbjxuPk2fmvpt5NVUalYo8TBSwmRpk5d/pPUobAh2kqIwsUDkm0Q5LcCjPAzqlr'
        b'1X1b33u2vrIUhW0kbRv5iLIxL8A7Tq4etEug3CVqxF+cqLR16VpH23o/oiysURWevhJur67SP0rCpe18HgZHjdrSwenjK+6uw14kghbi2/6I8L3htKP/iPGohdwxFn2U'
        b'7sIBd1nBcDHtn0i7J0lilcIQacVArVwYhz4j+cz3BGVEWo9DKVvp6SMVyXz6VgyswHthc1nv+0TII3MVPnm0T57cI29Cm/LyoT2j0FDj+TOJfftWDqwcse9fK137fkCM'
        b'PHaBIqCIDiiSexVNcCivsIcCT1oQMdJAC6LH8u6U3hPkyQV5Sg+/h6FRoxH3QzPvhWYqQrPp0GzEEt58FhP2pUrjZM5KTz/pujF9eU6+PAp/lInJd9bIcwvoxHky7rD+'
        b'SJPCK+4fSjeBlPu9OuUZKg+dqxDm08J8uVv+QxtHsQ7+69R5JFLHUn2Cg8U9I/qnba4ZMuoF87jP6Bj8T59ehs9srv0bD6v3sZpC39RW2gqsp2CJd8L+48F/TNHhR9yl'
        b'QazOZ9a4BV9vxcE2HPyKggcmpdhQbUUTs1dYiq3S1tQtIkrljdtxIMHaX24clFRDpST8QHe6Tu4DnWnar40+ODVGnDf+hoPdOJiNan+gNaW090BDpSH3QHe6YtoDvRkK'
        b'X0QXiKiMEIb8x9yx/RtDAy/Sn+PVYHJ8nFFD42OGXe9APCzQiyk1w6eBLvZpgAMrypkn17V/qGfcWiB2lnDEltIqWeyI8UjzWO7I0nF/eU6BfN4CeXaRvGShvLJGvmSZ'
        b'vKJOHlQvFyyX6zUo9BpovYYJdilLL3iC+n8VYocFjawnFcVxZngSSMSeBJKxJEbhYxK2xiFxaOEgNlMaCuSGAqUxfi5Y+KIkFr6PcdCaghKY2nYsVhq6yw3dlcZYxpsG'
        b'owSmwY9x0JqIElg5iVEtnnJDT6VxGEpgFYESWEU8xkFrGkpg6Sh2UxoK5YZCpXEUSmAZg5uBwsckbE1FaaY3NQ43NYE0NYE0NYFp6vQ0uKnGuKnGuKnGviSBkWUHqshF'
        b'buiiNPZCCYx8UAIjn8c4aI19qgT8gDImjyYUPiYhKcTMrmOl0pAvN+QrjSNQGrMonAaFj0nYih8v5vZiTaWhh9zQg2mJOW6JOW6JuW9r8lNE88RE88ZE88ZE836GaBmY'
        b'aFm4FhQ+JiGhm7WzOElp6CU39GLSWJM01iQNClvTJzRZemgJ8ZxAnaVnha+eCdQXcLCLhf+NkEEPk63+m9nqoif7ZMPw3KQZXnMoVasS8GYgp6eMO29GwSENoqaHDfVT'
        b'Kj0urWqNKZU9tf99lT1d6lmVvZqM5mycFQzDHnAAbPP18vMJ8Pb3BVeBrKmpsaWhWYRehWWo55fgFfTyfRkOGWjqautr6emAvaAV7IL74aHcLLgPHsnnUvACvKajA47A'
        b'wyrqJa4l0Ot2PraKh/F0HMoIHueAi/PhdXBmXjMWauAaOFNW34Ah596Utz3oZUwbbwV740kWFHBAH7gINjeizBc5KOcefQKZDwUD2Pe7my+Sij6UD2ro1mb8Lq1jFzBZ'
        b'KScTbmEyHscZj4DzJGcZ2FIGT4A2XzbGuvvCbjDI6FwdS4b7UIUkK4syduYsAqfg9UKK6FzBzvkW6A19ly8ioB/lB85kkurgIfvoJ90sByc4s1F97ag+OGDImNM+BDeB'
        b'Y6vhbl80XPwp/xhwi6muI92E6SPKuJDPYVPGRihbsyMhjPfa/FLQ4YvWHQFUAHqjP96MN0vUVhozVaEs8Dzox5lYuK5e0E9aCa5giGCDjS96KARSgblwF2kl2BgfrGql'
        b'BuhGFAHXOODqepQRMZ5pZSfYAmTw9DxfNJCDqCA4mkZaGWkbwjRSwxFXBc7AA4iUg7CbybUJ7l03C1wHWNc/mAoGu5rJSZOahs4kSWC7TT3HQcW8wDJG3WEnuLIkEpwC'
        b'Q4h5IVTIMnCCVOZoOYswfHOjHZsZK+1gK7zOMiJ9s4cj8Da8VYO1O2OomPlwhFFa2gmG55DaUFZHQvwMcBher4ddpLJMOID+BsEgVk6IpWJdgIS0cQ48Xs8nI5MDusMI'
        b'8c8Yo74dZDXjp7G2SQu4sU6EuB1HxcHjFBmYWRgjyhAS964Z7tVYSIiJKHkKHmdo0p8Et6LBhBVc46l4NLmkDL8v+yUTUuKc7i0asxnWlYWTXFmwH9XdB66IEMsTqASw'
        b'bQ1RPgI7zNHsY3rHkJOZRxc56Tqo0gNQzFR6GZwEHWprRIjviVQiuIAGDNnTup1vQLKAzdjANzxWCEYx+8+img3jyEjThmfAgbIFIsT3JCoJnq5jRkxn8myGFzhfwVow'
        b'GqbiIdw+h+SzzF4GLy+GmPPJVDKUrSbcgFcXuauai4LQMkwfMv2KRKShQjTzhlagOYFZn0KlgN16pJ8GYCTyCWE9J8UFmkiH56A6d6kGXGJhNDwAzsMhNlZPSUWtGyTV'
        b'hhuok9ZugZcamWxozqF8J1A8sd54CG6GN0En6swQYmka+oO9hEJwYAWUTg4fVN5NA1IE4ak3jxmul7OFcbAPDiGOplPp4BbcQmYjGw29w5NDaDO2G3kpjGGqhwvJuBTD'
        b'B8FNfHaCuJpBZdS5McQ9aLF6qrMa8EIy6JlkSoKAELfRfC0c1IdDiJ2ZaARLOKSX/OjZkyNIw56wQxcNyOuoW/tIruUW+bAdDbghxMssKqtAgxl4Q0kOTJ6YyWnVp4Fm'
        b'VRkj185HwDOWPlhrM5vKBjfgCdLENdF1zLjZhPmPW3eIA4/BUXh9LWwjEwQMg10LXUN1EB9zqByjAkJNGySVThB6kHxhDPO7wAC8ngWOMhUesAFnoSxLh43NLuRawB4y'
        b'ALTgLdA+NXJUApxhZRsi43WttaSL8Iw/vFGboYOYmEfl6cIhouSlBbbHThFUJcEZIXc6GF43s2CeNUcXg7314LoOYuNcaq6JJqEOFz3ItpMMYEsj4d5tV3h9ARKLuJMs'
        b'3wzQl6mDuJdP5cNOlcJdn4a9qoFgE/Nc0vaD1+3RXMT1OC0AJzLALh3EuwKqAI66EpU37QLQSQY2B61wAzlC0AOvO6AxiGsxz4TD9gE6iGvzqHlW8ByRNTYi7A2AeXCC'
        b'HtAJDpKpSybTKtBGhjUZ0ltBL9ZNQj/nU/NBfxgz4DvRk3jrBjAI2hGDCqlCOAI2k+ZV6LPhoAVoR+RfQC1IgycJV4JT9eFgHjyAeiqkhOAMkDFyZQg9WDtKZsEDqDee'
        b'lGch2MlMiR6XFrgdbM2liBoovAKukvuLCoDMApyDB1DpfIoPdsJLpHibNCAFJ8CRXER7Z8oZnF1PdP1gK2r9SCES8gdQ570oLw5sZeo9DK6GwRsL4QF1og8HZaHM4JHB'
        b'bk0kPW7kooa6UC4WWTxt5jm8Sw8eYAQkolYakoZIYKFHOJIBrczk0aBQuyYXI9qIZ6oHrj+8zYjKocaEKSlwCexAi45RlSy5vjiVYfzGArCb8J1txyK5d5ah6TcMDxB5'
        b'AKXzsObipJhugf2chYw8CIskCRpmw45J0ahhnQk3T8rUDXDz5MKnDT27SCuQBBsl4gQ9lm+hbrSh5x0BRfeglU8bM85xSZV+nIWTohktiUhfUoAM3HwyleCeWRoxqqHT'
        b'BC6RvsThU8ZJERRL+gkO2cPrbGMeizQWSNA0PZQK2zxgWxJ2UA4usiPBeTSxTzd+RtaUHY1RPG2iU/h6NVFJpLwSHObZLfZnFA2/XK6HtQ/dvFpO68WGBzA3f1lItA+9'
        b'vFwCl5bb85mbl8uMKHzK4RXxmPeLXS5zU0tfjXE24SJqutBYyNwcW61PocaZeeW/W6hIXszc3JWtjte3hl4tH4S0aAqYm+KiWRQSDUFeLR8ufslqHXPTaBXRp9T0arlV'
        b'dsnBkblZaG5CueGKbGIFuqWWzE0HbVXt+X9Y9eNSC+bmIS+2qpubcpqEkRTRFZ9VMQeNUFT7+h1ZawMNKR47L4FELI9VFRGwTvh6cwaTeoijwbRV/YT2Q/8w6rOjnfjf'
        b'q5Gkgtuaqp7MuRp32zif+syX/PsukpntQ/AUeppcgGL8cKTqqfoa2EGmixY8DnbDQSc+mkUrqZUoUZvK/wuWjuCIKVb3V407sBFNt6mRB4ZUvj3WaKm6UfKlSztagZCb'
        b'If4q0pSsNTA2cpypK8qlVK8UYZg0rCPUIqwrarqO1caWUM/7h95wUP5zU2XsY+8yw9bMVGZBHnBr6iqrVvI4RJu0Ec9qZl8Eu3yaMuaBh/dqG1FFeV1pzTLsg+qJwmht'
        b'jaipon7Z8ggDbZQLg/T/sZGSe+YynzFvGfeqziWdkehB/WH9qdvkfY90Nm/JPEqGh6b1BpZuiBFiZEZGjWnMXK4I70Lpf+68O+/dutxE4+PmrzSsrX2l7S9Lu8RrXj8t'
        b'+OFn63tzNLkPnAzdhO4latG9muY2HZc/01NLSIjbaegZJtb428KOnzi/6GyIObK34pVXgu32+L2+qPrvJUvf+GrdLyGPPX5LiL49/udcL02Pmsf2SV8ltgZt9FJEbzWL'
        b'3xXUGtSgCe+oJbQm97bWVLbO/7j11LjRK14ZHmXWDeEBhoEL39p/5s3q2g+/0vgl6b2dy+58rYz+RSvSaMNLGR8Jv3L55qWSjyK+crUZi/7I3srF5qXsj7ytXE+MJX/E'
        b'63I58dL8j9TWF9/71n89/DZox3cjG5OL7tiObH195G9vr7p43qf/+q1C6Z73C75e9I7bn7y+fgfmNQ+s1b5w6I+5Ag/RTcU7a7Klc774g+fs6L9pPBgy2LDa5OiqH35+'
        b'MHSs6OoDi0buf40cDrY43qkn/y3E+x/nZn944pW9X0N6a6Hfy9v1fJY4njrD35Mz++At7WvHvhW/9Ke3azt/tbDeW/dB6rsbCt7pOHbu5ntG/SOv6idJP/j2s2z2Pc/r'
        b'r7pzTN4Unfsm3KPwTwF/OXrOvwLSjZLa3r5XBqNjPvj88M/+EcJ3pFudrveXV8wW3lh6d0L67ktcR+9QN++2uzcWCUwrZd+dMHnltzDxN9+nH076emuQeF2tzbGigkrn'
        b'M3m8LJ9Xgs4VV2/dvPqBSflfZl/c8Uve6KHTCV3X7t+89saSGyuMvr12zLJO7+b3tvtHdD+sv6ofu89faPPFg7OJ8NxPN7tuhQQeW/e2VctIrusrlkNnYnj543+90KH7'
        b'xxu3q7Z8xNm94eiNb9adbjhn8/cbx0r0jpWd7/r22svfVlu9NJCeEpPwqW5ojqn1EqcF1pUHxIN9XtdqC2d/32pr++uhgz/cuMJLLq/+pHf1h74uy7bzrxb/wePPhe/x'
        b'Xj34+v7mep8Pvx/ev6DnXO25n2+EnA/61v3Q2WsFjZ2NPV9k/3nIp7Tx/e9fOW9z0fzVssZt2Z5fdQxXFr3p9867e3x/Kbz1ie+vgpO/pd//oHnFu9/90qV+QjfpaHHE'
        b'u18v6zm7Pdx65VlQT+9JuW7zXehSf89TpT/f5u29OPcvq/7g/Nfdx3ydT839QZxz2bP9+pxiv8tLrS4GRSysS9n27a8GfzZ1Ah1f8/QJOCJJh42P6dPTMrkUdy0LSsNh'
        b'rw88TYAIRTEC2E7sllNqSSy1IjCUBXcxaJTbYLAxFe5Bj7ZUgQPc786idOAxDnsBh/F0cBqt47H9b7QqQe9JHG0WGAE93ij9dnKyDc+nATF62oGBFC6lVskCt4rAKLg6'
        b'n+gozV61NjVTkJzsATanJatROi1seGwVxeS7bAW7pysSsg3ArVXLm0g+Xaf5qEhP1BS1ZhYcXIaWo61wC5PvODiBzU7A3VwKrTgus8EQKz8N9RJHzg7zxCqEU+qDq/FG'
        b'w1wwQsijxoaXGFvqbC1sb0CdDW/OBjuYUs/EYdcc7QTkoGbK0oTDoCdF5VuEV2xOgEzYLwS7hRWNOnuTQX8chj2JUw49CkwxkgI79FgP23mO//dKRi+EAiCy+/kaSTPO'
        b'+lU6SU8eBqunXZMDfg11lWmnpnQWZRLDao2fYBua6SsNLcW5Exx85SCQipgrv8gxI3L1kMRy8RWJJVckFl9NqFOzrFC8BnPtKEQpVNf+USyUiPzQZBJpMdckkeqaSUR+'
        b'aDOJdJhrkkh1zSQiP3SZRHrMNUlErinmBpOS3NFnUhow1ySl6ppJRH4YMolmMdckkeqaSUR+zGYSGTHXJJHqmklEfhgziUyYa5JIdc0kIj/mMIlMmWuSSHXNJCI/zJhE'
        b'5lPdMqO8fMeMlNZ2UtHMrwnbqTQ4aE2acJiyZd8bqjDypI088Zaxi3KO5ZEl+5dIjPbVH6zv4Chnmxzh7+eL8TG5ewdfMdufnu3fGqu0su1Kaktvje8IUJqYHVmwf8G+'
        b'4oPFrQkPZxl3GHXkiyv3FStmOdKzHFtjlBao4DC9eNYjEnao41MIW7GJuEVS3rlSqi5t7NNS2HrLvGUVIw6D1QrzcNo8fIIKnoVz4LAjWmlh1RGrtHYQz5X4dxZ1YW0U'
        b'kyASiFlKM8uT2ke1JQFSe2l8n6ssuo9POwYozAJps0A5+Sj5KK2/CS4Oh2IDpZ2DmKt0dBVrKu1dJCYSkUQk9e1e2btSZt+9VmHvR9v7TVA65p4kEEcrHZwl5b0u4tiH'
        b'tsIJimPtiZU6GmSz+kQDQRJNieZDvlCiqbR1kCw+ukG8QRY0svKeb6LcN1Fp53xWt0dXmt1t0GsgMVDiZCi1nbNkoURLotWrhWL08VU3+q90dJPOwn+9QahZZnYn9Y7q'
        b'dRp0GaDWOvKlsdIcaWxvuBhXIxYRY+wru8N7w2U+Ckd/hW0AbRsgVsMJ41CzEmRxMn9pGu0YjNO7YriHs9LK6Xt1CrXRrXNZ1zKpSCqSBfWtG1g3IlJ4xihsYsWcJ6Tw'
        b'717du1ph70Pb++C88SwmRIRw9ZBmIyo59qyXu4aPOMpd48aMxPES+84kcZLS1v7kiqMrJM2d67vWo8aYWU/rgp3DWY0eDSm3W79XH5HewUmsoXTmSf0l6RPUHHPMGRyK'
        b'45QuAhmre6k4UengKI6dYBtZx7OUbu4SrtLF/WxNT41MZyRX4RJNu0RLOEpHF+msnkBJoNKJp3R1l6gp3fjShX2aODFPGt29CCVxcZ+gNO0F0maZSCYa8RtcNbzqnmeU'
        b'3DNqLG/cWZ6V/arrnWJ5/vx78fPl8fOV7p4y+z6eJFbJ970Y1h82ojYyd8x3ZP6owfhsBT+N5qcxuo6injWSNUo3gdLDWxbXlyaJxxcxfSmS+Ak9ypX/AjUi2eEseJ8v'
        b'nFpTo884d7xivHG84q42+qHwzKU9p7BK8xX8+WikObqdjeiJkDmPaA57KhxjaMcYrCCDCMX3khnJHGRGAyGyJlnTSOLguuF1cn6c3OmffiZcMYUfaVLO7o8MCCMiyUTR'
        b'wvNuogm9qtt1hE071dd+wKlZtuiFDvRF2FrYk2N75l3kLFaImfbIuYE1XvARN3nkiNJZLNYsfKr+YsF/7Aj+Q9SSGf5ytf8/6t4DIKpj+x+/W+gdFlj60lmWDopSBAQR'
        b'WIoINtRIRxRBWRDF3lEsC6IuCLIg4qqo2FFjyUyK6bvmJm7ai+k9wcSUl/Leb2bu7kozMe/58v3/ZR3YO3Pnzsw9M3PmlM/RntgINJvBiHi5hiRMOAPPRpUa6+Lk6v8d'
        b'cXIz/zRSqkvm2LCYK3Bf2AwsZgO3lP1/CYzJGaPdepnkdPlxIpEdGHJY+RW5lnMoEvGzDFwB2Ni0cZYfBvDanp7tl5Kak4J5v1Q9KnIVOp/v0fcDZ93LX7rjwZXgg7a0'
        b'jT74QgSGVt0SepDF3dES7TLXwT4kn/Pi+hXj2p+7NQ3slIoL8p41bCnZfO8gP9pho8OEcOojO6PW4GwhmzEAvQG7fMXa6Dz6MaADStn2K8cTW9kgT3B0mNV9cMmQqFCg'
        b'30XIHjIrMJOl5cNMihaWFC1eQA7x9W4LcDDqBRi2+8EJfUgBwp1hNDQ8UxZOQ1PUVrqseZx0nJpne2Bq89Sm1JZUaeq7jj5K3yEhVez5UsMh81jvLVb5WLMY61CYycrM'
        b'09N4nv5Zi2yx0KCC0kzesmlo8lrg+Thm8tjmKNYWM+hmhyuDxQGZ2OybW+5J6TuyjeHmtUS6kzrXRwSbM9lUJrzBtkK8f6sXIann8hmpm+WMhRVZ9R6UkEWEqsuS4FVx'
        b'esDazEyMc2eYxZYEZ5PyR1MY6dfN6roAubCMCe4gz0vNMVu6rOVNDsWeyaJ+DSFiqp/cGNnV4Mzl6UvzJFQFdpSrN9Gj+JShOXqm6Zv8WLM8SoJlssFXfsuZUftDHeeJ'
        b'mRRHj+WteIo8rTqTCRYbX1Ru+llIDuNW2B//1odez7ExSqRJQj4p936mRuZlXmc6JWQtU87fJe/D5RV6GB7V/K6CIPzWLvr+w4/RnT5XaYpfypbgrn5Vdj9nhtny9HNm'
        b'S3MpSj+Q1eK1T4JHc+GP2cSo/Jgf9gaxOcO5vfijt8LJ+UOCh3T1v8xfs5i97fmA59E8M2Cxw75eT567drPNa3w8eYWUMORyLrkWuqv3teKNqNP+lH/EbXIpxujfjX5P'
        b'oeVoPjX/H+dJ8774bl2jCv3+4ORH1JbQdnJNpihuVKEbP2wtorZGszUBgmcWwsZUsF5IMMfC0Tijk1wa3D273CdoFVuC1SJxB6O35J6pfDvE0lv4vIf3m7utnyu/sryy'
        b'0fQfv9h/3vy75flx+bxF63nPLjNUdnepxn12/PnG8E9zfomNvT2zKC03IGF9TX3dt9+86+J2dsEzbsvjrgSf0ht0mx6e33bwu8rSzEV2V9Ivf7JzyYrvr/lnzPne0jrJ'
        b'SSib+MUve2sX9lqe1HtzSlFnaOBL5YFvZX+9pXv35B/HxR4s+5e6fe32g6efK86YdPDfa08A3s38wZz2uFU9kp9uvKCXqH/71ZbwHPr5gidc3jX9KbchlH3hJcOPXz9a'
        b'9GKC1WvTkm6F/HhvbVBUqJ6P9O0B2Vd35AYT1hd+89vxY4lmlxSBb52oOw+N+NE3Dh/ZJf2xZEt5tCgwe3JM3bev/3rAv/uzI7vWyoN2HN0nFL1ZXNR+5/i8J6ek7g17'
        b'iv5pqcOLLudMww+vbnrtuzVeR3grvvjspe8ufGprm3bi8JqazHb/Ww4F178KUXH3yS4fN769Sz1p4Kcok2cGj+54rbTZeN1J3+O/x3z5W/9Ps/71ZuUXy37gPnf+vd9j'
        b'o4x+uFU755V3g2ZYrImCPSfDPxK/cT/3hx8NehV5q1+oLYp+94mTSy++Pe06f8LmxH/vObT2zowpko9qrT5apbfXbkHcj869rK9CGta82yY68b3f5q+Wv/GPSRZljb+Z'
        b'Xc1/74O592KvFF5qPyc6+5bD8dKI1g/vpjq/0iexfu3zSebuV0Ob3nsm4sJvefNuvyfunfQ7J3vuQNKsr4WWRF6Q4Qx2i4XYNVMfHoY3KP0ytn8ivMAs5xsF9ujg7wt7'
        b'xAy2oSGQsqu855Ebw+AN2I09WDICqtB3bigL9I0HR4i0JdsDSMWwERyPwWHbdmFcO0PQxV6rn8aE1Ts9FcolNcuXm5mD3RYW8KzpMj2qDrbYwUMc0FEMTxPxSP58N0bi'
        b'MgcjIWGhy5NAYUCy6pyw6joD9GGZRhobbGZNXQc2kKzs+pWiNEbEAc/6U/rT2TzYLyBZM8CGLEb6Md6KyD9A9yx0F5k7Mti2UJQG9tYGaoQ8RiZssFcPSBnp0WnQCBrQ'
        b'vUKUTdnBdko/n+0JNsFLzDidgqemiIIIjNR0SwZICnSA3Ywn1zZwFawXpQXCBnB6ZWo6WrxMwBk27NAHzQyYT0OaqTh1jVuGZozns0vgHgmT1Qg3iLX7qXs92lHZ9lmF'
        b'jKdW2wq4iWB9pgv1bUALpR/N5mUvE9r/HzhTEGTuh7hMaCQpD7bI+iF/k736KY5mZyydxuKaOQxSD0uMKVuHhilqCxulhZva3ulAfXO93EuFA0f5Srn4wqrmVfJIlb2I'
        b'thfhCwLpSjmvaV3LOin3rpWDlC/zkuuprHxoK59BKsDMUeGh5vEPpDanygo7y9vKWxe3L1aE9ufS45KlqSreVJo3VcpS2/Ck06UF0ukt42RTb9t4Km081Tw3qVjObspq'
        b'yZJmIb7hwPLm5U0rWlZIue86OMuy5Vx5bZepyiGQdgiU6qvt3KWL5e5Hfbt9FX79ySqPaNojWmUXQ9vFSDlqO3sZR5bQqicrkhm1VKALNnYy7+YYaYw8QV6kcO8qUST2'
        b's45NkS/uyewvue0VrfSKVju6o5O+o4vcWOXoLzVQ8x06DdoM5AYKOxU/hOaHSPXUNnxZaPNE6US1s69MrGCdNjhu0M/pr1CFTL6ZrPIT035ilXM67ZwunaJ2dMPht7B9'
        b'rm0kPqDnqdyC+71U+LD8811nd3miPFFh0JXek65yDsHFvWUiecHR0u5SRU6/t8pnAu0zQeU4kXaciKqxsR+k7K2i1U7OshxZriy3PVKaxMRRq2md2D5RwVGUHDNROUWg'
        b'q4gRS2lOkeXKk1rnqnhCmidU8oRqgZe8pstEmiAtkZZKS5tSh/Fraic3aZI06S6qfYY8XDanPeaOU+Btp0CVUzDtFKx0Gtcfhiq2FwxS5rbRjPxC4E7O1BxF+TGLATuV'
        b'IJ4WxOPQbgJ5WFuULErt5X00uTtZEdFvy7h1DLirvKJlU9QevvhkzXUJUvv4kr7m9oerfCJpn0h8pvaS5yisumYowuVzemL6x932nKD0nIBP2Noz9aARuhXRqrePHL0/'
        b'eXlPOqrTS3g0ozuj32fAS+UVR3vFPfRSend6P1+Fg/ZFoQuWVgcMmg2ajFqMpEaDc1iIaAnlkuQeTu5Tw66Nlfz8889j5uWxKEveIMUx8xs2U8aYRyNnmgVPaSFAl2Uz'
        b'pDgiAnrzDWLC+zxlnjpObMF50YIrtjF40Y6FUoadNn2Lu7SgZuFb3OKCmoK3jMpKahbUlNdU/DUwCQLWPzRiGMOCP0WOyg/WFB7mtvdTughhJZjfxmag/13y2PjyOai9'
        b'RewhRzvdeXM1xZw3Cay5HjozU6UcHYz5SMvOvwGRX9ewYcEYNEr8mWsmirOwzyBR46N9yxp0G4JLHLjR0a1c+PL3HAKsW3PzxMEXYjo2bO/a23Xox73H9i4z+zDMR3/r'
        b'6/GmrKdM28uppXP1Wib5M1TCGfnC8aFXt4WYYap5sIsM/0o2EtwscuibrglDWqwoV9pMUNlMoG0mKE0nDDnf6VcD7Hjx9EO8L7BxnsaXgiGy5zCRDX/kDExn1ZTWc6Js'
        b'OiIzF0wqD08eGw1hpuP/kzS08FFoiJNZPvHp4xwJllN4h1082PWZlkQwgTjYcOAiwVYqeStva77+K6bU0iC9zE+OPhKJSIaTiGQUibhpSKQSkYiZfUOatEaWqzL1oE09'
        b'lNrPaCqBj0olLxAqGfbU2cOpZAmmEj4mhocnfwOVrMVUwtFQCYuxJS/l/o10MkoupzP5GEInxkz0Dz44B09pBBjLwRYuI8HojSdn/K9Eruxizm+G1NL3163wPsPYW5yt'
        b'5lAtk/Bf+aY/zPJnLh5dw2JHGHBQyYIFkaL5jGwEtMP1sC0HnKSwidQUsJUCh0ormFAhYgMqvxARjCDfNDU9mWIsHvebBOUEgvWgF+4XpaRyKP05bBw4urn8Xw7n9SS4'
        b'zxv2H1szLdoYhvBeW/Wvza5dl553eOtC0U3pmRr/H1nvdM39fFHUiuebPX8sadi0ae6mp872/LT5iV92LbTO832xw7ien0x3H9m/XB7w75z3F/GWhh98o+juS0Cy7ITn'
        b'+JOJgj2Lb3z/2VuS96c4qXOmv5z07PfvslMj5/waHPz89csHnu/9+OQqq69Pc+dHiDf+XvG5avfyZ4ouXe+u/ujzRN+YA/qf7eR+uOlXdvdR37V7LggNicJ8ETw5RRTo'
        b'lxIIr+Ww0cGljR1o5USOPHHhYBs6+wFF9tCzH9gFzhDHcnCBWivGlmPgYAA+BGbh6AA70UkMbIEXmTPTtYq14gCMejBE+70SNoFT5MxUsCwenCAHNbidAhtYlP5atocL'
        b'6GPQO/YUgyuaiOB6lOnUcqzFNp7IKLEH4EV/UQqWcVyAexFRR7LAKXDJinjrr4XyQK1u3GyZBlwXHoMKocGjcBh41mvAKZkVxRQv+UuLSxdg9qV+2DeyntCa9aQGbzn8'
        b'A1HNUU0xLTENSWpLF6mZrLhzcdtiha/KNYx2DVNZhtOW4Q0JH1vaSZfJvFWWAtpSILeiLT0bEtQ2tugeaxvMjoV+bO8iK2DYsSaulCUNVVvyDpg0myB+OaF19h3ngNvO'
        b'AYpsFYlxq7IMoYlHzKABZUO4udBBQ8rMak/6jvTtmTszGzLVppZ7xDvEMkN5RKuFytSPNvVTmvqpbdykYS2RLTFyrtImQF6DEuaDmoHZuSGLoEH153gkuH8I/kVGTsOa'
        b'MWvh63gtHDZgc/FSWKdbCiWPsBQ+3vUQMyTDFh0jze/vn2Wh9dDsAFVC5bGKqTx2MSuPw6ZaOC2mLQal7D72cOuyBoroM4jvDdZplBoWczYbDl/v8rhsqkSvmLuZKtbr'
        b'0+9FxHJCtxLn6ZM8A5RnOCrPgOQZoTzjUXmGJM8E5ZmOyjMieWYoz3xUnjHJs0B5lqPyTEieFcqzHpVnSvJsUB5vVJ4ZybNFeXaj8sxJnj3K44/KsyB5DijPcVSeJRpV'
        b'rGdx2myYZ0XKuZajvaTEavjY9rB2s/KsUFmsXTJC+5YzKm9d7EIiR7i9ZZBRUIn9MX8JNB4qk8iZMi1BsITJEpAIeUHD8oUsstsP2zAxgZBdqQEl+wyHRBzSvXzCYhnp'
        b'ts6RKq3/SbShXzYNazn+l1pZXlNeUFFeXyIhgSmH9ba8UlKD/VCDjEfdF7W0oLpgiQDPzygBDiqI/xLUVAkKmCqmJSULSssrSoJG3TlqJo3cvl0zawlkyRZzsJ6s19Pg'
        b'OdCYArdnBc7UAK+Bk7AhIIhFTWUZRObBiwSpDbQYGZosXZaDcrTFpoNTuYbLzZbmwoYMEmYDbUdFAkNTcBCeI4oJdzdz2BkJGwN1cWImGTIy8c1w8xosRVyflw73iDPw'
        b'LtXKXjUfMB4+PuPAdVFaRlAgPACO+qcRFzwbXw48GG7M2MUenh0tDgNH4fo0NsWCpyl4KdmFCVpzbYotFsx1wLZ0FsUuZIXOS2Oe2DgT9ouD0jICUtHTTOaBfVVs2AqP'
        b'w8uMU8hWMLCCbJhwO44PgsqgpgeDds5ksNuEcTvaBffiaD0nU1DDcCUWnnC3mDMbHBIRHoRlDY7jR18CO7FcEPcJXGKvWh1IctO8Qac4FQ4YZfijXDbRAYANq8BBwkv5'
        b'TXHHsYqYOEVQAbpxrKJ18CoTwukAaFwSugq1amjogE3gSdJjxCpgZJgdBWnp+kxcKIU9qZPHhU8uBldw6Cdd2CfQA/Yxw9HquFCD/8PEbgJbF+K4T92riTZo/zoulZRj'
        b'h+Oxmbp4BjMOcWA/euhW4gAwD8go95W5hCH7TKxHyd1J7DbTvT76WCmFORFf9A42iOCuPI4oaESEprnMjTH1iCiciPQgYHBxEsXEfToOLscsRAMLdz8IGwU6Qhg3mqsm'
        b'UIaxv4fEjIJdYAencC1UEMbRHQ3/BlGQeY42cBQbyKZMqyX43dvNsbffLu/oEZGdtHGdeG7kPTssBUcwoZADNHpT5lBuOo8zH3Er0vLueneOBO84M5JOnsyNzYIhlrHR'
        b'mW+fN/+8Lscybut7Ny1uFbrTXYkJ6d+ATzIDGsblOLyw5yPjHV+L23w25h2vefXTn1bXrXll1X2Wc3pxz+ffTLzJWndjsY3jZT296MuvpK+bUZH4yt2nw6r3/Gpw8O1U'
        b'8P6SCVnPS+6U2B5+8zvzWVtrf3yhPfAzz+DvVjz50mvyjUeujnsFeCQ/wyrd8uL0oENf885sfefEK1eD+5bW72rP3GIzrvqKbWbnj9nwy+wnppQo07wXTWs6mfuLmf8y'
        b'qzv+pv7tooPR3T3ZXV8Jet90ervH/42v9MZ3zl6naL1SfSi+ZcL9m1YWqcs/+qdv/Nc3TwTde+WZb9odr05wO9Qn6e69P6Vy4htvdEUtODc9knVyqsGbt55954ZteFFw'
        b'uG9rasbr92n6GZ8n3sw8N8fq5Lf/isxIMtk4feP+f7xzr8P1q7k/fPrNrP2vvv/05CNfXgmmEid9viQ7Ka5SfDK54+3KtH/vUbLfXd5YafPGko0vTW35xPPW6qfnXDry'
        b'j8svDmREDGTMo5d0X3i74qjtpd9XtjXYcY9wOyRzvyicNWfX20+vvHTyq1kdNZ8v9/5HmR7vncT7P5t9WXbaPvV1oaMmEAhoQyR5Eu4hi56GQV2VwdiZ7gDN4LA43T+I'
        b'yTOBcrClgg17ePVEWQBvgD4T2BhgA49manT1hrCRvQZN1c2E73aBikQTMejKgTuFOuQ6W7CNawi3WDPw8fJQvon/KnB8LHw7eBpehBuJbqGkEq1FjXBPYFosuIKWTXyq'
        b'CmN4/yi4LQ80BuMIRmTNNElYImHDNthsQ4Dg5oPrqeKs4hwG9S4B9oIOBmzqDDwPG9GNk/3wmqpZT+3gIW5U7hTyTD20ZB2BbeA8aMwKQ0sqp4I1030Jc1zYC7YvAtLZ'
        b'JHRrOg5N0MkCUjQeZ5hsmYUrytKuq+YL0VO3cibAxskEFc3eHHSSIEp4XUVHuhOatdU6kgO6xDxGETNgCVtRHXhhFU1illbrVRxwCe6eyhToBQ0YNy2LUbjgjsMDIdmo'
        b'59OZt2cHDs1A2amapdXEFjZ6s9EblIImxlL2DPo5IgrCAQnAiUxtTAJ08RrphN78uaR23WpoYcSD1zk1s50YQDsPcJTkB6BxwmuSviHbAW6A/WR0C2EzbMdvBa1KSYaa'
        b'dckaHuHADc6ppPql4FA5QX0jS5IJ6IxFpAMv5cB2BsmsBzaVofq167954qpqTnIIvHxfSPatGtgtygx8EDYO7po8bO2KrzWwAturmdAeG0EL+kEjrtuQzctSQB8nCq2r'
        b'jQw1bArlM2+sEJ/xmDXOegIHPAm67UmJTCtwDLU3JRU0psNzwcyMsDbnoPewqVZo/piwL7BWnTAsI0AvMB5IvaWGV8R4KIiD0oB3fc0AXwwuytEKEuVJKhshbSMcpIys'
        b'UlhEGaHTSLi0R3bGtcUpIlROIbRTCM7Blya1TVJ4MeoJrF+JZ73r6qcUTlK5xtGucUp+nNrJTxar4KmcgminIFIdLpaCivkrRckq16m061Qlf6raxV3u0z5Pym0xVrsF'
        b'yNYocvv9+p5QucXQbjHooik2FPY96tftp4hWeUTSHpHoooXaWdCZ0pYin9Ga1Z6FLhiNviAIlJspik8vPL6wf6UqKIEOSlAJJtOCySjTTO0eJHdR1JxecXzFgLEqOJEO'
        b'TlS5J9HuSSjT/I8z3Tw7V7StUBiq3EJpt1DcwLtunviX2sGlk9/Gl/upHES0g0iqr7ZxuEc5WYWq7QXyZKW9P/rc9Q2S16ldPOXJ7U8oZvZP6ZuvdI5WO3vIx7dn4l8T'
        b'aefAewZcP8f7FEpk3HbTQXNKGKxYSftNHPCg/WLv+CXe9ku8mXjLilF0yczUHkK5b//ygXI6MkXpkarySKU9UmUGalFov5AWxcgMaL6f2m9cfyGqQmbQbqYOmDjgTgeQ'
        b'DKHaP6TfgfaPHkig/SehXAt1SCR+Ks0PVPIDH6W1Q75G0c5B+PcE2jngnpkB7oSBphOWlK1DS/odXthtHg4vEUyHp6l4YponVvLE6gBEUS3pNE94192bDLGTW+eEtgny'
        b'NIa2pIZqGyc8kBF4IFOU9gHoc1cYorBXu3jLS2mXQMWKAb2+dUrnOLWzl3wmejr+PYd2DkZD6Y+H0h+3AhtzC0NRd/2iBybTfnF3/Kbc9ptys+hWqMovg/bL0A7liptG'
        b'dGSa0kOs8hDTHmI8lOH9qbRo0p8NZVj/RNo/dqCA9o8nQxk2ET+V5gcr+cGP1t6h3/No5xD8ezYaVTSauB8Gmn6Q0cy8w4u4zYvonz1QRY/LVPGyaF6WkpeFoamEaDwz'
        b'aZ6vmhlPKfoZIu4wZXCZwH+Ey6RRUT1Ya/5oqVmK5SFSSisPmZ/ziPKQ/7mgRIJPc+1GYdRZ8wSK8xcC3S/EcRv12CQS95ix7XVjoA1r/7IxNnbF+SSsvQc+gWpPrTpI'
        b'pmEB7KsxWNVfaFMpapOQ9ZbBAkl5WWVJ8SO3TIlb9gNrWMtIs6pKBbiqgpra6uEt+wuN2sw0irugMKzwkVv0Gm7RKd1Y+SVXFJQJyksF5TWCcgk6r08Om6wbu/+wXeQF'
        b'fkj9hRf4xvBGOeNhKqouKS6vqaoWlBf/pw0hEUC/5/6FhryJG3JB1xBXTUMKasqrKgX/zZhoCMhowZKq4vLS8r9AQu/gJvnoSMgXN6miQFIjYGoq+u/btlnbtpIVJUW1'
        b'NX+hbe8Nb5uXrm1MTY+pYQYM8tmjN+uD4bPOX0vjNUPWBUTsTK3/DXGRxhWXFCIyfeTGfTy8cW5kSSBVCAqKiqpqK2v+m3lH3qN26jxymz4b/h7dh82//7JVOurSSvAf'
        b'uVVfDm+V91DBIn6VWqni8JYNadgDVeVyCiu0D1AN7AaOxgSfYlPbR0hU17CInJUaJWdljZKlUmtZGjnrmHkPV1GOZYKv/xDXAdJqFuM6UMr6Gx0HUKt/mT1KVov/kalU'
        b't7AEjX81egloFg2ZUNVo0lejzbZGgMimsqpmtLh3lMhXRzvDNftfKML0JPg02qD86uALE7A7QSNLf6PDhNcon+2psewPNy8Xspioi93gyAR0/tPJCsAFMKCRF8DL8AKi'
        b'NksttWkYqZsYyNJNS226Rj+wui8tK6khRzhsJI25qsJZLMpZ0B6n5PkPYfK4DJM3nL/D6E/Etv8vPOtbzMOVURoDxrmzEAtnjXmxkclj02E9xX5Eyw+qgfW3Wn48kscK'
        b'oo9fSymuBOsFYiwrdKZBe8sdPDlwxgeLBFvXZz67gr/XfYu7bMM5Pap5kt6z810RwRAMk63wCIYgf0AxLGd4gSGYerjpj41Dqp/70/cp0dCOo4Z2FiHa8RXJixXjuhb3'
        b'LEanhiwp+hlmH0LIyIr1qFZEj9KEH4dbjJRjmnLARPTw5LFajAjZjOrjMlTAK+LsGuIUzrVggaOhjM2EEJ51FoP1YlEmzghngXPwAthT3sFfypFguL2mi1OwH9GGvV2b'
        b'hDHJu0K3nNly2O7WF/mZRWkF7LMOi/mL+DmyT0P0wpf2sqinGoyS+s20s3KsIxUm8AdD+CVK6q1GDSF5bxnMe1NzDQdnz2JxrUSD1BiJOcsKu22OndwVeCmKlfbh+GMZ'
        b'PmzFGOsFP1LbvsEvdLGGpubg12mE39qYyeNdJ8bcmsg6wSVbE5doUCmN5c/fs0GVog0qY9Tukoi9pSQMp4e2o+HaS4lAUlNeUSFYXlBRXvwnisix7M30M3OTiSKIt2YV'
        b'ZWgUhY72guUy9ntU+bXacD0JnsPCyWYHXwhDm5U32qx2tE7nb0rw2BnS5LFcsKebNnoFU+6L4bB2KXtlAP+7pU3s8cWvLXKQ8aNaF6P/+1kvz9sVMqtnawFLxLHrN22Y'
        b'FS64XxcWlO/Zd2pr147GDe6NLs9mFbxSmjBg8dHUV0ypeJnj1/euCg2J1FkAbmSJgkEnFoNqZKDm4CJnKtgOthC5rWWCvogRxYNrUKFVYcK9IYxUd998eEPjIpA3XqsM'
        b'XAMOEIn0VLjLXJQGn1z7QB5P9JuwuY7cHctzEsMmDHz3QNnImQ2OiQkkRCVsAScY6S6XtZDLAp3lFcQ+J2o26BfFpsLtWamgj0vpV7A9QCc4Q0yKjLPBQTG6HKBPcf2h'
        b'zJkFzlZKhHoPl5lg068hJjeG5ZIF5E0/YCu1V8gsb9PMpHq0OvOdW9bgeStQO7nJItT2Ti2r8Fd3eXHPYvKH2kkgG4evryVfFV59gQ+u3+XxWzKUvBB5bs9cbOrvIo2S'
        b'Fcj5Kht/2safKcZ36NRv0281bDeUJmBvgbTmtKb0lnR5qIrnhQopcm/bhCptQrWPkdYMM5wZg8kY025miMVRtVB/KEOt7fmveA1ZTmn9fx/KZ/yv2A68MWQy3bIZC3R7'
        b'CLo2thaq/gK/SU5hWGE1jkdT3aiHX6z2AP2Wofa4+pY+c5J7S585R71lqD27vGWoPXSQZZUMi9Dsv9cGmFEjkLCZUVdjayWt4chiPNh57BHg12wMfo0TfcrctmEW9muQ'
        b'+SvNvFVm3rSZ9yB7DsvMZ5D6z1OMV+3zoKbl7GHozBMwOnMUBmeOwtjMUQSa2c5VOlttKVRaCpkCdriAHS5gF9WQPAIAGmM32xDsZhuC3YxSggE9tEwYLhOBi0TgEhGk'
        b'wFDs5giM3TweYzePx9jN4wl281CE6FiMEB2HAaLjMD50HIGHHlogCheIwQVicIEYUmBoRzAith1BxLYjiNgoJX0ZWmYcLhOJi0TiEpGkwNCnYGBuPgbm5mNgbv7EUc3A'
        b'UR74sbhALC4QiwoYGptFDFIPS+wIyLWSiKvlE+UTu6J7oplvDamDXEuMJ/0XEgYLGi//cYin3Q7P6dRoxmA3G1wKAVeD4JZhO5u15vf3mNnZ5zDKWE2/hd9C9bGHm1QR'
        b'SyWzBusGm1K9x2mkxtSLDhhGmw01ZmmOxFTLcAxTLUOmdX3GI8zoMPthglrGLTYZ1TKjh9yjh07TpqNKG2v6z+8zG97SYifyDGvyFIvNRiPuMyH3UfjOFgP0w++z7EUL'
        b'zQl9bQkj9FPs3MAigNuMvZdZg3mDZYNVg00Dv9S02GZUnabatqAfwxajUk4frxcdRE7o4BKKXYj5oB6xIDNpMEX1WeAWNvAabBvsGuxRvZbFtqPqNdPVS2ptMeizG1Wv'
        b'nqZGC1KbHarJqNh+VE3mmrHljxxbNErsYodRo2tRbE5kVK5vmWtWSPSroKyk+v0IdPMwfixBMLwEZuLQb4mgAPFvQ7k6bKVWUCMoqMZy/mW15WjZH1ZRaVU1U74YZRXV'
        b'YDlbeY2gprqgUlJQhMWTkhHGbKk1iEusqtY8SveUAolO2ITYy0pBgaCsfHlJpabaquqVI6oJChLUFVRXlleWRUWNtpbDcqwRHdRxp5On5CYECZKqKn1rBLWSEtKDpdVV'
        b'xbWkue7DbQ3ZjIKpkz0CR0MHT4G30n16OhwNthbrnZgbGugQNPT+5wgaC4Xs9/NGvmYy4CMsDrXs+hLtwPxHRoe694JFVYg4hr7MMWVSmILIiy8OEqQSZUhxFWpRZRUW'
        b'ZZdLavCVOvx+CjX6gJIxjhCaBmnkpUybRklR68pxI1FOaS2qrqC4GBHbQ9pUWYz+CwqWLq0qr0QPHKoR+ZPziz41+vxillkbjb4FLsFGdnBXgL1bEInhNytFZz0Gm+Gu'
        b'dBLIdnpKeqY2Ch24AbeZwCPZU2pD0P0zwXHYro2tO/x2dBMxCoEng/Sp5XCb0ZrFYD9jJnc5KRLuRUf9FHgUbORSer4sKEtAmZhtihbMZHBB4Xawc0UA2Ezs2pzAxrCc'
        b'QNgLz8IjYeA6h+IEURYxbK9J4GCtH8rnwKugF0P4icClhTpwEmwfOm164Ew2FSnUA03g0DrGznIAbIK7RWieSDAEvVySANrIWe7nAPb0bg7x8ajYu5JNMVF+5aAL7H1g'
        b'VDcdNgApvJ6ejUMMBsDdGUxs4OwqA7gebllKOiF0t5QsCyjVw14HFNhhO7/87D++0JNYIprPqQrcN/1MJgzhPVnme+Y19paw2k9M+D9b69PbnylM8ZYaTrdK219ZOrWv'
        b'1aPnN68s24u/OHpuPJwy6dNv3r1qv06WtWK+e1/9vW7P9YcPrd/A/oeV5PXgeeM+aPNf+22Y1/5L07+v3OKTtbj9m8vb3H9UTVbsEGb+0BHZ0Qq8/H7u3vBiz5dmeYsU'
        b'5445BsW1f+5UVzPvta/d5jQNTrgBxn1RceKJHxznevT9s+XVG0kg7OM3nVfS4nt1xlXPrfnqM9+DqaUHj6yuX7ut4co/ua88/55z2axl7x3/d8anS9/Y9dZXOXEvXp2z'
        b'+5veHz7+vTx3g2pO/BPhedynbV5Y/USHwW8v+J8vvNEoW9L6wielt7M8Tq11aB2Y8s9Bs6VGOeelx4U8YsXlBzbDo3AbOC8mllrY+HUJOMS4hTTr+ZiI4RnT0eZpZxi8'
        b'gamlpQ8sUME+MTZATQAtpGIPCpEapoRFaVq/jrPwKDmo+jwBFEPM5krqsNEcPAZuEMun6fBaotbtAyrACY3jRzFUMN79x9iWYsbWWBgLT+lTRjw2IpQnwUGSbWQRDBsR'
        b'A5aJqMaiLMAfMfjgPCcbbswnB1pweoWNKBjuCEiN4epR+kDBDgibSfrCz9SHjQGMoZ5zmsZUj6onRnLlsCdWlJaRbh/JorjuLNCxOJl0ZBzsBA0MVgCahS2UBi3gwFIS'
        b'BhK2gybYIQoKAk9iIzLs5LIdTdVAxIWDi9wUKGUxh/4TcCtbIy4A/eiYqW/DNoOnYSuxAAQnwGbUvcasTDGO1ohbhzHB9SgrcIAD9oBDoJm8rBggB4exQRhZMJ7MJWuG'
        b'eQ4nA95AL4TMpy0p7uh+jJqJA3TuTsmAu8HuYHEgCSIK94ALZRxqKjhjgGo9BU4wbWsAJ/QYG2Ket86KuAtcJs9cORnIRUE4IMGwwJwC7hOT4XliWjY3zBL1LC8SNQpo'
        b'n4m4f1TRDXA+VWj8Hxz6MDqVYITbMLHJsB++mQ+3AktgToCDyXNYFN+NkSyksN519FJ6J6scp9KOU5W8qWp715Z1OCeByYlTOcbTjvFKXrza3qGl7sC65nXyGpV9AG0f'
        b'IOUyhmExbTEKrqJM5TSedhovNWTKrW1eKy9mXK7ReQPVpubZHRA3i+VcFc+b5nkred5qBxcZT7ZQwVE5BNA4XB/LdjKrn63mO3Yathkq3cP6Z52fq3KPV/ETaH6Ckp8w'
        b'yMElmHJMeo+k96mR1x+WEt/xh2TddXBqt+90bXNVGKocQmmH0EFKXzsKEwYiVEOG4u7olsfjlrsKOsvaylrL28s7q9qqVK7BtGvwHdeo265RKtcY2jVmIJt2jZNxcD/i'
        b'WcxdTHqPpPepkdcflmr6MVbWXfQCV8mLbtsLlfZCYqIXp3KNp13jlfx4tYs7sbtzFxLDK4EvMY7z8JF7yWtp3zilb8HNqU+n30maeztprnJeviqpgE4qUHkU0h6F2ApP'
        b'in4kJMaqq2uiIQcachNNDaAFC6VPm8ZNsec8Y8+d4mTwjCsLpRr8uCHWR5g5fAQTJAY/Tmd09AjU7WSC7tpG6TzkJbNZLJY7Fhj9teSx2RvhXfygUSh1xjzur5gbafTT'
        b'en+omx45CFoVdYzJMMujcB0bOprvHMJj/temSNWn/sA86mFtjTMZattSbaU/wo9tOGIdh1GWN3A1+r+/R10+Cj3g/y/q8upr7BHD+RDN9kvTQllEN/jqId5wzTbLZ4fX'
        b'BPZHX87RaLYXepSgLWz4BgYvwCtkE+OCLQ/TbPuMeP+SoooFBEfuDxTc0/P+KwX3Iz4y0WSonjsx7/9Qzz3Md53orxpYf6vv+iNROjezdhL6hjgfaeJIDgq7tW1P908L'
        b'AMdzGQ83fCErHatfEO/WkgW2m0xEB58t5ep3Z7MlcaieAN9ARj91OaVvbyjWUf1TLHvfeSvv2ZKdpqYnHAp+85lmmOyzNVPumqvK7F3hM2COwRNqKN9Jxl9IfhNyCDsH'
        b'LoCOwGGtgafrR7B0Wn4uHlxnmMnuJfDQENjGFZzh7iTtiEEnmF6NsCd0KNXDFnj+AesWb/sH6t0H+9Zzj0qTWl19rGYazEbTgI9RNmzTWfIZNA7gi/8kxvRpKlcx7SpW'
        b'8sVqH/8/UOcb/LE6/yGOzn+lyRkmw1ygZ+X9uW7/8Sr4sQu0kE3U+Gvh4UVicZYJPKfV74Nd4Bqj+z/lBjvEosw8cF6r4i+bVl6il86SjEPZ0dF9xHIDK/gfqPe/yU8t'
        b'yixgf8cfouC/SFF3JhnliwavsjS4mn+iBnwwrLfwsPIfNqzk3edSOn1/fB7LECv4x0h4HKzb/8PEkHL3Hlvtr/dwQvhL7Z2MX/xSDa0m5P2hDcDjNQTAMKBov8FauWHr'
        b'qQ5wYz3F2ANoXJv1G1gNBmgX1tOtqCNljP8TNJBfekfJxaaW1AgKtHzXUNnxwyWKS6pLShnp3Sgj8jGEftUlNbXVlZIoQYIgijiER+Vr3l++oKpwUUnRGGZwf2psoJdZ'
        b'i41gogzgRiJUwFqdGdNmBc6c9cDzGUidhzg/g/URRotg96LaIAqLDc7AveAaOC4eIdsbLsGabmIAd9mNK1++5wWupBLdtyIk6uALUcSa6vLeI3sD0RaxPzQ0pK90471F'
        b'DlFzrKpN+A796x23lsTfe33p5cIu65mbK4yLfMW2Tpy2Np9k+cvpn0UtdljMPycriJGfmJ1fsXnheNmMpxeAXTlFxQY2Vz4ft/Mp03YHql5p917oIqE+Ixk5Ewg2i1LS'
        b'ch74OeaWMxKXzfUzYWMAH54a7sbY5MyY/h0GB8NMxERIBI/Co0MFRaAB7GeAPjbBfQAjT4IG2KmRM8EtcDeRMtSwweH8heIHsk6TPDY8BTu5jBilE1ybbuKfZfUQH8gt'
        b'vL+CBzIEx9AEA1poaKveccRsH5JH1qcVmvleg/cmL+lqeZLCq0+oso+g7SMwrtqocz/LSsycnyffzFV5p6oc02jHNCUvTe3oLvOVe7UGtgdKDdQ2ji3Rcq+eANoj7LZN'
        b'mNImjGAZx6ocJ9GOk5S8SWp712EeLYbMtkb08n9sjGD4YG/TrGqF2BrhD/qZi9e11boNrSTvr/iwPLY1buVDmcV6ijlYaICOKI0F8d8GhvXLhTGXtZrRluNVpVrIhf/9'
        b'KpfAPPMRV7mHGHLWLL9OSQLQJfkzOxnc8HIWZ7zy+YGdTRsKxnnuXPDiNCjV+1QvfKLl0lKKeketv8ApVMgmUsBcu3EEPG6I+6gj7OCC6/n1ToVkfruDHVni1Ax/0GEw'
        b'BMbABJ4e28pTZ4Pnxn4IwWrGmUxMD83EzJ3Lopzc7jj633b0V0SoHENoxxA0wexdW9YqLb2HsQEPm0IMIPiDQ9WfPb8YT5glugkzZe4fTpjHNkMm4F6wGSQfA0nB8pIF'
        b'BZLMYZpHneIJG/Yw/ADRPDL8gGEDG00e/b9R71gmZL9fOJbeUTt/sFq3WBOu/pFmT4JOBV1SU4C9WwoYy/clVcsRg1FaXbVEW+/jmnrMPZrhjsLqSaJ8DsA6ySW1khqs'
        b'k2SWAklNeSXjDoRlUGMqFRm51DDvCax7RpWPpdDUzXrc1uqCOma4UJ//A/2jcWZtBIVd8B0XMywN2OM8BlczkqUBcriNCbnZucpJlAZ74Uk2xUqh4L7cNQQu9CO/WIyx'
        b'braUS3Fbe9axamgeUe35OhGI+PyJWfmmvgWeVC5jLYOTKnN0dM3KikEVTadgG7wMdpcXVtziSF5EmQuNL+ybFmoOQkxjojPe2rFrV6t9SMigeW/azlY+32969r7Z2QGG'
        b'W2OoM6Vf3M5q9rgw43iA+oX8Bd9kXr/0y/r3w3znr3x2tgsnds/eLS+WvWRjXaLcsiau4IdffMpy9+49CT54ddPGc2FK51+/Lnheai/sDHpybVvAYlOX740OvG4XTc+B'
        b'ddld7pNtL3LhJPGxRV3nZn/49KYrtskrWotv/WwnOv+df2u68o0V90qvFzwVUZH069Vnbe9A6XZRzaGXvLKilval/By5z/OFT+2Nrcffd70oNGSwJLaCbeAyUYmJgZbF'
        b'mgdPkyVyBmzk6dRPhMEKBnL2mtk1jIe+HF4FzSbiWNA7ShdnXU3MO+Fmr2KsoqoP16ioUsAmBoViM7wKO0T+BMgggEUZRYNLcC8bdILL9YR/AzfAQIQoaFXVmEqqlgQG'
        b'62I3PGCq1cqVwMtaNLYe0MMgWPeFZhO9WhXclqpRrDnCE/+NhkcwFHPaQAM+Vm83xnKMrpOtYCOL2Qqq5/63PJqtgzRX5iXnqmy9aVtvXNBbYa12cumMbIvEAMjSpEEO'
        b'ukYySHIPJ/epYdfGShjlxeg8fcrVo3Nu21yFQ3+CymU87TK+yVjKlRZjwN7haid7xwMrmlfIufJs+XT59B5Dlb2QthcSaF9ZcdMq9IeN4yDFtvJlVExl6FadosZXp2GS'
        b'81rN281l5lgd40uySIJ1Mb73qWHXxko0OpiRl+/aO0lNiJbkKRPbhADOUwHchBCDp8JZKIW2domRHBjJTYw2gJNYKGW2Y6Mh2/FC/T9la42oIQoSZpuuwXztQ+iiCm/R'
        b'GymdemTu3L+sHnls+/YMiriZEFUQ2byNdL7HjF2svz7G5qsoqCzLTS4yGLKQW2sX8h68n5sy+/k2zjbuNr1t+mhfx8ZsGPnTlBi0WTRYop3eqsEa7fM2DdwGqoHTwCu1'
        b'Jvu9AdrvTUbs94ZkvzcYtd8bjtrTDdYaavb7MfOG7fdruWPs9wnFxdi7ubKkbrhbADayYQx6GPujoqrq6hLJ0qrK4vLKsj/ALUO7cFRBTU11VL5OOpNPdlLMV1QJ8vNz'
        b'q2tL8vMDNH7Vy0uqidEysVcbVVnBQ+3TBEUFlXh/r67Chs5ax8eagmpEZYLCgsrFD2cyhpkhjTgmjGmE9FDW44/YFTwQ2EpKsrSkiPQwgBnlMZmPB774lbVLCkuqH9mk'
        b'SkeuTDMeeM7XLSwvWjiMCyI9qixYUjJmC6oYJ2DtOCysqihGU3YITzXCRXhJQfXiETaFupcmETBgAEGCLOwNWVcuYVqAGMOFVcWCqNLayiJEHqiM9pybP2ZF2tYXFVRU'
        b'oHdcWFJapWHRdDiDDBHUYm9lbBBYMGY9Q2nooSOp8yeKEoz0/H/gval97sO8ODV1FYYVjq5lKH7An9yP1xvEz+ZkCcaHTwwMJd9r0RqKJmFxifZVaetCpM9QydhOpUkl'
        b'pQW1FTUS7RTR1TXmG/eVCMhXbLg5qnHDmF4NZeKuLEWnXvTXI7Dsw3hhmzF4Yd/MWgJQe5ANOyRh1YgPraJAEzyEGKRucJHkZQEFGDBZvoxFsWADhbjgFtg+AZwVskgu'
        b'OO0Njogy4W4WxQa7WXAD6Ej0hDeI0DAIdMIudGc2w077BQX6wYZg/9QMxFkfz10K+qLg2ZqZjJUcaPE3mrDAmYFMPARPwdOI1bqBEbB05n0MTpXWtk+fKnrCEHQth0cJ'
        b'k53iZ0piqPc7rwx4PsaOqsWqAdhQXITZSZHWLA/uXpyMPY8ChIFpelSsSB/x3O21DHRyGzwPD4tQ5wdgsz7iSFAzOBEMAz+BCbx007wyYEFwPoO/vCyCCfyUv7q6oslD'
        b'zFzcognvfregLGCDqTXD5C9Ax4gN8DA8UsCEc4qAx0hgEnLH5EQmzLt8YWH6msWTqdoodDHEWUDAH3NSiG4rFbV+pwgfSkhPcsBG3BmUlxKQlh6UGog2TdgoNF0G9zIn'
        b'm3lLwI1RwtqdQsQag2O5mkMNOD1bqE+BDfCyETi8CFxIFmoQJveC9bBVh5loBs8yBk+nVxD7RTMozxXDHQxkIthIBc8EjQzY4rZI0KfDTARbYRfBTWyOYDAgD6eCDcNw'
        b'E+ERc4ybKDUkGhoDoZ0OuNALbMTYhaEMdCHstqgXgX5EDsPQCzmFQAouMS2+kIpDC6PuIZK9oAUvhFtBby1mwwrhNdBgGS7SoICNhi8EZwuEJoxx6CUgBy1a2M1ZYBdG'
        b'3gT9AtIFPXQC2aV1XNsHt2od19bBfcTxwdkRbEanwo3pI1zTwA7YSmaKO9gMesVhGuTNyWiGXYJ9UEr6nwj3CHTWh+AEPBoK9lsx43oB7mA/wN9EE6MRA3B6RZHRmZsS'
        b'hY5M4MkR+JucyeAA7CT3pyfCy+L4nOEOcfAIXM+M3anCdI2zHZTCAa27XS1YT/oMT0wLF8MN7OGojpz5cE85uR3sAVdtxGReWsMDOrHWbA06J9gMFeNyoBRzfbCDAsdh'
        b'fyXoAFcIVGaFGTN/1mfXm36YWEyRMVoC20mYv71ZXIptShmj7t4IgaeFxrUCzDmiGXBVYm4NrlXXYpvMMxZocC/VoIFexEm1AudrffBDz4MOPXgmUmI+tJAEnq/FQrle'
        b'DuwAu8EFgmw5BZ4uH1qsrmaZUbVZKhgw16f8OFy4cfUi8lxP2JAEz9XCbjRS5yXLTJeBXRbVtRzKxpkTCXeDE7XYKSwTUVevZFmtManKAl4wwviBtbiw9vFx9l5P6Ouh'
        b'Dipqsf+3n6REsgzNth7NPdpiNiWcBLDTkVAvvAYvgyu6apkWoua5wovgADjF9XEGLaQyifkKVNlucFVXWU01PI/aOIUTBa+kkjJlcB/c86AuNLXPwSfR0cFSnw1PjUsl'
        b'ZDzNChw3QZVvhttrUINMjcyq9SiztWxwLt+KIL7mwxNgWw5sNcuATTlwF9yXA3bh0GxtLHgxbiahZiN4flXOtGm4+Zso2CcoQCPRTWrPXwnbUO0pcOuIyoF0MkMyO+B+'
        b'eEgCL1qgHDaUjoe9LH+gKK/FilowkA8Ow0a0HIqDM9KzZuCdY7pGVBOAl/idqenkeH4ILRJg4wwjiQ/oIktw2jJwTOwBBnAkdVYUBVtmh5LO5EXDXngupQo2oeVBHIjm'
        b'UCaXsgLtHLD/Cc3GcoLtRKFF1dBSsHBebLwxs2pzLP2pXBwg0GBRYbuIS33K7LA/x2n+8IsXchns1+uwJwotIvsw/OtKamWRE7nsJQpDF3fBAbRZ1FP1a+BZclkMe7JF'
        b's8BBYoS+AtxAbxO3Xg/NHByabAc4i76VU+WLAsnBsfzy6hdYEnsORX3SFHZyprjqtXjLf9Q6P3faq/aXhrmfqsYfifE3F7CsJxvesx9Q/uoq2Hf8hZN5uW9a537QHysI'
        b'akhsPG/QIv7F0+FozbUvd263mJBWuOfGPz85cy7818Pf7x18SvbO/HuLXXceW13/1J3NCVLxlHuZFSH1Sa3Lcg5S9f7jdl/13TVvW+vxNy5PucU91Du9OuH9a8Lat9sq'
        b'15hH/xYWYrjg08Tfzc6ZV66584OT5BdV3S//9A4JSPitdvu5HwwPNbV4Jc2ebe4z2PGCr0qx/ox90fS2KfumfdL3qeHLP9HU0z6rr/57cuhPqzN9nF9aW/iZYucPM37M'
        b'2tz4fuvRD8u33p/WE7ya9njdwfK6T+/Rsh3W/7AJbOls+LHw9+4Z43/97Mus57siPbJunVlZuvr413vD056flMJ6N6Bx1+W+H173m3vgxYap/ctFMbc/Nrjw1aVpF74u'
        b'fH3jJ/575IUHvK5+UpX34bXfOgynWSyOWvyOqiLonuG7B1/s3nTG9vgd7rdb71UW7vj4mYVnzvI5a7YMTvo2/qUTdWfvte18pg9km+mdcFs480pdXVtL923LfacO3zbL'
        b'dey67er/tbgz+s74mpffybkQbLBj1oYPxPIVln7LOc/kyd/Of/HOE3nPeWYGvnNpws2PZ7X8c3vtlHWvTzf5YmVi4vP/WvDZSrOY0zcvNEeoF11/O+wf6c21/Q6rpr1Q'
        b'fmJOa+ibkvQfA3NSf5hzxOVUSFX+LD+H2LPGiz2/Ff/zK/aC59tg5ZyijDeuLc8x+LHAzX/d+ntnpn266bOC5lc8lquffe+dCyar3t63d1JarOuzr67028q/eqrO4bvB'
        b'j3ZZNx749OcWuytZe7bN/mni6uPJptGvZ0d/tW4Q5P/+4u2fYl761m52Tty9Ey/9QkemfLDnUs+r0W6pH/zW+55fyEChU1HK6vH5iW+0xz+TWfJ6b8bNPSExe9SlH+yu'
        b'69n1csUn5wIvrglvu9la6v/quJCc+cssLrxZ/MSbfW3lX3+w3+qjNbztP5om/cr6Yv61BvqTtxNzj4a8d3t/7/eGr5d/HvVcVcdXNWdm6ZmUbb5mNXFlp+fylBi/FXkv'
        b'+19b/9ozXSuTK191lO57boYHd64q+oPVP3MStnvsCVwhDCKyw0KOkSgTHIEdwyzYrFM5mJm1I7JDcHT5OB1f42kRDDaAjYxosBcc80BbpBM4yFiLZ5FSVnAbB+wUwcsM'
        b'wKyTRKP9xWJJsUArmIxKJpLDiYihUgzBqT4BdmI3AcR89ZBn2IOtYD9Gcu0ErQ9s3LX27Rl6RDltBzeBDizeZCH2SsHB8k0nY0axfGxlKrHAhzfWBWgN8OWwm1EdD8Aj'
        b'1QyEq1aw6QNP6GSbG8BxInwtMAIDmvgVQJ4AtzPxK8JAE3FkWAf6QJMoMwPu0qe4sWAgggWOeUvuMzv27kQi9QQ3crRSz1zQz0hMUX+maCWmiKOC10EXFpmCSwtJl2Zb'
        b'W5EYhNNANzYCwDEIp41jjO4Pw/WwWSwCp1B7duWJ9Sn9lWyvYtDKeGWsh11wAwl9iFg/0OygC8gImuaQ12kGzsVr4Ypn2WApsyCBVBxsMlvjOQHOQ7lQ4zpRDo+SfuY4'
        b'zMcxhoMN0FmmmwWOgPMzWHAvI93dD1pWaLADUL92Y/QAL9hMgFwCuSsQF4Y2rq2IP0W3wx0ZAYgpCebAfYh8uokMuhY2gitD9fv18BpR8e+HreTZqEvtdjoeEA6AplC4'
        b'JYrB4e3IQO9TB2Pegfg9wpO3wjambScNlj5gvY+WE877SjUDAnwFtericMhymT5mvU8VkOdaLovXsd58sI/Ahh+UMM/dDo7PEVXYjmK9L4cx4Ryvl88hjLcb2KLlu1nm'
        b'9zEXxoLHC8AxcPHhbDcaxIPM29zlATaIauBGVBNj3YAeA9dzqmAzet+YwI1mIua0EbGfWfBoZSAbkya27jtwH7tfLYTHET0g7kzDmcH+YItl8IIZ7GeFgY2sANitZwR7'
        b'0Gwgz5KhRg2ImXcEL4CdAZiLb2MjtkM6n9EzHJsEdosDCsNIlBewPTgVnPRjUU7JXNARupQJylI5icSQGQf2wj1oFlEGsIttOAOtBcSIZB9AXBXi4S/4Mps7evFHSNUC'
        b'KJuDTsqNbkPDjNl4ctCqIgXbCSUlBpmhEr3TcYmgDLgjLSMIPRvKuKAdXobrGdigjnngKEE2zgpAHAua2cfc0IJjP44bh9aUJ4mV45T5YAs8V8rgH2cGpoCdeAqK8Tzx'
        b'hp16+fPAesZw5SA69h4R48bsYN6NCbgOToJdbESOcnCKocwOuC2TaGa2J9YFoOHPZDuvFhEKmWsaDRvrsjTORjpXI3AM9jJ2M5engU3wnMVyjbrGaGEwPMYGJ+1XaSCs'
        b'0dPQgSs4UOgHu5jDWxkbnEXcznGh++MBTP4fJxJsLDpC6rJ+1D+NtU1BcfFDrW2G5BFNjo8+o8lZOw+H4mmZhBUas1nyMowEgv9SOwkITHNkX/RAzsD8mzOUsTm3SmRx'
        b'KqcZtNMMrIuYzUA0p9yKfClaJZypcp1Fu85S8mfpfHziiOJniKWNjbPSxk+Ro8jpdzj2RN8TAwW3A+OUgUwxTWRMJW+i2sa+KUbt4C7jy716gvq9VA6RtEPkIGVgGzQQ'
        b'pnZz76xrq2td2b6yc13bOpVbCO0Wcsct+rZbtMotlnaLlXHV7l5yG3muwr1nVpdzj7NMX+3hLfeUF8mLFF6KZX2+XRU9Ff3ZKp/xDAD0HY/Y2x6xA6Uqjym0xxQZV5bd'
        b'aoBVODhOKKvVuN1YZqzT6Bx16HZQRHS59bip+KE0P1TJD9XkDS9ojQt2OfU4qfiBDPrxoAVqPukDSe7h5D417NpYCdECjZFnSTm7Yk2ZPELBUrgrOD0TVU6BtFOgNOmu'
        b'jb0sWhYtr1E5BdBOAbdJmCIywlNVjim0Y4qSl6K29xylurOxbYk8MKl5ktxLZeNL2/j+gerOzvVARXNFU2VLpZRz11mgdvVVuk5WJJ5OOZ5yLK0v7U5A/O2AeFXAZDpg'
        b'stI17Wax2t1f7eSqdnJrj6GdRGo3j841bWta17WvUws8j5p1m3VZ9FioBV5qV8+7Aq8eU1oQqnbzbF9NuwWrtd89fXtiaM9I3Xcvv5502mui2sMHG3aNUwsD+5xpYeKg'
        b'lZG73SCFEzvK3a/HVO3m075KLfBFf3n698Qxf3mJaK8ItYewJ0gtDKGFk9BdbvgulAhd+daDFEqk3MFJlLs3eZrUDJFkSwxtQ8Bw5rLUIRHnTemQNCX53Mq4laH0ypNm'
        b'oEai18HtM6X9YlSesbRnrNJSoI6YcD6djkhRMp+0POXc+XTaE0r08V2A8uXWKksvtbu3nIemXpXKfTztPl5qrg6beD64H/3cnKScnksnzlCij/dMqbmsWmXpcZcZjXC1'
        b'd5jaL+C00XEjZdhklV8i7ZeI2qAOCKcDEpQB2TdnPT0P9zpG7eN/tLy7vN9c5RNH+8Qx11D3RUqP8f22anfPQVsTO9RtlEjZg3yKhw3D8RIQPv5SzNmYm8aqcDEdLlaS'
        b'z605t+YofWZJJ0tXNWWp7RylxU2lLaVSjtreUbpGVqu0D1LoY3KyR4Rq5YXRt6Paolpj2mNwvFmn1z0j+nNpzyilPf6Q9SP5Fk8lzFC5ZtKumUp+5iCH4kcP6lPOnu0x'
        b'CrbCSsFGNHPHKfS2U6jKKZx2Ch+jHkQuMu679n4KHo0eX6PRRZM4rE2rW1bjLx7SmpZVSns/9JFPZ36jy3ynTos2CwVXsXggbKBaxZ9M8ydL9dSWNgeMm41lEfIwhU2f'
        b'bb/1Mcd+yUCx1FhlmUhbJiotE3EJs2YzWYk8oX2hytKXZmBn0FWLZgs5V2XpTVt6Ky298RXzZnNZDabmEJVlKG0ZqrQMRZfvWLrftnRHk013sx2/pexAVXOVvFhlJ6Lt'
        b'RHhIsTp9TfMaeQ6jgh6k9Kw8BtlcWw+80Ji0mcgTVXw/mu+nJJ+f33XyQIu37ZAELZftdXi6KXIYiHn0Zh081M7ugxz0m3wZ5KByeJ1Bpw4e028m2BqmXqJt9sZbqVXi'
        b'uGRrzrPW3GQ7g2cdWCh9w9x2phf1hpf3LFPOHRMWShl1sy2jbtYpYatrsc5Zp36tXv6nKuhH3hwxQ5TP/Bu+LTJq6+NjmWMO2Qh3YNW1mmJU1xr1dfY8FotFvDb/D9PH'
        b'5iqIOkgdN0qgqKco8wRzjpDzlqHWCOwB8lQRl3rwT6fFkaNkn6VWEU5M2ww0anATjRqcTRThWA1OEQQVToNtqQ1RgnPZ1PYRCuw1ekZjmLGhK3qjFN3ctXoaJfiYecPA'
        b'NnLYYyjBZyzVeCIO14ETbXCBRpups4Z7uGZZW2I46kaNRjE7pIoAjX62qKByTKVdIda/C8qXED1d9R9o2/8TRTRW7Y/5VH9t8/wFBFmD6Ay17WA0wEyTsDofNb2S0bqO'
        b'rQQWJFYVl4RPFBQWVBOtJdPh6pKl1SWSElL3X7PyIwOo0dmPxIkfS9mOqh8bZFejytUqsrHu+M90nX9Vs2lIjdZsumXWRuITiLwUnkEHnKwguCsDHYGzh1r5Xaoaaei3'
        b'W2gET8fBa7Wh6N7gBeZDtYcpWJsGG7Jy/BgtEKNErIdHjfzE6NyJTqtEiJudai7CSp5afWwbCJvhNiIyjnc1oQZs/NGBOz/9S4NllASvgEdPXc8xW7qMQ7FnshK51IFX'
        b'aiejq7ETkkRAEUDOdntysNovI52c32YxnnZFgiG+dkMk3+g4yZlhBntXGpGGLGKbwnMsikInM9hHZYBuXwY28lnnXyjLyd9wqZD8Ev7Cb+cwMmt1azwTXmyT01zqHedI'
        b'DpW/ftHPE+vWMdnJ3UyA2hNrF7MUrif0KEH+ql7PPIpgjoRjH4RwtEqFWcygwkCTd20iumqJDnK9QwFaYENgWgbcizWXwXBXaoKnRjGcgkdZnJ2SFpDGSBngJbjHLI0N'
        b'GojYPwy1/yxsnAJPPcT/ZJTzyTminsaH5VnoIH6A2GanLh4S2hvH9Qb7wVaiIlsGL8ALIspaFx+K6PVWgqtEiQ1Pr50IG5Ng70P0qX6628AGcN1ojQvsIgMlduFQ84KI'
        b'rZZpbESARkUQv4gZxrvms6jzNZBFxa+vV5edL61uwS7yOEeoxxiZykPhVYBX1pXohNxKrZy2iLxU2GluDk5gycLs1VQ9uAwZojMGT4JTBLwmDJ6nVoCLboz64ZgAK3Mp'
        b'7IjTbkyVT40gWhbYlmKFBSqIcBr1Ke54Fjw/C5yeXUOUfrw8f8ZZB3SAzqFKv0MljM5wC9wJrg8Jj7ca9oNudKW9/JkX17EldmjB3+LM39VyrfLtEMvnUrPPXq8Qn3l5'
        b'QmZ3UIKbPPHS9SlHKReLQCnl0IPDk3ye/O2UWZl57ZGfv+H7RXZ/YM718/vz1R+9+++65z7sWPfKutBzq/N/fa46Oaa3Ytm6Vf3jzn2quMSO/Lj+adm33286eLypdJHe'
        b'lIp752L7xr/+Wlh+aYH/96fMlNZfBdbu/nVW73dvHlz06XzTJ5e9uvXTpxO/ntMau/z8lcFXnEyzdrw5r816c+fLU3tbC39MWfm04Rr9pD0dmZL8b35IbY/9uO4rzmJw'
        b'4O7VgbLg9nOr3vk4/d4ne1ojnvn+o4bYqMvbt+86FrD1p+McW/XmlyIn/bA65acTwbJjdlGbk6amxV850fb0lZdmGLZaf9l+pjbiK6vcnrz43cctnz2UdjNpS5WCuzP7'
        b'89zsa0/vDPcv8s79eRy/dEnx967/FI3rH7Cp6HE9lh3YJNs7TnZo/smNDV/+NG1l9dTbu4VvyCXza4N2Rtz5/aVfrnV/+O9Xz+3498RXbx39xMHz1VzTf3750h71u2u7'
        b'c/bdXF0rpydJEsKXPbEn6qeTOdHf+f708pfRksVHW0DLiuNP0fnPRvrPfP75iN+TX1Tv6br8wUX5LcG7b39w45mZ900H6NYX+qd63ll8Kqf2VPXsb65M2CS6lNx4rq5j'
        b'57/e2Z/LtR0wTHmx4If6dws7Lh6eZH08KGXGF7POfd/edKFpc8LhT9uLfZa+9p77Oz/eMAIbfSwPNd/fue1Q8trSzy/d0PO/VGG0XmhHJGRwt4T9IJZcfDk4BdbXEXHR'
        b'xPlwqxh2w10acBuNeNYUbteg8WSAk4ygvTJ3mAVwBLxIJKFzYeNakRfYNhzJtZSIsSYEgCc1Alwuyww0gE5wGj7JCDIbBWC/RrbuzkKLECL9LhaRn0+KhidMwHF3/7Fd'
        b'r/jgEqlhBTgsQQtRClYwclNYoDcenFu4gJGibnGAcjHcHQo3wz0icaA/VuMf5LDBHjaRbk4ugydxSM8+tJlwi1mgIRY8iRbAi0TWyEtNEqHF71paoKaEkQkb7IUXV5Bb'
        b'S8C+ZSJ4Yi1qEOmYkQsbSCeDbYxUeABeA92i5CIcD1sTDBvK84koshJeX4pF1ruz4A2X4RJruHc8KRKBxmcPlhsDRXoKUT9ilYTFeM48sBM0MrqFqwnwmigTPgm6GOcX'
        b'tH6jbUqkTzmBg1zQQekxVt/rQacHbJyJXgvayLL0KH1nNhfsyySjY1YKrxIxZU3icJnoXB4joVwPTlWLMsFR37Fkov01hDDmw/MiRiIK9xQxQlGNRBRs8SMCUZsloHG0'
        b'NBTInTUCUdCWyQza3ixD2LgMbsYiSa04kjdL6PZ/L2l8+CkLb3RDeaPR8kdt+O+hNoD1TiO9e4dkEhHkF5q4cRX5LIrvqLEcX6iyD6btcQw4q2mM+Cnx5kKVd6bKMYt2'
        b'JDGp7F2wG3K42sW9M68tr3Ve+zxpsjRZbesmzZPrKzgq2wDaFtti4yL+svmK8SqXMNolDBUhkMWl6BE2wbQNeYRI7eKJjcJb57fPxwUcZEmdaW1prent6bdt/JQ2fqQF'
        b'8SrHBNoxQclLYMzW/eRJKlshbSvEVYQppmvM1uWhrVHtUQr7204h0kRsvT4EKR1br4fdfxiO+oNEY70+Cmjd3nGQckTNdRJg0WsO46mfrXKdTrtOV/Knqx3dOv3b/OWz'
        b'VY5BtGOQFAPROrl2itpE8iKVoz/t6C9NVHv59qQ0ZUinyMbfdfFAvbV3ltU0r5auZgSmMxW1/bXH1qi8Y1Xuk2j3STJ9tcBLpqd290Z/2bvIuc1rpGvUAk85Rz5FMaN/'
        b'5rEnVF4xKkEsLYjVltIUxS2cqHZ171zUtkjh3a+vcFW5TqBdJ8g4d3HUPo5tmNovTGHcH37Mos+i1UzGlZWpnYgwIkzt4X3Uv9tfkdMV3BMsS7zr6DKiD/ZOeDwyGMoQ'
        b'qxzTacd0JS99hLRntHjzL3gmuIpkSxRJA0lK1wSVawLtmtBkIuVKS9Q29jJDLCd/6I3uvnfcQ2+7h6rcw2n3cHTP7CZztY3dIGVp5a3mOR7Ias6SpyiKVbxwmheu5IWr'
        b'ee7SDLmXgqviBdK8QCX53HV0lXm1+rT7oM7y7Mk9CfJlCncVL4DmBSh5AWq+szRBzXeQJbcay2eo+P7omz1fFt5cJ61TOwtkLLWzi1yvNVWhr3IOQt9QJanNqbIiebbC'
        b'XbGsP2FgsjRVxYujeXFKXhzOzWjOkHureH40z0/J89M+NEnFE9I8oZInxFcymzPlEQpj2jO8P5n2jFbxYmhejJIXg/Lu8Lxv87zRuPJENE+k5Ilw+bTmNFkNBv3meSl5'
        b'XowYiTCMwY6Jthxoy010MIDOLJQyMiM7RmaEkWQfyCUej5BozCUN1zxaavRAcnQLS47+aAEzNkW1PE1pREdYbpTPYrEwDPrfmDw2v4nNaCUWcpiRD8DvIFB/hFgIR+oj'
        b'R+BmlOwzGiIW4jQYNLA14d0Z0RCFhUOlpjpB0Mgg749fEFQqZL+fMJb3o1YQ9CDGu86ZkfhAPmbnYeYeLVw7c98YYcKCBImMoTtpykMM+ImvMZYWoaKpOVkTxoeEYunM'
        b'koIabKYtqakuryx7aBMYnPgHRusjAxgx+f8BXoMhYwIMT68A1x4O2LCjcJR3o8IqmbH53Du3/EGwdrAJtjExFLYBOWPzeQMqgDZCg8ZgdMX/a+874KNMjnxnNKOsUY5I'
        b'KICEskASCIQCEgLlhAIKCIQSCiihAEqAhFAWyijnnFHOQnaVn8/5xB7nxTqvved0tp9vLdac7Wf7zq96Bthl17vr8/nOvvdOM7/WNzP99dddXfWvqv6+roootIQp4RN1'
        b'56ADp95ICA87x0TPpDrAYvJvH0fwshmbjCVOPvC3lr/notjt8EtFvrZebFHxzr5sW3t4eL+dhMxPvvidZ0FP9r3CDjcdNtz4srrtooPtr37HlT195Gu//PHYsktiYUjJ'
        b'T/pPSKgED4Y+/m3K3/zwy4LJk75W1u4nl5/8IO93EVrVq4mq8x7JRUsX3psbVTXf7r3gsLom9Q9qHe9ne/84S8Vbxe9EWu7mwK+MS3750yS1L2uff/C7f/vXv/vuts5y'
        b'3BUzmU3tvNTG93pHv2ae/4UbpuKi2+BzUVrMbam++jo6hD5Uikz8pSCzN7cukh0OPbeDYUK0AbE7xvRDDwgdFcNtcZHjYqYvNLYTbqi8NMdFTybU4vbrJ0gaZEWXn/ez'
        b'+vDDKePQGZom82dOK/xxk1E+Vyihr43Ggx/B3Dd/FpqN73NEZuPZ+P/oHkQNw4bb/SFPNMyeapixe1ba7bm7Kob0fmZs3nCu/cATkfZSExqcjs80DBoK+k3G3Z5oHHuq'
        b'cYxZOQ7PDh/rd5rTfHL49NPDp9ulnhkffdvY/i1j+yfGDk+NHV62QWblrorRMyPWpmaj/7PD5mOOg44DzsPObx92eIu0qfBmIdkLkU8U9Z8pHmwQCDMoK5o+FcbvF70/'
        b'tL1e4UP7+V6j9Z+oLIWB0T6iCUUq8AlTgZ8+HflMCQ58SAlmxP2ZleCfTcP9H0Y47p5kQXImW3n/q8wJxgJgTHx8Q19WXFLyzZeB2l9mcnwjNPwfUF5uokXx1HzhKnpy'
        b'WmZqArsPkBBv8ImK7iVhPhpgnL7+hFsVn6kq+P7CONrYDGWXRA/TfXyvyAI0vl6LidWQSsZBn2Qn2V/ws9k6ddJJHxY4SxQ4UP2YzVVuj+9Xi7839Y9Z588aTUt9S/WL'
        b'/qNmdt+0lZAIOeFXa/QzqRNfLc47wTtbZ3uQ880g2eHfDZryResvFVgb/MGSkJYmzMbCoCgwjg0u+uA06aw3loQ8rIQLRj4HQ9/AVY5a5FkGq95qL9gCPkzDNnTiIkPV'
        b'eay1xEov0V0ALz9ch/YbL0/ygSlJmMMq6Pj0nGt7ijGiuX4lX9mvs5+9vnn5kQpCQHR+CYguCVyOqvrLxziMP8jL8xL9znzO+MPo9466qehG866i+ceTtL31CZDysSRt'
        b'exIfStL2Sd3skHsjSVtGPMEEc+Q+pfiz5uIRDi1rnsuWv/39Q9z9s/6VjVXxM3LzfBBXloUrE0b3EUYsEe6HFt5dFjoKQqgUEsJU6y+7UqPF+Ui6no97NjZsvj6SmEKe'
        b'3Qd/yPtIBh9plsGHFeqiDD6H+2/tCo4+ERx9Kji6L3ZQEMfd5/yxJcvWc+yD85zfSNbjxZL1+LAUNlS+EJbCfD0fzqTDMtRosAw1GixDjYZ9pce+lAJLNvOphf6nZKF5'
        b'V6DKBrUr0H0i0H0q0N0XEwj09jmfVrBR6L2uqvuSLB9qQYplJ3qj+OAU9o3qK0pm7wrMnwjMnwrM98U0WZKbzyxYQxav6x8XNRQ2brt2+Jne4XHVObbgJE8EouIFK951'
        b'OffM0WWfV8RlDfxnlc/FX11vny/8togn6lncOG8ueE11LWn3uMeuwPOJwPOpwHNfLEB45n91yWjnxf2gA1EvO3l4XGU8ZM5k18Thc+d2BV5PBF5PBV77YuoCgs0/vWBX'
        b'8+a+bslZdK3gXYHBE4HBU4HBvpiMwIJlSfpowU489PEKonAubEG8IBkncNHP5K7I7cJl5n/5BliKcUyMxW/CGjbm/kKM7edZgUrogSanDOw6pgjluIqbaiftoDgOH0mc'
        b'xkpSuk1SUIU9eE9PAA1YBv2kyprPnYNBWWiCaq42PoZVfCyAjtO4BHWwEAPLOBEiEMNZ8tgeOTnCY5jzhMceVKseq/NhFSZg2qoIhnxh1rEIt3FMEudgkl4bJ2AEhnA0'
        b'8YaNEXZYYzEOpEMv3qeRLGBXkRPUwCipxnkNjxuOAepQcxiL3W6n2OID3IbVZEcsv+5xQC/mgPtpH/EIm0KrABiK0LGEZlx2hHUcYzu70mESG6mZFU9YsU8zw3qbaKwV'
        b'4Gg8zqmQG9kPTThIr01sveqGnYG2KfAgDmckoBdWsDwD5rERe4NxBuZupeEwPL4Nm9gWAo1aOHj9ErbC8Ek1nPWEzWNQS2NvhDqlc/AoGEqNfagDK9h5Ch7dxqkL0MHF'
        b'UTIG7mELdNP/+iQYx04YvKXLk4UWWMI+GwscwpWkUzKOuAwVcTpQ7JEG9+Op2TY/2DKNc8/Qc8e6ZHyMXd74MEITZvJccQ0WaJrmnCSg/YJpKI27Bh5CmcyREFzUxAEc'
        b'pE+rfuQ8d4cTMR5CmwWunnI2cjJUVcGFi/RFd6HxJXPswElFFazABlgOyaZvG+VlDuEOnTGJ8/CIujPHwTbbBAfsiJKFe9BlA1vK2Ccf6wd1iTnOWByEbbpQE20nhTuw'
        b'pqMCa6mwow3lidTCdCZWYbu1Dg7GH7oY6XSUzL0JWIPR7BjiulbsDJHTiipIdyjEJZ3LB6HTHwa1LuEjIlEbjkvReJaIpTpx0AVrpaDiPG4co5lshSl7Gug0dXEVSsNp'
        b'EuotzxBHVOfBgoY2VhOJNrFf/g4Pt7DKwzANFnIfEN/jJC4cgZ4gV6gjvpeDLVxUK3KhCR47D8W60I3tlnLHcZamaB56eedhNC7msCk0JPGhRv/uURg5lVuQpIAPiRsH'
        b'cZyIW5t5NQy21cKh0wU6YR6GoTQGu82wzfwIruEGrPJgThpbtHElRjwTe2ApNOLWGey6HZwKAy4whV0sNKUJDYS4BGfSfRyolV4d6MKSwHBqvikc2k5CO1TEkviViNn7'
        b'YRPMWVKdBRyHyduXbqsoht+NPe6RiN1K+ceVcIZGW0PsXEqSce8EiVaVh56vYf4RYrh66MBpa2L0KWLQNayMwaZU2KJhncdNqJLEEWdsKoS+XB/XZJwxxgoTrMSdopNW'
        b'd6H8inQwrGnqsgQzOKZ0ip+BO1dxQQwb8tRjzuN9WJSB2jue0I4lOh5QFwHFWBavAH0wHhAcahOnfEQLJ1w9ZFSVrY6Ja9uGkhj1+GJlMM1wO05qEgxNQ3EMjtrRVG7C'
        b'PSzjYZM/NOK8Pnb7Y3U4TsIiX4kYsFoDBmkYDJrKom0YcaESp2HpVp4WPNCl680QU43nET9UFChJkUgsXsMWXC+yUYVmouF9mp45gq5lqUR5b+zTglnsj7yIUyR5Zbiq'
        b'dxm2/XxgB8akDaEpm0BhFMrtE3AxDavCYdvqALvzGhUAq9rEc1P4IAiafLyVom7hMl1vlHih9xKUkBDt0LBKbHBKxTjYUC0ASojgyxE4ksqyqATAgimuiUN7rCEMQK9p'
        b'7lPiyBPXcZEY0gnqGUNSr9fNYSnXHruj+NRqP95Pj4H+G7IkmW0nAi1gVPGqD0w4Qy2uEK22sE2buOgxVNPAFuCRF5RfIoEtO4Tbns7OTtjuDUPxijJYRgw7Qvy0CvcP'
        b'Q6f+TeLgNjFn2Mrn2Fl5YfP1HHO2gQVGycOphg2SnCYSua7YS5fTCT4GLbArhYi9ySE2qiY+nYQhaMWWqPMEizvmGmE5l69Avx/1cBgbcMmERKPxzCGbPKxVlYb1D3Mr'
        b'iUdroBb1Y/kWllpK34WldCFitsjnQwdB5airr12BQRzM+RcWqfOueECNBpRco4GxBb9RgqZSO2fi3XbJNHgAY9HQLKAJntAXQPMp7PCE/hyqUoJsJH3YSzppDIoVxLDU'
        b'iRBkRE0SVk/hhuYRYoUF2LDBx6q3cChdLZ+flIrF8JDEtRxbFIhQwzS8UdyCxUCay0ElrI44mEScVorzLjBMJN+KMibNNBuRp0OcO5DmhA1XSX+1mcLELRKGWiuaikFX'
        b'G4K4KuJJ0ptRx6+fwEaTFBy/fVa+gDpYCsXEx4OwaK1vEh8Di4Q2q3Kq2IwbWCqHle7QaxNC/AAD+dSBKqw3gWXilymoL8BBSW1DIvImDrtHHGUPvMi4m9GAywkf+0lp'
        b'd52DRY/EIJrIRbiXHUHT2WHF9vRtFmDNTWi/LJmArU7XPKyECr3eJ4e0TXku4UED1Wl19NAIxzYcMICu61AtdlMTuom9iYjE3tAbmUId3cE+nlGGtztWpQuwMSFM8uAV'
        b'nDkAbYy5jpI4D7orkc5cyP17YmxNukQ3g9p0oYWxhY/McYV7Xvcq9EtiR5AMF+bZzuk6Epp2aMiBBQ7BraEaFlsTjdt1CnFWEjZgOMHDBDrdYEqFtEGnFlWvk8duyTSd'
        b'FLYurEDC2G5jio9DrTyh60IhtuhArbfuSVIEqzJEnsdYIxkIE1eZuMRwM6OYOdSTjo9w83IYwQVD32nCATJBMuygS8XFPEgZH0VA49VzcO88bChiv8fdS0Sb/pOFKlAb'
        b'7BsBE0a4dPegG9uCPklTMpVGVJmCrkv5XGx1t4X1kGOF8m5YAl3Q7hxHqvkezfOgphIRvByHebCjhE2hGooHSPFVq0LDZd+YEJLdbdsLp1NJipvDodkKSn1Vj6rieCpM'
        b'u5D0VaZAyxG858bFYvFA2Ig/Cw/dk2HR2R82ofKsvdv5Owewg9ifUHGErlfBSSP8H8R5CegnOahSJ3lZIFLVY7cNbEOtFolptxFs3saVG87Etu2k6Oqw1fEGDroSpBTH'
        b'X8iDco8MEoH+29B6W40Yazk+HycSNbGdIHCAcKLaAR+EKdkhcXwDDnuQZUQ8PaJ/kvrQQ0dDLifzPBRJKZ47AIvBxIirsJR/nIR+GyfdsJbIVkb6ru+kLrPIsqD2mr4x'
        b'Y0ZsVD0jBINB6mYx9CZDa6xSwU0/7KarLJFgtUFTMvVmggyCUjGoyyXC12oV0vC6SHlOkc7MDocBK+zFYc0AQTCpibEUdRxIwIdeNL+juBkFPVepi7POMEtiXGkP95HJ'
        b'+Ta2hlITFVeSbjIFhCVpWkS3nYhMgpgFLDN0j5TBOW1r9wsHSZYnc+vEWKiMOQVibBrFayPCHNe4aVhHRoTTKXOWbHTupqyxvWQWGbHt7hex6SyNhu1qfUyDG8bFLKLT'
        b'CoOh8ENQboul1jHQQ1evhrnMQic5XZaW+lEs9lGdWbpq2109KDa/SBO+xj9FWNgK62Z2Z3DqMplpD3E9gUzMOtJik6Sgl5GQrfSuJbYoE9tWnr0M/d7YGuRCmrUhwQU6'
        b'Qs3I5BiGzdN0tTqyR/phS4GkuwcGFHHCE+qs87BJ3k8vMY3grkSSBKS3UCYa5oxOn/PVdBIQj03DQ3nLg3wiW4+Msj0u6R2R4rnjPQOiZLER8f2IkjYp+DpqcyYKSy9D'
        b'iysQODmTGiR8IgMBN6KxG3sdbhBmPYQx0ibDZOrP0URxAy0vQo0UxyidFHUXTAdgaSQORp2Gal8LPyJcKVS5pWgHeFxgRkz15TswGmuK9+KgWKVQn2CrCRsv4UoWsU/r'
        b'BZy6ipWWx6BNjHitzxcrXInDdgjaZxIvk1vSQPBdpaVJRF66is0OWAF9GaeI+OM2UO5MjDOMjdYRqtfs7ANiYfgqrmVEETb3OyjIGNmeVNWyNSVgX5LDKpVz/sakD3eM'
        b'oDuUWm0SEHc9ToPqoIskJhtR0H8ERlXjcT6dLthFA+25QsIwcilBjfCnCWas4JEskbMa2xKhSg8WLmde0TgDk6lUaQY6rhFCdPBSqFfFwcTzS7ZQ7wTbxqRx1/H+XVV8'
        b'zEnFLnNs9dDKfZtYMhzu2TGWLEkXcuQ2cWQeTiXgeL4UGT2lKoVEvpIjB8nAXdI5pozNimRGhgUVeELDXT2jwlwoj9EMjJYLIg0+xF5QeoKQv5VwhE5zYkZTkaIApvNo'
        b'Yjew7+IZWdKWK7CjcBVHsCOFtO2YOBbn4sOQBNguTKefumIvkykzK7QegKyHTdhOJtZfjCWtkKWHIybEFYMkOFMh6dhYpM92HjNTN4k6UHnldJqmLJ3RSMjRSrSo8Ysg'
        b'M2/ydvDtsKS8Q3L+SNbqEI4cIuAei3LOkyfS1gAT3QZYS890VoYVhRySkZIssigawv1tpQ1xLtafPW0bTFVW4L4kTgoSsPKCOXug7h5UZEKnArkp96E3DxeiiVHnjsqZ'
        b'exM8dSQruqfkO5PvNHiQBPQRgU2NtgmfaPnwGNmaDRqq0JKur3eeJHX6IK57EG49IN9kiTTyRjrb6Y9NN4xw9DA5t5N4/zZ0mlgS/K1J0sVKcdTWI8E2zyDqGsl4CclC'
        b'aS6JQacMNFmTZE7h6HVb7PI1IllYVFHKjiUI3MLJSJy8TIIzbEAs2H2SzJZVW6jAtcx0GMohL7ySvGWNY6oEmW1nCOcXHQ5T1xuS4AHZDeI4HkraspI4tdn5Oi6HamEZ'
        b'H1rwUQJdu4e4rZNz+JZTZmS2eiDN8fwhM+HTt43xOdDtnAfVh7FKPAprUqDDkeouwBJ7qhmrLrJ0d2ScdKv6ykOf95G7AcSh0zhbEJFKxmJbsPP5k8w3m7KHEdcssyhY'
        b'Jbaq94P5wmTVawRBHQrE4EuWOHShyAOb3c2IK2Y1DmHJUd+UUKxzdDGVED7cfdcu2MfLWVecwz3KoRO6okU5NYYPh/swTc8yYgpDqoRiqzBEVB5MX/AxJ6vmoRiH68LB'
        b'DmcsEUbYItr1RfhYEri1SHC4Z+gX0r4VwnMyPU+xe5uyHC6H680RKRXRORt0jUmssZCGea4w2m4vVl7K9eSRIjClKeghhfSABKPTRY5o/uiOjN4laWh1CFKIUaE2Gtku'
        b'/0Gi0kNmsB/B+17uflCe4qxuSkCziiNaBaSdyBnwUnS9ROjdAN2xWE/mCkkw9tmxJRdyvhvzrHLdYFKd2Xm3YSQhBitkYSArhsSmGXacoTjsAj70p3mk30kYy87T4TCM'
        b'cQhfK0KVyYLrOkrT1WMTachCPhwkd2DeLILarecE0DXLEghQH5EGbqZ5JgcnuQjKrUi7NoZAwxHyFBaIGyLJfGk8QuSagSZ78pLKcqL94LEPsfswKYkaYqoFHfKYSskr'
        b'q7Q3LYIKW7LdNggl5kgb9MOcAZnD49BxKuHUTR7WSyYoYLvndZiww7Uscz1cv4JTkV5qMCFZlJvglxVN+NkIw9Js1QDadbSwhAg7RWBUQtg4GhVJbdUSPVsjVFNIaNep'
        b'Cw0naKijTgdkwuSwN+6q0O3q5GGpDbkxxUSVGSQU3bGBWh7ORZgF2GBZOIHagAPOHSGhGbM1BxYiYgIaHMgcqqfxFGdp5PJJMTVk0xiGYfvcJbIlm6HaDHolcToZGzzh'
        b'4RnsDyXmqyXXZVtSDWuuGsSZumnjtBQ8vAoPs0hItk3lc3EiLisLR+nVdFtA3a2yuxhO4j1DUNxoiwtuHkVK1+Jh2UQAK/LY50lCde8kzhz1IrmegHJcSCU3rwerFMh9'
        b'X4KSA9AdTTAArWc8I/0vZYVFapBJVEmKfF3jFLZkHbUlnFi4ySN4GIFpS3XYyU3CqZPkDzSYqWCnBkNyUncVx+6SkC6fIHuxiq1HmfpfI3UKq0ehK4d4qgJWL0FFOunw'
        b'YZg8R+I743MXZqLJ5+ulWZ3xPi1cf9nikZrpu5RI/tQI1J/U0L5jTpbnkj9zJbDxGmzi4DEqdnBbXx1aE7ItcjTJ5JpyxrUrAiwR4BYXeq/cvUTezP3cUaFVtUMj/sjS'
        b'DCHprLO+i8JNnFaXOHALB+JJOkpiCZvnAy9htbequiuJ+Q60ZRE9y2VVxSOjfYMIeRpsDxDvtMIjLRy11vQxcITFQvIHKsI1AyzjXCVJra1duChco1kI0KOLdEKzHZFk'
        b'S4aGsJBOGDNIWmU7CVdyYcUUHkGNoznJxih2p9OH+pvHoZPUGouawHh1CObNYPZYBhn7vadxIf4Skbnc76IGszaRYHokjEv23hZJdYkOCdC8B2m5Xr4OjpkT8C7ikMpF'
        b'GD9EqFoHXS5ZvmRn9yaS6VnqwsB1Hkpup5KBr+1ClsKQlgJb2fLFsQJlNxmYTLtMOFwrWgfIjiMRaLhuRN0ilYYDdwgK1nVIEnrIzYUxvyucFKw4m0qY033lbCLphUXs'
        b'TqAeNuWQIi6lM8gqx564eHiUGngSlzQU4fHhSGKFdlUccbViFDHDCY0EXE8mrmF2/iT5DltZuH1F3FERO7StsSkgkzCtVgUHlQkxmwvJjiqGnRtk6yydgQmlAJMztoYs'
        b'4TC/EB9GSOGARwaRvcvEOFfXNFk90ENZCftV7uaeFkD5WTF/4vlJYsAqGL1DWDCQe9ETai4R0t4zhzXVBJLMLcKlldthaaQv06GOh/P0eZrMvPWYm4S33U5F4TgSYUnA'
        b'1IlTprB59grM6Bl5ES40symmaXhM0NZB+DCjRAPZxp07gb7U6PAJaEpT8wiga29oE0U23WDNlUC4Ilr80JmcvMu532TZBkkwV6AnGGte+7ZhdPEH0HZcj7m3EUGyXFhW'
        b'xkp/eCRhCTOXJNRhAgkEl04QGzyyv4jbUG2VbE8M2ihcNJk8ZEk4xpboOpQsoIxgjTi0HObINcDHtwIsTWm+pnDL2RUmdKBDQecAUb8WluJJWIfOOHJgQouQZdIIOuyx'
        b'2IDQbgGmw7EvFLpsIgh4KrygOz6CdMKji8xEGcSBiCxjcV6SI7YexZE8rLKChcMhWJp+DIZTzpJeGKYBj5HV2u1OeAPrvlhtEUGao8uMRPS+pUFYEo6cVIvMwsf+xG2t'
        b'pDvKjqtKQV9KOswRfvXSFeb8JUkIdjIDyGtvJIapheECGjRpqwM4ehQe5pI+afNPIXYit6XNQpAOZTL6p3HGPhnbvdXTYAsmcrHLHjZcs7CNaFePcxd1YSeEcwrvC6Ru'
        b'Z+EOj/pZ7qcG6+JseWTIHkYT1T2h9bz2AXtyuqppUDjjQEi+RTzxiMRglRhh+wb5n9MqRPaO2DgmOteSTAhVH4hFuSbekIPlSziaEuCffO0KmaoL8tSJTtK4UzK44AM1'
        b'cdB20VwDyMO4hw9S5GJwOgTqVVyuXi7EXm+/g9bYeAznDyZFYZ2tGDNdCYTKyI/uwy3fvCK2XyFWkbTXAD7W5RtBq0oQlseFe1w56+dOIl7rhA+zT8Xj+iECpFma1Bry'
        b'DCWiCR2mZSN0hAjDYLuFSNkedxzmcfmQKYluOw7lk8TVwZwJuT81SpIsllJmuBpdtCYetwNv0Ow8QLIPGqRhRdnBiiCtN1/lroIxCVcH4c1jC6yMht6TaSSVrdCUe45M'
        b'Gv8ims4Pcza5tis8MQ0cx0YXhSwYVpVIMWZPltFg5gkQW6253iFezHmKw7U4XBSQXC3T2AcsHOSxQSfyIJ9YvJP0dy3Z8NMFRO2Hx0OkQ2HWDjvDibs7Cbc3ZJlLDlM6'
        b'oURucqqhTh3Lgt2Z6aNCjc1E68GIDc6cN2M5sr0PsgCUh6DPSo/E86EjdKkRabqySemMJcB8uA7xeadY0HFtGNKyh+JYqDpKpq8TwaFeqKk2wURTEpaSKZeQdZf0Viks'
        b'RdiRSllMYBheI5kTaAsTcieJxPXYoRlNRFpXxsFENZyVMilwdbyhAT0n4ZFvETHVCCm+YezQwpUcb5xQJkunnnToZhKpggIZtyyaw15qpOnQqRwYduBb48wZQxh3lsHu'
        b'HJxWvHZZE0aVFG9AsxrW+iRSQyXQYiFp40fzSYYGkWWNr++X6XIyKAVnDxEyTJAQdV89hDvuBF1t0OPl6sQhyagmsSTrm4CrCVZkr2HFCVLOLE+WG8wdkOYSFKxGRxHo'
        b'jdCUrFGrZUpqYaTDH8CQFNxPgnJ7nLAk/K+8cxOaTkUhWyMf5MDiFQdtApQNKE82JjEb0wRSXAOWxBkdJBRz5FR3X5XWOoGbGtAWcson04M06DiM4wyfzroHi/qq9uRz'
        b'DMGoK0yK65AwdcOOkZoWWbMPzLChCBsYdapuwQIv84gDC+zlCIPGYbhOqhJblQwdDbH3FLQnhBPrVGJrFqmm7bxL+Oi4YyiUpuYQNLZYcexgNCZPNTaWCJ+ahJvwIBbm'
        b'bpD93EgW3AMi2PxpQtYyQ3vyC9exIuu0zzUnwoFKrC60JPouyHGJ+SblmG1Mc9kRn513G9YC6OMQdPqSg94HjzI9cTZMqBiXcNPxkjO0mZDSJP/XwwmXvMmCeyQbb02m'
        b'XHsECceOZCxZL8WHiMF2cnkkSM4wepAJUgnxM5Okbdw0JyxuJ/ZcscclTTJ2w7FZJtkNpgyxy+0oNPJIvfULWA0nxWRyGbcKEz09yRoo9Q6118fyggwysLdZavcZ0l99'
        b'0rhlJ5lKWmeKiwPBuGF0G4rJ8Xt4xF1BNhhb44W31mbYQv/dQmiBDbaeNQTrQTREkpNRtlZElu4IjHqqY0d+kHHkURrcQ5x0xJK75IAu65BqrIyCvlCytZYtJZIybDRh'
        b'zlOGBH+aKj6wIbqWp5IQbCtg/2UoI4NgjnRLnTU2aEvSGEekLXG2KIkMwPLYPLjvRDq5Dvp5uKApjV0XNd01iV2mTcQVD+LamVBokHeRItDcwGIPsmamGKSdwFkOae+H'
        b'WH9MPiGQPR9mcionRQa3FcMKjAnfySx3TguE+kxstgkmr5pZoYv2SUXEHVXGMKd02oeEeEADNmRgJTw/1QzHjVi8XnLsyq7gRp4MQU3F9fPBJBtl5JmME+40ktdiQPRu'
        b'08UeORneNQ2siUxJvhxti50+8tzz6nTqDDRKQJOSBslcM6ymyHmZH8UVXbb8Saq7GLYOwCq7eTemc5C8vtrYM05kKPQeJ3IMwOxBy3Ro9D1MYlFHzk92LnQcp2ko98Jl'
        b'R1ky4DfJMug+X6CBg3J3xGkQTe7QqSJdRBLXRJ8aYcc8/Wo+9BqQT1mqfCoAljWhW/Gkk9wtvOeNZTrRkjgWAk1J0AtTxEd1QRFsyRTHctl6F039JsHvHGmJUhy2wso7'
        b'0QakqMkGukh1e/xpMPfCcKXAigwzGCF5aWYRi2UjYnMjSSL7gGkTskiH7WhsO7ehRRebEsjoXr5BDDNzS5P4auo2VtyFKoJysj3uhRNClcNi7jtkK6VYk255JQcubGmq'
        b'Poy0MIFYyhn9IAVDbCAZCDMspJ+7tRLjpDVxWOuUIYskiLOJMC3peZUuskI20oiYHa5oww6OnUyRpRGVYX8OsDvAJZGO0MSHVk1C861b2OEDgzw6HIWNBFI343cIHOtJ'
        b'nFpoLhpldHHIm8B0iuVwwaYi3IFNR1WssoNNSxw09MOaVHany4utVcUHEnHKjhCmVMnxcTLhAHH+Ur4+ifm6dUAGsdywig3bXX9MHVsP65li15HzZDCQdLgRM2yrJuGy'
        b'HHY6GOCIgD3fGAWlbrjuAlPSeQQvzWT/PCR0HmLR8TYkoEfHE9pkyUMYOaYAA67W0GFLtkKZZogajh8+LiGBlRfcsEoW77kFkle8aUUmVoU9zitk4vJROR8bGLTFZtfT'
        b'LizkGnTySe6HCe7LC67qK8JsBtvIv05osA4l+sTtM1yyze7etCaGaw6CMlkhX6xHs2fqrx8hTOjGigwi3CjDguVjZH00X0uCoVPE0WwZvhmrNXDRjjybxkSolIDBJH0Y'
        b'58Mj59NkEpOLjsUXCMKWfG+RTn9sK0GW9RDUmmCpBdHmkToM3oY2JWLMykPsZrJ4kYRdYgi13OIoj61kPkjcYkZQqcqJdHL4yKK/RzDRCKMq2HFOI489WxFMxOuEjSs3'
        b'jWDSErbcYchUHDoMyMDqCoeJ6+T0zMCQZTSZQKS67U5nHIcNb+MbOGgE7d4wan7sPC6Kk1Jp8zIgv7YHF6xJy00wIekIVj5nS0b2lBXuhBoSurUFXZWPvh1yIIJ4pxKL'
        b'T/jSNdoPO+m53GbZfCqv44TFVVMx0Wb2LVI7XdlEgGWOKGrwKNfsME4Il6m8iKQtrwLbX2UrLLehypQn3GIvkQJLPhbBSlwO9xSHOtQM48JzyAYYhSkfrFPS5nC4xzgk'
        b'MAN6wl9yAx3Ytnki5iqfw3Wjk3JgSxQ9foVo9cCHXW7t1UpZ3QHqobDBzhtQ4hOA9+2pGzb0E1vlFXbhcoIK1vhilxGdY88hSRnXFK6HOeKavQ+5NBOhLxfX4H72yzy3'
        b'7IkTkvUa00icobMCODjoCmPC6NlkUbKbbn4EQoOiFbZGonKNsEWYIFu/08ccGm1eLstF6ZpyhUECBHxo8/FWzqbWzDlYSe62KLL/FNyLZaty7ImLl+tyNjhgynUX5qkX'
        b'hjH4zhEx4aPFx9ynzhSqOHNMecKvra/wXn4to/el4DBRzOQo65d1JRYz3zqUyPE3FfOnpoRBD5LPamnzs1lqPume/octfxOgfUHxi999b8Pyi2vfv5dW/ZO/f6FbUGFo'
        b'MqaT5XLA3u8rBq7e999VNtj+luBtkyDokP19/OPLGd88D3yfS4/zbXdMfz5z19/Hr2A47DfD0RLDVpfiA1e+0pDaHKPVeEGr+UZHg9e3rIJtLG1tzB3i/X+U8I9tv7bu'
        b'lw3VrHH/fc+hLzjNfqW+pb7zX36XdTHC6MQvMryO56XU/ZO1Y9/bhU3/NGDy1batf7GrsM17L/J+Uue3bv3j/3rnbsy2pJXqP2weiSv7lX3RbGj+8Nu2j80L3OQXfx/8'
        b'2ER1CjT+6TudX2r9zZfcv3Hyn5d/PRm4+1TuQeRM59fs4n5a2vXbr/F++P43igLvhInnNQR81axslnet5Jfrgt8kRAztL6cf+QknpTFs4PDuhW9aCNTKbn37co2rUb/y'
        b'LyN1zNwrdv+5SK7HJV7yoGvbGk9dwSjGa1vjmvqK9Dfet5i+kuIRtWn2S35hjN75+J+edkn+/g/ke769+U77lbi/eb6Qove9C3VZOt3Kxvnl/xT4d8oZ7xv0tQy1cA0K'
        b'xw5dyR2r+N+PT2fXz8c5LuY7v/eDK+9ltxv1ul9W27N59Ny50uOHmrnF7dfdU9/97XdkbH/2o/3+FL2KfPl//ZGrmWPJ058ei5yZPNbj/4VbJ/7Z8gc/+NkP9AfP/tgi'
        b'9Vfq6B/6o4fwhcnLe8HfF/uGW+uG688nxrpcE9/XLbx4edphsTNz7ERG80raN5LtXc8HFjy4+q/ydiETJwMvdV746o2f8hZ/r3StptC96GceP7+d/vM4x4i3n6v//Fvf'
        b'NhQUOzzL6b3z3rz/qMrOpV/+neI3Uuvq1qV+e6x+X+xn5nMK37/vsX9CkMX/7jelQr6Yr/cvvzp/rte//4v5vM1T5ctLDtwMv583d7v2Cq6HfcXggEeuit+U7FpL+tOI'
        b'nJ26r/iPuU699y8bX//6jV4Fl78NlH7x5WsvzF2Dj/vZHvfJPh4gu+ocOWwUOaoWOZK4cmUz9G9zIv9BPeNOtOlSXeJzb6f6dakbE09/dyYj5Lt676+HhGXu/GTk6x7h'
        b'lwKupp2BvXyx679S+uZ3fr+Y/m8NeUYvbt3lfvX99LNTY6YyLxgwnJAjbehLarlXhE513r7CjULxWKsh60PKtPxjWdAyoFu41Z08Yyj/UIbzaNh4I2TBeewTZTgfgsp4'
        b'2SyBtICshhqFrFw50vSrPI5OgYSALxWL7cJoo7dwOe91pVuXT+HKrRsCCY6mC49UTJeEMNhrFuFRVfZNuRu5uKoA1eZkftQqSAlkcE7hpjjHVJ7Pbkrki1K2t5B+Kvmg'
        b'7quKZ2Ba4SY8uPWyeT++BKxj9ynhnnwz6Dos+7o5KRwTu3v+6JUUUXt9YlCaDQ+kblAHs0lxVonag3mxN9rDZQl47HfyhSkDIjJXZz8UMfZVuFgcxEcfhIzthw3ToI8+'
        b'xC31V1T8xeMO/GUfpQ/iCIMeuHzK3yc+af/Jf6J9HlLR0akZMfHR0QWvj4QbOfpkPwhF9wf/ijn7F7kcgdo+X1Ja45mCcmV2g03Vrdpb7QbVRZVF7dnt2f02/THDJzoK'
        b'ugvGL3Tebb87Z0ivrDWDpdy1C0t581ZLVp8797lzX1L+vOcXPN+y8d218X1H80C7TXtM94kO6W7pfu8nmlZzGk80T+06+j/R8N8NCtkNvfg0KOwtjbBdjbB31PX7lVng'
        b'z11FQxaoMZy7L8NRVm1wbVGrPFt59tf7klxpL+4zZb0GyxG5XUv3J/oeT/U9nih7PlX23JXzZMENZDgaTpWyz9T0dw97P1HzrpTZJ2k3e6pxslLuXbZv/tyulK7wwIEO'
        b'9iV40g77nE8qZBSlD+5zPrswlJQ+ts/57EJZR1pzn/OphaM4q/yphTxf+vg+51MLOSnW3mcXqorSOmwIf1RxhKOlXSnY57tz2Tf/zjJITE/aZJ/zxxUNCc/ZvxcffHuO'
        b'y5FR3BfLEJO23+f85cvnwvKF6JhHXatVf9m5eHH69ExaY1/sDo/Nxl9L+VxYvhAdU481a3VfdZwvrHVWiqOjuyul+a60grD7iWLSWvucP718LixfiI4/ckFhrRCilOa+'
        b'2CEmbH9c8ZwVL4RHogZFZ3tzI8WlWWTL/0f/PRf9e/HmbwUyQom4LCltuM/5ayz7dZ4L/78Qlq+lRFjBRUHY+SBxVvmvq2xPfS78/0JYvu62sEKKiOYuEqzyX2/5XFi+'
        b'EB2/GoDwZ3e5MK60/j7nP1BmiZ1h2uNPK86KcRmEfmohwZU+zI7+cCEhYG19dqEvnKloMaaA/uvK58Lyhej4FeWFP58TF3YoVELaYp/z3698LixfiI5fDUz4s4vAWJK/'
        b'H8I9QmUQV3RsQuXFl9+w42QJUjFiQkUktu8pZUpfhb9R9aNlrsQ5vhSdICx9pHykDtIHVu5Kae2HK3KUDZj9cp4rKitdnwmzFwvYF6xs4L5j5rDm+tTMeS3nqdm5v1c0'
        b'6Dd4qmjYf+GJaEeomsF/Ym2df0ftfZ6wqsIHY8lmgXD6Xc+cNeWA6QE33suY1yeydric/8SARf99imwWUvXqHwwS98f4Rlk/ZPuTX7tF5qzFqyzpOPN9grlcriLbHf4/'
        b'xavizxYpnPH158WlXbU5n9eWdzXlJW+l3xXPvkCkH/9VaVqdV4CYq2LZZuJ3i2M01bmr/dJWF9yivvf+Uccbxt2j9poqjj/++rBu7skr9vnPA/ZWTAzeyv31lZHvTk2u'
        b'OnstfOlIRdT7XxorPlttMnrfO2RUZiRkpDalJbjnwM9jDT0GFY9+L+JrI+G/0O0Z+bfdur89o2G8GJ/+6Ku10w9bRoK/mWF81+50lF2Ove2LtdFkjcfv2wdyf2v2g2/n'
        b'9RwKsi40i7nVaHkjNfxHTTFl2uWmb594Z3DSpnXyiyvPC8/P/lRH65+vv/NuoFdsdWDbe6WDE5GpXtZfLvzejbmt/ADHX9ek/eauyZFvhDh+y836YfPP+n7xW6v5n771'
        b'5bmkKfmwr7eM/3jSb9biSPoNmaojkXNzXO20Uz/ul9XQXZkvvfxrqV23ytvnfvx9TkXljftxhib/yB87hZyE7qF7slHfkzGd/FLmgwNZ335X/db4kLVu7ffeLu7pyD4K'
        b'zzX2I1Ml3L5gqidca4uAASxm6/0BAQqwJAwZKcmRhQUxHI/ERWFgH0esCvQJsMR5VinAUgxHpThKuMWDAWfVl8l6bkIb1EC9KPcRuzkuyZFXzjnK04VtvCfKGNQNXZI+'
        b'Xn6SJmZ+khwJvpgUtAaJolE+xtITWHNUgoXBLOYGszW7LhwV5c5Zha0cc6wzsYSB82ylj8uRthKDTnbLSHRy2eWDp6DuVUolvj8X5qBXTBgwk5rrgAm2R9ny5c/yWJ2E'
        b'Gzz/XGwVheSohJ27d6D9dcRU6MPWeFGKpHJoTxM16+eFD0y9+Gq4ylHGZh5s3LQSDikuKNPH28Ifhi6fsOVyJLFJTMIsUXjlFLYR2MfGlk4UJlESxy3s4ygY8BxwTlQD'
        b'OmEYG1gVLz9RjTacpf7N8qylnIUxQVJgwB1m6OsalgaqnsfhX+DCJmyECH9lD2FCI5TcZFGo/Cw4HL41F6ZhJlmYGcyuQBmLg80t8QEL9prGhbXkKGGg0XCcTzfHB+x2'
        b'TB0uXgjw8qOR8znat/lwD1fwZeaxcexjU0VVaojUtX6M7LKmYuzRdjvhtHhgQ1E2q5CC/S9/l/ESI8qvQPELYUbPFWyHZVlcUMDlbPY0exWuZuLSDahREHA4Oof5kr65'
        b'wtgmtgGywqgs5txzrD0OsV6nGA7iwHHhzzDKwSpfmP8gL5gwJ9gOzgnTYl3BRujygRkTL0/ssBRmdxLmvgvwggdH/S1NJTge5yWLspJEGeQa9fJkYUML53CJpXlu5OAo'
        b'tsK4kI+UcDmM7T71SzJnwVvFi7g4jMtcUXTWGflY9pslVh6F+oNmryKqHMjlQ7kVdgsnROEojBLBq7EqGBqpz2Ic6SNiUGOYKGQ0P+g5a+5taeF/x8/SisuRU+PJQKeH'
        b'UHiSYRlGfWhSfKyI20iETCVOWnNUbHnYy/ZcCkNvRWCLwNzTwswNllnAMTYd2CCGszqwJlxIP5sZY+4tzsFhBa4Phyg/hcumZ/4Si7l/ccX/ZzIfzlDxCauu/z5DgoVx'
        b'YYZEcnpyzsv1VR3eJ66vknWhwxFXKfZnr2cC1bcFum8JdHvynghMngpMit2f8WUqfO/57ioZjJx6wrd4yrfY5Vs84wuKvdjrGV+p2I+9njGty17P+Da7n/x+xjff/UPv'
        b'D53+8QP13VfvZ3yr3T/0fsY32n3z/Yxvtvvme19MQlxtX4wnrfVMzmD3Y+9fv6NwgHlyWh8Uz+Q0K31fvcgiltYSUuyHsur0M7X1unimqFopzl5USVyNqrzL19198/2M'
        b'b7D75vs1DfclLpwWZ2b2//z7r/53LYeAUZWMwGMM+NUkzupwQJt71poDOvJnLXlgJsaOLbjs2JLHjq3l3Dg8OMOlUuQAme3xUhPSs/pJzvbEc3IzUxP2+KnJ2Tl7/Pjk'
        b'OCozMhPS93jZOVl74rH5OQnZe/zYjIzUPV5yes6e+DUy9ulfVkx6YsKeeHJ6Zm7OHi8uKWuPl5EVvydxLTk1J4E+pMVk7vEKkjP3xGOy45KT93hJCXlUhZqXSc5OTs/O'
        b'iUmPS9iTyMyNTU2O25M7Lwp65hdznU6Wy8xKyMlJvpYfnZeWuiflmxF33T2ZOikda2uXkM4ymuwJkrMzonOS0xKoobTMPb574Dn3PUFmTFZ2QjT9xAJw7imlZcTbn4yO'
        b'S0qIux4dn5yYnLMnGRMXl5CZk70nEA4sOieDfJf0xD1euJ/vnmx2UvK1nOiErKyMrD1BbnpcUkxyekJ8dEJe3J50dHR2ApEqOnpPPj0jOiP2Wm52XAwLEron/eoDDSc3'
        b'naU0+cC1zDbjvE569Jl/+vofgKGwYAkjsgu4n3Gf6U1gVOByU8WZt/H/d/nndbX0pV3tOJ+3kz/L5/1G6hqJQUJcktWeYnT0y+OXDvBvDrz8rJ8ZE3edJethEf3Ybwnx'
        b'/qZSwohle5LR0TGpqdHRomkWxjT7Dk3xnkRqRlxManbW59nahCXJqSgOmjDYG2OL30g5Ej/npiY4Z1lLsnCExBt3qCD85nL3xfhc/j6HFXIcWUGx5D4/9zRXdZ/zoTIz'
        b'l7wCpbeltN+S0m73fiJl/FTKeJ8jxj2xa+H8uSOfO/J5ky+Y7Fp40/uZlOIzGfVKi10N2ycyx5/KHN/lH3/GUdzlKDZoPuEceMo5sPvqLezf/wWrLi+I'
    ))))
