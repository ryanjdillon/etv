
def walkrename(path, find_str, n=4):
    '''Rename number at end of file or path with `n` digits and leading zeros

    Recursively follows directories looking for files or paths beginning with
    'find_str'. This method assumes the name's fomrat is <find_str001.json> etc.

    Args
    ----
    path: str
        Root path containing files or directories to be renamed
    find_str: str
        Prefix to file or path to be renamed
    n: int
        Number of following digits, filled will preceding zeros
    '''
    import os

    def rename(src, find_str, n=4):
        fmt = find_str+'{:0'+str(n)+'.0f}'
        s = os.path.split(src)[1]
        if s.startswith(find_str):
            print(src)
            num = int(s[len(find_str):])
            ext = os.path.splitext(s)[1]
            dst = os.path.join(os.path.split(src)[0], fmt.format(num)+ext)
            os.rename(src, dst)

    for root, paths, files, in os.walk(path):
        for item in (paths+files):
            src = os.path.join(root, item)
            rename(src, find_str, n=n)

    return None
