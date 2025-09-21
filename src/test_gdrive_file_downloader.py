import gdown


# https://drive.google.com/open?id=18GwXB7fpana6JAP4tigi8zfcqPvd6w8B&usp=drive_fs
# The file id from the URL: https://drive.google.com/open?id=FILE_ID
file_id = "1R7BZAarfgQwVEDMkuxjL-7sQ_aEv-_E2"
# Or you can use the full URL format
url = f"https://drive.google.com/uc?id={file_id}"

# The destination local path
output = "test.png"  # change extension/name

gdown.download(url, output, quiet=False)