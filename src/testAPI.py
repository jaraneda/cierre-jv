import getjusto
from settings import API_KEY

if __name__ == "__main__":
    getjusto = getjusto.Api(API_KEY)

    getjusto.orders()