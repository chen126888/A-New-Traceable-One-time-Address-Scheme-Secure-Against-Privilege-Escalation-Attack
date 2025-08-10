/****************************************************************************
 * File: python_api.c
 * Desc: Python interface functions implementation
 *       Provides simple byte-based wrappers around core cryptographic functions
 ****************************************************************************/

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "stealth_core.h"
#include "python_api.h"

// Macro to simplify pairing access
#define PAIRING (*stealth_get_pairing())

//----------------------------------------------
// Python Interface Functions Implementation
//----------------------------------------------

/**
 * Python Interface: Generate key pair
 */
void stealth_keygen_simple(unsigned char* A_out, unsigned char* B_out, 
                          unsigned char* a_out, unsigned char* b_out, int buf_size) {
    if (!stealth_is_initialized()) return;
    
    element_t A, B, aZ, bZ;
    element_init_G1(A, PAIRING);
    element_init_G1(B, PAIRING);
    element_init_Zr(aZ, PAIRING);
    element_init_Zr(bZ, PAIRING);
    
    // Call core function
    stealth_keygen(A, B, aZ, bZ);
    
    // Clear buffers first
    memset(A_out, 0, buf_size);
    memset(B_out, 0, buf_size);
    memset(a_out, 0, buf_size);
    memset(b_out, 0, buf_size);
    
    // Serialize to buffers
    element_to_bytes(A_out, A);
    element_to_bytes(B_out, B);
    element_to_bytes(a_out, aZ);
    element_to_bytes(b_out, bZ);
    
    element_clear(A); element_clear(B);
    element_clear(aZ); element_clear(bZ);
}

/**
 * Python Interface: Generate trace key
 */
void stealth_tracekeygen_simple(unsigned char* TK_out, unsigned char* k_out, int buf_size) {
    if (!stealth_is_initialized()) return;
    
    element_t TK, kZ;
    element_init_G1(TK, PAIRING);
    element_init_Zr(kZ, PAIRING);
    
    // Call core function
    stealth_tracekeygen(TK, kZ);
    
    // Clear buffers first
    memset(TK_out, 0, buf_size);
    memset(k_out, 0, buf_size);
    
    // Serialize to buffers
    element_to_bytes(TK_out, TK);
    element_to_bytes(k_out, kZ);
    
    element_clear(TK); element_clear(kZ);
}

/**
 * Python Interface: Generate address
 */
void stealth_addr_gen_simple(const unsigned char* A_bytes, const unsigned char* B_bytes,
                            const unsigned char* TK_bytes,
                            unsigned char* addr_out, unsigned char* r1_out,
                            unsigned char* r2_out, unsigned char* c_out, int buf_size) {
    if (!stealth_is_initialized()) return;
    
    element_t A, B, TK, Addr, R1, R2, C;
    element_init_G1(A, PAIRING);
    element_init_G1(B, PAIRING);
    element_init_G1(TK, PAIRING);
    element_init_G1(Addr, PAIRING);
    element_init_G1(R1, PAIRING);
    element_init_G1(R2, PAIRING);
    element_init_G1(C, PAIRING);
    
    // Deserialize inputs
    element_from_bytes(A, (unsigned char*)A_bytes);
    element_from_bytes(B, (unsigned char*)B_bytes);
    element_from_bytes(TK, (unsigned char*)TK_bytes);
    
    // Call core function
    stealth_addr_gen(Addr, R1, R2, C, A, B, TK);
    
    // Clear output buffers
    memset(addr_out, 0, buf_size);
    memset(r1_out, 0, buf_size);
    memset(r2_out, 0, buf_size);
    memset(c_out, 0, buf_size);
    
    // Serialize outputs
    element_to_bytes(addr_out, Addr);
    element_to_bytes(r1_out, R1);
    element_to_bytes(r2_out, R2);
    element_to_bytes(c_out, C);
    
    element_clear(A); element_clear(B); element_clear(TK);
    element_clear(Addr); element_clear(R1); element_clear(R2); element_clear(C);
}

/**
 * Python Interface: Verify address (fast version)
 */
int stealth_addr_verify_simple(const unsigned char* R1_bytes, const unsigned char* B_bytes,
                              const unsigned char* A_bytes, const unsigned char* C_bytes,
                              const unsigned char* a_bytes) {
    if (!stealth_is_initialized()) return 0;
    
    element_t R1, B, A, C, aZ;
    element_init_G1(R1, PAIRING);
    element_init_G1(B, PAIRING);
    element_init_G1(A, PAIRING);
    element_init_G1(C, PAIRING);
    element_init_Zr(aZ, PAIRING);
    
    // Deserialize inputs
    element_from_bytes(R1, (unsigned char*)R1_bytes);
    element_from_bytes(B, (unsigned char*)B_bytes);
    element_from_bytes(A, (unsigned char*)A_bytes);
    element_from_bytes(C, (unsigned char*)C_bytes);
    element_from_bytes(aZ, (unsigned char*)a_bytes);
    
    // Call core function
    int result = stealth_addr_verify_fast(R1, B, A, C, aZ);
    
    element_clear(R1); element_clear(B); element_clear(A);
    element_clear(C); element_clear(aZ);
    
    return result;
}

