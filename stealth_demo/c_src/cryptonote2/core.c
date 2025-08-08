/****************************************************************************
 * File: core.c
 * Desc: Core cryptographic functions for CryptoNote2 scheme
 * Based on: Original cryptonote2.c implementation
 ****************************************************************************/

#include "core.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

//----------------------------------------------
// Global State
//----------------------------------------------
static cryptonote2_context_t ctx = {0};

// Performance counters
static double sumH1 = 0;
static double sumGen = 0, sumStat = 0, sumSK = 0;
static int total_operations = 0;

//----------------------------------------------
// Utility Functions
//----------------------------------------------
static double timer_diff(clock_t start, clock_t end) {
    return ((double)(end - start)) / CLOCKS_PER_SEC * 1000.0;
}

//----------------------------------------------
// Configuration Parser
//----------------------------------------------
int cryptonote2_parse_config(const char* config_file, cryptonote2_context_t* context) {
    FILE *file = fopen(config_file, "r");
    if (!file) {
        fprintf(stderr, "CryptoNote2: Cannot open config file: %s\n", config_file);
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
int cryptonote2_init(const char* config_file) {
    if (ctx.initialized) {
        cryptonote2_cleanup();
    }
    
    // Parse configuration
    if (cryptonote2_parse_config(config_file, &ctx) != 0) {
        return -1;
    }
    
    // Initialize curve
    ctx.group = EC_GROUP_new_by_curve_name(ctx.nid);
    if (!ctx.group) {
        fprintf(stderr, "CryptoNote2: Failed to create EC group for %s\n", ctx.curve_name);
        return -1;
    }
    
    // Get generator point
    const EC_POINT *generator = EC_GROUP_get0_generator(ctx.group);
    if (!generator) {
        fprintf(stderr, "CryptoNote2: Failed to get generator\n");
        EC_GROUP_free(ctx.group);
        return -1;
    }
    ctx.G = EC_POINT_new(ctx.group);
    EC_POINT_copy(ctx.G, generator);
    
    // Get order of the group
    ctx.order = BN_new();
    if (!EC_GROUP_get_order(ctx.group, ctx.order, NULL)) {
        fprintf(stderr, "CryptoNote2: Failed to get group order\n");
        EC_POINT_free(ctx.G);
        EC_GROUP_free(ctx.group);
        return -1;
    }
    
    // Reset performance counters
    cryptonote2_reset_performance();
    
    ctx.initialized = 1;
    printf("✅ CryptoNote2 initialized with %s curve\n", ctx.curve_name);
    
    return 0;
}

int cryptonote2_is_initialized(void) {
    return ctx.initialized;
}

void cryptonote2_cleanup(void) {
    if (ctx.initialized) {
        if (ctx.G) EC_POINT_free(ctx.G);
        if (ctx.group) EC_GROUP_free(ctx.group);
        if (ctx.order) BN_free(ctx.order);
        memset(&ctx, 0, sizeof(ctx));
    }
}

void cryptonote2_reset_performance(void) {
    sumH1 = sumGen = sumStat = sumSK = 0;
    total_operations = 0;
}

cryptonote2_context_t* cryptonote2_get_context(void) {
    return ctx.initialized ? &ctx : NULL;
}

void cryptonote2_get_sizes(int* point_size, int* scalar_size, int* buffer_size) {
    if (point_size) *point_size = ctx.point_size;
    if (scalar_size) *scalar_size = ctx.scalar_size;  
    if (buffer_size) *buffer_size = ctx.buffer_size;
}

//----------------------------------------------
// Hash Functions  
//----------------------------------------------
void cryptonote2_H1(BIGNUM *outZr, EC_POINT *inG1, BN_CTX *bn_ctx) {
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
    
    // Convert EC_POINT to bytes
    size_t point_len = EC_POINT_point2oct(ctx.group, inG1, POINT_CONVERSION_COMPRESSED, NULL, 0, bn_ctx);
    unsigned char *point_buf = OPENSSL_malloc(point_len);
    EC_POINT_point2oct(ctx.group, inG1, POINT_CONVERSION_COMPRESSED, point_buf, point_len, bn_ctx);
    
    // Hash the point
    EVP_DigestUpdate(mdctx, point_buf, point_len);
    EVP_DigestFinal_ex(mdctx, hash, &hash_len);
    
    // Convert hash to BIGNUM and reduce modulo order
    BN_bin2bn(hash, hash_len, outZr);
    BN_mod(outZr, outZr, ctx.order, bn_ctx);
    
    // Cleanup
    OPENSSL_free(point_buf);
    EVP_MD_CTX_free(mdctx);
    
    clock_t t2 = clock();
    sumH1 += timer_diff(t1, t2);
}

void cryptonote2_hash_bytes_to_scalar(BIGNUM *out_scalar, const unsigned char *data, int len, BN_CTX *bn_ctx) {
    if (!ctx.initialized) return;
    
    EVP_MD_CTX *mdctx = EVP_MD_CTX_new();
    const EVP_MD *md;
    
    if (strcmp(ctx.hash_alg, "sha384") == 0) md = EVP_sha384();
    else if (strcmp(ctx.hash_alg, "sha512") == 0) md = EVP_sha512();
    else md = EVP_sha256();
    
    unsigned char hash[EVP_MAX_MD_SIZE];
    unsigned int hash_len;
    
    EVP_DigestInit_ex(mdctx, md, NULL);
    EVP_DigestUpdate(mdctx, data, len);
    EVP_DigestFinal_ex(mdctx, hash, &hash_len);
    
    BN_bin2bn(hash, hash_len, out_scalar);
    BN_mod(out_scalar, out_scalar, ctx.order, bn_ctx);
    
    EVP_MD_CTX_free(mdctx);
}

//----------------------------------------------
// Core Cryptographic Functions
//----------------------------------------------
void cryptonote2_keygen(EC_POINT *A, EC_POINT *B, BIGNUM *a, BIGNUM *b, BN_CTX *bn_ctx) {
    if (!ctx.initialized) return;
    
    // Generate random private keys
    BN_rand_range(a, ctx.order);
    BN_rand_range(b, ctx.order);
    
    // Compute public keys: A = a*G, B = b*G
    EC_POINT_mul(ctx.group, A, NULL, ctx.G, a, bn_ctx);
    EC_POINT_mul(ctx.group, B, NULL, ctx.G, b, bn_ctx);
}

void cryptonote2_addr_gen(EC_POINT *PK_one, EC_POINT *R, EC_POINT *A, EC_POINT *B, BN_CTX *bn_ctx) {
    if (!ctx.initialized) return;
    
    clock_t t1 = clock();
    
    BIGNUM *r = BN_new();
    BIGNUM *r_out = BN_new();
    EC_POINT *temp = EC_POINT_new(ctx.group);
    EC_POINT *r_out_G = EC_POINT_new(ctx.group);
    
    // Generate random r
    BN_rand_range(r, ctx.order);
    
    // R = r * G
    EC_POINT_mul(ctx.group, R, NULL, ctx.G, r, bn_ctx);
    
    // temp = r * A
    EC_POINT_mul(ctx.group, temp, NULL, A, r, bn_ctx);
    
    // r_out = hash(r*A)
    cryptonote2_H1(r_out, temp, bn_ctx);
    
    // PK_one = r_out*G + B
    EC_POINT_mul(ctx.group, r_out_G, NULL, ctx.G, r_out, bn_ctx);
    EC_POINT_add(ctx.group, PK_one, r_out_G, B, bn_ctx);
    
    // Cleanup
    BN_free(r);
    BN_free(r_out);
    EC_POINT_free(temp);
    EC_POINT_free(r_out_G);
    
    clock_t t2 = clock();
    sumGen += timer_diff(t1, t2);
}

int cryptonote2_addr_verify(EC_POINT *PK_one, EC_POINT *R, BIGNUM *a, EC_POINT *B, BN_CTX *bn_ctx) {
    if (!ctx.initialized) return 0;
    
    clock_t t1 = clock();
    
    BIGNUM *r_out = BN_new();
    EC_POINT *temp = EC_POINT_new(ctx.group);
    EC_POINT *r_out_G = EC_POINT_new(ctx.group);
    EC_POINT *check_PK = EC_POINT_new(ctx.group);
    
    // temp = a * R
    EC_POINT_mul(ctx.group, temp, NULL, R, a, bn_ctx);
    
    // r_out = hash(a*R)
    cryptonote2_H1(r_out, temp, bn_ctx);
    
    // check_PK = r_out*G + B
    EC_POINT_mul(ctx.group, r_out_G, NULL, ctx.G, r_out, bn_ctx);
    EC_POINT_add(ctx.group, check_PK, r_out_G, B, bn_ctx);
    
    // Check if PK_one == check_PK
    int ok = (EC_POINT_cmp(ctx.group, PK_one, check_PK, bn_ctx) == 0);
    
    // Cleanup
    BN_free(r_out);
    EC_POINT_free(temp);
    EC_POINT_free(r_out_G);
    EC_POINT_free(check_PK);
    
    clock_t t2 = clock();
    sumStat += timer_diff(t1, t2);
    
    return ok;
}

void cryptonote2_onetime_sk_gen(BIGNUM *sk_ot, EC_POINT *R, BIGNUM *a, BIGNUM *b, BN_CTX *bn_ctx) {
    if (!ctx.initialized) return;
    
    clock_t t1 = clock();
    
    BIGNUM *r_out = BN_new();
    EC_POINT *temp = EC_POINT_new(ctx.group);
    
    // temp = a * R
    EC_POINT_mul(ctx.group, temp, NULL, R, a, bn_ctx);
    
    // r_out = hash(a*R)
    cryptonote2_H1(r_out, temp, bn_ctx);
    
    // sk_ot = r_out + b
    BN_mod_add(sk_ot, r_out, b, ctx.order, bn_ctx);
    
    // Cleanup
    BN_free(r_out);
    EC_POINT_free(temp);
    
    clock_t t2 = clock();
    sumSK += timer_diff(t1, t2);
}

//----------------------------------------------
// Serialization Functions
//----------------------------------------------
int cryptonote2_point_to_bytes(EC_POINT *point, unsigned char *buf, int buf_size) {
    if (!ctx.initialized || buf_size < ctx.point_size) return -1;
    
    BN_CTX *bn_ctx = BN_CTX_new();
    size_t len = EC_POINT_point2oct(ctx.group, point, POINT_CONVERSION_COMPRESSED, buf, buf_size, bn_ctx);
    BN_CTX_free(bn_ctx);
    
    return (len > 0) ? (int)len : -1;
}

int cryptonote2_point_from_bytes(EC_POINT *point, const unsigned char *buf, int buf_len) {
    if (!ctx.initialized) return -1;
    
    BN_CTX *bn_ctx = BN_CTX_new();
    int result = EC_POINT_oct2point(ctx.group, point, buf, buf_len, bn_ctx);
    BN_CTX_free(bn_ctx);
    
    return result ? 0 : -1;
}

int cryptonote2_scalar_to_bytes(BIGNUM *scalar, unsigned char *buf, int buf_size) {
    if (!ctx.initialized || buf_size < ctx.scalar_size) return -1;
    
    // Pad to fixed size
    memset(buf, 0, ctx.scalar_size);
    int len = BN_bn2bin(scalar, buf + ctx.scalar_size - BN_num_bytes(scalar));
    
    return len > 0 ? ctx.scalar_size : -1;
}

int cryptonote2_scalar_from_bytes(BIGNUM *scalar, const unsigned char *buf, int buf_len) {
    if (!ctx.initialized || buf_len < ctx.scalar_size) return -1;
    
    BN_bin2bn(buf, ctx.scalar_size, scalar);
    return 0;
}

//----------------------------------------------
// Performance Functions
//----------------------------------------------
void cryptonote2_get_performance(cryptonote2_performance_t* perf) {
    if (!perf || total_operations == 0) return;
    
    perf->addr_gen_avg = sumGen / total_operations;
    perf->addr_verify_avg = sumStat / total_operations;
    perf->onetime_sk_avg = sumSK / total_operations;
    perf->h1_avg = sumH1 / (3 * total_operations);  // H1 called 3 times per full operation
    perf->operation_count = total_operations;
}

void cryptonote2_print_performance(void) {
    if (total_operations == 0) return;
    
    printf("\n=== CryptoNote2 Performance Results ===\n");
    printf("Operations: %d\n", total_operations);
    printf("Avg AddrGen Time     : %.3f ms\n", sumGen / total_operations);
    printf("Avg AddrVerify Time  : %.3f ms\n", sumStat / total_operations);
    printf("Avg OnetimeSKGen Time: %.3f ms\n", sumSK / total_operations);
    printf("Avg H1 Time          : %.3f ms\n", sumH1 / (3 * total_operations));
    printf("Curve: %s, Buffer: %d bytes\n", ctx.curve_name, ctx.buffer_size);
}

void cryptonote2_performance_test(int iterations, double* results) {
    if (!ctx.initialized || !results) return;
    
    cryptonote2_reset_performance();
    
    BN_CTX *bn_ctx = BN_CTX_new();
    
    // Initialize keys
    EC_POINT *A = EC_POINT_new(ctx.group);
    EC_POINT *B = EC_POINT_new(ctx.group);
    BIGNUM *a = BN_new();
    BIGNUM *b = BN_new();
    
    // Generate keys
    cryptonote2_keygen(A, B, a, b, bn_ctx);
    
    for (int i = 0; i < iterations; i++) {
        EC_POINT *PK_one = EC_POINT_new(ctx.group);
        EC_POINT *R = EC_POINT_new(ctx.group);
        BIGNUM *sk_ot = BN_new();
        
        // Run algorithms
        cryptonote2_addr_gen(PK_one, R, A, B, bn_ctx);
        cryptonote2_addr_verify(PK_one, R, a, B, bn_ctx);
        cryptonote2_onetime_sk_gen(sk_ot, R, a, b, bn_ctx);
        
        // Cleanup round
        EC_POINT_free(PK_one);
        EC_POINT_free(R);
        BN_free(sk_ot);
    }
    
    total_operations = iterations;
    
    // Fill results array
    results[0] = sumGen / iterations;    // addr_gen
    results[1] = sumStat / iterations;   // addr_verify  
    results[2] = sumSK / iterations;     // onetime_sk
    results[3] = sumH1 / (3 * iterations); // h1
    
    // Cleanup
    EC_POINT_free(A);
    EC_POINT_free(B);
    BN_free(a);
    BN_free(b);
    BN_CTX_free(bn_ctx);
}