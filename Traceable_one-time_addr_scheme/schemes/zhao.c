#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <openssl/ec.h>
#include <openssl/ecdsa.h>
#include <openssl/obj_mac.h>
#include <openssl/sha.h>
#include <openssl/bn.h>
#include <openssl/rand.h>
#include <openssl/evp.h>

#define LOOP 100

// Global variables
EC_GROUP *group;
EC_POINT *G;
BIGNUM *order;

double timer_diff(clock_t start, clock_t end) {
    return ((double)(end - start)) / CLOCKS_PER_SEC * 1000.0;
}

double sumH1 = 0, sumH2 = 0;
double sumGen = 0, sumStat = 0, sumSK = 0, sumTrace = 0;

// H1: hash1(r1, a1*A2) -> Zp  
void H1(BIGNUM *result, BIGNUM *r1, EC_POINT *a1A2, BN_CTX *ctx) {
    clock_t t1 = clock();
    
    EVP_MD_CTX *mdctx = EVP_MD_CTX_new();
    const EVP_MD *md = EVP_sha256();
    unsigned char hash[EVP_MAX_MD_SIZE];
    unsigned int hash_len;
    
    EVP_DigestInit_ex(mdctx, md, NULL);
    
    // Add r1 to hash
    unsigned char *r1_buf = OPENSSL_malloc(BN_num_bytes(r1));
    int r1_len = BN_bn2bin(r1, r1_buf);
    EVP_DigestUpdate(mdctx, r1_buf, r1_len);
    
    // Add a1*A2 to hash
    size_t point_len = EC_POINT_point2oct(group, a1A2, POINT_CONVERSION_COMPRESSED, NULL, 0, ctx);
    unsigned char *point_buf = OPENSSL_malloc(point_len);
    EC_POINT_point2oct(group, a1A2, POINT_CONVERSION_COMPRESSED, point_buf, point_len, ctx);
    EVP_DigestUpdate(mdctx, point_buf, point_len);
    
    EVP_DigestFinal_ex(mdctx, hash, &hash_len);
    
    // Convert hash to BIGNUM and reduce modulo order
    BN_bin2bn(hash, hash_len, result);
    BN_mod(result, result, order, ctx);
    
    // Cleanup
    OPENSSL_free(r1_buf);
    OPENSSL_free(point_buf);
    EVP_MD_CTX_free(mdctx);
    
    clock_t t2 = clock();
    sumH1 += timer_diff(t1, t2);
}

// H2: hash2(r2*A3) -> Zp
void H2(BIGNUM *result, EC_POINT *r2A3, BN_CTX *ctx) {
    clock_t t1 = clock();
    
    EVP_MD_CTX *mdctx = EVP_MD_CTX_new();
    const EVP_MD *md = EVP_sha256();
    unsigned char hash[EVP_MAX_MD_SIZE];
    unsigned int hash_len;
    
    EVP_DigestInit_ex(mdctx, md, NULL);
    
    // Add r2*A3 to hash
    size_t point_len = EC_POINT_point2oct(group, r2A3, POINT_CONVERSION_COMPRESSED, NULL, 0, ctx);
    unsigned char *point_buf = OPENSSL_malloc(point_len);
    EC_POINT_point2oct(group, r2A3, POINT_CONVERSION_COMPRESSED, point_buf, point_len, ctx);
    EVP_DigestUpdate(mdctx, point_buf, point_len);
    
    EVP_DigestFinal_ex(mdctx, hash, &hash_len);
    
    // Convert hash to BIGNUM and reduce modulo order
    BN_bin2bn(hash, hash_len, result);
    BN_mod(result, result, order, ctx);
    
    // Cleanup
    OPENSSL_free(point_buf);
    EVP_MD_CTX_free(mdctx);
    
    clock_t t2 = clock();
    sumH2 += timer_diff(t1, t2);
}

