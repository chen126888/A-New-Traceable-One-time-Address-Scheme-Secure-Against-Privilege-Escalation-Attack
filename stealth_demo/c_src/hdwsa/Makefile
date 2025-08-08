CC = gcc
CFLAGS = -Wall -fPIC -I. -O2
LIBS = -lpbc -lgmp -lcrypto -lssl
OUT = ../../lib/libhdwsa.so

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
	@echo "✅ HDWSA library built: $(OUT)"
	@echo "📁 Architecture: Core ($(CORE_SRC)) + API ($(API_SRC))"

# Compile core cryptographic functions
$(CORE_OBJ): $(CORE_SRC) core.h
	$(CC) $(CFLAGS) -c $(CORE_SRC) -o $(CORE_OBJ)
	@echo "🔐 HDWSA core functions compiled"

# Compile Python API layer
$(API_OBJ): $(API_SRC) python_api.h core.h
	$(CC) $(CFLAGS) -c $(API_SRC) -o $(API_OBJ)
	@echo "🐍 HDWSA Python API compiled"

# Clean build artifacts
clean:
	rm -f *.o $(OUT)
	@echo "🧹 HDWSA cleaned"

# Check if library loads correctly
check: $(OUT)
	@echo "🔍 Checking HDWSA library..."
	@ldd $(OUT) 2>/dev/null || echo "❌ Library dependencies missing"
	@echo "📊 Library info:"
	@file $(OUT)
	@ls -la $(OUT)
	@echo "✅ HDWSA library check complete"

# Debug: show what symbols are exported
symbols: $(OUT)
	@echo "🔍 HDWSA exported symbols:"
	@nm -D $(OUT) | grep " T " | grep hdwsa || echo "No hdwsa symbols found"

.PHONY: all clean check symbols