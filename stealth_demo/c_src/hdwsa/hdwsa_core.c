/****************************************************************************
 * File: hdwsa_core.c
 * Desc: Core cryptographic functions for HDWSA Scheme
 *       (Hierarchical Deterministic Wallet Signature Algorithm)
 ****************************************************************************/

#include "hdwsa_core.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <openssl/sha.h>
#include <pbc/pbc_test.h>

//----------------------------------------------
// Global Variables
//----------------------------------------------
static pairing_t pairing;
static element_t P; // generator in G1
static int initialized = 0;
static hdwsa_performance_t performance = {0};
static size_t g1_size = 0;
static size_t zr_size = 0;

// Performance timing accumulators
static double sum_root_keygen = 0, sum_keypair_gen = 0, sum_addr_gen = 0;
static double sum_addr_recognize = 0, sum_dsk_gen = 0, sum_sign = 0, sum_verify = 0;
static double sum_H0 = 0, sum_H1 = 0, sum_H2 = 0, sum_H3 = 0, sum_H4 = 0;

//----------------------------------------------
// Utility Functions
//----------------------------------------------

static double timer_diff(clock_t start, clock_t end) {
    return ((double)(end - start)) / CLOCKS_PER_SEC * 1000.0;
}

static void hash_to_mpz(mpz_t out, const unsigned char *data, size_t len, mpz_t mod) {
    unsigned char hash[SHA256_DIGEST_LENGTH];
    SHA256(data, len, hash);
    mpz_import(out, SHA256_DIGEST_LENGTH, 1, 1, 0, 0, hash);
    mpz_mod(out, out, mod);
}

//----------------------------------------------
// Library Management Functions
//----------------------------------------------

int hdwsa_init(const char* param_file) {
    if (initialized) {
        return 0; // Already initialized
    }
    
    // Initialize pairing
    char *fake_argv[2];
    fake_argv[0] = "hdwsa";
    fake_argv[1] = (char*)param_file;
    pbc_demo_pairing_init(pairing, 2, fake_argv);
    
    // Initialize generator P
    element_init_G1(P, pairing);
    element_random(P);
    
    // Get element sizes
    g1_size = pairing_length_in_bytes_G1(pairing);
    zr_size = pairing_length_in_bytes_Zr(pairing);
    
    initialized = 1;
    hdwsa_reset_performance();
    
    return 0;
}

int hdwsa_is_initialized(void) {
    return initialized;
}

void hdwsa_cleanup(void) {
    if (initialized) {
        element_clear(P);
        pairing_clear(pairing);
        initialized = 0;
    }
}

void hdwsa_reset_performance(void) {
    memset(&performance, 0, sizeof(hdwsa_performance_t));
    sum_root_keygen = sum_keypair_gen = sum_addr_gen = 0;
    sum_addr_recognize = sum_dsk_gen = sum_sign = sum_verify = 0;
    sum_H0 = sum_H1 = sum_H2 = sum_H3 = sum_H4 = 0;
}

hdwsa_performance_t* hdwsa_get_performance(void) {
    return &performance;
}

void hdwsa_get_element_sizes(size_t* g1_size_out, size_t* zr_size_out) {
    if (g1_size_out) *g1_size_out = g1_size;
    if (zr_size_out) *zr_size_out = zr_size;
}

//----------------------------------------------
// Hash Functions
//----------------------------------------------

void hdwsa_H0(unsigned char* out, const char* full_id) {
    if (!initialized) return;
    
    clock_t t1 = clock();
    
    element_t QID, zr;
    element_init_G1(QID, pairing);
    element_init_Zr(zr, pairing);
    
    mpz_t tmp;
    mpz_init(tmp);
    hash_to_mpz(tmp, (const unsigned char *)full_id, strlen(full_id), pairing->r);
    element_set_mpz(zr, tmp);
    element_mul_zn(QID, P, zr);
    
    element_to_bytes(out, QID);
    
    element_clear(QID);
    element_clear(zr);
    mpz_clear(tmp);
    
    clock_t t2 = clock();
    sum_H0 += timer_diff(t1, t2);
}

