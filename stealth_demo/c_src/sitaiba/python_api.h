/****************************************************************************
 * File: python_api.h  
 * Desc: Python interface functions for Sitaiba et al. scheme
 ****************************************************************************/

#ifndef SITAIBA_PYTHON_API_H
#define SITAIBA_PYTHON_API_H

//----------------------------------------------
// Python Interface Functions
//----------------------------------------------

void sitaiba_keygen_simple(unsigned char* public_key_out, unsigned char* private_key_out, int buf_size);

void sitaiba_sign_simple(const char* message, const unsigned char* private_key_bytes,
                         unsigned char* signature_out, int buf_size);

int sitaiba_verify_simple(const char* message, const unsigned char* public_key_bytes,
                          const unsigned char* signature_bytes);

void sitaiba_issue_credential_simple(const unsigned char* identity, int identity_len,
                                     const unsigned char* issuer_key_bytes,
                                     unsigned char* credential_out, int buf_size);

int sitaiba_verify_credential_simple(const unsigned char* credential_bytes,
                                     const unsigned char* issuer_public_key_bytes,
                                     const unsigned char* identity, int identity_len);

void sitaiba_hash_simple(const unsigned char* data, int data_len, 
                         unsigned char* hash_out, int buf_size);

void sitaiba_performance_test_simple(int iterations, double* results);

#endif /* SITAIBA_PYTHON_API_H */