void Setup() {
    // Initialize curve (using secp256r1)
    group = EC_GROUP_new_by_curve_name(NID_X9_62_prime256v1);
    if (!group) {
        fprintf(stderr, "Failed to create EC group\n");
        exit(1);
    }
    
    // Get generator point
    const EC_POINT *generator = EC_GROUP_get0_generator(group);
    if (!generator) {
        fprintf(stderr, "Failed to get generator\n");
        exit(1);
    }
    G = EC_POINT_new(group);
    EC_POINT_copy(G, generator);
    
    // Get order of the group
    order = BN_new();
    if (!EC_GROUP_get_order(group, order, NULL)) {
        fprintf(stderr, "Failed to get group order\n");
        exit(1);
    }
}

void KeyGen(EC_POINT *A, EC_POINT *B, BIGNUM *a, BIGNUM *b, BN_CTX *ctx) {
    // Generate random private keys
    BN_rand_range(a, order);
    BN_rand_range(b, order);
    
    // Compute public keys: A = a*G, B = b*G
    EC_POINT_mul(group, A, NULL, G, a, ctx);
    EC_POINT_mul(group, B, NULL, G, b, ctx);
}

void OnetimeAddrGen(EC_POINT *PK_one, EC_POINT *R, BIGNUM *r1,
                    BIGNUM *a1, EC_POINT *A2, EC_POINT *A3, EC_POINT *B2,
                    BN_CTX *ctx) {
    clock_t t1 = clock();
    
    BIGNUM *r2 = BN_new();
    BIGNUM *r3 = BN_new();
    EC_POINT *temp1 = EC_POINT_new(group);
    EC_POINT *temp2 = EC_POINT_new(group);
    EC_POINT *a1A2 = EC_POINT_new(group);
    EC_POINT *r2A3 = EC_POINT_new(group);
    
    // a1*A2
    EC_POINT_mul(group, a1A2, NULL, A2, a1, ctx);
    
    // r2 = hash1(r1, a1*A2)
    H1(r2, r1, a1A2, ctx);
    
    // R = r2 * G
    EC_POINT_mul(group, R, NULL, G, r2, ctx);
    
    // r2*A3
    EC_POINT_mul(group, r2A3, NULL, A3, r2, ctx);
    
    // r3 = hash2(r2*A3)
    H2(r3, r2A3, ctx);
    
    // PK_one = r3*G + R + B2
    EC_POINT_mul(group, temp1, NULL, G, r3, ctx);  // r3*G
    EC_POINT_add(group, temp2, temp1, R, ctx);     // r3*G + R
    EC_POINT_add(group, PK_one, temp2, B2, ctx);   // r3*G + R + B2
    
    // Cleanup
    BN_free(r2);
    BN_free(r3);
    EC_POINT_free(temp1);
    EC_POINT_free(temp2);
    EC_POINT_free(a1A2);
    EC_POINT_free(r2A3);
    
    clock_t t2 = clock();
    sumGen += timer_diff(t1, t2);
}

