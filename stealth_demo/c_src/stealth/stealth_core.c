/****************************************************************************
 * File: stealth_core.c
 * Desc: Core cryptographic functions for Traceable Anonymous Transaction Scheme
 *       Contains only the essential cryptographic algorithms
 ****************************************************************************/

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <pbc/pbc.h>
#include <pbc/pbc_test.h>
#include <openssl/sha.h>
#include <time.h>
#include "stealth_core.h"

// Global state for the library
static pairing_t pairing;
static element_t g;
static int library_initialized = 0;

// Performance tracking
static double sumAddrGen=0, sumAddrRecognize=0, sumFastAddrRecognize=0, sumOnetimeSK=0,
              sumSign=0, sumVerify=0, sumTrace=0;
int perf_counter = 0;

//----------------------------------------------
// Timer helper
//----------------------------------------------
double timer_diff(clock_t start, clock_t end) {
    return ((double)(end - start)) / CLOCKS_PER_SEC * 1000.0; // in ms
}

//----------------------------------------------
// hash_to_mpz: do sha256 -> mpz mod r
//----------------------------------------------
void hash_to_mpz(mpz_t out, const unsigned char *data, size_t len, mpz_t mod) {
    unsigned char hash[SHA256_DIGEST_LENGTH];
    SHA256(data, len, hash);
    mpz_import(out, SHA256_DIGEST_LENGTH, 1, 1, 0, 0, hash);
    mpz_mod(out, out, mod);
}

//----------------------------------------------
// Hash functions H1, H2, H3, H4
//----------------------------------------------
void H1(element_t outZr, element_t inG1) {
    unsigned char buf[1024];
    size_t len = element_length_in_bytes(inG1);
    element_to_bytes(buf, inG1);

    mpz_t tmpz; mpz_init(tmpz);
    hash_to_mpz(tmpz, buf, len, pairing->r);

    element_set_mpz(outZr, tmpz);
    mpz_clear(tmpz);
}

void H2(element_t outG1, element_t inAny) {
    unsigned char buf[1024];
    size_t len = element_length_in_bytes(inAny);
    element_to_bytes(buf, inAny);

    mpz_t tmpz; mpz_init(tmpz);
    hash_to_mpz(tmpz, buf, len, pairing->r);

    element_t z; element_init_Zr(z, pairing);
    element_set_mpz(z, tmpz);

    element_pow_zn(outG1, g, z);

    mpz_clear(tmpz);
    element_clear(z);
}

void H3(element_t outG1, element_t inG1) {
    unsigned char buf[1024];
    size_t len = element_length_in_bytes(inG1);
    element_to_bytes(buf, inG1);

    mpz_t tmpz; mpz_init(tmpz);
    hash_to_mpz(tmpz, buf, len, pairing->r);

    element_t z; element_init_Zr(z, pairing);
    element_set_mpz(z, tmpz);

    element_pow_zn(outG1, g, z);

    mpz_clear(tmpz);
    element_clear(z);
}

void H4(element_t outZr, element_t addr, const char* msg, element_t X) {
    unsigned char buf[2048];
    unsigned char g1buf[512];
    unsigned char g2buf[512];

    size_t len1 = element_length_in_bytes(addr);
    size_t len2 = element_length_in_bytes(X);
    size_t msglen = strlen(msg);

    element_to_bytes(g1buf, addr);
    element_to_bytes(g2buf, X);

    memcpy(buf, g1buf, len1);
    memcpy(buf + len1, msg, msglen);
    memcpy(buf + len1 + msglen, g2buf, len2);

    mpz_t tmpz;
    mpz_init(tmpz);
    hash_to_mpz(tmpz, buf, len1 + msglen + len2, pairing->r);

    element_set_mpz(outZr, tmpz);

    mpz_clear(tmpz);
}

//----------------------------------------------
// Library Management Functions
//----------------------------------------------

/**
 * Initialize the library with a parameter file
 */