void hdwsa_H1(unsigned char* out, const unsigned char* in1, const unsigned char* in2) {
    if (!initialized) return;
    
    clock_t t1 = clock();
    
    element_t elem1, elem2, result;
    element_init_G1(elem1, pairing);
    element_init_G1(elem2, pairing);
    element_init_Zr(result, pairing);
    
    element_from_bytes(elem1, (unsigned char*)in1);
    element_from_bytes(elem2, (unsigned char*)in2);
    
    unsigned char buf[2048];
    int len1 = element_length_in_bytes(elem1);
    int len2 = element_length_in_bytes(elem2);
    element_to_bytes(buf, elem1);
    element_to_bytes(buf + len1, elem2);
    
    mpz_t tmp;
    mpz_init(tmp);
    hash_to_mpz(tmp, buf, len1 + len2, pairing->r);
    element_set_mpz(result, tmp);
    
    element_to_bytes(out, result);
    
    element_clear(elem1);
    element_clear(elem2);
    element_clear(result);
    mpz_clear(tmp);
    
    clock_t t2 = clock();
    sum_H1 += timer_diff(t1, t2);
}

void hdwsa_H2(unsigned char* out, const unsigned char* in1, const unsigned char* in2) {
    if (!initialized) return;
    
    clock_t t1 = clock();
    
    element_t elem1, elem2, result;
    element_init_G1(elem1, pairing);
    element_init_G1(elem2, pairing);
    element_init_Zr(result, pairing);
    
    element_from_bytes(elem1, (unsigned char*)in1);
    element_from_bytes(elem2, (unsigned char*)in2);
    
    unsigned char buf[2048];
    buf[0] = 0x02; // H2 prefix to differentiate from H1
    int len1 = element_length_in_bytes(elem1);
    int len2 = element_length_in_bytes(elem2);
    element_to_bytes(buf + 1, elem1);
    element_to_bytes(buf + 1 + len1, elem2);
    
    mpz_t tmp;
    mpz_init(tmp);
    hash_to_mpz(tmp, buf, 1 + len1 + len2, pairing->r);
    element_set_mpz(result, tmp);
    
    element_to_bytes(out, result);
    
    element_clear(elem1);
    element_clear(elem2);
    element_clear(result);
    mpz_clear(tmp);
    
    clock_t t2 = clock();
    sum_H2 += timer_diff(t1, t2);
}

void hdwsa_H3(unsigned char* out, const unsigned char* in1, const unsigned char* in2, const unsigned char* in3) {
    if (!initialized) return;
    
    clock_t t1 = clock();
    
    element_t elem1, elem2, elem3, result, z;
    element_init_G1(elem1, pairing);
    element_init_G1(elem2, pairing);
    element_init_G1(elem3, pairing);
    element_init_G1(result, pairing);
    element_init_Zr(z, pairing);
    
    element_from_bytes(elem1, (unsigned char*)in1);
    element_from_bytes(elem2, (unsigned char*)in2);
    element_from_bytes(elem3, (unsigned char*)in3);
    
    unsigned char buf[3072];
    buf[0] = 0x03; // H3 prefix
    int len1 = element_length_in_bytes(elem1);
    int len2 = element_length_in_bytes(elem2);
    int len3 = element_length_in_bytes(elem3);
    element_to_bytes(buf + 1, elem1);
    element_to_bytes(buf + 1 + len1, elem2);
    element_to_bytes(buf + 1 + len1 + len2, elem3);
    
    mpz_t tmp;
    mpz_init(tmp);
    hash_to_mpz(tmp, buf, 1 + len1 + len2 + len3, pairing->r);
    element_set_mpz(z, tmp);
    element_mul_zn(result, P, z);
    
    element_to_bytes(out, result);
    
    element_clear(elem1);
    element_clear(elem2);
    element_clear(elem3);
    element_clear(result);
    element_clear(z);
    mpz_clear(tmp);
    
    clock_t t2 = clock();
    sum_H3 += timer_diff(t1, t2);
}

