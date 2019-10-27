import zipfile

def unzip(data):
    z = zipfile.ZipFile(data)
    z.extractall()
    return tuple(z.namelist())

