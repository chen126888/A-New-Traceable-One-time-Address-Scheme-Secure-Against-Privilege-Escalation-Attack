#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include "sitaiba_core.h"

/**
 * Test program to verify SITAIBA core functionality
 * Similar to the original sitaiba.c main function
 */

void print_element_hex(const char* name, element_t elem) {
    unsigned char buf[512];
    memset(buf, 0, 512);
    element_to_bytes(buf, elem);
    
    printf("%s: ", name);
    for (int i = 0; i < 65; i++) {  // Print first 65 bytes
        printf("%02x", buf[i]);
    }
    printf("\n");
}

void print_buffer_hex(const char* name, unsigned char* buf, int len) {
    printf("%s: ", name);
    for (int i = 0; i < (len > 65 ? 65 : len); i++) {
        printf("%02x", buf[i]);
    }
    printf("\n");
}

int main(int argc, char **argv) {
    if (argc < 2) {
        fprintf(stderr, "Usage: %s <param_file>\n", argv[0]);
        return 1;
    }

    printf("🧪 Testing SITAIBA Core Functions\n");
    printf("================================\n\n");

    // Initialize SITAIBA
    printf("1. Initializing SITAIBA with %s...\n", argv[1]);
    
    // Check if param file exists
    FILE* test_file = fopen(argv[1], "r");
    if (!test_file) {
        printf("❌ Cannot open parameter file: %s\n", argv[1]);
        return 1;
    }
    fclose(test_file);
    
    int init_result = sitaiba_init(argv[1]);
    if (init_result != 0) {
        printf("❌ SITAIBA initialization failed with code: %d\n", init_result);
        return 1;
    }
    printf("✅ SITAIBA initialized successfully\n\n");

    // Check if initialized
    if (!sitaiba_is_initialized()) {
        printf("❌ SITAIBA not properly initialized!\n");
        return 1;
    }

    // Get pairing for element initialization
    pairing_t* pairing = sitaiba_get_pairing();
    if (!pairing) {
        printf("❌ Failed to get pairing!\n");
        return 1;
    }

    // Test 2: Generate user key pair
    printf("2. Testing user key generation...\n");
    element_t A_r, B_r, a_r, b_r;
    element_init_G1(A_r, *pairing);
    element_init_G1(B_r, *pairing);
    element_init_Zr(a_r, *pairing);
    element_init_Zr(b_r, *pairing);

    sitaiba_keygen(A_r, B_r, a_r, b_r);
    print_element_hex("User A_r", A_r);
    print_element_hex("User B_r", B_r);
    printf("✅ User key generation successful\n\n");

    // Test 3: Get tracer public key
    printf("3. Testing tracer key access...\n");
    element_t A_m;
    element_init_G1(A_m, *pairing);
    
    if (sitaiba_get_tracer_public_key(A_m) != 0) {
        printf("❌ Failed to get tracer public key!\n");
        return 1;
    }
    print_element_hex("Tracer A_m", A_m);
    printf("✅ Tracer key access successful\n\n");

    // Test 4: Generate stealth address
    printf("4. Testing stealth address generation...\n");
    element_t Addr, R1, R2;
    element_init_G1(Addr, *pairing);
    element_init_G1(R1, *pairing);
    element_init_G1(R2, *pairing);

    sitaiba_addr_gen(Addr, R1, R2, A_r, B_r, A_m);
    
    print_element_hex("Address", Addr);
    print_element_hex("R1", R1);
    print_element_hex("R2", R2);
    printf("✅ Address generation successful\n\n");

    // Test 5: Verify address (full verification)
    printf("5. Testing address verification (full)...\n");
    int verify_result = sitaiba_addr_verify(Addr, R1, R2, A_r, B_r, A_m, a_r);
    if (verify_result) {
        printf("✅ Address verification successful\n");
    } else {
        printf("❌ Address verification failed!\n");
        return 1;
    }

    // Test 6: Fast address verification
    printf("6. Testing fast address verification...\n");
    int fast_verify_result = sitaiba_addr_verify_fast(R1, R2, A_r, a_r);
    if (fast_verify_result) {
        printf("✅ Fast address verification successful\n");
    } else {
        printf("❌ Fast address verification failed!\n");
        return 1;
    }

    // Test 7: Generate one-time secret key
    printf("7. Testing one-time secret key generation...\n");
    element_t dsk;
    element_init_Zr(dsk, *pairing);
    
    sitaiba_onetime_skgen(dsk, R1, a_r, b_r, A_m);
    print_element_hex("One-time SK", dsk);
    printf("✅ One-time secret key generation successful\n\n");

    // Test 8: Identity tracing
    printf("8. Testing identity tracing...\n");
    element_t B_r_recovered;
    element_init_G1(B_r_recovered, *pairing);
    
    sitaiba_trace(B_r_recovered, Addr, R1, R2, NULL);
    print_element_hex("Recovered B_r", B_r_recovered);
    
    if (element_cmp(B_r_recovered, B_r) == 0) {
        printf("✅ Identity tracing successful - B_r matches!\n");
    } else {
        printf("❌ Identity tracing failed - B_r mismatch!\n");
        printf("Expected B_r: ");
        print_element_hex("", B_r);
        printf("Recovered B_r: ");
        print_element_hex("", B_r_recovered);
        return 1;
    }

    printf("\n🎉 All SITAIBA core tests passed!\n");
    printf("=================================\n");

    // Cleanup
    element_clear(A_r); element_clear(B_r); element_clear(a_r); element_clear(b_r);
    element_clear(A_m); element_clear(Addr); element_clear(R1); element_clear(R2);
    element_clear(dsk); element_clear(B_r_recovered);
    
    sitaiba_cleanup();
    return 0;
}