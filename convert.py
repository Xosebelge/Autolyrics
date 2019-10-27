import json

def convert(song):
    words = []
    for word in song["fragments"]:
        new_word = {
            "end":   float(word.get("end", 0)),
            "start": float(word.get("begin", 0)),
            "word":  "\n".join([line for line in word["lines"] if line != ""]),
        }
        if (new_word["word"] != ""):
            words.append(new_word)
    result = {
        "transcript": "\n".join([word["word"] for word in words]),
        "words": words
    }
    return result


def convert_file(inp, out):
    s = None
    with open(inp, "r") as f:
        s = convert(f.read())
    with open(out, "w") as f:
        f.write(s)

if __name__ == "__main__":
    from sys import argv
    convert_file(argv[1], argv[2])