/**
 * Python Interface: Generate one-time secret key (DSK)
 */
void stealth_dsk_gen_simple(const unsigned char* addr_bytes, const unsigned char* r1_bytes,
                           const unsigned char* a_bytes, const unsigned char* b_bytes,
                           unsigned char* dsk_out, int buf_size) {
    if (!stealth_is_initialized()) return;
    
    element_t Addr, R1, aZ, bZ, dsk;
    element_init_G1(Addr, PAIRING);
    element_init_G1(R1, PAIRING);
    element_init_Zr(aZ, PAIRING);
    element_init_Zr(bZ, PAIRING);
    element_init_G1(dsk, PAIRING);
    
    // Deserialize inputs
    element_from_bytes(Addr, (unsigned char*)addr_bytes);
    element_from_bytes(R1, (unsigned char*)r1_bytes);
    element_from_bytes(aZ, (unsigned char*)a_bytes);
    element_from_bytes(bZ, (unsigned char*)b_bytes);
    
    // Call core function
    stealth_onetime_skgen(dsk, Addr, R1, aZ, bZ);
    
    // Clear output buffer
    memset(dsk_out, 0, buf_size);
    
    // Serialize output
    element_to_bytes(dsk_out, dsk);
    
    element_clear(Addr); element_clear(R1); element_clear(aZ); element_clear(bZ);
    element_clear(dsk);
}

/**
 * Python Interface: Sign message with DSK
 */
void stealth_sign_with_dsk_simple(const unsigned char* addr_bytes, const unsigned char* dsk_bytes,
                                 const char* message,
                                 unsigned char* q_sigma_out, unsigned char* h_out, int buf_size) {
    if (!stealth_is_initialized()) return;
    
    element_t Addr, dsk, Q_sigma, hZ;
    element_init_G1(Addr, PAIRING);
    element_init_G1(dsk, PAIRING);
    element_init_G1(Q_sigma, PAIRING);
    element_init_Zr(hZ, PAIRING);
    
    // Deserialize inputs
    element_from_bytes(Addr, (unsigned char*)addr_bytes);
    element_from_bytes(dsk, (unsigned char*)dsk_bytes);
    
    // Call core function
    stealth_sign(Q_sigma, hZ, Addr, dsk, message);
    
    // Clear output buffers
    memset(q_sigma_out, 0, buf_size);
    memset(h_out, 0, buf_size);
    
    // Serialize outputs
    element_to_bytes(q_sigma_out, Q_sigma);
    element_to_bytes(h_out, hZ);
    
    element_clear(Addr); element_clear(dsk);
    element_clear(Q_sigma); element_clear(hZ);
}

/**
 * Python Interface: Sign message (original version)
 */
void stealth_sign_simple(const unsigned char* addr_bytes, const unsigned char* r1_bytes,
                        const unsigned char* a_bytes, const unsigned char* b_bytes,
                        const char* message,
                        unsigned char* q_sigma_out, unsigned char* h_out, 
                        unsigned char* dsk_out, int buf_size) {
    if (!stealth_is_initialized()) return;
    
    element_t Addr, R1, aZ, bZ, dsk, Q_sigma, hZ;
    element_init_G1(Addr, PAIRING);
    element_init_G1(R1, PAIRING);
    element_init_Zr(aZ, PAIRING);
    element_init_Zr(bZ, PAIRING);
    element_init_G1(dsk, PAIRING);
    element_init_G1(Q_sigma, PAIRING);
    element_init_Zr(hZ, PAIRING);
    
    // Deserialize inputs
    element_from_bytes(Addr, (unsigned char*)addr_bytes);
    element_from_bytes(R1, (unsigned char*)r1_bytes);
    element_from_bytes(aZ, (unsigned char*)a_bytes);
    element_from_bytes(bZ, (unsigned char*)b_bytes);
    
    // Generate one-time secret key
    stealth_onetime_skgen(dsk, Addr, R1, aZ, bZ);
    
    // Sign the message
    stealth_sign(Q_sigma, hZ, Addr, dsk, message);
    
    // Clear output buffers
    memset(q_sigma_out, 0, buf_size);
    memset(h_out, 0, buf_size);
    memset(dsk_out, 0, buf_size);
    
    // Serialize outputs
    element_to_bytes(q_sigma_out, Q_sigma);
    element_to_bytes(h_out, hZ);
    element_to_bytes(dsk_out, dsk);
    
    element_clear(Addr); element_clear(R1); element_clear(aZ); element_clear(bZ);
    element_clear(dsk); element_clear(Q_sigma); element_clear(hZ);
}

/**
 * Python Interface: Verify signature
 */
