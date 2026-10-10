from src.services.bank.base import BaseBankProvider
from src.services.bank.mock import MockBankProvider
from src.services.bank.sber import SberProvider
from src.services.bank.tbank import TBankProvider
from src.services.bank.mkb import MKBProvider


def get_bank_provider(name: str = "mock") -> BaseBankProvider:
    providers = {
        "mock": MockBankProvider,
        "sber": SberProvider,
        "tbank": TBankProvider,
        "mkb": MKBProvider,
    }

    if name not in providers:
        raise ValueError(f"Unknown bank provider: {name}")

    return providers[name]()
