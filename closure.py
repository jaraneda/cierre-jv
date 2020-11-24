import pandas as pd
import helpers


def get_devolutions(closure_df):
    '''Creates and returns a new DF containing devolutions'''

    df = helpers.rename_closure_cols(closure_df)

    # Filter devolutions
    devolutions = df.query(
        'estado == "Devoluciones a clientes" or estado == "Propina para repartidores"')

    # Get order_id
    devolutions["order_id"] = [v[22:]
                               if "Devolución de pedido" in v else v[36:]
                               for v in devolutions["order_id"]]
    # Make devolution amounts negative:
    devolutions["pago"] = [int(v) * -1 for v in devolutions["pago"]]
    dates, times = helpers.get_dates_and_times(devolutions["fecha"])
    devolutions["fecha"] = dates
    devolutions["hora"] = times
    devolutions["costo envío"] = ""
    devolutions["metodo de pago"] = ""
    devolutions["valor"] = ""
    devolutions["restaurant_name"] = helpers.replace_store_name(devolutions["restaurant_name"])

    devolutions = helpers.add_empty_cols(devolutions)
    devolutions = helpers.reorder_final_df(devolutions)

    devolutions = devolutions.set_index("order_id")
    return devolutions


def get_payments(closure_df):
    '''Creates and returns a new DF with the Payments (Abonos) data'''
    df = closure_df.query(
        'Descripción.str.contains("Abono ")',
        engine='python'
    )
    dates, times = helpers.get_dates_and_times(df["Fecha"])
    order_ids = list(
        map(lambda descripcion: descripcion.split("#")[1], df["Descripción"])
    )

    empty_list = ["" for i in order_ids]
    df = pd.DataFrame({
        "order_id": order_ids,
        "restaurant_id": empty_list,
        "ciudad": empty_list,
        "restaurant_name": df["Local"],
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
    
    # CALCULAR VALOR A PAGAR: PAGO CON PROPINA - PROPINAS - DEVOLUCIONES
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
    order_ids = list(
        map(lambda descripcion: descripcion.split("#")[1], df["Descripción"])
    )

    df = pd.DataFrame({
        "order_id": [value.replace("-", "") for value in order_ids],
        "restaurant_name": df["Local"],
        "fecha": dates,
        "hora": times,
        #"estado": df["Descripción"],
        "pago": df["Monto"]
    })
    df = df.set_index("order_id")

    return df
