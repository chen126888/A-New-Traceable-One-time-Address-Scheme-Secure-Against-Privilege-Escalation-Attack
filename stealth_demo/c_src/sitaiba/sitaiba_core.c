/****************************************************************************
 * File: sitaiba_core.c
 * Desc: Core implementation for SITAIBA Scheme
 *       (SIgnature-based TrAceable anonymIty using BilineAr mapping)
 *       Performance timing excludes hash computation time
 ****************************************************************************/

#include "sitaiba_core.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <openssl/sha.h>
#include <time.h>

//----------------------------------------------
// Global Variables
//----------------------------------------------
static pairing_t pairing;
static element_t g;              // Generator
static element_t A_m, a_m;       // Manager key pair
static int is_initialized = 0;

// Performance counters (excluding hash time)
static double sumAddrGen = 0;
static double sumAddrVerify = 0; 
static double sumFastAddrVerify = 0;
static double sumOnetimeSK = 0;
static double sumTrace = 0;
static double sumH1 = 0;
static double sumH2 = 0;
int perf_counter = 0;

//----------------------------------------------
// Helper Functions
//----------------------------------------------

/**
 * Timer helper
 */
static double timer_diff(clock_t start, clock_t end) {
    return ((double)(end - start)) / CLOCKS_PER_SEC * 1000.0; // in ms
}

/**
 * Hash to mpz helper
 */
static void hash_to_mpz(mpz_t out, const unsigned char *data, size_t len, mpz_t mod) {
    unsigned char hash[SHA256_DIGEST_LENGTH];
    SHA256(data, len, hash);
    mpz_import(out, SHA256_DIGEST_LENGTH, 1, 1, 0, 0, hash);
    mpz_mod(out, out, mod);
}

//----------------------------------------------
// Library Management Functions  
//----------------------------------------------

int sitaiba_init(const char* param_file) {
    if (is_initialized) {
        return 0; // Already initialized
    }

    // Initialize pairing from parameter file
    FILE *fp = fopen(param_file, "r");
    if (!fp) {
        return -1; // Cannot open parameter file
    }
    
    // Read the entire file into a string
    fseek(fp, 0, SEEK_END);
    long fsize = ftell(fp);
    fseek(fp, 0, SEEK_SET);
    
    char *param_str = malloc(fsize + 1);
    if (!param_str) {
        fclose(fp);
        return -1;
    }
    
    fread(param_str, fsize, 1, fp);
    param_str[fsize] = '\0';
    fclose(fp);
    
    if (pairing_init_set_str(pairing, param_str) != 0) {
        free(param_str);
        return -1;
    }
    free(param_str);

    // Initialize generator
    element_init_G1(g, pairing);
    element_random(g);

    // Generate tracer key pair
    element_init_G1(A_m, pairing);
    element_init_Zr(a_m, pairing);
    sitaiba_tracer_keygen(A_m, a_m);

    // Reset performance counters
    sitaiba_reset_performance();

    is_initialized = 1;
    return 0;
}

int sitaiba_is_initialized(void) {
    return is_initialized;
}

void sitaiba_cleanup(void) {
    if (is_initialized) {
        element_clear(g);
        element_clear(A_m);
        element_clear(a_m);
        pairing_clear(pairing);
        is_initialized = 0;
    }
}

void sitaiba_reset_performance(void) {
    sumAddrGen = 0;
    sumAddrVerify = 0;
    sumFastAddrVerify = 0;
    sumOnetimeSK = 0;
    sumTrace = 0;
    sumH1 = 0;
    sumH2 = 0;
    perf_counter = 0;
}

pairing_t* sitaiba_get_pairing(void) {
    return is_initialized ? &pairing : NULL;
}

//----------------------------------------------
// Hash Functions (from original sitaiba.c)
//----------------------------------------------

void sitaiba_H1(element_t outZr, element_t inG1) {
    clock_t t1 = clock();
    unsigned char buf[1024];
    size_t len = element_length_in_bytes(inG1);
    element_to_bytes(buf, inG1);

    mpz_t tmpz; 
    mpz_init(tmpz);
    hash_to_mpz(tmpz, buf, len, pairing->r);
    element_set_mpz(outZr, tmpz);
    mpz_clear(tmpz);
    
    clock_t t2 = clock();
    sumH1 += timer_diff(t1, t2);
}

