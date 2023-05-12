#ifndef __COMMON_H__
#define __COMMON_H__

#ifdef __cplusplus
extern "C" {
#endif

#if __STDC_VERSION__ >= 199901L
#include "stdint.h"
#else
typedef unsigned char uint8_t;
typedef unsigned short uint16_t;
typedef unsigned int uint32_t;
#endif

typedef volatile uint8_t *addr8_t;
typedef volatile uint16_t *addr16_t;
typedef volatile uint32_t *addr32_t;

#ifdef __cplusplus
}
#endif

#endif /* __COMMON_H__ */