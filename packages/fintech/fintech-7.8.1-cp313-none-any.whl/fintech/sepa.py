
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
        b'eJzEvQlck0f+Pz5PLm4IJNxXuIQACaeKiAeCyg0S4i0QIEAUAROi4tFqPQriAaICWgU8wRPFVq22tTPdbq/tkk1bkHa7drfdbbvd/Wq1x9ru9j8zTwJBbLd2d39/XjqZ'
        b'Z+6Z5zOfeX8+85l5/gQs/rim33trsbMfKIAWRAEto2C8gJazlJtvA8b9KTgTGdYXZgpR2eFQ7lJ+IJhoCpmK/5fhvCmcpYJAoOCZc6iZpVaBYOlICRJQwbepkAoeLLdV'
        b'zM5LlqysKdNXqSU15ZK6SrUkr76usqZaMkdTXacurZTUqkpXqCrUclvbgkqNzpy2TF2uqVbrJOX66tI6TU21TqKqLpOUVql0OhxaVyNZU6NdIVmjqauUkCrktqWhFp0h'
        b'XbAj/X+AnUJQyBRyCrmFvEJ+oaDQqtC60KbQttCu0L7QodCx0KlQWOhc6FIoKhQXuha6FboXehR6FnoVehf6FPoW+hX6F0oKAwoDC4MKgwtDCicUhu4HSnelj9JTGaAM'
        b'VvorXZReSmullVKidFDylE5KW6VIaa+0UboqvZVAyVUKlX7KEOUEpVjJVzoqfZUeSjelnTJQKVBylIwySBmqdI4PI29muXV1WEHw6GhXS/2AMmz0WSkd9UtAcliyNBgE'
        b'PCK0HEzj+oNyxmarlJNTavmOY/F/ERkWHiWLCiB1zKmyxv5SXw4gYdHld9OtalVAH4QfKpbB51ETaszNmoca0K7JPrlStCtdmScTgNDZPPRSEOqQcvU+OCXqFsNnM9Mj'
        b'02WoEe3Mguey+cAR7eDmPAFb9aTCWdxcEs0HvA2Ax8BO9Eyk3g+H+ziisxEkT3Z2OtplDy9J03nABbVycc0n1kg5em+caKJTWWZsHI7PRLvRjvm5uBinAO5U1AQv671w'
        b'fHkwjU/PRrvhU5NJtCM6z40Jhp24AFILvIZr3KMjCdBOdNk3G+1kgG06B/bBM2iXPoT0oA9dgFvQYSc7dMkJPauDjehKLbq8CjY5OeBmBvGs6tEFKaN3xWnnhaxETVkZ'
        b'aCcXcAOT0IsMPGS9FseFk3JegDsVmfBcGB6KHZloJ2zMRbtz0+GuqByZVIBa4Q0wd7bVBnhEiDO44QyLk1NRP+5/Vi4f8JVw3wYGHU+rx5GkZ+gYvA4bIjJkkdkS1CeT'
        b'M8DelWsLu9AzOAEZ+GJr1BeRFhmOGkPhtizSLTvUzEHn0X50tpSxePNx5jf/Cnamxxbit49Jk4dJUoBJ1xqTK8CEa4cJ1wETqRMmWmdM2CJMtK6YXN0x0XpiMvfGZO+L'
        b'ydkfE3sAJuEgPAEIaYcqw5RSZbgyQhmplCnlyihltDJGGauMU8bHx5lImymwsyBtDiZtxoK0OWOImEnmUNIeFzpC2uUPk7bPONLOZUl7v58A2AMgjA4sz3pmmj+ggeoN'
        b'XErvd3JrqgKyA9jAblsbIMRz4E7Kqsi3wqzZQE8FD+BfSXPdE5EaLyHoBVW2ODigxoOXsOzvmHQ+Cv2S81xMYVglU0W46mJJO9NnBSTR6cPxH8R+U+8AaPAXZV867XNi'
        b'wu4IV9v9a2Fb5XdgGOijcESwFO3Dk6wpal5YGNoRlYbJBvXC07C3ICwjG+2JlKfLMrIZUO1kMw32oVZ9MqHnXp2rrk67epVeh65gyr2MLqHn0EX0LOp3sra3dbRxsIN7'
        b'YAPcGRsdHx0cOylmYhy8Avt4AL64xAads4rSpxPi6kAn52ZmZeSkZ2eiPXiG78RV78aTcRduTVhkuFwqi4AXYA88m49zX0JtqAWT1Y1c1IwOoFa0bwEA7tEOLounjCE0'
        b'Mqru5D2UE0LjEN6LSY3B5MWP55pIgVPAsyAFrt+YF63kjnnpnGQuJYVxoT9OCrxxpMDL0ZJ3qfndvL9xdHOxr9H+SH/pkTeEb3m88tomZpZHdvfR+gT3loKtsbyY0h0H'
        b'YWXPbsn8D5Z/6TGrfcvQxaHfiN8ofoP37m83S/f8NstV8LYb+NtB6/mzV0v590lfI1eugCeL8FvcgccRcwXeFAZeBHn3CfOCW9ERuF2FeiLkeIgbIxkggLs5MjyEZ2je'
        b'lOV4LI/BHRGysDQZB0ce5Mjgjvr7njguNxIeRztgb4QM7cqK4QPBYgadgzfgbppTCJ92Q01p8BwAnI0MDr42B21HV6W8YU6YVIsJGYw6OjIUkk2bNg27JpVra9apqyXl'
        b'7PIr16lrVdOHuXpNmdYFJ+KQ1HnY+XYTuDOHA8RubZNbJrfHt05rSB0SubIPnYkdiYeSjKKwQZHcIJIbRdEk0r0tsSWxXdMjNorkg6JYgyh2UJRgECUYRYkD9on3yKvR'
        b'WmFHKhi2qVatVOvwyq8e5qm0Fbphq6Iirb66qGjYrqiotEqtqtbX4pDR9gsIsyuW4C5onUmgi9lJJbHx2HmwCXwzm8Mwvh85ujet2GR3h8NnxLfsXJqmfMRz2po9ZO10'
        b'y1r07V3MZYXmpwf3CFXsEwSD43ZR3FLOo2iokpAx10TGPErIgnjeCCHz/5eEbDuOkJ1z6HIaH16sy+LjKXygDvUCeAo25uvFZErj9bEgE8cwqKVOCtDTDLyqJ6Nkp4Kb'
        b'UD9eYhjHAj6Az1pH0HKilyWhJhLq5zgboP3wKDxBVzhMTAfQCTu8ijMSeNoZwOsr4R5aw1p0DO2KIBGoIXweQIfgXhc2yw7MIBoi5ALAzIGnlgB0Cm1zo5WgzZBwuNZ5'
        b'2D+nZh3IXsTRk3cYiQ7wUSt+sZFg0spIeGqF1Ia2tTJOMhW/CrQNL6boCNqW5E0rQPszvNeT8BMAXUPb0Am8YN+gMXHoGnwRXscloTZS21XUNnspbS18EfVOQTTmClhf'
        b'g67AIylsa3flo4PwOobJ6DBIw4v9Ydgpo+sxOgkvwXOIRr0A7ODTeEVvjKdRy9E5dANed8IxXbgN8AjqcsccmbRZifZFomMcAjpj1tihp9AWtutHXeEBBS4qFKAbaHuo'
        b'CG6iXbebAM+jVjwXokGgWzQ6yqeNWhqJ4UgrasPhAjzt94AitMlDT6Z6EryGOUu/DvWvZgDHCp5CPUxwlo5lan9rP8fXvYF9ge//dmNzrt1TM4W/6rz+/J87k8JS6z6/'
        b'3a1w/kj66QezrSuazievfZPz2bH7G73jYvIOvRl9/aX6e2un3uOfc+v5a/hNhX1sWnNwa2R+mbHBR9uW8/KTHZtzQv7whGJ4+T75CvuBj0PmoNYL7z53tMJ/8dcD0+8d'
        b'Rfcy35g6t+y9vk7r72zulH3t/PWZTjR/6mGO358HVpd/863Hiq/+FPTaM/Jjyq2tkb+yPXH7/em1f6js/3LJJwef/2KBX6rXO2sy5r02qfGH11/NGvSe8sz3DnbvVwYH'
        b'rF79LuarZMBXT7CLkEvRjkg8IPAsfMmeE4f6p1HWCJ9xXYBxEWpIz8rhA7tKTAwXOehwRRhljWjXxBWoKRJDRoxVBYXwShwnyBa23A8gOdvQXoz0yJKLdmAkiBrh2Qw+'
        b'EFWHxXNxzCFwnyKvrWtmWDB09DzcQpg63JQitX6It/6ooyOvRyIhTMvEtobt1NWlNWXqIsJ0tRIzu/0Ny26/zsPs1nXI3aPZesg3oEfcV3BTPOrx8b/L57gHNMy9IwDO'
        b'Lm1WLVatNg3JHzp5Dold2+a2zG1Pac1qZobcvNpVrZohD89Omw6bruAertEjsjn5Dhe4e7er9mtwZr+QzmUdy44Utdg080je9Jb09jKjOGwvc5cL/GS3hd6DwhCDMKSr'
        b'vEdlFEY3JA8JaXXdyUaPKUeT21f1LO/173TuTjZ4TDEKE3G8SEyWhdYpA/Y+//iSCzwTdfZkoMNtUsTWcLIAuyzftxpmdMO21TVFOizGVap1WvKSte6PGDmrEXZv4vcS'
        b's0OQi26Kid/nYn7vfQdg53GZ/n5BCDhhF/1zmD5BL/wxTP+/iV4q/z16sWGB7FNZIhAMXtPxQbFP34o0Fp62ZqWDZpBWYF9cbPum90Ywh4a+zHfG9Xyrdqwttu9TlLNJ'
        b'z0XZATFYKOIJi+0/XFcLKONyzKuJWw/3RuPKYCsoQZ35mpcX5PJ0q3Hc/dPP95d2vCGEZ18Rwso3XgOCl3fOn2VvL02y//SPWfMVHh4um2/U/Vn4qqQnLDZ62++u7QzI'
        b'8spbfTSh68qAz6uS8qx3A7KiW1XLFV3lVv28uD6g58fx+i9Ff8pRY2C1cJ/HLM/b1ar+L4uL81S3s6zAx25OpdsuSzn3CeuOckGnzJgo3YugovKC+wTkL8ST9GhEcIU8'
        b'PTJcKscIGTUC4CHhFU5GB6X8H5+MfMAiINNMdC6tVJeuKCrVqss0dTXaIgx/wszzsZSdj3frOEAoao5rWtse0LShQ9cVd2htT+ChjUPuPkMurm3SFmlrREPKh05u7brO'
        b'Jzqe6KkY9J9k8J9EonG25OZZzVbtQe0l7avaQw3CgIbkW6LgrnlGUWhPvEEUNWAfpSWv2TwzuKWasmGr0hp9dZ22/jEmRpjZWWI5MXR4YniRieH1GBNDS4T+cWCe0mKZ'
        b'aUJQqdESyjNjJsN/KtVVPDwZ+OMmQyo7GdbwRSBpejYZjQ0u/HIT3bvXOoOzJXMAwHTvtEAFCuhqi5q0UUT+jYEvTgQx6KwbTdubyAcfzMHxM4sjC2dJAE06AW5bHofr'
        b'ioXPJIFYL3SRJs1YwAGb1E6ksqq9+iKgJ17Yvnp5HCaXOG8FiJtuRRNe4zoACQej0bxi+3ZXMaAgAC/qB2B7HAYh8eiaCsTDFh2tC3Y+MSsOj/bEkngwEXWjG7SIxlIx'
        b'uKHPJ83a4K4tZmcpaoOH0+LwYEySwl1gUhY6T9N+UeUDXivUkeqSQqz0prTX4I64OIw5JtvCrWDyTNRK067G3FMyYTsZGp8XVUFs2nUR8GIcJqmESeg4SMAgo4OmHZgY'
        b'DIbwcOM2lDT5+AAWS3Uu8IL92DMFnYAHsNuIrtDU2XOk4D44SegyMFjtx5YM94ZiEbQfD2XiOgFIRKcm07S+uZHgcslF0uLAr20WswOEpdcTsJWIKLPgAT6YlQe3sgPU'
        b'ha7Dp3V4jFNEgSBlqZyOe1hKMJEGUjfALpBaPYOmXGuPtuvwUM6Gp9FWMNvnSfYNNWWuJ9N+DicNzHHj68kEmiHm6vDYzPWFzWBuJdpBs6ehI65kZqUthVcwGjy0hm3W'
        b'ZfiUAJEep8POJJCOttazWM8RINKxDHRODTLgIXiWjs9CdB7D737c2ky0dwXIhP2wle3GfrTXF/XjNmc9ORdk8fLoSLwgEoCri/zwFCi2rynyZskvazmGif24I9lobyDI'
        b'5pXQpMcwqvzWD4MgYXHWi37Z7OuYCk/igvtx93IwSrkCcqpQM01dXBwKgl2eIQUHRqQlAdrtlV5LUD/ud27cSpC7Al6jKW/EhYOFvPOkXE6vci5gkfExjPD3on48HHlo'
        b'E7oM8lzRTpr8frAHuOlWRmpIiufMYwuOQFcqiaJ13tQoMA/unk9Tro2zAQ3SQJLSPqquiE05MQZ22eFhy1/nAvJVsIlNaecIFlZMx0C4uKpFGW2ihxZ0HbXY4ZFU+MIj'
        b'QLEePk/Dc2AzOmuHx7EAns4CBegsukAL+VeJF5iZtZz0Y2mDPJAdSvhMKdpth4dSmYw2AWUAnyYVhPsDe9lGUl9SmMSLTYpaK+vt8EDOR9diwXwFOkyT7lsUBD7V7SQj'
        b'WsIL82I7UbN2qh0exgXwVD1Y4IY2s51Y5w6qnJeSEU9ymltlKrSXE2NnRciiGz4DFvr60KSrfOTgsv8NUn+gfkEN21+uQw1swr+L4Al4HCzCMk83TewdEg/Orhog0zDf'
        b'Z5ETu4o3BMaBrsrfkma5PC+Qs4FH1kWDvIyXyeSedVwXAKQcdiD7J/nCJjzmizExXgGL0XYrdmyeXSiATXh8lyTCRrBEGVH17Q8//LBmIg98u05MGaJeu5QtuWLWJBDv'
        b'+HvSt/ysdRuB5vgrh7m6FDyuf0l/W9/yeg4nWbj9TAXfefYqtO1dvvskV/d9v+I2ukd9H9doYzWr5M7HrzTdTd9Q9INGEBPz9Udn7n+p1y/QvxV194Oja3MUjX5553Jb'
        b'YioubP/LzOLFsQ1fP7GnXPzmPN3bG2wc3tQJ/vxDxR+eef7m9rj8WuegPy2UiKJfnx38ekhkq/Rs85m01hULQyf3pVdrJh/7/cq//b1yzYLr64d/s11+7+PLhwdXJ78/'
        b'e99rG32an04IfDNhQm5txpHuWfPnBf01r4z7l4/58tcnnH9txQfNVypb1lz1731xlrdv3Zk5RfynFnZdir1c8cN7X/11UeyZlYv9VgT6b39t/euT804n3HuwKy7wxS+/'
        b'2PzdlSde/Ifx8NMDvcGzOV+lfjXlk0Oq5ytPBOxtTvq/jiN2kb/9Wrb+wd5Cj7+88JtLS/ier5ZPWerZr6t/fVVN4Mq4UJFr5wbuROf0qRwi5vhQPpeQgaWVHNSYheEM'
        b'A+wWz4BnOOg87IHXqDgzCYukWyNksG/5qI4INQXe96XcxWVlJhbJ0a5sWUZkOh/1wPPABV3loqfra+97ECp4RpGMRZmdIngtM51oiwQJHE/0UiwrDW1bu1EHz6XlyMKI'
        b'Gh7t4eKV6AXgjJq5sA+dQc/+AnFnBJwMO5pAlr60iIg9WrL/QBHWfA6LsNK4ZoQV00Rw1W2RW7O2nWme3DajZcagKNggCh5y97ZAWxjHeDoSeDXvDpf4PLzbTT5JUJfJ'
        b'FxbRY/JFx/WZfAlTr+azvuTUmyWsLyP7NS3rU8wfWLiY9S4tGlCVUu9tWguf+Ggt1EdroT5aC/XRWqiP1kJ9pJa71EdroT62FuplayFeIs2JcT1WrN/Tp33EHxDclW/2'
        b'h8t6Ssz+uEl9WrM/acZNxuxPZeYyr408ZTG5zEDeSGEFzAKGVG96XMYUM6QJ9NGaNCH/jg3r9/JtLzH7gyZ0ac3+yKg+zl2TPzHpZuCXxN+QfsceuLo1zL7DsXfw/cA/'
        b'rEfUo+gp6fF4zz+2ZW5zMpZm22Pa9Lc9fLu8BwNiDQGxffHGgISr2DfN4DHtIJ/02a8nvtvf4BF9kH8X46e4O47AN7BrVkdGs82QyK+93iCS9ij6XHoXGEXxQ94SLMuK'
        b'J+I2iD2+vc8HYt97gHHwveXuc4eLfx/oKOQKT3ZJmQHQDNtUe+4rdgx2zZpHLibGH4fXVM1oga5jzQ4BwFTN+A+iZuQyjPPjSpytgiBwzE7O/bcAm2zKAAuAzf1fbpuM'
        b'lzatWICt2OgAMPcIu8NdFcnlzzUBbN1SWyxDAuu+1XVZCRV+JshwAG1bH4dFyAR0npUiu1Grpiq8haMrwNEDsZ9RXTv0Ibr2rO46uc76mEveLmlBdvSx/UJuSmBz29ti'
        b'6POWz1s3Ofscyq3Ly1UD/Df+ErM1WhqzNfbmu/0L72yuj47uia49yQV/uG3TU/2qlGG1NH1wCzw7qjpHnbAHs8bn0Ukp75EsyqwGZ9mTF8uedHVafWmdHkuCRVp1uVqr'
        b'ri5VaxPMrGo2YHXhs3iY4oiGuzWpIfWWk0tzfFO9iWsNCfEMbs5vtm6P7+J0ObcnGIRBPynuCYZ5OlzVz6fDBLPzlCUdJvMYxuVxBDyS8WfQ31gB779Jf+N2pLnj6E+Q'
        b'Q5Wt1ny00w71owNaook9C2AHbIQnKRFaS+NBJS46etGhku+qKsAczbzfvgx0WOwDuUYvltY8zLQWlHfEUzG93SA+nckNDzi59zV0UwiP8+KdJojeKpvID3P8+ETc09GS'
        b'N1nqeneptbbisJRD1Y/wmZL1ZtrSoK101b289L6ERG0jy2QEbEdd4/QQaDM6IuU+/EZJR0cIz+Mh5cMo2U03k12CiezyLMmO7LHghbErflAUZhCF9ab08c6kX+WcycFE'
        b'eEsk6ykziuIG7OPGUlrpY1HadLPTaElpub+I0n6Obo2vZP5nurWfwe0ELLd7bb4T2UGOsY0uzrrh48pi34xAsvUrCXDAgPjSyjw28PdZxFKieB0HFGe5hU4EGqEsgtGV'
        b'4JjtHd8TdZnk15i+XiEUuMkmyzOgzi9v+r6XvV7LLCgBX/j2ql896pZhFbfYhnn3LvNujFXcZ9qY6I9juYveKp7XNb1r487wmT7w6CvCt3j9ye4NOs+Nv/f0SDACxU37'
        b'3MO9mC4JoMtF/avgEXgOnsnKjsStyWTgJbQF7rtPbB3s0WG0dWUsxpNod1RuNtqVkw7P8oB7Pm+SHdryGAoyh2r12rqiMr26qExVp9ammglzsYkwl/KAyP2Wd2RPwYVF'
        b'vYuM3pObrTF5tq8lHC/1Qm5vrjFy2k3GGJk8JJH2JHc7NKcPuUu6Ylo3Dnn43ha5N2TiddzDp0PTwxyqMriHN/Pw2i9yH6MT45Gah22q1Koy3Ij6x9EXp5qdPcBCLbYE'
        b'k7EvUYs9ziYhqxYzW1SRP4GZjKoJLfNY+yJMzRylgGqLrZTW8QITRXPHbBHy/MbQq5I3hna5yTxK0eNCf1xBZjOOovksRV9yj8OgxbrWBhRrOepClnhfyOFjin5tA2dm'
        b'cZWyNgdoyvnfcHVbcEzLe1v6S0+fPYRZp5uJdfqlhKUI4/zqXxXOdwibOm/P5oCDricDt05sN+yzgXL+7/hvBPh0Zz0/s1BuNZA1KSsupePc1yD7I8Elj5Sr+zye6sjq'
        b'lhv574t/YzP5kMLm+HZu+fT2PYOHJfdmDbX8ZstFVfnHF7dewlz3OQD8f+1ye9ExLA2RNR2eQfvhfngYvUj3aKwABx5llOgapm8CNqrQCbQ5M12WRq2JqC1RuxsVo9BZ'
        b'uAcez0SNkTjjrlwf+BwDrNFODtwaXc6W3IC2w9M4ssEVnYzCXJ2XzcCXYAu6Qtl9FLwUhbagTtSUDc9iYodbmbkBs6V2P1f+eZgmiVrELA6NzCr7CrXFpMoxT6rNpklV'
        b'iyeVd1tkS2SrvCFlSOTWltCS0JrYkPpnJ9cP3H3by7tKjO7SFl4zM+QT0sN0ZBOETBO1r2qdNuTt342n2rFIg7e8OfVjd6+PhL7tZV3pRqGc+Eo7KzsqDy3vndJXcGaG'
        b'wS/RKJx6z4bv4diQhiG82Kch12Lu2ZC5hyccWVOHBaX6upryH19D2O7a0ClYbLHbRbtHnQ7zJPwOT8IaPAlDvsSTMORxIXS7IAz02MWNhdAjKmK6sPBHIDSxawLx/P83'
        b'MNpt3DT0Z6fhZ5w3wT4GeDzhVmzzL+8q0zRcGwBm4kI/W1e8NLtsHhsYGUutjyolFcVV/0xdzwZ+GEPxdvETPsVV/oJUNtCJcQHBGAadsy/eoHZMZwND9D4AY4bKPYXF'
        b'PgH1gWzgsloWKZ1MLdb+YWomG+ifRg2iwuZNKM6S+ZeygettpSAPlykpLubk2T/BBv5m2QywAYC1l+KKtaA8iA30S54GiFVp1KLifFQ6zVTRjERQB8DMD7wxt6nPZQMb'
        b'53iCaACE3eXFS8vjOWzgbm8ZWAhAwpmCYs4DqYQNfM2G7FeBymPriqt0yT5s4C1OMtiEfz9eX5xfXaVnAzetY82x9GnFWYmCKDawVmlPZJWFnywprop3NjW+scoLYBQS'
        b'9qVzsQ9PHmpSZ5VMAlUYpjHy4vyds6eygdyUPNAFQN7JDcW2L9ny2MAEfhl4DRf9fWbxBM8QPzbQ6oly8BYekGFZcXlPEMMGvr/IDUTilM/Li5f+c5YDG/h6BgUUle5J'
        b'xZEB7iVsIG/ROnCfqEfFxZN0QU+ygauXEkYN1p5mimPXxE1nA714QcSyZeESbvGsu8sLgUb7+Z+4OiWm+9+3L9/Vei3nlWjh9sMJb2+UD2rFfYsbw49m9KfdYGYN3017'
        b'P1/moKl3XltUfuPt7uC0hG2/7vzLD78+Ehz1+dxPS4Lq3gVWCXDnbzMWJD558tNlNt26ZYbg5/YxOX+zNdjWJh/tsdlyVuOU9OcJ+Qe+K3f18Gt9dXPtPLRePmXus7kt'
        b'W61D/tJVqi1JmXZf8lHVQcXU0MNeIWUT5p8SXbbV3k+YpX5vuriuc3lC0POvXi+uUczY9MfajytfgejpeXM9kq99d7Lw43eadn7H84t7e/nHvaUrv3d7f1qjYabs2KlS'
        b'j79qgyRfrFtZLVwy/BJzvurZM8krXvfkxWmn333JY+qi1ddunncLP5+c833E1SPf/iHyU/FV0e+93rB53a1aNzXohc8170544cvz/7dix2cfvue/59W3JWuK7r/o9+nl'
        b'z25c+KHAeOXLNxxfL3xbF/M3n/+bkvLPv7363fdW0y6F39rx6bd2ZX+aL5NflXIpqufCF+HTGDnBzahtHHqKhc+xMue5OnQ9MzITnQ1LQ7sy8RoDz3Dq0VZ0gq4i2X5o'
        b'SwTOHM4Anj4FHWNQoz9qkbr8wlXk5yw0LuaFxvxnsd44k/WmRFW9oqiypkpDefoC86JTYFLC1fKB2L25rnVKQ+odAcCy7EajU/CQe3BXAcZlA8JwoqJybee22FFTgGZV'
        b'e0CLul3VoulKNrgSQ4Ee5555va59Lr1eVzmGsEQDtQkQOjfPa3duUbbPa1nUFWMQBxuEwSRY3KxtscEeZ1GzqsUNF+XVrqW7oyRHfotVe0wXp2Ny17yewO4FBu/IPue+'
        b'kovuBq8pBuGUMbkaZg05uzSXtRd0zetYZHCb0ONscAvvURlcowzOUWxkSUtFl3PLMoNzIH52EbeE4h8n5+ZZTWtueZKFMblL2zOre43RM6pF8JE5xOgZ3iy4a4173FzQ'
        b'HtOuMgolQ0K3Ds+umEM+uK/Yb/l4C/fHnIz1x7ZrjcJASz8ZPnecI/aQr0E4gc093m/OscooDLgrGF+9ZaqY9hKc6lH1WeZ+REvivMhyfzfBMgEeVRcRCzm6ko0uIUNi'
        b'1w6broBD9vidNTMYpIvE5th3XUJu24v35Dbmtie/Y+9H/NmN2TtzbweGN2S3Bxvs/YdE3mNwhPUwr16t0v40dBjVHhdb0i4lVOqcN8MHIoou4mNR9C54THmUYnjLFZtn'
        b'+r3XDsyaj6XkhATQchSMFkuefkBhQ839OPFcBYeAiOWMlkdOQyi4XsB80kEroCE8ixArGsK3CLGmIQKLEJulfCwtcOM5CitSshlmaG0V1lo7JZjGaO2DAYYZtsNWyWVl'
        b'WrVO99k3pAcCix5YmzHHWmCWqM2nHDAEIibdHCqNUDPveGsTEBIU2FoAISsMhAQWQMhqDOQRJFtRIDQu9HE27Pk5rKEJ7IdPieBzCuwPAAGlqJe1Xhu8ncHoDmHfr+TN'
        b'K3OvO3Ji7HW6z/86acJ8gWCSWyJ8xf3+72xiJDFHv9vxHf9fbYHne1MPhVwqDX37Vy+sesX+a6vvP7/IuBydpfgCvfH3m+c/7ZyUe/l+7dULN4//cWDV9X4Xp41rsl55'
        b'/pOcgvNvne4M6u1ZMmlfYdzuJ2fcyjl98fOanKHNv9l46Hq69eWTAc81Fs6JTwy69Zr82OffeNa/nrn+20+4d5a551eeldpSm7ON6JB1ZiTL9aXwhonxN8FnqVRel5E/'
        b'1gK4Pw5ehJtr6A4O3JKM9pht2XQSATzLiZPCXXRBSXKCN+iJAVIubIQHsdRynQMbN2xgbdka0Va4L0IuI3ooeNFWAI9zouWJ9/1JsT0ZaBdsgnvQnkwZln72WFGLxeNu'
        b'HPQ0vDqfGiBPCq6FTbl4RUK7IqQ4zTZ4mgecbLh1Vtbs9tBOqzk0QSTs5YHpqEFgzfHMRy+xW1ONci5sikINUdwUeTo5ycAHLugEF22eoqdjkiES4ni5NCNbxgC7Kixi'
        b'NXHQlTR09j+WmzZtspSbrIqKqtVrioqGnUzzQW4KoCsZEfKJ+LTWCnj7Nlt9KPIcEnu35bTkdE16Rxz+ocj7SN2Qt19nQkdC18JThX0ufQVXFl/NHwieafRObk41p40/'
        b'ldideCzpHXH0hyJ/cyB5/MDdp31BV6nBPbYv7qqV0X1mM29IEtrM2+cw5BuAf2yHAqT4x3HIPwT/2A+5ezfbWTBBu2FuaZVOS46HDPNKNXX1w9a1Nbo6siM2LNDVadXq'
        b'umF7ffWoGvrH9RxkbIrpn4Wugwg+Wg12vidJyBmtf2E+qbdimJnMfUDcx+CUlA8fFsjAObuEsYIWY57aPnRqK0E+GP+HuVallMnpZYati0zGTFJmmKdTV5UTAw0gYV+n'
        b'dVKVamVJmWr6sND8Ps0hDoxpMdgEelIvZJ/OpiP5i1qyFbcE184vIoMuZbRaMj6jrdDqiFNHmBMOvGeqU3zB67TXf1ynTZH5Ff9UvU4W9RZcKDxd+MvrrWDrtSpiCeqn'
        b'ahVajHD8haTTSeNrHVGUEsUmOcXB7gvg9er/p10Bbo4GROzi6AJxwAyfhpfa+ksPviGEXaOK1su23IpEkJXOeeEdlZShrC07Gj433X6UuRHOBpvhMSnHYkoRBjKi89To'
        b'LHaDhl3NtDkmmHIcoooi2LnSGnj4tKd2ZnRkGN1DB4ShFvOeT1/BoyYz1bVanGbYRByiA3JhRpXuX6usHw/kUErai5fzo3YyrpSnJTac2lXEqSfOBtqmHPIndcDTs4ic'
        b'wcAc1baoiD1zif32RUWr9KoqU4xTUVG5Rqurq9JUq6triooop8HMS1tTq9bW1VOOpl1BnCrirDR3Zdi1CI+Xqk5TWqSqq9NqSvR1ah0uz4Gc7VDpdKXqqqqiIikPzxI2'
        b'wPKox+hG3cwRDrfY7BAQpCOQ8B/bwR1bMJNJZYZiJ33DdXLwuQuIEwjc/Q3+U4xuiQ1zb4m8DT5xRlF8Q+otHCqZanRPaki75epr8JtsdE1omHPbwfUrDtch7B4XOLp9'
        b'TXz07dFNTddAL92q+qx0aYZMLgC2y/GKujxqDJHamX7vfYFf2nTnsfhRwdHyPMEiPEuw64T/C02/DuQ3mhPPMT2P+a/gThFQ5BlKcCdGcOYjeUKM3/gsBh3Binx6Bhej'
        b'SoWVwnoKB+NO8myDn23pszV9tsPP9vTZhj474GdH+mxLn53ws5A+29FnZ/zsQp/t6bMIP4vpswN9dsXPbvTZEbfQFnMEd9IurdNobxU8HOoxhaE9sMfo2XMMxhXScry8'
        b'wFKhwhuXxNU6jxkpJ4XPFI4iDOcmVtdche9D/Xah+f1wO/xpO0T0WYKfA+izeGxp+L8V/m8dz8UuTxE4hauQKknb2GOPZHwdlU7xNoqgh+pxpeUG43JDaLluigla9woe'
        b'5lbhGJWX0tVN44nf/TonW9Mjez7Zluy6abDQPcwjE+lR0ySn1MqCkhzN7G474bbWY88rY85rg3kvF7eUGTmeScYGI3dMF44mjmw1Btdb+41B7UrrMbzXKtmacuRxoZZW'
        b'6aopmNHZpldr6jSqKs06cui6Ui1RmTqqwXBFVV1KTm0n1qq0qpUS0uFEyWwNTqWlSdNnJedIarQSlSRWVqevrVLjTDSivEa7UlJTbktUFWo2fRhJHCmZlZ4iJVnCklNS'
        b'cpU5BUU5yuxZs/NxRHJOZlFKbupsqZxmK8DFVGHegrOu0VRVSUrUktKa6tWYK6nLyOFwUk1pjRYz79qa6jJNdQXNRVuk0tfVrCS8SVVVVS+XJFezwRqdhG7K4vy4fZLV'
        b'uM9lGDXIzd0jbzKR1kt85qPs5uGorKkqU2tHEpuQD5ve9ID7qMiVxcVMmiRJzspLS5bESh8qhbaRLUkSVlNLTr2rqqSjheLmmErEvke34FH5zECEzWt++vn5WUDB5mb9'
        b'PyPvGE45IqmOLOf2OfTUNewPgM1ktyZSTo5mZy5ADZloZzZ8bi4f+MOjPHgDNdlQhagrdw/wYZojONHF1Qci5gA92R9HL8LrcfBEBd2xyUMNRIKKQo3Yl6tgS1KmEdu2'
        b'7Oz0bIacUDtqg56DT6loidOqrIA9SKt3lBRHvj57MdBjyQysjIVXiK1cRCY5GJQ1L80sN53mob1Svi3sBYpkK9SGU7FWok5icpB45hIbUGz/TYSS1d7OKCVK6jS99czi'
        b'rCpuDdDLcaAaXV1kWTRqIEfIcTuj8tPQjiwBOYJ+YC46IUAX0fVI1rDmfCLcq1sFn4F95LDfHtwFmxhNbG0uX0cw3Ce339qYn1y9JVroY+99U/i7Z04X6j7nZig/GYhK'
        b'hW/2nko7tzfltXOfzx3+YXXAxZcTzuVO/bDj1qI3L7zrlHBrk95XlXC4/J9rpXcLQc3g+pupB+45r5r0rsez/xR8PX3qkb7Sv159yUpw7q8Hy75zrdS84/XMy71hDRFv'
        b'dxack/v+5dvI3WVuwXpRUMLE8u+tPorysu34416XOZOn9h7zjdl4+sW9ke8cfzL3s7Qb95Z8KPvz6xUXDu2aeqV0eOLAH19qrPiiMFjhHJtV7Xv4/fKhF+yvGevhwt8P'
        b'33z+q5r9spufSPsPuz31wdtn+ZqnS5Llhz7rOPH0Ab/TSR/n177zQ/tHneGHSmZue/qA27uvf/Vc0u/rd69ocnxtz0vWi+LPTldIXViZdbMt3w4L1N5opzRbLwtHO6I4'
        b'wBU+zbOexkrE09AZXxU8MsbkkhpceqexUvXlMF2mPCM7Mh3uwuL8Pil71t8LXuZVT0Lb6DZkAdwkDMqwPLTri7awpiFn4HWnTLQ7IDaNXEiwG+1hs7uirVx0tWYitdos'
        b'QifhCxFyW9j1sPVIMGq7T86Fw2PzFmNywdkjELlDgC0sKhP3h1xisGc23M4Fc+FFKyz874O7qSZh9XS0Ce1FRzJzZeTeAUJUdvM4aLdoJXsU+WyBdBnRF5ibxEcHGfQ8'
        b'7DdlRwdXoWaClik1nrfhokMMbv9+9CwV9WWoFe5IEZDsZGph6Ime5zDo0gxauBTujbHQM5zmgYVoE1EzrJTeJzdzRMPD8DhRJeySUkPTo/Gm8WXLioD9fLQtaiJ7uO8p'
        b'+CyujJSWhedtXwoXdTKwec4kVpdyyhPtx5HybAHQ46jnGHhoPmqkXZjiDttJA7MxM6H3TaBexrGCmyi1YXt4fi7sxVnNsK4c7nNM4c5BZwpZW9qtYUtJ7kg80DmyNB5Y'
        b'i7ocYQ83FV2CJ6VO/02dPTmfMKLisFR0YFyuwWsuRstCE6iQm0Oo4FHEsIJHoQ3wCOqKN7qHNfM+dPf+wCu4q9DoFT8gjr8lciPK/HZt6/SPvYIHQmYZvVIGxCkfirw6'
        b'dF2TD23oWWX0j/6AxEw1eiUNiJOG3LyaubdERAGu7InvyhoUxRhEMbfdvduTW9a0Pdny5KB7mME9bMg/eNA/2uAf3SfuU110vxp8ddW1UKP/rA7e7eCwDpt2XnvpkLt3'
        b'27qWda0bmnlD7j6D7qEG99AeXk/poHuswT2W1plo9Jo6IJ76ochtyMu3U9ohPRTRkjLk6tlW1FLUVTDoGm5wDe/RD0bNxf+GvPw7ZR2yHp7RS9acYta1+PjjHxvzk0kP'
        b'MyG8mfeOMGjIR0IjTT+SYBJ5SxI6JPa+Jfbv4hnFIeTX2iiWkl+BURx6z4Yf4EKS3bEHASHNvP0OFiKcMyvC7SLObuI8SuT598rth98+edPFFnocC6X3MeIcx44/EQWJ'
        b'IdYPm8A367EoOOMbgB2ycT7jcfU5xwXx4LLdjF+mz6lg9Tn8IoLwfkSvMEqsZjXOwlHVRntB5+KDi+moPggpGEGGBENg1GUGEWFatapMVlNdVS+V4+q4ZTWl/0lzeUUl'
        b'mtIf04L0YGfJmAYuOriIbWAwaSDGoT/Zvv9EL8ancvdPtawQB2p7yRNtUcRPg87/vGFEZaWtxf6fapRqzHAtO7iMbZzcEuH+0vZF/0T78jnjw8xqNg7mlipWRUPn5E+1'
        b'v4xMJ8eR9ncsG/SN+p1vlMUQ/xSq/l90oZJ2Qfs8MDGTn2p9xfjWx/3OlzX0fBD1c3D9/6IHFRY9WPlverB8fA9ifucbw/ZA9u9li/8GkfcytK0/1cyVZO5dAea5F11A'
        b'BVfcJkv9vMREdJIqekXZj7bt/60WtVzKWVdim0KEWJ1E8xD30qnVK+m1aVhSprKtLbk6zSSQK7CAjHs5W6+tkeSp6leqq+t0kmTcK7ltGO4q7jBOuHqSPFYeLR0r2Y1Y'
        b'Qlps9xVIGXppBdqBjtdE5MBDqwmU4s1k4Gl0DPVrCqohT5eIEzQFJ7FaXKLB3fush8csj6faY9SbPl/Ut+OSaocgThC3KPbpZZej/yw5g0oO2XIr7IBdu5XN8Twpj+I1'
        b'tD8ANYwANvhCKqmIBWyNivtEVYwuBqHDmQQ9w4uzxqPxEtRAcWHaLNiDmrLQTriJvdaLXuqFdsBj9Cw6egYeAZkUFkd4cgqZqBr00o/qkK2Islhdqxp2Mi+JpgAK38ju'
        b'DNmpqrQjZt3TWqYZRGFDwdLB4HhDcHxfwZVFFxfd5P3a+mXr1+oGguMHgguaU/dlE1i1sWXjgDD4F2mXXycOuSCk1lK7vMzuMbfQn2KnDoFBP8OymxjgMZjW/zeW3RWY'
        b'1hfYKtR1rFZKX1WnWamqMy2Tep1JiUPvHqzTqqp1Kos7BEvqbUmeRKqrSyzOxmE4K/5RVai1xQ+pLsbvRJjsa5+kCgngMbBRk7NQWsoqJMhFWZt+jjbCkzeijyB3amny'
        b'rt/j6oi58h+NfPbOhX3Bv70phF28so7Y2E3JcoV1UOyMdsNyW25K4GRuSnwBL0zQlq3+tt1eZat6e/Obx+OIIe2Nj23sO4qlHGoJbgsb4A5hjV3mODkYnUQt98mdAXAb'
        b'Orx0VCjLjsxDZ8YJZTZo60+cprEwNdKp64rMb4KCnGFP8xQYF0Unw0TTZNhAJoNBFHTLe0JXndE7sjn1lrtXe3xrfVds6xMf+IUNSOcY/eYOeMylMP9dYZCllTg7DXb/'
        b'yFz4EfNwcn5WO4CddYyFefgqPCU8iHm4x390a8LjLUnDjmNH5qdWp+0EhJFbocgiOugb/TvfaIsF9OfOAjnmXVJSJLkUYYxh+4j1RhUYNSnZD6gtLVGZj9rT/nfN2rfi'
        b'6fzF6HSu0WoqNNWqOtx4TdmPAYJq9RrTshQjj5GO6qFLNWWsrpL223zEBhckl+SrV+k1WtOwlGFfaZ2kTF2iqdNR1SthDrhEXc1KM6TV4NVdVaWroRnYotiRLFdrdaOK'
        b'WX0pW2PKrHSMEzSr9CQ/hmJhBBNItOZacdnpdSqCEmz/zakU6xx9EvZPgwfSM3PQTtP9gDmyeWnyjKIF2cTEvTEqHzVkzUvj5kthb7qksESrfUJTaANmVTithNvhFn0M'
        b'LmA1nuDHLJWO8LwtLsJcAICX0H4lXkD3M6vQs9YLplawC/devKpuR/32DCiALwLUA+ARf3iZXj3IS4KbdY76+WnEFkSJGiLnwxPBqAHtQU2wtyAtktSzMz0L7WAwezsu'
        b'XQsPBKOTBRxyudgV+zzUy9VHkBq2oF60nTSskmduWu1IqXkLZPOtQN6TAng8TK75/uXTHN1enCm1y+Oj/f2lhwlzFL+CmSMnOHqTYF/Ox+XFDeXbGwVxB2NnLezdGZCV'
        b'fLb9ATn6pbDe4jIg6PqsamFBTPfwXmh1eZuo2k5h3SrPc9+77K10VXGbVnXQ9ZUmqdtb9ka7K5u9fyVwK+u/+2DLlK3Onzpl3ctb9pYX3Pnnkq7f6oZUXwa8NdPPamfb'
        b'2zc7BGC9t1vdhzlSG6pwDIAH52KmT1RO8AQ8S9ROdtUcdAh2owv0kDVq89XbhctyyDFtwmbNzNgf9vPQBaI4JCpFB3RiA6tQXFZkugfwUAaLc3qJjU8mq1uDDWgv1a/Z'
        b'C7muq9FTlNcvRE+jlrGcPm8Cy+sbUQ8tfuYUGYY4RTMsAM7saLb4bfCSNGLMOTb47FyijKyBu00KOXQ0FTblwqtwL9XJsQo5+xJaMjzhVYwjFyQTjRyrj6sq+3cnjTY9'
        b'tHCMzvkiTdnYhWNMFF04TpoWjmJ7IHZvmUHw0Ya2DR/4hQ9EzDf6LRjwWDCiXGpOIWeUFH3BVyIvRg56zzB4z6ArSsrNUoM03eiXMeCRMSRyw4V4+3dO6Zgy6B1l8I7q'
        b'4w16TzR4T6RJc4x+uQMeuWOKlPYEDXrLDd5ymmLmzTjDyBpl0k+Rn/02lraQ7Eo1wnl/fLlir/GwXK8+Is4fsdNoXq/ISYpce4bxIaaQPo9rJdAmCAWn7GL/I4UQrwiz'
        b'2p9arbqJLNUHzLJUDBWyR/nxT0l6/4GgV84awvDIrQM/1brjY1s39ZEMPEWZ8vAu3SPaKeUO81Zq1eXDAp2molpdNmyDlxa9VovlqFKeRevszV0gphjTbcz7vHSBtR7Z'
        b'7WeUDvSSJY7SMd7etNzyCix2c6v5fmMWUyV/zMLKS+bT5XZcqCV6VpGN69EVl72lm0XCdLGzFB5H11bSSXapM6cdObk6ul1Ih4BNRZPg4SNhKiI6yyUpqmoig6pMcSXL'
        b'8SJMV1+yU4wXSEVuwqToGLpHTPZ3y4haAIunI8WPjGyiZE6VqkKyplJt2nHGDSZtHk1hbqS5+Ooa3JVErRo3pFqXKEl+WAQoNjVH/u9kXNscPcHqsA2+oB27PqMGcqPg'
        b'YSxzpkemK9NwcL5pvWViXWArbEX9mag/A4Sg447oILwm0xOBcFI93Jspl4VnYPbOFsFmp0WvRs+S0tMylGGm+w6zGYBO+NqjHjE8SGWRvy9MB32JoQxmGssLVauBfhIO'
        b'9H4Cbn1IFIFH0RaTOCLLyFZY7o02KWzQS3D7HIo7PCaiA6iJJqEbUOlkUY+YT64Ixqv1Xnh9ZHM0LTIjS54uCxcA1CS1X1WBnqK4QxUfZYE6lqGeeWmkQ6TqMLx+YPki'
        b'UirL4IN16JQN3OUCT0i5FHnAF+AFWX45rZsLeNMZeAbjikY9MeZKhNdDImhm9ExIZjY529fBWb+ymt6DrfCG5yMysk1jyMAb6CoQhXLRoVi0RSOecJ6rO4NTOQUU9v+J'
        b'CFeer2yyie+qo5JUXFZ8u2GfM8xQ8z4vfflY7q7NzPUdkklHV5bOurRL2Riw1eFVp/LnDnKUv7FZ8Junjh+UbfVc9IJyyvbl84PfjZz57NKAD05mVZ7/CDzY7BtspTj0'
        b'Jl/55tbu+aDnQESDt7HmpH3tC0sDdibfuKosvivy3hvhOXM6Z/jlPWEfv79VuLt49bTy9iPCt30c222/WNUNb3YwQNzgn2nswdCCaB7sUE9SJl1xOSULXJkYeBKdvB+M'
        b'I9Cp5XCPXfgjEIUdOoNBBToBr7C7ocfKEyk4gdvgLnZPjIITtAf2s3tih6W5menZ4Uuw3NeIi7CGTRy4Gd1AbXQz1A7jmBsUWcCd8OxYOTIQXqMAIBo2o8a1C003vJMz'
        b'mcvQGQociuvQJrJ/SU/RCKo46CX0YiB8EZ2jqCXPYxU9p5zL3sUZyaAzYiCK4mKweAz10ubPgj31Yzb0HCtE6CI3Ec+901L7/2gLjnDj8ftvdgRxmBjHsMgShpgCKQC5'
        b'DVgAUuJA1DgJbQkfeE0YCM0zes0bEM8jp/ST2pK6Uk9ldWcNBk/G/2h0ptEra0CcZbE/94HF/hzO1TGVir9GUSSNmGv0ShsQp5GdufKu0kFRuEEUfss3vGeS0Te2eQ4b'
        b'XDkoijKIooZ8gzqXdCw5tKx5zpDIk7VHPJRlFIXRgmYavZIHxMlkH8xHMuQXPOgnN/jJjX7RQwHhd614Upd7gBcgontgtsDDp21Dy4aBMUK2Ewtd/kqcL4jzN/BL9r1G'
        b'tz7H7nyZQM4/iEM+2HDKvPX1PQY5mQ4ME0G2viKIZB7xuEinUxAFLtgl/nKkIyWmzKZ3/1N44rWxmuMAsv7h1YWuhiPLpaWqWGrLas4vEOfPxKG2mp8R5xSgW8EmzaH2'
        b'nyTsMnGM5HXwiA1nLycHt22O1ENLzm9rtxJnG3GIERmxly+rKS0qYvcTnwamTcxhbomm9Ed3MoetzLspVGVIlCTDDmOUEywQHYWw/6C5TL3TNgC6Zfo/OeTm/NBstaCb'
        b'nWaHYBpdO9kg3w7u8jgOwi+tgaNrR1w3v7u0N7hXN+AfN+AVfy3ude4tL99e7sWUu1zGccrtuMlDidO/4cY7hHwFsHOPjwPv8LDvbhVmxz63hKFD4ql3+RzxtIbUuwIg'
        b'8r4lnDAkTsQhoqSGFBxiSpNM0qQwNJG7/y1h+JA4ldzZO4dpmGtKFTU2lYfkljBuSDwbB3nMZRrScJCb3y1hzJA4BQe5zWYa5oyWNYeUlYbL+tra2iHkSzHtWhevPcLg'
        b'MOFrjo1DBDFjDb1DfHfFwDfkljB6IDaFLcoXF5XNjoaoOwhn+Ibj6iC5A7BjyoV9dyPNfZtL+pbO0M6ZguaRIAUOYksJ6tb1xl+0Hpgw5eUCg0PGNxw/h+CvAXZIcZnM'
        b'HfJ8d7q56ZNJ06c0zWXNa8mqI1uKGnR4GcrKYaVaBtiu42Cw8axq3A3o5O9eLGa7013G29gquFq+gqcVRGNOpeBrrfF/G4VAa6uw0mJJX2vvCRbxqS2otckGl6F2oEKF'
        b'zRSOIgZjbTulMJ6rsH3I9tNhqeOI7azDFI7WiT474mcn+iykz0L87EyfiQWr41IX02krK2qn6aR0jrdWuFjavo6ULyLpR9omVIim0JNmNK9zPF8hfmQu8VJHYn87aqFK'
        b'PtoRz1G4UQtcN9wTxmSN667w8AJaD2J5q/UktrZaL1NabxrvrfDBYT7EtlbrS2xptX5KAc7tT2P9lQD7JdQvUQTg2AAaEkhDAomlrDbIVF4wDQtWhOCwEFPYBBo2wfQU'
        b'Sp9CTU9h9CnM9CSlT1Jaejj1h1N/BPVHUH8k9UcqbbBfRv0ypTX2y6lfroilp9zIKb0o0ym9KEW0NrqCb1MpjRsWJK+khrpvEUPddbaEK7MhrK0u+wUhLHiQryFUaFVE'
        b'4mDFh9L6EZNSLZaAkrU44Up1naZUQqzfVex+QikrzeAAIrDgvKxWsapeUlPNiiRmkULKGRYUrVZV6dXDNkXmGoa5s5X5OQ+SKuvqahOjotasWSNXl5bI1XptTa0K/0QR'
        b'K3pdFHkuX4tFrVGfrEylqaqXr11ZRe40S8nKG+amKecMc9NT84e5GXmLhrmZ+QuGucq5C+f0cob5bMXW5nrHKH1HrDOnEzt2Io1ywkxRZRgjPXpxZPdzlCNffFIwiWtw'
        b'eleyb5nPHZ/eTLMjJTsCsIRvjlVwlBwZlrNGvydF1MtKxvxczSi4SoaISioMfpWMgqfg0/qZfEs7anNp3JFWCUgV5icZ5iYyHCBzICXm8nE5Vqyf7MOO1qYEVSNSO+6N'
        b'HRj3NyJ5g6qRE5kV1hgu2Kz7v3Em0yZyG28xTV8KKyir2DQ0xEKvzL6tRGqkrMiVxcfGTLakzjIsT6eXE7lWoqtVl2rKNeqySCrtauqILIxRq9kYmpZs1mSwlD9yNIPm'
        b'SCSPicVl6nIVXvFHKLQYC9ia0kpSmobtF6ZtU7mYduW2n5GX/cBVU013lUdbFxqiCx1m5MNM9GcEMX/2A/57wJVHR+dIrYaFD1dDdk1VVbWVqmHb+aSls7XaGu0wX1db'
        b'panTWuP3MszX1+JZprVhyKVWLBwVEcQlZsZjBfJOLK6hpBho2Il9DyPWdB8SsNAG2Jv3xXgpHvIPGvSPN/jHN6cRiL62dVpXslEU0rNwUDbNIJs2KJthkM2geDrp6lrD'
        b'CDr38G6ffci2mT8kcmsPaU0aEnu2K7qSe7k9sy9k9mZe5Rojk67mGyJnGsOSDcHJBt9ZBvGsltm3cTJlS07z7Ft+IV3qQ9UYfNsNBUhP+XX7GQNimnn7HX/5UTBqWMLQ'
        b'Yfsxcy3zYJittb4aY92z5OASi20lS9qkFFRfq5YUY0opxbiwSp7K/hYXy7VnfmmLy1njDJsfb7E2mMC6Ma0sPMgel3vgTW3KHj0/xjSHY25Ozk8056e4Vz5vfFz4iDkS'
        b'l1LksLVKV0TPOwxbq9fW1lSrq3/0NB7p1HeEDr3YTpV1Lu9YPugXY/CLMfrFDfolGfA/X/Z83oNSagemX1mi1pLXYBp/SW2VqpQYoajqJFVqla5OEiuVS5Q6NZ3pJXpN'
        b'VZ1MU43flxa/xTIsdeGJqypbrscJSYKxpYwdrpGFgV5zZT3yzTAw8s0w25Fj5cyY/cD/wj3wKmIFZ6usJYIFy0fVa0srVdUVaomWBpWoyAZnDWvBglOpJLXamtUaYq1S'
        b'Uk8CbYk9S60ar9Ap+BVocSdnqapX0F0+XV0NFnMol6x+JEc0cUNzlUW0ymIyrnrKAVn+ShjvyO4eHldypMSWrvoYKFTWjKKBSIlOg1m/KRtJRoyILA+imNtsyphIPnuY'
        b'WGwCIMVkzbDQW5bU1JBPJEnKLRWgejpUZQ8NE+Xta9RaPI1XY8SgKiHWTCZV6L85uO+Yo5eRVxOdFiFLg8fQ5fRIomvKXED0hmh3GvbmKsMyItPxyr3SxRq9hA5L6e6e'
        b'FrbDG7AJ9aFn0Ytox7ywDBn59tWeiBz4LDqaL0MnOSB+Lr8iGV7WEyURaghAm3TyInQkOwPtXyNwAU6wjSvnzaPnJgQxcLflFmZYjiw8U1YCW/LN5WbyQZnQGl6HjfB5'
        b'qirUTpyuo9cZZ8MDYXzAh3sY3JgWT/oxQNQ3vQDuQi0K7OxTol1ov5IoE3MZdBkenjWHXq4e6AF08uwMPpiOrnFhOwM3BS7Wk60yL3Q9VZdG1YynfNCuTHieB5xxY+FZ'
        b'dMaPqjBdV8OdOjIq5EYYXPdGBp0LQmcKNH5/+AtHRxiE+G/ijfOyM7kxwsNVl/xvPXsuX5i6bzFv/V97/cTimsKvY1+/+VRo91cF2ru3o+7+kNh7SBK8Oir9wxsd33z4'
        b'heKew+qnOHt/2/CbBvnNnHkn7d8/mmEY2KY/OenI2ys+31me3Cc9enrrE4WcX9Xv/r8h9bqyMmuXM86/j7230mVKeO1quDoh81RztPqzDuXAr/uD/mU3Ff3jB/37f1/S'
        b'sCYptyPn4HDvxKt7eYVl+RNfvutT2Plkv+fffJ9/Y1Lm/1356kL7CxMa2zqWKovz/nmHf+ftz7L+8s6d9HcPz828kfjes5v+xe/6U6ttjvaw1knxj6IHD6ZXv7diSPS1'
        b'9O6Ev9msf9C66vNWh+tz5zz3xcW//NPhmwfRp2b4+vYsGfCf8V5EhPpP30mdWcv+vgVS8qozUZMVgNeSeDIGngMBNG5hXUqEzI2PdqDGqDS0iwvs53AFulmmG65z0A7Y'
        b'FCVDOxjgPJsXxcB+9BTaSjNGwwPwYERGdhYD0CbYygtg4OEseJIqLtFueCSPKD+z1xdbAQGPYz0PnaK59KjZP5O2hQFZXJ47A4+iS+gc1b3OgJfR4Yd1r7ABdZl3dGfA'
        b'g+x5gqOuPmgTOhEhl4az9MgHTugStx6ege1sAzYlopdYxaZvINWcluNKSIxSb/4yJh8siuPlMLCvwIvdTW72XkBUoumRctgYJSOadV94kI8RDw89h07B5vsTSN0H4Wn0'
        b'YqZ5qpbBM5m5cFcUO13D0Q0+eopBV1kV8dZE+DTuLN+FKFnJLGOAXRnREb8UcJ9+Ew7uj87MlS3kMYCzmknOQzfY+/SeQntQm+lGDLg9y3QVEuxccZ/YxKBjS6ZlZmdm'
        b'ZsvhC2g/aozMhLtyaVfD4W4+vOAAu+mNSU+izQ6oKQeeixSQMyq8VAa+oHWVCv/rKiTijLkiaUTp68oyz6Kx/H7Yx4SSHhlL9cCz2NMYdwqEwNm9za7FbsBn4jvCSUNu'
        b'vm01LTVdpacquyuNblGDbvEGt3ij26Rm7pDQrc2+xX7AN7Yv5R1hwi03z/ag1koc7u7VtrZlbZed0T3SdKJjwkDoDKPXzAHxzCGf4EEfmcFH1lPWN7l35dXFRp+0QZ9s'
        b'g0+20Se32WYoKPTUlO4px6Y2c98RSoY8vAc9wg0e4RiTevo1C4a8fJqthnwknVkdWT1u7/lEN6diqNuVafCPxkjXO7Arvseqe5rROwaHu/u01bfUd3kY3cN7yozusUMB'
        b'Ie2CoQnh7WEtueYbMRLeE0fedQC+MXccgdi3izsoiTVIYo2i2CFpbHPKO+IJ5GjGnFuS4C7lqcXdi48tfU8S25w25O7/rrt8yCegPRcXelBw1woExN2xBh5+zZYHLuy0'
        b'y8EvUS2zN2M8fJiCvB4t+VjBD+Ztc3KD0HonhnEmF2M8zh3eWvL5OozjiLwxxvxxZHuQ2kzxR74UyKcXgQKLq0A5BYL/oglkOcZI8wlGSmFBgul8LgvWCcjDazzBBSN4'
        b'2ASVCG7SmSRBW/NO6UPY6iEkJXkkkpJTZcpDOVUEaYwBNmZcUkMAENn2rScQzLZUVVrJ2kStVK+s0dbTXedyvZbFMjr2g9DjBOGxSN/C3L1Opa3AUqk55Zh93uqRjV52'
        b'Ppv3ec3gj0A4tc5S8/MzDLTYq/8m0IsHw6InFUxMLkhmT3/mzvUlNzGGRRfuTwgpimEDX1n6HFiL31bX2oDS9uRPS1hDq7NwB0YLDg4cwKDdi+EJgM49gS7r0wD5ys65'
        b'1ZkPAS2yoYx2FpM9ZbrRieFHATGWWoBRENkiHrW+wkx2nZ8wMQu2aJy3OzO6z3GJLp18fctFWxgt3B51cXB+02y7Hb+b/crLJ7Zs2eLKKwrInlkbHpiz+qvZ9ze+sH3o'
        b'5RW2J0K++eS7PdcV3zK7MsD6r//+XequxPy9ok/4XSd1vis/VTKhXgPdO77/+xyPoed/ePDewYK3NEEFf1yzz/P3Ew94fdebsfDvVdf26fZH/qHgD/OcLh58MO0d1atn'
        b'ftVgz13RvrD8z5P5zWeHHzwz6H1rxifhYUUfT1tYk/v7my3PLYgC59/8++6K0tlpG68u+8Ov1O/mqjInPBdU99mUE8cyM37Y27zI4NU30aNXe2RgBuP7hXpy08te9p/8'
        b'kDMpesMG5p2FYcfOd0sd6cKCDpbXUoOqtWi/+asZWybSpSsEXeCZdtwzk+ApAuOc5nOr0LkcdvFsgj3omsXww10q2D1m8cyDF1jscQZegHtHr6oNQk8zSnjKiS6BU7JQ'
        b'I7sEkuUPJ2obuwTmm0y/4GHULRvdPm1JhZ2TltGGKoQBEeh89OhVhHbwEgfXebSAPdL5PDyFTpIrbU332aID6Ah8CdPDdrbgSxskZhSBMcSCDbAvYjU9proBNq0YRRGO'
        b'MoojTCACnkON9wmSh1tWl0TQGNxuy9GI4qBLcAdTFGUdgPbD49amT9KivfBptDuC2qGlzOQDwXKOHzphQzd70Xa0bYMdvJj+CHvkhuUUL/FQ//SIyGyM9clHGdF5uAND'
        b'cCfYytWuRZ1Sm8db7W2AxTVSJtN8kzw17Gha2E3PdCmfYFrKy5yBT3Dn9I7pRu8IcqW1d3td58aOjUZR5JC3f3PmkIfPoEeEwSMCr65ufm1VLVWt1c3cD919RiJ6Si9U'
        b'9laeWW70SBjy8e/M7Mg8lN2TbPSR9QVdCbsYdjW/X0ZW4/SO9EOZPcGD4VMN+J/P1KulRp/kIbHHoFhuEMvfEUfjAjttO6hmyZ2cFOiabRRJTUcBemYb3WOo6dnCgSVF'
        b'g0sqDfiftNLopxnw0OBFtif4gqxXZghOMPgkNM8mndAbyadU/Lv0GF+YM5YapKVGv7IBjzKSJaw71+ATh1N7+HY6djh21Z1a172ub5rRI7mZf8vdt13dtdDoLh8Qyi3v'
        b'CWY1cVQJ9zPu+GPvCB5zyV8ByUouNg3jWFhiZzszjM+Xj2nZpv0T+LFrjNrBjyt8lI883kSVzR5EsT2qpsYpBeNTjqiXBUSXpeA8Xnq8jnNzHnBCNA94IfLYcimPDuaw'
        b'fVF1TZFJOaMb5qpKdFS5NF6RNCwsGrGVMu0vuJs1nQ9FZJARJgdvNoHbJpJKHQyeaAieaBRNxMR9PKir7NTy7uXHogzeMQPimNveAcdTengXbHttj+UavOMGxOyBszG7'
        b'ByMXkBNd1nTOfsDq5Qu4E02Datb4q54kmvsfeQGPCCX7CapFP/Z6Rkr1oaXyx6d4dKmjOwq5kUtG9g4UjJKTxDiSfYhH5qJx3Ee3nsbx4qxG9y5wOuvx6apxOH3d/Jx1'
        b'biOgbKVGh19RaSWFP+u4iZLQdVahVEcVOsyESvksNYg0K2urNKWauiKWY+k0NdV05gzbFNTXstpylj7YU0HDfIr9hq3ZrSocOdb4VjJyOGjYsahWS0wM1EVsFlcz8YwJ'
        b'nkdIh5gIYA5JDE/UXfMHRZEGzBOxxPBEyxM94gu+vb5G90mYjAa94/C/oWDpqezu7L7gK7KLMmPwzI7ZnwRGvB81+ar4Jd8bvq/xf+v4luMdLiNbyNwDTNAi5g5gfBcx'
        b't30CCMPETMjdp9l+vAp8REuVh53pGGgrmAIm8N+865E3+wg6Yt9sHJ8ae/By1lmz3Q8LXccLjcQvgxMq1ZJLuaQcltONHPeSjJ7XxwOlpTcTmjcY2IClHJNi99vN4FZU'
        b'bF/8lcSLieefvMn7tcMrDgPuOQPCnPEdHDlvROYp6d7j8Kx4jomnkGs5H1gRfiIJ0bHtH884rMglXaThjiMNp89FnBGFNPliQ+qpjO6MPt4Vh4sOA0HTDe7TB4TT2XY/'
        b'8hDYHGDitMy45pGNO8bMFqqZR/dBySRyTKdjODnDzP/H3HsAVHVk/+P3VXqRIh0eTXiUBwiIoqJ0EHgoD+wKSBNFwPcAe2IsEUQRRSNYMTawYm/RmJls2ia7PF8SkM3u'
        b'mt1sNpttmJiY+P3u5j9n7n2NIrpm/7+v5b47986dOTNzZubMzOecM6mTr4QKYrmbawTQRWYbgSuKOD+/AkwmWOlKAsFFJMq3vmxBdJNzclekxjmGTKqsqYL2ZLWTtNtW'
        b'+t8tUZC+VfiTJisrRypLiXFZSLB06LJEESFDX5Y81l7zU8pykeEGaXrgmcsfNEhPGG7gHHrwiyVLlck83dcusEodrhaGegrf+w2bI/uWng6xTCzU19kANTT9gEbqr2S5'
        b'Uf1BcAkwdQYzxADm4X14btvcjujzEzsnqj3GPSbjUAKv19v/pMcRjy7/a7ILMrX3VDJSOSbyHoxUz7oDJlB03sPM5sXOZphgXRmoyPSUdq80bncIVvO5vQ3S7m5e95wC'
        b'u20D/7u8uomrc+h9cSOyaplxt4MgRFEu53FAuP8anWcM+lTcyH2qzLhuIbgCCK3TETrkMAwoOZhnRp5l9Drm9iPMF3B8YzRfsA/W8Dlb7sCiTm6DjEoOXZMVHIEvUpdw'
        b'zFPJhzFhtmSoI05tCrpRObhToB+VqYhi1DXtecZdU1t2MuMUFhcbzTg0/BIMbmPZkg8xUrPrINLrYEuTrkROLjiyQOMU2W0bObhmdE0HC/nh68Wg2VjDHMptT+MgmOZZ'
        b'2g2mefpgIxBP0YkM1UPauZYs1EYah3+WVjN/5lZje3OosvE5WkpVu8hYNoDwq9Blmobs27p6D+TqPWjkmqejYvNI9c5SYlDv9AH4r6XOHkm9u3i0isBQEaxuQ7ttQ59S'
        b'82Dn5KnLFDHrSl1L47C1L3rm2qcoYkGftbyqJp3I8SVgX6Gk2KDviIZqkSGlddIuy2orjNqFhpugMgCRO3B6+8xN2u0g/a93IdbqsfLgSE3JEm/QlPTBbuCqlqfPGCdG'
        b'ajdv5sV6k8VTW9viOVob+loY29eevWUt8vNrlLUlxeV1pILsdBWke7aXz+FWBgkw7pIe9zC1e1iXqEulcZ9I1k5uXodj22I7RGq30G6H0AfuEphJOhzV7rLm5Ptu3u3+'
        b'dLHmFtPtEPP/ssb5T61x/nPNSU/4Yc9d5ZZErK6oqlKydW6vq3P9w8PQrUaq9BqN+yR9pTuq3WTdDjJtpfuTOP+nKl381EoXP6cg4P+8dW5CjU0bD2AQPglDwIkhhwDd'
        b'mv9rbd1QbGiucFDdBD5b3czT7V/lDYnoyuPpy/nscWvJb7UvtBupu6G2/bh4NEb402JE8bXDiJhwIakeMmVTaavLWOQS62u9T7RicVVFCSieLissrywuMdzx4eCQujYw'
        b'z89n0yXNMErXDNpH54HnwZTL03h+pcZ9anPyZ4St/U4GHQnqKNG4genBLwJCO4rPL+lcct1fEzAVHMgk33f3aY+GzWiN+3i4n3B+Wecy0mPIiso9rp/hOcY9xfp8AjOS'
        b'9B00DC8bCT/a5eNwMjl1LlFmxJQ0fB3GXFeuKsikWXN4ddvq1qUdUecnd07WOE3otp3wQsTHiEYkftOzEF9dpTIinoZvQY+6PuTqRtejcgxInKeLMQxRPN3bkUYGioWc'
        b'a8ysTyG/cJEx+TR8B9jQXVf3B4pYTttf1VFzfl3nOo3T5G7byT/Xwo2yyKsjkFleWWNEJg2/xed0kyiZrq1RMAm0vNxtO+bnom3xiLSZ0SmrkLUZajCJwZO3jRaV7mCK'
        b'sW2uZphtBB1ftDOcJgAZN2PJ14UWjAF/KPjGOH2FQCFkBeJQA9Irh9lxHXKvnp8r1o3PgpFHSFotIjmoyjFPfCiytbyyTFJdtYLFxkaEs6D42urqKjAJ/oQfLuvjRZBx'
        b'1EvLlX2my2sLK2vKV5ew/MnaEeozISmVldeo+gQlK6sHzGV6W0ISA3Q5VD+lwKj6uSfvGggQvfaurTNaJlIEebrGdVq3w7T7o8HoalFH6pFlas8ozejoZgEnqnNr4MQu'
        b'D43zlKFFdsIPAJimOO9OKn67QkEihtIHVPJ4LKWqiqoacLfgAWHrAXgn65LS0pKimvI61j0pEZAqClU1+SyCo0+YX6usUM6BLMEIrYFmoa6X95nqjqwsKOSChbOyOBx6'
        b'0gdcxE5mpXABq4DKKrjUwAUQEso1cHkZLhvhsgUusDZX7oTLa3BpgwssNpTtcKGmHDrhchYul+ByFS434XIbLnfhguHyEVyopuJ/2yffIHVF7sjThMddQCdJtYrH6iuK'
        b'hVa2/eaMS3h9+gMvv25L914Pr3p5r4c3ubh51Wf22s+oT+p1SyZ3PgHdll5/sHJoSz7ie6Ss2012w15tNfkx395qbD9DLqCDF9cPwYdBjKPHfdtAVgvQMZlXn8ypHQb3'
        b'OkSA2mEk1TqEJ5P6+bzR03kPRQLnHNBFNGesnXqtnB/z/a08v2XgQpJ1gYtTv5AEH8p55LaPkFGktvIBDcCwfoZcIIYvFw2eTSXRRj/kC62iqJ+Nfrj73tLMyuO70Tyr'
        b'bN43Yp7VlG/EfKugb0z5VsHfmwqtgr+x5FlJ9c++M+VZBX4nFlhFfWPOI0Htnex7UmlREDn4e7HYavz3tvqLiVXcd3Y8q9jvxNwlDi4BcJE+Fousoh4x5MIqJFIkxSsx'
        b'6KIKb8Pbw/B2fAe3BPMYU2d+bRq6NAgnDX++/YwHcK/BGonUUJYgTxglBD9xS0w5Px1CV0YhUoh1fjpMSNiUhk0N/HaIdX46WN1Dsc5PB+u3Q6zz08H67RDr/HSwfjvE'
        b'Oj8drN8OCFsb+O0QU11GCDuRsDMNs/44XEjYlYZH0bAbCbvTMOtvw4OEPWmY9bfhRcISGnagYW8S9qFh1m+GLwn70fBoGvYn4TE07ETDASQcSMPONCwl4SAadqHhYBIO'
        b'oWFXGg4lYRkNu9FwGAmH07A7DUeQ8Fga9qDhSBKOomFPGo4m4XE0zGo3xnDajeNBu1ExgVx9FLGg16iYqPQrm0Tk78l9NmAWJVdvOa1cTYbzwumk4c21BsYM3nLOP8gr'
        b'wPhThYKiwkqYhxaVcNpfNeUUCqdVC6DeJ7R6YaAZwGLWSorNOdydsTYAbDca2HErgJmukDXdUlxVVAvbSrrUzKuUWvBeeQ17BsxG10LhEuOzcpO4rwoMldPSSzk1hULJ'
        b'InoyTT5jkYSGNuRC2KS1tHN6kDXKEiigeaGKqlRCxlThoI58XVhRIamFlUnFKpirjQzSmRvJSTDxg+mJb+sE4F4dxBDdEs+UXcxBL8w1zeQNL5jM04keQ4MDdGKKQMHk'
        b'CSp0yzwaEhqFREYhsVHIxChkahQyMwppVZkZQxQoeW5hFMvSKGRlFLLWhQQkZGP0ztYoNMooZGcUsjcKORiFHI1Co41CTkYhZ6OQi1HI1SjkZhRyNwp5GIU8jUJeupCQ'
        b'hCS6EI+EvI1i+mhDefycVGbQH21d2zNpNdwyPTlPmJM+OKZCpOUKnZqqGJ7mCekJiTBbOsx34oHfFdrT75icaYNjA+QgTwjXSEGlcF6W9vnsqIEbGlRJNluXiwmhw0hJ'
        b'dt4M/bd5omiOhyVMVh14p5IwuWZkfSHI0dW5/k+uyaC8SNgJwCsCuoQzlSvfIfk8iWYHskFD3dMHNnrSmdLHy+/j5+c/8R/49eJC0J3Sq1tRZVGptM8yBzS1l3Han2IW'
        b'pcs6HROAVThRfm1JjRKMfrNmWfpsWNfGOiNU1G4Ga1CDWsugBjWokQ2wm9FnPcDKnEk+C5cmKVbXKsmquYRkQWVdE4qYqinsE+cvU5XRrJeCgS9Rfgn7Q819WWk/y6e+'
        b'HE3yixYDlJg64SusqVURgVtZAnCdwgown19ZWkUophVaXlpeRFXIiYzNDvq614XLavQF6nPIr6gqKqwYYFfVlOQEgGcVoY8O0iQZ+sv6XOxzzx9Q5WS1SgZjLq6I3C9T'
        b'9ZkTIpU1KlCAp0uGPhPSLtAmZI2rbRm2JUxUJTXwQmrOovNhmOgTL11BSFAZmF8dYrXECsMw9OnVLvROK/ucBpCpder5e1g2gVRPlk2/c3JrrWmPb1vRLYu75xVH1SIW'
        b'alzzux3yP3PyAPBRe5HGKahZCPBM4W5TnWMI6vuhNyAYHEP46ZxHSIycR2j9Qxw1M/Iiof318qX+PCU+hr4+uYeePlRnl3to/OMvhe99tFG5H/AusdtaG0dLmF8g/Hrr'
        b'wiHh8CvlaHvg6Uuz8fNnY2lj+0pPTjoy6UTczozmJNh6ntI2pSOStV3Y6+XTntu2uk3Y6+Jx2KvNq8Ohx0V2z0XWGxR6PuR0yE1ht9fkVuFnoPihNWEY0h2a2z1rnjp0'
        b'nsZzfrfz/M8c3FqTOkSfOsge2jB+Yx/aMs4+7X4nQ46EdIl7nGLUTjHdtjHdTjF6T6cv4CtT+Ufe8IrKzgM5RKuxbCcwMoWrtyU/KZcqOVQu1dumC2GN4dZUccb9QIGz'
        b'mMg95aWriJRjIIm8oAqzEnbvh9P15fPBixVj6NlhjLEzDNBEWFZVo7c0SL2ivYC3CeW5EehxBnq6dPQY+74YTA64Z/vPjTIqL41AjdsQtWPo92IAOZzPtf+8dqpHoMcT'
        b'6NFbdJIO4eriZySJVtFbI5DkbUzSb+IlrGc9Ve0izpwJtdYAdHD6QJyngqfSS9Vq2IQoUBgWItXkM1hQUPPqQ/g+kEkU+mel5SWQIbcKIKmTCHrtIb0PUEkQV39BIeS2'
        b'vIb+aj1XBFHYaxDrBiLoBVyZ3BuhEgOhEj/WVWLUYNvZw/B/fMKs+DBySX6BPkkI+2L48Y7SF2xM3yQju6lgubpkkbEF1YF0JuYkJ4UlJSfkvhidfxqBTpnA0BzD/H3z'
        b'WXpzKDcZiHucTprWdMQAZSyZJIma4GZVxypWFK5ScTZEJZUlZYWwG/lCpfhyhFKMNe5SQdoupVUsMygIJ+1JAhUzZ819IfO0yj+PQFW08VgYQCe1qqqlsHRmLaeSFXV1'
        b'dRWYLSJydy1ra/WFKuqrEUgaDyQ58LUk2eTqzMr851lztfGXEbKeCFn784xG4mVkjCksKzHoBtWLV6lA6VAyPT5dTsakihcgqpOn/HoEouKGaCI9MRVVZca0SAIzcpJT'
        b'Xoxr/joCSfHGJNFxvaSyOLSmKpT86AUiSWDyf04La/5Z+bcRaEkypsVjSKvBksCs/5wQTnz8+wiEpBpLinqvT96s/ipZGFWCBRSuc7OGn6fn5Ux/sdHzHyOQNc24O9nR'
        b'UZ6uHzkjLy/k5+jhCLlnGbdO0MAxG1ajoDwE94EJ2dkZ6fLU3OTZ/+mMwhrSVH4zAlXTgSqBrk7+OZAq47WzTJJCRsHUEkJnJZX4Vbqdy6H8DZNhe1Z6Si54EQ6RpM5M'
        b'DJFMz0nPipdn58aHSKBsGclzpCFUEScFmHMxl+ZwqSVlZ5G+zSaXEp+VnjmHvVfkJRgGc3Pi5Yr4xNz0bBqX5EB3U1eUq0AdurqiEFxOsDauX6Rqvx2hamca9wLZPQ9W'
        b'j++Jj8GEx25FsF2gkA4YhSpSzy/SO/85Al1zjLvBuIFNzu6kyCTxegNU6fKUbNJ4SfJUmAWBOV+o5vpHoHA+UCjVTT5OuVTiYrd1CFMUAzdWvYDQT3rr4xFIyB8w/3GW'
        b'z6lhNpaAEv1+veF69kVa7tEIRC0y7qwebL1oB3awQCCBQ4YhJmIdzuB1ng4GPQQpuq3JC8NhUgxUT5w51ZOhMFrDKEvpvwY7h8N9XcnL5fsws22HwiOQL4bQ9NNuxOYx'
        b'FYYxzQfH1FHvNlyMoWumQvT09zlWg5+RmNaDn2o3kyVP5dEnE3NYawpwrKOT39nlhv7waOjliExqqvwDsC4fLgM8qdK9WeqMSQjcJjBwt0p3DqEmdaB0i7KSGt3Wr9vA'
        b'jSGDlyXkM9U6hm4fgs7Our3rYI9sfNv4HrfJHQ7nXTpdupKupV1I6w6c3OM27a7Duy5vuTQn3fcL7ki6Jr0gvZ775vwb8zV+03TO10gCEdHXPC54tAoPW7VZfews63Vw'
        b'3pu1M6vHIVLtENmV1BOVoo5K+dghdYCvtqE7ILDSHqaMR2QFvjyX1Qsa3NMA+TB4A0yrLlIFAzr1pAJ6B09BG81nhu/tOga0HQ46qT09MYRChhnikzgnkD8CsULYZR5C'
        b'1dCU23/OH6o47BsltBmn4Gbv1GPvR/5RZdIQtVuIhmJqP3Nya01oWdls85SazX2Wwo4ett8MMU74QTuBAgU9ENGWVEQZbWityoqSSlLSIfa26YsVUFDJMAXtcRurdhvb'
        b'7TC218mZBflIAKas37xnuxLtNrA8p3undPpQgnFE9ugDBm7l93ABGZQKXexJCCw66RqCPSd5AHcgKNKljhJsQFKpni7H2AMU2KqgK2gqZVMhg86XdFpXfg4XOFmha0e5'
        b'1H9Y6BHd7qdgoT7rAUc2tLPTsUE/LAh43IjQZ2V8YiPmDmxMOGldmQxJirnDGhF7ViOkRzVCOKmhJuv7LI2OacTcKY2QnrhYDziPsTA8jhFz5zim+mMc9gjF2viYRhnH'
        b'5/qrMhnu0uFCMUbP7AVJ2cvjLgAyUD3hcaggMyvbx6NlVu79DLk8LOYxnmOogfCchyK+Zy6vXq63Pz4JLIvHPd1GuUEczjb3FLDNHc+aKKeP+vlCx7CHIrFTOHlmzRoS'
        b'73WYBlbEM3n1WSQa9whI8MhlH4HZcmk/n+c44aFIMDq2PuWhqTaDqZBBgt4GOqFiMlAxhVJBP+x18Ad75wHU3DkHWAK6HONZwNLgz7gn4+DJeMMnkfAkmj5x96MG18H4'
        b'uPuE+kx9ZoGQWRDNjPsKaHRIYI2y0wru5wscZ/AeikSeOVDHloyb731bMuiPJxHdYusz9IllQmJy1lI7B6wKBWBVGAVWDVEYrgGBUM/oevl3rDV3npX7N2KBleQ7c4GV'
        b'CwtLAltzc2bgCxZ1VtWW0ml4G76Gm4PlmTIw6IJ3CJigxSLUZZ4yyGEl/PkWDOIDhtMYn+RK+tV8itl01Q3iSjF9IjR4YkKfiAyemCrE5FuzPH4UD7BLS0yV5gpT8sQC'
        b'rG9H8QG/RJ5Z0vfUmrrSCjBMSmuFpdKmzIpME9Z99gOGxMxyVU35OkKxkZckvnYsH0/H8tm2eilqtqRCN+rPDq/QjdZhIGvppqcyToQV0nGtzyy/uJYDNJqBskFhRXnN'
        b'qj6fgUekQEy+Ib5GpdWUg1mhz1SXiKk2Da3OnMTAyrD7EKnqTA6vh6HfhR36Pbx3m/d6S3dbs5cxgXrHlv/5iYYXf/iTtCEp056mvQqy/AqGGQIs/pxbVAXDk6AsI++2'
        b'QE6rf46cCkfIqX74nHSykYzm9KzQd73T7iQY4BcNTQDMAMPyAZV1tgp0qosg0ySxahUap/Bu2/CfEzZOiKM0DgMcp9PUIEGao5TKKtuBUIAIadHt7IGxxims2zbsWeTb'
        b'0hHl22EqipVxm6EJE7RLTCO7Mzo1C0ve0zWmio0hYjwjOy1DaUENyQLUur2UmjEYeoU5xOqQfmMDo9ZQq0Rq3wZo0wPADOBrJEXLwd/k2Ax+ptfDlMDItxjMCYUa7qAs'
        b'A1vPi/SmuwMG1HiAcfTiqhLWsjFrl4b6R9CaCaTCD1nPFfC4YZHKX0pQIlACgIiF1wPPEUmturqkslhrkMbCIAs26rAqYoLC4uJB0jNlC/KiBTgSQCiUI73bgzte7nGa'
        b'onaa8pmrb7efQuOa2+2Q22vv2WPvq7b3ba85uerIKo19eK/bmB63YLVbMKc94jap18335Loj5C6KAvJzNa553Q55vbYOPba+alvfHtsgtW1Qx8RPbGOe0iMBIafvkQMV'
        b'SgzNPQzqe2lQSS5DlZKuLA5AOa0Yfc9rWdVtKxlMipH1SeORzJ6ZyVPxw0i29kyaM8NUjRpSHWMIdp7Oz3JlEWQqfqWBmq+Kzz4p1Sr59AlUtcuUctpBebrC9vFqjBR/'
        b'RTVVNUR0HrKw9NVhKKw/w46HrheSNG4TLiZ1LD+c1pZ2WH5AfiFJ7TZB4xTbbRv74z23CXTa3eoVbioV9lkbz9h09mFXMzA7yKW2Q65I9JoLlIf17KsX3qksD1hB2lDK'
        b'tTqBXjBQjAdm0AnxC/ncBaQaFUAFiRD/jVhoJSUipIO72j1SYx9Vn3TfyUstmahxmlSfZnD7jZBnFQEA9XDAxLt/LzaxGg8Ydm94NpGVCWFUwzv8XXUyoV4erEjHl3BD'
        b'iIzHJOGzJpmxs4zkQi2Y81tQOohzHSgXkr8C+lcoEymFgFRXmChMFWYKc4UF+MBRWJM7G4WtYpTCTmatFOXx80RE6rOnkp44D/y9m4LHmzy7PJcoE9Z/DZEiTVnkuU6K'
        b'NKNPRrsyCieFM8W2m+qw584U226qw547U2y7qQ577kyx7aY67Lkzxbab6rDnzhTbbqrDnkPYlqUrSgD4c0LRKPo+PJyZP0oPwk3ijeMpR5GYdjrfNXakdDzOc409vWf9'
        b'1jh4MtRrkIAaeBXrfHZa5VmT0tvS8tvnOeQ55o3Oc8pzjnJkPdws4SkdXZg5JtTbz2hF0ASeYizkR+pKwPq3MfA9NFoX01QRysbUersxiOWkCFM6lwUTuTqyzxJ6lhbM'
        b'XX5UAF1weh8vWyrq46cm9PHTk/v4yQrym9vHT0zrEySkyvsESRkZfYLUhOl9gnQFuUvLIZfEtJQ+gTyb3E3PJFFysslFkQwv5mYorWC6FqSmTyeSPD8htY+flKEE4xck'
        b'XZJ2Wk4fPzO9jy/P7uNPz+zj55BfRbJyC42QOJdEyCPEpA9SlaRAbxjQ4/g6d+NgOpchKwmhztm4+Gd0Ng57boOWTHQM1Zl3FcprAUiMbi+UQUerwQ3ZMrw9C9xzpun8'
        b'fVJ3mLJ0aq0y0zoqJD1rRhrpf9PA2CfqFDJxeIMNuvwSaij//l9inioGEld3XSoCB5QO6AFufu+ju7YfvceI3tp2YnpdUFGUfWZU/R6eYFP4W7mCw6fCq68yjN1N0Yr8'
        b'PqmANSd+CDei3RaoMyRNaz5zrt0ofFOAzkblUmOk6NVlwbgx2xftxVsJHWCQez9/JTObGuB8Ca2fCH6k8Y6MULSD/O5Gl00Yi9F8vAU31pLFzlCbFEJ2dDMEbToYcpsW'
        b'sQnjvQr8wlGviB6Mg1NryD37MXRWzta4Tu92mG6I1tRaR2HnSBM9rFQJlpqHMiVJ9e44r4F6YpTHScYXBQY+kQs9eDwv8BTo9byeAl8Tj2FOWEQIigyFNWstb8DgH2ei'
        b'ddm7ULhQtFC80IQwqzlhViEZAkR5JmRYYAcCMXXmZRtlzTGwaa6FAQObEQY2NWBgMyNWNY03oww86KmOgTcNZGCdow4dA3vJa4Hf0KVQvCVD62ONcGxoKB+/LgNnstQX'
        b'K7BS3vQVaFMa6hAwuKnaAjenoiO1sPJOjU/Wf0kYOzt0JmdmeBrejhuciwgfzQrEDbNMSQ8RMugGOm9hhQ/ZUCWIhSZixnItGYkkBSEdEycx1KtC0Dy8gxo7TpjLw00M'
        b'PotPVtPYWYmmjO3KNiFpX8tzM20Y6kViNWrHm7SOH6bjk9TjrLHdYxNmjsJk1RQX6kXCHF/LzEjPygjB26U8Zjo+biHn4xML0clab/IW70ebZgSngX1k2QTcEhkejjYV'
        b'ZDA+6IoA3cG78e7aMIjVoIoKloOV2+1ZeQaWlQNl+Ay6EBqI68OCwF1uldQUX5pcQUs1FrUty8CN6ZnBPmFiRuzEtx67hLI1pWouuomPBEM9F+GmUPIe3eSPQ9fwPvoW'
        b'tVTgs8FsK5gweNtLpsv55qgetdRGQiWaLlXoCIDMxy6F7GcEUift0wN1hJow6ABqMZ81N7gWdD3K0J1cBaEAbcY7ApnAJNRRCx0KNeJWa1UdvihkJgTyUBuRI0Lx9tqp'
        b'5JW7iSOp6e0hMtwEDj6qSaTcQNLKjSEhWXlpuClb68tY764PH6vGlwWWeAc6irbUwiiOu1ArPs95qZfirZmkuHgXarZPFeCDsSHUTy+6jM6M09Uw+WZrvkUGH72Gj+Hz'
        b'tbC+tRTh7Qpw6kGGus5ctti00DR/8sH51dm2JtW43q0WOB6fK67ALTPAYT3ew6xmsiK8WScfLalkgLuEL6yow5dRwwp8sUbM1FVbufFR21xhbRSJUlOE61XkOeHqkJmB'
        b'00JDFjiRGpjG5aSvXFIK1IKvmzPe6EwtGKnC22aXB0PlkMpqDMM7FIGBZDSuD5NDTaFmc1JZLHOi9ajTjFmAd9GdPNyJ290t8FV8WYWvLUfbVygtl+OrYIr6qlOkAG0i'
        b'NdlAaUe75gDjE67PCpWRGhcx6OYSO7RHgM4loou0w5woEDKmNSeEzNSCigNL4xjavvgWakZ7VctFjNMM0rYM2oou4HPluzfa8FWwj3/s60d7cjMUKNz2d5cd5jZfDvyB'
        b'v/nzYyZekdZO+SbZC93Ldv39/ZbIDqcHX4c9/OlmZ7H3ifZHu156/x8v/T5u15ofRdejhdu6xpq3/yB/abRzDLPwbff1o4/++NP+u2mbH6zzDXy4o3fK7G+ye790YBR5'
        b'b+747mjn27/3/d3NN0/Hb3HsPvPyvoKWsdNCDjedm9LQmfjvhiX/TrxWUzMrYoLvuoyv/efFtbXeVP7LtDrgb/9Yah4ePud9u7PR9isLJ1pvO9tUFvy3mLMJ1vNFN+KT'
        b'yi/tb5h/piNxw72zibIPFv3lZuVsq0tM5CffLKv4xUmX0hvd81794tU/3Lnq8c6Y0msJG14LbIy+vfW1W+1103ojl771268cHZf+z9XgLy9/V/bqb+afDbdpK3uUWoZ8'
        b'8BF8JfLXZ85OXPLrxx8m/rL4zLkgi5LVMTaVlkvfLPhtfsvB3/zi9u8XvN0a2R7o/Kb73N8knP/r7R0X/nrW5svYX71/7XjTWo+rPV/3TpkX49YqH3vr8XyN9a9ERz7l'
        b'/wV/9W7Rb/5RmFL/Z8FfZJkr+Vtne5j8/eKf+tzf23Ur6dpf3/A7+tGlL36ndjsgt3b+xGx5WNe0jl/uu7Vp9drR9os+efTO2T8Xbd4r/i70ZvjiuzOWPNow7uONXuV/'
        b'OfjX0f+c/5cP9/7uo0MH3W7Z/bH70EtTv/m3Vf7p4gXhdVJf6tEDXx2LrxgJCg45rKBgIad2w9cQ3jxDujdqCpOHppHR+0CWBTrPx8dN1rCixjW805t6fS5cYGyrOwp3'
        b'sU5D7vBmoMYV1lbmSnylyl6Fr9ZYiRmH5QJFjB01PZ6PW/CGjOxQGIsvgtsQfB69RqUUfzICN2aStYuAQVfxKQG+w0P7w1EDm+723ARCGJGypLieUOaC2yzQOT4+iq54'
        b'0gi2MUSIabSpw1dn4C3V+EotydbCib8YteE7rBB0GZ+wBrvv6IRzqNbueyfqoEKQHd6MzhKpLQTvRJuDpDI6lDKMs0S4cB0hD4ZPmUlchixLzBTiJv4q3iR0Yhl1ZT3L'
        b'YjXp8lvJyETo9iaj6AQe6V+v40Os5fMmCbqTQQY9MlqcRRv4C3lh6DDe+SiMSmV4H2pU1ZH+3krGSnzNBsz+25hameMumzoyEuCrK5aTUmQJxejGmjCa2zgyBOwMJuNz'
        b'Jn4TnY7gMeI5PHwGHxazbmPIlOWOG9PQWZL61kz+Ol6Kp+kj0INLRG1kQG7MJsPnmbQs1FCEr+EdMvCm7oquCFesQO20EpXoBNoH0ZrILE4aw4RJwTstpvLxa5a2NMK4'
        b'2sVgHR4cCjTmaMeh0ZlCK3zd/RE7dfFxO2oMI0xGlptpIkZcwPfBG9EJWs1k7t6Dm8lrbhglY9hZf4tsPnm6HW2hlMpXiSAHwoLZZP26g+RBZngx41LghY8L8SUJaQ3g'
        b'1BL+Wi4aPjmVZVZrIqwkoUNCWvGm6DQ+RX3/bI8ak0nqKZ3vhLrmUxv3E9G+Uuo8PFQmzxROykbb8Q4SxRUfEC5Hb+Dj1MK+H74dTWoiU64M085t1gpBljnJH8qpnJtI'
        b'3spCiQCUQfi1o8ACbeXjkzZzWBc4m/HxAvIe/D01kXbZgA6bjucvCkdtj2A/A98kk/ku7XtUn83mkE7YMhxfCAoU4VfWSmltOLvjvSSePAQ1hHHTCamzc/iQF74mEuFT'
        b'+Dbtl5n4DWtKDicGCZkitM0OnRPgRreiR+NIDNHkMugdRosW1IB2hBlvFuBtS4MJq273NUeHSQEfwUZ44EKzoT9Fnbg+U0pm84P4RiZjgi6SAbPjEehERsYS0mAi3AFe'
        b'3klbZ5FiNoVlkBI0sWdUPvhgKrpggna4TWC9F71phlpYxghFryDtR2JmNCPAb6aiy/91swyG7n8MzTLQ8xvHAYsb9uCGrm7u8unq5mGFB2hDBXTE9DhFqp0i6RKHcwb5'
        b'wMkTzBD2OAWqnVjX6yka19Ruh9Qvnbyoe8kwtVdYj1ek2iuyK/Va5oXMu3Z3vbujku6WaLwyn8vt5JdOHr1eAR3Raq/wHk95V/G1ZReW3U1Xj5P3eBZ15xQ1p4Jd2wVt'
        b'C3o8ZGoPWceK82s7115PuD6jO2zKXSeNR3pzygMXj8MebR49LkFqF/Ap7zK2Wfw7Jw/WYfzdcWqtjZJeL38we9QR0DVW4zWu2ZIzgtuytlnYa+/UWtde1vayxl72W1c/'
        b'jWKWZk5+t3+BxrWw26Hwgb1Lj72f2t6vPa/HPlhtH0yKnHEtg2YwTeOa0e2Q8cDdB6ykta/RuEc2m/3O3r3d6aT7EfeORR3Lu70jrrtovBNIur/xD+7IPT+nc07Xqk9C'
        b'4/sFvDGJYDTcLQmMhjuSK5l3vNpDCBFdK66tubaG5pB0t07tn6VxlXc7yL+092yf+PG4TI1vJle8iWp/ucY1u9sh+4G9d/t8jX0ESSQwBDweHF3bExCjDojpCZisDpis'
        b'CZjSnPSJg9+DgODmpI/Jr5c/1eXzCexwU/tEk3sbnV4g+0arocfpH7LmhffPp1F8A07GHok9GXckrsc3Ru0bo/GdAJElvZIAGplLgtP5GxPAaiH6hbEpGrgH5U4MqY4i'
        b'5G5532dMe21PwBR1wJSegMK7qe9mvpXZkzRPnTSve36BJqlQ47OoWbjHxmDRPYozeKMFVAnhcEAJdtWVoDvfZ1FUWKNTixWrihaXLCt5VkcPBj0OulYB90fX7/QdTvkh'
        b'yesaLODBXNZPpH89XkpW8Nm8xwxcv6HX51jJUxcTx8XRzBWLeEbwAghqUOKlZR7uPNV4pNAepP5gBGf9j2GpyntPOdz8mLx7YgybDQTwpc4IBEu4hHMUIAlUlhQWh1ZV'
        b'VqySvoCCI1ctFvmc4kV+efHTCPyXMd449J4Ha5X1SchQyhvlKj31huT+x0fhnTyKlHoahbD9aKD445lLtTZAZ0OnSPWilLAn1aAYXltTVVr6NGoEQqMGDaPqALU1oeQz'
        b'CejE6/VKgEKq3/qzkKccPwKniYEwPfY4iGKPy0s5sPEygIqT1iupBEsfxT9blVnmGww/TyPPDMiL0NUb1ekAPHQZ+BTTKWz9LDUVOAJDWQIpeqB4wPBuiY0JMsxLd6y9'
        b'iNE6Y6fGhATcTiKTa+AzrpLnSUg22EnkGe0ZMvE8upM46OnzbIWL5UNbNywA+njUJzCY09F6ARb8jF6AN0n5T/5lnmLo5NYYWqySqBZX1VYUw+k2Geyo/3NJYVkhAJLN'
        b'azgLPZLEipJCUK+QJFHrFMAXnAdcqh/FuTXn1AvKVeacd/OCglxlbQmZtMrZjhe0tKqypoqMrEVLgyQV5YuUhSQhUDbR+tU1B42JmkGDCImixTCy/u5YhZVVBnog5kbu'
        b'2gsKUgorVCTnAV7odLyqaxuBvNz+fUcBddax4pW3LhUd+MAW2b693izXebyGkUb+1YJvbbZVyqOCdyK6PR7kbnSWrB6bBgre+Nhawtq2WtbmjuKFpWUlNX1+RjOdqqgi'
        b'n9YCmfOgoKo4GcSiIjJ8DwcAFRLGXQI2CbodDPf5OTyVsfxAjxgKtCBv5T+hK/eTiy15roKNuh/XM98tkPB4ds+7ob9T7M0csQgRDG1pdzHtYJy7RhHdsufpTpz4ucKf'
        b'0VVj2TOdOIHHKdyCzs4ZuKCCffeGzKBpIehULmwHMw708KkhOxP2otFp1GAxIS+sPPphIJ9KUQ0Vu9lTpjNvMbyGsZaW3tviLVuZEz6b97/ivc9ljOuHiz8wLTw+9tXw'
        b'QF7WhoeJrcrWglP3XMZHMhXFwiLxT3dUUsGjcKDmIrqCWp++vktdhI/Q9R0+toB6x8W3inEzeMdFZxYbOsjVOsdFu/HeR7BfjF6RoYPsShA1uPoY82Plgmc5kCIMqnom'
        b'BlVxDBrIMuj3Sgnj7EHWJf6Tyb/PPIO6g6dpPDO6nTPujwnqiD66tDlpT7bRARVlXPunSb/cAZXeMKTyMbDyD+TiKjRwbbacsLILHFC5PI9rM0DGS/nsPu850vibMlIl'
        b'dHNNaMNDJ5ehPeyr04XoSsYkfC1YDq8ieegSOrO2XBX3BwHtShN+jL9UdOgDybu2HxQj5w8Df9H8i50mxVvGbrnYGm4S+cqP20aNf3PbWx+uzgyyPODCHPid+N4JC7YG'
        b'RsAxG5rD1NV/3+ih24W2BGfatVdo+t1ciemo4McOglFj+00Zb3+13sSlNu9h69w4b+WPUONPyMVGO3jAgmIeqXGz56nsDcxwNn3prMyns56QzHv8/8q8VzrycEFG/k0f'
        b'fSVSwdZRuiTtUtE+0t3b37ZFzmT0z3Q51uF92VxQ5spkpvHf8FSRGQBOA+fjLnTxqZtDyxZw20O6vaFF6LiUb1DhfNr9DOCDA0+DKW6QtrATW/0Pp3ozzm5DQAe1jTvE'
        b'nKBvXIPzXorL+TcYwTCYGb5/+Tlnhqc0bgHzXxdpBs0Egyd1oTy3/IOKRL4KNnp3SnLv3oZ5vflX77XxGJPXeOeyr2vxlANmaxZPOXADiwVS0gYxYxukP4U0iPtzTssU'
        b'D8UjjOhnOC0nez9n5T/k/z+s/EH9arBfX9Kv1kk+FFEkw6svz6ASFUA0ljl5W8ZnWjpL6h0VHzqkJH53Kry6lHwTJwj/9wEyW0LdzUQ3wHv90QkhsL8rnMpDV/DJWbTn'
        b'haJta6DjzfUYaV9W1/HwG+g23YDGp3FXDutSNVTMmKK9CnyLj3Y6CIbgAAo9HrSFSTHHlAMkLAc8ygQO0OKOe9zHqd3HadzHG1g0f3bGoJA5E8IYAYaMkfEfMYYh8MJd'
        b'2zbHgDEchwReAPLKmtpb1WKvxHn2FJmlQ2DlueS55pnkuZFFFJPnnueR5xnlrgNlWP2MoIxBS6nBoIxJcjpJL1fhUxm4EW1Ch9MzOciAcwULGYBpHm9G2/EefAzvt1Di'
        b'K/iKDRwW0wNsW3SMj2+iYyoqK85clk/Pr9MIa2SjM+wh9hBH2ES4v0OPsfGrKy2IQLcVH5aKKSUJ+JIVuoB3quAcmsHNDNqG9wlrYeAZg47hXfOX4Eu1YvLmMIN24nPL'
        b'6EdCdFOObqJNFvgqGaDxFQYdwa0LWfHjPD7sj0/NUYExZ1wPB1/nSQr01TF0zhTvZCyAffB5BrWifegwzQptxJvxCYcpKvDHhXcxaOtodIUec6famjCWZCXAVClD3Esj'
        b'mFp6vHcMtUzAreg1ON6HxI4y6DV0wYpmI0JH0EV8wN+wRK2LauFgBNXjk4tohQ2oJ9xVo8SXFWnBcLhHKmqemPTBZtRqtg696snCNPahW3hXJG6ODMfNeIuQ4ZEawetd'
        b'fSgeADXgBrRFi1ShMBXOjHDwDHQG1U+fhfdETlOYMHm4VYyvoNsv1QKMOyV8QuQ4tJvcRTARUYm10JuSKybjlnXokABUWsJQW1nFDz/99FNquAi4SbJ+/rKQ6/IgpjYR'
        b'cm1C61MydBnh+jTckBECS4XtYdPyAnEDIUIRKMU7ZqWlZ4GwnkXYBF3NAUYQV1otKCMiIywWatBJeoTTaBgPeIqMRw1h2VBHx/EtCv4wAN8AN51GtyzxxfC8Whi6cctC'
        b'3G5FvtlphdaHm4rw+jx8SIybcq3w7eUpdq6mk3LQLXQbH8Lnk8tWmpU6LTfHb4hXmKKtZtmWqAtvxMfC8e01Ui9cP1GG94nR3kQpuhQXhducyQpk0+haUOzEG6PqRPgV'
        b'/IoVE2EqQF156OJcvEeMbtSSNtiC9gShTfg23oGact3KX0IdeL0bur3Exw1dQ9vQZnS1dA3eJIgIJDRs98IXkuyzUAc6rwRGo9w2wdyNF8VnTPuzF6+LqqlkaCfzR5dJ'
        b'T2jMQmem4/p0Uvow3DCdYqd0oA90lnSpE2nyrCy6HDuHr1kU4TP4AE00LzmdaWaY8IKKJUv+HZ3K1ILJTnwRnxBAQdrMGIkluZm5cCnahc7gm/gILwJtwMcnRpImaSkg'
        b'M8gZvC8vAB+dS6he75iLNpSg+jLcjq+bLEZv4H3VtqvwSXSZMjg+IDA3oBRfQ6/oqE0LnSaycwRcIuqUkn+kk+HTZviac22ulFcL0wLeIyfi4RayuCC8QKYl3JQeQsYP'
        b'0tBOpsLw5OW1k4HpLi/GZzJCp2Up0uiaMB3wVMEzKRJSx/tNaSHTMmXpoUGE+e8QPtkqtSwn3WZbbQSksIcvMwTPhOHzRviZAeCZYBtCHh0k6tGFeAAO8Rh+mgA18RKD'
        b'UFstaB+g20uLg9NI5W3LYjtC2LT00BxVCQtuM4RPsTgisoiuhlFgek7oTD6zKtdmFT7qQNmLLJbWK1n8UjossBu90O0wWiBYhKdlZtPSymaYAvYgbVqWPCRUTnF00Ol0'
        b'2Ck6UuNtOaPQ8RR0hDLB+AQBlTUe5FVWfL5uOpHdaunh8eHsInRZnqE9XDbFXXwySp3CG2vhGAadistQZEuz0EY31mt83iwA8A1A78HwcwqtJ027C2+bL0Gn0XV0LM0b'
        b'vZnmHYnOC4HXXrFDbXizBwVppaBXC5zIyEn+2piZ4os2+FLN8loe46ASZE/DJ+kI64W78C4FDFpprgIy1p1h8Bm0BV2thRNffHU1Op4hDaV7EnJCVCAVYJagcwaKiQsk'
        b'pmgD2l3Bjp4b16JD1tUKtD0Xb88jXUQUxCMj6j4FHbEV6Dbaa1FnzSMZXc7Cr8G4cqCUIutS0U3cZvIybswkL8czuCkRX6AoMpJNJ2qh6MREf/bI3mIuH59Dr6NttSCo'
        b'oDezZrAQE+lMAcMCTPAdM8pJQiG6zQI1+Gi/AnAaG0gHgq/W4T1zWdyVK94qYoSePPR6LNrNAtduTiWdn/IGme82B0vRKSFjaStwxDerKbyrSIl2EsaW0h2PkHSAGkBK'
        b'6DRuFpHZdL2oNNeLGprHLejVGehUnW7s5pGGb+WjPUVRlIr5AenBpEME4y0sCMCyTECW+Lco7YuW40MZhBNeRi2EPiEPHV6JD9A2S7VCzbgxFO3Ae+UU5CBewHfE1+bX'
        b'suAUvBf6nGxaVjjeR3hxHA91jnuJVrI3uhgFPRpdrRDQIh+NdaIp4p2TyXDaSF55kZGFEcbxgLdwKx0t8tCGOcFst63IlhP2hJ4rIom1iMzwdfwG7ev4QgGp9kbC3HK8'
        b'DTWE6WsnCd/WVpCIkaNXTMj40Il3sfluCYsh49ArANKRkuHHbAIfHUdNIWyXaSCiRxPh3ssqfEmIb5owfHyWF+qBt5dPXWnHV00mM6dmRe/2mRlVfVNtF04JF/Pf8l6e'
        b'6blp+YyCtHsnjqUv2TW179TWoLzJ3n//1bSdyvrmxVU/fDpz8vdTLv90rWij029udT/pCpn4+w/XRk6M/P5/Nk4R3tz9nk30F5EnIta1//qx9yux0SUf3v/DiicWD8UB'
        b'j68fXrlpkuNmR/vJfRdLf+9T3P7R4/yomabRb+9x/HCcw4emlzLtvn6v/MrHKx+lTmnOmurzj/1jK5sbC3MkXzwMairYYXvu0h++GvX4vRa3D5u+18wdc9Eu5uKM9QI3'
        b'D/TB++8vtvjuUqxjtTL2tjVvy6eO/zvauW/629d3piW25N1wufTvpsysm0enzrKPOu3oc5B/OXaT09ud0U9CI377RWlc7NcfXH34cUt2UZzTeyenPu654HTj159mLvh7'
        b'8Lt/to38MzZzF70u3zz5jc8CU/oVESmfTH//h+U5n/5v1WLfy6VxUeExMw99HnX6xpWP3avwzD7FzUN3bUI/bf2x6GB0QuO8UxV+tWk2s36ZYPG/tTffWx3zEe+nsqO/'
        b'b6oa74blQU9mxpZ+GdR9S3o5YNHfwr7529lPvrt3M0KxI/r+76bP+uz9l8x/k9ljEnV4rtnXC1u+/o7Zd+PJV/euHogofPjnl3+9Wfrju4/2T5IsOvxkbMLZLR/e/EY6'
        b'0f3r1/su/qs75zfvvzOxrj0r27Fuh13m/vXB44u+/4O18vOpX3ueieptLP5n1FtpOx7NcbtxeNRfCt9NXPdl0283/+JQ8ajfM90Nxa8n2P+taVOt7V/vqe43dtSt+Gz+'
        b'4qo/X/lj3N8tFh7MnXyg7vUP89+r++Sfo/qPfbXu04O/ruq/MO/MjZCQb3z6bu8OfVsRPu+3tzPXLfxlrI/FJ9flDvXdniZLF/3lF7umvuZ36HPnS2uCf3k/fYNza8NJ'
        b'xz2rXd90+ftXC9xeu1t4Je5XN9s2Ps4/uWLsoSaHGbvbt2bGCP6+qyty4dpPey06/vgkZ51b4IRZK3jTFh754mzOvdT31xz/gu/vtXtXz4MHq98/+6d/ZX/41b8nyD+f'
        b'mp23edTj3V6L69/kO/Us/bB3472v3Sr/6Lp+y1/X762+/cqYc9eC76z5+LN/9PbPuaVGY5esy10svfPH66F3HIPe8Ll+NLvj84+vXWhsMnnHLn6KtGL3qEtfRX2YmPz3'
        b'g79R/zDjMf9fZ+467W1p2Hvr2KPvwiwzf/HonbVSf4rfEuMbfhw8DN1BnSxEjOLD0H508BEMHOjCRNRItyD5Y/HBOl78DHSAgtPQZnw1QDvCnjQnI+xY1Mbu+G5Gm63Q'
        b'VXSHIguNcYX42hSKqMKX0NFRaH1ksA45Zoqu8OsY3MjCAy/h24l05CdDwWsGY78lbqLL5fjF6AQ79NeiK7qxfwO+Q9Fk8/AlBQt7nO9HsWQs6hEdQuco7aqk2cEZS6cC'
        b'dSJGvITviddzODBFLDpP1kobgoNkUrw1hGHM5sC4dDqdpboVn/ANlqHtaB9MjCFk/EVN/FDUGEM/riCjYHuGTn52yBQyNjMFFS8H0R3zMUSSApgayF3Z6WXomk4OFzNe'
        b'GUJ8SIA6WbTZWXx+YjARj9EdlgYxOsOPJG2y9xG3/NqCjwaHpqYGpmmBj8ETHlGxa1f1OBXabrrcCl9U4cukVQ+hhiEQiPiKGN3Br+ELtLITYqcFyw3OivzLxIxdugC1'
        b'470CyibzA/DWDO2pQDZpcrTLRcyMwlsEaNu6AopYsyQSzSVERL2tYaEw+mfgXRUmjE22YDFukrJN2rVWEpwdgreig2NgFZVBOA3f4eNr+Lw/BXQWoouJMWS+N5aTbMto'
        b'oZ3RKXQM5kRHtJebE9fiTZQ63BqOdhigYAtxA59hYbBr0T4WtnlAgU4S6tzKAGrJogcL0G0KhxPgV03pbqkjWj8sJI6Fw21BhyjgcAnaX2huYQC/NMReouv57AFJ4wRL'
        b'Cgl0QhsGogIpJHA1ukGZdQ4+6R0sk05jT1HwpdUixgavF1RV41a24o6WkJmwkTBKBlmvXiJ1IGIsKvl4fwa+TEuXhm8R+QOmcLKQ56bwYLSf5djL+DQI+xRmjvZw4g46'
        b'TuoOXlsRVjrNyTsH1urFnZS5FK4oRfuZIaSdUB9O1hkdSUtgsTbanNQFxV9q0Zej8atCO68iui+GGsTzRkQrnko32hhD+50pTBedk5RmZKaT4ScH387hBdmYs9tllwrw'
        b'7RjckRESSIaPDFCBOs1fhV4rkQb+93CF//9e6CmWxODPYEdTA7CNfTYDfMewave6TcIBb+leYYyI3S3O9WYkfofXtq1l0YtdJtftNF6TAAfouXfN3jW9Tr7tazVOkZ95'
        b'BnZLM9+r+fWa99eopXM1nvO6nec9CMzsdvDv9Qs8mXkks8cvWu0X3bWoa3m334TmrF7/kJPzj8zv8umK6PaPbpb3OvlpnMbB0/wj+T3+49T+467LNLELev3HdhVr/GOv'
        b'v9Q9I08zJY9mlPZenFo6R+M5t9t57gN7l7bU9pT92Rr7YA4nWaf2T9a4pnQ7pNz3kLSPBkyhxkPW4xGt9ojuKtJ4xDab99qPbg3S2Pv1ekm5ggk0XlFdOWqv8c1poHE9'
        b'vmVd+3KNUyDNb3q3YoFaukDjubDbeWGvkwegPDvG9ARNVgdN1jhNvhv4ruwtWfeM3J6EPHUCS6K8e8asnhkFavJPWqDxLOx2Lvzc3qO1rEPUUdy+tsc+Sm0fBfnEtKzV'
        b'5tPP53kk874V8L1SeP0M3yUFoI1h49QOwc3y9tT7btFdlT1uyWq3ZJrBQo1nfrdzfr+AcU/hgfGZ8C6THqfxaqfxvdLwVuteH782kwfSYHLnHdbjHa32jtZ4x/R4T1Z7'
        b'T9Z4T2m27nX1PhzaFro/rNnkvqt/e5nGVUbu7Ec3r2iZ1O6rsfenlamtR/L8JY39mA47bS3naFwV3Q6KL+2dOP309rEtL1HCUjSeqd3OYAmtbU1H1PUktVe8ximevsrQ'
        b'eGZ2O2c+HZDptDdub1x72cmqI1U9Y2LUY2J6OVbz8jv8ctvLHSvOr+lcc1f4rtVbVq0vf+ol/8wnpDt0XvfCkp6F5WryL7Rc47Ok230JqRlJNlShi9dh6zbr7oB5HzvP'
        b'/x6s9ByJ7Vh8XdDjO0ntO+m+V3BH2vms67y7fu8GvxWs9pLvTLvv6NVu2uHb4yhTO8rue4V0zAboaxq4Q13cYdpjH6G2j+j1Cji8rm3d/pdJdBff9rSO4h6XSLULiwee'
        b'p3Gd3+0w/3OtR8j2FSfXHlnbldsTPe36gl437/aUtikdqV0LvxXwnJN5zUJSaBJxUtskjX0Ay8Ma18ndDpMfgIUwX/KPWggDAwY7kz5382Q9kXZGdtT0hCWowxI0wYmA'
        b'BnbukcaqpbHXx2ukSSRlwhbNSQCOdd47eefk9mSNvRR8ZCT1evi2L2qbtzPlgZsPgDRYtxHNSZ87B/Q6+H0jsHex+9zJrV9EfsHYk1+/CbnrN2UIv7jvc+83g5A54yI5'
        b'bLHPot8CQpbad1YQsibfHM7el91vAyFbxjeoxyfmnk9M/yhI0Y5x9+m3hzcOjEdwj3tal/Vdk+6wtB73me/Nem/aD/2OEGs04+rT7wSxnBk3r8Nh+8L6XeC5K+Pq2e8G'
        b'd+5w5wF3nnDnBXcSxie03xu+8mGkoectOy17AhPuBSb0+8JbP8jZn9w1i/pDyDc9LiFql5Ael3C1S3iXg8ZlHAVA3/cgga6Vd501HtOaU3ptR+8132neGt0e+LFtcG/I'
        b'2GYhayCiPUltK+21ddhrudNS+wTcdji5N1saHKF4sUcoH8EpCbWTkA0XBQXYlqzUIdwMbBA8D7r2Z5pPQDYfhNEdCiIfBqjTcHIJEnJ+LSlid4Y3j6egiF3jaz+9Pg96'
        b'F2yhXBLHC5i3BBbx1nDEBRYa5M+A4OHlifKYPPF/CcGzWMovlBIizONLa0qUkqLCigrqxAyAq5yTNjKHlsPkWVhh5NuMNWtfXMz6HymUVJasMGehk4EFBdOX1aRXlpJK'
        b'X1RRVbRUCoA08B2nxbTVqkpKaysAgLaqqlayorCS4sOKy+vKi0vMjTIpr6QvSqk9Os5OS4mKNd7C+jyRgPVxSXmxSmZuHltdqCxcJgEzebGSdIo9I0yoKgdfbSQdwKEV'
        b'SopqVTVVy9jPdKSmFxcUSMEEsjnIHQB2I+XhoKCBcFteKamLkY0lRUkgxV4Bha9ZXFijy12P2KMpcLRRB3EU5cpi6MgH4C7OqIhaMzZlyqraaupcgqZAilJTXlRbUahk'
        b'0X6q6pIinTU/lSQQTHaFkCKRbKhZ2lXVJFhSUyST0kqjaahKoEJqSrT1xrUDBSVXEppqSUWQ9KDVV2lbo7iKGsmpBpd/kIZRhQ1A7g0+ZzaX061RfIcIxfuo9nAY2ojO'
        b'sIeBReh19jQQYHsp6PyaQVqjq8sYhiqNoo0TajNIrPH4zEruZERiKoDDl5vLw/FuV880e//l09GVdfh8Dll9n01Eu+clpNeQVcER1GU6WR7igQ/gI/hAErrltRqdsg13'
        b'9aA71oEB6Wtb+RIeGRbMf6hzZWpBmwltIksGdhtREQg6W7PIGojekCWbzxIhPo3uTKSfLy8Wuv+bIWPL1IKK9+PNmPL6vp8Y1SnyZlf6Whab5v72erMNrRG/2OCysS2z'
        b'TfK3Sa8WfDldvFQSHLGBVyy2OLHaKvBg4Ft3bT+yjtks6tgnUFyRuQk2Sn03HfzAGZlqDvKLN3UJlxd9Hb75xh6Txv/5cfnpXyePnTzDfXFsi12iqe+H/yiYeVo6dXn7'
        b'OvWG6phL3rc+HP35uILFgeFCwb8OYzOFG6r4pbPfhr/2la8JvyULEyRGKKydMv0OvnJJxLzXMHr27nekFqwm5EF0O59uhZSka3Xl2I2QLaiF3e/Yis+jHRnZoej2LLIa'
        b'qePFm6Odj0CFHr1SgDqeRRsrGL8+Wbu+8UANdPVa4eKhQmfT5KGBbBw/fFBAVq/NAtQ1EW1iF4DtpDk68QZ8cMBuSQwhAFbOo9AVvIVqEUYU472cEiE670Dp5qNG1EWV'
        b'CEXrSGgdL0VMFp5UvbDL2hUUKEPRm+XcPkLObLY26oPQFd3uTQnJXreBkzmbrgwz+OjYUAvgZpIxLIJPR1HNOAV6HR+nq2D+siEXwbgZnx4RdaZf4JiBFQrWNqcx6kz3'
        b'nC5qQOUEFjUL/Yde1PRy2kBEdu1xCiL/vvAMILOYdCqvNyEFxMOHAp5UDtpHXtkwvblk87508yIyFkmNSGT712pVvKLVXtEar5hWIZGP2xLbhfvTO/j75US0a8/XuEZ3'
        b'O0SDLtCkjihW/YdanbpHRIjlatvATzkzgEbQw5yniQaDoYdTYKKeSi5HDaGHif48njNMys7PDT3k9ZmQ2SifTEdDW2GjczFPZ8GFtd8i0NlvEf2M9ltKyVx8nRBhriip'
        b'5LwcGftArVWxc3MJHZ3JVJGckJ6oMPRxyk2AJYvKi1T5RRXl5KtYCgbX2rYuBb8qRYtlNIYsGa6JNJqhq1QuFa5eYiWAVA/RQdXB25iqhJJRpSyGB2TqoVMF58512Dxk'
        b'KXmZBdQPQW11RVVhsbY02gLSRMAVkM6PAMxSnH6Iqra8hnW6qstU9Wy5JibmFoQ8a9S8Z46aPv1Zo8bPnvvMqSYlPXvUhGeNOjt57LNHjSyQcGLQM0SOKpDRqOmlrGN6'
        b'VkgpKQ6RBHHsE2SkAWCsekBhzKyUMZxSQYqykDq60/PEcDoFkMwskAvZXlEXKQs34i6q08C6YWLZj2RQV174bCVNyM0jWcSyNpRVbJ9i82HZsbx4gGg0GCXlKKcixHeR'
        b'Yor9CR93sqRyXDrDogC2haBOlUWmBJBC7Qxqw7fQWVaSuoWOEUHmJG7Fl8LDw0UMP53Bh/BFITUTkslDO4Ll6E0vGZmg0Wu8DPt4mh5+fRraRF7cQq9O45M3G3jjhYns'
        b'kWkD3oX2klcHZ8MWI6rnTUJH8T6pkMUgdVYvCEAX6Sk6vihiBK68yfgYusC+3ImP5052Iy+7avA1MrPiPTxve7yZTfecHF1UjcXr0WYln+FVMegauoCP0ncqvAVd98Jn'
        b'VPiqjZKUAJ/gBeEGe2rTBW9HTSvwiRTcwmKDVrvT0/M4QtQmEj8SdTEc3mk56pLy2To5QhK8mk/mUkM6i/AmepQ6xw6fRKfRQWM6URNqYo/Qr61FDRPQDUNivFEnzXVq'
        b'ALqlGkuy3qgrwxuoXiqgdSqW25kHGOUYgDbSillI4p3KkhlniC9XcE2L29ApfG2GRZ2ZSsgIzHhhSVm06AHo8ljFAgsrpQ3DCEJ4U+wq2XPiDrQDbSRCxGY4Draw5jEC'
        b'S96U+PxasLqHrqPd5RkgmiqorgSATYi0Shoc7VpLBOFteBMheTc6kEsCu/Eb+BjeRSTh3ej1UegNOxFDxLsuy9lSfIWekdtNQrcUuHkmaiOBJUw6fgPtp3U4D11KQQfn'
        b'4RbQy9imIPShBl482omayi8m7OGrnHkM47a1AjD3tsiVSrzhROLd4DLH+RvnhN5dc1ycE1w2tJ2Z5OysvJ/QG9UeZPdL8mj2htldX5Vc5X/gf0IwJ2Tqe64fjv7w3Lt2'
        b'bzd12n3leSLMOnOGIsX04LvOH5he+8h6sWuqbczMyJXhyYkuWa0PvgznfdJfdMFk2p8jBP/yrpd6Hakwt3JxFK9IeTmjOjCJ+S3fQfSN1Str5eFTRHuzN9w4E1/pJNyy'
        b'O3zcNfxZx4ZfCiu7rGztk94f+4rJ+8Ll/zvmB693C8VhvV7vFLw8reADXGS2qDGKt+Ki8P1df7KP8zv8XksJf8ous63FbevdvT6g11M/ZNXP3PJXu7uHfrXM+UfnDaIL'
        b'vxG+Zm8u0rxTEa5QuEyYx5jfjItrVEsdqAxrgc7grgy9XSGLuXx0lLDWuXC8j54h4Nt4PVknbUQHtEZD2DO9dHyMvvdAJ3KCDRRSLEME6E182gQdEdBzSrzDfVZGNrqN'
        b'boSy0jl6JYtKubNwo2nULGp9ScQI0SYe3igV08OPGny2iMjWd/T2PqixD7TbnhW7T+KL6HUicrcQBjMUu6ehVylJAHxCF4OnWeNreHsGiLSmuJGPXsFn4ui5TBwRbo+r'
        b'LFwI+14B3EsjYWZ8ZTl7iNc4xgw1VteaR5OuhbeQPo1uoi5aktKqBPLGb3y0mLwhvLwTH1xE00ONYtRKXqHjydGQXgODdwWidkrLStwqrQvnTGgY2M+YiW6xJ2A7UlGb'
        b'qm4y3g8QHHQCLGVtxevp8gF3uuI7KrRtPtqD6oGcZgZfjsNn2ZcH8AncpKpDW8XWIvLlSXhyAR9kU71IViUwkC1EN8kozkPnGHwwMY2ltj4KXVXVOaFTyyHHVoa0G1mE'
        b'sqW/kIyPqeoscdNykh96jcFb5+PL9PDYgixZT7ArIiu8PVALNWJXRFH+RFB+hp0uEJS5ExNOgUhFhMi+UcaKKuQRXS2ANX5YLVSO0a0WwtVe4V12Xd7dXlGwWnDdOaXX'
        b'K7ijRu0V2Zz6pb1r61rOukOdxmtyr39QV3Kvn7QrmqwaPGJ/Hzv5hu/14jfLb5TfkvULGEfXL53ce33HnBx/ZHxH7vl5nfOu+3eHTNX4xrea9nr5Hl7Ttmb/ulYhSZ9b'
        b'pJhqvKZ0O095aMI4e/SbMqN92nM1jtL7Ds69jt70FnyPrNq5qtsvSuMUpf9OqPGK7naOBnfALm0u7aUal5BhX5ZoXIIHvSTEuoY8cHTZO2fnnG6fWI1jrNYpysCYDwal'
        b'y37VPkbjGNjrFsAZ4U3SuEV0O0S8+Et/jWPAoJd/Gu3VGxlzbeLliXeF75q9bdYXOaVfxPeOJ8s2cETQz/BHJfAMllhi1hKCpeFyQEld6Q1AvosZrQlCdpU1G+KAA6u3'
        b'tNh3sED4MlllSZ97gWWnfInPug+pWVlerGL9fIBjjz5rQ9feJUrln9h4RVWVpeVlSjOI94DuJ+eXlq8sKWYdlVvml6vyi6uWlahqyouUPwG19yGSOXUgrqouLCpRatgH'
        b'en0tUT4sF8DNem15sVbLBIQx5a9B9dllKGO6fcL87HQ5yTwxLycnWZ6YnqxgLTPqjOz2WVQXlldy1hSU3TRTvQ0BdmtcZ3ZC+Wu4UDMTPxob46WKBnQDmi5uad1Ti7yu'
        b'/wdOZGHWGOEMVrmez13AQKtqPuvgo9+acfNsV3QJrkfeLVLbT6uHAxsn9/boLtH1vPf8e0e7Dbp9aCJ0s67P+N5SYBX82DzOqojwNVwfTuVTLxXSbwU8t+D6jM/B94S0'
        b'1yEOHFRMZR1UuPrctw3tdUggj1yTePXT9G5AosBLxzjqpINzbJEM36XyDH1ygJsMxwTWjQXnEAO8a7hNoA4xOO8X4KXDeUp92mNTG6uohxLGxVvtHHZkwtGJ5Kc+/Xsh'
        b'zyocDBq7wyWWjGPxvETeY8EKnpXHY0Z//ZZev1EKGGvHNl+1ledjvpuVtJ8hl2/JM69+CH4TC29z1VY+3/MnWiXw4I3vt/SWNZcsIZc6tB9tMDbjijagK0TWcE0Vli8u'
        b'N1qPaI2uf/sqmEl2AH0kY0PJSiEYSWYNJMuEnIlk9h4MJZuTv3APBpPBXDL7XH8/SmGnsFc40HtHxWjdvZPCmdy70HtXhZvCXeEhs1CK5ovzxFE8hSdso+hM/5roDATz'
        b'FJbkCv9NyX877X+F1wQTT8aTUUi5QxGBQjLAfLDpfLHOcLLvBL7STJ8m+W9B/vOj+Fx69tyvLfyG65/bcXnDL3xvHiVU+Cn8ubyDwEQ05J5nlmeVZ5fnEGXKGlc2oMKc'
        b'GlIWU5upo6LEnMFlC0Wg0jKPmcxTWlFzKMF9djA/J1IXyNSAeGmJshy8yK12NR/8hvUSaf5ERpagseWqqlhVTTH9HRsePnZsLKxcY1eqimNhVJKFh0eQ/2QNHCkV9Anl'
        b'2TlZfcK09NS0PmFeTur0Tl4fPymZXM0gm/xseeacTqESZLE+Ed1Z6TNjHVqXk1tRaUVhmep5so2AbIXKpTCUgfsS5TIw3SxMlytYnwnPmdYEqWhAWsoVNEFF0sz4JwmL'
        b'a2qqY8PCVqxYIVOVrwyFNbwS7IiEFnEGEmRFVcvCikvCBlAoIyv98LEykp+Ur0+/k09tOytbqfmQPrPM7MT4zHyy1H8yBohOTEinFJLf6YWrQKzKgSMYVQ1JVBYeRa5k'
        b'aoHEOnnKV1kfFcuBVktFujw1Mzk/IT43Me0Zk4qQCli6dEV+EjPgw0RllUqVQPcgjNPIrCrLUpXRlCIgJb4+JULgy5CWzYD6eOI6fKGeOA5ZeVILo1SA3ZQbhkh7gnIT'
        b'PB2QyASaSKRyI7wbPvOIJ8HPUdI+k+KS0sLaihpa/bQt/29rxbK7Epcj0WGqLYB3BvKotgA+g6+UT3xnl5AqzG4Yv1GrLitmTHbzojeeGffVMAqzfab5yqraGsL5rBMU'
        b'42FEpn1ppDu7WkqE7+dUkQQvKsomcpksMlCRXCH9D1QkO01YeelXQwhN3VrJyUiP0lxblesZ7Wn5EHqUPKo1CQasqenqKHOdjqTlz6sjWbiL1IF5OmtzpXx1icH+Pevi'
        b'nj30hWHcYL9eUVtdXaWErc5q6i6XipKqWHPzUMmAbiUJTEqWGj+GbjjoyQRJYJCqHE6E62Jk44KG+ITtuZLAxLTBL7keCS9DJAPTGX50kASm5z41RoRBjGftyPDJQCK0'
        b'RxPcdjG7D8uapSkuWVQDvuM555zamDCbsdEGNkO1srxKWV6zinUeExgEc2QQyRBmySB2tzwI5kp4BjNXEBxNBMGUEySV6UEB42RjZeGxXBT2Mz1eIJy+4lLRPx5HH7NJ'
        b'aQllLWlxpA5hH4stX4CKmsjSFY+uoNgTGt0BDWW6oa1YcfaBdHnqTVGxGbP8OtDKFFh20kE4itmzHnJfC0dQcJpDd/0pPKSksAYalBC5aqBRLwBAlLMnNnBSQL5bUajk'
        b'0CMGzlVp6SSKkhKgvbaiRFJYQ6SQRbU1bLaJ8bnJqdk5c/LBj3m2IjkfXE8rKBU6pAc1eKTSFZLtVGz5qNN6zoqctl61uyPcGQYLnNCfY9CzJ/YL/bFD0IA+FaSDjtAa'
        b'rGb5WkULPSDuhCCWWm2U8kr6HWdGi8hb7FEHgEUqJcl5Odz5SqVEsaK8ZnWJsoJWZM1TiGE7OMeLhOHSaworVtGIw/fgID1PcPa82ArTm/kCTuKqTGfyiz0K5CisYZEs'
        b'Bt6VjOIamXnT9dKhz45I8bhJXKVljwHpsHVGRVRDTktPiJdLFpVUVFWWwZcDzmTMBs2+tnK65T4DbcGtEegSbsnATbhZwPDxUV6gC2vdX+6UCUAWd4VWpx1tmMTCWOCt'
        b'SxHaq0oaDdb/Wdv/6OY8qpCIrq+aBYszBN4Nr+FLqEGY78NY4U183IgujKYqc6h5XpxeeyKXyQlm7PDrArRtvqAWphpcj1qqFINUPY3t5BcqweA82o6vmZuhJrxZymcP'
        b'ZC5mROCT+JDhIQI6bEuJRmcTKkrRAf3RA4N3UdVMy/m4zcA5ggztWqyjTqejWW1llQP+EQJD5XmBgXgr3haGt4aAVXvW4H8obOPutefhPdEp7InGedwlUqGL+BVqpJ81'
        b'0T8J7afnYbvGiRnLgighIynIbItfwGonl+M78YaG+9Nk07JwAyl0WA6uz5yRJsihyukHSnEDvoGOr/Jn0JtCC9yKW/jl429F8lT3SSL9vxQua75gtyHc8lVFyO6rf3j9'
        b'3Rsr//zVH7640PFn+/Hq8OXWn/3l8/YzcQ3/XBo0+otpr/n9602/LPnXVv7jMfNJcvOfOyLesfXdHThWfWrp1D2q/r9JrRJXtXdcSPrC/saj32cWjJnT/Y7V0dho1P8v'
        b'i/ZYhcPoD+UdM5mSe39Rr/ztzo/umu7+9J8r3+nrsd/mlrjsD1V777c3Jt0+nv94Pm//4Tr/e4G5Nmr1uMYF36eeqIlp+3Xq1e5zl4qCP1h6U3nH+chbmTduF3299B/8'
        b'3BuPPvlHwOquBff+mafJXfUT878LfWbkvy61YvE5nXinWbAsNM+a1Yo5xg+Xl7BoltYqKesRBW8Lnw96QQ1ohwljnSOIsHGkm9zTcKMVxdasKtBv8+OLSvZkYpvZJEMb'
        b'2qvxRRYa5JhF9+uXkzo/mLEGn8/mTh5w/XT64RS0czzw81h0RWvGGdSBcBu6yZpvb4RzMC3Kpi5OD7LJKacJWKI7K7VWsU+vM9jVnxD0iJqQ2DEhaYBx7bkMNa/NGtfG'
        b'Z2NpRnFh+DDoWVJD6Oh8gM4WehY+Qvfqa9HluBq8y/jkZbEzu8e/Bx8QLZhC8vn/2HsPuCiS7IG/JxCHKEgOQ2bISUABkZxBsggGchBEGDAnxAQmMIKggAkwAZIVBat2'
        b'VzedMzuuw7pB9ja4d5tUvHWDu/6rqgcY0L27vbv/7/f7f/536w3T3dPd1VWvqt6rfu/7cMftQUejGMHq5qTOw0GPbQRevt8fiR49g+EML8PrPKV/a40NL81Ie6dKUZtf'
        b'qb5Ls5tl6JX8p1m2lLqWQMu6zVyo5jmgPWJ+W1awMHF0buBIzu28pyyG+iLsL65n1KRfr18jO6pr3Owu1OXVyOD1+FeEQGhoT3lWa5s2F4q0XT42sh719B5WHlIGqx+x'
        b'GDYxxFloIXEWWsgY09YXGDuKtB2xtz/FsCF+RY/Rz0LIz0LJz0IZX+pzR63t69iNyqN2znXsuzq8LzV06oLFBvZCA/u2bLGBm9DAbQwv/BscS6tNazZtdhbMtqAzm4tm'
        b'uwx4DHsNe0nzpx+xKO8QhmC2i5Tpoizlmvx37Ynf9zvCCeqmOQ5LgX1xUrcobPB4UxI34WQbDPP94Y8ifQnLr0XWmerieP9rRN9cGgibwfr97KivkqAJpu8+9BSl7fin'
        b'hOvp8E9oyTOJu3hxKT7UL+4+OzDIP+E+OyAuKJAn9yq38FJnbC1mkjX+zLz00txs/jR7TnXimatx/5X/XS4OpuLIJaogew5bdqqEf6OWqO6m+v8K/WY7suxuY8vOLysL'
        b'qXPSnrsTmskrFuomdUpFpNvMwxrsvOWTbyOWv8Ihxk6i0U3CPrGrMCF9St8wE2mEGUhTRub7lN5chquyTGIVvNI+kmjWdMu+wkSiU4/Tv5W+Hb2fm87n5hQWp+MVA6Rj'
        b'56M9K8uLMrJLJ7y1UKEmLFqsnE14mvmRs5dP3mWanSF9mwkroyx7La2E46eioaVFtNuyxA8Z7cvPwhrp1KNMJiqXlIlrjQpSSopKNFDTuGAHBwdTnkQXpn2AiM96Om5N'
        b'fllpeWZZObra1JUcuMETLmhSx8n5k78hklC+qjB7okkk/nhI2caFR/p9EaoKco51XFBwEH5/FLQsOjHKPyjOjjthuiQELUrgTdZPNnFax5WTvTLLvqzYHv2Rej7r4lW0'
        b'E77UGWtfZb2hvdml2Flf2nqbdjou1qQxh2vk79li3An4q0RqyNl5xYXIen+1mcZFTxUUF+0X+bKJRvu1/46ZNpGGmn4UtMXFW0QgJO2G5QxZpqhdUAMtXx5dvBL3HCmH'
        b'/bVlU1fHJ+OzkFWAnehxh5kUjZzS4iL0qFnpEk/7wnJ6tSY3f3X2yglJQqKchX3FrDOLV/Lz0ePiM9GD55O9qFYmb0yfJm2z86SLTRelOKMgO7OM7i+01RMf4+nu5EyE'
        b'BVUeKR++h52EGi4pPzGysSyjTk/OyykvJbJJegMJBpgy3ehhdR43XmJK8blr8vKRNYZjCdahqxQiWzw7vZQ2qOgf032Lzy9GFnyZ5Fa0i2lpMRJ04nGKqkJS+UiwaDGi'
        b'H36qFztwo5EJl75qVWF+JvHSxDYukUfpWAda9gLoPpMu6eTo6ngG4VqjT54dF88jXOuYxDgeriw8n3Ct/YOiJXJrIxWM4c6zUZRyyfObHHpm5GOVdm39B/agMb0amwMG'
        b'YIUkegFZhrTZp7mOqBfEaJHXIQAveY7lcrv3CvUlTnzNtvAIXxmeWjZpDBoH0BYQ6AEdsJeGd4HjoJIGePUsJXeLA/WgTQL98kc6KeZ+KcNDCXTysWvw8oIZdiSxIjV9'
        b'4Z44h/Io/Jvr0WVwjyS1GM5al0Cza6Ij7G2SQu3CE2nbUQV0vDrNGs4E1hGkjiyGFtBHU83Op8AuKctR2cTXEmwtT8K6AqjE+Rr/7t1A7+yZxupUUslY60moEU+Wmuek'
        b'CTu9E4k3o2s6bJi0Sd1lfWF9dvk6XGMVxZYRhPxmHx6DDVP6CjLwoiuqrh2KFrqgXREbhLQ1uABWwEZ04NQssAOcSQDNWbGgyn8zqvdt4AL67zT6u3PFWlADzvlnLAXV'
        b'/qX5sbEFS0st0kD9ijw1pNv7GIBG2Ax20+nlGsGBYA7sW6XEpJhwiMEHfY6aTBqsVB9Z+sqC4VLBKl1QtQDUZoAd04qzA56Ch/H3g3DAeiPYsVwV7uJS4GKsug7sAJ3E'
        b'NdAyRn7SXXBpvCO8klyOJRcMw5PgxqSBzkuSsN1WlZcnwJpVyqrwYIKkvqWgZthex+0CdzPBKZLocBKCBipAmzy5kQrcrQUvbdlC0uaBs/Ac5in8HQgfPithWkvCXrBL'
        b'GRxUCFlrVx5IJBfV9bkI6bSi+8DFhURi0FUjCIkKidEhGX44qJ4VtAHJdjU8FIfEsJoBh0uUQ+w2E/FejCyxKy9dJ3QquVLStMuhCj4EmzjgsKYFPDcbtIKzWrNZqKmi'
        b'1MFZ+TjyfCWwGR58BTKPCVvgYXSfHm/UPNvgdlS52HdyCBWgChzMoOCuOKU4M7i/HEcIwl3uIVJrJZFhvHB7h8mke9IcPknBlGWLpvcWnHiofBaoBa3wQnkivuTpNJ0J'
        b'rlBs6B+69rQrr4X70cXjwjXBUFo+EeKclZv4q+F+2an1F9gGB4kPDPElUFpoTCeRlEohCQdN6CySFfAETneff+nzKgb/N2RhHPvpxZHEqBiwQO3E0c2PEjmaajd/nK2S'
        b'cUrOTM6k1F24/cy1qMi9cnstjTqdlz5XXer9l+/LV6dHiD+2GI1If/juhuKc3P5Dj/TzPpPPO6K1y/3Rw7WPt7XKb9Vad1G38mf557Z7PizwXv3+nAz11M/Pbl130rKj'
        b'7U1W3Cpub1521N3gG09y5s9akWe/RDMvMdmw5CDY4RN89+LWFx/drQ+uChoSGl4+XHPTcv6Ld08F7Z23Zp9wzpO5Xzkv/Gnn28+OWPzsxWGojJz502BaXPjydzp/afsq'
        b'x0vEGFB1LdT9+nK7QetoauwX3Tvqdga3ghWetaO2v47M2jDnlnqOzt3TqSVvpz1c4bnJI082rXs4mG/bqluz6mnFWt3YVJNzGpXRJ75u/KL8t0630nlHBi6V6jwPilv2'
        b'vpuzT+Rj5dHGNQnvfGbBP3fgcbVcYfQxDfGndku6Yf2BvFtj/byf3v9K/ZlWjs8bzcnCbxaseL3+w1vGb76uTZ1UPPpL1W8vRJ/29bheW/HXy/wvr++r7z+79KvvmsoL'
        b'fJw+Xtzg9VWoipuVx/wE8e39t98aGns3oPJuw/0zDeufhTDDInp+WgWvbvNYE7iiJxq+pv/znry/iriPH8bu/OQjv5iSVQ4nLunlujatvXdNa3PM/ccLXt+9ISCv+dY3'
        b'q4V3zD/44uHbyyK/9b7dUq5xw/+z+obk19f/+VnL0yecs38uu6GwnKdFnEkD5OHg1OIl2xGcoBd7jq6m13qqU+WmJWLjLDDKY8Kj8DRokixfWcHtETH5U/6r58EAjYPp'
        b'gkdA0zTf2U2aTHjZdD05zEY9vG3ays1ecAY0wOZUwiqBaJRdOpnBj87fh4bNrSSHnz/splfI9oDKIqk8gRw0P+8HF5nwrAzcR0NWGsFWODgD6AOrbPFqld5qchE0XFfC'
        b'DkmIGmgD5yYX0nbBarKUtCYRbpNyxAWHYTustJWlE82dgqdjMX0+DA2i22E3m5ItZJqWgdM0hahhk3YErHYPwbShpQxHNDgep+t1KNJA2usVnl0hSRx3wojGsPTOTnsp'
        b'AZ1dyNQa2TVwkfbmrfIsnMhqSmNQYFUxazaa+A9I/FlBFRP9wA4nfWbbMdYqgasBoIMuxRV4AtRMLrHR62uz8rjspapbyMlotgF7bB3sQ+29wDHJ6qQVaCAxcqDXBvRF'
        b'RPpvDgNVMwIGWZQTGJB1XAn2k9usRE19jkgRmsBi7GXBOdhFqQSyfOBRH7qMVyPhKToQEDZmSQIBzfSIzy0SiROrwR7HKHtebBAqgg+TqwzO87T/N/zocFl/h2oyFYF+'
        b'3/QVizWvQpjYsmgCeY49zthm2WYp1nYWajt/YGjWHNwW2BHVHoVRIMFjr17c45q3KrUoibnOQq4zoZRw59Qoj5pYS2Uoq1EZM7cWm7sJzd3E5p5Cc88BQ5F5iEDNZFRD'
        b'95hvrW/bHIFLgMAmUKQROGZqVRsxOtu0OUs026Zt84imyDFozNSyNuKRLGXuLDTzr4nAQA7HekeRnq1YL7RTtl+1S3VkjtAptEbuEXciw1nfmo/0zB9RDEt3vMrIGeQ8'
        b'ZjEsA0k6tCCSDi2IQRMf5tbObZYVaVh+om8qWWv0I0uM/mSJ0Z/xpb6ZJB3Zae86+R/HpLxtp05JIqckk1OSGWPaRui4hIgiIbw8YlE6PHRHLb2p07WNJKcHkdODyenB'
        b'DEyb8GryonkqIqNYgU7sxAJqosDOR2A+X6QxH11Kx+DYptpNQm2nzmQa8iGaEzXGte/UFHHnDJiL50Wgf/cWphLqR6LINElgkIRz0qFz2mTe07bvtB3RFPvFCf3iRC5x'
        b'5GYSTsyX2kbnNnRuEnkkjUqVJFJkFCXQiRo1MGuKaYrplOtX6leSFN+fFD+AFD+AMWbAbYqsjxQbOKF/nQn9aV1p4jnB6N8rf/1IETeCV62XWIMn1OC1WYg1nIQaTqPG'
        b'lrWhY8YmNaGfz9YT6Nu3lQlnB44k384RJC0RLMscDVooiFssSMsaZzG0chg1TFQdxpY1zMMcXFOTVxPYoC/eQg3vT0yskRyHtYcNaInsfD8wNm12o1tUZOxU4384lOBD'
        b'cAq+NiWRhtuotSvOYWcxKqn1SBEqkLltTeDhqDFt3RoFqbXhWb+LrZhanyxte9lF+p/p41hxf5k2IQWYuIk+amSkU8ItsWMw4ghUIg7XMvr8I+vH2H49J+tO9XH8GNMX'
        b'kGUnLFucf36+LHFyoj0S5RLlEyk32Ul3J5n/oLtTHo+5foFiXPbKrOxS/j9aGyULSxLjHS+VpPO5i6IiZ1joRtRMC50XTejOSDM/Ac5ETAWfx84E9+6Bg3BnsvVLFHo0'
        b'r19Snm0XTtTeVDV4UUrvjUKT1lT29HLQQt6WFmRsorOLU7CF1p0NdMpxSDg8Yp6Oj2DsQJ0D0hAcVqOPcBwXY75UxgOcXUmnh+eBHnx5NgXbNjKMKFCziH7tHKENOyWv'
        b'nDVw/Bt56wy3W5Mlhs3LaLauQDevMKYwmyJLBblwpxPBdUeD6xTFgCeRSQh2qxGb0W09OI+snwPgFB1JV1BKm6/bQG8aR6EUmUCnQCcDtlPwko0vfejibLjTlmcTBU/Z'
        b'IQVlHQNWGIA6+pVtcwmsj8DKD9gKuqNlKFktphK8ZCVBq+5eqhIVD/ex8VxOgQN8cIZe5jjgAPoIYJeC5yYIu7pgB1ke0VwOrmPrHu5Eczh56wz3+NI3255kIgmec4EV'
        b'kvi5TeiaRE06CLc5S8LuQGOCJCaxC9STi66Gx0AVXh5xxUoKuqVNMmwghYTH17DpFYzFqfTbb+NY+sV8mxZoiQf74OFEuA8iOwYchzUMSj6GAXtAvzGp/AbH/ZQBg9J5'
        b'pFGyMtHZj170yVloRmHDtjl6OTMiWpveKbMylHCwty7OV9wdtoje2ZimTKEHs17gutzuvJojvXNXrhZlR1FqC0vSvc/PZVCkMMrlSFCnM4ttwFUaW2wPD5NmWgG3m5D1'
        b'B7gtgV6CcPQHjfRL/jpwDBxGB0uUwRkbpA1rMrxA23Jyv0EnGjK/lbPJ7qE9G2fZIVGHQWtxK8RHSNqg35KOGK00hGfwmgPSY4/RYYps2lmgHDYpwG50ziJYJ0exLBk+'
        b'UXk8Bi3ZBU78aPyWF/YYMzkMLhyCJ0mRV4LTcBtnNexTlTFj4ot5IruaFoMVyWAv3IZEAUkkkg5kmK+FveTIJgMkBUqwT45S1GDAQxjO3JFGkPIFG5I5suAg+hZLxbo6'
        b'kFuks8Egx9rGFnZFMihfO/lw5uJS2EOLTA+onQO7HcNhfwZ5USsDKhnwaN7afPnBMSa/GA3BR6p63k35dYVBkM7JD3+5f+3659+V/lSQ0TB+/O69g+fz8hpm2R4+yFXm'
        b'ufbrpdqxRUmdabUL/c78yDBVrOb6qfOsd1tb79aczQsKDPTTVH+tie33SPuF3MOVuc++/GFTjtexNw48v3Is98GzdSd/Gq1ft+b7d4uufJlXOefWw7iL4/0eA53lB7pE'
        b'ipmRZ8AvufHvlnzn9ORWt6ZGdN37GZuyzp6+uLnHJfboZ61acele935wTvJof8iIcf9c6PmkSOWBwosHdxbn18LGkPsqLk9ORnyfv1fD8I29Ow8fvmP6rqis2/TBW3NW'
        b'KFt+1Hb9py9XbWCvq8oJdr78IPHqPucHRXU/n4l0jpVfFzj/QrfWc/8LAy7fXhsK7zZfzNr/5z+Zh4zct3G/taKwq+fpteff/mRk7JzbH35BO0fu8zlr1tu9N/6jCud6'
        b'xftvn3hnaNnnhwR/i94dzbj7WXlzXXXpatG1U20fN7U8+6Ltm5Y295jGH7zVl2qnqNbEvdbw1z9p2xcPuH6WdkN1rd6jiO65765zgZtHnL5SfeqUNWfLzbTc3Xyf9Htr'
        b'TmvFrwg58oPdPtcBe9svWSNF637bGNP0Sfvo96e6ZHe+9XyWzhFF3SM239RmFV9/J/3t72Xt1/xkEGS/jrUl+89rrcsMlipv7NVZtuQn77yv4+/+OXxnbdrC6+W7S/Ni'
        b'+21/Nev7uc75u3wHjRI7Kkfre19fZW9DmXqj4QOnnuu8/tqqjw6dm/tB7ICCw1++81z18ElQ9VtGqcx5z+IjG7ysP2O/vv7kD5nnHyRtdd30zoEL9RVu0Zb5F79NVNwW'
        b'/MG4gmWwy8cne8rv9ZT+0NzrOmJ1Yp9e447nqinjTdueZ+puUvEpfFf2jRtfa8x/sWvWz0+UXi/4puKm8kOVvk/vjr5nnan94vMVbm8Zf2N4/dCfnnhmnky4v2pxJf+v'
        b'2+c+DLTfyF418Nwu8E783bEXsdUpl6sPFRgYVy7WnrX2WtFV+Y99VRb+GrhpIa945JsIwYHsD18fGK018Wm+tKZBgf+pQnXQyZjXT27TfX+n1aWPmavHHD/fVOC1Nvmc'
        b'uSh7vfEdL2e/Hy7/GPnWwY/DjcWub/0iElx7tx5wotcHvm7ycH+YfU6ylWVExsqqJo0v5j9TKlfvfe/rX4cTf/BJifn86OW3HhxZfeTr5B/5X27s4m9OLEiuM/nuYNn7'
        b'5/t2Jp33X1qy93zWzudXWvrWGp1yXPA0aGvSjxFfat1uPJb+J1tNi4c3FAZSDb56umHH8PHX1C4FdfiV1+jvS9HLi5YZZ1xen9hgk7LnxftpHs8PFFQ2+H78fYHxhpsf'
        b'stUiNkZWaLzYwr+nklt5w+ZE57xfjaPbVPsf5K75yN1k/Gvq0iMP67ce9Oxne11tM1598N4Pr/FZi744+yRVc5+mzXPF65yc1z/cqntPo672aemO4YDTghvt69YlrVv3'
        b'hK+93s+q8fNwh0+Hln/fMTzu/2Jo+eYbcmujMivuzirwCnij795q2X324tU/bPQ4/61SZOrlb7/5qS/pQ90f+xd9+MGB61FFuct/eVZw7RkjxLj3xM3hoKI1lbl/YVXn'
        b'b1pzQO9b1ZaYX3IN2qgtxhbrFcS/HWjR7hRlBHdu28QsvXD8yeyzG2fbbFEU3jH5ecelNSW2j1N2PDijN5Yal/jTddk/r6nU+3XeqkSLkoAFn0bUzNW8c/eHU07fX3ht'
        b'6NHiv/467GB76Ys721pRT30e8uhtxycdfl7jcV/oN//5STHP5k7Wg9iEBpMHlY21sj89yXz+Q+3XP5Wm/3yj9kDQr9SvLw4VRwl/mZXSm3P/se97G7qqxzrG9pil7dgS'
        b'b6aaPLSzYnjZsW/lAiPh/bydd803/LxuXBjvuNdyyOTnqozjpXFf3tH8+kbTHvHbqbExadrvPW51v/rG49FPLK/vnVO37Kv5ZzdXvGDeP3VZVLpLafWb/PsdYHCY4cJ6'
        b'l3OP4hUShg64ArojcAq96fnzFCLoDHrO4AZZGVFQBv1T4B9XsIssqvjDPrLqMhucAb2TKw9m4Nikcw+oWkEWNligKTUC7ouQrEyYRFOUqhMrFx4He8nxFaqrpVZQYDNf'
        b'4mRUAqqeWhI1BtRi2M+MNZRIWaRCLZYsorTY0EtATcbl+IcEEusQmgfORyJlSSuSrawLGoinVaoiPGLrgOHJTsaT+OQDoIesb1ishkP8KSUWNsHzDEoZDrMWRJnQSyU9'
        b'G3T4Dlh7vRRgXxrNU0D6bDdeCUfPxaLc4AXZ+JJkeiWkEhxZRy/nqMAKW3SnZUybGOenWH1OdDSLiLRBxb8ITzCXMDyKwHZS0ZaoIIdRWziGxbPhXly4A0wLsAsOkZJ7'
        b'gF2gYxI3Ox/sIcTZyA20j9g5S3CBA3fbwy64NwIpl8OpcrCHGeONWglr7euSwMHJw7A7cgk4jp4M7EbqC9jhSMdEn7aBuwh1a5mahN0PawvJEl8pbJ843T6MgQOpz8gr'
        b'MpNBhyIJmZYFu0E13yYM7l9FAtkPRMtRaqCTBYfBwbLMcHp1aysYBEcjwu3CQBMYhvuRqgavM1lgHxgkVc+LRXu7I+CVGA5otwZNs2QpBdjPBGd5sIJUzgLFJXyMxFZA'
        b'jVMGamUoRbifCfdkq5DLu8r54fIp8JAKvzcCtG5goacbYmmAazmk8sAReF2dLP2BHt2JMPwQeIyWmtMLAFb79to68BStbbDqOkuHNWcz3AqrZEgF+METsJfjEAH7eHAP'
        b'qoAKeF5ehZm6AR6kVwdbmPCSbxg/mkHrUG1xoJJetTy2UR52o4rB9W6Liy9DqWux4kEjqDfn0J2wFlaDuohoO1DlKElQAtthrwylD7axwbl80EvXX40CbOE7hIEOJfSr'
        b'WHieolRkWb7gKLhIP0OXnwcn3D6yBFwKRfLJ58HT8CiD0k1gh3Cj6PYdRIXo913Ox6mD4Q0KDMJeWEMvHzbDM/BqBC+KTgCCIVoyqA8eZnk7l5Crb4TDsHeKEY2snFMS'
        b'SHQ62EqqIEAJXuaH2fAYC5CCCQ4zwL7U9eSALdyRrYLu3Q33yFAMDgWGCtikTsMTQdvkonIIOCgBrMOGeDru/xg4t4XmRoP6pRJuNDy2lJy7jJo/tVQKrsAemhoNtm8m'
        b'1Y5EbSc8wbFGFVESiWoCnGAicTnOBNeQet9A+meErzt+nih7BgWugksKzkxQZ44GJHxrf3gIDnAceDaowlCh5xfL5zPz3dAYgeWQkR9rixrJIQynolihgqoB7GNlwD53'
        b'CcpAB/ShG5eAY7HRWNNtZcCmpfAMKbUDaAbHOTzUQ7rhxSx8aRlYx4C9s/JpR8djcOcGeoEX7M4ma7zgapgNvXhatcwOiT84z/ZD1gCsYiCNfq8suSULVFhE0K+kUP9t'
        b'l6U44UzYGkeRhstENd/PR3VwhUDRV8AO1HGUmIToNkCeh4166RXccqWR0Q5guykaFhxZ8uCkM12m4UTQDXqRRHZHYrEZwImHTkWRMwPgDtCJbCSk56NRZBcymMENhj48'
        b'H0O/NeiFN1CXJu8FUlImCflbYS3NfjsAz8bQ1grohruwuZJiQCRd2xwOT73IAJVwwm21ez25rQm4ACrpAjuCZmRMKi5gohq7vJGM0HC4CM0gmO9Od2j02D1I0nHpNdEY'
        b'jaTqCBpx8Kjlw/Llw/08RXDZDvbhAf9KJBl1ddXYNoHwEt3rGsA5WI+uhA+bwKPYeEliwGpN2E6/NNmdAvvoHATYjMJvBuSX0oJQt84av9LEUcEV+G0CW52xFF7l05PD'
        b'RdhmyCcZfBThCQY4iapjKewn9WYF94OtyFqCVdbZcDvqTPAk+gG4Aei8A3BQyQQV2zp8jQ0Td+l9cuAQcy6sDiYd2Rtn8cOe2jF45aUKSVKiGqo9Jisr2pOcPl8DzeWS'
        b'YQaNPEfovC8GsI7kbgaHQKMNn0xraBSmh9LGAhalAy6wndEDHiKPph2rS88FoNWIWHMNSMaL4EVSgkj5WZKRFNUnGoPaUfvAXiQZBaCOjAduevAonqLRmbxAZhLDHrSa'
        b'khdFWuD8Cj5qcwVYtQY3/XEFYkvipRjQVAIP0+N4B7wKekgimfPwqCSTTCFoo6u1FQnYRfKKQdmNR79igNdpCgs4CC4ocsqVFWDjPFSpJgw/MLT0KV4MVHPX5sO9aBwI'
        b'MWZqMsxWqdJDSD3clUI/SVgJOoxG7ENYF2hnWRiAXeRRV0XgrAST2XXAdTQlkww76uAAkUVZUKlMGIWOYL83rI6y44VFoVE+gk774OktC04tcqDlbLc3bJx6sZIFq2TJ'
        b'exUr0EXyKpTCnTi7Aeo0Lye5mUwBNBQnQyXCy/KO4KIe/ertAmhR4ZBf2pegDoOzEvSwkNbXhkaPfnCO3Fozm4VuPDEOu8NaBqUSz4pCE3k9/V7szCJ4CckE7m4LQCNq'
        b'ziAmqvt2f4nSAPaDQ/iwuwIe+I8ywP6EpXRrVPDBMfrEaIdsWVR5c1gKqHbxS7ElWmDfK7j+MrlwJw32R7vI+KVfBusmngBdCj9BHwvW6YAz8LAz7YOOZBYcnJTpiRRB'
        b'YC+oIGmCUtAEiYsTaQIvctCvwFUvnHOhn4FqYRs8S57RDLQpcWD1hPJkCBvlKWasO5odyRh4IwU2oekgPBPWM9CpPag/rgOHaTFpiXTGz6gYHoUa6KgiOV8TbGfB3aBt'
        b'NtH2wFVXcMFsOYeH5g49Cu4wgbvpGfucIRp4o2GXI9I5yBs/tQJWMBKDaticTGR2LT8Ydts5OKhm4WGgHs1/xvACSUow3wBc42DgJWiJZvIYRoHepMHd4EEDPpoKYJXC'
        b'xNOAWiPUf2ENex48wyUd0Ad0q3DsHXgy2uFIxTRiasCWUNK3zMCwDUkvGG1vw6AMVeRxvz3qqESqSH4TGOA72sDOUNQIaB7rlQNDzFB12ExODQGXNWG3fTTsT4XH8Jiw'
        b'iQGPKIAKUipwAU0PR6XSMzQjaZ5M0WBoT8RwDhqDL/Adwst5qP8jBeQcmqeYTHAYngggtcXNJ05ZWNUOU7VG4/0AvIA9rwZZc3PMSBmi0bzQNRElwHCl4wRAVylpBGwj'
        b'HI1wiMILznnMdQzvyGy6bWtgHRyKIMtSaICrwjEES8BOMhKbo4H7km24BK0E+zxouhIPXuPp/u9iQHCDcF/+n3QmBtlSsu5/X/cV7zDpQ+TV5XoO/epyoxNJnoyxPh/p'
        b'WQqswkV6EQLNCIzr0a/XF+s6CnUdBU5+Il3/GtlRLb1jK2pXiLXshFp2bYkiLdca1qiOQROnniPWcRDqOAgcfUU6C2pkRnX0xTphzexWTgtHzHUTct06E0VcL7RvJOg1'
        b'BXzcqNm81bbFVqhjj7bol2ti7fC2bLFD2ABb7Bkm9Ay7ywuvYY8Zc2uUPjC2bF7dsAV90eQ2a7YatxiLNJ1rGF9qaH2gp18X2BRRHyGJXMgUGbh0OgsN5oj03GsCRrlm'
        b'tWFjevpNNvU2ozq6Yh0boY6NSMdunMXU16oJeCRLmZg3+7XI1oR9bmRaEzxqxmv1bvE+Pb8mclSTK9R0qon8yAzdGZP1T28WmblP7R81tBQb2gsN7dvSO/La89DFmxTr'
        b'FZvdW71avEQ6jnhbvl6+eXaDKv6K6qc5sDW8JVxsPrfTXWweOJAs0gkaNTBulBPr+Df7tYa1hLVldaYJHfxE5v6S/YGS/TmdG4UOASLzwDFdQ7HuguakM3roDwbzLxA6'
        b'LnhGqejqPcIfI+m3Cm4WjJqYNyaLDb3pUI3OHCHP+xnFNDQaMcFw2VGueatCi0JbkpDrKubOH5AVc0NHLFF1BDCMUG0YmYoNPZsTWlNaUjothRae5MyB9OG8wbxRrkkr'
        b'u4UtdVBsETCQJLaIGlkt4kajS/gaPVJDV2hKqU9psxQaOokNYjrT+1d0rUC3Nr9pPrIa2oncY1CTNIaIDZa1scXWnkJrT/R1IHZ48eDi24w77DfZtxPEUUuEUUtEoUtF'
        b'PsvG9VVCGHqPjChdvSblemXUEls6Zz+jGFYRjInyJNHJPHyEFj4DBSKLMBE3/BmLaRXIGDO2wLkcxMYeQmOPAUWRccC4DAtVlTy+mGy97KiBYVNgfSASJ4MWA7GJi9DE'
        b'RWTgOjr5DlZo4PSMkjM0eoQ/OmP7U7pSRrmWYm52m1uHd7u32Ha+0HY+2hxxvuV50/N24J3INyPFkcuEkcsEyzMF6ZmCyCxRQPYYPiVv4pQFQtsFaHMk9lbyzeTbCXfS'
        b'3kwTR2UIozIEmTmCrBxBVK4oKI/cJbzNucOj3aPTrd+7y1vsGih0DRyJH8kQuIaJbMPxs8u2yDaXYcEUW3kJrbxEXO9Rc5szimJujiA2URy7RBi7RByb/V5stsgxB33e'
        b'1uxX6FIYMB/gjzAHePecAoWx2ULHnHFlOXejcRklVC96uF6QDEvqZcY9PIVWniLuXNTMhkak2+BG9G5jdMi0y7RldRS1F4msvccVZNCFlPCFFOoV8IVQVaIGF3OT0S+V'
        b'25WRPOR25Q5kDRcOFornxwjnxwgWxgriEgTzE0XuSSLrZCRwJksZY7aOdH15oX+PWJSNk5gX1enXH9IVMhA4HDkYKfaOFHpHityixLw8QWycODZJGJskSE4VJ2cKkzPF'
        b'ybnC5FxRbN6Po37+t7RuaklECwlVqsgvbVyObWg0zpJFRVUjgVjNGs8oJBltJh3W7dajhiZTEmwY3JnTXzwiIzaIux2M5M4wkIF7kGqblpjr3+ne79vli4TKVm98BWOu'
        b'o9Y4NddIuyb46WoGZWxRx8RZNEoJs9m3LV2k7zjq7tlf0FUgNHCti24PGbN3rosetbRuLWgp6FRvKaoLGdMxIkKe3lrUUoQrL6Q+BLcC7q+mHZbtliKuM95WalFqi+tI'
        b'bk8W2wcNKIu4wURgQttcOjzbPdGXAcaw7KDsQOnw2sG1Is9Q8rioUYzMxYbhbYEX5dGfAU3x3HDh3PC7c8KfUfKGRqgVxAsXCxcuHjWxaNVt0W3LEZq44bYwHTAZth20'
        b'xfl10FDUqSU09xCb+w8Ei80jR3KQMHiZYmEwbZVvkR81t2gNbAmkxx2Be7CQFyzmJdx2uzP3zbli3lLBoqUi82XoFBNyioWY6yTkOiHJQF1rcdfiEcYt9k32SII4KFEY'
        b'lChakCSakzyuKh+LhqVZlCGXDETNgbQjDD0qqQ/rDerh+lBsUUSdxa3drZMtdlogdFogsvUTcf3RreZhUTU0agqqD5r4oUvH3Pa5YtsgoW3QbRdStIglwoglzYoC7tJx'
        b'liKqKT3K1LJVv03jroG92CCk06Tfust6wGXYa9BL5BIyamAkNnBFTSg2yED1zBnkjPjdCrwZeHuWOGy5MGy5KDBd5JmBfoWnpKaY+phnFKr9TgbufJK2G7WwbV3WVi42'
        b'j0N1azVoNWKKB+ZbjjcdRfPixOaFgqRkcVKqMClVkLZUnJYrTMsVp60Qpq0QJRWS2htnsZ2NHini5wquD54YBuNaU1tSxRZzhBZzRFz3Ua4pPfO6onEejWKozvEHKrHC'
        b'oAIaJ8TmuW2lOMeN2NFP6OiHNtHkkXcz73YpTq4kjkkXxqQLMrIFmdmCmBxRcO4YPqVg4pQAoWMA2kS9Su5NOcHCOPHCVOHCVPHCLOHCLEF2niAnT7AwXxRaQG4U1VbS'
        b'saZ9TWdp/4auDWKPEKFHyG3W7VkCj0iRYxSWmeCWYNQqXu1e9IgqMvcdtXY4g2bKfEFisjhxuTBxuTgx773EPJFrPvq8ndAf1hU2kDXiOuI/kH/PLVSYmCd0zUcD2VxT'
        b'NJCRBkRVE14fLqmaGffwEtp6icy9J6rSkFSlMa1BzEF6g9ggh5Z5VCNZN7OQkHi96SWOyBJGZImCs0XzcnDjooYVG0ShZpXtku0s6S/rKhvwH44ZjBGhp3KKwn03tD50'
        b'lOvwjOKYmHY697t3ueNiRLZEjlrzOtjt7FE7+46I9ohRJ+d+dhe7M6lbCRXI3gGJq72X2C5IaBc0kiWyixDbLSFdM0m4EA1vaaKFS9AQy7NBvZlnQ0belSJrH9RNLCxR'
        b'L7GwE5sHozIpdykP5Iqcgsdnc9xMcQncH2lRllatyS3Jbckiiznjuspo/FvDCGNY6T2jwhi6+sgYNrZ47MekjM0e5bApdT2xGleoxm1WRxpIaEvoqObsYyG1IUjPQs8t'
        b'0rTD22G1YfVFDcUiTQfJVl1Wc5rQyFmk6TKxI6d5o9DIVaTphneE14ZjRYhdz65LaEqrTxMbOggNHYimZNCkVK8k1uEJdXhtpm3OAh37Ts1+3S5doc68Z5SirtHInKF1'
        b'5ItkZvqAa4J0R14Lry2wI7I9UmznI7TzGcgYKBHY+QlN/UcyhaZhYtOk23li03TB4nRUpxaWWAIkVd8Wj8bNCe+qIOGcILF9ym3NOwZvGojDUoRhKSLrxaPWtmLruE52'
        b'v1KXEj2koE00aSfdTLodBJegId/CclxODguQAqpKOeXZWuMcDYtZTykNdY3H1pS6YV38XTWTUW29Y+tr1x/aKFAz++lJAJtyymX89GQ5k3IrYPBVkA7+vr2h3wIFh8f6'
        b'6I+KE+0XpfAq3M/v2wPY82j5NP2/1JmNPlzQh4GshMz/01bqWbkTgzHrCfUHiUDnaHDWMuw0hRGPPFlCr/oLLn1CdHQ0j40+Ss9iypbKq9iNpQwGoSDFB4QGRQXFE1oj'
        b'TSsiEbx/miQukkJj2GJpFb7N7NLq/ymLCpvbC36fqZjPknxgGhx/D3qcn3ZSj9lMZTXUC03jGKOGc0ZNkNZg+1hBxhxnpiL7fEZNzGbuCyL7jCf35aB99qMm9vTvbCZ/'
        b'N3NfONpnSe4xD+1znNw3Z8a+VPpctM8B7VvAwDsN7Ee1XEa17B/nM+boqOwOfbSSQaloPWVi/CELfXuEvz0xwozDZIFtjHBR6gf6xu3xgxo3+Y9ZDJVIxlhw+Khf0DOW'
        b'lzKOHMef4zJ4/yM2/v54PYPSNPhAzWpUM/CxDFMzmLE78Ik8uVp7dldw29KbmW/OEcYmCBNThIuXCMKXCoKWfaBn2O46aDaYedP85lrB3IWjhq7oVJU5qJ8GM9BzhcU8'
        b'Y4UwlfX+RuHPcTlyCH99Fsf2ZymbP6Pw5yPySSMYia/1AFOeEBhpPoWCJAADHpZHBrz3YllY7aE0zaGNI/k7noMxjBr/BIaRHa8g+a4o9Z2DvivFK5PvKui7qmS/mtR3'
        b'CZLRQWEStzj7d3GL7FfiFrUkyEPjSdyi9itxizp6VLxuvN5/ELeoP1eW3Jk7CVtUdpOJN/gHmEVDCWbRSAqzmMczua9KMMj5pdmZZYHZGfll+Z+iMWq9tuKM3X8QsOhJ'
        b'o7lceMz77ICYuKD7LH8X/9KVuOeuwh/YwemPXMsZXesP4RElJ3n+cQTixO0IKsgZIxBLN2CIAIvACks3Ymd0xbigqJiEIII+NJ+BHYwPDIzLLpkO7HIq3Ywf+J/5qfMk'
        b'H3CiID/r/N5VJ6GB08vMU5h2DdwOpX5sKfLgROWUBuAx3h8f+r17OJdW46f+3+cF5s3kBTKpmf6vMtG0u17zXFDFh33uDpNJDAxnEZ+8LFAJr3BWYwQ53E2FFMBGzup8'
        b'c53vWXweOlo5sAtjBNWAGob2614y1dGZpaur815954WF6WOFDOpT5TPa7Mp91TwG/fZnB+zXswXtcCdsmsLJw6aCl6mDZIK9rzOjT02nDeLXYJg2mOUp7co/qs+dIHyr'
        b'cf8VBmE42jdLTopBmO75LzAISw+w/g8zBnN5zPQS9u8xBrNIjWNIHI46/yOAwYneMwMwONHbXtrj+buAwekddAIw+Hv9WooI+Mo+SR//O8C/mTwLOnQ9fSWOQseYCgm0'
        b'YfJnOEXLS1DAafUmAQHisZyG/aHx3Ibn8M8S+ibu9PcYffk5/8Xz/c/h+SYk0uafh+hNF+Lfgei9UqD/f4rQk4lOKPehsMOIu/mrkW3wINwXSYcrT8Y0M0C9Ow5n38WB'
        b'Z63g3vz0W+cofjy6jIqgt/vLvM+Ov6X2LsUyUTIx6PpmwXHedtft9tvnbrfY7rP9/cOGphdG1N7RAbWQnfyu5mtvbGW4NZcperAC3Kwi3erePKwOwrMjc/Fk1lSp8Hqd'
        b'A0+GvHmTDYbnSUAiHY0Im8FVJ1jpR94YroIX4Z4JYhrhpcGahRPItCzQT8eMHoeN+lOOg+vA9Qk6WZjE1SACXaQGv9tbAy/QeDDmAtotqy8CHOUsVp0eTYpDSeEg2MZT'
        b'/BcMSDw3vZIZ9vIMLA0MC6Zn4Ker5lLqWjXFzWVCtTmduQNlI0m3E0fd/Ubcb3tiXFgigyyX1rAPK0uSVM+gbumY/c8Rt+KQsOnISRO3ijz/JeJWaTNrhnb3R0hbpaf+'
        b'DmfrpVqfgGz5o4JLQbZMf2fWeQmsJfv3g9Qy5aQKyJmmp8hM11PQUylI9BSmhJqljKlZbhyJniI3TU+RR3qKnJSeIj9NI5Hzkyd6ykt7pxGzvmX/Q2KWtNn1fxKXNZ0n'
        b'LFEuJAyqIjR9YDjRfwla/yVo/Zeg9S8RtOwmVZBCNPJJ58j+Q0AtqS70nwRq/YexUrNoox10MTcgPYBNwFI0VCrPgEYJY+gtaAFD8DztwBofCqti7JNo9G9oONxHslGD'
        b'46ApGaN3MUSHjV0M9yiAqxngPMmoDXq9nWeSosAxsJtmDlvCy2R9wHaWAV85Be6dZFTJwDoaNlw523TSuzBWih80Af5FSlEdhv8yKXAIxwQOwZ3ccjt0ZgE4y5pwrHa2'
        b'tI2Fu0PtSNGT4e4opAuG2YXJUMus5P1MQQc5IRsd7IiYoSCaBGOyjx3cH2UXht314zhycF+hY7kfLtsAPAe2wT2SqyUuTLZPSsZoovCoSNCeEAouhUY52IdFoVs7MsGV'
        b'fFjNcQF74uIpI9CoUgj3+dBUq2uwK4TvAs7A+on8jnCHYrkrhf3zWsGVGdfHuJ1VLqWYsUNgV2wKXnZaDvbIgSPwCDxV7ojOM5kNj8RP/FjSWgn0SRNPvhSep1Jz5MBZ'
        b'WGdCisGBHQqcUhVUj+ixelnqDB/QAS7S8Zx9YTgStn8Nn0XNgjuYcJhhCxr4JJ5zf5RM+GM693jkbwW5VH7ce0ZsvgZSRNhun56Iv74SOKnN96p5sXWhmv+OFn/DReej'
        b'UxaMeL2mraDgfIZZtUNpyc/mQ8Ud0Z+5+fSff5Tx9Xe/eL39SbDHSB7jq+q/tRwKE6xIKV4VzhAIr5vL3dB7/rdux3W+348fnxXuPqQoeNdnj8Pz2+oMA+bpsaxT80/s'
        b'+OvsznPxc0+fOWl/+q8dn7Q/SFyVKhOuVppkofh4zzVxKaf2VuOHj97Spry2rVwxcsH9zJvzXX7bfMv3C4PVG0Qqvtx7dd0nl2RsTj656p2vG07efs/Z1fFvZfH7F7ac'
        b'PNtgcdV3T/13jrd8+Htf/OXHEWf9cdPw9cMHmg/2lZ63rQw/dec8vLClzsNmFH4+cPrjs8tmZ241+XnHOzc239RgH1Mt+9nts4PJPDXiMSsP2rEXHhFl9F/rFJL4QBxR'
        b'zG1gPTw8A1PDVER2wFHU4r10rEUPF6nvMRuLJzA1A3BYQrgBjbBiOkSGGbYFnjUFV4mLobuvIyfC0uglnV8Z7qCdcA8aw6uTQidDcVYyc0EzbCiF22hf134kIO3InlAC'
        b'lyS4YXB6Dn3vnaAyeEZ2yRYNeBmeBudpz+q+JXEcmwLQOTPYig61WpdKLrM2RZEuP+r4oMcFVqHbqMBrrEgOqKB9apvAYBDcY49dPzXgMHs+A1zYCJpI8SK84Y0Il2jQ'
        b'G46Hkg5c3D3gOnGNZMA6WCkB34BKeJ5eNsyOokOHtmmY2IZH0a2C/Zgb1DSsWLAhHVUbGSbPgO5A24K1U7aa0ybOUyt8ZD+q8QMRkb/HjYH9Vo6OoIen8h96SYffN04H'
        b'tkjBWoxnavyvIrVsoPnMjwO9/gVSC2aGGB/bUrtFrG0t1LYmFliASC9QoBk4pmFEsCm0N9BItsg1ghz2F+kFCDQDHilR+qaYuVIjh6kl+IiPSG++QHP+qIbeMa9jXs0e'
        b'2GWw07zfrstO7OIvdPEXmfkTR8yJ32kbibWthNpWYm2eUJtHDsUKElLFCcuF6J/VcpFeukAznVyu1kuoYSMxE5vLWte1rOsMElnN/cjIRmAbdFvujtKbSkLbBJFRokAn'
        b'cdTQvCm1KbUtoSOlPWXAQmTvS34WfFsbvwsX2iaKjJIEOklj+qZifTuhvp1Y36NTS6zvN+BeIz+mb9bk01xSI/+5tkHdsrYsoXbASMjtJEFimmBpxmhgjCA2RZCaOc5i'
        b'6GRjWol6tnQyRJV/hvzxj99/E5mYDvmQInzkoSk/CFuqeD5/gQzVkHkMRhgBfIT9e4bq/x7Rw+closerbLd/EefBjSZAPi94YtY0mAeoXDKT5/G7LI/VoLGcxEruAjvg'
        b'iSmcB+ikMgJ8WBzKFNbAWniRBbfz/OhsS9UKfD48uVgqHQFsgWcJhHKRYTo8NJfCuA7C6gCnN5Hpd2EBi2osxpb28sjPy+ZTNPCiGpySIUAOpAXBehrIAU/Gl2ORiAWH'
        b'sui01lwzytEdtJHra4CD6SnK/BIc3LSfAlWFYA9RDrPBFXfM4pChLJGKiFkchbCTHDGDddkExRE9axYN4gD1RrRC04vutn096JVicWilk0dcCK4rEBIHi1KSpUEcsAFc'
        b'Iipg8Ty4nUM0SNjHx8wM2J1MozEOLgFnpNEYGIsRAc4zYA+sBPWkHrJ99lNrSz2ZlNPylawYNs22YAWYUt5xe3DlMBcEBNA798wOpQTO5gzUXWzmZa6hd96OUqI8fVxQ'
        b'AZcr7cz1pXfeW6FNdRouRuK33Fs9ci1VjgUltgScnEJjZKGJEdMxaDSGagoNDmkE22EfwV+wKNgDqjH/Ag5HkIu6qcmibmGIL2pXFpZMSZgVawoU+PAqGCKRYDgKDFx0'
        b'o7XzrflrCbKCSW0KwMgKcBhcI01m7QIGjOSngBWxoJ1u/fOZaHLrRnVPqBU0swI2W9E4liXgLIdIwdAmKhZ2gkO0hncGds/C3Ar+PBJthLkV4Jo9yboN+teBnTS3ItLW'
        b'YwJbAY/DQ/ljRRVs/luojT/1unh90a97UoM0TwwNHct6VnTw3AeFvn1nIwrzV3xQfbblu7ds7h1Ysufre/Xe1xYFnirK77phbxcUqBnoF+jnl6rWtbu5mRt33rrn7O7D'
        b'cYGBmmeCvmoaGx7Lcv0++8l39eKwj44vO9g4+Owj1wfP/sQadL2Ycqk751Jtum2T4QnH1a/lftMJdDTq237NO5fymYqZ8XexkZ61ybd/fvTWG0vrua6HqjR739BtcHr8'
        b'OeOA/rgn4HS/O6fcstT5S3fbbzePM/+2t2ioWX+TV2ZFssfrz/yeb3zNzDsm912ZQafhzjmP1tauD+tR0rQ4ErZfZUVd8b3zhfeavHhbtLcxO+quw5bX28N0Xd8Jv1ZQ'
        b'/fGjP1fM9vK4Pa53d0DllD61eEzf70zkN931fdXb7t3Y0ff23Lrmtr64xh/C1QOWfB4qp7t/3WdHl1x9kPdh+BtDnLwnlS1vNp7zPpGuv1xHYecGHe8bJxaHlVkFrmG8'
        b'kfHa2ZLo++vfjv0oKnZkreNyu0c+Ocvg6Dttv147tr4gac0F9Y/EIb5U5hVjZY8v67b9Wn/OuqmlzrpCfb1awSb5go9V/+zt37X747HHOq9fzfRsyPe5GPy4pDnS+NuQ'
        b'9xubdeTey+hZ3SY/fvetkzFOsauvmeVf+CbMNjsmxZa1Me4Dvcoru5ctGvcw2fL6+2KByQp3p2dLTqx6+PExl6N7NC9caf01+6FR3zcJH3ykkxnxYBzetXm0Iff7Ztfh'
        b'k87Lghev9h9uWfnDTo1nj1JGPn38kHv/VJvfi3FNMy/NppDPCowOgEW34tZe2zSP8f6w/EKfQx+0mg6zrx9rNnr7xp7eU389qC5YCVx5Kz7VfD3j3Tvmq2+6v78re0Xv'
        b'VsOv9qyN6ZD9Hmi9+dSl6NbX0XsPplae/FsHNXz83m/ni9yqbsjGrri+8/HaExnHb3hwf2nQPPtBUM93+067vfeLr4GCoovHu+++OeRk1/f13ubbD1wuaGSKnrgVvPlc'
        b'+8MTRx/H/Nq9UN3OLp1zRONYpXrAJz+7Bz6o+OoaZf/k2Ts/n73zi+Ahq/rgR2WHGx1+rnq8PfE7t7M/qPzJNtnr9F9/+DlgJO1z49jDTb197Icdizy+uJ1nzFI5sIUp'
        b'jEkf4nM/yaV+acxY3DH8Y8xHy5jvuD94rjj6em+UWUOn45OOdp/bA8MtSZ57Xt8baGXEWbV4xQaT4VMyD8THDv+puCW67OFi292ZQ4INb5f/kDM2+vGGHx7/fO3Zzw+v'
        b's559su72zmS5uIa4z3S8k3rfcH5NZ+CNrofXluzLXK6Hv+lffMP5keqiz0bvXI9C+355UdDI2Xr6gN6t5gen+DffGHx36c/7M+6PfpvY/Svrbv7wLT/N5u9vJdgLi8rU'
        b'CxgfKOawrUazx1LfM22Kr+0Yue3r9zR399Le9x3uaZyw+NHyRsUnOpeq39ugPFrM7v1refP5wG/e4gLHke7Gp3e/u3L7e3HC8Fcffv+rr4ntzp+iTixx//qOY/lmmXW/'
        b'6X/VanX6ucqptc9Vq98a+iGmusD2c8ex7r7opQ/2Ob72wWu/OGyWWa2R5NH8m9dP63d/opz1ty/6vi1+r++XlDtXr53N0T5ZUM4KGQ6/37Bgb8ydijW/Rp1Zff+jmD5R'
        b'fPK+s0M7n0c525cez10scznkgU/e07vXm6K+i4zrD3mh8ezYXRebFU/T1ljJzt3MeRq0qfhI//KHlt7nftWb95vjVdaO61blvFUkHN1cJX4aESIadkjZKei/GuKIwPSD'
        b'Q4QJAerQtDCZssa8hITWgk5k1O8DQ7BzBpKSy14KLznR1tZQZLkUFQIzIeA2HVYuvMSno8baA0ANbAfXpHgOEzAHZB0dIIZNngOso2kOdlGgU4JzyAED5A5bwElwUArn'
        b'QFAOy9awFujrEq6EBmgw4Ts4bAiDVfalvHCHkjAc8D0Bc/AC22VBd1gYbfo1KMOtkojzJYtpmIMxHVELrm6yJ8wGuHc22C2BNiB7kI6uhifBxQUE2nAgjXAbCLSBD67R'
        b'r7D22sJLkljaDlBPggcJtgHZjZXkF4vDl0tjGwizATZBzG2wCSdFM1A3IdAGzFSGewm2wRYeJbWjvwjspc+eb4a5DYTZcAHsJRYpbEBqWAUfVBm9DG4oAz2ghg5jvgav'
        b'rcLUBrg/e42E2QBrQB0dwXgKHEeFmaQ2yFIKKwwItIGNzF5s0CbC7fDMJLZBhlIEZ8sItgFWxZL6Seevk+I2EGgDL5ilsUGVrtsdHH9CXUDq4FVCXsDUBV9wmRimywxA'
        b'Baq4g1PYBbhflywjZCcWIz1gCFa8RF4A9fbqtCV9JB1clJjEDNhPW8RsitzWIQVe40TbK/FAFzyFHhqcZiBT/iC4RAv3DngBrwtKBVnjEOt4cJmVZQS305G3nZylE0gH'
        b'uNWPhKZOEB3gANxH94DDiaBvEumAeQ4rUd37Ih2mklzEEh4sJEgHrHrDKh6sAtdSML3BiM0GXdGl9MpDjwbonCQ3EGoDvASaWd5WoJH8wBznT5pCNxBsA7iyklW8GdKB'
        b'sfCENjzOJ8G1sE2ODuFdCgdIFQeD/Q4KlBS7AZwAuyQRy6BusfSKhy8YwvgGcFTSY1oo1PYE3yBDlawm9IYkM7pV94N9qtNIt/GeaqzZSqXkqNFG0DxBbmBSiptyCbdB'
        b'VQLBzdHi4WdJgG2Y3ECoDahhrtCx4Y3glBzGNqyKpMENGNuwFPaRYE51z6IpbAOBNqyCO1kZfHCVXDcE1HpgbEM02Kk5gW2IA8fIqXrwipWE2rAHdLInqA2wYhN50i1r'
        b'0yeovPHwBoE2rAGnySH7QthPUxsoWKdIYxs4BhJuMLiBJJ7mNshSHHgSDmFuA2yDp0jn4oFTYGCK3IB5Jz1wJ0E37GHTCzdX4Ql4aCLCGsdXg4vgOktBCY0uuPH80ak9'
        b'8IKnFLqheLaErWGDNGNCbmBRa0ADDW6oLCIH14DhogmccxnoknAbehLpbtPDIoMGODipsKNCXCGPBC6lw9NSCGpKNQmeB1tZhYqwlX7m3WAAVQgdS85Ag0ENuIaDyUE/'
        b'6hG4a6k7rXCznQ5vmAI3hGfQK2nnwe6UKXAD6FtBsxtocAOsyCRSJAvaQyTYhkgreFqCbUiCB0n4NDioXBrhmkK4DZjZwOfRPaEhDFYSaAPsVofXaGbDHAmyoQs0gzN8'
        b'uN2BYBtoZkMWg9RYCqyAl2hkA5PaCOtoZENiGS3tvYbomTGxAWzVwdAGAmxgwvP0YLLNFHSTAHLUkzLAEbxO3YueRQd2sm3VV5FbR1nDHmyibEBde8JGyQD7yGooPJbt'
        b'FwGPMiYToJmDTnriCGNz0CXJ9XBfUATX5cBBJpKQU/AMEU5HUJ/EIZHnoIrLxoasKWhNJxIPr4FBeHkipl6GUoK7/XJZqvCUJh1yvw39t49PT5kKGBSxQTJ8G3qxQS24'
        b'LuGdbJRDAziZfyJBw4IJUgQqzzl69mvPWDTFisDycBGZY5gVYScZfgJglSvYYw8ukXBxAototCFqylzQA+vAFR8pYIQULQLsgidJ2HdsdmIEWSwFx3MIKsJch9xaJgZc'
        b'lYI7ELAD6tx1LAtwI1cyNeNwcPoFzEI0s+AxjqY7uMD9RH1QWwxO03SHGWgHcMJYQneAlbPpnnEEjYVH+KDfZbLO0PlwG6tsiykRajOwD3RgeY3gKcBqXlpGmARFoAsq'
        b'2CFgH5cGZa2zpX+D5r1+8rhysBFrYvAwOa4CKjZLsRwwyAEensOKskETJm6PJbpIRZBa3w4Ce1YykR7QHkBqO0nVQLK0vMWBrCwjMbghgQ+lbuEj0TnAg10xSKwO2KKh'
        b'WW0dayNlRj8fMuBBgy0SQngAdKJBAK9UwHrmBngxnlbmTqOujHSxoXk4P0UV1i/x8zEo9dmsTeAsl0AuYGNgwEuMi0okTTMgETTkAnbnSNyAymU5WVkzGRFIAa0AB0n/'
        b'sV7iIcHFIBmLgNcJLuYQnbRx0UoGn5AxwHZ4lOYWqbuRylIEO8DJCS4OhuIgbaebJQ8vZtJY92q3vFcRLChLcGgZJlhoIA2K9PCd4DIc4KzBLTcDxHEaXNtAqkfRV3Ya'
        b'wALpeBV4liIAC3B2Hj0C3YAX8zhEU4gPpQEWsAVsoxuoGh4GZ2iExVo0hWDRwQgLeDGfno33I/3yEGZYMChLHo2wkLUm9edjG5INrk0yLKQAFiWoG+PRcpUF3G8UPcmv'
        b'cIY7yYn58OwsPtiaOINggYpyA1wgJV5WuInwK5hUJjxPAyxQMXaQnpkKj4EKDmwhFAuMsNjgTqpLBvSyJhEWoKtkgslBEBbzfGm/Lkt5DLAIV9WTACzOwCEy1ubNMqQB'
        b'FuC6OmZY0AQLWFtGhulMcMCIICzg6RxMsSAEC9BuTHPhQKUKTbCIBAfBEQnCIjON1pWvoRmwdj48LAWxmARYgPOwl9b198PmrAmEBRpxZ7thgAXoXULL6Q1LeFWaYEHo'
        b'FcYyrLn6oIueKVo1kOo2meayCOwmBIuTi2gC1AVwBeyMSIfHMcUCIyyQQNIIF2ukNrQTUEU+aMSsChpUAY6DCp7W/zCaAhf173ApSIjXfa2Z72qkiBTmivQrmgTvf5dI'
        b'oS/W8XoJPlEj80iW4pr8B2kStkIdW5GO/T9Pk3jVrn8OJKHZoPKfA0lIbiKJU22ObU1oSWizPJ2GnhbvQ8/fxiChkuTd0AVVkYGnJB69Obg1piVGZOD2xzAOU1wAlXoV'
        b'THFo2SK28hVa+Y4oiqwiRDqRuET/ZTL8l8mAiqqCi4pFXkukY43lQrleWer5JaQBqXjehI609jSxvY/Q3kdkPR/vVWhXwAHWIe0hncEXYlD98GzGZWQsLMdZkzG7LI6u'
        b'3ngsww1TG9wItaHwH1Mb2v4utWFly8o/Qm0Yl2GhZpP/t+EG4fXhzaX4Va/Yyk9o5TdSemvdzXXikBRhSEpduMBgsaRH44sptyjjugttCUVFSW1PFdsvENovQAUS2geJ'
        b'zIPxsYiWiE5mP6eLI3YKEDoFiJ3ChU7hYqd4oVO8IGGpyGmZyHz5xO/kROae43IyuEpxn1SjDI3/GTiCoXFTan1q07L6ZWJDj86AHrlnlAx65NjhlMEUSU2N2drjaP0O'
        b'3w5fJGpW9q3FnTJii/gB52GPQY8Rl1teN71u+d70FXnFiy2KBMmLxMlpwuQ0wZJl4iV5wiV54iWFwiWFouSiH0cX+N2SvSk7UnKr7GbZ7ShRyGLRglRU87jMMvMxFuO/'
        b'GIX/YhT+DYxCCmMepijMm4AorGFgiMJm1v81iML/t9kJ5SyanRBHsxNwnnaBiuFarsNfKcO1Fg7/UXLCh+hjt5wUOSHK+18mJzAmoAlz0UX/go1HAk1gYWiCG9rF0/yf'
        b'4BzwseX0KsQB/dQebMkHjsXmL34F4cDuFYQDu1cQDmbuy6H32Y8aBk3SDEKnXc/+9/ZhcIETBhfEMngEXJBEgwtYyiYScAH69kSRoAba5t80+x1sgQXBFlhIYQvw98fR'
        b'k9gCT4wtmPfHqQX4NnGMsaCwUS/fZyxf5WzGEwp/4tvEodvg78/8mYVMDCzAn4/IJw0sIIZlzzpXAiyAVXbhi72jHErComC1HYOyBsMyRTbgyDR/HRXJ3/ErmFYw+1Ws'
        b'glKZyYh/HLuvQaL6FSTR/irT9mpO21Kc2nJiubHi2XOZ8VYkRgVHqOCIFaVE5USVRLXEWYmabkrxMjNi/2XT0F3jZfWoeLl4+bnMUnmyrYC2Fcm2AtnmoG0lsq1ItpXR'
        b'tgrZ5pBtVbStRraVyLY62p5FtpXJtgba1iTbKmR7NtrWItuqZFsbbeuQbTWyrYu29ci2OtnWR9sGZHsW2TZE20ZkW4NsG6NtLtnWJNsmaNuUbM9OlHFjxJsRooEW+W5O'
        b'vmsnUqiWWKiOZBPlEzmojlRRHamTOrIgv9CJtyzVzWUp5PCs7ysF+EUlBEp8tPI95Ckq3RINEYo4QkD6EI0+mPSPLyvGOaP59G/muNjRf11JRmb8zU1xwu+L78D1kwpf'
        b'kURzkFBTSYwIOlqWXUqSQhevzi5FW3xF6aTQdtzs9Mw8bmn2qtJsfvZKqdOkYmJwkJTi7zniOygqRhfjuIewHFRC4qq2Jrs0m8svzyjKJ5EA+SulIm5J6AE6nI7+X5ZX'
        b'mp2tWJRdllecRQIlURmKC1dnE1+3crxGULgOhy1My2LNDconEQPWfjxJKFfhOkUcUiCJXqErzVFSZxM1Zce19udxJT9L5/KzcdRGWfbMCsV1bB3AwyG66VLRK5K4kuLS'
        b'/Nz8lemFOBZVQtdEj4fjZtFD8PnpuSQSOJvOxI2O0E/Gzcpelb0SPWAxXUASlmItOeaPW72omF+mmFlcVIRD0IgM8BwUo3nM+6y1RYX3ZTPTi8rmuGWyZowNxJdvM/qY'
        b'r0THnB2hiFzKof7LJDFndB9WRTKrlshwU5E4KbISpOLHVrKNqEQpikIie5o7IsuPTZwUX9o7LeKsgPGKyPhpAi4VFC+Jl0FPRofKLIqKlMSKkFTn5Lwpx0ZU8yQ+CXUH'
        b'OojJOptu/t/rG1IR46Ta5uHA48x01JuWo1sup2NY6JMnT5IWE0mC+PSsrHw64khyXa60iGABKinPlnQPfjmS7ckuSUf2TourovPAY4lPLy8rLkovy88kQlSUXZorlfVd'
        b'EhNcinrBquKVWbhG6H4zPYv7tElCjprp1GkUzccLkPs/2NHN/F74zJZ3voz3Jq9vD+/elQo+lb9J/myFMT0l2aIPD11wAHTDsxGwFvbj97NlPFjFA31gDw8eBVcAfQo4'
        b'Ww67Sb7iBOJcCdtXww5wQYaiNlNFJptjMojP32kVVoYDhb8tV+IstqWIJx4cBPs5oBsNe14UL9kLHgwr/PHFixc31dhu4Uw6niLDUpEiqaNi4MUQeAhednR1coKHXZ2Y'
        b'lMxcxkJYm8djluM3UX5wSIu/BbTCahVYtQYn5rDHy/UKNtYMygUelrU1cCX33KK3jGMDDsqj3cwohocr3IUugDUxRbgdXONLnQ4PgqOK+AuDMp0nYwqugWZSErgXHEHl'
        b'doI99EEWvMoA7eAMzuOFY2hgH9g2S/pCpWHJsNemJJoHu2zDIhywS0kSrJM3AK12xPMwwIkFuyeOyM9hMuGVlbCziMcivodzwRVHnGPbHta6Os1hUkqbmPB08Aq407Oc'
        b'eF6c1QNHpo7LUkqbmfA42F4IhmELXd4DrlFTP2BQSluY/qwiBVBHGpkPtuH4Gjo+JhT/LDaUdpSBF2EV7SwTqCqnbQcGiPMnzhLsSi/Lx9rDPrIirwH2s/RdQVPalvIQ'
        b'9BNjcAheknYansh8DqsiIyLsmSU+4IQBvA6qYXXxbHgFXonQBNURHEV4BewJj4unsnPUPDxBH+3UmsgO12QRWbA7lqtHlS+mcKQUbH3F9XGUkmN4ojWsCoV743FwUEQi'
        b'7JwQXFjF5hF35ZgwmVkWinAHOCsjAweDLEA7jwpaowlPwI41qM7J699TsBL2wG4rXdVVpUhQ4ADDEgzS2fxWa6pzVNfIl65GLc9m2ISAQeKkKgsurYfdsENGqYSccZFh'
        b'rlJEjrBU4Rl+cPIq8pqcpcRYDnaAFnIbszSwj58EtpfAK0r4nK0Mc3gYNiE5Im95dhrB8/yNSrCPXBEMMbRQS/XRbVoPLoIL6H43oqfuB1tAKxGZTNixcUaL+4HdRfD6'
        b'6nJPfOEzGUuls7ZH2YfHJIZO/j7WGuyHHaRKcfoBCjYVckCbNdxOEjPKriybdm4IvIRPRw+zgQ0Px2yi/W/7LeXjJa2CxiEFhlcGvI4kLX/ZCQGD74dmq3cO/PZ+8ocr'
        b'RQvUljz8cmD1e1fD7rt9YXI4Qj0xIqhh23t71lLba8Jf/27xeXl/TWaQYNHstq01ahvZzzX+vKPj0xMpVl6rr35doH93l6Vq3y1X/p/eOfnx31Ye2TJrab3Z0E2rxbqz'
        b'fr38N8esjnD5pnNasZvfydD9JC/7l5jrb0RbvO749v9D3HfARXWs7Z/dpSMIgoL0DssWytKrSO8ICCJSpIiIDRYEe1cUC4oFsABiAQssogJiwZkYMTG6R9SzGKOmx5um'
        b'0UTT/zNzFkuSe+93y/f9/flbTpnynpl3+vM+b1l0cJC4dkq2zVo7q3PLVmzjtPh6ap/2bNA+EWLY/bQ4aO6j8Gela0ZbTV+QfSRcZ/uxu1ON3Qy/bt/v0nnwM3NGZlr3'
        b'VcFFI5UIzoP+a/n2adnvrEvLnRS8L2NtgML+E41Fi6r4gxHM4n0bn919z9ySEQfMu3G47ET7GSvp3hJm3J2CxPLq6TdNti5qiV4QIy7eft0jzV+sn53RvOrsO9aneHu8'
        b'PJa4tHk9XGs+Wou31mNzfhdjvHhYuGAI/HZNr230x50m+elPls3aMuEy855N4XMraHiy59HN9oXM9nPDYbU5KuGfDf34UdT0E96e9fGb53x/695cne9vGRa9J0/MsZya'
        b'+NacktmmJu/vGv9N+yyvyxfy1+l45ux47vjR/duKb0zzH27y0/+4pTRo7/Rr64786ON/fMvF3O+d1MJTLq9JeLip+foMj+Trvz/afD/txNeJMiN4/dZCoeha4vFd4TG3'
        b'jdtM/My2PHE+bpO/45hFr3fCmeVvLZ7IbR2TX326kfEW/RQFM6xm+g6+uDzG2tL9Sf3s3x3e2pyqY3t6xcK3Fjmelh2b0Zro4RWPvk97cMuXD6z66xp/HdYY3n1o7MKL'
        b'Sba5dr+BqN6Vsf0mmxiT901Dxbcr3I37xj5MWaWV9dMdYdq3V2cd2Bi2tkTzd3nt7VTTn/rTbZdeNpsZsPfy1Sj9evPy31O/hw2X1T7+/GaozvrnM87taDh643D3+GOj'
        b'LpSYtcz2utV/fdu5j0+v0fKcuk0SkX0jyX+oqGPf92t+n3n3x7YntXcvfdW87/OjD/po3Q7r0LuX/rbrssE3n9270j3c1Padi0nYe8/9j1n+vmzrD3WdL5Y5ZH/ZOtR8'
        b'w3HnULPL40fenv0B658t8VH/obVkyQzP1r3+J22gzrHPpZY7ftXd8fUT902bHelQl8cRne3+wakpoQ+adI7FKY5bRJ7LvGr/Q9rosiVpv1r91D9rrOm9BZ0Xe76GD4Z/'
        b'V//igzspTpH8EHJqrQq2gfUCMTgOm+K5qJNo48TOCibHp3DdYtgBatLgQdCJe0bUX8KNXEobnEOdRUgZ63rlBDhVLIiGxyzj1FHkak4guKDBnkB2gW5/gS/oYiGVSjxl'
        b'AjjJnm/Ww0MFoMYGnnBhcXNquVwb2Kv0IwNaF/qi/qETDQMbXBKxpdgyrjNK5vwzEXo7k18IalwwDC9ODDYkxgjhNtAQjU+6XaKEzoSiRJ3KQfOKE3BNIQsubIZnRH8A'
        b'iPJADTxaBHqN2QPxfSLUYdeATW7CaLhZpEapZXNty5ax0pwHx8CJ2FlLE0XRQowJ0AanuPBcThJJeyFcnfsnZOosUJcNd4MLBEEogG2wV/tP/CBgo1RjNljDgmTqQNfy'
        b'ly4R8GEy2GwQBfrgela6A3qgF3YbuJAzZeV5cp4FOcs1rQCrBbDGMBqcQDMSlSIOXDcHRcMZ53NhOwZB6M5746TZBO5VKeUVkqNzn0Kw5yWmS6AHOirSWU9SrZ44rktM'
        b'fKwIHwY7w7MJyuh2cKeqf5w/C0hYD6oLpXBzNK6NWN0EETyVExrLpSwiVMChqcuVyM6ocOy3aqsmfo1e6oRzQQM8B/si4HaSirOJO8oqQSREY3EsySYjCGVk5aYCD3GU'
        b'fpTspxdLYWP6qxNx4tChdx4pPv4kTPGSKI6JF0bHcyjdmdjmt8sH7l/IHpf3ofnnbnbKoYQA6Hjy5oPz6qhkyan3ItgID6Ci6gMrMU1MLKxRp9Q0uaMK4A4CW3BQ1ZeG'
        b'ehLwBq+EswTus2LP0esmcmD3TNjEot8I9E2liq2y+iwL2D2NxwK5WBSXCmxmIS6bqtAIXrMArkAFSrBxqrCRA8+Ci+AwCx7rCYPHtcMdxbFiHPcoB9tqwj62Zg4mYMdy'
        b'f4VrA2cd4e7FDiyAcUs8XCFFc6NGsO4lxqwcdrP+lDaA83CNFO5BlU8Qaiw8DZxmnUc5wrYYUAPOuyUSVBsP7uGALYsoVlObnbGdCzzk5AK3CrB03RyAkYYnSYksAA1g'
        b'30uMZwrYBM5lQyXwZzfoykRlfAbuHsG3qMKzXA7sciFIDO8KrjQBnue9NN7pB+fY4jpobI5r9xUYMEFnDOjgwRoOn9WwU/BgIrH0ZaFKGqCR6wNWoK9cC+vZQmvyc/mD'
        b'c0Ij75dIdNABtpKP00aiYcOkxgoWTMqDpzno5RZwlv32Dm80f+p+uZBRo3QLeHr54aWJpF+aCPbMBjWVC+ApnVLl3HJqCsoTybHVBW6JihehGCnhGrrgtBKBGgB7YJtU'
        b'oIXm+XwOpb6UywN9HnGsl7kxxqlSQRmr7OqFXNADt7qjnmgjadnRYAvKivhX25wowHhrVWosPKoSC0/px04mvVa89xRtnC6bADjKBStMAuEqlDPBe+4PIU6CSApIR9Up'
        b'3QReJaydkKKEL6LCd5LGoFXJSezHigN7OHrw0Cji5Mg1IUIJ4IkFp+BaypCIlIxa1oU3XNCgdd5FAuIpQm2YAAw3ZMBjIwhrVxPQVqyED4JDi2GfFC2LuoywJbYhxxau'
        b'g6tYbFQdPJSABEXNJBo1TNQ72MyBW12i4GYeZQsPq3qXwh6lCxzQ6C1N4CuR97Ecahbcp2fOm4TEuKD0LwTrpo94rCuFXaAP9SAX2NbSlDtBCg6B42xx8cBaziLQD3ez'
        b'L1tt4gUxoliRcwLqXEYX8eChhdO94DrWoeTBIKRpr8uH1DAWqfkGDHbkZ6uCPWFg+zO8UEKz6xWw/g8aotSPRC80y/YHHWpLYVOCdDGLrD0Oek3Q4JHIjpAsrFwAq9nB'
        b'ecW0Im38YmRIQcP4bn14lodGvRqwkq3kPYbTBWTcQQOaBuznws1gL9iGypl1iOSdip2q/QmFlCsaA7oT+ab/t2ifv3/YgD/lLzBAf8GPNfb1baE3ybGOqLJQoFkTUV9p'
        b'UZ/f7MkY8GkDvsLErMmhwUFuHdgrHQgdMonaFvpw5FFAb96A7ZBJRG3o8Ljx9bb15XVza3kKS5talR2jFOZWTekN6U1ZDVltkiFzFxmHNndnzH1oc59egyHzwN482jwE'
        b'BdTC7h+mNkxlITkoIHlmYMQYiGj831Ph5YfhAIxXNO0VPcgf8kq95Z5aG3bLUPzQyl9h5auwCn2irjJ+TK3qYy3KxvGIaYvpYfNt0bWhChuHbbG1ofeMLOqljJHTkJGT'
        b'wtIW4wwYSw/a0kOWwlj60pa+Cr6wPmxvzD0L++b8IQuXet49a6c2gyFrz3q1YWPzJ6MpGxc0xJnay+39hkz85Yb+ivFmTSYNJrVqSmwRY+tB23rUqtzSs1LYC9pCWjKO'
        b'TGuZxth70fZe+KmNws65za0lmrHzo+38GLtg2i6YsZs64DVofcmXCZ1Mh05mQqfSoVNxYOthK1HbjM657XMZcQjGFFlNJERk5rbs8b0bbe7GmE+VpfWGdGX0LhmcQQen'
        b'0p6TGc+ptOdUtjhtm0MaMpqyG7LZw0rGXEKbS9iSRzF7Iwbc+qIvJvQlMAHxdEA8E5BMByQzAZPpgMlMwFQ6gE3FzKbZrSG6KaEhgTFzoc1cGDM/2syPMQuizYIYs1Da'
        b'LJQxmz+wYHD6pYVXll1axkROpSOnMpGFdGQhE1lCR5YwkfPpyPkoLc03JHIlTj5eSYQze2jt2MZpGX/EosWCsZbQ1hLG2oe2xq90FRaW6I/2++a2teEKU6smvwa/psCG'
        b'wNowfP6q2aCJ0U2MsX+bXSe/nd8pbBcyzv60s/+AyhWtS1pDRjHEwH7KkEWG3DhDYe1wxOSgSb3qsKlFfUXTsoZlQ6Zimf5tU/d7NmK5y8whm2K5WfETVcpG+FiNGjt+'
        b'd+z22BZJc8WRRS2LWoNpQ/fdsUgbLOwe61HWjrhShm1cZGqy0i5N5amrayTtGsm4xtGucYMFQzYpKMxoUp2y5PZZjDiYFgcz4ghaHMGIY2lx7GDqkFUyTuehqXWzdYNv'
        b'U+DeQKS1Ria7F2xbMEJA4EwbOTNGLrSRi1wSfdsoelgkkYViCFBPXFfcgO0Vx0uOgw6XXIZEyfUqt4ydFaYWuHwYUxFtKpKNGzL1VphZMWbim2ZimQ1t5nHbTIwbwfKm'
        b'5cNi/97QixF9ERdj+2JZJBETkC1PSmEP7ZmkDDopg0nKppOy5bkFQ+JC1EgS2QZhxn88hnIW4zbo8ImpbUtY2zgZt92k06LdYsjO546p7z/4ClnwbaOJw2LU+nrSu9Lx'
        b'sfaA5Ir3Je9Br0vBQ+IU/BGCv/MRLjfNXGTutJnnbTMX/BFLm5YOC317bS869Dlg3APjF0P7xTB+0wbzb8y4OuNG8dXiG3OvzpVn5w0J85H08Urp/ZD0AhcsvaPCHKuX'
        b'1n2D8UoSXsZIQBsJ2mIYI2/ayPuehaPcKX7IIkFunDBsZN3s0GbHfoXC2vGIeYt5q2WD2rC5Y5uazFBWKBvFmAfS5oEKG6dm43q19y3t63nDFs6o88OdCuoVm6oaqhhL'
        b'd9rSXebHWAbRlkEf2AgGDW+MvzZenprOpE4bSp0mF2YN2WTLzbIVnj71KgSXKDkS1BI0ZOz+nSZl5fB4NGVo8hqzgz57Av8AHyg/VPmfn8X/kxEFjxivSB7+NI6U2aHB'
        b'IloDBQxGdz+voJ4nTuRwOJaY68ESn9tb/gvn9lK8Cdms5krJtP15/xZB4Yx/RlD45rA3wk54AmX8Gjuh28i5IDlwE1oVFomtnPEphtjVUzJCpvpnssJ/S+I1WGIF9+9K'
        b'XOaACliG5bvLHZHPFMunPOiyKi54Q5J/S4iZSIh2zl2NnHz2xPIfydKNZel5WVbWhGWNUJHNsCLRMRfffywRLhY+565Ozsuzv5zifyjWGSyW48sicgixqphbXFpR+BfU'
        b'fv8l2UbljJw9/RPR+rBobi9Fc8YlJi1HRUZOsV4eYP03xSsT/hONOvemxotT5mHq4Lkz5hH6RKvpefMqyt9gHv7P5SJt8zD1j+W6+KZcpqlvMvL+d4To+CdCACyE7KUQ'
        b'Jq+EmBgd+l+qoO5/IsPlNwqi7DT1n1C2OnH+cWaDODO82mM/2Cn1L/iWRyhA/+PPL2KbjxZhaczBHIr/SLR38diCx4UVVH1qU05jzmuKQYgY2c7nvyWVBitV+bx/JNP1'
        b'N7vA8Uqyzf+uJDo5edNn46P6nHnzC+f+I3HoN7s+HywOjsOeW89+HTzyR1bV/5q0ui+lzZ89T1r4j8S9hcW9Rb0hLo70H4n7f+mfYs0f/VO8LKuXZ/+8hGLHO8c5UrwV'
        b'NhQ3pptqfOluItXYZ4jia3N1Hy3kc9jtmDVZsInsyVnA2lfbcmAD6ABdf+FhIhpV9V3DP6zfZxfOVS7fcRjsXWJ2BIcyNtu9eNtiuZ7Nv+hPAmdRFocqi8HND5cD9idR'
        b'EsH5NxxK/H+rp6J/Xk8qCanFTeIHqsQRVeuG5935e1v3vVN7fbCBQ6nv4nRYF7Bl9udKWM/5i02UvHnzZitrQUtZC2WkFv7F4seJlyWqYu9drxV/6X9e/BiuhPeIni6h'
        b'RuBKqAJUlHAljckcJUk2C1iiJo9+CVbipr5Ghz2XZ/FGwb8OXEKVwA3hkar509O/XzUYVSx5o2osWbbYNCOwHzRzpa8d27uWEORKc4EqpUHJCrQm5MbJ3bQoEtwTyFJA'
        b'J6yV6pZp4uAHOOLlEgJumO6Jg1NzcXBvkwSqgti+HoCHwS5yOoBtjjfETYLVcBM4DvbGopsETMuanJQsSuNS2RPUQYuDLuvvai/sFMbG4IN5sIWc+8CGKrzhnqBKOeer'
        b'gmOx4Dh7NL8VHIPNYC3YIn2FSIB1ehXELL8HbJn5miN7DVgP+2EHF+ycVVVB9iS35IAu0ArW4xMMcs6iIuKAE2AvPEK+1SwBNICmNJYujXClwZoggmYIDgE7lNuweEt6'
        b'8fTRRbzC0fNSWbq0HRXOZKtTFK1CaapTXC7YMldCUpzJy50AdrNmyioqHNAEz4ItJFLY8sn45I4vUqM0feG6NC44BPcuZunHNibCPXBjkZIOhVChgD3wMIud6OOh6qgR'
        b'JZAtU7UsLtgFasZGgSOEqy4AduHzjS3R2F1CHKyJSyifKByhshQEqsLNcL/pGwqsPaLAC7ACa72hwG+q7ytm9/+u6v7JO5H2n1RXlEAUdNBANW4mC60S9s+LpEhBgrWw'
        b'kc/SfoAGfZb2Q62AvIqJA62sVfQsUMMaRavDJlLGeVGwmq1Qw0hSpbhCPeFJQsymo50rJedt47TxiRtSih7C8Qa6kWIflMa5cFTmUVwNjnk4PMq6TVqjPj4Wn1ctAucJ'
        b'EQPSvO2kugwNwNYREgqkhywJBUpwHXk7Be4H/SPkIkj3txJ6kUmwl7xVS0xRsotMBWtYghE93ljQrUbwaot051nPwq4trCldQ+sENb4q0XFwGpzXVUaDO4NeRTsawirX'
        b'KQnoH+H5ADvAfkL0UWpMIpuqZIyQi8TC80p+EV4e2AJ2s81vm7Y1pi1hOUvgRrCCC+rjwEGC5fIRVghQpmKwYilqQGK+KCaeQ9mAtaq+emAj+aD5QWAHYQoBR2EPYQsh'
        b'TCEXNVnYUssia23WthwptkYYGrGNJGB9BT7pCAHbQc9fmKmXwiPYUn2F6gzQBvYTKJ1l3jRCZRBHDlNxhwM2orZiDFdyKId01RK4xYdQLLvzilGJN3HesNL/oxF8Alip'
        b'DmvBedhHFAqTU+9Q9jyoEjfg3sdOm3Q+oBNszflD53MMm23v5GeSPq4iZc7LHg6cgidGTrdHujiUwCZSDqqxcPfLDsoFdpE+SoPtvC0FoJElgsgFqwkRBDwVqQQtgVMp'
        b'StoDuA+sI8QHYF86ywC4ApyufK3TgBfAEe5Y9DFbib5nmtgp+5oifdLbjIonz4tAmztSXg7F8bEFNaj7nDiLxXathH1RgngRbnLHw1Wmo44S9UIseksCasEhpF9RIiEh'
        b'00JjAdjHXQJOCFgqyBpwqBBzBHgtfckS8JIhIMWcVeFWVAB7WSKBUnCWEHcU8UaDc3ADUQa4whHrJ9vJidNJN/dmJwfWwS4lDi1cFRwENfDkAhVD0E1xYBuF0XeNbLPd'
        b'X+4rhV1q6GrnbFBLgVp4Mo58OewvB2dhHXojpMaBU0J4zpaMeb+P03ZezHGiKL3cUbFVmSzN5CRvnq6ES9ChcdWVQezDI+NU5xtwSF816rhuEvvwW0udMUe5rpilMk5P'
        b'qCS5nBSkkWvItcK7grPznea/Ob/gjfSFGPpmi7pOPL0zoKJGU9Q8/UAsCflXwMXdagq1gNqpakXF6+NO1Ar1nN480sGiFSuZKnHvcsWudzkLpHhGZcWuI+5qBhQVzi2s'
        b'ml8WdDfgj2dY5YVlOTniALJWlwaJyT1B7r569jJ2oSaaWuEif4SWlvKw3JtTcuQpqVcyBu3eykDXP5Ip2Sqj8ZwKvLNpBDYnYRgeaqV1InE04fKImZQkSot6ffRSVivo'
        b'RiPnPq4WB6k2PDoq10afWJ3ogNpY1InzRagnqhnBTswup8wmq6AZxwVYV3zd30pFuh8VYsimdbenlCQahBie7/9614UVEzOdPqVPa4QbhiQnTdpgHabRkjdjwSi3txUa'
        b'B/QdHeyW/ZD4uD/ul/D7DdfFAokolB793cqv7wd+fk/67bkzH1x7b9Xoz/VehCuiv/1N5aFe6gbe3QeNZ8sc61uuv2094X1es7iyeJWj7vYXDy73q/A++tvs/QW68Tac'
        b'camfzFShuqLNTW3u5nB0e9p61jSp1h0sF0ab5mUE/nBtw3diXtqSQ3Pv60k+HNXXe+VcbuOoR4kFjMx//bEHaV0/rNqSK44PvxCh82PMAou87zuqF/18zWvGbp0rC5o5'
        b'v38+s+V5+ZX+1E7jKbdL+jvKpy1mclu3xl27smPLQ/4uG8mdWRktZ0YtoTIubHEC34hnHc74aePUaZO039uWYT72G83S2drqG3VqfVc75h/2PM28kN/lDX7oaXws9vcD'
        b'o79Ymv25sSBhm6q/3Xt1/RG/BfpfuG/6yf1vd79fDnWf/U32NrQYunTF4ofiqE2S2JvTP4so+eTbax/x+6S/tM8O3qPdNTx7ao1gneK9O0+ibm14K/jLsANbEzbF5ExI'
        b'09l02PrM/ds5Q7HZX3+uZnhDFle+aGNFvZvvRr0pk12zv12VN36qYUVH+1BAfcZ3BZ72k9+zDf1N+O52ndDw8/1fXt1oNnWXwKLTGQ5d2Pn2jpv1qe9sj/e3L9gkeFta'
        b'EhHuduanBf4t9xKcDn19YefRmPajO7KnpLu1G/ff2cS/rOieEXes9ANv1+y77W/N+uG2n2v7+ZM/eLQG6P/KvyHSDou3KbNznXnB6y3dr8ueBrwbKegSn7/1yYU8P9+n'
        b'56+vqzE4VfOu96JRicuXdH+0OrBbt3HJ+77FgV/s/fSLL+YwX4UGdo/+IGBx0rHIpTpNEbZan+wLeeAqfeFq+k3+snUlN9NLbs5rK/klU75l6LeV9PTv7ic03V90c7p5'
        b'zsxto9WmBR7fbbQq+quJ1ueOdJu+OPygw/pi7t/838t6Rg8aflu1PX7eu19dOfv2p88nPjoz4XO7397iPjg7sH7h9WlP2ukN1zZ8aV/59Lv3b288/qX0udmSt34r2LDV'
        b'3lTzhsEJgc23Gcbf9p5/9szpjsuen57n/3ry0byUj0y5iVKb1hdqYyKOG260StfOarPpbDvRPv83C6Fayic1HZHfKm58OP9+h73f82W7H3BeOJnaH1F7b9kNre7GTzMu'
        b'1Qx+vksxRhDRpy77KPlWUWl6waHDNVlTdnS3J6/PPfDoeG7OmX0V63ePl31X/GzB5XcefHjv6XTHD366PXw74eH0j1rrfnxmevfc129dWc/3ZUESexcm46kLaEPDa88s'
        b'PBSdEwWyYK9d8ADYre0thBv50ZpOaC2BJs764AgP7AX7YD+LWVg5SVPbGRONEdoYU3hMl5s2BbSRtOeBanh0BG0GTutSoGM8vMDiAVukoGeERQysNCJQKjzms0J1BC4T'
        b'sAA32OVCMG6gJpIF5/XyMBUKC7MC+xeySCt4wpZELIOdviNTP7dYduYXUUkknQAaFmrjLymNs6lw4atROiiQw2wvgheCa8GOSX8JsoqEXTy4O3kWST7NGm7BHF9qFrBD'
        b'CbECzVYs/utw5SjpK3AV+t6TnGyhurKM4Ta4TxvztoxdSHFTOUGwAdSzSJi+VNA1gp8SwAZMk9fOUt15guppLJkdWhERPjvCZiedST7HpQpsVNLDoerYyfLDLYQNLILq'
        b'GAdsG+F/q5eyFHCY/m0RPMLCfY6kjiLEhkKMQz8eAJu4ErAqn6BI0uEe0E5oJ5Wck2hkP85dCPtAA5HLBrQvH6G0I3x2C8M48LQu3M1W7PEpsJWw4REqPDTf2UB4u1iQ'
        b'qGMF3IlKGfNFohqCHUEqvhzQNR3sJVJlwpXpmINvhIEvNZBbHAJqSMwCuAJslcKN0dGwJ5ZLqZfGmHKd4eoR+r5daPV2FhOdKVnOQIMGd+r8AFIa5Wh5vAEVgqiUD3eC'
        b'LQTIpZXOBWdnwsMk7cLZ8LQ2aJ9P2LxUQWMkQDJ3govOBAsYtHAOjsyBBxMJVGlxOYuE7V9spx0TL1CjEkp54CwqcHgmj+SXAlrJWkZTHCvWQjM8A7iZMganVbzBIX8C'
        b'nRql7aCkKcL8Z0rWpM2L4niwDh6gSNtLigGNf8FPJtbFDGUXHAg8zRRedGI5vUb4vAKSuSGwBW4mqjXRAE8EXyJI55hx4M6QSUQATbslL5lBQa8SEaoDMDMo6Bey+3kN'
        b'oGbMCMPaITeWZI0QrMETswiU1K4E1GtX6GhyKR1dnjUnZNIItvU83AJPY9Y6gv5UDa/EM/7NdpB1NQGPB8NelooKyhxYLqocXZLi9ClglRIu5mNAgTYhrFHCLjPztJUg'
        b'M7Vx8EQ412YGaGYz65H4sdRVSt4quCmdOwnUw02snh/lebPMVWg5v4/lrpqGolrhd3vy4PE/cVf5osU+rIaHYR0RCewsrsI0U1NBPWGachxhQF0Ne+H+l2RTyvxVPFiu'
        b'qengHIk9w3AmIZvCVFNq87kGYE0JEWuK91xs7oNUDn2temwmPMm1jgJNbEdyHq5bqKS+coGHWeqr0olEUXnaoEXwGr4adMLNXBE8wiLy4Bp4ArTAGmEC6qoTl8CtKJA2'
        b'OMaFHajH7GRZFDudl5MAm/iwZzasJp5OOriwFS0SCWTPxdsPr0ZxwVJc0MJJGg9Z5lK4IwdsFySisQCtpk6iXwy61oYXuJhwCuxh8X7bwVGwXtsZbuGVSLCxlMdSTRYK'
        b'2mkKm0bwuHZVI4hcdWOwmaV4OwFOx6JlihJ2rp76GvAc1IMWvvX/f1ja/wRnYE39mcDqTxA2dgWg9Wpef5f/P14CkF3ZqWhd8QJP+J+FRXEooWezusJeiDFardnNXIWt'
        b'Y5t7q59CJGmOUAjdW8IfKq+awxXObiycqFn9oa1986wjQbL0nuyebIXAvTeiK5gWhDKCCFoQwQhiaUEsI0iiBUmMYIk8NVNeWEJPK6FTZzOp8+jUeUxqOZ1azqRW0qmV'
        b'TOoSOnVJc5jCUdBW3rmwfeGQo4/CJ1CmqhBKGGEALQzoTRso7MumhXGMMJ0WpjPCTFqYyQhzaWHuc4oSZXLlBSVMQTldUC6vWPyYopZzwrhPKGoB+6eQE859jv8ksXdJ'
        b'7F0ae5fG3mWyd5ncZm6zZ4umQuTRO6MrhxaFM6IoWhTFiOJpUTwjSqZFyYxomTwtS140h86eQ6fNZdJK6bRSJm0BnbaASVtIpy1k0pbRactQQl4tWiih9pwRjptQWhQ6'
        b'kl7+YOTVRCYum47LZuLy6bh8ZXhnt3YXxjmEdg5BleLqzVJYhNCuIei9b4uOwlmIngslnYnHE1GROQkx0VDnaFky4xhEOwYxjhOGHCconFw6ddt1ZeU9C7sW3nEKeaJK'
        b'iQKeqFFuPgqhuG1he7yC79pp3m7O8P1pvj8SsTOrPYsRBdOiYIVA3OnT7qNMgXHyp538GaeQ3rI/P3msyvN0eErxhI7P1SgnUUtFa+VzdZ7Q+7EaJfF+PIpy931iqutm'
        b'w8r92ILyDuotGlSjgxJor0TGK4X2SmG80mivNMYrk/bKRLXgHcKV58yQF82Vl1bSRZV0ThWTs5jOWYxe5XJCcAXhPyi9YNpKovAK7JrHeEXRXlGMVyJJMpX2SmW80mmv'
        b'dMZrGu01bSRkAHYMU3gpkQ5IZQKm0AFTmIBMOiCTCcilA7ACBYZjBZLPlsoXLKZnL6YLljAFy+mC5c9Z3VGqUDNXbutDW/k+RGVn2W7J8INofhDDn0jzJzL8SQNFV0ou'
        b'lTSr3bflt83oLOksGZb49hIQ1sCCwRmXlg1J0uQZWbQkq3lic1VL3ENHMebPalZRePuzTDqMdxztHcd4F8iTkuUp+XRSAc5QQlt5oPph64YRhdGiMKSEg9xBr6taIwrm'
        b'1pmDVSyEFoW8ekSYlTAdlfKR2L1zVvusznnt8xhx3MCYgchLpuiNd4s2Dvyy9pGaD7gPzLjkp4w1wrcVQAsC0COPFg0cPKM9ozO7PVsZxkXSuah9Uefy9uXogU/LqIee'
        b'ARjE1pPTlcN4RtOe0YxnwWA6S2mWQ8fnMPEFdDz6uOYg2sodK6JFu0WzmsLVnVUU1NmwwrONJZIWRTKiOFoU16x131aksHNoXtgSz9j50HY+vSaMbzTtGz3kG3vLLk7h'
        b'4slyGkXccolojnwzpNFFsz4zxjeW9o0d8o2/Y5fwhEe5RmK3tmKPzmnHp6Gu7Y3wYzH31cvU79jFofBivw9dPWV5veO75gy5himlZeVn+IE0PxB9hXcgbnI9y7qWMd5Z'
        b'g2PkcdPo6KyXFWlrL3fwYmy95bbeva+hDOVJWbcCsh7rUS5ucrcQWjyREUfR4qhBgyFxfHPkh86itqJjwl79IWe/kYZddsvJD0kkELNvbjv7IYVqK21ZxDj60o6+LPXb'
        b'gPog55IWMyGZnpDMTEilJ6Siz53IieYM6l8yGUyXT067OlXuFNSmLuO0a8kie0O6YoZRipXHAnrdhgQBColfj3+Xf3dgWxi6ZCThtCSckcSg/4rAEBlX5tWl9aGjc5t3'
        b'6xJZKeqx+1IGjHDC/TnypElDgZNQ39XL6dJiXCfSrhMZ1zDaNWzQSD4p+aoJE51JR2cy0VmoaBRuPr36XSa9ZUNuIQPpg5MuTWXC0+nwdCY8gw7PGA4Oo8Ny6Sk5Q2G5'
        b'Q8G5bVy5wP+mU8BDJzEuBbl3Ji7vV1xUyuJ+xuPwc3DVCtw7xe1i1F06u3UK2gX4hnEOpJ0DGef0AaMrppdMmZBkOiSZCUmnQ9JJOMbZj3b2Y5yDaefgZvX7ts4dRQrf'
        b'CQOOcp8Y1HCX0naeHzp5y32iaKfEwYnop1n1oat3s+pBHYWD4JD2dzk8NJj+SLhuVkfZ5ZtyBgUprujPPfOIIPRH6XvqrmZ5VUFh+fTi2dK76jnlVXnTpYX/CUxR6YXq'
        b'9SkCe366XRX91KEfHt7k80OPflpBPQ+N4nA4VhiZaPUvHKI+xZuee9WE1HFtbx6fRzbWc01gDcvOz3LzlxXxxoEaYrILZHZG7CtQzVrZwI4kAYcyAa0qoGbxWLLpj9Zw'
        b'R3iso21htAhsTIwRhheS1Cz9VeAOtNBq5HNHfPtUh76elQM4wQsCW8mGopo7rH0zrznlL7MCHWBlBba1ARtUwT4BNgc64RQVL47GzNQHJ83HlhXEHTmmUeZQuWM17ECf'
        b'ATn4qIS1ma+bNM8Eq0Yt584xnVKB3c+pAZlnLNwsQmvyVJKKm+ekKKWEfnZwJehTo8DGBcTg3V7f/nVv6PMXTEfTVJSv02vHCdNAo8boCQYsMc96IVrFv1EwYwWvCqbE'
        b'iZyFRHvAfumCl+lYLycpTVY6nsSfhJffM5ZrgAOwDRwg2ldskVKnKl3Eo6hdQc/Op787d2iCobn/go/srv9MO+h4GIc5Nx+aWBzC0dI+GLbK6eYm9XDDldxPrQ3PffyE'
        b'Y9WVG125hJczsOVGSN4lo/lFsxP3Xj9Y5mSTXFD02X5pzhWm7vwvrd9l3IpYP5h1Jeq31KRgzxXH1juBs2XBvi80f27s3xi/cLlj7yK/2/OT71/ZdS7i1H3jlmjuN8+Y'
        b'T+kT9rWaKz2oR18VXd4yvqnQ4KsFHr//1qDm42/xzeEz+vfMd+jd2vG33uZqt/FlKfvs/OdXHNPlulyuyr61y+7yxosG5YOieY17H/ztRfV3we9ZmV+1Mq9qs3j3sMRr'
        b'TEaDh8/FMUe+mn3Y++FvJ8/lHam6/Detr2bFBfkfHzv/s1VmjctvGF09bV5wOK/kcv7TMQHwLeE7GhcfVa77JC74pyV6vxarVi5+9MWXIc+cvXaaVCRr/OKv9Zbvwvck'
        b'bStvuJgzpYuEEc+mfEIbV4WeSUm7e/Cw3C4g/dYa36qQMx9LD60ZF56kZfv4mpvDoXznsuiuM4emlFypsXQXq983vJa9/WvJvmq/36j3Dw6+8P95bU/iw5zNF77LMe7v'
        b'Gp+YNP1y3VLumQ5rv7SWyVNbK85OZGbWdAy5z6mUHLwZ1il0OT0hsP+7xqK++PX83+7e/HGK0LJSR57WltPysUeAeuB40Y6U1fx7uctC13i03Hzri6XU4WszB0WiJaH6'
        b'H+7PE322J6lxatq0g4PuoRKb1sRfip0bomip9oM01yt73Tad/jinJlZ2Ze+2DxOmXZMm+s/85cKxefAd8znpT08+3Xdo+FGD3sd3zD7pKPfMG/J4b/vf0mwGFB/fSGnp'
        b'128oWrHsJF/jW9mvFx7vzxuXNSdbW/7z3V3fSDdOfb+15taYBu8Zk4RvTww4ERUwPLiwI8i/ZWWy+sapH+xkBmOqtT7+okTd8sdn5xwzLQMvJsF36Wn3Om4ExE1bcL/5'
        b'h1MG32y+mKCq7eqse/+dhCs/fHD70p6qmstXQuy/ffcY86H/j+dnegf5D13YfWRhwK7nZmFTW8oEMx/rCLWnLV3bau5P6YSVy0x8240e8xoyHj60uzL+qX7g8pXXPvvR'
        b'RHKBPtu4zVhYp/r5msoBjVnjg9a+o3jRMnul5bslH160G1xi0OK94vnG7A279k8YG103LkO9Xm39VyrJSV3JQRm3LPhNo+G7GoUhl+d4vNNVYvf56Sidr3u+kM+GF89+'
        b'6PLgQpOJwy/9Rl/M+qhv17If1Y3OXy8blcJ3JcZ/MWA/rAU18bD2r8y73jD/S9QkC/swcNwanJvP2hOO2BqW5LG7mutAPziKlumHRvZiyUZsZiHZ5JCaznrd0G0ulFHY'
        b'0A126pPtkVywdRLc7Ct4zSIY9ASTfc1we3jsTTvIM5zXXPII4HZ2W+CYht2rHSvYFB/PY3esYHUkuw2yJXxmLDwckqh0nKoJu0nWYfAQaJfCi2SDjOyOARmoI1kvhQcs'
        b'R5b8+IvhqSC4kyX6hztVwKkSFdbLCw+e0gbb4DZnAetvBXV62gZcuDoT7Gb3Q7Y6ohCxcFMpn0OpVnJGGcO9DqCbiKWRH6a07zOdhK1+90DWgQFo1oQHpUiUBqVrGmxu'
        b'qVXJBccM4CGlhTU8oeEFt0pfNwBc5c06Ld0ED+logzpwQYxqkJvO8Qfr9MkGhy88EKHcoDIA57HTmJYp5Cuyp4H2NwxFM+Am3QJeOGgEx9gNylPgtCHYBOqkzmQkIJiJ'
        b'VZIcIq6LhvObjnrgZnCe3Y5bZszqx2FwJuW1zTxOvh3cCdrBOXZvZj/s0P2zYV8C3K8yRg+sY02Ad+TDta9vOsH2MVxr2A7ZTV3YiU0/X22ycUEz2GoDVtiwb1e4ei2B'
        b'jVLsuRobYvJAOwdsBQcXsW9Xq/nMgbvw9vlmjHDggVMcVPKrTcmuFDgOt8E92uL4MvZ9eQInw4PSN+TNgo2APQwAGx1AHd6AZctOA/toquYW6JuQzaPscfikAK7Oec1V'
        b'EHEU5O3/DLPnjE0yRoNtNdz6OkXAX9IDSJUmzQcsvKSmoIbdEX65GxwGq4k0SXA9bH19O5jjjBS3M9SCKM4Y0AO2UxS786vc9+2AJ0nChaAJ7IwdsUpWy+GCfngGN9oV'
        b'7HnKarA/A9So2fwFvQI8vpDdsGyduQRerEIzM7YxJ3LginBQzZ61tIPTbhLQLXjdPnQ0rFF6S2oAvX/kJSjzVMnOUu6xwRXSUa+ZxOMdTyloRa3NuFDFJkhpFwuPxcI+'
        b'bN3KzoQ0fOItuXnZqM2wfogLBCPv2LlaigH5UktjFXgUbNYigiQV66O0D4DzWFlRlWOPJFpxXFALdzuRjqHUMgClgmdmYAPGnaGmsW1kGuU6Vc3A3oJUK+xJBRv/sfEs'
        b'OAZb1BLgFuX2ZzNYb/jatAtsVadAo0R3Ks/NCvULxHj3LAq0OvZV3qJkcGoEEAKrVcEp2AKbSWop8ADGs6LM4AasUzg12Bqvy+NZw17W4hpNy3rKMCP/CIEEPAfbbS3g'
        b'tv/V7UqN/+3tyj/wfLKLkXDuX5nbkn1KsifZgNYpP+I9ycdVERzKwqYpa19WbTgxUTxkUq+qsHbChOytFvVq2OwxuCGYMXWhTV1kXkOmvmhl3RCmMLd5ZREqSxsy91fY'
        b'2jWEfYJNGSMH7W+4XHVhYrJp9N8le8gmR26W81Diw1KoM5JoWhLNSIoH025MRaviKTOH4ovr1eSWLrSx67DATWbfw+/i94i7xAP2V/iX+IMR9MSUIUGqPD2TFmTWq9VX'
        b'0cZOCr6Y3VBj+BNo/gSGnzYQcSXmUszggqGwNBRmQYOuQizBlOiMOLS3nBEVIaFEV0VMzDQ6Zpo8dwYdMwMFW0QbOw8L8BaEaZ/pRYs+C8Y3jvbF9pOClJGcbByPiFpE'
        b'jI07bePO2HjTNt6MTXKv58XAvkDGP572j2f8k2n/5Hr1Yb6XrHJAZYgfzvAzBsfJk6bQ0RlKWQSunb7tvq82eBhBwoDqFc1Lmld0L+kqc3poZX9Et0WXZZ9GlcAXs9sd'
        b'ATQ/gOEnD6hhq9JBr6EJycpEUXjCVu1KW7nWq963tGtTlRn2WHZZDjlNUNg5Y7cBbZVDdt714Qpnl/rKhtGoDnqCuoIYSRQtiWIkCbQkgZFMoiWTGEkaLUkbqYSHSA9Q'
        b'9aPKtySbKJbeFyIeWjngzF4JqGAfsLmzjxgrH9rK5w8v/GgrP8YqmLYKxi9GtYw6MrplNOulgbGK7VXFtOEXdft0GZ9Y2if2saaqj0V9BN7DMfN4rjufM174A4V/Hxfw'
        b'KHvnIwktCYydL23nW6857MBvs+8UtYsY5wDaOYBxTrjEG4iGukMOifXaD00tGVNP9H/YUdAW3rqYcQyXlQyEdM1riHqiRjkJ26JZKmRGGEoLQxlhJC2MZIRxZNs7T45N'
        b'T7PopCwmKY9OyhtyzK+P+szU9qHYQ5aO9/SmDoy/YnHJggmZTIdMZkKm0iFT6yOavRsSFSKJLKI9mxFl9i68uKxvGROcRgenMcGZdHAmCuHVkDBs69zmR9vGDkSgn/qw'
        b'Yb6wLeOYBbYAH7ZDRer6mMe1D1T4BAwKFCK3J6ro5qGnP/lbH/5YgxJ57YsfNrdqHr8nu610yNz1EzundhOFFR9Fcw7lDLt5ygq7TRVCbxQD3T/0D2EvnlJc+zBOQ/gP'
        b'apSN4EM7idwj7DHFsU/nXA2TT0p7N1YxIfYJD98rEiezFyg3NUrkvi+ebdFDNlFysyjsTsOuaWHDQsZSQltKZDGMZfBNy2D02FHIOHjTDt6Mw4Rez/pIhaVD09KGpYyl'
        b'G/ovt3RTuEiaVQ+OUnhOuGXl/tB3wkXLPkvGN572jR+svLH06lIlc7pPXrPqLStPha3zkcCWQMbWk7b17DXEu4NDtqEKZ3Gnc7uzLL0nqyuL8Yyk0X/nqOZQhditc/bR'
        b'2bQ4rDftljisjTvs4i5zx9zp99yD5MEpQ+6pcmHqYy3K1Z1xmYD+4/eSY1W91seW3POaKA/NHPKaJned9phHuQY8FLkwoiBaFNRbSotCBlKv5FzKGRKlDgs9HvpPuBjU'
        b'F8T4J9L+iXf8J7XHtoXJ7BUuHu1LB3TlyWm3J6QpIqOvLL60WJ6STkdOkan26Hbp9pYPuYY9UaUCkjlI7fjiJ9aUSzgHDW4u/nL/yUPiNLlT2kML233az6SoaoTf8SgL'
        b'wY+E7npNpv40I87744PQL7uVpceC+Heq/gnJ/+8OKHp/2sp6ffwou4Jy+mDEzBZvZlViYwBTvJllis1sTf8Vs4Cf8ScY3FXNycn39LirkZMjnVlYWC4ti8SfE4Z/OlGI'
        b'u2o5xOKrTIifaGKThCB8FYJ/jmDJnuBnw1i8U/jWBb9wx1YLY3MwkWh+OXvyloNZQ4vnFpXl8dA79ZyqObPn5c0qu4GN0kzKVuOoa/DPWvyzDv9wcMLv4uSIjfF6/HMd'
        b'51NEUlBaqd4d9bpx6F3t18wxy9Jw6M04HhentQVfGWKTDc2XVmd31ZWmXndHvW5pdVfnDUsm1hSGGGSQiqjGZTf2/+5cFK+q/oI9fEQ57qsofzCpsXQ1EvMF5g8fpaP3'
        b'2Iyy58tHWX+kY9hg38KrN20v7ArtM+yruJTSW3LVk05Op6dkyidNo7Pz6IJietYcef5cuc88uWg+rVP6nJvD0fF9TuHfJ+QXE3+XcR6T50/CeCMU3pGYwjuaUx2GmpSJ'
        b'zbCeSGGIu0oTSXUMemJkOaznrDDEXaCRb3UkemJmN6znojAMQE/Mgqrj0BNT22E9scJwAnpiOpFTHYseKdMOw2lHsGkrH+G0DSXkiYHpsJ6DwtAVPTFwrw59FQb3s4ah'
        b'bDRjq2E9gcIwCD0ynsCpxuPNeOthPSGb0nhJdfQrKV2wlG6vS5mApUziEDHN7Yf1XNlH5uhR/PcaHB3b79U4OmbP1TJ5mGgc/z4lvyyrK97oBfXwZKD0zXk4PMVDE//x'
        b'sE2lEFwEh97Az75kkZ2NfoLUiXkUJrmmlPY5mh7qL02lVP43TdpGUX80lSpKqEhA17Gg0VXi6uHu5eYpQes5WXl52YLSCilar8jgKXgSnkFLpNOwe7TGKC1dTR1ttNSt'
        b'BpvgdrTk3g1rU5Iwu1iaKoXWfX3a2tMN2ELaPgfsIeDaGgEKeRSzZaHFcg2PMoD7MGRtdVEFbgv2mVUSbG4CTlFulJuNCUuRutsTHifB0Q8PrPKH1WUoXieKtxRuI+ho'
        b'qxnglEQFrbVBNeVOucP14CIBbifGJ5A8XUjEdHioTJlhoT4hHxWjNcw2CZdyA0coCSXxBWsJRDvHG2xBeZFonABdytAeRUn2JyK6BoEeiRqVaUV5UB5wmzHB2sfAdkvl'
        b'5+E4GrBzDMqoBsWK0iEsvuCEKsqIQ+UuQvXj6Qe2sRD9taDHjv0yHI0CrVzK0ADFioB9JFpZJtwlQWW5wYTyorwSkHg4mjNcAbawmeFoFmANisZB0dJhD0sEvAYcSpTw'
        b'qPmgh/KmvMEe6Yg50mqwWSmnOmgpE2RQBqAPRcxZSLJLgCthvUSditSifCgfsH0ce0CxefZoIiRc5yxQt2WzAps5pDjQit8cdFPUooWUL+Wrr05qDGwqBTtGSgMVQzpo'
        b'tFHWGGizJpYrIfAE2AK6VSi0qtxB+VF+YF0oOZkImQJOsvVcZsUNNRtRkB4LIuHSxTwpilNXRk2kJsKdcCtrRrUVrgK7SIZVS1BcW2Xh24N+Fjxfh9a9HVIuWsHrUqFU'
        b'qAHoIKYBxSGwW0BUkQdaAuB5Nbb04cqJJBpYgRburWiqkIzUI4wKAztmkgMguAfD2dhyxN+oDnrBhTxlUYK1LqQOwE5JpZSDPTmfo8Kp8GRQzZoSHAYd8Wxp4piuoWPY'
        b'8oRdRqyibIa7Z0lVqeRZVAQVAY4JiKkGaIANYBXbfLaClfAoW7BsA8LFugAcZmt+vQ/cLUWa1JNDRVKRHNhGLGEWxs8hoVEaJ+FJcM62FDUEcARF1AU7WZrpdbrFUrSI'
        b'rwfrqSgqKtyMfCkHnCthK4ONBy7AAwHKLFFv0EWKSeiOxOsmKNZzVDQVDTvmsNp9CNQvVcqMFU4Sk6esTfMJRFgt2JqCAaFZsJ2KQW2oOoycEGXD9SkjhQsa8omSs1+K'
        b'69QHHCG5usGV4CDs5lIqcCMVS8WWg1aWrHciqMcil6DGtRqeLFNGg3uSWYupVrjGHnarUaCJouKoOHAByIjOBhdi47qRPgZ9bpNLmbJKE+BFVh8Op4L9sBtVao8OFU/F'
        b'g4MGxIQkCXaDrSN6hKOehlsDlNV6HNaS8p0CNpnDblUq3JxKoBJAdQbbtTXysbnVyyZ5AKzSHqkZSTTJNCYJg0l5mNGtl0qkEothP1u668ChuSOKpG7tDTYp6yUHtrOq'
        b'0OmGY6pT4AiXSqKS8gxJ+5oGD/mwcSZaceF+qbJKpvuyanAU9gu0Kao8ippETdJHeWGltfEWsOqzEqtBWVEVEnEniuQJ17GxGuDWRG0VyriYSkaNZcVUtpn0gRZwmBQK'
        b'iReARG5QZgfqwCG2aZ6ZVanNxQx756kUKgUNIp1ECUC7tGpEdxpHejvcR7LVSYWR3gecDzfRVqNgzRgqlUr1da3AW2gO80H3S/3ZCveO9OTK2oTd+iSup84MbVSVnfAY'
        b'hQZfg1mkrxPC1UtwYNBbyQOry5SV2OJIPrMiRVdbFaNpG6k0Kg21KLZX3QF2x4yMMSvLxCEjPV0TrCMVoQb3m2nzqBLYR6VT6eAobCSDjOVY0IF0W20+iocmW944oxWo'
        b'7rBs8SVV2urYnfdaago1xSqDLU+ZMZpssK2Jh1TlHJQtGxnPwGmwnWQWDFbpgRqKCocHqAwqA55nmxoSsmcWqFGhNMFBaio1VSCuGI3Hv7FVoIZLZUyjMqlMazNSI2Hg'
        b'EOyFdehD14goMSX2A/Ws9lcbg/Wwjoe6ahnlQrkkAlaztZEGb01B5bkMTUCsPeEatvtbA47rwTou5WlFCSgB3DiXlWOrjzSFQ1XAdZQ9ZQ/q4AWSdgiUFcE6daocjQWu'
        b'lCvogwdJ2i4GUmzzJI6ihKhq1oM9RGpHcE4zRZUKmkk5UA5hYXwt0seBXWCvr3LAwaWTAqsD2JEbddxsEwdH0USF1BTWSjRb2KEcb1Hjuqi0BtMCZ151AqjHa5w70oWA'
        b'Lb5ER0yt3Ellc604FvAImwAaEPaz2rAStuqNDHwo2hhQk8dqkbcaEaIYbsFDlbJPhKvgJtuRHhVsV47T+8FRC1YI1MmdC4CnwHE2DUcdttvYQLa2BSOzqGR4KE+ZxgzI'
        b'ghQwiL5VmQ3J6BjsnTgymLaADew4vQcegYeVbaUPVAvUQ0e6y1q4m88hHepc26mxcIMQbogScVHPdoDSAJ3YB+pF/8/JPLK2bAJfi9iNhbvyKBVKEa9D5cYlq7uxxmSR'
        b'ZTqUMVW9ZHRS7uy3Aj3Yh7tVNSg9qtZ8VG5u3NG5U9mHMVMMKDvKaro6lWt2wdaafZiSrUJpUL3ROhNyZ6+eMpt9uF+qS5lR1XY6rrlxP2jbsw8zbNTQnFaWz7HKHfUL'
        b'V8Q+jNfQRxPhZnPV+blxT1UL2IeH3bUoQ8pHU0Mvd3ZfuCH7cIPfWMqJWpGpOyE3oGGSA/tQYYxzb/ZTmZA76ovxTuzDXH806FC5pehqdpeDCkUsgfcbGiEdHViqZZW7'
        b'xKtSRPG5qRGsiXAsNkp/7I2SiNNM8mZD+9urI1n1SkdZ5cb9bltGfd7YgP9dDSYZrHHCb32kKuhtiYYK9bmE/HsaTJqQvwjVJRoOUWNcR82j5oWNI03Feo6nAI3ftWAj'
        b'VUVVQZkm2Qsn+jTJHex8TeMiYN2Ixk1bQDKckT0OCT84V9cqN8AhL5T9zEcRuEAeSrUn5C75JbycffiBbwYlo74Yp5GbazJnrCf6zISEYl7aLBWpB1q3R9upr019P9k0'
        b'Um+fuZ3eGKMN4ZW1BVYrfbaVjqnePDtqyYcfDaidLLqSsSd3U/xgyuHkQzHfjQ1w2Pqjwe/bmp7uOPrJteMLwm2mH5t144dr5U1BHwzdPdH1QNVMNFc7atNevyjreLPL'
        b'xm6rS/PG+X6k4rAhpd7hs0lW1wfsrx+IErbEHW+OOd6SsBcGdK106Fpr+paqcL/fte41o3t/0nv3rbFLws5t2LqhqTn+3NrJH81ZEvPLqCYDRpbwC7eyurIr5KuHFk+C'
        b'vDZkvtj+YqyFnuVH+k/cziTum6Pur7hssf9hyVcfUxYXLllvmVvYY/61ive4MPmoz5a6vcjcTS8+1BPkohFyY1vIjea+b8LuJL7X/OiIemDtjE++qP11nvfBzVdH7f8V'
        b'/BLs8p3QOyzz2xMpISUhbfov5iy67FxuMv9yx70vb1rojDsRKb+upf+b/LBffsiH7TF7bi/qtDFtMXY741z+dsTVenrsYmnA+PTxy8uS4nuPHZye/PGcjrgfS6fFVulY'
        b'ly352P/dBzaxu37x1QicXqaifa1uw6+2O9O/rT4ZdPj3gqpin+93vPN2Zenby9bufvbNp0ND65PjHz16POdz7/13qn7qOb0xdafp4fEhOba2juf83zb48PC9HY+iNFvP'
        b'2mb1XdvZYzA5ZDRn2xi/zu9+e/b984k3AgKbxidKQ8+8syT5U+n7z1+c0XLu1PI5Yy6891WXY8oV/uPfDD/q1fv8i6e/bP1+sYT3GS2JLpI+ebRzv9fsxAf1zrfj1v+y'
        b'J+FmevGpjw9elFp8fU7jgSLo1KKehX/rX337eXfx7iyXC8eCvy2sD2+reWdyd8n2xt+79l7+4u0K/ZjdJp/ICz/96dMQi3Oph178fiz2qMrthg1Hn05R+6Fi7eKiXcdi'
        b'BHmi9pib66Wz2u/qnu2yeVev7MHk2zMTvt67t7y3ckHuL0/e+e7Wjo/T199622dy7KSKA8cPOCt6nlwrVaQVTu4aVVh2+W8/Nc5iZjaejahr33X2XPBvksDC64X1H5kF'
        b'nKj89OgXjd9cd0/J0rwYFFYReL3C7nxy+c9Z7XVZ5+Y+7T/8eepwk+UY0a17t78NSY7t6rSbKTuQ91WXQ//Ngi+CY8HPgnf6Becvv6Vl8CUz+NOTgI3y77Xdlj1x+bmB'
        b'3hm0gz+aHG2GB5riQ8d41LGeiktUpVSXcOBBp0By7jgPnEdLkRqW5lcliiNCKy7QAQ6SY9X58wxi4RY0EsSKnEEbPMChtOEeHhccKiAYhDjz2RCTBPSgNQVPiwMOw01u'
        b'ZWL2YPk0OBctQMPR8RhVSqWAYw9WoPFuHTjFYgAujo6PTRRFRwujo3gqlPYC7M++cR6JmTsHXhyxgQqC27EZFHch3A/bWITAHnDEF6Xr4syhVCo4pvPhhgw71lRljR/c'
        b'JhDDzapusJPigm5Omh3YwyYJq11e2T6p+HLQzHkf6JrHmqehicIBsF/Jd5FnpEqNUuPC82ML2ZdnFoHaWGKgjjI04oBTZeAAmvuy2IzqZaAffQcnBZ4i4IzyIpJfELxY'
        b'SqIsguuiwQk0S/PhjsezX3KqrgZWgVOYIl/L7HWS/CLYlMO3+/9vSvFvbDLiVeRfG1+8aYOhtL+Q5k+fm1M8Z3pRYdkXqhRFTjGHVVi+m/J4DjV2Iqc6/DFXz1hXoWda'
        b'n/KYh69sRG1S9sojeMCAXD0kb1XxFXlLrshbfPVYjdI3Q+/V2WtbMQqhvPacwEGByI0GG0iTvSaBlNdsIHKjxQbSZq9JIOU1G4jcjGID6bDXONAT5TUbiNzosoFGs9ck'
        b'JeU1G4jc6LGB9NlrEkh5zQYiN2PYQAbsNQmkvGYDkRtDNtBY9poEUl6zgcjNODaQEXtNAimv2UDkxpgEejKevXaVDBgozK3apG/++c5SD/t7fGKj5H3GftAZAxfawEUx'
        b'znT3rG2zmg3q5tXyFGPG7hZsE9Tnt9njY6BagXyMZ3WowswSu4zdEF8drhhrvDtzW2ZdVnXEh/qGtWn1BduyhvRtqyfeM3GpVcNbxZb1C5qnN1S1qbVr0pZuMjdZfq9N'
        b'1wxmfGBtiMLErDZ02Nym2XP/tHqOwtiU9cneFt7uKAtpF9C2XneMvZ/wKAvnTwQ+9aMVVjb1qgpbx3qNYWuHFmmbpLVKZt2y5I61R32Iwsa+xaE+9DNLsUIglum3S9t9'
        b'WjQeCsTNGgpLmz3LZT5Dkkh8cov9Q086OBoFOqDx0Mq+Oa9Vs21Si+4hzSdGlI0nKi87frt+s0+9hsLYCjuc3jtaYStoC21Lbg5E2VratEiaq1oDZe60reeQpVe9Cn4b'
        b'hvKLkIXJPOW2vvUa9y0dh83snqlRljbNTnvmtEtlPseW9kppl4m0RWg9jxXds3XRHWt3JLajsKVKZtuyjHEM7LVlHMMGDOrD90Shb7aRPLS0bqpsqGyu2LMM5WNsrhTH'
        b'yuaIeot6m2qrLioMG7t6dYU9H6UXXx+mcBDJOC0l9ZEKG9t6zIStcHJuVlU4OB8pbimWafemDDmENPMUtg5t+q3ew3Z8haNzs4rCSdCW166Bw/HbQlqKmnn3HZzbKrqk'
        b'vR7dC4dcJgykDtrLkyZddbyUJU/LGArPUDi7yKzb+c2hCoEEn6z3qvROHpD0jh4cMySIY02cpK2LFU4ihdBNFtYe1xyOLya2xzSH/6BDobd/L+3b4RlP9Ch70T2BeFB1'
        b'MH+w7KrWkEvKO1oDbjJV7Cq7N+SM7lUt2oVFJWTQggxUubZOmClXZt+r0eXC2E6kbScqBK4yA5lNm19XeW9k91K5IIyxC5PbhT1xpGwdn6lT9u7Pgimh7zNNyiToiTpl'
        b'6vp4EYcytPrxO3XKNZUjVUNd3Lv+pvE2euz5n9ZdXvGcon/p6I8wguW+2ZWS7pP89I8A1bHTW2k8h8PRf0qhn3/lWO9jFP0N54Q4R7KJT8iS1P/gnFCDuBllCZMoD62X'
        b'TgnV/otOCf9ElvRnN3lmCX9NEJeHZeayBHGTVTy4/zdUfrw/yaeaQNY2x5ejiYfdWBXsU2+StgFVgblM1OMBWSCnOynZw5yiolPgseAoPHmIVqW8F6s5wZ2wvfid6fNU'
        b'iE/jR+Nmduc3YirAazPt3xqodXpvQA8YvzW4ghPXcoob6iGJE9ZfNTzqvtNtTcjalZLVS82pr4xVF40Zw+eSiVelKliNZ3QbXBIma6tSagFcI7TsXvOMWBXsgevhjj/4'
        b'7nDJnD8CWV0Kz/K5rykkHrdHxnTt/JmF+SU5xXMLCqvuWuZgt5w5mA72lSXlawHIgI+/Hw/4M5NQQxlbW1rnqfSyvSP6nomD3HGEIt/IuFbjNfo71buc4r9qN2gGqmwe'
        b'bMt4jFsGUnBqrNYrCrwfipJQyxj9rzSKVSgmsdkYB8+FxgoTMKhRhVILhx0mXK2sCSwj2k6wv0wAtydwKa6+BTjIocA5uI1Uu40b3rVoG6OOqv1CLFrSclgWryMhpbFx'
        b'CQkisVrOZEojkSuFB+F6EmPdTG3KkDI2UNXLjXsv15PlYxwMCk3RmV/Ko7hpnBIXyuhLstAfX4hX/w+nqk7Ind1RZEXNxm6xryxSpZwMvLEyjho21uJFUFK8sB/X/1nK'
        b'5IrvK3kUr0uoyrHv8iC5pXHwHkTVOMwxNlGczZrEfNu772Mu9UkdpU1p2xaTcMfI/scU21FWucJCz2I2XJbKvY9VqcM/UrqU7o5iKd49m9sY+vGnqH4dqPJtxoVjiUVP'
        b'6qldKZN1FujMT6Wo02pqIs6OjPeluBSsfojHsEnb75zbnTAdk0EX75O+O2RrQYprXP5k3tDoq8Kr0aof3KHUOVz3eZNIvrVj7g5RVKcWxaf4e6LIo/fkoUMq1OEMyply'
        b'TnqHPFJr06nhUK7vU1lUllsIkU7DcHQNjf5+RHn8stazkTyb90BWQ6Nm+THVzFknSyNb0txK0Ahrogkdj0QFXshFi5Aabgw4CLYU33hylpJqok80P3O/IjWr5H1Xw/Pb'
        b'P31hG5PyaWuW95mCwzvcZihCn8p27Ar8plAwZYyK2updk96xWuT8zPvZ0tW/bv/1QtbVbZ9fK5vouu164Odf3CvJ+vTBCxe5emNTSvR+uPXWCpXQHb1LtZsPj115PXLD'
        b'7bkVgh1tB8QTb477SKboNP7wd9vxJ2aen3gpybPzI3HN4ck3s7IW6qybXDzB/ze9OX0fjflkxcq4O1sp7+qhpBVx57faO2Xr/Dwc/6zilqu7+dXj10orPx92fXfdqI9X'
        b'LOtouLLQ00DQke97ysxvRq7aIqsfF62+rvJZ8fOI77M3hzxQn2u08BNFy+jYd+vWeHqP3tydemT7CccpmXeKdNOtWmWbOJ2Due7297+qFffvu1DmmVma9UXqe1ryDZ3O'
        b'X74zNVHF7H5l+V0Tyyythrfq9txz/31P/Xvz9lT/2mBdlsi7Z1RYY+QvKP/mXtk17vXjrQt73qlctOHpFsefWl98tiGk4t7Wc3b3v62c9eX994v3exS92HC+8eGeod3P'
        b'y4PnMe3lmyd7b5XXNe59dOvjUveBys8nWy7r6F4XLN1wR7L7wzDzPm9Oyt3Bswn3zsIlQd13f/hk3czkfSo+Wz89/uFXMKDuaeC1Guqzg4/OvfdFoRH9TfWviyLepx0K'
        b'Fws21/z+bXNt9s+6jWk14gPvtVwVdQsa9w6lLNkPSqrU4y/qV0bulk1wiX3x3SP3qQPmV7/5nduyba4B9QNfjwXw7oS7wP5YPjZtUkOLvENgfxHX2Wc56x+mzg82/z/i'
        b'vgMgqiP//21l6b23pQnL0kEpIoIg0lEBe2EpAoqgu2DBjg3EsoiGXUBZLLBYQVSwJzPpMQmbNWE1iamXy11yiaZ5Fy+X/8y83WWx5JL7ef+7nI99bWbelO986+eLZT6C'
        b'/wXb5qIZJWVWg/NgC3lZAk8DKfbSzg5Ce1g4YxVGkUwDp+kY/t4pM4gImg73wCYjriN6uYu5EbbA08S/mJsnkNSsWmVuAfbCo/CSpSU8Z7aSgyjWYRY4BHcl0gL5VrBz'
        b'kYFAHgkvIYH8HNxC320ER0AnbMoGp9D0B9vgDnieMQ0e9yGtq4MKsFmYoZWCufBSzkymHRgUkS2lGhzGEHt6CXlCDjjiBVvplt+ADTFIsqarBfUcytiUieTtc6BJm/sI'
        b'bs1D7wqCsc8zd+WMQqbPUqiNPmgE7Xw9Ugrs9AOnmJFWPOLpvBYJ04dwuQ3pWTkcCgzGmoJ+JpLpt4Pr5OVNoD46Mz2b9DY4uZHiLWSWzgZSGgbjxGxL7R6IdsDxpmgP'
        b'BBezSZRBiuVs9CGNuVkCNIJrwicy7ZbFCRz/B07DBFnsKa7BWil6dJMVs7haKfo8k97nlkxnsM2dkXxq74ykKUtblaUnTktR11yn8FU7+kvZ+Gxd8zpFtNpRKGXfduQr'
        b'7Fo2SdmfWDvLfBWcW9bjlN4aO6fW9OZ0WVFnhbyifZkyvC9/ZHyqanyqNH3YbpqUobG1k86UiqTjZdPUtj637TwVzAO5aLvG2Tpa1kjZHzi7yWYo2IraLjO1c7CUe9vB'
        b'S+HV49/lrwzoS1V7T1Q7xCNR0MFRxpIlyTmyYmklOrV1kPm1xCuSFMVKr65SZXIfo3eqIqevVO07UePiJU3WuLgrTFQugVIjjZNzp5HcSGGkdgqTcjS2TrLwltjbbv5K'
        b'xlmjXqM+Vl+lKmzK86nqgEy1W5Z0qsbFU5p819EVCW6KeSrP0D5fFZa0/v6xm1dXstLoaJbKLUw69baLn0LUs6RriRKJNTFql1j0jq2jxhWJvrJ8WbQ0BSd8qWmPVbJ6'
        b'TVWuUdIUzLOkNafJ8uXzb9kJNHxfRU2XqTRJWipdIk3XMzQaV8/mlI9RKQWyeDoXido1dMR1fF+ENOWuI58WQfleRARjKSt6LYcc1PxEdM2Vr4hoj9P4+vWkdqUqo/rs'
        b'1b7RQ14q34myqRpvf1ocG+dPGpzfF6keF40lMV9FntK6q0AZqYjvG6/2idEgoUwnht03RvIKmhd+4xSliixUiq+gJ7sru2/ckK/ad/KTz7O6svqc1L5x6MzKutWo2eiA'
        b'8YO5DMrG/6d5DMrKTj95xs6pR+abpZ3Kko+uyQqkGE9aY+vYkPmgDJfyrvW4nyXmaPa+wEwzzjBnvW5ukuFqRHN7ZnfYK0Q15XfYJaIa0R3jstKaxTUVNZV/LOqX+GAa'
        b'5iChOUS8aMjBzkQrO+H0I6WYQ/T5CclOPn+ETXyOg3NAGggCejlkCUXLIQRoloNkJiqKpQeWZf83MZE51ONw1Yj/xDsGHAiHpzNzcSgGsb4hWcMGDLLgEfRf/UxwpGJp'
        b'7TCLBClIIi0Gig8jgUPxohWwA043y187BtJanpczKB9Xllv0V/RAsR7tcywI6WmVOR64UXJlrCNXmOTiTGHlM0mmsBJlhco2ZtgsxoDf54rZeJy4+PAktp9L6fxe6VHF'
        b'ZZNDgY7vx96uZTPRqLr/kQHF297/eECXPDqg+iYY4sQfu+TKkWDxrbbZFY/UzizdWJW//iLFNTH7i1mHMxU6xPLn2PyusZKMGSsz3VhpYeHvV6GxMneU1sjy3zXzfnyg'
        b'OL93oHDB5DDHcKCW44FyejYDVY4HiqUdKAbtBRnF/v8zVI+vPZMcGkz2BmwXjcqRflZIjIT9uUTI6gjzZK5n80KMV3yyaQ0jopZczFyPJMigl4ywQXhrtC1tKf0ujMGk'
        b'eBITaoXIU7RUQtGudENgD7yQh+0NoA30U3AbBQ7XgEvkjTPxRpRZTSiHQgLcq2nGFO2KmA8P5gXD54T28HxaOovizmUywLXoihel3zAlCvTAbNs7A8VytPpdaBVDTcgy'
        b'XpPNzb1p5pHdbYWpecocp0OvWL1p0mJeylsSUVp/omQJ542/Rn4eviOiPLHAd1644kTZlt5QzjucrK7dSV/PqSw1L32ntLiQ9+mL3q/s+Mabw/V9uLn7Z+bf2G1v7Hn/'
        b'FROzmK9LLUWc201hsduCG4zyFlp5djuFseU/Oic7s5zfvH0zUfS8Ejwv51LHfOxvmr0k4BG2LQJe4AmDA9Jw+uLF2aCNGZzjQPjPYtgBlDTbDY+Aoxh6l+a7LybQUGv9'
        b'cAfYRzwQmsBlsA/uycVYxrsRB1xWQFjfikB4AFujwGa+DpSPudYGbKO5+ueMxoOThC+GjZgx3gbrNzK9wZA2nWUoPOuttSthq9J4Yya8BhvAFcKGLoKnYAPcYStMIxYg'
        b'djQDnJkZQ8xuCX4R4BSG4jMwWYF+eArsEhj9ng0PL0it1YVe1GaYAK8oWbIY76ZiR92aPkZpjS6Y/jq1xjXHtcQ3pNy2cpeVdC6TL1P6qz0i1FaRDUmfWzlIV8r81FZ8'
        b'hbXKyqchSWNr35By18b2c0d3mQhv/81sxBFa2bWaNpvK8hVJ8jkjbkEqtyDlDLVb6C2rsAdGFGIXve7xKHPrfVmNWbtzNGZW+zIbM2U8RZTc8pZZACqxNbo5ujV+f7yC'
        b'PWwbpKh5xzaoIYUwCgZkxkj8Ff4g9m9if5AO0G74NLXBn0wO83WbPaY2EkJt7lF/kORgajtmtRtr/34fz0CDZ36QWkCJGXmUmJnHELPymGK2MzUXEQ90NEP/jKKYeaxY'
        b'tG8QBSpxy8ZK1CheHhuTJh2JEXMWcL2pPI4LlcfNM4plio3IOQ+dG5NzHjk3Qeem5NyYnJuhc3NybkLOLdC5JTk3JedW6NyanJuRcxt0bkvOzcm5HTq3J+cW5NwBnTuS'
        b'c0ty7oTOncm5FTl3Qeeu5NwafQ1WtLrhrxDbkLv8MGqBzSjZTGFMYIht0HNYhWyMiLE7edY2z0NsV+aJWBivO0bZoiocWFGxDI1Unb1J3tTpSfzl9DU+SecSYiJgkM1m'
        b'DNk31lFcHFmTwDNA9tf3MNmrjfUbAPfZbgB1eSbpVRU1FaLKirpSCcl5NKbtFVWSGhwXEmJiErdCJBYt5+PFGMfH+WvwL35NNV9EvzI9JZW/pKISPfrYNBu7qXjkED2y'
        b'BdgTLUxzgGcQJZmehuTX4FlaMBNwGjYEhTCoaQyjaMb42hD0sKMt3GO6Ig1cWZmH7ukezOdhBR1syCbQ1IhOFvN5ZuBwII223kfAB4MRQdpGcjRgtPVo0ET7R19LWijE'
        b'ANb7MrMZ2C9zgAflzHXwMmwmLl5WPNAnzHCxyKazSgsZlK0/C7aDQ/FkD6qFNxZmRmQwKQY8izWpN+AgOAzoDBXwIDxaiWh3FoNiFjHQjbPhFmK6RYeMQVumLgu5abWx'
        b'KRPKwcXptJ/dALwGdmFtSi5sNFuOobVxqnLYyZoCrsA9pIBMeH1qJjidlg16PEKCcSGWPqw5daWkycvh3jKthgB/0mlbHhhEX3QcysjtWbAL9GSmZweiB5hoR8/F2kGw'
        b'BZ7yIE6wWctBO8H9pzH/oRJsZsIeD9QdJHS5FW7B3tZZ8wIJVi6NlJsOFUQxPBug3iCpwJmLGLAFtIbCo2Av6Yw40QqcO6G9kED1k9QJ69PJCGSL4Alt7Ls2AYIEbmXZ'
        b'o1oOEj3xpTA2xePtMaISCyu7HQMp4tK1CMhrcD6Fwlovygt2wi2ETWhfjHbItEo2ejTrYbWI0soLoD8LniTpDnCuA3ABHjLIdxAF6ul30abCrmklnMqGwtl0QpXqEjPU'
        b'tCkCkoCBJF8AlycSl8pKnBaA5F+AUtCdTgPjkwQMXNhFpkaFtaku/QLYAS8YhzOBbBE4RYI+JPBsFmoQ7BU/nsaAZEhY7Um7OzY45eF5AuvBJSLqoBGzgArWQtBmXLHG'
        b'ZR1L0o1o9p66V4/nZ+bAMKsLtv7L27a947k8aYrUPkg6Z5gz5VOTg/+c289ofLv7TU6M0c7iN6c69Vz87FZVXpKD/LWb676/n/mdbL3XYbuGsqsDvOm1C5eb1TVavZj5'
        b'4nDc/ITvPaZ+MzU5+uUBzt01X1UaCe+88s4vi/O2HY6Le7vvrRuiu8FB6xtTWlqccqZL2EVdlW98f/Av18LfUjOHdr+6OXVKwntrt5R/dOjAVIeL79fvCa58p/5vczSL'
        b'JKmh10/edwidtLl1zZrbjKuHd7YOfn1gnsbH9mDuLw5LToc6aK62fCR9jbNR+i///D2F827uPVZf+PCdu5yP3U++qnhnQlTkrYXhb5TuNf/ToUV145z6+/817vXNr0x9'
        b'U/7BZxG33p065CI78UK3x4s7Zn2d8lJqzupDzu1Zr0rqvskZaCuvXrtB815hz+tvHTg0u8f6Ss8n36ZXf+CUH3vhRqvpx9/I1py4lvGtvPfjkYc3v8xmh9f9ml/XsuNu'
        b'yvKcm1+gg9u1r858bomvfO5Z13Kt7qO6nOr53753+oWcg4cEV04Pxppvyj1798V32/cu/GBv8F9/ncP95c8//4Xl9+2NP31dved6qMCFME5FkjRhWgKUj7JN4DnQT6sx'
        b'969bkpkVGEKzVKaV8CI8yITHlvrQQBwNnj4EgpW2roHB2TzYxNwAL84i3NzMdLYpSeFdGxw4AU0qDNZiD3ayeZxkOj/6mRy4w8A8NgEc1SYE1+a2bwBKup5dcD9ohd2I'
        b'yDXBfSRHBRez+a1+pJ40cGApaArVk0xTCeiE+5iwzbWaoB7Dgw6I59TivYwfl5RhQqN5bPaEjei9DJqQHkUUGRNTB3iYHcedRZyjoqfi/O3gCLiACSqrkjELXF9M+szO'
        b'FPagWyY+hJiyYCcDSD0SSGvHgV1L0K2QDLSspTQ9tShnxcBdSaRaT3jRHH9GykZCTrXE1CaaBbrgPlsa/kEKzuG8PKhmeB3TVJqg2qxjgcG6STSjfQ40gXqSpExLVU1n'
        b'hIAd6KPBlumkGYVCiJO766iqqd+iRUyogNehjCh0k/mg3wXcMITgZQYXziXaYL+J8AwpOhRtd0d0VNDSmFWTFEqmhcMmeAxegFfJQ4QScXlM5xqt+rwAKsBRPCCdqHF0'
        b'OhhMimzgcRbcsgq2kUErQeTlJHpIS49MkbzQaMeEgyvRzCO74CDYOg2Vn5UO26fRpN8imZWKvvnyDwJ0fzHYDRqEOUTjsgdKAx+nWom1RtbuYDPdGaCFdDrajWF7Mb0h'
        b'W5Sx4tZNozt8AOwHB1Bt4zmYtGnJmk0MC1yFA77kEWd4EaD+DHWEJ9LS0V96RdhYsEA3F+wRWDwjzy9saBuLsmuQI95Ky8qNTQ8/i6VND59HK30UKdr08K6e0hStptS9'
        b'M1oejbEqlFFq1zB8mb6SIE9Q+tL4FR94BAwLEtQek4edJt92DVDaqV1DpCl3XT1Jou5Utce0YadpGncvxTj5ApyZ+bZnkDK/L6B3kdozHmeVxy5h/j0BXQHKiWrvaJxg'
        b'W+PGxw5IioL2XJJsfOwpTr9dcra8t7xvrVqfTP22V4iy5uya3jVDJurQZLVXCs40/sSLOM30GvkaJU/tGY6r/9jTh+S2d3bvdJI7KQLUzkIpl2SP5itS1Y6Bn/iH4Gzn'
        b'qfJFyll9U3sXDrtNxJnUJ8hz8J9YlVvw90bsABcZu8PsngUlCFWuVQXEDnmrAiaNBCSrApKfT37VWh2QKTO/7S3oWzVUoYpOU3mny4w0wvA+gUoYLzO65RSgCRjfV4Te'
        b'kxl1mGuCYoe8VEHkhkATGNbnrAqcOJSkCkxAdy01YdEydqeZ3Oxdp+B/3zSD0ziVWwj+G4OEwe/NjbQttsJJ0bOas0bsIlR2EX0ThkJVkRm37DI1QWiw8Y1bdoKPvfxI'
        b'x7l6dsbIYxQZatdQKe+urSvuoTS1Y9AngjCNu59iico9WLlmiNO7adhtssbNVzEL1YT/zlW5haI+CsQ1Ygc7QTj6pICJQ1NUAZNHAqaqAqY+X/xquDogm+6jNc8bq6Iz'
        b'VN6ZuI8i+9JVwoR/10cRfbGqwElDIlVgIumjiFjURxZyi3edQn9P4wzP56ncwvDfOai7UDdpG026Kac5Z8QuSmUX1TdnqFo1PueWXS7GTxD0ClBXoZs4+TjuqoMWBmKy'
        b'GQ0wwH6KNu53KcxHF7VBvu5oVOIKQxl6YR6WoX/8gzI0Scnaxg2kTpiO/89SdZPEtL5PT1M8Sn10WbrfRM02yA3sTbJga4Wz0SzPzy4tt4Bxx2ixpKKs6ukJsWNRbw7j'
        b'ZtkxxzRLlxAbvy2qqRU/g7Sw5XSL2IuLIop+qzlq3Jw+fS8FpFaKyvgVS/gVNfwKCRJQp0RM0ffas0ll/Cfq6dmFcYveG9siN5LwVVxaUlFTLX5m6cvFQs5vt+I2bsVo'
        b'0l4PbSvofOXPpjeW0ENkvHh5dUnFkorfnjYf4PaM5lz2J0mmRZIaPv1y8bNsWLmuYaVrSotrfyPBO27YR2Mb5qtvGP3yM2+VEQ208Ztt+nTsGgvUTeoaAxKAZjdd0DNs'
        b'WUlpEZqkv9WyP41tmSdZ/eStZ5cxWz98ulXzWw36cuzweY1Zbc+sSfqprlNK/1aTvhrbJD9DjRkeQZ26bGyzDGscmzYY+7AyC1h6n1Aq30D1V8XwQM02UAUyxij9qCQG'
        b'UQU+dvXptqDHfUK5T/FZJa377yY1Lhcw68JMyPxfXV6Kek+MuhBNfYNVIC6lc7fX8NGIV1XXPKKFfGK26mmOYXS26ldqPxowyFVtJItRMwRmTMuwjwQMOuFIMzwB63Vy'
        b'LJBDRcaoHLsM7HhCruRvMQKep2471zdv1Ld0SVlpzZjc1UWzGZQbAbsbtgv8g8mTcW3iBWjafWvgOfrj/Nn/UfLk32NBRgP6X7IgP+Y+/fhURGN3xbiaI8HpdDPv147a'
        b'+ktef5Xieu2ONQuTvoUNbimW33JYK75oQMNI49bmF48qI9AAcirpISyDJ3/bwix+8G+HU6IdThtKKyqi4fQXKscfXSZNOZg7xuhMxtOW8TuNzrhqcSG6+pOh0bkCj63z'
        b'HzU6azNuwkHYDbdlEn0NVIBjbEsG6Elj08bePUA2IxNJ/Qzs6VbPjmSAAXisvOLwub+xJBHogetv/AW7c/NfsXq9BDjdDHhJ+lKzUcnOiPYwTuSWtbutd79wsy4r0Kwj'
        b'OKmI2svnthxJ0M3jJ7HteFBHv/Vv6HDH+rFuJh3rSneshs37cc5sBtta+JMFwzriY76vyjFy2CpyzIp5Ur8+XpNYhHr1G12vorJ/mot71fjZZHsnK4ZNCCOdq5nSG/Kf'
        b'uUN/XbBJMvZVl9AMAiKIY804Er6kpqKykr9KVFlR8ghtfNxDg5uTn0q047tC6yge+jiriV/zHcIj2BWF9jPYkg3ozvT7dbSR3QaRzChFjYkPK6s+Oc5nurlt1fjGejN+'
        b'3px7SkoO2PlwxyvjvPoEbimy+ql7gn0+cPPgcjncr0PeKuaJZhXxSnmiiNIpkfM3MwI8XtzT+4pdV2t4g+Pg+oCtIY6sZCvP7l2FS04KwkZ6IsWoQ70+tvnHkKWAR8M2'
        b'HxWCAaGBpogNDluAi6xpcB8cJDq0OnBxIm3mATegAustiZln3kZtQrTNYAdtMoFbgRIr+IjNxGYjnRWvswxcFdLEwi/HwAik1GbFsxGaZI5qDk3gFWyNSY8l90LRApNn'
        b'poMOcEOfWBwcMKMjUJesFMLG3HRwig0uwRaKW8n0nikgrwVEwIbM9AXwMjgVxKXYbgxwDt4ApwWcp8u92GvDwGrOq5AsJqM8KkvqrpBVVEfP9Ht1iDw5ubVuaN2gcSV+'
        b'luta1ylKepb1LNO4Yp+31o2tG5W+Z4PPBqPzj+2cWrObs0fswhT5PfO75ksZt22xDd1pxDZQZRuI3Rq5cm47T5qEHTAzmjNashThKjtf+rYyX20bTpc6xij+hG3tiTZx'
        b'A6cAcSVWDixHh4c6eZ4ED5GNDtvE/9BuRyiimXgyLvMLXHoW/kWg/2biX7n4kI4PqfjwNabYBVzix6onTeJ4dEGbu9f+6cB+o5h+2BVA/DUeKhaSasVYzyp+EwMI8nQS'
        b'1B2eTmS5w6W5+ztcmr2+w9NxtXd4es+Iv+n7heD0mf/fFaTYsfEJuHsuXO0BW7klDjrcPaa51XdcysJeHimvkQWqzP0eMOcyzMd9T5Eji7IYd49cuL+KqYOri8FwdXEE'
        b'rc7B47aVgL7iENeQOgpyh/HrbBMZBOVOeykCX4oiV7T4dVEYv24Cwa/Twt5NwrB3kwnqnfZKHL4ST65oK8O4ew5TGKQ27aXx+FI0uaJ9DQP4OcUaFoRxUJ0mNaT9xDMx'
        b'j7rvQDl7qZxCu2KPTkR/GtIfsK3M3b6n0IGGwiNGztXgNBzANkO9idoE7GWCK5bFY0iwjfbv91g3lOD8RF8MLvHFcEL/qDxWLJP4CJgX2BTYRnH+qA8G/S7i30yIJwPt'
        b'g+ESRi0wfsTrwXi03jzTWAbZx0xRjWzssWFQo8kjz3GQIGA+5gnTMV/glGcRy8xzJaXZkPKs8NNLGfrnzfTP69/BXijaf0551rFcD8qDynMrYBCwQNpXwrzAosCqwLrA'
        b'tsApygx7iYwp03xsG7T/eOifMeoL21hWnjvxbuEQ3wvTAjNUmiVuX4FdgX2BQ4EjKtUK+5qMKdXisVK1JeK25tmTUjna8ixJWQ6oHGPsozKmHEuDPnTEfYj6hYk9Vwx6'
        b'0SrPWWxdZonENY87Flryjv7goPQKC1O0331tksQfex3zAOivhC9C278hU4C9PUQ1fJEYKxJX1lYgwmKyBAlP5JkSdFpcg4X6ihp+jVhUJREVYy2IJMTEJL0GMRPVYm2R'
        b'+tJEEr1Mi7iQKr6IX1axqrRKW1S1eC16NSSEv1okrqqoKouLMzHBJhgsFj/SYD2zMmVqflIIP6W6yr+GXysp5ePWrRBXl9SSpniZCJi0rvhN5iMxoPqAyxXokMDRx4Ay'
        b'dYiSxKnGSB/9yXm20Z91Pz/mVKNjxJbrvvF3+dXouw6LvWicDPub9B4ePDIWJSH8dKLuLKlGNSL5l1+6pkJSg6+sxl1ZpNX7oQd1FWrVInSdjylLVlfgRqA7S2rR66KS'
        b'EjTe2jqrStA/vmjFiuqKKlSgoVrzEc6SSz3KWZrn1CZQGEBxHmgyTJKUpjcJwv1wTxZJaDQzLSsH7g01Bh2E90Ic3E5TeBw8l0fyIcFexBgNwqb1jCeVgt7V+rKsgjuN'
        b'N9huIm4siJnqhjtgCxJu0thUFLjE8WdAmUQLFOa/EXZagn4hmj0YL+gYPEgcZxzs5+QFo/fOweMRVDGQsUIoy3im70x4iLgxwYF58STvrTYaFjaAPQGYHZ0+fWbwLCYV'
        b'LeCA5ixwlsZ264YHQTvYmS9EU1ZCSZK08ZNfZjMJGx6WWiqMNLGgSB6pghmgJXP0i2ADLhx9LNybTadbmAEbxdVGcLPPFALkFx4PtkjAzk0rORhVjAK7bGF3RWNfAkPi'
        b'jrbq3ArJnpmTcmGY1YaL338yfcY2qxOBO9rS0szCliQFsiZTvu/P2Lmry+YA59x3RnMK//xrUVpo9rr0FO+Xrn9/7SZ73bf/FLdvhELTfy2oeq/Hui//QO0Rqx+/mcte'
        b'8EN1R+UnM9tXdLy55q1lU679xeOW0vRP+V5fbdju8cEnVvMjofvG+9OSL3ATXpsBpr4omNE4U1O8V7zywcLFRtvf3/jNt8eruJaLJ0V23FtgPAGueWXni19NmL/i6KzO'
        b'b3on/+ma6aeHzDqyH77dsRcO7n/4fe1Hr025e5V18sMbAcv+8l7CuuULgqyPhE9dtF258s1psesrzf8sM718/N3bqelvnfya8/Yl1swpywor/7nmhdgzFy227boQJeNw'
        b'tz585VKbKJgbmPDVrq8/M7r8asSu6myBHXHJDYf9NjrPLTDowghfCy4QUcAU7HfTu1nAXVCap3OzSKTTjBcCOdg86j9VuCSDCXvAENhGuzhYiYRge6KBzywcZBIRZD3Y'
        b'DHsNnD8Qs9BayYTHci1JsemwfyZsQnN0jE8tOJBIzPcV8DzckhmHphRxmBNwKWM7JugCzaCDmNODkayyHzYh1iMHTyKwH3QFIkYNnGfNgFtXEXkjH/a5C0PhLsyZeIPL'
        b'XKBkBlXCw+SjvUDzXNgE6uE2vfcJcT1BV/aRz1oHt7sJ4a5lGdmox9heDHBoOthCh8h1pAGpLgyOv5aLo+AmwaNEl+YDLvtoPSJgI3YowClE+oMRSwcustM8ZtDeKMfA'
        b'VbBHL9jBnbCDa8s0B+c30vq4QyucQJM13JKbk4lTbtCtswatLLAPtIE+2rthL+yYjL0bcoib2YpaREQs8ljZ8+GhH7BPIZSPd4BN5nyCFYSzq+xNy4Z7wd7QzGCSBgYD'
        b'JE4D/UZgHzwHzhDfaBdwAwfZgnPLswz84Aqm0+4inVMzDTKq7Miik6qwF4FtoJXOiNIAznmij0INAnR9IfAi3IuYUFTSjQTwnMDkP+DWMeLBI3A1tCuD49iNdaxHw2wG'
        b'LQemzkVyoCeW/j5w8R32S1W7TBu2m6Zx9Gjd1LqJXJqsdkkctkvUODq3rm5e3bqpeZOiRu0YJGXrHBzi5fFKtrJM7TpBytM9tbF5o6JkxFGockSMs0NrZnOmgn3Lzu+2'
        b's7usXMm65RzUx9Q4uXTy5Lxhr4i+2YPz++ervBJvOSU9YFEuwcPOQR87u3Y6yh07PeQeSt6Ic7jKOZy0JmYoSqVr0ieGpXnwO8vkZe0VndXyarVH6IhHnMojTu0RPzRD'
        b'5TFZxiLlfow+C0d7FasdBcQXY7LaI3HYKVHj7oXdLTReAmK95/sTPwnvcYraEf/JKv/JI/6i56e9kvVC1kjKfFXK/OEFheoUkdq7SMo+aPnAGRX8rnPQzw9MtD8kxNlT'
        b'6JkaxHrRJCx1EuvlIJPUOKOXJ5lMM9XGiJkYmLox+/I77N00lobewm1g3kYTiHI1NYgHk8xB4rAXxtLw+qPmbTlXQPWaRv1n5m2tgYTzW8aRx2alztIdj77AwNIdqWeF'
        b'Hud9DPieZ2j6Fn/4dMO8uBn18WTcQr01VZzHfcSjfiyMB4s22BSw9XryZ2uy+R168v+hyaYMMedfMx/poCdaYc6+HUpbYU5F/+OtLw3tMDHzKYGAGZRYJGAQ8gkPg6YN'
        b'Y8inlnaCXgFiBhtKn2aGGffIlJMUVy4m0B6/YY2ZOe//aI2Ro+mRbGpgjUme9+ysMWPCxIhuuYDxXwoT+x3zjJ1TOxH99l8FL6GteMx2il31G7MCM4LAiXzstQ/a/EMx'
        b'G9uYm4WVpuAkaDSNnWFXsb7+JEMyBRVy4mYQUSyL/MCpFyhGY4SZmdfuJDMZ1e29vX2LV5vzOJeb5a/zRMcjdoQFMLLr7yfLxLLCE+84o9lSudnINbdcwCLbexA8QCDX'
        b'H93dJ8U8tr9vAL0k1Rhsz5+u95WFxxZo0WR0vrKB4CCZh75gW9hj0xA+B86SbXwWbP8NU8co6X7we2emzrAkoGfmT3PQzHRyVxSM+E1C/yeegxlqj8xhp8zb4wKfYG8y'
        b'+m1701OCj4jVqRPN4WzdzoKtTrPxHHbGitY/ZHrCzu8CJvGtL4WXQX+mGWwgxidieFqdRu4EjIPtmSWo97HpiZidPMHOivaMNpYkCt1e89FtbOjTmp3sHo4annaek4UZ'
        b'RW75h4Hpier4mfuNBVMLv/NvlOejH/0PPCZOTxsTMgrulN4KlTiPwbMWPrBjWUfc41Fefo/ZoThP7+8nVCxWoN6eYjpqjXqQNO+PWqMw8g+igljHPIZw6EM7l1K0UUob'
        b'aMQtYBQYoU2AoycdnGdIOtAmULfEZFppDV+k264NNVCjyo/l4tIltCLiMd+2EJM4cWlNrbhKEsdP4seRYKq4Qu0QFfKri5aWFj9q7X/cosXJqcVtBFcKkCzVpFXGFkyf'
        b'HTwftsya/cToI7A5yngp7ALXanF6wYIok8xHdBSJC8eK4zNNjTDUCbhR8bo9kyOpxm/Zzh4oPoQ2tFMvWgEb4IC2tSw5v8YjmSec8A/+kqz+6dy8VF4mK3A/eOV5HJJq'
        b'ucRMpCot3nwyo9RMNHPKOwdfcXrd6cUdFSHD293mLNg89XhBLCvZO3o4p2ro0Gs9Wbz3pzgXOMWoqcOrzLelvSvg0gEF9eAqVICzaCkZiJzBUEobwc9GQilsCkJy5MEx'
        b'ch3sob2wkdh6gmsg7YYWgL1aadcJHCeCMjzjmzga4rQX9oeXWdMy12mjukytwIXELdN5THAFdMMz8LQ/IZ25lm4GwQh18MgYAgtPBf6RWFEDYBFTHCuqnTt3XB5ZwAb3'
        b'yBJeRi+v+zWYkPoqUpS+2DFV7RiFASAeE1+I1DHl+XyVX7raJWPYLuO2i5fCtz1YaqSxdWmd2DxR4dsT1BVE5+dT20YQILBJapeEYbsEJEZJDT1ceTQpJiag3zZ88Ubp'
        b'sZZE9GJZ4QQ65BsS5FJMIpzu/9Fo0O6nchYlFM0bagPQKb3D0TMHfqirJaSh5nHnseoluqDC/zulSKLLfAqleKJvyYOd33MI1BuUnqSB6+xwJPkUp+yuK5Ija826zJKy'
        b'ZIH5eN3tMWWd//FDAZPmT08VwPOZPrAdY1SQOAja5OMCD7Hr0KI8qDUrgza4FeP8HAdH6bgROhRvCTz+ZCcUvc9CAt6enjS7tR1HZrcXPbvv5c9nUK6eIy6BKpdAZZTa'
        b'JQxNWCT+opk9bOU3ZpN62pyk4elG2VpcvfgsmoEluk0KzcCfps7/o+gHeDdH4gGJiTaSiFaVLhZJcsYo8PWK4ypKt10RBT69XfGQXEVFcf8r6nscE/udfl5ig0aJNoHp'
        b'E2dlkt6oUlojwi6iItoZbXn1KrTZ4YxrunJ+7xSmn9H2ShzW6hMzShBW5S+vldRgVT69ZCQ1FVW0wywWk4lunhaVx7gXYmsKKqzEcHXgusWi1fTnoTb/W7W9SU5tJEVS'
        b'9XRbj9k+6b0TXsh58vbpuYho1tGScBKCw7NwwGwaBQ8m1RCovI0dX+ZlryEoe2yKLWfUZDQRbfiNyRjfj+KHzao0OVJkR+XTBlUCXt0VB1qFcFtqLipqJgXb/OMq+i1e'
        b'YkneRDe7//5crTTbAvCttnsOvzMhdVK9ZumnIOTKLZ+hj/3bhiJUIY2ujh4vPszY1JfeZPXdqzejYXzj2b3/ZLn/abj/Ld/uk0cOzfvS90BrpUukMm31+z82P2QOvZxw'
        b'tmFv5l7PH/ltfz6TMeNXl+1+O171Dcs9+1xg1PuzeR29N7uvFgV+d/ONvwyEZb3FXPB1T3/WyljLIfEhO2+zD44HvJ9e89cNdy8mfja1J9B57Vxu3MyPMgu/fnk4e917'
        b'GssbX37ZZnJqwaKPf0jos1/6XWf5XyeOO3nDuZT/3Lr1Ah7RONaCBtAl9IDyNMPIQXiSzkw9NC0R7eAdsG2shnbxAjqB9GXQGG8K29Ya7OXajRxuQ0UQUMfDfLBXGA23'
        b'jipxLeE1UvVyOJQuLCsP1EWvGU9kgk7YbUo0sAtgPWwUrpk6RpGrU+LCbg5hRFbBreA8bFroPkZ9PRf2E/WxrXMqrXqOAXs4FFE9u4b/XzSgfEOoMSMtesQdhyfQS3Sd'
        b'0Eo1TSvvi+f/Z5yAPUYeY9+y91PaaJWh7bHSlAcsymHcPS5OazxfPl/p3Jekdp/QbELDSxmoTx1dWtc0r1GwFTMUMxU8taOAPNG8Tsq+a+uCNaVlihpDTanCrsNCq8Z0'
        b'lZpKa6SmD+xRTe/a+/38wApdRs+SO7QC8gUz62QrFoiwSfZiQSuTZA8j6GWSHKZVQBobUP2+fxtwIzGmDHSP9G5wBb91FR2qDVWP8/Fu4PXdH1Q9imdQxDGSqELJvmCs'
        b'jyKh/VuqsdsNu1JUVVZsZECqbHSkCie7TDCjN4pFrEXsRZxFXLRhYLcAbEo3I64BlgVWaAuxLsBgDrZI+sF5Bu2ibLQbiVG+qcFGwkMbiZHBRsIbs2UYJfHIRvLYVUMG'
        b'R1SF9jSTpJISHIJSVbp6rE8etqPSNlnaRFxcLRaXSlZUV5VUVJUZoCmgHSBOVFMjjivUC6KFhKrjPaqaX1iYL64tLSwM0ga7rCoVEyciYt03ET3Vks8vFlXhvURcjR2N'
        b'dF7pNSIxWh/8IlHVstENa4yl+BFW7Yl24pDfs9XhrQ0bqiUrSotJi4PoXiIb2WhoU1Xt8qJS8VOt2PppQlczGnu0uryiuHzMjklaWCVaXkpqqKYDKXTfUV5dWYKIg8F+'
        b'+0iYxXKReFlpCW0Bl/DpCKkQfi52Rl9dIaFrQExAeXUJP25JbVUxGi70jE7uKCQv6lpTLKqsRH1eVLqkWrtd67FC6EGpxREd2N1BRN4zHEP9l+s90OL4j4Y7jTrD68rV'
        b'OcVr3y2KKHr8LcMgqUeex+sO8SJ5ufwJkbHB4eS8FlFTNGlLSnVdqXsXTSV6lEJI41NKl4hqK2skuimmf/eJI+Av4dMJeNc+yrBoRx43bQXi7NGvJ7BPY/gY28f4GP8c'
        b'YilnVIOtkggxYiGqKRN4GAzmgRM0doc0HOw3XbWSQTFgAwX3cWBH3jwBg763PTNPiCRbJPOCvYwaUTK4Ds7XhqM7HHhxJnppBs0BBcz1DQkOgA2hgenZiB06kb8CnquZ'
        b'RTsDgAOBxjGrQ4hGAfTDA2FjfCDoMHK968JKqKSKF/FA18pIwhYxjHDeKCqgflGh2ZYIPxqNOxEc9MJbv879IICO0A8SBGdwqElIxt8n5MK2xY50UrGpOIvnfi7FsKZg'
        b'pwc4bCYhJXMWYKBkas6ygMKsxQu0mZ72mBIubM5IbmHWMn9f+mKFhDgqFC7lFGZ9K8yntPnRroJWeJRZFExh9GV4DV4nCKLkDUkVTmxFBbxfWmj20ItP1eKdAu7ygXLY'
        b'FJyRnZdGFLTpqPW7hZiH3C1Mm6P9FnQrLSgjKyQ9OBBntBOYrQx2oNU4l70w8KyODwV74DEtL7pbgPgY0JufpjeJgy3wkjE4mm6VKuAR/3Zf2O8Gm0btt66ISWkPCqNB'
        b'sY/BnuhRKJOroDeUCc7RQGUdcM9kjGWiBTKZWAyOgP2wkziWzKxkZwaCY2PgTFj2uWALeTUVyFGhe3VoIvBSIuLMdoD9BOtjJuiFSuFoCH8ybKYBRUCrKe2Pf3r5bB2i'
        b'iHE4E55fDWTZ8BydRbYRHpgkhHueCCdin85ZUrJOYEpaGAkacaa3YC0SDtyCGnASDMKdxMcFA+AkjOLhYCfpInhknRvcSrBpYBscgj3CjLFoOG3o89vhZUi7tvAdYbse'
        b'EieFAwdtWGStwUawHcOZaZVFk5PCc/3Id6WgBdCWmZc8iofDhPLlpXQqx3pfXy0UDo3dYMTUQuH02pOXKzOgfNT3em4iAcKxHV9LO333E2gZLWYDdumeAxXruOHEJTME'
        b'XFs9qsljBoALWmiVI150d19jTdHD5GDBPCYDbJk8mZCAcni5KA9KC/BnHaLWgpaqOaCr8h+//vqriwtZLLwvpxVmfZCkjbHg4ZXZksummGaUHxqqG+AUPCIwIdkcbRFj'
        b'fFhiIa6F/WawH9SDnZZgFxysQV27lJUO5Qkky2kC3D5H/xB5QALP12KNQjc8m82ChzxgB3mQbQyaDB9cXbPSWGxuwaUCZk1gsRGvrtAOpTUasutwoBael6w0Wwmv8cEe'
        b'S3Eti7J1Y0WDzdXE8SheUiQp9F1Za0KKsoQXjGE/qtZsJZpe2gZMXsTlwCuglYDiCLJqJLqnN5TpHrEtZSVZgB4CxbMKYxzrn9E3zgOcYa8PG2dTR4qZDo5u1D/jUo46'
        b'QwzPo5ZNZcWVV5PsfLXwUpn+CSfYtBpRVi5lxWXCMxxwiIbOOeYLLpnCizWoGWbG5mIOZb6RaeIBBlaDq3QazSFwFvbkZcPmPLgHHswDe9heJIVfGwNeBAeBXIuOD69Y'
        b'5U2fjn9uRUsQdIhA/WJdisA2cOTRKqbCc2DADZ4iQ7/KGvRK4EVLdIsJuxnz4IlAsBkeqcXRMxsngEuwCdG7zNDsrFynKQV4Z5ipFZ6DMOXbnZ4Fd2Gol/oCYwmsz6Mx'
        b'lupgVybOdsWIw44tp+EB0IXICx7SceZoeAbSEBXIDEbrJYdNWYMO1izU5c/Bo5CGOfp7tisVhbrYwbpwwfrI9TRpfiEukMqnqBW1zoVFb8esoujshdTfJ2t/BCQK2ER+'
        b'jw2Cg+AkBc6h5bWWWrsWNtLebIPj4HVwEk2veLTqqDp41Yg8XrkAHhIaWYOttCPdddhAJ/Jtdk6BTdSUKrSNUBVwey6RRCpGYvqYEl/EKXM/Tzw0a3nurUSrwz/Vrb52'
        b'1/SHNZemXFsWG6bcYmq9j7fL5WhS8bahK+YvP9zG/OjL2b9u3vRC52ubVsy7s+iNtyZMTZtz+fv472/e/Oatb9r/tdjKh/vd2y0lV//O4Fd2t/ITfIoOvlvKftP2l+Lg'
        b'z458aHTmzbKQb5fULJp4ayDWqPC9rH98oPjlmwlU950Pf53tUpRVe7P1b/Wv1O398y9uhbuXFVstinvDddqG3Rderfgi5puz8z8P2nt03rxzgdE96VfjtllRX70uq4g4'
        b't92m/fTF7fPsJIr7s85bVVR2hazfvZQ/f+hC+8OizHN/Tsw9bb16osuW01a3L+R1eHpx2Ufge7xf570uvLewdm9Cw7TKtDXML3rnSr6N/1f2CPPGlfwFf3YZXPP2q2ui'
        b'z6x4KWKWKrts78bMKyKvoHWDrrO8g75hdzYIVBbLZMaisvaUVRdurV61tI7zt6mf3H3/YebX4V2HdndtUa29FBmzS1jdt3z8zkkF7x8bMC0K+Fn2a6T3DXfvyUdvrrtk'
        b'P6KeFZD9eSxn/19nRInPRny3tvTzptdf3fr6q60Hm6d95/ZtbtbXh/N/+XJjVUtt/2sumpLrE+Tt2V+IThZ9kdmyas7Z62LR0brscwMR69P8Fi+b9PWGJB+XB8uUgwmz'
        b'+huvBH71yZt/XRc0a4FF2/rjh9f/beTI2S/LX/nr56dlAvkPJ/wWvVk/O/L+vF86ou0eJK5qKVrsPTt6RBR3P1hxZ+WLp6aob0Z59qmP5wy+fmV9WD947t45909fnvSV'
        b'rOHF9PGf1Z0xDu0taTr7ysEFTm+vO1/wl4Of71j+SUnAqUsrNPPnxv5Y9xmv7KeQk0kT5705u62mM94m535C7PtdJ7d9OFj6/CZB0T/Xr/G5vc32F/OJST1fu9u9/9Eb'
        b'P4XfOz2JN8/zPMs83OFhQHG9hefKfat7Uj892TRk6+y/4Jujf7JtvuB5rePvXM/v34RxdzscHk75smbtxF/v7lq5WHCI+enuxPxvyjm5HzXI/irZ9ukvLxjP+ulfvHUm'
        b'sxL76h4sDm79+w6PqZf/XPplzE9z59o5XbnCce2LfLD7uWUfGlkuT+hw6hl8ZbzlmQvmsg25/8ge0gS+dmUe9+8btgf2fO3yjd28Tf9ivLzqivPWA4IQWrOzm79MONb+'
        b'bJPOSgC7gQKcBxeJemUxGJw9ysqcigsF52APMfDE2eRn6szhueQJa7iThUjeDrBbGEEqQNt6k5/OBgS7wXED3RG4bkm0T+XgDLicCRWeo7BxTNgDpWAPKcIYdhuBpscc'
        b'9CaAHrAP3JhN7EhFEtAr1Gme/EzAIdg6m1ZLbc9crYfRN6nG/oPz4Qk648uNOtBi4ECI2PCWMboncJlObbDLnjUG5/TIpI1M73VlpHxLsN1ImJMN93ApdhRj8XrEhO2A'
        b'7bTv4h6TZTqXSK4IHMV6qTnwOK1wk8NW37FJ+Q5HgP58uIPouxCfNBg9mhkAHp1UyPQBcnCN1BlfGJMpBGdQW7kU1wHuWsv0nQ3qabNZ27QYg2QJJFXCUouN8Cq8otXS'
        b'zZw6astDWws44wBvkCZZGAFp5hgH0MNgG+iajN4kvbAbtqTgdD2hRkhuOcIA9QEFcABeIt1fAaQFtImCzWZE4mQKEmMydgEJYCdsCkIMKXoR7soOQmxJKGsRGIIHwTnQ'
        b'T5dcXzgrk7lpjLEPnqldQjdYuZ7wYFoLIeJ1wvPAZtK/FbVxhuw3UNiAdnCmkJRpDa7DTgMmm4tY8CPZoIH07gRj0J3psuwRJhvI6BkTAVvgdQMue9IKcHldOG3Q3AJb'
        b'wwxYbMR9X6J5bNgKTtG4tpY+hjz2fjgAZIlBP+AA48BKk6dx2BDxc5wl4BRQEAdQDjwJu3AxtHmTMwM0UpZwM6sayLSAYFmIZxrCyRpCczHsrwju38gM9Mv7wR+/DbY5'
        b'YsZMiQaTMGeIM1sJL5jDPkYEqGcEoaqM/SE9XxzBcY9M/dDwYBvq+SjEHu6Ep2lL1EXQVKTNRwka3WB9aDo4HcCgXFPZaI1d0o7gGthZTnJ7jEcLhzKCXUxBPK8KttEm'
        b'3h3wIryAdvdwcJns7mBHEh112Q06Y7SgYFoYdlsf1mq0gvZ6WNJurh1lbPqBkGy0HBvhLiQ5oMqhjA060BI6SJfTCA4Ek8dyg4IDl6Aua0AUxnE8e7IR3EOw62LWIemV'
        b'lJMTnIakl33YVxitDj80R5rhZU4hUC4l3VEOt0RlJuTi5uyiB8cU7GHCLmNtopBcRGUIhl5jEOp10AzO5DDd0PANkIbkA1nqqJd0IBc0MLRO0t3gOdqz9xQcAiexb/Yc'
        b'y1VaNbox7GWC04iDJTUsQwPbgwYkWBCAp1AZExyLA+cQoRJ4PRvQsv/ygVgNn5z/8tEwwDumopKSp9raDe4RDbsfh7ZGblxA0JoTWhMUZdogUwKVFn12Yu/EobwbC58v'
        b'GJmU92qpbPJ7rgXENTft1ei3J742USWYpfaYPew029AlWWdet3VT2Qb05vU5n1w0JFIHT6Y9hNUuscN2sRpbx+b4285eCt+ekK6QPt9bztFDERo6k2D72s5N8k1qz7AR'
        b'z4kqz4lqz0ky9m0vX0W+0qtr9lE3Gfe2t19XsdJXubLX/2hl3wzVuAlq7+gR70kq70lDS9TeU2Vs2Qy5EdbL43QejA4TvYq+x7nLWRl11POWU7j22uhNG3zzqOstp+AH'
        b'lpRLzD0rys0DGw0UUUqG0ksRq3YNlqZ8bOson6ioUbsGqW2DyAdNU7ukDdul3Xb0GWuh0IJPJzQnKHxHbP1Vtv6PWSg0Dh6tlc2VLVVS1sdufI2H/4jHFGXy2bTetJMZ'
        b'I0GJqqBEddCUEY+M50s0XoEaVw8MXBYvjx9xFapchRpP784N8g3tmzR8nx7zLvOjlhq+r8bD52O+L84eOcIPV/HDMUbcevn6Ec9QlWeoZswdH/+e+K74EZ9olU/02Du+'
        b'AThBx4hvrMo3VuM9jvafGK/yHq8RBJ9163UbESSrBMn3rY29HO45UF4B+FWN57jOdfJ1Gr4/OfMJ7JncNVl35isc8Y1S+UZpvAV4tDWCsBFBgkqQgIrwdLgv8HCykbLv'
        b'JVBefqONkJqjGdIa3xw/YhuM/q8Jixo06zcbCcu4FZbxevaw7zxp9m0ffyX7rFmv2UhAvCogXu0zadiKr4mKGczqzxqJSrsVlTacMW94/kJ1xqJh/8XonsJGZeV728sP'
        b'zfHqrmq11wSphSYidjD0fOjzCcMz89XJBcN+s6QWMrHKyvtjXfdEqnwiNX4RmoCgs8a9xsMRU9QByajvNEGRI0FJqqCkkaAZz89+ZcELC/A3ozd0aSwt1OMm6y6hzxZ2'
        b'CUe8J/TZa7x87tubOthImT85UXbumsgJg/H98c+bvBeZ+frc4XGzpVOk65pzbzu4tCyRsrANaoOsdsQxRMnFZidHPAHi5HHt8dIUjaPrLZ+ovnyVT5zaMY6sydRX7VSC'
        b'bLVHzrBTzj0W5TTxHpdy8yEBAEyl9bCrcMQ1XOUarnaNfPR1NE1k7A8cA5R2KlRXjYo2sZFsKy3rtWlY9q9TOQYoZqIDuuDk2mkpt1SylcuGIobEaqcpUo7GyrbVpNlE'
        b'FqWIUNqete+177PpdemTDJVITVRWyfiuebO5rFSRJC+/ZeWPzy2bLRXsW1Z++LdFs4Wshp6qYSrPsFtW4ejqiJWXygqRCPy8g1NrWXNZa3VztaJE7SDEnUObADc0b1Dk'
        b'jTgKVI6Ce0y2vTdezqZyU0XyLacAnIvXjm7VLSsc4S41fbCJiRb3e87RD39YxUTd8z3FRO/QhAevJ2XeiGe4yjNc4+Z1n0XxI+6x0P2fJYSvj52SMNedpYm1nhtK3XY3'
        b'mRtkdDtUOM+ddceNgY66KHNiutPbysTXsCVObyUTX/+P8POeuCtgOaKQ/t/Y/YA2Ad7HNX2HDruwCRB77/66mXowYwGDwZjCeEDh40/k+EeiELCpUcmNoYZMk1gsAesO'
        b'T+eAMRo5X8ymRv+n1/LvQocEK50JkHiLGGkNgKZaAyCTmACxAZAikbisAvsoW635j51vYMyr4niM8RIp4Iwx9LGTOMT899hVQ69p0QCDokwKVmhDFsZa/4jdTKS1I+l9'
        b'TEZtbrorY0NCa7QmLoNXgrSWrmJRFTG3FGHLIp8kqsamklE74n9iksNGSlJqoK66QD4J+yTWHF09tK2MrhIbJlFTqmj7FW0u4ydXl5RGxvKLRGJiL6IbLC5dIS6VlJKy'
        b'ftsXhnyw1vr4KMbgk8yIqDhSsc4IpjPhYavao1alf2dDehy+3jOnNgYvVcwdt2bCxtwQuAcJksIZencY2hcms9LQG2avwBieBR1gO3GkMS0CNwytNmnpQaBrQ3oBbMjN'
        b'G2PBqYM9xkjkuAz7iTI93xVuExIdezu8iD1poIy2Dam8TSg7DFtvW5iVVJ1MhzHU/319XskDXQpOSv59bRpF0qwcLRECJRaeG+C+PGxzARfA1uwswmDPfsRh/1GtJKvA'
        b'HPHF++HuWkwh5iXYwwEGuCaiqGwqe206DRvzT+ZDyirjBJMKKyx1ijibS+sTNfLEfHJ7tsc86oPEz5hU4ealQzXmjvTt1COJ5K772qWMW0zK6e3QwonfrNtIkXqgwig2'
        b'kj2fheQ8KmI12F+LiY1/LdxuaECDDZRPcEY2bMGWIyQkpmstciQzbeaMtIygDBolGQ7CfeYZoUBONLKhy5BU8rhT0yMeTcK1Wp8m0GOmBZgPHg9lunxUQAoOGeSkqkfT'
        b'YzuxRjg7g1MGlpV8VJqcuQ7sSqzFbnBm8MDjDlU6I5Z2JmRDWTWqewu4brwB3ADdpJdMzYkhzuo9y8LKgsx1Wt1t4lK6D39YNos6n/UJurC5ThY/LVb8HsY0wXcEHNoq'
        b'cxa0Ajk4SRXh3IlrqbXwMovobkOg1BYJfdUhtMzXCjrp/j9dWSk02rieaHRdYTOt/+0Ee4NhE2VdTTS66Msuk0/OmIVmUhO85krCKJq4FHsCA5yF9UHEAAMuGIEjBhYY'
        b'J6ikLTDBnkTTHWmCQ8OjTTJHUwbAdmGFubiFKfFAe97lFSv35L9RpU60u7bxlZUeq2b6Z9u2RHHs2bf9mhxecJjFf/PQDO/+XfmX32gwt/F8fsek9ZzMjfVvf7rXdd/y'
        b'l8+/ONPt4eF1b23oeO2rTyw/LuZ+sTP2i4ke1aeuLM7dV11VR3le9d7rsG92QuKWn8vvZ/nYvv5t//MlH7p9u/PrXxo6g7xStpT9U/Xyma++nn9gw4kizgOviUUPuRPG'
        b'Vb4MHh4I+PbuvDM3bHPzv3rzTM147z85HZpym2vMnFPyXdf8kq7VvzgkzuP9NTDCse/CD9s25n248Jdjt660vXJWuXruR/mBq32WiwaOdT2n2OEka3g7/92e8ReP+buZ'
        b'fe9stcuylb+g0rRs6vjTV8U33nlpepyT9d2Xcsy/LZw9xL37gsWfAq72DE51zs9eOmtg/tm/nSs6/NfXFkhf3hZVk//uhrTjoevfbPv81Gc7BD94dOTdmHHhmx1D5/Yd'
        b'yM5y+NuFA/6fP3egc/yhc8Ao4u+/5gXUG+WIgPpGziebu+0Lt20VTvzofrQKdM0WaUacc8x27M7+9cOjRVfyV//tT7/sXhVVLJfD4hOLr3TmtvY9nLk2x5P1bdD4gfPb'
        b'XvpinGn3X+/ETPXYWzL//OAZ8fsTHvTuTtn22QctP+Ru7om488tM1cTZNneK/jzu2/dmXb3SGfPCgHBTknu/qa0fKIqI/TQ9ubXCfOXt51Wg1yXmrVurzX85ZbwwOb46'
        b'ke03Jfu+26ID/1K8evra5tiXHO69vPHBdwcjd84X/vNno3dfXjFtskTgQJSfYJszHBBaWxp4zSU4EH3ZcnAF9hsozMJAJwmaPmpK64pOgnZr07EOc2ix7MKKzyXziRJn'
        b'MWxfo8VvAl1mbALfBJtiaK3JdaDYkDmfk64HfXILJgqmBH/YIQTN8MCon91yeJKoS6rmg4OPJrDGHvHnVhKneJtgoqwBO4A0EJOKztA0bAdipzHAQCjcRtQP45PA9aLZ'
        b'mcSUnhkciKHe21lMuDmc1tSddwPnhCvBidFEquBqOaQ1F2BHXoY+2SlljBbbDpztdE4KHYfdDraDBiFqEfki4xXwnDsT0bpuN9IVk2FvOclhBXZEY81KGzMY1kOZFu89'
        b'FOzQKxFTBHo1Ijxor30ENIPTQIGzgABlFq0jngDqKcsJrAWx4BTRRE51ciQqoMWmcF82ot9oixJyKVfQjhVZLRPo79tSg7WGqPOychfCIxyK68Zkw64ppI5V4CIY0Kmr'
        b'GHCHXmMF95aCI7S+qnMxiToCjbAJbMNKK0OFFbhqR/y2XRaD/Tp1lU5ZNQ5eG8+e7DWLKArBdtgP2oU5M22fqLLiFIIroJk0OHNm7KiuCG7LLWOCc6jIawLP/70m6OnC'
        b'AB6O39YP6RJ3GXo+3XF9NJzK4CZREb3EpFVElYUMyslF73RZPuIYqnIMJSqN5OfLVX45apfcYbvcu47uGnevznnyee0LmlNv23squErWiH2Qyj7otnugcoLaPUKaiuHJ'
        b'lqAibENVtqEadx/siNm+UJqqsXWWpXRmyDPas9S2AaTsRLVL0rBdEvblDFCk3LIXKGdqfTkV4e1xSkeVa5g0Gbt0Bn7h6HLXlU8C7maoPWYOO83UuHh2BsoDFXPULiHS'
        b'ZCQMu3p0CuVCRbHaJVCarPH170nrSmvOlk792N0bVe7oJqtpWY8VTbOUtX21vRtUfpPUXgkyrobvK+NovPzQL0d3Bbtlw22+j2KqsqBvVu8ilW+8mj9JdxsfcA94eHUu'
        b'lS9V+ik91B4xMtYXrp63AyL6Ik9ays1lbFnZXVdvjbdfT2BXoDLvaKgs+WMXd4OG3XV0JZ+eqXbJGrbLMpDDH9Mx/R4vWA+hMmUoReWR1GyKtVKOMl5rwuOaKC//Ea9w'
        b'lVe42itSypbOaba4a+ugsXNpzW3OVaQpS27ZRd62w5K4XfA9D8rJTWp635Vy9Wwfh/rRzpE8laRYqfS6ZRekQXeTNE7OslS5iaJA5RSIzhydZJEtqzVufBlD4+YuT1dy'
        b'VW4h6Dd6FecDLlbMUHopVw5Nkaar7Cbjq9nN2Qq/W3YBusJTcCpc9DunOUcRpTRR+UT2pap8Jt6yi0dXR+z8VHZ+CtRIIX4mozlDVnPLzpcW91cy0Nx4z17wM4GgB772'
        b'mcGsN4JNMuO1rrYOtLz+PZcyAH97NgL6E9cpLvlxiX1Uarc0wk+igwlqr2Qy5tex1F6IpPZALLTThz/ivQtYJEMn+biV+DPF3EeEdNwzRIxaj/dCYwMhnYWEdKY22Rkt'
        b'qFNYVI8y04vl3GcolmOozE/0MvloujN99AYJ8viDUUf0MzrMPvq5J4CHh/CTae9OUpXWC5UEJWFBHd1Kz8uNmRAWjgXn5aIa7OsoqRFXVJXpq6DBAEc9Nx8FQabv/9tg'
        b'SB4dzRFpDXv/vdzDgFeggpZ8yrxSaQ7+vA1oXoNNS3rwS+x+BY6Dfjq52glwGFyiPbBS4TU9rmaS1gcJHIRdpWA32DzGxUvr4HXNrGLzt68wJRjKofTnioHPMMjoiRet'
        b'gDVwHw2f9H9q+OQnw7rwyTwcPvnRe07A5ubnUMrLt71p9brTzVMWdj9G80Rb5K3K1563AhY14zN5oTe3r4i1ULg5plksWRSSycu0muhw44UPTC94bRM02qcw/xFUmCCx'
        b'8q9ayM4q4bQ/f/RFqxd4ki5mchyrLI6qv+NkcjVdwCH837gQuFVvqHVIRWxncro2lxCSCc/TiZxA9yKDqMsdiIfDjMoyJNNvFfNMnxCscQzxDYRR6YYHsN/kI4ZZcKQG'
        b'MVVgM5ATVjMG1M+hLb7gSjIx+hYUgXPPOHvO47u+RS1ZVfp93/2RfX/sbTrzO0WHX0wp+c/CLxx9Fflqx0C86bjKat+x9dX4C6UpMpd37Hzv2rvfdvRSBCiTRxzDVI5h'
        b't33C+pzUPnEynsY/dMQ/VuUfq/afiB9WITpu66yy9dP44ZedmnM0PkKsVD+aMOIzEW0Bap9JaMOap7LikySj71oJDKLnLA3iKPSk7z8k7hLLxyk3TbKdMMl2Roe1hiS7'
        b'ulhPsu/9UZL9EDeecceormIFVg/+jzG/cdRdhUmSuLi8YpUWV1Cb1mAMYiEiyMm0Tq9yLVH6VSxfUVmK1ZKlJV56Yq39pEfB9NDlJ+WnfJw8snNIyknYvxK2EacMyvQx'
        b'1cyof3GRI6+iFrZXbFj1IVuShN4z/+EsDUhuJfgaEax6WfhLU2RZzl5B5so0b09WcpQwK0EWvi29dc8WRnfgwfA293Flr1O2n92kqKKb3Pi29wVssoy9w1IwJdkCTo0G'
        b'fjWvIjLbZEQ8Gw1kWLB/IZZhTacSUrOcDY89KsEOrCOeO4d9CTSG+yZ4Aw5gCnJiOeyHu4NhQzqtxEzPXql9JxOcNAJ96POP/Jvc21Yieth0K1uih0nX24QfeYCs/Sh6'
        b'7d9LLGVQdg56Q6Y/DRlMA089769f6x84CNQOwmEr4eNA6i5GT15xjwGpe+EHvdFBbmYApF5dglaR6x+GDWaLP2XgOKXFxUvKFuN5JZbilS9iaVsnfpuBtW05OfmpOWKM'
        b'fCOw+T3owKOIUAQSggR9k7hbEm5FDC6EfyMUgXwQAf11/t+Khs7UI4DBj3Odq7naA8YplZTrwIONza2+c8DgwT5dq1XmoQ+Y7ubFjHsUPmLo4LB75ML9BB1ycDpGDs5k'
        b'EOhgLQYwBup1jG2Y9oBnaR51n/8ILO+n5nZyH5W5xwOmubknLtLzHv71nQepFN34gcmjYYrRDfTrOzu6NRKVufAB08nc7T6FDvh+0D18+l0Uvj+7N/KSz21Pn167/uT7'
        b'LIZF7MeJKZr4xAes9QxztwcUPt4nx+856OY9Nv753XoWfrW4l9Wfd8nuUvlw1DSVedoDZi55BR9/JEdcVzrjHrn+3QLyjk+vbW9+f8BwwMQXUlTm6Q+YDuaBP1HogJ/N'
        b'QM+in98l4CfzVOZePzJNzIPwHe/v8S86epbwDwMhUXCAcHyuk4LS4QX8Mwu7IgX4c1YZw45ajDhUDi5bgENg/6Rq2B5mBXbAQXjFPnoC2FwMz3LjYANoBvt5oBEegvWe'
        b'5kAKtwMFOAVaUlLAEVOwH+xiuMLrYBBeNwfyOHge7AXnROAC7M03Z8IzYCs8OykeXAd9aeD6NPTUPrhrLRgEveBUyHpwNAuciV8Pr8EeI9gHTqD/Lo9HXOVR2F22MsIP'
        b'ysPhZthVBQ7DbYhzPQfb108CiJmCjaDfcdrK+FwH0OQDNydvWBoJ98BrYLAiHu5YNs3FU+SSGpfJmRuxLiQXHJ3rFgxa4IV4cAn2gAEgrQInYDMq5mIauBi7PBDui1gM'
        b'd5vD7hLYZ4s4WAXYD4+g/67A5wqTYdv0yKVgTzE8zUUc7kW4oxr0w+ZqcAUezoOnQd/q5YhVu74Bnbfmg2ZneGTZfPgcOBZtD8+kgSthiGpvRXXttU4BZ/PAVv9M1IaL'
        b'sC0GnN0AT84AcgbsBm2wHh4AHejvvnKgxJ7mqz1YpuAA4h07I4LgUXixPMYkHl4AO4vdwOZpy8G2ElRsaza4KihOrfZMhXsr4HXYngEPznUCp9ckwSFwDo1U3yQukM0Q'
        b'FKBPbwIHwXaTcflwwAl2wSPobDAb7AQdc1B/HAStQXAwJsFvkq+dLTw3C13oWOc/X4iYzhNWtnAnlIIL+RJ0tdnCxBvtIT2o8/rBWdScPgq2RpZOhPIFoD0CXLWBnRZF'
        b'2WBvWU0C3DwTtnqApsUTePAGGHKzBUOV4IYr2FGGXj+1AjZCWbgbPFLiPWvepFDYgqbCEOiWiNCsew625Zs5L6irmrgOnndb6A7acsAR5/nEjtYKlTz0MefRlGqDRxLh'
        b'bh7YORVeDkMj+Rw4GYu+8hTEWZm3zkEjsC94MpoRu9aAc46ucBfqHyTSWGxkwauwcZpvXn7tHiZWksLrc8GhmUlgL5r2Zjgppf36RDS+PVPBZg/QAWXBZlHwDBqefnCY'
        b'NRV0F4t8BEBazgZN/E2h4HhMbV25JTyIJuMRqEQdu3tF4WxwzX4OaEsEbaAfHANbRbAjELYKx8EheBkMskBfQpIxPOAKL4o4K+AhcL5g7urJsH1DXiU4iWSBFnAtAH0G'
        b'miDwdFXmRFTIYTfQDrdMn4NK3z8HtEYDGdhZhBbfFmZsNtwP+oLRM+egEpzYMH+DrdWcTUVR08pgh/XaKGt4Gn1rE5rMW9G6qB+PFlbjNM8s37Xj0FzbB+TwVDia5ifR'
        b'3ByCDSK4vxJcRV81FV4BjUbweALcvw501mYmVcDT/nBnABIPb6yPDtkEdiwyzgNDTh4Y/hb2WMewq+GNQniOCaVrHERT4TYwYAJ2b0wDMrjFbRrYOxcJfNtLLEEnUObm'
        b'FUQU24xzhr1J00zsbELCOK6RBWgFHcqCDXlofGXwhBNoQFRlswh2T0ADeQXUw+0suD8HNMN+PuzIgbvmIDFzgG2N5t4uR3AEfQYmTNsXR+C+BQ3wFDi/eo0z2OOB6juN'
        b'ppRyDZoNO+useWg1DCxBctSl9RF2oAX14TY0On2IcF3glVlkwE5ncAYq5s2CJ9Gi2w4HPReCa9mZ4AboMfYF+yWIJHSDHbGlcGA5bJwDroW4YK39glww6Ipm3Em4ZybY'
        b'n5lhvWA1vIDq60ZT4fB8sAWtnxvos7ZEwJO2/nm+ODIMdfiFufB4Jeo6ZS4Sz+AQB8iKfEEXKmZb7bt4Rv6/8r4EKsrsWreKKuYZmQcFRwZBBRVQQRCZJ0WRQZQZAZGh'
        b'AEUUBZEZGZVZRCZlkllmub13ctM36dtP0+l0N92dzuvcJDc3w8N0EjP16/f9hZ3k9UvusNZbK2+th65Tf1Wd//z/2Wfvb3/71H/2mdvLQ9BIN6oXNBL3vWBHM/mu3BUj'
        b'Rbs9fDsznnpy1GGWrQdO7KZBnbhAGnKnWn4KaS1zqxn06BlVo2tTNO5P5WdhrWVbecXP3d2N2wKoL0lHjcugsQPQqDm6vY06LC9DhVsV3Gn5quiggz83X8yzEx6UpEGw'
        b'zWpahOU0weQ6E86eywR29O7mznSIe0kERaqGpg5TH7Xw3RhvbuRVO6OIvHPnqScYd9jPDTxjDdtoPLrVsYBr9VVp4S/1FfbRcsIE9zF7hUvtVW/STKYcLu9qXaV24OSg'
        b'Z9DBQqtEmgi5dt1Qct6XaoyoJAUdW0UDg8Cl0oPu0N425Ut0hx7FUrMmhnjIUpOaXbjdj3ryUKWEhZ484G74pEdUrK3ApW4w+wEDZZpz4UXjnVCGKVp05Gf6V7gv0+Cq'
        b'NDWDi+ke7LWc72pDUP3o3iAv0/QJjGavLldHWaRC10p50oP6IfLlmF3wTE+iCsyF34YuuXFDHPxXqw0NXYE51DpgKHo9HQFxVdBK+M2Y/RcPcKN1Oj8uOqZViBssRRRf'
        b'D22e3mdpnRRP04CbOQ19buZFLtXgSh/qdjwNfaCHV3EDVVxvTbPQmBGqL+ReZbPtEPIS9/tE7aFn3KXmY4sOlwMfe+C0O4/TtO+FMAzkNN3KjRJ+hoY7fEBLhVxzmdrO'
        b'KSdzi1uKr4PcodcH5sHVlOcDERrk+WpuU8sRX6NIbqXOi1StcNmYuqDhkCI0nLqj03Gnq/xAsiMrwIerMjW5MTlC2eI8j5lSq6Bde2DRvT66NG+T/10F+RKqx64C1mbK'
        b'GcYyj9vxU7H35jjqUeb2MDUxTQoroupgNm3UkMddiIKmRMDc7QZcvA9ybjO/xk+UaZH6k32tqcOLRjbBI3SY4JQ6Le5SvmSeDt3p0IYttTna8LNwBz/qPHmN75pTbcBm'
        b'ZziDOTWI6BnXKJ+goTjBZOLF2TECIbqfyeO8dC4CoCFg8CjQADQk6yB1bvKwC9Pj8ShqjDtOt7xpUYd7fG+ehXx6nK9totpTQVE0tINnblp4xQE9hjEsI5cgmBHqPHtV'
        b'zC0+TrRweu81LS/0ppPa3BPhm29hrHuNdSH0cu6X0KouN4Ub6ZjC+VXrU8O5oPjTsN8Vp5OHMmDJzZHU7EClQfp79PlxBo16wAIr0+nuTr7lJeZixRO0mHSM7vmk0bR7'
        b'CC1R5TFXL+8bptwOEwA2DuB6FaJL8AK9PKlEPbCFKkPYzBREVc9djrRCtSZCpuUdtFTET3Pcobpt8HZ13HIkh3s9hc2Zk04WULlvFsygp4haigygGrNJV3nogjG3AQgf'
        b'AiuqD/OdCN2DDK1v4H5fUCPo9YClM+7hPo76PJwLfHXgGY+b0vQpKOMczVzdD8Nf4WEvroXYyuD1HjhvFliZjGpTLHcJCsmN+kflgNCL2yym7jRqSdAtvBzMXbjKDPSz'
        b'lZrScDdDIAWlClSXD8HXmlxD9zrhQkfgOXMj6aEDd3O/cajmKTiLR+mG/DCZ7/ljfAd5KYbux+EWn7gjzO7nSle6zYKtr3BLOJqoOJ96WXBDXHLJhKezgTFTXLbdJ1qN'
        b'J8z2+Zy0QHsr+Q0CaEMrJqHa6MOfeIQdz4svcR14hJuLHc3tpYnL6rtclWWgsW0+Z7jpGPpCPZ4Y4RVceloGKT0VgChyK5U7cem+eLqPa1fTRPY1N43NgbTC4wn8QFgE'
        b'AgxpvbmFiu3OYLjnpS5AwxZasD14lEfOgaXd44VkIcE0PNkwnPQsA9tKb9rzXUsVPaht5bFz1BPALWEe8K8NyR7UHm4L4tFPS4dwvTpQkh5a1oaB36eHOjzkR3X7CrhJ'
        b'K3jLhUuAvBJlGEj3NbVYmthx6HiQsZsmdGyU7mnZW0ghtvtqeq48s2WnisSHb1lBksU7oPcDumZw83XCIocYLj1Hdz0JAOUOZwiMAk3gxVhYe/fhHODWPXoEj9IPuj+B'
        b'gRKfsD9DNTsy4aw7aTSUS6O5N+YQVQftDobgSqnKK90s1PekQGSqz92gwQQbvpVIxZuuWXIrfFbjWX4qg/K0nOSROK6030utCtC0B0Fc4Qn9WgW4j104h8CkAQBeZWIM'
        b'Ic/EcfNhrqAHWS4Q/mNHKnfHMPdz474o/ZSDrqEJ1B/H81kxQOeew9pqO5yc9U2cbADtMxpctel4yC54xNUd1BWOVps0oVvPLlF12BkYyWIM9eykQf0knszEBTvRzfvn'
        b'YQoDZ5MNgD5NNOZA4+oQZjW3XqCqLTR1Lvu80VEazkClMWpPAT60S9JxV8WnoPEzTlTvRiu74HMX+PZNfX4myuBOO26JprtyvD1FfbqCTpZkylVyBSpZwCPJ/PiqCphP'
        b'6aZrkF/JTguQ3BnzvXrcrAMuGRFW6EcNN7fsuJZP5fHGJ2I1wuDE+4R/VHoA2N8CGMFpbgJzuq6jSaMFGNfFvLP84MxRdbjMp7SqHccD3J4Ol/tIkYvz+d7pZFq5lomv'
        b'OhPOgc88kVMIAoVYopU0aP90gjGXybbwgDXUohe2M3I6kxuvWwIeugTGm4pbqDx/6JKxuvBbOqCjBeKoCY4C2xsuOlUUkVqwVSOEQVr7eGArkPtRjHuBFgsZ2wXbbaD5'
        b'zGx3PXqqnQczKZGBVjREhjipbueJhBC+RS2nUOUp3VbmYc1krjxpJzyTcYsqsqlDG7HKbeou4KlYaOrEHg27AOBTe5qOT/pVd0RPvRaw0XFhbY+ZtRTSvLcXlLPBSJ/u'
        b'Zlpu8Yaxjlrwgi+A6w4ClBm45cVMYfUeN+Xs4MFtiHCH+XYRdVjbA//mlXGxUh508k12KrCKSYGZl8AYSvNhBx1q1LSP6y46cWfQDpjC9Cbd3ATg3zIPR/PwOVhNvxU0'
        b'sMsZvGXOiSp4PjuT+vIQhlciXDbaqw+8bD0KkJ8+vA233ZBKd0AcFPlxOFxlpbCUzv0iz4abcJmU7vJ4Mq57H8rWIdp2xS07OtfwhPAo4lZbWMt9akzKoy73AqrexlWK'
        b'MVyTTu1HUHeKZsA7W7nqDLxEDdhJl36QFj0I2HkzFAo6yk8KozLAFltPuXs7C8HZiCsNeMpsY2gOSlUfTJPX0vRTgD/t2tDvGXvuO3ndl5t9bKERT4y2csmeoPRwrjvA'
        b'dTZKG4+yFfMU9wVyWYa/oki8R8TVVrvkq/VtqDUnEKjy5Mtl03epVkd+CnjenFXg8Vg7BZHYQyRY5uv9OeieTC/QMs5eSSQ+Kiz2m6Q+eQYHGGKlJgKoQSHthFgkDhDB'
        b'JwzQsry1ACh7n7BobXC3WJ7frDt8f76fRFjjP4r+3YdHugPT6PDQgNzHb6htOatKLYfDtOM3wTM1OkAdeiGpewJr38m3/X2CqTzd3dAGWDPHAyaFcE8Pqdtfx/MsALyB'
        b'uhK4HnwFNswPDgrzLgi/Gwsc8r1o2FAge0U0kBzPFer0UBYPs2mmVXcqjjjJ90IwlvgeuN9nymXeeNdPj0TA2IpwPRC5zj0YtfuO0duhfCUWCAsmbaPQdL0oFJctSwas'
        b'jsMLN2O4EeqkXadyB3jYxtPUsBMRwxSUIhoUpnEnhDlGTa6Il8ryYoPpWSA0vh+OogYynjKHAEsRn1W62lynCifwt0XIbgIeoYcmrECLH1O7S7LLZQnXKydrc5vfRRo6'
        b'yPMyuy28cJ5Hov0NaEj5en5ysCyWhW0u+lWF2QNqMzfhEsh2BIhUAoQcjIlGW7UQaUuUfjrsdgG30HAAXR10M1WL0ODuxDh5ANYh4VJHhDPFEMwYA0tXHalWwhNRtqGO'
        b'XBYpbJhxmCd2wnYeOdmRsOxziBoOQyvq0Z9imVG+FM6pIRd96KeV42fBJ5up2pa6lXk0jRv86N5R7glHZFUrrAFVNuCaOKtEGy8zHlWhe3HQNdjKio1WPg8lymQ8iH9N'
        b'RZq43aqDZyIRSo4BjxudeMrL97puShLNWmvSUy1+4AfbuuXMY3v8Yd5DVM7C/E6VNqL4GSoxpa5YQAG1HPWLDjkri4g2AieqhCdfMHLhu7I9TsCKqcsSQMQAjdob0mp+'
        b'Ko84IyhosN3EHUYClsPjVey9CUOdPQDCWCXMSNmEpMCj0twe6syDTlXQ3FmqyIQT76fh41DxscCbNBaLwK8bQzoWcEg+CbMsgaN5cPYCjG2A6p2NzG7YgXrOhEABW7gx'
        b'hZa4dy+KVV6xNKSW5NzdecbgXCPuPH9ek0s0eVlM3edBr2/Z5Q8pCIsVm2HAX5mfge0/cbf00L7Mo4ZKplf4YRKMoyQB0Dx54ixXB+gbeiKAWaVWGWRZrq6vGB0bFIZm'
        b'GpxMoTctNB7ODSY8uM840OoITV9DSFARaRxqn+ipDNc2f/KMfK5mKnQLrtNBzQchlGU1dGIqE9DUC7+ykspP8+mpDY1TzRE7mMYgd2XiTf3l/dQBxwaMbxBUtY8mbenJ'
        b'3izw/e5DPJV0FoIuDz5jJBBOBlgPRIhB+pZh1yXmsJ9JX/i5bqk5P7ID/E5z36Yz9HgrsLWOOj1kQaDa3RdAQEs9BIidpJKiDHB8Mw+gVJ+JtjDBFcSPCvW81Gj40jmg'
        b'ce3GdEBuIiyg4eIO3BacGj+8ATBYMIch3Ee0S4+Cz4vSueJYBlCn6/yxC/AO09yVjDtsyoMrLsUZwsPW9xOTaDzjhDPPGOnQs23RUIY2fR7wdBAkYstDRsm8kAa9Eaj+'
        b'MMKHZRmvnFc8osPtZvu4KTQbqFa7iXv1EII1XwOZKqbVHBCemaM0pBtqfdRpOxxwD9+LUuGHvlkQeqf1rvzNNmmGJ3z1dLln0838Q5pUfkwhBDo/DAWsosEbAIKH+Wf8'
        b'qOYskPaWHc3rJ8Msl2EXT4siLsFfZlKdhCfxfhRMbyH+MvC2y+16JA9E2QOVOnjEhpaOnaexLTv8AQrNwgBjEJ4B19oBDmO66MYKr944EYRG+w9Q0yUD31Bce9EM8ljy'
        b'onlPgHBFrOLWo3nCdGj+d6CtR5wAKfdPcc2fItwIXP0Ote7fIgS5UWHqYprV48oQGleyp7GzSoY0xIDAmQPQgnHXM7xC1Q5prlDRRvnUyfBWe6CYMFXXrrubygBqUNBy'
        b'mkB4wM+uhNrbYLhGeNndk4bMqV3b3BTCr6WZJFhr39EjIhoyAa4M76B2Vy62AtZN0WgkPwinTscowE6FP3UlRcEjjJ8ROEovP4yS7VKUpB7hlj08UMBVDjS17TSXZu6l'
        b'/vRj8Ar96PEj+MIuHwAOLQRx9e4o+I1OW5jzbXuriFQecDaIlvGzEChbCzxH2X59FXqQnkkTQK9uXGEiRBk2sJodiri9EfpSS/2F6DTclSkP7qF7+fAmrSHp0CbItHW3'
        b'ZiaVqVke4jHXNG4LMLxEyzSUz52utOgp41bIrp4nzmym1dMiF76tqcKrEtxlebABLSgKUyR9rjR4wdCPWrzNTF0RdlWjSzx2GCi+DJUYhw3MQQ9WchB/jm6C0NsTEgW7'
        b'SUm1BqjeUYjxvJCjQbNneTA9NCQt5TyY6pQWbqEDDndEjacCqSaRWs/YGRFijFt8J10jnkdPU/0mj7hz17g7INhiHzfu5UmL1Biuc1IQmCtAqAxx9ANeDiq4jt7XJOjA'
        b'cz2MucrPNkt3UMumMC5PjPQ9fyzYBxZe68b3cl2SeGEr8OgJBrUG0aFSLMBhVD3KXA4wAm7fhSjbEvfTJM9utYHltnHfVRhcHU1YIwSq0VWGexzOjjTAZWuSeOVEDkbn'
        b'jrDxUIMqPdU77ABE67666ab2LlhXO+Dm2W6ujKVu50swytLj+cfAaRRs4Kv/UrER3T6VKBjxY2700JZRv75S+i5hMQR6Mwk4bNknDjjtL8RPiTyfyNOasKtZIXnN7sNa'
        b'3GAebSGFhnfAedeCw48WQtz39p9WDacnB7kjEsrdAeBeVBdichoxD4e8EVdTnSGXnfIRqM8mNDYWu4UGHHnM25ZBZgIsIKCarfTAYQvM894R6jSAZDpz4XQeJdNkpDnU'
        b'vEMhbL8Z9Zm4UnECVe0B/XUDGG4JtzEDTDSlcqkqTSbLbsJvldJM1EH4lOlkAcFrlPNOONGQhjMkXM/txrGQ0YIe914w4Ccq1oWeR3KM6L4zjQddh1YNwPH1c7sJP80L'
        b'4CE90Jx6+NClVDiCQjUvGYawG400bXXJo/7D0n08dnQ7PXZX4648HtVJOWdMg7o6OdRswLWBF9BQCd3drewYjOEEy4BY5qWWwdkezmHp/GQrgGEINtQVt5VXfQBdrXTf'
        b'39NNBMOohlWCgQfpArqa6Kl6ClccgHuGktZ40YSpqhhYMBcbA9gbwKDMo90yXYMIePE71KdCt1Op3JWH7IH/lTcuU5NLDAuT5b0imj5/2AyIskjlabuEfErG9NAeZt4O'
        b'o5hAWN0Vp2pygJeMqPW0S2C2L9znY3rMY1KccoumLfVdEXb00aAnDSuaw5i6aHWHgQnI7B1bbrjODYJwqq7QlCR752F82niEendF8AL8JLfobj+ynbtdqC05EppTyS0y'
        b'+KWVgrM8vv9IOJVm5AEY7zqIDtJgfIF+QgLknpHKS3QngSZyQJ8bwd7uQF6Th4CrZdtdERYucIXsUGCKG3Cgkquv2UO8Uxpi6N6whsCLMZTtSbkFRTQfird91BGEEP0B'
        b'jWf78ZMIuVec4aUjZ92p1Roec5Ef+LrxTADY27h60j7QuLYo2MaqcgK4WvFWrkjOV5AIG7sNwJnDjkqgzoIhrfCSHZC4Ddr51JVnjEF0I7lZLc2LRrZzp9ceapTAu/Vo'
        b'CjXcdNIQMS5fu+DnBypQGhDuasnlhVkg1yv8yBPjP0UPVHn5oHIGfM6ImB+e4sUdRVSM2O/eTh9t9VPckiT/eW1MmOy/eY3u0qIwpdVHC2HoIsxkUJgtAssdoEE/Q26/'
        b'GrYreg86d4+Hj3DJTa7jWXN4xsoYehAOrjVrr5Sa5WhME35qsPtRVLzjCLmWZ8AGVrS55xyVgQ1MwLPU7eMGkZKZMno5oGrPT66nggGWJxTQbTc45TrqkfCUsSp3njH2'
        b'MYbCjFor6ljw/NFwatDyUAFsLnKxL8jMiABpB/iJCO77Htfv1Uo+QWVnA61d8tLVeEUnonAXEB6k3P3SCarP5mbHUwirBRo67Zp6HfpRtYsmdA8FwoofGtGiGj2NvJph'
        b'y493ALfmENiVnefFAjUu9z4FuyhDUPIYqNOIgMUK4m7dzPc11CQpRlwTnZ52LtaJOwK1xN6GOG+MGpWoSdcIFtdMc+ka/nZ7+OlmYfYTfruYlk1pTvgF75G5BWK+2oSj'
        b'biDv3fshi4f0xMI+kxqDtsEq6hD35OZT+36MQrk/zx5RB31fAi3o8i404l6NG4roQZMPdWxSvQ6Da8K7Rlq1y4y7St1WiChL9VxCadaYunSc3TSu8K0ALjOPVeZHp6kp'
        b'lbppBGpUFxYlzJjyo3xhwgsjvwTwnYCLKOV+B668EWsFLw0GdAZ174egM7ci+GmhA2gZDcBcmuGoK9WjEvKjocUPSHAlYKP9B9G31SK6u5mbksG5Z3OgL2NXjKFWI0Vc'
        b'cZOqAOQgHrciqRUMPV/YbesE3dn+JyvwEGam6iPgg4Fg6Uctw7S3cwMsIGL7NXzdZXIhUdWY+01ctmNwV/nJBRpV9ovDNZ6CHw0oHOSnZrTKj5zT1dGhMu7JI+E34JLo'
        b'I9QkpRZjQPnyFSFpYK8Eh4O0mAxf81hIsVMPY7qLoWhU28x9AUDSEUi+lpuu8yotHdHnqoO0ZM+924O5JkP4rctfmKhKOgHZlO0EolRpSHk42RR6P3PVEka+sC80C+rW'
        b'v8kR99a015Bbtm2x4c6d3qALsA0v6MKKfirPanDHYSse0ETMWBZDpV5CWsgR1QKASzO4j7CnY58ICr+oRPfN/ahVHcHBwF5teui5j9qd6CGXGZ824Mfb9ispceVJL65S'
        b'51teJxAPLzmAXlW48qR2Ns/u0Qh0pF4nbvY85AGhTFOHFFbfD6QvL4yz1BFWgS4ACBaoxBKaPiYGKbt5eR+UrTmMytTlOrEQC/BevbgTcNDFFVmQ2qAAA7N7QTuaU1Kp'
        b'zwXaLMzAN3O1EU8fRETTeIEqlag31ZIeS2nc/RA/FSJzLj4J9JoJugJv/sxJCZy6j2qtuXQ3BDNuSL1F1KoLpazcKvyarHhd6eCF02j57hEtbgFxULoisJ/STQcyEevJ'
        b'n6YF46DBTdx+3JNrjQqERytOQXgdtHj+8g4atqdlH+qzUaR2K9Crzkgauoh4Z4z67GNBf+C3Dx7K2k+LAbtyuHcHtQXQoN1eb55WhEtp9bcS5m14ah8c3JBgI+2n9I47'
        b'gWCPOPBq+HZgW2tYnFZs0WnTKOhOJRcfCMI12ra5bfEoEoFeVl7kISsbG4WNhJIPoaH3NtIB0u198oyAto7p8qkj3QirXEce2bqRihbKNU33bTbyZkqgSv2BOr7CnJKL'
        b'sLtUDdVstFciTLIFghd1ClmmxHtFXBvJ9fLvdsPYOkF7Bm5ylVQk9hLOm6TpjXmyOgOeCQQR/HKajB/p4BaFaS87LjYMtKFqIam+I75J53n5KR5bMEg1uGBJEM5xFXH9'
        b'ZVX5F5voUVBgJgb1y5m1Q1z/ui1naszDOb0mNjglVMS93gEbl+84d0mIl0yCNybXGqnZWX7Cdlj9w8A9NPDlbFy8gY1YnjAwYc+BQJegALRjJ+JKmk6TT+s50Lwm10QE'
        b'/WkiDp6l1EbsI997UL76tTFcIn+sMy40N6P2oovIRiL/2MV6Y5Nd0ZZrGd91itvIgaist/FhsYMs4x/d9opCbBRC0JR8rWyaa8Cb0lxhM7eZD4ru3P1G5oceOuURZaf/'
        b'x8qHsj22T20Wvv6xLELvgssuibrUz/wfRJLf3k1sqHjzDyku0SfrknZ8t+TTPzp98Y32j3doz/X7Fg7szP9J8w2TBk+TpniTxpMmzTntDf7tTWntjVHtzVejGryjmpKj'
        b'Gt/95NOCIdu3Pl7ca3TY4Y2j2T//XOfTwFBri49Mh0K+yx84JH9SP/X9oqjECx5mPjGxBp96fj2hacjZWhrLz145x8S8cfzDP7geP//fnquXPPzpyMi/NYx6q0RtfkcS'
        b'3xnv/c//HLrY9lu3a/7az3p/2u8b++Lz+dpX5WZbvV/+y9xwdtXJMHfTzZVr32z+1jf/wcBmqcAjOihN9Vfvm9rk/Gagq1r6jbTqd7pCZV23L4ZNFfgGBOwLyPaKNgvs'
        b'L7Qa+07M2Ujvb5+N/JpW8v4391p1GuWXmCZ/t6px9sCb7Z/XRR8IdLo2TN2piu/tK7HpndlXqnR5aMntyNfNfmam+ub00vMc7WWLWcOW937WXhH0YrL8s/kev0sf9Z5X'
        b'qi06QnaffmTqb+34aP/bOQWFgZH7Kn4y8L282vjWFNvpacd3Tc50T3x+umPum7+erarbVh3DOu/6PP7E+EpX/7tb3uru+4nvymdqcfcuL6s4vdVl4TjWEO25J/RoqfhA'
        b'0bfab3ba/Piteedvn7gAz2L6i1vvRMTVGvzR6Ft+bxxpNjxvpXi/6N0Xvk4OLk4Hs38w/k9vrzelmUQmrX37a+m/m8h8sOWHi3uvT7x1YURjzsW3PTyGLb653PdW9aH6'
        b'nMJtLftCst4cDlOzPZ+YpfgL68xPVX/+7cXhNw+/c3HPj773Dwpur772Pck2Bc1fTLq+6Pvk5dthc7lvp23+WUq3cd/nR1KiTewKkr4T/JbCTNsHmy/cMJoQd04oKuX1'
        b'qH8YbHE5zug3cVu+94b4GxXBr3JFWqc+/bdd7y59v/IXank/vuGntar/r5+Of3+yyCLixcrx9274Vza06WY7vlv0e6VXH5x+9Tuzj1aGflHzxdIfVpW++ORru8/9s3b+'
        b'yx7Nn1q5/NG2/tnbyt0dBXmKm78QnVP44ruij23UNhbR1tGktxBqngjaAKE6L16Sr4Us5A7Lv3jE+GTWl0sV3PmePEnfDpo68JU1rfC6pX/a6cmOq+XbSODcYHWZZlCh'
        b'qiaoQY22LF8DaDknEZkXSlWoX1m+LR89O0R9qLVR5wo/vZID19yhqSQy9pDQk0N8S77+8oB/Ye5ljZx8ntOmaqrVo1ltFU01ntC+rCiy0ZLC+fbQY/nzz0C06f25mlf+'
        b'ovaXVemOvH20HSxVEn4g4tGNDH234Yum1bkp809tqvAjhT2ncXFhO3I3frAzVxdge0clB7eZCzdZ9Vfa5FkleqbFj+Q3HKsJn/5lKl66U2T/f+R744mjNmFffeJW5f+h'
        b'4u++KvXv+9yzsJuspaWlx7/z9zcfi/7bfxvP1avExmZkxSfFxsoclEUi+TPzUniqL7744o/FovUzYpGmwbpUWdXoA229BseaK21WNdfbc3sce+IfHugsfHyy8+bk9gnZ'
        b'vNVk/vzJyYJphzeOv6nHfu84Bn1kbNrm2BbffqBTtSfghbHDhNELY5fnR0JeGIU8Dzv9PPzMi7CId4wiPjK07NFrznyus11I9BQpXlcT6ek3eDYaVB5bVxIZuVWqv29g'
        b'+XxbwAuDgEo1fGJs+56R8wsj50qN71s5vWd1/IXV8ecqm+XHh19YHcbxb5QkqodfqemoWrwUoXi1XVl170sRild65qrGr44o4khLqrr/lYaKqvFLEYpX+jqq5r9EZfP1'
        b'nSITs0rNV1Ifsar5S5FQvgpT2KJq/VKEoiH5V8LL+nGxSE3nlUKWgqrrK9Gfy882Sgm+XJd/uZ6kiOP3VY1eKdyQ4IKiP5e/kpdCXeONE6TC+/VjKiLzzc9VjL+vqi0/'
        b'7YKCqskrkVD+ZVXh/fpptG38SmGr6uFfi1DIv18X3r4KEEcrqgqJkf7Ky683XtYL1eRdOKesuv2V6M/lL+Vlj/ln8tfXXREO1z205SeEKQpV/1y+lJdtGZ/JX1+fIByu'
        b'p29cwUNJqPrV8nVF+Qc+GhFiVcvPREL5SqZwVNX41yIUr44piCFCEYrfKIlVt71S0hSGC8W6pbzlWAUMjujP5es2hcP144ryKuFKqrtfib5afrZRblQXDtc9NHcpS9dP'
        b'i3eiDBNvHFujPPP6Exy/TFPCCCms+6nY4KPI/63SV8qX+UrHpSoKLwNVAlUsFJ6rmHwWqSPSs6r0/NBgV4P4I9vD854vbN3n817YHv+OjlWP1Qud7T0n39HZ9VIiMrT+'
        b'gYHVf1Rn63+ujvm/Vwe9N7T4pTZu67frXnlisaq/+AO9Lf0az+193rH0fUfP77mG38ZC4x5P8yAX0Vsum4LVXycGOyD76N/b4/X/o0K+uOevLID+T2KvHHHlhd2XKP+7'
        b'YtGrU2KxWEdYbve3i/9KojNhEN+QKHluEr2xSd1zsyRt6es/U8j1xhCWOKsmN3wQINmnX+50MeXBTxZ/GeT84Zqiwb/dCkgzeE/5zWKjS1+o25ivD96SXTf75D2rS94Z'
        b'spefW8XKtH58NUipPakxWGth+z9te6CgZtPbphdg02f6w9Mn7pt+54+G6olWAS93WP6o5f2zdtdaU/6x3Ny+b+EjZ6MfbXnvo+z53338o+Pv/PeYd37Y2xsesOODU5sD'
        b'f5h7bumyyeOGcwaT00VmuY/bs0fbZaecfuDj/Wh0qEszfGKgaG50REn50LdsnT/YUn1jdmQ64unpzuCiH7davPvDjrc9PzhV0ZX501+7lpYYru3NEalbvP+vvcrKDkrG'
        b'CVJVbd/1nFuixK5PNazezilR2eeQU3YxqCGuWt/po+8bmqS/mVOhkP/RD8T1qT2u93dT3W/X3z+/9o2E7WeaP/5Zf0HzavPI7y0qW9+bLZhSSrj0x8/Mf6768+u/MP/i'
        b'c+XgxNAn4KZbNhbePuNaJyHlbmio8NvwTq4NVBap05QCPw4120hUMhgZFxhqz5NCHQWuFtbD6PKyhB4i5m7foKmDwSB0NVS/kfyX7vCEjOqVRVp6ks20+no/MyrJ41lh'
        b'64hgZZFSBPVIFVTMFeRL+VSPCqt29yjxOC2IxKdE3EeLNChfymfIIxI7rrMWUorUiq2zRKoOCtSxGTRa/tzJLariR6/TCYukITQXIqYJE1s5JaWVIioW1m7Lz91GLaii'
        b'xdWSkFzrjVw0qyd2vs7u7E73hVw0xm7y3tCciIc2Gg0WEk7XB9n4S0V63CyhRXx6R37PBbxkFBiwO+SAk9iEb4uUuUlByWvrhkgfc1dioKMTzg3kOjN6IOTU0raSHOZh'
        b'bpPfmmIATQsV/IO57pJY+FqLn0j2USMvbCSdqeMhE64RtuGuR6zO7ddPimkpmRbkWWWoOoubhbXhwbtFIik9urhPTKMeDhtCXuHH5nb2fEfIohOvdElM84re8kwxQbl7'
        b'7ITs2UFCjq9g/92mvIRemRVJ6ZawYkGezsaPb28Wdt6s49rTN4IhcJG6jQI4frnPRsf6qDk2d+N7R6qTV1DzV6AJqqRFeShizaOys9ykzlPaPJuLwZnL5pkcBC6aIpH5'
        b'NqmyXoK8/46HFOUrR+38Ha4FC7M06tShwL3cTT0baXXuGwkrcb7Mgg21EDJhd+6m1l8Jm/pEbeXxQBqzxsgK+YzlWd5D/enOnhB7GyU/nhT5eitf53qZXFohsafVC7mW'
        b'J3hG2LaoEcqK+6/cyIyzHJ0grM4IDgoF9tCSy3Ux93NbwYZSd1rrC1/aC3sVyZd98kIRIjTTfCmVc3/4xm7BK8FUDXlXC6nWgxSoMkekulMBpjDOIxuD1bLXxC7Afncw'
        b'D3GpvYNYpGEgUctJk8szj5+4BGJQAh1wdj2PRXG9jZJok5OEu81zXyeBlsoXzNuiwqLwQ7IwJNygwE/SqUQ+4NyXpW4XoMhj3CMSB4q4jZd5yObo3yMU+ru7tf9LzlFY'
        b'P/43Ypb/mpvs+7KQRyffEgnRyf8sFn1mLlLc9L6m/nuam19obu4qeEfTutjnfalaRVBJ0HNdq36X70h3fyjV/FCq+6FU+xOp4wup4ydSOxx/+d/wE6nDx9IdH0tt1xWU'
        b'FA3WFSSqJh9rWP1aTaS45WOpFc59pXTykKI3yPN/+PKbjZf1lDyopn5x6G9/dRVHOmafgcCiUeN1CV7/8C/qhvhA0eB9Hf1qRXykaPD7XFtBP9WVvExFbKrlZSdha7GX'
        b'g4htxcKxnUQ4dtDwcpPwETHKDQpmuybJSM6UvS1s1KuYl5+dkbwmzUjLzVuTJqUloszKTs5ck+TmydYUE64Ka6WlCVlZGWuStMy8NcUUxHt4kcVnXkheU0zLzM7PW5Mk'
        b'psrWJFmypDWllLSMvGS8uRSfvSYpTMteU4zPTUxLW5OkJhegCppXS8tNy8zNi89MTF5Tys5PyEhLXNPw3lghHxx/ESdrZMuS8/LSUq7GFlzKWFMJykq86JOGm1RNcDqY'
        b'nClk51zTTMvNis1Lu5SMhi5lr0l9Thz3WdPMjpflJsfiKyFDyZrupawkV+eNzQhjk9IupOWtKccnJiZn5+Wuaco7FpuXhfA188KaJDI4aE09NzUtJS82WSbLkq1p5mcm'
        b'psanZSYnxSYXJK6pxsbmJkNUsbFrWplZsVkJKfm5ifJ9bddUv3yD7uRnCuk7/0xu5cMT95/8s7T8isIKaT1zz8gVFn/gdtpicYaiQOH+Wvkreflf5nablTwdRG84qHu6'
        b'Sn6vkoIhTk5MdVjTiY19ffw6vv+96ev3ltnxiReFJKpCagPhu+SkEBsV+QrxNeXY2PiMjNjYjS7IF5L/QfhcKSMrMT4jV/Y9gflfFmirfPG5fJH8xjTCEYxVfkayu6wQ'
        b'34iFfgejgI6LxS8VpGLpuoZIXbNY+ZfS/ENi/fXsfLFIVfc9FbMXKmZtAe+p7Hqhsuv5bvc3drL1O7sD3lfR+UDN8LmR0ztq+59L938g0mkwfldkKr/c/wK2yXC8'
    ))))
