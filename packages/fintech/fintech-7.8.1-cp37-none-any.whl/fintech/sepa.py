
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
        b'eJy0vQdgFMfVOD67V9VOQp1+dJ10Kkj0ZgRIqEuoUAT23Ul7kg4knbgCCAsMSHCAEKJ3m2J6r6YYgz0Tx05iO3HiJPb5S9zyOS4pduIkNnHi/5vZvdOdJITs7/dHaLQz'
        b'uztvypvX5s3bj5DPPxn8Todf+xRIBFSOqlE5J3AC34LKebPsiFyQHeVswwW5WdGMlijtSQt5s1JQNHPrOLPKzDdzHBKUJSigRqd6sDiwJKMoXVtnFZy1Zq21SuuoMWuL'
        b'Gh011nptpqXeYa6s0TaYKpeYqs1JgYGlNRa751nBXGWpN9u1Vc76SofFWm/XmuoFbWWtyW6HUodVu9xqW6JdbnHUaCmIpMDKUVL74+E3Dn6DaB9WQuJCLs7Fu2QuuUvh'
        b'UrpULrUrwBXoCnIFu0JcGleoK8zVxxXuinBFuqJc0a4YV6yrr6ufq79rgGuga5BrsEvrGuIa6hrmGu4a4RrpGlUVx0ZDvSpuo7wZrdKtVDbFNaMS1KRrRhxaHbdaNx/G'
        b'DUagSicrqPQMKwe/qfAbQZslZ0NbgnShBbVq2sS+MiRHWTXByBjMReQh5zAonCSfQ1rJpsK8OeQ+eY5sJG2FOtKWXVaUqESjMuTkfkaBTuYcAE+SO/j+gtxs/VjyXHYi'
        b'2US25CuQhmyWFRSS+84oeAAfrSMH4IFsRSjegeRyDh/Om+wcTO/cxrufSmDv5BeRlmzSpsuWo3CyU4bvpONzOp4BSMRn8Kbc1DS4jU+S27lka2G2AoUOkU3OUTr70xZs'
        b'mzCS3s+Wk5v54l0NuSgbvYS8AFXQJ3ArWbPcng03ARTZwqHAbLInmMeXG+Y7h8P9cQHkYBC5Gkpu2PEmcrOBXF+KW0NDEBpA7smGyVX4Jj6k45x9KbDdYWrSmpdDtsjI'
        b'0+QIkpF7HD6I706A+zq4P2ceOZSLL8RlJxaTm2RzLtmCNxXSRuG25IJEnRLNzlA1kRZyFZ5njV+D7+O95BrZQtrn5OcVKpCiiSPH8TZyD56IpY3ftgofTshJ1OcnJnEo'
        b'OApfIWdlgZNi4PZAuJ2O949OyNLHk015tGdBZBs5R9bw5CLZgW9Wcj4LK82DAdvorPujJfq/IqYrzqVzxbsSXHpXoivJlexKcY12pValSejKbQwAdOUBXTmGrjxDV241'
        b'L6FrtS+60sb274KuBhFdX52oRMEIhaVE43lTypYgVugcRXEYoZTolpg/muLFwl9bAlAYlKWMrCzdulQvFpbNkyP4q01Z9kJE/4JF6AyqDYTi8sC+8q/C0fQvIhq5d+d/'
        b'uOh8fRtXG0BrztnPXVbB830vZryR+my1EbHi1JF/C90VysV9gd6L/nj+xMrpyI2cerixKHMMLJzWZLybHJoTF0c2J2clks34TGlcTj5p1ydlJ+bkc6g+NGDqpCBnOp3e'
        b'3VMC7A7bsqVO+xIDoMxlcp1chSV3hdwg10LVwYGagJAg3I434i2pKWNSx40emwboeFmO8L2FAeTC2AZnDq1lF14fnZuXU5Cdn0vaYb1uIZsB2zeRNmhLnD4+SZeYgC/h'
        b'0/h8Mbx9lewl28luQJU9ZCfZRZ7Gh+chFJMSEl42z4sydDxV8BtDZyHFQ8tkVTJpSvmNMImrZDClPJtSGZtSfrVMmtKazhRI3mVK5QU2OteW/74UKbNPhKupJDjXtOjF'
        b'X7x0eduVPUMUr541zX/xVtirC1+8vu3onqPNFu4/t+yqyhAy46Q+eltWiqx6EsqpC+m/16RTOKLh/ZLS+OkKGP/NMAZbACUmcvjKlBIHXUZD8QVyIyEJhmaTfsxMDinx'
        b'Vj6RXCxiNzPq8cmExDiYqgPkIg/3DvCJeC151kE7P5bsLEtIJG15o8kxclWBlOUcuZAdzgA+julstWbhCwjxq7hwciKT3IvTcW4+TqeT2WhPfRIekgdRU6ps1pXmem2V'
        b'yISS7OYG0zS3zGkR6H27ko7XzEAunLMpPS/p5O6AelOd2Q4My+yWm2zVdrfKYLA56w0Gd5DBUFlrNtU7GwwGHd8BDq4pxtvoJNoUNKH1zaIwNBTGvTBeyfGckqVO2pvx'
        b'+D45kkBcs6GzHOLxPm4mvr0gs5LvhBJsFilDARpCkUJeJfcihaxHpKjqvM4DuyBFRAFjG4tgHdyw56XjQ9B0cgbhUwH4ujOcIiTZFpqbp29QIE6HiCsBX2F0khzD22F2'
        b'rxWSc/g63FMgfANKNjgj6frYOo4cJa2FY0k73MoAMm6c46Rwm/BzI4Ly8c0aKO6D8PN4RxwDUlOUlJBPLo+B4jmIHCQH1KxVZFdfcjwhCdbjXiXiFiJyKoGcF1/Qk7Nk'
        b'5xwtbcpKlD8SX2TFeNuUieT2U2QnjL0e6cnWSF0Aq6lyAX4Wb8VnJ8PgkvXwn9zDx1lbY/CNEfhY8JP0xgn4j1/AR1hbyXlyyqaPxM9DXWQv/B+VwMrx5pV4V6GesPKb'
        b'8L//VLGxzxhm4RfIJfw8jDR5Gv7PIGfFmo7OCVw8ibDyF+A/OTZafOMIuTxUj5vx86E0A/8byS3WqEX9yBpoymbyLE/FmyBym+x39oEbwO/IvQrSWgJ1jUKjZHrWbQdu'
        b'Hy5An3YCuqSgFHxfxhAM71g4GijOXis5AzdwOzKQW3itk64yoFRXS8g1O7m2DFCPnB4VwQ3HF8sYgfDSJN6XjPSDpBo1ocfDVnFN3EaQB23yJm47v1ROqQ9bN+Li4d18'
        b'Uoqbq9RxHcuQLYgHgVNqLXZHpbWuYdp8WiW9o0ROKn0OF+bnkrZcL+vOIrvwNSComwoLyBYdfk6Wmopbc/EOaLKePB1EziN8l9wJwpdt5KJlxgfvyuy7oZbfDDSP2PqC'
        b'Zl1RZPPPP82Qv3z4pZfefOULbl9bgGzTmxeWLg2PUe4b/uUXGs2/7p1Zs/DdJsuSFSM2zDgtHzjsjVj7Gy26mPeu42+jmvdqp+ad+/vp28HuZ3+fljblw8/GCD+tzXrz'
        b'o0b9iWljPuwzfO+7f9k8d+GWWc+GjPywePPEv966+hP7n59t/5/d/euf/2B2knXgv787t/7470Lfb9OVpIwHYskWzMmArIQkHdkMfEuJz/P4FrmShu8Oc1CxAm+ZiO+D'
        b'1EE2ZucVUJK6EQXhKzzIPGvIPva6g5wGZtWqB7kMhELlE3wqfmEYvprjGAo355NLwF0oIywhJ8hmELrIJnw+R4EixsjIDnIV32F1rB47yZdaK8l6INh5ZEMX0qmTd6al'
        b'/jPpDjLXV1oFs4ESU0ZGB1F8yZJzck4t/ci5QPgJ48O5MC6Yi+VsGh/yytndgfVWgx2E/Bqz3UZ5vI3Spq4t4W1h9DrUS1VpNdleqno73Jeqauk4nyWn8DMSMhHXAAmf'
        b'5Kgf2SFfnhHTA3llHNePvPbMc7tI/V15boAoRt3JD0dhiYVwZRwwP2WEKBzZrNlIqBjGIaMxZ+8gB8pkpUPjwtCi3OkINRj15kWLxEdfezwIvWZOBkHMqK+d8QRiRGIF'
        b'XrsiLQVEk+enI7wTVYBucNjyo4SPZfYFcDcyceXnxs+MNVV5pteq4vZ8suby/qsLNgvF+5r7ToqNTtELnwifGPWpsqt9J8fGpEYfTBeK5xfHlu8fnq7fEPmz9+eG5R6i'
        b'QsBtpcAvHFfCmP+w30at3aTV8YxPkzOAfgkl5Cpl5BITH09cDqYB3MDrdQlJ2fpGe7wuCQQxsgmhWK38ib4rJKrwSAzrU1ljrlxiqLSZBYvDajNI7JpNenkswzMNpIBX'
        b'fXzwSlZpEdyqSquz3mFr7BmtKN20RXjRitay0AvhlB9aUUlzDr6MzwFKZYFag7cWJoF8uQm6lQw0uj2PwxcVaCo+qCQngabv89MDvCjGhDoOkKxDqOMYgvVSTqfNHNEF'
        b'wYaKCKYfFIFAt0qp4Y1Njw3KlXBpyLIwBGtifoXDWDs5Q4VKWWkJsFn4u2JxoTF483hJpl9kYDJ97Cu8UR8aUSsW/s+wYASEI27EPGPwmOKBYuGPIiOp1j1fO8PYtHJp'
        b'pVj4/IABaAJQgBELjVNCqmxiYVD4EGpfiK1tMk5RGhvEwgMzRqAsWAe3ZhpnfAfyESuMmKNDRQipd1QZKwJTJ4uFX6To0XyqZSw08unJkkbxE4uKKiQTRicY865HOMVC'
        b'yxOBiK4Id4yxdr6mSixcPXsUygNAT44yzniJXyUWNqkSUCm0c02YcUZelAR9Sn5fYJsoa6TZOCBvaLpYeP8xps8Y/1ptDHbNjhIL9aZQBFpySuhEY22lcYhYWLOqPxoD'
        b'6/XVQcYp8gUJYuFn8YMQMLYUMsbYZA82iIUDlw2jEqF2mNJYMSsnWSw8NyAGZBVkzBxhnKIYNFcs3K5KRotgkG9PNVYMCdeJhdmjx6AaGM/fzzTa+mWYxEJucRpgAqpp'
        b'DjWmRtf2EwvfiklBRigc4DDOOJC2GumGMzmBx23kbBoid/EahEaj0WkGJ6WugyYZ0+R4bSk1W6TiIzGiKLUJn12cxpMT86gum0ZORTABZCBuCUlT4sugP4xBY/ClAFZK'
        b'XHjXE2lcOay4sWgs3j6VlU4D7nUoTWHBLaD0o3G181mpEx8ekibDx2Ecx6PxZOMEVhoyLSJNRZoHw9SiCeQy3ivKWkdBjbqOr4G4CWtpIppoWMlavDJsDr4mD4JHJqFJ'
        b'+Nh89nA+Pplul4PA04zQDDQDZLGTYiUH8KEUO4930F7PRDPxoaGsvC95Hp+wK0GA3UAF9Vnp5AzrOdmDt5Jn7NxQWp6BMh5bxMgtOTocb7UryHN4LUKZKBN0Tpco3t0E'
        b'0Wu3XbYQiDCajWaT22msnlSQtk7ZVUm4FXALZZVhsfpkci6BXEMjcDNlZNmPkyusltm4Da8n1+R4H1DXHJTTh9xjAyMrGUiu8fguoHIuyg0GqZXNzqknoFiJXfgZBFie'
        b'N9IpdnUfeWEQucb1o13NhxHZNI+1PRdvGU6uKfBJcgehAlQAdOoZVjveL8fHyTXZE8BSC1Fh2Tw2vPiwsIpcU2VaEazKIpU486S9qX8QynQCLQRqeBDvF0flJL4UEiQH'
        b'7XcdQsWoGGT1S6wpAybj3UE8jOV6oDioBKTcLax8NW4m54KU5Dbeg2ApluaQ26xH9aBNXAni8I40hMpQGbk0nzXFnFYXpCD35yI0F83Fh2pFoNvxZXImSAZi8S2QidG8'
        b'iWSN2PBLOZODVGRbX1g6aH5okjQ/o1JgDkCev4TQArSAnA0TTWXr8A1yBLfK8bOwUstROejpLrGraw1NuJVfQSd0IVo4flTt1999911IGDNmxC6dYQyOlpeKK21843hU'
        b'C0v6st6YWpW7HFki//sNZ38T7tz75h+pv61rn1zPj45t+ePN1/+db2yWDQlRHfmI/581fOAnmWOytr9dNHzH40ezTuY/XfGv8AEbS4rCn91Vc/abk7Gr0hUTA82nfjXu'
        b'13y6+jOrefuQV15pGXk1z3aoRRG94FjV/qi5CyqfbnOd/0n0u3+6/LNR/4z7U9oHaarrTR9sG3bvvwVT5n/1txv/OTT4rf/YBzzWnvpK1Z25TzT+OfJgwC+v7VyTN/np'
        b'oPfCX3vf/N1HP3rJ8u/39jT86/WDqLrWEbvw276PH3sz/K9Tm5vfKfvVOe3IX0YdW2B+UqbaP+nw9FIQZKmsOgCU8BaQRAuoDaxdz4Gkeo4nFxPIRXw/jYkGM/GBRtDv'
        b'0/AGr2SAz5Ld7O0qvJ+cBeksgbTlJ+bosxUonNySlQFmuqZVsLfx/tARIKZuyQ2cmU0VfeUEvq+A29jbs8neKDu+kFWQGEcNmaRdhvqQbbKCUfhyWppO0a1MIe9OAPCR'
        b'NDSSpOGsNFCZlokZ1LKMhGBOzodRUYOP5OhPOC8HcaAfzcvCQAAJY0KIkrNFekUQGYggzsqeJA/OFuUVOiIZF/cIHc/4WQiopXTxzHoqcgSSPZLUkQ+JaHPVkTUKvHMq'
        b'ud2DsEFNjshH2OB6L2x0L82qRGHjvXBRLGhIs+pfnDJDEjYGDA2iTFidYqjU/xE6Ka6xZ8kpspVKqSCi2vAhVBFLzlu2vj9TYZ8Jt1c1VHxuLH/x8rajO880H20+s3/0'
        b'+tEH9/zxaNbQ9brYV3NNBaYa8w75ldjifen6pRvKN2h+3E95ZNKe2iP93hiDfv73kGdWztdxDGuCF4M0OhPf8ZFGgYs84xE3e5j/fuL82x02Z6XDCfKmwWauMttAwxFx'
        b'IZiOx1OIV4MawwTOaJ/Zltvh4Z6nO8Y73fTFdd7pXuM33dRcjE8byU2vjJmcpIvPx9dVSbrEHCDkyTn5uYk5oNYUKBDejjcHkrXkbmaPs+8vavY8+366jKdC/9lXiqYi'
        b'cn8wuR5ELQWghT+Jj+H9geQWw4C+sUw+qdmaYSzeoJ6EMi2Dd09Q2MfDrZGvfPW5cRGb6CvNS7nKwI9m/Hjobc1JzY+rfhx5snbP0BP3Poj82LhBowx7bN/aawqkORuU'
        b'gS9IugY+rcC3mMWQV+Jb4uwictpBNyymTiNbqKrhp2ik4BeeILeGS7P08LmP7aRl+M98oDjzAWouGmbeFus775WPnPe+3nmnL26iFYaxeUff+M08VT1TQH1/pqt2UUD2'
        b'gILhO/ON+EwAMMpjg3pUY2WdrITfU43tburZBE+whq4QZCDnpxj1oxdmihwwqkYRvoqDrk035kUVZIiF6/SyvK0cvTLWbisdjSy/fnCSsxdA/tTejecaPjH+yfhqRU3V'
        b'efMnxtOmV/dVVCWnfmac/+KtbUOAAHCvVuWYdhg/EfhfvqZdjYrKVPbAkrRnJ8wcNXNIyYRtg1978R0ePT2lz2P7Aj0IsnM43ofP5eXr+eFkG5LncvhqNrnioGaJkEVk'
        b'H7ArsjW5MHVgPmkryMbn5SimWD4Ob8PXequPhtSbVzgMgtNsEEwOET3CRfQI5blAYA7U5sEDS7D186KJ3C2nD7sDas0mAd5rfISlg6rOtgFetKEVtfugzd/DO/MH3E62'
        b'hJJWugOGNxXq8nFbId35I89p0QhyVVGON5BtlTJpZhW+iDJORBQ525hSuJRVSglZZMykLAdkkTFkkTNkka2Wd7fPQKtUdkEWhYgsZi4NvTjg5xQFwq2FahEvrIEK9MkA'
        b'hiy185ZGIsup2HqFvQLuqM/uH7jlSsialGD5e8uKU9J/8xPN9V3btx1pLXaX9buW8XZk62dfPfjVxMS7KXHRip+8+blx9rM/UfU/eCsuZsqxW7P+940X4hvrp5xpmZL6'
        b'2I5Tb6dO/Hr8lH9/93rc/F9er5z82NTSvgNixkm7FkWzyA5mKxsZrAKN6BhXhvfgSw7GrQ6kkAu5DTF0EMW90ynkHrNoWMixjFy6Js/ho/ByWyGH1GQLj1vMscy0lmjH'
        b'B0krPj+UbEwG/iPP5/B9qLadYaeFXAKNojUfn8fnm6gW1sLNjiKXepJXlA+91Rkxg6vNnfAyVsTLvoCRILBoAC8DuWCe59V8NG8b6MVOBcVOQEmKcG5lpdNhrfKlaN0u'
        b'CMBaupVsG+SPqbTS/T6Y+mm0L6bSN2qrx+aSp8MKE33xFA3Gx+TkIL67rHs2NgZJQgzdN0VVil6yshZfFA2hFKoLig4WUTSu6qeodk6CDIUZs38yUrJa1FcOQbeimqkB'
        b'bspvAtIk1TtSjb6ePwpw2Zg3duUksfA7VSCSLxGtcosjHGLh4VkRqFTGTH1NU1WS5v511ED0VdkyQD7jolGhS8XCxgVj0D7FW3QthN+XDxYLL/EqVDocBlRrDJ5RXywW'
        b'/tygQxPsxyn0GeGThomFL4+Zhl7s/w0lxsW1fWPFwmOpU5Fj/r8ooGKXZblYOGbyZJQX/SltZ3GARiMVZseiXVYzrbMp64mZYuHf8hNRyvQb9PWh/3FWi4XTnuqDvn5y'
        b'Oh2Q4N/YgsXCb59MR2HVMPANxlT9OMm287ZRjr6u6kN7pB8yr04y40wIQULiaFqnfklsolj4XmA/1DLaSpvUNGFEiFi4Pns8OpLrpn0vPpYRLRb+ZlYR2macQQEt/usi'
        b'u1g4q1xAR/J3cwAos8ahFAvvJVWjsH6HOHhdOXqaZBqyjoxBaxoW0DqnPFkmmXFGJ2jQefVUOnTBd5+aLVnAcp5Er475MwdNis6ZIxmRJq5KQ+plP6GzWdyyaoVY+Mbc'
        b'oWhFI+XoxqFvhGQhy73PDynsiYDDT80uKdueX0BSwta/cuXvH/1oRH5Adr/5DWH1b2Ykp4Rnbd/26uaXV+xue+cf6j+HTAh45f0BW9r6v1T17dT7+78s+TD8VPSXRw/Z'
        b'Kn768UsBp/7ZgE4VbTFyEbvk/+2beORP3K/Vi351JO1kUwt3/sUPnwp978u5bw2cv+mAEDT8bd2ChOL5bS/+uqX8m/odt/o23lMd/DDkzKA48xuXPy797F9lOStm/u6b'
        b'3038za450xY5Xzr7/ur8fjd3Hrj/dOGlu/2M259rGvtB5o5/xjc0vz70jCO8NaNhXWrDtYY33v/r3cGfRP99t3uC/Y//5p0J//j8T2tSC8bcao/46LOT+2Ytf7Hu+OuH'
        b'f/uXeRX/aqw+9/aXL77z+r+H7U9b9HVu4d+Gf5yc+tu3fnPoR+/+sc/pSUGpMUOmjIj54tR3pwqbBk2//y0aGrn4yIKf6WQOLSW6G/H1IIlB+7BnfLtSPo5cwRcZ0R61'
        b'GF/M1cdlgRQElBefS1jON87lGOnFl8jRlAR4O54DwXiY3MmBangIH9CFPIKGPjrpgUL7mqopBa4w1S8x1FhrLZSmMjJcKpLhiWoZEGL4Hc6EhDBOy7ZDwpjAEM4Hy+k2'
        b'Cc82S+BH1ukvu9LIguH5cC4QSLias2m9JBzk0EazyeZDtXtgKZxtiJdg0you+hDstyJ9CXYiHdUbK8m2XEavc0DRbgUGRh0d2kHphwnSK3EL2Y6mkitKcss+2k9xUEh/'
        b'7VWQmKlHGSrnhSBm+uZBH+EFWUtAucwsF+SCogU1c+UKuFZK10q4VknXKrhWS9dqs5yygipeCBACW9RQEuAC2bc8kAmwwW5VuiDYzHZ7QaVSgq+Wfhnln0RZieh643XF'
        b'qVJLDEW5UQ0MRQUMRckYiooxFOVqVXcyD+VQXTVjRYFoljs3YE4J/B2C9+WgIYCFe0WXi8JZO+V2B1xtbBk9cPOVPjglTP5d4Z6WEtePZkWmK96IWzOr8tSg9K83Z10M'
        b'PlPy++FP2ic/nxtx8s4+x3tH47f8NWHO4KCmjOdTB93kP7wVUxvr/upPeZM3fPvuonnj137TdHgT/iKjPXikLORQ8KVZE9Ke/Tv+w6GQwv3/GvzqpcHjyubpAh1UFxlM'
        b'DuONnjVErsjoMuIbZeSOgwqauL1vnrg5OBhv9npzgBCzi4kw87LICZ/dS3I4n08j95OYBoYPgvTJvLBozfg+WQey0fM83vQEvidufb5AzuL7CUmJomp+XEP28yn4kFF8'
        b'+wR+IRy3gijbnps4aCZux+0qFBTNE1fAY+Le6E18JQu3FsIKJ234flmCDp+Vo9AAmWOStDeK11JTKH1Cj8/IkVJNnkV837ljHBTh8Q68jdzFrckgmSVli8aTcHKCvIBk'
        b'ZC2+hg+ywSGukKnwTJIuBz+Tn59IPbtaeXLTENJVTlf3moR0kAiVwVBvXm4wdOyVPgVCNtsjpcqlhl2Fc0rpZ2WohM1J0nvicle7ZZW1drZpBQqoxdHoVjdY6Ya6YHYr'
        b'7Q6b2exwBzvrOywZPakbShvdTLJRNULcBhtJE+paaYvz0gnqnPitD53Y0M+HTnRppVeK46RfuhTsbNsFLRZNTFyBjnOrDdIOHVzL7ebaqg7vAXG41FNqTXUVgmlaCNTy'
        b'd1rjyjAPLM+t3gJTGOhIAfWL98LwArIlQKKBl210i++RNVaJNQYYPKPeQ62h37dWlUGcwR7qDOtSp5+4nIREqw/QyB8gKNN/POpM12QFlq9fSpTZ6Ro5Pvybz42fGF+r'
        b'aF1fUxVc9X6eDEV8wWN9mY4TSch58kK6uAxTQfdhK5HvCyTkqOQY0r1ibbH72N46fLKegp/olVGeafd7ymPXYQPVgeO8H7eL944dNYeFcx6NfQ38fKHxxePugQBNp/90'
        b'QYCvBuoOZjC4Aw0G0WsZroMNhqVOU614h60UWI42a4PZ5mgUV9QI/2WVwrpL3cdMdnulubbWs667Go8Ax8TH4BHWBerl8S8kmQ7VCsSFhwVz7IdnjrKjLOSIPS9bl5OY'
        b'pMCXlChwMRBQchwf8JvfIOmvfQvnw5q5ctku2a7QXWHwG7Ir1MJX8XAl/Qh8m1LQU9bt47EaBqyTMu8AYMNyswKYt6oFAasOaOOBgSuEQJYPYnkV5INZPoTl1ZDXsHwo'
        b'ywdAPozl+7B8IOTDWT6C5YMgH8nyUSwfDPlolo9h+RBoWSCgfKzQt0VdrqE9EaiY0K+NY20OBpGjvzCAiQyh8O5A+q45VBgEb8vKw1jPQ4XBbbyQKJlCZIJWGML61gee'
        b'H8pgDWOwwiE/nOVHsHyE+PYu1S51lWyXXBjZJhOSmIAhup7T0dK4QqsChDhBx2qMhBriWQ0JrIYoQcZIQDIIMJWMKj4YFaj1+SeViv7wfnd0SrfcAmKnW05RsDuMK6hU'
        b'SRNO14jGs7gzKZ0QJaEAOnjSpHrckzVVGol+qJhcpAb6oWL0Q83oh2q1GuiHjMlF8g++AQz2axb9l11vcVhMtZaV1IG/xqw1SZ2wAG8y1VfSEwCdX5nUYLKZ6rS0Q5O0'
        b'GRZ4y8ZezZ6RXqC12rQmbWqiw9lQa4ZK2I0qq61Oa63qUhH9Zxbfj6Mv67UzsmfqaBVx6TNnFpYVlBoKyvJnZBTDjfSCXMPMwlkZuqRuqykFMLUmhwOqWm6prdVWmLWV'
        b'1vplsMDNAj2YQJtRabUB6Wiw1guW+upua2E9MDkd1jqTw1Jpqq1tTNKm14vFFruWWaChPuiPdhmMmQDcqmtzpOGhMz2JtYteeY5ZeIYX1A/BbHvoyxLTFd+XMjBGJYWJ'
        b'aaPHjdOm5xVlpWtTdZ1q7bZPIiRtnLWBntgw1XYzgB6g0B0JIlx13+Le1ONhuWJdntwPr09ktmJt4vUPqMvPat7VEBpc4KQLMgsfiKQ2Q30SPRGRO49spOcUDoIMLVrA'
        b'8F383ERmWHjpiXZ0JHMCj1KMSUqtDjknQOET+Cq+yKyHRWQjFbGTySa4Kixh9eSXZdH90Pz8bLw3MB804M3kWAB5Du+sEU0qTSp0ix/AzEmf14UiJxUS+lMHQ7rFmgAV'
        b'kGNpoNPNyWLiNZOtyQ4dPoNK0lVkL76DD7N6EkfI0KEsyj+Mea9HTZeMTUUK9KeCGGbMfTyoDDkphyM78LP4uLf2c9Np7WQjPcMBLU4uziKb85RoNjmhJFfINrxfcsW4'
        b'R1rtS4HVFdeRduiEeoHldfM6uf0XcPPTfx4b0T65fsbosIxX/nm3/ZuWiI+0b26LEvr+ae244n6tQ7MiN/xyzFL7e5riaePPN5/4X/eY6j/YX5nXb8LXtSNDn/rd74bv'
        b'q10dsuGzdVOXfHvc/vo7K47c/Grlsi+nv1c2+A9JnxydXznlndrKdRtWJ1/ThVs/qfrZvy7v3Zu47Jc/U//nwz889vTj27Nvn/jFj7568Mrvr/xz5Kb24WPv/+x/mw8+'
        b'/sXLPxp15/A926AjL7+l0d9/Zfhwqzbm8h9SS68tXjT+3th67WsDV4y6XbPIvHPJz558923lxM2P/Uf2x505I9PG6MJFxWQNXo/bgmCQdPnOxHiyOZlHUeQKYINLriYH'
        b'8TNs94KsjSI7ldSbuvOGO2khdx3UtroqLSM3KSdfn43bSDs7K4P64etkTbq8nlwmZ0RvvWfwLh3dQSP3Irz7o3sWOajYgls5ct+7+eSpIgpfXURaZOQWvkluMTh4LSDX'
        b'0U57bWQDWaeVP1EDbUmGZx4jN+ghCED09gSyCV9JK/RuZ+ZCH7eKe/az8RUVbkfkBLOtkxfwtSX4mTDR2sDQI2gOD+9snC3qZifwlidxK22YuYw2TUEOcOROrJJJnY/D'
        b'OG6mUie8h7dkgFZ3kKPWdnyNvdyHrMHN9GWKjOdLYckpyB2eWxEqdulpchawXFIuyW1yskO7XEmuOagmFAa9PkL1xzYd3QA4A2tOHOpcdvoqAV9TkPUTyHOiDLy1vIpV'
        b'l8fhw/gStOYwh7eBCiuasVbZC+BuUr6SHCT74OZzHD5YlM0aio9nL6DtzAcSEcAz87imWjZpUj27W4jXpcGbIOHh9Qkg5CmRZqYss5psFFXkvRZQc+FlPYxzJd7H/F01'
        b'+LRslhzv9Oxwaf7P5rDOojvIxRbg9JJam+mR2kermXtmMC96SMg5DR/MRfPU3hUsOQaHwa+y0w9PBXL4CeZB2RNpcJIHQIEoKAeIQj09u2KjFp1uxewOfaDXmrpOJVYS'
        b'4V87qzPeWzETxKmz+mA/XeKjkb66RJem915PpbJPD9rffI/21wHDows/GFHqFZUoEwOxwsPF4mxmk5Bora9t1CUBFJlgrXxki1rEFskNFZbKHhq00NOgB8MpeBCzeoT+'
        b'SLA1noGgsk0PcJ/wwk3oWRL6fuDFXtvoscIegJu8wJN8xagfCj9Qgr+Y82ACD8vKJOqjDCl7aIvgPxA9CVjfryFsJnhbhmcR9NCGam8bknsjmP3wdozquR2Lve1IfLRI'
        b'9wPQIqNn8HVe8CmlTEsByL6WOK00pdpadta52xb8cGOOpIw9ONZFQp1JtQu71tJpXdrN5jp2thpUGqZ0dHmRnreWNK0S0GygRxlOm1VbZGqsM9c77Np06EFXgTgOugmd'
        b'hReXjUtKTUrRPVxkpv8UqKsdvVTHiV6b7TMjE0Y9xliZfDqHz6bUWy4c+5mM+bhM+mbB58bXKrJMr34cV/yJ8dWKP0GOr/g48seRJ5/4WPPjFUpt+5B94bK1aTL0o1MB'
        b'Y6cO18nFkwn7RkR4GOU8TQefJNej2EmalavI1a6iEIhRzUwWInecTJwy4rsBpNW5SLwvnUo+WMOcCMgevGN6LhVH1Pgq4p/gkhvx1Z4sYCpqdvIcpJF8jp5CywK5aGpi'
        b'lUi99EzB9zR95ULS4Meudmj8Tbj+9cPLlPX14F1EzQTIxfXKu8iDl64uaFBidoimAWetwwKKsUTGnXZJE2bBBBw2U73d5BMUoKKxS0W0jknMODLJmA/PQFXwx1Rtthl7'
        b'0Nfov67GTslxpSRzKxrweLAMtLD6OQ2rkJNKBCPwGXL4YVrYIaOvItahhZFncbPlpXWNnJ0qcj/+Of7cmGOKmfTqx/riT42fGBdX/Un4zCh/U7flHX1G/Ihg3fRlEUXH'
        b'myc+M3r9kH1r0wai+D8H7fvLXB3PZFV68hVfD8I3HvNXGai6MBNvZLIquTsFb/DIqiuoEtaNrIovVkj+SY/a2LSbHQbPBDGuzFA0zIOiTyHOI9St7OtBpC7vFHiAMayc'
        b'5I+33XhBsSc6MDifrko/DN7o6wfVA+DeChwa/9d6oPIb/JlMb3E3yXPciJ1E7dYfi7m6MDcXaj70urr05I0lY8xJ/kEe140Fzru+rDZLtaXe5IB2WYSH8cN683KJZo9O'
        b'Gt2NnePhxh1BtKCwLnu8KAFQkrbYvNRpsUkjIsBVpUMrmCssDnu3BiW6uqEFdmudR6ayAJs01dqtrAKxanFQq8w2+8PNTc5KsUUzZ2QDA7YsddL6QB6Jo8xWa/O0CmBl'
        b'O0yU/fZMJLq6QqoLnFMpIzlRh5tzC+jWOGlNnhNXkDgny3sorJhszJuTJSvW4TPZs8lG7RMVNttqyxMBaEZ1aN0yss5JVWX9U5mkdR7eJxlKqA2mowKEr5LdZcCpdnNL'
        b'yQ31PEMKO/hQHYTvkGvBMONkXxY5jfAzqUoproGjyq5xzs2iG5xlZKN+Ltusb8VnSrP01Ny0rYlsyc4jmzkgTcd1K/Ce4eRkKY/IbnwzuIhc7scOuUFjtgZ7TTfQogZv'
        b'lUXzEueqUJFQ9JQSH6chDSwhSUd4uxXeCry/I/G1nwWsmR6c8WbTjw2yPRVDytccXHMkJeiVwEOvXwv681spdwKGuPpvfPM3f5bhnCefurz0451Dbk5xBKg/PLbglw3y'
        b'iKzCl2+UvnnhzpJfuX71yaCXXpmWcAHffE334IV1/336qYP9T//8NzXH6hu5ha9o95RrdAFs07dyGrkJ9Bi0ZaYrB9XzE6eRg/2DHXRHkxwnzfhCUDw9Z7AJNwPj3uIl'
        b'mIPxNTm59GSWuDW9D3TzdaJrMdmBd4mWkbxZTFhoBKZ+MbfDMIaCw2R4x+IoOdnGbDN4V76tk/2mH7wC9BhvkvbN59Ti7aQ1YYCvoJBE7rLq6xbXdDKm4I0rtPInhpHn'
        b'2LuPJ+F1uHUiucLMCZIpYfUU0Sayj5wgQOnJBXKA2hMkWwKsDdG3r1d+K5RidtAHzxHLoR3kPUIN+rhI4oMlQi/mlJ3orl8tBZ42MDLqJXw9UX2Zz2MdpH8OJJso6Y/0'
        b'kP416JvIhxJ/v0b0XskFItYDyT/qJfmjmY7VQeN6Ui56qVtUe9vg7EnRPu5tw+RuSdvMspmdrfbdtIZ6C9XZzFVupd1SXW8W3AFAlJ02G4jzmZVyqaXUiB3soXkzRKbU'
        b'EUgJuYIk95ngqmCJRck3KoBFKYBFyRmLUjAWJV+tkFhUNbCo/T2yKDFwlCi7MWrvq6o8fKuI9kWk9Z53vd77D7f6s56Lb7FXYNRomYkqaUnamaZ6qhGZpHsVi4Frdcuu'
        b'6IYUcJCSwgnjUkazrSi6TSRQtROUpYeC9w74JG1mralau7zGLG10QYdpnzue8HTqYeDrrY5uwNjM0JF6+yRtemeh2Ch15xH8rqtGFljAGMw0vC7An92RjRLxLcuComKJ'
        b'eXGp4SONeCfeSa7lkms5aAQ5riEHDOSWk8p10Y3m3KTE+BwgqL7ve+vNyimLk6IggBQ9CD9LTgwMJqeX4FYmmX+VmIW2zY+lJ+bjo/OHISc9WoJv4fuTqWR+eW43wnli'
        b'Tn6Jr2DeWhJA7pNnyWnWnjlzONLKHqEWa1DzbiRkQ1u2JFD22cGXQSHU5+QlZSfGKxFp1QUvnWxxUokNHroDvMWHYWYNJG20SxR4HJBtkLz1usQcBVpJTgXgtpVku07G'
        b'AnDg9QPGM9AyhLeR5+XTOHwOX8kSo1TdJMcDEsS3oc3kAN6gJvv5J2eQvSxGFz4MgA8l5ORLQ8mh+AkRo2TkYAFZa/nTnQucfSM89WXz0wPfeD6EpATLi4oNrVzqeter'
        b'YZ/+8pW2+Nuj1YVht43Lsg4PGlLXL+f1qNBbJDv+xX9FpM399sjxihUDF+gvna06u7do9Lu/+/Ijxzv5QRWuv+w5vHj1gYgdC8d+uyeu9Mvcki0/HfJWkyoqvPZoc/3j'
        b'7qBrqjuZicu2jXjl8IUHlQt/3Bpz/PPQ3bcSKt6eCPya+davJydn5zJORg6QrXwFNzqnhu0/kKfzSavEq3349AJyVWTVxSDcUNs62VmL9/qz/AZygxxcli6yxM34nj03'
        b'Oz8e5CcelZLratzK47WZwYzZZk8M9WfVj/FMc8Ltw5llntxLwDfEeiPxFub7jw8ixocjx5PjtGn3uELmm6qs5YcOwWuY5b2EHB3LfFcLAX3J5nw9PRdwJiJZRnYXZTH/'
        b'ttoZ+J5k1y8ix3K9hn18iVwWGWXw/yNzfBBlghLZYJxc38HJxyjZWUW1l48HSr/B7NgKL9rdI3zZqVSTxM2VIneaS5N5NJnvz9IDvp9jrVysab6X4c/zcrxySE514vrv'
        b'DvXl+t01s/e+Z9ILPfDbV738dghlFEBGGdvw8hk/m7qcOQnx8Mtl6qJto2kl1FBioyf6qOOfYK00GNi+gY3SDLa/4JZVWCofuoXhVnkMwNR8wzRgd4ifjspEIx+ZqZy9'
        b'JbVPnLA+/4+2ex6GbjZKe/vSeXoCLtRyOR8JCIW4QWN5JjT2OuU1gYOCeCpY8oFcZLTvnXBOO5heMRcnNTmrsecViOL4wDkcClzJA9U+vdSPgQVKf+3/7eTiJPDlckFW'
        b'rrCgcqUgL1fBr1pQlAcIyvJAQVUetEuxS70rbBdXJdsVJqjbeKEQRJ0gV1iVjHkcU+edYHOIECQEM1cmTRtfroF8KMuHsXwo5PuwfDjLh+3SmPuIMWVAhKI+NqGuPlVq'
        b'IUKIpO5IUGP4Lg3ADROi2ph3NHuuTxV1cIqRnoiAOqlrE/WBjoRnqKtTP6F/i7o8CtrGCQOEgXAdLQwSBreg8hjmuoTKY4WhwjD421d6Y7gwAp7qJ4wURkFpf+aOhMoH'
        b'CPFCAvwd6FJCTXohEZ4Z5EJwnSQkw/VgIUUYDfe1rCxVSIOyIcIYYSyUDZVqHieMh9JhwgRhIpQOl0onCZOhdISUmyJMhdxIKTdNeAxyo6TcdCEdcnEMwgxhJlzr2PUs'
        b'IQOu49l1pjAbrhNcAXCdJWTDtd6lhuscIReuE4UiyWoiE/KFgpaA8iRBzhb8HLcyvY75VJ31k3roohZviG5VYnBREOhoiLhqm4lKcqIYVtno9fjp5Ffj76RlgwrqzA5L'
        b'pZb6/5lEi2WlKE1CARUQoU7RDFLbqLXWiyJfdyKZjncrDctMtU6zO8DgaYVbllFWXPBgSo3D0TApOXn58uVJ5sqKJLPTZm0wwZ9ku8PksCfTfNUKEIM7rhIFk6W2MWlF'
        b'Xa1O6ZbNzCtyy7LKMt2y7FnFbllO0QK3LLd4nltWNnt+JkBWiIDVHrheY5Xf3kQTpaq8PZBS1lX8Rq6Jb+YEbonMPqiJP8IdRfZ4By/wTXw0oqFiN/JNgMirOEHWxC1R'
        b'2sqbOOo7CG9xR2Q0wKyg7AvPxaJINB6t4urVcF9FrzYi+l4TMsihVsVRoOMGpaBmmlvAB4buNIrObmfSHHd4nXV+4WFyOhsFUUswiXWwkh6sTuJwTWKOXSWFiWNSR4/3'
        b'RSEBlIvsKiq0a+0N5kpLlcUs6LsV7S0OqggAY/M4mDHIHu1ORFfQNWyWCudDlINJ9PYko2CuMgHP8KKQEbQNS2UNrd0ijhMgogQHkKtr3z6lc/4gylLPNog6ejNqhH2U'
        b'm0tycymfUmbw6Xfw74EsKSWlQKdyh3UGS3c3TLUNNSZ34FzakwybzWpzK+wNtRaHTaBsS+FsgCViM6OOfY16mlhRj2e3GUf9vVdOCJQDn4iUTBRango3K0NFBPi+W/Gs'
        b'WT2IB//wbsR7AHj34RM7owybuMYGs9YIE1IJDLw2aZb412hMAhiPoV57iIsj9PBmfe2VWvozb4Du0dAPGO8BFiYBo6t3MR/kNY7L2FS41Sa7gTlfutXmFQ3WetBPe2jI'
        b'v70NqWT78866CtBxYSCkEdA21Joq6SaoyaGtNZvsDm2qLklbZjczFK9wWmodiZZ6GDEbjKNgNFIMNQmLnfAgfcC/Fv/tU//zPhyLgeCNBe0978Mxq3qPW6kf/KU7AlPW'
        b'QOUrkbiYV1TWmOqrzVobK6owUfO/VdwxhadM2gabdZmF7oZWNNLCLpXR/dQGM/CImTCcNujQDFP9EmYItzusIP0xUlDfq2UvLXlPkwysSUY6pk62zEWiQqmP1wAOY0p9'
        b'UbvZT6ORuc2OGmsHv9Jr7Ragn1I19DW6oe3r0fqwPkoVTaKxvScZJVbazcZcj5aMCquVBlzVVvmaTJxsKoRO09AtQVxutsGiXAZ80FRBd+YfYjzxipEUieSosx1EU8BM'
        b'5FW4+cmExKxsPdVVc+dR0wLZmkW2TMTtuYVlcTn67EQlqgtXk/vCTBaieuFq8gzof5fJjTlxOYk0Im57QgG+QY4VJ5KTPMLts8bMVlSryH0WVlUzMd+elJ9Ddi9XhqNQ'
        b'fCob75Ul4esytmOAD5BL5HyHuQHvx2vzqC0mPjex2FN5rgLEUTV+vl80k5qXTyWn7XFkk0XOdgAVuJ2Dtpwlz4mWhPXz8a0S3EZ2lZE2snva3LJ8UGALOXLdvjyTRfuw'
        b'hE2mDVIgGd6nIG0cXoMP5TuZZ+KmtHB7lmiCyJ2Nt+GLctQHmovP44Nkt2jkeHYZXmOPyyG7yA2q9ypWceRC8qhSy9ydXyAWJGnDP9+NaptcvC49rOXJf/4kND6z9D8x'
        b'X0Tu67O/X+yC4SXlI/rUTE85OP3qK/uyp7SPel//RtXj//n6TrViZ5+jMT/ve2LQvXXbM2fO/PmBCWr9isx1CWPVY+xjFg//6oV/6w5ddBwddCNw6TMvvbwuqWngyl//'
        b'5Bdk9aevlbUuWvhg1s/+GDPkhY/Wv6n567svfWDJTBh4cc/fV5wJ/8cTm7e/NXPKf/52dsTSwp9G7/iHaXjLs3fT11377e+/6b/4/qDX/15SeO+pMaO+ISejdDtC/+Ho'
        b'31K95Y0vP373q82ffjS4qDz98ABB14ftK9TiA4+zIEakVYXkifgsvsnhC2V9mKUidfXyhESymWxKziJtMhRM1qZnypT98DrREfByA9mGW5PhCQ7Jk0kr3sXha+T0RGan'
        b'wGeWYldCTn4e3BsSGMXhp/ExctFBeWAavtI3NzsfX388Pl+FlHJePfkx8XzcDdJSl8uaA2/FkAvw2rE8vFt0Q71KTozuan2pGyQaXyr0ou1lW7ExIUkXD5ikbGCYFEqu'
        b'yhqriLjNkVWEn86Voibg8+QitZ5swddYi6vJPhrmWIxVLy94fBKHL8dOEre027PwQWocydYn4U3JdFnRYPPZWq2cPLd4oINqxOOxC1/P9Syz3ELcliwusnhylzxHrirI'
        b'ujxymRljSHsyviv2k1rxNlFP2RcWCzw5SI4Mc9DlHIVPj88tTOTQoMH8Mi4dkPmAOOa3ivCdXD25PKzjiDHfiO9EMwPVSLxvWW5+bm5+Etmkz/UEL4jHW+X4rgJfwi3k'
        b'AuvpaKOCtBbgC3olks8y0e2aF/C2uu/hhvhDjhZGiZTQ4E/8mf1nGqVmT0k/mkAWiJUKRtQ7M5J5YNIjiGHMCqSRQmqKpeGcuPOzcoAk4XQLxOuMQrfcfpDfJSe+ykSH'
        b'Zki+62T3afY7b9hjY6AuKjF277nCwp2wcFggDHA+4U549mGHHr1XPvhNd6LATJGXSedbRImPyinAWih78gpdkkRAxQO7JMV35TySyb+TSNFJgOheYOjKx0q7CicmygD9'
        b'+LWHfVopX6f7HY1U8ujaMlNljbhbXmeus9oa2fZMldMmsmA7+5jHo3l5ZyXJXzz18RZ0mGzVoJF4nuxxg6Peu8MhYoVng8MjM1FJx2z3VeV7YPndH+pWi/5AzyaH0HBn'
        b'8+8tMOpT5YFSwNPZA2nA0/muOcYBNaGjxcLy1OfQCi7MHoymL91X9p+JYqjtC0CLjtpDQnjEkXVDyFZackbupP7SqtAiH9LGxAfPborIV/HFUrrzPo+e10iek6XPHY+3'
        b'0w0KupUPNGjloLBJSzItpf8MkttPQX2/eOq5/LbJGpwSNqv6t5ohTZMi+yw9/1Vp0NG5m29dixsfYtmzIaLo7ZvvowHB745xWDOtY37aJyB07tzJO//4i3MDt++POb1p'
        b'pGlI+q2Pfxz48siXhuXtHxewdfWUm1tfCNk5bunBnz43mex3v30r98gv/7z3wfvnx39QlvX+u1/cHbiopLh991+G618+wcUIh8/9Z87Fvzx/59vqv60p+WfLR1emxI14'
        b'IyHriYtTjh28t6JlwvPP9NdpGL0MIPeA7bC99/w46UyCa7xIyp/Hp/Ca3CR8UeMZCDkKnSurBT6yn/EF/HwWvkWOlTyENQBbwHfJfbb1kFoqZ9tLKsSTc1oa8SeXXGXM'
        b'b1SBkZwkp7sl7kDZ+xWLewOnqlfiXeRObkdcILItXPS8v0gO400J3sAVw8lzwHSuApxE0sqAPzYfnxeW0RM33sBAUXHShkWuAfq5p4M3AmfEJ8g9kS+fJi9M9/JG8yAP'
        b'd2S8ET9PtjqorrUI2M9xJo9mQ9P9hoInV/HmaidnSFbj48Nxs+jvcIJcxncT2E6IohRfQcrF/KAgfJxtVZC1XDHbJKklrf7+ZZNnsQfq6vDJBP1EvCsfRFApxHgo3imz'
        b'5eIr3Z0w7y0PU0maAeNaqb5ca5zIr5TiOQIuWuJMNDKGhu1niL4JGm6lRmIOUlX+XmdWfwbVQ5QMXny2wwlhPSRxUJc9uoMtrUFu3whHnWH76diUtDAdm3r0Uh0bfqkd'
        b'rJ/AOXi4ljVz0fCAwPvlPMezH/AjLA/kI5JSq6ArtGXuYEO91SDpwHa3zFRhZzp69/q4O8zg3ZwWjYo5vOeANQ/Dxq+M8dhIOj3nZ/nz7grnQbKRhf9v5m2ZTRzrDVoi'
        b's02nvbLFN3FHaC/QUW4VVx/tkAlcE8vTJ6tkoj0QruX0EwLM3sIXPBjl5ZV1Fjs0obKGcZkRQOSpqYlpxPQCZo0NQISlrqHWUmlxGMThtlus9WyW3AGljQ2igUkcEtGa'
        b'5FYwluxWi6ZZq+0hbrgaQ4PNDKzKbGDPz+E9ro40fBbgnIaXsxANK6M8Q+b3fJdJZwNGkUagpkwYBGrMXMxV8dGieQW6Hi7WFEe7pxc7CY3rsH6Jc9rlQwr04A2AthkM'
        b'i3jpMwrI19ol3useC8NZgzx4KDWmijZGRbEMhr2bFnTGKpWBnpM3sIM/HvAaL3h2yyuH0b9yD/RYtgaOAD4I3FF+FRuQJm6Jd0C4KQCdfjBJnEBehL61myYoDYZah8FQ'
        b'wUsMG8EcrQzxtoHe+15N4DzDwE+Z+n3aYDYYqh7WBnOnNnixIsl3GQ31LJAlvFUrtgYIBF8iEgt2JZ0M8ZkXn1Y9BJ2hcealBsNiXrIlimjs10B636+BXntgMBskCjzY'
        b'4yvl8WDvaTTqoccNPjjRAaq+81g8aj7kDCxFiWnfYzqqYdrtD5mO6u+LEgovSkz7PigBColh+cPaYO60Lr1O6HTEPWSi49SJD2XvlgpQ05jB8GS3VEC85+2xn4g7vNse'
        b'x9DdHMQoNt/Me9dkAhBSb+c9ZvmOEajvtnFAIkyCYDCs9vIbGIlAXzLBbndZHz7oR5t3lOuwfx99xNhTqsgqbe6eKvoD7MV4xHYeD4YNXOIPHA+7s8Jg2PDQ8WC3ux8P'
        b'DWte0A8aEVZta/cj4g9ShnxIFBWxvSRK40CMHEE+suuY0H0Ct6bA6sgGxmymx4PMQk9j85BTMAZDnRMQdqsvwZL7DxF74PugzKleDBCrdFf3A+QP0A9lpvgOkLYr8vT3'
        b'Dln/TkMmCXcUlZJ7gUrdD1eQweCwOc2CZZnBsJf3HBxiND6Qh0EL93bC+9gP60c/bz/6ddcPRiL45B/ekWBgoLVWq4018XA3PYnw9qTjuR/WlWhvV6K764q4ukf84J6o'
        b'WHAgg+FUN53wwWGrLxWS+7a/CPmLBR3td9Ae0H10aGvH9SJ+Fb9KJvVD1kx7JBOvqnynx62EMQOwoEGwjl3y7528o3duxfIaa62ZegbXmSz1gvlhsnKgwSDWaTBc4j0x'
        b'0kUBg6dnu1f28fbX81z38jEVR0W2F8SmhpGUls7SzsM4IAurVm0w3OpWDmW3HgU2sANszfcA22C1GwzPdwuW3eoebCQD6xBBcj5slm21bvKflx6gg9JnMNzrFjq71SsR'
        b'o6oXIoaKbp2D3PRSt7DYrf9n4kwAW+AmqPJHPtDCfFc/vWlzok5WXr/1T1fMEmQLc4BGzbxPOEEmyCnfioGmrKIrheqo/Eb+qLh2pBXDGqko+JRW+mAo23m21FdrG6zL'
        b'xb3r0Smi94azocFK4/884FOS3NxoWD0rPdPmVi91muodlpVm34XlVkFN1RYH6OrmFQ0exfShphAYBQbcYHilg4yoWeBQje9oSA+J40qHRJfcyffQ9rhUn73W6qCBxFbQ'
        b'vMbfag75qipzpcOyTAwgDeS41mR3GET7sFtucNpqbdSb2LaFJh1ejF48dau9xoggZpAV93yZOZ+p5bbNNGGUZwdNdtFkD0320YTGjbYdoMkhmjxDk8M0ocKN7RhNjtPk'
        b'BE0oP7edpslZmpynCY1jartKk2s0uU6TGzR5jiY3aXLfM8a68P9/vCI7uaZUQPIaJ4VAVavknJyXcz4/QCMjo7o4Qsp4ThsHv0OCVZqgYJlappar5Rql+DdYFqxQs19a'
        b'olGznwAolX7EzyVvxOc4O9lC2qiPJFeYi9SxvBPfrfBzkZRLf+1vd3KR9IRGrZKzIK1qFtuNBWmlEd6k2G4sIKsQwPIqFutNwWK9qaTYbsEsH8LyASzWm4LFelNJsd3C'
        b'WL4PywexWG8KFutNJcV2i2T5KJYPYbHeFCzWm4o5XCqEWJbvy/I0nls/lu/P8mGQH8DyA1mexm8bxPKDWZ7Gb9Oy/BCWj2Dx3RQsvhvNR7L4bgoW343moyA/kuVHsXw0'
        b'5ONYXsfyMSyam4JFc6P5WMjrWT6R5ftCPonlk1m+H+RTWH40y/eHfCrLp7H8AMiPYfmxLD8Q8uNYfjzLi86Z1NWSOmdSJ0tUrmXulah8CHOsROVDhemMlqW7Q+nBmtKO'
        b'c6gfXO68keU5uunzkBRortNj1O2D+aBUmuopGawwS151DgvbRvJ4irDIZh5/O+osIu7XmP13lqT9LH/nEKqd+RyaNVKiaxLPBgnWSidVK7w1+9VmtXkqtDhEA5/4qmd7'
        b'aGZ6fuksqQbjQ5wB/TLZVZKni0lbwcyRUJ24q+d7qFcvgvT0VXL2dNjMdED86jPZmW8pbRzzP1kGNZlqa7VOKmDVNlI243da2O9lL3ulOiMlLnTf3F7FUU5nC6Pcri/a'
        b'yC8JsMV6OJ6D2WCPcqtkAnA3g5jKWapgqZKlKpaqWRrA0kCQO+nfIJYLZmkISzWCDNJQdh3G0j4sDWdpBEsjWRrF0miWxrA0lqV9WdqPpf1ZOoClA1k6iKWDgU/LDFqB'
        b'g3QIKxm6oqaJPzLsKJqFHl8E0q58laJJfgRW6FFuG2cHStMkj0Gr5PX9WKmSltpGCirg6COa5NS2uUruGAkcXt7Mw/PTHKMEdZNctEI74mh5k6JZxqGlf5mHNkIPF2s2'
        b'cuxJo0O3DlrBhKSAAtstKhOMFRdAl+XS84JgTCHTzRncvMHwQGEYYR9hfzCicyU1Juqd1eHgJZqC493BxcDsLXWS06RS3OAUQ43KDBbBrTA4zQ4bDRgjHohwh4pxyL0H'
        b'4Wz0qLJtOk1m0IQ6JInhVAqYMOB/ZhLEPXEnG2pscNpAkDUDCCYIqNiugMPkVhrq7NUM9BJ6llBhMIt/2MnCEM9r7Eta8FJlDd2FZbFtTQ6nHaQRm5ma7E21NN5RfZUV'
        b'WszG1VJlqWRu0yCAiDTDe9tU5+jokDvSUGutNNX6H9mnEYVr6N6xHdrH1ixUw/6KkYbdAwydhhyEV1iP0rMKuK6zuwOhkTaHnTqDM1HKrYJ5oXPi1qR7ZkacCZXd7JBu'
        b'2O1mG62Q3dApRX8Gar5wK5csp18O9wl7UI8eHXSBze57VPQrZ6JfGPPY6BwrS92l5CE/vPg3nBmb6D4ZNQHTWPIrYzqNSK+DOEuy/K9Qj96o4aD0iE6ysZ0Beb1lp5Qy'
        b'z4j6JR0nN/ViGAWHVTrhSp0XBSDclqpGIMc+ZLLXzrNikAe2EHpobpSnuQ9G+ofSoo4EdVZHx8FaFlS012d72drrAW6sF65/DK2uYGkU00dDlZS6GT1D7e/fW98IWp3A'
        b'SiFFezvKjwieNcgLV9dN8Kz/G+hHBGga4gX9brpWDCRrd1ZIxz+YYzyFJ7nzSLGaemwXE57EitiGKZV1GuA1KqewwDbdRH9K0pZ0lFVZzBSgJDhA7fBAh7OPlxfYtfHS'
        b'OMXr4dLiYH89cbbi2fZovBjuKr7X+FHQ82DFeQdrTNc4Jw/Bz/QZ89KTIcno/dp4q+dWJHhbMcXv6D0NKGKu8D+E37k1M4szZiXPyphR2vvW/Lrn1iR5W1PMZt6HfUvu'
        b'Xx5X/05+SUnaWSzuieiFVbvc1GiXzqFr683VJqp69zoK2W96bmOqt43xHiT3eFb5NFfi0dq4krnzyntPU37bM+yxXtijGFm3WpdQyVY8SQ8Cb0ODlR6vAtHIKZ6973Wn'
        b'3+4Z8AQv4NBS73mZ3gGQevZOzwAm+1OtOlinpmqzD/I11DTaqV+dtig9uwDWdW3vQbt7Bj3Nf1A7QNZaq/0hauNyizMyex1l0fZuz4DTvYBFf8J6IdFhTYQ/HaxaG5fR'
        b'O4hSV/+nZ4izvBAHdhvTQRuX3ztwEtb8rmdws73ghogOkyAO1tNTJdLiECNrFJUVF/Ue5O97BpnjBRnO6BmTjaXjMb2mUh/0DCO/gwJ0plJUnqYuPvQ6bkZhYW52wezS'
        b'jPm9oZBS/z7sGXaRF/ZfO8P2l/GTtJlAEWaboTX1TP6zexXu7kK8A6Gal51ZSgO167Wz587Ua4uKs/PTCwpL0/Va2oPcjAU6PXMayqSoUiPV+bDaZhXmw6oRq8tMz8/O'
        b'WyBel5TN8M2WFqcXlKTPLM0uZM8CBGYEWG6xU4/ZhloTjVclxvvo7QB+1PMAzvUO4FAf8i2qQyJCmtgCNNlhDHu77N7rGeYCL8xxnSdN1NmStOkdR9myCzILYfhnFcym'
        b'NJ0iUa/7/n7P7VjkbUdMKePnopoIkydQrLH2XhD8Y8+ADB3UXIrBwk5FimDMHUYfX12jt4vzDz2DrvAncR2kjTqOa6mdqhPzoK97dzfmSuDsBczXLpbtAjIfroYB9Fo8'
        b'MUt3M+BX3gypgT6vYL55CvqmgaVHlJCqjnKczwQ9mFwsOlZTS5VXfhGFqQ6bWffCVpJObfsl7SKNA9A5NjOzNdAABjYj6tiKn4i62wAKot9Rkyo1yyS3BwQabCzzu6Me'
        b'nyv7d1Ymfd7pfpao3UzwOBuWirsA3U8R3XWwyjq2nroorl6fmm7PUMZK82PT0J3bo4ju1Fb7bLXxNrq55JZTw8ND/OrUklnCQL8aJnmJsGMY3TRFfLD7Pkf6NEUMpStw'
        b'0mYwM2Z52qJg4/ZwJ79ac73BsLxTW7oxHLDnCnTDutuBYgYNtmfk1nQyTk30Yk0Hwhg8uOIO8bdNKSXTlEri0OxruW6lZJZSiFYpOTNKyalNigUYcQf7GaSUkj1KzmxL'
        b'mk6WpyBfw5NSslipOwxWorFI42+QsgVxEurY6MeqbOy7TwzJehODzfYKJG9Saw/d6FIHy/nw1F6EzFB0DaLxPYNudE3lPQfpCA5Uy9QK9j0L0k7apgctC2kI1uUgco5s'
        b'SSjIS6I+7DS0f3yNAl/GuwK6RFGk/+x0C7Jjx0ngWxD7EKBMkHs/BKiQrpXso4DitUpQCWp4Vu3iqzjxA4DlAWIojvJAFo2WpyE5oDSIPREqhMF1sNBHCIcnQoQItgYj'
        b'3RGdUDfPAlq0ZztM7ruY6QFHSkwNzLnCwNFtYgNfTYMQyAQvs5Ez+d0d4P3+LlzWWQVTLf0229DONkcKzeC7x2H3+F5Ec2wf1VOJ2lNHZwpFt1/XyLz+UdLH4gZ0A6f3'
        b'Z95reqWIbPCa87qF1uuPsknCwFCuR2guD7TeCjnDeq5vY7f1eSebOit4nDI6qDWNsmkb/vCK6XLf7MMuHjYNXen0IzwyfGB2YZKMvrT5QO3MECWojCI/giG29IYhbnt0'
        b'DyWm6HtgwOvxQg1NHpcme7gDAEtHAJhL1hKZfQxcM/cldk2v5EtktikOhbiZBXnlERV16uM6vsX5INFXTK2jgQEqOiItjOrUylH+jwtWs3gUXjxqwEK/eA7gMQoP4kyb'
        b'Z1GKn2QfQa9G0oT5etD5AXbU0ADqsOeMQZAPCPboQxynZCZB2OmVbaQIXMHsbxfGyoYXnu8edwIl3PH61/jOZFe8oV85POQzl327A9ZVjPL6V0ayNSLS7CY0CzVzEmBZ'
        b'gZ+46n2BHf2FRx8Ppoc9qBSynV/KvLo9nuT0k3wefzr6ZSE35+iyxiA54mm1Eq1M7K7VDqvDVAskiO4L2afBBaXq1rqGafR7F3Zn3UPkGwV77/CjxoQ9VaDTdJZtOlxh'
        b'GKJ04EiHGMCkggROGn1bklc06CGqyRB4aJVMGnBguUrxI39qGXUIoQ4fTkrQcDN5jrQCDx5cQbmwLwsm18gmPYCaRS6o8mqIy48RR0t/7Vs5P0YM08p+ZIcU5TLq8kEd'
        b'PugH/YRAymbpp/sEDWWrQp9DmnL6JV4FsNxwIQLYrIIdqlXT2FaucFffKpUQKURBudKsYnGsxK/3qoRYei30FfoxxxCV0J/lB7B8IOQHsvwglg+C/GCW17J8MOSHsPxQ'
        b'lg+B/DCWH87yGsiPYPmRLB8qtqhKJowS4qAtYWZVFTKHNaOtXHkY3AuH1uuEeLjTB3rCCQmCHq7D2XWikATXEcJEKXIXjR7S8elDDfQzjPU0whXpinJFu2JcsVVRLFJW'
        b'QHnkLtWuaCG1jRMmUSgwGjIWL4tGD4uinwkUxsG9yQzOeGECK48W0ph2MsUdTPHP46rg5orcXKFO4eZnz3Dz2RluPqME/pa6+ZlZbtmM2QVu2azcXLds9owityy7BK6y'
        b'iiGZmZXplhUUwlVRHjxSXAhJSQa9UZ5rszASNDu7SKdx8zNmu/lZubZUSs34bKg7q9jN52W7+YJCN1+U5+aL4W9Jhm0ce2BmOTxQBo3J9i53TwBz5pEgfRtADMQl94Yv'
        b'lz80fLmHmD8i3La8wJkF1+RYED5EZU4H2VSYRNryaQTRjrihLFonPpyYlM0OJubps/PnZME6yKGnOumXSKeRdaH4+txJljc1kTI73aZ6bHzB58bPjK9+HBceZ8oy1VbV'
        b'VuhNi15866Xr20Y3jdxHvxxR01/51xm/0smkWAWL8a4gfEaf5UycR46LhyP7kDsyfIGcwzvEr0u04j2jCP0WFQCmQQSOkq34IL/Cjm+KAaM3k9sBnm8dsy8d4w3B4seO'
        b'lXit58Tio/eHeQ9F9p6TFH8mUEfBlZG+aOT/BWFFx/607QuadP8FCZn4xHDvY17IVylpokdBvSchxZ9f+MXk77YFlWppkik4/49RqhneBEof5hYXmhi0p+NjlOqNAYBL'
        b'AYBLaoZLAQyX1KsD5nu8t31wSY66+x7fgAL2QT1ytgavzfVEEgTcSUxMopFnWcxWvBffo5NcVrQct2Th0zJEtjYEkW1l5CyLGLtgIDnY8S7gWGHiXOlwdg5pAxLcnjsv'
        b'jmyaB3NvA3SVI3wbXwoKSSAviF/4q1QlDZbF0u/x5Sn7NiIni+mxfireKB4Qx3eeYgfEJ+Ct4jHzxQGRv0ZahIzG2uaGevH7fYPI02S3X9RZz2nxo/iWdGJchRaUqBrJ'
        b'WnzYyb5LdoBcsuZm5+fqSRs+Q87pOBRUwJOTIX2dQ+mQbMen8O6ELHq0nOxMS0nBLcZclIRbh+IbMnyvgawVv+13hLhmJRTQM8Zt+WU+B9PjkvBhbWIc2ZgcT6PsWnVq'
        b'cq2abBbPv+/Qk9O5pDU7L1lJLs9Cyhhe8yTZwRCSxbzB90eS0wl00BOV0LbbSInv8OMyS510f5+cCyTbEsQZIRcW+oL0wJsTx+KnF8WJDcPrs2RoEF4fgm9qFGx8yV58'
        b'ZbV9GbkqR1wMPob3w2LWRIjVr5Un+X6bsWFZHszi1dI4+hU7vT6/TIx+L57J90w7h8hxWTBpVy92amkdB8kxcgB+D3pixZPNeYlKFDFbBhO1L5d9P4Qcw/uWdwxdYkd8'
        b'/o6OlOANcygkHm/mEb6B7weNDVkmfgznWkgd2TkHxmo/vodWovyxExlofLOG3MfNecD0ryxfRq7jTcvJVYcShfTn8f7J+A6LUmzPN9qhdC79KkBcTiJgANBFBqh4fkhc'
        b'R5OUCO8ktwIRvoSfdlJ6XoFvxiRIn/NrTSbtJXFxifHQ1AI6KvjgVO9nAfAafCYAkUNPskZF2ccFgXhy3U5uLsXrFbhtuS14KXkOoZg0GW5JjHSyg/NrVPj4wqmklX6Z'
        b'JDEJxlaBwvFuGb6YR0TU3zlFPqOvLIx9XXLPlADEwhGRHVnERT8UiXeTTYh9KnKAyTKg5Uu5fQnwpa8GP1VWnF1ApocdGmT9MnzHhHPv/ES2gk9+NeAvf/hl4Et70DvR'
        b'o/44Y/pn//Nty/7JhR/CApz6xtD/LV5WmPi7X427oc46b+6zlzeFGKYfmd5aUZ6zK//PkaGRJ/dcDShWKcofS+1Ts+T20ldHVYd8Isz9Mmur7Z1/vTZt76HtNXfT5+xs'
        b'Xjby7zvSpnwV/uWXmy7sTvm1pWLEhNFvH1b1m1uU/uXPLNMUz18P3NXGbSi/ODzj7ImXRx47zW8J3974zeAl70bOubzN9ZefvpIW8s2ef8tf3vPNG6NP/X/sfQdYVNfW'
        b'9jkzw1CGJgIabGNn6HbFSpM+KMUWlY6iSBsGxA7Sm4IgoKiIgCJFkSaKEvdKbnruzTXxJiam9+QmptwU0/5dZoaOJvd+3/M9/3NFYeScs8+ua6+19lrv+/ykpucuTu1d'
        b'WYmeW6b4y93JWuMbL1+ZP9GkNfjZFyIP/OX0haywv1y7FbriSuXGki2dJwtmKlyu/HD7wEsvv/WT7y5lvdvdOd8GLP7qZvdry6xDvvh6119yG8Jvei7+amxcxIrtpiB2'
        b'X7qytzB1/fvhL2UUrJxa/nXVjPe15OPtn43qee9S2+0tvRY9qXN2e5unfrrF9u3wNuFb62p+mhISlfee54/5B2Uni5a8MVE2PYkM9hLUjtIhEy6qtsYB+2IVVDGGxxY4'
        b'jYeakC7JbS3Ge4g4CbokgDpXVJHEYKjc9w5EZ/Z1YejMlxIpGAKcRufwgshPMTTQS4QOBXQmGYg5Ux7VJQgD8AytoABIs1ai0xTdR4AFVXcy7wSXvCnSws5kdAha8Vd+'
        b'fx4GOGnO3t65C7VTfs0CGeQshjZavxYBnIudQKs/C7KhHuUbJUNnPHQYiZX43ZJxgu2QbklBFXxRhraKQuIiOqUCsjiNVKyZNQkobSDPA5axreOloq1wCK7TisdaokJv'
        b'wuIgQG16qfwydBEdZYgMLagOtzvTFa/BPCwvcN1FS3jUiqVJLiObyoT2OEo2hZ+95r+Vt0eXXJJsOUJecQWOK5L1E5TQZYTyUIGRjoEeXDZKxusROlP2WibgVviKxHh/'
        b'atRheBRdqC7W2hYKfebw0LmUE2/koQlyUCnD727bgJog3wM1Y/1jpvl+fjXK3k05s3bvQQWE8zIfNXn4IrwD2hFUcwsx3o06RCnoMEqnys8+lAk9lBuT0BHl26MGH21O'
        b'skoAx/GumUGbGwCVqElF1qkWCuNDzH1EBj5TGI3pFdQ2BZFnbTy0Ym05cYhgWhyUUogqEzsjfIWJMyzWfbU4iZ8AytxRB8ULwe/OhEsq7i8/yF2HJcgR/BK8f4q5KVAn'
        b'wjL0uC8F9dguR9lqkjD5GCjuYwkrhEyGqNWCji2nGF2FPrzbTk7sKRiH0iCNTdZaVPA4hfy2tZP7+FFWVp6zMI2AKlECnpmX2NDWJ28hjJ50T8nBs5HsK4YBQt8gPJsZ'
        b'CryrPSELtcU6hucKbyGek3kCOA89wDCrYuZjQZ2+AN/iZeOJlQZOZ7EgDE6gFjoodqH7guzV11AOIzi19rQVcFaWWlgtqLdns7NryiR8l9wG5dqvdlOJdy3cH11aWig3'
        b'kGm+Zx5H5TMMaF00WCwmqEWIJ2Upqk4iQNAxcXCMrBCsoKNzeKJqlHSUi47YD7RQrfFGUzhdD53xd6Yz1SsYq8LsWWhLHfQoVghyfGRizofTxhO6QEpZZlEG6t6uYZnt'
        b'o5j1RdeHsMyuQ5eT2FZposPmB1I/Ica63UZzLA160fmU4RXv/zxrKnUcUAU+dqgCv1yP1yFEqQIRP56gmeKf5vx4gT4vYl4AErwpMKZI2RYEpktgQhPu9AV6QqyAC8T9'
        b'QkXJcZm43/+oq9hskGLOfMTMNtBTpSupY4lFxJuWSCZAIiE8vSsJD03ShAWLFeHbI3dFDgZW0X40lDM/XlVo4lryjRZCX+RP/kudNWv4/v3VNYLZ8fwA7tXhW/eoNGDa'
        b'waxNo0GsarzgA1/1yO5vlYc3YHR39QPNObElJSpRpz+w+klVmCeDqF0fLRpWxXojCVZFMQWPSn7zq6YiNsNFPkUr+ur2Zzg1yanxKG8nVhx7++RAGvJEAp7+HWZZ7eBw'
        b'ZVJcVNQo7xRq3knpTPH9tvgBKQnC7wu9IvWgYct/qBJRjxSeINZUwIqGJ0RHqeIRdpH4D9zjkbEkiyTiz7z7rn5wvzU8SiV0NZWgwVEkMGIbQX/TRA7+8c5/GHqxvuaV'
        b's0dGLx74YtV7qTDVIP0RM1UDB888BxzJa9nP7xHv46jngKeeA+4AP5wXSu3DHowENzxLqw19WxT/iBytUTLRu0p+GDRB8mcAI9DAEAuFVLE9ThkTQelaIxMpfLg0dFso'
        b'CcwYtiwNrZJLTGQoCVGSutKEFDKIKvxbGtenQgJXBfhED4+fqwIJDwkJTFRGhoQwMtlIqdXOuNikuHBCMGsljYkOSwzFhZMgLjXS7ohEf0lDVjPBwled9jO4QRYcltov'
        b'5urhaOkhIatDYxS4hkOB/mgmFdfvDz9kiIXy6GaJSKQgum6FafvnIc+E6dwriXonhud06vnbE/EcpsrhevvVQ9QIcz0tokVEjFWfwQw69RFFbYtk4GaUxPLgoK/Je2YM'
        b'2E4U4THBtF/7DjVIASNxv/JqLM0+0DICj28sUp1jD9ozD3Hf6PfbNZWu+A500sl9kHcViq01jUR5W3E74Thqwxpcrh8xlFAnHPOmxhZchi4Dh6U2/yHOWBZONcgvrDn1'
        b'6u8XJopBMuSHDFQEUQauYxFxr+T6WHnZoIuBzF9EfuHnQzmgGlGuZInVuOhQg1m8guiTa4qzPw+xM/ks5IUwy7nZ5lahPtQf/EXIJyGxUV+E5G3zCtWJesdHyB3X0xmz'
        b'5muZMIm44aBmz/5hlFCVBopaJvUpobOgniLJ7oI6yBgEtgsnrTWshHDMkpoQuyejSmxB3LQePNHINIMsdPWRfMV43ilU8858uHk3lR47Pnzu4ULU7+uD5x+Vw7XvNjod'
        b'Q/B0tBhxOn7S33esJBFj6DycmTPKfPTVHXY6WsvJdGydYLAM261nZALm/LsyAZXOc2JzVWTEo/PEK6/yCxpt3Y1a2HOieTxqQ82oNfr+jBe0KCHrbbNXdm7zCPfB02HH'
        b'uxcit2/bvi1mm1e4PFQeyn/z2M7xO8YHbPjY4eh7WvPiozjuKRvd0H8Eqw83+zvTRxwfXU1vjzxI5vp6xqI95sMPkvptIw9Gv202FI+C0Yij8K1xf1V6hPf9B7jK1ciG'
        b'D1nfWBxPcX1bS0Es3Te2xH6Ol+ILYduj9KPeeQHfWlv9jeDJVeZYJBPjE47DaTe1BameMJtdRrc9oWXIUA0KsxhZYFsOOeGg8RYjyOeRuLnJO6aOOB7vGo52ojIwvuPP'
        b'6iRDzk3In6Fbo0geGD3F4gWRgvy6J+RT71A6DIbrOJGMt/Jv7NPnhsYdnOFG60jrITYbCyZ59J2OlD9jxE58S380+3BQNOe/04uPcJKJZ/TMNwpECqJEdL/UYB36Scgz'
        b'utFhm59oP3q2ck5F2jwDbvqPwq93fYm3F6KErNWFUsi38bQVLNjIiVbxqAOKltD5Lp20avBsVzlLquHkCPN9N2RTr5I+aou1RulQQt2ttmJOB64LUDHKRnUjjKDBqEvB'
        b'bqjVzSJYH3kESfmzRxzBN0Ydwb5oWW7A8eJEde+HcfR4kZzf61OzQH2CL8geQ9WSAef42VrZj9FjR4vsCdkToyZqjh4lox49DlBXSEyX6ZDBt5HTszDPWLjpDW1Qzo7D'
        b'6FkY5MxlZ2Fk40et6Po2SSJ0QAdqhRyjBOKtJSc6xqhWANeMUpVLicBLQ7lwgx7qeOBh9ENNQ052+s51xkEFHmbI2i1BHUHTZWK69W0XoWYFOZNBhxdycJRDBXhfLKV1'
        b'HHsQFUGbUkxCOw9zcIZDxVjjqKT80xFwViSBTi1uUjQHHRzeSSsS2bnMVaiB84okntu1h4McDmXBVT96dLVS7i7B/YBqUzm4xKEKT8ihRW2NQp2KFAG33peDEnIy3oxq'
        b'6LlPOa7tfPeJ5Ig0JnKCPceYJG6u2k0OuUScOerm4ByHjkMXKqHv1sL7djltDFwbxxqzY41yAb6yD66g67SbBvUOXE5KhPYAD2viVWdHX0dRxd5Y3f1+c+iZJHS5ms2D'
        b'o/McRBwPZ4RQw8EhKIQ6ysMBN9F5twHnr2rIlbVr1qNOZyib5xWgzQVBhRg6rKYrycJBZah7AgkcmsPbc3PgGrpAf70eXVwGJCDMfh9ugP0O1Bvz4++///5EuIjbrRxD'
        b'zr70zy/YzymdiUCAI3JvzZsgx4OSfBfaewVZQi6uQoClDI6s9/AkulGBL1WK/EnTxNNQU6zBllnoptIFF7Mf66DHcO0vo6OQ3/92MpeIQmXvp+ql/iDkZAo1ouv6cGUJ'
        b'KlaSwG4JStcxwPcXG6BDDjpacCgITouhKNBgtYmFzjJ/dB3dgNNwyc09Yttu3ahxCXrQI07RQXm6fvroMhyGWge4sVc2BXKW2sEJMSp3kaG2FfOhcjyqCA9W+uM3rEIX'
        b'oUUL0iDNgJujI0yyR5eD0JVNUCbG0z8blVlhXf8GHEFFgROiD6ALcGgCurFj2gTUhWdzJuqM2gsZwjmWuBKFU6DVdazvioVUUtBZVrt/Ai9asUPEGYcsP+bqwKhkN2Gd'
        b'u51Qyap5ZKM3qplk+44++5HJtkCXJDxyCi0wUeDBScNmEG7aHdZeczklQXPDHXoSlZMmVOpyUn38Yd3WnagENcE1OMvPwXK4buk8PBbHQlCHwU6stZ4Img3nNuEqHzIL'
        b'ROmRKGcbVMNV7e2oxzh1BcqktcTP1pDwL9/BdLcCaAnwsPXSMjEjQS+oQYb/kpXVqAtdG0SBMl5J3fklcHwuCZshG0brGCjytMGiAo/vOB2RgySCstvjYS138LaFI3Bd'
        b'TY77cGLcPJl+NF73bUoyzaEWlYmHOTz2R+Xs/HjQ4TE6aoDrRwSG/WMLiKbPcwJUxK+1dpFDM7VRDy5QWnvgniugsT+PY7lp7+Vp629JYwOGxAR4YMMvnqz8Nf626wRc'
        b'aqBRKsqcrwykjUN12uyo3nOtKnYDinxRDbGx1nn4+NGG2q3VSYbOtR5evnIbW3kQYxPuFyhApTIU+I/BGye00CkwMU7IvbKThLaE+IRFL8fbHEVlWm4GLd70GMdbyEGD'
        b'gQ5cFqAcuOCrJCye6BJ0mgX4yXwZ9HzQ+kHxKKR1HJ7vF9EhyA1EF1AJFGyWYhv2Kqr1mIp6PabOQ5dE2MyBNBNUORF1s8CANLiON5E2aDPS1YErRtCWlKDkH3flTBVC'
        b'P3QhkgrVecaoMoAIKyFHTvqq0WUOmuZLKc/Rxrnx3jJbakXLca0sVWrFFqjXhPpvkeqgdCzXshlpcRMWtr0BqDAQCgmLEBYFWlY8OgG91iwM5KI3VEiSDXn8ruMcZODt'
        b'rXE9ukZ7KBFu8Liu7QpoIxj9zagb6njbDShNNobuFbH6cBHyCXNwpS6/mIOirSidvnQHnEFX1OE46OJYa56TbMLLAJVPpQWHoBt4M+s79dWBCh6dRCXedOPQW4g/sbPT'
        b'rTzchHR7a7jEQlLOLJ/NQhO0ONFk3DPHeFSjD+dUhXahLnWoxwIZuiji9I2FZtPjlMTE94HSDXjeR3rIqIlPcPnZeaYWNwsd0oqCnBBKvQTpW1C1RpzznCMU4doJcH9m'
        b'7aYhO5NRNr7AxA7K8ZZrcfrbhEZ4U75JK78cTu1XExLAtZmEk+CIP6t83QESF7d6oq2cnjyKtwjMoAJ62EZ6FUs43Jn0jFa0cA26zKMGHV0Wh9SWqPSmlNS4zWchg0fn'
        b'UHEMvRQZC2dUdNWiFVhVyOZR49TVNHboMTzuJap6ylEhqjf0I6tbi5uKjmnpYpW0S0lCZyEvAvVgaUDtdZSLGw3t6PLQTpKjNG04uhSO0L5GJ60nksNzGdl/8qBNd4kA'
        b'1cFhdCH6yeUf8QqCfBwWv8EtoDv2jVXG97acrnF9/Y7bc+42U5YU3y1bKXXLk3o+VmtxQcrfqg6046e6pq/leKuAq9KDUuWK6fHFjsFHjeLLuqyXyGpPpX771sl7r888'
        b'X3lhpqd/oZXW9coT9s++PO2H/HGS7M3yeSkzrH7yLFnvFbH1o2PS39ss8v3Tfl+paP+7/EtT7+TPq8doRbt7/2jTUSNd/5TzUtOP7mfHeS99fP33G9YEPrvZ9O1DXa+/'
        b'8W7491culyjzHQtttuR1SC7t/eedMU8V1to57nnz9taZz/713nvjXtl7d3/8i++UKptQY/j7a9883BpntfQlfva+Z35tuPjKavN/vPn+k3uWPDPrnckb1n3jVPab1bur'
        b'fi5785mf9gbuqZ/r/foivctvx/s/eCV45rzyB3WXfnWMdb23y1U3K/ds3AS7O7vKnb50/kFrq8sbddvejI54+fHqXLelz3xZ/ckvjb+usr13553Xzs6Z1HJlbtm9rydZ'
        b'uXeaTP8Zvg6zN/IR/VLx/r3K2zEHz+U1/tNg1zmf0P3P7n09LffWJy8/a/HaL3rPuYvf2LFtjNFnK04t9Ncrqk7N1F3dE/zYr+5fWnzxka3vOw7VbR2b3NrSIgtsz70z'
        b'5v3T64uf2mQeXvTZ1Ppvn9A3cOzdUvDJm19+r7M1NzW8IuPaT/JxSdFvac+uOB4sdly1/MX9i399cuuUr+SLV//2RlPk4qVvpRZ8fXCD5+Sa98csj4748PjZ5Z/f3ryr'
        b'Ksy1JqbV/V7ahtQ24+VH2sZKSyYlJfxz8gtJb77g84Fpr+7eu9nfdPxlkt+7CYfXO5Qtdjtx6tOjS6891frr1lnfFZy+tLeuoeof/tm7/7rr3luLv73U9ETB7g1LxA32'
        b'899b7Xn2jaxG2Bkq3xD82RM+W9y/ct35YFxrudbPRzpkM2lkA1ZB0uz6IhtcUZYmsuEwOkIjPLDU7oBKFpySzO/knHzgBAvgKEWX0GGNFIp2tXeDi+zA+hiUoTIaFoO6'
        b'Uf1AQo5xqJaac2tWQK06qkyLQw1wWAd1CAjdyHkWqNCa7KOWj5MWqsXjoigaTbFgqXc/2Yi3pLNYOG6KYeEJXTOi1RE7qMJJE7ID51A9o/XaYGQNJVSEyfCrCY8Iqkug'
        b'5fr6Qbe1lZ0M8vBOYmqku5Gs2WIDxrSVuRllWENzNCGry7XB0gkVCWzRlQPUuS5HN6HM264/5Qs6gWqFMVhnuko9qCaKSSS0gmgvfkR1XRXIlFcxN8VbhPWmSuihDRfj'
        b'nbLMGspRvqoeYtQkmLdLm3a603ZHa9TlQUN2WLiOALUnkaMjrDlmmyhQoU6CAVxRkIA6I6zknoa8fqEzNHAGOsTo5p7xrK/yTPl+zsl9Y4ir1sRTiKr37KVDORtrQ6e8'
        b'1R5iP8iLgm483mMgW4gKLOAwo7w5AQW4bfZ4kG0puaA2Z+SHrk8Vbt8MZ1gEDZ5DTdZ+NlgQYuMDNaM2fI8EbgqgayJkMX6XLGhYplE23J2ZriFcyrjjerGudV69aWxw'
        b'J3tGrRmLTG7FF0/3xXAJUjVRXKZQxWJvstaGoXxHqGJRLzTmxQOVJRFtAVqgdq7KJ8H5jRbC4TqB9shMcfyQkKGN2HSzICFDcHN+Ekk0nLoJ8vqFsKBC4aAoFmyRtLBY'
        b'mWZUIra2k3mpuXSM4NBqqBbGSRaxwOzcWXg55fsSZjgbrJO04x6QxArgpF4S7ZlFYtSp2d7gSiLe3aDHgF4Sz57YpwmgdmesCEB9IJ3LlkK8L6v0gJ0paj1gNxyntUfl'
        b'/qgZawI7DEfSBDpQNVvp11G1Ja6drR1W6072hQyZQ5bIBFoskwh92caUbcM7fdQOH9QVO8jnE4bXAhE+kJ+S4u3jiUWPP78enbJCh6GchkxhuVLg522j4ryDE6ie8t6J'
        b'0HmZ/r8T7SKb+D8Is/rHv/U53I0GoUxSv9bfOG6oX2sucb/qUNIXY0o0ZEzo8wQMPk1HBaRmjq+Tq8Q/RWDaCNS3CH8WqXiIDdk/XBL5ZII/kTJMKP2eMYnZwSXo0xQw'
        b'As5G+O4N6U8SAWSIyyZxP3oCktzLvvogZAW4BAH9yb5IAi8hqdFXlcVy9TSeskHN7h/ww4JxaC7WWPJtHI31idytiRPol9rU58cz+18bPXW4kIkmy4rUkNLtsEqN1cQM'
        b'Mexd/F+rEd2JrzkPIBQcrZNkPM3sko9yrklONnmKl/vwc001m+DrgmHO/52ikghpYGhMDEUD7cfBiysVTWoTGjMAJJSBSUVEMKy8UGlsZMqQQlnciGVIyJpdSZ6xUSEh'
        b'0rCYuPCdMjsVoKs6okCpiIxSxpBj/dQ4pTQllDEZRkQT8sGh/MD9KxEdS2+MornwqvTJSAXLqWT4fVKCSiSNjlA8Ok8gSeF3lHrSk308/xTRBDQVv4ec8odKw5WKpLhd'
        b'rFhN0zwjQkJkBOBlxGAI3D/q/iAfo2OlyYvsCO20M+7GFNKZSdtDkzS17Yu3GLZEVdsokisNDWJRDbgAgus6oIvU2anbEuOU8RTebdgScdOTosOVMaGJLG5DxRLPkAkU'
        b'UkuSF26DuwC/lgKGpMbj/0YmhdvJ6CCMELdBOjQpUj0uqnGnUVuxgwkhVaMfEUdzY+MJBvBwZQ4YgFEIFXluOEJFPTk1XZPghJl3nwc8Hl0x3KrV5wP3jYaavgSCQqfw'
        b'AfkD2+CoktCQTZlkoQVnoph3UKojJP7HawkOUGox2WPszIT9cMkfZaJmF1T6uLNnEt7Pz6LLOsvlNpOgCtu2Va7o+pQ96KKxA1Ydeqn35p/uHtxRjnO4bxmm9/50a045'
        b'm2ydvag6hlrLAeg89FiSBB+SgELyfLS5aTtE2B6/DDdpATn+IsIdLQ1J2Wvj6RrPRX97H0SKZCKFgj6f+dwNg8MOpm7v/ny68KfHpC4RafNjeDODF22PRh91qZx/NjUm'
        b'NM5ixrVzfk/PnybJ3PSd5JrRnaN7bl/4tHvpg8ZfhNm/PHn/yxc/vCjN2jyuyqH2ZbuVGa9+dvvqIv0fun0zPn3zxJ4nve4U/UuS1z1d3P78lKwVE85MtZZJ6CYfpIUV'
        b'B7+lvirrRG2acFhNocrBCWtQRc0nu0Ax72QDzUkkYwVVQRM6NUDn2ILyHhbTmwgtjL7wVBzcVBBfqS3uNHRJznxGY+CoEF2GdDjCFJAus1iN+QKdMzhmvbShTma9XEY1'
        b'j6si0mk4+mk/aLKABqqPona4CdXqiPT9wZDBr16BjjM1+JAzqrDu0+9RO8qzFaN8qmhLUlE1MavmwFHZQKtqArqcNIM83oGO2uBOQ2eheXBYO1VQL6OiJDI90HEoRml9'
        b'Oup4dHpIpPUVOKM+9npYvIYuSZSjq5UqJpbDKSYHucVEmSBKBlY2hEQBIarHoBN7TUEDeRDNB+7iw0RumA/cTSPxf8+R3VQ63G56iHvbZOSoAU0dSOgl3mSC8S6jQQlQ'
        b'J4+OFLQnzBGOmDoqpCEEond/FA2zlQZExqpgPAdihysVbGuNpMINS2I3Z0+XgH544CPtR5Fh0eGK4PCYaFwK465VAyRFEUDD8O129A47N/Ldhd42Esx4v1JV/eFIw/5s'
        b'NHF/BPhWEUmrGZcYQX6BJf2wklgFmz5iHexWB/mEUFA0ZXxMXGiEuvXqDhm2UIKuqQE5I5uEKuZVoYxOYuDlmkoNvz88tFYuLoEhNn/20aA//ajnmj/7qNOGTX/6ra6u'
        b'f/5R5z/76Aa3uX/+0Xkh0hG0qEd4eP4IkZeeUYw7hek0kRE2UivV9LcaEL45ML6Uhp8Nr4SMFDW6OjGUYkj3zeE/EiC6nqitTCokz7NzGLBaaGArw25lywm/MDk69M/1'
        b'lHNg0DBV6OO2JjKG1YMtt+iIUTQtEdePn1WjaY1l1NWix8XG6nTj+jHRqnTjk+tQlRaqUUgEJKWX5JSWwGV6OuBlirqgAOVBm4ODgxYn8CSZd9mm9BAGtcLlMGu5HT9u'
        b'EydAx3nvtXCFldfjA4es5V6CDagXX0nnF6N66KHPWMN1U2u5J486QvCVHH4ZpE+Sidh5UC7qhTNrTegZFVzR4oQW/HIjfZat3PY4XEW16Bq+eDkJuvD+DmX8VNS+hOqP'
        b'qHjjPMXcRAEq0uX4OKxEoJPoBL3iF4sKXJwV0GmEty8B1PNWa6GeHrRHOcE5dtDOLfK0hxZIp7UIgQuoA3KTafiAKhCiHDJlAnZYUpSyAHqTB1TRBRdIVAyb6bhrSiYP'
        b'qmGpNeuS9hC4AZWb+tdkiSqDNW/TKlJ5uAAXVLUv3yATsqiD00JUjYoG9okEOminkJCdbtSArg98JfRKWKecgJYJ6CKkSZJ18TwQ6vL2CziWPNy4ZlrobolBohHHCW34'
        b'ldPgLAt/TPdMIo7NNmiXGPKcUJ9f6Y0qlRtJYec3P+ZNlNwAGjhLTnCx1kuSmEv2Ya26ADJQDypFVYH4P6XQA7VQgtXqUtRjogVlYVoG+JsvVvO6USYULJOOxbqhiRG6'
        b'sAHSoq/qXuYV3+FXtP7oF/S3pfInHYzF71QmLDz5xTyJickks/PvmEcvfmJ7/vjuy5ad8Za7PerPVdfGOxqmXbjQsIQ7X/2e35WnWt4s6P1p+fFJ3WezykrPfFC1Ka8m'
        b'QnJwjMdTz7W5fm3nP31H09fyeU25Hznuf74k982ISV0TX3t7e/Gs1z5O6xIceyb67tqd0+osi6Z5OJx65YObTzcc+PjmmrILK35+zLGt+6DblYI3E3wPv/jy/uwXDWP4'
        b'nw+96K5IOWyX8GDcq+j36q43P5Y1f9/w+dSOK984/2Z0c0XF1awrl6pf/fre37w/+ejH5E/Mvot45Y2A5geLfri36nHFaqN9R3qbGvb9op3VuOUNo2iZKdV6J0I3773P'
        b'qC+dnDrl8fw8x5yZF1A5nvrnoGNgvmo8YomBk9ANdMHaQtkv1U3fRqgNVSg3iYw3Ogp1IUSjT8YzTJDMO62xoAqzATqF9eVqW5pNr8WJUAYPhxM3sXdewnrq1QRyWDog'
        b'0XQsnKBVhvMJ6BzV1PfjG8lZA9XUH0dZLHW0YxJqtSZOe1+oJ6qvDuQLUJrJCna1BevIGQo8kXl0eiXHQz5pYxM6y/T4K5COqlB+/AIBNEzFV7PxOpwRyZJOj01eSq6I'
        b'Jy/AF/AELF6EO4k+lQPtyeQSP28SvpSLlweqgavMH19uhRV+dQJnKDqiSeB0DKE2TzwUKxXJhvy4FRyP6jk4uR61UbthHToGJQosA3IE7lCOyz3KQTsUJdJ+3Rn0GH5I'
        b'ay0U4afOc1A1YRqrSst+KMArXR9Pc1JgCwenoDCVudxvQtF+RXICj/KX4EsVHBR4onLWtmp0bAm+JECVDvgSNsjyhOHsPKnDNEFjOtEB5merLCdzVD5CouIoYcYiBdaJ'
        b'qUWxbniLIoTYEMTlSBiuRSoHJ0H+o05N1Zc+TSLUE6hdjJp/2BLR4feMGRgxjN8oV2OO0LxC/f56dGLUQEOEV7chWmN+RGkSALfjT7dGsUFuDYhcHloPXLqQvkRO/o4b'
        b'BOR0VxTs5ym/Kwl2CfL3d5O7eLoFMMhKDcDTXUl8aHSsKjuQpije1etLn1MlM5KbB2U0hg4EgqK4UMQ7SY0q2irWQRb/l1zkifbE4hOqoNt0tI2FZOwNhYZa41cJ8KdH'
        b'xpMUGBvrCwwJN5lo4W4d3nSSDs/QMrpTEyVSVD7wJIPnLNxF0ZAJJwdE0eqrfiqs+IFUZQSriuFUVYlUSFXsM8Gr0sVf5DPBrSKoVez3fZ+NCTBkxFj62TTCTPPZPGIc'
        b'/jyefn4swiJiQsTEKgkhQcsWR/ERkyImZ+gQYMpS7VI+QlKqX6pTakK+IqYUakfMySY4WGJsv86ImElxnbQpedjsDC7CMkJGyNHIc6WSUkGUAD81Fv8zLjWJZv8zwaWZ'
        b'lOqW6kWJIqwirHF5cwnGFikxWzfbINsk2zRKhyJTkZJ1aeSqmEayjokSR9hHOGToECBMEbdJQkO65901IcvAhVImUESzqMjEB3MHaJFDb1Bxf/W/6YEdVkkdoxVxjoqk'
        b'CPpzroPD3LmORLN13K2IcCRLw87BYQ7+h3XmeTLhXZHcz9/3rsjD093jrijI330NNv8Frm74uy55ZbCf3GcjlmHE+L+rRS3Ju7qM4SIaf9SKwvaw4o+8dg55rSgxgayn'
        b'RPJNQVaoyFMewMAN/2BZS7DAGlhW4h5aYIDrOqcHztuTkuId7e1TUlLsFNG7bYmOn0hyQW3DVZl2duFxu+wjIu0H1dAOWwIOc+3w+2SCvvLxZwKvlehOE4Lv6vr4uTj5'
        b'BGPV/8EsUmkXZ09aQ/xzTWgqEWj+xAOsSMKF2jnMx9+xbEtgycQLWHEkvfCufoCn3N3HLdjZKdDF4xGLmoOlb8KAJj9YNOhBl8Q4hcKZ2iQDy/CJ2+ar2EZLmkNKEvSV'
        b'hGt2iJRlNKg/HliM3KgHZsN2nkwyoBQy3YYWO+gXS0Yoa/Cvl9Bfj16rka/NeWD9B7rnrnZEZFSoMiaJjhmdAP+RHIQhWXPDZXJQs2zsXrEqEq94PvEEN+6C9Oj2WmeW'
        b'4ZH0UkVOmyrHg2Z46GqNkuFxV4dwkSbhmT9yDhP5cmdQpQMljp362UdPFziCW7Ucf1JMG14bOMQ9NSBlYLS3yrTZ7r1mmC3cX7OPk7n8KYnqDJQPSDLQU3fvCk6VZMCp'
        b'GTQZelmUniaBQG/EBAJ1XnC69jDOTE+Wnxu9J7KfS5MR4bBjJiK1R3FhBqjpaqXxlK6AqjAKx6E32koHrSypJRbZo99GVtND71gitbRSRJMzq+RFdgutHqFItkClli4e'
        b'D79ZtWzJzTbSh71n5KUttfQM/ENPzBnliUcVA6SIwZUeyVus8ngx1xBLnVZRIKlB+Ed6kmyw7LHB0yY+MTouMToplaHmWlqRbZtQS5GN22p4B6IV2c7JPWRztSLeYiuy'
        b'K1rJ7PqOVRfazbVzcFTdMnwxfSewDvRWVal9v15If82KHqlhDMpB1bRhYBpY/8xWUKSGEbuHnk84Dsy9p4tseNAFVe78iHXqQ1dw1JCrDoVPIFAGmkP4Yc7YyR98jTLh'
        b'EQc+dZzSAIDI0CQyoRRqlrB+WBTkCHqEBH7ifMXlpIQmquIF+pE40N6RBkRGkrYqY/oRjw1blItToJu7n//GYMKM4xfgFkyoUQJoLTVn9YwObcROYkKI9Q+lL1LBmqjH'
        b'TW26qdzGwx9t97mS6fEEK6HP02s1SKZYjRgcQEconq1TBSNTGyRirFjr1LdExw6PLsBwKrAKq+aK3R4aK3UL8h/BJR4rDUiJTtoTmRhDBy5plMozgTjCWsILxjMpNCaV'
        b'PjiyhLMaec6qADbYgPThbpCZrxoSDQYHO50aoUVJLNahH6z2gGcHoKeMKLVoSUOOC3D3qFQmhXr6Dip3+DFR8Qv2vZfyOoZFxsTFbiMljeJWJ/qI7hD9yUhOo9ID1sJF'
        b'OOaNetA1KIKjQk4A53hLaFtA/arWWiIa3QB5KFud49c0lcU3EH/RIuhEuQTuE+WgTqyDEbxPT6igwfTTUTlUksx3VABd+KsS5UIbyhVxBpAhgHzUFUVTwaB3GRR690/P'
        b'WjcgAwZVBA8FxvTV8hJwC9BhQ8hw81d5uMOhCOUTD/DKCWofMPTAcXrNDM6iJokB1MNxtesY6qBUSQBe4HISykJVqKAfFmpfdTQpLPEGBv4EDdXSVh5kaQl5UGAPeTYE'
        b'9JIhetqKcfvLx/LQjs6tpi81mgo9FKoTWqGd4ylWJ1w+SE8zxniIiUfA+Al+W8z0kD0cTVVC59ENlNEfw9PDzssXcnHD7f0hx2eth3ALXPXH/Ui+ulFd6kwO9YokUAFd'
        b'c6OlF7N4BXHPvGR2Y2ahtx5aZex6fm/JTzM2SmJfvHuj5PFbvtNLDj0z43mdW9LSpUeObp46u919kcFXZkHLx4/PqBwnmI5u1Rxy797j//Y3b0hupXxZ/Kxd5uXXyqbU'
        b'Bnq9/Pp8zyX+H/89Ov69K5m991964bsZri9HXdtpYvx77PxfZ4x594uDiyzj7nuX7qj7rnvSE7tmrv5s3FffPr3p55PX6t9OqntWElY0a2uvLMb+X2bRMhaMCu07oNra'
        b'ztYDGg1oaEOtwGG6hCG5NaKeNQxbmGR/2JAgDVSBzWxDf+GcuFDqiLVGrRNYuMXl5D4nrje6xIJkS2aOQfl+ngsHRYpAjTv1mgZPhA7iVkZl9tStDNWomTmHT6DKXX2z'
        b'EdVuIoHbwpil3qxmR6EWrqOWoIEQjzTiAq6spjEZ49zhjMZji5uXu07lsUVFcI3GZHhBbajqjinoph85nBiE3teeRL2/EfHLY+DaQMRFirZ4EVeXhoZrk/xbH0jb28+5'
        b'Pg5qaFss8MI7jt/ThS7E4vXXjq/78qsJ3jqLlulCN7Z4Q5EPP8+UE4Txc6ZCw4AEf71/y/mmwYZzHMmM2mfC66kiUwl6h4g6akX0H6H7NRQIeIsRjB4VHpp8aPTn6PbP'
        b'KPEifwLKzXdU261j8kNtt0eFdVNhXmkFE/12FOSpQvyJgboN9zoNWbHdI+jQQwHZiD8swMPJ/66IkJHeFRFeUrXVOTDmlkW0kgDXu9oqMuvEUn5QXruRekfy4DR57czo'
        b'1FeZnQYMNjvbKMroEbLX1ZE0F4YzPp0iIhQDSZfVm+8wrkON2jbUho2SOhKl0jFEAyMSMsyxv41KCdLgW5F4yqHhp4OJBRl7LrHn+1TbJNJ7SSrF/5FMKpUyrKGYfZhV'
        b'xbio2LPDMMGGKqRRMVjmkpgbSnuqYnkcKeYmNHYAx9pgAtmRajHA1BiO4TUpcjfTo5M0xKi7WCzoCMGd+J7oCKIE9nVFH0sda4PUktKkk6ZRJW+a/2o7O7tpshHUUxY5'
        b'QQOVQ8ls6keKrCmZ8UEytbnv+rDlaZ7po3dUTQFVVNdAssdhy7D0d1vtRo563ILlQb7Obv42UrU1w/gwR4wEo5HJI/OhxsWzSO1RStg9nIE4AvnoKMWRPxr7kfTwaOad'
        b'BnNNNauHLU3Naj2cJSjFveLmL3fyGWr1DR/M/IiWoJrwinWFhheYTFjVvCHrAhvPkZT0OSREHhdLJMUoUd67k/reTvljSR+FxpDIaiIgNFM3KjFuF+6qiNARwrFjlMzh'
        b'ti06OTJWPfPx0owgEUCW4XGximjcXaQk3HHR9Le4l0esGCumv5tC1r+ZKpbksB2R4UlMHgxvGAX4LV7oMEfKeFxZe0gdbFRYnKr2Ur8BWZtYKA5bTpQyka41utoZI+uI'
        b'1iHbiRylASprTM2WTgLWU/FbYmLw4gtNZDYZu3l42aJQxIVH00HQ2IbxiXGE9Jz0Iu5a1WDjhcCm/fCd2Y93UCrHVmJofHxMdDiNTSRmOl1P/QPwh187LirS9T5mU7JJ'
        b'Sy3xd5mNlGzVUku/IH8ZGQyyZUstnd3kI6xDq34ZBQtlVo+Q56AJ9HLSiPpBzEOjBZBqTFSdYU3UKXJqhBpGa0LsoWQHsUHRMWimqg+1pdbFaWNb6qq9UBoSExA/jkWG'
        b'QasuHGFEFMQqvYANgWZ33dUspKlSAumaMKkQVI0KtFA7tdnEcBTVM3QWAs0Cl+LQ8Z3obCCN5j8A1ZAhSd5hrLFp+9uzWahH6UdKT4dSChbBOBF0sAUcqMIc8La1Wudh'
        b'4xU0IuGDirvgktsYXOMjKD8C1bDc8bNwFbI04U3oDMrB5u02lKVcj696Q53sD76PQl9Qipm1lgSJIj+IgVHIxJyjgylcRvUon56viN3hhCreCjWLsd2MCtcoU4hGv8nJ'
        b'm6Lz2Hr5EZuZFlOgBSWQqTfzMdSg12emroI0qMIXakxQJqoNRNURa1Gu8wF0AqVjU68RncM/s3buRrjrncO2ojznxOi1a3dsTZy5GVXu3G7MpYRB0fKJqAqa0Sk6gAbo'
        b'NNRLoDNeX8AJogyhh7cPQh0UEQP3VJPliBWD3MdQ7ipUHIYyB9QoE2qglHwmMWEhRpAt5VATqjqwdsx4KJvMgtJ6UbqPKiBtPZzR5e3RCTdlKLnSsTFQ4zuQbV27ToXF'
        b'E69UBsLReAMjKAlUdXs/xwLxJ5CxUaN2qPFqUBq6oENfYwg55tAMRUJG73HV9SDB/0Glq0ZESiLPBVpqkEXwYEIHyjZwh7PWFC/HxQzlemuYhhaj8wQGBDWtoXMGF+pN'
        b'MUTwRDqmpfBCeSZ4fufBMX9siufx0Jtg4L4njCasyCNRhnd/xiJSiIfajj28H5uy6wYUhzIlqNR0JtSbofOoztxMiNeg7xhUNw0uKMmRE+TrTB4G3EgAZ/FaKoD2ZXho'
        b'0iEDdysNzUMlYRxk++ujRkjzXxtEl93a2ehCPw+Oj6fMy9ZuGKIQuBHjr66WwcC1grvrlNIEFUMtOq0k8UWbUKVMjfOw1uMRCh9YcgLq7F+4v5cprnpTDIuPzIhGOSoi'
        b'F+IZ6sGz8chW6KTxPQw/68K8xD4aG7iozZhsGI0NykDFhPMweptlAK+ow8bV+dZFvmuXUuyISYndta7PdcZYf60t2/yR8RInq/NHuPB30iXPiD+d9tSV3JCQL7zcpXvH'
        b'LXE+ahV0VFhrmiiCyLdatksNtr21LWte29ziwFdO3M20jIgs/GWq672xO+vTHLVKX5FZy7/81FW56Td30avfffCv6uuuf9+U8NmxnYmd3WG36xpTtio+uvDTe7m7cqoO'
        b'v3jj+w8ueM/8tM3pXkxyWYj+uK3dTanf1O+/1rbM6fd9Z+88aFy97r7p8gMuP/PNBU27Dnre8RP/K2R9+csBt74V/DV4d9TL4bv/OvPFefcPPNH4Q0rWyynvbD93UhJ3'
        b'/5TLSfc4f79F125wKyb+/uBagPjt6fHPPmf2zM44QaLnC++ffqbliaCpD0z37/huicXPpTGbJ+/5Mf5dqzvLnVca7qmoufeXE7t65Gu63p//9jubCm6/+MRB9zeFv4/9'
        b'5WTrz/KfxrZV7zp7Y1JHz9sfH3NyOTjmdmRjqd/1L75cVd3ccEayVV5f4j31zrbD/2waH1eeHf7hY1YNP+XoNvx0f8+7T3jMbPtt+xOfP7F/YvJ7is25J/4aCpFmKW/N'
        b'6Xp33fN/f8Pv4tXftM2dWr8v+6vMnLmnzunj1WFny03qhw4gjEGXUDnLnz9EiGn7YBio+2qcjQCOo6v6zHlznoNaNQaDNZxzSkQtzIFFELG6vfsHZO6cKYAWcyuWhtQu'
        b'dOkLxby2jzqMUJMDY0coQiekKmYSJfT2kZMQZpLzW1nVixbNVYMpMCSFx1EaAVOoW86y7+v3ow61d2xTfD//GGpGOSymsQmuQ2Mf1APx3EEjykuGSwHUNahcGaEO7DSa'
        b'SUM7CaQZrb89nITjBKPWEzWJsEz2FscIpqHrHjQM0Qbd8OoDwWmcbA/1cJR16DUoX01dbnAd5agrT71y/nJKMoG6Ntj2MWoMdMgl7IY2w/0s/jN7ebA6T55lya9E+UIz'
        b'v9ns6qWUcfiqDaFpE+FFesSGR9dQCVygXRcVu0blykM3UE0/d97EFDY2bXBsLfGI2gqI3G6hLtEdKIulZx1Fp4mL2hPlDspXE3KJ6JwDuiq2j4VTqiDVx1EdnT2i1XiL'
        b'8cMqhaGrcPmY7czxmrtsizoRDRrGU2qUBVvpJck4SEf59r62MgFnBDfFywVSdFwk03nkBGej/5lAvjA1bmPOSL7Eg9wKPV5fQHPYBfo8yXg3FoiFOryJMcs8J9nshItC'
        b'/UmHhn+KVRnqxsLxgvH4J/lnTvPdCTOFKa+jZUjS0wTUUykw5E1o6SQ3XSzYM20YH9ugxOthHJQjucoSywfGkT56p/fPKi8fJrV8mKzyo8RzOWMkz+Uh7hvL/r7LR2jo'
        b'8FE/BOyBuvRYFAkXJdbE/whHRZffJhM9CBliLvhHxmJLVfEwvx11EqgME2KWhiqkG3x9RrE+xuB/k4dYHzZyej7lDT3oqHd/qkYslEtQxgAYufz1lkOSSKEKNRuYQZs9'
        b'o6W7hhqgYwAtnSxZs53jIsqoui0cv0mRbJaiUQuOJMMZqg08vslRgaVsA9YYkuywULVLxt+8SHz6jK1ai6LhOlVS90+1woWjQy4E7HEyOa5IR5kMSatTgCtwLNbOu98x'
        b'30aUSS2o5RsENPnGYWFywFNbN3O0Kombps8zEBHgSA7bUKexsLWLY9kzl/GW0eAKnaokFPsIlK1kseiZcEmia56SSFDYGjhoVoYwg+vUKqiyRl0KmRXBHknlIQ1dMmFq'
        b'dauhnzfZLuRanNhcYA6V+rsn0dICrUwCUPlSKBQRFZtDR+bAIWqjeaBCyAiA1mQN3hveUrStWHGNU1CjBI6v0aSIQPF+Bl23ATVjA4oc4PRLOVmODrPnypdYQNu+9f2S'
        b'VWasYEkuOahOJHFAlZQCEb/OCtrX0CuGqNuIUNQu7Us6cZYryUTaPh01B+BalgZhQ7AsCG94lb48p+NHDgezI2mX35lexE3kufEO2lsc3lzpyizZ2eHTOFcyDvw/FVxM'
        b'MPuldIYnTeZ2mGm009YxlRvAUaxZalJOxVFsjhcXV83t4yO4CD5T8Bh3VsNWjBXGTwlJJUlidYpI9ImOjVTzFYtiyH+GAubib1vEGtJiimjuY4qOUkBzdjapq9ZwoYRm'
        b'TfD+C5dAN+Si3CWQmbxqdVSCZ+KBWGhFtShtErdvrjFqhfKZtGU/bTHg8Ny0dIg6vDomwoU1N0BmztlwnLHDgW/GTlbguUhaBhfR9fiBEIDTlUqeQgBCNqqn4xEv2SVB'
        b'J/aozEJiFC5H1+gVkyWoRAKHnKAzwQDrPab80k1QwrAzXdg5rIN56UpPuRunRlq/zqNSiRgK+6ZRJ+TRsiLh2EoJlIVoUpOInU4nrN5Mf1zFhmhsLmtzwln8cjxlZTxb'
        b'MkcFcEghnx1CVD2BhJdqQ8afHsdteBwTT7CA1JO8hnM6sYofFvMYf2vuN4RUGFw0R8ckBHIoGTqNBKQZi7FixUguURqWVZ0SaNtObBG8uFAlXEKHmNVSra8FbfpzsV3W'
        b'qY1X3jGizF2GXpqcha6jXri+HRpJbdZya/VQLi1wFTbQJZZW1tAKJ7188DrwEmyC+n10VYZCkTMWkV7QhS9oocP846gDjq+H9ujuedVairW4McGvhEYGeStMg0xvdp35'
        b'9rkXVjlLjU0mz8nIMSrISa8Jc31yven8FSU5e0RfBNZlTzYvVZ6smbvCwrtxz63nappiDx4qy5T8o8lmnN0vBi22z9dsvvrN0vN7nQX5S/e/9MP+/V/+89urxxbn/uP2'
        b've/N3K6dX698T8ux7ZnnlE1eb2Tde3rSa8dffjf6612Jitf+suPCa7OOtEbar37yCd1nF7/79OXN8XY/tZZvv/hd0hezzdd8kery2KT9Z0yv/xj44oKfpuvl5TU8+WrZ'
        b'u66RZk07WhJvVRQ2NqSYxb1w8ZUtvyxqqdy07vmgzYtON0wJak2pM6wtVpRmfe0rrIi7+Dr33vzWTfXm7QqDnZJXP+g2u25U77jDf/mrpxYuSNyV5FLnWCVa6iqsX9F0'
        b'pzX8ic61t+eLFAH3Ts3Lq/xy4kGZ6UGXOZsvrk/bdf7OFdvO55Jz3t7aefntBTvCez9vrytQtL2SLjmYlSza+fEWmwe5m/526eU7mz/edN/p5d8M79nd+bt03ocvHXSa'
        b'Y+VX9k+76YVzzyy9/5cCr+aWuck73FzuP11ctvz1rRZhbjuUf1n44J0fQv/pnpH7Dv/63mkVPs33F1VrLy4JTJ1WYeIdqS05Yrrr579bvLus9SNrp/NP+b9+OFP7xfti'
        b'X/FHRx2M0l7f6vDEZLvvI4IOK3sPNNttv+s0PTgwIzXC/F8v3Xsz/fu1TbDhiO68ttNjrXuE3yVUux9q/Ua36dzq88lPvv3DjDsBTy1tP5Zstnf6hORtnn8L/9vZOz8u'
        b'1/3wa4F1atnyez+sv/r86XfnrSmOs/1Xx3XrnoAfp1eM/Tyo41zp9OTeOWG3Y12f3zDpXs2c1p232nLWuP9uVPt90NOv/O2HO+8dTJiX4DNvd8v56M3v/XLrrXSzrve+'
        b'9zoW+GZY8Ed1u8S1P595+r1jvVzUuisPpjUFNNxO+LF2cfbYIj4190yIX1vhjV2hBxwqwg6Yf2tj/mDfjd5JDb/c+y25ZuZ3XbeX/PXXGw0nf7DZG3Kp1eA3x3/a/pxq'
        b'Oif23j+aF175KKPL+7fOL1IvZb3fW3XhHX35L173L/4y+ez+tzeWpJ7/9vwrbxc/OMP9bHE/6v6ez7IMpHHxcW32ZTvEigvtE07zD+q/0/6y8sv5s54q3P39kXF6r9z7'
        b'Z9V713749ZuJcWUvf7Tb/4MludtTnvNMgDitk2H5s+vuL/TNm9Ci6/iiuZ/Xu7tOmK6P+uqoww8+Xq3blshifzzi89yB06ahC+XPvf5brc68gO+t3vjY375K/O33D/5R'
        b'Zd2d8kT8uBcVWq/Z9/685bbX8pvPt/1w+a2nH3A7nb6s003tyvzd8APRVwcNk4pnPS/bPNe202fCC74/Tjmx8OeGf7y7cYn96ZcSrHf6PPdhR6ryp/LUzAm/Tv/mluIf'
        b'+9Pl0iVPnc+9Z/3NEz90Ltr82r7gnze51+1/9+bJGPFPEz7+5db1nLe+g6D3pSk333wt+8O3P30v6sOcGuEnCSsdPQMa3q6sO/xrpXvXg5fTL9inyb586q8/ip2X3X46'
        b'NEEc89tLp5/q3Tym2eQf7/y+1jrg2fTNp4Je9f5duOa6e96T42Q7qcUHVTvg/CACk2VeffwlTcziS50oUpmq6BTKVAeaxKF8lt92c1xsv/iMbmjUxGicQlXMIs5Ehwjs'
        b'WqE3vQcdh5vkHiMH4TaUPo9axMud4WpfyMjYPWrbFJt8mRQqEGuHq4dYp6h2riZiRDCR2rlTUN70/qST8+Ea1qsI66Qlrg3NR74CNa7W/RELsSp7xjYe6pltfl6eqtAo'
        b'uwegzZrnDKBXuArlOzI7NBPrmgo7/HrbRLmMbP5tNEYHcoXcfGgUQ4Z1ABzi2bsq4QZkeKs9EeJgAp7YbIWOLkkieczWO+d7+4xFVVbYXt/CL0K5yxngSft8lIvHxB6r'
        b'16SGRwTB8pk60MMwF2tRozWDeZul5U14yRsFqXAeTlMLe48XypdAji3eaQqwyZ/uLeS0oV3gF4jOUgfHTujZp77uDW2oHLXgbccA5WBtAZ2OZ284hdIJJDWqRvUqZFke'
        b'NcxF19nVqjEbWAm2eBi7PHEN9ATr0Sl/Wr4UVUCpwsoTiuJp6ukRuTa3AJ02RpeFSUo4xqz8vDHx3iqaSy24IUA9UULoRh10/NBVVLEG2rzhip8ENViKOV3oSoV63G+o'
        b'ZAK7I80aNSsIEKQuHiMtTg+r800oWwD50L2e3XEOajaSOurK8NZcAFlwHPeDAeoRjo11Yz3chSrQBeupKf2zZ/1QA3v8yOMOZEyt7WR6llbEkwF5B0zGC+GQI2J4lDNF'
        b'UC7BdkSnDI6sgnzcBYaCxxNUUUVzUDo6qbAwlPNMd7iAypczFJ0qW6w1tOF2k963Ji3QImujeIy5EFVGQTvFD9yJu7/Lm3J4quCCO8biGTwBpYtQPcpzZj6ok3AzVmHn'
        b'iS7pW9qis3AaG7eGYuHKregq8/acg3NCiZetTwJq9sAzVTE3XMZzjwWK3I0hneWyXoK61QrowEYYqedNDnUbo2o6wsZKVOWtgrBeau2phVdiqXBZGDpHp/RC3RgNNqMF'
        b'Os3gGYVxerj1pFx9XP2zCl0dTysZ1qpQKY8KLVEGy5HtNCdkBNCpBflaHC/hUM/arWyZXJ9jP8Bhh07rCKDFH7EyZ8ThYcyftlMN3MijGicoYM6+fOi0GuiO2g1VQrNA'
        b'BRvKw3jwOySWuAsSfHCF9OAEytcRYD2tCrppY6OhAdJJg3yxMphpy3O6cwSoQg+dZpO91xJdkNjJrKAVr3Nca51oQTRuwg0mKq5i8ZRmjcfIDg+q3w48trg3UKEwzGMP'
        b'Q9m8PmsxfnmCnGh253kOj/yZEHSNFj19wkEJnj64MFysFlTwRugYdKjxOXehel1vF1SjdqVRN1qXH73mgM6giwpOaEcbLIRcAu18dC6dmXpwGBV7M++8mJN4HYRqAZy3'
        b'jKQPrt+yToHHJRH39Al0yQ6ve3uhjtN+es0RtS7HdcmAHh8yH64SPPyrUMN64RLW8Kvx1SIhYVrApjO6yU9AaXvZ1Wx0BdVDfvCS/vntqHA8g8Q9EgOnFPLti9V6P5yB'
        b'bMbUfGrjKk2cYT3uS5UPGE4By0Pf7gQtrL72PKe3yhSdJAZ8DRTTzcsL5W5SEOhUtlTxdGxTog5ceVMsiKF8J1xiXs3WuXBMAUUyPdRig6UaFupX4ApqxDc+ZiyyQlet'
        b'6TyK8MFbVBu9StTwdTyUYSstzw1doa1YjrIWekPeVnSSuVbt8d6Ww6ZuDTbsTpKTm2RowwM1hofugK3QAaVUGKREQDm+6BiWJOZ4dBp3xyY75qG8gU7bYwGMDXl7yLXE'
        b'awVO4xtWi+gwaq1Yjuts6ZUCF6DDSsBpo2OCJfGolXbcVlRKGo6XJzkyszFH3WSKGAmEEfbJrOwsPKmrrDUEwPrb4MoGoZGWKrY0Y3GUgm5cWMAS+bhsK5aO41GjaA7q'
        b'QtlsTLNi/JiQp0bJST4Bv/AMOj2dVmDiPNSuEpC0u/Rwc2tRG54VtrpMvNbiKdNMtmF0BF3FdwjW8bYzUTEVg46Q7azAY64LuSn4B7SuQTn4lrFwTIjOYAF5ks2bijER'
        b'3km7VADmeIZDJbrIFlVaNLqo9tGKlwug2FKK2sbQDdXTxUUSD2eVBrq4Q6fyTo56KhCFxHUKKNi4kpwWmPLTN6MbDCghe8Ys1hCsJhYkTbMlW32DcCY6u4OJj3Y9AufM'
        b'YN3x8jyFhZMK1z3fiBJRowa/CRT71h7yfG1knr5YbKtAlBcvE6MTK1DNLjxsVGZfi3KnLmnikMZGY5HKKQ2ZMyhaMWR6elE05D5QdRlWcQqcB8HNBkGLjv1UxCJcDaZG'
        b'Seh9tglU4oavHIMXKDq3YhYdqQXQrNDwUhcSP4GKl1oM1+jzdnigsFkuUy0yNyy98V57cRyeB9TBA9VY15myCN9ApPlxHhWF6jPBW20IDexB+Q6USYTJAqEuLq2W4uUu'
        b'2I7arWnFhoDlZuJZcUgraj5k0G5Z5DFT3QL6lt2Lx0CnENVCujFdwHFwFu/UGkR6AkePhfcZDST9JQc25/OhCHVLsOF+At/L4eXUxeOt95gTu1qEelC7BPKo4qNYhCe8'
        b'DidYO8mUYT5kQYGJBOWL8TbA4yfb8UKEQj3ag1MWQyVpph7eIPBM2TQRP2qKMoSQ47GdrvClYtQkQcWLZBzHW+BBxAoQA3gmHDOoQiGHVnusRlBZjQr2GO8Qojwj1ERf'
        b'rINyk7AMuGBuY2dHJEAl3tlQz2I6Z1NRD9yQeCmX4gUgkPGT0YnJjJA8Yzk6ocASHnJ1Ve1BzXCDLGE4KnK0nUi3zBDogm6JLW2QeLIAj/z1sT4mdOT0oRcVU8Ibue34'
        b'6VZkRncIsE7etoidL1mKFPZWcNkDHUW1MiJ6egQek6GN9dTRg3glttnKmbdiP28yD8qmbKByZXMQwTjpo0mHGxM0sMfH8OqicqWJKGsKOy+lDC9/rLsJ5q4RoNIDM5id'
        b'kA3FO1TatKcR1td9iGAzgG7hEnQ0hq3YMjIjUf4iqKfhJ+qQ7nwooaPhDFVYebGDhgRfLKhT+WXb8HZLZjKfjGqJ4zcTKok8CuPnBONxonPjGl5u1HHnuXCsBu1kJ2TJ'
        b'xvzPYOCKH3KdIVywfFxxIvX406MfHeIuG/7o5yBnpUOhhxmQsR5vQnE8CJqHKUMXFBBEEHaPDkUC0cH3mfKmAgt+PG8uMOcnalvw0wTGKqJyfd6QnyGYwVvgT1ItAlJs'
        b'KDAVkJ8zBKtExvxkfrzIkAIg07LJARNvzFsIJ+Lv5vh3kwUWAhNaC3P98fgNBI3ERjhcucb4mfH0eQaGrCcwF+hhIW0hUiOVMMJ0Kf4+C5cwkZ8l1uH3PDbMiQzrq5GY'
        b'VR/e7X0nRKdwV08kLkMi40c4ITrEfWTe/4xo5BrhV9MU+qM8STuWy2Ui/I3Gg8v0BwGYJBIyprs6wQEuHm6+bgEUsoRmSTMEkzUa2BFSw0RCi8Vaa/q/ASyCu2ihpoti'
        b'yWwkh2hRRJCJRCIVdrXw3/mpIzQ2JlOU402XMeARMnXE+P+TD3K6FMQVC7tuaBzO/S4wcOKWbRITmHloGJA7r6f6qdAbHXlEGKGj+qzb77Me/iyJ0KefDfBnQ9Xvjfp9'
        b'VqGQVOlqEEZMI8z6IYwI+yGMmBdqR8zSIIxMiJioQRghqCRcxJQI6R9AGJlaKI6YrcEXMYjSipgWMX1YZBGCZdIfWSRDZnnXiALsUDpp18iw6KQH9kNgRfpd/TcwRRaz'
        b'VPS5MsFdkYufv9tdofNcZzyhkpjLniBdqHBEEpPJ1E4h33bzj474sZglWM79QzAhqocW/3EoEPXraD7nHBUUSB/8h5C2KPEAxRfyd/P1C3SjSCAzBqFwBLi6+kcmDEwm'
        b'd1ABgDzSzXM0IBnqGj0YP1K5GpyMgZWX6Q4og4zS0EKNBvfY8GWN8vKRrsxJLKKy7D8Kn/EIpLRaLLYWVc3WFaEz/cH9tqA6dgZWCunBkuQEnsKVIWwzQ9XqRdFPxL0r'
        b'UBBVrKV7GmEW9wh9IcrqPe9QvahPuG/SH1s8j3v970t2idrhJxlPtaZVwa6oE3UOgGqDNO0RKDqPqEM9aF7VSPs9+ZKSPXPP+EGL9E/CcJhoE2Sm0bY78nV/ABzHiK9+'
        b'NCyOGoLFQWIw/kexOKaKHxWLI4K2hIANkFD+/yQQh3pdPQSIQ72WHnrH4kcG4hi4PEcC4hhp0Y6CjDHsUh7+/j8AhDE4aYvlF4TGktQAkns1QiaR5rHh0FWHgGcMGGcV'
        b'YAbZkxgIBt6XrEZO+nkYUoW6Jn8EqyI66r8wFf//wFSoV9wwKA3kz6OARQxctI8IFjHsAv4vVMQfhIogf4bm4WjJA2kKggUqQgXDwxNACRQSEtV8ayiz9/foO81AvZAt'
        b'gTrIRY3R0765LlSQPAST3UA4wz95Z3vUpideu/XKrddv3bn15q2/33rr1rWjp4qnZrYenn664bAsv/u16oyZmQ2Vj51uzZ2TObUibd4kLu2awfzvHWVa1ONhA7Vbacjs'
        b'lBUqDAHFRubnrUCZG1G6/iAYAYYh8NgMdk50RVtOArT6ZeurDl7toIfFylah41Dmja5PJnny1HEihSLqrgmfQ+OcG6FyCBIAahOr4z7/nahXTQb9rIepQqtZJr14OJ3k'
        b'/0aq/PhH0q8+mzy6fvWo+fLbab58Ygnfp+kNky3vjOvEsuWHvEmTKj9thB1zmPR48ejxveHa/daXRL3GVhEdT3uQlichel6URKXlaVMtTwdredpUy9OhWp72AZ1+Wt7+'
        b'4bS80ZPe+xu2/19kvA9EEVOpTqo08F14syH5uP9Ngv9vErz0v0nw/02Cf3gSvM2IClYMlv39udL+UE78KCLjfzMn/n8sk1s4rAZpwsBax4kUe9360aUZroHDDEyMeNY9'
        b'ddxZalqAB+T6qWHA4tZ4eGEljbCUrSf4Wzo0Dh+VoHxddC0FCihTOcmpgCpJMmqcOVxuNhxDTSyP+jw6hq5q0sJRDtbfmlE7qlEuIlcPQTa6qiEypzBg0C4YBglMQCiN'
        b'z+hCD3ShVqUtefYiqkNHvH1W7VFniUKOhw3LDYEcxtbqqcUFz9ZxmhistCNPFOi7ew9SoEkqrQ0U+dqQetEQMX+JNm5951SlE2nmGVpjFfmrZ9Ca9bbr1pNkYC9fH9QQ'
        b'6IEubkXNHr52tp6+uCh7AboimYvy/QO4yajKMAbOe9IIdgOs1V4ivB2EswPO+KCuVMhWkvMXuIqOx5DiO1BR/1eQRNf4uYkku5UmmYu4EJSvjcpS0XmlPXmuztItgN3o'
        b'ARk2qpHzCGTPaBr/eJQ2qoOeBTRafDt0rpYkrvY0xJ0pHMMvh+J5jBskHbKXQhvu2HIoTlGQTJVe3hrq0WEasH9/NmOms/EIifnEeR4X/eWDbpHiZXzlO0vLoCOtBsjB'
        b'2O2vyV886Snd4lUfUjTfZlWCScn0qR/UJln8faLt2Bl7HTx3uD6rX+U2w1Xxw/6vfrevnOuls/r1V0VNiU8/MO+qmKFX2jbx0Cu1UZ98vz99h+n6NM9Dd37MMtG+8PiH'
        b'E2bNMvGXG03L+fKZ8vlb0+P/kr24e54y697Zvzr8fOXZxK9OvX18UqrBzppV25uDa74xSnztpbIKxZe3br738dKvpn11vMy718H+9z0Lf8s9+byk6/CM/anhytu/Hhd9'
        b'eK7Kyv+XYO8s/787vfQp/8WnwvRWr/jVFTJjeuhrQ7JWvO3GoBrbAdmikGHOIonyUNsWda7ouJA+sDNvdI2GhcyHPJk6VVQBxU7xy9lzTVA2U5XK6YJabDW82JNQHb3B'
        b'EU5MHIJztnmtSGczVLMSMtA5OKeajnDdz0ZNRTwHTtE3K3ehdm+15RSsNcd2D4sFuRGazALe9kB7H2sI6oTTLNr1wkbXfoG5eI2r3s8ic1EZnGD5qlkom9B82FhAOW4F'
        b'Wbi5+F2GcF3oA9mzWaRfj9kKyLeFwnDGiMyjRlPEeDfWQQsUec/1IrLgEodn5iXoSkFX2VF9G7oBh6xRA5xCvX1+633GNIhggdECay/U4+jLArhwA8bOFsJJVM3yV82g'
        b'JMjRW5XJSY1SdB2XS3y966Fpi7cPajcZLo+TJnFujh5qcEn+gymUXg8zJuNpIqVQh5L46ojFFJLNVEUCrEfJg0mSpaGAXN8zZbDpNHwGpO6jZED2mZxaI5/Cao/MoTtM'
        b'oqPbI9mdN6T97c6HNek/nOuI7bcHWx6a6zicufaHEx0J8vfQRMfpcorBwGvZDU5zPGLt6Ut2godmOUZOVVKe8HNQE2TtAdceV6c5ostcmMtyoYSbBk1CyEAZkEEPlyzw'
        b'XntTkQwtfQgIRxK2syOpLNQTj58d56BJYuxFTVT4m41neYp/s0mIiZutx9E93QPK4MI8TZ7idCgjTqcTqJOqHHgvm451gy5Ux3IVUS+6SC+YwkV0TJHAY51AzhFdIPeA'
        b'PksFzITaEGtVpuL4DTykQaUxSwWsDVxEchWj9qqyFfWh21JF4+WMugNIqmL4JpasiLpmsFO0lt0LAzSJilBoxkFT5E66A87fZSZRJRWS1Cneym+9krildm3FZfVlD/ru'
        b'QJmq5MFglEb74YjPEZo8eGhcvPw1w60scS7YZjpNHjTeEyu4MymW/XJyImOCPTR1n9Wa+TF/Pnkw6g8nnV3T7ks6Ixh/EagtXMKoUmy8fO0SPH0hzwaKsSA9h+dYoben'
        b'LZSgNoKCQiIAZahTOBcrL96oBNoUEmjiXCDHKBDd9Kbtaj7IUgfjp+zz6fKxZo1d9RhLHeS0Y/Y9vdiVo4m36AwU4xnSP3cQZUF1gip7EJUa0hG0W28jUacHwk10iV8K'
        b'VV60VOtN2jRF8J3kFH2PdWG4tWyaFsmhWyGH9LGa2N4suPyn+3f7H+5foU5f/5rRCX0GXZOoE/rguge/eH4YvbI6Hi5IEoWcPqSxfD5UDw1MH+4lFHHQph8Al/tl9J11'
        b'pURzhEsPHZd4oEscTehbPJs+FAd1qIEl9OHdFspQPcnoQ607aL8sGLOXJPT5L9Ok9MHxFMfoN5u/4xWn8Br85teJysBnE03djZsvbo1afdskrPhvOb5fnNyVoZ/z1KFd'
        b'oq1PCA47hUw/WWdcn/mqy/Paky5O1/mLyGBM8nfjjO+t+HqmyD3bz1BeteTHL84FR71qbCLK/uK5cvu2RqvPgz48MDn5g32/X3J+vmif9FuH43V/v1hSGX9TO9iicmLI'
        b'F9FTNnwq/TaxYe3Jn7oF76d8EB4asWdRlzKtJchf2zat4AnRxsWLKvLnZrxqtTah4DUbm/RMS6PZrmN8GpuidkTeMNl4b3f9Cru5Rlf5Nx1uRnM/z7LZe//ILJu5HVe7'
        b'Su4/SDr1dGRF98pf3RfdtVf6ZS5wn/bTuK8/vBb92WG0Wq/S8sl1nzwz31J8cGaMWcyq9w9OPNth+E5c46TJaHPzon8dC8lKNf3QonyJT2WZUbt59+fP/evaX1+NPVQo'
        b'DQ/vaShZFmsX6Hz9tbBP4g4mxljvrXkzqth8z+sur9YsCHhJURS7za90qY2z/PeaqvUhyXPbJC8kPi/tfOMlz40bbnh9duTJglesv3vu7c9e2OeQNu9iet61b6Z+Mf21'
        b'yVGro7V7tpV94ZJkXxOes/ajpy/vX21udYOPW/nFoeaXG787dOq64I0Dz72c8IHZhjqvKdKfPb6tLlyytTT72u4Wo08cmp2MElfu0j7yyavLDry3LqX95FPKpyuWGv78'
        b'yungus27RKf+Zbrj3coGp+AdD6LvvLD/dsHKzz2Wz2/Usy/U2RK0sfRfL/0runhO1JbvT0xed/fjy2Mv6zrMTq0PuH/Tsuf7OVvPORv1RGSZOZ0Luu0fVG31m0lQ8FPB'
        b'36b4dB04P/l01qm0/Yc/idi3cMXTv/9+5+y3+fOT0r7b/O6s9J8Nv+1Z9cW0T/Mczpi8WjDurV+8V9ivfJ3/3uRMceQvSca//vDR7/P0DpyS35q7WKv3Rub/4+074KK6'
        b'lv/vvbvUpYuIBUVUpFsQsTcsdJRmRUCaRIqygKhYkA4CKthFBQUpgtIsgJrMJC/JSzM9MaaZ3ns0xfg/ZXdZ1PiSvPf/yceFs/fcU+a0mTPznQmsKX1XaRiScsXnpQkV'
        b'Rya88G7gk9sslEnOm07FlO7/9I2gP977NPN77yetXF9sOz5jlI37D/vLvzpK8nw/6Iusg+nPPrvGJvLrzw8eWtKj9/NZy7nzeu7+8VxK65Sv9caPKlpd1zHqy59nJtfa'
        b'eQ96747+bwaZxpnV75Z6rBr6/r5VpbN0DZ7b4nVWufHD+uJlIy9HBUclex9v0r9+KydlcPNr8WPGvLLpm5+qLt6K9X0v/8iL4u23zh2vqZneWzLl1rTzpj8e3vT1R7VL'
        b'n934x5fTv3nW4VfP+Xdk3dOHWkXf/HVeVuJCv09/umgePe2Up2X0lmUV6R7C1sLPrBPuSh9H3Xp+yYyp75bhyeotnVfLb04vqtxt9+T0dx/7w3/x82E3d6698ceIxEtf'
        b'nLmm55jKuFTIhyNzFU5QTU8sLXhcHwt+xIWx0Nvi5H1+XFxDeMjry7O4+fgx2Jnc33exHlRQaNwK6OI2wnXQg+c0yDgsHoWXODAOS6CXF1KHB5ZqI9rIwTs5hQLaoEGp'
        b'cnaydSDFs0Eb4djVmDbXZDjN3vfGU7CrD9DmHAWtKkBbPBSkO5IcpgOxRYVnc/Qlp5ITA48xQBs5jbqE6ZCnCx3uyPE/1AhmKkXcwEG4qEa1OZEXzrLHo6EcDlLsGuxJ'
        b'1sDXxsA55NgiPA8n/Dh6zU+kfhSqGX7NejwTiyywqA+dRniCctzH0Gt4QuAqre50cy30mj9W4Uk1em0kVHDswV4kcguL8k6RazOwQIRGU0JMJq+1U22WCr7mI9Kw49UU'
        b'voY9eEUFGPIbpA1fG5kZqCcw9Bo2D+FyUSM2TfHzdcGWTRoEmwzzoYpDgi7BLmvsEBL6AdgkqHMh9GEVXB5BQ6mf3NgPwEZvaNqgkavVCI2O9qHX/HCntQq8Ro63vawN'
        b'22ZhoQp/Vko6kQMVFICGu8OYqbM+7IQzykCRehGv5RC01UHMdtwBjlDkhhYC7Qrh9Up0BIZAyyBjxIy8z0DDxj5jJUIZIvfFzle5zgmDAkWg65jlRmTq6MBJEVvth7J2'
        b'u8EpKNLCpUDjIjzJcSlY5snGL0u00UK2EeH19DgNtM0DedRGuBIKe9TQNqeIWRzYFjKXgQHi8ALuUvjCGVNX/w2UPcdiRyxWOorCcLkc2rDWSgXbguK5agibj/k8FYRt'
        b'5Dw2BLPJqjugwbAFYAvmqEBsWG/N23BmA7Yp1aAHD8wXyazuUFmSx0LzIxy1Be3ZDMXmjJf50mje6OQXhsfviQUah6f43M+Dan+Kg+UoNi8soeb+xwnVhzI2vTfcDzp8'
        b'+2HZZAPp/sCeh8N56FBsm66NZaNAtnKs47I8tC9kODZXkQbkPMtwbCFTWM2LyOS6zGFstN14cQTFsVlAEyvZFI8GaUBsPuF4SAViC4diNuYTUshsc3AjHL4ayIbHJ3iy'
        b'Hq/BS/YUxRa4tQ/Hhl3YQNqsgoadwJMaf1AuhNW6IEJ39AQ+zy7PsFNqQGx4aLkIJ30gjxXsZQUtfoQtPtEHZZPwNBSrFgC0pTyiAp+4zWd7gAdh+Eowh0EnFm7WIZsD'
        b'mf/t6ziSbVKQCngKe5aQaabGsEEeVIlDE8P4zD4QnKUVonW8iwhHgmczFTuU+HopA5PghJrP9cYzvJXhWNDnKh/PBvB7qe24hxE2iXoyVJJm7e0D2EjQBO14gc1mQ337'
        b'exBslJs8B6UcwjYA6lg2kUzznn4QNrL11jPkFYWwYXEAp0kllE9hGLbxdhoUW8kKrOHgyz14McqPnCptASoIGzSEqBBs5HQ5TxFsztirBrGthgvQyV5MxN3J5OGyBA2C'
        b'zRTr2fiNI8dNHuF01fC1YSJ5vimWPTMaN5AD2JwkYREUMPzaEtjPdgHCF0cxSA1ZJvRudG8UUtyeNZ6TOwdBCxuNcYQ91zDYVlmUvY6HMnalZpyVQmbUYh+VNcJcqObg'
        b'kabFWKJIx2pVqV10PhrCXgnOWEM5K3S4cwIpkzrvYZOOiK92cDiQnxqN+mRPmInNWqA5manlLAbJNYPT2KB0XJjFTkcDjpoj55PNdDkha+9o1X3ZWjxFt20vIriqYXN4'
        b'PGwwmwo+44FCPesd+qHmyBycx/2O4e41LgwvVwbHVHg5zBnBhj8K26G3H2COTu2iCA6YI4c+HydsGQGdfiq83EwrspZsoY1T5kIw2Ro1MDdXkS0YhnNrwyLWvNGYE665'
        b'9RfpTnWW49zCIhnMDasmkz31fpzbTF810q12IHDYE/SSGZ6n5JyEwVQ8AY2EgrhTlg652MkxmQewEWnka8L2kFXr6INtccaMooMhR74oClVA/VILbOa5WJ/d/PXwqDQX'
        b'dulwKFAjXGRO3tTbbdByjm3LcldHQT4cj6XD5mlu39nNLBwg09CKb05d47CUU2yW1ygRmvHUGs4mHF6GlUpSa5AiECucvdaQ7dZskywbSuEMv7/NJQX1OGO5P+HLAsh4'
        b'jdHHQ9IWslAPcqj3MdhHziV6uhRT/pEyVFehhLA85gNlW03hYjqFfUQS+fl+xB8FzEH1insRf9hJtgO6fALgDNb1QeZwRzJpnQozV0X6RidjJuwgLMBSrOiDz0qUC2pj'
        b'UyXTI1qpxmcTdqlOhLL5Sk6zy3AF96pAwm5k+9rFQcKw24DB+nAHdEQ4Y1kSNj4I2rdDJx6axrFDNkEHK/qQiXg1kzWSQhOxyJHRaAJcme3sAKc8taF9GlhfLuxhPZlD'
        b'VvNBhRrSR+q8TGF93WQXZ6qShhg4qIb1kfmDhfYU16cgnC3t6EoywfMUalRfnCvZnzxsOON9BEqWaeH6yLt2cziubwPyfQaqJhkqHClNnBmwb4nASORPJlCXBtVnvIju'
        b'JAzUN8Oa7XyzoHopdqgBfUB4HHLKe/mwg8QTT6UQ7qULT6lAfdj8CBvTELjip43p85RYkxiibzu28AWeu5BQwtVtu64K1DdgLHDWgBwGFLzMIX1OhOvI5JA+MmfY5rbN'
        b'H7s4po8MApZ6MUifhQoAjyfHTKCIPqhNU4P6cB/UkKlCG+ZMBqJcG9VHT6hG6GCwPptsVrzCf7jSFnu1QH0SmVcH+DyAhtlYpoXpa8Tu0SpMnyV3GemGTVk0RosazQf5'
        b'euJCrMPj7Cy3g1os9iOHo7kK0LeC64SgZaMDB+1RX5FH4AKH7REmqczR5P8eqMfwWEy7ID0Mpcd/BquxemayP0Pp6WtQehbkx5KFhjEjaYrQ+w/oPJm+CkknZ8g5a/17'
        b'cXoWDJlnyXKYULyf3Fq0EuXSwv8Kn2fdH59nda8K4X8LzivSU2FCHqrV2CH82g+i9yeNIrVTKEJahxqfJ6MfD4TmpR2jGf8qKm/A/yUg7zip+32KWQwW/jkgT19mpqsC'
        b'4NmrAXgWJGU9h10lT5w9UH2BjfuwSnOJLRLR8qpO8kIo6mdIa6L6rdx5H+5uhbxKr8qgakC8RD+rTFR/W6p+G/LfibJ4WaysTIp10iiWaJQco0LjQpNCMxZJ24ji9xje'
        b'TSdON1Y3Vi9PoBHEy6QVeiRtyNIKltYnaSOWNmZpA5I2YWlTljYkaTOWNmdpBUlbsPQAljYiaUuWHsjSxiRtxdKDWNqEpK1ZejBLm5L0EJYeytJmJD2MpW1Y2pykh7P0'
        b'CJa2IGlblh7J0gNI2o6lR7G0ZaFOvKhC8Q1kf9OI5PorrJjhpIwp3fQLFYQ2poQ25ow2DrGOJMegWIlhopyvG3nNDQidr9KevX9eusdoklotaefggD+NzU16Kg0VoeR5'
        b'PCa68N/uLLAC/WtSv8LUSjqlm+1cLXNAlXUbAxaobOjI0/S4NBb3ITWTBsFN72/Opx0DwsU2LjpmrW1a3Pq0OGVcilYRWvaG1ES1Xwl/ZtDTX1XYLxGYSu24fOJtWfRX'
        b'pe3GuLQ4W2XGmuREZpmUmKKF12CmUuRxNPmfvjYtrn/lyXHpa1NjmQk7aXNqUmYcU2pm0L0naRM1ueoX5MJ2QSKzXnKY66gyvE3qb9NFTZ9UVoF8IMapxkFNcRdbh3mO'
        b'6mzRtso4ap2WHvewQaJj6ODlSEEe0VoWgCrbu9S0xITElOgkijZQYZsJCSiS4p6OKpXRCQxnEseDeZBcvPe2sXHryWartE3lDWdmfA6qZ/PoDEtOVfa35opJTU6mBsZs'
        b'7t1jMhjoKF2XZSUnXdeNiU5O95gUI1NtNTqqbYdpnairTxVqTK9QHWJLwbYPkWwgUryJSkMtK9LNFbbKN+tmy5iGWs401LJt8j5vvO//Kv4FHFm/xfPnxmJ/Zj9IesRN'
        b'B5cF+Kts31g0FVZu31iRUWH2oWQpPtio1CGOT6E/W6cPwTcxck6jMJWYaLLSo0iTorgNHy9MU4j2dPuTGDfRsbGJ3OJTVW+/6UYn5oaMONWSVWaQtaTZMh6M6+hnF8tD'
        b'19AVF52RnpocnZ4YwyZoclxaglZgmj9BiKSRlbg+NSWWUpiv44cHmtGca8aqSdbfgsAmUEm5XYvYjo4Xbzk7NqU7Pu1osul8qeNr7TlKIXGrfp3lTmZpn0E/QgMNoQP3'
        b'4AV6z5dOuH5HaCDi6nkodcT90A78FajDQjzOeMxQ7l5090rohmZS+zbB0WEbnMUapp+94yeT/CX6V1TSuMXBAs9cByfgKHSQLX66AHmZ08NkSbfv3r37TaR8+G8yMyJZ'
        b'RSVdyh7ALQjgHJxKZU6ZUwZjlft4SdCZKi4Owj2OEjdryIfjmK/EEhMs3shVBdCeTUREAycHUZiIVbrO07yYxjQpNFhBv8P8wVKA6Amdo0kRzG9JIxycpKQXUBGaQgzp'
        b'hyjYTdOxC57LPKUOWLtSwb+UYbcflZ0aiVxQTspwYbLKArykagXmBfKG+DhRKbjN2YdKCTIhHA/qDwvBMmZKR+TwNjiCHc5weKTqub6HlDICuhxlPMPltVhHA3m44h73'
        b'VKgY7yEJRluldfqG7PHUobPUD/Gq23gPXcFom5REpXZGtq1QBaXqDA7kuSgYbZeSp3tlUL0KNM2AvTxAiHeoN821xLtPDyMK800VeE5v0JqRGUy3sR/3Ducy4JJYqHDF'
        b'80wEHADlMjjuOzmD7mVTA6hnvD4LFXVMFSz29/NzlTbMhOphRIQvGUh9XGFlmJ8llPgpDLEdSn2DQ4S4eDNPPOfEQwbN0HH4iU8DF2mkpZCxirZhVwgeekAF1ChznG+Y'
        b'AxZ7I8lSRCT+MDynmbzMMoaI7hZjDDEf6nSwB8/q4KUFY6DRUViw0RKr8aAPITiTYi/7ZWKH6fo0UZDw4sptoj328tkditXDFPoU/S+T2+EJ0cloEbcf6Ya9cdhhtIG9'
        b'cmaqvjjaDoq5M96TWA+XlesD6cWszMgJDopR2ISt7D05HofDyg3YbkTf2zFulThahrvJTGJvHjXFBiWeZ4VCrznkilbUBIUNKx6Gq9jSVyUZilxxNJRE86dFUdCkHvTp'
        b'SepB95iYMZU+LYbjE7UjwwS4+gaFeauyj/dQkZR6GxPweJIC9mAnWfyXh2ZQH1DDMAdz1G9jJRHh1SUsdg3nbwq4V4jFi/rUmVx5oq6rm6gsJ2v8nU8CkiufSXl5jmXB'
        b'J1ZPltvcOja5rmq664WXfqlI81lpcWJeRFtT3vzJJ1IWOvqfctrQfu7as7p+a7sbfxdcvjwQlbPsW+HMsrZ5M6Rn3Ka6Z3hdSvrXJ79/Mlt5ZfBb118MCxhg8dwXvgVT'
        b'Pp6/VLl58dumyYFTpz/v8WlvlVn+6Jf+cNvvvXtX2tgne1ctMrtktikjJOb6IBfnj8a24ZLXy95Z1vWs81QT/yfen2Wata/wm0b4Tlns7rnorU8/qhw033zBmPyxIXU1'
        b'Y/fEPnrg+h8lo6cOz977+Jdbg0OeWljw/Jtz73SWFcwa4fftSq/BDe0upU36NTH+0wrCd72VVPuU/YKDN99J3xPw5vXOn0+sW5hnUHBG97szGck2PbcvurxqdrFsY+un'
        b'Z/DKD6+9OrXuqGO9667OjjVLjnZcwdmdP7y2MfpUhOWBM2mbTq1q+yVsdUGGY3md7NarIa3pz43+yOfswbs2tWtal336kuWi2YXPZMMN716jr9ddu9Dg1O3ifHPzzl9i'
        b'D+R8oj8j5F+VN/9YMvQdc681BjPeC/p2mt3ajQZOx9/ynjb+ru6NaxNeD9jgl/fxW0LGE03HwlIrXnn1dsT7EblP7/m+btzXRT03h0+p7wn0rfUede3r0mtnsuvLkyJl'
        b'7RnfvtItnzHCdUnuliMFdWLCSp+n39Pz//GJgjfyKivf8Rya+vvHb851/GxR8uPPeb5eZFpo2rnSrHXMlMfufvusZFr21PZNh09nrf3xle8nKY7Zf3umPv3a9Ce8tpz9'
        b'4+ZyneHXx+oE/dC1fOXhOpfDeX8ULs9/4SPrn58vqMh6u1fx1dr6mkGdpofjKpTpj/68Ljwj49rI+om3a98cPivqu/Px64/tN5y0f+7OMNvcF48l7Yh6YZP7Ew02wV4/'
        b'mxrMScxpf3VibKTxm+4ffnVHeuUTi+KNJx3nsiur7CXuzm4BkoAl2CJBg+iHddjK799qTWhQpbN0Z1kxkuw4WCIJCuglq20I7OQBXvbD0VnOPv56JPNYCYrEmbYx7NLP'
        b'Asqwp58DV7yCx11x3zh+J1gPJTR0zDiuwdSNkuAi2TF68Di/Va7BXHKklNJQU9Q4dZu0HeqdsAmK0ykkTumVTF6lytkxq/3doDiIOSqFonHeLk4M8qknRG6lkVxaxnAE'
        b'ZQVcwv1qDT4Uw2UXtW/bJYu4muuKhUQvv7DMVVfQXS3FQe4ouMDvsKEYD2X7Bbn6LIOjLlTdqIBOCXtJF3ZxMu0jfSniJgSkyVe1QyBvGcuUE7gbG/C4ykoZro7rF5C5'
        b'DPLYFV0wnsJK5Tgs8FHdArIrQM/N6oA2WKvt1At2YiWpeQ9W8RvCHDwG+c4+0ELOdXlCIO4XWSS2WnZDuGXmRHqH3f+GkMYSOCrfAD3L2FX7XLi4hSm3qH39RWgRoNWY'
        b'DMdI3vzyEELxrG2+AX6u9EIvUFXIaNynM91qLesktMzDHCWW+dCB8TMJdMVOP0mANp/hC+VQZ6Vkt/bJrnpUt11hEOg6mtCE5jBeIOElPIH5rK746XCAVBXo6hKgVQ90'
        b'TrKdIMc6ODKbX/63kYnZSn2UecNhrRtNKIQORo9IzJkNpUFuvgEuZOyP+QSIgsla2ZRFAptfMROt+SmObfMS2BFu7CHTI8kSPjvb4OQj7NJ/lx+W6gm6BhIcNTeKhf3c'
        b'ueFOLCM9JZwVOQbXhUCZmE0DoKkm0hqqI9SoLydHiEPhqi97ljqNuhLVqOKGTxAJ63PSkM94wgBF0Cq5clMHD4uboRu7Qydx1ddubGbmBOzGugkOrhDheCgZHnrhMx5a'
        b'hvTpKBdimVpNyVWUoWR+MRBycgRVIOoKCUO5jpBMcl532xos1PaOSehYshoOQherO8gdjlC1Eo1YRM3Hj9tSTXtJFm9YKxAmhvaqwpk2rcNnuQinBztxfWaPrsR1zqIC'
        b'TuFuAXqtlZzCV+FAmNpghqqkuyUsXyZCicTVPuUi1isZx5CCvcxqsZzwMXS1rR+2ho4r1+ditS3NYwGtMiylEaJUjncJV36Q5DL3VOv49eGwBMWz5nAFSdcG3H+PS22y'
        b'GrEGilR2Q/uhlo2Y3ig/wpeqtN9d0DZPhFbomMBrOQGdUMkfpzvKCK0ddQWTWNkC8/R0CpwxwNylULoxEzuNx2Lphj6GjQK8x2G5d4AreSFkgb4JHMUiNmmzyBI/qXTG'
        b'rnmGhHl2FAW9rdIkUkcTI4otGUelM5TbpPEJrxcnTZwwmRFlkzllH6kdBZTpMUuBEqzQEQZik9x8lTnris1wyFFgse/8jaq3oUma6Z7F1aIXA9arX3e0JhNUTzAJlM2x'
        b'T2HzJnGzs9KXWgmtgTYRL4hmsXiSb/5XvZMUzKUi5tpTr4pH8QA3EUqO0yhfxuAJjfZlEDazF4dBkYGSu172WEydL1dAJfcBegxzbZRU/SnMG0KdgK6J4arN82RH6qWT'
        b'8JAfaYoPWZdsZxjnjWUyYRTW63gGQyer29tzozLQUWUgNR2q/UTBzEa2hAaP5I1uWAGXlNyfMjYMEuBS8iZueNCE7duVnDgyyPeBCrICT5EeUQoZDYeTzr6ufq5Om6Au'
        b'kGwmpgmyaKzBQmaIhjsyrEnj+lpGUS7FVEHtuBq7MnXgiGSbTu/GoXChm2pO9JsQI3AXVARNJlzqdGjVDQzFMpWZlCfUaBn5XJhMg4xdmMKVNof84ZiCPmQTGHJGjaPa'
        b'u24ZtAzQY4vMcwAedfYj59R+eu6Qg00feyRyYlz14ft1vS9harnaCDunq88FpjUiYm6vo/F/f/f9P9LyPMjdQCf5+A86nO1CnKFoJlE8iK44TDSiuBCJ3aBTzAjTi+gy'
        b'/YiupM/+MiG5TMThor3oIFpIZuw7ffIdvW03I0+GkG+sRCvyxIL8NhGpHmg4KU2X3cD3+0akPybsTYpG4SVRTc7mgdr3T/d6PtDhOpRuqqPo6Y82MfqvRkLGi+srXUNN'
        b'H2qhTXes/6Cm2SFcstdW1Dy4H/8jrwct5A3u9aB/NRqXBxPU1+DsHtnFNi7BzdaJXowRCd9d7d3lQR4Q/mMD43kDwx7ewHPqBv46lLZEdatqmxjbr86/WNl1/cgYftX+'
        b'kBo7NDWOZMBlhtaNt2UvUvj936qXj8J140jNNXJk4sMqP6+p3H6ubUZK4oaMuAdg9P9BC4wi1ReMD2/AJU0DnGjvlemk++ySUnM/+U8aoRrr94WHjnWvpm63kFTqTygl'
        b'PpV5ObCNXpOakd7PPdHfqz+P1z/z4fVf7T/XtNzl/JPOznl4ZaCpbEhfZfN8vP5Rx+Y9vK4nNHU507pSovvcPakdZHAPAf+o8riHV/6UpnKH0Ac4Q1I34J9MakPmYCCS'
        b'wv0f0oBn+g8r8xLAl/U/qVOf15me+pAan9fUOFjlT+If1Bev3jrWRCdRzUlk6vq4lIdU+qKm0im0UpqbX+gnaWsC73U/8o/aZKJpU0xSqjLuIY16pX+jaPZ/3Kj/qQ9M'
        b'UbhXbSELTNTZYS8pqURl6HCLerPUj3/v9qtJRKypF182dnAUuUx8Hs7jIQaxJkJPmpVG7MHC+D9xY2mqNoihXOx/ZKa2CwmbLe859JPiUiIj/7oTS1rh65TfoBep/5Hf'
        b'2CE093Nl+cDK/yfDEP+fh0EeGJrYfWuUXEm/zviu3S/aKP49MgbyBVkfiAvj5/fNsvvpfFz4e3R+5D7mak1qatLfITSt8frfIHSD0cNYO167htK0Nqq/pfIW19/2+f1U'
        b'+4niOlyx0Fijv5WKdMgYyMgYSGwMZGwMpG0y1RgkaI8BVVMZkf/u/cZgRCDHseYNCVQpDbB9soQ7xNHTtzHFmfs8ufClOdOYGKVMHM4hh7CDLIsapUmagSh4rZOwVnRz'
        b'NGQKlheXyYVhXpYs++TIVQK735/JXK3RqxQO1afuLnb5YTHWQL1/IPWCEbw42DVcElbP0YMawYUZ3QzNxnIqmmIplI/T3JJRSfKiU4wONHuZ8rCME6FRpQrJwiqZkRiV'
        b'ifsYnPYR6PTrZ92LbaooFnlQxdQhg3EnFNBrHnYnBSdM5a4itATLmCJlgRwaORoYcqCOxy7db5rBLiqqoNGJC6+BVIw3TcDcdFkcnIH2UKZAM4HdcIZ21tHVR04dLjQa'
        b'6ElQ7gkXeRjG/Xh2JDfOhTbcI5eLcJwI5Llc8ZOHXcb07tORyJejNhhMlaBuiJI/OgC901QYn7FEqKQBqlzjmHpmGjD0kmsglTjhoq+gGyENJKVeyKALBCrwYowflvtQ'
        b'B37+WMqIzn0PhIc5z9TBss2j+81FhXouzu+bi/1noqjxU6aehYZ8Fi4lE+vhM5F2xeC+megWyOZb+yDq5yPLVm9OlIvZ0jSVojY/BlpIb7qUWiE58CR0M0Q3VhkNtNqq'
        b'1Iq9pGvB6DyJ3j9qjZPvStMEWZzVSKZ4s4H9w5yj1HeOYjYcC+KlncVDeEZJzYcl/YWeos1IuMKobw2HMEcdZhzPYLM4DnZm8dCZh4KW4DE7LSCFCEcmL2XPtkLZpsSY'
        b'PgCMCLXYCE0Z7IA5Cu14oH8gJ7xkJxs4Ck8wDThTLpOOloeE0MC15cJIYeRqOOSow+bhCLjkf8/LV7FHNnAiVHCyXaRxoLB0gZ92QKXJUMArz4uV9QFgyFSssWIAGCiA'
        b'fYx8UVBBloCboy/unRSgjhEFJ2YzxS3WuW9wJhW7kSXi5ujqGyAKdpAPtQt1pmIbmcq066tDbLSCMkGTnYSnQ7CcqyIboXqTYtJYbiwtCrr60iC4gruZ4t10JR7ViqOC'
        b'udvvsbcmm0khV9Efh2NYwwz0/dntsgu0m1AcXgm7erFfqrNu/Qzmq4YQ49gCGwOqArnX7lzLmjsQcvRwN7SPY3MkFvdGrLXSaFrFqLhpjPC6eDGDby1Gs/htKN9YyqAl'
        b'g8XHOYQnscsfDj1oA2O7F5yFU1yvSjYHD6iw02xDbA9ygyK2u0WnQis2D/DTCgjUo2RPRgZMnLFAY8dPrfg7sJFRfSIeoc5ZsHQ53w3YVjBmPXtrzhZjPJCtgQmS/QPq'
        b'VLD284QIF7EpmUxiURCn0OAxXUv5tlML+VOxZpsziz0kj6Y7YclQ7rSnM1JOJpe3K5zDJhcWJHG/lE1K2sm24IBpWf1j2HBD9wlhOgaL5qpW9my82i9m07lwmakFljA6'
        b'EtIVmegxLNUDti62cWElNbWg/R7huZ2cMu2ZckHEBtwXK+BpuArneBze/K3xcCxbiW26VL0kwG7/eWyE5Ql4CSt1BVcoEVwEFzwBeewce2+rQrAUsoYamkX5fxswgfsZ'
        b'OJpI3VC856MvRLkckibxL38gfdIXirJkc6KSugaG8C9LZlI3BdYTDBZHuWwMm8K/HGKjL5gJb4QYR0X5m41a2d8nA2Nm6H+6OLKFCJOtYra43ihWCCc76QYpVi2FcYZF'
        b'Fb1ZzLyHE//VYEZCXEpc1vq0WXEGKjcBciFjOfnl7ACnlffck+Ie7ibVR8/Fh1CA/HmgnycGrJRhB1Ra+MFed7M1k8mabdwEjQN1FmQKcHDJQPKsCHIy5tCRugJXXJn6'
        b'vgIrXd18GPjEd8li13DvB4wddEiG5ESuxqZw2GMUNRRPsyNfOSiN7NaOriyWBfXdWo572ZoYFiYnh2gDliUu218jKj8g3XrhUHNc6PTUlxdbzrpyfsD0wMMHKl/7rCfg'
        b'rUn50keNTjHbBAuLaifr1uD03KZJEXbpqfkOuYN269UHlj/+aN5tGxvr2zr+/nd0inKUFW9fe2nkz7e2fjK9YkvFvqeGL49uVezpurty7tonxuvG5Zl4/pr0xk3/CSlO'
        b'P1x7bKxXvK9ZQfupx1qE8p6n3vh2/oq9G7YMkczqz+XNzMoIePq9F8LPd+KZp37uerdqV45v09RPn9398sCpz975/fjHBkN74qavP/nMrSMR1z4bHfjK97U7WkurBjp8'
        b'Hlgb4jTKvdb7kVaZ3on2k8mhvhFvpDotmgblux4zvHXze2u7mE+fSVr14udvjN894pctZjufNxY6mpaNHZUd/UP2Kq/Q018euOE1I+C2x63NSUmjX9VNnfKUy7jsa2+f'
        b'/tG/12FwdV79wicPOK+YuCVxYo9jvP0nrqff/Ljry8ilnaN7ds4yy1lbtHzX3bkzmld9tjDpjSq3j9+bPmnSXrezuuv/Pe/J1z/5wTE18KPYwGfXvRs16NUVJ2I8Slx3'
        b'/2q5qfqVaU1T27wjThuMMz82stf/6wEfipdkwUu97+T1zn0k95Wwfx8Zc2P0jEVZZd/OyIgcNLTqt9z1pXYKyzdD38lp7Sp6dkBy25iU91P+2HjwwC9PDfu4c7iQMums'
        b'Z+3GaSvGvp58Y7vXQPsNvZf9FsV+3lJx+NO37F9/5XGPjOe6St8tOPJ4YFm6ZLZxvt/AuD0fe+ilLoms7XDLsH1sj8fvBd/13B7oesv9ce+Kb77b11bjezL/2v66kNyz'
        b'P7c98+2q/TcNb710LPLWnP1ZA96eHhPRWJZk/OadZpcN4zdv/FHZIkt87qdZftnfyX7Xczi9pav8rfajX6a/tPK35ye93PWHY+KtU+8uv741ASZL7x3LHH7V7404l/RN'
        b'palXnkzsXlb2tSL1w3PD428W9lbfWJRmGvPytVtPhS4If3xU96J16wOtb7U2FQ3/4K0DYV9+H/LrsjvzwuvejTl4NX9sVM2b+OsI47BK23Xjjj11XTn+vafelJm88OhX'
        b'd3Te3TMTrD9znKoOK3cCz2zMYOjzBjnbtnuh2JjpqZRwYJ2CgskMHAhj7ao7CE8K5nBaRjiLs1DHFdkHyMnUqHByxHY47sZ0s/pDpfBtnhyCV4TdG7GEAtM0IRBD1jIF'
        b'1yLsCXMO1VK9ikOxCy6yZ8OhE7tNsVGjHxexYDry4IC4P4uIB9W2WppZGlosDxtYf8zxEvRuga57uCVr1lhLhy2sOxv8xznqCplw3phksYdTcziErn4YnugHHh0saell'
        b'8Sw3wNhIOKZGrpklFRvrC1hhtZGH+XKGSqUzOaz6VLOroVqFvoQm2BuvcKCMkhRKmrtHnIUNmRyFdBkalodOU6teBRqljLshgH3YtKBfqM1lLhL0uC5h9YWYQzE5xGqV'
        b'2lErHbCZ0clk8WSlPxkVuif66QiGRqRdhI04Ych1iNiJORnOcIph5on0rQtnJHeyPXN00yZo2EY9CsCxdOZUgDkUINs0H4GaEdkKsjt39gu1iV2KKXxGlcClVQrcIe8L'
        b'0onHl0I5B8NdhRoz2I2NhMzUGQAZIflUEQhPN4K9HBbkQzHVLhTvqYkNWoyNKiOBNmxSYomPD3TAYbzgJwl6GyQn3eFcIZiPzVBNAa7O0QzbyCLCd4WzeoeRWd5LNZUb'
        b'HJni13CpPeZK0I0nLXi7SoDweYpFmA+N65lCUwcOi3gWiq2ZGnLlQjjEFZ2SJe70E0fhBVs2VUfCSajChgiFb4CzLhEQukXYsx7PshuewCTcRUUAAzc/N0O4AFcpX2QN'
        b'XXJPIZWp9IYkkwnDIWoMAHt8EltAloRRxkrMG80sLMLtsUAbqnoWqln3VFjVK+FsUBxpQDiO62wlDaIZGLLTME4drK8+ljzPweY+mxTCqqSpkHtLUrV9QIhC0jruAQKr'
        b'4Crri7EX7r4nPqU/va26Yk6WMJvfeaSOdqjNVmgiRdqpI9Sdhh3DlCIprdyBmZDoLBAJb3V8InvRAi9uwEsbFFohBrFmJC+zNBnKpsJhpSbuL2EOz3LDjW4jrFHAvlmq'
        b'MIAUeGwFV7iqv4I0poRDGJNwH9+UBGkJxe6x9XZx/VD7zQqtyISBUMF6uTZktgbAmBioGgwKYIQuJQMwRm7HaoUvQxqO8BCHP4Kl3OKmHTu9+gUQPEfIpYEbThrK7Sua'
        b'oHqmwsRNE0JwAFw25i2uhF0M1m5CeOarcHY96bCenzTyEdjHo8xCq2cCEWA6tIIaOsERNu9FOBfojDtWaBtvuULLNlbwNKgwxFKXQLJ9YwV5qCDCwSEnCVv9VnHfGvVY'
        b'N5Zl2OWIRcxZY+vUYIlscTu5QwEsWWxH5TjCQ5IV0oEd4mLogQPcTisXL4rOQS5kJZcyKy4FYdRKUiUaCXog6/F2sk3UK5ywnBAsYBNcFCfhUW6OgbVb4IraqIfjTE9k'
        b'Uque+WtUSNZm2KG2ZuuzZQtl5mxkTPc4Wv1/BoLdq5H9790lXjekkJxIZhrPOPJ/U/78P18vbhcsOYJRzhCN9NNEtGeacBfRSRzONOMUL0hxjZLIddkcPyjpGkkOopXo'
        b'IFmIJqK1xPThqoiG/LeRNIRh0qhuneYZQv4aIppJNJYhxzmaicNkQ5hu3JDksxWHkR9akhkrjaEuJXodudnxXg0z7W2k2wymk1LOcuvrPZcz5NcN0rNi49KjE5OU1/Ui'
        b'07PWRCvjtO5J/0GgAyK7vEa15a9qVOavkL9kVFqhoMO/cLO6Q7jL/TYass+MALo890I7Nv6ZfKORbohovP9PJRxhMh4ydYFDSxxl7IoiHNttVBHboQGOc583K+E4N+w/'
        b'gLuhkzyOtGaWkkFqw6ghcFIOpdlOLNeq2TZaLQiC3aNUEeBHTJeTjbt7FpFd6TY62x67VVXJoJjXtM2CV9S81JY63ikf/aB6oGY8wwhAMTlSapypR44WB+8AN5+AJetX'
        b'baPkoME5mPsCUYgaqD8amwLZ7Q/ZMOvxtJ/GQpuacyugXUoegUX8DqMxwdEPy1wJPxS6PnMkWdKdxhM8lnirOjBttK6QhIe5D+RDwWS9a8UHWU8rxlbzJQ5a9x6r4LC+'
        b'6QI589tMXbmSEdEijbm5NmWwyo75Ss4aTI4W1ou+ksJUXoZptyjnE2MTv10favFEZOLtqQMk5UUycyv3vxAX0pMyYK5l9YHXe77ouhw4bGwmOPdGFgyp8883mzcPLK39'
        b'1sbWtMUNm55fesh+4fW64vMni3cHzPWp3mvn8e6cx/QWL7C0PHooI2d+x5ZPbihfmHnr+RT7+A0rwmOPx9Y6Gz19+8sK+5Kbz/ZcNQq4rLPSAieFrTLw0Uv63rvdNLaz'
        b'Z96U3WODhWJTRfvuk8YTTy+ybDv9eFbDm7UOl8e86r95y+iuFVcsfnYsDZiY4Ng44MPfZ0ouc54Yu9T8YsmjNe//2Dz6m8DkvGPv7xgZsjPcwNtnwaO1l574d3nE+adu'
        b'ny518rU2GX5h13eXPpqUfKEkJjzszPyFTw4cpHgvrPD1Vw6br2jIOJA8fXbbDwNGjQu1adKJeOrTDxvdorYPlRXcrvvg1f2vfPxoS0vnkEde/lls/3h3wXdJN0YPrt72'
        b'8nCn70JXlse8+9z22v2lk5fO+kp31Y3IxjGTog2C5gd77xzt/28DH6c7i1uf+XXLu5YRt5I/OD1rxjdT8t9NPHFnanXIgEdv5e8KOP9SrZXycNuGCL1gozyDRa5RV7ob'
        b'3N48Mq++bIBdaP60+c9BoN7dpN+tDz2TOaJ5U9vIwqsbbndjW8eklxZ/+UF5eaPjR8PTGzeO+SixJijulCxi79Cxqzoq9psnRi66/PaLXxw1WGoUcXXE6gynSRuNLpQN'
        b'2L/00eWTNjfc2RXwgvK5u1MX1wW++uSB7sSri5Peu36z+8aKl/z9ZyZ9sfBfTxq7+i8/8JX/oYNZ31r9lAKRr/To/DjZPm3qsxY/ff3hhPSvTWY8c35JuUdx47NXPi3p'
        b'fn1s5udbX5o5OezZkCdaf/lRf/jhr8c1Nv02ZfvC+pv2AwcfP2r3VvubS/DjMa/cWPqvZLcP9PDNY+WhW76LKp594a1tT/gnPdJt//Sjha+ZXmqJuf1+pXvoBY+Ux9s9'
        b'vha7Emy+f/ZKoc3OabPdpj/v9ePOxWnXPt+de85r9KbAnRe2i8/LLQpKVjmOT+cuwoMIG9Vn1gbk0P4zW0fnbMZdDiMPWtSmlXgIa2XYJUIr1iVy1vvUIKhQS5C+eIgJ'
        b'kd5QzVmMs3AGd/cZ+ZFFFbCY2fjVmDIWwxB34G6VqAdHZzFpzxqrmKleDO6EKm2vzZ3T+7uMa4J8zkE1yrCeMNtjXTi7rWG1MzK5HWEunCS7oMphtV7CXGyL4TaMp5fE'
        b'qzl70Q5aRm2Yz9xFexoTIUzFnzg7bs2EJiIyMQ81uE9O5NMzUMVIM3xOhAKv4lknZ+4BjHRPMUDCXKU769ziYQ7UjnyDowg1iYLORhGP4l7M4fzgMV/owb0zVeaNAlxa'
        b'h9yn2gLIm6rcREjOHKYFUttSw40SYYlyoZOzZZ0epHnc+hELIF8G+eLmdAfWI1tLbCDMra4gLRXNcd90OBrAhfF8POIAR1P7uGmogktcAGiFNtL4Dg38iJrGBpJhXoDH'
        b'8CQb4zgdyGNe3AR6tXaRaUl2yoioS9ubMUKvv/xApAejqVR+OG/PbZaboperzeHJQVPHxQ9Ct3ZucH8ce6O1XGI0LOyzbcRmLOEyTCPW4B7OJFMGWX8xZZF98RjHRcSH'
        b'KbgsgHWDuB+iag/W8mw4O1ZJXf1T49NJuEMGjSJUrDViDxdh3ngq85dRwdw0QwZEHDgUiWe4ir4sEDsUbgFpPEM6qXTaWnNL2SN4kfvqItJ36wwFaQ6nGZyAfH1jKRZq'
        b'7Pj753BHBHakbL/Xcx0emJnOXNzvwK5hKmwERUbgvkl/Bo4gZDjNOedmPK6rJGdct7Y4S2TZ2GhO6lbocFeoxNgBeEIlyQ4nQ01njn0a5HFhFU9jFxdYycpRCbP5k1Uq'
        b'H1EPzqi8EDozTIK1F+wjR2q9/70sOeXH8zcwYg6DXXgRS/3YUk7Gs/IgEXdEQzMfvkuJmKuyjsXC5aqQnQeghfUqaO1GjVfH9VinQWSsg3Z+OXOVCOs0RrscLqhlBuZk'
        b'RhSs4+R266BS5S4OmnypbS8/7rEWCvWnSGuyoZCVgseg3Vj9mLA7s2erGZ4R1nJs8sZmNm6DZlBZxxsO0QlLxp660jL0l2A3nrNjBs5wbChZPaVBjMHZAcegWFsHM36F'
        b'7gC8DKeYJ8iV81209lpjrNXaavtMiLE5ntU8JyO7H1OpJ5iskNnJJhDJt5HbLl81ERlf1b/KYLzshEU60Ak7gXtddEw3pyUFEcnPTRWjTIaFkCsbmU6KoqOlxAayqalQ'
        b'NHhpNgXSjFpKyGvx/1GK+l/5kdH2E2OsNou5+NfkqWQq0+gza2LyXzKjkdqJJDOExm6nUg+RfayZlxgq71gwSUefSVvDZMPTiFxEUpayIcyK2Jp5r5eorbBE/zNfMKRM'
        b'I5qW9GUmMiNmzaxL5C9qkczK1OE+7y1EucRr1JfpS/fb5zLpSSUpcVOR1/6XFsYqScmpHxnf/hs2KHUPNy9mzad2XtYPjMc+MJJi8WPSuUAYSYH3NL4uc/7CfMEwDzDJ'
        b'5OO6nsrY9rqRtvXrdYWWJWraEJqbgkXTVtOPafSDBpC7bqAx7buup7K4u26kbQp33bifERqzeWL2OIwgnP4D/+/uGvqskC6S6j3peKwhKX0TuSSXXET7NcyFjPg//ZSM'
        b'ZEYybstRDqV4SgnkaLhH2hWFwdggj4MT2Q+24JoiCNxliqCJKKynseaSHmrN1c9+gx4GrsK91lyLAjMCyd+zZwx0Hz9p4uQJHu5wAc6lp6dlbshQkj36HGHO2vE8ORa6'
        b'sMMUC7FH38jQxMBYARVQRE6lvbgvZDHuwQPh5PBpxUsKRRK2ZpjTHu+HmsV0Wk7A1hXChIB4/m3ehLnucqru3o1nhYnBo7jr8n1wcq47GSF3V8gV3Ffj+Qwz8nWq0RB3'
        b'XUGYlGUnTIIOyGe630zcA4XuhFQeUdAmeFBTIG4Bco4wjznuZIQnYxM55SZvgFpuiNGK++G8OyGq5zJJ8IS9mezrLZBn506oPIVi6IQp0XiZfb1+G3ZDB/ljKnRgtzDV'
        b'cyprigUWbCGMMZGgA+KEadYGvNnnMGcGpeW8FCgT5mVDHYeNV2ETNFMtrhf544rgRSjVy3vfnaSnJD2aPwwuCvPHkJbTb71C/JU0+AVewU7y2TCT9ZPwKM1EjCb9WRiL'
        b'LcLCjXictQSKVk5SyiiDdTZAWLQ8hRfcGxSpJJ3xHjNe8Ia9WMSLOIcVq5B2xmeYkeBDOOTDrN2JSVQVQ9rtC3WzyUfjclayjq81UhcMfli7SvBbkqqKr0DIWoEdpNX+'
        b'5K16wX8h7GIENzam34vUG2wPFJPPo3CGFZ+NRSnYQRoeOFkpBJJJco61cfpCK+wgDQ+C3HQhKA2Os2/tEmZjB2n5YifcIyzGiwtYywdgsTXVlS+Bw9BMPg/gHpYb27KC'
        b'FaThwdDjTD72O7CGB+JeHYVEPdM1+gshDu7cp0TvaNilIM0OzYJOIRR64DTLjN2+CgVpdVhYqhCWgIWsyU5QFabQoY5pa/G0EB4BB1ne2XhynII0eemk1cLSUXCC07qR'
        b'sp8K0uZlY+cJy0as5NNvxyCqACd/LSfTrYJ89hpyI4bz5KcbSkmrV+CpYGHFSDjA6oyFxhQoJc1eaUK6vhKrk1m713lBNVbqUF9zpXBacIPzqawtZvYrsZJGxYCWQcK4'
        b'0GjeyXOEa71MrYBH2mCjMHIkoRP9PoishnNYSQp3ngkXBOdl2MvXwoFwrAshvR8DXcvIR5sny76cyAkXsFKPYii7VgvjrbCZk7t2fTy1sxBc8Hiq4JKWzgqZRF1LhpAW'
        b'2kdAkWAfgw2OLhm25MHqAYuZMUGpM4VB0uBTMjKSp0jh1TLsnmyWQUWiJCyey56RD3ciXcLONJLpLMlAtxtWDtksC7BOXRAeMFRloqUQ3qqGGbEYky7uJmU4JwSTTDJR'
        b'sBxDHpNdZz+3dKrQ8dA0ppWaCsksSBGltIj9mM8MXQj7VsnKoJmg25LkkQTLASyLyA1d2u3X8DLGJQ3nj0XyWCeUv185y43XQaS5PGc9qCGthEskgzfwiA3uUI5XnR+B'
        b'PFaH3ij+OlZns/fxsBG0a7rZmUxaZ6eixVxdnuMiYbxPkxbKCC/cRahgK6np0KzHajDCvalYutaV0VM2St3FvRMYkfyhwJ7SyI0IRKSMmhm8e+lYwIvPHU+29FIVneKh'
        b'a5zeGlUPRCtWgDXmGTACkedQHzZOz4J3wTeNXXOmDlzEHpEqxvFc1AtIJ1xmncgi+zitZng0M9gsJcOI7UZG1EcsJdRpkiVCZKO1PGU26yR5DoVEDCI5ZqgoQWS/0+zu'
        b'czQeX6iqDEtXT3emTWWkgH3T2bSxhl3zNZ0ZN041/8zIaUBJ4mHMStmIOVDrDK2JtLpcbE9TUQyOwiU2P+Ek9E5R1SPDY4tpm9TDmjCaEYWcwM5sgsuGUsEA22dwogSa'
        b'sBKwYQQ5EdUNMYnTg1p1d3G/Pb/HrfU1Y/2AQqofddYbqeptBOSxKnTgLJ94ywfrzesb9C5CC0qvAeTEvMJIikcHQw51oUKr2EfzVGALo3oaHghiRN0LTTzLDFUxI8n5'
        b'wGS/DszpIymfhnTF7grhJGkby+hqiK1Zmu7wkSa5Qsk2R2nixI09sXu8qzPmwYlxjLBpnCJjyKnKffZWkFORrrImQ/o8R73mlwrMCgxP+sIh58l4kA6bTCZYepJn7knc'
        b'2Qx1pV2raqQsDvZALZs/rCtp01hft5JRKORTUGaNlTTHDNWGUBzGCLrNnerG2cYkDdJa6AWmrBI3LNfnQ04d0pOdiM9Rvpjy57NOkEVeZc4qKYELMslWVBVxAsr5lkOd'
        b'UzerVnPpZlqfbA2nA+H7+KAswuaFqq44425o1cOd6oluLnIDz71QY82zFEKzjEzXXtX0mqPHF+3OjbiTjwRWjB7DKuEluMExvi9dXEwXnGpU/aDBWW+eil6zF7HRCocD'
        b'5lhqNI4NqZ6XqqOZeN5RZF31whMRftQv/lXYj8U0MJo+nJUgZxnWfMK4yd1pc1S241vGSoKtOXfo9O6W5dxoTs/eSDiaSMSNxVFG24NH8i/dQwyEE7pk4kVFJT09SBXy'
        b'6BvZAOFMtD99fVU0WT7sS0WIXHh0mzlz+LNRbsO/fNzbRHh21kxyRkUlYdQM/uWTtrrCUzNJk22j/OsGTeVf2ribCzeCFhBmLsol38xYZfFnoBC+nOpMDtIo//ZZbvzL'
        b'BaMHCvLVYbSi7JOZW/iXHut1BG9jZg2fdG25Pf/ywBpJKFIqWDf1/SMEZvb8ffAg4dmEZbT2GY6mfkT2C13IHsge0RGWWQ2kRfgv0vfmuX/dpCuErmNtTWrIXCB8cvgQ'
        b'/ff0bFZB9lo9oWHpYPrU6PCmAcIn7uzfD7PZSTyBsBDFdD8TUgOGCqk6kzkrchR6ZjuTYztrFFQKWbEG3PyYzoHp2LtUPdGgYb7WPLPFLlbhBqWVsGx1BK0w+wdJpgpL'
        b'ZWQpfJgRQhs+o2R1cH9rR40rMXrLkaCyd+QRkjSRkRJU0I/rOokpsXFZ6sBIRsKfBUYyNewLjETxf3hw2TDnQGrry6wJA/wJW3w2CPc9LNgUnMXDirnxeIr1ocZymWDr'
        b'HSWSeTZkmoUVGZXAwMTKy4EyZTqp54MlUxcEPxNoucSsZcuW+M31nzx97YfHxzqV2H1+4j1ZduCqwV6wxmLUmcBH58wbZlvv9XnripgqWcf4z0yjXqy8+PG6VRfTEld1'
        b'xMa9/a/3apWpYdXTwj65UTDNdu2Up2xLh636cMmOQjtfh5M7nR6x9rL54NsX5wxw7Xxx7qABUwp/uLij9GLeMwcfH7jqCQ//96elRA3x3KBwv1j2Jg72WjI5za7Lp+Yd'
        b'Y7t9DU8NbpSNTZsc1/ShzY1f6l+e8sPqoXHpH45+03zw2H+f+9fbBob7nn582hS4POuJzT/1PO2bbn0p+Kuu4o6j3zUGHMStWxTVll2paUNjb0T5rncK3briq8MzenzK'
        b'bZ5v+774B9fPr3k7DvljsPeib4eYvvT8gpDdgaaxJY9lfrhwaqZX3Ng6l2/8iyPcMp6qumTWXH1h8rwX0g79O7PgmXqIc0uZGvzb4/s6jhz48FrHy/IlN1rbCn858+OJ'
        b'C3NMXIPPFHTI9rrkXFn7flOax4ZFo283fWgVqFyy8Hzjvyebbv3Ct6x5FY56Mdj5WMYTj9w6fS7s5++tfjG9m7XT/qldOpdDKwYdmzbRccWM5vwnz8//JdAmaM2dF5+s'
        b'fa5+erWRvp9PzuU9EzNefO/NsucnfnDQc9uZncNe35Qdofig+ET2FwXfTUgY8liqyyH71yvtjqXFnArIHXrQL+GrcQPqA/xuJuxMeSaxZ8hjeik+Px18qz1hZqjjz8tu'
        b'v/WzzuNnx678tbP8k53fjB8zZuVH5a9WjDn04k2r+pBXzsbdtL8gf90ye9rY1/CNKz+vTx53d99rA1e/99EnMzyf+GDTM9fGfmG82uPp9EuHqkbdbL3jl5f81Wynl74s'
        b'fCTi7Cl/x3eP5PzUPPHE+6a/lD9+4Q/DgZP/kJZPfOfc/C8cTdjFYAwWE0a0YzxhQMm8DtIRdLJFPDV/JtMihEMvHsFS7spB7hDjLUKHlTG74V3sSc21yX7vNwR7mNNs'
        b'PCKToFGHqyza7Zm//g68QKRFme52Q3EC5KsciFwxW+2M5XDGV0eQj4U9sSL0Rulw9VEVXMVK6s/HBxuwxsVHLigyJdKEXpUfHiwdEuzn4iDDWm8tW7X6xezhQqy2IQWP'
        b'I42Rw0kiRYm0b1CSrooJuAu6CNNZlrFER5CgQwy3gG5+j0wOmXwtGzUsd6JmanhuHbc+6lwayKAf6ZFO1LBcV8LL0LiZlepmE+rH7GFolftDB4lQ6w8neNCLLjwPHaQv'
        b'AtQzPdTc5Zmsk552UMX9HRH5r0vlkIj6OxqLuY5D/28NXf78xlDvb17MXjdUxkSnRCYmRyfEsfvZK3SH/iv2LtuFALnKJ8ODfwwl7qfBkFmumMjsmd9taqVC7WOsmEcH'
        b'E+YDnHqLoJYu3CeEBbWMkVmS33bMwwP1wG3GLGskZjFjyH5TWxsHFp9UfbcrJ/nNRDcx7QPNnaDsuiwxOUHrOvYvkudDjWkKLauHmqbQ+86/cOFKf5601rp0ZexcIDY6'
        b'9DuIgnQIb1gqWK2W6+PO8f28uBqqT0YamlMLAyiqsFdSvKHGe6v8T7233ofApKfm/eG5bQIffFNIddCkTile+qdoT+m+unQC2ZG61lXGEGbjbaKSpmzdKDBbk6EzCNdP'
        b'oTmlSx1UEEEHb58Qb7pIfXQEzy26DstxX+Kmbw7JlRRr/FjpnC/0Xonyjn423mHvp1GrHj23O2dPTd6E/MZDbcVtuSMP5nToCKnf6d4e+qKjxHaZlEkjycYHLWSnYm5k'
        b'dGcQ3j0XTzFFMmHy64Yq5uPh+zwYcRU2tnirYRcPuAW+rohZGxezLpJxKWwRjf/ri2i74MCd3m8eEUkdFkdSTwh99lhaJauntJioNaGlfvP2Y828/Yj8NdBQFZ32L87b'
        b'HcJXJtozdy550286ES2o7zBv2KVy3gVNnvehRCgEKADLdaEE6uBUOHUwaq3A6kewnt38bZ841s+FBqjZJafQKfshkqFfCrsuWmACR5yh1Bb3BkqCZC4K4d5slsR7UqRN'
        b'g64kRLm89YgRjb3JNvVzadF+/oGBFFCmHwS5cERSwi499krMBkPBUpiyzdQsymV5hp+gpGzt6/ONQ4yfur5+g4wGlxEmlTP22TyRYgy9R5oStjw3kbDllKCZE+U0sig5'
        b'kJ5d+KJ14NhqQUmvqF5fuDskLOOnjTJB9u5oHXHMjgJW24QsivoZP5gU4e873FlQUvSu12dXP5CEI4WCQlDoPsrypQfSIKLeYw1so1wuuA3l+V5bGf6BjvBDpGAimBQ8'
        b'ozQlXy1bmPnBR2SE7T2WCtZu9kp6FjWFJ4WEGWcarw8lLO31l1zFqhnfK5m1mOtkpoltdHAcR60oBrTJPtwwg+3qDEu9/qs3XjZ92uVpsnT0xO7fpYlvDmH1vrOu9WVB'
        b'+KhccBQcjzzNvvo59dTLcqHxMcFJcHpqNfsqRJlcKgoOg4QIISIkk7Uu9MIjpTTU+k3jxUL+lwXsO3+bs6Uvkon3wWpjocAxnAmDMjsiB/owkI87ITGU2sAFyRcuLEl0'
        b'G39AUjaRWdn2ts6C4OkpN+YYjUmY9NKuzDtPP+k89amRRoNas4seXzlFz9bKRy4vNpO7Tdkhjvk2KTpLMWJOd47pXrtCn4+cPlybM2nIze+++27PzepLuWUjR//w8iLb'
        b'ooPD5g76tTS0bPeNvJUHbhTFKkNHe35a2li/Zvz07Kxy+/wXCp5bO9Z27Ia5H11+e56FR9O2QyG27755JeHEeFvDWd0GtXdW743xy1DkFus4r35xZ+nTRtYRUmZn0kfN'
        b'hm0f7jWZ9vLd529H97wQ/9OoJz6bolw9ycw57KbvvtqEoNZcm5+bL+WuXz353Dd2b1rvrfzyl1VHVslW3vrI9bcPLw1Z/Ep26w+r2l/wcL8bni3/952Y6t6U98LyZb9Z'
        b'rShSvK93vndt1EubbF6vNbo5//aBpvCgHe02n/14aoreq4MHVd7+/dfbPt+Gfu2/feHZD1OfPRb5wrEfZtQ4T2pu/XR+xIsTf6tanvK8e/dN2xu7Z35u0jHLo3rgJ9vf'
        b'jQt1ApOrdy4V3DWxm1ju98hn85s+uV0V/tvtHe/4H7wzrOm3dd/dHd76Xu6zY1Mc3rwTNyX6+QvBZYt+uDP+8wUGXxR+KXnGu3qs0x9xV3xu6/G0mWaOZtxyqMERr/g5'
        b'UktAXUF3AFQmSE5wCjgKIXMO9FKuiEP79GG3LbZIqTI7Zu8RLmVTqwws2R7gIgjyCSKcsR7PoyXlYh40MB7Mh2Qo1SOv1sBRzJe2wR5vHkuoMwPOKdMzM41NoNzUFNvJ'
        b'Pmy0QUewwmMyqIZOQ87lnYeTsylbWhfIOVPKls4VWfXp2ABVWCrZBsAZahudJy5yCeWsY1Ustjr7qlhAXXLgHAmWLHEPXGWFzk+krF4p7LDkLCLlD6FmPTeUvzwmkbCV'
        b'KkbYQKGzQYJKGs+S02of7okhrzq6UtMGXTyjFyWNssYCbl1RhIfgtLMazREJxyigYypcZNYVcVAIjbTkIh8a61IB1eOhTcJqLOYohk14VvTzCVAROiIdr0px0GbAqdA1'
        b'hgYHU51sE+AKPdzKYlRom9OkgRT06u9Ixs9p1XTS02rY81+qpv+J4W8/vrPvtGNH5sG/c2SONdFhEWQYb2lCeEkzVZR6ajVgy7hDyifSWC+UxzRi3sK4vzGak3Kbuoyr'
        b'pPwp5SuprbVEnjJra24foCqfcqBpn2g4Sp3r8vXR6Wuvy2Oj06OvGyTEpUemJ6Ynxf1dHlOW9hkt83P68anm1Kb1WP7tU/vr4dqnNjMZPuaFFfcc23pklhcIVgFyS9wp'
        b'xEgqNk2uzfVRtoVph8V4mQbbLz3Uw8R9zlbk9/F98kByeNuytUoEwqNEtKLQ62JySJCJbAEXpvrIcCfsx+7EVRk+opKuhVnVr3wR9WnU51H+0dmWX8YZMq8gQ1tl64/9'
        b'S8sniOxP9fLXjenA9J9gTn9ngq1N+0Iz5HI+QJ/3N+zQZryke8eRvhz2t8exxUx7HClfGoRFszi9+o0kXCa7yxgvndD1eOZ/NpL3cfCy+0ZSFpj4TFmDwFz+/z73eT5E'
        b'SfFrYr2j9ePfm63vryeMuC7zGTzuLw6S8r8bpHVpX947SJ89bJA+6z9I9OVlf3uQmu4bpM2J2OAceN8gYReQQcLjOlGJWx88SNTappAOk1goj5f/xWFaqz1MdIjuD8pg'
        b'GMggBRYDvLEAd/Yx3oTrTp/KnbSsGi5ly4U5s5Xvb78dorsqibbJKZKy3GZ2ekKU0b7NLN+mLSL57tMhpuujR5zZskTg3gCKwmJDoEUwwybqrIQGG9gL+1h+l3W6hNmd'
        b'46EgzK53ui3PvxaKsCzEFfc7e/vIBN3lUsZUMT0jsTSoQabcQp6f+ei2zbPTTWC85fwXD22Y9W/d3W/M2y/TCfAt9f5sjqXlC/sclYrhxn5zfg6ckPjNi7uaT9x0Pd08'
        b'vn2i+/sjvULDjRaNPuOd/XzBb4nfRLxWmzc6xqDN02Zx95RXzo9J+UGn5dbAx78+6Xm3tDD5jYVP7vvX2VlfvZz1rx9/FR0nDoeeqY76jFFYBpeGTsA9zq4OVD2hC4cl'
        b'VwM9drAm4hHjfuyNNHN1qs86buR5ySedKjZY7F/qAWKXhEcWQh4enckO3ilEStqjiflMr7ywJXmTl8gKDti+dfhUaGYsCBaL1B+33XpVeFU8Q3bKM+zuagCWaS6vhkAt'
        b'N0muW2vj7M2un+SeYvZqaIWzYdyWtR5z6MWfNmzzMB6GNmjWu28hkiXzoNOpb3ka0T10fWx8JD3w2Oqc9XdWZwq9kzFRIaGs2elsIaZ9pbViw2kt8nsARfc1U0r7mr4T'
        b'rm4XK2Ll3163py3uvZQZMcXLbzpcYdurtw85LTlNR2CeHOsH+fTbCw1Uv5VW90T0qpJVGVXpxUuxUpnILmmkPhc58fqxslh5nn6uuEIepxOrE6ubJ8TqxeqXSSt0SdqA'
        b'pQ1ZWo+kFSxtxNL6JG3M0iYsbUDSpixtxtKGJG3O0hYsrSDpASxtydJGJD2Qpa1Y2pikB7G0NUubkPRglh7C0qYkPZSlh7G0GY06RnplEzs8T3+FeZxOvBBnniuUiyvM'
        b'yRN6IWVAdqwRsbbkqUXsSLYv2V3XC4hOofZ7v7r2iyNDg0/ZJvNHPLJW/zgzhC+ku3K/TVJzVUWNDZn/IWavxkhLTzUDzXYp/9PtUhXB6Nfc/xi+qF8L+8IX/VmwILog'
        b'eLwi+hcNSxTNi1g8f6FtfGLSAyIfaWYTncL6923ZwwMzmDPjfYMhh63txXA4gUZNcQ1XgZ2gBYtc3ERhkajnCQ0DmVst7IGDpor1G0LII3W+UH16X4BFAdDGxBvmZCrG'
        b'Vt9oGFay7djbwol7jYG9E7njGCiHHHa7YgXHBvYFd6WhXf2VW0zMuC6ZmuhVO/sGuLni5ZnUVbizKAwYK8Mjj6Szm5x5oUQSnOgrCekxIp4V8IIyhd39pOElPE82UH9R'
        b'WAi9NHQxtLsxeJ1zNJT5UXfy1JW8InUWnpPwUCye5PVdwI4ALHUQyeZKkbGl/tTfPB6XzXNczhq7PcLAb+U0aPEmLaIFmI6SLVuF5dw/1y43pUoeoh2BCxIRzAq3wHHY'
        b'w5/vicb9RJhyIjmoPrpUwhJq2WCIV9g1hhxObtB2XHQOGiQ8PQbPcu9dZ+HCAJXzAqzPVvkvCLTnFnsF06CEO4mCdksWcLrJnJs15BBSF6j8QLlCBXcFpYfFXNHeBF2b'
        b'+vtygiY8KRtIRrE+6Ze7d+/+vozeOAlkksUaXVjObbbK4QCWh6TAMZIYKYwMxmp2Dp+MlbOs387LSFq5fTO9PWNWBeWb3LnLJryKV7XdNulMxUYX9uorQfx61lZI9J9j'
        b'aK6yyMiDI34qH1KwG45wP1JYEsuDCe1aOszZVanlSYq5kcJefzZQ0ghqNcQjtBtMkEaHwEGsh1PMe5NlAHRQP09w2vZP4upWQSWnTye2G/rhEcghM4ZJD2TkTPCELGIQ'
        b'liS+ZfeqXEmtkT8fPmbr3p4UHG+0wOdQ27BP7py//u5TeulfvtNSOqhGJ/hEbuWS1Z8vGLziwwFf1r27vGTJiDlvubxyWd7YHPNG5eurPZpWbI7IzT+57Z1f3zFZ8WM3'
        b'nrRq2flOqmnxE7qR18au9lyWm3vnq5wzhjP1Jk94r6P9k5DXYk/MzTyzMnlLxLVDn4amR3ZaVf/2Q+hrNV8a1X6zaPauWRXbRqfY9sQMnTj2pcGZy07igPBvMj/81jEu'
        b'45vHamzkYUcWj9Udbnk8ZIP7tmi7nrWLdL+8MWd6l6Lny9CWGf/6+vOBX3w446u9aR+HHozxSOiy6iqqTLiQnv1JSnDrbefV3h9371nh7fH7/km9Y748v+7rVYM/NTsU'
        b'kPKWftzIqtf9fcoDmzbH+K7xDXt7vZWP1RMue11+rXVZdneBz2yHz+zG3Kl1sfvo6tOrPIMVjcerFrwR5/tr/Y2P0iKfv7smfIhi47Xtvws/xxz4aXSt4xCmMFsUM4Oz'
        b'HGQmFFO2A1qD4SC71VjlCB1+/k5u/PRUJHkSJglPZWMFv2nZP5hj1/lFPotW2wDHtk5N4aCm3VljVTE8+IX7CKxTxfDowIMcTdGxGXer4WU9kH/f5by+ynuHNZyNpfoV'
        b'10BHeidK2d3J2KAKqT1gNTngNVubQpnqKeFhrF/AgWfHsV1iuDO9FKrxgzw4zxgqX+gxIu/RTY/veOmr6f2TfFoIFDMclxxLdKE0iGx7zm6CLEkMX27KFZ5t2bCf+Q31'
        b'FyF/Fdkijouw20jiV0g1cGwQlBpBWZB696OBNAaLjCRmBlDI1ER035swUrXzWXjKoAZ3hTDcyFKk6NnSILr5OWE53/8stsjgAjTZc0/2p6F9PqtftQcqlhCuspz0GdoX'
        b'sEasSwuk8QlUW6BiTMJGCU+Q1XaRPV2GO9JoqBnI1fZYsAgrGc5oHZ7COtLGXCgI0tqxTA1k6XgKTjIG11wPWlgDPM2Y5zldfWkwnnZgrQuGRn06HGTD2Oyh2jIssE6G'
        b'OZugiBGexg8/zEBXbNtQIPUe2SLhhSXQzWnYsMgFSqHdIEi9TZt4yRbCeV2G/XE0HbxuFJfJHuTjbU6GnjlczGBTIxouroDSxUuwQhMv3SRBNg0OSayrsM+cyDcs6gk0'
        b'TFTvOxZTZNBLqLOXT+JLaYQUpYyJnAi7VXykhYkM6idAs6POn98CGfxT3IHGZf+5v8OSbxcMDRlDbsSUrfoiv0SjABgWlpn9UDcBhkx9Sy/EdEUjuSWDwhgyZ/7qb/mP'
        b'kWTG1Lh/J7+huNlMxSfe66lfBaH5tL8Qr/+X7xcl/qpTPzKt/9uiwt5h2qCZ+xr7V31l3xAe6iv7OdIu7o5fU4PGE78d83+v4kf7fML/E9f7vDHX9SKViQkpD3WGf03d'
        b'IF692hk+fS86PSPtb7q0TuD1yiPXTFzzkEpf1lTqsDApOsE2Md42MZ3H3Zw3cZ6GBv/EV3nww+n/mqbmYcxddVpcbGJ6atrfDjegqu3q/2PuO+CqvM+Fz2DvJaCiooLI'
        b'RnAALhBlLwUFXOwpAnJAFAdL9t4b2RtkigylfZ70drdpOpImTXdv0oymzW172yZtv+f/vgcERZuk9/7uF39ROOd9//PZU/jS2X68Ott26Wx8h4HPvzvpwSqGXk2Oio+J'
        b'f+mV/mR1VhOu8Hy4JM2Qfy3yi04fszJ99I3oyPSXt1f42er0RqvT86/9W1uX57PAXjbzL1dnNlsBq7Q1KEXwxQ/xBeePio4gUHnJ/L9ZnX8Hh0vc8/9W/XvF0BUIfcm0'
        b'765Ou3MdTH+hiVdvesUG9JKJ31+d2HitWszOfEUnXj+5dG6OiT0bdSJcjToRFAlIuxeSdi/gtHshp90L7go3ykpjQz1vs1Z4QYTL56hmLuawXOZvwRv21OXgKyMumms8'
        b'nBbHOjo/hbLUaL4HAtf4Nyk57XnDwDrjwMp1PGd2t7P7WJarVi98q1Vard5brHNVoFAknIVFUyEnq+AQLl5i4io2OaxKrLy8Stp79gsKqYeuZOZy/Wo+uyiRJZDP3LHC'
        b'uVb3+TRyJSY2Os33s1dXZ8v4SEmapPiZWXW2oHZtlfV0xvBV9GGQ2Q44aQ7rzVeld6xeF7USEYK1XpzUD4/llOExPMKc/z1vyvPxUHStqbevizlvislCGPOmJMR8EFYW'
        b'6x7+zzp2wfKCXXPi/k9+Y8orBiScd59g/R17NTyfud4MaPhX3pbUsC98z8ovv2dJdNo68S1p/V2v98E8fWJ1UX/+Ardets4Lw2K9IQ+6gz7LtSfhIt07KQfs3s2Usfg6'
        b'LJuKuPw6N2h04CFCRv2CSAgDOKXHfbFVDEX8KzJ2Z7BeCNO7HeL3zLwjw/lwcg7UXol1j/QO9w5P+MVg5afRcbFxsd6RnuG+4cKP9a/oJ+gHBL9jI2uXEiMQTLQrvL49'
        b'47lgso0Dy1KDpYDDF8b6PHcmVpFXE2VqPndvKzNveD/PzPy7L3AxdWsjyDaYf2NizHnC+CLzglVP2GchyT7P0VMXFjAn4Rk+EeD1ll2JoSQtPjHR8Hp4YnzUS4y0QsFG'
        b'rETON9CVs5G17MsUKNAzEzd3X2+yVLOKT3j0nyJJKH3jXZH8fth3Ivb+p2e4SkyN3Lv0s4WWuMb71BlT77BjkkndqijT13I/DlHydhpO2OzYlKDvqN/aXHIkQV93wipK'
        b'UGJjEXbha/5o+OWqr3RA27fP6Mi/JrZtnJYVfF9G/9LpJ6YKfLz1PC6Em7vfgqGnbgs1eCh2g8FdfKRJGc5g64opV38Pb8y9ddeD9y+VmCSsWEdxAJ/wFtJb5ljKt0z0'
        b'tjZfQ2C0j/swK28IjPEvZ+OQqReMYa32Wssr3FflDCLhRhFeHrFbmBrNdTWAdjV+RUsBh80JBz1gVEYglyiCGqjbhYMrpXIalfG+lwd0ucCohZxAxkAIU5G4sMIn/pWn'
        b'SiFeEspdKYcrJz8vrmjzlfi4/7mYZVZXQmaN5rcy/IvY2YbrW8fd5OnFT74AOhVqbaiKri7IVHujwg1rKjRwbrMgdkhiUsRSWUBj6husYIPCivrwpsKKJP+mHC8UvynH'
        b'y6tvKqwIkG8qrMiAHGHgtsOfxb/f0HAN0fmIFnaFnRLL4VIg+Nl78d+vm6CmrCLiLMiGOE2MYJVDTJ2XFShBhQgWoQ961vFqLem/ktxnvX1ydfp1gihROfOByReqFmoV'
        b'asfIfnYvH/8WCRHKUSr3FJiXL0YQrcD51RTY2FGq5UIu4FuZxpWJUotS58ZVXP1OlgRWjShN7lMlbjX6UVrloigj7h0t7i2dqE33FOl7ZfpewJ6ok6c/+lG65XJRxlz5'
        b'B1lpCw/VQrVCjULNQu1C/RiVqM1RW7j3VPhx6Y9CnSKtdWu5OGoP59mU5dxvrAmNWqE6m61Qp3BToW6hHr2vEWUQtY17X1X6Pvd2nXzUdnrfhJuTvanOvaVLbyhy/kP2'
        b'hhq3v51sf7QDUdSuqN3cDtWjtDk6v/dNNSnk0z/hsdGpv9hPF7OOfDsbrn+C0Xz6V2IYTuR+LRNgDr/wNMPwVGZYuZYeTxC+bqAYEtS556Poq8g0prrFpxmmpYYnScIj'
        b'md4qecYv6JFGTCU5VTrV6izhklXNh7hRkmG4YWz89egk6bDJqTefGcbKyjAjPJW18XJ0fN7xyJSqZza4ysxOnAp0tjI8mZxkkmaYLonmdpCSmhyVzi1353pXq9RE5sf8'
        b'rWuzDtbXCFmtD8KufbVGiLhI/MJ8A6mv9Rfnn70Y7oiecbeu8OOrK1v5Qh7X1ZNk2hdd59rj31DNYnfOXVWUlaEHZ2eKSqYVkVpmGH0jXpLGPslgJxohNdBEbyAjSBck'
        b'1aj5NT2nZ2fEs0XSNzHpNFx4VBSBxwvWlBRF/xuGp6QkxyfRhGvtUC8RUNjVPZ/NoerLicJ+p3GABZOuLcjpvuo1wxos9+aKZ55x9/Zdqa0Fy1iojH0CY66ep/5lwcYv'
        b'0yu8ud0NxgTXsVDxzjkVzslnefAw1pqzAKgH0CIjkDURYhMMW3NFHhREOMxllgrggfENGIcq3qN3/xbOBVhiP05hn61AbCVQPyLCfCwyOoE96XvZE30hrKDy07ZRe5ms'
        b'44H5/ny3qEOmslAdiO1cUYuAnfDIXMR6aMjBuOTKfk5SqwsQed8V8hnFIRGZAm53WBCA7V5P94RF3il4j/WkKrfACh++LNnpZHnMhgErviLHNFYFS67JsloQAhtTKEmE'
        b'yvgMo1aB5Cv0bdq2H5+qZAFMKgVZA6pXbx7v9TSsAGOB4hvBuwp2bSq27Ve2iMkxN3r9FzZtQhPlPMt/3r39cPOmll+Uqxx917fM84DXabPhGc+L33jz+wFfDZ4+WBxk'
        b'2f3ePU/Jr34QvXNXSkT4a4WZjZYhqfPfA5di/7cwrFxVbTDj2sJETfLlKS97Y3iSuUmxWUO3+tU/mX6ScnTySeHX34n74X2tr51rr33fTeHU0jnJO/YTGsd//XM379Hh'
        b'P/zG/LH2oQOXrI973o2ZOHXtb8IdcHz6wx+b6vAFCMfCoZH31ositmKNcB8+IcmPMy8sYyeWr3jrYMaJd8Lx3rplE17MmzaDnDWe8wRFEcHiHE6stFwfwge8IzEYi3g/'
        b'Is5s4QRLMdTgxFpHopGvCHuhCye5kbOgZvtqZBOW7ZPWpJ/w5b4NOInVXnyIhKkce0ugqCOCLs1bnL9JHyqPYikxfl925WZyJCzPiKEBRk/vQ96JSULAPWdzayyhyx8R'
        b'yxIIDYossAc7pVUNtzo+dWLelHBuzDtWmMMd2X5tqCKB2VsI7fECmZ30D6sszn1lBM0ZfLy3sYq0fj/zHBqy/WAlZJvzBcGZdgqtyoRqlnICPXgo476TT400vXheKuDj'
        b'CNynEbRFqoQv1byPb8RhF6tv58UqyHEri0gRaEKjGCpNTnFHemaPDz3wFMnVAsRQDvU+suZ8ZcMBVpC+lEsHZbUCK7Den2XxQIW1lyVX2JBVZ3CDSXmolMNa/qAmfSFP'
        b'GvuQit3S2Acc3M6ZKC5jHuRKawTCID6SZkmyIoGXsY0vEjhMm5llsck0EZvU1JvLHBLo0ljLUEDK+HMhYJ8lonoj51jg59UEHJjYKMdFj6txceAqXI9rFkG+ndMLeDdW'
        b'pt56XvyCjtOrnHaNqvASZ6CYf3YDF9ZWZdqM4+fTHLIF76xNQ3zhkj+r/Vn2X5mAjyhLTcDPTbXq1rJbZeDPc+w13PnfaTH9muClbpjjK4v8LAbyFWa7zkZtw8tHTC4S'
        b'/39npWYSWPpGEhj7b52hOjX6anLaakdeEiXjktMTo5jkcz06ldMLDcNjw5lgtuFYq0FzLonR4amszevJVWlMaunmJKN4XvJjBpd0Zn/ZcDBJdBqT6MLCAlPTo8PCVpw1'
        b'ZleSk9KSuQRIM8PE+IjUcBqceQavh8cnhkckRr9QoEpbbbK8cq/0WnJqfGx8EhPqmDjuFp1KkHfTwjCZHUdGvGTj0Xhf5OoCXcMTJbTCL2rFzw+YF3NW/BN/t+Ks+JNC'
        b'LrOB9Zz9rw9NhVze02YrVrSeJ4+Yg8N+0tRKnkCmYcv/uB0/NHPPMxgriUwM5Q7+3zLnu3whsrW8zqDPWqFCmbzhqt5+Ep/gLPvZ288Sa8xXuAg7oucq+/O2XP3takc1'
        b'sPUlMfic3bFQ+MVi8FeQ+tmkl3RGtnCUxJ/8tTyWLZTFahZ7YzMsmHlawHAgH7rJPvTzZgY1GIFiZYd4bI2vDf+2QMJ4tVxQ+/thVlrvhX0rYq+uWbh3eGJMYsQHXz0b'
        b'9m5YUswHYSWxniwF41sCQYOKgnbvvKk4jQsQbUra/ezkQH9w8XkOTyLQFJcMHXIOHitvnAg9TCz9ARaq8gWhH2LJOQ5SRw3W3MIKoDqtOAVezqxX3RKf28QdwRjyZwLd'
        b'f+Gh2CDkfAM3hc8XgubZdWHnbuzYHttC2VMzVK7jZwdnzgOhf0LNYyv2SvtGwIgQe1d8FkLoCoKBMOjkvgogMattxWshhFwSi6cddON3v/uGkKtmYLQ/Z43bgnNaJMZ6'
        b'vvdOpC/nuNi8xnHRLxR8xUwxNOrHzzsuXuJxCv/CVxukoqQhk6n/oqt93onxL1Zx4gvd3ZfWOplevBqie8zKujF9YQfNYumJvsgShZFdpTDil4atx5jK/K3/OS7jRnwo'
        b'fEVIWmvUerHh5GpqdAxvpHgunGgD20ZqdFp6apLE0dB5tU27dNdhhskRCcTgX2KT2FiykfVNZ8FXCtjGGqFKof6sf5DluSAuvh0aoezZGHfI3q+YgKXQwPVtxW68J0Pq'
        b'OhRsXmfCWK+vn1GWx3JswKX4nT/ZIivxoxdP/6X7/bAPwt4L+3pEXMxwNHPGBH8pGCeqJoP77pnK7t39H69+641X3viyv7j3CkH7dFNOQshU03RzaZtncECT09SBsi+r'
        b'WPy9zVJQ66FZn/eWqRxfgP0qzDxNv8Ex6CQdNu8Ap3DZJ51f0RNx+JI03vUOlEEBH0w4DpXqysTWW9eGvPIatAfO842v8qGUFXi/Au2cDk4K+EI45/W5CC3Xvbx9YRIL'
        b'VhQ65fMiHCedupxXrYZwae8zlBtHTFYDZWVvrMPcF6sia0tbsCQgKehwuOz4eXE5hQ8uVOC6E2VueQaL1gy/Pgjw3HoavbGLRcQ/9lTs0KMhAr8Qso/rrEX2lyxzYzx/'
        b'LnTlZTLESmLK7IYYnvZ8wFByzEqGyf8+wjvzc34GhN/YS0pyru5v/WUkDOC3fJj4ftjFL736ZYN9hHUNXQU7S/dxpVmsfybT1Pt9UxFnNdiBTcpcluuaGNwt2C5zAIsy'
        b'N/lKe/8Zu0jzNWAGivmcDciBHHy0In1u7MdW/sI8KEvAQlU3AgTprbwUXoUvAFC2nqgvBKAdav8KQKXrkk76prwk/Hp0aLjEd2NDP6PKUr4kx6mzcp/RzB9HSmbERkrm'
        b'CvAyv0eUtMr8ZwJd51UfTXRaOIsLDOdjp64mXydGx+rCr4z7PwX3/DvSA3Jk3gDOO2PBFL6r6ZI0pgjzeChJY0oji1dkhosNFT/emLEu1o0pjTT4Rv6DVZRja00Nz+CP'
        b'i/b8EkxjsPS8uV/JN525fGEEc/auYa3RsqvMdUPGuh1nuOShFHNNc08RMY37AqG7AOvTsZorHtN5cFfAWdXF0uuqKTICmWZh2lt+nC39VSOWVHTjvMgpTGWTn5kgkDOk'
        b'8IWpH8ATc3M/EeSqC4RnBNhyEDrjXTZdF0qK2YAjh3y+NaYmctYQ/9z3nbu5O/cqdOiJZBR+LXNNq2q64NvGv/r94NuHop3Dzd78o/K9k8d32u1MO6HpVv/J75xrqw5M'
        b'HTF+1ybmSYPHxZJzRh1hb/wq266tz252/GN4pXe8b+6J55mt3/j51X3f+skv37K/dOjDbW9/uM3yauJ77w1UnNj/HbPcrP8u+sqfxGeH9+woSTRV4KyyKTiHRSss/Ah2'
        b'Myv07t0cndFNgHqOg3dz1ZRXUlbupEAfnxCCDyTMAq6Jpc/wb2e+UyYMyZ7hjMECGViCGWYN3oSDfPujGX0YMzez0odyaVKF4mER3IdebOX0qdMmhpw9OFcgNQmvsQdD'
        b'Ho7zmSyFOOG/JsM3CjuZHdwO8znhxDPKnrdicyZsLBCJLHAQml/APuU+q0n1TXlpLjBHSt0/PynVUJGW1tDiMgC0uNwDFaGOMFN3A0JGE623pHJEdLPoM0gE4jXPPqW6'
        b'W+nX5C9EdWt111LdFyyWDtJvJUf5TcXVgHk+VkJBxLKcE8OTYgNdI+WlCM22obWC0KxrApfaysyKSpyXnHnmRYXqhRqF4kJNqTNWK0ZLSqHlixSJQisQhZbnKLQCR6Hl'
        b'7yo8jYz6xV2ZDSi0c1QUi6xPis5YHxjFjGa8x5N30EYmp6ZGS1KSk6KYae/FWa1ENx3D09JSHcNWtaGwdQYz3qJnIbWjrZoWmQv+ucHCX+hyN4wMT2IUOTWZhamsBBan'
        b'hafS+RtGhCddeTFbWOenfUaq2tBL+0Jm8TIGww6CuZElKdGR3A4t+FPekF08zedISr8aEZ36mX3Oq4DFL+NpYkZGXHxk3Dq+xe0oKfzqxlbNZN7AunIOccmJUQTMa7jg'
        b'M7HyV8NTrzwTJrF6aRJDPrHEytBvxZLKvx6dFpccZegYk54USeBBz6wI0GEbDrSy+sjwxMRoZoiOSZYy1dXMcR4I0lnYPotxCN9wnLUw9MKTXA1HdDR8NuvkacT2yrwv'
        b'ityWjhVhG/H8KGtzV/7F+4wykAQS4Gd40M7Bch/3ezpRF0LCqOiVq1oZi0Cfh5KNTdAno2PC0xPTJCsosjrWhjduIjHkfmWxKM8tbp2YIoVMtpUUUhLop88gZK1KL+pS'
        b'QrdeejHx5fKlDeA+tkpsidwLkxVxluV9t2ty9qtIbMxQvn5NKBASU8xWEGAb5EGLqZDvJdKvjGXMXEY6MlRcx2Ghy61gThzCPFUspvdOc7KPMbSd3mtluReLrM08fEgS'
        b'Gg5Mwam0c3wAAdSZKdpfjEtnrqGQi9fXxTzw2oY04OEALlnJCSIvK0CXPYxx4lCZoworF7jXZo9frIvRQQEXsbDbgmv3XkFS1dOgBT4M08LU0lNWcNRcDluSnPjOJHow'
        b'Yo41cgLh9SxNAXSgtOqKkhErGSjQsNnzu4QdmpZ8NW3rED6l2+b63OWveWXyH6oekNbS3PP6Sett9gIuEGL/OejVk8Ee4jvKAmV3Da7oFve46QVFAT1hYxNz1XTMY4uA'
        b'C5e/exbzuIIAAe6codiDVl1mziTH1R3QF+4Wnt5WHpZmcqyfXqm6qco1uqgnnGnnCIxi23OmnTJTkoJgKJCXPQ2wjnU7JH1tXhF6sBEXXU0VuGT6azdwTOpPFohlsIbz'
        b'J0P9SS6qxBYKYIZPphddxjosE1pjIXbx/TQqocFRmk0vkMEpmGfp9JZwj89Yzw3WWp9Nb7JdvEkOlvkeAY9oJUXShHaBzAEjls6+OZ2viV+FyzfNV5LZWV+D1YT2iXgO'
        b'MEOwwMo8FIqe5rRDk4xbugm3KByGPPONkk73hOAcy2jHElg0VeYW6YQjOMsXY6AdjGI3V42hGB/wFRBycRrazSEfc9bVZLilDEvc63dvYaM0Ujfd42k9hlgXbpWhmO3B'
        b'1WMQ4gPSlOcENH2ZIYc8GdiAxStBHrTffuE+QyXuYGz28ZEx0pIMMTAuwmbXc3z1gAFo51rtrRRk0IPslZoMMOzFLenOdjpWaU0GGMAWaXTwNjfurrE7xt8rRLSuMMMt'
        b'd+jhXjW4jMurQTm2QSvZ/YqG3LfHccDdC7t3ra3ZQLvqT+bLgtbfxlYWSnTC/QyJzOJo4WHMxVquOkGKHZQEkCZUddafvpKzxJkjQugg4byAKwWaHiDFq3MX7Uoi9aX1'
        b'DvLTCEpLsdZPRiBSwWlsZdEvj2HWVImrZIbVidAAT2BQopaajpMqOKkOJTiXRjeQIPbYbMPVhcryUV3/tYQUL1nBFl877Bezun6Yy7dCvn8WS+jJWN/VZzPSrimmqqrJ'
        b'CfYSSuS6K/JF3UZhCiagOwmn03FGco1QsFw9NV0s0DYQH4IiGOX6QOM97BNIrqUrcQOp46wiTgbR7DPp7PmVRRy/LCertZNrMXLMEXLOH119Y+UJ7Wix8zWolba6hkX5'
        b'1SdWF7f9wAUYl9kDs/u5gSQnofggLK4ZKS0VZ2h5p8SO0nODoYNe/PfQD0VsLKLFcgINORGO0+aqOLgP9YM6ZXyYRitRUYQynFMlIV71rgimT4bxmN+hj7l0pf7+7EZl'
        b'cR4bk4VQfVKfn6OXWYgCfLA6AMuxPkA+E8pZKdIWIT7EKbzH49awE/SsTnIAC1fnSDHgQPU6a4YkwYfqqazqeHcg4YgZ1sBAOjPoXyQ0JzWRKKWXtY+331nGTM5IVW0L'
        b'RjPLPLxjYRlLiHJA7llFCVZ68FyrHdrOebGq7EJc8ndk7b3G5XnkqsMFGMZpdyIdXpZYrHHe21dGoAltYmjIgjKOfP/95BYBTa9gk/T9pEd+QdJmEvvNBYHsw2uv+v3S'
        b'N1jA99QQ/OW49Ie9TqYyHLfJgMd06K3YDyP0203BzbPH+T5OA7SewAwYIUaSKci8CuPcx4EOtKE+WOQD924YENXlWkqdIcrZC33I2lPFC+LP4XJ8+g+viiVXiN08UPj9'
        b'1TOHk3ScNcZ+1/z2Xz+qyFrc/tZfKv9qotslrhDIKe52sAiJOzd1LtLE/WhxkPuHX4pR/3lYi4uG4Xe+dFqhSOHm23Z7djW1BP3pclBQUP32hsBtCSFKb3TW6cY/eDNs'
        b'39tRX/9p+ZL90h/fmPuD5rdfqRd8bH15548kl7+zv3g4YNv7t/c8Ot71ns7Fnz/SuRj89++dUP/m9kK7v0afr+3uTx5U/H1+QUJXpLG9WdViQ6Zz4X9v/2rkG3vOvKaw'
        b'9fCUSaRvmYaucdvBIS3XtLsx7lXfaRH+/tWq8icm/YfSvE1eaf5h6rfyvjslyGh/L/C/0xy1tZOthoVm2xdKPilS/+btPVf8YqN/arH3uwp7L5+ofn/m/eyfWXSn7njT'
        b'4CeTH7caL8X8+NWL3j/b99ucP1dF9xnkOM/Mei/9vDsyNn965Du63xl3WPzdBwXT6jf+YHVy+atJZloJimP3zpww6aoZK2j8Xc3C6zGjn3wYEvjn0sYLo3+LTT0ZpvXO'
        b'J++mf8n8w7fNfn7auWHu3aLOal/NEzmfBP6lUn3bz56MfvS3HfrePz63r/H7r1/KH6lQLH/0wODi1yO/c+NPVuO7/+h9bu5ip3nrktzZ36W6LVX8ZH+P44+266i+JQm9'
        b'2eObJvPPgYoWS5fXqyus5s6eedXI6Y+H/vNjJ7cPL37nvz8sf1cSNfDp8QPJlzOe/EfFD4c8P9z+Zta8xO+Ngi1Jsik/+WC4bu5Gq92vXm8u+ebRxI/V/vHJkt2en/7m'
        b'6E+Xfxv+/i//s+sb9qY/efjlw6/GF26fnX536avDsdVvDZpc73kvB/1+KHjrN5c+/YvM8s2Yo4uz78gfu3Ts/iuSB3+zcvfP+Pjy3z8sOfbq/JHJ5tA3En/+/TmdO58q'
        b'TzZ+euXUVVMr3gddfX6t11QNmzgPtJaHGDqhCap5l0o/PD61IkXYEiZbYzFffuQsDmV6rbjF/QzE3DOaWCgmsjOvzM8wr4r9fNAjjhFurLX5kNDRwVtlirFZfU3Yoxz2'
        b'igivRrGPm2YPtMU8jdSzNuPsSnykHlRp82tcOBkktRvFYC0zG0H3Vs6kk+W239zKFKaIzHFlY1kQoTW2p/GEWc9gJYYwB2qeMRq54CI3gqlaMFdpzhU6nxabE6Vy82pA'
        b'H5Sa+/pguZxA5sru/UIY8o/lc3LaDcTMlmRvLLUmiSyIB85yUYDyoViwxgiVkME1XpjDR1zUYhj267IauJiPk3wd3DDRblNo5ANMq/Rw3sscxreQyOdFDPmmyGhHHG8g'
        b'63HAMS/M0V9fFlh0V5TCF9ddUPJaMduRTDPJ7HZ0Tg3cFYSkib1wiXi0NAiUDwBFksP5aResgMkupdbyjJ4rqgvPYtlh7gh0MSeDdzrI4IiQS1oausTd28lbW7HUgqRA'
        b'eg1LBNDlY0Ec3lqM9cSserlpk2EYWr2ehlgqn1fDWeJmV2X5bhJdp0mgkkpa5pgt3Cfvz8dR1sLDQ6tyLzy+w8u9xX58Pd9GVWh8KtvW72KibdBZPgGrCYqCnikU1btV'
        b'vCnqFv/qgucayfYELDDR1iSCO+DDTseeCrZ9NityLbRhD7farZ5O5iYn1oq1skmcZ9EKHx7aWKg9ms5k2tvRXESqFQkf3azUE+eAhJZL9IQ6ZouTScas5q7wgjwHOMXW'
        b'9E+VHyu2eFdkBiPCNKY8YQtpEtmr0g2x2Ick4VzDWVWcENpCrtACu2UV/XW4YzhG0PXASyucuxp2LwrYIiKh47EX52oV771JIsW8tPwiFFvzveu3uspAezphD1vMqdAU'
        b'r+MEtRV+HgcIXwTy2CVSgOw7fM95Eplg+nrKCl88AnXcwImsTrW0tAxhXbkWV8ZWe7eYpNolmOXRciYAqzHnGv+YlQ+WkJROk2OTDJ31MtznoCs8EIe4J/wIKxcsiOnT'
        b'3YgEegdkjsN0RBorj0WnVA33NyguKjDGUVdWW9QTH3ODhdGwpVw1yhL+ZpTpkhqgRIRdRjDAR18v3LzM2bbp9uhBOntfkcFt6OJAQwGrbJ+GSO/ylgZJn4bxzXyNmwEi'
        b'FNU4rX5dSgAVCbUa4kQwBrXYwIF0AuQTgSkNULS2NN3LAChWRFSrCupM1f/9JLGnFt7/xc7Xa/3e4VFR6/ze7zFh6vMZvQ+qcL2n5bguJSv1qflIYlaFWl+oJVJbjTVW'
        b'EIm4GtQiaYwx/fRMdxUlsYxw7R81sQI3EptFScjbqRW4WtYynHldiSvNwypda3BrUBOqibS47isrnVa2cIV61Lg4ZzWu/rUG56XfwO+55jikpnlF3r6+avhONWA291WT'
        b'd+q29eb6f6/auDw/z9OBuRm5ycxW5+ZM/TvppxJlaeHIz2Xqzxb8xeplLtY1R2AqflNhxcP5NMUyUoYXuQVygjUGL3+BgE+n4i38ilILv5Cz8TMLv6hQs1CrUFyoHaMt'
        b'te/LFMnlCe7IZsox32uA4LYsZ9+XuSu7xgMbINrAvn82RRpLvd68zxm6w6WG2lXX7IuN5itPrM+4SpPanNcMYSE1PUeGJ21oj4xgrgVDrrkQsx2+2JHwRWzszGux4axm'
        b'K8szM+Syqjhz6Mo6eOM2vyTmqaClJ/EG5Y3t24YuyVHRdg6GEeGpnEGW33BqdEpqtCSaG/vzuZy5A5S6I56tsLSRH4GG3zjaWGqlXrHRM7P4vzLjfh6j7cb9gnb4ph/i'
        b'ZJAAnCZuYwDZK73HT/u/2OtcYapIvBpz0lkQhjY8uMoEvFXjIjMaYpFfwDo7aSYO3MZ8RSjfjH2c4ukMS/rmnnuhQMR7q3FCmS916aAk0NG/zXoxJqqev8N3fQn7zc4A'
        b'1ZRrWv/gu76I76afok/NnKDeHAaZb7UIKwOYhdPHm+OoQVxAbhb2rI3HXVXlOT1efJb0AKgVcYtxhFISaVjD6u1Y7SPw8cX7fGUAsdbfBBoigb6NV2r0G1bXfXgl/I1m'
        b'p0DeXqt2QfATgcBGY1dDgv2O3B38167dTty3T2SuCH8gt411UTx8MOSqgO+b3Iz3fVmbcyEO2ApsjT3SXdjtYBtJ32vM1Vhk6emDtcxUS4JhGs56nJbugqsCe9rd08KT'
        b'L7RHAk+lqudJH852i72sP+nzcXk4gw9eED7gBYMr9fx7sfb82nL+pCDNcCX9xZh7HRZ4m989/20rhQigd4fUhJlsz9nqU27C7POWY8zDcan1eO+q5RNy4IninWj+mN+w'
        b'Ewlk9g+K6aZV7HZFSY0eTgn8OR7acU4wQ6fYadSQ+caeLO/VNqOcJdxUVto9XiaKs4SYet4U3ITxWL4Ne/GRLE7igxE9Evow5yZvIxmDolBmCcE2xRuCG7hwkPvY1y6G'
        b's4MowVS8IB4eYgG35VRjOsBSJgJjqdZu0qsOCuEBNkfxpWcf259nZs4o7FxXxdQEn3CmTCdfGOYl/9M2snyJWBKla+Nbfu4kkrQTxL3xxP5o1VGJzj6VAuO3PvnF2598'
        b'HK2deq/F7ICLs8cpeR3/qMH9NpJDtRHWfT+ZKB9XuOjs/Nu/m3+qcFfpwMepP3lU/adjNZc93rQ00jn0y3/87ctVrkE2Pw+qm8iy2vNjTbVf3LWclQlR788ytVMUb4e6'
        b'yZabu3fOe/8265cZ4//sbf/WD/o03TzvfLTLpjc3TW3TYe0/iDWW8jN+r6lf+Shr56N//sH/jMPZ8OGpnrg3eluGs773o581x/X0OOomfv39tp+dmewp+FA17b3zB3ZY'
        b'zg4fbhn6h1u6l+S6yduveTeP6rl9sPXD8dkPjrUecV7626N6h5H/Oiz5/eSvzwxd6Dt/vu1ti+9+cOXt1AN//VN8v97vzxQ1fkVXTtu8+XffeO/S1y9/3fAfaT+uMU+I'
        b'/3tc2n3HzPHfRogdfztw5u1mpfhjJ3502Ufvvayvm1m+Eu+WZ+g1/mj7/oV/7rFxOvkfM72Hdn/zU9dSp6DJXxRckv/rwcnfNHR88JPv/dHp9b9+9dymxyVnHl2a/Hr6'
        b'N+ZmugYqjd97ReeNSvtTV/6649Lg/VbVV6dV22y3vT7wru1Hw9/59NbvQ/8hElxuNLnyiqkup21mkaZcx9dxjhHwaY4wdJKTkmPCM1cSFbEdO6V66lUo5TQoXNJ1XVsP'
        b'FfpSpbYGe5zhho7VSuHraEw5SEtp7IrBLj725D62GXFB5aVQIq2/IXeJ1wpH9XYw8wI04COhNEmxFu5xBVZh5DbcWw0bPY0Nz9RXJQCc5hRlmbP4hO8qecadtH7WVTJY'
        b'ny9I0nECJ6V9JaVNJUmVKxCLcN6d27UiDGIf3z1yE7RL2/RgNozwdev7SJkYWumqA7NQxTrriKA2FTt5nXcGH2OTOS2Kdnf9MH27TQRVxARyuYWF7HJjtfuhxnGlfL8T'
        b'fcPOM0aLaf2rKryPhaGfVIPHtvPc3CKoPs+0aRj0hT5vacyP+kHxRVjS4AxAlzyh0dwXy7L4AEUio8QxzOUEW6GVdEnVNN40URzL9SUnhqIEQ36yAjkDER1/DrcIc0Vc'
        b'eKoxFnscgcYVjbEug1MYr5Om20yTNEHtRhrjzH4+4bPacievMEqVxc04x+uLuCDmrjI1Bgc20hZh9AjXiYI01AJ+va1YuZOOhGlqWGkrVdaMHf5NMV37f1E3e0ZBU1kb'
        b'UsBpaMOMyn8+DS1LYKXC6UtK0k6TClLdSJ/rD0SfiOkbEftJg9O5Vv5lXYVYRyFW9lSJ065W9DgNTptS4foNsUwmNWnPShmux5ASF/zE/s7c+mw+wZr9SFUsOV652bWq'
        b'8DAtY41OpfE/fb6mMmsmM1udkVOs9jKFQ2WlC8TnU6xItbJZq1q9bO8rIVxKbCHKomfUKiaWciLpCQEXcC1LihTfF0DEqVZiplzFqKwqUjIvVaRYoJTzRqGsK4rU0+YA'
        b'q5GpXEDr/3AYNv/OSh0e/r0NqmVaGbrwMTDcUl4Q28NFbTNtix71CPCzP2izj2k3V8PTWASHJI1la75wCXwBoKfxLM/WM+S//9xJIAq+nOh/E7qy1op7MKz50khV9z2u'
        b'nAtXfzN2cl5lbITepzWnUqGXFzGfWLvw9ayibVbdytC3j/NKHglkLnbOZ41tHIVfbSQANYL4R5a6IkkOPWd1T9eyZFKVdaH5KLRNw+W7gqJ9Gl5fEuhY+e/aGbV3u167'
        b'3KGv6v65X9/0h29//9Z7+7/m97WLnd++F6H4w8tfPZQX/8but7766zNvfeWVL90seyc7quvwL65p/Mrn8eClmKUEnek7pg3j4+UaNp/85Qf3L0Waj0f86c6vriZYf/98'
        b'Rs7yPwVJxrvf/sX3TGV5K919EjaHVhNMsDqEhAdnHOCsdEe57sx8hklF3NPwVCOo4b630JBblR5UPdY4Ktqu8la8PKgIX8cPGTeEEktiiB4C3hHx6GTgUzt5vLnw7BEY'
        b'XZc38m+xiDUUXC2dQ7J1NNz3i9DwLMGWlRwTvlvwCh1n1Dpz2zO0Zv2s6yntesKzhtJ+vkLdREa595XW01KOjJrRZze/MBkt3rWWjL58a6xSbWZ8CjO4/I+UtVzJWhl6'
        b'Pqw0NTIu/rq0ApK0sO66mksb0EkX3n6ReJMzeMRfTUmMZiab6KidL6Sp0s08WweIPv5XTVcEG1IlGV++i0oF5OIC34ty4+gl5k5yxcUIPYV4nNke/x3FX4u5wzu+o4ml'
        b'cQd/6Y0vz1RNunffM5X9mlZk3O3umMQIi/CkmLgIb5aVmygUDMwrlEf80VSGE8blYeCaFMHF0MMXQXkEc7ykWwljNxmtI/F2jR8rC3I5YdQO78GE8rPZYzAGjTIKMIId'
        b'aSwPCeo3YwOjE9Y4iWWsoSRvovHwuWYJeWr8a14wIg8TUJ/2L9u0aYTz17sCVxIOU+2/GKY6MDxdrSe6alp9Zob1qTXm63Fxg4Ki5qvmX1IABM0MvZy+CHplC367Lufz'
        b'X62T1ZyQ9fUNdPU1Ffny/2v8i4J8T4uChLO/9Dhiw35iMeqc9ZqTtDg6we2GP4rN/9uS9Wek2qnq9KOasjTjTUFZRmRouLbanoaGishAQ1dZSai7hRFjgXDPHS2hVZKW'
        b'0HAHZzQyORrJJT9nxnGa6krus0iw10T2+kWYSP+jiMVf4ZQBtEPN0WRstdEg1WoOFzcdOgjZkfhAzhGLoBpqFEgfa8fcHaqEKvnQCaNQe/IkdCtDDZQIt+ITFqCoCs2O'
        b'OAMVMBUOszgUqMoCjfLwwdEj8AQm3OGJGz1ViSU3YQ6GYNTqNvR4w/iR26RuDsjjBAzTn4UDrEAg9sdeszXG5n2YjV1J0IH3SGedwtbbR6EU+rEYJvXcrh3x04XS3Zjt'
        b'cifBDsvxMczFH8GCK25bdoRvcXX0kg2xvWXlBz0hBpZQi7NHYB4HYBqqkmCY1XyAh+7w0OGqGSlkoVimiv1ROKFNck0n1GA3/VnEhjAXbPG3S4DySByTgw5mckqGSazG'
        b'jgASGyYyrmIvPLkDi9gYCNWbsfvKBWyA3kObcNwdFm2gjPZeDRWaJ+FBAOSZeNECHmKLPTy4gyOnoVmI/dCCuVgHbfRvZRwp7S3QnbFdrAx1MIP3bVlJpIdx9kpHcBYK'
        b'Iw0g2+0q3IuiYRt9YMk00jV5hytWxOMTbPXE+hB9GLvhTJRtiq5p4qgcNJ02Pcta0UI95CvtCcRpfezCbvptzodoWFswHUY9NFrgnP0x46NGOto4dY4+aLtlcsEcm3FY'
        b'QxsLsQpmAyX0abWa0i5cpjeGcRIe0HImBNhoF30Ymy9Cqy0saeF9tQgfqIhNO4bZZ7BxO5SGHlTAZXhkoA2PEmF5KxTE0uujKSQXNu0zwO6oXefOH7XGWoKDR9AvCSeQ'
        b'a6DtNwsDVTZfzEw6fAtnDC5tgxZf6N58AR/QETXioALtZ4ZAqgW7nbBMAQpP4YIN3WQDjDjQRkdpiXOQF0yXUGl5nHVCvgFTeluxhI5oETvV7opxCYvdjAjU+9NLCPBN'
        b'PeKh/YwzVBDYq8ASTm+67UT3O3AKsrdDGzZZquzHcbqhSegQn4L+yPDdplAVJwOlhlnW0GefnhmnjvUEjN04SGdblhIWBI83BUOLE7AugL2QF45tZthovgcf4QLMiWFC'
        b'Eeu24sNw2RRsh5mzIRnHsfVOQCLxklY6isd7aRMEITiW5HWYhugwgFbM8Q+msWuCofEQNEFhBKFejsjBB2tgwpKemcJBGL5z4Y62RnBWxH63WGzTvLlfE8dop6UEynmE'
        b'FbkHCK2K3XZ4G93cQ8BWCc04uo+AfISA8xEWhWNNIizRnk7hIhTLY98xrLkF99O9nONxzAQL95KusHz7kFUWFFxWDIBH+ttZjTgc0LSXScblMJwSYdUN3fBTxCunlaDs'
        b'rjs0YY6BG1SEQDbmR6nDfRj0CzhrG6m1ZzMOObsp6WhZ2chutTtLKNTujUUBdLtNOKzPYiohOxz7D9I1LpKQkC/GGl+oxklDbPPFkmAchmkZTQK+Ej3opm0wspQfastO'
        b'FopwFGYybmyG8u003xjB1OANgoXCTE0FQofpGKzD+du2OlBLZ3iPFTIjsjWrEKvmifc3kzzQef4cjhDW5ePcjkvw2McLlmFAkeR8CRGEfihwiMbpq1gcDI+ttjCz3UU/'
        b'mNtK8DaC5WegxstT82IG6T1zRJkGseMC5BACLbM4YFsc0TYJMNrkByxeaDYE+xLp6Ab9YOr4PlN8JAtNEUbQpY3V6T8UcXl9zRYEkEzvIICkhc+bw0y6A7ZdlKGBO/Fe'
        b'Ujh0XlMmxGw84G8B/RphXjB0DMrwIR3XEjZuJUB6AiW0tyl44AEFFwhf83fhY/djx45ikyf0RGkoEbEvhj4CqTm4txtaDK8TBDeKjsHSTcFBKw+svZJmTvc2Df0ki5XA'
        b'AiFODWFca8SFS0lEPbotsDWBzntRQJBUQqA6DD3QgHUXTxFVXDbXC0q7dBk6fWiFvViFM3sJNaqP77K9gWU6ijC/FmAJPRr8N9M6ZjMwz1IxC2aSOIJZp3YTmolS9jt7'
        b'H8zcGQkTvrdu64ovu0GpHuTE0MaWaYB+okx5B48R+DbJX4VyGAiFWlW64yFDVai1x2Z36EyjR3JYfAvcxw5iSQOQrS7CvKNEQPo2ycOcPS7o7yFomIIFW3yik4E9SZtu'
        b'ysQlYjbUE7oWYJ06HVQvba8fl2Dan1lmNbEkZBtrsJqHk07QS0e+dNGEGNN4yA0DAt6uq0exKozYV6MpDGUQPpRZ0VV0O9sSkSsmsCS2eXH/lQNYvTcBB++cUMukBeZB'
        b'NoFyN0zvM9wbFQ7TRG3mVHSwFhcwTwWLXKHDNpDgAbpu0gKKsXIvzEIXjEBlJnbLbzWiQ17EXtcQa3iCbUquZrThAiKPncSzW0/CtFvsGbrIaciVhNB1NhM3vA+LmVh6'
        b'HZouyUdjw9EYNyuOn1d6pRGzKUgnklBFzzQccdMLJvW/9QqUiK7rE/W9j5UE4nSKBOLQcT6BVrpMWr1xsqcrFiepYnV0kPy2yzi2BRoZdFkTSne7ah6B7vQfiVg0bCkR'
        b'LCK1SZyAsYQPzPGh8NT2MOiUx+YzSkKYZBG9FYQ3TVCVBlMCIrdGmzB7H51xk8EtHJeHBeiNdtsLLS4wok3MoGUzPV6hhm3yVw0SCG5a1Akfm2xN8clZK3doPX0L6wyg'
        b'zHP7IeIDc0p0PE+wVN4fhsIYuoQLUy4yYag9CR/g4qUgohiMAI8SKSAJJPkgtGo7mZ/RwgchUB12EnJPwYIGdrplXaCz6Tx0SxvKArxDYMgYZ7K2uYQR6RimKxm5Socy'
        b'Aq0XbgqxwdUO5gNtbqm5YA60QtMxupbOSOLOuXTX3fqadOgF2CuGZU2sOaunsYXYX4kOVF3yDg8k/H1sd9oxkTC5NhhqrSDPW8daBwcTYdSJMLAoAer2YK6LELNl/WEh'
        b'6gTUu8bD9DFfWISiEw4up+5uwWZCASKOfTRfoeAqsYFunJSDTsKFYl3CmSk6rkpss4XHULaZULXNGBbv4MNrxwh0m4jZVWDDkWvY7UxkJTvq9A0ocEsmNOi8Aw13NhFw'
        b'zUbdxKFYfWwiSthFtKLkMJYHaR5Egvoq7HUj4Yjgus/wEK2hnX7qcTp0w02DGOPJLTAdQMA4BzM39xPiP8ZhFyyjo8sntnf/0HYmlKVCWYyhCQNIrNY5zhGEblpmNnTE'
        b'Q0OEZuZ1H2yjWWYIuRqhJp5WM0QyQZ4IKtLp8Ms236LttRIPHSHWKQmGLivswF59P9UA4hYDCbrYFY31HnTH/bh4EdrDaInjx2CcULnIAe4hw/XH2HCWhii8HHed8SHM'
        b'uboZp1OIxkxhvpHreSWc2LrP9fQ2GIS69GoC7T0RJBi2n2FpSCtShDk+El7FCpIijtqbw5wNTFxXNnGQTyUhtsn1HNacoK1ApzNd8GOaeTqVDukho0PBu6DADvP2hUM7'
        b'TV0CEym3jqps94LH+CAC79Mz40RCGrN2QLb5ObrtRzL2RAwbYN7s4HEcuURiWj3OR5OIWUGcbJiY9CwSacvLssQ6LYLbohOXoNMTG844EXetinaC5rNmJHb0wqIjzVZB'
        b'AkknLKkTdrdDlwYOuUPFvhtYo+azI/Yq0bscecKQjltKoTBh7HjSW/+oKgHYKNSrWW6ToTNrV9JywJkdexTErpi7k44x25gAv09zKzH5Chpz7CLmXYI6ZyDqdIxYIREo'
        b'EhJwIRTbsOPwNcKOepbAQqvpwAm6JaG/5TkoNU4iVt0Ko36Ydx67LzpCibeFDx1bHhS7JGz1czvNxJgSWIq9dBf6I0wxNxKytW8ZYiPxrOoL+DCVgKfhNI6EYZGlDTSK'
        b'CNLue2OhM8HXMhH3sdhLpJewKqnFm/XplGfCsPYwFsL9ZHsaddAWCo4R2PRi9b4QnZiDDn4R0BuGj5IvEnXuPKyuZGx3SGeznSmR9hkVLNY+6WtCHHHZGNrO0qg1qgRb'
        b'T65CyZlzhCQLF6FzD/TrROFkEk3YSjttv0yo0HchehNRoBoYs4IHynSeJdgYC8U7YOpSymW94zCcSA+NQXMM0YdmcQKtKjuAIH7GDiqPwmMT4rnzeC9LB58IElkDggaS'
        b'VmvSX2cqXT0U2TKwzEnioPIxQeUNHInGwZsKJPzkad+iQ8zZs425uwxstLBWg8TJoDOZ7lCVtcP4VjoUhOv7h6qcITbew/5A3gGi/g1ESOi1o0x4uq2hCqM36HIX8P65'
        b'48rEMh/CsnoY9mFzAnGLAVnMTsf6wGh4fCuJvmqNuETyzDgnQgCJEIvwOJ7AfzpCH/NTd2DfXoKMbkKekcAkrL5tSOShjYm8cdirpIhFlx2v6ivTO9VEPBpYp0OfEBL4'
        b'hu8E3AmKu7FLxRdJbu3Bvl1EvwcuHruhRudbCgx7q+BRUsoxLXionkaYkpNKgkVVsK+dohFORPhiLjQE0CMP4Z48DqtGY9Fp1q+VPi5MgRZ10lfuQccNnAolcJ2wVjH3'
        b'JArVHK/hmnDzGGlQ3dsITR8QvSnduleGTrPehqTOKj0dqEsy3HGK8HV0G867EekqJw1lhhjzQhJXZLDmmjH27yYVdxjv3YGWvZZEAR/J02R52G/nFm13Y+fFGML0HMKI'
        b'vHRChhYlqNmHFVfssNXbmPBhWltTEkEUcAmHz+PwJUKd3p0Eg22HSHKZs4NCfJSSBD1ppIcXkb6sZ6NDFLPxOJH56cO7adlVcVBOooMsDp4lhllEoFp77ArOnt2M+TJQ'
        b'hw+iaV6WeNYi2J1xNOW8RNefbnhylxnhSztUR6VB27EbULIbi2UvYmkCNB9hIS0wQ5JnIxafIz5RykJ2dbzV4L7nniw/AtFRHM8MSSR5sTHg2KlDTDsbcYA+51SzizBH'
        b'QFXpA5O34nViiAg1qxOEz1hiz+nbbljrakYwMa63C3OsvRPOstCUIlM5vkB0F8zDmJeHLNRvEwitBViim8WFiNgrHmT5Pp74UCBk+T7+7tzz2sTuZrzMRTCeJhA6sSCf'
        b'zu38QA/wyVYvSzljiUB4nH0+SjIQc+47pCkys7yQ1KdFgdBTQBxhEIr5zJ5TdJelFsLj2MfFRnVIvNNdxQKBgYo2nVAtlhNOtDip0IE/uKu044IiNBw+ox6uTUyp2org'
        b'oJuOiIVa51rA7B685+HqAwUJx3RNidLMYd/mTGJOXdDhoeF8geh3FbRFYCVJLIS/eP8gM7qQ+l19wyrdBYZ1mah3B/qiw7FQGbpSwwlpamH5GGQHncZ6X7pH+p5QMf8U'
        b'/dgLAwKisIVntUiGa7Wm62q3PW9EUJezjSUOmIXQuJUCP5ozP5qI6gNiwLV0z6TmxN+GAitirtWBULWHlIUpgobzLFR6D1G4MahxIF0pPy3UB554Eaj3EpsoJaCaMiC9'
        b'KY90syIH09tQaEfi2wLRiAmugtfETpKIB6HZPtr+uhgr5aPVscn9CgwdxEep5jtw/jKOnPfYBEPyt9OjfVJD6bqroVeRmQ6gyWAz5tDZjhApyiHi2H/xPI1VRkfaEKKT'
        b'QAg7T0uoOkBb7T+6RSlIBTsiwzjlq0WMebakyWTTqYwhkdFlWygT40SImZ8t5gcTSes6jBN7CGkG7MyBZVsMQdVhkoYqaT/ZqXrpMsSaqiS0h154fPICiZO1UGIGHfI4'
        b'Go9V7lB/HDvPsqRP0l4ey2/C0rCdkaYuW3FUAerDoD6VkOSxqVo6DkWmpmI//am5o0rLLT54LpjUyDEixNV2OOXidlszJgpm96rCQzW8705IlXsIx6w9CK+HoACZcadY'
        b'nTT4GcjZAm2hRAOg4bj7ed8LqUHn9UgcKiI+Pq9nj3Wp1nZEJKaui4k29MGopS4sp8fhyCHSB6rMtLFFjxFxYnaFNlkE9bMHSFYsZuYoU98YYqYwZw2taQRQhTB3AQqT'
        b'iIX3wvBJwt0xrywYCyWdr4OudMzTkTO/LImJw9y/EEv6VB9UHtLbetecpM4ZX6ZKYHUMLGK3Df21jI8NdaEhWmKRpk/i1sgxfHRZFXNUcUkIHZezLthgXXo/Kx5ykOZ9'
        b'xjBDSDd+zNBJ/TqO6sptycCuKEKMnAgiyZP+F7DEU0fXmVSXZWhMpaMsUNaRPR/qfYaITpXdFgKbBniwGfv36XvtPALTt0gbKAzW97OMdJYnfvbo9DnOQjPlt4MmaYHa'
        b'g3QgS0q0gakkokfdxEwex+HDdHhoShp66RFzQot+bEuiXyqv74cW4mdE2KsYmPbApBmM2ySTmN/hiFNRF+iQC3zO6TE5E4lC9wUJSdhbIoTOMSDcmXQj/tohY4AD5kRz'
        b'p7FH+xwM7mI5EtDqlOpNEnZHLMmdeU6Mrk5Czp1EEu23OpGU0LNZnZm1vHEgU8tFCYY1HK9eIiJcxtsBJJEE/1VXjGlhxMuw6y7RgXkDQoN2UnNhwOeyIAELTyQSwWm7'
        b'fCKWmMI0tkXTGmvSiAfn0Rushmp7ZBQ8SPQ/hDN6GvBk93m6kiYd7HO2YmdihkN60TgfT1DDZPxh0huWUvHxZdkjGti8dR/W+KWwFvba2K1F+lftLZKismH5Gkk6M8dh'
        b'SNNv73E7I+K7nVgfooBdbsl07K17TdK3m8br+rtpaWKndla6oyoUnBD5EsQPE/gVQ/9dIgNd6efcofQC0dlcc3ikE01IuURY8fBO0FVik0lQIcZJ+n2URLz58OtEbduO'
        b'3g7GvhBLokktOGIKiycuw9gOYw8iCbXsiukanhBVaybSMKZJ23iMy3f9vWnQ3gNQc3WTmx/NvbCVzmPRBR45E/0tDJXddTzNCyo5m40moR+0B2DpqmYbRJOXQ+P+HUy5'
        b'DTmjLIRZLSzyhQdyljB2QU4XhpDo38wBAoMHDueIwZRYxTsQgFZzJpPhXZZEwpiNrlnTAvKJorG+zzBBegE+yfCzNKXbGsGlY84wZADN6gZb6OzLYCaKULXn+BEBDG3e'
        b'Qm/fg2FjaHbA7J1E66ZgNBjvn4VW2xAiO4Ue0BYVQhzhwTkmnHRjV0iqiaw47gg2WGPfDSy2gqndgZiXZAO9CSeIK/TSngdIaG1zJYID895YYhFCfKPVjND5nuXOoDjs'
        b'O7TpfCo+8SVwayDOkb9fRwHuJyTBBFGvDpphwlee8GA5xY/U9mqCmDLozaR9E6/agv3WUJ9O3KTRN4HgidSWRgvVJMhXMnTEMYd4bPLUvQpLMJSOrQ6w4JyKjXR8lThx'
        b'bjssBwrs8Z6qAi6LaZUFPptgXpZZR3ocoD9W1x0aTm3d4kAqVwltCccOExVfIqDgkvMJEh5fI9VzVJvOvTkikmFOTNxeIqrloovOsddUYPYC9if4+cbHXCYhdUqNltBC'
        b'3HZECae8oDQSGs+Z6wGpF7lYnqASjqOBUKntFHbpFnZ4+mzbh9U2OLkt7iJW2ImYyEpUKJ9U6Pu45H3jNu2+NEKDOFcXPtkuYwwN2mewIDLY7fIJH1fC8bKjWC+xj8L5'
        b'XUSRxulWS0kvlAsl8jCqHGLAkRhGtevoIJsi98Mkzu4yJcxtwp6bhHAVMLGXdJ9STXlijsMpwZto0tIofOx/je6mHEk2qFKEh1qHrYimddzUzlI3IexqJoLzxAKLQqHj'
        b'0FUSU4q900+SPHOChJWqdaBNiu1DsUgPB7HaST0VenXkEkyI5rbTZiaJIjbsE3oGejDNKRIfReK0KiHWLO29y+KwGlYZnN8mQzDeQry7jGT30Uw67fr9gYpnYfwgtgQT'
        b'eLcQ4V5QZto4jBicpeNmlT0qdDE/wJWJPdo02FjoDuizxbFTZkiyjOc2OqHSXXDfagfhZ/0RaN1ER9MqIZ4zEA2TwQYE5S2iM/u3Qs9mB8iOgGJrEnuPEjXccdZ0K9GJ'
        b'mjjMU4TJ6NQsYlt5MBNykHjKdDQj4qXyaf52MKRyiI64Epv1Q+mQ5rWwO3YTjivszXQ+ck0P2g/BA+/bBFR9xPd6sXkzPkzzxCEtknIqiYUuxhEvyFRySaU77KBBanbZ'
        b'p0HvYZl9OHbcCAaPKWFbGo5qxFzSh35NjWtQuwnLvGJpoByos5C39aH7JCGDjuWRjKFPitOhMwk4vouQe4hQqC1sFy67Mk80tHs4H2U1A0oIKUnyJspVAw+VY7DwAIub'
        b'z8VSF5jYoigkQjAXepGoXh9dySMaNV9zUxCx8HLoUYB7cVDggEOWRP6L7l6HGvuLyKzk3QKYvnx4K5GTBSiINyE0G9CHLkvC8WbCiAlSp9vCFDcfwEU9aAy090pxI/45'
        b'CIM4JkOv5MK0oY4DKRs90O8Mw7IGhEltsGy8aTOJseVmWHUbq9jRFGfAlDhlz2H6tPoIdJsE4TwxSmzQNDpihB320BQdTHBThA2pxJYe37iAD/YfOQt5iWlEGOusBAeh'
        b'P/yGTkQEnXpiHC5CeQRMXCPArSbRrZxOa9KR6Gq+kQMpg/NYmOroFXOUiEARltyypMOdUhES5A2rMKGYLrI5SnLjDjzyo197oMWb1IP7tOkO4xR3HA/i+OIMLh65cAwa'
        b'9xLPJM3X7SjOeJL09kA5ah+JcU0hhBzL8hEkq2XvcoHH6TKESHRLQ8ysEkAXS4ydUOkxLpoTKW4i+HzogDP6JOkGY61SvAuMGGGrizVUi4nBdaqyJ45qxJOuuHQr1t2d'
        b'5IE8z7MOhliQmcyyrHHAmcaegvuKuHRQPpH4zogQuwJwwfgOZJPWV7/HVV05ABuiOOfaGDP0Z92COlhg5qwemD9D2yRE6WemIhJz+6DfXRebb54xOW9Nu6vH4SOYk4UV'
        b'OGtAzLHoIqucUQ2zlnJxybb6MOGuRJg/Sg+W29LZFiQSFjxWx85LkE8CwQSxlop9WLVVnvbYp2iJ47fjSAAsiLgB944SV66ATjFO6Sti6zl9V9ZBdnSvrMY2fHT8LFSp'
        b'OSkQ1VzAbDeSZkYYTTuA4wLi3/VYaaMW7Q/5F7z22qclKOFjjaBMEyLwJJMfu+oPlSlYaxtA6jSTQqcd4m4ThBSbwISmoxdhcZceLCjBw+CbiWY4aEx0a46UuvzLuHBD'
        b'CQtOBRBm5JNOMkhUp5r0lZ102I3bsV1FSRyjh6XnE+Ivhdphi5ea8JQuvTcG1XJQo6lHGFcLcwkqHubW+HA7s3sS586GpS0wx5x3AwbbiIqWRRw/SrJ7x346iy4Y32aZ'
        b'BNXeuwkvKkjtkaRD8y1Y3E/XUOCBs0eUSYBfJNmg7VSmHnar3JWlTdS4Qou24m3Cuhr6rRqWzZPCbkLHTiLWeVr2fjCrD20ah46qZGCuJ+YbhMrjQCDUxEEHjBAcVZwJ'
        b'YeZSHEhn1i66+kWivxPEJvKw1wqL7obuJD5NUtA5erbdl/aTG4QPM61INIM+wplaYtVFyiER6ecJK+8DYyckk/YepO0t34G67VgTTWL3LEsgHsvQJ7gauYOFWVBMtJxE'
        b'j9xgaDTDvPSfkax0C8ZOraKBEzNKVQYRFyYilnDc8Iy6EVYRCgQZ3aKv2zbHRirqY+9meyO632Ucj4VRefcwlqRMQlKf6CA+3ArLOHAoQZk2lI+dacD8vznnj0CNDDTo'
        b'EzVfysBmL+gW04/9sBBN7GbwLhHHSsKmOrqNaqXt2ONJGN5E2DlCp1+GNbdxGRaP6CArrGKJ3UY+WJrInF0ezFIV5U/nk7+HSEuxigwOR28h4J+5aUioPr/PjyWm92rb'
        b'0vpqbHSxYfcOU2zdc4qEBkIQFwKJxzpxOKuCLYd3Yp8qaY75FyHPBeedYETxBq2hliSgeqLQPQKC+wU5aDdwh0ZlUhP6bNShy3kfNNuRvJCvH7gJB3fvl5PDotMuWKyM'
        b'uS7+pBUvWpGQVeiAk+opOGut4mUL3XZY6+zoRAczDS0yhPq9RPILMsMMNVhC1jxRg3nIMSSAHxOSaJZ1fR8BXO0ZyFfm4GI+lMjV8pU9RBPasDCZTq6f0YJZGxI/amPi'
        b'oMeegJqZ4GuxRA+nD5JuUx0LRXLQHWcIgzLw4JgjPmT6OWafpuOd8c4gpv7ETo5k6x4o24t5FnQwD3Sh+w40ahJgFu1i/mTZ23IHYwNp5LojathA8oNcBpOC8rQPJJHK'
        b'RzJ9LpGJaujXxuaTejdYaEUAnVwLLFy+bgzDlrDkCj2mstC8kySs1mAYukJKzxj0WIaSDES8+6Bj8n5Y8DS5ht3G0OQJ/eY2p3BalhhLo8dO0mvbcWofsbkhhiTNAVon'
        b'7UjMHrHC5bNGRN0az4Sphd4J3BJCwFOE2Qe8aY6m3Ud3ON1hFYCKruDQUVg0FXHxsdBhpMVK2dDhD7NyNlwtmzZs4wxOB7DLRXKXRHGuAhsrv3bvqqmYS5G67HDLy0IY'
        b'cFggtBfQBY2GcC/szXD0wgoB9kUIhDYCZIaOVq64zV2S5xZY3pPM5gMCoQt7JV+dM1Dh/Uws9PKQvXWDt43BgETacVmJUH7My08EPfoCoS19lQJ1fEVZwqALWOote8tN'
        b'IHRgYXElt/gSOpWq2MNMavIwz5vUErDKlE/Lg2UNuoBSU1mNswKhnwC7Txzh568wO4alPnIEtZxVrVrXgTPOxeB0hJe5KAiHeCNccIKpkPvCRe+Cl6cslm4SCM0FWESi'
        b'Pbco/1v7ORvcfpjlTXDEg02FrlznIS7zrNZRxNdji3kg8/7dLQJTMffxwi1pmbZzfzPYYhTDF+7xOyv9MMYhqz7KVsDCx1y50bg0tfhvvt0iK/kSESmdA5I7tUF+W511'
        b'8mMz3v5tWEpXhkrTT299VHVCy+WEUVWFgbG7u8cNQy3307q//d1/mvrdPPHXMYfDl5ubCr/2WsJH8+8sSmJi/j79/lvzdr9Je1OuzOv994v/W82uL/jCwk+tf6Bwo2W6'
        b'snPszuvD7yp/ZRMo5n+tZOB7GfF3HJYPasyW73D1vWSs+pu/t+Vd0d731u9/EJC+6fAfTB6175XU9/h3+Cc123369QWF329eUvjD5idF7nMGv/EJ7Pz42C8P/rK87rTD'
        b'ty4Mun77zg/GTlX8qe5bp4dObav3PN0BjhWZtj/8yl2x1uiV4Nffvatl+qOz9l1nTBYDX4v79T0j36EoYw/L7D37A0qzApNy3+s0iirL1LCMM740N/ZKb8fOtwv+/InC'
        b'm+1H30r1ifXJyP3gT+6uZn0tiecSogP/ozn2fEP0hT9/fOBdJ5Mh37dmVF9P+VHbzdSG/R6LaX9JPOf6KCanpVr2x0bztQ9O6S14XL9lFPKfle/npX7zzk9//o2Gum/a'
        b'S/7c2Th++Webfvj3wUPlxZ9UhVv3vF4RP+6x64P/eJQ6f3mxJPbs17bFfvxVHcfH+z9Oeu3drwoGVN7o3/q9xYNp/4hR/Otf5UsPN736x+GYyo+vqezysn3/ZGKp4gnj'
        b'tL9kpT1Rc9Hfc/iD6fB/Llkq2mS57ctaVqnvvVyt+u3XI2V6fu32p5+KX3vv7a6PLn63cF/BtZ8mKSX3lbdf/m2tx/WYHzd/yWi5UGmp5/KXrSVK3x/d+mmC3PSvX7OP'
        b'PGrodeRXDt+aDv3oo29/Ghvk8tqX/tSwNP2toDBh6bemB/9L5k6GsmR203IXHP1BbeZS8alvDxhZXmirAa0Gh+gft6YOTOSeHQ3ftvWNV37kovDWG1+2+vNEpfjSjmNN'
        b'et9rPW7/E/+Psn62+dA2+19e+Nt3lip+uuXT1497DcFbY/Odd2WPfVVS0vGOcYee3xG7N/9r6hXJp69I+o8+8Dzy4P6NJ+8sxVoMdFac/eM/rP/wadCJiHxTJS6wHAb0'
        b'JYTQQhLfqjmKUgF1vnz22CO1hHUxrcmmfNh6JhZxUa+x/oHKcbobt6R5YIpTfBrbMDNoK6eqKqoSly9VT01XIdY8Jw6GZYFBpowCSYB9XH+bS6Ri5yiTdlK48mwGPsy4'
        b'pion0HcSE+fIxlq++MZYFjZIrqtcS8c5dSiBMnUFrNqkqoQT6tdlBaZqMjjqeoJrpEcy2jDWrD7aYsI/zT8K5SvD+8jIwTxW2/KVpkmZKlKWPoOLtiySf0BkTZxxmAvi'
        b'TccioQTKFa7RCiW7aCczULzBkDgrB09UPNL2sGVMevo8rQ3XGrFB8RSoi3u+3Y3d/21s6f/5X6YGHMX9/+UvvqV5aGhicnhUaCgXbN1PfwnMRSKRcL/QkEsu0xIpiGWE'
        b'CmI5Ef0Rq8lqaWkpamzXkNeQ01LS0ZYR6Xjo7zqYJdgvEjqysGsZGXrXMEtgsWXPSfZ76EGhAh+QHbmf/ynoGP+7vH7IFmcNsZpYS8MqS2Dkyn/qJTIVmYnM6W9zuX3c'
        b'T9wfFVmWyrZlzf+pVqshy+LUb7LtPA3ctv2/v+r/MxAT8ofBhVCzI2IVZyVq7FpfT1nbIYqrBVh2y5uUh0oSenKJHhT7eUMxVMoL1DaLt12E+vivyHgIJVuFAsGvg3MP'
        b'lLv5ip01To2YuH33jV/ZqOnfq3IX3VPcZZAnO7Fjsust5W9u9ZqY/uOlOZtDvzQ0yO2I8bf8qfVjpfpB99dM7rx6zmIsbNn6y3/Y89M36/9fcdcaG0URx3dv79XHtdAi'
        b'KBRKA8W21+uDPqCWVym0vd5dr1CK2oib63WPrlzvlts9LBQSQmi1tIBtqUEe1hoRKlB5tLW8ipkxkmgQlcTIxETjB/0AIZoYo/jF+c+2QPymMSGX/O7mZnZuHrs3v7nb'
        b'3+9/4mL6qQ/O4qHBz1vKD5YeGfut/9ZE7Ld1abMC3/T07LtTH1N6M/RZj68rmTavo+TVok13Ns5dVP/L97nebfUHy/t2Hf8rxdpwc+Ol+0JJbXpc2a3CgaUjKROVXeGy'
        b'6Ftd5NrX3+0Y2nXnj4FPb1+/3TeYMpT/c8DemzyKz/6EDhVMe/D0qnf2tqcFu/M6hFl19xoT5+28t+BjfnXKj9Ybryt76j6pUjrUl35Iyhz+EhWFlK74EjJebjHd/3V3'
        b'pfZV29H6rf1nhLElvye33xWzYjYduvFKZiqTzM4ppBSdUlKvl2lhLVwcupCHTxvwqVY8wkqsrn7Z5XXg87gT7q/1euFW9On4qoAGJbr6QAm1xaHPRja+Brp8+BGHTkaS'
        b'MC8Vv6EvbcOWGS7nTNzjyfJYOLPRYEX9iSznGcrdT+OuXDPH475ZdRz8KHpUjyk7uDDBjg9kOHBnYzHu5rmYHAPdH7xpYCowSUbj+mJnQifRMc5Yw6NzrXiALR11uMvm'
        b'cmYnoRNOh16GS8D7hBp0fakuIbtI96uvMUszPIEO60JwHulGUYl0s3tNr9qDj0134v2ZTiOXhPsEdDmngelT3A2rXNXZNUXoOPqwgOcsuNdgnocOsGa/iE42uBYX0MMi'
        b'NpduKJGYJpSuE1nL0ukYDkG2E0+0evTsBDws5KesmHQ9ay3GXRB47qCA+yOccR2PrtAd3oA+JL24eyFo9TzZHBpCFzhjPo/OrES7dQe3q2X4uN2B97v5SnyFM7bwaLy4'
        b'TZe1da/h7eAXF48vueFTPbTvRm7OLiPak5bEJtFow4MuJ0RV6/bAaMdl0nE4bKB75zNoL2u7YwNqVx8rEetEg2iPAZ2bb9HA2heP0o3LRBy+kIhHVdSJP1LwyFbKM2zg'
        b'YT2OxhYYLXgYH2V1xT9VyPREdqiPoycd3XYXGOCfdl0BZDcnT3q/4WMVUzF0O81sFcdjqVEXOpvhdGQ9y8y8mLWh14n259Y4Ms1c5VrLzipRt+gb3oYOxOFzeITnwugy'
        b'T4kVfj+9Qld478XtZXBfNOpt9ri9Js60k8fv5W5kA5ZWRbkSzXNE14Mx9tZJQjU7akQdqU42GXOnhelg72OWgifxgNvAxSwy0O6G9ImE23ov2qsd2R5HDk/7i95F54XY'
        b'Hct1F4NL/EwXnRBXTlsjPZxeOrTdyQUCfht3bmOUT6NE6Ii9KjsLnIRhOuhEnEbjBjyc7WP2ayoahfpNHO9Awy4OH9bapmLqZDz5r/P/aVGY+QSYxaPoyAqsPglWple3'
        b'sscM5ktmnVROglIL/MjAEyxp0iWMlhRC/171NfXI04VQjB5kESEohSK1dB0jJi2qBCViDMqqRoxNsp9iWJFCRFC1CDE1btcklRgbw+EgEeSQRkwBSo7oU8QX2iwRkxxS'
        b'ohoR/M0RIoQjTcQckIOaRBMtPoUIO2SFmHyqX5aJ0Cy10iK0+lhZheC2vpBfImYl2hiU/SR+ra5B9Pi20IPjlYikaXJgu9jaEiRWd9i/pUKmjYxpLCiWQuAFRWyyGhY1'
        b'uUWiFbUoxFhRu6aC2BRfRJVEmgXSazK9JdxUskSPjSE2yZtljVh8fr+kaCqxsY6JWphyvdBmIrzgcZM4tVkOaKIUiYQjxBYN+Zt9ckhqEqVWP4kRRVWiQyWKJCEUFsON'
        b'gajqZ8GJSMxUgnYnGgIzqEfESx/vjMhaoGbVAJUAXoD1AB6AVQBVAMUARQA1AKUAiwGWAywFKAN4DmAJQDmAEyAXIB9gBYAbAKzKIhsAVgMUACwDcAFUAKwBKAGoBSgE'
        b'yGNJkMatg1f1ACsfCv3gRIp5SKL+bHiMRLG8B9YAPVMkf3MOmSaKk68nOfWD2ZPp+YrPvwWcwECDCnlSU02mlUn2iEUUfcGgKOqnLBP13YX3zXpY0cgX8M7zU2z3H8Gm'
        b'iXUZnfdoUFoBKRWi2BoNlBf890unfgaz9/sbgchSjQ=='
    ))))
