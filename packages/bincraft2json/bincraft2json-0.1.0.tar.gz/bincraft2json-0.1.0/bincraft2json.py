from ._core import decode_bincraft

def convert_bincraft_to_json(filename, zstd_compressed=False):
    """
    Convertit un fichier BinCraft en JSON.
    
    Args:
        filename (str): Chemin vers le fichier BinCraft
        zstd_compressed (bool): Indique si le fichier est compressé avec zstd
        
    Returns:
        dict: Les données de l'aéronef au format JSON
    """
    return decode_bincraft(filename, zstd_compressed) 