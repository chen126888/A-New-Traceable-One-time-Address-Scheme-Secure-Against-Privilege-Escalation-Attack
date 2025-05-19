#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <pbc/pbc.h>
#include <pbc/pbc_test.h>
#include <openssl/sha.h>
#include <time.h>

#define LOOP 100

pairing_t pairing;
element_t G;

double timer_diff(clock_t start, clock_t end) {
    return ((double)(end - start)) / CLOCKS_PER_SEC * 1000.0;
}

double sumH1 = 0, sumH2 = 0;
double sumGen = 0, sumStat = 0, sumSK = 0, sumTrace = 0;

// H1: (Zr r1, G1 inG1) -> Zr
void H1(element_t outZr, element_t r1, element_t inG1) {
    clock_t t1 = clock();
    unsigned char buf[1024];
    unsigned char *p = buf;
    size_t len1 = element_length_in_bytes(r1);
    size_t len2 = element_length_in_bytes(inG1);
    element_to_bytes(p, r1); p += len1;
    element_to_bytes(p, inG1); p += len2;
    unsigned char digest[SHA256_DIGEST_LENGTH];
    SHA256(buf, len1 + len2, digest);
    element_from_hash(outZr, digest, SHA256_DIGEST_LENGTH);
    clock_t t2 = clock();
    sumH1 += timer_diff(t1, t2);
}

// H2: (G1 inG1) -> Zr
void H2(element_t outZr, element_t inG1) {
    clock_t t1 = clock();
    unsigned char buf[512];
    size_t len = element_length_in_bytes(inG1);
    element_to_bytes(buf, inG1);
    unsigned char digest[SHA256_DIGEST_LENGTH];
    SHA256(buf, len, digest);
    element_from_hash(outZr, digest, SHA256_DIGEST_LENGTH);
    clock_t t2 = clock();
    sumH2 += timer_diff(t1, t2);
}

void Setup(const char* param_file) {
    char *fake_argv[2];
    fake_argv[0] = "prog";
    fake_argv[1] = (char*)param_file;
    pbc_demo_pairing_init(pairing, 2, fake_argv);
    element_init_G1(G, pairing);
    element_random(G);
}

void KeyGen(element_t A, element_t B, element_t a, element_t b) {
    element_random(a);
    element_random(b);
    element_mul_zn(A, G, a);
    element_mul_zn(B, G, b);
}

void OnetimeAddrGen(element_t PK_one, element_t R,
                     element_t r1, element_t a1,
                     element_t A2, element_t A3,
                     element_t B2) {
    clock_t t1 = clock();

    element_t temp, r2, r3, a1A2;
    element_init_G1(temp, pairing);
    element_init_G1(a1A2, pairing);
    element_init_Zr(r2, pairing);
    element_init_Zr(r3, pairing);

    element_mul_zn(a1A2, A2, a1); // a1 * A2
    // r2 = hash1(r1, a1*A2)
    H1(r2, r1, a1A2);
    element_mul_zn(R, G, r2);

    element_mul_zn(temp, A3, r2);
    // r3 = hash2(r2 * A3)
    H2(r3, temp);

    element_mul_zn(temp, G, r3);
    element_add(temp, temp, R);
    element_add(PK_one, temp, B2);

    element_clear(a1A2);
    element_clear(r2);
    element_clear(r3);
    element_clear(temp);

    clock_t t2 = clock();
    sumGen += timer_diff(t1, t2);
}

int ReceiverStatistics(
    element_t PK_one, 
    element_t R,            
    element_t r1,               
    element_t a2, 
    element_t A1,                  
    element_t A3, 
    element_t B2) {
    clock_t t1 = clock();

    element_t temp, check_B2, r2, r3;
    element_init_G1(temp, pairing);
    element_init_G1(check_B2, pairing);
    element_init_Zr(r2, pairing);
    element_init_Zr(r3, pairing);

    element_mul_zn(temp, A1, a2);
    // r2 = hash1(r1, a2*A1)
    H1(r2, r1, temp);
    element_mul_zn(temp, A3, r2);
    // r3 = hash2(r2 * A3)
    H2(r3, temp);

    element_mul_zn(temp, G, r2);
    int ok1 = element_cmp(temp, R) == 0;

    element_mul_zn(temp, G, r3);
    element_add(temp, temp, R);
    element_add(check_B2, temp, B2);
    int ok2 = element_cmp(PK_one, check_B2) == 0;

    element_clear(r2);
    element_clear(r3);
    element_clear(temp);
    element_clear(check_B2);

    clock_t t2 = clock();
    sumStat += timer_diff(t1, t2);
    return ok1 && ok2;
}