int stealth_init(const char* param_file) {
    if (library_initialized) {
        // Clean up previous initialization
        element_clear(g);
        pairing_clear(pairing);
    }
    
    // Check if file exists
    FILE *fp = fopen(param_file, "r");
    if (!fp) {
        fprintf(stderr, "Error: Cannot open parameter file %s\n", param_file);
        return -1;
    }
    fclose(fp);
    
    // Use the original pbc_demo_pairing_init (void function)
    char *fake_argv[2];
    fake_argv[0] = "stealth_lib";
    fake_argv[1] = (char*)param_file;
    
    pbc_demo_pairing_init(pairing, 2, fake_argv);

    element_init_G1(g, pairing);
    element_random(g);
    
    // Reset performance counters
    sumAddrGen = sumAddrRecognize = sumFastAddrRecognize = sumOnetimeSK = 0;
    sumSign = sumVerify = sumTrace = 0;
    perf_counter = 0;
    
    library_initialized = 1;
    return 0; // Success
}

/**
 * Check if library is initialized
 */
int stealth_is_initialized(void) {
    return library_initialized;
}

/**
 * Cleanup library resources
 */
void stealth_cleanup(void) {
    if (library_initialized) {
        element_clear(g);
        pairing_clear(pairing);
        library_initialized = 0;
    }
}

/**
 * Reset performance counters
 */
void stealth_reset_performance(void) {
    sumAddrGen = sumAddrRecognize = sumFastAddrRecognize = sumOnetimeSK = 0;
    sumSign = sumVerify = sumTrace = 0;
    perf_counter = 0;
}

/**
 * Get the current pairing for use in API functions
 */
pairing_t* stealth_get_pairing(void) {
    if (!library_initialized) return NULL;
    return &pairing;
}

//----------------------------------------------
// Core Cryptographic Functions
//----------------------------------------------

/**
 * Generate a key pair (A, B, a, b)
 */
void stealth_keygen(element_t A, element_t B, element_t aZ, element_t bZ) {
    if (!library_initialized) return;
    
    element_random(aZ);
    element_random(bZ);
    element_pow_zn(A, g, aZ);
    element_pow_zn(B, g, bZ);
}

/**
 * Generate trace key (TK, k)
 */
void stealth_tracekeygen(element_t TK, element_t kZ) {
    if (!library_initialized) return;
    
    element_random(kZ);
    element_pow_zn(TK, g, kZ);
}

/**
 * Generate one-time address
 */
void stealth_addr_gen(element_t Addr, element_t R1, element_t R2, element_t C,
                     element_t A_r, element_t B_r, element_t TK) {
    if (!library_initialized) return;
    
    clock_t t1 = clock();

    element_t rZ, r2Z; 
    element_init_Zr(rZ, pairing);
    element_init_Zr(r2Z, pairing);

    element_t R3; element_init_G1(R3, pairing);

    element_random(rZ);
    element_pow_zn(R1, g, rZ);

    element_t Ar_pow_r; element_init_G1(Ar_pow_r, pairing);
    element_pow_zn(Ar_pow_r, A_r, rZ);

    clock_t hash_start = clock();
    H1(r2Z, Ar_pow_r);
    clock_t hash_end = clock();

    element_pow_zn(R2, g, r2Z);
    element_pow_zn(C, B_r, r2Z);

    // e(R2, TK)
    element_t pairing_res, pairing_res_powr;
    element_init_GT(pairing_res, pairing);
    element_init_GT(pairing_res_powr, pairing);

    pairing_apply(pairing_res, R2, TK, pairing);
    element_pow_zn(pairing_res_powr, pairing_res, rZ);
    
    clock_t t2 = clock();
    sumAddrGen += timer_diff(t1, t2) - timer_diff(hash_start, hash_end);

    clock_t hash_start2 = clock();
    H2(R3, pairing_res_powr);
    clock_t hash_end2 = clock();
    
    clock_t t3 = clock();
   
    // Addr = R3 * B_r * C
    element_mul(Addr, R3, B_r);
    element_mul(Addr, Addr, C);

    element_clear(rZ);
    element_clear(r2Z);
    element_clear(R3);
    element_clear(Ar_pow_r);
    element_clear(pairing_res);
    element_clear(pairing_res_powr);

    clock_t t4 = clock();
    sumAddrGen += timer_diff(t3, t4) - timer_diff(hash_start2, hash_end2);
}

