#include <pbc/pbc.h>
#include <pbc/pbc_test.h>
#include <openssl/sha.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

// Global pairing and generator
static pairing_t pairing;
static element_t g;

// AddrGen output: Addr (G1)
static element_t A, B, a, b, TK, k;

// Setup: initialize pairing and generator g
void stealth_setup(const char* param_file) {
    char *argv_fake[2];
    argv_fake[0] = "prog";
    argv_fake[1] = (char*)param_file;
    pbc_demo_pairing_init(pairing, 2, argv_fake);

    element_init_G1(g, pairing);
    element_random(g);

    // Generate static keys for test
    element_init_G1(A, pairing);
    element_init_G1(B, pairing);
    element_init_Zr(a, pairing);
    element_init_Zr(b, pairing);
    element_random(a);
    element_random(b);
    element_pow_zn(A, g, a);
    element_pow_zn(B, g, b);

    element_init_G1(TK, pairing);
    element_init_Zr(k, pairing);
    element_random(k);
    element_pow_zn(TK, g, k);
}

// Helper: hash to Zr using SHA256
void hash_to_mpz(mpz_t out, const unsigned char *data, size_t len, mpz_t mod) {
    unsigned char hash[SHA256_DIGEST_LENGTH];
    SHA256(data, len, hash);
    mpz_import(out, SHA256_DIGEST_LENGTH, 1, 1, 0, 0, hash);
    mpz_mod(out, out, mod);
}

// H1: G1 -> Zr
void H1(element_t outZr, element_t inG1) {
    unsigned char buf[512];
    size_t len = element_length_in_bytes(inG1);
    element_to_bytes(buf, inG1);

    mpz_t tmpz; mpz_init(tmpz);
    hash_to_mpz(tmpz, buf, len, pairing->r);
    element_set_mpz(outZr, tmpz);
    mpz_clear(tmpz);
}

// H2: GT -> G1
void H2(element_t outG1, element_t inGT) {
    unsigned char buf[1024];
    size_t len = element_length_in_bytes(inGT);
    element_to_bytes(buf, inGT);

    mpz_t tmpz; mpz_init(tmpz);
    hash_to_mpz(tmpz, buf, len, pairing->r);

    element_t z; element_init_Zr(z, pairing);
    element_set_mpz(z, tmpz);
    element_pow_zn(outG1, g, z);

    mpz_clear(tmpz);
    element_clear(z);
}

// AddrGen: returns Addr (G1) as byte array
int stealth_generate_addr(unsigned char* out_buf, int max_len) {
    element_t Addr, R1, R2, C;
    element_init_G1(Addr, pairing);
    element_init_G1(R1, pairing);
    element_init_G1(R2, pairing);
    element_init_G1(C, pairing);

    element_t rZ, r2Z; 
    element_init_Zr(rZ, pairing);
    element_init_Zr(r2Z, pairing);
    element_random(rZ);

    element_pow_zn(R1, g, rZ);

    element_t Ar_pow_r; element_init_G1(Ar_pow_r, pairing);
    element_pow_zn(Ar_pow_r, A, rZ);
    H1(r2Z, Ar_pow_r);

    element_pow_zn(R2, g, r2Z);
    element_pow_zn(C, B, r2Z);

    element_t pairing_res, pairing_res_powr;
    element_init_GT(pairing_res, pairing);
    element_init_GT(pairing_res_powr, pairing);
    pairing_apply(pairing_res, R2, TK, pairing);
    element_pow_zn(pairing_res_powr, pairing_res, rZ);

    element_t R3; element_init_G1(R3, pairing);
    H2(R3, pairing_res_powr);

    element_mul(Addr, R3, B);
    element_mul(Addr, Addr, C);

    // Output as byte stream
    int nbytes = element_length_in_bytes(Addr);
    if (nbytes > max_len) return -1;
    element_to_bytes(out_buf, Addr);

    // Clear temps
    element_clear(Addr); element_clear(R1); element_clear(R2); element_clear(C);
    element_clear(rZ); element_clear(r2Z); element_clear(Ar_pow_r);
    element_clear(pairing_res); element_clear(pairing_res_powr); element_clear(R3);

    return nbytes;
}

 