void OnetimeSKGen(element_t sk_ot,
                   element_t A1, element_t A3,
                   element_t a2, element_t b2) {
    clock_t t1 = clock();

    element_t temp, r2, r3;
    element_init_G1(temp, pairing);
    element_init_Zr(r2, pairing);
    element_init_Zr(r3, pairing);

    element_mul_zn(temp, A1, a2);
    H1(r2, temp, temp);
    element_mul_zn(temp, A3, r2);
    H2(r3, temp);

    element_add(sk_ot, r3, r2);
    element_add(sk_ot, sk_ot, b2);

    element_clear(r2);
    element_clear(r3);
    element_clear(temp);

    clock_t t2 = clock();
    sumSK += timer_diff(t1, t2);
}

void IdentityTracing(element_t B2_out,
                     element_t PK_one, element_t R,
                     element_t a3) {
    clock_t t1 = clock();

    element_t temp, r3;
    element_init_G1(temp, pairing);
    element_init_Zr(r3, pairing);

    element_mul_zn(temp, R, a3);
    H2(r3, temp);

    element_mul_zn(temp, G, r3);
    element_sub(temp, PK_one, temp);
    element_sub(B2_out, temp, R);

    element_clear(r3);
    element_clear(temp);

    clock_t t2 = clock();
    sumTrace += timer_diff(t1, t2);
}

int main(int argc, char **argv) {
    if (argc < 2) {
        fprintf(stderr, "Usage: %s <param_file>\n", argv[0]);
        return 1;
    }

    Setup(argv[1]);

    element_t A1, B1, A2, B2, A3, B3;
    element_t a1, b1, a2, b2, a3, b3;
    element_init_G1(A1, pairing);
    element_init_G1(B1, pairing);
    element_init_Zr(a1, pairing);
    element_init_Zr(b1, pairing);
    element_init_G1(A2, pairing);
    element_init_G1(B2, pairing);
    element_init_Zr(a2, pairing);
    element_init_Zr(b2, pairing);
    element_init_G1(A3, pairing);
    element_init_G1(B3, pairing);
    element_init_Zr(a3, pairing);
    element_init_Zr(b3, pairing);
    KeyGen(A1, B1, a1, b1);
    KeyGen(A2, B2, a2, b2);
    KeyGen(A3, B3, a3, b3);

    for (int i = 0; i < LOOP; i++) {
        element_t PK_one, R, B2_traced, sk_ot, r1;
        element_init_G1(PK_one, pairing);
        element_init_G1(R, pairing);
        element_init_G1(B2_traced, pairing);
        element_init_Zr(r1, pairing);
        element_init_Zr(sk_ot, pairing);

        element_random(r1);
        OnetimeAddrGen(PK_one, R, r1, a1, A2, A3, B2);
        int result = ReceiverStatistics(PK_one, R, r1, a2,A1, A3, B2);
        OnetimeSKGen(sk_ot, A1, A3, a2, b2);
        IdentityTracing(B2_traced, PK_one, R, a3);

        if (element_cmp(B2_traced, B2)) printf("FAIL at round %d\n", i);
        if (!result) printf("FAIL at round %d\n", i);
    }

    printf("Avg AddrGen Time     : %.3f ms\n", sumGen / LOOP);
    printf("Avg ReceiverStat Time: %.3f ms\n", sumStat / LOOP);
    printf("Avg OnetimeSKGen Time: %.3f ms\n", sumSK / LOOP);
    printf("Avg IdentityTrace Time: %.3f ms\n", sumTrace / LOOP);
    printf("Avg H1 Time: %.3f ms\n", sumH1 / (3*LOOP));
    printf("Avg H2 Time: %.3f ms\n", sumH2 / (4*LOOP));
    return 0;
}