int stealth_verify_simple(const unsigned char* addr_bytes, const unsigned char* r2_bytes,
                         const unsigned char* c_bytes, const char* message,
                         const unsigned char* h_bytes, const unsigned char* q_sigma_bytes) {
    if (!stealth_is_initialized()) return 0;
    
    element_t Addr, R2, C, hZ, Q_sigma;
    element_init_G1(Addr, PAIRING);
    element_init_G1(R2, PAIRING);
    element_init_G1(C, PAIRING);
    element_init_Zr(hZ, PAIRING);
    element_init_G1(Q_sigma, PAIRING);
    
    // Deserialize inputs
    element_from_bytes(Addr, (unsigned char*)addr_bytes);
    element_from_bytes(R2, (unsigned char*)r2_bytes);
    element_from_bytes(C, (unsigned char*)c_bytes);
    element_from_bytes(hZ, (unsigned char*)h_bytes);
    element_from_bytes(Q_sigma, (unsigned char*)q_sigma_bytes);
    
    // Call core function
    int result = stealth_verify(Addr, R2, C, message, hZ, Q_sigma);
    
    element_clear(Addr); element_clear(R2); element_clear(C);
    element_clear(hZ); element_clear(Q_sigma);
    
    return result;
}

/**
 * Python Interface: Trace identity
 */
void stealth_trace_simple(const unsigned char* addr_bytes, const unsigned char* r1_bytes,
                         const unsigned char* r2_bytes, const unsigned char* c_bytes,
                         const unsigned char* k_bytes,
                         unsigned char* b_recovered_out, int buf_size) {
    if (!stealth_is_initialized()) return;
    
    element_t Addr, R1, R2, C, kZ, B_recovered;
    element_init_G1(Addr, PAIRING);
    element_init_G1(R1, PAIRING);
    element_init_G1(R2, PAIRING);
    element_init_G1(C, PAIRING);
    element_init_Zr(kZ, PAIRING);
    element_init_G1(B_recovered, PAIRING);
    
    // Deserialize inputs
    element_from_bytes(Addr, (unsigned char*)addr_bytes);
    element_from_bytes(R1, (unsigned char*)r1_bytes);
    element_from_bytes(R2, (unsigned char*)r2_bytes);
    element_from_bytes(C, (unsigned char*)c_bytes);
    element_from_bytes(kZ, (unsigned char*)k_bytes);
    
    // Call core function
    stealth_trace(B_recovered, Addr, R1, R2, C, kZ);
    
    // Clear output buffer
    memset(b_recovered_out, 0, buf_size);
    
    // Serialize output
    element_to_bytes(b_recovered_out, B_recovered);
    
    element_clear(Addr); element_clear(R1); element_clear(R2);
    element_clear(C); element_clear(kZ); element_clear(B_recovered);
}

/**
 * Python Interface: Performance test
 */
void stealth_performance_test_simple(int iterations, double* results) {
    if (!stealth_is_initialized() || !results) return;
    
    stealth_reset_performance();
    
    // Generate test keys once
    element_t A, B, a, b, TK, k;
    element_init_G1(A, PAIRING);
    element_init_G1(B, PAIRING);
    element_init_Zr(a, PAIRING);
    element_init_Zr(b, PAIRING);
    element_init_G1(TK, PAIRING);
    element_init_Zr(k, PAIRING);
    
    stealth_keygen(A, B, a, b);
    stealth_tracekeygen(TK, k);
    
    // Run performance test
    for(int i = 0; i < iterations; i++) {
        element_t Addr, R1, R2, C, dsk, Q_sigma, hZ;
        element_init_G1(Addr, PAIRING);
        element_init_G1(R1, PAIRING);
        element_init_G1(R2, PAIRING);
        element_init_G1(C, PAIRING);
        element_init_G1(dsk, PAIRING);
        element_init_G1(Q_sigma, PAIRING);
        element_init_Zr(hZ, PAIRING);
        
        // Test all operations
        stealth_addr_gen(Addr, R1, R2, C, A, B, TK);
        stealth_addr_verify_fast(R1, B, A, C, a);
        stealth_onetime_skgen(dsk, Addr, R1, a, b);
        stealth_sign(Q_sigma, hZ, Addr, dsk, "Test message");
        stealth_verify(Addr, R2, C, "Test message", hZ, Q_sigma);
        
        element_t B_recovered;
        element_init_G1(B_recovered, PAIRING);
        stealth_trace(B_recovered, Addr, R1, R2, C, k);
        element_clear(B_recovered);
        
        element_clear(Addr); element_clear(R1); element_clear(R2); element_clear(C);
        element_clear(dsk); element_clear(Q_sigma); element_clear(hZ);
    }
    
    // Get performance results
    stealth_performance_t perf;
    stealth_get_performance(&perf);
    
    // Return results array
    results[0] = perf.addr_gen_avg;
    results[1] = perf.addr_verify_avg;
    results[2] = perf.fast_verify_avg;
    results[3] = perf.onetime_sk_avg;
    results[4] = perf.sign_avg;
    results[5] = perf.verify_avg;
    results[6] = perf.trace_avg;
    
    element_clear(A); element_clear(B); element_clear(a); element_clear(b);
    element_clear(TK); element_clear(k);
}