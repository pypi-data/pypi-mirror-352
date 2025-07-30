#ifndef __IRRSEQ00_H_
#define __IRRSEQ00_H_

#include <stdio.h>

#include <cstdint>

// These globals need to be defined differently depending
// on where they are compiled since BINDER on z/OS
// and off platform link editors (i.e., Mac/Linux)
// resolve symbols differently.
#ifndef __TOS_390__
extern char *r_admin_result_mock;
extern uint32_t r_admin_result_size_mock;
extern uint32_t r_admin_rc_mock;
extern uint32_t r_admin_saf_rc_mock;
extern uint32_t r_admin_racf_rc_mock;
extern uint32_t r_admin_racf_reason_mock;
#else
char *r_admin_result_mock         = NULL;
uint32_t r_admin_result_size_mock = 0;
uint32_t r_admin_rc_mock          = 0;
uint32_t r_admin_saf_rc_mock      = 0;
uint32_t r_admin_racf_rc_mock     = 0;
uint32_t r_admin_racf_reason_mock = 0;
#endif

extern "C" uint32_t callRadmin(char *__ptr32);

#endif