void sitaiba_H2(element_t outZr, element_t inGT) {
    clock_t t1 = clock();
    unsigned char buf[2048];
    size_t len = element_length_in_bytes(inGT);
    element_to_bytes(buf, inGT);

    mpz_t tmpz;
    mpz_init(tmpz);
    hash_to_mpz(tmpz, buf, len, pairing->r);
    element_set_mpz(outZr, tmpz);
    mpz_clear(tmpz);
    
    clock_t t2 = clock();
    sumH2 += timer_diff(t1, t2);
}

//----------------------------------------------
// Core Cryptographic Functions
//----------------------------------------------

void sitaiba_keygen(element_t A, element_t B, element_t aZ, element_t bZ) {
    element_random(aZ);
    element_random(bZ);
    element_pow_zn(A, g, aZ);
    element_pow_zn(B, g, bZ);
}

void sitaiba_tracer_keygen(element_t A_m_out, element_t a_m_out) {
    element_random(a_m_out);
    element_pow_zn(A_m_out, g, a_m_out);
}

void sitaiba_addr_gen(element_t Addr, element_t R1, element_t R2,
                     element_t A_r, element_t B_r, element_t A_m_param) {
    clock_t t1 = clock();
    
    element_t r1, r2, r3, tmp;
    element_init_Zr(r1, pairing);
    element_init_Zr(r2, pairing);
    element_init_Zr(r3, pairing);
    element_init_GT(tmp, pairing);

    element_random(r1);
    element_pow_zn(R1, g, r1);

    element_t Ar_pow_r1;
    element_init_G1(Ar_pow_r1, pairing);
    element_pow_zn(Ar_pow_r1, A_r, r1);

    // Measure hash time separately
    clock_t h1_start = clock();
    sitaiba_H1(r2, Ar_pow_r1);  // This adds to sumH1 internally
    clock_t h1_end = clock();
    double h1_time = timer_diff(h1_start, h1_end);

    element_pow_zn(R2, A_r, r2);

    element_t eR2Am;
    element_init_GT(eR2Am, pairing);
    pairing_apply(eR2Am, R2, A_m_param, pairing);
    element_pow_zn(tmp, eR2Am, r1);
    
    // Measure hash time separately  
    clock_t h2_start = clock();
    sitaiba_H2(r3, tmp);  // This adds to sumH2 internally
    clock_t h2_end = clock();
    double h2_time = timer_diff(h2_start, h2_end);

    element_t r3G, sum;
    element_init_G1(r3G, pairing);
    element_init_G1(sum, pairing);
    element_pow_zn(r3G, g, r3);

    element_mul(sum, r3G, R2);
    element_mul(Addr, sum, B_r);

    // Cleanup
    element_clear(r1); element_clear(r2); element_clear(r3);
    element_clear(tmp); element_clear(Ar_pow_r1); element_clear(eR2Am);
    element_clear(r3G); element_clear(sum);

    clock_t t2 = clock();
    // Subtract hash computation time from total
    double total_time = timer_diff(t1, t2);
    sumAddrGen += (total_time - h1_time - h2_time);
}

int sitaiba_addr_recognize(element_t Addr, element_t R1, element_t R2,
                       element_t A_r, element_t B_r, element_t A_m_param, element_t a_r) {
    clock_t t1 = clock();

    // Step 1: r2 = H1(a_r * R1)
    element_t R1_pow_a, r2Z;
    element_init_G1(R1_pow_a, pairing);
    element_init_Zr(r2Z, pairing);
    element_pow_zn(R1_pow_a, R1, a_r);
    
    clock_t h1_start = clock();
    sitaiba_H1(r2Z, R1_pow_a);
    clock_t h1_end = clock();
    double h1_time = timer_diff(h1_start, h1_end);

    // Step 2: R2' = r2 * A_r
    element_t R2_prime, r2a;
    element_init_G1(R2_prime, pairing);
    element_init_Zr(r2a, pairing);
    element_pow_zn(R2_prime, A_r, r2Z);
    element_mul(r2a, r2Z, a_r);

    // Step 3: r3 = H2(e(R1, A_m)^r2a)
    element_t eR1Am, r3Z, tmp;
    element_init_GT(eR1Am, pairing);
    element_init_GT(tmp, pairing);
    element_init_Zr(r3Z, pairing);
    pairing_apply(eR1Am, R1, A_m_param, pairing);
    element_pow_zn(tmp, eR1Am, r2a);
    
    clock_t h2_start = clock();
    sitaiba_H2(r3Z, tmp);
    clock_t h2_end = clock();
    double h2_time = timer_diff(h2_start, h2_end);

    // Step 4: reconstruct Addr = r3 * G + R2 + B_r
    element_t r3G, sum, Addr_reconstructed;
    element_init_G1(r3G, pairing);
    element_init_G1(sum, pairing);
    element_init_G1(Addr_reconstructed, pairing);
    element_pow_zn(r3G, g, r3Z);
    element_mul(sum, r3G, R2);
    element_mul(Addr_reconstructed, sum, B_r);
    
    int eq1 = (element_cmp(R2_prime, R2) == 0);
    int eq2 = (element_cmp(Addr_reconstructed, Addr) == 0);
    int result = eq1 && eq2;

    // Cleanup
    element_clear(R1_pow_a); element_clear(r2Z);
    element_clear(R2_prime); element_clear(r2a);
    element_clear(eR1Am); element_clear(r3Z); element_clear(tmp);
    element_clear(r3G); element_clear(sum); element_clear(Addr_reconstructed);

    clock_t t2 = clock();
    // Subtract hash computation time from total
    double total_time = timer_diff(t1, t2);
    sumAddrVerify += (total_time - h1_time - h2_time);
    
    return result;
}

