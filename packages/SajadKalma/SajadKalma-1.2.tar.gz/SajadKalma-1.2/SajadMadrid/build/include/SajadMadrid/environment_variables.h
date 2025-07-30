//     Copyright 2025, SajadKast, lyj891916@gmail.com find license text at end of file

#ifndef __SAJODE_ENVIRONMENT_VARIABLES_H__
#define __SAJODE_ENVIRONMENT_VARIABLES_H__

#ifdef __IDE_ONLY__
#include "SajadMadrid/prelude.h"
#endif

#include "SajadMadrid/environment_variables_system.h"

extern void undoEnvironmentVariable(PyThreadState *tstate, char const *variable_name,
                                    environment_char_t const *old_value);

#endif


