/****************************************************************************
 * File: core.c
 * Desc: Core cryptographic functions for HDWSA scheme
 * Note: Framework implementation - actual HDWSA logic to be added
 ****************************************************************************/

#include "core.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <openssl/sha.h>
#include <openssl/hmac.h>

//----------------------------------------------
// Global State
//----------------------------------------------
static pairing_t pairing;
static element_t g;  // Generator of G1
static int initialized = 0;

// Performance counters
static double sumKeygen = 0;
static double sumSign = 0;
static double sumVerify = 0;
static double sumDerive = 0;
static double sumHash = 0;
static int total_operations = 0;

//----------------------------------------------
// Utility Functions
//----------------------------------------------
static double timer_diff(clock_t start, clock_t end) {
    return ((double)(end - start)) / CLOCKS_PER_SEC * 1000.0;
}

//----------------------------------------------
// Library Management
//----------------------------------------------
int hdwsa_init(const char* param_file) {
    if (initialized) {
        hdwsa_cleanup();
    }
    
    // Initialize pairing
    if (pairing_init_set_str(pairing, param_file) != 0) {
        fprintf(stderr, "HDWSA: Failed to initialize pairing from %s\n", param_file);
        return -1;
    }
    
    // Initialize generator
    element_init_G1(g, pairing);
    element_random(g);  // In real implementation, use standard generator
    
    // Reset performance counters
    hdwsa_reset_performance();
    
    initialized = 1;
    printf("✅ HDWSA initialized with parameter file: %s\n", param_file);
    
    return 0;
}

int hdwsa_is_initialized(void) {
    return initialized;
}

void hdwsa_cleanup(void) {
    if (initialized) {
        element_clear(g);
        pairing_clear(pairing);
        initialized = 0;
    }
}

void hdwsa_reset_performance(void) {
    sumKeygen = sumSign = sumVerify = sumDerive = sumHash = 0;
    total_operations = 0;
}

pairing_t* hdwsa_get_pairing(void) {
    return initialized ? &pairing : NULL;
}

//----------------------------------------------
// Key Management Functions
//----------------------------------------------
void hdwsa_key_init(hdwsa_key_t* key) {
    if (!initialized || !key) return;
    
    element_init_Zr(key->master_secret, pairing);
    element_init_G1(key->master_public, pairing);
    element_init_Zr(key->chain_code, pairing);
    key->depth = 0;
    memset(key->fingerprint, 0, 4);
}

void hdwsa_key_clear(hdwsa_key_t* key) {
    if (!key) return;
    
    if (initialized) {
        element_clear(key->master_secret);
        element_clear(key->master_public);
        element_clear(key->chain_code);
    }
    memset(key, 0, sizeof(hdwsa_key_t));
}

void hdwsa_key_copy(hdwsa_key_t* dest, const hdwsa_key_t* src) {
    if (!dest || !src || !initialized) return;
    
    element_set(dest->master_secret, src->master_secret);
    element_set(dest->master_public, src->master_public);
    element_set(dest->chain_code, src->chain_code);
    dest->depth = src->depth;
    memcpy(dest->fingerprint, src->fingerprint, 4);
}

//----------------------------------------------
// Hash Functions
//----------------------------------------------
void hdwsa_hash_to_zr(element_t hash_out, const unsigned char* data, int len) {
    if (!initialized) return;
    
    clock_t t1 = clock();
    
    // Use SHA256 and map to Zr
    unsigned char hash[SHA256_DIGEST_LENGTH];
    SHA256(data, len, hash);
    
    element_from_hash(hash_out, hash, SHA256_DIGEST_LENGTH);
    
    clock_t t2 = clock();
    sumHash += timer_diff(t1, t2);
}

void hdwsa_hash_to_g1(element_t hash_out, const unsigned char* data, int len) {
    if (!initialized) return;
    
    clock_t t1 = clock();
    
    // Use SHA256 and map to G1
    unsigned char hash[SHA256_DIGEST_LENGTH];
    SHA256(data, len, hash);
    
    element_from_hash(hash_out, hash, SHA256_DIGEST_LENGTH);
    
    clock_t t2 = clock();
    sumHash += timer_diff(t1, t2);
}

