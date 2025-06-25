CC = gcc
CFLAGS = -Wall -fPIC -I.         # -fPIC：生成可重定位位置的 code (for .so)
LIBS = -lpbc -lgmp -lcrypto      #  -lgmp 支援 mpz_t　-lpbc: pbc -lcrypto:openssl
OUT = ../lib/libstealth.so       # 輸出路徑
SRC = my_scheme.c

all: $(OUT)

$(OUT): $(SRC)
	$(CC) $(CFLAGS) -shared -o $(OUT) $(SRC) $(LIBS)

clean:
	rm -f *.o $(OUT)