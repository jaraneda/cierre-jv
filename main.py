#!/usr/bin/env python3
import pandas as pd
from helpers import get_first_and_last_id
from closure import get_devolutions, get_orders, get_payments


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

    # Filter orders to only include payed orders
    orders_df = orders_df[orders_df['ID'].between(first_id, last_id)]

    orders = get_orders(orders_df, first_id, last_id)

    merged_dfs = pd.concat([orders, devolutions, payments])
    merged_dfs.to_excel("cierre-JV.xlsx")


if __name__ == "__main__":
    main()