//----------------------------------------------
// Core Cryptographic Functions
//----------------------------------------------
void hdwsa_master_keygen(hdwsa_key_t* master_key, const unsigned char* seed, int seed_len) {
    if (!initialized || !master_key) return;
    
    clock_t t1 = clock();
    
    // Initialize key structure
    hdwsa_key_init(master_key);
    
    // Generate master secret from seed using HMAC-SHA512
    unsigned char hmac_out[64];
    unsigned int hmac_len;
    const char* salt = "HDWSA seed";
    
    HMAC(EVP_sha512(), salt, strlen(salt), seed, seed_len, hmac_out, &hmac_len);
    
    // Split into master secret (32 bytes) and chain code (32 bytes)
    element_from_hash(master_key->master_secret, hmac_out, 32);
    element_from_hash(master_key->chain_code, hmac_out + 32, 32);
    
    // Compute master public key: master_public = master_secret * g
    element_mul_zn(master_key->master_public, g, master_key->master_secret);
    
    master_key->depth = 0;
    memset(master_key->fingerprint, 0, 4);
    
    clock_t t2 = clock();
    sumKeygen += timer_diff(t1, t2);
}

void hdwsa_derive_child_key(hdwsa_key_t* child_key, const hdwsa_key_t* parent_key, 
                           unsigned int index, int hardened) {
    if (!initialized || !child_key || !parent_key) return;
    
    clock_t t1 = clock();
    
    // Initialize child key structure
    hdwsa_key_init(child_key);
    
    // TODO: Implement proper BIP32-style key derivation
    // This is a placeholder implementation
    
    // For now, derive by hashing parent key with index
    unsigned char derive_data[256];
    int data_len = 0;
    
    // Serialize parent chain code
    data_len += element_to_bytes(derive_data + data_len, parent_key->chain_code);
    
    // Add index
    derive_data[data_len++] = (index >> 24) & 0xFF;
    derive_data[data_len++] = (index >> 16) & 0xFF;
    derive_data[data_len++] = (index >> 8) & 0xFF;
    derive_data[data_len++] = index & 0xFF;
    
    // Hash to get child values
    element_t temp_zr;
    element_init_Zr(temp_zr, pairing);
    hdwsa_hash_to_zr(temp_zr, derive_data, data_len);
    
    // child_secret = parent_secret + temp_zr
    element_add(child_key->master_secret, parent_key->master_secret, temp_zr);
    
    // child_public = child_secret * g
    element_mul_zn(child_key->master_public, g, child_key->master_secret);
    
    // Update chain code (simplified)
    hdwsa_hash_to_zr(child_key->chain_code, derive_data, data_len);
    
    child_key->depth = parent_key->depth + 1;
    memcpy(child_key->fingerprint, derive_data, 4);  // Simplified fingerprint
    
    element_clear(temp_zr);
    
    clock_t t2 = clock();
    sumDerive += timer_diff(t1, t2);
}

void hdwsa_keygen(element_t public_key, element_t private_key) {
    if (!initialized) return;
    
    clock_t t1 = clock();
    
    // Generate random private key
    element_random(private_key);
    
    // Compute public key: public_key = private_key * g
    element_mul_zn(public_key, g, private_key);
    
    clock_t t2 = clock();
    sumKeygen += timer_diff(t1, t2);
}

void hdwsa_sign(element_t signature, const unsigned char* message, int msg_len, element_t private_key) {
    if (!initialized) return;
    
    clock_t t1 = clock();
    
    // TODO: Implement proper HDWSA signature algorithm
    // This is a placeholder implementation
    
    element_t hash_msg, k;
    element_init_Zr(hash_msg, pairing);
    element_init_Zr(k, pairing);
    
    // Hash message
    hdwsa_hash_to_zr(hash_msg, message, msg_len);
    
    // Generate random k
    element_random(k);
    
    // signature = (hash_msg + private_key * k) * g (simplified)
    element_t temp;
    element_init_Zr(temp, pairing);
    element_mul(temp, private_key, k);
    element_add(temp, hash_msg, temp);
    element_mul_zn(signature, g, temp);
    
    element_clear(hash_msg);
    element_clear(k);
    element_clear(temp);
    
    clock_t t2 = clock();
    sumSign += timer_diff(t1, t2);
}

