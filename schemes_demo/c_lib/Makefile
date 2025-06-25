CC=gcc
CFLAGS=-Wall -fPIC -O2
LIBS=-lpbc -lgmp -lssl -lcrypto
SRCDIR=.
LIBDIR=lib
TARGET=$(LIBDIR)/libstealth.so
SRC=my_stealth.c

all: $(TARGET)

$(LIBDIR):
	mkdir -p $(LIBDIR)

$(TARGET): $(SRC) | $(LIBDIR)
	$(CC) $(CFLAGS) -shared -o $@ $< $(LIBS)

clean:
	rm -rf $(LIBDIR)

.PHONY: all clean
