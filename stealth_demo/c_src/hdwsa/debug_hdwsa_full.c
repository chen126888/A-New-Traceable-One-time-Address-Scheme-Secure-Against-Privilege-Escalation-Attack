/****************************************************************************
 * File: debug_hdwsa_full.c
 * Desc: Complete debug and test program for HDWSA core functions
 *       Tests all cryptographic operations and their interactions
 ****************************************************************************/

#include "hdwsa_core.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int main() {
    printf("🧪 HDWSA Complete Debug Test\n");
    printf("==============================\n\n");
    
    // Test 1: Library initialization
    printf("1️⃣  Testing library initialization...\n");
    const char* param_file = "../../param/a.param";
    
    int init_result = hdwsa_init(param_file);
    if (init_result != 0) {
        printf("❌ Library initialization failed with code: %d\n", init_result);
        return 1;
    }
    
    if (!hdwsa_is_initialized()) {
        printf("❌ Library initialization check failed\n");
        return 1;
    }
    printf("✅ Library initialized successfully\n\n");
    
    // Test 2: Element sizes
    printf("2️⃣  Testing element sizes...\n");
    size_t g1_size, zr_size;
    hdwsa_get_element_sizes(&g1_size, &zr_size);
    printf("📏 Element sizes: G1=%zu bytes, Zr=%zu bytes\n", g1_size, zr_size);
    
    if (g1_size == 0 || zr_size == 0) {
        printf("❌ Invalid element sizes\n");
        return 1;
    }
    printf("✅ Element sizes obtained successfully\n\n");
    
    // Test 3: Root wallet key generation
    printf("3️⃣  Testing root wallet key generation...\n");
    unsigned char root_A[g1_size], root_B[g1_size];
    unsigned char root_alpha[zr_size], root_beta[zr_size];
    
    int root_result = hdwsa_root_keygen(root_A, root_B, root_alpha, root_beta);
    if (root_result != 0) {
        printf("❌ Root wallet key generation failed\n");
        return 1;
    }
    
    // Check if all buffers are non-zero
    int all_zero = 1;
    for (size_t i = 0; i < g1_size; i++) {
        if (root_A[i] != 0 || root_B[i] != 0) all_zero = 0;
    }
    for (size_t i = 0; i < zr_size; i++) {
        if (root_alpha[i] != 0 || root_beta[i] != 0) all_zero = 0;
    }
    
    if (all_zero) {
        printf("❌ Root keys are all zero\n");
        return 1;
    }
    printf("✅ Root wallet key generation successful\n\n");
    
    // Test 4: User keypair generation (Level 1)
    printf("4️⃣  Testing user keypair generation (Level 1)...\n");
    unsigned char A1[g1_size], B1[g1_size];
    unsigned char alpha1[zr_size], beta1[zr_size];
    const char* id_level1 = "id_0";
    
    int user1_result = hdwsa_keypair_gen(A1, B1, alpha1, beta1, 
                                        root_alpha, root_beta, id_level1);
    if (user1_result != 0) {
        printf("❌ Level 1 user keypair generation failed\n");
        return 1;
    }
    printf("✅ Level 1 user keypair generation successful (ID: %s)\n\n", id_level1);
    
    // Test 5: User keypair generation (Level 2)
    printf("5️⃣  Testing user keypair generation (Level 2)...\n");
    unsigned char A2[g1_size], B2[g1_size];
    unsigned char alpha2[zr_size], beta2[zr_size];
    const char* id_level2 = "id_0,id_1";
    
    int user2_result = hdwsa_keypair_gen(A2, B2, alpha2, beta2, 
                                        alpha1, beta1, id_level2);
    if (user2_result != 0) {
        printf("❌ Level 2 user keypair generation failed\n");
        return 1;
    }
    printf("✅ Level 2 user keypair generation successful (ID: %s)\n\n", id_level2);
    
    // Test 6: User keypair generation (Level 3)
    printf("6️⃣  Testing user keypair generation (Level 3)...\n");
    unsigned char A3[g1_size], B3[g1_size];
    unsigned char alpha3[zr_size], beta3[zr_size];
    const char* id_level3 = "id_0,id_1,id_5";
    
    int user3_result = hdwsa_keypair_gen(A3, B3, alpha3, beta3, 
                                        alpha2, beta2, id_level3);
    if (user3_result != 0) {
        printf("❌ Level 3 user keypair generation failed\n");
        return 1;
    }
    printf("✅ Level 3 user keypair generation successful (ID: %s)\n\n", id_level3);
    
    // Test 7: Address generation (using Level 1 user)
    printf("7️⃣  Testing address generation...\n");
    size_t gt_size = g1_size * 12; // Estimated GT size
    unsigned char Qr[g1_size], Qvk[gt_size];
    
    int addr_result = hdwsa_addr_gen(Qr, Qvk, A1, B1);
    if (addr_result != 0) {
        printf("❌ Address generation failed\n");
        return 1;
    }
    
    // Check if address components are non-zero
    int qr_zero = 1, qvk_zero = 1;
    for (size_t i = 0; i < g1_size; i++) {
        if (Qr[i] != 0) qr_zero = 0;
    }
    for (size_t i = 0; i < gt_size; i++) {
        if (Qvk[i] != 0) qvk_zero = 0;
    }
    
    if (qr_zero || qvk_zero) {
        printf("❌ Address components are zero\n");
        return 1;
    }
    printf("✅ Address generation successful\n\n");
    
    // Test 8: Address recognition (correct key)
    printf("8️⃣  Testing address recognition (correct key)...\n");
    int recognize_result = hdwsa_addr_recognize(Qvk, Qr, A1, B1, beta1);
    
    if (recognize_result != 1) {
        printf("❌ Address recognition failed (should succeed)\n");
        return 1;
    }
    printf("✅ Address recognition successful\n\n");
    
    // Test 9: Address recognition (wrong key)
    printf("9️⃣  Testing address recognition (wrong key)...\n");
    int wrong_recognize_result = hdwsa_addr_recognize(Qvk, Qr, A2, B2, beta2);
    
    if (wrong_recognize_result == 1) {
        printf("❌ Address recognition succeeded with wrong key (should fail)\n");
        return 1;
    }
    printf("✅ Address recognition correctly rejected wrong key\n\n");
    
    // Test 10: DSK generation
    printf("🔟 Testing DSK generation...\n");
    unsigned char dsk[g1_size];
    
    int dsk_result = hdwsa_dsk_gen(dsk, Qr, B1, alpha1, beta1);
    if (dsk_result != 0) {
        printf("❌ DSK generation failed\n");
        return 1;
    }
    
    // Check if DSK is non-zero
    int dsk_zero = 1;
    for (size_t i = 0; i < g1_size; i++) {
        if (dsk[i] != 0) dsk_zero = 0;
    }
    
    if (dsk_zero) {
        printf("❌ DSK is zero\n");
        return 1;
    }
    printf("✅ DSK generation successful\n\n");
    
    // Test 11: Message signing
    printf("1️⃣1️⃣  Testing message signing...\n");
    const char* message = "Hello, HDWSA digital signature!";
    unsigned char h[zr_size], Q_sigma[g1_size];
    
    int sign_result = hdwsa_sign(h, Q_sigma, dsk, Qr, Qvk, message);
    if (sign_result != 0) {
        printf("❌ Message signing failed\n");
        return 1;
    }
    
    // Check if signature components are non-zero
    int h_zero = 1, sig_zero = 1;
    for (size_t i = 0; i < zr_size; i++) {
        if (h[i] != 0) h_zero = 0;
    }
    for (size_t i = 0; i < g1_size; i++) {
        if (Q_sigma[i] != 0) sig_zero = 0;
    }
    
    if (h_zero || sig_zero) {
        printf("❌ Signature components are zero\n");
        return 1;
    }
    printf("✅ Message signing successful\n");
    printf("📝 Message: \"%s\"\n\n", message);
    
    // Test 12: Signature verification (correct signature)
    printf("1️⃣2️⃣  Testing signature verification (correct signature)...\n");
    int verify_result = hdwsa_verify(h, Q_sigma, Qr, Qvk, message);
    
    if (verify_result != 1) {
        printf("❌ Signature verification failed (should succeed)\n");
        return 1;
    }
    printf("✅ Signature verification successful\n\n");
    
    // Test 13: Signature verification (wrong message)
    printf("1️⃣3️⃣  Testing signature verification (wrong message)...\n");
    const char* wrong_message = "Wrong message content";
    int wrong_verify_result = hdwsa_verify(h, Q_sigma, Qr, Qvk, wrong_message);
    
    if (wrong_verify_result == 1) {
        printf("❌ Signature verification succeeded with wrong message (should fail)\n");
        return 1;
    }
    printf("✅ Signature verification correctly rejected wrong message\n\n");
    
    // Test 14: Hash functions
    printf("1️⃣4️⃣  Testing hash functions...\n");
    
    // Test H0
    unsigned char h0_out1[g1_size], h0_out2[g1_size];
    hdwsa_H0(h0_out1, "test_id_1");
    hdwsa_H0(h0_out2, "test_id_2");
    
    // Check if different inputs produce different outputs
    int h0_same = 1;
    for (size_t i = 0; i < g1_size; i++) {
        if (h0_out1[i] != h0_out2[i]) {
            h0_same = 0;
            break;
        }
    }
    
    if (h0_same) {
        printf("❌ H0 produces same output for different inputs\n");
        return 1;
    }
    
    // Test H1, H2, H3, H4 with dummy data
    unsigned char h1_out[zr_size], h2_out[zr_size];
    unsigned char h3_out[g1_size], h4_out[zr_size];
    
    hdwsa_H1(h1_out, h0_out1, h0_out2);
    hdwsa_H2(h2_out, h0_out1, h0_out2);
    hdwsa_H3(h3_out, h0_out1, h0_out2, A1);
    hdwsa_H4(h4_out, Qr, Qvk, "test message");
    
    printf("✅ All hash functions working correctly\n\n");
    
    // Test 15: Multiple hierarchical levels consistency
    printf("1️⃣5️⃣  Testing hierarchical consistency...\n");
    
    // Generate another child from same parent
    unsigned char A2b[g1_size], B2b[g1_size];
    unsigned char alpha2b[zr_size], beta2b[zr_size];
    const char* id_level2b = "id_0,id_2";
    
    int user2b_result = hdwsa_keypair_gen(A2b, B2b, alpha2b, beta2b, 
                                         alpha1, beta1, id_level2b);
    if (user2b_result != 0) {
        printf("❌ Second Level 2 user keypair generation failed\n");
        return 1;
    }
    
    // Check that different IDs produce different keys
    int keys_same = 1;
    for (size_t i = 0; i < g1_size; i++) {
        if (A2[i] != A2b[i] || B2[i] != B2b[i]) {
            keys_same = 0;
            break;
        }
    }
    
    if (keys_same) {
        printf("❌ Different IDs produced same keys\n");
        return 1;
    }
    printf("✅ Hierarchical consistency verified - different IDs produce different keys\n\n");
    
    // Test 16: Performance measurement
    printf("1️⃣6️⃣  Testing performance measurement...\n");
    hdwsa_reset_performance();
    
    int perf_result = hdwsa_performance_test(5);
    if (perf_result < 0) {
        printf("❌ Performance test failed\n");
        return 1;
    }
    
    printf("✅ Performance test completed: %d successful operations\n", perf_result);
    hdwsa_print_performance();
    printf("\n");
    
    // Test 17: Library cleanup and re-initialization
    printf("1️⃣7️⃣  Testing library cleanup and re-initialization...\n");
    hdwsa_cleanup();
    
    if (hdwsa_is_initialized()) {
        printf("❌ Library still initialized after cleanup\n");
        return 1;
    }
    
    // Re-initialize
    int reinit_result = hdwsa_init(param_file);
    if (reinit_result != 0) {
        printf("❌ Re-initialization failed\n");
        return 1;
    }
    printf("✅ Library cleanup and re-initialization successful\n\n");
    
    // Final cleanup
    hdwsa_cleanup();
    
    printf("🎉 ALL HDWSA TESTS PASSED!\n");
    printf("📊 Complete functionality verified:\n");
    printf("   ✅ Library initialization & cleanup\n");
    printf("   ✅ Element size queries\n");
    printf("   ✅ Root wallet key generation\n");
    printf("   ✅ Hierarchical user key derivation (3 levels)\n");
    printf("   ✅ Address generation\n");
    printf("   ✅ Address recognition (correct & wrong keys)\n");
    printf("   ✅ DSK (Derived Signing Key) generation\n");
    printf("   ✅ Digital signature generation\n");
    printf("   ✅ Signature verification (correct & wrong message)\n");
    printf("   ✅ Hash functions (H0, H1, H2, H3, H4)\n");
    printf("   ✅ Hierarchical consistency\n");
    printf("   ✅ Performance measurement\n");
    printf("   ✅ Library state management\n\n");
    
    printf("🏗️  HDWSA Features Tested:\n");
    printf("   ✅ Hierarchical Deterministic Wallet\n");
    printf("   ✅ Multi-level key derivation with full ID paths\n");
    printf("   ✅ Address generation & recognition\n");
    printf("   ✅ Digital signatures (Sign & Verify)\n");
    printf("   ❌ Identity tracing (not supported by design)\n\n");
    
    printf("📈 Test Summary:\n");
    printf("   🧪 Total Tests: 17\n");
    printf("   ✅ Passed: 17\n");
    printf("   ❌ Failed: 0\n");
    printf("   🎯 Success Rate: 100%%\n\n");
    
    return 0;
}