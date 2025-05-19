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

double sumH1 = 0;
double sumGen = 0, sumStat = 0, sumSK = 0;



// H1: (G1 inG1) -> Zr
void H1(element_t outZr, element_t inG1) {
    clock_t t1 = clock();
    unsigned char buf[512];
    size_t len = element_length_in_bytes(inG1);
    element_to_bytes(buf, inG1);
    unsigned char digest[SHA256_DIGEST_LENGTH];
    SHA256(buf, len, digest);
    element_from_hash(outZr, digest, SHA256_DIGEST_LENGTH);
    clock_t t2 = clock();
    sumH1 += timer_diff(t1, t2);
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

void OnetimeAddrGen(
    element_t PK_one, 
    element_t R,
    element_t A, 
    element_t B) {
    clock_t t1 = clock();

    element_t temp, r,r_out;
    element_init_G1(temp, pairing);
    element_init_Zr(r, pairing);
    element_init_Zr(r_out, pairing);
    element_random(r);
    element_mul_zn(R, G, r);
    // r * A
    element_mul_zn(temp, A, r);
    // r_out = hash(rA)
    H1(r_out, temp);

    element_mul_zn(temp, G, r_out);
    element_add(PK_one, temp, B);


    element_clear(r);
    element_clear(r_out);
    element_clear(temp);

    clock_t t2 = clock();
    sumGen += timer_diff(t1, t2);
}

int ReceiverStatistics(
    element_t PK_one, 
    element_t R,                           
    element_t a,                   
    element_t B) {
    clock_t t1 = clock();

    element_t temp,r_out;
    element_init_G1(temp, pairing);
    element_init_Zr(r_out, pairing);
    // temp=aR
    element_mul_zn(temp, R, a);
    // r_out = h1( a*R)
    H1(r_out,temp);
    element_mul_zn(temp, G, r_out);


    element_add(temp, temp, B);
    int ok = element_cmp(PK_one, temp) == 0;
    element_clear(r_out);
    element_clear(temp);

    clock_t t2 = clock();
    sumStat += timer_diff(t1, t2);
    return ok;
}

void OnetimeSKGen(element_t sk_ot, element_t R,
                   element_t a, element_t b) {
    clock_t t1 = clock();

    element_t temp, r_out, r3;
    element_init_G1(temp, pairing);
    element_init_Zr(r_out, pairing);

    element_mul_zn(temp, R, a);
    H1(r_out, temp);

    element_add(sk_ot, r_out, b);

    element_clear(r_out);
    element_clear(temp);

    clock_t t2 = clock();
    sumSK += timer_diff(t1, t2);
}

int main(int argc, char **argv) {
    if (argc < 2) {
        fprintf(stderr, "Usage: %s <param_file>\n", argv[0]);
        return 1;
    }

    Setup(argv[1]);

    element_t A, B;
    element_t a, b;
    element_init_G1(A, pairing);
    element_init_G1(B, pairing);
    element_init_Zr(a, pairing);
    element_init_Zr(b, pairing);
    KeyGen(A, B, a, b);
    

    for (int i = 0; i < LOOP; i++) {
        element_t PK_one, R, sk_ot;
        element_init_G1(PK_one, pairing);
        element_init_G1(R, pairing);
        element_init_Zr(sk_ot, pairing);

        OnetimeAddrGen(PK_one, R, A, B);
        int result = ReceiverStatistics(PK_one, R, a, B);
        OnetimeSKGen(sk_ot, R, a, b);

        if (!result) printf("FAIL at round %d\n", i);
    }

    printf("Avg AddrGen Time     : %.3f ms\n", sumGen / LOOP);
    printf("Avg ReceiverStat Time: %.3f ms\n", sumStat / LOOP);
    printf("Avg OnetimeSKGen Time: %.3f ms\n", sumSK / LOOP);
    printf("Avg H1 Time: %.3f ms\n", sumH1 / (3*LOOP));
    return 0;
}