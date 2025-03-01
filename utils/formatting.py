def seconds_to_str_in_srt(seconds: float):
    hours = int(seconds // (60 * 60))
    seconds %= (60 * 60)
    mins = int(seconds // 60)
    seconds %= 60
    milli_seconds = int(seconds * 1000 % 1000)
    seconds = int(seconds)
    return f"{hours:02}:{mins:02}:{seconds:02},{milli_seconds:03d}"

if __name__ == "__main__":
    print(seconds_to_str_in_srt(100.100))
    print(seconds_to_str_in_srt(3661.758))
    print(seconds_to_str_in_srt(6000000000.9999999999999999))

