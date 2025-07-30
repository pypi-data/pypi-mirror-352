def assertEqual(actual, expected):
    """
    Tests whether `actual` dictionary matches the `expected` dictionary.
    
    Parameters:
    - actual (dict): The dictionary to test.
    - expected (dict): The dictionary with expected key-value pairs.

    Returns:
    - bool: pass/fail
    """
    if (isinstance(actual, float) and isinstance(expected, float)):
        return abs(actual - expected) < 1e-6
    
    if (isinstance(actual, int) and isinstance(expected, int)):
        return actual == expected
    
    if (isinstance(actual, str) and isinstance(expected, str)):
        return actual == expected
    
    if (isinstance(actual, list) and isinstance(expected, list)):
        if len(actual) != len(expected):
            return False
        for i in range(len(actual)):
            if actual[i] != expected[i]:
                return False
        return True

    if (isinstance(actual, dict) and isinstance(expected, dict)):
        for key, expected_value in expected.items():
            if key not in actual:
                return False
            if actual[key] != expected_value:
                return False

        extra_keys = set(actual.keys()) - set(expected.keys())
        if extra_keys:
            return False

        return True
    
    return False

def check_set_equality(set1, set2):
    set1.sort()
    set2.sort()
    if len(set1) != len(set2):
        print(f"Sets are not equal, lengths differ: {len(set1)} != {len(set2)}")
        exit(1)
    for item in set1:
        if item not in set2:
            print(f"Item '{item}' from set1 not found in set2")
            exit(1)
            
    print( f"Sets are equal: {set1} == {set2}")

def check_dataframe_equality(df1, df2):
    if df1.shape != df2.shape:
        print(f"DataFrames are not equal, shapes differ: {df1.shape} != {df2.shape}")
        exit(1)
    
    if not df1.equals(df2):
        print("DataFrames are not equal")
        exit(1)
    
    print(f"DataFrames are equal:\n{df1}\n==\n{df2}")
    
def check_dictionary_equality(dict1, dict2):
    if dict1.keys() != dict2.keys():
        print(f"Dictionaries are not equal, keys differ: {dict1.keys()} != {dict2.keys()}")
        exit(1)
    
    for key in dict1:
        if dict1[key] != dict2[key]:
            print(f"Values for key '{key}' differ: {dict1[key]} != {dict2[key]}")
            exit(1)
    
    print(f"Dictionaries are equal:\n{dict1}\n==\n{dict2}")