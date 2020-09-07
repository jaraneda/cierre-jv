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
    devolutions["restaurant_name"] = helpers.replace_store_name(
        devolutions["restaurant_name"])

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
        map(lambda descripcion: descripcion[35:], df["Descripción"])
    )

    empty_list = ["" for i in order_ids]
    df = pd.DataFrame({
        "order_id": order_ids,
        "restaurant_id": empty_list,
        "ciudad": empty_list,
        "restaurant_name": empty_list,
        "fecha": dates,
        "hora": times,
        "estado": df["Descripción"],
        "metodo de pago": empty_list,
        "cooking_time": empty_list,
        "valor": empty_list,
        "costo_envío": empty_list,
        "descuento asumido partner": empty_list,
        "descuento asumido peya": empty_list,
        "pago": df["Monto"]
    })
    df = df.set_index("order_id")

    return df


def get_orders(df, first_id, last_id):
    '''Creates and returns a new DF with the Orders data'''

    df = df.query('Pago != "Paga en el local"')
    df = df.rename(
        {
            "ID": "order_id",
            "Local": "restaurant_name",
            "Pago": "metodo de pago",
            "Monto en productos": "valor",
            "Fecha del pedido": "fecha",
            "Estado del pago": "estado",
            "Total con propina": "pago",
            "Precio despacho": "costo envío"
        },
        axis="columns"
    )

    # CALCULAR VALOR A PAGAR: PAGO CON PROPINA - PROPINAS - DEVOLUCIONES
    dates = []
    times = []
    payment_methods = []

    for label, values in df.items():
        if label == "fecha":
            dates, times = helpers.get_dates_and_times(values)

        if label == "metodo de pago":
            for v in values:
                if v == "Webpay: Débito":
                    payment_methods.append("dc")
                elif v in ("Tarjeta de crédito", "Webpay: Tarjeta de crédito"):
                    payment_methods.append("cc")
                else:
                    payment_methods.append(v)
        # Change store names from Justo to JV names
        elif label == "restaurant_name":
            store_names = helpers.replace_store_name(df["restaurant_name"])

    # Check that all IDs in payments are included in orders
    # first_id = first_id.replace("#", "")
    # last_id = last_id.replace("#", "")
    # print("First:", first_id, "LAST:", last_id)
    # if last_id not in df["order_id"]:
    #     print("Faltan ordenes en el archivo de pedidos:", last_id)

    df["order_id"] = [v[1:].replace("-", "") for v in df["order_id"]]
    df["estado"] = ["CONFIRMED" for i in df["estado"]]
    df["fecha"] = dates
    df["hora"] = times
    df["metodo de pago"] = payment_methods
    df["restaurant_name"] = store_names

    df = helpers.add_empty_cols(df)
    df = helpers.reorder_final_df(df)

    df = df.set_index("order_id")
    return df
