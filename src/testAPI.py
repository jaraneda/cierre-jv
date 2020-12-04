import getjusto
from settings import API_KEY

def getPaymentType(type):
    # TODO ¿expose API?
    paymentType = {
        "webpayOneClickTest": 'Webpay One Click Test',
        "webpayOneClick": 'Webpay One Click',
        "mercadoPagoCard": 'Tarjeta de crédito',
        "stripeMX": 'Tarjeta de Crédito o Débito',
        "kushkiPE": 'Tarjeta de Crédito o Débito',
        "kushkiCL": 'Tarjeta de Crédito',
        "kushkiAsyncCL": 'Tarjeta de Débito',
        "webpay": 'Webpay Rocoto',
        "orion": 'Webpay QVO',
        "webpayTest": 'Webpay Test',
        "webpayOrioneat": 'Webpay',
        "webpayCurry": 'Webpay Curry',
        "transbank": 'Redcompra',
        "cash": 'Efectivo',
        "inStore": 'Paga en el local',
        "khipu": 'Transferencia',
        "amipass": 'Amipass',
        "sodexo": 'Sodexo',
        "mach": 'MACH',
        "chek": 'CHEK',
        "externalPay": 'Pago externo',
        "kushkiCL": 'Tarjeta de crédito',
        "kushkiAsyncCL": 'Tarjeta de débito/crédito',
        "kushkiWebpay": 'Webpay',
        "kushkiPE": 'Tarjeta de débito/crédito'
    }

    return paymentType[type]

def getPaymentStatus(status):
    paymentStatus = {
        "pending": 'Pendiente',
        "done": 'Listo',
        "error": 'Cancelado/Error'
      }

    return paymentStatus[status]

def getOrdersFromApi():
    fromDate =  "2020-11-16T03:00:00.000Z"
    toDate =  "2020-11-23T03:00:00.000Z"
    justo = getjusto.Api(API_KEY)

    response = justo.orders(fromDate, toDate)
    response = response.json()
        
    items = response['data']['items']

    # columns used: 
    # ID = fullCode
    # Pago = paymentType (decode) 
    # Estado del pago = paymentStatus
    # Monto en productos = order.totalPrice - order.deliveryFee
    # Precio despacho =  deliveryFee
     
    item = items[0]
    obj = {
        "ID": item['fullCode'],
        "Pago": getPaymentType(item['paymentType']),
        "Pago": getPaymentType(item['paymentType']),
        "createdAt": item['createdAt'],
        "Monto en productos": item['totalPrice'] - item['deliveryFee'],
        "Precio despacho": item['deliveryFee'],
    }
    print(obj)



if __name__ == "__main__":
    getOrdersFromApi()