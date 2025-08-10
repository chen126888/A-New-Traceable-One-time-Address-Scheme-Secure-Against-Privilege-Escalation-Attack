#include <stdio.h>
#include "sitaiba_core.h"

int main(int argc, char **argv) {
    if (argc < 2) {
        fprintf(stderr, "Usage: %s <param_file>\n", argv[0]);
        return 1;
    }

    printf("🔍 Debug R2 Core Generation\n");
    printf("============================\n");
    
    // Initialize
    if (sitaiba_init(argv[1]) != 0) {
        printf("❌ Failed to initialize SITAIBA\n");
        return 1;
    }
    
    printf("✅ SITAIBA initialized\n");
    
    pairing_t* pairing = sitaiba_get_pairing();
    if (!pairing) {
        printf("❌ Failed to get pairing\n");
        return 1;
    }
    
    // Generate user keys
    element_t A_r, B_r, a_r, b_r, A_m;
    element_init_G1(A_r, *pairing);
    element_init_G1(B_r, *pairing);
    element_init_Zr(a_r, *pairing);
    element_init_Zr(b_r, *pairing);
    element_init_G1(A_m, *pairing);
    
    sitaiba_keygen(A_r, B_r, a_r, b_r);
    sitaiba_get_tracer_public_key(A_m);
    
    printf("✅ Keys generated\n");
    
    // Test address generation multiple times
    for (int i = 0; i < 3; i++) {
        printf("\n--- Test %d ---\n", i + 1);
        
        element_t Addr, R1, R2;
        element_init_G1(Addr, *pairing);
        element_init_G1(R1, *pairing);
        element_init_G1(R2, *pairing);
        
        // Call core address generation
        sitaiba_addr_gen(Addr, R1, R2, A_r, B_r, A_m);
        
        // Check if R2 is zero
        element_t zero;
        element_init_G1(zero, *pairing);
        element_set0(zero);
        
        int r2_is_zero = (element_cmp(R2, zero) == 0);
        printf("R2 is zero: %s\n", r2_is_zero ? "YES ❌" : "NO ✅");
        
        if (!r2_is_zero) {
            printf("R2 first few bytes: ");
            unsigned char buf[64];
            element_to_bytes(buf, R2);
            for (int j = 0; j < 10; j++) {
                printf("%02x", buf[j]);
            }
            printf("...\n");
        }
        
        // Test conversion to buffer
        unsigned char r2_buf[512];
        memset(r2_buf, 0, 512);
        element_to_bytes(r2_buf, R2);
        
        int buf_all_zero = 1;
        for (int j = 0; j < 64; j++) {
            if (r2_buf[j] != 0) {
                buf_all_zero = 0;
                break;
            }
        }
        printf("Buffer all zero after element_to_bytes: %s\n", buf_all_zero ? "YES ❌" : "NO ✅");
        
        element_clear(Addr);
        element_clear(R1);
        element_clear(R2);
        element_clear(zero);
    }
    
    // Cleanup
    element_clear(A_r); element_clear(B_r); element_clear(a_r); element_clear(b_r);
    element_clear(A_m);
    sitaiba_cleanup();
    
    return 0;
}