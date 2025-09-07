/****************************************************************************
 * File: hdwsa_python_api.c
 * Desc: Python API implementation for HDWSA scheme
 *       Simplified wrapper functions for Python integration
 ****************************************************************************/

#include "hdwsa_python_api.h"
#include "hdwsa_core.h"
#include <stdio.h>
#include <string.h>

//----------------------------------------------
// Library Management Functions
//----------------------------------------------

int hdwsa_init_simple(const char* param_file) {
    return hdwsa_init(param_file);
}

int hdwsa_is_initialized_simple(void) {
    return hdwsa_is_initialized();
}

void hdwsa_cleanup_simple(void) {
    hdwsa_cleanup();
}

void hdwsa_reset_performance_simple(void) {
    hdwsa_reset_performance();
}

int hdwsa_element_size_G1_simple(void) {
    if (!hdwsa_is_initialized()) {
        return -1;
    }
    size_t g1_size, zr_size;
    hdwsa_get_element_sizes(&g1_size, &zr_size);
    return (int)g1_size;
}

int hdwsa_element_size_Zr_simple(void) {
    if (!hdwsa_is_initialized()) {
        return -1;
    }
    size_t g1_size, zr_size;
    hdwsa_get_element_sizes(&g1_size, &zr_size);
    return (int)zr_size;
}

int hdwsa_element_size_GT_simple(void) {
    if (!hdwsa_is_initialized()) {
        return -1;
    }
    // GT size is typically larger than G1, estimated as 12 * G1 size for most curves
    // This should be properly implemented when pairing is initialized
    return hdwsa_element_size_G1_simple() * 12;
}

//----------------------------------------------
// Root System Functions
//----------------------------------------------

int hdwsa_root_keygen_simple(unsigned char* A_out, unsigned char* B_out,
                            unsigned char* alpha_out, unsigned char* beta_out) {
    if (!hdwsa_is_initialized()) {
        return -1;
    }
    
    return hdwsa_root_keygen(A_out, B_out, alpha_out, beta_out);
}

//----------------------------------------------
// Key Management Functions
//----------------------------------------------

int hdwsa_keypair_gen_simple(unsigned char* A2_out, unsigned char* B2_out,
                            unsigned char* alpha2_out, unsigned char* beta2_out,
                            const unsigned char* alpha1_in, const unsigned char* beta1_in,
                            const char* full_id) {
    if (!hdwsa_is_initialized()) {
        return -1;
    }
    
    return hdwsa_keypair_gen(A2_out, B2_out, alpha2_out, beta2_out,
                            alpha1_in, beta1_in, full_id);
}

//----------------------------------------------
// Address Functions
//----------------------------------------------

int hdwsa_addr_gen_simple(unsigned char* Qr_out, unsigned char* Qvk_out,
                         const unsigned char* A_in, const unsigned char* B_in) {
    if (!hdwsa_is_initialized()) {
        return -1;
    }
    
    return hdwsa_addr_gen(Qr_out, Qvk_out, A_in, B_in);
}

int hdwsa_addr_recognize_simple(const unsigned char* Qvk_in, const unsigned char* Qr_in,
                               const unsigned char* A_in, const unsigned char* B_in,
                               const unsigned char* beta_in) {
    if (!hdwsa_is_initialized()) {
        return 0;
    }
    
    return hdwsa_addr_recognize(Qvk_in, Qr_in, A_in, B_in, beta_in);
}

//----------------------------------------------
// DSK Functions
//----------------------------------------------

int hdwsa_dsk_gen_simple(unsigned char* dsk_out,
                        const unsigned char* Qr_in, const unsigned char* B_in,
                        const unsigned char* alpha_in, const unsigned char* beta_in) {
    if (!hdwsa_is_initialized()) {
        return -1;
    }
    
    return hdwsa_dsk_gen(dsk_out, Qr_in, B_in, alpha_in, beta_in);
}

//----------------------------------------------
// Signature Functions
//----------------------------------------------

int hdwsa_sign_simple(unsigned char* h_out, unsigned char* Q_sigma_out,
                     const unsigned char* dsk_in,
                     const unsigned char* Qr_in, const unsigned char* Qvk_in,
                     const char* msg) {
    if (!hdwsa_is_initialized()) {
        return -1;
    }
    
    return hdwsa_sign(h_out, Q_sigma_out, dsk_in, Qr_in, Qvk_in, msg);
}

int hdwsa_verify_simple(const unsigned char* h_in, const unsigned char* Q_sigma_in,
                       const unsigned char* Qr_in, const unsigned char* Qvk_in,
                       const char* msg) {
    if (!hdwsa_is_initialized()) {
        return 0;
    }
    
    return hdwsa_verify(h_in, Q_sigma_in, Qr_in, Qvk_in, msg);
}

//----------------------------------------------
// Performance Testing
//----------------------------------------------

int hdwsa_performance_test_simple(int iterations) {
    if (!hdwsa_is_initialized()) {
        return -1;
    }
    
    return hdwsa_performance_test(iterations);
}

void hdwsa_print_performance_simple(void) {
    if (hdwsa_is_initialized()) {
        hdwsa_print_performance();
    }
}

int hdwsa_get_performance_string_simple(char* output, int buffer_size) {
    if (!hdwsa_is_initialized() || !output || buffer_size <= 0) {
        return -1;
    }
    
    hdwsa_performance_t* perf = hdwsa_get_performance();
    if (!perf) {
        return -1;
    }
    
    int written = snprintf(output, buffer_size,
        "HDWSA Performance Statistics:\n"
        "Total Operations: %d\n"
        "Root KeyGen: %.3f ms\n"
        "User KeyGen: %.3f ms\n"
        "Address Generation: %.3f ms\n"
        "Address Recognition: %.3f ms\n"
        "DSK Generation: %.3f ms\n"
        "Sign: %.3f ms\n"
        "Verify: %.3f ms\n"
        "Hash Functions:\n"
        "  H0 (ID->G1): %.3f ms\n"
        "  H1 (G1×G1->Zr): %.3f ms\n"
        "  H2 (G1×G1->Zr): %.3f ms\n"
        "  H3 (G1×G1×G1->G1): %.3f ms\n"
        "  H4 (Signature): %.3f ms\n",
        perf->operation_count,
        perf->root_keygen_avg,
        perf->keypair_gen_avg,
        perf->addr_gen_avg,
        perf->addr_recognize_avg,
        perf->dsk_gen_avg,
        perf->sign_avg,
        perf->verify_avg,
        perf->h0_avg,
        perf->h1_avg,
        perf->h2_avg,
        perf->h3_avg,
        perf->h4_avg
    );
    
    return (written >= buffer_size) ? -1 : 0;
}