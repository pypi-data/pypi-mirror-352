
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
        b'eJy0vQdAVFfWOP7KzDB0REBU1MHKUAYUY4+KWIChCdjQZBh4A4wObQo2NPYBEbCXqFESe+816ubefCm7STabZHezs9lvN7ubbMqWbLLVzbf5n3vvm2GGpu7+/iKPd1+5'
        b'59x7zz3tnnveb7hO/0T4nQ6/tilwkLhiroIr5iVeEjZxxYJJPKqQxHbeOlxSmJQbuWUqm26xYFJJyo38Bt7kZxI28jwnqQo5/0qt38OlAYWz8tM0VTWSw2LS1JRr7JUm'
        b'Tf5Ke2VNtWa2udpuKqvU1BrLlhkrTLqAgKJKs839rGQqN1ebbJpyR3WZ3VxTbdMYqyVNmcVos8FVe41meY11mWa52V6pISB0AWWjvNoQD79x8BtI2rEWDk7OyTsFp+hU'
        b'OJVOldPPqXb6OwOcgc4gZ7AzxBnqDHP2cYY7+zojnJHOKGc/Z7Szv3OAc6AzxjnIOdg5xKlxxjqHOoc5hztHOEc6R5XH0R5Rr4lrVGzk1mhXBTTEbeQWcC8KhVyDdiPH'
        b'c2vj1moXQv9BT5Rrxdwy7y7m4XcM/PYl6CloNxdy2tBcixrOv28UBgSK5KzE8m76As4xggwI2oY342bclJc9Fzfiljwtbsmcl5+k4vCx+lGzFPjBbLRFKzoGwLP6JUv0'
        b'mYmZSbgJ70LX8LYcJReCt4q5w9IcUXB7ENo5hdxXcmgz3qBQ8OjIKrzNMQRuoQ2j0dkEeG9bTk4mbtFmKjjkRE3heJeI7lj1WsExiGCNX0BH9WNS4Qk9bs2DitLRntBY'
        b'cTI+j646Ykg92wbil8gTmTnsAbR7WQi+II7GDzi5Enwc30L7bZk5OnwYtwJAvI3nAjIFdGkx3uUYRippGoyvBuIrofi6DTXhm7X4Wh1qDg1eNYHjYoYp/NCNaVqeNngJ'
        b'voq24+bsLLxN5PAWdEvE93l0cBbaAA8QMpiPdmXq0fk46JOterwtIA815RHEUEtybpJWxc2Z5dcA3dsEj5MeQuf6z8dXAafsvLHPKDllA4+PDSmDm9EE8RsKdUJWErqL'
        b'ribmJOl4LihSDIhCO2RcGlDrwISMxHouHjdlkzYF4u0CvrAQtZXxnSZZqpsCdhMC9SVP7r8lUGecU+uMdyY4E51JTp0z2ZniHO0cU54qky3f6A9kKwDZ8h6yFSjZ8msF'
        b'mWw3dSZbgvTALmRrYGQ7Wq3igrhfTRc0JYlvLy7m6MUfWwROwWnygZYTa+b2YxfzHf5cGPeVQ1lSYiltCGAXh5gUnJoLi1dOL7H8PsOfO81ZAuDye+ZohTr7jzAFPh71'
        b'tXBj9IGq/pzFH27sGrafv+TXGBI6vWTMR9YBKUfZ5fQh34TuDj0dq8z/Ff/v6Nmpv+JcnCOJ0dvNNTCBmpPnxsXhrckZQArodFFcVg5uS9RlJmXl8KFjuepQ/6fxBpMj'
        b'nUyjZeiAzW6tr3PY8E18CV/DV/ANfBlfx1dD1UEBIf7BgagNNaJtY1LGjhk3+qlUdBNdggmzDl9A9xf74/PqUkc2oaZdufiBPjsrNzNHj9tg8m7DW4Him3ALIBOXiNej'
        b'ffE6bVICuohOoXMFUMsVvA/vwHvwdrwX78K7F3Bcv5TgcLQD3/OhITICfvDbjwzHWDeTE8tFeYyFRhjRNSKMseAZY5GOsbBWlMe4ojvWpOgyxopcKxl889jFzUrbRDj7'
        b'dFyS3rjke+++cmn75b2xyjfOGBd+71bYG4u/d217+972jWbe5pceVBaMZ5xIjNqekSJWqLis6uCYsV9olXY6i15aix/AcGzVZUCfwLRVTOTR5ZzR7GZzkjpBBz3VlMij'
        b'Y+gwp0KtQlKJyt6f3NyKduLDCUlxGUkCdMlVuPm8kIRu5tsj4a5lTHJCEm7JHq3Eews4VTGPzz83lt6JS8BO3JyBznOcsIbHLcWza9FZLe8S4rRa0Upa6nUQ4PAwckq5'
        b'tWaVqVpTziSVzmaqNU51iQ6zRO7bVKS/0gP4cN6qcr+kVbj8q41VJhtINZNLYbRW2Fx+BoPVUW0wuAINhjKLyVjtqDUYtEIHODgnU8BKBtOqJAdS30wCI4TAuB8mqHiB'
        b'D6BHB2kMNP1YAjST58agLQLaz6fPxy/PLhO6oQ46kOMIdQiUPhTlCg99iI+kj255QEAX+uib6yAXitGRNFs2tACfxndiOHRSHOGIgOvJ6Bw6rocbvLahhoNx2IAO0xvV'
        b'/Wrx1Ty4rpyHWjh0HSbX87SBi9AxMlzk1ix8Xc/hPegFFb2Dd01FRwNBpvF98F2BQ3dhmrxIK8On0Y1hCeTO3CX4EocPoq2LKT/H53A7bk3QqTh+MTqEdnL45Bx0kmI8'
        b'Gd+pxrvmwtmqVbiJy5mNLzj6QCkGX9UNLMK7YCASuUS0X9D6Mxh30PmqzL6ToafxZvgPDbtEb6AblehldDJuNblznLCbuwsphMyplfgUvHYXqsL74H+9jdW0YQm+MUKP'
        b'6fWb8B8dX0RBLxtcP7sB3YWOxofh/+CFtNkrRwB/uASMgd64B/9xYyhr3Q68P1KPWtHdUCgchf/AYQ5T2OhGLLpZBAL2JYHoQoF2vInBPoM24cvoMF5fCLWN4katQE3s'
        b'xtFgdCYVXcC7gHRSuBR0EF1gvX5UMxF40T64jNrwxYWcAV1n2gZ+MREdxFdt+Go93oBbeU7Ap/jheBu6T1mGD8cSvJkLebmCa+CeCVvDN/CNoEpaFQ38DqFOQVQmOpvo'
        b'4bTgEnQpLr7sNN8xOek0cQVMsZht9rKaqtqpC90zUgVQ1JxjOkGtMRpd08taCpX1GXg3uoqb4Hc9qFK5eJsW3RDHjEHNemAqV22B+ByHXsZ3AqGnd+F75tf+zilsTqhp'
        b'zszCES2Tw1FKWPryPWGl6iMbrtZu2G1v35QrKiPfdUW+dem2uHlNYen7matSV22pWBa9KetS6dv9B77zs/fq/uxIC5q7c1vKmhjrp2Nu3f1cXb9lcWGUaXxVdN0vVzdl'
        b'vPeDlctnvLsu+96qiFXX4ucvWWRe8vrDYf0+2fLzv//2T58c/+ffawa++sxzxy6PKnBOBeZJRjwDXwtM0CmmafHWRGgwOiekluLz9hhKDHPRIVBPcGNmdi7eblRygeiy'
        b'ABSwDZ2wE0ExCJ2EcW9OxNtWg/4G+qPqWWFY6hR7LCVJMzpPZSTeCvoY9NO5LCXXd6yI7uPn8c7hlZQBV82ALgLOTfg23okOyrz76YVd2KhW0Zmvdhq/QFN1WY1kMhDG'
        b'SlnqSEIlGQpewat5gaM/vPBvlaiGKwFwLUQI40P4ID6at4Z5sVze5gqorjHYwDqoNNmsRBGwEibVFSPBGk7O+3g4Lakm08Npb4d7c1oN6ZNteD/ez4hIV+omIwU3AO9U'
        b'LE/BrY/guVQi+/DcR8vkbs2FrjLZn+ldw/V9dSohA85KltxODmXa1FghM3Efp+G5kpKl75SmcbPp1YSJYbXbeJgZtSWWtNAF7NFnwwMW/k0ELTmsJPt3eTqOcbN1qfhg'
        b'akoyblQQBYYrLUD3zDunnVfYFsHd36wzflnyRUllebbxrfK4vZ+tu3TgyqLMyVulgv0b+0+KjkpJlD6TPitJHCNe6T85ut+YqINpUsHCgujiA8PTErdEzA/THyJKwm2V'
        b'JCweVwjKwSRu2E8j17//f1qByn/UBIpVOxPxRLyjQ/iOkBSWaCfKZwpuq0vQVeETmYnxWh0ob8C2uWiN4tnlK7X845Fdn7JKU9kyQ5nVJJntNVaDLM8pBRRHU+ILgSMQ'
        b'WV8vIhPLzJLLr6zGUW23ruydxkgXWiM9NEZqWeyBcNKHxoilugyfHwjkVRGXAeYSas3TgVLaBO1KRjDJQMY/jQ6q8AmwSO53sSE81Eb1Px7orUP/4ymt9a7jd9H/CMIj'
        b'utDaUEZr1oV9LSEcpbWYQ0NsMln9Y3ZYw1WRklXQQ/+RXBG9WrhKaf0W9HwOFPo+o2R7YNsokSsWmG0rqoLZxZnDggqm8ClgGJQEBdaHsYvWFRH2z7h88nrMrrQp7OLV'
        b'mJjKcLGWPLmkPa2eXcyr1aj8+XUEfMzc0NHs4qGS4SPjhO3kdSFngpZd/EuJduEF8SgAL5nx03j59c/9k9b2FS+ROoVj0RK7OHSYKvsUD7SoKQm6snQMu3h4XGB9FUdn'
        b'StAH9RZ2kVeOHCNx+8mTQ7f0lwEFTk7QxIinyJPCRFsCu6hN77/iS7GEQI/5cewQdvF0vP+ACEFDLlp+viKEXfy7FBp1kQMzN6Uk+9RyM7t4khsgvCdWkjpjhgwqYhcN'
        b'qsFFe8QV5Mkl/1iWxS6u6Tes6KDYSDpZmGtdyy6mRURF/QY4DOA5ZVRKIruYu0Bn9xdvkdeHnkvg2cWcGWM1VcK7pOus32TkyV3nN2bCs8IbpM7wr5XD2cVPk1OG/0b4'
        b'Hun5oeOHTOO0wx2EuxryFhLTdjSHL6HG0eg4OucAzYSbr6xJVRC/R03KGLSxij6KziAnej5VIMZwvCEVrfd3EIa8EB9H+1JBmo/l8lVj4wbQZ/3BUrqaChPgKW4sPvjU'
        b'M2gzVZey8dEVqUC14zh0Cl8bl2ehNaAHi5enwgQZD8Z88fjIVKZZrcH3U2HGTODAqtg1ITuSKkkL8AtqdBVOJnL4gd9E/AK+TOGtwlfQDnQVUJ7EjSuZhB/0oZcH4Kuo'
        b'icyMGVwFvjcDtWeyllzEuyps0JB0Dq9PSsdNqynICmjhbaKXzOSMQ2ai/akUu0J8e5QNWjKLm18yqxLvoDXgU1MsNmjIbA63oLbZi9BVpnndB6vzRRu0ZQ6HXsB75uAH'
        b'6Apj0m3oFr5jgwZlcOgI3phRgF+iNzL6og2YtCgTcMEtmaDsOSk2xXgfoA+4Z3F6dCdryFraAfhMFagEVwF3PYeO1uvxy5X0afyi3xJ8FXDP5krwgWx9naxT4m1h+Cpg'
        b'n8P1Q+05WbiRtikIN2nxVcA/l8upy50/mLZpxRjozquAex5XHJ8H2v1lhvlL6CogApjnk6FozX8W3aLPR6FNUcRnN5dDe9HBuejgYEo6YnB5IGBdwNWhtoL5agpvcNaS'
        b'QEC5kJuCXipEm/0pyuiFSnQqEFAu4hLwlaKnLPTqs1PRwUBAeB4gP3secibQjkUbwFQ/HQgYz+fwdrRtPmrFZxl6W9BpdDYQ0F4AnTN1AYztETbI59C92kBAeyGHW4sX'
        b'zkUP6OUa/NIk1AwnizhL2SJ8G2wYcvmpIYmoGdAuBiViYjHaiu6yDjw7ewFqFohIANX91mJ8br7lH999992iAEWIU2AM8yvFBDbFdujHxx3kPyTT1pqlWsyZM9Bope1H'
        b'pKu+eLWqbXKumBY282yFamNw9DeLF06t/7W4vY6vnl6yXbN66OVNr/5a/fbMbz6Jem97HbfhF5NrNa1p6t+sU8/74OLGM/ueuXHcaPvlttqffn/LVxcvzD+b+8PCGcbz'
        b'jlWpP/nscmvFxqniuJ+V/sswTnL2ufv7yz/kX4uNnBNTaEPaikPPZe/6bMRq48fzW37z3q1rCb8wfHT7tzvbWo3HP00tnv/lS3/alnlcP2L1qraoyDX/t3xPXsCi0R+Y'
        b'vrv1k4tv/zT7fypOvB5f2efTjZ/+vMh699fj48v/zznk1+cmPdUaA8ot0WCHogsK0E9zifusLTEVn+NBhT0r4AvoQSXVYNH5/ooO3WAGvikk4XPogJ06MDc+i06Csga2'
        b'cQ5YXTeTsoifMxzfErFzGD5K9Vd0tuA50F+36TOJL0A1IQu1Cf1h0F6gNeDD6ck2dD4jNwk0vx1xxBeK20SuD94uoksLFmiV3eoWiu4UAS+NI0TWOBxlBqLwUnXDQsSt'
        b'FMQrQKcFlUOQ9V3vH/4/uPatSqUAxSIaaowQQ0CVCQPNmfy1Rrlx0oqgzDjKetNheGs/N/L0PYlzqy8v+DgjiMKuFPAOUF/cyksOHODsFH6ReH61eJ0S7XoKb36E6kKc'
        b'n5yX6sI/UnWpfDw12Y+pLv6mYC4uYRxVMmyzLbLqYhkWwBWtTiBCNZFfHs2UXxveiw+lpijwnUKm/Nah6+aDN4cKNuIWlH7zqy9Lir93aXv7rtMb2zeePjB68+iD7RlD'
        b'N2uj39Abc42Vpp2Ky9EF+9MS67YUbwl5bYDq6KS9lqMD3gnifvjX4Ozaoy1/1PLMk3WcyBc3KePGSOLIAgu/ya3H9kJQAxhB2exWR5ndAYqswWoqN1nBnmLEFUQ65DlO'
        b'UIOxRDXZaK/BV9jg4d5Hv79n9MmLGzyjv85n9ImYD8D7FntGP1mH9q3UxufotElZOagpOStHn5QFtlOukoO2bg0AEb4H3XwkKfhqsY8mhS5eKnfFvqSgynVQBrIDX5oV'
        b'iBrxOuKhICb/AcCqlRLEi8ue4irjghVE+TkXUMTNNk881STYxsOts/s+/LJkCR34yxvr+LKA38x4bejtkBMhr5W/dqo84oRl79DjEZ+WbAlRhU3bvx6Uj5DWQO3MvWDT'
        b'EKD4Wg6+oMdXOzgXjPWu+ZTlocPaqQk6tz2DQEbLJs1idFYes54pIbqTMeNLBwGMDvzVfBTQgXWANxWUPZIKBnqogLzYRCoMo1TA/dOHDpLhWjjeEwF0kJ3Y1YjxJoOV'
        b'6LQ/bow1PdJuFjv5Kh9tN3ehAr4HKqAjHWsLrYwVmJI9XbeaidvWYKU9hxktiRcmpbKLjkJhxRXZaAnX6DnzaNVOpU0P5eKXKr8s+X3JG6WV5edMn5WcMr5Rnjzms5KF'
        b'37u1PRa4Av9GeZZxZ8lnkvDeW5q17c/4pfvZAgpTX5rww8z0Uemx+XnUL55fELZs/BCZTGZkgtJ8Fj2Pz2bnJAqcQs+jK6X4kJ0umZ0uzsfNU/H1RNyanJeDW3Iz0TkF'
        b'169AMc7meFzbN7jatMJukBwmg2S0MxoJYzQSFsBHgJhQw4CG8NYYD6UoXAryqMvfYjJK8NbKRzhYCKrWwR7KIRW1eVHONz7m71DSroNrlLiZrM+hpjxtDmrJy0yElk1T'
        b'ciPwFWVxJXq5TPQaVaU3sUxixKKgy2dKp6pcJROMSJ3bCiAY0UMwCkow4lpFTwRDqlZ1IRglI5jikFROsh9QEhPIf5FsgPXLVHDqknolEEx2SWE1Z/46/4HSVgp35iwZ'
        b'Nmjb5eB1KUGKX9YXpKT95M2Qa7t3bD/aXOCaN+DqrA8jmr+4NPEvD9+fmPRySlyU8s0ffVky56U3/QYevBXXb8qLt2Z+8s69+JXVU05vmrbz5IdjJv5j/JR/ffd23ML3'
        b'rpVNnvZ0Uf+YvwWAwkQ5y8UovIl67fy4WKWAXuTn4ZN4N130AINh20K22KtQLA3n0ZEl+Ah1o+AjpfiYHjeNwscT4eWWPJ5T420C2jSOCSd0Eh0C9bQZNyYDu1LkrEHX'
        b'efSgCG2iHpp4dDwON+egc9QKaYPX+DnoLr7Ym3qk6vFWZxoNqjB1ItEBjET7A3kKCqrNBPBBgiCohfBvFSrrEA+xKgmxAoUS+nOpyhz2mnJvHtft7AAiJt5Pq8aXcEml'
        b'B7wI9/OozoSLNoNWekGfl+RFt0pu8YAh6EUFPojO49M9S7oJnKz0kBVfrlz5BNKui88mGH4ju5DtEEa21yf/gOOqkkRQcTIdowRGtnOrNNwH5nXUZ7LGtlL2mdj8uZhV'
        b'I4gvItu5ooRd/G5pIBeWpKXuwdlVss/ENCucWxFJFjdLYj4IHMEu7o8dxK0Q7UTDajjfb5h80fgUt7+UOhPGTKmXHSlTBvpx+0MGEqMme6RV9u28PSOOeyvyJHXOXFk9'
        b'lV3cUzGVKxnwHWHSY96fHckuFtVO4Raa/04AWb8aI3tX3g+czOXXfU7wHDPcMpBdjBsYze0vNpE6GxT1A9jFaE0iVzmMOnxKny01yE/OCOO2r0wjHZL9aa2JXbwwYjoX'
        b'Md6Ph4tjBi0JZBdr1iq5f0yKpCLiwNpS+fXSIOKpIHVmNwmyb8dcPoCL9l9KUGr4XWwFu1geMZ7bPfGXpO3hSxdGs4upprlckG4mAZT1nqqQXSwpMHG7y/fxAKj8Uqzc'
        b'yVXqCq5o4GEeXh8ZPCKJXTQm9+M+m0t9Ow2uWfLrdfNCue1jJ5GuSzwXsVweYr9V3Fd5f+ABpfr2IbLQi1s2hps57PsEpHXS3BXs4tq4odyxdCLyS0oX1T7LmV+d4VLa'
        b'RgI973y4b96OnFycErb59cvf/ObVETn+OUsnBNz8LHJ2aR//pnOvn72Ucndw+21u1McxhzZerhv24bYHvxufujar4dMfD526e8Gz2f8zZdXHP/Z/51eRAYEhKemZ74rf'
        b'5/MX/er5Oc+k7ImaXSuc/e7phtcXzx3ySuYHw1drXsl9u3gHek1Y0HdZ3zuZv37n62853euTC8T8d5aU/OD0B386u/vPW/52rS26ft+HBWmfrHg/8uzWfz1l/ihv6b//'
        b'FnsvYOmmWXce/vjVgZmTTr0xqL75mEt/LuoV/y/e+AWa+NJz6rXHVieO/+L9t9I/a7Z/VPlh+Zzd5hdx4fOXDh4s2/tRn7831T/37OqPGn+xb+Oygtf7VoyXLlz6evkL'
        b'v531lkGqPnD4duPNvKUXNrwVr0gxJWxK/faHFVN/ePSXz3H1Z8xvPv+NVmQy+6WqULLa0pqMby3yldnT0uyErWnwdrRenxiXAfoRz+EH6JAazN2VUbiR+cL3mfEh0J2v'
        b'J0Ad8TyncPC4CW0O1wY/gp0++tALs/Z2lhNmXGqsXmaorLGYCXOlHHk+48gT1SLwZPgdTpWHMF5DV2fCqCIRLgQpAoBTA9NkP2Knv+zsd4qYIODpYKcCPwc7daiHm4OS'
        b'utJktHox8F7kC28d5uHdpIoLXrz7gwhv3p1I+vXA9Bh9Hto9jzDvLDDym1Erjc5ow03ZMEaJKu5pfFmFb6Gj07uYFkr5r62cMEMSHscVC1Ig9b8LYLkIkrjJv1g0KSSF'
        b'pNzEbeSLlXCuks9VcO4nn/vBuVo+V5sURCKUC5K/FLBJDVf8naAaFwdQVSXI5ZcmSVaTzZZbpvLCRS3/UuY/lUgVFj/kiScqV8uyRdWoBtniB7JF5ZEtflS2qNb69SRb'
        b'iNDqalQr2Xq/Bl9YghpRO9jJXCwXizfgOyxOpOl7XytsDjhL//71QVsv90EpYYrv8vZKJze9OjMiTflO3PeaVOqnN3wVuWNJ/4KTL2f+7dP6v2lz9n/x5rF/hcwzNhxp'
        b'WpXg2lP3ICLsX9d/tb49p+2da2VvPHjb4ei7v+3vB+KCDH95o2TMu99789IIdOC3P+5/OHWXbfRHppX/x71xacj4j9O0AUyFcUZzbGLhi/gMTC46sdCDuXTeoX349AL3'
        b'OqaIL61ly5joWBTzMu2b+VSCjq2wVqD7dJEVnc+gr+LtMTNoOBluqcFnScX4roCa8OUGNmUPo2PpCbokYudNwGdV6JiQAmCOMYZwaPYE1IzacJs+iahOfqPxbi4wSsBO'
        b'Dh2kT9Ti02gDas4jPKMlQQvn59AZBRfqL9rrqmjDpgGENvpEIjqt4PBu3K5SC/0b/KkHy1g1DDUng96mw9vxukwWgBeOj4t4Pb6MWqn2hw6iWwRIsk6blZPEr0Yvc4G4'
        b'WcA315i6qvTqx+YqHVzDz2CoNi03GCivGMx4xRqFvIobRZfXSOCMSv5ZFSrTtk5+j81/tUsss9joShqYq2b7Spe6toYs+Esml8pmt5pMdleQo7rDC9KbZaKykghRK/FY'
        b'sbU5Ehlo1ZJDvIdxkKWvb70Yx5YBXoyjC5Y+6h0v/5LJYCMzsoFbyqYUn3uad6kN8tIhnCtsJotXhAPrMvUUi7GqVDJODYZaviE1rgpzw3PfeiyAmwCglncpDaTHrEke'
        b'KB5QVmKvh8Cr1hSuU4RGT3VWsjr9De7+77He0CeqV8bVz8BGs8daw7qt1UejJgG1xHcE/PPxdekua+3kn8B15ndirjk/8C+8jcy+15a2fVnyWclbpc3rK8uDyn/1Fjz8'
        b'tfDqYruWp9whE72IW9jsxPvRCTJDyexcgNYxoha6nTDBZpuXN68jvuw5+IlaFekmBJ+nWHiMaNWRWjoo3xtAkqcXiWstHDrPFs4oex33VYg3bXcPAjg9+acNBPo1kMA2'
        b'g8EVYDCwIG04DzIY6hxGC7tDZw9MUWtNrckKpEdnGZ10HVNtLG0sCYQz2mxlJovFPdc7z9fThNrYY/AIbcJwOPyd9Azx0qqVlKC+C+8TxNMfASQ7Zft7kyUbOr86O1Ob'
        b'laRTcQFLgbmim2hXl3EOlP/atvFeYpwvFneLu0N3h8Fv8O5Qs1AuwJn8IwktKimRiHmv8NwwELFE0PuDyFaYlCDo/TZxINb9WwQQ9kopgJYDadkPykG0HEzLaiiH0HIo'
        b'LftDOYyW+9ByAJTDabkvLQdCOYKWI2k5CMpRtNyPloMBswCYAtFS/03q4hDSEomoFANaeIpzEKgnA6UYql6EwruDyLumUGkwvC0Wh9GWh0pDWgQpSfaoiJJGiqVt6wPP'
        b'D6WwhlFY4VAeTssjaLkve3u33251ubhbIY1sESUdVURYvD3prRBnaLm/FCdpaY0RUEM8rSGB1hApiXRSJoOyU0b55cNRARqvf/JVthHA545W5VKYQU91KQgxdkd7uWV+'
        b'XoNP5kuIe6JnEd7BtCZ/0oHywLrjsUPKQ2Se4kd1KDXwFD8PT1FTnuK3Vg08haGv+PifQNM+6JF/mdVmu9loMa8iOxgqTRqj3BgzSDBjdRnZAtH5lUm1RquxSkMaNkkz'
        b'ywxvWemrmTPScjU1Vo1RMybJ7qi1mKASeqO8xlqlqSnvUhH5Z2Lvx5GXEzUzMtO1pIq4tPT0vHm5RYbceTkzZhXAjbRcvSE9b+Ysra7baooAjMVot0NVy80Wi6bUpCmr'
        b'qa6HKW+SyM4MgkZZjRWYSW1NtWSurui2FtoCo8NeU2W0m8uMFstKnSatml022zTUqw31QXs09dBnEsiyrujI3UNGfBLFi5y595m4uxfsFpBXPb4si2X2vlyAPirMS0od'
        b'PW6cJi07PyNNM0bbqdZu28QgaeJqasmWFaOlmw50A4XmyBDhrHuMH6cetzhmdblL/3l9TAyz2tj5f1BXFyd8V59qUC7b43GxwEK8j4k6sgdEvwA36tGJKLplhTjR0MuZ'
        b'SdQb8VFBGxfDc9Ff1VaHfPb0ZM5BFmRW4n1LwWw7JeSgc/m4kWxHScZNcJZXCPVAJfMyyEJuTk5mDs+hrfhFf3wD34tljqVkPy4I1IpLyjVBZWqRcxAZivbjC/gMWRtO'
        b'0JPwx+y5GYDW3Uymh59R4J1adJorTPPD+8LRTVrPqb4iNY/WSZWWOfkFzHfSNk9JTDLNuoSq7E8GRrMNCPPnZnXUDLbmLbKRh2xZAWSTCzLw1mwVNwcfV+HL6egYXYeU'
        b'0LlYWx06MokEVLdBC6bim2b01//lbO/C3UntPxrRNrl6xuiwWa//7aVfv9z2z02a47EJJf1/v35cwYCEWdvjgo6bS7f+q37717ffnLRwwE9zbbOnLm84vn7jD8u//mrf'
        b'zbOKXW+3vZL/zKVRLasn/fRQi98q/cVR/UL/8sxf06o3DN761GvJB6uy3333T9K4Wb+O/IXln4Prv65pPvyXKTOmTfhnXsUCqaBaO3b0vW+vLD93L/PXhp3P//K3377z'
        b'tu4fpb8Wf7HcMDH03dKlfnuPlIXvHL89cKG1/5lFT10YaBgwPuzTkJd3LRl74cqb1z+5XmXZGPM/vzzyu8tZM/+g14bbiZ2At6VFB+rxxZl4mzbHkRSPtyYLXCRyKtTo'
        b'Ir7HHjmMnOaOEAEaHzCFhgjgfXiTXQOPVKE9eLtel5WTmIlacBvbGTQAXcNn6xTV4fg+s9POwBtbE/BZ/MBrUU493s4WJVD7Ej1utWez9Sx3JZF4k4hv4XvoFDXWgjj8'
        b'UoIOXcbOzuGIyegFO1FYBbwZ3YKRhxoSMNl2ROt7GRTD1mQ9tK+VBRjMQZf9wKjbGUctvHq0M4v5lSldBNrz5wq4dTB6iSKuDZqJmp8BvGWclPh5Ht8Z8hxr1Vl0ax5R'
        b'P8mLi/qK+CCPWqvxcRo5PEiZgJojzWB80jmmxHcEXlrIAh/W4zPoRS+780wsOsvMTrwVXbETCVqH2pOIbdmipXERV/BWuYNZdQnoqhJvxg8AGLWwr/ZF92mF2TyJqbku'
        b'4iM82p6JLjFET6J9UXBbl6Pi0DaDiG/w6GA52kE7oBLdKkbNuC2HxGkkZtaUKrmQCnHSsGpWc3MqWLDNeUzFK8V3VFxIujjbgS9Q61YfgO6SlxOhi3OTMtLzFFwIOiXO'
        b'TEPn3MtkIf+196yzAg/6sRnku2zyZrh199FqGk8aJKipU0zBhwhBfJRA3GNBPAtrJgEaqk4/AvzQs29VKjADGe/VuUHkMpXZn2n+08hhOuc2azsp3B12wWPb8Vo/Vkmk'
        b'b+20Tp2nYqqSz4DDEB+r4jcjva2KLqg/tlV4mliwRO/p0SZc6LYJO6C47eSHI4o8ShIRX6BQuOVXnNVklJJqqi0rtTqAIUo1ZY9tARPT3VBqLusRpcVulB4OJwiAitUr'
        b'/McCXO7uDKrX9gT5WQ/khN71oCdHgLTcmsC5rclugBs9wHXeStR/Az9Ahr+Ul10oWgGmmJHZqIw8e8JG8u2K3hSsJ0eFOiwEa55nQvSERYUHi+THUc3+005hmGh7w2Sp'
        b'B5OkR6t1/xl1Mix6QqDKg0BKEbVVALa3104jD6vGQrd894jDf+fuEenoKR6+2EVfTSe2hk1j7jRTbSZTFd1qDgYONUG6vEi2n8t2VyHYOdCyWQ5rjSbfuLLKVG23adKg'
        b'JV3V4zhoLjQaXqwfpxujS9H2rkCTf0quqwe+SMv2Ak4eF5eIzyXQXSmK6TxoNXvwGXPGF/NF2kd7kv/+ZclbpRnGNz6NK7hY91nJG6W/h7JQ+mnEaxEnnv005LUVKk1b'
        b'7P71V5Xcq9h/bmWkVsHUrP0gybeiy+O9RKksSNHRFLZhaD26XeQJ/gJ1ZG2ul5Ik4HYqy5/DR0BluzbNvUOb7c5GD+KYo303qFPn9ABprz9oLMKzfDLagFp685X5EReV'
        b'e8uQHOH0HFcfwEcRF60sCuRnmKi0PtW5tg7HGFnJqvURYTtDfJ2+vjWCCjEdHnxEABNxHXBO/rEDmNzU6exCDIUmO3MXOCx2MxjLMnN32GTrmGZYsFuN1TajV6aE0pVd'
        b'KiJ1TKKOk0klOfAMVAV/jBUma8kjbDjyr6tTVI6L2axitlnKgn6jhAUlzDabkQ/00Pxow6ww1WOaoR1oozl73jQFjY3YcSzuy5IsINrEgs9LPitZWv576YsSxY+0236W'
        b'OCt+RJB2en3f/GMbJ74wejOQ7uWCVJGL/2PggSMjtALTZi/hYyPAjvAyIkBnf4EaEpH4sJ2w7gJ8P6VDm81JRM1FXZXZZnRUDoN61DqpzWQ3uIeIymrv4Cryw7uVvlX9'
        b'3STV5Z1cNzCqZxE66z3Yij6h89Ay2QW5yoeWG73DrXoB/CSqSIjvqz3y/S2+gudx6Vfn3kFF2EPPoV80goZGzxAXoyeC5lGBX24PHdgkXT10nrlWYzVXmKuNdsDPLPUk'
        b'K6tNy2UuPlo3uhs/SM/OH4l5WGjT3ZGbAEinKTDVOcxWuWckOCuzayRTqdlu69bhRGY6YGCrqXJrXWYQoEaLrYZWwKpmnVtustp6dkc5yhhG6TMyQTSb6xykPtBW4ogY'
        b'1ljdWAGsTLuRCOZHM4yukZfqXMfTHFl6R4cL9LlkzZ2mY8hNmpvhiRYtwI3ZczPEAi06nal5ttSK29Fh61rzs/7cjIrQqv79HISetE/jQz5uGnh9gUWugENX8B6wgPEe'
        b'vg5fVy9AxxdQd8qoqeg4vhoE/Gb9QA6f4tALE0Jpoof5YKHftoU45meQtdJ5uDFxPtqFr9JYgGZ0uigjkYDZlpmNt/LAq45pV6C9w/GJIoHsSr8ZlI9PV9KQgv7oisIb'
        b'q1pPlfkLkgLwvvl+XP5zKnQMXcR3zFP+eIq31cBbfXb/IOmtH/ivmx4060cNrxnEvaWxxesOrjuaEvh6wKG3rwb+4YOUO/6xzoGNP/rJH0SUtfq5S3Wf7oq9OcXur/71'
        b'i4veq1X0zcj7n+tF37zyo/N3lr3vfP+zwVMTzqObb2kf3tvw78PPHRx46oc/qXyxeiW/+HXNXmur1p+ayAPw7Trgz3gbaoxm8YGB1QI+iE7iq3ayzIJeGon3B8Y/i66R'
        b'zRSEPbrZ6BB0VYEvoha0jorvWBiJjQlJcWVoT0dc86Ywthm5ZQC+oSf+hCPQZuZD44LCxMg8dJZ6T4rwg/G+TJqLoiwaO9FBttR+FbfFgOKANq/10h1wE9pPIdhGoZsd'
        b'kdPE9WLD14j3JQGfYzEAIFYyUHPe0+gIdUMwF8RodJgi3w/vwsfgbjhqJ14I5oIoe0YOJXys6BjCSDuYhXsr6dAOrt9XDWY84/xBMv9nJVUnduxTS64bB8rbPdywN2Eg'
        b'ej3WIRGegUMTL6+ZUYmwjvtnRI8ywQeJJ7OLgav1KAnaPZJgNDXJOlheb3bIE5ohWoqFo2fr/JgHi8nd8rr0eemd3fzd4EOikqqspnKXymauqDZJLn/g0g6rFTT+2WUK'
        b'L1yJ1zvIzQRnM2nVkXqKcwbKMTpB5UGy7FI0KkF2KUF2KTyyS0lll2KtUpZdFSC7DvQqu1jKLabgUTHgbdX0vMZE2sSEgPtdz1aCnpcLaA+wt+gr0HvkmpHYdTpNurGa'
        b'GE9G+V7pUhBn3coxspIFoqUwb8K4lNF0DYusL0nEVgW7qkfwno6fpJltMVZollea5BUyaDBpc8cT7kb1BL66xt4NGKsJGlJtm6RJ66w5l8jNeQxB2NV4C8h1EMdZCL6+'
        b'3C0H8QEFE4W4UfZ5zssA6VggS0Z+TDjaRaSSHl/N4kbgYyH4+Wi03kFytKHN6OXheh3el5MUnwVs1rsKj5TNyJoXJ6eFyOE5fHxQED61EN2lGvyq0kzuo+jhJFtA1rlR'
        b'YzkHsWDQ/lB0tHsVPikrp9CtwVvwYbK60lzojx+gHQsck8mr7fEhuJk+Rd3emUR8JswnqY9G4oteaysZiVnZusykeBWHm7VBdfhsAt1SNBefQHt95DtpC4EdB0wct61E'
        b'V/SJ2qQsJbcKn/RHLUPwXq1Ic6HEoJPoJoBGbROyckROMZVHZ60jaFhAFLqFTiTgVgFvgCr0OSRq64Cw2hRPM5YFJeCbCVnoypQcHetEnus7SsQHQTw0mZf+xM7byH7q'
        b'kX/+fNA7d4Mxak4JUuQXGJr5MZudb4R9/t7rLfG3R6vzwm6X1GfEVg3Iejsy9BbOjP/e3/umzv/26LHSFYMWJV48U35mX/7on//iz7+x/ywnsNT5x71Hlq59vu/OxU99'
        b'uzeu6M/6wm3fj/2gwS8y3NK+sfoZV+BVvzuzk+q3j3j9yPmHZYtfa+537MvQPbcSShecBiFO85QdxJfJnhu0fxGINqGUH41Oo810+QIdisabA+MLR3UvvvH1WuqDX1yP'
        b't8IYlxcwepG1gCHxTPZeT0Nn9Jn4UlxOPChWAqdGzQJaD3VT4R2cg294C+9wvN69UrPlOYoffqEcH9JnknxNbAcCj45UDGbO/x0D0TayHpIZtogExKoswlB8G4Q28TwY'
        b'0A4eNyci51zQnlg2kkQYj2QR78GnFWzL1E20nQSweVYIyPrAgExxEr6fzURn0P8jv34gEYsy86CyXdch28eqaKoItUeyB8i/QXQbDXHhC/8XoFzV11vEynXJEl7FZDVh'
        b'GlaJHEy+Yt7/yUJ6Fawmk0cJkDwSsAIOJztpAj8f6q0JdIfmk0Rxqd0v9SiB3/BI4FgiMoChUgHikTjerj+tgkYeCfDLz9ZGWQlTshLfgpVYfiTCUKopMxjoEoSV5CSj'
        b'SxUukfjnp5NiN6shLj+3B5l4fai57Ar2NWaJwuSlSVXQt9ztokPW5//R2lFPJGclRlJ/MlJb4EQtKBQRbIPvdwqBY8Px3eBxlLj+rRL/w7+KkIAgPjwASizFjiKAj4jq'
        b'/Ew4rxnCzh3EaFhbgJ22UPQgO5etEfJcwCoB2E8LOttF6AXIf23/7hRbJQnFCkksVpq5YpWkKPaDX7WkLPaXVMUBkl9x4G7lbvXusN18ubg7TFK3CFIeqEmBzrBykYZF'
        b'k6ihIFOwFCgF0RiqkBahOATKobQcRsuhUO5Dy+G0HLY7xNSHJeIB9YsE9oQ6+5Srpb5SBImDghrDd4cA3DApsoWGcNPn+pSTyKp+8hN9oU4SU0UCtSPgGRJjNUAauEld'
        b'HAm48VKMNAjOo6TB0pBNXHE/GjPFFUdLQ6Vh8Le//MZwaQQ8NUAaKY2CqwNpHBRXHCPFSwnwd5BTBTUlSknwzGAnB+c6KRnOh0gp0mi4r6HXxkipcC1WGis9BdeGyjWP'
        b'k8bD1WHSBGkiXB0uX50kTYarI+TSFOlpKI2US1OlaVAaJZemS2lQiqMQZkjpcK6l5zOlWXAeT89nS3PgPMHpD+cZUiacJzrVcJ4l6eE8ScqXXTGilCPlbvIv1kkKqrDO'
        b'danSqmgw1xkfbYmwAHaDxXOxdK6gCJJ8exVWI9EAmfpWttITYtQpkMc3OswKFVSZ7OYyDQlBNDJ3aBnTQuECUSyhTuZXsazU1FQzVbE7VU4ruFSGeqPFYXL5G9xYuMRZ'
        b'8wpyH06ptNtrJyUnL1++XGcqK9WZHNaaWiP8SbbZjXZbMimXrwD1ueMsSTKaLSt1K6osWpVLTM/Od4kZ82a7xMyZBS4xK3+RS9QXLHCJ8+YsnH1acCkZYLUbro8XzGcZ'
        b'pIFwYcEWQDjxGqGRbxA28hK/TLQNbhCO8u2cLd4uSEKDEMWRBL2NQgMQ8xpeEhv4ZSprcQNPAhfhLf6oSNL6Sqr+8Fw0F8GN59bw1Wq470fOGjnyXgNnUECtynbg+waV'
        b'pKZ2l//Hhu6skc6xbvI4d4S6dX6hJx2f9gSzMIysDnqlF1cW67JJNJqsMC9p7JjR473JSALDJLOcKPwaW62pzFxuNkmJ3ZoFZjsxIkAYuqPaKGS3hchIFuwUq7nU0YNh'
        b'MYncnlQimcqNIGU8ZFQCloq5rJLUbmb9BMQowwEC69q2z8mYP4w0V9N1qI7WjBphG+XidS4+5XMiPj7/Dv49FHUpKblaP1dYZ7Bk4cRoqa00ugLmk5bMslprrC6lrdZi'
        b'tlvriKBTOmphmlitHPUnUAWCEJh1DdfrJnQqg//Xo1sEKEBmRMiuDo1AVKJVoYwAnjwOQMtT1HpUKf7qiQJwg/AEASR1Jho6dCtrTZoSGJIyEPoW3Uz2t6REZyUm+hOE'
        b'J9Be6hGtf3g0nYE0FKF7QuwCTnCDC5PBkTm8VAh0bySAQSAD4lIbbQYa9+lSm1bU1lSDhdsjKv/yoFJGQwMcVaVgI0NXyH2gqbUYy8i6q9GusZiMNrtmjFanmWczUTIv'
        b'dZgt9iRzNfSZFXpSKikhVGqUljrgQfKAby1dV2x9NyfxNL2DJwu3Z3MST932va/eEtfHH7tjNvNqiXbGGI1pRVmlsbrCpLHSS6VGss5QwxZp4SmjptZaU28mC7ClK8nF'
        b'LpWRJdxaE8iMdNKp0LAZxupl1NNus9eA7kjZQvVjsQB5+rtRMlCUSkjfOuiUZwyGcCKPhx36lgTDdrN4R3Kjm+yVNR3yK1FjMwMvlashr5G1dO+Q2p7aKFc0iWRXn1Qi'
        b'i9ZuVgF79YiU1tSQbLaacm/Xi4MOhdRpGLpljstNVpie9SAXjaUkKKAHJ4yPakmIScF19qeE5FIHfHxdn4SkDAvemZlIbF79AuKkwK0ZcJo3Ly4rMTNJxVWFq/GDNegk'
        b'zQuOroTik2BEXpqowdfnxmUlkaTDbQm56Dp+sSAJnxC4sXOUFcVZNNHpUnwE3bfpcgpHZ+E9y1XhXCjaJ+rQHnyAxncm4Y34rrfTIi43KV6fVOCuVa/kpvWTwtTobh/0'
        b'Ms0kjvaX5NjicFNNHgvGQ208voQOaR109f0S3oLOFKIWvHsebsF75uXw3IJSdR6Pr6WgdbOptyN0BL6PLsQCTllKTkT7ebQO3dTR19EmfCoStVTYMpg/Q48uKLg+gDA6'
        b'NwGdYVnOd6DWAltcFn7+aWI+K9fw+PyUiCJzRm6A0vY6PBB0My+yZXL1jLlBM//wr0/Swgti793b3joof9gAfdMMZWbkz4LHPrslyTQxcd0nv/p5y5SK1usDwiYNrUz9'
        b'4C+HY5Imqyuvz2h6pdD+Rm06r9ry/tndg5T9n6t/0PL94IunfjZp2I/7n1p5Zda5XfUHY8YO2vfxkswTuk/6HhvjCkyKWV77YUhgTmpGYeO1Q6+3vfOzZ29PtE775AfT'
        b'zh+r/ehW1fqz91pUH3/7uvblLzV/HDbopxvfD//58lD9h+Pfu1X39F9/UHZuWknY7/z2PZ1tyBszbtpza/6l7cNiBg+j+yXQLTto7ifc7Mcpknh0PhCdpQsFC4qRMyEJ'
        b'bx2WhJuSM3CLyAXNFlXoHAtSyKP5ctdrUXMyPMNzimQeXZ2STe+NRE34GL6BjyRk5WTDrVgeHR6FT9uJKJw1inhQchLQ3vgcP06lENRhauoaCcbnnoms0VNc4J1+PHpR'
        b'xEftZAMNPohPluJ7aH1gfA/OmxtoC3WCVMHZjQSdNp6mqQISAlvsSCi+Iq4UtSz9Q/uqpfgKPuXOAMGjI/OXMtfM81GT0fnyBPlFRS6PLlX409hZmDTopX4kchO3ZSbq'
        b'UFNyUgZ9X6NR4Bv9cu0kcHueugyvD9N3zC/UkswmWDx+WYk3hKMmus5kw/djaStXp+uJG7CJ5wIlAR9MRNuLw7Is0c+F6POSeE6o59MaLHScxqK9AegG3unZEk13beIX'
        b'8To72bqHz+KLaCeJENHn6PU5OtyUqHdnXohHrUp0Ea/DN2gbF5Wno6ZA3JyLzieqOMVMHt1bhG8/QRjkf7LxMZIxQIMvzxfc8k92HD3HhZC4T+YyIvGhETQGlGyQZO6k'
        b'EBY1Kl8lkaN0m2SMrOJ0CyTXvZGKbnH8T+I+efYq1Rx2wuG7Tu6ijT67IXtFBuoiSmPPUTI0cwvN+gW6AO+VuUWgX9ToPVKmEjSBn3SnCaQzUSbvr2GqH1FXQLIQ6eTR'
        b'vmSFgGgHNlmh7yp45JWDThpFJ/2he32hqxgr6qqbGIn88xHXbulZQ8Q6WTZZSRSPrpgZyyrZanyVqarGupKu8pQ7rEwC2+jXVB4tyjvbS756qlesot1orQDjxP1kr+sk'
        b'1Z6FEkYd7nUSt8pEFB2Tzduyf4TE734DuprFHm2bEcxFc5+FqvNLgqSyFLb9IiR5EDeBq+ynyC+JSYmSk3E8P+cmtwIo5tLKOXUfptT409C5VfiAzgZsPThY4HjcyuHz'
        b'+IVsRxbVDIBZndF30h/K0Hn3qoxbqhblL0iavwAEPFlj6QgUAG60anDYpMl4nbl4+jHedgrqfGHvmzktk0NQStjMip+GxDZMiuhTd+4vRfO311bMnRRs3rulb/6Kmlf4'
        b'CdE3zJ/977b/rdzUNyI0Kmr1iB+295s8NPWHYbu2lZ5orH2npWX3gM1z9o85H9G6tqFq0OqBI83vFf/gxmR0wPXhtbn5n9+wran9ycGv4iM+/vlXL/9hSWFB2+Y/RkyM'
        b'2qc6tH3NhVc1f5tz686fvvj6yJtiyM+aD/3tk7SMiRfDvrF+3OcXnwSu2Dzh5bUztCEsMO8+6DYXE5Li1uItnqX92FS2i30TvgAqjZduAVx3f+h80YJ3S1SKoQMKdKKr'
        b'fBiL1rtFBGpbQIXUtMJi3JyAz9EERjR9UT90lwYh4Ju4aWBnNo82z/Bw+gfoKEVVhU7jRiLkjPiELOdwG77MUD35DDqbkIf2jvJk3whEVwSQI3vQaYpA/AIS6EESHQWH'
        b'kVRHPHqgyGfRA5fwhoFMRqIdKllM4l2YrbEEohvorI+UxAcKPYIS7cItdqKVps9EhxOoCIUG+HSIgK+gW6gVbeUNyWp0LBU3U7klofsVRImcjG9qQTarlgqDJyCWPSAK'
        b'9MEXvRddbBPlNZd6fIIKXEUwup6QmIPJ4gpN3z5VEYp2iVZ0d3Z3W+IfV6z5yTYCFWRTvAXZOCbCVHQzQ9B3ghDwb0FQ/1sQw/5PUBCxFUDzT4Z4YiBC+FUhsuSQK/UN'
        b'elvjK716yfghsGc7gh3Ih3TioC5bVIfMWse5vBM3dYbdxQIn/IZa4KRaYoHDL/GVDZB4uwDn4kY+Ch6QBJ+Sey/5Q2GE+aFihG5MOTSHYOcKMlTXGGQb2eYSjaU25lLp'
        b'xlp3hRk8S9/M9ZgluPeBC9Bxwqp+bi9Kp+e6+Ac9a84kSVMj/b7CRsE6u4Gn7eGWidbppF3W+Ab+KGkH186v4auj7KLEN9AyebJcZF5DOFeQbzTQNgq5D0d5xGiV2QZo'
        b'lFVSATQC+D9xSFFbmZzA2NEu6GuuqrWYy8x2A+t0m7mmmo6Vy79oZS1zQ9FOkX1OLiWV1i41c+LWWHuIAw4x1FpNIMVMBvr8XMEd+EiygwHlhQiEIlUw7qsi3R3n80a3'
        b'g0+7jc5D4vaEriCOz6V8uRDFfD/QAeGstjjSyETWVOtqz6CG+GKpNhgAptVgWELwo/qQtzuM3euZDMMpJm5ClLGgw+BHyAx63Qt0J3ryM5Ct/Aa6J8kNOcQDmd7yUdDI'
        b'ucINOJrS/1GgBIlvF9bQTmjgl7GYHwDPTzktWI9wsosQzuk8PNwNGiqDwWI3GEoFWYJzMDqrgj14kHtPjIaHGIUpT1uPE1AneoBsMhjKe4Js6gayhwZ03lNnqHtSLBNq'
        b'NAwHYAtEN6XXyRn1C7LBILj0QLSAkqnOYFgquGPXKbEGAOP0Qow80QUxj28wiHYJARrkjn1iAHrogmpoZq0XCXTAqe6uAx7V9Qr3NOCn9trzFTCuth56vuI/GXMl9QGS'
        b'MZ/a+5iDEWJY3hNkUzezzRPcTrrWPes7drd0MOyuc5t4wQyG1d3ObXbPp50+6uzwbtvZjyzkcJQNCxsFd5v5hNNix3SjjNWd+uOw52on9GD+GyXJYFjrESPUpPTiAfR2'
        b't1PAi9IIgu18h+P7ek9dT1gdrXFj96yuK7TH6I7ozt1Bpz2fZCUZ7q3Xum+2zVFqMGzpsdn0ds/NDqGIBHY0nG6Bu9Fbs2mNzd03uys0kfPiM8Tm9vCZEDtHeQqUIzo3'
        b'nC6HiK6Q3Bp7JkhUE9lkZJI66IF2Rk97ZgyGKgcQY6sgr2VwVG3z6RX6wGMTA0sJZH25t16hNe7uvle6QvMhhinevaLpShYDPf00sFM/yYnMCJEkdxBJD/0SaDDYrQ6T'
        b'ZK43GPZ14skC9E64B2HPY/85zgM8OA/oDmcmz5IfjXQQiDRLTY2VonOkG6z7erDueO4/RzvKg3ZUd2gzbWDEI7H2o3mDDIaT3SDsRYQ1nXmEwhvXfM5XKHfgaifYkvVt'
        b'wKvjfImwRlgjyjiLGwn2Ijsr9yYVlwr6CECD1k557KucN6N1myaE0bqUyytrLCYS9VtlNFdLpp600wCDgdVpMFwU3PnTaYuDBLLlO+C7VX08rXY/2bNGSvRAJpkC6WDI'
        b'rNCtcXQnnWgStgqD4Va36h+99TjwAjrgVT4KXm2NzWC42y08eqtneBEUnp3B4j08r5Iteu73GY+eoINxZTDc7xY6vfXYcp8stVov9QLJXA0KzCvdQqK3/h9B8qcT2AgV'
        b'vuoFK8x7dpOb1o1cN65Wn/lNZskyzhpmB8uVRoLwkigpiJDpB4isIbODWIJCo9DO5os8S+gQKHM/J5U+HEpXgM3VFZramuVsDXl0CoukcNTW1pAEQA+FFJ2LHw0zptE9'
        b'ZC51ncNYbTevMnlPJpcf1FRhtoNNbFpR6zb/enRAQE9Q4AbD6x3sQ01TjoZ494j8EJNNpFu0yZ0iB61L5fpslho7yS1GouxcIb7uayiXl5vK7OZ6loUaWK7FaLMbmIPW'
        b'pTA4rBbrPlLbQXIg8Q8sBtFDoy61x+gPpB5RtuZK/erU+LWS5NKM27STw0vkcJIcTpPDGXI4Sw7nyeEiOVwmB6p93SSH2+RwhxyoEL5HDg/I4RVywORA1vGs5LNN1jfJ'
        b'gST5tf6AHN4ihw/cfawN//8nprFTmAjZ7/QWWVMgoRNqUaFUCAre6wf4YkRkDwGLShJPO3iUAEMerRH4AFVIYJCoFtUKtSJExf4GiUFKNf0lV0LU9Mcfrso/NIgRX8X7'
        b'62x4G25hIYy46Wl1tODAe5CzSxCjQv5r+7BTEKM7u2q5guZ6VdO0bzTXK0n+Jqd9o3ldJX9a9qNp4JQ0DZyfnPYtiJaDadmfpoFT0jRwfnLatzBa7kPLgTQNnJKmgfOT'
        b'075F0HIkLQfTNHBKmgbOj4ZEKqVoWu5PyyTV2wBaHkjLYVCOoeVBtExSuw2m5SG0TFK7aWg5lpb70tRvSpr6jZQjaOo3JU39RsqRUB5Jy6NoOQrKcbSspeV+NNGbkiZ6'
        b'I+VoKCfSchIt94eyjpaTaXkAlFNoeTQtD4TyGFpOpeUYKI+l5adoeRCUx9HyeFpm4ZMkGJKET5IwSK5YQwMgueJYGvrIFQ+VplMRmuYKJVtmijq2oH58qfPaknu3ptdD'
        b'cg66To+RQAwaFVJmrCaMsdQkx7zZzXRlxx27QZOduaPhSPgGW0Ix+S72yEtMvuEaxIry2i9bQtiwke36kWrKHMQq8NTsU1uN1V2h2c4ca+xV94pNelpO0Uy5hpIeQvV8'
        b'CpnlcuyJUVNK3YBQHVto897Pm8hAutsqh2ParSbSIT71GW00+pMgRyNC6qEmo8WicRA1y7KSCB6fjcI+L/uIXGL1EZZD9oLbSnki/6xhRAb25xqFZf7WaLcctFP/Zzu/'
        b'RpRA5hnYUUGPSnpU0aMfParp0Z8eA0ADJX8DaSmIHoPpMUQS4RhKz8PosQ89htNjX3qMoMdIeoyix370GE2P/elxAD0OpMcYehxEj4PpcQhIb9GgkXg4xtIrQxuEo8Pa'
        b'uZncM0tA61WsUTYojsIcbee38zbgPQ2KftwaRfUAelVFrlqHS34g5Uc0KIhbcY3CPhKkvmKjAM9PsY+S1A0K5v+1x5HrDcqNIs/V/b4RWrc0pJGnzy2xazcABtQ49c+1'
        b'vk20hKfYBOgyXXqfEFRMzHbxBpdgMDxUGkbYRtgejuhcSaWRxEt1hFwx52u8K6gAxL+5Sg5pVLE1R5aPVDSYJZfS4DDZrSSDDNvi4AplOc09W9ysM4mAIl+CtRKXuZWs'
        b'3LCsJsVUPfDdGQkqIFtchhprHVZQbU0AgqoGftQjbze6VIYqWwUFvYzsFlQaTOwP3TsY7H6Nfg8MXiqrJAujNBGu0e6wgX5iNRFXudFC0iBVl9cAxrRfzeXmMhrYDCoJ'
        b'4xme28Yqe0eDXBEGS02Z0eK7V5+kIa4ky7k2wI/OWaiG/mXpiV0xhk5dDgotzEf5WSWcV9lcAYCk1W4j4dpUuXL5wbiQMXGFpLlHho2En81kl2/YbCYrqZDe0KpYqAHx'
        b'RLhUy5aTD6V75Txo4B6dcYGO7i+JMlhMlcEwGkzROZGWusuVHn4E9jeMuoqC6FeGyTGcX9WvU488UfZn2UvyGcf1HCsaDkYQC2GN7gzKE8s6pYiGK1Qv69iVmchyKNhr'
        b'5F2sJKBQAtZtLl8JDNmLUT5haKs1vTdkI93IPhzpm2OLrO1X1dg7ts7SPKNPsH/XmtEb3GgPXN/UWl3BksSmjweVGl/63qAO9G2td1qtTmDlLKOP39peM2oN9sDVdpNR'
        b'678ATQe4sDfQsR7QP0/TsNyyNkepvEGDhq0TeHKEjZy4qVe8qPLEKqKLlUTXqYXXiJ5C89p0kwpKpynsuFZuNhGAsuIAtcMDHfE3Hllg08TL/RSfCKdmO/3rTrwVT5cl'
        b'41n2q/gnoI9FvXVWnKezxnZNcdIDfabNWJCWDIdZj0mlchT8573hkeDBY4rPBnuSRcRU6rvVvjM+6QWzZibPnDWj6In22lu/6A0fnQefAjr6XiJcjspyh+J3ChfSaWbS'
        b'dCcsOMqy3LjSJu8y11SbKozEIH/8sQMsv+wNyzEeLOPdpO4OefJCWJbUmrjC+QuKnyBnHkD/fW/Qn/JAH0WZe03NMqLhsr3yoPjW1taQjVCgIjnY7vonAv2H3kBP8IAO'
        b'LfLsa3l8EDJF/rE3EJN9OVgVzFljhcmLDGsrV9pI2JsmPy0zF+a45TGBy2tyf+oN+FTfru0Aaqmp8IWpidMXzJr9ZDPxq95Ap3lAs5C/ainJXpMEfzoEtyZu1uPDZPk1'
        b'rH/uDeZMD8xB3eZv0MTlPD5AeXp/3RvAOR6AsSyuEVTEarIHRJ4qLJ9G/ryC/CeQxAD0m96AZnmAhlMeRzVmeTvL40OBvvxbb1ByOnhCZ85F9GwSdkPO42bk5ekzc+cU'
        b'zVr4uHxTnph/7w16vgf6nzpD99X+dZrZwCPmmACfaqoX2jymeHf54IF5LcicXUSyuidq5sxPT9TkF2TmpOXmFaUlakgb9LMWaRNpGM9sQjKVcp091TYzLwdmEKtudlpO'
        b'ZvYidl44b4Z3saggLbcwLb0oM48+CxCoe2C52UbCW2stRpK8iuX4eBLa/EdvXTjf04VDvZg6M5UYYRrpZDTaoBefZNr/pTeoizxQx3UeOGbR6TRpHZvQMnNn58EQzMyd'
        b'Qzg9IaUnav9fe8NkiQeTfkVU2jMzEoZQIrRT85hzReY73/YGytDB4+X8K3RXIwNk6nALedsiT9Lj/+wNeKkv0+tgdiTeW0N8Wd0IFXeYCV0XmS8DtOXSWLhoumZIg6xq'
        b'Y8g52/dK1kHgV7ERjgbyvJLGzinJmwZ6PKqCo187z3sN08PJBSwmmni0PDoOU7k6fGvdq2Q6rdr6O9LMZeTQKb0z9UmQxAXWKo4utXbkgO60eBRIvtwmV2kS3SuQYOdG'
        b'0y8vkajMVQM7G5xe7/Q8UsS7JvHy0m8RA9ndMJH1ihqxY+Gqi3nrCZHpcR9ktDxG1hCy1tvOkbXdCrZ0VskS4P6btFVBnBTdxsCpZQeGgXyZTI4GIW6B7pBhD/bc7ggv'
        b'ZFgWXk8vUNeXGxsls0N6CMmzmKoNhuWdsOnGyUCfy9UO6279ijo/6IqTK6STI2uah3I6iMbiphdXsK8fSyW7sfxkyU2/3utSyS4sJfNgKagDS0H8VzS9iCvIx3mlkn1X'
        b'CuqHCunkpQr0dlKpZO+WusO5xRxLIb7OK+twXiYfK/nkpDWOlzvxsbKyWT+Cw4+IZ4gscKlFRWD4mCdMj+HXU9qM/zLtRk9/VY+btiMoQC2qlQ4SKoXaUfuSwPrg2iBt'
        b'Ft6WkJuto1n520ROmBZfqUSX0Mth3WZlJP9sKzjvJS1J2MTRDxaKksLzwUKlfK6iHy9k536Sn6SGZ9VOoZxnHyos9mfZOIoDaMZbgWTlgKuB9IlQKQzOg6Q+Ujg8ESz1'
        b'pewxwtW3E71nm8FMV3ghqvDmAmRLI+HEBhrHYeDJ6rRBqCB5CETJo1spqFHg8vd8OxhOq2oko4V8OW5oZ8cmgWjwXkixucM8knm6fOuuRO2uozN7I6u+60RPPJX8KbuY'
        b'buA82bZ36nboy/ci+7Z4PIbdQnuiz8XJaunk3uA53fCepMYpvdXY2GONnkEnkRLueJAOdj+C1Pp0T1UTbrHVS+L0NBjdM/regjSgQR1QfSUtZU8tXlA7S1UZKmXojyFV'
        b'Nz1aqm5/dBtlydp5Z4An4CaX64iksoXbAbQc60+jvpaJtrFwTqOm6Dk5UywTrVPsSrZyBmXVUT8SDMh77X9I8tZ8q0iOgNKOtAujOmE6yvdxqcbEdsOzPQU0G4x7Ex4V'
        b'E6AXHeLkCcq+Mz+VnE0jBxpuQkYIZFptLdjb7s0EgV4g6KM9xGuJRknaJXptIVDLcdlkM0s3Epp2M7zTMxUFyFTkCSX2GtNOFDQKXjzkNab9uwPWvVbmic+MoPOF8fIG'
        b'bia3kZeJV8ztogN7XiIbHQgffSaI7PAgSs0OoY5EeFcyeStYE0jvNrBzMi9cvL0zRYbC4agox1urAMCqpO7wt9fYjRZgTmRZyjYVTgjPr6mqnarlXaLNUdWtwqSkbx15'
        b'VN/Qp3K1IZ2VpY7IHEo0HfTSoVdQNWMmL4+CdY5H1+gl4ckkeGiNKHc6SGQV+wShWiQxKSTmxEHc+6tm4cbAerwe7+kipPFV3JSo47mZ+Lxf9jB8v4ugjpL/2lp5H0EN'
        b'w0t/xEPKYpHEnJCIE/KxQSmAiGHyWUEphIhdqc+hkGLyRWEliORwqS+IYSXdbKsm6a+c4c7+5X5ShBQJ11UmP5rqin2F2E+KJudSf2kAjUzxkwbScgwtB0B5EC0PpuVA'
        b'KA+hZQ0tB0E5lpaH0nIwlIfR8nBaDoHyCFoeScuhDKNyURolxQEuYSa/cs4UtpFr5YvD4F44YK+V4uFOH2gJLyVIiXAeTs+TJB2c95Umysm9SFKRjs8yhkA7w2hL+zoj'
        b'nJHOKGc/Z3R5JE2m5V8csdtvd5Q0poWXJhEo0BsiTalFEoxFkk8YSuPg3mQKZ7w0gV6PklLpTJ7iCiI06I6VcPH5Lj5Pq3QJc2a4hMxZLmFWIfwtcgnpGS5xxpxclzhT'
        b'r3eJc2bku8TMQjjLKIBDesZsl5ibB2f52fBIQR4cCmeRG8V6az1lSXMy87UhLmHGHJcwU2/VE+4mZELdGQUuITvTJeTmuYT8bJdQAH8LZ1nz6APpxfDAPEAm02fau5On'
        b'05AI+RsFLF+XwpM6XdFr6nRmmXfzwdSuqb4VuQ6ylo5OFIcRDdWOm/J0uCWHZCftyElKEoIm6DLxtlDcmoCbshMzc+ZmwLTIIvs9yXdTp+INoega2ohvm7d+/bRoo585'
        b'6f/NlyV9pn5R8sanceFxxgyjpdxSmmhc8r0PXrm2fTT9jEXleL/AXwzRijSZ5OQRaEsgOp2YwTZMohPokMD1wXdEdB6drKV5FBrwbXwSk09mAWR0Et8jSQcOCivwXbSX'
        b'fk0gBe0Ebdrz1ebx5NSPfbUZ30fN7u2Lj16uFtx82rN9kv1MIJGMqyK8icr3S8jKjuVyq5IwqG4/9wociz4x0vOYB/IVwqxIYz3bItnPuz7fB+gWgzK111ATkL6fzVRT'
        b'KgqQPzfOph7L7tPx2Ux1oz9Qlj9QltpDWf6UstRr/Re6w8g7URYTJp0pKyaXpqcNR9u1enciQqCkpCQdyXFLk8SS0Z6Xvxxtyqhbhk6JHG6tDcTb8Rm8xUGyDvQbirfr'
        b'rSM9LwPJ5SXNl7dwZ+EWYNBt+gVxuGmBGkhXwaHb6GJgMJBAG91JfmGxin46MGV236A+z0RxDrIDGZ/GZ+ptePtTXlvJr6B1FjLh4hb4c2FARCn1/8g7Z6HJYlALPo5f'
        b'xs3o8GLvLPY+m8r9uEWFfivxndE0fW0abk7QZ+bo0XW8NxG3aHkuMFfAJ4bpHENJfTvwxuUJGWT3Od6VmpKCL+JzaFOJnhuKrovofiVqdowmWJ7Bm9ALCdDwXHQlA+bj'
        b'PK/d63G6pDjcmBxPvpZYo1Xjq+i8he6Sj0EX8dmGYD1uzsxOVnGqfkLIEKYC0Lw4eD/ega6iM/YE0u9J8AC6I4zD7eieg7gi0O1afDSBDUl3wObG0czt06T8uFyyNboF'
        b'bc4QucFoczC6ibbMp6lqcFM52mRLttTjKwqORwc43FaLX6Y5lAfOJTvHPV+QREfQpgW18FxRHAxkc2JizjyWgp9t2+/IXImPiUEghW+hFpr/t3iRVi9/+A5vzYZG9J1T'
        b'Xijiw/ggOkyJJgUdxO0JDEPoNkov7PMAXk0hQAJRq4C2Chy6jh4EPjUeH6UfH4Bh24oOjoJR3zWXKAZcTqHVEctuNOKboA1cXl6Pr6Gm5fiKXcUFD8TnJQEdKAHo5NM1'
        b'wD81Nrgzn3ycIC4rCSgAuCSFVxDnQWoY2gKYo134VgCHdvI0l3IEfoCaEkhf4PYo6KLmZNxWGBcHvLAxOXee5/MEQG1oHTrtz63ErezLnHfQ88sC8Q18zYZv1qGW5dYg'
        b'dD2rDt+A+ZMqok3onMlBNPDnTPgl3Ew+mZKkg+5VwsTcg9Zni+hCMDpC54tfkIJ+DTMl6tP0CWNGcJSmqvD6HPTiVFudUv62JUA6aY5b+LHStgz41pWVP59XkJmLp4cd'
        b'Glzz5/CdE87+7E1xhZD8hv8ff/ve0Ff2cj+LGvW7GdO/+OjbTQcm5/26/0ru6XeGflJQn5f0i/fHXVdnnDP12ScYgw3Tj05vLi3O2p3zh4jQiBN7r/gX+CmLp43pU7ns'
        b'dt0boyqCP5Pm/zmj9f9j7z3AmsryN+B7kxACoYmIFYyd0ItdcVREgVCUYi8gTRClhICoKIhIR0RAsKGCCogFERFBWc9v+ji9O2Wn7NR1naLTnOJ3ShICBHVmd//f93zP'
        b'yiME7r3nnHvqr75vyrs/3Zxz4PC+DV3zluzPSZt4t9xj9j3L774rOFvp+mbc+gnT3d6pNRyxdPG8716Im2PQecm4ooTfs/LceO+mk09NPNEgKLbcl/HL6I3vWS35dqz5'
        b'B5V7Y0d87/STUaHT3SORgQdmLa8M89qx0z23MuPz4jZPY9elEdFx08ev7y6veeG3Ys8lpk8Vq3Jge9TT7h6t4zsTpg1XfL4n6psjddfuHrr1tX/RpcjPTyd9mKlsyVj6'
        b't3c+fa94cMgz2/cnfTjpw2e3v2K3x7Q0bceOkXfPPf3MYaPhO+c7fzrD92npYde15S9ueWpd7OnOHVO2tLpuUVhnfLXG6e+RrcIPl574ZXR4TOEnvj8X7ZQfLp0Z8pV8'
        b'HD0m8dlWME7nnKRnpBXqwsekMbrCkBQuoyrCiEO4oCBvE6WDkqLzAjypj7myQpqC0FEtPAFeAc099J3TDehRii5aueHj8wS6km5mapwCbUq4nGoq5qyShSEoZyiDLToL'
        b'rb6KKbg0NTQQlgZyKDjQWOggvEJaHil0HOURPohSW9pClD0W5VNm0OLB0CWHfNrCcwI8RRtTWAt34cJL0FW4horM0+ByErSpcO3SoYINO+AUw73oxjvAKjjsoEMKCoWs'
        b'l6BmG+zSEk6g+ie0dJ9QBdm08XAIzqG9CrgEzYRTQpDBz7ZIppjXqtUCvAoL8baBGy+aMcmURy2oDq9q+ti+hahOMQ8uUN5OwoIFzbJUosDi4k7CRa90ZZpJsgrazVEh'
        b'KjaXmBrDBfM0vC7hcnoyfoMAkRh1+MMFNSRVsdvOkQ5OUOLvxnPiFTw+DS7DCVrRJCzJnMLtOLLGB53FEkkmv3CSIQV+kq1D51CRIZwPwvtas08AwuegM4FRH4HaROmT'
        b'LGkXjwE8HwinJ379S6gQHwr+WBKaK8DvX7mKSlOjMn0IKIZ6SxgDR8muYO0vMoW9axmueDZqgPMoCw6gIhcy4ww4cbhgLDorZ0N0DF+4jC/hfQ1OLiRbmwEnDRJAJR6Z'
        b'QwwYZC+qTVfTkgWR4xrXtHoVPkPF3Gg4KcK76bkQioaBClKhTerSn8Es3YEOCTQ6B6Kr0ymsV4k/7ipfwVBowD1Ft+YcKwIxbgpZtIJA/yDKJctzI+CwKHkS5DKmqTZ8'
        b'SnTjzbOIEJJqzxezEGEAOgJNtBm20IjyCdWp0zoFFjYUQjwrCwVw2hZ20fGyjt6Ir/o5bkBHfbHswEmmC9YvgEv0XR03j6LX8AWUT162g1Xhi+emvZ0B7szTYtrcdVCN'
        b'DuNbAx1RgQvd4FEDOuSCO380tBsYhM5iza1Z6kxbokVusUTnIAcKhHhO7FalEvx+fB5l4x0eL5BekjsqQHtd1FoswUNTa7IO+MgpGWeMauEq1KYS215wKOFfxU+jLrS3'
        b'XwkEq8VfLub8OUN0EXd2LaXJxZtL99p+NLkaitwWOKdLkwvVi+iMRdkWWPagMwXRZxYNx0+Jse4shO4FcFS/TP6fJ3+lVgYq26f0l+09jXkJ4XsViPhhBBUV/7TmhwlM'
        b'CFwK5YU14S0EFvi6MT8C/03ASR5IhJY0SdBEYCzE8rlArBPYStx2Yp3fqM15SB+5nRmbaQMbjdXpVprIZxExxaWQGZMyneiL0siIVG0Qs1gZuSF6U3RfEBbDx+iORklK'
        b'HK8uNIUc4qwQWlEC+ZXa1uN53T5rH0AreaEXiaz+t/szjGWG69TvNSBcq9ag3ruyP2VJpya+zQ+zet/X+qztKGWKJl2DtU6mxkbpBYP/+LG76neVrlPHWq17CCHP79qG'
        b'OOqLzopT9rTtr1KCUg/2QPUT5Y7VbxtKw7JIUNZfpshlDgcSRa9KTYyJGbBWobZWysmK73bCt8tI4kBPgBhpCQ20/tPNoLG1soeNv1jbAHsaMBEXo46Q2ETiUnCvR28m'
        b'mS9Rf63TcReYrNNZzQM2w0jbDBq+RYI1YgmMnDbS8S+9efHDBtxEW+WkgfGQe1esUy/dXLXQgZPxNy3UPDMwcCQbJ5Pfaryd0xoYeGpg4HbwAxkYNIbwvtByA5POutKa'
        b'Y/g/Rzn7sYrXA1VI/vViLeodBKKUKTckqhKiKPtsdAqFKZdFxEaQ0BG9ZWmpn7wSoiNISJVsAU2tIQOrxtalEYlqxHF1MFKcfmxeNRh5eHhoiio6PJxx40bL7Dcmbk5N'
        b'jCR8ufayhLj1KRG4cBJ0pkHxHZClMLXfKie4++pYBIZlyILZMnRixB6Nyh4evjAiQYlb2B9FkOaEcX3+8f2GWxgYd6cxnlcS2fjrX5Ys9f1n+LPrJTEf3cRiWCHf/oK/'
        b'nGdctwVoD9TqChtqUWO5EAsbqNiGGer4vm4lUUxsNIVNu0v9Sjv7fNluHd/rwFFGJqyj/dvjJyEF6NDYMtdRD39tJn4nC5HaSd7nHM3ivjfROUlV5CyZgPW1432MsrDP'
        b'Qfe1oAq1YuGuIGgK1GFdSo6Vh/0KCtSK9ZN2U1d0Ouk/TH87oGlZ60zTNS0Tg4yhZ2pvcdFlDpQSq0yBv72fI2oKZYYm8ocgf2LTQmdQgXQGOuUS1yV9Xqgkm1LnwhX/'
        b'DHe2vLvn6/Cb6+2s7SP8qTX5dviX4ZtjbocXxvpF4JmAFZwqqcTSxl0upAoZurpp8ICSKpVSIWs8E1Td0WEKl4tKlQlSe1SHlVe9kL5rsSJAJlkIIsyKfecYOoBOUZE2'
        b'afVjmZrxnFOq55y1vjk3hvg2H2Pe4UKYCCnSoQIYmIFQAwG2XTs1d+KpOWLAqfmlrumZMnHCfnR4zmNOzflp2pnpEEhmZstI09lrXeUCal9CB9dFKIbAaTppReY8Og3n'
        b'RexKZ+hWxROomz4k8uBRayC6FHc2919Ceq5Me/HLjbE+kf54KsR/3BC9IXZDbEKsX2RgRGAE//3wjcPih4Us/8LV4JXjHkmnhNxTDkbhZkKNp1TXDj/g2Bhpe5oqDHoH'
        b'yNrE2EK01Vr/ALEhETxkIHSO3hw8AuYDjsBdC10xe4D6/oMU7JzGHf3oVY635T+urBIoie17clBWoOM/8aK8uX5DjAndmgd/L3hy6Gd4aya7TXKG8YDK6mWs3eq4XbXK'
        b'qrNpv1HrE9BBh0fvnm3Xz09CIzt6tugBmMZJqWMGHIyPzR7miekfO/LvCCaacI3HOB9FgaFxy+1DREryZ3iqRBFhEvPU38imKLLj5dW/9Qh7/c4+6lkf+Ohz6KfYsZCV'
        b'gY86Ut74ATvwQ5OHKY16Ak3/3R7UO5X7C5REwrh2hVMS89lHb2x3iPgSSxir//a886Wy4zVu1dkeQm7cfeHdUVb4fCHWIBneBluhyJFYeFCumWguj9pgX3gqiWeAHFS2'
        b'sWeyz4Nreowz/QwzV4ZSM5Qj3kfPOyjs4Cqx0DqJOQl0CojrCPYPMIATH7oOnPtr5izSdsABJOVNGnAA33voAPZE8XL9PJKjNJ0ew1GPJAkCMKEqgiYMQJA3iAolvYIB'
        b'8gzyhlNP5Yi8kXmjYkZpvZXSR3or+409CY2x6jf2joHUPYhyyMGu9qBBnYI60RLmMyeaDH+bigWrY9KUTXAZ2qDNnDhcqCPIAtUL4KppEhV54ORO1E7dQD54AINQsx5f'
        b'UJqD1kUl5mDPFilqs0BZcjE9+wwtoUIJl6MRQYmBMg4Vc+gwa+BxyAqGVhVcQsfE+FotcSnuZijZcHUNlEvh8qCNxFnThu8VQDbzelZCJ+xWpvLoKh5YyOfQHlSBylSk'
        b'D5JdoUSq3JCEuwLOc6ga2hYz2onjnuioMn0hnMAvD+UcKkRdkEU9RYFrDdWe1UuxzwqXcfT+BXHbiXfMDRWSkuo4VAXXoJa5BctQ62D8PpnomOZ9/OCSigT/jJ+NKmhP'
        b'9ekguJCagt/x4sgQHwdiiqfdhMpQtVEmKkfXGC/HCahz9oAyD1cRh7otedwZkAWnZlLqcQuUDbt0aT5QLrrmo4GTWbJ4GVR6+IUYcmFQLYa2kC20L+AMdKTOhFLikHPj'
        b'3FAXKmR/r/KBDlQlARJ35sK5wAmThJ8fPHiwxEztMpv67pLnbD041Tx8szOuOUehrQnyfRyJuFvi4hdmBwW4CSF2cti7zMeXSEnFAVQ4CiavJxWLN5uu8VWo5tIqk8eS'
        b'6Avd+8h0IjKVS5C6l6gnOnGn2hdNJtIZ1GlCHNrLVetwIZnK9ab4gX2mKMtVYgBZYXBUDKWhpgstR0hmB6NOdA2Ownnv2C1GMUOTjaFLjGonpEtQoVGQCbqAt5t6V7i2'
        b'TT4a8mc5w0ExOuAlR61zJkPNMDxNyvGMDCWj0J4CzQaQDdmmnJtEiC6EoYsroVKMCiAPcoegSnu0G8+Evag0dGTcDtQAWSPRtfixI1E7KsZjcjlmG+wWutnhhpSMhpYF'
        b'gwNWo5N086BTLX/iSH6ygJNcMPtY8YVfBKciIWLLI+GiPsbbHncpIb2FGvOAAKpQnIN2aSQ6gqpokaMn+3BlxM2vilme5yXmVAH4j7PtniDvUGPEOSpkJvjj0rUb8URr'
        b'xlvwcd4N7YKTszzwcOwPx1t8MxwMmwR1K3GTs4aEol3RKD8WjsEVww2oyyJjK5ylMxsVbyGnQ/9W+jj5GVgOIYEzqFGOGqF6npz4Vc8Y4VbC9VA5TzeadcHQQvmGy9FV'
        b'fGJAqS8+FYjXfqhE5AqdBpTAF0/K3ahIoZfBtx99bzgqpwy+hXKTuMUqFREKoWGihPmcB3Y4o+qdGp8zarPHrRvCVvTlRUTe5zkBKuVNorwy0HXVArJBztjk4IP7rTiA'
        b'TX4XP1+nYDvUuAoVOfqE9Qsq8MEKYBJZ/4uDnZYKuIxQ84wt61TE9T5t8jLm6fddog75YIrFUh//IPqWzkskaXB5iY9fQKCjU2AYozzGWwgqXcZiDJYl0a0ZioMHoZPW'
        b'IXTwz5oLqBbsKg62W7l2Az5KadTGClS4SOGMz+aTTszvI4ELApS/0oQ2JQyK0ZmQIHkAQ7YPW9Y/jGUInA/j8JRvQll4ZMuheLUM67FXUL3PGNTtM8YDnRdxeNJmW6Ia'
        b'dIlTEQ9PFLo8FO+YreZGErhoDq2pySqes1LGQ5cwaBq6wLa4c9DiFEK2KiGHylfy0MxBsy1qpDRKtqGoWiF3oqp0oGMilPmG2fXNMFgjk6Bd29EJGgEywxKuE6aiPVAX'
        b'CiWEqcjAnkcHh6EOustFJcZK08x4jocqrJdZwxlZPD093FAz3g1aSYRBqyG32E0AZ3mnDTPkg2jEBOyDUjco8s9Iwk9O56B0Glymtfmjyo2oJlPR42uTrhTAuWDYT7s8'
        b'GF0co/EQo4ZYIVzn0SF8aBTTtsxyRfUKjYs1brgLOmxDO0SGLqH9LI7BgEOnoEZky6MTE5LV1NE5E+C0SBMggppEnImFcMi01TQNYxzUoDN4tsupXk9Q/mGvYjzeyUhR'
        b'E1GWQUzgVBoqgRd4PerCVSyboQEfk0C1AFXCbqhjoTQH0XE7dBRVO6jXiwFnEis0Hw/N7Lw7gIqnMi4flD2F0hy44tOWDugVqMWyQ5FTIPFQTorlxGsEQ8ZAB11VmbBb'
        b'BEXUlRtnJJrKo8at6AA7wM8uRfvIOsd9VTOavHMdOgy76FMmplhpLqLXIlEFpdION2IxK1W+9poW4rc9hA4GkWVtwI1B+w2MUJWCnpT4GG2dgbeAgiCsqKMCl949BHlr'
        b'WWcHomxDKPOHK/Q9xOhqhoNzGuzydZTjTclohgCdxFvVobjXLsbwykwsMuxcM807pHPz4HlWR2qOZG75l8qy+61AQbLtbO8j9qPnzsvOslyyxnvDsosn2l5YIV9vcHXh'
        b'xX+Uj33qjvniu8PtDKas+5th/Sc338lGR7e97PnF+zWzWme/tMDJtzw+VL48Nn5HwNFBGYtnr9tSn3H4q30N/5jku0O+75cVc3ftejl+rJ/BHw9uejy/pWPZ6tZzsNAq'
        b'ava4j5WbrHI77K2frrPLe2L7qqffu3Lx5V2f+H1+4mdx14t/WNdeqPWubF71RlxUo9xtxNr0hW+7TSipd555/32PHRPkz6q+k35tU/fNGo/p0Tanv/3nk1ut0sNv33q+'
        b'qvUZ+TfKB8Fh8U5F0jvJX3fNjgpJ+mmUQ+b558NrUjbs8jv32W829p6rakpmXDC+sE65UvzGulMeAb+7u847MvnEnaknRPD0K+1OQ/956gXZ269kZr/9iuqrFekjZtwT'
        b'b/j6FbOLq+xmPoh/YvHIxPik26/s/nHZ8//62bpSuMy37PePo1r2500V7Hj2uR9vfpqQfrbw7oumm074R2TemPXu0ZIbX76aM+TCLzMqzJ0uv/rSets3MmfG11uN8rpr'
        b'Obg4o/3iffP32955c+RBFDH3GYe24ljhM9XTF94Y97SnS2Re26inR73t5f/F0eErUne0Dnu14L1/8V3Bvz7taqT64UjgVzevmwe6nT1mEpB/f7r5naaP7g3elnnJ82PR'
        b'L4mdVa/eTvqn240HOyZk5Jca3ruyr9J5XPpbkzpWbnsqf8G762uvClvuxQ7aahtjnuXz4yvenZ7vfPXlzcB/SLrlv07M+r7yhs069Knx+Y+CP7H69PY7C953cwp8/yf3'
        b'k6fvJbzpsOmz+qqJaNvmQz/eOrQz2iDmJjzf6pMZbzHNz/j1y6sHr5FsQ/dv7k77euIOh5WjHwhaagx+H1Yon0AVqRGZUOAdqw6D0A2BqAtNJZpSGCoN1/BaJSvnTYJd'
        b'lA0MGmcqtZsPnBvtAvUyGvKQvgWdkiqwfHWxh9lDHTYTi67QKp0MoRofjLUoj8n3BpwEtQnS8C55jYW+5KJ2KLGBK333RVzmaUpmshKvvouanRHqoYRtjfb2NGoD6kc5'
        b'oQuDWXSPTmgP6oZqykoiRPkTHWhojwGcDaOsJKh+FVVYTdejSw72Keuc5VCIDxCjFXjRhsE+RrtWhq5DpwOhwCtw5G1QDV7ipQIne1THeOCrzH1HztYlkiEkMps5xiFT'
        b'OxW/VhGNs9sbROTV4WgvE1nF3GiFCI4GoXraAlt8KrU4sPpTzXAVzQKP9ZDLYjzOoJI0FswDzXHqeJ5GfC7SiMgqVANnlKhEkmwKF5UkAo/F1kDz3F7hNdAmRte9UAEL'
        b'AzqMmlCHQ28r7RRXS18hOua6jcVZ1C5IV2hsw0F00KFgySDIE6JiODmBRbrsQQdQ10R8PBGOexcnSlpoyJkHCTegkkg67EuDZg7zcAhyxLpKEb2IRTkBtAPWJumg2kLt'
        b'Ewrn5ZN7iRd4yFvphBu+KI0dF9C6mh4XTqia1Xw0FS71ivaCtpEsKDoBtdCSjbCcWKwJjEHl41hszHW4QklthgalToYs/Va33gEeR+IpWQ6UZsApsmL6hRbB9VGidE/U'
        b'SqNd/NCe6Zpwl1mom0S89I52gYbFtGNi8Mf81QvxmPtpSOzMIUuYiEtnQUat6MJYKN+OJWXcb7QTpJsFcGj2FjoplqAcfOqy0w1dxyc6Od7mowNsxuxFZ7HGp5YGxm6g'
        b'sgDKHsUmdBeUDY2z6SsMjIE9lJ8O1dqgo32lAdiFzveIA7B3Cp0iqXAA60JFAZFYOtSJLrKGPSJLQ8hOJdL+CNhnPYBtU4bKBjD3ZKekElnHC7rRfoW/L96GgnkxyrX3'
        b'XUwXywYpp3CEijG6/Ho+UCE3+XeCYeSj/osIsn/+W4+93bwPXCY1ZxHson7mLHdigJVQ1hgLylckfiAg/wXiP+h/oYmAZPkQnDmGDmeN7yV3CnjBA5GQoM8RLHMRLya8'
        b'MxSc2Iz9x+WST5b4EwnqsaSEfxYkuAeXYaIm+sM/8RWSPYVLE5iog4bMaECQSEjChYwFEgFBwSVfPai5AlyWgP5kX2JecEdsTfhvTNTlsgxBrSmtT4cw0x+LEmIRPDTj'
        b'y5F8c6UBQtFbekIKehKoevwPQ/7PxlUu0WnhHE0LU/K0jXLUBhpRe+Me/Kv9gPbGd+b3ojN8WCfJeZo/FvgItydxfPIUFvjx3J6aAIF3BXoCBObFpBLKwoiEBAp8qkMA'
        b'jBsXR1oVkdALD5VhZkVFMVDACNnm6PR+hbJwE7vw8MWbUn03x4SHy9YnJEZulDursWs1IQcqZXSMKoH4/TMSVbL0CMajGBVHqA/7kxPrNiJuM70xhqbyqxM3o5Usm5MB'
        b'FcoI5JIsLkr5+CyFBIFgpsyXuv7xPFTGEXxYXA8JA4iQRaqUqYmbWLHaV/ONCg+XE8SaAaMlcP9o+oN8jNssS5vmTLiv5+NuTCedmbohIlXb2p6ADL0lqt+NgtbSiCIW'
        b'9oALIBC2vbpIkxcbm5KoSqJIdnpLxK+eGhepSohIYYEdarp6BqyglNmR7HRH3AW4Wop7kpGEf41OjXSW00EYILCDdGhqtGZc1ONOA74296WjVI9+VCLNyk0icMf6yuw1'
        b'AI+gc+Q5fXSOxoFMi23DynCRNtFkEzo5VGC2BtqZnZyonvN9UVXvrITk2FHapARfVKQi6K1B6EyiAeRiVZaaD2USIbFRXk12hYoRtj6DJyRnwvlgLFqe9UIVq+b7pqIz'
        b'cBxdkHgGOtrAYTgOhxegztFbUZOF60opNe+8OZjZ9uZO2mT/PBYcVVQ8PZqAhQGiV4cQAt69y9xkRMrF570hNzZehOXOUrhKM4BOZTB77t8UG00WhsclH8oVKkmC39oz'
        b'5hOev2aa42rl/fGvR0t+GS7zisqenMAPMX3RqSyuzKtm8vGMhIjEEeOv1gU9M3msNHflPelV87fKtr7e8FXHrPtnfhPm/fbkt3de/KxJtmf10MOu9a86P7H7za9fvzLN'
        b'5KeOgN1fvX9w65OlWzp/kBZ2jBNfemH0njkja6dtk0uZELs3gkjXvXUYdNgMqzG5qJjKjyFzoVERhCpRnjoQH7UHULFkGZbDW3vkkvXJj+OFahnOgnZLEoOVxJDqZKex'
        b'Jg2CMqEFuoYuYMF6FxXBlm5GRepsm7SZGmVnNqqhqoht0kptbPtYFY1ur8PyErm0egFWkIp80CmVJrgdHYfdLKvgCHQM1wT1RyYSNSDSi7WoGeVYSrF4elDRT/+CPMij'
        b'kikWCQkHdD8JVoqO0Ph4dBjtZ/zN5VjNOqobs1062KOXDGuOKtSutkdGchiRDDy6VKncYq9PbtnJTafSCsHSf4C/C4lUQqSRPh59bVG9+RZdeh/m/UgiBeyOnkO1AP9a'
        b'Rw5Vmb5DNYv7u+XAUQXaNpBwTXzGrMOHTC+IAk2W6kCBfsJ84UNzVDUn6s8iPSdqSPRmNXBpb7R0lZKdsNF0j8Mbsvd8X68QHQT0gY6l6PVxkcp1kQlxuBRGoKuBeooh'
        b'0I2RG5zpHc7e5LsXvW0gYHWdUtX9MpOGBzpq4wMJ0K8ymjYzMSWK/AFv+Ho3ZDVQ/IBtcF4Y5h9Owd5USQmJEVGat9d0iN5CCZqoFryNnBXqiFmlKi6VwbVrG6X/mHhk'
        b'q7y8QsMd/+qjYX/5Ud/Ff/XRectX/uVaFyz464/O/6uPLvd2/+uPeoTLBhCmHuPhyQNEaPrGMP4YJtpERznK7NXT375XmGfvOFQaoqZfFhkounRhSgTFzO6Zw38mkHQZ'
        b'kV7ZrpDm4ezaa7XQAFiGVMuWE64wLS7ir/XU/NAwPU3oIdgmewxrB1tucVGPELhEnA4brFbgGsz4sz9KU3vcJ8a6xHtO5ajnJRMdmqWU4iNiJhYNjnGoBu2Ppt6CNeNQ'
        b'I7S6uroacAI4gep9OXzOta+n3gJ7VA3ZDoEyOOJMfHdVvALOOTOH/2k4ChcdAueiDj+s26Jd/HToGMLcfeecodshcOd4YqNA+fxsuIROyUW0sqAwyKVuLLhowAnhLKoY'
        b'wXuu30rlxITYJHzpQiq04zMear2gkh8D1egMdfEsTDdXusO5YfiQ4xM51G4FWbQd9nDeXQmXzVNI67sD4BRvj9qnqgYRoXTB4nC4rvHCb0K5amdkxnIlkS25FegQjS4I'
        b'QM1yAXUJoX0TsUTT07zdcAQ3DzeeXe2cY9XTQC+USxt4AnWwDtlnh3I1LVmJDpKWeG+jl6zRMWglrUfdmuZbw0W5kEnHHSsW9lQ5EfJxjVACXfTJxcoVPTWirEGkxjVW'
        b'dDzjUFuYNM0ID74Q9kOXEe+SaktfcIQXOiE1JegtQtiDjjnyTxiiahYkeSIuk3jmpGY8J7SDGhP+CeUSFUEdTNsKJxVEyA2hsbXEv7sM8jn8cuXbsThZDLtRF6pAh0Px'
        b'LxXQBfVYHDoMFajL0gAq1xuYwvE1+GcA7pLi2bLBWBi0NEcNcFkWV7JimkBJIDbvZSjCXvEMfNLVwuCjmuSph24nWo8fP9M+8IbTa0lZrxo/9Wyud0uuFz/f3cZgQu7r'
        b'yZIF3gEv8tMNhrg8Z92Z4vHH5xmOs1K8TB3kTzw3o83K+znrP8aWFVbGFnyypn7hG8s/PSIriVk++EXV/aoJgzuem7l5xoXuN8cGXHhZmGgwcd/rl+reWuDnXRY+s/G5'
        b'zL0hv7+Uedx+SeaPHqkxygeFUcM7Pj0oPlT3q9khm3cEP/KH9n5+x3DNJ/dcmnIfzEvseDlk5b9C3vaKj/4s97fR2zNdk02j180782nn8QOvvPjdv15x+PK5hvTTK39I'
        b'vNOZffnzYttf+J0rQjLumu/Zu6bb9Xu5FbP27oCz1H4PWahQx4afgI5Tm2wA1ECbNv11K6qiFnwzdIZaJqVwCOU5KJzsB+3UBCKbOAoN4dhiag50CEYViqCFcEWTVHsw'
        b'hJoDE+bZO7AsTBGqRRfQbh5yRquJ1cOsaHa9Jmc1yHEGj1qC3ZkhtF2Izqll9I1QrRHSl0AjM8Ce3mHnQIz6vqhkLZZ8JVAkQNlYyK6grRkxK0kp3bIG2ohfuIiDhgXz'
        b'WR5sJ5xcgIqStrtNIUAKeXgVTvCjbbHCc7QcX4FO5RQxvoQn3b7FqJOK/RuhEW9TRUnxqGMKKbAAS+FrJjHHxt4wuNCTADpvjiYFlEcd9Fl0xQCOKNOgaS7xUaNTHBza'
        b'Bvn00mTjNCUqnoWOoXzSmDIOLhmjg8xxsQ8uwAn8WKuFmQF+7DSHp3kesG6zQcUReIGPhSy8ufLoHAdHoAvtpTqVRyRe/Glj4Gwyqa2ag2LzSdRplO7orExbvDAZ14Sq'
        b'OChcuIYazvGSOgUlWGGaBZV9dSasMO2BygGyHB8SgyxSYkGYKhTr9SsU4USBIMZHko8oeCDGioWImkWZSVNA1QvNlwnNQjQWaMyN2v/4CXzvA8GDrYN6hxbj2gM1uCY0'
        b'OdFEV5BOKeylkdAYQvw2JVotpFCbQ1iMP914iCpyo1eAc/9WYDWMKB80dypQPrQPeNQt0bog38Bb0nVeYcHB3oFevt4hDHdTCyp1S5oUEbdZk1xIshxvGetk31FbpTbT'
        b'UicpMqc3+BTFoiK2Sqpb0bdi3TPi/0um9BQfovgJ1diREkMLoYBTf/H9Pv0uFpsZDJtLDOgiwV8ExRRZWJgIzAh1m4h7MDVDwlvZSFgUE2pC19GRPpkCPJfuMWKRKM4e'
        b'qvpF5Zqofyrt+d5MbgRJi6FoHRapcbTYZ4KmZYS/yGeCqkUwtdjfez5bEFjLqMH0s1XUEO1n66ih+PMw+nl41IiokVGjDksJR1yeOIaPsomy3S0hsJoVhhV8lLTCpEJS'
        b'YUm+okaXGEa55RGULjFWeMdHTaCoU4aUW23Sbi7KLkpOuOPIcxXSCkGMAD81GP+3qLCMY79Z4tIsK4wqjGNEUfZRDrg8d4IARkrMM8ozzbPMs4qRUNwsUrIRDYkV0xDZ'
        b'QTHiKJco190SAuMp4lZKaYi4xy1Lsmi8KJ8ExVyLiU65795L5Ox/g5oaTfem+85Yfp0Zp0ycqUyNoj/dXV3d3WcSMXjmFmXUTLKQnF1d3fB/LGB7yIW3RIFBwQG3RD6+'
        b'i3xuicKCFy1u5G8JFnjj70akynVBgf4rGkUpxFpwy4CqnbeMGPBuHP5oEIOVZ+WfqdaNVCtKqSSrr4p8O0DWs8g3MISBMf7Jsmbgza13WSnHaYEhC5bOuz9/Q2pq0kwX'
        b'l/T0dGdl3BYnohCkkLRTp0h1+p5zZOIml6holz4tdMZqg6u7M65PLugpv1FAwb9Swgm+Ie4g/yCvef7rsJ5wfyJptNd8X9pC/HNxRAbZ/oKJ1ViZigt1dp2Mv+OdkBTW'
        b'yKcE8tToc4i01STEN3CRv/e6+fNCvXwesyg3vFdX9nrl+9P6POiVkqhUzqcKTO8y/BNjA5SxtCQ3UpKgpyTcwEZSlnmf/rg/YuCXuj9Eb+fJpb1KIdMtpVlP2TNSzpG/'
        b'9ilkBi3EI+UsuTZw5W73Hf7Em94yjIqOiVAlpNLup2P5/06yB9N8rkQvpSF70ORNovbgzBZ0Km694BzLAlF2zFVEnPnaJOYjfOKJvPmF71Y9JAvkloSQsqbiGT1wwhP5'
        b'WsRgU3vvJM6aZwfOKcASJOeJPynH6pcBsrineuUVPKyWRkN2ZsfrObgTtKc3mZNfkVaEBvbLRDDW9CmREWgmAqchC2WoaDHG2iwD44dmGWgsmbsM9VgyfVkSb9zWaB17'
        b'JmP9Ya4msgs/xH4ZouHrlSVRDgYqwChn9r/RSdZnpcjsFnjLH34bWWmPvGOGzM5eGUf8VmnTnKfaP0aRbPHK7Lx8Hn2zepGSmx1lj6pn4A1EZucb+qeecHvIE4+7F5Ai'
        b'+jZ6IFOx2tzF7EIsv1rN96ThEhjoSXJgssf6TpuklLjElLjUDIbZa2dPjmHCpEUOYnv91kN7cjyTe8hhaU9MxfbklLOXO/e4Vqc6uzu7zlTfor+YHi+sK71VXWrPn6fS'
        b'P7OiB3oxhgGhfjU9CA+sfyYpKcjDgN1DnRQzeyfo00WmH69BnWA/YJt6QBlmarlk++MuEAwErSNej5+d/MPXKO0fsd5TqykNAoiOSCUTSqkhRdOBsSBu6AGy/InlFZeT'
        b'HpGijhnQ4aKgvSMLiY4m76pK0OFZ01uU17xQ70VBwSvWEdKfoBDvdYTvJYS2UuuvZ+xvA3YS24RY/1B+JjUqimbcNIqb2mas373dY0emvglWQo+Z177PnmI/YIAAHaEk'
        b'tk6VjDuuzxZjz95Oc0vcZv0QBAzgAoukGmrcDRGbZd5hwQPYwzfLQtLjUrdibZIOXOpDGs82xAHWEl4wvqkRCRn0wYF3OPuB56wamYMNSA9gB5n56iHRgncw19QAb5TK'
        b'4h10QL17PdsLeGXAXYuW1M9XgLtHLTcpNdO3T7n6x0RNp9hTL6WxXB+dkLg5lpT0CJs6kUWM+glP5oHU+CuHYnR2zWzYr4BSKBNyAqjj7WAX7FVbwzkoUEc4OPrRPMBI'
        b'YAiyLBEvW4balCPRtR4gUQLXRoMf4BxUo2Ki9aJiaCeokahANMOWM4XdAihC14U0iR6dEoxS6ECJ4uZUa+BN+8FuakA3Awz8BNwUlGMGu9GZTLmAGpyhIAnthrOpWkuw'
        b'Cf8E2o3a1Xl8iagB6kRqA7Ij/wRUwyEVQYZBeyAbDvWgs+oAm2oyXFDXxrAkU9NggrJq5xQYZmcHhVDsAoWOBFGToYU6ESvfgcE87EEnF7I6u9EFdEH5BK8DBBq4nXoy'
        b'PktXo7KmuU29GSDnaMKkADq9wl114EGX+Tj7BUABfnGXYMj3X+IjDEYFJPUNOtDJjAm4ApEU93FhaFzF6fucspZI3ftfmlCiMEZzLRac3lb+y/gV0s3XylfdCBhXnvXs'
        b'+BckN2QVs/aWrR4z6dKiaabfDAnzHDZsd81QwTh040TWoo6twX///j3pjfQ7+55zzr3wTuXo+lC/V9+d7Dsj+IvX4pI+uZjb/e1LN++NX/BqzNWNlhYPNk/+3TNy/KCP'
        b'b++cZpf4raIi/uS9Dpu/bZqw8Ouh39x9ZuWvh66e+nvqyeek60snru2WJ7j88NoyuSm1VBpA7XYHZycfJ4EVnlSoXuCK2lARg7G7iI4tSoUahl9MsJcdSZiGIWcWLHRD'
        b'J6GJmpahDqqmMWtujaonvjzDgkE/njFI7xUqgg5AEQ15RzlOzG57zm2oAk+eag1mIzqBDlND8JLhsBcdce0b4w1dEazoo3CUo5iRpjN7h17IUSm14O4cg+qhiUQP90Xx'
        b'87dloRmHUYNdHzhAdEaigweYFEhLUgyDowS9MRNVUwBHLXpjOmJAfOjCNpNRy3UAJnl0aBUqZD102BbOoephuCKy9i7h6wH8QiixYU/m4qmZp4BcOAyl/rgL1vNu0VDT'
        b'CxXC+N+yvmkx5hYMpEFtt2TWtwciIQtkJTgfIl7yQCwgPwUkOIRSHZsJBPyIATQhNbqaGnBmA6/PkrypF4hbwEOVrzbbRypffwbQjdGS3TJYR1HsBkKbKjHg1HBu+irU'
        b'kio7P4b42xeKjRimQnzmBd8SEcrUWyLCnio31Bc4y8JSSZTqLUM16XZKF68ne91cc5T4c9rsdaY1mqj1RlOGp51nHmP+mDnqQtpXoo8b9GmP86KilL0pojWnpx5bnlbu'
        b'6q+ExshmEqlwZrgWLCRcj9PeUS3FaFGsSFBk/xjSvnSHjO2XKOY9smkq6cVUteT+WDqRWprVEuI+Si1ifFjsWT2stRFKWUxCYgSxFcgoPauaf3KgiJmIzb243vqS3Q7U'
        b'il66gj4u2tToLUwQTtXSt25iAZ0DRGjie+KiiBTX0xU9jHnsHWR2lNadvBqV0sYGL3R2dh4rH0C+ZHEPNNo4gswmHRJnbcmMpZLJvT3X9ZanfaaHdFI9BdQxWb0pKPWW'
        b'YRfsvdCbeGq81wWGBcz3DnaUadQRxtM5YBwXDS8emK81MYmFWz+khC36NLwBiFEfUhz5p1UASQ8/TD/TIqupZ7Xe0jQs3PpUORnuFe/gwHn+/dU2/RHJj6nKabizWFdo'
        b'+YvJhFXPG7IusPYbTSmqw8MDEzeTneIhodpbUntqp+y2pI8iEkh4NNkgtFM3JiVxE+6qqIgBYqoTVMxiFhuXFr1ZM/Px0owi8Tt2kYmblXG4u0hJuOPi6F9xLw/YMFaM'
        b'rp1Brvuaajbn9fHRkalsP9Cv2YQETZ/q6iZj/LLsfUgbHNVYnOr3pYo/WZt4U9RbTowqha41utoZT+yA6h07kWbKQtTqlIbdnUSdZ+BaEhLw4otIYUoVu1n/3qJUJkbG'
        b'0UHQKndJKYmEpJ30Iu5a9WDjhcCmvf7O1OE+lAViNS8iKSkhLpJGFhI9m64n3Sh6/WvHS00S38O1Sg5rmR3+LneUkSNbZhcUFiwng0GObpndfO/AAdahvU5awFS5/WMk'
        b'K2jDtOZpt/o+ZEUPC//spWNK9OqYo5mBfkxmlDZKHpVuxUoklKdQGYgqQ5uUYu63aVj4loX7b/NMZEAq6GwSHFWapkzuYahoQvVqxerqCGhlsU5QxkWRRPMotI/FMnWE'
        b'wjWCwCKi8CvQgppQFZzHOhLVSQVwFVX2UUkJJcRxppQqJtGAfHQEnbeEIjVjAqHVCFVDCiic7Jf6OPqFDayZhi32m0dAWs57D8IqTE4cbfAIcxIphZqNejRTFRxXEUbX'
        b'ZWNJVNLjV4XqQymChpqLxmGJnRZnQi7mZrpawQWVOiwKyhehs1JrmVblRVnQqdrKUf6PPBIYRTB4nPyCiNbLijGAcsg1Rgc3TRiOGo17lM25WEU+jK+dsMSaQ30oOha1'
        b'BBXM34EOol3oDP6qwz/3bNyCytCp+evXosL5KXFLlsSvTZmwGtVs3GDBQannKKz3XDdmVoMSIx8pVu8OweUkE6wBQBfvgpqmqoLxtTkrUJbCHRoGahsUDEcFc9G+9Si3'
        b'V4ty4QRUkM8ksCvcHPJkHGpeMmhYoiXri0o88p1SJ55FlhnxLj6Qr4rmKCFIG65So/7Ll6qhdpJUqlAoS4LdcMXUHMpD1eOsYx0gFgEyQhpgDg0qDcpGDRJajxnkW8NZ'
        b'1OagmkNqOjQt9qF4SOShUPV4Jg5jI4obl2e6yBuyKX/IojFmCl1CohLUvJhOGlykgiKE4Jm030Dphwot8YQrXDgF9gfjeVjIQ3ey6SK4JqE4L1CPGtGpfiVB5WgftUKK'
        b'tdGlvcpEuVJUYTUBTg1Bp9FJ6yEEgiFgEDoZO0LlSUpsDTPohWDko2IvJYDjUIHruTQbj80u3JuFLMAOla/nIC/YJBi1CFWE3G8kXrcdOlYYf1+5n5OzPgoRTZNMdVbL'
        b'cnRFQXFdjqgs0T65RBVGNiK4sFAD6bDEZ9iyv1o4LTnYzwq3OieAzeADcAntU6ahUxt7bDtPDKXhOTTkA+qFxj0MNyMCXXX4bXBH5BHOxLihJm/zypNYx7r+W3zAkmub'
        b'35hr8aHNtms/Hsk8sLp8XLadt5/trkk+Bp6TvMft7not+7aV/C3TSfW+TdtEnUE3xsns7Z8U1s/+TmI34e93ZliWxF6vHf7yzecXBC8ZGX/gRFnllO87LVRBzTXir60W'
        b'B59unv6LX2zT698/Mbbh1KTzhh9MKH+rMKR2uyz20Mapa65e//agx6IXz066PCbFbOpPt/bXOVfWvyz+Ia7zvCjyyrfPR7+YM+1fUPKZ0f0vFG2vrpt8cdfpL78bect8'
        b'Q3TUpl8VF3e4N8zq3DHSc8jsoG9/y4619tzzhXPcH4LRoq4dNpl5pZevdtwT/93g0u1g73sTf0g9857io7rvzr88K/rbD4QHmldnd/04UXbgydl3Cm6PWD3kRNCrpxfW'
        b'ftoS9NzTnx3PMx96bv0Hnvf2H8uT31rT/O5T/xSppgXeNT332fQPTH5Lf3LGz7UfrSv+4KfnI2/uupyTNjM+Y+ffYnP2/DH+1AtvybtvXzzklX35+I4xW2bU+DnnLq81'
        b'vdy6vmuNTUnl+cW+Lw6ZWP/5i3dzheMqb97/lD8v/Mn3nYKXkyfEf5hnuizs/YyXt5u1r6z88HrIU8/stPZq+flOp9yaRj0moEODqHUInUVFOhaiUaidQRt0DkcXeycq'
        b'2aCzFG+hdT0zPpWjPDigCEobp4ltPIaKaNl+CXBRFxEBVaErDBVhPgvjOwIHkgj1V7GuySd1Kk3QDhlPwFh785SgsqWEqgSuQDFjmGhNxPukDmqCEO2hwAmijSzTvh7V'
        b'jeqhRMnRsW9ZQhc1LM2Gc6M0zELM7Ia64XDamjAaLxgVN97Bf54mQJMEZ84NohanDDi+gwDQ+qJmESf2dkwQjEWtkEvNgWtgV4QCbwwnUIuaTQSfPCdYgwrhKOlOZkvz'
        b'R8095jQ4v4pmMC3Dp86lPvY0KFgNHT38Gs2LqEFtOCqHzl6p8PggLLcQDoHsNcxo1gzd0IVHbR6UOhJKN5Ejj67C9dl0ZKdDyQ41mwrKytSxx+ENP5s+j07Afqhilk0s'
        b'6hzGG0a9wBXvEKyhcTTBHRW4oE5hX4giV3RF7ALnPOkwyeC4AZ1CPo6Qh3L8grBEYbZA6LkZZbF69qM2X21SGSpYRbPKmvH+S2fJccjF21ORS4CTHDdjK+r2FMhkcFgu'
        b'eezEZfP/TkjeHg1AYxWRGfUZBXdyc4x5EwHNVBeY8CTH3UIgFkp4SwuSUy56IBaSnHVCT8Gy10neOQnmFKsz0C2EwwTD8E/y35pmtROyCiteYmBGcs4EOkZHkq3+gBgc'
        b'RQIzActAFwu2jtVjguuTXh34qCT0HltaSnfvfLXHHwLd3PFuPQnkenLHy4hpk5iY9Zo2s7jv7XSNm4/xogMH9RB/BbX5sTgRLkasDe8RPg7I/P3wfvpEcPRmrMoqH2XY'
        b'o1YEteZC9NYIpWx5gP8j1BOSNmHbTz1xDKScb/HLSSqlDuVjHxC5omV2fZNEN0EXgVU5azpklTeF1YLTcAXl6HLaNUGVzpkPu9AFDSpWk1BJPEJo33i14LBVRKHQPBan'
        b'kwupznjTdUZdoWn4px9Jwxy/1mCaaCPNjvBabUGKFy1EXRxvi/d3U9hHwbjwdoZadL14cGkNbwcXoJvqWKtihJyI+3meIRduYjg+RO29O4hOxFDoSA7rWEdXoioOda+a'
        b'R5NMRiXDAZJiMtybJJmEYG2FZlp0C6BaapQiHEy0skaslZmjUvpert7oooPcHh8JogwbqOMhGxHgS9LmtUZwRYHPlE1L5YEGnNhaYLKDZXRAwyLoGL46BEpEJJuaQ3vT'
        b'8duQlk3IgEtqwDeys3WSbmoWGjM/XxmWiY9oHHnoKFzAms1e3Ay6g59DRT462TaV0yP5MVCGStSKx/jAnpyUEWi3Le+JDrrQRJyV49FRKWVQFHKSxbz9RlBjlTXF+/W4'
        b'FHGnlOHq8rHyQI6EuOCxBEquIgxKoJJAyWHRtl0SxOPt90AM7XiBcSk3in9lgtg1PFBp58Q03n2Z47gFnGyKhAsXlHPb2R/95/hyZZxsKRcebnzBegzXjwVZu/hknJoF'
        b'2RovN+4Yt52P4qL4XMFw7riGD5mQcn9FHACETmZeVIp/3OboRjUjsigB/9KX0plY9deIdUiRqXfWZOFOGrbM/JBGGnEYymmuBB88dQZ0QAEqmAG5aXMXxiT7puyYCaWb'
        b'UbYNt93dArWMhaP03cbHmXDDuKTJ3OJwx1qndPbC61cO5Ry5d7wEsvDV6zaOYCnz6ByWv5tlWDfsDwooDBqDLjM1v3ISapdq1Ue81E7wLvjUy6HzatwiIGn3yaZYQrJa'
        b'PI2fBTnQRatUOZIMsvxFYll4QpRsFScXML7Da6NnaidUxxY8wE0xamB2d3RBnY1khDrcsGTS5cBsEPXL1kArfsiQE06cBLW8J56X+XKelrd6ENqlDMSSId4UTnICKS+z'
        b'GflvDWcMHs4URHZ8IN+e4rl+nNxkAM/2GkBS+OjFpP1w2VyAX2CtBT89xp3+PcEZ5Vuh81KisUAz1uXkk+kKWemLaqDVBC4bwpVMvPb246uxkEe3BNgHB8OlHLdBwS3h'
        b'lqxADXR97IQzUCO1s3dAl3ygxZ/nJH6ClcvhGN2VbLDsdhxaXfzQnjnQji8aoBweqpaiM3HLM4aLlAtxY4e52UeHKfZahVldbz/6+8E7e7L32O4ZPuzpiL9NG2c+6Jm3'
        b'GxrqSneNG5tTuOyNg1GbQwLy3dpXv1JnbTRxSGSx25Oh/8pP/hgNUUSu/nbkbwa7DTYC+uZw0+bTEcmdL/1y/fzLHao7M9rXT/px68X3uuwqbj/3gvuPgpqVzz8fNd74'
        b'vT0fPGPzTtW++9N/vZzi8c7TTQXPLrWNOLN2d352XWXyvRnLnacv+2XfUEXY1889u9fp2LMZ3sOG/zHqixXbw16q//49QWG53PuztqWOr1kunTF4eOSTCz97Z5VFQWfK'
        b'pKZqv5XPLQidcrTR1npfeotxfdWS3Qe/CzCtTnz+K8n6N1pGnLKc7GG0cX/Tt0oP970T3Zsb4sfOmhL2Qv2+Kft8PA3Sika4vVk1LDwva1OYKiTyZkBU+quS9VeL7lUt'
        b'fn/PibCGbsHlgClLN132vnrk98+bcreva5r4/fC2xvz9ViuT7qdveG955IPIj8838b8nxisnejz3s93GxPntOZfiK6rH3nWye/oX+WtHvOuTP/Ew/HD3cZu/T0lbnxvw'
        b'8/6G58+ltt+aX/jk18Wb7t0ImfCjDKV+y31x1CzGUvHANNVl7Ir7jpGtCQWp6+7Ij1/esamtMbC+4+aXOy4vuB9+Z97rt451iD8fE2MrbnWKzfIs/2J8WEnqzkyHlxRt'
        b'a9reVtycfTXr7kvv39z1o1vzMy1mrh7TGgpOfoOlhC/nhdfXt85OiFqfN/hCabhnzYNFJY02GZtD4c7hmHt2qdM3/vaS1y+hpUO6fPb+8PuUry+ejjO3P9/+j7ttnXz0'
        b'a91ZNaMPN9msPZn/Qf74RJP34iedWDNO9fP+g+GdlrNzJGH3/shvPPbF2cqddVtvV2/9NiGoybc0eX+Xx9I38g9uVE04If5l9qQAD3Tkwai37i53yVrxUeF1yT8nRF1R'
        b'dD5pO+oDwffunjdsJ43M2BSzY3L12q2fK29ab93+ynulczzfeC/wSvGHaTNPN7Tnzcx4u8nwR8t3P+pe3Fm01nZR8eg7/wwdOUR5r2RX940Z37y5+Ldl6wd1Fdp0Wzt+'
        b'/828KT8ceSosfeaDb9+dNbvybvg6w7XmH/qsDlB+O/GHKb9s9/sh3Oj07fimN1a9P/JK5NWQastps+fGHnVI+nxz3taPlv/d5cfv0gZtKji1u9YjP62z2nLZeY+pCusA'
        b'3zumAQVnzntcrXU8WP7+yIOWyx74hqCbniHlXzieevLN9i1+P75S4dqa7Bd47/Tumo4TQc/Nqdmy/e41jy2H9hu0m3xu90r6V6JnXT78tSJu/NqfPZt/utAw9MNnZkL6'
        b'a5MftGcniuN3Pcibu+wNf7fs2IAcx9dFyiF/GJ7y3fGJ6ltvnyeigmKu7Jtw6h/oB+nOjyY+8Pnlo5ciMoudF3flBK3vPPB21p2N5yvfSw36NTfzj+sjE8zaDtXfuvGr'
        b'VeZX/1Q8Pe+Db29u9Pr5wkWnN9beax9tG9xa8PcZJ378IdbmyNd5iuY/TG66r6p9/cWcLUfmmBV9+OGp9Nsr7ilOj/G+PWL74JOuJyc/+6TRkrUPzN/7YMHpN+bLN1Lq'
        b'EsiOQYVSe8LEUeilh7pkEzpHNSgDDzhEtdihfE/4CDoPx5gO3+IK7VrizAjo0qp6sdDC9NJqXPguBT4EtZEZcJQzdxXGQhGqY5h6u7CEWNcrDGQGnGOq61F0iaFv1G7C'
        b'Oj67JRJqe9TXHt210oKVtjvDQYeokgQtaZkqsyCfKX7nlsUR7EIsQRY48gy6EF2GWqpTxqE6KFfq5h/NkJlCt3CuswUNS9kwc7XSGT/olBIoJwd9KzEOzkX78bsJuclw'
        b'RhyyJoVq62NHoCKiRJugA7QY8TqB/aqtVPvHrTq/TOFvLx46jhOs4adh0WAf1f4FqGIn1v5d4NpyLFeTpu0VTNi8lEbcTEGtWC92tPOBKmjrwXiDk1tY4uZ+G7gihXwn'
        b'aFmBDkKxQsgZwiVBkM0SioYCnVtRKbuMr0ErPmNQPeSbonwsFxihBlo9FMugUo0pK5rqjrp51IiOmDJdevd4lKcuoG6uky+u3liwbBk0MbCVmig4r7T3hdIkmle6N9CQ'
        b's0AXoAXVCVOF0En7fZoYlSn8HFH3YsqHaQDXBEKohkssYqgTqodDqwIuBklRo50Yzs/kjKCdIMXmOdM3zEAVcUqCBmmEh8ZgzkTOGEoFUJSB9rCRP6tCdaSBRnIszpP3'
        b'h7PojCnqEg7Gck8Ri+c5hsqTtHmxu2NW8pCzA/Yx5JxmLGCT4XRwlhvb2ROzhuUwC7gkhKyh6BqdG1CKxa5sqbMCLsNx1C2HItwLZoJVMsiiyZ5wad0EkZOSJHsQYaHB'
        b'bCa1pwwLsoBWX0p4WUzhLA24QdYrzISoxmgIrXqLKxQ6BCl6OD4JRvBItEuETkXBQVZ1A9oPDUpnX3TeBN9CRDtLM7HwCagazVrfsho6RXBW6ufkn4zO+uAZqpTz3PBQ'
        b'0aJBqJVOSDiGjiZhHaGCXODgOoc6IGsiHdwwqJiv0CBWG3BO6LwZqhDOlqTSoRkPZ6FBF5NxDNrDYBlLUTPLts32Slb62sux9IQqLNBVHpVMQNmsy/ejAxPwssA9W2TA'
        b'8VICtViJuulLLcHj0dhjyBsElSwzGnIms2crUK6pBrFRZIsqXXl0Yghr8sZ41KRjozJdRQEblaiAluyFutE+qR3uhWR/uYD4P/BsOShAnQprWvIUlI27HL/S7IUBTjxn'
        b'5CZA1ajVkK2k81CC2qTOcns7lEdw1fG2FyeIgzOZbCRax8FxBzxGzr4MH9l6lDkqEa4fibIYITC68ASp+RSqSQ4kktxpHmqXQhUtW4GOu0nlsNfImPWHAVTzWE0rRLUM'
        b'o/IAHCV7l8aqNjSaR1eHaFZnbrISz39ikBNCAZ72BNf5tCN78FLsGgWz1osd0AlO6ieA06jQhl08JIYsMjwp/oHOPLcj3dRFKEHHIuleNGt6MuSMoRsCB1fw3mgDBeyp'
        b'duiwwTpFCgmKE6DrYQn8SJQDlXTAVQFwUiegLsSQR4d8t9NLfnj8mphU3wJnqFQfDfWs646jo0N1QwZTwmnQ4H6891KttALPtDOspS48HHPnjOcKUOOoIEa31YouuSgJ'
        b'YipbpXgy1qJO2nIrwnR7wGwS3Yue8HHHa6VCCaVyY3TOEa9VvJFfxHcNtxDZo6Y5bJDrkilBe0nAbNRKrxos5aFwEDrEYKWKEiUU1BfyURkzte6dww6PWgImRnw4DnA1'
        b'DVrxMA3i12ayeMEU2LWUXBJbwXmOR0c5vBUWomr24IXpEVjEhwI7vErwydbtgW9YA7vom09H59AF3GI7v3moO91ewBmi/YIZUOZB+23upkEk3DWI2FoK6NTgpOYCYRSB'
        b'ICZdHpk5R4st7ofKKbz4nCFs3z+Iu6gJchRKelzhrVW9OQ5DZ0RuFtGs36/g4SJb51BvqpoYoEN4zsLV4XT7ssFty1JvjKSnoGkVXkxteEoYP8E2lpZ4gnZLcE7dDDnB'
        b'Ut4J7YND6jBVuAaFSjzcRlCQjn88QTB9cRWDYb8Q1U6T0DloKB7N4MpFtvPG4lmN99lDbA7uRuVuxEKLzqMuaqX1FMi8UD3dba39x0hVpka4N8dATSQ/bx6nbg06iI4o'
        b'odiJ34ROcwIrfpwQddF+tI4dzd7DN5lcJqzel0yhUTgh05G+aRwqgCo1GccZkQ6WO14WqZM4SmV2He9ZBC7MBQoDHOW+AXjLxk+g2nFyvEdNny1GJ2zT2QzrEBMubGqd'
        b'ppbp4VHENg0t8ymdsmBiGgVB1gCpo6OERq43wCzZ9sLgnMQlSMjOyAKHUCm9ySmZ7raD4BKqGy/E+8D5YHbHqY2oqRdlNR78a4S2Wg57GIJDA3Sg83g20DW2Gs9RY28B'
        b'atqAahhpNexC+eQq2cqr3KGNR6XT0HG2HRd7bWMPkm3Efp3pFKHRRiilYtF26FgIR3f2w8jtwcfdww4qlOerfQdazSC8QHPhmhCLI5Xz6KSZj07jN8UTesQgBkbfC4h+'
        b'L5ymc2MN1ECWlJ6FQryUq8l+2AD7VtOLgUEBUih0IjOzhk53CSdYkoiu0MUdvzwW7+5+PH7u0iS8wx6FLHSZrZZq2BNEXtHYLwBa0XHCMIAftkK7hXgjOGtEZ6sfVM/H'
        b'1Z2VyjmOH4G3ZXRgPuv8VjgqVQZCiwuWH+g+bRGP9qFmISrc6cv2gE68+vBacnR2JptATYQXwSDuWELnswyddpfiVbDNhxPIeVt0QMowls/CodF4VIqUeH+HAiP6WmwJ'
        b'Q5loJmQF0Gm/FQtQjVIsE59BpeTdxLaCwZEb6PLeKsJLipDbBELJECd7Mqnx6q2K2MHaVA7tU5Qu9nBhYaKPnOw8XQKfDOhiC7AJ1QdDq1NgUDyzS2Ty+PRud1CTpM+f'
        b'DkUaEvXBuKFapGN0BuXSuhNQjkzp7KeS4/VvgIoFnLEAC7moy4P2mBXqkjIJ2tHX3I5sbPjozTGFDuGMCJ7OOU/Uvkk3NjttJgH/m0YHIghVShTOAWLIRlc5QQY/Gy84'
        b'OsCL4BicV5CI7R0uNGYbnwcHaHPmYJnnADXKoTpfXy2ACW8vH/TfgbYVP+I6g6pgKbXiFGrap56fpcQMpt/zs5Ozl1B0YYZWbMxbUkgOAsxhRfECxQS3mIaJS9SIxeSz'
        b'Nb5qJRhB6MofCITW/IgHAskIXnZXYG7BWzwQCYz/EIgIwrEZP14wnh+BP426L/hDYErQiE3wE5a/CcTk83iB+IEdb/a7AD9vwdvyFn8IXhDPMqYYyBTNmGAa8xb8sN8F'
        b'4lH4J6lNxI/C34f9IjCyxHWR3/FfTYfhthAwErsHuCyDh9SNr47C95JyGTqyBJdhhdsjwSWa/SiWSu4JnjJRaIBLGAm7DH+fSGrmh/0hIK39XfCr2ErCbx2ux6HDel6H'
        b'j/VRA6eTqvwMHqpRxKJIkMIHcCllcZ9b6zqVBm4Drphmx7fzJBM5MFAuwt9ohHmjSR8kk5R4jiZih3j5eAd4h1DsEpo4zaBM4rX4I6SFKcQVxRxyVv8nCCOztB1UTuay'
        b'gdqdKRGIxGpQ699Ehv/BTzfF0wS8mblEg1WCpzTHbMkPrDw12CPD6FVj/Fkk1Fy13ckZU+fUBMhP0Zjxo1J0DfkCbvZKMRQq4FS/dHtj9U+l8cMxSIRREvVnI53Pxviz'
        b'NMqEfjbFn83UfzfX+azGIzlspMUasYoaooM1ItTBGrEuMYyaqMUaGRk1Sos1QvBJuKjRUbI/gTUypkQcNUmLNGIaYxA1NmqcXowRgmqiizGyQW53y5wC81C26gXR6+NS'
        b'77v0AxjRufpvoItMZ0ns7nLBLZFXULD3LeF89/kp1WTSHyTfDvOPD/MxnWVhuv8pbBD1Q9P/PP6Hpjqa9OlG8D9STrLkHILUkXKKYg8FewcEhXpT3I/xfTA3QhYsCI5O'
        b'7p1q7prSQF74cW5104JjaBpyf9hApWoRM3q3WW7UqwwyDilv6sJuaDon5W3yRm+RSwPV4ZZyidzz3wHLeEyKWgPG7bgAlc8naH7oCFyj2IKneHsl2s/8sYdQ9mBpGoH6'
        b'gvxEOcEIO+IQF3fbSaAk4uvTU2YTtnGfiJsx9p8oIowLVsZ8yX2/a/j0VdyMAtEr73vJmWgTC/tQITFGhaJL2jAgWfgApJ1tmpgQmpM1kGRAvmTklNw6rM/6ekzMDUtD'
        b'DSDxQAcZ+fq2F/bGwFVdJiP5IgHWIPvr/wmwxhjx4wJrRNEWE+QAEtb/n0TV0CyER6BqaBbSI++Y/tioGr3X5kCoGgMt8YfAXOhdrvrv/xOoFn0TuFiuQcRmkiZA8rAG'
        b'yCrSPqYPJ7UfEkavcVajX5BjgiFa4KPCfuAEoEfBTmha8meAJ+Ji/oc58f8fzAnNitMDuUD+PQ7yQ+9F+5jID3oX8P9wH/4C7gP51z8nxyAwlGUjFKK8rfrBBqAcSvzd'
        b'0Vk1vW6PzQ11Q54UTkZDVlzZq9cNlCREyD+ulXCEf/nRhphLC1f+7Z0bb9x498ZbN96/8dqND29cLTuyb0xuS864o4058qKOd47tnpDbWNNS4JY7pjrbw4bLvmo6+d0h'
        b'cgO1padpsTZ2tj4cDgtcbVARtaf4u6XNnqUXEgCKZMxlex0dhP1zxP3T7sdAF+Oza9k4VgGlnk7qfHfUjDqpuQd1rB5PiCGlevgUGlCZJtjz3wl81WbDOz5KyFmomxUv'
        b'1ieD/PmU92GPJft8bftw2efP5r2ndPAaKUxPzvt8Q06d896vJm3C+9gBTrl+Se7ihwfhRhr2WRFSzapYQKQzwz7ymZRIaDFStXxmSOUzCZbPDLXymYTKZ4Y7JDqp65n6'
        b'5LOHp67raon/v8hb7w3mpRZ61Mncm/AxQbJq/5fK/r9Udtn/Utn/l8r+6FR2xwFFowR8AujSlv2pzPaHbBn/l5nt/9V8bKFe2c+S2YBGoWZT6EYF2qRskpHdxEyDKmKA'
        b'R53okj0ULYMGEgkR4gMFQRpMLh8/KKGsYcsIGJaEBswToHsjdFUYrKJ+vTZUDYd7kqxVqI3lWbMca7jEYq5Hou45SsGoHuAwW6hQeeALvjPQabWvWi8aF2rZ6UfQuAQc'
        b'2g+1RtBlsEXlgJ/btsy/J30U8n0cWe4G5AeM89CQqq6bJJk3F1WqiFRiC12WCh2ZFx2ag8VemgvrCKUBjjSWK1hqCCWoMJaKzLaDUIeWoTVs8TKnpctIKq9fgD9qDPVB'
        b'Z30CnJ18A3AJLgK44IsuSt1RUXAIZ4sOmyVMYPQikOtOCHwvQ6e7hjIDXV+qInk88sCd2sInCljxJEE1yT2FZKXSDHERF46KDPELrGGk5SdXWIew+9BhdNZRM0ah7Bkt'
        b'l+yqGEN00h+10Y7fuRydk6aY4f4TWsHFQbwnFBrRSO5BaNdQaIX2dCWJizmjhG7eAQ5AHo2cz15FSOEky4znhvuHixdwcTa/WwuVr+IrvxwPCNvbYopcLbxfTrv9pK9s'
        b'jd+p8NLJjnOTLcvHjflHfeqI10Y5DR6/zdU3fsFzJoe9xy9Q/pT5zQOXGnc/ycJ33xQ1pzxz37q9erxxReuorDfqY778MXNXvNWybN+st37eY2nYsOqzkRMnWgYHmo/N'
        b'v/PsgclrdyU9nTe9w0O154PjL7v+evG5lG+O/L3KJsN044m5G86uO/G9+UuV1co7N65/8sWsb8Z+U1Wp6HZ1ebB16h8Fh16QtueMz8yIVL3+e5Xos7rD9sG/rVPsKd4d'
        b'/Nq8l77ib38l3NXil/TTZbkFy5U8gZrhsMLZad7iXlBgqCOTBlUsIv5Z3TxPGdpFQcbC0RFKGgEXUTZ0KrYO14CMxXLMnX5uLsly0GopCaiSsVdDB6qisQQ2G6ClrzZy'
        b'gPBlkDTMGta68hmoSYcu2AfaKGMw7B/MtJ1TKgMFqkJZWnyvDeHU820XO1YnxRRdltDItMVzaISCKbqcLoUyFxpA2z96doIXC3Uo2r6Zth8qUSOJEoECXIcZdAr9R0Me'
        b'q/7AeB81YbEoLoTQFc+JZBF1h1HRIsV81OLuRxb+eQ7aUVsw9W7PtLLWhjDWe1KrsTKMvuxkf2h18AugW8HBsbThgycJ4ZAxaqRPjhVvnoVqenRHges0VMwCW/ZgzS6P'
        b'ZV0yp9cy1Nwn6xJVbe7PIyf9D2Y7Ln6U0pdEcx6FEsqpKxGLiSeYt1Jz8hKfM/kyE5gJJNr8xa2j+6pN+pMUjR4nSbEnP9FgYI++4cBktnpyEb0fS+e8JtPVOR/1Sv+l'
        b'dMQYuej+mkemI+pT1v5SLiJxTvTPRRzHchHR/uQZfy4XEZU5iNW5iEPSVCSeMD4TjvZkIqIL3HovT2E6apZyY6FZCLvRqfnU3ePyRJxSDU3ZjA8Xkok4n13ZCScH0TRD'
        b'fOn4JJJmiCp30mPg23Ah9+Rk8grhjjeDVnD04FAYopyeNELIjiHQlyWogWYaQWN8BOOqIqGrnMsEOMhOwhwF7FYm81w8XOXwUYsK0B64zrKu8tehBk0yIbq+g4fstDD6'
        b'0CYjVKYYQQJkizW5hJuAEWm5zdpIEwmnxLFUQrQnnqWK1W9BZ3tyCbEo0sJBsxmcoAXyqCxWk/WHGtBV3h6/axfN7YNaZ/xgr+w+SRAcSOXhko037YwXLUu5hgWeAs41'
        b'3Ozv6xQsq+3d8HHclVEFpIfWv7rNgf1x5UQfbotkPM+Fh9v/tHTIv5fbt+HxksGuGuomgy3iaHr7aV5NQ+KIt9Nk3wAodIR9jPjICYtArQTChATuyZfGoMtCdyzAKFA5'
        b'tCql0Mx5Qb55KIdK6Bv95GvKVW+eynGLw01mp6Sy13xbPpRL8lxLkHy2zxlpxKlY/PpoqW4yH5Qt0ubzOUE1S8xsQFdWaFP2oAmd5mehlpm0UKshhlxXxnAKDyTdsoWT'
        b'83SSGKN9M2g0LifAa6RdysvQ4ZX/F0l2Qoluv5KmGKDyWG2SHeSk8NOhcTqdXgpoGkRy7KAGjrE8O+IbpZfMsDjMMu043gvKaKZdpLHKAl8KmQVXiIlqSfAGbkk0FNFF'
        b'loxOYAngFGonuXbaRDvBdBU5IFVwHerx1K5Ax1z8dBLtYPfUONHJFoGyEi9ASeJXqlCFcoi31Z07X9X8enD3tz7PmlosXis4MWjfzwsny46JM+Q+n7Q+Nf3GrAMFnzXF'
        b'fupt03gxvsrRLv7zvcvPOR5wtBvavLz1I8PlVZ+lB/7UZuk09IuXfnkp/aV/zcm8fmf+0FfnnivOdCoe9Wxi9KAJF4MXvuk+9EPzjxQOr48rFtZlVxrdPVYmbutwthrm'
        b'WfaEsUPrxtwz0oC6qom3jaN2T71Z9+GCMU2Stxq8X3Rbf7ch//MFjUMfPDvy8pIpG/dN2xR+qHWsedaqvzmd2SRd/l5DfN11YdGmccMbJ3Qtef0f38xsnln1gcfZP745'
        b'tSayu8Vn9NjrH6YmKOf//GxtfoJry6Yloj8WvjPxnSs3upN3p80ofXDr9nfjl3599evgU5Nu+H+3LHTV9s+tot8ascEhpT3s9Zg33t6c96+5T0c+92nbP755KfhkRccL'
        b'r3V/8Pk7m39c0PbMmHE3r34TeiDNf0Z3UqrLthNb0Zh/FJ99vsM8ZrTHrzea003WG75/sCL3gzOhv8vO+bXeSOh6Nerz52b4nzbbmPt+zoXT4UEeHl42SS/bn/zSI992'
        b'frF7ba7N5Yuh7wq6vghftLrk3ainP7g15Z0/nEpfGvvNxLRG96KbX6y5effE1oj8bXVzXV6zvSmqPT3rxoGbMX9cv53+0/OuRf9cG33H7vaUad0rf7k1zHjje+KKk9bf'
        b'/OPI/Pf+lhCYkvD/EPceYFVd2d/wOecWyqWDgB0LyqWq2HtD6UUUFUFAutIvYFcQVDpSVBAUEZHeFURQkrXTx5hixhjTNYnpZWLipIx+uxyaJZPM/N/5whNk33vO7nvt'
        b'1X5rmb36Sbtlmqu+r+fO8vx7q3JfCobGF/TfDcu9rLNbMlvts7ktCcIHZaGvL7n6m/fnSxxNNmjfS3L2bVBfaz7VK8ly3qt9h13vT53f1xUYiz5Ylrh4XlHv3x7uv1Gl'
        b'arinOlXsd+dBak9K0r5VX0+MzJrmkbE17G+Bn9q+5lxzPfDDO7/MXRU+/driDTtD6r7rixDynpUm7s+aMu25h/ap9/+168ezQQ++fW5+307tr+4F530zJX/m16+Pwn/L'
        b'V98vXD0qOSL3UNKuwzOvXu2b+fWNe6NufNHS+LHyzWn2DbP2RNYGhYX56X4dsMo86eGzS973+/m9ozNcv7h2XetFjd+umET7Hdqo+8Hh1vzAtz6c+rtP1Me3TGPv+JQH'
        b'l1yb9GvdO59992L47LCDOSkbhdnHzte90vpQ+/W7N5QXvF00kjbvj/vX7t5t693Uv1XcNLj3o/l3ZsoDqQsku5DwcMsbX1Vf7vu94n6oPHyOU7haYvQ8y6p75xcYwjb7'
        b'S+B6Z/bKje9G2VXti0rWuqsbvfod22sPNK8++Ni/asf8OTmoqlnyZfTpf34bpLnGaMc7ap+/emhdi/Fdh21fxI7Z9sVVzz5lLHOGPbgXpSr62e7VCx5hvDeLKfXmxS2T'
        b'wPnh4VeS8TE/wvjyDH84RGBrkGE7PGIwVIpIH7gAJ1D9MNya7rQF5pLwaFfm+pqFKvHdyYBmqN2OYM36cWbqUM4QUzWTCQuOjtuSBOIDQLNTaxkW4vBis2EwM23UtzVc'
        b'sjQKshIJP4ga0EFoF6FmymWoxBnfQ5bE8xeLFARrtgDS5dCxC2UzL94yuBjoEkWSN9oNwM20xSDHhlhiKrOCfCylZtoNAsvm89QjfCUmsKWR0EKxZYO4snJ0jjmMdwRC'
        b'u+n0AeyYiCtDXROplCbzg0vDcWXakGG+XiBgwDTmkN8XHTMAKkNn1/NQtw9qGfAgbyPqWYhOsgr6QWXG0EElxx1bwlWWTk47HgGVSRJHoCt00CMWQZELlj/POlsPIspk'
        b'cJ6+vQ3lk3zm/YAyQ6iWi4CylXuYKSwVytGhAUTZ5LEyEVGGr4g++kQwSrcdhijThl5oR4USQ1TEwvUEYJ7HbSpFhA2gwYxRF5XtdgXGEigYakIVDA6GWvSpl/lGaNpB'
        b'AWHQHDMMEybB916ZiNZSm649CFTjqJS3GZ2hjfKQnqhQ2+duo6Ukl2oVj5rhCKphg0r3nfwIVkRX2AmXJSGLRJzbElS+eABqlmA3FGyGTwVd8pn+qH4I1ExHvhS6JUuI'
        b'UzUD4uRBPWRQpBnK2wSXCYpByfBm46RSaNsKDSxJYwE6BVeG4Mp0oBidQB2ShRMZlMo8FLUPxZXpohQnlCqJhc6RDPGUq68cwCKgiiget1yBSpiAnAZV6CJDUUF+NAWW'
        b'+Y6h7QJRLQwI75iT6BEzbk6CPnYyewgrNAgs84YG4oefbsc2/HF9yBmElkGmh5RiyyaYMdJwCdoj+qFl2yBLEJFli6CLdhrP7IgEdJSMawBaFo8FcNJwNJYgypSok4DL'
        b'hiDLqtbTfi9FxZA5FFmmC7kmOyVbsIyQRqueBpWeCmhZb2E7iCxDR41or/eh9gAFVC9S4tUYAi2zwmtGjsp01BE3iCtDPaiPxwOpnc+8/K/AEbVBaNkmOEOgZad1Gc7C'
        b'BrpFaBnUR8sZtAylWzKQSzH0wNFBUIj2rMVxmLdLxa1SCQV3z5kShfVKhi5zQ3V0+TbIpEOwZah+FD8ays0YKauHKsMh4LLdu3goW4rfo9DZE5AzQuRnZyRgbhadnE+n'
        b'1tgTnRoejR7qbCVRWy1oPyWo11jEvMAl1MYz0Atqx3SI5mA4Oh+dEKFl1voiuGwQWKanwZJ2XoTTKHUormySzRBk2QkxOtlkOIzb6EAtcL4feUaxZavwgMmkSDEl6KPg'
        b'Mjz0s+abeTszOCYGo18Ml1VQjY9F4gC0DB1GjCLA+di9FFzGYab/DAWXQboG3RjbnaF1CLZsNcrl4VTiNLZEJ1WobimcpuiyAWgZ7lsNs+pXCqYU8UIS1GZA+0Y3dAH3'
        b'2BS1Sq308TLS85KBZZ5UaPAYxlPvBDaemXgn97kw/VkQFBCXgfKZdEMvdoFiBa3XjWS4TQ7BFBYKBXwIjkfQpR6HD3SdAtPbdhEwgyXVibOhm92QpahreT+uDR/XgzIK'
        b'bINulE8J2Wwoma5Skmtxk5ulxgCwbewCKRQ4zmJntWY5alEg/Aa9YAagbYGonHZwHxT5DSLbUPksXkS2oVodthcvjEXpDNqGF6sHnfDhbdAlfBzJrlmMag0otA3q1jF0'
        b'2xBoG2TgYZDpCZml1g9um0wQ1VVQCk1MwXnGasowPJo2qoMz3hJzTFKLaf+MIGXCOnR2QM3fj0dDh/BesyD9axwPmY/i0VDlSqoUFfFo0IXvC9JezBrIwhOGciGb8BK4'
        b'2xynhw5IEiFFhOuhNNS0n6AiXZQaKEvpZBYrXvkjIVW6WgOO00lRzHGMUrGn6IDVULmwDE5MZauWZYaJwlAEmo63CcqQuAWtZ9S1zmr7gD4WS3UyjupjI6CHbbVyaCGh'
        b'99iMLUYHVvLQgE9qNa1cCzXoq3Cj3gs88L7Kt8I3g95OyR44iw7TytWS8O4oh1NWeDdi1oyoIlCpsBtKkhm8Kw9yHFQkCuxxaMYnHF8OZHg8pz9CsncuKkwkxgIrdHjJ'
        b'MGTe45A2dHypCMxDWYvZUnavTSSoNm28l4cA2yRwFtdBuybFxKZMhLai44E8g7bi7mbSE7w3ImIAQI272c1jot8CBfTVJXB60yB8V9sOCqFdoo5fbqbQu+0e6OQTcHfo'
        b'aIgIvVODRsb3HsF9SKfguyPTh2IIJVC12IduAA/coWLxzIVAziPYO5QXwyhRO3SZDkDvtF14qLVAjPjpbMaLhaV4xSBMjUDv8J6vovR7yzy4MgC+C1PHZCpoHFubRqhw'
        b'IIQIE5tUCr8bAr1DVU4UIhcR4EZQd3BsFgPeXTJk7x6EBpRLkHeYay4bgr6TQBa+28oYM3HMPWwQeRcLh/GVPw5O015tw7xPAcHecQKmTkp+3ChMZymfX4cu7hwE3u2K'
        b'Hwq9m7qWwSIznNAVBdRAqY1tP/IOHV1Cp2M3OoDaBBKmlygjB7F3PugyXdp1eK8XQkoSxd8NoO/wyl+iJ23UaoK8jURHbNyHwO/OjGSQ/yrNERR+ZzOTAvCGoO/OoHpa'
        b'/QZ8Mpr74XccOiBj8LvdcIXVUB6LRYJh+Dtt1B3MSebhHjAOHRo2uAzF30F2OL8K8ykldN422aFDBIHHCShl805+ISbnKZRw7YESVALp+LAzndlApvBudFap87/H1lEI'
        b'FDMy/BGwjv2M7IfX6UmeDqxTHwDWGdAfKa/D6+Gy2e+CXI//i0A6NXUR2Cal4DX1h/j5h/Tnpnz2Y9C6B4KUweiM6Bs6xARC4XimvDEvxbXa8jrkffl/Cal7S2vhcEid'
        b'6dMgdcaPWiT+Wzxdhlq/E+AfmUVSuF+Hoeqe0g3cNsEgJLzbD6mTEEjdS7yoslQa/u+gcK/gRj8mWME93P8RFO6m3ErgdWRPhL1NfQT21v/dQ9NlNIicF1yZ/Jiem+fC'
        b'1CygTxadgNoe85PVEf9VHXgM7eYrLVYr1ig2DBPI72Id8W8j8V9N9m+kJEwSIskVQiwH7FAkMY7WYe3DOof1aCZrLYKaoygzWag8RB6ils6RDN65gq8aLmvSsoKW1XFZ'
        b'i5a1aVkDl3VoWZeWNXFZj5b1aVmBywa0bEjLWrhsRMsjaFkbl41p2YSWdXDZlJZH0rIuLo+i5dG0rIfLY2h5LC3r4/I4Wh5Pywa4bEbLE2jZEJcn0vIkWjY6LAvjRezc'
        b'CPo3yQiu7mtMvSwl1EanfliB50YXz40+nRuLECV+wiREoJp4q1taK5a5rV0pGto+7hQe8a4k7k1Dn2AwuwHnnMRYkhlCxZ6ZNcOa/WtP8yiQv2YOq6zfnqeyNVs2xG9Q'
        b'dIOj2AHR2Q5/mxiaQNM8xCaTpLWJw/3+hqZ8sDYLDQqOMEsIjUsIVYXGDKliiGMi8WgdVsPTPH+GWxWHFdxjicOXU5gZzdaqMtsemhBqpkraEh1JXZgiY4ZAMqhPFf46'
        b'CP+fGJEQOrzx6NDEiNgQ6qWO+xwblRxK7Z9JhNpE7SS+WcNyWpg5RFI3J4tlStFPN2q48xfxkRLdB9lC2Inr0D/j1mYWy5X9jwWZqUKJG1ti6B8tEllDixVKguMIGuIq'
        b'KDrpxSZEhkfGBEURQIEIQMZTQMASjwxUpQoKp1CSUJa7Az/FRm8WEhqHyavKLJZ1nPr7WYjfLSc7LDpWNdztKzg2Opr4I9O994hvobtSuCXZER11Sx4cFJ04a2awZAjZ'
        b'kYmkh5qonPEvESCmdrg/s5aCkhAeExEhTEc0aksy5GncXukuzT2SAaO2lBq1Jfukg0btj3/l/wRkbNgherp32dMcDvHImK/hBjdX0VmOJlGh9Q6uGV4d6lCKj+STvVAt'
        b'QtlWetp5/QMoE53W+QSREhyET3wg7lIgc/pjlQ1UMnTbPSW1TVBISCRzERXbHbbtyAaNTwoVj64qCZ+pAdLxZAjHMEdalrGGnLygpMTY6KDEyGC6UaNDE8KH5KN5Chgk'
        b'AZ/IuNiYEDLD7Dz/cX6ZYXectrjZhjsdjHVXESFv7N7cjjfuWynrE5UvKzuzlTfaU1XvfM1F7lWvzsinTvrUwQ6lQH4YdKAC1EX0h4lYdlBCJ2Qr0TEsOKWqUC1P3oHq'
        b'BZspg7qW2f9bXeAiNMiIE0E2t4/bF5ZAzbrHZpGIxBf3anOBWjfXTOCSiBwk2EIadAhcJOrhFnALIMcu6p8PHz78SZBhactzi9bSQOtuk1COxhZF5WsTWKjlYvtpAieb'
        b'x8MBqSdqQpeVAuUCFhjPV6EsHZS5nRkbsJSpYWnBW8RyM1Cx3MpTQfsHZepBCvwxB1njBDd+DjqyC79P5E+oJS5XQ6vQJL94bmIQap4vm4guQyoLOnxk10wF/QqOQS+W'
        b'wi7xUIcnpRdXRE0eZcFzhvXEyTLeHZ1TYoHfysnFlhg9fFCJ+hg+hoVyLtGETtRBvyrC4g/+Wn2WELMB2pQS2t4is40kd4fVdhtUYD9tlsBp7RW2oS44TW3BqB01ziHf'
        b'Q8UY9oCc09onRKHUEdSvAfqgAc7T5B8nIJc9wXNa+4XoCVCXRHhTOAHnoRELfpksPYjjWkf8tI2X41CzzkpdNRM93CSVt3qlm5gw6YVSvGxQJ5UlDSFPAhXTxiU54Ec0'
        b'RkDLUMeW/nQqKNPVxcVGiF8EJ8fgCc0agbvf7mIEWS4KTSzVZzvvXrrGmwsN05sDVWp049jrkc1wcYva0kDX79wiuCQ/0uUqLO51PqEB4s5p57zOAmU6ohxv4kfpsg61'
        b'9u9fKJ2ppG41Hk4yA3NNLG9Xy2So28Ec6pScw3YjdBIdk4qzjoXdWizDd+jGJfDQDWexbHiRnxIALQw7nYLSdRXqCcn8VjjBYVnCEg6No/6WLv4zUIdWfALvp4tfaeQn'
        b'78HbhsjXSatQmyqOqHzxhFeSrECBcAWamHdMbvBoVTxq1+JRH/4Oi6H8ZKNYvJ9ENUVWoAp14jrHu3EC9PLG6Mx4WqcPasDbljYXHMWaQ9XoIjswfU5QQNZdB3UNW3ZD'
        b'6vSLzkwKHZoSxs3G2WMdXXh0Fo7Q58VJJbI7hyqiFFAbhrKoMy0qM0DnH3vbcy7KsPFhL3GokAtBF9W5xcsiHbjlMtUBzNK99f3X0UULYg2X6b24/f6Nuws+/KVwbqZh'
        b'md4H6eFxO+ZqzNZxuMJHe54omHTDImv8maU92m9HTTbyd3D4+Cv98ZyXl6fXmgnOzvXq1WHJe+Oh6vtdny15+M4v3+xq8vd/y/3qrnX+pgann0mcnvRzdk/Bq2M/qvKr'
        b'0ukuUU7M1Omsm3xAe2yct+Yvms++hF5qKRn1dupHyG/XmJ6l8zd/V73uR0/HyAhLW6necv0zXXlnCnUuF0cV1pRtcp3+qaNaX/cr2nucJq++JHnX/4h19b90C0tP5m/L'
        b'uvlSa3dxYt92XTnv+ty9o0Fa6zZ/5uC18ub0Cf7Ickr07KOh5vrmiS3Fodc7Z1ft/frECC/X6VbBC8P9mwoUU0KbXV+P7v1xY7jsfpOvSfmaayHXjV+4tbHN4trGD79a'
        b'cv7HG9uDGv2Njjcm7Gz0a/tl3Ut3Lk327226+0rRqdKqPV+EX+8LKnYboRg7tfJyRdq2aaHfIcO327Z5jUjcbPxcbsnyOvRGfEZe5B3HiPueauUZ5omnF5xrSC/4xvyt'
        b'Jc4mdz94rmzkD+8ZdDmEbJbW/83np6Zd4Y03ZtzVvLanUhiZ0XP71MX8n0rzylo3bzJ8a1zGS43TNk3obMh7x3LXK2MPnbp/7JzOg0sf194pPWZ442HWj0LblBs/PBf1'
        b'XXbu2+4RFk4b7qvtuxW42Xfv9567R37o7Br8q+5r5Z++mzDvVzuPO0b517dtPLXqhetLT/nevvexUX5H108mHto7y7/lduZZe9wp3Vh2Ympv+IPx+YdkJR7Kbx+EvX4g'
        b'65ex5xu6X4h564PIxe85vrz4Q5tNf78eVFbq/LDoswWJFdvy7kbWe3qPfGHtwRkL32l7qNjeeGLkquiOGW3fma2sznzlzrkJv2l9ovHD9n2SWXv0l30oVy5j/qrViklW'
        b'tm4C540yBajlXVCGOlWAeq7cBtnQQsgIJi4oS+AU0Cug2imoceli6uYrrIA6KydXNc54iQAZ/KI5qJcphAvxzWQl2sihQhDN5CnoLNOu9Y0LgGw7agpFOfs5eaAwEcos'
        b'2HeVu/eTxEV2HjYCHIzj5PsEy0DUnEhcLIkWtxi/SGyrrraQ6UFtxJBhimrsHK0tKZZTjQvA93BTFOpmlpIM25XE5A+ZekOs/pLw8J1U67nKBKiiDOXayFGaByffLEwa'
        b't0WMlRixxcXDxsma6H0VcF6AenfU6xDDdMMFcMqDRslNhLPD3A3s4CLVw/Go1JH5McP5vcOBlX3QzIbasmspUxKihvH9esIxTOUOh9F5OEuidBEl4Xx0UdQTNkEK7bj5'
        b'RtRr5QRNFjxKQ4c5aTiPDoXFU31vOMpHV4i2281GHw9/UI84CpVL401RBq1gqQeqYREiIXU0NePhC7yQWQzOLHfHs+zs5mJDNH3u4uuTY0PRUdkCqN7LwsN2QLanCuU6'
        b'2Sonw0GU5aLjboPpoMCNWyWFahNTljHIHLUQs3j+FHRYQ/xe20FA3RttaFNyqCGe5HbuNtaRY9yGNGY2XYqq4bItU1ieR60rBiKOEX3nYke8EfLMmEm6DyqAROWzxVdT'
        b'kbObtZMbz+lESOYaQiubyyMb4CS+o3lPok9nyl7tWRI16Amj1a9GB0nuBIKvdUHZatt3c3INQcsXVdA9bhphrCJKemgWOMk2fg86k0Qn0DoQVYjmzg3EkHSFH426d7Ht'
        b'n4EqibGRGu8CUDex3/FwCo7OZh1u34MZEWKAIuZQdM6Fk6ETPLqEesVIlVqQ5aqwdbEVrKAcv1uPj5DmJGqmXwJpGgPhMiHL9BGjJhT3h0OuhEsom1kWw1ANC1vJo8ts'
        b'352HSzQbG7FHwkEvapIM9qNd3wRnCKTFg8bJvAA1uPkyHvJQo7kYVRL3O5uMLN9KCPPH33bwmFk6a0lbdUVn8Y3LgsLiyzifBobthCuiCX6Gd38UZxm6vB0P+pLAk2is'
        b'zKOkC86hFGYFRhlQRGKMuuwQbRw78F7A62tjqWvRbws2gGYJyoYSbXbMa9eaU0CCHcp1n0NsanBCgExIHUmnzROaIkUPIx4deMy3H9rRBToANZQ2B3OfxNKAjqKDeHgX'
        b'8LrvcaFt+OFlbSffRqwQJQA5pxMicTCxTSRsgOFEM8jenozOa8cPsmKYjSzVh3w7lOfoZoOf93ZQ14FavC/pjJzHTFebykqTGBq74bSS59T2CjMx8WJjakInVqqsEojZ'
        b'jrDCMk4tVJiBz1MnM2OkoKLReMwEj7MCcj1o6j4ZNwLVS/U1UQoLMgqn4bgCV6/U8MA8HKkC6oVFJLS2GGB6kz+pAhUkECMT3q9qnI67ZOlUK5atq260vsqZ+BaZKnnU'
        b'xevh8TdTo03oVicaKhEdMKRGmyw1trOzd+5hwRJxZUMtNiOgmK1yJjSpsWDKx5yZA00JtNBztnc/nKARPrlQexLgEzr3JJLoa8R2Ro6nB+6IEz6hlELYOaJcCTfJF4rQ'
        b'OdmcCZDHNkoaZMA5lbsy3skBzliKhkC9sRIvOAlptBVocgmisZJl2ixacpo7PRO6mGSmqCh9wcuSwkngIL/LP5RZmern2Vo5YwmnysXG0h0TF91wSdAoT2qs3Y5FwrL+'
        b'ztXjLUw7SJAxmcQHR7lZRsKoQnWikhDtSbPFLYIKoXPYNoF8j9mYJ10AzXL3GE/arG/kSOYthHnecjGUEJy3Yxb+Y6jSREG+TUKZ7uJm1keXJHjTXIICelY1oR4dtGJX'
        b'0JU9NnJOHfUIUDBaYES+ABOcahbqMRCaHjE2ZaNUpfZ/b835P7IKPSmaAMmA+m9sPvu5UE1eTyAwEjk/htcidhaBKtj/JZfpUUsPSX1FrCFyQZ3+pYOf0+HH8VN4C95A'
        b'0COptfDPGPqsHrWWyHlj3hjXaYD/1cE/6vhpTUEuGD/6CU9+dKjVibwrFyEtRvyuEUP1To8ENVDKGJjkNrFk3BkOUNH6r9ZCwqobrH1gPp2IVzf5/N8YZlK47ilDTTNP'
        b'HsefCpIQ9m+DJDSpc2KQhOHNDERImN6vBqd6ZGuz0HBbM0uiELOdNsu+P4DL4wET/nz34v+oe6393ft1NOmHqFM1iwwZ1uKfbqyOv6UeEMyU7U9ts2OgzQkU4UxhvWFm'
        b'9DWC0//LLYfjlpX8Le2AAVVyQOTTm+8caH7KMrOkmMj4pNAnwPn/k9HjPmgF9KsX/6gL3QNdsCQzoErEU0AVlAO6yf+0G+lkxUf90Yr3DrRt6x1LwgbFhMXSkAhmQVti'
        b'kxKHRSH6D9snMWWe2n7f8B03JCrOf9aY4x81BgONjRpsbLnTir/eFg2H4vJHbT3f31YCyc/7589nzh9V+tLAACzWPiGWUX+Yjv9oOHi7atJIAwEE9//ULvxt+ILRYAHs'
        b'0P6nB1WdtZoY+9Q2rw20OVIMLPEfthjRTxq2BEURq0hAbFxozFObfWOg2bmkWfIsU9VHDbX1PRqJ5D/ulc5Ar4KjYlWhT+3WW8O7RR7+r7r134arjHhSuEqee9Q0IXGP'
        b'nG04QaIiLPhF14Mk8KR62EdXOS6vQT2L77ocqWRO/m4qeb/MwyQeFbRjoQe1LHhKvEmLfocZouL/t8zTfi58l9EjV3xUaExAwNOjTZIG3lYXJ+ffchMpXMOwmJNPbOz/'
        b'jwWQuq+NPJ/zO68iH+cnnHFZ5xKkRVdAquQtD+0c3GuPz3Ebx+Y44SD/GO8SELAlNjbqjyaQvH3rL0xgrdYfMWSstWEzSHpL2iTSIbO6Dgbm7A8HxSyv/GHtAaurkCHD'
        b'cyvBcysMzK2Ezq2wT/K0WKxETiRJF+2Hze14d5bJshRS0ElVvGwtUfQzJT90wEVq83pBV8qpm4Zj+TVQ67RBBEdtCcZmkSodY3QwQYM8foa3NRETLL7mj58OfE6On7b+'
        b'VXMUx8JD5IzeQf1wXbBgV05h+iS8RY4L/sOdBL1Y47nGxkfgNi9Vg0rIGJFEUlJBlz+UujgTTT7k9eu/dhHlvoyzDJZBA5yBHJakExWjy6o4PIpzVGNBDBjouG0SEYJN'
        b'sCR1ZIh7LyqAFubiq6XOEJ9XPAyJDkcPjhN9EyfFomVTzDxm/KiWQJ+VMgRlMggwj1IdUQc1wmiFh2Ap1AXqUBYWQ4lUjuXQUC8oXEtnNFZ/NxX2bJykHGqFTg01AfLG'
        b'oj5qolmISlGti5MraiSYDamUh4ppvmwhTkH9XKLJVGIJ0QKd1ZgnQDV0JtDe+EEhljSzbcO0GdKH5o6axnKDpmxAF1G2jTuRGlHefk7uL4wQUGkSkdnnakW5oDwnEl7P'
        b'FWXTCcc/6SzwgNUiGcolyaIf25iK/o25cnBjDt+W/EBssj+zJdMf3ZJkTBqPbUlbd7rrPnGWchmTTMiuc90WPZtj9qYC1TQKV0GH/AhihcBVGmzYzJ2TQxV18HVFl4mP'
        b'L48XvgC66GKZo064SJbLxkRvcLFGowMsle04VEKVitMnM53iFXSEGoHhOB+icrWbBll4k6vzY9fF0+fXoabJBF2AOvezJOFj4SjbSgcD94mwim1xYk50dDSe2rzmQRYq'
        b'EwExeEkLOOk4Hs6go9BGbaXLoQaahmUEdx9H8oG3QS41YTPTXi8eUyO5hiegs+gQ/n0QDilltP4NasphrztDPX4fH+tDdHo0pkCjiE6BQnSc5RO3QyfpGfFCV9YzVIwM'
        b'XRgAxki2QDHKZ9vrrAe0DOBtIB9lE8xNjEuSGenVpd2LrIg27zTKsFVautkqbZzdeG4iHJTNwzs0l9WQD3Wr+vMncQpNqCUglwljGGwfXYADVl5i0hKek6sLJlAFF2kU'
        b'H224yA06X9u6Ppr2ZHEMjTWwea2Euui7MsXxmR2ErOA5J1qUKetl21DmviTChdjONCcGDep53iR/ovO5jHOHVDV0BB3DXSDzvmmcOTOP4lmvpdQlAArozKFaKNk3DDxw'
        b'IZwSl5lQTLul6YjrFGnYZHR4UI0v0jBCTsgUrEe1AYQKERK0HI4wKoSKN/Unf51MEQ5OLnTbVEETVNEDYT0/XvTkR1WclEQ3gctwic14CTpnsM+jnyhQikDSfbGd2og5'
        b'kwKGGYSLYxgx0Z/PWjuAjixC2fOW45f4ucSlvxSV0db2ojxUbEWSufuhQk4ahMmhITpOWwsKI33Pc7SxpmDQoxPgmLAHLgZS/wcLaEOFVhY2kLXd8vF8MxJUQGtfFuI2'
        b'kGOJ04J6w3CJ7qq4JBI8BU5pkaNDaNgK1DiEjA0hYTlQrRToAKZM9YFs1J4Ml2dLOR6vGKqxMaUnFx0TlqgmhqM2OUEkUXf9/TSj7Pp9UIuK5GRCZ3HW2ugivcuW71Vw'
        b'z0kxP6AX6HoxPp6FFtitIeFetyIqoEAttVn67MPv1KWcNJJSK63mUXHsQ7Nl2lxI3CwSmcA6Y+pG9uHv49W5MbZ4UIGB1j/FJT0egIGyhOR/Mq17OH+dvfwePk4rhPPB'
        b'5DReCBkQ4yjHI2ZS5pMf4bhvaSwMD40J3RGXsDhUQySvUhImYBOZznK81S6qHtGOY2pJ45paO+GFwuf1mBk6PiQOA3SiIgnqgCIDFyi019syG9VB3U6oGyFzSMabzWsE'
        b'6pgP9TR2CL6KWtcQ+zs+i0U2tk4UiuLs5Wnj4/joPYQXEDoETXwvn3TGLdRrBcpN6bGPRx0+mKRAvbON0gZlDRqEuDHrpHj75m6MDFp7Rap6AQ857Ne3Qr27Y95dqnfS'
        b'v7DQ4ssrUa/8w+bDa5+WH8wysn1TTf0900jj5FZBq1S+RtpxVJLmYPC5xM9zif4no3P2LK1/a9mXe5aGHT6/5cWDL93/oLf0nZOVt28vznkffSjfMidVw1TfpNj0ldqW'
        b'swWvTL/mlHqqsCTt9MF4L4s56R3Hnwu5x/sXv1KWqne+yv+b3LdszFcveW3H58/vPDnety9tzQGnhhEvlQbXtGQXl/1eI7tVFfML/94XCUldinmKuqLzhbZFX61/4ZUx'
        b'P9W8kfVykPv6jTY6H5m6ntoRPV7nt3Mpsm9yn6+tOXB2cWpbhmWJxyifk+rLfj9vkPaqIjXhxNpJNZtueVefdatF3WqWZgvRhrqPHN1X+m4zUj7Ta7m/86TVzwvrswpj'
        b'n506ZXXCCpfX/MtOvftGx/WeGx1Rd31+fm2074n3zcZ/7rn9pzHPP9Q7Zb/41+CRP71eM2bXizDx3jr7dNVIE9+f99lc+6p0ovFPvT/l/uwYfXj2jc9uCg0tGds3fHPE'
        b'963s95IO/WBwZ+MLf/t6n8fCkO0vfanZUJGxfeM37Zde2anK+S1nd87bpq+p7iddfrZ7fc6cee3PFNgYjnnXN/s54XLT9nu2e9PMrXNPOvoukt4KfznmuZjiRfcj7vt7'
        b'n1oVmfz2D20q38mv7U1eey7vFZsXY76uKVAVJMn/tTT2hKXPL+XXIlb+avBhfCSnHNfzhvnz4998u2Ph1enBi3ae9ZkCb23R3XZ3eZNO3Yp72tucVsg29rk01i2ed39K'
        b'p/Phm6PaXpyz8csjv4+7efcW15711YrSXwun3stvCe9JfG3+Bo/7c7+J2mty7B3fh8WNu299N/GrD766Mid09ITaZ+a/5r4meWz23gt1nYvfjPy5btRrWefi38xUvex9'
        b'4eS1iSeffU4/+dCbM1srK37Qev+N9S+c33Z98r3yD2yi1hz/7uaZL5e0ZjZN6vl47KXUnJOT6h86lMwWOj+88szPo/XivrTcof2gp29M3Gw/78+V86jVa4cClZCbHGql'
        b'6MI+Spl74TzqopaGKGiDVmhA9QoCHtOwwPwzZhT1oUYC5VChoIKoPT4rBxWWStTOwEHQvHC04IOaxcSCanAIU/4OVDtlICEhnGTmRlSEr5Z20Yy6EIpFO+pFYGZMdAqd'
        b'QCXMzu0PR5mZ2xylMKvw8Th0UjSyQo2GaGRF1QqW9Gw96hE5o4XogsgauW9jZqpWqEbn6YDioXuiq51SzmnjB6eg2pEUFTraCi6qElDDsMSEg2ZWNzjHoLDFbugYMaTu'
        b'w2wZs7GO2stMRh260Q6oQzUU9AkHlQzumhmLihQWUBerienjWn6xBTrJIFhn8G3fSGyyOQN5NScE03la6IIuDqS+5DRt9lB4Mp7vLPrm/tDtDOo7DVUTtC++sCMghYHH'
        b'L6M21KxyJYuDiZ8LAcTXj9YS4PR4VE/7Oi4aYbEGlVHIujWxyTcK9s4z6QLMgtoFQ2IInI2mYQQubKcLsNzcaj7kKh5BJ0PXUra0zSidRHc7pBgObUbltFUne8IVkRAA'
        b'OZKYhZx0Hg9tEjjFVrZ0DRQPwVOjDuNIIdIKZTKj5eX5ggplOTmhLheBU8OSTWa8YAl5IhTXeS9psh/TumWGs+C7XodaQ+fDCdRDTIzxzHiriQ6guvUCXHKaTQe7GW8j'
        b'6VIF1MVRM6QMTvCoRYkO0motrXjyKkpBdTxNQIhqoJX5z9TPWqRwdrOSRzhhKeASDwX2WgyKVW+CzqssoYd4X9q62GoSrskULkjnYEm3m56ulb7QpVqAihkabQDvaoR5'
        b'YVQUYEgtdY74/JWqSObNgYyLQzGpLSxXsIAuzB6G36xzoxDOvEA2pan4au1DRwP6XUqYP0m8Dm2Cx8NK64/4gPm0joGoDwLqxUewlG4lNRNUNSRnJKdpCd0UWYsrP8oM'
        b'xuf4yTR/I97G7ZxkAr8MFS+g7dug3gTUJiWAZeoEInPgMQdVAqfpZjCD9hUUexiLDhD4IQ+1mCpUixBpVKqvgoxFAyl4UTc6zBwZulGTAhXKFUOQxihLygacL9s7FLCI'
        b'ijdwgtcsqGL+EQ2YWT1NQYuuKI3gFvHx9cTnkCzK1LWoSrUEqvtzBg4FLaZCO7Mjn14GJXjV4UykhKb2CzNjhtmDCrlqJup5Yl4/XTM2ohrUgspmTFEMYgtXi7BQdBzV'
        b'oEziMIt3IR6wGvRouwgTUK8LG1QfFj+bGOJxE/GbRKVEpGtbyA5GMxyFyp1zrYYHJ8mERhZCIWvaNJRt7Y4pOGa5eE4RicrwcUbNc0VwdkwYOcfWhPVCGY5STrHJCJoF'
        b'VDVezIKLxUVoJVIbqod2kti6kvfE24OhHoPnjbbysMYHOps6YSnUxqIrAuraCpcZqSyIgDMKS5QXuA7Plxs/ExWhWvqiPkrDYjSdr8l7hnjnOBtRN6MJkK54zAutC1UR'
        b'T7TGFShFafz/Gun1iB31v4+OeEuTAGkCqCM75b0/IJz4v1fH7ueMGE5RSpGL5LcOP4Xar615S2J1ppg+Td6A1+MFnlmgCcZP64GWRJALP2rqWvDGvIVgwOvwpgK1ZIsJ'
        b'B9m/WsIoYqcWiFXcgFi7MZtsyusJJNGgqbqOQKzbYySjqFUb90Qw4zUfSsn/guYD+r+E1Crn5DSCvzFDXApERblL+aitmMxAgO1CallSLbYdnBEmZUhvaSTuCAlNDIqM'
        b'Ut1SC0jcsSVIFTrEFv4f5CTAkssDYuD714Dx+3f8l4TIKjPIAvx7bWsK93Bo0MYkV/xWHBShmqcJNiRNvCjc/IFkw81GpbrWelCilFBR2dfc34VFv8EEslHMqV4XSaV7'
        b'1AxVKMNFdHwcUP77oN5RUCWF7ETURJ/TxxxXBenESExImYDlIUbUGb9AiorXwwEsu7LLNhpSxPbglKXY3GXUSIUiLL9XyR9rzgJSWHOoQIe5zXebwTkr4prVBEWeFo5u'
        b'tk5uXnFkVmgiDRLHgOcCR6hPhmxz5ujfAU06xGnaJkJjiD82pGkx8bsRapa4oFwbzCatpfVMn+XlKA4gKWn+ZDmJ3NFHsRkhlnYsl4f7DpbNg7VrMUTx4Qcn1HWN0HE2'
        b'hZ2bqU9OPirc96SpQSnmNCgxqhy5TZVsAqXDa1snBhomwyJcUdh+dThj4xjZu9xKpqrAm9dymkuod0+M4TKjk6VjW7a//dX6ce7l32vpfcB71SzXn2VgIJu4Yfkkk+CX'
        b'5yZrZpXKJ33z5spNy7KMkldkWvwo28ObV6RM3Lq+fPfbMoNXf/1n+e7XFm0Pm9OyKd4s66O4jw8a+sx48E3ouGtv+e349Kx24+yE0y945Pw6+dAClymcKnBmyY3459c6'
        b'd0469480qU7TuJE1YesMr1V7T3nPZN5OB5/r19f2bNl7qz6hbcpph98Ev5y8197TV62+GjXjl63P9XyXPs1+pIXFrB1/f+atKE3bkwbr7345f3pVQM4on9+4JH5djm3t'
        b'OZfro/zeOW/ToJinOXLb926fvZv8/Laabywbesprnt/p+/oF/7Rtz6/TnLfvM8ud7zfrGn2vat72mnlkbbTd5fnJaZ+lbAw6d2cF+Hu99HK34o3Mmvc/GfXrNw/SOk2j'
        b'rVVvakz71u79GaV11i8l+rx82/rlL0tfGvWv5xpPXMgvaPnHvejxn+rPCNhyeMnOr8/UlTuPn3T/0+W5m3b+/Ys667csktrekHxT9LHxxZc2t63/4tzpr2+P17tkcPz0'
        b'3eLOFftm7dL8dNTJFxMCyvV+bCkJCB0XfqxGJ2/ve29k3rswI63hp+a7yzZ/4ZL2cnPYjdeEmiueDl9OPP5z8qHYV5zPrin59c4/5T0vzZj+ZvK1te+khnzxfVu25qxu'
        b'i0UPW1IbQt5Wj/1SfrlybmpZx6YwlW12YPszkd8YP1v78fmWnvnfrJXekbVXX373peM/f5tyOTt3A7KN/G5z5seq/XprZlUWfqX5YZz2b6ftIu5K4nfcLrt5bl71xu8K'
        b'Tv/tQ8fri5976G2h/UFR2L60Sw5ftq64lGrSF8xHOsTdu1GdHPtzRJ7dz3HfXfiHzYfJ0ZPk+uX7TkS/fdv67ufvqy5q1ydflCSectll+5LE3jb+wL3qI7cjPrWYeftg'
        b'xm/7+aR4vR2vr1dOo+6Kk/DhPfAkh8V+b0V0ZJXosKhi7AXmEatIMGLMcBwRwwoR78hpqIi5huYH6GEpEhVCLpEkmRiJqV4Rc5jOxzSvS+WOqrcpxZhnomseSrWjzJzS'
        b'GBVaOaFy6CLSHhP14lAJDYcBJZCTRLgHdOTJ0Zk14AzzADyOSWaNaijDjY9rPWW6x8Uxdr1n9iYXj3DUK0amxmS4msWsrkHlMzGPP8bChnH4670SiVUoGjMbJSpXLDRm'
        b'OlEHYqLvRudZYBp0VArn46GZcViHnDUUWPLIo2w0lnXwEBWGAkqLwiwYlWfTFOuJU3i8kkeHoYOTbedRuSkqo+0bwSEZcU1Ex/dx1DdRO4DWqhFAOUIaLG07qrbEj2hu'
        b'FzAHW4cqWa250GKkUqKqWdQ9mrou4v61Mka1ZxYWiW19Z+HFFNbzC9BhfyaFHtgK7cQTMzSScdVSzNlSDFXOVnPmA+sJXUPcXIMxr87SR6+AwypL1AsHKc2kRpEDy0Yz'
        b'kafLAcTIb5F4knKGyhGSGYxLLcSsd2u/GGKN22ae7Y37aA06830G809TNTJcWcWcEg9DKmP7OwSvQRZ5DTqkhlnkbSxv/Soo2yqKAzNQKZUIjKCQblBizLqoQpmQtRzP'
        b'Za4E97yOh/zNPnRYnkZhKpQNneZ4Nuvw3gYsEZS6oRa2BChNorBFB/3cEshVA3WJuGF9I8nW2dDGBnUQX8v5RHRkE4aFlDx1bSFkM4uXjg5Bo99A3LrJSRb9YetQ1+RE'
        b'cn+ivvigJwAb+lENUJjUD2xYGMRW6QBUGfXLsnB6GhFniSiLSnxph0ZAvU6/JIub6RWlWdSizabwTCCqUTjjbjZiwVUUW/f7Mjb/IhbdL4umHX67Nw07KEOnmdd/Bepa'
        b'OoQfD0OdA8CQRijax2o/u5nEhnJxQRfZWfbAAqb3SibCVOPjdMkK6nZDqfVAikyo2ky7rfTxoaiKAUgF9LgQVMV4NyZdVTh5MlFBDE1IqYg6SjUNlU5U7aLd1/EkwMz+'
        b'G30qqlSfK2xBZzWooAsnUWc8/tbS4VGWZrypFO/sBayZFizz1rAtitf7ArqEcoi86yrAEXR5LHNL7kaHbHFNhIWBTGplgSuoQ2Q4pvnKDSEdC3UEA7luBxbTn0hpqc8v'
        b'aoJy6vfrtlkMdTfTXNSLx2sz5lGN0/GVTIcUI9o0Oom71OUypGWSmOKgETXxoAwZlpirUD2tSysEqkldHihzORSTrUUrk0gmTPZny1EE9YMQmF0OFAED5ShLafD/UIb6'
        b'v4oWMzQazJR+55Ybf06aitaiidSJrIP/F/QEY34MlllGkZTqRN7BUo8pjQRDJB0DzPATOYjIWka/q6uNS8AyES4bSUZhwYolPdcknsUPBRKWg+SiFkiQDnVeB0tq5FO5'
        b'+JmmRI7lK+Eh+VQuURfUJToSLeqhLBeI3MYizqjLWPh7A16KPyU90sTPPu5xS6UoUWJirr0P/i99hkWJyXbYJL//F/xTqv/YYZh2n/h0mT4xDfqIAIKqD05kgmEAgdCT'
        b'DLQ0EzpNjE7ToRfgX7fUROfZW1pDfVlvKYZ6ldqTp4m1KGEb+bWU/NpL2tEYcOa7pSZ62N3SGur4dkt7uMMZ8XOivjp0Qtj8j/jf6SEGvY0+ws3PIeuxj6OxZ3SkgjU/'
        b'ZYsYI0byP/pXqiXRklDLfOTiyEdlYXyBH4KekahWGmoz5+neXAs5jgVI4QbSBKsNeHYJ/9azK+xRVw9ySdpwj3p2rXZPIk6mfpAdZz9t5ozZ02fZY36zNTExITk+SYWp'
        b'fStmnNrxndaGSWyHrrqWpo6GtgLyIQMTyUJ01HvSGE8sWR/3kRH9drdCEYr6kkhk9KjVO4hTSQLUTuem+45i8PqL0Gpsj9s2Rm0zuBm4xjT2eVUcarIXqPXjpD1nvw5V'
        b'UZMwnIPLUfbEUFwsn8nN3B9KXUKi8FOnydbdun0WNwuq4Ah7uGENVNjLCNgscDY3e7k58x/pQuXL7fHEorML5nBzktFF+vD+mXb2eKbnwOG53FzMqfRS2zTU+6DTmAsl'
        b'wBnXedw8VACZtBbUswGvWYeU2ETPzefmzzalsdlnRWHGD3/oFb2cW74d8yT02SOoyEYlEI+reSu4FXB8Cf14kWGCSk4NOO0ruZWoG2WzXl9AFfYqAjpsmuvAOaz3pZ+i'
        b'nvWoWCUjWsJxq7hV27axmiswr9CswoPZrLeaW42O6bIhtkNtvAqPZp2hI+eIJflW5kOQC5coOJvARKHRiXOCbgmtfRUcsSM2GG4hynbmnB2j6SKstCUrjPu9Gq64cC6Y'
        b'gWti1Ze5EKsS7vvMka6cKzo3l1ayGQpmoA7c8bFQ78a5BUxmjR7HPGUz6iBd70On3Dl3yF/KqumZBsWog6xE73wPzsNhBJ1CdM5aF3Xgzlu5enKey8fRD91QjhdxfTK1'
        b'8eK8UK2CfuiKDtsrpMTPat0abo2lOwsoUbEA+hRk53ShE96ctxHU090XFCZTUAeDCWu5tftcaAUCujRVQVTm1XPXceumbWBzWo8umShId4+P8OF8oNWTLcvJWSYK3NeZ'
        b'kLqeWz8NmllrlyEDNSrUiA5etoHbgE6MoTVD05Y9kI3/8Nq+kduYPIk5OtSvxyuTLaWTkunL+ULvBLbb61DZEsgmncbC4CZuk50G/VwD5S1ERaQrhyxtOVs4jzcU+TzG'
        b'DPJo0gzc/FE7zg5VzWcz2idAJ/FEgm6HCdwEVOHM2i2HA3AWFZH6z6AaK85KSKRzMttN7o2HH4uyzDnzpN1s+KcjoQwVqZFn507jpoXuYB93ovpl1BkDpU2x5qwTDek4'
        b'd0Kauzc5YSd2TOGmzJ2ptKa+JdCDzuujlDjqbpBtRaCQJEOVhDNEJyXoksyFpn6YhDn0TvoF/iWBAwlcLJQYohb8BGqDfJZmo2CHtL8O+sh0M1YHqoGTTDnXaO+B36cP'
        b'YEGgiueMzPH3o5Jo7AlotSDueQNVGOABBhrirqBL+qiNuQsdw1SojPWDPCLgA7vIyBA/MU+duoHZ7sL10grEr9s2GfH464mogoXUyF+9R2xCDSpjQhI4Q3yw0KUd6ART'
        b'5B3VhHZavz7UWqlN4ujbcAKdoa+vCBP6u4f7NZHbb8zmAC77scAM2XDZRpwhM6utgjiJULSFjt96piV9HZWq42cmcWxwM9BB+m0iHIi1otMvgUrUuXEhR0e2X0VnN2Ka'
        b'Bes4aV5tCwepMazrmMBn0MaX7IAu2nX6hAG+Ftpo73UX0svMxwjlBEax9vPZCNgy0wFk27IUHz2bOfo5HCDhO6A3AcvjGwyhhjyT40yf8YZ2vDPpINkzCzlNOCtuhsY5'
        b'dC03oBTUKLZF5noLbidF3A0HNGhQFtQKlwm6z3JwWHb9O49MC6qHKrboZzHtOUgalOyANNSe0P/AJXSedsgaakgGrf69SZ5YAMfZ7ISgQ3RyxoQm9s8tfmAhppOn6ORs'
        b'NqGz675dMdANNTiDR107Shz1gTUsMkoq9Mzon141LC9mTeifuxJooQsYtpw6BuGvl5vNthlY/Axt2gNbbSM2s6lk1mL3kq13FH+/chpdHiyLZQGb1lQ2rShzoVgFqsVX'
        b'GdFf70enoG0CHB+YWfEciDMSh6/vyYwunoYGJR5p/5jEQyfudnQItbP9mo8aN5BvoHyJBNIS2HbHrEEz/XqKGeT2n+fUPZoJ4oC1oYM6nCX4oQy8aFuhiKwNZzQHf7dW'
        b'oEviCKVRYhclcIZsI2hAZ9lotqN0Oucj4XiseJLIIwvxOuZQeoB3RiNd+XnEDD5AlMhxvuJKzwTKVGOTVoGanQfXnbSzHUrF7dGBl550c6XBFkYszFygiGeHSkNJGxgb'
        b'ii+67IHDsIWTz2EHPh/O01UfB1VhA5sYHVjIOaE+cdVLUR0dRsISOMe6gLdIL168CwtFqpEDJ+hkQEO4NVsDOlh8di9DtVjLUeilPXEyxWMZWFO15RyUhrLpitNl1LEc'
        b'pWNqT5cT80UNVmorxFXHnT2g5Nl6psMhdNCFJkJ0tDGeJHDq0CJAauicu5SNPJKwVKlJ3eiOJks4qXoC/iswqtQwhvnWXbfR5kwjVspJKqCtvuPYhzdHaXB6iU1S4nB3'
        b'YYET+7B9gQE3ea4/eX1Mpdcs9qGBnZRTd/1IIE5831p4sg8bF+lyY+LW89y0QK0zMVrsQ4/RapxW1Bs8ZxZoHTFNzDmUv1SPMzPKl3JxgdZx4VvZh1lOmpxRxC6e0wvU'
        b'yphsyT7cuMiIs5i7kvjIj0nb7M0+nMDJOPUoHTXS+oNVsezDTyYLnNRPXU6cDXvMRnPUNfr7GGPOepq+FLc+pjlGAwuGa1fRL7YG4wFYh5Iqoo7PXMKeLp6O+7rjKO1r'
        b'RfIO7u6JUvLfy0toAxqcnNNKtJWQnEZbFjtzd+3pfz8uYTxHF1whFxK+/+ejlFguVqFNOZTJW82sCCPS47+D24HOwGHmo0yRzMcxE3h42J6Di6hH3C5noYE22+SFhzBm'
        b'qRw36+fou54N1mkCnpYxcyW4+37vucx73DVyIG4Y0SyFi86RLIfSQO6kdBEJcksWGRMSuiOBsHJPSp6kqzk0eRKJH7p26UZ0erSVO/EMpt6Gbq4e6OgwO+EjeaiIZkqx'
        b'DGrX0+6/G7uBa5X6yfFG22VpvRkvi7t7ZJh2pkS1Djddu2CN25q/xRgu0/u61P+7W1+Fl194O/97zdeWqn+01MBRkP+u1j3hal3IWanDzZdTV7wWuSxKx/EBp/OVVUWB'
        b'fcAzqZKKVM+Vr8k3jlm1wNv/73/39601PHBIYjJvx/cFq3k+y6IyR7O+NohPsp64UuK2MqIyV+fSBpD5PWfu98II6zuWzR/Pj/loSkyQrCtereFi9oWWhkOFfrcnb63Y'
        b'svfeBK865/LS+fEG4QF+su1x32Vf++DbbdHFb2QWfRYWUv5caO5v/llH438IXOq9qPyE323FrW36d29q1zlseHHF7uyTOT9c2xH78j/f0oI1baNebw3+x9c14xZ83aaZ'
        b'+aP+hchzRrn7b3uduzlD5iU183b9/bngJT6d+8/tC3X+WlXndu7qwboTX9802dV5uG7MJb/ZI2xVPzxTMOrijD5Z3eFTSfqrfmh9gZ+dcGZZbNGYW5V1o+w0Vp328J2/'
        b'rvvEr/YGyetaX1VZx4ceq7/aPuKWdKvfp6PG/U1+4bbfrHWra+503On99F/BS75Yc/zq8k4nvYrwVutN0mTF5rl6370cG+Xx99+W3GyLmP2q3dfnZDphr7wV+vMz12as'
        b'Nm4LWt78421Hl81bP9eYen5kid5X51L9r3+yy/c575ir5yPjJF/dPjM19tyu3kMjDDX+4XrT5hffdWmT6n7uNje8EXw0/rc3+0K9j+d06t7bOXZvUFfpm4VNCe/G5Pr/'
        b'kDEXnF+YPyJ//HufOJa4eYUsPuD2yb38Hysiz34/xm7xZ93Kl2Nu6kja6z4KLXI9XBY5b8K3N5dM/LG8w+DVoMZVvi4GDysWtZ/8JuxOxw/3f5ij9XPttF8V3654M92P'
        b'U+pQDa/jFtRLtK9ufhNdPWScbA+PiG+Y6CYyIxgyVCibBWmQOvJ4R3fBaaq3trejbtWYsruQyNmYDzmlQGUSYSZcYKrjHHQeeu2nk6xpqAvLhBJNfvr0ibTi0agXTqKC'
        b'eVYoDxqdZZw0hIdeLTjAkmEEQg4J1+Nk7STloM1EkSygsjnQRrWcASZQKbqxQQ9cEtPhQLotNYW4qxlB6khcqx3ukTSJR5nzoqjTip8JXBZQnpUtypVxAnTwPnBSRSsc'
        b'O2cVakJXBjzYmP+aK0pjprADgZj9IuAPS3cZloENtOQCujwad4YaUPLGW6CODS7UUwY3aELylPRCD/Og6kHthviKbXbpz5wKBQF05jYvFWjuoih0bmggI8xvFClH/299'
        b'YJ6uMFT7i1rbW5qq4KCYgMjooPBQqrz9J6G8f8YVZj/nJhVodGT+//z3D3J9FrRBkzrDaEomiqGyWWBtI/ypnCp2jWjoCCNRkazHGxB9mMQI/2VGw4hr0lDe6rxUkNIw'
        b'EDQoN/6ZQnOcatISCQM+Eb8xg08gkj27TCS3JJHR4UP0uH9yYrWE/huH1NVDfFtmkhn9M74tKdyLpkO9WygPX7bdauj9NC6SHHfjzVJ1qIWex+K5avZfl0RFOwRXyIsQ'
        b'LiFMcyCOq/QP47g+EVGoxT0ps/dY96drFYljD25fCBP+Akr0MdgY+U94rF2ZO72E1+8VKHgtRTfY2kC6kqMAOB5qNAjfud6CpQj2snB08nZMtCZn3knGzdktt0BHtCMP'
        b'fL+VVxEfluubdb4KdAy6GuY0y6Lw80C/Z1qPpBZUpk8/WFfaltmWNqEk1V6bi70uv3U6UymIOTdQATrhwgLNQIu6jJMvFEygDc7RiEeWcAo6BpKqRcOVR0Me1czph3M8'
        b'Qa98SxEcERq8LYAyNPRcTvvz53I/Z8EC6e8aH0CCGgeQSAmDnl5Dau7f63zkkJ0uDNvQOgMbWhv/NYKwULP//IZO4b7RGbqll+I3t4Yk0YBjjviqYQCPx1yzCKzIDeXJ'
        b'IQuq4awPdC8jXsemCnRyEVSygJgX8U+WizVJhJMjJZ6XTfJRgqZWPHXgwtJhF1H+FLqjen9MT/R5Imccpdul00JYGimQvwJdtfx3k5SeDO8Wh464uLq729iiw6hGzql7'
        b'CCoNaKXvcIJC833BgqCCrK8vtOFUhCP2GbfSWzsuXsIJPgpHnhtlRXlvjamykHckegQWFNWtPYOLIhOLxsg40sjrkw213jGd5HmKUxG1l98vc73XJf20XcK9+qxExptX'
        b'2DOmeIZ03xJWhavlzARORXjZtcfC7wgEoRn2iWLLavpcsbp81BeCKUlOqjVhUzR77o13Rt+REYjxqoU6ms+rCN+rFZZ051P87pTpyZzpF6AiV+73P1R4r9NO1o5bi9lh'
        b'mw8f8sWvmKuI6Pn10Q1Wtk5VW6wt6yyI94Zhm+QTx3x6YVA09nMRa67rvmz9stPU2zJOjRdmGO2n7XbGxlwnO4ZT26DU6qYfldavv453kSVn9Z3lP4rpRyVTb2RjWuHP'
        b'mU713zKR9u7j0eHZJJX77W093MGcd+hnGvZTst/Ar96Zp+QOtbZQcdMaHVuGsp0ogsgeL3ANFnwgW3DGYnNlZF6cn6CqxjXX2Dg6rFnm/v5SrQvhM152faDmq7mk8suR'
        b'l5YeGHE8YmPxrPYjzmfrV1ovWlPtOX2/V4FMzdH29SIz9+sOxy9MDfhySvCiJUuWLNg3Mz8uWP3lhf9Ul+oXTfp8+f5T9RqFZfFfFZYdicrL+kS+d/rf12qFPVfT98bZ'
        b'uG03XZPlCQYmax+0b3I8s+rvHirhkwXv3tcykq98duqcFefvm8/rXNs1rWRD6+0RTRdLXk15wzxw9Vc+V+r1XGwjW+z/5fLC/Xf9ZzeMt3CPnXE3WtK2xrx5rXLXz5/M'
        b'N2370HpsuurmM83ZxoqQYEf39hqX6ATtqPe7dL8uurt1qdeP3ddULy9+2/r38bcneX47/qtPkqzG3Ox6fbmfxpLWT9dJOq59ddE4VG8q9Hle2CUv/sax5sMslefJyFnZ'
        b'r333WoDM49OIX/PvuT944fYvET+U39Xwr9yY5PDil1k33qm5dubmobRpK5JrR1/98q1Enz0PR77q/0L1xJwd93/t27/yhUg3m7EuPxlUvB5m8t0bv43sKNv70wPZtY8M'
        b'9xyyKnXv9Zva06OYevXTNfVfBHaPW3V5atD7f5vy/Qt+zq+apx/en9NcIUmPUeoxjEariYmLkvgYyjlUBS3ycMES1axnHFyWGbQRdougBvWJmlodjgixjhbUyWT+ukXE'
        b'DcTNmuOk00ejSh4aodhQzP80eTHl7JxQLsrGdOW8Gn61UtgHWaiYpbvMRuegXJWYnKytA3m6uqhdKx7KZ+BbFZ2SwEnI3SwG6VszdpDRXb6COFM1iVHU7Oa4oWw3kndO'
        b'j7hhp/OrUQUUsUEdhEallbPIW5qjJvkawch0C0tsqKscZDrRKcjBjOcqxLJr7t+AsjDHShsMQ8dknIZCgKJ9cIl5CaSjy9CDX1baEKcKKN8jDxQm+aA6FjUPLiT3g0cg'
        b'LZTiR6ABGtmrlfOMScUZTiSXpgLauFABnYSzs2mXPFEa1Lk4uZFphhxPPM3+QmjsdvrdFCjZ5tIfSA06tMj9NhIdZbUeQ5lbKKrWlXjblECGfIFgBA1J/6XB+z9xKx7G'
        b'zg7eePTaPPZXrs2pOjKam4aynTq8Ma8nxgzTowylVIwlRjLEEPZTi0YV0xJ9BtR5EoOM+HvrUdZVKhC/binz66bvGdAYZCz7izqfoDvAbMpuSeOCEiNuSUOCEoNuaYSH'
        b'JgYkRiZGhf5V9lOSoE/qNCC/9AbubdKO0V++t78dN/TeNsNvTkOV+HQMublR/QaKzjR2kxqhYnmwMIRbI/0ZYAIJB0wNy3yYZCB6gPBvowc8ZlLur/jRYCFKxit7w7kY'
        b'LLURgDfRJjqthTMyzgC6JOjANFQV+cL+dl5FBLmR1r99Ffh54JeBrkFfh2qGfeSaIpNwo49I1qxaOCSwiOSpRv9b2mSFhu8zy7+yzyISDAfWXspWiq7Zk3kw4dEFJS+v'
        b'+8sL2qQ3dEGpH3YGli7YhA3lxnRC1DjzFbK1qBDK/zdrKnlsTSXuke+FdktphgC30cvZckWFvReyJcQxSB0vmYQb/47E0dLxTy6Y6r9bsG0JRo8umP4fLZj+8AUjL2/4'
        b'ywtW/9iCecKJJCv3R9cLUjTwgqEKWSB0xjx9wUjbh8mS8YelYdK/sGSPSYFkuR7P56DpzljvLHQucoAvR4ctCFtuPp0yrKpJ4wX1VQ/UubiP9+8YeXAt/XDLDgnt6LRV'
        b'kV6f+G9hemFvBUeEuh2tulukPcamLBaGUxKc8IYm0kj6OMjhSEBfS/r4b6ZyIpvqTTN+1z/cYDTHwoPUT0LnvG3QMStHp8koS8LJNwq8C+RFjrv/rVSVhJ/Y6TVy7NUe'
        b'bWG6XvrHpT8sWilxTFw6z/FsutXS46nqlwuKzCulIdt3XXHpC7CvzDrUcqDSOTi48k6VlndBteEY3bn2Hxz3P3ymbEzz1RNRV+ef0Zl94crkzXebg1/qkLS9PW/X+wvf'
        b'nGGj+uja1b59745vmbtw/dnSsXVXXZTqVM+0ZjEUW9lYONoInBbqlMMJwWbCXna1Xpxh0s/58NDdz/lgPoEQr11QBEXUXEISEqOTI4j7ZQ7mQaxCmV9qE+Zu8vp1bblw'
        b'pl/X1rSN1V4yNhwaKH+CMnkuFrXL9wkTUc9Show7vG+TqDfjo2QcVZupTBljU4Mbs3LEhDUJteG9NYeH5oWQyRot3BnYr4rDz10Q1XFQC/mPHUt8gJ50gQ0eVi1CXeNC'
        b'wgLInUjP6uK/clZjiMufDtH00CucXN8GfMKIIeeXbOZb0kfwTI91U0gwJu8E9/eLVrHpL5/iGoNHT/ESlD2FUV1HJ3ydOlJNIjoCR8ajdClevENQ8BiF1BD/VRk/kiKs'
        b'WFKsVawWJoQIuTzV8wiDwXrC1EMkIdJ09TTeVxoqC5GFyNO5ELUQ9VzBV47LGrSsSctquKygZS1aVsdlbVrWoWUNXNalZT1a1sRlfVo2oGUFLhvSshEta+HyCFo2pmVt'
        b'XDahZVNa1sHlkbQ8ipZ1cXk0LY+hZT2SxgyPamzIuHR1X/1QWRgXqp/G5fG++vgbotPSwDRsfIgZ/tYgZALVGU28peYWFEPcB3+1GZaQhmSzMotmX7FUXcMT1mAGktDq'
        b'x0jngKZrKSdGQ6JucXR6yb2nMUBEpX9IRMWUSL+m/dt8SMN6OpgP6WnZh8gBYQmQyF8kz1EQq8Jz5SqzsMioJ6RSGrazyLZWf4yQj3NPIoGV41CbCz3uJE+Kh42PiLoy'
        b'0oMmlGFty3OrebU5e+EwDbGzg+Q5V8TFe+Ov+p/EAk7zWnWiYiCpimlqWhkXbKautXUHC0hzyBidZKFsFkEGC2XjjS4xp5YUJ8ggCWehZP+QnLOboYqlkelAqZCignIr'
        b'ZzeWntqK5wynSlDZdCyCEPK6Dy6iYy4znNWhWuB41MKhLidX+s1WqBlPEiuj5kSeE0hi5TLUTDukb6btYsvC10PPZE4RK6BSOMQzL5OTW6CSkdxMEsmERLhHFRJUjoqW'
        b'w2lreuHMm48uukCTI+4SiYCvO0mi2LZhFLooZsaBblRGxSmU4mFHolirQ5ewWxP1sNvqitpiLIftNLDE8pZAVRuQCtU+TNuVN1uzP5IStEIHyxc+Dh1kJvRmOLlKDLWA'
        b'6tFZMdYCHN/BvAybIHUJCV41MZnFrrJH5azWVtQBaWKAKnRpEotPFQppbAlqoXX/kPhSMWtownYo0aV6rsr1srWTBKqk0loxJoBjxuNULKi20WhV3GR0YkIspNH7+Rlv'
        b'mak3xzRavl7biM6NTmoHZBHfpVyrKNtHw0hFQip99Z9LJXobmbpOK01tBQsKhrJ2uYmhrbaassBWCaiBzvM8C9T0SLp3iSdq2wKpcqbna0PZMVhYVsD5wVTyXqiQxp9z'
        b'C/cW405lEHzRsABRNPIUysAsGPVtOIqXs55sFypr4BXTQacl6CKq9UfpsZFLVtYINCuqw1rp3sKeNWiansP2T3M/nftdl6yvQPf02Zqq+KpKdXsjd+fuZ42c+SKP1tFX'
        b'iv6+amFYysyG3duTk5IW/vzJhfW59cc2vx34cW1F55WuNOPL335f69Bw+v67K77P3NL2bPi9zLe1b3wUuH+3WcPy11LdtP7Z+PUvxbNGRhwZ+5XPu5tNEqfMH/G+SZPD'
        b'3QcLjyZZLEj7/Lc3dKteqxqfOfqlb28eupqZeGjsjc+/T/97z9h5e1w3vr87LuLFKW9lpqo9f3ftezkBJS/Z3irgF8x53f0bsF2wziq/rWfX8/PnefScLZ834rMNr25s'
        b'crC5/ck7NmM/7C4rtnqQZVLYHXPWeI12n7l2rEbPNycWrJfPXxlW9O7s5RvVP53lXVhVVP9BSWHJmnVzyh0KHaZnT86+YqG4sd/rTV3nS45OfRbZjr/Ezng7963lX04N'
        b'1U8uLbyi3N793vEf+0qOvgBj7wUs5n5OKTGYU6kcxcBTxxOtKXHiNNczVmS2CdPKX4H0TS6ulrb0S+jT4BRRAjrrjRhMaBFqtyAI+2jiAEMtASSF7l7I1aNoDW2U5c1y'
        b'hgxNGLKBGFucKfom1AQVE6U+5/8kEJzPSGZfbESpeKNko3wapks+ytxS0LRD6ZRVssX8UQW+9vuTaUvsOIVKQCfiUQYd2XiU7YG5A3TIQkTHHUAs0Th0mJIsZnZDKJ4x'
        b'OiVFrVvmR4xipstsyHSAbI8ZzoJONCeJ4n1QsRmblRxUTcCGHiShPEoZiylEBQ9HPFAR/dpiMiLZxW0HU3csRjVzUS8SU1znQz2fYEYtUEPon8EcCVSuUtBHnFAOHFeD'
        b'BlzLIAE02C2BLlQNzSwJyJmYpbQHRJ/kxm9DxZzCCw8cTz6dewu4jElOtoeTG6WAqDqaU5gL6DQ6g1rEUDWjUO/Q0ArQifoEmzAxvYXRar+BYKwUHamrIdkIqYkazHoL'
        b'ddBJUEAejGxwcnVvdFoYibrFMC0TopLg1AyyMIO0wwBVS1AqFiRoDQtRayCFiBG6Ae3oKKfAewd1ucEFMRwOJn6pJEu7GPJOZ4VkZPIq7/U0TwHqVkIfE94whYHUUY9F'
        b'oFuapKbvPp3ORTTqnkETyPRfmzrhEpQOWfONxN76QzHKDN7IFq2fAhnMlUAvuqBDV2QbKsFbpwUdJSzm/8fce8BVeZ+L42exp4AMRcXNYSmgKDgRBWTLUBCVPUVAhiiI'
        b'gsjeQ7YgQ/aesiR5ntsm7W3SJB1Jc9PbNh1J2jS3uxntzf/5vu8BwZXE3vu7f/moh/OO73r2fCRnaqmLoUvTUyr3bCuS0ovmQiy3BnjAhIuvK6/fFCgrc6UU+HQgRSFv'
        b'gmNJOVy7aO6HlTBgKTrKIhHJ8/JC+X/KK+hwCTrKXNOA5e/5n8/lFTU5H/E3fUZZmK4pEyIf7wsgS+/RXK33K35tK6WIf9Ri1XYlfmN9ospwZULPE5P9+tW7dZ9Xa/01'
        b'mhdf/H95hOW6/1u4evsyIfVR/fkXK/QvK6ytEJQcExX/nNL7byxNiB9+qfQ+eyokJTXpxQtsS4JCrUKfOewPloc1dowLiTKKiTSKSeH7ex6zOra8Cy9UdD/pguA5J/Dj'
        b'5ZENudLZSRHhMSkJSS/U4IArN//B8877J8ujbZSNxnc0eLHV3ea3VinoUkJ4TGTMc471veVxd3Jl7kOSU4z4h8L+lQlELU0g4mpEWOrzWjr8bHkC25YnwD/0Ly9fgc9V'
        b'e/bY7y+PbbIEXCkrUIugjH/BC8O2QlB4RCgBzTNn8OvlGWzisIq7+8Vr8y+f+xK0PnPgD5cH3rwKul946OUTXzIcPXPo3y0PvX2l5sx2fkltXj38itE59vZ4bItwObZF'
        b'UCDIEWQK05WvC5YNAULOECC4IXyWNZW98kkDuOJzYmq+Yd31JfOD/1N7+3KQlxYdwTVATolmHaYfwV9SBN+3gWtAHJ+Q8qQ94QmbwtIhPWHPj3l4U8RV1J/9cd3vHK7y'
        b'NfXjSAvuEv7Af1Eq5HtqdYZCwwohlwTXIZmga+cL5c8o+Z65lHnM9dD5+oLHTYFC+qYl/ra81keRMpFRESkez64Vz4b9L8bAWcLs12bgWYLqlTXjU+3o2fNrruG4TNhz'
        b'C8A7j8waWPl4aAwXlwgL8iqwIICR/zcOmidjr+hAP4ttEnIOmmrdS8xBExv5cXAJKEVxDho62C0/FOMrpnSwXBxbsR+rCrB8sJBzZulcYT7xqxw4STdf+IRVnn/CyREp'
        b'/DDZwsdisW4JVw7+txc455JVDpxD9KwO9pguH3QC5j//pElbYCdtosK+hilZqeOzW+DeeVbbgcGBREMI3VjkytmvnEjXyoYsHOCflFgLYTwFx2LeuXVeyBGrv7/z+4tR'
        b'zmFuIW4hsb/oiYiOio5yC3P56BchHiHCP+lf1I/V9/H/YLecdeKUQDAyo/jnPPknQtSeHq6WFCEDEr6Q1zc5H7Gqgroofc0TZ8S//Pbjp7J6yE9e4FRqVgakPWXgZ9Nd'
        b'zoPGF8UXLHvQvg71jSLq6/4E6XRgcXjJPNcnWrva9ptslJwSExdndCUkLib8K8y4QsHTOIi8h68jZ0ELUs9Q/VTAlA+jK/p7N6vEOGUGSJKD6Iruztd/F/x6qPFvXEJU'
        b'Iz+kT2Za4iq3E95St+DDyaO6FeHSt279KUDZ7WhfrIFdfay+nX5TQ9HBWH3dEYtwQdFus+DAV73Q6OWKb7VA82veOgpvid98z6rOWk3w1m/0j1xblCrymnenJnSZrtBB'
        b'1cXuMCV2gvZEvnRLli/Mmi7ZQw7v4k29WINT/OXpzfjAdcls4IDTvN0Ux7z4Yh1D0HKYYdF+o1WGYBjEUb6skdH5lUbZKLOtYv8YuM3V5rE1k/D6tUQiFKpBKxa487E/'
        b'5d6ZzMDTl+B5EgYkAvk40Rbo8eAMNCrBGq70pZm8QGIo3L+Lta50l7Gkr3RtKcYkB3EnyuHK8W+KK9p8NUHuLwuL5qpjSFZogUuvX8G0njGnR1xsF936xQvgUb7WUxXR'
        b'5SlItZ9WUmJF7QjOsxbOtkXMVDC2t0mMiLyruKQ2vKu4JL+/K8+Lwu/K8zLqu4pLIuO7issSX8TScniq9a+3T1xBbfTo40W2S2zCiiKJWFVoGPi/Vc1BXUVVxMU8HraB'
        b'ARzHOby9bAlShjIRzOlj7xNMWkv2f/Ktx32E8jX6NYJwUSnznCnkq+Vr5WtHyn193yD/FEkRKuGqtxWZbzBSEKHIeeMU2bvD1UqFXKS5Cr1XEq4ersG9V2n5mhzJqprh'
        b'a7hvlbnZ6IdrlYrCt3HPaHFP6YSvva1E11XouoDdUaNAP/rhuqXy4du5uhRyshYkavnq+Zr5a/K18/UjVcMNwtdxz6ny76UfxRolmuv6UnH4Ds4fKsc57FhHHfV8DTZa'
        b'vk7+2nzdfD16XjPcMHwD97ya7Hnu6RqF8I30/E5uTPakBveULj2hxHkd2RPq3Po2s/XRCkThW8K3civUCNfm5Cjjd9VlSEH/hURFJP1iDx3MKlJub7T6Dkb/6f9koxAi'
        b'/SsZAnMPhqQYhSQxi8vl1BgC/lUviiT5nLs/nC6FpTBNLibFKCUpJD45JIypssmPeRFPphCDSUiSDbU8SkjyshJEnCneKMQoKuZKRLzstQlJ1x57jYWFUVpIEus1Zmf3'
        b'pJuS6VePLXCZsR074WtvYXQ8IX5nilFqcgS3gsSkhPBUbrqbVztoZbazGNq/J1IeVhcwWS5ewo5+uYCJuED83GQHmYr0i7OPHxC3VY85aZd49KWlJb2Qn3Z5R5nyRce6'
        b'8hieqmWxs+eOLNzC6CRnhgpPoBmRVmYUcTUmOYV9k8Z2NlRmv4l4itwgm5BMzebn9ITynRbDJklXIlPpdSHh4QQmz5hTfDj9NQpJTEyIiacBV5qpvkJoYcf4ZCqJmkcq'
        b'C/bAchyR42uK8hVFnZfN3FiFpW5c8U9vZzcPLIPCnXz9MFjEfBW8jw2KqZaMhU/BlPrTX+ENNXHOS0b6K5ivlAl3oJgToQ2NhFhN0rOzRICj6nI7hVgPLCmb0dZd2OLO'
        b'UmCvCki66LhqDHxcOoxqQZuPOXbhGN63EogtBBoHRTHQuy0SBlK5psOKUC/rhCXLRDGDCejFQi++A9Y+qRxUYgfy5VxouKpDpiLWEIRWVJscb8cJcWaZYuXvy7IWAh1i'
        b'BJzXHbtgnpb2aGFYwDXZKjXDMnezk5iDtSxa+FSCAmZpwm2+oVCrLk4kX2ZVNcoFrGoZFF3bG6Ph/apc8it0edNvfn6i/IA67FbNu9nt3nbwu659kvfXxZ0TVWSVbg81'
        b'1nKusTwfbKlybvOMev4vVPcH6Md99vdfjr/W46W3z+ov9w5Ymvh9/0Rvz1sml6UXPT03hL327rYLewtMVO58/u3ei7kFLxXmntz02/M24d+ZLNXd6HL7XXWVgZFvb/zg'
        b'UvPrg7/6Xd3HWh6FI/81X3K7VjOy8o0/Jp4fbcmPCdX3fLPnyPaKQbvtb5dr/unq4G8+fmNaMyjxD+Idp3/0hz/d+c/K9U1ldZu2H7F8x+jIfwv+PnjEL8hRqsOXmmyV'
        b'RJDo6CDvJnP190EPp466w6T5k44+7MNaRazaxlcrxF6c4J3uWL+ddTBiPndslvI+vvx4zOY9kAKJEtYwFyS2Yh538chBGOF9kNvj2A2cC/IyTvOB3tBE8PAob/HQYRYq'
        b'5YUDvJPrFjThjCsfYyGVFyjpiDbCLLQdNUzhW0q1S7CYhAEPduQm8gJ1mBCnWp5yXcPJraxEY4HpLixiksIpuCMPPSKz3ad5QbkcsqRcdfFHjk+8a5OJD4HvEnGF5Iw+'
        b'kqTdWL1AvL9ZCHdxbC8fjX8bZ+2WI8wf3uAizLGfpGgjuhqI+WoyvxzXZqzE1VxeoAdTrO3UHecjcdzbxaSY5i6rALs2y2uL1DJM+Gp/Mwac3wzHHTxcWak8foJroE4M'
        b'5Qe3c0pEOHTZMdeax1K5QHUfsRy0usOsVwqzh+ECTrK4Ey6zlZUp5xKIoGyXqzlXwJFVknCCUQUc9aWNGI3kPXYV2BYmC5wQiKX0PIubUMISbsPkbmivLoWobyQ5A60X'
        b'aI8ruHlLjWCUxUMzIiQbUF6gKxAbGuAidHo+GVL2dYK4n+ZP82UE85soCrYs0FyeC1dX50LPVbn22yxkfSOnNvA+r3S91dz5Ga2wl3nvCr/Xc/yHYv7ep3i71qvQYpi9'
        b'6xuoGVmCD1YmRT5zyt/ESiz3fAvxQRWZhfiJwZZ9YNbLzPxJ7r2CU7+gU4zz16Q8z19zZGmKSSYscm0lY11louaMgFxY4LIR8OsYqZ8wAv6/MlInXRc+tpylfXrC/Pjt'
        b'D9bwHVq1E4+xDq1Xt7G4cAWBYqFwKvYdqZAvN5qL1ace4WhH8go0JSSdMf4Ki3LSDdZEdMdjYJAcFhfEZVF+I1OxwwtB/+IqY/EJetreOHLZhoiT7IObpzlWma6kQ1j7'
        b'NLMxcUKB/kb1Qxug+yvixDkbV77wX4sTXwKcx9M1OJO3g7H/49SaBQ4Wupm4mEHfvmRfPoqQfeXpxiw30A+FKraZOBzzS/m/yiUzLFBv1v5dsIW9UOu3wd8LNdY1CXEL'
        b'iYuMC/04+MPg+MiPg4uiXEL4vr21qoraWCsVc4W300NZhR429Fnl57EKKMfBY1wuL7TppCyn8pLEgPU4sTqXN5NjhDdJAihn0HYc2x5nCriYJF0KJHg+2V+ydSdlfV3Y'
        b'W23EfsKMvtqS7f5CYDip9TgY7t998gXAkFmmTaBVoH9M/aQc3paK+Hi+KczDStdr3o+M2mdwkJNXj8fAXVcsTnxk0ib5P2a4rV/CETebmbnHTdpxUS5hHpxJ24CZtF/Z'
        b'KDNqRwoE3zJTCvlVypNG7ed4HnKEL2rZPqOqrClJ13/W+a0wcH/F8Mde6MReWul9ePY0iPYxpH02PWCmOxaNTfRAjiiC3DJFEH9l0HO0VPJ51xNqoFNECum/Mga50sjx'
        b'bAX6UlJEJK+sPhF38hQdNykiJTUpPtnOyH65s7hs9cFGCaGxpHZ/hW76dG4n55HKIA4nYIzQu1gG+n5eZ8xPn1kRIr3pzCnnpRBpyNqjFAtZbqmM7uhAWaTrY3rsCmWN'
        b'pXX2rvdWUcBSaDeIeVXlu8JkT3rs7iuv/i744+DfBn8nNDqyL4KZ6f1f8seRilH/+7elcsZbv/3G9975t3de9hJ3XiSAH6/Pjv3htYCx+vGG4mYXf5/6o2N7S15WbTYQ'
        b'VJuvuabcJpXnEz3qcC6D018iN8uSOURQzmkvkq3bb4Q+pihkasE9LvDMAeeClhWnTU7LqhPTcXl7O85BLRSwCGsYgxJe7/KHPF4H6YXpSNdHQjwswKjKWREO3cAZrtQ/'
        b'64mAUytpLaOzpB5XLtHaVJhZhbrPFkRXVlNgKSUy0OGQ2e6bInMiH42myFUTSV/3GDateD0vBPTKosU4G/cjqfmppL9XxN/2SFY+RK/wfSGkH9JZifTPmeaz8f2JqIav'
        b'4v1L8QWTT8X0lCfjShIil/IU/vcR354f82si/tM9aSRs+hRlyiUznW+7lLDxnP7vX3rjZcLA2ra8zcWW9dnWYsEulFx/x1Uq4sMYFtZALZfjsxzDae8nJ1iHdyXpUG3K'
        b'oZmuh8D1pPspaFwZ8L8D7i35kp7u9dz2wuzopoBFNz4NJGTnIhNfD4uWxNcjopWjhr8QQLaofxVAykaX8ljwrkJyyJWIoJBkj2cbetkkZPxInlNt5L+hmTf0aWbeJWBl'
        b'9u9wWYn0rwWq9su2+oiUEBYyFsKHzlxKuEIMjhU1X3rv/xSc88/INsqOWYM5K70ZMwFfSk1OYSZgHu+SU2Li+UA6pqw+1YbLK7Crwp+YkZ5e/jT78TKKsbkmhaTx20Vr'
        b'/grMYmD8pLlX2YOz1frhwz0cQzUwfipLfYyhCoN4S+YteBhrqoVFLiKB0FmAd6ARp7gaJa7NOnxxE4lAcim4QZhSfI4zokackrB8J6PdNrXrd52zEfhyKjSfuTJjgg9N'
        b'Ha970ru8BdgI7XExL/93tySZlVnGzkD375mrH7PXFP/c44N/Shy8NA+e+blRliC72ahF8quBEAcr9fJ3F6Qqyj5vdgUZbftcqUGpTbtof997NmmNt80qf73ZPt/yz3s9'
        b'd1S87z2x5Y8F5lfe+aUk6iO3wf6D1pa9Fz8aHK76YZ7V1UBVz6E/Xmoe6v9b2Sefl9Xa2KT+0ccpau3Lixkvffwn4dEL21+e/LtUUVY6wwoWiX07bOMMkJz1sRPmOVOZ'
        b'+3mWVrWCfZfS7hEL3wwdHAs/a4PFKpux4gnzp2IclnBvj1mHvaYkqNRjJTMGMksgDOMD3h3f44G3TE2WwvCVcMD5gAhaoeMUpwJhEXQeMXUSPM0c6Az5hpzdbSsOQi9v'
        b'Aj3F+ojI0kXtkvgROmAGS5gVk6SBTmbJ5MyYmGf3dP4plf+6FrV3FWSppRwFdf7mFFRzqZiDlkiTK+igyDnjdYTpuk+hbDTQakMax+btRV8tEpBG8OjeR3KBA/2a8EJk'
        b'uFp3JRl+xmRpIznLHUeHlZZDq3m/+m7mmZfEhcRH+TqGKazAbLYUrSXM9makmWVIMpuTMuc6Ze5aUb5Gvma+OH+NzDunFaklI9kKBUpEshWJZCssk2xFjmQr3FB8pEb8'
        b'4obkKSTbPjycRWLHR6Stjp5hbineBcZ77MISkpIikhMT4sNj4qOekxxJhNQuJCUlyS54WT0K5oghYw0JRsHBvkmpEcHBZrIY8CsRSVyYAuebfeJlIc/0xRqFhcQzEp2U'
        b'wEIbloJPU0KS6ByMQkPiLz6bT6xy3D0mVj3VbfdM7vE8jsM2gvkVkxMjwrgVmvG7/FT+8SgDID71UmhE0td2Qi4DGD+NR6H8adExYdGrGBm3oviQSxFPnUECHze9tA/R'
        b'CXHhBNQr2OJjUdWXQpIuPuY/Xz60ZCM+EcHCyJNFxKbFJPMzIN4enRBuZBeZGh9G4EH3LEnSwU990dLsw0Li4uiMQyMiE2RcdjkRmQeCVBbgzZzfIU99z0oYeuZOLseu'
        b'2Rk9nqXwKIJ3adxnRfLK3hVqFfrkW1bmOnzF84xCkEji42lkY21rbsn9nkpUhpAwPGLpqJbeRaDPQ8nTA4uPR0SGpMalJC+hyPK7nnriO5ONuF9ZkMITk1slt8ggky0l'
        b'kbQE+vQ1pK5V4oyGjOCtFmd2enCCiQ0OQAdOhSdbEfUXJrCeIDPenJ3Lm9Tuoo3KKlcuCwVCLGC9E6bwoVTIyzO5UIp1fvuYBY3UZigTOlgdSWVNTbAlxZCeOcULQ8YW'
        b'5sZYsMuElAdn6PNNxDHIM0g5zTuTocZEaf8FvMM3Bc05BwOrfOB8cp33kvcb+ywFYRcUoc1QzAlIu7XVWJ06xVv+wW4/1j0g4BLBsXfHBiZLLPuvSbU/D7ex3NVMau4i'
        b'JzhkKo+NWLmPb8jRoGlkilXyAuEaARRaQAv2wDRf1W6LAqvRofjAONisxVpW7PovgZxEdjTfOTjuWnCmrKb3Zq6go/9RjeA4TUNfAVd/eqvcJuwQncIuVgNPBRs0uKJP'
        b'3P3f91ZiucVG3RHBbpOGKgLOvoyzwYe55HIfZ87KfJImX2LK5MnlhdAFZzMXN4uT5iGhJvICLJaqXs7ANs7Ko+BMp/a4jacESqFf6uLuBr2+zssuWsjGGSXoEK53lCpy'
        b'p3xo7U3mVNyPLZxfkXMqZgr56ii5OAcl2AIDLCGbT8fGfnf+2m11Ly4Z2wOa3OX4ZGwPaOdStaN0IvhU7NOYx2c3slzsaMzmU7VLBdjB5UPfhj6W3MhlRLPsau6y3Om0'
        b'FRnRWGLFJUWHOsA0N64xPHQxpYXg1KOE6Eis52pVKDripCwjekWyYkrKUj40VKpJVfjZZ2FODNvw9djsLuaz+ZNpApz7eBbyAliE50UcWZHNH5/IZ8ZP0w7eInnz+MbV'
        b'ufymDnydgPtYYAv92Ohq5bKUy++Lwxy4ucAo5qvYMGsTb2nCMsjj8+lrUjOYtW035HJJrVw2/x6Y4/t+jFqdW5XMH4vzXD7/MTF0cVPWvgKtj8JGYdGdpfP7+0Ef93JH'
        b'7DfhQlI1TR9l8sPkTj4dv1vFZ0ViuBjGudzw844hfAJ6dxLUkObvH7tS8fcP4i6eSoUyFkvijb04SWKzOEJ4gETvcb4XSRMOa/mQTlRxUODnRVflzYXQYoeFXEL+vWQ5'
        b'hkrOrx0PNlsb7yTgTyVfCkOQd5YWW+0pEYhUBbiIIyekynwjlXxSdCqT1ZNScVQVRzWgyNERp1No+2PFJzEfSrlSqjiGnRdX3oTTyThBmH0vlZk0usR4dz0UcvnzKnHw'
        b'YOWdaSmXlZLUIBvK1eUFxmIJ3sIH6/nU/x4HfVoWC0VRvQylGqTMDSSligXahuJ90djJkS91HaXky6nK3Js0cFKJVIWJVHY3TvvBFM2Bxj9yQV6OAKiVS8pPw3tYvvwI'
        b'63a6gbtJO0Jsnybhl1yulUl3GMC08ooZ0uw2wpBkRyxUc6XOgrESa1a8KAULrJJwgqZ3Qmy3Cbu50RyOwdjyPaS09KfhWIq8QFNehEMmfAMNrBaFq+BUSkwATUZVSY3E'
        b'eLUbIhhPWs+FDunjBJbTgXoR1NZ6sROVwxkhVJL+U8HXuWg+a+jjjpU+WIp3fKBUAh1nCWAahTgVbcvXBx5Kw2Y2BJThwupB1mAdz3SSryfjlAY8xCa6JMIuoYk/XWJu'
        b'yqsB2IzFRBpdd7m7efoxFuKNBXAXhzit24wRypKTblhEShjc8lNKhkJCPC6yZvwcNLuy8uJCO0EgVmGNwjZ+g+uwBipw3JmmXCcndTUnFPOQCNZAsxhqWaNDjmSf11gv'
        b'IDIb/fP1weeqNyrL2iHsNBH4EgR/oh987EHwaQHfAELw6RHZB+OjUgnf0ShbLgH6BX7YJhBcY12CsJj7/jJMEqGQYDupdumCdJjHGS6mKuE4NpoqnMAOFrx1lWC+gPt6'
        b'iz1mYzEhZz2pvIKYw3AvZt8fe8XJcaTq/HXrxCXvA/H/cVTz7nnv94Pab1Z9tBj3ymf7HN+aeXWN1s6jhi/9+iWh8VFN4zMvj41qBp9/503huQrb40VGUa+e8u50aZh2'
        b'tfNTVv/Z9zIOHDhgPdvqc3kgwiJ44dy6zruhxd9Kyd9+YF/SlesfjVx8X9xYbCr81esXNv949MJ396gXJW/4bYrFgwNd7xs2R83oNwf9481jf/+z+hfJn0WcrWrvC/T5'
        b'9S/+fNEkV/3Oz40cPvH+7fbf/yzDUD2k/+h3zta/U2hrkOSrEuL1b5fXmp4q/rFnrFZndZ/Ce8PfOf6zH7imO3SnODbrm+e/94WZdeLbo2WpTq8kW17Rbf+w7f2Hgw+K'
        b'rx7x/GAsJaWq+0dVSbHCb6kYe2+Y3pDYH+H7ybGmWwf84idvvT3w4wnNH6S5zXZvCA/4d4VgzUtm2rt+8uEbZ0N+PzvZMLn+x/Fn5yJ+b7PrZ599+Pc3PE4cM2+74+Xy'
        b'4TbfsTf/8N3zvlcaSyKmbYu/e+OPsTl+fz+mrugWnqm38LergzOB1w6++uof5O9q7nnL5LpxYuufvvzjw1831aVe+nJhnY+Nn9mv/pIa+IvZiH+cfe+MusUHm3dmHp6/'
        b'oVcrTN9RHPj6G3c2/GeWyeSM+D+Pxzf6GMQqFBW9NjM87+dol/Wlj8KP4t3fzla3+LtvzZvvOPxl32/GBnMiLaodkrd+blgv/dLztQNvDw6PhkUMhI7n/6a13MILBwXq'
        b'/Zlr/2zxX5e95yLa4R+CpoPwZYWTw/uZh3+OTepTFgMbe253fC9+/fzWDdMfhlgX/zij007+J6XpcTZ9Hwf84/hfR86//vErOz/9kc8vGwbvGs6kfBZnaNH8/pyR/e+/'
        b'k/HXadPPj2pfi7Q6su8nL72SIP30Uz1jk38ctLeWWvApUlV60M65T+9LV/iOtU6K4d7paL7CQwHW4jCOZTySHrzlOYuzNuvbzMomY+t+zpvtyd2xBvPFUOIv4O6xhnLI'
        b'WXLeYBG0rTD9YPd1ziptAJNmLOgNHsIkFx/JRb35X+KMO7uMWAFITw9swtonArWgT8p5li5iPmYTN98KnUvGIyzawU0fig+4cFFkJhuJvnNBZEYa3NQSt+xdGUE2cGKF'
        b'1QgrN/Ehd612mCMrXZayhRUvY5XL7PiKsCf2Qpuph7tdHJbKCyR7hNCL2VDLt0PIxlK4x0XFGQqXrEm+KKtcdgeqSXThbFHnVZZNUfQMX+kVuy5AI1d39fpe5qJjZVet'
        b'9Hgb3BDeOe1qCkNYYg3jrsSOr4m2bfLmHF2p0MpXti7BPGuuEq2sCi2OhfInmZPmb+psdk5n2X4Ho4G8+atmC7ZwAYDQE7MUAwhtkLde5riD2i04tIcVN9+lQGpCu9Av'
        b'VcJFOxqtu0TSKkxDO5/RAq1a67nZ2Aavw2IzLLt2hI6M9sHdjFj8LjHrdOLKp+iUakI755fDgR28a45zy+HcZj4fphi6Q+iIF1YIWmPQys03cDd0cjF0VZD1SN7FPBjm'
        b'Ty0L8iM4sRZ7XZfEWk0Y4571gmprXq6FuoBHci085K2c11JTOKm2GxeWpVoWnceJcLQjWLhCroWi87xcq0hsmO1U4EUPArZMx0dSLT6AKS6gIwn7rj4p1lri5JJceymJ'
        b'h452o0P0DhfeGSkHvdoCDcwSJ8AdXW5xzjBCilAxyXGea3HWXMQg0gTuJvANigevGK4ScUpTLuOkGo4IreCW0Azb5ZQ2Yy63Dw4wB4sELrssIvnTUcRGEQkV9Tp8gGTx'
        b'etWlin6Fu05CXiLX1Xm9o4TwcTaM73A9dRA6Wc1A6IKJk3sJcQQK2CZSxLtQl8IFFrerkWTRLzkk5pljvylHdW5iHU6wuiQNl5cLp5LEtFWMZZbQxt2i7WXPFy6xcMci'
        b'F6iMdbegwbFeAs3Qq8Z3pa4jIayXu8vTzBznsIPVUCLiordXcgQr0zjnLuY5kSL2WP1KEpwWGXZwBSwNsZ63IrfTtvZwVQ6LSG4p5AukqECpCNtwGvP46M18Up6zOEt3'
        b'oQirzGj3PUSG26CJm7Qi3N2+MlKWBMxmLlr2FM0um6+ok03yYi6Oa1wxd1rD00Il7BUR6mXRuXAoPnHtNJ2KOUy4SFlTeqUoEYxtPSHV+NdTix7Zev8X+zyvdIGHhIev'
        b'coH/iYlU38z8baPK9VmW55pnLFVG5kNKWf1jfaGWSH056FRRJBLqso7MsmBT+iSSF676+VSiIhGu+vlU8rH8JkXufXy7D95urUh/VbnCMBLW5flv8qryQlZrWZObi7pQ'
        b'XaQlVOdM8XwbkHVcmRd1LvBVXSji5qnOlZV5wgW5Yltkxnol3uK+bApPOs6s8MtG8KQTqw34/1q9awV+nEcv5kbkBrNYHpsz/p+kT0UqsjyXb2T8zxJ8avE8L+yKLZCK'
        b'31Vccn4+StALkwge/ZEXrDB9schkzqbP2/yVZDZ/IWf1ZzZ/Uf6afK18cb52pLbM4i8pkM8RZMqlKzPXrMziL8dZ/CU35FZY/H1ET7H4+yXKQmxXG/w503eIzHS77L19'
        b'thl96Y7VSTkpMiv0ileYyYzRYSHxT7VQhjJngxHXPYdZE5/tWngRqzvzYzx1VJOl6ZkYcYk3nIF0aR68uZufEvNd0NTjeRPz0y3eRg4J4RHWtkahIUmciZZfcFJEYlJE'
        b'cgT37m/mleY2UOageLxKz9M8C/T6p1eVkNmtl6z2zFD+VYbdb2rGfXo/m018oJfY05E4kCfMe8gaaZ96jl+6TKqEw2tVOHf2fmy1XmkwdWYmRCzw9DHmk5yvQD1vOU3H'
        b'biUoveLJadRROIizpjC3YcmdrQHznFr8mZeyQMd3h5xAMzhOScWPbz5SsvAHH0GFrP2IUBBzNdWJ8asSuGVlCj1mXAXDch9m7XR34/jsmUfBtVxoLdRD+eMqvthPDbuC'
        b'8R6nTKuT0NXPdVzGPFd3gTuMWvL55A3WX7Bscv2RLd9J9td6xYzXzt9pOMrXcx47Gyh4TyDYfXT791P2q+Qq8pcd249yV+Muxwp/qLxJTmAUfCB2j52A72fcjNkarE+3'
        b'JMJKYHUoKPW4gCvU2MT1lly2XmOBuYs7VjO7LUmMJ2XmcOfgfVxPhVPOLmYufN02EhHK1VxscCqVRcnEGlmutORCs/tzowvwPitPyeSDeBcd1oq6e0VJ+aV68ld3cha5'
        b'jTCxwxSy9y0lr/N2zRtYz0cK1mBL2sqhN0ELb0eW2ZCNl5+DbHiolAkLG7lNclckNUSnTY4le1lbm8oMIUdj+S38LOa0YIKk/aMbumPeCf3WuSQFxiOYNVwqxxf8HMbB'
        b'EOinT9dx5JrgGo7DDHfBwpwApF/CFeluZTJgHjTw0Q81UA0tXH/HmqtXBVc3wghnIfF1sUUuAGJ+XYwghnSULM5iCwuk3pBOQ+oZE4yxmFQuGyENm3OOt+iOKuH8qtqY'
        b'cVbMAhqNDbwh8/5pKCIQnInnBTtOJyBtpCpG2Gcvl9xCMCe2Wneo4lCytr1q3v2fLpQv/Plt2zpN7di+id06Nb4p2054h/fs0fmbW1GyyyU89eqJl04of3dhEcp/3t1Z'
        b'9rfdLZcm0jedHN7213VbitYnZvx3sHOH9Yd/POAynmm6413hldf+6e0SE/6Tpk9y3Do/uvx2iUF/w/ffOl5n/M/yf3w7NWiy2mDO933n3qBLgrz6ytfb4sJE//nSgU9F'
        b'ZxJVSjLee6j33uFDv6op99Mv/pWxvs1o5/tBE39L2/HOz3tUDQL/ZPfBsM7HPaEZwsHZ068puE7+tmxH35H++JjvfnIvsNG4+i9x5efv/3Sy9qf7qncUnNlUZxWReiPq'
        b'yuFfNZum9vq6j3c0fVb5z85AC8fFwx5/EV2w+qNVoEPCsc2/PB+wYPoT6U8Kjmgnn7P54Fbs2cPrftqt2uJqF5Dt8fmgb0Zn4/4NRjGbXlFJvRm+Jur9iQ77Clu9c39b'
        b'99MvdT7cbBTW/IOY9JwT98a9Ln9rKDelySvZfdgmPsHu3p//EtZfdOGE9Nyudzrtfn3x7Ju/e8UwNTTuHY39jq6fbbrb01q89o2mtYZW5nX5H+75fd/r/9j76aZdvYp1'
        b'a//0XSmv/uAwDEO5KdSFyBLhmB4bKiuXuIHUwUHXrZCzMpeN9NhK6OPNHW26WKxCkFjwZCCK0U1ec28i1XKWxegvVWG4aLQFeqx42byVLrBuggVLFRygFbJP8NcequM9'
        b'U+yN4LPZuACWLlhI2UbXjkEfzjyKMMV+aFldxTMOeP0Rs/TssNhYfkUXRTH0cvpaKE6FMvt/PeQvNVLkmiiecOSGV4VbyFp+n1jZJ/FoBqe1pGBZtGnGaVmnF1mbF7iD'
        b'+fyK65IOmAaSplq0i1uV0gYRVMRDKTchE+g9LysZz+rF74Uac2PI5TXEIUNswOLL2qTlP67jl5PiyQ5E1SCZ6drQ4yaz22hAu4qN+Jw+FHK5MpiDE3tYmL0PF7ZIxJT4'
        b'hqm8YD00kZ6JXfv5GQ5hdxJ7gTtrRCdvKLoOpZINeJ+fRhVRAVMRNHiYP65MQg3UclpX5G5DGsQSq5cUykfapJEXBxmWUICTpjpQvqROPlIlg2muXOuKrozQVZqkJfGq'
        b'EtdlRRLnvbiTiMKxbURobjvsMn+kwMVu/heFdu3/RY3tMbVNdWWoAae39TFe8M30tpsCC1VOf1KWNUVUlGlK+ly/GvpGTFdE7JOmrEUi/z/rcsM63LAimsqcrrWk3Wly'
        b'upUq1/+GZSjx2pcy968uN44W92/6+scTD1asR6ZwyfOqjsuy+sN0jhUalub/9P5KJSsGs1gekVOzPJnaobrUdOCbqVmkaO1eqWg9b+1LIV5WbCLWoqcoWUw45QRTljfI'
        b'Z1/Iys+LOEVLzFStSNVltUrylWpVFKlV9k+LfV1Sqx7VoF8OZeUiYP+H47T5Z5Zqu/DPPaXyooWRAx8jw03lGbE/XFg3073o1pM+nvttdlsyXedSSAqL8EhOSYqJj3rm'
        b'FPiiMo/iXR6vf8dff6FsEUUPLnRDC245rY4jsHJ4nvA5AIWOnCf4mAkWu0K+yap68v7K6ZwAteEyVi6XRBIowoglc0CbwyQnt8phcTRR6DYi6I+Vqz+20TPGT/iJODmb'
        b'bvPOlzMvGlWD3TrH/yuoWdPh+4ICS03XlwQ6Fl5bIhs2hxvfld/3iu7fuvSlP/rpDzJ+u+dVz1fP3XvtdqjSjy68si8n5p2t//HKr7z/41v/9tK1kg+ywtsO/OKy5i/d'
        b'F3rOR87H6oxnSmuHhko1d3/x6Q9bz4eZDoX+NfOXl2J3/eBsWvbil4L47Vt/+t67UjnObJ2RZLKUSL85jbOEz27kuKw8y8BfGclqo8biWIVYwwfZ526Du7w7g8TauVUC'
        b'BPZFyeyS0LSTs32v4IrY7s4YI3bACG/droBSD86eHqUus6jjNFSvSjP5lxjGCnqunsqh2iqK7vEiFP2mYN1SSgrf5naJqjPanb7hMcqzetTVdHc1GVpBd79ZIWgiqtzz'
        b'VqspK0dUT9F3116YqBZuWUlUn780VvU0PSaRGWH+R0sjirm0bMnnvU8GoSaFRcdckRXSkRVsXVW65ylU04G3bcRd44whMZcS4yKYOScifPMzKaxsUY+XkaGvv06nD8FT'
        b'aZTEg0tMO3OQdVxlOLYc6MQrqLttVoQ5heopxmCHb8z49lAxl92dqRTL8q79X3rn5YmKUef221K5V7XCoiPjQs10fhkSHxkd6iZr1dXdpJgQt00q4WqupTncWEZ3S4bu'
        b'dj4cFtqfwslVdS9Ex6HNXpdDdS3sgkGG6tuh4TFVAduhkUvrvQCL0MgyezfA7V0sqpy1POQNNyfdL8secYV+BRgxt/3KjmGaIfyxLsFVMoep+18MU20Zni7XoVw2uz42'
        b'wuo6496rcXF1CcZHd3Do5UufGlRljWq+MXplCT5alSr6VfNkNRTkPDx8HT2kIg/+r+ZXlHp7VEGC5bNy+W1cThEX0c5Ztjm5i6MT3Gr4rTD435azvybVTtpHH9VVZKKY'
        b'okiioizU3fR41TZNTVWRolBHQ1GorkzX1yny/cy/lIgEfJWEL3fc0BJaxGsJjTYp8q2gWKCP+eNZ1DCT4UkqnvFOuSsnsT/1TzQ2gfakgHTYqkMJ2LRbE/JwGufW7rOB'
        b'rDAclrfDAtKqqxRJbbuLtzapQQXmwj0YgOrjx0nFgyooEq7HhzCND9WgwQ4noAzGQmASe33VRDgEOTh86CA8hBFneOhEd5Vj0TWYhl4YsLgOHW4wdPA6LmC3Ao5AH/3M'
        b'7oX70IFdUZettmODJWZhWzy04G3i1mPYdP0QFEMXFsKontPlg566ULwVsxwyY62xFBdgOuYg5l10WrcpZJ2jnatcgFWGhSd0BBiaQzVOHqTt6IZxpvD2YSW9ZsoZpmwv'
        b'mWC5VRCWqGFXOI5ok9RzD6qwnX7msDbYARu9rGOhNAwH5aEFpjAvAUaxElt8cBBG0i5hJzzMhDms84VKA2y/GIi10LlvLQ45w9xuKKG1V0LZmuMw7AM5O11pAlPYiKPS'
        b'/TCcif2noEFIlKcRb2ENNNP/5dHQw3KD0jaKVUihncBWKzPswKno/coHcRLywwwhy+kS3A6nN9e5w7w0zDFhkyOWxeBDbHLBOwH6MHjVHh/AGJ3UyCF5qD8l9aOlF8Md'
        b'yFXe4Yvj+iS2tdNv0+6QD83+tB93oM4Mp/cf3n5om442jp2mL5ozdgaakr7fp6mN+VgBk77J9G2luvIWXKQn+nAUhmk6IwKss444gA3noMkK5rWwVT3UHcqiUg5jljfW'
        b'bYTiIBtFXIQHhtrwIA4W10NeFD0+kEgKd72lIbaHbzl99tAu0tR74QF0JYcQ1NVio6+qwbn0+AMZOGF4fgM0ekC7QSAO0/7UYY8iLWaCQKoR249iiSLkn8DZ3XSStdBv'
        b'S6scoPlNQ44/HUK5+RGCiKKrMKa3Hotof+bwnvoNMc5jodM26fnUUgL7PTBBu3zX2x7KCOxVYR7H114/SufbfQKyNkIz1pur7sEhOp5RaBGfgK6wkK1SqIiWQLHRzV1w'
        b'f39qerQGCXqF0I49tLElicFnYGGtPzQehUYYhU7ICcFmE6wz3YEPcBamxTCihDXrcSpELhHvwoRfQNoRbMr0iYN+bKJ9WDCmRTAIGYx3PUCvaDGEJsz28qd3V/lD3T6o'
        b'h/xQQr1ska07VhGjoXvGsAf6MgMztTX9b4bucYrC5jXX9qzBQVppMYFyDmHFrb2EVoVOm9y2XdtBkFYODThgSUDeT8D5AAtCsCoO5mlNJ3AOChXw/mGsyoDWVFf7GBzc'
        b'ifnGpEksXt9ncRPyLij5wAP9jazcGHav2S9JwMVgHBNhxVXdkBN4G8aVoeSGM9RjtqETlAWwmkzhGtAKPZ4+flZhWjsMsNfeSVlHy2K33HprP0Khu25Y4EOnW499+lBA'
        b'NCUrBLts6Bjn4BbmirHKAypx1AibPbDIH/tgXLKGIK9ID9ppGYws5QZZsZ2FAlJtJtKuGkDpRhpvkACq5yrBQn76GkXChfFIrMGZ61Y6UE17eJvOZoTI1qRilLoLthrA'
        b'EN47exr7CRhycXrTeVhwdyWS2L0PFpW2QVUy0YQuyLONwPFLWOgPCxZcc5VznjC9nkCuH0u9ocrVZc25NJykIbsIFloCIZsQaJFWlm2F/do7fbat9YRs2vPJALwfR7vX'
        b'4wljUnwgB/Wh21jnr+DUt0RcnEPxEYLIQ1DOIJJmPmMKE6m22HxOQq+9h7fjQ+DeZRVCy7q9XmbQpRnsCr2HoQSnaL/msW49QdJDKKLFjcHwScgLJGzN3YILzocPH8J6'
        b'F+gI11TGXILY+yzSAW5vhUajKwTCdaLDMH9NYGNxEqsvppjSwY0DyURYBLOEOVWEck2hgefjiXa0m2FTLG34HLPqFxGs9kEH1GLNuRNEFhdN9c6knL8A99xphp1YgRPG'
        b'hBuVR7ZYXcUSHSWYWQmxhB+1XgY0j8k0zDFXugkT8RzFrFG/Bg1EKrvs3WzSN4fBiEfGdV3xBSco1oPsSFrYIr2gi+hSjs1hgt96hUtQCt1BUK1Gh9xrpAbV+7HBGe6l'
        b'0C3ZyFbSii3Ek7ohS0OEOYeIgtxfqwDT+3FWfweBwxjMWuFDnTTsiF97TRIdh1lwh/A1D2s0aKM6aXldOA/jXnSY7WuwKGBDNEFbDo4ehU7a8vlzO4kzDQVcNSTobbt0'
        b'CCuCiX/VSaE3jRCixIKOot3eikhcIcEl8c1zey7uxUrjWOzJPKaeThPMgSyC5XYYtzQyDg+BcSI306o6WI2zmKOKBY7QYuVL8ABt12gChVhuDJPQBv1Qno7tCuu30SbP'
        b'YadjwC54iM3Kjia04Dyij/eIaTcdh3GnKG86yHG4lRxAx9lA7LAV5tKx+ArUn1eIwNpDkU4WHEMvd00hVpOXSjShgu6pPeik54+k3l6EItEVfWgm4KYdJOCGlrOxNMtF'
        b'0ve3J7g4YqHd9Xg1rIw4o7DhAg6uI5WYYGsXYXS745rDSak/YmA9AuNbGKGN58SLeRw2xSnhiY3BcE8BG7yVhTDqTUSmjFCmHipSYExAxHbbWsyypA2uN8zAIQWYhc4I'
        b'J2NodIB+bUKTRgO6vUwdmxUuGcYS0DRqECrWW0nxoZ+FMzSdysAaQyhx2biPuMC0Mu3NQyxW8ILeYIYrIcLEc0wauhuPwzh3/gzRC0Z+B4gQkPyRYANN2kdNvbVwOAAq'
        b'g4/DrRMwq4n3nG4G0sbc25ehDSU+bgHQux0nbm5wCCbC0Ufn0X+JdqUfmgKvCbHW0RpmfHdnqDtgNqvHdziMmPItOuR2/TW023nYKYbFNVjlp6e5jrhekQ5UnHcL8SXE'
        b'XbA+ZRdHKFztD9UWkOOms0sHe+Jg4CihXkEs1OzAWw5CzJLzgtnwY3DHMQbGD3swL8UxW4cTN9ZhA8E+kcX7NF6+4BIxgHYclYd7hASFuoQsY7RV5dhsBQtQYoAkAiD9'
        b'bIe5TJy6fJjgtp5YXRnWHryM7fZEU7LCT12FPKcEwoF7mVCbuZYgazL8GvZG6WM9EcE2IhRFB7D0zBobJJCvwE4nEo0IqO8b7aN53KVPHUf3XXXSJLZ4fB2M+xAkTsPE'
        b'tT2E9QvY54AltHW5xPRa921kIlkSlEQa7WTQiJU6Rzhq0E5TzYKWGKgNXZN+xR2baZQJwqw6qIqh2fSSRJAjgrJU2vwSgwxaYhNx0H5inMn+0GaBLdip76nmQ7yiO1YX'
        b'2yLwzkk64y6cOwd3g2mKQ4dhiPC4wBZuI0P0Baz1o1fkX4i+wrgQZl8ywPFEIjBjmLvN8awyjqy3dDy1IQpmU8tFLPXEmBjPXW9awrIMYYoPhJewjGSIQ/tNYXo3jFxR'
        b'2WmrkEQibL3jaaw6RkuBe/Z0yAs08ngSbdJUsAUjQ/5bIM8acyxD4C4NXgQjiRmHVDe6wgIOh2IrnccQUZC6m5sgy/Q0nfkDyX5WwxNmTGyOYP95ktHu4EwEiZjMG9JH'
        b'THoSibLl3DTHGi2C3IJj5+GeC9Z6HyXuWhFxFBr8TEjs6IQ5OxqtjASSezCvQQh+F9o0sdcZyiyvYpW6+6aoS0TushUIR1oylINgZLvdcTf9QyzcbwDuqJtvkNCu3VXW'
        b'ssWJTTsUxY54azNtZNZ2Av37a9YTky+jdw6ew5zzUGMPRJwOEx8k+kRCAs4GEQC2HLhMNOsOdBM36SRRf4TOSehlfhqKt8cTq26CAU/MOYvt5+ygyM3MnTYuBwodYtd7'
        b'Op1iYkzR+RvQFSrFW2GQpZ1hhHXEryoDcSqJYKf2FPYHY4H5bqgTEaC1umG+PYHXIhH2wajzpJRUEPEuNNCnLZ4IxuoDhBKtCftp63usIO8wQU0nVloG6ETa2HqGQmcw'
        b'Pkg4R5T53gEN5e3W+3QMrKVE1idUsVD7uMdO4oaL26HZj95apUag9fASFHmfJhyZPQf3dkCXTjiOxtOATbTMuxcIE+4HRqwlAlQFgxYwrEKbWYR1UVC4CcbOJ17QOwJ9'
        b'cXTTIDREEoloEMfSrLJ8COAnrKH8ECzsJH47g7dv6uBDQRzzB9ZeT0j9CYPJuwJXBpLZ8RxELhBEXsX+COy5pkiEOEc7g7Yve8cGwv0Jw91aWK1JguQZ73RnqLi5aXtG'
        b'KuSF6HsFqXoT/+5gP5Czl0h/LRESeuwQE5uua6rBwFU61llsPX1EhXjlFCxqBLPiuLHEa7vlMCsV7/hGwEJGPF1qCmUVA4Y42QFIdpiDhRgC/fFQfcxN2oT3jQkm2glx'
        b'+n3jsfK6EZGGZibsRtMECi7YXdJXoScqiWzU0l4UuwcQvvVl+mSeib66RdUDSV7twPtbmNvw3OGr6rS1xcDwtgIexCce1oIpjRTCkOwkpgr7e1grbcORUA+8BbU+dMsU'
        b'3FbAPrUILDjFuoTS1/mJ0KhBSsptaLmKY0EEpiO7VE1diDY1xGg6xl47TGpT+wZCz2GiNMXrjSW0l3d2k7RZoacDNfFGm04Qng5swBknIlqlpJlMED+ejWc1y7Dq8nbs'
        b'2kqqbR/ezoRGY3OifQ8UaLAc7LJ2irC+uvlcJGF4NmFCTiohQaMyVFli2UVrbHLbTngwrr0mOZRo3zz2ncW+84QynZsJ/Jr3kcAybQ35+CAxHjpSSP8uID1Zb7cO0cq6'
        b'IySIjR/YyoqKRkMpSQxy2ONHrLKAoLT68EWc9DPAXAnU4HAEjXuXIK1RsDXtUOLZZF0vOt/RLSaEKnehMjwFmg9fhaKtWCh3DotjoeEg3TtGGlQ/SQk1SCr5aeISxSSa'
        b'NOu4qUOry46bngShAziUHhBHomKdz+ET+5hm1m8L9+2TTM7BNIFVuTuMZsToRBIBatAgAJ8wx45T152w2tGEoGJIbwtm73KL9SPqRHKRVJ5Pz8k1Fl3DBteTcgLhLgEW'
        b'XcJhLhEp4RyTNbF9KW2IpMF66OTTiXpo0yuw4KyrqUggPCrABjdd7oIDHdL8FUWWDCA8Ql+TKF7KvSztCgHSJMviKxYKhC6sJnMLNnHPJNFxF0gPYbGZkIukasGci6nO'
        b'YoZ4OC+lzarGUkKOxqOqtPfDN5Q3BSpB7QFvjRBt4kyVFgQS7bRTd5jIvgNvn3R0h7zYw7pSIjbTeN8gndhTG7Sc1LQPJPpdAc2hWE4yC2Exttowowvp3pVXLVIdoE+X'
        b'SXqZcD8iBPNVoC0phFCnGhYPQ9aZU3jHg86TrhNC5p6gj53QLSAKm++nRWJc0y46trtWZ7cR9GVvIIVg1CSA3lsu8KQxcyOIqA4TC66m8yYdJ+Y65FkQe630hYodpCuM'
        b'EVScZQX1dtB+DUKVLelKuSlB7vCQNYTvJDZRTMA1ZkhKUw7pZgW20uuQb00C3CxRihHiB/dgZDMJxD3QsD9i/xUxlitEaGC980XotcEHSaabcOYC9p89uRZ6Fa6nRrgn'
        b'BSEL6+hUYnYDqDc0wGza2H467Gyij13nztK7Smg/awN0YglxZ2gKFXtpqV2H1imfUcWWsGBO82oUY44VKTJZtCuDSJR00QpKxDgSYOJphbn+RNjaDuDIDkKebmtTYBkb'
        b'vVBxgOShclpPVpJeqoQgoCKZ1tAJC8cDSaCshiITaFHAgRiscIY7R/Aec+yUkPKyoLCWVLrNYVKH9TigCHeC4U4SIcuCVD0Ve8OSkghdurAqU42mW2hz2p90yEEix5XW'
        b'OObgdH1NZDhMGqux+uKtzsTNbu3DwV0nCb97IQ+ZZadQgzT4CcheB81BRAug9ojzWY/ApDNn9UggKiA+PqO3H2uSdlkTsRi7IiYacR8GzHVhMTUa+/eROlBhoo2NeoyU'
        b'E7/L332TsHRyL0mMhcwWJfWIJH4K07ugKYUAKh+mAyE/nlh4J/Qdx9pEvA+DrjdhMIi0vhY61UEXO84CMy8mVtMaGEUa1X0o36e3/oYpiZ8THkyZwMpImMP23fTPIi4Y'
        b'6UJtRLJZij7JXP2H8cEFNcxWw3khtFy4GXgcelO7RaxoTx6d72PGGSKmQ4eNjmpcwQFd+XVp2BZOyJEdSuR51CsQi1x0dO1Je1mEuiTazjwVHbmzQW7eLGHQeh2BTi0M'
        b'G2CXpb7r5oMwnkE6Qb6/vqd5mL0CcbYHp05zVpoxz000SCNU29CmzCvTCsbiiS61E2NZiMapVJiSwjAUHzQl1OjC5ngWoXRlDzQSZyMiX8FAtQNGTWBodwIJ/C12OBYe'
        b'yIBvG+S5n9ZjAicSwb5/RkhS3zzhdbYhodCoE/G6FokhdpsSCR7HDu3T0LOF6GsZNB1NciNRuyWKBNCco4zEjkJ2ZhzJ+euPkrzQYaDBrFtu2J2u5aAMfZfOE0Uu4W0B'
        b'yWGEBBUXt9PMiLFh2w0iBjOGhAt3SdWFbvcLgljMPxZHVKf5wrEo4hDj2BxBM6xKIXacQ0+QYI53w8JhOM5rH07oacLDrWcJHup18L69BdsUE+zVi8CZGAIdJur3kfow'
        b'n4QLF+QOamLDekus8kwkqlaije1apIZVZ5A0lQWLl0nimTgCvWs8jY9YbyMmfA/vBChim1MC7XuT8c7UjdIYXS8nrTV4T/tmqp0a5B0TeRDY9xEMFkLXDaIFbamnnaE4'
        b'kCjtLVN4oBNBmDlPqDGVeeYS8cx4KBPjKP0+QKLeTMgVorfNh6774/0AcyJMjdgvhbljF2Bw0/aTdDTV7IzpEB4SaWsg+jC4hpaxgIs3vNzopZ17oerSWidPGnt2Pe3H'
        b'nAM8sCcinB8kt+VIilwQp9+esie5/K4PFi/rt2do7FKo27OJqbgB3ipCmNTCAg8YljeHwUB5XehFooETewkGhm1P4wIUWcTYEoBWclaTvi3mRMaYna5hjRnkElUjCM2D'
        b'EdIN8GGap7mUDqsf5w/bQ68hNGgYrqOtL4GJcELXjiMHBdBrwDL1t0ODLWZtJmI3BgP+2OoHTVYBRHfyT0JzeACxhOHTTEppx7aApJ1y4uiDWLsL71/FQtJFtvpiTvxu'
        b'6Iw9Rmyhk9bbTYJrsyNRHJhxwyKzAGIcTSaEzLfNN5+Jxvv71p5NwoceBGq1xDpy9+goQmtsPIwQ+WqhEUY8FIjaLCZ6kuZeSdBSAp3ptGhiVuuwaxfcSSVkr/OIJVgi'
        b'vaXOTC0ecpWN7HDQNgbrXXQvwTwRBWyyhVn7JJI2eln/htMbYdFXsB9vqyniophmmee+FmbkmHWkwxa6onSdofbE+nW2pHUV0ZJw8ACR8XkCiGHCgGmCgoXLpH0OaNOm'
        b'N4SGMayJjDYmqloqOmcfdVkVJgOxK9bTIybyAsmqY+o0hUZit/3KOOYKxWFQd9pUD0jFuIWlsaohOOAL5dpHg89nYIuL+wZLrNyNoxuiz2GZtYjJrkSCckmLbsV5t6vX'
        b'afXFoZrEutrw4RXHjZLtUKvtjXlh/k4Xjrk7En6XHMI7yfvDcWYLEaQhVgyUVEP5ICINAyoBhhyFYYS7hrayPmwPjOLkFinhbT12XCN0K4MRY9KAitcoEP3sS/RfS8MW'
        b'h+OC12U6nVIk8aBCCaa0DlgQSWu5pn1TYyfhVgMRm4dmWBAELfsukZhCkmLqcRJpAo7SkayEbNJup8QiPRKoKo9qJEGnjnzsTiK5d2k5o0QQay2FLr4nmf4Uhg/CcFyN'
        b'0GqSVt9mdkAdKwzPbpAQiDcS+y4hMX4gnfb7zh5fJT8YssFGf4LuRqLbsypMJYd+Q2IBxFnKoEwXc30cmeSjTS8bDNoE961w8IQJkjjjsoElk2+BVotNhJ13DkLTWtqa'
        b'pmTiOd0RMOpvSHDeKPLesx46DGwhKxQKd5EEfIho4SY/6XqiElXRmKMEoxFJN4lt5cBEgA2xlPEIRsOLFVK8rKFXdR9tcTk26AfRJs1oYXvUWhxSNE63P3hZD+7ug2G3'
        b'6wRW94nvdWKDAU6luGCvFqtEQVx0LppYQbqyQxKdYQu9pGrL/hToPCCxxMEj26DnsDI2p+CAZuR5fehao3kZqtdiiWsUvSgbaswUrNzpPEnOoG15IDFyTzy6zzsWh7YQ'
        b'ZeglJGoO3oKLjkS56uDuSftDAsKMIkJLEsCJblXBlEok5u+140qeFjvAyDolIZGC6aBzRPPu05E8oLfmrll7hlh4KXQowu1oyLPFXnMi/gU3rkDV/nPIDOXtAhi/cGA9'
        b'EZRZyIvZSYjWrQ9t5oTlDYQTI6RUNwcrGezFOT2o893vmuhE7LMHenBQQo/cgnEjHVvSOzqgyx765AwJl5phcftaA5JkS02w4jpWsK0pTIMxceKOA/Rt5UFo33kGZ4hJ'
        b'Yu2abQe3Yct+qI/wJ7gpwNokYkoLVwNxeM9BP8iJSyG6WGMhsIGukKs6oaG063HROAeloTBymWTnSpLeSlk/Bjsiq7nbbEkvnMH8JDtoNnSNPESUoACLMsxpf8dUhQR8'
        b'fapMNKazbAhPvpoJDzzp1w5odCMdvRWGE51x6AzHFSdw7mDgYagzJo5JKrDTIZxwIQFuWCXckiS5+gBCjkWFUBLXsrbQ89WpEjFXC6ObIJhQKZsgmuHSAs6ZEjWuJwCd'
        b'ssUJfZJ2/bFaOcYB+rdhk8MuqBQTf7unxu44pBlDeuN8RpSzMwkDOS5+tkaYl55AEvYCdtsTCIxBqxLO2yjEEd/pF2KbD85uz4Qs0gDv7HDUUPHB2nDOuzbIbP03M6AG'
        b'ZplRqwNmvGmRhCldzFxEou596HLWxYZr3jvP7qLl3cG+g5h9k/SvSUPijQXnoNWPpK1Jc/noBCt9GHFWJtQfYEWzrWhz8+IIDRY08N554ofZOELcpcwSK9Yr0BrvK5nj'
        b'0PVokgDzQq/C7UPElMvgnhjH9JWw6bS+oz7BzICxnOYGfHDEDyrUjyoS4ZzFLCcSZvoZUduLQwJi33ewfLd6hBfkBroa70+JVcYFzTPpO4nGk1x++JIXlCditZUPqdZM'
        b'DB23tcGx6OsEJYU7YWSNnSthcpsezCrDlP+1OBPs2U60a5p0u9wLOHtVGfNO+BB25JJq0kOUp5LUls2033Ub8a6qsjhSD4vPxsacD7LGRld14Qld1gUQKuWhao0eYV01'
        b'TMeqnjTdhVMbmQGUmHcWzK+DaebD6zbcQGpfSeiRQyTCt+yh7WiDoQ3m8VDptpVwo4y0n+RUaNhDx5B3EicPqpAQP0eyQfOJdD1sV70hRyuocoRGbaXrhHZV9FslLJrG'
        b'B1+Dls1ErXO09nvCpD40a+47pJqGt1ww1zBIAbt9oSoaWqCf4KjMO4AZTbE7lRm96OjniACPEJ/IwU4LLLgRtJlYNQlBp+neux60mFtncCrdgiQzuE9IU03cukAlIDT1'
        b'LKFlKzB+QgJppw2tbTETajZiVQQLIrhMADOYps+qlWRi/k0oJGJO0sctf6g7TEP/jFmnCqDZZBkPjjL7VPkZ4sRExmKPGHlrbMMKwoEz2zLocrNBVJiSPnYa7N9GB7yI'
        b'Q1EwoOAcTINMkZR0X2SDU+thEbv3xarQinLxXgowJ3D22YNQJYFafaLn82nY4ArtYvrYBbMRxHB6bhB5LCd0qqGzqFTeiB0uRE77aetLsOo6LsLcQR0stIE5c2zf5o7F'
        b'cczZdZIZrMK9aHNydxBhKVSVYF/EOoL8iWtGhOgzlp4JBHKd2lY0t6rduli7dZMUm3acIKGBsMOBgGFBJxonVbHxwGa8r0aqY+45yHHAmaPQr3SVCEw1SUB3iD53CAjo'
        b'Z+XhrqEz1KmQgnB/twa02VtCgzXJC7n6vmuxZ+seeXksOOWAhSp4y8GL1OI5CxKy8m1xVCMRJ3epulpBuzVW29sdpU0Zh0YJ4X0nEfy89GAjTZa+NUOkYAayjQjUB4Uk'
        b'mt28YknQVu0NuSocUMwEEQ1fvLiDCEIz5ifQrnUxQjC5m4SP6sho6NhP4Mys8NVYpIfjNqTVVEZBgTy0RxtBjwSGD9vhFFPQMesU0a8JtzRi6Q+t5Umu7oASY8wxo40Z'
        b'1oX2TKhbQ1BZsIU5lOWuy9tE+dKbaw6qYy1JD/JpTAbK0d4bT/oeyfO3iEZUQpc2NhzXg2L7qyy8woc2rxFmL1zZDn3mMO8IHVI5aNhMQlaTP/ReJJ1nEDrMg0gIIuZt'
        b'Y5ewB2Zddl7G9u1Q7wJdprtP4LgccZa6k5uxlnUksiQ+18uQpMFH67g1idn9Frjot42oW513sHpQpu+6AIKdAsza60Zj1G89tOloJmtgVHARe62hQCriCiNpGHgl0w60'
        b'QbnGUlEcOtdGLuvJfaOEK90WeYIr3ga5VlIxnyZVmujihfdcmV1pv4CZynQ5W1QEjhHJgVJXViFCuJul4U1jPp+LNesVHgasMVGhRCB0oIeOO3MXLIlB16hhzrKVDLr1'
        b'aG5smA1wV4F0rhlXVozWii6Jr/LFnMqIYudg7TEsdqOHbAWEJX2y0jd6cbFQHvfIsnYcJmT9gkmWu78liQC8WEoPeQqwXQ3quSlI07E/AGuw2J03rlXuwz7ugjvB2sxJ'
        b'HFo2xsVAllTI2/ZGtuFAEs67utDLTIlYJMlxWyDHbG7QsW+lPW4hQSp05DrucHlrmhasrNsbOzUEwXF2p0wFUr7m3LVQ9nW0hrwg2Exe34UvBfTHMDF9+QdHdUGwauu+'
        b'EAELM3Pk3sYlusUUbHIRJo8Qtaq8/u+Z1Wc819vr5Ealne+VV7U4atyV89HC39U3b1aq2JKdMnHq1m3vf+i87Kr7609+Iz2Stalp/Jd3Cq8VmA3/vSV5scH6W4tzN87N'
        b'/iD+dcvgc4E/+/4/0+oNvvXuW3+1H3V89e33xLc3/PSM1/2Hzt6bG70LBj9f98XQYEKdnPjyK5/GNPc2TbT9ozzDf/epX+g/TG+LN3k9Z828ocmhX5v43q8581HZ9amh'
        b'Y9fzhrdcdxwOfcv8lanC2B++98p85Hyli4nTVK7kt5/88sKh1/09//3gnfQ9Xr1rfm06UB29rdr4M3fn0aGw893/3GM1cPGyx337v/WEv/m9NW89uFdVt2dS8+wbLuaf'
        b'nbwm7XOoqrr825CDDus/ytuwfcdfb3yR+NbvP3xQ3oY/TTP7fsrbk9pdb2/9p/dWpbFrvXWWDcEtBgGVG34y/bs3Cg17m8Ps8qIe/O4Tka3r2U4HO7HNro7mcefXvtse'
        b'V/ne5O/ezI2v+unhkz/+vGe+L2vf/vHtflYvNx/6MOJMwhtr377x3qbSwi/e8BwO+v75thndwjcHf/49v/RPzn7iZ5lW9Z1NPh/+5a3vjX8nVJBjGPGG5UL9hcm2P0+7'
        b'bHv1iO/Zlzu73t6TEbfT8vbB78yvTzbbUVDz5ptfvnlFnGd57Mq24I6XbwRqhf73697/LTSwcF0waWpM+Dfjb79a/tFkfudrR/BeMpaFGmof/Knqf7ocuHvho2qpXXLK'
        b'DstvfeFVmvbD/mvW3ZY4K+2JtHSyKP77gEJEQ8bBcrnPS19+93s3T+81c29O+MnPXOfWFfuHtmy/u9Mw5UjY0N/e2mDS4rC195Vq/7euO46NvXbKyv/byk4Bf3Sa8fH/'
        b'1rofj2a7x4V8sfnWho9DNb7Y/1LbUPnG7/XvL7P5UX5QmnzZZ00L1ip/DMz58tMPDPyuz+3V+1HrG29LPL77Dz3Pf5yaN/uzZ+unO6/6/Wbxxvs3f7FPPrXv/b8FPZw7'
        b'Ndv8kVSZK8ahG60bspHQmCckZVAv4jKfiHCVQclyf4WACyv6KxRac+lrsaRYzD/eIEEksIVmPnuNmF8WdyNRyDbIV0lSU1IjDl+skZSqSlx5mjkJxQLDdIniRln7Nhje'
        b'h83L96XhVNplNXkiIYr6R8UwpBKTspPdlG+sn3xF9XIqTrNqZyUaimrKOKJxRU4gVSfCPSUhNkrsMYVFphKNIgntaXdD6dLrt+xyl8jDTDIMcLlpllgID1WwCSeW36uI'
        b'3aJdMHomhet0eMsHh5KhVPEyTZJVnyt88pWbDdxxUh4exsIkN2Vc3KCxsv7KiuIrMK3L1V8hkWX2yTZt1v+3Yaf/5/9IDTki+/+Xf/jO2UFBcQkh4UFBXBz2Gyyc1lQk'
        b'Egn3CDd+KRKxPDQtkaJYIlQUy4voR6wup6WlpaS5UVNBU15LWUdbItI5qb+F7r8psGY1SfazuGyxRMQ+b7xJ7xLqbz/OvgsSCQ/yUdthIqEd+//M8jfy+gHr7DXF6mIt'
        b'TZHQ7KZgq0h4nL+yVWQiktJfU/o3SzAg4e4WmXHfsJ8sQZeERVp/Ib9cSlyRq5jy6G+S33Lcszjp52zhj6K/rf7vgeL/DBiF/GZwcdhsi0wZALD+FIK3E1f2pGKZTxK4'
        b'a0saRjmWs65h1z2hEMoVBOoG4g3HcSRmxBb/v+KuPTaKIg7v3W57d7220EJ5h0eJ2vZoKW0qBYEAta3H9a4iQnm6XK97vaX32O7u0ZZHFalAiqVFCxRDBGp5yqPU1iJV'
        b'xBkhITFgQowyGqNBkQh/GI0mQILOb/YKxv80JuSS725vdubmsXvzzd1834/Xxpo4rmBWR0FLqYefN7T43adKr351Izd5VFPbc+YmW/q4zXHdExqK+kfurhhxp+387RE3'
        b'S8ZlFDUVfX4t8fjF+4cqDqamOe8dqCPNu35/ovDbT1cM9OjvC4v7ooUF+gehW7Wl13af//V6hWl91g/os5l5L0wbyPIeue6ekResreyovZr706nDjq+P466EB/d/vHzq'
        b'59pAz2ltPz/v9vWZX26caDleNenW3hHDti7B/YG72UdztIUDFcuXTu2bOvbPa/X36tbltU8uuPlNsFjtXHv2i5Udavz8Cby1vTu3qSXlkvJdZfOqO59sbt0oFM7dVjTu'
        b'+1EpHqV5lO2KssO+Mv1i2vKzl5LCOyeVjq27deDC7PG/bMtZ99uytIrL1Rf+uNTYqTywO46tqr8SzJzAJqIopfvngLSWV9eWM/8IC2dHPWZ8lPLFI4Z+uzsn4CrPxmfo'
        b'SeWwYR2flVLwhzyddU4gw8YJtRfDlgAYDxD6o9N4O/zcQ0cklR+fizYZWu19sFvQ5XRnuetRn4WLF8zWGnScpdXRhV8b7oStslMpR13E0dXJSbydTRnaaNTqwDsyQB78'
        b'ugliefbbcsx0OdFlZ0Llag8+E/Pt4qrRgOAx0ZXTK6jTsLSiq/TdsOee5qYcei87K5kybQ/qwl3ssxvp+81GzHU6p7YxfTnuD7HsfofdKNrtxC2ZToG2FO1NxW/y6NxG'
        b'tJNln2KZ51owxVOQbwI/hh4LfsMcjzZ5mLAttxDvcOWBL5zLMKyYjnuHTOKfiU8woiTtWYtaId3pjvlZ9KCOZHyKn9ZgSGXwgZdhdwNEq2vluYp0YaEJDYzMZ2nT6ZoO'
        b'/hdqcU/huDxKCaaZ0InJjYZ33MeLShzZuIXSDrQrTwiZKGnfl2got48tnuUAT4cykMq1DXe6acsFbuxGAb06Fw+wajvgryk6UHMywI/DDb1uzzTjNs4fcyCbjfdoTrfJ'
        b'9DA5wWmmnb4T79fTOdCvH5xvxz1DcB/4iPYruLeW8pKkRFq1cZMFC2payT7mxZz5Mee8OQ7oAY5eeW+ZcWc4hTUijLe9PBizNXm+4TZnt+kQaRm/J6S50MkMOqrN4GvS'
        b'TLkHGCmWO1HLVE92ZjxXWmzZsBafNfzDOumSvs2Ou3EvuHHvpNnT8GHUbWb9OAZvqoFt1O6y8onoozguboMJd7kq2PALNU5IygYXbm32oLZoTFRAW5yo1XCO2wL73mhn'
        b'N4OhYZmZQ12c7Ukz2p5ujg1T62rHguxS/NoUd3aOiUtM4xPQIRsrfiitUo+LjoYrh2amNw+tuBX1Dsvn8dtKPhPRN9IF/Tsgo+pDW7NA4gljgdtAzdFeqINBTE3taNSb'
        b'5YBlmovDHQuHDsYVynj83+n/08ww4jEQkUdBeRWYgpKtTAdvZY/hzAXNGtNgguYL2AU4j6XGvMjomXz43+vHBh+5hqSKcYQswgelsLqGTmckTo8qQYkIQVnTiVAl+yhG'
        b'FClMeE1XSVxlgy5pRKiMRIKEl8M6ifNTLkWfVG+4WiJxcliJ6oT3BVTCR9QqEu+Xg7pED0JehfDrZIXEeTWfLBM+INXTU2jxCbI2GPaexCvRyqDsI4nFhorR7a2hmRMV'
        b'VdJ12d8g1oeCxFoW8dWUyLSStsr8p6UwOE2RJFmLiLockmhBIYUIJc8/W0KSFK+qSSJNAik3SQlFqmZMN2JxiFVytawTi9fnkxRdI0msYaIeodQwXE34pe4yYtcCsl8X'
        b'JVWNqCQpGvYFvHJYqhKleh+xiaIm0a4SRZIcjoiRSn9U87HoSMQ2eECbEw2D1dQj9mX0d4YKtsBqLUAYYC1AA4AOUA0QAVgFsBIgClAJsAygCgAIrBoA8AK8BLAGQAFY'
        b'ArCU+c0BgOpQXQewninoAJYzfS0AVEwNAdQArAaoA1gBUMFKBpFdPbzaAOB/KBmEC8n2kEndXf43JsXS7ln99EqRfIEcMlQUY69jFPzemNjxRMXrqwGfMVCxQppU5cm0'
        b'MvEfsYiiNxgUReOSZfJAkMGReCNqqXoD3mkcpLz/iHFMrLPouEeD0hxQzjHVnQC84L/fOouHMxvBvwB1aAPN'
    ))))