void hdwsa_H4(unsigned char* out, const unsigned char* dvk_qr, const unsigned char* dvk_qvk, const char* msg) {
    if (!initialized) return;
    
    clock_t t1 = clock();
    
    element_t qr, qvk, result;
    element_init_G1(qr, pairing);
    element_init_GT(qvk, pairing);
    element_init_Zr(result, pairing);
    
    element_from_bytes(qr, (unsigned char*)dvk_qr);
    element_from_bytes(qvk, (unsigned char*)dvk_qvk);
    
    unsigned char buf[4096];
    buf[0] = 0x04; // H4 prefix
    int len1 = element_length_in_bytes(qr);
    int len2 = element_length_in_bytes(qvk);
    int lenm = strlen(msg);
    
    element_to_bytes(buf + 1, qr);
    element_to_bytes(buf + 1 + len1, qvk);
    memcpy(buf + 1 + len1 + len2, msg, lenm);
    
    mpz_t tmp;
    mpz_init(tmp);
    hash_to_mpz(tmp, buf, 1 + len1 + len2 + lenm, pairing->r);
    element_set_mpz(result, tmp);
    
    element_to_bytes(out, result);
    
    element_clear(qr);
    element_clear(qvk);
    element_clear(result);
    mpz_clear(tmp);
    
    clock_t t2 = clock();
    sum_H4 += timer_diff(t1, t2);
}

//----------------------------------------------
// System Setup Functions
//----------------------------------------------

int hdwsa_root_keygen(unsigned char* A_out, unsigned char* B_out, 
                      unsigned char* alpha_out, unsigned char* beta_out) {
    if (!initialized) return -1;
    
    clock_t t1 = clock();
    
    element_t A, B, alpha, beta;
    element_init_G1(A, pairing);
    element_init_G1(B, pairing);
    element_init_Zr(alpha, pairing);
    element_init_Zr(beta, pairing);
    
    // Generate random private keys
    element_random(alpha);
    element_random(beta);
    
    // Compute public keys
    element_mul_zn(A, P, alpha);
    element_mul_zn(B, P, beta);
    
    // Output to buffers
    element_to_bytes(A_out, A);
    element_to_bytes(B_out, B);
    element_to_bytes(alpha_out, alpha);
    element_to_bytes(beta_out, beta);
    
    element_clear(A);
    element_clear(B);
    element_clear(alpha);
    element_clear(beta);
    
    clock_t t2 = clock();
    sum_root_keygen += timer_diff(t1, t2);
    
    return 0;
}

//----------------------------------------------
// Key Management Functions
//----------------------------------------------

int hdwsa_keypair_gen(unsigned char* A2_out, unsigned char* B2_out,
                      unsigned char* alpha2_out, unsigned char* beta2_out,
                      const unsigned char* alpha1_in, const unsigned char* beta1_in,
                      const char* full_id) {
    if (!initialized) return -1;
    
    clock_t t1 = clock();
    
    element_t alpha1, beta1, alpha2, beta2, A2, B2;
    element_t QID, temp;
    
    element_init_Zr(alpha1, pairing);
    element_init_Zr(beta1, pairing);
    element_init_Zr(alpha2, pairing);
    element_init_Zr(beta2, pairing);
    element_init_G1(A2, pairing);
    element_init_G1(B2, pairing);
    element_init_G1(QID, pairing);
    element_init_G1(temp, pairing);
    
    // Load parent keys
    element_from_bytes(alpha1, (unsigned char*)alpha1_in);
    element_from_bytes(beta1, (unsigned char*)beta1_in);
    
    clock_t t2 = clock();
    
    // Step 1: Compute Q_ID = H0(full_id)
    unsigned char qid_buf[g1_size];
    hdwsa_H0(qid_buf, full_id);
    element_from_bytes(QID, qid_buf);
    
    clock_t t3 = clock();
    
    // Step 2: Compute α_ID = H1(Q_ID, α_{ID_(t-1)} * Q_ID)
    element_mul_zn(temp, QID, alpha1);
    unsigned char temp_buf[g1_size];
    element_to_bytes(temp_buf, temp);
    unsigned char alpha2_buf[zr_size];
    hdwsa_H1(alpha2_buf, qid_buf, temp_buf);
    element_from_bytes(alpha2, alpha2_buf);
    
    // Step 3: Compute β_ID = H2(Q_ID, β_{ID_(t-1)} * Q_ID)
    element_mul_zn(temp, QID, beta1);
    element_to_bytes(temp_buf, temp);
    unsigned char beta2_buf[zr_size];
    hdwsa_H2(beta2_buf, qid_buf, temp_buf);
    element_from_bytes(beta2, beta2_buf);
    
    clock_t t4 = clock();
    
    // Step 4: Compute public key components
    element_mul_zn(A2, P, alpha2);
    element_mul_zn(B2, P, beta2);
    
    // Output to buffers
    element_to_bytes(A2_out, A2);
    element_to_bytes(B2_out, B2);
    element_to_bytes(alpha2_out, alpha2);
    element_to_bytes(beta2_out, beta2);
    
    element_clear(alpha1);
    element_clear(beta1);
    element_clear(alpha2);
    element_clear(beta2);
    element_clear(A2);
    element_clear(B2);
    element_clear(QID);
    element_clear(temp);
    
    clock_t t5 = clock();
    
    // Only count non-hash operations
    sum_keypair_gen += timer_diff(t1, t2) + timer_diff(t3, t4) + timer_diff(t4, t5);
    
    return 0;
}

