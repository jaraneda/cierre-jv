from os import path
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


def replace_store_name(store_col):
    '''Returns an array with replaced store name'''

    store_names = []

    for name in store_col:
        if "Regiones" in name:
            store_names.append("Alonso de Cordova")
        elif "Chicureo" in name or "Food Truck" in name:
            store_names.append("Rosario Norte")
        else:
            store_names.append(name)

    return store_names

def get_order_ids_from_description(description_column):
    return list(
        map(lambda descripcion: descripcion.split("#")[1], description_column)
    )

def get_tips(closure_df):
    '''Returns a df of tips with order_id'''
    order_id_start_index = 36

    df = rename_closure_cols(closure_df)

    # Filter tips
    tips_df = df.query('estado == "Propina para repartidores"')
    tips_df = tips_df[['order_id', 'pago']]
    tips_df['order_id'] = [tip[order_id_start_index:] for tip in tips_df["order_id"]]
    tips_df = tips_df.set_index("order_id")

    # Group tips by order id
    grouped_tips_df = tips_df.groupby(tips_df.index).sum()

    return grouped_tips_df

def substract_tips(amounts_df, tips_df):
    '''Returns an array of payouts without tips sorted by order_id'''

    descriptions = amounts_df["Descripción"]
    amounts = amounts_df["Monto"]

    full_order_ids = get_order_ids_from_description(descriptions)
    order_ids_first_part = [value.split('-')[0] for value in full_order_ids]

    amounts_df = pd.DataFrame(
        {"order_id": order_ids_first_part, "pago": amounts}
    )
    amounts_df = amounts_df.set_index("order_id")

    # Substract tips from amounts by order_id
    result = amounts_df.sub(tips_df, fill_value=0)
    # Filter rows where amount is less than 0
    result = result[result['pago'] >= 0]

    return result['pago']

def existsFile(filename):
    return path.isfile(filename)
