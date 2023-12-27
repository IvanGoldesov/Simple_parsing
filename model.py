from dataclasses import dataclass

@dataclass
class Product:
    name : str
    link : str
    SALE : str
    price : int
    img : str
    available_sizes : str