/****************************************************************************
 * File: core.c
 * Desc: Core cryptographic functions for Zhao et al. scheme
 * Note: Framework implementation - actual scheme logic to be added
 ****************************************************************************/

#include "core.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

//----------------------------------------------
// Global State
//----------------------------------------------
static zhao_context_t ctx = {0};

// Performance counters
static double sumKeygen = 0;
static double sumSign = 0; 
static double sumVerify = 0;
static double sumHash = 0;
static int total_operations = 0;

//----------------------------------------------
// Utility Functions
//----------------------------------------------
static double timer_diff(clock_t start, clock_t end) {
    return ((double)(end - start)) / CLOCKS_PER_SEC * 1000.0;
}

//----------------------------------------------
// Configuration Parser (same as CryptoNote2)
//----------------------------------------------
int zhao_parse_config(const char* config_file, zhao_context_t* context) {
    FILE *file = fopen(config_file, "r");
    if (!file) {
        fprintf(stderr, "Zhao: Cannot open config file: %s\n", config_file);
        return -1;
    }
    
    char line[256];
    context->nid = NID_X9_62_prime256v1;  // Default to secp256r1
    context->point_size = 33;
    context->scalar_size = 32;
    context->buffer_size = 64;
    strcpy(context->curve_name, "secp256r1");
    strcpy(context->hash_alg, "sha256");
    
    while (fgets(line, sizeof(line), file)) {
        // Skip comments and empty lines
        if (line[0] == '#' || line[0] == '\n' || line[0] == '\r') continue;
        
        char key[64], value[64];
        if (sscanf(line, "%63[^=]=%63s", key, value) == 2) {
            if (strcmp(key, "nid") == 0) {
                if (strcmp(value, "NID_X9_62_prime256v1") == 0) context->nid = NID_X9_62_prime256v1;
                else if (strcmp(value, "NID_secp256k1") == 0) context->nid = NID_secp256k1;
                else if (strcmp(value, "NID_secp384r1") == 0) context->nid = NID_secp384r1;
                else if (strcmp(value, "NID_secp521r1") == 0) context->nid = NID_secp521r1;
            }
            else if (strcmp(key, "point_size") == 0) context->point_size = atoi(value);
            else if (strcmp(key, "scalar_size") == 0) context->scalar_size = atoi(value);
            else if (strcmp(key, "buffer_size") == 0) context->buffer_size = atoi(value);
            else if (strcmp(key, "curve_name") == 0) strncpy(context->curve_name, value, 31);
            else if (strcmp(key, "hash_algorithm") == 0) strncpy(context->hash_alg, value, 15);
        }
    }
    
    fclose(file);
    return 0;
}

//----------------------------------------------
// Library Management
//----------------------------------------------
int zhao_init(const char* config_file) {
    if (ctx.initialized) {
        zhao_cleanup();
    }
    
    // Parse configuration
    if (zhao_parse_config(config_file, &ctx) != 0) {
        return -1;
    }
    
    // Initialize curve
    ctx.group = EC_GROUP_new_by_curve_name(ctx.nid);
    if (!ctx.group) {
        fprintf(stderr, "Zhao: Failed to create EC group for %s\n", ctx.curve_name);
        return -1;
    }
    
    // Get generator point
    const EC_POINT *generator = EC_GROUP_get0_generator(ctx.group);
    if (!generator) {
        fprintf(stderr, "Zhao: Failed to get generator\n");
        EC_GROUP_free(ctx.group);
        return -1;
    }
    ctx.G = EC_POINT_new(ctx.group);
    EC_POINT_copy(ctx.G, generator);
    
    // Get order of the group
    ctx.order = BN_new();
    if (!EC_GROUP_get_order(ctx.group, ctx.order, NULL)) {
        fprintf(stderr, "Zhao: Failed to get group order\n");
        EC_POINT_free(ctx.G);
        EC_GROUP_free(ctx.group);
        return -1;
    }
    
    // Reset performance counters
    zhao_reset_performance();
    
    ctx.initialized = 1;
    printf("✅ Zhao scheme initialized with %s curve\n", ctx.curve_name);
    
    return 0;
}

int zhao_is_initialized(void) {
    return ctx.initialized;
}

void zhao_cleanup(void) {
    if (ctx.initialized) {
        if (ctx.G) EC_POINT_free(ctx.G);
        if (ctx.group) EC_GROUP_free(ctx.group);
        if (ctx.order) BN_free(ctx.order);
        memset(&ctx, 0, sizeof(ctx));
    }
}

void zhao_reset_performance(void) {
    sumKeygen = sumSign = sumVerify = sumHash = 0;
    total_operations = 0;
}

zhao_context_t* zhao_get_context(void) {
    return ctx.initialized ? &ctx : NULL;
}