int hdwsa_verify(element_t public_key, element_t signature, 
                 const unsigned char* message, int msg_len) {
    if (!initialized) return 0;
    
    clock_t t1 = clock();
    
    // TODO: Implement proper HDWSA verification algorithm
    // This is a placeholder implementation
    
    element_t hash_msg, temp_sig;
    element_init_Zr(hash_msg, pairing);
    element_init_G1(temp_sig, pairing);
    
    // Hash message
    hdwsa_hash_to_zr(hash_msg, message, msg_len);
    
    // Simplified verification: check if signature is in G1
    int result = element_is_sqr(signature);
    
    element_clear(hash_msg);
    element_clear(temp_sig);
    
    clock_t t2 = clock();
    sumVerify += timer_diff(t1, t2);
    
    return result;
}

//----------------------------------------------
// Serialization Functions
//----------------------------------------------
int hdwsa_element_size_G1(void) {
    if (!initialized) return 0;
    return element_length_in_bytes(g);
}

int hdwsa_element_size_Zr(void) {
    if (!initialized) return 0;
    element_t temp;
    element_init_Zr(temp, pairing);
    int size = element_length_in_bytes(temp);
    element_clear(temp);
    return size;
}

int hdwsa_element_to_bytes(element_t elem, unsigned char* buf, int buf_size) {
    if (!initialized) return -1;
    
    int size = element_length_in_bytes(elem);
    if (size > buf_size) return -1;
    
    return element_to_bytes(buf, elem);
}

int hdwsa_element_from_bytes_G1(element_t elem, const unsigned char* buf, int len) {
    if (!initialized) return -1;
    
    element_init_G1(elem, pairing);
    return element_from_bytes(elem, buf);
}

int hdwsa_element_from_bytes_Zr(element_t elem, const unsigned char* buf, int len) {
    if (!initialized) return -1;
    
    element_init_Zr(elem, pairing);
    return element_from_bytes(elem, buf);
}

//----------------------------------------------
// Performance Functions
//----------------------------------------------
void hdwsa_get_performance(hdwsa_performance_t* perf) {
    if (!perf || total_operations == 0) return;
    
    perf->keygen_avg = sumKeygen / total_operations;
    perf->sign_avg = sumSign / total_operations;
    perf->verify_avg = sumVerify / total_operations;
    perf->derive_avg = sumDerive / total_operations;
    perf->hash_avg = sumHash / total_operations;
    perf->operation_count = total_operations;
}

void hdwsa_print_performance(void) {
    if (total_operations == 0) return;
    
    printf("\n=== HDWSA Performance Results ===\n");
    printf("Operations: %d\n", total_operations);
    printf("Avg Keygen Time  : %.3f ms\n", sumKeygen / total_operations);
    printf("Avg Sign Time    : %.3f ms\n", sumSign / total_operations);
    printf("Avg Verify Time  : %.3f ms\n", sumVerify / total_operations);
    printf("Avg Derive Time  : %.3f ms\n", sumDerive / total_operations);
    printf("Avg Hash Time    : %.3f ms\n", sumHash / total_operations);
}

void hdwsa_performance_test(int iterations, double* results) {
    if (!initialized || !results) return;
    
    hdwsa_reset_performance();
    
    element_t public_key, private_key, signature;
    element_init_G1(public_key, pairing);
    element_init_Zr(private_key, pairing);
    element_init_G1(signature, pairing);
    
    // Generate keys once
    hdwsa_keygen(public_key, private_key);
    
    const char* test_message = "HDWSA scheme test message";
    
    for (int i = 0; i < iterations; i++) {
        // Run algorithms
        hdwsa_sign(signature, (const unsigned char*)test_message, 
                  strlen(test_message), private_key);
        hdwsa_verify(public_key, signature, (const unsigned char*)test_message, 
                    strlen(test_message));
    }
    
    total_operations = iterations;
    
    // Fill results array
    results[0] = sumKeygen / 1;           // keygen (only done once)
    results[1] = sumSign / iterations;    // sign
    results[2] = sumVerify / iterations;  // verify
    results[3] = sumDerive / 1;          // derive (not tested in this loop)
    results[4] = sumHash / iterations;    // hash
    
    // Cleanup
    element_clear(public_key);
    element_clear(private_key);
    element_clear(signature);
}