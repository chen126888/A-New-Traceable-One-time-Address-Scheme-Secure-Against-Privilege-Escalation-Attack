/****************************************************************************
 * File: python_api.c
 * Desc: Python API implementation for SITAIBA scheme
 *       Provides buffer-based interface for Python integration
 ****************************************************************************/

#include "sitaiba_python_api.h"
#include "sitaiba_core.h"
#include <string.h>

//----------------------------------------------
// Helper Functions
//----------------------------------------------

/**
 * Convert buffer to element (G1)
 */
static void buf_to_element_G1(element_t elem, const unsigned char* buf) {
    pairing_t* pairing = sitaiba_get_pairing();
    if (pairing) {
        element_init_G1(elem, *pairing);
        element_from_bytes(elem, (unsigned char*)buf);
    }
}

/**
 * Convert buffer to element (Zr)
 */
static void buf_to_element_Zr(element_t elem, const unsigned char* buf) {
    pairing_t* pairing = sitaiba_get_pairing();
    if (pairing) {
        element_init_Zr(elem, *pairing);
        element_from_bytes(elem, (unsigned char*)buf);
    }
}

// Removed element_to_buf wrapper - using element_to_bytes directly

//----------------------------------------------
// Python Simple API Implementation
//----------------------------------------------

int sitaiba_init_simple(const char* param_file) {
    return sitaiba_init(param_file);
}

int sitaiba_is_initialized_simple(void) {
    return sitaiba_is_initialized();
}

void sitaiba_cleanup_simple(void) {
    sitaiba_cleanup();
}

void sitaiba_reset_performance_simple(void) {
    sitaiba_reset_performance();
}

int sitaiba_element_size_G1_simple(void) {
    return sitaiba_element_size_G1();
}

int sitaiba_element_size_Zr_simple(void) {
    return sitaiba_element_size_Zr();
}

void sitaiba_keygen_simple(unsigned char* A_buf, unsigned char* B_buf,
                          unsigned char* a_buf, unsigned char* b_buf, int buf_size) {
    if (!sitaiba_is_initialized()) return;
    
    pairing_t* pairing = sitaiba_get_pairing();
    if (!pairing) return;

    element_t A, B, a, b;
    element_init_G1(A, *pairing);
    element_init_G1(B, *pairing);
    element_init_Zr(a, *pairing);
    element_init_Zr(b, *pairing);

    sitaiba_keygen(A, B, a, b);

    element_to_bytes(A_buf, A);
    element_to_bytes(B_buf, B);
    element_to_bytes(a_buf, a);
    element_to_bytes(b_buf, b);

    element_clear(A); element_clear(B); element_clear(a); element_clear(b);
}

void sitaiba_tracer_keygen_simple(unsigned char* A_m_buf, unsigned char* a_m_buf, int buf_size) {
    if (!sitaiba_is_initialized()) return;
    
    pairing_t* pairing = sitaiba_get_pairing();
    if (!pairing) return;

    element_t A_m, a_m;
    element_init_G1(A_m, *pairing);
    element_init_Zr(a_m, *pairing);

    sitaiba_tracer_keygen(A_m, a_m);

    element_to_bytes(A_m_buf, A_m);
    element_to_bytes(a_m_buf, a_m);

    element_clear(A_m); element_clear(a_m);
}

void sitaiba_addr_gen_simple(unsigned char* A_r_buf, unsigned char* B_r_buf, unsigned char* A_m_buf,
                            unsigned char* addr_buf, unsigned char* r1_buf, unsigned char* r2_buf,
                            int buf_size) {
    if (!sitaiba_is_initialized()) return;
    
    pairing_t* pairing = sitaiba_get_pairing();
    if (!pairing) return;

    element_t A_r, B_r, A_m, Addr, R1, R2;
    buf_to_element_G1(A_r, A_r_buf);
    buf_to_element_G1(B_r, B_r_buf);
    
    if (A_m_buf) {
        buf_to_element_G1(A_m, A_m_buf);
    } else {
        // Use internal manager public key
        element_init_G1(A_m, *pairing);
        sitaiba_get_tracer_public_key(A_m);
    }

    element_init_G1(Addr, *pairing);
    element_init_G1(R1, *pairing);
    element_init_G1(R2, *pairing);

    sitaiba_addr_gen(Addr, R1, R2, A_r, B_r, A_m);

    element_to_bytes(addr_buf, Addr);
    element_to_bytes(r1_buf, R1);
    element_to_bytes(r2_buf, R2);

    element_clear(A_r); element_clear(B_r); element_clear(A_m);
    element_clear(Addr); element_clear(R1); element_clear(R2);
}