void zhao_get_sizes(int* point_size, int* scalar_size, int* buffer_size) {
    if (point_size) *point_size = ctx.point_size;
    if (scalar_size) *scalar_size = ctx.scalar_size;  
    if (buffer_size) *buffer_size = ctx.buffer_size;
}

//----------------------------------------------
// Hash Functions  
//----------------------------------------------
void zhao_hash_to_scalar(BIGNUM *out_scalar, const unsigned char *data, int len, BN_CTX *bn_ctx) {
    if (!ctx.initialized) return;
    
    clock_t t1 = clock();
    
    EVP_MD_CTX *mdctx = EVP_MD_CTX_new();
    const EVP_MD *md;
    
    // Select hash algorithm based on config
    if (strcmp(ctx.hash_alg, "sha384") == 0) md = EVP_sha384();
    else if (strcmp(ctx.hash_alg, "sha512") == 0) md = EVP_sha512();
    else md = EVP_sha256();  // default
    
    unsigned char hash[EVP_MAX_MD_SIZE];
    unsigned int hash_len;
    
    EVP_DigestInit_ex(mdctx, md, NULL);
    EVP_DigestUpdate(mdctx, data, len);
    EVP_DigestFinal_ex(mdctx, hash, &hash_len);
    
    BN_bin2bn(hash, hash_len, out_scalar);
    BN_mod(out_scalar, out_scalar, ctx.order, bn_ctx);
    
    EVP_MD_CTX_free(mdctx);
    
    clock_t t2 = clock();
    sumHash += timer_diff(t1, t2);
}

void zhao_hash_point_to_scalar(BIGNUM *out_scalar, EC_POINT *point, BN_CTX *bn_ctx) {
    if (!ctx.initialized) return;
    
    clock_t t1 = clock();
    
    // Convert point to bytes first
    size_t point_len = EC_POINT_point2oct(ctx.group, point, POINT_CONVERSION_COMPRESSED, NULL, 0, bn_ctx);
    unsigned char *point_buf = OPENSSL_malloc(point_len);
    EC_POINT_point2oct(ctx.group, point, POINT_CONVERSION_COMPRESSED, point_buf, point_len, bn_ctx);
    
    // Hash the point bytes
    zhao_hash_to_scalar(out_scalar, point_buf, point_len, bn_ctx);
    
    OPENSSL_free(point_buf);
    
    clock_t t2 = clock();
    sumHash += timer_diff(t1, t2) - sumHash; // Adjust for double counting
}

//----------------------------------------------
// Core Cryptographic Functions
//----------------------------------------------
void zhao_keygen(EC_POINT *public_key, BIGNUM *private_key, BN_CTX *bn_ctx) {
    if (!ctx.initialized) return;
    
    clock_t t1 = clock();
    
    // Generate random private key
    BN_rand_range(private_key, ctx.order);
    
    // Compute public key: public_key = private_key * G
    EC_POINT_mul(ctx.group, public_key, NULL, ctx.G, private_key, bn_ctx);
    
    clock_t t2 = clock();
    sumKeygen += timer_diff(t1, t2);
}

void zhao_sign(EC_POINT *signature, BIGNUM *hash_value, const unsigned char* message, 
               int msg_len, BIGNUM *private_key, BN_CTX *bn_ctx) {
    if (!ctx.initialized) return;
    
    clock_t t1 = clock();
    
    // TODO: Implement Zhao's specific signature algorithm
    // This is a placeholder implementation - needs actual scheme logic
    
    BIGNUM *k = BN_new();
    BIGNUM *temp = BN_new();
    
    // Generate random k
    BN_rand_range(k, ctx.order);
    
    // signature = k * G (placeholder)
    EC_POINT_mul(ctx.group, signature, NULL, ctx.G, k, bn_ctx);
    
    // hash_value = hash(message || signature) (placeholder)
    // In real implementation, this would follow Zhao's specific hash method
    zhao_hash_to_scalar(hash_value, message, msg_len, bn_ctx);
    
    // Combine with private key (placeholder)
    BN_mod_mul(temp, hash_value, private_key, ctx.order, bn_ctx);
    BN_mod_add(hash_value, k, temp, ctx.order, bn_ctx);
    
    BN_free(k);
    BN_free(temp);
    
    clock_t t2 = clock();
    sumSign += timer_diff(t1, t2);
}

int zhao_verify(EC_POINT *public_key, EC_POINT *signature, BIGNUM *hash_value,
                const unsigned char* message, int msg_len, BN_CTX *bn_ctx) {
    if (!ctx.initialized) return 0;
    
    clock_t t1 = clock();
    
    // TODO: Implement Zhao's specific verification algorithm
    // This is a placeholder implementation - needs actual scheme logic
    
    EC_POINT *temp_point = EC_POINT_new(ctx.group);
    BIGNUM *temp_hash = BN_new();
    int result = 0;
    
    // Recompute hash
    zhao_hash_to_scalar(temp_hash, message, msg_len, bn_ctx);
    
    // Placeholder verification: compare hashes
    result = (BN_cmp(hash_value, temp_hash) == 0);
    
    EC_POINT_free(temp_point);
    BN_free(temp_hash);
    
    clock_t t2 = clock();
    sumVerify += timer_diff(t1, t2);
    
    return result;
}