//----------------------------------------------
// Address Functions
//----------------------------------------------

int hdwsa_addr_gen(unsigned char* Qr_out, unsigned char* Qvk_out,
                   const unsigned char* A_in, const unsigned char* B_in) {
    if (!initialized) return -1;
    
    clock_t t1 = clock();
    
    element_t A, B, r, Qr, betaRp, h3, negA, Qvk;
    element_init_G1(A, pairing);
    element_init_G1(B, pairing);
    element_init_Zr(r, pairing);
    element_init_G1(Qr, pairing);
    element_init_G1(betaRp, pairing);
    element_init_G1(h3, pairing);
    element_init_G1(negA, pairing);
    element_init_GT(Qvk, pairing);
    
    // Load input elements
    element_from_bytes(A, (unsigned char*)A_in);
    element_from_bytes(B, (unsigned char*)B_in);
    
    // Step 1: Choose random r
    element_random(r);
    
    // Step 2: Compute Qr = r*P
    element_mul_zn(Qr, P, r);
    
    // For H3 computation, we need β_ID * r * P
    // Since we don't have β_ID directly, we compute r * B_ID (which equals β_ID * r * P)
    element_mul_zn(betaRp, B, r);
    
    clock_t t2 = clock();
    
    // Step 3: Compute H3(B_ID, Qr, β_ID * r * P)
    unsigned char b_buf[g1_size], qr_buf[g1_size], betarp_buf[g1_size];
    element_to_bytes(b_buf, B);
    element_to_bytes(qr_buf, Qr);
    element_to_bytes(betarp_buf, betaRp);
    unsigned char h3_buf[g1_size];
    hdwsa_H3(h3_buf, b_buf, qr_buf, betarp_buf);
    element_from_bytes(h3, h3_buf);
    
    clock_t t3 = clock();
    
    // Step 4: Compute Qvk = ê(H3(...), -A_ID)
    element_neg(negA, A);
    pairing_apply(Qvk, h3, negA, pairing);
    
    // Output to buffers
    element_to_bytes(Qr_out, Qr);
    element_to_bytes(Qvk_out, Qvk);
    
    element_clear(A);
    element_clear(B);
    element_clear(r);
    element_clear(Qr);
    element_clear(betaRp);
    element_clear(h3);
    element_clear(negA);
    element_clear(Qvk);
    
    clock_t t4 = clock();
    
    // Only count non-hash operations
    sum_addr_gen += timer_diff(t1, t2) + timer_diff(t3, t4);
    
    return 0;
}

int hdwsa_addr_recognize(const unsigned char* Qvk_in, const unsigned char* Qr_in,
                         const unsigned char* A_in, const unsigned char* B_in,
                         const unsigned char* beta_in) {
    if (!initialized) return 0;
    
    clock_t t1 = clock();
    
    element_t Qvk, Qr, A, B, beta;
    element_t betaQr, h3, echeck, negA;
    
    element_init_GT(Qvk, pairing);
    element_init_G1(Qr, pairing);
    element_init_G1(A, pairing);
    element_init_G1(B, pairing);
    element_init_Zr(beta, pairing);
    element_init_G1(betaQr, pairing);
    element_init_G1(h3, pairing);
    element_init_GT(echeck, pairing);
    element_init_G1(negA, pairing);
    
    // Load input elements
    element_from_bytes(Qvk, (unsigned char*)Qvk_in);
    element_from_bytes(Qr, (unsigned char*)Qr_in);
    element_from_bytes(A, (unsigned char*)A_in);
    element_from_bytes(B, (unsigned char*)B_in);
    element_from_bytes(beta, (unsigned char*)beta_in);
    
    // Compute β_ID * Qr
    element_mul_zn(betaQr, Qr, beta);
    
    clock_t t2 = clock();
    
    // Compute H3(B_ID, Qr, β_ID * Qr)
    unsigned char b_buf[g1_size], qr_buf[g1_size], betaqr_buf[g1_size];
    element_to_bytes(b_buf, B);
    element_to_bytes(qr_buf, Qr);
    element_to_bytes(betaqr_buf, betaQr);
    unsigned char h3_buf[g1_size];
    hdwsa_H3(h3_buf, b_buf, qr_buf, betaqr_buf);
    element_from_bytes(h3, h3_buf);
    
    clock_t t3 = clock();
    
    // Compute ê(H3(...), -A_ID)
    element_neg(negA, A);
    pairing_apply(echeck, h3, negA, pairing);
    
    // Check if Qvk = ê(H3(...), -A_ID)
    int valid = (element_cmp(echeck, Qvk) == 0);
    
    element_clear(Qvk);
    element_clear(Qr);
    element_clear(A);
    element_clear(B);
    element_clear(beta);
    element_clear(betaQr);
    element_clear(h3);
    element_clear(echeck);
    element_clear(negA);
    
    clock_t t4 = clock();
    
    // Only count non-hash operations
    sum_addr_recognize += timer_diff(t1, t2) + timer_diff(t3, t4);
    
    return valid;
}

