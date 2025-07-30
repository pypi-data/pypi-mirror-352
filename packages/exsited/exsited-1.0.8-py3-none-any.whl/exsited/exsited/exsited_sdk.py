from exsited.exsited.account.account import Account
from exsited.exsited.auth.dto.token_dto import RequestTokenDTO
from exsited.exsited.credit_note.credit_note import CreditNote
from exsited.exsited.gift_certificates.gift_certificates import GiftCertificates
from exsited.exsited.invoice.invoice import Invoice
from exsited.exsited.order.order import Order
from exsited.exsited.purchase_order.purchase_order import PurchaseOrder
from exsited.exsited.refund.refund import Refund
from exsited.exsited.return_merchandise_authorisations.return_merchandise_authorisations import \
    ReturnMerchandiseAuthorisations
from exsited.exsited.setting.setting import Setting
from exsited.exsited.payment.payment import Payment
from exsited.exsited.express.express import Express
from exsited.exsited.purchase_payments.purchase_payments import PurchasePayments


class ExsitedSDK:
    _request_token_dto: RequestTokenDTO = None
    account: Account = None
    order: Order = None
    invoice: Invoice = None
    setting: Setting = None
    payment: Payment = None
    refund: Refund = None
    purchase_order: PurchaseOrder = None
    gift_certificates: GiftCertificates = None
    credit_note: CreditNote = None
    return_merchandise_authorisations: ReturnMerchandiseAuthorisations = None
    purchase_payments: PurchasePayments = None
    express: Express = None

    def __init__(self, exsited_url: str = None, grant_type: str = None, client_id: str = None,
                 client_secret: str = None, redirect_uri: str = None):
        if grant_type and client_id and client_secret and redirect_uri:
            self._request_token_dto = RequestTokenDTO(
                grantType=grant_type,
                clientId=client_id,
                clientSecret=client_secret,
                redirectUri=redirect_uri,
                exsitedUrl=exsited_url,
            )
            self._init_endpoints()

    def _init_endpoints(self):
        self.account = Account(request_token_dto=self._request_token_dto)
        self.order = Order(request_token_dto=self._request_token_dto)
        self.invoice = Invoice(request_token_dto=self._request_token_dto)
        self.setting = Setting(request_token_dto=self._request_token_dto)
        self.payment = Payment(request_token_dto=self._request_token_dto)
        self.refund = Refund(request_token_dto=self._request_token_dto)
        self.purchase_order = PurchaseOrder(request_token_dto=self._request_token_dto)
        self.gift_certificates = GiftCertificates(request_token_dto=self._request_token_dto)
        self.credit_note = CreditNote(request_token_dto=self._request_token_dto)
        self.return_merchandise_authorisations = ReturnMerchandiseAuthorisations(request_token_dto=self._request_token_dto)
        self.express = Express(request_token_dto=self._request_token_dto)
        self.purchase_payments = PurchasePayments(request_token_dto=self._request_token_dto)


    def init_sdk(self, request_token_dto: RequestTokenDTO) -> 'ExsitedSDK':
        self._request_token_dto = request_token_dto
        self._init_endpoints()
        return self
