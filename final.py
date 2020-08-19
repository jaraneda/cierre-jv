#!/usr/bin/env python3

from datetime import datetime
import pandas as pd


def get_dates_and_times(column):
    '''Returns a tuple with dates and times extracted from a DF column'''

    dates = []
    times = []
    for value in column:
        dta = datetime.fromisoformat(value)
        dates.append(dta.date().strftime("%Y-%m-%d"))
        times.append(dta.time())

    return (dates, times)


def get_first_and_last_id(df):
    '''Returns a tuple with the first and last order_id'''

    first = df["Descripción"][0][7:]
    last = df["Descripción"][len(df) - 1][7:]
    return (first, last)


def rename_closure_cols(closure_df):
    '''Returns a new closure DF with renamed columns'''

    return closure_df.rename(
        {
            "Descripción": "order_id",
            "Total": "pago",
            "Local": "restaurant_name",
            "Fecha": "fecha",
            "Tipo": "estado"
        },
        axis="columns"
    )


def add_empty_cols(df):
    df["restaurant_id"] = ""
    df["ciudad"] = ""
    df["cooking time"] = ""
    df["descuento asumido partner"] = ""
    df["descuento asumido peya"] = ""
    return df


def reorder_final_df(df):
    return df[
        [
            "order_id",
            "restaurant_id",
            "ciudad",
            "restaurant_name",
            "fecha",
            "hora",
            "estado",
            "metodo de pago",
            "cooking time",
            "valor",
            "costo envío",
            "descuento asumido partner",
            "descuento asumido peya",
            "pago"
        ]
    ]


def get_devolutions(closure_df):
    '''Creates and returns a new DF containing devolutions'''

    df = rename_closure_cols(closure_df)

    # Filter devolutions
    devolutions = df.query(
        'estado == "Devoluciones a clientes" or estado == "Propina para repartidores"')

    # Get order_id
    devolutions["order_id"] = [v[22:] if "Devolución de pedido" in v else v[36:]
                               for v in devolutions["order_id"]]
    # Make devolution amounts negative:
    devolutions["pago"] = [int(v) * -1 for v in devolutions["pago"]]
    dates, times = get_dates_and_times(devolutions["fecha"])
    devolutions["fecha"] = dates
    devolutions["hora"] = times
    devolutions["costo envío"] = ""
    devolutions["metodo de pago"] = ""
    devolutions["valor"] = ""

    devolutions = add_empty_cols(devolutions)
    devolutions = reorder_final_df(devolutions)

    devolutions = devolutions.set_index("order_id")
    return devolutions


def get_payments(closure_df):
    '''Creates and returns a new DF with the Payments (Abonos) data'''
    df = closure_df.query(
        'Descripción.str.contains("Abono JUSTO")',
        engine='python'
    )
    dates, times = get_dates_and_times(df["Fecha"])
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
    store_names = []

    for label, values in df.items():
        if label == "fecha":
            dates, times = get_dates_and_times(values)

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
            for name in values:
                if "Regiones" in name:
                    store_names.append("Alonso de Cordova")
                elif "Chicureo" in name or "Food Truck Maipú" in name:
                    store_names.append("Rosario Norte")
                else:
                    store_names.append(name)

    # Check that all IDs in payments are included in orders
    first_id = first_id.replace("#", "")
    last_id = last_id.replace("#", "")
    print("First:", first_id, "LAST:", last_id)
    if last_id not in df["order_id"]:
        print("Faltan ordenes en el archivo de pedidos:", last_id)

    df["order_id"] = [v[1:].replace("-", "") for v in df["order_id"]]
    df["estado"] = ["CONFIRMED" for i in df["estado"]]
    df["fecha"] = dates
    df["hora"] = times
    df["metodo de pago"] = payment_methods
    df["restaurant_name"] = store_names

    df = add_empty_cols(df)
    df = reorder_final_df(df)

    df = df.set_index("order_id")
    return df


# def get_tips(df):
#     tips = df.query('propina != 0')
#     # tips["tip"] = [i * -1 for i in tips["tip"]]
#     del tips["pago"]
#     tips = tips.rename({"tip": "pago"})
#     return tips


def main():
    '''Reads and process Excel and CSV file from Justo app to Excel for JV'''

    # Read Excel or CSV file for charges file
    charges_df = pd.read_excel(
        "Cierre Juan Valdez.xlsx", sheet_name="Cobros", parse_dates=True,
        usecols=["Descripción", "Tipo", "Total", "Local", "Fecha"])

    range_sheet = pd.read_excel(
        "Cierre Juan Valdez.xlsx", sheet_name="Pagos", parse_dates=True,
        usecols=["Descripción", "Monto", "Local", "Fecha"])
    # Get the first and last order id from payments sheet
    first_id, last_id = get_first_and_last_id(range_sheet)

    print("CHARGES COUNT:", len(charges_df))

    # Read Excel or CSV file for orders file
    cols_to_use = [
        "ID",
        "Local",
        "Pago",
        "Estado del pago",
        "Fecha del pedido",
        "Monto en productos",
        "Total con propina",
        "Precio despacho"
    ]

    orders_df = pd.read_csv(
        "Pedidos.csv",
        encoding="utf-8",
        usecols=cols_to_use,
        parse_dates=True,
        infer_datetime_format=True
    )

    payments = get_payments(range_sheet)

    # orders_df = pd.read_excel(
    #     "pedidos.xlsx",
    #     encoding="utf-8",
    #     usecols=cols_to_use,
    #     parse_dates=True,
    #     infer_datetime_format=True
    # )

    devolutions = get_devolutions(charges_df)
    print("DEVOLUTIONS COUNT:", len(devolutions.index))

    # Filter orders to only include payed orders
    print("ORIGINAL ORDERS COUNT:", len(orders_df.index))
    orders_df = orders_df[orders_df['ID'].between(first_id, last_id)]
    print("FILTERED ORDERS COUNT:", len(orders_df.index))

    orders = get_orders(orders_df, first_id, last_id)
    print("FINAL ORDERS COUNT:", len(orders.index))

    merged_dfs = pd.concat([orders, devolutions, payments])
    merged_dfs.to_excel("cierre-JV.xlsx")


if __name__ == "__main__":
    main()
