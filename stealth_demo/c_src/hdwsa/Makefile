CC = gcc
CFLAGS = -Wall -fPIC -I. -O2
LIBS = -lpbc -lgmp -lcrypto -lssl
OUT = ../../lib/libhdwsa.so

# Source files
CORE_SRC = hdwsa_core.c
API_SRC = hdwsa_python_api.c
HEADERS = hdwsa_core.h hdwsa_python_api.h

# Object files
CORE_OBJ = hdwsa_core.o
API_OBJ = hdwsa_python_api.o

# Main target: build the shared library
all: $(OUT)

$(OUT): $(CORE_OBJ) $(API_OBJ)
	@mkdir -p ../../lib
	$(CC) $(CFLAGS) -shared -o $(OUT) $(CORE_OBJ) $(API_OBJ) $(LIBS)
	@echo "✅ HDWSA shared library built: $(OUT)"

# Compile core cryptographic functions
$(CORE_OBJ): $(CORE_SRC) hdwsa_core.h
	$(CC) $(CFLAGS) -c $(CORE_SRC) -o $(CORE_OBJ)
	@echo "🔐 HDWSA core cryptographic functions compiled"

# Compile Python API layer
$(API_OBJ): $(API_SRC) hdwsa_python_api.h hdwsa_core.h
	$(CC) $(CFLAGS) -c $(API_SRC) -o $(API_OBJ)
	@echo "🐍 HDWSA Python API interface compiled"

# Check if library loads correctly
check: $(OUT)
	@echo "🔍 Checking HDWSA library..."
	@file $(OUT)
	@ls -la $(OUT)

# Debug: show what symbols are exported
symbols: $(OUT)
	@echo "🔍 Exported HDWSA symbols:"
	@nm -D $(OUT) | grep " T " | grep hdwsa || echo "No hdwsa symbols found"

# Clean build artifacts
clean:
	rm -f *.o
	@echo "🧹 Cleaned HDWSA build artifacts"

# Clean including library
clean-all: clean
	rm -f $(OUT)
	@echo "🧹 Cleaned all HDWSA artifacts including library"

# Development help
help:
	@echo "📚 HDWSA scheme build targets:"
	@echo "  all       - Build HDWSA shared library (default)"
	@echo "  check     - Check library dependencies and info"
	@echo "  symbols   - Show exported function symbols"
	@echo "  clean     - Remove build artifacts"
	@echo "  clean-all - Remove all artifacts including library"
	@echo "  help      - Show this help"

.PHONY: all check symbols clean clean-all help