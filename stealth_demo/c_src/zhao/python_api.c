/****************************************************************************
 * File: python_api.c
 * Desc: Python interface implementation for Zhao et al. scheme
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
    if (!zhao_is_initialized()) {
        fprintf(stderr, "Zhao: Library not initialized\n");
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

void zhao_keygen_simple(unsigned char* public_key_out, unsigned char* private_key_out, int buf_size) {
    if (!check_initialized() || !public_key_out || !private_key_out) return;
    
    zhao_context_t* ctx = zhao_get_context();
    if (!ctx) return;
    
    // Clear output buffers
    clear_buffer(public_key_out, buf_size);
    clear_buffer(private_key_out, buf_size);
    
    BN_CTX *bn_ctx = BN_CTX_new();
    EC_POINT *public_key = EC_POINT_new(ctx->group);
    BIGNUM *private_key = BN_new();
    
    // Generate key pair
    zhao_keygen(public_key, private_key, bn_ctx);
    
    // Convert to bytes
    zhao_point_to_bytes(public_key, public_key_out, buf_size);
    zhao_scalar_to_bytes(private_key, private_key_out, buf_size);
    
    // Cleanup
    EC_POINT_free(public_key);
    BN_free(private_key);
    BN_CTX_free(bn_ctx);
}

void zhao_sign_simple(const char* message, const unsigned char* private_key_bytes,
                      unsigned char* signature_out, unsigned char* hash_out, int buf_size) {
    if (!check_initialized() || !message || !private_key_bytes || !signature_out || !hash_out) return;
    
    zhao_context_t* ctx = zhao_get_context();
    if (!ctx) return;
    
    // Clear output buffers
    clear_buffer(signature_out, buf_size);
    clear_buffer(hash_out, buf_size);
    
    BN_CTX *bn_ctx = BN_CTX_new();
    BIGNUM *private_key = BN_new();
    EC_POINT *signature = EC_POINT_new(ctx->group);
    BIGNUM *hash_value = BN_new();
    
    // Convert bytes to objects
    if (zhao_scalar_from_bytes(private_key, private_key_bytes, ctx->scalar_size) != 0) {
        goto cleanup;
    }
    
    // Sign message
    int msg_len = strlen(message);
    zhao_sign(signature, hash_value, (const unsigned char*)message, msg_len, private_key, bn_ctx);
    
    // Convert results to bytes
    zhao_point_to_bytes(signature, signature_out, buf_size);
    zhao_scalar_to_bytes(hash_value, hash_out, buf_size);
    
cleanup:
    EC_POINT_free(signature);
    BN_free(hash_value);
    BN_free(private_key);
    BN_CTX_free(bn_ctx);
}

int zhao_verify_simple(const char* message, const unsigned char* public_key_bytes,
                       const unsigned char* signature_bytes, const unsigned char* hash_bytes) {
    if (!check_initialized() || !message || !public_key_bytes || !signature_bytes || !hash_bytes) return 0;
    
    zhao_context_t* ctx = zhao_get_context();
    if (!ctx) return 0;
    
    BN_CTX *bn_ctx = BN_CTX_new();
    EC_POINT *public_key = EC_POINT_new(ctx->group);
    EC_POINT *signature = EC_POINT_new(ctx->group);
    BIGNUM *hash_value = BN_new();
    int result = 0;
    
    // Convert bytes to objects
    if (zhao_point_from_bytes(public_key, public_key_bytes, ctx->point_size) != 0 ||
        zhao_point_from_bytes(signature, signature_bytes, ctx->point_size) != 0 ||
        zhao_scalar_from_bytes(hash_value, hash_bytes, ctx->scalar_size) != 0) {
        goto cleanup;
    }
    
    // Verify signature
    int msg_len = strlen(message);
    result = zhao_verify(public_key, signature, hash_value, (const unsigned char*)message, msg_len, bn_ctx);
    
cleanup:
    EC_POINT_free(public_key);
    EC_POINT_free(signature);
    BN_free(hash_value);
    BN_CTX_free(bn_ctx);
    
    return result;
}

void zhao_hash_simple(const unsigned char* data, int data_len, 
                      unsigned char* hash_out, int buf_size) {
    if (!check_initialized() || !data || !hash_out || data_len <= 0) return;
    
    // Clear output buffer
    clear_buffer(hash_out, buf_size);
    
    BN_CTX *bn_ctx = BN_CTX_new();
    BIGNUM *result = BN_new();
    
    // Hash data to scalar
    zhao_hash_to_scalar(result, data, data_len, bn_ctx);
    
    // Convert result to bytes
    zhao_scalar_to_bytes(result, hash_out, buf_size);
    
    BN_free(result);
    BN_CTX_free(bn_ctx);
}

void zhao_performance_test_simple(int iterations, double* results) {
    if (!check_initialized() || !results || iterations <= 0) return;
    
    // Clear results array
    memset(results, 0, 4 * sizeof(double));
    
    // Run performance test
    zhao_performance_test(iterations, results);
}

void zhao_get_curve_info(char* curve_name, int* point_size, int* scalar_size, int* buffer_size) {
    if (!check_initialized()) return;
    
    zhao_context_t* ctx = zhao_get_context();
    if (!ctx) return;
    
    if (curve_name) {
        strncpy(curve_name, ctx->curve_name, 31);
        curve_name[31] = '\0';
    }
    
    if (point_size) *point_size = ctx->point_size;
    if (scalar_size) *scalar_size = ctx->scalar_size;
    if (buffer_size) *buffer_size = ctx->buffer_size;
}