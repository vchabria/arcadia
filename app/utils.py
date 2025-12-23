"""
Utility functions for inbound order processing
"""


def parse_temperature_from_product_code(product_code: str) -> str:
    """
    Parse temperature from product code's last character(s)
    
    Rules:
    - F = Freezer
    - C = Cooler
    - R = Cooler
    - FR = Freezer Crates
    
    Args:
        product_code: Product code string (e.g., "PP48F", "BTL18-1R")
    
    Returns:
        Temperature string: "FREEZER", "COOLER", or "FREEZER CRATES"
    """
    if not product_code:
        return "FREEZER"  # Default
    
    product_code = product_code.upper().strip()
    
    # Check for FR (Freezer Crates) - 2 character ending
    if product_code.endswith('FR'):
        return "FREEZER CRATES"
    
    # Check last character
    last_char = product_code[-1]
    if last_char == 'F':
        return "FREEZER"
    elif last_char in ['C', 'R']:
        return "COOLER"
    
    return "FREEZER"  # Default

