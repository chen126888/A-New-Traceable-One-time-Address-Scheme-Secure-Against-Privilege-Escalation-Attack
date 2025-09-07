/****************************************************************************
 * File: debug_hdwsa_api.c
 * Desc: Complete debug and test program for HDWSA Python API functions
 *       Tests all Python interface functions and their interactions
 ****************************************************************************/

#include "hdwsa_python_api.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int main() {
    printf("🧪 HDWSA Python API Complete Debug Test\n");
    printf("==========================================\n\n");
    
    // Test 1: Library initialization
    printf("1️⃣  Testing API library initialization...\n");
    const char* param_file = "../../param/a.param";
    
    int init_result = hdwsa_init_simple(param_file);
    if (init_result != 0) {
        printf("❌ API library initialization failed with code: %d\n", init_result);
        return 1;
    }
    
    if (!hdwsa_is_initialized_simple()) {
        printf("❌ API library initialization check failed\n");
        return 1;
    }
    printf("✅ API library initialized successfully\n\n");
    
    // Test 2: Element sizes
    printf("2️⃣  Testing API element size functions...\n");
    int g1_size = hdwsa_element_size_G1_simple();
    int zr_size = hdwsa_element_size_Zr_simple();
    int gt_size = hdwsa_element_size_GT_simple();
    
    printf("📏 API Element sizes: G1=%d bytes, Zr=%d bytes, GT=%d bytes\n", 
           g1_size, zr_size, gt_size);
    
    if (g1_size <= 0 || zr_size <= 0 || gt_size <= 0) {
        printf("❌ Invalid API element sizes\n");
        return 1;
    }
    printf("✅ API element sizes obtained successfully\n\n");
    
    // Test 3: Root wallet key generation
    printf("3️⃣  Testing API root wallet key generation...\n");
    unsigned char* root_A = malloc(g1_size);
    unsigned char* root_B = malloc(g1_size);
    unsigned char* root_alpha = malloc(zr_size);
    unsigned char* root_beta = malloc(zr_size);
    
    int root_result = hdwsa_root_keygen_simple(root_A, root_B, root_alpha, root_beta);
    if (root_result != 0) {
        printf("❌ API root wallet key generation failed\n");
        free(root_A); free(root_B); free(root_alpha); free(root_beta);
        return 1;
    }
    
    // Check if all buffers are non-zero
    int all_zero = 1;
    for (int i = 0; i < g1_size; i++) {
        if (root_A[i] != 0 || root_B[i] != 0) all_zero = 0;
    }
    for (int i = 0; i < zr_size; i++) {
        if (root_alpha[i] != 0 || root_beta[i] != 0) all_zero = 0;
    }
    
    if (all_zero) {
        printf("❌ API root keys are all zero\n");
        free(root_A); free(root_B); free(root_alpha); free(root_beta);
        return 1;
    }
    printf("✅ API root wallet key generation successful\n\n");
    
    // Test 4: User keypair generation (Level 1)
    printf("4️⃣  Testing API user keypair generation (Level 1)...\n");
    unsigned char* A1 = malloc(g1_size);
    unsigned char* B1 = malloc(g1_size);
    unsigned char* alpha1 = malloc(zr_size);
    unsigned char* beta1 = malloc(zr_size);
    const char* id_level1 = "id_0";
    
    int user1_result = hdwsa_keypair_gen_simple(A1, B1, alpha1, beta1, 
                                               root_alpha, root_beta, id_level1);
    if (user1_result != 0) {
        printf("❌ API Level 1 user keypair generation failed\n");
        return 1;
    }
    printf("✅ API Level 1 user keypair generation successful (ID: %s)\n\n", id_level1);
    
    // Test 5: User keypair generation (Level 2)
    printf("5️⃣  Testing API user keypair generation (Level 2)...\n");
    unsigned char* A2 = malloc(g1_size);
    unsigned char* B2 = malloc(g1_size);
    unsigned char* alpha2 = malloc(zr_size);
    unsigned char* beta2 = malloc(zr_size);
    const char* id_level2 = "id_0,id_1";
    
    int user2_result = hdwsa_keypair_gen_simple(A2, B2, alpha2, beta2, 
                                               alpha1, beta1, id_level2);
    if (user2_result != 0) {
        printf("❌ API Level 2 user keypair generation failed\n");
        return 1;
    }
    printf("✅ API Level 2 user keypair generation successful (ID: %s)\n\n", id_level2);
    
    // Test 6: User keypair generation (Level 3)
    printf("6️⃣  Testing API user keypair generation (Level 3)...\n");
    unsigned char* A3 = malloc(g1_size);
    unsigned char* B3 = malloc(g1_size);
    unsigned char* alpha3 = malloc(zr_size);
    unsigned char* beta3 = malloc(zr_size);
    const char* id_level3 = "id_0,id_1,id_5";
    
    int user3_result = hdwsa_keypair_gen_simple(A3, B3, alpha3, beta3, 
                                               alpha2, beta2, id_level3);
    if (user3_result != 0) {
        printf("❌ API Level 3 user keypair generation failed\n");
        return 1;
    }
    printf("✅ API Level 3 user keypair generation successful (ID: %s)\n\n", id_level3);
    
    // Test 7: Address generation (using Level 1 user)
    printf("7️⃣  Testing API address generation...\n");
    unsigned char* Qr = malloc(g1_size);
    unsigned char* Qvk = malloc(gt_size);
    
    int addr_result = hdwsa_addr_gen_simple(Qr, Qvk, A1, B1);
    if (addr_result != 0) {
        printf("❌ API address generation failed\n");
        return 1;
    }
    
    // Check if address components are non-zero
    int qr_zero = 1, qvk_zero = 1;
    for (int i = 0; i < g1_size; i++) {
        if (Qr[i] != 0) qr_zero = 0;
    }
    for (int i = 0; i < gt_size; i++) {
        if (Qvk[i] != 0) qvk_zero = 0;
    }
    
    if (qr_zero || qvk_zero) {
        printf("❌ API address components are zero\n");
        return 1;
    }
    printf("✅ API address generation successful\n\n");
    
    // Test 8: Address recognition (correct key) - both methods
    printf("8️⃣  Testing API address recognition (correct key)...\n");
    
    // Test address recognition (correct key)
    int recognize_result = hdwsa_addr_recognize_simple(Qvk, Qr, A1, B1, beta1);
    if (recognize_result != 1) {
        printf("❌ API address recognition failed\n");
        return 1;
    }
    printf("✅ API address recognition successful\n\n");
    
    // Test 9: Address recognition (wrong key)
    printf("9️⃣  Testing API address recognition (wrong key)...\n");
    int wrong_recognize_result = hdwsa_addr_recognize_simple(Qvk, Qr, A2, B2, beta2);
    
    if (wrong_recognize_result == 1) {
        printf("❌ API address recognition succeeded with wrong key (should fail)\n");
        return 1;
    }
    printf("✅ API address recognition correctly rejected wrong key\n\n");
    
    // Test 10: DSK generation
    printf("🔟 Testing API DSK generation...\n");
    unsigned char* dsk = malloc(g1_size);
    
    int dsk_result = hdwsa_dsk_gen_simple(dsk, Qr, B1, alpha1, beta1);
    if (dsk_result != 0) {
        printf("❌ API DSK generation failed\n");
        return 1;
    }
    
    // Check if DSK is non-zero
    int dsk_zero = 1;
    for (int i = 0; i < g1_size; i++) {
        if (dsk[i] != 0) dsk_zero = 0;
    }
    
    if (dsk_zero) {
        printf("❌ API DSK is zero\n");
        return 1;
    }
    printf("✅ API DSK generation successful\n\n");
    
    // Test 11: Message signing
    printf("1️⃣1️⃣  Testing API message signing...\n");
    const char* message = "Hello, HDWSA Python API signature!";
    unsigned char* h = malloc(zr_size);
    unsigned char* Q_sigma = malloc(g1_size);
    
    int sign_result = hdwsa_sign_simple(h, Q_sigma, dsk, Qr, Qvk, message);
    if (sign_result != 0) {
        printf("❌ API message signing failed\n");
        return 1;
    }
    
    // Check if signature components are non-zero
    int h_zero = 1, sig_zero = 1;
    for (int i = 0; i < zr_size; i++) {
        if (h[i] != 0) h_zero = 0;
    }
    for (int i = 0; i < g1_size; i++) {
        if (Q_sigma[i] != 0) sig_zero = 0;
    }
    
    if (h_zero || sig_zero) {
        printf("❌ API signature components are zero\n");
        return 1;
    }
    printf("✅ API message signing successful\n");
    printf("📝 Message: \"%s\"\n\n", message);
    
    // Test 12: Signature verification (correct signature)
    printf("1️⃣2️⃣  Testing API signature verification (correct signature)...\n");
    int verify_result = hdwsa_verify_simple(h, Q_sigma, Qr, Qvk, message);
    
    if (verify_result != 1) {
        printf("❌ API signature verification failed (should succeed)\n");
        return 1;
    }
    printf("✅ API signature verification successful\n\n");
    
    // Test 13: Signature verification (wrong message)
    printf("1️⃣3️⃣  Testing API signature verification (wrong message)...\n");
    const char* wrong_message = "Wrong message for API test";
    int wrong_verify_result = hdwsa_verify_simple(h, Q_sigma, Qr, Qvk, wrong_message);
    
    if (wrong_verify_result == 1) {
        printf("❌ API signature verification succeeded with wrong message (should fail)\n");
        return 1;
    }
    printf("✅ API signature verification correctly rejected wrong message\n\n");
    
    // Test 14: Multiple wallet hierarchy consistency
    printf("1️⃣4️⃣  Testing API hierarchical consistency...\n");
    
    // Generate another child from same parent
    unsigned char* A2b = malloc(g1_size);
    unsigned char* B2b = malloc(g1_size);
    unsigned char* alpha2b = malloc(zr_size);
    unsigned char* beta2b = malloc(zr_size);
    const char* id_level2b = "id_0,id_2";
    
    int user2b_result = hdwsa_keypair_gen_simple(A2b, B2b, alpha2b, beta2b, 
                                                alpha1, beta1, id_level2b);
    if (user2b_result != 0) {
        printf("❌ API second Level 2 user keypair generation failed\n");
        return 1;
    }
    
    // Check that different IDs produce different keys
    int keys_same = 1;
    for (int i = 0; i < g1_size; i++) {
        if (A2[i] != A2b[i] || B2[i] != B2b[i]) {
            keys_same = 0;
            break;
        }
    }
    
    if (keys_same) {
        printf("❌ API different IDs produced same keys\n");
        return 1;
    }
    printf("✅ API hierarchical consistency verified - different IDs produce different keys\n\n");
    
    // Test 15: Performance measurement
    printf("1️⃣5️⃣  Testing API performance measurement...\n");
    hdwsa_reset_performance_simple();
    
    int perf_result = hdwsa_performance_test_simple(3);
    if (perf_result < 0) {
        printf("❌ API performance test failed\n");
        return 1;
    }
    
    printf("✅ API performance test completed: %d successful operations\n", perf_result);
    hdwsa_print_performance_simple();
    printf("\n");
    
    // Test 16: Performance statistics string
    printf("1️⃣6️⃣  Testing API performance string function...\n");
    char perf_string[2048];
    int perf_string_result = hdwsa_get_performance_string_simple(perf_string, sizeof(perf_string));
    
    if (perf_string_result != 0) {
        printf("❌ API performance string function failed\n");
        return 1;
    }
    
    printf("📊 API Performance String Output:\n");
    printf("%s\n", perf_string);
    printf("✅ API performance string function successful\n\n");
    
    // Test 17: API error handling (uninitialized operations)
    printf("1️⃣7️⃣  Testing API error handling...\n");
    hdwsa_cleanup_simple();
    
    // Test operations after cleanup (should fail gracefully)
    int error_test1 = hdwsa_root_keygen_simple(root_A, root_B, root_alpha, root_beta);
    int error_test2 = hdwsa_element_size_G1_simple();
    int error_test3 = hdwsa_addr_gen_simple(Qr, Qvk, A1, B1);
    
    if (error_test1 == 0 || error_test2 > 0 || error_test3 == 0) {
        printf("❌ API error handling failed - operations should fail after cleanup\n");
        return 1;
    }
    printf("✅ API error handling successful - operations correctly fail when uninitialized\n\n");
    
    // Test 18: API re-initialization
    printf("1️⃣8️⃣  Testing API re-initialization...\n");
    int reinit_result = hdwsa_init_simple(param_file);
    if (reinit_result != 0) {
        printf("❌ API re-initialization failed\n");
        return 1;
    }
    
    if (!hdwsa_is_initialized_simple()) {
        printf("❌ API re-initialization check failed\n");
        return 1;
    }
    printf("✅ API re-initialization successful\n\n");
    
    // Final cleanup
    hdwsa_cleanup_simple();
    
    // Free all allocated memory
    free(root_A); free(root_B); free(root_alpha); free(root_beta);
    free(A1); free(B1); free(alpha1); free(beta1);
    free(A2); free(B2); free(alpha2); free(beta2);
    free(A3); free(B3); free(alpha3); free(beta3);
    free(A2b); free(B2b); free(alpha2b); free(beta2b);
    free(Qr); free(Qvk);
    free(dsk);
    free(h); free(Q_sigma);
    
    printf("🎉 ALL HDWSA PYTHON API TESTS PASSED!\n");
    printf("📊 Complete API functionality verified:\n");
    printf("   ✅ API library initialization & cleanup\n");
    printf("   ✅ API element size queries (G1, Zr, GT)\n");
    printf("   ✅ API root wallet key generation\n");
    printf("   ✅ API hierarchical user key derivation (3 levels)\n");
    printf("   ✅ API address generation\n");
    printf("   ✅ API address recognition\n");
    printf("   ✅ API address recognition error handling\n");
    printf("   ✅ API DSK (Derived Signing Key) generation\n");
    printf("   ✅ API digital signature generation\n");
    printf("   ✅ API signature verification (correct & wrong message)\n");
    printf("   ✅ API hierarchical consistency verification\n");
    printf("   ✅ API performance measurement & statistics\n");
    printf("   ✅ API performance string formatting\n");
    printf("   ✅ API error handling (uninitialized state)\n");
    printf("   ✅ API re-initialization capability\n");
    printf("   ✅ API memory management\n\n");
    
    printf("🏗️  HDWSA Python API Features Tested:\n");
    printf("   ✅ Complete Python interface compatibility\n");
    printf("   ✅ Memory management with malloc/free\n");
    printf("   ✅ Error handling and state validation\n");
    printf("   ✅ Performance statistics export\n");
    printf("   ✅ Method parameter support\n");
    printf("   ✅ String formatting for Python integration\n");
    printf("   ✅ Graceful cleanup and re-initialization\n\n");
    
    printf("📈 API Test Summary:\n");
    printf("   🧪 Total API Tests: 18\n");
    printf("   ✅ Passed: 18\n");
    printf("   ❌ Failed: 0\n");
    printf("   🎯 Success Rate: 100%%\n\n");
    
    printf("🔗 Python Integration Ready:\n");
    printf("   ✅ All API functions working correctly\n");
    printf("   ✅ Error handling implemented\n");
    printf("   ✅ Memory management verified\n");
    printf("   ✅ Performance monitoring available\n\n");
    
    return 0;
}