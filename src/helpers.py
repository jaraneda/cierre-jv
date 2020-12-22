from os import path
from datetime import datetime

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

def process_charges_cols(df):
    df["pago"] = [int(v) * -1 for v in df["pago"]] # Make charges' amounts negative
    dates, times = get_dates_and_times(df["fecha"])
    df["fecha"] = dates
    df["hora"] = times
    df["costo envío"] = ""
    df["metodo de pago"] = ""
    df["valor"] = ""
    df["restaurant_name"] = replace_store_name(df["restaurant_name"], dates)
    df = add_empty_cols(df)
    df = reorder_final_df(df)
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


def replace_store_name(store_col, dates_col):
    '''Returns an array with replaced store name'''

    store_names = []

    for idx, name in enumerate(store_col):
        if "Regiones" in name and datetime.strptime(dates_col[idx], "%Y-%m-%d") < datetime.strptime("2020-12-15", "%Y-%m-%d"):
            store_names.append("Alonso de Cordova")
        elif "Regiones" in name or "Chicureo" in name or "Food Truck" in name:
            store_names.append("Rosario Norte")
        else:
            store_names.append(name)

    return store_names

def get_order_ids_from_description(description_column):
    return list(
        map(lambda descripcion: descripcion.split("#")[1], description_column)
    )

def process_payouts_and_tips(payouts, tips):
    for index, row in tips.iterrows():
        if(index in payouts.index):
            payouts.loc[index, 'pago'] = payouts.loc[index]['pago'] + row['pago']
            if(index in tips.index): tips.drop(index, inplace=True)
    return (payouts, tips)

def existsFile(filename):
    return path.isfile(filename)