int sitaiba_addr_recognize_fast(element_t R1, element_t R2, element_t A_r, element_t a_r) {
    clock_t t1 = clock();

    // Step 1: r2 = H1(a_r * R1)
    element_t R1_pow_a, r2Z;
    element_init_G1(R1_pow_a, pairing);
    element_init_Zr(r2Z, pairing);
    element_pow_zn(R1_pow_a, R1, a_r);
    
    clock_t h1_start = clock();
    sitaiba_H1(r2Z, R1_pow_a);
    clock_t h1_end = clock();
    double h1_time = timer_diff(h1_start, h1_end);

    // Step 2: R2' = r2 * A_r
    element_t R2_prime;
    element_init_G1(R2_prime, pairing);
    element_pow_zn(R2_prime, A_r, r2Z);

    int result = (element_cmp(R2_prime, R2) == 0);

    // Cleanup
    element_clear(R1_pow_a); element_clear(r2Z); element_clear(R2_prime);

    clock_t t2 = clock();
    // Subtract hash computation time from total
    double total_time = timer_diff(t1, t2);
    sumFastAddrVerify += (total_time - h1_time);
    
    return result;
}

void sitaiba_onetime_skgen(element_t dsk, element_t R1, element_t a_r, 
                          element_t b_r, element_t A_m_param) {
    clock_t t1 = clock();
    
    element_t r2, r3, eR1Am;
    element_init_Zr(r2, pairing);
    element_init_Zr(r3, pairing);
    element_init_GT(eR1Am, pairing);

    element_t R1_a, r2a;
    element_init_G1(R1_a, pairing);
    element_init_Zr(r2a, pairing);
    element_pow_zn(R1_a, R1, a_r);
    
    clock_t h1_start = clock();
    sitaiba_H1(r2, R1_a);
    clock_t h1_end = clock();
    double h1_time = timer_diff(h1_start, h1_end);

    pairing_apply(eR1Am, R1, A_m_param, pairing);
    element_mul(r2a, r2, a_r);
    element_pow_zn(eR1Am, eR1Am, r2a);

    clock_t h2_start = clock();
    sitaiba_H2(r3, eR1Am);
    clock_t h2_end = clock();
    double h2_time = timer_diff(h2_start, h2_end);

    // DSK is in Zr: compute r3 + r2*a + b
    element_add(dsk, r3, r2a);
    element_add(dsk, dsk, b_r);

    // Cleanup
    element_clear(r2); element_clear(r3); element_clear(eR1Am);
    element_clear(R1_a); element_clear(r2a);
    
    clock_t t2 = clock();
    // Subtract hash computation time from total
    double total_time = timer_diff(t1, t2);
    sumOnetimeSK += (total_time - h1_time - h2_time);
}

