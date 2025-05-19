CC = gcc
CFLAGS = -Wall -fPIC -I.         # -fPIC：生成可重定位位置的code (for .so)
LIBS = -lpbc -lcrypto            # 使用 PBC + OpenSSL
OUT = ../lib/libstealth.so       # 輸出路徑
SRC = my_stealth.c

all: $(OUT)

$(OUT): $(SRC)
	$(CC) $(CFLAGS) -shared -o $(OUT) $(SRC) $(LIBS)

clean:
	rm -f *.o $(OUT)

