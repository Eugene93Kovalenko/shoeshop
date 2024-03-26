from .cart import Cart


def cart(request) -> dict[str: Cart]:
    return {'cart': Cart(request)}