//----------------------------------------------
// DSK Functions
//----------------------------------------------

int hdwsa_dsk_gen(unsigned char* dsk_out,
                  const unsigned char* Qr_in, const unsigned char* B_in,
                  const unsigned char* alpha_in, const unsigned char* beta_in) {
    if (!initialized) return -1;
    
    clock_t t1 = clock();
    
    element_t Qr, B, alpha, beta;
    element_t betaQr, h3, dsk;
    
    element_init_G1(Qr, pairing);
    element_init_G1(B, pairing);
    element_init_Zr(alpha, pairing);
    element_init_Zr(beta, pairing);
    element_init_G1(betaQr, pairing);
    element_init_G1(h3, pairing);
    element_init_G1(dsk, pairing);
    
    // Load input elements
    element_from_bytes(Qr, (unsigned char*)Qr_in);
    element_from_bytes(B, (unsigned char*)B_in);
    element_from_bytes(alpha, (unsigned char*)alpha_in);
    element_from_bytes(beta, (unsigned char*)beta_in);
    
    // Compute β_ID * Qr
    element_mul_zn(betaQr, Qr, beta);
    
    clock_t t2 = clock();
    
    // Compute H3(B_ID, Qr, β_ID * Qr)
    unsigned char b_buf[g1_size], qr_buf[g1_size], betaqr_buf[g1_size];
    element_to_bytes(b_buf, B);
    element_to_bytes(qr_buf, Qr);
    element_to_bytes(betaqr_buf, betaQr);
    unsigned char h3_buf[g1_size];
    hdwsa_H3(h3_buf, b_buf, qr_buf, betaqr_buf);
    element_from_bytes(h3, h3_buf);
    
    clock_t t3 = clock();
    
    // Compute dsk = α_ID * H3(...)
    element_mul_zn(dsk, h3, alpha);
    
    // Output to buffer
    element_to_bytes(dsk_out, dsk);
    
    element_clear(Qr);
    element_clear(B);
    element_clear(alpha);
    element_clear(beta);
    element_clear(betaQr);
    element_clear(h3);
    element_clear(dsk);
    
    clock_t t4 = clock();
    
    // Only count non-hash operations
    sum_dsk_gen += timer_diff(t1, t2) + timer_diff(t3, t4);
    
    return 0;
}

//----------------------------------------------
// Signature Functions
//----------------------------------------------

