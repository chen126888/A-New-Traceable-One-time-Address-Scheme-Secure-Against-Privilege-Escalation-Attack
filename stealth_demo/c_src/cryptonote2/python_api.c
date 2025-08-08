/****************************************************************************
 * File: python_api.c
 * Desc: Python interface implementation for CryptoNote2 scheme
 *       Converts between byte arrays and OpenSSL objects
 ****************************************************************************/

#include "python_api.h"
#include "core.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

//----------------------------------------------
// Helper Functions for Error Checking
//----------------------------------------------
static int check_initialized() {
    if (!cryptonote2_is_initialized()) {
        fprintf(stderr, "CryptoNote2: Library not initialized\n");
        return 0;
    }
    return 1;
}

static void clear_buffer(unsigned char* buf, int size) {
    if (buf && size > 0) {
        memset(buf, 0, size);
    }
}

//----------------------------------------------
// Python Interface Implementations
//----------------------------------------------

void cryptonote2_keygen_simple(unsigned char* A_out, unsigned char* B_out,
                               unsigned char* a_out, unsigned char* b_out, int buf_size) {
    if (!check_initialized() || !A_out || !B_out || !a_out || !b_out) return;
    
    cryptonote2_context_t* ctx = cryptonote2_get_context();
    if (!ctx) return;
    
    // Clear output buffers
    clear_buffer(A_out, buf_size);
    clear_buffer(B_out, buf_size);
    clear_buffer(a_out, buf_size);
    clear_buffer(b_out, buf_size);
    
    BN_CTX *bn_ctx = BN_CTX_new();
    EC_POINT *A = EC_POINT_new(ctx->group);
    EC_POINT *B = EC_POINT_new(ctx->group);
    BIGNUM *a = BN_new();
    BIGNUM *b = BN_new();
    
    // Generate key pair
    cryptonote2_keygen(A, B, a, b, bn_ctx);
    
    // Convert to bytes
    cryptonote2_point_to_bytes(A, A_out, buf_size);
    cryptonote2_point_to_bytes(B, B_out, buf_size);
    cryptonote2_scalar_to_bytes(a, a_out, buf_size);
    cryptonote2_scalar_to_bytes(b, b_out, buf_size);
    
    // Cleanup
    EC_POINT_free(A);
    EC_POINT_free(B);
    BN_free(a);
    BN_free(b);
    BN_CTX_free(bn_ctx);
}

void cryptonote2_addr_gen_simple(const unsigned char* A_bytes, const unsigned char* B_bytes,
                                 unsigned char* pk_one_out, unsigned char* r_out, int buf_size) {
    if (!check_initialized() || !A_bytes || !B_bytes || !pk_one_out || !r_out) return;
    
    cryptonote2_context_t* ctx = cryptonote2_get_context();
    if (!ctx) return;
    
    // Clear output buffers
    clear_buffer(pk_one_out, buf_size);
    clear_buffer(r_out, buf_size);
    
    BN_CTX *bn_ctx = BN_CTX_new();
    EC_POINT *A = EC_POINT_new(ctx->group);
    EC_POINT *B = EC_POINT_new(ctx->group);
    EC_POINT *PK_one = EC_POINT_new(ctx->group);
    EC_POINT *R = EC_POINT_new(ctx->group);
    
    // Convert bytes to points
    if (cryptonote2_point_from_bytes(A, A_bytes, ctx->point_size) != 0 ||
        cryptonote2_point_from_bytes(B, B_bytes, ctx->point_size) != 0) {
        goto cleanup;
    }
    
    // Generate one-time address
    cryptonote2_addr_gen(PK_one, R, A, B, bn_ctx);
    
    // Convert results to bytes
    cryptonote2_point_to_bytes(PK_one, pk_one_out, buf_size);
    cryptonote2_point_to_bytes(R, r_out, buf_size);
    
cleanup:
    EC_POINT_free(A);
    EC_POINT_free(B);
    EC_POINT_free(PK_one);
    EC_POINT_free(R);
    BN_CTX_free(bn_ctx);
}

int cryptonote2_addr_verify_simple(const unsigned char* pk_one_bytes, const unsigned char* r_bytes,
                                   const unsigned char* a_bytes, const unsigned char* b_bytes) {
    if (!check_initialized() || !pk_one_bytes || !r_bytes || !a_bytes || !b_bytes) return 0;
    
    cryptonote2_context_t* ctx = cryptonote2_get_context();
    if (!ctx) return 0;
    
    BN_CTX *bn_ctx = BN_CTX_new();
    EC_POINT *PK_one = EC_POINT_new(ctx->group);
    EC_POINT *R = EC_POINT_new(ctx->group);
    EC_POINT *B = EC_POINT_new(ctx->group);
    BIGNUM *a = BN_new();
    int result = 0;
    
    // Convert bytes to objects
    if (cryptonote2_point_from_bytes(PK_one, pk_one_bytes, ctx->point_size) != 0 ||
        cryptonote2_point_from_bytes(R, r_bytes, ctx->point_size) != 0 ||
        cryptonote2_point_from_bytes(B, b_bytes, ctx->point_size) != 0 ||
        cryptonote2_scalar_from_bytes(a, a_bytes, ctx->scalar_size) != 0) {
        goto cleanup;
    }
    
    // Verify address
    result = cryptonote2_addr_verify(PK_one, R, a, B, bn_ctx);
    
cleanup:
    EC_POINT_free(PK_one);
    EC_POINT_free(R);
    EC_POINT_free(B);
    BN_free(a);
    BN_CTX_free(bn_ctx);
    
    return result;
}

