#include <spine/extension.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <spine/dll.h> 

// ---------------------------
// texture loader callbacks
// ---------------------------

static void (*createTextureCallback)(spAtlasPage*, const char*) = NULL;
static void (*disposeTextureCallback)(spAtlasPage*) = NULL;

SP_API void spAtlasPage_set_createTexture(void (*cb)(spAtlasPage*, const char*)) {
    createTextureCallback = cb;
}

SP_API void spAtlasPage_set_disposeTexture(void (*cb)(spAtlasPage*)) {
    disposeTextureCallback = cb;
}

// ---------------------------
// default texture behavior
// ---------------------------

void _spAtlasPage_createTexture(spAtlasPage* self, const char* path) {
    if (createTextureCallback) {
        createTextureCallback(self, path);
        return;
    }

    // 默认实现：仅复制路径作为 rendererObject
    self->rendererObject = path ? malloc(strlen(path) + 1) : NULL;
    if (path) strcpy(self->rendererObject, path);
    self->width = 1024;
    self->height = 1024;
}

void _spAtlasPage_disposeTexture(spAtlasPage* self) {
    if (disposeTextureCallback) {
        disposeTextureCallback(self);
        return;
    }

    // 默认释放路径
    if (self->rendererObject) {
        free(self->rendererObject);
        self->rendererObject = NULL;
    }
}

// ---------------------------
// file loading
// ---------------------------

char* _spUtil_readFile(const char* path, int* length) {
    FILE* file = fopen(path, "rb");
    if (!file) return NULL;

    fseek(file, 0, SEEK_END);
    *length = (int)ftell(file);
    fseek(file, 0, SEEK_SET);

    char* data = (char*)malloc(*length + 1);
    size_t result = fread(data, 1, *length, file);
    fclose(file);

    if (result != *length) {
        free(data);
        return NULL;
    }

    data[*length] = '\0';
    return data;
}