//----------------------------------------------
// Serialization Functions (same as CryptoNote2)
//----------------------------------------------
int zhao_point_to_bytes(EC_POINT *point, unsigned char *buf, int buf_size) {
    if (!ctx.initialized || buf_size < ctx.point_size) return -1;
    
    BN_CTX *bn_ctx = BN_CTX_new();
    size_t len = EC_POINT_point2oct(ctx.group, point, POINT_CONVERSION_COMPRESSED, buf, buf_size, bn_ctx);
    BN_CTX_free(bn_ctx);
    
    return (len > 0) ? (int)len : -1;
}

int zhao_point_from_bytes(EC_POINT *point, const unsigned char *buf, int buf_len) {
    if (!ctx.initialized) return -1;
    
    BN_CTX *bn_ctx = BN_CTX_new();
    int result = EC_POINT_oct2point(ctx.group, point, buf, buf_len, bn_ctx);
    BN_CTX_free(bn_ctx);
    
    return result ? 0 : -1;
}

int zhao_scalar_to_bytes(BIGNUM *scalar, unsigned char *buf, int buf_size) {
    if (!ctx.initialized || buf_size < ctx.scalar_size) return -1;
    
    // Pad to fixed size
    memset(buf, 0, ctx.scalar_size);
    int len = BN_bn2bin(scalar, buf + ctx.scalar_size - BN_num_bytes(scalar));
    
    return len > 0 ? ctx.scalar_size : -1;
}

int zhao_scalar_from_bytes(BIGNUM *scalar, const unsigned char *buf, int buf_len) {
    if (!ctx.initialized || buf_len < ctx.scalar_size) return -1;
    
    BN_bin2bn(buf, ctx.scalar_size, scalar);
    return 0;
}

//----------------------------------------------
// Performance Functions
//----------------------------------------------
void zhao_get_performance(zhao_performance_t* perf) {
    if (!perf || total_operations == 0) return;
    
    perf->keygen_avg = sumKeygen / total_operations;
    perf->sign_avg = sumSign / total_operations;
    perf->verify_avg = sumVerify / total_operations;
    perf->hash_avg = sumHash / total_operations;
    perf->operation_count = total_operations;
}

void zhao_print_performance(void) {
    if (total_operations == 0) return;
    
    printf("\n=== Zhao Scheme Performance Results ===\n");
    printf("Operations: %d\n", total_operations);
    printf("Avg Keygen Time  : %.3f ms\n", sumKeygen / total_operations);
    printf("Avg Sign Time    : %.3f ms\n", sumSign / total_operations);
    printf("Avg Verify Time  : %.3f ms\n", sumVerify / total_operations);
    printf("Avg Hash Time    : %.3f ms\n", sumHash / total_operations);
    printf("Curve: %s, Buffer: %d bytes\n", ctx.curve_name, ctx.buffer_size);
}

void zhao_performance_test(int iterations, double* results) {
    if (!ctx.initialized || !results) return;
    
    zhao_reset_performance();
    
    BN_CTX *bn_ctx = BN_CTX_new();
    
    // Initialize keys
    EC_POINT *public_key = EC_POINT_new(ctx.group);
    BIGNUM *private_key = BN_new();
    
    // Generate keys once
    zhao_keygen(public_key, private_key, bn_ctx);
    
    const char* test_message = "Zhao scheme test message";
    
    for (int i = 0; i < iterations; i++) {
        EC_POINT *signature = EC_POINT_new(ctx.group);
        BIGNUM *hash_value = BN_new();
        
        // Run algorithms
        zhao_sign(signature, hash_value, (const unsigned char*)test_message, 
                 strlen(test_message), private_key, bn_ctx);
        zhao_verify(public_key, signature, hash_value, (const unsigned char*)test_message, 
                   strlen(test_message), bn_ctx);
        
        // Cleanup round
        EC_POINT_free(signature);
        BN_free(hash_value);
    }
    
    total_operations = iterations;
    
    // Fill results array
    results[0] = sumKeygen / 1;           // keygen (only done once)
    results[1] = sumSign / iterations;    // sign
    results[2] = sumVerify / iterations;  // verify  
    results[3] = sumHash / iterations;    // hash
    
    // Cleanup
    EC_POINT_free(public_key);
    BN_free(private_key);
    BN_CTX_free(bn_ctx);
}