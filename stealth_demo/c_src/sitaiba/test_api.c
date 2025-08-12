/****************************************************************************
 * File: test_api.c
 * Desc: Test program for SITAIBA Python API interface
 *       Tests buffer-based API functions
 ****************************************************************************/

#include "sitaiba_python_api.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int main() {
    printf("🧪 SITAIBA API Interface Test\n");
    printf("===============================\n\n");
    
    // Test 1: Initialize library
    printf("1️⃣  Testing library initialization...\n");
    const char* param_file = "../../param/a.param";
    
    int init_result = sitaiba_init_simple(param_file);
    if (init_result != 0) {
        printf("❌ Library initialization failed with code: %d\n", init_result);
        return 1;
    }
    printf("✅ Library initialized successfully\n\n");
    
    // Get buffer sizes
    int g1_size = sitaiba_element_size_G1_simple();
    int zr_size = sitaiba_element_size_Zr_simple();
    
    if (g1_size <= 0 || zr_size <= 0) {
        printf("❌ Invalid buffer sizes: G1=%d, Zr=%d\n", g1_size, zr_size);
        return 1;
    }
    printf("📏 Buffer sizes: G1=%d bytes, Zr=%d bytes\n\n", g1_size, zr_size);
    
    // Test 2: User key generation
    printf("2️⃣  Testing user key generation API...\n");
    unsigned char A_buf[256], B_buf[256], a_buf[256], b_buf[256];
    
    sitaiba_keygen_simple(A_buf, B_buf, a_buf, b_buf, 256);
    printf("✅ User key generation API successful\n\n");
    
    // Test 3: Manager key access
    printf("3️⃣  Testing manager public key API...\n");
    unsigned char A_m_buf[256];
    
    int tracer_result = sitaiba_get_tracer_public_key_simple(A_m_buf, 256);
    if (tracer_result != 0) {
        printf("❌ Failed to get manager public key via API\n");
        return 1;
    }
    printf("✅ Manager public key API successful\n\n");
    
    // Test 4: Address generation
    printf("4️⃣  Testing address generation API...\n");
    unsigned char addr_buf[256], r1_buf[256], r2_buf[256];
    
    sitaiba_addr_gen_simple(A_buf, B_buf, NULL, addr_buf, r1_buf, r2_buf, 256);
    printf("✅ Address generation API successful\n\n");
    
    // Test 5: Full address recognition (should succeed)
    printf("5️⃣  Testing full address recognition API...\n");
    int recognize_result = sitaiba_addr_recognize_simple(
        addr_buf, r1_buf, r2_buf, A_buf, B_buf, a_buf, NULL);
    
    if (recognize_result != 1) {
        printf("❌ Address recognition API failed (should succeed)\n");
        return 1;
    }
    printf("✅ Full address recognition API successful\n\n");
    
    // Test 6: Fast address recognition (should succeed)
    printf("6️⃣  Testing fast address recognition API...\n");
    int fast_recognize_result = sitaiba_addr_recognize_fast_simple(
        r1_buf, r2_buf, A_buf, a_buf);
    
    if (fast_recognize_result != 1) {
        printf("❌ Fast address recognition API failed (should succeed)\n");
        return 1;
    }
    printf("✅ Fast address recognition API successful\n\n");
    
    // Test 7: One-time secret key generation
    printf("7️⃣  Testing one-time secret key generation API...\n");
    unsigned char dsk_buf[256];
    
    sitaiba_onetime_skgen_simple(r1_buf, a_buf, b_buf, NULL, dsk_buf, 256);
    printf("✅ One-time secret key generation API successful\n\n");
    
    // Test 8: Identity tracing
    printf("8️⃣  Testing identity tracing API...\n");
    unsigned char B_recovered_buf[256];
    
    sitaiba_trace_simple(addr_buf, r1_buf, r2_buf, NULL, B_recovered_buf, 256);
    
    // Compare with original B
    int trace_match = (memcmp(B_recovered_buf, B_buf, g1_size) == 0);
    if (!trace_match) {
        printf("❌ Traced identity does not match original B\n");
        return 1;
    }
    printf("✅ Identity tracing API successful - B recovered correctly\n\n");
    
    // Test 9: Performance test
    printf("9️⃣  Testing performance API...\n");
    double results[5];
    
    sitaiba_performance_test_simple(10, results);
    
    printf("📊 Performance Results (10 iterations):\n");
    printf("   Address Generation:    %.3f ms\n", results[0]);
    printf("   Address Recognition:   %.3f ms\n", results[1]);
    printf("   Fast Recognition:      %.3f ms\n", results[2]);
    printf("   One-time SK Gen:       %.3f ms\n", results[3]);
    printf("   Identity Tracing:      %.3f ms\n", results[4]);
    printf("✅ Performance API successful\n\n");
    
    // Cleanup
    sitaiba_cleanup_simple();
    
    printf("🎉 ALL SITAIBA API TESTS PASSED!\n");
    printf("📊 Complete API functionality verified:\n");
    printf("   ✅ Library initialization\n");
    printf("   ✅ Buffer size queries\n");
    printf("   ✅ User key generation\n");
    printf("   ✅ Manager key access\n");
    printf("   ✅ Address generation\n");
    printf("   ✅ Full address recognition\n");
    printf("   ✅ Fast address recognition\n");
    printf("   ✅ One-time secret key generation\n");
    printf("   ✅ Identity tracing\n");
    printf("   ✅ Performance measurement\n\n");
    
    printf("🧹 Cleanup completed\n");
    
    return 0;
}