/**
 * Recognize address (full version)
 */
int stealth_addr_recognize(element_t Addr, element_t R1, element_t B_r,
                          element_t A_r, element_t C, element_t aZ, element_t TK) {
    if (!library_initialized) return 0;
    
    clock_t t1 = clock();

    element_t R1_pow_a, C_prime, R3_prime, Addr_prime;
    element_init_G1(R1_pow_a, pairing);
    element_init_G1(C_prime, pairing);
    element_init_G1(R3_prime, pairing);
    element_init_G1(Addr_prime, pairing);

    element_pow_zn(R1_pow_a, R1, aZ);

    element_t r2Z_prime;
    element_init_Zr(r2Z_prime, pairing);
    
    clock_t hash_start = clock();
    H1(r2Z_prime, R1_pow_a);
    clock_t hash_end = clock();

    element_pow_zn(C_prime, B_r, r2Z_prime);

    element_t pairing_res, pairing_res_r2Z;
    element_init_GT(pairing_res, pairing);
    element_init_GT(pairing_res_r2Z, pairing);

    pairing_apply(pairing_res, R1, TK, pairing);
    element_pow_zn(pairing_res_r2Z, pairing_res, r2Z_prime);

    clock_t hash_start2 = clock();
    H2(R3_prime, pairing_res_r2Z);
    clock_t hash_end2 = clock();
    
    element_mul(Addr_prime, R3_prime, B_r);
    element_mul(Addr_prime, Addr_prime, C_prime);

    int eq = (element_cmp(Addr_prime, Addr) == 0);

    element_clear(R1_pow_a);
    element_clear(C_prime);
    element_clear(R3_prime);
    element_clear(Addr_prime);
    element_clear(r2Z_prime);
    element_clear(pairing_res);
    element_clear(pairing_res_r2Z);

    clock_t t2 = clock();
    sumAddrRecognize += timer_diff(t1, t2) - timer_diff(hash_start, hash_end) - timer_diff(hash_start2, hash_end2);

    return eq;
}

/**
 * Fast address recognition
 */
int stealth_addr_recognize_fast(element_t R1, element_t B_r, element_t A_r, 
                               element_t C, element_t aZ) {
    if (!library_initialized) return 0;
    
    clock_t t1 = clock();

    // 1) r2' = H1( (R1)^aZ )
    element_t R1_pow_a;
    element_init_G1(R1_pow_a, pairing);
    element_pow_zn(R1_pow_a, R1, aZ);

    element_t r2Z_prime;
    element_init_Zr(r2Z_prime, pairing);
    
    clock_t hash_start = clock();
    H1(r2Z_prime, R1_pow_a);
    clock_t hash_end = clock();

    // 2) C' = B_r^(r2')
    element_t C_prime;
    element_init_G1(C_prime, pairing);
    element_pow_zn(C_prime, B_r, r2Z_prime);

    // 3) Compare with C
    int eq = (element_cmp(C_prime, C) == 0);

    // clear
    element_clear(R1_pow_a);
    element_clear(r2Z_prime);
    element_clear(C_prime);

    clock_t t2 = clock();    
    sumFastAddrRecognize += timer_diff(t1, t2) - timer_diff(hash_start, hash_end);

    return eq;
}

/**
 * Generate one-time secret key
 */
void stealth_onetime_skgen(element_t dsk, element_t Addr, element_t R1,
                          element_t aZ, element_t bZ) {
    if (!library_initialized) return;
    
    clock_t t1 = clock();

    element_t R1_pow_a; element_init_G1(R1_pow_a, pairing);
    element_pow_zn(R1_pow_a, R1, aZ);

    element_t r2Z; element_init_Zr(r2Z, pairing);
    
    clock_t hash_start1 = clock();
    H1(r2Z, R1_pow_a);
    clock_t hash_end1 = clock();

    element_t exp; element_init_Zr(exp, pairing);
    element_mul(exp, bZ, r2Z);

    element_t h3_addr; element_init_G1(h3_addr, pairing);
    
    clock_t t2 = clock();
    sumOnetimeSK += timer_diff(t1, t2) - timer_diff(hash_start1, hash_end1);

    clock_t hash_start2 = clock();
    H3(h3_addr, Addr);
    clock_t hash_end2 = clock();
    
    clock_t t3 = clock();

    element_pow_zn(dsk, h3_addr, exp);

    element_clear(R1_pow_a);
    element_clear(r2Z);
    element_clear(exp);
    element_clear(h3_addr);

    clock_t t4 = clock();
    sumOnetimeSK += timer_diff(t3, t4) - timer_diff(hash_start2, hash_end2);
}

