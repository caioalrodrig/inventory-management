import unicodedata


class InventoryUtils:
    """Utility methods for inventory/stock identifiers and names."""

    @staticmethod
    def normalize_identifier(name: str) -> str:
        """Normalize name: lowercase, no accents. Remove leading/trailing whitespace."""
        n = unicodedata.normalize("NFD", name)
        n = "".join(c for c in n if unicodedata.category(c) != "Mn")
        return n.lower().strip()