void cryptonote2_onetime_sk_gen_simple(const unsigned char* r_bytes, const unsigned char* a_bytes,
                                       const unsigned char* b_bytes, unsigned char* sk_out, int buf_size) {
    if (!check_initialized() || !r_bytes || !a_bytes || !b_bytes || !sk_out) return;
    
    cryptonote2_context_t* ctx = cryptonote2_get_context();
    if (!ctx) return;
    
    // Clear output buffer
    clear_buffer(sk_out, buf_size);
    
    BN_CTX *bn_ctx = BN_CTX_new();
    EC_POINT *R = EC_POINT_new(ctx->group);
    BIGNUM *a = BN_new();
    BIGNUM *b = BN_new();
    BIGNUM *sk_ot = BN_new();
    
    // Convert bytes to objects
    if (cryptonote2_point_from_bytes(R, r_bytes, ctx->point_size) != 0 ||
        cryptonote2_scalar_from_bytes(a, a_bytes, ctx->scalar_size) != 0 ||
        cryptonote2_scalar_from_bytes(b, b_bytes, ctx->scalar_size) != 0) {
        goto cleanup;
    }
    
    // Generate one-time secret key
    cryptonote2_onetime_sk_gen(sk_ot, R, a, b, bn_ctx);
    
    // Convert result to bytes
    cryptonote2_scalar_to_bytes(sk_ot, sk_out, buf_size);
    
cleanup:
    EC_POINT_free(R);
    BN_free(a);
    BN_free(b);
    BN_free(sk_ot);
    BN_CTX_free(bn_ctx);
}

void cryptonote2_hash_simple(const unsigned char* point_bytes, unsigned char* hash_out, int buf_size) {
    if (!check_initialized() || !point_bytes || !hash_out) return;
    
    cryptonote2_context_t* ctx = cryptonote2_get_context();
    if (!ctx) return;
    
    // Clear output buffer
    clear_buffer(hash_out, buf_size);
    
    BN_CTX *bn_ctx = BN_CTX_new();
    EC_POINT *point = EC_POINT_new(ctx->group);
    BIGNUM *result = BN_new();
    
    // Convert bytes to point
    if (cryptonote2_point_from_bytes(point, point_bytes, ctx->point_size) != 0) {
        goto cleanup;
    }
    
    // Hash point to scalar
    cryptonote2_H1(result, point, bn_ctx);
    
    // Convert result to bytes
    cryptonote2_scalar_to_bytes(result, hash_out, buf_size);
    
cleanup:
    EC_POINT_free(point);
    BN_free(result);
    BN_CTX_free(bn_ctx);
}

void cryptonote2_hash_data_simple(const unsigned char* data, int data_len,
                                  unsigned char* hash_out, int buf_size) {
    if (!check_initialized() || !data || !hash_out || data_len <= 0) return;
    
    // Clear output buffer
    clear_buffer(hash_out, buf_size);
    
    BN_CTX *bn_ctx = BN_CTX_new();
    BIGNUM *result = BN_new();
    
    // Hash data to scalar
    cryptonote2_hash_bytes_to_scalar(result, data, data_len, bn_ctx);
    
    // Convert result to bytes
    cryptonote2_scalar_to_bytes(result, hash_out, buf_size);
    
    BN_free(result);
    BN_CTX_free(bn_ctx);
}

void cryptonote2_performance_test_simple(int iterations, double* results) {
    if (!check_initialized() || !results || iterations <= 0) return;
    
    // Clear results array
    memset(results, 0, 4 * sizeof(double));
    
    // Run performance test
    cryptonote2_performance_test(iterations, results);
}

void cryptonote2_get_curve_info(char* curve_name, int* point_size, int* scalar_size, int* buffer_size) {
    if (!check_initialized()) return;
    
    cryptonote2_context_t* ctx = cryptonote2_get_context();
    if (!ctx) return;
    
    if (curve_name) {
        strncpy(curve_name, ctx->curve_name, 31);
        curve_name[31] = '\0';
    }
    
    if (point_size) *point_size = ctx->point_size;
    if (scalar_size) *scalar_size = ctx->scalar_size;
    if (buffer_size) *buffer_size = ctx->buffer_size;
}