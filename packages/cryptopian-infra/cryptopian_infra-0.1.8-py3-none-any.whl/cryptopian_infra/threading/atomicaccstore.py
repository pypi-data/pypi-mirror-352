from decimal import Decimal


class AtomicAccStore:
    def __init__(self):
        self.store = {}

    def pop(self, key) -> Decimal:
        value = self.store.pop(key, Decimal('0'))
        return value

    def set(self, key, amount: Decimal):
        if key not in self.store:
            self.store[key] = amount
        else:
            self.store[key] += amount
        return self.store.get(key, Decimal('0'))
