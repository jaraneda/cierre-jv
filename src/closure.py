import pandas
import helpers
from datetime import datetime

def get_devolutions(closure_df):
    '''Creates and returns a new DF containing devolutions'''

    df = helpers.rename_closure_cols(closure_df)

    # Filter devolutions
    devolutions = df.query('estado == "Devoluciones a clientes"').copy()
    # Get order_id
    devolutions["order_id"] = [v[22:v.find(' ',22)] if "Devolución de pedido" in v else v[36:]
                               for v in devolutions["order_id"]]

    devolutions = helpers.process_charges_cols(devolutions)
    devolutions = devolutions.set_index("order_id")

    return devolutions

def get_tips(closure_df):
    '''Creates and returns a new DF containing tips'''

    df = helpers.rename_closure_cols(closure_df)

    # Filter tips
    tips_df = df.query('estado == "Propina para repartidores"').copy()
    tips_df['order_id'] = [value[1:].replace("-", "") for value in tips_df["Pedido"]]
    tips_df = helpers.process_charges_cols(tips_df)

    tips_df = tips_df.set_index("order_id")

    return tips_df

def get_payments(closure_df):
    '''Creates and returns a new DF with the Payments (Abonos) data'''
    df = closure_df.query(
        'Descripción.str.contains("Abono ")',
        engine='python'
    )
    dates, times = helpers.get_dates_and_times(df["Fecha"])
    order_ids = helpers.get_order_ids_from_description(df["Descripción"])

    empty_list = ["" for i in order_ids]
    df = pandas.DataFrame({
        "order_id": order_ids,
        "restaurant_id": empty_list,
        "ciudad": empty_list,
        "restaurant_name": helpers.replace_store_name(df["Local"], dates),
        "fecha": dates,
        "hora": times,
        "estado": df["Descripción"],
        "metodo de pago": empty_list,
        "cooking time": empty_list,
        "valor": empty_list,
        "costo envío": empty_list,
        "descuento asumido partner": empty_list,
        "descuento asumido peya": empty_list,
        "pago": df["Monto"]
    })
    df = df.set_index("order_id")

    return df

def get_orders(df):
    '''Creates and returns a new DF with the Orders data'''

    df = df.query('Pago != "Paga en el local"')
    df = df.rename(
        {
            "ID": "order_id",
            "Pago": "metodo de pago",
            "Monto en productos": "valor",
            "Estado del pago": "estado",
            "Precio despacho": "costo envío"
        },
        axis="columns"
    )
    df = helpers.filter_older_orders_out(df)

    # TODO: CALCULAR VALOR A PAGAR: PAGO CON PROPINA - PROPINAS - DEVOLUCIONES
    # En la función process_payouts_and_tips se ejecuta PAGO CON PROPINA - PROPINAS
    payment_methods = []

    for label, values in df.items():
        if label == "metodo de pago":
            for v in values:
                if v == "Webpay: Débito":
                    payment_methods.append("dc")
                elif v in ("Tarjeta de crédito", "Webpay: Tarjeta de crédito"):
                    payment_methods.append("cc")
                else:
                    payment_methods.append(v)

    df["order_id"] = [v[1:].replace("-", "") for v in df["order_id"]]
    df["estado"] = ["CONFIRMED" for i in df["estado"]]
    df["metodo de pago"] = payment_methods

    df = df.set_index("order_id")

    return df

def get_payouts(payouts):
    '''Creates and returns a new DF with the Payments (Abonos) data'''
    df = payouts
    dates, times = helpers.get_dates_and_times(df["Fecha"])
    order_ids = helpers.get_order_ids_from_description(df["Descripción"])

    df = pandas.DataFrame({
        "order_id": [value.replace("-", "") for value in order_ids],
        "restaurant_name": helpers.replace_store_name(df["Local"], dates),
        "fecha": dates,
        "hora": times,
        #"estado": df["Descripción"],
         "pago": df["Monto"]
    })

    df = df.set_index("order_id")
    return df
