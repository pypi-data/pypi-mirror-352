def foreign_key_helper(tn, attribute):
    _ =  f"{attribute}_id INTEGER REFERENCES {tn}(id) ON DELETE CASCADE ON UPDATE CASCADE"
    return _
