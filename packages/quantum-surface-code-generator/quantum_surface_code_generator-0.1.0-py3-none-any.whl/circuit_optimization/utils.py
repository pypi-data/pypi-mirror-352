def count_gates(circuit: dict) -> int:
    """Return the number of gates in the circuit."""
    return len(circuit.get('gates', []))

def calculate_depth(circuit: dict) -> int:
    """Estimate the circuit depth (max time step)."""
    # Assume each gate has a 'time' field; otherwise, return 0
    if not circuit.get('gates'):
        return 0
    return max((g.get('time', 0) for g in circuit['gates']), default=0) + 1

def count_swaps(circuit: dict) -> int:
    """Count the number of SWAP gates in the circuit."""
    return sum(1 for g in circuit.get('gates', []) if g.get('name', '').lower() == 'swap') 