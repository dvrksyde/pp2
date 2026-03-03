import re

with open("raw.txt", "r", encoding="utf-8") as f:
    while True:
        line = f.readline()
        if not line:
            break

        line = line.strip()

        print(bool(re.fullmatch(r"аб*", line)))
        print(bool(re.fullmatch(r"аб{2,3}", line)))
        print(re.findall(r"\b[а-яё]+(_[а-яё]+)+\b", line))
        print(re.findall(r"\b[А-ЯЁ][а-яё]+\b", line))
        print(bool(re.fullmatch(r"а.*б", line)))
        print(re.sub(r"[ ,.]+", ":", line))

        def snake_to_camel(s):
            parts = s.split("_")
            return parts[0] + "".join(p.capitalize() for p in parts[1:])

        def camel_to_snake(s):
            return re.sub(r"(?<!^)(?=[А-ЯЁ])", "_", s).lower()

        print([snake_to_camel(w) for w in re.findall(r"\b[а-яё]+(_[а-яё]+)+\b", line)])
        print(re.split(r"(?=[А-ЯЁ])", line))
        print(re.sub(r"(?<!^)(?=[А-ЯЁ])", " ", line))
        print(camel_to_snake(line))
