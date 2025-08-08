# Multi-Scheme Stealth Demo Master Makefile
# Build system for all cryptographic schemes

# Available schemes
SCHEMES = my_stealth cryptonote2 zhao hdwsa sitaiba

# Colors for output
GREEN = \033[0;32m
YELLOW = \033[1;33m
RED = \033[0;31m
NC = \033[0m # No Color

.PHONY: all clean help status $(SCHEMES)

# Default target: build all available schemes
all:
	@echo "$(GREEN)🔧 Building all schemes...$(NC)"
	@$(MAKE) my_stealth
	@echo "$(GREEN)✅ All available schemes built successfully!$(NC)"

# Build individual schemes
my_stealth:
	@echo "$(YELLOW)🔐 Building My Stealth scheme...$(NC)"
	@cd my_stealth && $(MAKE) all
	@echo "$(GREEN)✅ My Stealth scheme built$(NC)"

cryptonote2:
	@echo "$(YELLOW)💰 Building CryptoNote2 scheme...$(NC)"
	@if [ -f cryptonote2/Makefile ]; then \
		cd cryptonote2 && $(MAKE) all; \
		echo "$(GREEN)✅ CryptoNote2 scheme built$(NC)"; \
	else \
		echo "$(RED)❌ CryptoNote2 not available (source code needed)$(NC)"; \
	fi

zhao:
	@echo "$(YELLOW)🏛️ Building Zhao scheme...$(NC)"
	@if [ -f zhao/Makefile ]; then \
		cd zhao && $(MAKE) all; \
		echo "$(GREEN)✅ Zhao scheme built$(NC)"; \
	else \
		echo "$(RED)❌ Zhao scheme not available (source code needed)$(NC)"; \
	fi

hdwsa:
	@echo "$(YELLOW)🔑 Building HDWSA scheme...$(NC)"
	@if [ -f hdwsa/Makefile ]; then \
		cd hdwsa && $(MAKE) all; \
		echo "$(GREEN)✅ HDWSA scheme built$(NC)"; \
	else \
		echo "$(RED)❌ HDWSA scheme not available (source code needed)$(NC)"; \
	fi

sitaiba:
	@echo "$(YELLOW)🌐 Building Sitaiba scheme...$(NC)"
	@if [ -f sitaiba/Makefile ]; then \
		cd sitaiba && $(MAKE) all; \
		echo "$(GREEN)✅ Sitaiba scheme built$(NC)"; \
	else \
		echo "$(RED)❌ Sitaiba scheme not available (source code needed)$(NC)"; \
	fi

# Clean all schemes
clean:
	@echo "$(YELLOW)🧹 Cleaning all schemes...$(NC)"
	@for scheme in $(SCHEMES); do \
		if [ -f $$scheme/Makefile ]; then \
			echo "  🧹 Cleaning $$scheme..."; \
			cd $$scheme && $(MAKE) clean && cd ..; \
		fi; \
	done
	@echo "$(GREEN)✅ All schemes cleaned$(NC)"

# Check all built libraries
check:
	@echo "$(YELLOW)🔍 Checking all built libraries...$(NC)"
	@for scheme in $(SCHEMES); do \
		if [ -f $$scheme/Makefile ]; then \
			echo "  🔍 Checking $$scheme..."; \
			cd $$scheme && $(MAKE) check && cd ..; \
		fi; \
	done
	@echo "$(GREEN)✅ Library check complete$(NC)"

# Show status of all schemes
status:
	@echo "$(GREEN)📊 Multi-Scheme Build Status$(NC)"
	@echo "=================================="
	@for scheme in $(SCHEMES); do \
		printf "%-12s: " $$scheme; \
		if [ -f $$scheme/Makefile ]; then \
			if [ -f ../lib/lib$$scheme.so ]; then \
				echo "$(GREEN)✅ Built$(NC)"; \
			else \
				echo "$(YELLOW)📁 Source ready$(NC)"; \
			fi; \
		else \
			echo "$(RED)❌ Not available$(NC)"; \
		fi; \
	done
	@echo ""
	@echo "📁 Available libraries in ../lib/:"
	@ls -la ../lib/*.so 2>/dev/null || echo "  (no libraries built yet)"

# Install all libraries (optional)
install:
	@echo "$(YELLOW)📦 Installing all libraries...$(NC)"
	@for scheme in $(SCHEMES); do \
		if [ -f ../lib/lib$$scheme.so ]; then \
			sudo cp ../lib/lib$$scheme.so /usr/local/lib/; \
			echo "  📦 Installed lib$$scheme.so"; \
		fi; \
	done
	@sudo ldconfig
	@echo "$(GREEN)✅ All libraries installed$(NC)"

# Show help
help:
	@echo "$(GREEN)📚 Multi-Scheme Stealth Demo Build System$(NC)"
	@echo "=============================================="
	@echo ""
	@echo "$(YELLOW)Available targets:$(NC)"
	@echo "  all           - Build all available schemes (default)"
	@echo "  my_stealth    - Build My Stealth scheme only"
	@echo "  cryptonote2   - Build CryptoNote2 scheme only"  
	@echo "  zhao          - Build Zhao scheme only"
	@echo "  hdwsa         - Build HDWSA scheme only"
	@echo "  sitaiba       - Build Sitaiba scheme only"
	@echo "  clean         - Clean all build artifacts"
	@echo "  check         - Check all built libraries"
	@echo "  status        - Show build status of all schemes"
	@echo "  install       - Install libraries system-wide"
	@echo "  help          - Show this help"
	@echo ""
	@echo "$(YELLOW)Available schemes:$(NC)"
	@echo "  my_stealth    - Original stealth address scheme (✅ available)"
	@echo "  cryptonote2   - CryptoNote v2 protocol (❌ needs source code)"
	@echo "  zhao          - Zhao's scheme (❌ needs source code)"
	@echo "  hdwsa         - Hierarchical Deterministic scheme (❌ needs source code)"
	@echo "  sitaiba       - Sitaiba's scheme (❌ needs source code)"