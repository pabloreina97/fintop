def flatten_json(y):
    out = {}

    def flatten(x, parent_key=''):
        if isinstance(x, dict):
            for a in x:
                new_key = a  # Usar solo el nombre de la clave actual
                if isinstance(x[a], dict):
                    # Si el valor asociado a la clave es otro diccionario, se procesa recursivamente
                    flatten(x[a], new_key)
                else:
                    # Si el valor no es un diccionario, se añade directamente al resultado
                    out[new_key] = x[a]
        else:
            out[parent_key] = x

    flatten(y)
    return out
