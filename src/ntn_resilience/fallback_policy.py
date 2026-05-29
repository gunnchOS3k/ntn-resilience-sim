def select_path(terrestrial_up: bool, ntn_available: bool) -> str:
    if terrestrial_up:
        return 'terrestrial'
    return 'ntn' if ntn_available else 'offline'
