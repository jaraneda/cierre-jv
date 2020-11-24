#!/usr/bin/env python3
import pandas as pd
from helpers import get_first_and_last_id, reorder_final_df, existsFile
from closure import get_devolutions, get_orders, get_payments, get_orders, get_payouts


def main():
    '''Reads and process Excel and CSV file from Justo app to Excel for JV'''

    ordersFilename = 'Pedidos.csv'
    payoutsFilename = 'Cierre Juan Valdez.xlsx'
    
    if not existsFile(ordersFilename):
        print('No existe el archivo ' + ordersFilename)
        return False
          
    if not existsFile(payoutsFilename):
        print('No existe el archivo ' + payoutsFilename)
        return False

    # Read Excel or CSV file for charges file
    charges_df = pd.read_excel(
        payoutsFilename, sheet_name="Cobros", parse_dates=True,
        usecols=["Descripción", "Tipo", "Total", "Local", "Fecha"])

    payouts_sheet = pd.read_excel(
        payoutsFilename, sheet_name="Pagos", parse_dates=True,
        usecols=["Descripción", "Monto", "Local", "Fecha"])

    # Get the first and last order id from payments sheet
    first_id, last_id = get_first_and_last_id(payouts_sheet)

    print("CHARGES COUNT:", len(charges_df))

    # Read Excel or CSV file for orders file
    cols_to_use = [
        "ID",
        "Pago",
        "Estado del pago",
        "Monto en productos",
        "Precio despacho"
    ]

    orders_df = pd.read_csv(
        ordersFilename,
        encoding="utf-8",
        usecols=cols_to_use,
        parse_dates=True,
        infer_datetime_format=True
    )

    payments = get_payments(payouts_sheet)

    devolutions = get_devolutions(charges_df)

    # Filter orders to only include payed orders
    orders_df = orders_df[orders_df['ID'].between(first_id, last_id)]

    orders = get_orders(orders_df)

    payouts = get_payouts(payouts_sheet)

    merged_dfs = orders.merge(payouts, how="outer",  left_index=True, right_index=True)
    merged_dfs = pd.concat([devolutions, merged_dfs])
    merged_dfs.to_excel("cierre-JV.xlsx")


if __name__ == "__main__":
    main()