int ReceiverStatistics(EC_POINT *PK_one, EC_POINT *R, BIGNUM *r1,
                       BIGNUM *a2, EC_POINT *A1, EC_POINT *A3, EC_POINT *B2,
                       BN_CTX *ctx) {
    clock_t t1 = clock();
    
    BIGNUM *r2 = BN_new();
    BIGNUM *r3 = BN_new();
    EC_POINT *temp1 = EC_POINT_new(group);
    EC_POINT *temp2 = EC_POINT_new(group);
    EC_POINT *check_R = EC_POINT_new(group);
    EC_POINT *check_PK = EC_POINT_new(group);
    EC_POINT *a2A1 = EC_POINT_new(group);
    EC_POINT *r2A3 = EC_POINT_new(group);
    
    // a2*A1
    EC_POINT_mul(group, a2A1, NULL, A1, a2, ctx);
    
    // r2 = hash1(r1, a2*A1)
    H1(r2, r1, a2A1, ctx);
    
    // r2*A3
    EC_POINT_mul(group, r2A3, NULL, A3, r2, ctx);
    
    // r3 = hash2(r2*A3)
    H2(r3, r2A3, ctx);
    
    // Check 1: R == r2 * G
    EC_POINT_mul(group, check_R, NULL, G, r2, ctx);
    int ok1 = (EC_POINT_cmp(group, R, check_R, ctx) == 0);
    
    // Check 2: PK_one == r3*G + R + B2
    EC_POINT_mul(group, temp1, NULL, G, r3, ctx);  // r3*G
    EC_POINT_add(group, temp2, temp1, R, ctx);     // r3*G + R
    EC_POINT_add(group, check_PK, temp2, B2, ctx); // r3*G + R + B2
    int ok2 = (EC_POINT_cmp(group, PK_one, check_PK, ctx) == 0);
    
    // Cleanup
    BN_free(r2);
    BN_free(r3);
    EC_POINT_free(temp1);
    EC_POINT_free(temp2);
    EC_POINT_free(check_R);
    EC_POINT_free(check_PK);
    EC_POINT_free(a2A1);
    EC_POINT_free(r2A3);
    
    clock_t t2 = clock();
    sumStat += timer_diff(t1, t2);
    
    return ok1 && ok2;
}

void OnetimeSKGen(BIGNUM *sk_ot, BIGNUM *r1, BIGNUM *a2, EC_POINT *A1,
                  EC_POINT *A3, BIGNUM *b2, BN_CTX *ctx) {
    clock_t t1 = clock();
    
    BIGNUM *r2 = BN_new();
    BIGNUM *r3 = BN_new();
    EC_POINT *a2A1 = EC_POINT_new(group);
    EC_POINT *r2A3 = EC_POINT_new(group);
    
    // a2*A1
    EC_POINT_mul(group, a2A1, NULL, A1, a2, ctx);
    
    // r2 = hash1(r1, a2*A1)
    H1(r2, r1, a2A1, ctx);
    
    // r2*A3
    EC_POINT_mul(group, r2A3, NULL, A3, r2, ctx);
    
    // r3 = hash2(r2*A3)
    H2(r3, r2A3, ctx);
    
    // sk_ot = r3 + r2 + b2
    BN_add(sk_ot, r3, r2);
    BN_mod_add(sk_ot, sk_ot, b2, order, ctx);
    
    // Cleanup
    BN_free(r2);
    BN_free(r3);
    EC_POINT_free(a2A1);
    EC_POINT_free(r2A3);
    
    clock_t t2 = clock();
    sumSK += timer_diff(t1, t2);
}

void IdentityTracing(EC_POINT *B2_out, EC_POINT *PK_one, EC_POINT *R,
                     BIGNUM *a3, BN_CTX *ctx) {
    clock_t t1 = clock();
    
    BIGNUM *r3 = BN_new();
    EC_POINT *temp = EC_POINT_new(group);
    EC_POINT *r3G = EC_POINT_new(group);
    EC_POINT *a3R = EC_POINT_new(group);
    
    // a3*R
    EC_POINT_mul(group, a3R, NULL, R, a3, ctx);
    
    // r3 = hash2(a3*R)
    H2(r3, a3R, ctx);
    
    // B2 = PK_one - R - r3*G
    EC_POINT_mul(group, r3G, NULL, G, r3, ctx);    // r3*G
    
    // PK_one - R (using inversion: A - B = A + (-B))
    EC_POINT *neg_R = EC_POINT_new(group);
    EC_POINT_copy(neg_R, R);
    EC_POINT_invert(group, neg_R, ctx);
    EC_POINT_add(group, temp, PK_one, neg_R, ctx); // PK_one - R
    
    // temp - r3*G
    EC_POINT *neg_r3G = EC_POINT_new(group);
    EC_POINT_copy(neg_r3G, r3G);
    EC_POINT_invert(group, neg_r3G, ctx);
    EC_POINT_add(group, B2_out, temp, neg_r3G, ctx); // PK_one - R - r3*G
    
    // Cleanup
    BN_free(r3);
    EC_POINT_free(temp);
    EC_POINT_free(r3G);
    EC_POINT_free(neg_R);
    EC_POINT_free(neg_r3G);
    EC_POINT_free(a3R);
    
    clock_t t2 = clock();
    sumTrace += timer_diff(t1, t2);
}

