#backend.py

from .constants import TARGET_PATTERN

def validate_sequence(user_blocks_sorted: list) -> bool:
    """
    Verifică dacă lista de blocuri a utilizatorului (deja sortată vizual)
    corespunde modelului țintă.
    """
    if len(user_blocks_sorted) != len(TARGET_PATTERN):
        return False

    for i, block_ui in enumerate(user_blocks_sorted):
        # block_ui.data conține tuplul de configurare (Stare, Durata...)
        target_data = TARGET_PATTERN[i]
        
        if block_ui.data != target_data:
            return False
            
    return True