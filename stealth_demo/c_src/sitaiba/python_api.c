/****************************************************************************
 * File: python_api.c
 * Desc: Python interface implementation for Sitaiba scheme (simplified)
 ****************************************************************************/

#include "python_api.h"
#include "core.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static int check_initialized() {
    if (!sitaiba_is_initialized()) {
        fprintf(stderr, "Sitaiba: Library not initialized\n");
        return 0;
    }
    return 1;
}

static void clear_buffer(unsigned char* buf, int size) {
    if (buf && size > 0) memset(buf, 0, size);
}

void sitaiba_keygen_simple(unsigned char* public_key_out, unsigned char* private_key_out, int buf_size) {
    if (!check_initialized() || !public_key_out || !private_key_out) return;
    
    pairing_t* pairing = sitaiba_get_pairing();
    if (!pairing) return;
    
    clear_buffer(public_key_out, buf_size);
    clear_buffer(private_key_out, buf_size);
    
    element_t public_key, private_key;
    element_init_G1(public_key, *pairing);
    element_init_Zr(private_key, *pairing);
    
    sitaiba_keygen(public_key, private_key);
    
    sitaiba_element_to_bytes(public_key, public_key_out, buf_size);
    sitaiba_element_to_bytes(private_key, private_key_out, buf_size);
    
    element_clear(public_key);
    element_clear(private_key);
}

void sitaiba_sign_simple(const char* message, const unsigned char* private_key_bytes,
                         unsigned char* signature_out, int buf_size) {
    if (!check_initialized() || !message || !private_key_bytes || !signature_out) return;
    
    pairing_t* pairing = sitaiba_get_pairing();
    if (!pairing) return;
    
    clear_buffer(signature_out, buf_size);
    
    element_t private_key, signature;
    element_init_Zr(private_key, *pairing);
    element_init_G1(signature, *pairing);
    
    if (sitaiba_element_from_bytes_Zr(private_key, private_key_bytes, buf_size) == 0) {
        int msg_len = strlen(message);
        sitaiba_sign(signature, (const unsigned char*)message, msg_len, private_key);
        sitaiba_element_to_bytes(signature, signature_out, buf_size);
    }
    
    element_clear(private_key);
    element_clear(signature);
}

int sitaiba_verify_simple(const char* message, const unsigned char* public_key_bytes,
                          const unsigned char* signature_bytes) {
    if (!check_initialized() || !message || !public_key_bytes || !signature_bytes) return 0;
    
    pairing_t* pairing = sitaiba_get_pairing();
    if (!pairing) return 0;
    
    element_t public_key, signature;
    element_init_G1(public_key, *pairing);
    element_init_G1(signature, *pairing);
    int result = 0;
    
    if (sitaiba_element_from_bytes_G1(public_key, public_key_bytes, sitaiba_element_size_G1()) == 0 &&
        sitaiba_element_from_bytes_G1(signature, signature_bytes, sitaiba_element_size_G1()) == 0) {
        int msg_len = strlen(message);
        result = sitaiba_verify(public_key, signature, (const unsigned char*)message, msg_len);
    }
    
    element_clear(public_key);
    element_clear(signature);
    return result;
}

void sitaiba_issue_credential_simple(const unsigned char* identity, int identity_len,
                                     const unsigned char* issuer_key_bytes,
                                     unsigned char* credential_out, int buf_size) {
    if (!check_initialized() || !identity || !issuer_key_bytes || !credential_out) return;
    
    pairing_t* pairing = sitaiba_get_pairing();
    if (!pairing) return;
    
    clear_buffer(credential_out, buf_size);
    
    element_t issuer_key, credential;
    element_init_Zr(issuer_key, *pairing);
    element_init_G1(credential, *pairing);
    
    if (sitaiba_element_from_bytes_Zr(issuer_key, issuer_key_bytes, buf_size) == 0) {
        sitaiba_issue_credential(credential, identity, identity_len, issuer_key);
        sitaiba_element_to_bytes(credential, credential_out, buf_size);
    }
    
    element_clear(issuer_key);
    element_clear(credential);
}

int sitaiba_verify_credential_simple(const unsigned char* credential_bytes,
                                     const unsigned char* issuer_public_key_bytes,
                                     const unsigned char* identity, int identity_len) {
    if (!check_initialized() || !credential_bytes || !issuer_public_key_bytes || !identity) return 0;
    
    pairing_t* pairing = sitaiba_get_pairing();
    if (!pairing) return 0;
    
    element_t credential, issuer_public_key;
    element_init_G1(credential, *pairing);
    element_init_G1(issuer_public_key, *pairing);
    int result = 0;
    
    if (sitaiba_element_from_bytes_G1(credential, credential_bytes, sitaiba_element_size_G1()) == 0 &&
        sitaiba_element_from_bytes_G1(issuer_public_key, issuer_public_key_bytes, sitaiba_element_size_G1()) == 0) {
        result = sitaiba_verify_credential(credential, issuer_public_key, identity, identity_len);
    }
    
    element_clear(credential);
    element_clear(issuer_public_key);
    return result;
}

void sitaiba_hash_simple(const unsigned char* data, int data_len, 
                         unsigned char* hash_out, int buf_size) {
    if (!check_initialized() || !data || !hash_out || data_len <= 0) return;
    
    pairing_t* pairing = sitaiba_get_pairing();
    if (!pairing) return;
    
    clear_buffer(hash_out, buf_size);
    
    element_t result;
    element_init_Zr(result, *pairing);
    
    sitaiba_hash_to_zr(result, data, data_len);
    sitaiba_element_to_bytes(result, hash_out, buf_size);
    
    element_clear(result);
}

void sitaiba_performance_test_simple(int iterations, double* results) {
    if (!check_initialized() || !results || iterations <= 0) return;
    
    memset(results, 0, 5 * sizeof(double));
    sitaiba_performance_test(iterations, results);
}