void cleanup() {
    EC_POINT_free(G);
    EC_GROUP_free(group);
    BN_free(order);
}

int main() {
    Setup();
    
    BN_CTX *ctx = BN_CTX_new();
    
    // Initialize keys for three users
    EC_POINT *A1 = EC_POINT_new(group);
    EC_POINT *B1 = EC_POINT_new(group);
    EC_POINT *A2 = EC_POINT_new(group);
    EC_POINT *B2 = EC_POINT_new(group);
    EC_POINT *A3 = EC_POINT_new(group);
    EC_POINT *B3 = EC_POINT_new(group);
    
    BIGNUM *a1 = BN_new();
    BIGNUM *b1 = BN_new();
    BIGNUM *a2 = BN_new();
    BIGNUM *b2 = BN_new();
    BIGNUM *a3 = BN_new();
    BIGNUM *b3 = BN_new();
    
    // Generate keys
    KeyGen(A1, B1, a1, b1, ctx);
    KeyGen(A2, B2, a2, b2, ctx);
    KeyGen(A3, B3, a3, b3, ctx);
    
    printf("Running %d iterations...\n", LOOP);
    
    for (int i = 0; i < LOOP; i++) {
        EC_POINT *PK_one = EC_POINT_new(group);
        EC_POINT *R = EC_POINT_new(group);
        EC_POINT *B2_traced = EC_POINT_new(group);
        BIGNUM *r1 = BN_new();
        BIGNUM *sk_ot = BN_new();
        
        // Generate random r1
        BN_rand_range(r1, order);
        
        // Run algorithms
        OnetimeAddrGen(PK_one, R, r1, a1, A2, A3, B2, ctx);
        int result = ReceiverStatistics(PK_one, R, r1, a2, A1, A3, B2, ctx);
        OnetimeSKGen(sk_ot, r1, a2, A1, A3, b2, ctx);
        IdentityTracing(B2_traced, PK_one, R, a3, ctx);
        
        // Verify correctness
        if (EC_POINT_cmp(group, B2_traced, B2, ctx) != 0) {
            printf("FAIL: Identity tracing failed at round %d\n", i);
        }
        if (!result) {
            printf("FAIL: Receiver statistics failed at round %d\n", i);
        }
        
        // Cleanup round
        EC_POINT_free(PK_one);
        EC_POINT_free(R);
        EC_POINT_free(B2_traced);
        BN_free(r1);
        BN_free(sk_ot);
    }
    
    // Print timing results
    printf("\n=== Performance Results ===\n");
    printf("Avg AddrGen Time     : %.3f ms\n", sumGen / LOOP);
    printf("Avg ReceiverStat Time: %.3f ms\n", sumStat / LOOP);
    printf("Avg OnetimeSKGen Time: %.3f ms\n", sumSK / LOOP);
    printf("Avg IdentityTrace Time: %.3f ms\n", sumTrace / LOOP);
    printf("Avg H1 Time: %.3f ms\n", sumH1 / (3*LOOP));
    printf("Avg H2 Time: %.3f ms\n", sumH2 / (4*LOOP));
    
    // Cleanup
    EC_POINT_free(A1); EC_POINT_free(B1);
    EC_POINT_free(A2); EC_POINT_free(B2);
    EC_POINT_free(A3); EC_POINT_free(B3);
    BN_free(a1); BN_free(b1);
    BN_free(a2); BN_free(b2);
    BN_free(a3); BN_free(b3);
    BN_CTX_free(ctx);
    cleanup();
    
    return 0;
}