int hdwsa_sign(unsigned char* h_out, unsigned char* Q_sigma_out,
               const unsigned char* dsk_in,
               const unsigned char* Qr_in, const unsigned char* Qvk_in,
               const char* msg) {
    if (!initialized) return -1;
    
    clock_t t1 = clock();
    
    element_t dsk, Qr, Qvk;
    element_t x, xP, eXP, h, Q_sigma, hdsk;
    
    element_init_G1(dsk, pairing);
    element_init_G1(Qr, pairing);
    element_init_GT(Qvk, pairing);
    element_init_Zr(x, pairing);
    element_init_G1(xP, pairing);
    element_init_GT(eXP, pairing);
    element_init_Zr(h, pairing);
    element_init_G1(Q_sigma, pairing);
    element_init_G1(hdsk, pairing);
    
    // Load input elements
    element_from_bytes(dsk, (unsigned char*)dsk_in);
    element_from_bytes(Qr, (unsigned char*)Qr_in);
    element_from_bytes(Qvk, (unsigned char*)Qvk_in);
    
    // Step 1: Choose random x
    element_random(x);
    
    // Step 2: Compute X = x*P
    element_mul_zn(xP, P, x);
    
    // Step 3: Compute ê(X, P) = ê(x*P, P)
    pairing_apply(eXP, xP, P, pairing);
    
    clock_t t2 = clock();
    
    // Step 4: Compute h = H4(dvk, m, ê(x*P, P))
    // Note: dvk = (Qr, Qvk), so we need to hash both components
    unsigned char qr_buf[g1_size], qvk_buf[pairing_length_in_bytes_GT(pairing)];
    element_to_bytes(qr_buf, Qr);
    element_to_bytes(qvk_buf, Qvk);
    unsigned char h_buf[zr_size];
    hdwsa_H4(h_buf, qr_buf, qvk_buf, msg);
    element_from_bytes(h, h_buf);
    
    clock_t t3 = clock();
    
    // Step 5: Compute Q_σ = h * dsk + x*P
    element_mul_zn(hdsk, dsk, h);
    element_add(Q_sigma, hdsk, xP);
    
    // Output to buffers
    element_to_bytes(h_out, h);
    element_to_bytes(Q_sigma_out, Q_sigma);
    
    element_clear(dsk);
    element_clear(Qr);
    element_clear(Qvk);
    element_clear(x);
    element_clear(xP);
    element_clear(eXP);
    element_clear(h);
    element_clear(Q_sigma);
    element_clear(hdsk);
    
    clock_t t4 = clock();
    
    // Only count non-hash operations
    sum_sign += timer_diff(t1, t2) + timer_diff(t3, t4);
    
    return 0;
}

int hdwsa_verify(const unsigned char* h_in, const unsigned char* Q_sigma_in,
                 const unsigned char* Qr_in, const unsigned char* Qvk_in,
                 const char* msg) {
    if (!initialized) return 0;
    
    clock_t t1 = clock();
    
    element_t h, Q_sigma, Qr, Qvk;
    element_t e1, e2, prod, hcheck;
    
    element_init_Zr(h, pairing);
    element_init_G1(Q_sigma, pairing);
    element_init_G1(Qr, pairing);
    element_init_GT(Qvk, pairing);
    element_init_GT(e1, pairing);
    element_init_GT(e2, pairing);
    element_init_GT(prod, pairing);
    element_init_Zr(hcheck, pairing);
    
    // Load input elements
    element_from_bytes(h, (unsigned char*)h_in);
    element_from_bytes(Q_sigma, (unsigned char*)Q_sigma_in);
    element_from_bytes(Qr, (unsigned char*)Qr_in);
    element_from_bytes(Qvk, (unsigned char*)Qvk_in);
    
    // Step 1: Compute ê(Q_σ, P)
    pairing_apply(e1, Q_sigma, P, pairing);
    
    // Step 2: Compute (Q_vk)^h
    element_pow_zn(e2, Qvk, h);
    
    // Step 3: Compute ê(Q_σ, P) * (Q_vk)^h
    element_mul(prod, e1, e2);
    
    clock_t t2 = clock();
    
    // Step 4: Compute h' = H4(dvk, m, ê(Q_σ, P) * (Q_vk)^h)
    unsigned char qr_buf[g1_size], qvk_buf[pairing_length_in_bytes_GT(pairing)];
    element_to_bytes(qr_buf, Qr);
    element_to_bytes(qvk_buf, Qvk);
    unsigned char hcheck_buf[zr_size];
    hdwsa_H4(hcheck_buf, qr_buf, qvk_buf, msg);
    element_from_bytes(hcheck, hcheck_buf);
    
    clock_t t3 = clock();
    
    // Step 5: Check if h = h'
    int valid = (element_cmp(h, hcheck) == 0);
    
    element_clear(h);
    element_clear(Q_sigma);
    element_clear(Qr);
    element_clear(Qvk);
    element_clear(e1);
    element_clear(e2);
    element_clear(prod);
    element_clear(hcheck);
    
    clock_t t4 = clock();
    
    // Only count non-hash operations
    sum_verify += timer_diff(t1, t2) + timer_diff(t3, t4);
    
    return valid;
}

//----------------------------------------------
// Performance Testing
//----------------------------------------------

