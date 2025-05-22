#include <pbc/pbc.h>
#include <pbc/pbc_test.h>
#include <openssl/sha.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

// Global pairing and generator
static pairing_t pairing;
static element_t g;

// Static keys
static element_t A, B, a, b, TK, k;

void stealth_setup(const char* param_file) {
    char *argv_fake[2];
    argv_fake[0] = "prog";
    argv_fake[1] = (char*)param_file;
    pbc_demo_pairing_init(pairing, 2, argv_fake);

    element_init_G1(g, pairing);
    element_random(g);

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

void hash_to_mpz(mpz_t out, const unsigned char *data, size_t len, mpz_t mod) {
    unsigned char hash[SHA256_DIGEST_LENGTH];
    SHA256(data, len, hash);
    mpz_import(out, SHA256_DIGEST_LENGTH, 1, 1, 0, 0, hash);
    mpz_mod(out, out, mod);
}

void H1(element_t outZr, element_t inG1) {
    unsigned char buf[512];
    size_t len = element_length_in_bytes(inG1);
    element_to_bytes(buf, inG1);

    mpz_t tmpz; mpz_init(tmpz);
    hash_to_mpz(tmpz, buf, len, pairing->r);
    element_set_mpz(outZr, tmpz);
    mpz_clear(tmpz);
}

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

void H3(element_t outG1, element_t inG1) {
    unsigned char buf[512];
    size_t len = element_length_in_bytes(inG1);
    element_to_bytes(buf, inG1);

    mpz_t tmpz; mpz_init(tmpz);
    hash_to_mpz(tmpz, buf, len, pairing->r);

    element_t z; element_init_Zr(z, pairing);
    element_set_mpz(z, tmpz);
    element_pow_zn(outG1, g, z);

    mpz_clear(tmpz);
    element_clear(z);
}

void H4(element_t outZr, element_t addr, const char* msg, element_t XGT) {
    unsigned char buf[2048], g1buf[512], g2buf[512];
    size_t len1 = element_length_in_bytes(addr);
    size_t len2 = element_length_in_bytes(XGT);
    size_t msglen = strlen(msg);

    element_to_bytes(g1buf, addr);
    element_to_bytes(g2buf, XGT);

    memcpy(buf, g1buf, len1);
    memcpy(buf + len1, msg, msglen);
    memcpy(buf + len1 + msglen, g2buf, len2);

    mpz_t tmpz; mpz_init(tmpz);
    hash_to_mpz(tmpz, buf, len1 + msglen + len2, pairing->r);
    element_set_mpz(outZr, tmpz);
    mpz_clear(tmpz);
}

// Updated stealth_generate_addr to return R1, R2, C
int stealth_generate_addr(
  unsigned char* addr_buf,
  unsigned char* r1_buf,
  unsigned char* r2_buf,
  unsigned char* c_buf,
  int max_len
) {
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

  int n = element_length_in_bytes(Addr);
  int r1_len = element_length_in_bytes(R1);
  int r2_len = element_length_in_bytes(R2);
  int c_len  = element_length_in_bytes(C);

  if (n > max_len || r1_len > max_len || r2_len > max_len || c_len > max_len)
    return -1;

  element_to_bytes(addr_buf, Addr);
  element_to_bytes(r1_buf, R1);
  element_to_bytes(r2_buf, R2);
  element_to_bytes(c_buf, C);

  element_clear(Addr); element_clear(R1); element_clear(R2); element_clear(C);
  element_clear(rZ); element_clear(r2Z); element_clear(Ar_pow_r);
  element_clear(pairing_res); element_clear(pairing_res_powr); element_clear(R3);

  return n;
}


int stealth_addr_verify(unsigned char* addr_buf, unsigned char* r1_buf, unsigned char* c_buf) {
    element_t Addr, R1, C, R1_pow_a, C_prime, R3_prime, Addr_prime;
    element_init_G1(Addr, pairing);
    element_init_G1(R1, pairing);
    element_init_G1(C, pairing);
    element_init_G1(R1_pow_a, pairing);
    element_init_G1(C_prime, pairing);
    element_init_G1(R3_prime, pairing);
    element_init_G1(Addr_prime, pairing);

    element_from_bytes(Addr, addr_buf);
    element_from_bytes(R1, r1_buf);
    element_from_bytes(C, c_buf);

    element_pow_zn(R1_pow_a, R1, a);

    element_t r2Z_prime; element_init_Zr(r2Z_prime, pairing);
    H1(r2Z_prime, R1_pow_a);

    element_pow_zn(C_prime, B, r2Z_prime);

    element_t pairing_res, pairing_res_r2Z;
    element_init_GT(pairing_res, pairing);
    element_init_GT(pairing_res_r2Z, pairing);
    pairing_apply(pairing_res, R1, TK, pairing);
    element_pow_zn(pairing_res_r2Z, pairing_res, r2Z_prime);

    H2(R3_prime, pairing_res_r2Z);

    element_mul(Addr_prime, R3_prime, B);
    element_mul(Addr_prime, Addr_prime, C_prime);

    int eq = (element_cmp(Addr_prime, Addr) == 0);

    element_clear(Addr); element_clear(R1); element_clear(C);
    element_clear(R1_pow_a); element_clear(C_prime);
    element_clear(R3_prime); element_clear(Addr_prime);
    element_clear(r2Z_prime); element_clear(pairing_res); element_clear(pairing_res_r2Z);

    return eq;
}

int stealth_fast_addr_verify(unsigned char* r1_buf, unsigned char* c_buf) {
    element_t R1, C, R1_pow_a, C_prime;
    element_init_G1(R1, pairing);
    element_init_G1(C, pairing);
    element_init_G1(R1_pow_a, pairing);
    element_init_G1(C_prime, pairing);

    element_from_bytes(R1, r1_buf);
    element_from_bytes(C, c_buf);

    element_pow_zn(R1_pow_a, R1, a);
    element_t r2Z; element_init_Zr(r2Z, pairing);
    H1(r2Z, R1_pow_a);
    element_pow_zn(C_prime, B, r2Z);

    int eq = (element_cmp(C_prime, C) == 0);

    element_clear(R1); element_clear(C);
    element_clear(R1_pow_a); element_clear(C_prime);
    element_clear(r2Z);

    return eq;
}

int stealth_dskgen(unsigned char* addr_buf, unsigned char* r1_buf, unsigned char* out_buf, int maxlen) {
    element_t Addr, R1, R1_pow_a, r2Z, exp, dsk, h3_addr;
    element_init_G1(Addr, pairing);
    element_init_G1(R1, pairing);
    element_init_G1(R1_pow_a, pairing);
    element_init_Zr(r2Z, pairing);
    element_init_Zr(exp, pairing);
    element_init_G1(dsk, pairing);
    element_init_G1(h3_addr, pairing);

    element_from_bytes(Addr, addr_buf);
    element_from_bytes(R1, r1_buf);

    element_pow_zn(R1_pow_a, R1, a);
    H1(r2Z, R1_pow_a);
    element_mul(exp, b, r2Z);
    H3(h3_addr, Addr);
    element_pow_zn(dsk, h3_addr, exp);

    int len = element_length_in_bytes(dsk);
    if (len > maxlen) return -1;
    element_to_bytes(out_buf, dsk);

    element_clear(Addr); element_clear(R1); element_clear(R1_pow_a);
    element_clear(r2Z); element_clear(exp); element_clear(dsk); element_clear(h3_addr);

    return len;
}


int stealth_sign(unsigned char* Q_buf, unsigned char* h_buf, unsigned char* addr_buf, unsigned char* dsk_buf, const char* msg) {
    element_t Q_sigma, hZ, Addr, dsk, gx, XGT, xZ, neg_hZ, dsk_inv_h;
    element_init_G1(Q_sigma, pairing);
    element_init_Zr(hZ, pairing);
    element_init_G1(Addr, pairing);
    element_init_G1(dsk, pairing);
    element_init_G1(gx, pairing);
    element_init_GT(XGT, pairing);
    element_init_Zr(xZ, pairing);
    element_init_Zr(neg_hZ, pairing);
    element_init_G1(dsk_inv_h, pairing);

    element_from_bytes(Addr, addr_buf);
    element_from_bytes(dsk, dsk_buf);

    element_random(xZ);
    element_pow_zn(gx, g, xZ);
    pairing_apply(XGT, gx, g, pairing);

    H4(hZ, Addr, msg, XGT);

    element_neg(neg_hZ, hZ);
    element_pow_zn(dsk_inv_h, dsk, neg_hZ);
    element_mul(Q_sigma, dsk_inv_h, gx);

    int qlen = element_length_in_bytes(Q_sigma);
    int hlen = element_length_in_bytes(hZ);
    element_to_bytes(Q_buf, Q_sigma);
    element_to_bytes(h_buf, hZ);

    element_clear(Q_sigma); element_clear(hZ); element_clear(Addr); element_clear(dsk);
    element_clear(gx); element_clear(XGT); element_clear(xZ);
    element_clear(neg_hZ); element_clear(dsk_inv_h);

    return qlen + hlen;
}

int stealth_verify(unsigned char* addr_buf, unsigned char* r2_buf, unsigned char* c_buf, const char* msg, unsigned char* h_buf, unsigned char* q_buf) {
    element_t Addr, R2, C, hZ, Q_sigma, h3_addr;
    element_init_G1(Addr, pairing);
    element_init_G1(R2, pairing);
    element_init_G1(C, pairing);
    element_init_Zr(hZ, pairing);
    element_init_G1(Q_sigma, pairing);
    element_init_G1(h3_addr, pairing);

    element_from_bytes(Addr, addr_buf);
    element_from_bytes(R2, r2_buf);
    element_from_bytes(C, c_buf);
    element_from_bytes(hZ, h_buf);
    element_from_bytes(Q_sigma, q_buf);

    H3(h3_addr, Addr);

    element_t pairing1, pairing2, pairing2_exp, prod;
    element_init_GT(pairing1, pairing);
    element_init_GT(pairing2, pairing);
    element_init_GT(pairing2_exp, pairing);
    element_init_GT(prod, pairing);

    pairing_apply(pairing1, Q_sigma, g, pairing);
    pairing_apply(pairing2, h3_addr, C, pairing);
    element_pow_zn(pairing2_exp, pairing2, hZ);
    element_mul(prod, pairing1, pairing2_exp);

    element_t hZ_prime; element_init_Zr(hZ_prime, pairing);
    H4(hZ_prime, Addr, msg, prod);

    int valid = (element_cmp(hZ, hZ_prime) == 0);

    element_clear(Addr); element_clear(R2); element_clear(C);
    element_clear(hZ); element_clear(Q_sigma); element_clear(h3_addr);
    element_clear(pairing1); element_clear(pairing2); element_clear(pairing2_exp); element_clear(prod);
    element_clear(hZ_prime);

    return valid;
}

int stealth_trace(unsigned char* addr_buf, unsigned char* r1_buf, unsigned char* r2_buf, unsigned char* c_buf, unsigned char* out_buf, int maxlen) {
    element_t Addr, R1, R2, C, pairing_res, pairing_powk, R3, R3_inv, C_inv, B_r;
    element_init_G1(Addr, pairing);
    element_init_G1(R1, pairing);
    element_init_G1(R2, pairing);
    element_init_G1(C, pairing);
    element_init_GT(pairing_res, pairing);
    element_init_GT(pairing_powk, pairing);
    element_init_G1(R3, pairing);
    element_init_G1(R3_inv, pairing);
    element_init_G1(C_inv, pairing);
    element_init_G1(B_r, pairing);

    element_from_bytes(Addr, addr_buf);
    element_from_bytes(R1, r1_buf);
    element_from_bytes(R2, r2_buf);
    element_from_bytes(C, c_buf);

    pairing_apply(pairing_res, R1, R2, pairing);
    element_pow_zn(pairing_powk, pairing_res, k);
    H2(R3, pairing_powk);

    element_invert(R3_inv, R3);
    element_invert(C_inv, C);

    element_mul(B_r, Addr, R3_inv);
    element_mul(B_r, B_r, C_inv);

    int len = element_length_in_bytes(B_r);
    if (len > maxlen) return -1;
    element_to_bytes(out_buf, B_r);

    element_clear(Addr); element_clear(R1); element_clear(R2); element_clear(C);
    element_clear(pairing_res); element_clear(pairing_powk);
    element_clear(R3); element_clear(R3_inv); element_clear(C_inv); element_clear(B_r);

    return len;
}
