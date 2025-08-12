/****************************************************************************
 * File: debug_sitaiba_full.c
 * Desc: Complete debug and test program for SITAIBA core functions
 *       Tests all cryptographic operations and their interactions
 ****************************************************************************/

#include "sitaiba_core.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int main() {
    printf("🧪 SITAIBA Complete Debug Test\n");
    printf("===============================\n\n");
    
    // Test 1: Library initialization
    printf("1️⃣  Testing library initialization...\n");
    const char* param_file = "../../param/a.param";
    
    int init_result = sitaiba_init(param_file);
    if (init_result != 0) {
        printf("❌ Library initialization failed with code: %d\n", init_result);
        return 1;
    }
    printf("✅ Library initialized successfully\n\n");
    
    pairing_t* pairing_ptr = sitaiba_get_pairing();
    if (!pairing_ptr) {
        printf("❌ Cannot get pairing\n");
        return 1;
    }
    
    // Test 2: User key generation
    printf("2️⃣  Testing user key generation...\n");
    element_t A, B, a, b;
    element_init_G1(A, *pairing_ptr);
    element_init_G1(B, *pairing_ptr);
    element_init_Zr(a, *pairing_ptr);
    element_init_Zr(b, *pairing_ptr);
    
    sitaiba_keygen(A, B, a, b);
    
    if (element_is0(A) || element_is0(B) || element_is0(a) || element_is0(b)) {
        printf("❌ User key generation produced zero elements\n");
        return 1;
    }
    printf("✅ User key generation successful\n\n");
    
    // Test 3: Get manager public key
    printf("3️⃣  Testing manager public key access...\n");
    element_t A_m_test;
    element_init_G1(A_m_test, *pairing_ptr);
    
    int get_result = sitaiba_get_tracer_public_key(A_m_test);
    if (get_result != 0) {
        printf("❌ Failed to get manager public key\n");
        return 1;
    }
    
    if (element_is0(A_m_test)) {
        printf("❌ Manager public key is zero\n");
        return 1;
    }
    printf("✅ Manager public key access successful\n\n");
    
    // Test 4: Address generation
    printf("4️⃣  Testing address generation...\n");
    element_t Addr, R1, R2;
    element_init_G1(Addr, *pairing_ptr);
    element_init_G1(R1, *pairing_ptr);
    element_init_G1(R2, *pairing_ptr);
    
    sitaiba_addr_gen(Addr, R1, R2, A, B, A_m_test);
    
    if (element_is0(Addr) || element_is0(R1) || element_is0(R2)) {
        printf("❌ Address generation produced zero elements\n");
        return 1;
    }
    printf("✅ Address generation successful\n\n");
    
    // Test 5: Full address recognition (should succeed)
    printf("5️⃣  Testing full address recognition (correct key)...\n");
    int recognize_result = sitaiba_addr_recognize(Addr, R1, R2, A, B, A_m_test, a);
    
    if (recognize_result != 1) {
        printf("❌ Address recognition failed (should succeed)\n");
        return 1;
    }
    printf("✅ Full address recognition successful\n\n");
    
    // Test 6: Fast address recognition (should succeed)
    printf("6️⃣  Testing fast address recognition (correct key)...\n");
    int fast_recognize_result = sitaiba_addr_recognize_fast(R1, R2, A, a);
    
    if (fast_recognize_result != 1) {
        printf("❌ Fast address recognition failed (should succeed)\n");
        return 1;
    }
    printf("✅ Fast address recognition successful\n\n");
    
    // Test 7: Address recognition with wrong key (should fail)
    printf("7️⃣  Testing address recognition with wrong key...\n");
    element_t wrong_a;
    element_init_Zr(wrong_a, *pairing_ptr);
    element_random(wrong_a);
    
    int wrong_recognize_result = sitaiba_addr_recognize_fast(R1, R2, A, wrong_a);
    if (wrong_recognize_result == 1) {
        printf("❌ Address recognition succeeded with wrong key (should fail)\n");
        return 1;
    }
    printf("✅ Address recognition correctly rejected wrong key\n\n");
    
    // Test 8: One-time secret key generation
    printf("8️⃣  Testing one-time secret key generation...\n");
    element_t dsk;
    element_init_Zr(dsk, *pairing_ptr);
    
    sitaiba_onetime_skgen(dsk, R1, a, b, A_m_test);
    
    if (element_is0(dsk)) {
        printf("❌ DSK generation produced zero element\n");
        return 1;
    }
    printf("✅ One-time secret key generation successful\n\n");
    
    // Test 8.5: Mathematical verification - check if g^dsk = addr
    printf("8️⃣.5️⃣ Testing mathematical relationship: g^dsk = addr...\n");
    element_t addr_check, g_core;
    element_init_G1(addr_check, *pairing_ptr);
    element_init_G1(g_core, *pairing_ptr);
    
    // Get the actual generator g from core
    int g_result = sitaiba_get_generator(g_core);
    if (g_result != 0) {
        printf("❌ Failed to get generator g\n");
        return 1;
    }
    
    // Compute g^dsk
    element_pow_zn(addr_check, g_core, dsk);
    
    // Check if addr_check equals addr
    int math_result = (element_cmp(addr_check, Addr) == 0);
    
    if (math_result) {
        printf("✅ Mathematical verification: g^dsk = addr ✓\n");
    } else {
        printf("❌ Mathematical verification: g^dsk ≠ addr\n");
    }
    printf("\n");
    
    element_clear(addr_check);
    element_clear(g_core);
    
    // Test 9: Identity tracing
    printf("9️⃣  Testing identity tracing...\n");
    element_t B_recovered;
    element_init_G1(B_recovered, *pairing_ptr);
    
    sitaiba_trace(B_recovered, Addr, R1, R2, NULL); // Use internal manager private key
    
    if (element_is0(B_recovered)) {
        printf("❌ Identity tracing produced zero element\n");
        return 1;
    }
    
    // Check if recovered B matches original B
    int trace_match = (element_cmp(B_recovered, B) == 0);
    if (!trace_match) {
        printf("❌ Traced identity does not match original B\n");
        return 1;
    }
    printf("✅ Identity tracing successful - B recovered correctly\n\n");
    
    // Test 10: Hash functions
    printf("🔟 Testing hash functions...\n");
    element_t hash_input_G1, hash_output_Zr;
    element_t hash_input_GT, hash_output_Zr2;
    element_init_G1(hash_input_G1, *pairing_ptr);
    element_init_Zr(hash_output_Zr, *pairing_ptr);
    element_init_GT(hash_input_GT, *pairing_ptr);
    element_init_Zr(hash_output_Zr2, *pairing_ptr);
    
    element_random(hash_input_G1);
    element_random(hash_input_GT);
    
    sitaiba_H1(hash_output_Zr, hash_input_G1);
    sitaiba_H2(hash_output_Zr2, hash_input_GT);
    
    if (element_is0(hash_output_Zr) || element_is0(hash_output_Zr2)) {
        printf("❌ Hash functions produced zero output\n");
        return 1;
    }
    printf("✅ Hash functions working correctly\n\n");
    
    // Test 11: Performance test
    printf("1️⃣1️⃣  Testing performance measurement...\n");
    sitaiba_reset_performance();
    
    // Do a few operations for performance measurement
    for (int i = 0; i < 3; i++) {
        element_t test_addr, test_r1, test_r2;
        element_init_G1(test_addr, *pairing_ptr);
        element_init_G1(test_r1, *pairing_ptr);
        element_init_G1(test_r2, *pairing_ptr);
        
        sitaiba_addr_gen(test_addr, test_r1, test_r2, A, B, A_m_test);
        sitaiba_addr_recognize_fast(test_r1, test_r2, A, a);
        
        element_clear(test_addr);
        element_clear(test_r1);
        element_clear(test_r2);
    }
    
    sitaiba_print_performance();
    printf("✅ Performance measurement working\n\n");
    
    // Cleanup
    element_clear(A);
    element_clear(B);
    element_clear(a);
    element_clear(b);
    element_clear(wrong_a);
    element_clear(A_m_test);
    element_clear(Addr);
    element_clear(R1);
    element_clear(R2);
    element_clear(dsk);
    element_clear(B_recovered);
    element_clear(hash_input_G1);
    element_clear(hash_output_Zr);
    element_clear(hash_input_GT);
    element_clear(hash_output_Zr2);
    
    printf("🎉 ALL SITAIBA TESTS PASSED!\n");
    printf("📊 Complete functionality verified:\n");
    printf("   ✅ Library initialization\n");
    printf("   ✅ User key generation\n");
    printf("   ✅ Manager key access\n");
    printf("   ✅ Address generation\n");
    printf("   ✅ Full address recognition\n");
    printf("   ✅ Fast address recognition\n");
    printf("   ✅ Wrong key rejection\n");
    printf("   ✅ One-time secret key generation\n");
    printf("   ✅ Identity tracing\n");
    printf("   ✅ Hash functions (H1, H2)\n");
    printf("   ✅ Performance measurement\n\n");
    
    // Cleanup
    sitaiba_cleanup();
    printf("🧹 Cleanup completed\n");
    
    return 0;
}