/**
 * Sign a message
 */
void stealth_sign(element_t Q_sigma, element_t hZ, element_t Addr, 
                 element_t dsk, const char* msg) {
    if (!library_initialized) return;
    
    clock_t t1 = clock();

    element_t xZ; element_init_Zr(xZ, pairing);
    element_random(xZ);

    element_t gx; element_init_G1(gx, pairing);
    element_pow_zn(gx, g, xZ);

    element_t XGT; element_init_GT(XGT, pairing);
    pairing_apply(XGT, gx, g, pairing);

    clock_t hash_start = clock();
    H4(hZ, Addr, msg, XGT);
    clock_t hash_end = clock();

    element_t neg_hZ; element_init_Zr(neg_hZ, pairing);
    element_neg(neg_hZ, hZ);

    element_t dsk_inv_h; element_init_G1(dsk_inv_h, pairing);
    element_pow_zn(dsk_inv_h, dsk, neg_hZ);

    element_mul(Q_sigma, dsk_inv_h, gx);

    element_clear(xZ);
    element_clear(gx);
    element_clear(XGT);
    element_clear(neg_hZ);
    element_clear(dsk_inv_h);

    clock_t t2 = clock();
    sumSign += timer_diff(t1, t2) - timer_diff(hash_start, hash_end);
}

/**
 * Verify a signature
 */
int stealth_verify(element_t Addr, element_t R2, element_t C,
                  const char* msg, element_t hZ, element_t Q_sigma) {
    if (!library_initialized) return 0;
    
    clock_t t1 = clock();

    element_t h3_addr; element_init_G1(h3_addr, pairing);
    
    clock_t t2 = clock();
    sumVerify += timer_diff(t1, t2);

    clock_t hash_start1 = clock();
    H3(h3_addr, Addr);
    clock_t hash_end1 = clock();
    
    clock_t t3 = clock();

    element_t pairing1, pairing2, pairing2_exp, prod;
    element_init_GT(pairing1, pairing);
    element_init_GT(pairing2, pairing);
    element_init_GT(pairing2_exp, pairing);
    element_init_GT(prod, pairing);

    pairing_apply(pairing1, Q_sigma, g, pairing);
    pairing_apply(pairing2, h3_addr, C, pairing);
    element_pow_zn(pairing2_exp, pairing2, hZ);
    element_mul(prod, pairing1, pairing2_exp);

    element_t hZ_prime; element_init_Zr(hZ_prime, pairing);
    
    clock_t hash_start2 = clock();
    H4(hZ_prime, Addr, msg, prod);
    clock_t hash_end2 = clock();

    int valid = (element_cmp(hZ, hZ_prime) == 0);

    element_clear(h3_addr);
    element_clear(pairing1);
    element_clear(pairing2);
    element_clear(pairing2_exp);
    element_clear(prod);
    element_clear(hZ_prime);

    clock_t t4 = clock();
    sumVerify += timer_diff(t3, t4) - timer_diff(hash_start1, hash_end1) - timer_diff(hash_start2, hash_end2);

    return valid;
}

/**
 * Trace identity
 */