int sitaiba_addr_recognize_simple(unsigned char* addr_buf, unsigned char* r1_buf, unsigned char* r2_buf,
                                  unsigned char* A_r_buf, unsigned char* B_r_buf, unsigned char* a_r_buf,
                                  unsigned char* A_m_buf) {
    if (!sitaiba_is_initialized()) return 0;
    
    pairing_t* pairing = sitaiba_get_pairing();
    if (!pairing) return 0;

    element_t Addr, R1, R2, A_r, B_r, a_r, A_m;
    buf_to_element_G1(Addr, addr_buf);
    buf_to_element_G1(R1, r1_buf);
    buf_to_element_G1(R2, r2_buf);
    buf_to_element_G1(A_r, A_r_buf);
    buf_to_element_G1(B_r, B_r_buf);
    buf_to_element_Zr(a_r, a_r_buf);
    
    if (A_m_buf) {
        buf_to_element_G1(A_m, A_m_buf);
    } else {
        element_init_G1(A_m, *pairing);
        sitaiba_get_tracer_public_key(A_m);
    }

    int result = sitaiba_addr_recognize(Addr, R1, R2, A_r, B_r, A_m, a_r);

    element_clear(Addr); element_clear(R1); element_clear(R2);
    element_clear(A_r); element_clear(B_r); element_clear(a_r); element_clear(A_m);

    return result;
}

int sitaiba_addr_recognize_fast_simple(unsigned char* r1_buf, unsigned char* r2_buf,
                                       unsigned char* A_r_buf, unsigned char* a_r_buf) {
    if (!sitaiba_is_initialized()) return 0;
    
    element_t R1, R2, A_r, a_r;
    buf_to_element_G1(R1, r1_buf);
    buf_to_element_G1(R2, r2_buf);
    buf_to_element_G1(A_r, A_r_buf);
    buf_to_element_Zr(a_r, a_r_buf);

    int result = sitaiba_addr_recognize_fast(R1, R2, A_r, a_r);

    element_clear(R1); element_clear(R2); element_clear(A_r); element_clear(a_r);

    return result;
}

void sitaiba_onetime_skgen_simple(unsigned char* r1_buf, unsigned char* a_r_buf, unsigned char* b_r_buf,
                                 unsigned char* A_m_buf, unsigned char* dsk_buf, int buf_size) {
    if (!sitaiba_is_initialized()) return;
    
    pairing_t* pairing = sitaiba_get_pairing();
    if (!pairing) return;

    element_t R1, a_r, b_r, A_m, dsk;
    buf_to_element_G1(R1, r1_buf);
    buf_to_element_Zr(a_r, a_r_buf);
    buf_to_element_Zr(b_r, b_r_buf);
    
    if (A_m_buf) {
        buf_to_element_G1(A_m, A_m_buf);
    } else {
        element_init_G1(A_m, *pairing);
        sitaiba_get_tracer_public_key(A_m);
    }

    element_init_Zr(dsk, *pairing);

    sitaiba_onetime_skgen(dsk, R1, a_r, b_r, A_m);

    element_to_bytes(dsk_buf, dsk);

    element_clear(R1); element_clear(a_r); element_clear(b_r);
    element_clear(A_m); element_clear(dsk);
}

