#ifndef SPINE_EXTENSION_H
#define SPINE_EXTENSION_H

#include <spine/dll.h>
#include <spine/Atlas.h>

#ifdef __cplusplus
extern "C" {
#endif

SP_API void spAtlasPage_set_createTexture(void (*cb)(spAtlasPage* self, const char* path));
SP_API void spAtlasPage_set_disposeTexture(void (*cb)(spAtlasPage* self));
SP_API char* _spUtil_readFile(const char* path, int* length); 

#ifdef __cplusplus
}
#endif

#endif