void stealth_trace(element_t B_r, element_t Addr, element_t R1, element_t R2, 
                  element_t C, element_t kZ) {
    if (!library_initialized) return;
    
    clock_t t1 = clock();

    element_t pairing_res, pairing_powk, R3;
    element_init_GT(pairing_res, pairing);
    element_init_GT(pairing_powk, pairing);
    element_init_G1(R3, pairing);

    pairing_apply(pairing_res, R1, R2, pairing);
    element_pow_zn(pairing_powk, pairing_res, kZ);
    
    clock_t t2 = clock();
    sumTrace += timer_diff(t1, t2);
    
    clock_t hash_start = clock();
    H2(R3, pairing_powk);
    clock_t hash_end = clock();
    
    clock_t t3 = clock();

    element_t R3_inv, C_inv;
    element_init_G1(R3_inv, pairing);
    element_init_G1(C_inv, pairing);

    element_invert(R3_inv, R3);
    element_invert(C_inv, C);

    element_mul(B_r, Addr, R3_inv);
    element_mul(B_r, B_r, C_inv);

    element_clear(pairing_res);
    element_clear(pairing_powk);
    element_clear(R3);
    element_clear(R3_inv);
    element_clear(C_inv);

    clock_t t4 = clock();
    sumTrace += timer_diff(t3, t4) - timer_diff(hash_start, hash_end);
}

//----------------------------------------------
// Performance and Utility Functions
//----------------------------------------------

/**
 * Get performance statistics
 */
void stealth_get_performance(stealth_performance_t* perf) {
    if (!perf || perf_counter == 0) return;
    
    perf->addr_gen_avg = sumAddrGen / perf_counter;
    perf->addr_recognize_avg = sumAddrRecognize / perf_counter;
    perf->fast_recognize_avg = sumFastAddrRecognize / perf_counter;
    perf->onetime_sk_avg = sumOnetimeSK / perf_counter;
    perf->sign_avg = sumSign / perf_counter;
    perf->verify_avg = sumVerify / perf_counter;
    perf->trace_avg = sumTrace / perf_counter;
    perf->operation_count = perf_counter;
}

/**
 * Print performance statistics
 */
void stealth_print_performance(void) {
    if (perf_counter == 0) {
        printf("No operations performed yet.\n");
        return;
    }
    
    printf("\n=== Performance Statistics (%d operations) ===\n", perf_counter);
    printf("Address Generation:  %.3f ms\n", sumAddrGen / perf_counter);
    printf("Address Recognize:   %.3f ms\n", sumAddrRecognize / perf_counter);
    printf("Fast Recognize:      %.3f ms\n", sumFastAddrRecognize / perf_counter);
    printf("One-time SK Gen:     %.3f ms\n", sumOnetimeSK / perf_counter);
    printf("Sign:                %.3f ms\n", sumSign / perf_counter);
    printf("Verify:              %.3f ms\n", sumVerify / perf_counter);
    printf("Trace:               %.3f ms\n", sumTrace / perf_counter);
}

//----------------------------------------------
// Element serialization helpers
//----------------------------------------------

/**
 * Get the size needed for serializing an element
 */
int stealth_element_size_G1(void) {
    if (!library_initialized) return 0;
    element_t temp;
    element_init_G1(temp, pairing);
    int size = element_length_in_bytes(temp);
    element_clear(temp);
    return size;
}

int stealth_element_size_Zr(void) {
    if (!library_initialized) return 0;
    element_t temp;
    element_init_Zr(temp, pairing);
    int size = element_length_in_bytes(temp);
    element_clear(temp);
    return size;
}

/**
 * Serialize element to bytes
 */
int stealth_element_to_bytes(element_t elem, unsigned char* buf, int buf_size) {
    if (!library_initialized) return -1;
    int needed = element_length_in_bytes(elem);
    if (needed > buf_size) return -1;
    element_to_bytes(buf, elem);
    return needed;
}

/**
 * Deserialize element from bytes - Fixed const qualifier issues
 */
int stealth_element_from_bytes_G1(element_t elem, const unsigned char* buf, int len) {
    if (!library_initialized) return -1;
    element_init_G1(elem, pairing);
    // Cast away const to match PBC library signature
    return element_from_bytes(elem, (unsigned char*)buf);
}

int stealth_element_from_bytes_Zr(element_t elem, const unsigned char* buf, int len) {
    if (!library_initialized) return -1;
    element_init_Zr(elem, pairing);
    // Cast away const to match PBC library signature
    return element_from_bytes(elem, (unsigned char*)buf);
}