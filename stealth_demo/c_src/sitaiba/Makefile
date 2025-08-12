# Makefile for SITAIBA scheme
# Basic testing and compilation

CC = gcc
CFLAGS = -Wall -fPIC -I. -O2
LIBS = -lpbc -lgmp -lcrypto -lssl

# Object files
OBJS = sitaiba_core.o sitaiba_python_api.o

# Targets
.PHONY: all clean debug test test-full

all: libsitaiba.so debug_sitaiba_basic debug_sitaiba_full

# Core object
sitaiba_core.o: sitaiba_core.c sitaiba_core.h
	@echo "🔐 Compiling SITAIBA core..."
	$(CC) $(CFLAGS) -c sitaiba_core.c -o sitaiba_core.o

# Python API object  
sitaiba_python_api.o: sitaiba_python_api.c sitaiba_python_api.h sitaiba_core.h
	@echo "🐍 Compiling SITAIBA Python API..."
	$(CC) $(CFLAGS) -c sitaiba_python_api.c -o sitaiba_python_api.o

# Shared library
libsitaiba.so: $(OBJS)
	@echo "📚 Building SITAIBA shared library..."
	$(CC) -shared -o ../../lib/libsitaiba.so $(OBJS) $(LIBS)
	@echo "✅ SITAIBA shared library built: ../../lib/libsitaiba.so"

# Debug programs
debug_sitaiba_basic: debug_sitaiba_basic.c sitaiba_core.o
	@echo "🧪 Building basic debug program..."
	$(CC) $(CFLAGS) -o debug_sitaiba_basic debug_sitaiba_basic.c sitaiba_core.o $(LIBS)
	@echo "✅ debug_sitaiba_basic built successfully"

debug_sitaiba_full: debug_sitaiba_full.c sitaiba_core.o
	@echo "🧪 Building full debug program..."
	$(CC) $(CFLAGS) -o debug_sitaiba_full debug_sitaiba_full.c sitaiba_core.o $(LIBS)
	@echo "✅ debug_sitaiba_full built successfully"

# Test targets
test: debug_sitaiba_basic
	@echo "🚀 Running basic tests..."
	./debug_sitaiba_basic

test-full: debug_sitaiba_full
	@echo "🚀 Running complete tests..."
	./debug_sitaiba_full

# Clean
clean:
	@echo "🧹 Cleaning SITAIBA build artifacts..."
	rm -f *.o libsitaiba.so debug_sitaiba_basic debug_sitaiba_full
	@echo "🧹 Cleaned SITAIBA artifacts"