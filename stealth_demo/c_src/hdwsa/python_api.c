/****************************************************************************
 * File: python_api.c
 * Desc: Python interface implementation for HDWSA scheme
 *       Converts between byte arrays and PBC element_t objects
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
    if (!hdwsa_is_initialized()) {
        fprintf(stderr, "HDWSA: Library not initialized\n");
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

void hdwsa_keygen_simple(unsigned char* public_key_out, unsigned char* private_key_out, int buf_size) {
    if (!check_initialized() || !public_key_out || !private_key_out) return;
    
    pairing_t* pairing = hdwsa_get_pairing();
    if (!pairing) return;
    
    // Clear output buffers
    clear_buffer(public_key_out, buf_size);
    clear_buffer(private_key_out, buf_size);
    
    element_t public_key, private_key;
    element_init_G1(public_key, *pairing);
    element_init_Zr(private_key, *pairing);
    
    // Generate key pair
    hdwsa_keygen(public_key, private_key);
    
    // Convert to bytes
    hdwsa_element_to_bytes(public_key, public_key_out, buf_size);
    hdwsa_element_to_bytes(private_key, private_key_out, buf_size);
    
    // Cleanup
    element_clear(public_key);
    element_clear(private_key);
}

void hdwsa_sign_simple(const char* message, const unsigned char* private_key_bytes,
                       unsigned char* signature_out, int buf_size) {
    if (!check_initialized() || !message || !private_key_bytes || !signature_out) return;
    
    pairing_t* pairing = hdwsa_get_pairing();
    if (!pairing) return;
    
    // Clear output buffer
    clear_buffer(signature_out, buf_size);
    
    element_t private_key, signature;
    element_init_Zr(private_key, *pairing);
    element_init_G1(signature, *pairing);
    
    // Convert bytes to elements
    if (hdwsa_element_from_bytes_Zr(private_key, private_key_bytes, buf_size) != 0) {
        goto cleanup;
    }
    
    // Sign message
    int msg_len = strlen(message);
    hdwsa_sign(signature, (const unsigned char*)message, msg_len, private_key);
    
    // Convert result to bytes
    hdwsa_element_to_bytes(signature, signature_out, buf_size);
    
cleanup:
    element_clear(private_key);
    element_clear(signature);
}

int hdwsa_verify_simple(const char* message, const unsigned char* public_key_bytes,
                        const unsigned char* signature_bytes) {
    if (!check_initialized() || !message || !public_key_bytes || !signature_bytes) return 0;
    
    pairing_t* pairing = hdwsa_get_pairing();
    if (!pairing) return 0;
    
    element_t public_key, signature;
    element_init_G1(public_key, *pairing);
    element_init_G1(signature, *pairing);
    int result = 0;
    
    // Convert bytes to elements
    if (hdwsa_element_from_bytes_G1(public_key, public_key_bytes, hdwsa_element_size_G1()) != 0 ||
        hdwsa_element_from_bytes_G1(signature, signature_bytes, hdwsa_element_size_G1()) != 0) {
        goto cleanup;
    }
    
    // Verify signature
    int msg_len = strlen(message);
    result = hdwsa_verify(public_key, signature, (const unsigned char*)message, msg_len);
    
cleanup:
    element_clear(public_key);
    element_clear(signature);
    
    return result;
}

void hdwsa_master_keygen_simple(const unsigned char* seed, int seed_len,
                                unsigned char* master_secret_out, unsigned char* master_public_out,
                                unsigned char* chain_code_out, int buf_size) {
    if (!check_initialized() || !seed || !master_secret_out || !master_public_out || !chain_code_out) return;
    
    // Clear output buffers
    clear_buffer(master_secret_out, buf_size);
    clear_buffer(master_public_out, buf_size);
    clear_buffer(chain_code_out, buf_size);
    
    hdwsa_key_t master_key;
    
    // Generate master key
    hdwsa_master_keygen(&master_key, seed, seed_len);
    
    // Convert to bytes
    hdwsa_element_to_bytes(master_key.master_secret, master_secret_out, buf_size);
    hdwsa_element_to_bytes(master_key.master_public, master_public_out, buf_size);
    hdwsa_element_to_bytes(master_key.chain_code, chain_code_out, buf_size);
    
    // Cleanup
    hdwsa_key_clear(&master_key);
}

void hdwsa_derive_child_simple(const unsigned char* parent_secret_bytes,
                               const unsigned char* parent_public_bytes,
                               const unsigned char* parent_chain_bytes,
                               unsigned int index, int hardened,
                               unsigned char* child_secret_out,
                               unsigned char* child_public_out,
                               unsigned char* child_chain_out, int buf_size) {
    if (!check_initialized() || !parent_secret_bytes || !parent_public_bytes || !parent_chain_bytes ||
        !child_secret_out || !child_public_out || !child_chain_out) return;
    
    // Clear output buffers
    clear_buffer(child_secret_out, buf_size);
    clear_buffer(child_public_out, buf_size);
    clear_buffer(child_chain_out, buf_size);
    
    hdwsa_key_t parent_key, child_key;
    
    // Initialize keys
    hdwsa_key_init(&parent_key);
    
    // Convert parent bytes to elements
    if (hdwsa_element_from_bytes_Zr(parent_key.master_secret, parent_secret_bytes, buf_size) != 0 ||
        hdwsa_element_from_bytes_G1(parent_key.master_public, parent_public_bytes, buf_size) != 0 ||
        hdwsa_element_from_bytes_Zr(parent_key.chain_code, parent_chain_bytes, buf_size) != 0) {
        goto cleanup;
    }
    
    // Derive child key
    hdwsa_derive_child_key(&child_key, &parent_key, index, hardened);
    
    // Convert to bytes
    hdwsa_element_to_bytes(child_key.master_secret, child_secret_out, buf_size);
    hdwsa_element_to_bytes(child_key.master_public, child_public_out, buf_size);
    hdwsa_element_to_bytes(child_key.chain_code, child_chain_out, buf_size);
    
cleanup:
    hdwsa_key_clear(&parent_key);
    hdwsa_key_clear(&child_key);
}

void hdwsa_hash_simple(const unsigned char* data, int data_len, 
                       unsigned char* hash_out, int buf_size) {
    if (!check_initialized() || !data || !hash_out || data_len <= 0) return;
    
    pairing_t* pairing = hdwsa_get_pairing();
    if (!pairing) return;
    
    // Clear output buffer
    clear_buffer(hash_out, buf_size);
    
    element_t result;
    element_init_Zr(result, *pairing);
    
    // Hash data to Zr element
    hdwsa_hash_to_zr(result, data, data_len);
    
    // Convert result to bytes
    hdwsa_element_to_bytes(result, hash_out, buf_size);
    
    element_clear(result);
}

void hdwsa_performance_test_simple(int iterations, double* results) {
    if (!check_initialized() || !results || iterations <= 0) return;
    
    // Clear results array
    memset(results, 0, 5 * sizeof(double));
    
    // Run performance test
    hdwsa_performance_test(iterations, results);
}