void sitaiba_trace(element_t B_r, element_t Addr, element_t R1, 
                  element_t R2, element_t a_m_param) {
    clock_t t1 = clock();
    
    element_t eR1R2, powed, r3;
    element_init_GT(eR1R2, pairing);
    element_init_GT(powed, pairing);
    element_init_Zr(r3, pairing);

    pairing_apply(eR1R2, R1, R2, pairing);
    
    // Use internal tracer private key if a_m_param is NULL
    if (a_m_param == NULL) {
        element_pow_zn(powed, eR1R2, a_m);
    } else {
        element_pow_zn(powed, eR1R2, a_m_param);
    }
    
    clock_t h2_start = clock();
    sitaiba_H2(r3, powed);
    clock_t h2_end = clock();
    double h2_time = timer_diff(h2_start, h2_end);

    element_t r3G, Addr_tmp, R2_inv;
    element_init_G1(r3G, pairing);
    element_init_G1(Addr_tmp, pairing);
    element_init_G1(R2_inv, pairing);

    // r3G = r3 * G
    element_pow_zn(r3G, g, r3);

    // Addr_tmp = Addr * (r3G)^-1
    element_invert(Addr_tmp, r3G);
    element_mul(Addr_tmp, Addr, Addr_tmp);

    // R2_inv = R2^-1
    element_invert(R2_inv, R2);

    // B_r = Addr_tmp * R2^-1
    element_mul(B_r, Addr_tmp, R2_inv);

    // Cleanup
    element_clear(eR1R2); element_clear(powed); element_clear(r3);
    element_clear(r3G); element_clear(Addr_tmp); element_clear(R2_inv);

    clock_t t2 = clock();
    // Subtract hash computation time from total
    double total_time = timer_diff(t1, t2);
    sumTrace += (total_time - h2_time);
}

//----------------------------------------------
// Performance Functions
//----------------------------------------------

void sitaiba_get_performance(sitaiba_performance_t* perf) {
    if (!perf || perf_counter == 0) return;

    perf->addr_gen_avg = sumAddrGen / perf_counter;
    perf->addr_recognize_avg = sumAddrVerify / perf_counter;
    perf->fast_recognize_avg = sumFastAddrVerify / perf_counter;
    perf->onetime_sk_avg = sumOnetimeSK / perf_counter;
    perf->trace_avg = sumTrace / perf_counter;
    perf->operation_count = perf_counter;
}

void sitaiba_print_performance(void) {
    if (perf_counter == 0) {
        printf("No operations recorded yet.\n");
        return;
    }

    printf("\n=== SITAIBA Performance (Average over %d runs, excluding hash time) ===\n", perf_counter);
    printf("Address Generation:    %.3f ms\n", sumAddrGen / perf_counter);
    printf("Address Recognize:     %.3f ms\n", sumAddrVerify / perf_counter);
    printf("Fast Address Recog:    %.3f ms\n", sumFastAddrVerify / perf_counter);
    printf("One-time SK Gen:       %.3f ms\n", sumOnetimeSK / perf_counter);
    printf("Identity Tracing:      %.3f ms\n", sumTrace / perf_counter);
}

//----------------------------------------------
// Element Serialization Functions
//----------------------------------------------

int sitaiba_element_size_G1(void) {
    if (!is_initialized) return 0;
    return element_length_in_bytes(g);  // Use uncompressed size to match element_to_bytes
}

int sitaiba_element_size_Zr(void) {
    if (!is_initialized) return 0;
    element_t tmp;
    element_init_Zr(tmp, pairing);
    int size = element_length_in_bytes(tmp);
    element_clear(tmp);
    return size;
}

int sitaiba_element_to_bytes(element_t elem, unsigned char* buf, int buf_size) {
    int needed_size = element_length_in_bytes(elem);
    if (buf_size < needed_size) return -1;
    
    element_to_bytes(buf, elem);
    return needed_size;
}

int sitaiba_element_from_bytes_G1(element_t elem, const unsigned char* buf, int len) {
    if (!is_initialized) return -1;
    element_init_G1(elem, pairing);
    // Cast away const to match PBC library signature
    return element_from_bytes(elem, (unsigned char*)buf);
}

int sitaiba_element_from_bytes_Zr(element_t elem, const unsigned char* buf, int len) {
    if (!is_initialized) return -1;
    element_init_Zr(elem, pairing);
    // Cast away const to match PBC library signature
    return element_from_bytes(elem, (unsigned char*)buf);
}

//----------------------------------------------
// Manager Key Access
//----------------------------------------------

int sitaiba_get_tracer_public_key(element_t A_m_out) {
    if (!is_initialized) return -1;
    element_set(A_m_out, A_m);
    return 0;
}

int sitaiba_get_generator(element_t g_out) {
    if (!is_initialized) return -1;
    element_set(g_out, g);
    return 0;
}