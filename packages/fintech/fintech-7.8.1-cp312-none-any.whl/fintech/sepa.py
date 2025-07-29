
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
        b'eJzEvQlck0f+Pz5PLsJ9JNxXEBACSTi9EK0IKDcKeGEVAgkQRcCEqCBar0oQURCtIFXAEzxR61V72Jm222u7IHYF1t21br/fb9vt7mprt6273f3PzJNgELTa7v7+eUEy'
        b'z+eZZ87PfOb9+cxn5vkTMPtwjb/fLMNfe4EK5IJikMuomC0gl6PmLrMEoz4qzgmGDWktVVwOUPNPGO+sAjrLxRxMEah4pjibGHxtoR5+hgFVfMsSqeDBMqvsxDlxkhXl'
        b'Kn2pWlJeJKksUUvmVFWWlJdJZmnKKtWFJZIKZeFyZbFaYWWVU6LRmeKq1EWaMrVOUqQvK6zUlJfpJMoylaSwVKnTYWpluWR1uXa5ZLWmskRCslBYFQaZFT8Y/1uTGn+P'
        b'v2pBLVPLqeXW8mr5tYJai1phrWWtVa11rU2tba1drX2tQ61jrVOtqFZc61zrUuta61brXutR61nrVetd61PrWyup9asdV+tfG1AbWDu+NmgvMLgavAzuBj9DgMHX4GTw'
        b'MAgNFgaJwdbAM9gbrAwig43B0uBs8DQAA9fgYPAxBBrGG8QGvsHO4G1wM7gYrA3jDAIDx8AY/A1BBseiYNwXwnXBHFAXYGrndVJLwAE1waZrHJaawgxYH7xemg38x6Cu'
        b'Bmu4i8BqxnKLlJNRaN6nkfhfRBqFR9mgCkjtMkqFOByYwwGEdq1QWXpAWAX0gfgCbkiD+1E9qsuEF1emzUUG1JApRQ3J8+bIBSAokYfehBfspFy9J4n7unxB6jh0NFmW'
        b'LEd1aHs6H9ihbdwMtFWhF+P7GWtqUpNlaJtnMh/weAxsh62Wel/yYBfcujqUPIKa1OnpyahBmswDTqiZC1+FJ2KlHJp8ITyPtqVGRqELxThGKtqRidOx9+NOXTCO3keH'
        b'C+AOfB9uW5OcnM7etkOnuREhPGMKuB6b1urIvbWzcPHQdgZYJXNgDxc10sqWwpdhszU6Z48uwKvWOliHLlWgV1bCentbALz8eRboIGqUMnpXHDdWXYbq01LWF6LtXMBF'
        b'bzCwDe5EXfiulNRoOzwCL6XCU8EcdB63xrZUtB3WZZJCwYawDLlUAGYnWtSoAI7vhuPjJoVn0XlcqLTJMzP5gF/DoMPJ8LAxs+kl8I3QFLksHB5PlysYYOPMtUIbBPiu'
        b'B6nWidIloUmykGgBqksjlbJGjRx0Gl4NLWTMOj7K1PEQf+2JrMWdj/mSh/lRgPlWiHkVYK61xlxriznUHnOsI+ZqEeZYZ8yrrphj3TGPe2Ke98a87Is53Q/zrz/mfsLX'
        b'QYZgg9QQYgg1yAxyg8IQZgg3RBgiDVGG6KIoytdYOtRZD/M1h/I1Y8bXHDMOZtZzjHz9CHWYr4sf5WuvUXydyfL1u6stQOVK3P+SfNkX+c6AEo+u5gLxDNytIF8WE6tm'
        b'ie8GC0F+FJYg+fk2ianPG4kZPNAzzgWAGfk2H8oDQTcotcLkEA833n0nMOOuqIr5Xdj9CJ06C5QSEVrt0sL0WABJuHuZ8M+R/VMYlvzhgm/sd9szwXfBm3nvuv1YpgBD'
        b'QC8nrPKSyhE1JWDerA+bGxyMtoUlYX6B3TnBKelop0yRLE9JZ0CZveU0dGC5Pg4/kZIxXlepXbVSr0OXUA96BZ1DF9FZdAGdtxfaWNlZ2lrDndAAt0eGR0dOjJgQBS/B'
        b'Hh6Abyz24lmiU7DBQ5+CU3GAZ+1S0+AmeColIzk9Fe3EY3s72oZ24HHYgMsSLAtRSOWh8AwenSezcBrn0F7UhPagRvQSaka7FwDgGm7rhFqcR3AZaX3Cst+oCJdxiNTF'
        b'fMZg3uIXcSkf4FmjjjfMB1zLEb2Mw1yzHues5xr54BHqMB+UPMoHvFF8wMvQko7ULNycxdMl4dAb35a0fRC73+/FiPomhlsZeXrrtt/emTMXNb6zXfqqx6x4versnfnZ'
        b'1378sPf9l9/Z8U7ZUY+tn6TN+dGr5evvP7Ipup3GBYrXbRf95S0p/747Ts4DbhbDXXj01uPm20nkAW8KA8+WLL5PhnYOOoEuhCpw69bJGKANFsAdHDncEHnfhXT+mVR4'
        b'MlQenCTngFK9AO7jyFF7LH1OhjZVh8pRQ1oEH6CDNoJcBp3CrV9335kM+atxuNfrk2y58BRutHXMLHRCKuUNcYKlWgd8/+GXjjSDZMOGDQ+cY4u05dXqMkkRO+UqdOoK'
        b'5fQhrl6jqiZfHBJ7Dv76fgO4O4sDxC57JzVNaolunmZIGBA5sxftMa0xbbH9ouCbIkWfSNEvCic3XffGNMW0aLrE/SLFTVFknyjypmhyn2hyvyim1ybmG9ItWgsi5gRD'
        b'lmXKFWodnu3VQzyltlg3ZJGXp9WX5eUNWeflFZaqlWX6Ckx5WH4BGaP5ElwFrSMhOpExRsqbQO5G468HG8DfEzkM4/2pnWv98g3Wdzl8Rjxo7VQ/5VOe/Zb0AaH9oFD0'
        b'/T0sVR1MVw++IRzRLPAHh6wV3ELOWPxTRBiYa2RgHmVhQRFvmIX5/z0WthrFwo4ZesIuAfNgvS6Nj/u/Gw/9OgCPoePoKr0FD89GHan4HiNFR5EBoFrMkBvoLbQPs+Ae'
        b'dB7PKwwfHYHnALygnKEnOSidI1E9oSeiLtQF0J4cV0pXw01yazx/M47opakAXl0Oz+hJw0fgCSiU0Of6osMAtVU4spmfhCfmhioEgFkMW2EdQMfwxN2qJ/01sRruQc1z'
        b'qWDMBOk6JYUC6PUqPP1fhd2oGfevDMg80WGppZ6y9il0EtZHotqpuFfQi/hPhbbTzN1mydAVxVpCPoL/uDgHUla0Fb5cNPl5eBWnhPbiv6o0lt4lSUgUI0q+hP/GwYss'
        b'/dLyyudQM7yKATHaj//WzGIz7oLtFanoRURvvI7/xsOTdPqF2+ABPNxOZsOr9vhWB/6Dr8AONrWG59FOWD8fHeIQsGmNTk2m9WbG2/vDN7NxUkEgCNaik5T6vIMQ7VqE'
        b'mvFgCAfh6HIB23yX4dEFWKbuxWS4Uw13grwaeJhmjTbDQxhXnNeh86sqJzKAg7qYAMk6VqDN56dyda/j0CS74nWNEXYw3CbxLwHpnrkLQ/96LaJ68+nK40dS3BdbvvQZ'
        b'mLXHgVvwqeD1AEeOc98GV/t///CP3y3Qc3+7OX8J189y1+Fgv3SpWlWinzT9cxfl3P4T7dFBPyo+njP907aDm75lHkQ2Rs502eicJ9txhNv2zz8sicseiuR8hV6eHXbn'
        b'Y7v9Lft/dYqTscIjuafox6b8wl/vUi55a9HFg5vnR8d9dz15voVbxUcvv2aIWBB3T/vGg3//7csZf9LdER5dCxo2hB11eccoRS1QHewIVUjRNhkAAniSA4/D2ihXdPE+'
        b'xTgH3eFlDIGQITktgw9rrYA1PMtB+4XWVI5K5sErqF6GcSGGpYKlnAxk8Pdec9+fPLnRE71KZ1csnevQfgz7cE4nU/hAFM1Fu2AHbLhP0evReXEmCQ4vojajFEcGuFMq'
        b'fESoPvZLR/pFIiHSyiivhqzVZYXlKnUekbbV5hdU3vaz8vbeHCxvnQdc3RqFA95+XeKenGvihwEv33t8jqufYfZdAXB02mvRZNFsaYgbtHcfEDvvnd00uyW+Oa2RGXDx'
        b'aFE2aQbc3NstWy07Arq4/W6yxri7XODq2aLcpcEP+wS2L2ldciCvybKR11hInk5uSm5RdcT3i4ObGBzTR37bwfOmQ2CfQ2BHUZey3yHcEDfgQLPsjOt3m9IZ17Kyy7Fr'
        b'2XHffY4dcX1uU/odYnAMkZjMDs1Tem28fviaC9xjdDakRT0t44EQBvLwNyv+LYYY3ZBVWXmeDmtwJWqdlvSd1nWMdrQYlvpGsS8hEsS8+ZLNxP93mVj8ez6r+N8tCACH'
        b'rcOeRvwTBMMfIf7/cwim6KcRjCWLZGekOYEAACYv5ubXPFizksWnzuuTQSMAScUl+Sl/mBgMZlEqb6EjwE0mvFWVL4PaOWxUuZc1wNI3OMg5Py1o9nOAStVJqHZ9VDiv'
        b'HGNR2AwKsAKhaQ7/A1dHrASpl++0fRC5f2NdZ/OV5pUT/Lluh8OLoiLCxbpDdZHqq+Hh4oj5nHfOdRS8lz9h918LvlKFOHGOK9/N6X+fF3XKrfREVYZVqtVmMbexKEm5'
        b'p6CLs+3mplswC4FLe+SLN2/0a9kY5Q1mdzm/cslDyrlP2CA4PZmiIbQPtnIAi4eOwcv3qZbYAF9JCVUkY7WsVhYiVWBwjKdA4CbhLUWbMPzhP35U8gGLgYxD0rGwRF24'
        b'PK9Qq1ZpKsu1eRgAjSbR4ZlvHJ6VHOAgaoyqX9Pit62mVdcR1bama9y+dQOuXgNOznulTdLmUEP8oL1Li659fev6ruIbvhPJPfxMXOPMRosW/5aClpUtQX0OfnjcigI6'
        b'5vaLgrqi+0RhvTZhWtLXpvHBLdSohiwKy/VlldqqZxgexNQxRiUWmw8SHR4kHs8wSLREfI4C95QzC4yDg6qQD6E9M2Jg/FIVb9TA4I8aGAnswBCHisjAAOHrawXlq2KN'
        b'Y+DURAcyBiaHz0rIHD8+EuTQKdgyDO5MG0+U4QgQgflsJ4176QUewL+S8PHnVavsg9mhsRRuTsTgqSmKR8wmkeiYmsaNXMoaSsLnpzofZhYDPekS9OKidUr4RhSHKNpR'
        b'E/Q05r8m2QKM5YPDXdbGAo80wCKGjmy0QwDPRWFgEg2i4VG4iRZMBneqItDLUbjBJ4AJi+DrNInrPs7EjiUJX9/ktmD1BLZgcqyr4JlqTxRukYlg4kS0g8Y9IvIGk0l2'
        b'S7tmbZQK2bg8WAc35MJtURiKTAKT7GEPjTs00w/MII2z/rLX3GXRQI+RDShQoBP8zCjMXZPB5FIbGrFrTiBIIgVg6pQNGmc20SVoDzw/3R2ex+EpYArqtKVxfzdFCrAG'
        b'ER4ep1x5NScDsFjvKDwwE73mBc/jRosBMXAHukpjr1gvAwtJcSPesn7HBbc5aQXFuPGoJ5xoLTPBTHQVXaD5WfHQm7PhJh1u3XgQj9rhNhp59WIG7YcniI6QABJ0sI12'
        b'xQvoADwiLtXhhkwEiXZCtn9et1zChyeJKJgFZoljKRHu0o9DG/N0uGlmg9nFZbQRJpTNsp5KRlgSSIJveNCMMuWh6GglItVNBsnodCp93CIn380ZkWqlYKUcdlFibD5s'
        b'KJuNzuOipoLU5/Np+RcXOMPX4BvoPC5pGkiDB/JpC8ACC4BnSofwVWtn+lsuZDlp5SR0yscPncfFTwfpwRNZXl5lRUS3MHz85Tm/tY9iWxaeQq2W8CXYgs7jamWADHgs'
        b'hcaelxyEs8HprpyVrk8MZvmuUIbhTRvags7j6maCzHi0mUY+sDwU5JCk/Q75t4wXskmnwxfhlSmoFZ3HDTEHzIE9cBuNbQh2w9AVd7EPZ/z15UlskWfAqy7ogILYWueC'
        b'ueUlNOa6tULgQGIKNrqf0axgCwFblqIe2IC6rXGrZYEsaHChkf+RYk8sOG7hs/SZYd7xLJcFY+S7BV5Fp61xY2aD7ExvSnaCBgZTN1jjxszB+vVVV5qEf5InHk+4Hgq1'
        b'To+HOzvYjmIt4yxshOetcXvOA/MqktgWUvqAWJLf0l/netuvYyPLV8AXEe4ka9ya88F8uBs10cie6eMA0TbD4xLXRKRnsnWeGidygN3WuC0XgAXeaDuNGRbvgrUZ3PB2'
        b'8x1OJBaxyS7GXdQAt6M2a9yWC8FC2LCARj43UwGeJ2VwzJ4UzhexdS5xyX8OvQnrcXARWIRegWwR3lofDUrIKJxy3iI9x4adz7uVkYCYWcIX3V09b52EJa7IDAf5ZGDH'
        b'HZSvm/E8kHIoB5cs0MtRA6zHzZ4LclfA05TKxfpGLObMetzAi8HiudNKv//3v/+t8jAKQ0FzbD6ef2i67gETQSmpmuaT3E/SJwLNbm83ru453Kq/OjRb3/d+BifOQXD7'
        b'+BetG+euzAOrLSa9ve4t77QaS6fXf7R4x3PX7cYDFm5/anALWzrl3i4X2/i07eu+j/ni9JtTl/zY/cZ7B4Mdr3iPj7oWlnjQw2L+Z5s6zuX85W//9Nn/r39+sNH7yrxv'
        b'X3jn6j/SKm5fdLMMSLSPvxO+e/Km3ZO3Raz0Et0JOPq25iPD+RZR//i2iMGT73/c9tWm9xX7vsqaFPqdrO3+tuQz++571ETU6ldy2+64XHwndtXbnFXvTPuq3iL/nsPs'
        b'OxEZb2e/XJf4cr3rZfGZit/fmfgnwaXgdYtX2Fm+3zjt+NR7V9NvfrBo2z+qMndWHbSoD35l5hH59+kLHrT91mvKJ2//8Q3NhO/rrpapowKT/3V3wvLBD3vzj+Q3/+/S'
        b'9JLZOy53X4x6/Xcf/n7Kv+J3cn53rDpy+rTZE97J6by2rLft+JzNrx/znbdeqbyyE+s/RP/g5DtjDSZjGVbb69IwtmGwhnOCg06j41xq8gkNXkSg0XhYJzciI7jVjgVG'
        b'Wxn0aipqCEUN6fIUWfICuIUPnNBlLqqFB+Ahak1aiw4wePhvT01OxUP5FNawJnPc0WbFfQkZJO1oR64OnkrKkAdTK/zOcTO4wBE1cnHcs+jAz9B/hpHJkJ0RlOgL8wh2'
        b'r37kmsKsBRwWZiVxTTArYhsBV7dFLo3aFqZx0t7nmp67IQoYcPU0w1sYw7jbEYw19y6XhNw8W4whiX+HMRQc2mUMhUf1GEOTp17OYkNxCdcK2FBK+ntaNpQ9v3dhLht8'
        b'Pq9XWUiDt2kufBKiudAQzYWGaC40RHOhIZoLDZFc7tEQzYWG2FxokM2FBIl6J8b5WLBhd6+W4bBfQEeWKRwi7yowhaMm9mhN4djnrjGmcAIzm3lv+CqNyWR65wwnlsMs'
        b'YEj2xsslTD5DikAvhaQIWXct2bCHd0uBKew/vkNrCsvCejj3jOGY2GvjviZhQ/JdG+DsYki8y7Gx9b7lG9wl6sruKuhy+61vZNNsjIQrsYLbErFLf9vNu8Pzpl9kn19k'
        b'T3S/3+TLODStz21aK5/U2qfDvSu607fPLRxf2wJJ1F074D2uY2ZrSqPlgMinpapPJO3K7nHqXnBdFD3gKcFqq3gCLofY7fv7fCD2/howtt6Drl53ufj3gY7OOgFx1vGR'
        b'AEVaxk/nomkM/jbZI7mYER+Ps6nx0Qxmk8WzRzmYSGCKsX8gdkguwzg+qyK6SzAOHLSWc38Sa5PFGmCGtbn/Maz9FGZ0CxZrt4RgTBswyAFz8tPSoouMWHthAMYnOXd4'
        b'wCE/7YTKk534fMWoDauWAOjRWaJb2sPXNYHajRxdNr5ZH1hDjPCdzVOIEf7k1utLPkqz2b99/0cnOpdluZ1vdXPb5hbaGtOa3ZLtdnjDg2y3rJYjbsc3nLtgM+OTtAk2'
        b'FZ/IBj1sbN6yubD/5S/A25vtwoLPSBmqRBbDU1lGmzqRk3BjsRxtRLVS3pgSy2QfZ6WVB9u3ukqtvrBSjxWpPK26SK1VlxWqq59wj0qxRMDazmfyMC8Si3hzrCFh0N6p'
        b'Mbq+yijQBhzw+G7MahS2RHdwOhxbJvc5+D9RIxQM8XQ4l6fn0MmEQ59Q0k3m3BrHYxinZ9EIyYNPwaUjNcL/HJeO0gi5o7hUkEHxq2v2c9ZaYsc9CVvRYQBb4VYWaG6I'
        b'YIFUj5fOSWC9HMzS+CT+lasj62rohzCWIyNMHLl9RlVR2g/idz+ZsyTxFubOtP0V662yL1rPeWHC7rO73IM/3uBgX3T7I4zZl9jIIm8YjRjo9Ux00MiA9ugEO1fXg/s+'
        b'+F4oOoaOhSqSRxgw0B60h7cUHpFIuY92L6ngMHO6PaLfP2TNx96hjDnByJhzzBmTrNrgWbUj+oYouDu+h3ci+TLneAbm0UGRvEvVL4rqtYkayYiFz8SI0wkjPrZcdeZs'
        b'mPmz2PBprHZ8A/P/n9VOwArMvCx78HlMDIbp+bJJNnoWTe9bzAMluc5kVbm0ICOEJSI8WvI1xHSan/ZpgBpoWnyqOLqlpHg1G6khrpmY4roxgzKik0Vbei9ggTnBRr09'
        b'0WqG/qOFN+K+EL9bOl6wddwfMv5XfDREIdiqKJLUu8ve/cgy2t/NsPHi2cPhb6Wd5txRvOsTpNzwsQ3Q9zuJvvo15lvSrVkYL/bEoU3wRFq6jAN4qQw8FxRy35s0l1iB'
        b'wSnaEZaZjhoy4DYmGZ7kAdcs3kS4O/QZLG+2Zeo1lXkqvTpPpaxUV4+8pLyaa+TV53lA5DroKevKObOoe1G/56RGIebYljV9WEwmnMnszuyXTbvGXJfFDUikXXGdto3J'
        b'A66Sjohd6wbcvG+LXA2pGBa4ebVqupi20j7XkEYehhIi1xG2Nh7JdMiyVK1U4fyrnsUaTbTBR0q/E5iZ2hbznm05kjW1mTy0yEdgYqdSwtE81nsJ8zTHIKDWaAuDsEhA'
        b'+Zo7YjGSZzmCa3GYZ8bB3PU8I18/Qn08ELAcxdd8lq+Xc6Ow9lki4YH8SK1qPcvC1bF8rDpWAP6M/DTV9DCgiZ3TzOjIpDP987ltH0zE0lVulK4XbCbYLPpozWfuUxfV'
        b'309ZqLyz/6R0+4lWyVdukiUf5nx46/25KIf/2eqV4NcFKPrE1ilTt27sNFzd2oRHQOiLmgk3erqnzcv/JnWy8ssN516esH2/V/g3b9W8dprbevP9HaU+222jDr10ZGtg'
        b'y8bzfLA5ymvZexFY0aKrbQenom66IGQBOP5ieJCZlw+vsJL7DHodXU1NllEPJfjqCuKk1LCeXR/aW7KyAF5NRXXEjtKQyQAh2s6BW1DDQnaF6vJ6dBjfMYRhsc9LR7vR'
        b'YQa+SawzVAFbjV5Fh1B9OjyJOwWdQFfhFmY2fNNDav20utWjTEmsLSZVa3iA2RSrzcbXiCs6vDYbh1cFHl6ee2VNsmaFIX5A5LJ3ctPk5hhDwqf2zrdcvVuKOgr6XaVN'
        b'vEamMWLAK7CLaU0n4JtGa1m5a9qAp28nHnaHZH2eisaEz1w9PnXwblF1JPc7KEiosL2ktaRtWfeUnpwTz/X5xPQ7TP3Gku9mZ0jCGoLYy5BpNg4tyTjEg28WKb6gUF9Z'
        b'XvT4WYatuSUdjvlmq2zaDMJ7I6rbSmJOwV//wOOxHI/HwHsAfz0rNt8rCALHrCNHYvNhQzSdbvjD2Jw4UoEi/v8LfO4yalj6ssNSW/YB2I2ZEyzTW86we4Edlr97jrX2'
        b'bkjR1fzdu5wlpi2zZA101nqbq2tVLFHJrhEJwfritPiEBJbYoGXt60Cm8+p6PgmUkp77fAJrbe6x0sTKWMv4uwuM4MqyzOn28vnsw1OLBdTIeTdbW/o+E8oSDYpgaime'
        b'MVfJyc7OZ4l7pkwHNRgQ9UQUOqnSi1niH/2mgTXEl7O6VKvNmMkSv7eMAZW4lBX2ayNz3KaxxF5fd2qabFTovXjSdSzx4ArWyDzDa1XBb0qNs69TAl0dm3ztOb1NdRrX'
        b'uDrGiwMbSBsVlDtNcnFkiVVzWVPYhllKWdoqoyksO4c1698OLC21XGisZnymBzU/Au/q5zPLSlhisnISNZqBgvXa7x3HscSm6LmgA2dUUbYqZV2QPUt8NV4N3iMZea0f'
        b'//wkW5b4fkIRwOjSYQOnuOhy4UKW+O001sbYy11XU7tGyxJjHe2o/RRwitLkIUZh/F3VWnAfF2nOzOL5X8TOYomn8lmjoWR2VWTu2kiW6B/NWjjzOcs5lTP5QLM5rICn'
        b'wzIO/KvxvYbm1Aw0w2br/rTxfyuuurDhRmGP8n3bar714fkFffz696Zck1w0xH+2a6A/OTcwbtyi7f93Prz/33+M2vH1qReuWWS3Hv3u2vT2Bk3aD8zsFSn9pS1fXYv+'
        b'/ML0GRafHxpXMgEcf0nnJrzUtCr2lavvfb17gs+79R7v//DVy6/4zbYSZWXFHziVLLcNvpZ2vOrXv99nuyxr4cDC9oxejUzaaHjl97XvfXfH7k/u71/6w541v/uX43xx'
        b'VsA9fkPrO7/16+T9GVlfO/uZ1PlOYMLxav2+BXvfOKY4Fjwl+1ffe7tZnojwGb/ib40xMR/nPYj5y5cn9Z9ZHXK/cuD7Pz4fM2XV1Wt/dYk5PTf9n5630v75N9dKjx/r'
        b'yhq+3SK2vlTV0jT324tfnpv7w+SPJxyr+duDvOmvL57rfeD75Suk7Znftuf+bXnq4NJf/znY91bsbasfLzV/9j9/q3KZd3HzZ9+6Np3c5JdYIOVSNaAG7RRSQKWEx1lM'
        b'NQyolPAQnYumuJekyoKTUEMqo0cHgBCe4FTBLcvZKWzjfLglFMOxEEYdCnh6BtVJUY/U6WdOJU8z2ziZZhvTx2zScSRyt0BZtjyvpLxUQ6R59WgSnX4WGg19FXwgdm2s'
        b'bJ5iSLgrAFgpXtdnHzDgGtCRg7Far0MIsYQ5t3CbrKn7QaOyxa9JTZwbOuL6nIlzQpdj19xu5x6nbo/LnL7gmD7qheDg2Di3xbFpXsvcpkUdEX3igD6HAEIWN2qbLHHA'
        b'UdSobHLBSXm0aOlKLHkiq8miJaKD0zqpY27XuM4FfZ6yHseegrOufR5T+hymjHjKMHPA0alR1ZLTMbd1UZ/L+C7HPpeQLmWfc1ifYxh7s6Alsqm4w7FpSZ/jOExxIlkH'
        b'4YC9Y+PMbasH3ckkGdeh7ZrZubrfPaxJ8KmJ0u8e0ii4J8S1bsxpiWhR9jtIBhxcWt07Itq8cH1x2PxyENfJFI0NR7Zo+x3GmYdJE7riJyLbvPscxrNPjw6bnljZ7+B3'
        b'TzA6e/NYES0FONZY+Zk/PUZJojzI1H9vsnkE3LJOIhaAdMRddwocEDu3Wnb4tdngfmskrigiseluv1PgbRvxzsy6zJa4GzY+JJxel7498/a4EEN6S0Cfje+AyHMEphAO'
        b'8arUSu2TYcRDg3W+OTdrFxAoMZp/T5vwBNZYv1vExxrrXfCMaisF+eaTOM/4+802YLKeqMmWDJCL8YIlUFlQr0MOtaVY5pINGDwVZwswbbDI5VMK14wioBSeGcWCUvhm'
        b'FKGah9UIbhFHJdgiNOGNXEsDWMPkWmUDrNoKhyziVCqtWqcrFJgVV2jCHKuAScs27ajAAIh4kHOobkK9youEFAbhAtVZDcMgCwqDBGYwyMIM8AjWWxhh0CPUx+9mGO0S'
        b'wM+g62iwMXsavAK7iKnRD/jlwqusz5zthGlc3Q4cCl7+WdsHEfv99ne+1Nl8Pqlnqx91Btae3rot0ssxslIrjtKfc1l0JLwoonDu+3PfWvjR2+81cnK4hUci3qq8GVkw'
        b'6c2tEfXO2ZUTts8a+DV/ld9Ul7VXHI6nTL598KP9pa/fmbHv1FblBNEN27T9X01Iu1daMeHkDJ9bb2fYSew720Xv/WnL1V3Slo1RXDB/qe/F89ZSK6oloB1r0KlUeLLA'
        b'KPlZsS+yYDWQJnesoJicjJ3REaOH2m64hT4M98KDqMXchW6+KArunUrVEwfUXJ2alARPBSezCaOrHFgHa2E3nW3gaWiAXaEKOWs1PcxJgVfD52fT9SWsuZxDHagOnYf1'
        b'cCfamSqHO+FOC2DtwkG1oTXUQDAebWJgfSaeklBDqBS2oI3wOA/YW3IrV6BzbNXa4IE1NIoMdvOAQMiZMNs9BLXSFSi4QUO8KMOw9qRIpls3POCLwAkd4eKENqKm+8S7'
        b'H+2DVzPga+hVHFEhTUmXk50O9Rx0SQY7f7EatWGDuRplkZdXpl6dl1dtbxwHCiOBzmJE1SdK1BoL4OndaDEoch8Qe+7NaMromHhDHDIo8mytHPD0aZ/cOrlj4cGlPU49'
        b'OedyL2f1Bszo94xrTDDFjT4W0xlzKPaGOHxQ5Gsikstbrl4tCzoK+1wje6IuW/S7zmjkDUiCGnm7bQe8/fCP1YCfFP/YDfgG4h+bAVfPRmsz4Wc9xC0s1WlDSD14hZrK'
        b'qiFhRbmukixVDAl0lVq1unLIRl/20Dj8eLsHaZt8+jGzfRQT+fhou/yTRJ+Kv/6FpaPegmFmMN8A8v0M8pHK4pcFMnDSetJIfYsxjXIvOsprwDIw+oMlV4mUyehmhoR5'
        b'RgcqKTPE06lLi4grCJCwXSuMLVWuKFApp1c7mOpgotgyxglhA+hKOJN+PJ226s8qyRZcEpw7P490gJTRVpD2eVgK7UrSiKMKYIdjfGMsgPiMx3GPn1+AYrYAlnmmvn/q'
        b'QtibFSLnzNLjS39xK1jksWz31EVwMOuI6DOxx2NHF2HY3JoP2H0m7MIDntT+88r3qL1Go5cduBmaPacT+LpxmHDT/zdtH0RTr8nOYVPtWzYvXwzRgBU1PK+p30sZKpPh'
        b'FXQEXhghE+FGuNt9dZqUYzYKicwZNqBqdGbLOtXOppYbQaZCivgMEKhdIgRuXi0J7SmtKf2uQb0OQWaigk/7Y6zxTw23Zrsu1pF+Gjs3J+ahKf9bpfDZMBFltCaBH+i0'
        b'lnHx3E0+WIIJsVhRrlDn5Q1Z5eWxe0Fx2CYvb6VeWcreoXIIizZteYVaW1lF5Z1WQ74IM2qXm0o9ZEv2lSgxlFGXlublSXl4TLAE820mD9cCZwwLOmKKrjYBoe/I/SxS'
        b'yy3grhWYwSQwA5ETv+Pa23rdGwdcfft8p/S7xBhmY+nf5xXVL4o2JAxiqmRqv2usIWnQ2bvPZ1K/82TDrNu2zvc5XNvgb7jAzoWGaIfQjQDrVsArurRkqWp2ilwhAFbL'
        b'8AQrch3BetbG32+icS/vcXwIGFUMAYgLQA8X/9vjfwfjry351XCKOMbrEf8nOSeMCI8CzkACNzGOM+0DdMAojrfFchgk8sgeYAImVYKTFieMKzAUdPJVQky1NKNaUKoV'
        b'plqbUYWUaoOptmZUS0q1w1R7M6oVpTpgqqMZ1ZpSnTBVZEa1oVQxpjqbUW1xbaywTHDZIsy1e9g6Kgx+T7qaADGtsQ0G2W5mcNiepue+BajtVR44RaNtPtdhRBvbn/Q0'
        b'5aUaj9MhPuJclZdZiznSdLxxuXzMyuVEqb6YKjGjikamjf8t8L+wiFB4J/1MZVAFYYzNMe7ZJP1kZ7AvslSNM8tVTNP3x+kHmKXvXMXFU2QwBveFdIJ8EGRlrtEbqez2'
        b'6hF3yOqfBmtDQzwy9sYaahmFFmZMageM8nEL/tojHLn1GgtqSyyqubjozPBmU9J0wCDADGdHBbjFCLVBaDlCKcBhoZmotlgvNArwR6jmAvzTH3ArjKgU+SSXaSo1ylJN'
        b'NdlNXqKWKI1NoMHwSFlWSLajP/pITIVSq1whIc0RI0nU4Ke09NHkmXEZknKtRCmJlFfqK0rVOBF6o6hcu0JSXjQqIfJRs88Hk4dlkpnJ8VKSRHBcfHzmvIycvIx56TMT'
        b's/CNuIzUvPjMhESpYsxkcnA2pcrKSpzUak1pqaRALSksL1uF5aJaRXbJk2IUlmuxHKsoL1NpyorHTIXWQKmvLF+hrNQUKktLqxSSuDKWrNFJ6FIuTg/XR7IKt5kKI5vR'
        b'xTE2D+GTGFouEjLt+Tc1L9apVWrtYx82ojf2eeMFbqPsTHlUxMSJkri0OUlxkkjpI6mOWSc2J0lweQU5PkBZOkYDmjLF1THmiENjl/hp0jHhLTYt09XPT4+FTmxqbPhn'
        b'pDViChlW44fRi02GnpybgNU2gzNZ3JIp0A60PXUBMqSiWniJbuX3hQd58DW4AxqoxXiTcAfwWvkuA8Lzy5JFLkA/CROdvWAtXeOagwxEzQxDdTiUmU3S2Z4+L4m4GKan'
        b'J6czAG5DB+HeMkt0EdVa0ATbPSyATcWPArJNWzlrnHFz9IvooJz4LYamkm1baXOTTBrmcR56Eb2OdklhN8iOs0B7ywLYRQAsOXgVB3Ao3+YHWzfWvL2ghgeEk08xZA93'
        b'Q5Qf0CtI2lcifE1J40RI6siQloK24+KGZSWhbWkCMBsdEaCzsBNtoQ5Nq9BGHmembiXZgbkT18EBXdUkvfhrvs4STyXeDdp1u6aVbQl3eNFi8w8Rzy3atyf471ZNF4es'
        b'P3NrKjkZXBBoVdy2pyN50v0+n02pReEDb298u+HHqgPtf8x/Y5tF+DXwzucbfTbPuNdU0voHF07jge6a6sPbFxxR3XQF32b/+Uzu/U/m/vkvB2xO782rfuPLwPvZu4RT'
        b'XFpeO9v0a2f9LAXaNr/Bvi1Ccf54eOn3FzOKDy07cKF2pfeaD5vePKf5JPtC3b/+7jO5KmjtH/Z/q3tj4WurPtkYMvX737xe+/fWv2Zesmp189Uf5A3O70wZemEotSgj'
        b'43Xl/F8dvc40/YXPb+r5TDTopc0qsvsfO2e7QfH9rff//qC9YPyLR2903up1k10q/vatlTLb3/tV/VtwTpucFSGUOrHmilbv1da4baXpenlIvARtC+MAZ1jLE84spCaD'
        b'HHQyi3i8ojq4dYa5xytsQHtojGLvxFRFSrosGTZMQq1oJ+kcLvCAr/DK7NZSs8VStBW99NDXCx2bxJHHoc77ZLEKNcG9cGcq2pGUjnbAHfhxdBW+RpNwRlu46DI8v4Zm'
        b'8xzsRmeGfXLgYXhxeGNR6ZT7YSSpC3AfNGBmwamEInKOA5tmWKo8BO1IKyQus1wwG561gDs90D4K7t2zl6VmymHdFLgjk/KS9VwOfmYTepVudxR5E7drU534aB886s2g'
        b'V6ctZheiW2F7lqWIqAbkUS5qY+CO5Ofok3LYXESeTKXDko9eRY3oNQ7z/EpqJFkPu+Bm1hKTA48ahwo1xPjMuk+PpjgIWzJwE58l5pYGKT2og7SwKcFQeJ6PXrSFR2hm'
        b'z6NtcKu3JU0wjcEFaWdgI27ZjdQnebV2daU1vqdIJ2W8yMA2MWqltVdaoZdIIdPR9rVh7IK6XTE3JgO+RJMN8YAt+Lm0ZNgdJqVY1y6eO2sZTpZwzhJ+OXlWRoQNejEs'
        b'Q57EA3awi5swYY3U/j+5qEG2ewxbfsztP1j/0GBokJeHdVNWyipMFKpcZTOscrXUErj5d0T3uwY38gZdPW95BHQs7feI7hVHD4pcyPpGi3bX9M88AnoDZ/Z7xPeK4wdF'
        b'Hq26jkltNV0rr/uG3yJ3pvZ7xPaKYwdcPBq5gyKyHjCvK7oj7YYo4rarZ0tc0+q9LzS9cMM1eMA34KZveJ9veI+4R3nW9XLA5ZVXgvp9Z7bybgcEt1q28FoKB1w991Y3'
        b'VTfXNPIGXL1uugb1uQZ18boKb7hG0qxi+j2m9oqn4rINeHi3S1ulbaFN8QPO7nvzmvI6cm44h3Tpb4bNvh42e8DDt13eKu/i9XvIG+NNZicvX/xjaboymqTGhzTybjj4'
        b'D3hJ6E3jjySA3ByUBA2IPQfFvh28fnEg+RX2i6XkV9AvDvrGku/nRKLdtQF+gY28PbZmqqkjq5oayBdxFhtTv/tp+/6jPU56N9/MpGVm928H1BTxSHf7Eu2W+LL9ewP4'
        b'bi3Wbp/7DuAv4kvw3LPatg4JosB56+m/yLbFzyPI8/GWFGPxTZaUhQ+NOS057bn7cmkTPwjMGUasBEtgdGcCE8FatVIlLy8rrZIqcHZcVXnhLykuL69AU/jUpV08orSL'
        b'9i1iSxtASovB8RML+7MNVLRRCUp96mIuxTG0h8h9WrzQJ8PcX17KIlxKbRkOP3UJlSMacsm+JWxJFeaA+ucWNvwJhV3GGU0zMoOUg6WqkjWm0HH81JVRkSFoN1yZ1iU3'
        b'vcOue4eZNf6TEPt/oz7UrsnRvgKM0uipq1I8uipR171ZP9sHYU+jMPz3uoetzvJnqc6y0dWJuO4dwVZH/tMayy8dGKyQoQV/6jKvIIP3LDAN3vAcqqvjApoviUiMjCop'
        b'pcfPPbag/4+t0A8OjtLs4olWrpNoHpGMOrV6BT0gr0DNKuujHiSH5hktFNmasmLcBol6bblkjrJqhbqsUieJw3UerUgG44bBzYMfXDVREakIlz5Z1RxreTZHylBjZzLs'
        b'Qq+FZsjddBje8WYw8Djaho5ovvl+H1dHdjH8+cMPiRmdNaFHf74qUhVRuI07b+Kq8/nOaiROVz6PXtnnfnScz6IJLp6b3Sf3Mx7fWLlvmyrlUVQPd6N9QiOMfAgh0VXU'
        b'kQAK2XXNo97jiHqwcJZJQTBTDqZkUiiKVcxj6BVy0htsU5od9dYMG9iDmHZYwLpUDNKXxwoAZykThmFv3WOt9xbEcE7OAbE3caWRQEElWT4jy4ol1sRNf1rTtF5R8ECA'
        b'9GZAdF9AdE/OpUVnF13j/Ur4lvC9yt6A6P6AnMaE3ekE8q1rWtfrEPCz7PpvA7qYN7I0FeYW/SXWz+jlsJ4djQS0PYWPPnGaZPCI+S/56D+oHcWg2epK1tinL63UrFBW'
        b'Guduvc5o26JnVVZqlWU6pdmZkwVVoxIiacRQY2lMfjqOg5PCP8pitTb/Jywwo9ePjD7V6Qt2Ai8GuM0QLM84u3wK0JOBAM+tQIbHmlU0aO8oywoxq5yw1mxO+l+e7jmc'
        b'wukTvyHbBzqbu+fuqOsUJZ0pUoHNivGSdse3MpUfrVLmB99RbPx647iKK+M7Xs1wuvG/ay6nBXKLY8CyUJviwQQph44otAXVBRONPn8G1ekfavSws/D+eFLSfS7zzNRK'
        b'R9g4WrNkxj1hI5aZT5lOXZln6iEKz6rdTWw66taIXS41ZPj0ivwHPcd3VPZ7yhoTBl09WqKbqzoid62/5RPcK53V7zO71202VV0+cfA33xTADpy6x4yex+wG+IAMoseX'
        b'rto0nMjOgJV4OLn9okM4nhGB240szFPPk1sJhCQnkZG5/aZ3+HXvcLN5/WnHjgLLQmJ10JIDN0ZscBieGpaBh85EewH1oSbLGyY/6v/s9oYtUs6nacwYKwHDUqFcqynW'
        b'lCkrcW00qscBlzL1auMcGKGIGMPe+ngjs4q15NKGMm2LwhkpJFnqlXqN1tiOKhwqrJSo1AWaSt2Yhm0ik3AJdOUrTIheg4GKslRXThNgk2a7okit1T3e7K0vZEsUPzMZ'
        b'QyDNSj1JD+PPYAJ3JFpTqXBeyZVKAoCeLNpGb4MSZuhjcXg5j5uagbYbz7nMmAq3yucmKVLSyX6KurAsZEibm8TNksLuZMnSAq12vWapJZhZbL8CGtBlPQG1sKcYIwZz'
        b'W/DDp7GMRHuw6EF7mJVSO3RBuCCWT89Pk6Iua3SenFhpw5Aj3gA8AGtRq34GvqdG5+FxnZ1+fhLxOJonKUMG2XwsaXeietidkyQj2WxPTkPbGCxTD0vXwJcC0NEcDkB7'
        b'4CWbOdJMPTFJwEvLYswLVTGc3pwF8vkWYM4LgjX+8DDqrNC89bsBRkcMGns/9Gv7IIaI475DzYEY3YhX7g1HA9LtJ9z9To5/N+OobH7aJyc6K11Fovig3pyO1tKFORFx'
        b'nxe84ZRxeTBtf9q8GReSJoZPegC+1Sm//M2dd8Spyq1fyP53VuQe/mDsa4oiwat2MrcuQZnVud8tnNrad0twf1Hs1LQ3mt3f+9OGeyHukxeDsgDJMVWj1JLFOO2SCDy9'
        b'kMMB4uFOYqqzLuOgNnQZnaEnqCXC7fBN6xBywACR6ibJ7wvP8/zt0BnUhI7eJ3suJzvDTmqLdZMYTyhwcKbGwBXodX0qa7gvR9uoQdLGgeusQhepM3Q52gAN1unOJlux'
        b'2byyG26gzmN2mD0ICDMhsIXwGAZhu4vpvBTBwK2hsA6eemRbJW8pfNGLNae2odpccxtmYRVsXO9HfalXr0RtZibMYLQXtnmLfmpP24ZHZqqHUoOcJjViLhhxi85U+40z'
        b'Vb4N8YJ+jkC4ml01t3xCekPn9/ss6HVbMGyea4wne+CyewIuyc7Kbng+R+ev+GuFfdLkfp+UXreUAZELTsHTt31K65SbnmF9nmE9vBueE2i8jH6fzF63zBGJSbv8b3gq'
        b'6O0Z16L6hudCo22P/OyxNHelZWfEYRn++GmRetKOmBdvjZoXR7RFHWO2QyfThmG8iEet17N6j7wkGA+OWkf8IqsaLw9L5qeeGjuJCnkcmFTICGqCeCjLn6Tt/kJblZQW'
        b'Vf/0FrXDI4s6dUxJHz8v/tHF1DEKLeUO8VZo1UVDAp2muEytGrLEc5Req8XaYiHPrKg2pvpU4689lqbFfzq1C4d9SxiDLT06jGOwK7KhEz0PT/TDS/zr+JYjpnEc5ptN'
        b'6bz1fONE/wh1xJJ/6xMnevZMeha30znTXIF+/MI/aQJ2xjQ9O7yp+fFruLTB2KfoI7ixCU1JjA0KSbyyjOjpSuO9gmV47h9z0ifuBXgezs6cPDE8gjoWkEV/FbGyYBX+'
        b'sdkP91OMZFapsliyukRtdFvAFSZ1fhjDVKnHZV9WXjlGNlo1rkiZLkYS96hClG+szk+ghuHdrsOowSpDHw/I2eYcuMMcN8jnIgOdqmTJWOvZmI+pWUYgwEQ6Yb28GZ1P'
        b'RedTQCA6bIf22aBdeqJXh2fyUxXykBQ8BZkngBOG56PZtJNS5gUbDxjFahQ64m2DuvDEUcduzS6mpyyCQ4X5KcsnJQI90Tbgi/k+o/WySthIVDN5Snq2uVpWn22J3hTD'
        b's/pp5MkNaAe8gOpJJDzrJNGFxWSCN0IJAjFf7k6SpaQpkuUhAoDqpTYrcen1RA6jtufn8WHnCDxEqkT0wmA8z2GlSyaVp/BBNTpmCRvgDnhEymVPs92FDs6lWXMBbzox'
        b'ZjTAE6vj2aPku9FJtDWUPH92HU4inTiKt3LWlqnYE/534XqEpqQbWzKhhgGiIC5upF22msKZ4/g6YhT/48o/t30QhdFN1KPIZlbHMhfZceez9cVnHcNbLZWRGN4sD/Lc'
        b'3g5f/gtn/oeWCz7c9JnVxI5lRVu+LNVFXzgZ/L/nKrV67ZmiTUO/YcTKv322qfvzO5uO52864fD5Zx/cebfyh2WCFruOZUePvitbeisk/NbHW+/4bM2Y2GH7z8vfrtYe'
        b'7vkNxkVffLb9/zZ0X/P5+C2bl+UgbL3ch/cPDHwIYImBh+MxLklToy4GcAqYiEL4BkU8VujSCgJ44FG4ZzToQWfghRp2ifsq2vm8ETphTfdyqBE6wdYZFPhMRRfhydTk'
        b'9BfQzhAMUzlACOs5cCOqC7rvR1p7K9oHO4lGDfejy49gH7Qb7qYmJliHEVajaVMyY7kQtheIKCpSYcB7NXQqfBXVZdL9Y4JSzjh0MYGiKlgXU0m3mGXSo2/TZWHeuLfC'
        b'uGgP6oDHWeC3OTLCuEhLk3ddShdp4Sb4htTmFy2skjlg9KqqNYEARgFTLTLHBUYiRUdDgEVHBbbEDDZ51+RbHuN7g+b0e8ztFc8lp1bE7ortSDiW1pl2M2DS9YBJ9HZq'
        b'v0darzjNbNX1ltmqK36qdSo1BlwXyeiN2f0eSb3iJLLeWtRReEMUMugd0jWx3zuycRZLK7khChvw9m9f3Lq4bUnjrAGRO+tD25Z2XRRMk5jR7xHXK44ja5xekgGfgJs+'
        b'ij4fRb9P+IBfyD0LntTpG8DzE9H1TSvg5rW3pqmmd4SxwZ6FVv9Dvv6XfP0f+Dlrmg+XskeuahpB2H2CC8Zq7GMm+PVPDL9SbRkmlKxshj4r/DogUIDT1lN+HvwqYjGN'
        b'0FSmp8Y174204vuRmRXPO3SeHZ6Yzc32Uh5xLe7mZOD8ZkldtC+QZzeQr42A3fChKi/My6OrwFpyXgFdeh7iFmgKH7v+PGRhWs8iZlRqBhqyHWFtoRDYDDzfp0+ZKuv4'
        b'39mq6fjI4DNjhq2AujSzjelOGKCZeDJsAfd4HFuHr4XAzrk1qpPfWdgd0K3r9Y3q9Yi+EvU+d9DDu5t7Nv4+l7Gbcjtq0kDM9O+40baB3wDyxcfEuzwculfKALHXoEPQ'
        b'gHjqfT5HPM2QcE8ARJ6DDuMHxDGYIoo1xGOKMU4ciRPP0EiuvoMOIQPiBExyncUYZhtjhY2M5SYZdIgaECdikttsxpCESS4+gw4RA+J4THJJZAyzHqY1i6SVhNP6Vii0'
        b'DfxaTKvWwWsJvWE7/luOpW0occAOuktC98TAO3DQIbw3Mp5Nyhsnlc62hqjTHz/wd46zrcT4AA7dk5mqNZtUK5mh9TKS5hJSNiaxCfh36rqjzwp7x095K+eGbcp3HB/b'
        b'gPsAf5HkUpm75PredFOpJ5FST6mbzfqEE1cZl0T4pi4tA+0oiSQKNAOsqokfUbts1CsDAB1wxC3caaRbuIqTy1Nxc/kakCtQ8XIt8L9Qxc+1VAlyrVQWxKF6AejhE1dj'
        b'o9s4Q12OHU4Kh52bwzBgtzY4FHFVlmZuxsTp2tbo4m0z7GZsR6m2mGpnRrWnVHtMdTCjktzs1I7GTYMW1B/Y3uBYJFQ5PnTGHs7PicQeLq3DSadhF26iSJDnHYv4KtEY'
        b'T4pw3uItD6/F5GU3RRyV8xZhrjOuF0NdxF1UrltArqvKDX+7EefvXHdjPA9810PliSmeKi/87UVcunO9DQL8pA++52MAOOSLQ74qCb4jodd++NpPNQ5fjzOm448p/qoA'
        b'TAkwUgIxJdAYHo/D443hIBwOMoaDcTiYpijFISkNheBQCA2F4lCowRKHZDgkMwhxSI5DclU43Y5J9o8qtljmKqp4WC2KGBLEraDe38dHYHIiQdkbrAM4+1YtrG6Qt4UU'
        b'a5VEz2CVhMKqYe/iR3x4R7qTa3ECK9SVmkIJ2aKhZNdSClldBxOI+oLTZE2dpVWS8jJWIRlLYZByhgR5q5SlevWQZZ6pFEPcxHlZGQ9iSyorK2LCwlavXq1QFxYo1Hpt'
        b'eYUS/4TpKpWVujByXbQGK2kPQ3KVUlNapVizopScABifNmeImzRv1hA3OSFriJsyZ9EQNzVrwRB33uyFs7o5Q3w2Y6Ep3xFm7GFn2gCGmLHxXMfR2Yw937GrWzXD70dT'
        b'McsnYQnsUMNZxh0d28SqOrtKvomm4tRwqrGuZP7GtTp+DWO6XseouDXMKqANqGFUPBWf5scsswCjPirucCkERMqYrqqxIKnmk8ONSGplOG2VBRsma9kPc6oBecM6Py6/'
        b'NRj1MZUfxxzeQ1wlxDO+5ad5Y+nlj7riG3nxoSf+ow88TtulvcXq2ko2DUp5ggWc7dYY6uyenSmPjoyYZM7qKqyiJxcR1Veiq1AXaoo0apVsTAVZU0nUaYyxTE73NGeT'
        b'aYUdVlhj12oK9I9RsWPI7Zh8lbpIiYHEMKvnY51dU1hCUtew7YQHjDEfPAhG1+0LwlEPnDVldPH/YW2CAnVBQ4xiiAn/gojgL/6NPw+4ivDwDKnFkMOj2ZIFa2VpRYly'
        b'yGo+qUmiVluuHeLrKko1lVoO7sUhvr4CD2UtlyFHxLF4luyi1JKdjI/iEsIGEjPzIHW4s2f7edjf7g8ElOwGrHulGE/5A77+N32j+3yjG5MIul/TPK0j7roosGvhTfm0'
        b'Pvm0G/LnKBqPvbymbxjVu3m2JLZZNfIHRC4tgU2xA2L3luyOuG5uV+KZ1O7Uy9x+WezlrD7ZjP7guL6AuD7vmX3imU2Jt3G0eU0ZjYmDPoEd6rYyDN2tB/ykx3w6ffr9'
        b'Ihp5e+x+6XZM2maPw7imljBB3G9H+HAt3rfYbPnNnLEpe1VVqCX5mG0KMfYsVSSwv/n5Cu2RX1Libobt2acs8fcjSrx0H7tz9IEndTYce2CNKBrHVLSMJxTtSbJyGW/0'
        b'PethDycuZc0hoVKXRzfoDAnVayrKy9Rlj92Y+mgF/0GY04OtoKp9Weuymz4RfT4R/T5RN31i+/CfN7tT9UEhdQnUryhQa0n3GPtFUlGqLCTuRMpKSalaqauUREoVknk6'
        b'NRUPBXpNaaVcU4b7UYtzVWFdDo9upWqZHkckEUamMrLphqchelyccPjlfmD45X5WxgMZmBHrqf8Bp6RP/zqWOJ9XQVQcVpSr1xSWKMuK1RItJRUoyXJxOet7hGMpJRXa'
        b'8lUa4ldUUEWIoxIjnkkVaowc4nFnaXETzFSWLadLoLrKcqyAUcFb9lRC1ihgTUXKo0XKJ72gp0KVFeFE1g8vfeJeILuhxvD/IC8qVVeWlD9EMTKJToNnK2My5DHiTGa+'
        b'p+pxdTQmFENedRqTbwRYYziSPNH6WlBeTl6hJikyN/PqaVeoHumGMaef1WotFi6rMDpSFhCvuMcYfH/Cx8sug928s5sLm0PlSckyYkJLXUCsoWhHEg5mzgtOkSXLBWCF'
        b'k9BNiN5E+4E+FNC9CS+iS7Ae9aALc4NT5Ipq+ApZkA3NgBfQwSw5OsoB0bP5xfB8EjVXwlfh0TB0HL2pU6SnoD2rBU7AHu7lKl5Q0AIEo90+5gbS4Ax5SGrKUnkWSZqk'
        b'm8rH2ogQXkW70UU2wQ061KAjh6Afj2G3V8CdDOoJRq/pqU3tKrwC38iGDWj3PNSA9swj9tFMJlaAXqmBO2bRV3mi15Tosi4WnsJF4gMubGHgBngS7dCTpcppxegVXRIx'
        b'n1ZNRg2p8DQPOOICw5PwHHyNfeHXFrQVndcFp8BNjsTix1/HoFOcZTmab3+fwdFZ4KFWcTVn3ZwPU3gRDl99rIpsbl0nsYbjrNa/6Ops/6+NxYOpM754/cqdbt09l5YT'
        b'3zv+o/nozXQHp0l7A5bMW7Lkx09eiG8RzVzp9ded87b0dBxVbdlYuSg95MuQgXt/v6MJPbBNeWbXiU35U7775tqMwsR+lSDyr+9+VzWrcub0iO2vyC5sP73Euj9gQczU'
        b'iAtWqbk/7qxVRs1Y31/1/v2GP7+2nvlj5PVXdx3JFD0Hv/mxfFzxi5+n35rl+8Lmf2rv7PB8teuzyLq3fv93we30K33Ld5ROvJS14ouvd1spq3uvhRy9HFJVu2N+b/of'
        b'uu/vFH18J/bmkXErPs98tVVVgP5i8deKL9Xnrsbv1XxU57j/W9HATd+YK9OFlyZIHdljRdotslB9MGrCbIXqLQBPzsBT6LgLu8F+i9V4eBbtCpWTd3+FJaEGLrCZxRXw'
        b'BHRZWDAP7oL1cKNFGL7PAF4YA8/DfZHskvGOYPRmKDrhmpKehm/5MXA/fAUeohbZLPiya2py+mrUEJJuAQQ8jnAJvEgXk9fa5aeiTpwlOWofP+bKwIPhq6ixN7tqEjEp'
        b'o6Nw+1gm5Rgl65P4Mmbn7aEKaUiw8RW69ugcF12AR6rQZuPLH+EltMkudTF6zWQShu2WU2j2FZ5xoenWxgd5GQzsQZtgLU14qncJMfUmA3eZAtaFkVGJH5ZIeOgiOo1e'
        b'o+5baBc6PiUVHYOXHo5U2BDGDtUQ9Bofp3ZGSK3LqDUQxzssS2VfKkDGFwOsVcRtYCvspMX0h0fghtRMOboaxADOKiYObTK+zA1uR5uSUoePuCmEW8gpN+gVdIG2VPlK'
        b'm1TxmvTU1HQFqpOlwoZMWtYQuIMPz8DLaBetq24p3InqJ6CXM+ApmQDwEhj4etZiqcN/3JxGvkyCb6Q925mVrHkjJ5NqLyNqGPMuNXEnsduH7uY4AEfXvdZN1r1eE244'
        b'TBxw8d5b3lTeUXispLOk3yXspkt0n0t0v8vERu6Ag8temyabXu/InvgbDpMHXdxb/JtLMN3VY++apjUd1v2uMuMWpPG9Qc/1e8zoFc8Y8Aq46SXv85J3qXomda+4nNvv'
        b'lXTTK73PK73fK7PRcsA/6NiUzimHpjZybzhIBtw8b7qF9LmFYNjs7tMoGPDwarQY8JK0p7Wmdbn81iu8MQFD8Y7UPt9wjMQ9x3VEd1l0Tuv3jMB0V6+9VU1VHW79riFd'
        b'quuukQN+gS0C4l6X2BLclGk622byJ2LZXVvgHXHXDoi9O7g3JZF9ksjrosgBaWRj/A3xeLKzaNagJKBj3rHcztxDz/9WEtmYNODq27H6uqtiwMuvI7glEyfdKrhrAfyi'
        b'7gqBm0+j+Z4ha20J+DkWdPacm0f3A8XiTnpyX/7bZEEnR4KttWcYR3LmzbMc/68lL8bE6JOoSyOcZYcXRKl3HH/4LaR8evQvGD78l5gUBP8xh9kSjOZ+Oxaai2fhiHGT'
        b'PKt8EHCK0QFBGMOY3gjqCMLTGdXe0eDBuNL8CCp8BAOOjflGQ5Gc0fhSSTDMCMhlQkDlBJqRZfYqAh5Hl0xZWMK6uq1QryjXVlGvgCK9lkVROvp6+p+GY49aFUZqP2Zb'
        b'OyqV2mKswptiPnFdvWx4YZ1lSNO6ugn2ErCq1pnb6H6Gnx7rgpxkQw837bVT2aS6RhsPgLVjz3q9LVnv5SqsYYmJFhfBGswtHZO/0nzrOk5IvfqznvfX2eIZxWDLAQza'
        b'QV7n2o6a9eS1ywvRQbgt9REQOC+JXcGnK8oYEOUQt7kFxN85bK7RBQ8dyyVeeHgKqPZxiFltpendl8PV/Qmn2OY+Td80jbz39MX9r2isnZ0lG7+/Avw9S2Uvb/DZcISb'
        b'clEYkfMFLFr1tl918q2uuHuJM5PPJXzwjz+cL3yz2b6j0ebl/r9/l9pxLUe7d85U8OsI+cb7A594Xks4+ulnW917F3xdpChs+QhlJP7+c+uI5vDsiNT9hpDnj9/5Mu1L'
        b'n6gp1sVzynULTv3qs50nX0h5e9xXxUvg9U88/9pe4nyCe8Tnx+MbLfpP/OPBbIu/ZwXdiHuzLyjq1ob2P2/68tYq/wcfeIovptxbkLjG6UV9/ccrLt969Yt/tRfe+lop'
        b'8AqPzFm7Rqqs/Adn+Vcx0/bJpHZ0wyx8Ax22x/PkKbMXW8jha2gzXch1t0aHU4ebELWiwzxgP59bil7hsn7Z9XCTjG152ILB8xgT+1o8+RKZaYMOsM4WcLs9OSCbHI/t'
        b'jPawr1LdvgDVpeKJGZ0NHGtuzoAH7xOeWmq3mqwnow3LjPDEupBWYqLbuNDM9MXwium8U2t4joNO5ITSnAMK6Cu0DWFy2BpBjtBm4Jvr0D56rwCdLmRREzwXYIQ28KyO'
        b'wgV42hJDEYxtJqG25FHgBr7qcZ8s3SnQFTuii4wPJy7pmSMADgedg9uYvDAhPAwvC9mz9C7iNmuRWYVSp0Q+ECzj+KAj6E3qcLgSXUbHBAusRzssYrhPO8RqYUmoLB0R'
        b'pAdPpmC1YTsGcrCZqw3Pklo+G/ywBGbn0xm3kRi1w2o74+xkvKbYIsSILVSOwCugfXrr9H7PUHJ2vmdLZfu61nXXRbIBT9/G1AE3r5tuoX1uoXi6d/HZW9pU2lzWyB10'
        b'9Rq+0VV4pqS75MSy626TB7x821NbU9vSu+Kue8l7/C8Fnw2+nHVOTuBBcmtyW2pXwM2QqX34z2vq5cLrXnEDYrebYkWfWHFDHI4TbLdqpdY4V7KrpSPxukhq3LbSldjn'
        b'GkGdERf2Ls67ubikD/9JS/p9NL1uGjLjJ3YFnJF3y/sCJvd5TW5MJNXQXycvgvLt0Pe5ykyPFvZJC/t9VL1uKvah4M7MPq8oHN/Nu92u1a6j8lh1Z3XPtH63uEb+oKt3'
        b'i7pjYb+rotdBYX4QOWu+pJbLpzg4lD2EfMTJoRkEMTzSJ8EcI0Ygzv/pjgzjde8ZnRy1vwePO/tsN3i8naxmzN1+q4DWTcU8XFHAsQSjYw2vBgiIKVDFebb4lsVSbsYD'
        b'TqDmAS9QEVkk5dE2HbLJKyvPM9qwdENcZYGO2uNG296GHPKGXdvYRZ9qV5OV+JEbKaR1YwAxyN02clfCzYAJffhPNAHz+WH/DtWxZZ3LDoX1eUb0iiNue/odju/inbHq'
        b'tjqU2ecZ1Stm916OWNIZfuOBkCzpcPYCdhmljmtatdSuqmEe0+RjUMkij3bu2N2h9cIp8UfTx07p4TJPmbRyeFFHxdRw2hgVZ+xn2uiS0GPu8PZbPFxKwrGEo2Otw3Ta'
        b'pfyMapdhnLdCo8PdUFhCEVI1N0YSVG0RRA1yQUNMkJTP9rhIs6KiVFOoqcxjB4NOU15GB8mQZU5VBbuawPIAu2FtiE/h5JCQXS/EN0c6XUuG960N2eVVaNUYaanz6CPV'
        b'ziYGGUGeS9iD1B0LROLWo+6YfwPLP6yurG9a3yU+493tfd11IuaTm55R1z2jBgKkx9I703sCLsnPyvsDZrQm/s+40KGwSZfFb3pf9X6P/xu7D+3uchn5QnK2pf8i5i5g'
        b'vBcxt738iHDEwsbVq9Fm9BLBsH0sDX/twTBeRUywzJO72NihY7AM6dD9fGrT5mVUC9l6BwdV84JkuBc4QVIt2ekg5bDSbHgLouThyRa4hbT0aFPTygtLeJ5jNG5/vxEM'
        b'hkX2RF+KORtz6oVrvF/ZItte14xeh4zRlRveyUYGIanaswijIo5RYJC3GzywIMJCEqhjyz9aKljkkUMHccHthgtOr/M4w0Z58gqYhGMpnSk9vEu2Z217/af3uU7vdZjO'
        b'lnvMzYizgFGEMqOKB2oYFWMa8+uYsetQwyznGN2zORlDTGw3R0tOMWDZ2tgJixhTJxirIsjLKyWHi9gO14RcFuAo3/izFRmehBN7ovrdJuHJkz3aowNPmNJeB+l/t0Ye'
        b'RjGOe4UTO01b+FN1UY+sC74sGrsu0f1ukx/WZR572PsT6kLOcTJKYCzF6jjDEjj6MXw2pqRbHgywoqJ1Zx7Dh/ipMajkqezHTa4Me5eukrEMy3vYPo9sanwotXBbqVeO'
        b'aCtySTLXEQVppJTy9mvPbc3tmnBmavfUPu+JX2NhM5MZ8As85t3p3RN4SXFW0ec3A4sj53jm9k816PDKGikUYQ62AjamfQUsAnpCF5eN7GJyWcExuh3iLvb07ZjQOq3X'
        b'NbjXIfi/y5oJZoNt+k9yZvHIUUYuSRStmjF6Dv7Xyvn8Q8HGmf7TQ6h4ZPuSy9WkoJrhgo4pdYlmQ6aUn55QHp6WYPsT0wNZQxoxPbCEtRzjWyAIl7p6jjpRduyWLDMW'
        b'8Je0JdlHQg1d3BoyJ46xxmtKg3qUEs4I7eY+FMMUjIwYn7bMyPFpqj2eYpQq1Ygphl6vJ9Ismq37GKKZVXDw6CPGU1a9yDm2pHNJv2tUr0PU6NYZ7j6imz++bcy6jj2n'
        b'Rlv9JC4iMztberOZnRI2k+JTr1BA95o11XQk9v+U6P2P9JzVM/RcMe05ubbqGXpLpy8YCQjI9VYycNaOOcKHWz7Y2PLWP932VMSv+6mWZ0ti1vKUQN6rTd9Ai1ve/f9j'
        b'7jsAorrS/e+dRh1E6X1owlAGEFBBUel9QMBeAJkBRxFwilgTNRpBLCgWEAtYsWPv7ZzdTTabzQ5iFiTJRt/bl93NlkeMJlnflv85595pMBjF3fd/ljv3nnvuud899fvO'
        b'9/u+z6uZj115tWm6XcK19uGvqHu8jW1W8BCo9ZkLh1zMMH7rDcYLRkb02Umr1ZmIW5dj5x9ymdG44ZtrCbM8OWqPJZpKk/Yg19twJeDIuSbr2+ceYq2j+H9p7CB2ctOP'
        b'tSBDu1ELkoRduDO9++rlwohLMW0u37caPDavbGSbN2hkZrmMYIbW6zeoTXGxWqmRyxTLUMWM0leMPm0vnldyqYGMi6eoxzOiyzOik9+p6vacgAQjD59D8S3xHfwuj3Ct'
        b'Y/gTTxFeOzqcujwljamPPXzbAhlZrNtjnNZx3P9+RXNeWdGcN1x9XnIi3rimbRHHXFldrWSq2kFf1YbEQ3gQvbKu1d2eEw117dTlIdE6SnR1HYjy/J+oa8Er61rwxutF'
        b'4JtWtQVxKG86S+HrE3igbzU70PUS/FeGOuGjOuHp6yT4depErd9kMv9tq2nD171+3rmkfxI3GTxSa+b259i8JA/31XnKOboJQ4A6HqoatBYTVmq3KT8lMNR4H792YXWl'
        b'HBsELylVVMnkxhs3LOpTX//WxcVMuagJRuqbQJd0HndzbFszZDdf3u05pTH1c9STA06EtId0yLs9sL/N3waFd8jOLzq56Hpgd9AUHEQqtTnusadfWyyzg9ztOR5fxaFM'
        b'S04uQUMFSU6ek/op2mnSK4JLJFE/xl/bDNGZByyxr96UIeFmKkz6JLm+jidYd7Y20NqoPrSyZWXz4o6Y8wknE7pd4rT2cW9F/Fn+jxJf8TrE11SrTIgn17fwgGo1K7/o'
        b'B1SBEYlqfY4hiKL1d39sYiBgz0LT/voK8ksXmJJPru/inuipr/v9ZUx/a63uUJ9fc3JNt0uC1j7hXyWakVrW/AiZiiq1CZnk+gGHtfgiZLo3x+DZv+ldrf3o/z3arMhC'
        b'Vcq4yzVaunDKT0zERk/shLRldvcQGwX6ftFGscYUaALF+2tKG0PvkHEMe9Z4IpZxZTyG6V1pRPiaIbZPze62c+oF+mma+zqTJJki+dI/4POXfgSuq6iqENVU1zKA36hI'
        b'xlxAU1NTjZ3wv+RESvroKDSVuut6ZZ/lUk1plVqxUs70T8b1VJ8FKqlCoVb1ceXLawYsZQb3U8yEaqh+QoFJ9bMpH+Dqz2eqv9fBvXnqzgkELp/Z7Z6ldcx67Iz9DZd1'
        b'pLcv6fKO6XaObeSyHDkr4yZ3enW7Th6KMz9JOGsnTH7EAItK5UuWNFVltRqHWnHF32xnCqBB1+Xl8jK1YhkTsxfxQZWlKnUxg9fo4xVrlJXKAlwHM/DBYJupH9Z9lnqN'
        b'kg0BSDAwWgLeIaoGZRE+kAVsHj6U4AP2KKpciA+L8YG4hMRO75R4v1m5DB+wqK18Bx/W48MGfMAihBJ7LVFuwYdGfMD2k8pmfNiHDwcInfjQjg9H8OEMrp9/d2zOQQaf'
        b'rE4S4/1XshZfH2Oxp5pmDD4FPKF9vzXlFlmX+cQnQGvr2evlUyft9fJFBw+fupxeh6l1Kb0eqejML0hr6/MfQseW1Hb/9gqth+SGwyNhwnccB+EYbMQ4qR+ffRNCOXk9'
        b'tg9mLCidUum6VNZkM7TXMQqbbEYTi02cMrGfQzvn08/5XNcCbMdpTdm59Apdv+cECr2fUeiAi3XDB5d+Hrr8BrWknUsfoqDskdAPm1BG4Jv+bA502T8F5XD+hsMTxpDA'
        b'Ov347IWtldDruTMtzKOfCWjh5GcCjjDkmSVHGPrCkicMfWZLC8WGtOeWtDD4uYArjHlmTaNL3ZnkBaqqGJw59IVAIBz/wt5wsBBOej6KFsY/F7CHSfgQhA/i7wV8YUw/'
        b'hQ4GY06wYyGoV8EtcCtjy2npOseSowE7a82HhcS76Lv5psacxDkat45XjkNBWrIRebgbKBnvDH9ARB4BSrUwSrUwitNjSLU0itNjSLUyitNjSLU2itNjSLUxitNjSLU1'
        b'itNjSBUaxekxpNqRVGeU6mKUysTgcUWpbkap9iTVHaV6GKUycXY8UaqXUSoTZ8cbpfoYpTqQVBFK9TVKZWLm+KFUf6NUJ5IagFIDjVKdSepolBpklOpCUoNRqtgo1ZWk'
        b'hqDUUKNUN5IahlLDjVLdSaoEpUYYpXqQ1EiUGmWU6klSx6DUaKNUL5Iag1JjjVIZ89SxxDx1HDZPlY1HR19ZHDZNXRFvtVA8oW8EdohTZPDd97STHoAE1DmuM8rEBgsa'
        b'kA2bPhA7jLLSKrwOLpCzdnxqBcHh6awlSHwZnYUfNphgAG9yU2geCwg0NZDAG5tGjgZL8Kpbyvj0kVWXafA2lr5kk9KqlboCFWpGy8w8qsPXJSfmFqWwJZQMYX5ocpFZ'
        b'zlp7lIoWEJ04Ko6BRRo7QgxjXqn7VtYMVq2U4woxKa9URaxuMXHEBmMZKqm0slKkwYJV5QrMZ5h4WDR52ITfwwwMxn5/OwVxfrt5mJ1SWmCWCk9F9ZYaeii2Sq1nnMyD'
        b'E/RMFldGreYW62VVcsUzueKbXAlMrixMrixNrqxMrnTm7ZQx3BWl25jksjW5Eppc2emvuOhqhMk9e5OrkSZXo0yuHEyuHE2unEyunE2uXEyuXE2u3Eyu3E2uPEyuPE2u'
        b'vEyuvE2ufPRXiJUtFumvaHTla5LTT3e1mrMonRr0R1fXKdQ8ObvXwFvDX81blDk4r4yv6xcqgQzlIXobXpXfELkFutzKkTIsh2YNztNKr+a10ge4a3jqXD2d3NX6fReV'
        b'nTpPX54FeqOJbbR6qvEzq/m6+Gk0taWCh3uS1WruIn2dGv7U6yOmqThZGBjDJey+pVR5DJX9MpaZ2gZNhK+e6oiGNa2PLu7jFBe/DBz49MJSbHRmsFsjhrpicZ9tAeLb'
        b'FEtYy1sBA/plQh9yixWyPn6xRq5WYs/6jE+PvhFM1Gq9TzLlYVzDJ/EBR7BWVuMD8fT+S4rgaExc8iExk0F3oxJrNEokx8vRKwgzbkEQV+rSPkHxElUFefVi7A2OXyxn'
        b'fohvOKHusWISb9aiuGwhRiaTEKClao0KSQRKOYYClVbiUBZV5dWIYlKhinJFGfERgIQAZhnQ3y5dojZ8UJ9jcWV1WWmlqVtbHPN1IcZTqxB9ZBpGxZBfJhZsn2fxgCpH'
        b'8jOaYtm8fHS+RNVnjYhUqlXY8wERZ/osULvgNumzS9S1DNMSFiq5Gt8QWzM2B3jw9wkW1yISVEY+hM3IbwzLjic0ZsY2sOoksK7LADJ1AXa/xILcQVqvflW3JbbUaiWT'
        b'unwmEZOP+d3uxVrH4s9dvDC2qa2s2yWkkYeRnrxdlvqILSQoS29QKI7YEqCP6iIyieqiC9xyxMokvIvu18efxBwW+RnHI2YTvf2IyTSbaPoTKMbP++mysj847MsuO10e'
        b'HWEBwfjXV38dFol/xSxtT7z9yWsCAplcutz+4hMT2ycen7QjuzGlORDvg09umdwR/cgjotfHr62oZWULr9fN65BPi0+H46dukt6Q8PNhp8Ju8LQ+Cc28z4lBiyNxjRmm'
        b'DS/SzpjTFT6n23uu1nXu544ezSltAR38Tx0l/SOogDHf2FOufm0BJ8LawzoFj1zGae3HaV3GGeIwD9sTJRKmAT20vbXrwL6hs0sexTXx1WyIwTCxiFhjVC02OCkMY7w1'
        b'q6tZH5DY5lWGeB1F+QrEwRhxFm9hO052PNupYXyJE5cyDq0y2jRODbZzWFKtNnipJIET3yaqSsdwiHTFRBqcapqGpxlMIw7r+BYknh0OiR5m6tE4RM0AGtmAjMPuuK+M'
        b'TjMkkd6YSIMTL7GZ6DT/QjpJZd4aDp2+pnR+lihiAnyqNAtYVznEOQcmjrWQYqOHvPIjiDjFFESwzFj6qUGPYcmFhCcwE49EIio0pJUr5PiFrCiBSkcZDPZTelZCJQph'
        b'KzUkDJ0q1ORXF2cmhKB2Q5g4LSHD90yr/Hg4NRuMa/YTfc3GDHYtP8SYSkyakRiBDqnDHFmsPw44nNk21JToiSbuf7HzdvkCU0fAA4lPLkhNiUhJTSp6i2kBUf2T4RAv'
        b'4Rr76Ji7by7zEQWkMxoxpKyRn863yADrM4kohbimZ2ztKmtLV6hYJ7eiKnlFKd7Qfat2+elwPm2M6TAN0Q1Tnbmd0dexTKoouHD6jNlv1wo/Gw6psabTcxBZpqurF2Ph'
        b'nnECjGT+mppq7HsLyRAaxm3wW9H5wXDoHI/p/Eanw3s5okjv02j49LB4nA+HQ88ETI83bbJiLEHTXmmF3Gi81SxcocKWn6L8xEwpmiYrh0kpC5j8+XAonWSmhQ0UVlZX'
        b'mBIoCs4uSE17K8/gyo+GQ2eiKZ2MPW2VLFxdHY5+DGyjKDj17QhEFfmL4RCYYkqgl1nP26Lg3OFTx3LeHw+HunRTztsQl86XMUxGImYVdtnDzjeMv/X8aQX5b9fUvxwO'
        b'rVmmg3kUWbeIeM66KnqrUaIdDkm5po0bMnAVwjsA2OALnwcn5eVlZ0rTi1JnDnfhZGuvazik5mNSn+hr778Hkmq6iSERpaEpPF2OiK8iAphKv0lsLjg8WohmZKYV4RDv'
        b'YaL06clhovyCzNxEaV5RYpgIf3B26ixxGLG2SsMdfiFb5lClpeTlopmFKS4tMTczZxZzXjgtyfiyqCBRWpiYXJSZR/KiN5CN61qFCpvJ11SW4ggzjG/5txlZD4dT39NN'
        b'R5bkoRdjrPnSz2hdZzaKmGFVSqarUhUq4206xyfDIXaW6dAaO7BzMJtfElGiwWVbpjQtDzVzijQdL/a4b7/V8v6r4ZA9F5PtpyfbpYgwq8z2HOpTMtyZq4c5LbBz/q+H'
        b'Q1fxgGWejVpAPCAyVMkN6hbjLYu3afju4VC6wHRW8GJqULcqYRcZIqxQMsOE6LEuq2k90N4Mfaoj5nEsy2mMqBgCHDiEtd1yWmU71DPELxxnNW0e94JSzdiG6jbUV1PF'
        b'xjmtB+dUephPN//NxfxX318kHJyGctoNTtUpA+hXzlEvJxQwjjaw4k0v6TDSmkEFaF6ak4gtlQ9w+/8P/swB4arJPjt2C678OzqIuUYxrckuMK4/vTmDTYVcrdvGX+kx'
        b'sMMZ3ZSjx1R4e/qHtRS2/Fqzcw3e7RzfMv6hR0KH43m3k26dKdcyLmRogxMeemTdd/zA7YFbY8rjgNCOlM6Aa+IL4utF9+bemNsdkKWPIImKiIq95nXBq5l3SNgifOQq'
        b'6XV03Zu7I7fHMbrLMbozpScmrSsm7ZFj+oCAkyZ9Gv8hfRp3ob3UChJvTVrEWJcNHloYaDN4aOkMjqrxAkBiLWGrlVeg2QqooYe30t48Mlen1zJG2lYMRL2JOcpelNLH'
        b'w5oCMxaplqwOodjcRzB3lLitWDtIB5cehwDsvADbG4d1eYR1E4j25y4ezUlNyxtHvGLvOOtVn+j8JsF+VxCfjYwqS/d9fNKtzJvcVsqr0PeZ0UqQG7X480RDfF6Px5gu'
        b'jzFaxzG9Lq7k26Rif3MoMaL4ILiuPrsByisyVMjIMgyqv1HseOoTmuquBKzqyoLltpWpOJOAVVvxGa0VjyiteFhnRSIv9NmaKKwErL6KR3RPdgM0UzbGiikBq9GyNCi0'
        b'GGWSnanCSunBYfu6UoTP/DkErz4kmss0vJjyKh4kA7EZXVgbhB3EEiSXldD+e2eJ0PMbGU15jyYO8Que8zneRXSd1OBvfyL2pD/p1T75jfKwDuknY4f0iYxLfpLUz+E5'
        b'RTznC1wiUZod4zi/1zELe83PoetyUTY2CZPgVcQkYTf94n4O7RT3nM91jq9L+8ZS94Ip+AVJBp//iIoETMVkQgV5sNcxEPv3DyLu/VmQGabLKZEBmQ1+jE0Zi1PGG6dE'
        b'45RYkuIZQAIMYI/7nnF1OYaXBeOXhZCXsU9hGh2TmCAEpIL7OVynqfRzPt+7ANexLeXh/9geTZnjUUaP+LpsQ2E5uDApE5mABcOFYzBcBAHDmfkYtgExod6xddLnTPQC'
        b'Wuj5TMAVir615grdGDwZ1tyHrImyWSassRVnwS2h0hwJdpEDt3OpkIX+dnzQCTePHhR3Fv/5FsfoxfhaA7BsAzWby6HkGFSmnwZn80kK1yhFQFJ4RikWMj561rKOU07L'
        b'BBssZ1vJLNC1NfY8X86RWaIUG3LPCp3ZYpjZbOEKG7Qu2PY5DOjUOQqVaSQxjm76m8RMf7QJo8FBV/rJEgN2i/UTXgVmSfTz+gpWEOGRnZw+q2KZhoWbWmHTj9JKhXpF'
        b'n99A/TCmptgYYqTSGSWGcAjuVFeIpa4MnXmiyMi9taeZUvW+rtfi2dOHmT1ZFaivmChE2Z/RwYYAtcPXzfztFYytWfr0IWAxc4stDodPACudjOcMk4RNmITatyKBFULj'
        b'hktC3dAk6FkQCSHhdS0YdDIHR+mDF4R485ThxWLI/kOYi81cvXUpZiJSGBuZbpdIrX3kvwr9zwpHhMYh8P9kRRvEsbKUEjZhKyYUo6V0Rgo9HpIuD0m3S4TWPuJ12Mjy'
        b'H2Ujh6gohpVsxE3oxdE1obGzH721zD8o8/ZuKmOMHG1AF5l3GmG+4Umch2D0hHlhzYzARZ4YQey5zAhexKWQjdqAfjPC7qEnbAc/sWjE4DSDlSzNzJFc6ctw412LJdjz'
        b'+AKDg/mgAXUcZJpdVi1nPGczroFI/BCds0fCGSFRaSbNTqCEOVNOwGcT8YHYReBehti4mhp5lUznE8jG6BVM1iFN+7ilMtkgVpV0BHSjCfdBHL+J9EHfttCOdx+5TP7c'
        b'3V8bUNjtXqR1LOp18O5x8O9y8G9Tn1jRvuKhQ2Svx+gej9Auj1DG5uehx8ReD3x3TTs6jyGGFEXd7tO0jtN67R177P277P177EO67EM6JnxqP+4VQxCjAw1DcMBwM3HG'
        b'MWiw+eHB5mbuIwkXvx9/ppAyDLWmFVp70WBS9A5GMXzJdOpKobbTZZwKqowzz5VxAGXWkMZMX97B2eLOQ8+tMbK/LuPQJKVWZ5jVx1VplihH45Y0ckXRR6tNLLL56mp1'
        b'aaX5DyW3DuEPDaKYyc/9Qkq3R9yFlI6lzYmHMloyDklbpZ0pXR5x3S7xWvv4vz70iCOr82YviaVUbDdQCjEYlpCuaeiVeoad4d8zOGwDKHM5RJ4fwLrj9tUz7mNxQ5nj'
        b'cdZgyjEiEjHvzwQ8oRjxj46eXZ7R3Q4xdSmPXXy6RBO6XSbWZRidPuPRwihsVhCJLRk8XwgshOOx5YHvt+hyAsMQ4nk9RghumeEI4SVrUAfrwyQ0lQLPWuSMAadNGEMd'
        b'WvXb/8CbUe7GjCH6yyF/ufv5s7k4qoxMILOQWcqsZNYyG5mtTIjO7GQjZPaykfvtZvPqOHV8xPiNQuweHzGB/DpLHNCpblSdW7kFDs1EWEgLEoxJx0JakhSnDZTM+YyL'
        b'iQWCBYv+dzGxQLBg0f8uJhYIFiz638XEAsGCRf+7mFggWLDofxcTCwQLFv1vSB3B0F/OlQUgyu1JHokCDVu5vW4H4Si9jZ5tj/KNYoM5jUTfT5NQTqPIGQ7k5GDFhNDi'
        b'Ehe+An0UXGGdHaode1I/DnWOdU51znUuda7lTrLgDVbYImEG1WmB/jufEevj9UTid6Ha5MpCjUJxOenzWp4JM85LgkEZ8jmvCCFBoGxxx9Th3Pvo/D46T8zv46Qn9XEy'
        b'U/s4qYXot6iPk5zRx01Kl/ZxU7Kz+7jpSfl93MxCdJZRgA7JGWl9XGkeOsvPQVkK8tChMBXfmJ2txK7q0ROZ+WK7Pk5Seh8nJVtZgOd3TiYqO6Ogj5OT2ceR5vVx8nP6'
        b'OAXotzBVOZ1kSJ6NMkxDxGQOMmwlcHbGPQYTWHgvRXwiU0jG4BGPyFwTj8g8KxN/x8YhhWnqHe47PNYj8oBUY4/I0kEiFJk39X5zeVLi3dY1EazFI08N6/MkcGsujjSb'
        b'oQ9cOxKeIXFdJZnEKWhOWGbu1Aw0ILOwH1VwkkdNgutHgMvl8D3FSrfTPBUOLys4pWj9aMyB8evbm042te9qr7u1YQdtXeA6I/lx7pbAnMiusOkCW+3PeYVuH99vsaMa'
        b'fS19jj4Uc59jfrjMHe6zASfDMjThIaA1mXgoHQlvcsFZyTjig33xEnAKNuTBzYgCmrIErbGggbMcnGE9yrpUWIAGsB1uzw4H2+2VYLsFZePMgZvgpVwkBpnbtsD1MQDL'
        b'6mjcx3RAVjy0VDgiIonx6UU5ujSHdTmMJgtxXrd7vtYx3xjEqnNSwyyKFga0rRJHCjLnqJMYSLKRMH+MmIt4KsaOfXAI8lIvmvZ50/CXuwWB1DGbSG6ZMZtmp+skON7i'
        b'bgtdCOxNvE38TYJNFqjPWqM+y0MTAL/OAk0KzDQgIFHs7MvtSD9Gk2K9jb4fW5F+bGnUj62MeqzlO1ZsPx6Qqu/H5QP7sT5gjL4f+0g149H5XLgfdGTjgIMRYHcxEy85'
        b'PFyCwyOT2MK4U03LrwUbMkAHl4LbamxgI7wEN5OH5QnezKOk96ORED7dBxxnvTlnwa1oNdqePSMY1s+wREOFR4Eb4LyNcPES4k+6Rimgpvh6Ix6gJKxNNZLS4GYOmIQG'
        b'E+xUCfX+pBfBKyR7pZUl9aGDH27rylkzAigS8gMehE1wg0lUZHgabjd1L21BzSq0WGGZQ2Iao9JPwYvZmbnZYXCrmKZspPHgEAcer4THNSJ0P3h8dGgGcUPdFB0JLtVE'
        b'gg0l2ZQfuMIFd+EdsFYTgTKBMxMkoVLsUXhr7jQjD9bBknB4d34wrIsIwUGgq8WW8FIt3EAChYDb47OyUTZEbWZOhIASuHDsQDM8QXo68aUNDkwsCq0MwzUeju6Dm5yx'
        b'78JNJEzIJHB1QSi64QPuoNawoCyXcqxtwCbNWPxFG8BVVSFDgRfYi4lgKZgaDLeHwfr8YD2pFhTYD5qsZ6xJ12BLF3t4GBwoRAQEg81FVDDcWcmEjD4O14HTHrBRtQxe'
        b'5FE0aKHg9tI0zRRM6aSVsCEVbIZbwyRwG47zUoMyFQWjem0IC8udlgG35em8fOu6Bk3Bo1xbxJa0gnsaEvbiMDyOmmHjsmwmgxhuzkGf7JDOhQfegWeY4NONizFLw1JO'
        b'UTY4UkUDB+xZpCbBY+BtsLWiEId1gQ3gZBHz1bCxmHw4eT9F5dlb1IDNKeRbveF1B9iEbURWUv7v5sLL4wkpSbXgGLgVi7r0hdpl8DKor4UX1QJK6MEBLXBtLKlhNTgo'
        b'UqHk6bAO7AM3wqYHZ4Wj3oNmc+ZFhvpFHwGa4HVrCq5boMETDVhfFR6K6wbVVUME3F4YHBweglpHSioKXoBHMqcxfRSsBSetKLAH3NH44s+7AY442cCr8LIKXlsKttYq'
        b'52baLoVX0VwdzQUbcigSYKYK3IbNhYGwAfX+3HAJqnE+NQrs5oJz4HwoGTbOlTyqJhvNi1NKKk8FO1IaLJcrwA1L1VIkTsHt1BrwPmrN+lpF7ZVLtAqrw383qXJ3UUI1'
        b'iLS/4sCJ8pGC2rVXOwpviTRf/+Yf9s6np2195Ct6NL30D8v+NM3iJxFP8r5LupD5daP1iMyDa2r/+4sDquK/tc7kff1kiqJix9/39Tjv8tzTdgt+H8RP7/vJzAmH73j+'
        b'WX7sdu/fnCfOGpsQGP1945FFf7H2+xM9cvbTfe1fCSJ/6rf/cUJI/7qfp61LOlgwU/Ddun0F8X/928jm4F9WWa44siPd6tRXcbNDfDPDvnIOBPMOdMaPu9b8+89/cDvu'
        b'P/LGw3uHo3752w/WVnzboJjPm+oU+9PbF+/vXac48vW17x5sP9kR9NcIxaOcC7H3v8x/sO4/uz+L/8Opj6bbnT4fdth7+rEls2VVhf3VzrnzLCZcPXILZH3WsWb/5t/0'
        b'na5q2PanlkkXzvpV//6q+pHvzQtXArqolpdxX3cf+P3f/8y7PtXl859OmdV28PIan8/P3LH8fq6D5W83/vzYTf+IX146XLV+3ItPf7M4VVaTM5KfHiB4ej698M/rtmfU'
        b'Ovd/ItW4fH8h3u3Rp3s2xrUd+wv9D37T/i2f/Krge4uK/eOEsaf8HiasHXO4/dcTU2IeVkj8zrpX5EQdmv7DzrbQjQcdYqZb/m4Gf9GzB1s2XKrIyPt48+fvKo5WbV7p'
        b'/6sr8WuC/vQHiz97bLFs44n9SUAY0Ao3gh0x4IKOTTDiEeC5CMIk5DlXokEMtkVIwzOwt/bzYDs4zoHHSrxJEZWgHl7QeUEHl8F54/DlJ32Ir3ThnHdBQ62dsDbHWgmv'
        b'qOBVtVBAOS7lFsL1YDsJ5IJ4jnvgFmgE57LzwplIMWD/O8QLe6gGXIQNOUiU4WaCVooL79KI7P1zCYvikT8aEYc4LDGsI9SdC5Rz4BHsy50Jzr5uLDwOGkYsg1drUubA'
        b'Kxr0YhsXzsJUcJaJ8LMXtISHrgFrjTzqj4EthOq5aMbbiJi1sBCxZMZkMmkiDk/Emw82wXaG6lPwni2aaS9lS3IFFGcFPRGsh+uIm3t4tRCHndqMJqItXHDak+LF0eAC'
        b'2M8jYXHgWnADXl1ml42mOPTgfDoCHPIjLuqXrxihWma7VAOvjQCbwZYRlkJr2DliGRrq8KpYWLsU0Z/LE4Ab2fGE/tVwD7gW6gAaw+HWnCiaEsyi4ZnRVsy3XRWBugKA'
        b'ppgMcBaxC2voNLADbCH+8iPBtTUAcX4NaNECuzJyUSNul2Tlcil3cIVXawV3kAA/CaPhGZxrG1qwURMg9m8KOAy3ceAeuAvuZXpQmwTcxI73mbkGNtaS6cY5hycEzehl'
        b'uAUt0+FB0BAE70XgXsanBCUcPzSpXiQtlALeLwINEexkyads8rKTOXA3vAybmHgDLU6euHzUA/Mw55AbngyuIH4Z1ZsPPMaDlxYqCLMLr4HL9mzGiEi4i/RWO8SepASu'
        b'JNUxhSdF3GzLtAhcVaimMjku6MPuPMcqFHhnDJppG3Dp4Co4LZHm5IGtcDvK5g7385bC/ZOYd2wpg4dQheAlzAPuYVYxu0Jubj48RT6mNn41uo3W+/q8bC7qjZvBBYj4'
        b'iBMZ8DKhwSsnHd3PAnUuYZmIj6Esx3MWgBMLnweieyNRPR7Bd/EtUJfHLIKZ4RxwFK6jQoL5cN3S5UyVNIL1aC5vyJOGgfoIvHQgFgQvH3xUJdf4/JHgyHMR6fxgN6iX'
        b'g3ZCE8v88NBScI4LG2hw/Dl2Se+cDerwADEWWtDw2RMK6sH2CNMdhFC0kG31twaHUE+++zwKk9KO+tf7ps+DOngRUU6eBydhXY5YQOVQFgAVCtc+J5zSJbhXSVa/7UgO'
        b'Ql+akYs+eVtENvqULfMxA4H1V+ngggWSPrb6kI62QIarHvcTgJ94JxY/I6Cc0YRwD9xc8G/3raEz0xvoW4NoeJwGyBWMaodIOZc5TBjTSi9sLxbUMe6RSzSRc9g4pU9c'
        b'vLFDyEcuwWQrMa3bPV3rmP7UxYfEPI3o8ono8Ynu8onuTL+WcyHn/qj7vtqYlPvybp+c14+F+tTFq9cnqCO2yyfyobe0U3ZtyYUl9zO7xkofepdpC8oa07Gf4Xkt83q8'
        b'JF1eko7a86tPrr6edH2qNmLyfZdur8zGtCduXoe8Wrx63EK63EI6xna7jWkUPHbxIm+acn9sl86XTK9PIHZP1RHUOabbZ2yjLeuUuGl1I6/XwaV5WVtFy7tdDpIv3AMe'
        b'Fs54OKtYG1jS7V6qdSx94uDW4xDQ5RDQNu2RQyj62OyL2aT0rG73bK1j9hNPP+zDrm1Vt2d0o9VjB882lxOe7Z4dCzqWan2jrrt1+SahQvsCQzuKzs86OatzxaPwxH4u'
        b'PToZu2n3SMFu2p3QES07Pm1I1JR01l5bdXEVeUPK/WVdgbnd7lKto/Spg3fbhEdjc7r8c9hvm9AVKO12z9M65j1x8G2b2+UQhQoJDsOxJI6s7gka1xU0ricooSsooTto'
        b'cmPKp44BT4JCG1MeoV+fQGLe6Bfc4dHlF4vOR+hNJZk7OqNF1iST8fXcOpdk8Q86Ed8ef2JS+6Qe/3Fd/uO6/eNwZlGvKIhkZotgzSBHBzGGmQERTIlGAWtZDSIx28Rv'
        b't33sN7pN0xM0uSto8sOg0vvpH+Q8yOlJmdOVMkc7t6Q7pbTbb0Ejb/cII4F7JOuVSGdezMOKACV2KKSMxns1NmWlar2lsEBVtlC+RP66ITSMRhkeTiXsH/1Y+9FBdg1L'
        b'79jL2T/RKPt+MRLf8+jvKXz8hhzfQJZXYdb4qCCGumwzmTtsTedJGhs6k0oYStVo+iX6yLkm+NHhG2EdeoWS0/ybX5oiV4MxgFHvQIP5FBEbukEUrJSXysKrqypXiN86'
        b'sHCfTTFruFGskL0ZyX83RQaHP/RifOm+DDNnDqJQGb7H+APeopEJ4O/NaMabl0a2Sd5FxAgEm4DorcLeljZGU4tN7jXq6vLyN6OPyzPpBhHENkCjDkcFibD/AYPhCqaZ'
        b'WBT/SypT6fTGPVaASTWAg0MIOFhRzqKBl2AoOGpzeRX2niJ7eyoZi7Q+22Kjme7NCLbCBNvptM+MZQiGMFfgEHN6S7S3pZNAPXzfuGPaYuIMEPCgoWN1m5Jo/Ha9Dr2E'
        b'YmBFrIcqLtnIxEpOfUjCNTTZyKSMNjJpoy1L6h2a3cgckKrfyNzw4xvyAql5f5jzMXU0CY2NvSHpgmHrlQNvHQwb0fYUO0o0G1o5zTgksymGWCVSLazWVMqwrh3NtYpy'
        b'Bbb4rSjFyGOzZalZR0yi5Ep5KTbPEKUQNyO4Q7Exm4khF14mFWi8MkYHCvMxn1VyEsuxpKRIqZGj5VfBjPSQxdVV6mq0AJQtDhFVKhYoS1Hh2IBFFx3abGHYCEM9aG5D'
        b'j+mgmkx8RcYwZoWRvYnZ0hiTGT2BaaWVKkTh4MiGxPORcafQDxp9p+BKFX3tZXwVFtXmid5r/Wj8gfYm3wbagRddc5WiJnxDf8ilRQVimokpV78IthmJHFjgKAJ7dDLH'
        b'Ti80yOx1g4xFH/DKK+TqlQEmo0xVVllMqhCNN1wjqkkSnItIB/h5rAOpFFGeIuyrQutorOpgwWambBTRspToIONK7GL19d5oz2MVHX9dSz2fJ6LpUW+q6GgUiKg2m1Cu'
        b'eW/R5WTks2FK+USVQbMKOezPmfcvC1Fa8VoKOQwYFIN18PZASXM6rIP1OSFZYeBUEawDrUjUb4iYihPzcvAOPTgN6m3iJPCgovfzxxwSuG2ngz9Ww7U33ci43RSFeoyj'
        b'am8k7BVvOe3me2Z02uj3J34lbZO43msSH7Q6fmrnumgudWaa1dwD8WLuc4wLA7fm2w8h8G4D+31NBN59nmRPIh/eEeBg0YMCRbvBizx4PgLsJdnsS4BJJwV3wHEjyfg6'
        b'uPs6ujrUcVWv1XFVbMcNZjruN0oR5erVNq0nMOFhYMLn3iHa0Kxu72yta/bj0SEdsUcWN6bszjPR3ZEOLXyVcMDq7gzOTZXg9bo4os1d18VxpL2lqIu7vUmQPby5IuYQ'
        b'bcc80AQ2ZWfngYtZ4TTFG0GDE2AXOE02yj2D4J3sUGkGqMO3omlwyXq64tZXL2misf1j66jWjyamnTmwrqn9PfHWqI0XNh5x/vDrkr+UZJZJSznPXBe7LnItbP5dJD+6'
        b'5jiX6vG16t7zF6Z2fgQQbuzuVf/9K53N1wtpJW+mlXp5ls9niyxHhn7nyB05pt+S8g3skHUZXLjq3j5ki5i+XQlxewzx3hG6FkDv/W4OagGrN2kBjEk2v3CXUIy+n0RA'
        b'pso5/56l+8emFbSCLFnVwFfhkWcZW9L6UcyBI6nr6tub2smscKZ8g/aB7f4/UEvW8Ly+O4UWEqwQLV4ADgzcYmO2x4rA+iF22OBhcFPMMWoCDhmuRljLgbpsArIkre7C'
        b'js0pvpSrhxmcpa65zawthuY2Up0P/TpfoxXlxbtvuKK8orH/7VzaIEgHNaipedIiRUzDab4Kb9g37gkm3MLOHdFeVPlk63aOq1+ADos6gAlgsKgDdysYECppHyumffrT'
        b'UPt4vuFq/4qyA4yX91TfN2yM25z/b40xaDkfHJcajbt3lX/lEMzIk8MbSFtgIEy828Vm18gpzqHHexe5Cj/1ICCYz4v5zlt9FR+gtZfo2LfAToxzCcsM51A8tAq3TqHB'
        b'lck5ZGyCA7C1Cg/OVHh38PgcanDeXkpUY/CqCO4mGIPLCnFuuICyhLc4YAe4t8ZMryBQ7kF7WATDTXqFiOkVz3Nwr9DhuHs8x3Z5ju32HG/k6P/1O8srXhlk3Fmyh9VZ'
        b'jMEunroWw54GdzuZBbtgrJsd8VysQ7sJ6hwIFk6Peatzq3Ovs6jzQJIjVedZ51XnXe6pB8II/2VAmEEdbjAQZqKUwWd0zgZXsw3gDNCeZwdPwc0MPgNLCWqv8TZKeAVe'
        b'GYH18fAiaAS71ALKHhzlwJuIuzyswVExnafCNgIWyIBbxHngjA4t4AlvmAcMwPeX24Ar4H2RWEAgMPAkpVYVwLNY10/BRtypL0UQgAjcyR8NL80CTRoBujhEgR3wfdDB'
        b'PHQFXnW28ciEV7FW/woF2uHaFeQhJbgEdqsCQRPG/MI6CrwPO+AVAomA61bZ2syX4q4Ez1OgmR/DlLV2JDiligvCEengTgpsRkNqEwETeKVaULaoDm8GlIT9MCGXYtAi'
        b'76NxBS/BaxbwAi7pCAX2wKP5TFEHw+xVrvCu4VsyYDPBVHgsB4dJNQ3AUsBOtRJeLsyAm/NCsU6VwVQ0gmarNbAlhWmpkyPU0bAxGtwDxyJ5FI1qAq4F51ZpIvFLds/y'
        b'MsUDsd63p+bPgLujswotwIZaahpsFsAroBHWa3BnWINesC6a0sBbFBVFRcGd8AipoCSwLR82cTn5FBVBRSDhobXyh3/+8589Tjzcj+xnZpfk+DvyKU0iyusDLmRl618G'
        b'6zLCkPARCc6jhKxpwbAeEVIYLIbbZ2Rk5mK9Vy7qHuBqAf48QZVwntNIAq8RgPOhGEJonAv3JDQt1YO1zhF5bDVlGEGccB86DW7ZwosjlJoFzDR4EOwVomd2CMHaSEs+'
        b'XDsNHhQgmVaYNsrdcmIBuAXuwIPwfGrFcqtyl6XW8Lag1hJstsqzBZ3wPXg0Et5ZJfaBdRMkcJ8A7E0Wg0tz4YVJMbDFFTTDW2CdZhqu6iawDR7lw3VwnZCKsuSCzmng'
        b'4my4WwDq4SawOwRsgHfgdrCtyEPxDuiAaz3AnUV+HuAa2AI2gqvlq+AGblRwRRIiZKsPvJDikAvbwQUlwXrhg8s4dzqGQ9lLfUrWRCvSKQ2WzsBdcAFehg254Ew+rMtE'
        b'NRAB69FZHtwvNsLWgLMZ0txcIuGdg9dsyuatJEWqZmVQjRQ13ruiZFFV3HRKgzUbq+F+2IG/osWKEtmik+nzF4Od4Awa0+10FFgPj02Ax0XRqFWaSsAVeAbumxYEj8xG'
        b'ZK91QlydHNRVwDZ43WIhuG2/AraO0IxDhU4Ae60JlXAjuGNKaWFGeBZ/lBPGgYKTYvQPjTB42gpeAwfti8S0BnPyUXDvVNwN0MIEt2WGodkiYQVqZhdLXiRcH0TeYOk3'
        b'Ljs8KxeNFCxqZnMyMWgtdDqBner7/raMsKwcSWZ4COoim8W2CoUVQSXBi1PAbQJLAm1oNjAHTTKFJaVAxOGS6WTlSnAEo7JoNEjeozhgG52cDW5qsHnHyFjU8zPQJ2/J'
        b'ZYZARFZmeAGDINTj43TQtAwkkdfg8Z9fEC6dP51DrSgasQJcLtYUoZIs0JJ8gMGGZU4lj4JNluRzsEyfkZNHvlUy1XIZvDo1IytXGhYuJXBFlNeASyNALrilYCQ4Ng00'
        b'kQ6wJpODWY6ZTzklYZ7v2iGWToNXdz+4H5zOhufAJp1C3xJ2ckDdEjsNBozBfcWBhXniXLA1LzMsc9oMMwhJCvX5Hb7wFFiL2nUn3DJXBE4jifxohi+4l+EbDc7zUKXD'
        b'daNAC5LaD5M2nquZiWbNSyOsLNHAhZfUSzU0ZQO2Oqq4eQXgOKnssLmBhWjSAqfhpiwumujOUPDMbAtNGLrlOgOeyRaHk/0NKSIqeIBNKNjpRs0TWYL1+XAdwdOp0Ddu'
        b'L4QtGrC1CG6dhoYGP4QG+8BeuIVM1X6wfarNMjsaHk1Db9qDphS4VkZmRzfQFAMb3Nfk0BQ9noLb1oBrZB6OLVqF0Z9rZTqUn81sDjyXnE6qFInQ55IImOcoWiC2cFk0'
        b'TwloJV+WSMN1BBKD5qomAouBHWAzs8qd855NAG0J8G4un+J50+Cw0I/BBF5OFuJuUYNaeGuoGJziUbb2XCe4D+wm9rHwRpIEdWsx2UcJywRbp0UycBU+NRqs5ZerFpOa'
        b'hxfg5qhssB2NbUNoBtjMAbvhPbiXfFtW+rTQ4HCwURDCoC1sK7gj4HVwjAFqXhoL72XjYQmOZCIKeTQ4tEDELIbrF6LppCFcSiAlgnkcrxQnuLeK1PACcBaN9AZJVkBB'
        b'LpfijaXBybTx5I4FvLIKDeal4Bq+gT74COwsZCrjSswcVFxWKqzHtybRqFs12xF2JB99RmcoO2ZR18SDlj8DbqB8QRPfSgGvE4RsXh5eDuvzpHALqI8wrhtSM++C06hy'
        b'pGCdBWwUSkjQCtgMD8PNoeA4T5IZJkazjlUcBxxLA3fI3VQ0+65H/fayqgwcg5csKA48S4fDFoEijvMxX+WABGnw/JON03PzPpti/8UVrw8yM+qsXCdM+aHmh5CNBVk2'
        b'Z09dTcqY9qs7yrnHvj7+0YNEx/YXx6491dqceukPtv+p94LXhFvtcZX7V1SXf7nlUM9fL73cO2Wvw1+hJu5nwd1pfT/EB2h/+/7Hbv+Q3RSNC6g5/4tZB9etmjnm+08C'
        b'ZCkf9NwLDt3ouGLaxj1xG53Bx2NvzLOKLYry+HTj6Of/cPN9oPrtL39xe+ozL9ckl5iC8Jjpf/nv0qMB6vLUGTDtXNNmbcOpB7+2/PjCIvc//Ofq9avThH9aIHh27cFX'
        b'uRv3bYBzNm/7qiAmZuY81w6NyPbu0ZJfF45evHzkvQ0TlqWIG/b9/Rfird+C5r9snqCUb7mpdNz9p4ZRxSuyVA+EuRqNImvxE2h35vsxv+KnTw168rv4+r8sCZ/x2Scv'
        b'nhSXzl/4m/9p/nRU+Wbbz+L+kVT6wcbMP7fx3ll48dd3JmtnhsZsPPl15IsRxa1bN47+Ie+/fvZyT9CED+59O0/ys+9Dv/yvgkRNxUMPVcBflFV+VWMSv7e62/q7Dz6a'
        b'+1XC1e5VotzVgR98z7G4/Ufp5i+0638x/UGrctbe6g9VVu/87Xez7hQcmvggfebTu54zLi3973Oea+Zm/4/nX363q/ZR7PGbj5/cGrPp7AnbrPtWIRfOe8385cQ/lx4V'
        b'fhLutWhXp/DRlRPaKy3P/vvAugOPej9ZNNP1MSdI1dgUuWfM+0K7yY1/LPdWCxoyP1kwdl3fi9Jf/3T6g6W3Op5lnDs+qeFB7spvZ9Wudl6/fVvsBwtnOsvPLAv73ReO'
        b'a67O6/9l/ccjvv56+UKhtGLxtrz/lEzevUM9ufcnjw/8fPxnmW7+/l9k/jnkqse9qWFpwLr3zNIZoP4zrsXvNJJLf52QOmJH9deRXx750uozh/+y+Oi79vo/Rr/4eGRc'
        b'/irnHb+f98P8ek+/Z4n1nr7PMutvUx49ZaW/eXi/LeWJoqe7f9sff197L33kKiu7c0HjW23kG2cA8MJx7tziButz1ffhi8qf3aOvbFN99926fxwvdbokcZq1+Z/R4KPf'
        b'nIyd6jF96c+EpU+jO+MeBi39x6wdszb+qf4nBxd/nbDRaeusP1f9I/VBRN4n1lP/nhXy5T/ovGN2V04XigMJqkyFuPojBGbn7moA2nHgnrHgMoMWvAsbszEuEhydwUAj'
        b'74C9BE9WgqaVq2TGRILHDQZIuBNcI/BFOdjhr8NlhsDNo2CzHpa5LY0RX0+D83GhYav12DtLcIWzDFyCuwiYDY3pm7PQXL5KYTKVw2uwlUAck0EDEoXQZD5qtmEqB7dh'
        b'53N2Oj2JJ7YwsA3NKrv06FEOPBYM6sh3ccHdhFBCIZ8SLOL4wXvec8cxr96F5vL20AJ4MEQihpvR0mY1C003iG++Rr7bWZkVKsGrXBiaTsE2Dnrr4fDqalKd4NJ8cCbb'
        b'gHcD12dSI6ZzK1GeW88DMI8E1zpgrB9mpPIMDLUA3qukfLJ58GAQvEc+EJxHEtjpUJYCATjDAduXRMOTy8m2Arw9HtwINeBGl4C74Wg1P/scT7DghlOyCmy1XCqEF1UY'
        b'QF4TbwLlZICc8IoA3A2wJM2VwM0PNdY0CahRmUWwjgva0mA7o486VgyuZ+t0B3kEOjoS8dQnwUUu4p6vxpByQOvkXIA4t80R4XhSz7aA74EmakQedyE4Ws1ANvchsXRH'
        b'aF4YbIKbkDTVgHNRNvAuB17LAVfIxyGa4cnsWSJTzscj+jne/xbCEzPQQlfG1S1zVbCeVP1UH3B1IJJ4JNjHBWcnCEiLj/ZZiGjTAzBn2riAhpkMJPAUOIj6YwOqn11g'
        b'2+CdGBMgIYcmqo8qcK+ABbEaIVjtQAcBsaJ+t4vAJWXwfMhgXKUHvIwajsAqx9qT5g4Ed0eixs5iFC58/kJqBFzLrZ6RyiCJt9FxiHeHW1AVoY9Hn25TxYGt4AQ8xnSH'
        b'6/AsFy/KU8A+3aKMGmcv+e4VsLmWcC8yJx3zEriGFOufAK5h5gWc0hgzL4hbvEyInwQOS02Yl8xAE+alEF4lnQMeRiLQHkRguA68CtrBGVTNzvB93qg4cOg5sQpp5I8y'
        b'2YmeAs7+2GYXJ4Y0OmhbDe5l52TSifAmxSmgQ9LANmaU7F0CD2XTsC0sGM0i2diO7DRnxQLYIg7+90Ey/3cPRNtlrGceHGhtACy0b8SA2ESMbwL9NtyAu2QD0I7PbAsX'
        b'+VKigEOrW1Yz8M9Oi+ujun0mYiyl995VO1f1uvi3re5yif7cO1grzvlQ/atVP1/VJZ7d7T1H6zrnSXCO1jGwNyD4RE57Tk9AbFdAbOeCzqXagLjG3N7AsBNz2+d2+nVG'
        b'aQNjG6W9LgEddg9dxuL04vbiR4Fjr0u0OfO64uf1Bo7plD0MjL/+jnbqtIeTp5FXZXw4qUs8q9t7ttZ19hMHt5b0trTWvIcOoSzadFlXYGq3e5rWMe2xl6jNGYMzu70k'
        b'PV6xXV6xnWXdXvGN1r0Ozs0hXQ4BvT5i9tO43T4xnQVdPuMbM7Cd+vimNW1LH7oEk/flawvndYnndXvP17rO73XxwijZjtE9IQld6J9Lwv3gDyQPJNqpRY+SGPqk2qkz'
        b'eqaWdKF/4pJu71Kta+lTB6/mig5+h6xt9SOHGPyGcU2rdW/o59BeqfS3XI5PGt1PcdzSMDo0YmyXY2ijtC39sUdsZ9Ujj1RS9Pxu72Kta/FTF9QYj1zG94ojm+16/QJa'
        b'LJ6IQ9GZb0SPb2yXb2y377ge34Qu34Ru38mNdr3uvofCW8JbIxotHrsHtlV0u0vQmYNzY23TxDb/hw6BpOJ0dYbS3+l2GN0xSlejBd3uhVrHwqcOLqwFf9uYne8QatK6'
        b'vdO1rtgHW8uqjpjrKY98Eh+6JJJb2d3eOVrXnFejWF32Tto5qa3iRHV79aPR43rZXuUTcOjdlnc7as+vOrnqPu8D4QNh87uPfKSf+4Vpw+do58t75iu60L9wRbffIq3n'
        b'oieu3ofsWuy0QXMeuc4lbo3a4zsWXuc+8p/42Ce0I+NU7nX6fsAHoQ9CUSE7Mh47+bRZdvg/cpI89gnrmImxwRk4tO/CDstHDlG9PkGH1rSsaX0XZXTzb8vokD1yY0DS'
        b'c7rd52od5z7VBTVtqz2xun11Z9HD2Kzr83o9fNvSWiZ3pHfO/5ZLu6bSjTz0dSjjxJaJXQ5BTMfsdk/QOiY8wY7JUKX7E8dk2JvDjpSnHt5MMN2T0R3qnoikroik7tBk'
        b'DJR27RHHd4njr4/vFqegkj3T6MYUDB123ZuwI6Et9aGDGAdVSen18m9b0DJnR9oTDz+M3ejxiOjyiGhMeeoa1OsY8Izr4DbqqYtHPx/9Yo9YAf0W6KzfkkIdw3OfZ78V'
        b'vrKm3ESHbPbZ9NvgK1vdPSG+skPPHMrbl9c/Al/ZU/4hPX7jHvqN6x+JSxxFefr1O+A7jpRX6EPPjE67+xbaiIyHntM/nPFh1g/9TjiXM+Xu1++Cc7lSHj6HIvZF9Lvh'
        b'dHfK3bvfA5954jMvfOaNz3zwmYjyC+/3xU/5UeLw87YnbXuCkx4GJ/X747sB+M2B6KyR3x+GnulxC+tyC+txi+xyi+x07HYbS7Dhj73QRefy+67dXlmNab32znutd1g3'
        b'x7YFP7IP7Q0b08hjfGW0pXTZi3vtHffa7rDVpeA4Ly6ejbZG6g4fRt2xDyPoiNuIIHwIJfBj+XI9KM/IbcObYI//RcsE5q4GIZjNGQ280Lv1GWpFCMH6GWxSTmDNU31p'
        b'upDAmk2PbwJuxo5iLgoSOdQDjk2ikCumiZ8L6WtAeeg67MRB8G+B8mC43GOOGbhcYrlarhSVlVZWkmB3GMLLBv9DNaXAVVRaaRIDjwlDIJMxcW1KRVXy2kGFMvDQ4JKS'
        b'/CXqzKpy1EoLKqvLFoslbLxCHQBPo5KXayoxCm5FtUZUW1pFwGcyxTKFbDBIzYQIRRXJWE78/rEub+Qqxg8OE2tHhJ28ixQy1WAI26CE+JpSZekSEXZXGC/KJEA41MtV'
        b'ChwTEL0Hg+JKRWUalbp6CVOs/tMyZSUlYuwLekjsIKofXX3gU0WVaNk4yRhUFUmoGmtxZaoXlqr11BrgiWZLZL+NBCokWGEGBIgKwGELTapI51GoQlmtqSGxSsyWiD5d'
        b'rSjTVJYqGZijqkZepvfCqBIFY79rYagK0GuJm90VNehSri6TiEkjDAFzxBWqluvahW13Ag+vQjRrUEWi8nGvW6FrfVk18WdUg0NcmivTpAEGt+mPKLatpQRS5Of8rl7L'
        b'aKlx4dhNBjcYHSMWdGaAjbkmVr+szS84n4DNfuHmpRocAg+JN4fhdVb1IrLkYgXPzaWRcJe7d4ZD4NI18HwB2AjOJoNdc5Iy1Ug8aQedlgnSMC+4H7bD/Sngls9KcMp+'
        b'EtgeCQ6D02RvfGtCBmcXR0Sjec26wWMqpRmNWf4L4KQl3rPMTYLnC4OxWR62NMd2/RaU3yIePA2vgKvk+S9r+FQoZY8tjXOyViVSij8U8biqA+hO4++/YCB1cQ20gyyq'
        b'bPOxyOORZ8vXdy52K2he7PqR6+a/rX05K/JT58xdnfDFBerTmpJTJxeUlcz8pWXpuKhlY5wXqy/KlpadmiNUOYxwrn32n9O/5MdcythSjz1ljCzPs1581Uar+TxwfU3P'
        b'Bd9b7esvNNfv8OW7hnyzP9LpwMdOW2b5NX8n+cXRzhnfjIkMiP6p6kFKiNv4OVThTu+8mg/FNmQTA9yJhjfJ1gw4AK6bbM6ApnefE3Vpm2osY7MaPRtvzVziEVwBvDg9'
        b'3Tzmx4yYtRJsJLCCteAckdC5qAJPqrC6KjyYyQa2qblImm7kgs7kSczmzdmly0INOzfwRA7evIG3wHGyQ+JbCi+E6oxCwbUcbBcKd/sRaVQKrsJGnVWoqmQNnQZ3hxKD'
        b'VjnY5Kjb0oDX4EVsDmudxeznrEXdZYPRhpIt3KvbUKJlxN5Q8A4NGhbDnQMlckYcP2lDzBwXgZYAE2kc3PZnDR0ZaRxsgld+FAlnELSssA8PMpwHINL06US4wvEFsHA1'
        b'P9C8cNXLGnchrrrHJeShS8hvvYP6KVo8he5NSsNs7DdcWizFxmQ+ediYzC2Pfurhg5hCVBpiIVtX62z1Yrt8Yrt9xjXzEOfektzGa83s4OyTIl60rbjbPVbrGNvrH3R4'
        b'YkcMY81FPIY9RDzP0i774F+zXh5NoJIhr+JlBkMl+dxB0Dx9RRwxBkcmB9K06xuDI+k+C7Q2FqPF0bwDPcI30HqvPIxPHq7eJw//X+aTpxzxDT/wzPANhfIqNgCXaRxg'
        b'jYrhI+RkJkfLTmpSZnKhUWzfoRZf+QJFmaq4rFKBSokniHqdd/ByHJmnbKGE5JCk4mMyyTZUyGCjUtlajCcmAWF6mwAckU8lJ2RWK2U4AS1rZpcdNgTykDRI0qbllJBg'
        b'EZqayupSme7rdRVitlAcu0of/AGviKzFj0qjUDOBiPVEmV8Mf5Sq5OSikrDhPjpt2I9m5g/30cSZs4f91pSU4T+aNNxHZ6aOGf6j0SWiIVjG13g4ZgirjMxywkGxDJxc'
        b'FiYKYbt/iIlph6ntCYF1m+e4hrIoSVOWkuCWhj78JsYjMzCPzswKy6IlkSajhRi9MCHOmOGEXrhMUTq8mkoqmmaGhHjGr7iKmWMYOpjhppD9CFs5GL7mJCXc13xfged/'
        b'cVyxN6WchUtzGY9C8PxquFFlAxrhOYzlaqNACx82MCCqe7ATtMBLkZGRfIqTCe4kUPAgOJHDAMOuZMwKlUoQpwP20GF0ttiCAAFA40J4OFSaxUHp6+k8wXjfUpIO79nA'
        b'U6HSTJy/js6aOVFWI+YxBKyz9SQgB3iRT3HdfVfQCWPhdqIpn+UB7qJbnWp4DS0KcLfSi/atBNuYAne4IQ54jJJD0dVUmhO4RinIM/BIfoYKXh2hRCTD44gFXk+HwN1z'
        b'CM3OvqADYq+fEVQyPBcB3lvCINDq01ahR0oADgVJEGi5sINF/uctBreNqIP3QDOd4Cpk6uciPFFuTJ9LDu0L984nN1fDJrjZQAjcBtfRIWDLUobIDrgDNuioR7zeDXAt'
        b'EdwQcxmAwIEkxF8ZXloKOuiEVD9SbOpYuNn4leC6kPYFhyyJ3BAFzsDLNsusVDyKayUqpyPE8P2VI8cuCLQRKkcgRjIsm0NP5rqTlziDy/AKVtLb2NEU1xbemklPzoS7'
        b'NdgLJWyNhgezMQdfSCxhMPgHsfRYrbAPkbpzNRIctsAN4DbYBfYXoYtd8DY8CnciyWEXuD2KTyGGuNN25uhwUr3gLj23ELGYdyC2dl1EZcL3wEEGRnB7lQI2FWE8UiFW'
        b'ANaDs+8ipvmAlWJn9Fe0CvsL3Ji6q/WjiUguiCVyQSmSC45GZkU9GqO+GNv5a3QuXxwZqb6guejktOyi7ELJ1F/tX/LJ/fxduwBnwxlxpfhPqpkXe6M+pefdXye+uW9k'
        b'Us+YX0dKS8Kysp9++B8/O7XXovDy+1Fbrc4dsup436fhr/k397j9fmViWHnkp5Hn338/KZL78b3UHAfXbx3XTpRGRnjf+qzwOhJFVBzeuq+sy1RRH8sfjF99EAjHehwt'
        b'3hX294klf69Y9/KnP3/4Kxv1He98KafQ7k8hCs7xi7Kf75RH+Hz+5TPZH3636Y8zArIn+32+G2Xj9pzfXPxuffzc7dR3jhNbo1Ltb4VPcWt3F8XtFZbPd/CviKcy1TMO'
        b'7pGJHRk2f+MSYbbBZdZKsJ4oYcGtPHK7El5DPYDxjoM1sEGwHSthz8Amchtshe1WocTKiDExgqdX2YZxLZJjiOwCDpVZ6/ztpMJ1iVMnEY3OZMSUXwtlfLXwwAbU2vtp'
        b'+B4fbCRlysA+1Cd0rm0oXhxojaLBBRWSXcgr28ARKRJMji8x0SpbgzZyW2gBj4VmwWawB27Nxjw/kiM5YB28nsIokxowrFRlA6/QFA0bKHANiakdYMtoIrgErMBeWmpi'
        b'sRe4TdTSsbBRBXcS7ZSzogDfEKAbdVRECtwBLmiIRFPuDM/iO7i4egrsXoj6bHsCo3oDnQU6hzHSimS9v5gg0EwehU0yG9UyNFZocBwDny7BVrjPlSj7CkBzqApsAXWY'
        b'Ejx9gHZ4Gay1I7SsyElFj/HRYycocAyegPuVSYyKcNsisA5NELaImwXnKLgZ7IAHxoFbjC+hXfAcPK9athS/r5lKxRCsyFxSINwtz0E30LvAHipxNhL3QT1R+oWDQ2Cn'
        b'kZwIjsDruJUZQREe4SMh4jW2LbEQgdcUgzGYCjHRK0eaGvigJCJJYWdgWJKqGq2XpCK7fCI7R3X6an1isCTl3ji51ye0Q93lE92Y/tTBvXk168Jk2UOfhN7AkM7U3gBx'
        b'ZyySqLziv4xPuOF/XXZPcUNxS9LPpZzc/8PFs9d/9Inx7eM7is7POTnneqA2bEq3f2KzZa+P/6FVLata1zTzUPmsAGd5PaDbZ7LWdXKvk29b0UMn8WNHV90pDlOzYscK'
        b'bUBMl0uM4RFet0+s1jUWBwJ3a3FrK3/oFjbkTflDt9DBN53c9s7aMUvrF9/lFK8LnTMw05Mhnmob/dApuNcjiHUqndLtEaV1jHr7m4EPnYIG3fwvZ5/e6HHXJlyacJ/3'
        b'gRW0ehw9uZ/P8U1EgiwOuNFPcUYm0UZCp4Bx9WFrLPQoBdzBhgYCSudfk5E7cRhnMz3mgU7k/J+11HfvIpFT/KYip87IBrMzyrPYtN1lgOfmPl5xXqa0z6Y4eVpBQao0'
        b'OTO1kIkmo/fo3GdTU6qoYp1yKA9gpYG1wfEEo1TAoF/izkS5Hx+I+xJo6vmZOILGW/dEyiafLHb/P6CdxvPqj+ijlXlY42Di7/cIdpwygwkf029HeXi3FXZyr0ffL+ty'
        b'yKrD6i4Xz7bYTv71aR8G9jp7DDr9xoLnYVeX/cKWKwz93nqSsIx+RuHjN1M4JBCK+Fsu7RFal/0UhzcR9zpOwjFQpjAxUNz9HtuH9zomoST3FLouyxBpJgYHghlL4sCw'
        b'sVNS8XPptHHYFxyJxSmJiZTCxlzBAVw84kjMFTbACg4E4zq5LuM7yxHCmG9ElJtvl2tEe9yRCeinLvMFjxZGYlfanvgQ329JJdLJ9PfcWlro9T1lOH5Djs+UXMrOqcX/'
        b'kdD7O46HEH0aZefTj8+exeMbRY+Efs85E4RJNL7j/w05ZfxxE8eWp3OzTLwCH4whi7l7Ok8BWxeYsPI6t/3fbsBOuB2x1ZXBDfdsLnbBzbjf3s9jHXAz59gNtxX6i8+x'
        b'O27sjJtJN5zby0bKRskcyLmjzEl/7ixzQeeu5NxN5i7zkHnut5nNk/PrBOW0zGuD3tAGu+1mHUzTMht0tMWuptH/Ubr/Z7xPWzB5rdBfWRCrOeLKfIzcT1twKDmfdb7t'
        b'p3ezbWkoG/3HpXPKOWy5DuyvPf5VGNJHsTTgXyv037qcJ/M/E2BCQzB2Ro6pqLOqE9aNqnMst5QFGlFjRRxyC4j33ZHlAuK027qOWk7PtiGeP8R9o/CwSSbBvYkX93K5'
        b'8uUYE4lscAYmFKhJppcSJN7FK1TV8Sq1jPyOiYwcMyYeS4nxy1WyeDxJSSIjo9B/JH9Gi7l9PGleQW4fLyMzPaOPN60gPf8k3cdJSUVHK/zK4jxpzqyTPCVmEvr4ZFem'
        b'z4qJ865Ap/zyytIK1Zu8Ngq/lqckEdnF+BDCxfNrprSQCbzxhmXFifkDylLGkAILU6YnvkxaqFbXxEdE1NbWSlSK5eFYXlZirzLhZaxHC0lZ9ZIImTxiAIUSJFVHjpGg'
        b'94k5hvJPcojncGUFcSbTZ5WTl5yYU4zE6JejMdHJSZmEQvSbX7oCT4AFWHWkUqNCJZEx6IgWGVzYSVo5jQl0gsOk99kWZkrTc1KLkxKLkjNes6goMZehS//JL8cNeDBZ'
        b'Wa1SJRH53rSMnOqKXFUFKSkKl8QxlIQInIjLGjGgPl66D/1RL53MVp7YxqQU3N2Uk82UHafEsaEHFhJHColWTsH3hn551MvQN/jSPguZvLxUU6km1U/a8v+KPSpFmXEv'
        b'QcQOvCFgQ2QEPpeYR6xZogj6OJ4xGr78Yn3rR+PPWhOzYSFl3cZxUSuGMBrusyxWVmvUqNMzQXRMZxOJ7qaJ/fBKMeXq9YYmoTj+8yvfkMA3MgytFQ/DMPSkBcNRtZph'
        b'qw7oeCsT61FrXf0yIcmGsB6lia0odpVOnKSXW+stQ23/lS7Sn663MKNWyGS86ChWyo2UC2WkChntNp7zX6FMKNTU1FQr8T5lDQmoTFhRVfzgjOGiAeNSFJySKn51Njyu'
        b'fzRHnCg4RKXAqvJl4yRjQ16jSGaqEAUnZ/x4ZnZKwJnDRD/2nqGnK1FwZtEbPRH1iided+bBRQwkeii9Dbv3zGzSMg6OZPIF6mqlPhbsUE/i5Zl5bGC3qVEqqpUK9Qom'
        b'wFJwCF70QxBBeNkPMb+VH4KZAZwHL80hWG8TgtfUELHEgOYYKxkjiYxns5gvxgD8iCRZ2VINyWNJMlP0UB/GuJpjP82MuzimfoJUxGPckNVDNJTxph6yyCAz79KN9XA1'
        b'JE0GP20MYcx4HehwDbs002N/zEB78B90T4P1hViVRlQYBHckL1XjDoU+asVAn3gY+TKEmy2sBkHl1JYqWZiSUSxhUjuiQrkcf6umUi4qVSM2boFGbZ6s5MSi1PS8glnF'
        b'+dMK8vMKU4tx8PZCQqUeIkRcfpnBGbGVxExCTP3kJ2ZKda4ede2mE+RZBY55RI1BqUMUhUwJBp1LyIA5JWRITBJpoRpmnKpIJQ54Ni6E+TpdFkWVeR9gjL86xAAzeiCM'
        b'QqoSpU4rGEI5VSUqrFWoV8qVlaTh1K8gnpkQhxhLaMBkqksrV5AHh57hQobus6yjPaZBDP73cM9nm0Tvi4/REw/xRWoGYmUUgc3kWRMvjkPOWqSkQYo7VD0sl6bSdd8B'
        b'5ZpvEyKTGI+UzKREqWiBvLK6qgKX9CMKLqtBDJi9lBiUToVbwSmA4UtN2XAbbORSHHiEDuaAs4ymaTs8JM2GDaBFoA+vscbFEFwD3p4JbuKwIvBkIhtZJANsI4aUKfDY'
        b'NCy0gy3wGvp7CdTzisF7lBBu4KDy7sLdxGh0Crp102BsVESBE+AuNQoe5oItK2OYSBwnwP6lhQNNnUHH4EAcZL/+mrUV6IT7xRxGUbXeE9y0WGXQ2tCTZ64id6qE8Bp4'
        b'D17SKXroyeCihDFMPi4Fx40isBio05so1wiFBTgAS3D4GHBEOi04GG6GWyLg5jAcM4MJ7hKO99L3OtAa0JpG6koAzoLLJPYHDdrZ8B8584maMafCIuUbmqgZbY+EShij'
        b'fL+FybDBYHidIcnKhfXoeyMKYF3OVGtJBrcA1GMPBvAGOLYikAL3eDawGe60VIC/7eSqPkZFrPpk7pLGXGsQab+xYlFfTL1Tyo7DFkv/nPk5z2Vpz56kY19c93hw7Hrw'
        b'wba9MceeW+x8HBD95SpYNumZDX9LKv3zcdci/FOjNjruEP3mm3V+jTG2+1dabQ3IWrjS+8bnlrXHuXe+Xv/0y7YXmdvf/+JX1OPUTbF7Gg9slvnt+LLr8FcBs/92wW7T'
        b'zx0y/9B7c5zNNdGLzriKXOFf07J3zpikeCnxnvCLawEff9I0deucMWf+9MXHvzlC35n03bW4f9pd/3h09tlQTeY55/qmuMV8p7rPfI4ciriy1VssJNv8oXAtuBMqyYC7'
        b'whnDsaOcSNcqgvqSg3tpTLwlHDAqzB1uwHgxC8qugBsFj4UQ/Ygn2J8SamyvZwW3cZa5w+3E9msMPIr6H+OwHxzMNkKrwa1JRJVgAU6VYI0PbIV3GFPCjlRiuqWGl2PZ'
        b'fgyugrPEUTyxmjsLm1gonBjss8kGB330CDAd/CsarmfCPMxGD+sUKmB9vF6jAk7DXQT8BY+iv+fZPOoY1qG/sTd/cGY0KQs2h4E9oRJ4C7aTAAxG4ReSI5kIC8eDwTpw'
        b'M9pI+0WD1ip4iLl7GaDhMbEEvQsP38vofi6dBtucmNAIZ8HucjRh5NCwEe6jOAvoKPgeuCK2fat9WLx3Zwz7NvJdbVbiMnYTz2G0Ks9lodRIZ61zcEdAl/346y73Az4U'
        b'aPOn9cal3C//cOFzLj1yJjZTcfc+5NHi0SjodfNpG6t1EzfysW7EjMmQg4vBZMHFr62yy2XMF97BveMn3hPeEj5Y1s+lQ/IIqC2fgNry6ScuHlpUhksEtpCh6BCCf/sG'
        b'ZUsn2TJItgz6qYeoNzi8mbdf2BsW1cx75Cp+6uDanNbjGd7lGd4hf+QZ8wSrYTz3zt0xt82vLUrrFNjheN7tpFuX05jr4+5NuDnB2Nt9P5eamE5rncYYCbNCI8D/KyXJ'
        b'ocFxOAKmCRz/NRskF4vAEykWez8jBLsRf/GmzsSJv8w2QSTVaTNheM7EFzI+svnFWCwYyqGvue/QufXdir5DiYGPjFtfyWvIHgOde+M9yMKMxII+XkpqUlEfL7kgNUVs'
        b'Yc4MQ/mdLmpmn0XZwlJlhVxlIuOP0H11HTrsthzSQxT2D2VRZ4dkfCztjyCeoOzrRpaP+Pf4gXraYU7aT5TJEAtqDFvXcTtmdnr1fPLgTYNyUTzm4uNL9O4RS8wgnsJY'
        b'rlPv9hfj5gebGaC3GxNUhrjaBUh6qNaoDbKEGle8mpW0XkuGZaUPpl+8hhhbusTwrDE5TLqoVCUqr6wuxTtJSA5RoJQqzZIFcvMsP35dlX7XBDOQOmhlIinNHEqKocJE'
        b'tjMmQyfZqeXLGcEF1wrj+ngJg/kfAsSP8ihkmOs2VIVSTqw4EGXMN4iCEaFK8mmEq/YrSJNIJH7iIeQBBjRGDFJKcW9SqZWaMrUGlW4oWSJK02Euje6bLU//DOmZmppK'
        b'ua4LsIBWJIDgj0Uy0hJUlWbLCC5ITUvFOtLUYum03KTUgjCRTnwsSp1ZJB6yvuXEAgVXtrxKFq6uDkc/RvUTXF3DWOS8ooTl5iRylCpXYkseY4n8lcXhP3qBHdfwq+Rp'
        b'vStqtlebLW1hdaUMzZpmRW8RqpXUAmlizmAx27zRymuK3jKNvBgbsDBVga5E+Ip0WLbf4HGhllegfoE6SEmJtLoKzxSvsOZZrja8HReGS0GSFragwROEvuuWK6uXoKqS'
        b'lQ5hdlOpYXY4KxTL5FW6no+GpgyDH4PLqv8fe+8BF9WVPvzfmaF3pfcBaUOvAoIiSK/SRRDpXVAGVETELogiFhBsgIiAoDQRsKHnJFGTqAyTZDCahGyySdY0lUSjm8T3'
        b'nHMHHIym/HY/+3v/73/d7DBz7r2nPqfe5/k++dxsVF04JlRx2SQU1fJrM0ZHI3ouxBEtJp3VgpSc9NQiejx49U40Msxlrq0dEW7UOKQ8OA+WQucOwvKSgxrcN9Gg+Mp4'
        b'MooLSV8jvZ1YEr1+O05PYvPYkcLtL5e9Jisb7aixYVIJSiUvD3W+5EJ6E0zf/OqxhcstSM0mjTC9GV9ZWIA6MlFJR1UrbGzUEWixf3VlvhjlrNmhaFuevHJlXnYqUcvG'
        b'5yKkP4kaWr267yyix4xk4aCIUsfzO9sMfXIs2XiWZ5uFRUdwcGPg2Z5t5uUT+pp+aC5iOTaXY/4n7NmmdVw9p4f6l5xj/57u/B+cCeiHEj3HXLSBOirCbIRVcgqrwHGy'
        b'rCTb1Y6VEpQc9ZRsV/dYFtE+RgOtwIVpB6PrMGlxC9zlWywEiJ4F+7hCXGEWOIFDdsILtGLnCKiVx44iCeUQVnpSoG4ubIsib/7BKVCt/NIpAjlCYJbCqkzH4lB8TwsY'
        b'MINVQo+VUqvRvh7WrIwSoruCrMxj/C0Do3/PfydmIXb7zAJVYrCZZNgYbe8u02cGBbCTPjYAw7CLYNSklcDgi+RKS1Hu/jixF36Lw82mYW4cCWqerQrscdKbOmw5C1vx'
        b'eYQPvEwfScjB6uISXMbj4WZBhHFpFRiGDyXoSMThPrhNxlgTdMi8OApYCDfBI3AfuIShLrPBNnAiCjSlhYNKrw3gENgMOtH/WtDf7blrQQ046ZWSCHZ6FWaHh+ckFhon'
        b'gIbcLCUKVs9HO2XYGkBnbJe5nSw8t1JO3ItJMeFFhg24COqKI9GlOFDLfG3GYKUmqFwI9qaAbThH07nZtgFtqI/DA/gn1oxNUoQ72BToCp+lAbZEEl3l9bBXA6vlggqi'
        b'mcuwsS0qTkbhxWXu0ycznBh/Gma5srg4CjW5vCLcFyWsb+GhDdagxQc3+LwGN4zQiS5NfrQJC0Eb4HYpov2rACvU4GmL2YQ6WQLawNFX4UangZr4oagZLQkHwA5w0ULe'
        b'D5WsjpD7YC+olAua9l6NKXqgazES0IKMlVEo4iAC4UOtvl+cGwh2zkbSvRPujwBVYCcDjqxCMV0Ae4iIl4G9oPo3Mfm/2P3HzIgObJMFB1SM4UlVVI5WNVUWBRpCZi0G'
        b'R0Ar3AGaCBIT1ujBjlegQpmwGR7AQF531Dib4Va4kwVP0VrKYF8KBXdEyEWAIdhG8hW7HlaIHJQFB3ACraxjYMVvqmsqZ/IvOgtsKsP9BVXc0eLZYO8ssJ/gL9cpIUkW'
        b'otXC/X8Tt07On4udjjoiUAVcDIedZIDaEAR3v3C9W14K94DaMKIWR84rQ0E/rJh2UgyaYIWtqJdi7VwOMzQq26R1iMl9H20iGzUmdke9Ewptlc4ezTx84h+Hx+pklCRr'
        b'Jt7drT9xXTLKX82/4+D8KM+lp2RcJYeGZ/u94fe56Z2hYv+ef143/vbWN990XTr8/QPJWW8cvvdlfmDN2gyriiGlbD//MqPc2k+935wTtDs8uPLdIKXP7xxyj92/o53n'
        b'J/3FxwoHNib+aKsv17b2MzBx+Yxbjv1nlZYr8xZb2LWFbO+YP+xttlqzufqn9MXqSlXJvn3PK6W/Y0ZzPrp40EXB7sOYELMlZ8Eo882yjJvrJm39Okfjlt1ct4O/v2x9'
        b'yoSj09vHHqyT2ZnoybP5fFu/emLVvLtHu8E/1latY78X9muHQOY+Q9508MqwxcSPl85oez3ZHLcqfDDu+uTxM4diC3nm0eE3HlWH/yy1NuxNj/z6Vj9vv5b1JjlX7nd2'
        b'1dv2f96+rPAEr/WD+NX/PJkYFmV1v/jXHyYk6havMDhp99klvZVeH42VKDjp/qSk/224q3lx692so4VrZNcsH0jsOJRhcdzByXdPekzeA3Zv29bHyqUbrFclfvptd+na'
        b'0gcDuQ/nFTyoudPR76u8Q/JdzcHCx58WS5Z8lFv/95VfqslP5N799KOvAtOvhxzImTD5JPaXrlGDdwf2h4y5mNkWOwxmgBN7yjRTb7FOuT9nJh+vv71DiaNGI6CawAF4'
        b'Fp/mgaNwz5TbR3yaVwaP08acR11g60zPnqjbn8AnhXrgwA/ErKM/PGRKNxzWmHqCXU40Xqs3B54T0UiX1Qb7iUb6ZXiGnLxJgV3r6DM5MABPT53LrQLdJG+58Azq4NgZ'
        b'7AxXsKV5rEitEqKWvV5KiA0TIsOk/Qk0DOwBjSQDKzjJQitUOCAnegwJTmrSKvPDHF+LULgT1M/kmg3Nok8Gd4Nz8DJRb4dNUUTDnQG3hINttI52fSbcjn10BIAuMUoi'
        b'j6kKtxiCzhSif55gDNqmXbbCPnDBxgyeoo8rd4IGUCc82Fw93+aF99FAeJEcfc5eAJtn+DFVBltmnHzCk2CA9jLanAYuTvnAJkAouAV0Y6LliAOdx/PwMjiE7rAEHTHZ'
        b'YpSYJQOchyflSfUt0YLnaae1C7JFT01BazApQw4c1rewnj58joM7bENNCWrKAFQUBAUHgMopE2V/5hQ3lLIFQxI26UokBXdMxCTC4w/3wnrLwDC0AFHwZs3PMacPVy/D'
        b'pnUWLxzShuTBrgBYQ2u5t6/E7kJtQqw4KP35zFzQyQ7V5aj/b6jN4rxOrSxfT+kwfMUB26voTVgbGDtdyLDCfj5N2k3eU7e7ozunybfduzukIwQDkHwnXn1IyzZqk2uW'
        b'E7DteGw7QmdiO9XIjxuYiTi4rFGYMDITGDnyjBwFRi48I5chXb6R36iSwbiy5kGPvR7tTqP2i0bNvXnK3hOGpnuDxlUNm9LGVM3bN1xRGbPxmTA02Rv0QIIysusJ5c3x'
        b'qgnCcCKbBhu+lsWYln+PxKBir+IVJ56tf43kA/aUi8zeNfe0jB5QDJO5+LxYdlj2IYth4k38afoQf5o+DBqK47rXtUliTNnkjrah8NTYkxwWe5HDYi/Gp9pzhP4sW9wb'
        b'pCZElNlfPBFDnoglT8QyJtT10HUhCGoKbSX6nLqe8Dkf8pwvec6XgUE8bofcaH4UXy98VCN86gg8etRy/qjRAp7yApRpDZ2DZXvLRtVte2Jp1tGYU8gE26pHZYztNGQk'
        b'mBc0Ni+ItziewI+i+YYxozox2JMpeqZdnKdu1WNxRUXgGcHzjBizjyCJCblYn6rrNZf2lF1XGHOOGRfJSzBfL2RUI2RcZw7m+fRIDsr1yQkL4EUKsIgUYBFjQofdGNwQ'
        b'LNCxHdOx7YkaTOhNEDj5jjn5vvLuBzK4+t32ugmUOTxlTrvxe8q24/ome/0n9A1q/D9X1RrVtmov4ql6X4m9njEas2x0eeq4z+LRiKWjCWmTLIZaBqOGiWpD36SGeUAW'
        b'V9R0VKPmbu8pu98xMEPSG9ARMKQ2ZulxR9+wyZFuRb6+bY3XAX9CVcJOW9vleMqO42YO2PGp8biwxoN5KDdGFjXeB0Im1DVrpEUO92e/lubz4hi5MO23Zgd/pltjw6bf'
        b'Qnj+Wo+uERd1KrrMksGIIMSdCMYj8vlX3gPgfWqrhBM1IOtJzXwRIDG1g81CH7USRKOR1kWWrJCqoDIkpnUbxf9tuo0ZHOazpN9srCPS89PSC7l/dMJNjtOEW3h8gJPM'
        b'ZS8JCf6Dfboe9fI+nRNKlvDgOGidFzTlNHpjBFknE275C2p5VazZb3gZ8Ag4La+6xIGGO28BZ5dbwH69qZXvjFUvOAfOCAnMqvCgcPU8HyWMX17PhjXFxJ32NjCgja8V'
        b'WReBjWg9Yb0afQRi4zSjRHFntJqqIwtwlQi0xkEJYOcCZ9H+gwI1C5zJlSTxuVP6B05ytAZCSQg5aljozqLEjHbhe+SWpRpSZHu+Qhoew64KbLEj7IsotmMUGAGDCrQ5'
        b'bSscRvsVbLMK6pxtKBvTNUTVVBeekpKVLmRRDHFYDzsoeNojnuxuizbAPguOeYi4JtxJiZUw4Ca0a2qhN76XQVdiEF4shYpTxisl1JhysJ/Oso8uN3IJOAl3o1YBAxRa'
        b'XR0G1fRDTXKymC8eyMqCe4R48RJ3GnHdClvhGaJx4FRINvhoX7WJGHbme8OhKStVCXgQG6oyDGAt3EEfkhwXS5oyb10IT1IsLcZ8bXieNhatDJbHRyRiKNsVFCqfeZoQ'
        b'Bw4GrOKFmg9gayI5xcgHR4rJEvck3GoXicGy0WiXXIvB5VKuxmGoYSwgDXW3XL6H0lH9iknZJuU/1/OnT37W6xpS3u6WqOMlpdwP1qMDb3r6UzVilUw0agReLHamA7fm'
        b'yVMaUZ8wqcVJeb8uy6UDZ3upU5YJeWIUO8l9g0MgRXPDG7OkfoNsV4F1HlxW2DxLUpDl4IwuOYBggo2zhCcQlbSfDLgpD7aga6vkWaFgD8VSYbihjWsdSW6XnwQlZ6Qi'
        b'js+peh3LKaFOyHzQCuhGCLSlG6Ef1QqWnZUbCokt8CzYRw4dcmEfXZEno9HyHquKSKLF9zmKZcKYn5PCYZDovGGXETcU7xCwHeYeWQYbXDajJeEY2j9skV0NzykyxcE+'
        b'HKWLx1oijbBpgYFsADyO5BGJB9qfg24L+qysKw1uh/1y8JwkhbHk2+F+dMMiC1q2t6F1chUGkaUmhFPhcBBcoisBNWGArJm5BewNxtD1QcNA5lLrPCJYqllqsN8mEA6i'
        b'K2x4XBxsYcA6cBi2ZzfrCBhcHzRSf6MCLsX9M1cnWuXymseX+g+XfT5wZ4nyCuV4H8+zIVUV4vHmhmcXe6rM8fc1d569KjL1Pc0Df9vi/15F3c6KJnZKy2aVWap7Dc1l'
        b'jldMfGL405bM726hf0+/m8f/4BsbB+53Ty9PfnTtXumtb+787Jpcubty9wfnVJ4N5jQqfLd1Zdrtdb75Zw8Yj4f9fehm7zqzsBML072iDi25o5Q+XLhsdUYrJ4PRxJ3v'
        b'aOAQMRTjs1bTdI/mB1sPttYZFhgUbRmNOx9T9LP9E4MvjkQ+eOT4YUuoXdSypi/tvKJcDH/gnO/jHjW+d7w502m0P0LxW5WTxxOMBz+vjX085PP+hFlfNVN31fw3eOk/'
        b'vq19ek7KO4nuC5+cy+1c5fBh51DJ4KPg2u8etZnCinOHApV676vdO/WW2r2+Q9vfXuP5tVzPhzlqbxwwyHAuKH5772PXj0MdHG6fPqtnydEpXXbmmSDwuoHFhrv1P9x5'
        b'vCkrWqtjvXfke88lJjy8WpR/vB3uXe4joz+Yk7D/68Kg1VszLu0dlAjP1SpTrlganzhadkQg5wzDPYeePfp4Zd79q+OOEmcVq+68+Z3AroBxqiqnPMV4oGLf0qYTdyLH'
        b'Lmj1tDBWx1jE+Z96Q3P3pORn6xc/ecr2W3z3x3lvreCsk137t1WD/QbXvt0YV3QN3tz68Hsq8dy8d0/fD83nvvW3h5XlSxPVWNnzZBxV37fLb7Ubln1j+PBdw8lqpScr'
        b'D2/Yk/GDhq7kup813S1D1psqLc/sznC7cXdfvwvQLHhyLWdoZ+mO9iGbXpkrXuYmKebnu56YZpRRfaHnWr5OsrPTrh+5PO8XEz3b6rFF91Z7X1zQl3Z0dtAHfxM7Gjbn'
        b'xN+Tv/t7tdytt7Q/yLAI0ihIc7uec+50j00QtTxqz8KvOflOWeUH7sq58c4ea0y//vO4Ut0GRb0dSxupGI/M+NGHMQZfBLQbJj8/UufwfsalE2VfGn8m170q/sutiQPc'
        b'pX/nV/5InazY3HLo2zsWV8/ZLwrWK7iW+1Z2P5d9eaxVpvDqLZsLbhIP3SWLFdzCJ/vKNy+5Ku0WcnuDwn7ZY933vzApYroXfPfRufk/ffN+wuHCW/f+9knR8ie56oNn'
        b'btU/vGW9PLyt+pLeCaevnS5+EQibLR5LF350Mt4h7ZiN19fvjJ5ndBX/uDPOIzlxW71gyOl60oesC98u+EdpgcH3EyHlyo9Y3i6mDVLl/MbwSwVRNwcUBzaseNthjeOF'
        b'iz8feXjfadYHJU3zK1xYfdePvvvtOofPR+C17Wl1O3bdeV4reK9xS3/NU52eD96/e+/UxwHfSN/qDMsoNVX95KHhl/rjk2ZvXbin1ffe+6UXnY58+oSh/26UnaL2m+ef'
        b'bSxt5m5WKTq7WbGZWWTuxy3/bPhggufn9w47HC39x50r559JPTj0loaPdoS8htLBBHmNnyJiWDfiVjolXWnrktjXf6JDQq7r4BJ5o0aPRHmNHrdI+fVyDzinGFsei71/'
        b'pbzr58l7vi3FncduhjWf//x7gwmJUwu2yJy/8O2XixkuF2wVx+Otqbwtf7vU+lkZ47My6dPLPb92DlB1E9gWy/+04ucPrwu+3R7z1OrBh/L3B7/fWCcxmbv9ovqmcofv'
        b'9Nfvtzz1/Y51T87UXs0McH3+hUdcb3qB3tsyg10bqDKO0j/DNl5q3/BFzNtLN3z6wfVdz9+O7/hYY0/50bkb4E3F9fudyoat3ri4Ycuz57dtlrYXnjzf8e0/n9+6W/Tr'
        b'P1uel+/4WB8NgRtUfk5laIzdf/C1TWaYUXejbN83Tx1ru29tM91V+1z/nm/4u7+WF8Y/dwsc/C5QOfu69qHKkYCHPzutrz6qN7a8e39+x3OFYeMf1Ud1E8LGNI1+dP0h'
        b'6vMzP4CR4LbQ72Yt5OQRpnYURtG/wu3oQtgA+sVgd7I7DWjfDFs1RfFjTfAEPmSJgVvJeYgE6F5j4QxOWb+svIXG7ioSQxbYjs8wdgdNX1ZcIGPLyvQBw+QUJCoOnJlW'
        b'JiOnKQXZ+DwF+7f4AUPo4GFYHzTjRGXqOEUbXKB1yU6AQaJZpwu7QTMqFrhIs7OtrP2D0YpILVhMHh4ELeRQxc4M9Ewz5eFlW4yVtwJV60hm5+uBi9wXHDcGJS8fDkdY'
        b'C8FBDXK4Iw+7TLjWKHmrwtAyBkcarVn7iRIfrGRRjrBTItICbCSHI15gKCto6uzMy0tiOdMcNsBT5Mgt0hPuCAo2l0AT8RFwYBnDOZJDQxG2lIFK1B42aF3MQMtmVLt7'
        b'mMbwMpfEWA72+AdNs7cV0Eqyk1mSaUjy7akMWmVhhRWqtF1BLEoyCaV1lhkGakAnIbahte0+zGkR3gH70SQrD3aCQ6ACrVLSrMiJkfS6BML6Yy1GawDioARuzCIZi44C'
        b'2+iHrQLwvL0HnpFhxvqBZvqQ8eKaVSpwL9c8AFavJLiIPaGSlBLoYRWBhnkkAjNU/YeCCAuOvGbbJA4vMVn5oJJWOaxADXkA9gfBvjBZ0AFOm5hJUNJwkInXoXE0y74C'
        b'jMA+Lkb0S1vD03AQ7hanZGA1E1YhER0ikpQKKu1wLqU5sIdUg3xAHrjIUoYjcCcpoFuiPU27cI0UngZKwB0kB+FoUXuqwAg3poU1R8bMHHSIUbM1WHAjylcFqX5djWhZ'
        b'6yB4jgOrcBX0wQ4FZrxfLok4FzaDFi48LRfKoJdJ7aC6nFQ8rAA7dcFgFOxHRcd1T7wMiFOz1FigAbUPuckdDoOBoFBLUGkjdOgiTmmvgJvBZjFwsgCVDsvtWnUPrnUA'
        b'6JZDt1CUwnp4QILlAY4tJ90wXAZ0yAZaBa8Cp/2RdHI5DEoTHLGMEvPLg/uJzDnHW3JBNzzDwTm8TIFhhgSRHD1YDTqDprwbiVMK8Kw3OMByXwdO0zj8thA5EVg+pQj6'
        b'SzAtH7Zok2ypwA5wkBtgzmGCi2A/xQIHGGC3KTxJTgGzUW+sgP2ZYABWiVMMWQpczIW7SGPZorY9NXW8DC4pT3udGAbbaW+Om+Ex2EFg+iHiURY0TB/skSRHv24a2GOT'
        b'8OT0gOoUTT9PqKCKVtZ7YmTNUE2sCgadsIrDRLJyiAkugLNwE2nN+c4huFQhVgwkaDtU7ZigHm5EKeNr+YvhaVlrjjlqLpRrKaW52cxsPXiMVIcVOAEPWaAmsg4gHnco'
        b'xdmwCuxmpWTmkhJLgVZzlPAqJAiu+uKgjQEbwd5gGpiyAxxQlOWg7tGP4w0qRvs7BhyYhyoEp+oKBojXK0skemwf+qxXFZygH90IesBlJP2ooKABjlAsWMkALZmgnh43'
        b'hqTg0SDy5mkZrLWWoGQDmbCtEFwWHjODdi43mINEFqNDLkQEoZ6DdihNbNhMx34OHC3CTVgYjKlP8mAQNtqwpNhwD+0QYLcH6hjeYFswFp0hCpyRcCItZIvKtgvtgwrh'
        b'WRY8EI5Gs8sMbTt4iT4cPs7JE2rsgk4T4csBX3FSSfmgL3FqJ9IDTuOdyFk4Qs83ByEa10S8elCK5eBkDCtPXJqk6QG7QA+d14IsGwYls5AJOtxQNRnT29YtcB8XxbkF'
        b'O7ugezMqNB7tVNAIjSLfwiGuQdB29jI4wYXVHBlwxhKew8N9XzDuNAPgoJKYOYqA9vYAtsQao3iElyPAWfEYBtzpY0X7xwA74bDwPUEJKhPDRoxDCu9cuga/slwN+8Uo'
        b'tJNuFJvFSGSCPeTaBlN7LvFNxkBPbwLH8Ov0A+ACuaZqgXaYNrDSjGlfgKrsGAMcA8dgPcmJMhrDt6IcmwWuMWdSkvH5YD/TdTHsJm0c5EbeuaI+jF8ZYxGiFNPBJiYr'
        b'bVkCLSID+qpCb1HwEjwv9GkVhuLGw59s/jJuKJ7N0OgrHDs11sFa0ClmlwtrSMPkwvqpKQZVBGqFTnFwGEm3NzxCj+GdsMVUOH7CPlBJxEUGDiChmAVoQYKVqqjWq4hv'
        b'LGbi/BiGlaspebZoxSKumhdqb2lYuQb9IUkow/0s0Aha3Oj3CQ3SoAN7vGNpwh1CJ1ktfnQTtaPtbNvUuwZY6yIxn8mWR9nCaSaBbtAvWywvzVwFD1IsA4anVga5kCMF'
        b'm7lwF37vBTarqTDmgCMLydih5A020uUIWEWuy4NmOAA7WMaWYDf9ZmzAGG4NEnEeZoAKhf2HgYtLiXQppnKIuxIbuDPEMgxu5QSEoKFd6ADHxV0CHOdkkpgs4dE4+gWL'
        b'8OUKapuD3qz5sAs2/mCPk+oDg3HEh81rfXihrjOEoo2GZ6RswGGhUv32LOM8sEOW3Gy1Co/O1CzUS0GLARIY3JwmS8JRwi/e7imgYeViJCtEHi1RiHc3eEEViQTqZhtk'
        b'cDfzYYJTYA+aLXFjaMPD1vgiE9YUoxG/jgGq4QVFWs4uy5XRz5GhxA0OO7GkQQ1sIG+e3NxVLH5TgJBVEkIfJyiBMyT/slagAZwKm8o/Tgrl/xwLnNABdbQblPZZYNvL'
        b'7s8og6R07P0MtIAe+gXacJqYLJ4vwRA8hzrUIAMJSx/YR1+shQ3msnDn1KJJSteRYoaHB9GumLb7wTo0CQQyFPPRg2dRT3TOIysRNCdtA5u5CotRrmQCQ7CooIdVwFYW'
        b'rPBEa1482ZasgcOyYON8DkUxtCi4bQ7op9ulqtgNtMFGbijstUGrDPLWTymHBXZGoIUayVQNPOoA+y2trZmgOQ6l3IBmvaWggcis3PyVspizy0SlaOYw9OAltIDAtVGI'
        b'xobzXDQBwErpFwXSgFtRYjVi89yW0JyrftgOm2WtcKko2GYtocdUlrWih91T0WgFhB2nhlqZY88uSFBQ161bDXtJtlxS4HaujTns8UctIYkmLXCR6b8MreDx/GGwAFVv'
        b'v1UoObpBy4Fq8TIGqtyTsJ1U2AZ4aTnGiIHuFz5rpvzViIMuEn8ZaDflWgcWc6SXgV5YiSYoJhMc0CwnvSQT7isVLrMDFM3w2CafVw6HWa6w2V34IhhVyOZpCxDYl0eM'
        b'QMDxtaTaDJJgc5B1CBqkdeHREoY7OAx30zPbkB5sItYhqEovUCkMOzltUh2BaAo8ZhE4RS5Twy+qmWATWkN3czT/dxlAuJO9QkNP1CWNRCE55V+n+Yr3H/Ql8iJzpSz9'
        b'InO9LfEef6DknpbJqGkgXytoVCUIY7G0G7QFmjY8TZtRW0++pleNxLia1sHcvbkCNUuemmV7NF/NoYY1rqHTKNsgK9Cw5mlYj9p48DUW1oiPa2iPaQQ0ibXJNssK2I48'
        b'tmNPNJ/thsKu+FyRxtf1mozaLJotRjWs0C/6jduYemB7+ph1wJCYwCWA5xIwygmsEZvQZ9fI3dE3aVp9uBx9UWE3qbTpN+vzVexqGJ8qq93R0q73bgxqCBIapKTydex7'
        b'7Hg6TnytuTWLxtlz9gZMaGk3mjeYj2toCjTMeRrmfA3LSRZTW61m0QMJysCoybNZoibgcz3DGt/xOZw292b3lgU1weMooWCeim1N8L05KG3si6RlA3/OXNEr47omAl0r'
        b'nq5Ve3J3VkcWSqBRpkGmaW6bW7MbX8MG/5ZqkGpSPayIv6I6avJuC2wOHDNy7Zk7ZuQ9FMvX8BnX0a+XHNPwavJsC2gOaE/rSeBZe/KNvITh3sLwjJ71POtFfCPvCU3d'
        b'Mc2FTTFNWugPdmaykGezcJJS0NS6knwt52rOuIFRfeyYrjttg9OTweO4P0Jir3fFAKOtx9lGbdLN0u0xPLbDGHvBkMQY2/+KCaqNRQw9VBl6hmO6Lk1RbXHNcT0mPGMX'
        b'8uRQ8kjWcNY426BNrFlM5OKY8aKhmDHjkCur+exQFIWH3gMlFENjXENcuwlP13ZMJ6wneTC3NxclbXTV6MpqaMmfG4ZapN5vTGd5u5jAzIVn5oK+DoWPLB1eep1xW+yG'
        b'2PUoQcgyXsgyvn8if/7ySW0FP4bWAz1KU6tRvkG+afXx8h7VRxTDNIgxlZ8Y7NBIYDyfZzx/KIdvHMBnBz5iMU29GRP6xtjNjUDfmafvPCTD1180Kc7S1HoghSOTaJAY'
        b'19Ft9G7wRtKk06wjMLDnGdjzdRzGp9/K8nRsJylJXb2e8MG43rhxtskYO73dsdu9w11gsYBnsQD9vGJ3zeWqy3Xv28E3ggXBy3nBy0eTUkeTU0eD0/iL0ifwI1lTjyzk'
        b'WSxEP6+EX4u9Gns96nbCjQRBSAovJGU0NWM0LWM0JJPvk0VSCWy363bucO5xHHTvdRc4ePMcvK9EXkkZdQjgWwTiYks0SzQVYYEUmLrxTN34bPdxI/MmmTF2xmh4tCB8'
        b'GS98mSA8fSw8nW+TwQtPv67SwxiU7pUeMhriXmEOcd639R4NT+fZZEzKS87VmxSXQ5WihSsFya6wUl5KxYVn6sJnu6I21tUjXQa3oHs7o1u8Q7w9rXtFxwq+mfuktDiK'
        b'SA5HJN0gjSNC9Yhae4wdi+6U75BHwpDZmzmUNpI3nCdYEMZbEDa6OHw0Imp0QTR/bgzfLBZJm0EiY8LChq4xtzELtwcsytx2jBPS4zno1+s35D0SPBwscA/muQfzHUPG'
        b'OFmj4RGC8BheeMxobLwgNpUXmyqIzeTFZr4XnjXu6XVN7aqaUKyQQMXzPRMmJcV09SZZEiinSpSW3iHtJuVHFJKKdoNusw6zcV2DF9Kr69uT0VdwRXxMJ+K6L5I5XW8k'
        b'c0bHFdvVxthePXMHPXo9kEBZaE3mMlxt1CYpVz31Gt8fVjMofeN6JnY4VEho8R7tyWPaNuNzXQZzenN4Og71oR1+E1Z29aHjJmZtOc05PbOaV9T7YR9LWMCT21Y0r8B1'
        b'59fghxsB91XDbpMOEz7bDv+Wa5Zrj+iO7Ygds/IZkuezfYnE+Lfbd7t0uKAvQ4wRiWGJocKRtcNr+S7+pLioTfSMxnQD273bpdCfIRWBayDPNXDUKfARWvHooUYQLF7K'
        b'W7x03MC4TbNZsz2DZ+CIm8JwyGDEYtgCexhDI1CPGs/IeczIa8h3zCj4SgaSBTdDLAuGbVLNUuNGxm3ezd70mDM613eU4zvGibrueNv1husYJ3F0SSLfaDl6xIA8Yixg'
        b'2/LYtkgwUN9a2rv0CuOa2FWxK1ECn2ieTzR/YQzfKXZSUSocDUmzKV02GYSavGmVGHpEmjWiNayF60OmWQb1FscOxx4xge1Cnu1CvoUnn+2FkpqHJVVXr9GnwWfqRvtu'
        b'1w5XgYUPz8Lnuj3OmiBoGS9oWZMMn504yZJBNaVFGZoc125XHtWxGtPx6zEYNOs1G7IfcRt249v7jevoCXQcUBOO6aSgepYdlr3iec37qvf12YKAJF5AEt87me+Sgu7C'
        b's1FjWEPYIwrVPt33hG03bmxxfHl78ZhRBKpb02HTK4Z4UL5mc9WGPy9izChvNCZWEBPPi4kfTUgUJGTyEjIFCbm8hFx+TB6pvUmWmJ3eAxlcLt8G36khMKItvjleYOzE'
        b'M3bis+eOsw3pSdcBjfFoBEPtyBiRHpZGY8SYUWZ7Ifb6JbDx5Nl4op9ozsi6mnW9EHuWE4Ql88KSR1PSR1PTR8My+L6ZE/iRnKlHFvFsFqGfqENJ3pAcXRwhWBzPWxwv'
        b'WJzGW5w2mp41mpE1ujib759DEgppX9W9pmNNT+FgaW+pwNmP5+x3nXV99qhzMN8mBIuLb7MvahC3Djd6NOUbeYybWTehuTF7NDpWEJ3Ei04SRGeNRWfxHbJ50VnXo9AQ'
        b'ENAbMJR2xeGK11D2+47+o9FZPIdsNIi5GqJBjLQeqpfAhkBhvbyUihvPwo1v5D5Vj7qkHvXplYMTWi+M6WTQAo/qJO1qGpIQtxtugqA0XlAa3zedPy8Dtyxq1TGdENSm'
        b'Er0SPasGi3qLhrxGwobD+KhctiG44/o3+I+zrR9RsgaGPXaDc3vn4mwENwePm3G6xTrExi2tuoM6gsZt7QbFesV6YvrlUIasrJGsWrkJLH14lj5X0viWQWOWy0i/jOEt'
        b'RkNbAn/xMjS8csxRV+aYk1E3n282H/URYxPURYwtx4x8UZ7ke+WHMvm2vpOqso6GOAdzH6hRJqZtsc2x7bF8Y6dJTXk0+K1hBDBMtR5TAQxN7Uez0Gj1wJNJ6c95kCFG'
        b'zdISKLF5SuymWWjV4d/sP66ietBvrx9aX6Fy81Us8e+AvQENKw4X8FWshb/q05oSeHp2fBX7qYCMpvU8PQe+iiMOCNwbiBc/Yg1i9VGNCQ0JAl1rnq41WR3pNMo1yAk0'
        b'ODwNTrthux1aCfaoDGr2ao5qzHtEyWjqXXEaKiFfhLPSHbYBWjNymjnt3t3BHcECy/k8y/lDKUOrRi09eYZeV1J5hgFjhjHXs8YMk0eXJqM6NTbBEiCs+vZINGhOKVr5'
        b'8Jx8xqzirqvc1rmhIwiI4wXE8c2WjptZjJlF9IgNyvXK0eMJ+omm7JirMdd94DI03hubTEpKYgGSRlUpKa+qNimrbDz7B0p5lvJDM2qWbn3ke0oG4+paB9ftXbd//ajS'
        b'nKePFolRtpmMp4+SmJRjDoOYjo8Zaa+Vsr5vob1W3pZWk5J+FdDr9XsArGmUNGPNX/gdxn29fsGvI4Eew7CGpxupJ8W2DMbsh9RfJH4VMQk2FkPq/qGAYooKDQ3liKGP'
        b'wmQM05N7CdZa+IwisLPIRf4+IT6RBM9KoGQ0rfXwNGIV57xwC64F1cKt/6ldFN7iL3w9RNUY1+YraJAUVhcrZ6Bq3Eo9FGPKK6EuaRjBGNd1GjdA6weLh9LiRtidHwmb'
        b'P24w5+UwHxKmPx2WgcKsxg2s6PvMp+97OSwQhZmQNOahMJvpMKeXwuLpZ1GYNQpbyMCBOlbjavbjalYPsxlOGgoV/g/yGZSC2iSTIa+LKaZqD/C3R3qYbxo7ahHGWxJ/'
        b'R1u/I3JY+Sr3BxZDIZgx4Rs47unzmOUm78+YFMchD8Tw94frGJSKzh0l03EV7x/EmSq+jArvR1Ikno70Xt/2xKupN5x44VG86Dje0mWjgYmjPsvvaOl2OAzPGU69anR1'
        b'7ajr4nFdB/SoghPqrr4MVKKAsCcsP6a81iRFPiXJJfz1SYSYF0ve6EcKf9LIVfJysIKZTpCrNHVEesqogkm5L4VdoE4C7gyGF2foqckK/06mYfKq8h+QV1lpUsLv0iLf'
        b'ZdB32TQ58l0efVcQhiuKfBdSWI9ITxNWVV5DWGW9krCqOoNuqjtNWFX7DWFVfSuVptGl+e8mrHZpdUqI5EBvmq8qnyGepv07ZFWdl8iq+h8qEiBxdmF6apF3ekp20TOb'
        b'32BVRa7+C0xVFxqmZ89hfii2KCzC50OWl71XoQUeY6zwhw3rz8NNXWgalP1fIqIKH3L569TTqeQIfMoOU08LXTAMlEX4pIWuGFIqE+ETEhblQ2inRi+RRiO9vSPSV81E'
        b'3tkWuuEC/5lb7aaRoFMZeabxulinOaEz88yRnhEHbofCX0Vho1OVU4ghn4XP8aXXpWFX6IdL/b+NCM14GRHKpF7WchWnrVHj9OFB4hTEHpwhfkEY5qAK9tOqj4PLrWRX'
        b'rwqFpxnEcQE84gEPZqfxJhhcU3S52zv18NsuR70MmvcbVDGUT9hm5NraqtjF2CcfVMyYCGZR7wWIX+yQ4zDIWWkkOA/7yXtscAHunbJrMV76W9YoDQHVeKl3zWSM4hNa'
        b'zBhNcxHV8B/XZk8x9ZXY/xPy6GsTnS0pgh1NdvkfYEcLg1j/12JFMWjEQOLPYkXTSP1gbiI2kv93MkWnut8fMEWnuu8f3uHyp5miM0eE1zFFXzew/A7k85WDxKvv/wtM'
        b'z5dxKLTlfnI+NrrHVJPXMDqmH3uVy6bfcEBntLOQ/YknJ5rniSYo89fjNP4IujmVk7+C3czO+C9x8/8d4uZUj3sFcBL/+zPcy5md9k9yL1/Zgf9Lvfy3UC/FQ6OKF6Af'
        b'sBWTEl7gFVmgSZSwCPfB3cG0bbn/i3f5YATukIWtSs7Z56lRJhcbwJvnlhx+20lb7GjzVobEPM15ruvubHKMNM00jTflmgaZlpp+nbO6wnLOIplUUz935QSnSDVtloTZ'
        b'F9afbu2NrI9x8FoSsqtW7kg2tSZRfrj0G444/a56I+iA7ZFLRKxMbeFlcIZ+Qb8HnFPElENwCBwQkg5FMIfHZWitErCDg9UbykpfqH9i5U9/UEv7qYUDC6de0LbA+hSG'
        b'HQZDkEfZWq4iTmptHLWF1sFOYBdH5n9wJIAXEa9E+v12KSPK8/Ol108/rHSlZqnVFDQV8ZScejKHiq7EXI8en+t5Ze51F0zzi2aQs+8asQPy4+p6B0v3lb7ExdOY859j'
        b'4r22RBqSokC8FS7/IyBeYQLrpeX6XwHhFSbSDhBeCcH7TcanCHheKOMiBDzD18y6v6HeSfy+aWKqpEgGZWesMsVnrjLRGlNauMpkCpF28hhplyFLVpmSM1aZUmSVKSmy'
        b'ypQSWU9KbpASrjJfCp2xyix71Srz93F2ojvs/ydYdjOB7MKlmxDwtgJNdpi09V+83X/xduz/4u3+i7f7Y7yd5WsXeHlo3qB3XVMN8Rdod78zZPwnaXf/YUbbbOGpGGhR'
        b'm0K05YBzmMsO2sA+msyOX0iVwTqwjVYUj/SHlWFWMUL2VXY85mJVwj1BsZhgLoUthymwD1RJg/OgCVwm3DXZJUk0dQ0cMpgJXkNr5m2K9OFbVzZFgG8RBTT5HRwD/YTY'
        b'XkQbnQgVeV8HUGdScBM4APbDRml4cQUcKrbBkZ6Ce0FlUHBoFFqW0+gnWOFvSZuyw4oQuCuImFMsN5XynAfP0M/0g02wIUhk9b4AtuAFPOZkWcLqENo8JkJWEu52A3XF'
        b'HviZCjF4AlYJ4wvNjF4caxUTi2lfgSHBoCPKH5z2D7G2CghBkdgwQZ+sPaiKiKT0wBGFPFjtTZv31vmCJuKRGDTAc9gr8SCoMiFZ8ncPFEYOz6yyDKBjx+SqlfaFGFdF'
        b'4HFiVBKokgS1edrkmXCw2SNy6j5cXjNwBrVXFP3IdMnjMyRBayDoI2bE62BfqGyhgjyTU06xZjHmwzbYKLRcXxoJ++HgGi4rcxnFhCMMi1RwjFhFK0WLU1KUGVNmYVIw'
        b'K1idyu6+7CfGZaA14ZGHl47uC8knuPgjNc83mi/eplR6/v65d/SOx/Ys2Xp0i/nWfT6d+RKV6e8v+nxfcNYGN99TDzK6vnxyUzv+1+ryhYw3P98fyRk6s/7WThh4aFPC'
        b'6a+jGi1KjoWcOBneWWex6eK7gz+syNH7HlZzzX/+qOz4atm1kv2Gn8ytPfZNIvVuzY/r6pTn3DiwZMLs5veVzH7v2V/cOTMZFNyaw50buaCo4aoZ17ryu2V1LPO0773W'
        b'7dH7545f9Fq/TM0V3Nxe0HvgfPUZB0X+Z//kT97lhJVH7Cs/2XXiy42+Bl/9sLFkWVvr8aY7t0Ovbvjo2fXWH35++/3PPjm22J+tMUt826lDnzyV+FQgHv7c7zh3F4cG'
        b'9OQj+W0Psrby1TUXhT+BRriJNoNpQc13bAb+yWwNwcQ7wAGiAetUiAQSw59QTDswJr4ctJGofVBfqhOhM2WCBlmCZ9I1pzWZG1FX3Ce6AaO3X6tCpKyliCa4Eqh3nBZc'
        b'ccoN7pHNZ8LDSwKJfrUybJGnN3agy5hg2VvBWdrgaNcycESEOxUBe4lhUAa4RKPlz8GzsHvKcvHYMlHjRWK5iDadfURvOADWBZAirAf1WPseVqLkFOAFVnB2DMkE6JVJ'
        b'gFXYqAAccqfEFjBAZ+lqemu7dR44H2QfiLpMG6xjwG4KDmLiPm2LUF20hrYjy4wVnr7DLhdSLV7w5FyLQNQhwVbQiRsFFUDZlAUPwyOoYvHDzrAN+wUgO2a4fT3ZNBfF'
        b'EkNH0BxjPYPLNE1lQpk4SMhMYCSWo/BvegeOX+KzZxCRRNgp+i/vtF6FQiqkWfYPvd3+KgoJo3n0D5bvLX9P3YxshBfxtbxHVbwnlPUIkojWsLuSPuYQRC578bUWjaos'
        b'eiBHaRtinlGNJCYD4Svz+VoLRlUWjCtrHXTb59bkjLVve4wGLXstBfZePHuvsTleRK956j51PYG6KU/d9D11DgkPH42KF0Ql8dB/pkl8reRRlWQS1163UWVz4Va9qait'
        b'pLmkx2fM1PWenvmohc91ydtyN+R4FlF8vehRjehxXaPG+EPx7VHdcR1xQ8ZjVh7kNt/r6li/hGcRzdeLGdWImdA2FGhb8rQtx7Sde9TGtD2H5tZITWjPOTS/aVWN1Ofq'
        b'OvXL29N46ouu+F2PGY1OGE1MGfcOGw2PG41PnWQxNNIxDGhWuqgXX4U/g9f5Y60SIgozSTp/QRR88KGBG7r9+Ubqid88BiOA8ZjCn//SmcH/BjMH7aufLftDZs6rttH/'
        b'JmAOO5RM+kZxUUEvjJD/mJUDN+lP43LkYQWB3YTM9piGRNqCbrAN9FApi+azZClD2MWCW8HGOLJAywHD4CQNzAEbYQvt7iV3lhCmA4/K0iQc2BrBwCAc2CJklsT7MfFr'
        b'WLMD8kmWh7T8aDc7ifbxmHcjCVpsKSHuBh53IUgQuHFBGLbo2pFPUTaUDawFtWRlYG6jxF3FMIS7sNt0ClSi8budZpm0w93JFhzzWHAhRFzIu2liEPYIWnqNaAtxN2An'
        b'bKUI8GbnHBKhVylaUewWWwZrhcCbQtBESrMybCXG3eASBLKEvBtp0EweigBDoBatJDXD0SITo2mK0foLzyHm7rBtBn7Gch4lhfEzYrCC1IOdVTWlw6CyOm2TQtU0dGh+'
        b'zCIjQ8qbotbqSSUZei3NoAO/jQ6gatCSS7kgybzZI4AO3B0hT2lg+5rFSZaPS1bRgWNh6pQlRS3ZaZmU4BtoQzsXlgFnQKsofwaeDKQRNFxWmGkAWeo6GoNuzJhBs/Nu'
        b'eRaBzMyzJ1HWLcQoZCrrinVS3jlWEMVhkHKDgxLgEm2KmZbBlGWw48FxmvuyD7R4YiKMxhxFJgHCSK0iSZiguahatpAFLiROEWEGpehWaQSHcQ4JEgZeNGUQIkyAQjEe'
        b'YozVQK8sFQdPo/UjFR6/gWbI1IsHvqDBBDJh06ql4ADcV4zXAXPBMaMpIAw2+qSERJiLoDFbuyxHnNuKxG/5UOelJf+suhelcutmcEbGl8P8j+6szrSyyMruNDN7c6nn'
        b'+h5zmZ1jmzdbH9+tVrCqNm6g82OzBYsl1M+nRHtbmpu936sSvlhpryH6d5y9c2LkbzeOGu2/+TT/Ysfpp8Y31tx+emvNJ19+LLAomHfG4YjmY1/Au53zWe9X76xaP6vl'
        b'dlVy2HmF0hPX7D7ZfYnZtjGW83B2YFfl1c22JbGb1rg+XF1mYxZ+9OQvgZtr/zESlOf0XcP42kC51eerH8mFa7NznB4/vvTUMdYnevP9t7e9vd/qO58sya+u3zeotstd'
        b'rPu47sjuZ33Hvz906saZO271EcZOP6r4yAemue5PjYtNjxbUpUfXzm/nWnh/yVi6v0wpyGjB3ZKO5UG1No8K7++YdA2cA1WrPQZMYuCa+Z8q3ezJi9map74xSz7nYGBg'
        b'5IcbJHsKIr6Omvt+sumgYZGzt43ErtP1Fm+WVJ52HnirVUd810HGW4cu3vtGe+CN2nWXv/10ddTqvfmtl8TPMo91fRDu+um4pNPyN8NLnK79PDdrW27TB1+j/zyPGFe/'
        b'+Y3EHm3XcyZz30gKH/zo5sKw8T6BjPInVhUFPUH9H739zjdx6699/4Ppitruv53TUV2zpJOyPJEyryXl3fOfHPqRSvv2Mf+zidDcuaPlysXrtick57VecDn3uc4KnSJF'
        b'V8mP/u66NFX7xN/z81u1Dpd+Fr2mLL5h/ea3zD6c45cfcTB94vsbpQbr9P3kP/z+S43DYZ+ppng+uc2qeXpVpy5AXm/zUkWW47vU4/trFRc1+jXJvPPsafzPDQs6jb81'
        b's9Es/Sm8Wj5f0LJ6R8xwzmlJ21aVe0139Dy08yyq3ijaevAzu89u9/3Y0H0qjDmSeOrn7LtZWyWUBj7IzdqT6VI39kQnrXxTy/ruar/e3tpDh59vOXkq/IMvrPTbvo+p'
        b'T+2sW8/rutXodrHqrfccz53fcVzy26b+sR//sXvF8bzelkPb875Lr1AweCazML7wo67G9dVejfLVvsN3LeMNQFx5ZKheX1j9ZE//0aPB93/USsq/kapTW7AkfvOPj/af'
        b'7qh9ZHXl8xuDBs8Udq3T8S5TT/qeaxn9RPFX5Sc7qP6bEwuYqwPOeZinfxP/KDW/Me2MaYnmLQk7xcgd8VTXm45jQYYfe4RlWbU1qZ2VXOqnqbOYdyQi/+PqtNtZ/XNU'
        b'M90k3cbaauSfWEYc3v+ltvstl9vOD1Tfnfw2buWxggc29V/e7Ve5MSnflYm+PdG/PSl/+XnYseeaD2xqvtQ+G//50+f2jzy+1Bj4QO+jw8sXFj+eVFrJil7uJf6Z068W'
        b'7dQ3z+slu6yWsz6Z+6bbyc/KWJ8d3f7VoNIvt2J6R3Z35EK3957eOD//q5zaT1idC1wafqHOnm1YZvrpL7PG1/Q9Plu663T52wPVn+y++Xxz35c/Pnn7lm/ZL3f6Wk49'
        b'ylysvme8nPHNsZ+NzGpbDjz95S1e1J7nt4I43E/2XTrs9LFtnb3z9p8Se4/0PmPd9zi4Jvqr4GDTmg1Zz01tSg11wtq2Javu/O7dTct5X3369M3lUrc9eVbfl/ACkkv3'
        b'XvRsNPxil+nTERff8Hcfl5i+bTv2Xcrewi/SOW7l4w0Ov97+RtNQp7X/lH2D6ynD5xLnW55s+LBk68dl1Scun1T4hfXTSbH5QSc5K4nxK6yHdVzhvgXUzfnNvgVWZ5G9'
        b'h6ui8gzPX0wxWLXaChylDTXbrGCPhShthcskvJVC2m8Y6A1yFIWtRKlTiraszCRPsiPymwO24NdtL9goesWEjjIX9NCWlJfBMByYwqO4wD0UjUc5nUtvKDejSahLFJAS'
        b'YUnJY0AK3KrwAwdH0IlmjvNCRAon0HpVAMYoTBFSEuGQG9gqAfr1wmhIwDHJaY4DY/ksClNSZEEduaYFNy+dYqFIwjaahZJhSDZRTjqzX5BQQCcTtvmXqNiQCtJcGSEK'
        b'QoFnmaAP7g9D08ZOUoTQHGoGBgUMgEOUPMGg5JmRhMEFrSLMQbEHdSEsmoMCzgrtYEGDIzgqQkKRYUb4x9rDYyRqP9hTJApBgefmTXFQDMtJ1Ms0QbWQgrIIDlAEggJq'
        b'8mhMQwU8AM5MQ1AsLaYZKEVJpG2YChrT/BPfF/gTP7CJprBsLoGNovgTtPuvRiW7yFJ2BpuJcOiBdkcRhokCE16G9fGgspycBWQbreGGYuJhu5BhMgueJ69ywWAkvDQD'
        b'YFIFTkxDTOBJTXpXvF89Fu+Kw2C7/5RSmlYSTWLeCIdgvWyolRyHAhUpaCZvYcAzcFMKqTYWHHCZyS6IhkcoRSYrDVx0IEVzMlGapqPMzhHyUQgcBWwHe0kSitjO/wUf'
        b'xRJcoBQkWB4ca2KCbAyPcggeRbUQr6VhJYdmpOiJiYHe+RSp/3jUA/e+AKHAXrCRUsAkFHDcmsZknNe0FSGhWMBDlCImofhlkvIvkgQj3FAOWkSf4TCFVvGy6rSYt6OV'
        b'9D6C/VgO62gOCtzsSfe4QXhCfuq4Q0xrGoNSp0M/uinDjDBQwBFwCq+DMQVFS1fIZx6G56coKBLwzBQFpRRuJ9ctYIWpEIICt6i8YKAMwhE67gvOBdMQFDskiSOgHp4O'
        b'p8eR3RrWIgyUbCY4qZSNWukAqauUVWiQeAFBgefhPtQCu1kpYMsycrIioR1JU1CWqlA0BUULHCCZmgd3wAvTFJQC2EjRGJR8sJ3u2vrlGIICOzfgg0dCQUHDBJ2nNnAe'
        b'tuI+0AQHcWFpCoqKPbmqADtW0AwUeBwcmoKgqMNdpJqXgEvZ0wyUeQlTCBR4UJHu88OultPYAhN7St6JJe0Ij5AcrdT0IgNFCzgj5J+grcAp+rEq3xgMQAFHULc5y6IJ'
        b'KCwGyU8ckoRN+GCbCbe/cFsIznJIZ/N3UqWX3f5gE153o/FpK6kffQwtF+Gf+ASTMz1UX8fJCDRXEtbQOQXNzGkyw2FneorZm+LHfRl9ArpRJQvxJxUrCXBIXgFeEoWf'
        b'gFpbIf9EScw8EFSTAqxkgZ5p9Ak4qk0R9AloNSUFcAMHxWn0STjYx0zEDEqabwL3g1OwYQp/slKKwvCTpdFELEwtw2n2CRhezyDoE3twhD5w281kE/QJqFAzYwrZJ96g'
        b'k+REBmxc9YJ8AvYzQX2cK9rH7SKFsUWdYx+uEhnUiWDFYngkBA6gsmjAHjGLONBPD9x18KiX6F4jtXwp2AQ6SFnUk53os0g4EEbOIjejspAxtYPyliWxoihzUCdGfUEG'
        b'FRd0wQuovUjGR9BouFOWZjmIFeKtqCFqwkP0kHEJtIP9QkwFOA1ahdwV6ZWEwQYGUEc/yMXTZNaCAHPpafiKrpsY2IvEZj8pvgMDbJoir8SBwxQNXgFbHIjAKKT4TmNX'
        b'4OaoaerKBribLvkp1OH3C7ErsAJ0MGMYVjZovscDo2kA3MGdCV5xROM/zV7JlCIwC3hIem2QVWCAJZ4NMXhlwUIyCCxBBd8rSkpRgzvQYqCDZaxjQ26whkPOopgUzEjp'
        b'AD2gFlYxfzAlO0ZH1RegFFFKCqrBCzQpZTm8SCohFZwO5NILCun8QNBBUUpwM6tInEFkwFB/NhbVII403MkJKAP9wvlfE2wS8xMXniwrg/NINMltRAok4REmOJTtCSuX'
        b'0jPwdrCpRJSKkgIOUAqRrBAleJYGv4yAjaj3Cw+1Z5UEiFPkTBsOgW4i+zqgD+zCJ8ryYBOuLXyinIiuEVmqhQPgLBclHYZEao8FbPRDQ7JSCWs9PIc6ARngTkQqWyBB'
        b'RAs0zLmFDUzUd/tKw8rJPBm2HuzmYjculXgJiconDY6i9c8sVVaZnfkPdvj5Lam5vw+LgYPR06yYzfAwTe45CY8lvECtLAJ7p2krJqjysQwV6UbQzCVwwnwKugQPg1oh'
        b'1woVoA1dh8NwM5n6MAIMzfkHSZ2Iw9OS03Cp2WAnJW/DkmKsJR0AVsQEvADCJKZOI2GEQJgEOxr+NgI3yr6A2ciDnmmeDVpvjtD6ZjtnF9IdDXYViCJhCBCmA7bQQDK4'
        b'zUXWzArUGZhTUzyYXlmST7WYGFEYDMWEp4vCxWzJYw6zwA40G4IO60CGkAYDu+cTyYvXBj1cURQM3AL2C3EwaFLYTLpQIOiOl+VQ5fAgzYMBdaak6nTN0Vp5igWjZz5N'
        b'g7FfRKpdHQ2HOzAMBu4PsWYKYTBg39wfMPo8DQ4uJTSYuWgi4DD0IkvpeqiBO8NeoGD8daZhMDVi80A1anOcoVBjI5oDI65NYQwMPO1Hd4FTYCROhAODRhJtsAcNnhtB'
        b'PT3jHXITfwGCAReZsjloGb6A1JKBlt0UBsYbtTOhwIQbkBZUhB3RqN+I8F/gOW0aAQMqhNg1zxI7GgHjDPdPI2AMgkm+5i/LnUGAAcdhJxprhlmuFin0rFMP9urTBBit'
        b'mCkvwIkFNPdmHxoBqwkBBl6kmJgAcw7JA5HdvWAbuPSC9IJGJn9nsAl2JHPU/sNgF5zTl4+Lf2PhqfbyWbwIz0VPhn4bE+X+r/FctMc03H6DbqkRfyBBsQ3+jSwWC56G'
        b'BV/D6q+wWF4d+OcwLCqHFf59GBZhIkKL76bwtqjmqHaTlgRUYhyG6qCdQYyOyRuhTkW+josQ69Dk2xbWHMbXcfxrJJQXdA2FBoWm1W3lzeUCUw+eqccVGb5pEF8jGOfo'
        b'v1iT/99jTRRwTrG4q/E1zLBMyDfIixRfCOsQsYqP6k7oSBBYzedZzeebLcCh0h3SGFPg1+HX49sZhqqHYz4pLm5sMsmatnxnyWpqTYYzHDH4xJGAT/L+VfBJfnP+XwGf'
        b'TIqzUKtJ/ct8kMCGwKZC/HJXYOrJM/W8Unit5GqJwC+O5xdXH8jXWSrszTgy+WZ5XHf+zf4oK/Ed8QKrhTyrhQIrH56VD9/IF18Lag7qYQ7K9soKbBfxbBcJbAN5toEC'
        b'20iebeRoVCLfdjnfKGnqPkm+kcukpDiuUtQfHyhRuvp/hi+iq98Y3xDfuLxh+Ziuc8+iHslHlDgqcvhI3HCcsKYmLKww86Lb45QHkjRTq+MFPeJjxpFDdiPOw85X7K+5'
        b'XXW75nHVg+8WOWa8YjR2iSA2gRebMLpsuWBZFm9ZlmBZHm9Z3nuxK8YXel6TuCpxZdW1oqtF10P4fkv5C+NRxeMsiy/AYJn/gkj+CyL5n4JI4hjzMIdk3hSGZA0DY0g2'
        b'sP5vw5D8f5s+Usyi6SMRL+gjt2y1ue7WXxhpFzGs/630kdesTSskRdAjIe7/AnrkMUaPYL4qQY+wMHrkATYWUflPcEO4+KDoVcgQugYmcQ28TDn4FFNXQl+BC7F8BS7E'
        b'8hW4kJfDMugwq3Fdn2k0iP+M+KxeF4YpILaYAhLO4BAKSAxNAWHJGwgpIOjbIxlC72hfcHXOaxggxiIMEPz9Yeg0A8QFM0Dm/XUECE4ggjHhEzDu5vGE5SGP9ZzwJ04m'
        b'AiWDvz/xYuYxMf0Df9L0D7z5Tl1Owz9gpWVgiPWqgBC405JBmYGRpcriKwph5wx1GwXh38lnmPuh+jL1Y6nYNDUD8y+UCRlDWkjMUJgRqjLjl8yLX9msDFYXa4rDkWZM'
        b'rIGwLRC2DZKrkK9QqFCqmF2hkiGXJibCzxBnUukSaeJbqTSJLslpiockCZVCodIioVIkVAaFyoqESpNQORQqLxIqQ0IVUKiiSKgsCVVCobNEQuVI6GwUqiwSKk9CVVCo'
        b'qkioAglVQ6HqIqGKJFQDhWqKhCqRUC0Uqi0SOouE6qBQXZHQ2SRUD4Xqi4Qqk1A2CjUQCVWpEM9gpBlulVqqSr7NQd/UKihU4yxU3xIVUhWyqL4VUX3PIvVthK6rlzCl'
        b't3JMPpRb5BkS5S1U3fr0HPMlSypsyiB6B40jmVbELyrAnuG59D1O9pb0XwfiRx1/c5wR2ZSGGNea7SliIyQ0eSHWzkLDGnS1KL2QuHkvWJ1eiH7NtPERdfluyU5PTs1i'
        b'F6avLEznpueLRCFihIRt3mbE8Dot/5l6ajN+hBZg446ADFQ6ogS3Jr0wnc0tTlmRTcwVsvNFjMiJ/QS6nIz+X5RVmD4z8RXpRVkFacSuFuW5IG91OtGoK8ZzRF4JtsOY'
        b'4dOe7ZNNTBrMPDlCS768mYYe2B5CaCpEN4SNsB2matySbebFmbotmc1NxyYrRem/10i4Dc0WcbDlebKIWZDQIKegMDszOz85D5tAC4FQqAqwefdLBeVykzOJ8Xs6xgjk'
        b'Yes4uvTstPSVaFLksgvojBPbHjPhNS8sYSsKuDNNPFILVqzAFotE9l6yIwrlMD9krV2R96FEavKKIifHVNZLwx3RLlyPPmrlaHPFgxTpHJJoQGISc0V6UFJEHUepgpGh'
        b'QJQqWUyqctr0sEyMKFWyRJQqxUTUJ1kbxIRKlS+FzjBWxCPuHyIxZnS519udvM4UCdUDbYW0JCRYaEaDO0EyifdFC6O2JKZmqAO/2j7NLJ0WvNf17t9BNZBGmIct7lOT'
        b'0fiQhLKURJsD0ZFNRyIqpMn5r7bkS0vLpo3HhOnOEFIszquK04UdnVuMeuD0QPNqE/UZJnZrsrLRE7ifJhcXFaxILspOJWK9Ir0wU2hq9DvG7oWo/64syE/DNUz3/hk9'
        b'9/eVXiWpl5Ve9UK5+PVGnlRMP++JBedUEecG51bLuSrOB32buFR2mVQr5yE95WMFk0WqiqAf7oWD2GVyEQdWcsD2CHAOVHFgHegD9BOg1Xsu8ZgeRWs5blsaAjrBSdAj'
        b'TlEbqA1gN2ggWpFLfFiEJcReUBrcvNiXKsYH63CHN4qoP94WzQtulBs8HZb30/PnzyUCsTkKxbYNzbCszHGmFV7jDfSIK0p4wMGWyYmnxF0ZizNzOcxivExl2oNBLtyp'
        b'ACvX0PowYBs4EhxqLW1uxqDs4QEJi4A8On8DGqBGFoVaalHMEIYzaIOtKA6ie9ES7DkdR4EBikUGR8WgDOeJG8J2eJRWpOxYESxrjYpVT66x4HmstNJggSKxRJflYKX8'
        b'jIwEmK+Ch8HhUA7stQgIssaqOTGwXkrHAR4n8dnaysL+qStSTqAJnmDmg8vLOaxiorNwEIwoBIXCXVZwr4Ot03zYxqTkypi5NkZEc3M26GK8uAp3FElQchuYefA4rKV9'
        b'Og6AY7DnxR3O2NuRXDlzBegFNcUWOIFt8HAprIJVoBtWY9sif3xzuL+oZyZvRUl1uHVhMf3yB55PpV96hFvBc3BXEOiMYVHKoJoFGmEb6C3GZvpSRdqiatVmRENqMYpU'
        b'FVYFBwVZMVfNB0d14CWwUxX2wb4gFbAzSFYG9oGqwIhIKj1DyRlshjuJ4OQvo4UhST5VTlU5jSpegsvVvzblFQlg6y6bwGgzWOkPd0Vio6qgaNgzLb5EozssQHy2sQzc'
        b'BlrFM+3E4bCPMejgUD5rVOBRYw6qdSwlfn5GsF/RTXJlIYNiwiGGCahWJAJrmlEuK7XEo3A1ankxhjk4tIFo6maVwWrYL+ebvYo80MUwYsPTRGoj/cE27krQArcSFQSW'
        b'HCNpAzhPq3z3gNMRXCQd8ATsk8PPbWQYuXggQSINPwAvwiouPAeawFkSLbjIUAMjoIvE6+kB61CKDNg+nSRsTSN61NhaCB5/0eZa8Cjd5nCnfLELjvoA3AuO4htwu9uE'
        b'w4oQq7icwLBo/+lnhBWK3XNQsDFPFrSD4SzS/jaz4VmRR88Z4KfRsxQ1p1QMHiifTaTaGx4xjhQ2ChqIpBfBwwx4ycIj+1lcD5NriiZPCbGMm7E38/kLlT4uvueSf+9s'
        b'/oZDYgpWfwtjN8s0qzG8dMwVdMzDVy1sX+x9UO2cmVdIe+BZNVXn2EuGCttMr7NWLroo3331jbRrZ1YnrKgy36uTEpZx+WnGF3d/fBb0dwvukoTddx++dyX5RuYFtdv+'
        b't3btmQCVd7eATy78srrt0GexSvkfKD4w/eycBv+nWZGW+WeST6SMOYWf8GOrS7aYfTrwaH3gV58plrGVj18LiTO0rw25S82p9pY8+eXHCQr3ja6uSODKbr/uc/agD9vE'
        b'++/xBn/b+Y5t4+3ZpZfBuHmRfeHxzeZGsfmOH3TmhL15oNPto79L3tRZXcw/qXPzzNcc03jX3Xq6A22TVoUfSCd8cPjqMxOnR5kK/PxDw3PCSvpCHrgXfLhR83GMql9g'
        b'/UD1m9+lfONzYXzZxyseOt7vK37r0OXttaMb53Xf8bl/jOHFci19tN3p7rq3Y4I7ehd8dbr29uy2zaofG9nfnH0u/oNdak9v8NQtf/nq1Oi6vI/dtn6rl3yh4KDgeMTd'
        b'XYrf2Hu1cp89G78YtPXb5mKFBM61L9am7d6R67925Rpjnx1l35l+I2Mc3fd+wOcWz8UCj2x7+tPzk1Yld8/mW4HJ/nulXd/71N95Glj45q6NgTbUP1eNa+fkJCywm/+g'
        b'ZO6lgQPf/OO03AanN9ds4lsffMfEa3NIhoD3i/RbHxwtYkqOJNQz3/18nUTLpsjyHMMbmVt3fxW/ToEquveO71cbrJ9VRTbdzrV4tCHdd+Hz8kXP3zllKb43dUvPpd7P'
        b'I+5qhubq5RymirLVfUp3PqspP3lu267ya/vCUr82b+8/1v657sORTxpDozaONz2MXmjP775wJLjT8hPlksFvh3bFsHd73umqFcvcs++dN/bq/bjgK4ukRL+js3JGv/Z8'
        b'fqx5XsatxbprHH5tC7+m8HAkRjJly7zEQxuet85baXq9nfX1WreLMLNAJ//5xrefeav97V3LQ0s5PV/7Za1ovVD4aLXqW/yf0Efzz2mG/1D+dcN4x66U+6ty4dX+9QYK'
        b'zk8XeG8xEXjuZ6yNjmpy8NkkE3rrfCkHng8RlP0f4r4DLqpr3XdPo1dBAemdYZgZYOi99yYgqIigAkpQFIci9lhBUBEbCMpgHbAwiApYca0kYpps0MxgTKIpJ7knOTka'
        b'k5iet9bag2KS+9713HPfNfkNu6zy7bW+1f/f/xt+PXD6z03rayS3+6mPa1LFdR9IzsCttleqx+N/+KltPWXbb/LttgX8SAKbWbsWbhWIUtleRtgjCSsZ7oCnyRm0P9gP'
        b'BgDuvOuwCW863M5GI+oApQuuoE4BtkUzx7KDsAd0CBJTNLVhN0qhjhUK5IwXrer06c9c9GEAKmipFc41Y9BYus6gQUys7yiNQjZsBnsc+FrkVcBy2Ix6gHpxOmajWcde'
        b'DXe5syK+FaFXDjxrFAujJ1NEoD6dQDDhCTQe14kTPNwxs06yJlWAJg5n4CZ4jIAxguEm00lI2jUrKYKknR9FzptXRIPz+DQa7hBqUBrz2PDifEcP0E+O7UvgXp3kdGGi'
        b'B5/PTlqBvvo8G15xhGcYw8mdcPu0yQBeIF/HeExMA9cIHsMEXgY7JltWwt5X1Nw2sDeHAYrsBq25k4/hHeFRdkIxaCOyaeqiCcSEPxZ8Cr/NB+4L9WfO77cagQFBohAO'
        b'gjNoFsJdxIJb4dZqckjvBLvDMHyEHNPPTptw1DIdtnMrDJBw5Jz9ItjKh30p8Mi6CW9gqCCuMnCmS8t1UCknpSYLkzB6dEdymjoJJ7iPFwyuRBHt8KPAASnckShCs7YB'
        b'VCPJBmlC1H2zKZs4LjieAusYrM1x7MWxLxHu0iavLarZlH4sGylNcybJLRDUw50ouzRhxAKP1EmZ2Xlx4XFUkQzwDxXwGXiQARbAeh4njMEVwO5E8lozHJwGDemipFSP'
        b'xFSUeC+LMljMCQDbswlkqAo26DHzCgKjANfiOBgbqFkC28n7ErhBTBA3jcmwQZPS0GaDk6BFDxyBzUQl14PzYKc0BeyowO6QOGWsNWgeOsiU5Dm4SQv2VRZSK55BByPh'
        b'BaaWGsvQJLdPHJGMfYGp0XCaixnIwlZwFU0UMJ4LO1ejePAga9oceGlWEQP3asI4Vl0RPMFJJpiRbhaaAm1IIEUf7wbP/xEf6A2OT3hHW6XLJHEQTR4HCFAP1gsoBqgH'
        b'TzsQ0RJSIp65NuMas0Br7Dw0K9rLYOGOQ0UwKk3vGAIM5KDxFezMgwwCjwcH0LS9TyyxgbsEWLA+FlLTllzGE48CdAkwIrQmQu0n0COdaDoP7subQKzz0N0lth/YwoIH'
        b'uATGwrVIJShKeGEqhVGUuqCdAQydnA234WolMMow2Edso6eAsxw0pew2Y7DsXfBqPLGNVsPTwMFMNM0F9WAQbiduvFLhKXiZAex3F73oJZUB7Ctg04Rnv/6laMKcCQ/y'
        b'GVzqBRY4C2WAURJwNSgOvX22XtkH6zQogyJOrGH8t0JcbFuTYQdoqKmG5/Urns8fTVdiviwx3JmQKuRrUFmxWqgR2jAFjebym6QCHTSh57MozbVicIztMwt2EZ3LXRgv'
        b'Fawg2k5pFruCHrY3PEuRcomwhqhfxvhmsCNdgFHqoBNs4FFTYTfX2IlxrQjlvnCzLk6ZSQF0x9uxQ+FVeI7pv65MRTNkdRpiWF8G9mtSBmmcCIxZJnWZXT1VijSTZQlO'
        b'UyzYzzJKgD2MT61uczigy+dgkgMGBtUOtjFeMrvAJnhxAgmFlKH+uWcs2Kg2u54HtkA5qu7rS5852WyD/YxnuctzlxJnblBhQ7GxM7fePMak+gzYC7AmIIEScSM9upZ0'
        b'E+IEuINDOcITPH9wtZaxrJCXviJN4xODhVSkyY3JLMrImjMjC/V8JI9zYLe3lD9Vf8KBJmhOZhpr37JSKR9clZLy4iD1XAVbAIMvgtvgQdApSBImC93TUmPMWJThIs58'
        b'uBk1GCKeHHQYIemmJqjlY3BraAhL41H8eTzQBlrh5W/dUVCrlai0XtAR1A1jNcFKku7ny6KCwVmNNHCpggg1H1yMEoAuf9SQnqHxBfASo/l7YyqwhUECVudNaKqPVdoY'
        b'XuKAM0vLSOfrj+b3JwVkCELDmxa8jEbtA2ywG3aCOsafbF88BjdPAnSBa/Cc2qkXUNjzLf//oqf+82MbQhU3+d9fnd4QVrSpkzegXiR5a+cx0KpXolBXadOyUOZ7x4Sv'
        b'mm7V4dLqMmIfOiAdih6bnrA7+sHEo5CBBUOOY9PjmqLHp1m0OLZU7ilv4qhsHZq4e/VU1nYdua25Hfmt+XLJmLVYwaKtvZXWAbR1wIDJmHXowALaOhIF1MEOaea0zmHQ'
        b'TSggeWZipjQR0ibCERNflV8QRlco/RJpv8Rh/phf9oh3dlPMHVPRA7tglV2gyi76sSbXYkoT75EO5eB60rLT8oT17sSm6BZTlYPL7mR0Me2+mU2LVBZ918xNZeuIkRtK'
        b'Wx/a1keRdcc2UMX3aIlpT7pv4yxbiCS1Ebdw7tu7yU3kJWP2vi0a4+bWjwwpB/G3UyhL5xHnoLHpwSOmwSoLq47prdObNNRgLaWjD+3o08S9Y2SnchbIIztnn5zbOVfp'
        b'7Ec7++GnDiond7lXZ6LSKYh2ClI6hdNO4aNOc4b8hu1vBCqjZ9LRM5XRc+joOTiw/bidUF7SU95VrhRFYoiWXRRh1LN2xIgIpbUXbe01aj1HkTMQ2Tt7YM1wCR2eTfvO'
        b'VPrOoX3nMEXqKItsnd0xr3UecwastJbQ1hKm9FHMgbghr8HE62mDacqQVDokVRmSSYdkKkNm0iEzlSFz6BAmFSsHmVdrYkdaa5rSSkxbiZVWQbRVkNIqjLYKU1pF01bR'
        b'o1bLh6qH59+ovbnuxjpl/Bw6fo4yvpiOL1bGl9HxZcr45XT8cpSW9gsSedLWnpMlwpk9sHeVszotTtp02ijtJbS9RGkfQNvjVwYqG1v0R/d9a8emWJWlXUdQa1BHaGto'
        b'Uww+1tZu1cZgsVHzYLlTD7+L3+PR5aF0D6bdg4e4N3Vu6IyaJRGWglljNrNHzGer7F1OTj82vYU3bmnTUtWxrnXdmKVIYTxm6X3fQTQiXjzmUDpiVfqIRzl4PNKgploc'
        b'SG5O7pTIqk6u6lx1NJw29d6fjLTBxumREWXviitl3EGs0FBU9Gozh9lKz3jaM17pmUJ7pgwXjTlkoTCGpDoVmV2vKEXhtChcKYqjRXFKUTItSh7OHrPLxOk8sLSX2bcG'
        b'doS2hzZF49Pt6t3VDIWD0sydNnNXmolpM/GIJHHULHFcKFFEY1BVf0pvypDjTdcbrsMuN8RjwswW7h1zd5WlDS4fpaWQthRiBgZ/lZWd0ko0aiVSONBWPnetRLgVrD+4'
        b'flwUPBB9PW4w7nryYDKDzRoNmTeSkcVgIZQZs+mM2cqMeXTGvJHCojFRMWoo6UyDsOI/mkK5i3A7dPnU0rEzRj5Nwe6a3mPTZTPmFPCeZeD/5SsU4aNmUeMi1Pz6c3tz'
        b'MVpgSHLT/4b/sN+N8DFRFv4IwX/yEeJRK7HCm7byvWslxh+x9uDacY/AAcfrLoMuGE6iDEqig5JGg+YOL7xdcqvkdumt0tvlt8pH5i0Y81iIpE9VSx+EpBeIsfSuKmus'
        b'XjrjJhZqLnClmYA2E8iT7pj537dxHXFLHbNJGzFPGzezl7nIne6YiVX2rietO62P2rZqjFu7yjUUpopihd4d61CVg5vMvEXjfVvnFs64jbu6N0EdYsfK1pVKW2/a1lsR'
        b'dMc27AMHwbDpbYu3LEayc5XZc0ez54545I85zBuxmqfyDWjhEmin5GRYZ9ioufdjbcrOBclsOn0SJYYxA2ZowwTz7dz/Oqzh/zGM4GHiOTvGf3XwSNRCUTGjw88bqKfp'
        b'USwWy/YphX4wAsL2JRAQUrzn2KEhpnp0gzj/M9SaL37ABK/mGZTxJF5Nr4mjUXK26GFXvEhk546PPUSevpIJGuI/02z+6xIfY7+sxAos8Qn2hMSWWGL1iZxdadELsv1L'
        b'Yi1CYnWx7mkVLGSObl9Ouj4sXe+z8rQnrHmEKq7EjiSIuR//2zKWIBn5rHv6Bc+OMAtKX1LQi1hQ7rNidIm0qyovragq/gsyyX9HiSJp9QomjrReWthBLKzBM2HdcalK'
        b'K1GxkuOyZydl/y6BcfGu0H5pzbzyYlsSZS3DdN7lJcsIyafd/AXLqipfYAf/70u6GUvaSb2spNdflNQy+0Ve6/+2WKRpy19aLIDF6n4m1vTnYkUlRv+bpDrz0lK9/kJh'
        b'reih/sX+DjeDFfasl81+GGfvwJooFLfsv+BCnyDI/Xd1LDqE87MAM3C+nLBv4fEQj2UbqJbsjoKDBZMUjBB7Mp3hv0tOLUbOymUvJ+W7L3bSFmq62H+vbPoFC+YvwQiH'
        b'gmXLi8tfTkD6xc45AAuIU2EO5JdMxv/8kYn439ZdGzyTf+GSZdLil/uAO/gD3qVe+ACczH/rA/4XnQI9K7tnoAZOWumnbl+yyfbDz1XbLdqwgx/GvQ9XsvwEiwoeY39y'
        b'n8VnMXtPskCoYPYiwVnPie1INqgv0v4Lrz6OmJXN9A8TziXF5erNChwGe/RZEseizK0OrN69esTI4SV9+PznWShxE/alGP89ZXGsf8GBz/9SrW3+Y61Rf6o1blp2ae7x'
        b'czziH3Bq1Xek0pp3S/Tz7lE6MrYZ63umCP9cJ9Wsv1gELFi2bIm6UnTUlbKCVMpL1sb/JfF7k6uj4r9fHRg1hjXyySpqAjWGKoSrRo1p1bHUNPcMboyqM1Rjxtioqp4R'
        b'2q/laL9QEZPxY6hS2Os46qr6w9PJmLEXqwoD1yUvVJVtGoEcxKbnSivgOT3YiLcfCVrBFu4lgJ27EQxG40H6Wr2srFcYwA64BnbDVqnBCm2PXBz+CEsEt2cTTMfrNkz4'
        b'jCXLUvjL3akqT4pYz1+Bm8lxCcMgisl6G5PRRRqm8M3MyBTm5IMdbGpehCbo9HEj3HuwHrT5JydhPALYyZyH4fMpGx6Pcl/IA6fg2UKC0IBHrZZLl6eBs/DyGgaGAa85'
        b'EwgN7JgNd6IMM8C1F8zn97muYQA/J3L5+BwHUyvDo5oUV8gCZ2BfMEN4fGq6n4DvngraQKeaOU9PWIVPU1LBhTXqzWgk3PVqsh1dDPfHZpPXsBEcqBYkW82AjXxhIpfS'
        b'1mSDnfg0krwFV0A72IjZXOEpuBElzGWBDiRfFwGOCN3dBSJUutsSPfhCDUo7kA2Oz4NXybvVPuAwZtRJhc3g0ASlTu8shgD4hBhzjAjTppiQ0zuNfPbUVEvi2zEIFfXF'
        b'ZLgzEfs+SYENpMgx36HDWg4lCOXBHaAP7HlBfXUn1LcSq6/OC+r7ovJOeGb49yru4j8qru6fFFeYRrQzJYfLwMniZMkBmkVq7ezRK8PG5PAEODbBIaMtYl6dYRViM3rY'
        b'MHXCxB4cdyHFW6IvclvwrFqZOjUCxxhdaAQtodKUNBHGzTAnkHGGTIKXwCB4VZoiRs1AC7SCEyxrcK2QqZNjugUMtwd7HugHV1hi1Ay6iOLpwWZ4hKHrXgo6J1hNYtIZ'
        b'rbyWAC4StppUc7hXTVbjCQ8SBFAZ7Jg6QVaDD3fgTtiE2WqQBm0iWD3CE4gUZW95mVUWurSn7EWFfB4DH9oNurG2P4+uAXfh2OHwOMnaGmwAVzBxDOiawlbzxsCN8FoV'
        b'PlHPgZ1wN1CAa5M4axi+GqRNJ6rUFEWvFj8nw4HyajZoAW3wALEzAGfAeRMBylqEmpWIL0xKZVEOmFIT1PMCU8AhIiPsgU1wE0NBI9LApvQyQkEDLqBmgGUMcYYbgMxZ'
        b'TWSAVF2LbQavwH1VmNZ4HeoFdgleJGwAiuhJZAhV6FMJAfKAMdhLODNSyMEz7odiQT3YTtqPSy6vzAgcrcJ8EKHwKBKpAdNBgA3sv2aEQKmngVc1seiookjtnwP7wDWm'
        b'XzrpzPRLAZakIKF8PTjzIqUHvIQptvah6pET0CPsB01mf+774JEUdecHmsqI1kaBAXt1F7YE7lR3YfFajAjnbeF2FDPVELyqJh3RhQpGbY/xFxPO5mzQqGbYgDtWMB1U'
        b'B+ieXozuUW/yrC+B+0APaQllU1aTPghs11N3QbBjHQHWGbNR2TWg8KwAS9CBFfOaPwOG26ELNwtShXx4AexmU9z5qCflIpUgmW0uJ+RLCUIPQtO2X4/FXoNK7AQD27wG'
        b'L5qqeV9e4KLwAFd42qAnrIo5pDvvNxEItRYNTA0DWkyqMDcK2KUJB/+q8wPb4KC6+9MGXXw2I+nBynLQAM9VcykWlDtAOYX0rnsaeQcH4XV4TAp7NTAJSU0ZBZrQGHiV'
        b'ofk8DC6AHnjZCe5Bbz0oD7BlORkMf6jVpVAALc+cMI3U0BSGl/QDLwYu66lx3IVjJmAevq6v7siq+7wXLJAwD1MK9TCtqZunhrn0QH4N8zBsoTZlhMGlLrvKq9cLXpx4'
        b'cCY6SnzYmYz6VbwEyUfTprWsNayVLCmbRRVR+1kHWCyqUY+LOtIzHDITR4tmMo9i32OLPO+xqqV4umXHLEHuaYcsKi4vXrl8RdiqkD9u0FYWrygoQCsSvIEgDRORe4Jm'
        b'fv7sWexibTTLwue5X+BJ3EhMIT2rYCQre2gGmD3sBGejux/JlG2j0RQW47fralURBiOiBrpHKEokfDFJMzKEOQnqGi1c8kKd9rF1WBQ8BLv1CgVgK5lE5MDj81Cnzoet'
        b'sFsIt09CmVjN5ILTYCc4Unrijd08aTUqug3c7+7m5pWZRJoeHv/g/pjPO2dSD76hKlty3NTYWPt4UsYM490Oc05vt84K2h22ZCi5tfaJs9Ex8b3wB3nfhq8qkbSNfp3Y'
        b'cv5ay7avvn776drPgxfdftspfMoubWfXY1lLmz754msH++bKpPbmoZMne5qr3RsvvrJ5wL4ksWF8NKzywfsbXfOMynmDo8Z7A2MHylxZD7nG5ckBYEGn40BugI3BgpWm'
        b'Fg2aN6+NfK/hrLEqsUgP2nsVJWwOkoZMbX/s/olWXoTvMd74iU3my6f1UzYBb9kZS0tElSfMGmZ4NrCWiTJzlb///dcNX8r/eW+sI3Kl88Lrsau6i4bZmr0SgzcjG/Ua'
        b'PHvMv3x934dhu40LZ26q0xjnbWjc/kWTh0fSrI1i7ue/XPjgxAe1xg+TEyqz+04+1U661GbQm3BSNrd7yY2H5+bPmz9PEn3OqSD6R+U7P6zjbegNszla+mPrzu7DcSbG'
        b'P4bSuqU1e4//lD/kssX3i+/fqlrYelgp+eetb1sPv5YzpuFdPbgvwFe+4dddgsICGdvitv5Df6M3Uou+mvZ3u//4x+Xh9sb6ljwTL49LeVt9vXfcrjd/qztl1U+/fJW9'
        b'M+rwR+3fr7asn2pWsU7zcWOuMGbfvA/zOpbfvfSd14+8d8Qrfwn4yOcTzsI5kouNFpKDFctSdsX+o1f+4w6vH53fEZf+tnbhzb6Dj0daZrzXGP9GY+Cvfzts13iyxL2p'
        b'dJ/B2MqSr44dORRi+O6br12LmvvYSPvajsXXIt6Yd/D1/Ym7Kz/fd63/p14TQeArPWGhg1tXvq+988aPOp9vbTe3qGJLy/527PJDN/+ebXFpOxrbL80tUrWe/eGn395+'
        b'8Kvxbxp03E8xadtvea1SXL/XverCzC9/6j68q+tnnfMftpb2nuowXfjWoiehXMk/P3cea/rH6YSfby/p5F0+G+w6Oqt49sfnM912Vb96a9rVAduNa65/+LWBbH/Ind+0'
        b'7nBsPyv7evbfz35oOztTKRXtv/q7VdmD3woHzrZ7f/Tl+/Zen/3z0auNM08//ZW+dl0qfX/TnMY3v/laNu2o+0UD+dQtC7SPf/DuT7cdZ8+++9bp7/X/fler8vJHi7ad'
        b'OuS9jDdT5fvk7JPLZxY97bhqPfXHGoHEAYY7HPzkH+8NbH1YLuwbCvd57W8xF5fWt1saz95dNqfp8+6vt7Sm9SYa2j0p+DZ4X21kzG//eHCgfvj3Y657mz9ZXPO6fcEt'
        b'258lO3x/Z39l6rvfbgE/kGAtfMBmeBTPTYAcNntzyeBypSaZgPmkQBGqizmpwI6V2m5o2YDmxsbgJAe0wwOgl2BEjEAduKbrjum7CPOQJXwVXmbn2MJ+Bie2wxeNsX0p'
        b'BG4HBvUw4m4z2MwQK7ayUffQV7kCngf7PNQgMrgDtjAAy+O1ToJEcMYtJXQC6dcPLzIbDltRx7OJEK65of7/5ATGDFxZzUDAGuHmeGaaBzfOmpjmCXkTJEEHYBc4Vkg+'
        b'rCJFzNeg9GEjx8UENBHgFNgE6oqe48yAHDSpuejUQDMpHCSIIPv18xk+OJR1FdhMwV3xsJl8dawrmki0vwA1mwe6DZnvOoxmtc26mAeIYmebwmOsMHDKiLxaW15GeAUp'
        b'li68Cjswz+JB0KBmQ2wGbWo6RD6bigCH1XSIDWySo7kdOCAVobklaK2aoBYE++YQxMy6VDSATrAHJvPQ4AyOEv5AVBc7yZcsErLdQTsmYdvuQVEa4DRbIskj6Vqu0JrM'
        b'VQoPzWLXitRVbwP6l8HuvGd0iGouxCWQAXJWwkNUNdINwqSo5lE0B90M5qx5PlK7BsI02uiMFkTcQBbohcfBFvI6ApyAdZMJHBfAU+xSoICnGWYpsFFHCrcnJsL+ZDal'
        b'WQEPrWC7w24WA2i6GgyvTuLKq7Bjz0kDmxgsW50AbMJQqwoMZdOgwAYbnVw2Wkv0mTNidZimwDOrdEHXcozHQkIfZMEetNI4Q+qnEDSAEwSpRbFN4akcliNaMOwgJZjp'
        b'xtdNShWAk9UaaH1ziQV2h8M6BnJ2GHZb4TVMcIa2KFmkg0mvzMEFrj84BLczpFfHwavgspr1ytTjGY+eKZrjwz2u4ABBjErAebh5gu1uOlofMIR3arY7cARVJfnEK0gH'
        b'NrzIE5esz47MgFcZTNfemaAZjdWnXsDY7gNHtQnGLhUtNfrRynXfCzSzaorZsiSmBR1BM/Ptz2j70OvcmQxr3/xCpgq2o05gg26VvjbYAzpQ67RnRYINSaQMbZBuOhhj'
        b'PkSCmuXFstAEOI5pGce083Ux/2ngBLsZWnGcZlj8+uIiiS06PA1PsCggX2tOchKAcxawK0RNYMjQF+6CjI7pgi2RL3CiLYK97BlI7VpJbilwvzFSsSRwMGOCFQ0cYvyg'
        b'BEA53MnQogU6qonR1KRoZWGEvizGvoqwl7H5blDBsuGijgnXURaquZ24InPhCYbB7A/8ZRsYzy0HfWGPSSHDYUYYzMBWDpG5Cg6CbmzshDQQfa5mMjxVybZHa7AB8rnS'
        b'OaATM6qJXgGtE4xqs5AG4t50GnZeCg77vwA9FxqD/aReYRvYORs2eKShThzu8sBkkeBVXUw+fBYpz3amXtty0IfjMI18WJfApaZE64KzbHi0CqjlvuoLySqUQn11Z7If'
        b'KyMQ9ZlkaXVlKtwtSPdAatFA0Ogrse+Fa2zUDW4Dhxj8ZBtoKtJ1hztRqaXWouW8TwF6Y0V07jrS2ZN4Of8Mq8wAlQUcBq9Xjwaciy9C8qm14BCDyA8z4dv/70P1/isw'
        b'DHvqzyRpf4L1MXN/necz+lX8//Lkn2zW5qMVxQ9kqv9tTAKL8vCVaaqcPTBu7eg8GVvl6Cr3PhKkEkpkcSoP787YB+orWazK3YuBWMk0Hzg6y145EqbI7Z93bp5K4K3w'
        b'G4jrDacF0UpBHC2IUwqSaUGyUpBBCzJGBWtGsvNG5i4YKS6j55bR2UuU2cvo7GXK7Eo6u1KZXUNn1yiz19DZa2QxKleBvLKntqt21DVAFRA6UK3gyTVUHhKlRwjtETKQ'
        b'M1Q8OI/2SFF65NIeuUqPPNojT+lRSHsUfkNRwjz2SFGZsqiSLqocqVr9iKLWs2LYjymqmvlTzIplP8V/Mpi7DOYuh7nLYe7ymLs8towt8+3UVgl9FDkDJb0FtDBWKUyg'
        b'hQlKYSotTFUKM2lh5qhw3UhO/si8opFFS+l5S+mccmVOBZ1TocyppnOqlTm1dE6tMmcdnbMOpebXqUNS6yqYoFaKpoXRTKKjwoXD8SPZc26lK1Pm0SnzlCkL6ZSF6kju'
        b'XgqXLrHSPZJ2j0Q15enPUKhE0p6RKERgp77K3QM995D0pJ9OR0Xo5oFJrroNFZlK1zDaNeyua4TKTdxj0GWgqOyv7a296xb5iEcJQx5rUF4BKg+RvLYrVcX37LHuslby'
        b'g2l+MBKzJ78rXykMp4XhKoGoJ6ArQJ2C0i2YdgsedYscWPHnJ494HF+XJxTHw/WpBuUm7Kw6WvONJsfD/5EGJfF/pEd5B35raeDlwAj9yIbyDxtYNKxBh6XRfulKvyza'
        b'L0vpl0P75Sj98mi/PFSj/pHskYKSkUXlIxU19KIaumClsmA1XbAa1VQhKxLXFP6D0gun7SQqv1BUUcuUfgm0X4LSL50kmk37ZSv9cmm/XKXfXNpv7kTYEOyFqPhGOh2S'
        b'rQyZRYfMUobk0SF5ypBCOgTrUmgs1qWRJdKR6tX0ktV00Rpl0Xq6aP1TRo3U2iRjjzgG0HaBD1Dp2XbZKvlhND9MyY+i+VGj/BlDi26W3SiTaYw78uUlPWXdZeOSwAEC'
        b'VhuqHi65sW5MkjMyO5+W5MuiZCs7Ux64ijBzm4yr8g9mqJyU/im0f8qof9FIRuZI1kI6owhnKKHtfFANMbWjFMbQwphRYeYwe9jvls6Emnn1FGA1i6SFkc8fEVIvzISm'
        b'fiTy7nml65WeZV3LRkUpQ1OG4m9Yojf+nbo48LP6HxWmDnkPldwIUseaYHoLoQUh6JFPpxYOPrtrds+8rnnqMGJJz6quVT3ru9ajBwGdeg98QzDYr7+gt0Dpm0j7Jo76'
        b'Fg3nMnR6BXRqgTK1iE5FHycLo+28sSradNnINFSe3oyqoA6IEZ5pMPG0MF4pTKGFKTKdcUehyslFVtuZqnQKoJ0CBqYrAxPpwMSxwOQ7TikqsS9DqhV3Rxwni38xpNl1'
        b'q0ErZWAyHZg8Fph61yntEYfyjMd+rEU+PXNPz0Xd3Qvhp2LatWep33VKQeFFQQ89fRULBix6l455xqilZeRX8kNpfij6Cv9Q3Oj61/WuG/XPH54ykjKXTsx/VpGOziMu'
        b'fmOO/gOToJgjGfmjIfmPjCix14hXJC2KUooSaFHCsMmYKFUW/9BdKF90ymPAeNQ9aKJdr7jjFvSYQwlEzJsx9yCkTfKKzlVK10DaNfCOa/CQ5jDrho4yIpOOyLwTkY2+'
        b'MoqVyBo2vjF9OHdkZs6tOSNuYXJNBatLRxE/ENmbNI7SqjkVMuA1KghRSYL6g3uD+0LlMehSKYmlJbFKSdKoJEkVGqlgK/x6dR66usv9j65RVKB+ezBryAwnfLlgJGPG'
        b'aOgM1GMNsHp1lJ5RtGfUHc+YYbORGZm3pisT8+jEvDuJ+SqvgAHj3ukDK0a9Iodyh2fcmKOMzaVjc+/Ezh4Pj6HJbtRYTOFYeKGcPSJAXU3IAzcR/uwR/zxcus+pz9SF'
        b'+y2HxS/AFSnw7hF1iVDf6O7VI+gS4BuleyjtHjrqnjtkdtPyhqUyMpOOzFRG5tKRuSSc0j2Idg9SuofT7uEyzXFH965FqsCIIdeRgCTUTNfSTr4P3fxHAhJot/ThKPQj'
        b'4z3w9JfxjumrXATHdB8XcNBw+iMhU9qUwCsUs4a1M6ejP/ec4nTRH7Vbs3valSuLiivnly6R3tMsqFy5YL60+L8D5FQ7OJs8S2BOVpN4FPUSswMO3gcMQhF/2kA9jU5g'
        b'sVh22NWZ3UscuT7BO6FtGgLqlK4fh89hPCfVO4ALyUkeOvA88QBK/ELAMwuZreTdEjHjMwLUPTNWmg42W4GjXNCwFl6rwvPmWtg6H03vdqGZaaIQbGcsHCnKERyzDebC'
        b'vaCfy2eTbfAIQ9CGszJ4ntMUHskoCfQF/Tkj2CUlGc0Hm6rw1qzpLHBEgKnpz7glpIoSU2csxyYpMxLUJN76oIVFFU7Vciph9uQN4Qa351bfXB+10fcuIdnkXgMGYGcy'
        b'3AGa5wjRcj6bpOXlOyNBLX6QkwYVBnYREoNssBtuwn4i8PYpmt/mMhm7PTticK/kUXPBQS3D1TxyaBNRbPQXJQKuppESmVZMjkjgbrTgOCr9Q1Jwb+ZMtRta/F146V6y'
        b'XgscMYYniIaWgpvreNJoDkXVZV69mvtB2ViG6XXX1EvnU8OVVWW5/UGv7bB3cHD33mrI0zSx5cYWHd2o3Fgzsq0oxdpf5tCStPvqFxHff/H+o9m/LPylICRR2rf3/sAp'
        b'k6cjjdKv/1lzLb08bN+HSj/tpmjvuUVOPyqdNceXbjM6sBycN/3V5A5cvtMi8deKHyp9DTza7kgk/KOKvqi6Q533tt0r/NVweavRScfy0n6jW/pVO9eG1Oh98vtH7I89'
        b'fO8nL++OGHjjzSnXz23cXeZzeWv6Dr0vh/NnfLK/41hW6i+hBmXep/9hybo+6Bd357dXPxps+WiwqV/02ciGjDX3UhMCHc/kfthjtsIMtLdHL4neeCjr074Yv6Y+85/e'
        b'/2l1WOMpTqnVUl8D/w3+Jq/tC3ysP1tfK2TJzlDhlsOiBPPgNw/72e2Ifm/GdOG2nANOdbrNAZVn+xre/PDY02zn97L2DWkeOiN/fEnD/ytv/+VZZ1wu3PgqN+t0zpaZ'
        b'HRxh7nqTX53rvzoX896MJ9PP3I0qm1Li/+WXv6YtX/fo9K+HFo3vk6iaj/b8ZvZG2ZuNi4ZLfPYsevDFl0dcPjyf+7Tkylb/L99ZvXQZfar20LrDadclH3Tt/Xrg8N5B'
        b'l3dX6v78w4kVei4//Fx+uO2I+Ohvb8+v+ShpwVc6h5etyG/X7U/Y+ffg/JjPNC1f/bCobIrte87er9ekD8xOuftkhlXt4f6Cn/e85zTjbkp1HjgS8Ct95+MPA/ZlVWTV'
        b'W28ezHuQdf+rstszvp8atjGv5bSh+Nt3dU1fKdnat1Y27fZj9hnb4qjG11PLvzty1uJ+26dDc34M7r66+vPNfIXOnguvd79rVbrwXbeO9wpb29KSVWnxMjPPh7H21Sav'
        b'tN9fqrjt5zT7XsqbX5yOsN7wRO/zj8u/efsHg6Gq/uGG7qmh1Gpr6eLv9m/hPin9zsHH+4PchZn948qRqG+/z7g5/6KNy/HVr/3GV8olP1/9ar/CJOmrGZnJ7x9xvFz0'
        b's+5hD83QmdOmVnx891DDB3Pf+qqi+Z1S7heZpx0rVqsEXjv/VmqV/TQ0rVbzowg/89AH095vjvko+c3XnrLitv14DwQ351WcuvLTGzLhvHFHg8btX2zbvEMzL6K8XjMr'
        b'dM7dx2+VFP6H07SP1niEfSmxYj8we/uLrq9///o/Pp364/5a1uBv4mm39L7Pvcf3/Ba370WLMYvLH40gQb2Nzh+NIDcXq50HmcxizCpdQd+E0aVlFNkFqEAL3gH1luyr'
        b'sF69J4ua9AWy0rdOXj1h6jdh56cFzswoX8vsorSxvMi+KbhsqN44jQGNjIONRq2oCdezz81B4VZwSG0Sumuxeot0EejAW1bPN6zmCsiWVZ8nsSbMLICHGce7vbAfO94F'
        b'DTPIIj8RHoAKZocMXNHDtozw1XUk7yi4HXRNLPDxZ8PzZJkPtllaw31ccH7RMobPfx9QgHNIyh5wRsD47EGfqGvChpvAdRvGfvwqVFRjE3PYNreCz6J4NSzYDnrhq8z3'
        b'H6LAVikfHIanJ2wdTWA9+S7smGGnFG6Hijzs4SgNm5/q1LDBqRSgYLwADdgGS7HlKOgsVhtDgq3BjAHlJjjA1hXhTcMr0excVjC8Vs44HsJ+RqRpQtMJu054VkB2kexy'
        b'QP1kw9kd4AJjOAtPQya7KXCHJXG5FJtPMXiJjemwgbEp3QN2TZ+8BycABye24dCIc4rokCE8AbfhfbxlQc938uwSSTlWeOG901TQnTiJtp6xcIQ7kkj0tbZFuDAGFz/b'
        b'bWLbrwV1ZIt1NjgGTuq6uTtCxfOdtXPwOOO0wxG7SKlHZbgDdMINHCR7FwuNVdvhIcbseTk8hTfQd4Au2IT1lwPOs0CrngNjG99nzdMVpa5gAlSijI1NOUuA/BW4JYzZ'
        b'wtwNrgbogi5wCWxYzmzUaumzi+AgOMbsqB5caoWNoq/Ag4y3qWe+pqaAC4QwYZoVPPsnxgRQh4bL7j8yJoBt6cy+aG817ESaqyOe2BwmO8PTAGMkjaJsBI14Y3gmODlp'
        b'b3gKn2nNp6d44/3fBLhlYv8XHoKNpDRY4Dg4hFtzIegjsxLsJwz2Q8bx1ZSsEryxBTbxJu1tqakmDoSSRhWp7QAb8JSlzBg16HQW3IA94WAFMpqVQFw5A8X8CTPZFaCf'
        b'KcQzvrMEInfWJF9rhKfBB5wkG4K12vaTttvIHieLMs9bWsx1AI3gALMd3lQNToCGdHCqRj3/0ApgLwCXkY7gJu0LthD/3H+cdSWDjbbmXNidC2UkmWgu6umEEUvT0Ec3'
        b'EOc2Oils0FQCr5PzljTUMg6iZPA8C9SLk0BLwcRMhkd5ztEwEYBmYkRcG+aDutgA2PGnXvYFG+JzoJsxFN5dXjBpCgV2JcJ9mpTBHI4XuGJPDJjhZqQTm5InMp7IFfSV'
        b'8Ch3WMcD58EecI3RuXOgKwqnlg7rsUqBXWiKhVLjcOx9ExkVOFOJfd2jsrikOcGr4Rgv/R/dm9T6n96b/ANlLLPssGP/lckYWXaQDchWtCz5kWxAPloZx6JsHDryD+U3'
        b'xRIbzePTW3gqezdM8H/UpkUD232Gt4YrLcW0pVjhN2oZiJbMrTEqa4fnJrGKnFHrYJWjU2vMp9iWM37Y+bb4lliZNI9G/4vnjTkUjFgVPJAEMLz8SkkiLUkclZQO59ye'
        b'g9a9sxaPpZa2aIzYimlzz3GBl8K5n9/L7xf1ioacb/Jv8Ifj6KisMUH2SG4eLchr0WhZSZu7qfgiZq9MyY+g+RGj/JyhuJtJN5KGq8diclCY6lYDlUiCWfZHRdEDlaPC'
        b'RUgo4S2hMmkunTR3pLCETipBwVbR5u7jAry3YDloed1m0EYZmEIHYgNSQdZETg6uJ4WdQqWDN+3grXTwpx38Rx0yB3yvhw6GKoNT6eBUZXAmHZzZojnO91PUDHHH+LGj'
        b'/NnD00YyZtGJs9WyCDx7ArsCn+/cjArShng3tW9o3zS4YaDO6YGd80mDTgOG0hxVAl/E7GOE0PyQUX7mkAY2qx32G4vIVCeKwhMKdE/azrOFN27rJOcpTPtte21H3SJU'
        b'Tu7YDYW8ZszJvyVW5S5GcWpaDVEt9If1hiklCbQkQSlJoyVpSskMWjJDKcmhJTkT1fAAaQJSAFT9tnh/ZNTWfzDugZ0Lzu65iCrmAZM/80hpF0DbBfzhRRBtF6S0C6ft'
        b'wvELvU69k4adhozvj1G75AEeJqO/bjBooAxIpgOSH2nzAmxa4vD2jJXPU4PlLAuP7yj8+6iIQzm7n0zrTFM6BdJOgS3a4y58uXOPsEuodA+h3UNG3dNucIYSocGYS3qL'
        b'7gNLW6Wl76il77irQB57dPWoa6yibCiyd1lrwmMNys1DnsiQbCs9ommPaKVHPO0Rr/RIoT1SRj0WjGDr23w6I1+ZsYDOWDDmurAl4aGl4wORjyIXb9fNGbK4aXPDRhk5'
        b'k46cqYycQ0fOaYmT+bemq4QSRVzXvFFh3kDt9XWD65ThOXR4jjI8jw7PQyH8WtPGHd3lQYpa2jF5KA79tMSM8z3ks0/ZYFP4cSdUqJ6POGznUFVAyLBAJfR6zEM3D3yD'
        b'yd+W2EdalNCvJfZQ6ri1ncyibZ68YtTa81Mnt67pKjs+iugezRr38lUU91mqPPxRHHT/IDiSuXhCsZ1jWK2x6PMdBA+dJCM+MY8olnMu61bMyIyct5JVEcmPOfhelT6T'
        b'uUD5aVBCb5wf07LHHBJGrBKwqxanjtrWWqWthLaVKJLu2oajZ64eShd/2sV/1CViwLclXmXr0rG2da3S1mvM1ksllsh4x/RUvhEy3h077weBEddtB22Vgal0YOpwze21'
        b't9aqefkDFuAAvipH95OhnaFKR1/a0XfAFG/90Y7RKndRj3uXuyK3P783X+kbT6P/3RNk0SpRkHxhz5KuJbQoZiDnjihGzh4Xeyu8T9fc9w4bCc8a884e8ch+pEN5eivF'
        b'EaPiCPxWcmrlgH33mvt+USPReWN+c0c856qEYqUwjBaGDVTQwsih7JsFNwpGhdkqD58HwRHXwwbDlMHpdHD6e8EzupLlMQpnldhHvnbIYCQzZzQiRxWfeHP1jdUjWbl0'
        b'/CwFr9+g1wB1PJ4xj3hUSCYLFTpf9MieEsey0MgmDh4Jnjkmyhlxy3lg49iu+40U1YnHYw5lI/iRsKhvnq0/R5s1PsUf/TKbVkYMkD+F9yc0/786oBj9adPqvzB+fDBh'
        b'coy3qGqwQYAlNjm2xCbHli9jGvAdzugMtkczX7EeX2/AP6/in5/Qz72pBZhkdWElszNWgBlVS8sXEWvoFRvxTxs2UHLkoKCaalvZe3qTDVLv6U4y+FwhwqHrcLyf8U89'
        b'/jFgYQzfM1uze5pqc657epNtp+7pv2CJRGxXiMkEKSb+1P9/p5N4qvkXDPETtdbKRbX2Ave0P66stUjUHzBBvJ6+0SMrypk/omf/sb5pq3Mnp8Wyq7g3etB0sOpG1kDZ'
        b'LV86M5eelTcyYy49bwFdVEq/snRkYflIwLIR4fI7+hVP2QUs/cCnFP7FnO4rWI/Ik8cxnAmO9njM0Z7IqotB6j7dYdxIqDL1Qo+mS+qS0BMz23Ejd5WpP3piFlgXj55Y'
        b'OY0biVWmIeiJVVhdCnpi6ThuJFKZRqAnllGsumT0SJ12DE47jklb/QinbSohT0wsx41cVKae6ImJd1308zCROEw0E83cbtxIoDINQ4/MI1h1eCCwsB838mBSspDUJT6X'
        b'Uoyl9JosZRqWMoNFxLR2HjfyZB5Zo0ep32qx9B2/1WDpWz3VyOPoOz2l8O8j8suQy+Jd1HIggxulkyfHmqCBzMgtoJxbDK4uewGz+ozLFpvK7dMktkuYfZxSG8tol2g+'
        b's2Pi/s9Zn+lRf7RjWpRWlUFhZ9BQBjZLPH28/bx8JaAfKCorV1RXVEnRMkIBz8Nz8CJau1yAfYZaejoGa8BlbX1dsAvUgUbYDPdlZaDV3oEcHgXPwkFdXVjvSraJDcAp'
        b'2EWwrQ0CMYas7yoC+2EDhzKBhzjwkmtIFZZlpgTul2CkWDtFeVFeKJPzBEEONoXC0ygObADbgtFfDti4AsXsQTHBRQaOjaH48LyEC6+DfRTlTXkvA00EYC8FrSySLc9S'
        b'/CwmzhO0zSREqOAYHNSXsGfDjRhLLHEB+8ge9LwaeBVlhaXlsChTZw7YCjfDS1MjmeyO+cDDEg3QDrZQlA8G84FjjKj70ZLlKvOlpaYk9hSUYQPKEG4oZTI87FwpQUtG'
        b'gKrKl/KFTRnEescAduiRb0SrfBKPTZmaoGjhYJAUDjzOSpbwUBnXYTY8P7ARbGesflqFaNWLvzAhSqyOx0LxhGAzE68ZV5yEA84nU5Q/5Q/aJIx1xJUUPXWNaIJOVCpg'
        b'kGOEnQPbwr1VuOuJg/tWSTSBAvRRVAAVUCAg2RnCy/CAAC3JXsWyCjQdmdzAftBJsitGwvSiKPAarsVAKrB4CimYOUABT5DcyuA1MY7LcVDXoYY6w2mwXQz6uOBIKkUF'
        b'UUFRDiRD0AYPwqPqWkedM6k9RSa8tGYlMf6A293ANinXOJqioqioFSFMochtMKYG9NuhDFFUx4k62BjCWIx01+RL2WvnolUyFe0ANzM5DfJBu4BoJwd0huDiB5sXoG9r'
        b'cCPyeYNWM6lGNFaUGCoGbighxMTzg2YyxeiNXb0KxJoLSFGiaM2wncSD58GVdCnLPYKiYjFG8QKJlxEIN5D6hnKsMCjiFHVRXgYnSDxwJWillFcLr6K6QLVRX026G7B5'
        b'ngMpR0Y50eXuqUxLIu1hN2hhCKkvGoDTUg44m0dR8VT8K6ChipDcdYKjPjg6JzoRyXsOaesVXPcnUVx/sJXk61wAT0g1FwA5RSVQCWB/DtEXz3gBLhjzqIloIRNZtmox'
        b'irY5wgz2UWBLOkUlUtjeq5NETJEuJvLORW2DqMyCiRbYq0UakxPYAbfAPi5sB80UlUQlJYM+8qmGsK6MKVtcPuhjNcAB5lNJXe5GGo4/tQTJMwD72KBHG1sBJHvlMaY1'
        b'e1HofkEtOIfrcxM8t0IdEeyfwzTEg0ChB/s04kAPkpJKsSgjR0DwIrgENpE8rcyJ2pGopE5hCzxLPnaeO+yGfSx4xJ2iUqlU2IbqGmfqBmWwDVdNaoY6aoi6VndpMuq6'
        b'OTEU9vGE2RSVRqVNt2CyHAAbUD9EPlSK80ZN8shEtYAL85gaVejHwj7sKnSQotKp9EW1apJk01hGj1Ase6ZODqBGeAn2JZB4ZW5WsE8TXlmLdI7KQH34BULLbACbljKR'
        b'otStygu0w0vxcB+jfFvTBLoUGto2U9QMaoZjEnOuuBGcARuI/qAO4BxTMPs4sAnsRIKeAExDhvvgqWm6XAusuZlUZm0FEZTrAvpI0yIRQ0iWGcEo2hnQztRHB+rFj+iy'
        b'rXywzXjWOniZaMErLHharfDq8ePyOpTMhBZcBnVqhU+H53Q1UCeD+p1sKls7l0hchFrE1mdKRNrMoSoSnVRobSKROFGK4rI0cFc3k5q5HmwkRYTdXNcL8MBGho5NK5iq'
        b'hOd4JBJrXbEuD7QkUlQOlQNfBeeYXuQo6i+YYQ59KjNOFS2FlxbAVkbOUwlwry4nHW6jqFwq1wpuZEyDjoEesE0Ar0wjnTiafPmjrLKggmQ1FZXNdl3NBSivWdQssCOO'
        b'dCHxzvAA+ai16DWqkSOkLZO2NZ/RthmwbRVooLTCKGo2Nds6iOiuXjzepuWCbeAo6pepOatRQZMql3NsQQN7GUQNP4/K05WSJCrWaMI9vGhwjKJElMjRjwm6LWwR3MPR'
        b'QFNRMSUOBDuZUfFVPDxlUXHgVWKJhwaF7cw3t8Dd9nAPe0kmRQkoQTW4zPQYbXh/MIsFu71Qr0M5OwIFQ21/egk8CfdowmO4QjwpT3BOj2SbXc6FezTAVmtidkTBXpJ6'
        b'JVWUxUOdLMrUhXJB49MGvg7T2R0XwT5cEaTLYgooBI/lqA77UedBdpivgaNWuLoKLZieXz3sclwY2vnWWamkiN3BFtKcmSLGmucoIZZSeiWlzHBtxyIjRhvohJe4lkTl'
        b'/TP5OGkOaGJ0l7NA3Rk0gjZmuiCvcCbJg21owoTaIhqg1N3qWrCfnPPXLjJmxjCkYVdIZ2KbCy+5+TAc9hvhMdR3krZxBJwjTYSzYKJj3gCuM7n0wEYvJtAuqbrNq/Uk'
        b'Ud1vgf3l2EQTnMbHFzhAtPorw+FRPosEKUFF1Z8M6z1gfQJ2ewt62HAv9nsrg/s/J3PKphURfB1itSVBxYgmlp6vaBWmNMyuYEy5bMyJfddiOr8w5cSCRczDdTO0sH2X'
        b'UfSCwiXRGkHMw2I9E8oJjT6faBWu+d2Fwzy8YkxsxlbGpxamdCyvZR7eLjegkHAZ5SGFHmlmbszDjiWaeH5r/plHoV6tKJ55+I7ImEJ9bULmysIlm9cbMw83qy3WkowL'
        b'PYZLPJmH0YWmlBuKXpJYONfMXMw8/HsUMfQO+D29UM8iYS7zcLcfsW0zqmEV6m0My6aIke4X/mZIN6mVN4WFa9rXuVJ8dnYcefFmNEli8Yn0wiVBhVwmdLtUA8tq1OFU'
        b'uOQL40Tq84Ot+N+tcJLBlkLyJbO+dC5c4lvmTX0uIf+ehDOm4EfQXHkTrqY6cJ2illHL4C5T0iRqQT3oR9qkqEGCUCvXwPOMtawtM1WW4f4CqUOx4EWdQwNxO8k3P3Aa'
        b'/oaMqaLCNV22QuZrnXOm4nJJ0I8tDPm+eAXz8KbGbEqB5P/bwsKgY2Ge6GvT0krXR17mSt3RKv7s9Igte29JLWNN37ic13zmnf1FtT5zlgjeZbOmXGzacprbdtdoeMHy'
        b'BNNpa/cNDbhrBs6syO5Jb9970H1a7nZdZfvbBa/tE8z8RXfN2NEZ2Qkbuv/mf/XK0++UPau/LfrejLf0bo2ORlfoDh/vT/VKbnmsKLLhnasLXGHjfK5RZ3CD+6DWrtM3'
        b'XL9c3JR6ftjZY49g8R5NRZLNa52h71QZfKK1+vbD2m/c5tkVvJb8qZeVa8Ebgk9Prdyxxtp12H95c8iWsU8triQefj3wmxBRk1lF/RrdA7f6e+POfnIo9NfsT/KvbHv6'
        b'mBX2mkYYuDmwMf3Rf/T8ePLeK0c1Tm36vjAwY8/1tSbXa9zb01PfNbz3c1B5aLnhvcgSb7ZFybspO3+v9qWrW8dv1b3f3v/GiYC8lo+X/HCx9KdwO/7cL8diJO4VCyUD'
        b'186u8zkkXXLb82Mjx/JvnyTdaiz66VuLC731tz/+8Lfly0SLtgT2Pd37zqWQPYvPnnp3yqIVzfp/c/k1YU7J6zFzmr/s+yjj9v3FU88emxp28tLXvyTuCLmrm3HR/MzQ'
        b'57KiPSrVZ6qDB8zDXWe3Npj+48qnqwflNwceul+s/Gj4ivDWFdP+dMHdsoRS1Zy9wKdn4PHbFpKGh9r8wjLlVwfjvtoQ+EG2sn2R+Ep7TvvMjNTitzINkn5fNy1bIPmm'
        b'xNTi0Pb3Z9ee7xPPPb7HpDthtvvAZ+45fL27NZU/PNn0pvzE0fvr3T7Y+W7Qqq+AfOOWourT1YdP5dufPeSx5EncP/5+mNY5lH/V5Oo/Y/rKO8LSv3hLFvRZUfybF99c'
        b'ter3C7//PnPWa/u/O+beUKP/668Pfa7+4HFmW2reWzPgT5n6vyRar3G+8OmpXt+u+ZJ7M9K3xSvmf/nV+n9UTl/y+nbfrqflSfDuyYMrlwfmftFp/JFvzd8O/eOoVf4n'
        b'Kn9RHz9occq4dt+x8WM3d++6dKf34bnvfoUfJ3/w2c/ZSffvrP4t2/D1LpvKgWnrwqs113woP+OS/mRbjvJ+Vv7Y/C1Lk7NHDn7cs+/0oz3aV32O/mMx94Ow37d91fzD'
        b'jW/2pjgnf/LRktvJOSeeTH3c/PjyibdWS36bm/vwn6Xrxh8WHNPOtRafuOv4mvHF7zI+u/arZfs548BfDvINyXGWyxrsfyMTLZYaU1PSeRRvDQsek3qQd3NhsxA2iBPg'
        b'VnAYMxFzE1igLyGIOd09FQoPJKO4u8Cr4KwgGTti14VtHHYmbCfHoVHkaLQP/dc/H/ZLeRRHh+UFd4LL5EQzXx/WCdDd6UVZSTyKW8QCV4BsGcm1ArYbJ6cLp5okJnok'
        b'cindajZsywOnvmUM+9sDJ9spsWEPqK+NzSHnp7PENQJ8NtmdhWThVrFg/UJ4jIErgI3zBSK4g0exQR8LTR3P5qzUJwlGzy9Tmye152CecmKftAgeZwisr68tFiQJ1y7A'
        b'nAU8Sk+DDa+ikXwTY9XWBo7Dw8nYDkICDyFxuGbESqPxWzJfuWg4hyAn2NWs6pzIMDeSoKdTOgp/kfh+SQRnKEojgG0B21yZc0wZOADaJpH5UyvhYcLmD3Yu5Tv979s1'
        b'/At7jfjc968tIV40iFAbQ0gXzi8vKF06f1HxqknX5LDxMy5DTVOZyqKmRrHqYh+xjcwNVEaWLVmPOPjKQSiXMlc+4UMm5OoBecvDV+QtuSJv8dUjDcrYCr3XZK4dRSiE'
        b'+to3goUCkRstJpA2c00Cqa+ZQORGhwmky1yTQOprJhC50WMC6TPXONBj9TUTiNwYMIEMmWuSkvqaCURujJhAxsw1CaS+ZgKRmylMIBPmmgRSXzOByI0pE2gqc00Cqa+Z'
        b'QORmGhPIjLkmgdTXTCByY04CPbZgrj0lQyYqazu59MU/39gaYa+ejx3U/NQngzuD75iIVdMsD7yy+xWZyZ5lTRzVlKkHBLsFLQvlzviUpkkwNsW3LlplZYu9Bden1sU2'
        b'+ammmh/I2523J78u7qGxaVNOS9Hu/DFjx7qo+9PFTRp409i2pVo2v3WlXEO+okubtvVSeCkWDjj0ligtQpsiVdOtmqLHrR1kvofntrBU5paEr9VPbi+P7XJVRHYJaEe/'
        b'u+b+jziUjfungoAWQ5WdQwtP5ejaojVu79IplUuOrlTYd655z96nJVLl4Cyb3+nSEv3QVqQSiOQVCuMuaVdAp9YDgUimpbJ1kC0+uF4RMLByVBKPj1qxk/AZxwxRUBTE'
        b'zlm24Ki2fEanwTHtR2aUgy8qOid+l7EsoEVLZW6HvY63G6ocBfJoeaYsFGVv69Apka08Gqrwph19x2z9Wrj4bQzKM04Ro/AdcQzEgVxVVk7falAob7e2pV1SRcCptQNS'
        b'WhxF20S3cJhP8D266j17byS+qwfKfqXCsXPdqGvogOOoa8yQSUuszP5gAvp+B8kDW/uOmtYaWVXbOpSXubVaJDuHk5qdmnLeUQNUMA5OLZoqZz5KM7UlRuUiVLA6y1ri'
        b'VQ6OLdEqBxeVm7uMp3JxP1naWarQHcgac4mUcVSOLnLjI/4qJ77K1V3GVbkJ5Au6tHA4vjyyc5GMM+7iLq/qlQ749NWOiiOGsoedRzJm3HK9kT+SM3s0drbKXayw7+LL'
        b'olUCCT4OH+AOzBySDBgOTxkTpDD2R9Ijq1VuQpWHlyKmK0UWiy+iupJksY/1KfT2P0t7LHY2akbOwvsC0TBveOHwils6Y+KsWzpDXgoe9pk+EHnBYFiHFjNQgtm0YDaq'
        b'ZEc3zPWrcB7Q6hXfcYxSCTwVJgoHeVBv5UB839oRQYzSKWbEKeaRK+Xo+o0m5ez9TTjlEfiNNjU97JEmZen5aBVaydn9iF55ZrPQ9Jyi3jI2T3EzYo7sdO5xSpcueqnT'
        b'OkLkVfhi77riIEaRT+pWL0/AxLHLY2kqi8Uy/oZCPy9z/PYBiv6CP0ecMdnlJ9RGmn/w56hFXM0y9EZUic4zP44a/zY/jn+iNvqzJz+rtL+mdivEErMZarc6bgn7/we5'
        b'G+dP0vHSyCpnlxWbWuyMz0wKlxS7+VAMp87ZqGq8WM51U7N8uSW4BiVmJeA5SCKP8l+t4Ra0oJSKv8mW+qPgo+LAtjd9MJ/fFq+2+lc7Ey7t8WrYzeKc3jraqOf8tmev'
        b'6YnA9Xcz9qU2HtK7odduQaV9o2Xs9JjPWJqDDR6wKTm3esLRg0YI2ywanGFM5wfhaXDhLyCmx/wZhCnYZ81nT9JHPIRPjPK6CxcXLywrKC0vKl65yrYAezwtwASzz00Z'
        b'JgUgYz9aA5Kxf3EGaidTmyqafdXu1vcm3p/uMuI6QepvZt6kNYm0jnePVfpXzQbNRdWtg2kYR3DD+H8JMlXnOYXdd4syUGsxfJmGsg7FJMxA6eB8abJHGmgzwuhELqUx'
        b'na3D1WeIqY6CPbBZAJvT2BTYApvZxiwKXIJniEIM+bAZVpvqRvaUknyKz2JoczaBxprklAUOaWmYzkkrnS2Fp+EWEqU+RYdhxylJNvxnuSnDuZjwy3iW/vKKtXc5FDuH'
        b'RX0vIZsCr5eq6XGmcbkrcvypJdh9ukEujzKnEvD5tN74rH/OWUZJ8VL/3RMPs2ZWfaT3XQ2H4vBYzuP9zCYGd4IqzHb15wbajDWLs7FNGPUJGzOM6Z4TkXCnXMgOg5Fn'
        b'zm6HYHsJE27ZE7dD9p/wMLOfwYZAqSF6ZLu855PPKoPZeI/N3OI2McbZsacoa6Z+tf7ybGrLA0pDyNor+UWKS/VJYi7xVtXlhlHMJr2c2p8+bewgWxBSrBA7Q+aOGZ7S'
        b'uuVxC7UTTRbbm2dC8m1uH65dOoaVheK3v0YelT/Wfc9vDBW1O+X+9kny6G+3wwxPNaBOI5/K/+c5It2Uqz4N9AJ9dPUxtWVaPHmm3LK1gV5rgqJ+Qm0d2UV2We1hWyFs'
        b'SATXlxASHQkqI9DATkqcV8pOTGRJn6JEVbHfVGWnpr8fYXQo//3HPzk6uWjvlXVrBtjdSTacmX5V9hsn7X58dpWTwQl3t4OhdjPdLSu6sx87vr3rq69c2syXBH9zQ7Ls'
        b'o/1PrtRKxtf/R8cvFjZPbZ6U1X/cP7pBtoVv8+47x0xHVqXMWHbkFDAtHomT3bd3aql4wl1v+A5L48Lc+LBN+0ty4pZOay6+v/O9a3HDJ7ODf59y1zL21P1PtQJaOG80'
        b'iKl9zREb3iwzLvzG+8se2aYOuDTentfikfVueeWXI+e8oPzo73ujdj25W1m0Yrtnn5XpO5GGizf8+HFj1Y78koF3Txufrr39mdNOqxVXzltV1IRur/nuvMOWhxuvd/et'
        b'2/L2rFlvGBxaM8/1hDzsp+437HNff0e7d1NJUu/NoNRXso5/0R3V/fqyQfHAJ9zB5ENz3vhgXUbUm98vKzjk9eWxTb6yJeOFnwZO2xt0PPCpwc2cd06vfff2zEfrpP4X'
        b'YrO8t32jsF0tLj++wbZ67Omp6wO3f28IC3ft+bVSmtGwLGRbwQdfP6j83KAk+dGHrqHlHzc2C1d/bDV3mcnTDZrl8PV3hmKtP/6POzVyXv038k2PjU7mvRH2dnD7VWBV'
        b'U7jz4tiF364sczz44fsdi873nXq3VjNuWfm+s+478rYsO2G4NGbPpteih1fbn/3M+ab4ITfsxpmBT0rnVcxkpRf8c5NgwOTW099/ndG+udmCb8TY2jf4ZyXz4Y78EKGb'
        b'BqWxiO0OjoiZBeYhcAl0ofUgd1Eyw8ylBZrYy6aFMzDUNnBwOYZWp3po+qBRzIsFTkeAqxNOo06Y45XpZdzHJMIdmI9JC3Sy11nArYSKwgb0gQvSyupqfQOw09AQntOr'
        b'4FFl4MI0eJgDDoGBQAZiv7kI7CWr9CR+mnqVvtSSGR3a8lDqDangNEWti2eDzax4sANeIdFKQP0aQRJs4FYSsLFGJtsU7NImEGEnuA3sTWYI1RTYpRdZNINeoGDQ15vz'
        b'YasgaRa8LCS58ihtXTbYA3qCGIOAfjjgj2LzYTPcIMQ4ZY1CtiPYMIt52wePwk0CEd8ZXT3jNwGKAPLWYmE4WsrDusSUNB48CvZTuqCXDQ9p+jEAa3AxNzkxUStVXdD5'
        b'7OJk0E2+tDi3HG9z1INXQcvEOJgFLjC+/BzBNsJcBwbFKXxUfcFs02oW3+x/AewrxbL+J5Be9er6+Qi3atI1GWGvs5mBrSSDxdW3QOvWqRZ1sSpDkxFDW+xVY9XuVTKn'
        b'MTPXJi6+W717tcx/zEzQxB03s5OZ7lnfxH1obNHiJOPdMXaRO6hMzQ8k7k5sWdBR2lraVib3UmQrfeNo37imxDHT+CaWysS0KbNpfpNvS/yoieO4qa2MvTcdjd3Y2cie'
        b'lU3c+xZWLTNkXFlVp96YhbBJY3yavcz+pGunq9xNETfmEDw2LQStEqeZtXBaIlt5LQublqBbk2ktzs0hskjZQrl9Z7E8WsHqipWlKYpHnYJV0+2bolXTrWU69HT3Jk2V'
        b'uUWHZqumTFM+bczcs4mnMjFv8WoOHLdylbN6NLs0FRzFEtozaihuzC15zCqlKVY13RYtF80s8VpuDm0rVjjRtn6t3AdW9p3Rcs2jKbSVZ1Ps+HS0DDxZ0lkiz1I4j7kE'
        b'jE0PRJFMzFSWaFXckt3i3xSDXdZUtgXKOfLiLl3a0qcpBs9iEnYntGTLYlrz7pjyVXZOsspO3abIpuKmkqbEZ5MclaXt7pgHKKWZMklLCONTZcxSPGrpq/BG6ZrZMQtU'
        b'O3uyKOPIS7sMB6aN2UWgZ5Z2Mu+DQSon55NxnXFyH8XUMSf/AXvaKbglVuXgyizQXFyJ4NkKyZiLP16bOcmy5MadM+USWYjCd9QxAC/TJhZmj7TRIgYpiLOLDBWzLAWl'
        b'48Q/mdqZqnAZcBpzCv/r+5TOFIX5mFMQujMyPqC5W3Ov9tPZLGqK6+M5LMrI9Jkevahef1A9Q9MRQzv0rGVmEyaLVpmY1SU/XYRTGTF2+UmKB+MbVLx/ooRzS8JLDNFk'
        b'ZoF697jL51cuvsctml85/572ouLKgsrSyiUvZ6lL0JSTPaswM8fzZEn1vC2Z6qiXVNiTSjGeJDp+h5ZUji8zU0xFaS5kT1ojPFug/B/m3gQuqiPbH7+9sO80OwjNTtPs'
        b'oAgCguy7CgIiKsgmiqAsLigKroioDah0C0oDKg2ogCjibqqymJkkQwuJmDETNZkkk5fJU2NilnmTf1XdbmgEE81zfu+vH5qm7r11az11lu85J4eiBRQSLVYJiVJUHms8'
        b'Oiz7tUWHnYLcGm+AQgRqxH5iQ1+GukVsInaqWAuPE0MdIp764CILbofXYG3BhZ2fKREd4Bfuc5r/FHCsem9bY1tjV+M6rc9WOSj/7amHat79QgaVkK2kHpJBTxfr+ZHH'
        b'ItI4DdPC0zdBxib/SSgZZhNxErSVC0kStBxJwShn9rDmbAW5QLnkAoa/XnwBBpYI4JkK8sFlPMuTX7VILg38XEX9kL8QTfSMV5ljzO3//32OWQkFpwRn2GT6IvVKJ03f'
        b'TA7LxMMr2WvtoME2ior4gr1zcfVLTV/p5OkrnTJ9srDwj4vQ9GkZC8qEyR9q2kydu8GXnbtrZO4mvSdNce7W4LkzeT1zl4fnjiWbOwaNsMxj/wdmb0rgcaUps6eeQMAG'
        b'mvA4uITETZmsibi+00jeBNfBCSKL9RZYMb+Z85MqtfbBto2FGWqk8DzFothbLJhY9WCspEJbXU/iZpY90aHQINZ5RsoCQXfAzi1J2I6BOLct4DyOi3wli9xvvB5JeWwW'
        b'k+Jmxo2xLSgirG6C51WSXOERflQ0i1JevBEKmIwlsKHg3x1q7NIWdEP+vtXNf/I61tY4U6anWHo6TvOYS/DM94SrFpqkhpaDr9J366cIC7VC1UdWOUhi8qL7Cv1DXbO1'
        b'ilih9bxaZyNht4mD4Gj6KbO3Xda7DPZ/5LGo39MjZ92K+uzQDWq2w5/bvG2ZJF58b6hSJXnXJ24/JKQIlqqOVLXdPPLWji6vfTpJpxv9jvXvXqf3WfpgkGCb6Q7T2Uuo'
        b's29ZzyxeyFMlbqAp4ZV8VyeMR1AGfWvBUaZrogrhE+frJ2DbzTinDi4tZBZn0S6isCGjnAAZEL+eiAMS1yFW9RLimsE1xPli9nSlKWxVNGyBM77MTaAZ9NAOetfME0FP'
        b'DIlVuBdx1PD65q1MG9gLL9GSwgUgzpCF1lZCc94FrmNTFWc9YVKd7GBTCBDxo4hvINsXJ3094UYuJRepUuHy8Hwy41cJn6fyMici3o4yAw69uTUxhVybk7ccH7cVk/4i'
        b'W/sUJbPgYMps0uRf798YUBN2V3eGMKd1tWi1xHHE0mtE17sm5HNdI8E6of2ILlesJ9W1rQkZ4xiiG/U5nxvPEGZhRqGeLWAIPMd0DZo06jUQ+xQiSrtj4SK1cJEsGLFw'
        b'H9X1eKJCcQweqVJaegfj9sbVJYxp6h6M3RsrVBX7iHRGNZ3GOFYCrybfet+mgPoAMXuY4yIuu81xqQkjTIUCvVEp+TvuG/s3Y3uQsZAxBzTZuYXJzqQhWKJAdZ6VvjLV'
        b'wX6Yk7a8muz3d9iH4LBWE5VLpTNyqHRmDiMdbbtUqo+FfjTRj0oe8zSzR6byrKGICpbgvrEaNk81h7VTVU5n0tlMKlcph72TylE6rdwjo3LpyqRUBZWqKpSqkFI1VKqu'
        b'UKpKSjVQqaZCqRop1UKl2gql6qRUB5XqKpRqkFI9VKqvUKpJSjmo1EChVIuUGqJSI4VSbVJqjEpNFEp1SKkpKjVTKNVFo4GVveY7VdP1yB2WBYjU5erJx+QE4wAjXQ/d'
        b'hVXYaoieW6A79TfNQGeo1ccq8VlF2N3jZ1d1RdkrKXx+CHcNfYlLMsO4TbrOY5BjbNIxoian4WvRx2FVhaQA45NF2AG18QNF+XUeKD/vmNRC/C+6qKCsIKuwoCK3lCRo'
        b'mtSrgqLSMuzO4qY+5Tn/tVklWWu4eNX7c3HSHPyNW1bMzaKrmB8Wwc0rKMx1m/LklBU++VCzTCjnURiFlAIaCDmbH4Vkb9cUWRAUcAbWuLgxqEiGChwo9V1jVY7zVpsF'
        b'z9RYuy4JXZLfl6yKNYiwJh5rIVp0ol0Qwc7mqmqCc/oE5aTFDyex25Ny5aHbL4FqGmp5xAOc5uNI5wdj4zEdF+Ew7MzN8XCAXF8EcXj8mHg39fkkpzefQXEcWbA5T5bn'
        b'IJwDemO9YpgroIRiwF4chr5Lk0ZWHYOXK9HhEccoBAco5gqGJ9yRXi4j7pfBgVg697tHBYPSKGZCEajeRmOr2uERHMUenSs44uO+UlgXh1qmDVtZ80ANh+iVC1W1YsGZ'
        b'qHg3V3ARtEWjyzq2rLQ4W8IhzCkAjbG0jh/3CN2xHfYzNwPRHDobADgfEhsd74yuYwTePtifyATVJYtoCGmnIdwpSyUAdoYoUySTQCXcTk77HDskBZDgvFvhHnlw3opo'
        b'0t0Y0AerSfIGeGY2xVzGcE+CpwhPMTPKmc7N4AhuyHIzqEIaOTkXXIqfSK6wAnawKZKa4VoU0WFvR3vTi4XocXCmi3KlOUUjg1tio+g0DbAHdFl7rCfcSWSs0soPGeTW'
        b'uJbQEKxMx8f0GrhPg+RPiPWblEFByQ/uTCMPBi9gqv8bq7mpTJfYoPU0G5S+LJ3O6RDDkOV0AHvgSbIgtoVNpHMwBLvGMzqAaznkUbtAIJzI5wCGNJlAqJtL8oqged0B'
        b'2yZyLTDhMYVsCCTXAuxdIcOMmoMqvEIQi1EMdpC50oZi1lJ4EBwq+HiuRKm0BdF/l9NBJxddKQIeBhc4jroNwdXzxYedy7+pGu39x9G3Vjy6KUg57Ow347Lo2teRw+5f'
        b'39P5R3nfDGPz7R9rXvrgsd+zB5xbm59UM+306/f+zS34/UXhNj164X8t/I6rrHnJWGNpXM6cq8vXDNh2f3Xoa8/KrwsOrdh/Peurs5+eW/Wmvbfne+LckjB48j1R0yl9'
        b'SdLNvW/O5PyQfe0veuaXlkpvPfxhzlD/W/H+Q4H75vz4SUfTp3e2xDYdb4sNuPyN5ic3O/48Jy/G9dth8ZOC0bbCpW9ZpC73+fJH00W9w8vf9JwR8xfugZwMlb7L828N'
        b'rfP2WfRXf+EXJQcTPj/2ScWqhIK2T7/zr4rp/2jLB3G+bWffgCWFJSq/nK6Kd/lmYVZSp8q1JOGx+Z9/8/Y/u1r+8eEX3169a/3BogzJUOEHduv/8ubyxjMZmucy7t7g'
        b'aH5sO+Mv33c/3pT15JbXj5XXZznGzu66/kb+ii0Oq1JW5NmvSnn4472PrLc9Em3c4vDrI1HL05/+VrpqT9CGD7TXnX04763Q1vdFP66uqHQ4+5fTazdFnvL4dcmj92/9'
        b'+eTWipB3f1bZ9FDU5lDHMyPcpbK1HSFscPsGGasWkkI4wLhIXmycsxu51ghqKEqjkAlPwFZ4kFwugjstSURX2hKoin7XgDPMyvKFJAhEohEY0CCJ0mlLHajHmVsMwR62'
        b'KjwMbpAoD+A0L4S26G2nJhn1ZBa9/YjZxEt2vS/Yj8P8u2JLi/K2dCRPwBMudCyK9rkcsM9dRh9BhyMiVqVMeHQprCK9AxfgcURzE10ZmuspEk6mp0IeO/kChrG7I9JJ'
        b'E05rExzE5DjbX9eXPKrFywD7EhHpBKeYFKuQkQKOa5HmzNgA20lOsjj/KBzft5UBBCm6tMrXAQrRJUw5reFOTPe0V7Jmb0I8NRkT0JFI0hUgylm9nBBPTDn1fVmgbR2s'
        b'JR0yMNDBYTHORMGeeNQyXIX+ZhaikTtX0eFwhxAdu0peTwgoGICdqM8LUJ/BzvUEJ5eJBm4HuoOmoUrgGpPSsGdCMTgJxQQT5geH4E6FYL6SVBzPt1yGsmuF9Wi+98li'
        b'brjYkSAtOmqsMv0E8vRCuCOCXHbBccaVQT9flWm6Bu6mgwFfhq1peEJq3MEBOCjPKaMPT7Jg9coE8gZbdIZtJzFUEBGCLeAMhvHtwwF9tzvSavULi1CH9yViMp9ujo2M'
        b'2qGsiOWg+Sk+i3kp+fwEV1nKlh5wbkraluByFT30ikN0dwRIZCSrB5+90VpB+OjVzmf5w6oc2nLRPr+CTBm8YBFPFEpoAerPZoGrsGM1GfJ0E1CFmhsVbQkk+DcRavS1'
        b'WeAUOqV387RfE3ANm/0UAWqT0ijryri+8QzKRL6Zz6JVF6uSaM2TOGyUwxsztxKEyfS3M1p9Rb44DIbEZ8TcAxfTJUGiIIndqLn7PUunYV7QiOXcYZO5d82dJAYj5m5Y'
        b'bWxFMqBHjFhGDptEjs2wFjuIMkjKaysXSXKfU9eyEasA9LcmBrE5djq1OUnmjNj44szlYxZcjJoSL2pOJFncJ/+J85rn9K7sWtm3aWQ8S/1dazdJWe/Gro1D6iPuoSPW'
        b'YTiF+7SFOH/3RtFGieqIlSd+/X0rW/xrzHRGq4nIROw0YsoXKJO03FxxhNTY+YGjG04jHyFaJknpC+9aOmwxB6eonyVKwL/8pBau36mwncyE7BbNR9oUz12ySerkN2Qj'
        b'dQq84xQqdQq9GXpLb8QpVqh114bXt36oQOobNWoTLVQZ43v28aT8AKHKqInTmNPMvhXoOaFKi9aYi9+QtdSFXOCNOXv0mUqd5wyFSJ2D0FWdMQ9fIbtVU6T5oYnr7zdN'
        b'4U9/qYUb/j0byZvfaanIWqyLs83H1cfdMfCSGuA4yu5S75hRg9gxFzTT+MKoAe++tT0ZOHOr1tmi2eKYEXN3gepdjjkeoSipscsDnsfYDHtxnnSGq2TjkFLXtmGLuWMW'
        b'duIU9Cb8e7HUwh2NkTN+I4YE8jxRl5zmDM2TOs294xQudQq/mX3Lc8Qpnh6jjTfVpL4xozaxeIy8+6Kl/KDfGyOvPj+pc+BQltQ5mIyRlx8aI22R9ocm7i/TOMW/06UW'
        b'Hvh3GhouNEyyRpNhSqhPuGPgIzXw6UsbKpbOTBg1SMQxGXhdPDRU6CLO6o6H6rC2giSuSUcuuPCHIhfI9PcT2/m3dvNauRYfi+pLk7Co/pR6NXmdpI8VKfOoLg2fP5YK'
        b'nSTaZfxG+ubxZsvTlb6Pmq2QD9mG5BSXSWsT+bBfT9pzWXpYleWlBflFL04vPqWNw7iNjxmT2ijPLI6ryiorL3kN2Wt30s1jL1/hteKl2zaC2zaRuNkpojArn1uQxy0o'
        b'4xaUItl1nte88fF8PTmvP6VeYXo/mtw8C5KNtiQ3p6CsuOS15IwnmaW/YL9Ck+7iJk2kILaUNYnOD/96xmklPZNqy9cU5xTkFbzCUruHGzeRctqR5OHOKi3j0jVl/0da'
        b'mbsxN7u87BVa+enkVtqNt5Ku6fU1MV++Y0n4kZdv4MPJO9ZZvivKFKgL2h50ra9t56osz8ldgRb2Szfz75ObaUUIC6ni9eUVH59l+bZ76dZ9NXmWrSft3dffPrnO+aXb'
        b'91+T22evqLTDEy3X2E1uo+LrJydIxohfZg1LhqGlmNTecd1kJYPoKikFXSVDQStJbWXIdJXPlb4Y4TsVQ6v8AoTv/4vkzT+nTdFq4n9k22xYmYtGswQNKdoxCpunBG31'
        b'EnQ8l3HRcigqLpuqGJ2iHJ02l/eBTbMYJJf35YCdUzN5F4QxP+M94zHo8KsDcDuS1xQkbiJvwytMtv+W+dOkjr6CgzlZyRfOeIsnsLJ5+bllkzJ7r0hlUBYk7N+wgfMr'
        b'5pJ+qbf9twIk9+mS1D+UVfpljPBUDeM/YoSfYsadupLRpD6sj2CUYvQ3z4s5YYQvmGnLMinzetv7ZrB963xWvj+VM8x+MyBMPr3V6qAdze4s58nzy/YHtUD421b6EvC7'
        b'g18qm2p9Sibyoql25EtmdqwWhB1OnGSuJ3OtxXhJc/1LvfoHRQN+AZ5301c14POYRP0akQjOwX2gN5a46rF1GKATnNcjGupEHCugaEssPwFf8WagDSNcUPB0y3JmKU4A'
        b'ej2kEmPrqxvbdvD2e+7q39VhdOvrzITsmCzmOdPVJqtMkoRfeiiRnfcp740atTCtf8lX/3TiCZ7wiVHAzu0VelNGgQz5DHrIx9iqT9NSGWw9/vfaDD2v+1w7SY7U2HtY'
        b'13vSTptuzF/qXd/Kxxi96/vFeIzV/lcZ2yfvLTahwXTCa0oGkXi9lBidEj/HTyGjoRjPX0qzL4juTjZolXJLywoKC7nrswoLcn7HNjUVLqOckBxBA/X9KqjPVxugAeCu'
        b'H/PL2FTw71+L2aUl6Mr5nxJodEPqr/aILht4p3gxc4UeubUbqx66pL1pyhdVeRWmvfdQqbb0/mh1+Knt/cI99Ywr/3NBM07z2HszNY/F9bSdC2fO1Fx8T+icCsvLvPIe'
        b'PzzSmyV5uCLz1kOYXA9a/slcl29vi6iBYZ5JYPw6niod5/sgvACv86NgjWX0uM5MGwyyIlWViRbRNQ/HnqLVtrBXn1i2mJutEohueTMQLZBbiAzBIDESMTdjf11yOXcz'
        b'2MkfpzKg21hm84oMIFVrLQqJBWcy/aJk+lNseoLVsIdodX2ySM7ZaHDBTJapXSWfPJUEqyz5GFdbtSQanGZTyoVMG3gZHCdPlWWAwVhU7BKJ6AfbggHOsVx4Si+W/TE6'
        b'RgGnoFpQupzM8QQfJC8hO2wDveofVSCiZmLRVNlQOWZOULCbGzaLczpXt68eM8cwxKatDVsldr2u3a7o7/sGJk3x9fG3DTzEyZ1L2pYIGHc5GKxgMspxxohTZZFys6og'
        b'BGNjY+pjGuPEnlIDuzscZynHWZJ8m+NJVzkJeDDNKTkt7kABg1FioazI3sm79YvCQfms9JUPSjwhsvzFnOmCLCpEU8RgiZIv8CizkOhdgjXEJduU8KDL5bePVeUy0sfK'
        b'tNDwsTLNqH+sKmeJP1aVc7CEPJFe8bT+90pdjBCdJuLhnzFYQ27JX43Hykge7JCppftEmdI2FHmLyoTOo1r2z5iLGVoOTyj8iaMXOjwiBY/XM+WRAmfjSIH+JFCgkeVd'
        b'XR5dYuRfEzERXxCHDuQEM0iAQVmRFy7yISWy0IE+OHTgLBI6UBZxMBBHHJxLAg7KSvxxSQApkb0Mhzw0mscgb5MVzcRFvqRE9hiOnWjip1jRHFwSWBP1vaq6ls9jI8rU'
        b'Wmri3ubXMQf9qol+xtbVsnhEoQ86CiHmMSNBnQ0cwHp8X39iQlcHB3Ci0rNg9yRSqS/7/V0Q2l2HTacBqiijHxP0Q51mymEZBPWgVaNfw8lT+uMAFboWxLup7VSVAVNM'
        b'CLhDdRK4Q3WiFafVx4Ey+HTSQO9n52govF9t2nuVkDShqXCX+qR+mZzWkrcpx5TUqk/q1dmpNv6ExvgTlPwpDN2R/Zic1u1Rpu9UQ/9zzGoYJIQjjQrRqtGu0a3Rq+HU'
        b'mORp5ugp1Ko5uR2yH1X0o5bHOq3fI/PczDEnoCAlgjPRqNFE9engNtYY1BjWGNUYo3p1czgK9WpNqVdWJ27vaQOFepVkNeqQ2oxQTWo5hgo1aSuMp9HEeKLxYeYYK4yo'
        b'ziZtxC9bfKwt26boV1Z+bskDH/TIpKM6hDv5Dny+o9+l3Cx0tCse+BjTklXGzSrB2tF15QWI9kyqKA/JYuT+HHQpuwxrEwrKuGUlWUWlWdlYMVP6HPQlugwxEMUlsleN'
        b'vyWrdFx8RpxHETeLm1+wPrdIVm1xyabnqnFz427IKikqKMr395+KrcGS+XMdHGdc5oUnh7hxw4qLHMu45aW5pAdrS4pzyklzrScjkJi0Jv0o8zkH3nF/2SL0cVhp3IGX'
        b'KY8WSkBIKuOuu0qvzXUXiUMP0p+fTjKwz+GQ5BzbGvkA/CEo0vj4Y7EcLQLFSZtW/sYrhUxwjhs3mqiFc4pRi5C8zs3dWFBahks24HlYIdOC5k7DRcoaJNP50G2aogna'
        b'UIAbia7klaPqsnJy0KJ6QZuKctAPN2vt2uKCIvRCRY3w77CwytTzLKxWQnkQhVUD4PJmxRRWUW6xoDtGZo6FDXB/HEk4tTAqLkGeCgLcgHs04Mn18Gy5O6rC291ncgXk'
        b'adAJz6Aa0HMEMaRMrYd71Cq1gJj2ZD1XlgwbkbgVtRS0syklRwYU6sMmOm7b1eVlfBVwGdSS6FI4NQodcfFaEDfJFQzhbMHwHDzpRbHcKJ0App0mFJRjr+E162E9SWA8'
        b'7jCNUWPgEmyZv9A1hUn58pRAvR64SrBC7qFgB5+pAdsRB0CVwqN8ws/nlBDHW9VLSpkuBltSqXI+KpxnairD2+AOwZq4BTirhws8EE/nz1hQjANHqsAq50I6UN1RcEip'
        b'dJ0SFbcMceMUqDWGxwueZr7FLEXMNuU+eLn5T0FIMPDDYkFpkwcc49X1mFqfdogQrzJidosEyQP5/VndHzx80+C/Pq/6x9cPb7btM28+a/DFh3G6611Z2pVXfyzkr2d+'
        b'/fDysnc6t9djFcGZ3da7lPIaeRgcnX2Ee+qsQco3bYuVyozBVQOPnaK3bwnubId/B8IVM9eW1v4kAC1nGll3DzhESJrvSu+51BY8XCVc83Dj53br/nxybZXdatFw5a5A'
        b'u69F5943NakVjGg4Lqx48NXndXveSdViCd5R+azci7XpkZD588GTjTNjGSO71d+2Kej7Z4ywZHG3cAUvw+OXLJ9hy423Ur2cvE28DLyPeHt6hTEr37o1zMl4w+Ld+R/U'
        b'WC9T0/vyPYr61T3iwZiAZ0DnEj4Aqlcg2WMd7IljEFRcAZI6CLThDOiFRwmmZa7ZOFSFRrRUwwYaFn1i67ZY+VrTiIFNoIkJO51hDV33jtylBGuzzVsGtdGV5V1aCNuM'
        b'5GAbDLQB572Z8IQLaCJXPcHxjXLINKhfKkNNO4DTRBrSAf04ZQ1BIuIcQscr1AyYoI0Pd9J6mSPg2Fa4Lx4KwSCsS8ALyBnxl+A8a0EAbCaAlmAggif57rDWJTrcSwkD'
        b'QpguSzXoDtUu01JA+azcrAr3MSuhIIjuUHtJChLE4uCVCAbFtmaAY4GgnkhToCtah076Xg6Oyv0iL8E6koHIAR4qo+EnnuswugjnjndFTCgYZCOBEewkjYq3gxdkkiPY'
        b'swxVwWFq6fuR5xctLMRJXWJxyhS6XXqgiQV2I0bwIBqMIzSuo7Mc7d59iaAD1E9QDe0kVrwHbHmKYZqwH5xJQhUcwEER9ybiVFpo9g+4x7qSND44gKYBJxL0q4CDuR60'
        b'C+pJSpnGF/rFyuGFsCWDTqt0FfZAIXYJBwfg1cmZcRBFqKLTTbcsmYs6hZoDmtWB/J2IbUaV3VgBjvLU/4CMgQNgcJ9zEyNmZuPJx/Zk7MgCBi1zRixGMqcVljTvmdkN'
        b'20eMmEUOG0SOGVs2bWvYRormjpgFDxsEjxmbNm2o39C0rX6buGzE2EXAlqNJAkQBErYkf8R8lkBVftfW+q3inFFjxOcbNcXWx4rZowb2d01nCFdKWKOmLn3MMROzVlWR'
        b'6rC1V1/qxSX9S6TWwaMmIc9YlJnrsKnLfVPzVmORcaulyFKiOmrqSdoxe8hHKm/MA8WqLLmt+aL85oLWYlHxiKX7HUt/qaX/iGXA0AKp5Vwhi1R6H3UIu/ll3zbmEdTL'
        b'3BHL4GGT4LEZ1hjYMmbNIzgJriNBpNg4iMvvOM6VOs697Zh1M/KduDfi7oQtkYYtGc7IHAnLGrFZIWAf1nlmSrf252fqsi+lZO1bWEXos+AsjwhL1tv6ShHmKm9bKkU4'
        b'ypwD1RVABZgVeglkAR1bZRxL8BIzbK6h4BVYmobEb2scaMX6VfEEQmUnSqLh/cfxBDzGx0q/aRh6vgdy+1CAxiRogfc4JzWVdVJgk14T1oCYyrt+AwnxolbP1VA0T5ew'
        b'lZ9zoZgc+YVF26xq2DJd/+u1Wr1E5Jf/M6sVYrxLhpjPDc60BqaeH/7NJAYm76Nrm/80+5vvFUxMLGrOKPPzv/vwGE9J1PBdiIzLqOs4aQVdcJAmr7Bu6YuMTA7PTWdp'
        b'duFyEojlN2xNC9P/l7aml3xpqIaCySk0/fWZnCb5DhK1eA3j/43v4NSFyE4oD8AzuGcJ6JGdyOagbfxQxm4Ue+OcY1xAdzLtUYELEuOwdhf0gL0afpuWFnw5K4Bd6odq'
        b'+bhYk1Z6X4q62ug5hb91KN65O0HsZnKjkXdc7VR3Q7U3izq9SC3j2W4ei/AFy8GeIEW2YHXCVMaAZgtgjw4JTgSvrYPdE7GJYBW8OhnKnAcukyAYcCB8vcIKBTtAvwID'
        b'ALfH/4axZoL0g5ddPnKjGY9es4/T0Jo1mSFedMc+8LZ9IMF4xoxYxg6bxOLgZ1NtaSq/bUt7gSfaqzQvXmPCsPYsNf1VDWsYRc5jEnnHE16siAU7NCbsaslaxKyWADsd'
        b'Y63MJqxqYDc8W/CP9K8Y5MWHNzkQG+dksxpP/G1mdHZCFvOJiaJpjUXdsVYbSZA5jv+eAWBiSCAeEpMXDQmZIytq3MoWnM5Q1eP/YMDS83qkSlnbT2NnU3rxfLzSq+dp'
        b'TBjdfghJf1WjG44xhYgq1sFPIjLj3sErKdr2JvMsU65h1KigM0VpnMwovTYyk8dj/nxqigIiMreMmyXnDhSVcS9W3awpyc2j1SRTsIzTaFdKcsvKS4pK/bkhXH/id+ef'
        b'KRvsTG7xilW52dNgK37HsKeUUI6nBFxch0OvxdMGq0XgHGydn+qakjqtBxqo8lFbVQ7EJCW4YXbyhK6AVp9MVhYsTMrVUIH7QTfYUfDZ7HnsUswISdh/bv6TP7H2Jz29'
        b'1Hiy0RXRztN524cvaB47Pfb5gNDzrVUmKd7z0t7aYn/aQ2rwdsIR51nKQxkc2+FlDjs/Tn/b7G2XWXEjVd8+vLnC3ejw3S80NcPv2d9bay7SXf+hh7L32kGKyn+Hcyk6'
        b'jKdMRLwc9zgsDu+HHeNuwgwkmxHYfmMePDzZvYRZBNor4SF4moh3M8NgHUnU2zmLN1kYnwcv0cJpgxH2tjtAi/FroMgzFonE+Flr0Auuxk4IhRrgCLyWzoRnEfW+QDxT'
        b'nJCsfG1qsDlMzHVgP+zdBOpexWVZISSOBvbQla2rCrPntqXCNUITVsrodhmm23biMIkdRiyPGPvgQCWT5SwiIc27mSy1jx4xixk2iLlrZi22a3YVqIxxzJrm1M8R23W6'
        b'tLnQ2SBvc7xIFLvAEbOgYYMgJOwJFHHPqjTZJ5a137YGqk7Qfhm5WYTNgb/Rr2S5ZIIJfi4mOCaPXhHpXFL2Qp5mBUUzrrJ4CJQMDvbaI1n8fGFaQlM2FQJYnCf3Qf3P'
        b'050Q+p0vSXemhf7En45TIuyCWuBMOpIjz7kXR0Yo8zq7u/Yjr1GPHM+sbtW8++9R1EeeSjsH0fFLqz8EoNOYBGYhnjYbnGOJhc4MHmNXwC7YRgcVuAj2gY4J5840rKFh'
        b'gmrzwunxQeOQEXPmC1aVbJjJbrGmd8uj5CUMytzqjpmz1MxZ4jNi5oH2AJL+0U4Z1rWfdIa+aJnT4Ron+PXfe32OAhfzffiSV/W098GtYdJu/yqlWetzl2eVJkwykYxr'
        b'zgsp+XlKTCT0eaqKpEgqT/k/YCBZyWM+WDGdgUS+2rGdKUeWtO+l1nrIuE0stywLA42zaDjimuL16IDG2Qzl9b6ujUI/IxtWf2xHIdYwF2w8WVNeWoaNJ/TGLS0rKKIx'
        b'2ljTMK31g9Y+TAKoYmMYqnw6y8v4HsVtLcnaQA8X6vMrG0rUE8rxKoGnTfUQR5CKRA+aKfgdhgC2wsN0upmrOeAaP4ZJMRJgXRTOXnR8NQlT+em2oyS+5TOntWyKLWKU'
        b'6UFig+heQGJrRtUlZhbWBoZQybQZnsTouwD3z+AnorpgB7iwkIJHESdxsiDcsZBZ+ia6PlvEW5P41Rch6sBDt+UTn4J9kg29D1kBP+onKh30iypKD+Gpbb9YlfpY739O'
        b'xK82+Nhup9bAwIC3+/fKMH/Zz7czK9Itu3f8JanS9pQwPBb2LsvICZu56a7Tvyp0vv7BWeP9de9oH3ARBTx4uGTG6p3mjqobZv39UO+uD2y+vJn1gRr/PZc3DkkPctJF'
        b'm2ziO0/2g9b8u7WnNny27zuHE492fRDJO6Jmf8Bs5zrtP//y7zP94fGpDskzYjYeL2oHh9/eeF/72JMfGXtmuX1ZH81TpdXYV5w3IRYFHAGCcRYFNIJ6Qs0SKJx1nGZR'
        b'Nq2VMSmVoEvmeQhb8qNoD9h53EkMigbsIgxKNmiHB/gx8b45cTLtORwMJk6gfqAf9POdiYocHHRzYVBqc5igFfvl05qOA0lAIHPghAcrnlOhI4n4FGnBQnAJR0wkhoO9'
        b'iAjL463AdiAh3QsDbWAv3z0RFdViak00/0wg+d+oobmKAQBVZPFIKoymIZ6onNBtKU23H5cs+QNcjiGOAsgeNbSX6MvU0c1+grBnLMrI4ZEyThC+RLREYtoXMjJjVr26'
        b'gC3IwTAqBRW2sVnTxvqNYrZ4gXihWHXEmEdiwAlz6jcL2Hc5ZlhlnS8uU1RZiw1atGUqZXOBhqBMoPHMEL1t2ND+52e68mJaE/yGil6oKgs464casKCqUqieCjRQCrWU'
        b'aYLVFM6fJcq/y2upUQpKYPpcysfM1guGtlhRBbwEn0nWj19RBVyygCKAWqKmJqeT2rjHFA2TmqGMI9UUZhXlZ6so0C99Of2qw8eVJn1c7WHtYe9R2qOMji0MIsHRqjQJ'
        b'kESnRhcdZHo1+ugY4yAhEecKNcjTJ8eZCjrONMaPM1VynKkoHGeqCgeXylZV2XH2XKki5/ZgK3ua4ywkJwf7WxXlbpiM0MTGbtqwTuMAsotLSnJL1xYX5RQU5f9GVBF0'
        b'yPhnlZWV+GeOS9qZ5KDAx2YxNzMzuaQ8NzPTRebptT63hCDVCD5kSmVZL8SDcLOzivDxVVKM0W1y14myrBK0BrgrsopWv/gMnQQHeI5nnRYM8MKT9bdOYzwQGK1QujY3'
        b'm/TQhR7lac/WCY/BovI1K3JLXhraML4o6WZMePVtWFmQvXLSIU96VJS1JnfaFhTTTkbycVhZXJiDNpQCy/CcC9KarJLVz2F4xietlEs7KrpxE7EHxoaCUroFiO9ZWZzD'
        b'9c8rL8pGywPdIxeNMqetSN767KzCQjTHK3LzimUcyHi0H3oRlGNvKAzAyZq2HsU19MKRHAdj+3Of90Wc8BiRv/dFniOyulZ4rZhai6JH4+88j6kKYteSErmzvP1cPcnf'
        b'5YjCoU2YkyufKnldaOnTq2R6R5aw3Lys8sKyUvkWGa9r2hl3LOWSPzFQakrjJvF0spWJu7IWiWDo20twpJNYPc4UVs8xgQBQwNHU9FIvTVBdghitYiQ6mTCIOhO0c3ga'
        b'63PhiXUMxIDVIDYDtOXxGHR0vBYncJGfAMVr4AEGxQQHGKEJoIdwjuAIPB6psX7dAppNdHJzdYI17s7R8Yhj7E5eC8+Vpcxf6BqSlMKkwCFntdlInrtCghmB3VAM9k/C'
        b'1tDym/WSCVhN9jJV0OYG6wnruH4jyYHn5OGgajY824aiIyhdUUM8FOKU+KZgrxwaQ+O/XXiuMUpUIF8ZHs0HJ2jwyiktIz5sYEOJMsXQo8Bx0BFDB5gvU5aFcv8wtZYZ'
        b'QkcK/HK1Eh0HftYB9XXbttCFfray6PUpfMavsbLYPM5a88AlI9hBh4d3gwMk9DG5PyKKJOnz8MjzDfxuniFVjs/OUG0wQAdmiiL2gGjU8Do+ZrXH8T3oQpRLTJxbtKuz'
        b'MrVBBe7jaa5bCU/QGrxqdRwpKX4ys17Hi4mPA13JUeOYjUjYCarhJTWcpvFoBE+VxEEygnvYNNiAQA3QLYcZoDnRk+bBd4C9a2NhLbgBG+KUSTgjcNCfPIdYxqPz6IBG'
        b'OJrRVrQUEKN5LY1AaJfEwF4c0Ag0gB46qJEsotH5DaTesHjbWFlkD7YLvK7FAJe9wEE6i+S1+VbR8Jg8ttB4YKHIMtlrHeAA301rtTy0EBMIYTO4QdJIgEE4UDARWEgh'
        b'WAfcAXeSyEKzmDwNeoEfKPcnY45DYemD6wzQ4+9Kgj95cjT5aBpOLZsIhsXcDAdAN7maZALbxr0CfKzkgbBMKujmVUEh2B/rVQbPYymIRMJCdXWS5aYNr8IdqN/r4UEZ'
        b'6CePTliN7mgDO2LdYmA3PI+jYcljYZ1OJmGQ3MAJeBTsXTwRDWs8FJZVIcGY6YSBQ9x5smBYcm8Ef9oXqJAXg16aGTwRCYu5ma9EXszTwgGd4OCEGlcWX0lfiZ6MHcu2'
        b'xUbng30TcbKYoBq0g11kDCOZ4EYSFMDz8xfhm49RRcGgiYSscvGS7RWHhcuB03KK3L4gfxXqQaMlJ5FNMTUpeAPsAo2yBKN2QMwv1S4ph/2asD8AVumAWnixDA3uKlY0'
        b'ODKPzhKyD+4GLeN3kVtK4flyJWqjjxk8xYLHQK0FuTMAHgCHFG/cULZOrURLWxlNZo0Tiw23QxGHzgHdhUbgABwoh+dL12muA1VAAvbrlJSzKI4FyxccgHto8nQYkZXD'
        b'pevK1Ul1OvCCGuxHr0ZP7N8MG+XtmLtMWclrNulQekje+O143uS3cHJZIaBOiX75AXAB1o7fNt5IS3B2KRCxHWJ06VBoF5TB+fG7eM5oYErgedTCcJY/aJlP7uGiXS4q'
        b'XYfo71F5bYjYKlO6ykx4Nr6QjqZ1aAMY0oCDZagtmmpaSAArUaK0tjLBgB68RO5wdwWD8yOT4mF9Emrx4SSwH6d1OMqAg+BwpmzbBIPLSfNhlf58sj6oLHgxhqyVjG2z'
        b'J+qO5MirzoWXy2lQE7jBL4WDOugCE56CZ+FuhnN+fDn2OYOXVO3hPkT1Yt3j4xIXYQTjQpmewQXTv7roOFiLCIEWuAy2L1IrBQMc+iA6u5ARC/eDOljLohj+OE91I2wg'
        b'8ZvheYeZcCAK0YJYV7RjQMusBDalB1pY4IgtbC4kYOBgc8oHZxFZVlWqlUsnWzVzppJxkfVAjsBdlaKTsVI/zpV9cQrmsUlW0GQg0LJDYi2WADZRm2C1DSnmwn50FIpB'
        b'DzoSKqgKeGQ1neO3qRBccDTjqxCQZwY4RI7eYnABiFYqw33oewFVAGrBOSKxFTzZr8kqNWNR1E5p57GUT1aPBut++n6l/aV7Fy5t/bvbmtIKw64ayY8L3mxXXRh+IkrP'
        b'9fq3+/56MaP/pJ3krSbX8C16Vh9f3+t+Z9v7v74RffTz298WRl0riS/6wffGp+99k+c1d86NmrTPw/79o/uu92e+ed05b1P84GcrpXdPXo9Q67hSZrL0wsifnN7QOvbP'
        b'iNrsRfe29Sbcqjn+yX8n3fzKK2/svcejJSv/+79OR4Slbuza/+HFYPiXz8z9rv7yd/f7jm2Wp06Dpz7f/mJnx3jgauodc3ZLe+b7Kb27fGp9xe991bDub23KC1o/Ctry'
        b'pdtZj1L3Z/sS332v+sjZiOsHO/gPvKPWv28Qafumxfa+jcYPOrs+9duWeszWfsVxd27czs2rej3n7Pv19rWqT11dzv7lkOj0J3/+l3bGg3lKnbua0wctl81W43zWSN0y'
        b'fQD8vrLVs/9TltKT4I9+ot4901Dyyz9bHp5Y697y37ytWgvizmYZrnhyf1P6TrPUn8pnNrj33Gn4UlCjJK3WLOaa3gvzkhitM+oFW++qn1xyLr76zQqNA1eXmm266PNk'
        b'WcHnO27fOnz7VuS5/eUHyr/anfY/j4IKO8r7pWZjK6/POtq8/4usnhV5Se+835ey9UtQ8dPRH4s2faOXmzJ/brvj4T7txM2JD/ZeXXPu7D2nbd3Ba/xX9omKtmxbuPfb'
        b'jmUW/I7/Ph8X/s4zp7zR0rqfTT+zP/7V5faO/OKwr2Z9FTRPpV/yc5h1yq6G47ylD+0c/2f1kQtj9/pNzcB3V4a3pegtcvz7nlVvGOjeeTfz2oknnMXLZ57kvaXVDB43'
        b'7YKtt652fVpt2/LPzsWz3nd6K3F0+bvlP256EMXRbOCVRXVE/js0NltDpWHpbOmvw+qn2/3szvswa/KjfGKtojP/depT3lrhvy7VqboM3gr4yGwR56zR/Y9yWtYutkpZ'
        b'xjX7n5UlWaljH4684SRyeHAm70lqTfq+md8lJdZt3t91LPS0bc3tyi8tRsztTn1s0iZkzdLtLdRW/at678Wa1Dnfm62vi/rnUj2HAz+G1s8K+6ZIwLgUurtMJeEXhzSn'
        b'nxYE/mtgyV27OWXBg592Lot989khU6N3Yp5V/7R2zZ6WfrNP/80ojGffzubx3GjU6QHKhq8AxBGDcxjmoB/NAuKMMOJTBwczQQtiYRzZcgam24+Y59Lh1VmxcjRmIqyt'
        b'jEc36ME9LFCXpvaUTnoNhfoasVCsNhFgTqZcQ4dGHcFqxqqC7bFx0QvXy8G4TNgJ2yKJscII7ChQRJAywDk5iPQguAoGiHXSHxxKwuBWrJuDh6CAAY4th3uJ3mwG4he6'
        b'aXgrhpHCgwTfauZBN64fHGfw3dIMafXcZN1cfDhRHSrFgxaF6MrgEDiivJVpA46kkvoTUSNO8RPi4X5liu0Dr8Qw0Gl4CV4gHdOCh4ppsC5mwIREZ7cSHqfD4Q3F4giY'
        b'E9GVgbgUK/x2gRO0AeYyankDzmdCcpnAOtBF8plUZ5H3LoONZrF8cBY1WBlxAcrKm5h28DyoIXXHw0vwBk6k0mQyOcPL3LynxKgSP3M84PNGKwY4m69DniuEe8AljE8W'
        b'gCEZv0sAyoWwnrbTHnO1xHZuDSByV0FCSztj0WLaPgwPw9bVtB2JzQZd8AgDtIZvpO3DdTpcuM8FsaHoMIK18aVOLoglcWfBw7GRpKc5cNAyNi4hAwN5ZFZeYuGtMiaN'
        b'hWJXJvYwPRUlY/gyYsgIlCPG+LQC153ohSG+NXw6OWtv4rYJxtoT1OJEMk1giCClDUE/l3DWxwwVGes5umTSQow1JvhqsEsX8dWwA61U3JflsIoD2mDfFM4anlEnD2cB'
        b'8Qa+G6iCxxR46w3WdF60Fgf85DScdYU+4auL4A467ayadvwqHPiTNmmjV8AqVvH8AjLSJmyIhbO97omuTGoWOIwWo/PK2U+dCI8DeudOsGH7ddbBC1qwj4H24HkvsJ3h'
        b'AtuV1CpgA51N5wYQoHHdN1MbT4oLZtGPMtH52eUkQ+iBS1qymONgL+Kce9yjwRknBmUewQbHYDXspcf50DYHNFrbFidGz0SbhlKBbUxVWD2fzl7UA3vRPF5LGD/Lu0E7'
        b'Da4WwYugXRYbkOy87eAqGkuOLQvN9H4/gsDSAIOgjb7HLR4e3wxrkciAGgCFbLwlwXlSFVpbsBfRrz1wCN2Z6II4FTQ5TMp4Jnsu4kP7adTXDdgbRFeV4BqFeB1slMG7'
        b'IrvQHrYqZcIWeIT2HJAg2oGDsaN9fhnW0tOjAfYzkXBxBg7RyZV28bcRY8JeFyaVt0w5gWmB9nwzbUno1gfV69cQQXISgB/2p9DBLK/AnkI4oLM+C16XEUM12MVElTeh'
        b'DhEcfw2owQvbPWKtK88Jr6F8JjgHuhfzrF9P+ML/8Acx7j6nR6ma8k8GscjKyXkhxELhGjE+GCvRRuOtGSREfFBDkDhf5nBN4ib69s7pmjOUdHnpzUW3A5Nu5Qrnjpov'
        b'IgDyqFu+f5nz7hwpL2XEMnXYJFURMi8HVnAshjlOXUl9pj3LhrJuu86lcewjZn7DBn5jHGNBwF1Ta7Fdp1ubW5/dqKnvkNcYnfy0eVPrNtG2ESuPO1ZzpFZzRqwChey7'
        b'1nbiZIl1W2qHhVD5ro19W7bETrKuy7GjsG+B1GHWiI3vHZtAqU3gUN6ITbiQLVwgUsEWC5x4iNGiPm686DRtM5X4dFiNmnjKyiYu6uOLHeajJq7PdCiz2Y90KQtLbFIR'
        b'+0gYEmux34i5qyDsPsdYNEdcNmLucpvjQjoUOWIWNWwQddfYdrLxhmNI4t0H1QeJ7UY5jlOMN2NGlk2F9YWNRQLWfQvumKXjbct5ktDeqK6onpg7LsFSl+ARl3m3LWNu'
        b'5oxZO4+ZW+IohgGigDvmfKk5f8zKprVSVNm8bYxr26nVptWhM8a1G7O0vc+1wxlv73A9pVxPHDByi2jLHSt3qZX72KQrto6dAW0Bd2x9pba+k6/YOeHkQXfs/KR2fmM2'
        b'DjRsZqbUZuYYz7XXosviDi9Uygt9rKdmbfTIiLJ2wo+OWTm0bhZtHuM6kr9snTvnts2V/2XHv2PnI7XzGbPh4ake43nc4QVJeUGoCiujxzxLE30B+1EQZW0/0QiBFloe'
        b'OFPAHY7rbY7rmIfPRc1+zTseMSMeMe/GD9ulC+Lv2jpK2L2aXZp3nAKkTgEjtoHDutwxn9kX4/rj7vhEjfhEDcekDy9Zejtm2bDjcnRNrC/VtbtrbY8WeHFb8Yj1LIH2'
        b'mJffRfcB95tBwwuTb4cuGrZPEWgLS6S6Nvflw+MttfUes/cac3LpVetSG/aaN+IUisZuzMX7jkuI1CXktsuCm6nvZLyRgfuMnpCn3dUecZgrL0Ld5rfxb9vM6jMcs7Z9'
        b'bKhhpC9gPjahDGaMec+6GNAfcFP9Q+/YdxcPO6QK5gk21yfeNTJrzBOwxozNGiqF5beN3STK2BpnjBeAv8i/OUAQNmZsPmrr05cstfWXGvuTDRlxy0DKix+xTBg2Sbhv'
        b'bkPcUpgSvWFz/h1zT6m554i59/PPofUhZN8zdpIYSNFLyqS0zZGkgGrcgr/aCMqw24jU2Em8EH2gIhPzVh2RjoQtWT3kNVQyYjJPoDSmy2lSr1cX+oi9JJxewy7DPv0u'
        b's77SoRyB+qhuKL6qVa8lzBWHiFaO6jriv3XqdcTsUV17/F27XltYRq9SD6mVx6iuJyq9o2st1UWkAd9vZNKUX5/fVFxfLM4ZMeLjcaGtopX1leKkUWPeIybb0AbvYQ2R'
        b'hjh01MQJpxA3oJs0qoujPAg0nm1joh0tNfX95el6JmVh+4RiomdoaoP3kSRp1MpzzML6MYviej1ioYs/E0gqMJ8XlBrIumOql6ZO3QlUSlNRGVO3T/NijXky0CdtyTSk'
        b'LZnjdsKSldicOW4hLCn4XevmS58DmAXIpP9NPgFoi+ix6eBnCjS/FltF56E7f62ini3IYDAY8xjPKPz5Pfl8FQcZbJDtVPalLmqEMFk81seqciDMREyKbDY18W9c1V+D'
        b'Pg7ryq2iBMajIrOJashsokxiFcU2UYq4sbNqDPM4xCLKZlJ7x+2blUpqk+A76LuSgu2TvVVJZhF9rlTRSeRBEnMai+iitTLfmskGUWIazJKZtsaRPy82M8rvmOwKXSaz'
        b'0ilU4SIz1mVnFU1rwVmBjbFckkUaW1tebHr9I1ZJbOed9q3O8uY5c4m7MzEgydtBmwPpJmHbLmp6EW2Cm94iyA0tzsn19uOuyCohJiy6wyW5a0tyS3NJ3a+GaCIDKDPg'
        b'Ph/QdDrLK6p++ihvMrue3KqJDYm/Z/h6VTOXKvW8mcuKBjmngL0liDVOdIP7kbjLX/BiQFPAPHCApwZ7s0F3uSd60tl7JrEnye0w2MICaxKTJlmVAsDeCtipBvaDPns6'
        b'60W/KTiMgVBwdzCDAKGOgN1E62g0V4MyoKoWauhmxq1ZTPx8Zr5zMklrxqW16+jMxVmflYcRVn1NOB9IsIBRAw8mYWNQfBxh/lMn+amAQd+pmlLWIi14qmANUUqiVklM'
        b'4ACDmmtExVPxquAsHc/puyW/ULrM2dmUR2aukHFTl9ZxjomCk8ll8+R06h7FXamUWbVqKHCBP305oj2YXN3tu4oxylQ1Z3IzN/8aGkgRjaaaMRB5sykky++kvCgveBw2'
        b'lIfiFhyzrVQ07cEa15h42IiNWkhojpYZC+EFe5LwO3ZBVIxLDC2gwovwoFYMuLyG1hMjEfTQFEPXlEksVZLh0izgcR6DqMdnzgZX6Xx+48n8YAM4SxL6WYJW2gpzxN8H'
        b'noMdk9KgMDeDetBP3g4O8n1eaGVzkgeZ6obV6O3V4LpapbkzGaoZ5iyKTQ3x2VRmnGSVhkypHLyKHsgBhxTqPNXnoxlcVTEW2DyzpAa7bOIrPCUyfSnwmjfWM+MBxLpm'
        b'Ko6OHHA8FfZg4VQD3CDy6dECcnsh3I0aqkKBs0pY2ewMrxAV9IbFYAfWNLtwia65g03bd47yQTeWyMH5ediEqEyxZzFArzcUkygEZkiS3K9oGwLbg4h5SBN20nlS+sH2'
        b'LLgvFvSjFU7rK7AVsGNNwZtfjCiVqiCS77vn1/2N8cWjHrq7/zn707sH7f5aduWTU6qLVHUdte/NfqIze9HDld/fj7FoiAnv6U95+IWhiluNVb3lT9V1A+VBa50KT8R7'
        b'bfri2J3PHh/8MLH9o+1jc9/4RhhjXrGl23jD8b0l3bePJdb89MPh7nMfjM5jD877buPcQ63eeyScRd1/ftvv7W5d2/xuH/89T+rT1od1x+gFnqx92lhePFcc4/Xo26dn'
        b'+z/uivHz/vBvetFVNW+mfHb23Yd/+yd/nt3fw5Y7NDYEntnWtenYvfevWGwbbr106lHax92VG06yDtxy+FrZ1ubi3sSvgr3+8WR+xc2No2d93zl85ubfPftmnM378vvN'
        b'u3LsTBMF638qDPYOUrnTbtqatfvUtVW7tNX/yvBYW9zyt07nr2OT7wUbj1jq7Hr6Rq/XaFri6dLHf0lwiTTcPeeo9s8ZNfuP/TU+tvq61yLJd10/+W7m7fh1rpVu3HGd'
        b'055BVmm+e6ocdS513f52iZOt6k8xS87u/slx2xef8cb+Xbk0/bNr10e6k43bz0cfbh8pSpG+b8RU/aXGOejrr95zilFPDhgo39jWu1sUsNU5u+bZ2eOiyjmrvap39v71'
        b'Uu1Poq3Q9M3ed+7OO1r75eC3f5Ne1s3+9osHVx/vD7qdOkur/h9xsVeFacWeNssSVu7c0vPLB+5Pf63ZGhh+sMaXEzbMudyc+rlr1z+uhb47M8Lpp2+3/PlG3+qSxI7m'
        b'T796t/nGxRqeEVGrpMNWc37UQnBiImUbz5XOxtBgBvvhfpuJEANEfWdVQWs7z1LY6QptN7AXDD6ni+0LpfU5dfAA6MDOdNHgNKgxooOrGZnS+pwGQ5vYaHAgnVbzMUAr'
        b'HFpEFMSJxgX8GD64ES+HR1aAq0SNBA+HlY07Z6iD+ufzhgyU0OrDLnguG1Ef94QouB/t9CgGGDApJn1ydDCJJQb9WPZKV2ecf6KZxURUsZU8uBIMgi5EbObakITQJAl1'
        b'Ma0h9Y2BLXC/Hs7rrJAt2jaNDg/Qyg7UL+ajphCdpdoMJhAAoRV97SA4CS+RPH624ChO5XeU6coyJMrytA2WirpMrMlMBVewMhNcgL1EBZQE+sBBol6UxMlcYhzhXp1Z'
        b'rIwSOvwAc8liooqCB+MRiUaHEV+Z4uiZg2asWGsB1+hG9Bfp4Kfj4xLB2SIlStmCyYZnlMkb1MNnKqjOsNoMUXesOQMnSomSSQd0Ro8rzmitmTWb1ps5KpO1EATa55M7'
        b'wC5weLLSDA7AvqfEVLwble55XmsG2kKw4oxWm53YRPTGsC0KzWU/OItGRUFnBa/BvTyr/3uN1ItFFGL1Vfg3VU8lT1+oiP6qMH/eR0/hIlFVvcWkVVWFmQzKxGwcF7ty'
        b'1NidqFZCb66U2ieMmCUOGyTeNZ4xNsO6NV2U3pxRH3HX0EqsLGGNGrrcneEsmTUyw0sQgYMF5qGHOe5jM2wxSrZ5qSBijGMqDGuNEcU0x93mOJFag0fMQoYNQjDQ1kkc'
        b'NmrIkyyUAW3Fns3+EmOpuYcgFONtnR8Ym9015xKv0gUjlguHTRaOmVm1OoucxWkjZm6C0EfKlLllK1/EF2ePmDkLQsfsHDuj2qLq4wXhwln3Z9ig1xtbCMsatmBNV4qk'
        b'vK+8q1JqHzhiHSRUHuPaCZXGrO3RN+MZYnZD5V2urThcsqgvpWuZ1C5ghBsov4w/cO8trVtXiVZJ7PuUJZYjlrOFrAfmVnedvPq8e3REWkK2MP+uuc2YjX2nc5uzJKnD'
        b'XRh632yGQuPuGpuT7seOmMUNG8QpKAWmqLl+F6NsyZeEDYWNWobUawjYgtwxjrFQtSFoqjrM2vGOtafU2nPE2hvdl1avfZdjNGZg1pRYnyiOkuSMGnjfNbAW20nYowau'
        b'jywpEwuBxmNzytyq2QENpoExuS9EvE5iPWrgMoauhoyZmAojROriRVITZ/SXsYnQu2HDmAVXyBizmCFWEkVLlKUWbugv9DDOn54tXiCxlqzrCxmaJ4geNZiLy+Pr48X2'
        b'owZO8heE4azh6HtCfYLYR6IutfXui5Dazhk1CECldwzspQb2aBgM+PiemPoYYdmogR2tgVjHQItEasj7maTGADqGMT6sP/koxQTJ8NBGtBbhuDKlENXx9agNpt2nuOap'
        b'eoQJXcIVrEv4rV2pjvpROhfd+i+sTMhkMBjOWJfg/AP+eCU3WhbJY0w6bYW7z1V+TneAR4zITxXo47Cagu6AVaNSw5Sla6T1BxTWIORpjmsLlF+rtiBkOncgubZgImfj'
        b'uHcPcQp6zb5v9DPyqJ70c9OkMHDjhtLQWNKUF0B+iascVimgW6OTEmfP8vDEIvyarDIM7CwtKykoyn9hE+hwohMw1+fDrNPXX9kBWDWByDWb4WAkOq7rDX9PrpJJVXqw'
        b'J4JOGrkf7IaXx0FnsCuFxp2BxgAaDCcG25XoALsLK8ahZ5aaBKDDBX1wSBHQpgS6ZZg2e3igQPDramYpDj7j5fPhrgOe+sBDk527JKFQ9er2B4YB7xzWUGcpncirS7p5'
        b'wq9id+Tnjarb26JMRtM2NHywefW3J9SMtL+L+uzr7x8NsufOPJj3Te7XHw7/88jmJffE9xMMK/OM7X9N+fSTlOodQfO7mbmG70Vc/adZS8q51B39Ti7v7vVmNf2ZvyM7'
        b'8I1lG/9WMJyv4Vq7/E9hv/7yReLxSgfV8MZwQ7fwyCefsD56aPvtvps8JZp7rYbt4Ny4YRqeIC48bXAPba/cBZqDZD48u/PHPY0r3ebQydZuwFbYDS4kK2aykzG3XgsI'
        b'2+RvCzufZ97c1T0Q7+aRSvhbPqidj83btG3b0oyxyBpWv+akYVNZC+1ysiPHmYsZz5GxyZcJe9FH0W4483L+gBuOsZ04ecTYGRt9zIXlUo7dmCNfECY0u21gd9dwxl1j'
        b'a7GTJHTU2OOurUefyYitv1B1zNH9jqOf1NFvxHEOvlOKjgmO6TDHfsweP2lSnzBmy8fmg46gO7Zz0AkzYhuITsV0qS6XJHAWh32oy1Pw5tRR8KYZp6F/8PQo1Zl6NNBn'
        b'wpv4TPjtwdykKXO8wadCcfb4qfAqB8L3uEeMj1UqCtZiLef/ac4A7O7cNdVjpiR7ZcF6WeRRWSqWSbFOp6H1obSisXAT0UwWrFlbmIt1q7k51i88F2QD8HwkTVT8Mvl8'
        b'p1JWdgJBja51MYklYtQ8uP3FsOwVxqoFLmBXwZG/MZVKcXyaqkoNHCuEjkCU45ldW+51Jm9nX+2Ph1fFpGW18+qOxS0q1NT0uOTwtv564b1VykKTfDPqG4naBu0feWwi'
        b'gqWbgmZCjcAxcE2eG705lkbvDIJO0KgoZ/PhDiRqg4MVhBxlQ8k2GSVCD3UoUiMd2EXHtLsKBUuRsIVoUT+sc4U10XB/DhzEqtXo+HWyJ2JBjwroy1z720kZPtbNoudY'
        b'vrBLx9MkjBtWnruB0BFPmo48Cs5lUAZG4xZgx1GOMx1O7qbjON24Z8QbMeIP6/KnJnB46wXbd0oCh/eVFRI4vKhlIk2FBA7FOWhTmr9qPHLSupIzDKz/S0hIjkgo+Qk3'
        b'V/d34pNPBHrDkVhIfATiT06c94i9ijCahLKQvvBM/2/FV1PquZDlUzljezzkz8VF1saWtVR5FHM1Ld0nRjiKuW3bhlEt92fMGVrZDBy93OMR+fo4SB68PBoHL49lkOjl'
        b'sjDkOFa4sV9N5A+qOlo+j7nPRQZ/qGUgsh3VsvyBqaVlhau0eoS/PbEkr0MXvmOq0pHS0QX07YkB3Y7SUS3+M6aJlgW+5PIIf3vigy+ldnlfsr1rZdtl0B/6lMXQ9rsf'
        b'HDYWEPyMtYWhZfGMwp/fKaHiR2z89ckWFn4ou4vVn3TJ4NLKYZ/IUa2oZ8xEcjP+/I7+RLdFMx6R8icZ5BnbLk5Xcr/TsNOcN8JGtaKfMY20nJ9S6APfG4PuRV+fBOE7'
        b'k0a1rJ8y1bVc8BWbx/gb7X+Ng5P4gSpwno6DHu0yB+yMhhfw9ziM3XJyVFpvCuvLn6AVBrYzQBMiMw2BxbDZQxexhBfhFUPfWaAqG/Yq+8MaUA8aVMFeeAxut9ICAsQM'
        b'icFp0BgWBto1QAOoZZjD6+AivK4FRP7wPDgAzmWBC7ArWYsJz4IdsDcwAFwHfVHgeiS66yCs3QQugi5w2m0L6IgDZwO2wGuwUwX2gW70//JMcBJ0wFP567zsocgTVsG2'
        b'InAc7sRKOti8JRDsA6cQUew3jlwXkGgE9tnCqtDKVd5wP7wGLhYEwN2rI82ssswi/GOVFnttdksEHYstXEEjvBAALsFOMAAERaAb1qNqBqPAoN8aZ3jQazms04KncmAf'
        b'B7G6YtAA29H/K/BIZig8Ot97FdifDc8og+NgEO4uBv2wHh5PgmdA34Y18AS4XgmuwKZkUG8K21cvgUfACV9DeDYKXPEAdajv9eCAXhjoTQI7HGNRAwbh0dmgtxL2LAAi'
        b'BjwFjsLt8BBoQb8PrgQSeBS0b7BkaYBDaN5avVxgBxxcOVs9AF4Ae7ItQFXkGrAzB1XbFA+u8rIjiq0iEJ8Nr8PmGHh4sQk4szEEDoFzaJr6ApWBcAFvEer3PnAY7FJ3'
        b'SIYDJrANsbiHwcV4sAe0pGE/IdDkAi/ODrIPtDPgwHMpqKBls+MSPhTBbl0O3AMFiKUtRaX12jMj1W0Ql9uJxq4f9KIG9VGwyTt3DhRlgGYvcFUftmqviAcH8suCYNVC'
        b'2GQJ9i2fpQpvgCELDhgqBDfMAeKbO8HptXAvFHpawPYcm5T0QHfYiFbCEDhVmoUW3RF4NFnTNKOiaM5meN5i6QxwNAG0my6BvWiEmqBEFXXnPFpRR2F7MKxTBXvC4WUP'
        b'NJFHQI8f6udp1L6LYEcamoODrnPRgqjdCM4Zm8NaNEJXoFh7Kwsdensj7dBMl+9Dyz4Dnp0Fji0MAQfQqtcEV+GA4ZZgNL2d4aDKErRAoaumDzyLJqgfHGeFg1PZWbY8'
        b'IFjJBvu429zBydnlFSt14GG0FtuhBA1t3drMVHDNMA0cDQZHQT84AXZkwRZn2MR3QGLSZXCRBfrU4CFzOJiltBYeA+cXLd4wFzZXJhWCHtiMxuGaE+oEWiDwTFHsHFTF'
        b'cQvQDKvnp6G6G9JAky8Qgj0r0M6rZvrFwwbQ54ruOQcloLtySSVHN23bCp/IfNiit8lHD55BPd2HVvIOtCm2z0S7am+kVZzdJge01g4CETztidZ4D1qbQ7AmCzYUgquo'
        b'T+HwCtirAk8GwYbNoLU8NqQAnnGEe5yQAHlji6/bNrB7mVoSGDKxxEGrYafebHYxvJEJzzGhYKNRVjjcCQbUQd3WKCCE1RaR4MBiUAV35eiAViBJTFrkla3vYAq7QiLV'
        b'DfTdPJTMvRehHXQsDtYkodkVwm4TDDsEVVnw1Cw0jVfAdriLBRsSQD3s58KWBFibhuSrAbYeWnm1xqAddQNTpV3LvfDIghp4GpzfsNEU7LdE7zuDFpRkI1oLeyr0VNFu'
        b'GMiDh+ClLV4GoBGN4U40N32Ial1QzdeOga3+sMEUMUni9BTYg/bdLnjRaim4Fh8LboBONTvQUIrBv2C3Xy4cWAP3poFrbmbYmpCRCC6aoyXXA/cvBA2xMXoZG+AF9MpT'
        b'aC0cX4KESRFGfYJqL9jDcUyyM0wE1WjMLyyGJwvR6EkSwTkeHFICwhV2oG1rTPkIE4Mz1y5F6zEQHMTrEbX7Eh+cL/eDLRlsVKkY7izKAuJ1GmhbNs2c7wJO6WbGgq4g'
        b'UAcH0WhdhU3maB1dB7Woa+dAbzTYvQTt1V028FpUUFAgFMaAjhxddbgLrdeTaEVdBDttwVHuerSAm5hB4OomapZbNGxcXcZH0zYATiHeshZcRvumAW245hVLlhYh2tHu'
        b'AptXoeG+gv10atFK7QYd4Ag8lBGOaOINvnFq2dJlQByPWngC+5Q5oZ1RP9fGayOsM1ADlxTXK9odR+abonZc2JA9F+5wVdsGzhcRgnlIexMQIUp5KiRuVoV1NuhL2LzF'
        b'iLUsEuwzBtV5qGs3UBWnEGXaMSsIrV+hyhqwH3QuB41aaJK7uFqgcTYURQFxGbqlGuK+tMLj6EjqBFU6TLgjEFGQk4Yq4OJseNnEAS2Hc+CyF7xusAF2FBluYq8shFXg'
        b'MNqvu+EhHTRUJ1AHT8GrYGA+msx2PVi7eMZKtNp2wP5gcAIN+tUMR3QwnV280QKt3rY1gVCQiY6vJh7o2oA2RJ0bmoz2EC9E4vaidYmOzQyf1TNhvdMqKKmcp12BGrgD'
        b'ndEH0Xoe8OQ65WSR1HcXNQ1gI7wMd2jCmghw3CsZrQjQtgk1YC886AQuYKclxOnDdhVzOzTMV+CJiMXu4DpsUY9wRh3ejeijGJ3ZzWFgIDJ/IZrKAbC9dDH2LkOnYSu4'
        b'UgH3rQfCpSq58EhgXqQbOc8Pxpahw2Z3OaIJAnTPkYBI4zTYBJpXg1rmehPQghY3GkG0uMHx9FWolTdgK8u+OCYC7i3SgvW5qSozlsEzZoiLQGvLHe3n9gg91F1B+Shm'
        b'L25w0XJDhLaIcBdXYS8fDjLCLTOBWAWKFqozQD/2FTuAtowQCMrAOQoRWztDWOWJBlhosRmexeH1T+RGOoGjoaCHg46Co6bo9gPasEVljcUqtGiO6qCtKPTiweuL3KJA'
        b'84LN8JAFqIux9MVee+pobK7DfSrzQVcm3i1ZjLUZmBM6VgR74ZWlqYheYPJ7GlEBxH4UzwLNnGD+Qn3YuxjUZ4aB7eHgsi4UR25bggZG7LuZA+qS4haDLnt4ftuM0ExE'
        b'NbrRfPSsQaPSA5qXbGLAIxHe4FKyx2btUFgNmoEwKBsdy9vRJLeb6KHR3g1PsMANPdiwyFjXDJ16tQZAsDQuKxlt3WveC/wL0SZuTAONbmBHnIG7AZQUgtPBaPPVrAKH'
        b'HOD2UAasUpoPLufMA4cjCsBAUAK4Amrm+YWGbzWDIrT2EVk8id63h1qDDoB22K8MxGgT7DVCm+UcGqqDsMULXAN1pmiXttiDK5VwcF0QWrNCdMwdgEcC1sH2EERRqnIW'
        b'bAS7I4vR+hdXgiOVhmhVXcjZBLvyTaAQEcA2RCZq58D9qXqzIFruAngiEnFFaEGf5PqiNhxD3zqCfTdG6qIjMcwMDCShVXgRnN/kg/b8NdgdCuvQsO1CB16rryXmxkpA'
        b'XR7XEa9EWG8wl1CCdtTMKnC8ABxZoVexPh62oLecR7uqCTQUoNZ0IW4ACb0HytHA15luRt1rRqdnDzo0S9Owj/lxeMIkUSsJnROdq4xgWy48HI3m9xS8kgGOZaImng0C'
        b'/195XwIVVXatfYsqhmKWeZRBkBkEVEAGQRSZJwVEhpKhZBABC1AUVBCZUSaZ51FGGUVGiXunX6dNXqJt+nVLd6c7Y790Oi/Y2m3SSf95+1bZ3XlZnbxkrX+t/Gv96Dp1'
        b'695zz71nn72//e1T9+x7h2y4yg2u440oZO18A1ujqJXKxPTzrBPC0rO6uJBL+DKP5WZ+J+VxVt/RL8IQ7+QVNJFiZ0EPoUVPJPXiawphg8ucs3iTKISnqw3c2wOz5xUs'
        b'3GRFRGDb/aKx6RD1Bvp9aIw36OILIpLTEotBJ0yhwhnLHJOozU2C3tncIk/FnUGwgTPJ2Ed17pA9tV01ghKbaBrwZZ4rAWErrFjvP4iTCUTRWnBFSPTyJvmwCfLQd5Fg'
        b'reyqHd5SI7WtOpQA/YHYGulNrrVB6A0dUdbEOYZh7QBd7SaxkX5YVyHr7oEBVRz3h5uOhdikHGKUdpawrlSWDKS3SF4As+YHDgfreCqRjk1Bi7KdIY9k1iOv5oaLRrvl'
        b'uH54zYTEWGJOej+yQ588/E1qczoeyxLglg8QMnmREyRwIoaAqwLsxl73cwRYLXCbnMkw0fxZGihOuF001Jpnk5/ugqkwLDuJg/EHoCbYNoTEVgbVvpn6YUcjWA5Tk3AF'
        b'RpOt8FoKlKgXGWMbuavGOFwSkfK0RuDkKayy2wNtUqRpfcFY6UP6tUmoPp2WQAFJAyF3ta4OiXjxFDa7YyX05biS6MecoMKL1GYYGx1jNU7vdwtLhuFTuJwTT7Dc764i'
        b'b+7soqHrzD7HsKiI1eqHQy3IGW6aQ3cUtdqkRLp1/yzUREaTkazGQ/9uGNVIw41UnMuma3ZRT3sSyRpG4oSaBEBNMG0PMwokzxpsS4NqI5hPyE3UPggTWVRpGjpOE0R0'
        b'cDPpxkqOkdIvOkO9J2xYkMddwetXNfA+k4VdNsSdJ7Gu4G02AZ0umRZpZWm2WCk3SCkLcVKIYxfliPiUqReRDEt3GxLDXTTYo4bNqkQlYyIv+UPDVSPzogKoSNIJFyhG'
        b'kg8fYv9B2T4C/1aCEjrNkyVOxapKMFVIY7uKfdEHFchbLsGmyikcwY5M8ra3pbGkAFuOC2GjKJsOdSUnEJm5I+YPQPxhDTYySPsXknWwXGSEI5akGINkO5PHs7Gx2JgA'
        b'opulu+l0A1WJB87qKNAZjQQerSSN2pBYonoTl49djkkvNFUMRWKsQzhiSth9O95qj1ehMom3FljjbYDl7FwvNVhSySdDKRURp2g4EerMN8PZ5FC8Bq3HqMoSXJfFCSUh'
        b'VkXYsM+JXIPKXOhUoUDlOvsujXkBaeusg6JNIGFUR4aqX+ZFLwqeBg3JSmcIcWr1LXkkzZY9xDgbtDXgVrax0REy1ylDXDlK4HWDopNF8smr2ewKR2w6Z46juyi6ncDr'
        b'l6HT0o4GalmWLlaGo85Hhc6FJvGnydBLySDKCsgWOuWhyRFvnnHGrmBzMocF9R15yYSB6zhxEicSyHKGTUgLu10Ihu45QyUu52bDUD67Eo9CZe09GoSZbQcJ6Bfcd9Ft'
        b'N6TDDWIN0jgWRe6yipS12esM3o3SxXIe3MIZIV23h7Stk9l1wTP3ZJ5WOI3wnKm1eA6yMTUfur0KoWYXVkvHY20mdHhQ3XlYJNrZhtXR5ClqiZp0awQrQ1/g7qthpKFT'
        b'eOdSbBaRxbZjXkdc2Mhs0g1GfETW8XCPlKo+BOaKMjROEwZ1qJCCL9rhUETxUWz2s2Zf0qFtiqUOwZlRJLs+uGYlI3lqjkLQ80EB0gzHwSuRwRpVqJE8r3lLJiSIfXyH'
        b'cwCGHOgry/okZwzZRAfZSDEc7/hIhkjGOI5L9jdF2LHrLTkHj+ICe2AoWdLSfZhVY3+J4TCcwF2wwWDXgRRx+gdTvHUUa21pvz8BTS+DveFhBUe5DKODM+dJRs14g6yi'
        b'01uRRD5zRd4ojg+t7pEqSerkmBrtSRMGSUgtLF/fjdcD/EKgItNLy4qg5h6O6LLr0wagN0DVJ47QuwG6k7Ge6AqZL/btZ6dbKOxuLLQv8IUJLZbkXYYRYRJWKsCAKIls'
        b'phk2vaAkJgJbQmkY6ThZYvkR2hyG2wzha2WUGjG4LgcarR6nk2ZsIhFDigbmrGOp3XomjK5ZLiRInSEP3EzDTOFNRjFU2JN3bTwODbspUJgnZThJ9KVxN0HcNDS5UYxU'
        b'ni8IgftBpOnD5CRqSafmDSheKqOwrMrNqhgqnYm7rRJEzJI36IdZE+LCY9DhKnQ9z8V6WaEKtu+CQf8zML4fl0U2RriSiJMnAzRhXLa4QBgiEhCINsIwn501gHYDXSwl'
        b'2U4SGJUSOo7Gn6Tm6kikrbEamWSyK3QXDfuot6OeevIxitibckocd3VyscyJApkSEsw0Eo5uOkEdF2djrcOcsPwEgdqAO87uJrO57WwD7LLYcWhwJ0ZUT10qEWkX8Mg3'
        b'NeRRN4Zh43Ac0clmqLGGXlmcysAGf2g5iP1RRHLrKHTZkNXE2lMmKVa++jglBy2noEVEZrJhpVyA4ykiEY7Sv6bLSnS71fujTxBsTxMUNzrjvO/R4h2nU+GupRIsKWOf'
        b'P5nVNRecdgggyx6HCmRndqpVKH5fhFI96BYQCkDrQf+ToXGimJPaRImqyJGvaLviLZGDM8HE/HkuocMITNlpwWZBOk66UDDQYK2OndosjJPDq9xzlWz07j7ii9XsXJRV'
        b'6GlyqHDPAbrySacq4V4cVGaTDx+GicNkvdNBV2FawKYIolGdDjwgnnxZ55KP6YtLo2BqBOpdtPWv2BDzXAxl4whsPA1rOLiHik3cMNaCVmGebb4OUa5JL1xOVMJSJVzn'
        b'QG/i1TgcUCkYY8OFHsKLO389MUMgesfL2FvlPE5pyehdwIFUso7SZILlufA4rAnU0PKhyGUT2kQkzAoFDemTguBIaqjBWY8UpxVmdHHUUSfIxAMWiigeqDyhE2aX4iNL'
        b'Pm05Ilo8QzMfZkQX6YTm/SSSdXl2JXo2YdIgOZSNdFwqgCUrmIFaDxuyjVHszqYv9ef3Qif5NAKoBlZRh2DOGu7sySGy33sA51PjSMwVIdHaLNtEQumRGA7xvXWy6lID'
        b'MqC5o+TienkGeNuGOr2AQ+rRKXowZsomnIEub1EwMe3eNCKfZd4sus5B6eUsovj63kQVhnRV2ImtYLx9Sc1XHibOJhAQ10kmAvJSyAIazpjTjZE/w4ErBAYrBmQIPRTl'
        b'wu2QRCYTKw9lEep0Jx5KI8ewgN1CusemfPLDZXQG8XLsSUmFmaxwF1zUVoX7u06SMrRr4IiPPSsTaxzXFuJKBukNy/QnKHpYF+FGorSHKnboO2JTWC6hWp06DqpRBNZc'
        b'RFyqBDbPEdlZPAjjO8IsDzqbke/tx5ZYORw4mkNi77K0KNhplaEVflRtB/arXy04oAQVh6RCSecnSAGrYfQKAcFAQbQ/1MYR0l6zgWUNIZnlOtnF0uWYs+Qqs+EmF+fo'
        b'+xQRvZWk84S33Z7FJ3Ak1o6AqRMnrWDtUCJMG5kHECg0s0NMw3CfoK2DwGF6B3VjAzevhAdTo8P7oOms5tEwuvaqPsljzReWfQiEKwXSpgfzPWGh4C1S1gvxIdBzDGu/'
        b'Dm1j6No3oG2vERvdxkYqcOCuGlaFwoyMHUzHyWjBOBIGLu4jLZhxi8YNqLHPcCP9bBRPmUyY2hGGsVN0HTtsoZwgjRS0AmYpMsD7F8LsrGiwJnHdywfGDaBDxUCPRF8H'
        b'i6lkq0MHPRgY1yVUmTCHDjcsMSGkm4epE9gXBV1OsQQ6lQHQnRpLLmEmmiUngzgQK7KQ5qZ7YKsDjhRitT3M7zqOZdl7YDjzELmFYervbeKs3X4EN7ASjDW2seQ4uqzJ'
        b'mK/bmcSk44iL5kkR3g8lVWsl11G+V0MO+jKzYZawq5euMBsqSzawmRtGQXsjaUsdDF+iTpOz0sNRB2gpIHfSFppJukRRS5utUjbp3zqUyxsfwGm3DGwP1DpL38cLsMsN'
        b'Vn1E2Ebyq8fZ6J2weZxxxetKcrjJpTutCNGEFWl2cmTIDUbTtPyh9Yi+nhtFXTXULZx2JxxfJ6WYISu4R5qwcY4C0Cl1EnxHcgprOafTLQlWb0jF+6SdU4S7cTiaGRaa'
        b'cTqRiOq8Mt1CJ7ncSXmcD4LaFGiLttEGCjKu4Y1MxSScOg716t6nEoqwNzDE0BEb9+CcYXo83nSWYokroVA5BdJ9uB5cWEwSqE1WJd81gPd38syhVT0SK1JOHE08FOJH'
        b'Fl7niS15rqm4YkqIdIeGtZZCQxkBwcOUQqyBGGJY3L5FwmxP2QtzeNfUiiy3HYcuksHdhFlLIia1O2TJPU7kntCki9am4kb4ORqfG0gEoYEPS2ru9oRpvRfVr6pYkHV1'
        b'ENzct8UqAfS6nCWiMh1e4Mdl33moSGP/l7pNse0SV0obx7DRW0UEwxoymRaEuT3UmTlCxFZHTuDxADZ+SsHlFFxQIsO6S30fsHVXxgaDk4Y8UvJO8t51xOCnLpG0W/Ye'
        b'50fBnf3YeYL0u5OAe1WBjclh0iCKxE1RNdzUwvJjfiz3UafGpgVGMOKE00eskQhNIAXiWGsKffZGZJ8tHtClSaLpyiOvc1sIcycMSNM7pSL36sOQrhuUJEO1A1FfT0JD'
        b'oygrfcKJpnQs48OcUHSVHFcZLMbuJ5+yIGRBvFY2P9wZxhVdSMT12KEjICGtqOFgmibekbO85ONxTht6XGAmuJiUaoQ83zB26OJSfiCOqxHVqScnupZOvuCSvK+IxrCX'
        b'Gmkydc2HYXeeI04fNIMxL3nszscp1dMJOjC6Q/UcNGtiXVAaNVQKt2xlnUJoPIlmkFiWecYhud4ukZl4x5SwYZzMqPuUKW76EXa1kTluQk+AjydDtlFD34iBs6k7YEnh'
        b'NFbuIw/N5vnwhVk9PocA4Z4gnpBvhIZlmVou36EZQ478BgzJwfV0qHDDcTtyAVVXzkOTazyyM+WDDCwkuusTrKxCRYYFmdptHRiwI1vvIKuYpcC6+xRfdx+uaUPbcdeg'
        b'3KPkQ8dgDKd5dMo1WDDWcKOgYwhGfWBC2oCsqRs2zTV1ic/esMaGYmxgxVN9Aea5ubvdaW+jBwxaxOAKOUts3WHmYYa9rtAuPEG6U4WtInJNG4VxOLPXIwrKsvIJHW/Z'
        b'M/thNKlQIzmZJJ+VjmtwIxlmzxGDbiQCd4N9098BAtdyMzcKClewUnQg6LQnAUEV1hTZkYDnFTmkfROstnfRYHak5hVehuUw+joEncEUoffBTK4/3okRO8ZFXPOI84I2'
        b'S3KaFP4e9cTFQPaFjwqpjuxr/WLJOjZlk4mulZgSZW0u4JIp+eB1Y9aSSkmhWVPawDUbguN20s8lN1zUIa57ApvlM3xh0gy7fB2gkUsOrl+JreGpmkHx4npRmr8/sYGy'
        b'wCg3Y6y4lEMUewNv+5AGzEMfH9f3y2aR45nk4MAxXDW/DCUU+bXs9lNROIatqeJf1qbZmf6rRWxmCXZGawhWIqmLZCij7GwREd0RGPXXwo6LkRYnHahzLTjhgaVX8Sbe'
        b'NSDnWBUPfVHEtu7ayaTnOOnArL88Wf4UVbzhRHKtyCIr2FDB/gQoJ0IwS+7lpiM26MtSH0f4dninOJ0oYEVyIVz3JK98E/q5OK/Dx65oHT8dUpcpS2lVQ1w+GAUNyt5y'
        b'hJqrWHKU2Mwki2n78A5D/rsF6/coC8OhPC7I0jU/Ux43VGMuWRDAEyv3OkuesSQc6nOx2ekYhdUsF11wSy9m8x9awOyOA+wKpwFtWJWHpRMXs6xxzJyw6x52QXkirhbK'
        b'Y8WRY2QZ5RScjBHyNFLgYkICb9uJPYry3NPaWHsyMyNB4IydQcqcI1p03jQ0ykDTDm2yuGa4l6kYYOOASzvZGVBy3yWwrgf32B/wbhsYUuBXl3zQkxh8716SxwDcMbTL'
        b'hsbgXWQXN7HdP68AOvbSOFQE4F0PBeLwa8QOuo9c0sZBxSvS1IMmP+hU5xeTyTXRt0bYtMk+dRF6TQity9Rcw+CuDnSrungqXsBrgVhuIJDF28ehKR16YZIU6WZkLDtr'
        b'ircL2EkvGvs1AuBZ8hNlOGyPVVcEJuSsiQZFU92eUOrMtRhcumRP3IxdiUIWsgFVCrHJBSfJJPuA9SdESYf3U982L8OtndgkJAi6e440ZvqCDinW5GWsvArVBObEP66d'
        b'gDZbmCv4CZElexy2/toOvNmZqfoYcsOEYpkHjSNVzLCBbCDGrIgOd+umpfB1cFjX1YwGeBPvpMGUrP8pusYS0aQRqf24pA+beNslU4E6VI79+cD+AFx60gOaeNCqw9KI'
        b'C9gRBINc2hyFVSH5m7ErhIz1ZE63aCga5XfiUCCh6SRJvg6binET1jw0sHo/rNnhoFkI1maxP3UFsFNVqeEkm/LdhCnVijycEOqR5i9eNCYzX3EMyyF1G1Z3ontr2qOF'
        b'rbuMrLBr9xFiDGQdvqQLGxrpeFcRO91NcESJAsfyeCjzxRVvmOQXErw0EwVqIWgeYpMurcpAj4E/tClQjDCyRwUGfByhw5nIQrnOcU0c27VXRgarInyxWgGv+YYnJhPG'
        b'rNkTz6p0wzmVXLzroBjkBIPO2OxzwJvEsgCdPLL8YUL7ikunjFXZxagrBAYrUGpMuj7NIXZ29bwjqVtzJJQriLViRUAAvnlmN0FCN1bmkNxGWSi4u4fYR/PpdBhyJX1m'
        b'5+GbsUYbF/ZTaNOYBlUyMJhuDGM8mPE6gEtsgI4lEYRgi8EXyKffd5Yhaj0EdZZYZkuimdGCwcvQtoPUssqU/TlZulhmf9pxavmWhzK2En2QucCSoDL1fdkU8RGlv0Yo'
        b'0Qij6thxWLuQfbDiGMmuE1YTz5vDhB2s+8GQlTR0mBDB6joB42co5pmGITsBUSBy3fsP5OyF1UCLczhoDu2BMGqz5wguSJNPaQswocC2B+cdycONsybScUztsDPR7El7'
        b'3IwyI3BrizylLLh8XC+WVKcKS/YF0zXad3kaeV9miGBWnSE1uI+DVlLiLInRWHrxVZJEFayVwlGONXnyKvH8kZQpO4nQn+30VaperA2x4kreu7AZgS1B7NSSKzQYM8TI'
        b'oVxyYBJnrYPYJFycPbjmyGCdc6H4gCWZ2Dy78pPHcHwP8OmU896S+atZAvYmyRSZnYAhRlaJLa9efobV8lAfxL6SwQk78+iYLdySHGh2OYK1wXSOG0XTDNYrYKf4gA52'
        b'7n81r4YTXmzKJSyzkqQlDaMO9GCtFZ0URsO9yOAg9mSJF6uKMsKpb+zc2m5tBhuj/V+lKhadkczEWUIfgx2hcNeKI66vYoDjQYHUkE2mGYNVUdaSVJXloWQHr2bizNwY'
        b'7LKAUSuOn/h9oeK1t6VFUsz3ktmHm08puhwzZKy44t3lMlxmb7x4d/BZT3NJ4t5xCymmOFGB3WkbrG7OhFpJhVJT4pW6GaPzSry8/yKQivHILz/+RuS73hoGT+eznhbe'
        b'e7B/f9fTl5c/eLmP/7qBqP/jljGze9cD5Y7YW038KuCnnQ/LD35o8aTJ3GePjNHxj6/MxM2k/dvztECZEWvfyOYk3cbVuoftWU3nOhoCOpoyOhpjO5ovPrWNS/XREgYs'
        b'PZyf+t7S5s8u9NlLQfyeot9p/vRP/n/wsPju2/+uF1Rq6rqplZ/5ZGzjWeaw13/N2mh82vAkYSW3UbXgylaU3I+2W77cuRLZrfz6j6KvVCfwPM1/3furtsE/ekU7vDbV'
        b'rzu8+90Hge3NfXsjXrofe3C076f7tqvTfi/38vn4jv7fh3w3c8gzlNl0vnZr+fG0x2+5dtvyuWqu/+6jzx151PPZmYx+g/AfjgtLnPKZ937w+ndiLeN+rVrYHfdg7Bb3'
        b'yacRJ8xzU+J/pjtr8tD3bQPVomu+H1YOZN2vDq+9KPrdnTpNpwvvrXp+xqjkdS7k6nzkEfbcdjT2FyFev1DfFSKdXvuytPPTn4ScGf/VzZWPC9Pf++H77/38i7rnGqNj'
        b'brbP9H6Hv/ze98L59tNhCcUuv40/EfBBxGvxehYXtWIfPorS+7gz/kjzl0d+keV7oej9qXNv3+1J+c+6lDeHnc/I/Cb+++9d+7HKMfc3VpTWYgeVXc9fuhn9gwSXtwLe'
        b'f7DadekHP/L8qDDLXfm2383V/plOx5xfftnxwiL0cVt3nW0B3v5It29ss1mvsvHO62EuoP5n4dbPPF+3CdvoNd7+eDJuZM+Fp7dfe+sTvaSPX3ezfrIj5oHKp6o/KhPI'
        b'HCw51gb8332k8cM/Goc/vmx0bfDQ695D66Vf6vhNf2ih5PnQ9cGR4jRMPLMrdFd7+mL2YNXMJ9/Nivrz1H98PsVUVibEXVh/GP9TrqtWhuLNn4cZXpXv7A/oHMzoHIjt'
        b'XHuS3quV3tia3hFtsH5J2/VJRkFc8e8rrpT/x3b0d+I+NP35l09mND+SibvXF/b0N99x6r1nHvXIz/eXv7J5OF3x8Lcxt9yVWtYcbHIcop75Hi9P/uC1HIdDiUZHNvRf'
        b'/HT3huJ97Q80v/yTkWVq7MJ5Pyt5ydraYWhjV5cHs/iDZdIM3uRnS96OXYMlh189Sxyf+JdPEmvBhGSRbeMubPsfr0Bzp3jnm1W26eHiN6VRqN0EYwoiJb4S0YJaFVGB'
        b'Ivnye1zG4BIvBDbkruC4eH1qxCmLrytdwKULZP7155RkGB1vLoVTMCBujMdj8s4rnivAeypQA3UqckqX9eRxVuW8NGOlzGOnNA1fsO+3g/59in9VUVwNbrBNs82G8Ez5'
        b'MrCCiw7iVSCnAuG2AlWiqOGGpD05vC3lcEzzBfu0MuHdQGQe3JA7R7eXR56x+lsapDh1BUZl4D5h+gsLMbQT2W/+lsx4r7LiyWdI8x1hzSryr5+ylft/qPiXr5b91z7r'
        b'HMmIl+p6/52/v/ko9N/+kzw+LycQZOUkpQoEl77eEj8f/xsKHf/85z//qYTZjuYwSprbPFm+9lMVtQan2gvtJjXFHXn9Tv1JA/u6Lo1FdF6dM5sVLZvMFSxHzBUu2D84'
        b'/D019H/TKfg9Hb12p/akjn1d/P7Axzr2s9qPdVwfeYQ+1g59FHn8UVT048iYN7Vj3tMy7ldrzn6karbNZXROcLblGTWNBp9GzapD2zKMtmeVwjuaxo92BT7WDKySpz06'
        b'1m9ruzzWdqlS/NDE+W2Tw49NDj+S2ynedn9s4k7bn8lw+e4v5VX5hi/NZPl7Plcz4Ot87iFNW8o8/t6XinJ8nZcaqnyDbYYtdjO6+lVKL3l+HHYPW76MlDLiW24zVDQI'
        b'X7Af24c5jLzqS6kcKb7bS+ab8lNx+ZxLB7fFB7dTpWn7Hb72S6krXLoW8035XFJSXR3JCTz2+/YhOcZg5yM5nQ/5KuLT0qT4up8zbPmXVdnv28epbZ2XUqZ89xcMFeLj'
        b'2+zXl4Gck9J8NkvUt3y8kHxsX5IXdyFBlm/2kvmmfCYu+w2eiz9fdYXd3PZWEZ8QKc1W/abcFpftWc/Fn69OEB/IlFzBW4at+k35ubh8VVG8208xhsM3/pRhy5ciqYN8'
        b'necMFZ8fkuLw3T6T4fB3vZRR4utsG4vbE0jRkDBs+bm4fNUSu7l9WFpcJUqGb/uS+evyU3H5qjq7ue2tZCHL2z7O2U1lJEeybUll9Ks9tP0sQ4bGRWrbX86Kdp34H5X+'
        b'qnxWIHOYJyf1LEguSM5Q6pGc7vMTqoyaSZXPu5oWDZz3rN2XfR5bey3nP7Y+/GNVk36Tx6pm/RFvqlqQnmtZ/lzT5H+rY/qP1TH4e3WeUR3DZyp0W7/f9s3ncPgBnKdq'
        b'RsOKj+z8nhgffaLm/0jRX7LYud9HJ1ie+YG8erDhq5Rp+0Rrf++tyv8fFeJlOae+NU3CP4KzonfYxShfQ6zNV7D+hxLm5TEOh6PKLr771oJdpq36zyR8Y0fygZSMjxrz'
        b'QE3Bx5CbUdbeKp0XQOPYF3lQ2PBGINdHtaLoc88FM+fqgPeqDsUT6V1eL5d947Kc6RNt/nfLfnL9i2OFmkbQlv+JmfHoH7e/DLn6VsKPP2rY++Ybxs2282+YtHmc2vup'
        b'VX+DaWZ4MH/kVkTzyVvHnpkHTmu0FKrP/OwN1TNnMu+8eW/JuPL59huxLkFf1k86jNkluqwMpJ8bTc9bGI1wezMpZvUT//q4h/tsBDJZ32+YFp79bmly2a7X2hVeu/68'
        b'M7rlYd2+p6m+fzj/VpPbH63dC+zfeXI95ndffBJ99mlSwvsXo2I+d416OvOFqPnnv7wa1+3tq2/4n++UlNoHv3hUKa3/7jsP7A2Wdb6DXsWK50p8ea7geOiw6wOrH+45'
        b'xP2o6lxpULyJT43i2+mD5frv/UzZreaNMcWfJOz/6FcbOlW/Tt+34vnsE1v38SLD2vrKjkLHf0se/XLhyke7bj1bdlp/Q0V6f+aha2VWRuJVtWYwl8PGwGFhJ8+LE4TI'
        b'MgowL4VjsB4pXgp32RCqg8LssBw7cY6txy5+2YHrXBhwIAIrzrpbG4dd7PtGQ6FekhOZnTWWZZTVuDtlcUCcYiYF20LZ15EKwkNkGRmelJwcVIsPKEKdCdY6yOAMzjKc'
        b'YwwOZdmImaSCs7IN3rSUMmSzm9RxGD7FeJ3EDDfE6WGuYm24mC9DJ9SwWZdCOTCLtbKv0viehvtBQn6AbYDdqxzMyljDZR9ampDQ9etpuBEUYItzdl/lwkmyliT4XTfw'
        b'Ebd7Li4kJABvWAXwGDVs5sJqLs6Jr8xVweWgQFvs9g3d58xhZLFJSoYo66RkHfMUxQHDQU7OMXCbzg56lWPahOtOd74gqbJMVSqpCi4oBgSESGoo4x2uI3RDnySH8DgO'
        b'Z2KtNd6EzatYz2V4ERxYw9Ujktwya5bs76k3QqKwjjg6z5EDU1iTIk6okw21cjZ2eKMIK9hcPmc5sIx3LcXXveSLgzZsMvFg9pIhJBvqmUj/Mg+u4XiReFnk2QjoDWJv'
        b'qQC7SGqs1BWspLABrklJYpn70I0LeWyNg7tfVZAPkIJZKIVucabmQ9CoooDzKnjXFlrzoBrv5eLiOYpWlBjGYBdPln3MRaIzkzgDi+KloTaX4DrbJJsyulMKB6EHRsVi'
        b'CEf2Sdza4EDxiglxlnAOdEFlrjhddgGJqy4Ipi2xNJWGmU32LM6BHxYANxxC7diX/RyRLVY0liR9HoQRZwWcxcUDbuzbnBoZHM3FXrHM4qSPse2HBF+UDiMYKubg8F6s'
        b'kLxrt8tTkz1mx77B6atFnTh/RK+ABxVYaSNe2n4Iu/RJ5jWHEtkU9MFSDH+3lPixtTbJyvdeityGbALtbGkIF0Ps7DmMoiZXvghrJAaIpTFBNC4JgUH2dD4ZEN25ujMX'
        b'ewOKxUK3lYMVG39baxiEGTZPADso2MBmWO/E8hdsvjMDtzibQGmsimM4QQy2u0Op1cF/RQD0L3dw/5fcJJto5G9EKv+cw2TXprIOMyM7I/9VTPJ9ho1J/k8J89yAkVZ/'
        b'R0njbaWdj5V2dhc+UbIs8XuHJ18ZXBr8aIfJsOuPebbv8pTe5e14l6fyAc/pMc/pA54NbX/1X+sDnv37PPP3edbbUjLSmttSXL7u+4omn8kz0kbv80zo3JcyEQekjxCD'
        b'/l8/PpN8bJ/OJ+XUKAn7/YuLtKWq/ynDYRvV2ebS5x9/oaBFO6Q131HVqJGmXdKaX+RZs7CgIOOry6Cukq8VF3dL+doyaMlht6247Latgu8BLrpxqJQwMustbpYwW9RF'
        b'AtmSzi/IzRJu8bIy8vK3eKkZKVTm5Aqzt7h5+aIt6eSL+cK8LV5yTk7WFjcjO39L+jSxD/oQJWWnCbekM7JzC/K3uCnpoi1ujih1S+Z0Rla+kL6cTcrd4l7KyN2STspL'
        b'ycjY4qYLC6kKNS+fkZeRnZeflJ0i3JLJLUjOykjZUjwiWSAfknSGTlbMFQnz8zNOXxQUns3akgvOSTnjl0E3yU923i/MZjOKbill5OUI8jPOCqmhs7lbPL/ww35bSrlJ'
        b'ojyhgA6xuU22dpzNSXVzkbyTUpCakZaRvyWblJIizM3P21ISd0yQn0NkKjtti3siJHhLIS8943S+QCgS5Yi2lAqyU9KTMrKFqQJhYcoWXyDIE5KoBIIt5ewcQU7y6YK8'
        b'FPEblLf4X32h7hRksylFv+G64uE59Q/+GRt/o7Xigk27mxctVlj6I5anwuFkSbOM7tvK5+Lyn2Z5hjI+dswDOwUfV+4XcqdpiIUp6fZbqgLBq+1XbPMLvVffjXOTUs6w'
        b'iWDZzAbsMWFqqJWceC34lqxAkJSVJRBIuiBeLb5FnHFLJisnJSkrT7TBBgLGpIOSFebilfCSGQQPGquCLKGXyEyWTctA/Q6kgnScw3kmxePwthUZBaUS2U95BQc4Gtu5'
        b'BURHdrwtp/9YTr898MdyFo9svR7sRsvHtoHvyKk+ldd6pO38RH7vI97ep4xqg85bjJ74Wv8N6yFktg=='
    ))))
