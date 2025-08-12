/****************************************************************************
 * File: debug_sitaiba_basic.c
 * Desc: Basic debug and test program for SITAIBA core functions
 *       Tests basic functionality and interface compatibility
 ****************************************************************************/

#include "sitaiba_core.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int main() {
    printf("🧪 SITAIBA Basic Debug Test\n");
    printf("==========================\n\n");
    
    // Test 1: Library initialization
    printf("1️⃣  Testing library initialization...\n");
    const char* param_file = "../../param/a.param";
    
    int init_result = sitaiba_init(param_file);
    if (init_result != 0) {
        printf("❌ Library initialization failed with code: %d\n", init_result);
        return 1;
    }
    
    if (!sitaiba_is_initialized()) {
        printf("❌ Library initialization verification failed\n");
        return 1;
    }
    
    printf("✅ Library initialized successfully\n\n");
    
    // Test 2: Element size check
    printf("2️⃣  Testing element sizes...\n");
    int g1_size = sitaiba_element_size_G1();
    int zr_size = sitaiba_element_size_Zr();
    
    printf("📏 G1 element size: %d bytes\n", g1_size);
    printf("📏 Zr element size: %d bytes\n", zr_size);
    
    if (g1_size <= 0 || zr_size <= 0) {
        printf("❌ Invalid element sizes\n");
        return 1;
    }
    
    printf("✅ Element sizes are valid\n\n");
    
    // Test 3: Basic key generation
    printf("3️⃣  Testing key generation...\n");
    
    element_t A, B, a, b;
    pairing_t* pairing_ptr = sitaiba_get_pairing();
    if (!pairing_ptr) {
        printf("❌ Cannot get pairing\n");
        return 1;
    }
    
    element_init_G1(A, *pairing_ptr);
    element_init_G1(B, *pairing_ptr);
    element_init_Zr(a, *pairing_ptr);
    element_init_Zr(b, *pairing_ptr);
    
    sitaiba_keygen(A, B, a, b);
    
    // Check if elements are not zero
    if (element_is0(A) || element_is0(B) || element_is0(a) || element_is0(b)) {
        printf("❌ Key generation produced zero elements\n");
        return 1;
    }
    
    printf("✅ Key generation successful\n");
    
    element_clear(A);
    element_clear(B);
    element_clear(a);
    element_clear(b);
    
    printf("\n4️⃣  Testing tracer key generation...\n");
    
    element_t A_m, a_m;
    element_init_G1(A_m, *pairing_ptr);
    element_init_Zr(a_m, *pairing_ptr);
    
    sitaiba_tracer_keygen(A_m, a_m);
    
    if (element_is0(A_m) || element_is0(a_m)) {
        printf("❌ Tracer key generation produced zero elements\n");
        return 1;
    }
    
    printf("✅ Tracer key generation successful\n");
    
    element_clear(A_m);
    element_clear(a_m);
    
    printf("\n🎉 All basic tests passed!\n");
    printf("📊 Functions available: keygen, tracer_keygen, initialization\n");
    printf("⚠️  Note: Full testing requires implementation of remaining functions\n");
    
    // Cleanup
    sitaiba_cleanup();
    printf("\n🧹 Cleanup completed\n");
    
    return 0;
}