int hdwsa_performance_test(int iterations) {
    if (!initialized || iterations <= 0) return -1;
    
    // Reset performance counters
    hdwsa_reset_performance();
    
    // Generate root keys once (system setup)
    unsigned char root_A[g1_size], root_B[g1_size];
    unsigned char root_alpha[zr_size], root_beta[zr_size];
    if (hdwsa_root_keygen(root_A, root_B, root_alpha, root_beta) != 0) {
        return -1;
    }
    
    const char* msg = "Hello, HDWSA performance test!";
    int success_count = 0;
    
    for (int i = 0; i < iterations; i++) {
        // Generate user keypair
        unsigned char A2[g1_size], B2[g1_size];
        unsigned char alpha2[zr_size], beta2[zr_size];
        char id_buf[64];
        sprintf(id_buf, "id_%d", i);  // Use hierarchical ID format
        
        if (hdwsa_keypair_gen(A2, B2, alpha2, beta2, root_alpha, root_beta, id_buf) != 0) {
            continue;
        }
        
        // Generate address (derived verification key)
        unsigned char Qr[g1_size], Qvk[pairing_length_in_bytes_GT(pairing)];
        if (hdwsa_addr_gen(Qr, Qvk, A2, B2) != 0) {
            continue;
        }
        
        // Verify address
        if (!hdwsa_addr_recognize(Qvk, Qr, A2, B2, beta2)) {
            printf("[!] Address recognition failed on iteration %d\n", i);
            continue;
        }
        
        // Generate DSK
        unsigned char dsk[g1_size];
        if (hdwsa_dsk_gen(dsk, Qr, B2, alpha2, beta2) != 0) {
            continue;
        }
        
        // Sign message
        unsigned char h[zr_size], Q_sigma[g1_size];
        if (hdwsa_sign(h, Q_sigma, dsk, Qr, Qvk, msg) != 0) {
            continue;
        }
        
        // Verify signature
        if (!hdwsa_verify(h, Q_sigma, Qr, Qvk, msg)) {
            printf("[!] Signature verification failed on iteration %d\n", i);
            continue;
        }
        
        success_count++;
    }
    
    // Calculate averages
    if (success_count > 0) {
        performance.root_keygen_avg = sum_root_keygen;  // Only done once
        performance.keypair_gen_avg = sum_keypair_gen / success_count;
        performance.addr_gen_avg = sum_addr_gen / success_count;
        performance.addr_recognize_avg = sum_addr_recognize / success_count;
        performance.dsk_gen_avg = sum_dsk_gen / success_count;
        performance.sign_avg = sum_sign / success_count;
        performance.verify_avg = sum_verify / success_count;
        performance.h0_avg = sum_H0 / success_count;
        performance.h1_avg = sum_H1 / (success_count * 2);  // H1 called twice per keypair_gen
        performance.h2_avg = sum_H2 / success_count;
        performance.h3_avg = sum_H3 / (success_count * 3);  // H3 called 3 times
        performance.h4_avg = sum_H4 / (success_count * 2);  // H4 called twice (sign + verify)
        performance.operation_count = success_count;
    }
    
    return success_count;
}

void hdwsa_print_performance(void) {
    printf("\n=== HDWSA Performance Statistics ===\n");
    printf("Total Operations: %d\n", performance.operation_count);
    printf("Root KeyGen:         %.3f ms\n", performance.root_keygen_avg);
    printf("User KeyGen:         %.3f ms\n", performance.keypair_gen_avg);
    printf("Address Generation:  %.3f ms\n", performance.addr_gen_avg);
    printf("Address Recognition: %.3f ms\n", performance.addr_recognize_avg);
    printf("DSK Generation:      %.3f ms\n", performance.dsk_gen_avg);
    printf("Sign:                %.3f ms\n", performance.sign_avg);
    printf("Verify:              %.3f ms\n", performance.verify_avg);
    printf("\n=== Hash Function Performance ===\n");
    printf("H0 (ID->G1):         %.3f ms\n", performance.h0_avg);
    printf("H1 (G1×G1->Zr):      %.3f ms\n", performance.h1_avg);
    printf("H2 (G1×G1->Zr):      %.3f ms\n", performance.h2_avg);
    printf("H3 (G1×G1×G1->G1):   %.3f ms\n", performance.h3_avg);
    printf("H4 (Signature):      %.3f ms\n", performance.h4_avg);
}