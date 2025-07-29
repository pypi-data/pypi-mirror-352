
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
        b'eJy0fQd8FMfV+JZr0p0KQg0QcIgincpJSHQwRoBAXUIFsCh3J+1JOjjpxBWKEFXASQjRezEIMM100WxscGYc2/nsOHHiL4kvTpzq4DjFcZrjJPb/zeze6VSB5PtLP412'
        b'Zndn3sy8eW3evP0l0+2Hh78Z8OeYBonAlDPVTDkrsAK3hSnnzPwpmcC3s/ZRgswsb2JWMg79Is6sEORN7GbWrDRzTSzLCIoSJmCLTvnlssCSzKIMba1NcFnNWluV1llj'
        b'1hatcdbY6rRzLHVOc2WNtt5UudxUbdYHBpbWWBzeZwVzlaXO7NBWueoqnRZbnUNrqhO0lVaTwwGlTpt2lc2+XLvK4qzRkib0gZVxfn1IgL94+FOTfmyDxM24WTfn5t0y'
        b't9ytcCvdKneAO9CtdmvcQe5gd4g71D3AHeYe6A53R7gj3VHuaPcg92D3EHeMe6h7mHu4W+se4Y51j3SPco92j3HHVcXTEVGti2+WNTHrdA1hjfFNzAKmUdfEsMz6+PW6'
        b'Er/rVBhHGJEqHV9Q6T/ULPylwd9AAqaMDncJowspsKrg+pVRHEPKtIsdmt9PMjCukZApQ3dluBW3FObNw824rVCHDyTgtuyyomQFE5cpww8Tx+h412B4cjy6ZsutLM9O'
        b'yk7GLXhHvpwJxtv5ghp0zRUBt9G1CYNz4aackclY5J6NTgr4sEsLdybhO+hYIn0nPxu36bKRG22TMWF4H49exluydZwrBh7DB9AmfDo3LR2eycU7C7MH4MtyJmQEP7Xi'
        b'WddQeCAO38fXyf3sfHIb38CbCAxX+bHo/FKoZAip5EHiKge5D43hHSyzCN0PzObQ9UZ0zjUK7oc/g5vV+GYIvu1ALfhuPUB1Cd9agVpDghgmZqRMiffO1bGuQaSq0+hh'
        b'EG7Ny8E7eIbHD9gs1IGO4ZNRcJ+gQ9xqfCYXXYmH4diei3eglkICFWpLKUjWKZi5+DzanqlsRM+jk1KFiagNncQdAFleoRydHs/IG1l8FrXUeBs8smFDYk5yUn6ynmUA'
        b'rBc0EXwgvovOwv1ouK8cFJKYlZSAW/JIz2JHqvFuDl9d21DJdlts6V4MOE4QtSuaMv8torrj3Tp3gjvRneROduvdKe5U91h3WlW6hL5scwCgLwfoy1L05SjKsuu5Er9r'
        b'CX23dEdfAvyQHuhrENH3u6OUjIZhFs6JNSZ9OP45hhZ+UsUTnF74syBj3m5mkVg4ekYAEwp4t3CZMe8nWbPEwqCRcgb+z/g8z6gZaBzIXGSsgVBcEj9I9pewnxnlzM/j'
        b'PufujL22dBNrDYAbuxuOsNeVr1UFzjCmfWhXDuYYWmzS/zlkf8iKcnnRz9ivFk6EVeJhXKlk9s6ge+gFWEqtKfPi4/H2lCzAC3SxNB6fzsjJx7uS9NnJOfksUxcS8Aze'
        b'gppcs8miuYx2qx1OJdpuX7nC5cB38XV8C9/EdwC5b+OOEJUmMDggSI12oWa0Iy11XNqEsePT0V10XcagB4sC8BV0abkrm1R0x9KYm5dTkJ2fi3fBQt6Bt+OdZfgE4Hcb'
        b'QBSflKDXJSeia+gCulwMFdzEh/AefADvxgfxPrx/AcNEpQaFoS3OLshEpkAJf1Fe6k2pHl/FS5PNNcOUruNhsjk62TydYG49X+J3LU12TW+0StZjsmUFdoIFlgHZ35E7'
        b'JsNVDM/lmha/9t1vXN994+AI+VuXTAtfuxf61qLXbu1uP9jeZGEdysogPPNcwuCkyN1ZqXz1FCanNmjI1p/q5E6yavDZzEyYle0wLLCOZXjbmsksupHucBJEQ4fIkCTi'
        b'q2iLHkatJYllFGgnl7wEb3ZGUXIC49SUiDscyfFZyRzcPMolPzOLVrwuE95E5/CNZNyWN1bOKMpZmI8z4c5IUvEVfFuOW7PQFYbh1rEh+NQctDVUx3q4eJ2Ot5Pu+iUc'
        b'JF9GTKuy2xrMddoqkY/pHeZ603QP77II5L5DQQZtViAbxtoV3pd0Mk9AnanW7ACeZ/bITPZqh0dpMNhddQaDR20wVFrNpjpXvcGg4zqbg2uyIOxkZu1ykpD6CDo6CB1m'
        b'HoRyCpZjFTTl/sVxMFUs8xXJuUjfovBOdCcROs0y1fgShw6zsxbjTXMquV4wh07udII5HMUdWZXMhzv8E+NOr4QisAfuDCyg8KVHo+voElD4POgcvsig83gbftUVBreK'
        b'ns3gAnKhnNUx2I0O4MuucDJbx5biezrchDsK4ZacQbdDpog39g4fE4o341ZSngksKgJdp22gu7BWX0EP0U01MEJ2AIPux6A28Z0dQLsfZrKJ5MY8Bh9D50pdBFDnSnQ5'
        b'G+1M1CsYdhGDzyvwXvGFS3gzemg34n3zINfA5OMms2sAwb7b2agD74PZSUqsYJImaHQBtHwt2rRwKow23lo6ExJ2Iq1mIYcOrCWlL1SgY5Dil/EhegOfrMJH0X2oBh+a'
        b'vAESdKaejsawoegqpuV3SxdAMnma2LedK9BNdB/GGJ9AxziSnsZNlMnji3a0GdNbr6J7syDFJxrEOzvgxll0PwQuTzlSIMEPxtNuoya8ow6fAcjU+JCCUafjK7QXPN6R'
        b'VgI1xQ1FbUycC22ipcYFyI33Aeqk4p3PMKl8DO3CcnQ/vRpW8T58CG6hXYyBsbvIAh2HLq2B1Yk7VrIMhy8MR6+yo1bgB5SGdCFlnD+1IeJMNdPILAldxzayzSB02mWN'
        b'7B5uhYwgG11ZNLnIeTh9qoetvMh2LlS6ZDyB06wWh7PSVls/fSHk/0zacBFE1wETOJEriTBUGsjC+2EaW0DGKsA7dOgOn5aGWnPRXoBbjS8z6BWYqT0KNSDtTYXltRXP'
        b'yh3NUE9iY9XotqnBKDV09qo4tkJ1cnNH/eb9zvYtdVtqWN2BJZte/zg4/G/5LfkT0wuPVq+esG3pBdmNPYk/OL7iXfmQKfqH+uYROXsHnNtV+e7i0UO/8YPUrOf2//6W'
        b'6fV//2x0bHbcoX8PyuDT/vrbeY++dWnhitoXVgz8dNfiA4v+8NN9D/cd+vijh1eiVv2TPbczbuH7a4GMkoFGV0tzE2XoVb0Ob09igBBe5tKfw62UiuIjoRUguODm7LwC'
        b'OaNGN7hKmKsT+Di+QSklyEDb0Rncio4EJYFwBzxTsZQbaV3mHE5ubiqPo1wTbweJDbegyzlyZuA4fC+Tx3sb45xkrvT4ErruR8QnR6ObQMRz0M0etFQn605cu02c2lxX'
        b'aRPMBkJdKV3VkqnLkrEyVgW/3FcKXgXXgXAdzIWywayGjWbtA/woLuvwBNbZDA5QHWrMDjuRCuyEGPWEhbMTdLOH+QgtqSbbR2hfCuub0BLZHHego3hHN1zahO/LmMF4'
        b'r2wVDMbLjyG6lF13IbpPzrCrn4xhB4jS2ZdLwxgiYKdOP1qwoSxMlLkCJmYzu6EsNeI7FblpNmYOLa3IDGVg0CelTnh96d3MRvHRCfVqBla6KnXCXEUaG8vQZa8CWno1'
        b'HW3Dl1KhPbSPqajOtrR8uFXueA7ungz85afG3xprqvJM71TFH3y08fqRm89tF4oPNw2aEh2ZmiQ8Eh4Zk9L4m4OmRkelRR7LEIoXFkeXHxmVsWpt0rbw+aG5x4kE8ZJC'
        b'4BZNKAHJQcGM/FHE5rfkOo6i7UJ0EO1LpIwfnUB3ReaPj46naLsMXUTXE/XZSQk6PQh3+CK+hlsYJlorW4puoD069smwcUBljblyuaHSbhYsTpvdIPH6YDLe5dEUJ4Mh'
        b'BQwM98NAvtIieJSVNled076mfwQktNke6UNAUssiHwKe7wcBiYqDruFXBwDyZYFChe6OQzsL9SDKtiThlhQEaxEEgGfQMQU+F1nYQwfx4SEVG1nAxE6xkaVY+B/qCKQb'
        b'o3tgYayIhaY4ioXxqxXGaUdNORLC3c6gCFeUuMGYVPbMs0wpLT2YTRWC+uH5RuvE+SUiGg4T9YnVH4E+scmWKRbenq9hACGidUuNmh8xkj7x7XHhxCIwIyTX2LiCXS4W'
        b'LgNFdRK0dPM542IufKxYeGf4CGL/WKhZb5z2tXKyWDhz8mgmC1qflG/kNs6cIRa+u0DHFEFhpmCsOBZfLBb+dWkSAywm6/US40zl6EFiYeYcqgxlLdYa83S2GLFw48RA'
        b'sobiowYb86Y7osTCXyyKY/IYpmas1hibNlRqaP/gBKYUQPpsmJGbGBsiFmqrBzGgyWSNqzLG/FqXLRa+o6e6VNaOSqM1QfesWIjnhzCAQKHp04152mGSKmbgBjPjYLG/'
        b'OtjYmBO4WCycsXo4AxiwsGaCMUZZPVQsrFg+koibofd548y3l5eLhUxjFAOMZVLzGGOMxakUC69mpzCLYTw/HGecmTLAJhbGTh3P1MAcTc0xpgVHSN2MGZoOmMDEP9AY'
        b'w8bl6MTCW/axjBH6vmW1sWLQ1HpGN4rKGBWTUFs6g1sKGGYsM/Y59KIopxwYiu6my/A5fIoYUdLQ1dli+Sm8uSCdQ3f0RLNOh3X/UJRU0Ma8dEXiHBBCQAy5jU7RUlgy'
        b't2PSWXRoAsOMZ8azsVTSKluNDqbL0T58ECgdMwFdnkOL09AO1JHOow5oZyIzMQxddoWSOu6umJ2uVMH8TmImrYaKqZTYii/Bk0TwOsYwk5nJCyTx0YovgnbYIcM7YJqn'
        b'MFPQRdwiAt6B74Q4ZPgCTNVMZiZqwzto9UHE5OHgnoWXZzGzDCMoKLh9Km52KAz4JFEFZo8CBZU8G1jjcLAL0QnAOCYTb5bk0hto7waHfHksw8xh5hhANiSlcxKHO3h8'
        b'HYHwMpeZG4qPi+NxNWmGQ6kFEQ/QPQsfnkFbq8MHYDA6mFrcRhhidmQ+hRh06DujcIcMhvwhw+QwOWEbaHnuShCqOjj8ImqCDJM7CD8Uhc5T2aC1dShQGzrMAJbn4WO4'
        b'g74RX4Hu4A4W5IbLDJPP5CO3ijZcCDJ/B+6QT8J3GKaAKUiQiQ1fnwfD08Eno23wDFOoQDvo2BajO+hl3KHETQiQoogpQpectB50Q4ub1CAqE0DnMfMWPkPrqUXnQ9Qy'
        b'4NsX4F14ews6Lw7jekbN4V2w4EuYkhH4In14AmifW9UK/DwskFKmFO2XEBG7ByC3msWboKEypgztQ2dEOf4CvoaeV8tD8X6Gmc/MR5uQONEg0Z9MVPMutJEBcroABMmD'
        b'FMjhqH2SWokv4z2wApmFanxDfPw0bm5ErUwmyHXPMc+BdLpLHGV0fAVqlY3FB4D3MOXAxtwU+JyEFNTKOfWEcywqQW3WL77++mtXLKWe0e0FxrwXCyzietswfCJjBfql'
        b'ijWGZS13MJaFLfm84z24M+rgxtpdUwv4jNDZL1ZHDvnzWMU76LMbA4e/diTltSBV0qi3ns/avTu14PDIGel7to4TYjYa/x4c01wSiidpZ0b89dNTvzUfqjX/6FWDpn7B'
        b'/2z77Jr+wrwXzweUmdpuN6RPePTdb3Zk70q+84Hp74YfVO9i/xlT/1boL5uPVhaojtvfmBw1fN+oKd9auvBl1y8vjLv6u+K73x9yaPHn77137fYXOw7+7xePFlUuXn5O'
        b'2PXH906fDtmw4B9nExLnt/9uuPzfnsZvlzV+3BA9v3z+dz46t/fT8Scurf7rH9Yzy6dMPnZpNIjFMZQ4sAxuTSogRrldSex6dBbk3xc5fBU1makQEYUPxyV6jQftoFcR'
        b'GWIf3knfjojDe0G8A106H7WuSs4h1tMwfI/HbuMQ+nY4uroS5N4dudnEkKB4FjVP4gbh5+c7gZ0xg/Cr4xzoSlZBMmi4t+KJgRXv4pkBeDcPKHA9SifvVfiQ9SYp+Ikk'
        b'wZJI4qo0EEGZyiNJhEALGlYGEjHIJFw4S341/1IoZCArRJMSPhhklVCQmzXw3x7lrVPHg7TiquxPSGHt0d7G6XsC45VPnu/HEkFkgDx0ZTJo59u8IgrIJ/mQEGlZzujw'
        b'RqC4owc8RjQhxlHGTzRhn1g0eUKLllIUTQYMCiJCRHxq1fTpn4fGSqLJ2PWS2Bt557mWfC1DF+IC3OJIT0UXSiShV4suW8rLn+Ecs+Dmpl+WfWosf+367vZ9F5vamy4e'
        b'Gbt17LFtl9qzYrfqot/KNRWYasx7ZTeiiw9nJK3YVr4t+I3BilNTDlpPDX43kvnugKBXDC/pWCehnoqF6K6ImosmisJtGXrFK7j2gyCDRQRxOO2uSqcLJFeD3VxltoNe'
        b'JSKLhozFBoZTASpQ0XWQHzLIHPBw/9gw2IcN5MXNPmzY2A82jCNrcRvwjws+XEjR6xLy9brknHzUkpKTn5ucg9vQIU0uqKhoD9oeCJpU27DHIkdXufXJkaPH1oy3ga7I'
        b'oRBNVvgij15SE6sFUOvr6B6DjhSjMxRD6irGUWln2Qxj8c1pPDPHop/cwDkmEoKd9+1PjYspKtxoWsFWBrqm/HLmG7EvBZ8LfqPqjfBz1oOxL4R/bNwWrAh99vCm9CAm'
        b'eIc6LvaQpN7gPfgUbqcIMBttlGyb+MpKqtIPm5Pup9xQxQbtl8uW4msTpJnsGz+iu+k0XbEjUMSOABUbCdhhH+KPG5WPxY0YH26QF1tIhcMobjD/6Ac7xsITS2LRST86'
        b'0anHUNyYj+4DehDcWIMuBuBmdEvzWNWa72bP/C9V696Qg2LAhTHBRNqe1PyM0XqRlcTlyDDKfyftmG3MO1O4QSz89WiqvRgjOaPmF3PXMJaOLwJ4Ry7cMfzt9U+NvzO+'
        b'VVFTddn8yHjBFF+ZlPbIuPC1e7tHAP1g36r6qSbHtNf4SOC+9452ffsS5SylI7Ak/cykWXGzRhQVUrv6PHOoLWQfoA81jR/Cd+PRi3n5SRwjy2UrMTC3ofiOk+zUBWXh'
        b'/cAV8c5yRUphPm4ryEaXZUxUsWwCvhj/pKpxUJ15tdMguMwGweQUcSdUxJ3QQGA+1FgDyrF9qA+DZB4ZedQTYDWbBHhrzWOMMwRz7MN9GEUq2uWHUX/uRzsmpg58Eh0B'
        b'lttKNgFRS6EuH7UVZifh+/nAfEbjm/JydLi4kvebZbk/Es0UkUhG9+fkbkWVQkIknhrGZYBIPEUkGUUefr2sxO+6P+1Y0QOR5CIiTbGmUeaq5RrS7EFrRJxRDpERRNIa'
        b'UzZYPxrKM5aW9EGcowLunI+4PXTHjaCNqRrZRyuLUzN+8K3gW/t1oc55OfdzKu+ojlXMO7F0w5TzpgdboxTfPK2d3DD0dzXj/mGsHBj1681zww9d+PClBaO/0xZ34LO5'
        b'n4cvGqP8elv11w8HyXOPrrT+RvlM2aChz3KSbVEOAvNhagNUEjVnO4dOs2W6KCfpRJhtId1VnijuK5/EJ8dSAqVrxEDqYQm34jbcwheyjArv4NCWRHSPUrcR6CDIy624'
        b'OSWZw0fwUUaWz6KH6pG0wdEY9C7cmk+Ug2rcBK+xc9HNsv4EJkWft7rjraba3A1tB4toOwhQlpOxRE4CKYnjOBUX9i+Zwq71IbCcIDBgLcFJj6LS5bRV+dPDXlcMIHYs'
        b'uR7RFZlJpUf8kPmTyL6RmbylnKLOLUzuRGPA4TK8Zzg6LcPHlPhS33xyBiMJUWSHmamS/1/wyiD4i+iBxcNFLP5C9Tazn2UmjY4yBqyaEClicVqxlthYsi6sMDYmlgli'
        b'oTyO2i6K2o1GzY2gdLHwfxZQI8nChqHGvMMmyR4ywkDtRqs/kxljuGLJoGFXxBBjTuqypcaYH6idjJX0+e04anwwLswyFj+/ij737HwFscXUPBdrtC6pbpA2ppfGE1NO'
        b'UWOFMfbDgRJ9TtdPZxoByvfGGcPGDZ0mmYeencashtd3LTTar6/IEgtnO6YyTpAWIwYYi63q0WLhwaHUQFNjqzI26rmVYmHROGoe0lYZjLEX4paKhQN01OK1cMAGY968'
        b'DVJ/qmIyABGYhTlrjWHrRkWIhd9IpMt/xo1Mo3WfYYpY+N6zVFYNrSo1WueUjxMLf+IYQuw7WbsGGhvXVk8QC98fPYFofKqv9Maw406HWHhkXBFzCkB6b5UxYeWgdWLh'
        b'Myoz8xa0/s5cY9VX9cPEwoS0KuYdqHN0rLHqZoxkh3o0IJJYgmb8KdYY8079QMkKFk1NTkUfTDZqdtRNEgsbhLXMX2DacgYZ5+tHqcXC+5WUyoVWBxjtP1sgmfDCAqjJ'
        b'adJ4pTH2WzOzGYv7g9G8YwxgdehpS9mejLqm1NDMN38k0xQE6ORv/n5eQ+ti09mk2MyE1qtvJE74g36uKupRdsPO589UHjq1Mn39Rxuq/iUfoV4WNjzhgvanplsZMtfG'
        b'kbKtaJPynaIw50Y7Uxp87+Ns2+FAZeQrr32+IeSjP81//5nVLUcF5agfXVyYWLxw6s+WFV+pnJj94ZTnh7/2my9mLGP+58jEH9Un/PWfCeZX2j/55R+495cM8RSZ/viy'
        b'UGZ/OKbtfsfgh7Pyrp2+mZptWJL38p6zZ3I+rJiafWnz6/aw46dyPiw4nv6Pfz6Ka3i94oW6I2u2r2v58sA21w9OLx5TPi1pYJ3L8U7kD39R1/77kz98fkHF32/9/a/f'
        b'+xP6IOjIkHf+deI7nye8kZL293d+uvibP47734kZVZHc4ZuDfjHo698knpz73fPDN/zZcmOmWsdTqze+PAk1U85O+XoCOuDH2u9k080a/Cp6YUBuUnwWyFNAlYk2fAXv'
        b'X4POrxPlhodD0flEqCCBZWToAu9iccsqdEkX9BgC+/ikH/Ltb3En5LnCVLfcUGOzWgi5pTR6vkijJ6t4oNLwN4qKGKGslu7/hFJxI4zTyAKBdnNsoPjLd/svXv1GFqMB'
        b'Kg+6MFB40IVH+ug7iLhrzCa7H0nvh+Ow9lE+ak6quOpHzd8P75uaE129nEMPRHJuRHtziJCCdlK/kF24JQ9mLEnBPINvKPA9UDJ6aCly6b+jChIz8dWD+gQ1NeJzoAxx'
        b'Ar8loJw3ywSZIN/CNLHlcrhWSNcKuFZK10q4VknXKrOMsIkqTggQAreooCTADcJqeSDVpDUeZYYg2M0OR0Glwg8WlfRHOcEcwmpEJyafU1OVSmI4imYVMBwlMBwFZThK'
        b'ymQU65Ulftf9+RP01NzlBdSMFjUetZcQJgHKODowAh1iRRcV44NvsQ4g0kx2eubQ7TcGoNRQ2deFB7eUuF+fHZ4hfzd+4+zK88MyvtiedVVzseSnSuWotY6p93MHnnv5'
        b'sPOj9oQdf0ycNzzzftqwu9wv7kVZoz1/+V3e1G3/+vHiBRM3/aPxZAv6LHOXZgwfdFxzbfak9DN/Rr86HlR45O7wt64OH7/2e7pAKuaEYvcC31qLmk1W2xp8F1+kMlIa'
        b'ujrHf9cUX0OvsugGPo43UieVmuSFiXQ/Fx8PlLZ08aVRTuqLtndDBHVuoxWj7TYVvs+hlgFjxc3gl2LVifrkrGR0EO0mmuNZLnUY3ipujOWj66gV7cK7cpPxSbwLwa+S'
        b'UUdy2I03oXMUsMnoKN6KWguBCuC2xIoKHbokY0ICeOc00XsmNHEOvZuELsYEyRiFihuEz9RSk1klswS1poBYp8/GOwtT0T1qMnuBx5saxotq7anclfCEXpejMecns4wa'
        b't3L47shxPRUA1RNTl07qoTQY6syrDAbOtxg3gKwu7RdH0r064qGjkH4bQiSs1kvviXRA5eErrQ66LQdKr8W5xqOqtxFvAsHsUTicdrPZ6dG46jotLP3pMQo7cUy1E29V'
        b'caNPRxKyfWdP9BGQMZD8y4+AbBvcJwHpAXMX2Y+V/siCcJCV2cgsE5cUW3CR9agM0q4kXMscZmtVpzOFOICqaVZTbYVgmh4EtdiJQtcQ6m3Pe+uJGqyBBnWsR24g42fX'
        b'+1rxNWUnXnnB3laeps4Ag3c2+qw35KnqrRbrVRrEue2z1tBea+0ibk9hRLMU0NH/A4sl+eGY7nSPL7BcHQ1KICEEXycd+9T4yLh/3zsVNVWaqp/lKZmBf+Kw1aNjRW7f'
        b'YVbTtYp3o9OwXqXVuh/dEVGd63UZBVkcfvbDTve2DfAb2RDhRYguT4keObw9hdTSuR78G9D7RpPYA8NYr3fHRvj9LLhvjO+9QaD/5EenBqw2EC87g8ETaDCI/uRwrTEY'
        b'VrhMVvEOXWGwjO22erMdEJKuRLowO5fjONp14pVncjgqzVarlx50X9MXCQ6Kj8EjtEPE3P13Mk6EI6nkAPrXYQM0LP3lOMmBeAfag3c48rJ1PDqQk6xXMIHLgOwqFvSY'
        b'c7X037GD9WPxbDm/n98fsj8U/oL2h1i4Kg6upF+Ba1MISUQE8PMfDgX2S4SAAGDnMrMchADlFgZYfkAbB4KAXAikeTXNKyGvofkgmldBPpjmQ2g+APKhND+A5gMhH0bz'
        b'A2leDflwmo+geQ3kI2k+iuaDALJAWBbRwqAtqvJg0hOBiBuD21gKswZElyFCDBU9QuDdoeRdc4gwDN7my0Npz0OE4W2ckCxZZHhBK4ygfRsAz8fStkbStsIgP4rmR9P8'
        b'QPHt/cr9qip+v0wY08YLeiqkiAcDyGgFu0OqAoR4QUdrDIcaEmgNibSGCIGnCzQFBKFKSkO/jAvU+v1IpeKJhS53dAqPzAISrUdGULE3zCuoVPpNPlk7wd5FX0zoiShR'
        b'BZABlCbW6zAeXBUs0Rklla9UQGeUlM6oKG1RrleV+F0DnRG7Ifv5PwCzu4BJfrLrLE6LyWppIEcuasxak9QpC/A6U10lObPR/ZUp9Sa7qVZLOjhFm2mBt+z01eyZGQVa'
        b'm11r0qYlO131VjNUQm9U2ey1WltVj4rIj1l8P568nKSdmT1LR6qIz5g1q7CsoNRQUJY/M7MYbmQU5BpmFc7O1Ol7raYUmrGanE6oapXFatVWmLWVtrqVsPDNAjlKQsCo'
        b'tNmBpNTb6gRLXXWvtdAemFxOW63Jaak0Wa1r9NqMOrHY4tBSKzrUB/3RroQxE4DP9QRHGh4y81MoXOTKezDGO7yg6RBe1tfLEssW35cyMEYlhcnpYydM0GbkFWVlaNN0'
        b'3WrttU9iS9p4Wz05Y2Oy9jKA3kahO1KLcNU7xE9Sj5dVi3V5c/95fSKLFmsTr/+DunoY93vaZDUFdAsTv/gMPkKMmEl6cmgldwFuzgV97e68fDlDrG/oFXRzPjVhTM7Y'
        b'ycSwzGpmqrHulZpYxjWJvP7CVHSCWjKLcDMR1lNwC1wVltBqInFTflkW2SLOz8/OJ3I8Ph2A7+BjAq3x65HUiUil1hnzLAvWM65khmw5byNHBvCORAJHS968LFFKJzI6'
        b'3osuqXToIlOSocSHJuJjtBpPMT1XlJWhNiYtjpAcf+5UUruS6tczjVZVdIhYNz6NtgymdQ+tkGrHzeSADYCbUpyFt+eRgzMvKPANdDVdPFW0Gd80OdIXrCCu3LtIB66i'
        b'2xZL3udyx3fh9ofxI0fvmlo3c2xoZsrHb/7tlV3/2KJ9b3eEMOh3myYUD26NzQrf9r1xKxwfBRdPn3i56YVfe8ZV/8rx5oLBk76wjgnZ8JOfjDpsXR+07bebn1n+r7OO'
        b'b3+w+tTdvzSs/NOMj8qG/0r/qH1h5bQPrJWbt61P6dCF2R5Vvf3364cOJa/83tuqf//iV8+eWLIn+6UXvvv6X75886c3/jamZdeo8Q/f/nXTsSWfffP1uJdPPrAPO/XN'
        b'94OTHr45apRNG3X9V2mlHcsWT3wwvk77ztDVcS/VLDbvW/722h//SDF5+7P/5n+zL2dMy790YaKZZVshPq+GEdLlu5IT8Ha0E21K4ZgI5Jap4tAVKni58M71fp4H1O2A'
        b'FfDVMg3dguEWqHP1OUtX5Sdloza8SzzFNBjdktXhey6qKI1CL+Mmyb2xA7WL+3+R+Ab1LUAbZXG+3TLy+vQkUkEE3sLje0vwJtoGVN3cuUv4rJ8H5Fl0yUnkNNyK9uXD'
        b'hEMViZgckJK2ZnOhV4Dt+Nxg4rEwF91Qgpr40nSqHM6V4aOi7YLig3oeh15Cp/FOK9pKVdNhBtBjW6UuLZ3HyPFRFr+MT02gvdKg+zOJPLo9BwZGwfD4GAuj93wjfXUK'
        b'Oosfkndzyfm1tXgfvPwyx66tcRK1KAbvSfcppRTdj+ObVC3Fr6AjTsJSYciuLyD6Z5uOnmcTBxdqm4pfggWbiDrkeGsivk1BGZe/SJSMr6BDeSyAcpJFu0PQTVFNfX4B'
        b'CMmthfpafD2fwHmHRceMeD+FBD1YhQ4ROPOJ60dSthyw/hUmuJqfgi7jY1QPxifQRtQOFYC0R0S9JWg7EzyLnwMKdzsdxuKSMaSGJBjtguQsWcp8Jhhd4GfjI+iCdwcu'
        b'+L82uXWX60FQtgCLl/TjLK9IP1ZFPVk1nIpa0mRsMKdhIzliU9Oworc18RxRdPvliLxOfv+lUICWKJJfvbeJAlF2DhAVgmdJMoPx6sDdJO9OdeGJlX6dUqwksmvttM4U'
        b'X8VUNidbecO7KBu/HNO3stGjI0+kQlaJ+rXcQAShPhXIhX5KtdSKV6n+cnSpT2oi/AwkDC9Di7ebTUKyrc66RqeHNnjBVvk0Or/MUGGp7BOkRV6QvhxFAACZq9/2n1hP'
        b'p4NBBd6+Wl7qazmxf8Ho6QEgs2EnhtY+Gzf5Gtf7S1X/TfuBUvvLWAkCHQcLziSqriKy9gWN0HUo+pO4nh4Uat3g7IW+5dEXFNU+KFKeRFb77yBJ6A+SZT5Ikh8v5z0t'
        b'cojLQoSiLwBqfQCkllLlBdr2N/hppWnVWumh9T5h+L+xDfEUoWRfnu4hyM4iSohDa+m2Yh1mcy09NA+aD9VNerxIDtJLClkJKEDQw0yX3aYtMq2pNdc5HdoM6FFPuTke'
        b'ug2dhxdXTtCn6VN1/UvW5EfO9DTbl+pYejoM305EpxILktGBhCwZI5vBoktoNz5nObllhMxBzslXb738qfGdiixTvDm++JHxrYrfQY6r+Dj8jfBzSz8OfmO1QrtrxOFN'
        b'6UMDBzGvfx4w4fmlOhllvzH4chVqRefw2U4WKzLY3HIn2Y/H59a7ughQPvHpRiS+h/fhE9SSvgK1m8kZc90C7ylzdAw/UFHXB33yhFwiApkMDLeUTcFX8PH+bGpKYrzy'
        b'HmqSvKw2MCsD2Uhi0pW4gfSMyDvt47vX1mlAI/th9V142t5+DGjd6wcJYwa89hgXKmJkYNzsU7tQ8XSRyb5098COErNTNCy4rE4LqNUS1Xc5JD2aBo9w2k11DpNfEIiK'
        b'NT0qInVMoaaWKcZ8eAaqgn+marPd+Bhtj/z0NKlKHjiJrl1Eh4t+bXZDgW1DOeMibnwj8UN8pk8djipwuvpuKpwG3bXoy/+XcxAlMHZh4KfGHMDhpOJPjI+My6p+J/zW'
        b'KHtPt2OF54OkzITRGt2MlQOLzjZNfn7sVorNTGK++uh3S3QcxWX9LLzZT9kQFQ3cOlSmKpnuJGZN1MandQq96Hp1p9zrE3q5hZIP1uO2Xx1mp8E7O5R/+3t2kV/WKxY2'
        b'DPJiVY93CryNUUmMoFr/nl70iRQfcpMTmw1dkLu5b1+vfsB4YuM/CCvBXV/tkzNs68qanhSR9d6zXkS56NvrjAyE6KlDrJM+b50n9TnjaX9kPwd1pqdxz7f4bHZLtaXO'
        b'5AQ4LUJfXLXOvEqi82P1Y3sxofRtNxJE4wwdAq+TKTSk1xabV7gsdmmEBLiqdGoFc4XF6ejVVkWWPkDgsNV65TMLsFqT1WGjFYhVi4NcZbY7+rZkuSpFiGbNzAYmblnh'
        b'IvWBXBNPGLbW7oUK2sp2mggLfzwF6ekMqipwEZdkfB/vU+cWkC19GmmiIHlelujMqgrELSnFuDlvXhZfrEMXs7VLK+z29ZalAczM6pDaWfi8iwQGGY7u4Qdd7Ds+X9hi'
        b'WNzbGXQTHygD1fEAuwLfVi2IR/upJaYEnU7FHWgHvq5hyVkUBj2vi3MR1QfdrkLtjlpTsGt+FnG9L8PNSfOpr0ErulialUTa2ZGdh7ezQLzO6lajg6PwuVKOBHy5qylC'
        b'B9EVahxCrwDra/KHrN5XY9GC5PlKdAGfZIo2KNDZ9YmWI2d3yx11ZKSWfJ38zn3ipZg5bwOysXNModEb3wgLe8edGcipd398Q27dHlGT9PbcH4aeabrLml648tEHk/78'
        b'rd2Lhr0sk614L8nyo6aAs+d/UX7p0fyf3P4EW5whJw/M//mij8P/vTTj63cffjvo/erl4+bdfWXJIu3R1fG6AGp8saFtyUCxJe2cUddxZnQKH8M7GJH5H5iyQZ1ADnYQ'
        b'I4FEVRvxfhj8Dhm+Voq2O8mBngERS7xHQ8YsItaXoWgvtVM4h+KHuZ12CEYTytfjIxEjh1Czy5BivMePXuN76LbXODRjkWhcOFwPeNI6Au/vjF6DjkVlUsNABTqJz3aa'
        b'bdY5vVab/HW08UZ03QqizSnUXIh3+uwW6JBRrPomPovuAnocX1eo9xkuloRJDoxP5IFD6GgnjfCeeY3tZAEDVaD1i2xAIzEDMafoRo271FLghYESeh8x7I8z8H6PdbKH'
        b'JZC0sF6QNtLff/TtcdMPSE+j2ssMQNr6ZAvtPrYwlmpwnXSvP7XlKVVaHYXC1bcyf9YHxdReCd6sslndtwl6gYf4QdXazVUehcNSXWcWPAFAql12OygGcyplfrASq7nG'
        b'SwkLRNbVGWuLcaslPyBNlUZiZLJmOTAyOTAyGWVkcsq8ZOvlJX7XfozsSL+MTIw1Jop/lCf4K0F971WRvokcwfuu7whE39sOdCTEt+grMIqkzETUQb12lqmO6Fom6V7F'
        b'MuBtvTI1siMGfKakcNKE1LF0L4zsUwlExQU1rM/mfRMwRTvHaqrWrqoxSztt0GHS584nvJ3qq/k6m7OXZuxm6EidY4o2o7tcbZS68wRcsaeuF1jgyoDrwueWduWJuFki'
        b'zmX4vDYLSoslNsemhaF95OxpLu7IYUbjs8H4aA7e7nqGoSd992lz9ckJOUB4/arI8lWdlVMWTwNdoGvr8wpAHMcvDNXgC/gM2kTl+9ySLOb92aNYxmjMOTIsR5Tv8UtA'
        b'jG/2LuAn5+SXZOHLuM1vk6a1JAA/HD/UNRXeDV+DD+NW8SliRM8mvDRx0SrCX/13aLKScvL02ckJCga36jQrQC294yIK7upn8PEuzJ4OCTQdD7Qd79JE5ybpknPkTAM+'
        b'HwAi/W50XsdTdh+FO0Jx66BIaJpnZNNZ9OJ4dJbGgcPbBuBTifT13Hzidn+EW4Xca1fjDhqBDb2EbsxIzMmXhhGG6Oq8gXE8PjY6znI3tI11kEM7DzKKhr57PwinamRF'
        b'xYZWNm2r+63QT77347btM+o4NHC27vDQ4qxj24od3+T/UL838LO/vr4j4qP4i9FL50a+/eKlI78dXfrO3+obpy5Z+f3NP2p3//r+0ZMfb/lVcZAtbGvCesv2eWsCxn+U'
        b'sVW26NFQ66lFw3+/9QN+yZnIqW/t/eV35v/7Rsovv8l/788hB44nznn9NeDn1FDQlI42AcdFN9EWYHlcBTsWuPkLlJlPyljejZejNhcwXJGXkzPdoiPMdrXgLxIkrqzj'
        b'oI5X8RnKVTOmoZdys/MTQMziGBVq5fA5dAJtcigoS2/EDwK8LP25Qp8SJlMBs32Rygr4bkFmLt6q9kXYO6lKpqAPx3fxQbK5Qh1xFVZ8M4KLzdLTfYTaWWgT9dYtFOOr'
        b'JLFM/OCBKTw+gF/Am6nyZ1uGHnp3GnCLllZPNxo24ZdFfqr5P9obUBPuKNEOyvD1nQx/nIIGulD52H2g9Kehp3zINgD370B5w0B/TivVJbF9hcjACc2wCyQxd+X9AU/n'
        b'SywTazL7JAPBxwirITnfTTz4cWzf4kFvQD+xIVFHfOqkl/pky2/52PIIwj+AulJu4mM//uZDnYw6NXHwx87RRdonkEoImbITUwJxcBRslQYD3dSwkwBsdPPDwxMb/wyS'
        b'7WV/xaP0WqGJ2Yiq156gruoukan8hK1q+pa3X3QCB/wf7Ub1hYB2QuIHkXlrhAsVJ5OFs4qvZWSmvh42gaLYVwr+P/wvCw7UsGGBnBhBSBbIhkd2fyKM1Q4XrymdtKGH'
        b'+LQjr4CI+c0plFIGNnDEWujswfcCpf+Or7q5awlcuUzgy+UWplwhyMqV8KcS5OUBgqI8UFCWq/fL96v2h+5nq/j9oYKqjRMKQWJSu0OreOqFTRyRNOYgQS1oqFtWcBtX'
        b'Hgz5EJoPpfkQyA+g+TCaD90fbB4ghhUCSYz4CoW4B1SphIFCOHGtghrD9gdDu6FCRBv1GKfPDagizlpR0hMDoU7ipkX8wsPhGeK2NVgYskVVHgGwsUKMMBSuI4VhwvAt'
        b'THkUdcNiyqOFWGEk/B8kvTFKGA1PDRbGCHFQOoS6VjHlMUKCkAj/h7oVUFOSkAzPDHMzcK0XUuB6uJAqjIX7WlqWJqRD2QhhnDAeymKlmicIE6F0pDBJmAylo6TSKcJU'
        b'KB0t5aYJz0BujJSbLjwLuTgpN0PIgFw8bWGmMAuudfR6tpAJ1wn0eo4wF64T3QFwnSVkw3WSWwXXOUIuXCcLRZKJhhfyhYItAeV6QUZl1nkeRUYt9Q+71EVgIgtfvCG6'
        b'iImhbEEWJNEEq+0mIgSKElzlGp+3UjefoK4OZ3aooNbstFRqiU+jSbSXVoqCKBQQ2RLqFO0s1jVaW50oLfYmzek4j8Kw0mR1mT0BBi8UHj6zrLjgy2k1Tmf9lJSUVatW'
        b'6c2VFXqzy26rN8G/FIfT5HSkkHzVapCgO6+SBZPFuka/utaqU3j4WXlFHj6rbI6Hz55d7OFzip7z8LnFCzx82dyFcy5yHrnYsMrbbhfrWJcNFEIYGjlHIKG/67hmtpFr'
        b'YgV2Oe8Y1sidYtsZR4KTE7hGLpIhwYmbuUZA5nWswDeyKxl7eSNLfCHhLfYUT0IaC4pB8Fw0E85MZNaxdSq4ryRXzQx5r5ExyKBWeTtQe4NCUNHJDfi5oTeFpLvbnDTP'
        b'nV5z3V/oS8ynIyEqGSaxDlrSj2lLHLIp1DGtpDB5XNrYif5oJIBukl1FZH6to95caamymIWkXjUDi5PoEcACvQ5ytGWvsiiiLKgqdkuFqw/dYgq5PcUomKtMwFt8aGQE'
        b'ZcVSWUNqt4jjBMgotQMI1rNvn5A5/zLCUkd3rjp7EzfaEedh9R429RPCND75Gn6+5PWpqQU6pSe0e7Nkv8Vkra8xeQLnk55k2u02u0fuqLdanPYVhL3JXfWwTOx2hhoa'
        b'qBBBEMy+jun3/DzlvD8lfCqc0n4Z8IxwyQai5YhY1BAiIsDTeRCI0gQFrU9B4q8+/wFvEz73geTuSEOnbk29WWuEKakEVm/Vzxb/G416Ozmr8xTWDzpKfYL1hU++GUKd'
        b'GHpHxB7Ncd7mQqXmyBpexql95g6eTohHZXIYqAupR2VeXW+rAyW3T1D+6QOlkjoVuGorQE2GoZDGQFtvNVWSHVuTU2s1mxxObZpOry1zmCmaV7gsVmeypQ7GzA4jKRiN'
        b'BEtNwjIXPEge6FpLz73ermehWBqgwheB3HcWiqXm/Cfb992ik/38D70RnbJ6IpuJBMe8urLGVFdt1tppUYWJ7EPYxO1deMqkrbfbVlrI1m3FGlLYozKy+VtvBt4xiwwu'
        b'dHCmqW45tcA7nDaQHCl5qHsiUiCRAS9IBgqSkYyxiy59kdAQiuSzvMMYE//aXnb5SHx4s7PG1snHkrQOC9BUqRryGtmN9/fS7auPUkVTSIT5KUaJxfayXdivcaTCZiMx'
        b'e7VV/lYYF50Kods09EokV5ntsExXAn80VRC3gj7sMV1ETIJUMqa7aSW4wEUWAT6K9+oTk7Oyk4gCnLuAuJPinVlwWVgWn5NUig9lJyuY2jAVfhiBjothA1tX4N2gVF7H'
        b't+fF5ySvMZPYyrsSC9BtfLo4GZ/jmHFz5dV4Pz4pGhTOozP4jkOfn4MPrLINVoQxIegQr0eXRrioD+HL+AX0kr8RI74gOSE3uRiqphXnluCdchBXVeg+gx/QkxA5mhEO'
        b'MSDSSXwsX87I0S4WXw9EV2kg+XK8cXUJasP7y3AbPlCWj9wCy6gKWXwLnxk0h5o/JuN2fIqAJGcGr+PRYRZtzDW7qE6NX0GbHVmieSMXXZUxY/HGAQAwurwEd1C3A7S1'
        b'FjR7GBx8Ad0AfVq+jsVXlilKLQ1XYzjHW/DEZ1ftEW1T62bO08z+/T9/zQaUZtlSzlYq329+I6y4OON0+J6fbHnj7esvJMWpjZO/WDnyO0cqryi27FR5NONfjZv7djBX'
        b'fqWo4rPwoWkfztv4jQTz3Iw3knd/By84Y3/T8L71xJ7fat6f9kHsD7Lv5wcfffft+qujSg7Z2Ys77pzb+ku24J+mdovCErjn4J+/eG/yj9UT5/5h+D/+NjdRFzOxbu3P'
        b'll07k3Hvq/rAP45p/nrPu8e+YWn5/Q9w2N9OjKtb/PBPf4v+dGL063/9xq9V3/91QNrFZ5tWDtcNEAO8vpKAXqFxqnCrktHhS7JkFl2ZF00NI+oQfD0xGW/HLSlZ69Ed'
        b'3MYzmjm8YjDeLAWPxTfwXtSaAo+wDLqHtstSWNSBD+FXaZQifFiTl5iTnwf6ND4mG8GiE2jrJGoSQcdzUQexqSyqyFcyChnwxlhqElmA75bmUnBYBt9Fx2RRLDo92OUk'
        b'IRIaNayfNQefxZukPW/RnBOxhtpjADnaVyXqdQkUifLRxUw5E4Jv8mvQDvQCbSMXbUG3RFMPfgltoRYZdKWeghw7F91NlL6RkLlaVsCi689aneQML2rCG9GLxN6SnaRH'
        b'LdDnLcosWolWK8N3qLWIeIWjHQp8LNe70kpRe24hakvJSSJLLQG/Isebn0NNFFLFs/iA2Nds8g2CZbiFZdQCsTydwDfFYTqATkBlhcksw61k8cakDNs60WLVhjatzk3C'
        b'm/ADv8Paa+aidjpSuGnuhtz83Nx8PT4ViFuScr1xIRLQTjm6xs0QD4puc6CruLUAXUlSMOgGTP1sFr2KtgY9haflf3IQM0KkiYaubIDalYhviWRX2sAEE9dS0aJEXFDD'
        b'qZspObApWpuCRcdUqZQ4p9JjmzGS9NNrIwXeQ1v0yOV/4lrKiq9SoWIvJF93syY19XM6s1/QoGYiXfbtd0OjztCQZyA0sH5RZzj62ZEn872pApHhB72JDLNEnied7RFl'
        b'RSLfAAsibMwnrkmSAxEjHJIG0JNDSbsN3USPboJG74JFT35X2lOIMRFG2YWve9msjfB/stWyhkgoPSEzVdaI2/m15lqbfQ3dGapy2UVW7aCfnnk8z++uYHUVbP3cIp0m'
        b'ezVoM94n+91bqfNtrohY4t1b8cpWRCIyO/xNAY8RDXo/GK8SvZlCh5K4uLdZpsio+dU0q3jwY1tUDDNJM4WHwsU3olZIcXHn3mFWs0xqWeCMFQurZs4Tz3ZsXaF3BAVx'
        b'6BTeBMR9J4OvxE1w5RCichEdJ9S9i6SRXSbt43g5bynxClgAEgDZmPF6GcTH4e1AoxqGhU5BTajdsmhuCee4CHWO/eBqvhRPvfqHwaHTh25vnjS/ISEx615H6IHv766y'
        b'TGK3/j0yZmOT6di2P3z7UducSRl/MppuRH0eM+UGn/Zn2dhvxY/Zrjr/4Y+yLs5bvWXs92f+/NGbh16otOH4/HLLB3eUk0qGHPtBYMJPqi6FvNswcOnW2Lrw5394ZXnO'
        b'b1O/fyL2zV8U7xp58zv/+5Vqwd+XLPkq/aU3p6/d8/2r01S630RULH132qlnNrw7mV3bMumNr76pC6Zn4AOAFT6g7gHoTI4UnW2ikrLblSm1uX7yR8gCw3zemof2UBaD'
        b'T1Wgu51DNySpO+cYJ8bhCA3C18SYS/gWusPQmEuR+IhzFJmZ/fg2flUi/i3oRVd34o92VlIg5XivTProD3ajJsIEp+IOytcNJdidKAb/ip9CtibU6CaHXwQWt4u+OhHv'
        b'Bc4jBmhiZFotCc80epL48YzzybjDy0BlDSmEgSpYkSltXYKO+vFPyjxhou+KDNTGOolXdik6OpKKrNkAtjgUwKRuEkyCweDwTbSdNaSo0Fl4kA4GD2LCgUS6AQPs+ZCc'
        b'USzjhkWw4mGMW5mJXdzj1OiCtDlzSYp3Vou2qxOT8kFCleLXh+BLtWgfb8cP0MPeTuw/KZdTSloE5WvT/PnaBJGjKejxCc3XHBf4FcepvuL40H9zMsLFSDiSYMrlRDeK'
        b'YLYhWGIdUqVdnejWdWVm/QQm4cRnO/0l9kMSD3U5RnWysI2Mp++IU90h6aG5E7JDNXeigRDNHf6IjW2wwDo5uOab2Eh4QOC65LyxpL7kRlu+lI3WpwGjorB6NIY6m0HS'
        b'rR0e3lThEE0xvWj5nlCDb9dcNFnmcN7j6RwMI9cQ5bW+dHuuh13Rt12dB0kz/dJEE2ef08jS/jDLefsM0i97QiN7ivSDaWfXsXWRTl5gG2mePFnFi9ZGuJaRr1XQPnIF'
        b'X8b5uGmtxQFgVNZQPjQa2AAxZFHdmlzATNIhGGiprbdaKi1OgzjoDoutjs6cJ6B0Tb1ovqKDItmqPHLKtD0q0fhrs/fhdhxsqLebgZmZDfT5eZx0Rp2hoWAVMGAEPwkW'
        b'NER4B67LG71OPh02QgsEYi6FoSAG02VsFRcpulTCAISJtcWTTiaJXbWv9U1qcFcoVQYDtGk3GBYT+Kh45G9GE+/1jYZhFBIvIkpQbCFQKAmawaj7Nd0Nn5QGElPAQM9E'
        b'eVsO9rVMb3WR18i1zNtwNMX/U4AJAtvOraOD0Mgu9w0CO+0iZz/JSKZFuKar8kQvYCgMBqvTYKjgJEbOwOw0BPngIPeeGgyWnsUBMLhpz9hfIE2d66Nls8FQ1VfL5l5a'
        b'9uGA3n/pxHoXxXLOphVhWMYuJ1YtWk6uxKM5a72w9IG0AJJ5hcGwjPO6ylNkDQQy6gcYeaIHYD6booYOCWlU4z2SJDbQxxDUQTfr/VCgs5263gbgcUMv89IBdnq/I18N'
        b'8+roY+Sr/5M5l3sxn5ve/5yDTmJY1VfL5l5Wm89rngytd9X7HKj9CHbPtU2sZgbD2l7XtnivSz+7SLWjeu1nFNkAYigZ5po4b5/ZxIt853KjhNUbkeSEr7QbeLD+TYJg'
        b'MKz3sRGqb/rRAHq71yXgh2kEwHa/4bjd19ATUkdrbOqd1PVs7QmGI7r7cIjUJ9neQdq91Xu3Ha4Kg2Fbn92mt/vudjAFRN214/Y7/XWb1tjae7d7tsYzfnSGnHPw0Zlg'
        b'J0NpCuTDu3dc3DjwBBfYnNnAUc3kOJNZ6MQHOhh9HdExGGpdgIw7OWkPhKFCXJdRoQ88MTKIEYvsr/Q3KrTG/b2PSs/WuiDDNP9R0fZEiyG+cRrSbZyEThaV0okkfYyL'
        b'2mBw2l1mwbLSYDjUjSZzMDphPoB9j/3nMA/2wTy4T5i5lMcDrQGWZrXZ7BSck71APdAHdedz/znYkT6wI3sDWyRPox8LtZIGMDIYzvcCsB8S2rrTCJk/rEVMV6bcCauT'
        b'QEv2xQGuzuvF3DpuHS/BzDcR6Hnxqsp/2D0KGCNoGqR2SmNfZ/wJrVdRIYTWI19VY7OaieNwrclSJ5j7kk4DDQaxToPhGicRFbHHGo4cOQ/8umGAr9feJ/uWSIkcKHIm'
        b'NZ0MiTN4JY7euBONGFdtMNzrVfyjt56kvcDO9qof1169zWEw3O+1PXqr7/bCaXtOsS22G82zH+4yH321DsqVwfCg19bprSfm+1SSu95PS5Y6EGC+0WtL9NZTSRh9txRA'
        b'F7AJKnzdr61Q/9VNbtqbmF4sr13WN1klyxl7qBM0V+pBwgq8ICNMJgoAWUdWB9EEuWauXVwv0iqhSCYv+IRU+mUs3Tm21FVr622rxL3nsamiB4arvt5GYhB9yaXqPexY'
        b'WDHN3inzqFa4THVOS4PZfzF5lFBTtcUJOrF5db1X/evTHAEjQRs3GN7sJB8qGic12H9EpIdE3kSGRZfSzc/Qvkyqz2G1OUmQM/JNbU9wV2s25KuqzJVOy0oxmDaQXKvJ'
        b'4TSIdlqPzOCyW+2HSG3HSEJs26LHog9HPSqf0q+mhlFxj5Ya3anyaycxskVq006SMyQ5TxJiM7RfIsmLJLlCkmskuUESKn3dJclLJHmZJJQJv0qShyT5BkkwSd4kCdn2'
        b's3+LJP9DkrdJ8g5J3veOsS7s/48HZDf3Ehsk75ANB+JyoeJlchknY/1+gS6GR/Th5ignvrjD4oibY7SWYwMVwWoNr+JVMpUsWCH+1/AauYr+kZJgFf0NgFLpl+7PopOz'
        b'0S4H3oHbRM9HfLpOFc25zLU9XB9l0n/Hj7q5PnpDwFbJaEBaFY0/RwPSkih0Uvw5GnxWCKB5JY1HJ6fx6JRS/DkNzQfRfACNRyen8eiUUvy5UJofQPNqGo9OTuPRKaX4'
        b'c+E0H0HzQTQenZzGo1NSR0q5EE3zg2iexJwbTPNDaD4U8jE0P5TmSYy5YTQ/nOZJjDktzY+g+YE0Bp2cxqAj+XAag05OY9CRfATkx9B8HM1HQj6e5nU0H0UjzslpxDmS'
        b'j4Z8Es0n0/wgyOtpPoXmB0M+lebH0vwQyKfRfDrNx0B+HM2Pp/mhkJ9A8xNpXnS6JC6UxOmSOE8y5VrqNsmUj6AOk0x5rDCDCrEZnhBy1qa080Drz69332Dynvn0e0gK'
        b'htftMeK2QX1IKk11hCxWmCVPOaeFbu94PT1otDWvDx1x9hD3Ucxdd3ykfaauzh1Eh/I7fWskRNgkHhcSbJUuohP4au5Sm83urdDiFM1q4qvebZtZGfmls6UajH04+HXJ'
        b'ZFdJniombQU1AkJ14m6b/+ngJLFJb18lJ06n3UwGpEt9Jgf1GSXAUf+RlVCTyWrVuoiQZV1D2E6XY8ddXu7CcInORwgOCWjlqGAJ97OHEg44iGnmXKw92ssFndT62c6u'
        b'4wXgeAYxldFUTlMFTZU0VdE0gKaBIH+S/2qa09A0iKbBAg9pCL0OpekAmobRdCBNw2kaQdNImkbRNJqmg2g6mKZDaBpD06E0HUbT4cC7eYNWYCEdQUtiG7lTI9uZ2cyS'
        b'xSDzytbJG2WnYI22s7tZB9CeRlkUs05WN5iWKkipfZSgBB4/ulFGjIrrZM4xwPNlTRw8P80ZJ6gaZaL11xlPyhvlTTzLrPhdM/RuWXAzS59bnMNsBgiowBRQYP82kRHG'
        b'iwugx3Lpf0FQJjHHwxo8nMHwpdww2jHa8eXo7pXUmIh3VaeDlmh61Xk0xcD8LbWSI6RC3HgUw6LyBovgkRtcZqedRKwRj0N4QsQw7L6zcfbZhD2Rz+PaicHcTg4Fi1FU'
        b'yqlw0PVoJQiA4g4z1FjvsoNga4YmqGCgpPZ4p8mjMNQ6qmnTy8lxQ7nBLP6jhw+DvK/Rz5zBS5U1ZHeURuk1OV0OkE7sZmIoN1lJ2KW6KhtATMfVUmWppO7QIJCINMN3'
        b'21Tr7OyQJ9xgtVWarF1P/pMYyTVkT9cB8NE1C9XQ/2LsZE+ModuQgzgL61F6Vg7XtQ5PIABpdzqIkzcVrTxKmBcyJ57gDO/MiDOhdJid5IZOIXod0JB9iuWryMfi/eIn'
        b'NDKPj95AZ/MjIvqVU9EvlPpVdA/bpepR0scvJ/4PpYYhDf3UMknD2IaobiPwVKGoJZvII4bp26M0DFQe0dE1untTPo/XaaXUR6FueefxzSQxAoPTJh17Je6GApBqS9Ua'
        b'IMB+hPEpHGCp8jGrP2AjvMB+OaZrDC+yoV9rc3aetaWBTZ/wwC9tN6u/dqN97XYN3dWzWRJJ9cmDI9lz+2t1SNfe+oft6tasFNb0yXvbb8SuYb52db1E7Ppvmy7pr+kR'
        b'vqZ/nKEVg9k6XBXSMQ7q3E7ak9xqpMBQ/cJFhSWxIro1SWSbeniNyCU0PE4voab02pLOsiqLmTQoCQpQOzzQ6XTjo/0ObYI0TglJcGlx0v/ewF4JdBMyQYyulfAU+PFc'
        b'f4MV7xuscT0DpPSBnxkzF2SkQJL5VIfh7Z/0B0eiD45pXU7kk9gj5oquZ/O7wzOrOHN2yuzMmaVPEfAO4Pltf/DoffAU09n3Y9mSK5bXYb+bj5BeO5sGSRE9oqyrTGsc'
        b'0nF0bZ252kTU76catU/7gzLNB2WCF9W9fk5+AEucWRtfMn9B+dON0e/6a328r/U4StxttuVEohUP1YOgW19vI8elQCRyicfwn6rjv++v6Um+pkNKfadfnrwJqXd/6K+J'
        b'qV0pWC2sWVO12Q8N62vWOIivm7YoI7sA1rj1CRuXtpz+2F/j07sObWejVlt11za18bnFmXOegktBvz/rr+kMX9Oin1+dkOy0JcO/Tsatjc98ujahu3/qr83ZvjaH9hro'
        b'QRuf/+QNSvjzeX8NzvU1OEJ0ZgSRsI6cFJGWihiAo6isuOjpRvbP/TWa42s0jNI4KiFLh16eJlSn/W/9tZLfSRO6Uy4iVxMnG3IdP7OwMDe7YG5p5sInpZvSwP69v9aL'
        b'fK3/sXvrXaV9vXYO0Ii5ZoCnjsqFDp/q3VsAeiBeC7LnlJIw8knaufNnJWmLirPzMwoKSzOStKQPuZnP6ZKo084cgjI1Up191Ta7MB9WkFjdnIz87LznxOuSspn+2dLi'
        b'jIKSjFml2YX0WWiBmgNWWRzEp7XeaiIhr8RgIE8zhF/0N4TzfUMY60fURdVIREwTXYwmB4zi0xxW+0t/rT7na3VC94kTNTi9NqPzqFp2wZxCmILZBXMJpSeo9FSQ/LU/'
        b'SBb7IIkqpdxeVBthCgWCO7anEBRhrfyrv6YMnTReCtRCzz6KDZk7zUD+usjTzPM/+mu8oivR6yR2xMlbS2xXvTAVr1MJ3QWZLzXoKKCeb9F0h5C6VNXHkGvxdCzZ9YA/'
        b'WROkBvK8nHrKycmbBpqeUkCqbGdZP/C/nFosOkITC5ZPxhFFrk5bWu8imV6nsv+GdHM5SboFk6Y2CBLUwF7L0I3VzojT3baK1OTjclKVZt673wh6bjT9KBTxyGwY0l3h'
        b'9Hun75ki1jSBlTZ6S8Ume5smsjth4zu3qXqotz6HmD5PS0ZLc2QPJju77QzZya3u3JKD/n9F+iojRolePd5UksHCQL6TJvl+ELNAb8CID/bd73A/YMQovwIrbRdTU5cX'
        b'Grmoh/ThgGc11xkMq7pB04uRgT5XoBvZ224VNX7Q/SVPcDfD1bM+zOlEGqsXXzxBXe1WCslspZQ4N/0MsUchmazkosVKRg1WMmKvooFIPJouxiqFZKuSUbtTcDerlNrf'
        b'KKWQrFmqTmOWaEgK7mqsso9kJfSxjyZXcaw0iE8U1M3+ISTvEcsQ2c5S8TJ1WNpThtBQ9hVa478MzdHXf8WThvbQBKp4ldxFI6HuXoyb1StT0b6geo0uB+9ILMjT03OG'
        b'u3gmoUaOruNz6Eiv0RzJj2M147+JJXBbGPodRV6Q+b6jKJeuFfSbiuK1UlAKKnhW5eaqWPH7ieUBYtSO8kAaQpcj0TugVE2fCBFC4VojDBDC4IkgYSBdMeGegd0wPs8C'
        b'irrMD1CZPx0geElosYH6bRhYshtt4KpJvAJe8LEMGVULPAG+Tx7DZa1NMFnJZ+1iu5sySYsG/60Th9etQ8/S7VpvJSpvHd0JHNnl3cj7/Kek7+zF9NLO0x2Ppw6c5JNh'
        b'fUdm9dkMe23tqb5eJwnfU/prz+1t72n499T+amzus0bfpBPPCK//RyfBH0VqndZX1YRebPfjOX1NRu+kvi+nDEnw6my1K6+lBKrNr9XufFVqlZL0J+Cr1Y/nq7sf30eJ'
        b't3Y/CeBzsCFBDL2eU44wJzQt+fZTL6/lvGMcXFMvKXpNrmTLefs0p1zcK4O84pSSOP+xfucdkv1l31oSS6CiMzxDXDdI47o+LtjM4ml58QwBjRrjPXtHGQVIRscZaYFS'
        b'XmV/hlxNJwl1LyEzBFytvh40bu/hAbVfE/TRPvyzeJMg7OP9jgyoJD9scpSlFx5Nhxne6RuLAiUs6nQh6pzTbhhEPv983G9OB/XWWO9ymc8fM5yuF5GWNzKzmSZW8iji'
        b'C3pIwb6XiIBA6OgSDTnRQcSaPdwK4tG9ReS4nD2BjG6jeE3WhYd1dsfIEEhO+UhScm+wO21OkxUIE9mEckyHC0LvbbX103Wsh3e4ansVl+T0rZOPGxf6VIEuuLuo1OmF'
        b'QxGmE1c6pQoqZMxipRmwz/FJGv0ERZkMD63jpQEHfqwQv3yo4on/CfEvcZFoZGh3yDL1SuDNU9HOruwZd+CWJIBoNr6izBsxsAeLjpT+O/ayXVg0TCz95Y/Ly3niX0K8'
        b'S8gXDoVAwoDJtwyFYMJwhQHHg8vJJ47lwIzDhIHAgOX0lK2KBMhyh7kHVSmFcCECyhVmJQ2GJX4WWSlEk2thkDCYeqEohSE0H0PzgZAfSvPDaF4N+eE0r6V5DeRH0Hws'
        b'zQdBfiTNj6L5YMiPpvkxNB8iQlTFC3FCPMASalZWMRbGHNrEnGV3suWhcD8MeqATEuDuAOgNKyQKSXAdRq+TBT1cDxQmSyHASOiRzu9BBkNfQ2lvB7rD3RHuSHeUO7oq'
        b'gobcCigP36/cHymktbHCFNIKjAhPA2+RMGQR5NuJwgS4N5W2M1GYRMsjhXTKnKd5NAQLvb4RHrbIwxbq5B5u7kwPl53p4TJL4H+ph5uV5eFnzi3w8LNzcz383JlFHj67'
        b'BK6yiiGZlTXHwxcUwlVRHjxSXAhJSSa5UZ5rX0kJ0tzsIl2wh5s518PNzrXnENrGZUPdWcUeLi/bwxUUeriiPA9XDP9LMu0F9IFZ5fBAGQCT3WXRe0OvUxcI6ZMHYlQv'
        b'mS/wuuyJAq97Sf0TBAqXFbjIHjq6jW7hzWQxOHFLoR635ZOgplkF64d6g5nSEKL6bHpqMS8pO39eFiyRHHri86KMmY43h6BbKnza8ul7jzgHWV153w351PhbY7w5Pize'
        b'lGWyVln/cr8iybT4tfe/cWv32MObOuRMjU0ZNMWj42lsSbQpRKVGF5Ni0Lks76cFBuCXeXRFHSLGfjiENuM7mHyuC91tgKZJCIJj3Oqp+Cg9V1nFz/J+ShrtikLP+74k'
        b'jV7Gbu/pxcfvWHNeQu07PSn+TiKuiw3h/njV9TvN8s4dc7uMUKlePzsLZIs+Eed7zNfyTUKxSEgU36lI8fe7/XxuoFd4KlV+c04A6PoBTxVFq0Dpo+jiWhSDAnV+wFPV'
        b'HACoFgCopqKoFkDRS7U+oMTvuq8PBZN+9vyGYUyBi1B/dJlfmytGMqRxc5OT9SRSLg0zC9OfxQeVFa1CW7LQBZ7BO+vVNDjMKRf5XA06jW7Gd74LGFiYPB8d5KRT3Tm4'
        b'Dcj3rtwF8bhlgQpwWUbiy15TB1Uuo+fKm4YpSIDo1G/rjdarhnzGRWZ57QZ0xREUujiIk06V45Zo+vTyIhUDzDJ6w3Jj0tqIRsZF9oPRnjx8oms8/GQ5Ou1/xlzJPFei'
        b'XDMS7XMR00jgoMrc7PyF6GpuEm7TsYy6gMPnYlGLSws3U+alJ2aRk+h4X3oqOoCPp6ItxlwmFt3m0YNgfJAG5Q1HJ/CDxAJyQLstH53Ht8r8TrLH65PjcXNKAgkFbNOp'
        b'cAc6hQ5Rp0kC5+Zc3Jqdl4I60PMKRhHFBePN+DpFVtGvchO+jd2JZNCT0X10Bp5BL3MT6gfS+Mbj51nprd6bW4Db58XjXUm4pShehA1tzeKZYWhrELo7dgrt+2K0R+NY'
        b'CWtyK74pY1h0hMG7AJbb9DsAQDd2omv+37KsX4lvlsbHNpAPSiYl5ZeJwfzFY/zeOWcZfJbXAIM+iF6k0XnIqeosb/R7vD1v5MhkBTNwLo9PoPM28aOX5+fFeYevrCh5'
        b'Pm5eNVD62kBnd+aRZji0nSOU8KF6/Bp8h2LHNPzqBrxvHlw1MOgs2p2/Fm4QAo32jcsAKeHGqpX4FmpZhW+G44tOBRM0hENH8N3pLvKxHLS/JtCBbzrnk08cxOckAwYA'
        b'xaRNFZNBQw8bJKAUUB++F8jgV6bQzy6gvfi8LJF+WXMnPL0CKNiukvh4oIrNKQVlfl85YNBGdDEAJJk1Lhox5uJsvE0NRPKWA99dgdpW2TUr8JFJ+A7DRKXzaMsi3ESh'
        b'h3pfRodxK/kmS7I+Kw+dHVQgZ8LQAR5dxQfWUvx/00y/yZl6dJYxLyx5JkODFS1DZ/Fth/f7mvdhlLdDa1csE1cFyhzLgZp997PssuLc4qYZoSeGKcKm/2NPylffZqdt'
        b'jnsr5+9V348YebFYHT9/X9t7l97dOTJ17a5fjbUzQz6/+D8fZ3znn85CfnxAllUYXMWZeMOMos0DPhm3L/5TT8Hwb+26Ujzg9QmBt9YLo4oGvXT7W6PX8jXXLv+l5Xff'
        b'M32k/mfMzbmn/9ZgyZhw6UBe2rs1xpFhJydP+OHpS/+PvfcAi+rM/sfvFIaBoYmADRU7Qwd7rygdpdgVkK5IG8Cu9F4VVFSwFxQUREDBEs9JNsmmbLIx2cSUNdn0vkk2'
        b'xRT/b5kZ2oya7Hf3+T+/Z0WGC/fet5dzznvO5/PiwLZ7i75K/nLIypz87w68svab7+OH+uSNuL/44jiD6FcKN8/LkpmMrlr4zdN3bQzed36/ZccnG96cd/kfc9Z3Rt5U'
        b'/fmTVEPfNQZjzWODV04PiW38oqog4pNNzz3hPuDn1R9m/zRkR7b4r0M+kz39k5dtq3vr2Jq2T0vHqRYGGX708b1fzix/Y8roL0O+3Tf3q5szV86d7Pb9j1P+ce78wptF'
        b'c78amBQ155w1Dl2yY+6tsm0r/hH8Yq7DnkVm/zDw/pPvEbf1VRuuf3ip9W9vXw/d+vPqd4evulP4leKnActn3tvsmf9AFHPGvj6v60fD+cfLg0oHKsfwfXOfoRXdN/mm'
        b'uRRytPvmQFsGSeCB1bCfTCky3/ZiBSefUsAlMZ6Gk3CZbZ0Z1qAl9SHDvKEHpvRWCwalAJmYZU8W4gKs3mJmapxKRgG2p5nKBKsUSTBexC6OO50Fpd6+gXADmjiA0PwU'
        b'J04EcQsuGFHqqlUUWEHDMbHKgeMnnYVDeILSk7pvIGXAQlbAi2I8CU1bWB1DScIXocQ8A9uTsS3dVLZ9pKAYJI7DQ1DD0290jePwF+0UMYzhX0AlKRVNf7kU69UUFtAM'
        b'p9mqxUkswmE/I8+ahnvhsK/L8on+MkG8TTQLD0xlyQbhaRWZK8VY4U9WYVJu6XQRtGy2ZDAQRBqporRGxWSHqvCTcdqtIzFpjLu2ec1KVYZJSjp2mEMxlJrLTY2x2TyD'
        b'TEls35JiKpsDewV/qQyuYY4jg4Gat3yPozOW+blHY5ZIkK0SYeMgb5bPjhlwE0u84DCSZiXyyS7RYrgO9Qy/IwPrMZN0S/7QQLKiNXr5A9kAXSgK+1Bok26BI1DEZCex'
        b'N+QxelG4GUTLXOJHZKN5Ytw/wp2PEZJGiYbr1NkF2uVkyTUQbPykpnF4lOFsYOcUoMhbdKhZuBoIsnDx6MEGLPUQP6gmdwJ2ww2+zhoIikAx1thhDQOoSiGrVLaaXzSQ'
        b'btEkCyyaPok02kg8LSW71gms5YP5jEN6TyLS7VDFidJmYjPv6EPBIxn8V5lfONSRhvIWD4JcOMrA17fDMbKtlJA1rIvlEeAXyOhsRcJQPCJNicQKPt6aoimMeaB2U8Fs'
        b'pWAWLPGH41jGUTzO4zEytkqIJHwRLzgTOcNXQoZksRjPYocBRzErCJpNHvBx8iZSgyCfRuXMrg3J8zgi18VdUEfvYvF6+gBjR6FZeTuLBQd7A8xyJGOTigAGZLo1kScD'
        b'nKDIlS/wA9NJy48k+RiYQjXHMTlFJshZWhw1jks2adCLUrJgX5SQbjszKY1q1D5wy4DOEdPk6ZjVQ4yHIqhw7a3fOpINp2yMMRzdQbYnKtdg5VJH+q4j1vdSAdi70ICF'
        b'fkqZ4CcYwmW3sZyrtxHb5Q/h6lUT9ZrDYagYiXs5TXDZutV0mJAH6RvLVtB3ZESZlpDl4Ty06BbP/++JZ5nVgYn5yf3F/NnGIjnlmhVLRYMpkir5aSMaLDahwCmMk9ZE'
        b'ZCG2IPeNRUNpNO4DucSShQeaiI0lRFAXy3o4udIjPFmP35j12bqPyM7Nzqx4DcbqQCuN17OUGuVS6dhOnUp1R0VkRJrWgVmmioyL3hzdF4zF8DEao0GeGidSJ5rK+C1Z'
        b'Iiwjuo1zK3u8qGeLdehRT557CH2t7rr+HtpWwzB1LfXCvWqtWr0z+10WduZIuPlh1vD72tNse8a6ognc4KWzU2Ok9ALPf3yvXnVdFWFqL6ywh3D7/KotiJMuv614VXfZ'
        b'/hBTbYOIn23ry59qdzz/ESHMYYu6a/1hcl5+tEH96dPTkmJi9OYq0ebK2GDJ087kcTsaQtDtOkZLwlyw/xBHcOrIh/W/TFsAB+ZKER+j9p3YTD1WSKtHJ9IYmKg/3AQm'
        b'YT3mtt5iGGmLwRy7qBtHLEWV0/pA/qGalz6sw020WU7Qj6fcO+Me+bKFVosoSONatVD13NIg0LicXaLtljsFZmkQMeuCsFsU3OPaTRO33sfSoDGU90Wc0097O42VIEb0'
        b'B0hvKQVUukgHkiH914sIqbe7iMpOFZeUnhDF+G+jUxnsuV1EbAR1MtGZlpZNamFCdAR1vrJbxIJuaEerMXqZ76IawVztthSvG+NXDW4eHh6Smh4dHs7ZeaPtHDYlJaYl'
        b'RVLGXge7hPgNqREkceqepkED1suCmNZv1lMcf7XXAoc65G5v23p4kz0a5T08fHFEgoqUsD/IIIsWE/r8E/XrdklA/GG4LlJRcfqSzPCz8Gc2yGPuEUlXXiQ6O6Zd9KWS'
        b'w8LtcTDqIYYwIQQ7sEktiHRiPbfnifoeP0ljYqMZuNq37PxpT5+vEdvH9tqAVJEJYax9u89UaAI92HT5EVM3je5OUicLkqmKimR9dtlM4RsTvftsOt1pMG/FKmbBJQL0'
        b'8W4RDqsce1YV90MrEQKLAgOIqkW0pX2+DOwVm7HD1A2zFP8hFl6ddkLNDO5nkqZZ4eVYOMMlTEPM7hYyKZlVkZ+DjxOcD+FWKfqHQD/GhnUBihTToRE7488pnzdQUSkm'
        b'ZO7Mz8JdLD8Nf37DkWh7G4cIP2qL3vB5+MfhiTGfhxfH+kTwUbJfIbd87b5SwuXb/AxGL6lTvrWGy90iLlRshy5O5FgVYNWL/AmqhvZAC3aBEiYGL9+4pOfwg5N7usVg'
        b'Mv5KH8tUTQajSj0YbXQNxlH0cPQxBiRJhEue0h6cA/o5EDWYYTu1Y3Y3GbND9Y7Zj/WbrtNpAN8mE8hhY9YQTv2OIesYQIdsyzDTWXhWUIq5aYp0ST0bzFgGxwWpuQjO'
        b'wr5p6bR5En3gPHsJW3CfIJ1IIaMbVsSrDkkkqknk/uRZyzfFekX6kbGx8d1z0XGxcbEJsT6RAREBEaJvhmwavHFw8MqP3MKOGkxMPiMRnnI0Cv/0Q83ha0/Lvn4sBG3b'
        b'M71DZ5fZmBhbSLfb6O4y3knih3RNj107m/SJud4++dZCv7yuJ/f/AIu8zu1c94JA1vUE/yqxitqsY+aUfxZ++8ePyWyOizGJuZcgEqzMxPcmlJG1nVl7m5KIysm04Ier'
        b'wHh5kFYLdsXqfr3Zx3eEdZvOZd++3xkMcyLpXuX1cKbTVEfp7aR3H8KfrjO//3OJR28H9d94pQEh8S0bXxCp6J/n3ljvG0F6xk8iSMflThDZO4V0S5X9NlV2vK9/T3Xs'
        b'p0Fynxn9eyhNb6zeZn1H/x6qJ6f/Xrv2l2PJwO9aVSVRUaPV+K6fHSM+frmTCDVrn7hSebyWH6GOtZGaG3uQTYtB4e6z3IAlTtTIJJ0n8sB90DYarqdR/wrIhyq88RgT'
        b'I2dbD/PQWrjCwN/lUJ7OAW+dZW54U5BjlxiqoBQz9fTquIdOGZf+dgHuAay3V2l6E/T26pu/o1e7fY2FfsektpoeoFTRat5YE6auaJwVxAUDmAjUy2WhwKBgCDs+HVow'
        b'rMA2xlZ7hKp47CPUfgOCuvFY9RsQTgHsYM0Qq4mM044X+fkeP9uDExb8aM+OfDjEYJsiFduwzZweA+FlOJ+WJhMs4JQYOzE3I52OiVFD4IIqLZyeUHmRvg2ERp3HVNoz'
        b'KszfqoC2hdiplLHDsYg0rFYtWkJPlwSsFKDUHI6x7RYqPClpKp6cky4jt44KZKwcmcFgvBOwZbhiBdnT2+kZUpsAx/F4WjqtJXRNSlONiEkjPY2FZLxOh3yeWPVOPKQQ'
        b'QQ5tBrwkwEEswCvpdGBhtZ+tynMyxY3EvQIU+8Syk6vvZhjS9rOYF5ac0Bk+SWBttgo6oZ6UqQkPYgtN6aQA+83wEs/jCkn1tArPxHRXRjWVH+LV7FrKDvH6tAw2p6Xi'
        b'lWAvR3o6QJoHy5aTWVMJB412ic1YorFwY8NErJzoJhVEtA1ueWDmlJXp7jSDm3govNcxsgbdZtnSFVgz0SfYUAjFg/PgoIz0YSWeTKf6NzZGhE10oWZ/d8EdMr1YG9gN'
        b'hibchxfGkhHtKpAkliX8+ODBA+Nwdnpn5xYe62dqGCAwaYukdWmMrzYrLPRi1Otlrj6h9lhEyhBsr8SKFYOxxcubyl2l/kzgCqKdL0s0XQdH4Ho6DT6H9ljIpX4hK3o8'
        b'SAcReeIYFdVcA9XN1BOAnQ6hC9Blgpdnw+X0CJpO9jqsMCUvVJlCppvcADNDsV6G5SGmiy2HymcFQRfcwHq85Bm71ShmUIoxXpdtkUOxUaAJNGOOiMiMp9zwxg7lSCyc'
        b'6YKHZHBgoRJa50zC2sGkQy9jZTp1eJicBNUGmIVZpoK7XALNoXB5NdbIoAgLoMYBcidhAwUah/KQYfG74RxmDoMbG0cPgw4ohTxoj9mBuRJ3e1KOspHYsmig/65xbPlg'
        b'Y61h9jDRJLEgtxu9afYHcWM5h28CHJioi8G3+wQXmrysIF/D4XsROxSR6TNZgi+P8xIqBcHticQMn6mmoUK6P+24U+HjaQ1qjQQ7E3KxfP0m2EvVHDwucodsPD2T5If7'
        b'wqENG/FQ6AQ8uZoeDFmLYkIgOxoKY/EYXjWMg+sW26IS2bDO8EmlJWyZ3a+QXs4+BpbW1K0HGpTkP5lXeMEIO0inhyhFbHUhG8shMnHpkVGFK5Z7O1E1ps2e9O8gudTN'
        b'y481wpi1s337UhGv2v4QKuJipUn8xpXs/DsN2uCqI5Hjr4xUH4E//Px7BpwhRWMMI9egDsqo+iASxFAOBbhXtBByoZCpyAZQPMfRizRcqT+fAK4+3s5BzO0kFK9hVV8v'
        b'h2VeRMlMprN/aZDzcrGwLcR829K0dGpDg3I8t8PXnCiJ9GDHe5naB0Wto3r5BbIKuyyTZ2D7Mi8f/wAn54BQTuPcw+WBJE1qXho0AE4beLL+/9xTwtTueatSnH4dGCdo'
        b'6nXZ0c8XGqe6qA+j5NgshkI8tDadxhsNGYclwV7QHqj059D7oSv6O9aECmTEn4dM0rV7sXStHVGWr8Ipr1Fwy2vURLgkJXlgliXUBkdzH4EmPO1MFsxWcyM44yDHy+bY'
        b'mpaSTuRtlSRQas10rhG4zyyYrlcSssQ1CmQlysHGlA3p7Aj0BJyEdl+lM9PXA0iZ7PvGQKyzWzNMDtlLsYEt0dOh1jcYrsmgLATLQsnEMHAQwaGVjiwrLIbrcEGRYUap'
        b'ffbjFVe6lpzfyO6tD8EjpKRXVNhqKIixSTTf3tkTcpUD2JZjjkehlgzVDqijvEDTBCz3W824pKA1dI+vy+Zu5xLFajFeJG1UyW4PN6GkB34+mgNrskhkwmEshDq2YY1M'
        b'J0olFrOT362QL3J1HM8JnU4OMeeuFQaCdIQIjwhwAq+tZjyuZOGvWO6Ll6zVHitwXiqYWEis4ZoynR0cZkFTKhn4SmZCoIwE/EhWjocMhPGQaRCTpPbvsU2W+iZDTjcq'
        b'mhwPiqFm+iJ2dzkR7AocsWSies4YCCaxEnM8vpTtTP6YAzd9NeTQm0LhKJk0lbyZW1aNdIEaLHEOYAensnVi621YyitGT1evYQk7X5ZOETnDLWjwHsF30Et4yd+X83+P'
        b'oLRL5+DkOL4PYoXFJMZKzqnB8yzgAt6anM4ONi9Fb3BUFxE7VGTs0qltIIyCfQZGeAtvpFMDNF7HsgSyDjADABS59m8ePDfDQAiALEOsDIdO3rdXSFEzHcnaesbF20lJ'
        b'1iaj6WI4PRyq4re9e9JAtYcIDRNTGz2DuxLfnGdxfeYIZbFl9BpXn91PfjMm8FTGB+ZeVaO9gmQNNi5e89zsb786wA3GrjSwOOaRp/jGMOijieJBDd8a/CasqJ35rPeo'
        b't7/4/PnPv3inaknDubHeQW0O0s9CXrj47MT3fN53/XBE/IjT2+19fvLeG+a1aPfQymP3SoaWLMh6MPebUo/1H37wt8YLi51TPeqrvr42pXho7Z8/+tNJt5y5Ow//aU3X'
        b'5b9knwiKGf3A7PpTv8lGth7NP9146M7F6OPKKUPX/7B4xYCn2k6ZOdx/a/JupfKZtN+Gfep8cuTa4GmnN5/9+sLr29//ITzhzefzW9Hoq9SvFtRsHPet6svU967PWjQw'
        b'eYut40/HisOrklF6eu2zb+yI6pwycXhKuHX4rXdPyc91eJ05tN0zPNvhouerDZ6i/LcX/v3y2sbPHH71W/iD9XrJitOb3o7/+KVhx4oWvlmYeDzuwXO/Lkq88uLtFv/I'
        b'u+sctry3Jur7teMXpz39z52f/bn+C7Mf5zx9uH7JJ9/7fBD72bDVXwXl/Wtc0umZGeaLD5jtfyImdumcy6+vnll2NexfHzfvD0qWvuDo5/beF3/9dG7q0xsOJMWLC+YM'
        b'd3519KHvh0d+Pni6+ZAfrhfavpY2WBVi6lZnGBP38hsv7PR6+ssrO772+XwYjr3zgfmM48E/z5l2+0r2iYihz1RcTBh5K/m1pw+bPV344PU2+dmfh1W4/7bF91lJyFsn'
        b'J7Q5pQ/oXH80ZuMHHyy09Ny369PvnoKj+eeuHR0hVH1+vDgjtvmVlxvqnhm1e+D3/sIHm3Jm3sx8etz623mLBp387pnct6b4l7/9g8fx2O92vuGc8OHVveOf3JFY+9qf'
        b'D++KNIh5MuevrcuSvNI3NF+qsToTfW38rEHt+OmdSZ/f8f8uYNLcBwYPamRTmwcpxzF3BCJAFi+HErg2LpBulT2cM7BiNnerOTECb6g5ufBoiGg+ZoUzp5GNK7BDswTh'
        b'rWSRK57BcpaonysU9eAhmY4ntCTxl5dwQq/DG7HWMQ7PBGh8NuTQJs6wxkzmiYHFG+CiL7RG9F0dD0Ele98LzkBXz+URyqLgMLRgO0++YY8ZlgzZrPHkULscBWCumgSO'
        b'6C9tJn5cq+QUKlCCbfzm+ckrHPHQMAcXJRYTjc9oFZm5RFRjSu4o01FwYbojJfMrciILFJSLnV1FjF4MDsBBb195bE+6m+WShG3maSwcr5VsAQXUu4TKLYHe/lDgpJFd'
        b'ZcJIXynWu8NN7utSaDrakbSOOn8ZNIonRlqzJk80DlwLtczXSO1ntAabmMlYhXV4ULVhNZTJU0zxsoo6Bvbz+yFrb5sMbiZiZxpzI2wgW0wmt3bOstWcRgiW3hI4Bkcj'
        b'2TNzBrv6shulsJ/aoANZhw/AAgmUSoH7zRBVLhtKMjDXFYtdnRn3oqFgHiiJI0ICe2AOFm12nEmWUCcy3ErYbQXeFGMHVf9ofw2FfdDguwnyeksYtriXVdsRzxlqdwzI'
        b'TIWjAaSzaPFWEIm5njmgQQUe6u25jfWpnPetyZqU/pKb2nNH7bZzCCrSHOkodhtNhn+DUpdtopfvifM2TjiUifnUyMdcnoj0W97X7QnLA9iDK1biEY2PDnPB8cL8Xl44'
        b'UDyflW/RltmOBlDnovTREAmZY6YkKcqbl/7iVgFLFOb+lDePNoEiUYyHI6CTM+YdXRTavb1tnwoXBvkzv63R6yGrhxywaAqcIPrMeeYx5YnHVb7YSQvfSw6Ih1N8rJ6B'
        b'nFU65AAipF5XCwJE2uK+SgexgkjJ3e5O44aRBrbBfKklXlycNoPNRaItFD/U+ENePNDXOQjO2THvOFs8M9vXz5usPkHLnUUOZNY3smm6wyDNl0ymXKeehIB7oEBp8u/4'
        b'6Sht/4PAtr//o9uGb94Hx5PZt94nH/3sWx7UeCtnZDYWjFRJ9kBMv8Wy39i3xERMA5IoIB6HsbMhz9InxSLxA6mEwuRRiHWpSEbpcBhmshn/JunSK0tyRT2OLBlJoQX1'
        b'PCJpmKjJCclPcsf4gVRsovZlMqO/SagPk7FYLqawvPSrG8ZXTFIRs5/8SyYSfymzoYQ8JuoUeQij1o7Wpym4FZA7L3HHIhaS5sg8iZjfUvTWbt+G7iiv7tMM6/9ajyrl'
        b'PUo4W1PC1HxtoRy1/k/M9JhHfnXQa3p8fcFDyBcf1mRKEQt5C3jEeSs9cRUx3OLfd96q8Vd4Q6zDX2F+TBolWIxISGAIrT14jUkh42npIhJ6AbdysK+oKI5mGGGXGL2l'
        b'X6LcG8Y+PHzp5jTvxJjwcLsNCUmRm5QuapBdjQdEuio6Jj2BuiFsS0q32xLBWR+j4ilRY3/O5Z6FiE9kD8YwDAJ1vGm0igehcoRFO4oVZRcfpXp8TkUKnTDDzpt5IpDR'
        b'qYqnQLYkH+qVEGEXma5KS9rMk9VWzTsqPFxJoXb0Om+Q9tG0B72MT7TLmOpCqb0XkGbcQhszLS4iTVvabv8QnSmq68bQdZnDE/fCIAlQrN1eTaQJ541NTUpPZhB8OlMk'
        b'VU+Lj0xPiEjlfiaq5OhILSKEys6eBtU7kSYg2TLAlm3J5NfotEgXJesEPX4mtEHTojX9ou535o+W2Jc8U937UUksmDiZ4jLrSrNXBzyCfFIk6CKfNA7gOuglLLDstpZH'
        b'bxOb7cKD3F5OFdEUbNveJ25iklQbNhGC+ekUZNYS8ydQM9zBQdSWaCeXUHtlZ4obVg8d4TVwXMouvBQEedC0EKrXLPBOI3rucWiWzw5wGo5H8DgeWQRdI7fDeQu3NXiQ'
        b'GXtWuXtTY598RGS48WvJm4V0Jt6cJSIi07KDKaFwxYoEogkXssgmQ2H0RileWLGUvT05w4DaeKft9Q5PWDtskxCPx48ZqGhg4omoT8f9+YZpjpuV57s/17/wlTBktOKl'
        b'ZoOQ+LiL9n4Dp9tbT3rpekJE0tCxnScDn55kZ5R3KN3w7XzXDUlDJ81ZsWRPzZ571QtNjr6z1sFjQe350pEmKVeeC4xo+XHaxcnP/bzzlvyNtFca3P8ld75gVtwwTjbp'
        b'25GFo4ed8LJVKrh79TXIx2vM21yrzQzAm1ShGTeQCRR4IWiEb6D7EnWMABEN9zIPZswePP4hUsomn/4OzHgTCpjzBdTY4zEVNHkFONtr7EtwCA8MwEoJNGMlFjMxNxnK'
        b'8YpjL5UnzDoDW/Ao1zzOwX64zh3xqRe+0kSEjZGQyYo9c/l8LPEaJtV64ZeHMkHPejwe7VYI8AoSpQD3e3GH9hLpUqqHTQ/VMkJyNYzUizkjjY7zVEuyWikWzwsa//1G'
        b'rGN+/kPSobaXJEukRijZ2i3JTjBQH8I90nHEiIYIsjnKBBgHXQLMHmEaE1so1v8D8imh4gkVS/o4CGiT6s0O6dJ7b+9HaSnmT3TvsYXk15N0j3XRtcdmCn9/SASknhJR'
        b'p1Ky1YSRvaYXwIImylafO6KkUPJYMbaaDfZHqY4NNjg6UQ3A2hvlPV3FN9xotuSR9dlzgffC4B7I7fp2qegN8ZGqsMiEeJIKZ//VQFbFUAjKyDgX9oSLJ/1cyB7TBwjf'
        b'I1V1+8xgzotOWu9FClisimbFTEqNon8g67/O9VkNcK+3DC6LQ/3CGWhdenJCUkSUpvaaBtGZKEVF1YLQ0a1D7d+rSo9P4zDz2kLp3jUeWaqFC0PCnf7oq6F/+FXvpX/0'
        b'1fkrV//hXBct+uOvLvijr6709Pjjr04Mt9MjWz3Gy5P0+I96x3DWGy7pREc52Tmoh79DLyfU3l6yzE9Ot2iiz/d1cWoEw/7uHsO/x811BRVm+aqQMdHFrddsYe65HHGX'
        b'TyeSYUZ8xB9rqQUhoTqK0M0OTtcYXg4+3eKjHiF/SYUeHLZa+WsgJ/8WyfmRvDAlwq9jpYfADlBiDKHVepxKQY/vjwlQi7eSmF+BwhhzsNVt2iw3NwNB7C1g/SAzdpKD'
        b'h/ASVDkGuNCzvf2rZ4t8oc6HHz9cxqO41zHAR0zuZMM5hWga1MazXHZh7iLHAGq9gEK8pBDNEsyVUnZIMgzK7OkBF5RBnjleNhAkQ0WzMRdb2N1teJLIEa3YPMApDTvI'
        b'jo81olF4ELJYGVMG4lmVB9n1RElTpgvQgbV4gGVnYrRehe0ugeZkZxPjGZGDtSl7Aa8NgxLchxehiZ/Uq7CUVSoET86BOk9Vt+cBVuxS+zSaJhBpgpQwfUR3+a7gXla+'
        b'WGyEvbR8UzZ1lw8aIZ+f1VST2p4niZpbaEsCRx1ZUYaRt4rVhQ+GXFL6eE+lhLVjDJ6OohnOgnptjvPTWIrGQ6bT3Bywo0dzVKawFB2xJlaRgbXbjUjPS4xErqPxHGuN'
        b'bVA+VGGqHEPxZyROorl4mjtkUlEnnx7ZwbkFCjORIDERzbV3S6dQ3jR2rtaXNH02ZGFFMHPvpSfAK7CQninu3Ukk7FLMheukikdCyC/VeB1P4V4iYlfDdUsDrNlgYEo+'
        b'/CEPS2fZDSSCoqU5nBMFx/8Y/L2goiCha2LLQ1+aGfCkm4XsXm3K91W7ZJWVH5+bZtDhhaLFjtV2g8bMszIzkD+bZlVtFfD0KAvryZMN71mF/OLd/nrN4X9OvfX05TEr'
        b'Qlr2frPvyNKFy6oTnwmQNNz5xmnZ80vOL1r3xfOb8if/tSVgw4x3Lr8/esWq50wN2x3rzgz4/h9PDMvyfn9SfENK1V8neSU3Vb9/q6Ah46NbSz84N6dryIyucTs8PSre'
        b'SvW+8cLLuwpeyEgQ/Zz5guG3P9xwSbk/6FXY/dKaxG+rl795x/Po6le/WfC9YdhXfmsXvmEc17Jn6ncm25v3zPzOdvu0j/9VZfP24a7EY2UzzyzZ/UTY/uqw3ySVynXP'
        b'TfdTWjF5dALW2jIEBTiOdT3N+jehg0e1FqYmEpk9DHK7DfuHrUOZ1ZIaeLHE0dfZYY1cE+Vn4iQx9IXDzEiMRyZDsfqcAtoSRPPhBl5gBvVVcMjeERqWWDh5GQhSyBWR'
        b'Gb53OU/0Kpk77TTKFmogGyu0YbY+Lkwkn2bjyeR1OvK1pxSzMY+fMpyACxMdeUzkFioMy7FEDFnBcJ2L83XYbKNSYBs9NC5JwZMCnsN6aObecrkj8TSUJE+myA8FMsgh'
        b's89yD48yrR+I1+ktGblFhl+8gFVwFI6wFoqCimR6j6ZZBMciBNwLe+EgM8biCezA7B4RrN4OUh7AijVwldmLZynGq9gpNpwZMllAep5cwOvSiUWJKiiFQlqgSjL6jwqk'
        b'zu3QyrLFalLaq+RVA/LqWdkC0tqYTdSWQVzluoT1ZLaTNVYEFyXDBaxbj6dYNVeL/VUZKTS/g1iFNwSibRXARXZrOmZCHrlJ8oP9ntAlYLEVmd7MqtyyarJWmxoVxvta'
        b'rUsdNtUTqfkQB2ipiojETOEI161whFMFg1oqmcpBvqXMesotn2KmfGi+TFgkpbFYY5vUfpM3yLMPxA+2D+jtx0zyDtCAtLAAS5OeAnVqUS99hfkekrqUanWUIm0cZAm5'
        b'uv0QReX2Q3yr+5eJqGxUNWHxXwHKQX3Ase5KwwK9A+4qwhaGBgV5Biz09gzmqKJa0Ky7iuSI+ERNgCSN27xr3COCkJk5tbGjPcI8s3uDazGsrTyRWg9jdeSNNfT/T/b3'
        b'1CVUSaQxqBvIb3JDCwkdC/JfZTIzg8HzqH1dKv6D4J5SCwsLsRklnJMKD6Zsk4ushstF3AkmBxpN+sAiiYQwg6FLpPHDMbefD6+J+qfKQdSbgI6CgnFAsCNSNSQYv6bA'
        b'YEbki15TgDAKD8b/3n1tQbE5owaya6soa+21TdQgcj2YXQ+JGho1LMr2iIJS2xXIYkRRw6NG5MopNmi1YbUoSlFtUi2vtqRfUSPLDKPcCyjgmIzovWOjxjHwLENGCTch'
        b'V4iyj1JSyjv6XrWiWhwjJm8NJN8W1Zbx/DdLkppltVG1cYw0yiHKkaTnQcHMaIoFRgWmBZYFVjFyBv9FUzZiPrMy5kM7IEYW5RrlliunWKRSYbWC6dET71rS2bGQ0WIw'
        b'8LiY6NT7Hr0kzv4PqBndej5034WIrzPiVUkzVGlR7KeHm5uHxwwqBc/YqoqaQWeMi5ubO/km8vVEpeSuNCAwyP+u1Mt7idddaWjQkqUNorviRZ7k04hmGRYY4LeqQZpK'
        b'jQZ3DZjWedeI4wfHk0uDGKI7q35Ptu40W2lqNZ1mNfRjP524Uu+AYO4o/zvTmk7WtN5ppR5jCQYvWj7//oK4tLTkGa6uW7ZscVHFb3Wm+kAqjZF1jlTHFrpEJm12jYp2'
        b'7VNCF6I1uHm4kPyU4u70G8QMwyw1jII0kgbyC1w43y+MqAn3x9NCL1zgzUpIfi6N2EbXuSBqQ1alkURd3CaRT7Lk0cQaRKn+HOfxEC2rSbB3wBI/z7AF80MWej1mUu5k'
        b'ia7uVeX7U/u8uDA1SaVawPSX3mn4JcX6q2JZSu40JXF3SqSA52ha5n3a4/5Q/ZW6b62z8ZSKXqnQ4ZZ6QUfa01Ob6F/7JDKdJTIxtZHe05+5+33H31HTu4ZR0TER6Qlp'
        b'rPlZX/5HAhx0os/pChxhKlB6DNTtmaHx7aOOfZfhXPxL79wTWETJO5+8ZbuExZQkiASpp2jxpDUPiSi5K6eMsmlkZOsPtaJfSzgGbO8VxUXzrv5QhCukGrPJlcpNtwiQ'
        b'KTz1kHCEh+XZYMi37Hgd+/Ym7eZNR+ontEwhAf0CGIw1LewjqAMYBA3zKUd4izHWBicYP1ZwgsbMmW2ow8zpzeOP47dH9zB2cmojfixF1+iHGDeDNRTEdsmMaILJMaoZ'
        b'/R90tuszj+zsF3kqH/4YnYePfGK6nb2DKp6ecWVMdZni8BhJ8qltZ7/Q69EPq6cwfdjJ7lH56F9e7Oy9Q37XG+4PeeNxVwqaRN9C67Mjq21h3GjEQ8PVpFYawgR9b9Lt'
        b'lL/Wd9gkp8YnpcanbeOwxPYOdJOmdGF0m3bQbVp0oJs3fYZupQ7UjuxA90AHpUv3MewUFw8XtxnqR3Qn031i68YeVafa/ecp7M88aX0V43AW6qrpAKvg7TNBxfAq9DYP'
        b'O8mY0RtbgE0y3dATamwAvWXqxpeYoSXI7Q8hQeEctIf2Os7k6T9yj3EbUtM+M6kyh4HoiDQ6oFQa5rceiBz0yFoPQAE1y5J0tkSkqv0LehBusNaxC46OpnVNT+hBJqcz'
        b'qYXzQzyXBAatCqPMRoHBnmGU1CaYlVJ7ts8p7vQ2El+EePswEio1wIum3zT6m9qgrPsovNvIzA4ueArdNmCHPmuKg15nAtZDyXyeqjhBXp8lxoHXTvNIfKJu9ASO1UEE'
        b'Vg3fb1xEop1naJAeY3miXfCW+LTt0akJrOPSHlJ4viDqmUtkwninRSRsYy/qX+Ec9I9ZNcgI75Bu7BE68tVdosUh4edWemqUxn0jeuCW93q3F4aM3lWLpdTvIIE0j1qq'
        b'UmmGb590dfeJmjOyO1/G1bkhOiEpMZam9AiDO5VQjPqJVOYB3P29Ew5CqTE04z5fLMdKiSDGkyJ7zJ7K7K9RUAF7uT9EylgePyjHfO4PwSx5xyfIVKa2kK2FRd2NhekM'
        b'5CAX6lRUI4ZSCvuHHeSrFYqkginmirEEbm3h8J7FS5J9e8Z+Le+OrdmFZ9XhNb0RRP0NfMTCZMgxw9zlmKU2gW+1gb2r8AS1FWsMxViDV5jZeQWe3RiILQpTjXl5GZxn'
        b'EV9BcAHzewDFdhdEGxaTbGoaRHFi7Z0DQu3tsRhLXbHYiYKCctBTZ2r6OwAdmDNQJIH2xdyq3hyCR1QZeGFgN6IptorYEYefKT/iqPTcbpIviRcYiCo0QyVzuNWG/HjR'
        b'A/4iJ3q0sNM1CAv9lnlJgqCIBs3hNTi9bZwAt6QKPLgIW+O3LlKJVcdIMs/snDquzN0Y5ll4xsbu+zxx7+rmf/m0Z78QPmB+1MCgcRal0PGt/Fnr1AWxbUO2fvXtgzRp'
        b'9tFt7uFSq+Zn7lVeevFc0o9fPPnEvyaNv+w73injg5ftP9i7bvORsSP9Av95xzporGLLu8Nf+DDCYtFhl0n/vFi05MeurLve4l/e+PXiinfu7bf7YON7H2UIU09Xhri+'
        b'c7ai5vup6eldn/jU2eSWW9WHub3vNm7kYqUpM0P6CNDk6OLs5YwNUEOdIU6J3aBmGgfHKIdrUMIBmimmtBP168DcyYaCWZDEHevhCDOCQmYaFHb7Z0AmnmcGX/vVzLfE'
        b'EjsmTMeW3s4lzFW+DsuZk4aJY4JvIN7APLVziQiuc+tqO1ya3T0iE+AUdw4PsmAJB0emad3lbfFwt58GyaeZW0Rzt1OfC61lN4QOAWbahTqoZl67odgIF+gjHpDdC+pQ'
        b'C3SIB3Avs3r7QDHeUINSYkW8kxaScqc1a8oMM6y2phF2PfzrD68bwduoaDcUQi1kkazo9LtC7vuLFkOWNbdrH4MCuERmvQsW+5FG2CByx8LBvZAqjP8tQ5wWPm+ePt1q'
        b'pyU1x0m4EyxFIpGK5A9kYvpTTP1JGJ+zmVgsGqpHI1IDxamxcmJFuozLCb3Q6fwfqpK1jfidKtnvQarL5ehtBmEMrE8fjFYZueI4dboy1PJIuzyGMNwXY44asYK95gfd'
        b'lVKW2LtSShirNNTliMvdXKnX611DNa94apdIRyi8uWZjCRG0ofBclzRRa5OmHDG8wDzG/HcGvGt0ynO6dMr5UVGq3uzYmj1Vh/1PK431V01j7GZQWXFGuBbEJFzHOb+T'
        b'WrbRwnJRt8r+Xqh9mR450TFV27sl1jTammlqef6xNCW1jKvlAn6UssSpwPi7Ogh7I1R2MQlJEdSSYMeYadXUm/qcbCISe9Hc9eX51VeKXhqELhretOitXDxO0zLXbuYu'
        b'oXp8PMkz8VFUtutuim6yQF4HO3vGYE+rxmS30UGLXVxcRiv1SJ3cVYL5K0fQ0dSDv1qbMifo5NJw932d6Wnf6ebbVA8BtRtXb/ZNnWnYB3ku9qTHOJ5hAaH+CzyDnOw0'
        b'SgqnKNXr+sUclPVT1SYlc4fth6SwVZfep4cT9iHJ0X9atZC28MO0Ni1UnHpU60xNQ0CuS8GzI63iGRQw36+/Mqfbp/kxFTwNaRhvCi11Mx2w6nFD5wXRiaMZO3d4eEBS'
        b'Il0pHuLsvTWtO3dG7EvbKCKBOljTBUI7dGNSkzaTpoqK0OOVnZDO7Wix8RnRiZqRT6ZmFHX5sY9MSlTFk+aiKZGGi2d/Ja2st2A8mZ7WB2XPaqqJrDdsjI5M4+uBbn0n'
        b'OHDaFDd3O06ty+tDy+CkBhtV15eZA+jcJIuiznRi0lPZXGOznVPk6lX6+M40wy5YrWRpiO2p3/o2kktCApl8Ealc1eIP615bVKqkyHjWCVqVLzk1ifLT01YkTavubDIR'
        b'+LDX3Zg9aB/tAojyF5GcnBAfyZwRqfbN5lNPP3zdc2chXzMiumlm6aZtZ08+lU52dOu2sw8MDVLSzqBbuJ39As8APfPQoUdgwRSlw2OEO2g9u+Zrl/o+TE0P8xjtpXnK'
        b'dWqeIzk4DWRaLSWCORGFr2mxafAkXGLiENOU3pEbCgfHjRQEu/CEVyWeXOO0hlo8rzI1FUOmvVrlHL5zMXfuaorFLhXeVHa7SIURRY/eGjkc24hUnTO8G9MFTk8IYT79'
        b'e4g2WqDWVDVaKh6E42pNdemk9KU0uSrIw2NYoqaEoLQhIWqgAl9nh+VeTj6hGjwIKIOW/korp2+45DmA6DY50MXb4AINMVXrrETz2c/01pWD0ikvLJ6CI0seI0OiVnT0'
        b'1JK7GXiW2WsxLJQyYYabFTaL4ABTiZ2hZinTh+E8VDOd2GNxOiWSjLPG874M0sfZJ5AqxTwNA9yLecbjhkCDcbcSOg+z8Ai5ccIS8uBUCByLWgZFC3bDIcgm+s0FOEl+'
        b'5m/aCpVwZsGG9VC8IDV+2bKN61PHrYWmkVC7Kc6CqHuzbeEIdMRwGg0/JwW2J5uInVMFMV4XucLNCUxR3wpnd+stFRYNgaJ5ULVhKRlMeb1KlIcnsJpeU3ewcHMssBOg'
        b'cdmAwfFTWX6wb/Q6RYaRSmqJdcwfDcvj0qNo2xfgZajSWgaUy9X4Pcnp6SFYmWxqjntD7OHMIt7iPewG1FxAu0YD81GqRrkhStg5Oc1JMMNCG2wyhZp0SvBq6LRA9TBg'
        b'JfpOiD3ecu3Zk9gGBaZLqBGFoezsnAj5vgE9CJjKoHEpGy8kVV+GOEIG0T4DvLxYRfRJSzLCi3FfEBmHxSK8lWK6ZKwdC1vBIms41i8hr27tdHmv9CBPAdVW4/CMNZyF'
        b'0zbWEgEuClDrPwBOOw3kxp0yOAd5fVCRsB1zGIsKHsdqkteVWaR7sjGXtC/zzIO9G0jzB5kEYT4UpS9j5cIKzx5WGj9vpY+ziy62FDIZKrCLF8+094QhrVaXbglV0AXH'
        b'0kOpiQBuxWrAItySlnk9Xvp60g7ysSIlz57PsTFuGEC7KoPo/WQZuaA2/0TuYj486dREMB5O+TkOytBS+vSk81m1i1JGxh8fMFWsOk00rjvZO/2X3Qh4a57FO8N33Lg5'
        b'8+dMiZl8mfGfZ0kD51lvD1gwxnhN56Ipx6w+Gz/oVNanI25/qfxGXlhs/IHIPnBbbuHepB9KF/2j9qvYP01s9aheeSf70wb7qFVZv7y25G3LTWfKhxpYWbs7lid+PG/y'
        b'6jmjszeuTu18xX9syvFpGS8brPvs0yP+A/9ya9oL3t6vBi5J2PW+VcKnV07uPbTyxJRP7vzwQadl6btZwX8737nlzM1bV2YtepB23ub+gcVT7g3Y/kve93JnRWPT0XHx'
        b'BXWdbd8m3d6H3xr/Ze7WP92O3Hqy9PyDJw6P+Mst2d+Xe/uuGz495yvp3bFbT264cudfA77OePC3H+qsdm55YsgFx7LryX866WG87fWBb0y/+taSQScDs+bM3HW09IXQ'
        b'j9/9Je/bpVsMd/3ts93F2603Ln93xvp1/3rll6xNdy/sD5wqe5B5VfSb0S/r/76r6Xru85sc436+sb/98M6XfqoNe2rSs7M+DPRPvTbuJZs7AVLXCWO8o+1eG1e3uXFw'
        b'bOybuz4Y5dAw43ZuyPBbYa9P3Pvc1bc/+XpG8lf3636ceHHRq7V/T95fUPe35833XFj14ecNQ3/ZLZlSctl97gSlDXMHNN3uyyxHjpDfA1YgPpB5VDq7Qxtcl+gwSWWG'
        b'cjCB0mnYynBJ87CLBzxVQSn3TzwZG7Xe0LcPxIJMxG/mOuJ5tQEobYfaBDQAa1iu5itGQ0kfJhb72BRJcCqeZEaibasNN0xlrC+9GF9K4Sp7fw2cC1csX9ONEKGxd+3C'
        b'fJb7FCy2d4zoHSmV4YRXuTGtEepoaFaDk5cBdgVpPDoLyG2Gw3AEjwY4MhfegkBvaJQKsgTxaDixnnmJToDiXQy0gqwMtxhrymioZEa4tdFwUGNhg1N4gBWce0/WJfC4'
        b'+Dpswkv9qERoWioNl8i+hayMW7AxHA8M9e2LtNPpxurnBJVO5J4TNEhDoEmQOomgEyqgjtv6asnm2+II5yI1FjqtfW425LBaJNlBnaMLno135nFfp8Rui0LTKKsbNMOF'
        b'bb5+3lDk2hfwyA2uYvlUmStZpzkOgMQBc9nI8XJahzU+gUSUMFskmQ2X4BRv6DoiPZxzdMZKvKyJSROR1m8dzIaWNdmCm6DEdSfU+DsrSTFmi+2WUw7Wx42FNv/PuOrl'
        b'aeAf91JxUZeFcI8wx1hkImZh72ITEQ2YtxDLJHKRpYUJdwGV0AB4SsPBQ+FpIDt1+ZSpQ9otJIPFg8lP+m3DQuQpKYeVSG5gRuPWxGoLpNiMhtSL5A+kYjMxD2iXibeP'
        b'1mGB6xOfHfComPZuU1rqzd7xbo/f/D1D0W/qiEfXEYpeSe2clBdOp50zU/jGXr+l8zGqrd8biG78zADIXUmEGJnWL0jy2BD6cUrp/fB+ykVQdCLRa1WPsvIxk4JajaFK'
        b'bITKbqW/3yN0lQHke0Q/XcUpIH0+nV434SLm+PakvOyBVieazw6tVtj3I8/BI9Bkag23EhgcHrSOx/bJcMlR58a/wILpN3ATskyY8MAEhzkhWGE1i5+oHR4DZ+mdNBey'
        b'DLtkkA8f6sqOFc5j1xtMTYImFkoRMXoWTZq8PkKYtp5M/OuJXNc4jmc3a0/5klPYOV8sFjJVy3acRJCu/Dvp1HAnj3VTOYkb7ofjsxgypSAESURYL8CtCXCd5WKE5zYh'
        b'5ViGwjBXwZWoTrd4+MqtBKXCKJXivDUI88Zh0w44yjSwzWShJsurA9kiNkG2dJsIs6DNnFXZ2YcCcpMdxso2wECQ2YhNoGAXS23sBsze6h6MZVJKPSqQdbdpEzu2NMcb'
        b'WKtGlCNCYydFlcNGIv5d4xihbcOH8tO+iU4snKTTlrfBLWzZRqNTWGgKdHix6JTJMayEGePwKsOxowEtUBlKY1rStrNyTLEdpWA8kUlwgVTNATpIM7AAgFY4hIc0h45Y'
        b'acTOHfPNOOdgkQ9cDoYyrA6dR5QWrKFYdfJAEV6ZDAdYs4/MKBdso6fJBLdwlzfiFnO1NzVitLBoaRepcrj4pZkj+B87dnkLlYt2SoTw8I3ntyuFfjTQ2vlHRxqjgbYh'
        b'M044JuwURQlRojzxEOG4hhCaspJ/Qg8EKG/O/KhUv/jE6AY1JbQ0gfzSl9OaWvnXydTnEhwitJyeaDKPZ35QaaSRhnEvi7MQBU2ZjtewCIqmY55KkjFvcUyKd+ruRMga'
        b'Luz0sIAWMSfbtFpsKgyOKjcUloY7OXtP5bUtnmAjONn+KiGa/9opUekCG/9QFEEkBwY02I0yiLW4nyENkotrrEtmQ4snVyKJRIVVTI3EM3iSdeRIosJnkbspphJhvpvE'
        b'SjTTeyjL8eg8mWCy1Y/mmGC10ZyCxdOhGZAykI8jqIcqOpIonCUbYnGwfztTHYUgyKOqY8pa9sasuPGkXUxTDQXswC7JeNFs2O+vFDEM1qTAPaoAKhaKFSLzVXZQbfpv'
        b'd2Pqbbr0A/14UiT0IyOnHdek7TjaAnGGWKDIwHZzsTAWSkjBp03YziqER/aMX7JCQbUUCtFYuxzL+Vl2jjm0YasJthuSSb1P2G1I5IouG64/nyda6Q0FvcpPXiYsw7NE'
        b'raUvDcauwQp7B0ds8SPTojNM7iNejUWxDNsQyqHFGFtdfbAjBA6Q+waQQ6EamyE3fum0H8UqTzL0Z5/6LTrUt8Iq1OpmR/2vh77Mz8ofkj9k8J8inpg6xnzA0387d+5k'
        b'efaY0TnFS14aXbvx/LNPHlzjEnfH4/apDaXu+QfPD3d3WXt1Q3ypYnfOrczm8M0rf6wLfnWMpOTN9Bd/2JX+YpPqL9fqphX97W83vvf07Lzk+smTirSYqprPVta0m+7I'
        b'nNnsfBJPvvfm+x82l726tMV/ROQFh8VPPmH07LR3h6x0mXbgl9d9J4Xen/H9QIV96u4LpeW7A4qd5oSq/H8rzD6xwSEl/fS+c43ZoS+EugxuTZn8zw9DP3X5e/mmM/tf'
        b'TbX+W1nsp4ahn69rlMS/b3s8YucrwoeHN07JHezfuL/B4Iu1eHfe5G2Jiz58N2TJ5PNnO988tvhiWeK5kIJ94VNfrmzYcmdohvB6zMZD+eGJ53coFru/subepdz3bKzq'
        b'gn4d1+x8Z0ZSSdPlpvc6/rLmmR8M2qr+8lK+R8Dqjbfzbi2cmT35/lybX32cP95zsuzai2338MQN0dtTXvur28ToDw8vLX02OPrN57win//I7HoKzrwZ+fmd4rtfT1ha'
        b'M/yNgLtPFt/5tPydL3I+8vl8QW7DPdGzs639zi7/cepLbxdG5Z01ODzAN3qHcYXV5t/+PPTdGS0f7j2248ZHTwW9kZNn6P+RywuhbuZG37oddDaQfF41esKFoY0/fzYs'
        b'ffkry4deWzvgw5e3Hdny5Yc2VyoiZpe3BR58o+3Qync3HwsU3jYvrdm537As4Is429dGNU4o2RJX3W59bZlp146gl/Cldxv/OdPwg2CD5d84zPT4esXV5+o/nL10WZLz'
        b'R5t+EL9o9Zs4JvGLkC8+Nl7y+a7NT575ojCj5tWXAye5ZDhvlQ349ONfRwUv/Mua5x786YUn3V+498bNM0ZFKTk3gpe/Vfymo39QSsmu2n3tQ/a+uMfss22Ng5543tcz'
        b'LPdflh5vvbtug3nA66JvPObeHhE9bNvmiN2TDq7fbaNystm+s6mj7uv3O9/JODHuu/ZXZt++cePivi2N730RV7P566OvvHj5wNMW/yj4ecari5868vX2Z8MOHPlh47Tf'
        b'HIuM1z9VHqaweX/LXP/dsd6v1n05N/X7cr8PbF//W9bUnKlBU9+fvnXfz4d2TT8d01wYnLHw4p01fx12NXL7voOWU+8+HbvePvnDxAM77j3zhOsP/8wYsrnq7KL6Vwoz'
        b'LhyxnHrd6XWTNbPG5XUk+rz19aFjO954T6m8nh78Xv6eb6rlqr9UW01/TpmChz3GdW31yb22w6fc9Myig29cDnxjTv321G9vtH4/+WnfRKPnI4599Y1Rc9juH4xe8bnx'
        b'8Y6VX0WkuF6vSPf58pRyW0feA5M70q+WzDsQ33nkiVfOPLU/Puea+IHklZi5/+r8cckzc6wCP7paNfnM+9Cm2HNv/IPCncmxzXMWD6r8/N6+J78cNPnez3c/s5ry91d2'
        b'xx+98ZXssOcX469mfP3icddfk1+dZrrNpi1i543URS8nftcxcvix2jtfjTgxO2fVkrP3Xz5xbq5B69jXYnd+a7d+Sya+d6njp2E/2zz4Jj6u5qrsQdHqWh+b9z89eL7+'
        b'Z3PLa4tqS95RbuKQH2cS4UQPwhUrOKfWZDnhynZnpkOtgGNY3q3ILoRrTJfFykAOV3IRD8MZKIlx7KfrGS/jEYrXXKHIl+x9yljM1dw3d5PEDkvjxOR5u4epVdLlcNG1'
        b'W2sd4sGUVk+sINJfT50VM+FWL78QLzjC1HJXvL5TGNZNxKll4YSi0Vy1ptGSNzj6oTVmawAQo4PY61FYvkRFpdkgsu6qg5VM8ZZkHrTbMWLKoXggVeVCco6NcU4NUNLN'
        b'vZV542CRRJiEF2TB2L6Oa57FcHgSV57JCp5JEpKFiR2IblvOjRoN5Kvc189BJojXiWKhdio2wGnuntIpZ13i6g05eBJLaRErxOPw/HymeMeFwhFfDWTcFjzCUOOkeJBV'
        b'LxiPKRVY6IwtWOorEQbCXkO8Ig4cMYpVTwmnh/G7FjbkPraSTcYUCokosCOBu77UKKBODVCbMkg6RQQNUJTCUo6cCa38XWdvkQBlkCM3Fq8whqNsEKTGYK3KwRvLk6k5'
        b'GCsCDIUoZwtolqRhFmdhXWgY4UvhV46Q5ioXBAO8IZYsAbVr0LE4OImtvng5kIJ5KqDBXkYk6Q4xnI6Feg70uA8PY4GKAkrCEThoRPQNA8EYy8VYgufhMhtHHgHptIRG'
        b'KrisxGbWAKZwXTJwD1ZxHMJyI6jjRhcBs4jwzK0u1QNYDnGYC5W0Nx1dlMb2DtAgpT1hOViCmdgGJTxOdD8Wb1G4+GK7EktEwmpvuZl4zXhTNeYl1NjgQbyholEhVFQ4'
        b'Nw3PsdYxmjAfW0nj0F5hmJgGwtiwATYSqE2E/YzTCA9CkaVvDxLTAIMZWEtGcrYUzkwCtVmoCS57qVy84ZJotQl5TBDMZJK5mGvGG/EmXhmh8HH2S4EmLzJCVUqRkugG'
        b'Q0KkS6B0GcdBPYuV9maG5A5V3ci8DCZDjrbc8qFw2pdiX5OZdiWQYTSaQbVkFjbPZhWIgAt4hZTch7TF2V4Qj9CWxEdOERTiYZW3g1IsLBZLoFoEZXN5z8NFbziwi8pK'
        b'WGIgiBQCXIcWOMbtN0ToucXjqQ9G9zDhQZcfG+zxRJLK1oBABkMnxUY+gfvMODZQJtTAPj7HXOF6DxtVWxSPJm6Bw1ihsCetAR1Yl+JHCmeMh8TQBQVYzTJYN0xB6+Xv'
        b'LKLo3reM3MVwkMiynCwX9s2CKwoXpQPpOFL0aTJ5vDjeTwPwWiWCvY6kq1ySoMyb4y6bQ5lkww44wet9fJoZyTtl+KwAKsudFeFRIvh3sDk+HU9JFEqqKswbQ5M2wIMi'
        b'bMOjUMAyXhOEmWrjGuXkOsCsa9hqxCxn/uNHkHlA67onSYJFIjiZThYVVt58RaCvn7cSysJ8nF1kgsJHjGcTyeygxZHDecyiHTRtbaofhYAwdZXI1zrx3muF6lmDaHH8'
        b'6NC4SvsMm9itQLcJRKNIpU5yJlAlhpuiYdBgoYaLNSPKq9rDbqg9N7CSQXqI43qWqqBDK9Z7zrQTwxX+WqY0nZqDJ2BeT5TZabb87v4hkEeLiZcnpvq5igTjeWKyCrXY'
        b'MrSn8TONoDaAckqX8qlK/UBJma3I+osHoHEVe2oHmf3nVViuNIaLTthOV/LLfqIoKBGGWEgd4EwsDwg/7SMhidCbA2dQcXu5CItnGzAvSNjr46EBBhZtNnRdph4uw8l4'
        b'rKUHNxnYvBNbpYJ0gGg9VI3kCR4hQ2i/imHSi6CeDD93rNiznS/qVzdjFRHuscheLEAeNkuwnjyjxDKWbsYKPEcKbO+zxUEsWCw3hH3i6Xga29lIs4ki20AJlgV67wyl'
        b'B2dsWJiLJVGYG8c32FbshFIGBH4ZL3XjlUO7Jec/7iJ/vaVi+xVZXPnauDtFGAwXpO5kf+IWb6KUYw1f4qHalukfh8mYpVsr09rztw9Tt3nlZiVtUDKX2siAgHYy4OnA'
        b'jHGDUrr1UqfJ5SIFVjqvhX3ceZV0wznMMlWR/jbCoi3kB9OABuI+CRwFsnKyBvQg86Ocg6CTPfMKnewnHUnpmP2nwUkOJa7+zqaT1YbaPZjNB9r++XBKkW5qJBYyoEgy'
        b'SjTfdi5f7jLHbVBhKXVktRKNxOwxcCuBtZebAd7kVYmDWu8U9ogpNkjGDV7Mp3YlKdRl325seOMUjg5vhCfS7OkDTXCAlJDijrkSSaELi/2dlN7+ZPVWwzFPmyWDE1sD'
        b'WG67MVfKbdRktlxz0hqpsSgkjZGZHMRMKYNVLgqEsjR9GO0GQihelLtCqZr0vWWjlYI95ZzCVl0oWzSAzFKykeaHs/6ciCe8GUv3wNWa4xFK0o0dY/mgOR2LFWRMKOES'
        b'VvKZ5ikmw/sCnuajuXYxtNP7YrIXXJTAfhFZqxtHs+FqZ4zZ9JZroHopmSwhTQM3mIy0iCRYrQN71yAcL3PoXchL4oTWh0k7H9TUgmUFedAwANslcCqQtDUdvNCYINdg'
        b'3BOxozG+J8Y9GbJVfLGtH4b7FWxThOopEuwQwTkX5ALVWEq0pMBijVTki4fkgnjZWshlr87C1llkkfchO0CLvwSvkGlJpEOOC51hvAyPB9CqGvv40yFDXreCXAkWBljx'
        b'Xb9GDDdI5x1VKAVBNJTIsngRW/iEuWAEV1UB2OJKxAm2XrtBtsVGCRTbwSX28kZnMq1bnVxcxMLOKAnWkr0NGkfy4V4FLU4KOhPESlIVrBgxAJqYnDJw4DoVWeOxyEhb'
        b'I2i3EAZjpXQGFC9hb3sSMSpH4eyinLmWVEs2QjwQ6kxZWwwhK0UnY84JcHYQCXjJXU4n8f4MYy6K12AWlKlcHbDZi/QGlo0whOtiL7JhtqrFZzhlj63OAdgRZ0WXiF0i'
        b'rCHLcz6r8fRpu7AhoieWsgZJGZoms+x9E6FZ5eKTTqGElGQlIDKcWAzVcCGZyzCXIc9NLVGvD/U2t6crnSlek0yHEs2R3wW8Ke523F6GFdR3O0LJAVTqnaDS18WfLNvb'
        b'RMlQNAv3kk5md6rwEBwjeyr36B443d0WO1n3u9nNZ4Y5ajJeg1c5AIqbgXLAfwY9V/aI+xzSgkfiylKZYZ+dBC2nFjHdJ0F7BAc5gy7mUMjGIksG5EHhPKwYBiE9yZEz'
        b'P3K5Gg6ZXtuQu1bioZSm/YFYYiMa+kAsHyqy+1ZsbiGyeCAVG/8mllL4ZDPRWPFY0VByZXtf/JvYlAIem5A3LH8Ry+j1WLHsgb3I7Fcxed9CNEJk8Zv4OdlMYwawzACT'
        b'KWyyyEI0+FexzJb8pLlJRbbkc/BPYiNLkhf9nfzVdDApCwUwsX9A0jJ4SN7kri15lqbLAZjlJA0rUh45SdHse5lC/p34KRNfDdwJJ5+3I5/jac6iwb+JaWl/Ff8ss5KL'
        b'tg/RcazDW74H1+yjOq5HhPOfSFfZykifUWpMPcdMmcKHNvoPmvSXiBSDhdq3i2gAc0CAUko+mAt6g0kf/JPUjQKL5g5e6OXp7xnMEE9Y9DUHQInXopbQ8qZSnHN+ZGf1'
        b'X8Elmaltrio6sumpXC75KRdLZWoU7V+khv+HV8/LpopFZuZydpRJGvqB1WwNegkddOLfpBL61xF7BON0dgpdTdbQfVpD/vnInrZ8sTBrtYxoontT+wXpG6t/qowfjmAi'
        b'iZKrr416XBuTa0WUCbs2Jddm6r+b97hWo5kcMdIilVhFWfdAKpH0QCqxKTOMGq9FKhkWZatFKqHoJkLUyCi734FUMqpMFjVBi1NiGmMQNTpqjE6EEoqJ0hOhJE5pf9ec'
        b'4fcwIu5F0Rvi0+679oMn6XH338AmmcaD3D2U4rvShYFBnnclCzwWpB6go7yWfhwWPT5IyDQepenxu5BF1C9N+/3oIZrsWFCoO0UPST3Fg3cozkfqaQZRFOTpHxjiyVBD'
        b'xvZB7AhetCgoOqV3KLpb6lla4cd51F0LraEpyP3B+lLV4m30LrPSqFcatB9S7/QE7dA0TuprtEav0lv68nBPbaXP/GehNh6TVduAA2HDPjw0ksICclDA7UStdxgRzW8d'
        b'gOowRUYKVAynOByFRB+MwhvxK/NdpSoqyDrZ11FKda+I52Mc3vONMI75WPgme8i0V4S4xOmbpJdxsFLEpMLRq6BBbaWSQi5cGiLCHJtIPUShVzSeIlTN0isf0C87uldu'
        b'H9xnmj0mYIelobqR9W5n9OvrhwB36M+4jXbv8xSVY6zwX0TliFFK3x0le1xUjihWcgo7QL3//y8hOTSz5BGQHJpZ9sgnpj02JEfviasPkkPf/H8IRobOuaz7+d8BidE3'
        b'zouHJEQk0mgCGq6lJ/hI+5ouBNZ+MBq9+lkNnUH3EA6HQfYRB/1xQo/CrNCU5PegVsTH/A+w4v8dwArNjNOB10D/PQ5sRO9J+5iwETon8P9AI/4AaAT91z90xyAghMMV'
        b'NMIhyNMJV+A62RX3Ypmfmta322UZbmGBAk/HjYl3yPvAQEUDF25vG+UY8XH4x/fiYlY/8frtO7ffuP3a7bdu//X2O7c7K+uqRuW15IypH7e/IUdZcu31Y7nj8hpqW4rc'
        b'80YdzJooEbK6TCdnnFIacGtJ2QwoZJACYkG2Bjqpmy1ehS5mSUqBG1jbB1EgAIo5osCceGaRWUye6eoRtU9qlaPxKS5Zycys8YaTmF1lMdSzYHloggJmPLPaiSd6cOi5'
        b'jsLraifpBe4a79B/x0tWG0dv/yjZZ7Emnl6mSxD5/cHygx9LHPr0IUHzekvxWBHzMUpRQOpVkUZM0xEtv8BQ7dzUPydtqPxoPRtev/B42cP9dyMN+0wOhWaC0OiZAsM+'
        b'IpuCCm0xCrXIZshENjkR2QyZyCZnYprhbnlwj+seQe+7dIlsDw9676lV/j8R8d4bHEwtB6nDwDeTnYPG4/4vCP5/QfB2/wuC/18Q/KOD4J30SksJZCfoSZn2u2LiH7Jk'
        b'/Ddj4v+jkdwSneKgZQDzAjZJgJMMIyzBVx3HPcmJQ4RR4zceXAw3ufdEsBcWBWoQvrx8sIyRla2g8FpyPAFtzMUe9kKJEfUCwVoWnm0HDbC/R3h2G3T1BBIzGsLcrkfg'
        b'QbhIw8IHJqmjwqVwLZ2aeQbBEWjkZ9wWRMjTD/Mlpkavo0Z43QG70qm8gRcS8UZ33CkWejnxQA8spBSvpPjVzIUobIJ8foQze2UQnnfw9YU8rTTMZWEaSuuE5f6UlksQ'
        b'ghSG5N0DWJhOqRuhfuNALFFzxoYuXeG8fAWND+lYqvTx94OGEC9o8vJ3cfb2J6m4iuGywgNKgoKFEXDELCFZxCsfiCWUp2MFXhRESQJ0QC2UpdMzd2s4OkybOPl7Pc+A'
        b'hrYme6TSeFYWXS4VwqHEEGoWT0inUUSrsXZ1sOY5dW+F8OcDfbTstmtiDOE0tEAxD/yoiDJUpJqRVpRAJdYPEM2eEMr4R+Ag1EAT6c6OLSqJIIbqULwlcgyFU8zv/lKA'
        b'VPhlLklgXniCct5YImQfeVNQvURH2GIMrZhtBm4meV+c+mRuWuT7Vkdy8hRuKxcYW57/K1S7pLk7Toj76rb3jDGLX8wc4zDK5uen/r4j0Pisrft351e5F/656eM1r0+z'
        b'XxB08tPMfx1bEjdl86LOpx2D3n9XnPhclYHHki/aF7w3b+WaV44/HeN6YOzaWXdf/8nt9MSWlqu7Dgfdj17oOXX8jS3bYt97ZoXbBOPsiZ1K+x8q13pfe3/Ee467b74y'
        b'4+uYQ9dS9339zaXYd+uvnAu78rnV4fv+r75wxXfxizsmhzR+cGvI00ea/7nRL6Ny+JyCN3y2LI5WcmcivBa/kgWJTrHu4RQkhiZ2Lr0wGc9DycTJ/WJEC8VpNIIADmdY'
        b'0hBRaDNlEaJKa+4k0Yh5eBVLQrGgTyCnL97gB97N3o4aHcUyukcc54gEnsI5PBZCFLp6yO9NXwx10MbUn62R2MD0n4FbOFbYJTzGXX6yBuFV38Vwvk946vqtjJIuDZox'
        b'v4f3LXe9xet4Tu1+uyyKlUC8DU/zOFRfvGpH/X/8RIIZdkn8sGwU93NpcFqvYVCe4jtHBBemTmDanz8Zh0d9PXzEeBAPk+l/ScAOKMBr7Nx79SLcpzEzx4zkrpC10Mxd'
        b'Fy5ZGzj6+LP14BIeZ2UfOEGCh7EJC5iReuRSKVUryTQ+rAnf9IeTzP9j6w7I0Ru+OWK5jHJS1/cntVP8H4ZN+j1KIUxmwZMSOWP6lctk9AhZZKVmCqaH1fTLTGwmlrNA'
        b'yO0j+ypRuqMdjR4n2rE70NFAvxuAoX6SXR1BjZ6PpY/esNOvjz6qgv+FuMZ1j4xr1KXI/aGgRnrC0T+ocUwAg42AJsjGSn1BjWSPrX54WKMJtjMe0pETsKM7pBGahQ0L'
        b'oQBuzpYohNHYKMFcrF/PtqkVklge2BiIp9WYmDk8aEo1PYzHLMKtKaIRAlTCfuxk+8OfEyWUMcxik3m409WAmTwwcSYecaRxiUPC3ASBxyWSTb6IhzFV41k4Sv3tDi9j'
        b'/FnJu9JZbKf5WFUKdfosF1znQtHqOSzjZCyFi45KBzg7m7Kv06hE53k8+LGSbFztLCwxANs387jEOdPZCdgoU7zcHZS4D3OgAq46sOizyFl4msYlzobDPjQIkoYlQj00'
        b'sT0ymTRcBxFlxicROYfFEWZxQIixNNSSRwqq4wSt4DQPFRwGZawh5kZVCLYiwS1zUrjZxoiJPE5O5DBGWEREpLGi8AUyn538j4MXeFGyWAvLxPCNIQNE/16oYMzjxZh1'
        b'asww6UvIhx8lRVKzoTiR5TXF2x+LnbBK7X+Ee6GVwqJQ5A0ltEs8EigSZokvpSlTKUiTLcRC85CtU1htTFQmAmnYlclB4U6Nw9bzKsZKBwlOpN63xobP+jR8KG/EaOyc'
        b'hdkBfSMEWXRgzFzWcWFkxJ+m4X8WVqYSgYb/EdnkNEvyp2QGy5o8eVS4X/HccYJSxCPcDscs4M69kL9erBDZzYXi/0aDSuSaBqXDdLsdddHA9jgoNBdToJppeM2WA/Be'
        b'w1IDTdDeEC+oxSzIYne8xjuqo/YGGtO4PWwMwnPpNMkJizcqBMgjhaUhe42xPJL1IFRhqzZmT+4jNrBbjUVbWcheMuTDQR6y5wdVgzUhe5CLh+IDv5BKVAdIAU6cGpwe'
        b'4quy9rT68stPan8+lPu11zOmFvPmWVmMEc//5+0x9sf+ZDhn69jRry+2vfdi9IKWT99IXrbkQuOh04riQz+N2e/459OK5/IcX3P5RbTf86e6V3Y1LXruqWuqm9/WqboC'
        b'j17qeslzUuVzkR15VZJtK2yWjXaMDnFWvfurcPOKx+znp7kNXVnrZm4cv/TwZwuyXpb8VNbs0bXsaudLkzbGw8V5i+Nw1qf+VieKw8tW37EdM6WiOC6gevs//3I9Ylho'
        b'q822V2Tt0x2/Ea4avHX5bntmW9n5KZ/ObH59yt6q1TBssv9vF2+fj3zD9cyrD169sunzqTaffFV4afLwN49YzPlm/+5Boz/zS1hjlXVrRLtoSuLXSbbH15X/49aU7bOK'
        b'ajovdlZ/Eu8W/Iv1q+OPTvesbZPdLX3L+dUrQ/7VtibizcqW2dtO7P/l7WXnqz22rL7f8bPtm0/Vn6tPe0be+qHvq6eHB79YYfv2C+QvqfLpkY6puyXfTpq444nGdJMN'
        b'O94+VJ339oWQXc77T62Kfe3vmzxak8xeacDVo34Y8vru11uff36p4VutPsr7ticMLU4+/1GEYZNTaLvwlcXnzRfchz1/dU2X7P8j7j0Aqjq2tuG99ymUQ2+iIoJY6KBY'
        b'sWFB6YgoKoKANFH6AewFRDpIESmCgCKIqDSlq8mamMTEmJ4YUk2M6T03RWP8pxyaJTe5937vH6Iyu8zMnrJmtWetdx8cP9nx/D2DvjUVzne0x/zUf3qT4ccfmL+Se0HJ'
        b'4enPvvD6/vQ7z39Y9se3m4wjEt63un5Jdf6dO+usgsYvC4l590D7Gx8f7Pfd8q5rgWZ9Rf/5F0x80w3WGH9mdsnH7Mdy++aEZzo3hE4LnhYiD/b6wbLl6d2X1O4q7dyv'
        b'el/pC6E59bKXa7N+6pnbM8/cmBz5+68Hvti38rNfpV973tyYdWNa3LTvvn9w5atXd1v9LC84EvDJn6m7J371x4GbSvUWsMD0TIXNwU9rdvo5Vkvvmb783HTH3IRfnv5x'
        b'4tG7+zx049Wm1t7znZlq+meNyp7bbx+bpv7TdqW3fr+2bX1jTXz0mJ31IZl+Uesbf53be2zBa63LmmeefV2pPiTiz1MhXQ1vt3pNbM9odEHXz77x/e91GRUVCQtb9/Ol'
        b'b9y/ur+356Me9/Dy16obxxbo/rLXbqBbrcO4/3BIWcgbH+rvs5qdEJPXleBwY7rHZ9qXtnb+du+HpvwNpmbB5/nx7gNrwm9eEf1ckez2zRurl1Z3Gb9/V/W7gWKVp/dq'
        b'9Env73l6vktO8Ec3DnzQ+tSV9T/vivou6MHL92Yc7DhW3yHqTVh5xGfXW9Uqt94cGxjSkDD+xNmYzqM+i2e/m/FTZufJ6GmRH4o7Ine8bX78hvon35/+6sCu8eaXd5en'
        b'6Uk2/cLv6gh5s/nqvFf9746fOOaLl62etohLIqf0eDiFTirYcCxWDnPiCi4cn5kHqYCiDyXbRodzgcrkFFQ/m7mMnw3d/wgADkr2bMJkgblbZ6stpBg4xX091E0xcKFQ'
        b'Sg0ty6DG/FHcGkpF2eqQOo2JSIVxKJdB1/ChEaOArskGM85VoVPT5CPSbOGjP1WBXiuZnUTyVE/HnEUVha/ZJFq42SZAuZMrwbYMAtjmQ7oUH0HHUR2VEGbDIR1F+Bcs'
        b'q6QxBFuAnPZlJ9SvoBg1zCgcsVRA1PBBVct6mrtJMoRRIwA1uAiZO1HDWDZWvVBoOAKlRiBqcAE1e0+CHPYpfaglZugBAvBQ1lEA1fwgl/rz2iSQoHO2blDmQ8UeHprG'
        b'ODOx6zwm2BnDUDVlVQEqdq6Ds7MY0urUDKgaCVXDbFGBlxJHwWqDPsHhqNvPnSULP7dVAVbbhVJp78cbESUMwapBvdFIqBpqkyiAQVhOOkKhavPg+Eikmrsy7aETt4Di'
        b'1BQgtWBUzXBqE5cy5GAqhzqHQWbKGgKkQvdGI9TOoCnHlOHEIMZsOw+njbewDytJWjgSZaaB2gnQjMLMoEAxpS5w1pgIfZGoZiiRZITio+M1oF3mZaNmMQW68TfDSR6d'
        b'R2cmsY8mWHcKQRkEoMz0ZBCUI4nUluiKDhiNgd7REDYFfg0VjqWrYik6KqfwNQpeQw3+DL92LonWYM5BGoWvLVtBgyhkW1AMG2csFkObgW8SO28PoAIKVKMgNdSjpcCp'
        b'9WorAF+oBE4QQJcCpIal9HMMqIYOLmSwhhp8op+We1mocxZEJ0NgDXF4dCjTcCjIeQilFrsG+tEBlEG7HrcPjlON1zaTEZJ8LMqidTo6raMYNWheSbhlglHDq7CCKRAa'
        b'8SI6y7YRHJaMAKnV4rfJRwVAF1ygIDUHODESo3YgiIGzqubOHsSoqUwXDLdAuSc0s6VyGWVB4TBCTTlKwPxIf5RqIK157FrUTxFqDJ62BloYQg1dmcPSdKbBgZ0EouY1'
        b'BY4NYdTKg9jLeAQrGUYN5e6EtkGQGnTG08GauFGNQNRQ+U6iJ6MINY85bPf3e6FzBKJ2aDf5WIZRwxSkifX5DLTBRQpTOww5wzi1hACGMKjlUDcBXFBkicF6hi3JhAsM'
        b'FtE4D9PoQZTaNjM8zGVS9l4adEkIUg0a8LxdIBq1y/x4lL2dzlDsQmOmaoXLw+Hgxwl0Q+2AS6iE8bJx2wkrO282o9in8WpLHw55L46dSHVSqHMPnRfngPWkn0snjwDP'
        b'HI2kup1deBaqH49S0whAZZjwNNPnUCnqQ5WQA7mPoNUoVA31mNHurxe8FEg1D3TOSQFV2zCNdmMZZKNOhlXzg3MkHBiqhRNUMTRhVTzDqnU4z2RQtWRnttDbgnUZTg2d'
        b'saBQtcOcJ9se1ahfl+LU5I7meH9QlJrSVHovjl84hFEjCLVtqGoeKl9Hd6+ch5zV+JsJUgZvE6IJvog/whC1iq2gayObooOB0DqSkx4LR/zxDDawPmWhwlAG0NgcThVp'
        b'degUJT4envYyWqcHVOFqyUJXhWIBzqLLUrZD6lyhWEZBNqgiQExE0klBLrTN6ds3E/AQXh1Nw7g4EsOS0swNIlQgJychOuDgaqkyCI3jJswXEwCOLa1iC/TAAXaeeCTB'
        b'mUFcnGMiU5V1u6FzbJb3Q9EoXFz9LqaeO+aqooDF6foKfrzNZnSZti6dHvY4QJwe6oQaOIhYnDQgSajdbdzw4U4OOgKJ8xPT9Wln4sfaZQg2OGDAQGz7oZUOWyj07h6B'
        b'YSMINm2ox4JdA/TRQGuLjSFdgWHLmQn1j4Ow4U9jwHrUgPLW0qHC44SqA6EJS9IoTZS0A7rpUob0JfhcvLyWrFN3CxWUY+GqON7HQqqYBOW8wI7nZg+4zB6iX6yEqgTr'
        b'rUt2onQ2nIWGZhS0plCZYgpXz2BrBaiGVrAH1U9kqnsXaBnWx6Ij+xkg67gayifaUPsZZLyINhROTaXfMBY1bZbjVr3xajpshTJ1ManV2inaA5VQyLxlyqB2qRVegpgN'
        b'IyGJUIWwZMnuuEAGVutdiQ7ISazRbMIsthHGBw5h/kZbX7TXF/VQLN9KdJKF4GNS/CNAPv/okVC+Csy60Syp6ZgMpA7j4HygDneNweD80Xn62Qvw/uijuNi66BG42LNQ'
        b'xYICrnHCN2PREXqoEfQ1KtxIB2T+2hDyGiWnY+EShf3u1qMLALNQdZijfAiqR+FvpJMMq9cSSVdbnOfEYbjhGsijHSRwQ0ko/Ya1qNiewfQ81xOg3kiUnjfm60hXTNCx'
        b'7TJzm92oEXOjDKO3Fg4xYpuPN2X2CJCeMif4Q5OPGT5GydTYwUFoxgedD7rkxnMKlN4pKKGLxgJOOD2K0YOueJRlEk73oC8qMVUg9PbjXX4I0+de2q4EnYO+IZCe8WJy'
        b'YFGMnqmI0rzVMaiYQPTQ8Rm2hBxSjF7l5iSiOjNbDxkUopdkJljwxlMMGF6xbjs+87vUHgbpMYTeCkzTKLVrR0VbCELPzUTMEHpTUD6zSNRDo+kwQo/A81BnHBydiwro'
        b'QkhBGShnCKFH4HlyqCBqxrOUWu1JimD4PA+88C8qEHqoAhXTWQqEdNT8GIDePijSMcYUhzHQk6GFgPRQxrQRGL09qIUx54dQu4kCo8cQekaYX6QgPQM4wgh9jismnxSj'
        b'F43X2GB+laNq9LxFtV6QSkF6cGWssJNfoGPH4PyFPDo9BMWjOLxSdBDzvgVw3ELj/x5+R3FR1Jyw6q+wd+xn7CACT0v0ZOyd8hD2Tof+iHkNXguXTf4QpFr8P8TaKSkr'
        b'sG9iim9TfoCff0B/bkpnP4K++1MQM6SdHn1Dgxg7KGLPkDfgxbhWW16DvC/9L1F3b6gtGI26M3wS6s7gYYvDfwu5yyJGEAJj+0sjyAHu7l8A757QKdwTAlBIHBhE3YkI'
        b'6u45XqGetND9v0PLXcON3iLgwmjuf4SWuym1EngNyQhk3LQRyDjFNcMlyfSUL1cPkqVANzrzkBKb58zhiiQGdQc+4i6rofhXnvYIIs5ffETpiMoR3QiB/H1EQ/G7nuJf'
        b'VfZvlChCFCbKF8Ish+xMJJ2OWqZ6pkamFs2VrUaQdRSJJgmXhknDlNI5kiM8X/BXwmVVWpbRsjIuq9GyOi2r4LIGLWvSsioua9GyNi3LcFmHlnVpWQ2X9WhZn5bVcdmA'
        b'lsfQsgYuG9LyWFrWxOVxtDyelrVw2YiWJ9CyNi4b0/JEWtbBZRNaNqVlXVyeRMtmtKyXKYngFfg6ffo7yTmu7G9APSxF1AannCnDY6OJx0abjo15mAV+YkyYQPXsVgNq'
        b'y5Z4rlmuMKDd6hQe8qgkLk0jn2BQvCGHnKQ4kkdCzp6ZNcOa/etAsy6Q32aOqmzQTie3NVkywldQ4fpGIQQKBzt8Nyk8kSaFiEshiW+TRvv6jUwQYW0SHhK6xSQxPD4x'
        b'XB4eO6KKEc6IxJt1VA1P8vYZbS0cVfCKI05erhEmNOOr3GR7eGK4iTx5c0wUdVuKih2BzKB+VPh2CP6TtCUxfHTjMeFJW+LCqLM67nNcdEo4tWsmE/oSvZP4Y43KgGHi'
        b'HEVdm8yXWCh8dKNHO3wRvyiFyyCbCDvFPAyOuLWJ+VKLwcdCTOThxHUtKfyvJonMofkyCwLnCBnhHqhwzItLjIqMig2JJrgCBSoZDwHBTDz0oXJ5SCRFlISzTB/4Kfb1'
        b'JmHh8Zigyk3iWMepj5+54t5SssJi4uSjXb1C42JiiC8yXXsP+RN6WQgDoh0x0QPS0JCYpFkzQ0UjyI5EQXqoAYrkSlDgxZQyB/NxySgJ4TERESI0FEZrUZb0ILdXvEtn'
        b'j4garcXUUC3aJ/Yd8bvCaJ1uIb51l/8bCLJRm+nJnmVPcjbEX8j8DNd7eigc5WjqFVrv8NzhWaLOpHhrPt4D1TycLakn7du/QDbR4XUkAJXQELzzg3GXgpnDH6tsqJKR'
        b'y+8JCXFCwsKimHuoot1Ry48s1ITkcMUWlifjvTVEQh6P6BjlRMvy3JAdGJKcFBcTkhQVShdsTHhi5IgsNk/AhiTinRkfFxtGRpjt67/OSjPqrFNXLLrRTgUTvORERNno'
        b'HN3x6q9WFmeSLK5Z5OV35lq81Z4q56L2Kp/S388MmpaU+d+4ETpQEeoiisIkLEBYQKkadEKuBToK7cBegVPxYZRPXUPDp67RQrXQLDFB5zluH7cPHTRjoXGXCsRFYNVi'
        b'cbDaB46zOfosOona1aFDiNiGJUNuPmpLiv7twYMHPziKSVYawwMuwdYDolCOmj432xnTYMxLsFjpYC9wknn8KizzYtEvmfj5wPEtDnKUo4GytzOTApxFB7GUqWJpznMz'
        b'0BGp1XIoYb4HuUvsZeSq4Am9ofwc1LID10GsL3A4gei+hitRJX/x3CSUig45SiZhCaCCWqiNFiyQ2UKfEb0rQr08NK2FS7gWa3zTGU6hy6O64mqJxWjUZuXqbksMG36o'
        b'3A7KlY0WoCJamzjODHUM3lSeBcWzhVhTEwsRjaG8xw5a3b2wcH4Z5dmgIgf7WQKntlfYZulGoxfjG5Xu7l7oCmQO3pdyavuEaJQGNdSzz8AQOt295pkM3uY5tf1CjBeq'
        b'o1MswDFUQjKJwAGURxwIXbzwgz4uIyw33HJNpTHJVjQ4dhzKRAeZLOljgzqxJLkJikhkvwIR1DhDdzJBaKBUaF4/0mNFkfIGV+rh7m4jJCyEaiN0CXL0sdzZ7q4HOe4y'
        b'VXQ5GcvcuW6rfbnwCK05sWzVHEigK8HcB6+ERu2lXLI/vmi6BzU/pnrivmnnttYcZWP505c4TbqvRa1DK5e6yXi7SnSmqGKJ+5QEesZJUI/zFGiy4Jy366Fq1BKEx5yI'
        b'wyqQAbWoQ3Ouc3wiXiaom58atZOuHT90wl+mDN1BiSl44sW8Zcws+oYu9JGAWmq2qxLoG2f5ySv06Z3xcBDq5PFLF1KVrkiND/ZWTAykolLIkSdAFh7IdjXy2gF+Mjq8'
        b'Aq8jqg+/jDLM5KgTTgXTSqGfN0DpUEmr1ZgcjZvTix5qDo5DBV0wSlA7Hy+YdH70hENNGHX0hTPoKGoYmT/G0waq0Ak377V06ukriiHFa6KDQzXRMjiNMuBsshV+f9Ne'
        b'q9Ev4xdX2fixFzhUzIWh7hA4r8zpaURZLugX5GmYocs8IsSUzJfrTtd6bkr1nss/Vdtll8xNUL7luSMjPbMkuGTV7fGvZLh2hEorrv3mrLpi61zV8IxrAc7Ot74au4hb'
        b'5rzE2fXqqtWrw8vfOHs7N9T40KfvX/mz716J9bZ1Yy7qdtyosv1ZZVVwb7njvavvP39H4/sl530yA67rFS1Xmr9G5+m7Gt0Wh/YcCr4dcnvddeO3Uz+6H7DLqM/peMkN'
        b'WfOdusLXXvm6W8tJ2TnrA8cct4FfV7c7G8fFOFw9YjbhjzuWb/80pcjoC43o5CXtR1IWu0Q4TvzOYrMZurP6tT8/WPS5xN7g9bKM6Wt2Voxx1g65Wp6k3mzY9c7yo6XL'
        b'j7ziZ/Hi1G8+OPJL21b/5dOvns37IS85Ri3A3lYenhb7SfVLllY3t9/oDV4+r9Tz2MStjVfT5obubXnwyg3/D3vqUjYFtL5wtS7x2p0y08NfnUj6ofO4hfeuiIIfT9V4'
        b'Psjwmb32+pzq9JR9v5x/Kv2SpnfA1TOSta/s3KD19mbVU1NXPmfqODXfrO6bZRPiJxm8mvpt+XmdFSkGPg/MA6t2T4iLeEq+7D29op3ap203vNn15bm63qp56+LvHFcN'
        b'M4nNnf+x7bemvt7fFKUnj6usTfFeHnHoC9W2tWuv+73qGzvj5/6umWu/f1t9pf7LF460fruuakzWrLaCaRHn7GZvml9Xd/PSfdFidXu7cwN9LZfy4qY0TL+fGfnsj0b3'
        b'yxpnwydJs629bT5pMn058eOkkPTnomIeXO3IW+DVl7lg5dHGX944m/yS7gfTHxxWui9cb9Dru/JFjNPVPzQG3gwInbX1u5nfxTWE1Xx39NyXX7Q+fd3r15I73p8vetvo'
        b'Zd91dQ0z8ppUw3e81nZPNv9GxdgVMa0z2r4zWX6q4AXUa3pP7bb2D0H3pa7faG/dZG6xhGp7Ji7nrGw9BbyZTi+BDt59C6QxdeolqBdBLrQQIoKKoB6TF5QjcDLox7sr'
        b'ZDwzSaImdMjK1UMJv56F90wBvxBloHRmRypBV1COwhzObOHQGmQzDQ7RV2327odcO+bfKg0W7NGFSXgPZVFlYgyUQQHJcWTnTZxX9wkkM5flvklJRKEAddANtfhdYsD1'
        b'sIVsb2YIzrJzsbakoE4lLmhv+BZlOAeNMawrB0yN3DEpdB6y7lPTPnRo0K5sA2ILwpXk20g56SYBHx1pZpJ99NUl0yLcvW1c8c7vsCbxz2RwgfgAX4BjTC1avWLqSLeC'
        b'VbNYZN0w1ER1ZmYob+NIiCWq8FP4L8+yoZ+6MAb6RyoLUbGX4IJ6lGjH5HBaT6EspIpCixhUijLHMF14LrROtXJFRQKcwye3OJLHBOkiHGU6TsyikHTU6LDnPqgYqUwc'
        b'h6rECSEzmVmmHB3AhLbDY+WmwaiSkONLfYStIAd/Y66dmycxbeRj6slen4xP8tOoVDIfdaE6ZldogDxDOcp3JdPhruFlgy64C5zxCmiDOjGcgnSUyeysx1GbG+pwhbTd'
        b'6LCK4jF1ZwH1QIYu7bQVYaZy7bxsrD1HtGgyfTZqE6NTHqiAaSFrMbdVQtWf+dA2Qv+Jmucz/Wy3DmqEXG+8hgicwdrVk+c0tojmos5EOnAbpm2TexiMIwe2QvGrPkuk'
        b'tNuOaUYv6hpS80CeO8pV4qQqAjphrxaqiH+IWbwuyJN74Fm4TMLqibbxe7TRWTYfDXCUpMRLmjg9cci8CUe86IsbdqA61GFnhPpofElmtbP2U4R08yXHPP5YGqdTgip5'
        b'1KRDwsAtZAaTWpQuwrzVYVN3quE+w0PNLh869nOhb93DVkySHkMRbhOdVfTbeTo+cAfDXkLbduLBit+i9/YYQK/CCElNkOjokk1wdg8zKpXAJXza4rHMw+uEWDBF6BgJ'
        b'M3gSXaS7IwbO+BNjZDomE4etSO86eMCDD2VsgeWghnhino6FSkVkWfwEU2J3rMeLI3cwdKIE9QqQA528nhpV3etIbQZDkwbb8SYGe6hqezuUoCrcHWby3WNMYQg6cF6E'
        b'cjfBBdrloOkokwZzVBjVoBL1ugiQDaWQytZrOfQvesStnzgTQa+5GLXgRczmunCWB+ZBodDTghnJL/JwftVUOmUaM/BG7bDaAvWDrJSU0wgTOaOqJUk2+P5U8zGQuz0F'
        b'XVBPGGbKCHrbDhW4eNrgp32dUQ6cUdbwgYPM0t8Dpx3lVqqYQbbgOaW9qNlYmGkHRxQBehO15FaJbK0rhS+WCzPwbjrKIncexoNcjb+Y4GTyvWm2P3Rwo4TTR2fE2tCN'
        b'KSpZ17qW22WkblYF5ng6oE1YuBhTMbrqDyVH4SrE1rQSO5StxGl4iZxWx1DbjDsULJK7kTjXPLEYrOK1lsxigT1zolCrzGKZWBFZEY5BNZ0EbZQ7f9BmMweVWQwZbVC3'
        b'H1vT3ahVQ+4VBDmDoZix3FLM1kwhJkstg2FBodWYN9sPbZQoLeQ34l7inrji7Unpg50LyhdhIluNjqEGyRy8TM8wItGOSRkJjplA/KeIn1ieO89pTRD5bFpAh3QRPpVy'
        b'5BZQBZWDsZYx+WykPZgFrfr4ViUqoqMlgkP8Lm4vG6i69TRNSLOSjbuNpRemLJqRohDImUOjjmJaV08ttuNQxnAvCSQmm1i2LTZJ8Ah1QlYS4RqhDZUtGL1KUGv04ELx'
        b'no2Z1PlwXurlpphBqMaDlGMFTY7O1kOuQXg+8uiK1JmuJSNnKV7OQZvogtZGvSI4p4+K2HarROeDrehBhM84ZdQXAHUCFG1Axylx3o0y1EdZnfY7KwJDmkCthfp/b9b5'
        b'H5mHHhdcgORM/TfGn/1cuCqvJRDkiJQ34tWIwUWguvX7UokWNfmQ1FnELCIVlOlvGvg5Dd6Yn8qb8zqCFknLhX+M6LNa1Gwi5Q14A1ynDv5XA/8o46dVBalg8PAVnvxo'
        b'UPMTeVeqQLHo8bv0RyqeHopzYCFhGJJbxIjx8Whcitp/NRciVt1w7UPj6YoFS/kCMp5/baE5wPVMfbKN5vFf9bfiJkT+27gJ5wb9yx9qZihowvRB7ThVL1ubhEfamlgS'
        b'/Zit/SyHwfAuj8ZQ+PthHeL/qnutg927O570Q6FqNYkKG9Xi3x6LJn5AOSiU6eCf2GbHUJumFOxMEb4RJvQ1Atn/xy2n45Yt+AH1oCENc1DUk5vvHGp+6hKT5NiohOTw'
        b'xyD7/5Ovx31QCxrUNv5VF3qGumBJRkCehIeA6iuHVJX/aTfIUCSO/asZ7x9q29Y3jgQVio2Io9ERTEI2xyUnjYpR9B+2T0BPT2z/yugVNyJmzn/WmMtfNQZDjY0bbmyp'
        b'67J/3hbdSu5/1dbVwbYSPbm/uT8p+cj7q0qfH/oA8zWPiXQ0GLHjP/ocvFxVadCBIBIC4IldeHH0hNG4AWzT/uNWt7BWlVmrSXFPbPPGUJtjFTEm/sMWIwdJw+aQaGIk'
        b'CYqLD499YrOvDjU7lzRLnmWa++iRJsCHg5L8xwRLY6hXodFx8vAnduuN0d0iD/9X3fpfRbqMeFykS5572GIh8op66+djYjlRel6dt4HErFSOkJl/dJ3jlHP4rgcfWPCK'
        b'tD2oBkgQfEvNEeIQloXC3J4QrHLaoEMNUf3/W55qPxe5S++hsz46PDYo6MmhKkkDbxMmgwQQ+LdMxgGu+S8CVj626f8/50XstSaq8M2lEjm5vML+hHuIWsRHHkqccYrY'
        b'nLeoShheio+OfBvHRj4xnX+EtQkK2hwXF/1Xw0reHvgHw3r6L4b18W2PGlfSd9IDssiY5XY41udgOClmveUz1Ycst0KWBI+4CI+4QEdcREdZ2CfyHfG7YsTTHx5xYhoj'
        b'aR4dRo34RC9mFihErdAtT4BDq4etBlOhiVrOmqZKqL1Ed1mw2nsrdnDUaKG7M1GuARfDElXI0yd4253bqXElypsaV+w/XRmsFmqynaOxMdZB/WaqYHGn4H4SFCPPHf/i'
        b'ZY2y+eV2q1ettvETuE1OSlCHarcy09sZKFrl7kaMAlAwqESDWpTjjuVAy1AJNDugagrX1VgGXfJ4LKP2DVlDoASdonaLCDuUNsJB2M2eJbmYhK6wBIc10UFEjbPEn+qq'
        b'xDY8nEPtCSzW7QmUoWJlsUVqOQgPRs1QQ0drOaqQW7nNCaESLJHqsQgbPgYOraGVuq1DNVROtHHFQ4FqVZQEKDBNYqEyqvdDjrvrBmfi1CsW81CjvIq2tj4BeokW1ALL'
        b'lnOgUGWeAKfckqlVZv/4uSjXFkvFGW6DOKA55gyofBxa0HGUa7Na14tq+qSBgr7xMmp2nDKNxmxwJVH6PFAuHWonPC40SoHVQgnK1138yJKUDS5Jj+ElOXpB8kNRzf7J'
        b'YnwkADH5ZJVHFqOtF11v/XPIEuoer+4UHB3uKzAcrD80bZR7WVhBzRCmRZ5Chy4cXYIWuaslNK8c8gzeEcrSsOaiDEizcrNBZ1DLyMmCXtTMZvmiMxyQe3ipwxWFNhLP'
        b'exa7dQXOL5MTP2QBFUOmMj8B13KeLn6Zb6AidY4xSt/E20VACV0Y4j1wlIAw1kL+MAbDGuXSmwmoRJNhaJrgwiCIRh3qKMw2GTW7K4BoWqh+GEFThC5RM3gyQQZ7QPEm'
        b'fHC7xXGmnKmKjYWEvoqKjKBO8a4p9A69q4H66CrxRIdRA8GxrB0/BGNB/T5sgGrRJX2Cn0EFs21HZnhCHdDH8uZ2oEqLIWyO4QKSPQqdgQ6Ku46HrEVWuFlbC0tPWwsb'
        b'N0+emwR9UA6HJPMsk+gOhHzoW0egMG7+6NwQEgYP6AU6yJFQskiELij8rvEKVhbG7B9DHfFW71z+uBQrxGcbut0lEV7QSpPDrtkJfdTB34MqnUnoHcih22HquiVrJdtS'
        b'liZTxrsSfxGxiAx5rS+Bkkdr94JUJUwNz+qylMyn7CfJ470WQMMgadFHTXTUZ6LmkJHQA7splLKgHMij9CsSXYSqh+kXpnmhg+QLj1IqnZ/NY6GbECH3SWHDROjkXkag'
        b'jqMyNfzqOsgchEagPpTBAhjARX2CAkCdcwdhAG6a7K3G0Mm4gG8OkwWoMqb3HPDktRJYoSacHSQnKG8BnQyUgeqgH+UuRvX4LX4uhwrMUD4jXO3ToM7K00aTgLfEIZga'
        b'JhmytoriUA9eXS421gQzuno/HBX27FhIDft7IN15OK/NkLt8szPxmJfCYVqB8rgg9gzu8iB6xRaTdkLEdiahYw8TMZS3fvUQDQtFJywEavhGWdA9BXJRe4qY41G3HJ0m'
        b'ueBO4HOAumdUBM2Rb5yI2qTEWsBBYYIWu96ADo9FJVKSsO0EZ81Zbwukp5iHt4zT426KRVrB1qabFrDQA5vCqLeJnogLtt5mnsgu7pARYhWsrekUrPaJsgG7qOSgzhly'
        b'Wb78qmC1FzaPYRdXR6lwWtxcbUlwsNp3uvMfDc5A+Ubyh+y7PVygxl5+Dx+vFsb5YWqaIIQNCX2UAVIkbeZTHuLPB1QWRIbHhu+IT1wUrqLg0pM3km/tRUehQ/6QTh0V'
        b'sfCo1q42kIN/KRsVoAGViDAlKJ4OJTruUOygtXk2aoKmndCkL3FO4aDcRx8f681TaKb0vXjptBITPt6GJTa2rjSWkJvPKhs/ElwkDR19aBrRYegQVHmCxzqjFhwJl+ma'
        b'WYHr6MIU20KcZIM307AhyWitGM5GbIn6vegbQX4df67VWVm4b0/su05a1YHFxeZfXo5+IXHPtS75vMi6SYdyf+bTZq6oPJR/llvWwI95OvbTp4KLxH9wYyYXxin/qL5i'
        b'kX+Mydov1zT9yFdUn9Kfb7v88q93Xrr+rZp+2a8mCb/u35b1vt6MV6xtVWbfeXVV/EuHTlaf1Fk0b8bK1LCBtR7dplX9Ts+e/PWFtQE7HLTSkuqtLmV31+l9/1mU984E'
        b'H4Pnnv3O/MaSd7dOSTJ4/osXZ9xpeBCV+nPrxgRxV2/AB9+m3ShOPuFXtDbp/gsbSk/8OdP/dcnawuTVL5rNFQcu/+Dmwft1tk3FP+vMHptlEhNR2Hq6ISfqxdNjQ58/'
        b'vG16eb+WfWP+LNV2s4U+rn1Zu47cWyHOilSWaRt9n/eOf4nLAcucL6e93hNxw+zLnNdtPn/mc5eWqF/ey/+iZ8K8+Ze2ObycEhv2oL/hna8N7jpltNt9Zv+n0g9Vv5TW'
        b'fL+lds/1p7dfV1t9eUtm/LOfrH7uvZZlO0WBfuHz4vaUBK7pq8tOtkjJfKPs+d31v6yyeVHypeOyHUXfW9+aklgzSfPahOJejy9X3t67+l79+VUfGN0yvcXfWgs/vbHX'
        b'87zvt1Nuqee8V/d8g4aG5zlJWOp7xe8mKl15OufMZK9n8o2Fbzs2z9482+14X/e9y+e9Ts7ta97xsVHZq/LDRhebTqagNt17sxOf/fGGyXcvqgeuS3ZsdKioveyyPcAo'
        b'9Wr2+MDgP/h9C90bjxYdX6T34tjX82/65jtM9Xv2pundhnFR7uKdV2Rvai1L+jZiaktmtP47J7+67jj30so7PY5p/R8PlG8Mumv44IeX9pR96+o96xvjxur8796z9/2q'
        b'pnh71/0bP33b59tpnKac99Pt59ub13+dq972O+/dkfnmFr+5+Sc3BbjUZNnMl80/eD0kIiOga437olNje0ta0hPe7s3/fOzl+WfyAy83a/g9qBs4Iw+e3Z8/56M2+VMf'
        b'3Kq/0vqyx3b909+++9mZe+MMjfqETan7fxsz5vc5iRmXLOZRu0ncdlRFTvIx8XBaTGlzP/QZM9xvBtQulKEcC2/U66pijplnzClqQ6MIqlCdObNQFDg6yEhWQYYuggK4'
        b'NF7ww4TxMq08FJ2UoY7d6MxQAkSUiRqo7UwXlToSYOlkXNmQ4bUHTjCzSSFqhGorVziHOaLsQUP5cnRekbEzBGoomhK1w7khy6wRS3WIjsEZQhQ83FZjajzEEiVtY8bR'
        b'I6gTGslHoYu7XRM87CyknDp+auo0VEIjF2xEJWoPWWcxg9U2lA0R9aMM+m1LUdtihXkWH+6ZFO6pr0S/TR8TtXOQvmCkhXaTL8pkdsFuyEPnZDQJlzAO6tfwi/DpeJ5Z'
        b'2KrRURvUsRLz2INJPbejTkVmOjgOlRTQnACpocOAZtSCDrBhIeCgSoIQblIfRgjrojLm83B0HiqVe5Cpyo5YiadLwqmqCVAbjlppt7aiLjg6zYImUrXmOCmcFRxQTTKz'
        b'cxYGzh8OPBC+nOTGxTxGP6u4f6clOoSKBkHNQ4jm6jEK7Gs01ITuoIDoQTS0G6SyxLoziTMbtX7We5C5Es/joU2GDtFmjfD0nx0Bw7adFyVEQclk9rWX8TFSKkc5rq6o'
        b'y13glMwdEwRLlGNFBzIaclyHMbFrULGb4L+FWQMnyfYTO2WCBcoIojZg1XUC9Jqjo3RBT4Iib3wGFcigKZ5aMyVQyaMWKN/NJqjLCkt+zMyJuZoKPd5sDPQxxLASdMnc'
        b'POH4VCspFgl6eTwfxyezjXQGdU7EHL8talNTsXW3VSVSlSFcFM/BzHAHyxpdC1mQqkC3McTsLjhCMXf5IlSCDptS/54t2ptGgVvxGZcxlPER1eyj47ba3nckFJSfhaqE'
        b'JT6QRj9/F6r20oWDIx1UUCkWcy/SnvpboBMElGuADgxFiVDEiJiI0hVpMZcvVyT03Y/yRyBz4yMYMDfPcqUsWX0FOqWCd6YpvwRyk9jGbMbMwPHxQFNyUkcSiTOPZUIZ'
        b'he5tj4DLMnOb7ZOGQIxQMI3eWQSntslR55ahBMAkDynz3jiHCuHoljCZIhMgQShjEtREm3PAG71iJPQRyndwgo+mH31VBhfgMF5bc1D5EPIRstApRdCH7Z4jkI+YLNUN'
        b'ZShEpyCDfuc6TKJKWC5BZwJUxBsilb4twUxNHZlJ84mPIhW1cNf1GZXKWLJSi2IVGVIRXWDJ/FZDNkojbrd4BXoRJG89ancXTFHTTrYXa7cpUehkJ+ocwk6Ox5uYfPNs'
        b'dAo1WgaNct+ygTQopbQvWh+aUa61FybkhOPBDBiPx6FZQOddjOnU6ivjaScP5Flw+iiLhnU8L6CT1ool7onK4QAR3TDjqDkD6vhVcAqdY+SpA2UssvK2xns5FzoF6s8l'
        b'Q5cF1DUP8+2UDqRjAaRUZokKaFxOa09+JnRCHu2ZEar0xiOGelDfaAcfQ2hkiarTUMPCIb+27HCoGuHWNlVqYfD/Gir2kDX2vw+rOKBKcDlB1B+ecuHvEZ7832tv93N6'
        b'DPYopkBI8rcGP5Vawa15S2K7phBBVV6H1yLaQvpDIINqf6qJBKnwk6qmOW/Amws6vAZvKFB7uCLFIftXTRhHrN0Csa3rEJs5ZpgNeS2BpDY0VNYQiI3cSDSO2sZxTwQT'
        b'XvWBmPwRVP+kf0SkVjWaGMCAwTcFLXxll8XDFmby/UG2C6g9Sr7Idng8mLQhHlBJ2hEWnhQSFS0fUApK2rE5RB4+wp7+H6Q5wBLMfWIW/GPIgH4P/ybCdcqdyPD/eyXs'
        b'Ae7Bk+M9JrviOjakoKP/RuLRSnqszMMEHryJKzStUc0sCxHVhkRjlqnM3Q16URsL6Evj5kyflUz2hZnSdkVEnawh76mJcHgcnBRD7uK9DA2Qj/LHkPahFFfF+sC8Lzlu'
        b'4nwx5oj6IhWu2gZwCE65u+2wHNESXEGlNDQyaliE6eDDrbk6ssYSoT2ZeFHhY6hQ2YqE9jhn7uJp6+rpE08GwwdVLnShKhNPTHWC9ZUnY16njSmE6rEUV0pcvY0fcvU+'
        b'DgXJUxnLdJoEl823wVzTmviUlE24xumzfFwUX+E4WcptDKVq3xQ4HDAyUwhr3BwT8jpIU3hFSrgAqFTWhAI1hr7sD8SHDZmf87aPGx44sJUFaC6euVme4oMuKWpU1LZW'
        b'EbKYfBzhjyL2K8MJq8go+wFTkbwer+SGm2+F+74Y+7qTXnXZhHfbdKfFvN5g0yJ8Gqj11flVV8epZEsmhTmobp4kmWZxNmLy8sLo2aXrzra7TH6mUn/zO7M+fCXOSfkH'
        b'vmqskkq2Z+LeGz2fHZ9vPCZ70sp6vYURWVNzTty59GGGwZ9pNtkhlZbn0+uXze6xe0dpxsBGU6Pni/ScXgv13qU/YOpwt+DEL6XP10fkVv5ctsbhi4nFsEvidjNow1fF'
        b'Y62ed+THGOkEmzou6i14JTldI7+hZsrOf131Kx+rPrbcsf9Lpy8tpQYvWx+dm7y56Ovra9WnqGUWbHT+BW3tTfFHFscs156or/huK9//xfdHt46vO+Qv//ryi97Pl/Qu'
        b'sNhR99atL6Na6ksyB6x0Lk4POz1xXuA2VxulmG2fvulzLEWjsHOZ47NdyWVHku563vv8mZaBxHH3PrzfOJDy5h3LxoX8Ok2/2HkvbbghL9q9s3zlzuKS/ulZtysD9k8s'
        b'rzx2OTRtktOdwM++71BOtj/psHXp7UXr2l3937hQ/mpxeJvGKUNV3fzOVMmX/b3BH+qV711Qt3RdvdnP179Jef7ldqVg24Gf1n+Tq5v4m29myzyjSL9nxhWIftHJ8f45'
        b'vXJX6bK375Wpbtohspwe+Panz1a16LVpJL334fiFLUdcnrX//d4P4Z8tb37D5b2KjjOiLz5+deGEI9F3m3/8I0i07ssA0Xtvee52T1BdZ7Du07eKj27e+t2dfdc6Og2m'
        b'vpr9frOebkZ0woNxP169/5VTXLDVc+qGhcfWqtdsjMta++4Z6H1mZtKy940Lr+yeWPRBdtTmk1O9qrw/nOT89l4rz2Sll2X26l3N5r/ftroZ82KB49Gy7+Xb8zeevx16'
        b'KjS5tbvvmbJ35+941mOrf++Ua9v29L3u0HPS9/atEt+fjbf06ze/tWPM5wtOuThGvCVySAlM+02lLuw943vFC6beyl18QUtjtTlY2CcRz6Lp6DxcfMgJEh/SaY86Qipr'
        b'wLmZjK274IQZyA6rwOgRLpeYmWWJ7qELVc/H8qXmdLsh+XIvz9z9jkPLTLkXaprPHP6GvP2kKJuxdy2oFrJphNicYXfp1TMZw5wamYKZiXMTH+MTShxCz62n3NS6QNRE'
        b'OO8htnu7hDLem92ZM2Qtygtw946Gw4SjT8HM6oVxjD/rUt+I+XwvVMgSnZthMZW5oqIizMPJPdAxU+aMTIA56AILcINKxXDBS8wiOnRhyponwzIIjR2WhArw58l0BXQQ'
        b'LqDLTIY5FgUnZe5wFgtueQkWmBnfzqMqaLBhssYRaISsINRC4nUpvB1PzmRSbD40RstZpDWv7ah7IX5CdbsAzfMxl0+6r76Dl1tAPzfsC4mOKtOY3ujScnOZLSq2xtMo'
        b'rOPnL1xHB2IqSk8JgkL5EJMNJbMYu19kj+ehw2q82WivWUtUz7z069BJSJNbwlEoojSTGkrS4MQWOgqzMEd6GUsU0vE2DwsUCxWjsMkGD1SHDbQFjpRIrsBpFsWlB2Wm'
        b'QMn6x+W/RqkOjLXMDJw3zDFboSolzDDHRdB7AXj9tsrM/exGiAjpqJtpLw6iCpQhR9lx+Gg8TJxSRdDEw+EdzMt/0VRLOeZmz+zGw42FdRFgIaFiJhxhIXXOoZoomW3Y'
        b'Ws9Ect5goQM3ra0n2goliEVXh4OQiaqJIMlGDV3crawuhJGo4YynzUXFeHRo0Dv8FOqDmqGod1AYQWETHuioz2jQBKqAnkeBEwQ20aVE18ZOqnJlEm42lJsNSrhwBcro'
        b'Z23F1RfhBu2MRkq4ewLZbj4BhXjC3KB4huewHHsM1dEludEGXcKbmU9hZz+JXIiKl9CJtkdtZsMMuvcKfEwOMeheS2nDhnDWiVijmtaw3ezNY3HjHMqlN2fDqbVW0ASN'
        b'6OKwpyy0BDOniDS75LG7H4kEuSkMS1NE5JoMnUuZ7KxYZJSWzI80DBdPgouoT7Hb7HyIJzI72reifOW5wmbc4imq98G9Pkp82703hD/CUBmKsQTfiyee7utKlEYyDBD5'
        b'Gc/8RdRqTERgDwEPXG04rQtqPFEprmr6fIJEg+xhQIaEs/eX6sJl6KTuxB5wCZ0eQW+ToHKE3/mwOzFqnE/n1nzNYsqokNCDg8ykEqfhL5pu7cha7vfCzOLoVlHOemrA'
        b'RlkSuOAGDUwlccFISnnCVg9vLA/akvZwTSKRKWqGQ0yhERpFIli2oaYhjI2Z4xYLnf+HYtX/Kh7NyHgzUwbdY974ewJWjBrN5k7EH/wHiy4GvBEWZMaRvO5EBMKCkCGN'
        b'NUOEHx0sBRDRiIhfen8oKxknYjEJl/VE47CsRTKvk+ewnPBAwEKYgAUkEgBEmdfAohu5JlVcUxVJscAlPCBXpSJlQVmkIVKjjs9SgQhyxPEYtydhgfR1eDG+Svqjip99'
        b'1HWXClYKIYp5DN//X7oiK4Qou1FD/P4/8GQ59U/8kOnHEFcxw8dmYtcPItj90CQmOQYRoD5Jf0uTsdPc7DQjeyH+a0BJ4ZM7oDbSRXZANtJZdQZ5ejF5bxv5y4n8tZe0'
        b'ozLkIzigpHDcG1Ab6U83oD7aj414TVEfHzo8bDb0/+/UFMNeSh/i5ueQ2dnH0dg2GmLBmp+6WRGNRvR/9K9YTaQmoua2+ADXh+VjntsVNBadFofjY+zkk73BlnMcC8fC'
        b'DeUoVhryDBP+tmfYI35K5Iix4R72DFvplexFSGofHNN0sJ85Y/b0WQ7QBa1JSYkpCclyTP1bMd/XjjoxibyIOjSV1VQ1VOLHq8swVc2CPHy4l/quQkWozE/CofOoRybb'
        b'Bbm7NJTHr3fgOJcd3HRuuoYutXRrQBaqdRBz+Ki6wM3gZqBUdIymEfAO0nQQyMsdnAPnkIzyWJT4Jnzu9DtgjqLCg5vJzYTL6AgNQwBXIqDLgeegCnK5Wdyscf60FsjX'
        b'T3aQcAJ0cLO52cFwgj68JHSfg4hYaCu5OdwczGNfZg83xaA2ByUOTiRyc7m5Stup0RqOTjfEr3OoDx3i5nHz9qNWWslWOI75lg4xN9Wdc+QcpXCRXl4Ox+A0Hsl4dJFb'
        b'yi1FJwJZLWeh0EYucHDOllvGLcPsVxttE39gu44cf0/vJG45t1zNglbig5pRmZznMH9ZyjlzzoFa9OENUsymSjgo0eJWcCsC4RC9utslSY6/5gBUciu5lahNmcaeh173'
        b'GXL8Lb32nAvn4u3FRqlixQZEvqUR5XKunKuTLb28Eg5qElsN1EEe58a5icS04lDtSNSBu1yPqjh3zn1rJPuS3LWYKeqQYm7AgfPgPBbhblDjfi/m6LA0xHMzNnKenCdc'
        b'CWZtFiUqoQ4Jp72N8+K8UB3U0cq1wzED2iHipqhy3pz3JKhgw9GpvxB1KHH753GruFXQzjpiK0FnZBxninJoIP0eD9aR0iAsQuBe9/txq7nVeNGxpYCa5wfKBLKi2vFa'
        b'9hVDO/OpaBqPOmR4pE/gEVjDrcF8RDYdqSDMDBTKeOIetZZbG+tAm9SH2jCZhAtG6Zwf54eq9OjVuZugQSYiGt9avNPWGavSBu0gf6pMiVuFUrn13Hr8hTlsOXWj7ol4'
        b'NXIpW7gN3IbFWxTdQAU7IFfMbcOP+3P+mFU+SB+PU4d6yBW4XdrcRm6jgK6wjznsjPpRiYTTt+ZsOVvosmWDXYnn4AIqEXGaaiT3hiGU00pc0GmU7Ysp327itAR58ezp'
        b'vCmeqITOZClnxVnhpUivR+IxaPTFy6w+iZvCTcFb6xLzw6nCElw5KlHCvBI6zdljDrdwLH1jvT40EAcOVKVB/DdQIWphc9GHB7HWF6/NdC9uKjc1BrVbWFN/IXR62SLq'
        b'ppBrZYcOwyGUY0XAnCJOF1WLUK8rbpIwZfqobye9YYUFCizniCAtET/Sgh9JQmXJhAO0QWWQyioyXzP0BKlELqEqPB5dWYHrIO2IeE7PSmcKvgcFPlRd6I95+cOKjkAn'
        b'SiUP6eD3c8kz+etpC5gjTkUXWTf0UD95ROD0dPETS2ype5V9HOaGaQ+gbrbiNo9v7/ei76OmZOIgSJ9QgjrcPVM8vT34gbEi6vITOmsdrR3VG1spmbF318+iAwBpcSiN'
        b'1W0KfXSIJikGwAEvKCoKXPYkY0Q+3ETgdOEUqqGfvwpdoL0j4hMbINQ+HT9npvg8FTd2u8BkFRkeUkPdAk4Ple8hnwY1kSwMScsYSGOdx5Jfq4OVndJm3Ajpva2MVuDp'
        b't531PhcTvlR8X4d9gfUYOtP7TPHio62TKTiPRX36rEjxFcshm+pSF2Eqc4DewKJy/0QSPwT68VBBI+lMB2TSkxIKNkEj+9iNeCPRhxYoasIPNdAum+0XFA2iy6iSDPpm'
        b'xYqIx09QxW39Djgz+FF41q5MshtcfWRkrCPZwBbOQX2kMeU5mDC3Jyru4ifP07UThslx5mBLl6AEd4o+RQfHZhyd+3h8JJaw4U0OoA8sYKOjhA80MsEptnMGO7IAWvD6'
        b'ODH40SgHStgUHF2hqhhhKyVTfLcStdAvRt3Qynp6GuXRwOn4gaVkEaCCpfSD1TSYQjl9C9SywU0lg4abWBQDpWTQsvzoJHqkJNNhpbfxiC7DchipQKrHtmsZFGART/Gt'
        b'pLeloXRDKcZk6TT62F7Urzk0rHhbZzsoHqJDgvmCaubOeGpPLN3250n41IOJbES2LacDgq5A9RRGFnB36F4mJn3yfiFKVbhDQt5KKzu7ECzWHhaJOL05+K4e6qOzkoBy'
        b'Nim6CSXLRHCCLiP6MegkamTjUWiLuq3onG+EVvoMnhZCF1Aa6wWxPs9TEKc0dMxqeM9j3uYwXYvqmKNpoi2JUHEEmVrWEl0juZDOdlffUiil3yKYYOKjAY20jrMojU1t'
        b'KuTGKZopW0lnaDMbja1wjraCDuD93zo47h2mVkoobWjFF6NiWs1qKIEjiq6k0m9BWaiFp2O+mI6KPWQbsz2Id0QJXeybFbWgdOiitbiSoE2DQ1c8ly4mxchN8KerWXcn'
        b'YRHoz1nUaaW0bJBSnkXFFjxdijNQrr47zb3oQqOr1sEZaCGZBfodPqOsZWGik4Uq9cW7NY/klvoN/xrs8c4EX+agNyWe5BvK8lJdFezRZ2jJLn4Vp8xpcaf9ZMHB0Xc3'
        b'7GUXFyvrcJM5Jyd8HC/4cXoCu9jjQ9zkf/MUOwWrvbIpmV2U8JqcEZc1Vt0+2Prkrjh28Y8UKafGBe9WMwlWe3OZIqHTeA0tzoTLclaND/bwMVvOLvrOI36IH5lpagV7'
        b'xCSvYRfL/PU4c85+N+cUbNSgvZJdFI0hfoiFUg2nYI+3ZYo6B7yIx6LhTE38mdxYFY66V39vSzIofc+LTIL3+Po7YxFyzQp6Q1ubfMAOFxVcxbHlruzpUlfSV0NjwSQ4'
        b'Oma2IfdZZQX579pi2oCfHUmddNpJHd9d7p3CfeZA//tpMT37gyeNJZQNmsy4OC4O9dlQ7kY9yc4Ks4GNAdwObscslMf8m8kE7nNdr1gDwo6Riy0K8lhGsJ2k569Y454b'
        b'9XmtYN9YpaaPR8MlWOQUvGDAb9+jbpVDAcvI/o1UOFayFE1DqZkUVk5+QBIVGxa+I5E4wj8uN5MmltiZRyXB+KIMXxLDmPgTUz9FTw9vVPpQgqsZmA2pdh9OcAUtqFK2'
        b'RGU57XvHpPVcK3dgHx8c7LhGzwRPhZdX1PvxF0TytbjdgUnZnqtfjNVdovV1ReB3A19FVl18+/D3qi87KX/kpOMiSP9Q6jG93hRWL3a+eS112ctRS6I1XP7kNL6yqily'
        b'CHoqVVSTumr5y9INRivm+wa++Wag/2ndtAzRmHk7vi9ayfM55nV5qmdOh/DJ1pOWizyXb6nL1+hdD5KAZ6YEPKtv/Ynl+VuOsR9NjQ2RdCUoNXfnXmxpzigO+Hjy1prN'
        b'e3829Wlyq6pwTNCJDAqQbI//LvfGB99uiznyanbJnYiwqmfC8+8F5pQm/BDs5LuwqjLgY9nANu3Pbqo3Oa9/btnu3Oq8H27siLv2G6xuG/dKa+iPXzcaz/+6TTX7J+2L'
        b'UQ16+fs/9mm4OUPiIzbx9fjjmdDFfp37G/aFu30tb/JsuH6oqfLrm2N2dWY2GfUGzNa3lf/wVNG47hlXJE2Zx5O1V/zQ+iw/O/HEkrgSo4G6pnF2Kitqvf0d1/ZU3nXQ'
        b'SVnb+pLcOiH86Jnr7foD4q0Bn44zflF68eOAWWtXNn7S8Un/p/dDF3+xuuz60k5XrZrIVuuN4hTZprla312Li/Z+897im21bZr9k93WDRCPihTfCf3nqxoyVBm0hS8//'
        b'9LGL+6atn6tMuzC2XOurhtTA12/v8n/GN/b6hah40Vcfn5gW17CrP0NfV+VHj5s2v/uvPWjW9EvPFN23QksT7r12Jdy3LK9T8+edE/aGdFW8Vnwu8d3Y/MAfsuaC27OO'
        b'+ocnvnfbpdzTJ2xRmr/U8/bPh3+qiar/3shu0Z0ei2uxNzVE7U0fhZd4ZB6Lmmf67c3Fk36q6tB5KeTsCn93nQc1C9urv4n4pOOHX3+Yo/bLafu7sm+XvZZ+6SULDap/'
        b'jUSXMAPRQWK9d67z8JZwkj08qoeeNcyvheRvwAeMLWpk8SHELjx0TGX2jq0kT6k7zReIJfBGdxLCW4aOiQQ4y1EtfyjU7UcdKgEk8SsWDkWq/HSoRo3MOpCj7WMF7d4k'
        b'Y4ibhBOH8fjMAObuhXdK5mYaKqgXtbtau4o5WYqAjs2A0wpnqUI4MSLlTiU+i5uFneM0mI2odqOdVTTehQV2uD/iZB5lT5DSO+GoY6IVTVEjoHPq0MH7TYZztMFgKaSj'
        b'3IVQQo03gx5vkAXlzObTsTPFys3GPUrTxpI4pksFdMlLXRFPxEtwn47Sqd8+bm4MiZleHsF6UhGDTpNMrbi9HlSRwi/xR1nUTLFKDQ6SBElYyLkwKowSOgSXLMb/37rN'
        b'PFmlqPQPtboDqvLQkNigqJiQyHCq3L1MSO/f8Z7Zz3mKFdEdHv8j/kGqzWI+qFIvGFXRJEXIbRagWw9flVIFrh6NPKGnUBdr8TpE0yXSw7+Z0HDkqjQkuDIvFsQ0igQN'
        b'7o1/ptKsqKq0RMKJT8JvzOATVYVBNaFoQBQVEzlCX/s3h0cmDB4cpK4+FUUe0b+hkSU/zxk+2bGFsqrHFkPDyKNHdT/ZxQabxMqowOyRKLGqg2egGzcUJVZKwykzaJcQ'
        b'oToUHVb8t6LDPlZ3RxAJytyj8UGfrEUkwcxxP4QI4T9AlUY+DlUqPNK+xIsetp6WNJ8oZ7/iWuSkcDuOerP4muqQ1Md+JNmpApxo7uLq60I2tquEm7Nbag7np0aVRGhI'
        b'5MRI1L3n1lfBLiHXI8yLPw8OeKq1MLWoLn36Tz2HmirastsOmpandki4uB+kv22NtRAUmQKwNFXuPhjCRrpA2ISOjoETi6nlPCAuUGYAdY8LpkQys52A7EG0x2O0yQOy'
        b'0C3hoduCKM9Cd5793995+zlzFqx/18QgEjg5iIRdGHYAG1Hz4D7go0bsAmHUYlcfWuxq+Dd9VYV++G8u9gPcNxpPXu7EAOBnFEzjmrlgwYcBQlCZUchDblsEheSJCqSQ'
        b'A6eg3o8E4DOUYREufSsFGlmhanTWffMYa5JoJ0/MSccJqpC2jmqLVFWgxwoVq+zFDLOgzXModz1dM3bTyZoJNsV/oovs4khqUKqOKpul6u7h5UXwbMregsdSeTScpC+E'
        b'm6hihr11i5pWsJpq6BpOTvjgCwH6vurxCaIv3DjBj+e8Myhn3WVI2O2n9ASnYOu7PjO4aDK4A7vEJOcp/uLDuu8YipV4Tk6Ubkvnf+G7u3xt8r+2iziRhJ+SxHhfo2jC'
        b'9CuHyrDIsSXAj5MTlvVayFOfCJzrd5yMky24QJ9ziSBsevAeKRY4Yib5suc21kV8gs99B06D0/iClxP2VtL39ief4gmcyoWZGGY2y4l6cPUbc8d84btWPUU9fg3HSW34'
        b'IydXycnx2HGYp0bgb/KbzIkzh26b6Pa+N+ixQPHbr+0Jf13zmvU1vI2UeKHjzxnfv0zb/XbR5dc5ThzNWXAW41LopeD7t18Xc+pmnCVnufIGvfROcHguzz2lwgVygbpF'
        b'tHd7evbkvor//ZibtvlQxL/otcxf7XJfxYvwEy7WM2Peu1SMcMbSeg3KdaUoIwc8QpAr+KEON9RiG+X9VZlEfgGTo+Wv/uG82nPr+05qRyMW/JL34Yver995R2XhMteO'
        b'58+sfN4297VLyjMzXum2SapLPeA7o0XrS2fN4KDaaRbzPDVXRf1Raxj9g+uHjd7txi+ZBYxfOkNzkbDkmdvKlzfvLzqjUnws4aviY4XRBTm3pfc3n2kyvL5lX+WW1d3T'
        b'o6fOF83LllnWfG1QfNrnX+9Xcb/f+GWh6BDv8/21l7S+KSs22nhmo6GH9fofcvwCrkc89blO68lkq7i1WVPKLrxd8af3s7++Gzi7eaK5V2bPHWdR2+op59dY7PrltqNh'
        b'24fWE+rvnE4NHHPt2cKqsJfHxCZ+Wq4e/f432365Jp9Ve/r36z8FtL9cderPTXvEL9wPre6PPSS6Z+CfZdWkGb3zzafO/uR43nnsM9lvXPG9uEt65BuXxg9z5Kuqo2bl'
        b'vux9ZZHq8Rde/Tnu81N/5F/9qfmq/Pi0pEMRb+pPaLbyj6xxzN08XmP12PZl7wf7NTZ0fHzvuy3fzrDNs//4/Z8e/Kk9tnHWxSTrr6csqnvJ9oOTr4/tOLb3X39uem/M'
        b'j2oGt3753Cbvzk+fVnx0dw9XvcFon3vKdhuv3168v+b1pxN983aFr/7Xsl8Ovn3Hbe46LeM/ed+S2sLzFRZazI3pOPQudEeHtC2IE6KUk0YKllww88UphCvEFx//T8GG'
        b'ylAoQCs6EQeXZzCXiovQ40B8RDytOTE6w4mn8ySmM2JR16DfE7W6U9pPMiwp4ffrBG+9fZCPSqlvgx5UmsmTUlLUNaBAUxO1q6Fz6GwCPnfRcRFU719H+7fKO9GK8bd7'
        b'oZqxuFGYpaTsb8ecJJTrKYN2zCxzAqTzK6FBEUYQVUD2UqsVqMxNwVVKVwt66pMoQx6pB1nu7PI8KFTwm/2KrIbR0DSbYJwZS60iE5ZPhRIVFphzS/xc/B6cQLkWNsTT'
        b'QhosmBkCA78YJKJyK8AMxEiYydyFzF/mAsobvwuaSL1ZriRVpwzaBFSNaS7Lsog6nNxdPRWjHCjooePhKG0xvaeMupzcV3mMOPHGoCo4Tz8kfjbJboaH/BIm3B4WePLm'
        b'44+Eov/SCv6fuB+P4mCHj0B6jh79J+foNA0JTYhDeVQN3oDXUsQn06Lcp1gRt4ykpSG8qhqNYKZGHQnIkyTeGfEK16J8rlgg3t9i5v1N3zOn8c5YyhllPlFjiDOVDIjj'
        b'Q5K2DIjDQpJCBlQiw5OCkqKSosP/Ka8qStQidWqTvzSHDnLSjt4/Psi/NX7yQU42kCa6bD/yJEelKIfCOw08xXoJ0BoqjGDlSO+GOEWicKHWZj5CNBSCQPjbIQgeyyuK'
        b'uUcjkOAjnmgt18PxuViII0BxolHEq1wHukQ+6DhKg2OoPuqlz2dK5GSnnOmRfhX8efCXwR4hX3+5LVw14qNonht/XhT/9eUR4UpET3QJGFAnEzd6+Vn+k+W3JVFnaEmI'
        b'2QTSqXw8ryY8PM/k5bX/eJ7PaT15nicT+nESk+IsNoDDbNsuvPHxXE9ZJlmzHLX8P5vrR+QS8p/okbkWeUWt7b7P0eQFF57OZ7MYHbE5zCVEmc7ixF9FRywjKl75m/Mo'
        b'/+/mcVui7sPzqPVX86g1eh7Jy+v/8Tye+Yt5JOYqfTi/28rroVkMoZOIaiTB/OYnTyLxP8ok08hniiPE/4stS6bw0fQTqooQNnVQpw4H8aIbyeB7T6MMsH2s8aoWpd+U'
        b'ufhb+7u3TWXMfcpSJhA+ZRWhNn6yEWOp3/bliM58R6148/6PJBYs+IjhVGjzhXOklXS8tCPhOCqR0MeXzCecNacVPy/BY4m2lGMxEc7uRJd8bdBRKxdXESfdIAQH8lvh'
        b'ZNScvc8K8hT8wLj6vgnXdVL61IXpWum3Kn5YuFzkkuQ0T3k16E8LlE76eYXX0fRx0ZZXt3/x67apa1793sd+TVS0dVJ/aYhle1JaaKrDJ8nvJJv3vnjrhbPXnj1r9mWw'
        b'71fuH+/81nG21u7qk2+/ZHbudUclg4g/d1zdvvu2euZzEz8Mm3B/1mwLZebJ3Yky0AVNVGJlY04MJVKoFGxQtg3zIK7dCJkP8U9ntsVx6DBT0Z0MWUdNLCRRMsnclycE'
        b'zYJ0OK/H9IanUKrFqKzYY6Fnp/sO9u5xlOu/HJXTyBRE1OZJXPJJazA3QuXkRg3USNRtRNmGWQmmb/NG+dQlWhs6p1i5EIWZfjgnnsPDeccoxvG1QS8JaKFQ4UE3HGRq'
        b'PHPU9shuxfvqcafg8B5WI7Q4PiwiiByswuAq/ttbOJY4E2oQ3RLlA1iM0kS9EduarOcB8UPgqUe6KSTqk3dCB/tFq9j4jzd3o86TNzc1rZbKoZvRaBdXfCrT8eWUNkxE'
        b'6WLUgMf13CNUVEXxr3zcQ5nOjoiOqB1RihDChHyeKpaE4ahBEcphojBxuvJB3l8cLgmThEnTuTClMOV8wV+Kyyq0rErLSrgso2U1WlbGZXVa1qBlFVzWpGUtWlbFZW1a'
        b'1qFlGS7r0rIeLavhsj4tG9CyOi6PoWVDWtbA5bG0PI6WNXF5PC0b0bIWycaGv2pCmHG6sr92uCSCi+LCtQ9y9XwB76+N7xJFmgqmbxPDTPATOmGm9ACaNKDkGRJLfBPv'
        b'2ozKqUMSc5nEsFss69jonDuYLSU0/RGyqjJI90h0SRqaifrc0SEm56TKEIEV/y0CK6LBRMR3D/7b1E6jejyc2ulJiZTIzmG5nMhvJGVTCKti1fIVJhFR0Y/JCjVqlZH1'
        b'/qgO0dgrmcSHTjCwtHJBdY6KzC/eNn4KwBecQ1nWtjy3kleag4omUIyYNZwPk8Un+OI7g4+tEcEhZaLJINmbSXwSTONCTZTVJqMiFlGrEPogi0TVIbFxnBaRoDprIYfe'
        b'04FusxGZc2PDUYWwO86M2tqXJaJ2KzdPFlXdiud0vaZME6FjqF0RRqh5q7H7DDdohmy8B1ELh7r2m7GQO227J5CM0KgPZfIczQndCEU0oo33FKh3Hwy/L0MnZsUJWEQ8'
        b'AU1UAbwK9c2jVBgdtCcY4lwPEqQf1YiWQhc6Tk/E9Vt93OGcC+qBGtwzUoummWi9iTbzLCpD6eiyQi1JMwE34u51CbtRrhHVomBWLXUfFvEs8QMCpuUVcyGXGNPPoTSW'
        b'aSaLF9G4TjSoExbw0klgp1VQz+5ekKKTLB85CfqQsZjGfeDgMFW3OULhThJAC4oCpBzJ5623jo6T22rcn1wWiEm82ZsEyIr3Yb05NcFLEeOKBbhC+dCqJdJHbVFUmVY2'
        b'hijTVoWrOwWr7QoJ4pjvXuWOWF8sxcwjrmeoGJrpkX1jPNW7SfCj1u2y1ZyC4ceHYiPxucm3sto0Kp7VIck8qBDRV5uWU3v6DE0u2PrHcdPYaR86DRNRVGBNg2vBAW0S'
        b'X2syHKBT4Lo6jEC01/CjgmutMGCLLT/KZCiylgo0ktBaq1EZxUGOmaT+xOBXVVAqifCNYNNYt47Di2QLuuJJ5RQ8VRqoVhSIDkJelPrblRKa2TXizWf3FvetRvZazts/'
        b'9bw997suyZUizdr6xpMJJ1PHjtHzynCLjT+pZ/+7uO/W/A0xz4RKXTp6t0euW/dcqPem3W+e3vppsrpBwd2oz3ZPufB5cuZKG3/JpQ8n6OSqX6717o9tlSrde1e0QX+X'
        b'RvTmpxqdX/51Q0mq9J222IvfJC9pPHHvhNKJi59fr2l8TSM80vC+yV2fnzf8HJqw7J3qm4XzSm+cRuMmHG/d1RWa+fJTX35wcNn86XVe6gvMF0V+fOcPWJ7yaoH6zUOp'
        b'KRFlKW82+e/Me/9fVm9d2zkw5ep7TfbPbX1a7LrVbOvYaS/HfvrbjUT/s79bbXK501ta6T7rj6P7drjfjJnzXs+MV0xnHHuvU/+FAPOWimKj6jX/evbIM0fO9N6yLrbO'
        b'2TB5w8/OFR1/5hbvW/Was9td54qVL+wv6Yk9dWf1YoufWl888rPnhojEoGcfbPY3lG233/EHJzpQ9uDXrRbjmMamFa/CA4wt4cSznQlbMg+OMgVKN9TEuHtY2rK7MlSH'
        b'sqIFEt3ekvEtWXCYuNdhZpWZGpShQIxyhb3boZhhmvKge9vIxCcCp2+yjeQ9gaLpDPzWop9M0jBABTQ/znogQA/j6S5AnhQIh9SMDlPKRjhj1ApFtCENVAZH8Ok/RNpk'
        b'IsiQC6gSM1Q1LEH7QWjHtMjbxgzvYorMS0DFLDhDAzqCLtMsJ0O0zwDyoRAdFzvCwXmKCCwdqAVyvWe4kfB8OZAbzftBtiL/hcZSdIxmm/AgkR+6oAnV8FAI/YpkFOg0'
        b'NBEVlbct6oPGEblIbKCTQQ/LoXIitYHlew/RQR1UAmVzRFCHMuC0Iuk61GPqmeuNCaKCGOqgWqfdIugat5jp/tJ0cMdzvYcoogyVo1IfPA5eymxGT3sHkiwRCooog2ro'
        b'nyKgWiPIYfxtLSqdZEUyc42K+IAq1icxgl22jVVfAm1DdExTRZSEDiiCxuAOYjEjd8FKbwU5kSpjBrr+/yPuPeCqus/H4Xu5l72HDEHFLbJEXCAgONhDGQpO9hLZCKII'
        b'yN57L9lbNoKKNM/TNh0ZbdO0Sdo0TdOmbZqmbdqmSZO27/M954KgaBL76/8Nnyjee853PntiOZ+iNgl9LHfdnAjKEjnRwHwz7BVhtnQgf9Wl7jDE5ahxVEURBtcRTOHd'
        b'a3yjFLgDt7ez3vPwEHIkpFvlmMgRKqSSud58D3HkNK/uPUl84C7USAvsU2TVQ0koZ7OZa8Ei1yEHJkVL3FQlQmS9w50HjrsEWax6LjGxJeKkQVyn4JAIHmClNt8kKY/0'
        b'ggUmfD6SQDVomw9VRNAHIx5G0k83XMk/bxbGcueDOSZxfFXpPlOgoMDVeOCTkuSEvNWPJQdxbbG5H1YXlqUKKUhJkfQvI5T5l4ysFpcopMD1RFj+nP/5p4ycGufD/rrv'
        b'KAjT1SQS5uNtDyRpRqqrjQdyX9kwKsW/ar7quOK/tvZRbfD0xKInlv6Vi3UnrntWKfmXl+KzHs2w3NZgC9dOQCLHPiqv/3x9DCRVvGUvJUVFxD6js8APlhbET7/UWYC9'
        b'FZSckvj89cPFl4L3Bj912teWp93lGBMUYRgVbhiVzHczPbr36PIpPF99+4uCZ9zAT5ZnNuAqgyeGhUYlxyU+V/8Gbrb3n3Xfby7PtlEyG9+w4b8qBi9/6UpcaFR41DOu'
        b'9efL8+7kqvgHJSUb8i+F/DcLCF9aQFhaWEjKszpWvLO8gG3LC+Bfev7Zc5dgmsuZe/rcv1qee/cScCWvQC2CMn6A574A2UuhYcEENE9dwW+WV7CJwyru6edvPbB870vQ'
        b'+tSJf7c88eZV0P3cU+cuTb1kdHrq1H9Ynnr7SuWanfySZr16+hWzc8zu8Zgb4XLMjaBQkCPIEKZr3BBwNgMhZycQ3BT6rPj9aaWc2dBP2tblnhHz85x15EUc8RP/03/N'
        b'zsYcJKZGhnHtn5MjWZ/tR/CYGMa3qeDaL8fGJT9pgnjCDLF0aU+4DKxe+b6AaxwwnL3INw74pbtIIFcoVPn+zF+HjfhyGtdxevMKqTjYlsnFTCbGB7JPqV9/Yyk1mgHA'
        b'15BJMgWy6ZuWmN3yRh8F8oRHhCV7Pr3wPZv2T4y3M9b3lXl7lqDm6QXwU5jNVEiSex9OSawsWPfIOkLC3WNxOyxYEgpkBLAgowgL0IIN/2/dgE+GjNE9t7TcEnKuIYep'
        b'AuYaig7/MLA0wjlI7oe6XE+CLXdFfQmdkvsOsmJVi1ZoQTgcyl+4nP6XOY4Sbz73zSs+++aTwpL5abKEj4WQZQtXTv7Jc9x/6TMcR7Y0UhS0QO1XvH/SOIT21nT9uxXp'
        b'ixyoMJLizEHhpAh2c9CBvS4CsaoQ+uNDeA/LAixgA/eiF+QKxJZC1g1xJGoxZ0KYtJce+H6U7+UI5xD3IPeg6HcHwiIjIiPcQ1yDPIOEH+te1tXDaF0f/9/ukbaMDxcI'
        b'xtvkfnrH8Yk4u7Vj7hLDJADDTfO1bkukJKsila7+xI3xg+c8fkerp/zoOe6o9ulRdWss4+kEm/Pk8d0ABMuevK9Dtpmh2eMJmnuMhRgm8eIDEenVduYkw6TkqJgYw6tB'
        b'MVGhX2IyFgrWYkEynr6OfDHv6HSBnFDg/LGs4dU3Ek4qRSUlbhInXaJvxmzr/xD4SvCu912DlMJ/R7+ZaIiq3XXxhLeRe6Bd0oR2ZajRj259HKDgbj8UrWfdGK1rrdvS'
        b'VGwTras9bhYqKN5jEnjuOyfR8IXKb7VD68veWrI/Eu1tsBQJfvQ7XQfxTSPecKBxDoqMJeotTGIlU3FVYFbkpC4rUdoxy5lZlkUaEtsysyzDbRzknWp3XFI4O61jPG+p'
        b'ZVZaaNDj3vWUtV6BWb17hAJNZniG/hDuXR3stXeTmDyg/oTEBOyUyQext8KtA7zWzlpRjEMRdMBcAB/DhB0wbUxI6gIjYoGMujhGaku0WFICNOukG31sIiMQGwhhwhAm'
        b'd6dJ+NmXOtjkopIucVfKodDxr4tCmnz5RO5/Fg7O1f4Qr9Anl4ZfwfGesqZHLNCMHv38OdCr4OnutTUWZKS5VsmMFbUxOG9fKDskEVPt2FEn/oeVypBbUkfeklvSC96S'
        b'4UXst2R42fctuSVR9C25ZUkybGlzPGn773tQriBJ2vTrZXZmbMFyUmKRktDg3P+qWoWKopoU52bJwAprnqfggg0HuAqsJ/b92I1P8HQNyd9J+Y87KmVqdWsFoVJlzHUn'
        b'W6BcoFGgGS791R2U/FskfCiGKuXKMQcl5xKUk7gE5dj4ocplQi7GXpHGFoeqhKpyY8svfydN0q9aqDr3qQK3It1QjTKp0G3cOxrcW1qh63Ll6XtF+l7AnqiVpR/dUO0y'
        b'mdDtXOUNaUlTFuUClQK1AvUCzQLdcKVQvdD13HtK/Lj0I1crT+vVLxOF7uAcs9Kc15B1F1IpUGWzFWgVrCvQLtCh99VCDUI3cO8rS97n3q6VDd1I7+/k5mRvqnJvadMb'
        b'8pzrk72hwu1vM9sf7UAqdEvoVm6HqqGanKqz6y0VCVrQX0ERYYnv7qPLWUXbHQxXP8EYAv2dZBhEvGAlh2C+yaBkw6BEZstJSIki8F81UDhJ+tzzofRVSDLTEaOSDZMT'
        b'g2KTgkKYkpz0mAvTJZk4TlyiZKrlWYKSltUrYlWxhkGGEVFXw2Ilw8YlXntsGDMzw9SgRNakzdr6SR8p09we2+Aypzt6wtfBzPB4XOzOZMOUpDBuB/GJcaEp3HI3r/YS'
        b'S2x0kXR+TyR7rC7RslyehV39cokWUaHoK6V5iDiVT/zu2ccvijuyxzzFS8z7ytLWnstZvHyyTJ2j6115HWvqbQwGuKsLNTN04QxdoXG0ItLzDMPSopKS2Sep7ISDJRai'
        b'sDUECsmCJIo8v6Yn1PvUKLZI+iY8hYYLCg0lcHnKmmJD6X/DoPj4uKhYmnClIexLpBl2nU86wJU9uUQIyIcmLh17uaiq87J1HauxzF1Lmat+6u3s7rlUMg0WsUARe2ER'
        b'slNMaIwrAtHaA9BLLkaJsZxb4CoWyGfY+/OOyhK7nVhDwrazWID3kqV3CrER2kN5H+s01O4wlhVcc2HpvNdhlHPX2u675GOKfUdp6kns3SsQmQlUbaS2YT/cTTFibxVv'
        b'wBpJR7BBeLiUeMPc+nwvsING0qzY4R2+bklzhsBYSrCeBKckQdIumOHEOpOzLHxLN1pZEGjyF8ObghSWn+MRibfdHm0IC7lmY2UmWO5h4mIIHSwG+lScLGbJnOQ80Vvh'
        b'gXvSZVhMkGaVTQRQHCYdNT+O0km/oC9v1HR6VHpEiyyU8jq+qAn90ft31c7+rqtk4+0Fl9sl1X4H8rNEmhqpv38z+cAHQ7a32o79xtDKIWzsVuUP3ivymtTbGPTPE+Xp'
        b'/9yRf+bdgNqh76W1Kf3M/cjsJ/WjrwWkDESfbP1GzI/Gk8U/UX/lbx/8o7fbOerXI38eP/oXu3cDt6V7HLr4jvqv9Ae+7Tj597o3jjcpR7xp/uG67yn/8Z53wdGM0R8n'
        b'ON6refBqfPfO5A/qf/5K3o357Q2KXW/94TW/AY+Mut+8cFVjc8r39GN6X2n0/+yzTRs2hqVX1ce2/ubgN6/Ff2o/9bnsfwKPzy2YG2nxxSaNoRybQ904DxwLQDgL87y/'
        b'aQHuBaxwQOIIPmBOSOaCZNXtOTd/rsVRPggAKmBxqbuTDzRwAqY0vdJDw5tIPKTMP3oU+OroQfowwrtHoRBnOBcpc496XOXkVpEbK/kAd0+tysy0V+FkXnssgCo3PuLD'
        b'SEYgbwSTWlKsUlAQ7+orS2KtD0hKwFas8WSgsFuGBO5p0alwDU64dU4MMzbHYiY/2GC1DAxImeC4Ou8hK8bGHau8shVpzCsrh4vcq95QL2e8Ax66etBpiTcLoQ27oWKp'
        b'10UZtC31bIAuaOAC6vcG8H6u0ps4JakFz7RfwrxYnDaVEejArNj5pgV/nCU7WQlCiRsMBq7IaEopYwsO8EPMmaRBiZenG1R44T3Cdn6J6tAgggpc3MptYCNMYxZz8TnK'
        b'LBMAFR+RBz7Q4IpYWmN7PL3IsndJumcZUxfpJMuh3NzNlCthyYpmOMGELF1oxVluVQZwH6qwxMpuKZqDhXJgH9zmjlsfc049KgZJysFSPUjS0POSWQwp1OBdJxb0TdPw'
        b'U2LZYSyXEWjTWIsxWP9kANxXiVtfy5/nywjo11EorFhsvQwXoa/CRdsrCfew30m52MupF7zPLV1nNdd+SqfxZZ68wu/2DP+liH92DW+bvqIk0utrqCNZgt8+PWn0qRv4'
        b'OgZy6WdbqG0UJRbqJyZb9sFZLrP6J3n7Cj7+3zQXT3qWv+jI0hITjViQ3Uq2u8pEzlkZuSjGZSvj1zGSP2Fl/H9qJM8ljfe68LHtLZ3bE3bOB0Hq0pw9W7vgh7w9u91W'
        b'YtGe2aFkJOR4gZ9m2moEJuyFOcjiMPhS+peYtBMzWEvWHY8BRVJIzCUuy/Rr2aqPPRdmLD7DWn1CwAKXdeUfGStn2C/uXqZYbbxyy6yW75OGa1wUCnQ3qti6rvuSUHjO'
        b'fFYg/L8JhV8CqsezVzjb+z4oh+7VRB7LWQhkkftuVxMY8uWjIdkHXu4uHicwh4TEYShStMI7mBslVrwtTmL0aH/XR38INNN4p+SDwJeCd2nvDnIPigmPCf4w8HeBseEf'
        b'BhZHuLJEiZcEgnolOc3ABCMRx2Fwxt7w8clXsxfoxEWexWyP5YJ4sBKKYUZxt2fm2nnQO5w4RqJsQyNxYIijxCcfgSIHhp7YsRT/8GxusWRvT8z8qmC52pD+hCk/e5U1'
        b'3eO5IHTmGbHabDA1qHN6DggloR0fYh6B6FEVF6jGRiOpFL4nU52Hm1sI5LI6FZxlHXIlTUyJ1/dBrZsxlGG3J/uWGddPwN2oo3bxUkn76AmbyluXIxLsVpvXYyJcQzw5'
        b'A7veZd1l8/qsQPAtZ/mM1IInzevP8IjcEj6vjf2MkoKaOF33aXe6wtT+JdMffa5b/MbTvSJPXxQRTobbTycf9gLO/s7IhzQREOllAiL6yqHexBP+2feE3ukUlkwKt4Tn'
        b'rrSuPF1jv5IYFs5rx0+E0qyhVCeGJackxiZZGzos94KXnEKgYVxwNOn5X6IMr804pT1TGBwqbWTtVSU44XfyjCkJnyOnz6wZGA5Z++SjnaCUiww/T58uLKmJw55LuvMK'
        b'VZHpid6KslgGUzJR0ZffFiV50Xs/f93jD4EfBn4Q+N3gyPChMOYx8P+GP45XTvj35hpJ79r67R+89MY333jhpKjnMmHBVGN2dMDkloLGqaaSVld/n0b7yf2lLyi16glq'
        b'TNWvXSw2kuEVh0USp+uMnbFj/yM9CXqwm1dnRowJg0tMWIuWZa2EqSREAwf5IugPcU5lZaQoqQC1EkUtRMCXsumnEe/xOl7iBqblQT/W8eNXkZY24yYxF2AhNJPGoHhW'
        b'Cu+EwyIXZxp+BkcUn6hQAfNwn6fOp6ByFWI/XeJdWbqCZdpIQIhDdeuvi+rxfNidHFfWJX39Y9i1YnheohiUhMVxZvZH4vmazGJQin/skVBuQ0P4PhdJuKP1dJLwjEU/'
        b'nRo8Eb7xVQWJJU/czJp0IPnJQJq48KXcjf89WXDg5/yKZGFtjx9Js60B35BKYhLrm8lH/hB4/hvm8IMXCD3rO/M3l1g0ZlsqC8xfEKf/5xUjKUnlfUsZLgEKK5bzQdZr'
        b'QDG2idN3uvPeuQfnj3NpEHdOSjIhuDSIPKhY8nmt7bTd+tw8LFPAojvXgg3JxUhEZFupJRHZTmrlrKHPBaftz3AWP2MtRjyqvCWbFHQ17FJQkufTzdFMsZUwMRlOtZJ5'
        b'DmM0MbJ3g9cyRi/BMLPWh0pK1n8lCHZY9iyEJQex0LkgPmToStxV4oqsyPzSuP9X4M+/Izkwa2az5nwKJsxQfSUlKZkZqnl0TEqOiuUDCpnSvKalmVekV4WBMZcCDb6W'
        b'lXsZ89haE4NS+eOiPX8JwjHgftIoreCZYslQZAxLdbFE2WUFK34WG4YWe67ytG+igrErjkI/wZqzAOugEnO50jHfHLfiK86IBeKml14SJr8byJl804+wejeCtM6jgSbd'
        b'lmdoAK4WIxvrIM5vN/Y6ARU0ljerRt2IC1HWFj8XJrXTt/F38sPKjFWkHNSOD9+PSM059pfXDAQfZR9T0wiVnZB6Yct1Jc3qq+eD3teO9Pz2eHmla92A6wdWrQ9+X3UI'
        b'ep12HOsMygjZ3q+n8fZ337zd+ul8YWhtr+HHwuKTdbnxTbEWHx64ferF6PcMfPdp2SX8eteO+R/2ndS6knQ5pfDfp2zSiuJCYvaOVWy8Ezc2eGH7qKN3xPnCP7+Y/q/J'
        b'Txpbj4T91Og3OeeM5HhKMwc1MLCUTnIQW3GBCQJNuMB/3S8rXmmZxBKfVKkMaIVZLgRppw6UrRQCRLoSEUAfcjm//TashjZjieFSN5mZLnOC+IzgOUs5491LWQvyh8MP'
        b'SUHHepjnlC6XVJxebbc0Jc2gSmK4VINRTobRVIPe5SRcgdgKiy8IYeICNvORBs3+0GTskywxunIWVzuoXZv5Gsl8VbvfW7KSdF2Ozjp/fTqrtlRlY4eUGtfKQ44LLdgl'
        b'TNdeg+LRRKvNfZyMYC/15fIEKRuPnl1h6aN/xj0Xsa7RfjqxfsrS6Vg5ayNHreWXA9D5KAHia4K3xDFBsRG+jiGyK/CebUxjCe/PMgLOUk6ZZUyBcwMz17NUgWqBWoGo'
        b'QF3iadQI15AQdtlCeSLsckTYZTnCLscRc9mbcj4rfl9B2G+K1yDsDqGhLG49Nix1dYgQc7Hx7jze+xgSl5gYlhQfFxsaFRvxjGxTIrfWQcnJidaByxpYIEcyGQOJMwwM'
        b'9E1MCQsMNJFEzF8NS+SCLzh/8xODBT3Vv2wYEhTLCHliHAvYWArVTQ5KpPswDA6Kvfx0brLKCfmYTLamC/KpPOZZfIkdBPORJsWHhXA7NOFPeU0u8yhfIjblSnBY4ld2'
        b'qC4DGr+MR4kPqZFRIZGr2B23o9igK2FrriCOjzJfOofIuJhQAu4VzPOxGPQrQYmXH4sJWL60JEM+bcPM0IvFC6dGJfErIAkgMi7U0Do8JTaEwIOeWRLHA9ccaGn1IUEx'
        b'MXTHwWHhcRJevJzhzQNBCguHZw79oDXHWQlDTz3J5UA9a8PHczoexTcvzfu0OGfJWMF7g58cZWVmyJe8zygFCS4+XoYHLK1MLbh/pxC1ISQMDVu6qqWxCPR5KFk77Pp4'
        b'WHhQSkxy0hKKLI+15o3vTDLk/skCL55Y3CrpRgKZbCvxpGLQb19BNlsl9KhKCN9qoWenJydwyKrAZNJe4gdC6NkdxzoMdh/gY1MLIyFL8WoCUWTMITGkUICtUGUrKR24'
        b'xwoqmc1OKJAyxQUoFx7Dap8UpiNg1zpteu0ULzHtMjPdhYXmu108SHga8o3HyeTT6jt55zjU7pY/hPWaXI/Xm3Gs0QBz50PLIYlHn89R5Nz5nDM/5KIcdMIM5PA1S+KU'
        b'BbqHSqQFJwNjxKbJAt4jfw8GcY7JFsZcHUxoPux+ahefE2piZOoqLbA1lsHmyExuF5mQLYP5jsZYLSMQqrPSHq1QydfodpURKBkqCgWGgSalXvv5oipjG0he0W2TEtgH'
        b'mrwaaMh/+IMbJCgYxhAnDDSh2xJw3UXcN2AZdksxt+KcokARS224Kl3cC++skxeoGdL0gYExbwa5ClKYJgy5B624fH0fZ87kzBpUlhozsVOyEfdT9IWziau7mYvpbg+8'
        b'IyPAEiOlhHOuKSwc7zLrnLJkQzqJNcuya6kRSUow6Ou87GeGbJyXh26oxjlHIzlJf4srMIJNzAq10jcKbQe44IJEaIdSlucuI5DK8L4oNFeN4ZPj6zFLYA9jy6nuLNGd'
        b'FQXmB603ubEq1V0Ns1NE62Dak7PcpuKYCKpNlzPOWbp5YLCkn8aNXSzd3GwjDqzMNz97iLu0s56QYxe8nHHO0s3XJXPVmoKi6LSezPjE2n1cxrl0OMw5GSly01/BlovW'
        b'MLtUIoEVSMDRTH76uQ04jzk7VxRJ4AJZi07wKfz9WKy2PmpVmQSuSELjEW552An9mW4sSViYacDVSMA7tjxGDcFskCRAAfKxiZmvZrGVt1bf2+74qEpC3EXIl8ImF0lz'
        b'AsIM1pGBSw02lV9VJKH1ALeoTdAEZVyE7DHofFQkAbNoeL6OgU3UZuxeUSeBq5GQv5Vvr1J7+jibXINwZ1X2/SB0890x2o8QOHR6raijwKwH2IjD3GlehEroYpEy3qYy'
        b'kHVGIAoTHnZT4E7TCu4e8SH9qdLvJOv3Z4r5W4QET/NQwhU8qD5FqpDNBhlCqZjvntsl4A9j3BAe0n5rvMR0Us04pyTARWVsN1LgakboKl9OUklMwQklnFCFYrybDLdw'
        b'jK4hWuQib8X3X+6L2rj6mSQCy2v+0oL12CfCNhzewUGMywWx5DFDzOaeTE1OkE9UVpER7BKJ8RZW4RTfRKIKO0g/nErB6aQEpQQoU01MccAmkUDTQHQQBk9w9tjdLDs9'
        b'KSFFgRtJFWfkcYKmZY/zC5AWHLmoibdkpAkbp7lyDZv3QfbyG/xDMC2UFmiGiRxuwjhX38bxBuZD9Z7lx5aXuBHuiHdgLcxyS9xsBmMrhkpOxGm4600rPCGyhiro5eaD'
        b'arh77dFIpDoRRZYRqMlI4R0HbOTAzR3rCHl3K+JsMq1ISV6ZxHzlm1JEYgpgkQenLkfIoVs9eZJdqjTOJx4WQlUQVHP3Y+Fq5uOBVT7YjfVEBut8oIxVL20W4ixmOXBT'
        b'pLCGHPZYvcYcUxt4GGiCXP8MzEnCWdVEVvO8T7gb2+AhZzHfShQLS4hGupl7pEGxu5cf4yjeEiXdhBHMUhd3LCbKAbf85JPwHubxFUy6Q5RCsdqNFYMXWhPgYwmU83Uz'
        b'emlJMz4yOOVMFMTNlCiup1igDq0iInP9kXydWpf1gn0Ce4FALfCGtL4OT86nNhsLfJ3fk6UPj77ktF/A9+gQfHpE8ssueyMx38qpOgPvwjD7rWLbNcE1T+A7UQUeEsOw'
        b'mHX4PJQuSMd+SXERmMdOrDGWZd3ac9MEaRuhgPvcF8ugCEvYkrvlogRRUHMjyn9sszjpBlPDXpi84u0Wre+gNvqRnsv6X/+17ttHvvvef5w+2/nLtD+e+Mmb4epSF7W3'
        b'6OXs2XpY7TXRC8duz8R3iSItRHbHvmM0KWd11LNS89cpFQZyuUFDwx8s3PnoTvq9hlM3R8J2BB5u2td+9WNT7d8eNnlzvqrmPcWCCzV/8jG6I22T+rHUfH2ZRp9bVccH'
        b'9jt7f/mJ3m/6v2GtXZL1Q/dfXzBNNr88ceZ75mekjYbe2u+34YuLHnk/yNb4sH/govNCz8L9whxhzG+MAxRrDlscFqlc3lyqk+h7wvXHweov7pf/UcLree8Mfzf0kmZN'
        b'yViyuKzmt/s+yxCXf/aLX/72jQ9/m3W/I1Th3/t+VBX7+wGtCJVY228eTv9kw5VfXw/w/h78MKHe1+17g9K65i84J0//ruSc6Xv7zebkx+9+b/T0n+H19RsOvdqYfObw'
        b'wGT937MNf+a/4+Lkm9kz8FbKZZ/LB0fenr76/beuXGy/3gjfeMX1lukLdYGuf97mP/nun79nY3LW41tdb3/Y9t2f/+b1b5/5Y9WHmpU/+LbZP995d+b9mNffvekqc/AX'
        b'8tlbTVEk+q3Rn8w/CnhwLeBnr/T4hHzyvrblNbuzP49/e8tF049iVT7cqnro/b9fO/np75peirM6ceZqmmjkmz/55JrmzGDPlh+o6F5688PPv33uxEDGNxenL/3xJ/v+'
        b'PpM50Q+1vyhpqrne+P3ZT1rmSwveP/63Nw/6/HtTS2pfif+x1BM9W7o9psI/35pecO7nxa9KJZzcMFCYeq3ivbdMg9eFFvzgU7ufbP6TaqHqp5UFB00HLAY+GmzEHw+p'
        b'/TBjg+kD2ZdttH947PW97X6vb+0e6rr8rxeHFPOsajrOFA7v3LE3eqPqhXtp1kl2X0T6fqH6j8/3+9rWO/V9ZOmjmPa34i9+uEmw+1+2Zj8wMuPj7dpMWCeqSuPVYRYa'
        b'LiK4DTNyXLBeBvarSwSKRKwhiSIIhviXpxQumcG825K73Yt7SB0LRFCKXTv5WhoFUH9l2UR0xouvKcJMRMkakvbR16H1UU0fV5jBSinsx9xQPv4sC5pOYafscgzayviz'
        b'YCzks1XuQ447Sb0txo9C5KCAaCVXIqMYe7BXEiKHD2CErzmL45l8LY8ZHIe7q4xNV+Cu21KQXBzMcbamKFfseVREzgOauTpy0H2Nc3WtJ5qVg8P+xp4eWCYjEO8TwmBq'
        b'HN+ZIUfviCTwL1nAW6E28HUz9OL3YA3cX2nBYp0gqul0uU0VY+EmN0kN3dgEroouklzITRhMxGnOzRjuEFWVOZghkLkmtU3zFBeMp47D588YP15Q+CZM4ABfyXheCaeP'
        b'XjZeER+JeRd5p2AhdLhEp64Ic2QxjhGSMEQn6PRmvZDMZYnP3yYu1yX0i9fnN1mKA5DjtP1RYk+HkSt3fxY4dRhnmZ3OhIRDehmLPUyI+5uLiG8NYTe35FRHLHN7FDus'
        b'eNaVZDi8Q6rBHW54dayELIksFgCVTBQbi+fO8Lgik5Dp7FfLwhOYzy1ZHzpuHrBYJfJawS0e7sYsfR+TeMv0ROvwvg035RaYOr5OdpXAe0GPb0VdaCnDCbxWULdS4MV+'
        b'e97uWA/TsdggvUrm1dFI3s7dKXSFrSH06kCzROgNp1vi8ObWCSxhQySyfmpF3PpVMUsUhz0O3DROUEMnVEICnpepVLQcA8fd2G6ezBoMeGKv7UrpJwFnlHFcuBduCU2g'
        b'5QR2Sctj10Huyt09cOY8CfZLFyOHzVKEMYP7eAwvdMVZSW1FKDJ3gdFdmG8hFOg7iqFNzoU7D31/7IUHrIAjncV+whmBLHZKyWE+NiRziixOsfqLjGeWQgExTWEo7war'
        b'M4Z6U6iVlH6RFLzV3Cpi1WqsuEeSItL5b808sJhEeANsprmxUQyt1+EOX++lFMqgmHvKy4TkgNOEUIVEYnT2i4+QCNjFHbsf5nKh5KsqitLZtV6SlBSFPszi3dqtl2GI'
        b'KzZZzMOMIg0/BLlSpCjc8+EOfpsYFzmTeJGJlAO2CGQ8pQxUYJaHjfwrrpxi57n+8MoYYBUY5L4/hqzFqOpViTtbHgcNsV2K0O22AQ+UE5CrCyO76DpMjXYx4ImQgkki'
        b'UItGqv99JtUj0/D/sIX3Snd7UGjoKnf7x0zE+nrW8gOs74oKFy2rxVe+YfVuhBu5utVyQhOhhpTKciStnJSUUJsZpyURtPTb451ePhUrioWrfj4VfyizSY4bj+/xwpu5'
        b'5eh/Ja7ajpg18P5ERklGyGpmq3FrURGqSGkIVTjLvRxXg2c9VztHhYvmVRGy2jkqXJDAGl7VFccise3L8wb6ZVt54jFmtF+2kiceX23v/+/qlsvy8zwamJuRn2x5bs5X'
        b'4Ey/FStKOrh8LV9BluBTs6/u2l1xIEait+SWPKmPshNDxIJH/8kIVljIzgsEfLIR7yKQl7gIhJyTgLkIpArUCzQKRAWa4ZoSB4G4UCZHkCGdrsH8vGcEN6Q5p4D4prTP'
        b'it9XOAh8pNZwEPjFS+KHV/sHOEt5kMTSu+wSfrrVfemJ1flIyRKj9YohTCS265Cg2DUNmsHMN2HItUNixseneyKex0jP3B5rzrp7aXm7DbmcI86eurQO3jrOL4m5Omjp'
        b'sbxFem0DueGxuNAwSyvD4KBEzqLLbzgxLD4xLCmMG/vrubq5A5T4Mx4vgbSWI4KGX7tEh8TMvWTkZ3b1L7MDf12r79pNjDZ5prDMXUsYMXd71Cv91FqeblagUeLtLjeS'
        b'x7GjMJzCwpmJ1XUxDXSFZZI5y7HQy2fZ0ArFMMGMraTOykNZLHZw2ncKVmGzsSvnJjciJlQHY9jDKdF/N2INIgeU5NUClW4pHeX7zfw+4qdcv5nP93D9ZmYGU5wErA/a'
        b'sJYxDJgQ639AUkwhVvgwK6mHO8eCzzwRHrzaHCDyU8Y+Wl0Z30J7Gu5BDmutfcaUtdYWp/Op9v8I+PzGKyJDsWBPYNgbme0yvCr/RpO9L/f15Nmz/g+k5oSCwKzouQty'
        b'zvzXjl323LcynpeFP5a6bSxnGHguwsuEr+EJY/q+lmIBDm5mzdivYnXKMfrU1wnaOKP3SaiRpLFhoamrB9Yway8Jki4SMzrXyMntlLOriSsvH+JdrFB2hYZMPnKhAnM2'
        b'clKCdvRXiVzAvkwjIW9a7ITZa0bHn2wRgLc8jvAFySvWX2CmUO30FcbQ7TjJGWJcrsEiNy/Jx4UrZ16yO+9aNqJCNjyUz4AcY+6Qwm1Y1ptchowgMKbltJ/EamIfzR/h'
        b'N21PH/hcRDzFPiv9jYhcl0QZxkCYBd1Immu+eTHDnVlSQnwE1wTX8J48d5sW3jjGpMJT0CJglpR5Y+7oRTiw11hWcBHaWGof1KZwI2wTazMjSqiTIEoQ5YFj/F6nT7Hu'
        b'u0XMEi6DPVEC8QEhjLnKp/ANA9ut3cxcsR56VhcpPYrTvMlqBO7KSzQDXz1eNyBFJSvqTzLfkU4aJQ554Gf7basWy1+zV/t2xE//cET/cGbr9/MUC9TW7U/W8j2zxVpB'
        b'bH2qzN61R+svdVPKsfI6OzRk/yH3h/Li376rl6bwcP/mswHNbZ/98aWDHTO/8N73gcxrF94OcJzu+8WN/W9dffX1b8fcDrl/Kbp31Oz69bTestkFq9mQHcfeL5v94XaF'
        b'f1S9M487kydDGoqsZf7+XpRhZ6Pl+/EPp154sHNHwWsR+Z+UNPw447pDuM2mPxdd2/P2uf1vv3r/VslETVGYt97IG/4Jn5m/9c9z+pO/nFOYD/3Q4vOK+l+lbXlz/+i4'
        b'fLRd6Pnuj+benJdNirQPtVmXumVvrP32LU5/1/vnezNzrx54+aTq9oPW6z5Mulxhp+WddU/o99cPRyJuhh8J/se3Bt54UeZh2suv/yHGbUG5tzxW8cc5vpWj/6x5J6/2'
        b'/F8//kVw9+60wU+DjzX+TfHHH7jPJFifHFrYaGv9xU9OtA4ec7rs/Ftv19e3vpV55gMjXYuEVxp+r/Tnpp8GbdFMMHb9KPds9E2x04dBL5/5/Q693fHStW+afbMv9ZeX'
        b'f/Hn9z7f8q+6N4o3vaRr+vfMZKHtT/V/tVPfOuy0d1vX96eNaz9L/fXiF9L7dJrqNF8w0uajSkphGmd43RZmt0vU28FUPs+ubZs8p9uy/uaP9FsYwmYuKtU89fHap1Ag'
        b'xt4IOVJEF/nh2/QsuQSDHljgi1TESG3B25mcnQQaD3lyCrCqRAW2h1JOC1Xdhh2cZQIGd0ny90axngtzNYS70MXiXHFo7XqqwgxO6dgMWUwpYH0xN23jO2NiBTRxy4Zq'
        b'gtsBN5w7yzmjVvTG7IQsbgEOgVAi6Q4kPivpf4kjnP6XgCX6xq6m66DzUSsf0iwXJLX1iQUEGdNylLZwmr38BilSv7GOU5GFWOhtbEoK4bnliv7GRyVGGxW4jbOuayr9'
        b'7aRqMQw1hrqbTAEPxTIYcJfYdVQPiM6H0dK4BI15yIcZTm3DCg8TV7izm3ENYxlS61tI/7wuyV8c0UFmRCn1wDZsZw0JZQykxDAp5g9nQmxudHotHXMOhjiVz+io3CMl'
        b'k8EGKZpLWqavG68Gj0PbpUc65pKCiTVJR3AGK5OZcwLz/LHySR2TUzBtoE06UBHv8zpePU5DPtPw/OQf6XjE3Gb/S7le83+o1D2m2SmtDFPgVLshxhG+nmqXKTBT4lQs'
        b'BUmzTDlJI00TrjURfSKib6TEnIIl5p7j/2YNjVgzI1a8VIFTx5YUQDVO/VLiWh2x7CteQVPg/tTm5tHg/kzXfzwvYsV+JDqZDK8NuSxrSEwRWaGEqf1fn6+ReMVk5ssz'
        b'cpqYJ9NBSEhMcmfn/PU0MdLF9jxdF3vWSSyFkFmwZe2VWkMPY3IrJ7N6CrgAcWnSvPgOAVKcLiZi2li40rLmJf7KmlcEaV4Oa8XcLmlej9oELIfQcpG3/8dh4/w7SzVw'
        b'+PfWqHxpZniMj7rhlvKUaCIuypypZ/Soi4/XoQN7LJg6dCUomcWMJCUnRsVGPHUJfPGdRxE0j9cb5L9/rtQWOT61hdjiSNCq3JbVYimOY9dq0XSXhyPnYrSHJp2zmOv2'
        b'qNA1c2ifJkGNMyuPivEO7822wOZlh7a2P+cJhQa4DUPEtvslTvOVLnPs0I+a6/qLVFIWPbn4avnvPjQtnlCGPVrH/9TRZn87QvBN3cLtgQIFnV3SR/OTPTUPvqj9SZ+u'
        b'0etvv3Y98YP9pd9p7Xy5MFj+9V/0q+YMHjH8WfDHg3+MCf5lbpq8s/bP9V7t1v3TB8f/aPmexzmLnzUEJ6Rcyc367q/cMj8pG/20+PXUstTBBffLb6/D92TjPLa+Oz9j'
        b'JM1XYO8npaSIkzGwzUliQk+N5oj7LlXM5+NlhVj5KG1GE6r5et+90bi4LGPE6z7yhgTI8fbHbK8Anmteu/4Y38yGOZ4nz8uzhgX4cJvEFN8l9MMJbFiVDvNfcZIVhF4l'
        b'hcO2VaTe83lIfaZg/VLqDN8XeYncM+KevuExIrR61tUEeTVFWkGQv15lbqK23PsWq0kuR21P0mfXnpvaFm15OrV99kZZGdr0qHhmuPmfFKNcqmY6+GS8a2JIZNRVSR0i'
        b'SSXdVZWP1iCnx3i7SMw1zpASdSU+JoyZgsJCNz+V9Eo293j1Hfr4q3RpEaxJvMSeXEialtU+3ufldzJQ+LRwqmAduSjswMqoh50HpbnGxSf/Hpb+CktB9//GGy9MV044'
        b'd+UaSX9HIyQyPCbYJCg2PDLYXZJv3N8mlxBrYiTmkDAAa6FT4kIzwQpezZhAvsU7VF8leVwyabDPkpoxgmU8jueF4/QTigbOB4vlYHIfn858C+/dZAVFzGnQUtYNkzf9'
        b'uHgkmOKkO/+SGwzLwvhNyP3SLnFqQfz1LsFZEofHh54Pj60YFi/XAF024T42w+qy8KdWY+rqgpePnuCQj5lbm5SW6MzXRb4swe+fkQ77ZatmJSekPT19HT2NpDz5/9W+'
        b'pILeo/IbLIOXy9njEqK4QHvOgs4JbxxN4fbGH4ze/1pY/4oUPvEA/aqiKKkXICclVlQQam96vBiempqalJxQS1VOqKJA36+XE8r8R8wO9j87bmoIzWI1hIab5CT9vW5h'
        b'79n90PBk3riUYNdO6as3bVL+SlN6wAC2QxtU28Zhyx41Uoju4v11Bw9AVgiOyViTHlYF1XKk+bXhrU3KUIl5JCWMQI0Yco4fJ5UZqqFYqI8P4S4+VIYma9KpymEyCGZw'
        b'0FdZCu9ADo7Z2sBDGHeGh070VAUWXyNlexBGzG5AtzvcsbmBC9gvi+MkfAzBvf3QC93YF5Gwdzs2WWAWdsZCO+biIE5iyw1bKIE+LIIJHacEGy9tKNmKWccyoi1JcV+A'
        b'u1E2mH/Zaf2moPWO1m7SAXuvm3lBd4CBKSnSMzYwj/0wBZWxMMQ6acCsM8xaXSFVdu8lLFXGvlAc1ySGfpvU+C76uY/1gcew+aRlNJSF4KgMtLPeeXEwQbp4uw+Ownjq'
        b'FeyBhxlwHxt8oUoPuy6fY2aug+vwjjPc3wOltPcqKFc/DmM+kLPTjRYwi82HYCwDh09Bk5Ckl2a6pVpopb8rIukimqErdaNIEWpJCuvYa4LdOBt5SMEGZ6AgxACynK5A'
        b'bigN2+ABD4xCHOM2OWJ5FD7EFlesC9CF0TQHUqYn6abGbWWg8ZSRH+27BOogT2GHL07pYid20b/uekABtPrTYdRBgwnePWS33XabliZOnqYPWq/vPGeMTTikpokFWAkz'
        b'vkn0aZWKwhZcpDeGcALGaDnjAmywDDuMTeehZS880MAOlWAPKI9ItsMsb2zYCCWXDsjhIswZaMJcDCzqQ34EvT4ST6Jao4UBdoVuOX3W1hxrCA7moC8piKCuHpt9lfTO'
        b'p8cevo7TBhc2QLMndOmdwzE6nwYckKPNTBM8NWOXPZbKQcEJvLeHrrEehq24psKLeBdy/OkGKkyPEDgUp8Gkjj4W0/ncx9sqN0X4AIuctmGtMKVMimn/O2nmNm8HKCe4'
        b'V4IHOLXuhj3dbv8JyNoIrdhoqrQP79D9TEC76AT0hQRtNYLKSDGUGGaaQ++hlPRIVZIGi6ALB+hkS+MDz8DCOn9otodmmIAeyAnC1t3YYLwD5/Ae3BXBuDzW6uNskHQ8'
        b'tsG0X0DqEWzJ8ImBYWyhg1jYRbsg+MDRWLfDNES7AbRg9kl/GrvaHxoOQiMUBBPuZUtZeWA1jJvSM5M4AEMZ5zI01fwzg/c5RWCr+rV96jhKWy0hQM4hnLi1n5CqyGmT'
        b'+7ZrLOixAppwxIJAfJhAcw4Lg7A6Bh7Qnk7gfSiSxV47rL4OHSluDlE4uhMLdpHGsXjjoFkm5F+U94E53Y2scBv2qx8Sx+FiIE5KYWWadtAJzIUpBSi96QyNmG3gBOUB'
        b'kIV5oarQAQNePn57QzR26OGgg5OClobZHml9Sz9CoDZ3LPSh622EsUgc0oVCoitZQdh3gK7yPtzCPBFWe0IVThhiqycW++MQTInVCfqKdaCLdsJIU96lvexwoRBHYDo1'
        b'TQ/KNtKUo3S1A2kEDwXp6nKED1PhWIvzN/ZqQQ3NlkvXM050a0YuQsUVO/RIYrh99jQOE9rl4d1NF2DBww0WoV9+G1QnEUXog3yrMJy6gkX+sGC2nhkHz3vBXX2CuWEs'
        b'84ZqN1f186k4Q/P1ESy0nyP9rYn2MAbZe3FYc6fPtnVekE1nPhOAvTEsRMcLJo1wThoag7dBJ8kTKa9LMQtZhgEBpC1UMICkVc8bw3SKFbaeF9OotzE3NghuJ0AuTigS'
        b'ajbsP2kCfWqBbjBoB6U4S+f1ABv0CZgeQjFtbhLGXCD/HGFs3hZccLazs8VGV+gOVVPAPALaXgKru5C7FZoNrxIUN0jZwYNrggNmLlhzOdmY7m4K+khwKoZ7hD3VhHYt'
        b'wecuxBL96DLBlmg68PsCgqZiAtch6IZ6rD1/gujiorHOmeQLF+G2B62whxSv6V2EHlVHtuxNw1IteZhfCbSEIvUn9WgdM6mYYyqfCdOxHMmsVbkGTUQr+xzcD6RvDoFx'
        b'z+s3tEUXnaBEB7LDaWOLXHX5Ssg5YEcg3Ch7Bcqg/xLUKNMlDxoqQ80hbHKG28n0SDaynXQQhyuHfshSlcIcW6Iivetk4e4hvKe7g8BhEu7txYdaqdgdu+6aODIGs6CO'
        b'UDYfa1XpoHpoe334AKZO0n12qWNxwIZIgrYcnLCHHjryB+d3Emu6E5BmQNDbecUWKwOJgTUYwWAq4USpGV1Fl8NeInOsvjLxzvP7Lu/Hql3ROJBxVCWdFpgDWQTLXTBl'
        b'YbgrNAimiOLcVdLCGhbJpoSFjtC+15dgAjqv0QKKsGIXzJAMOwwV6dglq7+NDvk+9jgGmMNDbFVw3E0bzicaeZsYd8txmHKK8KaLnIJbSQF0nU3EDzvgfjqWXIXGC7Jh'
        b'WG8b7mTGMfUKt2RiN/kpRBYq6Zl6Gycdf2yAlstQLHVVF1oJvukECb6h/Ww0rXIRO0Tb41wdsShWGavCzshuuIij66GBQZY5EYEuR3WC+L6UHzNaWwR59ozWxnIixgMc'
        b'M8ZZ4YmNgXBbFpu8FYQwwaKQywlrGqEyGSYFRG+3rcMsCzrgRoPreEcW7kFPmNMuaD4Gw5rEDpr16PFyFWyVvWIQTUDTrErY2LjXCB/6mTlDy6nrWGsApa4bDxInuKtA'
        b'Z/MQS2RPwmAgw5UgYfx5Jg21xeIY3r9whugFo8AjRAhIAIk7AC2a9sbeGjgWAFWBx+HWCbinhredMs/Rwdw+eF0TSn3cA2BwO05nbjgWSIRjiO5j+AqdyjC0nLsmxHpH'
        b'S5j33XNd5RhmQws02oUQY75Fl9ylq06nnY89IlhUx2o/HbX1xPmKtaDygnuQLyHuguUp6xhC4Rp/qDGDHHctcy0ciIERe0K9wmio3YG3jgkxS/ok3As9CnWOUTBl58na'
        b'Vh61Onbi5npsIthnYes0X4HgCvGALpyQgduEBEXahCyTdFQV2LoXFqBUj3C0dTvcz8DZBDuC2UbidOVYb5OAXQ7MARd6Kg3yneII/m9nQH3GOoKqmdBrOBihi41EAzuJ'
        b'SBQfxrIz6geQwL0Se5xILiKA7jU8SGtoo9+67Q+mOakRVzy+HqZ8CArvwvS1fYTxCzh0DEvp2PKI53Uc3MjksUQoDTfcySARq7SOcJSgi5aZBe1RUB+snn7Vg6UZEfLm'
        b'EpBVR9FqBkkiyJGC8hQ6+FK967S9FmKgw8Q3k/xZH7Z27NH1UvYhPtEfrY2dYVjnQvfbh/fPmxCOtwXSKu/YccVWCq2IrDI8X8B6Pxql4GLkVcaEMPuKHk7FE32ZxLxt'
        b'jmcVcFzfwvHUhm3wMKWCAFs6Jo3AmkXDL8kQxjgnvILlJEPYHjKGu3tg/KriTivZRBJgGx1PY/VR2gvcdqAbXqB5pxLplGYZBfLfAvmWmGMRBG00cTGMx1+3VdroBgs4'
        b'FkyK8iwtMw8aMjdBlvFpuu458SEig/Uwv/vAERy+QCJaHc6HkXhZTkxsiFj0DBJRy8k0xVoNAtrCoxfgtivWe9sTY60Ms4cmv90kdPTAfWuarZzEkdtydPIPVAm926BT'
        b'DQedodwiDatVPDZFXCFily1LGNJ+XeESjG+3Pu6ua6tMQDYCdSqmG8R0aG0KGlY4vWmHnMgRb21mQXzbCfB71fWJy5fTmKPnMecC1DoAkSY7IgtEnUhKwHuXsBXbDycQ'
        b'xaqDfuIlPSTpj9NNCU+anoaS7bHEqFtgxAtzzmLXeWsodjfxoJPLgaJj0fpeTqeYHFN84Sb0BRvhrRDI0rxuiA3ErarO4WwiQU/9KRwOxELTPdAgRaDW4Y4FDrTNRaJH'
        b'oxEXSCepJNJdpKdLpzwdiDWHsQA64g7R6Q/shXw7gpserLII0Ao/YOUVDD2BOBd3nujy7cOqCtstD2rpWRoRUZ9WwiLN4547iRcubodWPxq1Wpkg6+EVKPY+zaIVz8Pt'
        b'HdCnFYoTsTRhC22z7SLhQu+5sHVEfqph1AzGFOkwi7EhAoo2weSF+Is6R2Aohh4ahaZwIhBNomhaVZYPgfy0JVTYwsJO4rbzmJuphQ8FMdhiTLBQfTXlJ0yM6NPVYECZ'
        b'HcvB5ALBZBoOh+HANTmSenI0r9P5Ze/YQBLutMEeDaxRI1HyjHe6M1Rmbtp+PQXyg3RPXlLyJvbdzX4gZz9R/nqiI/SaLZOabqgpw0ga3es97Dh9RJFY5SwsqgZiLzZF'
        b'E6vtl8asFKzzDYOF67H0VUvwBZJl7nCiA5DocB8Wogj4p4J1MS9xE/buIqDoItQZ9o3FqhuGRB1ambgbSQsovGh9RVeRFSAlylFPh1HiEUBy3lCGT8aZyLQtSp5IEms3'
        b'9m4hwt1/3i5NhSVDAsPbSpiLjbfTgFnVZDqZ7EQSJyr9PS3lt+F4sCfegnofemQWcmVxSDkMC0+xzq/0cYEGjsZDsyqygmjtaTh5iUB13FzJ2JUoVFOUmmP0NTtSnro2'
        b'EJaOEb0p0d9FejDU7SF5s1JHC2pjDTedIHQd2YDzTkS6ykg/mSaOfC+WRfVjdcJ27NtK2u0Q5mZA8y5TooBzsjRZDvZZOoVZpm0+H06Ink3YkMNyfZoVoNoCyy9bYov7'
        b'dsKFKU31pGCigA9w6CwOXSC06dlMINh6kMjZXUsowLn4WOhOJhW8kFRlnT1aRDEbjhCZnzq8lZZdGQllJDNI44AfMctCgtQau8s446eHeWKoxbEwmreNoK1ZsDXVNv5s'
        b'kvZJuuKJLbsJXdqgKjQZWu3SoHgrFkmfx5JoaLKhZ5m/dJiQrug08YkSEkxatdxVoMN1R6YXV1vqTnpADAmKDT52Jw4y3WzYCnodEnefh7sEVRUeMHE9SiucaFCTKgH4'
        b'tCl2n7rhhDWOuwko7uhswWxz92g/LBesM5Lh8m5PsSmxLMTNRVogNGeh+eMiLr8HOzy8XF0fZShB9xXu821JJqlQ6GYsJRDaCzipvICLerGB4suBUMTSC4RH6As3R74j'
        b'80MYgG5HcxZeLxQIXQXYsg5muKkNMNcWKk9giYmQK1jSDvU3UxxF9M7gDi86oBosY7WU7ZXovMduKmw6Jw/1h71VgzSJJ1WZERh00QnVMUF9B+a6OHpAfrSdthERmbvY'
        b'q5dOjKkT2l3UHM4xRza0BmMFSSqEvNhxgJlbSOuuSjNLOQZD2ky+y4DesCAsUITOxCCW8ASLdpB15hTWedId0veEh3kn6Nce6GeplwV+GiS8tZjTVbXtPcsqcWdvIDVg'
        b'YncAjVsh8KI588KImI4R862hOyblJuoG5JsRY63yhcodpCFMEiScJcmlagcRt1GotiINKS/5kgc8dCMw7yH2UEIANWlA2lIOaWSFVkY3oMCSxLZ7RCDGiQ/chvHNJAYP'
        b'QNOhsENXRVghG6aKjc6XYfAAziUab8L5izh81mUdDMreSAnzSLxEtLMKeuSZxQAaDfQwmw52mOhQNtHFvvNnudawdVgfoBVNyDpPS6jcT1vts12vcEYJ20MCOZWrWYQ5'
        b'e0l9yaJTGUWioIt7oVSE4wG7vfZinj/Rs87DOL6DEKbf0phrkzsIlYdJEqqg/WQl6qSIiSVVJtEeemDh+DkSI2ugeDe0y+JIFFY6Q90RvO1HmlQpqSwLsuuwJHBziNEx'
        b'fRyRg7pAqEskBFkwUknBwZDEROyjn+oMZVpu0YHT/qQ8jhIVrrLEyWNON9TDQ2FmlzLMqmCHMyHUrYM4au5COD0I+chsOkWqpLpPQ/Z6aL1E+A/1R5zPep5LPHNWh0Sh'
        b'QmLh8zqHsDbR3JIIxORVEdGFXhgx1YbFlEgcPkhKQOVuTWzWYRSc+FzBnkxW+W0/yYlFzApl5BlOfBTumkNLMgFUAdw9BwWxxLp7YOg44e2oWyaMXiJFr52udNTVmjO8'
        b'PBARe+k4F0FKVC9UHNTRv2lMEue0J9MfsCoc7mPXHvpjERcMtaE+LMkkWZfkrGE7nLuojNnK+EAItw5C+8XMc/bJKQOMd3XThkset8oQAb1jZ2ivehVHtGXWp2JnKCFH'
        b'djCR5ImT57DYVUvbgXSWRWhIpOPMV9SSPnvJ3ZtIQKXlegKdehjTwz4LXbfNNjB1nTSBAn9dL9MQB1liaHOnTnPmmUmvTTRJM9QcYHXOFWgTk7EsRYT4yUIkzqbArBGM'
        b'QYmNMaFGH7bG0j8qru6DZmJoRNgrGah2w8RuuLMnjsT8dmucDD1HB53vcVqHCZlIFLr3jJBkvQeE1NkGhD8TTsTf2sUG2G9MNHcKuzVPw8AWom7l0GKf6E4SdnsECZ05'
        b'9oyuTkB2RgyJ9vr2JCR066kyo5Y79qdrHFOAoSsXiASX8up/UghhQOXl7bQsYmbYeZMowbwBIUIbabfQ73FREI0FR2OI5LRePBpBLGEKW8NohdXJxIJz6A2Sx7EtJBTG'
        b'Yk4exGkdNXi49SwBQ6MW9jqYsRPZjYM6YTgfRXDDJPwh0hoeJOLCRWkbNWzSt8Bqr3giaaWa2KVBmlfNdRKhsmAxgcSc6SMwqO6164jlNmK8t7EuQA47neLo0Ft27UzZ'
        b'aBSlfdJJQx1va2amWCtD/lEpT4L5IVboFfpuEiHoTDntDCXniMzeMoY5rTBCyweEF7MZZ64Qk4yFchFO0L9HSL6bD7pKxLbV9oY/9gaYElVqxmEjuH/0Ioxu2u4ihgdE'
        b'F2rYHdM9PCTS1kT0YVSd1YzCxZsn3Wncnv1QfWWdkxdNf0+fjuT+MZhzICJccEl6y5FkZ6eUn0qxRsUjRFbafLBkWa09Q/OXQcO+TUyzDfBWFMKMBhZ6wpiMKYyek9GG'
        b'QRzfTPu6D9P7CRbGrE7jAhSbRVkRlFZxBpOhLaZEy5iVrkndBPKItBGY5sM46Qb4MNXL1IgubRgf2DnAoAE0qRqspysohelQwtnuIzYCGNQj6jK0HZqsMGszUbxJGPHH'
        b'Dj9o2RtAxKfABVpDA4gvjJ1m4kkXdgYk7pQWRdpgvTn2pmGRGUxu9cWc2D3QE32UxRnTpvtJam11JLID8+5YbBJA3KNlNyF1runmM5HYe3Dd2UR86EkgV0/8I2+flhx0'
        b'RMfCONGwdpph3FOWMGEx3ouU9iqCmlLoSadNE8daj33mUJfC8pM8owmmSG9pMFGOhTwFQ2sctYrCRlftK3RZgynYYgX3HBKxgc6vAsdPb4RFX8EhzFWWw0URrTLfYx3M'
        b'SzPDSLcV9EVoO0P9Cf31VqRzFdOWcPQw0ZQHBBhjhAl3CRoWEkj5HNGkQ28KDmHYEx65i0hrmdR5h4gEJZg5h33RXp5R4RdJTp1UoSU0E88dVsBJNygJgYbTxjpA+sUt'
        b'LItWCsIRX6jQtA+8cB3bXT02WGDVHpzYEHkeyy2lmNxKdCiPlOgOfOCedoM1Mw9WI/7ViQ83irdDvaY35of4O1086uFIWF5qi3VJh0JxfgvLuKMrLSHFUOYSEYgRxQAD'
        b'jsgw2l1LB9kYsg8mcGaLEWFvI3ZfI6Qrh/FdrC+AuiyxyKF4/3U0aUkoLpxMoLspQ5IQKuVhVuOwGVG19muamao7CRKbiOQ8NMHCS9B+8ArMWmJDygmSafyJoPaugm3S'
        b'bGdFUjo4gFX2qonQoyUTvZMeaqPNTBBNrLcQuvq6MNUpBOdCcEqZMGsGi3yYe9bksApWGpzdICYYbyYmXkqIM5JOB163z1feD+4cwGZ/Au9mot73FJk+DsMGfnTipFZD'
        b'uTbm+Tgy+UeTxhu9tAl69+Loid1IQo3rBpZ4twU6zDYRjtbZQMs6Op2WJJZ6HgYT/gYE6M1S3vv0oVvPCrKCocicZF9bIoqb/Iz0iVxUR2KOPEyEJWbSZnNgOuAAMZap'
        b'MEbJS2STT1rCoNJBOuUKbNK9ROc0r4FdEevwjtyudAebBB1oOwhj7jcIrnqJAfZgkx7OJrvioAaJOxXES+9HEkNIVziWSNfYToNUbzmUDD2HxRY4emQbDNgpYGsyjqiF'
        b'X9CFPnW1BKhZh6VuETRQNtSayO71oCslaYOOZU5s6BFvf9A7Gu9sIdIwSFjUGrgFFx2JfjVAm4uDrYBQo5jwksRvol7VMKsYjgX7iUkTkJYcg/H18kKiBXcvnSfK10tX'
        b'Mkej5qmvO0O8vAy65SA3EvKtcNCUuEDhzatQfeg8MiN5lwCmLh7WJ4pyD/KjdhKm9etCpymheRMhxTip1K2B8nr78b4ONPgecot3IiY6AAM4KqZXbsGUoZYVqyMNfQ4w'
        b'JG1AyNQKi9vX6ZE8W7YbK29gJTuaolSYFMXvOEyfVtlA184zOE/cEuvVt9lsw/ZD0BjmT3BTiPWJxJ0W0s7h2D4bP8iJSSbCWGsmOAB9QWlawcF06jGRRFjLgmE8gSTo'
        b'KpLhyui0JqyJruZtsyKlcB4LEq3dwm2JDhRi8XVTOtxJJSFB3pASk47pIptCk9IyYM6L/tkNze6knnfAWLwz3jnD8cZpvG9zzg4adhHfJOXXyRanWQXDMcVQCxLmGgMI'
        b'ORZlg0liy9pCBHwiRSxi/S9OEckmTMomaGaotID3jYkUNxJwzlrhtC7Ju/5YoxB1DIa3Ycsxc6gSEZO7rcyesFWLIm3xwfUIZ2eSCHJc/awMMT89jmTsBex3oOufhA55'
        b'fHBANoYYz7AQO33w3vYMyCK9r26Ho6qiD9aHcp61UWbjz6QjbrkOtXCPWbS6Yd6b9kmY0sfsRSTw9kKfszY2XfPeedacdliHQzaYnYnlOGNAHLLwPHT4kcw1YyoTGbdX'
        b'F8adFQj7R+jBsr10uPkxhAYLqnj7AuSRYDBO7KXcAiv1ZWmfvfKmeOdGJImC+cFpkGtL3LkcbotwUlceW07rOuoSzIzsklbbgHNH/KBSxV6OKOc9zHIiqWaY0bX9eEdA'
        b'fLwOK/aohJ2EvHNuuw4lRyvggtqZ9J1E5Ek6t7tyEirisWavDynVTB6dsoq8QSBStBPG1a3dCI07deCeAsz6X4vZjQPbiXbdxRbIu4j30hQw/4QPoUYeaScDRHaqSHPZ'
        b'TAfesBHblBRE4TpYcjY66sIlS2x2UxGe0Kb3RqFKBqrVdQjlauButJKLsTnObmTWT7r5LHiwHu4y/12/wQbS/EqDj9iSFN++j86iE+5sMI2FKvethBjlpAAlpUDTPrqD'
        b'fBecsVEkOf4+SQatJ9J1sEvppjTtoNoRmjXlbxDOVdO/qmDRODbwGrRvJr0yR+OQF8zoQqvaQVulVLzlinkGl2Sx3xeqI6EdhgmQyr0DmMUU+1OYvYvu/T5R33HiEznY'
        b'Y4aFNy9tJkZNctBperbNkzZz6wzOppuRfAa9hDE1xKsLFQOCU84STnYA4ycklvYcoL0tZkDtRqwOI8l7JoGgZTRVl4BqOAMLMqGIKDnJHrf8aeaO4ynvkLh0gSDs4TIi'
        b'2DPLVMUZ4sNEw6KPGHqrbsNKQoIz267T1616ESHyutijd4iObXAb3fAi3omAEVnnQJpoluSkXqkDOKsPi9h/MJqlBufh7WRgXuDsszZQLYZ6XSLoD1JJsYcuEf3aB/fC'
        b'iOMM3CT6WEE4VUsDVylsxG5XoqfDdPylWH0DF+G+jRYWHYD7pti1zQNLYpiny4WZq0JP0gHl7SDKUqQkxqGw9QT609cMCdnnLbziCOZ6NPfS2qr3aGP91k1G2LLjBIkN'
        b'hB7HWA1PrUicUcLmw5uxV5k0yLzzkHMM5+1hWD6NiEwNyUB1RKC7BQT192SgzcAZGhRJVejdowqdDhbQZEkSQ56u7zoc2LpPRgYLTx3DIkW8dewkacf3zUjMKrDCCdV4'
        b'nDFXctsLXZZY42BtT4cyBc1iQv4eovj56YGGajBgQpdaT8JWtiGB+6iQhLPMqxYEcTXekKfIAcb8JSLii5d30H21YkEcnVofowQze0gAqQmPhO5DBNLMDF+DxTo4dYD0'
        b'm6oIKJSBrkhDGBDDmJ01zjI9HbNOERGbdk8lnv7QUobE624o3YU5JnQwY9rQlQEN6gQfhVuYQ1n6hsyBCF9WvNxGBetJgpBJZXJQjub+WFL7SLK/RUSiCvo0sem4ThqL'
        b'rPChk2uGexevbochU3jgCN1G0tC0mWSsFn8YvEyqzyh0m14iKYhY9wHruH1wz3VnAnZth0ZX6DPecwKnpImvNLhsJv22DSctiMsNMixp8tE4bklS9rAZLvptI9rW4B2o'
        b'cinDd30AAU4hZu13pzkat9puss8QkIxZeBkHjzpKWisQ1+k0xonLKwvwxPtypqiwrXiPqxmnD0NCVjMuJtpIxCfUTSlvPC12Y4alQwJmr9zDj1VH8NOsg6x0u0Ag3MOq'
        b'OwzzxcWg4HpSlB9LuhILhMfoHTtVbiTFWEUYEz+yjk1eo3WxL5yZM87jjJuXlEC4l74xy+BTt3oJZUZI6XyAJe70khVLiuvFKr4mVy9x/PtQavfIrGa0j8ZjsbcRdKft'
        b'hO6lWGJE73kJiKbnQw733XE6+k4CsVws8eDNa1U0UD1fSmjyNB1ePmsxITHJQaWfkZBbIwmH89LXk91caUBjARbq3eQb0E3d8CQwH1lhkyOEHDESOnKNibjUt7fjWWKc'
        b'wP7nsoExD8wOCYxE3Mc3A6TYx2kGokD3o0fS+NJDGMM9e/JF6UD3f8WrCFh4mSM3GpcrF6W7oUuQNE4UK/zE1YyaM176Dlp5EakXfn9AJkTUmer+p4VUOXmXLC15Nyf9'
        b'7c67vuWl/iD01Eex7R+LPp2wOnyxqbHgOx+n/8nqHy1WPl/c//zFusPvXbWSKb38h8/z/qNi2e1/7p6dyU/kPmu+Xjje/bnC0I91XIyOv6Ywsf9SyDszf//jUKDhR7pH'
        b'ypJSXgvd9Z/3Nq5z9z2UP3ZxqKV4IlA8pljXnrhu6EffG052OnLuM7WOd2/kvhppt8M2MbhlwPHljJcuf1t/sCcx5tzAsV/ZfbQ94ZV0R+2Bbae8eh1rx8Y9O7PdL3w3'
        b'7nhzyq2Uo597fGf8zrek69Lf7K8+YekUCdvrWvedUuyUHv2xd0dtQ5+1SVTT7Y3ftpyuuvOOX7D3JsO3y8s/17X+uejFj91Tjx0OSl/Ya7jf2+nAThe9Bpf3m+r83qwT'
        b'Hc72TK76INH9xT8TI7qwLcKlJNk54hvvh5YmaQ9aBVRfqb5+VePt321+872a0NGK7w0rpOVYnvPeXvPSmyV2V/8ufSHhjy/+64eNc5tEf5P528/XNV+u0n1b4ZXzvb+9'
        b'85uL65L6G7+wyPM0f9mmxUTG4pun8g1eK/m9n7515vDxW19g7zr3qPQLUzuvKuB3ql6at3gx+Jaz3oZ/bbry0xBxd6iT6MD6D+9u3/z+n0x+s6m2avLHlyd7P5MpDWr9'
        b'Yu7idee3vrBUsj74x1079nz3tZd/OTr92u9rbjb1WXpFKLz2QPX1NKeF5oNJMlMj+jnRKn/99WTaq+nOp+deVPTveUdt5OUvIvy2/ug7n53+YmF6eCI37P2An1wDh39Y'
        b'vh9t/nbnr6z2VabbFIW9HLHN+LDB9px1I4m1fpm1h/P2j4SIWt6AA1c3bnnjWxs/Scg6ZvD7f376wksvJjzotfvinmU8vPNhW0DhO+u/ePHIqwO/+tnofM+/cx/+5N3p'
        b'lzL/8s1N+P29//mwKLP4TNi//7Dz3zo3Q05G7I79j/T6c6ecYqu3Wxkp8Olv0zBxg1kxStx5glLuvI3LniKOuf1RuGsd4dRy1DuJPXlcxljgll1rdHsodeeT4E4E8SlW'
        b'5cSB5xUTleWVicmXqCamKBHFn8bbeFckMEgXy+FQIlc+2gI7/JYfS8XZ1ARlGcF6bNe1FxH9qIFebjjRVo2kq0oJKXhXFYqhVFVOWQHHVa9KC7DzsJGKmIhgTTAXjRtO'
        b'YmrZWo9uPQVlS8N7iGU4a3ATlyNg5HFSkR6CLCd+SDnslzJ3OJhswXwAWIsVSVAml0DrSyI+V7Q0HqMvK0bEGRl4qI7dyTvZ5kmWlsWplO3Etteq68KKusDsjifb2ln+'
        b'/xtp+v/7H0YG/19zVxsbxXGG9+s+7LOP43BcY1ogIBKf72xjHIqhJDJgOznOZ5OQgMNHN+e7PXvhvLe3twd2wMUBAgHncEpSSkoMJCZACHaNMRDFBZKZlkr9gaK0VdGo'
        b'SiuhSFFFo7RKW+GopPPO2gZVyo9WlahW9+zezuzX7OzOM6t5npe9X/9fwIpILsuJZCQmy2wg9kcUOL8gCPwj/MyvBQH0a17BKUq8U7QLdBLdNq/Xm+OZ6XF47N7cgmmS'
        b'UBAsmkPz7+CqwO6kGgZmi5IAyzN30H3xRfNqYZ0s8EutYdtRgV8C87WTa+xFzxYv84hu0esR+MAObq7A11opc4VSwUd/ford3FmJ5RYCbA1M3dxJCYZaf2WfNDUHIUfR'
        b'PT/j6cmhzqLxR7jwu8O/F9z/SnHfKiNvFQYbeg1FBPFj0yAN4n6nf3MwLniNPh6cjnooie+mBLkXgqihfajXwbmni9+hfLRHrevKSunpPMcdSn6xMBtsxDWeuncfbQom'
        b'frnlIafzwcocZ3/RgQ+Fc5eG/3S99Ejt0Iqxd9bvdqXcB5aNVp75xVdvr706WrgwOHZ8K9n/9t/mVX/y8/WjF82L0m+zmfeinxnxz1KDaki+fevd7kcfMP7w+yULnqoc'
        b'LY2c+vOW6gW3jJYbNz+e/+nyX//o9V+9/vSxr+/8NfbmSnf475nBas/I0YHVlx3G8T0B6fLHLbc+MkbGCn/zcmfTkUXrms9fW3PtzsgH6w/dyV5xfdocrl7Y98Tnpzd+'
        b'fvGfvn/UnJ7f/YGnsH6o8prk3tBwbm9Xxxepbm6vM7U7+sZs5Lvumfvh4nJ9n9/Ud5Vrqb3bvnxlDhaNL//y0sNL+2sWXx28ueR23o1PblQUXN/Bv5XcUJN4xDeL6S+W'
        b'JdAhoLBNTUyj64CwqVddaFjAp/FPTdZkzcHHp4aayvA5yEXnL+I+gZuKfyZSgvkCusSarFbcj4foHRnG7I6AkQB8+aF3xCvOrMR9rFEMFM4BG9awA+1UObskOGfTxgcS'
        b'1tTRbkRPBeWpuK9oNYf7a/BBJh5Zt6jMjw+UgMz4ZZ7LoWz3SrlAme3JVZYC/cRz3IQfmNTIP4xeQkOU5XZbYufLKFtMWfOmYCBYNp7JjfeLjfBlwjJqe3EqOjvp0obP'
        b'P4aOidvZttVh3dpvOIizviB6YavEefGrInpfQwfZtuGu9tDKQOPCKp5zbIIBL4K9Ic5kbTFKjS+EFlTRLZkLWGeNjZvyoPg99GP0piV5OYUu4DOQIxiGDLQ3fwVObVCs'
        b'xG/4WIu5CB9txj0Qrq+X8uQn+Rlr0Sh+dQVLa0aH4VNrNhzgOKmSR5edtPvQW8K07UJqlr8MZ8H2r53HQxJ6D/WiUUYD8NkiGKKSpYwEDhqmly1xM7okumYX2okOV1hO'
        b'a/vy0JkQnBdIyGmZo2OyyyfQHvfuKeMGgq3z0vek/wCdzQ0KaGhjOZPw48O5+JALD0/BF9JoH76kx9AlPJKi/CSf4749V3JkXNZxhvA7q5lEyQ8747igz4V+IuC38EDc'
        b'0hUOLJ12r48dPrwcHSmuMJlT9msCPhVCAyX0voIzGfNqbAqibEVjmc/OPU67jf11ju0rIqxMVqITThc93kgt7gdH8B9y+OS2pKWW70PvL4ex1OGGJhvYD3K27Tw+Ue+0'
        b'zBDhO/kuSC4DH/DUOBErztAy24D2zEA9VviuV2AMOy32/WCY2CBwOUG08yEB9dBu9Wusms6iXMS/siwQLivnaTXK5j0g5sK3fcuzrQ8NF4XojQmV0+3ps+P7Ftpj56ZV'
        b'ifgoOoGPWcU1QLteB/1PBEpBEUqLfTE+6gJryMEGjT1Bq6rReT/02ehT2BeitwEdrJmIjlRy/9/0/6P2ovA+0JO7oY11aJjcTqaqd7KpgNmuOceFmyAFA84BS97xUMY0'
        b'p6j957KyiWm+pa1izKGUiAlFM1TaqBGbmdETCpESatokUkyNUkzqikbEtGkQW0unqaSJ1JJMJoioaiaxxSnDojMjorUqxKZqesYkYrTNIGLSiBF7XE2YCv3THtGJ+Lyq'
        b'E1skHVVVIrYpHTQL3X2umla1tBnRogqx65mWhBoleXWWyDEc2Uw3ztMNxTTVeKfc0Z4gzoZkdHO9Sk8yp6Xqu4oGJlYkX00nZVNtV+iO2nUi1a+qrSf5esRIKzJNAgk4'
        b'mdqejC1eZEUFkWNqq2oSRyQaVXQzTfLZhclmkhJGrZWIzeEG4kq3qXFTVgwjaZD8jBZti6iaEpOVjijJkeW0QotKlolbS8rJlngmHWXRnEjOxB96ORkNXKzucjKrvEuM'
        b'zcDadIB2gAxABwBIBg2IeWNoABsA1gOYABGAZqakBfg+QCvAcwAbAVSAJMAzAGsBYgBwaKMT4HkmpQN4FqAFIAWQANgEAITZ2AKwDmAN2zOo7bbC0jbmmjepJISKlDPJ'
        b'r26v+0Z+xXKOOeO03ijRtnLikeXx5XGaPlY8/n+2HoluBkMzkLxCmhJr9DmZJpA4ZDmSSMiyVYGZahBixhG7FdLVuAlruiZo8b9FiibOpbQWZBLKYxBmLg3hpyXgC//9'
        b'g/RMAXMx/Bf6GxSy'
    ))))
