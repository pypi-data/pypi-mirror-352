def get_flags_from_int(value, enum):
    set_flags = [flag for flag in enum if value & flag.value]
    return set_flags