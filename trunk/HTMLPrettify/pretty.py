import BeautifulSoup
import sys

if __name__ == '__main__':
    if len(sys.argv) != 2:
        sys.exit()
    filein = sys.argv[1]
    fileout = 'ou_' + filein
    
    f = open(filein, 'r')
    cont = f.read()
    f.close()

    b = BeautifulSoup.BeautifulSoup(cont)
    f = open(fileout, 'w')
    f.write(b.prettify())
    f.close()