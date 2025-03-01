def seconds_to_str_in_srt(seconds: float):
    hours = seconds // (60 * 60)
    seconds %= (60 * 60)
    mins = seconds // 60
    seconds %= 60
    milli_seconds = int(seconds * 1000 % 1000)
    seconds //= 1
    return f"{hours}:{mins}:{seconds},{milli_seconds}"