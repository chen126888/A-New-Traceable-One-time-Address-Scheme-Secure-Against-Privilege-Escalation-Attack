CC = gcc
CFLAGS = -Wall -fPIC -I. -O2
LIBS = -lssl -lcrypto
OUT = ../../lib/libcryptonote2.so

# Source files
CORE_SRC = core.c
API_SRC = python_api.c
HEADERS = core.h python_api.h

# Object files  
CORE_OBJ = core.o
API_OBJ = python_api.o

# Main target: build the shared library
all: $(OUT)

$(OUT): $(CORE_OBJ) $(API_OBJ)
	@mkdir -p ../../lib
	$(CC) $(CFLAGS) -shared -o $(OUT) $(CORE_OBJ) $(API_OBJ) $(LIBS)
	@echo "✅ CryptoNote2 library built: $(OUT)"
	@echo "📁 Architecture: Core ($(CORE_SRC)) + API ($(API_SRC))"

# Compile core cryptographic functions
$(CORE_OBJ): $(CORE_SRC) core.h
	$(CC) $(CFLAGS) -c $(CORE_SRC) -o $(CORE_OBJ)
	@echo "🔐 CryptoNote2 core functions compiled"

# Compile Python API layer
$(API_OBJ): $(API_SRC) python_api.h core.h
	$(CC) $(CFLAGS) -c $(API_SRC) -o $(API_OBJ)
	@echo "🐍 CryptoNote2 Python API compiled"

# Clean build artifacts
clean:
	rm -f *.o $(OUT)
	@echo "🧹 CryptoNote2 cleaned"

# Check if library loads correctly
check: $(OUT)
	@echo "🔍 Checking CryptoNote2 library..."
	@ldd $(OUT) 2>/dev/null || echo "❌ Library dependencies missing"
	@echo "📊 Library info:"
	@file $(OUT)
	@ls -la $(OUT)
	@echo "✅ CryptoNote2 library check complete"

# Debug: show what symbols are exported
symbols: $(OUT)
	@echo "🔍 CryptoNote2 exported symbols:"
	@nm -D $(OUT) | grep " T " | grep cryptonote2 || echo "No cryptonote2 symbols found"

# Test: build a simple test program
test: test_cryptonote2
	./test_cryptonote2 ../../param/ecc_params/secp256r1.conf

test_cryptonote2: test_main.c $(CORE_OBJ) $(API_OBJ)
	$(CC) $(CFLAGS) -o test_cryptonote2 test_main.c $(CORE_OBJ) $(API_OBJ) $(LIBS)
	@echo "✅ CryptoNote2 test executable built: test_cryptonote2"

.PHONY: all clean check symbols test