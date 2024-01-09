# import numpy as np
def change_price(max, min, percent = True): # Нахождение процентного отклонения цены
    change_price = (float(max) - float(min)) / float(min) * 100
    if percent:
        return f'{change_price:.2f}%'
    return round(change_price, 2)


def average_value(meaning, divider):
    average_value = float(meaning) // float(divider)
    return average_value


def down_price_token(max_price, min_price, percent = True): # Нахождение просевших монет
    rez = (float(max_price) - float(min_price)) / float(max_price) * 100
    if percent:
        return f'{rez:.2f}%'
    return round(rez, 2)




