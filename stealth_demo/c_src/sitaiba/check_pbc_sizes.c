#include <stdio.h>
#include "sitaiba_core.h"

int main(int argc, char **argv) {
    if (argc < 2) {
        fprintf(stderr, "Usage: %s <param_file>\n", argv[0]);
        return 1;
    }

    printf("🔍 Checking PBC Parameter Sizes for %s\n", argv[1]);
    printf("======================================\n");
    
    // Initialize
    if (sitaiba_init(argv[1]) != 0) {
        printf("❌ Failed to initialize SITAIBA with %s\n", argv[1]);
        return 1;
    }
    
    printf("✅ SITAIBA initialized with %s\n", argv[1]);
    
    pairing_t* pairing = sitaiba_get_pairing();
    if (!pairing) {
        printf("❌ Failed to get pairing\n");
        return 1;
    }
    
    // Create sample elements to check sizes
    element_t g1_elem, zr_elem;
    element_init_G1(g1_elem, *pairing);
    element_init_Zr(zr_elem, *pairing);
    
    // Set random values
    element_random(g1_elem);
    element_random(zr_elem);
    
    // Check element_length_in_bytes
    int g1_size = element_length_in_bytes(g1_elem);
    int zr_size = element_length_in_bytes(zr_elem);
    
    printf("📏 Element sizes (element_length_in_bytes):\n");
    printf("   G1 size: %d bytes\n", g1_size);
    printf("   Zr size: %d bytes\n", zr_size);
    
    // Check compressed sizes if available
    int g1_compressed = element_length_in_bytes_compressed(g1_elem);
    printf("   G1 compressed: %d bytes\n", g1_compressed);
    
    // Check our library functions
    int lib_g1_size = sitaiba_element_size_G1();
    int lib_zr_size = sitaiba_element_size_Zr();
    
    printf("📚 Library reported sizes:\n");
    printf("   Library G1 size: %d bytes\n", lib_g1_size);
    printf("   Library Zr size: %d bytes\n", lib_zr_size);
    
    // Test serialization
    printf("\n🧪 Testing serialization:\n");
    unsigned char g1_buf[1024], zr_buf[1024];
    
    element_to_bytes(g1_buf, g1_elem);
    element_to_bytes(zr_buf, zr_elem);
    
    printf("   G1 first 10 bytes: ");
    for (int i = 0; i < 10 && i < g1_size; i++) {
        printf("%02x ", g1_buf[i]);
    }
    printf("\n");
    
    printf("   Zr first 10 bytes: ");
    for (int i = 0; i < 10 && i < zr_size; i++) {
        printf("%02x ", zr_buf[i]);
    }
    printf("\n");
    
    // Test deserialization
    element_t g1_test, zr_test;
    element_init_G1(g1_test, *pairing);
    element_init_Zr(zr_test, *pairing);
    
    element_from_bytes(g1_test, g1_buf);
    element_from_bytes(zr_test, zr_buf);
    
    int g1_equal = (element_cmp(g1_elem, g1_test) == 0);
    int zr_equal = (element_cmp(zr_elem, zr_test) == 0);
    
    printf("🔄 Serialization roundtrip test:\n");
    printf("   G1 roundtrip: %s\n", g1_equal ? "✅ SUCCESS" : "❌ FAILED");
    printf("   Zr roundtrip: %s\n", zr_equal ? "✅ SUCCESS" : "❌ FAILED");
    
    // Check if our 512 byte buffer is sufficient
    int max_needed = (g1_size > zr_size) ? g1_size : zr_size;
    printf("\n📦 Buffer size analysis:\n");
    printf("   Maximum needed: %d bytes\n", max_needed);
    printf("   Current buffer (512): %s\n", max_needed <= 512 ? "✅ SUFFICIENT" : "❌ TOO SMALL");
    
    if (max_needed > 512) {
        printf("⚠️ WARNING: Current 512-byte buffer is too small!\n");
        printf("   Recommend buffer size: %d bytes\n", ((max_needed + 63) / 64) * 64); // Round up to 64
    }
    
    // Cleanup
    element_clear(g1_elem); element_clear(zr_elem);
    element_clear(g1_test); element_clear(zr_test);
    sitaiba_cleanup();
    
    return 0;
}