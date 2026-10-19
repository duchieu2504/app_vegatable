"""
Centralized name mapping for Vietnamese plant and disease names.

Single source of truth — all modules must import from here
instead of defining their own NAME_MAP.
"""

# Maps raw class labels (from model training) to human-readable Vietnamese names
NAME_MAP = {
    # Plants
    "RAUDEN": "Rau dền",
    "RAUMONGTOI": "Rau mồng tơi",
    "RAUMUONG": "Rau muống",
    "RAUNGOT": "Rau ngót",
    # Diseases
    "BENHDOMLA": "Bệnh đốm lá",
    "BENHSAUANLA": "Bệnh sâu ăn lá",
    "BENHXOANLA": "Bệnh xoăn lá",
    "BENHSAUVEBUA": "Bệnh sâu vẽ bùa",
    "BENHKHAMLA": "Bệnh khảm lá",
    # Health status
    "KHOEMANH": "Rau khỏe mạnh",
    "HEALTHY": "Rau khỏe mạnh",
}


def pretty_format(text: str) -> str:
    """
    Convert a raw class label segment to a human-readable Vietnamese name.
    Example: 'RAUMUONG' -> 'Rau muống', 'BENHDOMLA' -> 'Bệnh đốm lá'
    """
    text = text.replace('_', ' ').strip()
    return NAME_MAP.get(text.upper(), text.capitalize())


def parse_disease_id(disease_id: str) -> tuple:
    """
    Parse a disease_id like 'RAUMUONG___BENHDOMLA' into (plant_name, disease_name).
    Returns (plant_name, disease_name) as formatted Vietnamese strings.
    """
    parts = disease_id.split('___')
    if len(parts) == 2:
        return pretty_format(parts[0]), pretty_format(parts[1])
    return "Khác", pretty_format(disease_id)
