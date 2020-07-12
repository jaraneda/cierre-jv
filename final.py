#!/usr/bin/env python3

from datetime import datetime
import pandas as pd


def get_dates_and_times(values):
    dates = []
    times = []
    for v in values:
        dt = datetime.fromisoformat(v)
        dates.append(dt.date().strftime("%Y-%m-%d"))
        times.append(dt.time())

    return (dates, times)


def get_first_and_last_id(df):
    first = df["Descripción"][0][7:]
    last = df["Descripción"][len(df) - 1][7:]
    return (first, last)


def get_devolutions(df):
    df = df.rename(
        {
            "Descripción": "order_id",
            "Total": "pago",
            "Local": "restaurant_name",
            "Fecha": "fecha",
            "Tipo": "estado"
        },
        axis="columns"
    )

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
    devolutions["restaurant_id"] = ""
    devolutions["ciudad"] = ""
    devolutions["cooking time"] = ""
    devolutions["costo envío"] = ""
    devolutions["metodo de pago"] = ""
    devolutions["valor"] = ""
    devolutions["descuento asumido partner"] = ""
    devolutions["descuento asumido peya"] = ""

    # Reorder columns
    devolutions = devolutions[
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
            "descuento asumido peya", "pago"
        ]
    ]

    devolutions = devolutions.set_index("order_id")
    return devolutions


def get_orders(df):
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
            dates, times = get_dates_and_times(values)

        if label == "metodo de pago":
            for v in values:
                if v == "Webpay: Débito":
                    payment_methods.append("dc")
                elif v == "Tarjeta de crédito" or v == "Webpay: Tarjeta de crédito":
                    payment_methods.append("cc")
                else:
                    payment_methods.append(v)

    df["order_id"] = [v[1:].replace("-", "") for v in df["order_id"]]
    df["estado"] = ["CONFIRMED" for i in df["estado"]]
    df["fecha"] = dates
    df["hora"] = times
    df["restaurant_id"] = ""
    df["ciudad"] = ""
    df["cooking time"] = ""
    df["descuento asumido partner"] = ""
    df["descuento asumido peya"] = ""
    df["metodo de pago"] = payment_methods

    df = df[
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

    df = df.set_index("order_id")
    return df


# def get_tips(df):
#     tips = df.query('propina != 0')
#     # tips["tip"] = [i * -1 for i in tips["tip"]]
#     del tips["pago"]
#     tips = tips.rename({"tip": "pago"})
#     return tips


def main():

    # Read Excel or CSV file for charges file
    charges_df = pd.read_excel(
        "cierre.xlsx", sheet_name="Cobros", parse_dates=True,
        usecols=["Descripción", "Tipo", "Total", "Local", "Fecha"])
    range_sheet = pd.read_excel(
        "cierre.xlsx", sheet_name="Pagos", parse_dates=True,
        usecols=["Descripción"])
    # Get the first and last order id from payments sheet
    first, last = get_first_and_last_id(range_sheet)

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
        "pedidos.csv",
        encoding="utf-8",
        usecols=cols_to_use,
        parse_dates=True,
        infer_datetime_format=True
    )

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
    orders_df = orders_df[orders_df['ID'].between(first, last)]
    print("FILTERED ORDERS COUNT:", len(orders_df.index))

    orders = get_orders(orders_df)
    print("FINAL ORDERS COUNT:", len(orders.index))

    merged_dfs = pd.concat([orders, devolutions])
    merged_dfs.to_excel("cierre-JV.xlsx")


if __name__ == "__main__":
    main()