void sitaiba_trace_simple(unsigned char* addr_buf, unsigned char* r1_buf, unsigned char* r2_buf,
                         unsigned char* a_m_buf, unsigned char* B_r_buf, int buf_size) {
    if (!sitaiba_is_initialized()) return;
    
    pairing_t* pairing = sitaiba_get_pairing();
    if (!pairing) return;

    element_t Addr, R1, R2, B_r;
    buf_to_element_G1(Addr, addr_buf);
    buf_to_element_G1(R1, r1_buf);
    buf_to_element_G1(R2, r2_buf);
    
    element_init_G1(B_r, *pairing);

    if (a_m_buf) {
        element_t a_m;
        element_init_Zr(a_m, *pairing);
        buf_to_element_Zr(a_m, a_m_buf);
        sitaiba_trace(B_r, Addr, R1, R2, a_m);
        element_clear(a_m);
    } else {
        // Use internal tracer private key
        sitaiba_trace(B_r, Addr, R1, R2, NULL);
    }

    element_to_bytes(B_r_buf, B_r);

    element_clear(Addr); element_clear(R1); element_clear(R2);
    element_clear(B_r);
}

void sitaiba_performance_test_simple(int iterations, double* results) {
    if (!sitaiba_is_initialized() || !results) return;

    sitaiba_reset_performance();
    
    pairing_t* pairing = sitaiba_get_pairing();
    if (!pairing) return;

    // Generate test data
    element_t A_r, B_r, a_r, b_r, A_m, Addr, R1, R2, dsk;
    element_init_G1(A_r, *pairing); element_init_G1(B_r, *pairing);
    element_init_Zr(a_r, *pairing); element_init_Zr(b_r, *pairing);
    element_init_G1(A_m, *pairing); element_init_G1(Addr, *pairing);
    element_init_G1(R1, *pairing); element_init_G1(R2, *pairing);
    element_init_Zr(dsk, *pairing);

    sitaiba_keygen(A_r, B_r, a_r, b_r);
    sitaiba_get_tracer_public_key(A_m);

    // Run performance tests
    for (int i = 0; i < iterations; i++) {
        // Test address generation
        sitaiba_addr_gen(Addr, R1, R2, A_r, B_r, A_m);
        
        // Test address recognition
        sitaiba_addr_recognize(Addr, R1, R2, A_r, B_r, A_m, a_r);
        
        // Test fast recognition  
        sitaiba_addr_recognize_fast(R1, R2, A_r, a_r);
        
        // Test one-time SK generation
        sitaiba_onetime_skgen(dsk, R1, a_r, b_r, A_m);
        
        // Test identity tracing - use NULL to use internal tracer private key
        element_t B_recovered;
        element_init_G1(B_recovered, *pairing);
        sitaiba_trace(B_recovered, Addr, R1, R2, NULL);
        element_clear(B_recovered);
    }

    // Set performance counter manually since core functions don't auto-increment
    extern int perf_counter;
    perf_counter = iterations;
    
    // Get performance results
    sitaiba_performance_t perf;
    sitaiba_get_performance(&perf);
    
    results[0] = perf.addr_gen_avg;
    results[1] = perf.addr_recognize_avg;
    results[2] = perf.fast_recognize_avg;
    results[3] = perf.onetime_sk_avg;
    results[4] = perf.trace_avg;

    // Cleanup
    element_clear(A_r); element_clear(B_r); element_clear(a_r); element_clear(b_r);
    element_clear(A_m); element_clear(Addr); element_clear(R1); element_clear(R2); element_clear(dsk);
}

int sitaiba_get_tracer_public_key_simple(unsigned char* A_m_buf, int buf_size) {
    if (!sitaiba_is_initialized()) return -1;
    
    pairing_t* pairing = sitaiba_get_pairing();
    if (!pairing) return -1;

    element_t A_m;
    element_init_G1(A_m, *pairing);
    
    int result = sitaiba_get_tracer_public_key(A_m);
    if (result == 0) {
        element_to_bytes(A_m_buf, A_m);
    }

    element_clear(A_m);
    return result;
}