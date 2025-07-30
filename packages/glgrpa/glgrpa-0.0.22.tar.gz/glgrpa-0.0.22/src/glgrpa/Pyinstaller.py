def obtener_ruta_recurso(ruta_recurso: str) -> str:
    """
    Devuelve la ruta absoluta de un recurso, considerando si el script está empaquetado con PyInstaller o no.

    :param ruta_recurso: Ruta del recurso (puede ser absoluta o relativa).
    :return: Ruta absoluta del recurso.
    """
    import os
    import sys

    # Verifica si el script está empaquetado con PyInstaller
    if os.path.isabs(ruta_recurso):
        return ruta_recurso
    
    if hasattr(sys, '_MEIPASS'):
        base_path = os.path.dirname(sys.executable)
    else:
        base_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..')
        
    return os.path.join(base_path, ruta_recurso)