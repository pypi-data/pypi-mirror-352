from typing import List


class GenericResponse:
    def __init__(self, identificador, identificador2, sucesso, mensagem):
        self.identificador: str = identificador
        self.identificador2: str = identificador2
        self.sucesso: int = sucesso
        self.mensagem: str = mensagem
        # self.protocol: str = Protocolo


class PriceResponse:
    def __init__(self, erp_code, sucesso, mensagem):
        self.erp_code = erp_code
        self.sucesso = sucesso
        self.mensagem = mensagem


class StockResponse:
    def __init__(self, sku_seller_id, success, message):
        self.sku_seller_id: str = sku_seller_id
        self.success: str = success
        self.message: str = message


class InvoiceResponse:
    def __init__(self, code: int, message: str):
        self.status = code
        self.message = message


class SentResponse:
    def __init__(self, status_code: int, text: str):
        self.status = status_code
        self.message = text


class DeliverResponse:
    def __init__(self, status_code: int, text: str):
        self.status = status_code
        self.message = text


class ProductResponse:
    def __init__(self, product_code, category_code, message, success, sku_results):
        self.identificador = product_code
        self.identificador2 = category_code
        self.message = message
        self.sucesso = success
        self.sku_results = sku_results


class PhotoResponse:
    def __init__(self, product_code, photo, message, success):
        self.identificador = product_code
        self.identificador2 = photo
        self.message = message
        self.sucesso = success


class CatalogoResponse:
    def __init__(self, message: str, status: int = 3, codigo_erp: str = '', protocolo: str = '',
                 loja: str = '', Identifiers2: str = ' ') -> None:
        self.codigo_erp = codigo_erp
        self.status = status
        self.message = message
        self.protocolo = protocolo
        self.loja = loja
        self.identifiers2 = Identifiers2


class OkvendasResponse:
    def __init__(self, Identifiers: List[str], Status: int, Message: str, Protocolo: str, Identifiers2: str = ' '):
        self.Identifiers = Identifiers
        self.Status = Status
        self.Message = Message
        self.Protocolo = Protocolo
        self.Identifiers2 = Identifiers2


class ListaPrecoResponse:
    def __init__(self, identifiers, status, message, protocolo, identifiers2=' '):
        self.identifiers: List[str] = identifiers
        self.status: int = status
        self.message: str = message
        self.protocol: str = protocolo
        self.identifiers2 = identifiers2


class ProductTaxResponse:
    def __init__(self, Identifiers: List[str], Status: int, Message: str, Protocolo: str, Identifiers2: str = ' '):
        self.identifiers: List[str] = Identifiers
        self.status: int = Status
        self.message: str = Message
        self.protocolo: str = Protocolo
        self.identifiers2 = Identifiers2


class RepresentativeResponse:
    def __init__(self, Identifiers, Status, Message, Protocolo, Identifiers2=' '):
        self.identifiers = Identifiers
        self.status = Status
        self.message = Message
        self.protocolo = Protocolo
        self.identifiers2 = Identifiers2


class ClientResponse:
    def __init__(self, Identifiers: List[str], Status: int, Message: str, Protocolo='', Identifiers2=' '):
        self.identifiers: List[str] = Identifiers
        self.status: int = Status
        self.message: str = Message
        self.identifiers2 = Identifiers2


class OkvendasEstoqueResponse:
    def __init__(self, codigo_erp, Status, Message, protocolo, loja, Identifiers2=' '):
        self.codigo_erp = codigo_erp
        self.Status = Status
        self.Message = Message
        self.protocolo = protocolo
        self.loja = loja
        self.identifiers2 = Identifiers2


class SbyResponse:
    def __init__(self, identificador: str, identificador2: str, sucesso: str, mensagem: str):
        self.identificador = identificador
        self.identificador2 = identificador2
        self.sucesso = sucesso
        self.mensagem = mensagem


class SbyResponseError:
    def __init__(self, status: int, message: str, statusMessage: str, objectMessage: None, notificacao: None,
                 sucesso: bool):
        self.status = status
        self.message = message
        self.statusMessage = statusMessage
        self.objectMessage = objectMessage
        self.notificacao = notificacao
        self.sucesso = sucesso
        self.identificador = None
